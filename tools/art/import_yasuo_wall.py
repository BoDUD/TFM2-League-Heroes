#!/usr/bin/env python3
"""Import Codex's Wind Wall loop for league_yasuo_wall: upright wind pieces that stand along the wall's ground line.

    python tools/art/import_yasuo_wall.py [--preview DIR]

The user, 2026-10-24: 「跟着方向转有点奇怪啊风墙 做成像英雄联盟那样啊」 - League's wall is a line on the ground (any
direction) with the wind always RISING from it, so the picture is never turned. Source:
assets/source/yasuo/windwall/yasuo_w_wall_loop.png (Codex, six frames of a 46-pixel wall front on). Each frame is shrunk
to game size (the commonest colour of each block), mapped to one palette for the six frames (wind shades + ochre), the
ochre ground line taken out, and the wind cut into PIECES columns. Written to addons/league_yasuo_wall/effects/
league_yasuo_wall_fx (#sheet.png + #anim.fanim):
  plume_<k>  piece k of the wind, the six frames looped for the wall's 4 s, standing on the ground line SOLES rows
             under the frame's middle (the pivot: a unit's soles are that far under the point the game places it at);
  ground     one ochre ground dot for the line (3 x 2) on that line, 4 s;
  cast / block / fade  Codex's gust at his feet (on his soles, SOLES under the pivot), the flash where a missile is
             stopped (centred) and the wall dispersing (centred FADE_UP over the ground line), 4 frames each.
The add-on plays plume_<k> at PIECES points along the wall (left to right on screen) and ground dots every DOT units,
all upright: the line follows the wall, the wind always rises (src/lib.rs `pieces`). --preview also draws the wall
across, up and down, and slanting next to Yasuo at game size.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "yasuo", "windwall", "yasuo_w_wall_loop.png")
OUT = os.path.join(ROOT, "addons", "league_yasuo_wall", "effects", "league_yasuo_wall_fx")
WIDTH = 46                       # the wall's length at game size (src/lib.rs HALF * 2 = 44000 units, + the plumes' tips)
WIDTHS = [7, 6, 7, 6, 7, 6, 7]   # the pieces, left to right (src/lib.rs PIECES = 7)
LIFE = 4.0                       # seconds (src/lib.rs LIFE = 240 ticks)
FRAME = 1 / 12
WIND_COLOURS = 6
# the one-shot pictures: file, game px wide (the widest frame), frame ms, where the pivot is (soles: SOLES under it;
# middle: centred; up: FADE_UP over the ground)
SHOTS = {"cast": ("yasuo_w_cast.png", 26, 60, "soles"), "block": ("yasuo_w_block.png", 12, 50, "middle"),
         "fade": ("yasuo_w_fade.png", 22, 80, "up")}
SOLES, FADE_UP = 11, 10
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return PRE + p if os.name == "nt" and not p.startswith(PRE) else p


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 128)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def shrink(a, w):
    """Each target pixel = the commonest colour of its block (alpha by majority)."""
    H, W = a.shape[:2]
    h = max(1, round(H * w / W))
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        y0, y1 = int(j * H / h), max(int(j * H / h) + 1, int((j + 1) * H / h))
        for i in range(w):
            x0, x1 = int(i * W / w), max(int(i * W / w) + 1, int((i + 1) * W / w))
            blk = a[y0:y1, x0:x1].reshape(-1, 4)
            on = blk[blk[:, 3] > 128]
            if len(on) * 2 < len(blk):
                continue
            q = (on[:, :3] // 12).astype(np.int32)
            key = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
            vals, cnt = np.unique(key, return_counts=True)
            out[j, i, :3] = on[key == vals[cnt.argmax()]][:, :3].mean(0)
            out[j, i, 3] = 255
    return out


def frames():
    a = np.asarray(Image.open(lp(SRC)).convert("RGBA"))
    on = (a[..., 3] > 40).any(0)
    runs, s = [], None
    for x, c in enumerate(list(on) + [False]):
        if c and s is None:
            s = x
        if not c and s is not None:
            if x - s > 50:
                runs.append((s, x))
            s = None
    return [crop(shrink(crop(a[:, x0:x1]), WIDTH)) for x0, x1 in runs]


def kmeans(px, k, it=20):
    rng = np.random.default_rng(0)
    c = px[rng.choice(len(px), k, replace=False)].astype(float)
    for _ in range(it):
        lab = ((px[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            if (lab == j).any():
                c[j] = px[lab == j].mean(0)
    return np.round(c).astype(np.uint8)


def build():
    fr = frames()
    H = max(f.shape[0] for f in fr)
    fr = [np.pad(f, ((H - f.shape[0], 0), (0, WIDTH - f.shape[1]), (0, 0))) for f in fr]     # bottoms aligned
    allpx = np.concatenate([f[f[..., 3] > 0][:, :3] for f in fr]).astype(int)
    warm = allpx[:, 0] > allpx[:, 2] + 20
    wind_pal = kmeans(allpx[~warm], WIND_COLOURS)
    ochre_pal = kmeans(allpx[warm], 3) if warm.sum() >= 3 else np.array([[200, 150, 70]] * 3, np.uint8)
    base = min(int(np.nonzero((f[..., 3] > 0) & (f[..., 0].astype(int) > f[..., 2].astype(int) + 20))[0].min())
               for f in fr if ((f[..., 0].astype(int) > f[..., 2].astype(int) + 20) & (f[..., 3] > 0)).any())
    plumes = []
    for f in fr:
        g = np.zeros_like(f)
        rgb = f[..., :3].astype(int)
        on = f[..., 3] > 0
        hot = on & (rgb[..., 0] > rgb[..., 2] + 20)
        wind = on & ~hot
        lab = ((rgb[wind][:, None, :] - wind_pal[None].astype(int)) ** 2).sum(-1).argmin(1)
        g[wind] = np.c_[wind_pal[lab], np.full(len(lab), 255)]
        g[base:] = 0                                   # the ground line and anything under it: the dots draw it
        plumes.append(g[:base])
    ochre = sorted(ochre_pal.tolist(), key=lambda c: -sum(c))
    dot = np.zeros((2, 3, 4), np.uint8)
    dot[0, :] = ochre[0] + [255]
    dot[1, :] = ochre[2] + [255]
    dot[1, 0, 3] = dot[1, 2, 3] = 0
    return plumes, dot, base


def cells_of(a, n):
    """Codex's frames: the solid runs of columns, grouped into n by which equal share of the sheet holds their middle."""
    W = a.shape[1]
    on = (a[..., 3] > 40).any(0)
    runs, st = [], None
    for x, c in enumerate(list(on) + [False]):
        if c and st is None:
            st = x
        if not c and st is not None:
            if x - st > 8:
                runs.append((st, x))
            st = None
    groups = [[] for _ in range(n)]
    for r in runs:
        groups[min(n - 1, int((r[0] + r[1]) / 2 / (W / n)))].append(r)
    return [a[:, g[0][0]:g[-1][1]] for g in groups if g]


