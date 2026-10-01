#!/usr/bin/env python3
"""Import Shaco's effects (assets/source/shaco/PROMPTS_FX.md, 1-16) and build his Hallucinate clone, as game sheets.

    python tools/art/import_shaco.py --raw <Codex's delivery folder>   # once: delivered PNGs -> native strips
    python tools/art/import_shaco.py                                   # native strips -> effect sheets + the clone

The body comes from tools/art/import_native.py. --raw turns every delivered strip into a native strip
(assets/source/shaco/shaco_fx_<name>.png, 8x blocks) the way tools/art/import_fiora.py does: the frames from
manifest.json's `assets[].frames[].rect` (or equal cells across the image), each game pixel the majority colour of
the source pixels it covers, opaque when a third of them are solid, every colour snapped to the ramps that strip
asked for; then the ring comes off the glows (import_riven.unrim's rule: an edge pixel of a ramp's darkest shade goes
when two lighter neighbours hold the shape, else it takes the next shade). The box and the jester popping out of it
are objects drawn like the character: their near-black outline stays. A delivered strip already made of flat 8x8
blocks is read one pixel a block instead. Writes shaco_fx_anchors.json beside the strips.
One scale per strip, set by the kit (1000 distance units a pixel): the hits 10-26 px wide, the shiv 12 long, the fear
16 wide, the puffs 24-32, the box 10 in the air and 24 on the ground, the blast 60 (radius 30000), the three mini boxes
64 (their shots reach 32000).
The second step places every cell by its anchor on the unit and times it by the kit (60 ticks a second): a hit on the
chest, the fear over the crown, the puffs and the boxes on the soles' row; W's box pops w_arm ticks after its landing
picture and stays for its 300 ticks of shots (the loop 4-7 repeated), the mini boxes for their 150. Writes
league/effects/league_shaco_fx and league_shaco_big.
The clone (league/effects/league_shaco_clone) is Shaco himself, cut from league/champions/league_shaco: his idle
frame (clone_idle, replayed every 4 ticks by the kit while nothing strikes), his attack (clone_attack, 24 ticks: the
kit's r_pic) and his idle coming out of Deceive's reappearing puff (clone_in). It stands on the champion's ground line
24 px to its left, facing it, drawn under it - first it stood 9 px behind (above) him like league_annie's Tibbers and
read as hanging on him (the user: "大招的分身也有点奇怪 看起来像是挂在别人身上的"); if the game mirrors a view on a unit
with the unit's facing, the clone keeps to his back - and its outline is the demon violet instead of near-black, a hint
that it is not Shaco.
"""
import argparse
import json
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import tfm2_ase as T  # noqa: E402
from import_morgana import load_manifest, rect  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shaco")
MOD = os.path.join(ROOT, "league")
Z = 8
HIT = (0, -8)                          # a hit on the upper body of a 35-40 px hero
OVERHEAD = (0, -31)                    # over a 35-40 px hero's crown (the fear)
GROUND = (0, 10)                       # the middle of a ring round a unit's feet (the soles 11 px under its pivot)
SOLES = (0, 11)                        # the soles' row: what stands on the ground stands here
CLONE = (-24, 0)                       # the clone's pivot: beside the champion it rides, on its ground line
CLONE_LINE = (0x5E, 0x24, 0x91)        # the clone's outline: the demon violet
OUTLINE = (0x0F, 0x04, 0x19)
# the pack's colours (PROMPTS_FX.md)
DEMON = ["FFFFFF", "F2D9FF", "C98CF0", "9447D1", "5E2491", "2E0F4D"]
POISON = ["F4FFD6", "C8F27A", "86D23F", "4C9A2A", "1F5419"]
STEEL = ["FFFFFF", "E6E8F0", "B8C4D8", "7F8CA8", "4A5470"]
CRIMSON = ["FFF2F2", "FF9A9A", "FC2D3F", "B3112D", "6A0A1E"]
SMOKE = ["E8E0F0", "A89BB8", "6E6280", "3E3450", "1E1828"]
DUST = ["C8BCA8", "9A8C78", "6E6252"]
BOX = ["0F0419", "1D264A", "334782", "475C75", "6A0A1E", "B3112D", "FC2D3F", "8A5D25", "F3BF27", "FFF2A3", "D1CBDE",
       "F7F7F8", "03A7E9", "B8FAFF"]
