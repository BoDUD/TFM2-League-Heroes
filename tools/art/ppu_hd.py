#!/usr/bin/env python3
"""High-density (PPU) frames inside a hero's own sheet: `hd_<tag>` next to every `<tag>`.

The user, 2026-10-12: 「PPU 可以先改一版亚索试试」「这个要装进主包里 不是附加包」. The main pack's DLL (addons/league_main,
league.dll) swaps a registered hero's playing animation `<tag>` for `hd_<tag>` on the battlefield and sets the display
entity's draw scale (+0x1b4) to its base / PPU, so a frame drawn PPU times denser shows at the same size, its squares
PPU times finer. The hd tags sit in the hero's own sheet the way Kayn's form tags do (`rh_idle` ...: the anim-name swap
proven on game 0.6.3); the cards, the encyclopedia and the face icons draw `idle` and stay 1x. Without the hook (another
game version, the DLL not loaded) nothing plays the hd tags: the 1x hero as before.

    python tools/art/ppu_hd.py                 # every hero in PPU: rewrite its hd_ tags
    python tools/art/ppu_hd.py --hero yasuo --check
    python tools/art/ppu_hd.py --hero yasuo --review dist/ppu_review

A frame is centred on its pivot (odd 1x sizes), so the hd frame is exactly PPU x the 1x frame (the same centre). Its
pixels: `assets/source/ppu/<hero>_<tag>.png` (a strip of the hd frames, PPU x each 1x frame, left to right with 1 px
gaps) when drawn, else the 1x frame scaled by PPU (nearest: every 1x pixel a whole PPU x PPU block, none lost), with
the hero's HEAD pasted in where the frame carries the idle's head.

HEAD: a finer head drawn by an image model (Yasuo's: 「你有PPU后 直接搬运帅气的脸不就行了吗」, Codex's 2026-09-27 picture
assets/source/ppu/yasuo_codex.png read back on its own 8-px grid - 68 x 60 squares, head 18 rows against the 1x
sprite's 12). Every one of its squares becomes `scale` x `scale` hd pixels - no square dropped or doubled
(「像素不要缺失」) - which is why Yasuo's PPU is 3: his body x3, the picture's squares x2, the head the 1x head's size.
It goes wherever the 1x frame holds the idle's first-frame head pixel for pixel (`box`: the 1x head; armour grey and
scarf blue are not head), at `at` (its top-left in the idle's first hd frame) moved by that frame's offset. The old
head is NOT cleared first (cleared, the gap behind the new head showed the ground: 「像素缺失了啊」): only its pixels
standing above or in front of the new head go, never on the scarf rows (from `keep_row` down), then the outline is
closed. The new head sits one 1x pixel further back than the old one (its back edge on the old back edge: 「自然一点行吧」,
the old cheek showed behind it); pixels of the `on_top` colours (the ponytail's tie, as in the idle) round the head
are drawn over it again.
tools/art/import_native.py calls add_hd() for the heroes listed here after writing their sheets.
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
MOD = os.path.join(ROOT, "league")
# heroes of another pack in this repo (the tft pack, mod_id tft: Teamfight Tactics' own units): hero -> the pack's
# folder and id prefix; every other hero is league_<hero> in league/
PACKS = {"powder": "tft"}


def hero_id(hero):
    return f"{PACKS.get(hero, 'league')}_{hero}"


def mod_dir(hero):
    return os.path.join(ROOT, PACKS.get(hero, "league"))


def stem_of(hero):
    """The hero's sheet without #sheet.png / #anim.fanim."""
    return os.path.join(mod_dir(hero), "champions", hero_id(hero))
SRC = os.path.join(ROOT, "assets", "source", "ppu")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

