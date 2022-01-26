import json
import yaml
from collections import UserDict
from os.path import exists
from pathlib import Path

DATA_DIR = 'data'

def get_data_folder():
    return Path(__file__).parent.resolve() / 'data'

class JsonObject(UserDict):
    def __init__(self, filename):
        self.filename = get_data_folder() / filename
        if exists(self.filename):
            with open(self.filename) as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save(self, ensure_serializable=True):
        s = json.dumps(self.data) # fail here rather than failing and half-overwriting the file
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

class Aggregated(JsonObject):
    def __init__(self):
        super().__init__('aggregated.json')
    def keys_by_gear(self, gear):
        return [k for k, v in self.data.items() if v['gear']==gear]

class Skills():
    def __init__(self):
        with open(get_data_folder() / 'skill_list.yaml', "r") as stream:
            self.data = yaml.safe_load(stream)

class Config(UserDict):
    def __init__(self):
        with open(get_data_folder() / 'config.yaml', "r") as stream:
            self.data = yaml.safe_load(stream)