RAMPS = {"demon": DEMON, "poison": POISON, "steel": STEEL, "crimson": CRIMSON, "smoke": SMOKE, "dust": DUST, "box": BOX}
RIM = {"2E0F4D": "5E2491", "1F5419": "4C9A2A", "4A5470": "7F8CA8", "6A0A1E": "B3112D", "1E1828": "3E3450"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames; ramps; scale by `size` game px over `measure` ("w" the widest drawing, "h" the tallest);
# anchors per axis: "cell" the cell's middle, ("at", share) of the cell, "lowest" the lowest drawn row over all frames;
# `mirror` the top half onto the bottom; `object` keeps the near-black outline (no unrim)
RAW = {
    "hit": dict(n=5, ramps="steel", size=14, measure="w"),
    "q_hit": dict(n=6, ramps="crimson demon", size=26, measure="w"),
    "bs_hit": dict(n=5, ramps="crimson demon", size=18, measure="w"),
    "e_shiv": dict(n=4, ramps="steel poison", size=12, measure="w", mirror=True),
    "e_hit": dict(n=5, ramps="poison", size=16, measure="w"),
    "fear": dict(n=8, ramps="demon", size=16, measure="w"),
    "shot_hit": dict(n=4, ramps="demon", size=10, measure="w"),
    "q_vanish": dict(n=6, ramps="smoke demon", size=30, measure="w", y="lowest"),
    "q_appear": dict(n=5, ramps="smoke demon", size=24, measure="w", y="lowest"),
    "r_poof": dict(n=6, ramps="smoke demon crimson", size=32, measure="w", y="lowest"),
    "r_burn": dict(n=5, ramps="demon", size=18, measure="w"),
    "w_throw": dict(n=4, ramps="box", size=10, measure="w", object=True),
    "w_land": dict(n=5, ramps="box dust", size=24, measure="w", y="lowest", object=True),
    "w_box": dict(n=10, ramps="box demon smoke", size=24, measure="w", y="lowest", object=True,
                  align=(range(8), [8, 9])),
    "r_boom": dict(n=7, ramps="demon crimson smoke", size=60, measure="w", y=("at", 0.667)),
    "r_mini": dict(n=10, ramps="box demon smoke", size=64, measure="w", object=True, align=(range(8), [8, 9])),
}


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    return out


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere), in chunks."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def unrim(a):
    """The ring off the glows: an edge pixel in a ramp's darkest shade goes when 2+ lighter 8-neighbours hold the
    shape, else it takes the ramp's next shade. Returns the picture and how many edge pixels were in the ring shade."""
    a = a.copy()
    op = a[..., 3] > 0
    hexa = np.array([["%02X%02X%02X" % tuple(p[:3]) for p in row] for row in a])
    rim = op & np.isin(hexa, list(RIM))
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    gone = target & (lit >= 2)
    a[gone] = 0
    for dark, nxt in RIM.items():
        m = target & ~gone & (hexa == dark)
        a[m, :3] = rgb(nxt)
    return a, int(target.sum())


def mirror(cell, U):
    """The top half (rows 0..U) mirrored onto the bottom: exact symmetry about the anchor row."""
    out = cell.copy()
    for r in range(U):
        out[2 * U - r] = cell[r]
    return out


def anchors_of(spec, rects, box):
    """Source (x, y) of every frame's anchor."""
    out = []
    for axis, how in ((0, spec.get("x", "cell")), (1, spec.get("y", "cell"))):
        vals = []
        for k, (x, y, w, h) in enumerate(rects):
            o, size = (x, w) if axis == 0 else (y, h)
            if how == "cell":
                vals.append(o + size / 2)
            elif how == "lowest":
                vals.append(y + max(b[3] - r[1] for b, r in zip(box, rects)) - 0.5)
            elif how[0] == "at":
                vals.append(o + size * how[1])
            else:
                raise ValueError(how)
        out.append(vals)
    return list(zip(out[0], out[1]))


