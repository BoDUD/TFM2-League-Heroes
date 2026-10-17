#!/usr/bin/env python3
"""league_anivia's action frames posed from the approved designs' own squares (the user, 2026-10-17: 「动作帧的话你参考
塔姆怎么做的 做到完美后喊我review 你也要自己review」; 2026-10-18 on the first rig: 「模型有点大 翅膀有点变形」).

    python tools/art/rig_anivia.py --parts DIR      # the designs with their parts tinted
    python tools/art/rig_anivia.py --review DIR     # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_anivia.py --audit DIR      # per-frame checks + every tag at 6x
    python tools/art/rig_anivia.py                  # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    (every mode takes --rows N: her height in game rows, default GAME_ROWS)

The designs: Codex's step-1 takes A-2 (read 91 x 57) and B-1 (read 46 x 32), brought to GAME_ROWS game rows at PPU
1.2 (the egg half of that) by design_anivia_cut.cut_to (whole rows / columns dropped, never the face's). The parts are
outlined on the reads and carried through the kept rows and columns, so another height is one number.
Every pose is rigid (memory no-deformation-lossless-poses): parts cut square by square from the design, moved by whole
squares and mirrored. The first rig also swayed the wings (whole columns lifted more toward the tip): every square was
kept, but the wing's outline and feather lines leaned and stepped - 「翅膀有点变形」 - so a wing now has two shapes only:
  as drawn   the near wing (image left) spread down to the ground, the far wing (image right) raised, its tip curling;
  mirrored   top to bottom about the root's row: the near wing raised high (drawn behind the head: a quarter turn piled
             its leading edge over the crown), the far wing pressed down, the tip lagging up.
A beat goes as drawn -> both up (the near wing mirrored) -> as drawn -> both down (the far wing mirrored), the whole bird
rising on the downstroke and bobbing between; nothing goes under the ground line.
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
import design_anivia_cut as DC  # noqa: E402

HERO = "anivia"
PPU = 1.2
GAME_ROWS = 38                  # her height in game rows (the user: 44 「模型有点大」 -> 38, tools/art/design_anivia_cut.py --sizes)


def lp(path):
    return R.lp(path)


class CutDesign:
    """What ppu_rig.Rig needs of a design: the squares, the standing point, the outline colour (rig_nasus.CutDesign)."""
    TURN_PAD = 0

    def __init__(self, d, px, kept):
        self.hero, self.ppu = HERO, PPU
        self.d = d
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = px
        self.kr, self.kc = kept
        self.outline = PD.edge_colour(d)
        self.parts, self.order, self.props = {}, [], set()

    def x(self, bx):
        """A read column -> this design's column (the nearest kept one)."""
        return int(np.searchsorted(self.kc, bx))

    def y(self, by):
        return int(np.searchsorted(self.kr, by))

    def poly(self, pts, base_shape):
        """An outline drawn on the read (base_shape) -> this design's squares inside it."""
        img = Image.new("L", (base_shape[1], base_shape[0]), 0)
        ImageDraw.Draw(img).polygon([(x, y) for x, y in pts], fill=1, outline=1)
        m = np.asarray(img, bool)[np.ix_(self.kr, self.kc)]
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

    def layer(self, name):
        m = self.parts[name] if name != "rest" else self.rest()
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


# ------------------------------------------------------------------------------------------------- the parts (on the reads)
# A (read 91 x 57). The core: the crown's spikes, the face, the neck and the body (navy), the violet back marking and
# both talons. The near wing lies in front of the body's left side; its trailing feathers sweep down under the talons
# to the lowest tip and turn with it; the talons are drawn over them. The far wing starts at the dark outline between the
# crown's last spike and its root.
READ_A = (57, 91)
CORE_A = [(39, 17), (44, 12), (50, 11), (57, 12), (57, 28), (60, 35), (65, 36), (65, 48), (51, 48), (43, 47), (40, 39),
          (38, 32), (37, 24)]
