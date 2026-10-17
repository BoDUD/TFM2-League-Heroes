#!/usr/bin/env python3
"""Sion's game-size designs (1x) from Codex's step-1 raw drafts, by whole-row / whole-column cuts (Nautilus's way).

    python tools/art/design_sion.py --sheet OUT.png        # the cuts beside Codex's own finals and the pack's heroes
    python tools/art/design_sion.py --cut                  # design/front_cut.txt: the cut + tidy() as a letter table
    python tools/art/design_sion.py --write                # design/front.png from the hand-finished design/front.txt
    python tools/art/design_sion.py --hd                   # hd/front.png: the PPU 1.5 design the user picked

How it came about (2026-10-14): the user picked picture A (the axe hanging by the near leg) at 44 rows crown to soles.
Codex's step 1 (codex_model/) drew its finals with a script on the 80 x 53 grid: blocky flat muscles, a side view with
the legs and the axe tangled. Its raw generated drafts (codex_model/raw/*-generated.png) are clean pixel art on ~12-px
(front) and ~9-px (side) squares. As for league_nautilus (design_nautilus.py, the user: 「用这个吧 感觉这个最还原」), every
kept square is the draft's own:
  1. the raw read back on its own grid (the skill's regrid.py, alpha >= 128);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, seed 1);
  3. rows by design_riven.keep_axis (rows most like a neighbour go, three offsets, the least loss kept), never the
     face's rows; then the columns the same, the width in proportion, never the face's columns;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. the front tidied (tidy()): the far eye one red square wide like the near one's rows (the cut left it orange and
     dark), the ribbon's bright red moved off the eyes' red, lone specks (a square none of its 8 neighbours share,
     5 or more of them one colour) taken by that colour, the scar dashes of one or two squares the cuts left on the
     skin taken by the skin - the face and the furnace kept.
  6. finished by hand in a letter table (design/front.txt + palette.json, one letter a square), after an independent
     reviewer's list (2026-10-14: 「NOT YET」 - the near fist lost to the column cuts, the belt and both boots dark
     noise, the boots' tones swapped, open outlines): the near fist redrawn round the haft (rows 30-33), the belt
     redrawn (two round buckles, the furnace, the grille under it), both boots redrawn (the near one lit, the far one a
     shade darker and its sole a row higher, a spike on it), the pauldron's lone black squares filled and its edges
     lit, a row added on top (the blade's hilt capped) and a column on the right (the gauntlet's outline);
     --write closes the outline (strips.complete_outline) and writes front.png.
Front: 44 rows crown to soles (the user picked this cut over Codex's own finals, 2026-10-14).
Then the user: 「用PPU优化一下 调稍微清晰一点」 and picked PPU 1.5 from a true-size sheet: the raw draft is 67 rows crown to
soles = 44 game rows at PPU 1.52, so hd/front.png is the draft itself square for square (hd()): HD_K colours of its own
(design_varus.kmeans), two majority passes (pixel_down._majority: a lone square takes the colour 4+ of its 8 neighbours
share), the outline closed (dark 45), the enclosed specks of the bone ring filled with outline. The 1x design (front.png)
stays for the 1x frames the game falls back on. The side view was
dropped by the user (「不要侧面，全用 3/4 正面」): every action is drawn from the front. Side: the same scale as the front, measured belt (the furnace) to soles.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
import tfm2_ase  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sion", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "sion", "design")
K = 24
TARGET = 44                      # crown to soles, the user's pick
# raw draft -> crown row (the head's outline top), soles row, furnace row, the face's rows / columns (read-back grid)
DRAFTS = {
    "front2": dict(raw="sion-front-2-generated.png", crown=8, soles=74, furnace=41,
                   face_rows=range(11, 20), face_cols=range(52, 64)),
    "front1": dict(raw="sion-front-1-generated.png", crown=8, soles=74, furnace=41,
                   face_rows=range(11, 20), face_cols=range(58, 70)),
    "side2": dict(raw="sion-side-2-generated.png", soles=107, furnace=56,
                  face_rows=range(20, 30), face_cols=range(76, 92)),
}
NEIGHBOURS = ["darius", "nautilus", "alistar", "renekton"]


def read_back(name):
    path = os.path.join(SRC, "raw", DRAFTS[name]["raw"])
    raw, _, _ = regrid(np.asarray(Image.open(path).convert("RGBA")))
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def scale(name):
    """Kept rows per draft row: the front by crown -> soles = TARGET, the side by the front2's furnace -> soles."""
    d = DRAFTS[name]
    if "crown" in d:
        return TARGET / (d["soles"] - d["crown"] + 1)
    f = DRAFTS["front2"]
    return scale("front2") * (f["soles"] - f["furnace"]) / (d["soles"] - d["furnace"])


