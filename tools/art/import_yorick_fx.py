#!/usr/bin/env python3
"""Import Yorick's effects (assets/source/yorick/PROMPTS_FX.md, 18 pictures) as the game sheets league_yorick_fx and
league_yorick_big.

    python tools/art/import_yorick_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/yorick/codex_fx/yorick_fx, Codex 2026-10-25/new-chat:
pixel_1x/yorick_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json (a list: cell_1x,
frames, symmetry); alpha 0 / 255; the mist globule drawn flying right and symmetric top to bottom, every other one
symmetric left to right (k_bite and e_mist redrawn by tools/art/fix_yorick_fx.py into assets/source/yorick/fx_fix,
read first) - checked again here, then made an odd number of squares across the symmetric way).
Each frame is placed as the kit plays it (import_sejuani_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames). The walkers' swarm and the Maiden loop a second (the kit's
AddCasted plays them every 60 ticks while they last: tools/kit/build_yorick.py k_swarm, r_maiden), the mark and the slow
loop while their buffs last, the mist globule while it flies; the rest play once.
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

SRC = os.path.join(ROOT, "assets", "source", "yorick", "codex_fx", "yorick_fx")
MOD = os.path.join(ROOT, "league")
FIX = os.path.join(ROOT, "assets", "source", "yorick", "fx_fix")   # tools/art/fix_yorick_fx.py: k_bite, e_mist redrawn

BIG = {"w_wall", "e_cloud", "r_spawn", "r_maiden"}
FLYING = {"e_mist"}             # turned with its flight: drawn going right, symmetric top to bottom
ROUND = set()
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
OVER = (0, -28)                 # over a unit's head
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
FEETRING = (0, 11)              # the middle of a ring drawn round a unit's feet
MAIDEN = (0, 0)                 # her lowest row 12 px over the ground: she hovers, her veil and claw crown above the unit


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the shovel blow, Last Rites' heavy blow, the grave it digs (on the ground, left behind)
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "q_hit": ("q_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT]),
    "q_grave": ("q_grave", "bottom", seq(range(6), [60, 70, 80, 120, 150, 300]), [GROUND]),
    # the Mist Walkers: clawing up round the unit, gnawing at it (a second, again and again while they last), a bite, the
    # pounce on a champion marked by the mist
    "k_spawn": ("k_spawn", "bottom", seq(range(6), [60, 60, 70, 80, 90, 100]), [GROUND]),
    "k_swarm": ("k_swarm", "bottom", loop(6, 167), [GROUND]),
    "k_bite": ("k_bite", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "k_leap": ("k_leap", "core", seq(range(4), [50, 60, 70, 90]), [HIT]),
    # Dark Procession (the Awakening's cage): the ring of spirits round the unit, the hands on a caged champion's feet
    "w_wall": ("w_wall", "bottom", seq(range(8), [70, 80, 100, 110, 200, 200, 150, 100]), [(0, 15)]),
    "w_hit": ("w_hit", "bottom", seq(range(4), [80, 100, 400, 420]), [GROUND]),
    # Mourning Mist: the globule flying, its splash on the ground, the burst on each one hit; the mark and the slow
    "e_mist": ("e_mist", "core", loop(4, 60), [LINE]),
    "e_cloud": ("e_cloud", "core", seq(range(6), [60, 70, 90, 110, 120, 130]), [FEETRING]),
    "e_hit": ("e_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "e_mark": ("e_mark", "bottom", loop(4, 150), [OVER]),
    "slow": ("e_slow", "bottom", loop(4, 110), [GROUND]),
    # Eulogy of the Isles: the Maiden rising behind the champion, hovering over it (a second, again while she stands),
    # her claw, his bonus hit on it
    "r_spawn": ("r_spawn", "bottom", seq(range(7), [70, 80, 90, 100, 110, 120, 150]), [MAIDEN]),
    "r_maiden": ("r_maiden", "bottom", loop(6, 167), [MAIDEN]),
    "r_claw": ("r_claw", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "r_mark": ("r_mark", "core", seq(range(3), [40, 60, 80]), [HIT]),
}


def cells(name, meta, src):
    fixed = os.path.join(FIX, meta["pixel_1x"])
    a = np.asarray(Image.open(lp(fixed if os.path.isfile(fixed) else os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        m = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == m).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd_(c, name) for c in out]


def odd_(c, name):
    """import_hwei_fx.odd with this hero's projectile."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    if isinstance(man, dict):                     # a delivery shaped {"schema_version", ..., "effects": [...]}
        man = man.get("effects") or man.get("items")
    meta = {}
    for e in man:
        f = os.path.basename(e["file"])
        name = f[:-4].replace("yorick_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join("pixel_1x", f))
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
    tables = {"league_yorick_fx": {}, "league_yorick_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_yorick_big" if tag in BIG else "league_yorick_fx"][tag] = out
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
