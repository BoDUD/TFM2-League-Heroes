#!/usr/bin/env python3
"""Some of Anivia's effects read back again from Codex's own image_gen drafts (its step-3 delivery's raw/), keeping the
drafts' proportions (tools/art/readback_nasus_fx.py's way).

    python tools/art/readback_anivia_fx.py [--raw DIR] [--only q_stun,r_cast] [--review out.png]

Codex's readback (assets/source/anivia/codex_fx/HANDOFF.md) fitted each frame into the target cell and then cleared
the middle for the body and pushed the side art into narrow bands at the cell's edges: the freeze's two ice pillars
became a 3-square stub and a line on the ground, the blizzard's two spirals round her (drawn 360 draft pixels wide,
stretched 5 times across a 70-square cell) a few dotted lines. Here each frame (between the manifest's
source_frame_cuts, rows source_crop_y) is brought down by one scale for the whole effect (READ: draft pixels a square),
the drawing's own mirror axis on the cell's middle and the crop's bottom on the cell's bottom row (the feet); a square
takes the commonest palette colour (the ice and snow ramps) of its draft pixels when enough of them are not the black
ground, its mirror twin voting with it (so every frame is symmetric left to right, the red side's rule). The squares go
to assets/source/anivia/codex_fx/pixel_1x/anivia_fx_<name>.png and their cells to readback.json, which
tools/art/import_anivia_fx.py prefers to the manifest. The drafts stay in Codex's outputs folder (not in the repo).
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "anivia", "codex_fx")
RAW = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Codex", "2026-10-17", "new-chat-7", "outputs",
                   "anivia_fx", "raw")
PRE = chr(92) * 2 + "?" + chr(92)
# the ice and snow ramps of the prompts (PROMPTS_FX.md): no deep ground blues on these
PALETTE = ["#FFFFFF", "#E4FBFF", "#A6EEFF", "#5CCBF5", "#2C8FD8", "#155AA6",
           "#EEF8FF", "#CDE6FA", "#9CC4EA", "#6F94C8", "#46669E"]

# name -> cell (w, h), draft pixels a square, how much of a square must be drawn (not ground) to keep it
READ = {
    # the freeze round a stunned champion: two ice pillars up its sides on a frost ring, drawn at the prompt's
    # 16 px a square (362 x 649 a frame -> 22 x 40)
    "q_stun": dict(cell=(22, 40), scale=16.2, cover=0.3),
    # the blizzard round her as she raises her wings: the spirals 474 draft pixels tall -> 52 squares, as wide as drawn
    "r_cast": dict(cell=(40, 52), scale=9.1, cover=0.3),
}


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def axis(fg):
    """The drawing's own mirror axis in a crop (x, crop pixels): the line its drawn pixels best overlap their mirror
    image about (the frame cuts are not centred on it)."""
    w = fg.shape[1]
    best, at = -1.0, w / 2
    for a2 in range(w // 2, 3 * w // 2):        # the axis at a2 / 2, within the middle half
        lo, hi = max(0, a2 - w + 1), min(w, a2 + 1)
        left = fg[:, lo:hi]
        right = fg[:, a2 - np.arange(lo, hi)]
        both = int((left & right).sum())
        score = both / max(1, int(fg.sum()))
        if score > best:
            best, at = score, a2 / 2 + 0.5
    return at


def read(name, entry, raw_dir):
    cfg = READ[name]
    raw = np.asarray(Image.open(lp(os.path.join(raw_dir, entry["file"]))).convert("RGBA")).astype(int)
    rgb, alpha = raw[..., :3], raw[..., 3]
    ground = (alpha < 128) | (rgb.max(-1) < 40)
    pal = np.array([hexrgb(c) for c in PALETTE])
    W, H = cfg["cell"]
    s = cfg["scale"]
    y0, y1 = entry["source_crop_y"]
    cuts = entry["source_frame_cuts"]
    out = []
    for k in range(entry["frames"]):
        x0, x1 = cuts[k], cuts[k + 1]
        cx = axis(~ground[y0:y1, x0:x1]) + x0
        ox = cx - W / 2 * s
        oy = y1 - H * s
        votes = np.zeros((H, W, len(pal)))
        drawn = np.zeros((H, W))
        for gy in range(H):
            for gx in range(W):
                ya, yb = int(round(oy + gy * s)), int(round(oy + (gy + 1) * s))
                xa, xb = int(round(ox + gx * s)), int(round(ox + (gx + 1) * s))
                ya, xa = max(ya, y0), max(xa, x0)
                yb, xb = min(yb, y1), min(xb, x1)
                if yb <= ya or xb <= xa:
                    continue
                blk = rgb[ya:yb, xa:xb].reshape(-1, 3)
                fg = ~ground[ya:yb, xa:xb].reshape(-1)
                drawn[gy, gx] = fg.mean()
                if fg.any():
                    near = np.argmin(((blk[fg][:, None, :] - pal[None]) ** 2).sum(-1), axis=1)
                    votes[gy, gx] = np.bincount(near, minlength=len(pal))
        # the mirror twin votes with each square: symmetric left to right
        votes = votes + votes[:, ::-1]
        drawn = (drawn + drawn[:, ::-1]) / 2
        cell = np.zeros((H, W, 4), np.uint8)
        keep = drawn >= cfg["cover"]
        best = votes.argmax(-1)
        cell[keep, :3] = pal[best[keep]]
        cell[keep, 3] = 255
        assert (cell == cell[:, ::-1]).all()
        out.append(cell)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=RAW, help="Codex's raw/ folder (its step-3 delivery)")
    ap.add_argument("--only", help="comma separated effects (default: all in READ)")
    ap.add_argument("--review", help="write the new cells at 8x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    entries = {e["name"]: e for e in man["effects"]}
    names = a.only.split(",") if a.only else list(READ)
    rb_path = os.path.join(SRC, "readback.json")
    rb = json.load(open(lp(rb_path), encoding="utf-8")) if os.path.exists(lp(rb_path)) else {}
    shown = []
    for name in names:
        cells = read(name, entries[name], a.raw)
        W, H = READ[name]["cell"]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(SRC, "pixel_1x", f"anivia_fx_{name}.png")))
        rb[name] = {"frames": len(cells), "cell_1x": [W, H], "scale": READ[name]["scale"],
                    "source": f"raw/{entries[name]['file']}"}
        shown.append((name, strip))
        print(name, len(cells), "frames", W, "x", H, [int((c[..., 3] > 0).sum()) for c in cells], "squares")
    with open(lp(rb_path), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rb, f, ensure_ascii=False, indent=1)
    if a.review:
        Z = 8
        tiles = []
        for name, strip in shown:
            bg = Image.new("RGBA", (strip.shape[1], strip.shape[0]), (30, 34, 44, 255))
            bg.alpha_composite(Image.fromarray(strip))
            tiles.append(bg.resize((strip.shape[1] * Z, strip.shape[0] * Z), Image.NEAREST))
        sheet = Image.new("RGB", (max(t.width for t in tiles), sum(t.height + 8 for t in tiles)), (0, 0, 0))
        y = 0
        for t in tiles:
            sheet.paste(t.convert("RGB"), (0, y))
            y += t.height + 8
        sheet.save(lp(a.review))


if __name__ == "__main__":
    main()
