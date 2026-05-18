1. The product team to clarify the correct minimum stake value

The feature spec states the minimum stake is €1.01 (validation rules table, section 4.1). 
However, the UI accepts a stake of exactly €1.00 and allows the bet to be placed successfully. 
The error copy in section 4.4 reads "Minimum stake is €1.00" which contradicts the €1.01 value in the validation table, suggesting an unresolved ambiguity between the product and engineering teams that has resulted in inconsistent implementation.

Real-world Common Practice - Many betting platforms use €1.00 as minimum.
But some strict platforms especially regulated ones use €1.01 to avoid 1.00 odds edge cases.

2. Real-time Balance Updates after successful bet placement
Balance NOT UPDATED after successful bet placement, only updates after page

3. Alignment of UI and API
a. POST /api/reset-balance does not reset user's balance to initial configured value of EUR125.50 in the UI while API returns the correct initial configured value =
b. Real-time balance updates
SEE:
    1. Screenshot_Manual_TC-001-5_Successful single_bet_placement_(happy path)_PAGE_REFRESH_BALANCE_UPDATES.png
    2. Screenshot_Manual_TC-001-6_Successful single_bet_placement_(happy path)_PAGE_API_BALANCE_UPDATES.png
b.  Error message: Stake exceeds available balance (e.g. 126) 
Expected: Insufficient balance
Actual: Stake must be at most 100.00.
See BUG-002 — Balance Does Not Update Automatically After Placing a Bet

4. 
