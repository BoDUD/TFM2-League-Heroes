#!/usr/bin/env python3
"""league_velkoz's action frames, posed on the approved 3/4 design after League's own clips, frame by frame (the user,
2026-10-20: 3/4 only, A-2 at 36 game px / PPU 1.5; actions rigged by me after League's clips, perfect before review).

    python tools/art/rig_velkoz.py --parts DIR       # the design with its parts tinted (12x)
    python tools/art/rig_velkoz.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_velkoz.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_velkoz.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/review_velkoz_actions.py --out DIR   # League left / ours right, one GIF

The design (tools/art/design_velkoz_model.py: Codex's step-1 take A-2, drawn at the count - 54 rows crest top to the
lowest tentacle, 76 wide; Codex's own eyes): League's idle seen 3/4 from the front-right - the khaki-gold carapace with
the big magenta eye turned to the image right, one tentacle curling up behind on the upper left (`ul`), one coiled in a
loop under the near side (`ll`), one curling down and out on the far side (`lr`).
He floats (no legs): the design stands FLOAT rows above the ground line (League's Vel'Koz hovers; league_malzahar's
float), so every pose moves him whole without touching the ground.
Lossless (memory rig-deformation-checks): parts cut square by square from the design and moved by whole squares, the
far tentacle also turned by quarter turns about its root; the carapace and the eye are never cut apart, sheared or
turned. Tried and dropped (8x self-review, 2026-10-20): opening the shell for Q / R by lifting the crest and lowering
the jaw - any gap between the plates, filled dark or with the flesh's crimson, read as a stripe cut across the head;
sliding the far tentacle right or down - it tore off its root; turning the upper tentacle up - it hid behind the crest.
What stays: the eye lit for the shots (`shot`), the far tentacle thrown forward (one quarter turn) or raised behind
(two), the upper one lifted whole, the near loop nudged over its stalk, the whole figure bobbing, recoiling and lunging;
the death closes the shell over the eye (the crest set down a row and the jaw up a row onto it: plates overlapping, no
gap) while the eye goes dark.
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
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "velkoz"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "velkoz", "hd")
FLOAT = 4                      # rows between the lowest tentacle and the ground line (he hovers)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU
        self.ground += FLOAT


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 38                     # the carapace's middle column: the standing point
UL = (0, 20, 0, 21)            # rows, columns (inclusive): the upper-left tentacle, left of the carapace's left edge
UL_ROOT = (8, 19, 22, 30)      # its root behind the carapace (the dark squares there go with it)
LL = [(34, 53, 0, 23), (45, 53, 24, 37)]          # the near loop and its bottom curve (the armoured stalk stays)
LR = [(23, 53, 58, 75), (38, 53, 53, 57)]         # the far tentacle, right of the carapace's spikes
CREST = (0, 19, 22, 60)        # the crest block over the eye (the spike crown, the three small eyes)
JAW = (33, 44, 38, 57)         # the jaw plates under the big eye
EYE = (19, 33, 40, 56)         # the big eye with its flesh rim (brightened on a release)
EYES = (8, 34, 30, 58)         # every eye, the three small ones too (going dark in the death)
RIMS = (8, 36, 30, 62)         # the red flesh round the eyes (glowing as Q and R charge)


# the seams the shell opens along (column, first row below the seam): over the flesh rim and the big eye; under it
CREST_SEAM = [(21, 17), (28, 17), (34, 18), (40, 19), (46, 20), (52, 20), (58, 19), (63, 18)]
JAW_SEAM = [(38, 33), (44, 34), (50, 33), (56, 31), (58, 30)]


def under_seam(D, seam, above):
    """The squares above (or from) a polyline seam through the given (column, row) points, within its columns."""
    xs = np.arange(D.W)
    rows = np.interp(xs, [p[0] for p in seam], [p[1] for p in seam])
    yy = np.arange(D.H)[:, None]
    m = yy < rows[None, :] if above else yy >= rows[None, :]
    m &= (xs[None, :] >= seam[0][0]) & (xs[None, :] <= seam[-1][0])
    return m & (D.d[..., 3] > 0)


def gold(d):
    """The carapace's squares: khaki, gold and its olive shading (red and green at least blue: the tentacles' teal,
    navy and purple are bluer, their magenta tips have far less green), not the near-black outline."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (r >= b) & (g >= b - 5) & (r + g + b > 90)


