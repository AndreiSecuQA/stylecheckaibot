import re
from typing import Optional

from app.services.gemini_service import analyze_image, ask_text
from app.utils.logger import logger


class NotFashionImageError(Exception):
    """Raised when the submitted image does not contain fashion or clothing content."""
    pass


def _strip_markdown(text: str) -> str:
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_\n]+)_{1,3}", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"^\s*[*\-+]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _check_fashion_sentinel(raw: str) -> None:
    if "NOT_FASHION" in raw[:60].upper():
        raise NotFashionImageError()


def _build_body_context(name: Optional[str], height_cm: Optional[int], weight_kg: Optional[int], lang: str) -> str:
    if not any([name, height_cm, weight_kg]):
        return ""
    parts = []
    if name:
        if lang == "ru":
            parts.append(f"Имя: {name}")
        elif lang == "en":
            parts.append(f"Name: {name}")
        else:
            parts.append(f"Nume: {name}")
    if height_cm:
        if lang == "ru":
            parts.append(f"Рост: {height_cm}см")
        elif lang == "en":
            parts.append(f"Height: {height_cm}cm")
        else:
            parts.append(f"Inaltime: {height_cm}cm")
    if weight_kg:
        if lang == "ru":
            parts.append(f"Вес: {weight_kg}кг")
        elif lang == "en":
            parts.append(f"Weight: {weight_kg}kg")
        else:
            parts.append(f"Greutate: {weight_kg}kg")
    if lang == "ru":
        prefix = "Профиль пользователя: "
    elif lang == "en":
        prefix = "User profile: "
    else:
        prefix = "Profilul utilizatorului: "
    return prefix + ", ".join(parts)


_SENTINEL_INSTRUCTION = (
    "\n\nIMPORTANT: If this image does NOT show clothing, fashion items, an outfit, "
    "or a person wearing clothes, respond ONLY with the exact token: NOT_FASHION"
)

# ── Criteria → prompt label maps ─────────────────────────────────────────────
_CRITERIA_LABELS_LANG = {
    "color_harmony":    {"en": "color harmony",          "ro": "armonie cromatică",        "ru": "цветовую гармонию"},
    "body_proportions": {"en": "body proportions",       "ro": "proporțiile corpului",      "ru": "пропорции тела"},
    "fit_silhouette":   {"en": "fit and silhouette",     "ro": "croială și siluetă",        "ru": "посадку и силуэт"},
    "occasion_fit":     {"en": "occasion appropriateness","ro": "potrivirea cu ocazia",     "ru": "соответствие случаю"},
    "fabric_texture":   {"en": "fabric and texture",     "ro": "material și textură",       "ru": "ткань и текстуру"},
    "trends":           {"en": "current fashion trends", "ro": "tendințele actuale",        "ru": "актуальные тренды"},
    "accessories":      {"en": "accessory coordination", "ro": "coordonarea accesoriilor",  "ru": "сочетание аксессуаров"},
    "layering":         {"en": "layering technique",     "ro": "tehnica de stratificare",   "ru": "технику многослойности"},
    "footwear":         {"en": "footwear coordination",  "ro": "coordonarea încălțămintei", "ru": "сочетание обуви"},
    "personal_style":   {"en": "personal style",         "ro": "stilul personal",           "ru": "личный стиль"},
}

_FEEDBACK_INSTRUCTIONS = {
    "short":      "Be extremely brief. Use short bullet points only. Maximum 5 lines total. No lengthy explanations.",
    "friendly":   "Use a warm, encouraging, casual and friendly tone. Be supportive and positive.",
    "diplomatic": "Be balanced and constructive. Highlight positives first, then give gentle, tactful suggestions.",
    "detailed":   "Be thorough and comprehensive. Provide specific details and professional analysis.",
}


