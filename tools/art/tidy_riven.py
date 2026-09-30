#!/usr/bin/env python3
"""Check Codex's ten Riven strips, tidy them and write them to the native strips.

    python tools/art/tidy_riven.py <Codex's delivery folder>     # riven_animation_pack/ of the 65-frame delivery
    python tools/art/tidy_riven.py --blade <Codex's second delivery>   # riven_fx2_complete/: the reforged sword

Codex drew the strips from the approved design (assets/source/riven/MODEL_STRIPS.md) on the reference cells
(96x96 game pixels, assets/source/native/riven_cells.json): every game pixel one flat 8x8 block, only the design's
27 colours, alpha 0 or 255, the design's head copied into every frame (two 2x2 eyes on one row), the last frame of
every action the design itself. That is checked here (the script stops on a failure), then two fixes:
  - one outline: the black just inside the outline turned into the material's own darkest shade, outline spurs
    and lone specks off (tools/art/tidy_codex18.py's one_outline, here design_riven.one_outline); the head Codex
    pasted (its manifest's head_origin and rotation, reference/head_master_1x.png) and the ring round it are left
    alone, so every frame keeps the design's head, and frames that are the design itself are not touched;
  - the run floated: its soles stood 3-5 rows over the feet line in all eight frames (League's run, which the
    references showed, plants a foot in four). The whole strip moves down RUN_DROP rows, which puts the soles of
    frames 4 and 7 on the line and keeps the head's one-row bob.
Writes assets/source/native/riven_<tag>.png (8x) and riven_idle.png (the design on the idle pivots, from the pack),
then run import_native.py --hero riven (EYES steadies idle and run on the eyes' green).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_riven as D  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["run", "attack", "skill", "q2", "q3", "skill2", "ult", "r_slash", "hit", "dead"]
EYES = [(0xFF, 0xFF, 0xFF), (0x16, 0x3A, 0x22), (0x3E, 0x8E, 0x48)]
FALL = {"dead": 2}              # rows a frame may reach under the feet line
RUN_DROP = 3
# --blade: the reforged sword (the user's option B) - each strip and the strip it is drawn over
BLADE = {"ult": "ult", "r_slash": "r_slash", "attack_r": "attack", "skill_r": "skill", "q2_r": "q2", "q3_r": "q3",
         "skill2_r": "skill2"}
BLADE_RUNE = (0x42, 0x6E, 0x3B)         # the broken blade's rune green, lit to #87D46A where the energy runs
BLADE_GREENS = {(0xF6, 0xEA, 0xDB), (0xC9, 0xEF, 0x9A), (0x87, 0xD4, 0x6A), (0x4B, 0xA8, 0x5A), (0x2D, 0x69, 0x40)}
ULT_BROKEN = 2                          # the ult's first frames keep the broken blade
# the user's pick after the first delivery ("开大时 刀没变大？" -> the mock "照示意图"): a big energy blade drawn under
# the frame along Codex's blade axis, wrapping the whole broken blade (League's R); half its width, how far it runs
# past the broken end (less where Codex shortened its tip, never out of the cell) and back toward the hilt
REFORGE_HALF = 6.5
REFORGE_TIP = 16
REFORGE_HILT = 22
RIM2, BODY2, INNER2, CORE2, HOT2 = ((0x2D, 0x69, 0x40), (0x4B, 0xA8, 0x5A), (0x87, 0xD4, 0x6A), (0xC9, 0xEF, 0x9A),
                                    (0xF6, 0xEA, 0xDB))


def reforge(c, axis, ext, keep):
    """The energy blade under one frame's squares (never over them, never on `keep`): along the axis from the
    broken end (x0, y0) in direction (ux, uy); it widens from the hilt over 4 squares, holds REFORGE_HALF and comes
    to a point over its last 9; a #2D6940 rim, #4BA85A inside it, #87D46A down the middle, a #C9EF9A line past the
    break that turns #F6EADB near the point."""
    x0, y0, ux, uy = axis[:4]
    n = float(np.hypot(ux, uy))
    ux, uy = ux / n, uy / n
    H, W = c.shape[:2]
    room = min((W - 1 - x0) / ux if ux > 0 else 1e9, x0 / -ux if ux < 0 else 1e9, y0 / -uy if uy < 0 else 1e9)
    e = min(REFORGE_TIP if ext >= 12 else ext, room - 1)
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = xx - x0, yy - y0
    s = dx * ux + dy * uy
    d = np.abs(-dx * uy + dy * ux)
    w = np.where(s < -REFORGE_HILT + 4, 2.5 + (s + REFORGE_HILT) * 0.75,
                 np.where(s > e - 9, REFORGE_HALF * np.clip((e - s) / 9.0, 0, None), REFORGE_HALF))
    inside = (s >= -REFORGE_HILT) & (s <= e) & (d <= w) & (c[..., 3] == 0) & ~keep
    out = c.copy()
    col = np.zeros((H, W, 3), np.uint8)
    col[:] = BODY2
    col[d < w * 0.5] = INNER2
    col[(d < 0.8) & (s > 0)] = CORE2
    col[(d < 0.8) & (s > max(e - 7, 0))] = HOT2
    col[d > w - 2.4] = BODY2
    col[d > w - 1.2] = RIM2
    out[inside, :3] = col[inside]
    out[inside, 3] = 255
    return out


