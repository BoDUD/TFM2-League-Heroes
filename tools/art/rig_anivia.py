#!/usr/bin/env python3
"""league_anivia's action frames posed from the approved designs' own squares (the user, 2026-10-17: 「动作帧的话你参考
塔姆怎么做的 做到完美后喊我review 你也要自己review」).

    python tools/art/rig_anivia.py --parts DIR      # the designs with their parts tinted
    python tools/art/rig_anivia.py --review DIR     # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_anivia.py --audit DIR      # per-frame checks + every tag at 6x
    python tools/art/rig_anivia.py                  # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_anivia_cut.py: Codex's step-1 takes A-2 and B-1 brought to 53 and 26 rows, PPU 1.2, by
whole rows / columns dropped, never the face's): A the cryophoenix (85 x 53 squares, the crown's top row 0, the near
wing's lowest tip row 52), B the Rebirth egg on its ice nest (37 x 26). Every pose is lossless (memory
no-deformation-lossless-poses): parts cut square by square from the design and only moved by whole squares, mirror
images and ppu_rig.sway (whole columns lifted more toward a wing's free end - the flap; every column's squares kept).
Parts of A: the core (crown, face, neck, body, the violet back marking, both talons), the near wing (image left, spread
down to the ground) with its trailing feathers, and the far wing (image right, raised, its tip curling down). A wing
turns about its root:
  sway   the columns lifted up to k rows at the free end, nothing at the root (a flap of a few rows);
  flip   mirrored top to bottom about the root's row (the near wing raised high, the far wing pressed down: the ends of
         a beat - League's idle and run go from both wings up in a V to both pressed under her).
The body rides a beat: up as the wings press down, down as they rise, so a tip never goes under the ground line.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "anivia"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "anivia", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign:
    """What ppu_rig.Rig needs of a design: the squares, the standing point, the outline colour (rig_nasus.CutDesign)."""
    TURN_PAD = 0

    def __init__(self, d, px):
        self.hero, self.ppu = HERO, PPU
        self.d = d
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = px
        self.outline = PD.edge_colour(d)
        self.parts, self.order, self.props = {}, [], set()

    def poly(self, pts):
        img = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(img).polygon([(x, y) for x, y in pts], fill=1, outline=1)
        return np.asarray(img, bool) & (self.d[..., 3] > 0)

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

    def layer(self, name):
        m = self.parts[name] if name != "rest" else self.rest()
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


# ------------------------------------------------------------------------------------------------- design A
# The core: the crown's spikes, the face, the neck and the body (navy), the violet back marking and both talons. The
# near wing lies in front of the body's left side; its trailing feathers sweep down under the talons to the lowest tip
# (row 52, columns 47-48) and turn with it (left hanging when it rose they read as a loose shard); the talons are drawn
# over them. The far wing starts at column 54 (the dark outline between the crown's last spike
# and the wing's root).
CORE_A = [(36, 15), (41, 11), (47, 10), (54, 11), (54, 26), (56, 33), (60, 34), (60, 45), (48, 45), (40, 44),
          (37, 36), (35, 30), (34, 22)]
FAR_A = [(54, 0), (85, 0), (85, 53), (59, 53), (59, 34), (55, 33), (53, 26), (53, 12)]
NEAR_ROOT_A = (38, 21)          # where the near wing leaves the body (the row it is mirrored about when raised)
NEAR_SWAY_A = 30                # the near wing's sway leaves its columns from here on still (the inner feathers by the
                                # body and the trailing tip on the ground line)
FAR_ROOT_A = (55, 21)
TALON_ROW_A = 35                # the core's squares from this row down are the talons, laid over the near wing


def design_a():
    d = load("design_A.png")
    D = CutDesign(d, px=45)
    D.part("far", D.poly(FAR_A))
    D.part("core", D.poly(CORE_A))
    D.part("near", D.rest())
    return D


# ------------------------------------------------------------------------------------------------- design B (the egg)
EGG_B = [(15, 0), (21, 0), (26, 4), (28, 8), (28, 15), (26, 17), (12, 17), (10, 15), (10, 8), (12, 4)]
EGG_SPLIT_B = 8                 # the egg's rows above this lift off when she hatches (the crack)


def design_b():
    d = load("design_B.png")
    D = CutDesign(d, px=18)
    D.part("egg", D.poly(EGG_B))
    D.part("nest", D.rest())
    return D


def tinted(D, z=8):
    """The design with each part tinted, at z x, with a ruler every 5 squares."""
    col = {"core": (255, 80, 80), "near": (80, 255, 80), "far": (80, 120, 255),            "egg": (255, 80, 80), "nest": (80, 255, 80)}
    out = D.d.copy()
    for name, m in D.parts.items():
        c = np.array(col[name])
        out[m, :3] = (out[m, :3].astype(int) * 0.55 + c * 0.45).astype(np.uint8)
    img = Image.fromarray(np.repeat(np.repeat(out, z, 0), z, 1))
    can = Image.new("RGBA", (img.width + 30, img.height + 30), (230, 230, 230, 255))
    can.alpha_composite(img, (30, 30))
    dr = ImageDraw.Draw(can)
    for x in range(0, D.W + 1, 5):
        dr.line([(30 + x * z, 30), (30 + x * z, 30 + D.H * z)], fill=(0, 0, 0, 90))
        dr.text((30 + x * z + 2, 4), str(x), fill=(0, 0, 0, 255))
    for y in range(0, D.H + 1, 5):
        dr.line([(30, 30 + y * z), (30 + D.W * z, 30 + y * z)], fill=(0, 0, 0, 90))
        dr.text((2, 30 + y * z + 2), str(y), fill=(0, 0, 0, 255))
    return can


# ------------------------------------------------------------------------------------------------- poses
KEEP = 254                      # alpha of the design's own lone outline squares (the crown's spike tips, feather tips)


def lone(a, outline):
    """Outline squares with no coloured square among their 8 neighbours."""
    from scipy import ndimage
    op = a[..., 3] > 0
    dark = op & (np.abs(a[..., :3].astype(int) - np.array(outline)).sum(-1) < 30)
    return dark & ~ndimage.binary_dilation(op & ~dark, structure=np.ones((3, 3)))


def only(D, m):
    out = np.zeros_like(D.d)
    out[m] = D.d[m]
    out[m & lone(D.d, D.outline), 3] = KEEP
    return out


class CleanRig(R.Rig):
    """ppu_rig.Rig whose finish also drops the lone outline squares a pose made (a sway's steps leave single outline
    corners standing off the figure; in a loop they come and go along the edge): every lone outline square but the
    design's own (alpha KEEP, moved with their part), one at a time while the figure stays one piece."""

    def finish(self, can):
        from scipy import ndimage
        out = super().finish(can)
        o = self.D.outline
        for _ in range(3):
            cand = lone(out, o) & (out[..., 3] == 255)
            if not cand.any():
                break
            for y, x in zip(*np.nonzero(cand)):
                op = out[..., 3] > 0
                n0 = ndimage.label(op, structure=np.ones((3, 3)))[1]
                op[y, x] = False
                if ndimage.label(op, structure=np.ones((3, 3)))[1] <= n0:
                    out[y, x] = 0
        out[out[..., 3] == KEEP, 3] = 255
        return out


