#!/usr/bin/env python3
"""league_pantheon's frames: Codex's step-2 strips (assets/source/pantheon/codex_strips, its 1x copies on the design's
153 x 153 grid at PPU 1.5) and the design -> the dense strips at PPU 1.5 and the 1x sheet.

    python tools/art/rig_pantheon.py [--review DIR]

The user, 2026-10-16: 「完成这一步 有问题的地方你帮忙修复 然后自己review 完美了再喊我review」. Codex's frames are already at
the user's density (「选A 40尺寸 PPU1.5」, design = model1_cut 66 x 66 squares), so nothing is rescaled: each tag is a list
of Codex frames, re-ordered, reused or moved by whole squares (lossless - the no-deformation rule), never redrawn:
  * attack: frame 1 held the spear head backward (Codex's HANDOFF too) -> Q's wind-up (skill_1, the head forward);
  * attack_w (empowered W: three thrusts): Codex's 3rd frame lifted the spear over the head on one leg -> wind-up,
    thrust, the thrust pulled back (the whole frame DRAW squares back), thrust, pulled back, thrust, recover;
  * skill_throw: frames 1 and 3 held the head backward -> the low wind-up (skill_1), the cock (2), the cock lunging
    forward (2 moved WHIP squares on), the release with the hand empty (4, 5), the spear back (6);
  * e_hold (the 1.5 s channel loop): frame 1 raised the spear overhead and 3 turned it backward -> the two
    thrusts (2, 4), each drawn back first (moved DRAW squares back);
  * e_bash: frames 1 and 4 turned the spear backward and the shield barely moved -> 2, 3, 3 lunging BASH squares
    forward (the bash), 3 a little forward, 5;
  * ult_leap: the three frames stood at one height -> lifted LEAP squares more each;
  * ult_land: 3 put the spear's gem on the shield, 4 did not come back to the stance -> 1, 2, 2 rising RISE squares,
    the design;
  * dead: 6 = 4 (the last picture still); the first lying picture dropped onto the ground with a bounce (8 frames);
  * run: Codex's run redo (assets/source/pantheon/codex_run, the legs on League's run; RUN_ORDER below);
  * idle: the design breathing (above the waist up BREATH squares, the spear and the shield carried whole);
    hit: the design moved HIT_DX back, a white flash on the first frame;
  * tidy (rig_kalista's): the outline closed, 1-square slits and small holes filled, loose specks off.
Writes assets/source/ppu/orig/pantheon_<tag>.png / .json (each round(PPU x its 1x frame) round the pivot) and
league/champions/league_pantheon#sheet.png / #anim.fanim (the 1x tags). Then tools/art/ppu_restyle.py --hero pantheon
and tools/art/ppu_hd.py --hero pantheon.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "pantheon")
STRIPS = os.path.join(SRC, "codex_strips")
RUN = os.path.join(SRC, "codex_run")
STEM = os.path.join(ROOT, "league", "champions", "league_pantheon")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.5
FEET = 11                         # 1x rows from the pivot down to the ground row
SOLE, PIV_X, N = 140, 66, 153     # the pack's grid (tools/art/pack_pantheon_strips.py)
CORNER = (PIV_X + 0.5, SOLE + 1)  # the pivot column and the ground line, in squares
ORDER = ["idle", "run", "attack", "attack_w", "skill", "skill_throw", "skill2", "e_hold", "e_bash", "ult", "ult_leap",
         "ult_land", "hit", "dead"]
IDLE_MS = 150
BREATH = [0, 1, 1, 2, 2, 2, 1, 1]  # >= 2 rows of rise (the idle rule: BP idles that barely move)
HIT_DX = 3
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
DRAW, WHIP, BASH, RISE = 3, 3, 5, 2
LEAP = [0, 6, 14]
HOLE_FILL = 8
SPECK = 10
# the design's spear: the line from its butt to its head (design squares), the half width taken as the spear
SPEAR = ((10.5, 31.5), (65.0, 61.0), 1.6)
# The idle, the hit and the landing's last frame stand in Codex's ready stance (Q's recovery, skill_4), not the upright
# design: the design stood 66 squares tall and every Codex action crouches (51-60), so each change from the idle
# dropped him 6-10 game px (Darius's run stays at his idle's height) - the user: 「潘森还是变大变小啊」「局内模型为什么
# 变这么小了」. skill_4 is the design's own pose drawn lower by Codex at the strips' size, its spear one 2:1 line.
IDLE_SRC = "skill_4"
IDLE_SPEAR = ((36.0, 111.0), (92.0, 139.0), 1.9)   # canvas squares: the butt, the tip, the half width (its outline)
IDLE_HEAD_X = 78                                    # the spear head's first column (its widening, carried too)
# tag -> [(source, dx, dy, ms)]: source = "<tag>_<n>" of the step-2 strips, "design", dx > 0 = forward (right)
TABLE = {
    "attack": [("skill_1", 0, 0, 80), ("attack_2", 0, 0, 80), ("attack_3", 0, 0, 100), ("attack_4", 0, 0, 90),
               ("attack_5", 0, 0, 90)],
    "attack_w": [("attack_w_1", 0, 0, 60), ("attack_w_2", 0, 0, 70), ("attack_w_2", -DRAW, 0, 50),
                 ("attack_w_4", 0, 0, 70), ("attack_w_4", -DRAW, 0, 50), ("attack_w_5", 0, 0, 80),
                 ("attack_w_6", 0, 0, 90)],
    "skill": [("skill_1", 0, 0, 60), ("skill_2", 0, 0, 60), ("skill_3", 0, 0, 90), ("skill_4", 0, 0, 90)],
    "skill_throw": [("skill_1", 0, 0, 100), ("skill_throw_2", 0, 0, 140), ("skill_throw_2", WHIP, 0, 80),
                    ("skill_throw_4", 0, 0, 90), ("skill_throw_5", 0, 0, 90), ("skill_throw_6", 0, 0, 100)],
    "skill2": [(f"skill2_{k}", 0, 0, ms) for k, ms in zip(range(1, 7), (60, 60, 60, 70, 90, 100))],
    "e_hold": [("e_hold_2", -DRAW, 0, 125), ("e_hold_2", 0, 0, 125), ("e_hold_4", -DRAW, 0, 125),
               ("e_hold_4", 0, 0, 125)],
    "e_bash": [("e_bash_2", 0, 0, 60), ("e_bash_3", 0, 0, 60), ("e_bash_3", BASH, 0, 90), ("e_bash_3", 2, 0, 80),
               ("e_bash_5", 0, 0, 90)],
    "ult": [(f"ult_{k}", 0, 0, ms) for k, ms in zip(range(1, 5), (100, 100, 150, 650))],
    "ult_leap": [(f"ult_leap_{k}", 0, -LEAP[k - 1], ms) for k, ms in zip(range(1, 4), (80, 80, 120))],
    "ult_land": [("ult_land_1", 0, 0, 80), ("ult_land_2", 0, 0, 120), ("ult_land_2", 0, -RISE, 150),
                 (IDLE_SRC, 0, 0, 150)],
    # 8 frames (2026-10-19 frame audit, the pack's deaths have 8): the first lying picture also 4 squares above the
    # ground before it lands and 1 after (a bounce)
    "dead": [("dead_1", 0, 0, 100), ("dead_2", 0, 0, 100), ("dead_3", 0, -4, 50), ("dead_3", 0, 0, 70),
             ("dead_3", 0, -1, 50), ("dead_4", 0, 0, 120), ("dead_5", 0, 0, 150), ("dead_4", 0, 0, 400)],
}
# the run: Codex's leg redo (RUN_REDO.md) - RUN_ORDER: 1-2 the near leg ahead, 3 the legs crossing, 4-6 the far leg ahead; its 7
# and 8 came back broken (outline gaps round the loincloth, loose pieces by the shield), so the loop is 7 frames with 3
# again as the second crossing (League's cycle 933 ms: 7 x 133). Its far-leg-ahead frames put the planted foot 79, 83,
# 80 squares out (4, 5, 6): played 5, 6, 4 and 4 moved 2 back, 2 moved 2 back too, each planted foot goes back under
# the body frame by frame (69, 67 / 83, 80, 77) - no glide forward.
# 2026-10-19 frame audit: 8 frames like the pack's runs - the near-leg-ahead half gets a third frame as the far half
# has, 1 moved 2 forward before it (its planted foot going back under the body frame by frame, as 5, 6, 4 do), 117 ms
# each so the cycle stays League's 933 ms
RUN_ORDER = [(1, 2), (1, 0), (2, -2), (3, 0), (5, 0), (6, 0), (4, -2), (3, 0)]
RUN_MS = 117
# Codex drew the run redo bigger than the design: its helmet 11 squares wide and 17 tall against the idle's 9 and 15 -
# the user: 「还有模型会变大变小」 (idle <-> run). The run is brought to the idle's size by taking whole rows and columns
# out (tools/art/shrink_frames.py, league_senna's way: nothing resampled, the soles on their row).
RUN_SCALE = 0.87


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


DESIGN = load(os.path.join(SRC, "hd", "design.png"))


def palette():
    d = DESIGN
    cols = {tuple(int(v) for v in c) for c in d[d[..., 3] > 0][:, :3]}
    return np.array(sorted(cols, key=sum), np.uint8)


PAL = palette()
OUTLINE = tuple(int(v) for v in PAL[0])


def design_canvas():
    """The design on the pack's canvas, its feet's middle on the pivot column, the soles on SOLE."""
    d = DESIGN
    h, w = d.shape[:2]
    ys, xs = np.nonzero(d[-4:, :, 3] > 0)
    x0 = int(round(PIV_X - (xs.min() + xs.max()) / 2.0))
    y0 = SOLE - (h - 1)
    can = np.zeros((N, N, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    return can, (x0, y0)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys, xs = np.nonzero(a[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W) & (ty <= SOLE)
    out[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
    return out


def frame(src):
    if src == "design":
        return design_canvas()[0]
    tag, k = src.rsplit("_", 1)
    if tag == "run" and os.path.isdir(lp(RUN)):
        return load(os.path.join(RUN, f"pantheon_run_{k}_1x.png"))
    return load(os.path.join(STRIPS, f"pantheon_{src}_1x.png"))


def cracks(a):
    out = a.copy()
    for _ in range(2):
        op = out[..., 3] > 0
        lr = np.zeros_like(op)
        lr[:, 1:-1] = op[:, :-2] & op[:, 2:]
        ud = np.zeros_like(op)
        ud[1:-1] = op[:-2] & op[2:]
        m = (lr | ud) & ~op
        if not m.any():
            break
        out[m, :3] = OUTLINE
        out[m, 3] = 255
    return out


def tidy(a):
    out = G.complete_outline(cracks(a), color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > HOLE_FILL:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < SPECK:
                out[lbl == k] = 0
    return out


def dist_line(x, y, a, b):
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(x - (ax + t * dx), y - (ay + t * dy))


def spear_mask(can, at):
    """The design's spear on the canvas (the pixels within the spear line's half width, the head's widening too)."""
    a, b, r = SPEAR
    ys, xs = np.nonzero(can[..., 3] > 0)
    x0, y0 = at
    d = dist_line(xs - x0 + 0.5, ys - y0 + 0.5, a, b)
    head = (xs - x0 >= 52) & (d <= 3.2)
    m = np.zeros(can.shape[:2], bool)
    sel = (d <= r) | head
    m[ys[sel], xs[sel]] = True
    return m


