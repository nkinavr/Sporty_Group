"""
API client for the Sports Betting QA application.

A thin, stateless wrapper around `requests` that:
  - Injects the required x-user-id header on every call
  - Exposes typed methods for each endpoint
  - Returns raw responses so tests can assert on status codes and bodies directly
  - Filters matches to only include upcoming fixtures (date > today)

No business logic lives here — just HTTP mechanics.
"""
import requests
from datetime import datetime
from typing import List, Dict, Optional
from config import API_BASE_URL, USER_ID
import allure

@allure.label("owner", "Nkina Ramonyai")
@allure.epic("Stake Validation")
class BettingApiClient:
    def __init__(self, user_id: str = USER_ID, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"x-user-id": user_id})

    # ── Matches ──────────────────────────────────────────────────────────────

    def get_matches(self) -> requests.Response:
        """GET /api/matches — returns all matches (both upcoming and past)."""
        return self.session.get(f"{self.base_url}/matches")
    
    def get_upcoming_matches(self) -> List[Dict]:
        """
        GET /api/matches and filters to only upcoming matches (date > today).
        
        Returns:
            List of match dictionaries for matches scheduled in the future.
            Empty list if no upcoming matches found.
        """
        resp = self.get_matches()
        if resp.status_code != 200:
            return []
        
        matches = resp.json()
        current_date = datetime.now()
        upcoming_matches = []
        
        for match in matches:
            match_date = self._parse_match_date(match.get("date", ""))
            if match_date and match_date > current_date:
                upcoming_matches.append(match)
        
        return upcoming_matches
    
    def get_upcoming_match_id(self) -> Optional[str]:
        """
        Returns the ID of the first upcoming match.
        
        Returns:
            Match ID string if an upcoming match exists, None otherwise.
        """
        upcoming_matches = self.get_upcoming_matches()
        if upcoming_matches:
            return upcoming_matches[0]["id"]
        return None
    
    def get_first_upcoming_match(self) -> Optional[Dict]:
        """
        Returns the first upcoming match as a dictionary.
        
        Returns:
            Match dictionary if an upcoming match exists, None otherwise.
        """
        upcoming_matches = self.get_upcoming_matches()
        if upcoming_matches:
            return upcoming_matches[0]
        return None
    
    def _parse_match_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse match date from API response.
        
        Supports multiple date formats:
            - ISO format: "2024-03-15T14:30:00Z"
            - Simple date: "2024-03-15"
            - Date with timezone: "2024-03-15T14:30:00+00:00"
        
        Args:
            date_string: Date string from API response
            
        Returns:
            datetime object if parsing succeeds, None otherwise
        """
        if not date_string:
            return None
        
        # Try different date formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",   # ISO with milliseconds
            "%Y-%m-%dT%H:%M:%SZ",      # ISO standard
            "%Y-%m-%dT%H:%M:%S%z",     # ISO with timezone
            "%Y-%m-%d",                 # Simple date
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except (ValueError, TypeError):
                continue
        
        # Try using dateutil as fallback (if available)
        try:
            from dateutil import parser
            return parser.parse(date_string)
        except ImportError:
            pass
        except Exception:
            pass
        
        return None
    
    def match_is_upcoming(self, match: Dict) -> bool:
        """
        Check if a match is upcoming (date > today).
        
        Args:
            match: Match dictionary from API response
            
        Returns:
            True if match is scheduled for the future, False otherwise
        """
        match_date = self._parse_match_date(match.get("date", ""))
        if match_date:
            return match_date > datetime.now()
        return False

    # ── Balance ──────────────────────────────────────────────────────────────

    def get_balance(self) -> requests.Response:
        """GET /api/balance — returns current user balance."""
        return self.session.get(f"{self.base_url}/balance")

    def reset_balance(self) -> requests.Response:
        """POST /api/reset-balance — resets balance to initial configured value."""
        return self.session.post(f"{self.base_url}/reset-balance")

    # ── Bet placement ─────────────────────────────────────────────────────────

    def place_bet(
        self,
        match_id: str,
        selection: str,
        stake: float | int | str,
    ) -> requests.Response:
        """
        POST /api/place-bet

        Args:
            match_id:  ID string from GET /api/matches (recommend using upcoming matches)
            selection: "HOME" | "DRAW" | "AWAY"
            stake:     numeric stake value (passed as-is to test boundary behaviour)
        """
        return self.session.post(
            f"{self.base_url}/place-bet",
            json={"matchId": match_id, "selection": selection, "stake": stake},
        )

    def place_bet_raw(self, payload: dict) -> requests.Response:
        """
        POST /api/place-bet with an arbitrary payload dict.
        Used to test malformed / missing-field scenarios without the helper's defaults.
        """
        return self.session.post(f"{self.base_url}/place-bet", json=payload)

    def place_bet_no_auth(
        self,
        match_id: str,
        selection: str,
        stake: float,
    ) -> requests.Response:
        """POST /api/place-bet without the x-user-id header (auth test)."""
        return requests.post(
            f"{self.base_url}/place-bet",
            json={"matchId": match_id, "selection": selection, "stake": stake},
        )
    
    # ── Convenience Methods for Testing ─────────────────────────────────────

    def place_bet_on_upcoming_match(
        self,
        selection: str,
        stake: float | int | str,
    ) -> Optional[requests.Response]:
        """
        Convenience method: places a bet on the first upcoming match.
        
        Args:
            selection: "HOME" | "DRAW" | "AWAY"
            stake: numeric stake value
            
        Returns:
            Response object if an upcoming match exists, None otherwise
        """
        match_id = self.get_upcoming_match_id()
        if match_id:
            return self.place_bet(match_id, selection, stake)
        return None
