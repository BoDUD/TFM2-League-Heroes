#!/usr/bin/env python3
"""Sona's action strips: Codex's delivery (assets/source/sona/codex_strips) with the reaching arms redrawn as short sleeves.

    python tools/art/fix_sona_strips.py [--check] [--review OUT.png]

Codex built every frame from the design's own pixels (codex_strips/HANDOFF.md: the head, the body, the Etwahl and its
ribbons moved as layers) and drew the arms that leave the strings itself, out to the hands of League's adult pose
(manifest.json hand_targets: Q's reach 16 squares from the shoulder, wider than her body): long two-square sticks.
The user: "手臂异常问题你不修复吗 还是看起来怪啊". At chibi size the pack's heroes reach 6-9 squares (Lux, LeBlanc,
Morgana), with thick sleeves and small hands. So every reaching arm (ARMS: attack 2-5, the Power Chord 2-5, Q 2-5,
W 2-5, R 2-6) is drawn again:
  - Codex's arm goes: in each frame the head, the body and the Etwahl are the design moved by the manifest's head and
    instrument translations (the Etwahl's front end one row up or down where the manifest tilts it); a square none of
    those layers explains, in a band round the line from the shoulder to Codex's hand, is its arm - it takes the layer
    behind it (the Etwahl or the body), or nothing;
  - the new arm is the design's own far arm (sleeve, gold cuff, hand and their outline, cut along the outline) turned
    about the shoulder by RotSprite (rig_nocturne.py's), mirrored for the near arm: ANGLES gives each arm's direction
    in degrees above the level, outward (the design's arm hangs 39 degrees below it toward the strings), from League's
    pose - the gestures kept small and the arm its own six squares, so the silhouette stays the compact chibi one;
    a first try drew new sleeves along League's reach (Q's hands 16 squares out) and read as planks;
  - layers: the twin tails behind the arm (League's tails stream behind her), the face never covered.
Everything else is Codex's, square for square. Writes assets/source/native/sona_<tag>.png (8x) for every tag and
sona_cells.json (Codex's, the standing points native_pose.py measured). --check compares with the committed files.
"""
import argparse
import json
import math
import os
import shutil

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "sona", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(OUT, "sona_native.png")
Z = 8
TAGS = ["idle", "run", "attack", "attack_p", "skill", "skill2", "ult", "hit", "dead"]

O = (0x10, 0x10, 0x20)          # outline
DARK = (0x18, 0x3F, 0x9E)       # the sleeve's underside
MID = (0x22, 0x5C, 0xD4)        # the sleeve
LIGHT = (0x33, 0x8E, 0xF1)      # its lit edge
GOLD = (0xFF, 0xD0, 0x62)       # the cuff
GOLD_D = (0xD9, 0x9A, 0x35)
SKIN = (0xFF, 0xD4, 0xB1)
SKIN_D = (0xE7, 0x9F, 0x8D)
SHOULDER = {"near": (58, 82), "far": (68, 82)}     # the design's sleeve tops beside the collar
REST = {"near": (55, 61, 82, 86), "far": (66, 74, 82, 86)}   # the design's resting sleeve + hand: x0, x1, y0, y1
FACE = (59, 69, 68, 79)                           # x0, x1, y0, y1 on the design: never under an arm
# each moving arm's direction in degrees above the level, outward (League's pose, kept small), per (tag, frame)
ANGLES = {
    ("attack", 2): {"far": -15}, ("attack", 3): {"far": 0}, ("attack", 4): {"far": 10}, ("attack", 5): {"far": -20},
    ("attack_p", 2): {"far": 40}, ("attack_p", 3): {"far": 70}, ("attack_p", 4): {"far": -30},
    ("attack_p", 5): {"far": 5},
    ("skill", 2): {"near": -10, "far": -10}, ("skill", 3): {"near": 20, "far": 20},
    ("skill", 4): {"near": 30, "far": 30}, ("skill", 5): {"near": -10, "far": -10},
    ("skill2", 2): {"far": 45}, ("skill2", 3): {"far": 70}, ("skill2", 4): {"far": 70}, ("skill2", 5): {"far": 20},
    ("ult", 2): {"near": 60, "far": 60}, ("ult", 3): {"near": 35, "far": 35}, ("ult", 4): {"near": 40, "far": 40},
    ("ult", 5): {"near": 35, "far": 35}, ("ult", 6): {"near": 60, "far": 60},
}
REST_DEG = math.degrees(math.atan2(4, 5))      # the design's far arm: shoulder (68, 82) to hand (73, 86)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def at1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def head_mask():
    """The head pasted into every frame (strips_pack_so.py's head_rows): rows 60-79 of the design minus the collar."""
    m = np.zeros((128, 128), bool)
    m[60:77] = True
    m[77, :] = True
    m[77, 57:62] = False
    m[78, :] = True
    m[78, 56:62] = False
    m[79, :57] = True
    m[79, 62:68] = True
    m[79, 70:] = True
    return m


