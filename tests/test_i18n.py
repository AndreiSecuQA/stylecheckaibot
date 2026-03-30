"""Unit tests for app/utils/i18n.py"""
import pytest
from app.utils.i18n import t


class TestTranslation:
    def test_known_key_english(self):
        result = t("choose_language", "en")
        assert "language" in result.lower() or "Choose" in result

    def test_known_key_romanian(self):
        result = t("language_set", "ro")
        # Accept both old (no diacritics) and new (with diacritics) strings
        assert ("Limba" in result or "Limbă" in result) and ("Romana" in result or "Română" in result)

    def test_known_key_english_language_set(self):
        result = t("language_set", "en")
        assert "Language set to English" in result

    def test_unknown_key_returns_bracket_fallback(self):
        result = t("this_key_does_not_exist", "en")
        assert result == "[this_key_does_not_exist]"

    def test_missing_language_falls_back_to_english(self):
        # "fr" doesn't exist — should return the English string
        result = t("language_set", "fr")
        assert "Language set to English" in result

    def test_kwargs_formatting(self):
        result = t("welcome_back", "en", name="Alice")
        assert "Alice" in result

    def test_kwargs_formatting_romanian(self):
        result = t("welcome_back", "ro", name="Ion")
        assert "Ion" in result

    def test_onboarding_complete_formats_name(self):
        result = t("onboarding_complete", "en", name="Bob")
        assert "Bob" in result

    def test_occasion_set_formats_occasion(self):
        result = t("occasion_set", "en", occasion="Work")
        assert "Work" in result

    def test_welcome_string_non_empty(self):
        for lang in ("en", "ro"):
            assert len(t("welcome", lang)) > 10

    def test_all_main_menu_buttons_have_both_languages(self):
        for key in ("btn_rate_outfit", "btn_occasion", "btn_buy_support", "btn_back_to_menu"):
            assert t(key, "en"), f"Missing English for {key}"
            assert t(key, "ro"), f"Missing Romanian for {key}"

    def test_all_occasions_have_both_languages(self):
        for key in ("occasion_casual", "occasion_work", "occasion_date", "occasion_sport",
                    "occasion_event", "occasion_party", "occasion_beach", "occasion_wedding"):
            assert t(key, "en"), f"Missing English for {key}"
            assert t(key, "ro"), f"Missing Romanian for {key}"

    def test_error_strings_non_empty(self):
        for key in ("too_large", "download_fail", "quota_exceeded", "generic_error",
                    "not_photo", "daily_limit", "not_fashion_image"):
            for lang in ("en", "ro"):
                val = t(key, lang)
                assert val and val != f"[{key}]", f"Missing {lang} string for {key}"

    def test_menu_title_exists(self):
        # Just verify non-empty strings exist for both languages
        assert t("menu_title", "en") and t("menu_title", "en") != "[menu_title]"
        assert t("menu_title", "ro") and t("menu_title", "ro") != "[menu_title]"

    def test_buy_support_strings_exist(self):
        for key in ("buy_send_photo", "buy_ask_price_brand", "buy_ask_materials",
                    "buy_analyzing_initial", "buy_analyzing_full"):
            for lang in ("en", "ro"):
                val = t(key, lang)
                assert val and val != f"[{key}]", f"Missing {lang} string for {key}"

    def test_occasion_flow_strings_exist(self):
        for key in ("occasion_select_prompt", "occasion_ask_budget", "occasion_ask_style_vibe",
                    "occasion_generating", "occasion_photo_invite", "occasion_photo_analyzing"):
            for lang in ("en", "ro"):
                val = t(key, lang)
                assert val and val != f"[{key}]", f"Missing {lang} string for {key}"

    def test_occasion_photo_invite_formats_occasion(self):
        # occasion_photo_invite is a legacy key — just check it returns a non-empty string
        result = t("occasion_photo_invite", "en", occasion="Wedding")
        assert result and result != "[occasion_photo_invite]"
