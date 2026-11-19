"""league_chogath's run (the user, 2026-11-19, on GPT's redraw: 「大虫子跑步有问题吧节奏这么快？」): GPT's 8 run frames
are two bodies in turn - frames 1, 3, 5, 7 low and leaning forward, frames 0, 2, 4, 6 reared up with the dark neck over
the back (the source panel's separate poses) - so every 0.09 s the body flipped between them: four bounces in a 0.72 s
loop. The run is now the four low frames alone (one body, the legs one cycle), 0.2 s each (0.8 s a loop): the 1x, hd_
and lo_ tags take those frames' own rects (no pixel drawn); the hd strips hold the four.

    python tools/fix/gpt784_review/chogath_run.py [--check]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
STEM = os.path.join(ROOT, "league", "champions", "league_chogath")
KEEP = [1, 3, 5, 7]
SECS = 0.2


def main():
    doc = json.loads(open(STEM + "#anim.fanim", "rb").read().decode("utf-8-sig"))
    an = doc["anims"]
    if "--check" in sys.argv:
        ok = all(len(an[p + "run"]["frames"]) == len(KEEP) and all(abs(f["duration"] - SECS) < 1e-9 for f in an[p + "run"]["frames"])
                 for p in ("", "hd_", "lo_"))
        print("chogath run: OK" if ok else "chogath run: not as this tool leaves it")
        sys.exit(0 if ok else 1)
    if len(an["run"]["frames"]) != 8:
        sys.exit("the run is not GPT's 8 frames any more")
    for p in ("", "hd_", "lo_"):
        fr = an[p + "run"]["frames"]
        an[p + "run"]["frames"] = [{"duration": SECS, "data": dict(fr[i]["data"])} for i in KEEP]
    open(STEM + "#anim.fanim", "wb").write(json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    sheet = np.asarray(Image.open(STEM + "#sheet.png").convert("RGBA"))
    pics = []
    for f in an["hd_run"]["frames"]:
        d = f["data"]
        x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
        pics.append(sheet[y:y + h, x:x + w])
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + len(pics) - 1
    st = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        st[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1] + 1
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        js = os.path.join(d, "chogath_run.json")
        meta = json.load(open(js))
        meta["sizes"] = [[p.shape[1], p.shape[0]] for p in pics]
        Image.fromarray(st).save(os.path.join(d, "chogath_run.png"))
        json.dump(meta, open(js, "w"))
    print(f"chogath run: frames {KEEP}, {SECS} s each")


if __name__ == "__main__":
    main()
