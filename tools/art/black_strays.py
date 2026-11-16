#!/usr/bin/env python3
"""Black strays: squares of a hero's outline colour that are no part's outline, cleared from every frame - the engine of
tools/art/warwick_strays.py and tools/art/ksante_strays.py (the user, 2026-11-17: 「不对奎桑提其实还有点黑影没处理干净
武器连接着头部有黑影 狼人也没太处理干净 都重新再处理一遍」).

The rule on the dense (hd_) and 1x frames: a square of the outline colour is an outline only within a square
(chessboard) of another colour - of one that carries an outline (`own`: an effect a hero's frames have drawn into them in
colours of its own carries none) - the frame's own outline (thin_outline.json keeps one square on these heroes' dense
frames; on the 1x frames one square is one game pixel, the outline the dense frames show). Deeper, it is no part's
outline and goes, but what the hero's settings keep (`protect`: a mouth's inside, his hair). What it leaves:
- open to the ground round him (8-adjacent to the clear squares reached from the frame's edge): ground;
- shut in by his pieces: ground (`pocket` "ground": a gap between an arm and a weapon shows the ground as it does when
  the arm is away) or the hero's own colour round it (`pocket` "fill": a pocket inside his body, his fur);
- a piece of the outline colour alone (no other colour in it): ground.
The lo_ frames (the UI's: ppu_hd.add_lo grew the dense frames x UI_PPU x SIZES / PPU, nearest - every colour square of
theirs is the dense square it was grown from - and thin_outline.py left them a two-square outline) follow their dense
frame once it is clean: an outline-coloured square of theirs more than a square from every colour takes the value of the
dense square it was grown from when that one is no longer the outline colour (ground, or a filled pocket's colour) and
it lies between two parts (colour on both opposite sides within three squares: the outline ring round the figure keeps
its two squares) or is more than two squares from every colour; one whose dense square is still black (the hair, a
mouth) stays.
No other square changes; every outline square within a square of a colour stays. On the dense and lo_ frames
tools/art/thin_outline.py's pass (the hero's thin_outline.json settings) runs after the clearing, the two in turn until
neither changes anything: thin_outline.py --check finds nothing after this, and this tool's --check nothing after
thin_outline.py.

The frames: the sheet's own tags (the run tags are tools/art/run_body_anim.py's, the reels rects of these frames), the
dense strips tools/art/ppu_hd.py reads (assets/source/ppu/<hero>_<tag>.png, each its sheet frame) and the run's own
sources the hero names (the drawn run, its kept 1x / lo_ frames) - run_body_anim.py --hero <hero> lays those in after
this. CI runs the heroes' --check with python -I: numpy and PIL only.
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

RUN = ("run", "hd_run", "lo_run")
REELS = ("idle", "bp", "hd_idle", "hd_bp", "lo_idle", "lo_bp")
KEEP = {"hd": 1, "one": 1, "lo": 2}
UI_PPU = 1.5                    # ppu_hd.UI_PPU (ppu_hd.py needs scipy: CI runs this without it)
BETWEEN = 3                     # a lo_ square between two parts: colour on both opposite sides within this many


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# ------------------------------------------------------------------------------------------------- geometry
def dil8(m, n=1):
    """m grown by n squares (8-neighbours)."""
    m = m.copy()
    for _ in range(n):
        p = np.pad(m, 1)
        g = np.zeros_like(m)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                g |= p[dy:dy + m.shape[0], dx:dx + m.shape[1]]
        m = g
    return m


def label(m, eight=True):
    """(labels, count) of m's 8- (or 4-) connected pieces (numpy only: CI runs python -I without scipy)."""
    H, W = m.shape
    lab = np.zeros((H, W), np.int32)
    steps = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx] if eight else \
        [(-1, 0), (1, 0), (0, -1), (0, 1)]
    n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        stack = [(y0, x0)]
        while stack:
            y, x = stack.pop()
            for dy, dx in steps:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    stack.append((yy, xx))
    return lab, n


def reach4(src, through):
    """The squares of `through` 4-connected (through `through`) to a `src` square."""
    out = np.zeros_like(through)
    front = src.copy()
    while True:
        p = np.pad(front | out, 1)
        g = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & through & ~out
        if not g.any():
            return out
        out |= g
        front = g


