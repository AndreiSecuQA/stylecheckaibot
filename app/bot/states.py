from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_weight = State()


class RateOutfit(StatesGroup):
    waiting_for_photo = State()
    viewing_results = State()


class OccasionSuggestions(StatesGroup):
    waiting_for_occasion = State()
    waiting_for_budget = State()
    waiting_for_style_vibe = State()
    viewing_suggestions = State()


class BuySupport(StatesGroup):
    waiting_for_photo = State()
    waiting_for_price_brand = State()
    waiting_for_materials = State()
    viewing_analysis = State()
