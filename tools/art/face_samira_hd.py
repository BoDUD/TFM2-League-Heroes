#!/usr/bin/env python3
"""Samira's face kept as drawn while the rest of her goes coarse (the user, on the PPU 2.2 build: 「这嘴也太丑了」, then
「你可以其他地方模糊点 脸做好点啊」): 2.2 squares a game pixel voted her mouth - a dark lip line over the lips - into a
dark maroon slash and her one-pixel green eye away. So her frames stay on the 2.84 grid they were drawn on, everything
is brought to 2.2 squares and laid back on it (ppu_restyle.py RESTYLE samira look=2.2), and the face - this module's
keep(): her skin by the hair with all it encloses (eye, eye patch, scar, nose, mouth), a pixel round it - is put back
as drawn: the face of the approved 2.84 design in a 2.2 body, the way Yasuo's finer head sits on his body.

The face: the hair's teal finds the head (its top, its middle column), the biggest piece of her skin within 36 rows
under that top and 30 columns either side is the face. The hit flash (ppu_rig.flash: 45 % white) is undone first so
its skin is found; FACE gives the face's box by hand where the head lies on its side (the death), where the search
would take her midriff.

    python tools/art/face_samira_hd.py --review DIR    # every drawn frame with the face kept outlined in magenta
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
SKIN = [0xDB885B, 0xBE6F4B, 0x9B543A, 0xEBA064, 0xA3734C, 0x8F5D45, 0x753E2D]
FLASH = 0.45                    # ppu_rig.flash's white
# (tag, frame) -> (y0, y1, x0, x1): the box the face is the biggest skin piece in - the fall's first frame has no teal
# showing, and its face's skin runs on into her chest
FACE = {("dead", 2): (4, 30, 8, 34)}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def teal(a):
    """Her hair's teal: hue 170-215, saturated, not dark."""
    rgb = a[..., :3].astype(float) / 255
    mx, mn = rgb.max(-1), rgb.min(-1)
    c = mx - mn
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cs = np.where(c > 1e-6, c, 1)
    h = np.where(mx == b, 4 + (r - g) / cs, np.where(mx == g, 2 + (b - r) / cs, (g - b) / cs)) / 6 % 1 * 360
    s = np.where(mx > 0, c / np.maximum(mx, 1e-6), 0)
    return (a[..., 3] > 0) & (c > 1e-6) & (h > 170) & (h < 215) & (s > 0.35) & (mx > 0.25)


def unflashed(a):
    """A flashed frame back to its colours (its outline, drawn after the flash, goes black), near enough to find her
    skin and hair."""
    out = a.copy()
    out[..., :3] = np.clip(np.round((a[..., :3].astype(float) - 255 * FLASH) / (1 - FLASH)), 0, 255).astype(np.uint8)
    return out


def keep(tag, i, a):
    """The face of frame `a` (as drawn): a mask of the pixels to keep as drawn (the flashed hit frame: found on
    its colours with the flash taken out)."""
    m = _face(tag, i, a)
    return m if m.any() else _face(tag, i, unflashed(a))


def _face(tag, i, b):
    op = b[..., 3] > 0
    rgb = b[..., :3].astype(int)
    if (tag, i) in FACE:
        y0, y1, x0, x1 = FACE[(tag, i)]
    else:
        ys, xs = np.nonzero(teal(b))
        if not len(ys):
            return np.zeros(op.shape, bool)
        top = ys.min()
        cx = int(np.median(xs[ys <= top + 14]))
        y0, y1, x0, x1 = top, top + 36, max(0, cx - 30), cx + 30
    box = np.zeros(op.shape, bool)
    box[y0:y1, x0:x1] = True
    # her skin: the design's skin colours (a flashed frame's come back a step off: within 12 of one)
    pal = np.array([[(c >> 16) & 255, (c >> 8) & 255, c & 255] for c in SKIN])
    d = np.abs(rgb[..., None, :] - pal[None, None]).max(-1).min(-1)
    skin = op & box & (d <= 12)
    lbl, n = ndimage.label(skin, structure=np.ones((3, 3)))
    if not n:
        return np.zeros(op.shape, bool)
    face = lbl == (np.argmax(ndimage.sum(skin, lbl, range(1, n + 1))) + 1)
    face = ndimage.binary_fill_holes(ndimage.binary_dilation(face, iterations=1))
    return ndimage.binary_dilation(face, iterations=1) & op


def strips():
    """{(tag, i): frame as drawn} from assets/source/ppu/orig (read only)."""
    out = {}
    for fn in sorted(os.listdir(lp(ORIG))):
        if not (fn.startswith("samira_") and fn.endswith(".json")) or "." in fn[:-5]:
            continue
        tag = fn[len("samira_"):-5]
        with open(lp(os.path.join(ORIG, fn)), encoding="utf-8") as f:
            sizes = json.load(f).get("sizes")
        if sizes is None:                                   # (samira_face.json: the face point)
            continue
        s = np.asarray(Image.open(lp(os.path.join(ORIG, f"samira_{tag}.png"))).convert("RGBA"))
        x = 0
        for i, (W, H) in enumerate(sizes):
            out[(tag, i)] = s[:H, x:x + W]
            x += W + 1
    return out


def review(out_dir, z=3):
    os.makedirs(out_dir, exist_ok=True)
    tiles, seen = [], set()
    for (tag, i), a in strips().items():
        if tag in ("idle", "bp") or a.tobytes() in seen:
            continue
        seen.add(a.tobytes())
        m = keep(tag, i, a)
        ov = a.copy()
        ov[m & ~ndimage.binary_erosion(m)] = (255, 0, 255, 255)
        im = Image.new("RGBA", (a.shape[1], a.shape[0]), (150, 165, 150, 255))
        im.alpha_composite(Image.fromarray(ov))
        im = im.resize((im.width * z, im.height * z), Image.NEAREST)
        ImageDraw.Draw(im).text((2, 2), f"{tag} {i + 1}" + ("" if m.any() else " (no face)"), fill=(0, 0, 0, 255))
        tiles.append(im)
    cols = 10
    cw = max(t.width for t in tiles) + 6
    ch = max(t.height for t in tiles) + 6
    can = Image.new("RGB", (cols * cw, ((len(tiles) + cols - 1) // cols) * ch), (40, 40, 40))
    for j, t in enumerate(tiles):
        can.paste(t, ((j % cols) * cw, (j // cols) * ch), t)
    can.save(os.path.join(out_dir, "samira_face_kept.png"))
    print("written", os.path.join(out_dir, "samira_face_kept.png"), len(tiles))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    a = ap.parse_args()
    review(a.review)


if __name__ == "__main__":
    main()
