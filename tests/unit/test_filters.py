# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser tests - See LICENSE (AGPL-3.0).
"""Unit tests for Jinja template filters and app helpers used in templates."""

import json
from datetime import datetime

import pytest

import app as app_module


class TestFromJsonFilter:
    """Tests for the fromjson template filter."""

    def test_valid_json_array(self):
        assert app_module.fromjson("[1,2,3]") == [1, 2, 3]

    def test_valid_json_object(self):
        assert app_module.fromjson('{"a": 1}') == {"a": 1}

    def test_invalid_json_returns_empty_list(self):
        assert app_module.fromjson("not json") == []
        assert app_module.fromjson("") == []
        assert app_module.fromjson("{") == []


class TestToJsonFilter:
    """Tests for the tojson template filter."""

    def test_list(self):
        assert app_module.tojson([1, 2, 3]) == "[1, 2, 3]"

    def test_dict(self):
        assert app_module.tojson({"a": 1}) == '{"a": 1}'

    def test_with_indent(self):
        out = app_module.tojson({"a": 1}, indent=2)
        assert "  " in out
        assert "\n" in out

    def test_non_serializable_returns_str(self):
        # e.g. object with no default repr
        class C:
            pass
        result = app_module.tojson(C())
        assert isinstance(result, str)


class TestDatetimeFilter:
    """Tests for the datetime template filter."""

    def test_float_timestamp(self):
        # 2022-01-01 00:00:00 UTC (approx, depends on local TZ)
        ts = 1640995200.0
        result = app_module.format_datetime(ts)
        assert "2022" in result or "2021" in result
        assert "-" in result and ":" in result

    def test_string_timestamp(self):
        result = app_module.format_datetime("1640995200.0")
        assert "2022" in result or "2021" in result

    def test_invalid_or_none_returns_placeholder(self):
        assert app_module.format_datetime("invalid") == "—"
        assert app_module.format_datetime(None) == "—"


class TestRelativetimeFilter:
    """Tests for the relativetime template filter (#52)."""

    def test_just_now(self):
        from datetime import timezone
        from datetime import datetime as dt
        ts = dt.now(tz=timezone.utc).timestamp()
        result = app_module.relativetime(ts)
        assert result == "just now"

    def test_minutes_ago(self):
        from datetime import timezone, timedelta
        from datetime import datetime as dt
        ts = (dt.now(tz=timezone.utc) - timedelta(minutes=5)).timestamp()
        result = app_module.relativetime(ts)
        assert "min" in result and "ago" in result

    def test_none_returns_placeholder(self):
        assert app_module.relativetime(None) == "—"

    def test_invalid_returns_placeholder(self):
        assert app_module.relativetime("invalid") == "—"


class TestJsonLoadsFilter:
    """Tests for the json_loads template filter."""

    def test_valid_json(self):
        assert app_module.json_loads_filter("[1,2]") == [1, 2]
        assert app_module.json_loads_filter('{"x":1}') == {"x": 1}

    def test_none_returns_empty_list(self):
        assert app_module.json_loads_filter(None) == []

    def test_invalid_returns_empty_list(self):
        assert app_module.json_loads_filter("not json") == []
        assert app_module.json_loads_filter("") == []


class TestMarkdownFilter:
    """Tests for the markdown template filter."""

    def test_basic_markdown(self):
        result = app_module.markdown_filter("# Hello")
        assert "Hello" in result
        assert "<h1>" in result or "h1" in result

    def test_none_returns_empty_string(self):
        assert app_module.markdown_filter(None) == ""

    def test_plain_text(self):
        result = app_module.markdown_filter("plain text")
        assert "plain text" in result

    def test_xss_script_stripped(self):
        """Markdown output is sanitized; script tags must not appear (XSS prevention)."""
        result = app_module.markdown_filter("<script>alert(1)</script>")
        assert "<script" not in result and "script>" not in result
        result2 = app_module.markdown_filter("Hello\n\n<script>evil()</script>")
        assert "<script" not in result2 and "</script>" not in result2
