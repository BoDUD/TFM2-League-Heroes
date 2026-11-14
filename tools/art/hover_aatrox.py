#!/usr/bin/env python3
"""World Ender keeps Aatrox in the air for its whole length (the user, 2026-10-04: 「剑魔的大招应该一直在天上的吧？」;
2026-11-14, on the list of differences from League: 「全改吧」): the hover frames league.dll's LOOKS row plays instead of
idle / run / hit / ult while `league_aatrox_r` is on him (addons/league_main/src/looks.rs), and his R casts kept off the
ground between them - all of it his own approved frames moved whole, the wings beating while he hovers.

    python tools/art/hover_aatrox.py            # rewrite league/champions/league_aatrox#sheet.png and #anim.fanim
    python tools/art/hover_aatrox.py --check    # exit 1 when the sheet is not what this writes
    python tools/art/hero_reels.py --check      # the idle / ban-pick reels still point at the right squares

Why it was on the ground. tools/art/air_aatrox.py (2026-10-04) rebuilt the R casts airborne (League's ULT clips: the
feet 39-117 units over the floor, only the Q slams touching down), but the game plays idle / run / hit by name and the
kit could not swap them, so every cast took off from the ground and landed on it, and between casts he stood with the
wing loop `league_aatrox_r_look` drew behind him on his standing point (league_aatrox_big r_aura, 1x art).

The hover pose is REST, the last frame of every R cast: Codex's PPU redraw (2026-11-03, rig_aatrox_hd.py) of
air_aatrox's REST - his idle with the loop's wings spread at rest; its body the idle's own, square for square at the
same rows (the head's top, the chest core and the soles where the idle has them). Lifted HOVER_HD dense px (7.03 game
px, 16 at PPU 91/40): the airborne frames of his attacks fight 6-7.4 game px up (their chest core 17.5-20.0 game px over
the pivot against the idle's 12.6; REST lifted: 19.1). Every frame here is an existing frame moved whole by whole pixels
of its own density (1x, hd_, lo_: 7, 16 and 11 px for the hover) - nothing redrawn, turned or rescaled, so the body is
exactly the size it is everywhere else (「模型不要变大变小」).

- r_hover (his idle under R) and r_run (his glide): REST lifted with its wings beating (the user, after the still hover:
  「翅膀要扇啊 别僵硬啊」). The body stays square for square where it is in every frame - head, chest core, arms,
  sword, legs at the same rows (「上下摆动全不要了啊」: no bob, no lift on the down-stroke) - and only the wings move: each
  wing's squares beyond a vertical line at the body's side (WING_CUT, above a line clear of the sword) bent about that
  line, every column moved down whole by FLAP rows at the tip and nothing at the line (inbetween.repose: laid behind the
  body, the outline closed only where the move bared an edge; no tear where the wing meets what stays). REST's wings
  are the top of the stroke - they are spread high already, and lifted further their sloping rims fray into steps -
  so the beat goes down from them and back: down in three frames, back up in four and a held top, a beat about a
  second while he hovers (FLAP_MS) and quicker in the glide (RUN_MS). The same bend at every density, from the
  frame of that density, so the body's squares are the same at 1x, hd_ and lo_ too. Not `r_idle`: hero_reels makes
  any `<x>_idle` a held frame (its reels); r_hover is played as drawn;
- r_idle: gone (the still hover of 90fcff015);
- r_hit: REST lifted and pushed back HIT_BACK game px, the first frame flashed as his own hit's first (ppu_rig.flash
  inside the outer band of his outline, which stays dark as there);
- the R casts: every frame of attack_r, attack_p_r and skill2_r lower than the hover raised to it (they took off and
  landed: he would dip to the ground at every attack); the Q casts (skill_r, q2_r, q3_r) only before the swing, frames
  1-2 (their copies with E's dash, *_r_fx*, start at 300 ms in frame 3 and are left alone) - the slam and the REST after
  it stay on the ground as drawn (League: only the Q slams touch down). Played only under R, they change in place.
- r_ult: the transformation rising as drawn and settling on the hover, frames 6-8, instead of landing. `ult` itself
  stays as drawn - the ban/pick card and the idle reel play it (it would end in the air and drop to the standing
  idle there); the LOOKS row swaps it for r_ult in game (`league_aatrox_r` comes on in the tick the kit plays `ult`,
  and frames 1-5 are the same frames).
- the wings: REST carries Codex's spread wings, so the kit's view of `league_aatrox_r_look` (the 1x wing loop on his
  standing point, 7 game px under the hovering shoulders and a second pair of wings) is gone from the main pack's
  league_aatrox.data_champion and league_aatrox_chain's copy; the buff stays (the attack tree that gives it is frozen).

A cast frame is raised to the hover by the lowest opaque row: the frame's soles line (its centre + FEET game px) to it,
against the idle's plus the hover, never lowered. The sheet is written packed with identical frames sharing their
squares (strips.write_sheet share), so a repack leaves no square behind.

Numpy and Pillow only (CI runs `--check` with nothing else): the pieces of ppu_hd (the sheet read), ppu_rig (flash, the
feet line) and inbetween (repose, for parts laid behind the figure) it uses are carried here with scipy's labels, hole
fill, dilation and distance transforms done in numpy - the same squares out (checked against the scipy versions).
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402  (write_sheet; numpy and Pillow only)

HERO = "aatrox"
STEM = os.path.join(ROOT, "league", "champions", f"league_{HERO}")
PREFIX, LO, UI_PPU = "hd_", "lo_", 1.5                        # ppu_hd's dense and UI copies of a tag
PPU = 91 / 40                                                 # tools/art/ppu_hd.py PPU, addons/league_main/src/hd.rs HEROES
DENSITY = {"": 1.0, PREFIX: PPU, LO: UI_PPU}                  # pixels a game pixel: 1x, hd_, lo_
FEET = 11.5                                                   # game px from a frame's centre down to the soles line
DARK = 26                                                     # inbetween.DARK: a square this dark is outline already
HOVER_HD = 16                                                 # dense px: 7.03 game px
HOVER = HOVER_HD / PPU
REST = ("attack_r", -1)                                       # the last frame of every R cast
LIFT_ALL = ("attack_r", "attack_p_r", "skill2_r")
LIFT_SOME = {"skill_r": (0, 1), "q2_r": (0, 1), "q3_r": (0, 1)}
ULT_SETTLE = (5, 6, 7)                                        # r_ult's frames on the hover (from 0)
HIT_BACK = (2.0, 1.0)                                         # game px r_hit's two frames are pushed back
# his outline colour and its outer band's depth in dense px (ppu_restyle's outline round the figure): his own hit's
# flash frame keeps that band dark and whitens what is inside it
OUTLINE = (11, 2, 13)
OUTLINE_HD = 3
# the wing beat: the tips' drop per frame (dense rows down; 0 = REST's wings, the top of the stroke) - down in three
# frames, back up in four - and each frame's ms in the hover and in the glide
FLAP = (0, 6, 12, 16, 14, 10, 6, 2)
FLAP_MS, RUN_MS = 130, 80
BEND = 1.0                                                    # the bend's profile along the wing: (distance / length) ** BEND
# where the wings are cut off the body, game px from the frame's centre (its pivot; + right, + down): the near wing is
# what lies left of WING_CUT[0] and above the line SWORD_LINE (clear of the greatsword under it), the far wing what lies
# right of WING_CUT[1] and above FAR_LOW (clear of his claw hand); read off REST's dense frame (x 40 / 95, the sword
# line from (40, 52) to (0, 73), the hand under row 70 of 166 x 138 - its centre (69, 83))
WING_CUT = ((40 - 69) / PPU, (95 - 69) / PPU)
SWORD_LINE = (((40 - 69) / PPU, (52 - 83) / PPU), ((0 - 69) / PPU, (73 - 83) / PPU))
FAR_LOW = (70 - 83) / PPU
# the hover tags and the tags whose timing they take; they go in after idle_base (the last plain tag)
NEW = {"r_hover": None, "r_run": None, "r_hit": "hit", "r_ult": "ult"}
GONE = ("r_idle", "r_idle_base")                              # 90fcff015's still hover (hero_reels made the pair)
AFTER = "idle_base"


def px(n, k):
    """`n` game px in pixels of density k (whole)."""
    return int(round(n * k))


def read_sheet(stem):
    """stem#sheet.png + stem#anim.fanim -> {tag: [(frame array, ms), ...]} in the fanim's order (ppu_hd.read_sheet)."""
    px_ = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        fr = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px_[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000, 3)))
        out[tag] = fr
    return out


