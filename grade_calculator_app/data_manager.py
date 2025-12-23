import json
import os
from typing import Dict, Any

class DataManager:
    def __init__(self, filepath: str, settings_filepath: str = "settings.json"):
        self.filepath = filepath
        self.settings_filepath = settings_filepath

    def save_settings(self, settings: Dict[str, Any]):
        try:
            with open(self.settings_filepath, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_settings(self) -> Dict[str, Any]:
        if os.path.exists(self.settings_filepath):
            try:
                with open(self.settings_filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return {}
        return {}

    def save_data(self, data: Dict[str, Any]):
        try:
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
            raise e

    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    # Migrate old list format to new dict format if necessary
                    if isinstance(data, list):
                        return {"Year 1": data}
                    return data
            except Exception as e:
                print(f"Error loading data: {e}")
                return {}
        return {}
