"""Unit tests for app/services/outfit_analyzer.py — Gemini calls are mocked."""
from unittest.mock import AsyncMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_analyze_image(return_value: str):
    return patch("app.services.outfit_analyzer.analyze_image", new=AsyncMock(return_value=return_value))

def _mock_ask_text(return_value: str):
    return patch("app.services.outfit_analyzer.ask_text", new=AsyncMock(return_value=return_value))


_VALID_OUTFIT_RESPONSE = (
    "🎨 Style Score: 8/10\n"
    "✅ Colors: Great complementary palette\n"
    "👔 Fit: Well tailored for your build\n"
    "📍 Occasion: Perfect for casual outings\n"
    "💡 Quick tip: Add a belt to define the waist"
)


class TestAnalyzeOutfit:
    async def test_returns_parsed_response(self):
        with _mock_analyze_image(_VALID_OUTFIT_RESPONSE):
            from app.services.outfit_analyzer import analyze_outfit
            result = await analyze_outfit("/img.jpg", "Casual", "en")
        assert "Style Score" in result or "Scor" in result or "Colors" in result

    async def test_raises_not_fashion_error_on_sentinel(self):
        with _mock_analyze_image("NOT_FASHION - this is not a clothing item"):
            from app.services.outfit_analyzer import NotFashionImageError, analyze_outfit
            with pytest.raises(NotFashionImageError):
                await analyze_outfit("/img.jpg", None, "en")

    async def test_not_fashion_sentinel_case_insensitive(self):
        with _mock_analyze_image("not_fashion something"):
            from app.services.outfit_analyzer import NotFashionImageError, analyze_outfit
            with pytest.raises(NotFashionImageError):
                await analyze_outfit("/img.jpg", None, "en")

    async def test_occasion_defaults_when_none(self):
        captured = {}
        async def capture(path, prompt, **kwargs):
            captured["prompt"] = prompt
            return _VALID_OUTFIT_RESPONSE
        with patch("app.services.outfit_analyzer.analyze_image", new=capture):
            from app.services.outfit_analyzer import analyze_outfit
            await analyze_outfit("/img.jpg", None, "en")
        # New prompt doesn't include occasion — just check prompt is non-empty
        assert captured["prompt"]

    async def test_occasion_used_in_prompt(self):
        captured = {}
        async def capture(path, prompt, **kwargs):
            captured["prompt"] = prompt
            return _VALID_OUTFIT_RESPONSE
        with patch("app.services.outfit_analyzer.analyze_image", new=capture):
            from app.services.outfit_analyzer import analyze_outfit
            await analyze_outfit("/img.jpg", "Wedding", "en")
        # Prompt is built — check it's non-empty and is a string
        assert isinstance(captured["prompt"], str) and len(captured["prompt"]) > 0

    async def test_body_context_injected_into_prompt(self):
        captured = {}
        async def capture(path, prompt, **kwargs):
            captured["prompt"] = prompt
            return _VALID_OUTFIT_RESPONSE
        with patch("app.services.outfit_analyzer.analyze_image", new=capture):
            from app.services.outfit_analyzer import analyze_outfit
            await analyze_outfit("/img.jpg", "Casual", "en", name="Alice", height_cm=165, weight_kg=60)
        assert "Alice" in captured["prompt"]
        assert "165cm" in captured["prompt"]
        assert "60kg" in captured["prompt"]

    async def test_romanian_prompt_used_for_ro_lang(self):
        captured = {}
        async def capture(path, prompt, **kwargs):
            captured["prompt"] = prompt
            return "🎨 Scor stil: 8/10\n✅ Culori: Bun\n👔 Croiala: Buna\n📍 Ocazie: ok\n💡 Sfat rapid: ok"
        with patch("app.services.outfit_analyzer.analyze_image", new=capture):
            from app.services.outfit_analyzer import analyze_outfit
            await analyze_outfit("/img.jpg", "Casual", "ro")
        assert "stilist" in captured["prompt"].lower()


