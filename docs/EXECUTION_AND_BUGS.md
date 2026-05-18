# Test Execution Results & Bug Reports

**Executed against:** https://qae-assignment-tau.vercel.app/?user-id=candidate-N6pYw2Jk7A 
**Date:** 2025-05-07  
**Tester:** QA Engineer  
**Scope:** TC-001, TC-002, TC-003 + exploratory checks  

---

## Execution Summary

| ID     | Title                           | Result                          | Notes                                                                                |
|--------|---------------------------------|---------------------------------|--------------------------------------------------------------------------------------|
| TC-001 | Successful single bet placement | PARTIAL — see BUG-002           | BUG-001: Balance NOT UPDATED after successful bet placement, only updates after page |
| TC-002 | Stake boundary validation       | PARTIAL — see BUG-003 + BUG-004 | BUG-002 - Minimum Stake Requirement Inconsistency (€1.00 vs €1.01)                   |
| TC-002 | Stake boundary validation       | PARTIAL — see BUG-004           | Min boundary ambiguity confirmed as defect    |
| TC-003 | ****Stake cannot exceed b ****  | PARTIAL — see BUG-005           | **Insufficient balance not enforced at U  *** |

---

## TC-001 — Execution Notes (PASS)

**Steps executed:** Full happy path  
**Findings:**
- Match list loaded correctly with home/away teams, competition, and kickoff date
- Clicking an odds button populated the bet slip correctly
- Payout preview calculated as `stake × odds` — correct
- Place Bet button showed "Placing..." loading state as expected
- Receipt modal appeared with Bet ID, match details, stake, odds, payout, and timestamp
- Balance in header decreased by exactly the stake amount after placement
- Closing the receipt returned to main flow with bet slip cleared

**Result:** PASS — - BUG-002: Balance NOT UPDATED after successful bet placement, only updates after page 

---

### TC-002 — Stake boundary validation: minimum and maximum (PARTIAL PASS → BUG-003 + BUG-004)


| Stake Value | Expected: Result + Place Bet Button  | Actual: Result + Place Bet Button    | Expected Message                 | Actual Message             |
|-------------|--------------------------------------|--------------------------------------|----------------------------------|----------------------------|
| 0.99        | Rejected + Place Bet Button Disabled | Rejected + Place Bet Button Disabled | "Minimum stake is €1.00"         | Same as Expected           |
| 1.00        | **To Be Confirmed** - see Note       | Accepted + Place Bet Button Enabled  | Contradiction (Section 3 vs 4.1) | No error message           |  
| 1.01        | Accepted + Place Bet ButtonEnabled   | Accepted + Place Bet Button Enabled  | No error message                 | Same as Expected           |
| 100.00      | Accepted + Place Bet ButtonEnabled   | Accepted + Place Bet Button Enabled  | No error message                 | Same as Expected           |
| 100.01      | Rejected + Place Bet Button Disabled | Rejected + Place Bet Button Disabled | "Maximum stake is €100.00"       | Same as Expected           |
| 126         | Rejected + Place Bet Button Disabled | Rejected + Place Bet Button Disabled | "Insufficient balance"           | "Maximum stake is €100.00" |

> **Note:** The spec states both Section 3 (Business Rules) specifies minimum stake = €1.00, while Section 4.1 (Validation Rules) specifies €1.01. This test intentionally covers both values. The actual behavior should be documented and the specification clarified with the product team to fix this contradiction.
BUG-002 - Minimum Stake Requirement Inconsistency (€1.00 vs €1.01)
BUG-003 - Incorrect error message for stake exceeding available balance (€126 > €125.50)  - Expected: "Insufficient balance" vs Actual: "Maximum stake is €100.00" 

