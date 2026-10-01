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
chain tile) as League has it (the user: "要的是和联盟一样 从手臂飞出去的爪子勾人", "lol里面机器人什么样你就什么样"): the hand
flies out of his arm on its chain, and what it catches it brings back along the same line to his arm, where it goes
back on. A projectile's picture is turned to its flight and cannot carry a height of its own (section "A beam from a
raised weapon" in champion-data.md); the hook leaves from his raised arm (y_offset -11500: 16.5 px over his pivot,
sloping down to the range's end; thrown straight ahead its line runs along the arm of the Q strip and out of its
socket) and moves 6 px on every tick from the throw. The claw goes over the units (`q_hand`, `q_hc*`, `q_mc*`, z 1 in
the kit: it holds its catch in sight) and the chain under them (`q_twin`, `q_hn*`, `q_mn*`, z -1), running back along
the line to where the hook left: his straight arm hides it there, or his body when the hook flies at an angle (his
body only faces left or right, and most hooks go up or down: 15 of 80 within 15 degrees of level in 4 logged games).
Out, a frame a tick: the open claw from SHOW_OUT px along (in front of where the strip's frame 3 holds it), on the hook;
its chain on the twin, which flies with it. A hook that stopped h ticks after the throw is 6 (h + 1) px along; 2
ticks later the kit sends two projectiles along the same line (they leave where the hook left and head for where it
stopped, LINE_V a tick) carrying, for that h, the claw and the chain coming back, a frame a tick: held (`q_hc<h>`,
`q_hn<h>`), the closed claw with its catch (the drag began on the tick before) back where frame 3 holds it (DOCK) just
as the catch stops STOP px off him, in reach, when the kit plays the strip's hold (the closed claw on the arm); empty
(`q_mc<h>`, `q_mn<h>`: a miss or a blocked hook), the open claw fast (MISS_V), gone at DOCK, when the strip's frame 7
has it on the arm. The claws on their way back carry no rocket steam. Writes league/effects/league_blitzcrank_fx and
league_blitzcrank_big.
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
OUT_V, DRAG_V, MISS_V = 6.0, 1.5, 9.0   # px a tick: out, back with its catch (the drag), back empty
LINE_V = 1.5                            # px a tick: the projectiles that carry the way back (the kit's q_line)
TIERS = 14                              # the ways back q_*0..13: the hook stopped h ticks after the throw
HAND_P = (8, 7)                         # the claw's middle in its cell: the projectile's point
WRIST = 1                               # the cell's column where the chain meets the wrist
CABLE_ROW = 6                           # the chain's top row in the cell (3 rows)
SHOW_OUT = 36                           # px along the line: the flying claw shows (frame 3 holds it at 32)
DOCK = 32                               # px along the line: the claw back on the arm (the kit's q_dock)
TOUCH, STOP = 12, 33                    # px: the hook stops this short of a champion's centre; the catch stops
                                        # this far from him (the kit's q_touch, q_stop)
STEAM = {(0xFF, 0xFF, 0xFF), (0xE8, 0xEC, 0xF0), (0xC8, 0xD0, 0xD8), (0x9A, 0xA4, 0xB0)}   # the claws' rocket puff


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


FULL = math.hypot(END[0] - START[0], END[1] - START[1])   # the line's length (thrown straight ahead)


def along(h):
    """Px along the line where a hook stopped h ticks after the throw (it moves on the throw's tick too)."""
    return min(OUT_V * (h + 1), FULL)


def drag(h):
    """Ticks the kit drags a held catch: from where the hook stopped to STOP off him."""
    return max(0, round((along(h) + TOUCH - STOP) / DRAG_V))


def claw_frame(claw, off):
    """The claw, its middle off px along the line from the projectile (the picture's pivot), pointing out."""
    return G.centre_frame(claw, int(round(off)) - HAND_P[0], -HAND_P[1])


def chain_frame(chain, off, length):
    """length px of chain ending at the wrist of a claw whose middle is off px along from the projectile, running
    back toward where the hook left; the links fixed on the claw's end."""
    length = max(int(round(length)), 0)
    if not length:
        return EMPTY
    tile = np.tile(chain, (1, -(-length // chain.shape[1]) + 1, 1))
    seg = tile[:, tile.shape[1] - length:]
    end = int(round(off)) - (HAND_P[0] - WRIST)    # the wrist, from the projectile
    return G.centre_frame(seg, end - length, CABLE_ROW - HAND_P[1])


def claw_cells(name):
    a = np.asarray(Image.open(G.lp(os.path.join(QREDO, f"blitzcrank_fx_q_{name}_1x.png"))).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    return [a[:, k * 16:(k + 1) * 16] for k in range(a.shape[1] // 16)]


def no_steam(cells):
    out = []
    for c in cells:
        c = c.copy()
        puff = np.isin(c[..., :3].reshape(-1, 3).view([("", c.dtype)] * 3).ravel(),
                       np.array(sorted(STEAM), dtype=c.dtype).view([("", c.dtype)] * 3).ravel()).reshape(c.shape[:2])
        c[puff & (c[..., 3] > 0)] = 0
        out.append(c)
    return out


def grab_tags():
    opened, closed = claw_cells("claw_open"), claw_cells("claw_closed")
    bare_open, bare_closed = no_steam(opened), no_steam(closed)
    chain = np.asarray(Image.open(G.lp(os.path.join(QREDO, "blitzcrank_fx_q_chain_1x.png"))).convert("RGBA")).copy()
    tail = HAND_P[0] - WRIST                         # the claw's middle to its wrist
    # out, a frame a tick: d px along on the throw's tick k; the claw on the hook, the chain on the twin back to the
    # hook's start
    ds = [OUT_V * (k + 1) for k in range(int(FULL // OUT_V))]
    ms = ticks_ms(len(ds))
    out = {"q_hand": [(claw_frame(opened[k % 2], 0) if d >= SHOW_OUT else EMPTY, m) for k, (d, m) in enumerate(zip(ds, ms))],
           "q_twin": [(chain_frame(chain, 0, d - tail) if d >= SHOW_OUT else EMPTY, m) for d, m in zip(ds, ms)]}
    for tag in ("q_hand", "q_twin"):
        out[tag][-1] = (out[tag][-1][0], 600)        # held past any flight
    # the way back, a frame a tick from the projectiles' first tick (2 ticks after the hook stopped): they left from
    # the hook's start and are LINE_V (k + 1) px along on tick k
    for h in range(TIERS):
        d0 = along(h)
        # held: the claw with its catch, dragged since the tick before, back at DOCK as the catch stops (it slides
        # from the catch's front onto it: the catch has TOUCH px more to go), then the hold takes over
        hold = max(0, drag(h) - 1) if d0 > DOCK else 0
        v = (d0 - DOCK) / drag(h) if hold else 0
        claws, chains = [], []
        for k, m in zip(range(hold), ticks_ms(hold)):
            d = d0 - v * (k + 1)
            off = d - LINE_V * (k + 1)
            claws.append((claw_frame(bare_closed[k % 2], off), m))
            chains.append((chain_frame(chain, off, d - tail), m))
        out[f"q_hc{h}"], out[f"q_hn{h}"] = claws + [(EMPTY, 600)], chains + [(EMPTY, 600)]
        # empty: the open claw fast back to DOCK
        dd = [d0 - MISS_V * k for k in range(int(FULL // MISS_V) + 1) if d0 - MISS_V * k > DOCK]
        mm = ticks_ms(len(dd))
        out[f"q_mc{h}"] = [(claw_frame(bare_open[k % 2], d - LINE_V * (k + 1)), m)
                           for k, (d, m) in enumerate(zip(dd, mm))] + [(EMPTY, 600)]
        out[f"q_mn{h}"] = [(chain_frame(chain, d - LINE_V * (k + 1), d - tail), m)
                           for k, (d, m) in enumerate(zip(dd, mm))] + [(EMPTY, 600)]
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