def breathe(a, waist, k, carried):
    if k == 0:
        return a.copy()
    out = a.copy()
    mask = np.zeros(a.shape[:2], bool)
    mask[:waist] = a[:waist, :, 3] > 0
    mask |= carried
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    out[ys - k, xs] = a[ys, xs]
    hole = (out[..., 3] == 0) & mask & ~carried
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            if y + 1 < a.shape[0] and out[y + 1, x, 3] > 0:
                out[y, x] = out[y + 1, x]
    return out


def idle_spear(can):
    """The idle frame's spear (IDLE_SPEAR's line, its head's widening too), carried whole by the breath."""
    (x0, y0), (x1, y1), r = IDLE_SPEAR
    ys, xs = np.nonzero(can[..., 3] > 0)
    a = (y1 - y0) / (x1 - x0)
    d = np.abs((ys + 0.5 - y0) - a * (xs + 0.5 - x0)) / np.hypot(1, a)
    sel = ((d <= r) & (xs >= x0 - 2)) | ((xs >= IDLE_HEAD_X) & (d <= 3.2))
    m = np.zeros(can.shape[:2], bool)
    m[ys[sel], xs[sel]] = True
    return m


def idle_frames():
    can = frame(IDLE_SRC)
    ys = np.nonzero(can[..., 3] > 0)[0]
    waist = int(ys.min() + (ys.max() - ys.min()) * 0.55)
    carried = idle_spear(can)
    return [(tidy(breathe(can, waist, b, carried)), IDLE_MS) for b in BREATH]