def blocks(path):
    a = np.asarray(Image.open(D.lp(path)).convert("RGBA"))
    if a.shape[0] % Z or a.shape[1] % Z:
        sys.exit(f"{path}: not a multiple of {Z}")
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    if not np.isin(a[..., 3], [0, 255]).all():
        sys.exit(f"{path}: semi-transparent pixels")
    return b[:, 0, :, 0].copy()


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def colours(a):
    return {tuple(int(v) for v in p) for p in a[a[..., 3] > 0][:, :3]}


def head(shape, master, origin, rotation):
    """The head Codex pasted (its master's opaque squares at the frame's head_origin, turned clockwise by the
    frame's rotation) and the ring round it: left alone, so every frame keeps the design's head square for square."""
    hm = np.rot90(master, k=-(rotation // 90)) if rotation else master
    m = np.zeros(shape, bool)
    x, y = origin
    h, w = hm.shape[:2]
    m[y:y + h, x:x + w] = hm[..., 3] > 0
    grown = m.copy()
    for dy, dx in D.N8:
        grown |= D.shifted(m, dy, dx)
    return grown


def blade(folder):
    """--blade: the reforged sword drawn over the strips (Codex's second delivery). Checked against the strips it
    was drawn over (the delivery's reference/original_riven_<tag>.png, which must be ours for the strips that stay):
    only transparent squares filled and the blade's rune green lit, all in the effects' greens, nothing removed,
    nothing in the face box round the eyes, nothing under the feet line, the ult's broken-blade frames untouched.
    Then every reforged frame gets the big energy blade under it (reforge(), the user's pick of the mock), and the
    face and feet checks are made again. Writes assets/source/native/riven_<tag>.png and the `_r` tags into
    riven_cells.json (the rows of the strip they are drawn over)."""
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    with open(D.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        records = {k: v["records"] for k, v in json.load(f)["strips"].items()}
    cw, ch = cells["cell"][:2]
    for tag, base in BLADE.items():
        ref = np.asarray(Image.open(D.lp(os.path.join(folder, "reference", f"original_riven_{base}.png"))).convert("RGBA"))
        if tag != base and not (ref == blocks(os.path.join(SRC, f"riven_{base}.png"))).all():
            sys.exit(f"{tag}: reference/original_riven_{base}.png is not our riven_{base}.png")
        a = blocks(os.path.join(folder, "strips", f"riven_{tag}.png"))
        if a.shape != ref.shape:
            sys.exit(f"{tag}: {a.shape[1]}x{a.shape[0]}, not {ref.shape[1]}x{ref.shape[0]}")
        diff = np.any(a != ref, -1)
        if (diff & (a[..., 3] == 0)).any():
            sys.exit(f"{tag}: squares removed")
        lit = diff & (ref[..., 3] > 0)
        was = colours(ref[lit][None]) if lit.any() else set()
        if was - {BLADE_RUNE}:
            sys.exit(f"{tag}: squares other than the blade's rune green {BLADE_RUNE} recoloured: {sorted(was)}")
        now = colours(a[diff][None]) if diff.any() else set()
        if now - BLADE_GREENS:
            sys.exit(f"{tag}: colours outside the effects' greens: {sorted(now - BLADE_GREENS)}")
        rows = cells["tags"][base]
        cols = layout(len(rows))
        per = []
        for i, f in enumerate(rows):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            d = diff[y0:y0 + ch, x0:x0 + cw]
            c = ref[y0:y0 + ch, x0:x0 + cw]
            eye = np.zeros(d.shape, bool)
            for e in EYES[1:]:
                eye |= (c[..., 3] > 0) & np.all(c[..., :3] == np.array(e, np.uint8), -1)
            ys, xs = np.nonzero(eye)
            if d[max(0, ys.min() - 4):ys.max() + 6, max(0, xs.min() - 3):xs.max() + 4].any():
                sys.exit(f"{tag} frame {i + 1}: the face changed")
            if (a[y0 + f["pivot"][1] + 12:y0 + ch, x0:x0 + cw, 3] > 0).any():
                sys.exit(f"{tag} frame {i + 1}: squares under the feet line")
            if tag == "ult" and i < ULT_BROKEN and d.any():
                sys.exit(f"ult frame {i + 1}: the broken blade changed")
            rec = records[f"riven_{tag}.png"][i]
            if rec["blade_axis"]:
                keep = np.zeros(d.shape, bool)             # the head round the eyes, and everything under the feet
                keep[max(0, ys.min() - 12):ys.max() + 8, max(0, xs.min() - 8):xs.max() + 9] = True
                keep[f["pivot"][1] + 12:] = True
                a[y0:y0 + ch, x0:x0 + cw] = reforge(a[y0:y0 + ch, x0:x0 + cw], rec["blade_axis"], rec["extension_px"],
                                                    keep)
            per.append(int(np.any(a[y0:y0 + ch, x0:x0 + cw] != c, -1).sum()))
        big = Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST)
        big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        if tag != base:
            cells["tags"][tag] = rows
        print(f"riven_{tag}.png  over riven_{base}.png, squares added or lit per frame {per}")
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(cells_text(cells))


def cells_text(cells):
    """riven_cells.json in native_pose.py's layout: one line a tag."""
    return (f'{{"cell": {json.dumps(cells["cell"])}, "scale": {cells["scale"]}, "tags": {{\n'
            + ",\n".join(f"  {json.dumps(t)}: [" + ", ".join(json.dumps(r) for r in rows) + "]"
                         for t, rows in cells["tags"].items()) + "\n}}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery", nargs="?", help="Codex's strips delivery (riven_animation_pack)")
    ap.add_argument("--blade", help="Codex's second delivery (riven_fx2_complete): the reforged-sword strips")
    args = ap.parse_args()
    if args.blade:
        blade(args.blade)
        return
    if not args.delivery:
        ap.error("a delivery folder or --blade")
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    design = blocks(os.path.join(SRC, "riven_native.png"))
    ys, xs = np.nonzero(design[..., 3] > 0)
    body = design[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    palette = colours(design)
    cw, ch = cells["cell"][:2]
    master = np.asarray(Image.open(D.lp(os.path.join(args.delivery, "reference", "head_master_1x.png"))).convert("RGBA"))
    with open(D.lp(os.path.join(args.delivery, "manifest.json")), encoding="utf-8") as f:
        manifest = {k: [(fr["head_origin"], fr["head_rotation_clockwise"]) for fr in v["frames"]]
                    for k, v in json.load(f)["animations"].items()}
    idle = np.asarray(Image.open(D.lp(os.path.join(args.delivery, "reference", "riven_idle.png"))).convert("RGBA"))
    Image.fromarray(idle).save(D.lp(os.path.join(SRC, "riven_idle.png")))
    for tag in TAGS:
        a = blocks(os.path.join(args.delivery, f"riven_{tag}.png"))
        extra = colours(a) - palette
        if extra:
            sys.exit(f"{tag}: colours not in the design: {sorted(extra)}")
        fr = cells["tags"][tag]
        cols = layout(len(fr))
        out = a.copy()
        changed = []
        for i, f in enumerate(fr):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c = a[y0:y0 + ch, x0:x0 + cw]
            op = c[..., 3] > 0
            ys, xs = np.nonzero(op)
            eyes = sum(int((op & np.all(c[..., :3] == np.array(e, np.uint8), -1)).sum()) for e in EYES[1:])
            if eyes != 6:
                sys.exit(f"{tag} frame {i + 1}: {eyes} eye squares (dark and green), not 6")
            crop = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            if crop.shape == body.shape and (crop == body).all():
                changed.append(0)
                continue
            origin, rotation = manifest[tag][i]
            hm = np.rot90(master, k=-(rotation // 90)) if rotation else master
            x, y = origin
            pasted = c[y:y + hm.shape[0], x:x + hm.shape[1]]
            if pasted.shape != hm.shape or not (pasted[hm[..., 3] > 0] == hm[hm[..., 3] > 0]).all():
                sys.exit(f"{tag} frame {i + 1}: the head is not the design's at {origin}")
            t = D.one_outline(c, head(c.shape[:2], master, origin, rotation))
            changed.append(int(np.any(t != c, -1).sum()))
            if tag == "run":
                t = np.concatenate([np.zeros((RUN_DROP, cw, 4), np.uint8), t[:ch - RUN_DROP]])
            low = int(np.nonzero(t[..., 3] > 0)[0].max()) - (f["pivot"][1] + 11)
            if low > FALL.get(tag, 0):
                sys.exit(f"{tag} frame {i + 1}: {low} rows under the feet line")
            out[y0:y0 + ch, x0:x0 + cw] = t
        big = Image.fromarray(out).resize((out.shape[1] * Z, out.shape[0] * Z), Image.NEAREST)
        big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        print(f"riven_{tag}.png  {len(fr)} frames, pixels changed per frame {changed}")


if __name__ == "__main__":
    main()
