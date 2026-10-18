#!/usr/bin/env python3
"""league_ziggs's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧的话你参考塔姆
怎么做的 做完后自己review 完美了再喊我review」).

    python tools/art/rig_ziggs.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_ziggs.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_ziggs.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_ziggs.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_ziggs_cut.py: Codex's step-1 take A-1 brought to 48 rows, PPU 1.5, by whole rows /
columns dropped, never the goggles' nor the teeth's, the bombs cut on their own with their skulls kept): 61 x 48
squares, the helmet's top row 0, the soles row 47. Every pose is lossless (memory no-deformation-lossless-poses): parts
cut square by square from the design and only moved by whole squares or quarter turns about half-integer pivots
(league_jarvaniv / league_tahmkench); nothing is drawn again.
Parts: the near hand (image left: the bomb, its fuse and spark, the orange glove and the blue cuff, the blue sleeve up to
the near shoulder), the far hand (image right: the bomb, the glove, the blue cuff and the red sleeve up to the far
shoulder), each bomb also on its own (a throw takes it out of the hand: the projectile carries it on), the body (head,
torso, satchel) and the two legs (row LEG_TOP down, split between the boots). The hands move whole (a quarter turn about a
shoulder hid the far hand behind the head and put the near one across the face), the legs move whole.
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

HERO = "ziggs"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "ziggs", "hd")
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
LEG_TOP = 37                                    # the legs from here down (the overalls' bib ends on row 36)
FEET_SPLIT = 30                                 # columns <= this: the near leg; beyond: the far leg (and the brown seat)
NEAR_PIVOT = (19.5, 25.5)                       # the near shoulder (the red sleeve's top under the ear)
FAR_PIVOT = (45.5, 27.5)                        # the far shoulder (the red sleeve's top beside the beard)
STAND = 31                                      # the column between the boots: the standing point


def orange(d):
    r, g, b = (d[..., i].astype(int) for i in range(3))
    return (d[..., 3] > 0) & (r > 150) & (g > 60) & (g < 170) & (b < 60) & (r - g > 60)


def dark(d):
    return (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 70)


def design():
    d = load("design.png")
    D = CutDesign(d, px=STAND)
    org = orange(d)
    # the near hand: everything left of the ear's column, then the blue sleeve under the ear (rows 20-30) and the red
    # sleeve at the shoulder (rows 24-31, columns 17-22)
    near = D.box(5, 31, 0, 12) | D.box(20, 30, 13, 16) | D.box(24, 31, 17, 22)
    D.part("near_hand", near)
    # the far hand: the bomb, fuse and glove right of column 50, the blue cuff, the red sleeve from the far shoulder
    far = D.box(12, 35, 51, 60) | D.box(27, 35, 49, 50) | D.box(25, 31, 45, 48)
    D.part("far_hand", far)
    # the legs: row LEG_TOP down, split between the boots
    D.part("near_leg", D.box(LEG_TOP, D.H - 1, 0, FEET_SPLIT))
    D.part("far_leg", D.box(LEG_TOP, D.H - 1, FEET_SPLIT + 1, D.W - 1))
    D.part("body", D.rest())
    # the bombs inside the hands: the ball, the fuse and the spark (all but the glove's orange and what lies under it)
    D.near_bomb = D.parts["near_hand"] & D.box(5, 25, 0, 12) & ~org
    D.far_bomb = D.parts["far_hand"] & D.box(12, 31, 51, 60) & ~org
    return D


def turn_pt(p, about, k):
    """A point turned k quarter turns counter-clockwise on screen (y down) about `about` (ppu_rig.put's way)."""
    x, y = p
    ax, ay = about
    for _ in range(k % 4):
        x, y = ax + (y - ay), ay - (x - ax)
    return x, y


class Form:
    """The design's layers and pivots; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.body = pad(D.layer("body"))
        self.near_leg = pad(D.layer("near_leg"))
        self.far_leg = pad(D.layer("far_leg"))
        self.hands = {}
        for side, bomb in (("near", D.near_bomb), ("far", D.far_bomb)):
            m = D.parts[f"{side}_hand"]
            self.hands[(side, True)] = pad(D.layer(f"{side}_hand"))
            self.hands[(side, False)] = pad(D.layer(f"{side}_hand", m & ~bomb))
        self.bombs = {"near": pad(D.layer("near_hand", D.near_bomb)), "far": pad(D.layer("far_hand", D.far_bomb))}
        self.ref_holes = None

    def pose(self, crouch=0, whole=(0, 0), near=0, far=0, near_reach=(0, 0), far_reach=(0, 0), near_bomb=True,
             far_bomb=True, legs=None, leg_layers=None, far_front=False, near_front=True, fill=True):
        """crouch: rows the body (with both hands) sets down onto the legs (the legs' top rows hidden behind it, never
        lifted off them); whole: the whole figure; near / far: quarter turns of a hand counter-clockwise about its
        shoulder, *_reach: whole squares it moves after; *_bomb: the bomb still in that hand; legs: ((near dx, dy),
        (far dx, dy)); far_front: the far hand over the body (a throw past his face's front)."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        U = (wx, wy + crouch)
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        legs_l = leg_layers if leg_layers is not None else [(self.far_leg, dict(dx=wx + flx, dy=wy + fly)),
                                                             (self.near_leg, dict(dx=wx + nlx, dy=wy + nly))]
        far_l = (self.hands[("far", far_bomb)], dict(dx=U[0] + far_reach[0], dy=U[1] + far_reach[1], rot=far,
                                                     about=FAR_PIVOT))
        near_l = (self.hands[("near", near_bomb)], dict(dx=U[0] + near_reach[0], dy=U[1] + near_reach[1], rot=near,
                                                        about=NEAR_PIVOT))
        layers = [] if far_front else [far_l]
        layers += [*legs_l, (self.body, dict(dx=U[0], dy=U[1]))]
        if far_front:
            layers.append(far_l)
        layers.insert(len(layers) if near_front else 0, near_l)
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

    def bomb_on_ground(self, side, dx):
        """A bomb alone on the ground (its lowest square on the soles' row), dx squares from where it is held."""
        can = R.compose(self.rig, [(self.bombs[side], {})])
        ys = np.nonzero(can[..., 3].any(1))[0]
        out = self.rig.canvas()
        sh = self.rig.GY - 1 - ys.max()
        src = can[max(0, -sh):can.shape[0] - max(0, sh)]
        out[max(0, sh):max(0, sh) + src.shape[0]] = src
        return np.roll(out, dx, axis=1)


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


# frame lengths (ms); League's Ziggs: attack 0.656/s (windup 20%), spells 0.25 s casts, R 0.375 s
MS = {"idle": [140] * 8, "run": [110] * 8, "attack": [80, 80, 70, 100, 110], "skill": [70, 80, 70, 70, 110, 110],
      "skill2": [70, 80, 70, 110, 110], "skill_w": [70, 70, 90, 90, 80], "ult": [80, 90, 90, 70, 110, 160],
      "hit": [100, 100], "dead": [100, 100, 120, 60, 100, 60, 140, 500]}

# The idle's breath and the walk's bob (tools/art/idle_breathe.py's recipe, league_jarvaniv's dip): the figure above the
# shins sinks a row, each leg one plain shin row shorter, the boots where they stand
DIP_ROWS = {"near_leg": 40, "far_leg": 40}


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
    dip = [(dipped(F.far_leg, DIP_ROWS["far_leg"]), {}), (dipped(F.near_leg, DIP_ROWS["near_leg"]), {})]
    out["idle"] = [p(whole=(0, 1), leg_layers=dip) if b else p() for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    # The throws move whole hands, never turn them: turned about its shoulder the far hand went behind his head (hidden)
    # and the near one across his face (--parts tries, 2026-10-18). The far hand rises beside the head's far side.
    # auto attack (League's Ziggs_Attack1: the far hand's bomb tossed forward): the hand raised beside his head, the
    # body leaning back; the throw (frame 3, the bomb leaves on a_rel), the empty hand forward; a new bomb in the hand
    out["attack"] = [p(whole=(-1, 0), far_reach=(0, -5)), p(crouch=1, whole=(-1, 0), far_reach=(-1, -8)),
                     p(whole=(1, 0), far_reach=(3, -3), far_bomb=False), p(far_reach=(2, -1), far_bomb=False), p()]
    # Q Bouncing Bomb (League's Ziggs_Spell1: a big overhand lob): down and back, the hand high beside his head, the
    # throw forward from the toes (frame 4), the empty hand out, back
    out["skill"] = [p(crouch=1, whole=(-1, 0), far_reach=(0, -6)), p(crouch=2, whole=(-2, 0), far_reach=(-1, -11)),
                    p(crouch=1, whole=(-1, 0), far_reach=(0, -12)), p(whole=(2, 0), far_reach=(4, -6), far_bomb=False),
                    p(whole=(1, 0), far_reach=(2, -2), far_bomb=False), p()]
    # E Hexplosive Minefield (League's Ziggs_Spell3: a scattering underhand throw): the far hand swung down and back,
    # crouched; flung forward and up (frame 3, the mines leave on e_rel), the hand out empty; back
    out["skill2"] = [p(crouch=1, far_reach=(-1, 2)), p(crouch=2, far_reach=(-1, 3)),
                     p(whole=(1, 0), far_reach=(3, -3), far_bomb=False), p(whole=(1, 0), far_reach=(2, -2), far_bomb=False),
                     p()]
    # W Satchel Charge (League's Ziggs_Spell2): crouched, both hands down to drop the satchel at his feet (frame 2, the
    # blast on w_rel), blown up and back off his feet (3-4), landing on his feet
    down = dict(near_reach=(0, 2), far_reach=(0, 2))
    # (the hop only lifts: MoveBack carries the unit itself back, so a sprite offset would snap back when the tag ends)
    out["skill_w"] = [p(crouch=1, **down), p(crouch=2, **down), p(whole=(0, -5)), p(whole=(0, -6)), p(crouch=1)]
    # R Mega Inferno Bomb (League's Ziggs_Spell4): both hands raised empty beside his head (the big bomb is the effect
    # r_cast drawn above it), down, up on his toes, the heave forward (frame 4, the bomb leaves on r_rel), down, back
    hands = dict(near_bomb=False, far_bomb=False, near_front=False)
    out["ult"] = [p(crouch=1, near_reach=(1, -12), far_reach=(-1, -12), **hands),
                  p(crouch=2, near_reach=(1, -13), far_reach=(-1, -13), **hands),
                  p(whole=(0, -3), near_reach=(1, -14), far_reach=(-1, -14), **hands),
                  p(whole=(2, -2), near_reach=(3, -6), far_reach=(3, -6), **hands),
                  p(crouch=1, **hands), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Ziggs_Death: knocked off his feet backward): staggers back, the bombs dropped as he sinks,
    # sits down, falls on his back (a quarter turn counter-clockwise, the head to the back: lying he is wider than tall
    # only with the hands in - spread, the turned figure stood taller than he does), the two bombs on the ground
    bombs = over(F.bomb_on_ground("near", -12), F.bomb_on_ground("far", 12))
    nb = dict(near_bomb=False, far_bomb=False)
    sink = p(crouch=2, whole=(-1, 0), near_reach=(3, 3), far_reach=(-2, 2), **nb)
    sit = p(crouch=4, whole=(-1, 0), near_reach=(6, 6), far_reach=(-4, 5), **nb)
    # lying sunk 4 rows into the ground line (league_tahmkench's way): lower, it reads as fallen
    body = p(crouch=4, near_reach=(9, 4), far_reach=(-7, 1), **nb)
    lying = R.lie(F.rig, body, k=1, dx=-2, sink=4)
    # (8 frames since the 2026-10-19 frame audit: he lands from 2 rows up, lies, bounces a row, lies - the bombs on the
    # ground stay where they fell)
    out["dead"] = [p(whole=(-1, 0)), over(bombs, sink), over(bombs, sit), over(bombs, R.lie(F.rig, body, k=1, dx=-2, sink=2)),
                   over(bombs, lying), over(bombs, R.lie(F.rig, body, k=1, dx=-2, sink=3)), over(bombs, lying),
                   over(bombs, lying)]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own legs moved whole (memory codex-legs-deform: never Codex's legs), Nasus's wide-stance way: the boots
# stand far apart (a yordle's bow-legged stance) so the legs never cross - each steps on its own side, planted and
# sliding back, then lifted and carried forward, the far leg half a cycle later; the body dips a row as each foot lands
# (the idle's dip, skirt-free here).
def _steps(stride, lifts):
    near = [round(stride * (1 - k / 4) + 1e-9) for k in range(5)]
    swing = [1, stride - 1 - (stride > 4), stride]
    dx = [v - stride // 2 for v in near + swing]
    up = [0] * 5 + list(lifts)
    return dict(near=list(zip(dx, up)), far=[(dx[(i + 4) % 8], up[(i + 4) % 8]) for i in range(8)],
                bob=[1, 0, 0, 0, 1, 0, 0, 0])


# The user, 2026-10-18: 「感觉走路时候有点 僵硬」 (stride 4, lifts (1, 2, 1), the dip on the contact frames only: under a
# game pixel once at PPU 1.2, the hands still). Hands bouncing against the steps were turned down (「手臂有点变形吧」:
# moved against the body, the sleeve stretched at the shoulder); picked 「用 D 版走路」: a stride of 6, lifts (2, 3, 2),
# the dip on the contact frames and the whole figure a row up as the legs pass (league_braum's spring) - 2 rows of bob,
# the hands never moving against the body (work/zg/walk_variants.py showed now / A / D / E).
WALK_STEP = dict(_steps(6, (2, 3, 2)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    dip = {"far_leg": dipped(F.far_leg, DIP_ROWS["far_leg"]), "near_leg": dipped(F.near_leg, DIP_ROWS["near_leg"])}
    rise = st.get("rise", [0] * len(st["bob"]))
    for (ndx, nup), (fdx, fup), bob, up in zip(st["near"], st["far"], st["bob"], rise):
        # bob: the figure above the shins a row lower (each leg a shin row shorter, the boots where they stand);
        # rise: the whole figure, legs too, `up` rows higher (the step's spring, league_braum's walk)
        legs = [(dip["far_leg"] if bob else F.far_leg, dict(dx=fdx, dy=-fup - up)),
                (dip["near_leg"] if bob else F.near_leg, dict(dx=ndx, dy=-nup - up))]
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
    tries = [F.pose(), F.pose(far=1), F.pose(far=3), F.pose(near=3, far=1, near_bomb=False, far_bomb=False),
             F.pose(far_bomb=False, near_bomb=False), F.pose(crouch=2)]
    sheet([F.rig.finish(c) for c in tries], os.path.join(a.parts, f"{HERO}_tries.png"))


if __name__ == "__main__":
    main()