# hero -> pixels per 1x square; the DLL's table (addons/league_main/src/hd.rs) must list the same. 2026-10-13: every
# hero but zeri / irelia brought to about 2.2 squares a game pixel by tools/art/ppu_restyle.py (RESTYLE there)
# gragas, zeri, irelia: dense strips drawn by tools/art/ppu_gragas.py, ppu_zeri.py, ppu_irelia.py; kassadin: posed from
# his PPU design by tools/art/rig_kassadin.py (134 design rows / 37 game rows); vladimir, karma, ashe,
# yasuo: Codex's strips read back by tools/art/import_ppu_strips.py; corki: tools/art/rig_corki_hd.py; braum: Codex's
# strips (tools/art/import_braum_strips.py) brought to the sheets by tools/art/rig_braum.py, 121 rows / 42 (all in assets/source/ppu)
PPU = {"yasuo": 2.2, "gragas": 1.45, "zeri": 3, "vladimir": 1.8, "karma": 2.2, "ashe": 2.2, "irelia": 2, "kassadin": 2.42, "corki": 2.2, "garen": 1.9, "braum": 1.98, "mordekaiser": 2.0, "soraka": 2.2, "nidalee": 2.2, "galio": 1.65, "nilah": 1.98, "kindred": 2.2, "malzahar": 1.38, "smolder": 1.5, "milio": 2.2, "jayce": 1.5, "elise": 1.8, "katarina": 1.5, "tahmkench": 1.2, "kalista": 1.4, "drmundo": 1.5, "pantheon": 1.5, "orianna": 2.2, "aphelios": 1.5, "rell": 1.5, "reksai": 1.2, "urgot": 1.2, "morgana": 1.5, "nami": 1.5, "janna": 1.5, "jax": 1.5, "xinzhao": 1.5, "kaisa": 1.45, "camille": 1.5, "fiora": 1.5, "leblanc": 2.0, "darius": 1.45, "yunara": 1.5, "swain": 1.5, "nasus": 1.2, "renata": 1.5, "anivia": 1.2, "jarvaniv": 1.5, "ziggs": 1.2, "maokai": 1.3, "gangplank": 1.5, "wukong": 1.2, "cassiopeia": 1.2, "akshan": 1.2, "poppy": 1.2, "volibear": 1.2, "rammus": 1.2, "zoe": 1.5, "quinn": 2.0, "riven": 1.5, "yuumi": 1.5, "powder": 1.75, "chogath": 1.2, "karthus": 1.5, "vex": 1.5, "zyra": 1.7, "graves": 1.5, "warwick": 1.2, "gnar": 1.5, "sylas": 1.2, "mel": 1.5, "velkoz": 1.5, "ornn": 1.5}
PREFIX = "hd_"
# lo_<tag>: the same frames at UI_PPU squares a displayed game pixel - what the BP grid, the encyclopedia, the pick
# slots and the pick moment draw (league.dll's UI table; the user, 2026-10-13: 「BP界面里看英雄还是太清晰」, picked the
# 1.5 row of the preview); made from the hd_ frames here, never drawn by hand
LO = "lo_"
UI_PPU = 1.5


def plain(tag):
    """A tag of the 1x animations (not an hd_ / lo_ copy)."""
    return not tag.startswith((PREFIX, LO))
# hero -> dense px every dense frame is drawn lower (a hero shown smaller on the battlefield, league_main hd.rs SIZES:
# the soles stay on the ground; tools/art/ppu_gragas.py SHIFT) - the checks compare against the 1x frame moved as much
SHIFT = {"gragas": 6, "braum": 4}  # braum: tools/art/rig_braum.py SIZE / SHIFT
# heroes whose dense frames are a new drawing, not the 1x art (league_zeri: Codex's pictures read at 111 rows): the
# checks against the 1x frame scaled do not apply to them (tools/art/ppu_zeri.py checks its frames)
REDRAWN = {"zeri"}


def up1(hero, a):
    """A 1x frame doubled to its dense size and moved down as the hero's dense frames are."""
    b = up(a, PPU[hero])
    k = SHIFT.get(hero, 0)
    if k:
        m = np.zeros_like(b)
        m[k:] = b[:-k]
        b = m
    return b
HEAD = {
    "yasuo": {"src": "yasuo_head.png", "scale": 2, "at": (75, 30), "box": (8, 22, 24, 37), "keep_row": 20,
              "on_top": [(25, 10), (25, 11)], "face_box": (13, 21, 28, 36), "tolerance": 30,
              # the 1x head's colours: its outline, hair and skin (a sleeve or a blade in the box is not the head)
              "line": (20, 19, 25), "hair_cols": [(43, 26, 31), (74, 42, 48), (107, 60, 63)],
              "skin_cols": [(232, 185, 140), (201, 142, 95)], "hair": [46, 23, 29],
              # frames whose face is drawn too differently to be found (turned, bowed, lying): (dx, dy, flip) by eye;
              # flip "v" pastes into the frame turned upside down (he lies on his back) and turns it back
              "place": {("attack", 1): (-15, 9, None), ("q3", 6): (-3, 22, None), ("dead", 2): (-2, 3, None), ("dead", 3): (-5, 2, None), ("dead", 5): (-11, -9, "v"),
                        ("dead", 6): (-8, -9, "v")}},
}


def read_sheet(stem):
    """stem#sheet.png + stem#anim.fanim -> {tag: [(frame array, ms), ...]} in the fanim's order."""
    px = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        fr = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000, 3)))
        out[tag] = fr
    return out


def up(a, k):
    if k != int(k):
        return scale_any(a, k)
    k = int(k)
    return np.repeat(np.repeat(a, k, axis=0), k, axis=1)