def instrument_mask(design, man):
    """The Etwahl and its ribbons on the design: what Codex's R frame 4 shows above the head, moved back."""
    fr = man["animations"]["ult"]["frames"][3]
    x, y, w, h = fr["cell_rect_1x"]
    sheet = at1x(os.path.join(SRC, "sona_ult.png"))
    cell = sheet[y:y + h, x:x + w]
    ix, iy = fr["instrument_translation_1x"]
    m = np.zeros((128, 128), bool)
    top = fr["head_bbox_1x"][1]                      # everything above the head's box is the flying Etwahl
    ys, xs = np.nonzero(cell[:top, :, 3])
    dy, dx = ys - iy, xs - ix
    ok = (dy >= 0) & (dy < 128) & (dx >= 0) & (dx < 128)
    for yy, xx, py, px in zip(dy[ok], dx[ok], ys[ok], xs[ok]):
        if design[yy, xx, 3] and tuple(design[yy, xx, :3]) == tuple(cell[py, px, :3]):
            m[yy, xx] = True
    return m


def layer_at(design, mask, dx, dy, shape):
    """The design's pixels in `mask`, moved by (dx, dy), on a cell of `shape`."""
    out = np.zeros(shape + (4,), np.uint8)
    ys, xs = np.nonzero(mask & (design[..., 3] > 0))
    cy, cx = ys + dy, xs + dx
    ok = (cy >= 0) & (cy < shape[0]) & (cx >= 0) & (cx < shape[1])
    out[cy[ok], cx[ok]] = design[ys[ok], xs[ok]]
    return out


def arm_sprite(design):
    """The design's far arm: sleeve, cuff, hand and their outline (rows 82-87, columns 67-74, not the collar), and the
    shoulder (68, 82) in it."""
    m = np.zeros((128, 128), bool)
    m[82:87, 68:75] = True
    m[84:87, 67] = True
    m[87, 72:74] = True
    m &= design[..., 3] > 0
    ys, xs = np.nonzero(m)
    y0, x0 = ys.min(), xs.min()
    spr = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
    spr[ys - y0, xs - x0] = design[ys, xs]
    return spr, (SHOULDER["far"][0] - x0, SHOULDER["far"][1] - y0)


