# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser tests - See LICENSE (AGPL-3.0).
"""E2E tests using Playwright. Require: pip install -r requirements-testing.txt && playwright install."""

import pytest

pytest.importorskip("playwright")
pytestmark = pytest.mark.e2e


@pytest.fixture
def base_url(live_server_url):
    return live_server_url


class TestE2EHomePage:
    """E2E tests for the home page."""

    def test_home_loads_and_shows_nav(self, page, base_url):
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")
        # Nav bar
        assert page.locator("text=ChatGPT Browser").first.is_visible() or page.locator("nav").first.is_visible()

    def test_home_has_settings_link(self, page, base_url):
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")
        settings = page.get_by_role("link", name="Settings").or_(page.locator("a[href*='settings']")).first
        assert settings.is_visible()


class TestE2EConversation:
    """E2E tests for conversation view (seeded E2E data)."""

    def test_conversation_nice_view_loads(self, page, base_url):
        page.goto(f"{base_url}/conversation/e2e-conv-1/nice")
        page.wait_for_load_state("domcontentloaded")
        # Should show conversation content
        assert page.locator("body").first.is_visible()
        # Either title or message content
        assert page.locator("text=E2E").or_(page.locator("text=Hello")).first.is_visible()


class TestE2ESettings:
    """E2E tests for settings page."""

    def test_settings_page_loads(self, page, base_url):
        page.goto(f"{base_url}/settings")
        page.wait_for_load_state("domcontentloaded")
        assert page.locator("body").first.is_visible()
        # Settings form or heading
        assert (
            page.locator("text=Settings").or_(page.locator("input[name='user_name']")).first.is_visible()
        )
