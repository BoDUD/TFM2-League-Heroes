#!/usr/bin/env python3
"""Smeech's Codex poses (assets/source/smeech/codex_poses: POSE_PROMPTS.md, 20 key poses of his own TFT clips on his
design, 2026-10-29) as game pictures: read on their grid, the design's head on every standing pose, specks dropped,
gaps closed.

    python tools/art/design_smeech_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_smeech_poses.py                  # writes assets/source/smeech/hd/pose_<name>.png (+ .json)

Codex delivered every pose on the pack's exact 9 px squares from the canvas corner (its root folder; baseline_1176/ is
the same shifted 3 px), all in the design's 36 colours, so a pose is read square for square (a[4::9, 4::9]). Its heads
are its own drawing - 16-22 squares of hat as the design's 18 x 17, so the scale held, but the face turned and redrawn
frame to frame, and in the walk a claw over the face (the TFT walk carries the near claw by his cheek). So every
standing pose gets the design's head (HEAD_POLY of hd/idle.png: the hat, the goggles, the hair, both ears, the face to
the chin; not the arm by the left ear): placed on the pose's hat (the largest component of the hat's teal colours) and
nudged to where most of its squares match Codex's own head; then Codex's head-only squares left round it (within
LEFT squares, not covered) cleared, and the head drawn over all (the claw by his cheek goes behind it). The two falls
keep Codex's head: the hat came off (the prompt's), the head tilted with the body.
Each pose's json keeps where its picture's top-left square is on the pack's grid (grid_at: Codex drew each pose where
its reference put it, so rig_smeech places them by it) and where the head's box went (head_at).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_smeech_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import pack_smeech_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "smeech", "codex_poses", "smeech-poses")
OUT = os.path.join(ROOT, "assets", "source", "smeech", "hd")
NAMES = list(PK.POSES)
FALLS = ("d_fall", "d_down")
WALK = tuple(f"run{k}" for k in range(1, 9))
# the walk's heads go on Codex's chins (the user, 2026-10-29: 「走路时身体和头有点不协调」): by the hat they sat 1 to 7
# squares off the neck Codex drew, a different way each frame (its walk hats lean), so the body slid under the head
FUR = ((243, 206, 188), (192, 145, 127), (131, 91, 84))   # the face's fur: its chin is the largest part's bottom
# the design's head on hd/idle.png (x, y): the hat, the hair's right spike, the right ear, the chin, the left ear's
# underside over the arm's ring, the left ear's tip
HEAD_POLY = [(62, 0), (96, 0), (96, 17), (106, 17), (112, 22), (112, 42), (101, 47), (70, 47), (66, 45), (59, 41),
             (53, 35), (49, 24), (56, 21), (62, 21)]
ARM = ((92, 95, 68), (140, 146, 106), (54, 51, 45), (47, 225, 8), (25, 176, 13), (13, 103, 23), (209, 247, 14))
# the arm's olive and its neon-green lights (read off hd/idle.png's arm), kept out of the head
HAT_AT = (65, 1)                 # the design hat's top-left square (its teal component)
SEARCH = 6                       # squares the head is nudged round the hat's place
LEFT = 6                         # squares round the pasted head where Codex's own head-only squares are cleared
# drawn wrong, cleared by hand (pack-grid squares, read at 8x): q_crouch's left ear was drawn as a purple-red cape
# flaring over his back (the pasted head brings the ear back)
CUT = {"q_crouch": [[(35, 62), (61, 58), (63, 76), (56, 82), (45, 84), (35, 80)]]}
EAR_SHADES = ((183, 40, 22), (123, 38, 19))   # the ears' darker reds (the body wears them only under the chin)
CHIN = 46                        # the head box's rows down to the chin
HANG = 8                         # squares round the head a part may reach and still be a leftover of Codex's head
# Codex's head left round the pasted one where it hangs on a claw or the coat (head-box squares x0, y0, x1, y1, read
# at 10-12x; only squares off the pasted head): q_crouch's own right ear, its goggles' rim over the hat, its chin;
# run2's hat patch and third goggle left of the pasted hat and its old ear tip under the left ear, run8's patch (the
# walk's heads on the chins)
HEAD_CUT = {"q_crouch": [(52, 20, 66, 38), (29, 6, 40, 18), (45, 40, 54, 49)], "run2": [(8, 5, 17, 24), (-8, 36, 8, 46)],
            "run8": [(10, 14, 20, 22)]}
# squares recoloured on the cropped picture (box, colour, new colour): d_down's cheek carried a smear of the arm's
# olive (Codex's own head, kept in the falls) - the fur's middle shade
RECOLOUR = {"d_down": [((28, 18, 40, 27), (140, 146, 106), (131, 91, 84))]}
SPECK = 8                        # parts apart from the figure smaller than this are dropped


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA")).copy()


def head_template(d):
    """(the head's squares on their box, its mask, the box's top-left on the design)."""
    m = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(m).polygon(HEAD_POLY, fill=1)
    mask = (np.asarray(m) > 0) & (d[..., 3] > 0)
    for c in ARM:
        mask &= ~np.all(d[..., :3] == c, axis=-1)
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    t = d[y0:y1, x0:x1].copy()
    tm = mask[y0:y1, x0:x1]
    t[~tm] = 0
    return t, tm, (x0, y0)


def hat_colours(d):
    x0, y0 = HAT_AT
    box = d[y0:y0 + 16, x0:x0 + 18]
    cs = {tuple(c) for c in box[box[..., 3] > 0][:, :3]}
    return {c for c in cs if int(c[1]) > int(c[0]) + 25}


def hat_of(g, hats):
    m = np.zeros(g.shape[:2], bool)
    for c in hats:
        m |= np.all(g[..., :3] == c, axis=-1) & (g[..., 3] > 0)
    lb, n = ndimage.label(m, np.ones((3, 3)))
    k = np.argmax(ndimage.sum(m, lb, range(1, n + 1))) + 1
    ys, xs = np.nonzero(lb == k)
    return xs.min(), ys.min()


def head_only(d, t, tm, at):
    """The colours only the head uses (not on the rest of the design)."""
    rest = d.copy()
    x0, y0 = at
    rest[y0:y0 + tm.shape[0], x0:x0 + tm.shape[1]][tm] = 0
    return {tuple(c) for c in t[tm][:, :3]} - {tuple(c) for c in rest[rest[..., 3] > 0][:, :3]}


def read(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"smeech-pose-{name}.png"))).convert("RGBA"))
    return a[PK.PX // 2::PK.PX, PK.PX // 2::PK.PX].copy()


def drop_specks(g):
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, np.ones((3, 3)))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for k, s in enumerate(sizes, 1):
        if s < SPECK:
            g[lb == k] = 0
    return g


def hat_mask(g, hats):
    """Codex's own hat: the largest component of the hat's teal colours."""
    m = np.zeros(g.shape[:2], bool)
    for c in hats:
        m |= np.all(g[..., :3] == c, axis=-1) & (g[..., 3] > 0)
    lb, n = ndimage.label(m, np.ones((3, 3)))
    return lb == np.argmax(ndimage.sum(m, lb, range(1, n + 1))) + 1


def clear_strays(g, keep, ears, ink, zone, chin=None):
    """After the head went on: Codex's ear-red squares off the pasted head (its own ears drawn elsewhere,
    q_crouch's 'cape'); every part left that lies wholly in `zone` (round Codex's old head: its goggles, the hat's
    patch, the chin it drew); then outline squares left with nothing but outline or clear round them."""
    for c in ears:   # the pasted head has both its ears: any other ear-red square is Codex's
        g[np.all(g[..., :3] == c, axis=-1) & ~keep] = 0
    if chin is not None:   # the ears' darker reds beside the head down to its chin (run2's, run7's streaks)
        x0, x1, y1 = chin
        side = np.zeros(g.shape[:2], bool)
        side[:y1, max(0, x0 - HANG):x1 + HANG] = True
        for c in EAR_SHADES:
            g[np.all(g[..., :3] == c, axis=-1) & side & ~keep] = 0
    rest = (g[..., 3] > 0) & ~keep
    lb, n = ndimage.label(rest, np.ones((3, 3)))
    for k in range(1, n + 1):
        if not ((lb == k) & ~zone).any():
            g[lb == k] = 0
    # bits that hang on the head's rim only (seen apart from it, within HANG of it): run2's red chin streaks, the
    # patch off its old hat; the neck, the arms and the claws behind the head reach farther and stay
    rim = ndimage.binary_dilation(keep, iterations=1)
    rest = (g[..., 3] > 0) & ~rim
    lb, n = ndimage.label(rest, np.ones((3, 3)))
    hang = ndimage.binary_dilation(keep, iterations=HANG)
    for k in range(1, n + 1):
        if not ((lb == k) & ~hang).any():
            g[lb == k] = 0
    body = (g[..., 3] > 0) & ~rim
    lone = rim & ~keep & (g[..., 3] > 0) & ~ndimage.binary_dilation(body, np.ones((3, 3)))
    g[lone] = 0
    for _ in range(3):
        op = g[..., 3] > 0
        line = op & np.all(g[..., :3] == ink, axis=-1)
        body = op & ~line
        orphan = line & ~ndimage.binary_dilation(body, np.ones((3, 3)), iterations=1) & ~keep
        g[orphan] = 0
    return g


def chin(g, upper=0.5):
    """(x, y) of a face's chin: the bottom middle (its last 3 rows) of the largest part in FUR's colours within the
    figure's top `upper`."""
    m = np.zeros(g.shape[:2], bool)
    for c in FUR:
        m |= np.all(g[..., :3] == c, axis=-1) & (g[..., 3] > 0)
    oy = np.nonzero(g[..., 3].any(1))[0]
    m[int(oy.min() + (oy.max() - oy.min()) * upper) + 1:] = False
    lb, n = ndimage.label(m, np.ones((3, 3)))
    ys, xs = np.nonzero(lb == np.argmax(ndimage.sum(m, lb, range(1, n + 1))) + 1)
    return float(xs[ys >= ys.max() - 2].mean()), int(ys.max())