def _build_criteria_instruction(criteria_str: str, lang: str) -> str:
    if not criteria_str:
        return ""
    items = [c.strip() for c in criteria_str.split(",") if c.strip()]
    if not items:
        return ""
    labels = [
        _CRITERIA_LABELS_LANG.get(c, {}).get(lang)
        or _CRITERIA_LABELS_LANG.get(c, {}).get("en", c)
        for c in items
    ]
    prefix = {
        "en": "\nFocus especially on: ",
        "ro": "\nConcentrează-te în special pe: ",
        "ru": "\nУделяй особое внимание: ",
    }.get(lang, "\nFocus especially on: ")
    return prefix + ", ".join(labels) + "."


def _build_feedback_instruction(style: str) -> str:
    return "\n" + _FEEDBACK_INSTRUCTIONS.get(style, _FEEDBACK_INSTRUCTIONS["friendly"])


# ── Prompts ───────────────────────────────────────────────────────────────────

_OUTFIT_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "Analyze this outfit and respond EXACTLY in this emoji format. Keep each line SHORT:\n\n"
        "🎨 Style Score: X/10\n"
        "✅ Colors: <one short sentence>\n"
        "👔 Fit: <one short sentence>\n"
        "📐 Proportions: <one silhouette tip — e.g. high-waist to elongate legs, oversized top to balance hips>\n"
        "📍 Occasion: <best occasion in 3 words>\n"
        "💡 Quick tip: <one specific actionable tip>\n\n"
        "Be direct and confident. No greetings, no markdown, plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Analizeaza aceasta tinuta si raspunde EXACT in acest format cu emoji. Fiecare linie SCURTA:\n\n"
        "🎨 Scor stil: X/10\n"
        "✅ Culori: <o propozitie scurta>\n"
        "👔 Croiala: <o propozitie scurta>\n"
        "📐 Proportii: <un sfat de silueta — ex: talie inalta pentru picioare lungi, bluza oversize pentru echilibru>\n"
        "📍 Ocazie: <cea mai buna ocazie in 3 cuvinte>\n"
        "💡 Sfat rapid: <un sfat concret de imbunatatire>\n\n"
        "Fii direct si sigur. Fara salutari, fara markdown, doar text simplu."
        "{sentinel}"
    ),
    "ru": (
        "Ты профессиональный стилист. {body_context}\n"
        "Проанализируй этот образ и ответь СТРОГО в этом формате. Каждая строка КОРОТКАЯ:\n\n"
        "🎨 Оценка стиля: X/10\n"
        "✅ Цвета: <одно короткое предложение>\n"
        "👔 Посадка: <одно короткое предложение>\n"
        "📐 Пропорции: <один совет по силуэту — например, высокая талия удлинит ноги>\n"
        "📍 Случай: <лучший случай в 3 словах>\n"
        "💡 Быстрый совет: <один конкретный совет>\n\n"
        "Будь прямым и уверенным. Без приветствий, без markdown, только простой текст."
        "{sentinel}"
    ),
}

_TIPS_FOR_10_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "Look at this outfit and give exactly 3 specific tips to make it a 10/10.\n"
        "Use this format:\n\n"
        "✨ Tips for a 10/10:\n\n"
        "1️⃣ <specific tip — what to add, swap, or change>\n"
        "2️⃣ <specific tip — color, fabric, or accessory>\n"
        "3️⃣ <specific tip — fit or styling trick>\n\n"
        "Be specific (name colors, items, brands if helpful). Plain text only, no markdown."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Uita-te la aceasta tinuta si da exact 3 sfaturi concrete pentru a o aduce la 10/10.\n"
        "Foloseste acest format:\n\n"
        "✨ Sfaturi pentru 10/10:\n\n"
        "1️⃣ <sfat concret — ce sa adaugi, schimbi sau inlocuiesti>\n"
        "2️⃣ <sfat concret — culoare, material sau accesoriu>\n"
        "3️⃣ <sfat concret — croiala sau truc de styling>\n\n"
        "Fii specific (numeste culori, piese, branduri daca ajuta). Doar text simplu, fara markdown."
        "{sentinel}"
    ),
    "ru": (
        "Ты профессиональный стилист. {body_context}\n"
        "Посмотри на этот образ и дай ровно 3 конкретных совета для 10/10.\n"
        "Используй этот формат:\n\n"
        "✨ Советы для 10/10:\n\n"
        "1️⃣ <конкретный совет — что добавить, заменить или изменить>\n"
        "2️⃣ <конкретный совет — цвет, ткань или аксессуар>\n"
        "3️⃣ <конкретный совет — посадка или стилистический приём>\n\n"
        "Будь конкретным (называй цвета, вещи, бренды). Только простой текст, без markdown."
        "{sentinel}"
    ),
}

