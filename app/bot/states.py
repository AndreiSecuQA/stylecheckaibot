from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    waiting_for_name = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_access = State()     # Gemini key OR request admin approval


class RateOutfit(StatesGroup):
    waiting_for_photo = State()
    viewing_results = State()


class OccasionSuggestions(StatesGroup):
    waiting_for_occasion = State()
    viewing_suggestions = State()


class BuySupport(StatesGroup):
    waiting_for_photo = State()
    viewing_initial_feedback = State()   # After photo, optional brand/price
    waiting_for_brand_price = State()    # User chose to add brand + price
    viewing_rating = State()             # After star rating shown
