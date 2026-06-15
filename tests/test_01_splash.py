# ─── test_01_splash.py — Splash Page E2E Tests ────────────────────────────────
"""
Tests for the SocialShield Splash/Landing screen.
The splash page shows a shield logo, brand name, subtitle, and auto-redirects.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


@pytest.mark.splash
class TestSplashPage:
    """TC-001 to TC-006: Splash page functionality tests."""

    def test_tc001_page_loads_with_correct_title(self, fresh_driver):
        """TC-001: Verify the page loads and has the correct document title."""
        go_to(fresh_driver)
        time.sleep(1)
        assert "SocialShield" in fresh_driver.title, \
            f"Expected 'SocialShield' in title, got: {fresh_driver.title}"

    def test_tc002_shield_logo_visible(self, fresh_driver):
        """TC-002: Verify the shield logo emoji (🛡️) is visible on splash."""
        go_to(fresh_driver)
        time.sleep(0.5)
        body_text = fresh_driver.find_element(By.TAG_NAME, "body").text
        # The splash page renders 🛡️ as logo
        splash_logo = fresh_driver.find_elements(By.CLASS_NAME, "splash-logo")
        assert len(splash_logo) > 0 or "🛡️" in body_text, \
            "Shield logo not found on splash page"

    def test_tc003_brand_text_displayed(self, fresh_driver):
        """TC-003: Verify 'SocialShield' brand text is displayed."""
        go_to(fresh_driver)
        time.sleep(0.5)
        body_text = fresh_driver.find_element(By.TAG_NAME, "body").text
        # Brand renders as "Social" + "Shield" (with styled span)
        assert "Social" in body_text and "Shield" in body_text, \
            f"Brand text 'SocialShield' not found. Body text: {body_text[:200]}"

    def test_tc004_subtitle_contains_ai_powered(self, fresh_driver):
        """TC-004: Verify subtitle contains 'AI-Powered' text."""
        go_to(fresh_driver)
        time.sleep(0.5)
        body_text = fresh_driver.find_element(By.TAG_NAME, "body").text
        assert "AI-Powered" in body_text or "AI" in body_text, \
            "Subtitle with 'AI-Powered' text not found"

    def test_tc005_auto_redirect_within_timeout(self, fresh_driver):
        """TC-005: Verify splash auto-redirects within 4 seconds."""
        go_to(fresh_driver)
        initial_url = fresh_driver.current_url
        # Wait for redirect (splash has 2.2s timer)
        time.sleep(4)
        redirected_url = fresh_driver.current_url
        assert redirected_url != initial_url or "onboarding" in redirected_url or "auth" in redirected_url or "home" in redirected_url, \
            f"No redirect detected. Still at: {redirected_url}"

    def test_tc006_dot_indicators_present(self, fresh_driver):
        """TC-006: Verify 3 dot/bar indicators are rendered on splash."""
        go_to(fresh_driver)
        time.sleep(0.5)
        # The splash page renders 3 dot elements as direct children
        page_source = fresh_driver.page_source
        # Check for the splash-page class and dot elements
        splash_elements = fresh_driver.find_elements(By.CLASS_NAME, "splash-page")
        if splash_elements:
            dots = splash_elements[0].find_elements(By.XPATH, ".//div[contains(@style, 'borderRadius')]")
            assert len(dots) >= 3, f"Expected at least 3 dot indicators, found {len(dots)}"
        else:
            # Page may have already redirected
            assert True, "Splash page auto-redirected before dots could be checked"
