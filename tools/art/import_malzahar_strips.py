#!/usr/bin/env python3
"""league_malzahar's action frames from Codex's step-2 fine drafts (assets/source/malzahar/codex_strips) on the design's
grid (PPU 2.2: one square = one dense pixel), the way tools/art/design_malzahar.py made the design.

    python tools/art/import_malzahar_strips.py [--review DIR]

Codex drew the 35 frames as fine drafts (~5-px squares) on the pack's canvas (tools/art/pack_malzahar_strips.py:
1536 x 1024, a design square 10 px, his lowest point on y 960, his middle on x 700), each a little bigger or smaller
than the design and drifting (its HANDOFF). So per frame:
  * the head: the four diamond marks found (white squares next to their blue rims; the eyes have none) and the frame's
    size against the design's head by normalised cross-correlation over scales (HEADS, measured 2026-10-14 with
    %TEMP%/../scratchpad headmatch.py: the design draft's head round its marks on the pack canvas, 0.85-1.55);
  * the size, one per action (SIZES): Codex drew each action's frames with the one before attached, so they agree
    within an action far better than single measures do - the geometric mean of the action's median head scale and its
    median body (marks to the lowest point against the design's), the head alone where the pose bends the body (the
    glide leans, the channel crouches) and for the death;
  * the cut (design_malzahar's own steps): the frame pixelated to the design's grid in squares of 10 x size px through
    the marks' centre (each square the mean snapped to the design's colours, outline where dark), the glow round the
    marks and the dagger's gold / sheath brightness-wins, every square snapped to the design's palette (no colour
    flicker between frames);
  * placed: the marks' centre where Codex put it relative to the design (PLACE moves a frame: Codex's drift), the glide
    held over the standing point, the death's lying frames on the ground row;
  * one face (memory one-face-all-frames): the design's own marks, eyes and face cloth pasted at the frame's marks
    (FACE_SKIP: the frames whose head is tilted keep their own eyes, the marks still pasted);
  * the outline closed (strips.complete_outline), one-square cracks and notches closed, one calm pass (design_malzahar.calm's
    rule: a lit square never turns outline).
idle = the design floating (the whole figure bobbing a square at a time), hit = the design 2 / 1 squares back with a
white flash on the first frame.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_malzahar as D  # noqa: E402
import pixel_down as PD  # noqa: E402
sys.path.insert(0, D.SKILL)
import strips as G  # noqa: E402

ROOT = D.ROOT
SRC = D.SRC
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
K = D.K
PX = 10.0                          # pack canvas px a design square at size 1 (pack_malzahar_strips.py PX)
REF = (756.0, 283.0)               # the design draft's marks centre on the pack canvas (design/malzahar_on_canvas.png)
COLS, ROWS = 160, 112              # the frame canvas (design squares)
DX, DY = 50, 22                    # the design's top-left square on the canvas
DESIGN_MARKS = (32, 8)             # the design's marks centre square (col, row): MARK_AT + 2
SOLE = DY + 76 + 6                 # the ground row: the design's boots hang 6 squares (2.7 game px) over it - he floats
PIV_C = DX + 26                    # the standing column (under the boots' middle, the pack's x 700)
TAGS = [("run", 6), ("attack", 5), ("skill", 5), ("skill2", 5), ("ult", 4), ("ult_loop", 4), ("dead", 6)]
# marks centre (pack canvas px) and head scale per frame (headmatch.py, NCC 0.70-0.89; the lying death frames' match
# is poor and their scale comes from the standing ones), and the body: marks to the lowest point over the design's
HEADS = {
    "run_1": (868.9, 279.6, 1.11, 0.978), "run_2": (937.2, 280.6, 1.08, 0.962), "run_3": (916.3, 245.6, 1.09, 1.017),
    "run_4": (958.6, 260.0, 1.15, 1.009), "run_5": (1054.7, 260.2, 1.18, 1.015), "run_6": (1011.3, 269.3, 1.17, 0.991),
    "attack_1": (824.2, 227.3, 1.01, 1.068), "attack_2": (824.2, 226.3, 1.06, 1.005), "attack_3": (773.7, 249.4, 1.04, 0.998),
    "attack_4": (780.5, 249.6, 1.08, 1.091), "attack_5": (781.6, 253.2, 1.06, 1.077),
    "skill_1": (761.2, 162.1, 0.83, 1.105), "skill_2": (808.6, 153.9, 0.99, 1.167), "skill_3": (801.8, 158.5, 1.04, 1.187),
    "skill_4": (856.6, 236.4, 1.10, 1.059), "skill_5": (754.8, 229.0, 0.95, 1.073),
    "skill2_1": (762.9, 263.6, 0.96, 1.027), "skill2_2": (782.4, 229.5, 1.05, 1.070), "skill2_3": (779.2, 186.3, 1.13, 1.091),
    "skill2_4": (812.4, 243.5, 1.06, 1.025), "skill2_5": (767.6, 275.1, 1.01, 1.047),
    "ult_1": (823.7, 178.0, 1.10, 1.104), "ult_2": (752.0, 189.7, 0.98, 1.002), "ult_3": (778.9, 249.4, 1.03, 0.991),
    "ult_4": (778.9, 240.4, 1.05, 1.016),
    "ult_loop_1": (806.8, 331.3, 1.03, 0.887), "ult_loop_2": (826.5, 318.9, 1.06, 0.919), "ult_loop_3": (817.7, 372.0, 0.98, 0.852),
    "ult_loop_4": (827.1, 394.9, 0.99, 0.820),
    "dead_1": (645.4, 251.5, 0.82, 1.023), "dead_2": (793.6, 378.5, 1.16, 0.854), "dead_3": (860.9, 338.4, 0.98, 0.834),
    "dead_4": (697.0, 211.7, 0.82, 1.140), "dead_5": (1190.2, 610.2, 1.21, 0.287), "dead_6": (1291.0, 642.2, 1.41, 0.321),
}
HEAD_ONLY = {"run", "ult_loop", "dead"}
# frames whose head is tilted or lying: their own eyes stay (the design's marks still pasted where they are)
FACE_SKIP = {"dead_1", "dead_3", "dead_4", "dead_5", "dead_6"}
# the death: Codex's dead 4 straightens up again between the curl and the fall (its HANDOFF) and its dead 6 lies 15 %
# longer than dead 5 (drawn bigger) - both left out: dead 1-3, then dead 3 moved halfway down (the fall: the same
# drawing, a whole move), then dead 5 lying, held. Every death frame's body centred over the standing column.
DEAD_USE = [1, 2, 3, 3, 5]
DEAD_MS = [100, 120, 140, 80, 500]
DEAD_FALL = 3                      # the index (0-based) of the in-between: dead 3 moved down half the way to the ground
# the channel: Codex drew it 9 squares lower and 3 right of the start's last frame and bobbing 5 squares inside the
# loop, and its fourth frame threw the cloth tail up over the hood (its HANDOFF): the loop is frames 1, 2, 3, 2 with
# the marks held where ult 4 has them, LOOP_DY lower (he sinks into the crouch)
LOOP_USE = [1, 2, 3, 2]
LOOP_DY = 4
# per-frame moves (squares) over Codex's placement: (dx, dy) - Codex drew attack 1 (the wind-up) 7.6 squares right of
# the idle and attack 2 back over it (a jump each way), ult 1 (gathering) 4.4 right
PLACE = {"attack_1": (-5, 0), "ult_1": (-3, 0)}
# the glide: Codex drew it drifting forward (the marks 11 to 30 squares ahead of the idle's, its hips 0 to 12): the marks
# held RUN_LEAN squares ahead of the idle's - Codex's lean (marks to hips 12-18 squares, mean 14.2) with the hips' mean
# over the standing point - and RUN_DY up, bobbing RUN_BOB (no sliding back and forth inside the loop)
RUN_LEAN = 8.8
RUN_DY = -1
RUN_BOB = [0, -1, -2, -2, -1, 0]


def design():
    return np.array(Image.open(D.OUT).convert("RGBA"))


def palette():
    d = design()
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(float)


def sizes():
    """One size per action (see the docstring)."""
    out = {}
    for tag, _ in TAGS:
        keys = [k for k in HEADS if k.rsplit("_", 1)[0] == tag]
        head = float(np.median([HEADS[k][2] for k in keys if not (tag == "dead" and int(k[-1]) in (1, 4, 5, 6))]))
        body = float(np.median([HEADS[k][3] for k in keys]))
        out[tag] = head if tag in HEAD_ONLY else float(np.sqrt(head * body))
    return out


def read(key):
    a = np.array(Image.open(os.path.join(CODEX, f"malzahar_{key}.png")).convert("RGBA"))
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def snap(d, pal):
    """Every drawn square to the nearest design colour (Lab); the outline stays the outline."""
    op = d[..., 3] > 0
    dark = op & (d[..., :3].astype(int).sum(-1) < 70)
    m = op & ~dark
    if m.any():
        L = PD._lab(d[m][:, :3].astype(float))
        j = ((L[:, None] - PD._lab(pal)[None]) ** 2).sum(-1).argmin(1)
        d[m, :3] = pal[j].round().astype(np.uint8)
    d[dark, :3] = K
    return d


def cut(a, s, marks, at, pal):
    """The frame `a` on the canvas: squares of PX x s px through the marks' centre, which lands at `at` (col, row:
    fractional, the square's corner at the integer part)."""
    c = PX * s
    k = 1.0 / c
    fc, fr = at[0] - np.floor(at[0]), at[1] - np.floor(at[1])
    pivot = (marks[0] - fc * c, marks[1] - fr * c)
    d, (nx0, ny0) = PD.pixelate(a, k, pivot, K, pal=pal)
    box = (int(marks[0] - 60 * s), int(marks[1] - 45 * s), int(marks[0] + 60 * s), int(marks[1] + 75 * s))
    d = D.dagger(a, D.glow(a, d, k, pivot, box), k, pivot)
    d = snap(d, pal)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    ys, xs = np.nonzero(d[..., 3] > 0)
    r = ys - ny0 + int(np.floor(at[1]))
    q = xs - nx0 + int(np.floor(at[0]))
    ok = (r >= 0) & (r < ROWS) & (q >= 0) & (q < COLS)
    can[r[ok], q[ok]] = d[ys[ok], xs[ok]]
    return can


