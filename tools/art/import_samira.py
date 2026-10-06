#!/usr/bin/env python3
"""Import Samira's effects (assets/source/samira/PROMPTS_FX.md, 23 sheets) as the game sheets league_samira_fx and
league_samira_big, and the pictures that point into her own frames (assets/source/native/samira_bake.json).

    python tools/art/import_samira.py --raw assets/source/samira/codex_fx   # once: Codex's PNGs -> native strips
    python tools/art/import_samira.py                                      # native strips -> the effect sheets
    python tools/art/import_native.py --hero samira                        # then: the bake into her frames

Codex delivered generated originals (about 2172x724, semi-transparent edges, the frames in equal columns: its
HANDOFF.md). --raw turns each frame into a cell of a native strip (assets/source/samira/samira_fx_<name>.png, 8x, plus
samira_fx_anchors.json) the way import_xerath.py does: each game pixel the majority colour of the source pixels it
covers, opaque when a quarter of them are solid, every colour snapped to the ramps the pack gave that effect, then the
fire's darkest shade comes off its edge (import_jhin.unrim; the Style letters keep their dark outline). One scale per
strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m).

Red side and blue side alike (the user: 「注意红色方和蓝色方的技能特效不要不对称 导致歪的」): the client mirrors her own
frames with her facing and never an effect picture, so
- every picture with a front and a back that rides on her is drawn into her frames (samira_bake.json): the muzzle
  flashes (attack, Q, both pistols in R), the sword's chop arc, Q's half-moon sweep (skill_m), E's dash trail (skill2);
- the bullets are mirrored top to bottom about their middle row (cast leftward the engine turns them upside down);
- what plays on her whichever way she faces - the whirl ring, R's storm, the reset and Style flashes - is mirrored
  left to right about its middle; the Style letters are never mirrored (they read the same both ways round).
Spots (game px from the pivot, x forward, y down; her soles 11 under it) come from the finished strips
(tools/art/rig_samira.py; pack_samira_fx.SHOTS): the muzzle in the attack's firing frame (+23, -11.5), Q's (+23, -12.5),
R's pistols (+24 / -26.5, by frame). Times from the strips (rig_samira.MS) and the kit (60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "samira")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (tools/art/pack_samira_fx.py)
RAMPS = {
    "GUN": ["9E2208", "E8520E", "FF9A1E", "FFD24A", "FFF4C2", "FFFFFF"],
    "BLADE": ["6E0A18", "C8102A", "F0402A", "FF8A64", "FFE2D2", "FFFFFF"],
    "ROSE": ["7E1230", "C8264A", "F25A7E", "FFB4C4"],
    "GOLD": ["A85A08", "E89A10", "FFD040", "FFF0A0", "FFFFFF"],
    "SAND": ["6E5232", "A8844E", "D2B07C", "F2DDB4"],
    "INK": ["1A0A0E"],                       # the Style letters' outline
}
# the fire's darkest shade on its edge goes (or takes the next)
RIM = {"9E2208": "E8520E", "6E0A18": "C8102A", "7E1230": "C8264A", "A85A08": "E89A10", "6E5232": "A8844E"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, sym ("lr" / "tb"), rim (False: keep it),
# hollow (half width: the columns over the ring's middle row cleared - drawn over her, its far side crossed her chest)
RAW = {
    "a_bullet": dict(n=4, size=12, measure="w", anchor="front", ramps="GUN", sym="tb"),
    "q_bullet": dict(n=4, size=22, measure="w", anchor="front", ramps="GUN", sym="tb"),
    "r_bullet": dict(n=3, size=16, measure="w", anchor="front", ramps="GUN", sym="tb"),
    "a_flash": dict(n=3, size=14, measure="w", anchor=("fixed", "left", 0), ramps="GUN"),
    "q_flash": dict(n=3, size=20, measure="w", anchor=("fixed", "left", 0), ramps="GUN"),
    "r_flash": dict(n=2, size=10, measure="w", anchor=("fixed", "left", 0), ramps="GUN"),
    "a_hit": dict(n=4, size=12, measure="m", anchor=("fixed", "core", 0), ramps="GUN"),
    "a_slash": dict(n=3, size=28, measure="h", anchor=("fixed", "box", 0), ramps="BLADE"),
    "a_slash_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="BLADE"),
    "j_up": dict(n=4, size=28, measure="h", anchor=("fixed", "low", 0), ramps="BLADE SAND"),
    "q_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="GUN"),
    "q_slash": dict(n=4, size=40, measure="h", anchor=("fixed", "box", 1), ramps="BLADE"),
    "q_slash_hit": dict(n=4, size=18, measure="m", anchor=("fixed", "core", 0), ramps="BLADE"),
    "e_dash": dict(n=4, size=44, measure="w", anchor=("fixed", "box", 1), ramps="BLADE SAND"),
    "e_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="BLADE SAND"),
    "e_reset": dict(n=4, size=22, measure="m", anchor=("fixed", "box", 1), ramps="GOLD", sym="lr"),
    "w_spin": dict(n=4, size=60, measure="w", anchor=("fixed", "box", 0), ramps="BLADE", sym="lr", hollow=12),
    "w_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="BLADE"),
    "r_on": dict(n=4, size=64, measure="w", anchor=("fixed", "box", 0), ramps="GUN BLADE ROSE", sym="lr", hollow=11),
    "r_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="GUN ROSE"),
    "g_letters": dict(n=6, size=13, measure="h", anchor="box", ramps="INK GOLD BLADE", rim=False),
    "g_up": dict(n=3, size=16, measure="m", anchor=("fixed", "box", 0), ramps="GOLD", sym="lr"),
    "g_s": dict(n=4, size=28, measure="m", anchor=("fixed", "box", 1), ramps="GOLD BLADE", sym="lr"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def from_raw(folder):
    V.TF = TF
    anchors = {}
    for name, spec in RAW.items():
        V.RIM = RIM if spec.get("rim", True) else {}      # import_varus.convert's unrim reads its module's RIM
        J.RIM = V.RIM
        fn = f"samira_fx_{name}.png"
        _, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        idx = J.snap(a, solid, pal)
        rects = V.grid(a, spec["n"])
        out, cell, anc, s, ext = V.convert(name, spec, a, solid, idx, pal, rects)
        if spec.get("sym"):
            X.symmetric(out, cell, anc, spec["n"], spec["sym"])
        if spec.get("hollow"):                   # the ring's far side passes behind her: her columns over its middle
            X.hollow(out, cell, anc, spec["n"], spec["hollow"])
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"samira_fx_{name}.png")))
        anchors[name] = {"cell": list(cell), "anchor": list(anc), "frames": spec["n"]}
        print(f"samira_fx_{name}.png  {spec['n']} cells of {cell[0]}x{cell[1]}, anchor {anc[0]},{anc[1]}, scale "
              f"{s:.4f} ({spec['size']} px over {ext}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "samira_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"samira_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"samira_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x forward, y down), measured on the finished strips (pack_samira_fx.SHOTS)
MUZZLE_A = (23, -11.5)          # the attack's muzzle in its firing frame (frame 4: the hand at +12, the barrel 9 on): the
                                # flash's bright left end on the barrel's last square
MUZZLE_Q = (22, -12.5)          # Q's firing frame (frame 3)
# R: the far pistol (right) and the near one (left) in the firing frames 2-9; three poses (the arms see-saw)
R_POSES = {"rf_a": ((23, -11.5), (-25.5, -12.5)), "rf_b": ((23, -13.5), (-25.5, -10.5)),
           "rf_c": ((23, -9.5), (-25.5, -14.5))}
R_FRAMES = ["rf_a", "rf_b", "rf_a", "rf_c", "rf_a", "rf_b", "rf_a", "rf_c"]     # ult frames 2-9
SLASH = (19, -10)               # the chop arc's box middle in front of her (attack_m 4: the hand at +15, -6)
Q_SWEEP = (23, -9)              # the half-moon's box middle: its inner edge 6 in front of her, from over her head to
                                # the ground
DASH = (-14, 4)                 # E's trail: its box middle behind her, low
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
WAIST = (0, -3)                 # the whirl ring round her waist
BODY = (0, -8)                  # R's storm round her
OVER = (0, -36)                 # the Style letters and flashes over her head (her crown 28 over the pivot)
SOLES = (0, 11)                 # what stands on the ground: its lowest row there
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

FX = {
    # the bullets: the attack 55 px at 8 px a tick (homing: up to twice that), Q 95 px at 9, R 55 px at 12; out of the
    # muzzle 24 px ahead: 3 empty ticks (2 for R's faster ones)
    "a_bullet": [("a_bullet", flight(4, 60, 300, lead=3), [(0, 0)])],
    "q_bullet": [("q_bullet", flight(4, 60, 400, lead=3), [(0, 0)])],
    "r_bullet": [("r_bullet", flight(3, 60, 250, lead=2), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "a_slash_hit": [("a_slash_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "j_up": [("j_up", seq(range(4), [50, 60, 70, 80]), [SOLES])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_slash_hit": [("q_slash_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_hit": [("e_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "e_reset": [("e_reset", seq(range(4), [60, 70, 80, 90]), [BODY])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "r_hit": [("r_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "g_up": [("g_up", seq(range(3), [50, 60, 70]), [OVER])],
    "g_s": [("g_s", seq(range(4), [60, 70, 80, 100]), [OVER])],
    # baked into her frames (samira_bake.json): each flash ends inside the frame that holds the gun there
    "a_flash": [("a_flash", seq(range(3), [25, 45, 60]), [MUZZLE_A])],
    "q_flash": [("q_flash", seq(range(3), [25, 30, 35]), [MUZZLE_Q])],
    "a_slash": [("a_slash", seq(range(3), [40, 50, 60]), [SLASH])],
    # the Style letters (buffs, looped while they last): E D C B A S
    **{f"g{k + 1}": [("g_letters", [(k, 1000)], [OVER])] for k in range(6)},
}
BIG = {
    "w_spin": [("w_spin", seq(range(4), [90] * 4), [WAIST])],
    "r_on": [("r_on", seq(range(4), [100] * 4), [BODY])],
    # baked into her frames: Q's sweep into skill_m from its slash frame, E's trail into skill2's dash
    "q_slash": [("q_slash", seq(range(4), [40, 60, 60, 60]), [Q_SWEEP])],
    "e_dash": [("e_dash", seq(range(4), [40, 40, 45, 45]), [DASH])],
}


def r_flash_frames(strip, anc, pose):
    """Both pistols' flashes in one frame per picture: the far one as drawn (pointing right), the near one mirrored."""
    out = []
    right, left = R_POSES[pose]
    for k, ms in zip(range(2), [50, 70]):
        c = strip[k]
        m = c[:, ::-1].copy()
        ma = (c.shape[1] - 1 - anc[0], anc[1])
        a = J.place(c, anc, [right])
        b = J.place(m, ma, [left])
        out.append((overlay(a, b), ms))
    return out


