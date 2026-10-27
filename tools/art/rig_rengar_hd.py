#!/usr/bin/env python3
"""league_rengar redone at PPU 1.475 (the user, 2026-10-27: 「可以参考另外一个账号 利用PPU1.5重做一下狮子狗模型」): the
design is Codex's picture traced from his sprite (the hunched stalking crouch) read on its own squares
(tools/art/design_rengar_hd.py: 76 x 59, 「设计图通过」), every action Codex's whole-frame redraw of his old frame in its
old pose read onto it (tools/art/casts_rengar_hd.py: his head the design's size), tools/art/rig_leesin_hd.py's way.

What Codex did not draw (tools/art/pack_rengar_actions.py): the old frames that were his idle pose itself (SAME_DESIGN)
are the design; a frame that repeated another (SAME) repeats its drawing; idle_base breathes and R crouches as the old
sheet did - the design's upper body sunk over its feet (BREATH, ULT: the old sheet's sinks in 1x pixels, x PPU). The
idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py. Nothing is baked: the bola, the roar,
the slashes and the leap dust are effects of their own.

    python tools/art/rig_rengar_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_rengar_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero rengar && python tools/art/ppu_hd.py --hero rengar
    python tools/art/hero_reels.py --hero rengar       # then: the idle / ban-pick reels from idle_base
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_draven_hd as CD  # noqa: E402
import casts_rengar_hd as CS  # noqa: E402
import design_rengar_hd as DH  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402
import rigkit as K  # noqa: E402

HERO = "rengar"
PPU = CS.PPU
DESIGN_ROWS = 59
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
# (pack_rengar_actions) + dead 2: Codex drew the old frame 2 (still up, the claw flung out) already lying - his
# frame 3 (the same stagger) stands in for it, the fall from frame 4 as the old sheet's
SAME = {"dead": {2: 3, 7: 6, 8: 6}}
SAME_DESIGN = {"attack": [6], "leap": [8], "skill": [8], "skill2": [6], "skill_w": [2, 7]}
# the old sheet's sinks in 1x pixels: idle_base its breath, ult its crouch (= idle_base's sunk frames)
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]
ULT = [1, 2, 2, 1]
# The run (「走路两个腿不交换的 怎么看起来」): Codex's eight run frames all kept the far leg planted in front and the near
# leg lifted behind - the legs never took turns. Rebuilt as his old run, the trot the user picked (「不对选A 不用交叉步」,
# tools/art/rig_rengar.py): the design's lower legs swung about the knees in turn (rigkit.swing_leg: whole rows; the
# feet stand 12 columns apart, so front and back swap without crossing), each foot lifted while it swings forward, the
# body dipping as a foot lands, the arms swinging against the legs, the tail's end swaying - the old rig's numbers x PPU.
TROT_STRIDE = [4, 3, 0, -3, -4, -3, 0, 3]
TROT_LIFT = ([0, 3, 4, 3, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 4, 3])      # the near (image-left) foot, the far one
TROT_DROP = [1, 0, 0, 0, 1, 0, 0, 0]
TROT_ARM = [-3, -1, 0, 1, 3, 1, 0, -1]
TROT_TAIL = [-2, 0, 2, 0, -2, 0, 2, 0]
LEGS = ((49, 18, 41), (50, 41, 63))     # the lower legs: (knee row, first column, column past) near, far
ANKLE = 55                              # the feet: this row down
ARMS = ((27, 0, 22, 53), (27, 57, 999, 57))  # the claw arm, the blade arm: (elbow row, columns, lowest row)
BLADE_LOW = (46, 63)                    # from row 46 the blade arm is the blade only (columns 63 up): the far foot is not
FEET = (52, 18, 63)             # the design's feet: rows 52 down between columns 18 and 62 (the claw and the blade out)
# The tail (design_rengar_hd: Codex drew it in front of him, the user: 「怎么尾巴在手上？」「尾巴还是不对」). On the frames that
# copied the design's front tail it is taken off (FRONT_TAILS: the box round it on the cast picture, design_rengar_hd.
# untail) and every one of those frames gets the tail behind him: out of his hip (HIPS: a square inside his body at the
# back of the hip, read off each frame), down behind the near leg to the ground behind his back foot, along it to the
# gold ring and the tuft - the design's shape (tail_path); in the air it hangs as far under his hip as when he stands.
# Frames Codex already drew with the tail behind him (the leap's 2nd, 4th and 5th, the fall) keep theirs.
FRONT_TAILS = {
    "attack_1": (30, 50, 69, 82), "attack_2": (35, 55, 61, 75), "attack_3": (36, 56, 63, 77),
    "attack_4": (33, 54, 60, 73), "attack_5": (34, 48, 56, 69),
    "leap_1": (27, 44, 70, 82), "leap_3": (38, 56, 64, 82), "leap_6": (32, 46, 60, 73), "leap_7": (21, 40, 74, 92),
    "skill_1": (27, 44, 72, 85), "skill_2": (44, 66, 62, 77), "skill_3": (45, 63, 61, 76), "skill_4": (47, 64, 73, 87),
    "skill_5": (31, 47, 63, 81), "skill_6": (38, 56, 57, 73), "skill_7": (43, 56, 63, 77),
    "skill2_1": (25, 39, 64, 77), "skill2_2": (27, 42, 70, 83), "skill2_3": (29, 46, 63, 76),
    "skill2_4": (26, 42, 77, 91), "skill2_5": (29, 46, 64, 77),
    "skill_w_1": (30, 47, 71, 85), "skill_w_3": (39, 58, 65, 80), "skill_w_4": (40, 60, 70, 87),
    "skill_w_5": (40, 59, 64, 80), "skill_w_6": (27, 42, 60, 71),
    "hit_1": (23, 41, 68, 80), "hit_2": (23, 39, 69, 82), "dead_1": (48, 60, 49, 66),
}
HIPS = {
    "attack_1": (45, 24), "attack_2": (42, 20), "attack_3": (48, 25), "attack_4": (46, 24), "attack_5": (44, 25),
    "leap_1": (46, 27), "leap_3": (43, 32), "leap_6": (40, 24),
    "leap_7": (44, 26), "skill_1": (46, 26), "skill_2": (60, 24), "skill_3": (60, 24), "skill_4": (60, 28),
    "skill_5": (44, 25), "skill_6": (51, 22), "skill_7": (57, 26), "skill2_1": (45, 23), "skill2_2": (44, 26),
    "skill2_3": (51, 20), "skill2_4": (49, 30), "skill2_5": (50, 25), "skill_w_1": (52, 27), "skill_w_3": (51, 22),
    "skill_w_4": (52, 26), "skill_w_5": (52, 23), "skill_w_6": (43, 22), "hit_1": (45, 26), "hit_2": (44, 25),
    "dead_1": (47, 22),
}
HANG = 16                       # rows from his hip down to the ground the tail lies on (the design's: 43 -> 59)


def tail_path(hip, ground):
    """The design's tail from hip (row, column) to the ground row: down behind the near leg, then along the ground."""
    r, c = hip
    return [(r, c), (r + 5, c - 5), (ground - 6, c - 8), (ground - 3, c - 10), (ground - 2.4, c - 16),
            (ground - 2.8, c - 22)]