def scale2x(s):
    """EPX / Scale2x (rig_nocturne.py's)."""
    key = (s[..., 0].astype(np.int64) << 24) | (s[..., 1].astype(np.int64) << 16) |           (s[..., 2].astype(np.int64) << 8) | s[..., 3].astype(np.int64)
    p = np.pad(key, 1, mode="edge")
    A, Bv, C, D = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]
    pk = np.pad(s, ((1, 1), (1, 1), (0, 0)), mode="edge")
    up, right, left, down = pk[:-2, 1:-1], pk[1:-1, 2:], pk[1:-1, :-2], pk[2:, 1:-1]
    h, w = s.shape[:2]
    out = np.zeros((h * 2, w * 2, 4), np.uint8)
    out[0::2, 0::2] = np.where(((C == A) & (C != D) & (A != Bv))[..., None], up, s)
    out[0::2, 1::2] = np.where(((A == Bv) & (A != C) & (Bv != D))[..., None], right, s)
    out[1::2, 0::2] = np.where(((D == C) & (D != Bv) & (C != A))[..., None], left, s)
    out[1::2, 1::2] = np.where(((Bv == D) & (Bv != A) & (D != C))[..., None], down, s)
    return out


def rotsprite(s, j, deg):
    """RotSprite about the joint, + counter-clockwise on screen (rig_nocturne.py's)."""
    big = scale2x(scale2x(scale2x(s)))
    h, w = s.shape[:2]
    r = int(np.ceil(np.hypot(max(j[0], w - j[0]), max(j[1], h - j[1])))) + 2
    t = np.radians(deg)
    oy, ox = np.mgrid[-r:r + 1, -r:r + 1]
    sx = np.cos(t) * ox - np.sin(t) * oy
    sy = np.sin(t) * ox + np.cos(t) * oy
    bx = np.floor((sx + j[0] + 0.5) * 8).astype(int)
    by = np.floor((sy + j[1] + 0.5) * 8).astype(int)
    ok = (bx >= 0) & (bx < w * 8) & (by >= 0) & (by < h * 8)
    out = np.zeros((2 * r + 1, 2 * r + 1, 4), np.uint8)
    out[ok] = big[by[ok], bx[ok]]
    return out, (r, r)


def fix_frame(cell, design, imask, tr, itr, tilt, hands, codex_hands, arm):
    h, w = cell.shape[:2]
    hm = head_mask()
    rest = np.zeros((128, 128), bool)
    for side in hands:
        x0, x1, y0, y1 = REST[side]
        rest[y0:y1 + 1, x0:x1 + 1] = True
    body = (design[..., 3] > 0) & ~imask & ~hm & ~rest
    lay_body = layer_at(design, body, tr[0], tr[1], (h, w))
    lay_head = layer_at(design, hm, tr[0], tr[1], (h, w))
    lay_instr = layer_at(design, imask, itr[0], itr[1], (h, w))
    alts = [lay_instr]
    if tilt:                                  # the front end tipped a row: explain both ways
        alts += [layer_at(design, imask, itr[0], itr[1] + d, (h, w)) for d in (-1, 1)]
    out = cell.copy()

    def explained(x, y):
        c = tuple(int(v) for v in cell[y, x])
        return any(tuple(int(v) for v in lay[y, x]) == c and lay[y, x, 3] for lay in [lay_body, lay_head] + alts)

    # Codex's arms: unexplained squares in a band round its arm lines
    for side in hands:
        sx, sy = SHOULDER[side][0] + tr[0] + 0.5, SHOULDER[side][1] + tr[1] + 0.5
        tx, ty = codex_hands[0 if side == "near" else 1]
        tx, ty = tx + 0.5, ty + 0.5
        L = math.hypot(tx - sx, ty - sy)
        if L < 1:
            continue
        ux, uy = (tx - sx) / L, (ty - sy) / L
        nx, ny = -uy, ux
        for y in range(h):
            for x in range(w):
                if not cell[y, x, 3] or lay_head[y, x, 3]:
                    continue
                vx, vy = x + 0.5 - sx, y + 0.5 - sy
                a, b = vx * ux + vy * uy, vx * nx + vy * ny
                if not (0.5 < a < L + 3.0 and abs(b) <= 4.0) or explained(x, y):
                    continue
                behind = lay_instr if lay_instr[y, x, 3] else lay_body
                out[y, x] = behind[y, x] if behind[y, x, 3] else 0
    # the new arms, the tails behind them, the face in front of everything
    face = np.zeros((h, w), bool)
    fx0, fx1, fy0, fy1 = FACE
    face[max(0, fy0 + tr[1]):max(0, fy1 + tr[1] + 1), max(0, fx0 + tr[0]):max(0, fx1 + tr[0] + 1)] = True
    ys, xs = np.nonzero(lay_head[..., 3])
    out[ys, xs] = lay_head[ys, xs]
    spr, joint = arm
    for side, deg in hands.items():
        if side == "far":
            turned, j = rotsprite(spr, joint, deg + REST_DEG)
        else:                                   # the near arm: the far one mirrored, turned the other way
            mir = spr[:, ::-1].copy()
            turned, j = rotsprite(mir, (spr.shape[1] - 1 - joint[0], joint[1]), -(deg + REST_DEG))
        S = (SHOULDER[side][0] + tr[0], SHOULDER[side][1] + tr[1])
        ys, xs = np.nonzero(turned[..., 3])
        cy, cx = ys + S[1] - j[1], xs + S[0] - j[0]
        for y, x, py, px in zip(cy, cx, ys, xs):
            if 0 <= x < w and 0 <= y < h and not face[y, x]:
                out[y, x] = turned[py, px]
    return out


