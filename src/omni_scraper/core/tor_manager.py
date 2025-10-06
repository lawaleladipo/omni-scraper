from stem.control import Controller
from stem import Signal
import time
from ..config.settings import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class TorManager:
    def __init__(self):
        tor_cfg = config.get('tor') or {}
        self.control_port = tor_cfg.get('control_port', 9051)
        self.socks_port = tor_cfg.get('socks_port', 9050)
        self.password = tor_cfg.get('password')
        self.retry_count = 0
        self.max_retries = tor_cfg.get('max_retries', 3)
        self.renewal_interval = tor_cfg.get('renewal_interval', 5)

    def renew_identity(self):
        try:
            with Controller.from_port(port=self.control_port) as controller:
                if self.password:
                    controller.authenticate(password=self.password)
                else:
                    controller.authenticate()
                controller.signal(Signal.NEWNYM)
                logger.info("Tor circuit renewed")
                self.retry_count = 0
                time.sleep(self.renewal_interval)
                return True
        except Exception as e:
            self.retry_count += 1
            logger.error(f"Tor renew failed: {e}")
            if self.retry_count >= self.max_retries:
                logger.critical("Max Tor renew retries exceeded")
                raise
            return False

    def get_socks_url(self):
        return f"socks5h://127.0.0.1:{self.socks_port}"
