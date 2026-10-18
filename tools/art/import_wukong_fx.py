#!/usr/bin/env python3
"""Import Wukong's effects (assets/source/wukong/PROMPTS_FX.md, 14 pictures) as the game sheets league_wukong_fx and
league_wukong_big.

    python tools/art/import_wukong_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/wukong/codex_fx: pixel_1x/wukong_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's effects (cell_1x); alpha 0 / 255; symmetric left to right -
checked again here; no flying picture). Each frame is cut by the manifest's frame size and placed as the kit plays it
(import_maokai_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a
point's ground too (the clone stands on W's anchor point). Times from the kit (build_wukong.P, 60 ticks a second): the
clone's three pictures fill one w_slot (20 ticks) each, the cloud the E's 300 ms.
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
from build_wukong import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "wukong", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"e_cloud", "e_land", "w_poof", "w_clone", "w_clone_atk", "w_clone_spin", "r_on"}
FLYING = set()
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


SLOT = P["w_slot"] * MS         # one clone picture: a slot of W's clone (20 ticks)
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Crushing Blow: the thrust's hit and the armour break over the target's head (a buff)
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_shred": (("feet", 0), loop(4, 130), [SOLES]),
    # Nimbus Strike: the cloud under him through the dash (a caster picture, P e_dur), the landing, the images' strikes
    "e_cloud": (("feet", 8), seq(range(5), [50, 60, 60, 60, P["e_dur"] * MS - 230]), [SOLES]),
    "e_land": (("feet", 6), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    # Warrior Trickster: the poof where he vanishes; the clone on the anchor, one slot a picture; its taps
    "w_poof": (("feet", 4), seq(range(5), [50, 60, 70, 80, 100]), [SOLES]),
    "w_clone": (("feet", 1), loop(4, SLOT / 4), [SOLES]),
    "w_clone_atk": (("feet", 1), loop(4, SLOT / 4), [SOLES]),
    "w_clone_spin": (("feet", 1), loop(4, SLOT / 4), [SOLES]),
    "w_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Cyclone: the whirl round him while he spins (a buff, looped), its hits
    "r_on": (("feet", 4), loop(4, 60), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Stone Skin at five stacks (a buff, looped)
    "p_stone": (("feet", 4), loop(4, 150), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {os.path.basename(e.get("file", e.get("pixel_1x", "")))[len("wukong_fx_"):-4]: e for e in man["effects"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_wukong_fx": {}, "league_wukong_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_wukong_big" if name in BIG else "league_wukong_fx"][name] = out
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
