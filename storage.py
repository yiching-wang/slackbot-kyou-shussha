import json
import os
from datetime import date

IGNORE_FILE = "ignore.json"

def is_ignored_today():
    if not os.path.exists(IGNORE_FILE):
        return False
    with open(IGNORE_FILE) as f:
        data = json.load(f)
    return data.get(str(date.today()), False)

def set_ignore_today():
    data = {}
    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE) as f:
            data = json.load(f)
    data[str(date.today())] = True
    with open(IGNORE_FILE, "w") as f:
        json.dump(data, f)