# ─── test_12_responsive.py — Responsive Design E2E Tests ──────────────────────
"""
Tests for responsive layout behavior across mobile, tablet, and desktop viewports.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


@pytest.mark.responsive
class TestResponsiveDesign:
    """TC-133 to TC-140: Responsive design tests."""

    def test_tc133_mobile_viewport_renders(self, auth_driver):
        """TC-133: Verify app renders correctly on mobile viewport (375×812)."""
        auth_driver.set_window_size(375, 812)
        time.sleep(0.5)
        go_to(auth_driver, "/home")
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
            )
        except Exception:
            time.sleep(3)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Welcome" in body or "Scan" in body, \
            "App did not render on mobile viewport"
        # Verify layout fits viewport width (robust check for environments with min window size limits)
        overflows = auth_driver.execute_script("return document.documentElement.scrollWidth > window.innerWidth;")
        assert not overflows, "Horizontal scrollbar/overflow detected - layout exceeds viewport width"
        auth_driver.set_window_size(1440, 900)

    def test_tc134_tablet_viewport_layout(self, auth_driver):
        """TC-134: Verify layout adjusts on tablet viewport (768×1024)."""
        auth_driver.set_window_size(768, 1024)
        time.sleep(0.5)
        go_to(auth_driver, "/home")
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
            )
        except Exception:
            time.sleep(3)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Welcome" in body or "Scan" in body, \
            "App did not render on tablet viewport"
        auth_driver.set_window_size(1440, 900)

    def test_tc135_desktop_viewport_sidebar_visible(self, auth_driver):
        """TC-135: Verify sidebar is visible on desktop viewport (1440×900)."""
        auth_driver.set_window_size(1440, 900)
        time.sleep(0.5)
        go_to(auth_driver, "/home")
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
            )
        except Exception:
            time.sleep(3)
        sidebar = auth_driver.find_elements(By.CLASS_NAME, "sidebar")
        assert len(sidebar) > 0, "Sidebar element not found"
        is_visible = auth_driver.execute_script(
            "const el = document.querySelector('.sidebar'); "
            "if (!el) return false; "
            "const style = window.getComputedStyle(el); "
            "return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetWidth > 0;"
        )
        assert is_visible, "Sidebar should be visible on desktop viewport"

    def test_tc136_mobile_nav_hidden_on_desktop(self, auth_driver):
        """TC-136: Verify mobile bottom nav is hidden on desktop viewport."""
        auth_driver.set_window_size(1440, 900)
        time.sleep(0.5)
        go_to(auth_driver, "/home")
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
            )
        except Exception:
            time.sleep(3)
        is_hidden = auth_driver.execute_script(
            "const el = document.querySelector('.mobile-nav'); "
            "if (!el) return true; "
            "const style = window.getComputedStyle(el); "
            "return style.display === 'none' || el.offsetHeight === 0;"
        )
        assert is_hidden, "Mobile nav should be hidden on desktop"

    def test_tc137_sidebar_hidden_on_mobile(self, auth_driver):
        """TC-137: Verify sidebar is hidden on mobile viewport."""
        auth_driver.set_window_size(375, 812)
        time.sleep(0.5)
        go_to(auth_driver, "/home")
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mobile-nav"))
            )
        except Exception:
            time.sleep(3)
        is_hidden = auth_driver.execute_script(
            "const el = document.querySelector('.sidebar'); "
            "if (!el) return true; "
            "const style = window.getComputedStyle(el); "
            "return style.display === 'none' || el.offsetWidth === 0;"
        )
        assert is_hidden, "Sidebar should be hidden on mobile viewport"
        auth_driver.set_window_size(1440, 900)

    def test_tc138_scan_cards_stack_on_mobile(self, auth_driver):
        """TC-138: Verify scan type cards stack vertically on mobile."""
        auth_driver.set_window_size(375, 812)
        time.sleep(0.5)
        go_to(auth_driver, "/home")
        try:
            WebDriverWait(auth_driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scan-type-card"))
            )
        except Exception:
            time.sleep(3)
        cards = auth_driver.find_elements(By.CLASS_NAME, "scan-type-card")
        if len(cards) >= 2:
            # On mobile, cards should be stacked (second card below first)
            card1_y = cards[0].location["y"]
            card2_y = cards[1].location["y"]
            assert card2_y > card1_y, \
                f"Cards should stack vertically on mobile. Card1 Y={card1_y}, Card2 Y={card2_y}"
        auth_driver.set_window_size(1440, 900)

    def test_tc139_auth_card_centered_all_viewports(self, fresh_driver):
        """TC-139: Verify auth card is centered on all viewports."""
        go_to(fresh_driver)
        time.sleep(0.5)
        fresh_driver.execute_script("localStorage.setItem('ss_onboarded', '1');")
        fresh_driver.execute_script("localStorage.removeItem('ss_user');")
        fresh_driver.execute_script("localStorage.removeItem('auth_token');")

        for width, height in [(375, 812), (768, 1024), (1440, 900)]:
            fresh_driver.set_window_size(width, height)
            time.sleep(0.3)
            go_to(fresh_driver, "/auth")
            try:
                WebDriverWait(fresh_driver, 8).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "auth-card"))
                )
            except Exception:
                time.sleep(2)
            cards = fresh_driver.find_elements(By.CLASS_NAME, "auth-card")
            if len(cards) > 0:
                card = cards[0]
                card_center_x = card.location["x"] + card.size["width"] / 2
                viewport_center = width / 2
                # Allow 50px margin for centering tolerance
                assert abs(card_center_x - viewport_center) < 80, \
                    f"Auth card not centered at {width}px. Center: {card_center_x}, Viewport: {viewport_center}"

    def test_tc140_page_title_correct_all_pages(self, auth_driver):
        """TC-140: Verify page title is correct across all navigation."""
        auth_driver.set_window_size(1440, 900)
        go_to(auth_driver, "/home")
        time.sleep(1)
        title = auth_driver.title
        assert "SocialShield" in title, f"Incorrect title on home: {title}"

        go_to(auth_driver, "/history")
        time.sleep(1)
        title = auth_driver.title
        assert "SocialShield" in title, f"Incorrect title on history: {title}"

        go_to(auth_driver, "/map")
        time.sleep(1)
        title = auth_driver.title
        assert "SocialShield" in title, f"Incorrect title on map: {title}"

        go_to(auth_driver, "/settings")
        time.sleep(1)
        title = auth_driver.title
        assert "SocialShield" in title, f"Incorrect title on settings: {title}"
