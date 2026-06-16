# ─── test_09_settings.py — Settings Page E2E Tests ────────────────────────────
"""
Tests for the SocialShield Settings page.
Covers profile card, toggle switches, AI models, about section, and danger zone.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _go_settings(driver):
    """Navigate to settings page with auth, wait for content to load."""
    go_to(driver, "/settings")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "toggle-switch"))
        )
    except Exception:
        time.sleep(3)


@pytest.mark.settings
class TestSettingsPage:
    """TC-103 to TC-114: Settings page functionality tests."""

    def test_tc103_page_header_settings(self, auth_driver):
        """TC-103: Verify page header shows 'Settings'."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Settings" in body, \
            f"'Settings' header not found. Text: {body[:300]}"

    def test_tc104_profile_card_displays_user_info(self, auth_driver):
        """TC-104: Verify profile card displays user info."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "E2E Tester" in body or "Shield User" in body or "e2e" in body.lower(), \
            f"User info not displayed. Text: {body[:300]}"

    def test_tc105_edit_button_on_profile(self, auth_driver):
        """TC-105: Verify 'Edit' button is present on profile card."""
        _go_settings(auth_driver)
        buttons = auth_driver.find_elements(By.TAG_NAME, "button")
        edit_btn = None
        for btn in buttons:
            if "Edit" in btn.text:
                edit_btn = btn
                break
        assert edit_btn is not None, "'Edit' button not found on profile card"

    def test_tc106_pro_plan_badge_visible(self, auth_driver):
        """TC-106: Verify 'Pro Plan' badge is visible."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Pro Plan" in body, "'Pro Plan' badge not found"

    def test_tc107_preferences_four_toggles(self, auth_driver):
        """TC-107: Verify Preferences section has 4 toggle switches."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Preferences" in body, "Preferences section not found"
        toggle_switches = auth_driver.find_elements(By.CLASS_NAME, "toggle-switch")
        # At least 4 in Preferences + 2 in Advanced = 6 total
        assert len(toggle_switches) >= 4, \
            f"Expected at least 4 toggle switches, found {len(toggle_switches)}"

    def test_tc108_dark_mode_on_by_default(self, auth_driver):
        """TC-108: Verify Dark Mode toggle is ON by default."""
        _go_settings(auth_driver)
        dark_mode = auth_driver.find_elements(By.ID, "dark-mode")
        assert len(dark_mode) > 0, "Dark Mode toggle not found"
        assert dark_mode[0].is_selected(), "Dark Mode should be ON by default"

    def test_tc109_toggle_switches_clickable(self, auth_driver):
        """TC-109: Verify toggle switches are clickable and change state."""
        _go_settings(auth_driver)
        notifications = auth_driver.find_elements(By.ID, "notifications")
        if len(notifications) > 0:
            initial_state = notifications[0].is_selected()
            # Click the label (parent toggle-switch) since the checkbox may be hidden
            label = notifications[0].find_element(By.XPATH, "./..")
            label.click()
            time.sleep(0.3)
            new_state = notifications[0].is_selected()
            assert new_state != initial_state, \
                "Toggle state should change after click"

    def test_tc110_advanced_section_backend_url(self, auth_driver):
        """TC-110: Verify Advanced section shows Backend URL."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Backend URL" in body or "Advanced" in body, \
            "Advanced section with Backend URL not found"
        assert "socialshield" in body.lower() or "Connected" in body, \
            "Backend URL or connection status not displayed"

    def test_tc111_ai_models_section_four_models(self, auth_driver):
        """TC-111: Verify AI Models section lists 4 models."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "AI Models" in body, "AI Models section not found"
        models = ["EfficientNet", "CNN Temporal", "Mel-CNN", "DistilBERT"]
        found = sum(1 for m in models if m in body)
        assert found >= 4, f"Expected 4 AI models, found {found}"

    def test_tc112_about_section_version(self, auth_driver):
        """TC-112: Verify About section shows Version 1.0.0."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Version" in body, "Version label not found"
        assert "1.0.0" in body, "Version 1.0.0 not found"

    def test_tc113_sign_out_button_danger_zone(self, auth_driver):
        """TC-113: Verify 'Sign Out' button is in Danger Zone."""
        _go_settings(auth_driver)
        logout_btn = auth_driver.find_elements(By.ID, "logout-btn")
        assert len(logout_btn) > 0, "Sign Out button not found"
        assert "Sign Out" in logout_btn[0].text or "🚪" in logout_btn[0].text, \
            f"Button text incorrect: {logout_btn[0].text}"

    def test_tc114_clear_history_button_danger_zone(self, auth_driver):
        """TC-114: Verify 'Clear History' button is in Danger Zone."""
        _go_settings(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Danger Zone" in body, "Danger Zone section not found"
        assert "Clear History" in body, "Clear History button not found"
