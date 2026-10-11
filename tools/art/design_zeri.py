#!/usr/bin/env python3
"""Zeri's game-size design (step 1) from Codex's generator drafts (assets/source/zeri/codex_model/raw).

    python tools/art/design_zeri.py --options OUT_DIR          # every draft at 40 and 42 rows + Codex's own A / B
    python tools/art/design_zeri.py --tryn B1 42 --tryn-out x.png
    python tools/art/design_zeri.py --final [--check]          # PICK -> assets/source/native/zeri_native.png

How it came about (2026-10-11): the user picked Codex's picture A (League's Idle: the rifle upright at her image-right
shoulder, the other arm hanging). Codex's step 1 drew three generator drafts (raw/zeri_A_attempt1/2.png,
zeri_B_attempt1.png, about 37-40 x 62-63 squares on their own ~19 px grids) and cut draft B1 down itself (its own
zeri_design_A/B: 30 x 40 / 32 x 42). Here league_tryndamere's way (design_syndra.tryn, the user's 「就按照那种方式」 for
Syndra): a draft read on its own grid, its own 24 colours, whole rows and columns dropped where least is lost, the
face kept, only the outline closed; the figure placed with its soles on row 99 and the middle of its feet on column 64.
The user picked Codex's own codex_B (32 x 42), then asked for a smaller head, a smaller figure and no muddy spots: polish()
gave p35c (28 x 36), Codex redrew it clean (step 1b) and that redraw is final: --final copies it (plus FIXES).

Then (2026-10-11) the user: 「而且我感觉有点丑 头有点大 身体做的不好」 and gave their own picture of her
(assets/source/zeri/user_ref/zeri_user.png): 「你拿这版泽丽 一点点还原吧 还原到完美」, 40 rows. The picture was
block-voted at 40 rows (each square its commonest non-black colour, outline only where half of it is ink), the face
kept at the picture's own size and every detail kept, then finished square by square (design40/zeri40_v5.txt; the user:
「眼睛嘴巴做的不太像泽丽 其他都挺好的」). Codex redrew the face box alone (rows 8-15 x columns 7-14, pack
tools/art/pack_zeri_face.py, delivery codex_face/); the user picked take C 「深绿瞳+收敛嘴」 -> design40/zeri40_final.txt,
which --final now writes (palette design40/palette.json, the 24 x 40 table at x 53 / y 60: soles on row 99).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips  # noqa: E402
from regrid import regrid  # noqa: E402
import design_rengar as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zeri", "codex_model")
RAW = {"A1": "raw/zeri_A_attempt1.png", "A2": "raw/zeri_A_attempt2.png", "B1": "raw/zeri_B_attempt1.png"}
OUT = os.path.join(ROOT, "assets", "source", "native", "zeri_native.png")
K = 24
PICK = "codex_refine"  # the user's final pick (2026-10-11, 「定稿 refine」): Codex's clean redraw at p35c's size (step 1b,
                       # codex_refine/zeri_refine_1x.png, 28 x 36, 19 colours), after codex_B (32 x 42) had too big a head
# the user, on the final pick: 「枪要补齐吧」 - its rifle stopped two rows under the buns with one electrode left uncapped;
# rows 62-70, columns 73-77 redrawn as the picture's rifle: two capped electrodes, the silver muzzle, the lime and orange
# body (rows 71 down untouched). None = transparent.
_GUN = {"a": "#100C14", "r": "#C8CCD6", "n": "#B4E01E", "h": "#7A9A08", "m": "#F6A418", "q": "#E8FA5A", ".": None}
_GUN_ROWS = [".a.a.", "arara", "arrra", "anrra", "ahrra", "ammra", "anmma", "anqma", "anqma"]
FIXES = [(62 + r, 73 + c, _GUN[ch]) for r, row in enumerate(_GUN_ROWS) for c, ch in enumerate(row)]
# then 「杂乱的黑色像素得清理吧 保持干净啊人物」 (the user's crop: between the hair and the rifle): the hair's outline and
# the rifle's ran side by side with a 1-square transparent slit between them (rows 74-78, column 70) and the hair's edge
# had no outline at rows 69 and 71 - the hair now runs on to the rifle's own single outline
_H, _N = "#7A9A08", "#B4E01E"
FIXES += [(68, 72, "#100C14"),
          (69, 70, _N), (69, 71, _N), (69, 72, _H), (70, 70, _N), (70, 71, _H), (70, 72, _H), (71, 70, _H), (71, 71, _H),
          (72, 70, _H), (73, 69, _H), (73, 70, _H)]
FIXES += [(y, x, _H) for y in range(74, 79) for x in (69, 70)]
FIXES += [(80, 71, "#100C14")]


def read(v):
    """A draft on its own grid (regrid measures the square), cropped, hard alpha."""
    raw, _, _ = regrid(np.asarray(Image.open(R.lp(os.path.join(SRC, RAW[v]))).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def face_box(raw):
    """The face's rows and columns on a read-back: the biggest blob of peach skin in the upper half, one square more
    round it (the eyes and the plaster sit inside the skin)."""
    r, g, b, a = (raw[..., i].astype(int) for i in range(4))
    skin = (a > 0) & (r > 200) & (g > 130) & (g < 215) & (b > 90) & (b < 185) & (r - g > 20) & (r - g < 95)
    skin[raw.shape[0] // 2:] = False
    seen = np.zeros_like(skin)
    best = []
    for y0, x0 in zip(*np.nonzero(skin)):
        if seen[y0, x0]:
            continue
        stack, comp = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < skin.shape[0] and 0 <= nx < skin.shape[1] and skin[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if len(comp) > len(best):
            best = comp
    ys, xs = zip(*best)
    return range(max(1, min(ys) - 1), max(ys) + 2), range(max(0, min(xs) - 1), max(xs) + 2)


def on_canvas(fig):
    fig = R.crop(fig)
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = R.SOLE_ROW + 1 - fig.shape[0], int(round(R.MID_COL - (feet.min() + feet.max()) / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def tryn(v, height):
    import design_riven as DR
    import design_varus as dv
    raw = read(v)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    fr_, fc_ = face_box(raw)
    face = range(fr_.start - 1, fr_.stop - 1)
    rows = [0] + [r + 1 for r in DR.keep_axis([idx[y] for y in range(1, H)], height - 1, face)]
    sub = idx[rows]
    cols = DR.keep_axis([sub[:, x] for x in range(W)], round(W * height / H), fc_)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in fr_ if r in rows]
    fc = [cols.index(c) for c in fc_ if c in cols]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    ink = tuple(int(c) for c in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    return on_canvas(R.crop(can)), rows, cols, added, (raw.shape, fr_, fc_)


# The user on codex_B (2026-10-11): 「你还得精修啊 头太大了」「整体模型尺寸也太大了」「还有好多模糊的地方」: its head (bun tips to
# chin) was 21 of its 42 rows. refine() cuts draft B1 (the same draft) band by band: the buns, the face and the body each
# keep their own number of rows (the face's eyes whole), the columns in proportion over the whole figure (the face's eyes
# whole), fewer colours (K), lone squares merged into the colour round them, then only the outline closed.
BANDS = {"B1": ((0, 14), (14, 29), (29, 62))}      # draft rows: the buns, the face (brow to chin), the body
EYES = {"B1": (range(15, 18), range(14, 23))}       # draft rows / columns of the eyes and the plaster (never cut)


REFINES = {
    "r38": dict(keep=(5, 9, 24), width=25, k=18),
    "r38b": dict(keep=(4, 9, 25), width=24, k=16),
    "r40": dict(keep=(5, 10, 25), width=26, k=18),
    "r36": dict(keep=(4, 9, 23), width=23, k=16),
}


def idle(hero):
    """A pack hero's first idle frame on the 128 canvas (soles on row 99, feet centred), for size."""
    import tfm2_ase
    sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA")).copy()
    f[..., 3] = np.where(f[..., 3] > 127, 255, 0)
    return on_canvas(f)


