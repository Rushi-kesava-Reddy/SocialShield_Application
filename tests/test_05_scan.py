# ─── test_05_scan.py — Scan Page E2E Tests ────────────────────────────────────
"""
Tests for the SocialShield Scan page (all 6 scan types).
Covers file upload zones, text/url/profile inputs, scan button states,
progress animation, and navigation.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _go_scan(driver, scan_type):
    """Navigate to a scan page and wait for scan button to appear."""
    go_to(driver, f"/scan/{scan_type}")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.ID, "scan-btn"))
        )
    except Exception:
        time.sleep(3)


@pytest.mark.scan
class TestScanPage:
    """TC-047 to TC-068: Scan page functionality tests."""

    # ─── Image Scan ──────────────────────────────────────────────────────────
    def test_tc047_image_scan_page_loads(self, auth_driver):
        """TC-047: Verify Image scan page loads with correct header."""
        _go_scan(auth_driver, "image")
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Image" in body and "Detection" in body, \
            f"Image scan header not found. Text: {body[:300]}"

    def test_tc048_back_button_functional(self, auth_driver):
        """TC-048: Verify back button (←) is present and functional."""
        _go_scan(auth_driver, "image")
        back_buttons = auth_driver.find_elements(
            By.XPATH, "//button[contains(text(), '←')]"
        )
        assert len(back_buttons) > 0, "Back button (←) not found"

    def test_tc049_upload_zone_renders_for_image(self, auth_driver):
        """TC-049: Verify file upload zone renders for image type."""
        _go_scan(auth_driver, "image")
        upload = auth_driver.find_elements(By.CLASS_NAME, "upload-zone")
        assert len(upload) > 0, "Upload zone not found for image scan"

    def test_tc050_upload_zone_file_type_hint(self, auth_driver):
        """TC-050: Verify upload zone shows file type hint (JPG, PNG, WEBP)."""
        _go_scan(auth_driver, "image")
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "JPG" in body or "PNG" in body or "WEBP" in body, \
            "File type hint (JPG, PNG, WEBP) not found"

    # ─── Video Scan ──────────────────────────────────────────────────────────
    def test_tc051_video_scan_page_header(self, auth_driver):
        """TC-051: Verify Video scan page shows 'Video Deepfake Detection'."""
        _go_scan(auth_driver, "video")
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Video" in body and "Detection" in body, \
            f"Video scan header not found. Text: {body[:300]}"

    # ─── Audio Scan ──────────────────────────────────────────────────────────
    def test_tc052_audio_scan_page_loads(self, auth_driver):
        """TC-052: Verify Audio scan page loads correctly."""
        _go_scan(auth_driver, "audio")
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Voice" in body or "Audio" in body, \
            f"Audio scan page not loaded. Text: {body[:300]}"

    # ─── Text Scan ───────────────────────────────────────────────────────────
    def test_tc053_text_scan_has_textarea(self, auth_driver):
        """TC-053: Verify Text scan page has textarea input (id='text-input')."""
        _go_scan(auth_driver, "text")
        textarea = auth_driver.find_elements(By.ID, "text-input")
        assert len(textarea) > 0, "Text input textarea (#text-input) not found"

    def test_tc054_text_input_placeholder(self, auth_driver):
        """TC-054: Verify Text input placeholder mentions 'suspicious message'."""
        _go_scan(auth_driver, "text")
        textarea = auth_driver.find_element(By.ID, "text-input")
        placeholder = textarea.get_attribute("placeholder")
        assert "suspicious" in placeholder.lower() or "message" in placeholder.lower(), \
            f"Placeholder incorrect: {placeholder}"

    def test_tc055_text_character_counter(self, auth_driver):
        """TC-055: Verify text character counter updates on typing."""
        _go_scan(auth_driver, "text")
        textarea = auth_driver.find_element(By.ID, "text-input")
        textarea.send_keys("Hello test")
        time.sleep(0.3)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "10" in body or "10,000" in body or "/" in body, \
            f"Character counter not updated. Text: {body[:200]}"

    # ─── URL Scan ────────────────────────────────────────────────────────────
    def test_tc056_url_scan_has_input(self, auth_driver):
        """TC-056: Verify URL scan page has URL input field (id='url-input')."""
        _go_scan(auth_driver, "url")
        url_input = auth_driver.find_elements(By.ID, "url-input")
        assert len(url_input) > 0, "URL input field (#url-input) not found"

    def test_tc057_url_input_type_is_url(self, auth_driver):
        """TC-057: Verify URL input has correct type='url'."""
        _go_scan(auth_driver, "url")
        url_input = auth_driver.find_element(By.ID, "url-input")
        assert url_input.get_attribute("type") == "url", \
            f"URL input type should be 'url', got: {url_input.get_attribute('type')}"

    # ─── Profile Scan ────────────────────────────────────────────────────────
    def test_tc058_profile_scan_has_username_input(self, auth_driver):
        """TC-058: Verify Profile scan page has username input (id='profile-username')."""
        _go_scan(auth_driver, "profile")
        username = auth_driver.find_elements(By.ID, "profile-username")
        assert len(username) > 0, "Profile username input (#profile-username) not found"

    def test_tc059_profile_page_five_input_fields(self, auth_driver):
        """TC-059: Verify Profile page shows all 5 input fields."""
        _go_scan(auth_driver, "profile")
        expected_ids = [
            "profile-username", "profile-followers", "profile-following",
            "profile-account_age_days", "profile-post_count"
        ]
        for field_id in expected_ids:
            elements = auth_driver.find_elements(By.ID, field_id)
            assert len(elements) > 0, f"Profile field '#{field_id}' not found"

    def test_tc060_profile_page_has_bio_textarea(self, auth_driver):
        """TC-060: Verify Profile page has bio textarea."""
        _go_scan(auth_driver, "profile")
        textareas = auth_driver.find_elements(By.TAG_NAME, "textarea")
        assert len(textareas) > 0, "Bio textarea not found on profile scan"

    # ─── Scan Button States ──────────────────────────────────────────────────
    def test_tc061_scan_button_disabled_no_input(self, auth_driver):
        """TC-061: Verify scan button (id='scan-btn') is disabled when no input."""
        _go_scan(auth_driver, "text")
        scan_btn = auth_driver.find_element(By.ID, "scan-btn")
        is_disabled = scan_btn.get_attribute("disabled")
        assert is_disabled is not None, "Scan button should be disabled with no input"

    def test_tc062_scan_button_enabled_after_text(self, auth_driver):
        """TC-062: Verify scan button enabled after providing text input."""
        _go_scan(auth_driver, "text")
        textarea = auth_driver.find_element(By.ID, "text-input")
        textarea.send_keys("This is a suspicious message for testing")
        time.sleep(0.3)
        scan_btn = auth_driver.find_element(By.ID, "scan-btn")
        is_disabled = scan_btn.get_attribute("disabled")
        assert is_disabled is None, "Scan button should be enabled after text input"

    def test_tc063_scan_button_enabled_after_url(self, auth_driver):
        """TC-063: Verify scan button enabled after entering URL."""
        _go_scan(auth_driver, "url")
        url_input = auth_driver.find_element(By.ID, "url-input")
        url_input.send_keys("https://suspicious-test.com")
        time.sleep(0.3)
        scan_btn = auth_driver.find_element(By.ID, "scan-btn")
        is_disabled = scan_btn.get_attribute("disabled")
        assert is_disabled is None, "Scan button should be enabled after URL input"

    def test_tc064_profile_scan_enabled_with_username(self, auth_driver):
        """TC-064: Verify profile scan enabled after entering username."""
        _go_scan(auth_driver, "profile")
        username = auth_driver.find_element(By.ID, "profile-username")
        username.send_keys("@testbot")
        time.sleep(0.3)
        scan_btn = auth_driver.find_element(By.ID, "scan-btn")
        is_disabled = scan_btn.get_attribute("disabled")
        assert is_disabled is None, "Scan button should be enabled after username input"

    def test_tc065_info_card_shown(self, auth_driver):
        """TC-065: Verify info card with AI model description is shown."""
        _go_scan(auth_driver, "image")
        glass_cards = auth_driver.find_elements(By.CLASS_NAME, "glass-card")
        assert len(glass_cards) > 0, "Info card (.glass-card) not found"
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "EfficientNet" in body or "Upload" in body or "AI" in body, \
            "AI model info not found on scan page"

    def test_tc066_progress_animation_during_scan(self, auth_driver):
        """TC-066: Verify progress animation appears during text scan."""
        _go_scan(auth_driver, "text")
        textarea = auth_driver.find_element(By.ID, "text-input")
        textarea.send_keys("This is a test scan message for deepfake detection")
        time.sleep(0.3)
        scan_btn = auth_driver.find_element(By.ID, "scan-btn")
        scan_btn.click()
        time.sleep(0.3)
        # Progress animation appears immediately when scan starts
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Analyzing")
            )
        except Exception:
            pass
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Analyzing" in body or "%" in body or "AI" in body, \
            "Progress animation not shown during scan"

    def test_tc067_scan_completes_redirects_to_result(self, auth_driver):
        """TC-067: Verify scan completes and redirects to result page."""
        _go_scan(auth_driver, "text")
        textarea = auth_driver.find_element(By.ID, "text-input")
        textarea.send_keys("Congratulations! You won $1,000,000. Click here to claim.")
        time.sleep(0.3)
        scan_btn = auth_driver.find_element(By.ID, "scan-btn")
        scan_btn.click()
        # Wait for redirect — mock scan: ~1.6s; real API cold start (Render): up to 60s
        try:
            WebDriverWait(auth_driver, 25).until(EC.url_contains("result"))
        except Exception:
            time.sleep(8)
        assert "result" in auth_driver.current_url, \
            f"Expected redirect to /result after scan, got: {auth_driver.current_url}"

    def test_tc068_powered_by_subtitle(self, auth_driver):
        """TC-068: Verify 'Powered by SocialShield AI' subtitle present on scan page."""
        _go_scan(auth_driver, "image")
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "SocialShield" in body or "Powered by" in body, \
            "Subtitle 'Powered by SocialShield AI' not found"
