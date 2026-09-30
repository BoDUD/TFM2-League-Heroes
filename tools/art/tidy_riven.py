#!/usr/bin/env python3
"""Check Codex's Riven strips, tidy them and write them to the native strips.

    python tools/art/tidy_riven.py <Codex's strips delivery>     # 1. the ten strips (riven_strips40_complete)
    python tools/art/tidy_riven.py --redo <Codex's redo delivery>   # 2. frames redrawn after League (riven_redo18b)
    python tools/art/tidy_riven.py --neck                          # 3. the one-square necks widened
    python tools/art/tidy_riven.py --blade                         # 4. the energy blade while R lasts

1. Codex drew the strips from the approved design on the reference cells (96x96 game pixels,
assets/source/native/riven_cells.json): every game pixel one flat 8x8 block, only the design's 27 colours, alpha 0 or
255, the design's head pasted into every frame (its manifest's head_origin and rotation, reference/head_master_1x.png;
two 2x2 eyes on one row), the last frame of every action the design itself. That is checked here (the script stops
on a failure), then:
  - one outline: the black just inside the outline turned into the material's own darkest shade, outline spurs
    and lone specks off (design_riven.one_outline); the pasted head and the ring round it are left alone, and frames
    that are the design itself are not touched;
  - a run that floats goes down as far as its lowest sole allows (the 46-row run stood 3 rows over the feet line;
    the 40-row one stands on it);
  - every frame's head placement and sword (the manifest's `sword`: the broken end's middle and the unit vector from
    the hilt to it, null when the blade faces the camera) go to assets/source/native/riven_frames40.json.
2. --redo: the 40-row delivery (a nearest-neighbour shrink of the 46-row strips) kept the 46-row poses, and 18 of
them put the sword over the head with the arm hidden behind it, or apart from the hand (the user: "脖子拉伸 手看起来
脱节？", "各种身体脱节", "还有无影手了？"). Codex redrew those after League's frames at the 40-row scale (round 1:
REDO18.md; round 2, REDO18B.md: arms as thick as the design's, swords reused from untouched frames or redrawn square
by square, never rotated). The redo's strips replace ours after the same checks; every frame it did not list must be
ours square for square, and its records replace the redrawn frames' in riven_frames40.json.
3. --neck: under the pasted chin the shrink left a one-square neck ('h p h' with clear squares beside it, two rows)
in many frames; widened to the design's ('h p x r h' on the first row under the chin, 'h p x h' on the second). A
frame whose neck is already wide is left as it is, so the step can run again.
4. --blade: the user's pick for the R ("照示意图"): a big energy blade drawn under every frame that has a sword record,
along it, wrapping the broken blade (League's R), and the blade's rune green lit where the energy runs; the ult's
first ULT_BROKEN frames keep the broken blade. It writes the `_r` strips (attack_r ... skill2_r: the actions while R
lasts) and redraws riven_ult.png and riven_r_slash.png in place (only clear squares are filled, so it can run again).
Then run import_native.py --hero riven (EYES steadies idle and run on the eyes' green).
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
# --blade: the reforged sword (the user's option B) - each strip and the strip it is drawn over
BLADE = {"ult": "ult", "r_slash": "r_slash", "attack_r": "attack", "skill_r": "skill", "q2_r": "q2", "q3_r": "q3",
         "skill2_r": "skill2"}
BLADE_RUNE = (0x42, 0x6E, 0x3B)         # the broken blade's rune green, lit to #87D46A where the energy runs
BLADE_GREENS = {(0xF6, 0xEA, 0xDB), (0xC9, 0xEF, 0x9A), (0x87, 0xD4, 0x6A), (0x4B, 0xA8, 0x5A), (0x2D, 0x69, 0x40)}
ULT_BROKEN = 2                          # the ult's first frames keep the broken blade
# the user's pick after the first delivery ("开大时 刀没变大？" -> the mock "照示意图"): a big energy blade drawn under
# the frame along Codex's blade axis, wrapping the whole broken blade (League's R); half its width, how far it runs
# past the broken end (less where Codex shortened its tip, never out of the cell) and back toward the hilt
# (drawn for 46 rows at 6.5 / 16 / 22; scaled to the 40-row sprite)
REFORGE_HALF = 5.5
REFORGE_TIP = 14
REFORGE_HILT = 19
FRAMES = os.path.join(SRC, "riven_frames40.json")
# --neck: the neck's squares
NECK_H, NECK_P, NECK_X, NECK_R = (0x49, 0x33, 0x28), (0xA8, 0x64, 0x3F), (0xFB, 0xC6, 0x97), (0xCB, 0x80, 0x53)
RIM2, BODY2, INNER2, CORE2, HOT2 = ((0x2D, 0x69, 0x40), (0x4B, 0xA8, 0x5A), (0x87, 0xD4, 0x6A), (0xC9, 0xEF, 0x9A),
                                    (0xF6, 0xEA, 0xDB))


def reforge(c, axis, keep):
    """The energy blade under one frame's squares (never over them, never on `keep`): along the axis from the
    broken end (x0, y0) in direction (ux, uy); it widens from the hilt over 4 squares, holds REFORGE_HALF and comes
    to a point over its last 9; a #2D6940 rim, #4BA85A inside it, #87D46A down the middle, a #C9EF9A line past the
    break that turns #F6EADB near the point."""
    x0, y0, ux, uy = axis[:4]
    n = float(np.hypot(ux, uy))
    ux, uy = ux / n, uy / n
    H, W = c.shape[:2]
    room = min((W - 1 - x0) / ux if ux > 0 else 1e9, x0 / -ux if ux < 0 else 1e9, y0 / -uy if uy < 0 else 1e9)
    e = min(REFORGE_TIP, room - 1)
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