def table_ppu():
    """His PPU in league.dll's table (addons/league_main/src/hd.rs): PPU must be it."""
    src = open(os.path.join(ROOT, "addons", "league_main", "src", "hd.rs"), encoding="utf-8").read()
    m = re.search(rf'\("league_{HERO}", ([0-9.]+), include_str!', src)
    return float(m.group(1)) if m else None


# ------------------------------------------------------------------------------------------------- scipy's, in numpy
def grow4(m):
    """m with every square's four neighbours added (ndimage.binary_dilation, the cross, once; nothing from outside)."""
    out = m.copy()
    out[1:] |= m[:-1]
    out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def fill_holes(m):
    """m with the air it shuts in filled (ndimage.binary_fill_holes: the air reached from the edge by four-neighbour
    steps stays air)."""
    air = ~m
    reach = np.zeros_like(m)
    reach[0], reach[-1], reach[:, 0], reach[:, -1] = air[0], air[-1], air[:, 0], air[:, -1]
    while True:
        nxt = grow4(reach) & air
        if np.array_equal(nxt, reach):
            return ~reach
        reach = nxt


def pieces4(m):
    """The four-connected pieces of m, each a mask (ndimage.label's cross)."""
    H, W = m.shape
    seen = np.zeros_like(m)
    out = []
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        piece = np.zeros_like(m)
        seen[y0, x0] = piece[y0, x0] = True
        stack = [(y0, x0)]
        while stack:
            y, x = stack.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = piece[yy, xx] = True
                    stack.append((yy, xx))
        out.append(piece)
    return out


