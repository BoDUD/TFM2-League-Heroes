#!/usr/bin/env python3
"""Import Rek'Sai's effects (assets/source/reksai/PROMPTS_FX.md, 18 pictures) as the game sheets league_reksai_fx and
league_reksai_big.

    python tools/art/import_reksai_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/reksai/codex_fx: pixel_1x/reksai_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's entries (frame_size_1x); alpha 0 / 255, the red side's symmetry
already exact - checked again here - and no dark outline round the light). Each frame is cut by the manifest's frame
size and placed as the kit plays it (import_urgot_fx.py's way): spots are game px from the pivot (x forward, y down); a
unit's soles are 11 under it, a point's ground too. Times from the kit (build_reksai.P, 60 ticks a second).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from build_reksai import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "reksai", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SYM = {"q2_shot": "tb"}            # every other one "lr"
BIG = {"w_dig", "w_burst", "r_dive", "r_burst", "r_hit"}
HIT = (0, -14)                     # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                    # on the ground under a unit or a point
HEAD = (0, -38)                    # over a champion's head
CREST = (1, -24)                   # on her crest's tip (37 px from the claws, the pivot 11.5 over them)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # Prey Seeker's burst flies its line (64000 at 9000 a tick), turned to its way
    "q2_shot": ("core", flight(4, 30, max(120.0, P["q2_len"] / P["q2_speed"] * MS), lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "e_hit": ("core", seq(range(5), [40, 50, 60, 80, 90]), [HIT]),
    "q2_hit": ("core", seq(range(5), [40, 50, 70, 90, 100]), [HIT]),
    "r_hit": ("core", seq(range(6), [40, 60, 80, 90, 100, 120]), [HIT]),
    # on the ground where she stands (late caster pictures, not following: symmetric, the red side's rule)
    "q2_cast": (("feet", 4), seq(range(4), [50, 60, 80, 100]), [SOLES]),
    "w_dig": (("feet", 3), seq(range(5), [50, 60, 80, 100, 160]), [SOLES]),
    "w_burst": (("feet", 5), seq(range(6), [40, 60, 80, 90, 100, 110]), [SOLES]),
    # the hole she goes into for Void Rush stays open while she is under (r_hide ticks)
    "r_dive": (("feet", 6), seq(range(6), [80, 100, 160, P["r_hide"] * MS - 80 - 100 - 160 - 200 - 120, 200, 120]),
               [SOLES]),
    "r_burst": (("feet", 4), seq(range(5), [40, 60, 80, 100, 120]), [SOLES]),
    # under the champion she knocks up, for the knock-up (w_up ticks)
    "w_up": (("feet", 2), seq(range(5), [P["w_up"] * MS / 5] * 5), [SOLES]),
    "w_heal": (("feet", 0), seq(range(6), [70, 80, 90, 100, 110, 120]), [SOLES]),
    # the add-on's tunnels: an entrance replayed every 24 ticks (400 ms), one caving in
    "e_tunnel": ("core", seq(range(4), [100] * 4), [SOLES]),
    "e_break": (("feet", 3), seq(range(5), [60, 80, 100, 120, 160]), [SOLES]),
    # buffs (looped while they last)
    "p_full": (("feet", 0), seq(range(4), [100] * 4), [CREST]),
    "q_buff": ("core", seq(range(4), [100] * 4), [SOLES]),
    "r_mark": ("core", seq(range(4), [120] * 4), [HEAD]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["frame_size_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} frames of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    sym = SYM.get(name, "lr")
    for k, c in enumerate(out):
        ok = (c == c[:, ::-1]).all() if sym == "lr" else (c == c[::-1]).all()
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {sym}")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest():
    m = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    out = {}
    for e in m["entries"]:
        name = e["file"][len("reksai_fx_"):-len(".png")]
        out[name] = e
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest()
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    for n, (kind, frames, _) in FX.items():
        if len(allc[n]) != len({k for k, _ in frames if k != EMPTY}):
            sys.exit(f"{n}: {len(allc[n])} frames delivered, the timing uses {len({k for k, _ in frames if k != EMPTY})}")
    tables = {"league_reksai_fx": {}, "league_reksai_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_reksai_big" if name in BIG else "league_reksai_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in allc.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        Ht = sum(r.height + 10 for _, r in rows)
        sheet = Image.new("RGB", (W, Ht), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
