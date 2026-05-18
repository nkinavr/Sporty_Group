# Sports Betting QA — Automation Framework

QA assessment submission covering manual test planning, execution, bug reports, automation framework, api and strategy.

**Application under test:** https://qae-assignment-tau.vercel.app/  
**Stack:** Python 3.11 · Selenium WebDriver · Pytest · requests

---

## Note on testing timeline:
The active testing effort required approximately 6–8 hours of focused work. 
However, the overall calendar duration extended to 10 days due to external factors, including a regional storm that caused intermittent electricity and network outages. These delays did not impact the quality or depth of the testing, which remained thorough and aligned with the assignment's requirements.


---

## Setup

### 1. Clone and 
```

### 2. Install dependencies

**Option A — pip (recommended for quick setup):**

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


### 3. Chrome

The framework uses `webdriver-manager` to automatically download the correct `chromedriver`. 
You just need Chrome installed:

- **macOS:** `brew install --cask google-chrome`
- **Linux:** `sudo apt-get install -y google-chrome-stable`
- **Windows:** Download from https://google.com/chrome

---

## Running Tests

```bash
rm -Recurse -Force allure-results, allure-report
$env:JAVA_HOME = "C:\Program Files\Java\jre1.8.0_491"
pip install poetry 
pytest tests/ --alluredir=allure-results -q 
allure generate allure-results -o allure-report --clean
allure open allure-report 

# All tests
pytest

# API tests only (fast, no browser)
pytest -m api

# UI tests only
pytest -m ui

# Smoke suite (fastest subset)
pytest -m smoke

# Headed browser (useful for debugging UI tests)
HEADLESS=false pytest tests/ui

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test reports

allure generate allure-results -o allure-report --clean
allure open allure-report 

---

## Tooling Choices

| Tool | Reason |
|------|--------|
| **Python 3.11** | Required by spec; modern type hints (`float \| int`) |
| **Selenium 4** | Required by spec; modern API with relative locators and CDP support |
| **Pytest** | De facto standard for Python testing; fixture system is powerful and composable |
| **pytest-html** | Zero-config HTML reports; self-contained single file easy to share and attach to CI |
| **requests** | Required by spec; simple, battle-tested HTTP client for API tests |
| **webdriver-manager** | Eliminates chromedriver version management from setup instructions |

### Why no POM (Page Object Model)?

The Page Object Model introduces an extra indirection layer that rarely pays off on small-to-medium test suites. 
Instead, UI interaction is organised as pure helper functions in pages/, grouped by UI component (match list, bet slip, receipt modal). 
This means:

- Locators are visible at the call site — you never need to open a second file to understand a test
- Adding a new helper is one function, not a new class method
- Functions can be freely composed without inheritance chains

If the suite grew to 100+ tests across multiple features, the next step would be grouping helpers into modules per feature area — still no class hierarchy.
