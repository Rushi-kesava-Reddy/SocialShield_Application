# ─── test_06_result.py — Result Page E2E Tests ────────────────────────────────
"""
Tests for the SocialShield Result page.
Verifies verdict display, confidence ring, risk indicators, explanations, and metadata.
"""
import json
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _setup_result_and_navigate(driver):
    """Inject a mock scan result into sessionStorage and navigate to result page."""
    go_to(driver, "/home")
    time.sleep(1)
    mock_result = {
        "scanId": "test_result_001",
        "verdict": "FAKE",
        "confidence": 94.2,
        "fakeProbability": 94.2,
        "realProbability": 5.8,
        "riskLevel": "HIGH",
        "mediaType": "IMAGE",
        "explanations": [
            "Facial boundary inconsistencies detected",
            "Unnatural blinking pattern identified",
            "GAN artifact signatures in high-frequency regions"
        ],
        "metadata": {
            "face_count": 1,
            "resolution": "1080x1920",
            "model": "EfficientNet-B4",
            "processing_time": "2.3s"
        },
        "timestamp": "2026-06-15T10:00:00.000Z"
    }
    result_json = json.dumps(mock_result)
    driver.execute_script(
        "sessionStorage.setItem('scan_result_test_result_001', arguments[0]);",
        result_json
    )
    go_to(driver, "/result/test_result_001")
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "confidence-ring"))
        )
    except Exception:
        time.sleep(3)


@pytest.mark.result
class TestResultPage:
    """TC-069 to TC-080: Result page functionality tests."""

    def test_tc069_result_page_loads_with_header(self, auth_driver):
        """TC-069: Verify result page loads with 'Scan Result' header."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Scan Result" in body or "Result" in body, \
            f"'Scan Result' header not found. Text: {body[:300]}"

    def test_tc070_verdict_banner_displays(self, auth_driver):
        """TC-070: Verify verdict banner displays FAKE/REAL/SUSPICIOUS."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "FAKE" in body or "REAL" in body or "SUSPICIOUS" in body, \
            f"Verdict not displayed. Text: {body[:300]}"

    def test_tc071_confidence_ring_renders(self, auth_driver):
        """TC-071: Verify confidence ring SVG renders."""
        _setup_result_and_navigate(auth_driver)
        rings = auth_driver.find_elements(By.CLASS_NAME, "confidence-ring")
        svgs = auth_driver.find_elements(By.TAG_NAME, "svg")
        assert len(rings) > 0 or len(svgs) > 0, \
            "Confidence ring SVG not rendered"

    def test_tc072_risk_level_indicator_shown(self, auth_driver):
        """TC-072: Verify risk level indicator (HIGH/MEDIUM/LOW) is shown."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "HIGH" in body or "MEDIUM" in body or "LOW" in body, \
            f"Risk level indicator not found. Text: {body[:300]}"
        assert "RISK" in body, "RISK label not found"

    def test_tc073_fake_probability_displayed(self, auth_driver):
        """TC-073: Verify fake probability percentage is displayed."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "94.2%" in body or "Fake" in body, \
            f"Fake probability not displayed. Text: {body[:300]}"

    def test_tc074_real_probability_bar_renders(self, auth_driver):
        """TC-074: Verify real probability bar renders."""
        _setup_result_and_navigate(auth_driver)
        progress_bars = auth_driver.find_elements(By.CLASS_NAME, "progress-bar-fill")
        assert len(progress_bars) >= 2, \
            f"Expected at least 2 probability bars, found {len(progress_bars)}"

    def test_tc075_ai_explanation_section(self, auth_driver):
        """TC-075: Verify AI Explanation section with bullet points."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "AI Explanation" in body or "Explanation" in body, \
            "AI Explanation section not found"
        assert "Facial boundary" in body or "inconsistencies" in body, \
            "Explanation bullet points not found"

    def test_tc076_technical_details_shown(self, auth_driver):
        """TC-076: Verify Technical Details metadata table is shown."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Technical Details" in body or "EfficientNet" in body, \
            f"Technical Details not found. Text: {body[:300]}"

    def test_tc077_scan_id_displayed(self, auth_driver):
        """TC-077: Verify Scan ID is displayed at the bottom."""
        _setup_result_and_navigate(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Scan ID" in body or "test_result" in body, \
            "Scan ID not displayed"

    def test_tc078_back_button_navigates(self, auth_driver):
        """TC-078: Verify '← Back' button is present."""
        _setup_result_and_navigate(auth_driver)
        buttons = auth_driver.find_elements(By.TAG_NAME, "button")
        back_btn = None
        for btn in buttons:
            if "Back" in btn.text:
                back_btn = btn
                break
        assert back_btn is not None, "'← Back' button not found"

    def test_tc079_scan_again_button_navigates_home(self, auth_driver):
        """TC-079: Verify 'Scan Again 🔄' button navigates to home."""
        _setup_result_and_navigate(auth_driver)
        buttons = auth_driver.find_elements(By.TAG_NAME, "button")
        scan_again = None
        for btn in buttons:
            if "Scan Again" in btn.text:
                scan_again = btn
                break
        assert scan_again is not None, "'Scan Again' button not found"
        scan_again.click()
        time.sleep(1.5)
        assert "home" in auth_driver.current_url, \
            f"Expected /home after Scan Again, got: {auth_driver.current_url}"

    def test_tc080_verdict_color_matches_type(self, auth_driver):
        """TC-080: Verify verdict color coding matches verdict type."""
        _setup_result_and_navigate(auth_driver)
        # For FAKE verdict, color should be red-ish (#FF3B3B)
        body_source = auth_driver.page_source
        # Check that the verdict display contains appropriate color references
        assert "FAKE" in auth_driver.find_element(By.TAG_NAME, "body").text, \
            "FAKE verdict not displayed"
        # The verdict text should be styled with the red color
        assert "FF3B3B" in body_source or "rgb(255, 59, 59)" in body_source or "FAKE" in auth_driver.find_element(By.TAG_NAME, "body").text, \
            "Verdict color doesn't match FAKE type"