def load_frames():
    with open(D.lp(FRAMES), encoding="utf-8") as f:
        return json.load(f)


def save_frames(table):
    with open(D.lp(FRAMES), "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n" + ",\n".join(f"  {json.dumps(t)}: [\n" + ",\n".join(f"    {json.dumps(r)}" for r in rows)
                                  + "\n  ]" for t, rows in table.items()) + "\n}\n")


def blade():
    """--blade: the energy blade under every frame with a sword record (riven_frames40.json), the rune green lit
    inside it; nothing drawn in the box round the eyes or under the feet line."""
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    table = load_frames()
    cw, ch = cells["cell"][:2]
    for tag, base in BLADE.items():
        a = blocks(os.path.join(SRC, f"riven_{base}.png"))
        rows = cells["tags"][base]
        cols = layout(len(rows))
        per = []
        for i, f in enumerate(rows):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c = a[y0:y0 + ch, x0:x0 + cw]
            rec = table[base][i]["sword"]
            if rec is None or (base == "ult" and i < ULT_BROKEN):
                per.append(0)
                continue
            eye = np.zeros(c.shape[:2], bool)
            for e in EYES[1:]:
                eye |= (c[..., 3] > 0) & np.all(c[..., :3] == np.array(e, np.uint8), -1)
            ys, xs = np.nonzero(eye)
            keep = np.zeros(c.shape[:2], bool)             # the head round the eyes, and everything under the feet
            keep[max(0, ys.min() - 12):ys.max() + 8, max(0, xs.min() - 8):xs.max() + 9] = True
            keep[f["pivot"][1] + 12:] = True
            axis = list(rec["broken_end"]) + list(rec["direction"])
            t = reforge(c, axis, keep)
            # the broken blade's rune green lit where the energy runs (the band behind the broken end)
            x, y, ux, uy = axis
            yy, xx = np.mgrid[0:ch, 0:cw]
            along = (xx - x) * ux + (yy - y) * uy
            across = np.abs(-(xx - x) * uy + (yy - y) * ux)
            rune = (np.all(t[..., :3] == np.array(BLADE_RUNE, np.uint8), -1) & (t[..., 3] > 0) & (across <= 2.5)
                    & (along <= 1) & (along >= -REFORGE_HILT) & ~keep)
            t[rune, :3] = INNER2
            per.append(int(np.any(t != c, -1).sum()))
            a[y0:y0 + ch, x0:x0 + cw] = t
        big = Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST)
        big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        if tag != base:
            cells["tags"][tag] = rows
        print(f"riven_{tag}.png  over riven_{base}.png, squares added or lit per frame {per}")
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(cells_text(cells))


