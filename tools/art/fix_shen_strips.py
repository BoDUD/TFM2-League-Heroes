#!/usr/bin/env python3
"""Shen's action strips from Codex's step-2 raws (assets/source/shen/codex_strips/raw) + the approved design.

    python tools/art/fix_shen_strips.py [--review DIR] [--only TAG]

Writes assets/source/native/shen_<tag>.png (every frame a 128 x 128 canvas cell at 8x, the soles on row 99, the
standing point on column 64) and shen_cells.json; then tools/art/import_native.py --hero shen.

Codex drew every frame as its own generator image after League's pose (pack: assets/source/shen/MODEL_STRIPS.md) and
then made "final" copies itself by resizing and re-quantising them: those are blurred and lost the glowing eyes
(codex_strips/1x, kept for reference only). The raws are crisp, but each frame came out at its own square size
(about 6.5-10.7 px on the 1254-px image; the canvas square is 1254 / 128 = 9.8), i.e. some frames are drawn with up to
40 % more squares than the design. Here, per frame:
  1. read the raw on its own grid (the skill's regrid.py) at its square size - measured from the outline, which is one
     square thick (SQUARE overrides), and map every square to the design's 30 colours (CIELAB);
  2. bring it to the design's scale by deleting whole rows and columns evenly (design_rengar.even_drop: never two
     neighbours, the cheapest lines; the eyes' rows and columns and the soles kept), the factor being its square size
     over the canvas square (FIX corrects frames Codex drew bigger or smaller on the canvas);
  3. stand it where League's frame stands: its lowest row on League's lowest row (the soles' row for a grounded frame),
     its eyes on League's head column (else its middle on League's);
  4. clear specks (pieces of fewer than SPECK squares apart from the body) and close the outline.
The idle is the design square for square, breathing (the body above the sash sinks over the legs); the run is Codex's
skin swap of oppi's Lee Sin run (RUN_SHEET). Q and R start from the design itself (League's casts start from the idle
pose).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402
import design_rengar as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shen", "codex_strips", "raw")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "shen_native.png")
SPEC = os.path.join(ROOT, "assets", "source", "shen", "poses.json")
POSE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "sn_work", "pose")   # native_pose renders (League)
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
SOLES, MID = 99, 64
PIVOT = (MID, SOLES - 11)
CANVAS_SQUARE = 1254 / 128
# The run: Codex's skin swap of oppi's Lee Sin run (a wide-stanced, baggy-trousered humanoid: the legs cross, the fists
# pump, the body bobs) - assets/source/shen/codex_run_swap. Its 1x sheet is 3 x 3 cells of 60 x 60 on the design's 30
# colours, the soles on the cell's row RUN_SOLES, the cell's middle column where the pack put the design's feet middle.
# (The first run moved the design's own legs whole under the body: the wide stance could not cross - the hakama
# bulbs hid behind the apron or rose into the sash; the user: 「腿变形严重了 交叉步也不对」.)
RUN_SHEET = os.path.join(ROOT, "assets", "source", "shen", "codex_run_swap", "shen_run_3x3_1x.png")
RUN_CELL, RUN_SOLES = 60, 55
# The user kept Codex's legs and asked for the design's upper body (「腿部ok的 上半身用之前的」): the design's rows above
# RUN_CUT (head, arms, sword, sash; its near hand down to row RUN_CUT + 1) square for square over Codex's legs and
# hems below RUN_CUT, RUN_BOB rows lower per frame (down only).
RUN_CUT = 85
RUN_HAND_COL = 78
RUN_BOB = [1, 1, 0, 0, 0, 0, 0, 1, 1]   # lowest in the wide strides (1-2, 8-9), up through the pass
EYE = (239, 226, 246)
SPECK = 4

# tag -> [(source, ms)]; a source is a Codex frame name (placed by ITS League frame) or ("sink", name, row, n): that
# frame with everything above `row` moved n rows down over the rest (a breath, nothing redrawn)
TAGS = {
    # the idle breathes without a cut: the body above the sash (and the whole near hand) sinks over the legs, which stay
    # square for square (import_native's idle_breathe cut two rows out of the trousers, boots, apron and tail hem)
    "idle": [(("breath", n), 140) for n in (0, 0, 1, 2, 2, 2, 1, 0)],
    "run": [(("swap", k), 100) for k in range(1, 10)],
    "attack": [(f"attack_{k}", ms) for k, ms in zip(range(1, 7), (50, 60, 60, 90, 80, 60))],
    # Q: Codex's four frames were four bodies (frame 4 tall and thin); the palm push is one drawing held
    # (League's Q starts from the idle pose: the design itself, so the cast starts without a jump)
    "skill": [("design", 60), ("skill_3", 240)],
    "skill2": [(f"skill2_{k}", ms) for k, ms in zip(range(1, 5), (50, 50, 100, 100))],
    # R: Codex's four channel frames were four different drawings (they flickered as a loop): the wind-up ends on
    # ult_2 (sword down, hands together before the chest) and the channel is that drawing breathing
    # (ult_3, the fists pushed forward, has a bare chest where the design wears its chest plate: left out). League's
    # R starts from the idle pose, and Codex's ult_1 was the idle redrawn (85 % on the design's squares, 15 % the same
    # colour, a two-row eye slit): the design itself, as for Q
    "ult": [("design", 150), ("ult_2", 150)],
    "ult_loop": [("ult_2", 300), (("sink", "ult_2", 84, 1), 300)],
    "hit": [("hit_1", 100)],
    "dead": [(f"dead_{k}", ms) for k, ms in zip(range(1, 9), (100, 100, 120, 150, 150, 200, 250, 400))],
}
# frames moved whole after placement (columns, rows)
NUDGE = {}
# eyes painted where Codex's glow did not survive the read (canvas row, column after placement): on the frame's skin
# eye slit, where Codex's raw has them (two in a front view, one in a side view)
EYES = {"skill_3": [(64, 67), (64, 68)], "attack_2": [(57, 58), (57, 60)], "skill2_3": [(77, 72)],
        "skill2_4": [(72, 74)], "dead_4": [(66, 64)], "dead_6": [(76, 73)], "dead_7": [(79, 69)]}
AIR = {"attack_3", "skill2_2", "skill2_3", "skill2_4"}   # off the ground: the lowest row stays where League's is
SQUARE = {}          # name -> square size in raw px, when the outline measure is off
# name -> extra scale factor: Codex drew these figures bigger on the canvas than the design (judged against the design's
# silhouette, soles aligned: work/sn/sizecheck_sn.py; the head template and mask measures were too noisy to trust)
FIX = {"skill_2": 0.92, "skill_3": 0.85, "skill_4": 0.9, "attack_1": 0.95, "attack_5": 0.88, "ult_1": 0.8, "skill2_1": 0.9, "ult_2": 0.95,
       "ult_3": 0.9, "ult_loop_2": 0.85, "ult_loop_3": 0.85, "ult_loop_4": 0.9, "hit_1": 0.8, "dead_1": 0.95,
       "dead_2": 0.95}


def lp(path):
    return R.lp(path)


def design():
    return np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[::Z, ::Z].copy()


def palette(des):
    return np.array(sorted({tuple(int(v) for v in c[:3]) for c in des[des[..., 3] > 0]}), np.uint8)


SKIN = ((238, 169, 109), (182, 115, 70))


def glow(a):
    """Codex's glowing eyes, which the nearest-colour map would turn into the silver of the trims: light violet or
    white squares with skin right beside them (the eye slit), in the figure's upper part; at most the 4 of the row
    that has the most (the blade's lavender edge and the mask's rim are not eyes)."""
    c = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    violet = op & (c[..., 2] - c[..., 1] > 25) & (c[..., 0] - c[..., 1] > 10) & (c.sum(-1) > 450)
    white = op & (c.min(-1) > 215)
    skinish = op & (c[..., 0] > 150) & (c[..., 0] - c[..., 2] > 50) & (c[..., 1] > 80)
    beside = np.zeros_like(op)
    for dx in (-2, -1, 1, 2):
        beside |= np.roll(skinish, dx, axis=1)
    cand = (violet | white) & beside
    ys = np.nonzero(op)[0]
    if not len(ys):
        return cand
    cand[int(ys.min() + 0.45 * (ys.max() - ys.min())):] = False
    if cand.sum() == 0:
        return cand
    row = int(np.argmax(cand.sum(1)))
    keep = np.zeros_like(cand)
    xs = np.nonzero(cand[row])[0]
    if len(xs) > 4:                      # the two most violet of them
        v = (c[row, xs, 2] - c[row, xs, 1]) + (c[row, xs, 0] - c[row, xs, 1])
        xs = xs[np.argsort(-v)[:2]]
    keep[row, xs] = True
    return keep


def pal_map(a, pal):
    """Every square to the nearest design colour (CIELAB) - never to the eye colour, which only glow() sets."""
    pal = np.array([c for c in pal if tuple(int(v) for v in c) != EYE], np.uint8)
    pl = R.lab(pal.astype(float))
    lab = R.lab(a[..., :3].astype(float))
    idx = ((lab[..., None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
    out = np.zeros_like(a)
    out[..., :3] = pal[idx]
    out[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    out[glow(a)] = EYE + (255,)
    return out


def outline_square(a):
    """The silhouette's outer ring is one square of near-black: the median length of the dark runs that start at the
    transparent edge, along every row and column (the mean of the runs near that median)."""
    op = a[..., 3] >= 128
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    dark = op & (lum < 40)
    runs = []
    for o, dk in ((op, dark), (op.T, dark.T)):
        for r_op, r_dk in zip(o, dk):
            if r_op.sum() < 5:
                continue
            d = np.diff(r_op.astype(int))
            for e in np.nonzero(d == 1)[0] + 1:
                n = 0
                while e + n < len(r_dk) and r_dk[e + n]:
                    n += 1
                if 3 <= n <= 20:
                    runs.append(n)
            for e in np.nonzero(d == -1)[0]:
                n = 0
                while e - n >= 0 and r_dk[e - n]:
                    n += 1
                if 3 <= n <= 20:
                    runs.append(n)
    runs = np.array(runs, float)
    m = np.median(runs)
    return float(runs[(runs > m * 0.6) & (runs < m * 1.5)].mean())


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name + ".png"))).convert("RGBA"))


def read(name, pal):
    """The raw on its own grid, in the design's colours, cropped; and its square size."""
    a = raw(name)
    s = SQUARE.get(name) or outline_square(a.astype(float))
    rb, _, _ = regrid(a, s)
    return pal_map(R.crop(rb), pal), s