def one_across(h):
    """ndimage.distance_transform_edt(h).max() <= 1.5: every square of h has a square not of h among its eight
    neighbours (the distances between squares are 1, 1.41, then 2; outside the picture counts as h)."""
    p = np.pad(h, 1, constant_values=True)
    H, W = h.shape
    inner = h.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                inner &= p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
    return not inner.any()


def lum(rgb):
    """inbetween.lum (float32, as there: the same squares under DARK)."""
    rgb = rgb.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def flash(a, k=0.45):
    """ppu_rig.flash: the figure whitened (a hit's first frame)."""
    out = a.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


def repose(d, moves, outline, pad=0, crack=10, slit=40):
    """inbetween.repose for parts laid behind the rest of the figure (how "under", seam on), the same squares out: the
    picture d with each part's squares moved by (dx, dy) arrays the picture's size (a square's own move), the rest of
    the figure untouched; the outline put on the air next to a light square where the move bared that edge; the
    figure's outline drawn on a part behind it where the two did not lie side by side in d; the cracks the move opened
    (at most `crack` squares, or `slit` squares one square across) filled with the outline. -> on a canvas `pad`
    squares bigger on every side."""
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    taken = np.zeros((H, W), bool)
    for mask, _ in moves:
        taken |= mask & op
    Ho, Wo = H + 2 * pad, W + 2 * pad
    out = np.zeros((Ho, Wo, 4), np.uint8)
    sy = np.full((Ho, Wo), -1, int)
    sx = np.full((Ho, Wo), -1, int)
    depth = np.full((Ho, Wo), -1, int)

    def lay(mask, off, under, n):
        dx, dy = off
        ys, xs = np.nonzero(mask & op)
        if isinstance(dx, np.ndarray):
            dx, dy = dx[ys, xs], dy[ys, xs]
        ty, tx = ys + pad + dy, xs + pad + dx
        if not ((ty >= 0) & (ty < Ho) & (tx >= 0) & (tx < Wo)).all():
            sys.exit("repose: a part leaves the picture (pad more)")
        if under:
            free = out[ty, tx, 3] == 0
            ty, tx, ys, xs = ty[free], tx[free], ys[free], xs[free]
        out[ty, tx] = d[ys, xs]
        sy[ty, tx], sx[ty, tx], depth[ty, tx] = ys, xs, n

    lay(op & ~taken, (0, 0), False, 1)
    for n, (mask, off) in enumerate(moves, 2):
        lay(mask, off, True, n)
    drawn = out[..., 3] > 0
    light = drawn & (lum(out[..., :3]) >= DARK)
    opd = np.pad(op, 1)
    ring = np.zeros((Ho, Wo), bool)
    line = np.zeros((Ho, Wo), bool)
    pdrawn, pdepth = np.pad(drawn, 1), np.pad(depth, 1, constant_values=-1)
    for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = pdrawn[1 + dy_:1 + dy_ + Ho, 1 + dx_:1 + dx_ + Wo]
        nb_depth = pdepth[1 + dy_:1 + dy_ + Ho, 1 + dx_:1 + dx_ + Wo]
        ys, xs = np.nonzero(light & ~nb)
        if len(ys):
            qy, qx = sy[ys, xs], sx[ys, xs]
            known = qy >= 0
            was = np.zeros(len(ys), bool)
            was[known] = opd[qy[known] + 1 + dy_, qx[known] + 1 + dx_]
            ty, tx = ys[was] + dy_, xs[was] + dx_
            ok = (ty >= 0) & (ty < Ho) & (tx >= 0) & (tx < Wo)
            ring[ty[ok], tx[ok]] = True
        ys, xs = np.nonzero(light & nb & (nb_depth > depth))
        ty, tx = ys + dy_, xs + dx_
        asd = (sy[ty, tx] >= 0) & (sy[ty, tx] == sy[ys, xs] + dy_) & (sx[ty, tx] == sx[ys, xs] + dx_)
        line[ty[~asd], tx[~asd]] = True
    ring &= ~drawn
    out[ring, :3] = outline
    out[ring, 3] = 255
    line &= drawn & (depth >= 2)
    out[line, :3] = outline
    gaps = fill_holes(op) & ~op
    keep = np.zeros((Ho, Wo), bool)
    keep[pad:pad + H, pad:pad + W] = grow4(gaps)
    drawn = out[..., 3] > 0
    for h in pieces4(fill_holes(drawn) & ~drawn):
        if (h & keep).any():
            continue
        size = int(h.sum())
        if size <= crack or (size <= slit and one_across(h)):
            out[h, :3] = outline
            out[h, 3] = 255
    return out


