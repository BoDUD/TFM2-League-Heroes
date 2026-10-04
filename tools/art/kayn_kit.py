"""Kayn strip repair kit (copied into the repo from work/ka/fixkit.py, which the repair workflows of 2026-10-04 used;
tools/art/rig_kayn.py builds on it): look at frames, measure them and edit them pixel by pixel (1x, one game pixel per pixel).

    python tools/art/kayn_kit.py show <tag> [--frames 1,2] [--z 8] [--src orig|work] [--out FILE]
    python tools/art/kayn_kit.py ref <tag> <frame> [--z 6] [--out FILE]      # our frame | League's frame (game size) | League's render
    python tools/art/kayn_kit.py check <tag> [--src work]                    # per frame: pieces, head match, halo, holes, feet line
    python tools/art/kayn_kit.py compare <tag> [--z 4] [--out FILE]          # orig vs work, changed pixels marked
    python tools/art/kayn_kit.py gif <tag> [--src work] [--out FILE]         # the strip playing at its frame times, 4x
    python tools/art/kayn_kit.py design [--form base|darkin|shadow] [--z 10]  # the approved design with a coordinate grid
    python tools/art/kayn_kit.py legs <tag> [--src work]                     # run: the two lowest leg blobs per frame

Tags: run attack skill skill2 ult ult_exit transform hit dead (base) and rh_<tag> / sh_<tag> for attack skill skill2
ult_exit (the Darkin's / the Shadow Assassin's strips on the base strip's cells). A frame is a 96 x 128 RGBA array (cell
rows x columns, the pivot at cells.json's "pivot", the soles' row = pivot y + 11 = row 81; NOTHING may be below row 81).

Folders (Temp/ka_work/perfect):
  orig/kayn_<tag>.png   Codex's strips as imported (8x, frozen - never write here)
  work/kayn_<tag>.png   the repaired strips (8x; created from orig on the first save)
  refs/                 designs, heads, idle strip, League's frames (now_<tag>.png at game size 8x, pose_<tag>.png renders)
  views/                pictures written by show/ref/compare/gif (open them with the Read tool)

Library (import with sys.path.insert(0, 'tools/art'); import kayn_kit as K):
  K.load(tag, src='work'|'orig') -> list of frames      K.save(tag, frames)  (writes work/ at 8x + a 1x copy)
  K.pieces(frame) -> [(size, mask)] largest first       K.head_match(frame, form) -> (share, x, y)
  K.paste_head(frame, form, x, y)                       K.halo(frame, form, x, y, r=3) -> mask of pixels round the head
  K.holes(frame) -> mask of clear pixels shut in by 4 opaque neighbours
  K.palette(form=None) -> {hex: (r,g,b)}                 K.nearest(rgb) -> palette rgb
  K.line(frame, (x0,y0), (x1,y1), rgb, width=1)         K.move(frame, mask, dx, dy)   K.erase(frame, mask)
  K.rotsprite(sprite, joint, deg)                       K.part(frame, mask, joint) -> (sprite, joint in sprite)
  K.stamp(frame, sprite, joint_sprite, at_xy)           K.design(form) -> the design on a 96x128 cell at the idle pivot
  K.form_of(tag) -> 'base'|'darkin'|'shadow'            K.pivot(tag, k) -> (x, y) of frame k (0-based)
  K.outlined(frame) -> the frame as the game will show it (the import closes the outline with #0B0710:
                       strips.complete_outline; nothing is added under the soles' row)
  `show ... --outlined` draws the frames that way.
"""
import argparse
import json
import os
import shutil
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
KA = os.path.dirname(os.path.dirname(HERE))          # the repo
ROOT = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ka_work", "perfect")
ORIG, WORK, REFS, VIEWS = (os.path.join(ROOT, d) for d in ("orig", "work", "refs", "views"))
PACK = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ka_work", "strips", "kayn_strips_pack")
CELLS = os.path.join(PACK, "kayn_cells.json")
Z8 = 8
FEET_ROW = 81
OLIVE = (150, 170, 120)
DARK_BG = (28, 26, 38)
BASE_TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "ult_exit", "transform", "hit", "dead"]
FORM_TAGS = ["attack", "skill", "skill2", "ult_exit"]
FORMS = {"base": "", "darkin": "rh_", "shadow": "sh_"}
DESIGN = {"base": "kayn_design_1x.png", "darkin": "kayn_darkin_design_1x.png", "shadow": "kayn_shadow_design_1x.png"}
HEAD = {"base": "kayn_head_1x.png", "darkin": "kayn_darkin_head_1x.png", "shadow": "kayn_shadow_head_1x.png"}
DESIGN_PIVOT = (64, 88)          # the designs' pivot on their 128x128 canvas


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def font(n):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", n)
    except OSError:
        return ImageFont.load_default()