# the design's face opening under the marks: brow line, both eyes, the face cloth (design rows 11-13, cols 27-35)
OPEN_ROWS, OPEN_COLS = (11, 14), (27, 36)
GLOW = [(245, 250, 251), (33, 145, 235)]       # the marks' and eyes' white and blue (the design's palette)


def face(can, mc, mr, eyes=True):
    """One face: Codex's own glow round the head cleared (its eyes and marks drawn a square off the design's would read
    as four eyes), then the design's marks (5 x 5 centred on (mc, mr)) and, where the head is upright, its face opening
    (brow, eyes, cloth) at the design's offsets. Tilted heads keep their own eyes: only the ring round the marks is
    cleared there."""
    d = design()
    dr, dc = mr - DESIGN_MARKS[1], mc - DESIGN_MARKS[0]
    clear = np.zeros(can.shape[:2], bool)
    if eyes:
        clear[mr - 3:mr + (OPEN_ROWS[1] - DESIGN_MARKS[1]) + 2, mc - 7:mc + 7] = True
    else:
        clear[mr - 3:mr + 4, mc - 3:mc + 4] = True
    rgb = can[..., :3].astype(int)
    glow = np.zeros(clear.shape, bool)
    for g in GLOW:
        glow |= (rgb == g).all(-1)
    # the marks' ring: any square there that is neither the hood's magenta nor the outline is Codex's rim (light blue,
    # lilac, its grey-violet mix)
    ring = np.zeros(clear.shape, bool)
    ring[mr - 3:mr + 4, mc - 3:mc + 4] = True
    ring[mr - 2:mr + 3, mc - 2:mc + 3] = False
    hood = (rgb[..., 0] >= 100) & (rgb[..., 1] * 10 < rgb[..., 0] * 3)
    outline = rgb.sum(-1) < 70
    bad = clear & (can[..., 3] > 0) & (glow | (ring & ~hood & ~outline))
    for y, x in zip(*np.nonzero(bad)):
        nb = can[y - 1:y + 2, x - 1:x + 2].reshape(-1, 4)
        nbad = bad[y - 1:y + 2, x - 1:x + 2].reshape(-1)
        ok = (nb[:, 3] > 0) & ~nbad
        if ok.any():
            cols, cnt = np.unique(nb[ok][:, :3], axis=0, return_counts=True)
            can[y, x, :3] = cols[cnt.argmax()]
    for r, row in enumerate(D.MARKS):
        for c, ch in enumerate(row):
            can[mr - 2 + r, mc - 2 + c, :3], can[mr - 2 + r, mc - 2 + c, 3] = D.FACE[ch], 255
    if eyes:
        for r in range(*OPEN_ROWS):
            for c in range(*OPEN_COLS):
                if d[r, c, 3] > 0:
                    can[r + dr, c + dc] = d[r, c]
    return can


