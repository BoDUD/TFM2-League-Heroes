#!/usr/bin/env python3
"""Import Ivern's effects (assets/source/ivern/PROMPTS_FX.md, 15 pictures) as the game sheets league_ivern_fx and
league_ivern_big.

    python tools/art/import_ivern_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/ivern/codex_fx/ivern_fx, Codex 2026-10-22/codex-2:
pixel_1x/ivern_fx_<name>.png, one row of equal frames each at game size, frame sizes and durations in manifest.json
(cell_1x, frame_durations_ms); alpha 0 / 255; the two projectiles drawn flying right and symmetric top to bottom, every
other one symmetric left to right - checked again here, then made an odd number of squares across the symmetric way).
Each frame is placed as the kit plays it (import_hwei_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames), "mid" (the middle of all its frames' drawn rows). The buffs
(the seed shield, the slow creepers, the bound roots, the rush whirl, the brush's leaves) and the projectiles loop; the
rest play once, timed to the kit (tools/kit/build_ivern.py): the brush over w_t (240 ticks = 4 s, Codex's own timing),
the seed shield over e_t (120 = 2 s, Codex's). Daisy's own frames (r_drop, r_punch, r_slam) are not here: they are her
dense sheets (rig_ivern.py); r_dust, r_shock and r_hit are laid under / on them there and stay in the big / small
sheets for the previews.
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
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from import_hwei_fx import anchor, lp, odd  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ivern", "codex_fx", "ivern_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"w_brush", "e_burst", "r_dust", "r_shock"}
FLYING = {"a_seed", "q_vine"}   # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
MIDDLE = (0, -7)                # vines curling round the unit
SOLES = (0, 11)                 # on the ground under a unit or a point
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def codex(name):
    """Codex's own frame durations (manifest.json frame_durations_ms) for every frame."""
    return ("codex", name)


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the attack's seed and its pop; the brush (the passive): the patch, the allies' leaves, the magic on-hit
    "a_seed": ("a_seed", "core", loop(4, 50), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    "w_hit": ("w_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    "w_brush": ("w_brush", "mid", codex("w_brush"), [SOLES]),
    "w_buff": ("w_buff", "mid", loop(4, 100), [SOLES]),
    # Triggerseed: the shield round the carrier, its burst (on the carrier or on him), the slowing creepers
    "e_seed": ("e_seed", "bottom", codex("e_seed"), [GROUND]),
    "e_burst": ("e_burst", "bottom", seq(range(7), [40, 50, 60, 70, 80, 90, 100]), [GROUND]),
    "e_slow": ("e_slow", "bottom", loop(4, 100), [GROUND]),
    # Rootcaller: the vine, its strike, the roots on the legs, the allies' rush
    "q_vine": ("q_vine", "core", loop(4, 50), [LINE]),
    "q_hit": ("q_hit", "core", seq(range(5), [40, 50, 60, 80, 100]), [MIDDLE]),
    "q_root": ("q_root", "bottom", loop(4, 100), [GROUND]),
    "q_rush": ("q_rush", "mid", loop(4, 70), [SOLES]),
    # Daisy!: the earth bursting as she rises, the slam's shockwave, a punch landing
    "r_dust": ("r_dust", "bottom", seq(range(6), [60, 70, 80, 100, 120, 140]), [GROUND]),
    "r_shock": ("r_shock", "mid", seq(range(6), [50, 60, 70, 90, 110, 130]), [SOLES]),
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
    return [odd_(c, name) for c in out]


def odd_(c, name):
    """import_hwei_fx.odd with this hero's projectiles."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man.get("effects", []):
        name = e["file"][:-4].replace("ivern_fx_", "")
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
    tables = {"league_ivern_fx": {}, "league_ivern_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if isinstance(frames, tuple) and frames[0] == "codex":
            frames = seq(range(len(cs)), meta[pic]["frame_durations_ms"])
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_ivern_big" if tag in BIG else "league_ivern_fx"][tag] = out
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