def ink(d):
    """Near-black outline squares."""
    return (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 40)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    warm = gold(d)
    # the carapace keeps its own outline: outline squares touching carapace squares stay with it when a tentacle moves
    shell = warm | (ink(d) & ndimage.binary_dilation(warm, structure=np.ones((3, 3), bool)))
    D.part("ul", (D.box(*UL) | D.box(*UL_ROOT)) & ~shell)
    D.part("ll", (D.box(*LL[0]) | D.box(*LL[1])) & ~shell)
    D.part("lr", (D.box(*LR[0]) | D.box(*LR[1])) & ~shell)
    D.part("crest", under_seam(D, CREST_SEAM, above=True) & ~D.box(*UL) & ~D.parts["lr"])
    D.part("jaw", under_seam(D, JAW_SEAM, above=False) & D.box(*JAW) & ~D.parts["lr"] & ~D.parts["ll"])
    D.part("body", D.rest())
    return D


TINT = {"ul": (60, 200, 255), "ll": (0, 255, 120), "lr": (255, 120, 0), "crest": (255, 220, 0), "jaw": (255, 0, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# ------------------------------------------------------------------------------------------------- lossless moves
def magenta(a, light=False):
    """The eyes' magenta squares (and with `light` their white-pink highlights too)."""
    rgb = a[..., :3].astype(int)
    m = (a[..., 3] > 0) & (rgb[..., 0] > 150) & (rgb[..., 2] > 150) & (rgb[..., 1] < 170)
    if light:
        m |= (a[..., 3] > 0) & (rgb[..., 0] > 200) & (rgb[..., 2] > 200)
    return m


def lit(layer, box, k, to, light=False):
    """The eyes' magenta squares inside `box` (design rows / columns; with `light` their highlights too) blended towards
    `to` by k (0..1)."""
    out = layer.copy()
    m = np.zeros(out.shape[:2], bool)
    y0, y1, x0, x1 = box
    m[P + y0:P + y1 + 1, P + x0:P + x1 + 1] = True
    m &= magenta(out, light)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + np.array(to) * k).astype(np.uint8)
    return out


def flared(layer, box, k):
    """The red flesh rims round the eye inside `box` lit towards a hot pink by k (0..1): the shell's flesh glowing as Q
    and R charge (League's Spell1 / Spell4 spread the red petals round the eye; a colour change only - every square
    stays where it is)."""
    out = layer.copy()
    m = np.zeros(out.shape[:2], bool)
    y0, y1, x0, x1 = box
    m[P + y0:P + y1 + 1, P + x0:P + x1 + 1] = True
    rgb = out[..., :3].astype(int)
    m &= (out[..., 3] > 0) & (rgb[..., 0] > 110) & (rgb[..., 1] < 120) & (rgb[..., 2] < 130) & (rgb[..., 0] > rgb[..., 2] + 40)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + np.array([255, 40, 100]) * k).astype(np.uint8)
    return out


# where each tentacle leaves the carapace (square edges): what its quarter turns are about
ROOTS = {"ul": (27.0, 17.0), "lr": (60.0, 25.0), "ll": (25.0, 40.0)}


def turned(layer, k, about):
    """A padded layer turned k quarter turns counter-clockwise on screen about `about` (design square edges): every
    square kept, none stretched (rig_warwick.turned)."""
    out = np.zeros_like(layer)
    ys, xs = np.nonzero(layer[..., 3] > 0)
    ax, ay = about[0] + P, about[1] + P
    ox, oy = xs + 0.5 - ax, ys + 0.5 - ay
    for _ in range(k % 4):
        ox, oy = oy, -ox
    tx = np.floor(ax + ox).astype(int)
    ty = np.floor(ay + oy).astype(int)
    ok = (tx >= 0) & (tx < out.shape[1]) & (ty >= 0) & (ty < out.shape[0])
    out[ty[ok], tx[ok]] = layer[ys[ok], xs[ok]]
    return out


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad=(40, 40, 40, 16)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), ul=(0, 0), ll=(0, 0), lr=(0, 0), lid=0, shot=0.0, dark=0.0, flare=0.0):
        """whole: the figure (dx, dy); ul / ll: a tentacle's (dx, dy) on the body; lr: the far tentacle's (dx, dy) or
        (dx, dy, quarter turns counter-clockwise about its root: 1 thrown forward, drawn in front of the carapace's far
        edge; 2 raised behind); lid: rows the crest sets down and the jaw comes up over the eye (the shell closing, the
        death); shot: the eye lit (0..1); dark: the eye dimmed (0..1, the death); flare: the flesh rims round the eye lit
        (0..1, Q and R charging)."""
        wx, wy = whole
        L = self.L
        k = lr[2] % 4 if len(lr) > 2 else 0
        far = turned(L["lr"], k, ROOTS["lr"]) if k else L["lr"]
        body = L["body"]
        if shot:
            body = lit(body, EYE, shot * 0.6, (255, 150, 255))
        crest, jaw = L["crest"], L["jaw"]
        if flare:
            body, crest, jaw = (flared(a, RIMS, flare) for a in (body, crest, jaw))
        if dark:
            body, crest, jaw = (lit(a, EYES, dark, (40, 10, 50), light=True) for a in (body, crest, jaw))
        layers = [(L["ul"], dict(dx=wx + ul[0], dy=wy + ul[1]))]
        if k != 1:
            layers.append((far, dict(dx=wx + lr[0], dy=wy + lr[1])))
        layers += [(body, dict(dx=wx, dy=wy)),
                   (jaw, dict(dx=wx, dy=wy - lid)),
                   (crest, dict(dx=wx, dy=wy + lid)),
                   (L["ll"], dict(dx=wx + ll[0], dy=wy + ll[1]))]
        if k == 1:
            layers.append((far, dict(dx=wx + lr[0], dy=wy + lr[1])))
        can = R.compose(self.rig, layers)
        can[self.rig.GY:] = 0
        return can


