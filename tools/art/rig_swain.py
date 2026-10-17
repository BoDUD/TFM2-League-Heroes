#!/usr/bin/env python3
"""league_swain's action frames posed from the approved designs' own squares (the user, 2026-10-17: 「动作帧的话你参考塔姆
那种方式做吧 做到完美了喊我review」).

    python tools/art/rig_swain.py --parts DIR       # the designs with their parts tinted (8x)
    python tools/art/rig_swain.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_swain.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_swain_cut.py, Codex's step-1 takes A-1 and B-1 brought to 60 rows, PPU 1.5, by whole
rows / columns dropped, never the face's): A his idle (38 x 61 squares, hair top row 1, soles row 60), B the demon.
B is built from A so the two forms wear the same coat: A's body + B-1's two wings behind it (B-1's squares moved by
B_OFF, the face and the hair set on A's) + the demon arm on his far side + glowing eyes. League's demon arm is his
LEFT arm - the far side of a sprite facing right (League's casts: the arm the Arm_Mat overlay lights) - and B-1 drew it
on the near side, so the arm is taken from B's picture mirrored (assets/source/swain/hd/picture_bf.png), brought to the
design's grid ONCE, hanging (ppu_rig.Design.turned at 0), and only ever moved losslessly: quarter turns about his far
shoulder (ARM_PIVOT: hanging, straight ahead, straight up) and whole squares (`reach`). The first cut drew it again from
the picture at every angle and the user saw it change shape as it moved (「右手臂移动时候有点变形」, 2026-10-17). Everything
else moves only losslessly too (memory no-deformation-lossless-poses): whole squares moved, the upper body over the
coat's hem, the boots stepping under it, a whole frame a quarter turn for the death.
Parts of A (design squares): the far sleeve (cols 32-37, rows 18-40: taken off while the demon arm casts, its glove
rows filled with the sleeve's own row 29 repeated, the coat hanging empty), the two legs in the coat's opening (the
shins and the boots), the coat's near and far panels (over the legs), the upper body (rows 0-40).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "swain"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "swain", "hd")
P = 40                                          # padding round a design-sized layer (ppu_rig.Design.TURN_PAD)

# B-1's squares in A's coordinates: A = B - B_OFF (the faces, the hair and the soles agree: 17.6 / 18 / 20 columns,
# 5.4 / 3 / 4 rows)
B_OFF = (18, 4)
# the demon arm in picture_bf's design squares (Design(picture_bf), 75 x 65): the bare arm under the shoulder pad down
# to the claws; turned about the shoulder joint; drawn at A's far shoulder
ARM_POLY = [(42.5, 26.5), (48.5, 26.5), (49.5, 31), (51, 37), (51, 44), (41, 44), (41, 37), (43, 31)]
ARM_ABOUT = (46, 27.5)
SHOULDER = (34, 19.5)                           # A's far shoulder under the pauldron
ARM_PIVOT = (34.5, 19.5)                        # the quarter turns' centre (both halves: square centres stay centres)
UPPER_END = 40                                  # the upper body: rows 0..40
LEG_TOP = 44                                    # the shins show from this row (above: the tassets' dark hem)
HEM = 50                                        # the coat panels sway from this row down


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

    def mask(self, rule):
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        return rule(yy, xx) & (self.d[..., 3] > 0)

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


def design_a():
    d = load("design_A.png")
    D = CutDesign(d, px=22)
    # the far sleeve and its glove
    D.part("far_arm", D.mask(lambda y, x: (y >= 18) & (y <= 40) & (x >= 32)))
    # the coat's panels hang over the legs (their hems sway in the walk); registered before the legs, which take the
    # boots back from them
    D.part("near_coat", D.mask(lambda y, x: (y > UPPER_END) & (x <= 12)))
    D.part("far_coat", D.mask(lambda y, x: (y > UPPER_END) & (x >= 33)))
    # the shins in the coat's opening (their armour's squares and outline, never the lining's reds) and the boots
    # under its hem
    rgb = d[..., :3].astype(int)
    red = (rgb[..., 0] > 70) & (rgb[..., 1] < 12)
    D.part("near_leg", D.mask(lambda y, x: (((y >= LEG_TOP) & (y <= 57) & (x >= 12) & (x <= 17)) & ~red) |
                              ((y >= 58) & (x >= 8) & (x <= 13))))
    D.part("far_leg", D.mask(lambda y, x: (((y >= LEG_TOP) & (y <= 57) & (x >= 24) & (x <= 33)) & ~red) |
                             ((y >= 58) & (x >= 26) & (x <= 36))))
    D.part("upper", D.mask(lambda y, x: y <= UPPER_END) & D.rest())
    D.part("lining", D.rest())
    return D


def empty_sleeve(D):
    """The far sleeve hanging empty while the demon arm is out: its rows 18-29 as drawn (the coat over the shoulder),
    the glove's rows 30-40 the sleeve's own row 29 repeated (columns 32-34) closed by the outline."""
    out = D.layer("far_arm")
    out[30:41] = 0
    for y in range(30, 41):
        out[y, 32:35] = D.d[29, 32:35]
        out[y, 35] = (*D.outline, 255)
    return out


EYES = {(8, 22): (248, 2, 92), (8, 23): (211, 57, 74), (8, 26): (248, 2, 92)}     # the demon's glowing eyes


def demon_upper(D):
    """The upper body with the demon's eyes."""
    out = D.layer("upper")
    for (y, x), c in EYES.items():
        out[y, x, :3] = c
    return out


