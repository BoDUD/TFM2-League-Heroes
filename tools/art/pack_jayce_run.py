#!/usr/bin/env python3
"""Jayce's run redo pack for Codex (assets/source/jayce/RUN_PROMPT.md): both runs' 8 frames with the legs crossing.

    python tools/art/pack_jayce_run.py [--out dist/jayce_packs/jayce_run_pack]

Codex's step-2 runs (assets/source/jayce/codex_strips/jayce_run_* and jayce_c_run_*) keep both feet near the same spots
(run 1-4 the rear foot 24-29 px behind, c_run 1-4 frozen): the user, 2026-10-15: 「跑步时腿没感觉到明显换位置啊」.
Legs built from the design's parts read as deformed on every hero so far (memory run-legs-caitlyn-way), so Codex
redraws the legs only, along a line per leg - league_milio's way (tools/art/pack_milio_run.py):
  now/jayce_<tag>_<n>.png    Codex's own run frame (held by the head like the import: rig_jayce.ALIGN) with its legs
                             taken away under the belt (the navy coat tails kept)
  guide/jayce_<tag>_<n>.png  the same with the legs to draw as lines: red = the near leg (in front, full tone), blue =
                             the far leg (a shade darker), hip - knee - ankle - toe, the ground row, the standing point
  ref/                       the side designs (legs: slate trousers, cream-gold knee guards, dark brown boots),
                             league_caitlyn's run at 6x (the cross-step run the user approved), the step-2 runs
The near leg goes through 8 phases (planted ahead, under the body, the far leg swinging past it = the cross step,
pushing off behind, lifted, kicked up, swung through, reaching) and the far leg the same 4 frames on, so the legs swap
between frames 1-4 and 5-8 and cross in frames 3 and 7. Same pack grid as step 2 (pack_jayce_strips.py): 5 px a
design square, the soles on row SOLE, the standing point on column PIV.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_jayce as R  # noqa: E402
import rigkit as K  # noqa: E402

SRC = R.SRC
DOC = os.path.join(SRC, "RUN_PROMPT.md")
PX = 5
PIV_X, SOLE = R.PIV, R.SOLE
RED, BLUE = (255, 40, 40), (40, 110, 255)
COAT = [(17, 24, 45), (30, 36, 52)]   # the coat tails' navies (the trousers are the slate (65, 72, 89) / (43, 49, 70))
# the legs' bones in design squares (hd/hammer_side.png: crown row 24, the belt's lowest row 77, the knee guards' middle
# row 95, the boots' soles row 121; the trousers start under the belt)
CUT = 54                         # rows under the matched head's top (its crown): the belt's lower edge - legs below
HIP = 57                         # the hips this many rows under the crown
THIGH, SHIN = 19.0, 20.0
FOOT = (8, 3)                    # the toe from the ankle: forward, down (the boot)
ANKLE_UP = 5                     # the ankle over the ground with the boot flat
HIP_DX = -2                      # the hips' middle from the head's middle (the body leans ahead)
NEAR_HIP, FAR_HIP = -3.0, 3.0    # the near hip image left, the far one image right (3/4 side view)
# the near leg's 8 phases from its hip: the ankle's x (forward +) and its height over the ground; the far leg four on
# (league_milio's PHASES x 1.6 for the longer legs)
PHASES = [(14, 5), (6, 5), (-2, 5), (-11, 7), (-16, 13), (-10, 23), (3, 18), (13, 10)]
TAGS = ("run", "c_run")


def legless(a, crown):
    """The frame without its legs: under the belt (crown + CUT) everything goes but the coat tails (the navy pieces
    reaching up past the cut) and their outline."""
    out = a.copy()
    cut = crown + CUT
    rgb = a[..., :3].astype(int)
    coat = np.zeros(a.shape[:2], bool)
    for c in COAT:
        coat |= np.all(rgb == np.array(c), axis=-1) & (a[..., 3] > 0)
    lbl, n = ndimage.label(coat, structure=np.ones((3, 3)))
    keep = np.zeros_like(coat)
    for k in range(1, n + 1):
        piece = lbl == k
        ys = np.nonzero(piece.any(1))[0]
        if ys.min() < cut and ys.max() > cut + 2:
            keep |= piece
    dark = (a[..., 3] > 0) & (rgb.sum(-1) < 90)
    keep |= dark & ndimage.binary_dilation(keep, structure=np.ones((3, 3)))
    below = np.zeros(a.shape[:2], bool)
    below[cut:] = True
    out[below & ~keep] = 0
    return out


def big(a, bg=None):
    im = Image.fromarray(a).resize((a.shape[1] * PX, a.shape[0] * PX), Image.NEAREST)
    canvas = Image.new("RGBA", (1536, 1024), bg or (0, 0, 0, 0))
    canvas.alpha_composite(im, (0, 0))
    return canvas


def leg_points(hip, k):
    hx, hy = hip
    ax, ah = PHASES[k]
    ankle = (hx + ax, SOLE + 1 - ah)
    knee, ankle = K.elbow((hx, hy), ankle, THIGH, SHIN, bend=1)
    if knee[0] < min(hx, ankle[0]) - 0.5:             # knees point forward (image right)
        knee, ankle = K.elbow((hx, hy), ankle, THIGH, SHIN, bend=-1)
    toe = (ankle[0] + FOOT[0], ankle[1] + FOOT[1])
    if ah > ANKLE_UP:                                 # a lifted foot hangs: the toe down and back a little
        toe = (ankle[0] + FOOT[0] * 0.7, ankle[1] + FOOT[1] * 1.6)
    return [(hx, hy), knee, ankle, toe]


def draw_guide(img, legs):
    d = ImageDraw.Draw(img)
    gy = (SOLE + 1) * PX
    d.line([(0, gy), (1536, gy)], fill=RED, width=2)
    px = (PIV_X + 0.5) * PX
    d.line([(px - 12, gy - 12), (px + 12, gy + 12)], fill=BLUE, width=2)
    d.line([(px - 12, gy + 12), (px + 12, gy - 12)], fill=BLUE, width=2)
    for pts, col in legs:
        P = [((x + 0.5) * PX, (y + 0.5) * PX) for x, y in pts]
        d.line(P, fill=col, width=5, joint="curve")
        for x, y in P[:3]:
            d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=col, width=3)
        x, y = P[-1]
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "jayce_packs", "jayce_run_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("now", "guide", "ref", "step2"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    plan = {}
    for tag in TAGS:
        frames, heads, _ = R.matched(tag, 8)           # aligned by the head, as the import does
        hw = R.HEAD.shape[1]
        for k, (f, (s, hy, hx)) in enumerate(zip(frames, heads)):
            crown = int(round(hy))
            mid = hx + hw * s / 2.0
            up = legless(f, crown)
            name = f"jayce_{tag}_{k + 1}.png"
            big(up).save(os.path.join(out, "now", name))
            hip = (mid + HIP_DX, crown + HIP)
            legs = [(leg_points((hip[0] + FAR_HIP, hip[1]), (k + 4) % 8), BLUE),
                    (leg_points((hip[0] + NEAR_HIP, hip[1]), k), RED)]
            g = big(up, (255, 255, 255, 255))
            draw_guide(g, legs).convert("RGB").save(os.path.join(out, "guide", name))
            big(f, (255, 255, 255, 255)).convert("RGB").save(os.path.join(out, "step2", name))
            plan[name] = {"crown": crown, "hip": [round(hip[0], 1), hip[1]],
                          "legs": {"far": [[round(x, 1), round(y, 1)] for x, y in legs[0][0]],
                                   "near": [[round(x, 1), round(y, 1)] for x, y in legs[1][0]]}}
    for n in ("hammer_side", "cannon_side"):
        side = np.asarray(Image.open(os.path.join(SRC, "hd", f"{n}.png")).convert("RGBA"))
        Image.fromarray(side).resize((side.shape[1] * PX, side.shape[0] * PX), Image.NEAREST).save(
            os.path.join(out, "ref", f"jayce_{n}_design.png"))
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
    with open(os.path.join(out, "legs.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(plan, fh, indent=1)
    shutil.copy(DOC, os.path.join(out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{zp}: now/ guide/ step2/ x16, ref/ 3")


if __name__ == "__main__":
    main()
