# ─── conftest.py — Shared Pytest Fixtures for Selenium E2E Tests ──────────────
import os
import json
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ─── Base URL ──────────────────────────────────────────────────────────────────
# Set SITE_URL env var to your GitHub Pages URL, e.g.:
#   https://rushi-kesava-reddy.github.io/SocialShield_Application/
BASE_URL = os.environ.get("SITE_URL", "https://rushi-kesava-reddy.github.io/SocialShield_Application/")

# Remove trailing slash for consistency
BASE_URL = BASE_URL.rstrip("/")


# ─── Screenshot directory ─────────────────────────────────────────────────────
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "test-results", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# ─── Chrome Options ───────────────────────────────────────────────────────────
def _chrome_options():
    """Configure headless Chrome for CI environments."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--allow-running-insecure-content")
    return opts


# ─── Driver Fixture (module-scoped) ───────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """Create a headless Chrome WebDriver for the test module."""
    opts = _chrome_options()
    try:
        service = Service(ChromeDriverManager().install())
        drv = webdriver.Chrome(service=service, options=opts)
    except Exception:
        # Fallback: use system chrome/chromedriver
        drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(5)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()


# ─── Function-scoped Driver ──────────────────────────────────────────────────
@pytest.fixture(scope="function")
def fresh_driver():
    """Create a fresh headless Chrome WebDriver per test function."""
    opts = _chrome_options()
    try:
        service = Service(ChromeDriverManager().install())
        drv = webdriver.Chrome(service=service, options=opts)
    except Exception:
        drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(5)
    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()


# ─── Authenticated Driver ────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def auth_driver():
    """
    Create a WebDriver pre-authenticated by injecting localStorage tokens.
    This bypasses Firebase auth for E2E testing on the static build.
    """
    opts = _chrome_options()
    try:
        service = Service(ChromeDriverManager().install())
        drv = webdriver.Chrome(service=service, options=opts)
    except Exception:
        drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(5)
    drv.set_page_load_timeout(30)

    # Navigate to the site first (required before setting localStorage)
    drv.get(BASE_URL)
    import time
    time.sleep(1)

    # Inject demo auth tokens into localStorage
    demo_user = json.dumps({
        "uid": "e2e_test_user",
        "email": "e2e@socialshield.ai",
        "displayName": "E2E Tester"
    })
    drv.execute_script(f"""
        localStorage.setItem('ss_user', '{demo_user}');
        localStorage.setItem('auth_token', 'e2e_test_token_{{}}'.replace('{{}}', Date.now()));
        localStorage.setItem('ss_onboarded', '1');
    """)

    yield drv
    drv.quit()


# ─── Auto-screenshot on failure ───────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver_fixture = item.funcargs.get("driver") or item.funcargs.get("auth_driver") or item.funcargs.get("fresh_driver")
        if driver_fixture:
            screenshot_name = f"{item.nodeid.replace('::', '_').replace('/', '_')}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_name)
            try:
                driver_fixture.save_screenshot(screenshot_path)
            except Exception:
                pass


# ─── Helper: navigate to a route ──────────────────────────────────────────────
def go_to(driver, path=""):
    """Navigate the driver to BASE_URL + path."""
    url = f"{BASE_URL}/{path.lstrip('/')}" if path else BASE_URL
    driver.get(url)
