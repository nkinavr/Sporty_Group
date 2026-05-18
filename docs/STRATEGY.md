# Strategy & Recommendations

## Why These 2 Tests Were Selected for Automation

### Test 1 — E2E UI: Negative Bet Amounts Validation (All Odds, First Match)
**Rationale:**

Stake validation is a legal and financial control that directly impacts revenue. The platform defines precise boundaries (minimum €1.01, maximum €100.00, balance check). Testing these boundaries at the UI layer ensures that users receive immediate, correct feedback before attempting to place invalid bets.

This test was chosen over API-only validation because:

**1.User-facing errors must be visible and clear** — The stakeWarning element, error styling on input, and disabled Place Bet button are user experience elements that API tests cannot verify
**2.Revenue protection requires frontend guardrails** — Users should not reach the API with invalid stakes; the UI must prevent this at point of entry
**3.BUG-001 (€1.00 being accepted)** was discovered precisely because UI validation was missing or incorrect — this test makes that bug impossible to miss in future regression

**Why test all 3 odds (1, X, 2) on the first match:**

Stake validation logic should be **identical regardless of which outcome the user bets on**. 
By testing all three odds in a single test:

1.We verify the validation logic is consistently applied across all bet types
2.We catch asymmetry bugs where minimum stake works for HomeWin but not Draw/AwayWin
3.Execution remains efficient (3 iterations vs 3 separate test methods)

**Why negative cases are worth the UI test cost:**

Negative UI tests are often more valuable than positive ones for revenue-critical rules because:

**1.Invalid stakes should never reach the API** — UI must block them first
**2.Error messages must be accurate** — Wrong error message ("Insufficient balance" instead of "Below minimum") confuses users and creates support tickets
**3.The €1.00 edge case** revealed that the boundary implementation was flawed — only UI testing exposed this because the API might have had different validation logic

The test takes screenshots at each step, providing visual evidence of validation failures for bug reports and compliance audits.

### Test 2 — E2E UI: Positive Bet Placement (Happy Path - All Odds)
**Rationale:**

The complete bet placement flow is the only revenue-generating action in this application. 
Automating it provides three critical safeguards:

**1.Regression guard across the entire integration surface** (UI → API → balance deduction → receipt display)
**2.Contract validation** — The receipt must reflect exactly what was shown at selection time (odds, stake, potential payout)
**3.Balance consistency check** — After placing 3 valid bets (€1.01, €15, €100), the balance must be correctly reduced

**Why the happy path over more negative cases for the E2E slot**:

E2E UI tests are expensive to maintain and run (Selenium overhead, wait times, screenshots). 
The happy path delivers the **highest value per maintenance cost because:**

1.It validates that real money movement works correctly (€116.01 total staked across 3 bets)
2.It confirms the receipt modal renders with correct data — the user's confirmation of the transaction
3.One failure here blocks all revenue — if this breaks, the platform cannot generate money
4.Negative UI cases (except stake validation) are better covered by faster API tests or can use fault injection

**Why test all 3 odds (1, X, 2) on the first match with different stakes:**

This design decision tests three distinct scenarios in one efficient test:

**1.€1.01** — Minimum valid stake (boundary testing)
**2.€15** — Mid-range stake (typical user behavior)
**3.€100** — Maximum valid stake (boundary testing)

Testing all three odds ensures consistency across all bet types. If the HomeWin bet works but Draw fails, the bug is caught immediately. Each bet type runs exactly once (tracked via placed_bet_types set), preventing duplicate execution that would waste test time.

**Why include a balance reset API call before the test:**

The test calls /reset-balance via API before starting to guarantee a known clean state (€125.50 balance even though the balance resets to €120 in the screenshot). 
This eliminates flakiness from previous test runs and ensures the €100 maximum bet can be placed without balance insufficiency errors.

**Why screenshots are captured:**

Each test creates a timestamped screenshot directory, capturing:

1.Bet placement steps (odd selection, stake entry, confirmation)
2.Receipt display
3.Balance updates

