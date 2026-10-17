#!/usr/bin/env python3
"""Milio's run redo pack for Codex (assets/source/milio/RUN_PROMPT.md): the 8 run frames with the legs crossing.

    python tools/art/pack_milio_run.py [--out dist/milio_packs/milio_run_pack]

Codex's step-2 run (assets/source/milio/codex_strips/milio_run_*) kept the light near leg forward and the dark far one
back in all 8 frames; played twice with the legs' shades swapped (league_kindred's way) the stride never changed and
the legs never passed each other (the user, 2026-10-15: 「走路没后交叉步 步伐没有变化」). Legs built from the design's
own parts read as deformed on every PPU hero so far (league_galio's four tries; memory run-legs-caitlyn-way), so Codex
redraws the legs only, following a line per leg - league_galio's round 2 (tools/art/pack_galio_run.py):
  now/milio_run_<n>.png    Codex's own run frame with its legs taken away (head, arms, tunic, kilt: keep them),
                           placed at the frame's bob
  guide/milio_run_<n>.png  the same with the legs to draw as lines: red = the light near leg, blue = the darker far leg
                           (hip - knee - ankle - toe, a dot on the toe), the ground row, the standing point
  ref/                     the side design, Codex's own near leg (a whole leg to copy: thickness, wrap, sandal),
                           league_caitlyn's run at 6x (the cross-step run the user approved), the step-2 run (what to fix)
The near leg goes through 8 phases - planted ahead (1), under the body (2-3: the far leg swings past it, knee high:
the cross step), pushing off behind (4), lifted (5), kicked up (6), swung through under the body (7), reaching (8) -
and the far leg the same 4 frames on, so the legs cross in frames 3 and 7. Same pack grid as step 2
(tools/art/pack_milio_strips.py): 6 px a design square, the soles on row 160, the standing point on column 120.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_milio_strips as I  # noqa: E402
import rigkit as K  # noqa: E402

SRC = I.SRC
DOC = os.path.join(SRC, "RUN_PROMPT.md")
PX = 6                            # the step-2 pack's grid: 6 px a square, 256 x 170 squares
PIV_X, SOLE = 120, 160            # its standing column and ground row
RED, BLUE = (255, 40, 40), (40, 110, 255)
KILT = [2, 7, 9, 12, 15, 16, 17, 22, 24, 28, 13, 19]   # the kilt's and the sash's colours (the wraps have some too:
                                                     # only the piece joined to the sash counts)
# the legs' bones in design squares (hd/side.png: the hip under the kilt about row 64, the knee at the kilt's hem,
# the ankle on the sandal's top, row 86, the soles row 95)
HIP_UP = 31                       # the hips this many rows over the ground row (inside the kilt, its hem about 23 up)
THIGH, SHIN = 12.0, 12.0
FOOT = (7, 8)                     # the toe from the ankle: forward, down
NEAR_HIP, FAR_HIP = -2.0, 2.0     # the hips' columns from the kilt's middle (the near one image left, 3/4 side view)
# the near leg's 8 phases from its hip: the ankle's x (forward +) and its height over the ground (the sandal flat on the
# ground at 9); the far leg four phases on
PHASES = [(9, 9), (4, 9), (-1, 9), (-7, 10), (-10, 14), (-6, 20), (2, 17), (8, 12)]
BOB = [1, 2, 1, 0, -1, 0, 1, 0]   # the body this many rows down (stance low, flight high)
SOURCE = [8, 5, 2, 4, 8, 5, 2, 4]  # Codex's run frame whose upper body each frame uses (its own order of bob)


def can_rgba(name):
    return np.asarray(Image.open(os.path.join(I.OUT, name)).convert("RGBA")).copy()


def legless(a):
    """Codex's run frame without its legs: under the kilt's hem (the lowest row of the kilt-and-sash piece in each
    column) everything goes; in the columns the kilt does not reach, everything 8 rows under the sash's top (the back
    leg kicked out behind; the back fist ends above it). Outline squares left hanging go too."""
    idx = I.to_idx(a)
    op = idx >= 0
    kilt = np.isin(idx, KILT)
    lbl, n = ndimage.label(kilt, structure=np.ones((3, 3)))
    sizes = ndimage.sum(kilt, lbl, range(1, n + 1))
    body = lbl == (int(np.argmax(sizes)) + 1)         # the kilt and the sash: the biggest piece of those colours
    ys, xs = np.nonzero(body)
    top = ys.min()
    cut = np.zeros_like(op)
    for c in range(a.shape[1]):
        col = np.nonzero(body[:, c])[0]
        if len(col):
            cut[col.max() + 2:, c] = True
        else:
            cut[top + 8:, c] = True
    out = a.copy()
    out[cut] = 0
    # hanging outline: dark squares with no lit square within one
    idx2 = I.to_idx(out)
    dark = np.isin(idx2, [I.OUTLINE, 1])
    lit = (idx2 >= 0) & ~dark
    out[dark & ~ndimage.binary_dilation(lit, structure=np.ones((3, 3)))] = 0
    hem_rows = np.nonzero(body.any(1))[0]
    low = body[hem_rows.max() - 6:hem_rows.max() + 1]
    hx = np.nonzero(low.any(0))[0]
    return out, (hx.min() + hx.max() + 1) / 2.0


def on_pack(a, dy):
    """A frame canvas (I.COLS x I.ROWS, standing column I.PIV, ground row I.SOLE) on the pack's canvas, dy rows down."""
    can = np.zeros((170, 256, 4), np.uint8)
    ox, oy = PIV_X - I.PIV, SOLE - I.SOLE + dy
    ys, xs = np.nonzero(a[..., 3] > 0)
    r, c = ys + oy, xs + ox
    ok = (r >= 0) & (r < 170) & (c >= 0) & (c < 256)
    can[r[ok], c[ok]] = a[ys[ok], xs[ok]]
    return can