def best_pick(lines, n_out):
    import design_riven as DR
    if n_out >= len(lines):
        return list(range(len(lines)))
    best = None
    for off in range(3):
        k, lost = DR.pick(lines, n_out, off)
        if k is not None and (best is None or lost < best[1]):
            best = (k, lost)
    return best[0]


def despeckle(idx):
    """A square none of whose 8 neighbours has its colour, with three or four of its 4 neighbours alike, takes theirs."""
    out = idx.copy()
    H, W = idx.shape
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            v = idx[y, x]
            if v < 0:
                continue
            ring = [idx[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if v in ring:
                continue
            four = [idx[y - 1, x], idx[y + 1, x], idx[y, x - 1], idx[y, x + 1]]
            vals, cnt = np.unique([f for f in four if f >= 0], return_counts=True)
            if len(cnt) and cnt.max() >= 3:
                out[y, x] = vals[cnt.argmax()]
                n += 1
    return out, n


def thin_ink(idx, ink, protect):
    """Dark specks inside an area: an inner near-black square whose two opposite neighbours (left and right, or up and
    down) share one other colour takes it - the 「脏的黑色素」 the user had cleaned off Syndra; never in `protect`."""
    out = idx.copy()
    H, W = idx.shape
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if idx[y, x] != ink or protect[y, x]:
                continue
            four = [idx[y - 1, x], idx[y + 1, x], idx[y, x - 1], idx[y, x + 1]]
            if min(four) < 0:
                continue
            for a_, b_ in ((idx[y, x - 1], idx[y, x + 1]), (idx[y - 1, x], idx[y + 1, x])):
                if a_ == b_ and a_ != ink:
                    out[y, x] = a_
                    n += 1
                    break
    return out, n


# inner dark lines in each material's own darkest shade (art-spec: one near-black outline round the figure, very few
# inner dark lines): an inner near-black square whose opaque neighbours (at least 5 of 8 not near-black) are all one
# material takes that material's darkest shade
MATERIAL = {
    "lime": (("#EAFB2A", "#BCDE04", "#A9CA02"), "#A9CA02"),
    "teal": (("#0094BA", "#006796", "#014774", "#002B4E", "#1A2760"), "#002B4E"),
    "maroon": (("#792850", "#56173D"), "#56173D"),
    "boots": (("#A14633", "#43201C", "#AF3E12", "#FC9300", "#FBA500"), "#43201C"),
}


def soften_ink(idx, pal, ink, protect):
    fam = {}
    for name, (members, dark) in MATERIAL.items():
        for h in members:
            hit = np.nonzero((pal == R.hx(h)).all(1))[0]
            if len(hit):
                fam[int(hit[0])] = (name, int(np.nonzero((pal == R.hx(dark)).all(1))[0][0]))
    out = idx.copy()
    H, W = idx.shape
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if idx[y, x] != ink or protect[y, x]:
                continue
            ring = [idx[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if min(ring) < 0:
                continue
            other = [v for v in ring if v != ink]
            if len(other) < 5 or any(v not in fam for v in other):
                continue
            names = {fam[v][0] for v in other}
            if len(names) == 1:
                out[y, x] = fam[other[0]][1]
                n += 1
    return out, n


def refine(v="B1", keep=(5, 9, 24), width=25, k=18):
    import design_riven as DR
    import design_varus as dv
    raw = read(v)
    idx, pal = dv.kmeans(raw, k)
    H, W = idx.shape
    rows = []
    er, ec = EYES[v]
    for (lo, hi), n_keep in zip(BANDS[v], keep):
        part = list(range(lo, min(hi, H)))
        lines = [idx[y] for y in part]
        if lo <= er.start < hi:
            prot = range(er.start - lo, er.stop - lo)
            kept = DR.keep_axis(lines, n_keep, prot)
        else:
            kept = best_pick(lines, n_keep)
        rows += [part[i] for i in kept]
    sub = idx[rows]
    cols = DR.keep_axis([sub[:, x] for x in range(W)], width, ec)
    small = idx[np.ix_(rows, cols)]
    small, merged = despeckle(small)
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keepm = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in er if r in rows]
    fc = [cols.index(c) for c in ec if c in cols]
    keepm[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    ink = tuple(int(c) for c in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=ink, feet=fig.shape[0], keep=np.pad(keepm, 1))
    return on_canvas(R.crop(can)), merged, added


# polish(): the same three wishes on the user's pick itself (codex_B, 32 x 42): its rows cut band by band - the buns
# (rows 0-7), the face (8-20; the eyes, rows 12-15, whole), the body (21-41) - its columns cut over the whole figure
# (the face's columns 11-23 whole), near colours merged (MERGE), lone squares merged into the colour round them
# (outside the face), then only the outline closed.
CB_BANDS = ((0, 8), (8, 21), (21, 42))
CB_EYES = (range(12, 16), range(11, 24))
MERGE = {"#FDE846": "#FDE02C", "#0076A2": "#006796", "#57372C": "#43201C", "#32071F": "#56173D"}
POLISH = {
    "p36": dict(keep=(5, 10, 21), width=27),
    "p35": dict(keep=(4, 10, 21), width=27),
    "p34": dict(keep=(4, 9, 21), width=26),
    "p33": dict(keep=(4, 9, 20), width=26),
    "p35c": dict(keep=(4, 10, 21), width=27, thin=True),
    "p34c": dict(keep=(4, 9, 21), width=26, thin=True),
}


def polish(keep=(5, 10, 21), width=27, thin=False):
    import design_riven as DR
    a = np.asarray(Image.open(os.path.join(SRC, "zeri_design_B_1x.png")).convert("RGBA"))[58:100, 48:80].copy()
    for src, dst in MERGE.items():
        m = (a[..., :3] == R.hx(src)).all(-1) & (a[..., 3] > 0)
        a[m, :3] = R.hx(dst)
    pal = sorted({tuple(int(v) for v in c) for c in a[a[..., 3] > 0][:, :3]})
    lut = {c: i for i, c in enumerate(pal)}
    idx = np.full(a.shape[:2], -1)
    for y, x in zip(*np.nonzero(a[..., 3])):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]
    pal = np.array(pal, np.uint8)
    er, ec = CB_EYES
    rows = []
    for (lo, hi), n_keep in zip(CB_BANDS, keep):
        part = list(range(lo, hi))
        lines = [idx[y] for y in part]
        if lo <= er.start < hi:
            kept = DR.keep_axis(lines, n_keep, range(er.start - lo, er.stop - lo))
        else:
            kept = best_pick(lines, n_keep)
        rows += [part[i] for i in kept]
    sub = idx[rows]
    cols = DR.keep_axis([sub[:, x] for x in range(idx.shape[1])], width, ec)
    small = idx[np.ix_(rows, cols)]
    fr = [rows.index(r) for r in range(8, 21) if r in rows]
    fc = [cols.index(c) for c in ec if c in cols]
    face = small[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1].copy()
    small, merged = despeckle(small)
    small[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = face
    if thin:
        prot = np.zeros(small.shape, bool)
        prot[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
        small, thinned = thin_ink(small, lut[R.hx("#100C14")], prot)
        small, softened = soften_ink(small, pal, lut[R.hx("#100C14")], prot)
        merged += thinned + softened
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keepm = np.zeros(m.shape, bool)
    keepm[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=R.hx("#100C14"), feet=fig.shape[0], keep=np.pad(keepm, 1))
    return on_canvas(R.crop(can)), merged, added


def sheet(figs, path, z=8):
    """Options side by side at z x on one soles line, labelled, plus each at 1x below."""
    boxes = [Image.fromarray(f).getbbox() for _, f in figs]
    top = min(b[1] for b in boxes)
    pad = 16
    cells = []
    for (name, f), b in zip(figs, boxes):
        crop = Image.fromarray(f).crop((b[0] - 1, top - 1, b[2] + 1, 100))
        cells.append((name, crop, f"{b[2] - b[0]}x{b[3] - b[1]}"))
    w = sum(c.width * z + pad for _, c, _ in cells) + pad
    h = max(c.height for _, c, _ in cells) * z + 2 * pad + 60
    img = Image.new("RGBA", (w, h), (232, 232, 226, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for name, c, size in cells:
        big = c.resize((c.width * z, c.height * z), Image.NEAREST)
        img.alpha_composite(big, (x, pad))
        img.alpha_composite(c, (x, pad + big.height + 22))
        d.text((x, pad + big.height + 4), f"{name}  {size}", fill=(0, 0, 0, 255))
        x += big.width + pad
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", metavar="OUT_DIR")
    ap.add_argument("--tryn", nargs=2, metavar=("DRAFT", "ROWS"))
    ap.add_argument("--tryn-out")
    ap.add_argument("--refine", metavar="OUT_DIR", help="the smaller-head options (band cuts, fewer colours)")
    ap.add_argument("--polish", metavar="OUT_DIR", help="codex_B with a smaller head, narrower, cleaned")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.options:
        os.makedirs(a.options, exist_ok=True)
        figs = []
        for v in ("A/B", ):
            for name in ("A", "B"):
                c = np.asarray(Image.open(os.path.join(SRC, f"zeri_design_{name}_1x.png")).convert("RGBA")).copy()
                figs.append((f"codex_{name}", c))
        for v in RAW:
            for h in (40, 42):
                can, rows, cols, added, info = tryn(v, h)
                Image.fromarray(can).save(os.path.join(a.options, f"zeri_{v}_{h}.png"))
                figs.append((f"{v}->{h}", can))
                print(f"{v} {h}: read-back {info[0][:2]} face rows {info[1].start}-{info[1].stop - 1} cols "
                      f"{info[2].start}-{info[2].stop - 1}, outline +{added}")
        sheet(figs, os.path.join(a.options, "zeri_design_options.png"))
    if a.refine:
        os.makedirs(a.refine, exist_ok=True)
        figs = [("codex_B", np.asarray(Image.open(os.path.join(SRC, "zeri_design_B_1x.png")).convert("RGBA")).copy())]
        for name, kw in REFINES.items():
            can, merged, added = refine(**kw)
            Image.fromarray(can).save(os.path.join(a.refine, f"zeri_{name}.png"))
            figs.append((name, can))
            print(name, kw, "merged", merged, "outline +", added)
        for h in ("syndra", "seraphine", "samira", "twitch"):
            figs.append((h, idle(h)))
        sheet(figs, os.path.join(a.refine, "zeri_refine_options.png"))
    if a.polish:
        os.makedirs(a.polish, exist_ok=True)
        figs = [("codex_B", np.asarray(Image.open(os.path.join(SRC, "zeri_design_B_1x.png")).convert("RGBA")).copy())]
        for name, kw in POLISH.items():
            can, merged, added = polish(**kw)
            Image.fromarray(can).save(os.path.join(a.polish, f"zeri_{name}.png"))
            figs.append((name, can))
            print(name, kw, "merged", merged, "outline +", added)
        for h in ("syndra", "samira", "twitch", "jinx"):
            figs.append((h, idle(h)))
        sheet(figs, os.path.join(a.polish, "zeri_polish_options.png"))
    if a.tryn:
        can, rows, cols, added, info = tryn(a.tryn[0], int(a.tryn[1]))
        Image.fromarray(can).save(R.lp(a.tryn_out))
        print(a.tryn, info[0], "outline", added)
    if a.final:
        import json
        d40 = os.path.join(ROOT, "assets", "source", "zeri", "design40")
        pal = json.load(open(os.path.join(d40, "palette.json")))
        rows = open(os.path.join(d40, "zeri40_final.txt")).read().splitlines()[:40]
        can = np.zeros((128, 128, 4), np.uint8)
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch in pal:
                    can[60 + y, 53 + x, :3] = R.hx(pal[ch])
                    can[60 + y, 53 + x, 3] = 255
        bb = Image.fromarray(can).getbbox()
        cols = len({tuple(c) for c in can[can[..., 3] > 0][:, :3]})
        msg = f"{bb[2] - bb[0]} x {bb[3] - bb[1]} box {bb}, {cols} colours"
        if a.check:
            old = np.asarray(Image.open(R.lp(OUT)).convert("RGBA"))[4::8, 4::8]
            print("identical" if np.array_equal(old, can) else "DIFFERENT", msg)
        else:
            Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(R.lp(OUT))
            print("wrote", OUT, msg)

if __name__ == "__main__":
    main()