def hit_frames():
    can = frame(IDLE_SRC)
    out = []
    for dx, flash, ms in HIT:
        a = shift(can, -dx, 0)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, ms))
    return out


def centred(can):
    """A canvas frame centred on the pivot square (shrink_frames' form)."""
    px, py = int(CORNER[0]), int(CORNER[1] - FEET * PPU)
    w = max(px, can.shape[1] - 1 - px)
    out = np.zeros((2 * py + 1, 2 * w + 1, 4), np.uint8)
    out[:can.shape[0], w - px:w - px + can.shape[1]] = can[:2 * py + 1]
    return out


def on_canvas(a, like):
    """A pivot-centred frame back on the canvas."""
    px, py = int(CORNER[0]), int(CORNER[1] - FEET * PPU)
    can = np.zeros_like(like)
    y0, x0 = py - a.shape[0] // 2, px - a.shape[1] // 2
    ys, xs = max(0, -y0), max(0, -x0)
    ye, xe = min(a.shape[0], can.shape[0] - y0), min(a.shape[1], can.shape[1] - x0)
    can[y0 + ys:y0 + ye, x0 + xs:x0 + xe] = a[ys:ye, xs:xe]
    return can


def shrunk(frames, idle, scale):
    """frames at `scale` of their size, whole rows and columns out (the idle's body range counts them)."""
    import shrink_frames as SF
    cf = [(centred(a), ms) for a, ms in frames]
    plan = SF.plan_tag(cf, SF.body_of([(centred(idle[0][0]), 0)]), scale)
    return [(on_canvas(a, frames[0][0]), ms) for a, ms in SF.apply_tag(cf, plan)]


def actions():
    out = {"idle": idle_frames(), "hit": hit_frames()}
    out["run"] = shrunk([(tidy(shift(frame(f"run_{k}"), dx, 0)), RUN_MS) for k, dx in RUN_ORDER], out["idle"],
                        RUN_SCALE)
    for tag, rows in TABLE.items():
        out[tag] = [(tidy(shift(frame(src), dx, dy)), ms) for src, dx, dy, ms in rows]
    return {t: out[t] for t in ORDER}


def one_of(can, px, py, hw, hh, need=0.5):
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot). The pivot: the pivot
    column, FEET 1x rows above the ground line."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh))[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's PPU frames on the canvas (1 square = 1 px) here")
    a = ap.parse_args()
    acts = actions()
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, t in frames:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"pantheon_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"pantheon_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            for j, (can, _) in enumerate(frames):
                Image.fromarray(can).save(os.path.join(a.review, f"pantheon_{tag}_{j + 1}_1x.png"))
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_pantheon#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