def big(a, bg=None):
    im = Image.fromarray(a).resize((a.shape[1] * PX, a.shape[0] * PX), Image.NEAREST)
    canvas = Image.new("RGBA", (1536, 1024), bg or (0, 0, 0, 0))
    canvas.alpha_composite(im, (0, 0))
    return canvas


def leg_points(hip_col, k, dy, mid):
    """hip - knee - ankle - toe in pack squares for phase k of a leg whose hip is hip_col squares from the kilt's middle
    (`mid`, a frame-canvas column)."""
    hx, hy = mid - I.PIV + PIV_X + hip_col, SOLE + 1 - HIP_UP + dy
    ax, ah = PHASES[k]
    ankle = (hx + ax, SOLE + 1 - ah)
    knee, ankle = K.elbow((hx, hy), ankle, THIGH, SHIN, bend=1)
    if knee[0] < min(hx, ankle[0]) - 0.5:             # knees point forward (image right)
        knee, ankle = K.elbow((hx, hy), ankle, THIGH, SHIN, bend=-1)
    toe = (ankle[0] + FOOT[0], ankle[1] + FOOT[1])
    if ah > 9:                                        # a lifted foot hangs: the toe down and back a little
        toe = (ankle[0] + FOOT[0] * 0.7, ankle[1] + FOOT[1] * 0.9)
    return [(hx, hy), knee, ankle, toe]


def draw_guide(img, legs, hem):
    d = ImageDraw.Draw(img)
    gy = (SOLE + 1) * PX
    d.line([(0, gy), (1536, gy)], fill=RED, width=2)
    px = (PIV_X + 0.5) * PX
    d.line([(px - 12, gy - 12), (px + 12, gy + 12)], fill=BLUE, width=2)
    d.line([(px - 12, gy + 12), (px + 12, gy - 12)], fill=BLUE, width=2)
    for pts, col in legs:
        P = [(x * PX, y * PX) for x, y in pts]
        d.line(P, fill=col, width=5, joint="curve")
        for x, y in P[:3]:
            d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=col, width=3)
        x, y = P[-1]
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "milio_packs", "milio_run_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("now", "guide", "ref", "step2"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for k in range(8):
        src = can_rgba(f"codex_run_{SOURCE[k]}.png")
        up, mid = legless(src)
        packed = on_pack(up, BOB[k])
        big(packed).save(os.path.join(out, "now", f"milio_run_{k + 1}.png"))
        legs = [(leg_points(FAR_HIP, (k + 4) % 8, BOB[k], mid), BLUE), (leg_points(NEAR_HIP, k, BOB[k], mid), RED)]
        g = big(packed, (255, 255, 255, 255))
        draw_guide(g, legs, mid).convert("RGB").save(os.path.join(out, "guide", f"milio_run_{k + 1}.png"))
        shutil.copy(os.path.join(I.OUT, f"run_{k + 1}.png"), os.path.join(out, "step2", f"milio_run_{k + 1}_step2.png"))
    # refs: the side design; Codex's own near leg (run_2's planted front leg) boxed on its frame; Caitlyn's run
    side = np.asarray(Image.open(os.path.join(SRC, "hd", "side.png")).convert("RGBA"))
    Image.fromarray(side).resize((side.shape[1] * PX, side.shape[0] * PX), Image.NEAREST).save(
        os.path.join(out, "ref", "milio_side_design.png"))
    leg = on_pack(can_rgba("codex_run_2.png"), 0)
    ref = big(leg, (255, 255, 255, 255))
    ImageDraw.Draw(ref).rectangle([(PIV_X + 8) * PX, (SOLE - 30) * PX, (PIV_X + 45) * PX, (SOLE + 2) * PX], outline=RED,
                                  width=4)
    ref.convert("RGB").save(os.path.join(out, "ref", "milio_leg_from_codex_run.png"))
    sys.path.insert(0, HERE)
    from preview_garen import frames_of, load
    sp = load(os.path.join(ROOT, "league", "champions", "league_caitlyn"))
    fs = [f for f, _ in frames_of(sp, "run")]
    bb = None
    for f in fs:
        b = f.getbbox()
        bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    fs = [f.crop(bb) for f in fs]
    w, h = fs[0].size
    strip = Image.new("RGBA", (len(fs) * (w + 2) * 6, h * 6), (255, 255, 255, 255))
    for i, f in enumerate(fs):
        strip.alpha_composite(f.resize((w * 6, h * 6), Image.NEAREST), (i * (w + 2) * 6, 0))
    strip.save(os.path.join(out, "ref", "caitlyn_run_reference.png"))
    shutil.copy(DOC, os.path.join(out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{zp}: now/ guide/ x8, ref/ 3, step2/ x8")


if __name__ == "__main__":
    main()
