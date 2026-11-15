#!/usr/bin/env python3
"""league_caitlyn's run: her own drawn frames, the far leg a shade darker and one head in every frame (the user, on
her run: 「女警看不出交叉步啊」, then 「调暗后腿试试」 - darken the back leg - and 「怎么感觉耳朵也变形了」 - her ear changed from
frame to frame).

    python tools/art/caitlyn_run_shade.py                 # run / hd_run / lo_run into the sheet (+ the strips)
    python tools/art/caitlyn_run_shade.py --check         # exit 1 when the sheet's run tags are not what it makes
    python tools/art/caitlyn_run_shade.py --dry           # make them, write nothing

The frames are her old run's drawings as tools/art/run_fix.py left them (assets/source/caitlyn/hd/
caitlyn_run_drawn.png: the old frames 0 1 2 3 4 6 7 - the 6th, drawn small, dropped - the feet on the ground line,
117 ms a frame in one step and 156 in the other). No square of them moves but whole frames; only colours change, and
the head is one drawing:

- the far leg: her left leg (League's L leg: in her poses.json camera, tools/lol/pose_joints.py, it is the one away
  from the camera), the same leg through the cycle - swinging back in frames 0-2 (kicked up, folded, passing), landing
  in front in 3, planted under her in 4-5, lifting behind in 6 - its stocking and its boot (every square of FAR's
  rects in her leg colours, but a gold of the rifle's stock or the skirt's trim reaching in) one step down her own
  ramps (DARKER: the boot's browns, the stocking's navies, the buckles' golds); the darkest of each ramp stays (a
  step more is the outline). The near leg, and where it lies over the far one, untouched;
- the head: the standing frame's (hd_idle_base[0] within HEAD: the hat, the face, the ear and the sidelocks in front
  of it - cleaner than any run frame's, and the head she has standing; not the bit of her rifle HEAD's corner takes
  in) put in every frame where that frame's own head was (its hat matched square for square, so it follows her bob
  by whole squares); where the rifle passes in front of her chin (frame 6) the rifle stays in front, an outline on
  the head's side of it; round the head the frame's own hat, face and sidelocks cleared (never the rifle), her back
  hair kept; where the head meets that hair, 2 squares of outline on the hair's side; an edge the clearing bared
  closed with outline, and a pinhole of ground the head shut in filled with outline. The ear's window then changes
  from frame to frame only where her hair moves behind it.
The 1x frames come from the dense ones as tools/art/ppu_one.py's one_frame makes them, at her 1x tags' own scale
(ONE: her idle, attack and old run 1x frames are her hd_ ones at 1 / 1.5, not 1 / PPU - a run at 1 / 1.45 stood
4 % taller than her other 1x tags), the lo_ frames as tools/art/ppu_hd.py's add_lo does. Her frames feed no derived
art (illaoi_souls / hero_reels read other heroes).
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
import run_fix as F  # noqa: E402
import thin_outline as T  # noqa: E402

HERO = "league_caitlyn"
SOURCE = os.path.join(ROOT, "assets", "source", "caitlyn", "hd", "caitlyn_run_drawn")
OUT = (14, 0, 21)
ONE = 1.5                 # her hd_ squares a 1x pixel in her 1x tags (idle, attack, the old run: measured)
# one step down her ramps (light -> dark): boot browns, stocking navies, buckle golds
DARKER = {(135, 80, 35): (108, 61, 43), (108, 61, 43): (79, 42, 31), (79, 42, 31): (45, 32, 32),
          (40, 39, 98): (35, 33, 79), (35, 33, 79): (22, 12, 44),
          (251, 204, 74): (238, 175, 49), (238, 175, 49): (217, 152, 38), (217, 152, 38): (201, 132, 29),
          (201, 132, 29): (186, 119, 29), (186, 119, 29): (160, 97, 29), (160, 97, 29): (135, 80, 35)}
LEG = set(DARKER) | {(45, 32, 32), (22, 12, 44)}
# the far leg's squares in each frame: [((row0, row1), (col0, col1))] inclusive, frame squares, from the skirt's hem
FAR = {
    0: [((46, 49), (24, 34)), ((50, 58), (22, 33))],      # swinging back, kicked up (the planted leg from col 35)
    1: [((47, 48), (31, 33)), ((49, 51), (24, 32)), ((52, 60), (22, 31))],   # kicked up higher (its thigh's top
                                                                             # under the hem as frame 0's)
    2: [((47, 50), (34, 45)), ((51, 61), (33, 44))],      # folded, passing behind the planted leg
    3: [((47, 70), (51, 70))],                            # landed in front
    4: [((46, 69), (26, 42))],                            # planted under her (the near leg kicks back, cols < 26)
    5: [((47, 71), (40, 56))],                            # planted, the near leg passing behind (cols < 40)
    6: [((46, 56), (26, 45))],                            # lifting behind (the near leg planted from col 46)
}
# what shines on the rifle and the skirt's trim: their golds, creams and whites (a gold of FAR's that runs into these
# outside FAR is theirs, not a buckle of the leg's)
SHINE = {(251, 204, 74), (238, 175, 49), (217, 152, 38), (201, 132, 29), (186, 119, 29), (160, 97, 29),
         (247, 237, 206), (242, 221, 175), (251, 250, 251), (223, 227, 242), (196, 201, 229)}
HEAD = [(19, 0), (47, 0), (47, 16), (44, 17), (44, 28), (26, 28), (26, 17), (19, 17)]   # hd_idle_base[0] squares
EAR_COL, BRIM, CHIN = 26, 17, 28      # (idle squares) the ear's left edge, the brim's underside, the chin's bottom


def lp(path):
    return F.lp(path)


def drawn():
    """The source frames -> ([dense frames], [ms], [1x sizes], [lo sizes])."""
    with open(lp(SOURCE + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    px = np.asarray(Image.open(lp(SOURCE + ".png")).convert("RGBA"))
    out, x = [], 0
    for w, h in meta["sizes"]:
        out.append(px[:h, x:x + w].copy())
        x += w + 1
    return out, meta["ms"], meta["one"], meta["lo"]


def far_mask(a, i):
    m = np.zeros(a.shape[:2], bool)
    for (y0, y1), (x0, x1) in FAR[i]:
        m[y0:y1 + 1, x0:x1 + 1] = True
    leg = np.zeros(a.shape[:2], bool)
    for c in LEG:
        leg |= (a[..., :3] == np.array(c)).all(-1)
    far = m & leg & (a[..., 3] > 0)
    shine = colour_mask(a, SHINE)
    lab, n = ndimage.label(shine, structure=np.ones((3, 3)))
    for j in set(np.unique(lab[far & shine]).tolist()) - {0}:
        if ((lab == j) & ~m).sum() >= 3:
            far &= lab != j                             # the rifle's stock, the skirt's trim
    return far


def shaded(a, i):
    b = a.copy()
    for y, x in zip(*np.nonzero(far_mask(a, i))):
        c = tuple(int(v) for v in a[y, x, :3])
        if c in DARKER:
            b[y, x, :3] = DARKER[c]
    return b


def the_head(idle):
    """The standing frame's head -> (picture, mask, top-left in the idle frame): HEAD's squares joined to the head
    (not the bit of her rifle HEAD's corner takes in by the chin)."""
    m = F_poly(idle.shape, HEAD) & (idle[..., 3] > 0)
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    m = lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))
    ys, xs = np.nonzero(m)
    y0, x0 = ys.min(), xs.min()
    h = idle[y0:ys.max() + 1, x0:xs.max() + 1].copy()
    hm = m[y0:ys.max() + 1, x0:xs.max() + 1]
    h[~hm] = 0
    return h, hm, (int(x0), int(y0))


