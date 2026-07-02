#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tsv_diff",
        description=(
            "Visual diff for TSV files. Inputs can be file paths or git ref paths "
            "like HEAD~1:database/animeapi.tsv."
        ),
    )
    parser.add_argument("old", nargs="?", help="Old TSV path or git ref path")
    parser.add_argument("new", nargs="?", help="New TSV path or git ref path")
    parser.add_argument(
        "--key",
        default="title",
        help="Primary key column for row matching (default: title)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Max rows to show per section (default: 30, use 0 for unlimited)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )
    parser.add_argument(
        "--ignore-type-change",
        action="store_true",
        help=("Ignore type-only differences (e.g. 1 vs 1.0, true vs True, 0 vs 000)."),
    )
    parser.add_argument(
        "--more",
        action="store_true",
        help="Show all entries in a scrollable pager (less -R) and disable row limit",
    )
    return parser.parse_args()


def _supports_color(disabled: bool) -> bool:
    return not disabled and sys.stdout.isatty()


def _colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    codes = {
        "red": "31",
        "green": "32",
        "yellow": "33",
        "cyan": "36",
        "bold": "1",
        "magenta": "35",
    }
    code = codes.get(color)
    if not code:
        return text
    return f"\033[{code}m{text}\033[0m"


def _read_input(input_value: str) -> str:
    path = Path(input_value)
    if path.exists():
        return path.read_text(encoding="utf-8")

    if ":" in input_value:
        result = subprocess.run(
            ["git", "--no-pager", "show", input_value],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ValueError(
                f"Failed to read git ref path '{input_value}': {result.stderr.strip()}"
            )
        return result.stdout

    raise ValueError(f"Input not found: '{input_value}'")


def _parse_tsv(
    content: str, key_column: str
) -> tuple[list[str], dict[str, dict[str, str]]]:
    reader = csv.DictReader(content.splitlines(), delimiter="\t")
    if not reader.fieldnames:
        raise ValueError("TSV has no header")
    if key_column not in reader.fieldnames:
        raise ValueError(f"Key column '{key_column}' not found in TSV header")

    rows: dict[str, dict[str, str]] = {}
    for row in reader:
        key = (row.get(key_column) or "").strip()
        if not key:
            continue
        rows[key] = {k: (v if v is not None else "") for k, v in row.items()}
    return reader.fieldnames, rows


def _auto_resolve_inputs() -> tuple[str, str]:
    target = "database/animeapi.tsv"
    status_result = subprocess.run(
        ["git", "--no-pager", "diff", "--name-status", "--", target],
        check=False,
        capture_output=True,
        text=True,
    )
    if status_result.returncode != 0:
        raise ValueError(f"Failed to inspect git diff: {status_result.stderr.strip()}")

    staged_status_result = subprocess.run(
        ["git", "--no-pager", "diff", "--cached", "--name-status", "--", target],
        check=False,
        capture_output=True,
        text=True,
    )
    if staged_status_result.returncode != 0:
        raise ValueError(
            f"Failed to inspect staged git diff: {staged_status_result.stderr.strip()}"
        )

    status_lines = [
        line.strip()
        for line in (
            status_result.stdout + "\n" + staged_status_result.stdout
        ).splitlines()
        if line.strip()
    ]
    for line in status_lines:
        if line.startswith("D\t") and line.endswith(target):
            raise ValueError(
                f"YELL: {target} is deleted in git diff. No preview to be seen."
            )
        if line.startswith("A\t") and line.endswith(target):
            raise ValueError(
                f"YELL: {target} is newly initialized in git diff. No preview to be seen."
            )

    porcelain = subprocess.run(
        ["git", "--no-pager", "status", "--porcelain", "--", target],
        check=False,
        capture_output=True,
        text=True,
    )
    if porcelain.returncode != 0:
        raise ValueError(
            f"Failed to inspect working tree status: {porcelain.stderr.strip()}"
        )
    for line in [x for x in porcelain.stdout.splitlines() if x.strip()]:
        if line.startswith("?? "):
            raise ValueError(
                f"YELL: {target} is untracked/newly initialized. No preview to be seen."
            )

    result = subprocess.run(
        ["git", "--no-pager", "diff", "--name-only", "--", target],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(f"Failed to inspect git diff: {result.stderr.strip()}")

    changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if target not in changed:
        raise ValueError(
            f"No working-tree diff found for {target}. "
            "Pass explicit inputs or modify the file first."
        )

    return f"HEAD:{target}", target


def _changed_columns(
    old_row: dict[str, str],
    new_row: dict[str, str],
    columns: list[str],
    ignore_type_change: bool = False,
) -> list[tuple[str, str, str]]:
    changed: list[tuple[str, str, str]] = []
    for col in columns:
        old_val = old_row.get(col, "")
        new_val = new_row.get(col, "")
        if not _values_equal(old_val, new_val, ignore_type_change):
            changed.append((col, old_val, new_val))
    return changed


def _print_limited(items: list[str], limit: int) -> list[str]:
    if limit <= 0:
        return items
    return items[:limit]


def _truncate(text: str, max_len: int = 120) -> str:
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 3]}..."


def _print_table(
    headers: list[str], rows: list[list[str]], out_lines: list[str]
) -> None:
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def visible_len(text: str) -> int:
        return len(ansi_re.sub("", text))

    widths = [visible_len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], visible_len(cell))

    term_width = shutil.get_terminal_size((120, 30)).columns
    max_per_col = []
    for i, h in enumerate(headers):
        raw_h = ansi_re.sub("", h).lower()
        if raw_h == "changes":
            max_per_col.append(80)
        elif raw_h == "title":
            max_per_col.append(50)
        else:
            max_per_col.append(24)
        widths[i] = min(widths[i], max_per_col[i])

    def total_table_width(col_widths: list[int]) -> int:
        # "│ " + each col + " │" separators + ending
        return 3 + sum(col_widths) + (3 * (len(col_widths) - 1)) + 2

    while total_table_width(widths) > term_width and max(widths) > 12:
        idx = max(range(len(widths)), key=lambda x: widths[x])
        widths[idx] -= 1

    def pad_visible(text: str, width: int) -> str:
        pad = width - visible_len(text)
        if pad <= 0:
            return text
        return text + (" " * pad)

    def fmt(row: list[str]) -> str:
        return (
            "│ "
            + " │ ".join(pad_visible(cell, widths[i]) for i, cell in enumerate(row))
            + " │"
        )

    def wrap_cell(text: str, width: int) -> list[str]:
        if width <= 1:
            return [text]
        plain = ansi_re.sub("", text)
        if visible_len(text) <= width:
            return [text]
        if plain != text:
            # avoid wrapping colored inline fragments badly; fallback truncate
            return [text[: max(1, width - 1)] + "…"]
        return textwrap.wrap(
            text,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]

    top = "╭─" + "─┬─".join("─" * w for w in widths) + "─╮"
    mid = "├─" + "─┼─".join("─" * w for w in widths) + "─┤"
    bot = "╰─" + "─┴─".join("─" * w for w in widths) + "─╯"

    out_lines.append(top)
    out_lines.append(fmt(headers))
    out_lines.append(mid)
    for row in rows:
        wrapped_cols = [wrap_cell(cell, widths[i]) for i, cell in enumerate(row)]
        height = max(len(c) for c in wrapped_cols)
        for line_idx in range(height):
            row_line = [
                wrapped_cols[col_idx][line_idx]
                if line_idx < len(wrapped_cols[col_idx])
                else ""
                for col_idx in range(len(row))
            ]
            out_lines.append(fmt(row_line))
    out_lines.append(bot)


