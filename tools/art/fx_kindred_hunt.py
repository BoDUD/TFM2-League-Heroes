"""League's Lamb mark over the champion Kindred hunts (the add-on league_kindred 0.2.0, 2026-11-11).

    python tools/art/fx_kindred_hunt.py           # addons/league_kindred/effects/league_kindred_hunt#sheet.png / #anim.fanim
    python tools/art/fx_kindred_hunt.py --check   # (tests) the sheet is what this script draws

The user (2026-11-11): 「千珏印记是不是不能印记英雄啊 你看看 如果不能的话就要改了」. The add-on now hunts as League does
(addons/league_kindred/src/hunt.rs): it names an enemy champion, the mark arms 8 s later, a takedown on him is a mark.
The picture over the hunted champion is her own Mark of the Kindred - the swirl the main pack plays over her when she
gains one (league/effects/league_kindred_fx `p_stack`, Codex's step-3 drawing) - looped:

- `wait` - named, not armed yet: the swirl at WAIT_ALPHA, breathing (every other loop fainter);
- `on`   - the hunt is on: the swirl as drawn.

The swirl's centre sits Y game px over the champion's position (a frame is drawn with its centre on the unit), higher
than the main pack's target pips (27-40 px up), so it crosses none of them.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "league", "effects", "league_kindred_fx")
OUT = os.path.join(ROOT, "addons", "league_kindred", "effects", "league_kindred_hunt")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))

Y = 47              # the swirl's centre over the hunted champion's position
WAIT_ALPHA = 0.5    # `wait`: the swirl this opaque, and every other loop half that


def source_frames():
    """The p_stack swirl frames, each cut to its ink: [(rgba array, ms)]."""
    anims = json.load(open(SRC + "#anim.fanim", encoding="utf-8"))["anims"]
    sheet = Image.open(SRC + "#sheet.png").convert("RGBA")
    out = []
    for fr in anims["p_stack"]["frames"]:
        d = fr["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        img = sheet.crop((x, y, x + w, y + h))
        box = img.getchannel("A").getbbox()
        out.append((np.asarray(img.crop(box)), round(fr["duration"] * 1000)))
    return out


def placed(ink, y=Y):
    """The swirl in a frame whose centre is the champion: centred on x, its middle y px up."""
    ih, iw = ink.shape[:2]
    half_w = iw // 2 + 1
    w = 2 * half_w + 1
    h = 2 * (y + ih // 2 + 1) + 1
    a = np.zeros((h, w, 4), np.uint8)
    cy, cx = h // 2, half_w
    top, left = cy - y - ih // 2, cx - iw // 2
    a[top:top + ih, left:left + iw] = ink
    return a


def faded(a, k):
    b = a.copy()
    b[..., 3] = (b[..., 3].astype(np.float32) * k).round().astype(np.uint8)
    return b


def tags():
    src = source_frames()
    on = [(placed(ink), ms) for ink, ms in src]
    wait = [(faded(placed(ink), WAIT_ALPHA), ms) for ink, ms in src] + \
           [(faded(placed(ink), WAIT_ALPHA / 2), ms) for ink, ms in src]
    return {"wait": wait, "on": on}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = tags()
    if a.check:
        anims = json.load(open(OUT + "#anim.fanim", encoding="utf-8"))["anims"]
        sheet = np.asarray(Image.open(OUT + "#sheet.png").convert("RGBA"))
        for name, frames in t.items():
            got = anims.get(name, {}).get("frames", [])
            if len(got) != len(frames):
                sys.exit(f"{name}: {len(got)} frames, want {len(frames)}: python tools/art/fx_kindred_hunt.py")
            for g, (arr, ms) in zip(got, frames):
                d = g["data"]
                x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
                if not np.array_equal(sheet[y:y + h, x:x + w], arr) or abs(g["duration"] * 1000 - ms) > 0.5:
                    sys.exit(f"{name}: the sheet is not this script's drawing: python tools/art/fx_kindred_hunt.py")
        print("league_kindred_hunt: up to date")
        return
    import strips
    w, h = strips.write_sheet(OUT, t, share=True)
    print(f"wrote {os.path.relpath(OUT, ROOT)}#sheet.png ({w}x{h}), tags {', '.join(f'{k}:{len(v)}' for k, v in t.items())}")


if __name__ == "__main__":
    main()
