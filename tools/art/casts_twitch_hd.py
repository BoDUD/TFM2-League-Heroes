#!/usr/bin/env python3
"""Twitch's actions from Codex's whole-frame redraw (assets/source/twitch/hd/casts: tools/art/pack_twitch_actions.py's
pack, delivered 2026-10-24; the user: 「有问题的地方你帮我修正吧 做到完美后喊我review」), read onto the design's squares
the way Ahri's were (casts_ahri_hd.py on ahri-ppu22):

1. the near-white ground keyed off (the white flooded in from the sheet's edge: the claws' white stays inside their
   outline), each cell's figure the pieces of it big enough (the dropped crossbow of the death is one);
2. brought to the design's size: Codex drew each sheet at its own scale (5.0-7.1 px a square against the 5 asked), so
   a sheet takes the scale that gives its standing frames the design's area (AREA_SCALE: sqrt(figure pixels / design
   squares), both cells of a sheet drawn at one scale); the lying sheets of the death take the lying frame's share of
   the standing area measured on the sheets that hold both (LYING); every design square the Lab mean of the Codex
   pixels it covers, snapped to the design's colours, the outline where it covers OUTLINE_SHARE of outline; speckle
   cleaned (design_jinx_hd.clean);
3. the design's head put on (head()): the goggle, the grin and the nose drawn by hand on the design (design_twitch_hd's
   face()) in every frame, matched where Codex's head is; crossbow, arms and claws in front of the face kept on top;
4. placed on the ground: standing frames on their soles, the run's head steady, every other tag's rear foot planted.

    python tools/art/casts_twitch_hd.py --review DIR      # every tag read, at 3x
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_jinx_hd as JD  # noqa: E402
import ppu_rig as R  # noqa: E402

HERO = "twitch"
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
SRC = os.path.join(HD, "casts")
TAGS = ["run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
CELL = (768, 1024)
WHITE = 228                     # a ground pixel: every channel at least this, joined to the sheet's edge
MIN_PIECE = 300                 # Codex pixels: smaller bits off the figure dropped
ENCLOSED, POCKET = 240, 40
LYING = 0.91                    # a lying frame's area over a standing one at one scale (dead_1, dead_2: 0.906 / 0.914)
LYING_SHEETS = {"dead_3", "dead_4"}
UPRIGHT = {"dead_1": [0], "dead_2": [0]}    # the cells of a mixed sheet that stand (or fly) upright
SPECK = 12                      # design squares: a smaller piece apart from the figure is noise
SPECK_DEAD = 100                # the death: the dropped crossbow is the only piece apart (a curl of the tail broke off)
OUTLINE = (14, 10, 16)
OUTLINE_SHARE = 0.40
# the head: the design's squares inside HEAD_POLY (the ears, the goggle, the snout with the grin, not the scarf nor
# the backpack); NEAR_EYE the goggle's middle
HEAD_POLY = [(43, 0), (56, 0), (57, 7), (65, 4), (77, 0), (79, 12), (85, 19), (85, 29), (80, 37), (70, 37),
             (63, 33), (57, 29), (52, 24), (43, 22)]
NEAR_EYE = (63.5, 18.5)
GOGGLE = (58, 13, 70, 25)       # the design's goggle box (x0, y0, x1, y1)
ZONE = (-19.5, 17, 26)          # from the goggle: Codex's head lies right of x - 19.5 (the near ear's left edge), above
                                # y + 17 (the jaw), left of x + 26 (past the nose)
FACE_LAB = 14                   # Lab distance: a head square matched on a square of its own colour family
HEAD_DROP = 30                  # rows under the figure's top the ears may sit
NO_HEAD = {"dead_1", "dead_2", "dead_3", "dead_4", "dead_5", "dead_6", "dead_7", "dead_8"}   # Codex's own head kept: turned up (the shot's recoil), tilted in the fall, lying
GROUND = 71                     # the design's first row under the soles
PIVOT_COL = 53                  # the design's standing point: between the rear claws (33) and the front claws' tips (74)
CELL_X = 384                    # Codex's standing point in a cell (the template's)
FEET_ROWS, FEET_WIDE, FEET_GAP = 3, 3, 6       # a foot's claws lie 1-3 squares apart, the feet 10 or more
OLD_SOLES = 11                  # the old 1x frames: the soles this many pixels under the frame's centre standing
OLD_REV = "9dd65f7d4"           # main when the redo began: the old sheet the lifts are read from
PPU = 2.2


def lp(p):
    return R.lp(p)


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


def rgb24(a):
    return (a[..., 0].astype(np.int32) << 16) | (a[..., 1].astype(np.int32) << 8) | a[..., 2]


def keyed(rgb):
    """The sheet with its near-white ground transparent: the white joined to the sheet's edge, and the white pockets
    the crossbow's string and arms close (ENCLOSED: a patch of at least POCKET pixels, every channel ENCLOSED or more -
    the claws and teeth are cream, far darker)."""
    light = rgb.min(-1) >= WHITE
    lbl, _ = ndimage.label(light)
    edge = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    bg = np.isin(lbl, list(edge))
    plbl, n = ndimage.label((rgb.min(-1) >= ENCLOSED) & ~bg)
    if n:
        sz = ndimage.sum(np.ones_like(plbl), plbl, range(1, n + 1))
        bg |= np.isin(plbl, [k + 1 for k in range(n) if sz[k] >= POCKET])
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(bg, 0, 255)
    return out


def figure(cell):
    op = cell[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if not n:
        return None
    sz = ndimage.sum(op, lbl, range(1, n + 1))
    keep = np.isin(lbl, [k + 1 for k in range(n) if sz[k] >= MIN_PIECE])
    out = cell.copy()
    out[~keep] = 0
    return out if keep.any() else None


def palette():
    d = design()
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0)


def resample(fig, step, pal):
    """Codex's figure -> design squares (step Codex pixels a square): per square the Lab mean of what it covers but
    the outline, snapped to pal; the outline where its share is OUTLINE_SHARE (casts_ahri_hd.resample)."""
    import design_lux_hd as DL
    ys, xs = np.nonzero(fig[..., 3] > 0)
    fig = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    op = fig[..., 3] > 0
    plab = color.rgb2lab(pal[None].astype(float) / 255.0)[0]
    lab = color.rgb2lab(fig[..., :3] / 255.0)
    near = np.argmin(((lab[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
    oi = int(np.argmin(np.abs(pal.astype(int) - np.array(OUTLINE)).sum(1)))
    out_px = (op & (near == oi)).astype(float)
    DL.STEP = step
    wy, wx = DL.cover(fig.shape[0]), DL.cover(fig.shape[1])
    opf = op.astype(float)
    inner = opf * (1 - out_px)
    cov, oc, wi = wy @ opf @ wx.T, wy @ out_px @ wx.T, wy @ inner @ wx.T
    area = wy.sum(1)[:, None] * wx.sum(1)[None, :]
    mean = np.stack([wy @ (lab[..., c] * inner) @ wx.T for c in range(3)], -1) / np.maximum(wi, 1e-9)[..., None]
    k = np.argmin(((mean[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
    keep = cov >= 0.5 * area
    d = np.zeros(cov.shape + (4,), np.uint8)
    d[keep, :3] = pal[k[keep]]
    d[keep & ((oc >= OUTLINE_SHARE * cov) | (wi < 0.2 * area)), :3] = pal[oi]
    d[keep, 3] = 255
    return JD.clean(d), (xs.min(), ys.min())


def head_piece():
    """The design's head squares (HEAD_POLY) and its top-left in the design."""
    d = design()
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in HEAD_POLY], fill=1, outline=1)
    m = np.asarray(img, bool) & (d[..., 3] > 0)
    ys, xs = np.nonzero(m)
    piece = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    mm = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    piece[mm] = sub[mm]
    return piece, (int(xs.min()), int(ys.min()))


