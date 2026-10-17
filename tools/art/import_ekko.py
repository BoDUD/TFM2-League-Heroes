#!/usr/bin/env python3
"""Import Ekko's effects (assets/source/ekko/PROMPTS.md, 1-14) as game sheets, and build Chronobreak's hologram.

    python tools/art/import_ekko.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_ekko.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py. Codex's strips come back as raw
image-generator output (soft alpha, antialiased colours, canvases of their own size) with a manifest.json that
gives every frame's rectangle in the source (`assets[].frames[].rect`, [x, y, width, height] or {x, y, w, h}).
--raw turns every frame into a cell of a native strip like import_malphite.py (every game pixel one flat 8x8
block, binary alpha, 16 colours by median cut, each game pixel the majority colour of the source pixels it
covers, opaque when a third of them are) and writes assets/source/ekko/ekko_fx_<name>.png plus
ekko_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the widest
drawing becomes the hit 14 px, Z-Drive Resonance's ring 24 px, the Timewinder device with its trail 16 px, its
field 44 px (radius 22000), the Phase Dive afterimage 28 px, its strike 28 px, Parallel Convergence's forming
rings and its dome 80 px (radius 40000), the detonation 90 px, the stun clock 16 px, the shield bubble 44 px
round his 36 px crouch, Chronobreak's vanishing boy 32 px tall (his own height, not the ring's width), its arrival rings 70 px (radius 35000) and its hits 22 px.
Each frame sits in its cell on an anchor: the device on its core (a few px behind its nose, the projectile's
hitbox); the hits and bursts on their cell's middle; the afterimage and the vanish on the ground row they stand
on; the ground rings on the ellipse's middle, at the share of the canvas height the prompt asked for.

The second step places every cell by its anchor: the device flies with its core on the projectile; hits on the
body; the ground rings on the ground under the unit (11 px below the pivot); the stun clock over the head; the
shield round his body. Chronobreak's hologram (r_ghost, 4 s where he cast it) is Ekko's front view
(assets/source/red_side/ekko_front.png: it faces no way, as nothing mirrors it) in the mint of League's rewind skin,
with scan lines and two glitch frames. No palette or outline pass on the sheets. Writes league/effects/league_ekko_fx (hit, q_hit, z_proc,
q_device, e_dash, e_hit, w_stun, w_shield, r_hit) and league/effects/league_ekko_big (q_field, w_forming,
w_sphere, w_shatter, r_ghost, r_depart, r_arrive).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import tfm2_ase as T  # noqa: E402
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ekko")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
CHEST = (0, -4)
BODY = (0, -6)                         # the middle of a 34 px hero
EKKO = (3, -5)                         # the middle of his crouch (he leans forward)
HEAD = (0, -26)                        # over a head, under the Sunlight-style marks' 30

# raw strip -> native: name: (frames, size in game px, measured on "w" (widest drawing) or "h" (tallest),
#                             x anchor, y anchor, x offset in game px)
#   x: "nose" the drawing's right edge, "cell" the middle of its rectangle
#   y: "strip" the middle of all the strip's drawings, "ground" the lowest row of its drawings, "widest" the
#      row where the drawings are widest (an ellipse's centre; the median over the frames), or a share of the
#      rectangle's height
RAW = {
    "hit": (5, 14, "w", "cell", "strip", 0),
    "z_proc": (6, 24, "w", "cell", "strip", 0),
    "q_device": (4, 16, "w", "nose", "strip", -4),
    "q_field": (6, 44, "w", "cell", "widest", 0),
    "e_dash": (5, 28, "w", "cell", "ground", 0),
    "e_hit": (6, 28, "w", "cell", "strip", 0),
    "w_forming": (10, 80, "w", "cell", "widest", 0),
    "w_sphere": (4, 80, "w", "cell", "widest", 0),
    "w_shatter": (7, 90, "w", "cell", "widest", 0),
    "w_stun": (6, 16, "w", "cell", "strip", 0),
    "w_shield": (4, 44, "w", "cell", "strip", 0),
    "r_depart": (6, 32, "h", "cell", "ground", 0),
    "r_arrive": (8, 70, "w", "cell", "widest", 0),
    "r_hit": (5, 22, "w", "cell", "strip", 0),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        data = json.load(f)
    return {os.path.basename(a["file"]): a for a in data["assets"]}


def rect(fr):
    r = fr.get("rect", fr.get("source_rect"))
    if isinstance(r, dict):
        return [int(r["x"]), int(r["y"]), int(r.get("w", r.get("width"))), int(r.get("h", r.get("height")))]
    return [int(v) for v in r]


def from_raw(folder):
    manifest = load_manifest(folder)
    anchors = {}
    for name, (n, size, measure, xr, yr, xoff) in RAW.items():
        fn = f"ekko_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        if not (a[..., 3] < 255).any():             # delivered on black: alpha from the brightness
            a[..., 3] = np.clip(a[..., :3].max(-1).astype(int) * 3, 0, 255)
        solid = a[..., 3] >= 100
        pal = palette(a)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - pal[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        frames = manifest[fn]["frames"]
        if len(frames) != n:
            sys.exit(f"{fn}: the manifest lists {len(frames)} frames, not {n}")
        rects = [rect(f) for f in frames]
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        extent = max((b[1] - b[0]) if measure == "w" else (b[3] - b[2]) for b in boxes)
        s = size / extent
        rows = (min(b[2] for b in boxes), max(b[3] for b in boxes))
        if yr == "widest":                           # each frame's widest row, the median over the strip
            wide = []
            for (x, y, w, h), box in zip(rects, boxes):
                spans = [np.nonzero(solid[r, x:x + w])[0] for r in range(box[2], box[3])]
                widths = [sp[-1] - sp[0] + 1 if len(sp) else 0 for sp in spans]
                wide.append(box[2] + int(np.argmax(widths)))
            mid_row = float(np.median(wide))
        anchor = []
        for (x, y, w, h), box in zip(rects, boxes):
            ax = (box[1] if xr == "nose" else x + w / 2) + xoff / s
            if yr == "strip":
                ay = (rows[0] + rows[1]) / 2
            elif yr == "ground":
                ay = rows[1] - 1
            elif yr == "widest":
                ay = mid_row
            else:
                ay = y + yr * h
            anchor.append((ax, ay))
        left = max(ax - b[0] for b, (ax, _) in zip(boxes, anchor))
        right = max(b[1] - ax for b, (ax, _) in zip(boxes, anchor))
        up = max(ay - b[2] for b, (_, ay) in zip(boxes, anchor))
        down = max(b[3] - ay for b, (_, ay) in zip(boxes, anchor))
        L = R = max(math.ceil(left * s), math.ceil(right * s)) + 1
        U = D = max(math.ceil(up * s), math.ceil(down * s)) + 1
        tw, th = L + R, U + D
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anchor)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U) / s))
                sy1 = max(int(math.floor(ay + (r + 1 - U) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)             # this frame's rows only
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L) / s))
                    sx1 = max(int(math.floor(ax + (c + 1 - L) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)         # and columns
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({size} px over {extent} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "ekko_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"ekko_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"ekko_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# League's rewind skin, light to dark (Ekko_Base_R_RewindSkin): the hologram's four tones by brightness
MINT = [(0xD8, 0xFF, 0xF0), (0x9C, 0xE8, 0xD0), (0x5C, 0xC4, 0xAC), (0x3A, 0x8C, 0x7E)]
GHOST_ALPHA, SCAN_ALPHA = 200, 130


# Ekko from the front (Codex, 2026-10-06; assets/source/red_side/PROMPTS.md): 8x blocks on a 56 x 56 canvas, the
# soles on row 46, the middle on column 28. The client never mirrors an effect picture, so the hologram made from his
# side-on idle faced right on the red side too; a front view faces no way.
FRONT = os.path.join(ROOT, "assets", "source", "red_side", "ekko_front.png")
FRONT_SOLES, FRONT_MID = 46, 28


def front():
    """The front view at game size, centred on his pivot (the soles 11 rows under it)."""
    a = np.asarray(Image.open(G.lp(FRONT)).convert("RGBA"))[4::8, 4::8].copy()
    py, px = FRONT_SOLES - 11, FRONT_MID
    hh = max(py, a.shape[0] - 1 - py)
    hw = max(px, a.shape[1] - 1 - px)
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    out[hh - py:hh - py + a.shape[0], hw - px:hw - px + a.shape[1]] = a
    return out


def hologram():
    """Ekko's front view (front()) in the rewind skin's mint: each pixel by its brightness (the outline the darkest),
    every third row a dimmer scan line; 8 x 500 ms, the third and sixth frames glitching (a band of rows slid a pixel
    sideways). Until 2026-10-06 it was his side-on idle, which faced right on the red side."""
    f = front()
    on = f[..., 3] > 0
    lum = (0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]) / 255.0
    cuts = np.quantile(lum[on], [0.75, 0.45, 0.2])
    tone = np.where(lum >= cuts[0], 0, np.where(lum >= cuts[1], 1, np.where(lum >= cuts[2], 2, 3)))
    base = np.zeros_like(f)
    for k, c in enumerate(MINT):
        m = on & (tone == k)
        base[m, :3] = c
    base[on, 3] = GHOST_ALPHA
    ys = np.nonzero(on.any(1))[0]
    scan = np.zeros(on.shape, bool)
    scan[ys[0]::3] = True
    base[on & scan, 3] = SCAN_ALPHA
    out = []
    for k in range(8):
        g = base.copy()
        if k in (2, 5):
            band = slice(ys[0] + (4 if k == 2 else 12), ys[0] + (8 if k == 2 else 16))
            g[band] = np.roll(g[band], 1 if k == 2 else -1, axis=1)
        out.append(g)
    return out


# sprite: {tag: (frames, spot of the anchor from the pivot, ms per frame, times played)}
FX = {
    "league_ekko_fx": {
        "hit": (5, CHEST, [50] * 5, 1),
        "q_hit": ("hit", CHEST, [50] * 5, 1),
        "z_proc": (6, BODY, [50] * 6, 1),
        "q_device": (4, (0, 0), [60] * 4, 1),
        "e_dash": (5, FEET, [60] * 5, 1),
        "e_hit": (6, BODY, [50] * 6, 1),
        "w_stun": (6, HEAD, [83] * 6, 2),
        "w_shield": (4, EKKO, [100] * 4, 1),
        "r_hit": (5, BODY, [60] * 5, 1),
    },
    "league_ekko_big": {
        "q_field": (6, FEET, [125] * 6, 1),
        "w_forming": (10, FEET, [150] * 10, 1),
        "w_sphere": (4, FEET, [62, 63, 62, 63], 1),
        "w_shatter": (7, FEET, [60] * 7, 1),
        "r_depart": (6, FEET, [60] * 6, 1),
        "r_arrive": (8, FEET, [70] * 8, 1),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "ekko_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (n, (sx, sy), ms, times) in tags.items():
            src = n if isinstance(n, str) else tag
            count = len(ms)
            ax, ay = anchors[src]["anchor"]
            out[tag] = [(G.centre_frame(f, sx - ax, sy - ay), m) for f, m in list(zip(cells(src, count), ms)) * times]
        sheets[sprite] = out
    ghost = hologram()
    h, w = ghost[0].shape[:2]
    sheets["league_ekko_big"]["r_ghost"] = [(G.centre_frame(g, -(w // 2), -(h // 2)), 500) for g in ghost]
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