class Bird:
    """Design A on its rig with the layers a pose moves (back to front): the far wing, the core's upper part (crown,
    face, body), the near wing, its trailing feathers, the talons."""

    def __init__(self, D, pad_=(24, 24, 34, 12)):
        self.D = D
        self.rig = CleanRig(D, pad=pad_)
        core = D.parts["core"]
        rows = np.arange(D.H)[:, None]
        self.talons_m = core & (rows >= TALON_ROW_A)
        self.upper_m = core & ~self.talons_m
        self.L = {"far": only(D, D.parts["far"]), "upper": only(D, self.upper_m), "near": only(D, D.parts["near"]),
                  "talons": only(D, self.talons_m)}

    def wing(self, name, how):
        """One wing's options: how = k (swayed: k rows at the free end, + up), "up" (the near wing mirrored top to bottom
        about its root's row: raised high and out to the left, drawn behind the head - at game size the clearest of the
        raises tried: a quarter turn piled the wing's leading edge over the crown, a sway of 10-14 rows only leans it)
        or "flip" (the far wing mirrored the same way: pressed down, the tip lagging up)."""
        root = NEAR_ROOT_A if name == "near" else FAR_ROOT_A
        about = (root[0] + 0.5, root[1] + 0.5)
        if how in ("up", "flip"):
            return dict(flip=True, rot=2, about=about)
        if how:
            return dict(sway=(0, NEAR_SWAY_A, how, "right") if name == "near" else (root[0], self.D.W - 1, how, "left"))
        return {}

    def pose(self, near=0, far=0, body=0, whole=(0, 0), sink=0):
        """near / far: Bird.wing's how; body: rows the whole bird rises (never lowered: her lowest feather is on the
        ground line); whole: (dx, dy) more; sink: rows the crown, face and body (and the far wing on them) settle down
        over the near wing and the talons (the death)."""
        dx, dy = whole
        dy -= body
        far_l = (self.L["far"], dict(self.wing("far", far), dx=dx, dy=dy + sink))
        upper_l = (self.L["upper"], dict(dx=dx, dy=dy + sink))
        near_l = (self.L["near"], dict(self.wing("near", near), dx=dx, dy=dy))
        talons_l = (self.L["talons"], dict(dx=dx, dy=dy))
        # raised, the near wing's inner feathers turn up over the crown: the head stays in front of it then
        layers = [far_l, near_l, upper_l, talons_l] if near == "up" else [far_l, upper_l, near_l, talons_l]
        return R.compose(self.rig, layers)


