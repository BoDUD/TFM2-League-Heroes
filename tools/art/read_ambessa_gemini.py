#!/usr/bin/env python3
"""Read the user's Gemini pictures of Ambessa's first ten effects (tools/art/pack_ambessa_fx.py: a_hit pw_hit pw_aura
st_dash st_land q_sweep q_hit q_tip q2_crack q2_hit; the user, 2026-10-25: 「特效是包含gemini的十张和codex的十张 你一起处理
反正是每人做了一半」 - Codex drew the other ten) into game-size strips like Codex's pixel_1x, so tools/art/import_ambessa_fx.py
takes both halves the same way (read_aphelios_gemini.py's way).

    python tools/art/read_ambessa_gemini.py [--review DIR] [name ...]

Source: assets/source/ambessa/gemini_fx/ambessa_fx_<name>.jpg (Gemini's JPEGs, renamed after the delivery's
gemini-existing-map.json), the frames side by side in equal columns, on black (st_land on white). Each column: its
sides (EDGE px: the template's cell lines where Gemini kept them) and the background keyed out (MARGIN from black or
white: her dark smoke stays), then import_kassadin.py's read: one scale for the effect - the source cell onto the pack's
cell (cw x ch game px), or SIZE where Gemini drew the frames in a band of the column (its biggest frame's content to n
game px) - every game pixel the commonest colour under it snapped to the prompt's ramps (a bright colour wins from a
fifth: the white cores stay), lone dark specks dropped, the red side's symmetry: q2_crack top to bottom (it flies), the
two drawn into her own frames (FORWARD: q_sweep, st_dash) none, the rest left to right about the frame's own best axis
(the fuller half mirrored). Every frame keeps its place against the others (the union of the frames' content laid on
the cell the same way for all), so a ring stays on the ground and a burst rises as drawn.
Writes assets/source/ambessa/gemini_fx/pixel_1x/ambessa_fx_<name>.png (the frames side by side in cw x ch cells; the
FORWARD ones in cells as big as their content) and manifest.json (Codex's shape: file, frames, cell_1x, symmetry).
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
sys.path.insert(0, HERE)
import import_kassadin as K  # noqa: E402
import pack_ambessa_fx as PK  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ambessa", "gemini_fx")
OUT = os.path.join(SRC, "pixel_1x")
NAMES = ["a_hit", "pw_hit", "pw_aura", "st_dash", "st_land", "q_sweep", "q_hit", "q_tip", "q2_crack", "q2_hit"]
EDGE = 8                         # px off each column's sides (the template's lines Gemini kept in a_hit and pw_hit)
MARGIN = 24                      # a pixel is drawn when it is this far from the background (black: max > 24; white)
WHITE = {"st_land"}              # drawn on white
# the biggest frame's content in game px ("w" | "h", n) where Gemini drew in a band of the column (the pack's sizes)
SIZE = {"pw_aura": ("w", 38), "st_land": ("w", 27), "q_sweep": ("h", 40), "q2_crack": ("w", 42)}
GROUND = {"pw_aura", "st_land"}  # laid on the cell's bottom row (a ring round the feet)
# a game pixel is drawn from this share of the source pixels under it (import_kassadin's 45 %; thin faint lines - the
# fading X of q_tip, the cleave's last sparks - from less: Codex read its half at 15 %)
COVER = {"q_tip": 0.2, "pw_hit": 0.2, "a_hit": 0.3, "q2_hit": 0.25, "q_hit": 0.3}
SYM = {"q2_crack": "tb", "q_sweep": None, "st_dash": None}       # every other one "lr"


def layout():
    """name -> (frames, cell w, cell h, ramp colours) from the pack's lines."""
    pat = re.compile(r"row of (\d+) equal .*? cells, image size \d+x\d+ \(each cell (\d+)x(\d+)")
    out = {}
    for x in PK.FX:
        if x[0] in NAMES:
            n, w, h = (int(v) for v in pat.findall(x[7])[0])
            out[x[0]] = (n, w // 16, h // 16, re.findall(r"#[0-9A-Fa-f]{6}", x[5]))
    return out


LAYOUT = layout()


def use_ramp(names):
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in names]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    lum = sorted(cols, key=lambda c: c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11)
    K.DARKS = set(lum[:2])


