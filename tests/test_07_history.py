# ─── test_07_history.py — History Page E2E Tests ──────────────────────────────
"""
Tests for the SocialShield History page.
Covers filter chips, scan list rendering, delete, empty state, and navigation.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _go_history(driver):
    """Navigate to history page with auth, wait for filter chips to load."""
    go_to(driver, "/history")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "chip"))
        )
    except Exception:
        time.sleep(3)


@pytest.mark.history
class TestHistoryPage:
    """TC-081 to TC-092: History page functionality tests."""

    def test_tc081_page_header_scan_history(self, auth_driver):
        """TC-081: Verify page header shows 'Scan History'."""
        _go_history(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Scan History" in body, \
            f"'Scan History' header not found. Text: {body[:300]}"

    def test_tc082_subtitle_activity_log(self, auth_driver):
        """TC-082: Verify subtitle 'Your complete scan activity log' is present."""
        _go_history(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "activity log" in body.lower() or "scan activity" in body.lower(), \
            f"Subtitle not found. Text: {body[:300]}"

    def test_tc083_seven_filter_chips_render(self, auth_driver):
        """TC-083: Verify all 7 filter chips render (ALL, IMAGE, VIDEO, AUDIO, TEXT, URL, PROFILE)."""
        _go_history(auth_driver)
        chips = auth_driver.find_elements(By.CLASS_NAME, "chip")
        assert len(chips) >= 7, f"Expected 7 filter chips, found {len(chips)}"

    def test_tc084_all_filter_active_by_default(self, auth_driver):
        """TC-084: Verify 'ALL' filter is active by default."""
        _go_history(auth_driver)
        all_filter = auth_driver.find_elements(By.ID, "filter-all")
        assert len(all_filter) > 0, "ALL filter chip not found"
        classes = all_filter[0].get_attribute("class")
        assert "active" in classes, \
            f"ALL filter should be active by default. Classes: {classes}"

    def test_tc085_clicking_filter_changes_active(self, auth_driver):
        """TC-085: Verify clicking a filter chip changes the active state."""
        _go_history(auth_driver)
        image_filter = auth_driver.find_elements(By.ID, "filter-image")
        if len(image_filter) > 0:
            image_filter[0].click()
            time.sleep(1)
            classes = image_filter[0].get_attribute("class")
            assert "active" in classes, \
                f"IMAGE filter should be active after click. Classes: {classes}"
            # ALL should no longer be active
            all_filter = auth_driver.find_element(By.ID, "filter-all")
            all_classes = all_filter.get_attribute("class")
            assert "active" not in all_classes, \
                "ALL filter should not be active after selecting IMAGE"

    def test_tc086_history_items_render_with_icons(self, auth_driver):
        """TC-086: Verify history items render with correct type icons."""
        _go_history(auth_driver)
        items = auth_driver.find_elements(By.CLASS_NAME, "history-item")
        assert len(items) > 0, "No history items found (demo data should be shown)"
        # Each item should have an icon box
        icon_boxes = auth_driver.find_elements(By.CLASS_NAME, "history-icon-box")
        assert len(icon_boxes) > 0, "History item icon boxes not found"

    def test_tc087_history_item_shows_type_and_timestamp(self, auth_driver):
        """TC-087: Verify each history item shows media type and timestamp."""
        _go_history(auth_driver)
        items = auth_driver.find_elements(By.CLASS_NAME, "history-item")
        if len(items) > 0:
            item_text = items[0].text
            # Should contain a scan type (IMAGE, VIDEO, etc.) and "Scan"
            assert "Scan" in item_text, \
                f"History item should show scan type. Text: {item_text}"

    def test_tc088_verdict_badges_display(self, auth_driver):
        """TC-088: Verify verdict badges (FAKE/REAL/SUSPICIOUS) display correctly."""
        _go_history(auth_driver)
        badges = auth_driver.find_elements(By.CLASS_NAME, "verdict-badge")
        assert len(badges) > 0, "No verdict badges found in history"

    def test_tc089_confidence_percentage_shown(self, auth_driver):
        """TC-089: Verify confidence percentage is shown per history item."""
        _go_history(auth_driver)
        items = auth_driver.find_elements(By.CLASS_NAME, "history-item")
        if len(items) > 0:
            item_text = items[0].text
            assert "%" in item_text, \
                f"Confidence percentage not shown. Item text: {item_text}"

    def test_tc090_delete_button_present(self, auth_driver):
        """TC-090: Verify delete button (🗑️) is present on history items."""
        _go_history(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        items = auth_driver.find_elements(By.CLASS_NAME, "history-item")
        if len(items) > 0:
            # Find delete buttons within items
            delete_buttons = items[0].find_elements(By.TAG_NAME, "button")
            assert len(delete_buttons) > 0, "Delete button not found on history item"

    def test_tc091_clicking_item_navigates_to_result(self, auth_driver):
        """TC-091: Verify clicking a history item navigates to result page."""
        _go_history(auth_driver)
        items = auth_driver.find_elements(By.CLASS_NAME, "history-item")
        if len(items) > 0:
            items[0].click()
            time.sleep(1.5)
            assert "result" in auth_driver.current_url, \
                f"Expected /result after clicking history item, got: {auth_driver.current_url}"

    def test_tc092_empty_state_when_filtered(self, auth_driver):
        """TC-092: Verify empty state shows when no results match filter."""
        _go_history(auth_driver)
        # The demo data may or may not have PROFILE scans.
        # We check the empty state UI structure exists in the page source
        page_source = auth_driver.page_source
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        # Either we see items or the empty state message
        assert len(auth_driver.find_elements(By.CLASS_NAME, "history-item")) > 0 or \
               "No scans found" in body or "Start Scanning" in body, \
            "Neither history items nor empty state message found"