def flash(can, outline, k=0.45):
    """A hit's flash: every square but the outline brightened (ppu_rig.flash lightens the outline too, and the
    finish then draws a second one round it)."""
    out = can.copy()
    m = (out[..., 3] > 0) & (np.abs(out[..., :3].astype(int) - np.array(outline)).sum(-1) > 30)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


class Egg:
    """Design B on a canvas of A's size with its standing point on A's (one sheet, one pivot for both)."""

    def __init__(self, bird):
        D = design_b()
        ra = bird.rig
        left, top = ra.CX - D.px, ra.GY - D.ground
        self.D = D
        self.rig = CleanRig(D, pad=(left, ra.CW - left - D.W, top, ra.CH - top - D.H))
        rows = np.arange(D.H)[:, None]
        egg = D.parts["egg"]
        self.L = {"nest": only(D, D.parts["nest"]), "top": only(D, egg & (rows < EGG_SPLIT_B)),
                  "bottom": only(D, egg & (rows >= EGG_SPLIT_B))}

    def pose_nest(self):
        """The nest alone (the egg gone: she has burst out)."""
        return R.compose(self.rig, [(self.L["nest"], {})])

    def pose(self, dx=0, lift=0):
        """The egg on its nest moved dx columns; lift: rows the egg's top half rises off its bottom (the crack)."""
        return R.compose(self.rig, [(self.L["bottom"], dict(dx=dx)), (self.L["top"], dict(dx=dx, dy=-lift)),
                                    (self.L["nest"], dict(dx=dx))])


def form_a():
    return Bird(design_a())


def over(*cans):
    """Canvases laid back to front."""
    out = cans[0].copy()
    for c in cans[1:]:
        m = c[..., 3] > 0
        out[m] = c[m]
    return out