FAR_A = [(57, 0), (91, 0), (91, 57), (64, 57), (64, 36), (58, 35), (56, 28), (56, 13)]
NEAR_ROOT_A = (41, 23)          # the row the near wing is mirrored about when raised
FAR_ROOT_A = (58, 23)
TALON_ROW_A = 38                # the core's squares from this row down are the talons, laid over the near wing
PX_A = 48                       # the standing point's column (under the body)
# B (read 46 x 32): the egg's oval; the nest's crystals the rest; the egg's rows above EGG_SPLIT_B lift off as she hatches
READ_B = (32, 46)
EGG_B = [(18, 0), (26, 0), (32, 5), (34, 10), (34, 19), (32, 21), (15, 21), (13, 19), (13, 10), (15, 5)]
EGG_SPLIT_B = 10
PX_B = 22

_CUTS = {}


def cuts(rows):
    if rows not in _CUTS:
        _CUTS[rows] = DC.cut_to(rows)
    return _CUTS[rows]


def design_a(rows=GAME_ROWS):
    d, kr, kc = cuts(rows)["A"]
    D = CutDesign(d, 0, (kr, kc))
    D.px = D.x(PX_A)
    D.part("far", D.poly(FAR_A, READ_A))
    D.part("core", D.poly(CORE_A, READ_A))
    D.part("near", D.rest())
    D.near_root = (D.x(NEAR_ROOT_A[0]), D.y(NEAR_ROOT_A[1]))
    D.far_root = (D.x(FAR_ROOT_A[0]), D.y(FAR_ROOT_A[1]))
    D.talon_row = D.y(TALON_ROW_A)
    return D


def design_b(rows=GAME_ROWS):
    d, kr, kc = cuts(rows)["B"]
    D = CutDesign(d, 0, (kr, kc))
    D.px = D.x(PX_B)
    D.part("egg", D.poly(EGG_B, READ_B))
    D.part("nest", D.rest())
    D.split = D.y(EGG_SPLIT_B)
    return D


def tinted(D, z=8):
    """The design with each part tinted, at z x, with a ruler every 5 squares."""
    col = {"core": (255, 80, 80), "near": (80, 255, 80), "far": (80, 120, 255), "egg": (255, 80, 80),
           "nest": (80, 255, 80)}
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
    """ppu_rig.Rig whose finish also drops the lone outline squares a pose made (where two parts meet in a new way the
    outline pass can leave a single square standing off the figure; in a loop such squares come and go along the edge):
    every lone outline square but the design's own (alpha KEEP, moved with their part), one at a time while the figure
    stays one piece."""

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
    face, body), the near wing, the talons."""

    def __init__(self, D, pad_=(24, 24, 40, 12)):
        self.D = D
        self.rig = CleanRig(D, pad=pad_)
        core = D.parts["core"]
        rows = np.arange(D.H)[:, None]
        self.talons_m = core & (rows >= D.talon_row)
        self.upper_m = core & ~self.talons_m
        self.L = {"far": only(D, D.parts["far"]), "upper": only(D, self.upper_m), "near": only(D, D.parts["near"]),
                  "talons": only(D, self.talons_m)}

    def mirrored(self, name):
        root = self.D.near_root if name == "near" else self.D.far_root
        return dict(flip=True, rot=2, about=(root[0] + 0.5, root[1] + 0.5))

    def pose(self, up=False, down=False, body=0, whole=(0, 0), sink=0):
        """up: the near wing raised (mirrored, behind the head); down: the far wing pressed down (mirrored); body: rows
        the whole bird rises (never lowered: her lowest feather is on the ground line); whole: (dx, dy) more; sink: rows
        the crown, face and body (and the far wing on them) settle down over the near wing and the talons (the death)."""
        dx, dy = whole
        dy -= body
        far_l = (self.L["far"], dict(self.mirrored("far") if down else {}, dx=dx, dy=dy + sink))
        upper_l = (self.L["upper"], dict(dx=dx, dy=dy + sink))
        near_l = (self.L["near"], dict(self.mirrored("near") if up else {}, dx=dx, dy=dy))
        talons_l = (self.L["talons"], dict(dx=dx, dy=dy))
        layers = [far_l, near_l, upper_l, talons_l] if up else [far_l, upper_l, near_l, talons_l]
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

    def __init__(self, bird, rows=GAME_ROWS):
        D = design_b(rows)
        ra = bird.rig
        left, top = ra.CX - D.px, ra.GY - D.ground
        self.D = D
        self.rig = CleanRig(D, pad=(left, ra.CW - left - D.W, top, ra.CH - top - D.H))
        rr = np.arange(D.H)[:, None]
        egg = D.parts["egg"]
        self.L = {"nest": only(D, D.parts["nest"]), "top": only(D, egg & (rr < D.split)),
                  "bottom": only(D, egg & (rr >= D.split))}

    def pose_nest(self):
        """The nest alone (the egg gone: she has burst out)."""
        return R.compose(self.rig, [(self.L["nest"], {})])

    def pose(self, dx=0, lift=0):
        """The egg on its nest moved dx columns; lift: rows the egg's top half rises off its bottom (the crack)."""
        return R.compose(self.rig, [(self.L["bottom"], dict(dx=dx)), (self.L["top"], dict(dx=dx, dy=-lift)),
                                    (self.L["nest"], dict(dx=dx))])


