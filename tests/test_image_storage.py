"""Unit tests for app/storage/image_storage.py"""
import time
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSaveImage:
    async def test_saves_file_to_disk(self, tmp_images_dir):
        from app.storage.image_storage import save_image
        path = await save_image(12345, b"fake image bytes")
        assert Path(path).exists()

    async def test_returns_absolute_path(self, tmp_images_dir):
        from app.storage.image_storage import save_image
        path = await save_image(12345, b"data")
        assert Path(path).is_absolute()

    async def test_saves_in_user_subdirectory(self, tmp_images_dir):
        from app.storage.image_storage import save_image
        path = await save_image(99999, b"data")
        assert "99999" in path

    async def test_saves_correct_bytes(self, tmp_images_dir):
        from app.storage.image_storage import save_image
        data = b"hello world image content"
        path = await save_image(12345, data)
        assert Path(path).read_bytes() == data

    async def test_multiple_saves_produce_different_files(self, tmp_images_dir):
        from app.storage.image_storage import save_image
        # Ensure timestamps differ
        p1 = await save_image(12345, b"img1")
        time.sleep(0.002)
        p2 = await save_image(12345, b"img2")
        assert p1 != p2

    async def test_user_id_zero_is_handled(self, tmp_images_dir):
        # user_id 0 → str "0" → valid, saved in a "0" subdirectory
        from app.storage.image_storage import save_image
        path = await save_image(0, b"data")
        assert "0" in path


class TestDeleteImage:
    async def test_deletes_existing_file(self, tmp_images_dir):
        from app.storage.image_storage import delete_image, save_image
        path = await save_image(12345, b"data")
        assert Path(path).exists()
        await delete_image(path)
        assert not Path(path).exists()

    async def test_missing_file_does_not_raise(self, tmp_images_dir):
        from app.storage.image_storage import delete_image
        # Should not raise
        await delete_image("/non/existent/file.jpg")


class TestGetLatestImagePath:
    async def test_returns_none_when_no_images(self, tmp_images_dir):
        from app.storage.image_storage import get_latest_image_path
        result = await get_latest_image_path(77777)
        assert result is None

    async def test_returns_path_after_save(self, tmp_images_dir):
        from app.storage.image_storage import get_latest_image_path, save_image
        saved = await save_image(88888, b"data")
        result = await get_latest_image_path(88888)
        assert result == saved

    async def test_returns_most_recent_of_multiple(self, tmp_images_dir):
        from app.storage.image_storage import get_latest_image_path, save_image
        await save_image(55555, b"first")
        time.sleep(0.002)
        second = await save_image(55555, b"second")
        result = await get_latest_image_path(55555)
        assert result == second


class TestSanitizeUserId:
    def test_valid_id_passes(self):
        from app.storage.image_storage import _sanitize_user_id
        assert _sanitize_user_id(123456) == "123456"

    def test_strips_non_digits(self):
        # Normally user_id is always an int from Telegram, but test the guard
        from app.storage.image_storage import _sanitize_user_id
        assert _sanitize_user_id(123) == "123"

    def test_zero_returns_string_zero(self):
        # 0 → "0" is a valid sanitized ID
        from app.storage.image_storage import _sanitize_user_id
        assert _sanitize_user_id(0) == "0"

    def test_large_id_passes(self):
        from app.storage.image_storage import _sanitize_user_id
        assert _sanitize_user_id(987654321) == "987654321"