def build(name):
    d = DRAFTS[name]
    raw = read_back(name)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    s = scale(name)
    rows = R.keep_axis([idx[y] for y in range(H)], round(H * s), d["face_rows"])
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], round(W * s), d["face_cols"])
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in d["face_rows"] if r in rows]
    fc = [cols.index(c) for c in d["face_cols"] if c in cols]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    return trimmed(can)


RIBBON_RED = (214, 34, 38)
SCAR_REDS = [(70, 23, 37), (111, 39, 37)]


def tidy(fig):
    """The front's finish (step 5). Coordinates are the trimmed front2 cut's (kmeans seed 1, deterministic)."""
    a = fig.copy()
    eye = a[10, 37].copy()                       # the near eye's red (2 x 2 at rows 10-11, columns 37-38)
    for y in (10, 11):
        a[y, 41] = eye                           # the far eye: one square wide, the same rows
    a[10, 42] = a[11, 42]                        # the orange / dark leftover beside it -> the cheek
    red = (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - eye[:3].astype(int)).sum(-1) == 0)
    red[10:12, 36:43] = False
    a[red, :3] = RIBBON_RED
    keep = np.zeros(a.shape[:2], bool)
    keep[8:16, 32:45] = True                     # the face
    furnace = (a[..., 0].astype(int) > 200) & (a[..., 3] > 0)
    keep |= furnace
    dark = (a[..., :3].astype(int) * [299, 587, 114]).sum(-1) < 30000
    H, W = a.shape[:2]
    for _ in range(2):
        b = a.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if keep[y, x] or a[y, x, 3] == 0 or dark[y, x]:
                    continue
                me = tuple(a[y, x, :3])
                nb = [tuple(a[y + dy, x + dx, :3]) if a[y + dy, x + dx, 3] else None
                      for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
                if me in nb or None in nb:
                    continue
                best = max(set(nb), key=nb.count)
                if nb.count(best) >= 5:
                    b[y, x, :3] = best
        a = b
    # the scars' dark reds: the row cuts broke the draft's scar lines into dashes of one or two squares that read as
    # specks on the skin -> each takes the skin colour most of its neighbours have; longer marks (the neck's shadow,
    # the belt's edge) stay
    scar = np.zeros(a.shape[:2], bool)
    for c in SCAR_REDS:
        scar |= (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - c).sum(-1) <= 6)
    lab, n = ndimage.label(scar & ~keep, np.ones((3, 3)))
    b = a.copy()
    for i in range(1, n + 1):
        part = lab == i
        if part.sum() > 2:
            continue
        for y, x in zip(*np.nonzero(part)):
            nb = [tuple(a[yy, xx, :3]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                  if 0 <= yy < H and 0 <= xx < W and a[yy, xx, 3] and not scar[yy, xx] and not dark[yy, xx]]
            if len(nb) >= 3:
                b[y, x, :3] = max(set(nb), key=nb.count)
    # cracks the cuts closed in (enclosed clear runs of 3 squares or fewer: between two pauldron horns, beside the
    # axe hand) -> outline; the armpit's opening (24 squares) is the draft's own and stays; then the outline closed
    out = tuple(int(v) for v in b[0:3, :, :3][b[0:3, :, 3] > 0][0])
    lab, n = ndimage.label(b[..., 3] == 0)
    border = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    for i in range(1, n + 1):
        if i not in border and (lab == i).sum() <= 3:
            b[lab == i, :3] = out
            b[lab == i, 3] = 255
    can = np.pad(b, ((1, 1), (1, 1), (0, 0)))
    can = strips.complete_outline(can, color=out, feet=b.shape[0], keep=np.pad(keep, 1))[0]
    b = trimmed(can)
    return b


LETTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HD_K = 28
HD_PPU = 1.52                    # 67 draft rows / 44 game rows


def hd():
    """The PPU design: the front2 draft square for square (see the module's notes)."""
    import pixel_down as pd
    raw = read_back("front2")
    idx, pal = dv.kmeans(raw, HD_K)
    a = np.zeros_like(raw)
    m = idx >= 0
    a[m, :3] = pal[idx[m]]
    a[m, 3] = 255
    for _ in range(2):
        a = pd._majority(a, a[..., 3] > 0, np.zeros(m.shape, bool))
    out = tuple(int(v) for v in pal[int(np.argmin(pal.sum(1)))])
    can = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    can = strips.complete_outline(can, color=out, feet=a.shape[0], dark=45)[0]
    lab, n = ndimage.label(can[..., 3] == 0)
    border = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    for i in range(1, n + 1):
        if i not in border and (lab == i).sum() <= 4:
            can[lab == i, :3] = out
            can[lab == i, 3] = 255
    return trimmed(can)


def table(name):
    """A letter table (design/<name>.txt) with design/palette.json -> RGBA."""
    pal = json.load(open(os.path.join(OUT, "palette.json")))
    rows = open(os.path.join(OUT, name + ".txt")).read().splitlines()
    a = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".":
                a[y, x, :3] = [int(pal[ch][i:i + 2], 16) for i in (1, 3, 5)]
                a[y, x, 3] = 255
    return a


def finished():
    """The hand-finished front: front.txt, the outline closed round light squares (the face box kept)."""
    a = table("front")
    keep = np.zeros(a.shape[:2], bool)
    keep[9:17, 32:45] = True
    out = (8, 7, 7)                              # the outline colour (palette "0")
    can = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    can = strips.complete_outline(can, color=out, feet=a.shape[0], keep=np.pad(keep, 1), dark=45)[0]   # dark 45: the dark irons and browns get an outline too
    return can[1:-1, 1:-1]


def idle(hero):
    sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}#sheet.png"))
    f = sp.frames[sp.tag_frames("idle")[0]]
    return trimmed(np.asarray(f))