_OCCASION_IDEAS_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "Suggest 3 outfit ideas for: {occasion}\n"
        "Base suggestions on the user's height ({height_cm}cm) and weight ({weight_kg}kg) only.\n"
        "Use this format for each outfit:\n\n"
        "1️⃣ <Outfit name>\n"
        "• Top: <specific item>\n"
        "• Bottom: <specific item>\n"
        "• Shoes: <specific item>\n"
        "• Extra: <one accessory>\n\n"
        "2️⃣ ... (repeat)\n\n"
        "3️⃣ ... (repeat)\n\n"
        "Keep it practical and specific. Plain text only, no markdown."
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Sugereaza 3 idei de tinute pentru: {occasion}\n"
        "Bazeaza sugestiile doar pe inaltimea ({height_cm}cm) si greutatea ({weight_kg}kg) utilizatorului.\n"
        "Foloseste acest format pentru fiecare tinuta:\n\n"
        "1️⃣ <Numele tinutei>\n"
        "• Sus: <piesa specifica>\n"
        "• Jos: <piesa specifica>\n"
        "• Pantofi: <piesa specifica>\n"
        "• Extra: <un accesoriu>\n\n"
        "2️⃣ ... (repeta)\n\n"
        "3️⃣ ... (repeta)\n\n"
        "Fii practic si specific. Doar text simplu, fara markdown."
    ),
    "ru": (
        "Ты профессиональный стилист. {body_context}\n"
        "Предложи 3 идеи образов для: {occasion}\n"
        "Основывай советы только на росте ({height_cm}см) и весе ({weight_kg}кг) пользователя.\n"
        "Используй этот формат для каждого образа:\n\n"
        "1️⃣ <Название образа>\n"
        "• Верх: <конкретная вещь>\n"
        "• Низ: <конкретная вещь>\n"
        "• Обувь: <конкретная вещь>\n"
        "• Доп: <один аксессуар>\n\n"
        "2️⃣ ... (повторить)\n\n"
        "3️⃣ ... (повторить)\n\n"
        "Будь практичным и конкретным. Только простой текст, без markdown."
    ),
}

_FABRIC_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist and fabric expert.\n"
        "Look at this clothing item and analyze the visible fabric and texture.\n"
        "Use this EXACT format:\n\n"
        "🧵 Fabric Analysis:\n\n"
        "🔍 Material: <what fabric this appears to be — e.g. cotton, polyester, linen, wool, silk>\n"
        "✅ Quality: <premium / good / average / low — plus one short reason>\n"
        "🌡 Season: <best season(s) to wear this fabric>\n"
        "💡 Tip: <one care or styling tip based on this fabric>\n\n"
        "Be honest. If the fabric looks cheap (e.g. synthetic shine, pill texture), say so. "
        "Plain text only, no markdown."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist si expert in materiale textile.\n"
        "Uita-te la acest articol vestimentar si analizeaza materialul si textura vizibila.\n"
        "Foloseste EXACT acest format:\n\n"
        "🧵 Analiza Material:\n\n"
        "🔍 Material: <ce material pare sa fie — ex: bumbac, poliester, in, lana, matase>\n"
        "✅ Calitate: <premium / buna / medie / slaba — plus un motiv scurt>\n"
        "🌡 Sezon: <cel mai bun sezon pentru acest material>\n"
        "💡 Sfat: <un sfat de ingrijire sau stilizare bazat pe material>\n\n"
        "Fii sincer. Daca materialul arata ieftin (ex: stralucire sintetica, aspect pufos), spune-o. "
        "Doar text simplu, fara markdown."
        "{sentinel}"
    ),
    "ru": (
        "Ты профессиональный стилист и эксперт по тканям.\n"
        "Посмотри на эту одежду и проанализируй видимую ткань и текстуру.\n"
        "Используй ТОЧНО этот формат:\n\n"
        "🧵 Анализ ткани:\n\n"
        "🔍 Материал: <что это за ткань — например, хлопок, полиэстер, лён, шерсть, шёлк>\n"
        "✅ Качество: <премиум / хорошее / среднее / низкое — плюс одна короткая причина>\n"
        "🌡 Сезон: <лучший сезон для этой ткани>\n"
        "💡 Совет: <один совет по уходу или стилизации>\n\n"
        "Будь честным. Если ткань выглядит дёшево — скажи об этом. "
        "Только простой текст, без markdown."
        "{sentinel}"
    ),
}