def F_poly(shape, pts):
    from PIL import ImageDraw
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    return np.asarray(img, bool)


def hat_anchor(a):
    """The hat's left edge and top (its purples)."""
    rgb = a[..., :3].astype(int)
    pur = (rgb[..., 0] - rgb[..., 1] > 20) & (rgb[..., 2] - rgb[..., 1] > 20) & (a[..., 3] > 0) & (rgb.sum(-1) > 120)
    top = np.nonzero(pur.any(1))[0][0]
    return int(np.nonzero(pur[top:top + 16].any(0))[0].min()), int(top)


def place(a, h, hm, at, idle):
    """Where the head goes in frame a: its hat on the frame's own hat (the best match within 3 squares of the hats'
    corners lining up)."""
    ix, iy = hat_anchor(idle)
    ax, ay = hat_anchor(a)
    bx, by = at[0] + ax - ix, at[1] + ay - iy
    rows = slice(0, BRIM - at[1])
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = bx + dx, by + dy
            if x < 0 or y < 0:
                continue
            sub = a[y:y + h.shape[0], x:x + h.shape[1]]
            if sub.shape[:2] != h.shape[:2]:
                continue
            same = (np.abs(sub[..., :3].astype(int) - h[..., :3].astype(int)).sum(-1) <= 30) & hm & (sub[..., 3] > 0)
            sc = same[rows].sum() + 50 * ((sub[..., 3] > 0) == hm)[rows].mean()
            if best is None or sc > best[0]:
                best = (sc, x, y)
    return best[1], best[2]