def shrink(a, s, cover=0.45):
    """import_kassadin.shrink with its coverage share a parameter: every game pixel from the source pixels under it,
    snapped to the ramps; a fifth or more of a bright colour -> the brightest with a tenth or more; else, `cover` or
    more covered -> the commonest (a brighter one wins from 35 %); else clear."""
    H, W = a.shape[:2]
    h, w = max(1, int(round(H * s))), max(1, int(round(W * s)))
    idx = K.snap(np.clip(a[..., :3], 0, 255))
    alpha = a[..., 3] > 100
    bright = K.PAL_LUM >= K.BRIGHT
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        ya, yb = int(j / s), max(int(j / s) + 1, int((j + 1) / s))
        for i in range(w):
            xa, xb = int(i / s), max(int(i / s) + 1, int((i + 1) / s))
            m = alpha[ya:yb, xa:xb]
            if m.size == 0 or not m.any():
                continue
            ids, cnt = np.unique(idx[ya:yb, xa:xb][m], return_counts=True)
            share = cnt / m.size
            if share[bright[ids]].sum() >= 0.2:
                cand = [(K.PAL_LUM[ids[k]], ids[k]) for k in range(len(ids)) if bright[ids[k]] and share[k] >= 0.1]
                best = max(cand)[1] if cand else ids[np.argmax(np.where(bright[ids], cnt, -1))]
            elif m.mean() >= cover:
                share = cnt / cnt.sum()
                best = ids[cnt.argmax()]
                for k in np.argsort(-K.PAL_LUM[ids]):
                    if share[k] >= 0.35:
                        if K.PAL_LUM[ids[k]] > K.PAL_LUM[best]:
                            best = ids[k]
                        break
            else:
                continue
            out[j, i, :3] = K.PAL[best]
            out[j, i, 3] = 255
    return out


def key(rgb, white):
    if white:
        return np.where(rgb.min(-1) < 255 - MARGIN, 255, 0).astype(np.int16)
    return np.where(rgb.max(-1) > MARGIN, 255, 0).astype(np.int16)


def source(name):
    p = os.path.join(SRC, f"ambessa_fx_{name}.jpg")
    return p if os.path.isfile(p) else None