def close_small(a, most=6):
    """Ground showing inside the figure (memory gap-check): enclosed clear pockets of `most` squares or fewer and
    one-square cracks between two drawn squares (left-right or up-down) become outline."""
    while True:
        op = a[..., 3] > 0
        lab, n = ndimage.label(~op)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        fill = np.zeros_like(op)
        for j in range(1, n + 1):
            if j not in border and (lab == j).sum() <= most:
                fill |= lab == j
        p = np.pad(op, 1)
        fill |= ~op & ((p[:-2, 1:-1] & p[2:, 1:-1]) | (p[1:-1, :-2] & p[1:-1, 2:]))
        if not fill.any():
            return a
        a[fill, :3] = K
        a[fill, 3] = 255


def pinholes(a, most=3):
    """Enclosed holes of at most `most` squares take the commonest colour round them (rig_kindred.pinholes: at 2.2 a
    game pixel they read as specks of ground; the design has four); the openings between an arm and the body stay."""
    op = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() > most:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
        a[m, :3] = cols[cnt.argmax()]
        a[m, 3] = 255
    return a


def finish(can, keep):
    can, _, _ = G.complete_outline(can, color=K)
    can = close_small(can)
    op = can[..., 3] > 0
    lit = op & (can[..., :3].astype(int).sum(-1) >= 70)
    e = PD._majority(can, op, keep | ~lit)
    grew = (e[..., :3].astype(int).sum(-1) < 70) & lit
    e[grew] = can[grew]
    return pinholes(e)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys = slice(max(0, dy), min(H, H + dy))
    xs = slice(max(0, dx), min(W, W + dx))
    out[ys, xs] = a[max(0, -dy):min(H, H - dy), max(0, -dx):min(W, W - dx)]
    return out