_BUY_INITIAL_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist and shopping advisor.\n"
        "Look at this clothing item and give a quick first impression.\n"
        "Use this EXACT format:\n\n"
        "🛍 First impression:\n\n"
        "✅ Style: <versatile/trendy/classic — one word + one reason>\n"
        "🔍 Quality: <apparent quality from the photo in one sentence>\n"
        "📍 Works for: <2-3 occasions, comma separated>\n\n"
        "Keep it short and honest. Plain text only, no markdown."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist si consilier de cumparaturi.\n"
        "Uita-te la acest articol si da o prima impresie rapida.\n"
        "Foloseste EXACT acest format:\n\n"
        "🛍 Prima impresie:\n\n"
        "✅ Stil: <versatil/la moda/clasic — un cuvant + un motiv>\n"
        "🔍 Calitate: <calitatea aparenta din poza intr-o propozitie>\n"
        "📍 Merge pentru: <2-3 ocazii, separate prin virgula>\n\n"
        "Scurt si sincer. Doar text simplu, fara markdown."
        "{sentinel}"
    ),
    "ru": (
        "Ты профессиональный стилист и консультант по покупкам.\n"
        "Посмотри на эту одежду и дай быстрое первое впечатление.\n"
        "Используй ТОЧНО этот формат:\n\n"
        "🛍 Первое впечатление:\n\n"
        "✅ Стиль: <универсальный/трендовый/классический — одно слово + одна причина>\n"
        "🔍 Качество: <очевидное качество по фото в одном предложении>\n"
        "📍 Подходит для: <2-3 случая, через запятую>\n\n"
        "Коротко и честно. Только простой текст, без markdown."
        "{sentinel}"
    ),
}

_BUY_RATING_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist and shopping advisor. {body_context}\n"
        "The user wants to buy this clothing item.\n"
        "Brand and price: {price_brand}\n\n"
        "Give a concise buy recommendation. Use this EXACT format:\n\n"
        "RATING: X\n\n"
        "💶 Value: <one sentence on price vs quality>\n"
        "✅ Pro: <one main advantage>\n"
        "❌ Con: <one main disadvantage>\n"
        "🏷 Verdict: BUY IT or SKIP IT — <one short reason>\n\n"
        "Be honest and direct. Plain text only, no markdown."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist si consilier de cumparaturi. {body_context}\n"
        "Utilizatorul vrea sa cumpere acest articol.\n"
        "Brand si pret: {price_brand}\n\n"
        "Da o recomandare concisa. Foloseste EXACT acest format:\n\n"
        "RATING: X\n\n"
        "💶 Valoare: <o propozitie despre pret vs calitate>\n"
        "✅ Pro: <un avantaj principal>\n"
        "❌ Contra: <un dezavantaj principal>\n"
        "🏷 Verdict: CUMPARA sau NU CUMPARA — <un motiv scurt>\n\n"
        "Fii sincer si direct. Doar text simplu, fara markdown."
        "{sentinel}"
    ),
    "ru": (
        "Ты профессиональный стилист и консультант по покупкам. {body_context}\n"
        "Пользователь хочет купить эту вещь.\n"
        "Бренд и цена: {price_brand}\n\n"
        "Дай краткую рекомендацию. Используй ТОЧНО этот формат:\n\n"
        "RATING: X\n\n"
        "💶 Ценность: <одно предложение о соотношении цены и качества>\n"
        "✅ Плюс: <один главный плюс>\n"
        "❌ Минус: <один главный минус>\n"
        "🏷 Вердикт: КУПИТЬ или ПРОПУСТИТЬ — <одна короткая причина>\n\n"
        "Будь честным и прямым. Только простой текст, без markdown."
        "{sentinel}"
    ),
}

