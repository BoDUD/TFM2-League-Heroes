"""league_riven's redrawn action frames, read back from Codex's raw sheets (hd/actions_raw/, the answer to
tools/art/pack_riven_actions.py): hd/actions/<tag>_<n>.png (n: League's frame, 1-based) + hd/actions/actions.json.

    python tools/art/actions_riven_hd.py [--review DIR]
    python tools/art/actions_riven_hd.py --run [--review DIR]      # the run's frames: hd/run_raw/ -> hd/run/

Codex's exported sheets were resampled onto the template grid with stray light squares on the rims, so the raw
sheets are read instead (as tools/art/swords_riven_hd.py did): white ground flooded from the edges (her cream hair is
inside the outline), each cell read on Codex's own square phase but on a pitch SCALE times its own, so she stands
STAND rows tall as in the design (Codex drew her ~61), every square the nearest colour of the design's own palette
(the design without its sword).

Per frame actions.json keeps (in the frame's squares): "pivot" - the template's standing point (the cell's middle on
the ground line), "fist" - her sword fist: the small skin-coloured piece (a hand) nearest the template's blue circle
(FIST_FIX overrides one where that picks the wrong hand), "size".
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402
import pack_riven_actions as PA  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "riven", "hd")
NATIVE = (7.0, 12.5)                   # Codex's own squares lie in here
SCALE = 61.2 / 56                      # its standing figure (attack_1 frame 1) is 61.2 of them; hers is 56
SKIN = [(252, 181, 101), (244, 182, 108), (225, 152, 86)]
HAND_MAX = 45                          # squares: a hand, not the face or a leg
# "<tag>_<n>": (x, y) squares - her sword fist, picked by eye on every frame (the nearest skin piece was a knee or
# the other hand too often): the closed fist that does what League's sword hand does in that frame (Codex drew the
# sword fist on either side)
FIST_FIX = {
    "attack_1": (5, 21), "attack_2": (30, 18), "attack_3": (38, 36), "attack_4": (35, 30), "attack_5": (29, 30),
    "attack_6": (37, 26),
    "attack2_1": (3, 18), "attack2_2": (25, 25), "attack2_3": (35, 19), "attack2_4": (2, 17), "attack2_5": (3, 15),
    "attack2_6": (2, 19),
    "attack3_1": (2, 20), "attack3_2": (2, 4), "attack3_3": (44, 40), "attack3_4": (35, 32), "attack3_5": (38, 33),
    "attack3_6": (31, 25),
    "skill_1": (3, 21), "skill_2": (33, 25), "skill_3": (35, 32), "skill_4": (32, 30), "skill_5": (44, 28),
    "skill_6": (50, 22), "skill_7": (3, 19),
    "q2_1": (3, 21), "q2_2": (2, 24), "q2_3": (1, 26), "q2_4": (41, 25), "q2_5": (36, 30), "q2_6": (37, 39),
    "q2_7": (2, 19),
    "q3_1": (2, 18), "q3_2": (11, 7), "q3_3": (2, 11), "q3_4": (33, 11), "q3_5": (37, 34), "q3_6": (26, 44),
    "q3_7": (2, 24),
    "skill2_1": (14, 11), "skill2_2": (4, 11), "skill2_3": (3, 18), "skill2_4": (8, 19), "skill2_5": (33, 3),
    "skill2_6": (32, 4), "skill2_7": (40, 4), "skill2_8": (4, 20),
}


def lp(path):
    return FD.lp(path)


def cutout(a):
    mn, mx = a.min(2), a.max(2)
    white = (mn > 228) & (mx - mn < 18)
    lab, _ = nd.label(white)
    rim = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    fig = ~np.isin(lab, [v for v in np.unique(rim) if v])
    fig = nd.binary_opening(fig, iterations=1)
    return fig


def read_cell(c, op):
    FD.PITCH = NATIVE
    (px, phx), (py, phy) = FD.fit(c, op, 1), FD.fit(c, op, 0)
    p = (px + py) / 2 * SCALE
    return read_on(c, op, p, phx, phy), (phx, phy, p)


def read_on(c, op, p, phx, phy):
    """The cell on squares of p raw px from (phx, phy): each square the median of its figure px, where they are most."""
    xs, ys = np.arange(phx, c.shape[1], p), np.arange(phy, c.shape[0], p)
    out = np.zeros((len(ys) - 1, len(xs) - 1, 4), np.uint8)
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            y0, y1 = int(round(ys[j])), int(round(ys[j + 1]))
            x0, x1 = int(round(xs[i])), int(round(xs[i + 1]))
            win = c[y0:y1, x0:x1].reshape(-1, 3)
            m = op[y0:y1, x0:x1].reshape(-1)
            if m.sum() * 2 > len(m):
                out[j, i, :3] = np.median(win[m], axis=0)
                out[j, i, 3] = 255
    return out


def to_palette(d, pal):
    op = d[..., 3] > 0
    lab = V.srgb2lab(d[op][:, :3].astype(float))
    pl = V.srgb2lab(pal.astype(float))
    k = np.argmin(((lab[:, None, :] - pl[None]) ** 2).sum(-1), axis=1)
    out = d.copy()
    out[op, :3] = pal[k]
    return out


HAIR = [(251, 235, 215), (236, 234, 234), (210, 188, 174), (213, 209, 204), (192, 164, 144), (176, 172, 170),
        (173, 147, 134)]
DESIGN_HAIR = 164                      # squares of hair (its biggest piece) in hd/design.png


def hair_area(d):
    m = np.zeros(d.shape[:2], bool)
    for c in HAIR:
        m |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(m)
    return int(nd.sum(m, lab, range(1, n + 1)).max()) if n else 0


def find_fist(d, want):
    skin = np.zeros(d.shape[:2], bool)
    for c in SKIN:
        skin |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    hair = np.zeros(d.shape[:2], bool)
    for c in HAIR:
        hair |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(skin, structure=np.ones((3, 3)))
    best = None
    for k in range(1, n + 1):
        piece = lab == k
        ys, xs = np.nonzero(piece)
        if len(ys) > HAND_MAX or len(ys) < 3:
            continue
        if (nd.binary_dilation(piece, iterations=2) & hair).sum() >= 6:      # her face, framed by her hair
            continue
        dist = float(np.min(np.hypot(xs + 0.5 - want[0], ys + 0.5 - want[1])))
        if best is None or dist < best[0]:
            best = (dist, (float(xs.mean() + 0.5), float(ys.mean() + 0.5)))
    return best


# ------------------------------------------------------------------------------------------------- the run (--run)
# The user, 2026-11-17: 「锐雯这个跑步姿势不太对吧 不然让codex补一补动作？」→「只做跑步」: the run posed by
# rig_riven_hd swung the sword from low in front to over her shoulder every cycle (League's riven_run holds it level in
# front, pointing forward), took short shuffling steps and stood upright. Codex redrew the run's eight frames whole on
# the pack's templates (League's riven_run, 8 x 121 ms; assets/source/riven/RUN_PROMPT_PPU.md), white ground, no
# sword: hd/run_raw/ (run_1: frames 1-3, run_2: 4-6, run_3: 7-8). --run reads them into hd/run/run_<n>.png + run.json:
# - one square for all eight: Codex drew every head the same size (its hair 171-180 raw px across in every frame), so
#   every frame is read on RUN_PITCH raw px a design square (the phase fitted per frame at that pitch): her body,
#   neck to soles, as tall as the design's, arms and legs 3 squares thick as the design's;
# - the head: the design's own (the idle's: hair, face, outline - PA.no_sword_canvas), laid where Codex's head is
#   (Codex's hair box + HEAD_AT), Codex's head (down to RUN_CHIN) cleared first: Codex drew it 15 % smaller than the
#   design's, the hair one flat cream, and the face (a narrow side eye) a little differently in every frame;
# - the standing point: the template cell's middle, measured from the head (Codex drew every head within half a square
#   of the same place from it, so the head keeps its column), the lowest sole on the ground (every frame has a foot
#   down);
# - her sword fist: the front fist at her chest, the one furthest forward in the RUN_CHEST rows (Codex drew it there in
#   every frame, in front where League's blade comes out; the far fist of its frames 1-3 is raised behind her
#   shoulder, where League hides the hand), RUN_FIST by hand where the rule picks badly;
# - clean: her palette, the outline closed, loose specks and pinholes gone (ppu_rig.tidy), no outline square more than a
#   square from a colour nor a piece of outline alone (tools/art/black_strays.py's rule), RUN_FIX squares by hand.
RUN_RAW = os.path.join(HD, "run_raw")
RUN_DIR = os.path.join(HD, "run")
RUN_PITCH = 8.5                        # raw px a design square in every run frame
RUN_CHIN = 18                          # Codex's head: rows from its hair's top to the chin (16-18 measured)
DESIGN_CHIN = 20                       # the design's head (PA.no_sword_canvas): its chin's last skin row
HEAD_AT = (-1, -2)                     # the design's hair box from Codex's: eye on eye, chin on chin
RUN_CHEST = (18, 34)                   # rows under the hair's top: her front fist's middle
RUN_SKIN = SKIN + [(195, 117, 61), (182, 106, 56)]
INK = (14, 3, 12)                      # the design's outline
# her palette's dark slate (one square of the design's far bracer): in the run it is only Codex's soft edge between a
# light square and the outline read as it (single squares on the outline) - the outline's colour there
RUN_TO_INK = [(52, 54, 62)]
RUN_FIST = {}                          # n: (x, y) her front fist's middle, by eye
RUN_FIX = {}                           # n: {(x, y): (r, g, b) or None} squares set by hand after the read


def kinds(d):
    """(opaque, outline-dark, light hair-like, green, yellow) squares of a frame in her palette."""
    c = d[..., :3].astype(int)
    op = d[..., 3] > 0
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(-1), c.min(-1)
    dark = op & (mx < 60)
    light = op & (mn > 120) & (mx - mn < 60) & (r >= b)
    green = op & (g >= r - 10) & (g > b + 15) & (mx >= 40) & ~dark
    yellow = op & (r > 200) & (g > 195) & (b < 100)
    return op, dark, light, green, yellow


def hair_piece(d, rows=24):
    """The biggest piece of light (hair) squares in the frame's top rows."""
    op, _, light, _, _ = kinds(d)
    hair = light.copy()
    hair[int(np.nonzero(op.any(1))[0].min()) + rows:] = False
    lab, n = nd.label(hair, structure=np.ones((3, 3)))
    return lab == (np.argmax(nd.sum(hair, lab, range(1, n + 1))) + 1)


