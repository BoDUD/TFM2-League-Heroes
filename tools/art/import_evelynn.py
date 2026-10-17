#!/usr/bin/env python3
"""Import Evelynn's effects (assets/source/evelynn/PROMPTS_FX.md, 31 sheets) as the game sheets league_evelynn_fx and
league_evelynn_big.

    python tools/art/import_evelynn.py --raw <Codex's delivery folder>   # once: Codex's PNGs -> native strips
    python tools/art/import_evelynn.py                                   # native strips -> the effect sheets

The body comes from import_native.py (tools/art/fix_evelynn_strips.py built the strips). --raw turns each frame of
Codex's generated drawings (its cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]) into a cell of a native
strip (assets/source/evelynn/evelynn_fx_<name>.png, 8x, plus evelynn_fx_anchors.json) the way import_twistedfate.py does:
each game pixel the majority colour of the source pixels it covers, opaque when a quarter of them are solid, every colour
snapped to the ramps the pack gave that effect (PINK: the hearts, spikes and slashes; VIOLET: the lashes' light, streaks
and rings; SHADE: Demon Shade's and R's smoke), then the darkest shade comes off the rims of the glows (an edge pixel in
a ramp's darkest shade goes when two lighter neighbours hold the shape, else it takes the next shade). One scale per
strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m) - over one frame's (`of`) for the
shade's three strips, which share a frame (sh_in 5 = sh_loop 1 = sh_out 1) and so must share the scale and the anchor.
Anchors (source pixels): the hits on their white flash (core), the hand flashes on the star's left end (left), the
flying lash, spikes and curse on their head (front: 3 game px in from the front end), the marks over the head and the
rings round the body on the drawing's box (box), the dash trail on its left end (lmid), the smoke on its lowest row
(low), the ground rings on their widest lower row (ellipse).
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot), the caster's hands measured on the strips (Codex's manifest, `release_hand`): Q's hand in skill 3 (17, -12),
W's in skill2 2 (13, -12) - and times it by the kit (work/ev/build_evelynn.py, 60 ticks a second): the flying lash,
spikes and curse start with empty ticks (a projectile's first move points its picture up, import_lucian.py's RAY_SKIP;
they leave her pivot, so each stays unseen until it is past her hand) and loop over their longest flight; R's slash is
a view-only line crawling 30 ticks at the champion picked, drawn 20 px ahead of her (the cone's middle).
Writes league/effects/league_evelynn_fx and league_evelynn_big (the dash trail, R and the shade).
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
import import_twistedfate as TW  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "evelynn")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/ev/fx_pack_ev.py)
RAMPS = {
    "PINK": ["6E1240", "C0306A", "F05AA0", "FF9ACA", "FFE0F0", "FFFFFF"],
    "VIOLET": ["3A1A70", "7034C8", "A468F0", "D2A4FF", "F4DEFF", "FFFFFF"],
    "SHADE": ["2A0E5C", "4A1C96", "7A34D2", "A468F0", "D2A4FF"],
}
RIM = {"6E1240": "C0306A", "3A1A70": "7034C8", "2A0E5C": "4A1C96"}

# raw strip -> native: frames n, size (game px) over measure (of frame `of` when given), anchor, ramps
RAW = {
    "a_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="PINK VIOLET"),
    "e_hit": dict(n=5, size=18, measure="m", anchor="core", ramps="VIOLET PINK"),
    "e2_trail": dict(n=5, size=48, measure="w", anchor=("fixed", "lmid", 2), ramps="SHADE PINK"),
    "e2_hit": dict(n=5, size=22, measure="m", anchor="core", ramps="PINK VIOLET"),
    "e_emp": dict(n=4, size=24, measure="w", anchor=("fixed", "box", 0), ramps="VIOLET"),
    "e_haste": dict(n=4, size=24, measure="w", anchor=("fixed", "box", 0), ramps="VIOLET"),
    "q_cast": dict(n=4, size=14, measure="w", anchor="left", ramps="PINK VIOLET"),
    "q_lash": dict(n=4, size=18, measure="w", anchor="front", ramps="PINK VIOLET"),
    "q_spike": dict(n=3, size=20, measure="w", anchor="front", ramps="PINK VIOLET"),
    "q_hit": dict(n=4, size=14, measure="m", anchor="core", ramps="PINK VIOLET"),
    "q_mark": dict(n=4, size=10, measure="w", anchor=("fixed", "box", 0), ramps="PINK VIOLET"),
    "qb_hit": dict(n=3, size=10, measure="m", anchor="core", ramps="PINK"),
    "sp_cast": dict(n=3, size=12, measure="m", anchor="core", ramps="PINK VIOLET"),
    "sp_hit": dict(n=3, size=10, measure="m", anchor="core", ramps="PINK"),
    "w_cast": dict(n=4, size=14, measure="w", anchor="left", ramps="PINK"),
    "w_bolt": dict(n=4, size=14, measure="w", anchor="front", ramps="PINK VIOLET"),
    "w_hit": dict(n=4, size=16, measure="m", anchor="core", ramps="PINK"),
    "w_mark": dict(n=4, size=10, measure="w", anchor=("fixed", "box", 0), ramps="PINK"),
    "w_ripen": dict(n=4, size=14, measure="m", anchor=("fixed", "box", 3), ramps="PINK"),
    "w_ripe": dict(n=4, size=10, measure="w", anchor=("fixed", "box", 0), ramps="PINK"),
    "w_pop": dict(n=5, size=20, measure="m", anchor="core", ramps="PINK"),
    "w_charmed": dict(n=6, size=14, measure="w", anchor=("fixed", "box", 0), ramps="PINK"),
    "w_shred": dict(n=4, size=16, measure="w", anchor=("fixed", "box", 0), ramps="PINK VIOLET"),
    "sh_in": dict(n=5, size=40, measure="h", of=4, anchor=("fixed", "low", 4), ramps="SHADE"),
    "sh_loop": dict(n=6, size=40, measure="h", of=0, anchor=("fixed", "low", 0), ramps="SHADE"),
    "sh_out": dict(n=4, size=40, measure="h", of=0, anchor=("fixed", "low", 0), ramps="SHADE"),
    "r_cast": dict(n=5, size=40, measure="h", anchor=("fixed", "box", 2), ramps="PINK VIOLET SHADE"),
    "r_slash": dict(n=6, size=48, measure="w", anchor=("fixed", "box", 2), ramps="PINK VIOLET"),
    "r_hit": dict(n=4, size=20, measure="m", anchor="core", ramps="PINK VIOLET"),
    "r_blink": dict(n=5, size=36, measure="h", anchor=("fixed", "low", 0), ramps="SHADE VIOLET"),
    "r_land": dict(n=4, size=28, measure="w", anchor=("fixed", "ellipse", 1), ramps="SHADE PINK"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


def anchor(how, k, a, solid, rects, s=1.0):
    """(x, y) of frame k's anchor in the source: import_twistedfate's, plus `lmid` (the drawing's left end, halfway down
    its box) for a trail that starts where she leaps."""
    if how == "lmid":
        x, y, w, h = rects[k]
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        return x + xs.min(), y + (ys.min() + ys.max() + 1) / 2
    if isinstance(how, tuple) and how[0] == "fixed":
        x, y, _, _ = rects[k]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects, s)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    return TW.anchor(how, k, a, solid, rects, s)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"evelynn_fx_{name}.png"
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
            if not len(xs):
                boxes.append(None)
                continue
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        seen = [b for b in boxes if b]
        if "of" in spec:
            seen = [boxes[spec["of"]]]
        ext = {"w": max(b[1] - b[0] for b in seen), "h": max(b[3] - b[2] for b in seen)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, solid, rects, s) for k in range(len(rects))]
        live = [(c, b) for c, b in zip(anc, boxes) if b]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in live) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in live) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        for i, (x, y, w, h) in enumerate(rects):
            if boxes[i] is None:
                continue
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
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "evelynn_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"evelynn_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"evelynn_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down)
Q_HAND = (17, -12)          # the hand that flings Q in skill 3 (Codex's release_hand)
W_HAND = (13, -12)          # the blowing hand in skill2 2
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
CROWN = (0, -31)            # Hate Spike's thorn crown on the head of a 36-41 px unit
CHARM = (0, -36)            # the hearts circling a charmed head, over the crown
HEART = (0, -42)            # Allure's heart over all of them (the mark, its ripening, ripe): the three show at once
BODY = (0, -10)             # her middle (the empowered whip's glow, the spikes' flash)
CHEST = (0, -14)            # her chest: R's burst
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # the ground under a unit (its soles' row)
DASH = (0, -4)              # where the dash trail starts: her hips as she leaps
SLASH = (20, 0)             # R's slash: 20 px ahead of the crawling line (the cone's middle; radius 45 px)
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "e2_hit": [("e2_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "q_cast": [("q_cast", seq(range(4), [30, 40, 50, 60]), [Q_HAND])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "qb_hit": [("qb_hit", seq(range(3), [40, 50, 60]), [HIT])],
    "sp_cast": [("sp_cast", seq(range(3), [40, 50, 60]), [BODY])],
    "sp_hit": [("sp_hit", seq(range(3), [40, 50, 60]), [HIT])],
    "w_cast": [("w_cast", seq(range(4), [40, 50, 60, 70]), [W_HAND])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_ripen": [("w_ripen", seq(range(4), [50, 60, 70, 80]), [HEART])],
    "w_pop": [("w_pop", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # the buffs' pictures loop while the buff lasts
    "e_emp": [("e_emp", seq(range(4), [110] * 4), [BODY])],
    "e_haste": [("e_haste", seq(range(4), [90] * 4), [FEET])],
    "q_mark": [("q_mark", seq(range(4), [120] * 4), [CROWN])],
    "w_mark": [("w_mark", seq(range(4), [120] * 4), [HEART])],
    "w_ripe": [("w_ripe", seq(range(4), [110] * 4), [HEART])],
    "w_charmed": [("w_charmed", seq(range(6), [90] * 6), [CHARM])],
    "w_shred": [("w_shred", seq(range(4), [120] * 4), [FEET])],
    # the lash: 60 px at 5 px a tick (12 ticks), out of her hand 17 px away: 3 empty ticks
    "q_lash": [("q_lash", flight(4, 50, 240, lead=3), [(0, 0)])],
    # the spikes: 55 px at 6 px a tick (10 ticks), out of her middle: 2 empty ticks
    "q_spike": [("q_spike", flight(3, 50, 170, lead=2), [(0, 0)])],
    # the curse: homing at 9 px a tick, up to 90 px (10 ticks; twice that chasing), 13 px out of her hand: 2 empty ticks
    "w_bolt": [("w_bolt", flight(4, 60, 340, lead=2), [(0, 0)])],
}
BIG = {
    "e2_trail": [("e2_trail", seq(range(5), [50, 60, 70, 80, 90]), [DASH])],
    "r_cast": [("r_cast", seq(range(5), [50, 60, 70, 80, 90]), [CHEST])],
    # the slash crawls 30 ticks (500 ms), shown once; its last frame is empty
    "r_slash": [("r_slash", seq(range(6), [50, 70, 90, 100, 100, 1000]), [SLASH])],
    "r_blink": [("r_blink", seq(range(5), [60, 70, 80, 90, 100]), [SOLES])],
    "r_land": [("r_land", seq(range(4), [50, 60, 70, 80]), [FEET])],
    # Demon Shade: ThreePhase (pre sh_in, loop sh_loop, remove sh_out), on her feet
    "sh_in": [("sh_in", seq(range(5), [70, 80, 80, 90, 90]), [SOLES])],
    "sh_loop": [("sh_loop", seq(range(6), [110] * 6), [SOLES])],
    "sh_out": [("sh_out", seq(range(4), [60, 70, 80, 90]), [SOLES])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "evelynn_fx_anchors.json")), encoding="utf-8") as f:
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
                if not strip[k][..., 3].any():
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
    for sheet, table in (("league_evelynn_fx", FX), ("league_evelynn_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
