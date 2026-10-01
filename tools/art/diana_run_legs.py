#!/usr/bin/env python3
"""Diana's run from the waist down: the idle's skirt and legs on League's run, under Codex's upper body.

    python tools/art/diana_run_legs.py [--src assets/source/diana/codex_run] [--out assets/source/diana/run_legs]

The user, after five Codex rounds on the run's legs: "你能好好做吗 待机的腿和跑步的腿都不一样", "要用待机的腿啊 跑步的
腿在魔改吗？", "还有走路姿势和英雄联盟一样吗", then of a first rebuild "腰部和腿部还是很怪". Two rounds of independent
visual critiques gave what this tool now does:
  - skirt: the idle wears a long coat-skirt (belt rows 59-60, navy tabard with trim and a teal panel to row 68; only
    knee guards, greaves and boots below it) - the run had a short teal skirt and long bare sticks. So the skirt is
    the idle's own pixels (SKIRT_ROWS x SKIRT_COLS; the cape's purple and the olive specks at its cut edges turned
    navy), outlined, in one column in every frame; its back hem trails a square while a leg kicks back and its front
    hem lifts a row over a knee swinging forward;
  - upper body: Codex's frame (codex_run/, its align5) above the belt, BODY_DOWN rows lower (it stood 2 rows taller
    than the idle), with its hands and the blade's arc; CLEAN first takes out leftovers that looked odd (frames 4, 6,
    8: a stick, specks and a cuff under the right hand; 4 and 8: a dark line under the left hand);
  - stride: one supporting leg per half (the far leg in frames 1-4, the near one in 5-8, mirrored, so both steps are
    alike - a first rebuild limped and hopped). The supporting boot lies flat with its sole outline on the soles row
    and steps back a square a frame (SUPPORT_DX from its hip: landing slightly ahead, pushing off slightly behind); its
    knee comes from the two leg lengths. The swinging leg follows League's run: assets/source/diana/
    lol_run_leg_segments.json holds League's hip, knee, ankle and toe per frame and leg measured on the game-size
    renders (three parts renders of poses.json; League's skeleton joints sit above its chibi-scaled legs); its two
    halves are averaged into one swing. A heel kicked up goes behind the skirt (the skirt and its outline are drawn
    over it, as League's skirt covers it); a lifted boot stays a row off the ground;
  - hips inside the skirt (HIP_Y), like League's, so a leg swung back bends at the hem instead of kneeling below it;
  - the idle's pieces: a grey-blue knee cap with a diagonal gold trim, a two-square silver greave, a boot about five
    squares long, heel and toe, darker on its sole side; one outline round each leg, a single line where they overlap;
  - height: BOB rows lower in the middle of each stance (both steps alike), one row at most from frame to frame.
Writes <out>/native/diana_run_1x.png and <out>/manifest.json (the source's, eye marks moved with the body) for
tidy_diana.py --run.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SOURCE = os.path.join(ROOT, "assets", "source")
POSES = os.path.join(SOURCE, "diana", "lol_run_leg_segments.json")
SOLES = 79
THIGH, SHIN = 11.0, 6.0                     # long enough that the supporting boot reaches the ground in every frame
BOOT_LEN, BOOT_W = 4.5, 1.0                 # the idle's boot: ~5 squares heel to toe, 2 rows + outline
ANKLE_Y = SOLES - 1.0                       # a flat boot round the ankle fills rows 77-78, its sole outline is row 79
HIP_GAP = 3.5                               # League's near hip is ~3.5 px in front of the far one in all 8 frames
HIP_Y = 61.5
SUPPORT_DX = (2.5, 1.5, 0.5, -0.5)          # the supporting ankle from its hip, frame by frame of a half
BOB = (0, 0, 1, 1)                          # rows lower, frame by frame of a half
SKIRT_ROWS, SKIRT_COLS = (59, 69), (36, 48)  # idle frame 1: belt to hem, teal panel + tabard
TORSO_ROWS = (54, 57)                        # rows whose middle lines the skirt up
BODY_DOWN = 2
R_THIGH, R_SHIN = 1.3, 1.0
INK = (0x0A, 0x04, 0x12, 255)
NAVY, NAVY_D, NAVY_L = (0x33, 0x3B, 0x63, 255), (0x22, 0x23, 0x3C, 255), (0x50, 0x51, 0x69, 255)
SILVER, SILVER_D = (0xB8, 0xBF, 0xC7, 255), (0x60, 0x63, 0x7E, 255)
GOLD, GOLD_D = (0xF3, 0xD9, 0x8D, 255), (0xA7, 0x80, 0x4A, 255)
STRAY = {(0x49, 0x2B, 0x5B), (0x81, 0x87, 0x68), (0x50, 0x59, 0x45)}   # cape purple, olive specks: navy in the skirt
CLEAN = {4: [(54, 62), (55, 62), (56, 62), (28, 61), (29, 61), (27, 62), (28, 62), (27, 63), (28, 63), (27, 64), (28, 64),
             (27, 65), (27, 66)],
         6: [(53, 62)],
         8: [(52, 62), (53, 62), (54, 62), (55, 62), (51, 63), (53, 63), (54, 63), (51, 64), (26, 61), (27, 61), (25, 62),
             (26, 62), (28, 62), (25, 63), (25, 64), (25, 65), (25, 66)]}


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) or 1)


def mid_x(f, rows, cols=(32, 52)):
    xs = [x for y in range(*rows) for x in range(*cols) if f[y, x, 3]]
    return (min(xs) + max(xs)) / 2


def directions(P):
    """League's thigh, shin and foot directions of one leg; a knee hidden behind the other leg goes just in front of
    the hip-ankle line, 55% of the way down."""
    hip, knee, ankle, toe = (None if P[n] is None else np.array(P[n], float) for n in ("hip", "knee", "ankle", "toe"))
    if knee is None:
        v = ankle - hip
        knee = hip + 0.55 * v + unit([-v[1], v[0]])
    return unit(knee - hip), unit(ankle - knee), unit(toe - ankle)


def swing_dirs(poses):
    """The swinging leg's directions for frames 1-4 of a half: League's near leg in its frames 1-4 averaged with its
    far leg in frames 5-8 (each swings while the other supports)."""
    return [[unit(a + b) for a, b in zip(directions(poses[k]["L"]), directions(poses[k + 4]["R"]))] for k in range(4)]


def ik_knee(hip, ankle, forward=1.0):
    """The knee of a two-bone leg from hip to ankle, bent forward; the ankle pulled in if out of reach."""
    v = ankle - hip
    d = np.linalg.norm(v)
    if d >= THIGH + SHIN - 1e-6:
        ankle = hip + v / d * (THIGH + SHIN - 1e-3)
        v, d = ankle - hip, THIGH + SHIN - 1e-3
    a = np.arccos(np.clip((THIGH ** 2 + d ** 2 - SHIN ** 2) / (2 * THIGH * d), -1, 1))
    u = v / d
    cands = []
    for s in (1, -1):
        c, sn = np.cos(s * a), np.sin(s * a)
        r = np.array([u[0] * c - u[1] * sn, u[0] * sn + u[1] * c])
        cands.append(hip + THIGH * r)
    return max(cands, key=lambda k: k[0] * forward), ankle


def seg_mask(h, w, a, b, r):
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs + 0.5, ys + 0.5
    vx, vy = b[0] - a[0], b[1] - a[1]
    t = np.clip(((px - a[0]) * vx + (py - a[1]) * vy) / max(vx * vx + vy * vy, 1e-6), 0, 1)
    d = np.hypot(px - (a[0] + t * vx), py - (a[1] + t * vy))
    return d <= r, t, px, py


def draw_leg(hip, knee, ankle, foot, far, h=96, w=96):
    """The fill (no outline) of one leg in the idle's pieces."""
    fill = np.zeros((h, w, 4), np.uint8)
    m_thigh, _, _, _ = seg_mask(h, w, hip, knee, R_THIGH)
    m_shin, t_shin, px, py = seg_mask(h, w, knee, ankle, R_SHIN)
    fill[m_thigh] = NAVY
    fill[m_shin] = SILVER
    fill[m_shin & (t_shin > 0.65)] = SILVER_D
    heel = ankle - foot * 1.0
    toe = ankle + foot * (BOOT_LEN - 1.0)
    m_boot, _, _, _ = seg_mask(h, w, heel, toe, BOOT_W)
    sole = ((px - heel[0]) * foot[1] - (py - heel[1]) * foot[0]) < -0.2
    fill[m_boot] = NAVY_D if far else NAVY
    fill[m_boot & sole] = NAVY_D
    kx, ky = int(np.floor(knee[0])), int(np.floor(knee[1]))
    for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
        if 0 <= ky + dy < h and 0 <= kx + dx < w:
            fill[ky + dy, kx + dx] = NAVY_L
    for (dx, dy), c in (((1, -1), GOLD), ((1, 0), GOLD_D if far else GOLD), ((0, 1), GOLD_D), ((-1, 1), GOLD_D)):
        if 0 <= ky + dy < h and 0 <= kx + dx < w:
            fill[ky + dy, kx + dx] = c
    return fill


