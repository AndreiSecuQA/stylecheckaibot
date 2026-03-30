from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_criteria = State()
    waiting_for_feedback_style = State()


class EditProfile(StatesGroup):
    choosing_setting = State()
    editing_name = State()
    editing_height = State()
    editing_weight = State()
    editing_criteria = State()
    editing_feedback_style = State()


class RateOutfit(StatesGroup):
    waiting_for_photo = State()
    viewing_results = State()


class OccasionSuggestions(StatesGroup):
    waiting_for_occasion = State()
    viewing_suggestions = State()


class BuySupport(StatesGroup):
    waiting_for_photo = State()
    viewing_initial_feedback = State()
    waiting_for_brand_price = State()
    viewing_rating = State()
