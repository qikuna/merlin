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

import re

COLOR_MAP = {"r": "red", "g": "green", "b": "blue", "y": "yellow", "w": "white"}


def process_line(raw_text):

    match = re.match(r"^#([rgbyw])\s(.*)", raw_text)
    if match:
        color_command = match.group(1)
        clean_text = match.group(2)
        color_name = COLOR_MAP.get(color_command, "white")
        return clean_text, color_name

    return raw_text, "white"
