#!/usr/bin/env python3
"""Import Gwen's effects (assets/source/gwen/PROMPTS_FX.md, 16 sheets) as the game sheets league_gwen_fx and
league_gwen_big, and the pictures that point into her own frames (assets/source/native/gwen_bake.json).

    python tools/art/import_gwen.py --raw <Codex's gwen-fx folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_gwen.py                                 # native strips -> the effect sheets
    python tools/art/import_native.py --hero gwen                   # then: the bake into her frames

Codex delivered generated originals (about 2172x724, semi-transparent edges, the frames in equal columns - the R
volleys in one column, the mist in two rows: its HANDOFF.md). --raw turns each frame into a cell of a native strip
(assets/source/gwen/gwen_fx_<name>.png, 8x, plus gwen_fx_anchors.json) as import_samira.py does: each game pixel the
majority colour of the source pixels it covers, opaque when a quarter of them are solid, every colour snapped to the
ramps the pack gave that effect, the darkest shade off the edge of light (import_jhin.unrim; the Q stack mark keeps its
dark outline). One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m), or
over the cell's width (cw: the volleys, whose needles travel across a cell as wide as the line).

Red side and blue side alike: the client mirrors her own frames with her facing and never an effect picture, so
- what points and rides on her is drawn into her frames (gwen_bake.json): the attack's snip at the scissors' point,
  Q's cuts in front of the blades, E's thread trail behind the skip;
- the volleys are mirrored top to bottom about their middle row (cast leftward the engine turns them upside down);
- what plays on her or on the ground whichever way she faces - E's threads, the mist and its veil, the bind on slowed
  enemies - is mirrored left to right about its middle; the stack marks are placed by this script, four slots in a row.
Spots (game px from the pivot, x forward, y down; her soles 11 under it, the standing point 12) come from the finished
strips (tools/art/rig_gwen.py, pack_gwen_fx.rig_points): the attack's point (+47, -12) in its thrust frame, the blades'
middle (+30 / +31, -12) in Q's shut frames. Times from the strips (rig_gwen.MS) and the kit (60 ticks a second).
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
import import_twistedfate as TF  # noqa: E402
import import_varus as V  # noqa: E402
import import_xerath as X  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gwen")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (tools/art/pack_gwen_fx.py)
RAMPS = {
    "HOLY": ["105C8E", "1E9ECB", "4CD8F2", "A8F4FF", "E6FFFF", "FFFFFF"],
    "SILVER": ["565E94", "8C96C4", "C4CCEC", "EEF2FF", "FFFFFF"],
    "MIST": ["4C8CB4", "7CC0DA", "B4E2EE", "E2F6FA", "FFFFFF"],
    "INK": ["0A1A2A"],                       # the stack mark's outline
}
# light's darkest shade on its edge goes (or takes the next)
RIM = {"105C8E": "1E9ECB", "565E94": "8C96C4", "4C8CB4": "7CC0DA"}

# raw -> native: frames n (rows: grid rows), size (game px) over measure, anchor, ramps, sym ("lr" / "tb"), rim
RAW = {
    "a_snip": dict(n=3, size=18, measure="w", anchor=("fixed", "left", 0), ramps="HOLY"),
    "q_snip": dict(n=3, size=30, measure="w", anchor=("fixed", "core", 0), ramps="HOLY"),
    "q_final": dict(n=4, size=44, measure="w", anchor=("fixed", "core", 0), ramps="HOLY"),
    "e_dash": dict(n=3, size=34, measure="w", anchor=("fixed", "box", 1), ramps="HOLY"),
    "a_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="HOLY"),
    "q_hit": dict(n=3, size=12, measure="m", anchor=("fixed", "core", 0), ramps="HOLY"),
    "q_true": dict(n=4, size=20, measure="m", anchor=("fixed", "core", 0), ramps="HOLY"),
    "r_hit": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0), ramps="HOLY SILVER"),
    "w_mist": dict(n=8, rows=2, size=74, measure="w", anchor=("fixed", "box", 2), ramps="MIST", sym="lr", sheer=True),
    "qs_marks": dict(n=4, size=6, measure="h", anchor="box", ramps="INK HOLY", rim=False),
    "e_on": dict(n=4, size=40, measure="h", anchor=("fixed", "box", 3), ramps="HOLY", sym="lr", open_=8),
    "w_in": dict(n=4, size=44, measure="h", anchor=("fixed", "box", 0), ramps="MIST", sym="lr", open_=9, top=7),
    "r_slow": dict(n=4, size=24, measure="w", anchor=("fixed", "box", 0), ramps="HOLY SILVER", sym="lr"),
    "r_v1": dict(n=6, rows=6, size=82, measure="cw", anchor="cell", ramps="HOLY SILVER", sym="tb"),
    "r_v3": dict(n=6, rows=6, size=82, measure="cw", anchor="cell", ramps="HOLY SILVER", sym="tb"),
    "r_v5": dict(n=6, rows=6, size=82, measure="cw", anchor="cell", ramps="HOLY SILVER", sym="tb"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def open_middle(out, cell, anc, n, half, top=0):
    """Her place cleared in a picture drawn over her (the veil and the threads whited her out): the columns within
    `half` of the anchor, every row but the `top` ones (the knot over her head)."""
    tw, th = cell
    L, _ = anc
    for i in range(n):
        out[top:, i * tw + L - half:i * tw + L + half + 1] = 0


def sheer(out):
    """The mist's flat fill let through every other square (it lay on the ground as a white slab): squares of the two
    commonest colours more than two squares inside its edge go in a checkerboard; the rim, the wisps and the threads
    (the other shades) stay."""
    op = out[..., 3] > 0
    cols, counts = np.unique(out[op][:, :3], axis=0, return_counts=True)
    fill = [tuple(c) for c in cols[np.argsort(counts)[-2:]]]
    inner = op.copy()
    for _ in range(2):
        inner = inner & np.roll(inner, 1, 0) & np.roll(inner, -1, 0) & np.roll(inner, 1, 1) & np.roll(inner, -1, 1)
    yy, xx = np.indices(op.shape)
    hit = inner & ((yy + xx) % 2 == 0) & np.isin(out[..., 0].astype(int) * 65536 + out[..., 1].astype(int) * 256 + out[..., 2],
                                                 [int(c[0]) * 65536 + int(c[1]) * 256 + int(c[2]) for c in fill])
    out[hit] = 0


def drawing_w(solid, rects):
    w = 0
    for x, y, rw, rh in rects:
        xs = np.nonzero(solid[y:y + rh, x:x + rw].any(0))[0]
        if len(xs):
            w = max(w, xs.max() + 1 - xs.min())
    return w


def from_raw(folder):
    V.TF = TF
    anchors = {}
    for name, spec in RAW.items():
        V.RIM = RIM if spec.get("rim", True) else {}      # import_varus.convert's unrim reads its module's RIM
        J.RIM = V.RIM
        fn = f"gwen_fx_{name}.png"
        _, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rows = spec.get("rows", 1)
        if rows == spec["n"]:                    # one column: grid() reads n // rows columns
            H = a.shape[0]
            rects = [[0, round(r * H / rows), a.shape[1], round((r + 1) * H / rows) - round(r * H / rows)]
                     for r in range(rows)]
        else:
            rects = V.grid(a, spec["n"], rows)
        sp = dict(spec)
        if spec["measure"] == "cw":              # the cell's width is the line's length
            sp["measure"] = "w"
            sp["size"] = spec["size"] * drawing_w(solid, rects) / rects[0][2]
        out, cell, anc, s, ext = V.convert(name, sp, a, solid, idx, pal, rects)
        if spec.get("sym"):
            X.symmetric(out, cell, anc, spec["n"], spec["sym"])
        if spec.get("open_"):
            open_middle(out, cell, anc, spec["n"], spec["open_"], spec.get("top", 0))
        if spec.get("sheer"):
            sheer(out)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"gwen_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": spec["n"]}
        print(f"gwen_fx_{name}.png  {spec['n']} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({sp['size']:.1f} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "gwen_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"gwen_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"gwen_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x forward, y down), from the finished strips (pack_gwen_fx.rig_points; measured again
# when she was made smaller - 42 rows, the held blade 27 long, the far hand 3 rows lower)
POINT = (40, -9)                # the attack's thrust (frame 4): the snip's bright left end 4 in from the scissors' point
                                # (+44) so the X stays inside her 128-wide cell
BLADES_Q = (29, -9)             # Q's shut frames 3 and 5: the blades' middle, the cut's crossing on it
BLADES_F = (30, -9)             # Q's frame 7 (one column further: the lunge)
DASH = (-17, -1)                # E's trail: its box middle behind her, knee to chest
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
BODY = (0, -8)                  # round her: E's threads, the mist's veil
GROUND = (0, 12)                # the standing point: the mist's middle, the bind round the ankles
OVER = (0, -34)                 # the stack marks over her head (her crown 28 over the pivot)
SLOTS = (-9, -3, 3, 9)          # the four stack marks' columns from her middle
LINE = (0, 0)                   # a LineRangeProjectile's picture is centred on its line
EMPTY = J.EMPTY
seq = J.seq

MIST_LOOP = [k for _ in range(7) for k in (2, 3, 4, 5)]      # 28 x 130 ms + the rise and the fade: the 4 s (240 ticks)
FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_hit": [("q_hit", seq(range(3), [40, 50, 60]), [HIT])],
    "q_true": [("q_true", seq(range(4), [50, 60, 70, 80]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_on": [("e_on", seq(range(4), [110] * 4), [BODY])],
    "w_in": [("w_in", seq(range(4), [130] * 4), [BODY])],
    "r_slow": [("r_slow", seq(range(4), [110] * 4), [GROUND])],
    # baked into her frames (gwen_bake.json)
    "a_snip": [("a_snip", seq(range(3), [40, 50, 60]), [POINT])],
    "q_snip": [("q_snip", seq(range(3), [30, 40, 50]), [BLADES_Q])],
    "q_final": [("q_final", seq(range(4), [50, 60, 70, 80]), [BLADES_F])],
}
BIG = {
    "w_mist": [("w_mist", seq([0, 1] + MIST_LOOP + [6, 7], [100, 120] + [130] * len(MIST_LOOP) + [150, 160]),
                [GROUND])],
    # the volleys: built by volley() (the lines live 11 ticks, r_delay 12)
    # baked into her frames: E's trail over the skip (skill2 frames 1-3, 120 ms)
    "e_dash": [("e_dash", seq(range(3), [40, 40, 50]), [DASH])],
}


def marks(anchors):
    """qs1..qs4: one frame each, the mark (Codex's first cell) in slot k over her head (pack: cell k holds slot k)."""
    c = cells("qs_marks", anchors["qs_marks"]["frames"])[0]
    ys, xs = np.nonzero(c[..., 3])
    m = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    anc = ((m.shape[1]) / 2, (m.shape[0]) / 2)
    return {f"qs{k + 1}": [(J.place(m, anc, [(OVER[0] + dx, OVER[1])]), 1000)] for k, dx in enumerate(SLOTS)}


VOLLEYS = {"r_v1": "r_v1", "r_v2": "r_v3", "r_v3": "r_v5"}    # kit tag -> Codex's sheet (1, 3, 5 needles)
TIPS = (-24, -10, 4, 18, 32, 40)        # the needles' points along the 80-px line from its middle, frame by frame
VOLLEY_MS = [30] * 5 + [200]


def volley(src, anchors):
    """Six frames of the needles flying along the line at an even pace: Codex's fullest frame of the sheet (its rows
    were not aligned and the last ones cut at the edge), the same group moved forward each frame, its rows kept about
    the line (the strip is mirrored top to bottom about it)."""
    strip = cells(src, anchors[src]["frames"])
    best = max(strip, key=lambda c: int((c[..., 3] > 0).sum()))
    xs = np.nonzero((best[..., 3] > 0).any(0))[0]
    g = best[:, xs.min():xs.max() + 1]
    U = anchors[src]["anchor"][1]
    out = []
    for tip, ms in zip(TIPS, VOLLEY_MS):
        out.append((J.place(g, (g.shape[1] - 0.5, U), [(LINE[0] + tip, LINE[1])]), ms))
    return out


def build(table):
    with open(G.lp(os.path.join(SRC, "gwen_fx_anchors.json")), encoding="utf-8") as f:
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
    if table is FX:
        out.update(marks(anchors))
    else:
        out.update({tag: volley(src, anchors) for tag, src in VOLLEYS.items()})
    return out


# the pictures drawn into her frames (import_native.bake): the strips' times (rig_gwen.MS)
BAKE = {"fx": "league_gwen_fx", "items": [
    {"tag": "a_snip", "into": "attack", "at_ms": 190},              # attack 4: 190-260 ms
    {"tag": "q_snip", "into": "skill", "at_ms": 110},               # skill 3 (shut): 110-170
    {"tag": "q_snip", "into": "skill", "at_ms": 230},               # skill 5 (shut): 230-290
    {"tag": "q_final", "into": "skill", "at_ms": 360},              # skill 7 (shut after the wide snip): 360-440
    {"tag": "e_dash", "into": "skill2", "at_ms": 0, "fx": "league_gwen_big"},   # the skip, frames 1-3
]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_gwen_fx", FX), ("league_gwen_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    text = json.dumps(BAKE, indent=1) + "\n"
    with open(G.lp(os.path.join(NATIVE, "gwen_bake.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("assets/source/native/gwen_bake.json:", len(BAKE["items"]), "items")


if __name__ == "__main__":
    main()
