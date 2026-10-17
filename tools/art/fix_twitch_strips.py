#!/usr/bin/env python3
"""Twitch's strips (assets/source/native/twitch_<tag>.png): Codex's step-2 delivery with its faults fixed from the
design's own pixels (tools/art/rigkit.py; the user: 「完成下一步 有不对的地方你帮忙修改 灵活利用工具」).

    python tools/art/fix_twitch_strips.py [--review DIR]

Codex (assets/source/twitch/codex_strips/, raw/rebuild_twitch_strips.py) posed every action from the design's parts
too - the head pasted, the rat legs the design's own - and its idle, attack, Q and hit frames are kept as delivered.
Rebuilt here:
  W / E / R  Codex cut the near arm as a 12 x 12 box (rows 79-90, columns 55-66: the backpack's lower edge, the belt
             pouch and the coat went with it) and filled the hole with flat stripes - a blue-and-teal block on his
             side in every frame the arm moved. ARM is the arm alone: the green upper arm hanging from the shoulder
             (columns 57-59, rows 76-82) and the forearm and hand reaching the stock (columns 60-66, rows 83-86).
             Where it leaves, each square takes the colour of the nearest square of his body to its left in that row
             (the backpack strap, the pouch, the coat), the outline left as it was. The moved arm (rigkit.turn about
             the shoulder, 45-degree steps) gets a ring of outline where it lies over his body, so it reads apart from
             the green backpack.
             R's crossbow went 8 right / 6 up and hung in the air apart from him: now it rises 4 rows and comes 2
             forward with the far hand on it, the stock still against his chest.
  run        the far leg was recoloured to the belt's dark brown (a brown block between his feet): it takes FAR_LEG, a
             shade of the legs' own grey-purple, and its toe claws stay the design's cream.
  dead       kept (hit, knocked back, 45 degrees, lying at 90 - Sivir's accepted fall).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as rig  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "twitch", "codex_strips")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "twitch_native.png")
OUT = os.path.join(ROOT, "assets", "source", "native")
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
LAYOUT = {"idle": (3, 2), "run": (4, 2), "attack": (3, 2), "skill": (3, 1), "skill2": (4, 1), "skill2_e": (3, 2),
          "ult": (3, 1), "hit": (2, 1), "dead": (4, 2)}
CW, CH = 128, 96
LEG = (112, 67, 94)              # the legs' and the tail's grey-purple
FAR_LEG = (78, 45, 68)           # one shade darker for the run's far leg
BROWN = (63, 35, 31)             # the belt's dark brown Codex used for it
SHOULDER = (58, 77)              # the near arm's shoulder on the design canvas (the outer corner)
# the near arm, rows -> (first, last) column, only its green / dark-teal / brass squares
ARM_ROWS = {76: (57, 58), 77: (57, 58), 78: (58, 58), 79: (58, 58), 80: (57, 59), 81: (57, 58), 82: (57, 58),
            83: (60, 65), 84: (60, 66), 85: (62, 66), 86: (62, 64)}
ARM_COLOURS = {(51, 107, 94), (25, 59, 67), (245, 169, 52), (2, 2, 1)}
BOW_ROWS = {82: (74, 82), 83: (67, 85), 84: (68, 89), 85: (68, 89), 86: (66, 88), 87: (66, 88), 88: (67, 88),
            89: (67, 88), 90: (77, 88), 91: (85, 88)}   # Codex's crossbow with the far hand on its fore-stock
BOW_JOINT = (67, 86)


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def load(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


DES = rig.Design(DESIGN)
D = DES.a
OUTLINE = DES.outline
OP = D[..., 3] > 0
HEAD = load(os.path.join(SRC, "source", "twitch_head_1x.png"))


def arm_mask():
    m = rig.mask_rows(ARM_ROWS) & OP
    keep = np.array([tuple(int(v) for v in D[y, x, :3]) in ARM_COLOURS for y, x in zip(*np.nonzero(m))])
    out = np.zeros_like(m)
    ys, xs = np.nonzero(m)
    out[ys[keep], xs[keep]] = True
    return out


ARM = arm_mask()
BOW = rig.mask_rows(BOW_ROWS) & OP


BODY_FILL = {(25, 59, 67), (51, 107, 94), (6, 107, 172), (0, 64, 122)}   # dark teal, green, coat blue, dark blue


def body_without(mask):
    """The design with `mask` lifted off: each square takes the nearest body square of his torso / coat colours
    (BODY_FILL) along its row, left first (no brass or brown streaks)."""
    b = D.copy()
    b[mask] = 0
    for y, x in sorted(zip(*np.nonzero(mask))):
        src = None
        for dx in (-1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -6, 6):
            q = (y, x + dx)
            if b[q][3] and not mask[q] and tuple(int(v) for v in b[q][:3]) in BODY_FILL:
                src = b[q]
                break
        b[y, x] = src if src is not None else (25, 59, 67, 255)
    return b


H_, B_, V_ = (51, 107, 94, 255), (25, 59, 67, 255), (253, 246, 208, 255)


def built_arm():
    """The near arm as one rigid piece pointing straight down from the shoulder (the design's arm is a strip and a
    hand blob that do not join): 3 squares wide in its own green with the dark-teal shadow side, 7 long, a 4-wide
    green claw hand with two cream claw tips, one outline ring. Joint = the shoulder (top middle)."""
    w, n = 3, 7
    s = np.zeros((n + 6, w + 4, 4), np.uint8)
    for r in range(n):
        s[1 + r, 1:4] = (H_, H_, B_)
    s[1 + n:1 + n + 3, 1:5] = H_
    s[1 + n + 2, 4] = B_
    s[1 + n + 3, 1] = V_
    s[1 + n + 3, 3] = V_
    op = s[..., 3] > 0
    ring = np.zeros_like(op)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        ring |= np.roll(np.roll(np.pad(op, 1), dy, 0), dx, 1)[1:-1, 1:-1]
    s[ring & ~op] = (*OUTLINE, 255)
    return rig.Part(s, (2.5, 1.0))


ARM_PART = built_arm()
# the venom cask in his hand: a 3x3 brass-hooped barrel of emerald venom in an outline ring
_P, _M, _L = (245, 169, 52, 255), (24, 226, 131, 255), (185, 102, 29, 255)
CASK = np.zeros((5, 5, 4), np.uint8)
CASK[...] = (*OUTLINE, 255)
CASK[1:4, 1:4] = [[_P, _M, _P], [_M, _M, _M], [_L, _P, _L]]
CASK[0, 0] = CASK[0, 4] = CASK[4, 0] = CASK[4, 4] = 0


def ringed(dst, part, at):
    """Place a moved part and outline it where it lies over the body (it reads apart from the green backpack)."""
    lay = np.zeros_like(dst)
    rig.place(lay, part, at)
    m = lay[..., 3] > 0
    H, W = m.shape
    grow = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow |= np.roll(np.roll(m, dy, 0), dx, 1)
    ring = grow & ~m & (dst[..., 3] > 0)
    dst[ring, :3] = OUTLINE
    dst[m] = lay[m]
    return dst


def pose(arm_deg=None, arm_shift=(0, 0), bow_shift=(0, 0), cask=False):
    """The design with the near arm turned arm_deg about the shoulder (None: in place) and the crossbow moved."""
    if arm_deg is None and bow_shift == (0, 0):
        a = D.copy()
    else:
        a = body_without((ARM if arm_deg is not None else np.zeros_like(ARM)) | (BOW if bow_shift != (0, 0) else
                                                                                  np.zeros_like(BOW)))
        if bow_shift != (0, 0):
            a[BOW & ~ARM] = body_without(ARM)[BOW & ~ARM] if arm_deg is not None else a[BOW & ~ARM]
            bow = rig.Part.from_canvas(D, BOW, BOW_JOINT)
            rig.place(a, bow, (BOW_JOINT[0] + bow_shift[0], BOW_JOINT[1] + bow_shift[1]))
    if arm_deg is not None:
        arm = rig.turn(ARM_PART, arm_deg)
        at = (SHOULDER[0] + arm_shift[0], SHOULDER[1] + arm_shift[1])
        ringed(a, arm, at)
        if cask:
            hand = hand_point(arm_deg, arm_shift)
            rig.put(a, CASK, hand[0] - 2, hand[1] - 2)
    rig.put(a, HEAD, 0, 0)
    return a


def hand_point(deg, shift):
    """The middle of the built arm's hand after its turn about the shoulder."""
    x, y = 0.0, 10.0
    t = math.radians(deg)
    return (round(SHOULDER[0] + x * math.cos(t) + y * math.sin(t) + shift[0]),
            round(SHOULDER[1] - x * math.sin(t) + y * math.cos(t) + shift[1]))


