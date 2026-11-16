#!/usr/bin/env python3
"""Small drawn parts of a hero's League design laid on EVERY frame of its tags: the pieces the design has and the hero's
drawing lacked, added to one tag first (league_aurelionsol's four stars, added to his run by tools/art/run_body_anim.py
`add`), so they never vanish when the hero stops running, attacks, casts or dies (the user, 2026-11-16, after those runs
were approved: 「改了模型的那几个其他动作帧也要改吧 没影响吧 贾克斯 卡密尔 卑尔维斯之类的」).

    python -I tools/art/part_sprites.py --hero aurelionsol           # the hero's tags (dense, 1x, lo_) into its sheet
    python -I tools/art/part_sprites.py --check                      # every hero with a data file: exit 1 when a sheet's
                                                                     # tags are not what this makes (CI)
    python -I tools/art/part_sprites.py --hero aurelionsol --dry     # every frame's placements and clearances, nothing written
    python -I tools/art/part_sprites.py --hero aurelionsol --init [--rev REV]
                                                                     # keep the 1x frames it starts from (once, before
                                                                     # the first write: the sheet's, or at a revision)
    python -I tools/art/hero_reels.py --check                        # then: the reels read the 1x frames' outlines

Each hero's data is its own file, assets/source/<hero>/hd/<hero>_part_sprites.json:
- `sprites`: {name: {"key": {character: [r, g, b]}, "rows": [...], "one": [...], "outline": "characters"}} - a part's
  picture in the hero's own colours, `rows` of characters at the dense frames' density, `one` the same part drawn by
  hand for the 1x frames ("." nothing); `outline`: its outline's characters, kept dark in a `flash` frame. A part is
  laid on its centre square (the picture's middle row and column);
- `parts`: [{"name", "sprite", "front": true (over the drawing) / false (behind it: only where it is clear), "phase":
  steps along `path`, "wave"}] in the order they are laid (the ones behind first, then the ones in front);
- `wave` (a part): {"from": col, "to": col, "one_from": col, "one_to": col, "lag": frames} - a strip of cloth or hair
  that sways the way tools/art/run_body_anim.py moves a chain with `tip` / `tip_lag` (league_belveth's hair ribbon,
  made for her run): the picture's columns from `from` (its root, held) out to `to` (its tip) each shifted up or down
  by its share of the way out times the tag's `tip` rows for that frame (the periodic curve through them, `lag` frames
  earlier at the root end - a wave running out along it), neighbouring columns never more than a square apart; the
  columns on the root's far side stay as drawn. The 1x picture the same over `one_from`..`one_to`, the rows / PPU;
- `path`: the loop every part moves on, [rows, cols] off its place a step, and `loop_ms` a loop at the run's speed. A
  frame's step is its start in its tag: a tag of half a loop or more goes round a whole number of loops nearest its
  length (it ends where it starts, so the actions and the idle / ban-pick reels cut from them meet without a jump); a
  shorter one at `loop_ms`; `phase` (a list, a step a frame) sets them by hand. Between two steps of `path` a part is
  where the line between them puts it, rounded to whole squares (no square of a part ever changes: it only moves);
- `poses`: {name: {"ref": [tag, frame], "head": [first row, last row, first col, last col], "face": [...], "at":
  {part: [row, col]}, "still": [part, ...]}} - a drawn pose and the part's centres in its reference frame; every frame
  of the pose is found by its head (the box's squares, colour and clear alike, matched in the frame within 24 squares:
  a frame laid a few squares off, lifted a row, flashed white) and its parts moved with it, so they ride the drawing;
  a part in `still` stays on its centre (held in a hand: it does not go round the path there); `front_but`: polygons
  of (row, col) corners in the reference frame - in this pose the parts are laid in front of the drawing, but behind
  it inside the polygons (league_belveth's ribbon: over the wing she swings across where it streams, behind her head and
  the wing top it comes from);
- `tags`: {tag: {"poses": [a pose a frame], "nudge": {frame: {part: [rows, cols]}}, "sprite": {frame: {part: name}},
  "phase": [...], "flash": [frame, ...], "tip": {part: [rows a frame]}}} - a part's place moved by hand where the
  pose's own drawing is in the way (an arm turned in an in-between), or another picture of it; a waved part's tip rows
  a frame (down +; none: as drawn); in a `flash` frame (a hit's or a death's first, drawn
  flashed white by tools/art/ppu_rig.py flash) the parts are flashed the same way, so their colours are that frame's.
  Every part's colours are ones each frame already has: a colour new to a frame would change the lo_ frames' own palette
  (pixel_down.pixelate snaps every square to the frame's commonest colours), and with it squares far from the part;
- `strip`: {tag: the strip its dense frames are kept in, when not its own name} (league_aurelionsol's idle_base: the
  drawn idle, assets/source/ppu/aurelionsol_idle.png).

The dense frames the parts are laid on are the strips tools/art/ppu_hd.py reads (assets/source/ppu/<hero>_<tag>.png,
which this tool never writes: ppu_restyle.py's output, and thin_outline.py's for a hero it lists, so a later pass of
theirs is followed - and CI's --check fails until this runs again); the 1x frames are the sheet's as they were before
the parts (--init keeps them in
assets/source/<hero>/hd/<hero>_part_sprites_one.png + .json); the lo_ frames are made from the new dense frames the way
tools/art/ppu_hd.py add_lo makes them (its pixel_down.pixelate carried here in numpy, square for square the same), on
the colours of the frame before the parts (see lo_frame): a lo_ square changes only where a part reaches it. Every
frame keeps its rect: the fanim, which league.dll embeds, never changes - a part that would leave a frame is an error.
Run it after the tools that write those tags (ppu_hd.py, hero_reels.py, run_body_anim.py's run is its own) and
before hero_reels.py --check (the reels' snippets read the 1x frames' outlines). Numpy and Pillow only: CI runs --check.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402  (numpy / Pillow only: the sheet's read, the dense-hero tables)

UI_PPU = 1.5            # tools/art/ppu_hd.py UI_PPU: the lo_ frames' squares a displayed game pixel
SEARCH = 24             # squares a pose's head is looked for off its reference place


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def short(hero):
    return hero.split("_", 1)[1] if hero.startswith(("league_", "tft_")) else hero


def data_file(hero):
    return os.path.join(ROOT, "assets", "source", short(hero), "hd", f"{short(hero)}_part_sprites.json")


def one_file(hero):
    return os.path.join(ROOT, "assets", "source", short(hero), "hd", f"{short(hero)}_part_sprites_one")


def heroes_with_data():
    return sorted(os.path.basename(p)[:-len("_part_sprites.json")]
                  for p in glob.glob(os.path.join(ROOT, "assets", "source", "*", "hd", "*_part_sprites.json")))


def load(hero):
    with open(lp(data_file(hero)), encoding="utf-8") as f:
        return json.load(f)


def picture(spec, which):
    """A sprite's `rows` (dense) or `one` (1x) as RGBA."""
    rows = spec[which]
    key = {k: tuple(int(v) for v in c) for k, c in spec["key"].items()}
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            if ch not in ". ":
                a[y, x, :3] = key[ch]
                a[y, x, 3] = 255
    return a


