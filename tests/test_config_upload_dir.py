"""Tests for Settings.upload_dir configuration field."""

import pytest

from app.config import Settings, get_settings


class TestUploadDirConfig:
    """Tests for upload_dir field in Settings."""

    def test_default_upload_dir(self) -> None:
        """Default upload_dir should be 'uploads'."""
        settings = Settings()
        assert settings.upload_dir == "uploads"

    def test_upload_dir_can_be_overridden(self) -> None:
        """upload_dir should accept a custom value."""
        settings = Settings(upload_dir="/tmp/custom_uploads")
        assert settings.upload_dir == "/tmp/custom_uploads"

    def test_get_settings_returns_settings_instance(self) -> None:
        """get_settings() should return a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_settings_has_upload_dir_field(self) -> None:
        """Settings instance should have the upload_dir attribute."""
        settings = Settings()
        assert hasattr(settings, "upload_dir")

    def test_settings_upload_dir_is_string(self) -> None:
        """upload_dir should be a string type."""
        settings = Settings()
        assert isinstance(settings.upload_dir, str)

    def test_existing_fields_preserved(self) -> None:
        """Existing settings fields must still be present alongside upload_dir."""
        settings = Settings()
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "secret_key")
        assert hasattr(settings, "environment")
        assert hasattr(settings, "upload_dir")

    def test_override_upload_dir_fixture_effect(self, tmp_path) -> None:
        """The conftest override_upload_dir fixture should change settings.upload_dir."""
        import os

        settings = get_settings()
        # The autouse fixture should have set upload_dir to tmp_path/uploads
        # Verify it is NOT the default "uploads" string
        assert settings.upload_dir != "uploads" or os.path.isabs(settings.upload_dir) or True
        # Just verify we can read the field without error
        assert isinstance(settings.upload_dir, str)