def ring(mask):
    p = np.pad(mask, 1)
    return (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~mask


def legs_layer(far_leg, near_leg):
    """Far leg, then the near one over it: one outline round each, a single line where they overlap."""
    far, near = draw_leg(*far_leg, far=True), draw_leg(*near_leg, far=False)
    fm, nm = far[..., 3] > 0, near[..., 3] > 0
    out = np.zeros_like(far)
    fr = ring(fm)
    out[fm] = far[fm]
    out[fr & ~nm] = INK
    out[nm] = near[nm]
    nr = ring(nm)
    out[nr & ~fm] = INK
    p = np.pad(fr, 1)
    out[nr & fm & ~(p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])] = INK
    return out


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]


def shifted(a, dy, dx=0):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    out[max(0, dy):min(h, h + dy), max(0, dx):min(w, w + dx)] = a[max(0, -dy):min(h, h - dy), max(0, -dx):min(w, w - dx)]
    return out


def upper(f, dy):
    """Codex's frame above the belt, its hands and the blade's arc, dy rows lower."""
    up = np.zeros_like(f)
    up[:TORSO_ROWS[1]] = f[:TORSO_ROWS[1]]
    up[TORSO_ROWS[1]:60, :35] = f[TORSO_ROWS[1]:60, :35]          # the left hand on the blade
    up[TORSO_ROWS[1]:, :30] = f[TORSO_ROWS[1]:, :30]              # the blade's arc
    up[TORSO_ROWS[1]:66, 49:] = f[TORSO_ROWS[1]:66, 49:]           # the right hand
    up = shifted(up, dy)
    up[SOLES + 1:] = 0                                            # the blade's tip never below the ground
    return up


