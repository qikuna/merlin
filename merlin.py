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

import os
import shutil
import sys

from core import storage
from ui.tui import launch_tui


def uninstall():
    print("==> [Merlin Uninstaller] Initializing...")
    bin_path = os.path.expanduser("~/.local/bin/merlin")

    if os.path.exists(bin_path):
        os.remove(bin_path)
        print(f"--> Removed system launcher: {bin_path}")
    else:
        print(f"--> Launcher not found at {bin_path}")

    data_dir = storage.DATA_DIR
    ans = (
        input(f"\nDo you want to delete ALL your saved data in '{data_dir}'? (y/n): ")
        .strip()
        .lower()
    )

    if ans in ("y", "yes"):
        shutil.rmtree(data_dir, ignore_errors=True)
        print("--> Data deleted successfully.")
    else:
        print("--> Data preserved.")

    print("\n[Uninstallation finished] MERLIN has been removed from your system.")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        uninstall()
    else:
        try:
            launch_tui()
        except KeyboardInterrupt:
            pass
