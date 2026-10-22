#!/usr/bin/env python3
"""Import Hwei's effects (assets/source/hwei/PROMPTS_FX.md, 24 pictures) as the game sheets league_hwei_fx and
league_hwei_big.

    python tools/art/import_hwei_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/hwei/codex_fx/hwei_fx: pixel_1x/hwei_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the four projectiles drawn flying right
and symmetric top to bottom, every other one symmetric left to right - checked again here, then made an odd number of
squares across the symmetric way). The user had Gemini draw 22 of them (JPGs, 2026-10-22), brought to that delivery by
tools/art/process_hwei_fx.py, which draws the two Gemini left out (r_paint, r_canvas). Each frame is placed as the kit
plays it (import_shyvana_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under
it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle), ("feet", r) (r rows above
the cell's bottom), "bottom" (the lowest drawn row of all its frames), "mid" (the middle of all its frames' drawn rows),
"mid0" (of the first frame's: q_e_lava's flames rise over its oval later). The eye over a rooted head (e_w_open) opens
where Gaze of the Abyss's beam then starts (e_w_hit's eye, measured on its first frame). The buffs (the seal, the bound,
the haste, the slow) and the projectiles loop; the rest play once, timed to the kit (tools/kit/build_hwei.py): the
bolt's tell over q_w_at (45 ticks), the eye over e_w_setup (39), the jaws over e_e_at (30), the lava field over q_e_t
(150), the canvas over r_t (180, the burst at its end).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hwei", "codex_fx", "hwei_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"p_burst", "q_w_hit", "q_e_lava", "w_pool", "r_canvas", "r_burst"}
FLYING = {"a_ink", "q_q_ball", "e_q_face", "r_paint"}   # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
CHEST = (0, -12)                # Grim Visage's face before the chest
MIDDLE = (0, -7)                # the jaws round the unit
SOLES = (0, 11)                 # on the ground under a unit or a point
GROUND = (0, 12)                # a picture's lowest row on the ground line
OVER = (0, -26)                 # the bolt's cloud: its lowest row just over a 36 px unit's head (its top at -25)
LINE = (0, 0)                   # a projectile's point
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots); spot "eye" = where e_w_hit's eye is
FX = {
    # the attack's ink, its splash; the signature under a signed champion and its burst
    "a_ink": ("a_ink", "core", loop(4, 50), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(2), [50, 70]), [HIT]),
    "p_mark": ("p_mark", "mid", loop(6, 100), [SOLES]),
    "p_burst": ("p_burst", "bottom", seq(range(7), [50, 60, 60, 70, 80, 90, 100]), [GROUND]),
    # Subject: Disaster - the fireball and its burst, the bolt's tell and the bolt, the lava field; the slow (a buff)
    "q_q_ball": ("q_q_ball", "core", loop(4, 50), [LINE]),
    "q_q_hit": ("q_q_hit", "core", seq(range(5), [40, 50, 60, 80, 100]), [HIT]),
    "q_w_tell": ("q_w_tell", "bottom", loop(6, 125), [OVER]),
    "q_w_hit": ("q_w_hit", "bottom", seq(range(6), [40, 50, 60, 80, 100, 120]), [GROUND]),
    "q_e_lava": ("q_e_lava", "mid0", seq(range(13), [80, 90, 110, 140] + [230] * 5 + [250] * 3 + [180]), [SOLES]),
    "slow": ("slow", "bottom", loop(4, 100), [GROUND]),
    # Subject: Torment - the visage's streak and face, the eye opening and its gaze, the bound legs, the jaws
    "e_q_face": ("e_q_face", "core", loop(4, 50), [LINE]),
    "e_q_hit": ("e_q_hit", "core", seq(range(6), [50, 60, 70, 80, 90, 100]), [CHEST]),
    "e_w_open": ("e_w_open", "mid", loop(8, 81), ["eye"]),
    "e_w_hit": ("e_w_hit", "bottom", seq(range(5), [50, 60, 80, 100, 120]), [GROUND]),
    "e_bound": ("e_bound", "bottom", loop(4, 100), [GROUND]),
    "e_e_open": ("e_e_open", "core", loop(6, 83), [MIDDLE]),
    "e_e_hit": ("e_e_hit", "core", seq(range(5), [40, 50, 70, 90, 110]), [MIDDLE]),
    # Serenity (the passive): the pool under him, the allies' shields, his haste (a buff)
    "w_pool": ("w_pool", "mid", seq(range(6), [60, 80, 100, 120, 140, 160]), [SOLES]),
    "w_shield": ("w_shield", "bottom", seq(range(5), [60, 80, 100, 120, 140]), [GROUND]),
    "w_haste": ("w_haste", "mid", loop(6, 70), [SOLES]),
    # Spiraling Despair: the paint bolt, the canvas, its burst, the hit on the units in it
    "r_paint": ("r_paint", "core", loop(4, 50), [LINE]),
    "r_canvas": ("r_canvas", ("feet", 9), seq(range(14), [100] * 6 + [300] * 8), [SOLES]),
    "r_burst": ("r_burst", "bottom", seq(range(6), [50, 60, 70, 80, 100, 120]), [GROUND]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
}


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
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
    return [odd(c, name) for c in out]


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    ax = 0 if name in FLYING else 1
    n = c.shape[ax]
    if n % 2:
        return c
    return np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)


def rows_drawn(cs):
    ys = np.concatenate([np.nonzero(c[..., 3].any(1))[0] for c in cs])
    return ys.min(), ys.max()


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    x = (w - 1) / 2
    if kind == "core":
        return [x, (h - 1) / 2]
    if kind == "bottom":
        return [x, float(rows_drawn(cs)[1])]
    if kind == "mid":
        y0, y1 = rows_drawn(cs)
        return [x, (y0 + y1) / 2]
    if kind == "mid0":
        y0, y1 = rows_drawn(cs[:1])
        return [x, (y0 + y1) / 2]
    return [x, h - 1 - kind[1]]


def eye_spot(cs, anc, spot):
    """Where e_w_hit's eye is when its anchor sits on `spot`: the middle of the topmost blob of its first frame."""
    lbl, n = ndimage.label(cs[0][..., 3] > 0, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lbl)
    top = min(objs, key=lambda o: o[0].start)
    cy = (top[0].start + top[0].stop - 1) / 2
    return (0, spot[1] - (anc[1] - cy))


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man.get("effects", []):
        name = e["name"].replace("hwei_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join("pixel_1x", e["file"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="the delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest(a.src)
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n], a.src) for n in pics}
    w_hit = FX["e_w_hit"]
    eye = eye_spot(allc["e_w_hit"], anchor(allc["e_w_hit"], w_hit[1]), w_hit[3][0])
    print("e_w_open's eye on", eye)
    tables = {"league_hwei_fx": {}, "league_hwei_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        spots = [eye if s == "eye" else s for s in spots]
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_hwei_big" if tag in BIG else "league_hwei_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name in sorted(allc):
            cs = allc[name]
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
        sheet = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
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
