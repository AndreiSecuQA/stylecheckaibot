"""Internationalisation strings for StyleCheckAIBot. Supported: 'en', 'ro', 'ru'."""
from __future__ import annotations
from typing import Dict

_STRINGS: Dict[str, Dict[str, str]] = {

    # ── Language picker ──────────────────────────────────────────────────────
    "choose_language": {
        "en": "Please choose your language:",
        "ro": "Alege limba ta:",
        "ru": "Выбери язык:",
    },
    "language_set": {
        "en": "Language set to English! 🇬🇧",
        "ro": "Limbă setată la Română! 🇷🇴",
        "ru": "Язык установлен на Русский! 🇷🇺",
    },

    # ── Onboarding ───────────────────────────────────────────────────────────
    "ask_name": {
        "en": "👋 What's your name?",
        "ro": "👋 Cum te numești?",
        "ru": "👋 Как тебя зовут?",
    },
    "ask_height": {
        "en": "📏 What's your height in cm? (e.g. 175)",
        "ro": "📏 Ce înălțime ai în cm? (ex: 175)",
        "ru": "📏 Какой у тебя рост в см? (например, 175)",
    },
    "ask_weight": {
        "en": "⚖️ What's your weight in kg? (e.g. 70)",
        "ro": "⚖️ Cât cântărești în kg? (ex: 70)",
        "ru": "⚖️ Какой у тебя вес в кг? (например, 70)",
    },
    "invalid_number": {
        "en": "Please enter a valid number.",
        "ro": "Te rog introduci un număr valid.",
        "ru": "Пожалуйста, введи корректное число.",
    },
    "height_range_error": {
        "en": "Please enter a height between 100 and 250 cm.",
        "ro": "Te rog introduci o înălțime între 100 și 250 cm.",
        "ru": "Пожалуйста, введи рост от 100 до 250 см.",
    },
    "weight_range_error": {
        "en": "Please enter a weight between 30 and 300 kg.",
        "ro": "Te rog introduci o greutate între 30 și 300 kg.",
        "ru": "Пожалуйста, введи вес от 30 до 300 кг.",
    },

    # ── Style Criteria ────────────────────────────────────────────────────────
    "ask_criteria": {
        "en": (
            "🎯 What should I focus on when analyzing your outfits?\n\n"
            "All criteria are selected by default. Tap to deselect what you don't need.\n"
            "Select at least 1."
        ),
        "ro": (
            "🎯 Pe ce să mă concentrez când îți analizez ținutele?\n\n"
            "Toate criteriile sunt selectate implicit. Apasă pentru a deselecta.\n"
            "Selectează cel puțin 1."
        ),
        "ru": (
            "🎯 На что мне обращать внимание при анализе твоих образов?\n\n"
            "Все критерии выбраны по умолчанию. Нажми, чтобы отменить выбор.\n"
            "Выбери хотя бы 1."
        ),
    },
    "criteria_color_harmony":    {"en": "🎨 Color Harmony",      "ro": "🎨 Armonie Cromatică",   "ru": "🎨 Цветовая Гармония"},
    "criteria_body_proportions": {"en": "📐 Body Proportions",   "ro": "📐 Proporții Corp",       "ru": "📐 Пропорции Тела"},
    "criteria_fit_silhouette":   {"en": "👔 Fit & Silhouette",   "ro": "👔 Croială & Siluetă",    "ru": "👔 Посадка & Силуэт"},
    "criteria_occasion_fit":     {"en": "📅 Occasion Fit",       "ro": "📅 Potrivire Ocazie",     "ru": "📅 По Случаю"},
    "criteria_fabric_texture":   {"en": "🧵 Fabric & Texture",   "ro": "🧵 Material & Textură",   "ru": "🧵 Ткань & Текстура"},
    "criteria_trends":           {"en": "✨ Trends",              "ro": "✨ Tendințe",              "ru": "✨ Тренды"},
    "criteria_accessories":      {"en": "💍 Accessories",        "ro": "💍 Accesorii",            "ru": "💍 Аксессуары"},
    "criteria_layering":         {"en": "🌊 Layering",           "ro": "🌊 Stratificare",         "ru": "🌊 Слои"},
    "criteria_footwear":         {"en": "👟 Footwear",           "ro": "👟 Încălțăminte",         "ru": "👟 Обувь"},
    "criteria_personal_style":   {"en": "🎭 Personal Style",     "ro": "🎭 Stil Personal",        "ru": "🎭 Личный Стиль"},
    "btn_criteria_done": {
        "en": "✅ Continue ({n} selected)",
        "ro": "✅ Continuă ({n} selectate)",
        "ru": "✅ Продолжить ({n} выбрано)",
    },

    # ── Feedback Style ────────────────────────────────────────────────────────
    "ask_feedback_style": {
        "en": "💬 How should I talk to you?",
        "ro": "💬 Cum vrei să îți vorbesc?",
        "ru": "💬 Как мне с тобой общаться?",
    },
    "feedback_short":     {"en": "⚡ Short & Punchy",       "ro": "⚡ Scurt & Direct",       "ru": "⚡ Коротко"},
    "feedback_friendly":  {"en": "😊 Friendly & Casual",   "ro": "😊 Prietenos",            "ru": "😊 Дружелюбно"},
    "feedback_diplomatic":{"en": "🤝 Diplomatic",          "ro": "🤝 Diplomatic",           "ru": "🤝 Дипломатично"},
    "feedback_detailed":  {"en": "📋 Detailed",            "ro": "📋 Detaliat",             "ru": "📋 Подробно"},

    # ── Access step (kept for legacy) ─────────────────────────────────────────
    "ask_access": {
        "en": "🔑 Almost done! Choose how to get access:",
        "ro": "🔑 Aproape gata! Alege cum să obții acces:",
        "ru": "🔑 Почти готово! Выбери способ доступа:",
    },
    "btn_enter_own_key": {
        "en": "🔑 Enter my Gemini API key",
        "ro": "🔑 Introduc propriul API key",
        "ru": "🔑 Ввести мой Gemini API ключ",
    },
    "btn_request_approval": {
        "en": "📨 Request access from admin",
        "ro": "📨 Solicit acces de la admin",
        "ru": "📨 Запросить доступ у админа",
    },
    "ask_gemini_key": {
        "en": "🔑 Paste your Gemini API key below.\nGet it free at: https://aistudio.google.com/app/apikey\n\nIt looks like: AIzaSy...",
        "ro": "🔑 Lipește API key-ul tău Gemini mai jos.\nÎl obții gratuit la: https://aistudio.google.com/app/apikey\n\nArată astfel: AIzaSy...",
        "ru": "🔑 Вставь свой Gemini API ключ.\nПолучи бесплатно: https://aistudio.google.com/app/apikey\n\nОн выглядит так: AIzaSy...",
    },
    "validating_key": {
        "en": "Validating your API key...",
        "ro": "Validez API key-ul tău...",
        "ru": "Проверяю твой API ключ...",
    },
    "key_valid": {
        "en": "✅ API key is valid! You have unlimited access.",
        "ro": "✅ API key valid! Ai acces nelimitat.",
        "ru": "✅ API ключ действителен! У тебя неограниченный доступ.",
    },
    "key_invalid": {
        "en": "❌ That API key doesn't seem to work. Please check it and try again.",
        "ro": "❌ Acel API key nu funcționează. Verifică-l și încearcă din nou.",
        "ru": "❌ Этот API ключ не работает. Проверь его и попробуй снова.",
    },
    "approval_requested": {
        "en": "📨 Request sent! You have 5 free analyses while you wait. Once approved, you'll have unlimited access. ✅",
        "ro": "📨 Cerere trimisă! Ai 5 analize gratuite cât aștepți. După aprobare, vei avea acces nelimitat. ✅",
        "ru": "📨 Запрос отправлен! У тебя есть 5 бесплатных анализов пока ждёшь. После одобрения — неограниченный доступ. ✅",
    },
    "approved_notification": {
        "en": "🎉 Great news! The admin approved your access. You now have unlimited analyses!",
        "ro": "🎉 Veste bună! Adminul ți-a aprobat accesul. Acum ai analize nelimitate!",
        "ru": "🎉 Отличные новости! Администратор одобрил твой доступ. Теперь у тебя неограниченные анализы!",
    },
    "denied_notification": {
        "en": "❌ Your access request was not approved. You can enter your own Gemini API key with /setkey.",
        "ro": "❌ Cererea ta de acces nu a fost aprobată. Poți introduce propriul tău Gemini API key cu /setkey.",
        "ru": "❌ Твой запрос не был одобрен. Ты можешь ввести свой Gemini API ключ командой /setkey.",
    },

    # ── Access limit ──────────────────────────────────────────────────────────
    "no_access": {
        "en": "🚫 You've used all your free analyses.\n\nTo continue:\n• Get your free Gemini API key at https://aistudio.google.com/app/apikey and type /setkey\n• Wait for admin approval",
        "ro": "🚫 Ai folosit toate analizele gratuite.\n\nPentru a continua:\n• Obține-ți gratuit un Gemini API key la https://aistudio.google.com/app/apikey și scrie /setkey\n• Așteaptă aprobarea adminului",
        "ru": "🚫 Ты использовал все бесплатные анализы.\n\nЧтобы продолжить:\n• Получи бесплатный Gemini API ключ на https://aistudio.google.com/app/apikey и введи /setkey\n• Жди одобрения администратора",
    },
    "free_uses_remaining": {
        "en": "ℹ️ {count} free {analyses} remaining.",
        "ro": "ℹ️ Mai ai {count} {analyses} gratuite.",
        "ru": "ℹ️ Осталось {count} бесплатных анализов.",
    },

    # ── Onboarding complete ───────────────────────────────────────────────────
    "onboarding_complete": {
        "en": "🎉 You're all set, {name}! Let's find your perfect style.",
        "ro": "🎉 Ești gata, {name}! Să găsim stilul tău perfect.",
        "ru": "🎉 Всё готово, {name}! Найдём твой идеальный стиль.",
    },
    "welcome_back": {
        "en": "👋 Welcome back, {name}!",
        "ro": "👋 Bun revenit, {name}!",
        "ru": "👋 С возвращением, {name}!",
    },
    "menu_title": {
        "en": "What would you like to do?",
        "ro": "Ce vrei să faci?",
        "ru": "Что хочешь сделать?",
    },
    "complete_profile_first": {
        "en": "Please complete your profile first. Type /start to begin.",
        "ro": "Te rog completează-ți profilul mai întâi. Scrie /start pentru a începe.",
        "ru": "Пожалуйста, сначала заполни профиль. Напиши /start чтобы начать.",
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
        "ru": (
            "👗 Добро пожаловать в StyleCheckAI — твой личный AI-стилист!\n\n"
            "📸 Оценить аутфит — отправь фото, получи мгновенный отзыв\n"
            "👔 Образы для случая — идеи образов для любого мероприятия\n"
            "🛍 Советы по покупке — умные советы перед покупкой\n\n"
            "Начнём!"
        ),
    },

    # ── Main menu button labels ───────────────────────────────────────────────
    "btn_rate_outfit":  {"en": "📸 Rate My Outfit",       "ro": "📸 Evaluează Ținuta",          "ru": "📸 Оценить аутфит"},
    "btn_occasion":     {"en": "👔 Occasion Outfits",     "ro": "👔 Ținute pentru Ocazii",      "ru": "👔 Образы для случая"},
    "btn_buy_support":  {"en": "🛍 Buy Support",          "ro": "🛍 Sfaturi Cumpărături",       "ru": "🛍 Советы по покупке"},
    "btn_back_to_menu": {"en": "🏠 Back to Menu",         "ro": "🏠 Înapoi la Meniu",           "ru": "🏠 Главное меню"},
    "btn_settings":     {"en": "⚙️ My Profile",           "ro": "⚙️ Profilul Meu",              "ru": "⚙️ Мой профиль"},

    # ── Settings / Profile ────────────────────────────────────────────────────
    "settings_title": {
        "en": "⚙️ Your Profile",
        "ro": "⚙️ Profilul Tău",
        "ru": "⚙️ Твой профиль",
    },
    "settings_summary": {
        "en": "👤 {name}\n📏 Height: {height} cm\n⚖️ Weight: {weight} kg\n🌐 Language: {language}\n🎯 Criteria: {criteria_count} selected\n💬 Feedback style: {feedback_style}\n\nWhat would you like to change?",
        "ro": "👤 {name}\n📏 Înălțime: {height} cm\n⚖️ Greutate: {weight} kg\n🌐 Limbă: {language}\n🎯 Criterii: {criteria_count} selectate\n💬 Stil feedback: {feedback_style}\n\nCe vrei să schimbi?",
        "ru": "👤 {name}\n📏 Рост: {height} см\n⚖️ Вес: {weight} кг\n🌐 Язык: {language}\n🎯 Критерии: {criteria_count} выбрано\n💬 Стиль ответов: {feedback_style}\n\nЧто хочешь изменить?",
    },
    "settings_edit_language":     {"en": "🌐 Change Language",       "ro": "🌐 Schimbă Limba",             "ru": "🌐 Сменить язык"},
    "settings_edit_body":         {"en": "📏 Update Height/Weight",  "ro": "📏 Actualizează Înălțime/Greutate", "ru": "📏 Обновить рост/вес"},
    "settings_edit_criteria":     {"en": "🎯 Update Style Criteria", "ro": "🎯 Actualizează Criterii Stil", "ru": "🎯 Обновить критерии стиля"},
    "settings_edit_feedback":     {"en": "💬 Feedback Style",        "ro": "💬 Stil Feedback",              "ru": "💬 Стиль ответов"},
    "settings_saved": {
        "en": "✅ Settings saved!",
        "ro": "✅ Setări salvate!",
        "ru": "✅ Настройки сохранены!",
    },
    "settings_ask_new_height": {
        "en": "📏 Enter your new height in cm:",
        "ro": "📏 Introdu noua înălțime în cm:",
        "ru": "📏 Введи новый рост в см:",
    },
    "settings_ask_new_weight": {
        "en": "⚖️ Enter your new weight in kg:",
        "ro": "⚖️ Introdu noul greutate în kg:",
        "ru": "⚖️ Введи новый вес в кг:",
    },

    # ── Rate My Outfit flow ───────────────────────────────────────────────────
    "rate_send_photo": {
        "en": "📸 Send me a photo of your outfit and I'll give you instant style feedback!",
        "ro": "📸 Trimite-mi o poză cu ținuta ta și îți dau feedback instant de stil!",
        "ru": "📸 Отправь мне фото своего образа и я дам мгновенную оценку стиля!",
    },
    "rate_analyzing": {
        "en": "✨ Analyzing your outfit...",
        "ro": "✨ Analizez ținuta ta...",
        "ru": "✨ Анализирую твой образ...",
    },
    "btn_tips_for_10": {
        "en": "✨ Tips for 10/10",
        "ro": "✨ Sfaturi pentru 10/10",
        "ru": "✨ Советы для 10/10",
    },
    "generating_tips": {
        "en": "Creating your tips for a 10/10...",
        "ro": "Creez sfaturile pentru 10/10...",
        "ru": "Создаю советы для 10/10...",
    },
    "btn_check_fabric": {
        "en": "🧵 Check Fabric Quality",
        "ro": "🧵 Verifică Calitatea Materialului",
        "ru": "🧵 Проверить качество ткани",
    },
    "checking_fabric": {
        "en": "🧵 Analyzing fabric quality...",
        "ro": "🧵 Analizez calitatea materialului...",
        "ru": "🧵 Анализирую качество ткани...",
    },
    "photo_deleted": {
        "en": "🗑 Your photo has been automatically deleted from our servers to protect your privacy.",
        "ro": "🗑 Poza ta a fost ștearsă automat de pe serverele noastre pentru a-ți proteja confidențialitatea.",
        "ru": "🗑 Твоё фото автоматически удалено с наших серверов для защиты конфиденциальности.",
    },

    # ── Occasion Outfits flow ─────────────────────────────────────────────────
    "occasion_select_prompt": {
        "en": "👔 Choose an occasion:",
        "ro": "👔 Alege o ocazie:",
        "ru": "👔 Выбери случай:",
    },
    "occasion_generating": {
        "en": "👔 Generating outfit ideas for you...",
        "ro": "👔 Generez idei de ținute pentru tine...",
        "ru": "👔 Генерирую идеи образов для тебя...",
    },

    # ── Occasions ─────────────────────────────────────────────────────────────
    "occasion_casual":  {"en": "Casual",   "ro": "Casual",      "ru": "Повседневный"},
    "occasion_work":    {"en": "Work",     "ro": "Serviciu",    "ru": "Работа"},
    "occasion_date":    {"en": "Date",     "ro": "Întâlnire",   "ru": "Свидание"},
    "occasion_sport":   {"en": "Sport",    "ro": "Sport",       "ru": "Спорт"},
    "occasion_event":   {"en": "Event",    "ro": "Eveniment",   "ru": "Мероприятие"},
    "occasion_party":   {"en": "Party",    "ro": "Petrecere",   "ru": "Вечеринка"},
    "occasion_beach":   {"en": "Beach",    "ro": "Plajă",       "ru": "Пляж"},
    "occasion_wedding": {"en": "Wedding",  "ro": "Nuntă",       "ru": "Свадьба"},
    "occasion_set": {
        "en": "Occasion set to: {occasion}",
        "ro": "Ocazie setată la: {occasion}",
        "ru": "Случай установлен: {occasion}",
    },

    # ── Buy Support flow ──────────────────────────────────────────────────────
    "buy_send_photo": {
        "en": "🛍 Send me a photo of the item — on a hanger or worn.",
        "ro": "🛍 Trimite-mi o poză cu articolul — pe umeraș sau purtat.",
        "ru": "🛍 Отправь мне фото вещи — на вешалке или надето.",
    },
    "buy_analyzing_initial": {
        "en": "🔍 Analyzing the item...",
        "ro": "🔍 Analizez articolul...",
        "ru": "🔍 Анализирую вещь...",
    },
    "btn_add_brand_price": {
        "en": "💰 Add brand & price for a rating",
        "ro": "💰 Adaugă brand & preț pentru rating",
        "ru": "💰 Добавить бренд и цену для рейтинга",
    },
    "buy_ask_price_brand": {
        "en": "💶 What's the brand and price? (e.g. 'Zara, 150 RON' or 'Nike, $80')",
        "ro": "💶 Care e brandul și prețul? (ex: 'Zara, 150 RON' sau 'Nike, $80')",
        "ru": "💶 Какой бренд и цена? (например, 'Zara, 2000 руб' или 'Nike, $80')",
    },
    "buy_analyzing_rating": {
        "en": "⭐ Calculating rating...",
        "ro": "⭐ Calculez ratingul...",
        "ru": "⭐ Вычисляю рейтинг...",
    },
    "btn_analyze_another": {
        "en": "📸 Analyze another item",
        "ro": "📸 Analizează alt articol",
        "ru": "📸 Анализировать другую вещь",
    },

    # ── Admin ─────────────────────────────────────────────────────────────────
    "admin_approval_request": {
        "en": "🔔 New access request:\n\nUser: {name}\nID: {user_id}\nLanguage: {lang}",
        "ro": "🔔 Cerere nouă de acces:\n\nUser: {name}\nID: {user_id}\nLimbă: {lang}",
        "ru": "🔔 Новый запрос доступа:\n\nПользователь: {name}\nID: {user_id}\nЯзык: {lang}",
    },
    "admin_approved": {
        "en": "✅ User {user_id} approved.",
        "ro": "✅ Utilizatorul {user_id} a fost aprobat.",
        "ru": "✅ Пользователь {user_id} одобрен.",
    },
    "admin_denied": {
        "en": "❌ User {user_id} denied.",
        "ro": "❌ Utilizatorul {user_id} a fost refuzat.",
        "ru": "❌ Пользователь {user_id} отклонён.",
    },
    "admin_not_configured": {
        "en": "⚠️ ADMIN_TELEGRAM_ID not set. Add it to your environment variables.",
        "ro": "⚠️ ADMIN_TELEGRAM_ID nu e setat. Adaugă-l în variabilele de mediu.",
        "ru": "⚠️ ADMIN_TELEGRAM_ID не установлен. Добавь его в переменные среды.",
    },

    # ── Errors & misc ─────────────────────────────────────────────────────────
    "not_fashion_image": {
        "en": "👗 I can only analyze clothing and outfits. Please send a fashion photo!",
        "ro": "👗 Pot analiza doar haine și ținute. Te rog trimite o poză cu modă!",
        "ru": "👗 Я могу анализировать только одежду и образы. Пожалуйста, отправь модное фото!",
    },
    "too_large": {
        "en": "📦 Photo is too large. Please send a smaller image (max 10MB).",
        "ro": "📦 Poza este prea mare. Te rog trimite o imagine mai mică (max 10MB).",
        "ru": "📦 Фото слишком большое. Отправь изображение меньшего размера (макс. 10МБ).",
    },
    "download_fail": {
        "en": "⚠️ Could not download the photo. Please try again.",
        "ro": "⚠️ Nu am putut descărca poza. Te rog încearcă din nou.",
        "ru": "⚠️ Не удалось загрузить фото. Попробуй снова.",
    },
    "quota_exceeded": {
        "en": "⏳ AI service is busy right now. Please wait a moment and try again!",
        "ro": "⏳ Serviciul AI este ocupat acum. Așteaptă un moment și încearcă din nou!",
        "ru": "⏳ AI-сервис сейчас занят. Подожди немного и попробуй снова!",
    },
    "generic_error": {
        "en": "⚠️ Something went wrong. Please try again in a moment.",
        "ro": "⚠️ Ceva nu a mers. Te rog încearcă din nou în scurt timp.",
        "ru": "⚠️ Что-то пошло не так. Попробуй снова через минуту.",
    },
    "not_photo": {
        "en": "📸 Please send a photo, not a file.",
        "ro": "📸 Te rog trimite o poză, nu un fișier.",
        "ru": "📸 Пожалуйста, отправь фото, не файл.",
    },
    "daily_limit": {
        "en": "🚫 You've reached your 15 analyses/day limit. Come back tomorrow!",
        "ro": "🚫 Ai atins limita de 15 analize pe zi. Revino mâine!",
        "ru": "🚫 Ты достиг лимита 15 анализов в день. Возвращайся завтра!",
    },
    "send_photo_first": {
        "en": "📸 Please send a photo first.",
        "ro": "📸 Te rog trimite mai întâi o poză.",
        "ru": "📸 Пожалуйста, сначала отправь фото.",
    },
    "unknown": {
        "en": "I didn't understand that. Please use the menu buttons.",
        "ro": "Nu am înțeles. Te rog folosește butoanele din meniu.",
        "ru": "Я не понял. Пожалуйста, используй кнопки меню.",
    },

    # ── Legacy keys ───────────────────────────────────────────────────────────
    "btn_get_perfect":          {"en": "✨ Tips for 10/10",          "ro": "✨ Sfaturi pentru 10/10",     "ru": "✨ Советы для 10/10"},
    "btn_change_colors":        {"en": "✨ Tips for 10/10",          "ro": "✨ Sfaturi pentru 10/10",     "ru": "✨ Советы для 10/10"},
    "btn_send_another":         {"en": "📸 Analyze another item",   "ro": "📸 Analizează alt articol",  "ru": "📸 Анализировать другую вещь"},
    "generating_perfect":       {"en": "Creating tips for 10/10...", "ro": "Creez sfaturile...",         "ru": "Создаю советы..."},
    "generating_colors":        {"en": "Creating tips for 10/10...", "ro": "Creez sfaturile...",         "ru": "Создаю советы..."},
    "occasion_photo_invite":    {"en": "Here are your outfit ideas!", "ro": "Iată ideile de ținute!",    "ru": "Вот идеи образов!"},
    "occasion_photo_analyzing": {"en": "Generating ideas...",        "ro": "Generez idei...",            "ru": "Генерирую идеи..."},
    "buy_ask_materials":        {"en": "Any info about the material?", "ro": "Informații despre material?", "ru": "Информация о материале?"},
    "buy_analyzing_full":       {"en": "⭐ Calculating rating...",   "ro": "⭐ Calculez ratingul...",    "ru": "⭐ Вычисляю рейтинг..."},
    "analyzing":                {"en": "Analyzing...",               "ro": "Analizez...",                "ru": "Анализирую..."},
    "no_recent_outfit":         {"en": "Please send a photo first.", "ro": "Te rog trimite mai întâi o poză.", "ru": "Сначала отправь фото."},
    "generating_outfit":        {"en": "Generating outfit ideas...", "ro": "Generez idei de ținute...",  "ru": "Генерирую идеи образов..."},
    "generating_occasion":      {"en": "Generating ideas...",        "ro": "Generez idei...",            "ru": "Генерирую идеи..."},
    "occasion_ask_budget":      {"en": "What's your budget?",        "ro": "Care e bugetul tău?",        "ru": "Какой у тебя бюджет?"},
    "occasion_ask_style_vibe":  {"en": "Describe your style.",       "ro": "Descrie stilul tău.",        "ru": "Опиши свой стиль."},
}


def t(key: str, lang: str, **kwargs: str) -> str:
    entry = _STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("en") or f"[{key}]"
    return text.format(**kwargs) if kwargs else text