These screenshots serve as auditable evidence for compliance and make debugging failures trivial — you see exactly where the flow broke.

**Why These 2 Tests Together Form a Complete Revenue Assurance Suite**
| Test                    | Layer                      | What It Protects             | Failure Impact                                                         |
|-------------------------|----------------------------|------------------------------|------------------------------------------------------------------------|
| **Negative Validation** | UI Frontend                | Users placing invalid stakes | Revenue loss from below-minimum bets, user confusion from wrong errors |
| **Positive Happy Path** | Full Stack (UI → API → DB) | Complete betting flow        | Complete revenue blockage if broken                                    |

**They are complementary, not redundant:**

1.The negative test ensures prevention (bad stakes blocked)
2.The positive test ensures execution (good stakes work)
3.API tests (elsewhere in suite) catch backend-only issues, but these UI tests verify what users actually experience

**Why UI Tests Strictly Automate Upcoming Matches to Avoid Revenue Loss**
**The Core Problem: Stale Matches Create False Positives**
If UI tests automate **past matches** (already finished) or **non-bettable matches**, they would:

1.Fail incorrectly — Odds buttons may be disabled, place bet API may reject with 410 Gone
2.Generate false revenue loss alarms — Tests would fail even when the platform is working correctly
3.Waste debugging time — Engineers investigate test failures that are not real bugs
4.Erode trust in automation — Teams ignore test results when flaky failures become common

**The Solution: Date-Based Match Filtering**
The "extract_upcoming_matches()" method implements **strict date filtering** to only include matches where parsed_date > today.

**Why Not Automate Other Scenarios in UI?**
| Scenario                              | Why Not Automated in UI                          | Where It Is Covered                     |
|---------------------------------------|--------------------------------------------------|-----------------------------------------|
| Error modal on API timeout            | Requires fault injection (fragile in Selenium)   | Manual exploratory testing              |
| Match odds updating in real-time      | Highly dynamic, changes per second               | API contract tests                      |
| Multiple bet slip management          | Complex state, high maintenance                  | Manual regression suite                 |
| Different matches beyond first        | Assumed consistent across matches                | Smoke test on match selection only      |


The principle: **Automate the 20% of flows that generate 80% of revenue risk**. 
These two tests represent that 20%.

Summary Statement
*"These two UI tests were selected because they directly guard the revenue-generating path of the application. The negative test validates that stake boundaries (€1.01 minimum, €100.00 maximum, balance check) are enforced with correct user-facing error messages, preventing invalid bets from ever reaching the API. The positive test verifies that valid bets (minimum, mid-range, and maximum stakes across all three odds) successfully complete end-to-end, deducting the correct amount from balance and displaying an accurate receipt. Together, they provide regression assurance for the platform's core financial transaction in under 2 minutes of execution time, with screenshots providing audit evidence for compliance."*

---

### Test 2 — API: Stake Validation Business Rules

**Why These 2 API Tests Were Selected for Automation**

**Test 1 — Valid Stake Acceptance & Response Integrity (test_valid_stake_is_accepted)**
**Rationale:**

This parametrized test validates that legitimate, revenue-generating bets are correctly processed by the API. 
It covers three critical boundaries: minimum valid stake (€1.01), mid-range stake (€50.00), and maximum valid stake (€100.00). 
For each valid stake, it performs six essential checks:

1.HTTP 200 response — The API accepted the bet
2.Required response fields — message, matchId, selection, stake, odds, payout, balance, currency (spec section 5.3)
3.Payout calculation — payout = stake × odds (financial accuracy)
4.Stake preservation — Returned stake matches what was sent
5.Balance deduction — new_balance = initial_balance - stake (revenue movement)
6.Currency format — Must be "EUR" (though BUG-005 currently returns "USD")

**Why this test is high-value for revenue:**