def head_at(d, img):
    """Where the head piece img sits best on the read frame d: the most of its squares on a square of the same colour
    family (Lab within FACE_LAB) less those on nothing, its face (the goggle, the grin, the nose, the ears' pink:
    every head colour but the fur's greys and the outline) counting four times. -> (x, y) of img's top-left, score."""
    hy, hx = np.nonzero(img[..., 3] > 0)
    hl = color.rgb2lab(img[hy, hx, :3][None].astype(float) / 255.0)[0]
    grey = (np.abs(img[hy, hx, 0].astype(int) - img[hy, hx, 1]) < 18) & (np.abs(img[hy, hx, 1].astype(int)
                                                                                - img[hy, hx, 2]) < 40)
    wt = np.where(grey, 1.0, 4.0)
    op = d[..., 3] > 0
    dl = color.rgb2lab(d[..., :3].astype(float) / 255.0)
    top = np.nonzero(op.any(1))[0].min()
    best, at = -1e9, None
    for sy in range(top - hy.min() - 4, top - hy.min() + HEAD_DROP + 1):
        for sx in range(-hx.min() - 10, d.shape[1] - hx.max() + 10):
            ty, tx = hy + sy, hx + sx
            ins = (ty >= 0) & (ty < d.shape[0]) & (tx >= 0) & (tx < d.shape[1])
            on = np.zeros(len(hy), bool)
            on[ins] = op[ty[ins], tx[ins]]
            dist = np.full(len(hy), 1e9)
            dist[on] = np.sqrt(((dl[ty[on], tx[on]] - hl[on]) ** 2).sum(-1))
            sc = (wt * (dist < FACE_LAB)).sum() - (wt * ~on).sum()
            if sc > best:
                best, at = sc, (sx, sy)
    return at, best / wt.sum()


