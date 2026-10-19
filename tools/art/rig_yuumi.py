#!/usr/bin/env python3
"""league_yuumi's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way: no
Codex strips, lossless poses compared with League's clips).

    python tools/art/rig_yuumi.py --parts DIR       # the designs with the idle's head pasted on (12x)
    python tools/art/rig_yuumi.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_yuumi.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_yuumi.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/rig_yuumi.py --ride-tags       # after ppu_restyle / ppu_hd: the add-on's blank a_* tags

The pipeline: this (no flags) -> ppu_restyle.py --hero yuumi -> ppu_hd.py --hero yuumi -> this --ride-tags (the rig's
export writes the sheet without them, so the restyle never sees a blank frame; ppu_hd rebuilds their hd_ / lo_ copies
blank if it runs again).

The designs (tools/art/design_yuumi_model.py, the user's picks 2026-10-19; 32 game px at PPU 1.5, one palette):
idle.png (A-2, 3/4 front in the open book, 45 x 48), side.png (S-1, side-on in the book, 46 x 48: the run's base),
leap.png (L-2, out of the book stretched long, 51 x 42), ult.png (R-2, the book standing upright, the cat clinging to
it, 31 x 45) and book.png (C-1, the closed book, 39 x 27). League's Yuumi has no legs to run on: she rides the book
(Run01), leaps out of it to strike (Attack01, Spell1 / Spell3_detached), stands it up for Final Chapter (Spell4_in)
and dives into it as it shuts and drops (Death01) - so every pose here is a whole design moved by whole squares, a
quarter turn or a mirror.
One face in every frame (the user's rule): the side, the leap and the ult carry the idle's 3/4 head - the idle's head
(rows 0..its chin, from IDLE_HEAD_X right) laid with its chin and face middle on theirs (HEADS), their own head cleared
above their chin only (their neck, collar, ruff and paws below it stay), then every square the paste left open between
the new head and the body (a hole, or a dent the design did not have) given back its own square, again until none is
left (the first try cleared to below the chin and left a clear row under the leap's head: 「头和身体分离了？」). The side
design is the rig's own (its standing point: the middle of the book's bottom); the others stand on the same point and
ground.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet  # noqa: E402

HERO = "yuumi"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "yuumi", "hd")

# the idle's head: rows 0..its chin (IDLE_CHIN y: the white muzzle's lowest row) from column IDLE_HEAD_X (the tail's
# tuft lies left of it); IDLE_CHIN x is the face's middle
IDLE_HEAD_X, IDLE_CHIN = 16, (32, 24)
# each design's own chin (x: the face's middle, y: the white muzzle's lowest row) and the first column of its head
HEADS = {"side": ((35, 24), 16), "leap": ((40, 25), 19), "ult": ((18, 19), 6)}
NECK = 6                                # rows above / below a design's chin where the paste's openings are closed


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def stand_col(d, rows=3):
    """The middle of the lowest `rows` rows' squares: where the design stands."""
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


def idle_head():
    d = load("idle.png")
    h = np.zeros_like(d)
    h[:IDLE_CHIN[1] + 1, IDLE_HEAD_X:] = d[:IDLE_CHIN[1] + 1, IDLE_HEAD_X:]
    return h


def openings(a):
    """Clear squares closed in by the figure: holes, and dents (three or four of the four neighbours opaque)."""
    from scipy import ndimage
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    n = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    return (ndimage.binary_fill_holes(op) & ~op) | (~op & (n >= 3))