HAIR = {(22, 12, 44), (35, 33, 79), (40, 39, 98), (49, 41, 137), (64, 49, 168)}     # her hair's navies
# her own head's colours (cleared round the locked head): the outline, the hat's purples, the hair, skin, blush, mouth -
# never the rifle's golds, creams, whites or blues passing her face
HEADS = {OUT, (47, 12, 65), (59, 16, 86), (74, 25, 111), (87, 36, 144), (252, 207, 174), (244, 162, 125),
         (212, 115, 84), (208, 37, 56)} | HAIR


def hairish(c):
    return tuple(int(v) for v in c[:3]) in HAIR


def removable(c):
    """A square of the frame's own head round the locked one (HEADS)."""
    return tuple(int(v) for v in c[:3]) in HEADS


# the rifle's colours: its golds and creams (BODY), the scope's blues, its greys (not the whites: her collar's too)
BODY = {(251, 204, 74), (238, 175, 49), (217, 152, 38), (201, 132, 29), (186, 119, 29), (160, 97, 29), (135, 80, 35),
        (247, 237, 206), (242, 221, 175)}
RIFLE = BODY | {(97, 212, 241), (9, 185, 249), (8, 158, 237), (6, 111, 206), (6, 110, 190), (6, 73, 167),
                (3, 90, 109), (68, 111, 143), (134, 186, 165), (122, 113, 105), (85, 92, 27)}


def colour_mask(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == np.array(c)).all(-1)
    return m & (a[..., 3] > 0)


def rifle_over(a, full, top):
    """The rifle's squares inside the head's (with its outline there): where it passes in front of her chin. The
    rifle: a run of its colours with 8 or more squares out of the head below the brim (row `top`) and its golds in
    it - not the frame's own eyes inside its face, nor her collar's jewel."""
    m = colour_mask(a, RIFLE)
    gold = colour_mask(a, BODY)
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    out = ~full
    out[:top] = False
    big = [j for j in range(1, n + 1) if ((lab == j) & out).sum() >= 8 and ((lab == j) & gold).sum() >= 3]
    inside = np.isin(lab, big) & full
    ink = T.is_outline(a, [OUT]) & full & ndimage.binary_dilation(inside, structure=np.ones((3, 3)))
    return inside, inside | ink


def locked(a, h, hm, at, idle):
    """The frame with the one head -> (frame, the head's top-left, its squares, the rifle's squares over it)."""
    x, y = place(a, h, hm, at, idle)
    b = a.copy()
    full = np.zeros(a.shape[:2], bool)
    ys, xs = np.nonzero(hm)
    full[ys + y, xs + x] = True
    ear, brim, chin = EAR_COL - at[0], BRIM - at[1], CHIN - at[1]          # in the head's squares
    rifle, over = rifle_over(a, full, y + brim)
    head = full & ~over
    zone = ndimage.binary_dilation(full, iterations=3) & ~full & (a[..., 3] > 0)
    for yy, xx in zip(*np.nonzero(zone)):
        r, c = yy - y, xx - x
        if r >= chin:
            continue                                    # the neck, the collar: the body's
        if r >= brim and c < ear and (hairish(a[yy, xx]) or tuple(a[yy, xx, :3]) == OUT):
            continue                                    # her back hair behind the ear
        if removable(a[yy, xx]):
            b[yy, xx] = 0
    put = ~over[ys + y, xs + x]
    b[ys[put] + y, xs[put] + x] = h[ys[put], xs[put]]
    # the rifle in front of her chin: an outline on the head's side where it meets the rifle
    edge = head & ~T.is_outline(b, [OUT]) & ndimage.binary_dilation(rifle)
    b[edge, :3] = OUT
    # an edge the clearing bared (the rifle's by her face) closed again: 2 squares of outline on what was cleared
    cleared = zone & (b[..., 3] == 0)
    body = (b[..., 3] > 0) & ~T.is_outline(b, [OUT]) & ~head
    d = T.steps_from(body, np.ones(b.shape[:2], bool), 2)
    close = cleared & (d <= 2) & ndimage.binary_dilation(body & ndimage.binary_dilation(cleared), iterations=2)
    b[close, :3] = OUT
    b[close, 3] = 255
    # where the head meets her back hair: 2 squares of outline on the hair's side
    hb = head & ~T.is_outline(b, [OUT])
    d = T.steps_from(hb, np.ones(b.shape[:2], bool), 2)
    seam = np.zeros(b.shape[:2], bool)
    for yy, xx in zip(*np.nonzero((d >= 1) & (d <= 2) & (b[..., 3] > 0) & ~full)):
        if brim <= yy - y < chin and hairish(b[yy, xx]):
            seam[yy, xx] = True
    b[seam, :3] = OUT
    b[seam, 3] = 255
    # a pinhole of ground the head shut in between its outline and the rifle's (not one of her drawing's): outline
    shut = pockets(b) & ~pockets(a)
    if shut.any():
        lab, n = ndimage.label(shut)
        if max(ndimage.sum(shut, lab, range(1, n + 1))) > 3:
            sys.exit(f"{HERO}: the head shuts in a pocket of ground bigger than a pinhole")
        b[shut, :3] = OUT
        b[shut, 3] = 255
    return b, (x, y), head, over


