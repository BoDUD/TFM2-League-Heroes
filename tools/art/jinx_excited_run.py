#!/usr/bin/env python3
"""league_jinx's Get Excited sprint (2026-11-03, the user: 「金克丝刷新被动后少了点跑步的加速动作？」).

After a takedown her four Get Excited buffs (league_takedowns JINX_EXCITED: +40 / +30 / +30 % move speed for 2 / 4 / 6 s)
nearly double her speed, but the game plays the same easy jog (`run`: 8 frames of 0.117 s) at any speed: she glides.
Her sheet gets a sprint twin of the jog, `run_x` (and `hd_run_x`, `lo_run_x`), which the add-on plays instead while the
first two speed buffs last (addons/league_takedowns/src/view.rs: run -> run_x):

- the same 8 frames, `FRAME_S` each (0.56 s a stride instead of 0.936 s, x1.67);
- her upper body leant forward from the waist (`LEAN`: every row above `HIP` squares over the soles slid toward where she
  runs, the higher the further - about 11 degrees; the minigun, her arms on it and her legs stay as they are, the braids
  bend back from the head);
- two afterimages behind her (`GHOSTS`): the leant poses of the frame before and the one before that, as silhouettes in
  her hair's cyan, 5 and 10 squares back, the further one fainter, under her. Of three drafts (speed lines, two
  afterimages, one) the two afterimages read as a dash best.

Each twin frame is its jog frame padded `PAD` squares on both sides (the pivot is the frame's centre: the soles stay
where the jog's are, so the swap in mid-stride does not jump), the same height and timing slot for slot. The 1x frames
(`run_x`) and the dense ones (`hd_run_x`, PPU 2.2, what the game draws through league.dll) get the same lean and trail
at their own density; `lo_run_x` (the UI's, never played there) is `lo_run`'s own frames at the sprint's timing.

The twins go in a strip under the rest of the sheet; run again, it cuts the old strip off first.

    python tools/art/jinx_excited_run.py                  # (re)write run_x, hd_run_x, lo_run_x into her sheet
    python tools/art/jinx_excited_run.py --preview DIR    # run beside run_x (dense, 4x) -> DIR/jinx_excited_run.png
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STEM = os.path.join(ROOT, "league", "champions", "league_jinx")
PPU = 2.2                      # addons/league_main/src/hd.rs league_jinx
SUFFIX = "_x"
FRAME_S = 0.07                 # a sprint frame (the jog's are 0.117 s)
LEAN = 0.2                     # squares slid forward per square above the waist (tan 11.3 degrees)
HIP = 17.5                     # 1x squares over the soles where the lean starts: just over the minigun
PAD = {1.0: 12, PPU: 26}       # clear squares added on each side: 41 -> 65 and 90 -> 142 (65 x 2.2)
GAP = 20                       # clear rows between the sheet and the strip (past an hd_idle's 18-square pad)
# (frames back, 1x squares behind her, colour, alpha), the nearer first: it takes the squares both cover
GHOSTS = [(1, 5, (110, 205, 255), 110), (2, 10, (110, 205, 255), 50)]


def frames(an, px, tag):
    out = []
    for f in an[tag]["frames"]:
        d = f["data"]
        x, y, w, h = (int(round(d[k])) for k in "xywh")
        out.append(px[y:y + h, x:x + w].copy())
    return out


def soles(a):
    """The lowest opaque row of a frame."""
    rows = np.where((a[..., 3] > 0).any(1))[0]
    return int(rows.max()) if len(rows) else a.shape[0] - 1


def lean(a, k):
    """Every row above the waist slid right (forward: her frames face right), the higher the further."""
    out = np.zeros_like(a)
    bend = soles(a) - HIP * k
    w = a.shape[1]
    for y in range(a.shape[0]):
        s = int(round((bend - y) * LEAN)) if y < bend else 0
        if s <= 0:
            out[y] = a[y]
        else:
            out[y, s:] = a[y, :w - s]
    return out


def behind(op, shape, dy, s):
    """A silhouette (bool rows x columns) in a frame of `shape`: dy rows down (the two frames' centres together), s
    columns back (left)."""
    out = np.zeros(shape, bool)
    (hh, ww), (h, w) = shape, op.shape
    y0, y1 = max(0, dy), min(hh, h + dy)
    x1 = min(ww, w - s)
    if y1 > y0 and x1 > 0:
        out[y0:y1, :x1] = op[y0 - dy:y1 - dy, s:s + x1]
    return out


def sprint(fr, k):
    """The jog's frames at density k -> the sprint's: padded, leant, the afterimages under each."""
    p = PAD[k]
    leant = []
    for a in fr:
        out = np.zeros((a.shape[0], a.shape[1] + 2 * p, 4), np.uint8)
        out[:, p:p + a.shape[1]] = a
        leant.append(lean(out, k))
    made = []
    for i, a in enumerate(leant):
        b = a.copy()
        for back, dx, colour, alpha in GHOSTS:
            g = leant[(i - back) % len(leant)]
            sil = behind(g[..., 3] > 0, a.shape[:2], (a.shape[0] - g.shape[0]) // 2, int(round(dx * k)))
            b[sil & (b[..., 3] == 0)] = (*colour, alpha)
        made.append(b)
    return made


def build():
    path = STEM + "#anim.fanim"
    an = json.load(open(path, encoding="utf-8-sig"))
    anims = an["anims"]
    px = np.asarray(Image.open(STEM + "#sheet.png").convert("RGBA"))
    twins = {"run" + SUFFIX: ("run", 1.0), "hd_run" + SUFFIX: ("hd_run", PPU)}
    lo = "lo_run" + SUFFIX
    for t in list(twins) + [lo]:
        anims.pop(t, None)
    # the old strip goes: the sheet ends under the lowest frame of every other tag
    bottom = max(int(round(f["data"]["y"] + f["data"]["h"])) for v in anims.values() for f in v["frames"])
    px = px[:bottom]
    made = {t: sprint(frames(anims, px, src), k) for t, (src, k) in twins.items()}
    strip_h = max(f.shape[0] for fr in made.values() for f in fr)
    width = max(px.shape[1], sum(f.shape[1] + 1 for fr in made.values() for f in fr))
    sheet = np.zeros((bottom + GAP + strip_h, width, 4), np.uint8)
    sheet[:bottom, :px.shape[1]] = px
    x, y0 = 0, bottom + GAP
    for t, fr in made.items():
        anims[t] = {"frames": []}
        for f in fr:
            sheet[y0:y0 + f.shape[0], x:x + f.shape[1]] = f
            anims[t]["frames"].append({"duration": FRAME_S, "data": {"x": float(x), "y": float(y0),
                                                                      "w": float(f.shape[1]), "h": float(f.shape[0])}})
            x += f.shape[1] + 1
    anims[lo] = {"frames": [{"duration": FRAME_S, "data": dict(f["data"])} for f in anims["lo_run"]["frames"]]}
    Image.fromarray(sheet, "RGBA").save(STEM + "#sheet.png", optimize=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(an, ensure_ascii=False, separators=(",", ":")))
    print(f"{STEM}#sheet.png {sheet.shape[1]} x {sheet.shape[0]}: " +
          ", ".join(f"{t} {len(v['frames'])} frames" for t, v in anims.items() if t.endswith(SUFFIX)))


def preview(out_dir, z=4):
    """hd_run over hd_run_x on the battlefield's green, with the ground line and the frame's centre."""
    os.makedirs(out_dir, exist_ok=True)
    an = json.load(open(STEM + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    px = np.asarray(Image.open(STEM + "#sheet.png").convert("RGBA"))
    bg = (92, 120, 76, 255)
    rows = []
    for tag in ("hd_run", "hd_run" + SUFFIX):
        fr = frames(an, px, tag)
        cw = max(f.shape[1] for f in fr)
        ch = max(f.shape[0] for f in fr)
        im = Image.new("RGBA", ((cw + 4) * len(fr), ch), bg)
        for i, f in enumerate(fr):
            # centre on the cell, the frame's centre at the cell's centre (the game's pivot)
            ox = i * (cw + 4) + (cw - f.shape[1]) // 2
            oy = (ch - f.shape[0]) // 2
            im.alpha_composite(Image.fromarray(f), (ox, oy))
        rows.append((tag, im.resize((im.width * z, im.height * z), Image.NEAREST)))
    w = max(r.width for _, r in rows) + 110
    s = Image.new("RGB", (w, sum(r.height + 12 for _, r in rows)), (24, 24, 28))
    d = ImageDraw.Draw(s)
    y = 0
    for tag, r in rows:
        s.paste(r, (110, y))
        d.text((6, y + 6), tag, fill=(255, 236, 160))
        y += r.height + 12
    path = os.path.join(out_dir, "jinx_excited_run.png")
    s.save(path)
    print(path, s.size)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="write jinx_excited_run.png here instead")
    args = ap.parse_args()
    if args.preview:
        preview(args.preview)
    else:
        build()