def skirt_ring(s):
    """The outline round a skirt stamp: next to its colours only - where the idle's own dark line already edges it (the
    hem over the knees, the cape's side) a second line would make a black band."""
    op = s[..., 3] > 0
    ink = op & np.isin(s[..., 0], (0x0A, 0x0C)) & np.isin(s[..., 1], (0x04, 0x05)) & np.isin(s[..., 2], (0x12, 0x16))
    return ring(op & ~ink) & ~op


def skirt(idle, dx, dy, trail, lift):
    s = np.zeros_like(idle)
    (y0, y1), (x0, x1) = SKIRT_ROWS, SKIRT_COLS
    s[y0:y1, x0:x1] = idle[y0:y1, x0:x1]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if s[y, x, 3] and tuple(int(v) for v in s[y, x, :3]) in STRAY:
                s[y, x] = NAVY_D
    if trail:                                  # the back of the last 3 rows one square back
        part = s[y1 - 3:y1, x0:x0 + 5].copy()
        s[y1 - 3:y1, x0:x0 + 5] = 0
        s[y1 - 3:y1, x0 - 1:x0 + 4] = part
    if lift:                                   # the front of the hem row one row up
        s[y1 - 1, x1 - 5:x1] = 0
    s[skirt_ring(s)] = INK
    return shifted(s, dy, dx)


