#!/usr/bin/env python3
"""league_karthus's action frames posed from the approved designs' own squares (the user, 2026-10-20: 「动作帧你参考其他
英雄怎么做的 不太需要依赖codex 做完美了喊我review」 - league_zoe's / league_swain's way: no Codex strips, lossless poses
compared with League's clips, tools/lol/anim_graph.py Karthus + pose_ref.py).

    python tools/art/rig_karthus.py --parts DIR       # the side design with its parts tinted + pose tries (12x)
    python tools/art/rig_karthus.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_karthus.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_karthus.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_karthus_model.py, the user's picks 2026-10-20: A-1 and side-1, 40 game px crown to soles
at PPU 1.5 = 60 rows, the staff 6 rows over the crown; one palette, one head, one staff): idle.png (3/4 front, 39 x 66)
and side.png (side-on facing right with the idle's 3/4 head, 44 x 66: every action's base). Every pose is lossless:
parts cut square by square from a design and only moved by whole squares, quarter turns about half-integer pivots and
mirrors.
Parts of the side design: the staff (the shaft from column STAFF_X, the crystal and its crimson bar), the far hand
gripping it (HAND: drawn over the staff, the shaft's squares under it go with it), the far sleeve reaching to it
(FAR_ARM), the near arm (the grey bracer and the bony claw hanging behind his hip: NEAR_ARM, by its colours - the robe's
reds and purples round it stay), the hem (rows from HEM: the ragged robe and the feet); the rest is the body.
League's Karthus floats: his run is a glide (the robe trailing, no steps), his casts lift the staff or fling a hand.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet  # noqa: E402

HERO = "karthus"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "karthus", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def stand_col(d, staff_x, rows=4):
    """Where the design stands: the middle between his two bony feet (the bone-coloured squares of the lowest `rows`
    rows left of the staff - the robe's rags reach much further back than his feet)."""
    rgb = d[..., :3].astype(int)
    bone = (d[..., 3] > 0) & (rgb[..., 0] > 120) & (np.abs(rgb[..., 0] - rgb[..., 1]) < 20) & (rgb[..., 2] > 90)
    bone[:, staff_x:] = False
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    xs = np.nonzero(bone[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


# ------------------------------------------------------------------------------------------------- the side's parts
STAFF_X = 34                          # the staff: every square from this column (its crimson bar reaches 32 on rows 9-11)
BAR = (9, 11, 32)
HAND = (35, 41, 34, 42)               # rows / columns of the far hand round the shaft
FAR_ARM = (36, 41, 31, 33)            # the far sleeve from the robe to the hand
GRIP = (38.5, 38.5)                   # the staff turns about the hand's middle (the shaft's column 38)
NEAR_ARM = (38, 52, 11, 18)           # the near bracer and claw, by colour (ARM_COLS)
ELBOW = (13.5, 38.5)                  # the near arm turns about its top
HEM = 50                              # the robe's hem: rows from here sway in the glide
IDLE_STAFF_X = 31                     # the idle design's staff (columns from here, but its hand's rows)
IDLE_HAND = (35, 39)
IDLE_LEG_ROW = 46                     # the idle design's robe from this row stays while the body breathes
ISLAND = 8
SHADE_PURPLE = (50, 22, 80)           # the design's darkest purple
# Requiem's book, open (League's: a crimson leather tome, its pages lit by a teal rune), in the design's own colours:
# K outline, A / B the pages light / shade, E the rune's cyan, R / D the cover's crimson light / dark
BOOK = [".KKK.KKK.",
        "KAAAKAAAK",
        "KAEAKAEAK",
        "KABAKABAK",
        "KRRRRRRRK",
        ".KDDDDDK."]
BOOK_INK = {"K": (6, 1, 10), "A": (218, 218, 184), "B": (167, 166, 127), "E": (7, 234, 247), "R": (187, 3, 39),
            "D": (130, 1, 30)}


def arm_colours(d):
    """The near arm's squares: the outline, the bracer's greys and the claw's bone (not the robe's reds and purples)."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    red = (r > 80) & (g < 20)
    purple = (b > r + 25) & (g < 60)
    return ~red & ~purple


def design():
    d = load("side.png")
    D = CutDesign(d, px=stand_col(d, STAFF_X))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    D.part("hand", D.box(*HAND[:2], *HAND[2:]))
    staff = ((xx >= STAFF_X) | ((yy >= BAR[0]) & (yy <= BAR[1]) & (xx >= BAR[2]))) & (d[..., 3] > 0)
    D.part("staff", staff & ~D.parts["hand"])
    D.part("far_arm", D.box(*FAR_ARM[:2], *FAR_ARM[2:]))
    D.part("near_arm", D.box(*NEAR_ARM[:2], *NEAR_ARM[2:]) & arm_colours(d))
    D.part("hem", D.box(HEM, D.H - 1, 0, STAFF_X - 1) & ~D.parts["near_arm"])
    D.part("body", D.rest())
    return D


TINT = {"staff": (255, 60, 60), "hand": (255, 220, 0), "far_arm": (0, 220, 120), "near_arm": (60, 120, 255),
        "hem": (255, 0, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def sway_rows(layer, y0, dx):
    """The rows from y0 down moved whole, the lowest dx columns, less up to y0 (a hem trailing)."""
    if not dx:
        return layer
    out = layer.copy()
    H = layer.shape[0]
    n = max(1, H - P - 1 - y0)
    for y in range(y0, H):
        d = int(round(dx * min(1.0, (y - y0 + 1) / n)))
        if not d:
            continue
        row = layer[y]
        out[y] = 0
        if d > 0:
            out[y, d:] = row[:-d]
        else:
            out[y, :d] = row[-d:]
    return out


class Form:
    """The designs' layers; pose() / front() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.idle = self.placed(load("idle.png"))
        self._staff = {}

    def placed(self, d):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(d, IDLE_STAFF_X)
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        lay[top:top + d.shape[0], x0:x1] = d[:, x0 - left:x1 - left]
        self.idle_left, self.idle_top = left, top
        return lay

    def pose(self, crouch=0, whole=(0, 0), staff=(0, 0), staff_rot=0, reach=0, near=(0, 0), near_rot=0, hem=0,
             fill=True, staff_back=False, drop=None, book=None, no_staff=False, lean=0):
        """crouch: rows the body (with the arms and the staff) sets down onto the hem; whole: the whole figure; staff:
        the staff, its hand and the far sleeve moved (dx, dy), staff_rot quarter turns counter-clockwise about GRIP
        (3: its crystal points forward, level through the fist; 1: back); reach: columns the hand (and the staff) goes
        forward of the sleeve, the sleeve's last column repeated into the gap (Cassiopeia's reach: the hand never leaves
        its forearm); near: the near arm moved, near_rot quarter turns counter-clockwise about ELBOW (1: forward, 2: up);
        hem: columns the hem's lowest row trails (negative: back); staff_back: the staff behind the body (turned
        level, its foot end passes behind him); drop: (quarter turns, dx, dy) - the staff let go, put down on its own
        (the hand stays an empty fist where `staff` puts it); book: (x, y) of Requiem's book's top left in design
        squares (moved with the body), drawn over everything (held in the near claw); no_staff: the staff left out
        (the death lays it down on its own); lean: the upper body bent forward over the hem one square every `lean`
        rows (league_zoe's leant: the head - the crown to the chin, rows to HEAD_LOW - one block, the hand's rows one
        block with the staff, which moves whole: nothing on it sheared)."""
        if crouch < 0:
            raise ValueError("the body never lifts off the hem")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        sx, sy = ux + staff[0], uy + staff[1]
        L = self.L
        hem_l = sway_rows(L["hem"], P + HEM, hem) if hem else L["hem"]
        sleeve = self.sleeve(reach)
        if drop is not None:
            k, ddx, ddy = drop
            staff_l = (L["staff"], dict(dx=ddx, dy=ddy, rot=k, about=GRIP))
            behind = True
        else:
            staff_l = (L["staff"], dict(dx=sx + reach, dy=sy, rot=staff_rot, about=GRIP))
            behind = staff_back or staff_rot % 4
        layers = [(hem_l, dict(dx=wx, dy=wy), "hem")]
        if no_staff:
            behind, staff_l = True, None
        if behind and staff_l:
            layers.append((*staff_l, "staff"))
        layers += [(L["body"], dict(dx=ux, dy=uy), "upper"),
                   (L["near_arm"], dict(dx=ux + near[0], dy=uy + near[1], rot=near_rot, about=ELBOW), "upper")]
        if not behind and staff_l:
            layers.append((*staff_l, "staff"))
        layers += [(sleeve, dict(dx=sx, dy=sy), "upper"),
                   (L["hand"], dict(dx=sx + reach, dy=sy, rot=staff_rot if drop is None else 0, about=GRIP), "hand")]
        if book is not None:
            layers.append((self.book_layer(book), dict(dx=ux, dy=uy), "upper"))
        moved = near != (0, 0) or near_rot % 4
        if lean:
            can = self.rig.canvas()
            top = self.rig.oy + uy
            for lay, o, group in layers:
                one = R.compose(self.rig, [(lay, o)])
                if group == "upper":
                    one = leant(one, top, lean)
                elif group in ("staff", "hand") and drop is None and not no_staff:
                    one = shift(one, lean_at(GRIP[1], lean), 0)
                m = one[..., 3] > 0
                can[m] = one[m]
        else:
            can = R.compose(self.rig, [(lay, o) for lay, o, _ in layers])
        if moved:
            if fill:
                can = self.behind_arm(can, ux, uy)
            can = drop_islands(can)
        return self.close_holes(can) if fill else can

    def book_layer(self, at):
        """Requiem's book (League's Karthus sings from it: Spell4_In takes it out, spell4_loop holds it up), open, its
        top left at design square `at`: BOOK's rows in the design's own colours."""
        lay = np.zeros_like(self.L["body"])
        x0, y0 = at
        for j, row in enumerate(BOOK):
            for i, ch in enumerate(row):
                if ch != ".":
                    lay[P + y0 + j, P + x0 + i] = (*BOOK_INK[ch], 255)
        return lay

    def behind_arm(self, can, ux, uy):
        """Where the near arm hung and the frame is now clear inside the figure: the robe behind it in its shade, the
        rags' darkest purple (spreading the squares round it, fill_under, ran the crimson sleeve down into a red block;
        taking each row's neighbour drew stripes; the sleeve's dark crimson over the top rows read as a red patch)."""
        rig = self.rig
        m = np.zeros(can.shape[:2], bool)
        m[rig.oy + uy:rig.oy + uy + self.D.H, rig.ox + ux:rig.ox + ux + self.D.W] = self.D.parts["near_arm"]
        op = can[..., 3] > 0
        hole = m & ~op & ndimage.binary_fill_holes(op | m)
        out = can.copy()
        out[hole] = (*SHADE_PURPLE, 255)
        return out

    def sleeve(self, reach):
        """The far sleeve, its last column (next to the hand) repeated `reach` times."""
        if not reach:
            return self.L["far_arm"]
        lay = self.L["far_arm"].copy()
        y0, y1, x0, x1 = FAR_ARM
        last = lay[P + y0:P + y1 + 1, P + x1].copy()
        for k in range(1, reach + 1):
            lay[P + y0:P + y1 + 1, P + x1 + k] = last
        return lay

    def front(self, crouch=0, whole=(0, 0), flash=False):
        """The 3/4 idle design, its body (above IDLE_LEG_ROW, not the staff) set down `crouch` rows onto its own robe;
        the hand slides down the staff with it."""
        lay = self.idle
        legs, top, staff = lay.copy(), lay.copy(), lay.copy()
        yy, xx = np.mgrid[0:lay.shape[0], 0:lay.shape[1]]
        sx = self.idle_left + IDLE_STAFF_X
        hand = (yy >= self.idle_top + IDLE_HAND[0]) & (yy <= self.idle_top + IDLE_HAND[1])
        is_staff = (xx >= sx) & ~hand
        legs[(yy < P + IDLE_LEG_ROW) | is_staff] = 0
        top[(yy >= P + IDLE_LEG_ROW) | is_staff] = 0
        staff[~is_staff] = 0
        wx, wy = whole
        can = R.compose(self.rig, [(legs, dict(dx=wx, dy=wy)), (staff, dict(dx=wx, dy=wy)),
                                   (top, dict(dx=wx, dy=wy + crouch))])
        return R.flash(can) if flash else can

    ref_holes = None
    close_holes = _Form.close_holes                   # small enclosed holes the side lacks, filled (league_wukong)
    MOST = _Form.MOST


def drop_islands(can, most=ISLAND):
    op = can[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n < 2:
        return can
    out = can.copy()
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    for k, sz in enumerate(sizes, 1):
        if sz <= most:
            out[lbl == k] = 0
    return out


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


HEAD_LOW = 29                         # the head's lowest row (the jaw, the hair under it): a lean moves it as one block


def lean_at(y, per):
    """Columns a design row moves forward in a lean of one square every `per` rows above the hem."""
    ref = max(int(y), HEAD_LOW)
    return (HEM - ref) // per if ref < HEM else 0


def leant(can, oy, per):
    """The upper body (a canvas; the design's top at canvas row oy) bent forward over the hem on an even line, no square
    resampled (league_zoe's leant): every row above HEM forward lean_at() of its design row, the head as one block, the
    hand's rows (HAND) as one block at the grip's amount (they move with the staff)."""
    out = np.zeros_like(can)
    for y in range(can.shape[0]):
        r = y - oy
        sh = lean_at(GRIP[1] if HAND[0] <= r <= HAND[1] else r, per)
        if sh > 0:
            out[y, sh:] = can[y, :-sh]
        else:
            out[y] = can[y]
    return out


def form():
    F = Form(design(), rig_pad=(50, 70, 50, 20))
    F.rig.idle_canvas = F.pose()
    return F


def tries(F):
    p = F.pose
    return [p(), p(staff_rot=3, reach=2), p(staff=(0, -4)), p(near_rot=1), p(near_rot=2), p(hem=-2),
            F.front(), F.front(crouch=1)]


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_karthus.py) come from these
MS = {"idle": [160] * 8, "run": [110] * 8,
      "attack": [80, 80, 70, 90, 80, 70], "attack_w": [80, 80, 80, 90, 90, 60],
      "skill": [60, 70, 90, 90, 80, 60], "skill2": [70, 80, 90, 90, 70],
      "ult": [110, 110, 110] + [210] * 12 + [150], "hit": [100, 100],
      "dead": [100, 110, 130, 160, 120, 120, 120, 500]}
STAFF_UP = (0, -6)                     # the staff (with the hand and the sleeve) at shoulder height
# Requiem's book: over the near claw held forward at chest height (near_rot 1, near NEAR_BOOK), or up behind his head
# (near_rot 2, near NEAR_HIGH: the claw at design square (8, 23))
BOOK_AT, NEAR_BOOK = (23, 29), (0, -3)
BOOK_HIGH, NEAR_HIGH = (4, 17), (-5, -2)
RISE = 14                              # Requiem's hover: rows off the ground (League rises about a third of his height)


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle (League's Karthus_Idle01: a slow breath, the staff still): the 3/4 design's body sets down a row onto its robe
    out["idle"] = [F.front(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # auto attack (League's karthus_attack1, 2026-10-20 frame by frame: 0-350 ms the staff held level at his shoulder,
    # the crystal aimed forward; 438 ms thrust forward and down - the bolt leaves; 525-612 ms swung back up, upright and
    # raised; then the idle): aimed level at the shoulder (two frames, the hand easing out), thrust lower and further
    # (frame 3: the bolt leaves the crystal), held, upright raised, the idle
    out["attack"] = [p(staff=STAFF_UP, staff_rot=3, reach=1), p(staff=STAFF_UP, staff_rot=3, reach=2),
                     p(staff=(0, -1), staff_rot=3, reach=4, crouch=1), p(staff=(0, 0), staff_rot=3, reach=3, crouch=1),
                     p(staff=(0, -3)), p()]
    # W Wall of Pain in the attack (League's Karthus_Spell2: 0 ms the staff upright raised; 125-250 ms swung across his
    # body, the crystal up and back; 375 ms upright again, the arms flung wide - the wall goes up; 500-875 ms the arms
    # held wide, the rags flying): raised, swung back level at the shoulder, lower, the arms wide (the staff held out
    # forward, the claw back; frame 4: the wall), held with the rags flying, the idle
    out["attack_w"] = [p(staff=(0, -3)), p(staff=STAFF_UP, staff_rot=1), p(staff=(0, -4), staff_rot=1, crouch=1),
                       p(reach=3, near_rot=3), p(reach=3, near_rot=3, hem=-2), p()]
    # Q Lay Waste (League's Karthus_Spell1a: by 125 ms the near claw swept down and back, held low behind him to 375 ms
    # with the robe's tail flicked out, then flung forward at chest height at 500 ms, the idle by 875): the claw going
    # back, low behind him, flung forward (frame 3: the mark on the target), held out with the rags flicked back,
    # coming down, the idle
    out["skill"] = [p(near_rot=3, near=(0, 2)), p(near_rot=3, near=(0, 5), crouch=1),
                    p(near_rot=1, near=(1, -1), hem=-2), p(near_rot=1, near=(2, -1), hem=-1),
                    p(near=(1, 0)), p()]
    # E Defile (League has no cast for the toggle - karthus_spell3 is a stub: the souls simply rise round him): the arms
    # flung wide like W's (frame 1: the aura begins), lifted a row by the souls, held, down, the idle
    out["skill2"] = [p(reach=2, near_rot=3), p(reach=3, near_rot=3, whole=(0, -1), hem=-1),
                     p(reach=3, near_rot=3, whole=(0, -2), hem=-2), p(reach=2, near_rot=3, whole=(0, -1), hem=-1), p()]
    # R Requiem (League's Karthus_Spell4_In: the book taken out at his chest; karthus_spell4_loop: he rises well off the
    # ground and sings for 3 s, the book held up behind his head or out in front, the staff held out raised, the rags
    # flying, then comes down): the book out, rising, hovering RISE rows up with a row's bob - the book up behind his head,
    # then in front, then up again -, coming down; the whole tag 3 s, the channel
    low = dict(near_rot=1, near=NEAR_BOOK, book=BOOK_AT)
    high = dict(near_rot=2, near=NEAR_HIGH, book=BOOK_HIGH)
    hover = [(high, 0, -2), (high, 1, -3), (high, 1, -3), (high, 0, -2), (low, -1, -2), (low, -1, -3), (low, 0, -3),
             (low, 1, -2), (high, 1, -2), (high, 0, -3), (high, -1, -3), (high, -1, -2)]
    out["ult"] = ([p(**low), p(staff=(0, -2), whole=(0, -5), hem=-1, **low), p(staff=(0, -4), whole=(0, -10), hem=-2, **low)] +
                  [p(staff=(0, -4), reach=2, whole=(0, -RISE + b), hem=h, **arm) for arm, b, h in hover] +
                  [p(staff=(0, -2), whole=(0, -6), hem=-1, **low)])
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]

    # the death (League's karthus_death: the staff dropped at his feet, he stands with his arms raised as his spirit,
    # and League fades him out; a sprite's body stays on the ground, so he sinks into his robe by his staff):
    # staggering, the staff falling level out of his hand, on the ground with his arms raised, hovering, then sinking
    # into his robe a few rows at a time, his arms down, lying in a heap
    ground = rig.D.ground - 1 - int(GRIP[1])           # the staff lying level: its middle row on the ground row
    drop = (3, -12, ground + 1)
    arms = dict(staff=(0, -8), near_rot=1, near=(0, -4))
    EMPTY = (-1, 5)                                     # the empty fist let down to his hip as he sinks
    out["dead"] = [p(whole=(-1, 0)), p(drop=(3, -6, -6), staff=(0, -4), whole=(-2, 0)),
                   p(drop=drop, **arms), p(drop=drop, whole=(0, -2), **arms),
                   p(drop=drop, crouch=4, staff=EMPTY), p(drop=drop, crouch=8, staff=EMPTY),
                   p(drop=drop, crouch=11, staff=EMPTY), p(drop=drop, crouch=12, staff=EMPTY)]
    return out


# ------------------------------------------------------------------------------------------------- the glide
# League's karthus_run: he floats on bent forward, off the ground with his toes hanging, bobbing, the rags streaming
# back, the near claw held out in front, the staff carried upright ahead of him; no steps. The upper body leant forward
# (one square every LEAN rows), the near arm forward, the whole figure LIFT rows off the ground (his shadow stays on
# it: the user, 2026-10-20, 「死歌是飘着走路的吧 我们现在不是」 - the first glide only bobbed a row, his feet on the
# ground) and bobbing a row, the hem trailing back two or three columns and fluttering.
LEAN = 6
LIFT = 6
GLIDE = dict(bob=[0, 0, -1, -1, -1, -1, 0, 0], hem=[-2, -3, -3, -2, -2, -3, -3, -2])


def run(F):
    return [F.pose(whole=(0, b - LIFT), hem=h, lean=LEAN, near_rot=1) for b, h in zip(GLIDE["bob"], GLIDE["hem"])]


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": run(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
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
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)
    F = form()
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()
