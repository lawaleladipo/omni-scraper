import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from ..config.settings import config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class OutputHandler:
    def __init__(self):
        self.format = config.get("output.format", "json")
        self.dir = Path(config.base_dir) / config.get(
            "output.directory", "data/outputs"
        )
        self.timestamp = datetime.now(timezone.utc).strftime(
            config.get("output.timestamp_format", "%Y%m%d_%H%M%S")
        )
        self.dir.mkdir(parents=True, exist_ok=True)

    def _filename(self, prefix):
        ext = self.format
        return self.dir / f"{prefix}_{self.timestamp}.{ext}"

    def save(self, prefix, data):
        path = self._filename(prefix)
        try:
            if self.format == "json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif self.format == "csv":
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    with open(path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                        writer.writeheader()
                        writer.writerows(data)
                else:
                    raise ValueError("CSV requires list of dicts")
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(str(data))
            logger.info(f"Saved output to {path}")
            return str(path)
        except Exception as e:
            logger.exception(f"Failed to save output: {e}")
            raise