def weights(a):
    w = np.ones(a.shape[:2])
    eye = (a[..., :3] == EYE).all(-1) & (a[..., 3] > 0)
    w[eye] = 12
    lum = a[..., :3].astype(int).sum(-1)
    w[(lum > 560) & (a[..., 3] > 0)] = 3        # silver trims, the blade
    return w


def scale_to(a, f):
    """Whole rows and columns deleted evenly so the figure is f of its size (never two neighbouring lines, the eyes'
    rows and columns and the two lowest rows kept)."""
    if f >= 0.999:
        return a
    H, W = a.shape[:2]
    eye = (a[..., :3] == EYE).all(-1) & (a[..., 3] > 0)
    ey, ex = np.nonzero(eye)
    idx = a[..., 0].astype(np.int64) * 65536 + a[..., 1].astype(np.int64) * 256 + a[..., 2] + (a[..., 3] > 0) * 2 ** 25
    w = weights(a)
    R.JITTER = 1
    qr, qc = H - round(H * f), W - round(W * f)
    hr = set(ey.tolist()) | {H - 2, H - 1}
    dr = R.even_drop([idx[y] for y in range(H)], [w[y] for y in range(H)], 1, H - 3, qr, hr) if qr else []
    kr = [y for y in range(H) if y not in dr]
    a, idx, w = a[kr], idx[kr], w[kr]
    hc = set(ex.tolist())
    dc = R.even_drop([idx[:, x] for x in range(W)], [w[:, x] for x in range(W)], 1, W - 2, qc, hc) if qc else []
    kc = [x for x in range(W) if x not in dc]
    return a[:, kc]


