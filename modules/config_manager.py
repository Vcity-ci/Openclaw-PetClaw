import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_dir = self._resolve_config_dir()
        self.config_file = self.config_dir / "settings.json"

    def _resolve_config_dir(self) -> Path:
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "PetClaw"
        return Path.home() / ".petclaw"

    def load(self) -> dict:
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def save(self, data: dict) -> bool:
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def update_paths(self, root_path: str, input_path: str, output_path: str) -> bool:
        payload = {
            "openclaw_root": root_path,
            "input_dir": input_path,
            "output_dir": output_path,
        }
        return self.save(payload)