def sheet(cans, path, z=4, rig=None):
    """Canvases side by side at z x on grey, the ground line red."""
    allc = np.stack(cans)
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, max(ys.max() + 3, (rig.GY + 2) if rig else 0), xs.min() - 2, xs.max() + 3
    tiles = []
    for c in cans:
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(c[y0:y1, x0:x1]))
        if rig:
            ImageDraw.Draw(bg).line([(0, rig.GY - y0), (x1 - x0, rig.GY - y0)], fill=(200, 60, 60, 255))
        tiles.append(bg.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
    out = Image.new("RGB", (sum(t.width + 8 for t in tiles), tiles[0].height), (40, 40, 40))
    x = 0
    for t in tiles:
        out.paste(t.convert("RGB"), (x, 0))
        x += t.width + 8
    out.save(lp(path))


# ------------------------------------------------------------------------------------------------- the actions
# Timings: the kit's (tools/kit/build_anivia.py) - the attack 28 ticks, the bolt released on tick 10 (frame 3 from
# 165 ms); Q and E 24 ticks, released on tick 9 (frame 3 from 145-150 ms); R's cast 24 ticks, the storm on tick 10; the
# add-on's egg: egg_in 12 (+2) ticks, the egg's loop re-issued every 30 ticks (32), hatch 18 ticks.
MS = {"idle": [125] * 8, "run": [95] * 8, "attack": [80, 85, 70, 90, 80, 62], "skill": [70, 75, 70, 90, 95],
      "skill2": [70, 75, 80, 90, 85], "ult": [80, 85, 85, 80, 70], "hit": [100, 100],
      "dead": [100, 120, 120, 120, 150, 150, 150, 500], "egg_in": [70, 80, 90], "egg": [540], "egg_idle": [500],
      "egg_hit": [100, 100], "hatch": [60, 70, 85, 85]}


def beat(F, n, up, down, rise, lag=0):
    """A wing beat in n frames: the wings' tips swing up to `up` rows over the drawn pose and `down` rows under it (up
    first), the body rising `rise` rows as they press down; lag: the near wing that many frames behind."""
    out = []
    for i in range(n):
        ph = np.sin(2 * np.pi * i / n)
        pn = np.sin(2 * np.pi * (i - lag) / n)
        k = lambda v: int(round(v * (up if v > 0 else down)))
        out.append(F.pose(near=k(pn), far=k(ph), body=int(round(rise * max(0.0, -ph)))))
    return out


def frames_a(F):
    p = F.pose
    o = F.D.outline
    out = {}
    # hovering (League's anivia_idle1 is a slow, full beat): the tips 7 rows up and 5 down, the body up to 2 rows on the
    # downstroke (4 rows each way read as a still bird on the ban/pick card)
    out["idle"] = beat(F, 8, 7, 5, 2)
    # flying (anivia_run): the drawn pose -> both wings up (the near wing spread up and out) -> both pressed down (the
    # far wing mirrored under, the near wing swung down), the body up as they press
    out["run"] = [p(), p(near=6, far=6), p(near="up", far=8), p(near="up", far=4, body=1), p(near=2, body=1),
                  p(near=-6, far=-3, body=2), p(near=-6, far="flip", body=3), p(near=-3, far="flip", body=2)]
    # the attack (anivia_attack1): the wings raised and drawn back, then beaten down as the bolt leaves (frame 3)
    out["attack"] = [p(near=4, far=4, whole=(-1, 0)), p(near="up", far=8, whole=(-2, 0)),
                     p(near=-6, far="flip", whole=(1, 0), body=2), p(near=-6, far="flip", whole=(1, 0), body=2),
                     p(near=-2, far=-1, body=1), p()]
    # Q Flash Frost (anivia_spell1): a big upswing, both wings up, then the beat that flings the ball (frame 3)
    out["skill"] = [p(near=6, far=6, whole=(-1, 0)), p(near="up", far=8, whole=(-2, 0)),
                    p(near=-7, far="flip", whole=(2, 0), body=3), p(near=-7, far="flip", whole=(2, 0), body=3),
                    p(near=-3, far=-1, whole=(1, 0), body=1)]
    # E Frostbite (anivia_spell3): a quick flick of the wings toward the target (the shard on frame 3)
    out["skill2"] = [p(near=3, far=4), p(near=6, far=8, whole=(-1, 0)), p(near=-5, far=-3, whole=(1, 0), body=1),
                     p(near=-5, far=-3, whole=(1, 0), body=1), p(near=-2)]
    # R Glacial Storm (anivia_spell4): both wings flung up high and held as the storm falls (tick 10), then down
    out["ult"] = [p(near=5, far=5), p(near="up", far=8, body=1), p(near="up", far=8, body=1),
                  p(near="up", far=4, body=1), p(near=2, far=2)]
    out["hit"] = [flash(p(near=3, far=3, whole=(-2, 0)), o), p(near=1, far=1, whole=(-1, 0))]
    # the death (anivia_death): a last beat up, then she drops with the wings spread limp and settles on the ground
    lie = p(near=-6, far="flip", sink=5)
    out["dead"] = [p(near=4, far=4, body=1), p(near="up", far=8, body=2), p(near=-6, far="flip", body=1),
                   p(near=-6, far="flip", sink=2), p(near=-6, far="flip", sink=4), lie, lie.copy(), lie.copy()]
    return out


def frames_egg(F, E):
    """The add-on's egg (League's AniviaEgg, still in its nest): curling in, held, struck, hatching (the egg's cap
    lifted off its bottom: a crack, then the cap thrown up as she bursts out with her wings up)."""
    p, e = F.pose, E.pose
    out = {}
    out["egg_in"] = [p(near=-6, far="flip", body=1), e(), e()]
    out["egg"] = [e()]
    out["egg_idle"] = [e()]
    out["egg_hit"] = [flash(e(dx=-1), E.D.outline), e()]
    out["hatch"] = [e(lift=1), e(lift=3), over(E.pose_nest(), p(near="up", far=8, body=2)), p(near=4, far=4)]
    return out


def frames(F, E):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    acts = {**frames_a(F), **frames_egg(F, E)}
    out = {}
    for tag, ms in MS.items():
        cans = acts[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def audit(F, acts, out_dir, loops=("idle", "run")):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), enclosed holes the drawn pose (idle 1) does not
    have, colours in no design, outline squares with no colour beside them (more than the drawn pose has), the squares
    under the ground line; in the loops, one-frame blinks (squares filled in the frames before and after, empty in this
    one, inside the figure). Each tag at 6x: every piece but the biggest red, new holes magenta, orphan outline orange,
    blinks cyan (rig_nasus.audit, memory review-run-blinks)."""
    from scipy import ndimage
    os.makedirs(lp(out_dir), exist_ok=True)
    rig = F.rig
    o = np.array(F.D.outline)
    allowed = set()
    for d in (F.D.d, design_b().d):
        allowed |= {tuple(c) for c in d[d[..., 3] > 0][:, :3].tolist()}
    allowed |= {tuple(F.D.outline)}

    def look(f):
        op = f[..., 3] > 0
        dark = op & (np.abs(f[..., :3].astype(int) - o).sum(-1) < 30)
        orphan = dark & ~ndimage.binary_dilation(op & ~dark, structure=np.ones((3, 3)))
        holes = ndimage.binary_fill_holes(op) & ~op
        return op, orphan, holes
    _, orphan0, holes0 = look(rig.finish(F.pose()))
    e0 = Egg(F)
    _, orphan_e, holes_e = look(rig.finish(e0.pose()))
    bad = 0
    for tag, fr in acts.items():
        fins = [rig.finish(c) for c, _ in fr]
        tiles = []
        for i, f in enumerate(fins):
            op, orphan, holes = look(f)
            egg = op.sum() < 1000                       # the egg's frames (the bird's are ~2400 squares)
            base_orphan = int((orphan_e if egg else orphan0).sum())
            base_holes = int((holes_e if egg else holes0).sum())
            new = holes if holes.sum() > base_holes + 2 else np.zeros_like(holes)
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - allowed
            under = int(op[rig.GY:].sum())
            blink = np.zeros_like(op)
            if tag in loops and len(fins) > 2:
                a_, b_ = fins[i - 1][..., 3] > 0, fins[(i + 1) % len(fins)][..., 3] > 0
                blink = a_ & b_ & ~op & ndimage.binary_fill_holes(op)
                blink &= ndimage.binary_erosion(a_ & b_, structure=np.ones((3, 3)))
            cap = tag == "hatch" and i == 1             # the egg's cap thrown off: two pieces on purpose
            if tag == "hatch" and i == 2:               # she bursts out over the nest: the air between is no hole
                new = np.zeros_like(new)
            flag = ((len(sz) > 1 and not cap) or (odd and "hit" not in tag) or under or new.sum()
                    or orphan.sum() > base_orphan or blink.sum())
            bad += bool(flag)
            print(f"{tag:9s} {i + 1}: pieces {sz[:3]} new holes {int(new.sum())} orphan {int(orphan.sum())}/{base_orphan} "
                  f"blinks {int(blink.sum())} odd {len(odd)} under {under}{'  <--' if flag else ''}")
            show = f.copy()
            if n > 1:
                big = 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
                show[(lbl > 0) & (lbl != big)] = (255, 0, 0, 255)
            show[new] = (255, 0, 255, 255)
            show[orphan] = (255, 140, 0, 255)
            show[blink] = (0, 255, 255, 255)
            tiles.append(show)
        sheet(tiles, os.path.join(out_dir, f"{HERO}_{tag}_6x.png"), z=6, rig=rig)
    print("frames flagged:", bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    F = form_a()
    E = Egg(F)
    if a.parts:
        os.makedirs(lp(a.parts), exist_ok=True)
        tinted(F.D).convert("RGB").save(lp(os.path.join(a.parts, f"{HERO}_A_parts.png")))
        tinted(E.D, z=14).convert("RGB").save(lp(os.path.join(a.parts, f"{HERO}_B_parts.png")))
        ref = F.rig.canvas()
        ref[F.rig.oy:F.rig.oy + F.D.H, F.rig.ox:F.rig.ox + F.D.W] = F.D.d
        print("A rest pose vs design: squares differing", int((np.abs(F.pose().astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
        ref = E.rig.canvas()
        ref[E.rig.oy:E.rig.oy + E.D.H, E.rig.ox:E.rig.ox + E.D.W] = E.D.d
        print("B rest pose vs design: squares differing", int((np.abs(E.pose().astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
        return
    acts = frames(F, E)
    if a.audit:
        audit(F, acts, a.audit)
        return
    if a.review:
        F.rig.review(acts, a.review)
        return
    F.rig.export(acts)


if __name__ == "__main__":
    main()