def build():
    design = at1x(DESIGN)
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    imask = instrument_mask(design, man)
    arm = arm_sprite(design)
    outs = {}
    for tag in TAGS:
        sheet = at1x(os.path.join(SRC, f"sona_{tag}.png"))
        res = sheet.copy()
        for k, fr in enumerate(man["animations"][tag]["frames"], 1):
            hands = ANGLES.get((tag, k))
            if not hands:
                continue
            x, y, w, h = fr["cell_rect_1x"]
            res[y:y + h, x:x + w] = fix_frame(sheet[y:y + h, x:x + w], design, imask,
                                              fr["head_translation_from_design_1x"], fr["instrument_translation_1x"],
                                              fr["instrument_right_end_tilt_rows"], hands, fr["hand_targets_cell_1x"],
                                              arm)
        outs[tag] = res
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="Codex's frames over the fixed ones for every redrawn frame, 5x")
    a = ap.parse_args()
    outs = build()
    if a.check:
        bad = [t for t, im in outs.items() if not np.array_equal(
            np.asarray(Image.open(lp(os.path.join(OUT, f"sona_{t}.png"))).convert("RGBA")),
            np.repeat(np.repeat(im, Z, 0), Z, 1))]
        print("identical" if not bad else f"DIFFERENT: {bad}")
        return
    for t, im in outs.items():
        Image.fromarray(np.repeat(np.repeat(im, Z, 0), Z, 1)).save(lp(os.path.join(OUT, f"sona_{t}.png")))
    shutil.copyfile(lp(os.path.join(SRC, "sona_cells.json")), lp(os.path.join(OUT, "sona_cells.json")))
    print("written", ", ".join(f"sona_{t}.png" for t in outs), "and sona_cells.json")
    if a.review:
        man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
        keys = sorted(ANGLES, key=lambda q: (TAGS.index(q[0]), q[1]))
        s, cw, ch = 4, 76, 52
        img = Image.new("RGBA", (len(keys) * cw * s, 2 * ch * s + 8), (118, 126, 86, 255))
        for i, (tag, k) in enumerate(keys):
            fr = man["animations"][tag]["frames"][k - 1]
            x, y, w, h = fr["cell_rect_1x"]
            for j, src in enumerate((at1x(os.path.join(SRC, f"sona_{tag}.png")), outs[tag])):
                c = src[y:y + h, x:x + w][24:24 + ch, 22:22 + cw]
                img.alpha_composite(Image.fromarray(c).resize((cw * s, ch * s), Image.NEAREST),
                                    (i * cw * s, j * (ch * s + 8)))
        img.convert("RGB").save(a.review)
        print("review", a.review, img.size)


if __name__ == "__main__":
    main()
