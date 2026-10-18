#!/usr/bin/env python3
"""league_gangplank's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧参考塔姆
那种做法 不用依赖codex 然后做完了你自己review 完美了再喊我review」).

    python tools/art/rig_gangplank.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_gangplank.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_gangplank.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_gangplank.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_gangplank_cut.py: Codex's step-1 redo take A-2 - the slimmer belly, 「普朗克不是大肚子」 -
brought from 57 x 62 to 46 x 50 squares, PPU 1.2, by whole rows / columns dropped, never the face's; the hand cannon cut
in its own box, the cutlass by paired row / column drops along it): the hat's top row 0, the soles row 49. Every pose is
lossless (memory no-deformation-lossless-poses): parts cut square by square from the design and only moved by whole
squares or mirrored (league_jarvaniv / league_ziggs); nothing is drawn again.
Parts: the hand cannon (gold; its bell points BACK over the shoulder, so a shot mirrors it to point forward), the near
arm (the glove on the cannon, the red wrap and the gold bracer, from the near shoulder), the far hand (the red wrap, the
fist and the hilt), the cutlass (mirrored top to bottom it points up: the raised blade), the body (head, torso, sash,
coat tails) and the two legs (row LEG_TOP down, split between the boots; the coat's purple and its gold trim stay with
the body). Hands and props move whole (league_ziggs: a hand turned about its shoulder lands behind the head or across
the face; a hand moved against the body stretches the sleeve), the legs move whole.
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

HERO = "gangplank"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "gangplank", "hd")
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

    def box(self, y0, y1, x0, x1):
        m = np.zeros((self.H, self.W), bool)
        m[max(0, y0):y1 + 1, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

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

    def layer(self, name, m=None):
        m = self.parts[name] if m is None else m
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


def pad(a):
    out = np.zeros((a.shape[0] + 2 * P, a.shape[1] + 2 * P, 4), np.uint8)
    out[P:P + a.shape[0], P:P + a.shape[1]] = a
    return out




# ------------------------------------------------------------------------------------------------- the design's parts
LEG_TOP = 37                                    # the legs from here down (the red sash ends on row 36)
STAND = 21                                      # the column between the boots: the standing point
GUN_PIVOT = (9.5, 10.5)                         # the cannon's middle (its mirror axis for a shot)


def cls_purple(d):
    r, g, b = (d[..., i].astype(int) for i in range(3))
    return (d[..., 3] > 0) & (b > g + 15) & (r > g) & (r + g + b > 90)


def design():
    d = load("design.png")
    # Codex's far boot lost its sole's outline row in the cut (row 48 is leather): close it on row 49
    d[49, 23:31] = np.where(d[48, 23:31, 3:4] > 0, np.array([*PD.edge_colour(d), 255], np.uint8), d[49, 23:31])
    D = CutDesign(d, px=STAND)
    coat = cls_purple(d)
    # the hand cannon with the glove on it (the hat's brim, rows 3-8 from column 11, stays with the head)
    D.part("gun", D.box(9, 15, 2, 15) | D.box(6, 8, 2, 10))
    # the near arm: the red wrap and the gold bracer under the cannon, out from the near shoulder
    D.part("near_arm", D.box(15, 24, 5, 13))
    # the far hand: the fist and the hilt (the red wrap stays on the forearm); the cutlass on its own
    D.part("far_hand", D.box(30, 35, 30, 36))
    D.part("blade", D.box(35, 45, 34, 45) | D.box(36, 37, 33, 33))
    # the legs: the trousers from LEG_TOP and the boots, the coat's purple left with the body
    D.part("near_leg", (D.box(LEG_TOP, 49, 13, 21) | D.box(42, 49, 9, 18)) & ~coat)
    D.part("far_leg", D.box(LEG_TOP - 1, 49, 22, 30) & ~coat)
    D.part("body", D.rest())
    return D


def vflip(layer, row):
    """A padded layer mirrored top to bottom about design row `row` (the blade raised: it points up)."""
    y = P + row
    out = np.zeros_like(layer)
    for i in range(layer.shape[0]):
        j = 2 * y - i
        if 0 <= j < layer.shape[0]:
            out[j] = layer[i]
    return out


def hflip(layer, col):
    """A padded layer mirrored left to right about design column `col` (the cannon turned to point forward)."""
    x = P + col
    out = np.zeros_like(layer)
    for i in range(layer.shape[1]):
        j = 2 * x - i
        if 0 <= j < layer.shape[1]:
            out[:, j] = layer[:, i]
    return out


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        L = {k: pad(D.layer(k)) for k in D.order}
        self.L = L
        self.gun_fwd = hflip(L["gun"], 9)
        self.blade_up = vflip(L["blade"], 35)
        self.ref_holes = None

    def pose(self, crouch=0, whole=(0, 0), gun=(0, 0), gun_fwd=False, gun_rot=0, arm=None, hand=(0, 0), blade=None,
             blade_up=False, legs=None, leg_layers=None, fill=True, no_blade=False):
        """crouch: rows the body (with hands and props) sets down onto the legs; whole: the whole figure; gun: the
        cannon and the near arm moved together (arm: the arm's own move, default = gun's); gun_fwd: the cannon mirrored
        to point forward; gun_rot: quarter turns of the cannon counter-clockwise about GUN_PIVOT; hand: the far fist with the cutlass (blade: the blade's own move, default = hand's);
        blade_up: the blade mirrored to point up from the fist; legs: ((near dx, dy), (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        U = (wx, wy + crouch)
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        arm = gun if arm is None else arm
        blade = hand if blade is None else blade
        legs_l = leg_layers if leg_layers is not None else [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)),
                                                             (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly))]
        layers = [*legs_l, (L["body"], dict(dx=U[0], dy=U[1])),
                  (L["near_arm"], dict(dx=U[0] + arm[0], dy=U[1] + arm[1])),
                  (self.gun_fwd if gun_fwd else L["gun"], dict(dx=U[0] + gun[0], dy=U[1] + gun[1], rot=gun_rot,
                                                                about=GUN_PIVOT))]
        if not no_blade:
            layers.append((self.blade_up if blade_up else L["blade"], dict(dx=U[0] + blade[0], dy=U[1] + blade[1])))
        layers.append((L["far_hand"], dict(dx=U[0] + hand[0], dy=U[1] + hand[1])))
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    MOST = 10

    def close_holes(self, can):
        """Small enclosed holes the idle does not have (where a turned arm leaves its shoulder) filled from the squares
        round them."""
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


