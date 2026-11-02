#!/usr/bin/env python3
"""The Cinderling's (绯红树怪) effects from the user's Gemini sheet (2026-11-02, 「特效让gemini生成了 你处理一下就能用了
还有技能图标」): every picture cleaned into game-size frames the import reads (pixel_1x + manifest.json, Codex's
delivery shape) - clean_krug_fx.py's way, but from ONE sheet.

    python tools/art/clean_cinderling_fx.py [--review out.png]

The source: assets/source/cinderling/gemini_fx/cinderling_fx_sheet.jpg (2400 x 1792 JPEG on a flat dark grey, every
effect of PROMPTS_FX.md with its label, mostly ONE or two drawings an effect, not frames; the three icons at the
bottom). PIECES are the drawings' boxes on it (read off a box-detection pass, labels left out; a white label crossing a
box is masked out as near-white grey). Per piece: the drawing = what differs from the background by more than BG_DIFF;
FIRE_ONLY pieces keep only the fire's colours (r_cast's critter inside its flames, p_full's leaf bush: the critter
draws its own body and leaves). Each frame of an effect (FRAMES) is a piece brought to the effect's game cell (one scale
fitting the cell less a margin, times the frame's own `k`; each square drawn when KEEP of its block is, its colour the
block's median), snapped to the pack's ramps (pack_cinderling_fx: FIRE LEAF WOOD BARK DIRT + a near-black outline, the
squares darker than DARK dropped from fire), then made symmetric (the flying leaves turned to point right first and
mirrored top to bottom; every other picture left to right: the client never mirrors an effect picture) and shaped
by its ops: "dim" (every colour a step down its ramp), "sparse" (every other drawn square of a fixed checker gone: the
fade-out), "up<n>" (n rows higher: rising embers, the bob).
The three icons: each tile (its bright frame, the label under it cut off) brought to 64 x 64 (LANCZOS).
Writes assets/source/cinderling/gemini_fx/clean/pixel_1x/cinderling_fx_<name>.png, cinderling_icon_<slot>.png and
manifest.json.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_cinderling_fx as PF  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "cinderling", "gemini_fx")
SHEET = os.path.join(SRC, "cinderling_fx_sheet.jpg")
OUT = os.path.join(SRC, "clean")
BG = np.array([46, 47, 52])
BG_DIFF = 30
KEEP = 0.35
DARK = 48
OUTLINE = (24, 16, 20)

# piece -> (box on the sheet, options): fire = keep only the fire's colours; cut = boxes (sheet px) cleared
PIECES = {
    "leaf_big": ((795, 118, 935, 262), {}),
    "leaf_mid": ((635, 150, 755, 262), {}),
    "hit_small": ((1100, 140, 1265, 270), {}),
    "slash": ((1325, 112, 1615, 276), {}),
    "crown": ((1960, 128, 2370, 320), {"fire": True}),
    "spiral": ((60, 445, 350, 705), {}),
    "fan": ((460, 436, 782, 684), {}),
    "split": ((925, 482, 1228, 646), {}),
    "flame_a": ((1945, 520, 2080, 706), {}),
    "flame_b": ((2140, 505, 2280, 706), {}),
    "dig": ((60, 836, 545, 990), {}),
    "clods": ((575, 785, 1035, 1036), {}),
    "burst": ((1300, 745, 1724, 1036), {}),
    "mud": ((1902, 840, 2305, 1036), {}),
    "rcast": ((122, 1150, 575, 1485), {"fire": True, "cut": [(285, 1285, 500, 1470)]}),
    "blaze": ((758, 1262, 1198, 1418), {}),   # only the swirl's front arc: mirrored whole it made a face on top
    "rleaf_a": ((1583, 1105, 1765, 1220), {}),
    "rleaf_b": ((1417, 1121, 1603, 1215), {}),
    "rleaf_c": ((1367, 1206, 1520, 1358), {}),
    "spark_s": ((1935, 1142, 2080, 1290), {}),
    "spark_b": ((2093, 1200, 2292, 1410), {}),
}
# the flying pieces: the long axis turned level, the flaming end (the tail) at the left
FLYERS = {"leaf_big", "leaf_mid", "rleaf_a", "rleaf_b", "rleaf_c", "spiral_0", "spiral_1", "spiral_2"}

# name -> (cell (w, h), symmetry "lr" / "lr_union" / "tb", place "core" / "bottom", [(piece, k, ops), ...])
FX = {
    "a_leaf": ((10, 6), "tb", "core", [("leaf_big", 1, ()), ("leaf_mid", 1, ()), ("leaf_big", 1, ("dim",)),
                                       ("leaf_mid", 1, ())]),
    "a_hit": ((14, 12), "lr_union", "core", [("hit_small", 0.55, ()), ("slash", 1, ()), ("slash", 1, ("dim",)),
                                             ("hit_small", 0.9, ("dim", "sparse"))]),
    "p_full": ((44, 36), "lr", "top", [("crown", 0.75, ()), ("crown", 0.75, ("up1",)), ("crown", 0.75, ("up2", "dim")),
                                       ("crown", 0.75, ("up1",)), ("crown", 0.75, ()), ("crown", 0.75, ("dim",))]),
    "p_burn": ((20, 26), "lr", "sides", [("flame_a", 1, ()), ("flame_b", 1, ()), ("flame_a", 1, ("up1",)),
                                         ("flame_b", 1, ("up1", "dim")), ("flame_a", 1, ("dim",)), ("flame_b", 1, ())]),
    "q_leaf": ((12, 7), "tb", "core", [("spiral_0", 1, ()), ("spiral_1", 1, ()), ("spiral_2", 1, ()),
                                       ("spiral_1", 1, ("dim",))]),
    "q_hit": ((26, 22), "lr", "core", [("fan", 0.6, ()), ("fan", 0.85, ()), ("fan", 1, ()), ("fan", 1, ("dim",)),
                                       ("fan", 1, ("dim", "sparse"))]),
    "q_wound": ((10, 10), "lr", "core", [("split", 1, ()), ("split", 1, ()), ("split", 1, ("up1",)),
                                         ("split", 1, ("up1", "dim")), ("split", 1, ()), ("split", 1, ("dim",))]),
    "e_dig": ((40, 18), "lr", "bottom", [("dig", 0.7, ()), ("clods", 1, ()), ("clods", 1, ("up1",)), ("dig", 1, ()),
                                         ("dig", 1, ("dim", "sparse"))]),
    "e_pop": ((48, 26), "lr", "bottom", [("burst", 0.5, ()), ("burst", 0.75, ()), ("burst", 1, ()),
                                         ("burst", 1, ("dim",)), ("burst", 1, ("sparse",)),
                                         ("burst", 1, ("dim", "sparse"))]),
    "e_slow": ((22, 8), "lr", "bottom", [("mud", 1, ()), ("mud", 1, ("dim",)), ("mud", 1, ()), ("mud", 1, ("up1",)),
                                         ("mud", 1, ()), ("mud", 1, ("dim",))]),
    "r_cast": ((56, 48), "lr", "bottom", [("rcast", 0.45, ()), ("rcast", 0.75, ()), ("rcast", 1, ()),
                                          ("rcast", 1, ("up1", "dim")), ("rcast", 1, ("sparse",)),
                                          ("rcast", 1, ("up2", "dim", "sparse"))]),
    "r_blaze": ((52, 20), "lr", "core", [("blaze", 1, ()), ("blaze", 1, ("up1",)), ("blaze", 1, ("dim",)),
                                         ("blaze", 1, ()), ("blaze", 1, ("up1", "dim")), ("blaze", 1, ())]),
    "r_leaf": ((12, 8), "tb", "core", [("rleaf_a", 1, ()), ("rleaf_b", 1, ()), ("rleaf_c", 1, ()),
                                       ("rleaf_a", 1, ("dim",))]),
    "r_hit": ((16, 16), "lr", "core", [("spark_s", 0.8, ()), ("spark_b", 1, ()), ("spark_b", 1, ("dim",)),
                                       ("spark_s", 1, ("dim", "sparse"))]),
}
ICONS = {"skill": (657, 1425, 968), "skill2": (1056, 1425, 1377), "ult": (1464, 1425, 1775)}   # x0, y0, x1


def ramps():
    """Each ramp's colours, light to dark; the palette is all of them and the outline."""
    out = []
    for ramp in (PF.FIRE, PF.LEAF, PF.WOOD, PF.BARK, PF.DIRT):
        out.append([tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in ramp.split(", ")])
    return out


