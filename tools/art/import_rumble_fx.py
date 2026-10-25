#!/usr/bin/env python3
"""Import Rumble's effects (assets/source/rumble/PROMPTS_FX.md, 17 pictures) as the game sheets league_rumble_fx and
league_rumble_big, and write the bake that draws Flamespitter's fire into his skill frames.

    python tools/art/import_rumble_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery as tools/art/process_rumble_fx.py brought Gemini's JPGs to it
(assets/source/rumble/gemini_fx/rumble_fx: pixel_1x/rumble_fx_<name>.png, one row of equal frames each at game size,
frame sizes in manifest.json; alpha 0 / 255), with the effects tools/art/fix_rumble_fx.py redrew after League's own
look (assets/source/rumble/fx_fix/pixel_1x, read first): the harpoon flying right and symmetric top to bottom, the fire
pointing right (it is drawn into his own frames), every other one symmetric left to right - checked again here, then
made an odd number of squares across the symmetric way.
Each frame is placed as the kit plays it (import_yorick_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames), or a point (x, y) in the cell. Buffs loop while they last
(the shield, the haste, the slow, the burn, the Danger Zone's steam, Overheat's smoke), the harpoon while it flies, the
fire through the skill; a landing rocket's tag is as long as its burning zone (build_rumble.py r_t).
The fire (q_flame) is a tag only for rig_rumble.py's bake (assets/source/native/rumble_bake.json, written here): each frame
with its nozzle on the pivot, the bake moves it onto the cannon's muzzle in q_spray (MUZZLE).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from import_hwei_fx import anchor, lp  # noqa: E402
from build_rumble import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rumble", "gemini_fx", "rumble_fx")
FIX = os.path.join(ROOT, "assets", "source", "rumble", "fx_fix")      # tools/art/fix_rumble_fx.py: redrawn effects
MOD = os.path.join(ROOT, "league")
NATIVE = os.path.join(ROOT, "assets", "source", "native")

BIG = {"oh_on", "r_launch", "r_fall"}
FLYING = {"e_harpoon"}          # turned with its flight: drawn going right, symmetric top to bottom
FORWARD = {"q_flame"}           # drawn into his own frames: points right, no symmetry
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
BODY = (0, -6)                  # the middle of Rumble's mech (36 px tall, its soles 11 under the pivot)
SHOULDERS = (0, -13)            # the top of his hull, where the steam and the smoke rise from
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
NOZZLE = (0, 0)                 # the fire's nozzle on the pivot (the bake moves it onto the muzzle)
MUZZLE = (35, 3)                # the cannon's muzzle in q_spray, game px from the pivot (rig_rumble.Canvas, measured)


def seq(frames, ms):
    return list(zip(frames, ms))


def loop(n, ms):
    return seq(range(n), [ms] * n)


def over(n, ms, total):
    """n frames of ms each, looped to fill `total` ms (the last one cut)."""
    out, t, k = [], 0, 0
    while t < total:
        d = min(ms, total - t)
        out.append((k % n, d))
        t += d
        k += 1
    return out


def ms_of(ticks):
    return ticks * 1000.0 / 60.0


Q_FIRE = ms_of(P["q_t"]) - 133            # the fire from q_spray's first moment to the end of the skill (rig_rumble.MS)
R_ZONE = ms_of(P["r_t"])                  # a landing rocket's burning zone
R_HEAD = [40, 40, 60, 80, 100]            # the rocket diving, the flash, the blast, the cloud settling
R_TAIL = [160, 240]                       # the fire dying down to embers
R_LOOP = 4                                # frames 6-9 burn in a loop between them


def r_fall_frames():
    head = seq(range(5), R_HEAD)
    burn = R_ZONE - sum(R_HEAD) - sum(R_TAIL)
    mid = [(5 + k, ms) for k, ms in over(R_LOOP, 120, burn)]
    tail = seq([9, 10], R_TAIL)
    return head + mid + tail


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the ball's blow, Overheat's burning blow
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "oh_hit": ("oh_hit", "core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    # Flamespitter: the fire (baked into his skill frames), the scorch on each one burnt
    "q_flame": ("q_flame", "nozzle", over(4, 114, Q_FIRE), [NOZZLE]),
    "q_hit": ("q_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    # Electro-Harpoon: the harpoon flying, the jolt, the second harpoon's bigger blast, the slowed one crackling
    "e_harpoon": ("e_harpoon", "core", loop(4, 60), [LINE]),
    "e_hit": ("e_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "e2_hit": ("e2_hit", "core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    "e_zap": ("e_zap", "bottom", loop(4, 110), [GROUND]),
    # Scrap Shield: the shell round him, the exhaust at his feet while he is faster
    "w_shield": ("w_shield", "bottom", loop(4, 120), [GROUND]),
    "haste": ("haste", "bottom", loop(4, 100), [GROUND]),
    # the heat: the Danger Zone's vent and its steam; Overheat's blowout and its smoke
    "dz_on": ("dz_on", "core", seq(range(5), [60, 70, 90, 110, 130]), [BODY]),
    "dz_steam": ("dz_steam", "bottom", loop(4, 150), [SHOULDERS]),
    "oh_on": ("oh_on", "bottom", seq(range(6), [60, 80, 100, 140, 160, 200]), [GROUND]),
    "oh_smoke": ("oh_smoke", "bottom", loop(4, 150), [SHOULDERS]),
    # The Equalizer: the rockets off his back, each one's landing and the fire it leaves, the burn on one standing in it
    "r_launch": ("r_launch", "bottom", seq(range(5), [60, 80, 90, 110, 160]), [GROUND]),
    "r_fall": ("r_fall", "patch", r_fall_frames(), [(0, 11)]),
    "burn": ("burn", "bottom", loop(4, 100), [GROUND]),
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
        if name not in FORWARD:
            m = c[::-1] if name in FLYING else c[:, ::-1]
            if not (c == m).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd(c, name) for c in out]


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    if name in FORWARD:
        return c
    ax = 0 if name in FLYING else 1
    n = c.shape[ax]
    if n % 2:
        return c
    return np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)


def anchor_of(cs, kind):
    if kind == "nozzle":                      # the fire's root: the middle of its leftmost drawn columns
        x0 = min(int(np.nonzero(c[..., 3].any(0))[0].min()) for c in cs)
        ys = np.concatenate([np.nonzero(c[:, x0:x0 + 3, 3].any(1))[0] for c in cs])
        return [float(x0), (ys.min() + ys.max()) / 2]
    if kind == "patch":                       # a landing's burning patch: the middle of its ground ellipse (the
        h, w = cs[0].shape[:2]                # lowest 9 rows of the burning frames)
        return [(w - 1) / 2, h - 1 - 4.0]
    return anchor(cs, kind)


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man["effects"]:
        meta[e["name"]] = dict(e, pixel_1x=os.path.join("pixel_1x", e["file"]))
    fixed = os.path.join(FIX, "manifest.json")
    if os.path.isfile(lp(fixed)):                 # the redrawn ones' own sizes and frame counts
        for e in json.load(open(lp(fixed), encoding="utf-8"))["effects"]:
            meta[e["name"]] = dict(e, pixel_1x=os.path.join("pixel_1x", e["file"]))
    return meta


def write_bake():
    dx, dy = MUZZLE
    bake = {"fx": "league_rumble_fx",
            "items": [{"tag": "q_flame", "into": "skill", "at_ms": 133, "dx": dx, "dy": dy}]}
    os.makedirs(lp(NATIVE), exist_ok=True)
    with open(lp(os.path.join(NATIVE, "rumble_bake.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write('{\n  "fx": "league_rumble_fx",\n  "items": [\n')
        f.write(",\n".join("    " + json.dumps(e) for e in bake["items"]))
        f.write("\n  ]\n}\n")
    print("assets/source/native/rumble_bake.json:", len(bake["items"]), "items")


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
    tables = {"league_rumble_fx": {}, "league_rumble_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor_of(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_rumble_big" if tag in BIG else "league_rumble_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    write_bake()
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