def overlay(a, b):
    """Two pivot-centred frames into one."""
    h, w = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])
    h, w = h | 1, w | 1
    c = np.zeros((h, w, 4), np.uint8)
    for f in (a, b):
        y0, x0 = (h - f.shape[0]) // 2, (w - f.shape[1]) // 2
        sub = c[y0:y0 + f.shape[0], x0:x0 + f.shape[1]]
        m = f[..., 3] > 0
        sub[m] = f[m]
    return c


def build(table):
    with open(G.lp(os.path.join(SRC, "samira_fx_anchors.json")), encoding="utf-8") as f:
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
                anc = anchors[src]["anchor"]
                if src == "g_letters":               # each letter on its own box middle
                    c = strip[k]
                    ys, xs = np.nonzero(c[..., 3])
                    anc = [(xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2]
                out[tag].append((J.place(strip[k], anc, spots), ms))
    if table is FX:
        strip = cells("r_flash", anchors["r_flash"]["frames"])
        for pose in R_POSES:
            out[pose] = r_flash_frames(strip, anchors["r_flash"]["anchor"], pose)
    return out


# the pictures drawn into her frames (import_native.bake): the strips' times (rig_samira.MS)
BAKE = {"fx": "league_samira_fx", "items": [
    {"tag": "a_flash", "into": "attack", "at_ms": 180},             # attack 4 shows 180-250 ms
    {"tag": "q_flash", "into": "skill", "at_ms": 120},              # skill 3: 120-210
    {"tag": "a_slash", "into": "attack_m", "at_ms": 140},           # attack_m 4: 140-230, held to 330
    {"tag": "q_slash", "into": "skill_m", "at_ms": 140, "fx": "league_samira_big"},   # skill_m 4: 140-240
    {"tag": "e_dash", "into": "skill2", "at_ms": 0, "fx": "league_samira_big"},       # the dash, frames 1-3
    *[{"tag": pose, "into": "ult", "at_ms": 150 + 184 * i} for i, pose in enumerate(R_FRAMES)],
]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_samira_fx", FX), ("league_samira_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    text = json.dumps(BAKE, indent=1) + "\n"
    with open(G.lp(os.path.join(NATIVE, "samira_bake.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("assets/source/native/samira_bake.json:", len(BAKE["items"]), "items")


if __name__ == "__main__":
    main()
