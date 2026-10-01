#!/usr/bin/env python3
"""Import Blitzcrank's effects (assets/source/blitzcrank/PROMPTS_FX.md, 1-12) as game sheets.

    python tools/art/import_blitzcrank.py --native <Codex's delivery folder>   # once: Codex's 1x strips -> native strips
    python tools/art/import_blitzcrank.py                                      # native strips -> effect sheets

The body comes from tools/art/import_native.py. Codex delivered the effects finished at game size (blitzcrank_fx_done,
2026-10-01): `logical/blitzcrank_fx_<name>_1x.png` in the pack's ramps, binary alpha, manifest.json's
`assets[].frames[].rect_1x` the cells. --native copies every pixel: each frame is cut by its cell and saved at 8x as
assets/source/blitzcrank/blitzcrank_fx_<name>.png (its first Rocket Grab, a fist and a cable tile, gave way to the
redraw below and is left in codex_fx/).
The second step places every cell by its anchor (ANCHOR, in the cell) on a spot from the pivot (60 ticks a second):
hits on the upper body, the bolt's strike and the uppercut's burst on the chest, the silence over a 35-40 px hero's
crown, the field's ellipse round the soles; the steam where the pack put it (the pivot at (24, 47) of the steam cell:
it rises from the smokestacks), the charge and the shield as Codex drew them, standing on row 47 of their cells (the
soles, 11 px under the pivot). Rows measured on Codex's frames where its drawing moved off the pack's points: the
bolt's burst at (9, 32) (the pack: (10, 31)), the uppercut's flash at (11, 30) (the pack: (12, 26)).
The Rocket Grab is drawn here from Codex's redraw (codex_q_redo/logical, 2026-10-02: an open claw, a closed one and a
chain tile; the user: "要的是和联盟一样 从手臂飞出去的爪子勾人"). A projectile's picture is turned to its flight, so the
claw points along it with the chain behind, and a picture cannot carry a height of its own (section "A beam from a
raised weapon" in champion-data.md); the hook itself leaves from his raised arm (y_offset -11500: 16.5 px over his
pivot, sloping down to the range's end, START -> END; straight ahead it passes the Q strip's empty socket 25 px along).
Only left and right exist for his body while most hooks go up or down (in 4 logged games 15 of 80 within 15 degrees
of level, 60 between 30 and 90 up), so the claw and the chain go under the units (z -1 in the kit) and the chain
always runs into him: his arm and body hide what lies over them, and nothing hangs in the air at any angle. The hook
moves 6 px on every tick from the throw. `q_hand`, a frame a tick: the open claw from SHOW_OUT px along (in front of
where frame 3 of the strip holds it on his arm), its chain back to where the hook left (inside his chest), the links
moving with the claw; the last frame held. A hook that stopped h ticks after the throw is 6 (h + 1) px along its
line, and its return flies to his pivot whatever its y_offset (a logged game). `q_back0`..`q_back13` (the kit picks
one by h): the closed claw turned round (its wrist toward him) coming back at 1500 a tick, a frame every 2 ticks, its
chain into his pivot, until the return gets there (the kit ends the pull pose then); thrown straight ahead (`stop`)
- at an angle the distance differs by up to about 15 px and the chain ends that much off inside his body; straight
ahead it passes 2-3 px under the pull pose's socket (30, -5) into his belly. `q_miss`: the open claw and its chain
coming back from the range's end (78 px from him at any angle) at 9000 a tick, gone at MISS_GONE px, when frame 7 of
the strip has it on his arm again. Writes league/effects/league_blitzcrank_fx and league_blitzcrank_big.
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
# the Rocket Grab (Codex's redraw, codex_q_redo/logical: the open claw flying, the closed claw holding, an 8x3 chain
# tile; 16x14 cells, the claw's middle (8, 7) on the projectile, its wrist socket at the cell's left)
QREDO = os.path.join(SRC, "codex_q_redo", "logical")
START, END = (0.0, -16.5), (78.0, 0.0)  # the hook's line from his pivot, thrown straight ahead
OUT_V, DRAG_V, MISS_V = 6.0, 1.5, 9.0   # px a tick: out, back with a champion, a miss coming back
TIERS = 14                              # the held returns q_back0..13: stopped h ticks after the throw
HAND_P = (8, 7)                         # the claw's middle in its cell: the projectile's point
WRIST = 1                               # the cell's column where the chain meets the wrist
CABLE_ROW = 6                           # the chain's top row in the cell (3 rows)
SHOW_OUT = 36                           # px along the line: the flying claw shows (frame 3 holds it at 32)
MISS_GONE = 24                          # a miss's claw is gone (frame 7 has it on his arm)


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


def cut(name, n):
    a = read8(name)
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def placed(cell, anchor, spot):
    h, w = cell.shape[:2]
    ax, ay = (w // 2, h // 2) if anchor == "centre" else anchor
    return G.centre_frame(cell, spot[0] - ax, spot[1] - ay)


EMPTY = np.zeros((1, 1, 4), np.uint8)


def ticks_ms(n, every=1):
    """Durations of n frames of `every` ticks each, rounded so they keep time with the game (60 ticks a second)."""
    return [round((k + 1) * every * 1000 / 60) - round(k * every * 1000 / 60) for k in range(n)]


def stop(h):
    """How far from his pivot a hook thrown straight ahead stopped h ticks after the throw."""
    lx, ly = END[0] - START[0], END[1] - START[1]
    full = math.hypot(lx, ly)
    d = min(OUT_V * (h + 1), full)
    return math.hypot(START[0] + lx * d / full, START[1] + ly * d / full)


def grab_frame(claw, chain, length, back=False):
    """One picture of the hook, its pivot on the projectile: the claw's middle there and `length` px of chain from its
    wrist toward Blitzcrank, the links fixed on the claw. Out the claw points along the flight; back (the picture
    turned toward him) it is turned round, its wrist first."""
    length = max(int(round(length)), 0)
    hh, hw = claw.shape[:2]
    canvas = np.zeros((hh, length + hw, 4), np.uint8)
    x0 = length                                    # the claw cell's left column on the canvas
    if length:
        tile = np.tile(chain, (1, -(-length // chain.shape[1]) + 1, 1))
        canvas[CABLE_ROW:CABLE_ROW + 3, x0 + WRIST - length:x0 + WRIST] = tile[:, tile.shape[1] - length:]
    op = claw[..., 3] > 0
    canvas[:, x0:x0 + hw][op] = claw[op]
    px = x0 + HAND_P[0]
    if back:
        canvas = canvas[:, ::-1]
        px = canvas.shape[1] - 1 - px
    return G.centre_frame(canvas, -px, -HAND_P[1])


def claw_cells(name):
    a = np.asarray(Image.open(G.lp(os.path.join(QREDO, f"blitzcrank_fx_q_{name}_1x.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    return [a[:, k * 16:(k + 1) * 16] for k in range(a.shape[1] // 16)]


def grab_tags():
    opened, closed = claw_cells("claw_open"), claw_cells("claw_closed")
    chain = np.asarray(Image.open(G.lp(os.path.join(QREDO, "blitzcrank_fx_q_chain_1x.png"))).convert("RGBA")).copy()
    # out: a frame a tick, 6 (k + 1) px along the line on tick k
    full = math.hypot(END[0] - START[0], END[1] - START[1])
    along = [OUT_V * (k + 1) for k in range(int(full // OUT_V))]
    tail = HAND_P[0] - WRIST                         # the claw's middle to its wrist
    out = {"q_hand": [(grab_frame(opened[k % 2], chain, d - tail) if d >= SHOW_OUT else EMPTY, m)
                      for k, (d, m) in enumerate(zip(along, ticks_ms(len(along))))]}
    out["q_hand"][-1] = (out["q_hand"][-1][0], 600)  # held past any flight
    # held returns: a frame every 2 ticks, r px from his pivot on tick k after it left (it moves on that tick too)
    for h in range(TIERS):
        s = stop(h)
        ks = list(range(0, int(s // DRAG_V), 2))     # until it is back on him
        out[f"q_back{h}"] = [(grab_frame(closed[j % 2], chain, s - DRAG_V * (k + 1) - tail, back=True), m)
                             for j, (k, m) in enumerate(zip(ks, ticks_ms(len(ks), 2)))] + [(EMPTY, 600)]
    # a miss: a frame a tick from the range's end
    rs = [r for r in (END[0] - MISS_V * (k + 1) for k in range(int(END[0] // MISS_V))) if r >= MISS_GONE]
    out["q_miss"] = [(grab_frame(opened[k % 2], chain, r - tail, back=True), m)
                     for k, (r, m) in enumerate(zip(rs, ticks_ms(len(rs))))] + [(EMPTY, 600)]
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