def exterior(clear):
    """The clear squares reached from the frame's edge (4-neighbours): the ground round him."""
    edge = np.zeros_like(clear)
    edge[0], edge[-1], edge[:, 0], edge[:, -1] = clear[0], clear[-1], clear[:, 0], clear[:, -1]
    return edge | reach4(edge, clear)


def steps8(src, through, cap=99):
    """8-neighbour steps through `through` from the nearest `src` square (cap + 1 where farther or never reached)."""
    d = np.full(src.shape, cap + 1, np.int32)
    d[src] = 0
    front = src.copy()
    for step in range(1, cap + 1):
        new = dil8(front) & through & (d > cap)
        if not new.any():
            break
        d[new] = step
        front = new
    return d


def colour_mask(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == np.array(c)).all(-1)
    return m & (a[..., 3] > 0)


def grow_src(hshape, lshape, k):
    """lo_ square -> the dense square ppu_hd.add_lo grew it from (ppu_hd.grow about the frame's centre, nearest, centred on
    the lo_ rect): (row per lo_ row, column per lo_ column), -1 where none (as ksante_eyes.grow_src)."""
    H, W = hshape
    c = 1.0 / k
    px, py = W / 2, H / 2
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    sx = np.floor(px + (np.arange(nx0 + nx1) - nx0 + 0.5) * c).astype(int)
    sy = np.floor(py + (np.arange(ny0 + ny1) - ny0 + 0.5) * c).astype(int)
    LH, LW = lshape
    ox, oy = int(np.floor(LW / 2 - nx0 + 0.5)), int(np.floor(LH / 2 - ny0 + 0.5))
    ry, rx = np.full(LH, -1), np.full(LW, -1)
    for i, s in enumerate(sy):
        if 0 <= i + oy < LH and 0 <= s < H:
            ry[i + oy] = s
    for i, s in enumerate(sx):
        if 0 <= i + ox < LW and 0 <= s < W:
            rx[i + ox] = s
    return ry, rx


def grown(dense, lshape, k):
    """The dense frame's squares under each square of its lo_ frame (clear where none)."""
    ry, rx = grow_src(dense.shape[:2], lshape, k)
    out = np.zeros(lshape + (4,), np.uint8)
    oy, ox = ry >= 0, rx >= 0
    out[np.ix_(oy, ox)] = dense[np.ix_(ry[oy], rx[ox])]
    return out


# ------------------------------------------------------------------------------------------------- the rule
def deep_of(a, ink, keep, own=None):
    """-> (outline-coloured squares, other colours, outline squares more than `keep` from every colour that carries an
    outline). own(frame, colours) -> the colours that do (all of them by default: an effect drawn into a hero's frames
    in colours of its own, never outlined, carries none)."""
    op = a[..., 3] > 0
    out = op & (a[..., :3] == np.array(ink)).all(-1)
    col = op & ~out
    body = col if own is None else own(a, col)
    return out, col, out & ~dil8(body, keep)


def alone_of(a, col):
    """The opaque 8-connected pieces holding no other colour."""
    lab, n = label(a[..., 3] > 0)
    alone = np.zeros(col.shape, bool)
    for j in range(1, n + 1):
        b = lab == j
        if not (b & col).any():
            alone |= b
    return alone


def strays_of(a, hero, kind, ctx):
    """The squares the rule takes (before thin_outline's pass): the verification map - empty on a clean frame.
    ctx: the hero's (protect's) on the dense and 1x frames; on a lo_ frame, its clean dense frame grown onto it."""
    out, col, deep = deep_of(a, hero.ink, KEEP[kind], hero.own)
    alone = alone_of(a, col)
    if kind == "lo":
        body = hero.own(a, col)
        mirror = out & ~dil8(body, 1) & (T.between(body, BETWEEN) | deep)
        return (mirror | alone) & ~colour_mask(ctx, [hero.ink])
    return (deep | alone) & ~hero.protect(a, kind, ctx)


def clear_once(a, hero, kind, ctx):
    """One pass of the rule -> frame."""
    st = strays_of(a, hero, kind, ctx)
    if not st.any():
        return a
    b = a.copy()
    if kind == "lo":
        b[st] = ctx[st]
        b[st & (ctx[..., 3] == 0)] = 0
        return b
    op = a[..., 3] > 0
    ground = dil8(exterior(~op))
    lab, n = label(st)
    for j in range(1, n + 1):
        m = lab == j
        if hero.pocket == "ground" or (m & ground).any():
            b[m] = 0
        else:
            b[m, :3] = hero.fill_colour(a, m)
            b[m, 3] = 255
    return b


