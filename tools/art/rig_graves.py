#!/usr/bin/env python3
"""league_graves's action frames, posed from the approved designs' own squares and Codex's poses on skeletons.

    python tools/art/rig_graves.py --parts DIR       # the side design with its parts tinted (12x)
    python tools/art/rig_graves.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_graves.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_graves.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_graves_model.py, the user's picks 2026-10-20: A-1 and side-2, 38 game px hair to soles at
PPU 1.5 = 57 rows; one palette, one head): idle.png (3/4 front, 67 x 57) and side.png (side-on facing right with the
idle's head, 74 x 57: every action's base). Lossless: parts cut square by square from a design, moved by whole
squares only; the shotgun is never turned off the level by the rig (a tipped gun comes from Codex's poses, drawn
straight: pack_graves_poses.py / design_graves_poses.py).
Parts of the side design: the legs under the belt (LEG_BAND: the back leg to LEG_SPLIT, the front leg past it); the rest
is the body (head, scarf, pauldron, torso, arms and the shotgun with both hands on it - the gun's golds and steel are
mixed square by square with the hands, the sleeves and the trousers' top, so it never moves apart from the body).
The walk is league_nautilus's / league_braum's approved walk (the heavy heroes' rule, memory run-legs-caitlyn-way: Galio's
final ruling): the design's own legs cut under the belt, one lifted per frame by losing its top rows and set a little
forward, the body floating a row; no part turned, sheared or redrawn.
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
from rig_wukong import CutDesign as _Cut, P, pad, sheet  # noqa: E402

HERO = "graves"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "graves", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the side's parts
STAND = 33                     # the column between his boots: the standing point
LEG_BAND = 41                  # the belt's lowest row: the legs start below it
LEG_SPLIT = 33                 # the column between the legs (back leg to it, front leg past it)
MUZZLE = (73, 30)              # the muzzle's middle (design square): the flash is laid here
IDLE_STAND = 33                # the idle design's standing column (between its boots)
IDLE_LEG_ROW = 41              # the idle design's legs from this row stay while the body breathes


def design():
    d = load("side.png")
    D = CutDesign(d, px=STAND)
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    D.part("back_leg", D.box(LEG_BAND + 1, D.H - 1, 0, LEG_SPLIT))
    D.part("front_leg", D.box(LEG_BAND + 1, D.H - 1, LEG_SPLIT + 1, D.W - 1))
    D.part("body", D.rest())
    return D


TINT = {"back_leg": (60, 120, 255), "front_leg": (255, 60, 60)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def lifted(layer, lift):
    """A leg layer lifted `lift` rows by losing its top rows (the thigh turned toward us): league_braum's walk."""
    if not lift:
        return layer
    out = layer.copy()
    ys = np.nonzero(layer[..., 3].any(1))[0]
    out[:ys.min() + lift] = 0
    return np.roll(out, -lift, axis=0)


class Form:
    """The designs' layers; pose() / front() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.idle = self.placed(load("idle.png"), IDLE_STAND)

    def placed(self, d, stand):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        lay[top:top + d.shape[0], x0:x1] = d[:, x0 - left:x1 - left]
        return lay

    def pose(self, whole=(0, 0), crouch=0, back=(0, 0, 0), front=(0, 0, 0)):
        """whole: the whole figure (dx, dy); crouch: rows the upper body (with the gun: the gun is never moved apart
        from the body - its golds and steel are mixed with the hands and the trousers) sets down onto the legs;
        back / front: a leg's (dx, dy, lift)."""
        wx, wy = whole
        ux, uy = wx, wy + crouch
        L = self.L
        layers = []
        for name, (dx, dy, lift) in (("back_leg", back), ("front_leg", front)):
            layers.append((lifted(L[name], lift), dict(dx=wx + dx, dy=wy + dy)))
        layers.append((L["body"], dict(dx=ux, dy=uy)))
        can = R.compose(self.rig, layers)
        return close_cracks(can, self.D.outline)

    def posed(self, name, whole=(0, 0), lift=0):
        """A Codex pose (hd/pose_<name>.png, design_graves_poses.py) standing where the side design stands: the middle
        of its feet (feet_mid) on the side design's, its lowest row on the ground - `lift` rows above it (the hop)."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1) - lift
        left = P + int(round(feet_mid(self.D.d) - feet_mid(d)))
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        y0, y1 = max(0, top), min(lay.shape[0], top + d.shape[0])
        lay[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
        return R.compose(self.rig, [(lay, dict(dx=whole[0], dy=whole[1]))])

    def lying(self, name, dx=0):
        """A pose lying on the ground (lie): its lowest row on the ground, centred dx squares from the standing point."""
        d = load(f"pose_{name}.png")
        ys, xs = np.nonzero(d[..., 3] > 0)
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - int(round((xs.min() + xs.max() + 1) / 2)) + dx
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        lay[top:top + d.shape[0], x0:x1] = d[:, x0 - left:x1 - left]
        return R.compose(self.rig, [(lay, {})])

    def front(self, crouch=0, whole=(0, 0), flash=False):
        """The 3/4 idle design, its body (above IDLE_LEG_ROW) set down `crouch` rows onto its own legs."""
        lay = self.idle
        legs, top = lay.copy(), lay.copy()
        yy = np.mgrid[0:lay.shape[0], 0:lay.shape[1]][0]
        legs[yy < P + IDLE_LEG_ROW] = 0
        top[yy >= P + IDLE_LEG_ROW] = 0
        wx, wy = whole
        can = R.compose(self.rig, [(legs, dict(dx=wx, dy=wy)), (top, dict(dx=wx, dy=wy + crouch))])
        return R.flash(can) if flash else can


def feet_mid(d, rows=3):
    """The middle of a figure's feet: halfway between the leftmost and the rightmost square of its lowest `rows` rows."""
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    xs = np.nonzero((d[ys.max() - rows + 1:ys.max() + 1, :, 3] > 0).any(0))[0]
    return (xs.min() + xs.max() + 1) / 2


