"""The parts of tft_scuttlecrab GPT's 85 % shrink missed (PR #784, 29929a743 「缩小迅捷蟹」; the user, 2026-11-19, on the
UI frames left big: 「这个缩」).

GPT's commit drew the crab's hd_ frames (the battlefield's, assets/source/ppu/scuttlecrab_*.png) and 1x frames at about
85 % and wrote its idle reel from the smaller idle frame, but left
- idle_base / hd_idle_base - hero_reels.py's frame 0, which every later run starts from, and the frame illaoi_souls.py
  takes the crab's spirit from - pointing at the old, bigger idle frame: the ban/pick card (hd_bp) was the old crab;
- every lo_ frame (the UI's: the pick slot, the pick moment, the encyclopedia ...) at the old size.
This points idle_base / hd_idle_base at the idle's frame 0 as GPT drew it (the same rect, no pixel moved) and makes every
lo_ frame again from its hd_ frame the way tools/art/ppu_hd.py's add_lo does (sheetkit.lo_of, a replica: on the crab's
frames before GPT's commit it gives all 30 lo_ frames exactly), lo_idle_base from the idle's hd frame 0; a frame that no
longer fits its rect gets one of its own below the sheet. Then run hero_reels.py --hero scuttlecrab (the reels' rects)
and illaoi_souls.py.

    python tools/fix/gpt784_review/scuttlecrab_shrink_rest.py            # write
    python tools/fix/gpt784_review/scuttlecrab_shrink_rest.py --check    # exit 1 when not done
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

REELS = ("idle", "bp", "idle_base")       # hero_reels.py's tags: rects of the others' frames


def main():
    check = "--check" in sys.argv[1:]
    k = Kit(REPO, "tft", "scuttlecrab")
    todo = []
    for pre in ("", "hd_"):
        base, idle = k.anims[pre + "idle_base"]["frames"], k.anims[pre + "idle"]["frames"]
        if len(base) != 1:
            sys.exit(f"{pre}idle_base: {len(base)} frames, this tool knows the crab's single one")
        if base[0]["data"] != idle[0]["data"]:
            todo.append(pre + "idle_base")
            base[0]["data"] = dict(idle[0]["data"])
    jobs = [(t, i, t, i) for t in k.anims if not t.startswith(("hd_", "lo_")) and t not in REELS
            for i in range(len(k.anims[t]["frames"]))]
    jobs.append(("idle_base", 0, "idle", 0))              # lo_idle_base from the idle's frame 0
    stale = 0
    for t, i, src, j in jobs:
        want = k.lo_of(k.cell(src, j).shape, k.cell("hd_" + src, j))
        have = k.cell("lo_" + t, i)
        if have.shape == want.shape and (have == want).all():
            continue
        stale += 1
        k.put("lo_" + t, i, want)
    if stale:
        todo.append(f"{stale} lo_ frames")
    if check:
        print("tft_scuttlecrab: " + ("idle_base and lo_ frames as GPT's shrink wants" if not todo else "not done: " + ", ".join(todo)))
        sys.exit(1 if todo else 0)
    if todo:
        k.save()
    print("tft_scuttlecrab: " + ("wrote " + ", ".join(todo) if todo else "already done"))


if __name__ == "__main__":
    main()
