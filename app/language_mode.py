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


# --- UI translation registry (Task 006B) ------------------------------------
# Full page-chrome localization. Each dict is keyed by UI string key; missing
# keys fall back to English. Technical values (model paths, job ids, return
# codes) are never translated.

UI_TEXT_BUNDLES: dict[str, dict[str, str]] = {
    "en": {
        "product": "AfrekaOS Offline",
        "tagline": "Offline SME operations copilot",
        "offline_mode": "Offline mode",
        "local_model": "Local model",
        "sqlite_retrieval": "SQLite retrieval",
        "no_cloud_dependency": "No cloud dependency",
        "mission_control": "Mission Control",
        "demo_scenarios": "Demo Scenarios",
        "daily_advisor": "Daily Advisor",
        "inventory_advisor": "Inventory Advisor",
        "cashflow_advisor": "Cashflow Advisor",
        "offline_status": "Offline Status",
        "response_language": "Response language",
        "select_language": "Select language",
        "back_to_mission_control": "Back to Mission Control",
        "local_only": "Local-only",
        "operational_guidance_only": "Operational guidance only",
        "choose_advisor": "Choose a coach above to reason through a daily operations question.",
        "daily_operations_advisor": "Daily Operations Advisor",
        "inventory_and_stock_check": "Inventory and Stock Check",
        "cashflow_pressure_coach": "Cashflow Pressure Coach",
        "offline_system_status": "Offline System Status",
        "your_operations_question": "Your operations question",
        "your_question": "Your question",
        "get_operating_guidance": "Get operating guidance",
        "running_local_model": "Running local model...",
        "loading_message": (
            "AfrekaOS received your question. It is building local retrieval "
            "context and running the local model. This can take 30 to 90 "
            "seconds on CPU-only hardware."
        ),
        "operating_guidance": "Operating Guidance",
        "runtime_summary": "Runtime summary",
        "runtime_status": "Runtime status",
        "model_path_exists": "Model path exists",
        "llama_binary": "Llama binary",
        "retrieval_index": "Retrieval index",
        "locked_candidate": "Locked candidate",
        "retrieval_grounded": "Retrieval-grounded",
        "direct_answer_mode": "Direct-answer mode",
        "yes": "yes",
        "no": "no",
        "request_received": "Request received",
        "building_retrieval_index": "Building local retrieval index",
        "retrieving_sme_context": "Retrieving SME context",
        "building_grounded_prompt": "Building grounded prompt",
        "running_qwen_model": "Running local Qwen model",
        "formatting_answer": "Formatting answer",
        "complete": "Complete",
        "failed": "Failed",
        "queued": "queued",
        "running": "running",
        "inference_time_warning": (
            "Local inference may take 30 to 90 seconds on CPU-only hardware."
        ),
        "boundary_warning": (
            "AfrekaOS provides operational guidance only. It is not accounting, "
            "banking, payroll, tax, lending, or ERP software."
        ),
        "error_title": "AfrekaOS hit a local runtime error.",
        "check_terminal_logs": "Check terminal logs for details.",
        "check_model_present": "Is model/afrekaos.gguf present?",
        "check_llama_available": "Is llama-completion available?",
        "check_timeout": "Did the request time out?",
        "suggested_checks": "Suggested checks",
        "error_summary": "Error summary",
        "current_route": "Current route",
        "job_not_found": "Job not found",
        "job_not_found_detail": "was not found. It may have expired (jobs are kept in memory only).",
        "demo_intro": (
            'Ready-made SME operations scenarios. Click "Run this scenario" '
            "to submit the prompt to the matching advisor."
        ),
        "run_this_scenario": "Run this scenario",
        "demo_low_sales": "Low sales, stockout, supplier delay",
        "demo_expansion": "Expansion readiness",
        "demo_inventory": "Inventory pressure",
        "demo_cash": "Cash pressure and customer credit",
        "empty_answer": "(model produced no visible answer text)",
        "enter_question": "Please enter an operations question.",
        "prompt_echo_removed": "Prompt echo removed from display.",
        "footer": (
            "AfrekaOS Offline — local-only. No cloud. Operational guidance, "
            "not accounting/banking/payroll/tax/ERP software."
        ),
    },
    "fr": {
        "product": "AfrekaOS Offline",
        "tagline": "Copilote d'exploitation PME hors ligne",
        "offline_mode": "Mode hors ligne",
        "local_model": "Modèle local",
        "sqlite_retrieval": "Recherche SQLite",
        "no_cloud_dependency": "Aucun cloud",
        "mission_control": "Contrôle Mission",
        "demo_scenarios": "Scénarios de démo",
        "daily_advisor": "Conseiller quotidien",
        "inventory_advisor": "Conseiller stock",
        "cashflow_advisor": "Conseiller trésorerie",
        "offline_status": "Statut hors ligne",
        "response_language": "Langue de réponse",
        "select_language": "Choisir la langue",
        "back_to_mission_control": "Retour au Contrôle Mission",
        "local_only": "Local uniquement",
        "operational_guidance_only": "Conseils d'exploitation uniquement",
        "choose_advisor": "Choisissez un conseiller pour analyser une question d'exploitation.",
        "daily_operations_advisor": "Conseiller en opérations quotidiennes",
        "inventory_and_stock_check": "Inventaire et contrôle de stock",
        "cashflow_pressure_coach": "Coach en pression de trésorerie",
        "offline_system_status": "Statut du système hors ligne",
        "your_operations_question": "Votre question d'exploitation",
        "your_question": "Votre question",
        "get_operating_guidance": "Obtenir des conseils",
        "running_local_model": "Modèle local en cours...",
        "loading_message": (
            "AfrekaOS a reçu votre question. Elle prépare le contexte local et "
            "exécute le modèle. Cela peut prendre 30 à 90 secondes sur CPU."
        ),
        "operating_guidance": "Conseils d'exploitation",
        "runtime_summary": "Résumé d'exécution",
        "runtime_status": "Statut d'exécution",
        "model_path_exists": "Chemin du modèle existe",
        "llama_binary": "Binaire llama",
        "retrieval_index": "Index de recherche",
        "locked_candidate": "Candidat verrouillé",
        "retrieval_grounded": "Basé sur la recherche",
        "direct_answer_mode": "Mode réponse directe",
        "yes": "oui",
        "no": "non",
        "request_received": "Demande reçue",
        "building_retrieval_index": "Construction de l'index local",
        "retrieving_sme_context": "Récupération du contexte PME",
        "building_grounded_prompt": "Construction de l'invite",
        "running_qwen_model": "Exécution du modèle Qwen local",
        "formatting_answer": "Mise en forme de la réponse",
        "complete": "Terminé",
        "failed": "Échec",
        "queued": "en file",
        "running": "en cours",
        "inference_time_warning": (
            "L'inférence locale peut prendre 30 à 90 secondes sur CPU."
        ),
        "boundary_warning": (
            "AfrekaOS fournit uniquement des conseils d'exploitation. Ce n'est "
            "pas un logiciel de comptabilité, banque, paie, fiscalité, prêt ou ERP."
        ),
        "error_title": "AfrekaOS a rencontré une erreur locale.",
        "check_terminal_logs": "Consultez les logs du terminal.",
        "check_model_present": "Le fichier model/afrekaos.gguf est-il présent ?",
        "check_llama_available": "llama-completion est-il disponible ?",
        "check_timeout": "La demande a-t-elle expiré ?",
        "suggested_checks": "Vérifications suggérées",
        "error_summary": "Résumé de l'erreur",
        "current_route": "Route actuelle",
        "job_not_found": "Travail introuvable",
        "job_not_found_detail": "introuvable. Il a peut-être expiré (les travaux sont en mémoire uniquement).",
        "demo_intro": (
            "Scénarios PME prêts à l'emploi. Cliquez sur « Lancer ce scénario » "
            "pour soumettre au conseiller correspondant."
        ),
        "run_this_scenario": "Lancer ce scénario",
        "demo_low_sales": "Ventes basses, rupture, retard fournisseur",
        "demo_expansion": "Préparation à l'expansion",
        "demo_inventory": "Pression d'inventaire",
        "demo_cash": "Pression de trésorerie et crédit client",
        "empty_answer": "(le modèle n'a produit aucune réponse visible)",
        "enter_question": "Veuillez saisir une question d'exploitation.",
        "prompt_echo_removed": "Écho d'invite supprimé de l'affichage.",
        "footer": (
            "AfrekaOS Offline — local uniquement. Aucun cloud. Conseils "
            "d'exploitation, non un logiciel de comptabilité/banque/paie/fiscalité/ERP."
        ),
    },
    "yo": {
        "product": "AfrekaOS Offline",
        "tagline": "Akọniṣẹ́ ìdájọ́ PME aládàáyé",
        "offline_mode": "Aládàáyé",
        "local_model": "Àpòwọ̀ àgùntàn",
        "sqlite_retrieval": "SQLite àwáàrí",
        "no_cloud_dependency": "Láìsí cloud",
        "mission_control": "Ìdarí iṣẹ́",
        "demo_scenarios": "Àwọn àpẹẹrẹ",
        "daily_advisor": "Amọ̀ran ojóumọ́",
        "inventory_advisor": "Amọ̀ran ọjà",
        "cashflow_advisor": "Amọ̀ran owó",
        "offline_status": "Ipo aládàáyé",
        "response_language": "Èdè ìdáhùn",
        "select_language": "Yan èdè",
        "back_to_mission_control": "Páàpọ̀ sí Ìdarí iṣẹ́",
        "local_only": "Àgbègbè nìkan",
        "operational_guidance_only": "Ìmọ̀ràn iṣẹ́ nìkan",
        "choose_advisor": "Yan amọ̀ran láti rò nínú ìbérè iṣẹ́ ojóumọ́.",
        "daily_operations_advisor": "Amọ̀ran iṣẹ́ ojóumọ́",
        "inventory_and_stock_check": "Ẹ̀rọ̀jà àti yíyẹ̀wò̀n ọjà",
        "cashflow_pressure_coach": "Olùràn ìdábọ̀ owó",
        "offline_system_status": "Ipo eto aládàáyé",
        "your_operations_question": "Ìbéèrè iṣẹ́ rẹ",
        "your_question": "Ìbéèrè rẹ",
        "get_operating_guidance": "Gba ìmọ̀ràn iṣẹ́",
        "running_local_model": "Àpòwọ̀ nṣiṣẹ́...",
        "loading_message": (
            "AfrekaOS ti gba ìbéèrè rẹ. Ó ń kó àkójọpọ̀ àkósílẹ̀ àti ṣiṣe "
            "àpòwọ̀. Lè gba ìgbà 30 sí 90 lórí CPU."
        ),
        "operating_guidance": "Ìmọ̀ràn iṣẹ́",
        "runtime_summary": "Àkótán iṣẹ́",
        "runtime_status": "Ipo iṣẹ́",
        "model_path_exists": "Ọ̀nà àpòwọ̀ wà",
        "llama_binary": "Llama binary",
        "retrieval_index": "Àkójọ àwáàrí",
        "locked_candidate": "Àpòwọ̀ tí yà",
        "retrieval_grounded": "Lórí àwáàrí",
        "direct_answer_mode": "Ìdáhùn taara",
        "yes": "bẹ́ẹ̀ni",
        "no": "rárá",
        "request_received": "A ti gba béèrè",
        "building_retrieval_index": "Kíkọ́ àkójọ àwáàrí",
        "retrieving_sme_context": "Kígba àkósílẹ̀ PME",
        "building_grounded_prompt": "Ṣíṣe ìkìlẹ̀",
        "running_qwen_model": "Ṣíṣe àpòwọ̀ Qwen",
        "formatting_answer": "Ṣíṣe ìdáhùn",
        "complete": "Ti parí",
        "failed": "Kò ṣeéṣe",
        "queued": "n dúró",
        "running": "n lọ",
        "inference_time_warning": (
            "Lè gba ìgbà 30 sí 90 lórí CPU."
        ),
        "boundary_warning": (
            "AfrekaOS ń ṣèrànwọ́ lórí iṣẹ́ nìkan. Kì í ṣe ètò ìṣirò owó, bánkì, "
            "iṣẹ́-ṣíṣe owó, owó-orí, tàbí ERP."
        ),
        "error_title": "AfrekaOS ní ìṣòro àgbègbè.",
        "check_terminal_logs": "Ṣàyẹ̀wò àkósílẹ̀ tẹeminú.",
        "check_model_present": "model/afrekaos.gguf wà bẹ́ẹ̀?",
        "check_llama_available": "llama-completion wà bẹ́ẹ̀?",
        "check_timeout": "Béèrè tí kúrò lásìkò?",
        "suggested_checks": "Àwọn yíyẹ̀wò̀n",
        "error_summary": "Àkótán àṣìṣe",
        "current_route": "Ọ̀nà lọ́wọ́",
        "job_not_found": "Iṣẹ́ kò rí",
        "job_not_found_detail": "kò rí wà. Ó lè ti parí (iṣẹ́ wà nínú rẹ nìkan).",
        "demo_intro": "Àwọn àpẹẹrẹ PME. Tẹ bọ́tínì láti fi ránṣẹ́ sí amọ̀ran.",
        "run_this_scenario": "Ṣiṣe éyí",
        "demo_low_sales": "Títà kéré, ọjà kún, ìdásílẹ̀ olùpèsè",
        "demo_expansion": "Ìfẹsẹ̀múlẹ̀ iṣẹ́",
        "demo_inventory": "Ìpọ́nju ẹ̀rọ̀jà",
        "demo_cash": "Ìpọ́nju owó àti gbèsè oníbàárà",
        "empty_answer": "(àpòwọ̀ kò ṣe ìdáhùn)",
        "enter_question": "Jọ̀wọ́ kọ ìbéèrè iṣẹ́ kan.",
        "prompt_echo_removed": "Àkósílẹ̀ ìkìlẹ̀ ti kúrò.",
        "footer": (
            "AfrekaOS Offline — àgbègbè nìkan. Láìsí cloud. Ìmọ̀ràn iṣẹ́, "
            "kì í ṣe ètò owó/bánkì/iṣẹ́/owó-orí/ERP."
        ),
    },
    "ha": {
        "product": "AfrekaOS Offline",
        "tagline": "Mataimakin kasuwancin PME ba tare da intanet ba",
        "offline_mode": "Ba tare da intanet",
        "local_model": "Samfurin gida",
        "sqlite_retrieval": "Binciken SQLite",
        "no_cloud_dependency": "Babu cloud",
        "mission_control": "Sarraunin Aiki",
        "demo_scenarios": "Misalan kwaikwayo",
        "daily_advisor": "Mai ba da shawara ta yau",
        "inventory_advisor": "Mai ba da shawara kayayyaki",
        "cashflow_advisor": "Mai ba da shawara kuɗi",
        "offline_status": "Matsayin ba tare da intanet",
        "response_language": "Harshen amsa",
        "select_language": "Zaɓi yare",
        "back_to_mission_control": "Komawa Sarraunin Aiki",
        "local_only": "Gida kawai",
        "operational_guidance_only": "Shawarar aiki kawai",
        "choose_advisor": "Zaɓi mai ba da shawara don nazarin tambayar aiki.",
        "daily_operations_advisor": "Mai ba da shawaran ayyukan yau",
        "inventory_and_stock_check": "Kayayyaki da duba stock",
        "cashflow_pressure_coach": "Kocin matsalar kuɗi",
        "offline_system_status": "Matsayin tsarin ba tare da intanet",
        "your_operations_question": "Tambayar aikin ku",
        "your_question": "Tambayar ku",
        "get_operating_guidance": "Samu shawarar aiki",
        "running_local_model": "Samfurin gida yana gudan...",
        "loading_message": (
            "AfrekaOS ta karɓi tambayar ku. Tana gina bayanan gida da gudanar "
            "samfurin. Wannan na iya ɗaukar sakan 30 zuwa 90 akan CPU."
        ),
        "operating_guidance": "Shawarar aiki",
        "runtime_summary": "Takaitaccen bayanin aiki",
        "runtime_status": "Matsayin aiki",
        "model_path_exists": "Hanyar samfurin tana nan",
        "llama_binary": "Llama binary",
        "retrieval_index": "Fihirisar bincike",
        "locked_candidate": "Samfurin da aka daure",
        "retrieval_grounded": "Dangane da bincike",
        "direct_answer_mode": "Yanayin amsa kai tsaye",
        "yes": "eh",
        "no": "a'a",
        "request_received": "An karɓi buƙata",
        "building_retrieval_index": "Gina fihirisar gida",
        "retrieving_sme_context": "Samo bayanan PME",
        "building_grounded_prompt": "Gina umarni",
        "running_qwen_model": "Gudanar da samfurin Qwen",
        "formatting_answer": "Tsara amsa",
        "complete": "An kammala",
        "failed": "An gazanta",
        "queued": "cikin jeri",
        "running": "yana gudan",
        "inference_time_warning": (
            "Wannan na iya ɗaukar sakan 30 zuwa 90 akan CPU."
        ),
        "boundary_warning": (
            "AfrekaOS tana bayar da shawarar aiki kawai. Ba tsarin lissafin "
            "kuɗi, banki, albashin, haraji, ko ERP ba ne."
        ),
        "error_title": "AfrekaOS ta sami kuskuren gida.",
        "check_terminal_logs": "Duba log din tasha.",
        "check_model_present": "model/afrekaos.gguf tana nan?",
        "check_llama_available": "llama-completion tana samuwa?",
        "check_timeout": "Bukatar ta kare lokaci?",
        "suggested_checks": "Dubawa da ake buƙata",
        "error_summary": "Takaitaccen kuskure",
        "current_route": "Hanyar yanzu",
        "job_not_found": "Aiki ba a same ba",
        "job_not_found_detail": "ba a same ba. Yana iya ƙarewa (ayyuka a cikin ƙwauri kawai).",
        "demo_intro": "Misalan kasuwancin PME. Danna don tura wa mai ba da shawara.",
        "run_this_scenario": "Gudanar da wannan",
        "demo_low_sales": "Kasuwanci mai gari, kayayyaki sun ƙare, jinkirin mai bayar",
        "demo_expansion": "Shirin faɗaɗa",
        "demo_inventory": "Matsalar kayayyaki",
        "demo_cash": "Matsalar kuɗi da bashin ciniki",
        "empty_answer": "(samfurin ba ya bayar da amsa)",
        "enter_question": "Da shigar da tambayar aiki.",
        "prompt_echo_removed": "An cire ma'anar umarni.",
        "footer": (
            "AfrekaOS Offline — gida kawai. Babu cloud. Shawarar aiki, ba "
            "tsarin lissafi/banki/albashin/haraji/ERP ba."
        ),
    },
    "sw": {
        "product": "AfrekaOS Offline",
        "tagline": "Msaidizi wa biashara wa PME nje",
        "offline_mode": "Hali ya nje",
        "local_model": "Modeli ya ndani",
        "sqlite_retrieval": "Utafutaji wa SQLite",
        "no_cloud_dependency": "Hakuna cloud",
        "mission_control": "Udhibiti wa Misheni",
        "demo_scenarios": "Mifano ya onyesho",
        "daily_advisor": "Mshauri wa kila siku",
        "inventory_advisor": "Mshauri wa bidhaa",
        "cashflow_advisor": "Mshauri wa fedha",
        "offline_status": "Hadhi ya nje",
        "response_language": "Lugha ya jibu",
        "select_language": "Chagua lugha",
        "back_to_mission_control": "Rudi Udhibiti wa Misheni",
        "local_only": "Ya ndani tu",
        "operational_guidance_only": "Mwongozo wa uendeshaji tu",
        "choose_advisor": "Chagua mshauri kuchambua swali la biashara.",
        "daily_operations_advisor": "Mshauri wa shughuli za kila siku",
        "inventory_and_stock_check": "Hifadhi na ukaguzi wa bidhaa",
        "cashflow_pressure_coach": "Kocha wa shinikizo la fedha",
        "offline_system_status": "Hadhi ya mfumo wa nje",
        "your_operations_question": "Swali lako la biashara",
        "your_question": "Swali lako",
        "get_operating_guidance": "Pata mwongozo",
        "running_local_model": "Modeli ya ndani inaendelea...",
        "loading_message": (
            "AfrekaOS imepokea swali lako. Inaandaa muktadha wa ndani na "
            "kuendesha modeli. Hii inaweza kuchukua sekunde 30 hadi 90 kwenye CPU."
        ),
        "operating_guidance": "Mwongozo wa uendeshaji",
        "runtime_summary": "Muhtasari wa utekelezaji",
        "runtime_status": "Hadhi ya utekelezaji",
        "model_path_exists": "Njia ya modeli ipo",
        "llama_binary": "Llama binary",
        "retrieval_index": "Faharasa ya utafutaji",
        "locked_candidate": "Modeli iliyofungwa",
        "retrieval_grounded": "Inategemea utafutaji",
        "direct_answer_mode": "Hali ya jibu moja kwa moja",
        "yes": "ndiyo",
        "no": "hapana",
        "request_received": "Ombi limepokelewa",
        "building_retrieval_index": "Kujenga faharasa ya ndani",
        "retrieving_sme_context": "Kupata muktadha wa PME",
        "building_grounded_prompt": "Kujenga maelekezo",
        "running_qwen_model": "Kuendesha modeli ya Qwen",
        "formatting_answer": "Kuandika jibu",
        "complete": "Imekamilika",
        "failed": "Imeshindwa",
        "queued": "kwenye foleni",
        "running": "inaendelea",
        "inference_time_warning": (
            "Hii inaweza kuchukua sekunde 30 hadi 90 kwenye CPU."
        ),
        "boundary_warning": (
            "AfrekaOS inatoa mwongozo wa uendeshaji tu. Sio mfumo wa uhasibu, "
            "benki, mishahara, kodi, au ERP."
        ),
        "error_title": "AfrekaOS imekumbatia kosa la ndani.",
        "check_terminal_logs": "Angalia kumbukumbu za terminal.",
        "check_model_present": "model/afrekaos.gguf ipo?",
        "check_llama_available": "llama-completion inapatikana?",
        "check_timeout": "Ombi limekwisha muda?",
        "suggested_checks": "Ukaguzi unaopendekezwa",
        "error_summary": "Muhtasari wa kosa",
        "current_route": "Njia ya sasa",
        "job_not_found": "Kazi haijapatikana",
        "job_not_found_detail": "haipatikani. Inaweza kuwa imeisha (kazi ziko kwenye kumbukumbu tu).",
        "demo_intro": "Mifano ya biashara ya PME. Bonyeza kuwasilisha kwa mshauri.",
        "run_this_scenario": "Endesha hii",
        "demo_low_sales": "Mauzo machache, bidhaa zimeisha, kuchelewa kwa muuzaji",
        "demo_expansion": "Utaratibu wa upanuzi",
        "demo_inventory": "Shinikizo la bidhaa",
        "demo_cash": "Shinikizo la fedha na mkopo wa mteja",
        "empty_answer": "(modeli haikutoa jibu)",
        "enter_question": "Tafadhali andika swali la biashara.",
        "prompt_echo_removed": "Maandishi ya maelekezo yameondolewa.",
        "footer": (
            "AfrekaOS Offline — ya ndani tu. Hakuna cloud. Mwongozo wa "
            "uendeshaji, sio uhasibu/benki/mishahara/kodi/ERP."
        ),
    },
    "pcm": {
        "product": "AfrekaOS Offline",
        "tagline": "Business helper wey no need internet",
        "offline_mode": "Offline mode",
        "local_model": "Local model",
        "sqlite_retrieval": "SQLite search",
        "no_cloud_dependency": "No cloud",
        "mission_control": "Mission Control",
        "demo_scenarios": "Demo Scenarios",
        "daily_advisor": "Daily Advisor",
        "inventory_advisor": "Stock Advisor",
        "cashflow_advisor": "Money Advisor",
        "offline_status": "Offline Status",
        "response_language": "Answer language",
        "select_language": "Select language",
        "back_to_mission_control": "Back to Mission Control",
        "local_only": "Local only",
        "operational_guidance_only": "Business guide only",
        "choose_advisor": "Choose advisor to reason through your business question.",
        "daily_operations_advisor": "Daily Operations Advisor",
        "inventory_and_stock_check": "Inventory and Stock Check",
        "cashflow_pressure_coach": "Cashflow Pressure Coach",
        "offline_system_status": "Offline System Status",
        "your_operations_question": "Your business question",
        "your_question": "Your question",
        "get_operating_guidance": "Get business guide",
        "running_local_model": "Local model dey run...",
        "loading_message": (
            "AfrekaOS don hear your question. E dey build local context and run "
            "the model. This one fit take 30 to 90 seconds for CPU."
        ),
        "operating_guidance": "Business Guide",
        "runtime_summary": "Runtime summary",
        "runtime_status": "Runtime status",
        "model_path_exists": "Model dey there",
        "llama_binary": "Llama binary",
        "retrieval_index": "Search index",
        "locked_candidate": "Locked model",
        "retrieval_grounded": "Grounded for search",
        "direct_answer_mode": "Direct answer mode",
        "yes": "yes",
        "no": "no",
        "request_received": "We don see am",
        "building_retrieval_index": "Building local index",
        "retrieving_sme_context": "Getting business context",
        "building_grounded_prompt": "Building prompt",
        "running_qwen_model": "Running Qwen model",
        "formatting_answer": "Formatting answer",
        "complete": "Done",
        "failed": "Fail",
        "queued": "for queue",
        "running": "dey run",
        "inference_time_warning": (
            "This one fit take 30 to 90 seconds for CPU."
        ),
        "boundary_warning": (
            "AfrekaOS dey give business guide only. E no be accounting, bank, "
            "salary, tax, loan, or ERP system."
        ),
        "error_title": "AfrekaOS get local error.",
        "check_terminal_logs": "Check terminal logs.",
        "check_model_present": "model/afrekaos.gguf dey there?",
        "check_llama_available": "llama-completion dey available?",
        "check_timeout": "The request time out?",
        "suggested_checks": "Things to check",
        "error_summary": "Wetin happen",
        "current_route": "Current route",
        "job_not_found": "Job no find",
        "job_not_found_detail": "no find. E fit don expire (jobs dey memory only).",
        "demo_intro": "Ready-made business scenarios. Click to submit to advisor.",
        "run_this_scenario": "Run this one",
        "demo_low_sales": "Low sales, stock finish, supplier delay",
        "demo_expansion": "Expansion readiness",
        "demo_inventory": "Stock pressure",
        "demo_cash": "Money pressure and customer credit",
        "empty_answer": "(model no give answer)",
        "enter_question": "Abeg write your business question.",
        "prompt_echo_removed": "Prompt echo comot from display.",
        "footer": (
            "AfrekaOS Offline — local only. No cloud. Business guide, no be "
            "accounting/bank/salary/tax/ERP system."
        ),
    },
}