def feet(a, k):
    """Pixels from the frame's soles line (its centre + FEET game px) up to under its lowest opaque row (negative:
    something hangs below the soles line)."""
    rows = np.nonzero((a[..., 3] > 0).any(1))[0]
    return a.shape[0] / 2.0 + FEET * k - (rows.max() + 1)


def lift(a, n):
    """The frame's picture n pixels higher about its centre (the pivot): n more rows at both ends, the picture at the top."""
    n = int(n)
    if n <= 0:
        return a
    out = np.zeros((a.shape[0] + 2 * n, a.shape[1], 4), np.uint8)
    out[:a.shape[0]] = a
    return out


def back(a, n):
    """The frame's picture n pixels further back (left: he faces right) about its centre."""
    n = int(n)
    if n <= 0:
        return a
    out = np.zeros((a.shape[0], a.shape[1] + 2 * n, 4), np.uint8)
    out[:, :a.shape[1]] = a
    return out


def flash_inside(a, k):
    """ppu_rig.flash (his hit's first frame) inside the outline: the outer band of his outline colour - OUTLINE_HD dense
    px, as many game px at the other densities - stays dark, as in his own hit's flash frame."""
    out = flash(a)
    op = a[..., 3] > 0
    # the squares within n four-neighbour steps of the air (ndimage.distance_transform_cdt taxicab <= n, the picture
    # framed in air): the air grown n times
    near = ~np.pad(op, 1)
    for _ in range(max(1, px(OUTLINE_HD / PPU, k))):
        near = grow4(near)
    keep = op & near[1:-1, 1:-1] & (a[..., :3] == OUTLINE).all(-1)
    out[keep] = a[keep]
    return out


