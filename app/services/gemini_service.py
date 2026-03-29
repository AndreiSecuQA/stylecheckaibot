import asyncio
import functools
from typing import Optional

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from PIL import Image

from app.utils.config import settings
from app.utils.logger import logger

# Configure Gemini on module load with system key
genai.configure(api_key=settings.gemini_api_key)

# Fallback model order — try each until one works (deduped so primary isn't retried)
_MODEL_FALLBACK_ORDER = list(dict.fromkeys([
    settings.gemini_model,           # primary (from config) — gemini-2.5-flash
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]))

# Per-model singleton cache (system key only)
_models: dict = {}

# Lock to serialize calls that use a non-system API key
_user_key_lock = asyncio.Lock()


class QuotaExceededError(Exception):
    """Raised when all models have exhausted their quota."""
    pass


class InvalidApiKeyError(Exception):
    """Raised when a user-provided API key is invalid."""
    pass


def _get_model(model_name: str) -> genai.GenerativeModel:
    """Return (or create) a cached GenerativeModel for the given model name."""
    if model_name not in _models:
        logger.info("Initialising Gemini model: %s", model_name)
        _models[model_name] = genai.GenerativeModel(model_name)
    return _models[model_name]


def _call_vision_sync(image_path: str, prompt: str, api_key: Optional[str] = None) -> str:
    """Try each model in fallback order for a vision call."""
    if api_key:
        genai.configure(api_key=api_key)

    img = Image.open(image_path)
    last_err: Optional[Exception] = None
    for model_name in _MODEL_FALLBACK_ORDER:
        try:
            model = genai.GenerativeModel(model_name) if api_key else _get_model(model_name)
            response = model.generate_content([prompt, img])
            logger.info("Vision call succeeded with model: %s", model_name)
            return response.text
        except ResourceExhausted as e:
            logger.warning("Model %s quota exhausted, trying next fallback...", model_name)
            last_err = e
        except Exception as e:
            logger.warning("Model %s failed (%s), trying next fallback...", model_name, e)
            last_err = e
    raise QuotaExceededError(
        "All Gemini models have exhausted their quota. Please try again later."
    ) from last_err


def _call_text_sync(prompt: str, api_key: Optional[str] = None) -> str:
    """Try each model in fallback order for a text call."""
    if api_key:
        genai.configure(api_key=api_key)

    last_err: Optional[Exception] = None
    for model_name in _MODEL_FALLBACK_ORDER:
        try:
            model = genai.GenerativeModel(model_name) if api_key else _get_model(model_name)
            response = model.generate_content(prompt)
            logger.info("Text call succeeded with model: %s", model_name)
            return response.text
        except ResourceExhausted as e:
            logger.warning("Model %s quota exhausted, trying next fallback...", model_name)
            last_err = e
        except Exception as e:
            logger.warning("Model %s failed (%s), trying next fallback...", model_name, e)
            last_err = e
    raise QuotaExceededError(
        "All Gemini models have exhausted their quota. Please try again later."
    ) from last_err


def _validate_key_sync(api_key: str) -> bool:
    """Test that a user-provided API key is valid by making a minimal text call."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        model.generate_content("Say OK")
        return True
    except Exception as e:
        logger.warning("API key validation failed: %s", e)
        return False
    finally:
        # Restore system key
        genai.configure(api_key=settings.gemini_api_key)


async def validate_user_api_key(api_key: str) -> bool:
    """Validate a user-provided Gemini API key. Non-blocking."""
    async with _user_key_lock:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _validate_key_sync, api_key)


async def analyze_image(image_path: str, prompt: str, api_key: Optional[str] = None) -> str:
    """Send an image + prompt to Gemini Vision. Non-blocking."""
    loop = asyncio.get_running_loop()
    logger.info("Gemini vision request: image=%s", image_path)
    try:
        if api_key:
            async with _user_key_lock:
                result = await loop.run_in_executor(
                    None, functools.partial(_call_vision_sync, image_path, prompt, api_key)
                )
                # Restore system key after user-key call
                genai.configure(api_key=settings.gemini_api_key)
        else:
            result = await loop.run_in_executor(
                None, functools.partial(_call_vision_sync, image_path, prompt)
            )
        logger.info("Gemini vision response received (%d chars)", len(result))
        return result
    except QuotaExceededError:
        raise
    except Exception:
        logger.exception("Gemini vision API call failed")
        raise


async def ask_text(prompt: str, api_key: Optional[str] = None) -> str:
    """Send a text-only prompt to Gemini. Non-blocking."""
    loop = asyncio.get_running_loop()
    logger.info("Gemini text request (%d chars)", len(prompt))
    try:
        if api_key:
            async with _user_key_lock:
                result = await loop.run_in_executor(
                    None, functools.partial(_call_text_sync, prompt, api_key)
                )
                genai.configure(api_key=settings.gemini_api_key)
        else:
            result = await loop.run_in_executor(
                None, functools.partial(_call_text_sync, prompt)
            )
        logger.info("Gemini text response received (%d chars)", len(result))
        return result
    except QuotaExceededError:
        raise
    except Exception:
        logger.exception("Gemini text API call failed")
        raise
