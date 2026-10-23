#!/usr/bin/env python3
"""Import Bel'Veth's effects (assets/source/belveth/PROMPTS_FX.md, 14 pictures) as the game sheets league_belveth_fx and
league_belveth_big.

    python tools/art/import_belveth_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/belveth/codex_fx/belveth_fx, Codex 2026-10-24/new-chat:
pixel_1x/belveth_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json (a list: cell_1x,
frames, symmetry); alpha 0 / 255; the rift wave drawn flying right and symmetric top to bottom, every other one symmetric
left to right - checked again here, then made an odd number of squares across the symmetric way).
Each frame is placed as the kit plays it (import_singed_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames). The pictures round her body (the coral burst, the true
form's aura, the maelstrom) left her place clear with their ground ring at the cell's bottom: put on her claws' ground.
The lasting ones loop (tools/kit/build_belveth.py: the maelstrom e_t, the true form r_t, the frenzy p_t, the slows, the
rift wave); the rest play once.
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

SRC = os.path.join(ROOT, "assets", "source", "belveth", "codex_fx", "belveth_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"w_slam", "r_burst", "e_storm"}
FLYING = {"w_tail"}             # turned with its flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
BODY = (0, -12)                 # her body's middle (47 px from the claws to the spike tips)


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def lasting(opening, looped, closing, total):
    """An opening (frames with ms), the looped frames at their ms repeated while the total lasts, a closing: a picture
    stretched to a zone's life (total ms)."""
    head = sum(ms for _, ms in opening) + sum(ms for _, ms in closing)
    per = sum(ms for _, ms in looped)
    n = max(1, round((total - head) / per))
    return opening + looped * n + closing


T = lambda ticks: ticks * 1000 / 60     # noqa: E731

# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the wing-blade's cut (she attacks fast: a short hit)
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    # Death in Lavender: the frenzy at her feet while it lasts; the coral drawn into her body
    "p_as": ("p_as", "bottom", loop(4, 100), [GROUND]),
    "c_eat": ("c_eat", "core", seq(range(4), [80, 100, 120, 140]), [BODY]),
    # Void Surge: the launch where she starts, the cut on each one passed
    "q_dash": ("q_dash", "bottom", seq(range(4), [50, 70, 90, 110]), [GROUND]),
    "q_hit": ("q_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    # Above and Below: the slam round her, the rift wave flying, the launch under the one hit, the slow at the feet
    "w_slam": ("w_slam", "bottom", seq(range(5), [60, 80, 100, 120, 150]), [GROUND]),
    "w_tail": ("w_tail", "core", loop(4, 50), [LINE]),
    "w_hit": ("w_hit", "bottom", seq(range(4), [50, 70, 90, 110]), [GROUND]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Endless Banquet: the coral burst round her, the hit, the true form's aura behind her while it lasts
    "r_burst": ("r_burst", "bottom", seq(range(6), [70, 90, 110, 130, 150, 170]), [GROUND]),
    "r_hit": ("r_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    "r_aura": ("r_aura", "bottom", loop(4, 150), [GROUND]),
    # Royal Maelstrom: the storm round her while it lasts, the cut on the one slashed
    "e_storm": ("e_storm", "bottom", loop(6, 70), [GROUND]),
    "e_hit": ("e_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
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
        name = f[:-4].replace("belveth_fx_", "")
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
    tables = {"league_belveth_fx": {}, "league_belveth_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_belveth_big" if tag in BIG else "league_belveth_fx"][tag] = out
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