# Localized default advisor prompts (the textarea default text).
DEFAULT_PROMPTS: dict[str, dict[str, str]] = {
    "en": {
        "daily": (
            "A small shop has low sales, missing fast-moving stock, supplier "
            "delay, and more customers asking for credit. Give a short "
            "operating checklist."
        ),
        "inventory": (
            "I have two fast-moving items out of stock and a supplier that is "
            "delayed. What should I check, and how do I avoid overstocking "
            "slow-moving items?"
        ),
        "cashflow": (
            "Customers are asking for credit and my cash records are "
            "irregular. What should I check before extending credit?"
        ),
    },
    "fr": {
        "daily": (
            "Une petite boutique a des ventes en baisse, des articles à forte "
            "rotation en rupture, un fournisseur en retard, et plus de "
            "clients demandant du crédit. Donnez une courte checklist."
        ),
        "inventory": (
            "J'ai deux articles à forte rotation en rupture et un fournisseur "
            "en retard. Que dois-je vérifier pour éviter le surstock ?"
        ),
        "cashflow": (
            "Les clients demandent du crédit et mes registres de caisse sont "
            "irréguliers. Que dois-je vérifier avant d'accorder du crédit ?"
        ),
    },
}


# Localized demo scenarios: (title_key, advisor_action, advisor_name_key,
# prompt). The prompt text controls the answer language; titles come from
# the UI bundle.
def _build_demo_scenarios(language: str = "en") -> list[tuple[str, str, str, str]]:
    """Return demo scenarios with localized titles/prompts for a language."""
    lang = normalize_language_code(language)
    b = get_ui_bundle(lang)
    # Prompt defaults: use the localized daily/inventory/cashflow prompts
    # where available, else English.
    prompts = DEFAULT_PROMPTS.get(lang, DEFAULT_PROMPTS["en"])
    return [
        (b["demo_low_sales"], "/advisor/daily", b["daily_operations_advisor"],
         prompts["daily"]),
        (b["demo_expansion"], "/advisor/daily", b["daily_operations_advisor"],
         prompts["daily"]),
        (b["demo_inventory"], "/advisor/inventory", b["inventory_and_stock_check"],
         prompts["inventory"]),
        (b["demo_cash"], "/advisor/cashflow", b["cashflow_pressure_coach"],
         prompts["cashflow"]),
    ]