def league(tag, cells):
    """League's frames of a tag at game size on our canvas (as the pack showed them) and their head columns."""
    cw, ch = cells["cell"]
    frs = cells["tags"][tag]
    nat = np.asarray(Image.open(os.path.join(POSE, f"shen_native_{tag}.png")).convert("RGBA"))
    cols = nat.shape[1] // (cw * Z)
    out = []
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * cw * Z, (i // cols) * ch * Z
        g = nat[Y:Y + ch * Z, X:X + cw * Z][::Z, ::Z].copy()
        g[np.abs(g[..., :3].astype(int) - 225).sum(-1) < 12] = 0
        dx, dy = PIVOT[0] - fr["pivot"][0], PIVOT[1] - fr["pivot"][1]
        g = shift(g, dx, dy)
        out.append((g, fr["head"][0] + dx))
    return out


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys, ye = max(0, dy), min(H, H + dy)
    xs, xe = max(0, dx), min(W, W + dx)
    if ys < ye and xs < xe:
        out[ys:ye, xs:xe] = a[ys - dy:ye - dy, xs - dx:xe - dx]
    return out


def feet_mid(a, bottom):
    """Middle column of what stands on the lowest 3 rows."""
    xs = np.nonzero((a[max(bottom - 2, 0):bottom + 1, :, 3] > 0).any(0))[0]
    return (xs.min() + xs.max()) / 2


def place(fig, lol, ref, air=False):
    """fig (cropped) on the 128 canvas. Grounded: its lowest row on the soles' row; off the ground: on League's lowest
    row. Sideways: it moves from the design's stance as League's frame moves from League's idle (feet middles when
    grounded, middles of mass in the air) - so a pose that starts like the idle starts where the idle stands.
    ref = (League idle's feet middle, League idle's middle, the design's feet middle, the design's middle)."""
    l_feet, l_mid, d_feet, d_mid = ref
    ly = np.nonzero(lol[..., 3] > 0)
    if air:
        bottom = min(int(ly[0].max()), SOLES)
        tx = d_mid + float(ly[1].mean()) - l_mid
        fx = float(np.nonzero(fig[..., 3] > 0)[1].mean())
    else:
        bottom = SOLES
        tx = d_feet + feet_mid(lol, int(ly[0].max())) - l_feet
        fx = feet_mid(fig, fig.shape[0] - 1)
    x0 = int(round(tx - fx))
    y0 = bottom + 1 - fig.shape[0]
    can = np.zeros((128, 128, 4), np.uint8)
    H, W = fig.shape[:2]
    ys, xs = max(0, y0), max(0, x0)
    ye, xe = min(128, y0 + H), min(128, x0 + W)
    can[ys:ye, xs:xe] = fig[ys - y0:ye - y0, xs - x0:xe - x0]
    return can


def place_ref(des, cells):
    g = league("idle", cells)[0][0]
    ly = np.nonzero(g[..., 3] > 0)
    dy = np.nonzero(des[..., 3] > 0)
    return (feet_mid(g, int(ly[0].max())), float(ly[1].mean()), feet_mid(des, SOLES), float(dy[1].mean()))


def despeck(a):
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n <= 1:
        return a
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    near = ndimage.binary_dilation(lab == main, iterations=2)
    out = a.copy()
    for i, s in enumerate(sizes, 1):
        if i != main and s < SPECK and not (near & (lab == i)).any():
            out[lab == i] = 0
    return out


def close(a, pal):
    out, _, _ = strips.complete_outline(a, color=tuple(int(v) for v in pal[0]), feet=SOLES, keep=None)
    return out


def pinholes(a, most=2):
    """Enclosed transparent spots of at most `most` squares take their commonest opaque neighbour's colour."""
    op = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    out = a.copy()
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) > most:
            continue
        for y, x in zip(ys, xs):
            nb = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= yy < 128 and 0 <= xx < 128 and a[yy, xx, 3] > 0]
            if nb:
                out[y, x] = max(set(nb), key=nb.count)
    return out