def sheets():
    return json.load(open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8"))["sheets"]


def scales():
    """{sheet name: Codex pixels a design square} (AREA_SCALE / LYING, see the docstring)."""
    D = design()
    area = float((D[..., 3] > 0).sum())
    out = {}
    for sh in sheets():
        k = keyed(np.asarray(Image.open(lp(os.path.join(SRC, sh["name"] + ".png"))).convert("RGB")))
        s = []
        for i in range(len(sh["frames"])):
            c = figure(k[:, i * CELL[0]:(i + 1) * CELL[0]])
            if c is None or i not in UPRIGHT.get(sh["name"], range(9)):
                continue
            s.append(np.sqrt((c[..., 3] > 0).sum() / area))
        v = float(np.mean(s))
        out[sh["name"]] = v / LYING if sh["name"] in LYING_SHEETS else v
    return out


def frames():
    """{"<tag>_<frame>": (design-square picture, x, y of its top-left on the design's grid, near eye on it or None)}
    for every frame Codex drew, placed by Codex's own cell: its standing point (CELL_X) on PIVOT_COL, the sheet's
    ground (its lowest sole) on GROUND."""
    pal = palette()
    sc = scales()
    piece, (px0, py0) = head_piece()
    out = {}
    for sh in sheets():
        tag = sh["tag"]
        k = keyed(np.asarray(Image.open(lp(os.path.join(SRC, sh["name"] + ".png"))).convert("RGB")))
        cells = [figure(k[:, i * CELL[0]:(i + 1) * CELL[0]]) for i in range(len(sh["frames"]))]
        ground = max(int(np.nonzero(c[..., 3].any(1))[0].max()) + 1 for c in cells if c is not None)
        step = sc[sh["name"]]
        for fno, c in zip(sh["frames"], cells):
            if c is None:
                continue
            d, (cx0, cy0) = resample(c, step, pal)
            x, y = int(round(PIVOT_COL + (cx0 - CELL_X) / step)), int(round(GROUND + (cy0 - ground) / step))
            name = f"{tag}_{fno}"
            eye = None
            if name not in NO_HEAD:
                d, (gx, gy), eye = head(d, piece, (NEAR_EYE[0] - px0, NEAR_EYE[1] - py0))
                x, y = x + gx, y + gy
            out[name] = (d, x, y, eye)
            print(name, "step", round(step, 2), "size", d.shape[1], "x", d.shape[0])
    return out


def goggle_at(d):
    """Codex's goggle on the read frame: where the design's goggle (GOGGLE: its ring, lens and pupil) lies on the most
    squares of their own colour family (Lab within FACE_LAB), in the frame's upper half. -> its middle (x, y)."""
    D = design()
    x0, y0, x1, y1 = GOGGLE
    g = D[y0:y1, x0:x1]
    gy, gx = np.nonzero(g[..., 3] > 0)
    gl = color.rgb2lab(g[gy, gx, :3][None].astype(float) / 255.0)[0]
    op = d[..., 3] > 0
    dl = color.rgb2lab(d[..., :3].astype(float) / 255.0)
    best, at = -1, None
    for sy in range(0, d.shape[0] // 2):
        for sx in range(0, d.shape[1] - (x1 - x0)):
            ty, tx = gy + sy, gx + sx
            ins = ty < d.shape[0]
            on = np.zeros(len(gy), bool)
            on[ins] = op[ty[ins], tx[ins]]
            sc = (np.sqrt(((dl[ty[on], tx[on]] - gl[on]) ** 2).sum(-1)) < FACE_LAB).sum()
            if sc > best:
                best, at = sc, (sx, sy)
    return at[0] + NEAR_EYE[0] - x0, at[1] + NEAR_EYE[1] - y0


def head(d, piece, eye):
    """The design's head on the read frame with its goggle on Codex's (goggle_at), Codex's head under it; the squares
    under it of a colour the head lacks (the crossbow, a bracer, a hand) kept on top; then what shows of Codex's head
    past the design's (an ear set higher, a longer snout, a lower jaw) peeled off: head-coloured squares outside the
    design's head, within ZONE of the goggle, open to the ground, layer by layer. -> (frame grown to hold it, where
    the old frame's top-left went in it negated, near eye)."""
    ex, ey = goggle_at(d)
    sx, sy = int(round(ex - eye[0])), int(round(ey - eye[1]))
    X0, Y0 = min(0, sx), min(0, sy)
    X1, Y1 = max(d.shape[1], sx + piece.shape[1]), max(d.shape[0], sy + piece.shape[0])
    can = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8)
    can[-Y0:-Y0 + d.shape[0], -X0:-X0 + d.shape[1]] = d
    ox, oy = sx - X0, sy - Y0
    hm = piece[..., 3] > 0
    m = np.zeros(can.shape[:2], bool)
    m[oy:oy + piece.shape[0], ox:ox + piece.shape[1]] = hm
    head_cols = set(rgb24(piece)[hm].tolist())
    rgb = rgb24(can)
    op = can[..., 3] > 0
    front = m & op & ~np.isin(rgb, list(head_cols))
    lbl, n = ndimage.label(front)
    for j in range(1, n + 1):                      # specks of an odd colour on the old head: not a thing in front
        if (lbl == j).sum() < 4:
            front[lbl == j] = False
    front |= m & op & ndimage.binary_dilation(front) & (rgb == rgb24(np.array([[list(OUTLINE)]]))[0, 0])
    keep = can.copy()
    sub = can[oy:oy + piece.shape[0], ox:ox + piece.shape[1]]
    sub[hm] = piece[hm]
    can[front] = keep[front]
    gx, gy = ox + eye[0], oy + eye[1]
    # Codex's head past the design's: over the design head's lowest square in each of its columns (the ears set
    # higher, the brow between them), and right of it over its nose's lowest row (a longer snout)
    above = np.zeros(can.shape[:2], bool)
    cols = np.nonzero(m.any(0))[0]
    for c in cols:
        above[:np.nonzero(m[:, c])[0].max() + 1, c] = True
    right = int(cols.max())
    nose_low = int(np.nonzero(m[:, right - 2:right + 1].any(1))[0].max())
    above[:nose_low + 1, right + 1:min(can.shape[1], int(gx + ZONE[2]))] = True
    gone = above & ~m & ~front & (can[..., 3] > 0) & np.isin(rgb24(can), list(head_cols))
    can[gone] = 0
    return can, (X0, Y0), (gx, gy)


def feet(d):
    """The middles of the groups (FEET_WIDE squares or wider, FEET_GAP apart) of squares in the FEET_ROWS rows over
    the lowest square, and that row. -> ([x, ...] in d's columns, the row under the lowest)."""
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    low = ys.max() + 1
    xs = np.nonzero(op[low - FEET_ROWS:low].any(0))[0]
    groups = [g for g in np.split(xs, np.where(np.diff(xs) > FEET_GAP)[0] + 1) if g.max() - g.min() + 1 >= FEET_WIDE]
    return [(g.min() + g.max() + 1) / 2.0 for g in groups], low


def old_lift():
    """{"<tag>_<frame>": design rows the old 1x frame stood off the ground} (its soles over OLD_SOLES): the old sheet
    as main had it when the redo began (OLD_REV - the sheet in league/ is this redo's own once exported)."""
    import io
    import subprocess
    stem = "league/champions/league_twitch"

    def show(path):
        return subprocess.run(["git", "show", f"{OLD_REV}:{path}"], cwd=R.ROOT, check=True, capture_output=True).stdout
    sheet = np.asarray(Image.open(io.BytesIO(show(stem + "#sheet.png"))).convert("RGBA"))
    anims = json.loads(show(stem + "#anim.fanim").decode("utf-8-sig"))["anims"]
    out = {}
    for tag in TAGS:
        for i, f in enumerate(anims[tag]["frames"]):
            dd = f["data"]
            x, y, w, h = (int(dd[k]) for k in ("x", "y", "w", "h"))
            ys = np.nonzero(sheet[y:y + h, x:x + w, 3].any(1))[0]
            out[f"{tag}_{i + 1}"] = max(0.0, (OLD_SOLES - (ys.max() + 1 - h / 2)) * PPU)
    return out


def placed():
    """{name: (picture, x, y)}: frames() set on the ground and along it. Each frame's lowest square on GROUND less the
    old frame's lift (the hop, the run's bob); the run keeps his goggle in one column; every other tag starts with his
    feet's middle on PIVOT_COL and keeps the rear foot planted while both feet stand; the frames between (in the air)
    run straight from shift to shift; the death keeps Codex's cells."""
    raw = cached_frames()
    lift = old_lift()
    tags = {}
    for n in sorted(raw, key=lambda n: int(n.rsplit("_", 1)[1])):
        tags.setdefault(n.rsplit("_", 1)[0], []).append(n)
    out = {}
    for tag, names in tags.items():
        ys = {}
        for n in names:
            d, x, y, eye = raw[n]
            _, low = feet(d)
            ys[n] = int(round(GROUND - lift.get(n, 0.0))) - low
        known = {}
        if tag == "dead":
            known = {i: 0 for i in range(len(names))}
        elif tag == "run":
            for i, n in enumerate(names):
                known[i] = NEAR_EYE[0] - (raw[n][1] + raw[n][3][0])
        else:
            rear = None
            for i, n in enumerate(names):
                d, x, y, eye = raw[n]
                mids, low = feet(d)
                if len(mids) < 2 or lift.get(n, 0.0) > 0:
                    continue
                if rear is None:
                    known[i] = PIVOT_COL - (x + (mids[0] + mids[-1]) / 2.0)
                    rear = x + mids[0] + known[i]
                else:
                    known[i] = rear - (x + mids[0])
            if not known:
                known[0] = 0.0
        for i, n in enumerate(names):
            if i in known:
                v = known[i]
            else:
                lo = [k for k in known if k < i]
                hi = [k for k in known if k > i]
                if lo and hi:
                    a, b = max(lo), min(hi)
                    v = known[a] + (known[b] - known[a]) * (i - a) / (b - a)
                else:
                    v = known[max(lo)] if lo else known[min(hi)]
            d, x, y, eye = raw[n]
            X = x + int(round(v))
            out[n] = (despeck(d, SPECK_DEAD if tag == "dead" else SPECK), X, ys[n])
            EYES[n] = None if eye is None else (X + eye[0], ys[n] + eye[1])
    return out


EYES = {}                       # placed(): each frame's goggle middle on the design's grid (None: Codex's head kept)


def despeck(d, most):
    """Pieces of fewer than `most` squares off the figure (a string's end, a scarf speck by the snout) dropped."""
    lbl, n = ndimage.label(d[..., 3] > 0, structure=np.ones((3, 3)))
    if n < 2:
        return d
    sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    out = d.copy()
    out[np.isin(lbl, [k + 1 for k in range(n) if sz[k] < most])] = 0
    return out


def cached_frames():
    """frames(), kept in the temp folder against this file's, the design's and the sources' bytes."""
    import hashlib
    import pickle
    import tempfile
    h = hashlib.sha1(open(__file__, "rb").read() + open(lp(os.path.join(HD, "design.png")), "rb").read())
    for f in sorted(os.listdir(lp(SRC))):
        if f.endswith(".png") or f.endswith(".json"):
            h.update(open(lp(os.path.join(SRC, f)), "rb").read())
    path = os.path.join(tempfile.gettempdir(), f"casts_twitch_{h.hexdigest()[:16]}.pkl")
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    fr = frames()
    pickle.dump(fr, open(path, "wb"))
    return fr


def review(fr, out_dir, z=4, tags=TAGS):
    """Per tag: <out_dir>/<tag>.gif (the frames on one canvas, the design's ground and standing point marked) and
    <tag>.png (the frames side by side), z screen pixels a square."""
    os.makedirs(out_dir, exist_ok=True)
    allx = [x for d, x, y in fr.values()] + [x + d.shape[1] for d, x, y in fr.values()]
    ally = [y for d, x, y in fr.values()] + [y + d.shape[0] for d, x, y in fr.values()]
    X0, X1, Y0, Y1 = min(allx) - 2, max(allx) + 2, min(ally) - 2, max(GROUND + 3, max(ally) + 2)
    for t in tags:
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        ims = []
        for n in names:
            d, x, y = fr[n]
            can = Image.new("RGBA", (X1 - X0, Y1 - Y0), (96, 112, 96, 255))
            dr = ImageDraw.Draw(can)
            dr.line([(0, GROUND - Y0), (X1 - X0, GROUND - Y0)], fill=(70, 80, 70, 255))
            dr.line([(PIVOT_COL - X0, GROUND - Y0), (PIVOT_COL - X0, GROUND - Y0 + 2)], fill=(200, 60, 60, 255))
            can.alpha_composite(Image.fromarray(d), (x - X0, y - Y0))
            ims.append(can.convert("RGB").resize((can.width * z, can.height * z), Image.NEAREST))
        ims[0].save(os.path.join(out_dir, f"{t}.gif"), save_all=True, append_images=ims[1:], duration=150, loop=0)
        strip = Image.new("RGB", (sum(i.width + 8 for i in ims), ims[0].height), (30, 30, 30))
        for i, im in enumerate(ims):
            strip.paste(im, (i * (im.width + 8), 0))
        strip.save(os.path.join(out_dir, f"{t}.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr = placed()
    if a.review:
        review(fr, a.review)
        print("written", a.review)


if __name__ == "__main__":
    main()
