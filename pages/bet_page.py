# bet_page.py - FULL COMPLETE CODE
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re
import time
import os
from typing import List, Dict, Optional

class MatchOdds:
    """Class to store match and odds information"""
    def __init__(self, match_id: str, league: str, home_team: str, away_team: str, 
                 date_text: str, odds: Dict[str, float], odd_elements: Dict[str, any]):
        self.match_id = match_id
        self.league = league
        self.home_team = home_team
        self.away_team = away_team
        self.date_text = date_text
        self.odds = odds
        self.odd_elements = odd_elements
        self.parsed_date = None

class BettingPage:
    """Page Object Model for the Sports Betting Website"""
    
    # Locators
    MATCH_CARD = (By.CLASS_NAME, "matchCard")
    MATCH_META = (By.CLASS_NAME, "matchMeta")
    TEAMS_DIV = (By.CLASS_NAME, "teams")
    TEAM_ROW = (By.CLASS_NAME, "teamRow")
    TEAM_NAME = (By.CLASS_NAME, "teamName")
    ODDS_GRID = (By.CLASS_NAME, "oddsGrid")
    ODDS_BUTTON = (By.CLASS_NAME, "oddsButton")
    ODDS_BUTTON_LABEL = (By.CLASS_NAME, "oddsButtonLabel")
    ODDS_BUTTON_VALUE = (By.CLASS_NAME, "oddsButtonValue")
    STAKE_INPUT = (By.XPATH, "//input[@placeholder='0.00']")
    PLACE_BET_BUTTON = (By.XPATH, "//button[contains(., 'Place Bet')]")
    CLOSE_BUTTON = (By.XPATH, "//button[contains(., 'Close')]")
    BALANCE_DISPLAY = (By.CSS_SELECTOR, ".balance, [class*='balance']")
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.matches = []
        self.screenshot_counter = 0
        self.screenshot_dir = None
    
    def set_screenshot_directory(self, screenshot_dir: str):
        """Set the directory for saving screenshots"""
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)
        print(f"Screenshots will be saved in: {screenshot_dir}")
    
    def take_screenshot(self, name: str) -> Optional[str]:
        """Take a screenshot with the given name"""
        if not self.screenshot_dir:
            print("Screenshot directory not set. Call set_screenshot_directory() first.")
            return None
        
        self.screenshot_counter += 1
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{self._sanitize_filename(name)}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            print(f"Screenshot #{self.screenshot_counter}: {filename}")
            return filepath
        except Exception as e:
            print(f"Failed to save screenshot: {e}")
            return None
    
    def _sanitize_filename(self, text: str) -> str:
        """Remove special characters for filename"""
        return re.sub(r'[^\w\-_\. ]', '_', text)
    
    def _parse_match_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from match card"""
        date_text = date_text.strip()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_text.lower() == 'tomorrow':
            return today + timedelta(days=1)
        
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if date_text.lower() in weekdays:
            target_weekday = weekdays.index(date_text.lower())
            days_ahead = target_weekday - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        pattern = r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(\d{1,2})\s+(\w+)'
        match = re.search(pattern, date_text)
        
        if match:
            day = int(match.group(1))
            month_str = match.group(2)[:3].lower()
            month = month_map.get(month_str, 1)
            year = today.year
            
            match_date = datetime(year, month, day)
            if match_date < today and month == 1:
                match_date = datetime(year + 1, month, day)
            
            return match_date
        
        return None
    
    def extract_upcoming_matches(self) -> List[MatchOdds]:
        """Extract all matches with dates > today and store in array"""
        self.matches = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Wait for matches to load
        self.wait.until(EC.presence_of_element_located(self.MATCH_CARD))
        
        match_cards = self.driver.find_elements(*self.MATCH_CARD)
        print(f"\nFound {len(match_cards)} total matches on page")
        
        for card in match_cards:
            try:
                # Extract all matches from the web match metadata
                match_meta = card.find_element(*self.MATCH_META)
                meta_spans = match_meta.find_elements(By.TAG_NAME, "span")
                
                league = meta_spans[1].text if len(meta_spans) > 1 else "Unknown"
                date_text = meta_spans[3].text if len(meta_spans) > 3 else ""
                
                match_date = self._parse_match_date(date_text)
                
                # Only include matches with date > today
                if match_date and match_date > today:
                    match_id = card.get_attribute("id")
                    
                    # Extract team names
                    teams_div = card.find_element(*self.TEAMS_DIV)
                    team_rows = teams_div.find_elements(*self.TEAM_ROW)
                    
                    home_team = team_rows[0].find_element(*self.TEAM_NAME).text if len(team_rows) > 0 else ""
                    away_team = team_rows[1].find_element(*self.TEAM_NAME).text if len(team_rows) > 1 else ""
                    
                    # Extract odds and their clickable elements
                    odds_grid = card.find_element(*self.ODDS_GRID)
                    odds_buttons = odds_grid.find_elements(*self.ODDS_BUTTON)
                    
                    odds = {}
                    odd_elements = {}
                    
                    for btn in odds_buttons:
                        label = btn.find_element(*self.ODDS_BUTTON_LABEL).text
                        value = float(btn.find_element(*self.ODDS_BUTTON_VALUE).text)
                        odds[label] = value
                        odd_elements[label] = btn
                    
                    match = MatchOdds(match_id, league, home_team, away_team, date_text, odds, odd_elements)
                    match.parsed_date = match_date
                    self.matches.append(match)
                    
                    print(f"Added: {home_team} vs {away_team} ({league}) - {date_text}")
                
            except Exception as e:
                print(f"Error extracting match: {e}")
                continue
        
        print(f"\nTotal upcoming matches: {len(self.matches)}")
        return self.matches
    
    def get_match_by_index(self, index: int) -> Optional[MatchOdds]:
        """Get match by index from the array"""
        if 0 <= index < len(self.matches):
            return self.matches[index]
        print(f"Match at index {index} not found. Total matches: {len(self.matches)}")
        return None
    
    def get_first_match(self) -> Optional[MatchOdds]:
        """Get the first match from the array (index 0)"""
        return self.get_match_by_index(0)
    
    def click_odd(self, match: MatchOdds, bet_type: str) -> bool:
        """Click on a specific odd for a match"""
        if bet_type not in match.odd_elements:
            print(f"Invalid bet type: {bet_type}. Use '1', 'X', or '2'")
            return False
        
        try:
            odd_element = match.odd_elements[bet_type]
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", odd_element)
            time.sleep(0.5)
            odd_element.click()
            print(f"Clicked {bet_type} odd (Odds: {match.odds[bet_type]}) for {match.home_team} vs {match.away_team}")
            return True
        except Exception as e:
            print(f"Failed to click odd: {e}")
            return False
    
    def enter_stake(self, amount: float) -> bool:
        """Enter stake amount"""
        try:
            stake_input = self.wait.until(EC.element_to_be_clickable(self.STAKE_INPUT))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", stake_input)
            stake_input.clear()
            stake_input.send_keys(str(amount))
            print(f"Entered Stake: €{amount}")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Failed to enter stake: {e}")
            return False
    
    def click_place_bet(self) -> bool:
        """Click the Place Bet button"""
        try:
            place_btn = self.wait.until(EC.element_to_be_clickable(self.PLACE_BET_BUTTON))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", place_btn)
            time.sleep(0.5)
            place_btn.click()
            print("Clicked Place Bet")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Failed to click Place Bet: {e}")
            return False
    
    def is_close_button_visible(self) -> bool:
        """Check if close button is visible and clickable"""
        try:
            close_btn = self.wait.until(EC.element_to_be_clickable(self.CLOSE_BUTTON))
            print("Close button is VISIBLE and CLICKABLE")
            return True
        except Exception as e:
            print(f"Close button NOT visible: {e}")
            return False
    
    def close_success_modal(self) -> bool:
        """Close the success modal"""
        try:
            close_btn = self.wait.until(EC.element_to_be_clickable(self.CLOSE_BUTTON))
            close_btn.click()
            print("Closed confirmation modal")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Could not close modal: {e}")
            return False
    
    def place_bet(self, match: MatchOdds, bet_type: str, stake: float, 
                  take_screenshots: bool = True, screenshot_prefix: str = "") -> Dict:
        """
        Complete bet placement workflow - FIXED to prevent duplicate clicks
        """
        result = {
            'success': False,
            'match': match,
            'bet_type': bet_type,
            'stake': stake,
            'odds': match.odds.get(bet_type),
            'screenshots': []
        }
        
        bet_name = {'1': 'HomeWin', 'X': 'Draw', '2': 'AwayWin'}.get(bet_type, bet_type)
        match_name = f"{match.home_team}_vs_{match.away_team}"
        
        print(f"\n{'='*60}")
        print(f"Placing {bet_name} Bet - Stake: €{stake}")
        print(f"{'='*60}")
        
        # Wait a moment for any previous modal to close
        time.sleep(1)
        
        # Click the odd
        if not self.click_odd(match, bet_type):
            return result
        
        # Small delay after clicking odd
        time.sleep(0.5)
        
        # Enter stake
        if not self.enter_stake(stake):
            return result
        
        # Screenshot 1: After entering stake
        if take_screenshots:
            screenshot_name = f"{screenshot_prefix}{match_name}_{bet_name}_bet_{stake}" if screenshot_prefix else f"{match_name}_{bet_name}_bet_{stake}"
            path = self.take_screenshot(screenshot_name)
            if path:
                result['screenshots'].append(('Amount Entry', path))
        
        # Click Place Bet
        if not self.click_place_bet():
            return result
        
        # Check for close button (success confirmation)
        if self.is_close_button_visible():
            # Screenshot 2: After successful bet
            if take_screenshots:
                screenshot_name = f"{screenshot_prefix}successful_bet_{match_name}_{bet_name}" if screenshot_prefix else f"successful_bet_{match_name}_{bet_name}"
                path = self.take_screenshot(screenshot_name)
                if path:
                    result['screenshots'].append(('Successful Bet', path))
            
            # Close the modal
            self.close_success_modal()
            result['success'] = True
            print(f"{bet_name} bet placed successfully!")
            
            # CRITICAL: Wait for modal to fully close before next bet
            time.sleep(2)
        else:
            print(f"Bet placement failed - no confirmation modal")
        
        return result
    
    def display_matches(self):
        """Display all upcoming matches"""
        if not self.matches:
            print("\nNo upcoming matches available")
            return False
        
        print("\n" + "="*60)
        print("UPCOMING MATCHES (Date > Today)")
        print("="*60)
        
        for i, match in enumerate(self.matches, 1):
            print(f"\n{i}. {match.league}")
            print(f"{match.home_team} vs {match.away_team}")
            print(f"Date: {match.date_text} ({match.parsed_date.strftime('%Y-%m-%d')})")
            print(f"Odds: 1:{match.odds.get('1', 'N/A')} | X:{match.odds.get('X', 'N/A')} | 2:{match.odds.get('2', 'N/A')}")
        
        return True
    
    def get_balance(self) -> float:
        """Get current balance"""
        try:
            balance_element = self.driver.find_element(*self.BALANCE_DISPLAY)
            balance_text = balance_element.text
            balance_match = re.search(r'[\d,.]+', balance_text)
            if balance_match:
                return float(balance_match.group().replace(',', ''))
        except:
            pass
        return 0.0
        