def box(m):
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def head_mask(d, chin):
    """The head down to row `chin`: the colour squares (no outline, no green or yellow - the collar) 4-connected to the
    hair, its holes (the eyes) filled, and the outline squares round it one row further down."""
    op, dark, _, green, yellow = kinds(d)
    rows = np.arange(d.shape[0])[:, None]
    body = op & ~dark & ~green & ~yellow & (rows <= chin)
    lab, _ = nd.label(body)
    seed = hair_piece(d) & body
    core = np.isin(lab, [v for v in np.unique(lab[seed]) if v])
    core = nd.binary_fill_holes(core | (dark & (rows <= chin) & nd.binary_dilation(core))) & op
    ring = dark & nd.binary_dilation(core, structure=np.ones((3, 3))) & (rows <= chin + 1)
    return core | ring


def run_pieces(pal):
    """[(n, frame, stand_x)]: every run frame read on RUN_PITCH in her palette and cropped, with the x of its template
    cell's standing point (the cell's middle) in the frame's squares."""
    with open(lp(os.path.join(RUN_RAW, "sheets.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cw = spec["cell"][0]
    out = []
    for sh in spec["sheets"]:
        a = np.asarray(Image.open(lp(os.path.join(RUN_RAW, sh["name"] + ".png"))).convert("RGB")).astype(int)
        fig = cutout(a)
        lab, nl = nd.label(nd.binary_dilation(fig, iterations=6))
        sz = nd.sum(fig, lab, range(1, nl + 1))
        keep = sorted([k + 1 for k in range(nl) if sz[k] > 0.02 * fig.sum()], key=lambda k: np.nonzero(lab == k)[1].min())
        if len(keep) != len(sh["frames"]):
            sys.exit(f"{sh['name']}: {len(keep)} figures for frames {sh['frames']}")
        for i, (k, n) in enumerate(zip(keep, sh["frames"])):
            m = (lab == k) & fig
            ys, xs = np.nonzero(m)
            y0, x0 = int(ys.min()), int(xs.min())
            c, op = a[y0:ys.max() + 1, x0:xs.max() + 1], m[y0:ys.max() + 1, x0:xs.max() + 1]
            FD.PITCH = (RUN_PITCH, RUN_PITCH + 0.005)
            (_, phx), (_, phy) = FD.fit(c, op, 1), FD.fit(c, op, 0)
            d = to_palette(read_on(c, op, RUN_PITCH, phx, phy), pal)
            yy, xx = np.nonzero(d[..., 3] > 0)
            d = d[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
            stand = (i * cw + cw / 2 - x0 - phx) / RUN_PITCH - xx.min()
            out.append((n, d, float(stand)))
    return out


def lay_head(d, head, hm):
    """Codex's head cleared and the design's laid in its place -> (frame, the design head's squares in it, (dx, dy) the
    old frame moved by, Codex's hair box in the new frame)."""
    l, t, _, _ = box(hair_piece(d))
    old = head_mask(d, t + RUN_CHIN)
    hl, ht, _, _ = box(hair_piece(head))
    hy, hx = np.nonzero(hm)
    oy, ox = t + HEAD_AT[1] - ht, l + HEAD_AT[0] - hl          # head squares -> frame squares
    top, left = int(max(0, -(oy + hy.min()))), int(max(0, -(ox + hx.min())))
    right = int(max(0, ox + hx.max() + 1 - d.shape[1]))
    f = np.pad(d, ((top, 0), (left, right), (0, 0)))
    f[np.pad(old, ((top, 0), (left, right)))] = 0
    f[hy + oy + top, hx + ox + left] = head[hy, hx]
    at = np.zeros(f.shape[:2], bool)
    at[hy + oy + top, hx + ox + left] = True
    return f, at, (left, top), (l + left, t + top)


class _Ink:
    """tools/art/black_strays.py's settings for a drawn frame of hers: the design's outline colour, every colour carries
    an outline, a pocket inside her filled with the colour round it; the design's own head (ctx) kept as it is (its
    outline is two squares thick at three hair tips and under the jaw, as in every other frame of hers)."""
    id, ink, pocket, thin = "league_riven", INK, "fill", None

    def own(self, a, col):
        return col

    def protect(self, a, kind, ctx):
        return ctx

    def fill_colour(self, a, m):
        ring = nd.binary_dilation(m, structure=np.ones((3, 3))) & ~m & (a[..., 3] > 0) & ~(a[..., :3] == INK).all(-1)
        cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
        return cols[cnt.argmax()]


def front_fist(d, hair_top):
    """Her front fist: the skin piece of a hand's size furthest forward with its middle in the RUN_CHEST rows."""
    skin = np.zeros(d.shape[:2], bool)
    for c in RUN_SKIN:
        skin |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(skin, structure=np.ones((3, 3)))
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if not 4 <= len(ys) <= HAND_MAX or not RUN_CHEST[0] <= ys.mean() - hair_top <= RUN_CHEST[1]:
            continue
        if best is None or xs.max() > best[0]:
            best = (xs.max(), float(xs.mean() + 0.5), float(ys.mean() + 0.5))
    return best[1:] if best else None


def read_run(review=None):
    import black_strays as BS
    import ppu_rig as R
    design = PA.no_sword_canvas()
    pal = np.unique(design[design[..., 3] > 0][:, :3], axis=0).astype(np.uint8)
    hm = head_mask(design, DESIGN_CHIN)
    reads = run_pieces(pal)
    laid = []
    for n, d, stand in reads:
        for c in RUN_TO_INK:
            d[(d[..., :3] == c).all(-1) & (d[..., 3] > 0), :3] = INK
        f, at, (dx, dy), (cl, ct) = lay_head(d, design, hm)
        head = f.copy()
        # (a square of room round her first: the outline closed under a sole or past an edge the read cut flush)
        f, at, head = (np.pad(v, ((1, 1), (1, 1)) + ((0, 0),) * (v.ndim - 2)) for v in (f, at, head))
        f = R.tidy(f, INK)
        f, cleared, filled = BS.clean(f, _Ink(), "one", ctx=at)
        f[at] = head[at]                                         # (the design's head square for square)
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0, y0 = int(xs.min()), int(ys.min())
        f = f[y0:ys.max() + 1, x0:xs.max() + 1].copy()
        for (x, y), c in RUN_FIX.get(n, {}).items():           # (the saved frame's squares)
            f[y, x] = (0, 0, 0, 0) if c is None else (*c, 255)
        laid.append((n, f, stand + dx + 1 - x0, cl + 1 - x0, ct + 1 - y0, int(cleared.sum()), int(filled.sum())))
    # the standing point from the head: the cell's middle where Codex put it on average from its hair box
    off = float(np.median([stand - cl for _, _, stand, cl, _, _, _ in laid]))
    os.makedirs(lp(RUN_DIR), exist_ok=True)
    info = {}
    for n, f, stand, cl, ct, cleared, filled in laid:
        fist = RUN_FIST.get(n) or front_fist(f, ct)
        if fist is None:
            sys.exit(f"run_{n}: no front fist")
        info[str(n)] = dict(pivot=[round(cl + off, 2), f.shape[0]], fist=[round(v, 2) for v in fist],
                            head=[cl + HEAD_AT[0], ct + HEAD_AT[1]], size=[f.shape[1], f.shape[0]],
                            stand_off=round(stand - cl - off, 2), strays=[cleared, filled])
        Image.fromarray(f).save(lp(os.path.join(RUN_DIR, f"run_{n}.png")))
        print(f"run_{n}", info[str(n)])
    with open(lp(os.path.join(RUN_DIR, "run.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(info, f, indent=1)
    if review:
        os.makedirs(review, exist_ok=True)
        z = 6
        ims = []
        for n in sorted(info, key=int):
            im = Image.open(lp(os.path.join(RUN_DIR, f"run_{n}.png"))).convert("RGBA")
            bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
            bg.alpha_composite(im)
            big = bg.resize((im.width * z, im.height * z), Image.NEAREST)
            dr = ImageDraw.Draw(big)
            for (x, y), col in ((info[n]["pivot"], (255, 0, 0)), (info[n]["fist"], (0, 60, 255))):
                dr.ellipse([x * z - 9, y * z - 9, x * z + 9, y * z + 9], outline=col, width=3)
            ims.append((f"run_{n}", big))
        FD.strip(ims).convert("RGB").save(os.path.join(review, "run_frames.png"))
        print("review written to", review)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--run", action="store_true", help="the run's frames instead (hd/run_raw -> hd/run)")
    a = ap.parse_args()
    if a.run:
        read_run(a.review)
        return
    with open(lp(os.path.join(HD, "actions_raw", "sheets.json")), encoding="utf-8") as f:
        sheets = json.load(f)["sheets"]
    with open(lp(os.path.join(HD, "riven_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    tmp = os.path.join(os.environ.get("TEMP", "."), "riven_no_sword.png")
    pal = PA.no_sword_design(tmp).astype(np.uint8)
    out_dir = os.path.join(HD, "actions")
    os.makedirs(lp(out_dir), exist_ok=True)
    info = {}
    global SCALE
    q0 = PA.her_joints(joints["design"])
    ground0 = max(q[1] for k_, q in q0.items() if not k_.startswith("weapon"))     # the idle's ankles, ~-3.7
    for sh in sheets:
        a_ = np.asarray(Image.open(lp(os.path.join(HD, "actions_raw", sh["name"] + ".png"))).convert("RGB")).astype(int)
        fig = cutout(a_)
        # the frames: the big pieces of figure left to right (Codex kept the three cells, but not always the
        # template's 1536 x 1024 nor its cell edges)
        lab, nl = nd.label(nd.binary_dilation(fig, iterations=6))
        sz = nd.sum(fig, lab, range(1, nl + 1))
        keep = [k + 1 for k in range(nl) if sz[k] > 0.02 * fig.sum()]
        keep.sort(key=lambda k: np.nonzero(lab == k)[1].min())
        if len(keep) < len(sh["frames"]):
            sys.exit(f"{sh['name']}: {len(keep)} figures for frames {sh['frames']}")
        keep = keep[:len(sh["frames"])]           # (a last sheet's empty cells Codex filled anyway)
        pieces = []
        for k in keep:
            m = (lab == k) & fig
            ys, xs = np.nonzero(m)
            sub = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
            pieces.append((a_[sub], m[sub]))
        # her size: Codex drew each sheet on its own squares and at its own size - the hair's area (the same in
        # every pose) against the design's sets the sheet's scale
        SCALE = 1.0
        areas = [hair_area(to_palette(read_cell(c, op)[0], pal)) for c, op in pieces]
        SCALE = float(np.sqrt(np.median(areas) / DESIGN_HAIR))
        for (c, op), n in zip(pieces, sh["frames"]):
            d, _ = read_cell(c, op)
            d = to_palette(d, pal)
            ys, xs = np.nonzero(d[..., 3] > 0)
            d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            # where League's frame (the template, its standing point at 0, 0) has her: grounded, her feet over the
            # template's feet; in the air (the leap, the somersault), her middle over the template's trunk
            Q = PA.her_joints(joints["tags"][sh["tag"]][n - 1]["j"])
            pts = [q for k_, q in Q.items() if not k_.startswith("weapon")]
            low = max([q[1] for q in pts] + [Q["head"][1] + PA.HEAD_R])
            # her lowest point, 0 on the ground: League's foot joints are ankles, so measured against the idle's
            y_low = min(0.0, max(q[1] for q in pts) - max(0.0, low) - ground0)
            op_ = d[..., 3] > 0
            ys, xs = np.nonzero(op_)
            if y_low > -3:
                feet_t = (Q["l_foot"][0] + Q["r_foot"][0]) / 2
                bot = ys >= d.shape[0] - 4
                px_ = float(xs[bot].mean() + 0.5) - feet_t
            else:
                px_ = float(xs.mean() + 0.5) - (Q["pelvis"][0] + Q["chest"][0]) / 2
            pivot = (px_, d.shape[0] - y_low)
            want = (pivot[0] + Q["r_hand"][0], pivot[1] + Q["r_hand"][1] - max(0.0, low))
            name = f"{sh['tag']}_{n}"
            fist = FIST_FIX.get(name)
            dist = None
            if fist is None:
                got = find_fist(d, want)
                dist, fist = (got if got else (None, want))
            Image.fromarray(d).save(lp(os.path.join(out_dir, name + ".png")))
            info[name] = dict(pivot=[round(v, 2) for v in pivot], fist=[round(v, 2) for v in fist],
                              want=[round(v, 2) for v in want], fist_off=None if dist is None else round(dist, 1),
                              size=[d.shape[1], d.shape[0]])
            print(name, info[name])
    with open(lp(os.path.join(out_dir, "actions.json")), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        z = 6
        for tag in PA.TAGS:
            names = [k for k in info if k.rsplit("_", 1)[0] == tag]
            names.sort(key=lambda k: int(k.rsplit("_", 1)[1]))
            ims = []
            for k in names:
                im = Image.open(lp(os.path.join(out_dir, k + ".png"))).convert("RGBA")
                bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
                bg.alpha_composite(im)
                big = bg.resize((im.width * z, im.height * z), Image.NEAREST)
                dr = ImageDraw.Draw(big)
                for (x, y), col in ((info[k]["pivot"], (255, 0, 0)), (info[k]["fist"], (0, 60, 255)),
                                    (info[k]["want"], (255, 0, 255))):
                    dr.ellipse([x * z - 9, y * z - 9, x * z + 9, y * z + 9], outline=col, width=3)
                ims.append((k, big))
            FD.strip(ims).convert("RGB").save(os.path.join(a.review, f"actions_{tag}.png"))
        print("review written to", a.review)


if __name__ == "__main__":
    main()