def wings(a, k):
    """The two wings' masks in a hover frame of density k (WING_CUT, SWORD_LINE, FAR_LOW about its centre) and the
    cut columns: (near mask, near cut column, far mask, far cut column)."""
    H, W = a.shape[:2]
    cx, cy = W / 2.0, H / 2.0
    op = a[..., 3] > 0
    Y, X = np.mgrid[0:H, 0:W]
    (x0, y0), (x1, y1) = ((cx + x * k, cy + y * k) for x, y in SWORD_LINE)
    near_cut, far_cut = cx + WING_CUT[0] * k, cx + WING_CUT[1] * k
    near = op & (X < near_cut) & (Y < y0 + (X - x0) * (y1 - y0) / (x1 - x0))
    far = op & (X > far_cut) & (Y < cy + FAR_LOW * k)
    return near, near_cut, far, far_cut


def bend(shape, cut, tip, drop):
    """The moves of a wing bent about the column `cut`: every column toward `tip` moved down whole, `drop` pixels at the
    tip and nothing at the cut, by (distance / length) ** BEND (inbetween.repose's per-square (dx, dy))."""
    H, W = shape[:2]
    dy = np.zeros((H, W), int)
    for x in range(W):
        t = (x - cut) / (tip - cut)
        if t > 0:
            dy[:, x] = int(round(drop * min(1.0, t) ** BEND))
    return np.zeros((H, W), int), dy


def beat(hover, k, drop_hd):
    """The hover frame of density k with its wings `drop_hd` dense rows down at the tips (0: the frame itself)."""
    if not drop_hd:
        return hover
    near, near_cut, far, far_cut = wings(hover, k)
    drop = drop_hd / PPU * k
    nx, fx = np.nonzero(near.any(0))[0], np.nonzero(far.any(0))[0]
    moves = [(near, bend(hover.shape, near_cut, nx.min(), drop)), (far, bend(hover.shape, far_cut, fx.max() + 1, drop))]
    pad = int(np.ceil(abs(drop))) + 4
    f = repose(hover, moves, OUTLINE, pad=pad)
    H, W = hover.shape[:2]
    out = f[pad:pad + H, pad:pad + W]
    if (f[..., 3] > 0).sum() != (out[..., 3] > 0).sum():
        sys.exit(f"the wing beat ({drop_hd}) leaves the frame")
    body = (hover[..., 3] > 0) & ~(near | far)
    if not np.array_equal(out[body], hover[body]):
        sys.exit(f"the wing beat ({drop_hd}) changed a square of the body")
    return out


