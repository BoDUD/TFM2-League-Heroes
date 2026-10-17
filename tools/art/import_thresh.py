#!/usr/bin/env python3
"""Import Thresh's effects (assets/source/thresh/PROMPTS.md, 1-14) as game sheets.

    python tools/art/import_thresh.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_thresh.py                                   # native strips -> effect sheets

The body comes from tools/art/restyle_native.py and tools/art/import_native.py (his head is drawn and pasted).
Codex's fourteen strips came back as raw image-generator output with real alpha (2172 x 724 and similar
canvases) and a manifest.json giving every frame's rectangle in the source (`assets[].frames[].rect`,
[x, y, width, height], one band of rows per strip). --raw turns every frame into a cell of a native strip the
way tools/art/import_yone.py does (every game pixel one flat 8x8 block, binary alpha, 16 colours by median cut,
each game pixel the majority colour of the source pixels it covers, opaque when a third of them are, the anchor
on the middle of a game pixel). The pictures that fly (the lash, the hook out and back, the lantern) are turned
to their direction by the game, so they are made exactly symmetric about their middle row (the upper half
mirrored down); Codex's upright lantern is first laid on its side (lay(): turned a quarter, ring toward its
trail), or it would fly upside down to the left. Writes assets/source/thresh/thresh_fx_<name>.png plus
thresh_fx_anchors.json.
One scale per strip, set by the kit (1000 distance units a pixel) and measured on the drawings: the lash 16 px
and the empowered one 22 px from tail to blade, the hook's blade 20 px tall (both ways), the lantern with its
trail 24 px, the hits 14-24 px, the chains round a hooked champion 22 px wide, the lantern's shield 42 px tall
(round his 39 px), Flay's sweep 66 px wide (its circle has a radius of 32000), the Box 84 px wide (radius 40000,
the walls standing on its rim; its ground squeezed from Codex's 1.6:1 toward the game's 2:1), the shackles at a
slowed champion's feet 24 px.

The second step places every cell by its anchor. The lash and the hook ride on their projectiles with the blade
at the front (the anchor a few pixels behind the tip, where the projectile's circle is), the lantern with its
body on the projectile. The hook's chain is drawn here link by link (chain()): a picture has one length, and
Codex's 48 px chain stuck out behind Thresh as the hook left his hand, so the chain grows with the throw (hook())
and shrinks as the hook comes back with the dragged champion (pull()), the frames timed to the flight. On the
units: the hits and the chains on the body; the shield standing on the ground under the unit; the shackles on
the ground at its feet. Flay's sweep is a caster view (mirrored when he faces left) centred on his feet; the Box
lies on the ground where he stood, its pentagon's middle on his feet. The Box plays 5 s in one Animation: three
frames rising, the four standing ones ten times, three shattering.
No palette or outline pass on the sheets. Writes league/effects/league_thresh_fx (lash, lash_flay, hit,
flay_hit, q_hook, q_return, q_hit, w_lantern, w_shield, e_hit, r_hit, r_slow) and
league/effects/league_thresh_big (e_sweep, r_box).
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
from import_leona import palette  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "thresh")
MOD = os.path.join(ROOT, "league")
Z = 8
FEET = (0, 11)
BODY = (0, -6)                         # the middle of a 34 px hero
HIT = (0, -8)                          # a hit on the upper body

# raw strip -> native: name: dict(n frames, size in game px, measure "w" (widest drawing) or "h" (tallest),
#   x anchor, y anchor, mirror)
#   x: "cell" the middle of the frame's rectangle; ("nose", px) the drawing's right edge plus px game pixels;
#      ("tail", px) the drawing's left edge plus px; ("frame", k) the middle of frame k's drawing
#   y: "strip" the middle of all the strip's drawings; ("bottom", px) the lowest drawn row plus px game pixels;
#      ("frame", k) the middle of frame k's drawing
RAW = {
    "lash": dict(n=4, size=16, measure="w", x=("nose", -3), y="strip", mirror=True),
    "lash_flay": dict(n=4, size=22, measure="w", x=("nose", -4), y="strip", mirror=True),
    "hit": dict(n=5, size=14, measure="w", x="cell", y="strip"),
    "flay_hit": dict(n=6, size=22, measure="w", x="cell", y="strip"),
    "q_hook": dict(n=4, size=20, measure="h", x=("nose", -5), y="strip", mirror=True),
    "q_return": dict(n=4, size=20, measure="h", x=("tail", 4), y="strip", mirror=True),
    "q_hit": dict(n=8, size=22, measure="w", x="cell", y="strip"),
    "w_lantern": dict(n=4, size=24, measure="w", x=("nose", -5), y="strip", lay=True, mirror=True),
    "w_shield": dict(n=6, size=42, measure="h", x="cell", y=("bottom", -1)),
    "e_sweep": dict(n=7, size=66, measure="w", x="cell", y="strip"),
    "e_hit": dict(n=5, size=20, measure="w", x="cell", y="strip"),
    # the ground squeezed from Codex's 1.6:1 toward the game's 2:1 (sy); a pentagon's middle lies below its box's
    "r_box": dict(n=10, size=84, measure="w", x=("frame", 0), y=("frame", 0), sy=0.8, ady=2),
    "r_hit": dict(n=6, size=24, measure="w", x="cell", y="strip"),
    "r_slow": dict(n=4, size=24, measure="w", x="cell", y=("bottom", -3)),
}


def load_manifest(folder):
    with open(os.path.join(folder, "manifest.json"), encoding="utf-8-sig") as f:
        return {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}


def rect(fr):
    r = fr.get("rect", fr.get("source_rect"))
    if isinstance(r, dict):
        return [int(r["x"]), int(r["y"]), int(r.get("w", r.get("width"))), int(r.get("h", r.get("height")))]
    return [int(v) for v in r]


def x_anchor(how, k, rects, boxes, s):
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2
    kind, arg = how
    if kind == "nose":
        return boxes[k][1] + arg / s
    if kind == "tail":
        return boxes[k][0] + arg / s
    if kind == "frame":                     # frame arg's drawing middle, at the same place in every rectangle
        return x + ((boxes[arg][0] + boxes[arg][1]) / 2 - rects[arg][0])
    raise ValueError(how)


def y_anchor(how, k, rects, boxes, rows, s):
    x, y, w, h = rects[k]
    if how == "strip":
        return (rows[0] + rows[1]) / 2
    kind, arg = how
    if kind == "bottom":
        return rows[1] + arg / s
    if kind == "frame":
        return y + ((boxes[arg][2] + boxes[arg][3]) / 2 - rects[arg][1])
    raise ValueError(how)


def lay(cell, L, U):
    """The lantern turned on its side, ring toward the trail. A projectile's picture is turned to its direction, so
    Codex's upright lantern (a cage with a roof and a ring on top) would fly upside down to the left; lying along
    the flight it is the same picture every way. The lantern (the box round its grey-brown metal, the glow inside
    it included) is turned a quarter to the left and set on the anchor, the trail behind it moved onto the middle
    row; the halo round the rest of the upright lantern is left out."""
    rgb = cell[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    metal = (cell[..., 3] > 0) & (mx < 0.8) & (mx - mn < 0.35 * np.maximum(mx, 1e-6))
    ys, xs = np.nonzero(metal)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    body = np.rot90(cell[y0:y1, x0:x1].copy(), 1)          # top -> left
    trail = cell[:, :x0].copy()
    cell[:] = 0
    rows = np.nonzero(trail[..., 3].any(1))[0]
    if len(rows):
        dy = U - (rows.min() + rows.max()) // 2
        for r in range(trail.shape[0]):
            if 0 <= r + dy < cell.shape[0]:
                cell[r + dy, :x0] = trail[r]
    bh, bw = body.shape[:2]
    top, left = U - bh // 2, L - bw // 2
    m = body[..., 3] > 0
    cell[top:top + bh, left:left + bw][m] = body[m]


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "thresh_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        n = spec["n"]
        fn = f"thresh_fx_{name}.png"
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
        ext = (lambda b: b[1] - b[0]) if spec["measure"] == "w" else (lambda b: b[3] - b[2])
        extent = max(ext(b) for b in boxes)
        s = spec["size"] / extent
        sv = s * spec.get("sy", 1.0)                # the vertical scale (the Box's ground squeezed to 2:1)
        # the rows the drawings use, counted inside each frame's own rectangle (the bands are equal)
        rows_rel = (min(b[2] - r[1] for b, r in zip(boxes, rects)), max(b[3] - r[1] for b, r in zip(boxes, rects)))
        anchor = []
        for k, ((x, y, w, h), box) in enumerate(zip(rects, boxes)):
            rows = (y + rows_rel[0], y + rows_rel[1])
            anchor.append((x_anchor(spec["x"], k, rects, boxes, s),
                           y_anchor(spec["y"], k, rects, boxes, rows, sv) + spec.get("ady", 0) / sv))
        # the anchor is the middle of pixel (L, U); the cell is 2L+1 x 2U+1
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for b, (ax, _) in zip(boxes, anchor)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for b, (_, ay) in zip(boxes, anchor)) * sv - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * n, 4), np.uint8)
        for k, ((x, y, w, h), (ax, ay)) in enumerate(zip(rects, anchor)):
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / sv))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / sv)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)             # this frame's rows only
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)         # and columns
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            cell = out[:, k * tw:(k + 1) * tw]
            if spec.get("lay"):
                lay(cell, L, U)
            if spec.get("mirror"):
                cell[U + 1:] = cell[:U][::-1]
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U]}
        print(f"{fn}  {n} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over {extent} source px), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    """The native strip read one pixel per 8x8 block, cut into its n equal cells."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"thresh_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"thresh_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# Thresh's chain, drawn here link by link so that it can grow with the throw and shrink with the pull: rows U-1 to
