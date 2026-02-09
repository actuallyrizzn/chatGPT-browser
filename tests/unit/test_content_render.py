# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser tests - See LICENSE (AGPL-3.0).
"""Unit tests for content-type dispatch: _render_content_part and render_part filter (#35, #39)."""

import pytest

import app as app_module
from markupsafe import Markup


class TestRenderContentPart:
    """Tests for _render_content_part (content-type dispatch)."""

    def test_none_returns_empty(self):
        assert app_module._render_content_part(None) == Markup('')

    def test_string_renders_as_markdown(self):
        out = app_module._render_content_part("Hello **world**")
        assert isinstance(out, Markup)
        assert "Hello" in out
        assert "world" in out

    def test_export_type_text_extracts_text(self):
        part = {"type": "text", "text": "Hello, how are you?"}
        out = app_module._render_content_part(part)
        assert "Hello" in out
        assert "how are you" in out

    def test_image_asset_pointer_placeholder(self):
        part = {
            "content_type": "image_asset_pointer",
            "asset_pointer": "sediment://...",
            "width": 400,
            "height": 300,
        }
        out = app_module._render_content_part(part)
        assert "[Image" in out
        assert "400×300" in out

    def test_image_asset_pointer_no_dimensions(self):
        part = {"content_type": "image_asset_pointer"}
        out = app_module._render_content_part(part)
        assert "[Image]" in out

    def test_audio_transcription_extracts_text(self):
        part = {"content_type": "audio_transcription", "text": "Voice message here"}
        out = app_module._render_content_part(part)
        assert "Voice message here" in out
        assert "🎤" in out or "Voice" in out

    def test_audio_asset_pointer_placeholder(self):
        part = {"content_type": "audio_asset_pointer"}
        out = app_module._render_content_part(part)
        assert "[Audio]" in out

    def test_video_placeholders(self):
        for ct in ("real_time_user_audio_video_asset_pointer", "video_container_asset_pointer"):
            out = app_module._render_content_part({"content_type": ct})
            assert "[Video]" in out

    def test_navlist_citation_placeholder(self):
        part = {"content_type": "navlist"}
        out = app_module._render_content_part(part)
        assert "[Citation]" in out

    def test_unknown_dict_nice_mode_placeholder(self):
        part = {"content_type": "unknown_type", "foo": "bar"}
        out = app_module._render_content_part(part, dev_mode=False)
        assert "[Content]" in out

    def test_unknown_dict_dev_mode_shows_json(self):
        part = {"content_type": "unknown_type", "foo": "bar"}
        out = app_module._render_content_part(part, dev_mode=True)
        assert "foo" in out
        assert "bar" in out
        assert "<pre" in out or "content-json" in out

    def test_turn0news_replaced_in_nice_mode(self):
        out = app_module._render_content_part("See turn0news1 and turn0news7", dev_mode=False)
        assert "[1]" in out
        assert "[7]" in out

    def test_turn0news_unchanged_in_dev_mode(self):
        out = app_module._render_content_part("See turn0news1", dev_mode=True)
        assert "turn0news1" in out
