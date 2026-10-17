#!/usr/bin/env python3
"""Shen's run from League's own joints: the design's body (rows <= 84, its tail hem and apron) over legs drawn from
League's run joints (assets/source/shen/run_joints.json: tools/lol/pose_joints.py poses.json --tag run, 8 frames at
100 ms) in the design's own materials - the hakama bulb as a
capsule from the hip to the knee (purple, dark edges, silver cuff), the boot shaft as a band from the knee to the
ankle (brown), the design's own foot pasted at the ankle (the far foot for the far leg, the near foot mirrored for the
near leg; a quarter-turned foot when it points down in a heel kick). fix_shen_strips.py takes frames() for its run tag; run alone it writes
run_<k>.png (128 x 128) and a zoom sheet to --out for a look.

    python tools/art/run_shen_legs.py [--sx 0.9] [--lift 0.55] [--out DIR]

Codex's two skin-swap runs (assets/source/shen/codex_run_swap) came before this: the first squeezed both hakama legs
into one cone in the passing frames, its redo ballooned them into a squat (「腿变形了啊大哥」「这是什么？？？？你觉得能用吗」);
the user then picked legs drawn from the joints, as Talon's were.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

JOINTS = os.path.join(ROOT, "assets", "source", "shen", "run_joints.json")
SOLES = 99
C = {k: v for k, v in {
    "K": (11, 1, 15), "a": (17, 2, 24), "g": (35, 21, 72), "q": (89, 60, 156), "p": (88, 59, 149), "i": (32, 32, 98),
    "z": (195, 195, 197), "w": (163, 165, 171), "v": (138, 141, 152), "t": (118, 122, 139),
    "k": (87, 51, 39), "f": (61, 36, 30), "e": (52, 30, 26)}.items()}
HIP_ROW = 83            # the leg's top, under the sash (rows <= 84 are the body's)
KNEE_W = 3.0            # half-width of the bulb at its cuff (the design's cuff: 6 wide)
HIP_W = 2.5             # at the hip (the design's bulb starts 5 wide under the sash)
BULGE = 1.75            # the balloon in the middle: 8-9 wide like the design's bulb (its outline outside)
KNEE_ROW = SOLES - 6.5  # the planted leg's cuff: the design's cuff row 92, boot shaft 93-96, foot 97-99
SHIN_W = 2.0            # half-width of the boot shaft (the design's: 4-5 wide)
HIP_SPREAD = 1.6        # League's hips 3.7 apart -> 6: both bulbs show, the near one in front (a 3/4 view)
LEAGUE_HIP_X = 4.0      # League's pelvis middle, x from the pivot
MID = 64                # the design's body middle column (sash cols 54-75)
TAIL_DX = 4             # the tail hem moved in behind the far leg (it hung left of the idle's wide near leg)


def design_parts(des):
    """The body (rows <= 84 and the near hand's bottom), the tail hem (behind the near leg), the apron (in front)."""
    body = des.copy()
    body[85:] = 0
    body[85:87, 78:] = des[85:87, 78:]
    tail = np.zeros_like(des)
    for y in range(85, 95):
        c1 = 53 if y >= 91 else 52
        tail[y, 46:c1 + 1] = des[y, 46:c1 + 1]
    apron = np.zeros_like(des)
    for y in range(85, 94):
        c1 = 65 if y >= 91 else 67
        apron[y, 62:c1 + 1] = des[y, 62:c1 + 1]
    near_foot = des[97:100, 51:58].copy()[:, ::-1]          # the near foot, mirrored: its toe forward
    far_foot = des[97:100, 67:78].copy()
    return body, tail, apron, near_foot, far_foot


def seg_dist(p0, p1, h=128, w=128):
    """Distance of every pixel centre to the segment p0-p1 and the position t along it (0 at p0)."""
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs + 0.5, ys + 0.5
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L2 = max(dx * dx + dy * dy, 1e-6)
    t = np.clip(((px - x0) * dx + (py - y0) * dy) / L2, 0, 1)
    cx, cy = x0 + t * dx, y0 + t * dy
    return np.hypot(px - cx, py - cy), t


def capsule(p0, p1, w0, w1, flat_end=False, flat_start=False, bulge=0.0):
    """Pixels within the width of the segment p0-p1: w0 at p0 to w1 at p1, plus `bulge` in the middle (a hakama leg
    balloons between the hip and its cuff)."""
    d, t = seg_dist(p0, p1)
    m = d <= w0 + (w1 - w0) * t + bulge * np.sin(np.pi * t)
    (x0, y0), (x1, y1) = p0, p1
    ys, xs = np.mgrid[0:128, 0:128]
    if flat_end:                                    # no round cap past p1
        m &= ((xs + 0.5 - x1) * (x1 - x0) + (ys + 0.5 - y1) * (y1 - y0)) <= 0
    if flat_start:                                  # none before p0
        m &= ((xs + 0.5 - x0) * (x1 - x0) + (ys + 0.5 - y0) * (y1 - y0)) >= 0
    return m


def paint(can, mask, col):
    can[mask] = C[col] + (255,)


def draw_leg(can, hip, knee, ankle, toe, foot, foot_down):
    """One leg into can (over what is there): outline, shaft, bulb with its cuff, foot."""
    bulb = capsule(hip, knee, HIP_W, KNEE_W, flat_end=True, bulge=BULGE)
    shaft = capsule(knee, ankle, SHIN_W, SHIN_W, flat_start=True)
    leg = bulb | shaft
    out = ndimage.binary_dilation(leg, np.ones((3, 3))) & ~leg
    paint(can, out, "K")
    # the boot shaft: brown, darker at its edges
    ds, _ = seg_dist(knee, ankle)
    paint(can, shaft, "k")
    paint(can, shaft & (ds > SHIN_W - 1.0), "f")
    # the bulb: purple, its two edge columns dark, a highlight column on the front side
    paint(can, bulb, "q")
    edge = bulb & ~ndimage.binary_erosion(bulb, np.ones((1, 3)))
    paint(can, edge, "g")
    d, t = seg_dist(hip, knee)
    length = max(np.hypot(knee[0] - hip[0], knee[1] - hip[1]), 1e-6)
    ys, xs = np.mgrid[0:128, 0:128]
    nx, ny = -(knee[1] - hip[1]), knee[0] - hip[0]
    front = ((xs + 0.5 - hip[0]) * nx + (ys + 0.5 - hip[1]) * ny) > 0
    paint(can, bulb & ~edge & (d > 1.0) & (d <= 2.2) & front, "p")
    # the cuff: the bulb's last 2 px along the thigh (its end is flat at the knee), silver
    cuff = bulb & ((1 - t) * length < 2.0)
    paint(can, cuff, "w")
    paint(can, cuff & edge, "t")
    # the foot block: a forward foot hangs from the ankle (heel 2 columns behind it); a down foot points down
    if foot_down:
        f = np.rot90(foot, -1)
        fh, fw = f.shape[:2]
        x0, y0 = int(round(ankle[0])) - fw // 2, int(round(ankle[1]))
    else:
        f = foot
        fh, fw = f.shape[:2]
        x0, y0 = int(round(ankle[0])) - 2, int(round(ankle[1])) + 1
    x0, y0 = max(0, x0), max(0, y0)
    y1, x1 = min(128, y0 + fh), min(128, x0 + fw)
    sub = f[:y1 - y0, :x1 - x0]
    m = sub[..., 3] > 0
    can[y0:y1, x0:x1][m] = sub[m]


def over(can, part):
    m = part[..., 3] > 0
    can[m] = part[m]


def shift(a, dx, dy):
    return np.roll(np.roll(a, dy, 0), dx, 1)


def build(sx=0.9, lift=0.45, kscale=0.8):
    import fix_shen_strips as F
    des = F.design()
    body, tail, apron, near_foot, far_foot = design_parts(des)
    with open(F.lp(JOINTS), encoding="utf-8") as f:
        J = json.load(f)
    hips_y = [j["joints"]["L_Hip"][1] for j in J]
    top = min(hips_y)
    frames = []
    for k, fr in enumerate(J):
        j = fr["joints"]
        bob = int(round((hips_y[k] - top) * 0.33))
        bob = min(bob, 1)
        can = np.zeros_like(des)
        legs = []
        # one vertical scale a frame: the planted leg's, its toe on the soles (the hip is the sash's row)
        hy = HIP_ROW + bob
        sys_ = [(SOLES + 1 - hy) / (j[f"{sd}_Toe"][1] - j[f"{sd}_Hip"][1]) for sd in ("L", "R") if j[f"{sd}_Toe"][1] >= 8.8]
        sy = sum(sys_) / len(sys_) if sys_ else 0.9
        for side_ in ("L", "R"):
            hip, knee, ankle, toe = (np.array(j[f"{side_}_{n}"][:2]) for n in ("Hip", "KneeLower", "Foot", "Toe"))
            z = j[f"{side_}_Foot"][2] + j[f"{side_}_KneeLower"][2]
            hx = MID + (hip[0] - LEAGUE_HIP_X) * HIP_SPREAD
            planted = toe[1] >= 8.8
            pts = {}
            for n, p in (("knee", knee), ("ankle", ankle), ("toe", toe)):
                pts[n] = [hx + (p[0] - hip[0]) * sx, hy + (p[1] - hip[1]) * sy]
            if planted:
                pts["toe"][1] = SOLES + 1
                pts["ankle"][1] = SOLES - 3
                pts["knee"][1] = KNEE_ROW
            else:                                   # the swing leg's lift compressed (League kicks heel to seat)
                for n in ("ankle", "toe"):
                    rest = SOLES - 3 if n == "ankle" else SOLES + 1
                    pts[n][1] = rest - (rest - pts[n][1]) * lift
                pts["knee"][1] = min(KNEE_ROW, max(hy + 4, hy + (pts["knee"][1] - hy) * kscale + (1 - kscale) * 8))
            legs.append((z, side_, (hx, hy), pts, planted))
        legs.sort(key=lambda l: l[0])                       # the farther leg first
        over(can, shift(tail, TAIL_DX, bob))
        over(can, shift(apron, 0, bob))
        for z, side_, (hx, hy), pts, planted in legs:
            foot = near_foot                     # the design's near foot (7 wide), toe forward, for both legs
            ankle, toe = pts["ankle"], pts["toe"]
            down = False                     # the foot is the design's block, only moved (「脚也别变形」)
            draw_leg(can, (hx, hy), tuple(pts["knee"]), (ankle[0], ankle[1]), (toe[0], toe[1]), foot, down)
        over(can, shift(body, 0, bob))
        can[SOLES + 1:] = 0
        frames.append((can, bob, legs))
    return frames


def frames(sx=0.9, lift=0.45, kscale=0.8):
    """The 8 run frames (128 x 128 canvases, the soles on row 99)."""
    return [can for can, _, _ in build(sx, lift, kscale)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sx", type=float, default=0.9)
    ap.add_argument("--lift", type=float, default=0.45)
    ap.add_argument("--kscale", type=float, default=0.8)
    ap.add_argument("--out", default=os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "sn_work", "legs_proto"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frames = build(a.sx, a.lift, a.kscale)
    z = 6
    r0, r1, c0, c1 = 52, 101, 38, 90
    tiles = []
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
    except OSError:
        font = ImageFont.load_default()
    for k, (can, bob, legs) in enumerate(frames, 1):
        Image.fromarray(can).save(os.path.join(a.out, f"run_{k}.png"))
        c = can[r0:r1, c0:c1]
        im = Image.new("RGBA", (c.shape[1] * z, c.shape[0] * z + 16), (226, 226, 226, 255))
        im.alpha_composite(Image.fromarray(c).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST), (0, 16))
        d = ImageDraw.Draw(im)
        d.text((2, 0), f"run {k} bob {bob}", fill=(200, 0, 0, 255), font=font)
        for zz, side_, (hx, hy), pts, planted in legs:
            col = (0, 200, 255, 255) if side_ == "L" else (255, 120, 0, 255)
            P = [(hx, hy), tuple(pts["knee"]), tuple(pts["ankle"]), tuple(pts["toe"])]
            for (x0, y0), (x1, y1) in zip(P, P[1:]):
                d.line([((x0 - c0) * z, 16 + (y0 - r0) * z), ((x1 - c0) * z, 16 + (y1 - r0) * z)], fill=col, width=1)
        d.line([(0, 16 + (SOLES + 1 - r0) * z), (im.width, 16 + (SOLES + 1 - r0) * z)], fill=(220, 60, 60, 255))
        tiles.append(im)
    import fix_shen_strips as F
    des = F.design()[r0:r1, c0:c1]
    dim = Image.new("RGBA", (des.shape[1] * z, des.shape[0] * z + 16), (226, 226, 226, 255))
    dim.alpha_composite(Image.fromarray(des).resize((des.shape[1] * z, des.shape[0] * z), Image.NEAREST), (0, 16))
    ImageDraw.Draw(dim).text((2, 0), "design", fill=(200, 0, 0, 255), font=font)
    tiles.insert(0, dim)
    W, H = tiles[0].size
    sheet = Image.new("RGB", (5 * (W + 6), 2 * (H + 6)), (255, 255, 255))
    for i, t in enumerate(tiles[:10]):
        sheet.paste(t.convert("RGB"), ((i % 5) * (W + 6), (i // 5) * (H + 6)))
    sheet.save(os.path.join(a.out, "sheet.png"))
    print(os.path.join(a.out, "sheet.png"), sheet.size)


if __name__ == "__main__":
    main()
