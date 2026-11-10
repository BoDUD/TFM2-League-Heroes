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
2. Drakes and the Elder: base = the design; idle = its wings flapping (wing_flap: the tips up 0 / 2 / 3 / 2 squares,
   the roots pinned, the body still - 0.2's sinking upper body squashed it); attack = the design with Codex's frame inside the moving zone only
   (League's attack1 moves only the neck, head and jaw: the squares whose silhouette moves in any attack frame, the
   central band, closed and filled, plus each frame's element where it differs strongly) - Codex redrew the whole body
   in every frame (a quarter of its squares the design's colour), which would shimmer; dead 1-6 = Codex's, each frame's
   main body put on the ground line (the lying frames were drawn 19 squares high), dead_6 at dead_5's height; dead 7 =
   dead_6 breaking into shards, dead 8 empty (as native). Attack frames 2-5 get the breath dragon_fx.py draws (gathering
   in the jaws, poured onto the ground in front of the feet, the blast there, the element's shockwave round the drake).
3. Baron: base = the design; idle = his legs flexing and his seams glowing (baron_idle); attack_left and dead 1-7 = Codex's, each frame's magenta spine
   over the design's and its bottom on the pit line, nothing under the line; attack frames 2-5 get the acid he spits at
   the side he bites (dragon_fx.spit), attack_right = attack_left mirrored (the design is symmetric); dead 2-3 a shock
   ring as he screams, 8-15 = dead_7 slumping back into the pit (dragon_fx.sink), 16 empty; the target effect = the acid
   splashing on the target (dragon_fx.splash, 7 frames, the target the frame's centre).
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
sys.path.insert(0, HERE)
import dragon_fx as fx  # noqa: E402

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


# the drakes' idle: the wings flap, everything else still (the user, 2026-11-10: 「小龙上下摆动会造成模型变形 请用别的
# 动作」 - 0.2's idle sank the upper body 0 / 2 / 4 / 2 squares behind the legs and squashed it)
WING_BAND = 0.20       # the body's half-width (head, neck, chest) over the design's width: never moves
WING_LEGS = 0.66       # the legs' line over the design's height: below it nothing moves
WING_LIFTS = (0, 1, 2, 3, 3, 2, 1, 0)   # squares the wing tips rise in the 8 idle frames (eased; the roots pinned)


def wing_flap(d, k):
    """the design with its wings raised: each wing column (outside the body band, above the legs' line) up by k x its
    distance out from the band, so the roots stay pinned and the tips rise k squares; where a wing column met the body at
    the legs' line its lowest rows stay to bridge the gap; the body drawn on top"""
    on = d[..., 3] > 0
    ys, xs = np.nonzero(on)
    top, bot = ys.min(), ys.max()
    cx, W = (xs.min() + xs.max() + 1) / 2, xs.max() + 1 - xs.min()
    leg = int(round(top + WING_LEGS * (bot + 1 - top)))
    dist = np.abs(np.arange(d.shape[1]) - cx + 0.5) - WING_BAND * W
    wing = on & (dist > 0)[None, :] & (np.arange(d.shape[0]) < leg)[:, None]
    body = d.copy()
    body[wing] = 0
    out = np.zeros_like(d)
    span = max(1.0, dist.max())
    for x in range(d.shape[1]):
        if dist[x] <= 0:
            continue
        s = int(round(k * dist[x] / span))
        col = np.where(wing[:, x, None], d[:, x], 0)
        if s:
            moved = np.concatenate([col[s:], np.zeros((s, 4), np.uint8)])
            if wing[leg - 1, x] and on[leg, x]:
                moved[leg - s:leg] = np.where(moved[leg - s:leg, 3:4] > 0, moved[leg - s:leg], d[leg - s:leg, x])
            col = moved
        out[:, x] = col
    return over(body, out)


# the drakes' attack (the user, 2026-11-10: 「攻击特效看起来好像没有」, then 「小龙攻击的时候火焰不够大啊 看不出来在攻击」
# 「大龙 远古龙应该也是 看不出喷射的火焰」 - Codex's breath is a puff on the chest): frame 2 the breath gathering in the jaws,
# 3-5 the breath poured from the lowered head onto the ground in front of the feet, the blast there, and the native
# serpen's shockwave (its frames 3-5 draw a ring round itself, radius 96 / 98 / 111 game px) made of the element -
# dragon_fx.py draws them
RINGS = (160.0, 180.0, 200.0)   # the shockwave's radius in attack frames 3, 4, 5 (squares)
RING_MARGIN = 220               # squares every drake canvas is padded by on each side so the shockwave fits
# the jaws, squares under the anchor, read off Codex's frames (a ruler every 10 squares): of the raised head in attack
# frame 2 (the breath gathers there) and of the lowered head in frame 3 (it leaves there); the heads are centred
JAWS = {
    "infernal": (-19.5, 30.5), "mountain": (-17.5, 38.5), "ocean": (-18.5, 34.5), "cloud": (-17.5, 34.5),
    "hextech": (-13.5, 36.5), "chemtech": (-13.5, 32.5), "elder": (-33.5, 30.5),
}


def pad(a, m):
    return np.pad(a, ((m, m), (m, m), (0, 0)))


def drake_frames(model):
    d = READ[model]["design_flat"]
    ys = np.nonzero(d[..., 3].any(1))[0]
    top, bot = ys.min(), ys.max()                      # bot: the soles' last row
    tags = {"base": [d]}
    tags["idle"] = [wing_flap(d, k) for k in WING_LIFTS]
    _, fr, zs = zones(model)
    tags["attack"] = [np.where(zs[n][..., None], fr[n], d) for n in sorted(fr)]
    anchor = (128.0, bot + 1 - 66.5)
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
    # every frame padded (the shockwave reaches 230 squares round the anchor), then the breath
    tags = {t: [pad(a, RING_MARGIN) for a in frs] for t, frs in tags.items()}
    big = (anchor[0] + RING_MARGIN, anchor[1] + RING_MARGIN)
    glow = (big[0], big[1] + JAWS[model][0])
    mouth = (big[0], big[1] + JAWS[model][1])
    tags["attack"] = fx.drake_attack(tags["attack"], big, model, mouth, bot + RING_MARGIN, RINGS, glow)
    meta = {"ppu": 1.8, "anchor": list(big), "dead_dy": dys, "wing_lifts": WING_LIFTS, "durations": DRAKE_MS,
            "mouth": list(mouth), "glow": list(glow)}
    return tags, meta


# Baron's idle (the user, 2026-11-10: 「大龙的动作也是上下摆动 很僵硬」 - 0.2 sank him 0 / 2 / 4 / 2 squares into the
# pit; then 「大龙左右晃动模型变形啊」 - 0.3.0's sway sheared the rows, slanting his heads and horn): his body, heads and
# horn never move; his six clawed legs flex (each leg's root by the body pinned, its claw lifted up to ARM_LIFT squares,
# eased, the right legs a quarter of the cycle behind the left), and the magenta seams on his back and his eyes glow
# brighter and fade like breathing (the palette's magentas swapped for lighter ones, no pixel moved)
BARON_IDLE_N = 16                 # frames (100 ms each)
ARM_BAND = 24                     # squares either side of his middle that are his body (the legs start outside it)
ARM_TOP = 56                      # squares over the pit line where his legs start (above it: his heads)
ARM_LIFT = 3.0                    # squares a claw tip rises at most
GLOW = {   # Codex's magentas -> a step lighter, two steps lighter
    (246, 3, 252): ((250, 84, 252), (255, 150, 255)),
    (219, 6, 233): ((240, 40, 246), (250, 92, 252)),
    (186, 3, 202): ((214, 10, 228), (232, 32, 240)),
    (161, 2, 182): ((186, 4, 204), (206, 8, 222)),
}


def baron_idle(d, pit, k):
    """idle frame k of BARON_IDLE_N: the legs lifted (column by column, the further from his body the more), the glow"""
    n = BARON_IDLE_N
    on = d[..., 3] > 0
    ys, xs = np.nonzero(on)
    cx = (xs.min() + xs.max() + 1) / 2
    out = d.copy()
    for side, lag in ((-1, 0.0), (1, 0.25)):
        ease = 0.5 - 0.5 * np.cos(2 * np.pi * ((k / n - lag) % 1.0))
        inner = cx + side * ARM_BAND
        reach = abs((xs.min() if side < 0 else xs.max()) - inner)
        for x in range(d.shape[1]):
            off = (inner - x) * -side
            if off <= 0:
                continue
            lift = int(round(ARM_LIFT * ease * (off / reach) ** 0.9))
            if lift == 0:
                continue
            col = d[:, x].copy()
            arm = np.zeros(d.shape[0], bool)
            arm[pit - ARM_TOP:pit + 1] = on[pit - ARM_TOP:pit + 1, x]
            new = col.copy()
            new[arm] = 0
            yy = np.nonzero(arm)[0]
            new[yy - lift] = col[yy]
            out[:, x] = new
    p = 0.5 - 0.5 * np.cos(2 * np.pi * k / n)
    level = 0 if p < 0.35 else (1 if p < 0.75 else 2)
    if level:
        rgb = out[..., :3]
        for src, steps in GLOW.items():
            m = (out[..., 3] > 0) & np.all(rgb == np.array(src, np.uint8), axis=-1)
            rgb[m] = steps[level - 1]
    return out


def baron_frames():
    d = READ[BARON]["design_flat"]
    ys = np.nonzero(d[..., 3].any(1))[0]
    pit = ys.max()                                    # the pit line's last row
    sx0 = spine_x(d)
    tags = {"base": [d]}
    tags["idle"] = [baron_idle(d, pit, k) for k in range(BARON_IDLE_N)]
    al, notes = [], {}
    for k in range(1, 6):
        a = READ[BARON][f"attack_left_{k}"]
        al.append(place(a, sx0, pit, notes, f"attack_left_{k}"))
    tags["attack_left"] = al
    tags["dead"] = [place(READ[BARON][f"dead_{k}"], sx0, pit, notes, f"dead_{k}") for k in range(1, 8)]
    # every frame padded (the spat acid reaches 150 squares out of his jaws)
    M = BARON_MARGIN
    tags = {t: [pad(a, M) for a in frs] for t, frs in tags.items()}
    pitp = pit + M
    anchor = (85.0 + M, pit + 1 - 82.5 + M)
    # the bite (the user, 2026-11-10: 「大龙没有攻击特效」「大龙 远古龙应该也是 看不出喷射的火焰」): frame 2 the acid
    # gathering in the biting head's jaws, 3 spat out toward the side he bites at, 4 its tail and drops, 5 drops falling
    spat, mouths = [], []
    for i, a in enumerate(tags["attack_left"]):
        if i >= 1:
            mx, my = mouth_left(a)
            mouths.append([mx, my])
            a = over(fx.spit(a.shape[:2], (mx, my), (mx + SPIT_AIM[0], my + SPIT_AIM[1]), i - 1, 51 + i), a)
        spat.append(a)
    tags["attack_left"] = spat
    tags["attack_right"] = [np.ascontiguousarray(a[:, ::-1]) for a in spat]
    # the death (the user: 「大龙的死亡帧还是没有」): Codex's 7 poses with a shock ring as he screams (2, 3), then he
    # slumps back into his pit, melting at the pit line (8 frames), then nothing
    dd = tags["dead"]
    dd[1] = over(dd[1], fx.roar(dd[1].shape[:2], (anchor[0], pitp - 6), 66.0))
    dd[2] = over(dd[2], fx.roar(dd[2].shape[:2], (anchor[0], pitp - 6), 92.0, seed=82))
    dd += fx.sink(dd[-1], pitp, SINK_STEPS)
    dd.append(np.zeros_like(dd[0]))
    tags["dead"] = dd
    tags["attack_target_effect"] = [fx.splash(k, EFX) for k in range(7)]
    meta = {"ppu": 1.5, "anchor": list(anchor), "spine": sx0, "placed": notes, "durations": BARON_MS,
            "effect_anchor": [EFX / 2, EFX / 2], "mouths": mouths}
    return tags, meta


BARON_MARGIN = 130                  # squares every Baron canvas is padded by on each side so the spat acid fits
SPIT_AIM = (-118.0, 24.0)           # where the spit flies from the jaws (squares; attack_left, mirrored for the right)
SINK_STEPS = (0.06, 0.15, 0.26, 0.39, 0.53, 0.68, 0.84, 0.96)   # how far into the pit, death frames 8-15
EFX = 150                           # the target effect's dense canvas (squares, square), the target at its centre


def mouth_left(a):
    """the biting head's jaws in an attack_left frame: the leftmost drawn square in the rows of his heads (the snout's
    tip, 35-75 squares under his top), 4 squares in and 3 down"""
    m = a[..., 3] > 0
    top = np.nonzero(m.any(1))[0].min()
    sub = m[top + 35:top + 75]
    x = np.nonzero(sub.any(0))[0].min()
    yy = np.nonzero(sub[:, x])[0]
    return float(x + 4), float(top + 35 + yy.mean() + 3)


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


DRAKE_MS = {"idle": [110] * 8, "dead": [100, 110, 120, 150, 240, 240, 180, 120]}
BARON_MS = {"idle": [100] * BARON_IDLE_N,
            "dead": [90, 110, 100, 100, 110, 130, 170] + [90] * 7 + [100] + [60]}   # 1.6 s: the poses, the sinking, nothing
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
        per = meta.get("durations", {}).get(t)
        ms = [per[k] if per else DURATIONS.get(t, 80 if model != BARON else 60) for k in range(len(tags[t]))]
        anchor = meta["effect_anchor"] if t == "attack_target_effect" else meta["anchor"]
        pairs = [crop_pair(a, anchor, ppu) for a in tags[t]]
        hd["hd_" + t] = [(d, m) for (d, _), m in zip(pairs, ms)]
        one[t] = [(o, m) for (_, o), m in zip(pairs, ms)]
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
