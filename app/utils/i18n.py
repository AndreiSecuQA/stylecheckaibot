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
        "ro": "Limba setata la Romana!",
    },

    # ── Onboarding ───────────────────────────────────────────────────────────
    "ask_name": {
        "en": "What is your name? (I'll use it to personalise your experience)",
        "ro": "Cum te numesti? (Il voi folosi pentru a-ti personaliza experienta)",
    },
    "ask_height": {
        "en": "Great! Now, what is your height in cm? (e.g. 175)",
        "ro": "Super! Acum, ce inaltime ai in cm? (ex: 175)",
    },
    "ask_weight": {
        "en": "Almost done! What is your weight in kg? (e.g. 70)",
        "ro": "Aproape gata! Cat cantaresti in kg? (ex: 70)",
    },
    "invalid_number": {
        "en": "Please enter a valid number.",
        "ro": "Te rog introdu un numar valid.",
    },
    "height_range_error": {
        "en": "Please enter a height between 100 and 250 cm.",
        "ro": "Te rog introdu o inaltime intre 100 si 250 cm.",
    },
    "weight_range_error": {
        "en": "Please enter a weight between 30 and 300 kg.",
        "ro": "Te rog introdu o greutate intre 30 si 300 kg.",
    },
    "onboarding_complete": {
        "en": "You're all set, {name}! Let's find your perfect style.",
        "ro": "Esti gata, {name}! Sa gasim stilul tau perfect.",
    },
    "welcome_back": {
        "en": "Welcome back, {name}! Here's your menu.",
        "ro": "Bun revenit, {name}! Iata meniul tau.",
    },
    "menu_title": {
        "en": "Here is your menu:",
        "ro": "Iata meniul tau:",
    },
    "complete_profile_first": {
        "en": "Please complete your profile first. Type /start to begin.",
        "ro": "Te rog completeaza-ti profilul mai intai. Scrie /start pentru a incepe.",
    },

    # ── Welcome ──────────────────────────────────────────────────────────────
    "welcome": {
        "en": (
            "Welcome to StyleCheckAIBot - your AI-powered personal stylist!\n\n"
            "Here is what I can do:\n"
            "📸 Rate My Outfit - send a photo and get instant feedback\n"
            "👔 Occasion Outfits - get outfit ideas for any occasion\n"
            "🛍 Buy Support - get advice before buying clothes\n\n"
            "Choose an option from the menu below to get started!"
        ),
        "ro": (
            "Bun venit la StyleCheckAIBot - stilistul tau personal cu AI!\n\n"
            "Iata ce pot face:\n"
            "📸 Evalueaza Tinuta - trimite o poza si primesti feedback instant\n"
            "👔 Tinute pentru Ocazii - idei de tinute pentru orice ocazie\n"
            "🛍 Sfaturi Cumparaturi - sfaturi inainte de a cumpara haine\n\n"
            "Alege o optiune din meniu pentru a incepe!"
        ),
    },

    # ── Main menu button labels ───────────────────────────────────────────────
    "btn_rate_outfit": {"en": "📸 Rate My Outfit",       "ro": "📸 Evalueaza Tinuta"},
    "btn_occasion":    {"en": "👔 Occasion Outfits",     "ro": "👔 Tinute pentru Ocazii"},
    "btn_buy_support": {"en": "🛍 Buy Support",          "ro": "🛍 Sfaturi Cumparaturi"},
    "btn_back_to_menu":{"en": "🏠 Back to Menu",         "ro": "🏠 Inapoi la Meniu"},

    # ── Rate My Outfit flow ───────────────────────────────────────────────────
    "rate_send_photo": {
        "en": "📸 Send me a photo of your outfit and I will give you a full style analysis!",
        "ro": "📸 Trimite-mi o poza cu tinuta ta si iti voi face o analiza completa de stil!",
    },
    "rate_analyzing": {
        "en": "Analyzing your outfit...",
        "ro": "Analizez tinuta ta...",
    },
    "btn_get_perfect": {
        "en": "✨ Get 10/10 Outfit",
        "ro": "✨ Obtine Tinuta Perfecta",
    },
    "btn_change_colors": {
        "en": "🎨 Change Colors",
        "ro": "🎨 Schimba Culorile",
    },
    "generating_perfect": {
        "en": "Creating your perfect 10/10 outfit...",
        "ro": "Creez tinuta perfecta 10/10...",
    },
    "generating_colors": {
        "en": "Suggesting better color combinations...",
        "ro": "Sugerez combinatii de culori mai bune...",
    },

    # ── Occasion Outfits flow ─────────────────────────────────────────────────
    "occasion_select_prompt": {
        "en": "👔 What is the occasion? Choose one:",
        "ro": "👔 Care este ocazia? Alege una:",
    },
    "occasion_ask_budget": {
        "en": "💰 What is your budget for this occasion? (e.g. $50, 200 RON, or just say 'any')",
        "ro": "💰 Care este bugetul tau pentru aceasta ocazie? (ex: 200 RON, $50 sau 'orice')",
    },
    "occasion_ask_style_vibe": {
        "en": "🎨 How would you describe your style vibe? (e.g. minimalist, bold, classic, casual chic)",
        "ro": "🎨 Cum ai descrie stilul tau? (ex: minimalist, indraznet, clasic, casual chic)",
    },
    "occasion_generating": {
        "en": "Generating outfit ideas for you...",
        "ro": "Generez idei de tinute pentru tine...",
    },
    "occasion_photo_invite": {
        "en": (
            "You can now send me photos of specific clothing items and I will tell you "
            "if they work for {occasion}. Or tap Back to Menu to exit."
        ),
        "ro": (
            "Acum poti trimite poze cu articole de imbracaminte si iti voi spune "
            "daca merg pentru {occasion}. Sau apasa Inapoi la Meniu pentru a iesi."
        ),
    },
    "occasion_photo_analyzing": {
        "en": "Checking if this works for {occasion}...",
        "ro": "Verific daca merge pentru {occasion}...",
    },
    "btn_send_another": {
        "en": "📸 Send Another Photo",
        "ro": "📸 Trimite Alta Poza",
    },

    # ── Occasions ─────────────────────────────────────────────────────────────
    "occasion_casual":  {"en": "Casual",     "ro": "Casual"},
    "occasion_work":    {"en": "Work",        "ro": "Serviciu"},
    "occasion_date":    {"en": "Date",        "ro": "Intalnire"},
    "occasion_sport":   {"en": "Sport",       "ro": "Sport"},
    "occasion_event":   {"en": "Event",       "ro": "Eveniment"},
    "occasion_party":   {"en": "Party",       "ro": "Petrecere"},
    "occasion_beach":   {"en": "Beach",       "ro": "Plaja"},
    "occasion_wedding": {"en": "Wedding",     "ro": "Nunta"},
    "occasion_set": {
        "en": "Occasion set to: {occasion}",
        "ro": "Ocazie setata la: {occasion}",
    },

    # ── Buy Support flow ──────────────────────────────────────────────────────
    "buy_send_photo": {
        "en": "🛍 Send me a photo of the clothing item you are thinking of buying!",
        "ro": "🛍 Trimite-mi o poza cu articolul de imbracaminte pe care vrei sa-l cumperi!",
    },
    "buy_analyzing_initial": {
        "en": "Getting first impressions of this item...",
        "ro": "Imi formez prima impresie despre acest articol...",
    },
    "buy_ask_price_brand": {
        "en": "💶 What is the price and brand? (e.g. 'Nike, $80' or 'Zara, 150 RON')",
        "ro": "💶 Care este pretul si brandul? (ex: 'Nike, $80' sau 'Zara, 150 RON')",
    },
    "buy_ask_materials": {
        "en": "🧵 What do you know about the material or fabric quality? (e.g. '100% cotton', 'synthetic', or 'not sure')",
        "ro": "🧵 Ce stii despre material sau calitatea tesaturii? (ex: '100% bumbac', 'sintetic', sau 'nu stiu')",
    },
    "buy_analyzing_full": {
        "en": "Running full value analysis and rating...",
        "ro": "Fac analiza completa si evaluarea valorii...",
    },
    "btn_analyze_another": {
        "en": "🛍 Analyze Another Item",
        "ro": "🛍 Analizeaza Alt Articol",
    },

    # ── Errors & misc ─────────────────────────────────────────────────────────
    "not_fashion_image": {
        "en": (
            "I can only analyze fashion items and clothing. "
            "Please send a photo of an outfit, garment, or clothing item. "
            "I am here to help with your style!"
        ),
        "ro": (
            "Pot analiza doar articole de moda si imbracaminte. "
            "Te rog trimite o poza cu o tinuta, un articol vestimentar sau o piesa de imbracaminte. "
            "Sunt aici sa te ajut cu stilul tau!"
        ),
    },
    "too_large": {
        "en": "Photo is too large. Please send a smaller image.",
        "ro": "Poza este prea mare. Te rog trimite o imagine mai mica.",
    },
    "download_fail": {
        "en": "Could not download the photo. Please try again.",
        "ro": "Nu am putut descarca poza. Te rog incearca din nou.",
    },
    "quota_exceeded": {
        "en": "The AI service is at capacity right now. Please wait a minute and try again!",
        "ro": "Serviciul AI este ocupat acum. Te rog asteapta un minut si incearca din nou!",
    },
    "generic_error": {
        "en": "AI service is temporarily unavailable. Please try again in a moment.",
        "ro": "Serviciul AI este temporar indisponibil. Incearca din nou in scurt timp.",
    },
    "not_photo": {
        "en": "Please send a photo, not a file.",
        "ro": "Te rog trimite o poza, nu un fisier.",
    },
    "daily_limit": {
        "en": "You have reached your daily outfit check limit. Come back tomorrow!",
        "ro": "Ai atins limita zilnica de verificari. Revino maine!",
    },
    "send_photo_first": {
        "en": "Please send a photo first so I can help you.",
        "ro": "Te rog trimite mai intai o poza pentru a te putea ajuta.",
    },
    "unknown": {
        "en": "I did not understand that. Please use the menu buttons below.",
        "ro": "Nu am inteles. Te rog foloseste butoanele din meniu.",
    },
    "analyzing": {
        "en": "Analyzing your outfit...",
        "ro": "Analizez tinuta ta...",
    },
    "no_recent_outfit": {
        "en": "Please send a photo first so I can work with your outfit!",
        "ro": "Te rog trimite mai intai o poza cu tinuta ta!",
    },
    "generating_outfit": {
        "en": "Generating your perfect 10/10 outfit suggestion...",
        "ro": "Generez sugestia pentru tinuta perfecta 10/10...",
    },
    "generating_occasion": {
        "en": "Adapting your outfit for a different occasion...",
        "ro": "Adaptez tinuta ta pentru o alta ocazie...",
    },
}


def t(key: str, lang: str, **kwargs: str) -> str:
    entry = _STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("en") or f"[{key}]"
    return text.format(**kwargs) if kwargs else text