def form_a(rows=GAME_ROWS):
    return Bird(design_a(rows))


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
MS = {"idle": [150] * 8, "run": [95] * 8, "attack": [80, 85, 70, 90, 80, 62], "skill": [70, 75, 70, 90, 95],
      "skill2": [70, 75, 80, 90, 85], "ult": [80, 85, 85, 80, 70], "hit": [100, 100],
      "dead": [100, 120, 120, 120, 150, 150, 150, 500], "egg_in": [70, 80, 90], "egg": [540], "egg_idle": [500],
      "egg_hit": [100, 100], "hatch": [60, 70, 85, 85]}


def frames_a(F):
    p = F.pose
    o = F.D.outline
    out = {}
    # hovering (League's anivia_idle1 is a slow, full beat): as drawn, both wings up, as drawn, both down, the bird
    # rising a row as they lift and two as they press
    out["idle"] = [p(), p(body=1), p(up=True, body=1), p(up=True, body=2), p(body=2), p(body=1), p(down=True, body=2),
                   p(down=True, body=1)]
    # flying (anivia_run): the same beat, faster
    out["run"] = [p(), p(up=True), p(up=True, body=1), p(body=1), p(down=True, body=2), p(down=True, body=3),
                  p(body=2), p(body=1)]
    # the attack (anivia_attack1): the wings raised and drawn back, then beaten down as the bolt leaves (frame 3)
    out["attack"] = [p(whole=(-1, 0)), p(up=True, whole=(-2, 0)), p(down=True, whole=(1, 0), body=2),
                     p(down=True, whole=(1, 0), body=2), p(body=1), p()]
    # Q Flash Frost (anivia_spell1): both wings up and back, then the beat that flings the ball (frame 3)
    out["skill"] = [p(up=True, whole=(-1, 0)), p(up=True, whole=(-2, 0), body=1), p(down=True, whole=(2, 0), body=3),
                    p(down=True, whole=(2, 0), body=3), p(whole=(1, 0), body=1)]
    # E Frostbite (anivia_spell3): a quick beat toward the target (the shard on frame 3)
    out["skill2"] = [p(), p(up=True, whole=(-1, 0)), p(down=True, whole=(1, 0), body=1),
                     p(down=True, whole=(1, 0), body=1), p()]
    # R Glacial Storm (anivia_spell4): both wings flung up and held as the storm falls (tick 10), then down
    out["ult"] = [p(), p(up=True, body=1), p(up=True, body=2), p(up=True, body=2), p(body=1)]
    out["hit"] = [flash(p(whole=(-2, 0)), o), p(whole=(-1, 0))]
    # the death (anivia_death): a last beat up, then she drops with the far wing limp and settles on the ground
    lie = p(down=True, sink=5)
    out["dead"] = [p(body=1), p(up=True, body=2), p(down=True, body=1), p(down=True, sink=2), p(down=True, sink=4), lie,
                   lie.copy(), lie.copy()]
    return out