See screenshots:
Stake Value 0.99: Screenshot_Manual_TC-002-1_Stake_boundary_validation_minimum_and_maximum.png
Stake Value 1.00: Screenshot_Manual_TC-002-2_Stake_boundary_validation_minimum_and_maximum.png
Stake Value 1.01: Screenshot_Manual_TC-002-3_Stake_boundary_validation_minimum_and_maximum.png
Stake Value 100.00: Screenshot_Manual_TC-002-4_Stake_boundary_validation_minimum_and_maximum.png
Stake Value 100.01: Screenshot_Manual_TC-002-5_Stake_boundary_validation_minimum_and_maximum.png
Stake Value 100.01: Screenshot_Manual_TC-002-6_Stake_boundary_validation_minimum_and_maximum.png
---

## TC-003 — Execution Notes (PARTIAL PASS → BUG-002 + BUG-003)

**Steps executed:** Entered stake value exceeding current balance  
**Finding:** See BUG-002 — the UI does not block placement when stake exceeds balance. The API returns a 422 error, but the UI surfaces a generic error modal rather than the specific "Insufficient balance" message.

---

## Exploratory Testing Notes

The following areas were explored for 15–20 minutes beyond the scripted scenarios:

- **Decimal precision:** Entered `10.999` — UI appeared to accept it; API returned a 422. No clear UI-level rejection message for >2dp inputs. → See BUG-003
- **Empty stake field:** Clicking Place Bet with no stake shows validation message — working correctly
- **Remove All button:** Clears the bet slip correctly; no ghost selection remains
- **Per-selection X button:** Removes the selection; bet slip returns to empty state correctly
- **Rebet on error modal:** Retries placement — works correctly; does not create a duplicate bet
- **Close on error modal:** Clears selection and stake — works correctly
- **Date filter:** Filtering by a single day returns only matches on that date — correct
- **Match ordering:** Home team always displayed on the left — consistent with spec
- **Balance display consistency:** Header balance and bet slip balance are in sync — correct

---

## Bug Reports

---

### BUG-001 — Balance Reset Does Not Sync Correctly Between API and UI

**Severity:** Medium
**Area:** UI — Balance Display

**Description:** 
    After calling the `/api/reset-balance` endpoint, the API correctly returns the initial balance of **€125.50**, but the UI displays **€120.00** instead. 
    This creates a synchronization issue between backend and frontend.

**Reproduction Steps:**
1. Go to the API documentation: `https://qae-assignment-tau.vercel.app/api/docs`
2. Authorize using a valid `user-id`.
3. Execute `POST /api/reset-balance`.
4. Verify the response returns `balance: 125.50`.
5. Open the application using the same `user-id`: `https://qae-assignment-tau.vercel.app/?user-id=candidate-N6pYw2Jk7A`
6. Check the displayed balance in the UI.

**Expected Result**
| Step | Expected Result                                                                                      |
|------|------------------------------------------------------------------------------------------------------|
| 6    | Server returns status code **200 OK**                                                                |
| 7    | Response body contains: {"message": "Balance reset successfully","balance": 125.5,"currency": "EUR"} |
| 9    | UI displays balance as **€125.50**                                                                   |
| 10   | Balance in UI matches exactly with API response                                                      |

**Actual Result**
| Step | Expected Result                                                                                       |  Actual Result                     |
|------|-------------------------------------------------------------------------------------------------------|------------------------------------|
| 6    | Server returns status code **200 OK**                                                                 | Same as Expected                   | 
| 7    | Response body contains: {"message": "Balance reset successfully","balance": 125.5,"currency": "EUR"}  | Same as expected                   |
| 9    | UI displays balance as **€125.50**                                                                    | UI displays balance as **€120.00** |
| 10   | Balance in UI matches exactly with API response                                                       | UI does **not** match API          |
 
**Business Impact:**
    - Users see incorrect balance information after reset.
    - Risk of confusion when placing bets.
    - Breaks trust in the balance display.
    - Inconsistent behavior between API and UI layers.
    - Poor user experience

**Affected Components:**
    - UI Balance Display
    - Balance synchronization logic between API and UI

**Evidence:**
    - Screenshot_Manual_TC-001-6_Successful single_bet_placement_(happy path)_PAGE_API_BALANCE_UPDATES.png
    - The API response contains the correct updated balance ("balance": 110.00), but the UI does not consume or display it. 
    - This occurs after every successful bet placement.

