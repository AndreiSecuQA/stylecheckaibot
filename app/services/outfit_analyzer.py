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
        parts.append(f"Name: {name}" if lang == "en" else f"Nume: {name}")
    if height_cm:
        parts.append(f"Height: {height_cm}cm" if lang == "en" else f"Inaltime: {height_cm}cm")
    if weight_kg:
        parts.append(f"Weight: {weight_kg}kg" if lang == "en" else f"Greutate: {weight_kg}kg")
    prefix = "User profile: " if lang == "en" else "Profilul utilizatorului: "
    return prefix + ", ".join(parts)


_SENTINEL_INSTRUCTION = (
    "\n\nIMPORTANT: If this image does NOT show clothing, fashion items, an outfit, "
    "or a person wearing clothes, respond ONLY with the exact token: NOT_FASHION"
)

# ── Prompts ───────────────────────────────────────────────────────────────────

_OUTFIT_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "Analyze this outfit and respond EXACTLY in this emoji format. Keep each line SHORT:\n\n"
        "🎨 Style Score: X/10\n"
        "✅ Colors: <one short sentence>\n"
        "👔 Fit: <one short sentence>\n"
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
        "📍 Ocazie: <cea mai buna ocazie in 3 cuvinte>\n"
        "💡 Sfat rapid: <un sfat concret de imbunatatire>\n\n"
        "Fii direct si sigur. Fara salutari, fara markdown, doar text simplu."
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
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _OUTFIT_PROMPT.get(lang, _OUTFIT_PROMPT["en"])
    prompt = prompt_template.format(
        body_context=body_context,
        sentinel=_SENTINEL_INSTRUCTION,
    )
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
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _TIPS_FOR_10_PROMPT.get(lang, _TIPS_FOR_10_PROMPT["en"])
    prompt = prompt_template.format(body_context=body_context, sentinel=_SENTINEL_INSTRUCTION)
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
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    height_val = str(height_cm) if height_cm else "?"
    weight_val = str(weight_kg) if weight_kg else "?"
    prompt_template = _OCCASION_IDEAS_PROMPT.get(lang, _OCCASION_IDEAS_PROMPT["en"])
    prompt = prompt_template.format(
        body_context=body_context,
        occasion=occasion,
        height_cm=height_val,
        weight_kg=weight_val,
    )
    raw = await ask_text(prompt, api_key=api_key)
    return _truncate(_strip_markdown(raw))


async def analyze_buy_item_initial(
    image_path: str,
    lang: str = "en",
    api_key: Optional[str] = None,
) -> str:
    prompt_template = _BUY_INITIAL_PROMPT.get(lang, _BUY_INITIAL_PROMPT["en"])
    prompt = prompt_template.format(sentinel=_SENTINEL_INSTRUCTION)
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
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _BUY_RATING_PROMPT.get(lang, _BUY_RATING_PROMPT["en"])
    prompt = prompt_template.format(
        body_context=body_context,
        price_brand=price_brand,
        sentinel=_SENTINEL_INSTRUCTION,
    )
    raw = await analyze_image(image_path, prompt, api_key=api_key)
    _check_fashion_sentinel(raw)
    return _truncate(_parse_buy_rating(raw))


async def answer_question(user_text: str, lang: str = "en") -> str:
    prompts = {
        "en": f"You are a professional fashion stylist. Answer this fashion question briefly and confidently in 2-3 sentences. No markdown formatting, plain text only: {user_text}",
        "ro": f"Esti un stilist profesionist. Raspunde la aceasta intrebare de moda scurt si sigur in 2-3 propozitii, in romana. Fara formatare markdown, doar text simplu: {user_text}",
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
