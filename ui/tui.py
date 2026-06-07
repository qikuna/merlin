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

import curses
import os
import textwrap
from datetime import datetime

from core import parser, storage

os.environ.setdefault("ESCDELAY", "25")


def launch_tui():
    curses.wrapper(tui_controller)


def init_colors():
    try:
        curses.use_default_colors()
    except curses.error:
        pass
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    return {
        "red": curses.color_pair(1),
        "green": curses.color_pair(2),
        "blue": curses.color_pair(3),
        "yellow": curses.color_pair(4),
        "white": curses.color_pair(5),
    }


def safe_addstr(stdscr, y, x, text, attr=0):
    height, width = stdscr.getmaxyx()
    if 0 <= y < height and 0 <= x < width:
        max_len = width - x - 1
        if max_len > 0:
            if len(text) > max_len:
                text = text[:max_len]
            try:
                stdscr.addstr(y, x, text, attr)
            except curses.error:
                pass


def get_layout(text, max_width):
    lines_rendered = []
    mapping = []
    current_line = ""
    y, x = 0, 0

    for char in text:
        mapping.append((y, x))
        if char == "\n":
            lines_rendered.append(current_line)
            current_line = ""
            y += 1
            x = 0
        else:
            current_line += char
            x += 1
            if x >= max_width:
                lines_rendered.append(current_line)
                current_line = ""
                y += 1
                x = 0

    lines_rendered.append(current_line)
    mapping.append((y, x))
    return lines_rendered, mapping


def find_nearest_idx(mapping, target_y, target_x):
    best_idx = -1
    last_x_in_row = -1
    for idx, (my, mx) in enumerate(mapping):
        if my == target_y:
            best_idx = idx
            if mx == target_x or mx > target_x:
                return idx
            last_x_in_row = idx
    return last_x_in_row if best_idx != -1 else -1


def input_parrafo(stdscr, start_y, start_x, max_width, max_lines, initial_text=""):
    curses.curs_set(1)
    buffer_texto = initial_text
    cursor_idx = len(buffer_texto)
    scroll_offset = 0

    while True:
        lines_rendered, mapping = get_layout(buffer_texto, max_width)
        cy, cx = mapping[cursor_idx]

        if cy < scroll_offset:
            scroll_offset = cy
        elif cy >= scroll_offset + max_lines:
            scroll_offset = cy - max_lines + 1

        for i in range(max_lines):
            safe_addstr(stdscr, start_y + i, start_x, " " * max_width)

        for i in range(max_lines):
            line_idx = scroll_offset + i
            if line_idx < len(lines_rendered):
                safe_addstr(stdscr, start_y + i, start_x, lines_rendered[line_idx])

        screen_cy = start_y + (cy - scroll_offset)
        screen_cx = start_x + cx
        try:
            stdscr.move(screen_cy, screen_cx)
        except curses.error:
            pass
        stdscr.refresh()

        try:
            ch = stdscr.get_wch()
        except curses.error:
            continue

        if (
            ch == 27
            or ch == "\x1b"
            or ch in ("\n", "\r", 10, 13)
            or ch == curses.KEY_ENTER
        ):
            break

        elif ch == "\x0e":
            buffer_texto = buffer_texto[:cursor_idx] + "\n" + buffer_texto[cursor_idx:]
            cursor_idx += 1

        elif ch in ("\x7f", "\x08", b"\x7f", curses.KEY_BACKSPACE):
            if cursor_idx > 0:
                buffer_texto = (
                    buffer_texto[: cursor_idx - 1] + buffer_texto[cursor_idx:]
                )
                cursor_idx -= 1

        elif isinstance(ch, int):
            if ch == curses.KEY_BACKSPACE:
                if cursor_idx > 0:
                    buffer_texto = (
                        buffer_texto[: cursor_idx - 1] + buffer_texto[cursor_idx:]
                    )
                    cursor_idx -= 1
            elif ch == curses.KEY_LEFT:
                if cursor_idx > 0:
                    cursor_idx -= 1
            elif ch == curses.KEY_RIGHT:
                if cursor_idx < len(buffer_texto):
                    cursor_idx += 1
            elif ch == curses.KEY_UP:
                if cy > 0:
                    cursor_idx = find_nearest_idx(mapping, cy - 1, cx)
            elif ch == curses.KEY_DOWN:
                if cy < len(lines_rendered) - 1:
                    cursor_idx = find_nearest_idx(mapping, cy + 1, cx)

        elif isinstance(ch, str):
            if ord(ch) >= 32:
                buffer_texto = (
                    buffer_texto[:cursor_idx] + ch + buffer_texto[cursor_idx:]
                )
                cursor_idx += 1

    curses.curs_set(0)
    return buffer_texto


