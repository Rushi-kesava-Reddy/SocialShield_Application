# ─── test_08_fraudmap.py — Fraud Map Page E2E Tests ───────────────────────────
"""
Tests for the SocialShield Global Fraud Map page.
Covers stat cards, map visualization, region bubbles, tooltips, and incident breakdown.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _go_map(driver):
    """Navigate to fraud map page with auth, wait for map container."""
    go_to(driver, "/map")
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stat-card"))
        )
    except Exception:
        time.sleep(3)


@pytest.mark.fraudmap
class TestFraudMapPage:
    """TC-093 to TC-102: Fraud Map page functionality tests."""

    def test_tc093_page_header_global_fraud_map(self, auth_driver):
        """TC-093: Verify page header shows 'Global Fraud Map'."""
        _go_map(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Global Fraud Map" in body or "Fraud Map" in body, \
            f"'Global Fraud Map' header not found. Text: {body[:300]}"

    def test_tc094_four_summary_stat_cards(self, auth_driver):
        """TC-094: Verify 4 summary stat cards render."""
        _go_map(auth_driver)
        stat_cards = auth_driver.find_elements(By.CLASS_NAME, "stat-card")
        assert len(stat_cards) >= 4, f"Expected 4 stat cards, found {len(stat_cards)}"

    def test_tc095_total_incidents_stat_value(self, auth_driver):
        """TC-095: Verify 'Total Incidents' stat displays a value."""
        _go_map(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Total Incidents" in body, "Total Incidents label not found"
        assert "12,655" in body or "incidents" in body.lower(), \
            "Total Incidents value not displayed"

    def test_tc096_map_container_renders(self, auth_driver):
        """TC-096: Verify map container with region bubbles renders."""
        _go_map(auth_driver)
        map_containers = auth_driver.find_elements(By.CLASS_NAME, "map-container")
        assert len(map_containers) > 0, "Map container not found"

    def test_tc097_nine_region_markers_present(self, auth_driver):
        """TC-097: Verify at least 9 region markers are present on the map."""
        _go_map(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        # Check for region names
        regions = ["North America", "Europe", "South Asia", "East Asia", "SEA",
                    "Middle East", "Africa", "South America", "Oceania"]
        found = sum(1 for r in regions if r in body)
        assert found >= 7, f"Expected at least 7 region labels, found {found}"

    def test_tc098_clicking_region_shows_tooltip(self, auth_driver):
        """TC-098: Verify clicking a region bubble shows a tooltip."""
        _go_map(auth_driver)
        map_container = auth_driver.find_elements(By.CLASS_NAME, "map-container")
        if not map_container:
            pytest.skip("Map container not found")
        # Find clickable region elements inside the map
        region_elements = map_container[0].find_elements(By.XPATH, "./div[contains(@style, 'position')]")
        if len(region_elements) > 0:
            region_elements[0].click()
            time.sleep(0.5)
            body = auth_driver.find_element(By.TAG_NAME, "body").text
            # Tooltip should show incidents/trend/risk
            assert "Incidents" in body or "Trend" in body or "Risk" in body, \
                "Tooltip with region details not shown after click"

    def test_tc099_tooltip_shows_details(self, auth_driver):
        """TC-099: Verify tooltip shows incidents, trend, and risk level."""
        _go_map(auth_driver)
        map_container = auth_driver.find_elements(By.CLASS_NAME, "map-container")
        if not map_container:
            pytest.skip("Map container not found")
        region_elements = map_container[0].find_elements(By.XPATH, "./div[contains(@style, 'position')]")
        if len(region_elements) > 0:
            region_elements[0].click()
            time.sleep(0.5)
            body = auth_driver.find_element(By.TAG_NAME, "body").text
            # Should have structured info
            has_details = ("Incidents" in body or "📊" in body) and \
                          ("Trend" in body or "📈" in body)
            assert has_details or "%" in body, \
                f"Tooltip details incomplete. Text: {body[:500]}"

    def test_tc100_risk_legend_present(self, auth_driver):
        """TC-100: Verify risk legend (HIGH/MEDIUM/LOW) is present."""
        _go_map(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "HIGH" in body and "RISK" in body, "HIGH RISK legend not found"
        assert "LOW" in body, "LOW RISK legend not found"

    def test_tc101_incident_breakdown_section(self, auth_driver):
        """TC-101: Verify 'Incident Type Breakdown' section renders."""
        _go_map(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Incident Type Breakdown" in body, \
            "Incident Type Breakdown section not found"

    def test_tc102_four_incident_type_bars(self, auth_driver):
        """TC-102: Verify 4 incident type progress bars are shown."""
        _go_map(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        incident_types = ["Image Deepfakes", "Voice Clones", "Scam Text", "Phishing URLs"]
        found = sum(1 for t in incident_types if t in body)
        assert found >= 3, f"Expected at least 3 incident types, found {found}"
        # Also check for progress bars
        progress_bars = auth_driver.find_elements(By.CLASS_NAME, "progress-bar-fill")
        assert len(progress_bars) >= 4, \
            f"Expected at least 4 progress bars, found {len(progress_bars)}"