# Telegram's hard message limit with a small safety margin
_TG_MAX_LENGTH = 4000


def _truncate(text: str) -> str:
    """Trim text to Telegram's message length limit."""
    if len(text) <= _TG_MAX_LENGTH:
        return text
    return text[: _TG_MAX_LENGTH - 3] + "..."


def _parse_buy_rating(raw: str) -> str:
    clean = _strip_markdown(raw)
    stars_map = {1: "⭐☆☆☆☆", 2: "⭐⭐☆☆☆", 3: "⭐⭐⭐☆☆", 4: "⭐⭐⭐⭐☆", 5: "⭐⭐⭐⭐⭐"}
    match = re.search(r"RATING:\s*([1-5])", clean, re.IGNORECASE)
    if match:
        rating = int(match.group(1))
        stars = stars_map.get(rating, "")
        clean = re.sub(r"RATING:\s*[1-5]", f"{stars} {rating}/5", clean, flags=re.IGNORECASE)
    return clean


# ── Public functions ──────────────────────────────────────────────────────────

async def analyze_outfit(
    image_path: str,
    occasion: Optional[str],
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
    api_key: Optional[str] = None,
    style_criteria: Optional[str] = None,
    feedback_style: str = "friendly",
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _OUTFIT_PROMPT.get(lang, _OUTFIT_PROMPT["en"])
    criteria_instruction = _build_criteria_instruction(style_criteria or "", lang)
    feedback_instruction = _build_feedback_instruction(feedback_style)
    prompt = prompt_template.format(
        body_context=body_context,
        sentinel=_SENTINEL_INSTRUCTION,
    ) + criteria_instruction + feedback_instruction
    raw = await analyze_image(image_path, prompt, api_key=api_key)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def generate_tips_for_10(
    image_path: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
    api_key: Optional[str] = None,
    style_criteria: Optional[str] = None,
    feedback_style: str = "friendly",
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _TIPS_FOR_10_PROMPT.get(lang, _TIPS_FOR_10_PROMPT["en"])
    criteria_instruction = _build_criteria_instruction(style_criteria or "", lang)
    feedback_instruction = _build_feedback_instruction(feedback_style)
    prompt = prompt_template.format(
        body_context=body_context,
        sentinel=_SENTINEL_INSTRUCTION,
    ) + criteria_instruction + feedback_instruction
    raw = await analyze_image(image_path, prompt, api_key=api_key)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def analyze_fabric(
    image_path: str,
    lang: str = "en",
    api_key: Optional[str] = None,
    style_criteria: Optional[str] = None,
    feedback_style: str = "friendly",
) -> str:
    prompt_template = _FABRIC_PROMPT.get(lang, _FABRIC_PROMPT["en"])
    criteria_instruction = _build_criteria_instruction(style_criteria or "", lang)
    feedback_instruction = _build_feedback_instruction(feedback_style)
    prompt = prompt_template.format(sentinel=_SENTINEL_INSTRUCTION) + criteria_instruction + feedback_instruction
    raw = await analyze_image(image_path, prompt, api_key=api_key)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def generate_occasion_suggestions(
    occasion: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
    api_key: Optional[str] = None,
    style_criteria: Optional[str] = None,
    feedback_style: str = "friendly",
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    height_val = str(height_cm) if height_cm else "?"
    weight_val = str(weight_kg) if weight_kg else "?"
    prompt_template = _OCCASION_IDEAS_PROMPT.get(lang, _OCCASION_IDEAS_PROMPT["en"])
    criteria_instruction = _build_criteria_instruction(style_criteria or "", lang)
    feedback_instruction = _build_feedback_instruction(feedback_style)
    prompt = prompt_template.format(
        body_context=body_context,
        occasion=occasion,
        height_cm=height_val,
        weight_kg=weight_val,
    ) + criteria_instruction + feedback_instruction
    raw = await ask_text(prompt, api_key=api_key)
    return _truncate(_strip_markdown(raw))


async def analyze_buy_item_initial(
    image_path: str,
    lang: str = "en",
    api_key: Optional[str] = None,
    style_criteria: Optional[str] = None,
    feedback_style: str = "friendly",
) -> str:
    prompt_template = _BUY_INITIAL_PROMPT.get(lang, _BUY_INITIAL_PROMPT["en"])
    criteria_instruction = _build_criteria_instruction(style_criteria or "", lang)
    feedback_instruction = _build_feedback_instruction(feedback_style)
    prompt = prompt_template.format(sentinel=_SENTINEL_INSTRUCTION) + criteria_instruction + feedback_instruction
    raw = await analyze_image(image_path, prompt, api_key=api_key)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def analyze_buy_item_rating(
    image_path: str,
    price_brand: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
    api_key: Optional[str] = None,
    style_criteria: Optional[str] = None,
    feedback_style: str = "friendly",
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _BUY_RATING_PROMPT.get(lang, _BUY_RATING_PROMPT["en"])
    criteria_instruction = _build_criteria_instruction(style_criteria or "", lang)
    feedback_instruction = _build_feedback_instruction(feedback_style)
    prompt = prompt_template.format(
        body_context=body_context,
        price_brand=price_brand,
        sentinel=_SENTINEL_INSTRUCTION,
    ) + criteria_instruction + feedback_instruction
    raw = await analyze_image(image_path, prompt, api_key=api_key)
    _check_fashion_sentinel(raw)
    return _truncate(_parse_buy_rating(raw))


async def answer_question(user_text: str, lang: str = "en") -> str:
    prompts = {
        "en": f"You are a professional fashion stylist. Answer this fashion question briefly and confidently in 2-3 sentences. No markdown formatting, plain text only: {user_text}",
        "ro": f"Esti un stilist profesionist. Raspunde la aceasta intrebare de moda scurt si sigur in 2-3 propozitii, in romana. Fara formatare markdown, doar text simplu: {user_text}",
        "ru": f"Ты профессиональный стилист. Ответь на этот вопрос о моде кратко и уверенно в 2-3 предложениях на русском. Без markdown, только простой текст: {user_text}",
    }
    prompt = prompts.get(lang, prompts["en"])
    raw = await ask_text(prompt)
    return _truncate(_strip_markdown(raw))


# ── Legacy aliases (kept for backward compatibility with tests) ────────────────

async def generate_perfect_outfit(
    image_path: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    return await generate_tips_for_10(image_path, lang, name, height_cm, weight_kg)


async def generate_color_suggestions(
    image_path: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    return await generate_tips_for_10(image_path, lang, name, height_cm, weight_kg)


async def generate_occasion_outfit_ideas(
    occasion: str,
    budget: str = "",
    style_vibe: str = "",
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    return await generate_occasion_suggestions(occasion, lang, name, height_cm, weight_kg)


async def analyze_item_for_occasion(image_path: str, occasion: str, lang: str = "en") -> str:
    return await analyze_buy_item_initial(image_path, lang)


async def analyze_buy_item_full(
    image_path: str,
    price_brand: str,
    materials: str = "",
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    return await analyze_buy_item_rating(image_path, price_brand, lang, name, height_cm, weight_kg)
