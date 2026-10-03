"""
conftest.py — shared pytest configuration for the backend test suite.

Sets environment variables before any module is imported so that:
  - The academic API search uses mock data (no real HTTP calls).
  - The LLM service has a placeholder API key so its lazy
    initialiser does not raise a ValueError during tests that
    do not exercise LLM functionality.
"""

import os
from app.database.init_db import init_db

# ---------------------------------------------------------------
# Use mock data for Semantic Scholar so tests never hit the
# real API and do not require network access or an API key.
# ---------------------------------------------------------------
os.environ.setdefault("MOCK_SEMANTIC_SCHOLAR", "true")

# ---------------------------------------------------------------
# Provide a dummy API key so that the LLM client can be
# constructed without raising a ValueError.  Tests that call
# real LLM endpoints should mock the client themselves.
# ---------------------------------------------------------------
os.environ.setdefault("LLM_API_KEY", "test-dummy-key-for-pytest")

# Initialize the database tables for testing
init_db()
