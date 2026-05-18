# Test Plan — Single Bet Placement Feature

**Application:** Sports Betting QA — https://qae-assignment-tau.vercel.app/  
**Feature:** Single Bet Placement  
**Scope:** Match list display, bet slip interaction, bet placement, receipt modal, stake validation  
**Out of scope:** Live betting, accumulators, mobile UX, other sports

---

## Overview
This test plan covers critical risk areas for the single bet placement flow on the sports betting web application.

---

## Scenarios

---

### TC-001 — Successful single bet placement (happy path)

**Priority:** Critical  
**Risk Rationale:**  
This is the core revenue-generating action on the platform. 
If a user cannot complete a valid bet end-to-end, the entire feature fails its business purpose. 
Any regression here is a P0 incident. 
It also validates the most complex integration point: UI → API → balance update → receipt modal.

**Preconditions:**  
- Valid user-id in query param  
- Balance ≥ stake (starting balance €125.50)  

**Steps:**
1. Navigate to app with valid user-id  `https://qae-assignment-tau.vercel.app/?user-id=candidate-N6pYw2Jk7A`
2. Confirm match list loads with at least one upcoming match
3. Click the **1** (home win) odds button on the first upcoming match — note the odds value displayed
4. Confirm the bet slip on the right populates with: match name, selection "Home", the odds, and stake field
5. Enter `10.00` in the stake field
6. Confirm payout preview = `stake × odds` (e.g., €10 × 2.45 = €24.50)
7. Verify stake ≤ available balance 
8. Click **Place Bet**
9. Confirm button changes to **Placing...** (loading state)
10. Confirm success receipt modal appears

**Expected Result:**
- Receipt modal shows: Bet ID (non-empty string), correct match name, selection "HOME", stake €10.00, correct odds, payout = stake × odds and a valid placement timestamp
- Balance in header decreases by exactly €10.00 
- Closing the receipt clears the bet slip (no active selection)

---

### TC-002 — Stake boundary validation: minimum and maximum

**Priority:** Critical  
**Risk Rationale:**  
Stake limit enforcement is a critical financial and regulatory control. 
Incorrect implementation of minimum (€1.00 / €1.01) or maximum (€100.00) stake rules can lead to:
- Regulatory violations (if minimum stake is too low)
- Excessive financial risk exposure for the operator (if maximum stake is not enforced)
- Poor user experience and potential disputes
This is one of the most commonly broken areas in betting platforms, especially around boundary values (e.g. €1.00 vs €1.01) and edge cases like €100.01 or stakes exceeding available balance.

**Preconditions:**  
- Valid user-id in query param  
- Balance ≥ stake (starting balance €125.50)   
- Upcoming match is available 


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
| 0.99        | Rejected + Place Bet Button Disabled | "Minimum stake is €1.00"            |
| 1.00        | **To Be Confirmed** - see Note       | Contradiction (Section 3 vs 4.1)    |  
| 1.01        | Accepted + Place Bet Button Enabled  | No error message                    |
| 100.00      | Accepted + Place Bet Button Enabled  | No error message                    |
| 100.01      | Rejected + Place Bet Button Disabled | "Maximum stake is €100.00"          |
| 126         | Rejected + Place Bet Button Disabled | "Insufficient balance"              |


> **Note:** The spec states both Section 3 (Business Rules) specifies minimum stake = €1.00, while Section 4.1 (Validation Rules) specifies €1.01. This test intentionally covers both values. The actual behavior should be documented and the specification clarified with the product team.

---

### TC-003 — Odds filter: invalid range is rejected with clear feedback

**Priority:** Medium  
**Risk Rationale:**  
- The odds filter is a key UX affordance for experienced bettors looking to narrow down selections efficiently. 
- An invalid odds range (e.g., min > max) that either silently returns no results or causes the filter to crash leaves users confused and unable to identify value bets. 
- While this issue is lower priority than core bet placement, it remains important for usability, data integrity, and maintaining a polished user experience.

**Preconditions:**  
- Match list is loaded and visible
- At least multiple matches with varying odds are present

**Steps:**
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

---

### TC-004 — Date filter: invalid range is rejected with clear feedback