def casts():
    """casts_rengar_hd's frames, the tail behind him (retail)."""
    return {n: retail(n, *c) for n, c in CS.placed().items()}


def retail(n, pic, x, y):
    """A cast (picture, x, y on the design's grid) with its front tail off and the tail drawn behind him."""
    if n not in HIPS:
        return pic, x, y
    q = DH.untail(pic, FRONT_TAILS[n]) if n in FRONT_TAILS else pic
    P = 30
    big = np.zeros((q.shape[0] + 2 * P, q.shape[1] + 2 * P, 4), np.uint8)
    big[P:P + q.shape[0], P:P + q.shape[1]] = q
    soles = CS.GROUND - y                                   # the soles' row on the picture
    r, c = HIPS[n]
    ground = soles if y + pic.shape[0] >= CS.GROUND else min(soles, r + HANG)
    big = DH.tail(big, [(a + P, b + P) for a, b in tail_path((r, c), ground)], ground=soles + P)
    ys, xs = np.nonzero(big[..., 3] > 0)
    return big[ys.min():ys.max() + 1, xs.min():xs.max() + 1], x + int(xs.min()) - P, y + int(ys.min()) - P


def lp(path):
    return R.lp(path)


def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.d0 = D.d.copy()
    D.bare = DH.bare()                              # no tail: the sunk frames draw it, the root sinking with him
    D.px = int(round(CD.shoes_mid(D.bare)))         # between his feet (the tail's end lies on the ground behind them)
    if (DH.tail(D.bare, DH.BACK, ground=d.shape[0]) != d).any():
        sys.exit("design_rengar_hd's bare design + tail is not hd/design.png")
    return D