def frame(key, size, pal):
    mx, my, _, _ = HEADS[key]
    tag = key.rsplit("_", 1)[0]
    # where the marks go: Codex's place relative to the design's (its drift moved by PLACE)
    at_c = DX + DESIGN_MARKS[0] + 0.5 + (mx - REF[0]) / PX
    at_r = DY + DESIGN_MARKS[1] + 0.5 + (my - REF[1]) / PX
    if tag == "ult_loop":
        ux, uy = HEADS["ult_4"][:2]
        at_c = DX + DESIGN_MARKS[0] + 0.5 + (ux - REF[0]) / PX
        at_r = DY + DESIGN_MARKS[1] + 0.5 + (uy - REF[1]) / PX + LOOP_DY
    if tag == "run":
        k = int(key[-1]) - 1
        at_c = DX + DESIGN_MARKS[0] + 0.5 + RUN_LEAN
        at_r = DY + DESIGN_MARKS[1] + 0.5 + RUN_DY + RUN_BOB[k]
    pdx, pdy = PLACE.get(key, (0, 0))
    can = cut(read(key), size, (mx, my), (at_c + pdx, at_r + pdy), pal)
    mc, mr = int(np.floor(at_c + pdx)), int(np.floor(at_r + pdy))
    can = face(can, mc, mr, eyes=key not in FACE_SKIP)
    keep = np.zeros(can.shape[:2], bool)
    keep[mr - 3:mr + 7, mc - 6:mc + 5] = True
    can = finish(can, keep)
    if tag == "dead":
        ys, xs = np.nonzero(can[..., 3] > 0)
        dx = int(round(IDLE_CX - xs.mean()))
        dy = SOLE - int(ys.max()) if int(key[-1]) >= 5 else 0
        can = shift(can, dx, dy)
    return can