def _format_change_list(
    old_row: dict[str, str],
    new_row: dict[str, str],
    columns: list[str],
    use_color: bool,
    ignore_type_change: bool = False,
) -> tuple[int, str]:
    changes = _changed_columns(old_row, new_row, columns, ignore_type_change)
    shown = changes[:4]
    segments = [
        (
            f"{_colorize(col, 'yellow', use_color)}: "
            f"{_colorize(repr(old), 'red', use_color)} -> "
            f"{_colorize(repr(new), 'green', use_color)}"
        )
        for col, old, new in shown
    ]
    compact = ", ".join(segments)
    if len(changes) > len(shown):
        compact += f", ... (+{len(changes) - len(shown)} more)"
    return len(changes), compact


_NULL_LIKE = {"", "null", "none", "nil", "nan"}
_BOOL_TRUE = {"true", "1"}
_BOOL_FALSE = {"false", "0"}
_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)$")


def _coerce_loose(value: str) -> object:
    s = value.strip()
    low = s.lower()

    if low in _NULL_LIKE:
        return None
    if low in _BOOL_TRUE:
        return True
    if low in _BOOL_FALSE:
        return False
    if _INT_RE.match(s):
        try:
            return int(s)
        except ValueError:
            return s
    if _FLOAT_RE.match(s):
        try:
            return float(s)
        except ValueError:
            return s
    return s