def align_boxes(out, tw, frames, after):
    """The box drawn a little higher or wider in some frames (W's box 4 rows up in 6-8, the mini boxes 1-2): each of
    `frames` moved so its box's lowest row and its left gold edge in the bottom rows match the first frame's; the
    smoke frames `after` the box goes move with the last box frame. Returns the moves."""
    gold = np.array(rgb("F3BF27"))
    box = [np.array(rgb(h)) for h in ("1D264A", "334782", "F3BF27", "8A5D25")]
    def spot(c):
        m = (c[..., 3] > 0) & np.any([(c[..., :3] == b).all(-1) for b in box], 0)
        ys = np.nonzero(m.any(1))[0]
        low = int(ys.max())
        g = (c[..., 3] > 0) & (c[..., :3] == gold).all(-1)
        g[:max(0, low - 3)] = False
        return low, int(np.nonzero(g.any(0))[0].min())
    cells = [out[:, k * tw:(k + 1) * tw].copy() for k in range(out.shape[1] // tw)]
    ref = spot(cells[frames[0]])
    moves = {}
    for k in list(frames) + list(after):
        if k in frames:
            low, left = spot(cells[k])
            dy, dx = ref[0] - low, ref[1] - left
        else:
            dy, dx = moves[frames[-1]]
        moves[k] = (dy, dx)
        c = cells[k]
        moved = np.zeros_like(c)
        H, W = c.shape[:2]
        moved[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = c[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
        out[:, k * tw:(k + 1) * tw] = moved
    return moves


def flat_blocks(a):
    """The image one pixel a block when it is made of flat 8x8 blocks with alpha 0/255, else None."""
    H, W = a.shape[:2]
    if H % Z or W % Z or not set(np.unique(a[..., 3])) <= {0, 255}:
        return None
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    return b[:, 0, :, 0].copy() if (b == b[:, :1, :, :1]).all() else None


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "shaco_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"shaco_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        native = flat_blocks(a)
        if native is not None:                     # already at game size: one pixel a block, the cells equal
            n = spec["n"]
            if native.shape[1] % n:
                sys.exit(f"{fn}: {native.shape[1]} px is not {n} equal cells")
            tw, th = native.shape[1] // n, native.shape[0]
            out = native
            L, U = tw // 2, th // 2
            if spec.get("y") == "lowest":
                U = int(np.nonzero(native[..., 3].any(1))[0].max())
            Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
            anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": n}
            print(f"{fn}  native: {n} cells of {tw}x{th}, anchor {L},{U}")
            continue
        solid = a[..., 3] >= 100
        if fn in manifest:
            rects = [rect(f) for f in manifest[fn]["frames"]]
        else:                                      # equal cells across the image
            cw = a.shape[1] // spec["n"]
            rects = [[k * cw, 0, cw, a.shape[0]] for k in range(spec["n"])]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        box = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            box.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1) if len(xs) else
                       (x + w // 2, x + w // 2 + 1, y + h // 2, y + h // 2 + 1))
        ext = {"h": lambda: max(b[3] - b[2] for b in box), "w": lambda: max(b[1] - b[0] for b in box)}[spec["measure"]]()
        sx = sy = spec["size"] / ext
        hexes = [h for r in spec["ramps"].split() for h in RAMPS[r]]
        idx = snap(a, solid, np.array([rgb(h) for h in hexes], float))
        pal = np.array([rgb(h) for h in hexes], np.uint8)
        anc = anchors_of(spec, rects, box)
        L = math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, box)) * sx) + 1
        U = math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, box)) * sy) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * spec["n"], 4), np.uint8)
        rims = 0
        for k, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[k]
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / sy))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / sy)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / sx))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / sx)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    out[r, k * tw + c, :3] = pal[col]
                    out[r, k * tw + c, 3] = 255
            cell = out[:, k * tw:(k + 1) * tw]
            if not spec.get("object"):
                cell, n = unrim(cell)
                rims += n
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, k * tw:(k + 1) * tw] = cell
        if spec.get("align"):
            moves = align_boxes(out, tw, *spec["align"])
            print(f"  {fn}: box frames moved (dy, dx) " + " ".join(f"{k + 1}:{v}" for k, v in moves.items() if v != (0, 0)))
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": spec["n"]}
        print(f"{fn}  {spec['n']} cells of {tw}x{th}, anchor {L},{U}, scale {sx:.4f}, {rims} ring pixels, "
              f"{len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"shaco_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"shaco_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def stay(total_ms, pop=(80, 80, 80), loop=(100, 100, 100, 100), out=(80, 80, 80)):
    """Frames and durations of a box that pops (1-3), loops (4-7) and goes (8-10) over about total_ms."""
    n = max(1, round((total_ms - sum(pop) - sum(out)) / sum(loop)))
    used = [0, 1, 2] + [3, 4, 5, 6] * n + [7, 8, 9]
    return used, list(pop) + list(loop) * n + list(out)


W_BOX = stay(5000)                    # the shots: w_shots_t 300 ticks from the pop
R_MINI = stay(2500)                   # the mini boxes' shots: r_mshot_t 150 ticks

# sprite: {tag: [(strip, its frames used, spot of the anchor from the pivot, ms per frame), ...]}
FX = {
    "league_shaco_fx": {
        "hit": [("hit", range(5), HIT, [50] * 5)],
        "q_hit": [("q_hit", range(6), HIT, [55] * 6)],
        "bs_hit": [("bs_hit", range(5), HIT, [50] * 5)],
        "e_shiv": [("e_shiv", range(4), (0, 0), [60] * 4)],
        "e_hit": [("e_hit", range(5), HIT, [60] * 5)],
        "fear": [("fear", range(8), OVERHEAD, [125] * 8)],
        "shot_hit": [("shot_hit", range(4), HIT, [50] * 4)],
        "q_vanish": [("q_vanish", range(6), SOLES, [70] * 6)],
        "q_appear": [("q_appear", range(5), SOLES, [60] * 5)],
        "r_poof": [("r_poof", range(6), SOLES, [70] * 6)],
        "r_burn": [("r_burn", range(5), HIT, [60] * 5)],
        "w_throw": [("w_throw", range(4), (0, 0), [50] * 4)],
    },
    "league_shaco_big": {
        "w_land": [("w_land", range(5), SOLES, [30, 30, 30, 40, 40])],      # the landing over w_arm's 10 ticks
        "w_box": [("w_box", W_BOX[0], SOLES, W_BOX[1])],
        "r_boom": [("r_boom", range(7), GROUND, [70] * 7)],
        "r_mini": [("r_mini", R_MINI[0], GROUND, R_MINI[1])],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "shaco_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, parts in tags.items():
            out[tag] = []
            for src, used, spot, ms in parts:
                ax, ay = anchors[src]["anchor"]
                strip = cells(src, anchors[src]["frames"])
                for k, m in zip(used, ms):
                    out[tag].append((G.centre_frame(strip[k], spot[0] - ax, spot[1] - ay), m))
        sheets[sprite] = out
    return sheets


def clone_sheet():
    """The clone from his own frames: the outline violet, 9 px behind the champion it rides."""
    sp = T.load_sprite(os.path.join(MOD, "champions", "league_shaco"))

    def frames(tag):
        out = []
        for i in sp.tag_frames(tag):
            a = np.asarray(sp.frames[i].convert("RGBA")).copy()
            line = (a[..., 3] > 0) & (a[..., :3] == np.array(OUTLINE, np.uint8)).all(-1)
            a[line, :3] = CLONE_LINE
            cy, cx = a.shape[0] // 2, a.shape[1] // 2      # the champion's frames are centred on the pivot
            out.append((G.centre_frame(a, CLONE[0] - cx, CLONE[1] - cy), sp.durations[i]))
        return out

    idle = frames("idle")[0][0]
    attack = frames("attack")
    puff = None
    anchors = json.load(open(G.lp(os.path.join(SRC, "shaco_fx_anchors.json")), encoding="utf-8"))
    if "q_appear" in anchors:
        ax, ay = anchors["q_appear"]["anchor"]
        puff = [G.centre_frame(c, CLONE[0] + SOLES[0] - ax, CLONE[1] + SOLES[1] - ay) for c in cells("q_appear", 5)]
    clone_in = []
    for k in range(5):                                   # the puff, the clone standing in it from its third frame
        layers = ([puff[k]] if puff else []) + ([idle] if k >= 2 else [])
        clone_in.append((overlay(layers) if layers else idle, 60))
    return {"clone_in": clone_in,
            "clone_idle": [(idle, 100)],                 # the kit replays it every 4 ticks
            "clone_attack": [(a, ms) for a, ms in attack]}


def overlay(layers):
    """Centred frames laid over each other (later ones on top), centred on the shared pivot."""
    H = max(a.shape[0] for a in layers) | 1
    W = max(a.shape[1] for a in layers) | 1
    out = np.zeros((H, W, 4), np.uint8)
    for a in layers:
        y0, x0 = (H - a.shape[0]) // 2, (W - a.shape[1]) // 2
        m = a[..., 3] > 0
        out[y0:y0 + a.shape[0], x0:x0 + a.shape[1]][m] = a[m]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    ap.add_argument("--only", action="append", help="with --raw: only this strip (repeatable)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    sheets = build()
    sheets["league_shaco_clone"] = clone_sheet()
    for sprite, tags in sheets.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