1.Direct revenue validation — If this test fails, users cannot place valid bets, meaning the platform cannot generate money
2.Payout calculation errors would cause immediate financial disputes and chargebacks
3.Balance deduction errors would allow users to bet without spending money (infinite betting exploit) or deduct incorrect amounts (revenue leakage)
4.The parametrized design tests all three revenue-critical boundaries (minimum, typical, maximum) in a single test, minimizing maintenance while maximizing coverage

**Why API over UI for this validation:

1.Payout and balance calculations are mathematical operations best verified at the API layer without UI rendering overhead
2.The required fields contract (8 fields per spec) is deterministic and easily asserted in JSON responses
3.API tests execute in milliseconds vs seconds for UI, enabling this test to run on every commit

**Known defect handling:** BUG-005 (currency returns "USD" instead of "EUR") is marked with pytest.xfail so the test suite stays green while the defect is tracked. When fixed, the assertion activates automatically.

**Test 2 — Balance Enforcement (test_stake_exceeding_balance_returns_422)**
**Rationale:**

This test validates that users cannot bet more money than they have. 
It depletes the balance with two €50 bets (leaving ~€25.50), then attempts a €30 bet that should be rejected with HTTP 422.

**Why this test is high-value for revenue:**

1.Prevents debt creation — If users can bet beyond their balance, the platform creates uncollectable debt
2.Stops "free betting" exploits — Without balance enforcement, users could chain bets indefinitely using money they don't have
3.Financial integrity — This is a critical accounting control; its absence would make the platform insolvent

**Why this is the highest-value negative API test:**
Defect Impact          | Without This Test                                            | With This Test            |
|------------------------|------------------------------------------------------------|---------------------------|
| **Revenue Leakage**    | Users place €100 bets with €25 balance → platform owes €75 | Caught before deployment  |
| **Exploit Discovery**  | Found in production by malicious users                     | Found in CI/CD pipeline   |
| **Legal Compliance**   | Violates gambling regulations on user funds                | Compliance enforced       |

**Why BUG-002 is marked xfail with strict=True:**

1.The test currently fails because the API accepts bets exceeding balance (BUG-002). By marking it xfail(strict=True):
2.The test suite remains green while the defect is being fixed
3.The failure is explicitly documented in test output
4.When the bug is fixed, the test will automatically start passing (no code change needed)
5.A passing test after fix confirms the balance enforcement works correctly

**Why API over UI for balance enforcement:**

1.Balance state is server-managed; testing at the API layer directly verifies the source of truth
2.Multiple bet sequences (deplete → exceed) are faster and more reliable without UI navigation
3.UI could block via frontend validation, but API must enforce regardless — API test catches backend-only regressions

**Why These 2 API Tests Together Form a Revenue Integrity Suite:**

| Test                       | What It Validates                                   | Revenue Impact If Broken                     |
|----------------------------|-----------------------------------------------------|----------------------------------------------|
| **Valid Stake Acceptance** | Correct processing of legitimate bets               | Platform cannot generate revenue             |
| **Balance Enforcement**    | Users cannot exceed available funds                 | Platform creates uncollectable debt          |

**They test opposite sides of the same financial coin:**
These tests are critical because they directly protect the **financial integrity** and **revenue generation** of the betting platform. 

**Valid Stake Acceptance** ensures the system can process legitimate bets correctly, directly enabling revenue generation.
**Balance Enforcement** prevents users from betting money they don’t have, protecting the platform from financial loss and bad debt.

Comparison: API vs UI Coverage for Revenue Logic

| Business Rule              | UI Test          | API Test             | Why Both?                                     |
|----------------------------|------------------|----------------------|-----------------------------------------------|
| Minimum stake (€1.01)      | Negative test    | Valid stakes test    | UI for UX, API for backend enforcement        |
| Maximum stake (€100.00)    | Negative test    | Valid stakes test    | UI for UX, API for backend enforcement        |
| Balance deduction          | Not tested       | Valid stakes test    | API is source of truth for balance            |
| Exceeding balance          | Not tested       | Balance enforcement  | Only API can test server-side enforcement     |
| Payout calculation         | Not tested       | Valid stakes test    | Mathematical accuracy at source               |
| Required response fields   | N/A              | Valid stakes test    | API contract compliance                       |


