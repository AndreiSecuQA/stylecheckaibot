"""Unit tests for app/bot/keyboards.py"""
import pytest
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


class TestLanguageKeyboard:
    def test_returns_inline_markup(self):
        from app.bot.keyboards import language_keyboard
        kb = language_keyboard()
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_has_two_language_buttons(self):
        from app.bot.keyboards import language_keyboard
        kb = language_keyboard()
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(buttons) == 2

    def test_has_english_button(self):
        from app.bot.keyboards import language_keyboard
        kb = language_keyboard()
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "lang:en" in callbacks

    def test_has_romanian_button(self):
        from app.bot.keyboards import language_keyboard
        kb = language_keyboard()
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "lang:ro" in callbacks


class TestMainMenuKeyboard:
    def test_returns_reply_markup(self):
        from app.bot.keyboards import main_menu_keyboard
        kb = main_menu_keyboard("en")
        assert isinstance(kb, ReplyKeyboardMarkup)

    def test_has_three_buttons_english(self):
        from app.bot.keyboards import main_menu_keyboard
        kb = main_menu_keyboard("en")
        all_buttons = [btn for row in kb.keyboard for btn in row]
        assert len(all_buttons) == 3

    def test_has_three_buttons_romanian(self):
        from app.bot.keyboards import main_menu_keyboard
        kb = main_menu_keyboard("ro")
        all_buttons = [btn for row in kb.keyboard for btn in row]
        assert len(all_buttons) == 3

    def test_rate_outfit_button_english(self):
        from app.bot.keyboards import main_menu_keyboard
        kb = main_menu_keyboard("en")
        texts = [btn.text for row in kb.keyboard for btn in row]
        assert "📸 Rate My Outfit" in texts

    def test_rate_outfit_button_romanian(self):
        from app.bot.keyboards import main_menu_keyboard
        kb = main_menu_keyboard("ro")
        texts = [btn.text for row in kb.keyboard for btn in row]
        # Accept both old and new Romanian strings
        assert any("Evalueaz" in t or "Tinuta" in t or "Ținuta" in t for t in texts)

    def test_buy_support_button_english(self):
        from app.bot.keyboards import main_menu_keyboard
        kb = main_menu_keyboard("en")
        texts = [btn.text for row in kb.keyboard for btn in row]
        assert "🛍 Buy Support" in texts


class TestOccasionKeyboard:
    def test_returns_inline_markup(self):
        from app.bot.keyboards import occasion_keyboard
        kb = occasion_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_has_eight_occasions(self):
        from app.bot.keyboards import occasion_keyboard
        kb = occasion_keyboard("en")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(buttons) == 8

    def test_all_callbacks_start_with_occasion(self):
        from app.bot.keyboards import occasion_keyboard
        kb = occasion_keyboard("en")
        for row in kb.inline_keyboard:
            for btn in row:
                assert btn.callback_data.startswith("occasion:"), f"Bad callback: {btn.callback_data}"

    def test_buttons_in_pairs(self):
        from app.bot.keyboards import occasion_keyboard
        kb = occasion_keyboard("en")
        for row in kb.inline_keyboard:
            assert len(row) == 2


class TestRateOutfitKeyboard:
    def test_returns_inline_markup(self):
        from app.bot.keyboards import rate_outfit_keyboard
        kb = rate_outfit_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_has_two_buttons(self):
        # Simplified: Tips for 10/10 + Back to Menu
        from app.bot.keyboards import rate_outfit_keyboard
        kb = rate_outfit_keyboard("en")
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(buttons) == 2

    def test_has_tips_for_10_callback(self):
        from app.bot.keyboards import rate_outfit_keyboard
        kb = rate_outfit_keyboard("en")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "action:tips_for_10" in callbacks

    def test_has_back_to_menu_callback(self):
        from app.bot.keyboards import rate_outfit_keyboard
        kb = rate_outfit_keyboard("en")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "action:back_to_menu" in callbacks


class TestOccasionPhotoKeyboard:
    def test_has_back_to_menu_callback(self):
        from app.bot.keyboards import occasion_photo_keyboard
        kb = occasion_photo_keyboard("en")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "action:back_to_menu" in callbacks

    def test_returns_inline_markup(self):
        from app.bot.keyboards import occasion_photo_keyboard
        kb = occasion_photo_keyboard("en")
        assert isinstance(kb, InlineKeyboardMarkup)


class TestBuyResultKeyboard:
    def test_has_analyze_another_callback(self):
        from app.bot.keyboards import buy_result_keyboard
        kb = buy_result_keyboard("en")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "action:analyze_another" in callbacks

    def test_has_back_to_menu_callback(self):
        from app.bot.keyboards import buy_result_keyboard
        kb = buy_result_keyboard("en")
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "action:back_to_menu" in callbacks


class TestPostAnalysisKeyboardLegacyAlias:
    def test_is_same_as_rate_outfit_keyboard(self):
        from app.bot.keyboards import post_analysis_keyboard, rate_outfit_keyboard
        kb1 = post_analysis_keyboard("en")
        kb2 = rate_outfit_keyboard("en")
        cb1 = [btn.callback_data for row in kb1.inline_keyboard for btn in row]
        cb2 = [btn.callback_data for row in kb2.inline_keyboard for btn in row]
        assert cb1 == cb2
