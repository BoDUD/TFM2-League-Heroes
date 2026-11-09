#!/usr/bin/env python3
"""The League dragons' bodies (league_dragons, the user 2026-11-09: 「大小龙模型呢？codex做吗 还有攻击动画」「你要参考英雄联盟里面
的攻击姿势啊」「龙魂的也都交付了 你处理完」) from Codex's two deliveries: step 1's eight front designs
(dragons_models_done.zip: dragons-models/<model>-A.png, Codex's copies normalized on 6 px squares) and step 2's 91
action frames (dragons_actions_done.zip: dragons-actions/<model>/<tag>_<k>.png, the untouched generations on the
templates of tools/art/pack_dragons_actions.py). Neither is in the repo (League's renders went into the packs); this
tool reads them where they were unzipped and writes the sheets:

    python tools/art/dragons_hd.py --designs DIR/dragons-models --actions DIR/dragons-actions [--review DIR]

addons/league_dragons/effects/league_drake_<element>, league_drake_elder (native serpen's tags: idle 4 x 160, base, attack 5 x 80,
dead 8 x 80; PPU 1.8, the soles 37 game px under the anchor) and league_baron (native epic's: idle, base, attack_left /
attack_right 5 x 80, attack_target_effect 7 x 60, dead 13 x 60; PPU 1.5, the pit line 55 game px under the anchor),
every tag with its hd_ twin; the 1x frames the dense ones' area majority. Every frame is cropped symmetric about the
anchor the game draws it on (a frame's centre), dense W = PPU x the 1x w exactly.

1. Read: every frame on the canvas' 6 px squares (the phase whose squares are purest), each square the palette colour
   most of its drawn pixels (alpha >= 128) snap to; the palette a model's own: k-means (Lab, 40 shades, 48 for the
   Elder and Baron) over the design's squares and the frames' square centres, each shade a colour Codex drew. Codex's
   copies of the designs keep thousands of colours, so the design is snapped to the same palette.
2. Drakes and the Elder: base = the design; idle = its upper 72 % sunk 0 / 2 / 4 / 2 squares behind the legs (native
   serpen's idle sinks its top 0 / 2 / 5 / 2 px); attack = the design with Codex's frame inside the moving zone only
   (League's attack1 moves only the neck, head and jaw: the squares whose silhouette moves in any attack frame, the
   central band, closed and filled, plus each frame's element where it differs strongly) - Codex redrew the whole body
   in every frame (a quarter of its squares the design's colour), which would shimmer; dead 1-6 = Codex's, each frame's
   main body put on the ground line (the lying frames were drawn 19 squares high), dead_6 at dead_5's height; dead 7 =
   dead_6 breaking into shards, dead 8 empty (as native).
3. Baron: base = the design; idle = it sunk 0 / 2 / 4 / 2 squares into the pit; attack_left and dead 1-8 = Codex's,
   each frame's magenta spine over the design's and its bottom on the pit line, nothing under the line; attack_right =
   attack_left mirrored (the design is symmetric); dead 9-12 = dead_8 breaking into shards, 13 empty; the target effect
   = Codex's 7 cells read about each cell's target point (the template's cross).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

DES = ACT = None
SQ = 6
FAR = 14.0
MODELS = ["infernal", "mountain", "ocean", "cloud", "hextech", "chemtech", "elder", "baron"]
BARON = "baron"
NAMES = {**{m: f"league_drake_{m}" for m in MODELS[:6]}, "elder": "league_drake_elder", "baron": "league_baron"}
OUT_DIR = os.path.join(ROOT, "addons", "league_dragons", "effects")
READ = {}
PALETTES = {}
BAND = 0.25
DE = 22.0


def design_of(model):
    name = model if model in ("baron", "elder") else "drake_" + model
    a = np.asarray(Image.open(os.path.join(DES, f"{name}-A.png")).convert("RGBA"))
    return a[SQ // 2::SQ, SQ // 2::SQ][:a.shape[0] // SQ, :a.shape[1] // SQ].copy()


def lab(rgb):
    return color.rgb2lab(rgb.reshape(-1, 1, 3).astype(float) / 255.0)[:, 0]


K = {"baron": 48, "elder": 48}   # flat shades a model (k-means in Lab over the design's squares and the frames'), else 40


def palette(dsg, frames, k=40, seed=7):
    """the model's flat palette: k-means (Lab) over the design's squares and every frame's square centres (alpha >= 128),
    each cluster's colour its member nearest the centre (a colour Codex actually drew)"""
    from scipy.cluster.vq import kmeans2
    pts = [dsg[dsg[..., 3] > 0][:, :3]]
    for a in frames:
        c = a[SQ // 2::SQ, SQ // 2::SQ]
        pts.append(c[c[..., 3] >= 128][:, :3])
    rgb = np.concatenate(pts)
    L = lab(rgb)
    np.random.seed(seed)
    cen, lbl = kmeans2(L, k, iter=40, minit="++", seed=seed)
    out = []
    for i in range(k):
        mem = np.nonzero(lbl == i)[0]
        if not len(mem):
            continue
        j = mem[((L[mem] - cen[i]) ** 2).sum(-1).argmin()]
        out.append(rgb[j])
    return np.unique(np.array(out, np.uint8), axis=0)


def snap(rgb, pal_lab):
    flat = rgb.reshape(-1, 3)
    u, inv = np.unique(flat, axis=0, return_inverse=True)
    d = ((lab(u)[:, None] - pal_lab[None]) ** 2).sum(-1)
    return d.argmin(1)[inv.ravel()].reshape(rgb.shape[:2])


def read(a, pal, pal_lab):
    H, W = a.shape[0] // SQ, a.shape[1] // SQ
    m = a[..., 3] >= 128
    idx = snap(a[..., :3], pal_lab)
    # vectorised purity per phase
    scores = {}
    k = len(pal)
    for oy in range(SQ):
        for ox in range(SQ):
            hh, ww = (a.shape[0] - oy) // SQ, (a.shape[1] - ox) // SQ
            ii = idx[oy:oy + hh * SQ, ox:ox + ww * SQ].reshape(hh, SQ, ww, SQ).transpose(0, 2, 1, 3).reshape(-1, SQ * SQ)
            mi = m[oy:oy + hh * SQ, ox:ox + ww * SQ].reshape(hh, SQ, ww, SQ).transpose(0, 2, 1, 3).reshape(-1, SQ * SQ)
            on = mi.sum(1) * 2 >= SQ * SQ
            ii, mi = ii[on], mi[on]
            if not len(ii):
                scores[(oy, ox)] = 0; continue
            cnt = np.zeros((len(ii), k), np.int32)
            rows = np.repeat(np.arange(len(ii)), SQ * SQ)
            np.add.at(cnt, (rows[mi.ravel()], ii.ravel()[mi.ravel()]), 1)
            scores[(oy, ox)] = cnt.max(1).sum() / mi.sum()
    oy, ox = max(scores, key=scores.get)
    out = np.zeros((H, W, 4), np.uint8)
    hh, ww = (a.shape[0] - oy) // SQ, (a.shape[1] - ox) // SQ
    ii = idx[oy:oy + hh * SQ, ox:ox + ww * SQ].reshape(hh, SQ, ww, SQ).transpose(0, 2, 1, 3).reshape(hh, ww, -1)
    mi = m[oy:oy + hh * SQ, ox:ox + ww * SQ].reshape(hh, SQ, ww, SQ).transpose(0, 2, 1, 3).reshape(hh, ww, -1)
    for j in range(hh):
        for i in range(ww):
            sel = mi[j, i]
            if sel.sum() * 2 < SQ * SQ:
                continue
            v = np.bincount(ii[j, i][sel], minlength=k)
            out[j, i, :3] = pal[v.argmax()]
            out[j, i, 3] = 255
    # the phase's squares start at (oy, ox): a phase over half a square belongs to the next square's index
    sy, sx = (1 if oy > SQ // 2 else 0), (1 if ox > SQ // 2 else 0)
    if sy or sx:
        out = np.roll(out, (sy, sx), (0, 1))
    return out, (oy, ox), scores[(oy, ox)]



def lab_img(a):
    return color.rgb2lab(a[..., :3].astype(float) / 255.0)


def zones(model):
    d = READ[model]["design_flat"]
    dm = d[..., 3] > 0
    ys, xs = np.nonzero(dm)
    cx, W = (xs.min() + xs.max() + 1) / 2, xs.max() + 1 - xs.min()
    band = (np.abs(np.arange(d.shape[1]) - cx) <= BAND * W)[None, :].repeat(d.shape[0], 0)
    names = sorted(n for n in READ[model] if n.startswith("attack"))
    fr = {n: READ[model][n] for n in names}
    dl = lab_img(d)
    common = np.zeros_like(dm)
    per = {}
    for n, a in fr.items():
        am = a[..., 3] > 0
        alpha_diff = (am != dm) & band
        common |= alpha_diff
        de = np.sqrt(((lab_img(a) - dl) ** 2).sum(-1))
        per[n] = (de > DE) & am & dm & band
    common = ndimage.binary_closing(common, iterations=3)
    common = ndimage.binary_fill_holes(common)
    out = {}
    for n in names:
        z = common | per[n]
        z = ndimage.binary_closing(z, iterations=2)
        z = ndimage.binary_fill_holes(z)
        z = ndimage.binary_dilation(z, iterations=1) & band
        # keep only pieces of real size (lone recoloured squares stay the design's)
        lbl, k = ndimage.label(z)
        if k:
            sz = ndimage.sum(z, lbl, range(1, k + 1))
            z = np.isin(lbl, [i + 1 for i in range(k) if sz[i] >= 25])
        out[n] = z
    return d, fr, out



def main_box(a, keep=0.9):
    """box of the biggest pieces holding `keep` of the drawn squares (specks of a dissolve left out)"""
    m = a[..., 3] > 0
    lbl, k = ndimage.label(m, structure=np.ones((3, 3)))
    if k == 0:
        return None
    sz = ndimage.sum(m, lbl, range(1, k + 1))
    order = np.argsort(-sz)
    tot, sel = 0, []
    for i in order:
        sel.append(i + 1)
        tot += sz[i]
        if tot >= keep * m.sum():
            break
    ys, xs = np.nonzero(np.isin(lbl, sel))
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def shift(a, dy, dx=0):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys, yd = (slice(max(0, -dy), H - max(0, dy)), slice(max(0, dy), H - max(0, -dy)))
    xs, xd = (slice(max(0, -dx), W - max(0, dx)), slice(max(0, dx), W - max(0, -dx)))
    out[yd, xd] = a[ys, xs]
    return out


def over(top, bottom):
    out = bottom.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def shards(a, steps, seed, block=5, rise=7):
    """`a` breaking into shards, one frame a step in `steps` (0 = whole, 1 = gone): the drawing cut into block x block
    pieces (the cut lines jittered a square), each piece leaving at its own random moment and rising up to `rise`
    squares (with a little sideways drift) until it does - whole pieces, never a dither"""
    rng = np.random.default_rng(seed)
    H, W = a.shape[:2]
    oy, ox = rng.integers(0, block, 2)
    by = (np.arange(H) + oy) // block
    bx = (np.arange(W) + ox) // block
    lab = by[:, None] * (bx.max() + 1) + bx[None, :]
    n = lab.max() + 1
    t = rng.random(n)
    drift = rng.integers(-1, 2, n)
    speed = 0.5 + rng.random(n)
    out = []
    for s in steps:
        f = np.zeros_like(a)
        alive = t >= s
        for k in np.nonzero(alive & np.bincount(lab[a[..., 3] > 0].ravel(), minlength=n).astype(bool))[0]:
            m = (lab == k) & (a[..., 3] > 0)
            ys, xs = np.nonzero(m)
            dy = -int(round(rise * s * speed[k]))
            dx = int(round(drift[k] * s * 2))
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            f[yy[ok], xx[ok]] = a[ys[ok], xs[ok]]
        out.append(f)
    return out


def spine_x(a, rows=24):
    """Baron's magenta spine: the mean column of its brightest magenta squares in the bottom rows"""
    m = a[..., 3] > 0
    ys = np.nonzero(m.any(1))[0]
    yb = ys.max()
    sub = a[max(0, yb - rows):yb + 1].astype(int)
    mag = (sub[..., 3] > 0) & (sub[..., 0] > 180) & (sub[..., 2] > 180) & (sub[..., 1] < 90)
    xs = np.nonzero(mag)[1]
    return xs.mean() if len(xs) else None


def drake_frames(model):
    d = READ[model]["design_flat"]
    ys = np.nonzero(d[..., 3].any(1))[0]
    top, bot = ys.min(), ys.max()                      # bot: the soles' last row
    tags = {"base": [d]}
    split = int(round(top + 0.72 * (bot + 1 - top)))
    idle = []
    for k in (0, 2, 4, 2):
        up = d.copy(); up[split:] = 0
        lo = d.copy(); lo[:split] = 0
        idle.append(over(lo, shift(up, k)))
    tags["idle"] = idle
    _, fr, zs = zones(model)
    tags["attack"] = [np.where(zs[n][..., None], fr[n], d) for n in sorted(fr)]
    dead = []
    dys = {}
    for k in range(1, 7):
        a = READ[model][f"dead_{k}"]
        b = main_box(a)
        dys[k] = bot - (b[3] - 1)
    if abs(dys[6] - dys[5]) <= 3:
        dys[6] = dys[5]                              # the same lying pose dissolving: no jump
    for k in range(1, 7):
        dead.append(shift(READ[model][f"dead_{k}"], dys[k]))
    dead += shards(dead[-1], [0.55], seed=11)
    dead.append(np.zeros_like(d))
    tags["dead"] = dead
    meta = {"ppu": 1.8, "anchor": [128.0, bot + 1 - 66.5], "dead_dy": dys, "idle_split": split}
    return tags, meta


def baron_frames():
    d = READ[BARON]["design_flat"]
    ys = np.nonzero(d[..., 3].any(1))[0]
    pit = ys.max()                                    # the pit line's last row
    sx0 = spine_x(d)
    tags = {"base": [d]}
    tags["idle"] = [clip(shift(d, k), pit) for k in (0, 2, 4, 2)]
    al, notes = [], {}
    for k in range(1, 6):
        a = READ[BARON][f"attack_left_{k}"]
        al.append(place(a, sx0, pit, notes, f"attack_left_{k}"))
    tags["attack_left"] = al
    tags["attack_right"] = [np.ascontiguousarray(a[:, ::-1]) for a in al]
    dead = []
    for k in range(1, 9):
        dead.append(place(READ[BARON][f"dead_{k}"], sx0, pit, notes, f"dead_{k}"))
    dead += shards(dead[7], [0.3, 0.5, 0.7, 0.88], seed=41, block=6, rise=12)
    dead.append(np.zeros_like(d))
    tags["dead"] = dead
    tags["attack_target_effect"] = target_effect()
    meta = {"ppu": 1.5, "anchor": [85.0, pit + 1 - 82.5], "spine": sx0, "placed": notes,
            "effect_anchor": [EFX_W / 2, EFX_H / 2]}
    return tags, meta


def clip(a, pit):
    a = a.copy()
    a[pit + 1:] = 0
    return a


def place(a, sx0, pit, notes, name):
    """Baron's frame: its spine over the design's, its bottom on the pit line, nothing under it"""
    sx = spine_x(a)
    dx = int(round(sx0 - sx)) if sx is not None else 0
    b = main_box(a, 0.97)
    dy = pit - (b[3] - 1)
    notes[name] = [int(dx), int(dy)]
    return clip(shift(a, dy, dx), pit)


EFX_W, EFX_H = 64, 86          # the target effect's dense canvas (squares): the cell's grey box and more, the target at its centre


def target_effect():
    """the 7 cells of Codex's effect sheet read on 6 px squares about each cell's target point (the template's cross:
    the cell's centre, 40 px down), the target the frame's centre"""
    a = np.asarray(Image.open(os.path.join(ACT, BARON, "attack_target_effect.png")).convert("RGBA"))
    pal = PALETTES[BARON]
    pl = lab(pal)
    out = []
    for i in range(7):
        x0, y0 = (i % 4) * 384, (i // 4) * 512
        px, py = x0 + 192, y0 + 256 + 40
        cx0, cy0 = px - EFX_W // 2 * 6, py - EFX_H // 2 * 6
        cell = np.zeros((EFX_H * 6, EFX_W * 6, 4), np.uint8)
        sx0, sy0 = max(cx0, x0), max(cy0, y0)
        sx1, sy1 = min(cx0 + EFX_W * 6, x0 + 384), min(cy0 + EFX_H * 6, y0 + 512)
        cell[sy0 - cy0:sy1 - cy0, sx0 - cx0:sx1 - cx0] = a[sy0:sy1, sx0:sx1]
        fr, ph, pur = read(cell, pal, pl)
        out.append(fr[:EFX_H, :EFX_W])
    return out




def read_model(model):
    """step 1: the design and every frame on the 6 px squares, snapped to the model's palette (READ, PALETTES)"""
    dsg = design_of(model)
    folder = os.path.join(ACT, model)
    names = sorted(f[:-4] for f in os.listdir(folder) if f.endswith(".png") and f != "attack_target_effect.png")
    frames = {n: np.asarray(Image.open(os.path.join(folder, n + ".png")).convert("RGBA")) for n in names}
    pal = palette(dsg, list(frames.values()), K.get(model, 40))
    pl = lab(pal)
    flat = dsg.copy()
    on = flat[..., 3] > 0
    flat[on, :3] = pal[snap(flat[on][:, :3][None], pl)[0]]
    flat[..., 3] = np.where(on, 255, 0)
    got = {"design_flat": flat}
    for n, a in frames.items():
        got[n] = read(a, pal, pl)[0]
    READ[model] = got
    PALETTES[model] = pal


def sizes(half_w, half_h, ppu, x_half, y_half):
    """the smallest 1x (w, h) whose dense twin (PPU x, whole) covers the half extents about the anchor, the dense size
    even where the anchor is on a square's edge (x_half / y_half False) and odd where it is a square's middle"""
    def pick(half, odd):
        n = 1
        while True:
            big = ppu * n
            if abs(big - round(big)) < 1e-6 and (int(round(big)) % 2 == 1) == odd and big / 2 >= half:
                return n, int(round(big))
            n += 1
    w1, W = pick(half_w, x_half)
    h1, H = pick(half_h, y_half)
    return w1, h1, W, H


def crop_pair(full, anchor, ppu):
    """(dense crop, 1x frame): the dense frame cut symmetric about the anchor, the 1x its area majority"""
    ax, ay = anchor
    m = full[..., 3] > 0
    if m.any():
        ys, xs = np.nonzero(m)
        hx = max(ax - xs.min(), xs.max() + 1 - ax) + 1
        hy = max(ay - ys.min(), ys.max() + 1 - ay) + 1
    else:
        hx = hy = 2
    w1, h1, W, H = sizes(hx, hy, ppu, ax % 1 != 0, ay % 1 != 0)
    x0, y0 = int(round(ax - W / 2)), int(round(ay - H / 2))
    dense = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(full.shape[1], x0 + W), min(full.shape[0], y0 + H)
    if sx1 > sx0 and sy1 > sy0:
        dense[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = full[sy0:sy1, sx0:sx1]
    return dense, one_x(dense, ppu, w1, h1)


def one_x(dense, ppu, w1, h1):
    """each 1x pixel the colour most of the dense pixels under it are (area-weighted, on a supersampled grid), drawn
    where half of it is"""
    u = {1.8: 5, 1.5: 2}[ppu]
    b = int(round(ppu * u))
    sup = np.repeat(np.repeat(dense, u, 0), u, 1)
    out = np.zeros((h1, w1, 4), np.uint8)
    cols = sup[..., :3].astype(np.int32)
    key = (cols[..., 0] << 16) | (cols[..., 1] << 8) | cols[..., 2]
    on = sup[..., 3] > 0
    for j in range(h1):
        for i in range(w1):
            blk_on = on[j * b:(j + 1) * b, i * b:(i + 1) * b]
            if blk_on.sum() * 2 < b * b:
                continue
            k = key[j * b:(j + 1) * b, i * b:(i + 1) * b][blk_on]
            v, c = np.unique(k, return_counts=True)
            best = v[c.argmax()]
            out[j, i] = [(best >> 16) & 255, (best >> 8) & 255, best & 255, 255]
    return out


DURATIONS = {"idle": 160, "base": 100, "attack": 80, "attack_left": 80, "attack_right": 80, "attack_target_effect": 60}


def build(model, review=None):
    read_model(model)
    tags, meta = baron_frames() if model == BARON else drake_frames(model)
    ppu = meta["ppu"]
    order = ["idle", "base", "attack", "attack_left", "attack_right", "attack_target_effect", "dead"]
    one, hd = {}, {}
    for t in order:
        if t not in tags:
            continue
        ms = DURATIONS.get(t, 80 if model != BARON else 60)
        anchor = meta["effect_anchor"] if t == "attack_target_effect" else meta["anchor"]
        pairs = [crop_pair(a, anchor, ppu) for a in tags[t]]
        hd["hd_" + t] = [(d, ms) for d, _ in pairs]
        one[t] = [(o, ms) for _, o in pairs]
    W, H = G.write_sheet(os.path.join(OUT_DIR, NAMES[model]), {**one, **hd}, share=True)
    if review:
        os.makedirs(review, exist_ok=True)
        for t, frs in tags.items():
            for k, a in enumerate(frs):
                Image.fromarray(a).save(os.path.join(review, f"{model}_{t}_{k + 1}.png"))
    print(f"{NAMES[model]}: sheet {W}x{H}, PPU {ppu}, " + ", ".join(f"{t} {len(v)}" for t, v in one.items())
          + f"; idle {one['idle'][0][0].shape[1]} / hd_idle {hd['hd_idle'][0][0].shape[1]} wide", flush=True)
    return meta


def main():
    global DES, ACT
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--designs", required=True, help="Codex's step-1 dragons-models folder")
    ap.add_argument("--actions", required=True, help="Codex's step-2 dragons-actions folder")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--review", default=None, help="also write every finished dense frame (full canvas) here")
    a = ap.parse_args()
    DES, ACT = a.designs, a.actions
    for model in a.only or MODELS:
        build(model, a.review)


if __name__ == "__main__":
    main()