def redo(folder):
    """--redo: the strips of Codex's redo delivery in place of ours, after the checks; the redrawn frames' records."""
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    with open(D.lp(os.path.join(folder, "manifest.json")), encoding="utf-8") as f:
        anims = json.load(f)["animations"]
    master = np.asarray(Image.open(D.lp(os.path.join(folder, "reference", "head_master_1x.png"))).convert("RGBA"))
    palette = colours(blocks(os.path.join(SRC, "riven_native.png")))
    table = load_frames()
    cw, ch = cells["cell"][:2]
    for tag, v in anims.items():
        a = blocks(os.path.join(folder, "strips", f"riven_{tag}.png"))
        ours = blocks(os.path.join(SRC, f"riven_{tag}.png"))
        if a.shape != ours.shape:
            sys.exit(f"{tag}: {a.shape[1]}x{a.shape[0]}, not {ours.shape[1]}x{ours.shape[0]}")
        extra = colours(a) - palette
        if extra:
            sys.exit(f"{tag}: colours not in the design: {sorted(extra)}")
        recs = {r["frame"]: r for r in v["frames"]}
        rows = cells["tags"][tag]
        cols = layout(len(rows))
        for i, f in enumerate(rows):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c, o = a[y0:y0 + ch, x0:x0 + cw], ours[y0:y0 + ch, x0:x0 + cw]
            if i + 1 not in recs:
                if not (c == o).all():
                    sys.exit(f"{tag} frame {i + 1}: changed but not listed")
                continue
            r = recs[i + 1]
            rot = r["head_rotation_clockwise"]
            hm = np.rot90(master, k=-(rot // 90)) if rot else master
            x, y = r["head_origin"]
            pasted = c[y:y + hm.shape[0], x:x + hm.shape[1]]
            if not (pasted[hm[..., 3] > 0] == hm[hm[..., 3] > 0]).all():
                sys.exit(f"{tag} frame {i + 1}: the head is not the design's at {(x, y)}")
            op = c[..., 3] > 0
            eyes = sum(int((op & np.all(c[..., :3] == np.array(e, np.uint8), -1)).sum()) for e in EYES[1:])
            if eyes != 6:
                sys.exit(f"{tag} frame {i + 1}: {eyes} eye squares, not 6")
            if int(np.nonzero(op)[0].max()) > f["pivot"][1] + 11 + FALL.get(tag, 0):
                sys.exit(f"{tag} frame {i + 1}: squares under the feet line")
            table[tag][i] = {"head_origin": r["head_origin"], "head_rotation_clockwise": rot, "sword": r["sword"]}
        big = Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST)
        big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        print(f"riven_{tag}.png  frames {sorted(recs)} redrawn")
    save_frames(table)


def neck():
    """--neck: every frame's one-square neck under the pasted chin widened to the design's."""
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    table = load_frames()
    cw, ch = cells["cell"][:2]
    for tag in TAGS:
        a = blocks(os.path.join(SRC, f"riven_{tag}.png"))
        rows = cells["tags"][tag]
        cols = layout(len(rows))
        done = []
        for i in range(len(rows)):
            rec = table[tag][i]
            if rec["head_rotation_clockwise"]:
                continue
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c = a[y0:y0 + ch, x0:x0 + cw]
            ox, oy = rec["head_origin"]
            y = oy + 16

            def col(yy, xx):
                return tuple(int(v) for v in c[yy, xx, :3]) if c[yy, xx, 3] else None

            def put(yy, xx, rgb, only_clear=False):
                if not (only_clear and c[yy, xx, 3]):
                    c[yy, xx, :3] = rgb
                    c[yy, xx, 3] = 255
            for n in range(ox + 10, ox + 18):
                if (col(y, n) == NECK_P and col(y, n - 1) == NECK_H and col(y, n + 1) == NECK_H
                        and (col(y, n - 2) is None or col(y, n + 2) is None)):
                    break
            else:
                continue
            second = col(y + 1, n) == NECK_P
            put(y, n - 2, NECK_H, True)
            put(y, n - 1, NECK_P)
            put(y, n, NECK_X)
            put(y, n + 1, NECK_R)
            put(y, n + 2, NECK_H, True)
            if second:
                put(y + 1, n - 2, NECK_H, True)
                put(y + 1, n - 1, NECK_P)
                put(y + 1, n, NECK_X)
                put(y + 1, n + 1, NECK_H)
            done.append(i + 1)
        if done:
            big = Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST)
            big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        print(f"riven_{tag}.png  necks widened in frames {done}")