def flashed(a, k=0.45, keep=()):
    """A picture flashed white as a hit's first frame is (tools/art/ppu_rig.py flash: its colours k of the way to white,
    so they are the flashed frame's own) - but the colours in `keep` (its outline: the frame's outer outline is laid by
    ppu_restyle.py after the flash and stays dark)."""
    out = a.copy()
    m = out[..., 3] > 0
    for c in keep:
        m &= ~(out[..., :3] == np.array(c)).all(-1)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- the frames
def rect(f):
    return tuple(int(round(f["data"][q])) for q in ("x", "y", "w", "h"))


def strip_frames(hero, tag, sizes):
    """The dense frames of `tag` from its strip (assets/source/ppu/<hero>_<tag>.png: left to right, 1 px apart)."""
    p = os.path.join(T.STRIPS, f"{short(hero)}_{tag}.png")
    if not os.path.isfile(lp(p)):
        sys.exit(f"{p}: no strip - the dense frames this tool lays its parts on")
    s = np.array(Image.open(lp(p)).convert("RGBA"))
    out, x = [], 0
    for w, h in sizes:
        if x + w > s.shape[1] or h > s.shape[0]:
            sys.exit(f"{p}: smaller than the sheet's {len(sizes)} frames - the strip is not what the sheet was made from")
        out.append(s[:h, x:x + w].copy())
        x += w + 1
    return out