def lay_head(name, g, t, tm, place, only, hats, ears, ink, search=SEARCH):
    """The design's head on g: placed by the hat, nudged to the best match (within `search`); Codex's own hat and
    head-only squares round it cleared, then its stray ears and orphaned outline. Returns (g, the head box's top-left
    on g, the match)."""
    px, py = place
    old_hat = hat_mask(g, hats)
    best, at = -1, (px, py)
    H, W = tm.shape
    for dy in range(-search, search + 1):
        for dx in range(-search, search + 1):
            x, y = px + dx, py + dy
            if x < 0 or y < 0 or x + W > g.shape[1] or y + H > g.shape[0]:
                continue
            win = g[y:y + H, x:x + W]
            score = int((np.all(win[..., :3] == t[..., :3], axis=-1) & tm & (win[..., 3] > 0)).sum())
            if score > best:
                best, at = score, (x, y)
    x, y = at
    near = np.zeros(g.shape[:2], bool)
    near[y:y + H, x:x + W] = tm
    near = ndimage.binary_dilation(near, iterations=LEFT)
    covered = np.zeros(g.shape[:2], bool)
    covered[y:y + H, x:x + W] = tm
    old = old_hat.copy()
    for c in only:
        old |= near & np.all(g[..., :3] == c, axis=-1) & (g[..., 3] > 0)
    zone = ndimage.binary_dilation(old | covered, iterations=2)
    g[old & ~covered] = 0
    g[y:y + H, x:x + W][tm] = t[tm]
    g = clear_strays(g, covered, ears, ink, zone, (x, x + W, y + CHIN))
    for bx0, by0, bx1, by1 in HEAD_CUT.get(name, ()):
        box = np.zeros(g.shape[:2], bool)
        box[max(0, y + by0):y + by1, max(0, x + bx0):x + bx1] = True
        g[box & ~covered] = 0
    return g, at, best / tm.sum()