def read(name):
    n, cw, ch, ramp = LAYOUT[name]
    rgb = np.asarray(Image.open(source(name)).convert("RGB")).astype(np.int16)
    H, W = rgb.shape[:2]
    sw = W / n
    crops = []
    for k in range(n):
        x0, x1 = int(round(k * sw)) + EDGE, int(round((k + 1) * sw)) - EDGE
        p = rgb[EDGE:H - EDGE, x0:x1]
        crops.append(np.concatenate([p, key(p, name in WHITE)[..., None]], -1))
    boxes = []
    for a in crops:
        ys, xs = np.nonzero(a[..., 3] > 0)
        boxes.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else None)
    U = (min(b[0] for b in boxes if b), min(b[1] for b in boxes if b), max(b[2] for b in boxes if b),
         max(b[3] for b in boxes if b))
    sh = H - 2 * EDGE
    if name in SIZE:
        dim, target = SIZE[name]
        ext = [(b[2] - b[0]) if dim == "w" else (b[3] - b[1]) for b in boxes if b]
        s = target / max(ext)
    else:
        s = min(cw / (sw - 2 * EDGE), ch / sh)
    sym = SYM.get(name, "lr")
    if sym is None:                                   # drawn into her frames: a cell as big as the content
        cw, ch = int(np.ceil((U[2] - U[0]) * s)) + 1, int(np.ceil((U[3] - U[1]) * s)) + 1
    elif name in SIZE:                                # a band drawn bigger than the pack's cell: the cell grows to it
        cw = max(cw, int(np.ceil((U[2] - U[0]) * s)) + 2)
        ch = max(ch, int(np.ceil((U[3] - U[1]) * s)) + 2)
    use_ramp(ramp)
    # where a source pixel lands on the cell: the source column laid centred on the cell at the cell's scale; a band
    # (SIZE) or a cell as big as the content (FORWARD): the union of the frames' content centred, or on the bottom
    # row (GROUND)
    uw, uh = (U[2] - U[0]) * s, (U[3] - U[1]) * s
    if name in SIZE or sym is None:
        ox = (cw - uw) / 2 - U[0] * s
        oy = (ch - uh) - U[1] * s if name in GROUND else (ch - uh) / 2 - U[1] * s
    else:
        ox, oy = (cw - (sw - 2 * EDGE) * s) / 2, (ch - sh * s) / 2
    out = []
    for a, b in zip(crops, boxes):
        cell = np.zeros((ch, cw, 4), np.uint8)
        if b is None:
            out.append(cell)
            continue
        sub = a[b[1]:b[3], b[0]:b[2]]
        g = shrink(sub, s, COVER.get(name, 0.45))
        m = g[..., 3] > 0
        if not m.any():
            out.append(cell)
            continue
        gx = np.nonzero(m.any(0))[0]
        gy = np.nonzero(m.any(1))[0]
        if sym == "lr":
            g = K.mirror_lr(g, K.best_axis(m, int(gx.min()), int(gx.max())))
        elif sym == "tb":
            g = K.mirror_tb(g, K.best_axis(np.ascontiguousarray(m.T), int(gy.min()), int(gy.max())))
        g = K.despeckle(g)
        gm = g[..., 3] > 0
        if not gm.any():
            out.append(cell)
            continue
        yy, xx = np.nonzero(gm)
        top = int(gy.min()) if sym != "tb" else 0            # rows the read left clear over the content
        lft = int(gx.min()) if sym != "lr" else 0
        g = g[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        h, w = g.shape[:2]
        # a symmetric picture lies even in its cell only with the cell's parity: else its middle column (row) twice
        if sym == "lr" and (cw - w) % 2:
            g = np.insert(g, w // 2, g[:, w // 2], axis=1)
        elif sym == "tb" and (ch - h) % 2:
            g = np.insert(g, h // 2, g[h // 2], axis=0)
        h, w = g.shape[:2]
        # across: the cell's middle (lr: mirrored about its own axis), else the content's own place; down: the cell's
        # middle (tb: mirrored about its own middle row), else the content's own place
        x = (cw - w) // 2 if sym == "lr" else int(round(ox + b[0] * s)) + lft
        y = (ch - h) // 2 if sym == "tb" else int(round(oy + b[1] * s)) + top
        x, y = min(max(0, x), max(0, cw - w)), min(max(0, y), max(0, ch - h))
        cell[y:y + min(h, ch - y), x:x + min(w, cw - x)] = g[:ch - y, :cw - x]
        out.append(cell)
    while len(out) > 1 and not out[-1][..., 3].any():   # a last fade too faint to keep a square at game size
        out.pop()
    return out, sym


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--review", help="write the read strips at 8x here")
    a = ap.parse_args()
    names = a.names or [n for n in NAMES if source(n)]
    os.makedirs(OUT, exist_ok=True)
    man_path = os.path.join(SRC, "manifest.json")
    man = {e["file"]: e for e in json.load(open(man_path, encoding="utf-8"))} if os.path.isfile(man_path) else {}
    for name in names:
        if not source(name):
            print(name, "not there yet")
            continue
        cs, sym = read(name)
        strip = np.concatenate(cs, 1)
        f = f"ambessa_fx_{name}.png"
        Image.fromarray(strip).save(os.path.join(OUT, f))
        man[f] = {"file": f, "frames": len(cs), "cell_1x": [cs[0].shape[1], cs[0].shape[0]],
                  "symmetry": {"lr": "left-right", "tb": "top-bottom", None: "none (forward)"}[sym],
                  "source": f"ambessa_fx_{name}.jpg"}
        print(name, f"{len(cs)} frames of {cs[0].shape[1]}x{cs[0].shape[0]}",
              "drawn", [int((c[..., 3] > 0).sum()) for c in cs])
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            big = Image.fromarray(strip).resize((strip.shape[1] * 8, strip.shape[0] * 8), Image.NEAREST)
            bg = Image.new("RGBA", big.size, (40, 40, 52, 255))
            bg.alpha_composite(big)
            bg.convert("RGB").save(os.path.join(a.review, f"gemini_{name}.png"))
    with open(man_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump([man[k] for k in sorted(man)], fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