def kept_ones(hero, cfg):
    """{tag: [1x frame]} as they were before the parts (<hero>_part_sprites_one.png + .json, --init)."""
    base = one_file(hero)
    if not os.path.isfile(lp(base + ".json")):
        sys.exit(f"{base}.json: none - run --init first (before the parts are written)")
    with open(lp(base + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    s = np.array(Image.open(lp(base + ".png")).convert("RGBA"))
    out, x = {}, 0
    for tag in cfg["tags"]:
        fr = []
        for w, h in meta[tag]:
            fr.append(s[:h, x:x + w].copy())
            x += w + 1
        out[tag] = fr
    return out


def init(hero, rev=None):
    """Keep the 1x frames of the data's tags (the sheet's, or at git revision `rev`) as the tool's 1x source."""
    cfg = load(hero)
    hid, pack, _, _ = T.resolve(hero, T.all_heroes())
    if rev:
        rel = os.path.relpath(T.stem(hid, pack), ROOT).replace(os.sep, "/")
        env = dict(os.environ, MSYS_NO_PATHCONV="1")
        fan = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}#anim.fanim"], capture_output=True, check=True,
                             env=env)
        png = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}#sheet.png"], capture_output=True, check=True,
                             env=env)
        import io
        anims = json.loads(fan.stdout.decode("utf-8-sig"))["anims"]
        px = np.array(Image.open(io.BytesIO(png.stdout)).convert("RGBA"))
    else:
        anims, px = T.read(hid, pack)
    frames, meta = [], {}
    for tag in cfg["tags"]:
        meta[tag] = []
        for f in anims[tag]["frames"]:
            x, y, w, h = rect(f)
            frames.append(px[y:y + h, x:x + w])
            meta[tag].append([w, h])
    H = max(a.shape[0] for a in frames)
    s = np.zeros((H, sum(a.shape[1] + 1 for a in frames) - 1, 4), np.uint8)
    x = 0
    for a in frames:
        s[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1] + 1
    base = one_file(hero)
    Image.fromarray(s, "RGBA").save(lp(base + ".png"), optimize=True)
    with open(lp(base + ".json"), "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n" + ",\n".join(f'  "{t}": {json.dumps(v)}' for t, v in meta.items()) + "\n}\n")
    print(f"{base}.png: the 1x frames of {', '.join(cfg['tags'])}" + (f" at {rev}" if rev else ""))


# ------------------------------------------------------------------------------------------------- the lo_ frames
# tools/art/ppu_hd.py add_lo with tools/art/pixel_down.py's pixelate, edge_colour, palette_of and despeckle, in numpy
# (scipy's binary erosion by the cross: every square whose four neighbours are set, outside the frame clear)
def erode4(m):
    p = np.pad(m, 1)
    return m & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]


def edge_colour(a):
    op = a[..., 3] > 0
    edge = op & ~erode4(op)
    cols, n = np.unique(a[edge][:, :3], axis=0, return_counts=True)
    return tuple(int(v) for v in cols[np.argmax(n)]) if len(n) else (0, 0, 0)


def palette_of(a, n=64):
    px = a[a[..., 3] > 0][:, :3]
    if not len(px):
        return np.zeros((1, 3))
    cols, cnt = np.unique(px, axis=0, return_counts=True)
    return cols[np.argsort(-cnt)[:n]].astype(float)


def despeckle(a):
    key = (a[..., 0].astype(np.int64) << 24) | (a[..., 1].astype(np.int64) << 16) | \
          (a[..., 2].astype(np.int64) << 8) | a[..., 3].astype(np.int64)
    p = np.pad(key, 1, constant_values=-1)
    up, dn, lf, rt = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
    m = (up == dn) & (dn == lf) & (lf == rt) & (up != key) & (up >= 0) & (a[..., 3] > 0) & \
        (a[..., :3].astype(int).sum(-1) >= 70)
    out = a.copy()
    ys, xs = np.nonzero(m)
    out[ys, xs] = a[ys - 1, xs]
    return out


