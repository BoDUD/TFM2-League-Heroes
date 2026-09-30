#!/usr/bin/env python3
"""Import Riven's effects (Codex's riven_vfx_pack and riven_fx2_complete) as game sheets.

    python tools/art/import_riven.py --raw <Codex's delivery folder>   # once: the delivery's layers -> native strips
                                                                       # (layers/ or effects/, e.g. riven_redo18b)
    python tools/art/import_riven.py --fx2 <Codex's second delivery>   # once: its effects -> native strips
    python tools/art/import_riven.py                                   # native strips -> effect sheets

Codex drew Riven's effects the way oppi's artists do (art-spec): on her own action strips, frame for frame - the
same 96x96 cells, the same standing points and frame times as assets/source/native/riven_cells.json - and split
each into a layer behind her and one in front of her (the head's area only behind, so nothing covers her face).
Seven sets: Q1 and Q2's green slash arcs, Q3's ground crack, E's shield sweep, W's ground burst, the R's green
energy on the blade and the Wind Slash crescent; every game pixel one flat 8x8 block, alpha 0 or 255, six greens and
whites (#183A2A ... #F6EADB, Q3's rocks two of the design's browns).
--raw checks that and takes the outline off: effects carry none (art-spec; the accepted sheets of league_ahri have
dark pixels on 1-18% of their edge), and Codex ringed every shape in its darkest green #183A2A (67% of Q1's edge).
One pass: a #183A2A pixel on a shape's edge goes when two of its 8 neighbours are lighter (the shape stands on
them), else it takes the next green #2D6940 (thin strokes stay whole); inside a shape it stays, as shading. Writes
assets/source/riven/riven_fx_<set>_<back|front>.png (1x, the delivery's cell layout).
The sheets: every frame cut round its cell's standing point (strips.centre_frame, as import_native cuts the body),
so a CasterViewEffect played with the action's CasterAnimation (both on the action's first tick, `is_follow`)
lands on her frame for frame; the back layers are bound with z -1 (under the units), the front ones with z 1.
Drawn at her own scale they are not resized: Ki Burst's ring reaches 41-42 px to either side and Q3's crack 28-39,
which is where a unit's standing point is still hit - a RangeEffect's radius (25000 and 26000) plus the collision
radii of the caster and the unit tested, about 17000 together (league_garen E began 45 px from its target at a range
of 28000). The rings of the heroes before her were drawn at the bare radius (2 px a 1000).
Wind Slash's flying wave, r_wave, is made from Codex's own drawing, unscaled: the crescent of the slash's front
layer (frames 3 and 4, a two-frame loop) cut round the point 15 px over the standing point - the projectile carries
it with y_offset -15000 - so on the release tick it stands where the slash drew it (11-42 px ahead of her) and then
flies on; made exactly symmetric about its middle row (the game turns a projectile's picture to its flight: leftward
it is turned 180 degrees). The front layer itself is not bound (it would stay behind as a second crescent).
The second delivery (assets/source/riven/PROMPTS_FX2.md, the effects the first one left out) came as effects drawn
in their own cells, each with an anchor (the manifest's `cell`, `anchor`, `ms`): --fx2 checks them the same way
(8x blocks, alpha, the effects' palette plus Q3's two rock browns for the knock-up, the frames and times the pack
asked for), takes any dark rim off and writes assets/source/riven/riven_fx2_<name>.png (1x) and
riven_fx2_cells.json. Every frame is cut round the unit's standing point, FX2's `unit` away from the anchor: the
hits 8 px under their anchor (on the chest), the stun ring 28 px over the head's standing point, the rune glyphs
40 px over hers and 8 px apart (one glyph a rune: rune_1, rune_2, rune_3), the knock-up, the shield and the R aura on
it. The shield is split into its three phases (shield_in 1-2, shield 3-6, shield_out 7-8) for a ThreePhase buff view.
Writes league/effects/league_riven_fx (q1, q2, q3, r_slash back layers, r_wave, the hits, knock-up, stun, runes) and
league/effects/league_riven_big (e, w, r_on, the shield, the R aura).
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

SRC = os.path.join(ROOT, "assets", "source", "riven")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
Z = 8
CELL = 96
RIM = (0x18, 0x3A, 0x2A)
NEXT = (0x2D, 0x69, 0x40)
PALETTE = {RIM, NEXT, (0x4B, 0xA8, 0x5A), (0x87, 0xD4, 0x6A), (0xC9, 0xEF, 0x9A), (0xF6, 0xEA, 0xDB),
           (0x49, 0x33, 0x28), (0x86, 0x74, 0x69)}
SETS = {"q1": "skill", "q2": "q2", "q3": "q3", "e": "skill2", "w": "skill2", "r_on": "ult", "r_slash": "r_slash"}
SHEETS = {"league_riven_fx": ["q1", "q2", "q3"], "league_riven_big": ["e", "w", "r_on"]}
WAVE_LIFT = 15                  # px: the projectile's y_offset -15000 lifts its picture this far
# the second delivery: sheet, where the unit's standing point is from the anchor, the shield's phases
FX2 = {"hit": ("league_riven_fx", (0, 8)), "rune_hit": ("league_riven_fx", (0, 8)),
       "q_hit": ("league_riven_fx", (0, 8)), "r_hit": ("league_riven_fx", (0, 8)),
       "knockup": ("league_riven_fx", (0, 0)), "stun": ("league_riven_fx", (0, 28)),
       "shield": ("league_riven_big", (0, 0)),
       # the rune glyphs float over her head: 40 px over the standing point at 46 rows, 34 at 40 rows
       "rune_1": ("league_riven_fx", (8, 34)), "rune_2": ("league_riven_fx", (0, 34)),
       "rune_3": ("league_riven_fx", (-8, 34)),
       "r_aura": ("league_riven_big", (0, 0))}
PHASES = {"shield": {"shield_in": (0, 2), "shield": (2, 6), "shield_out": (6, 8)}}
ROCKS = {(0x86, 0x74, 0x69), (0x49, 0x33, 0x28)}
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def unrim(a):
    """The dark outline off: edge pixels of the darkest green go where two lighter neighbours hold the shape, else
    they take the next green."""
    a = a.copy()
    op = a[..., 3] > 0
    rim = op & np.all(a[..., :3] == np.array(RIM, np.uint8), -1)
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    a[target & (lit >= 2)] = 0
    a[target & (lit < 2), :3] = NEXT
    return a


def load_blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    if a.shape[0] % Z or a.shape[1] % Z:
        sys.exit(f"{path}: not a multiple of {Z}")
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    if not np.isin(a[..., 3], [0, 255]).all():
        sys.exit(f"{path}: semi-transparent pixels")
    return b[:, 0, :, 0].copy()


def from_raw(folder):
    with open(G.lp(os.path.join(NATIVE, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        manifest = json.load(f)["effects"]
    layers = "layers" if os.path.isdir(G.lp(os.path.join(folder, "layers"))) else "effects"   # the redo deliveries
    for name, tag in SETS.items():
        frames = manifest[name]["frames"]
        rows = cells["tags"][tag]
        if all("pivot" in f for f in frames):
            want = [(tuple(f["pivot"]), f.get("duration_ms", f.get("ms"))) for f in frames]
            if want != [(tuple(f["pivot"]), f["ms"]) for f in rows]:
                sys.exit(f"{name}: frames differ from the {tag} cells")
        cols = layout(len(rows))
        size = (-(-len(rows) // cols) * CELL, cols * CELL)
        for layer in ("back", "front"):
            a = load_blocks(os.path.join(folder, layers, f"riven_fx_{name}_{layer}.png"))
            if a.shape[:2] != size:
                sys.exit(f"{name} {layer}: {a.shape[1]}x{a.shape[0]}, not the {tag} strip's {size[1]}x{size[0]}")
            extra = {tuple(int(v) for v in c) for c in a[a[..., 3] > 0][:, :3]} - PALETTE
            if extra:
                sys.exit(f"{name} {layer}: colours outside the effects' palette: {sorted(extra)}")
            b = unrim(a)
            Image.fromarray(b).save(G.lp(os.path.join(SRC, f"riven_fx_{name}_{layer}.png")))
            rim = lambda x: int((np.all(x[..., :3] == np.array(RIM, np.uint8), -1) & (x[..., 3] > 0)).sum())  # noqa: E731
            print(f"riven_fx_{name}_{layer}.png: {len(rows)} frames, dark green {rim(a)} -> {rim(b)} px")


def from_fx2(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        manifest = json.load(f)["effects"]
    table = {}
    for name in FX2:
        m = manifest[f"riven_fx_{name}.png"]
        (w, h), n = m["cell"], m["frames"]
        if len(m["ms"]) != n:
            sys.exit(f"{name}: {n} frames, {len(m['ms'])} times")
        a = load_blocks(os.path.join(folder, "effects", f"riven_fx_{name}.png"))
        if a.shape[:2] != (h, n * w):
            sys.exit(f"{name}: {a.shape[1]}x{a.shape[0]} game px, not {n} cells of {w}x{h}")
        cols = {tuple(int(v) for v in c) for c in a[a[..., 3] > 0][:, :3]}
        extra = cols - PALETTE if name == "knockup" else cols - (PALETTE - ROCKS)
        if extra:
            sys.exit(f"{name}: colours outside the effects' palette: {sorted(extra)}")
        b = unrim(a)
        Image.fromarray(b).save(G.lp(os.path.join(SRC, f"riven_fx2_{name}.png")))
        table[name] = {"cell": [w, h], "anchor": m["anchor"], "ms": m["ms"]}
        rim = int((np.all(a[..., :3] == np.array(RIM, np.uint8), -1) & (a[..., 3] > 0)).sum())
        print(f"riven_fx2_{name}.png: {n} frames of {w}x{h}, anchor {tuple(m['anchor'])}, {sum(m['ms'])} ms, "
              f"dark green {rim} px")
    with open(G.lp(os.path.join(SRC, "riven_fx2_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(table, indent=1) + "\n")


def fx2_frames(name, spec):
    """The second delivery's frames of one effect, each cut round the unit's standing point."""
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"riven_fx2_{name}.png"))).convert("RGBA"))
    (w, h), (ax, ay), (ux, uy) = spec["cell"], spec["anchor"], FX2[name][1]
    return [(G.centre_frame(a[:, k * w:(k + 1) * w], -(ax + ux), -(ay + uy)), ms) for k, ms in enumerate(spec["ms"])]


def strip_cells(name, layer, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"riven_fx_{name}_{layer}.png"))).convert("RGBA"))
    cols = layout(n)
    return [a[(k // cols) * CELL:(k // cols + 1) * CELL, (k % cols) * CELL:(k % cols + 1) * CELL] for k in range(n)]


def symmetric(fr):
    """Rows under the middle made the mirror of the rows over it."""
    fr = fr.copy()
    h = fr.shape[0] // 2
    fr[h + 1:] = fr[:h][::-1]
    return fr


def build():
    with open(G.lp(os.path.join(NATIVE, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    sheets = {s: {} for s in SHEETS}
    for sheet, names in SHEETS.items():
        for name in names:
            rows = cells["tags"][SETS[name]]
            for layer in ("back", "front"):
                cs = strip_cells(name, layer, len(rows))
                sheets[sheet][f"{name}_{layer}"] = [(G.centre_frame(c, -r["pivot"][0], -r["pivot"][1]), r["ms"])
                                                    for c, r in zip(cs, rows)]
    rows = cells["tags"]["r_slash"]
    back = strip_cells("r_slash", "back", len(rows))
    front = strip_cells("r_slash", "front", len(rows))
    fx = sheets["league_riven_fx"]
    fx["r_slash_back"] = [(G.centre_frame(c, -r["pivot"][0], -r["pivot"][1]), r["ms"]) for c, r in zip(back, rows)]
    fx["r_wave"] = [(symmetric(G.centre_frame(front[k], -rows[k]["pivot"][0], -(rows[k]["pivot"][1] - WAVE_LIFT))),
                     rows[k]["ms"]) for k in (2, 3)]
    with open(G.lp(os.path.join(SRC, "riven_fx2_cells.json")), encoding="utf-8") as f:
        table = json.load(f)
    for name, (sheet, _) in FX2.items():
        frames = fx2_frames(name, table[name])
        for tag, (k0, k1) in PHASES.get(name, {name: (0, len(frames))}).items():
            sheets[sheet][tag] = frames[k0:k1]
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder (riven_vfx_pack): its layers -> native strips first")
    ap.add_argument("--fx2", help="Codex's second delivery (riven_fx2_complete): its effects -> native strips first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    if args.fx2:
        from_fx2(args.fx2)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
