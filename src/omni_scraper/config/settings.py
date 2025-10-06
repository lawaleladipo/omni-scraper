import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self._load_environment()
        self._load_config()

    def _load_environment(self):
        env_path = self.base_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)

    def _load_config(self):
        config_path = self.base_dir / 'config' / 'default.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}
        # Sensible defaults
        self.config.setdefault('hibp', {})
        self.config.setdefault('tor', {})
        self.config.setdefault('crawler', {})
        self.config.setdefault('logging', {})
        self.config.setdefault('output', {})

        # Env overrides
        self.config['hibp']['api_key'] = os.getenv('HIBP_API_KEY', self.config['hibp'].get('api_key'))
        self.config['tor']['password'] = os.getenv('TOR_PASSWORD', self.config['tor'].get('password'))
        self.config['shodan'] = self.config.get('shodan', {})
        self.config['shodan']['api_key'] = os.getenv('SHODAN_API_KEY', self.config['shodan'].get('api_key'))

    def get(self, key, default=None):
        keys = key.split('.')
        v = self.config
        for k in keys:
            if not isinstance(v, dict):
                return default
            v = v.get(k, None)
            if v is None:
                return default
        return v

config = Config()
