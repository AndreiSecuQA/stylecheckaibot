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
    text = re.sub(r"^\s*[*\-+]\s+", "- ", text, flags=re.MULTILINE)
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
        "Analyze this outfit photo and respond ONLY in this exact format, no extra text:\n\n"
        "Style Score: X/10\n"
        "Colors: <one sentence>\n"
        "Fit: <one sentence tailored to the body type>\n"
        "Occasion: <suitability for {occasion}>\n"
        "Suggestion: <1-2 specific actionable tips>\n\n"
        "Be concise, direct, and confident. No greetings, no closing remarks. "
        "Do not use any markdown formatting. Plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Analizeaza aceasta poza cu tinuta si raspunde DOAR in acest format exact, fara text suplimentar:\n\n"
        "Scor stil: X/10\n"
        "Culori: <o propozitie>\n"
        "Croiala: <o propozitie adaptata tipului de corp>\n"
        "Ocazie: <potrivire pentru {occasion}>\n"
        "Sugestie: <1-2 sfaturi concrete de imbunatatire>\n\n"
        "Fii concis, direct si sigur. Fara salutari, fara remarci finale. "
        "Nu folosi formatare markdown. Doar text simplu."
        "{sentinel}"
    ),
}

_PERFECT_OUTFIT_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "Based on this outfit photo, describe in detail what a PERFECT 10/10 version would look like. "
        "Keep the person's face, body type, and skin tone exactly as they are - only change the clothing, colors, and accessories. "
        "Write as a clear, vivid description a stylist would give to a shopper. "
        "Be specific about colors, cuts, fabrics, and brands if relevant. 2-4 sentences max. "
        "Do not use any markdown formatting. Plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Pe baza acestei poze cu tinuta, descrie in detaliu cum ar arata o versiune PERFECTA de 10/10. "
        "Pastreaza fata, tipul de corp si tonul pielii exact cum sunt - schimba doar hainele, culorile si accesoriile. "
        "Scrie ca o descriere clara si vie pe care un stilist ar da-o unui client. "
        "Fii specific despre culori, croieli, materiale si branduri daca e relevant. Maximum 2-4 propozitii. "
        "Nu folosi formatare markdown. Doar text simplu."
        "{sentinel}"
    ),
}

_CHANGE_COLORS_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "Look at this outfit and suggest 2-3 improved color combinations that would work better. "
        "For each suggestion, explain why it works for this person's skin tone and body type. "
        "Be specific - name actual colors (e.g. dusty rose, navy blue, camel). Keep the same style and occasion. "
        "Do not use any markdown formatting. Plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Uita-te la aceasta tinuta si sugereaza 2-3 combinatii de culori imbunatatite care ar functiona mai bine. "
        "Pentru fiecare sugestie, explica de ce functioneaza pentru tonul de piele si tipul de corp al acestei persoane. "
        "Fii specific - numeste culori reale (ex: roz pudrat, albastru navy, camel). Pastreaza acelasi stil si ocazie. "
        "Nu folosi formatare markdown. Doar text simplu."
        "{sentinel}"
    ),
}

_OCCASION_IDEAS_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. {body_context}\n"
        "The user is preparing for: {occasion}.\n"
        "Budget: {budget}\n"
        "Style vibe: {style_vibe}\n\n"
        "Suggest 3 distinct outfit ideas for this occasion. For each idea:\n"
        "- Give it a short name\n"
        "- Describe the specific pieces (top, bottom, shoes, accessories)\n"
        "- Explain why it works for this occasion\n\n"
        "Be practical, specific, and inspiring. "
        "Do not use any markdown formatting. Plain text only."
    ),
    "ro": (
        "Esti un stilist profesionist. {body_context}\n"
        "Utilizatorul se pregateste pentru: {occasion}.\n"
        "Buget: {budget}\n"
        "Stil: {style_vibe}\n\n"
        "Sugereaza 3 idei de tinute diferite pentru aceasta ocazie. Pentru fiecare idee:\n"
        "- Da-i un nume scurt\n"
        "- Descrie piesele specifice (bluza, pantaloni/fusta, pantofi, accesorii)\n"
        "- Explica de ce functioneaza pentru aceasta ocazie\n\n"
        "Fii practic, specific si inspirational. "
        "Nu folosi formatare markdown. Doar text simplu."
    ),
}

