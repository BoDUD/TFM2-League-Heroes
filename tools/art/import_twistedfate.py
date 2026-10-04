#!/usr/bin/env python3
"""Import Twisted Fate's effects (assets/source/twistedfate/PROMPTS_FX.md, 29 sheets) as the game sheets
league_twistedfate_fx and league_twistedfate_big.

    python tools/art/import_twistedfate.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_twistedfate.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_twistedfate.py built the strips). --raw turns each frame of Codex's
drawings (its cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]) into a cell of a native strip
(assets/source/twistedfate/twistedfate_fx_<name>.png, 8x, plus twistedfate_fx_anchors.json) the way import_sivir.py
does: each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid, every
colour snapped to the ramps the pack gave that effect (BLUE, RED, GOLD, MAGIC, the CARD paper and the cards' and dice's
INK outline), then the ring comes off the glows (an edge pixel in a ramp's darkest shade goes when two lighter
neighbours hold the shape, else it takes the next shade) - the INK outline of the cards and the dice stays. One scale
per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m).
Anchors (source pixels): the flying cards on the card (the white core in the drawing's front half), the hits on their
white flash, the hand flashes on the star's left end, the pictures over the head on their lowest row, the rings on the
ground on the ring of a full-size frame.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot), measured on the rigged strips (tools/art/rig_twistedfate.py, the far hand): the hand that throws in attack 4
(11, -12) and in Q 4 (11, -8); over the hat (its top 29 over the pivot) - and times it by the kit
(work/tw/build_twistedfate.py, 60 ticks a second): the flying cards start with empty ticks (a projectile's first move
points its picture up, import_lucian.py's RAY_SKIP; it leaves his pivot, so the card stays unseen until it is past his
hand) and loop over their longest flight; the Q band plays once over its flight; the Gate and its mark on the ground
loop their middle frames over the 90-tick channel.
Writes league/effects/league_twistedfate_fx and league_twistedfate_big (the Q band, the red card's blast, R).
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
import import_jhin as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "twistedfate")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/tw/fx_pack_tw.py)
RAMPS = {
    "BLUE": ["142E80", "2456D6", "4A8CFF", "8CC4FF", "D6ECFF", "FFFFFF"],
    "RED": ["5C0C14", "B01824", "F03C30", "FF8A6A", "FFD6C8", "FFFFFF"],
    "GOLD": ["6B400A", "C07A10", "F2B21E", "FFD84E", "FFF4BE", "FFFFFF"],
    "MAGIC": ["3A1A70", "7034C8", "A468F0", "D2A4FF", "F4DEFF", "FFFFFF"],
    "CARD": ["9C8A62", "D6C9A4", "F4EEDC", "FFFFFF"],
    "INK": ["2A1E14"],                         # the cards' and the dice's outline
}
RIM = {"142E80": "2456D6", "5C0C14": "B01824", "6B400A": "C07A10", "3A1A70": "7034C8"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps; cards drawn a little over the pack's sizes so
# the card itself is ~6 px (Sivir's lesson: a 10-px spinning blade was a blur)
RAW = {
    "a_card": dict(n=4, size=20, measure="w", anchor="front", ramps="INK CARD MAGIC"),
    "a_card_e": dict(n=4, size=24, measure="w", anchor="front", ramps="INK CARD MAGIC"),
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="MAGIC"),
    "e_cast": dict(n=4, size=16, measure="w", anchor="left", ramps="INK MAGIC CARD"),
    "e_hit": dict(n=5, size=18, measure="m", anchor="core", ramps="MAGIC"),
    "dice_roll": dict(n=5, size=15, measure="h", anchor=("fixed", "low", 4), ramps="INK CARD GOLD"),
    "dice_faces": dict(n=6, size=14, measure="m", anchor="low", ramps="INK CARD GOLD RED"),
    "dice_out": dict(n=3, size=13, measure="m", anchor="cell", ramps="INK CARD GOLD"),
    "w_show": dict(n=3, size=15, measure="h", anchor="low", ramps="INK CARD BLUE RED GOLD"),
    "w_blue": dict(n=4, size=19, measure="h", anchor="low", ramps="INK CARD BLUE"),
    "w_red": dict(n=4, size=19, measure="h", anchor="low", ramps="INK CARD RED"),
    "w_gold": dict(n=4, size=19, measure="h", anchor="low", ramps="INK CARD GOLD"),
    "wb_card": dict(n=4, size=22, measure="w", anchor="front", ramps="INK CARD BLUE"),
    "wr_card": dict(n=4, size=22, measure="w", anchor="front", ramps="INK CARD RED"),
    "wg_card": dict(n=4, size=22, measure="w", anchor="front", ramps="INK CARD GOLD"),
    "wb_hit": dict(n=5, size=18, measure="m", anchor="core", ramps="BLUE"),
    "wr_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="RED"),
    "wr_burst": dict(n=6, size=50, measure="w", anchor=("fixed", "ellipse", 1), ramps="INK CARD RED"),
    "wr_slow": dict(n=4, size=18, measure="w", anchor="ellipse", ramps="RED"),
    "wg_hit": dict(n=5, size=20, measure="m", anchor="core", ramps="GOLD"),
    "q_cast": dict(n=4, size=18, measure="w", anchor="left", ramps="INK MAGIC CARD"),
    "q_cards": dict(n=6, size=20, measure="h", anchor="front", ramps="INK CARD MAGIC"),
    "q_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="INK MAGIC CARD"),
    "r_seen": dict(n=4, size=12, measure="w", anchor="low", ramps="GOLD RED INK"),
    "r_cast": dict(n=7, size=72, measure="h", anchor=("fixed", "ellipse", 3), ramps="INK CARD GOLD"),
    "r_gate": dict(n=8, size=60, measure="h", anchor=("fixed", "ellipse", 3), ramps="INK CARD GOLD"),
    "r_dest": dict(n=6, size=40, measure="w", anchor=("fixed", "box", 3), ramps="GOLD"),
    "r_out": dict(n=5, size=56, measure="h", anchor=("fixed", "ellipse", 0), ramps="INK CARD GOLD"),
    "r_in": dict(n=5, size=56, measure="h", anchor=("fixed", "ellipse", 2), ramps="INK CARD GOLD"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def anchor(how, k, a, solid, rects, s=1.0):
    """(x, y) of frame k's anchor in the source: import_jhin's, plus `box` (the middle of the drawing's box), `front`
    (a flying card: 3 game px in from the drawing's front end, halfway down its box) and `ellipse` (a ring on the
    ground: its widest row in the drawing's lower half - a ring's ends lie on its middle row)."""
    if how == "front":
        x, y, w, h = rects[k]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        return x + xs.max() + 1 - 3 / s, y + (ys.min() + ys.max() + 1) / 2
    if how == "ellipse":
        x, y, w, h = rects[k]
        m = solid[y:y + h, x:x + w]
        ys = np.nonzero(m.any(1))[0]
        y0, y1 = ys.min(), ys.max() + 1
        best, rows = -1, []
        for r in range((y0 + y1) // 2, y1):
            xs = np.nonzero(m[r])[0]
            if not len(xs):
                continue
            wid = xs.max() - xs.min()
            if wid > best:
                best, rows = wid, [r]
            elif wid == best:
                rows.append(r)
        r = rows[len(rows) // 2]
        xs = np.nonzero(m[r])[0]
        return x + (xs.min() + xs.max() + 1) / 2, y + r + 0.5
    if how == "box":
        x, y, w, h = rects[k]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        return x + (xs.min() + xs.max() + 1) / 2, y + (ys.min() + ys.max() + 1) / 2
    if isinstance(how, tuple) and how[0] == "fixed":
        x, y, _, _ = rects[k]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects, s)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    return J.anchor(how, k, a, solid, rects)


# the dice faces: at 14 px the drawn pips blur into each other (2-6 read alike). The front face (rows 7-12, columns 5-11 of
# each converted cell) gets a seventh row (row 9 copied under itself) and its pips are put back on a 3 x 3 grid of
# single squares with a square between them (rows 8 / 10 / 12, columns 6 / 8 / 10); the 1 a red plus in the middle
DICE_FACE = (7, 13, 5, 11)                    # rows, columns of the front face once it is seven rows tall
PIPS = {1: [], 2: [(8, 10), (12, 6)], 3: [(8, 10), (10, 8), (12, 6)], 4: [(8, 6), (8, 10), (12, 6), (12, 10)],
        5: [(8, 6), (8, 10), (10, 8), (12, 6), (12, 10)], 6: [(8, 6), (10, 6), (12, 6), (8, 10), (10, 10), (12, 10)]}
FACE_CLEAR = {"F4EEDC", "FFFFFF", "2A1E14", "F03C30", "B01824", "FF8A6A", "FFD6C8", "D6C9A4"}


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def dice_pips(cell, k):
    """Face k + 1's cell with a seven-row front face and its pips on the grid."""
    cell = np.concatenate([cell[:10], cell[9:10], cell[10:]], 0)
    r0, r1, c0, c1 = DICE_FACE
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if cell[r, c, 3] and "%02X%02X%02X" % tuple(cell[r, c, :3]) in FACE_CLEAR:
                cell[r, c, :3] = rgb("F4EEDC")
    for r, c in PIPS[k + 1]:
        cell[r, c, :3] = rgb("2A1E14")
    if k == 0:
        for r, c in ((10, 8), (9, 8), (11, 8), (10, 7), (10, 9)):
            cell[r, c, :3] = rgb("F03C30")
    return cell


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"twistedfate_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = J.snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, solid, rects, s) for k in range(len(rects))]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        for i, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[i]
            cell = np.zeros((th, tw, 4), np.uint8)
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 4:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            out[:, i * tw:(i + 1) * tw] = unrim(cell)
        if name == "dice_faces":
            out = np.concatenate([dice_pips(out[:, i * tw:(i + 1) * tw].copy(), i) for i in range(len(rects))], 1)
            th += 1
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "twistedfate_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"twistedfate_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"twistedfate_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (fx_pack_tw.hand_at)
E_HAND = (11, -12)          # the far hand that throws in attack 4 (the release)
Q_HAND = (11, -8)           # the far hand that throws Q in skill 4
OVER = (0, -31)             # the lowest row of a picture over the head: 2 px over his hat (the idle's top -29)
DICE = (0, -36)             # the resting die's middle (dice_faces' lowest row on OVER)
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
EMPTY = J.EMPTY

seq = J.seq
flight = J.flight


def looped(first, loop, ms_first, ms_loop, total):
    """Frames `first` once, then `loop` repeated until `total` ms (the last frame cut to fit)."""
    out = seq(first, ms_first)
    t = sum(ms_first)
    k = 0
    while t < total:
        ms = min(ms_loop, total - t)
        out.append((loop[k % len(loop)], ms))
        t += ms
        k += 1
    return out


GATE_MS = 90 * 1000 // 60                     # r_ch: the 90-tick channel
FX = {
    # the cards: the attack 57.5 px at 5.5 px a tick (homing, so twice that); out of his hand 13 px away: 3 empty ticks
    "a_card": [("a_card", flight(4, 50, 420, lead=3), [(0, 0)])],
    "a_card_e": [("a_card_e", flight(4, 50, 420, lead=3), [(0, 0)])],
    "wb_card": [("wb_card", flight(4, 50, 420, lead=3), [(0, 0)])],
    "wr_card": [("wr_card", flight(4, 50, 420, lead=3), [(0, 0)])],
    "wg_card": [("wg_card", flight(4, 50, 420, lead=3), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_cast": [("e_cast", seq(range(4), [30, 40, 50, 60]), [E_HAND])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "wb_hit": [("wb_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "wr_hit": [("wr_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "wg_hit": [("wg_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_cast": [("q_cast", seq(range(4), [30, 40, 50, 60]), [Q_HAND])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # over the head: the shuffling card (one picture each), the locked card, the slow, Destiny's eye
    "w_show_blue": [("w_show", seq([0], [1000]), [OVER])],
    "w_show_red": [("w_show", seq([1], [1000]), [OVER])],
    "w_show_gold": [("w_show", seq([2], [1000]), [OVER])],
    "w_blue": [("w_blue", seq(range(4), [100] * 4), [OVER])],
    "w_red": [("w_red", seq(range(4), [100] * 4), [OVER])],
    "w_gold": [("w_gold", seq(range(4), [100] * 4), [OVER])],
    "wr_slow": [("wr_slow", seq(range(4), [110] * 4), [FEET])],
    "r_seen": [("r_seen", seq(range(4), [130] * 4), [OVER])],
    # Loaded Dice: thrown up, the face shown (dice_show 54 ticks), gone
    "dice_roll": [("dice_roll", seq(range(5), [50, 50, 50, 50, 70]), [OVER])],
    **{f"dice_{k}": [("dice_faces", seq([k - 1], [1000]), [OVER])] for k in range(1, 7)},
    "dice_out": [("dice_out", seq(range(3), [60, 70, 80]), [DICE])],
}
BIG = {
    # Q: 115 px at 4 px a tick (29 ticks, 480 ms), once; out of his hand 11 px away: 3 empty ticks
    "q_cards": [("q_cards", [(EMPTY, 50)] + seq(range(6), [70, 70, 80, 80, 90, 1000]), [(0, 0)])],
    "wr_burst": [("wr_burst", seq(range(6), [50, 60, 70, 80, 90, 100]), [FEET])],
    "r_cast": [("r_cast", seq(range(7), [40, 50, 60, 80, 80, 70, 60]), [FEET])],
    "r_gate": [("r_gate", looped([0, 1], [2, 3, 4, 5, 6, 7], [60, 60], 80, GATE_MS), [FEET])],
    "r_dest": [("r_dest", looped([0, 1], [2, 3, 4, 5], [60, 60], 100, GATE_MS), [FEET])],
    "r_out": [("r_out", seq(range(5), [50, 60, 70, 80, 90]), [FEET])],
    "r_in": [("r_in", seq(range(5), [40, 50, 70, 80, 90]), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "twistedfate_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((J.place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_twistedfate_fx", FX), ("league_twistedfate_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