def frames_egg(F, E):
    """The add-on's egg (League's AniviaEgg, still in its nest): curling in, held, struck, hatching (the egg's cap
    lifted off its bottom: a crack, then the cap thrown up as she bursts out with her wings up)."""
    p, e = F.pose, E.pose
    out = {}
    out["egg_in"] = [p(down=True, body=1), e(), e()]
    out["egg"] = [e()]
    out["egg_idle"] = [e()]
    out["egg_hit"] = [flash(e(dx=-1), E.D.outline), e()]
    out["hatch"] = [e(lift=1), e(lift=3), over(E.pose_nest(), p(up=True, body=2)), p()]
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


def audit(F, E, acts, out_dir, loops=("idle", "run")):
    """Every frame after the rig's finish(): its pieces (8-connected), enclosed holes beyond the drawn pose's, colours in
    no design, outline squares with no colour beside them (more than the drawn pose has), the squares under the ground
    line; in the loops, one-frame blinks (squares filled in the frames before and after, empty in this one, inside its
    own silhouette). Each tag at 6x: every piece but the biggest red, new holes magenta, orphan outline orange, blinks
    cyan (rig_nasus.audit, memory review-run-blinks)."""
    from scipy import ndimage
    os.makedirs(lp(out_dir), exist_ok=True)
    rig = F.rig
    o = np.array(F.D.outline)
    allowed = set()
    for d in (F.D.d, E.D.d):
        allowed |= {tuple(c) for c in d[d[..., 3] > 0][:, :3].tolist()}
    allowed |= {tuple(F.D.outline)}

    def look(f):
        op = f[..., 3] > 0
        dark = op & (np.abs(f[..., :3].astype(int) - o).sum(-1) < 30)
        orphan = dark & ~ndimage.binary_dilation(op & ~dark, structure=np.ones((3, 3)))
        holes = ndimage.binary_fill_holes(op) & ~op
        return op, orphan, holes
    _, orphan0, holes0 = look(rig.finish(F.pose()))
    _, orphan_e, holes_e = look(rig.finish(E.pose()))
    bad = 0
    for tag, fr in acts.items():
        fins = [rig.finish(c) for c, _ in fr]
        tiles = []
        for i, f in enumerate(fins):
            op, orphan, holes = look(f)
            egg = op.sum() < 0.5 * (F.D.d[..., 3] > 0).sum()
            base_orphan = int((orphan_e if egg else orphan0).sum())
            base_holes = int((holes_e if egg else holes0).sum())
            new = holes if holes.sum() > base_holes + 2 else np.zeros_like(holes)
            if tag == "hatch" and i == 2:               # she bursts out over the nest: the air between is no hole
                new = np.zeros_like(new)
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
    ap.add_argument("--rows", type=int, default=GAME_ROWS, help="her height in game rows")
    a = ap.parse_args()
    F = form_a(a.rows)
    E = Egg(F, a.rows)
    if a.parts:
        os.makedirs(lp(a.parts), exist_ok=True)
        tinted(F.D).convert("RGB").save(lp(os.path.join(a.parts, f"{HERO}_A_parts.png")))
        tinted(E.D, z=14).convert("RGB").save(lp(os.path.join(a.parts, f"{HERO}_B_parts.png")))
        for D, f in ((F.D, F), (E.D, E)):
            ref = f.rig.canvas()
            ref[f.rig.oy:f.rig.oy + D.H, f.rig.ox:f.rig.ox + D.W] = D.d
            got = f.rig.finish(f.pose())
            print(f"{D.W}x{D.H}: rest pose (finished) vs design: squares differing",
                  int((np.abs(got.astype(int) - f.rig.finish(ref).astype(int)).sum(-1) > 0).sum()))
        return
    acts = frames(F, E)
    if a.audit:
        audit(F, E, acts, a.audit)
        return
    if a.review:
        F.rig.review(acts, a.review)
        return
    F.rig.export(acts)


if __name__ == "__main__":
    main()