def scale_any(a, k):
    """`a` scaled to round(k x its size), every pixel the source pixel under its centre (any k > 0)."""
    h, w = a.shape[:2]
    H, W = max(1, round(h * k)), max(1, round(w * k))
    ys = np.minimum(((np.arange(H) + 0.5) / k).astype(int), h - 1)
    xs = np.minimum(((np.arange(W) + 0.5) / k).astype(int), w - 1)
    return a[ys][:, xs]


def is_drawn(hero, tag):
    return os.path.isfile(os.path.join(SRC, f"{hero}_{tag}.png"))


def hd_size(w, h, k):
    return round(w * k), round(h * k)


def head_pixel(p):
    """Hair, skin, eyes and outline - not the armour's grey nor the scarf's blue."""
    r, g, b, a = (int(v) for v in p)
    if a == 0:
        return False
    if b > r + 30 and b > 120:
        return False
    return not (abs(r - g) < 20 and abs(g - b) < 25 and r > 90)


def head_mask(a, box):
    y0, y1, x0, x1 = box
    m = np.zeros(a.shape[:2], bool)
    for y in range(y0, min(y1, a.shape[0])):
        for x in range(x0, min(x1, a.shape[1])):
            m[y, x] = head_pixel(a[y, x])
    return m


def find_head(frame, tpl, tmask):
    """Where `frame` (or its mirror) holds the template's pixels best: (wrong pixels, dx, dy, mirrored)."""
    ys, xs = np.nonzero(tmask)
    want = tpl[ys, xs].astype(int)
    best = None
    for flip in (False, True):
        f = (frame[:, ::-1] if flip else frame).astype(int)
        H, W = f.shape[:2]
        for dy in range(-ys.min(), H - ys.max()):
            for dx in range(-xs.min(), W - xs.max()):
                bad = int((np.abs(f[ys + dy, xs + dx] - want).max(axis=1) > 0).sum())
                if best is None or bad < best[0]:
                    best = (bad, dx, dy, flip)
    return best