def clean(a, hero, kind, ctx=None, rounds=8):
    """The rule until it changes nothing (thin_outline's pass between on the dense and lo_ frames) -> (frame, cleared:
    outline squares left as ground, filled: squares painted another colour)."""
    cur = a
    for _ in range(rounds):
        nxt = clear_once(cur, hero, kind, ctx)
        if kind in ("hd", "lo") and hero.thin is not None:
            nxt = T.change_fixed(nxt, hero.thin[kind], hero.thin["outline"], hero.thin["grow"])[0]
        if (nxt == cur).all():
            break
        cur = nxt
    else:
        raise RuntimeError(f"{hero.id}: no fixed point")
    changed = (cur != a).any(-1)
    return cur, changed & (cur[..., 3] == 0), changed & (cur[..., 3] > 0)


# ------------------------------------------------------------------------------------------------- the frames
def kind_of(tag):
    return "lo" if tag.startswith("lo_") else "hd" if tag.startswith("hd_") else "one"


def plain(tag):
    return tag[3:] if tag.startswith(("hd_", "lo_")) else tag


def rect(fr):
    return tuple(int(round(fr["data"][q])) for q in ("x", "y", "w", "h"))


def sheet_frames(anims):
    """[(tag, index, (x, y, w, h), kind)]: every frame of the sheet's own tags, each rect once, the dense and 1x ones
    first (a lo_ frame follows its clean dense frame); the run tags and the reels left out (run_body_anim.py's, and
    rects of these)."""
    out, seen = [], set()
    for tag, an in anims.items():
        if tag in RUN or tag in REELS:
            continue
        for i, fr in enumerate(an["frames"]):
            r = rect(fr)
            if r not in seen:
                seen.add(r)
                out.append((tag, i, r, kind_of(tag)))
    return sorted(out, key=lambda t: t[3] == "lo")


def strips(short):
    """[(path, tag, sizes)] of the hero's dense strips (assets/source/ppu/<short>_<tag>.png), the run's left out (the
    drawn run's, run_body_anim.py writes it)."""
    out = []
    for path in sorted(glob.glob(os.path.join(T.STRIPS, f"{short}_*.png"))):
        tag = os.path.basename(path)[len(short) + 1:-4]
        if "." in tag or tag == "run" or not os.path.exists(lp(path[:-4] + ".json")):
            continue
        with open(lp(path[:-4] + ".json"), encoding="utf-8") as f:
            out.append((path, tag, json.load(f)["sizes"]))
    return out


def frames_of(sizes):
    out, x = [], 0
    for w, h in sizes:
        out.append((x, w, h))
        x += w + 1
    return out


class Hero:
    """A hero's settings. ink: the outline colour; protect(frame, kind, ctx) -> the deep outline squares kept;
    ctx(tag, frame, kind) -> what protect needs on a dense / 1x frame; pocket: "ground", or "fill" with
    fill_colour(frame, pocket) -> colour; run_sources() -> [(path, sizes, kind, tag for a dense / 1x source or, for a
    lo_ one, the index of each frame's frame in the dense source before it)]."""
    ink = None
    pocket = "ground"

    def __init__(self, hid):
        self.id = hid
        self.short = hid.split("_", 1)[1]
        _, self.pack, ppu, size = T.resolve(hid, T.all_heroes())
        self.grow = UI_PPU * size / ppu                 # ppu_hd.add_lo's factor
        if self.grow <= 1:
            sys.exit(f"{hid}: lo_ frames averaged down (UI_PPU x size / PPU = {self.grow:.3f}), not grown - the lo_ "
                     "rule no longer holds")
        st = T.load_state().get(hid)
        self.thin = st if st and not st.get("skip") else None

    def ctx(self, tag, f, kind):
        return None

    def own(self, a, col):
        """The colour squares that carry an outline (all of them, unless the hero draws effects into his frames)."""
        return col

    def protect(self, a, kind, ctx):
        return np.zeros(a.shape[:2], bool)

    def fill_colour(self, a, pocket):
        raise NotImplementedError

    def run_sources(self):
        return []


