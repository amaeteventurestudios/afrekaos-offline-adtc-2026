"""Language-mode configuration for AfrekaOS Offline.

Controlled multilingual response support for English, Yorùbá, Hausa, Swahili,
Nigerian Pidgin, and French. Reuses the language-architecture discipline
(language registry, localized response rules, glossary files, clear fallback)
without copying any external product's content.

Standard library only. No cloud translation. No external APIs. The local model
is asked to answer in the selected language; difficult technical terms may
remain in English where no clean translation exists.

Language codes follow ISO 639-1 / 639-3 where practical:
  en  -> English
  yo  -> Yorùbá
  ha  -> Hausa
  sw  -> Swahili
  pcm -> Nigerian Pidgin
  fr  -> French
"""

from __future__ import annotations

DEFAULT_LANGUAGE = "en"

# Ordered registry of supported languages. "native" is the endonym shown in the
# UI selector; "label" is the English name used in runtime summaries.
LANGUAGES = {
    "en": {"code": "en", "label": "English", "native": "English"},
    "yo": {"code": "yo", "label": "Yorùbá", "native": "Yorùbá"},
    "ha": {"code": "ha", "label": "Hausa", "native": "Hausa"},
    "sw": {"code": "sw", "label": "Swahili", "native": "Swahili"},
    "pcm": {"code": "pcm", "label": "Nigerian Pidgin", "native": "Naija"},
    "fr": {"code": "fr", "label": "French", "native": "Français"},
}

# Per-language response instructions injected into the grounded/ungrounded
# prompt. These tell the model which language to answer in and how to handle
# terms that do not translate cleanly. The boundary language (not accounting/
# banking/...) is enforced separately by the answer rules.
LANGUAGE_INSTRUCTIONS = {
    "en": (
        "Answer in clear, simple English."
    ),
    "yo": (
        "Answer in Yorùbá. Use simple, respectful business Yorùbá. If a "
        "technical business term has no clean Yorùbá equivalent, you may keep "
        "that term in English for clarity."
    ),
    "ha": (
        "Answer in Hausa. Use simple, clear business Hausa. If a technical "
        "business term has no clean Hausa equivalent, you may keep that term "
        "in English for clarity."
    ),
    "sw": (
        "Answer in Swahili. Use simple, clear business Swahili. If a technical "
        "business term has no clean Swahili equivalent, you may keep that term "
        "in English for clarity."
    ),
    "pcm": (
        "Answer in Nigerian Pidgin (Naija). Keep it simple and respectful — "
        "write the way a market operator would explain it, not comic "
        "exaggeration. If a technical business term is clearer in English, "
        "you may keep it in English."
    ),
    "fr": (
        "Answer in French. Use clear, simple Francophone business French "
        "suitable for West and Central Africa. If a technical business term "
        "is clearer in English, you may keep it in English."
    ),
}


def get_supported_languages() -> dict:
    """Return the full language registry (code -> {code, label, native})."""
    return dict(LANGUAGES)


def normalize_language_code(code: str | None) -> str:
    """Normalize a language code to a supported one, falling back to English.

    Accepts case-insensitive codes and common aliases (e.g. "yoruba", "pidgin",
    "naija"). Returns the canonical supported code, or DEFAULT_LANGUAGE if the
    code is unknown.
    """
    if not code:
        return DEFAULT_LANGUAGE
    raw = str(code).strip().lower()
    # Direct code match.
    if raw in LANGUAGES:
        return raw
    # Common aliases.
    aliases = {
        "english": "en",
        "eng": "en",
        "yoruba": "yo",
        "yorùbá": "yo",
        "hausa": "ha",
        "swahili": "sw",
        "kiswahili": "sw",
        "pidgin": "pcm",
        "nigerian pidgin": "pcm",
        "naija": "pcm",
        "french": "fr",
        "francais": "fr",
        "français": "fr",
    }
    if raw in aliases:
        return aliases[raw]
    return DEFAULT_LANGUAGE


def get_language_label(code: str) -> str:
    """Return the English label for a language code (e.g. 'fr' -> 'French')."""
    norm = normalize_language_code(code)
    return LANGUAGES[norm]["label"]


def get_language_native(code: str) -> str:
    """Return the native/endonym label (e.g. 'fr' -> 'Français')."""
    norm = normalize_language_code(code)
    return LANGUAGES[norm]["native"]


def get_language_instruction(code: str) -> str:
    """Return the response-language instruction for a code (English fallback)."""
    norm = normalize_language_code(code)
    return LANGUAGE_INSTRUCTIONS[norm]


def is_supported_language(code: str) -> bool:
    """True if the code (after normalization) is a supported language."""
    return normalize_language_code(code) != DEFAULT_LANGUAGE or (
        str(code or "").strip().lower() in LANGUAGES
    )


def language_summary() -> dict:
    """Return a non-raising summary of the language configuration."""
    return {
        "default": DEFAULT_LANGUAGE,
        "count": len(LANGUAGES),
        "codes": sorted(LANGUAGES.keys()),
        "languages": {
            c: {"label": v["label"], "native": v["native"]}
            for c, v in sorted(LANGUAGES.items())
        },
        "cloud_translation": False,
    }


__all__ = [
    "DEFAULT_LANGUAGE",
    "LANGUAGES",
    "LANGUAGE_INSTRUCTIONS",
    "get_supported_languages",
    "normalize_language_code",
    "get_language_label",
    "get_language_native",
    "get_language_instruction",
    "is_supported_language",
    "language_summary",
]