**Related Tests:**
    - TC-001 — Successful single bet placement (happy path)
    - test_bet_all_odds_for_first_match (UI positive test)
    
**Potential Fix:**
Update the UI to extract the balance value from the API response and update the balance display component immediately after bet confirmation, without requiring a page reload.

---

### BUG-002 — Balance Does Not Update Automatically After Placing a Bet

**Severity:** High  
**Area:** UI — Balance Display & State Management

**Description:** 
    After successfully placing a bet, the user's balance in the header does not update automatically. 
    The updated balance is only reflected after manually refreshing the page.

**Reproduction Steps:**
1. Navigate to app with valid user-id  `https://qae-assignment-tau.vercel.app/?user-id=<your-user-id>`
2. Confirm match list loads with at least one upcoming match
3. Click the **1** (home win) odds button on the first upcoming match — note the odds value displayed
4. Confirm the bet slip on the right populates with: match name, selection "Home", the odds, and stake field
5. Enter `10.00` in the stake field
6. Confirm payout preview = `stake × odds` (e.g., €10 × 2.45 = €24.50)
7. Verify stake ≤ available balance (€10 < €120)
8. Click **Place Bet**
9. Confirm button changes to **Placing...** (loading state)
10. Confirm success receipt modal appears

**Expected Result**
- Bet is placed successfully and receipt modal is displayed with correct details.
- Balance in the header is **automatically updated** (decreased by the stake amount).
- After closing the receipt, the bet slip is cleared.

**Actual Result**
- Bet is placed successfully and receipt is shown.
- Balance in the header **does not update** after the bet is placed.
- Balance only updates after manually refreshing the page.

**Business Impact:**
- Users see outdated balance information after placing bets.
- Risk of users attempting to place bets with incorrect balance visibility.
- Poor and confusing user experience.

**Affected Components:**
- Frontend Balance Display
- UI State Management (after bet placement)

**Evidence:**
    - Screenshot_Manual_TC-001-6_Successful single_bet_placement_(happy path)_PAGE_API_BALANCE_UPDATES.png
    - The API response contains the correct updated balance ("balance": 110.00), but the UI does not consume or display it. 
    - This occurs after every successful bet placement.

**Related Tests:**
    - TC-001 — Successful single bet placement (happy path)
    - test_bet_all_odds_for_first_match (UI positive test)
    
**Potential Fix:**
Update the UI to extract the balance value from the API response and update the balance display component immediately after bet confirmation, without requiring a page reload.

**Notes:**
- This appears to be a frontend reactivity / state synchronization issue.
- Related to previous balance reset inconsistency (BUG-001).

---

### BUG-003 - Minimum Stake Requirement Inconsistency (€1.00 vs €1.01)

**Severity:** High  
**Area:** Stake Validation (UI + API) — Minimum Boundary

**Description:** 
-There is an inconsistency in the specification regarding the minimum stake:
- **Section 3 (Business Rules)** specifies minimum stake = **€1.00**
- **Section 4.1 (Stake Validation)** specifies minimum stake = **€1.01**
- The application currently accepts **€1.00** and allows the bet to be placed successfully. 
- The error message defined in the spec ("Minimum stake is €1.00") further conflicts with Section 4.1.

**Reproduction Steps:**
**Reproduction Steps:**
1. Navigate to the application with a valid `user-id`.
2. Click on any odds button for an upcoming match to open the bet slip.
3. Test the following stake values one by one:
   - Enter `1.00` → Observe validation message and **Place Bet** button state
   - Clear the field
   - Enter `1.01` → Observe validation message and **Place Bet** button state

**Expected Result**
| Stake Value | Expected Result              | Place Bet Button               | Expected Message                  |
|-------------|------------------------------|--------------------------------|-----------------------------------|
| 1.00        | **To Be Confirmed**          | Depends on final spec decision | Depends on final spec decision    |
| 1.01        | Accepted                     | Enabled                        | No error message                  |

