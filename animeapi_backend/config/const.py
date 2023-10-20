"""Module for constants, such as login credentials, etc."""

import os
from time import time

from dotenv import load_dotenv

from animeapi_backend.prettyprint import PrettyPrint

# Check if .env file exists, load it
if os.path.isfile(".env"):
    load_dotenv()

# Kaize login credentials
KAIZE_XSRF_TOKEN = os.getenv("KAIZE_XSRF_TOKEN")
"""Kaize XSRF token"""
KAIZE_SESSION = os.getenv("KAIZE_SESSION")
"""Kaize session cookie"""
KAIZE_EMAIL = os.getenv("KAIZE_EMAIL")
"""User email for Kaize login"""
KAIZE_PASSWORD = os.getenv("KAIZE_PASSWORD")
"""User password for Kaize login"""

# Program start time
START_TIME = time()

# Whether the script is running from GitHub Actions workflow_dispatch event
GITHUB_DISPATCH = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"

# PrettyPrint class instance
PPRINT = PrettyPrint()
"""Instance of PrettyPrint class globally available"""
