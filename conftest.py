import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from api.client import BettingApiClient
import os

BASE_URL = "https://qae-assignment-tau.vercel.app/"
USER_ID = "candidate-N6pYw2Jk7A"
FULL_URL = f"{BASE_URL}/?user-id={USER_ID}"



@pytest.fixture(scope="function")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    driver.get(FULL_URL)
    yield driver
    driver.quit()

@pytest.fixture
def screenshot_dir():
    """Create one main 'screenshots' folder in root with timestamped files"""
    base_dir = "screenshots"
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

#── API client fixture ─────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def api():
    """Yields a configured BettingApiClient instance."""
    yield BettingApiClient(user_id=USER_ID)


# ── Balance reset fixture ──────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset(api):
    """Resets balance before every test."""
    r = api.reset_balance()
    assert r.status_code == 200
    yield