def old_head(frame, spec, dx, dy):
    """The 1x pixels of this frame's own head: the idle's head where the face matched, the pixels of the idle head's
    colours joined to it inside the head's box (a hand of skin colour beyond a sleeve is not), and the outline pixels
    that border nothing else (an arm's or a blade's outline does)."""
    H, W = frame.shape[:2]
    col = lambda y, x: tuple(int(v) for v in frame[y, x][:3])
    pal, line, tie = spec["palette"], spec["line"], spec["tie_cols"]
    y0, y1, x0, x1 = spec["box"]
    inbox = np.zeros((H, W), bool)
    inbox[max(0, y0 + dy):max(0, y1 + dy), max(0, x0 + dx):max(0, x1 + dx)] = True
    colour = np.array([[frame[y, x, 3] > 0 and col(y, x) in pal for x in range(W)] for y in range(H)]) & inbox
    region = np.zeros((H, W), bool)
    ry, rx = np.nonzero(spec["region"])
    ry, rx = ry + dy, rx + dx
    ok = (ry >= 0) & (rx >= 0) & (ry < H) & (rx < W)
    region[ry[ok], rx[ok]] = True
    lab, _ = ndimage.label(colour)
    out = np.isin(lab, [v for v in np.unique(lab[region & colour]) if v])
    for y, x in zip(*np.nonzero(inbox)):
        if frame[y, x, 3] == 0 or col(y, x) != line:
            continue
        nb = [(y + a, x + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= y + a < H and 0 <= x + b < W]
        out[y, x] = any(out[q] for q in nb) and all(
            frame[q][3] == 0 or out[q] or col(*q) in {line} | tie for q in nb)
    return out


def paste_head(hero, frame, k, offset):
    """frame x k with the hero's HEAD at `offset` (1x pixels from the idle's first frame)."""
    spec = HEAD[hero]
    hd = up(frame, k)
    head = up(np.asarray(Image.open(os.path.join(SRC, spec["src"])).convert("RGBA")), spec["scale"])
    dx, dy = offset
    X0, Y0 = spec["at"][0] + k * dx, spec["at"][1] + k * dy
    hh, hw = head.shape[:2]
    if X0 < 0 or Y0 < 0 or Y0 + hh > hd.shape[0] or X0 + hw > hd.shape[1]:
        return None                              # it would leave the frame: this frame keeps its own head
    new = np.zeros_like(hd)
    new[Y0:Y0 + hh, X0:X0 + hw] = head
    nm = new[..., 3] > 0
    mine = old_head(frame, spec, dx, dy)
    keep_row = spec["keep_row"] + dy
    # something in front of the face that is not the head (a hand, a blade, a sleeve) stays in front of the new one:
    # what reaches into the new head's box from its right or top side (a shoulder or the scarf come from below / behind)
    ys_, xs_ = np.nonzero(nm)
    by0, by1, bx0, bx1 = ys_.min(), ys_.max() + 1, xs_.min(), xs_.max() + 1
    cx = (bx0 + bx1) // 2
    # (its own colours only: an outline runs on along the old head and would carry the old head's edge with it)
    lines = np.array([[tuple(int(v) for v in p[:3]) in {spec["line"]} | spec["tie_cols"] for p in row] for row in frame])
    other = (hd[..., 3] > 0) & ~up(mine | lines, k)
    other[k * keep_row:] = False
    lab, _ = ndimage.label(other[by0:by1, bx0:bx1])
    reach = set(lab[:, -1][lab[:, -1] > 0]) | set(lab[0, cx - bx0:][lab[0, cx - bx0:] > 0])
    covered = np.zeros_like(nm)
    if reach:
        covered[by0:by1, bx0:bx1] = np.isin(lab, list(reach))
    out = hd.copy()
    out[nm & ~covered] = new[nm & ~covered]
    # Round the new head, whole 1x pixels: the old head's pixels and any outline pixel in the head's box go unless
    # they are behind it (its back half: there they fill what the new head leaves, as hair - no gap, no cheek);
    # an outline pixel an arm or a blade needs (next to it, clear of the new head) comes back.
    left = np.full(nm.shape[0], -1)
    right = np.full(nm.shape[0], -1)
    for y in range(by0, by1):
        if nm[y].any():
            xs = np.nonzero(nm[y])[0]
            left[y], right[y] = xs.min(), xs.max()
    y0, y1, x0, x1 = spec["box"]
    H, W = frame.shape[:2]
    cleared = []
    near = ndimage.binary_dilation(nm, structure=np.ones((3, 3)))
    hair = np.array(spec["hair"] + [255], np.uint8)
    # the ponytail's root: from a tie above the new head down to it the old pixels stay (the tie never floats)
    root = np.zeros((H, W), bool)
    tie_px = [(y, x) for y in range(max(0, y0 + dy - 4), min(H, y1 + dy)) for x in range(max(0, x0 + dx - 4), min(W, x1 + dx))
              if frame[y, x, 3] and tuple(int(v) for v in frame[y, x][:3]) in spec["tie_cols"]]
    for ty, tx in tie_px:
        for x in range(tx - 1, tx + 2):
            if 0 <= x < W and nm[:, k * x:k * x + k].any():
                head_top = np.nonzero(nm[:, k * x:k * x + k].any(axis=1))[0].min() // k
                if ty < head_top:
                    root[max(0, ty - 3):head_top + 1, x] = True
    for y in range(max(0, y0 + dy - 2), min(H, max(keep_row, (by1 + k - 1) // k))):
        for x in range(max(0, x0 + dx - 2), min(W, x1 + dx + 2)):
            if frame[y, x, 3] == 0 or not (mine[y, x] or lines[y, x]) or root[y, x]:
                continue
            block = (slice(k * y, k * y + k), slice(k * x, k * x + k))
            if nm[block].all():
                continue
            Y, X = k * y + k // 2, k * x + k // 2
            mid = (left[Y] + right[Y]) / 2 if left[Y] >= 0 else (bx0 + (bx1 - bx0) / 3)
            sub = out[block]
            if y >= keep_row:
                # on the scarf's rows only the old face's own edge in front of the new head goes (a chin's outline
                # ending in the air); what borders the scarf or an arm stays
                nb = [(y + a, x + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= y + a < H and 0 <= x + b < W]
                if X < mid or Y < by0 or not all(frame[q][3] == 0 or mine[q] or lines[q] for q in nb):
                    continue
                sub[~nm[block]] = 0
                cleared.append((y, x))
                continue
            if X < mid and Y >= by0:
                if mine[y, x] and tuple(int(v) for v in frame[y, x][:3]) not in {spec["line"]} | spec["tie_cols"]:
                    sub[~nm[block]] = hair          # behind the new head: its hair
                continue
            sub[~nm[block]] = 0
            cleared.append((y, x))
    objects = (frame[..., 3] > 0) & ~mine & ~lines
    for y, x in cleared:
        if not lines[y, x] or near[k * y:k * y + k, k * x:k * x + k].any():
            continue
        if any(0 <= y + a < H and 0 <= x + b < W and objects[y + a, x + b] and out[k * (y + a), k * (x + b), 3]
               for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[k * y:k * y + k, k * x:k * x + k] = frame[y, x]
    # the new head's own outline where hair lies outside it (behind: the old head's hair) is hair: no seam in the hair
    hairs = {tuple(int(v) for v in c) for c in spec["hair_cols"]} | {tuple(spec["hair"])}
    sc = spec["scale"]
    for Y in range(Y0, Y0 + hh, sc):
        for X in range(X0, X0 + hw, sc):
            blk = (slice(Y, Y + sc), slice(X, X + sc))
            if not nm[blk].all() or tuple(int(v) for v in out[Y, X][:3]) != spec["line"]:
                continue
            outside = [(Y + a, X + b) for a, b in ((-1, 0), (sc, 0), (0, -1), (0, sc))
                       if 0 <= Y + a < out.shape[0] and 0 <= X + b < out.shape[1] and not nm[Y + a, X + b]]
            if outside and all(out[q][3] > 0 and tuple(int(v) for v in out[q][:3]) in hairs for q in outside):
                out[blk] = np.array(spec["hair"] + [255], np.uint8)
    # the tie's colours (the idle's `on_top` pixels) round the head stay in front of it
    y0, y1, x0, x1 = spec["box"]
    for Y in range(max(0, y0 + dy - 4), min(frame.shape[0], y1 + dy)):
        for X in range(max(0, x0 + dx - 4), min(frame.shape[1], x1 + dx)):
            if tuple(int(v) for v in frame[Y, X][:3]) in spec["tie_cols"] and frame[Y, X, 3] > 0:
                out[k * Y:k * (Y + 1), k * X:k * (X + 1)] = frame[Y, X]
    # the outline closed round the new head only (elsewhere the frame is the 1x frame, untouched)
    closed, _, _ = G.complete_outline(out)
    zone = ndimage.binary_dilation(nm, iterations=k + 1)
    out[zone] = closed[zone]
    # a pocket the clearing shut in (between the new head, the ponytail, the tie): filled - hair where the old head's
    # hair or skin was, outline where its outline was, else what was there
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op & (hd[..., 3] > 0)
    holes &= ~up(ndimage.binary_fill_holes(frame[..., 3] > 0) & ~(frame[..., 3] > 0), k)
    hairish = {tuple(c) for c in spec["hair_cols"]} | set(spec["skin_cols"])
    for y, x in zip(*np.nonzero(holes)):
        c = tuple(int(v) for v in hd[y, x][:3])
        out[y, x] = (spec["hair"] + [255]) if c in hairish else hd[y, x]
    # a piece of the old head the new one cut off (a flick of hair, an outline end): mostly its colours, apart now
    lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
    was, _ = ndimage.label(hd[..., 3] > 0, structure=np.ones((3, 3)))
    head_lab = np.bincount(lab[nm].ravel(), minlength=n + 1)[1:].argmax() + 1 if nm.any() else 0
    own = {tuple(c) for c in spec["hair_cols"]} | set(spec["skin_cols"]) | {spec["line"], tuple(spec["hair"])} | spec["tie_cols"]
    under = was[nm & (hd[..., 3] > 0)]
    body = np.bincount(under[under > 0]).argmax() if (under > 0).any() else -1
    for v in range(1, n + 1):
        if v == head_lab:
            continue
        part = lab == v
        if len(np.unique(was[part])) == 1 and was[part][0] == body and np.mean(
                [tuple(int(c) for c in p[:3]) in own for p in out[part]]) >= 0.8:
            out[part] = 0
    # a speck the old head left apart from the figure (smaller than anything the 1x frame has) goes
    lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
    lab1, n1 = ndimage.label(frame[..., 3] > 0, structure=np.ones((3, 3)))
    least = min([k * k * int(z) for z in ndimage.sum(frame[..., 3] > 0, lab1, range(1, n1 + 1))] or [0])
    for v, z in enumerate(ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1)), 1):
        if z < min(least, 40):
            out[lab == v] = 0
    return out


def drawn_strip(hero, tag, sizes, k):
    """The drawn hd frames of `tag` (None when there is no strip). Each is round(k x the 1x frame), or the size
    <hero>_<tag>.json lists (tools/art/import_ppu_strips.py: grown alike at both ends, the centre kept)."""
    p = os.path.join(SRC, f"{hero}_{tag}.png")
    if not os.path.isfile(p):
        return None
    s = np.asarray(Image.open(p).convert("RGBA"))
    side = os.path.join(SRC, f"{hero}_{tag}.json")
    if os.path.isfile(side):
        with open(side, encoding="utf-8") as f:
            big = [tuple(v) for v in json.load(f)["sizes"]]
        if len(big) != len(sizes):
            sys.exit(f"{side}: {len(big)} sizes for {len(sizes)} frames")
    else:
        big = [hd_size(w, h, k) for w, h in sizes]
    out, x = [], 0
    for W, H in big:
        if x + W > s.shape[1] or H > s.shape[0]:
            sys.exit(f"{p}: too small for {len(sizes)} frames of {k}x the 1x sizes")
        out.append(s[:H, x:x + W].copy())
        x += W + 1
    return out


def add_hd(hero, sheet):
    """Replace `sheet`'s hd_ tags ({tag: [(array, ms)]}) with fresh ones from its 1x tags.
    -> {"drawn": tags, "scaled": tags, "head": {tag: [frame indices with the HEAD]}}."""
    k = PPU[hero]
    for t in [t for t in sheet if not plain(t)]:
        del sheet[t]
    made = {"drawn": [], "scaled": [], "head": {}}
    tpl = tmask = None
    if hero in HEAD:
        spec = HEAD[hero]
        tpl = sheet["idle"][0][0]
        tmask = head_mask(tpl, spec["face_box"])
        spec["tie_cols"] = {tuple(int(v) for v in tpl[y, x][:3]) for x, y in spec.get("on_top", ())}
        spec["region"] = head_mask(tpl, spec["box"])
        spec["palette"] = set(spec["hair_cols"]) | set(spec["skin_cols"])
    for tag in list(sheet):
        frames = sheet[tag]
        drawn = drawn_strip(hero, tag, [(a.shape[1], a.shape[0]) for a, _ in frames], k)
        if drawn is not None:
            sheet[PREFIX + tag] = [(b, ms) for b, (_, ms) in zip(drawn, frames)]
            made["drawn"].append(tag)
            continue
        out = []
        for i, (a, ms) in enumerate(frames):
            hit = find_head(a, tpl, tmask) if tpl is not None else None
            placed = HEAD[hero]["place"].get((tag, i)) if tpl is not None else None
            if placed is not None:
                dx, dy, how = placed
                flip = {"h": "h", "v": "v"}.get(how)
                bad = "set"
            elif hit is None or hit[0] > HEAD[hero]["tolerance"]:
                out.append((up(a, k), ms))
                continue
            else:
                bad, dx, dy, mirrored = hit
                flip = "h" if mirrored else None
            turn = {"h": lambda x: x[:, ::-1], "v": lambda x: x[::-1], None: lambda x: x}[flip]
            b = paste_head(hero, turn(a), k, (dx, dy))
            if b is None:
                out.append((up(a, k), ms))
                continue
            out.append((np.ascontiguousarray(turn(b)), ms))
            made["head"].setdefault(tag, []).append(f"{i + 1}{flip or ''}({bad})")
        sheet[PREFIX + tag] = out
        made["scaled"].append(tag)
    add_lo(hero, sheet)
    return made


def lo_size(w1, h1):
    return round(w1 * UI_PPU), round(h1 * UI_PPU)


def grow(a, k, pivot):
    """`a` brought to k times as many pixels a side (k > 1) on a grid through the pivot, each new pixel the dense pixel
    under its centre (nearest). pixel_down.pixelate averages squares of 1/k pixels: for k > 1 a square can hold no pixel
    centre, so every few rows and columns came out clear - the grid of lines over Malzahar, Kalista and Tahm Kench on
    the BP cards (the user, 2026-10-16: 「BP界面这塔姆怎么回事？全是网格」). -> (frame, new pivot)."""
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


def add_lo(hero, sheet):
    """lo_<tag> for every tag: its hd_ frames brought to UI_PPU squares a displayed game pixel (tools/art/pixel_down.py;
    the hero's SIZES size counted in), each on a frame of round(UI_PPU x the 1x size) - grown alike at both ends where
    the drawing needs more - the pivot at its centre."""
    import pixel_down as D
    k = PPU[hero]
    size = D.sizes_of().get(hero, 1.0)
    for tag in [t for t in sheet if plain(t)]:
        out = []
        for (one, ms), (b, _) in zip(sheet[tag], sheet[PREFIX + tag]):
            outline = D.edge_colour(b) if (b[..., 3] > 0).any() else (0, 0, 0)
            f_ = UI_PPU * size / k
            if f_ > 1:                                   # a hero drawn coarser than the BP frames: grown, not averaged
                lo, (px, py) = grow(b, f_, (b.shape[1] / 2, b.shape[0] / 2))
            else:
                lo, (px, py) = D.pixelate(b, f_, (b.shape[1] / 2, b.shape[0] / 2), outline)
            W, H = lo_size(one.shape[1], one.shape[0])
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
            out.append((f, ms))
        sheet[LO + tag] = out


def check(hero, sheet):
    """Every 1x tag has its hd_ tag: as many frames, the same timing, PPU x each size. -> list of problems."""
    k, bad = PPU[hero], []
    for tag, frames in sheet.items():
        if not plain(tag):
            pre = PREFIX if tag.startswith(PREFIX) else LO
            if tag[len(pre):] not in sheet:
                bad.append(f"{tag} has no 1x {tag[len(pre):]}")
            continue
        lo = sheet.get(LO + tag)
        if lo is None:
            bad.append(f"{tag} has no {LO}{tag} (the BP / encyclopedia frames: python tools/art/ppu_hd.py --hero {hero})")
        elif len(lo) != len(frames) or any(abs(m1 - m2) > 1e-6 for (_, m1), (_, m2) in zip(frames, lo)):
            bad.append(f"{LO}{tag}: {len(lo)} frames or the timing unlike {tag}'s")
        else:
            for i, ((a, _), (c, _)) in enumerate(zip(frames, lo)):
                W, H = lo_size(a.shape[1], a.shape[0])
                # (a margin may be odd: a 1x frame made from its hd_ frame by tools/art/ppu_one.py grows by whole 1x
                # pixels at both ends to hold the drawing, and every frame is drawn about its own centre)
                if c.shape[1] < W or c.shape[0] < H:
                    bad.append(f"{LO}{tag}[{i}]: {c.shape[1]}x{c.shape[0]}, want {W}x{H} or grown alike at both ends")
        hd = sheet.get(PREFIX + tag)
        if hd is None:
            bad.append(f"{tag} has no {PREFIX}{tag}")
            continue
        if len(hd) != len(frames):
            bad.append(f"{PREFIX}{tag}: {len(hd)} frames, {tag} {len(frames)}")
            continue
        for i, ((a, ms), (b, ms2)) in enumerate(zip(frames, hd)):
            W, H = hd_size(a.shape[1], a.shape[0], k)
            # a drawn frame may be grown alike at both ends (the centre, the pivot, kept); the margin may be odd where
            # tools/art/ppu_one.py grew the 1x frame for the drawing brought down from it (each frame is drawn about
            # its own centre: the pivot is from the frame's size)
            grown = is_drawn(hero, tag) and b.shape[1] >= W and b.shape[0] >= H
            if ((b.shape[1], b.shape[0]) != (W, H) and not grown) or abs(ms - ms2) > 1e-6:
                bad.append(f"{PREFIX}{tag}[{i}]: {b.shape[1]}x{b.shape[0]} {ms2} ms, want {W}x{H} {ms} ms")
            elif tag == "idle" and b.shape[1] != W:
                bad.append(f"{PREFIX}idle[{i}]: {b.shape[1]} wide - the DLL needs hd_idle exactly round(PPU x {a.shape[1]})")
    return bad


def outside_head(hero, sheet):
    """hd pixels that differ from the 1x frame scaled, far from where its head is (the body must stay the 1x art)."""
    bad = []
    for tag in [t for t in sheet if t.startswith(PREFIX) and not is_drawn(hero, t[len(PREFIX):])]:
        if hero in REDRAWN:
            continue                    # the whole frame is the drawing, not the 1x art
        for i, (b, _) in enumerate(sheet[tag]):
            a = up1(hero, sheet[tag[len(PREFIX):]][i][0])
            diff = np.abs(a.astype(int) - b.astype(int)).max(axis=2) > 0
            if not diff.any():
                continue
            lab, n = ndimage.label(ndimage.binary_dilation(diff, iterations=6))
            if n > 1:
                sizes = ndimage.sum(diff, lab, range(1, n + 1))
                bad.append(f"{tag}[{i}]: changes in {n} places ({', '.join(str(int(z)) for z in sizes)} pixels)")
    return bad


def strays(hero, sheet):
    """Pixels left over in the hd frames: specks apart from the figure (a part under 40 pixels; nothing in the 1x frame
    is that small once scaled) and slivers (a pixel with 6+ clear neighbours of 8 - a whole k x k or 2 x 2 block never
    has more than 5). -> list of problems ("别留多余的像素")."""
    bad = []
    for tag in [t for t in sheet if t.startswith(PREFIX)]:
        if is_drawn(hero, tag[len(PREFIX):]):
            bad += drawn_strays(tag, sheet[tag])
            continue
        for i, (b, _) in enumerate(sheet[tag]):
            op = b[..., 3] > 0
            lab, n = ndimage.label(op, structure=np.ones((3, 3)))
            sizes = ndimage.sum(op, lab, range(1, n + 1))
            small = [int(z) for z in sizes if z < 40]
            p = np.pad(op, 1)
            clear = sum((~p[1 + a:1 + a + op.shape[0], 1 + c:1 + c + op.shape[1]]).astype(int)
                        for a in (-1, 0, 1) for c in (-1, 0, 1) if a or c)
            sliver = op & (clear >= 6)
            one = sheet[tag[len(PREFIX):]][i][0]
            p1 = np.pad(one[..., 3] > 0, 1)
            # the 1x frame's own lone pixels and specks are its drawing, not leftovers
            lab1, n1 = ndimage.label(one[..., 3] > 0, structure=np.ones((3, 3)))
            small1 = sorted(int(z) * PPU[hero] ** 2 for z in ndimage.sum(one[..., 3] > 0, lab1, range(1, n1 + 1))
                            if z * PPU[hero] ** 2 < 40)
            # holes: clear pockets shut in by the figure that the 1x frame does not have ("像素缺失")
            holes = ndimage.binary_fill_holes(op) & ~op
            holes1 = up1(hero, (ndimage.binary_fill_holes(one[..., 3] > 0) & ~(one[..., 3] > 0))[..., None])[..., 0]
            new_holes = holes & ~holes1
            if hero in REDRAWN:         # the drawing's own gaps (under the arm), not leftovers
                new_holes[:] = False
            if new_holes.any():
                ys, xs = np.nonzero(new_holes)
                bad.append(f"{tag}[{i}]: {int(new_holes.sum())} hole pixels at {list(zip(xs.tolist(), ys.tolist()))[:4]}")
            if sorted(small) != small1 or sliver.any():
                ys, xs = np.nonzero(sliver)
                bad.append(f"{tag}[{i}]: specks {small} (1x had {small1}), {int(sliver.sum())} sliver pixels"
                           + (f" at {list(zip(xs.tolist(), ys.tolist()))[:6]}" if sliver.any() else ""))
    return bad


def drawn_strays(tag, frames):
    """A drawn frame's leftovers: specks of 1-3 pixels apart from the figure ("别留多余的像素")."""
    bad = []
    for i, (b, _) in enumerate(frames):
        op = b[..., 3] > 0
        lab, n = ndimage.label(op, structure=np.ones((3, 3)))
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        small = [int(z) for z in sizes if z < 4]
        if small:
            bad.append(f"{tag}[{i}]: specks {small}")
    return bad


def review(hero, sheet, out_dir):
    """<hero>_hd_<tag>.png per tag: 1x frames above (x 2k) and hd frames below (x 2), as on a 2x screen."""
    k = PPU[hero]
    os.makedirs(out_dir, exist_ok=True)
    ground = np.array([120, 150, 90, 255], np.uint8)
    for tag in [t for t in sheet if plain(t)]:
        rows = []
        for frames, z in ((sheet[tag], 2 * k), (sheet[PREFIX + tag], 2)):
            cells = [up(a, z) for a, _ in frames]
            h = max(c.shape[0] for c in cells)
            row = [np.pad(c, ((h - c.shape[0], 0), (0, 8), (0, 0))) for c in cells]
            rows.append(np.concatenate(row, axis=1))
        w = max(r.shape[1] for r in rows)
        img = np.concatenate([np.pad(r, ((0, 8), (0, w - r.shape[1]), (0, 0))) for r in rows])
        img = np.where(img[..., 3:] > 0, img, ground)
        Image.fromarray(img).save(os.path.join(out_dir, f"{hero}_hd_{tag}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", help="default: every hero in PPU")
    ap.add_argument("--check", action="store_true", help="only check the sheets, write nothing")
    ap.add_argument("--review", help="write 1x-over-hd frame sheets per tag to this folder")
    a = ap.parse_args()
    bad = 0
    for hero in a.hero or sorted(PPU):
        if hero not in PPU:
            sys.exit(f"{hero}: not in PPU (tools/art/ppu_hd.py and addons/league_main/src/hd.rs)")
        stem = stem_of(hero)
        sheet = read_sheet(stem)
        if not a.check:
            made = add_hd(hero, sheet)
            w, h = G.write_sheet(stem, sheet)
            print(f"{hero_id(hero)}#sheet.png {w}x{h}: hd_ tags at PPU {PPU[hero]} - drawn: "
                  f"{', '.join(made['drawn']) or 'none'}; scaled: {', '.join(made['scaled']) or 'none'}; head in "
                  + (", ".join(f"{t} {' '.join(v)}" for t, v in made["head"].items()) or "none"))
        if a.review:
            review(hero, sheet, a.review)
        problems = check(hero, sheet) + strays(hero, sheet) + outside_head(hero, sheet)
        for p in problems:
            print(f"{hero_id(hero)}: {p}")
        bad += len(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
