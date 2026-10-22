#!/usr/bin/env python3
"""Hwei's effects drawn by Gemini (the user, 2026-10-22: 「慧的特效在这里面 注意别和奇安娜的混淆了」 - 22 of the FX pack's 24
pictures came back as JPGs in Downloads, made in the pack's order, among Qiyana's) brought to the delivery
import_hwei_fx.py reads: assets/source/hwei/codex_fx/hwei_fx/pixel_1x/hwei_fx_<name>.png (one row of equal game-size
frames, alpha 0/255) + manifest.json - process_shyvana_fx.py's way (its keying, cutting, voting and symmetry, called with
Hwei's tables, process_qiyana_fx.py's setup()).

    python tools/art/process_hwei_fx.py [--src C:/t/hw_work/gemini] [--review DIR]

Which JPGs are his: the 24 downloaded 16:21-16:29 (Gemini_Generated_Image_rxl9yn* x10, k8a4t2* x10, gy0g39* x2,
edy4w2* x2), copied to --src as g00.jpg .. g23.jpg in the order they were made (not committed). The last two (edy4w2*,
16:28) are Qiyana's River / Grass pictures (a blue puddle with white spray, a green grass ring) - not his, left alone;
the first 22 follow the pack's order but for the ult's projectile and canvas, which Gemini left out: g20 is r_burst,
g21 r_hit. Of the two missing ones the user had Gemini draw r_paint (the spiralling paint bolt) afterwards
(Gemini_Generated_Image_qpgagw*, 16:57: --src g22_r_paint.jpg; read 24 x 12, the pack's 20 x 10 mashed its spiral); r_canvas (the painted spiral on the ground, 3 s) came from GPT
(pack_hwei_canvas.py's prompt; Codex 2026-10-22/new-chat-4 outputs/hwei-canvas, --src g23_r_canvas.png: 14 frames on a
4 x 4 grid of 384 x 256 cells, black ground, its rows drifting a few px - each frame centred up and down, no border band
trimmed, MARGIN / VCENTRE); draw_r_canvas, the stand-in drawn here before it came, is the prompt's layout guide.
The JPGs have no alpha and backgrounds of black, white, grey, a grey gradient (slow), a painted chequerboard (q_q_ball)
and mixed cells (q_q_hit, r_burst, r_hit); every cell is keyed by flooding in from its own border. e_e_open has pure
white blocks pasted into its black ground (WHITE_BLOCKS: painted black first), r_burst one in its black first cell
(FIRST_WHITE). e_w_hit is read 26 x 48 (the pack: 20 x 40; at 20 wide its ground splash held it to 39 rows) so its eye opens
over a head, not on it. p_mark and w_pool came drawn from the
front (a round seal ring, a round pool): squashed to ground ellipses (SQUASH, the height kept of the whole picture)
before the cut. Gemini's layout: q_e_lava four rows of four (the pack's twelve frames in the first three, its last faint
cracks alone at the end of the fourth: thirteen kept), w_haste three rows of two (six frames, the pack asked four) -
all kept. The ground is keyed from the GREY border colours only (key()): his navy ink touching a cell's border was
taken for the ground and keyed out everywhere (a_ink, a_hit, slow came back empty). Symmetric from the fuller half: left to right, top to bottom for the
four projectiles the game turns with their flight (a_ink, q_q_ball, e_q_face, r_paint).
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
import process_shyvana_fx as S  # noqa: E402  effect(), key(), down() with this module's tables put in
import process_chogath_fx as PC  # noqa: E402  symmetric_tb
import process_powder_fx as PP  # noqa: E402  symmetric

OUT = os.path.join(ROOT, "assets", "source", "hwei", "codex_fx", "hwei_fx")
FLYING = {"a_ink", "q_q_ball", "e_q_face", "r_paint"}
FORWARD = set()
# (rows, columns) of the picture's grid where it is not one row of `frames` cells; the cells read row by row
LAYOUT = {"q_e_lava": (4, 4), "w_haste": (3, 2), "r_canvas": (4, 4)}
# the cells' x edges on the JPG where they are not equal (cut on the gaps between the drawings: a_ink's balls and
# e_q_face's heads reach over the equal cuts); ROWS the y edges where a grid's rows are not equal
CUTS = {"a_ink": [0, 1540, 3000, 4470, 5856], "e_q_face": [0, 1550, 2970, 4460, 5856],
        "q_e_lava": [0, 688, 1375, 2064, 2752], "r_canvas": [0, 384, 768, 1152, 1536]}
ROWS = {"q_e_lava": [0, 383, 752, 1120, 1536], "r_canvas": [0, 256, 512, 768, 1024]}
MARGIN = {"r_canvas": 0.0}    # its ovals reach within 6 px of their cells' sides: no border band trimmed
VCENTRE = {"r_canvas"}        # each frame's drawing centred up and down (GPT's rows drift a few px)
# the cells kept where not the first `frames`: q_e_lava's twelve in three rows and the faint cracks alone in the fourth
PICK = {"q_e_lava": list(range(12)) + [15]}
NEUTRAL = 18                  # a ground colour is grey: black, white, a panel, a chequerboard, a gradient (not his navy)
# keyed by saturation instead: slow's ground is a gradient from black to grey (its middle tones match neither end) and
# its puddle's darkest navy is nearly black; the ground has no colour at all, the ink is blue (holes in a blob filled)
SAT_KEY = {"slow": 9}
# a white ground also keyed where the flood from the border cannot reach: inside r_paint's spiral loops (it has no white
# of its own)
WHITE = {"r_paint"}
PALE = {"r_paint"}           # and its pale fringe squares (white ground blended into the magenta) dropped after the read
SQUASH = {"p_mark": 0.5, "w_pool": 0.36}         # front-drawn rings brought down to ground ellipses
WHITE_BLOCKS = {"e_e_open"}
FIRST_WHITE = {"r_burst": 7}                     # its first (black) cell of seven: the white in it is no drawing
# file -> (effect, frames, game size (w, h); the eye and the cloud over a head kept to their own box)
SOURCES = {
    "g00.jpg": ("a_ink", 4, (12, 6)), "g01.jpg": ("a_hit", 3, (10, 10)), "g02.jpg": ("p_mark", 6, (20, 8)),
    "g03.jpg": ("p_burst", 7, (28, 28)), "g04.jpg": ("q_q_ball", 4, (16, 8)), "g05.jpg": ("q_q_hit", 5, (20, 20)),
    "g06.jpg": ("q_w_tell", 6, (16, 24)), "g07.jpg": ("q_w_hit", 6, (24, 48)), "g08.jpg": ("q_e_lava", 13, (44, 20)),
    "g09.jpg": ("slow", 4, (16, 8)), "g10.jpg": ("e_q_face", 4, (16, 8)), "g11.jpg": ("e_q_hit", 6, (24, 24)),
    "g12.jpg": ("e_w_open", 8, (20, 14)), "g13.jpg": ("e_w_hit", 5, (26, 48)), "g14.jpg": ("e_bound", 4, (16, 16)),
    "g15.jpg": ("e_e_open", 6, (28, 24)), "g16.jpg": ("e_e_hit", 5, (28, 24)), "g17.jpg": ("w_pool", 6, (40, 16)),
    "g18.jpg": ("w_shield", 5, (22, 40)), "g19.jpg": ("w_haste", 6, (24, 8)), "g20.jpg": ("r_burst", 7, (56, 44)),
    "g21.jpg": ("r_hit", 4, (14, 14)), "g22_r_paint.jpg": ("r_paint", 4, (24, 12)),
    "g23_r_canvas.png": ("r_canvas", 14, (56, 22)),
}
KEY = {"a_ink": 26, "a_hit": 26, "e_q_face": 22, "r_paint": 30}     # white grounds: his pale pink and white cores kept
THIN = {"r_paint": 0.45, "q_w_tell": 0.35, "q_w_hit": 0.35, "a_hit": 0.25, "p_burst": 0.4, "q_q_hit": 0.4, "e_q_hit": 0.4,
        "e_w_hit": 0.4, "e_e_hit": 0.4, "w_shield": 0.35, "w_haste": 0.35, "w_pool": 0.4, "r_burst": 0.4,
        "r_hit": 0.4, "e_bound": 0.4, "e_w_open": 0.4}


def hexes(s):
    return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in s.split(", ")]


# the pack's ramps (pack_hwei_fx.py), lightest first
FIRE = hexes("#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14")
DREAD = hexes("#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060")
INK = hexes("#5A5E9A, #33366E, #1C1D44, #0E0E24")
GOLD = hexes("#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416")


_boxes = S.boxes


def setup():
    """process_shyvana_fx's functions read their module's tables: put Hwei's in (and his boxes and cells)."""
    S.FLYING, S.FORWARD, S.LAYOUT, S.KEY, S.THIN = FLYING, FORWARD, LAYOUT, KEY, THIN
    S.boxes = boxes
    S.cells_of = cells_of


