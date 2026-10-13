"""Translation service. Local NLLB by default, remote providers optional."""
from __future__ import annotations

import logging

import httpx

from ai_dub.config.settings import StudioSettings
from ai_dub.models.segment import TranscriptSegment, TranslatedSegment

log = logging.getLogger(__name__)

_LANG_ALIASES = {"zh": "zho_Hans", "pt": "por_Latn", "en": "eng_Latn", "es": "spa_Latn"}


class TranslationService:
    def __init__(self, settings: StudioSettings) -> None:
        self._settings = settings
        self._nllb = None

    def _load_nllb(self):
        if self._nllb is None:
            from transformers import pipeline  # noqa: PLC0415

            self._nllb = pipeline("translation", model="facebook/nllb-200-distilled-600M")
        return self._nllb

    async def translate_segment(
        self, segment: TranscriptSegment, target_lang: str
    ) -> TranslatedSegment:
        provider = self._settings.translation_provider
        if provider == "local_nllb":
            text = self._translate_nllb(segment.text, target_lang)
        elif provider == "libretranslate":
            text = await self._translate_http(segment.text, target_lang, endpoint=self._settings.translation_endpoint)
        else:
            raise ValueError(f"unknown translation_provider: {provider}")

        return TranslatedSegment(
            source=segment, target_text=text, target_lang=target_lang, engine=provider
        )

    def _translate_nllb(self, text: str, target_lang: str) -> str:
        nllb_lang = _LANG_ALIASES.get(target_lang, target_lang)
        result = self._load_nllb()(text, src_lang="eng_Latn", tgt_lang=nllb_lang)
        return result[0]["translation_text"]

    async def _translate_http(self, text: str, target_lang: str, endpoint: str | None) -> str:
        if not endpoint:
            raise ValueError("translation_endpoint required for HTTP provider")
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                endpoint, json={"q": text, "source": "en", "target": target_lang, "format": "text"}
            )
            resp.raise_for_status()
            return resp.json()["translatedText"]