def run(hero, check, review=None):
    """Clean (or --check, or --review DIR) every frame of the hero."""
    an, px = T.read(hero.id, hero.pack)
    px2 = px.copy()
    bad, log, pics = [], [], []
    dense = {}

    def one(name, f, kind, ctx, keep_pic=True):
        b, c, fl = clean(f, hero, kind, ctx)
        if (c | fl).any():
            log.append(f"{name}: {int(c.sum())} cleared, {int(fl.sum())} filled")
            if keep_pic:
                pics.append((name, f, c, fl, b))
        return b
    for tag, i, (x, y, w, h), kind in sheet_frames(an):
        f = px[y:y + h, x:x + w]
        if kind == "lo":
            r = rect(an["hd_" + plain(tag)]["frames"][i])
            ctx = grown(px2[r[1]:r[1] + r[3], r[0]:r[0] + r[2]], (h, w), hero.grow)
        else:
            ctx = hero.ctx(tag, f, kind)
        px2[y:y + h, x:x + w] = one(f"{tag} {i}", f, kind, ctx)
    changed = int((px2 != px).any(-1).sum())
    if changed:
        bad.append(f"sheet: {changed} squares")
    sources = [(path, frames_of(sizes), "hd", "hd_" + tag) for path, tag, sizes in strips(hero.short)]
    sources += [(path, frames_of(sizes), kind, ref) for path, sizes, kind, ref in hero.run_sources()]
    last_dense = []
    for path, fr, kind, ref in sources:
        s = np.array(Image.open(lp(path)).convert("RGBA"))
        s2 = s.copy()
        is_strip = os.path.dirname(os.path.abspath(path)) == os.path.abspath(T.STRIPS)
        for k, (x, w, h) in enumerate(fr):
            f = s[:h, x:x + w]
            if kind == "lo":
                ctx = grown(last_dense[ref[k]], (h, w), hero.grow)
            else:
                ctx = hero.ctx(ref, f, kind)
            s2[:h, x:x + w] = one(f"{os.path.basename(path)[:-4]} {k}", f, kind, ctx, not is_strip)
        if kind == "hd":
            last_dense = [s2[:h, x:x + w] for x, w, h in fr]
        n = int((s2 != s).any(-1).sum())
        if n:
            bad.append(f"{os.path.relpath(path, ROOT)}: {n} squares")
            if not check and review is None:
                Image.fromarray(s2, "RGBA").save(lp(path), optimize=True)
    if review is not None:
        write_review(review, hero.short, pics, log)
        print(f"{hero.id}: {len(pics)} frames would change - {review}")
        return
    if check:
        if bad:
            print("\n".join(bad))
            sys.exit(f"{hero.id}: black strays left - run tools/art/{hero.short}_strays.py, then "
                     f"tools/art/run_body_anim.py --hero {hero.short}")
        print(f"ok: {hero.id} holds no black strays")
        return
    if changed:
        Image.fromarray(px2, "RGBA").save(lp(T.stem(hero.id, hero.pack) + "#sheet.png"), optimize=True)
    print(f"{hero.id}: " + ("; ".join(bad) if bad else "nothing to change"))


def write_review(out_dir, short, pics, log):
    """Each changed frame: before / cleared (magenta) and filled (cyan) / after, x5."""
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{short}_strays.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    S, BG = 5, (232, 230, 222)

    def show(a, c=None, fl=None):
        img = np.zeros(a.shape[:2] + (3,), np.uint8)
        img[:] = BG
        op = a[..., 3] > 0
        img[op] = a[op][:, :3]
        if c is not None:
            img[c] = (255, 0, 220)
            img[fl] = (0, 220, 220)
        return np.repeat(np.repeat(img, S, 0), S, 1)
    for k in range(0, len(pics), 6):
        part = pics[k:k + 6]
        cells = []
        for name, a, c, fl, b in part:
            gap = np.full((a.shape[0] * S, 4, 3), 30, np.uint8)
            cells.append((f"{name}: {int(c.sum())} cleared, {int(fl.sum())} filled",
                          np.concatenate([show(a), gap, show(a, c, fl), gap, show(b)], 1)))
        W = max(c.shape[1] for _, c in cells)
        H = sum(c.shape[0] + 18 for _, c in cells)
        sheet = Image.new("RGB", (W, H), (20, 20, 20))
        dr = ImageDraw.Draw(sheet)
        y = 0
        for name, c in cells:
            dr.text((2, y + 2), name, fill=(255, 255, 0))
            sheet.paste(Image.fromarray(c), (0, y + 16))
            y += c.shape[0] + 18
        sheet.save(os.path.join(out_dir, f"{short}_strays_{k // 6:02d}.png"))