def form():
    F = Form(design())
    F.rig.idle_canvas = F.pose()
    # gap-check: enclosed gaps a move opens that the standing frame does not have (a tentacle a square off its root)
    # are closed with the outline by Rig.finish - small ones only (the near loop's own hole is in the standing frame)
    F.rig.fill_rows = (0, F.D.H + FLOAT)
    F.rig.CRACK = 12
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_velkoz.py) come from these (a frame's start in ticks = ms x 0.06)
MS = {"idle": [150] * 8, "run": [95] * 8,
      "attack": [80, 80, 70, 90, 80, 50],
      "skill": [80, 80, 90, 90, 90, 70],
      "skill2": [90, 90, 80, 120, 120],
      "ult": [90, 90, 90],
      "ult_loop": [120, 120, 120, 120],
      "hit": [100, 100],
      "dead": [120, 120, 140, 160, 200, 600]}


def frames_all(F):
    """Moves kept where a tentacle stays on its root (checked at 8x): the far one (lr) slides only left / up (behind the
    carapace) unless turned (once: thrown forward; twice: raised behind), the upper one (ul) lifted or nudged whole,
    the near loop (ll) only right / up (over its armoured stalk)."""
    p = F.pose
    out = {}
    # idle (League's Velkoz_Idle1v2: he hovers, rising and sinking slowly, the tentacles curling a beat behind): the
    # figure a square up and back down, the tentacles swaying a square in turn
    bob = [0, 0, -1, -1, -1, -1, 0, 0]
    ul = [(0, 0), (1, 0), (1, -1), (1, -1), (0, -1), (0, 0), (-1, 0), (0, 0)]
    ll = [(0, 0), (0, 0), (1, 0), (1, -1), (1, -1), (0, -1), (0, 0), (0, 0)]
    lr = [(0, 0), (-1, 0), (-1, -1), (-1, -1), (0, -1), (0, -1), (0, 0), (0, 0)]
    out["idle"] = [p(whole=(0, b), ul=u, ll=l, lr=q) for b, u, l, q in zip(bob, ul, ll, lr)]
    # run (League's Velkoz_run: he glides, the tentacles trailing behind and rippling): the figure bobbing two squares
    # (twice a cycle, the idle's one square once), the far tentacle trailing back a square or two, the upper one and the
    # loop rippling
    rise = [0, -1, -2, -1, 0, -1, -2, -1]
    ul = [(0, 0), (-1, 0), (-1, 1), (0, 1), (0, 0), (-1, 0), (-1, -1), (0, -1)]
    ll = [(0, 0), (0, -1), (1, -1), (1, 0), (0, 0), (0, -1), (1, -1), (1, 0)]
    lr = [(-1, 0), (-2, 0), (-2, -1), (-1, -1), (-1, 0), (-2, 0), (-2, -1), (-1, -1)]
    out["run"] = [p(whole=(0, r), ul=u, ll=l, lr=q) for r, u, l, q in zip(rise, ul, ll, lr)]
    # auto attack (League's Velkoz_Attack1: drawn back with a tentacle cocked, the tentacle thrown forward, the bolt
    # from the eye): drawn back, the far tentacle raised behind; thrown forward; the eye fires (frame 3, tick 10); held;
    # the tentacle down again; back
    out["attack"] = [p(whole=(-1, 0), ul=(1, -1), lr=(0, 0, 2)),
                     p(whole=(1, 0), ul=(1, 0), lr=(0, 0, 1)),
                     p(whole=(2, 0), ul=(1, 0), lr=(0, 0, 1), shot=0.6),
                     p(whole=(2, 0), lr=(0, 0, 1), shot=0.3),
                     p(whole=(1, 0)),
                     p()]
    # Q Plasma Fission (League's Velkoz_Spell1: rearing back with the tentacles flared, the eye charging, then the bolt):
    # rearing back with the tentacles up, the eye charging, the shot (frame 3, tick 10) with the figure thrown forward,
    # the glow fading, back
    out["skill"] = [p(whole=(-1, -1), ul=(0, -2), lr=(0, 0, 2), shot=0.15, flare=0.25),
                    p(whole=(-2, -1), ul=(0, -3), lr=(0, 0, 2), shot=0.4, flare=0.5),
                    p(whole=(1, 0), ul=(1, -1), lr=(-1, -1), shot=1.0, flare=0.6),
                    p(whole=(1, 0), ul=(1, -1), lr=(-1, -1), shot=0.6, flare=0.35),
                    p(shot=0.2, flare=0.1),
                    p()]
    # E Tectonic Disruption (League's Velkoz_Spell3: rearing up with the tentacles raised, then slamming down): rising
    # with the tentacles raised, higher, the slam down and forward (frame 3, tick 11), held low, back
    out["skill2"] = [p(whole=(0, -2), ul=(0, -2), lr=(0, 0, 2), ll=(0, -1)),
                     p(whole=(-1, -3), ul=(0, -3), lr=(0, 0, 2), ll=(1, -1)),
                     p(whole=(2, 1), ul=(1, 1), ll=(1, 0)),
                     p(whole=(2, 1), ul=(1, 1), ll=(1, 0)),
                     p(whole=(1, 0))]
    # R Life Form Disintegration Ray (League's Velkoz_Spell4_in + Channel: the tentacles lifted behind him, the eye
    # charging, the beam held): ult = the wind-up (16 ticks), ult_loop = the channel, the eye pulsing, the figure bobbing
    out["ult"] = [p(ul=(0, -1), lr=(-1, -1), shot=0.3, flare=0.25),
                  p(whole=(0, -1), ul=(0, -2), lr=(0, 0, 2), shot=0.55, flare=0.45),
                  p(whole=(0, -1), ul=(0, -3), lr=(0, 0, 2), shot=0.85, flare=0.65)]
    out["ult_loop"] = [p(whole=(0, b), ul=u, lr=(0, 0, 2), ll=l, shot=s, flare=f)
                       for b, u, l, s, f in ((-1, (0, -3), (0, 0), 0.85, 0.65), (-2, (1, -3), (1, -1), 0.55, 0.45),
                                             (-2, (1, -3), (1, -1), 0.85, 0.65), (-1, (0, -3), (0, 0), 0.55, 0.45))]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Velkoz_Death: he slumps, sinks to the ground and lies there, the eye going out): slumping,
    # sinking with the upper tentacle falling, down on the ground, the shell closing over the eye as it goes dark
    down = FLOAT
    out["dead"] = [p(whole=(0, 1)),
                   p(whole=(-1, 2), ul=(1, 1), dark=0.15),
                   p(whole=(-1, down), ul=(1, 2), lr=(-1, 0), lid=1, dark=0.35),
                   p(whole=(-1, down), ul=(1, 2), lr=(-1, 0), lid=1, dark=0.55),
                   p(whole=(-1, down), ul=(1, 2), lr=(-1, 0), lid=2, dark=0.7),
                   p(whole=(-1, down), ul=(1, 2), lr=(-1, 0), lid=2, dark=0.8)]
    return out


def frames(F):
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = [(c, m) for c, m in zip(cans, ms)]
    return out


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
        print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)
        return
    F = form()
    acts = frames(F)
    if a.audit:
        import rig_wukong as RW
        RW.HERO = HERO
        RW.audit(F, acts, a.audit)
    elif a.review:
        F.rig.review(acts, a.review)
    else:
        F.rig.export(acts)


if __name__ == "__main__":
    main()
