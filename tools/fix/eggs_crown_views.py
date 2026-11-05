#!/usr/bin/env python3
"""The Queen of the Freljord's ice crown in the three queens' `view_buffs` (league_eggs, 2026-11-05).

    python -X utf8 tools/fix/eggs_crown_views.py [--check] [files ...]

addons/league_eggs hangs `league_eggs_crown_<queen>` on the winner of the War for the Freljord (Ashe, Sejuani,
Lissandra: the first of them to kill or help kill a rival queen once the match has 20 kills + assists) for the rest of
the match. A buff's picture shows only when the champion's own data names the buff in `view_buffs`, so each queen
carries

    {"type": "Animated", "name": "league_eggs_crown_<queen>", "anim": "asset/league/effects/league_eggs_crown_1x",
     "tag": "<queen>", "repeat": true, "z": 4}

(the sheet: addons/league_eggs/make_fx.py --out league/effects/league_eggs_crown_1x - one tag a queen, a plain 1x sheet
the game draws itself, not registered in league.dll's hd.rs).

  league_sejuani     generated: tools/kit/build_sejuani.py carries the entry (its add-on copy, addons/league_sejuani,
                     from addons/league_sejuani/make_override.py) - only checked here
  league_ashe        hand-kept (no tools/kit generator)
  league_lissandra   generated, then baked (CasterAnimation / view entries, tools/fix/arm_refund_read.py): a rebuild
                     would not reproduce the shipped file; build_lissandra.py carries the entry too, for the next one
This script appends the entry to `view_buffs` of the files a rebuild does not reproduce and of their add-on copies
(addons/league_lowhp's Lissandra, which addons/league_lowhp/make_override.py makes from the main pack: its --check
stays "up to date"), and replaces an entry of that name that differs. Idempotent; --check: exit 1 while an entry is
missing or differs (Sejuani's two files included). With file paths as arguments it patches those files instead (the
queen read from the file's "id").
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANIM = "asset/league/effects/league_eggs_crown_1x"
# file -> patched here (True) or made by a kit and only checked (False)
FILES = {
    "league/champion/league_ashe.data_champion": True,
    "league/champion/league_lissandra.data_champion": True,
    "addons/league_lowhp/override/league_lissandra.data_champion": True,
    "league/champion/league_sejuani.data_champion": False,
    "addons/league_sejuani/override/league_sejuani.data_champion": False,
}
QUEENS = ("ashe", "sejuani", "lissandra")


def lp(path):
    path = os.path.abspath(path)
    pre = "\\\\?\\"
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def entry(queen):
    return {"type": "Animated", "name": f"league_eggs_crown_{queen}", "anim": ANIM, "tag": queen, "repeat": True,
            "z": 4}


def dumps(d, nl):
    return json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl


def place(d, queen):
    """The crown entry in d's view_buffs: 'ok', 'added' or 'replaced' (d changed in place)."""
    want = entry(queen)
    views = d.setdefault("view_buffs", [])
    for i, v in enumerate(views):
        if isinstance(v, dict) and v.get("name") == want["name"]:
            if v == want:
                return "ok"
            views[i] = want
            return "replaced"
    views.append(want)
    return "added"


def shown(path):
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:          # another drive
        return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("files", nargs="*", help="data files to patch instead of the list above")
    a = ap.parse_args()
    todo, stale_kit = [], []
    files = {os.path.abspath(f): True for f in a.files} if a.files else {os.path.join(ROOT, f): w for f, w in FILES.items()}
    for path, writable in files.items():
        rel = shown(path)
        with open(lp(path), "rb") as f:
            raw = f.read()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        nl = "\r\n" if "\r\n" in text else "\n"
        d = json.loads(text)
        queen = d.get("id", "").removeprefix("league_")
        if queen not in QUEENS:
            sys.exit(f"{rel}: id {d.get('id')!r} is none of the queens {QUEENS}")
        if dumps(d, nl) != text:
            sys.exit(f"{rel}: not in json.dumps(indent=2) form - patching would rewrite the whole file; look at it")
        state = place(d, queen)
        if state == "ok":
            print(f"{rel}: league_eggs_crown_{queen} in view_buffs")
            continue
        todo.append(rel)
        if not writable:
            stale_kit.append(rel)
        if a.check or not writable:
            print(f"{rel}: league_eggs_crown_{queen} {'missing' if state == 'added' else 'differs'}"
                  + ("" if writable else " - rebuild it from its kit (tools/kit/build_sejuani.py, then the add-on's "
                                         "make_override.py)"))
            continue
        with open(lp(path), "wb") as f:
            f.write((b"\xef\xbb\xbf" if bom else b"") + dumps(d, nl).encode("utf-8"))
        print(f"{rel}: league_eggs_crown_{queen} {state}")
    sys.exit(1 if (todo if a.check else stale_kit) else 0)


if __name__ == "__main__":
    main()