_OCCASION_PHOTO_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist. "
        "The user is preparing an outfit for: {occasion}.\n"
        "Look at this clothing item or outfit photo and tell them:\n"
        "1. Does it work for {occasion}? (yes/no/with modifications)\n"
        "2. Why or why not?\n"
        "3. If it needs modifications, what specifically?\n\n"
        "Be direct, helpful and encouraging. 3-5 sentences max. "
        "Do not use any markdown formatting. Plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist. "
        "Utilizatorul se pregateste pentru: {occasion}.\n"
        "Uita-te la aceasta piesa de imbracaminte sau tinuta si spune-i:\n"
        "1. Merge pentru {occasion}? (da/nu/cu modificari)\n"
        "2. De ce sau de ce nu?\n"
        "3. Daca are nevoie de modificari, care anume?\n\n"
        "Fii direct, util si incurajator. Maximum 3-5 propozitii. "
        "Nu folosi formatare markdown. Doar text simplu."
        "{sentinel}"
    ),
}

_BUY_INITIAL_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist and shopping advisor. "
        "Look at this clothing item and give a quick first impression:\n"
        "- Style assessment (is it versatile, trendy, classic?)\n"
        "- Apparent quality impression from the photo\n"
        "- What occasions it could work for\n\n"
        "Keep it to 3-4 sentences. Be honest and helpful. "
        "Do not use any markdown formatting. Plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist si consilier de cumparaturi. "
        "Uita-te la acest articol de imbracaminte si da o prima impresie rapida:\n"
        "- Evaluare stil (este versatil, la moda, clasic?)\n"
        "- Impresia aparenta de calitate din poza\n"
        "- Ce ocazii ar putea sa mearga\n\n"
        "Pastreaza-o la 3-4 propozitii. Fii sincer si util. "
        "Nu folosi formatare markdown. Doar text simplu."
        "{sentinel}"
    ),
}