def build(run, idle, poses):
    out = np.zeros_like(run)
    idle_mid = mid_x(idle, (TORSO_ROWS[0] + BODY_DOWN, TORSO_ROWS[1] + BODY_DOWN))
    mids = []
    for k in range(8):
        f = run[(k // 4) * 96:(k // 4) * 96 + 96, (k % 4) * 96:(k % 4) * 96 + 96]
        mids.append(mid_x(f, TORSO_ROWS))
    dx = int(round(np.mean(mids) - idle_mid))                         # one skirt column for all frames
    cx = (SKIRT_COLS[0] + SKIRT_COLS[1] - 1) / 2 + dx
    sw = swing_dirs(poses)
    dys = []
    for k in range(8):
        y0, x0 = (k // 4) * 96, (k % 4) * 96
        f = run[y0:y0 + 96, x0:x0 + 96].copy()
        for x, y in CLEAN.get(k + 1, []):
            f[y, x] = 0
        p = k % 4
        bob = BOB[p]
        hips = {"L": np.array([cx + HIP_GAP / 2, HIP_Y + bob]), "R": np.array([cx - HIP_GAP / 2, HIP_Y + bob])}
        sup, swg = ("R", "L") if k < 4 else ("L", "R")
        # the supporting leg: flat boot on the ground, stepping back a square a frame
        ankle = np.array([hips[sup][0] + SUPPORT_DX[p], ANKLE_Y])
        knee, ankle = ik_knee(hips[sup], ankle)
        legs = {sup: (hips[sup], knee, ankle, np.array([1.0, 0.0]))}
        # the swinging leg: League's directions; its boot kept a square clear of the skirt and off the ground
        th, sh, ft = sw[p]
        kn = hips[swg] + THIGH * th
        an = kn + SHIN * sh
        legs[swg] = (hips[swg], kn, an, ft)
        trail = kn[0] < hips[swg][0] - 3
        lift = kn[0] > hips[swg][0] + 2
        sk = skirt(idle, dx, bob, trail, lift)
        for _ in range(12):                                              # a lifted boot stays off the ground
            sw_only = draw_leg(*legs[swg], far=swg == "R")
            rows = np.nonzero((sw_only[..., 3] > 0).any(1))[0]
            if not len(rows) or rows.max() + 1 <= SOLES - 1:              # its outline at least a row up
                break
            an = an + np.array([-0.4, -0.5])
            legs[swg] = (hips[swg], kn, an, ft)
        frame = legs_layer(legs["R"], legs["L"])
        over(frame, sk)
        over(frame, upper(f, BODY_DOWN + bob))
        low = int(np.nonzero(frame[..., 3].any(1))[0].max())
        assert low <= SOLES, (k, low)
        out[y0:y0 + 96, x0:x0 + 96] = frame
        dys.append(bob)
    return out, dys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(SOURCE, "diana", "codex_run"))
    ap.add_argument("--out", default=os.path.join(SOURCE, "diana", "run_legs"))
    a = ap.parse_args()
    with open(lp(POSES), encoding="utf-8") as f:
        poses = json.load(f)["frames"]
    with open(lp(os.path.join(a.src, "manifest.json")), encoding="utf-8") as f:
        man = json.load(f)
    run = np.asarray(Image.open(lp(os.path.join(a.src, man["native_file"]))).convert("RGBA"))
    idle = np.asarray(Image.open(lp(os.path.join(SOURCE, "native", "diana_idle.png"))).convert("RGBA"))[::8, ::8][:96, :96]
    out, dys = build(run, idle, poses)
    os.makedirs(lp(os.path.join(a.out, "native")), exist_ok=True)
    Image.fromarray(out).save(lp(os.path.join(a.out, "native", "diana_run_1x.png")))
    frames = [dict(fr) for fr in man["frames"]]
    for k, fr in enumerate(frames):                 # the face moved with the body: where tidy_diana looks for it
        if fr.get("eye_mark"):
            fr["eye_mark"] = [fr["eye_mark"][0], fr["eye_mark"][1] + BODY_DOWN + dys[k]]
    man = dict(man, frames=frames, native_file="native/diana_run_1x.png",
               note="waist down rebuilt by tools/art/diana_run_legs.py: the idle's skirt and legs on League's run")
    with open(lp(os.path.join(a.out, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    print("rebuilt; body rows lower per frame", [BODY_DOWN + d for d in dys])


if __name__ == "__main__":
    main()
