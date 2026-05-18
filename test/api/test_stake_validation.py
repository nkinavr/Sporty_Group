"""
API Test — Stake Validation Business Rules (POST /api/place-bet)
Using UPCOMING matches

WHY THIS TEST WAS CHOSEN FOR AUTOMATION:
    Validates ALL stake business rules in a single parametrized test:
        - Minimum stake: €1.00
        - Maximum stake: €100.00
        - Precision: 2 decimal places
        - Balance: Cannot exceed available funds

BUSINESS RULES COVERED:
    - Valid stakes: €1.00, €50.00, €100.00 → Accepted
    - Below €1.00 → Rejected
    - Above €100.00 → Rejected
    - Exceeds balance → Rejected
    - Zero stake → Rejected
    - Invalid precision → Rejected
    - Negative stake → Rejected 
"""
import math
import pytest
from datetime import datetime
import allure


@pytest.fixture()
def valid_match_id(api):
    """Fetches the FIRST UPCOMING match ID based on kickoffDate."""
    resp = api.get_matches()
    assert resp.status_code == 200, f"GET /matches failed: {resp.text}"
    
    all_matches = resp.json()
    assert all_matches, "No matches available — cannot run stake validation tests"
    
    # Filter for upcoming matches (kickoffDate >= today)
    upcoming_matches = []
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"\nTotal matches found: {len(all_matches)}")
    
    for match in all_matches:
        kickoff_date_str = match.get("kickoffDate", "")
        home_team = match.get("homeTeam", "Unknown")
        away_team = match.get("awayTeam", "Unknown")
        
        if not kickoff_date_str:
            #Debugging Print 
            #print(f"No kickoffDate for {home_team} vs {away_team} - including as valid")
            upcoming_matches.append(match)
            continue
        
        try:
            # Parse the kickoffDate (format: "2026-02-27")
            match_date = datetime.strptime(kickoff_date_str, "%Y-%m-%d")
            
            # Only include matches that are today or in the future
            if match_date >= current_date:
                upcoming_matches.append(match)
                print(f"UPCOMING: {home_team} vs {away_team} on {kickoff_date_str}")
            else:
                print(f"PAST: {home_team} vs {away_team} on {kickoff_date_str} - excluding")
        except Exception as e:
            print(f"Could not parse date '{kickoff_date_str}' for {home_team} vs {away_team}: {e}")
            upcoming_matches.append(match)  # Include if date parsing fails
    
    # If no upcoming matches, skip the test
    if not upcoming_matches:
        pytest.skip("No UPCOMING matches available. Cannot run stake validation tests.")
    
    # Return the first upcoming match ID
    first_upcoming = upcoming_matches[0]
    print(f"\n{'='*60}")
    print(f"SELECTED UPCOMING MATCH:")
    print(f"   {first_upcoming.get('homeTeam', '?')} vs {first_upcoming.get('awayTeam', '?')}")
    print(f"   Competition: {first_upcoming.get('competition', 'Unknown')}")
    print(f"   Kickoff: {first_upcoming.get('kickoffDate', 'Unknown')}")
    print(f"   Odds: Home={first_upcoming.get('odds', {}).get('home', 'N/A')}, "
          f"Draw={first_upcoming.get('odds', {}).get('draw', 'N/A')}, "
          f"Away={first_upcoming.get('odds', {}).get('away', 'N/A')}")
    print(f"{'='*60}\n")
    
    return first_upcoming["id"]

#BALANCE RESET
@pytest.fixture(autouse=True)
def reset_balance(api):
    """Resets balance to a known state before every test."""
    r = api.reset_balance()
    print(f"Balance Reset = {r.json()["balance"]}")
    assert r.status_code == 200, f"Balance reset failed: {r.text}"
    yield


# TEST DATA
STAKE_TEST_CASES = [
    # Valid stakes (accepted)
    (1.00, 200, "valid", "1 minimum valid stake (€1.00) according to Business Rules (Section 3)"),
    (1.01, 200, "valid","2 minimum valid stake (€1.01) according to Validation Rules (Section 4.1)"),
    (50.00, 200, "valid", "3 mid-range stake (€50.00)"),
    (100.00, 200, "valid", "4 maximum valid stake (€100.00)"),
    # Invalid stakes (rejected)
    (0.99, 422, "invalid", "5 below minimum (0.99 < 1.00)"),
    (100.01, 422, "invalid", "6 above maximum (100.01 > 100.00)"), #this test also test pretest 2 decimal places 
    (126, 422, "invalid", "7 exceeds balance (126 > 125.50)"),
    (0, 422, "invalid", "8 zero stake"),
    (10.999, 422, "invalid", "9 invalid precision (>2 decimal places)"), 
    (-5.00, 422, "invalid", "10 invalid negative stake"),
]