RAMPS = ramps()
PAL = np.array([c for r in RAMPS for c in r] + [OUTLINE], float)
DIM = {c: (r[i + 1] if i + 1 < len(r) else c) for r in RAMPS for i, c in enumerate(r)}
DIM[OUTLINE] = OUTLINE
FIRE = set(RAMPS[0])


def fire_mask(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (r > 170) & (r >= g) & (g >= b) & (r - b > 90)


def key(name):
    """spiral_<k> (one of the spiral's three leaves) is cut from the spiral piece."""
    return "spiral" if name.startswith("spiral_") else name


def piece(name, sheet):
    """A piece's RGBA (alpha = drawn), cropped to its drawing."""
    (x0, y0, x1, y1), opt = PIECES[key(name)]
    a = sheet[y0:y1, x0:x1].astype(int)
    d = np.abs(a - BG).max(-1)
    mn, mx = a.min(-1), a.max(-1)
    m = (d > BG_DIFF) & ~((mn > 165) & (mx - mn < 32))      # not the white labels
    if opt.get("fire"):
        m &= fire_mask(a)
    for cx0, cy0, cx1, cy1 in opt.get("cut", ()):
        m[max(0, cy0 - y0):max(0, cy1 - y0), max(0, cx0 - x0):max(0, cx1 - x0)] = False
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = a
    out[..., 3] = np.where(m, 255, 0)
    if name.startswith("spiral_"):   # the spiral's three leaves, biggest first
        from scipy import ndimage
        lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=2))
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        k = int(name.split("_")[1])
        j = 1 + int(np.argsort(-sizes)[k])
        out[..., 3] = np.where(m & (lab == j), 255, 0)
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def level(p):
    """A flying piece turned so its long axis is level and its fiery tail is at the left."""
    ys, xs = np.nonzero(p[..., 3] > 0)
    c = np.cov(np.vstack([xs, ys]))
    w, v = np.linalg.eigh(c)
    ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
    im = Image.fromarray(p).rotate(ang, resample=Image.NEAREST, expand=True)
    a = np.asarray(im).copy()
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    fy, fx = np.nonzero(fire_mask(a) & (a[..., 3] > 0))
    gy, gx = np.nonzero((a[..., 3] > 0) & ~fire_mask(a))
    if len(fx) and len(gx) and fx.mean() > gx.mean():   # the tail (fire) belongs at the left
        a = a[:, ::-1]
    return a


