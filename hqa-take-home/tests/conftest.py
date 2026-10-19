import base64
import os
from pathlib import Path

import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.sports_betting_page import SportsBettingPage


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--window-size=1440,900")
    if os.getenv("HQA_HEADLESS") == "1":
        options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


@pytest.fixture
def betting_page(driver, user_id):
    return SportsBettingPage(driver, user_id)


@pytest.fixture
def ready_page(request, betting_api):
    """Reset funds, then open a browser. The bet slip has no reset control of its own."""
    betting_api.prepare_balance()
    return request.getfixturevalue("betting_page")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page = item.funcargs.get("ready_page") or item.funcargs.get("betting_page")
    browser = item.funcargs.get("driver") or getattr(page, "driver", None)
    if browser is None:
        return
    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    screenshot = reports / f"{item.name}.png"
    browser.save_screenshot(str(screenshot))
    encoded = base64.b64encode(screenshot.read_bytes()).decode("ascii")
    report.extras = getattr(report, "extras", [])
    report.extras.append(pytest_html.extras.png(encoded, name="Failure screenshot"))