def pockets(a):
    """The clear squares the figure shuts in (not reaching the frame's edge)."""
    lab, n = ndimage.label(a[..., 3] == 0)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return (lab > 0) & ~np.isin(lab, edge)


def make():
    """-> {"hd_run", "run", "lo_run": [(frame, ms)]} and per frame the far leg's and the head's squares."""
    import ppu_one
    import ppu_hd
    hid, pack, ppu, size = T.resolve(HERO, T.all_heroes())
    an, px = F.read_sheet(hid, pack)
    idle = F.frames_of(an, px, "hd_idle_base")[0][0]
    h, hm, at = the_head(idle)
    frames, ms, ones, los = drawn()
    dense, info = [], []
    for i, a in enumerate(frames):
        s = shaded(a, i)
        b, head_at, head, over = locked(s, h, hm, at, idle)
        dense.append(b)
        info.append({"far": far_mask(a, i), "head": head, "head_at": head_at, "rifle_over": over})
    one = []
    for b, (w, hh) in zip(dense, ones):
        ws = [w + 2 * k for k in range(6)]
        hs = [hh + 2 * k for k in range(6)]
        f, off = ppu_one.one_frame(b, w, hh, 1.0 / ONE, ws, hs)
        if off:
            sys.exit(f"{HERO}: a 1x frame loses {off} squares off its rect")
        one.append(f)
    mini = {"run": list(zip(one, ms)), "hd_run": list(zip(dense, ms))}
    ppu_hd.add_lo(hid.split("_", 1)[1], mini)
    return {"hd_run": list(zip(dense, ms)), "run": list(zip(one, ms)), "lo_run": mini["lo_run"]}, info


def strips(dense):
    """assets/source/ppu/caitlyn_run.png (+ .json) and its orig/ twin: these frames (tools/art/ppu_hd.py's strip)."""
    for folder in (os.path.join(ROOT, "assets", "source", "ppu"), os.path.join(ROOT, "assets", "source", "ppu", "orig")):
        png, js = (os.path.join(folder, "caitlyn_run." + e) for e in ("png", "json"))
        H = max(a.shape[0] for a in dense)
        out = np.zeros((H, sum(a.shape[1] + 1 for a in dense) - 1, 4), np.uint8)
        x = 0
        for a in dense:
            out[:a.shape[0], x:x + a.shape[1]] = a
            x += a.shape[1] + 1
        Image.fromarray(out, "RGBA").save(lp(png), optimize=True)
        meta = {}
        if os.path.exists(lp(js)):
            with open(lp(js), encoding="utf-8") as f:
                meta = json.load(f)
        meta["sizes"] = [[a.shape[1], a.shape[0]] for a in dense]
        with open(lp(js), "w", encoding="utf-8", newline="\n") as f:
            json.dump(meta, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    new, _ = make()
    hid, pack, _, _ = T.resolve(HERO, T.all_heroes())
    an, px = F.read_sheet(hid, pack)
    if a.check:
        bad = []
        for t, fr in new.items():
            cur = F.frames_of(an, px, t)
            if len(cur) != len(fr) or any(c[1] != m or not np.array_equal(c[0], f) for c, (f, m) in zip(cur, fr)):
                bad.append(t)
        if bad:
            sys.exit(f"{HERO}: {', '.join(bad)} not as tools/art/caitlyn_run_shade.py makes them")
        print(f"ok: {HERO} run tags as made")
        return
    if a.dry:
        print({t: len(v) for t, v in new.items()})
        return
    F.write(hid, pack, an, px, new)
    strips([f for f, _ in new["hd_run"]])
    print(f"{HERO}: run / hd_run / lo_run {len(new['hd_run'])} frames written")


if __name__ == "__main__":
    main()