def drop_specks(can, most=4):
    """Bits of up to `most` squares cut off from the figure: gone."""
    out = can.copy()
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] <= most:
                out[lbl == k] = 0
    return out


class RengarRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


def on_grid(rig, d, x, y):
    """A picture whose top-left square sits at (x, y) on the design's grid, on the rig's canvas."""
    ys, xs = np.nonzero(d[..., 3] > 0)
    can = rig.canvas()
    Y, X = ys + y + rig.oy, xs + x + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    if not ok.all():
        sys.exit(f"{int((~ok).sum())} squares off the canvas")
    if Y.max() >= rig.GY:
        sys.exit("a frame reaches under his soles' row")
    can[Y, X] = d[ys, xs]
    return can


def sunk(D, rows):
    """The design's body `rows` squares lower with the feet where they stand (drawn over it), nothing under the soles;
    the tail drawn on it, its root sunk with him, its end where it lay."""
    if rows == 0:
        return D.d0.copy()
    d = D.bare
    h = d.shape[0]
    out = np.zeros_like(d)
    out[rows:] = d[:h - rows]
    r0, c0, c1 = FEET
    feet = np.zeros(d.shape[:2], bool)
    feet[r0:, c0:c1] = d[r0:, c0:c1, 3] > 0
    out[feet] = d[feet]
    back = [(r + rows, c) if i < 2 else (r + rows / 2, c) if i == 2 else (r, c) for i, (r, c) in enumerate(DH.BACK)]
    return DH.tail(out, back, ground=h)


def trot(D, k):
    """Run frame k: the tail-less design's lower legs swung and lifted (TROT_*), the arms swung, the rest dipped, the
    tail drawn behind it (its root with him, its end swaying)."""
    b = D.bare
    h, w = b.shape[:2]
    op = b[..., 3] > 0
    R_, C_ = np.mgrid[0:h, 0:w]
    legs = [op & (R_ >= kr) & (C_ >= c0) & (C_ < c1) for kr, c0, c1 in LEGS]
    arms = [op & (R_ >= er) & (C_ >= c0) & (C_ < c1) for er, c0, c1, _ in ARMS]
    arms[1] &= ~((R_ >= BLADE_LOW[0]) & (C_ < BLADE_LOW[1]))
    top = b.copy()
    top[legs[0] | legs[1] | arms[0] | arms[1]] = 0
    for m, (er, _, _, low), sign in zip(arms, ARMS, (-1, 1)):
        K.put(top, K.swing_leg(b, m, er, low, sign * TROT_ARM[k]), 0, 0)
    feet = np.zeros_like(b)
    for m, (kr, _, _), sign, lift in zip(legs, LEGS, (-1, 1), TROT_LIFT):
        K.put(feet, K.swing_leg(b, m, kr, ANKLE, sign * TROT_STRIDE[k], lift[k]), 0, 0)
    c = K.put(K.shifted(top, 0, TROT_DROP[k]), feet, 0, 0, under=True)
    c[h:] = 0
    back = [(r + TROT_DROP[k], c_) if i < 2 else (r, c_ + TROT_TAIL[k] * (i - 1) / 4) for i, (r, c_) in enumerate(DH.BACK)]
    return DH.tail(c, back, ground=h)


def frames(rig, casts):
    sheet = R.sheet_of(HERO)
    d0 = rig.D.d0
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag == "idle_base":
            fr = [on_grid(rig, sunk(rig.D, round(s * PPU)), 0, 0) for s in BREATH]
        elif tag == "ult":
            fr = [on_grid(rig, sunk(rig.D, round(s * PPU)), 0, 0) for s in ULT]
        elif tag == "run":
            fr = [on_grid(rig, trot(rig.D, k), 0, 0) for k in range(n)]
        else:
            fr = []
            for k in range(1, n + 1):
                if k in SAME_DESIGN.get(tag, []):
                    fr.append(on_grid(rig, d0, 0, 0))
                else:
                    fr.append(on_grid(rig, *casts[f"{tag}_{SAME.get(tag, {}).get(k, k)}"]))
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        if len(fr) != n:
            sys.exit(f"{tag}: {len(fr)} frames for the sheet's {n}")
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = list(out["idle_base"])
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    cs = casts()
    rig = RengarRig(D, pad=pad_for(D, cs))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