def finish(a, pal):
    return close(pinholes(a), pal)


def action_frame(name, tag, k, pal, lol, ref):
    fig, s = read(name, pal)
    f = s / CANVAS_SQUARE * FIX.get(name, 1.0)
    fig = R.crop(scale_to(fig, f))
    g, _ = lol[k - 1]
    a = despeck(place(fig, g, ref, name in AIR))
    if name in NUDGE:
        a = shift(a, *NUDGE[name])
    a = finish(a, pal)
    for y, x in EYES.get(name, ()):
        assert a[y, x, 3] > 0, (name, y, x)
        a[y, x] = EYE + (255,)
    return a, s, f


def swap_frame(k, des):
    """Run frame k (1-9) of Codex's skin swap on our canvas: its soles on ours, its cell's middle on the design's feet."""
    sheet = np.asarray(Image.open(lp(RUN_SHEET)).convert("RGBA"))
    r, c = divmod(k - 1, 3)
    cell = sheet[r * RUN_CELL:(r + 1) * RUN_CELL, c * RUN_CELL:(c + 1) * RUN_CELL]
    can = np.zeros_like(des)
    dy, dx = SOLES - RUN_SOLES, int(round(feet_mid(des, SOLES))) - RUN_CELL // 2
    ys, xs = np.nonzero(cell[..., 3] > 0)
    can[ys + dy, xs + dx] = cell[ys, xs]
    bob = RUN_BOB[k - 1]
    up = des.copy()
    up[RUN_CUT:, :RUN_HAND_COL] = 0
    up[RUN_CUT + 2:] = 0
    up = shift(up, 0, bob)
    can[:RUN_CUT + bob] = 0
    m = up[..., 3] > 0
    can[m] = up[m]
    return can