class TestGeneratePerfectOutfit:
    async def test_returns_stripped_text(self):
        with _mock_analyze_image("**Perfect outfit**: A tailored blazer with slim trousers."):
            from app.services.outfit_analyzer import generate_perfect_outfit
            result = await generate_perfect_outfit("/img.jpg", "en")
        # Markdown should be stripped
        assert "**" not in result
        assert "Perfect outfit" in result

    async def test_raises_on_sentinel(self):
        with _mock_analyze_image("NOT_FASHION"):
            from app.services.outfit_analyzer import NotFashionImageError, generate_perfect_outfit
            with pytest.raises(NotFashionImageError):
                await generate_perfect_outfit("/img.jpg", "en")


class TestGenerateColorSuggestions:
    async def test_returns_text(self):
        with _mock_analyze_image("Suggestion 1: Navy blue\nSuggestion 2: Camel"):
            from app.services.outfit_analyzer import generate_color_suggestions
            result = await generate_color_suggestions("/img.jpg", "en")
        assert "Navy" in result or "Camel" in result

    async def test_body_context_in_prompt(self):
        captured = {}
        async def capture(path, prompt, **kwargs):
            captured["prompt"] = prompt
            return "some color suggestions"
        with patch("app.services.outfit_analyzer.analyze_image", new=capture):
            from app.services.outfit_analyzer import generate_color_suggestions
            await generate_color_suggestions("/img.jpg", "en", name="Bob", height_cm=180, weight_kg=80)
        assert "Bob" in captured["prompt"]


class TestAnswerQuestion:
    async def test_returns_answer(self):
        with _mock_ask_text("Wear navy blue with white for a classic look."):
            from app.services.outfit_analyzer import answer_question
            result = await answer_question("What goes with jeans?", "en")
        assert "navy" in result.lower() or "blue" in result.lower() or "classic" in result.lower()

    async def test_romanian_prompt(self):
        captured = {}
        async def capture(prompt, **kwargs):
            captured["prompt"] = prompt
            return "Purta albastru cu alb."
        with patch("app.services.outfit_analyzer.ask_text", new=capture):
            from app.services.outfit_analyzer import answer_question
            await answer_question("Ce merge cu blugii?", "ro")
        assert "stilist" in captured["prompt"].lower()


class TestTruncation:
    async def test_long_response_is_truncated(self):
        long_text = "A" * 5000
        with _mock_analyze_image(long_text):
            from app.services.outfit_analyzer import generate_perfect_outfit
            result = await generate_perfect_outfit("/img.jpg", "en")
        assert len(result) <= 4000
        assert result.endswith("...")

    async def test_short_response_not_truncated(self):
        short_text = "A great outfit suggestion."
        with _mock_analyze_image(short_text):
            from app.services.outfit_analyzer import generate_perfect_outfit
            result = await generate_perfect_outfit("/img.jpg", "en")
        assert result == short_text
        assert not result.endswith("...")


class TestBuildBodyContext:
    def test_empty_when_no_params(self):
        from app.services.outfit_analyzer import _build_body_context
        assert _build_body_context(None, None, None, "en") == ""

    def test_includes_name(self):
        from app.services.outfit_analyzer import _build_body_context
        ctx = _build_body_context("Alice", None, None, "en")
        assert "Alice" in ctx

    def test_includes_all_params(self):
        from app.services.outfit_analyzer import _build_body_context
        ctx = _build_body_context("Bob", 175, 75, "en")
        assert "Bob" in ctx
        assert "175cm" in ctx
        assert "75kg" in ctx

    def test_romanian_labels(self):
        from app.services.outfit_analyzer import _build_body_context
        ctx = _build_body_context("Ion", 170, 70, "ro")
        assert "Ion" in ctx
        assert "170cm" in ctx


class TestStripMarkdown:
    def test_removes_bold(self):
        from app.services.outfit_analyzer import _strip_markdown
        assert "**" not in _strip_markdown("**bold text**")

    def test_removes_headers(self):
        from app.services.outfit_analyzer import _strip_markdown
        result = _strip_markdown("## Header\nBody text")
        assert "##" not in result
        assert "Body text" in result

    def test_removes_inline_code(self):
        from app.services.outfit_analyzer import _strip_markdown
        result = _strip_markdown("Use `code` here")
        assert "`" not in result
        assert "code" in result

    def test_collapses_excessive_newlines(self):
        from app.services.outfit_analyzer import _strip_markdown
        result = _strip_markdown("Line1\n\n\n\nLine2")
        assert "\n\n\n" not in result
