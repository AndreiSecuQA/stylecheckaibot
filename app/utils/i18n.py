"""Internationalisation strings for StyleCheckAIBot. Supported: 'en', 'ro'."""
from __future__ import annotations
from typing import Dict

_STRINGS: Dict[str, Dict[str, str]] = {

    # ── Language picker ──────────────────────────────────────────────────────
    "choose_language": {
        "en": "Please choose your language / Alege limba ta:",
        "ro": "Please choose your language / Alege limba ta:",
    },
    "language_set": {
        "en": "Language set to English!",
        "ro": "Limba setată la Română!",
    },

    # ── Onboarding ───────────────────────────────────────────────────────────
    "ask_name": {
        "en": "👋 What's your name?",
        "ro": "👋 Cum te numești?",
    },
    "ask_height": {
        "en": "📏 What's your height in cm? (e.g. 175)",
        "ro": "📏 Ce înălțime ai în cm? (ex: 175)",
    },
    "ask_weight": {
        "en": "⚖️ What's your weight in kg? (e.g. 70)",
        "ro": "⚖️ Cât cântărești în kg? (ex: 70)",
    },
    "invalid_number": {
        "en": "Please enter a valid number.",
        "ro": "Te rog introduci un număr valid.",
    },
    "height_range_error": {
        "en": "Please enter a height between 100 and 250 cm.",
        "ro": "Te rog introduci o înălțime între 100 și 250 cm.",
    },
    "weight_range_error": {
        "en": "Please enter a weight between 30 and 300 kg.",
        "ro": "Te rog introduci o greutate între 30 și 300 kg.",
    },

    # ── Access step (onboarding) ──────────────────────────────────────────────
    "ask_access": {
        "en": (
            "🔑 Almost done! To use the AI features, choose one option:\n\n"
            "1️⃣ Enter your own Gemini API key (free, unlimited)\n"
            "   Get it here: https://aistudio.google.com/app/apikey\n\n"
            "2️⃣ Request access from the admin (you get 5 free analyses while waiting)\n\n"
            "Which do you prefer?"
        ),
        "ro": (
            "🔑 Aproape gata! Pentru a folosi funcțiile AI, alege o opțiune:\n\n"
            "1️⃣ Introdu propriul tău Gemini API key (gratuit, nelimitat)\n"
            "   Îl găsești aici: https://aistudio.google.com/app/apikey\n\n"
            "2️⃣ Solicită acces de la admin (primești 5 analize gratuite în așteptare)\n\n"
            "Ce preferi?"
        ),
    },
    "btn_enter_own_key": {
        "en": "🔑 Enter my Gemini API key",
        "ro": "🔑 Introduc propriul API key",
    },
    "btn_request_approval": {
        "en": "📨 Request access from admin",
        "ro": "📨 Solicit acces de la admin",
    },
    "ask_gemini_key": {
        "en": (
            "🔑 Paste your Gemini API key below.\n"
            "Get it free at: https://aistudio.google.com/app/apikey\n\n"
            "It looks like: AIzaSy..."
        ),
        "ro": (
            "🔑 Lipește API key-ul tău Gemini mai jos.\n"
            "Îl obții gratuit la: https://aistudio.google.com/app/apikey\n\n"
            "Arată astfel: AIzaSy..."
        ),
    },
    "validating_key": {
        "en": "Validating your API key...",
        "ro": "Validez API key-ul tău...",
    },
    "key_valid": {
        "en": "✅ API key is valid! You have unlimited access.",
        "ro": "✅ API key valid! Ai acces nelimitat.",
    },
    "key_invalid": {
        "en": "❌ That API key doesn't seem to work. Please check it and try again.",
        "ro": "❌ Acel API key nu funcționează. Verifică-l și încearcă din nou.",
    },
    "approval_requested": {
        "en": (
            "📨 Request sent to admin!\n\n"
            "You have 5 free analyses while you wait. "
            "Once approved, you'll have unlimited access. ✅"
        ),
        "ro": (
            "📨 Cerere trimisă adminului!\n\n"
            "Ai 5 analize gratuite cât aștepți. "
            "După aprobare, vei avea acces nelimitat. ✅"
        ),
    },
    "approved_notification": {
        "en": "🎉 Great news! The admin approved your access. You now have unlimited analyses!",
        "ro": "🎉 Veste bună! Adminul ți-a aprobat accesul. Acum ai analize nelimitate!",
    },
    "denied_notification": {
        "en": "❌ Your access request was not approved. You can still enter your own Gemini API key to continue.",
        "ro": "❌ Cererea ta de acces nu a fost aprobată. Poți introduce propriul tău Gemini API key pentru a continua.",
    },

    # ── Access limit ──────────────────────────────────────────────────────────
    "no_access": {
        "en": (
            "🚫 You've used all your free analyses.\n\n"
            "To continue, either:\n"
            "• Get your free Gemini API key at https://aistudio.google.com/app/apikey and type /setkey\n"
            "• Wait for admin approval"
        ),
        "ro": (
            "🚫 Ai folosit toate analizele gratuite.\n\n"
            "Pentru a continua:\n"
            "• Obține-ți gratuit un Gemini API key la https://aistudio.google.com/app/apikey și scrie /setkey\n"
            "• Așteaptă aprobarea adminului"
        ),
    },
    "free_uses_remaining": {
        "en": "ℹ️ {count} free {analyses} remaining.",
        "ro": "ℹ️ Mai ai {count} {analyses} gratuite.",
    },

    # ── Onboarding complete ───────────────────────────────────────────────────
    "onboarding_complete": {
        "en": "🎉 You're all set, {name}! Let's find your perfect style.",
        "ro": "🎉 Ești gata, {name}! Să găsim stilul tău perfect.",
    },
    "welcome_back": {
        "en": "👋 Welcome back, {name}!",
        "ro": "👋 Bun revenit, {name}!",
    },
    "menu_title": {
        "en": "What would you like to do?",
        "ro": "Ce vrei să faci?",
    },
    "complete_profile_first": {
        "en": "Please complete your profile first. Type /start to begin.",
        "ro": "Te rog completează-ți profilul mai întâi. Scrie /start pentru a începe.",
    },

    # ── Welcome ──────────────────────────────────────────────────────────────
    "welcome": {
        "en": (
            "👗 Welcome to StyleCheckAI — your personal AI stylist!\n\n"
            "📸 Rate My Outfit — send a photo, get instant feedback\n"
            "👔 Occasion Outfits — outfit ideas for any occasion\n"
            "🛍 Buy Support — smart advice before you buy\n\n"
            "Let's get started!"
        ),
        "ro": (
            "👗 Bun venit la StyleCheckAI — stilistul tău personal cu AI!\n\n"
            "📸 Evaluează Ținuta — trimite o poză, primești feedback instant\n"
            "👔 Ținute pentru Ocazii — idei de ținute pentru orice ocazie\n"
            "🛍 Sfaturi Cumpărături — sfaturi înainte să cumperi\n\n"
            "Să începem!"
        ),
    },

    # ── Main menu button labels ───────────────────────────────────────────────
    "btn_rate_outfit":  {"en": "📸 Rate My Outfit",       "ro": "📸 Evaluează Ținuta"},
    "btn_occasion":     {"en": "👔 Occasion Outfits",     "ro": "👔 Ținute pentru Ocazii"},
    "btn_buy_support":  {"en": "🛍 Buy Support",          "ro": "🛍 Sfaturi Cumpărături"},
    "btn_back_to_menu": {"en": "🏠 Back to Menu",         "ro": "🏠 Înapoi la Meniu"},

    # ── Rate My Outfit flow ───────────────────────────────────────────────────
    "rate_send_photo": {
        "en": "📸 Send me a photo of your outfit and I'll give you instant style feedback!",
        "ro": "📸 Trimite-mi o poză cu ținuta ta și îți dau feedback instant de stil!",
    },
    "rate_analyzing": {
        "en": "✨ Analyzing your outfit...",
        "ro": "✨ Analizez ținuta ta...",
    },
    "btn_tips_for_10": {
        "en": "✨ Tips for 10/10",
        "ro": "✨ Sfaturi pentru 10/10",
    },
    "generating_tips": {
        "en": "Creating your tips for a 10/10...",
        "ro": "Creez sfaturile pentru 10/10...",
    },
    "btn_check_fabric": {
        "en": "🧵 Check Fabric Quality",
        "ro": "🧵 Verifică Calitatea Materialului",
    },
    "checking_fabric": {
        "en": "🧵 Analyzing fabric quality...",
        "ro": "🧵 Analizez calitatea materialului...",
    },
    "photo_deleted": {
        "en": "🗑 Your photo has been automatically deleted from our servers to protect your privacy.",
        "ro": "🗑 Poza ta a fost ștearsă automat de pe serverele noastre pentru a-ți proteja confidențialitatea.",
    },

    # ── Occasion Outfits flow ─────────────────────────────────────────────────
    "occasion_select_prompt": {
        "en": "👔 Choose an occasion:",
        "ro": "👔 Alege o ocazie:",
    },
    "occasion_generating": {
        "en": "👔 Generating outfit ideas for you...",
        "ro": "👔 Generez idei de ținute pentru tine...",
    },

    # ── Occasions ─────────────────────────────────────────────────────────────
    "occasion_casual":  {"en": "Casual",   "ro": "Casual"},
    "occasion_work":    {"en": "Work",     "ro": "Serviciu"},
    "occasion_date":    {"en": "Date",     "ro": "Întâlnire"},
    "occasion_sport":   {"en": "Sport",    "ro": "Sport"},
    "occasion_event":   {"en": "Event",    "ro": "Eveniment"},
    "occasion_party":   {"en": "Party",    "ro": "Petrecere"},
    "occasion_beach":   {"en": "Beach",    "ro": "Plajă"},
    "occasion_wedding": {"en": "Wedding",  "ro": "Nuntă"},
    "occasion_set": {
        "en": "Occasion set to: {occasion}",
        "ro": "Ocazie setată la: {occasion}",
    },

    # ── Buy Support flow ──────────────────────────────────────────────────────
    "buy_send_photo": {
        "en": "🛍 Send me a photo of the item — on a hanger or worn.",
        "ro": "🛍 Trimite-mi o poză cu articolul — pe umeraș sau purtat.",
    },
    "buy_analyzing_initial": {
        "en": "🔍 Analyzing the item...",
        "ro": "🔍 Analizez articolul...",
    },
    "btn_add_brand_price": {
        "en": "💰 Add brand & price for a rating",
        "ro": "💰 Adaugă brand & preț pentru rating",
    },
    "buy_ask_price_brand": {
        "en": "💶 What's the brand and price? (e.g. 'Zara, 150 RON' or 'Nike, $80')",
        "ro": "💶 Care e brandul și prețul? (ex: 'Zara, 150 RON' sau 'Nike, $80')",
    },
    "buy_analyzing_rating": {
        "en": "⭐ Calculating rating...",
        "ro": "⭐ Calculez ratingul...",
    },
    "btn_analyze_another": {
        "en": "📸 Analyze another item",
        "ro": "📸 Analizează alt articol",
    },

    # ── Admin ─────────────────────────────────────────────────────────────────
    "admin_approval_request": {
        "en": "🔔 New access request:\n\nUser: {name}\nID: {user_id}\nLanguage: {lang}",
        "ro": "🔔 Cerere nouă de acces:\n\nUser: {name}\nID: {user_id}\nLimbă: {lang}",
    },
    "admin_approved": {
        "en": "✅ User {user_id} approved.",
        "ro": "✅ Utilizatorul {user_id} a fost aprobat.",
    },
    "admin_denied": {
        "en": "❌ User {user_id} denied.",
        "ro": "❌ Utilizatorul {user_id} a fost refuzat.",
    },
    "admin_not_configured": {
        "en": "⚠️ ADMIN_TELEGRAM_ID not set. Add it to your environment variables.",
        "ro": "⚠️ ADMIN_TELEGRAM_ID nu e setat. Adaugă-l în variabilele de mediu.",
    },

    # ── Errors & misc ─────────────────────────────────────────────────────────
    "not_fashion_image": {
        "en": "👗 I can only analyze clothing and outfits. Please send a fashion photo!",
        "ro": "👗 Pot analiza doar haine și ținute. Te rog trimite o poză cu modă!",
    },
    "too_large": {
        "en": "📦 Photo is too large. Please send a smaller image (max 10MB).",
        "ro": "📦 Poza este prea mare. Te rog trimite o imagine mai mică (max 10MB).",
    },
    "download_fail": {
        "en": "⚠️ Could not download the photo. Please try again.",
        "ro": "⚠️ Nu am putut descărca poza. Te rog încearcă din nou.",
    },
    "quota_exceeded": {
        "en": "⏳ AI service is busy right now. Please wait a moment and try again!",
        "ro": "⏳ Serviciul AI este ocupat acum. Așteaptă un moment și încearcă din nou!",
    },
    "generic_error": {
        "en": "⚠️ Something went wrong. Please try again in a moment.",
        "ro": "⚠️ Ceva nu a mers. Te rog încearcă din nou în scurt timp.",
    },
    "not_photo": {
        "en": "📸 Please send a photo, not a file.",
        "ro": "📸 Te rog trimite o poză, nu un fișier.",
    },
    "daily_limit": {
        "en": "🚫 Daily limit reached. Come back tomorrow!",
        "ro": "🚫 Limita zilnică atinsă. Revino mâine!",
    },
    "send_photo_first": {
        "en": "📸 Please send a photo first.",
        "ro": "📸 Te rog trimite mai întâi o poză.",
    },
    "unknown": {
        "en": "I didn't understand that. Please use the menu buttons.",
        "ro": "Nu am înțeles. Te rog folosește butoanele din meniu.",
    },

    # ── Legacy keys (kept for backward compatibility) ─────────────────────────
    "btn_get_perfect":       {"en": "✨ Tips for 10/10",           "ro": "✨ Sfaturi pentru 10/10"},
    "btn_change_colors":     {"en": "✨ Tips for 10/10",           "ro": "✨ Sfaturi pentru 10/10"},
    "btn_send_another":      {"en": "📸 Analyze another item",    "ro": "📸 Analizează alt articol"},
    "generating_perfect":    {"en": "Creating tips for 10/10...", "ro": "Creez sfaturile pentru 10/10..."},
    "generating_colors":     {"en": "Creating tips for 10/10...", "ro": "Creez sfaturile pentru 10/10..."},
    "occasion_photo_invite": {"en": "Here are your outfit ideas! Tap Back to Menu when done.", "ro": "Iată ideile de ținute! Apasă Înapoi la Meniu când ești gata."},
    "occasion_photo_analyzing": {"en": "Generating ideas...", "ro": "Generez idei..."},
    "buy_ask_materials":     {"en": "Any info about the material?", "ro": "Informații despre material?"},
    "buy_analyzing_full":    {"en": "⭐ Calculating rating...",    "ro": "⭐ Calculez ratingul..."},
    "buy_ask_price_brand":   {"en": "💶 What's the brand and price?", "ro": "💶 Care e brandul și prețul?"},
    "analyzing":             {"en": "Analyzing...",                "ro": "Analizez..."},
    "no_recent_outfit":      {"en": "Please send a photo first.",  "ro": "Te rog trimite mai întâi o poză."},
    "generating_outfit":     {"en": "Generating outfit ideas...", "ro": "Generez idei de ținute..."},
    "generating_occasion":   {"en": "Generating ideas...",        "ro": "Generez idei..."},
    "occasion_ask_budget":   {"en": "What's your budget?",        "ro": "Care e bugetul tău?"},
    "occasion_ask_style_vibe": {"en": "Describe your style.",     "ro": "Descrie stilul tău."},
    "buy_analyzing_initial": {"en": "🔍 Analyzing the item...",   "ro": "🔍 Analizez articolul..."},
}


def t(key: str, lang: str, **kwargs: str) -> str:
    entry = _STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("en") or f"[{key}]"
    return text.format(**kwargs) if kwargs else text
