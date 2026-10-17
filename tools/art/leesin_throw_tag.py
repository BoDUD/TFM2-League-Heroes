#!/usr/bin/env python3
"""Lee Sin's q_throw tag: Sonic Wave's palm strike alone, for the combos (tools/kit/leesin_combos.py).

    python tools/art/leesin_throw_tag.py [--check]
    python tools/art/import_native.py --hero leesin

RQQ throws Sonic Wave at the champion his kick sends flying. The skill animation shows the palm 16 ticks in (its
frame 5), too late for the wave to catch the champion in the air; q_throw is skill frames 4-7 (the crouch, the palm,
its hold, the recovery), with the palm 4 ticks in. Writes assets/source/native/leesin_q_throw.png (those four cells
cut from leesin_skill.png), the q_throw rows of leesin_cells.json (skill's pivots and durations) and of
leesin_retouch.json (skill's face retouches), so import_native.py builds the tag like any other: its frames come out
the same as skill's. --check only compares.
"""
import argparse
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
FRAMES = [3, 4, 5, 6]          # skill's frames, from 0
TAG = "q_throw"


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def layout(n):
    """import_native's grid (tools/art/native_refs.py layout): columns x rows for n frames."""
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def strip(cells):
    """leesin_q_throw.png: the chosen cells of leesin_skill.png, in import_native's grid."""
    w, h = (v * cells["scale"] for v in cells["cell"])
    skill = Image.open(lp(os.path.join(SRC, "leesin_skill.png"))).convert("RGBA")
    cols, _ = layout(len(cells["tags"]["skill"]))
    out_cols, out_rows = layout(len(FRAMES))
    out = Image.new("RGBA", (out_cols * w, out_rows * h), (0, 0, 0, 0))
    for i, k in enumerate(FRAMES):
        x, y = k % cols * w, k // cols * h
        out.paste(skill.crop((x, y, x + w, y + h)), (i % out_cols * w, i // out_cols * h))
    return out


def cells_text(raw, cells):
    """leesin_cells.json with the q_throw line after skill's (one line per tag, as native_refs.py writes it)."""
    line = f'  "{TAG}": [' + ", ".join(json.dumps(cells["tags"]["skill"][k]) for k in FRAMES) + "],"
    rows = [r for r in raw.split("\n") if not r.startswith(f'  "{TAG}": ')]
    at = next(i for i, r in enumerate(rows) if r.startswith('  "skill": '))
    return "\n".join(rows[:at + 1] + [line] + rows[at + 1:])


def retouch_text(touch):
    frames = {}
    for tag, v in touch["frames"].items():
        if tag != TAG:
            frames[tag] = v
        if tag == "skill":
            frames[TAG] = [v[k] for k in FRAMES]
    return json.dumps({**touch, "frames": frames}, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    cells_path, touch_path = (os.path.join(SRC, f"leesin_{x}.json") for x in ("cells", "retouch"))
    png_path = os.path.join(SRC, f"leesin_{TAG}.png")
    raw = [open(lp(p), "rb").read().decode("utf-8") for p in (cells_path, touch_path)]
    nl = ["\r\n" if "\r\n" in r else "\n" for r in raw]
    raw_cells, raw_touch = (r.replace("\r\n", "\n") for r in raw)
    cells, touch = json.loads(raw_cells), json.loads(raw_touch)
    assert json.dumps(touch, indent=1) == raw_touch.rstrip("\n"), "leesin_retouch.json is not indent-1 JSON"
    new_png, new_cells, new_touch = strip(cells), cells_text(raw_cells, cells), retouch_text(touch)
    json.loads(new_cells)
    if args.check:
        same_png = os.path.exists(lp(png_path)) and \
            list(Image.open(lp(png_path)).convert("RGBA").getdata()) == list(new_png.getdata())
        ok = same_png and new_cells == raw_cells and new_touch == raw_touch.rstrip("\n")
        print(f"{TAG}:", "up to date" if ok else "OUT OF DATE")
        sys.exit(0 if ok else 1)
    new_png.save(lp(png_path))
    new_touch += "\n" if raw_touch.endswith("\n") else ""
    for path, text, end in ((cells_path, new_cells, nl[0]), (touch_path, new_touch, nl[1])):
        open(lp(path), "wb").write(text.replace("\n", end).encode("utf-8"))
    print(f"wrote leesin_{TAG}.png ({new_png.size[0]}x{new_png.size[1]}, skill frames "
          f"{', '.join(str(k + 1) for k in FRAMES)}) and its rows in leesin_cells.json, leesin_retouch.json")


if __name__ == "__main__":
    main()