def boxes(name, n, H, W):
    if name not in CUTS:
        return _boxes(name, n, H, W)
    xs = CUTS[name]
    ys = ROWS.get(name, [0, H])
    out = []
    m = MARGIN.get(name, S.OVERLAP)
    for y0, y1 in zip(ys, ys[1:]):
        my = int(m * (y1 - y0))
        for x0, x1 in zip(xs, xs[1:]):
            mx = int(m * (x1 - x0))
            out.append((y0 + my, y1 - my, x0 + mx, x1 - mx))
    return out


def key(sub, dist):
    """process_shyvana_fx.key with only GREY border colours as the ground: his ink is a dark navy (saturation 40+) that
    reaches the cells' borders (a_ink's balls, slow's puddle), and taken for the ground it went everywhere."""
    cols = S.G.border_colours(sub)
    grey = cols[cols.max(1) - cols.min(1) < NEUTRAL]
    cols = grey if len(grey) else cols
    fg = S.G.key_cell(sub, dist, cols)
    dark = cols[cols.mean(1) < 60]
    if len(dark):
        f = sub.astype(float)
        near = (((f[:, :, None, :] - dark[None, None]) ** 2).sum(-1) <= dist ** 2).any(-1)
        fg &= ~near
        fg = ndimage.binary_opening(fg, np.ones((3, 3), bool))
    return fg