def cells_text(cells):
    """riven_cells.json in native_pose.py's layout: one line a tag."""
    return (f'{{"cell": {json.dumps(cells["cell"])}, "scale": {cells["scale"]}, "tags": {{\n'
            + ",\n".join(f"  {json.dumps(t)}: [" + ", ".join(json.dumps(r) for r in rows) + "]"
                         for t, rows in cells["tags"].items()) + "\n}}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery", nargs="?", help="Codex's strips delivery (riven_strips40_complete)")
    ap.add_argument("--redo", help="Codex's redo delivery (riven_redo18b_complete): its strips and records")
    ap.add_argument("--neck", action="store_true", help="widen the one-square necks")
    ap.add_argument("--blade", action="store_true", help="the energy blade while R lasts")
    args = ap.parse_args()
    if args.redo:
        redo(args.redo)
    if args.neck:
        neck()
    if args.blade:
        blade()
    if args.redo or args.neck or args.blade:
        return
    if not args.delivery:
        ap.error("a delivery folder, --redo, --neck or --blade")
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    design = blocks(os.path.join(SRC, "riven_native.png"))
    ys, xs = np.nonzero(design[..., 3] > 0)
    body = design[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    palette = colours(design)
    cw, ch = cells["cell"][:2]
    master = np.asarray(Image.open(D.lp(os.path.join(args.delivery, "reference", "head_master_1x.png"))).convert("RGBA"))
    with open(D.lp(os.path.join(args.delivery, "manifest.json")), encoding="utf-8") as f:
        anims = json.load(f)["animations"]
    manifest = {k: [(fr["head_origin"], fr["head_rotation_clockwise"]) for fr in v["frames"]] for k, v in anims.items()}
    save_frames({k: [{"head_origin": fr["head_origin"], "head_rotation_clockwise": fr["head_rotation_clockwise"],
                      "sword": fr["sword"]} for fr in anims[k]["frames"]] for k in TAGS})
    idle = np.asarray(Image.open(D.lp(os.path.join(args.delivery, "reference", "riven_idle.png"))).convert("RGBA"))
    Image.fromarray(idle).save(D.lp(os.path.join(SRC, "riven_idle.png")))
    for tag in TAGS:
        path = os.path.join(args.delivery, f"riven_{tag}.png")
        if not os.path.exists(D.lp(path)):
            path = os.path.join(args.delivery, "strips", f"riven_{tag}.png")      # the 40-row delivery's layout
        a = blocks(path)
        extra = colours(a) - palette
        if extra:
            sys.exit(f"{tag}: colours not in the design: {sorted(extra)}")
        fr = cells["tags"][tag]
        cols = layout(len(fr))
        out = a.copy()
        changed = []
        drop = 0
        if tag == "run":                          # a run that floats goes down as far as its lowest sole allows
            gaps = [f["pivot"][1] + 11 - int(np.nonzero(a[(i // cols) * ch:(i // cols + 1) * ch,
                                                             (i % cols) * cw:(i % cols + 1) * cw, 3] > 0)[0].max())
                    for i, f in enumerate(fr)]
            drop = max(0, min(gaps))
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
            if drop:
                t = np.concatenate([np.zeros((drop, cw, 4), np.uint8), t[:ch - drop]])
            low = int(np.nonzero(t[..., 3] > 0)[0].max()) - (f["pivot"][1] + 11)
            if low > FALL.get(tag, 0):
                sys.exit(f"{tag} frame {i + 1}: {low} rows under the feet line")
            out[y0:y0 + ch, x0:x0 + cw] = t
        big = Image.fromarray(out).resize((out.shape[1] * Z, out.shape[0] * Z), Image.NEAREST)
        big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        print(f"riven_{tag}.png  {len(fr)} frames, pixels changed per frame {changed}")


if __name__ == "__main__":
    main()