def idle_cx():
    d = design()
    ys, xs = np.nonzero(d[..., 3] > 0)
    return DX + float(xs.mean())


IDLE_CX = None


def on_canvas(dx=0, dy=0):
    d = pinholes(design())
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[DY + dy:DY + dy + d.shape[0], DX + dx:DX + dx + d.shape[1]] = d
    return can


# the idle: the design floating - the whole figure a square up and back down (no part moves alone)
IDLE = [(0, 160), (-1, 160), (-2, 200), (-1, 160)]


def idle_frames():
    return [(on_canvas(dy=dy), float(ms)) for dy, ms in IDLE]


def hit_frames():
    out = []
    for dx, flash, ms in ((-2, True, 90), (-1, False, 120)):
        a = on_canvas(dx=dx)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, float(ms)))
    return out


def frames():
    pal = palette()
    sz = sizes()
    print("sizes:", ", ".join(f"{t} {v:.3f}" for t, v in sz.items()))
    cells = json.load(open(os.path.join(CODEX, "cells.json"), encoding="utf-8"))
    ms = {}
    for f in cells["frames"]:
        ms[f["file"][len("malzahar_"):-4]] = f["ms"]
    global IDLE_CX
    IDLE_CX = idle_cx()
    out = {"idle": idle_frames()}
    for tag, n in TAGS:
        use = DEAD_USE if tag == "dead" else LOOP_USE if tag == "ult_loop" else range(1, n + 1)
        fr, made = [], {}
        for j, i in enumerate(use):
            key = f"{tag}_{i}"
            t = DEAD_MS[j] if tag == "dead" else ms[key]
            if key not in made:
                made[key] = frame(key, sz[tag], pal)
            f = made[key].copy()
            if tag == "dead" and j == DEAD_FALL:
                ys = np.nonzero((f[..., 3] > 0).any(1))[0]
                f = shift(f, 0, (SOLE - int(ys.max())) // 2)
            fr.append((f, float(t)))
        out[tag] = fr
    out["hit"] = hit_frames()
    return out


def review(acts, path, z=4):
    from PIL import ImageDraw
    tiles = [(f"{t}_{k + 1}", a) for t, fr in acts.items() for k, (a, _) in enumerate(fr)]
    W, H = COLS * z, ROWS * z
    per = 6
    rows = (len(tiles) + per - 1) // per
    big = Image.new("RGBA", (per * W, rows * (H + 14)), (150, 160, 150, 255))
    dr = ImageDraw.Draw(big)
    for n, (name, a) in enumerate(tiles):
        x, y = (n % per) * W, (n // per) * (H + 14)
        big.alpha_composite(Image.fromarray(a).resize((W, H), Image.NEAREST), (x, y + 14))
        dr.text((x + 4, y + 1), name, fill=(255, 255, 255, 255))
        dr.line([(x, y + 14 + (SOLE + 1) * z), (x + W, y + 14 + (SOLE + 1) * z)], fill=(0, 90, 255, 255))
        dr.line([(x + (PIV_C + 0.5) * z, y + 14 + (SOLE - 2) * z), (x + (PIV_C + 0.5) * z, y + 14 + (SOLE + 3) * z)],
                fill=(0, 90, 255, 255), width=2)
    big.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a contact sheet of every frame at 4x here")
    a = ap.parse_args()
    acts = frames()
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for tag, fr in acts.items():
        for k, (f, ms) in enumerate(fr):
            Image.fromarray(f).save(os.path.join(OUT, f"{tag}_{k + 1}.png"))
            meta.setdefault(tag, []).append(ms)
    with open(os.path.join(OUT, "frames.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"canvas": [COLS, ROWS], "standing": [PIV_C, SOLE], "ms": meta}, f, indent=1)
    if a.review:
        review(acts, a.review)
    print("frames:", ", ".join(f"{t} {len(f)}" for t, f in acts.items()))


if __name__ == "__main__":
    main()
