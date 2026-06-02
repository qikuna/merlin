# Copyright (C) 2026 Qikuna <dev@qikuna.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import sys

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PORTABLE_DIR = os.path.join(APP_DIR, "data")

if os.path.exists(PORTABLE_DIR):
    DATA_DIR = PORTABLE_DIR
else:
    DATA_DIR = os.path.expanduser("~/.local/share/merlin/data")

os.makedirs(DATA_DIR, exist_ok=True)


def get_file_path(date_str):

    return os.path.join(DATA_DIR, f"{date_str}.json")


def load_day(date_str):

    file_path = get_file_path(date_str)
    if not os.path.exists(file_path):
        return {"date": date_str, "blocks": []}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"date": date_str, "blocks": []}


def save_day(date_str, data):

    file_path = get_file_path(date_str)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_dates():

    if not os.path.exists(DATA_DIR):
        return []
    files = os.listdir(DATA_DIR)
    dates = [f.replace(".json", "") for f in files if f.endswith(".json")]
    return sorted(dates)


def delete_day(date_str):

    file_path = get_file_path(date_str)
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_specific_entry(date_str, block_index):

    data = load_day(date_str)
    if 0 <= block_index < len(data["blocks"]):
        data["blocks"].pop(block_index)
        save_day(date_str, data)
        return True
    return False
