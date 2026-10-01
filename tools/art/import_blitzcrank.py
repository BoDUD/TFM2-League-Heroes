#!/usr/bin/env python3
"""Import Blitzcrank's effects (assets/source/blitzcrank/PROMPTS_FX.md, 1-12) as game sheets.

    python tools/art/import_blitzcrank.py --native <Codex's delivery folder>   # once: Codex's 1x strips -> native strips
    python tools/art/import_blitzcrank.py                                      # native strips -> effect sheets

The body comes from tools/art/import_native.py. Codex delivered the effects finished at game size (blitzcrank_fx_done,
2026-10-01): `logical/blitzcrank_fx_<name>_1x.png` in the pack's ramps, binary alpha, manifest.json's
`assets[].frames[].rect_1x` the cells. --native copies every pixel: each frame is cut by its cell and saved at 8x as
assets/source/blitzcrank/blitzcrank_fx_<name>.png, the Rocket Grab's pieces as blitzcrank_fx_q_hand.png (the fist, two
frames, aligned on their knuckles: Codex drew the second 2 px to the left) and blitzcrank_fx_q_cable.png (a 12x3 tile).
The second step places every cell by its anchor (ANCHOR, in the cell) on a spot from the pivot (60 ticks a second):
hits on the upper body, the bolt's strike and the uppercut's burst on the chest, the silence over a 35-40 px hero's
crown, the field's ellipse round the soles; the steam where the pack put it (the pivot at (24, 47) of the steam cell:
it rises from the smokestacks), the charge and the shield as Codex drew them, standing on row 47 of their cells (the
soles, 11 px under the pivot). Rows measured on Codex's frames where its drawing moved off the pack's points: the
bolt's burst at (9, 32) (the pack: (10, 31)), the uppercut's flash at (11, 30) (the pack: (12, 26)).
The Rocket Grab is drawn here from the pieces, a frame every 2 ticks: the projectile's picture is turned to its
flight, so the fist points along it with the cable behind; no height can be added (section "A beam from a raised
weapon" in champion-data.md), so the hand flies at the hook's line (y_offset 2000) and appears once it is REACH px
out, past his arm, the cable running back to CABLE px from where it left (inside the front of his body).
`q_hand`: out at 6000 a tick (12 px a frame), the cable growing; the last frame held. `q_back1`..`q_back4`: a held
hook coming back with its champion at 1500 a tick (3 px a frame) from the tier's distance (BACK: the middle of the
returns logged for each flight window, 25 / 35-41 / 45-52 ticks), the fist turned round (its wrist toward him), the
cable shortening; `q_miss`: the fast return (4500 a tick, 9 px a frame) from the hook's full range. Each ends empty when
the hand is back within REACH. Writes league/effects/league_blitzcrank_fx and league_blitzcrank_big.
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "blitzcrank")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 35-40 px hero
CHEST = (0, -6)                        # the bolt's strike, the uppercut's flash
OVERHEAD = (0, -30)                    # over a 35-40 px hero's crown (the silence)
GROUND = (0, 10)                       # the middle of the field round his feet (the soles 11 px under the pivot)
PIVOT = (0, 0)                         # the steam cell's own pivot
SOLES = (0, 11)                        # the soles' row under the pivot
# the effects as Codex delivered them: (frames, anchor in the cell; "centre" = the cell's middle)
NATIVE = {
    "hit": (5, "centre"), "p_mark": (6, "centre"), "p_bolt": (6, (9, 32)), "q_grab": (5, "centre"),
    "e_hit": (6, (11, 30)), "w_steam": (6, (24, 47)), "r_charge": (5, (30, 47)), "r_field": (7, (66, 36)),
    "r_hit": (5, "centre"), "r_silence": (6, "centre"), "mb_on": (6, (30, 47)),
}
# the Rocket Grab, in px: the hand shows from REACH out; the cable runs back to CABLE from the start
REACH, CABLE = 24, 16
OUT = 12                               # px a frame going out (6000 a tick, a frame every 2 ticks)
DRAG, FAST = 3, 9                      # px a frame coming back with a champion (1500), without (4500)
BACK = {"q_back1": 28, "q_back2": 38, "q_back3": 57, "q_back4": 71, "q_miss": 78}
HAND_P = (10, 6)                       # the fist's middle in the hand cell: the projectile's point
WRIST = 5                              # the hand cell's column where the cable meets the wrist socket
CABLE_ROW = 5                          # the cable's top row in the hand cell (3 rows: light, light, dark)
FRAME_MS = 33                          # 2 ticks


def load_manifest(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        return {a["name"].replace("blitzcrank_fx_", ""): a for a in json.load(f)["assets"]}


def rgba(path):
    return np.asarray(Image.open(G.lp(path)).convert("RGBA")).copy()


def save8(a, name):
    Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"blitzcrank_fx_{name}.png")))


def read8(name):
    a = rgba(os.path.join(SRC, f"blitzcrank_fx_{name}.png"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"blitzcrank_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    return b[:, 0, :, 0].copy()


def from_native(folder):
    assets = load_manifest(folder)
    for name, (n, _) in NATIVE.items():
        asset = assets[name]
        a = rgba(os.path.join(folder, asset["file"]))
        rects = [tuple(f["rect_1x"]) for f in asset["frames"]]
        if len(rects) != n:
            sys.exit(f"{asset['file']}: {len(rects)} frames, not {n}")
        cw, ch = rects[0][2], rects[0][3]
        out = np.zeros((ch, cw * n, 4), np.uint8)
        for k, (x, y, w, h) in enumerate(rects):
            out[:, k * cw:(k + 1) * cw] = a[y:y + h, x:x + w]
        out[out[..., 3] < 128] = 0
        out[out[..., 3] > 0, 3] = 255
        save8(out, name)
        print(f"blitzcrank_fx_{name}.png  {n} cells of {cw}x{ch}, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    parts = assets["q_parts"]["components"]
    hand = rgba(os.path.join(folder, parts["hand_strip"]))
    cells = [hand[:, k * 16:(k + 1) * 16] for k in range(2)]
    # align the fists on their knuckles (the rightmost opaque column)
    right = [int(np.nonzero(c[..., 3].any(0))[0].max()) for c in cells]
    for k, c in enumerate(cells):
        dx = max(right) - right[k]
        if dx:
            cells[k] = np.roll(c, dx, axis=1)
            cells[k][:, :dx] = 0
    save8(np.concatenate(cells, axis=1), "q_hand")
    cable = rgba(os.path.join(folder, parts["cable_tile"]))
    save8(cable, "q_cable")
    print(f"blitzcrank_fx_q_hand.png  2 cells of 16x12 (knuckles moved {[max(right) - r for r in right]}), "
          f"blitzcrank_fx_q_cable.png {cable.shape[1]}x{cable.shape[0]}")


def cut(name, n):
    a = read8(name)
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def placed(cell, anchor, spot):
    h, w = cell.shape[:2]
    ax, ay = (w // 2, h // 2) if anchor == "centre" else anchor
    return G.centre_frame(cell, spot[0] - ax, spot[1] - ay)


def grab_frame(hand, cable, d, back=False):
    """One frame of the hook: the fist's middle on the projectile (the pivot), the cable from its wrist to CABLE px
    from where the hand left (d px behind it). Out: the fist points right, the cable runs left; back (the picture
    turned toward Blitzcrank): the fist turned round, the cable runs right. Empty within REACH."""
    if d < REACH:
        return np.zeros((1, 1, 4), np.uint8)
    length = d - CABLE - (HAND_P[0] - WRIST)
    hh, hw = hand.shape[:2]
    pad = max(length, 0) + hw
    canvas = np.zeros((hh, pad + hw, 4), np.uint8)
    x0 = pad                                       # the hand cell's left column on the canvas
    tile = np.tile(cable, (1, -(-max(length, 1) // cable.shape[1]) + 1, 1))
    if length > 0:
        seg = tile[:, tile.shape[1] - length:]     # the tile's pattern fixed on the wrist end
        canvas[CABLE_ROW:CABLE_ROW + 3, x0 + WRIST - length:x0 + WRIST] = seg
    op = hand[..., 3] > 0
    canvas[:, x0:x0 + hw][op] = hand[op]
    px = x0 + HAND_P[0]
    if back:
        canvas = canvas[:, ::-1]
        px = canvas.shape[1] - 1 - px
    return G.centre_frame(canvas, -px, -HAND_P[1])


def grab_tags():
    hands = cut("q_hand", 2)
    cable = read8("q_cable")
    out = {"q_hand": []}
    d, j = 0, 0
    while d <= 78:                                  # the hook's range: 78000
        out["q_hand"].append((grab_frame(hands[j % 2], cable, d), FRAME_MS))
        d, j = d + OUT, j + 1
    out["q_hand"][-1] = (out["q_hand"][-1][0], 600)  # held past any flight
    for tag, start in BACK.items():
        step = FAST if tag == "q_miss" else DRAG
        frames, d, j = [], start, 0
        while d >= REACH:
            frames.append((grab_frame(hands[j % 2], cable, d, back=True), FRAME_MS))
            d, j = d - step, j + 1
        frames.append((np.zeros((1, 1, 4), np.uint8), 600))
        out[tag] = frames
    return out


# sprite: {tag: (strip, frames used, spot of the anchor from the pivot, ms per frame)}
FX = {
    "league_blitzcrank_fx": {
        "hit": ("hit", range(5), HIT, [60] * 5),
        "p_mark": ("p_mark", range(6), HIT, [167] * 6),            # 1 s: until the bolt
        "p_bolt": ("p_bolt", range(6), CHEST, [70] * 6),
        "q_grab": ("q_grab", range(5), HIT, [70] * 5),
        "e_hit": ("e_hit", range(6), CHEST, [70] * 6),
        "w_steam": ("w_steam", range(6), PIVOT, [167] * 6),        # played each second of Overdrive
        "r_hit": ("r_hit", range(5), HIT, [70] * 5),
        "r_silence": ("r_silence", range(6), OVERHEAD, [167] * 6),  # 1 s
        "mb_on": ("mb_on", range(6), SOLES, [167] * 6),            # loops while the shield holds
    },
    "league_blitzcrank_big": {
        "r_charge": ("r_charge", range(5), SOLES, [80] * 5),       # 400 ms: the field on tick 23
        "r_field": ("r_field", range(7), GROUND, [80] * 7),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (src, used, spot, ms) in tags.items():
            n, anchor = NATIVE[src]
            cells = cut(src, n)
            out[tag] = [(placed(cells[k], anchor, spot), m) for k, m in zip(used, ms)]
        sheets[sprite] = out
    sheets["league_blitzcrank_big"].update(grab_tags())
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--native", help="Codex's delivery folder: rebuild the native strips from its 1x strips first")
    args = ap.parse_args()
    if args.native:
        from_native(args.native)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
