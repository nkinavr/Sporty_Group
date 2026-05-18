"""
Central configuration module.
All env-driven settings are read here so tests never import os.environ directly.
"""
import json
import os

#UI Variables
BASE_URL: str = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app")
USER_ID: str = os.getenv("USER_ID", "candidate-N6pYw2Jk7A")
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

#API Variables
FULL_URL = f"{BASE_URL}/?user-id={USER_ID}"
API_BASE_URL = f"{BASE_URL}/api"