def cells_of(img, name, n):
    rgb = np.asarray(img.convert("RGB"))
    H, W = rgb.shape[:2]
    out = []
    for y0, y1, x0, x1 in boxes(name, n, H, W):
        sub = rgb[y0:y1, x0:x1]
        if name in SAT_KEY:
            f = sub.astype(int)
            fg = ndimage.binary_opening(f.max(-1) - f.min(-1) >= SAT_KEY[name], np.ones((3, 3), bool))
            fg = ndimage.binary_fill_holes(fg)
        else:
            fg = key(sub, KEY.get(name, S.KEY_D))
        if name in WHITE:
            f = sub.astype(int)
            fg &= ~((f.max(-1) - f.min(-1) < 16) & (f.mean(-1) > 228))
        a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
        a4[..., :3] = sub
        a4[..., 3] = np.where(fg, 255, 0)
        if name in VCENTRE:
            a4 = S.G.centred(a4, 0)
        out.append(a4)
    return [out[i] for i in PICK[name]] if name in PICK else out[:n]


def prepared(name, img):
    """The JPG made ready for the cut: e_e_open's pasted white blocks painted black, p_mark / w_pool squashed."""
    if name in WHITE_BLOCKS:
        a = np.asarray(img.convert("RGB")).copy()
        white = a.min(-1) > 238
        lbl, _ = ndimage.label(white)
        for j, o in enumerate(ndimage.find_objects(lbl), 1):
            area = (lbl[o] == j).sum()
            box = (o[0].stop - o[0].start) * (o[1].stop - o[1].start)
            if area > 4000 and area > 0.85 * box:          # a block, not a fang's highlight
                a[o][lbl[o] == j] = 0
        img = Image.fromarray(a)
    if name in FIRST_WHITE:                                # r_burst: a white block pasted into its black first cell
        a = np.asarray(img.convert("RGB")).copy()
        x1 = a.shape[1] // FIRST_WHITE[name]
        cell = a[:, :x1]
        cell[cell.min(-1) > 238] = 0
        img = Image.fromarray(a)
    if name in SQUASH:
        img = img.resize((img.width, round(img.height * SQUASH[name])), Image.LANCZOS)
    return img