**Priority:** Medium  
**Risk Rationale:**  
The filter is a key UX affordance for experienced bettors narrowing their selection. 
An invalid date range that either silently returns no results or crashes the filter leaves the user confused and unable to find value bets. 
This is lower priority than core bet placement but important for usability and data integrity.

**Preconditions:**  
- Match list is loaded and visible  
- Multiple matches across different dates are available

**Steps:** 
1. Open the date filter  
2. Select an invalid date range where the start date is later than the end date  
   - Example: Start Date = `30 August 2026`  
   - End Date = `1 August 2026`  
3. Apply the filter  
4. Observe the system behaviour and validation feedback  
5. Select a valid date range  
   - Example: Start Date = `1 August 2026`  
   - End Date = `30 August 2026`  
6. Apply the filter  
7. Verify that only matches within the selected date range are displayed  
8. Reset the filter  

**Expected Result:**
- When an invalid date range is selected:
  - The system prevents invalid filter application, automatically corrects the range, or displays clear validation feedback to the user  
  - The application does not crash or fail silently  
- When a valid date range is applied:
  - The match list is filtered correctly  
  - All displayed matches fall within the selected date range inclusive  
- Resetting the filter:
  - Clears all selected date values  
  - Restores the full unfiltered match list  

---

### TC-005 — Bet slip: selecting a new outcome replaces the previous selection

**Priority:** High  
**Risk Rationale:**  
The spec explicitly states only one active selection is permitted at a time. If a second selection is added rather than replacing the first, the user could believe they have placed one bet while actually having a different one on the slip — a significant trust and financial risk. This is a common bug in single-to-accumulator migration scenarios.

**Preconditions:**  
- At least two matches visible, or at least two odds buttons on one match

**Steps:**
1. Click the **1** (home win) odds button on Match A — note the selection in the bet slip
2. Click the **X** (draw) odds button on the same Match A
3. Confirm the bet slip now shows only the Draw selection (not both)
4. Click the **2** (away win) odds button on Match B (different match)
5. Confirm the bet slip now shows only Match B / Away selection
6. Confirm only one item in the bet slip at all times

**Expected Result:**
- Each new selection replaces the previous one in the bet slip
- The bet slip never shows more than one active selection
- The odds value in the bet slip matches the most recently clicked button

---

### TC-005 — Stake cannot exceed available balance

**Priority:** Critical  
**Risk Rationale:**  
Allowing a bet that exceeds the user's balance would mean the platform accepts bets it cannot honour, creating a financial integrity risk. This is both a legal requirement and a trust issue — users expect the system to prevent overspending.

**Preconditions:**  
- User balance is known (e.g., €125.50 initially, or after reset)  
- Match selected with bet slip populated

**Steps:**
1. Note the current balance (e.g., €125.50)
2. Enter a stake equal to `balance + 0.01` (e.g., `125.51`)
3. Attempt to click **Place Bet**
4. Observe feedback
5. Enter a stake exactly equal to the balance (e.g., `125.50`) — note: this exceeds €100.00 max so it should be rejected by max-stake rule first
6. Reset balance via `POST /api/reset-balance` if needed
7. Enter `125.51` and confirm rejection

**Expected Result:**
- Stake > balance: blocked with message "Insufficient balance"
- The correct rule fires in the correct order (max stake check before balance check, or vice versa — confirm the priority)

---


### TC-006 — Odds filter: invalid range is rejected with clear feedback

**Priority:** Medium  
**Risk Rationale:**  
The filter is a key UX affordance for experienced bettors narrowing their selection. An invalid range that either silently returns no results or crashes the filter leaves the user confused and unable to find value bets. This is lower priority than core bet placement but important for usability and data integrity.

**Preconditions:**  
- Match list visible with multiple matches at varying odds

**Steps:**
1. Open the Odds filter
2. Enter a **min** value greater than the **max** value (e.g., min: `5.00`, max: `1.50`)
3. Apply the filter
4. Observe the feedback
5. Enter a valid range (e.g., min: `1.50`, max: `5.00`)
6. Apply the filter
7. Confirm only matches with odds within that range are displayed

**Expected Result:**
- Invalid range (min > max): clear error message displayed, no results broken
- Valid range: match list is filtered correctly; all displayed odds fall within [min, max] inclusive
- Removing/resetting the filter restores the full match list
