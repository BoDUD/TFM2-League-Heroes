#!/usr/bin/env python3
"""Nautilus's action strips from Codex's side-on redraw (step 2 again: tools/art/pack_nautilus_strips2.py,
MODEL_STRIPS2.md; delivered 2026-10-11 as nautilus_strips_pack_done.zip, kept in assets/source/nautilus/codex_strips2:
the 1x strips, nautilus_cells.json, manifest, HANDOFF; the raw generations stay in the user's Codex outputs).

    python tools/art/fix_nautilus_strips2.py [--check]

The user: 「完成泰坦吧 有问题的地方你帮我修复 做到完美版了再喊我review」. Codex's strips are side-on like the pack's other
heroes and oppi's sprites (the body and the helmet turned to the right, a crossing run, the anchor carried and swung
whole); what is fixed here:
  1. attack and skill: the bronze one step brighter than every other strip (#FDCC31 light, #F94102 mid-dark): yellow ->
     #FAAC2A, orange-red -> #A84217, #A84217 -> #8C3815, except the eyes (red #E4221F and what touches it);
  2. skill: single red squares Codex left on the body (knee guards, shoulders, boots) - a red square touching the bronze
     and no anchor grey, not one of the eyes - become #A84217;
  3. ult 3 (Codex's body curled into a ball) is skill 3 (the anchor drawn back behind his head); ult 5-6 (shrunk into
     a ball, the anchor flattened under him) are the attack's lunge (attack 4: the anchor out in front at knee height);
     ult 7 (the anchor overlapping his body) is the attack's recovery (attack 5) - each with its own standing point;
  4. dead 2-8: Codex drew another anchor (a ring on top, a thin stock, small flukes) standing beside him; it goes
     (every square left of a per-row boundary, B) and the anchor he carries everywhere else (attack 5's, cut above the
     fist) stands on its crown in its place, behind him, the outline closed (rigkit.finish).
  5. the anchor carried on his back: the shank's last stretch, hidden behind the helmet and the shoulder plate (「武器没拿在
     手里 看起来像是插在脑袋里了？」), drawn on into the near fist (GRIP), frames whose shank misses the fist mended from
     one that holds it (GRIP_FROM).
The idle is side-on too (the user: 「待机图也改成侧面的吧 不然太奇怪了」, after the front-on design idle beside the side-on
actions): W+E's first frame, breathing (the body above the hip band sinks a row over the legs). Writes assets/source/native/nautilus_<tag>.png (8x) and nautilus_cells.json; then
python tools/art/import_native.py --hero nautilus.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import rig_nautilus as RN  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nautilus", "codex_strips2")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
TAGS = ["idle", "run", "attack", "skill", "skill_pull", "skill2", "ult", "hit", "dead"]
Z = 8
D = K.Design(RN.DESIGN)
L = D.letters()
INV = {c: k for k, c in L.items()}
OUT = tuple(int(v) for v in D.outline)
BRONZE, GREY = set("tpkjhmuo"), set("nsv")


def cols_of(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def cell(k, n, cw, ch):
    c = cols_of(n)
    return slice((k // c) * ch, (k // c + 1) * ch), slice((k % c) * cw, (k % c + 1) * cw)


def is_(a, ch):
    return np.all(a[..., :3] == L[ch], -1) & (a[..., 3] > 0)


def near(m):
    out = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def bronze_down(a):
    """1: u -> t, m -> k, k -> j outside the eyes (red squares and what touches them)."""
    eyes = near(is_(a, "l"))
    u, m, k = is_(a, "u") & ~eyes, is_(a, "m") & ~eyes, is_(a, "k")
    a[k, :3] = L["j"]
    a[m, :3] = L["k"]
    a[u, :3] = L["t"]


def red_specks(f):
    """2: red squares on the body (touching bronze, no grey) that are not the eyes -> k. The eyes: the biggest red
    piece in the face rows (60-82) and a piece beside it on the right (the far eye) within 8 columns."""
    lm = is_(f, "l")
    lab, n = ndimage.label(lm, np.ones((3, 3)))
    face = [(int((lab == i).sum()), i) for i in range(1, n + 1) if 60 <= np.nonzero(lab == i)[0].min() <= 82]
    keep = set()
    if face:
        eye = max(face)[1]
        ey, ex = np.nonzero(lab == eye)
        keep.add(eye)
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            if abs(ys.min() - ey.min()) <= 2 and 0 < xs.min() - ex.max() <= 8:
                keep.add(i)
    for y, x in zip(*np.nonzero(lm)):
        if lab[y, x] in keep:
            continue
        nb = {INV.get(tuple(int(v) for v in f[yy, xx, :3])) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
              if (yy, xx) != (y, x) and f[yy, xx, 3]}
        if nb & BRONZE and not nb & GREY:
            f[y, x, :3] = L["k"]


def grip(f, B, F, t0=0.4, half=1.0):
    """5: the shank from the band B on to the fist's top F over the body, then the fist (its grey piece and the squares
    round it) back on top."""
    out = f.copy()
    (by, bx), (fy, fx) = B, F
    ln = math.hypot(fy - by, fx - bx)
    uy, ux = (fy - by) / ln, (fx - bx) / ln
    grey = is_(f, "n") | is_(f, "s") | is_(f, "v")
    lab, _ = ndimage.label(grey)
    fid = lab[int(round(fy)) + 2, int(round(fx))]
    fist = (lab == fid) if fid else np.zeros_like(grey)
    ring = ndimage.binary_dilation(fist, np.ones((3, 3))) & ~fist & (f[..., 3] > 0)
    red = is_(f, "l") | is_(f, "m")
    for y in range(int(min(by, fy)) - 3, int(max(by, fy)) + 4):
        for x in range(int(min(bx, fx)) - 4, int(max(bx, fx)) + 5):
            py, px = y + 0.5 - by, x + 0.5 - bx
            t = (py * uy + px * ux) / ln
            if t < t0 or t > 1.0 or (red[y, x] and t < 0.5):
                continue
            d = py * ux - px * uy
            if abs(d) <= half:
                out[y, x] = (*L["n" if d > 0.3 else "f"], 255)
            elif abs(d) <= half + 1.0:
                out[y, x] = (*L["0"], 255)
    out[fist] = f[fist]
    out[ring] = f[ring]
    return out


def bounds(spec):
    return {r: c for r0, r1, c in spec for r in range(r0, r1 + 1)}


# 4: per death frame, the columns left of which every square is Codex's other anchor (rows: first, last, column)
DEAD_B = {2: bounds([(0, 68, 51), (69, 70, 53), (71, 71, 55), (72, 72, 54), (73, 127, 53)]),
          3: bounds([(0, 81, 59), (82, 127, 60)]),
          4: bounds([(0, 127, 60)]),
          5: bounds([(0, 73, 70), (74, 77, 69), (78, 92, 66), (93, 127, 73)]),
          6: bounds([(0, 73, 68), (74, 88, 65), (89, 92, 66), (93, 93, 70), (94, 94, 71), (95, 95, 72),
                     (96, 97, 73), (98, 127, 74)]),
          7: bounds([(0, 74, 59), (75, 79, 56), (80, 80, 57), (81, 88, 56), (89, 92, 57), (93, 94, 59), (95, 95, 61),
                     (96, 96, 62), (97, 127, 63)])}
DEAD_B[8] = DEAD_B[7]
DEAD_LEFT = {2: 23, 3: 34, 4: 28, 5: 49, 6: 47, 7: 42, 8: 42}   # the new anchor's left column (its crown on the soles)
ANCHOR_BOX = (40, 58, 28, 60)                                   # attack 5: rows, columns of the anchor above the fist
# 3: ult frames taken from other strips (ult frame <- (tag, frame)), 1-based
# 5: the anchor on his back looked stuck in his helmet (the user: 「武器没拿在手里 看起来像是插在脑袋里了？」): Codex's shank
# points at the near fist but its last stretch hid behind the helmet and the shoulder plate. Drawn on over them - from the
# red band B on to the fist's top F (rows, columns), the shank's dark core, a grey edge, the outline - and the fist put
# back over it: he holds the anchor over his shoulder, League's carry. Frames where the shank does not point at the
# fist take a mended frame instead (GRIP_FROM).
GRIP = {("run", 1): ((59, 51), (78, 57.1)), ("run", 2): ((58.5, 50.5), (77, 55.8)), ("run", 3): ((58, 51), (78, 55.5)),
        ("run", 4): ((59.2, 52.5), (77, 58.0)), ("run", 5): ((60.5, 52.5), (79, 58.4)),
        ("run", 6): ((58.9, 54.7), (77, 58.2)), ("run", 7): ((59.5, 49.5), (76, 55.1)),
        ("run", 8): ((56.5, 53.5), (75, 58.2)), ("skill2", 1): ((63, 52), (80, 58.9)),
        ("skill2", 5): ((63, 52), (80, 60.4)), ("skill2", 6): ((60, 50), (80, 58.6)),
        ("hit", 2): ((56, 49.3), (78, 58.6)), ("ult", 8): ((62.1, 54.3), (76, 61.2))}
# (tag, frame) <- the mended W+E stance (the idle's), or the mended hit 2 a column back
GRIP_FROM = {("attack", 1): ("skill2", 1, 0), ("attack", 6): ("skill2", 1, 0), ("skill_pull", 4): ("skill2", 1, 0),
             ("ult", 1): ("skill2", 1, 0), ("hit", 1): ("hit", 2, -1)}
IDLE_BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
IDLE_CUT = 86                                                   # the last row that sinks (the hip band's)
ULT_FROM = {3: ("skill", 3), 5: ("attack", 4), 6: ("attack", 4), 7: ("attack", 5)}


def build():
    with open(os.path.join(SRC, "nautilus_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    strips = {t: np.asarray(Image.open(os.path.join(SRC, f"nautilus_{t}_1x.png")).convert("RGBA")).copy()
              for t in TAGS if t != "idle"}
    n = {t: len(cells["tags"][t]) for t in TAGS}
    for t in ("attack", "skill"):
        bronze_down(strips[t])
    for k in range(n["skill"]):
        red_specks(strips["skill"][cell(k, n["skill"], cw, ch)])
    for dst, (tag, src) in ULT_FROM.items():
        strips["ult"][cell(dst - 1, n["ult"], cw, ch)] = strips[tag][cell(src - 1, n[tag], cw, ch)]
        cells["tags"]["ult"][dst - 1]["pivot"] = list(cells["tags"][tag][src - 1]["pivot"])
    f5 = strips["attack"][cell(4, n["attack"], cw, ch)]
    r0, r1, c0, c1 = ANCHOR_BOX
    piece = np.zeros_like(f5)
    piece[r0:r1, c0:c1] = f5[r0:r1, c0:c1]
    ys, xs = np.nonzero(piece[..., 3] > 0)
    anchor = piece[ys.min():ys.max() + 1, xs.min():xs.max() + 1][::-1].copy()     # on its crown
    for (tag, k), (B, F) in GRIP.items():
        sl = cell(k - 1, n[tag], cw, ch)
        strips[tag][sl] = grip(strips[tag][sl], B, F)
    for (tag, k), (src, j, dx) in GRIP_FROM.items():
        piece = strips[src][cell(j - 1, n[src], cw, ch)]
        strips[tag][cell(k - 1, n[tag], cw, ch)] = K.shifted(piece, dx, 0)
        cells["tags"][tag][k - 1]["pivot"] = list(cells["tags"][src][j - 1]["pivot"])
    dead = strips["dead"]
    for k in range(2, 9):
        sl = cell(k - 1, n["dead"], cw, ch)
        f = dead[sl].copy()
        for r in range(ch):
            f[r, :DEAD_B[k].get(r, 0)] = 0
        c = np.zeros_like(f)
        K.put(c, anchor, DEAD_LEFT[k], RN.PIVOT[1] + 11 - anchor.shape[0])
        K.put(c, f, 0, 0)
        c[RN.PIVOT[1] + 12:] = 0
        dead[sl] = K.finish(c, OUT, RN.PIVOT[1] + 11)
    # the idle: side-on like every action (the user: 「待机图也改成侧面的吧 不然太奇怪了」) - W+E's first frame (Codex's
    # braced stance, both boots flat, the anchor on his back), breathing: everything above the crotch (rows to
    # IDLE_CUT) sinks a row over the legs in frames 3-6
    for t in cells["tags"].values():
        for fr in t:
            fr.pop("head", None)
    stand = strips["skill2"][cell(0, n["skill2"], cw, ch)]
    pivot = list(cells["tags"]["skill2"][0]["pivot"])
    cells["tags"]["idle"] = [{"pivot": pivot, "ms": m} for m in RN.MS["idle"]]
    cols, rows = K.layout(len(IDLE_BREATH))
    sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, b in enumerate(IDLE_BREATH):
        fr = stand.copy()
        if b:
            up = np.zeros_like(stand)
            up[:IDLE_CUT + 1] = stand[:IDLE_CUT + 1]
            fr[:IDLE_CUT + 1] = 0
            K.put(fr, up, 0, b)
            fr = K.finish(fr, OUT, RN.PIVOT[1] + 11)
        sheet[cell(k, len(IDLE_BREATH), cw, ch)] = fr
    strips["idle"] = sheet
    return strips, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    a = ap.parse_args()
    strips, cells = build()
    bad = []
    for t in TAGS:
        big = np.repeat(np.repeat(strips[t], Z, 0), Z, 1)
        path = os.path.join(NATIVE, f"nautilus_{t}.png")
        if a.check:
            if not np.array_equal(np.asarray(Image.open(path).convert("RGBA")), big):
                bad.append(t)
        else:
            Image.fromarray(big).save(path)
    path = os.path.join(NATIVE, "nautilus_cells.json")
    text = json.dumps(cells, indent=1) + "\n"
    if a.check:
        with open(path, encoding="utf-8") as f:
            if f.read() != text:
                bad.append("cells")
        print("differs:", bad or "nothing")
        sys.exit(1 if bad else 0)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", ", ".join(TAGS))


if __name__ == "__main__":
    main()