def get_ui_text(key: str, language: str = "en") -> str:
    """Return a localized UI string. Falls back to English, then to the key."""
    lang = normalize_language_code(language)
    bundle = UI_TEXT_BUNDLES.get(lang, UI_TEXT_BUNDLES["en"])
    return bundle.get(key, UI_TEXT_BUNDLES["en"].get(key, key))


def get_ui_bundle(language: str = "en") -> dict[str, str]:
    """Return the full UI text bundle for a language (English fallback)."""
    lang = normalize_language_code(language)
    # Merge English defaults with the selected language so missing keys fall back.
    base = dict(UI_TEXT_BUNDLES["en"])
    base.update(UI_TEXT_BUNDLES.get(lang, {}))
    return base


def get_default_prompt(advisor: str, language: str = "en") -> str:
    """Return the localized default textarea prompt for an advisor."""
    lang = normalize_language_code(language)
    prompts = DEFAULT_PROMPTS.get(lang, DEFAULT_PROMPTS["en"])
    key = advisor.split("/")[-1] if "/" in advisor else advisor
    return prompts.get(key, DEFAULT_PROMPTS["en"].get(key, ""))


def get_demo_scenarios(language: str = "en") -> list[tuple[str, str, str, str]]:
    """Return localized demo scenarios (title, action, advisor, prompt)."""
    return _build_demo_scenarios(language)


def get_boundary_warning(language: str = "en") -> str:
    """Return the localized operational boundary warning."""
    return get_ui_text("boundary_warning", language)


def get_footer_text(language: str = "en") -> str:
    """Return the localized footer text."""
    return get_ui_text("footer", language)


def get_progress_steps(language: str = "en") -> list[str]:
    """Return the localized ordered job progress steps."""
    b = get_ui_bundle(language)
    return [
        b["request_received"],
        b["building_retrieval_index"],
        b["retrieving_sme_context"],
        b["building_grounded_prompt"],
        b["running_qwen_model"],
        b["formatting_answer"],
        b["complete"],
    ]


__all__ = [
    "DEFAULT_LANGUAGE",
    "LANGUAGES",
    "LANGUAGE_INSTRUCTIONS",
    "UI_TEXT_BUNDLES",
    "DEFAULT_PROMPTS",
    "get_supported_languages",
    "normalize_language_code",
    "get_language_label",
    "get_language_native",
    "get_language_instruction",
    "is_supported_language",
    "language_summary",
    "get_ui_text",
    "get_ui_bundle",
    "get_default_prompt",
    "get_demo_scenarios",
    "get_boundary_warning",
    "get_footer_text",
    "get_progress_steps",
]