def trimmed(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sheet(path):
    shots = []
    for v in ("front-1", "front-2", "side-1", "side-2"):
        shots.append((f"codex {v}", trimmed(np.asarray(Image.open(os.path.join(SRC, f"sion-{v}_1x.png")).convert("RGBA")))))
    for name in DRAFTS:
        a = build(name)
        shots.append((f"cut {name} {a.shape[1]}x{a.shape[0]}", a))
    for hero in NEIGHBOURS:
        a = idle(hero)
        shots.append((f"{hero} {a.shape[1]}x{a.shape[0]}", a))
    tall = max(a.shape[0] for _, a in shots)
    big, pad = 4, 6
    w2 = sum(a.shape[1] * 2 + pad for _, a in shots) + pad
    w4 = sum(max(a.shape[1] * big, 150) + pad * 3 for _, a in shots) + pad * 3
    img = Image.new("RGBA", (max(w2, w4), tall * 2 + tall * big + 70), (205, 205, 205, 255))
    dr = ImageDraw.Draw(img)
    x = pad
    for _, a in shots:
        im = Image.fromarray(a).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST)
        img.alpha_composite(im, (x, tall * 2 - im.height + 4))
        x += im.width + pad
    y4, x = tall * 2 + 20, pad * 3
    for name, a in shots:
        im = Image.fromarray(a).resize((a.shape[1] * big, a.shape[0] * big), Image.NEAREST)
        img.alpha_composite(im, (x, y4 + tall * big - im.height))
        dr.text((x, y4 + tall * big + 6), name, fill=(0, 0, 0, 255))
        x += max(im.width, 150) + pad * 3
    img.convert("RGB").save(path)
    print("wrote", path, img.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--cut", action="store_true")
    ap.add_argument("--hd", action="store_true")
    ap.add_argument("--front", default="front2", help="the draft to cut (tidy()'s coordinates are front2's)")
    a = ap.parse_args()
    if a.sheet:
        sheet(a.sheet)
    if a.cut:
        a_ = tidy(build(a.front))
        cols = sorted({tuple(int(v) for v in p[:3]) for p in a_[a_[..., 3] > 0]}, key=sum)
        lut = {c: LETTERS[i] for i, c in enumerate(cols)}
        rows = ["".join(lut[tuple(int(v) for v in a_[y, x, :3])] if a_[y, x, 3] else "." for x in range(a_.shape[1]))
                for y in range(a_.shape[0])]
        open(os.path.join(OUT, "front_cut.txt"), "w").write("\n".join(rows) + "\n")
        print("wrote design/front_cut.txt (palette letters by brightness, as palette.json)")
    if a.write:
        Image.fromarray(finished()).save(os.path.join(OUT, "front.png"))
        print("wrote design/front.png")
    if a.hd:
        path = os.path.join(os.path.dirname(OUT), "hd", "front.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.fromarray(hd()).save(path)
        print("wrote hd/front.png")


if __name__ == "__main__":
    main()
