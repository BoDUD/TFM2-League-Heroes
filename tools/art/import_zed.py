#!/usr/bin/env python3
"""Import Zed's effects (assets/source/zed/PROMPTS_FX.md, 19 sheets) as the game sheets league_zed_fx and
league_zed_big.

    python tools/art/import_zed.py --raw assets/source/zed/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_zed.py                                  # native strips -> the effect sheets

The body comes from import_native.py (tools/art/rig_zed.py built the strips). --raw turns each frame of Codex's
drawings into a cell of a native strip (assets/source/zed/zed_fx_<name>.png, 8x, plus zed_fx_anchors.json) the way
import_rengar.py does, the frames cut by the delivery's manifest.json rects (an equal grid of `n` cells when it has
none): each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid,
every colour snapped to the ramps the pack gave that effect (work/zd/fx_pack_zd.py: SILVER, SHADOW, RED, SPARK), then
the lights' darkest ring comes off (import_jhin.unrim; the shadow ramp's near-black stays: it is the shadow's inside).
One scale per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m); the sizes are the
pack's, the slash rings the kit's radius (e_r 24000 -> 48 px across), the shadow figure his own height (40 px).
Anchors (source pixels): the shurikens on their front, the hits on their white core, the rings on their widest row, the
shadow figure and the swap column on their lowest row (the feet), the rest on the middle of their box.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot, his crown 28 over it) and times it by the kit (tools/kit/build_zed.py, 60 ticks a second): the shadows'
pictures are one checkpoint long (W echo_step 12 ticks, R r_echo_step 6) - a standing frame, or the shadow's own throw /
spin (sh_q / sh_e, Codex's later delivery assets/source/zed/codex_fx_shadow) where the checkpoint copies his cast.
sh_throw's strip stays from the first delivery; the shadow's throw (sh_q) replaced it in the game.
The red side: the client never mirrors a data picture. The shurikens are turned to their flight - drawn over their own
top-bottom flip; everything on a unit or on the ground is drawn as stored whichever way he faces - drawn over its own
left-right flip (league_xayah's FLIP_TB / FLIP_LR). Every frame is centred on the pivot, so the flips are about it.
Writes league/effects/league_zed_fx and league_zed_big.
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

SRC = os.path.join(ROOT, "assets", "source", "zed")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps (work/zd/fx_pack_zd.py), darkest first
RAMPS = {
    "SILVER": ["3A4258", "5E6A84", "8FA0B7", "C6D0E0", "EEF2FA", "FFFFFF"],
    "SHADOW": ["120A22", "261447", "44287E", "6A48B8", "9A7AE0", "C8B4F4", "F2ECFF"],
    "RED": ["7A0808", "C01410", "F23A24", "FF8A6A", "FFD8C8", "FFFFFF"],
    "SPARK": ["F59A3A", "FFD08A", "FFF2D8", "FFFFFF"],
}
# the lights' darkest shade on their edge goes (or takes the next); the shadow's near-black is its inside and stays
RIM = {"3A4258": "5E6A84", "7A0808": "C01410", "F59A3A": "FFD08A"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=12, measure="m", anchor="core", ramps="SILVER RED SPARK"),
    "cw_hit": dict(n=5, size=18, measure="m", anchor="core", ramps="SHADOW RED"),
    "cw_ready": dict(n=4, size=10, measure="w", anchor=("fixed", "box", 0), ramps="SHADOW RED"),
    "q_star": dict(n=4, size=20, measure="w", anchor="front", ramps="SILVER RED"),
    "sh_star": dict(n=4, size=20, measure="w", anchor="front", ramps="SHADOW RED"),
    "q_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="SILVER RED SPARK"),
    "e_spin": dict(n=5, size=48, measure="w", anchor=("fixed", "ellipse", 2), ramps="SHADOW SILVER"),
    "sh_spin": dict(n=5, size=48, measure="w", anchor=("fixed", "ellipse", 2), ramps="SHADOW RED"),
    "e_hit": dict(n=3, size=10, measure="m", anchor="core", ramps="SHADOW"),
    "e_slow": dict(n=4, size=16, measure="w", anchor=("fixed", "ellipse", 0), ramps="SHADOW"),
    "w_dash": dict(n=4, size=16, measure="w", anchor=("fixed", "box", 1), ramps="SHADOW"),
    "sh_in": dict(n=5, size=42, measure="h", anchor=("fixed", "low", 4), ramps="SHADOW RED"),
    "sh_stand": dict(n=4, size=42, measure="h", anchor=("fixed", "low", 0), ramps="SHADOW RED"),
    "sh_throw": dict(n=3, size=18, measure="m", anchor="core", ramps="SHADOW RED"),
    "sh_out": dict(n=4, size=42, measure="h", anchor=("fixed", "low", 0), ramps="SHADOW RED"),
    # the shadow's own casts (assets/source/zed/codex_fx_shadow): sized so their last frame (arms down, nothing raised)
    # stands as tall as the standing shadow (41 px; Q's first frame lifts the crossed blades over the hood); each frame
    # on its own box's middle over its soles (Codex drew E's spread frame ~15 px right of the others in its cell)
    "sh_q": dict(n=3, size=43, measure="h", anchor="boxlow", ramps="SHADOW RED"),
    "sh_e": dict(n=3, size=42, measure="h", anchor="boxlow", ramps="SHADOW RED"),
    "w_swap": dict(n=5, size=40, measure="h", anchor=("fixed", "low", 0), ramps="SHADOW"),
    "r_hit": dict(n=5, size=24, measure="m", anchor="core", ramps="SHADOW RED"),
    "r_mark": dict(n=4, size=14, measure="w", anchor=("fixed", "box", 0), ramps="SHADOW RED"),
    "r_pop": dict(n=6, size=36, measure="m", anchor="core", ramps="SHADOW RED"),
}


def anchor(how, k, a, solid, rects, s=1.0):
    """import_varus's anchors plus `boxlow`: the middle of frame k's box, on its lowest row."""
    if how == "boxlow":
        x, y, w, h = rects[k]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        return x + (xs.min() + xs.max() + 1) / 2, y + ys.max() + 1
    return VARUS_ANCHOR(how, k, a, solid, rects, s)


VARUS_ANCHOR = V.anchor


def from_raw(folder):
    manifest = {}
    mpath = os.path.join(folder, "manifest.json")
    if os.path.exists(G.lp(mpath)):
        with open(G.lp(mpath), encoding="utf-8-sig") as f:
            m = json.load(f)
        manifest = {os.path.basename(x["file"]): x for x in m.get("assets", [])}
    V.RAMPS = RAMPS
    V.RIM = RIM
    V.anchor = anchor
    apath = os.path.join(SRC, "zed_fx_anchors.json")
    anchors = {}
    if os.path.exists(G.lp(apath)):
        with open(G.lp(apath), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        fn = f"zed_fx_{name}.png"
        if not os.path.exists(G.lp(os.path.join(folder, fn))):
            continue                    # a later delivery holds only its own sheets; the others keep their strips
        hexes_, pal = V.palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        if fn in manifest:
            rects = [list(fr["rect"]) for fr in manifest[fn]["frames"]]
        else:
            rects = V.grid(a, spec["n"])
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames in the manifest, {spec['n']} expected")
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    with open(G.lp(apath), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"zed_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"zed_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the rigged strips (zed_shots.png)
HIT = (0, -12)              # a hit on the upper body of a 36-44 px unit
BODY = (0, -8)              # round his body
FEET = (0, 10)              # a ring on the ground round a unit's feet
GROUND = (0, 11)            # what stands on the ground at a point: the shadow's feet, the swap column's foot
OVER = (0, -34)             # over a head: the Death Mark, the passive's sigil
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
# The shadows are drawn in pieces, one checkpoint long, so a checkpoint that copies his shuriken or slash plays the
# shadow's own cast (sh_q / sh_e) in place of its standing frame - two pictures never overlap: the W shadow's pieces
# last echo_step (12 ticks = 200 ms), the R shadow's r_echo_step (6 ticks = 100 ms; a cast covers two of them).
# The W shadow forms over the 10 ticks before its first checkpoint: 2 ticks, then the combo's slash copy (sh_e8) or the
# rest of the forming; the R shadow forms in one piece.
FADE = [90, 100, 110, 120]
CAST = [66, 67, 67]


FX = {
    # the shurikens: 10000 a tick (20 px) over 70000 (7 ticks); the shadow's flies back to him from up to ~60000
    "q_star": [("q_star", flight(4, 40, 400, lead=1), [(0, 0)])],
    "sh_star": [("sh_star", flight(4, 40, 600, lead=0), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "cw_hit": [("cw_hit", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(3), [40, 60, 80]), [HIT])],
    "w_dash": [("w_dash", seq(range(4), [50, 60, 70, 90]), [BODY])],
    "sh_in_a": [("sh_in", seq(range(2), [16, 17]), [GROUND])],
    "sh_in_b": [("sh_in", seq(range(2, 5), [40, 45, 48]), [GROUND])],
    "sh_in_r": [("sh_in", seq(range(5), [20] * 5), [GROUND])],
    **{f"sh_st{k}": [("sh_stand", [(k, 200)], [GROUND])] for k in range(4)},
    **{f"sh_sr{k}": [("sh_stand", [(k, 100)], [GROUND])] for k in range(4)},
    "sh_q": [("sh_q", seq(range(3), CAST), [GROUND])],
    "sh_e": [("sh_e", seq(range(3), CAST), [GROUND])],
    "sh_e8": [("sh_e", seq(range(3), [40, 45, 48]), [GROUND])],
    "sh_out": [("sh_out", seq(range(4), FADE), [GROUND])],
    "w_swap": [("w_swap", seq(range(5), [40, 60, 70, 80, 90]), [GROUND])],
    # the buffs' loops
    "cw_ready": [("cw_ready", seq(range(4), [120] * 4), [OVER])],
    "e_slow": [("e_slow", seq(range(4), [110] * 4), [FEET])],
    "r_mark": [("r_mark", seq(range(4), [120] * 4), [OVER])],
}
BIG = {
    "e_spin": [("e_spin", seq(range(5), [30, 40, 50, 60, 80]), [FEET])],
    "sh_spin": [("sh_spin", seq(range(5), [30, 40, 50, 60, 80]), [FEET])],
    "r_hit": [("r_hit", seq(range(5), [40, 50, 60, 70, 90]), [HIT])],
    "r_pop": [("r_pop", seq(range(6), [40, 50, 60, 70, 90, 110]), [HIT])],
}
FLIP_TB = {"q_star", "sh_star"}
FLIP_LR = set(FX) - FLIP_TB | set(BIG)


def build(table):
    with open(G.lp(os.path.join(SRC, "zed_fx_anchors.json")), encoding="utf-8") as f:
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
                f = J.place(strip[k], anchors[src]["anchor"], spots)
                f = X.over_flip(f, "tb" if tag in FLIP_TB else "lr")
                out[tag].append((f, ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_zed_fx", FX), ("league_zed_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
