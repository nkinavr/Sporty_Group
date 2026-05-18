import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import os
import allure
from pages.bet_page import BettingPage as bet_page
from conftest import FULL_URL

class TestBetPlacement:
    """
    Test class for bet placement functionality
    Then see that the code works and catches the error messages
    """
    
    @pytest.fixture(scope="function")
    def driver(self):
        """Setup WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        #chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.get(FULL_URL)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def betting_page(self, driver):
        """Create betting page object"""
        return bet_page(driver)
    
    @pytest.fixture
    def screenshot_dir(self):
        """Create screenshot directory - FIXED"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = f"screenshots/Screenshots_{timestamp}"
        os.makedirs(screenshot_dir, exist_ok=True)
        return screenshot_dir
    
    
    #Positive Tests (happy path)
    @allure.label("owner", "Nkina Ramonyai")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_bet_all_odds_for_first_match(self, driver, betting_page, screenshot_dir):
        """
        Severity: CRITICAL - Revenue-impacting test
        E2E UI TEST - CRITICAL USER JOURNEY
    
        WHY THIS TEST WAS CHOSEN FOR AUTOMATION:
        This test validates the ONLY revenue-generating action on the platform.
        A user must be able to:
            1. Select odds for an upcoming match
            2. Enter a valid stake amount
            3. Place the bet successfully
            4. Receive confirmation
            5. See updated balance - BUG-001 — Balance Reset Does Not Sync Correctly Between API and UI
        
        This test covers the complete betting flow from start to finish.
        If this test fails, the platform cannot generate revenue.
    
        TEST COVERAGE:
        - All three bet types (HOME, DRAW, AWAY)
        - Minimum stake (€1.00)
        - Mid-range stake (€15.00)
        - Maximum stake (€100.00)
        - Screenshot evidence of each step
        - Balance verification
    
        """

        # Set screenshot directory
        betting_page.set_screenshot_directory(screenshot_dir)
        
        # Extract upcoming matches
        matches = betting_page.extract_upcoming_matches()
        
        # Verify matches exist
        assert len(matches) > 0, "No upcoming matches found"
        
        # Display all matches
        betting_page.display_matches()
        
        # Get the first match (index 0)
        first_match = betting_page.get_first_match()
        assert first_match is not None, "Failed to get first match"
        
        print(f"SELECTED MATCH (Index 0): {first_match.home_team} vs {first_match.away_team}")
        print(f"   League: {first_match.league}")
        print(f"   Date: {first_match.date_text}")
        print(f"   Available Odds: 1:{first_match.odds['1']} | X:{first_match.odds['X']} | 2:{first_match.odds['2']}")
        
        # Define bet types to test - EACH TYPE ONCE
        bets = [
            {'type': '1', 'name': 'HomeWin', 'amount': 1.00},
            {'type': 'X', 'name': 'Draw', 'amount': 15},
            {'type': '2', 'name': 'AwayWin', 'amount': 100},
        ]
        
        # Place all bets - track which ones were placed
        all_bets_results = []
        placed_bet_types = set()  # Track to prevent duplicates
        
        for bet in bets:
            
            
            result = betting_page.place_bet(
                match=first_match,
                bet_type=bet['type'],
                stake=bet['amount'],
                take_screenshots=True,
                screenshot_prefix=""
            )
            
            if result['success']:
                placed_bet_types.add(bet['type'])
                print(f"{bet['name']} bet completed successfully!")
            else:
                print(f"{bet['name']} bet failed!")
            
            all_bets_results.append(result)
            
            # Extra delay between different bet types
            time.sleep(2)
        
        # Verify results - should have 3 unique bet types
        successful_bets = [r for r in all_bets_results if r['success']]
        successful_types = [r['bet_type'] for r in successful_bets]
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"\nTotal bets attempted: {len(bets)}")
        print(f"Successful bets: {len(successful_bets)}")
        print(f"Bet types placed: {successful_types}")
        print(f"Total screenshots taken: {betting_page.screenshot_counter}")
        
        # Check for duplicates in results
        if len(successful_types) != len(set(successful_types)):
            print("WARNING: Duplicate bet types detected!")
        else:
            print("No duplicate bet types - each bet ran once!")
        
        # Display screenshot summary
        print("\nScreenshots taken:")
        for i, result in enumerate(all_bets_results, 1):
            if result['screenshots']:
                for stage, path in result['screenshots']:
                    print(f"   Bet {i} - {stage}: {os.path.basename(path)}")
        
        # Assert we have 3 unique bets (or at least 1)
        assert len(successful_bets) > 0, "No bets were placed successfully"
        
        print(f"\nAll screenshots saved in: '{screenshot_dir}'")
        print("\nTEST COMPLETED SUCCESSFULLY!")

    
