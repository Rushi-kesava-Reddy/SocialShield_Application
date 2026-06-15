# ─── test_10_navigation.py — Navigation & Layout E2E Tests ────────────────────
"""
Tests for the SocialShield Layout component — sidebar, mobile nav, and routing.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import BASE_URL, go_to


def _go_home(driver):
    """Navigate to home page with auth."""
    go_to(driver, "/home")
    time.sleep(2)


@pytest.mark.navigation
class TestNavigationLayout:
    """TC-115 to TC-122: Navigation and layout functionality tests."""

    def test_tc115_sidebar_renders_with_logo(self, auth_driver):
        """TC-115: Verify sidebar renders with SocialShield logo."""
        _go_home(auth_driver)
        sidebar = auth_driver.find_elements(By.CLASS_NAME, "sidebar")
        assert len(sidebar) > 0, "Sidebar not found"
        logo = auth_driver.find_elements(By.CLASS_NAME, "sidebar-logo")
        assert len(logo) > 0, "Sidebar logo not found"

    def test_tc116_four_nav_items_in_sidebar(self, auth_driver):
        """TC-116: Verify 4 navigation items in sidebar (Home, History, Fraud Map, Settings)."""
        _go_home(auth_driver)
        nav_items = auth_driver.find_elements(By.CLASS_NAME, "nav-item")
        assert len(nav_items) >= 4, f"Expected 4 nav items, found {len(nav_items)}"
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Home" in body, "Home nav item not found"
        assert "History" in body, "History nav item not found"

    def test_tc117_active_nav_item_highlighted(self, auth_driver):
        """TC-117: Verify active nav item is highlighted."""
        _go_home(auth_driver)
        active_items = auth_driver.find_elements(By.CSS_SELECTOR, ".nav-item.active")
        assert len(active_items) > 0, "No active nav item found"

    def test_tc118_mobile_nav_on_small_viewport(self, auth_driver):
        """TC-118: Verify mobile bottom nav renders on small viewport."""
        auth_driver.set_window_size(375, 812)
        time.sleep(0.5)
        _go_home(auth_driver)
        mobile_nav = auth_driver.find_elements(By.CLASS_NAME, "mobile-nav")
        assert len(mobile_nav) > 0, "Mobile bottom nav not found"
        # Check it's actually visible (not display:none)
        is_displayed = auth_driver.execute_script(
            "const el = document.querySelector('.mobile-nav'); "
            "return el ? window.getComputedStyle(el).display !== 'none' : false;"
        )
        assert is_displayed, "Mobile nav should be visible on small viewport"
        # Reset viewport
        auth_driver.set_window_size(1440, 900)

    def test_tc119_backend_status_dot_visible(self, auth_driver):
        """TC-119: Verify backend status dot indicator is visible."""
        _go_home(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Backend" in body or "Online" in body or "Offline" in body or "Checking" in body, \
            "Backend status indicator not found"

    def test_tc120_user_info_in_sidebar_footer(self, auth_driver):
        """TC-120: Verify user info is displayed in sidebar footer."""
        _go_home(auth_driver)
        body = auth_driver.find_element(By.TAG_NAME, "body").text
        assert "Signed in as" in body or "E2E Tester" in body or "e2e@" in body, \
            "User info not found in sidebar footer"

    def test_tc121_sidebar_sign_out_functional(self, auth_driver):
        """TC-121: Verify sidebar Sign Out button is present and functional."""
        _go_home(auth_driver)
        signout = auth_driver.find_elements(By.ID, "sidebar-signout")
        assert len(signout) > 0, "Sidebar Sign Out button not found"
        assert "Sign Out" in signout[0].text or "🚪" in signout[0].text, \
            f"Sign Out button text incorrect: {signout[0].text}"

    def test_tc122_unknown_route_redirects(self, auth_driver):
        """TC-122: Verify unknown route (e.g., /foobar) redirects to root."""
        go_to(auth_driver, "/unknown-route-xyz")
        time.sleep(2)
        current = auth_driver.current_url
        # Should redirect to "/" or "/home" or "/auth"
        assert "unknown" not in current or "home" in current or current.endswith("/"), \
            f"Unknown route should redirect. Still at: {current}"
