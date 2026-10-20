#!/usr/bin/env python3
"""Import Warwick's effects (assets/source/warwick/PROMPTS_FX.md, 10 pictures) as the game sheets league_warwick_fx and
league_warwick_big.

    python tools/art/import_warwick_fx.py [--review out.png]

The source is the step-3 delivery (assets/source/warwick/codex_fx/warwick_fx: Gemini's ten pictures brought to the
game's size by tools/art/process_warwick_fx.py - pixel_1x/warwick_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255; every picture
symmetric left to right - checked again here). Each frame is cut by the manifest's frame size and placed as the kit
plays it (import_zoe_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it,
a point's ground too. Warwick's own pictures are centred on his standing point (HIM_X: symmetric for the red side).
Times from the kit (build_warwick.P, 60 ticks a second).
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
from build_warwick import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "warwick", "codex_fx", "warwick_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = set()                      # no projectile pictures: every strike of his is a hidden homing strike
BIG = {"e_howl", "e_guard"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head
# his own pictures are centred on his standing point, not on his hunched body 4 px ahead of it nor his head 6 px ahead:
# the client never mirrors an effect picture, so one set off his pivot would sit on the wrong side of him facing left
# (the red side; lint_mod.py's "front and a back" check)
HIM_X = 0
HIS_HEAD = (0, -28)             # over his own head (his ear tips 39 px over his soles)
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 90]), [HIT]),
    # the heal's ellipse middle 4 squares over the cell's bottom row, on the ground under him
    "q_heal": (("feet", 4), seq(range(5), [70, 80, 90, 100, 110]), [(HIM_X, 11)]),
    # the guard's dome: its open bottom on the cell's bottom row, on the ground round him (a buff: looped)
    "e_guard": (("feet", 0), loop(4, 120), [(HIM_X, 11)]),
    # the howl's ring: its ellipse middle 3 squares over the cell's middle - 18.5 rows over the bottom row of its 32
    "e_howl": (("feet", 18.5), seq(range(6), [50, 60, 70, 80, 90, 100]), [(HIM_X, 11)]),
    "e_roar": (("feet", 0), seq(range(6), [50, 60, 60, 70, 80, 80]), [HIS_HEAD]),
    # the fear lasts e_fear ticks: six frames over it
    "e_fear": ("core", loop(6, round(P["e_fear"] * MS / 6)), [OVERHEAD]),
    # the suppression lasts r_sup ticks: eight frames over it; the shackle's cell bottom on the champion's soles
    "r_bind": (("feet", 0), loop(8, round(P["r_sup"] * MS / 8)), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    # the Blood Hunt under him: the ellipse middle 6 squares over the cell's bottom row (a buff: looped)
    "w_hunt": (("feet", 6), loop(4, 110), [(HIM_X, 11)]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in TB else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
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
    meta = {}
    for e in man.get("effects") or man["entries"]:
        # Codex's manifest: "effects" (or "entries"), each with file (warwick_fx_<name>.png), frames and cell_1x
        name = e.get("name") or e.get("id") or os.path.basename(e["file"])[len("warwick_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", os.path.basename(e["file"])))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_warwick_fx": {}, "league_warwick_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_warwick_big" if name in BIG else "league_warwick_fx"][name] = out
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
