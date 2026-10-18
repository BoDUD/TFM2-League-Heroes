#!/usr/bin/env python3
"""league_maokai's action frames posed from the approved design's own squares (the user, 2026-10-18: 「codex交付了 动作帧
的话你参考塔姆怎么做的 做完后自己review 完美了再喊我review」).

    python tools/art/rig_maokai.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_maokai.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_maokai.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_maokai.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_maokai_cut.py: Codex's step-1 take A-2, 75 x 80 on its own grid, brought to 60 rows by
whole rows / columns, PPU 1.5 - the user: 「太模糊了 PPU调整一下像素」): 56 x 60 squares, the branch's leaf row 0, the
moss crown's top row 2, the root feet row 59. Every pose is lossless (memory no-deformation-lossless-poses): parts cut
square by square from the design and only moved by whole squares, quarter turns about half-integer pivots and mirror
images; nothing is drawn again at another angle.
Parts: the huge near arm (the shoulder, the pale wood arm and the fist's carved face, rows 17-54 on the left), the far
claw holding the sapling (right), the lantern on its cord (top left: it sways), the near roots (under the arm and the
gold knee root) and the far root leg; the rest is the trunk (the moss crown, the branch, the face, the belt, the violet
cloth). League's clips (tools/lol/pose_ref.py renders): attack1/2 the huge arm swung up and down in front; spell1 the fist
slammed into the ground; spell2_up / down sinking into the roots and bursting out at the target; spell3 the far claw
throwing the sapling; spell4 both arms raised and slammed down; run a heavy lumbering walk.
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
import pixel_down as PD  # noqa: E402

HERO = "maokai"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "maokai", "hd")
P = 60                                          # padding round a design-sized layer


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign:
    """What ppu_rig.Rig needs of a design: the squares, the standing point, the outline colour."""
    TURN_PAD = P

    def __init__(self, d, px):
        self.hero, self.ppu = HERO, PPU
        self.d = d
        self.d0 = d.copy()
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = px
        self.outline = PD.edge_colour(d)
        self.parts, self.order, self.props = {}, [], set()

    def rows(self, spans):
        """{row: (x0, x1)} inclusive spans -> mask."""
        m = np.zeros((self.H, self.W), bool)
        for y, (x0, x1) in spans.items():
            m[y, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

    def box(self, y0, y1, x0, x1):
        return self.rows({y: (x0, x1) for y in range(y0, y1 + 1)})

    def part(self, name, m):
        for k in self.parts:
            self.parts[k] &= ~m
        self.parts[name] = m.copy()
        if name not in self.order:
            self.order.append(name)

    def rest(self):
        m = self.d[..., 3] > 0
        for v in self.parts.values():
            m &= ~v
        return m

    def layer(self, name, src=None):
        m = self.parts[name] if name != "rest" else self.rest()
        out = np.zeros_like(self.d)
        out[m] = (self.d if src is None else src)[m]
        return out


def pad(a):
    """A design-sized layer padded P squares on every side (compose() reads the padding from the size)."""
    out = np.zeros((a.shape[0] + 2 * P, a.shape[1] + 2 * P, 4), np.uint8)
    out[P:P + a.shape[0], P:P + a.shape[1]] = a
    return out


# ------------------------------------------------------------------------------------------------- the design's parts
def spans(table):
    out = {}
    for rows, cols in table:
        for y in rows:
            out[y] = cols
    return out


# The anatomy at the bottom (a material map of rows 32-59, 2026-10-18): the huge arm's fist rests on the ground on its
# root fingers (rows 52-59, columns 4-30, one piece with the fist); the near leg is wholly behind the fist; between
# the fist and the far leg hangs a root tassel from the belt (gold on top, dark below, its tip at row 55, off the
# ground), left of the violet cloth; the far leg is one diagonal root from under the cloth (row 44) to the ground. The
# second rig took the gold tassel for a knee and the fingers for a foot and slid them about (「左右腿还是太奇怪了」).
# the huge near arm: the shoulder (rows 17-20), the arm, the fist and its root fingers on the ground
ARM = spans([((17,), (15, 19)), ((18,), (11, 19)), ((19, 20), (9, 19)), (range(21, 25), (1, 19)),
             (range(25, 29), (1, 18)), ((29, 30), (0, 19)), ((31,), (0, 20)), ((32,), (0, 21)), ((33,), (0, 23)),
             ((34,), (0, 24)), (range(35, 38), (0, 25)), ((38, 39), (0, 26)), (range(40, 45), (0, 29)),
             ((45, 46), (3, 29)), (range(47, 52), (5, 29)), ((52,), (5, 30)), ((53,), (5, 28)), ((54,), (4, 27)),
             (range(55, 60), (0, 30))])
ARM_PIVOT = (14.5, 22.5)                        # the near shoulder
# the far claw with the sapling in it (right of the face)
FAR = spans([((19, 20), (49, 55)), (range(21, 33), (47, 55)), (range(33, 44), (45, 55)), (range(44, 48), (47, 55))])
FAR_PIVOT = (46.5, 34.5)                        # the far shoulder
# the lantern and its cord (hanging from the branch at top left)
LANTERN = spans([((7, 8), (5, 9)), (range(9, 18), (3, 13))])
LANTERN_TOP = 7
HIP, FOOT = 46, 58                              # the far leg swings about row HIP (under the cloth); its foot row
# the root tassel hanging from the belt (it sways; never a leg)
TASSEL = spans([((45,), (30, 33)), ((46,), (30, 34)), (range(47, 50), (30, 35)), ((50, 51), (30, 36)), ((52,), (31, 36)),
                ((53,), (31, 37)), ((54,), (31, 34)), ((55,), (32, 35))])
# the far root leg, whole: the thigh coming out right of the cloth (row 44) to the foot on the ground (the cloth's
# violet squares stay with the trunk)
FAR_LEG = spans([((44,), (40, 42)), ((45,), (40, 43)), ((46,), (40, 44)), ((47, 48), (39, 46)), (range(49, 52), (39, 47)),
                 ((52,), (36, 47)), ((53,), (36, 48)), ((54,), (35, 49)), ((55,), (34, 49)), ((56,), (33, 50)),
                 ((57, 58), (32, 51))])


# the sapling in the far claw (thrown by E: the claw is empty from the release until the next one grows)
SAPLING_ROWS, SAPLING_COL = 36, 48


def violet(d):
    """The violet cloth (and its dark blue shade): blue well over red and green."""
    rgb = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (rgb[..., 2] > rgb[..., 0] + 40) & (rgb[..., 2] > rgb[..., 1] + 40)


# The far forearm (2026-10-18, the user on the PPU choices: 「怎么感觉右手和身体是断开的」): in Codex's A-2 (80 rows) the
# moss sleeve runs from under the beard straight into the wooden hand that holds the sapling; the 60-row cut dropped every
# other column between them (49, 51 ... 59), and the cut's outline weight (x3) kept the outline columns over the
# sleeve's, so the sleeve came out moss and outline in turn and the hand looked cut off. Every outline square between
# the beard and the hand (rows 30-40, columns 44-48) whose A-2 squares are sleeve takes the sleeve's commonest moss
# there (tools: the cut's kept rows / columns recomputed, design_maokai_cut.dp_cut) - the moss now runs into the wrist
# as in A-2 (and the two squares where A-2's light moss meets the hand, columns 58-60 rows 47-50, column 47 here);
# nothing else changes.
SLEEVE = {(33, 44): (69, 85, 43), (33, 46): (167, 190, 52), (34, 45): (112, 137, 49), (36, 48): (112, 137, 49),
          (37, 44): (50, 61, 37), (37, 48): (69, 85, 43), (38, 48): (112, 137, 49), (39, 48): (50, 61, 37),
          (34, 47): (112, 137, 49), (35, 47): (112, 137, 49)}


def design():
    d = load("design.png")
    for (y, x), rgb in SLEEVE.items():
        assert d[y, x, 3] and max(d[y, x, :3]) < 45, (y, x, d[y, x])   # outline squares only
        d[y, x] = (*rgb, 255)
    D = CutDesign(d, px=31)
    D.part("far_leg", D.rows(FAR_LEG) & ~violet(d))
    D.part("tassel", D.rows(TASSEL) & ~violet(d))
    D.part("far", D.rows(FAR))
    D.part("lantern", D.rows(LANTERN))
    D.part("arm", D.rows(ARM))
    return D


def sapling_mask(D):
    m = np.zeros((D.H, D.W), bool)
    m[:SAPLING_ROWS + 1, SAPLING_COL:] = True
    return m & D.parts["far"]


TINT = {"arm": (255, 60, 60), "far": (60, 120, 255), "lantern": (255, 220, 0), "tassel": (255, 0, 255),
        "far_leg": (0, 220, 120)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def put_layer(D, name, keep=None):
    out = np.zeros_like(D.d)
    m = D.parts[name] if keep is None else D.parts[name] & keep
    out[m] = D.d[m]
    return pad(out)


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        tidy = self.rig.finish

        def finish(can):
            """ppu_rig's finish, then nothing under the ground line (its outline pass drew under the W cut, the hit's
            flash and the lying body)."""
            out = tidy(can)
            out[self.rig.GY:] = 0
            return out
        self.rig.finish = finish
        self.arm = put_layer(D, "arm")
        self.far = put_layer(D, "far")
        self.far_empty = put_layer(D, "far", ~sapling_mask(D))
        self.lantern = put_layer(D, "lantern")
        self.tassel = put_layer(D, "tassel")
        self.far_leg = put_layer(D, "far_leg")
        self.body = pad(D.layer("rest"))
        self.ref_holes = None

    def pose(self, whole=(0, 0), crouch=0, arm=(0, 0), far=(0, 0), lantern=0, leg=(0, 0), tassel=0, empty=False,
             lean=0, fill=True):
        """whole: the whole figure moved (dx, dy); crouch: rows the trunk (with the far claw, the tassel and the
        lantern) sinks, over the far leg's top (the leg goes on behind the cloth, never a row taken out of it - the first
        rig did that: 「腿部变形了吧 少了像素？」); lean: columns the trunk moves; arm: the huge arm with its fist and root
        fingers moved (dx, dy) from where it stands - it never follows the crouch or the lean (the fist stays planted
        unless lifted) and dx is never < 0 (backward opens a slit beside the trunk); far: the far claw moved with the
        trunk; lantern / tassel: columns they swing (lantern None: none); leg: the far leg moved whole (dy < 0 lifts:
        its thigh goes up behind the cloth); empty: the far claw without its sapling (thrown)."""
        if arm[0] < 0:
            raise ValueError("the arm never moves back off the trunk")
        if lean < 0:
            raise ValueError("the trunk never leans back off the far leg (a slit opens beside the cloth)")
        wx, wy = whole
        ux, uy = wx + lean, wy + crouch
        layers = [(self.far_empty if empty else self.far, dict(dx=ux + far[0], dy=uy + far[1])),
                  (self.swung(leg[0]), dict(dx=wx, dy=wy + leg[1])),
                  (self.body, dict(dx=ux, dy=uy)),
                  (self.tassel, dict(dx=ux + tassel, dy=uy)),
                  *([] if lantern is None else [(self.lantern, dict(dx=ux + lantern, dy=uy))]),
                  (self.arm, dict(dx=wx + arm[0], dy=wy + arm[1]))]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def swung(self, dx):
        """The far leg swung about its hip: each design row moved whole, round(dx * (row - HIP) / (FOOT - HIP)) columns -
        the hip under the cloth stays, the foot moves dx (moved whole, the leg's top slid out from under the cloth and
        opened a see-through slit at the hip)."""
        if not dx:
            return self.far_leg
        out = np.zeros_like(self.far_leg)
        for y in range(self.far_leg.shape[0]):
            k = int(round(dx * min(max(y - P - HIP, 0), FOOT - HIP) / (FOOT - HIP)))
            row = self.far_leg[y]
            if k > 0:
                out[y, k:] = row[:-k]
            elif k < 0:
                out[y, :k] = row[-k:]
            else:
                out[y] = row
        return out

    def lantern_on_ground(self, dx):
        """The lantern alone, upright (as it hangs), standing on the ground dx columns right of the standing point."""
        can = R.compose(self.rig, [(self.lantern, dict(dx=0, dy=0))])
        ys, xs = np.nonzero(can[..., 3] > 0)
        out = self.rig.canvas()
        sub = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        top, left = self.rig.GY - sub.shape[0], self.rig.CX + dx - sub.shape[1] // 2
        out[top:top + sub.shape[0], left:left + sub.shape[1]] = sub
        return out

    MOST = 12

    def close_holes(self, can):
        """Small enclosed holes the idle does not have filled from the squares round them (rig_jarvaniv's way)."""
        if self.ref_holes is None:
            idle = self.pose(fill=False)
            op = idle[..., 3] > 0
            self.ref_holes = ndimage.binary_dilation(ndimage.binary_fill_holes(op) & ~op, iterations=2)
        op = can[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op & ~self.ref_holes
        lbl, n = ndimage.label(holes)
        fill = np.zeros_like(holes)
        for k in range(1, n + 1):
            m = lbl == k
            if m.sum() <= self.MOST:
                fill |= m
        if not fill.any():
            return can
        out = R.fill_under(can, fill)
        left = fill & (out[..., 3] == 0)
        if left.any():
            src = (out[..., 3] > 0) & (out[..., :3].astype(int).sum(-1) >= 70)
            _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
            out[left] = out[iy[left], ix[left]]
        return out

    def under_ground(self, can):
        out = can.copy()
        out[self.rig.GY:] = 0
        return out


def form():
    return Form(design(), rig_pad=(40, 50, 40, 20))


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_maokai.py) come from these: a_hit frame 3, q_rel frame 3, the W dash,
# e_rel frame 3, r_rel frame 4
MS = {"idle": [150] * 8, "run": [125] * 8, "attack": [80, 90, 110, 120, 100], "skill": [80, 110, 120, 120, 110],
      "skill2": [80, 100, 100, 120], "skill2_land": [70, 80, 90, 100], "skill_e": [80, 80, 110, 110, 100],
      "ult": [100, 110, 120, 130, 120, 120], "hit": [100, 100], "dead": [100, 110, 120, 140, 160, 500]}


def frames_all(F):
    p = F.pose
    out = {}
    # idle: the trunk sinks a row behind the roots and rises (the roots and the planted arm stand), the lantern swings
    # a column after it
    out["idle"] = [p(crouch=c, lantern=l) for c, l in zip([0, 0, 1, 1, 1, 1, 0, 0], [0, 1, 1, 0, 0, -1, -1, 0])]
    # auto attack (League's maokai_attack1: the huge arm swung up and brought down in front): the arm drawn up with
    # the tree a column back (never the trunk alone: a slit opens beside the cloth), the blow (frame 3): the arm down on the ground again, the whole tree a column forward,
    # the trunk low and leaning in; held, back
    out["attack"] = [p(arm=(0, -2), whole=(-1, 0)), p(arm=(0, -4), whole=(-1, 0), lantern=-1),
                     p(whole=(1, 0), lean=1, crouch=1, lantern=1), p(whole=(1, 0), lean=1, crouch=1), p()]
    # Q Bramble Smash (League's Maokai_spell1: the fist raised and slammed into the ground): raised high with the trunk
    # leaning back, the slam (frame 3): the fist down, the tree two columns forward, the trunk two rows low; held while
    # the shockwave runs, back
    out["skill"] = [p(arm=(0, -4), whole=(-1, 0)), p(arm=(0, -6), whole=(-1, 0), lantern=-1),
                    p(whole=(2, 0), lean=1, crouch=2, lantern=1), p(whole=(2, 0), lean=1, crouch=2),
                    p(whole=(1, 0), crouch=1)]
    # W Twisted Advance (League's maokai_spell2_down): crouched into the roots and down under the ground
    out["skill2"] = [p(crouch=2), F.under_ground(p(whole=(0, 14))), F.under_ground(p(whole=(0, 34))),
                     F.under_ground(p(whole=(0, 56)))]
    # and out at the target (maokai_spell2_up): bursting up out of the ground, up over it, landing low
    out["skill2_land"] = [F.under_ground(p(whole=(0, 28))), F.under_ground(p(whole=(0, 6))),
                          p(whole=(0, -4)), p(crouch=2)]
    # E Sapling Toss (League's maokai_spell3): the far claw drawn up (it never moves more than a column off the
    # trunk: it parts from it), the throw (frame 3: the claw empty from here), held out, back
    out["skill_e"] = [p(far=(0, -2)), p(far=(0, -4), whole=(-1, 0)), p(far=(1, -2), lean=1, empty=True),
                      p(far=(1, -1), empty=True), p(far=(0, 0), empty=True)]
    # R Nature's Grasp (League's maokai_spell4): both arms raised high, held, slammed down (frame 4) with the trunk low,
    # held while the wall rises, back
    out["ult"] = [p(arm=(0, -3), far=(0, -2), whole=(-1, 0)), p(arm=(0, -6), far=(0, -3), whole=(-1, 0), lantern=-1),
                  p(arm=(0, -7), far=(0, -3), whole=(-1, 0)), p(whole=(2, 0), far=(1, 1), lean=1, crouch=2, lantern=1),
                  p(whole=(2, 0), far=(1, 1), lean=1, crouch=2), p(whole=(1, 0), crouch=1)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's maokai_death: he sinks forward and falls on his face, to the right): staggers, sinks, low,
    # then lying forward; the lantern falls off the branch and stands on the ground before him (turned with him it
    # would hang sideways)
    lying = R.lie(F.rig, p(crouch=2, lantern=None), k=3, dx=6)
    lamp = F.lantern_on_ground(dx=40)
    lying[lamp[..., 3] > 0] = lamp[lamp[..., 3] > 0]
    out["dead"] = [p(whole=(-1, 0), arm=(0, -1)), p(whole=(-2, 0), crouch=1), p(whole=(-2, 0), crouch=3),
                   lying, lying.copy(), lying.copy()]
    return out


# the walk (League's maokai_run: a heavy lumbering walk). His near leg is wholly behind the fist, which rests on its
# root fingers, so he walks on the fist and the far leg in turn, like a knuckle-walker: the fist planted four frames
# sliding back 2 columns (the tree moving over it), then lifted (1-2 rows) and set 2 columns forward again; the far leg
# the same half a cycle later (its thigh going up behind the cloth when lifted). The fist never goes back of where it
# stands (a slit would open beside the trunk), the far leg never further back than a column (under the cloth). The
# trunk dips a row after each landing; the tassel, hanging between the fist and the far leg, is pushed along by
# the fist; the lantern swings a step behind. Earlier tries, turned down
# (2026-10-18): the near "leg" (the tassel and the fingers) shuffling a column (「左腿完全不动啊？」), then stepping 4
# columns with the far leg's lower half alone (「左右腿还是太奇怪了」).
WALK = dict(arm=[(2, 0), (1, 0), (1, 0), (0, 0), (0, -1), (1, -2), (2, -2), (2, -1)],
            leg=[(0, -1), (1, -2), (2, -2), (2, -1), (2, 0), (1, 0), (0, 0), (-1, 0)],
            bob=[1, 1, 0, 0, 1, 1, 0, 0],
            tassel=[2, 1, 1, 0, 0, 1, 2, 2],          # pushed along by the fist (never half behind it)
            lantern=[0, -1, -1, 0, 0, 1, 1, 0])


def walk(F):
    return [F.pose(crouch=bob, arm=arm, leg=leg, tassel=ts, lantern=lan)
            for arm, leg, bob, ts, lan in zip(WALK["arm"], WALK["leg"], WALK["bob"], WALK["tassel"], WALK["lantern"])]


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": walk(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def audit(F, acts, out_dir):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), new enclosed holes, colours in no design,
    orphan outline squares; each tag at 6x with every piece but the biggest red, every new hole magenta and every
    orphan outline square orange (rig_jarvaniv.audit)."""
    from PIL import ImageDraw
    os.makedirs(lp(out_dir), exist_ok=True)
    rig = F.rig
    allowed = {tuple(c) for c in F.D.d[F.D.d[..., 3] > 0][:, :3].tolist()} | {tuple(F.D.outline)}
    idle = rig.finish(acts["idle"][0][0])
    iop = idle[..., 3] > 0
    idark = iop & (np.abs(idle[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
    base_orphan = int((idark & ~ndimage.binary_dilation(iop & ~idark, structure=R.CROSS)).sum())
    idle_holes = ndimage.binary_fill_holes(iop) & ~iop
    bad = 0
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            f = rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(idle_holes, iterations=3)
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - allowed
            dark = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dark & ~ndimage.binary_dilation(op & ~dark, structure=R.CROSS)
            flag = len(sz) > 1 or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
            bad += bool(flag)
            print(f"{tag:12s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}{'  <--' if flag else ''}")
            show = f.copy()
            if n > 1:
                big = 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
                show[(lbl > 0) & (lbl != big)] = (255, 0, 0, 255)
            show[new] = (255, 0, 255, 255)
            show[orphan] = (255, 128, 0, 255)
            tiles.append(show)
        allc = np.stack(tiles)
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        z = 6
        sheet_ = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 8), (y1 - y0) * z + 16), (40, 40, 40))
        dr = ImageDraw.Draw(sheet_)
        for i, t in enumerate(tiles):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
            sheet_.paste(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST),
                         (i * ((x1 - x0) * z + 8), 16))
            dr.text((i * ((x1 - x0) * z + 8) + 2, 2), str(i + 1), fill=(255, 255, 0))
        sheet_.save(lp(os.path.join(out_dir, f"{HERO}_{tag}_6x.png")))
    print("frames flagged:", bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D = design()
        tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
        print({k: int(v.sum()) for k, v in D.parts.items()}, "rest", int(D.rest().sum()))
        F = form()
        idle = F.pose()
        ref = F.rig.canvas()
        ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
        print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
        return
    F = form()
    if not (a.audit or a.review):
        F.rig.export(frames(F))
        return
    acts = frames(F)
    if a.audit:
        audit(F, acts, a.audit)
    else:
        F.rig.review(acts, a.review)


if __name__ == "__main__":
    main()