def with_head(name):
    """A design with the idle's head laid on at its chin (grown on the left / top when the head sticks out)."""
    d = load(f"{name}.png")
    (cx, cy), col = HEADS[name]
    dx, dy = cx - IDLE_CHIN[0], cy - IDLE_CHIN[1]
    h = idle_head()
    top, left = max(0, -dy), max(0, -dx)
    H = max(d.shape[0] + top, h.shape[0] + dy + top)
    W = max(d.shape[1] + left, h.shape[1] + dx + left)
    own = np.zeros((H, W, 4), np.uint8)
    own[top:top + d.shape[0], left:left + d.shape[1]] = d
    out = own.copy()
    out[:top + cy + 1, left + col:] = 0                  # its own head, down to its chin
    ys, xs = np.nonzero(h[..., 3] > 0)
    out[ys + dy + top, xs + dx + left] = h[ys, xs]
    # where the paste left the figure open between the new head and the body, the design's own squares come back:
    # only round the chin (NECK rows above it to NECK below) and never inside the idle head's own openings (the
    # antenna's loop: filling it closed the loop with the old head's squares)
    head = np.zeros_like(out)
    head[ys + dy + top, xs + dx + left] = h[ys, xs]
    keep_open = openings(own) | openings(head)
    band = np.zeros(out.shape[:2], bool)
    band[max(0, top + cy - NECK):top + cy + NECK + 1] = True
    for _ in range(8):
        back = openings(out) & ~keep_open & band & (own[..., 3] > 0) & (out[..., 3] == 0)
        if not back.any():
            break
        out[back] = own[back]
    out = drop_islands(orphan_outline(out))
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def orphan_outline(a, dark=70):
    """Outline squares of the cleared head left touching no coloured square (4-neighbours): a lone ear edge."""
    op = a[..., 3] > 0
    ink = op & (a[..., :3].astype(int).sum(-1) < dark)
    col = op & ~ink
    near = np.zeros_like(col)
    near[1:] |= col[:-1]
    near[:-1] |= col[1:]
    near[:, 1:] |= col[:, :-1]
    near[:, :-1] |= col[:, 1:]
    out = a.copy()
    out[ink & ~near] = 0
    return out