def b_wings():
    """B-1's two wings in A's coordinates (design-sized, padded P): the near wing left of B-1's near shoulder line, the far
    one right of its coat's far edge."""
    b = load("design_B.png")
    H, W = b.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    near = (((yy < 14) & (xx <= 29)) | ((yy >= 14) & (yy < 21) & (xx <= 23)) | ((yy >= 21) & (yy < 38) & (xx <= 21)) |
            ((yy >= 38) & (xx <= 10)))
    far = (((yy < 14) & (xx >= 49)) | ((yy >= 14) & (yy < 31) & (xx >= 52)) | ((yy >= 31) & (xx >= 56)))
    m = (near | far) & (b[..., 3] > 0)
    out = np.zeros((61 + 2 * P, 38 + 2 * P, 4), np.uint8)
    ys, xs = np.nonzero(m)
    ty, tx = ys - B_OFF[1] + P, xs - B_OFF[0] + P
    ok = (ty >= 0) & (ty < out.shape[0]) & (tx >= 0) & (tx < out.shape[1])
    out[ty[ok], tx[ok]] = b[ys[ok], xs[ok]]
    return out


def aura_wings(px):
    """The demon's wings as the main pack shows them: a picture following him while R lasts (view_buffs - a mod hero's
    idle and run can't change, memory form-switch-limits), so it is drawn behind every frame, his own ones and the
    add-on's demon body alike. The client never mirrors an effect's picture (the red side), so its shape is symmetric
    about his standing line: B-1's two wings and their mirror image together (each square B-1's own colour where B-1
    has one, the mirror's elsewhere) - the near wing mirrored alone left a gap at his far shoulder, his body reaching
    22 columns left of the line and 15 right of it. -> design-sized layer padded P."""
    w = b_wings()
    out = w.copy()
    axis = P + px                                      # the standing line: the left edge of design column px
    ys, xs = np.nonzero(w[..., 3])
    tx = 2 * axis - 1 - xs
    ok = (tx >= 0) & (tx < w.shape[1])
    free = out[ys[ok], tx[ok], 3] == 0
    out[ys[ok][free], tx[ok][free]] = w[ys[ok][free], xs[ok][free]]
    return out