def shot(fn, width, n=4):
    a = np.asarray(Image.open(lp(os.path.join(os.path.dirname(SRC), fn))).convert("RGBA"))
    raw = [crop(c) for c in cells_of(a, n)]
    s = width / max(r.shape[1] for r in raw)
    small = [shrink(r, max(1, round(r.shape[1] * s))) for r in raw]
    px = np.concatenate([f[f[..., 3] > 0][:, :3] for f in small]).astype(int)
    pal = kmeans(px, min(8, len(px)))
    out = []
    for f in small:
        g = f.copy()
        on = g[..., 3] > 0
        lab = ((g[on][:, :3].astype(int)[:, None, :] - pal[None].astype(int)) ** 2).sum(-1).argmin(1)
        g[on] = np.c_[pal[lab], np.full(len(lab), 255)]
        out.append(g)
    return out, [r.shape[0] for r in raw], s


def placed(f, where, rows):
    """A frame in a cell whose middle is the pivot: drawn standing on the soles, centred, or over the ground."""
    h, w = f.shape[:2]
    if where == "middle":
        H, top = h + (h % 2 == 0), 0
    elif where == "soles":
        H = 2 * (rows - SOLES) if rows > SOLES else 2 * h
        H = max(H, 2 * (h - SOLES) + 1)
        top = H // 2 + SOLES - rows
    else:
        up = FADE_UP - SOLES                                          # over the ground line, which is SOLES under
        H = 2 * (abs(up) + (h + 1) // 2) + 1
        top = H // 2 - up - h // 2
    W = w + (w % 2 == 0)
    cell = np.zeros((H, W, 4), np.uint8)
    cell[top + rows - h if where == "soles" else top:(top + rows if where == "soles" else top + h), :w] = f
    return cell


def write(plumes, dot, base):
    pieces, x0 = [], 0
    for w in WIDTHS:
        pieces.append([p[:, x0:x0 + w] for p in plumes])
        x0 += w
    tiles, anims, x = [], {}, 0
    loops = int(round(LIFE / (FRAME * len(plumes))))
    for k, fr in enumerate(pieces):
        rects = []
        for f in fr:
            # a unit's soles are SOLES rows under its pivot (the point the game places it at): the ground line is too
            H = 2 * max(base - SOLES, SOLES) + 1
            cell = np.zeros((H, f.shape[1], 4), np.uint8)
            top = H // 2 + SOLES - base
            cell[top:top + base] = f
            tiles.append((x, cell))
            rects.append({"x": float(x), "y": 0.0, "w": float(cell.shape[1]), "h": float(cell.shape[0])})
            x += cell.shape[1] + 1
        anims[f"plume_{k}"] = {"frames": [{"duration": FRAME, "data": r} for _ in range(loops) for r in rects]}
    for tag, (fn, width, ms, where) in SHOTS.items():
        frs, _, _ = shot(fn, width)
        rows = max(f.shape[0] for f in frs)
        rects = []
        for f in frs:
            cell = placed(np.pad(f, ((rows - f.shape[0], 0), (0, 0), (0, 0))) if where == "soles" else f, where, rows)
            tiles.append((x, cell))
            rects.append({"x": float(x), "y": 0.0, "w": float(cell.shape[1]), "h": float(cell.shape[0])})
            x += cell.shape[1] + 1
        anims[tag] = {"frames": [{"duration": ms / 1000, "data": r} for r in rects]}
    cell = np.zeros((2 * (SOLES + 2) + 1, 3, 4), np.uint8)
    cell[SOLES + 2 + SOLES:SOLES + 2 + SOLES + 2] = dot              # on the ground line, SOLES under the pivot
    tiles.append((x, cell))
    anims["ground"] = {"frames": [{"duration": LIFE, "data": {"x": float(x), "y": 0.0, "w": 3.0,
                                                            "h": float(cell.shape[0])}}]}
    x += 4
    sheet = np.zeros((max(t.shape[0] for _, t in tiles), x, 4), np.uint8)
    for tx, t in tiles:
        sheet[:t.shape[0], tx:tx + t.shape[1]] = t
    os.makedirs(lp(os.path.dirname(OUT)), exist_ok=True)
    Image.fromarray(sheet).save(lp(OUT + "#sheet.png"))
    with open(lp(OUT + "#anim.fanim"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"anims": anims}, f, indent=1)
        f.write("\n")
    print("wrote", OUT, sheet.shape, "pieces", [p[0].shape for p in pieces], "loops", loops)
    return pieces


# the add-on's layout (src/lib.rs `pieces`, `dots`): the line in map units, 1000 units a game pixel
HALF, BOW, DOT, AHEAD = 22_000.0, 5_000.0, 1_600.0, 24_000.0


def layout(mid, d):
    side = np.array([-d[1], d[0]])
    if side[0] < 0 or (abs(side[0]) < 1e-9 and side[1] < 0):
        side = -side                                    # pieces go left to right on screen (top to bottom if upright)
    def at(t):
        return np.array(mid) + side * HALF * t + np.array(d) * BOW * (1 - t * t)
    n = len(WIDTHS)
    plumes = [at(-1 + (2 * k + 1) / n) for k in range(n)]
    ndots = int(2 * HALF / DOT) + 1
    dots = [at(-1 + 2 * i / (ndots - 1)) for i in range(ndots)]
    return plumes, dots


def preview(path, pieces, dot):
    import pack_squill_windwall as P
    yas = P.champ_1x("league_yasuo")
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    cases = [("敌人在右边：墙竖着", (1.0, 0.0)), ("敌人在下面：墙横着", (0.0, 1.0)), ("敌人在右下：墙斜着", (0.7071, 0.7071)),
             ("敌人在左上：墙斜着", (-0.7071, -0.7071))]
    tiles = []
    for name, d in cases:
        W, H = 110, 100
        img = Image.new("RGBA", (W * Z, H * Z + 30), P.ARENA)
        me = np.array([40.0, 55.0])
        img.alpha_composite(P.up(yas, Z), (int((me[0] - yas.shape[1] / 2) * Z), int((me[1] - yas.shape[0]) * Z) + 30))
        mid = me * 1000 + np.array(d) * AHEAD
        plumes, dots = layout(tuple(mid), d)
        for p in dots:
            q = p / 1000
            img.alpha_composite(P.up(dot, Z), (int((q[0] - 1.5) * Z), int(q[1] * Z) + 30))
        order = sorted(range(len(plumes)), key=lambda k: plumes[k][1])           # back (higher up) drawn first
        for k in order:
            f = pieces[k][0]
            q = plumes[k] / 1000
            img.alpha_composite(P.up(f, Z), (int((q[0] - f.shape[1] / 2) * Z), int((q[1] - f.shape[0]) * Z) + 30))
        ImageDraw.Draw(img).text((6, 4), name, fill=(255, 255, 255, 255), font=font)
        tiles.append(img)
    out = Image.new("RGB", (sum(t.width + 8 for t in tiles), max(t.height for t in tiles)), (50, 54, 44))
    x = 0
    for t in tiles:
        out.paste(t.convert("RGB"), (x, 0))
        x += t.width + 8
    out.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    plumes, dot, base = build()
    pieces = write(plumes, dot, base)
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        preview(os.path.join(a.preview, "wall_ways.png"), pieces, dot)
        print("preview", a.preview)


if __name__ == "__main__":
    main()