def form():
    return Form(design(), rig_pad=(40, 40, 30, 12))


def over(base, top):
    out = base.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def sheet(cans, path, z=4):
    allc = np.stack(cans)
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    tiles = []
    for c in cans:
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(c[y0:y1, x0:x1]))
        tiles.append(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
    out = Image.new("RGB", (sum(t.width + 6 for t in tiles), tiles[0].height), (40, 40, 40))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + 6
    out.save(lp(path))


# frame lengths (ms), timed to the kit (tools/kit/build_gangplank.py): attack 26 ticks (433 ms), the hit on tick 9;
# Q 24 (400), the shot on tick 10; E 22 (367), the keg on tick 9; W 20 (333), the bite on tick 10; R 24 (400), the
# flare on tick 10
MS = {"idle": [140] * 8, "run": [110] * 8, "attack": [70, 80, 100, 100, 83], "skill": [80, 90, 80, 80, 70],
      "skill2": [70, 80, 90, 70, 57], "skill_w": [80, 90, 60, 60, 43], "ult": [80, 90, 100, 80, 50],
      "hit": [100, 100], "dead": [100, 100, 120, 150, 200, 500]}

# The idle's breath and the walk's bob (tools/art/idle_breathe.py's recipe, league_jarvaniv's dip): the figure above the
# shins sinks a row, each leg one plain trouser row shorter, the boots where they stand
DIP_ROWS = {"near_leg": 39, "far_leg": 39}


def dipped(layer, row):
    """A padded leg layer one row shorter: design row `row` out, the rows over it a row down (the boot stays)."""
    y = P + row
    out = layer.copy()
    out[1:y + 1] = layer[:y]
    out[0] = 0
    return out


def frames_all(F):
    p = F.pose
    out = {}
    L = F.L
    dip = [(dipped(L["far_leg"], DIP_ROWS["far_leg"]), {}), (dipped(L["near_leg"], DIP_ROWS["near_leg"]), {})]
    out["idle"] = [p(whole=(0, 1), leg_layers=dip) if b else p() for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    # auto attack (League's Gangplank_Attack1: an overhand cutlass chop): the blade raised (mirrored to point up from
    # the fist), the fist up beside the body, leaning back; the chop down and forward (frame 3, the hit on a_hit), the
    # follow-through low; back
    out["attack"] = [p(whole=(-1, 0), hand=(0, -1), blade_up=True), p(whole=(-1, 0), hand=(0, -2), blade_up=True),
                     p(crouch=1, whole=(1, 0), hand=(1, 1)), p(crouch=1, whole=(1, 0), hand=(1, 2)), p()]
    # Q Parrrley (League's Gangplank_Spell1: the pistol brought down and fired forward): the cannon off the shoulder,
    # turned forward (mirrored) and held at the chest with the arm, the shot (frame 2, q_rel), the kick back, back up
    # (only mirrored and moved whole: it leaves the shoulder below the beard, never across the face)
    fwd = dict(gun_fwd=True)
    # (aimed: the bell past his chest at shoulder height, the arm across the chest under the beard)
    out["skill"] = [p(gun=(11, 8), arm=(7, 6), **fwd), p(whole=(1, 0), gun=(22, 6), arm=(14, 4), **fwd),
                    p(gun=(21, 6), arm=(13, 4), **fwd), p(gun=(11, 8), arm=(7, 6), **fwd), p()]
    # E Powder Keg (League's Gangplank_Spell3: a keg set down with a stoop): he bends at the knees, both hands low as he
    # puts it down (frame 3, e_rel - the keg itself is thrown by the kit at the enemy's feet), up again
    low = dict(hand=(1, 2), gun=(0, 1))
    out["skill2"] = [p(crouch=1, hand=(1, 1)), p(crouch=2, **low), p(whole=(1, 0), crouch=2, **low),
                     p(crouch=1, hand=(0, 1)), p()]
    # W Remove Scurvy (League's Gangplank_Spell2: a bite of citrus): the near hand a square nearer the mouth (never over
    # the face), a bite (frame 2-3, w_rel; the fruit is the effect w_cast), chewing, back
    out["skill_w"] = [p(crouch=1, gun=(1, 0)), p(crouch=1, gun=(1, 1)), p(gun=(1, 0)), p(crouch=1), p()]
    # R Cannon Barrage (League's Gangplank_Spell4: the signal to his ship): the cannon turned to point at the sky (a
    # quarter turn clockwise) and raised beside his head, the flare fired (frame 3, r_rel; the flare is the effect
    # r_cast), down
    up = dict(gun_rot=3)
    out["ult"] = [p(gun=(0, -1), **up), p(gun=(0, -3), arm=(0, -1), **up),
                  p(whole=(0, -1), gun=(0, -4), arm=(0, -2), **up), p(gun=(0, -3), arm=(0, -1), **up), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Gangplank_Death: he staggers and falls back): back, down on his knees, on his back (a quarter
    # turn counter-clockwise, the head to the back), lying sunk into the ground line
    sink = p(crouch=2, whole=(-1, 0), hand=(0, 2))
    sit = p(crouch=4, whole=(-1, 0), hand=(0, 3))
    lying = R.lie(F.rig, p(crouch=4, no_blade=True), k=1, dx=-2, sink=4)   # the cutlass dropped under him
    out["dead"] = [p(whole=(-1, 0)), sink, sit, lying, lying, lying]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own legs moved whole (memory codex-legs-deform), league_ziggs's picked walk (D): the boots step on their
# own sides, the dip on each contact and the whole figure a row up as the legs pass (league_braum's spring); the hands
# never move against the body (「手臂有点变形吧」).
def _steps(stride, lifts):
    near = [round(stride * (1 - k / 4) + 1e-9) for k in range(5)]
    swing = [1, stride - 1 - (stride > 4), stride]
    dx = [v - stride // 2 for v in near + swing]
    up = [0] * 5 + list(lifts)
    return dict(near=list(zip(dx, up)), far=[(dx[(i + 4) % 8], up[(i + 4) % 8]) for i in range(8)],
                bob=[1, 0, 0, 0, 1, 0, 0, 0])


WALK_STEP = dict(_steps(6, (2, 3, 2)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    L = F.L
    dip = {"far_leg": dipped(L["far_leg"], DIP_ROWS["far_leg"]), "near_leg": dipped(L["near_leg"], DIP_ROWS["near_leg"])}
    rise = st.get("rise", [0] * len(st["bob"]))
    for (ndx, nup), (fdx, fup), bob, up in zip(st["near"], st["far"], st["bob"], rise):
        legs = [(dip["far_leg"] if bob else L["far_leg"], dict(dx=fdx, dy=-fup - up)),
                (dip["near_leg"] if bob else L["near_leg"], dict(dx=ndx, dy=-nup - up))]
        out.append(F.pose(whole=(0, bob - up), leg_layers=legs))
    return out


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
    outline squares with no colour beside them (rig_jarvaniv.audit); each tag at 6x."""
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
            dk = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
            pieces_ok = len(sz) == 1 or (tag == "dead" and len(sz) <= 3)
            flag = (not pieces_ok) or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
            bad += bool(flag)
            print(f"{tag:10s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}{'  <--' if flag else ''}")
            show = f.copy()
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
    if not (a.audit or a.review or a.parts):
        F = form()
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    R.Design.ruler(D, os.path.join(a.parts, f"{HERO}_parts.png"), z=12)
    F = form()
    idle = F.pose()
    ref = F.rig.canvas()
    ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
    print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
    tries = [F.pose(), F.pose(gun_fwd=True, gun=(3, 6)), F.pose(hand=(0, -2), blade_up=True), F.pose(hand=(1, 2)),
             F.pose(crouch=2)]
    sheet([F.rig.finish(c) for c in tries], os.path.join(a.parts, f"{HERO}_tries.png"))


if __name__ == "__main__":
    main()