# U+1, a link every 5 px in Codex's dark iron with a grey-green hole, every fourth link lit, the light moving one
# link a frame toward the blade
IRON, METAL, HOLE = (0x39, 0x2B, 0x2A), (0x68, 0x52, 0x50), (0x6C, 0x90, 0x72)
LIT_METAL, LIT_HOLE = (0xA9, 0xF1, 0xC1), (0x4F, 0xE4, 0x8E)
LINK = ["iiii.", "mhhmi", "iiii."]


def chain(cell, U, x0, step, length, frame):
    """`length` px of chain from column x0 (the pixel next to the blade) going `step` (-1 left, 1 right)."""
    for i in range(max(length, 0)):
        x = x0 + step * i
        if not 0 <= x < cell.shape[1]:
            break
        lit = (i // 5 + frame) % 4 == 0
        for r, row in enumerate(LINK):
            ch = row[i % 5]
            if ch != ".":
                col = {"i": IRON, "m": LIT_METAL if lit else METAL, "h": LIT_HOLE if lit else HOLE}[ch]
                cell[U - 1 + r, x] = (*col, 255)


def widen(cell, L, U, L2):
    """The cell on a wider canvas, 2 * L2 + 1 wide, its anchor still in the middle."""
    out = np.zeros((cell.shape[0], 2 * L2 + 1, 4), np.uint8)
    out[:, L2 - L:L2 - L + cell.shape[1]] = cell
    return out


def hook(anchors):
    """The hook thrown: Codex's blade, its own chain cut off, and the chain behind it as long as the hook has
    flown. It leaves Thresh at 5.5 px a tick (5500) and the chain hangs from its hub 3 px behind the anchor, so in
    frame k (two ticks each, from tick 2k) the chain is 11k - 3 px long and ends where it was thrown from; the
    seventh frame is held until the hook stops (72000 is 13 ticks)."""
    L, U = anchors["q_hook"]["anchor"]
    L2 = 3 + 11 * 6
    blades = cells("q_hook", 4)
    hub = L2 - 3
    out = []
    for k in range(7):
        c = widen(blades[k % 4], L, U, L2)
        c[U - 2:U + 3, :hub] = 0
        chain(c, U, hub - 1, -1, 11 * k - 3, k)
        out.append(c)
    return out, (L2, U), [33, 34] * 3 + [400]


def pull(anchors):
    """The hook coming back: Codex's blade (its chain and glow in front of it cut off) with the chain in front of
    it, toward Thresh, shorter every frame. The hook flies back at the drag's 1.5 px a tick from where it caught
    (45-70 px out in the simulated games, once 12) and stops on him; drawn for 55 px, the chain starting 5 px in
    front of the anchor: a frame every four ticks, 45 - 6k px (the middle of the frame), then the blade alone,
    held for a missed hook (75 px, 49 ticks)."""
    L, U = anchors["q_return"]["anchor"]
    blades = cells("q_return", 4)
    hub = L + 5
    out = []
    for k in range(9):
        c = blades[k % 4].copy()
        c[U - 5:U + 6, hub:] = 0
        chain(c, U, hub, 1, 45 - 6 * k, k)
        out.append(c)
    return out, (L, U), [67, 66, 67] * 2 + [67, 66] + [400]


MADE = {"q_hook": hook, "q_return": pull}

# the Box: three frames rising, the four standing ones ten times (110 ms), three shattering: 5.0 s
BOX = list(range(3)) + [3, 4, 5, 6] * 10 + [7, 8, 9]
BOX_MS = [100] * 3 + [110] * 40 + [100] * 3

# sprite: {tag: (strip, its frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_thresh_fx": {
        "lash": ("lash", range(4), (0, 0), [60] * 4),
        "lash_flay": ("lash_flay", range(4), (0, 0), [60] * 4),
        "hit": ("hit", range(5), HIT, [50] * 5),
        "flay_hit": ("flay_hit", range(6), HIT, [60] * 6),
        "q_hook": ("q_hook", None, (0, 0), None),                 # frames and times from MADE
        "q_return": ("q_return", None, (0, 0), None),
        # the flash, then the chains held while the 1 s stun lasts, breaking at its end
        "q_hit": ("q_hit", range(8), BODY, [80] + [120] * 6 + [100]),
        "w_lantern": ("w_lantern", range(4), (0, 0), [70] * 4),
        "w_shield": ("w_shield", range(6), FEET, [100] * 6),
        "e_hit": ("e_hit", range(5), HIT, [50] * 5),
        "r_hit": ("r_hit", range(6), BODY, [60] * 6),
        "r_slow": ("r_slow", range(4), FEET, [100] * 4),
    },
    "league_thresh_big": {
        "e_sweep": ("e_sweep", range(7), FEET, [50] * 7),
        "r_box": ("r_box", BOX, FEET, BOX_MS),
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "thresh_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (src, used, (sx, sy), ms) in tags.items():
            if src in MADE:
                strip, (ax, ay), ms = MADE[src](anchors)
                used = range(len(strip))
            else:
                ax, ay = anchors[src]["anchor"]
                strip = cells(src, RAW[src]["n"])
            out[tag] = [(G.centre_frame(strip[k], sx - ax, sy - ay), m) for k, m in zip(used, ms)]
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--only", nargs="+", help="with --raw: just these strips (e.g. q_hook w_lantern)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