def _values_equal(old_val: str, new_val: str, ignore_type_change: bool) -> bool:
    if old_val == new_val:
        return True
    if not ignore_type_change:
        return False
    old_coerced = _coerce_loose(old_val)
    new_coerced = _coerce_loose(new_val)

    if old_coerced == new_coerced:
        return True

    # Treat null-like and zero-like as equal in type-ignoring mode.
    # This suppresses churn such as "0" -> "" from normalization changes.
    if {old_coerced, new_coerced} in ({None, 0}, {None, False}):
        return True

    return False


def main() -> int:
    args = _parse_args()
    use_color = _supports_color(args.no_color)

    if (args.old and not args.new) or (args.new and not args.old):
        print(
            "Error: Provide both 'old' and 'new', or provide neither.", file=sys.stderr
        )
        return 1

    if args.old and args.new:
        old_input, new_input = args.old, args.new
    else:
        try:
            old_input, new_input = _auto_resolve_inputs()
            print(
                f"{_colorize('Auto mode', 'cyan', use_color)}: "
                f"{old_input} -> {new_input}"
            )
        except ValueError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1

    try:
        old_content = _read_input(old_input)
        new_content = _read_input(new_input)
        old_cols, old_rows = _parse_tsv(old_content, args.key)
        new_cols, new_rows = _parse_tsv(new_content, args.key)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    all_cols = sorted(set(old_cols) | set(new_cols), key=lambda x: (x != args.key, x))
    old_keys = set(old_rows.keys())
    new_keys = set(new_rows.keys())

    added = sorted(new_keys - old_keys, key=str.casefold)
    removed = sorted(old_keys - new_keys, key=str.casefold)
    common = sorted(old_keys & new_keys, key=str.casefold)

    changed_keys: list[str] = []
    for key in common:
        if _changed_columns(
            old_rows[key], new_rows[key], all_cols, args.ignore_type_change
        ):
            changed_keys.append(key)

    if args.more:
        args.limit = 0

    out_lines: list[str] = []
    out_lines.append(_colorize("TSV diff summary", "bold", use_color))
    _print_table(
        [
            _colorize("metric", "magenta", use_color),
            _colorize("count", "magenta", use_color),
        ],
        [
            ["added", _colorize(str(len(added)), "green", use_color)],
            ["removed", _colorize(str(len(removed)), "red", use_color)],
            ["changed", _colorize(str(len(changed_keys)), "yellow", use_color)],
        ],
        out_lines,
    )

    if added:
        out_lines.append(f"\n{_colorize('Added rows', 'green', use_color)}")
        shown = _print_limited(added, args.limit)
        _print_table(
            [_colorize("title", "magenta", use_color)],
            [[key] for key in shown],
            out_lines,
        )
        if args.limit > 0 and len(added) > len(shown):
            out_lines.append(f"... ({len(added) - len(shown)} more)")

    if removed:
        out_lines.append(f"\n{_colorize('Removed rows', 'red', use_color)}")
        shown = _print_limited(removed, args.limit)
        _print_table(
            [_colorize("title", "magenta", use_color)],
            [[key] for key in shown],
            out_lines,
        )
        if args.limit > 0 and len(removed) > len(shown):
            out_lines.append(f"... ({len(removed) - len(shown)} more)")

    if changed_keys:
        out_lines.append(f"\n{_colorize('Changed rows', 'yellow', use_color)}")
        shown = _print_limited(changed_keys, args.limit)
        changed_rows: list[list[str]] = []
        for key in shown:
            change_count, change_text = _format_change_list(
                old_rows[key],
                new_rows[key],
                all_cols,
                use_color,
                args.ignore_type_change,
            )
            changed_rows.append(
                [
                    _colorize(key, "cyan", use_color),
                    _colorize(str(change_count), "yellow", use_color),
                    change_text,
                ]
            )
        _print_table(
            [
                _colorize("title", "magenta", use_color),
                _colorize("cols", "magenta", use_color),
                _colorize("changes", "magenta", use_color),
            ],
            changed_rows,
            out_lines,
        )
        if args.limit > 0 and len(changed_keys) > len(shown):
            out_lines.append(
                f"\n... ({len(changed_keys) - len(shown)} more changed rows)"
            )

    if not added and not removed and not changed_keys:
        out_lines.append(_colorize("\nNo differences found.", "cyan", use_color))

    output = "\n".join(out_lines)
    if args.more:
        pager = os.environ.get("PAGER", "less -R")
        proc = subprocess.run(
            pager,
            input=output,
            text=True,
            shell=True,
            check=False,
        )
        if proc.returncode != 0:
            print(output)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