def tui_controller(stdscr):
    colors = init_colors()
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    available_dates = storage.get_all_dates()
    today_date = datetime.now().strftime("%d-%m-%Y")
    if today_date not in available_dates:
        available_dates.append(today_date)
    available_dates = sorted(available_dates)

    selected_date_idx = available_dates.index(today_date)
    block_idx = 0
    focus = "history"

    history_scroll = 0
    entries_scroll = 0

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        max_text_width = width - 39

        history_marker = " *" if focus == "history" else ""
        safe_addstr(stdscr, 1, 2, f"=== MERLIN ==={history_marker}", curses.A_BOLD)

        visible_history_lines = height - 4
        if selected_date_idx < history_scroll:
            history_scroll = selected_date_idx
        elif selected_date_idx >= history_scroll + visible_history_lines:
            history_scroll = selected_date_idx - visible_history_lines + 1

        for i in range(visible_history_lines):
            idx = history_scroll + i
            if idx >= len(available_dates):
                break
            date = available_dates[idx]

            if idx == selected_date_idx:
                attr = curses.A_REVERSE if focus == "history" else curses.A_UNDERLINE
                safe_addstr(stdscr, 3 + i, 2, f" > {date} < ", attr)
            else:
                safe_addstr(stdscr, 3 + i, 2, f"   {date}   ")

        for y in range(height - 1):
            safe_addstr(stdscr, y, 22, "|")

        current_date = available_dates[selected_date_idx]
        day_data = storage.load_day(current_date)
        blocks = day_data.get("blocks", [])

        if len(blocks) == 0:
            block_idx = 0
            if focus == "entries":
                focus = "history"
        elif block_idx >= len(blocks):
            block_idx = len(blocks) - 1

        entries_marker = " *" if focus == "entries" else ""
        safe_addstr(
            stdscr, 1, 25, f"Date: {current_date}{entries_marker}", curses.A_BOLD
        )

        if len(blocks) > 0 and focus == "entries":
            if block_idx < entries_scroll:
                entries_scroll = block_idx

            while True:
                sim_y = 3
                for i in range(entries_scroll, block_idx + 1):
                    clean_text, _ = parser.process_line(blocks[i]["text"])
                    lines_count = 0
                    for p in clean_text.split("\n"):
                        if max_text_width > 0:
                            if len(p) == 0:
                                lines_count += 1
                            else:
                                w = textwrap.wrap(
                                    p, width=max_text_width, break_long_words=True
                                )
                                lines_count += len(w) if w else 1
                        else:
                            lines_count += 1

                    sim_y += lines_count + 1

                if sim_y > height - 2 and entries_scroll < block_idx:
                    entries_scroll += 1
                else:
                    break
        elif focus == "history":
            entries_scroll = 0

        y_offset = 3

        for i in range(entries_scroll, len(blocks)):
            block = blocks[i]
            if y_offset >= height - 2:
                break

            clean_text, color_name = parser.process_line(block["text"])
            color_attr = colors.get(color_name, colors["white"])

            if focus == "entries" and i == block_idx:
                safe_addstr(stdscr, y_offset, 24, " >", curses.A_BLINK)

            safe_addstr(stdscr, y_offset, 27, f"[{block['hour']}] ", colors["green"])

            text_lines = []

            for paragraph in clean_text.split("\n"):
                if max_text_width > 0:
                    if len(paragraph) == 0:
                        text_lines.append("")
                    else:
                        wrapped = textwrap.wrap(
                            paragraph, width=max_text_width, break_long_words=True
                        )
                        if wrapped:
                            text_lines.extend(wrapped)
                        else:
                            text_lines.append("")
                else:
                    text_lines.append(paragraph)

            for line_idx, line_text in enumerate(text_lines):
                if y_offset >= height - 2:
                    break
                safe_addstr(stdscr, y_offset, 38, line_text, color_attr)
                if line_idx < len(text_lines) - 1:
                    y_offset += 1

            y_offset += 2

        safe_addstr(
            stdscr,
            height - 1,
            0,
            "[↑/↓]: Navigate | [TAB]: Focus | [n]: New | [e]: Edit | [x]: Delete | [q]: Quit",
            curses.A_DIM,
        )
        stdscr.refresh()

        key = stdscr.getch()

        if key == ord("q") or key == 27:
            break

        elif key == 9:  # TAB
            if len(blocks) > 0:
                focus = "entries" if focus == "history" else "history"
            else:
                focus = "history"

        elif key in [curses.KEY_UP, ord("k")]:
            if focus == "history" and selected_date_idx > 0:
                selected_date_idx -= 1
                block_idx = 0  # Reiniciamos el block al cambiar de día
                entries_scroll = 0  # Reiniciamos el scroll visual
            elif focus == "entries" and block_idx > 0:
                block_idx -= 1

        elif key in [curses.KEY_DOWN, ord("j")]:
            if focus == "history" and selected_date_idx < (len(available_dates) - 1):
                selected_date_idx += 1
                block_idx = 0  # Reiniciamos el block al cambiar de día
                entries_scroll = 0  # Reiniciamos el scroll visual
            elif focus == "entries" and block_idx < (len(blocks) - 1):
                block_idx += 1

        elif key == ord("n"):
            focus = "history"
            selected_date_idx = available_dates.index(today_date)
            start_time = datetime.now().strftime("%H:%M:%S")

            for y_clear in range(3, height - 1):
                safe_addstr(stdscr, y_clear, 24, " " * (width - 25))

            safe_addstr(
                stdscr,
                3,
                25,
                f"[{start_time}] Write:",
                curses.A_BOLD,
            )

            ancho_disponible = width - 25 - 2
            alto_disponible = height - 7

            if ancho_disponible > 0 and alto_disponible > 0:
                entered_text = input_parrafo(
                    stdscr, 5, 25, ancho_disponible, alto_disponible
                ).strip()
            else:
                entered_text = ""

            if entered_text:
                today_data = storage.load_day(today_date)
                if "blocks" not in today_data:
                    today_data["blocks"] = []
                today_data["blocks"].append({"hour": start_time, "text": entered_text})
                storage.save_day(today_date, today_data)

        elif key == ord("e"):
            if focus == "entries" and len(blocks) > 0:
                current_block = blocks[block_idx]

                for y_clear in range(3, height - 1):
                    safe_addstr(stdscr, y_clear, 24, " " * (width - 25))

                safe_addstr(
                    stdscr,
                    3,
                    25,
                    f"[{current_block['hour']}] Edit:",
                    curses.A_BOLD,
                )

                ancho_disponible = width - 25 - 2
                alto_disponible = height - 7

                if ancho_disponible > 0 and alto_disponible > 0:
                    entered_text = input_parrafo(
                        stdscr,
                        5,
                        25,
                        ancho_disponible,
                        alto_disponible,
                        initial_text=current_block["text"],
                    ).strip()
                else:
                    entered_text = ""

                if entered_text:
                    day_data = storage.load_day(current_date)
                    day_data["blocks"][block_idx]["text"] = entered_text
                    storage.save_day(current_date, day_data)

        elif key == ord("x"):
            if focus == "history":
                date_to_delete = available_dates[selected_date_idx]
                safe_addstr(
                    stdscr,
                    height - 2,
                    25,
                    f"Delete data for {date_to_delete}? (y/n): ",
                    curses.A_BOLD,
                )
                stdscr.refresh()
                confirm_key = stdscr.getch()
                if confirm_key in [ord("y"), ord("Y")]:
                    storage.delete_day(date_to_delete)
                    available_dates = storage.get_all_dates()
                    if today_date not in available_dates:
                        available_dates.append(today_date)
                    available_dates = sorted(available_dates)
                    selected_date_idx = max(0, selected_date_idx - 1)

            elif focus == "entries" and len(blocks) > 0:
                safe_addstr(
                    stdscr,
                    height - 2,
                    25,
                    "Delete this line? (y/n): ",
                    curses.A_BOLD,
                )
                stdscr.refresh()
                confirm_key = stdscr.getch()
                if confirm_key in [ord("y"), ord("Y")]:
                    storage.delete_specific_entry(current_date, block_idx)
                    block_idx = max(0, block_idx - 1)