def settle(a, px, dx=0, dy=0):
    """The design canvas (pivot 64, 88) into a 128 x 96 cell with the pivot at (px, 70)."""
    return rig.shifted(a, px - 64 + dx, -18 + dy)[:CH]


def cells_of(tag):
    a = load(os.path.join(SRC, "1x", f"twitch_{tag}_1x.png"))
    cols, rows = LAYOUT[tag]
    n = len(CELLS["tags"][tag])
    return [a[(i // cols) * CH:(i // cols + 1) * CH, (i % cols) * CW:(i % cols + 1) * CW].copy() for i in range(n)]


CELLS = json.load(open(os.path.join(SRC, "twitch_cells.json"), encoding="utf-8"))


def build():
    out = {t: cells_of(t) for t in TAGS}
    piv = {t: [fr["pivot"][0] for fr in CELLS["tags"][t]] for t in TAGS}
    # run: the far leg in the legs' own darker shade instead of the belt's brown
    for f in out["run"]:
        m = (f[..., :3] == BROWN).all(-1) & (f[..., 3] > 0)
        low = np.zeros_like(m)
        low[70:, :] = True                    # only below the belt (the pouch above keeps its brown)
        f[m & low, :3] = FAR_LEG
    # W: the cask taken from the belt, wound back up, thrown forward (the hand empty), back to the stance
    w = [pose(-30, cask=True), pose(225, cask=True), pose(90, (1, 4)), pose()]
    out["skill2"] = [settle(a, piv["skill2"][i], dx) for i, (a, dx) in enumerate(zip(w, (0, -1, 1, 0)))]
    # E: crouch (Codex's frames), the burst hop with the arm flung up and back, landing, stance
    e3 = settle(pose(225, bow_shift=(1, -1)), piv["skill2_e"][2], dy=-3)
    out["skill2_e"][2] = e3
    # R: lift, the crossbow at the shoulder with the near arm flung back, back down
    out["ult"][1] = settle(pose(225, bow_shift=(2, -4)), piv["ult"][1])
    for t in ("skill2", "skill2_e", "ult"):
        for f in out[t]:
            assert not f[82:, :, 3].any(), t
    return out


def save(out):
    for t, frames in out.items():
        cols, rows = LAYOUT[t]
        atlas = np.zeros((rows * CH, cols * CW, 4), np.uint8)
        for i, f in enumerate(frames):
            atlas[(i // cols) * CH:(i // cols + 1) * CH, (i % cols) * CW:(i % cols + 1) * CW] = f
        Image.fromarray(np.repeat(np.repeat(atlas, 8, 0), 8, 1)).save(lp(os.path.join(OUT, f"twitch_{t}.png")))
    with open(lp(os.path.join(OUT, "twitch_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(CELLS, f, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write 1x atlases here instead of the strips")
    a = ap.parse_args()
    out = build()
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for t, frames in out.items():
            cols, rows = LAYOUT[t]
            atlas = np.zeros((rows * CH, cols * CW, 4), np.uint8)
            for i, f in enumerate(frames):
                atlas[(i // cols) * CH:(i // cols + 1) * CH, (i % cols) * CW:(i % cols + 1) * CW] = f
            Image.fromarray(atlas).save(os.path.join(a.review, f"twitch_{t}_1x.png"))
        return
    save(out)


if __name__ == "__main__":
    main()