**Actual Result**
| Stake Value | Actual Result                | Place Bet Button     | Actual Message      |
|-------------|------------------------------|----------------------|---------------------|
| 1.00        | Accepted                     | Enabled              | No error message    |
| 1.01        | Accepted                     | Enabled              | No error message    |


**Business Impact:**  
- Creates confusion for testing and development teams due to conflicting requirements.
- Potential regulatory compliance risk if the intended minimum is €1.01.
- Platform may be accepting bets below the intended minimum threshold.
- No single source of truth for minimum stake validation.

**Affected Components:**
- UI Stake Validation Logic
- Bet Placement Flow
- Error Messaging

**Evidence:**
- Stake Value 1.00: Screenshot_Manual_TC-002-2_Stake_boundary_validation_minimum_and_maximum.png
- Stake Value 1.01: Screenshot_Manual_TC-002-3_Stake_boundary_validation_minimum_and_maximum.png
- API accepts €1.00 successfully with an incorrect currency returned: USD

**Related Tests:**
TC-002 — Stake boundary validation: minimum and maximum
test_stake_validation_business_rules(api, valid_match_id, stake, expected_status, description)

**Potential Fix:**
- Product Owner / Business Analyst should clarify and unify the minimum stake requirement across all sections of the specification and update the implementation + error messages accordingly.

---

### BUG-004 - Incorrect error message shown when stake exceeds available balance
stake exceeding available balance (€126 > €125.50)  - Expected: "Insufficient balance" vs Actual: "Maximum stake is €100.00" 
 
**Severity:** High  
**Area:** Stake Validation —  Balance Check vs Maximum Stake Check

**Description:** 
When a user enters a stake of €126 (which exceeds both the €100.00 maximum stake limit AND the €125.50 starting balance), 
the UI correctly blocks the bet but displays the wrong error message. 
The UI shows "Maximum stake is €100.00" — which is technically true but misleading, because the more financially significant violation is that the stake exceeds the user's available balance.

The two rules being violated simultaneously are:
| Rule                  | Limit    | Violation   | 
|-----------------------|----------|-------------| 
| Maximum stake         | €100.00  | €126 > €100 |  
| Insufficient balance  | €125.50  | €126 > €100 |  


**Reproduction Steps:**
1. Navigate to `https://qae-assignment-tau.vercel.app/?user-id=candidate-N6pYw2Jk7A`
2. Confirm match list loads with at least one upcoming match
3. Click the any odds button on any upcoming match — note the odds value displayed
4. Test each stake value below **one by one** following these steps:
   a. Enter the stake amount
   b. Confirm payout preview = `stake × odds` (e.g., €10 × 2.45 = €24.50)
   c. Observe the validation message (if any) and the state of the **Place Bet** button (green-enabled OR grey-disabled)
   d. Verify the **Place Bet** button behaviour against the error message 
   - After each test step, clear the stake field before entering the next value.
| Stake Value | Expected: Result + Place Bet Button  | Expected Message / Behavior         |
|-------------|--------------------------------------|-------------------------------------|
| 126         | Rejected + Place Bet Button Disabled | "Insufficient balance"              |

**Expected Result:**  
When a stake exceeds the available balance, the error message "Insufficient balance" is shown and the Place Bet button is disabled.
| Stake Value | Expected: Result + Place Bet Button  | Actual: Result + Place Bet Button    | Expected Message                 | Actual Message             |
|-------------|--------------------------------------|--------------------------------------|----------------------------------|----------------------------|
| 126         | Rejected + Place Bet Button Disabled | Rejected + Place Bet Button Disabled | "Insufficient balance"           | "Maximum stake is €100.00" |

**Actual Result:**  
The UI displays "Maximum stake is €100.00" and disables the Place Bet button — even when the balance is the binding constraint.
| Stake Value | Expected: Result + Place Bet Button  | Actual: Result + Place Bet Button    | Expected Message                 | Actual Message             |
|-------------|--------------------------------------|--------------------------------------|----------------------------------|----------------------------|
| 126         | Rejected + Place Bet Button Disabled | Rejected + Place Bet Button Disabled | "Insufficient balance"           | "Maximum stake is €100.00" |

