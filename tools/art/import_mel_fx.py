#!/usr/bin/env python3
"""Import Mel's effects (assets/source/mel/PROMPTS_FX.md, 18 pictures) as the game sheets league_mel_fx and league_mel_big.

    python tools/art/import_mel_fx.py [--review out.png]

The source is the step-3 delivery (assets/source/mel/codex_fx/mel_fx: pixel_1x/mel_fx_<name>.png, one row of equal frames
each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255). The bolts and the orb are projectiles
(the game turns them to their flight: flying left they turn upside down, so they must be symmetric top to bottom); every
other picture is symmetric left to right (the client never mirrors it on the red side) - both checked again here. Each
frame is cut by the manifest's frame size and placed as the kit plays it (import_zoe_fx.py's way): spots are game px
from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Mel's own pictures are centred
on her standing point (HER_X: symmetric for the red side). Times from the kit (build_mel.P, 60 ticks a second).
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
from build_mel import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "mel", "codex_fx", "mel_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bolt", "p_bolt", "e_orb"}           # projectiles: turned to their flight by the game
BIG = {"q_volley", "e_orb", "r_cast", "r_hit", "w_on", "x_hit"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head
FLIGHT = (0, 0)                 # a projectile's own point
HER_X = 0                       # her own pictures: centred on her standing point
WAIST = (HER_X, -2)             # her waist (13 px over her soles)
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    "a_bolt": ("core", loop(3, 60), [FLIGHT]),
    "p_bolt": ("core", loop(3, 60), [FLIGHT]),
    "a_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "p_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "p_3": ("core", loop(4, 120), [WAIST]),
    "p_6": ("core", loop(4, 120), [WAIST]),
    "p_9": ("core", loop(4, 120), [WAIST]),
    # Q's volley from its release on the target's spot: the first pair lands as the lob does (q_fly ticks), then a pair a
    # burst (q_gap ticks); the ground ellipse's middle 6 squares over the cell's bottom row
    "q_volley": (("feet", 6), seq(range(8), [round(P["q_fly"] * MS / 2)] * 2 + [round(P["q_gap"] * MS)] * 5 + [120]),
                 [SOLES]),
    "q_hit": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "e_orb": ("core", loop(4, 80), [FLIGHT]),
    # the root lasts e_root ticks (looped while the buff holds); the lower ring 4 squares over the cell's bottom row
    "e_bound": (("feet", 4), loop(4, 100), [SOLES]),
    "e_slow": (("feet", 3), loop(4, 110), [SOLES]),
    "e_burn": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    # the eclipse over her: the cell's bottom on her soles (its centre 14 squares under the cell's top)
    "r_cast": (("feet", 0), seq(range(8), [60, 60, 70, 70, 80, 80, 90, 100]), [(HER_X, 11)]),
    # the sky beam: its foot on the struck champion's soles
    "r_hit": (("feet", 0), seq(range(6), [40, 60, 80, 80, 90, 100]), [SOLES]),
    # the barrier's open bottom on her soles (a buff: looped while it holds)
    "w_on": (("feet", 0), loop(4, 100), [(HER_X, 11)]),
    "m_mark": ("core", loop(4, 120), [OVERHEAD]),
    "x_hit": (("feet", 0), seq(range(6), [60, 60, 70, 80, 90, 100]), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    if name in TB:
        out = [fold(c) for c in out]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in TB else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def fold(c):
    """A projectile made symmetric top to bottom (the game turns it to its flight, so flying left it is drawn upside
    down): each row and its mirror row both get the squares either one has (the upper row's where both have one).
    Codex drew the bolts pointing right but not mirrored (2026-10-20)."""
    out = c.copy()
    h = c.shape[0]
    for y in range(h // 2 + 1):
        m = h - 1 - y
        row = np.where(c[y][:, 3:] > 0, c[y], c[m])
        out[y] = row
        out[m] = row
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
    for e in (man if isinstance(man, list) else man.get("effects") or man["entries"]):
        # the delivery's manifest: "effects" (or "entries"), each with file (mel_fx_<name>.png), frames and cell_1x
        name = e.get("name") or e.get("id") or os.path.basename(e["file"])[len("mel_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", os.path.basename(e["file"])))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_mel_fx": {}, "league_mel_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_mel_big" if name in BIG else "league_mel_fx"][name] = out
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