class DemonArm:
    """The demon arm from the mirrored B picture at any angle (degrees counter-clockwise from hanging), its shoulder
    joint on A's far shoulder; cached."""

    def __init__(self):
        self.BF = R.Design(HERO, PPU, 40, pic_top=70, coarse=True, picture="picture_bf")
        self.cache = {}

    def at(self, angle, shoulder=SHOULDER, size=(61, 38)):
        key = (angle, shoulder)
        if key not in self.cache:
            arm = self.BF.turned(ARM_POLY, angle, ARM_ABOUT)          # BF's design + its own TURN_PAD
            Pb = self.BF.TURN_PAD
            out = np.zeros((size[0] + 2 * P, size[1] + 2 * P, 4), np.uint8)
            dx, dy = int(round(shoulder[0] - ARM_ABOUT[0])), int(round(shoulder[1] - ARM_ABOUT[1]))
            ys, xs = np.nonzero(arm[..., 3])
            ty, tx = ys - Pb + dy + P, xs - Pb + dx + P
            ok = (ty >= 0) & (ty < out.shape[0]) & (tx >= 0) & (tx < out.shape[1])
            out[ty[ok], tx[ok]] = arm[ys[ok], xs[ok]]
            self.cache[key] = out
        return self.cache[key]


# ------------------------------------------------------------------------------------------------- posing
# the walk (League's Swain_Run: an upright walk, the far leg stepping in the coat's opening, the near panel swinging
# with the near leg, the boots under the hem): per frame (near boot (columns forward, rows lifted), far leg (...), the
# upper body's bob, the near panel's hem (columns at its lowest rows), unused). The boots stay
# on their own sides - the coat hides the hips.
WALK = [((-3, 0), (4, 0), 0, -2, -1), ((-2, 1), (2, 0), 1, -1, -1), ((0, 2), (0, 0), 1, 0, 0), ((2, 1), (-2, 0), 0, 1, 1),
        ((3, 0), (-4, 0), 0, 2, 1), ((2, 0), (-2, 1), 1, 1, 1), ((0, 0), (0, 3), 1, 0, 0), ((-2, 0), (2, 1), 0, -1, -1)]


def shift_rows(layer, y0, y1, dx):
    """Whole rows y0..y1 of a layer moved dx columns, nothing wrapping round."""
    out = layer.copy()
    if not dx:
        return out
    band = layer[y0:y1 + 1]
    moved = np.zeros_like(band)
    if dx > 0:
        moved[:, dx:] = band[:, :-dx]
    else:
        moved[:, :dx] = band[:, -dx:]
    out[y0:y1 + 1] = moved
    return out


def sway_hem(layer, y0, y1, dx):
    """The hem swung dx columns at its lowest row, less up to y0 (whole rows, each its own share)."""
    out = layer.copy()
    out[y0:y1 + 1] = 0
    n = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        d = int(round(dx * (y - y0 + 1) / (n + 1)))
        row = shift_rows(layer, y, y, d)
        out[y] = row[y]
    return out