def build(sheet):
    """{tag: [(frame, ms)]} of the tags this writes (the lifted casts and the hover tags at every density) from `sheet`
    (ppu_hd.read_sheet)."""
    out = {}
    for pre, k in DENSITY.items():
        target = feet(sheet[pre + "idle_base"][0][0], k) + px(HOVER, k)
        for tag in LIFT_ALL + tuple(LIFT_SOME):
            frames = list(sheet[pre + tag])
            for i in (range(len(frames)) if tag in LIFT_ALL else LIFT_SOME[tag]):
                a, ms = frames[i]
                frames[i] = (lift(a, round(target - feet(a, k))), ms)
            out[pre + tag] = frames
        hover = out[pre + REST[0]][REST[1]][0]
        flap = [beat(hover, k, d) for d in FLAP]
        for tag, timing in NEW.items():
            if tag == "r_hit":
                ms = [m for _, m in sheet[timing]]
                out[pre + tag] = [(flash_inside(back(hover, px(HIT_BACK[0], k)), k), ms[0]),
                                  (back(hover, px(HIT_BACK[1], k)), ms[1])]
            elif tag == "r_ult":
                ult = sheet[pre + "ult"]
                out[pre + tag] = [(lift(a, round(target - feet(a, k))) if i in ULT_SETTLE else a, m)
                                  for i, (a, m) in enumerate(ult)]
            else:
                out[pre + tag] = [(f, float(FLAP_MS if tag == "r_hover" else RUN_MS)) for f in flap]
    return out


def gone(tag):
    """A tag of the still hover this no longer writes (GONE, at any density)."""
    return tag in GONE or any(tag == pre + g for pre in (PREFIX, LO) for g in GONE)


def merged(sheet, made):
    """The sheet with `made` in: the tags it has in place, the new ones after idle_base / hd_idle_base / lo_idle_base,
    the GONE ones out."""
    out = {}
    for tag, frames in sheet.items():
        if gone(tag):
            continue
        out[tag] = made.get(tag, frames)
        for pre in DENSITY:
            if tag == pre + AFTER:
                for new in made:
                    if new not in sheet and new.startswith(pre) and (pre or not new.startswith((PREFIX, LO))):
                        out[new] = made[new]
    missing = [t for t in made if t not in out]
    if missing:
        sys.exit(f"nowhere to put {missing}")
    return out


def same(a, b):
    return a.shape == b.shape and np.array_equal(a, b)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the sheet differs")
    a = ap.parse_args()
    if table_ppu() != PPU:
        sys.exit(f"league_{HERO}: PPU {PPU} here, {table_ppu()} in addons/league_main/src/hd.rs")
    stem = STEM
    sheet = read_sheet(stem)
    made = build(sheet)
    if a.check:
        bad = []
        for tag, frames in made.items():
            have = sheet.get(tag)
            if have is None:
                bad.append(f"{tag}: not in the sheet")
            elif len(have) != len(frames) or any(not same(x, y) or abs(m - n) > 1e-6
                                                 for (x, m), (y, n) in zip(have, frames)):
                bad.append(f"{tag}: frames differ")
        bad += [f"{t}: still in the sheet" for t in sheet if gone(t)]
        print("\n".join(bad) if bad else f"league_{HERO}: the hover tags and the raised R casts are as written")
        sys.exit(1 if bad else 0)
    out = merged(sheet, made)
    w, h = G.write_sheet(stem, out, share=True)
    lifted = {t: [i + 1 for i, ((x, _), (y, _)) in enumerate(zip(sheet[t], made[t])) if not same(x, y)]
              for t in made if t in sheet and not t.startswith(("r_", PREFIX + "r_", LO + "r_"))}
    print(f"league_{HERO}#sheet.png {w}x{h}: hover {px(HOVER, 1)} / {HOVER_HD} / {px(HOVER, UI_PPU)} px (1x / hd_ / lo_); "
          + "; ".join(f"{t} raised {v}" for t, v in lifted.items() if v and not t.startswith((PREFIX, LO)))
          + "; " + ", ".join(t for t in made if t.startswith("r_")))


if __name__ == "__main__":
    main()