**Business Impact:**  
- Users see an irrelevant error message ("Maximum stake is €100.00") when their actual problem is insufficient funds, leading to confusion and frustration.
- Increased support tickets as users question why they cannot place smaller bets (e.g., €110) despite having a €125.50 balance.
- Potential revenue loss from users who abandon the platform assuming it is broken, rather than checking their balance or depositing more funds.

**Evidence:**  
Screenshot_Manual_TC-002-6_Stake_boundary_validation_minimum_and_maximum.png

**Related Tests:**
TC-002 — Stake boundary validation: minimum and maximum
test_stake_validation_business_rules(api, valid_match_id, stake, expected_status, description)

**Potential Fix:**
Evaluate balance check before or alongside max stake check: 
If both rules are violated → show "Insufficient balance"
If only max stake is violated → show "Maximum stake is €100.00"

---

### BUG-005 — Odds filter returns matches outside filter range
 
**Severity:** Medium  
**Area:** Odds filter 

**Description:**  
The Odds filter supports min/max range (inclusive) and must reject invalid ranges with clear feedback.

**Reproduction Steps:**
1. Open the Odds filter  
2. Enter an invalid odds range where the minimum value is greater than the maximum value  
   - Example: Min Odds = `5.00`  
   - Max Odds = `1.50`  
3. Apply the filter  
4. Observe the system behaviour and validation feedback  
5. Enter a valid odds range  
   - Example: Min Odds = `1.50`  
   - Max Odds = `5.00`  
6. Apply the filter  
7. Verify that only matches with odds within the selected range are displayed  
8. Reset the filter 

**Expected Result:**
- When an invalid odds range is entered:
  - The system prevents invalid filter application, automatically corrects the range, or displays a clear validation message to the user  
  - The application does not crash or fail silently  
  - The match list remains unchanged until a valid range is provided  
- When a valid odds range is applied:
  - The match list is filtered correctly  
  - All displayed odds fall within the selected range inclusive  
- Resetting the filter:
  - Clears all selected odds values  
  - Restores the full unfiltered match list  


**Actual Result:**  
- When an invalid date range is selected:
  - The system does not prevents invalid filter application
  - The application does not display any matches  
  - There is no error message displayed for the incorrect range
- When a valid date range is applied:
  - The match list is filtered incorrectly  
  - All displayed matches do not fall within the selected date range inclusive  
- Resetting the filter:
  - Clears all selected odds values and resets odds to default odds range
  - Restores the full unfiltered match list  

**Business Impact:**  
- Incorrect odds filtering may confuse users and reduce trust in the platform, as matches outside the selected range are displayed. 
- While core betting functionality remains unaffected, the issue negatively impacts usability, user experience, and confidence in the filtering feature.
- Although the issue does not block core betting functionality, it can reduce user confidence, increase frustration, and potentially decrease user engagement with advanced filtering features.

**Evidence:**  
- No error message: Screenshot_Manual_TC-003_2_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_4_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_5_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_7_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_8_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_9_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_10_Odds filter_invalid_range_is_rejected_with_clear_feedback.png
- Odds filter returns matches outside filter range: Screenshot_Manual_TC-003_11_Odds filter_invalid_range_is_rejected_with_clear_feedback.png

**Related Tests:**
TC-003 — Odds filter: invalid range is rejected with clear feedback

**Potential Fix:**
- The filter should validate the odds range in real time as the user types (on input change) and prevent applying the filter if the range is invalid (i.e. min > max).
- When an invalid range is detected, the system should:
  - Disable the Apply button to prevent submission
  - Display a clear, user-friendly inline error message (not a pop-up unless necessary), such as "Minimum odds cannot be greater than maximum odds"
  - Optionally highlight the offending field(s) in red
- Once the user corrects the range (min ≤ max), the error message should disappear, and the Apply button should be re-enabled.

