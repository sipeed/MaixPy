import os
import json

class Params:
    def __init__(self, path = None):
        if not path:
            home = os.environ.get("HOME", "/root")
            path = os.path.join(home, ".config", "maixhub", "params.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self.params = {
            "resolution": (448, 448)
        }

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.params, f, indent=4)

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, "r") as f:
            try:
                params = json.load(f)
                self.params.update(params)
            except Exception as e:
                import traceback
                traceback.print_exc()
