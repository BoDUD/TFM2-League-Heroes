#!/usr/bin/env python3
"""Import Talon's effects (assets/source/talon/PROMPTS_FX.md, 16 sheets) as the game sheets league_talon_fx and
league_talon_big.

    python tools/art/import_talon.py --raw assets/source/talon/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_talon.py                                      # native strips -> the effect sheets

The body comes from tools/art/fix_talon_strips.py + import_native.py. --raw turns each frame of Codex's drawings into a
cell of a native strip (assets/source/talon/talon_fx_<name>.png, 8x, plus talon_fx_anchors.json) the way
import_hecarim.py does: the frames on the equal grid or split at the emptiest column near each grid line, each game
pixel the majority colour of the source pixels it covers, every colour snapped to the ramps the pack gave that effect
(work/tl/fx_pack_tl.py), then the lights' darkest ring comes off (import_jhin.unrim; the stealth smoke's near-black is
its inside and stays). One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side
(m) - or over frame `ref`'s alone (the rings are the kit's radii: r_r 30000 -> 60 px across).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (tools/kit/build_talon.py, 60 ticks a second).
The red side: the client never mirrors a data picture. The flying blades are turned to their flight - drawn over their
own top-bottom flip; everything on a unit or on the ground is drawn over its own left-right flip (league_xayah's
over_flip), centred on the pivot.
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
import import_varus as V  # noqa: E402
import import_xayah as X  # noqa: E402
import import_hecarim as HC  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "talon")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/tl/fx_pack_tl.py), darkest first
RAMPS = {
    "STEEL": ["3C4560", "63708C", "93A2BE", "C9D4E8", "EEF4FF", "FFFFFF"],
    "GLEAM": ["1A2A78", "2A4FC0", "4A86F0", "8EC4FF", "D8ECFF"],
    "BLOOD": ["400408", "7A0810", "C0141C", "F23A30", "FF8A7A", "FFE0D8"],
    "SHADE": ["140F30", "241E5A", "3A3490", "5A5CC8", "8A9AF0", "C8D4FF"],
    "SPARK": ["F59A3A", "FFD08A", "FFF2D8"],
    "HEAL": ["2E9A3A", "6AD860", "B8F5B0", "F0FFF0"],
    "DUST": ["807060", "B8A890", "E8DCC8"],
}
# the lights' darkest shade on their edge goes (or takes the next); blood's and the smoke's darkest are their inside
RIM = {"3C4560": "63708C", "1A2A78": "2A4FC0", "F59A3A": "FFD08A", "2E9A3A": "6AD860", "807060": "B8A890"}

# raw strip -> native: frames n, size (game px) over measure (of frame ref when given), anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=12, measure="m", ref=1, anchor=("fixed", "box", 1), ramps="STEEL GLEAM SPARK"),
    "p_wound": dict(n=4, size=10, measure="w", anchor=("fixed", "low", 0), ramps="STEEL BLOOD"),
    "p_bleed": dict(n=6, size=20, measure="m", ref=2, anchor=("fixed", "box", 2), ramps="BLOOD STEEL"),
    "q_leap": dict(n=4, size=24, measure="w", ref=1, anchor=("fixed", "low", 1), ramps="STEEL GLEAM DUST"),
    "q_hit": dict(n=5, size=18, measure="m", ref=2, anchor=("fixed", "box", 2), ramps="STEEL BLOOD SPARK"),
    "q_heal": dict(n=5, size=24, measure="h", ref=2, anchor=("fixed", "low", 2), ramps="HEAL"),
    "w_out": dict(n=4, size=20, measure="h", anchor=("fixed", "box", 0), ramps="STEEL GLEAM"),
    "w_back": dict(n=4, size=20, measure="h", anchor=("fixed", "box", 0), ramps="STEEL BLOOD"),
    "w_hit": dict(n=3, size=10, measure="w", ref=0, anchor=("fixed", "box", 0), ramps="STEEL GLEAM"),
    "w_slow": dict(n=4, size=16, measure="w", anchor=("fixed", "ellipse", 0), ramps="STEEL BLOOD"),
    "e_vault": dict(n=5, size=26, measure="w", ref=2, anchor=("fixed", "low", 2), ramps="STEEL GLEAM DUST"),
    "e_haste": dict(n=4, size=18, measure="w", anchor=("fixed", "ellipse", 0), ramps="STEEL GLEAM"),
    "r_out": dict(n=6, size=60, measure="w", ref=3, anchor=("fixed", "ellipse", 3), ramps="STEEL GLEAM SHADE"),
    "r_back": dict(n=6, size=60, measure="w", ref=0, anchor=("fixed", "ellipse", 0), ramps="STEEL BLOOD"),
    "r_hit": dict(n=4, size=14, measure="m", ref=1, anchor=("fixed", "box", 1), ramps="STEEL BLOOD GLEAM"),
    "r_on": dict(n=4, size=34, measure="h", anchor=("fixed", "low", 0), ramps="SHADE GLEAM"),
}


def from_raw(folder):
    """Codex's PNGs -> native strips + talon_fx_anchors.json (import_hecarim.from_raw's way, Talon's tables)."""
    V.RAMPS = RAMPS
    V.RIM = RIM
    V.anchor = HC.anchor
    apath = os.path.join(SRC, "talon_fx_anchors.json")
    anchors = {}
    if os.path.exists(G.lp(apath)):
        with open(G.lp(apath), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        fn = f"talon_fx_{name}.png"
        if not os.path.exists(G.lp(os.path.join(folder, fn))):
            print("missing", fn)
            continue
        hexes_, pal = V.palette(spec["ramps"])
        im = Image.open(G.lp(os.path.join(folder, fn)))
        a = np.asarray(im.convert("RGBA")).copy()
        if im.mode != "RGBA" or (a[..., 3] == 255).all():   # drawn on opaque black: the black is the background
            a[..., 3] = np.where(a[..., :3].max(-1) > 40, 255, 0)
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = HC.split(solid, spec["n"])
        sp = dict(spec)
        if "ref" in spec:               # the size is frame ref's: the scale of the strip from it
            boxes = [HC.box_w_h(solid, r) for r in rects]
            ext = {"w": max(b[0] for b in boxes), "h": max(b[1] for b in boxes)}
            ext["m"] = max(ext["w"], ext["h"])
            bw, bh = boxes[spec["ref"]]
            ref = {"w": bw, "h": bh, "m": max(bw, bh)}[spec["measure"]]
            sp["size"] = spec["size"] * ext[spec["measure"]] / ref
        out, cell, anc, s, ext = V.convert(name, sp, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale {s:.4f} "
              f"({spec['size']} px over {spec['measure']}{' of frame %d' % spec['ref'] if 'ref' in spec else ''}), "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(apath), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"talon_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"talon_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down); his design is 42 rows: the crown 30 over the pivot
HIT = (0, -13)              # a hit on the upper body
OVERHEAD = (0, -33)         # the wound mark's lowest row: just over the hood
FEET = (0, 10)              # a ring on the ground round a unit's feet
GROUND = (0, 11)            # what stands on the ground: its lowest row on the soles
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_wound": [("p_wound", seq(range(4), [120] * 4), [OVERHEAD])],
    "p_bleed": [("p_bleed", seq(range(6), [40, 60, 80, 100, 120, 140]), [HIT])],
    "q_leap": [("q_leap", seq(range(4), [40, 60, 70, 80]), [GROUND])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    "q_heal": [("q_heal", seq(range(5), [60, 80, 90, 100, 110]), [GROUND])],
    # the blades fly w_len 55000 at 5000 a tick (11 ticks = 183 ms), back at the same speed: looped
    "w_out": [("w_out", flight(4, 50, 300, lead=0), [(0, 0)])],
    "w_back": [("w_back", flight(4, 50, 400, lead=0), [(0, 0)])],
    "w_hit": [("w_hit", seq(range(3), [40, 60, 80]), [HIT])],
    "w_slow": [("w_slow", seq(range(4), [110] * 4), [FEET])],
    "e_vault": [("e_vault", seq(range(5), [40, 50, 60, 70, 90]), [GROUND])],
    "e_haste": [("e_haste", seq(range(4), [90] * 4), [FEET])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_on": [("r_on", seq(range(4), [120] * 4), [GROUND])],
}
# R (League's Shadow Assault): the blades fly out to the ring in r_fly ticks (r_out's first four cells, 183 ms), hang
# there for the stealth - the kit plays one r_ring<k> piece (r_step ticks, 100 ms) on his cast point every r_step
# ticks while r_on lasts: r_out's last cell, its blades alone (the specks between them off) a shade lighter so they
# stand out on the stealth smoke, one row of them (top to bottom) lit white in turn - and fly in to where he is when
# they come back (r_back on him: the lit ring, then r_back's blades closing in and the flash, without its leftover dots)
RING = 4
BIG = {
    "r_out": [("r_out", seq(range(4), [30, 40, 50, 63]), [FEET])],
    **{f"r_ring{k}": [("r_out", seq([("ring", 5, k)], [100]), [FEET])] for k in range(RING)},
    "r_back": [("r_out", seq([("ring", 5, None)], [40]), [FEET]),
               ("r_back", seq(range(5), [40, 50, 50, 60, 80]), [FEET])],
}


def ring(cell, lit):
    """r_out's cell with its blades alone (pieces of 5 px or more), each colour a step lighter on its ramp, and the
    blades of row `lit` (rows of them from the top, RING rows) two steps lighter; lit None: all two steps."""
    a = cell.copy()
    on = a[..., 3] > 0
    seen = np.zeros(on.shape, bool)
    blades = []
    for y0, x0 in zip(*np.nonzero(on)):
        if seen[y0, x0]:
            continue
        stack, comp = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    v, u = y + dy, x + dx
                    if 0 <= v < on.shape[0] and 0 <= u < on.shape[1] and on[v, u] and not seen[v, u]:
                        seen[v, u] = True
                        stack.append((v, u))
        if len(comp) < 5:
            for y, x in comp:
                a[y, x] = 0
        else:
            blades.append(comp)
    order = sorted(range(len(blades)), key=lambda i: np.mean([y for y, _ in blades[i]]))
    row = {i: r * RING // len(blades) for r, i in enumerate(order)}
    step = {}
    for name in ("STEEL", "GLEAM", "SHADE"):
        ramp = RAMPS[name]
        for i, h in enumerate(ramp):
            step[h] = ramp[i + 1:] + [ramp[-1]] * 2
    for i, comp in enumerate(blades):
        k = 1 if lit is None or row[i] == lit else 0
        for y, x in comp:
            h = "%02X%02X%02X" % tuple(a[y, x, :3])
            if h in step:
                a[y, x, :3] = [int(step[h][k][j:j + 2], 16) for j in (0, 2, 4)]
    return a
FLIP_TB = {"w_out", "w_back"}


def build(table):
    with open(G.lp(os.path.join(SRC, "talon_fx_anchors.json")), encoding="utf-8") as f:
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
                cell = ring(strip[k[1]], k[2]) if isinstance(k, tuple) else strip[k]
                f = J.place(cell, anchors[src]["anchor"], spots)
                f = X.over_flip(f, "tb" if tag in FLIP_TB else "lr")
                out[tag].append((f, ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_talon_fx", FX), ("league_talon_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