def pixelate(a, k, pivot, outline, pal=None):
    H, W = a.shape[:2]
    c = 1.0 / k
    px, py = pivot
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    Wn, Hn = nx0 + nx1, ny0 + ny1
    if k > 1:
        sx = np.floor(px + (np.arange(Wn) - nx0 + 0.5) * c).astype(int)
        sy = np.floor(py + (np.arange(Hn) - ny0 + 0.5) * c).astype(int)
        out = np.zeros((Hn, Wn, 4), np.uint8)
        okx, oky = (sx >= 0) & (sx < W), (sy >= 0) & (sy < H)
        out[np.ix_(oky, okx)] = a[np.ix_(sy[oky], sx[okx])]
        return out, (nx0, ny0)
    cx = np.floor((np.arange(W) + 0.5 - px) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - py) / c).astype(int) + ny0
    cell = (cy[:, None] * Wn + cx[None, :]).ravel()
    n = Hn * Wn
    op = (a[..., 3] > 0).ravel().astype(float)
    tot = np.bincount(cell, minlength=n)
    na = np.bincount(cell, weights=op, minlength=n)
    rgb = np.stack([np.bincount(cell, weights=a[..., c_].ravel() * op, minlength=n) for c_ in range(3)], 1)
    rgb /= np.maximum(na, 1)[:, None]
    alpha = np.bincount(cell, weights=a[..., 3].ravel().astype(float), minlength=n) / np.maximum(na, 1)
    dark = np.bincount(cell, weights=((a[..., :3].astype(int).sum(-1) < 70).ravel() * op), minlength=n)
    dark = (dark / np.maximum(tot, 1)).reshape(Hn, Wn)
    keep = ((na > 0) & (na * 2 >= tot)).reshape(Hn, Wn)
    if pal is None:
        pal = palette_of(a)
    rgb = rgb.reshape(Hn, Wn, 3)
    d = ((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1)
    col = pal[np.argmin(d, -1)]
    out = np.zeros((Hn, Wn, 4), np.uint8)
    out[keep, :3] = col[keep]
    out[keep, 3] = np.clip(np.round(alpha.reshape(Hn, Wn)[keep]), 1, 255)
    edge = keep & ~erode4(keep)
    m = keep & ((dark >= 0.4) | (edge & (dark >= 0.25)))
    out[m, :3] = outline
    return despeckle(out), (nx0, ny0)


def grow(a, k, pivot):
    H, W = a.shape[:2]
    c = 1.0 / k
    px, py = pivot
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    sx = np.floor(px + (np.arange(nx0 + nx1) - nx0 + 0.5) * c).astype(int)
    sy = np.floor(py + (np.arange(ny0 + ny1) - ny0 + 0.5) * c).astype(int)
    out = np.zeros((ny0 + ny1, nx0 + nx1, 4), np.uint8)
    okx, oky = (sx >= 0) & (sx < W), (sy >= 0) & (sy < H)
    out[np.ix_(oky, okx)] = a[np.ix_(sy[oky], sx[okx])]
    return out, (nx0, ny0)


def lo_frame(b, one_wh, ppu, size, base=None):
    """A dense frame brought to the lo_ squares on the rect of round(UI_PPU x its 1x frame), grown alike at both ends
    where the drawing needs more (ppu_hd.add_lo). With `base` (the dense frame before the parts) its colours and outline
    colour are the ones snapped to: the parts change the frame's colour counts, and with them which of two colours a
    square exactly between them takes (pixel_down.palette_of orders by count) - squares of the drawing far from any part
    flipped between two cyans; with the frame's own palette only the squares the parts reach change."""
    ref = b if base is None else base
    outline = edge_colour(ref) if (ref[..., 3] > 0).any() else (0, 0, 0)
    f_ = UI_PPU * size / ppu
    if f_ > 1:
        lo, (px, py) = grow(b, f_, (b.shape[1] / 2, b.shape[0] / 2))
    else:
        lo, (px, py) = pixelate(b, f_, (b.shape[1] / 2, b.shape[0] / 2), outline, palette_of(ref))
    W, H = round(one_wh[0] * UI_PPU), round(one_wh[1] * UI_PPU)
    op = lo[..., 3] > 0
    if op.any():
        ys, xs = np.nonzero(op)
        while W / 2 < max(px - xs.min(), xs.max() + 1 - px):
            W += 2
        while H / 2 < max(py - ys.min(), ys.max() + 1 - py):
            H += 2
    f = np.zeros((H, W, 4), np.uint8)
    ox, oy = int(np.floor(W / 2 - px + 0.5)), int(np.floor(H / 2 - py + 0.5))
    if op.any():
        ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W)
        f[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return f


# ------------------------------------------------------------------------------------------------- the places
def path_at(path, p):
    """[rows, cols] at step p (a float) along the closed loop `path`, on the line between its two steps, rounded."""
    n = len(path)
    i = int(np.floor(p)) % n
    f = p - np.floor(p)
    a, b = np.array(path[i], float), np.array(path[(i + 1) % n], float)
    v = a * (1 - f) + b * f
    return int(np.floor(v[0] + 0.5)), int(np.floor(v[1] + 0.5))


def steps(cfg, tag, ms):
    """Each frame's step along the path (before the part's own phase) - see the module."""
    tc = cfg["tags"][tag]
    if tc.get("phase") is not None:
        return [float(v) for v in tc["phase"]]
    n, loop = len(cfg["path"]), float(cfg["loop_ms"])
    total = float(sum(ms))
    loops = round(total / loop)
    starts = np.cumsum([0.0] + list(ms[:-1]))
    if loops >= 1:
        return [n * loops * t / total for t in starts]
    return [n * t / loop for t in starts]


def head_shift(ref, box, a):
    """(rows, cols) the reference frame's head box lies best at in frame `a`, and the share alike: every square of the
    box counts its clear-or-not, and an opaque one its colour too (a flashed frame matches by its outline)."""
    r0, r1, c0, c1 = box
    t = ref[r0:r1 + 1, c0:c1 + 1]
    top = t[..., 3] > 0
    best = None
    H, W = a.shape[:2]
    pad = np.zeros((H + 2 * (SEARCH + t.shape[0]), W + 2 * (SEARCH + t.shape[1]), 4), np.uint8)
    oy, ox = SEARCH + t.shape[0], SEARCH + t.shape[1]
    pad[oy:oy + H, ox:ox + W] = a
    for dy in range(-SEARCH, SEARCH + 1):
        for dx in range(-SEARCH, SEARCH + 1):
            y, x = oy + r0 + dy, ox + c0 + dx
            s = pad[y:y + t.shape[0], x:x + t.shape[1]]
            sop = s[..., 3] > 0
            score = int((sop == top).sum()) + int((top & sop & (s[..., :3] == t[..., :3]).all(-1)).sum())
            key = (score, -(abs(dy) + abs(dx)))
            if best is None or key > best[0]:
                best = (key, dy, dx)
    full = top.size + int(top.sum())
    return best[1], best[2], best[0][0] / float(full)


def places(hero, cfg, dense, ms_of):
    """{tag: [{part: (centre row, centre col, sprite name)}]} and per-frame info (the head's shift and match)."""
    out, info = {}, {}
    refs = {}
    for name, ps in cfg["poses"].items():
        rt, ri = ps["ref"]
        refs[name] = dense[rt][ri]
    for tag, tc in cfg["tags"].items():
        st = steps(cfg, tag, ms_of[tag])
        rows, inf = [], []
        for i, a in enumerate(dense[tag]):
            pose = cfg["poses"][tc["poses"][i]]
            dy, dx, alike = head_shift(refs[tc["poses"][i]], pose["head"], a)
            here = {}
            for part in cfg["parts"]:
                nm = part["name"]
                if nm not in pose["at"]:
                    continue
                r, c = pose["at"][nm]
                pr, pc = (0, 0) if nm in pose.get("still", ()) else \
                    path_at(cfg["path"], st[i] + float(part.get("phase", 0)))
                nr, nc = tc.get("nudge", {}).get(str(i), {}).get(nm, (0, 0))
                sp = tc.get("sprite", {}).get(str(i), {}).get(nm, part["sprite"])
                if sp is None:
                    continue
                here[nm] = (r + dy + pr + nr, c + dx + pc + nc, sp)
            rows.append(here)
            inf.append({"pose": tc["poses"][i], "shift": (dy, dx), "alike": round(alike, 3), "step": round(st[i], 2),
                        "front_but": [[(y + dy, x + dx) for y, x in poly] for poly in pose.get("front_but", ())]})
        out[tag], info[tag] = rows, inf
    return out, info


def poly_mask(polys, shape):
    """The squares whose centres lie inside any of the polygons of (row, col) corners (run_body_anim.poly_mask)."""
    H, W = shape[:2]
    Y, X = np.mgrid[0:H, 0:W]
    y, x = Y + 0.5, X + 0.5
    out = np.zeros((H, W), bool)
    for poly in polys:
        m = np.zeros((H, W), bool)
        for k in range(len(poly)):
            (y1, x1), (y2, x2) = poly[k], poly[(k + 1) % len(poly)]
            if y1 == y2:
                continue
            m ^= ((y1 > y) != (y2 > y)) & (x < x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        out |= m
    return out


def one_mask(mask, one_shape, ppu):
    """A dense frame's mask brought to its 1x frame: each 1x square takes the dense square under its centre."""
    H, W = mask.shape
    h, w = one_shape[:2]
    ys = np.clip(np.floor((np.arange(h) + 0.5 - h / 2.0) * ppu + H / 2.0).astype(int), 0, H - 1)
    xs = np.clip(np.floor((np.arange(w) + 0.5 - w / 2.0) * ppu + W / 2.0).astype(int), 0, W - 1)
    return mask[np.ix_(ys, xs)]


def curve(vals):
    """The periodic curve through vals (one a frame): its value at any (fractional) frame (run_body_anim.curve)."""
    n = len(vals)
    X = np.fft.rfft(np.asarray(vals, float))

    def at(t):
        out = X[0].real / n
        for k in range(1, len(X)):
            w = 1.0 if (n % 2 == 0 and k == n // 2) else 2.0
            out += w / n * (X[k] * np.exp(2j * np.pi * k * t / n)).real
        return out
    return at


def wave_rows(tips, i, lag, root, tip):
    """{col: rows} of a waved part at frame i - run_body_anim's chain with `tip` / `tip_lag`: a column u of the way
    from the root out takes the tip's rows `lag` x (1 - u) frames on, times u; each never more than a square off the
    column before it."""
    cols = range(min(root, tip), max(root, tip) + 1)
    span = max(1, abs(root - tip))
    at = curve(tips) if lag else None
    d, prev = {}, 0
    for x in sorted(cols, key=lambda x: abs(root - x)):
        u = abs(root - x) / float(span)
        v = int(round((tips[i] if at is None else at(i + lag * (1.0 - u))) * u))
        v = max(prev - 1, min(prev + 1, v))
        d[x] = v
        prev = v
    return d


def waved(pic, rows):
    """`pic` with its columns shifted by `rows` ({col: rows}, down +), grown alike above and below (its centre kept)."""
    P = max([abs(v) for v in rows.values()] + [0])
    out = np.zeros((pic.shape[0] + 2 * P, pic.shape[1], 4), np.uint8)
    out[P:P + pic.shape[0]] = pic
    for x, v in rows.items():
        if v:
            out[:, x] = 0
            out[P + v:P + v + pic.shape[0], x] = pic[:, x]
    return out


def frame_pictures(cfg, tag, i, placed, pics, pics1, ppu):
    """{part: (dense picture, 1x picture)} of frame i: its sprite (flashed in a `flash` frame), waved by the tag's tips."""
    tc = cfg["tags"][tag]
    lit = i in set(tc.get("flash", ()))
    out = {}
    for part in cfg["parts"]:
        nm = part["name"]
        if nm not in placed:
            continue
        sp = placed[nm][2]
        p, p1 = pics[sp], pics1[sp]
        if lit:
            spec = cfg["sprites"][sp]
            keep = [spec["key"][ch] for ch in spec.get("outline", "")]
            p, p1 = flashed(p, keep=keep), flashed(p1, keep=keep)
        w = part.get("wave")
        tips = tc.get("tip", {}).get(nm)
        if w and tips:
            if len(tips) != len(tc["poses"]):
                sys.exit(f"{tag}: {nm} has {len(tips)} tips for {len(tc['poses'])} frames")
            lag = float(w.get("lag", 0))
            p = waved(p, wave_rows(tips, i, lag, w["from"], w["to"]))
            p1 = waved(p1, wave_rows([t / ppu for t in tips], i, lag, w["one_from"], w["one_to"]))
        out[nm] = (p, p1)
    return out


def lay(a, pics, placed, parts, where, front_but=None):
    """`a` with the parts ({part: picture}) laid on their centres (the ones behind only where it is clear; with
    `front_but`, a mask of the frame, every part in front of the drawing but behind it inside the mask) -> (frame,
    the squares each part covers or is hidden under)."""
    b = a.copy()
    body = a[..., 3] > 0
    cover = {}
    for front in (False, True):
        for part in parts:
            nm = part["name"]
            ahead = bool(part.get("front", True)) or front_but is not None
            if nm not in placed or ahead != front:
                continue
            r, c, _ = placed[nm]
            pic = pics[nm]
            top, left = r - pic.shape[0] // 2, c - pic.shape[1] // 2
            if top < 0 or left < 0 or top + pic.shape[0] > a.shape[0] or left + pic.shape[1] > a.shape[1]:
                sys.exit(f"{where}: {nm} at ({r}, {c}) leaves the {a.shape[1]}x{a.shape[0]} frame - move it in "
                         f"(the frames keep their rects)")
            m = pic[..., 3] > 0
            sub = b[top:top + pic.shape[0], left:left + pic.shape[1]]
            under = body[top:top + pic.shape[0], left:left + pic.shape[1]] & m
            put = m if front else m & (sub[..., 3] == 0)
            if front_but is not None:
                keep = front_but[top:top + pic.shape[0], left:left + pic.shape[1]]
                put = m & (~keep | (sub[..., 3] == 0))
            sub[put] = pic[put]
            cover[nm] = int(under.sum())
    return b, cover


def one_centre(r, c, hd_shape, one_shape, ppu):
    """A dense frame's square -> the 1x frame's (both about the same centre, the dense one PPU times as fine)."""
    H, W = hd_shape[:2]
    h, w = one_shape[:2]
    y = (r + 0.5 - H / 2.0) / ppu + h / 2.0 - 0.5
    x = (c + 0.5 - W / 2.0) / ppu + w / 2.0 - 0.5
    return int(np.floor(y + 0.5)), int(np.floor(x + 0.5))


def make(hero, cfg=None):
    """-> ({tag, "hd_" + tag, "lo_" + tag: [frame]}, places, info)."""
    cfg = cfg or load(hero)
    hid, pack, ppu, size = T.resolve(hero, T.all_heroes())
    anims, _ = T.read(hid, pack)
    dense, ms_of = {}, {}
    for tag in cfg["tags"]:
        sizes = [(int(round(f["data"]["w"])), int(round(f["data"]["h"]))) for f in anims["hd_" + tag]["frames"]]
        dense[tag] = strip_frames(hero, cfg.get("strip", {}).get(tag, tag), sizes)
        ms_of[tag] = [round(f["duration"] * 1000) for f in anims[tag]["frames"]]
    ones = kept_ones(hero, cfg)
    pics = {nm: picture(sp, "rows") for nm, sp in cfg["sprites"].items()}
    pics1 = {nm: picture(sp, "one") for nm, sp in cfg["sprites"].items()}
    placed, info = places(hero, cfg, dense, ms_of)
    out = {}
    for tag in cfg["tags"]:
        hd, one, lo = [], [], []
        for i, (a, a1) in enumerate(zip(dense[tag], ones[tag])):
            fp = frame_pictures(cfg, tag, i, placed[tag][i], pics, pics1, ppu)
            fb = info[tag][i]["front_but"]
            fm = poly_mask(fb, a.shape) if fb else None
            fm1 = one_mask(fm, a1.shape, ppu) if fb else None
            b, cover = lay(a, {nm: p for nm, (p, _) in fp.items()}, placed[tag][i], cfg["parts"], f"{hid} hd_{tag}[{i}]",
                           fm)
            p1 = {nm: one_centre(r, c, a.shape, a1.shape, ppu) + (sp,) for nm, (r, c, sp) in placed[tag][i].items()}
            b1, _ = lay(a1, {nm: q for nm, (_, q) in fp.items()}, p1, cfg["parts"], f"{hid} {tag}[{i}]", fm1)
            hd.append(b)
            one.append(b1)
            lo.append(lo_frame(b, (a1.shape[1], a1.shape[0]), ppu, size, a))
            info[tag][i]["cover"] = cover
            info[tag][i]["base"] = a
            info[tag][i]["pics"] = {nm: p for nm, (p, _) in fp.items()}
        out["hd_" + tag], out[tag], out["lo_" + tag] = hd, one, lo
    return out, placed, info


# ------------------------------------------------------------------------------------------------- the sheet
def differ(hero, new):
    """[tag] whose frames in the sheet are not `new`'s (a size off is an error: the frames keep their rects)."""
    hid, pack, _, _ = T.resolve(hero, T.all_heroes())
    anims, px = T.read(hid, pack)
    bad = []
    for tag, fr in new.items():
        if len(anims[tag]["frames"]) != len(fr):
            sys.exit(f"{hid} {tag}: {len(fr)} frames made, the sheet has {len(anims[tag]['frames'])}")
        for i, (f, b) in enumerate(zip(anims[tag]["frames"], fr)):
            x, y, w, h = rect(f)
            if (w, h) != (b.shape[1], b.shape[0]):
                sys.exit(f"{hid} {tag}[{i}]: made {b.shape[1]}x{b.shape[0]}, its rect is {w}x{h} - a part grew the "
                         f"frame (the fanim would change): move it in")
            if not np.array_equal(px[y:y + h, x:x + w], b):
                bad.append(tag)
                break
    return bad


def write(hero, new):
    hid, pack, _, _ = T.resolve(hero, T.all_heroes())
    differ(hero, new)                                    # (the sizes)
    anims, px = T.read(hid, pack)
    for tag, fr in new.items():
        for f, b in zip(anims[tag]["frames"], fr):
            x, y, w, h = rect(f)
            px[y:y + h, x:x + w] = b
    Image.fromarray(px, "RGBA").save(lp(T.stem(hid, pack) + "#sheet.png"), optimize=True)


def report(cfg, new, placed, info):
    """Every frame: its pose, the head's shift and match, each part's centre, the squares between it and the drawing
    (Chebyshev, 99: 8 or more; 0: touching or over it), what it covers / is hidden under, how many of its squares show
    and the distance of those from the face box."""
    for tag in cfg["tags"]:
        print(f"-- {tag}")
        for i, here in enumerate(placed[tag]):
            inf = info[tag][i]
            pose = cfg["poses"][inf["pose"]]
            dy, dx = inf["shift"]
            shown = (new["hd_" + tag][i] != inf["base"]).any(-1)
            parts = []
            for nm, (r, c, sp) in here.items():
                pic = inf["pics"][nm]
                m = pic[..., 3] > 0
                ys, xs = np.nonzero(m)
                ys, xs = ys + r - pic.shape[0] // 2, xs + c - pic.shape[1] // 2
                gap = clearance(inf["base"], ys, xs)
                vis = shown[ys, xs]
                f0, f1, g0, g1 = pose.get("face", (0, -1, 0, -1))
                fy0, fy1, fx0, fx1 = f0 + dy, f1 + dy, g0 + dx, g1 + dx
                face = min([max(fy0 - y, y - fy1, fx0 - x, x - fx1, 0) for y, x in zip(ys[vis], xs[vis])] or [-1]) \
                    if f1 >= f0 else -1
                parts.append(f"{nm} ({r},{c}) gap {gap} cover {inf['cover'].get(nm, 0)} shown {int(vis.sum())} "
                             f"face {face}")
            print(f"  [{i}] {inf['pose']} shift {inf['shift']} alike {inf['alike']} step {inf['step']}: " + "; ".join(parts))


def clearance(frame, ys, xs):
    """Clear squares between the part's squares and the drawing (the frame before the parts): Chebyshev, 0 = touching
    or over it, 99 = 8 or more."""
    op = frame[..., 3] > 0
    H, W = op.shape
    best = 99
    for y, x in zip(ys, xs):
        for d in range(0, 8):
            if op[max(0, y - d - 1):min(H, y + d + 2), max(0, x - d - 1):min(W, x + d + 2)].any():
                best = min(best, d)
                break
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--rev", help="--init: the 1x frames from the sheet at this git revision")
    a = ap.parse_args()
    if a.check and not a.hero:
        bad = []
        for h in heroes_with_data():
            new, _, _ = make(h)
            p = differ(h, new)
            print(f"{'ok' if not p else 'FAIL'}: {h}" + (f" - {', '.join(p)} not as tools/art/part_sprites.py makes them"
                                                       if p else ""))
            bad += p
        sys.exit(1 if bad else 0)
    if not a.hero:
        ap.error("--hero or --check")
    if a.init:
        init(a.hero, a.rev)
        return
    cfg = load(a.hero)
    new, placed, info = make(a.hero, cfg)
    if a.check:
        p = differ(a.hero, new)
        if p:
            sys.exit(f"{a.hero}: {', '.join(p)} not as tools/art/part_sprites.py makes them")
        print(f"ok: {a.hero}")
        return
    if a.dry:
        report(cfg, new, placed, info)
        return
    write(a.hero, new)
    print(f"{a.hero}: {', '.join(new)} written ({sum(len(v) for v in new.values())} frames, every rect kept)")


if __name__ == "__main__":
    main()