def down(p, cw, ch, k, fire_only):
    """p brought to fit the cell (cw, ch) less a margin, times k: each square drawn when KEEP of its block is, its colour
    the block's median, snapped to the palette."""
    h, w = p.shape[:2]
    f = min((cw - 1) / w, (ch - 1) / h) * k
    ow, oh = max(1, round(w * f)), max(1, round(h * f))
    out = np.zeros((oh, ow, 4), np.uint8)
    for j in range(oh):
        for i in range(ow):
            blk = p[int(j * h / oh):max(int(j * h / oh) + 1, int((j + 1) * h / oh)),
                    int(i * w / ow):max(int(i * w / ow) + 1, int((i + 1) * w / ow))].reshape(-1, 4)
            on = blk[blk[:, 3] > 0]
            if len(on) < KEEP * len(blk):
                continue
            col = np.median(on[:, :3], axis=0)
            if col.max() < DARK:
                if fire_only:
                    continue
                out[j, i] = (*OUTLINE, 255)
                continue
            out[j, i, :3] = PAL[np.argmin(((PAL - col) ** 2).sum(1))]
            out[j, i, 3] = 255
    return out


def sym(c, how):
    if how == "tb":
        f = c[::-1]
    else:
        f = c[:, ::-1]
    if how in ("tb", "lr_union"):
        out = c.copy()
        put = (out[..., 3] == 0) & (f[..., 3] > 0)
        out[put] = f[put]
        return sym(out, "lr") if how == "lr_union" else _tb_fix(out)   # where both halves were drawn: one of them
    # lr: the fuller half mirrored on to the other
    w = c.shape[1]
    hw = (w + 1) // 2
    left, right = c[:, :hw], c[:, w - hw:]
    out = c.copy()
    if (left[..., 3] > 0).sum() >= (right[..., 3] > 0).sum():
        out[:, w - hw:] = left[:, ::-1]
    else:
        out[:, :hw] = right[:, ::-1]
    return out


def _tb_fix(c):
    """A union mirrored top to bottom is symmetric only where both halves agree: take the upper half's."""
    h = c.shape[0]
    hh = (h + 1) // 2
    out = c.copy()
    out[h - hh:] = c[:hh][::-1]
    return out


def ops(c, names):
    c = c.copy()
    for op in names:
        if op == "dim":
            for y, x in zip(*np.nonzero(c[..., 3] > 0)):
                c[y, x, :3] = DIM.get(tuple(int(v) for v in c[y, x, :3]), tuple(c[y, x, :3]))
        elif op == "sparse":
            yy, xx = np.mgrid[0:c.shape[0], 0:c.shape[1]]
            w = c.shape[1]
            xs = np.minimum(xx, w - 1 - xx)   # the checker mirrored, so the frame stays symmetric
            c[((yy + xs) % 2 == 1) & (c[..., 3] > 0)] = 0
        elif op.startswith("up"):
            n = int(op[2:])
            c = np.concatenate([c[n:], np.zeros((n,) + c.shape[1:], np.uint8)])
    return c