_cells = None


def cells():
    global _cells
    if _cells is None:
        with open(CELLS, encoding="utf-8") as f:
            _cells = json.load(f)
    return _cells


def base_tag(tag):
    return tag[3:] if tag[:3] in ("rh_", "sh_") else tag


def form_of(tag):
    return "darkin" if tag.startswith("rh_") else "shadow" if tag.startswith("sh_") else "base"


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def pivot(tag, k):
    return tuple(cells()["tags"][base_tag(tag)][k]["pivot"])


def durations(tag):
    return [fr["ms"] for fr in cells()["tags"][base_tag(tag)]]


def read_strip(path, n):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    if a.shape[0] % Z8 == 0 and a.shape[0] >= 96 * Z8 // 2 and a.shape[1] >= 128 * Z8 // 2:
        a = a[Z8 // 2::Z8, Z8 // 2::Z8]
    a = a.copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    cols, rows = layout(n)
    return [a[(k // cols) * 96:(k // cols + 1) * 96, (k % cols) * 128:(k % cols + 1) * 128].copy() for k in range(n)]


def load(tag, src="work"):
    """The strip's frames (1x). src 'work' falls back to orig until the strip is first saved."""
    n = len(cells()["tags"][base_tag(tag)])
    if tag == "idle":
        return read_strip(os.path.join(REFS, "kayn_idle.png"), n)
    path = os.path.join(WORK if src == "work" else ORIG, f"kayn_{tag}.png")
    if src == "work" and not os.path.exists(path):
        path = os.path.join(ORIG, f"kayn_{tag}.png")
    return read_strip(path, n)


def save(tag, frames):
    n = len(frames)
    cols, rows = layout(n)
    a = np.zeros((rows * 96, cols * 128, 4), np.uint8)
    for k, f in enumerate(frames):
        f = f.copy()
        f[f[..., 3] < 128] = 0
        f[f[..., 3] > 0, 3] = 255
        a[(k // cols) * 96:(k // cols + 1) * 96, (k % cols) * 128:(k % cols + 1) * 128] = f
    os.makedirs(WORK, exist_ok=True)
    Image.fromarray(np.repeat(np.repeat(a, Z8, 0), Z8, 1)).save(lp(os.path.join(WORK, f"kayn_{tag}.png")))
    Image.fromarray(a).save(lp(os.path.join(WORK, f"kayn_{tag}_1x.png")))


def _rgba(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def design(form="base"):
    """The approved design on a 96 x 128 cell with its pivot where the idle's pivot is."""
    d = _rgba(os.path.join(PACK, "design", DESIGN[form]))
    px, py = cells()["tags"]["idle"][0]["pivot"]
    out = np.zeros((96, 128, 4), np.uint8)
    dy, dx = py - DESIGN_PIVOT[1], px - DESIGN_PIVOT[0]
    ys, xs = np.nonzero(d[..., 3] > 0)
    for y, x in zip(ys, xs):
        yy, xx = y + dy, x + dx
        if 0 <= yy < 96 and 0 <= xx < 128:
            out[yy, xx] = d[y, x]
    return out


def head_template(form):
    h = _rgba(os.path.join(PACK, "design", HEAD[form]))
    ys, xs = np.nonzero(h[..., 3] > 0)
    return h[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def head_match(frame, form):
    """(share of the design head's pixels found exactly, x, y of the template's top-left) at the best place."""
    t = head_template(form)
    m = t[..., 3] > 0
    win = np.lib.stride_tricks.sliding_window_view(frame, (t.shape[0], t.shape[1], 4))[:, :, 0]
    hits = ((win == t).all(-1) & m).sum((-1, -2))
    y, x = np.unravel_index(int(hits.argmax()), hits.shape)
    return float(hits[y, x] / m.sum()), int(x), int(y)


def paste_head(frame, form, x, y):
    t = head_template(form)
    m = t[..., 3] > 0
    reg = frame[y:y + t.shape[0], x:x + t.shape[1]]
    reg[m] = t[m]
    return frame


def head_mask(frame, form, x, y):
    t = head_template(form)
    m = np.zeros(frame.shape[:2], bool)
    m[y:y + t.shape[0], x:x + t.shape[1]] = t[..., 3] > 0
    return m


def halo(frame, form, x, y, r=3):
    """Opaque pixels within r of the pasted head (outside it) and not part of the body below the chin: what Codex left of
    its own head shows up here (check by eye: an arm or the scythe may pass legitimately)."""
    hm = head_mask(frame, form, x, y)
    grow = hm.copy()
    for _ in range(r):
        g = grow.copy()
        g[1:] |= grow[:-1]
        g[:-1] |= grow[1:]
        g[:, 1:] |= grow[:, :-1]
        g[:, :-1] |= grow[:, 1:]
        grow = g
    t = head_template(form)
    ring = grow & ~hm
    ring[y + t.shape[0]:] = False                 # below the chin: the body
    return ring & (frame[..., 3] > 0)


def pieces(frame, min_size=1):
    """8-connected opaque pieces, largest first: [(size, mask)]."""
    op = frame[..., 3] > 0
    lab = np.zeros(op.shape, int)
    out = []
    n = 0
    for y0, x0 in zip(*np.nonzero(op)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        q = deque([(y0, x0)])
        c = 0
        while q:
            y, x = q.popleft()
            c += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < op.shape[0] and 0 <= xx < op.shape[1] and op[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        q.append((yy, xx))
        if c >= min_size:
            out.append((c, lab == n))
    return sorted(out, key=lambda t: -t[0])


def holes(frame):
    op = frame[..., 3] > 0
    p = np.pad(op, 1)
    return ~op & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]


def palette(form=None):
    cols = {}
    for f, fn in DESIGN.items():
        if form and f != form:
            continue
        d = _rgba(os.path.join(PACK, "design", fn))
        for c in d[d[..., 3] > 0][:, :3]:
            cols["#%02X%02X%02X" % tuple(int(v) for v in c)] = tuple(int(v) for v in c)
    return cols


def nearest(rgb):
    P = np.array(list(palette().values()), int)
    return tuple(int(v) for v in P[((P - np.array(rgb, int)) ** 2).sum(1).argmin()])


def line(frame, p0, p1, rgb, width=1):
    """A pixel line (Bresenham) from p0 to p1 (x, y), `width` pixels thick (grown downward/right)."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        for wy in range(width):
            for wx in range(width):
                yy, xx = y0 + wy, x0 + wx
                if 0 <= yy < frame.shape[0] and 0 <= xx < frame.shape[1]:
                    frame[yy, xx, :3] = rgb
                    frame[yy, xx, 3] = 255
        if (x0, y0) == (x1, y1):
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return frame


def move(frame, mask, dx, dy):
    pix = frame[mask].copy()
    ys, xs = np.nonzero(mask)
    frame[mask] = 0
    for (y, x), p in zip(zip(ys + dy, xs + dx), pix):
        if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]:
            frame[y, x] = p
    return frame


def erase(frame, mask):
    frame[mask] = 0
    return frame


def outlined(frame):
    """The frame after the import's outline pass (tools/art/import_native.py COMPLETE)."""
    sys.path.insert(0, os.path.join(KA, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import strips as G
    b = np.pad(frame, ((1, 1), (1, 1), (0, 0)))
    ys = np.nonzero(b[..., 3].any(1))[0]
    low = int(ys.max()) if len(ys) else 0
    out, _, _ = G.complete_outline(b, color=(11, 7, 16), dark=70, feet=max(FEET_ROW + 1, low))
    return out[1:-1, 1:-1]


def part(frame, mask, joint):
    """The masked pixels as a sprite, with the joint (x, y in the frame) in sprite coordinates."""
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    sub = mask[y0:y1, x0:x1]
    s[sub] = frame[y0:y1, x0:x1][sub]
    return s, (joint[0] - x0, joint[1] - y0)


def scale2x(s):
    key = (s[..., 0].astype(np.int64) << 24) | (s[..., 1].astype(np.int64) << 16) | \
          (s[..., 2].astype(np.int64) << 8) | s[..., 3].astype(np.int64)
    p = np.pad(key, 1, mode="edge")
    A, Bv, C, D = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]
    pk = np.pad(s, ((1, 1), (1, 1), (0, 0)), mode="edge")
    up, right, left, down = pk[:-2, 1:-1], pk[1:-1, 2:], pk[1:-1, :-2], pk[2:, 1:-1]
    h, w = s.shape[:2]
    out = np.zeros((h * 2, w * 2, 4), np.uint8)
    out[0::2, 0::2] = np.where(((C == A) & (C != D) & (A != Bv))[..., None], up, s)
    out[0::2, 1::2] = np.where(((A == Bv) & (A != C) & (Bv != D))[..., None], right, s)
    out[1::2, 0::2] = np.where(((D == C) & (D != Bv) & (C != A))[..., None], left, s)
    out[1::2, 1::2] = np.where(((Bv == D) & (Bv != A) & (D != C))[..., None], down, s)
    return out


def rotsprite(s, j, deg):
    """RotSprite about joint j (x, y in the sprite), + = counter-clockwise on screen: (sprite, joint)."""
    big = scale2x(scale2x(scale2x(s)))
    h, w = s.shape[:2]
    r = int(np.ceil(np.hypot(max(j[0], w - j[0]), max(j[1], h - j[1])))) + 2
    t = np.radians(deg)
    oy, ox = np.mgrid[-r:r + 1, -r:r + 1]
    sx = np.cos(t) * ox - np.sin(t) * oy
    sy = np.sin(t) * ox + np.cos(t) * oy
    bx = np.floor((sx + j[0] + 0.5) * 8).astype(int)
    by = np.floor((sy + j[1] + 0.5) * 8).astype(int)
    ok = (bx >= 0) & (bx < w * 8) & (by >= 0) & (by < h * 8)
    out = np.zeros((2 * r + 1, 2 * r + 1, 4), np.uint8)
    out[ok] = big[by[ok], bx[ok]]
    return out, (r, r)


def stamp(frame, sprite, joint, at):
    """Draw the sprite's opaque pixels with its joint on `at` (x, y in the frame)."""
    m = sprite[..., 3] > 0
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        yy, xx = y - joint[1] + at[1], x - joint[0] + at[0]
        if 0 <= yy < frame.shape[0] and 0 <= xx < frame.shape[1]:
            frame[yy, xx] = sprite[y, x]
    return frame


# ---------------------------------------------------------------------------------------------------- pictures
def _tile(frame, z, grid=True, mark=None, bg=OLIVE, label=None, piv=None):
    h, w = frame.shape[:2]
    top = 20 if label else 0
    im = Image.new("RGB", (w * z, h * z + top), bg)
    t = Image.fromarray(np.ascontiguousarray(frame)).resize((w * z, h * z), Image.NEAREST)
    im.paste(t, (0, top), t)
    d = ImageDraw.Draw(im)
    if grid and z >= 4:
        for x in range(0, w + 1):
            if x % 10 == 0:
                d.line([(x * z, top), (x * z, top + h * z)], fill=(90, 105, 80), width=1)
        for y in range(0, h + 1):
            if y % 10 == 0:
                d.line([(0, top + y * z), (w * z, top + y * z)], fill=(90, 105, 80), width=1)
        for x in range(0, w, 10):
            d.text((x * z + 2, top + 1), str(x), fill=(40, 50, 40), font=font(10))
        for y in range(10, h, 10):
            d.text((2, top + y * z + 1), str(y), fill=(40, 50, 40), font=font(10))
    d.line([(0, top + (FEET_ROW + 1) * z), (w * z, top + (FEET_ROW + 1) * z)], fill=(220, 40, 40), width=1)
    if piv:
        px, py = piv
        d.line([(px * z + z // 2, top + py * z - 6), (px * z + z // 2, top + py * z + 6)], fill=(40, 60, 220), width=2)
    if mark is not None:
        ys, xs = np.nonzero(mark)
        for y, x in zip(ys, xs):
            d.rectangle([x * z, top + y * z, x * z + z - 1, top + y * z + z - 1], outline=(255, 0, 255), width=max(1, z // 4))
    if label:
        d.text((4, 2), label, fill=(0, 0, 0) if bg == OLIVE else (240, 240, 240), font=font(14))
    return im


def _row(tiles, gap=8, bg=(255, 255, 255)):
    W = sum(t.width + gap for t in tiles)
    H = max(t.height for t in tiles)
    out = Image.new("RGB", (W, H), bg)
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + gap
    return out


def _col(rows, gap=8, bg=(255, 255, 255)):
    W = max(r.width for r in rows)
    H = sum(r.height + gap for r in rows)
    out = Image.new("RGB", (W, H), bg)
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height + gap
    return out


def _crop_box(frames, pad=3):
    op = np.zeros(frames[0].shape[:2], bool)
    for f in frames:
        op |= f[..., 3] > 0
    ys, xs = np.nonzero(op)
    return max(0, ys.min() - pad), min(96, ys.max() + pad + 1), max(0, xs.min() - pad), min(128, xs.max() + pad + 1)


def _out(path, default):
    os.makedirs(VIEWS, exist_ok=True)
    return path or os.path.join(VIEWS, default)


def check_frame(frame, tag, k):
    form = form_of(tag)
    ps = pieces(frame)
    share, hx, hy = head_match(frame, form)
    ha = int(halo(frame, form, hx, hy).sum()) if share >= 0.9 else -1
    below = int((frame[FEET_ROW + 1:, :, 3] > 0).sum())
    hole = int(holes(frame).sum())
    pal = set(palette().values())
    off = sum(1 for c in frame[frame[..., 3] > 0][:, :3] if tuple(int(v) for v in c) not in pal)
    return {"frame": k + 1, "pieces": [p[0] for p in ps[:5]], "head": round(share, 3), "head_xy": [hx, hy],
            "halo_px": ha, "below_feet": below, "holes": hole, "off_palette": off}


def cmd_show(a):
    frames = load(a.tag, a.src)
    if a.outlined:
        frames = [outlined(f) for f in frames]
    ks = [int(v) - 1 for v in a.frames.split(",")] if a.frames else range(len(frames))
    form = form_of(a.tag)
    sel = [frames[k] for k in ks]
    y0, y1, x0, x1 = _crop_box(sel + [design(form)])
    tiles = [_tile(design(form)[y0:y1, x0:x1], a.z, label=f"design ({form})")]
    for k in ks:
        p = pivot(a.tag, k)
        tiles.append(_tile(frames[k][y0:y1, x0:x1], a.z, label=f"{a.tag} {k + 1} ({a.src})",
                           piv=(p[0] - x0, p[1] - y0)))
    rows = [_row(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
    out = _out(a.out, f"show_{a.tag}_{a.src}.png")
    img = _col(rows)
    # the crop's origin, so coordinates read off the picture add (x0, y0)
    ImageDraw.Draw(img).text((img.width - 260, 2), f"crop origin x0={x0} y0={y0}", fill=(200, 0, 0), font=font(14))
    img.save(out)
    print(out, img.size, f"(the grid numbers are cell coordinates minus x0={x0}, y0={y0})")


def cmd_ref(a):
    k = a.frame - 1
    bt = base_tag(a.tag)
    ours = load(a.tag, a.src)[k]
    now = read_strip(os.path.join(REFS, f"now_{bt}.png"), len(cells()["tags"][bt]))[k]
    bg = (now[..., :3].astype(int) - 225).__abs__().sum(-1) == 0
    now[bg] = 0
    y0, y1, x0, x1 = _crop_box([ours, now])
    t1 = _tile(ours[y0:y1, x0:x1], a.z, label=f"ours {a.tag} {a.frame}")
    t2 = _tile(now[y0:y1, x0:x1], a.z, label=f"League {bt} {a.frame} (game size)")
    pose = Image.open(os.path.join(REFS, f"pose_{bt}.png")).convert("RGB")
    cols, rows = layout(len(cells()["tags"][bt]))
    cw, ch = 128 * Z8, 96 * Z8
    pc = pose.crop(((k % cols) * cw + x0 * Z8, (k // cols) * ch + y0 * Z8, (k % cols) * cw + x1 * Z8, (k // cols) * ch + y1 * Z8))
    pc = pc.resize((t1.width, t1.height - 20))
    t3 = Image.new("RGB", (t1.width, t1.height), (255, 255, 255))
    t3.paste(pc, (0, 20))
    ImageDraw.Draw(t3).text((4, 2), f"League render {bt} {a.frame}", fill=(0, 0, 0), font=font(14))
    out = _out(a.out, f"ref_{a.tag}_{a.frame}.png")
    _row([t1, t2, t3]).save(out)
    print(out)


def cmd_check(a):
    frames = load(a.tag, a.src)
    for k, f in enumerate(frames):
        print(json.dumps(check_frame(f, a.tag, k)))


def cmd_compare(a):
    o, w = load(a.tag, "orig"), load(a.tag, "work")
    y0, y1, x0, x1 = _crop_box(o + w)
    rows = []
    for k, (fo, fw) in enumerate(zip(o, w)):
        diff = (fo != fw).any(-1)
        rows.append(_row([_tile(fo[y0:y1, x0:x1], a.z, label=f"{a.tag} {k + 1} before"),
                          _tile(fw[y0:y1, x0:x1], a.z, label=f"after ({int(diff.sum())} px changed)"),
                          _tile(fw[y0:y1, x0:x1], a.z, mark=diff[y0:y1, x0:x1], label="changed")]))
    out = _out(a.out, f"compare_{a.tag}.png")
    _col(rows).save(out)
    print(out)


def cmd_gif(a):
    frames = load(a.tag, a.src)
    ms = durations(a.tag)
    y0, y1, x0, x1 = _crop_box(frames)
    z = a.z
    imgs = [_tile(f[y0:y1, x0:x1], z, grid=False) for f in frames]
    out = _out(a.out, f"gif_{a.tag}_{a.src}.gif")
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=ms, loop=0)
    print(out)


def cmd_design(a):
    d = design(a.form)
    y0, y1, x0, x1 = _crop_box([d])
    out = _out(a.out, f"design_{a.form}.png")
    _tile(d[y0:y1, x0:x1], a.z, label=f"design {a.form} (crop origin x0={x0} y0={y0})").save(out)
    print(out)


def cmd_legs(a):
    frames = load(a.tag, a.src)
    for k, f in enumerate(frames):
        px, py = pivot(a.tag, k)
        band = f[py + 1:py + 12].copy()
        rgb = band[..., :3].astype(int)
        red = (rgb[..., 0] > 150) & (rgb[..., 1] < 80)
        blue = (rgb[..., 2] > 200) & (rgb[..., 0] < 100)
        op = (band[..., 3] > 0) & ~red & ~blue
        fake = np.zeros(band.shape, np.uint8)
        fake[op] = 255
        desc = []
        for size, m in pieces(fake):
            if size < 6:
                continue
            ys, xs = np.nonzero(m)
            low = ys.max()
            fx = xs[ys == low]
            desc.append(f"leg x{xs.min() - px:+d}..{xs.max() - px:+d} lowest row +{low + 1} foot x{(fx.min() + fx.max()) / 2 - px:+.0f}")
        print(f"{a.tag} {k + 1}: " + " | ".join(desc))


def setup():
    """Freeze Codex's strips (as imported) in orig/ and copy the references (run once, by the orchestrator)."""
    os.makedirs(ORIG, exist_ok=True)
    os.makedirs(REFS, exist_ok=True)
    os.makedirs(VIEWS, exist_ok=True)
    nat = os.path.join(KA, "assets", "source", "native")
    for t in BASE_TAGS[1:] + ["rh_" + t for t in FORM_TAGS] + ["sh_" + t for t in FORM_TAGS]:
        shutil.copyfile(lp(os.path.join(nat, f"kayn_{t}.png")), os.path.join(ORIG, f"kayn_{t}.png"))
    shutil.copyfile(os.path.join(PACK, "kayn_idle.png"), os.path.join(REFS, "kayn_idle.png"))
    for t in BASE_TAGS:
        shutil.copyfile(os.path.join(PACK, "now", f"kayn_now_{t}.png"), os.path.join(REFS, f"now_{t}.png"))
        shutil.copyfile(os.path.join(PACK, "pose", f"lol_pose_{t}.png"), os.path.join(REFS, f"pose_{t}.png"))
    for d in os.listdir(os.path.join(PACK, "design")):
        shutil.copyfile(os.path.join(PACK, "design", d), os.path.join(REFS, d))
    print("orig/refs ready in", ROOT)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    for name in ("show", "check", "gif", "legs"):
        p = sub.add_parser(name)
        p.add_argument("tag")
        p.add_argument("--frames")
        p.add_argument("--z", type=int, default=8 if name == "show" else 4)
        p.add_argument("--src", default="work")
        p.add_argument("--out")
        p.add_argument("--outlined", action="store_true")
    p = sub.add_parser("ref")
    p.add_argument("tag")
    p.add_argument("frame", type=int)
    p.add_argument("--z", type=int, default=6)
    p.add_argument("--src", default="work")
    p.add_argument("--out")
    p = sub.add_parser("compare")
    p.add_argument("tag")
    p.add_argument("--z", type=int, default=4)
    p.add_argument("--out")
    p = sub.add_parser("design")
    p.add_argument("--form", default="base")
    p.add_argument("--z", type=int, default=10)
    p.add_argument("--out")
    sub.add_parser("setup")
    a = ap.parse_args()
    {"show": cmd_show, "ref": cmd_ref, "check": cmd_check, "compare": cmd_compare, "gif": cmd_gif,
     "design": cmd_design, "legs": cmd_legs, "setup": lambda _: setup()}[a.cmd](a)


if __name__ == "__main__":
    main()