_BUY_FULL_PROMPT: dict = {
    "en": (
        "You are a professional fashion stylist and shopping advisor. {body_context}\n"
        "The user wants to buy this clothing item.\n"
        "Price and brand: {price_brand}\n"
        "Material/fabric info: {materials}\n\n"
        "Provide a complete buy recommendation with:\n"
        "- Overall rating: X out of 5 stars (use format 'RATING: X')\n"
        "- Value for money assessment\n"
        "- 2 pros and 2 cons\n"
        "- Final verdict: BUY IT or SKIP IT and why\n\n"
        "Be honest, practical and direct. "
        "Do not use any markdown formatting. Plain text only."
        "{sentinel}"
    ),
    "ro": (
        "Esti un stilist profesionist si consilier de cumparaturi. {body_context}\n"
        "Utilizatorul vrea sa cumpere acest articol de imbracaminte.\n"
        "Pret si brand: {price_brand}\n"
        "Informatii material/tesatura: {materials}\n\n"
        "Ofera o recomandare completa de cumparare cu:\n"
        "- Evaluare generala: X din 5 stele (foloseste formatul 'RATING: X')\n"
        "- Evaluarea raportului calitate-pret\n"
        "- 2 avantaje si 2 dezavantaje\n"
        "- Verdict final: CUMPARA sau NU CUMPARA si de ce\n\n"
        "Fii sincer, practic si direct. "
        "Nu folosi formatare markdown. Doar text simplu."
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


_EXPECTED_PREFIXES = ("Style Score", "Scor stil", "Colors", "Culori", "Fit", "Croiala", "Occasion", "Ocazie", "Suggestion", "Sugestie")


def _parse_outfit_response(raw: str) -> str:
    clean = _strip_markdown(raw)
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    matched = sum(
        1 for prefix in _EXPECTED_PREFIXES
        if any(line.lower().startswith(prefix.lower()) for line in lines)
    )
    if matched >= 3:
        return clean
    logger.warning("Structured outfit response parsing failed (%d matches)", matched)
    return clean


def _parse_buy_rating(raw: str) -> str:
    clean = _strip_markdown(raw)
    stars_map = {1: "⭐☆☆☆☆", 2: "⭐⭐☆☆☆", 3: "⭐⭐⭐☆☆", 4: "⭐⭐⭐⭐☆", 5: "⭐⭐⭐⭐⭐"}
    import re as _re
    match = _re.search(r"RATING:\s*([1-5])", clean, _re.IGNORECASE)
    if match:
        rating = int(match.group(1))
        stars = stars_map.get(rating, "")
        clean = _re.sub(r"RATING:\s*[1-5]", f"Rating: {stars} ({rating}/5)", clean, flags=_re.IGNORECASE)
    return clean


# ── Public functions ──────────────────────────────────────────────────────────

async def analyze_outfit(
    image_path: str,
    occasion: Optional[str],
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    occasion_text = occasion if occasion else ("general use" if lang == "en" else "utilizare generala")
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _OUTFIT_PROMPT.get(lang, _OUTFIT_PROMPT["en"])
    prompt = prompt_template.format(
        body_context=body_context,
        occasion=occasion_text,
        sentinel=_SENTINEL_INSTRUCTION,
    )
    raw = await analyze_image(image_path, prompt)
    _check_fashion_sentinel(raw)
    return _truncate(_parse_outfit_response(raw))


async def generate_perfect_outfit(
    image_path: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _PERFECT_OUTFIT_PROMPT.get(lang, _PERFECT_OUTFIT_PROMPT["en"])
    prompt = prompt_template.format(body_context=body_context, sentinel=_SENTINEL_INSTRUCTION)
    raw = await analyze_image(image_path, prompt)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def generate_color_suggestions(
    image_path: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _CHANGE_COLORS_PROMPT.get(lang, _CHANGE_COLORS_PROMPT["en"])
    prompt = prompt_template.format(body_context=body_context, sentinel=_SENTINEL_INSTRUCTION)
    raw = await analyze_image(image_path, prompt)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def generate_occasion_outfit_ideas(
    occasion: str,
    budget: str,
    style_vibe: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _OCCASION_IDEAS_PROMPT.get(lang, _OCCASION_IDEAS_PROMPT["en"])
    prompt = prompt_template.format(
        body_context=body_context,
        occasion=occasion,
        budget=budget,
        style_vibe=style_vibe,
    )
    raw = await ask_text(prompt)
    return _truncate(_strip_markdown(raw))


async def analyze_item_for_occasion(
    image_path: str,
    occasion: str,
    lang: str = "en",
) -> str:
    prompt_template = _OCCASION_PHOTO_PROMPT.get(lang, _OCCASION_PHOTO_PROMPT["en"])
    prompt = prompt_template.format(occasion=occasion, sentinel=_SENTINEL_INSTRUCTION)
    raw = await analyze_image(image_path, prompt)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def analyze_buy_item_initial(
    image_path: str,
    lang: str = "en",
) -> str:
    prompt_template = _BUY_INITIAL_PROMPT.get(lang, _BUY_INITIAL_PROMPT["en"])
    prompt = prompt_template.format(sentinel=_SENTINEL_INSTRUCTION)
    raw = await analyze_image(image_path, prompt)
    _check_fashion_sentinel(raw)
    return _truncate(_strip_markdown(raw))


async def analyze_buy_item_full(
    image_path: str,
    price_brand: str,
    materials: str,
    lang: str = "en",
    name: Optional[str] = None,
    height_cm: Optional[int] = None,
    weight_kg: Optional[int] = None,
) -> str:
    body_context = _build_body_context(name, height_cm, weight_kg, lang)
    prompt_template = _BUY_FULL_PROMPT.get(lang, _BUY_FULL_PROMPT["en"])
    prompt = prompt_template.format(
        body_context=body_context,
        price_brand=price_brand,
        materials=materials,
        sentinel=_SENTINEL_INSTRUCTION,
    )
    raw = await analyze_image(image_path, prompt)
    _check_fashion_sentinel(raw)
    return _truncate(_parse_buy_rating(raw))


# Legacy functions kept for backward compatibility
async def generate_occasion_restyle(image_path: str, lang: str = "en") -> str:
    return await analyze_item_for_occasion(image_path, "any occasion", lang)


async def answer_question(user_text: str, lang: str = "en") -> str:
    prompts = {
        "en": f"You are a professional fashion stylist. Answer this fashion question briefly and confidently in 2-3 sentences. No markdown formatting, plain text only: {user_text}",
        "ro": f"Esti un stilist profesionist. Raspunde la aceasta intrebare de moda scurt si sigur in 2-3 propozitii, in romana. Fara formatare markdown, doar text simplu: {user_text}",
    }
    prompt = prompts.get(lang, prompts["en"])
    raw = await ask_text(prompt)
    return _truncate(_strip_markdown(raw))