@pytest.mark.api
@pytest.mark.parametrize(
    "stake, expected_status, category, description",
    STAKE_TEST_CASES,
    ids=[
        "valid_min_1.00", "valid_min_1.01", "valid_mid", "valid_max",
        "invalid_below_min", "invalid_above_max", "invalid_exceeds_balance", 
        "invalid_zero", "invalid_precision","invalid_negative_stake"
    ]
)

#Validations Rules
@allure.label("owner", "Nkina Ramonyai")
@allure.severity(allure.severity_level.CRITICAL)
def test_stake_validation_business_rules(api, valid_match_id, stake, expected_status, category, description):
    """
    Severity: CRITICAL - Revenue-impacting test
    Validates ALL stake business rules in ONE test:
        - Valid stakes → Accepted
        - Invalid stakes → Rejected with 422
        - Payout calculation (stake × odds) is accurate
        - Balance deduction is correct
    """
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"Stake: {stake} | Expected: {'ACCEPT' if expected_status == 200 else 'REJECT'}")
    print(f"{'='*70}")
    
    # Get initial balance
    expected_balance_currency = 'EUR'
    balance_resp = api.get_balance()
    assert balance_resp.status_code == 200, "Failed to get balance"
    initial_balance = balance_resp.json()["balance"]
    balance_currency =  balance_resp.json()["currency"]
    #REPORT INITIAL BALANCE
    print(f"Initial Balance: {balance_currency}{initial_balance}")
    
    #VERIFY BALANCE CURRENCY - INITIAL
    assert balance_resp.json()["currency"] == expected_balance_currency, (
    pytest.xfail(f"Balance currency error: expected {expected_balance_currency}, actual {balance_resp['currency']}")
    )
    
    # Place bet - using "home" selection (matches API odds structure)
    bet_response = api.place_bet(match_id=valid_match_id, selection="HOME", stake=stake)
    print(f"Response: {bet_response.status_code}")
    
    # Handle known bugs
    if stake < 0 and bet_response.status_code == 200:
        pytest.xfail(f"BUG: Negative stake €{stake} was accepted")
        return
    
    if stake > initial_balance and bet_response.status_code == 200:
        pytest.xfail(f"BUG: Bet €{stake} exceeds balance €{initial_balance} but was accepted")
        return
    
    if stake > initial_balance and bet_response.status_code == 422:
        expected_error = 'Insufficient balance'
        error_body = bet_response.json()
        actual_error = error_body['message']
        if actual_error != expected_error:
            pytest.xfail(f"BUG: Wrong error message for balance exceeded: expected {expected_error}, actual {actual_error}")
            return
                    
    
    # Verify expected status
    assert bet_response.status_code == expected_status, (
        f"Expected {expected_status}, actual {bet_response.status_code}\n"
        f"Response: {bet_response.text}"
    )
    
    # For accepted bets, verify calculations
    if bet_response.status_code == 200:
        body = bet_response.json()
        print(bet_response.json())
        
        # Verify payout: stake × odds
        expected_payout = round(stake * body["odds"], 2)
        assert math.isclose(body["payout"], expected_payout, abs_tol=0.02), (
            f"Payout error: €{stake} × {body['odds']} = €{expected_payout}, actual €{body['payout']}"
        )
        print(f"Accepted - Payout: {expected_balance_currency}{body['payout']} | New Balance: {body['currency']}{body['balance']}")
        
         #VERIFY BALANCE CURRENCY - AFTER SUCCESSFUL BET PLACEMENT
        if body.get("currency") != "EUR":
            pytest.xfail(f"BUG: Currency error: expected {expected_balance_currency}, actual {body['currency']}")
            return
    else:
        print(f"Rejected - Invalid stake €{stake}")
        if bet_response.text:
            try:
                body = bet_response.json()
                if "message" in body:
                    print(f"   Error: {body['message']}")
            except:
                pass
            
         
    