**Summary Statement**
*"These two API tests were selected because they directly protect the platform's revenue integrity at the server layer. The first test (test_valid_stake_is_accepted) validates that legitimate bets (minimum, mid-range, and maximum stakes) are correctly processed — confirming payout calculations, balance deductions, and response contracts. The second test (test_stake_exceeding_balance_returns_422) validates that users cannot bet more than their available balance — a critical financial control that prevents debt creation and ensures regulatory compliance. Together, they provide revenue assurance that complements the UI tests: UI tests verify user-facing validation and flow completion, while API tests verify the backend mathematical and financial integrity that UI cannot access. Both tests execute in under 500ms, enabling them to run on every pull request and catch revenue-critical regressions before they reach production."*
---

## What Was Intentionally Left as Manual Only

### 1. Error modal interactions (Rebet / Close / X button behaviour)
Reliably triggering the error modal requires either: 
(a) fault injection at the network or API level, 
(b) a controlled test environment where the API can be forced to return a 500. Neither is available here. Testing this manually during sprint ceremonies or with a mock-enabled local environment is the right approach. The behavioural spec is clear enough for a skilled manual tester to verify quickly.

### 2. Odds filter — visual and UX validation
The odds filter involves drag handles, range inputs, and dynamic list filtering. The business logic (inclusive min/max, invalid range rejection) can be tested manually in minutes. Automating it with Selenium's action chains on range sliders is fragile, version-sensitive, and high-maintenance relative to the value. Recommend leaving this manual until a component-test framework (e.g., Playwright component tests, Storybook) is available.

### 3. Date filter — date range selection
Same reasoning as the odds filter. Date range pickers require complex interaction simulation that breaks across browser updates. Manual verification per sprint is appropriate at the current scale.

### 4. Receipt data integrity — full field-by-field comparison
TC-005 (receipt data integrity) is partially covered by the E2E test (stake and payout presence). A full field-by-field comparison (Bet ID format, timestamp plausibility, match name matching) requires reliable receipt data parsing. The current receipt modal structure is not annotated with `data-testid` attributes, making reliable parsing brittle. This is flagged as a **spec clarification item** (see recommendations below) — once test IDs are added, this should be automated.

### 5. Balance consistency across sessions
Verifying that balance persists correctly across page reloads and between the header and bet slip is a quick manual check (2 minutes per sprint). Not worth the Selenium overhead.

---

## Top 3 Recommendations if This Project Scales

### 1. Add a bets-placed section where you are able to see current bets placed.

This is the single highest-leverage change for automation quality. Right now, tests use class names and text content to find elements — both of which change during UI refactors. 
**Recommendation:** A `data-testid` on the stake input, Place Bet button, receipt modal, balance display, and each odds button would:
- Cut test maintenance cost by ~60%
- Make tests resilient to visual redesigns
- Enable reliable receipt data assertions (resolving the TC-005 gap above)

This is a 1-2 hour engineering task that pays for itself on the first UI refactor.

---

### 2. Real Time Balance Update 

If you do not refresh the browser, the balance stays the same and only after refreshing the browser you get to see the actual balance
**Recommendation:** After every bet placed, the balance must be update on the Front end in real-time

### 3. Clarify and resolve the minimum stake ambiguity (BUG-001) as a spec process change

The discrepancy between "Stake min €1.00" in the business rules table and "Stake min €1.01" in the validation table is a symptom of a process gap: validation rules and business rules were written by different people at different times without a reconciliation step.

**Recommendation:** Establish a single table of business rules that is the canonical reference for both engineering and QA. 
Every validation rule should have: a value, an error message, the owning layer (UI, API, or both), and a test case ID. When spec and implementation diverge, the test case fails — not the spec.

For this specific case: agree on one value (likely €1.01 given the validation table was written later), update the spec, update the error copy to "Minimum stake is €1.01", and add it to the API parametrized test.
