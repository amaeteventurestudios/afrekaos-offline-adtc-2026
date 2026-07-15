"""Tests for app/language_mode.py (Task 006A).

Validates the controlled multilingual response configuration. Standard library
only. No model, no internet.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import language_mode as lm  # noqa: E402


class TestSupportedLanguages(unittest.TestCase):
    def test_all_six_languages_present(self) -> None:
        langs = lm.get_supported_languages()
        self.assertEqual(set(langs.keys()), {"en", "yo", "ha", "sw", "pcm", "fr"})

    def test_each_language_has_code_label_native(self) -> None:
        for code, info in lm.get_supported_languages().items():
            self.assertEqual(info["code"], code)
            self.assertTrue(info["label"])
            self.assertTrue(info["native"])

    def test_english_is_default(self) -> None:
        self.assertEqual(lm.DEFAULT_LANGUAGE, "en")


class TestNormalize(unittest.TestCase):
    def test_direct_codes(self) -> None:
        for code in ("en", "yo", "ha", "sw", "pcm", "fr"):
            self.assertEqual(lm.normalize_language_code(code), code)

    def test_case_insensitive(self) -> None:
        self.assertEqual(lm.normalize_language_code("FR"), "fr")
        self.assertEqual(lm.normalize_language_code("Yo"), "yo")

    def test_aliases(self) -> None:
        self.assertEqual(lm.normalize_language_code("yoruba"), "yo")
        self.assertEqual(lm.normalize_language_code("pidgin"), "pcm")
        self.assertEqual(lm.normalize_language_code("naija"), "pcm")
        self.assertEqual(lm.normalize_language_code("french"), "fr")
        self.assertEqual(lm.normalize_language_code("kiswahili"), "sw")

    def test_unknown_falls_back_to_english(self) -> None:
        self.assertEqual(lm.normalize_language_code("zz"), "en")
        self.assertEqual(lm.normalize_language_code(""), "en")
        self.assertEqual(lm.normalize_language_code(None), "en")  # type: ignore[arg-type]


class TestLabelsAndInstructions(unittest.TestCase):
    def test_labels(self) -> None:
        self.assertEqual(lm.get_language_label("fr"), "French")
        self.assertEqual(lm.get_language_label("pcm"), "Nigerian Pidgin")
        self.assertEqual(lm.get_language_label("zz"), "English")  # fallback

    def test_native_labels(self) -> None:
        self.assertEqual(lm.get_language_native("fr"), "Français")
        self.assertEqual(lm.get_language_native("pcm"), "Naija")

    def test_french_instruction_exists(self) -> None:
        instr = lm.get_language_instruction("fr")
        self.assertIn("French", instr)
        self.assertIn("Francophone", instr)

    def test_pidgin_instruction_exists(self) -> None:
        instr = lm.get_language_instruction("pcm")
        self.assertIn("Pidgin", instr)
        self.assertIn("respectful", instr)

    def test_instruction_fallback(self) -> None:
        instr = lm.get_language_instruction("zz")
        self.assertIn("English", instr)


class TestIsSupported(unittest.TestCase):
    def test_supported(self) -> None:
        for code in ("en", "yo", "ha", "sw", "pcm", "fr"):
            self.assertTrue(lm.is_supported_language(code))

    def test_unsupported(self) -> None:
        self.assertFalse(lm.is_supported_language("zz"))


class TestSummary(unittest.TestCase):
    def test_summary_shape(self) -> None:
        s = lm.language_summary()
        self.assertEqual(s["default"], "en")
        self.assertEqual(s["count"], 6)
        self.assertFalse(s["cloud_translation"])
        self.assertIn("fr", s["codes"])


class TestUiText(unittest.TestCase):
    def test_french_mission_control(self) -> None:
        fr = lm.get_ui_text("mission_control", "fr")
        self.assertEqual(fr, "Tableau de bord")

    def test_english_mission_control(self) -> None:
        self.assertEqual(lm.get_ui_text("mission_control", "en"), "Mission Control")

    def test_unknown_key_returns_key(self) -> None:
        self.assertEqual(lm.get_ui_text("nonexistent_key", "fr"), "nonexistent_key")

    def test_unknown_language_falls_back(self) -> None:
        self.assertEqual(lm.get_ui_text("mission_control", "zz"), "Mission Control")

    def test_bundle_merge(self) -> None:
        b = lm.get_ui_bundle("fr")
        # French value
        self.assertEqual(b["mission_control"], "Tableau de bord")
        # English fallback for a key not in French bundle (all keys present in
        # both, but this verifies the merge mechanism)
        self.assertIn("footer", b)

    def test_boundary_warning_localized(self) -> None:
        fr = lm.get_boundary_warning("fr")
        self.assertIn("comptabilité", fr.lower())
        en = lm.get_boundary_warning("en")
        self.assertIn("accounting", en.lower())

    def test_footer_localized(self) -> None:
        fr = lm.get_footer_text("fr")
        self.assertIn("cloud", fr.lower())

    def test_progress_steps_localized(self) -> None:
        fr = lm.get_progress_steps("fr")
        self.assertEqual(len(fr), 7)
        self.assertEqual(fr[0], "Demande reçue")
        self.assertEqual(fr[-1], "Terminé")
        en = lm.get_progress_steps("en")
        self.assertEqual(en[0], "Request received")

    def test_default_prompt_localized(self) -> None:
        fr = lm.get_default_prompt("daily", "fr")
        self.assertIn("boutique", fr.lower())
        en = lm.get_default_prompt("daily", "en")
        self.assertIn("shop", en.lower())

    def test_all_non_english_prompts_and_descriptions_are_localized(self) -> None:
        for language in ("fr", "yo", "ha", "sw", "pcm"):
            for advisor in ("daily", "inventory", "cashflow"):
                self.assertNotEqual(
                    lm.get_default_prompt(advisor, language),
                    lm.get_default_prompt(advisor, "en"),
                )
            self.assertNotEqual(
                lm.get_ui_text("inventory_advisor_description", language),
                lm.get_ui_text("inventory_advisor_description", "en"),
            )

    def test_demo_scenarios_localized(self) -> None:
        fr = lm.get_demo_scenarios("fr")
        self.assertEqual(len(fr), 4)
        self.assertIn("Ventes basses", fr[0][0])
        en = lm.get_demo_scenarios("en")
        self.assertNotEqual(lm.get_demo_scenarios("sw")[2][3], en[2][3])
        self.assertIn("Low sales", en[0][0])
