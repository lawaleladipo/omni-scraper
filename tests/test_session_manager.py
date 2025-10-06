from omni_scraper.core.session_manager import SessionManager
import pytest

def test_session_manager_creation():
    manager = SessionManager()
    assert manager is not None

def test_session_manager_with_tor():
    manager = SessionManager(use_tor=True)
    assert manager is not None

def test_session_manager_get():
    manager = SessionManager()
    # This will test the session creation
    session = manager.get_session()
    assert session is not None
