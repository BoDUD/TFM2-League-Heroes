#!/usr/bin/env python3
"""Some of Nasus's effects read back again from Codex's own image_gen drafts (its step-3 delivery's raw/), keeping the
drafts' proportions.

    python tools/art/readback_nasus_fx.py [--raw DIR] [--only w_slow,q_soul] [--review out.png]

Codex's readback (assets/source/nasus/codex_fx/manifest.json "processing") fitted each frame's crop into a target
rectangle of another shape - q_soul's wisps 335 x 214 draft pixels into 38 x 6 squares, squashed five times - and
pushed the side art of the wrapping pictures into narrow bands at the cell's edges (w_slow's wisps became two bars the
height of the cell, a cage round the champion). Here each frame's crop (the manifest's raw_crop_xyxy) is brought down by
one scale for the whole effect (READ: draft pixels a square), centred where READ puts it; a square takes the commonest
palette colour of its draft pixels when enough of them are not the black ground, its mirror twin voting with it (so
every frame is symmetric left to right, the red side's rule). The squares go to
assets/source/nasus/codex_fx/pixel_1x/nasus_fx_<name>.png and their cells to readback.json, which
tools/art/import_nasus_fx.py prefers to the manifest. The drafts stay in Codex's outputs folder (not in the repo).
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "nasus", "codex_fx")
RAW = os.path.join(os.environ["USERPROFILE"], "Documents", "Codex", "2026-10-17", "new-chat-5", "outputs", "nasus_fx", "raw")
PRE = chr(92) * 2 + "?" + chr(92)

# name -> cell (w, h), draft pixels a square, where a frame's crop centre goes in the cell (x, y), how much of a
# square must be drawn (not ground) to keep it, rows cut off at the bottom of the crop (draft pixels)
READ = {
    # the withering glyph over a 36-tall champion (its head's top on row 8), the wisps hanging over its shoulders, the
    # motes falling beside it; the lowest motes cut where the cell ends
    "w_slow": dict(cell=(24, 44), scale=14.0, at=(11.5, None), top=0, cover=0.2),
    # the soul wisps at his chest (14 under the head's top: row 18), as Codex drew them, one scale
    # (frame 6's crop in the manifest catches the end of frame 5's ring: its own sparkles only)
    "q_soul": dict(cell=(40, 48), scale=9.0, at=(19.5, 19.0), top=None, cover=0.2,
                   crop={6: (1895, 150, 2097, 530)}),
}


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def axis(fg):
    """The drawing's own mirror axis in a crop (x, crop pixels): the line its drawn pixels best overlap their mirror
    image about (Codex's crops are not centred on it and catch bits of the next frame)."""
    w = fg.shape[1]
    best, at = -1.0, w / 2
    for a2 in range(w // 4, 3 * w // 2):        # the axis at a2 / 2
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
    raw = np.asarray(Image.open(lp(os.path.join(raw_dir, os.path.basename(entry["raw"])))).convert("RGBA")).astype(int)
    rgb, alpha = raw[..., :3], raw[..., 3]
    ground = (alpha < 128) | (rgb.max(-1) < 40)
    pal = np.array([hexrgb(c) for c in entry["palette"]])
    W, H = cfg["cell"]
    s = cfg["scale"]
    out = []
    for fd in entry["frame_details"]:
        x0, y0, x1, y1 = cfg.get("crop", {}).get(fd["frame"], fd["raw_crop_xyxy"])
        cx = axis(~ground[y0:y1, x0:x1]) + x0
        if cfg["top"] is not None:                 # the crop's top on this cell row
            oy = y0 - cfg["top"] * s
        else:                                      # the crop's middle on cfg["at"][1]
            oy = (y0 + y1) / 2 - cfg["at"][1] * s
        ox = cx - (cfg["at"][0] + 0.5) * s
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
    entries = {e["name"]: e for e in man["images"]}
    names = a.only.split(",") if a.only else list(READ)
    rb_path = os.path.join(SRC, "readback.json")
    rb = json.load(open(lp(rb_path), encoding="utf-8")) if os.path.exists(lp(rb_path)) else {}
    shown = []
    for name in names:
        cells = read(name, entries[name], a.raw)
        W, H = READ[name]["cell"]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(SRC, "pixel_1x", f"nasus_fx_{name}.png")))
        rb[name] = {"frames": len(cells), "cell_1x": [W, H], "scale": READ[name]["scale"],
                    "source": f"raw/{os.path.basename(entries[name]['raw'])}"}
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
