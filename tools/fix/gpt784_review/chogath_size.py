"""league_chogath back to the user's 「38 像素」 after GPT's full redraw (#784, 2026-11-19), his drawing kept as drawn:
GPT's frames stand 58 dense rows spikes to soles at his PPU 1.2 (48 game px; rig_chogath.py's were 46 rows, 38 px).
league.dll draws him at 79 % (addons/league_main/src/hd.rs SIZES) about his position, so his feet would float; here:

1. every dense frame's picture moves DROP rows down inside its frame (Zaahen's drop: the frame keeps its size; every
   frame has >= DROP clear rows under it) - each rect once, so a rect two tags share moves once;
2. every lo_ frame is ppu_hd.add_lo's computation again (the replica in tools/fix/xinzhao_galio_1119/sheetkit.py) from
   the moved hd_ frame, his SIZES now in it (UI_PPU x 0.79 / 1.2 = 0.99: pixelated, no longer grown x 1.25); a lo_
   frame of a new size goes in a rect of its own below the sheet;
3. the hd strips (assets/source/ppu[/orig]/chogath_<tag>.png + .json sizes) rewritten from the moved hd_ frames (the
   idle's strip, chogath_idle.png, holds the idle_base frames as for the other heroes).
The 1x frames stay (the game's own frames: no SIZES there, as for every hero in that table). The idle / bp reels are
hero_reels.py's to write afterwards; champion_view's face point goes to 79 % about the soles by hand.

    python tools/fix/gpt784_review/chogath_size.py            # once (moves the pictures again on a second run)
    python tools/fix/gpt784_review/chogath_size.py --check    # lo_ = add_lo(hd_), strips = hd_
"""
import os
import sys

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

DROP = 4
REELS = ("idle", "bp")


def plain_tags(k):
    return [t for t in k.anims if not t.startswith(("hd_", "lo_")) and t not in REELS]


def strip_name(t):
    """the strip a tag's dense frames are kept in: idle_base's is the idle's"""
    return "idle" if t == "idle_base" else t


def check(k):
    from PIL import Image
    bad = 0
    for t in plain_tags(k):
        n = len(k.anims[t]["frames"])
        for i in range(n):
            hd = k.cell("hd_" + t, i)
            if not np.array_equal(k.lo_of(k.cell(t, i).shape[:2], hd), k.cell("lo_" + t, i)):
                bad += 1
        pics = [k.cell("hd_" + t, i) for i in range(n)]
        for sub in ("", "orig"):
            png = os.path.join(ROOT, "assets", "source", "ppu", sub, f"chogath_{strip_name(t)}.png")
            st = np.asarray(Image.open(png).convert("RGBA"))
            x = 0
            for p in pics:
                if not np.array_equal(st[:p.shape[0], x:x + p.shape[1]], p):
                    bad += 1
                x += p.shape[1] + 1
    return bad


def write_strip(k, t):
    """Kit.strip under the strip's own name (idle_base -> chogath_idle)"""
    import json
    from PIL import Image
    n = len(k.anims["hd_" + t]["frames"])
    pics = [k.cell("hd_" + t, i) for i in range(n)]
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + len(pics) - 1
    st = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        st[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1] + 1
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        js = os.path.join(d, f"chogath_{strip_name(t)}.json")
        meta = json.load(open(js))
        meta["sizes"] = [[p.shape[1], p.shape[0]] for p in pics]
        Image.fromarray(st).save(os.path.join(d, f"chogath_{strip_name(t)}.png"))
        json.dump(meta, open(js, "w"))


def main():
    k = Kit(ROOT, "league", "chogath")
    if abs(k.size - 0.79) > 1e-6:
        sys.exit(f"hd.rs SIZES has league_chogath at {k.size}, not 0.79")
    if "--check" in sys.argv:
        bad = check(k)
        print("chogath size: OK" if not bad else f"chogath size: {bad} frames / strip cells not as this tool leaves them")
        sys.exit(1 if bad else 0)
    # 1. each dense rect once
    seen = set()
    for t in k.anims:
        if not t.startswith("hd_"):
            continue
        for i in range(len(k.anims[t]["frames"])):
            r = k.rect(t, i)
            if r in seen:
                continue
            seen.add(r)
            x, y, w, h = r
            cell = k.sheet[y:y + h, x:x + w].copy()
            rows = np.nonzero((cell[..., 3] > 0).any(1))[0]
            if len(rows) and h - 1 - rows.max() < DROP:
                sys.exit(f"{t}[{i}]: only {h - 1 - rows.max()} clear rows under the picture")
            moved = np.zeros_like(cell)
            moved[DROP:] = cell[:h - DROP]
            k.sheet[y:y + h, x:x + w] = moved
    print(f"{len(seen)} dense rects moved {DROP} rows down")
    # 2. lo_ again from the moved hd_ frames
    for t in plain_tags(k):
        for i in range(len(k.anims[t]["frames"])):
            lo = k.lo_of(k.cell(t, i).shape[:2], k.cell("hd_" + t, i))
            k.put("lo_" + t, i, lo)
    k.save()
    # 3. strips
    for t in plain_tags(k):
        write_strip(k, t)
    print("lo_ frames and strips written; now hero_reels.py --hero chogath")


if __name__ == "__main__":
    main()
