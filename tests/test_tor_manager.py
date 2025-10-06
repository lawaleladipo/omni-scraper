from omni_scraper.core.tor_manager import TorManager

def test_tor_manager_creation():
    manager = TorManager()
    assert manager is not None

def test_tor_manager_ports():
    manager = TorManager()
    assert hasattr(manager, 'tor_port')
    assert hasattr(manager, 'control_port')