def close_cracks(can, outline, most=12):
    """Enclosed gaps of at most `most` squares a move opened (between a leg and the belt): the outline (gap-check)."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        if h.sum() <= most:
            out[h] = (*outline, 255)
    return out


def form():
    F = Form(design(), rig_pad=(40, 40, 40, 20))
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_graves.py) come from these (a frame's start in ticks = ms x 0.06)
MS = {"idle": [160] * 8, "run": [115] * 8,
      "attack": [60, 70, 80, 90, 80, 60, 60], "attack2": [60, 70, 80, 80, 100, 100, 70, 60],
      "skill": [70, 60, 90, 90, 80, 60], "skill2": [50, 90, 90, 60, 60],
      "ult": [80, 80, 70, 90, 90, 80, 60], "hit": [100, 100],
      "dead": [120, 120, 160, 200, 160, 600]}
# the walk: per frame the back leg's (dx, dy, lift), the front leg's, the body's rise (league_nautilus's 1x steps, at
# PPU 1.5 a step of 2 squares, a lift of 3)
WALK = [((0, 0, 2), (0, 0, 0), 1), ((2, 0, 3), (0, 0, 0), 1), ((2, 0, 1), (0, 0, 0), 0), ((2, 0, 0), (0, 0, 0), 0),
        ((0, 0, 0), (0, 0, 2), 1), ((0, 0, 0), (2, 0, 3), 1), ((0, 0, 0), (2, 0, 1), 0), ((0, 0, 0), (2, 0, 0), 0)]
HOP = 6                        # R's hop: rows off the ground at its top


def frames_all(F):
    p, q = F.pose, F.posed
    out = {}
    # idle (League's graves_idle1: a slow breath, the gun still at the hip): the 3/4 design's body sets down a row
    out["idle"] = [F.front(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    out["run"] = [p(whole=(0, -r), back=b, front=f) for b, f, r in WALK]
    # auto attack (League's graves_attack1, frame by frame 2026-10-20: the shot from the level gun at ~0 ms, the gun
    # kicked up about 30 degrees by ~190 ms and pumped, level again by ~1100 ms): aimed, the shot as frame 3 starts
    # (130 ms = tick 8: the flash at the muzzle; his whole figure kicked back two squares), the pump (Codex's tilt on the
    # design's legs), back to aim a square behind, aimed
    out["attack"] = [p(), p(), p(whole=(-2, 0)), q("tilt", whole=(-1, 0)), q("tilt", whole=(-1, 0)), p(whole=(-1, 0)),
                     p()]
    # the second shell (League's graves_reload_slow: the same shot, the gun held up longer while he reloads)
    out["attack2"] = [p(), p(), p(whole=(-2, 0)), q("tilt", whole=(-1, 0)), q("tilt", whole=(-1, 0)),
                      q("tilt", whole=(-1, 0)), p(whole=(-1, 0)), p()]
    # Q End of the Line (League's graves_spell1: a low step forward, the shell fired level at ~180 ms, the gun swung up
    # by the kick): the lunge, the shell as frame 3 starts (130 ms = tick 8), the kick up (tilt), aimed
    out["skill"] = [q("lunge"), q("lunge"), q("lunge", whole=(-1, 0)), q("tilt", whole=(-1, 0)), q("tilt"), p()]
    # E Quickdraw (League's graves_spell3: a low dash, the gun held level): the lunge through the dash (tick 3 on)
    out["skill2"] = [q("lunge"), q("lunge"), q("lunge"), q("lunge", whole=(0, 0)), p()]
    # R Collateral Damage (League's graves_spell4 + spell4_BACK: the gun hefted to the shoulder, the shell fired at
    # ~230 ms, the recoil throwing him back off his feet, the gun pointing up): the heft, the shot as frame 3 starts
    # (160 ms = tick 10), the hop (HOP rows up, then half), landed, aimed
    out["ult"] = [q("shoulder"), q("shoulder"), q("shoulder", whole=(-1, 0)), q("hop", lift=HOP), q("hop", lift=HOP // 2),
                  p(), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's graves_death: the gun knocked out of his hands at the shot, he staggers back, drops to his
    # knees and falls on his face): staggering (two frames, a square back), on his knees, falling, lying face down
    out["dead"] = [q("stagger"), q("stagger", whole=(-1, 0)), q("kneel"), q("kneel", whole=(1, 1)), F.lying("lie", 6),
                   F.lying("lie", 6)]
    return out


# the muzzle blasts drawn into his shot frames (the client never mirrors an effect picture, only his own frames: the
# skill's rule "Both sides"): tag -> (the picture's tag in league_graves_fx, the shot frame); the shot frame split into
# one frame per blast frame while it lasts (the gun is level only on it: the next frame tips it up or lifts him)
SHOTS = {"attack": ("a_flash", 2), "attack2": ("a_flash", 2), "skill": ("q_flash", 2), "ult": ("r_flash", 2)}
FX_SHEET = os.path.join(R.ROOT, "league", "effects", "league_graves_fx#sheet.png")


def muzzle(can):
    """The muzzle on a canvas: the right edge of its rightmost squares (the shotgun reaches furthest forward in every
    shot frame) and the middle of their rows."""
    ys, xs = np.nonzero(can[..., 3] > 0)
    x1 = xs.max()
    rows = ys[xs >= x1 - 1]
    return x1 + 1.0, (rows.min() + rows.max() + 1) / 2.0


def blast_frames(tag):
    """The blast's frames from league_graves_fx brought to PPU (nearest, as Rig.bake), with their ms; None before the
    effects are imported."""
    if not os.path.isfile(lp(FX_SHEET)):
        return None
    import tfm2_ase
    sp = tfm2_ase.load_sprite(FX_SHEET)
    out = []
    for i in sp.tag_frames(tag):
        a = np.asarray(sp.frames[i].convert("RGBA"))
        h, w = a.shape[:2]
        yy = np.minimum(((np.arange(round(h * PPU)) + 0.5) / PPU).astype(int), h - 1)
        xx = np.minimum(((np.arange(round(w * PPU)) + 0.5) / PPU).astype(int), w - 1)
        out.append((a[yy][:, xx].copy(), sp.durations[i]))
    return out


def with_blasts(F, acts):
    """{tag: [(canvas or {"body", "over"}, ms)]}: each SHOTS frame split under its blast's frames (their centre - the
    muzzle, import_graves_fx.py - on the frame's muzzle)."""
    out = dict(acts)
    for tag, (fx, k) in SHOTS.items():
        pics = blast_frames(fx)
        if not pics:
            continue
        can, ms = acts[tag][k]
        mx, my = muzzle(can)
        parts, left = [], ms
        for pic, pms in pics:
            if left <= 0:
                break
            t = min(pms, left)
            over = F.rig.canvas()
            h, w = pic.shape[:2]
            y0, x0 = int(round(my - h / 2)), int(round(mx - w / 2))
            ys, xs = np.nonzero(pic[..., 3] > 0)
            ok = (ys + y0 >= 0) & (ys + y0 < over.shape[0]) & (xs + x0 >= 0) & (xs + x0 < over.shape[1])
            over[ys[ok] + y0, xs[ok] + x0] = pic[ys[ok], xs[ok]]
            parts.append(({"body": can, "over": over}, t))
            left -= t
        out[tag] = acts[tag][:k] + parts + acts[tag][k + 1:]
    return out


def flat(c):
    """A frame as one canvas (a blast laid over its body)."""
    if not isinstance(c, dict):
        return c
    out = c["body"].copy()
    for key in ("under", "over"):
        lay = c.get(key)
        if lay is not None:
            m = lay[..., 3] > 0
            if key == "under":
                m &= out[..., 3] == 0
            out[m] = lay[m]
    return out


def frames(F, blasts=True):
    """{tag: [(canvas or {"body", "over"}, ms)]} in the sheet's order (blasts: the muzzle blasts laid on, with_blasts)."""
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return with_blasts(F, out) if blasts else out


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
        acts = frames(F, blasts=not a.audit)
        acts = {t: [(flat(c), ms) for c, ms in fr] for t, fr in acts.items()}
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


if __name__ == "__main__":
    main()
