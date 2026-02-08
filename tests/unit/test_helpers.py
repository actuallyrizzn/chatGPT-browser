"""Unit tests for app helper functions: get_setting, set_setting, _parse_timestamp."""

import pytest

import app as app_module


class TestParseTimestamp:
    """Tests for _parse_timestamp."""

    def test_none_returns_none(self):
        assert app_module._parse_timestamp(None) is None

    def test_float_passthrough(self):
        assert app_module._parse_timestamp(1640995200.0) == 1640995200.0

    def test_string_numeric(self):
        assert app_module._parse_timestamp("1640995200.0") == 1640995200.0
        assert app_module._parse_timestamp("1640995200") == 1640995200.0

    def test_invalid_returns_none(self):
        assert app_module._parse_timestamp("not a number") is None

    def test_non_string_non_numeric_passthrough(self):
        # Code returns ts unchanged when not str and float(ts) not applied (e.g. list)
        assert app_module._parse_timestamp([]) == []


class TestGetSettingSetSetting:
    """Tests for get_setting and set_setting (require test_db so DB exists)."""

    def test_get_setting_default_when_missing(self, test_db):
        # Key that doesn't exist
        assert app_module.get_setting("nonexistent_key_xyz", "default") == "default"
        assert app_module.get_setting("nonexistent_key_xyz") is None

    def test_set_and_get_setting(self, test_db):
        app_module.set_setting("test_key_xyz", "test_value")
        assert app_module.get_setting("test_key_xyz") == "test_value"

    def test_set_setting_overwrites(self, test_db):
        app_module.set_setting("overwrite_key", "first")
        app_module.set_setting("overwrite_key", "second")
        assert app_module.get_setting("overwrite_key") == "second"

    def test_default_settings_exist_after_init(self, test_db):
        assert app_module.get_setting("user_name") == "User"
        assert app_module.get_setting("assistant_name") == "Assistant"
        assert app_module.get_setting("dev_mode") == "false"
        assert app_module.get_setting("dark_mode") == "false"
        assert app_module.get_setting("verbose_mode") == "false"