def drop_islands(a, most=12):
    """Bits of the cleared head the idle's head did not cover (an ear's outline, a lock of the circlet): pieces of at
    most `most` squares standing apart from the figure (8-neighbours) are taken off."""
    from scipy import ndimage
    op = a[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n < 2:
        return a
    size = ndimage.sum(op, lbl, range(1, n + 1))
    out = a.copy()
    for k, sz in enumerate(size, 1):
        if sz <= most:
            out[lbl == k] = 0
    return out


def design():
    d = with_head("side")
    D = CutDesign(d, px=stand_col(d))
    D.part("body", D.rest())
    return D


class Form:
    """The designs placed on the side design's standing point and ground; whole() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {"side": pad(D.d)}
        self.L |= {"idle": self.placed(load("idle.png")), "leap": self.placed(with_head("leap")),
                   "ult": self.placed(with_head("ult")), "book": self.placed(load("book.png"))}

    def placed(self, d):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(d)
        y0, x0 = max(0, top), max(0, left)
        lay[y0:top + d.shape[0], x0:left + d.shape[1]] = d[y0 - top:, x0 - left:]
        return lay

    def whole(self, name, dx=0, dy=0, rot=0, flash=False):
        """A design moved dx, dy (dy < 0: up), turned rot quarter turns counter-clockwise about its own middle."""
        lay = self.L[name]
        if rot % 4:
            ys, xs = np.nonzero(lay[..., 3] > 0)
            sub = lay[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            t = np.rot90(sub, rot % 4)
            lay = np.zeros_like(lay)
            cy, cx = (ys.min() + ys.max() + 1) // 2, (xs.min() + xs.max() + 1) // 2
            # turned about its middle, then stood back on the ground
            y0 = ys.max() + 1 - t.shape[0]
            x0 = cx - t.shape[1] // 2
            lay[y0:y0 + t.shape[0], x0:x0 + t.shape[1]] = t
        can = R.compose(self.rig, [(lay, dict(dx=dx, dy=dy))])
        return R.flash(can) if flash else can

    ref_holes = None
    close_holes = _Form.close_holes
    MOST = _Form.MOST


def form():
    return Form(design(), rig_pad=(40, 60, 70, 20))


# ms per frame; the kit's ticks (tools/kit/build_yuumi.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [60, 70, 90, 80, 80, 100],
      "skill": [60, 70, 80, 80, 80, 90], "skill2": [60, 60, 60, 120], "w_off": [70, 70, 80, 100],
      "ult": [60, 80, 100, 130, 130], "hit": [100, 100], "dead": [100, 100, 100, 100, 80, 80, 100, 500]}


def frames_all(F):
    w = F.whole
    out = {}
    # idle (League's Idle01: she sits in the open book as it floats): the 3/4 design floating up a row and down
    out["idle"] = [w("idle", dy=d) for d in (0, 0, 0, -1, -1, -1, -1, 0)]
    # run (League's Run01: she rides the flying book, rising and dipping)
    out["run"] = [w("side", dy=d) for d in (0, -1, -2, -2, -1, 0, -1, -1)]
    # auto attack (League's Attack01: she springs out of the book, stretched long at the target, and drops back in):
    # sitting, the leap up and forward, the reach (the bolt leaves, frame 3), coming back, settling
    out["attack"] = [w("side"), w("leap", dx=2, dy=-4), w("leap", dx=4, dy=-6), w("leap", dx=2, dy=-3),
                     w("side", dy=-1), w("side")]
    # Q Prowling Projectile (League's Spell1_detached: she leaps high out of the book, flicks the missile from the top
    # of the jump and comes down onto it): up, the top (the flick, frame 3), down, landing - the leap never turned
    # (a quarter turn laid her face on its side)
    out["skill"] = [w("side"), w("leap", dx=1, dy=-7), w("leap", dx=2, dy=-13), w("leap", dx=1, dy=-8),
                    w("side", dy=-3), w("side")]
    # W You and Me! (League's Spell2_Attach_in: she flies stretched long at the ally): leaving to the right
    out["skill2"] = [w("side"), w("leap", dx=3, dy=-2), w("leap", dx=8, dy=-3), w("leap", dx=14, dy=-2)]
    # the jump off at the end of the attach (League's Spell2_Detach_out: down out of the air into the book)
    out["w_off"] = [w("leap", dx=-3, dy=-8), w("leap", dx=-1, dy=-3), w("side", dy=-1), w("side")]
    # R Final Chapter (League's Spell4_in: she hops up, the book stands on end, she clings to its top)
    out["ult"] = [w("side"), w("side", dy=-3), w("ult", dy=-2), w("ult"), w("ult")]
    out["hit"] = [w("idle", dx=-2, flash=True), w("idle", dx=-1)]
    # the death (League's Death01: she dives into the book, it snaps shut and drops): a hop, gone into the closed book
    # high up, falling, on the ground, a bounce, lying
    out["dead"] = [w("side"), w("side", dy=-3), w("book", dy=-12), w("book", dy=-6), w("book"), w("book", dy=-2),
                   w("book"), w("book")]
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


# the add-on's riding body (addons/league_yuumi/src/view.rs FORM_TAGS): while she rides an ally every action of hers is
# drawn from a_<tag> - blank: the cat on his head is the buff picture league_yuumi_w_ride on him
RIDE_TAGS = ["idle", "run", "hit", "attack", "skill", "skill2", "w_off", "ult", "dead"]


def ride_tags():
    """a_<tag>, hd_a_<tag>, lo_a_<tag> for every RIDE_TAGS tag: one clear frame the size of the tag's first frame, as long
    as the whole tag, written into the finished sheet."""
    import ppu_hd as PH
    import strips as G
    stem = os.path.join(R.ROOT, "league", "champions", f"league_{HERO}")
    sheet = PH.read_sheet(stem)
    ride = {pre + "a_" + t for t in RIDE_TAGS for pre in ("", PH.PREFIX, PH.LO)}
    for t in [t for t in sheet if t in ride]:
        del sheet[t]
    for t in RIDE_TAGS:
        for pre in ("", PH.PREFIX, PH.LO):
            src = sheet[pre + t]
            sheet[pre + "a_" + t] = [(np.zeros_like(src[0][0]), sum(ms for _, ms in src))]
    w, h = G.write_sheet(stem, sheet)
    print(f"league/champions/league_{HERO}#sheet.png {w}x{h}: + blank a_* / hd_a_* / lo_a_* for {', '.join(RIDE_TAGS)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ride-tags", action="store_true")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if a.ride_tags:
        ride_tags()
        return
    if not (a.audit or a.review or a.parts):
        F = form()
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            import rig_wukong as RW
            RW.HERO = HERO
            RW.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    F = form()
    t = [F.rig.finish(F.whole(n)) for n in ("idle", "side", "leap", "ult", "book")]
    sheet(t, os.path.join(a.parts, f"{HERO}_heads.png"), z=8)


if __name__ == "__main__":
    main()