def place(fig, cw, ch, where):
    cell = np.zeros((ch, cw, 4), np.uint8)
    h, w = fig.shape[:2]
    if where == "sides":   # a flame at each side of the lower body: the piece at the left, mirrored later
        fig = fig[:, :]
        y, x = ch - h, 0
    elif where == "bottom":
        y, x = ch - h, (cw - w) // 2
    elif where == "top":
        y, x = 0, (cw - w) // 2
    else:
        y, x = (ch - h) // 2, (cw - w) // 2
    cell[y:y + h, x:x + w] = fig[:ch - y, :cw - x]
    return cell


def clean(name, sheet, cache):
    (cw, ch), how, where, frames = FX[name]
    out = []
    for pname, k, names in frames:
        if pname not in cache:
            p = piece(pname, sheet)
            cache[pname] = level(p) if pname in FLYERS else p
        p = cache[pname]
        fire_only = PIECES[key(pname)][1].get("fire", False)
        if where == "sides":
            fig = down(p, cw // 2 - 2, ch * 2 // 3, k, fire_only)
        else:
            fig = down(p, cw, ch, k, fire_only)
        c = place(fig, cw, ch, where)
        if how == "tb":
            c = sym(c, "tb")
        else:
            c = sym(c, "lr" if how == "lr" else "lr_union")
        out.append(ops(c, names))
    return out


def icon(sheet, x0, y0, x1):
    a = sheet[y0:, x0:x1]
    d = np.abs(a.astype(int) - BG).max(-1) > BG_DIFF
    rows = np.nonzero(d.mean(1) > 0.5)[0]            # the tile's rows (the label under it is narrow text)
    top, bot = rows.min(), rows.max()
    cols = np.nonzero(d[top:bot + 1].mean(0) > 0.5)[0]
    im = Image.fromarray(a[top:bot + 1, cols.min():cols.max() + 1]).resize((64, 64), Image.LANCZOS)
    return np.asarray(im.convert("RGBA"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    sheet = np.asarray(Image.open(SHEET).convert("RGB"))
    os.makedirs(os.path.join(OUT, "pixel_1x"), exist_ok=True)
    man, rows, cache = [], [], {}
    for name in FX:
        cs = clean(name, sheet, cache)
        (cw, ch), how, *_ = FX[name]
        for k, c in enumerate(cs):
            if not c[..., 3].any():
                sys.exit(f"{name} frame {k + 1} came out empty")
        f = f"cinderling_fx_{name}.png"
        Image.fromarray(np.concatenate(cs, axis=1)).save(os.path.join(OUT, "pixel_1x", f))
        man.append({"file": f, "frames": len(cs), "cell_1x": [cw, ch],
                    "symmetry": "top-bottom (pointing right)" if how == "tb" else "left-right"})
        rows.append((name, cs))
        print(name, len(cs), "x", cw, ch)
    for slot, (x0, y0, x1) in ICONS.items():
        Image.fromarray(icon(sheet, x0, y0, x1)).save(os.path.join(OUT, f"cinderling_icon_{slot}.png"))
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1)
    if a.review:
        Z = 6
        W = max(sum(c.shape[1] + 3 for c in cs) for _, cs in rows) * Z + 110
        H = sum(max(c.shape[0] for c in cs) * Z + 10 for _, cs in rows) + 64 * 3 + 20
        img = Image.new("RGB", (W, H), (40, 44, 36))
        d = ImageDraw.Draw(img)
        y = 0
        for name, cs in rows:
            x = 110
            h = max(c.shape[0] for c in cs)
            for c in cs:
                d.rectangle([x - 1, y - 1, x + c.shape[1] * Z, y + c.shape[0] * Z], outline=(80, 90, 70))
                im = Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST)
                img.paste(im, (x, y), im)
                x += (c.shape[1] + 3) * Z
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += h * Z + 10
        for k, slot in enumerate(ICONS):
            ic = Image.open(os.path.join(OUT, f"cinderling_icon_{slot}.png"))
            img.paste(ic.resize((128, 128), Image.NEAREST), (110 + k * 140, y))
        img.save(a.review)
        print("review", a.review, img.size)


if __name__ == "__main__":
    main()