def ear_colours(t, tm, only):
    """The ears' reds (head-only, red over green and blue)."""
    return {c for c in only if int(c[0]) > 150 and int(c[1]) < 90 and int(c[2]) < 60}


def cut(g, name):
    """CUT's polygons cleared (pack-grid squares)."""
    for poly in CUT.get(name, ()):
        m = Image.new("L", (g.shape[1], g.shape[0]), 0)
        ImageDraw.Draw(m).polygon(poly, fill=1)
        g[np.asarray(m) > 0] = 0
    return g


def pose(name, d, t, tm, at, hats, only):
    g = cut(read(name), name)
    head = None
    if name not in FALLS:
        ink = tuple(int(v) for v in PD.edge_colour(d)[:3])
        if name in WALK:   # the chin on Codex's chin, where its head meets the body (no nudge)
            (cx, cy), (tx, ty) = chin(g), chin(np.where(tm[..., None], t, 0).astype(np.uint8), upper=1.0)
            g, head, fit = lay_head(name, g, t, tm, (round(cx - tx), cy - ty), only, hats, ear_colours(t, tm, only),
                                    ink, search=0)
        else:
            hx, hy = hat_of(g, hats)
            place = (hx - (HAT_AT[0] - at[0]), hy - (HAT_AT[1] - at[1]))
            g, head, fit = lay_head(name, g, t, tm, place, only, hats, ear_colours(t, tm, only), ink)
        print(f"{name:9s} head at {head} (matched {fit:.0%} of Codex's own head)")
    g = close_gaps(drop_specks(g), d)
    ys, xs = np.nonzero(g[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    fig = g[y0:ys.max() + 1, x0:xs.max() + 1].copy()
    for (bx0, by0, bx1, by1), was, now in RECOLOUR.get(name, ()):
        box = fig[by0:by1, bx0:bx1]
        box[np.all(box[..., :3] == was, axis=-1) & (box[..., 3] > 0), :3] = now
    head_at = [int(head[0] - x0), int(head[1] - y0)] if head else None
    return fig, {"head_at": head_at, "grid_at": [int(x0), int(y0)]}


def big4(a, z):
    bg = np.zeros((a.shape[0], a.shape[1], 4), np.uint8)
    bg[...] = (200, 200, 200, 255)
    im = Image.fromarray(bg)
    im.alpha_composite(Image.fromarray(a))
    return im.resize((a.shape[1] * z, a.shape[0] * z), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    d = design()
    t, tm, at = head_template(d)
    hats, only = hat_colours(d), head_only(d, t, tm, at)
    figs = {n: pose(n, d, t, tm, at, hats, only) for n in NAMES}
    if a.sheet:
        z = 4
        cells = [("design", big4(d, z))] + [(n, big4(f, z)) for n, (f, _) in figs.items()]
        cols = 5
        cw = max(c.width for _, c in cells) + 20
        chh = max(c.height for _, c in cells) + 30
        rows = (len(cells) + cols - 1) // cols
        sheet = Image.new("RGB", (cw * cols, chh * rows), (255, 255, 255))
        dr = ImageDraw.Draw(sheet)
        for k, (n, c) in enumerate(cells):
            x, y = (k % cols) * cw + 10, (k // cols) * chh + 24
            sheet.paste(c, (x, y + chh - 30 - c.height))
            dr.text((x, y - 20), n, fill=(0, 0, 0))
        os.makedirs(lp(a.sheet), exist_ok=True)
        path = os.path.join(a.sheet, "smeech_poses.png")
        sheet.save(lp(path))
        print(path, sheet.size)
        return
    for n, (fig, meta) in figs.items():
        if n in WALK:      # the walk's frames are design_smeech_walk.py's (one body; run5's read is its base)
            continue
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump(meta, fh)
    print(len(figs), "poses ->", OUT)


if __name__ == "__main__":
    main()