class Poser:
    def __init__(self):
        self.D = design_a()
        self.rig = R.Rig(self.D, pad=(70, 70, 90, 30))
        self.arm = DemonArm()
        self.aura = aura_wings(self.D.px)
        self.sleeve = pad(empty_sleeve(self.D))
        self.upper_a = pad(self.D.layer("upper"))
        self.upper_b = pad(demon_upper(self.D))
        self.lining = pad(self.D.layer("lining"))
        self.legs = {k: self.D.layer(k) for k in ("near_leg", "far_leg")}
        self.coats = {k: self.D.layer(k) for k in ("near_coat", "far_coat")}
        self.far_arm = pad(self.D.layer("far_arm"))

    def pose(self, form="A", arm=None, up=(0, 0), whole=(0, 0), near=(0, 0), far=(0, 0), hem=0, reach=(0, 0)):
        """form A or B (the demon: the demon arm always out, glowing eyes; the wings are the aura's); arm: quarter turns
        of the demon arm counter-clockwise from hanging, in degrees (90 straight ahead, 180 straight up) - None in A =
        the far sleeve as drawn; reach: whole squares the turned arm moves (pulled in toward his chest: negative x);
        up: the upper body (and the arm) moved over the coat and the legs - rows DOWN only (a crouch: the upper body
        overlaps the coat; lifted it would open a gap at the waist); whole: the whole figure; near / far: (columns
        forward, rows lifted) of a boot and its shin; hem: columns the near panel's hem swings at its lowest row (the
        far panel half as much)."""
        D = self.D
        wx, wy = whole
        if up[1] < 0:
            raise ValueError("the upper body never lifts off the coat")
        ux, uy = up[0] + wx, up[1] + wy
        layers = [(self.lining, dict(dx=wx, dy=wy))]
        fill = []
        for name, (dx, lift) in (("far_leg", far), ("near_leg", near)):
            img = self.legs[name]
            if lift:
                img = img.copy()
                # a lifted boot: its shin's top rows go under the tassets (cut at LEG_TOP)
                img[:LEG_TOP + lift] = 0
            layers.append((pad(img), dict(dx=wx + dx, dy=wy - lift)))
        for name, h in (("near_coat", hem), ("far_coat", int(np.trunc(hem / 2)))):
            img = sway_hem(self.coats[name], HEM, D.H - 1, h) if h else self.coats[name]
            layers.append((pad(img), dict(dx=wx, dy=wy)))
            if h:
                fill.append((name, (wx, wy)))
        layers.append((self.upper_b if form == "B" else self.upper_a, dict(dx=ux, dy=uy)))
        if form == "A" and arm is None:
            layers.append((self.far_arm, dict(dx=ux, dy=uy)))
        else:
            a = arm or 0
            if a % 90:
                raise ValueError("the demon arm turns in quarter turns only")
            layers.append((self.sleeve, dict(dx=ux, dy=uy)))
            layers.append((self.arm.at(0), dict(dx=ux + reach[0], dy=uy + reach[1], rot=(a // 90) % 4,
                                                 about=ARM_PIVOT)))
        can = R.compose(self.rig, layers, fill=fill)
        if near != (0, 0) or far != (0, 0):
            # where a shin stood in the coat's opening, now bare: the lining behind it, from the squares round it (the
            # boots' rows stay open - the ground between the boots)
            m = np.zeros(can.shape[:2], bool)
            for name in ("near_leg", "far_leg"):
                part = D.parts[name].copy()
                part[56:] = False
                y0, x0 = self.rig.oy + wy, self.rig.ox + wx
                m[y0:y0 + D.H, x0:x0 + D.W] |= part
            can = R.fill_under(can, m & (can[..., 3] == 0))
        return can


MS = {"idle": [140] * 8, "run": [125] * 8, "attack": [60, 60, 80, 90, 70, 73], "skill": [70, 80, 70, 70, 60, 50],
      "skill2": [70, 80, 70, 80, 70, 63], "ult": [60, 60, 60, 60, 60, 70, 70, 60], "hit": [100, 100],
      "dead": [100, 100, 120, 120, 120, 150, 150, 500], "flare": [60, 70, 70, 67]}
# each form's tags by role
TAGS = {"A": dict(idle="idle", run="run", attack="attack", skill="skill", skill2="skill2", hit="hit", dead="dead"),
        "B": dict(idle="b_idle", run="b_run", attack="r_attack", skill="r_skill", skill2="r_skill2", flare="r_flare",
                  hit="b_hit")}
# (no b_dead: Demonic Ascension ends with his life - the form's buff dies with him and the add-on shows A's death)


def frames(ps):
    out, role = {}, {}
    for form in ("A", "B"):
        t = TAGS[form]
        role.update({v: k for k, v in t.items()})
        p = lambda **k: ps.pose(form=form, **k)
        rest = None if form == "A" else 0
        bob = [0, 0, 1, 1, 1, 1, 0, 0]
        out[t["idle"]] = [p(arm=rest, up=(0, b)) for b in bob]
        out[t["run"]] = [p(arm=rest, up=(0, b), near=n, far=f, hem=h) for n, f, b, h, _ in WALK]
        # auto attack (League's Swain_Attack1: the demon hand flung forward, the raven bolt leaving it): leaning back,
        # the arm coming out ahead (pulled in), straight out on frame 3 (the release) with a step in, back down
        IN = (-3, 0)
        out[t["attack"]] = [p(arm=a, reach=r, whole=w) for a, r, w in
                            [(0, (0, 0), (-1, 0)), (90, IN, (0, 0)), (90, (0, 0), (1, 0)), (90, (0, 0), (1, 0)),
                             (90, IN, (0, 0)), (0, (0, 0), (0, 0))]]
        # Q Death's Hand (Swain_Spell1: a wide crouch, the claw thrust out ahead): the bolts leave on frame 3
        out[t["skill"]] = [p(arm=a, reach=r, up=(0, c), whole=(w, 0)) for a, r, c, w in
                           [(0, (0, 0), 1, 0), (90, IN, 2, 0), (90, (0, 0), 2, 1), (90, (0, 0), 2, 1), (90, IN, 1, 0),
                            (0, (0, 0), 0, 0)]]
        # E Nevermove (Swain_Spell3: the arm raised high, then thrown out ahead): the hand leaves on frame 3
        out[t["skill2"]] = [p(arm=a, reach=r, up=(0, c), whole=(w, 0)) for a, r, c, w in
                            [(180, (0, 0), 0, 0), (180, (0, 0), 0, -1), (90, (0, 0), 1, 1), (90, (0, 0), 1, 1),
                             (90, IN, 0, 0), (0, (0, 0), 0, 0)]]
        if form == "A":
            # R Demonic Ascension (Swain_DemonWindup -> Swain_DemonLand): crouch, leap - the demon from frame 4 on (the
            # kit starts the wings' aura at that frame: ULT_WINGS_AT) - land
            out["ult"] = [ps.pose("A", up=(0, 2)), ps.pose("A", arm=0, up=(0, 3)),
                          ps.pose("A", arm=90, reach=(-3, 0), whole=(0, -4)), ps.pose("B", arm=180, whole=(0, -7)),
                          ps.pose("B", arm=180, whole=(0, -5)), ps.pose("B", arm=90, whole=(0, -1)),
                          ps.pose("B", arm=0, up=(0, 2)), ps.pose("B", arm=0)]
            role["ult"] = "ult"
        else:
            # Demonflare: the claw raised, the nova (the effect), the claw down
            out[t["flare"]] = [p(arm=90, reach=(-3, 0)), p(arm=180), p(arm=180), p(arm=90, reach=(-3, 0))]
        out[t["hit"]] = [R.flash(p(arm=rest, whole=(-2, 0))), p(arm=rest, whole=(-1, 0))]
        if form == "B":
            # the wings: R's aura (view_buffs on league_swain_r_on plays this tag of his own sheet - league.dll draws it
            # dense like him, and its frames sit on his standing point like his own), flapping a row
            out["r_wings"] = [R.compose(ps.rig, [(ps.aura, dict(dy=d))]) for d in [0, 0, -1, -1, -1, -1, 0, 0]]
            role["r_wings"] = "idle"
            continue
        # the death (Swain_Death): he staggers, sinks to his knees with the demon claw raised, falls back
        knelt = p(arm=180, up=(0, 7), whole=(-2, 0))
        # he falls back: the kneeling figure with the arm let fall along his side, a quarter turn onto the ground
        lying = R.lie(ps.rig, p(up=(0, 7), whole=(-2, 0)), k=1, dx=-3)
        out[t["dead"]] = [p(whole=(-1, 0)), p(arm=90, reach=(-3, 0), up=(0, 4), whole=(-1, 0)),
                          p(arm=180, up=(0, 7), whole=(-1, 0)),
                          knelt, lying, lying.copy(), lying.copy(), lying.copy()]
    res = {}
    for tag, fr in out.items():
        ms = MS[role[tag]]
        if len(fr) != len(ms):
            sys.exit(f"{tag}: {len(fr)} frames for {len(ms)}")
        res[tag] = list(zip(fr, ms))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit", help="per-frame checks + every tag at 6x into this folder")
    a = ap.parse_args()
    D = design_a()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        R.Design.ruler(D, os.path.join(a.parts, f"{HERO}_parts.png"), z=10)
        can = aura_wings(D.px)
        body = pad(D.d)
        m = body[..., 3] > 0
        can[m] = body[m]
        arm = DemonArm().at(0)
        m = arm[..., 3] > 0
        can[m] = arm[m]
        Image.fromarray(np.repeat(np.repeat(can, 8, 0), 8, 1)).save(lp(os.path.join(a.parts, f"{HERO}_B_first.png")))
        return
    ps = Poser()
    acts = frames(ps)
    if a.audit:
        audit(ps, acts, a.audit)
        return
    if a.review:
        ps.rig.review(acts, a.review)
        return
    ps.rig.export(acts)


def audit(ps, acts, out_dir):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), the holes it closes in that the idle does not,
    colours that are in neither design nor the arm's picture; and each tag at 6x with the frame's number, every piece
    but the biggest red and every new hole magenta, for looking at."""
    from scipy import ndimage
    os.makedirs(out_dir, exist_ok=True)
    rig = ps.rig
    allowed = {tuple(c) for c in ps.D.d[ps.D.d[..., 3] > 0][:, :3].tolist()}
    b = load("design_B.png")
    allowed |= {tuple(c) for c in b[b[..., 3] > 0][:, :3].tolist()}
    for arm in ps.arm.cache.values():                    # the demon arm's own squares (from its picture)
        allowed |= {tuple(c) for c in arm[arm[..., 3] > 0][:, :3].tolist()}
    allowed |= {tuple(c) for c in EYES.values()} | {tuple(ps.D.outline)}
    idle = rig.finish(acts["idle"][0][0])
    iop = idle[..., 3] > 0
    idle_holes = ndimage.binary_fill_holes(iop) & ~iop
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            f = rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(idle_holes, iterations=3)
            cols = {tuple(v) for v in f[op][:, :3].tolist()}
            odd = cols - allowed
            # outline squares with no other colour beside them (4-neighbours): a stray black dot or a doubled line
            dark = op & (np.abs(f[..., :3].astype(int) - np.array(ps.D.outline)).sum(-1) < 30)
            other = op & ~dark
            orphan = dark & ~ndimage.binary_dilation(other, structure=R.CROSS)
            flag = "  <-- " if len(sz) > 1 or new.sum() or odd or orphan.sum() else ""
            print(f"{tag:9s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}{flag}")
            show = f.copy()
            if n > 1:
                big = 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
                show[(lbl > 0) & (lbl != big)] = (255, 0, 0, 255)
            show[new] = (255, 0, 255, 255)
            tiles.append(show)
        allc = np.stack(tiles)
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        z = 6
        sheet = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 8), (y1 - y0) * z + 16), (40, 40, 40))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(sheet)
        for i, t in enumerate(tiles):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
            sheet.paste(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST),
                        (i * ((x1 - x0) * z + 8), 16))
            dr.text((i * ((x1 - x0) * z + 8) + 2, 2), str(i + 1), fill=(255, 255, 0))
        sheet.save(lp(os.path.join(out_dir, f"{HERO}_{tag}_6x.png")))


if __name__ == "__main__":
    main()
