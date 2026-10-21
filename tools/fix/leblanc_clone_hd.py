#!/usr/bin/env python3
"""LeBlanc's passive clone drawn from her current dense idle (the user, 2026-10-21: 「妖姬有点bug吧 分身怎么不是高清帧啊 被动的」).

    python tools/fix/leblanc_clone_hd.py [--check]

Mirror Image's clone is a picture, not a unit: the view `league_leblanc_p_clone` played where she stood. Its tag
`p_clone` in league_leblanc_big was cut by tools/art/import_leblanc.py from her old 1x design (assets/source/native,
43 x 63, six frames) before her PPU 2.0 redo (#397), so it showed the old LeBlanc, and at 1x. This writes a dense effect
sheet of its own, league/effects/league_leblanc_clone (league_main hd.rs EFFECTS, PPU 2.0 like her body), and points
the view at it:
  * tag idle    = her current 1x idle (league_leblanc#sheet.png `idle`, eight breathing frames) where she stood, then
                  league_leblanc_big's blink-out column (the last five frames of the old p_clone);
  * tag hd_idle = the same at PPU 2.0: her `hd_idle` frames, the column's pixels doubled (nearest), every frame centred
                  on the pivot like its 1x frame.
The old p_clone tag stays in league_leblanc_big (no view reads it). Idempotent; --check only reports.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

PRE = chr(92) * 2 + "?" + chr(92)
LEAGUE = os.path.join(ROOT, "league")
HERO = os.path.join(LEAGUE, "champions", "league_leblanc")
BIG = os.path.join(LEAGUE, "effects", "league_leblanc_big")
OUT = os.path.join(LEAGUE, "effects", "league_leblanc_clone")
CHAMP = os.path.join(LEAGUE, "champion", "league_leblanc.data_champion")
VIEW = "league_leblanc_p_clone"
ANIM = "asset/league/effects/league_leblanc_clone"
PPU = 2
BODY_MS = 75                   # her eight idle frames over 600 ms (the old clone: six of 100 ms)
COLUMN = 5                     # the blink-out column: the old p_clone's last five frames


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def tag_frames(stem, tag):
    an = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    out = []
    for f in an[tag]["frames"]:
        b = f["data"]
        x, y, w, h = (int(round(b[k])) for k in ("x", "y", "w", "h"))
        out.append((np.asarray(sheet.crop((x, y, x + w, y + h))).copy(), round(f.get("duration", 0.1) * 1000)))
    return out


def build():
    one = [(f, BODY_MS) for f, _ in tag_frames(HERO, "idle")]
    hd = [(f, BODY_MS) for f, _ in tag_frames(HERO, "hd_idle")]
    for f, ms in tag_frames(BIG, "p_clone")[-COLUMN:]:
        one.append((f, ms))
        hd.append((np.repeat(np.repeat(f, PPU, 0), PPU, 1), ms))
    return {"idle": one, "hd_idle": hd}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tags = build()
    s = open(lp(CHAMP), encoding="utf-8-sig").read()
    d = json.loads(s)
    views = [v for v in d["view_effects"] if v["name"] == VIEW]
    if len(views) != 1:
        sys.exit(f"{VIEW}: {len(views)} views")
    v = views[0]
    print(f"{VIEW}: {v['anim']} / {v['tag']} -> {ANIM} / idle;", {t: len(f) for t, f in tags.items()})
    if a.check:
        return
    w, h = G.write_sheet(lp(OUT), tags, share=True)
    print(f"league/effects/league_leblanc_clone#sheet.png {w}x{h}")
    if (v["anim"], v["tag"]) != (ANIM, "idle"):
        old = json.dumps(v, ensure_ascii=False)
        v["anim"], v["tag"] = ANIM, "idle"
        # the file's own layout kept: only this view's two fields change
        src_view = None
        for line_start in [i for i in range(len(s)) if s.startswith('"name": "' + VIEW + '"', i)]:
            src_view = line_start
        assert src_view is not None, old
        head, tail = s[:src_view], s[src_view:]
        end = tail.index("}")
        block = tail[:end].replace('"asset/league/effects/league_leblanc_big"', '"' + ANIM + '"', 1)
        block = block.replace('"tag": "p_clone"', '"tag": "idle"', 1)
        s = head + block + tail[end:]
        assert json.loads(s) == d, "the rewrite changed more than the view"
        with open(lp(CHAMP), "w", encoding="utf-8", newline="") as f:
            f.write(s)
        print("view updated in", os.path.relpath(CHAMP, ROOT))


if __name__ == "__main__":
    main()