def sink(a, row, n):
    """Everything above `row` n rows lower, over what is below (moved, not redrawn)."""
    up = a.copy()
    up[row:] = 0
    out = a.copy()
    out[:row] = 0
    up = shift(up, 0, n)
    m = up[..., 3] > 0
    out[m] = up[m]
    return out


BREATH_ROW, HAND_COL, HAND_END = 85, 76, 89   # the sash's underside; the near hand (cols >= 76, above row 89)


def breath(des, n):
    """The design with its body (rows < BREATH_ROW and the near hand) n rows lower over its legs."""
    if not n:
        return des.copy()
    up = des.copy()
    up[BREATH_ROW:, :HAND_COL] = 0
    up[HAND_END:] = 0
    out = des.copy()
    out[:BREATH_ROW] = 0
    out[BREATH_ROW:HAND_END, HAND_COL:] = 0
    up = shift(up, 0, n)
    m = up[..., 3] > 0
    out[m] = up[m]
    return out


def source_of(name):
    tag, k = name.rsplit("_", 1)
    return tag, int(k)


def build(only=None):
    des = design()
    pal = palette(des)
    cells = json.load(open(os.path.join(POSE, "shen_cells.json"), encoding="utf-8"))
    lols, cache, sheet, info = {}, {}, {}, {}
    ref = place_ref(des, cells)

    def frame(name):
        if name not in cache:
            tag, k = source_of(name)
            if tag not in lols:
                lols[tag] = league(tag, cells)
            a, s, f = action_frame(name, tag, k, pal, lols[tag], ref)
            cache[name] = a
            info[name] = (s, f)
        return cache[name]

    for tag, rows in TAGS.items():
        if only and tag not in only:
            continue
        frames = []
        for k, (src, ms) in enumerate(rows, 1):
            if src == "design":
                a = des.copy()
            elif isinstance(src, tuple) and src[0] == "breath":
                a = breath(des, src[1])
            elif isinstance(src, tuple) and src[0] == "swap":
                a = pinholes(swap_frame(src[1], des))
            elif isinstance(src, tuple) and src[0] == "sink":
                a = sink(frame(src[1]), src[2], src[3])
            else:
                a = frame(src)
            frames.append((a, ms))
        sheet[tag] = frames
    return sheet, info


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def write(sheet):
    cells = {"cell": [128, 128], "scale": Z, "tags": {}}
    path = lp(os.path.join(OUT, "shen_cells.json"))
    if os.path.exists(path):        # --only rebuilds some tags: keep the others' cells, in TAGS order
        with open(path, encoding="utf-8") as f:
            old = json.load(f)["tags"]
        cells["tags"] = {t: old[t] for t in TAGS if t in old and t not in sheet}
    for tag, frames in sheet.items():
        cols, rows = layout(len(frames))
        strip = np.zeros((rows * 128, cols * 128, 4), np.uint8)
        for k, (a, ms) in enumerate(frames):
            r, c = divmod(k, cols)
            strip[r * 128:(r + 1) * 128, c * 128:(c + 1) * 128] = a
        Image.fromarray(strip).resize((cols * 128 * Z, rows * 128 * Z), Image.NEAREST).save(
            lp(os.path.join(OUT, f"shen_{tag}.png")))
        cells["tags"][tag] = [{"pivot": list(PIVOT), "ms": ms} for _, ms in frames]
    cells["tags"] = {t: cells["tags"][t] for t in TAGS if t in cells["tags"]}
    with open(lp(os.path.join(OUT, "shen_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write("{" + json.dumps({"cell": cells["cell"], "scale": Z})[1:-1] + ', "tags": {\n')
        f.write(",\n".join(f'  "{t}": ' + json.dumps(v) for t, v in cells["tags"].items()))
        f.write("\n}}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write <tag>_<k>.png (128 x 128) here instead of the strips")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    sheet, info = build(a.only)
    for name, (s, f) in info.items():
        print(f"{name:12s} square {s:5.2f}  scale {f:.2f}")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for tag, frames in sheet.items():
            for k, (fr, _) in enumerate(frames):
                Image.fromarray(fr).save(os.path.join(a.review, f"{tag}_{k + 1}.png"))
        print("review frames in", a.review)
        return
    write(sheet)
    print("wrote", ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