# ---------------------------------------------------------------------------------------------- drawn here
def draw_r_canvas():
    """Spiraling Despair's canvas on the ground, 56 x 22, 14 frames over 3 s: a dark indigo ink oval growing from 20
    squares wide (frame 1) to 52 x 17 (frame 6) and staying; on it magenta and orange strokes curling round the middle
    in a mirrored double spiral, thin gold strands between them, cracks of light in the middle; the strokes turn a
    little each frame; frames 12-14 brighter, the cracks white-hot, about to burst. Drawn on the right half, mirrored."""
    W, H = 56, 22
    cx, cy = (W - 1) / 2, 12.0
    A, B = 26.0, 8.5
    frames = []
    for f in range(14):
        s = 0.38 + 0.62 * min(f, 5) / 5
        hot = max(0, f - 10)                                     # 0 .. 3: the last three frames brighter
        ph = f * 0.33
        c = np.zeros((H, W, 4), np.uint8)
        for y in range(H):
            for x in range(int(math.ceil(cx)), W):
                u, v = (x - cx) / (A * s), (y - cy) / (B * s)
                r = math.hypot(u, v)
                if r > 1.0:
                    continue
                th = math.atan2(v, u)
                col = INK[2] if r < 0.88 else INK[3]
                if r < 0.55:
                    col = INK[1] if r > 0.3 else INK[2]
                # two spiral arms (magenta, orange) and a gold strand between them
                arm = ((th - 5.2 * r + ph) / (2 * math.pi) * 2) % 1.0
                if r > 0.18 and r < 0.97:
                    if arm < 0.16:
                        col = DREAD[2] if arm < 0.08 else DREAD[3]
                        if hot:
                            col = DREAD[1] if arm < 0.08 else DREAD[2]
                    elif 0.5 < arm < 0.64:
                        col = FIRE[2] if arm < 0.57 else FIRE[3]
                        if hot:
                            col = FIRE[1] if arm < 0.57 else FIRE[2]
                    elif 0.31 < arm < 0.35 or 0.81 < arm < 0.85:
                        col = GOLD[3] if not hot else GOLD[2]
                # cracks of light in the middle
                if r < 0.3 + 0.06 * hot:
                    ray = (th * 3 / math.pi + 0.5 + ph * 0.2) % 1.0
                    if ray < 0.18 + 0.06 * hot or r < 0.08 + 0.04 * hot:
                        col = GOLD[1] if not hot else GOLD[0]
                c[y, x, :3] = col
                c[y, x, 3] = 255
        frames.append(PP.symmetric(c))
    return frames


DRAWN = {}                    # draw_r_canvas stays for pack_hwei_canvas.py's layout guide


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/hw_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    setup()
    os.makedirs(S.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    work = [(fn, name, n, size) for fn, (name, n, size) in SOURCES.items()] + [(None, name, 0, None) for name in DRAWN]
    for fn, name, n, size in work:
        if fn is None:
            cells = DRAWN[name]()
            src = "drawn by tools/art/process_hwei_fx.py (Gemini left it out)"
        else:
            img = prepared(name, Image.open(S.lp(os.path.join(a.src, fn))))
            cells = S.effect(name, n, size, img)
            if name in PALE:
                for c in cells:
                    f = c[..., :3].astype(int)
                    c[(f.mean(-1) > 205) & (f.max(-1) - f.min(-1) < 80)] = 0
            src = f"gemini {fn}"
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(S.lp(os.path.join(OUT, "pixel_1x", f"hwei_fx_{name}.png")))
        entries.append({"name": name, "file": f"hwei_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "left-right", "source": src})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(S.lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images; r_canvas by GPT), "
                   "processed by tools/art/process_hwei_fx.py"}, f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 5
        rows = []
        for name, s, w in sheets:
            n = s.shape[1] // w
            im = Image.new("RGBA", ((s.shape[1] + 2 * n) * Z, s.shape[0] * Z), (40, 40, 52, 255))
            for k in range(n):
                cell = s[:, k * w:(k + 1) * w]
                bg = Image.new("RGBA", (w * Z, s.shape[0] * Z), (70, 74, 60, 255))
                bg.alpha_composite(Image.fromarray(cell).resize((w * Z, s.shape[0] * Z), Image.NEAREST))
                im.alpha_composite(bg, (k * (w + 2) * Z, 0))
            rows.append((name, im))
        W = max(r.width for _, r in rows) + 110
        sheet = Image.new("RGBA", (W, sum(r.height + 12 for _, r in rows)), (20, 20, 26, 255))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.alpha_composite(r, (110, y))
            d.text((4, y + 4), name, fill=(255, 255, 255, 255))
            y += r.height + 12
        path = os.path.join(a.review, "hwei_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
