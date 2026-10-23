#!/usr/bin/env python3
"""Import Zac's effects (assets/source/zac/PROMPTS_FX.md, 15 pictures) as the game sheets league_zac_fx and
league_zac_big.

    python tools/art/import_zac_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/zac/codex_fx/zac_fx, Codex 2026-10-23/new-chat-5:
pixel_1x/zac_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json (cell_1x, frames,
symmetry); alpha 0 / 255; the two projectiles drawn flying right and symmetric top to bottom, every other one symmetric
left to right - checked again here, then made an odd number of squares across the symmetric way).
Each frame is placed as the kit plays it (import_ivern_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames), "mid" (the middle of all its frames' drawn rows). The three
pictures round his body (the burst, the slingshot's landing, the bounce) have his place cleared with his soles 3 squares
over the cell's bottom (Codex's HANDOFF): their middle goes that far over his soles. The buffs (the grip, the slow), the
projectiles and the lying blob loop; the rest play once, timed to the kit (tools/kit/build_zac.py): the lying blob is
stamped every 15 ticks, so its three frames are 250 ms.
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

SRC = os.path.join(ROOT, "assets", "source", "zac", "codex_fx", "zac_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"w_burst", "q_slam", "e_land", "r_land"}
FLYING = {"q_fist", "b_fly"}    # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
BODY = (0, -11)                 # the middle of his body (44 px tall: 22 over his soles, the pivot 11 over them)


def round_him(cell_h):
    """A picture round his body: his soles 3 squares over the cell's bottom, so the cell's middle is (cell_h / 2 - 3) over
    his soles - the spot of the "core" anchor."""
    return (0, 11 - (cell_h // 2 - 3))


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the punch
    "a_hit": ("a_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    # Unstable Matter: the burst round him (on his spot, not following), its hit
    "w_burst": ("w_burst", "core", seq(range(6), [40, 50, 60, 80, 100, 120]), [round_him(44)]),
    "w_hit": ("w_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    # Stretching Strikes: the rubber arm, its grab, the grip on the champion, the slam on his spot, the sticky slow
    "q_fist": ("q_fist", "core", loop(4, 50), [LINE]),
    "q_hit": ("q_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "q_held": ("q_held", "core", loop(4, 100), [HIT]),
    "q_slam": ("q_slam", "bottom", seq(range(6), [50, 60, 70, 90, 110, 130]), [GROUND]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Elastic Slingshot: the landing round him, the knock-up
    "e_land": ("e_land", "core", seq(range(6), [50, 60, 70, 90, 110, 130]), [round_him(28)]),
    "e_hit": ("e_hit", "bottom", seq(range(4), [40, 60, 80, 100]), [GROUND]),
    # Let's Bounce!: each landing round him, the knock-up
    "r_land": ("r_land", "core", seq(range(5), [40, 60, 80, 100, 120]), [round_him(24)]),
    "r_hit": ("r_hit", "bottom", seq(range(3), [50, 60, 80]), [GROUND]),
    # Cell Division: a blob thrown, lying on the ground (stamped every 15 ticks), absorbed
    "b_fly": ("b_fly", "core", loop(3, 60), [LINE]),
    "b_lie": ("b_lie", "bottom", seq(range(3), [83, 84, 83]), [GROUND]),
    "b_pick": ("b_pick", "core", seq(range(4), [50, 70, 90, 110]), [BODY]),
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
    if isinstance(man, dict):                     # this delivery: {"version", "generator", "items": [...]}
        man = man["items"]
    meta = {}
    for e in man:
        f = e.get("file") or e.get("name")
        f = os.path.basename(f) if f.endswith(".png") else f"zac_fx_{f}.png"
        name = f[:-4].replace("zac_fx_", "")
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
    tables = {"league_zac_fx": {}, "league_zac_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_zac_big" if tag in BIG else "league_zac_fx"][tag] = out
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
