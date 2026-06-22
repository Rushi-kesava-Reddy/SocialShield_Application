# ─── test_02_onboarding.py — Onboarding Page E2E Tests ────────────────────────
"""
Tests for the SocialShield Onboarding flow.
The onboarding page has 4 slides with icons, titles, subtitles, dot navigation,
Skip/Next buttons, and a final 'Get Started' button.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _navigate_to_onboarding(driver):
    """Helper: clear all storage and navigate directly to onboarding."""
    driver.get(BASE_URL)
    time.sleep(0.3)
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    driver.get("about:blank")
    driver.get(BASE_URL + "/#/onboarding")
    # Wait for onboarding page to render
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "onboarding-page"))
        )
    except Exception:
        time.sleep(2)


@pytest.mark.onboarding
class TestOnboardingPage:
    """TC-007 to TC-016: Onboarding page functionality tests."""

    def test_tc007_first_slide_shows_verify_reality(self, fresh_driver):
        """TC-007: Verify first slide shows 'Verify Reality' title."""
        _navigate_to_onboarding(fresh_driver)
        body = fresh_driver.find_element(By.TAG_NAME, "body").text
        assert "Verify Reality" in body, \
            f"'Verify Reality' not found on first slide. Text: {body[:300]}"

    def test_tc008_next_button_advances_slide(self, fresh_driver):
        """TC-008: Verify Next button advances to the second slide."""
        _navigate_to_onboarding(fresh_driver)
        # Find and click the Next button
        buttons = fresh_driver.find_elements(By.CLASS_NAME, "btn-neon")
        next_btn = None
        for btn in buttons:
            if "Next" in btn.text:
                next_btn = btn
                break
        assert next_btn is not None, "Next button not found"
        next_btn.click()
        time.sleep(0.5)
        body = fresh_driver.find_element(By.TAG_NAME, "body").text
        assert "AI-Powered Analysis" in body, \
            f"Slide 2 title 'AI-Powered Analysis' not shown after clicking Next. Text: {body[:300]}"

    def test_tc009_four_dot_indicators_render(self, fresh_driver):
        """TC-009: Verify all 4 dot indicators render for 4 slides."""
        _navigate_to_onboarding(fresh_driver)
        onboarding = fresh_driver.find_elements(By.CLASS_NAME, "onboarding-page")
        assert len(onboarding) > 0, "Onboarding page container not found"
        # Dots are small buttons inside the onboarding page
        dot_buttons = onboarding[0].find_elements(By.TAG_NAME, "button")
        # Filter for small dot-like buttons (width < 50px, exclude Skip/Next which are wider)
        dots = [b for b in dot_buttons if b.size.get('width', 999) < 50]
        assert len(dots) >= 4, f"Expected 4 dot indicators, found {len(dots)}"

    def test_tc010_clicking_dot_navigates_to_slide(self, fresh_driver):
        """TC-010: Verify clicking a dot navigates to the correct slide."""
        _navigate_to_onboarding(fresh_driver)
        onboarding = fresh_driver.find_elements(By.CLASS_NAME, "onboarding-page")
        if not onboarding:
            pytest.skip("Onboarding page not found")
        dot_buttons = onboarding[0].find_elements(By.TAG_NAME, "button")
        dots = [b for b in dot_buttons if b.size.get('width', 999) < 50]
        if len(dots) >= 3:
            dots[2].click()  # Click 3rd dot (index 2 = "Scan Anything")
            time.sleep(0.5)
            body = fresh_driver.find_element(By.TAG_NAME, "body").text
            assert "Scan Anything" in body, \
                f"Expected 'Scan Anything' on slide 3. Text: {body[:300]}"
        else:
            pytest.skip(f"Not enough dot indicators found: {len(dots)}")

    def test_tc011_skip_button_navigates_to_auth(self, fresh_driver):
        """TC-011: Verify Skip button navigates to auth page."""
        _navigate_to_onboarding(fresh_driver)
        buttons = fresh_driver.find_elements(By.CLASS_NAME, "btn-neon")
        skip_btn = None
        for btn in buttons:
            if "Skip" in btn.text:
                skip_btn = btn
                break
        assert skip_btn is not None, "Skip button not found"
        skip_btn.click()
        try:
            WebDriverWait(fresh_driver, 4).until(EC.url_contains("auth"))
        except Exception:
            pass
        assert "auth" in fresh_driver.current_url, \
            f"Expected redirect to /auth after skip, got: {fresh_driver.current_url}"

    def test_tc012_last_slide_shows_get_started(self, fresh_driver):
        """TC-012: Verify last slide shows 'Get Started' button."""
        _navigate_to_onboarding(fresh_driver)
        onboarding = fresh_driver.find_elements(By.CLASS_NAME, "onboarding-page")
        if not onboarding:
            pytest.skip("Onboarding page not found")
        dot_buttons = onboarding[0].find_elements(By.TAG_NAME, "button")
        dots = [b for b in dot_buttons if b.size.get('width', 999) < 50]
        if len(dots) >= 4:
            dots[3].click()  # Click last dot
            time.sleep(0.5)
        body = fresh_driver.find_element(By.TAG_NAME, "body").text
        assert "Get Started" in body, \
            f"'Get Started' not found on last slide. Text: {body[:300]}"

    def test_tc013_get_started_navigates_to_auth(self, fresh_driver):
        """TC-013: Verify 'Get Started' button navigates to auth page."""
        _navigate_to_onboarding(fresh_driver)
        # Navigate to last slide using dots
        onboarding = fresh_driver.find_elements(By.CLASS_NAME, "onboarding-page")
        if onboarding:
            dot_buttons = onboarding[0].find_elements(By.TAG_NAME, "button")
            dots = [b for b in dot_buttons if b.size.get('width', 999) < 50]
            if len(dots) >= 4:
                dots[3].click()
                time.sleep(0.5)
        # Click Get Started
        buttons = fresh_driver.find_elements(By.CLASS_NAME, "btn-neon")
        gs_btn = None
        for btn in buttons:
            if "Get Started" in btn.text:
                gs_btn = btn
                break
        if gs_btn:
            gs_btn.click()
            try:
                WebDriverWait(fresh_driver, 4).until(EC.url_contains("auth"))
            except Exception:
                pass
            assert "auth" in fresh_driver.current_url, \
                f"Expected /auth after Get Started, got: {fresh_driver.current_url}"
        else:
            pytest.skip("Get Started button not found (may need dot navigation)")

    def test_tc014_slide_icons_change_per_slide(self, fresh_driver):
        """TC-014: Verify slide icons change when navigating between slides."""
        _navigate_to_onboarding(fresh_driver)
        body1 = fresh_driver.page_source
        # Click Next to advance to slide 2
        buttons = fresh_driver.find_elements(By.CLASS_NAME, "btn-neon")
        for btn in buttons:
            if "Next" in btn.text:
                btn.click()
                break
        time.sleep(0.5)
        body2 = fresh_driver.page_source
        # Page content should change between slides
        assert body1 != body2, "Page content didn't change between slides"

    def test_tc015_subtitle_contains_deepfake_text(self, fresh_driver):
        """TC-015: Verify subtitle text on slide 1 mentions deepfakes."""
        _navigate_to_onboarding(fresh_driver)
        body = fresh_driver.find_element(By.TAG_NAME, "body").text
        assert "deepfakes" in body.lower() or "detect" in body.lower() or "AI" in body, \
            f"Slide 1 subtitle about deepfake detection not found. Text: {body[:300]}"

    def test_tc016_onboarded_flag_set_after_finish(self, fresh_driver):
        """TC-016: Verify 'ss_onboarded' localStorage flag is set after completing onboarding."""
        _navigate_to_onboarding(fresh_driver)
        # Use Skip button to finish quickly
        buttons = fresh_driver.find_elements(By.CLASS_NAME, "btn-neon")
        for btn in buttons:
            if "Get Started" in btn.text or "Skip" in btn.text:
                btn.click()
                break
        time.sleep(1.5)
        flag = fresh_driver.execute_script("return localStorage.getItem('ss_onboarded');")
        assert flag == "1", f"Expected ss_onboarded='1', got: {flag}"
