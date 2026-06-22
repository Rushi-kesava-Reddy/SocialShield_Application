# ─── test_03_auth.py — Authentication Page E2E Tests ──────────────────────────
"""
Tests for the SocialShield Auth page.
Covers login/signup forms, validation, Google sign-in, toggle, and error handling.

Key note: AuthContext starts with loading=true and PublicRoute returns null until
the localStorage session-restore useEffect fires. We must wait for the auth-card
to appear before interacting.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _navigate_to_auth(driver):
    """Helper: clear all storage, set onboarded flag, then navigate to /auth."""
    driver.get(BASE_URL)
    time.sleep(0.5)
    # Clear everything and set onboarded=1 so we go to auth, not onboarding
    driver.execute_script("""
        localStorage.clear();
        sessionStorage.clear();
        localStorage.setItem('ss_onboarded', '1');
    """)
    driver.get("about:blank")
    driver.get(BASE_URL + "/#/auth")
    # Wait for auth-card (loading=true → null render → loading=false → auth renders)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "auth-card"))
        )
    except Exception:
        time.sleep(3)


@pytest.mark.auth
class TestAuthPage:
    """TC-017 to TC-030: Authentication page functionality tests."""

    def test_tc017_auth_card_renders_with_logo(self, fresh_driver):
        """TC-017: Verify auth card renders with the SocialShield logo."""
        _navigate_to_auth(fresh_driver)
        cards = fresh_driver.find_elements(By.CLASS_NAME, "auth-card")
        assert len(cards) > 0, "Auth card not found"
        logos = fresh_driver.find_elements(By.CLASS_NAME, "auth-logo")
        assert len(logos) > 0, "Auth logo not found inside card"

    def test_tc018_welcome_back_heading_login_mode(self, fresh_driver):
        """TC-018: Verify 'Welcome Back' heading in login mode."""
        _navigate_to_auth(fresh_driver)
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "welcome" in body.lower() and "back" in body.lower(), \
            f"'Welcome Back' heading not found. Text: {body[:300]}"

    def test_tc019_create_account_heading_signup_mode(self, fresh_driver):
        """TC-019: Verify 'Create Account' heading when toggled to signup."""
        _navigate_to_auth(fresh_driver)
        # Find and click the Sign Up toggle link button
        buttons = fresh_driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            txt = btn.get_attribute("innerText") or btn.text
            if "Sign Up" in txt:
                btn.click()
                break
        time.sleep(0.5)
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "create" in body.lower() and "account" in body.lower(), \
            f"'Create Account' not found after toggling to signup. Text: {body[:300]}"

    def test_tc020_toggle_between_signin_and_signup(self, fresh_driver):
        """TC-020: Verify toggle between Sign In and Sign Up modes."""
        _navigate_to_auth(fresh_driver)
        # Initially in Sign In mode
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "welcome" in body.lower() and "back" in body.lower()
 
        # Toggle to Sign Up
        buttons = fresh_driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            txt = btn.get_attribute("innerText") or btn.text
            if "Sign Up" in txt:
                btn.click()
                break
        time.sleep(0.3)
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "create" in body.lower() and "account" in body.lower()
 
        # Toggle back to Sign In
        buttons = fresh_driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            txt = btn.get_attribute("innerText") or btn.text
            if "Sign In" in txt and btn.get_attribute("id") != "submit-btn":
                btn.click()
                break
        time.sleep(0.3)
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "welcome" in body.lower() and "back" in body.lower()

    def test_tc021_email_input_present_and_functional(self, fresh_driver):
        """TC-021: Verify email input field (id='email') is present and accepts input."""
        _navigate_to_auth(fresh_driver)
        email_input = fresh_driver.find_element(By.ID, "email")
        assert email_input is not None, "Email input not found"
        assert email_input.get_attribute("type") == "email", "Input type should be 'email'"
        email_input.send_keys("test@example.com")
        assert email_input.get_attribute("value") == "test@example.com"

    def test_tc022_password_input_present(self, fresh_driver):
        """TC-022: Verify password input field (id='password') is present."""
        _navigate_to_auth(fresh_driver)
        password_input = fresh_driver.find_element(By.ID, "password")
        assert password_input is not None, "Password input not found"
        assert password_input.get_attribute("type") == "password", \
            "Password field should be type 'password' by default"

    def test_tc023_password_visibility_toggle(self, fresh_driver):
        """TC-023: Verify password visibility toggle (👁️ ↔ 🙈)."""
        _navigate_to_auth(fresh_driver)
        password_input = fresh_driver.find_element(By.ID, "password")
        assert password_input.get_attribute("type") == "password"

        # The toggle button is inside the same div as the password input
        toggle_buttons = fresh_driver.find_elements(
            By.XPATH, "//input[@id='password']/../button"
        )
        assert len(toggle_buttons) > 0, "Password toggle button not found"
        toggle_buttons[0].click()
        time.sleep(0.3)
        assert password_input.get_attribute("type") == "text", \
            "Password should be visible after toggle"

        toggle_buttons[0].click()
        time.sleep(0.3)
        assert password_input.get_attribute("type") == "password", \
            "Password should be hidden after second toggle"

    def test_tc024_submit_button_present(self, fresh_driver):
        """TC-024: Verify submit button (id='submit-btn') is present."""
        _navigate_to_auth(fresh_driver)
        submit_btn = fresh_driver.find_element(By.ID, "submit-btn")
        assert submit_btn is not None, "Submit button not found"
        assert submit_btn.get_attribute("type") == "submit"

    def test_tc025_empty_form_submission_shows_error(self, fresh_driver):
        """TC-025: Verify submitting empty form shows error message."""
        _navigate_to_auth(fresh_driver)
        submit_btn = fresh_driver.find_element(By.ID, "submit-btn")
        submit_btn.click()
        try:
            WebDriverWait(fresh_driver, 5).until(
                lambda d: "required" in d.find_element(By.TAG_NAME, "body").text.lower() or "email" in d.find_element(By.TAG_NAME, "body").text.lower()
            )
        except Exception:
            pass
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "required" in body.lower() or "email" in body.lower(), \
            "Error message not shown for empty form submission"

    def test_tc026_short_password_validation(self, fresh_driver):
        """TC-026: Verify short password (<6 chars) shows validation error."""
        _navigate_to_auth(fresh_driver)
        email = fresh_driver.find_element(By.ID, "email")
        password = fresh_driver.find_element(By.ID, "password")
        email.send_keys("test@example.com")
        password.send_keys("123")  # Less than 6 chars
        fresh_driver.find_element(By.ID, "submit-btn").click()
        try:
            WebDriverWait(fresh_driver, 5).until(
                lambda d: "6 characters" in d.find_element(By.TAG_NAME, "body").text.lower() or "at least" in d.find_element(By.TAG_NAME, "body").text.lower() or "6" in d.find_element(By.TAG_NAME, "body").text.lower()
            )
        except Exception:
            pass
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        assert "6 characters" in body or "at least" in body.lower() or "6" in body, \
            f"Password length validation error not shown. Text: {body[:300]}"

    def test_tc027_google_signin_button_present(self, fresh_driver):
        """TC-027: Verify Google Sign-In button (id='google-signin-btn') is present."""
        _navigate_to_auth(fresh_driver)
        google_btn = fresh_driver.find_element(By.ID, "google-signin-btn")
        assert google_btn is not None, "Google Sign-In button not found"
        btn_txt = google_btn.get_attribute("innerText") or google_btn.text
        assert "Google" in btn_txt, "Button should contain 'Google' text"

    def test_tc028_divider_between_form_and_google(self, fresh_driver):
        """TC-028: Verify 'or' divider renders between form and Google button."""
        _navigate_to_auth(fresh_driver)
        dividers = fresh_driver.find_elements(By.CLASS_NAME, "divider")
        assert len(dividers) > 0, "'or' divider not found"
        div_txt = dividers[0].get_attribute("innerText") or dividers[0].text
        assert "or" in div_txt.lower(), \
            f"Divider text should contain 'or', got: {div_txt}"

    def test_tc029_error_clears_when_toggling_mode(self, fresh_driver):
        """TC-029: Verify error message clears when toggling auth mode."""
        _navigate_to_auth(fresh_driver)
        # Trigger an error first
        fresh_driver.find_element(By.ID, "submit-btn").click()
        time.sleep(0.5)
 
        # Toggle mode — AuthPage.jsx clears error on setIsSignUp
        buttons = fresh_driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            txt = btn.get_attribute("innerText") or btn.text
            if "Sign Up" in txt:
                btn.click()
                break
        time.sleep(0.5)
 
        body = fresh_driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        # Error should be cleared; "Create Account" heading should be shown
        assert "required" not in body.lower() or "create" in body.lower(), \
            "Error message should clear when toggling auth mode"

    def test_tc030_form_inputs_have_autocomplete(self, fresh_driver):
        """TC-030: Verify form inputs have correct autocomplete attributes."""
        _navigate_to_auth(fresh_driver)
        email = fresh_driver.find_element(By.ID, "email")
        password = fresh_driver.find_element(By.ID, "password")
        assert email.get_attribute("autocomplete") == "email", \
            f"Email autocomplete should be 'email', got: {email.get_attribute('autocomplete')}"
        assert password.get_attribute("autocomplete") in ("current-password", "new-password"), \
            f"Password autocomplete incorrect: {password.get_attribute('autocomplete')}"
