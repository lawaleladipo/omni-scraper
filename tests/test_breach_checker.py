from omni_scraper.modules.breach_checker import BreachChecker
from unittest.mock import Mock, patch
import pytest

def test_breach_checker_creation():
    checker = BreachChecker()
    assert checker is not None

def test_breach_checker_headers():
    checker = BreachChecker()
    headers = checker._headers()
    assert 'User-Agent' in headers
    assert 'Accept' in headers

@patch('omni_scraper.modules.breach_checker.SessionManager')
def test_check_email_no_api_key(mock_session_manager):
    checker = BreachChecker()
    checker.api_key = ""  # No API key
    
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {"records": []}
    mock_session_manager.return_value.get.return_value = mock_response
    
    result = checker.check_email("test@example.com")
    assert result == []
