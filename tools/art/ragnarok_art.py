#!/usr/bin/env python3
"""The ragnarok pack's sheets from Codex's deliveries: one engine, each hero's import_<hero>.py its settings.

Codex draws a ragnarok hero in 128 x 128 cells, the soles' point at SOLE, eight actions of eight frames and an effect
sheet of eight pictures - dense frames already. Here (tools/art/import_lubu.py has the long story):
- the swing pictures go into the hero's own frames (BAKE): the client never mirrors an effect picture and does mirror
  his frames; each effect frame on the body frame showing at that moment, its cell's centre at the soles plus Codex's
  anchor, the body frames cut where an effect frame starts or ends;
- the 1x frames: each dense frame brought to 1 / PPU squares by pixel_down.pixelate, the pivot 11.5 game px over the
  soles at the centre of an odd frame;
- the dense frames: assets/source/ppu/<hero>_<tag>.png, each round(PPU x its 1x frame) - ppu_hd.py then writes hd_ / lo_;
- the effects played on units: ragnarok/effects/ragnarok_<hero>_fx, 1x by pixel_down.scale_fx with hd_ twins.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as D  # noqa: E402
import strips as G  # noqa: E402

PPU_DIR = os.path.join(ROOT, "assets", "source", "ppu")
MOD = os.path.join(ROOT, "ragnarok")
FEET = 11.5                 # game px from a frame's pivot (its centre) down to the soles
ACTIONS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
# the hero being imported (setup): Codex's folder, ids, PPU, the soles' point, the baked swings, retimed actions, the
# pictures played on units - each hero's import_<hero>.py holds them
SRC = ID = HERO = SHEET = FX_SHEET = PROJ_SHEET = PPU = FX_PPU = SOLE = None
BAKE, RETIME, TARGET_FX, SPLIT, PROJ_FX, EXTRA_FX, SHIFT = [], {}, {}, {}, {}, [], {}
TAGS, BANKS = ACTIONS, None
# 别的包用这个引擎时的设定（tools/art/import_<英雄>.py 给，不给就是终末包原来的做法）：
# BODY_STEM / FX_STEM：Codex 的身体图、特效图叫什么；BLEND：画进身体帧的特效按透明度叠（Codex 的特效边上是半透明的，
# 直接盖上去身子会透出底色）；FX_MAKE(fx) -> {新标签: 帧}：从交来的特效另做几组（拆开、停住某帧、翻转、转平、加长）；
# SCALE_FX：特效缩成 1 倍用的函数（默认 pixel_down.scale_fx）；PROJ_IDLE：弹道图也带空的 idle / hd_idle
BODY_STEM = FX_STEM = None
BLEND, FX_MAKE, SCALE_FX, PROJ_IDLE = False, None, None, False


def setup(cfg):
    """Point the engine at one hero (a dict of the names above)."""
    global CW, CH, CS, MOD, BODY_STEM, FX_STEM, BLEND, FX_MAKE, SCALE_FX, PROJ_IDLE
    global SRC, ID, HERO, SHEET, FX_SHEET, PROJ_SHEET, PPU, FX_PPU, SOLE, BAKE, RETIME, TARGET_FX, SPLIT, PROJ_FX, EXTRA_FX, SHIFT
    global TAGS, BANKS
    SRC, ID, HERO, PPU, SOLE = cfg["SRC"], cfg["ID"], cfg["HERO"], cfg["PPU"], cfg["SOLE"]
    # MOD：包的文件夹（边境巡团是 border/），不给就是 ragnarok/
    MOD = cfg.get("MOD", os.path.join(ROOT, "ragnarok"))
    BODY_STEM, FX_STEM = cfg.get("BODY_STEM", f"{ID}_native"), cfg.get("FX_STEM", f"{ID}_fx_native")
    BLEND, FX_MAKE, SCALE_FX = cfg.get("BLEND", False), cfg.get("FX_MAKE"), cfg.get("SCALE_FX")
    PROJ_IDLE = cfg.get("PROJ_IDLE", False)
    # CANVAS：合成用的画布（宽、高、脚底点），格子比 128 大时跟着放大（亚当、宙斯按两倍重出，一格 256）
    CW, CH, CS = cfg.get("CANVAS", (288, 224, (144, 176)))
    # FX_PPU: the effect sheets' own density (the pictures on units and the projectile pictures keep their size when
    # the hero is drawn smaller: Lu Bu at 1.94 since 2026-11-20, his effects at Codex's 1.65); his baked swings follow him
    FX_PPU = cfg.get("FX_PPU", PPU)
    BAKE, RETIME, TARGET_FX = cfg["BAKE"], cfg["RETIME"], cfg["TARGET_FX"]
    # SPLIT {action: [(new tag, its first body frame), ...]}: parts of an action that only an event plays (Thor's empty
    # hands while the hammer flies, his catch on its real return), cut off in order; PROJ_FX {tag: centre}: pictures a
    # projectile carries (drawn at 1x, turned with its flight)
    SPLIT, PROJ_FX = cfg.get("SPLIT", {}), cfg.get("PROJ_FX", {})
    # EXTRA_FX: more of Codex's effect sheets (stems of <stem>#sheet.png / #anim.fanim), their tags added to the effects
    # (Lu Bu's Sky Eater wave came on its own in the first redraw round)
    EXTRA_FX = cfg.get("EXTRA_FX", [])
    # SHIFT {action: dx}: an action Codex drew off his soles' point, moved whole by dx dense px (a plain move, nothing
    # redrawn): Thor's idle stands 7 px forward of his run and attack, he would hop forward each time he stops.
    # dx 也可以按帧给一串（每个身体帧一个）：波塞冬重画的跑步，人在格子里前后滑，逐帧挪回原来的位置；画进帧里的特效跟着挪
    SHIFT = cfg.get("SHIFT", {})
    # BANKS [(Codex 的图名, {它的标签: 本表的标签})]：一个英雄几张身体图（宙斯三种形态各一张、变身过渡一张）按顺序合成一张，
    # 标签照表改名（膨胀的 idle -> mu_idle）；不给就是 <ID>_native 一张、标签原样。TAGS 是合成后本表的动作，顺序就是图里的顺序
    BANKS = cfg.get("BANKS")
    TAGS = tuple(cfg.get("TAGS", ACTIONS))
    SHEET = os.path.join(MOD, "champions", ID)
    FX_SHEET = os.path.join(MOD, "effects", f"{ID}_fx")
    PROJ_SHEET = os.path.join(MOD, "effects", f"{ID}_proj")


def tags():
    """The sheet's tags: the eight actions and the ones SPLIT cuts off them."""
    return list(TAGS) + [new for parts in SPLIT.values() for new, _ in parts]


def idle_pair():
    """The empty idle / hd_idle pair an effect sheet carries for hd_engine to read its FX_PPU from: a width w with FX_PPU x w
    whole (1.65 x 20 = 33)."""
    w = min(range(12, 41), key=lambda n: (abs(n * FX_PPU - round(n * FX_PPU)), n))
    return w, round(w * FX_PPU)


def read(stem):
    px = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        fr = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), float(f_["duration"])))
        out[tag] = fr
    return out


def over(dst, src, x, y):
    """src alpha-composited onto dst with its top-left at (x, y) (hard alpha: src's opaque pixels win)."""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    m = s[..., 3] > 0
    d = dst[y0:y1, x0:x1]
    d[m] = s[m]


def blend(dst, src, x, y):
    """src 按透明度叠在 dst 上（src-over），左上角在 (x, y)：半透明的特效盖在身上，底下的颜色透上来，不会把身子挖透。"""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float64) / 255
    d = dst[y0:y1, x0:x1].astype(np.float64) / 255
    sa, da = s[..., 3:4], d[..., 3:4]
    oa = sa + da * (1 - sa)
    oc = (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-9)
    out = np.round(np.concatenate([oc, oa], -1) * 255)
    dst[y0:y1, x0:x1] = np.where(oa > 0, out, 0).astype(np.uint8)


def no_specks(a, under=4):
    """Pieces of fewer than `under` pixels apart from everything else go (the user's rule for every frame: 「别留多余的
    像素」; ppu_hd.drawn_strays flags them): the charge's first one-pixel glints, a grain of dust by his knee."""
    from scipy import ndimage
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if not n:
        return a
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    small = np.zeros(n + 1, bool)
    small[1:] = sizes < under
    out = a.copy()
    out[small[lab]] = 0
    return out


# the composing canvas: room for the widest swing round the soles
CW, CH, CS = 288, 224, (144, 176)


def baked(body, fx):
    """{action: [(dense frame on the canvas, seconds)]}: the body frames with the BAKE pictures, cut where an effect
    frame starts or ends."""
    out = {}
    for tag in TAGS:
        frames = body[tag]
        durs = RETIME.get(tag, [d for _, d in frames])
        starts = np.cumsum([0.0] + durs[:-1])
        end = float(sum(durs))
        bakes = [b for b in BAKE if b[0] == tag]
        shift = SHIFT.get(tag, 0)
        cuts = {0.0, end} | {float(s) for s in starts}
        plays = []
        for b in bakes:
            _, name, t0, anchor, step = b[:5]
            origin = b[5] if len(b) > 5 else (64, 64)
            # 第 7 项 "behind"：画在身子后面（索尔大招蓄力的雷圈围着锤头，锤子横在胸前、竖在身前时画在前面会从脸上划过）
            behind = len(b) > 6 and b[6] == "behind"
            fr = fx[name]
            dt = step if step is not None else fr[0][1]
            for j in range(len(fr) + 1):
                t = t0 + j * dt
                if t < end:
                    cuts.add(round(t, 6))
            plays.append((name, t0, anchor, dt, fr, origin, behind))
        cuts = sorted(c for c in cuts if c <= end)
        segs = []
        for a, b in zip(cuts, cuts[1:]):
            if b - a < 1e-6:
                continue
            i = int(np.searchsorted(starts, a + 1e-9, side="right") - 1)
            dx = shift[i] if isinstance(shift, (list, tuple)) else shift
            canvas = np.zeros((CH, CW, 4), np.uint8)
            for layer in ("behind", "body", "front"):
                if layer == "body":
                    over(canvas, frames[i][0], CS[0] - SOLE[0] + dx, CS[1] - SOLE[1])
                    continue
                for name, t0, anchor, dt, fr, (ox, oy), behind in plays:
                    if behind != (layer == "behind"):
                        continue
                    j = int(np.floor((a - t0) / dt + 1e-9))
                    if 0 <= j < len(fr):
                        # 锚点也可以按身体帧给一串，特效跟着身体走（亚当睁眼的光跟着头）
                        ax, ay = anchor[i] if isinstance(anchor, list) else anchor
                        (blend if BLEND else over)(canvas, fr[j][0], CS[0] + ax - ox + dx, CS[1] + ay - oy)
            canvas = no_specks(canvas)
            if segs and np.array_equal(segs[-1][0], canvas) and segs[-1][2] == i:
                segs[-1] = (canvas, segs[-1][1] + (b - a), i)
            else:
                segs.append((canvas, b - a, i))
        if tag in SPLIT:
            parts = SPLIT[tag]
            bounds = [first for _, first in parts] + [len(frames)]
            for (new, first), last in zip(parts, bounds[1:]):
                out[new] = [(c, d) for c, d, k in segs if first <= k < last]
            segs = [s_ for s_ in segs if s_[2] < bounds[0]]
        out[tag] = [(c, d) for c, d, _ in segs]
    return out


def outline_of(frames):
    return D.edge_colour(np.concatenate([f for f, _ in frames], axis=1))


def one_x(dense, pivot, outline, pal):
    """A dense canvas -> (the 1x frame, odd, its pivot at the centre; the pivot's pixel)."""
    c = PPU
    px, py = pivot
    small, (nx, ny) = D.pixelate(dense, 1.0 / c, (px - c / 2, py - c / 2), outline, pal)
    op = small[..., 3] > 0
    if not op.any():
        return np.zeros((1, 1, 4), np.uint8)
    ys, xs = np.nonzero(op)
    rx = max(nx - xs.min(), xs.max() - nx)
    ry = max(ny - ys.min(), ys.max() - ny)
    W, H = 2 * rx + 1, 2 * ry + 1
    f = np.zeros((H, W, 4), np.uint8)
    f[ys - ny + ry, xs - nx + rx] = small[ys, xs]
    return f


def dense_of(dense, pivot, size):
    """The dense frame of `size` (W, H) cut round the pivot at its centre."""
    W, H = size
    px, py = pivot
    x0, y0 = int(round(px - W / 2)), int(round(py - H / 2))
    out = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(dense.shape[1], x0 + W), min(dense.shape[0], y0 + H)
    out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = dense[sy0:sy1, sx0:sx1]
    lost = dense[..., 3].sum() - out[..., 3].sum()
    if lost:
        sys.exit(f"a dense frame lost {lost / 255:.0f} pixels outside round(PPU x its 1x frame) - widen the 1x frame")
    return out


def hero_sheets(body, fx):
    """-> ({tag: [(1x frame, ms)]}, {tag: [dense frame of round(PPU x 1x)]})."""
    segs = baked(body, fx)
    every = [f for tag in tags() for f, _ in segs[tag]]
    outline = D.edge_colour(np.concatenate(every, axis=1))
    pal = D.palette_of(np.concatenate([body[t][0][0] for t in TAGS], axis=1), 96)
    pivot = (CS[0], CS[1] - FEET * PPU)
    ones, denses = {}, {}
    for tag in tags():
        ones[tag], denses[tag] = [], []
        for canvas, secs in segs[tag]:
            f1 = one_x(canvas, pivot, outline, pal)
            h1, w1 = f1.shape[:2]
            # the dense frame must hold the whole picture: grow the 1x frame alike at both ends until it does
            while True:
                size = (round(w1 * PPU), round(h1 * PPU))
                try:
                    d = dense_of(canvas, pivot, size)
                    break
                except SystemExit:
                    w1, h1 = w1 + 2, h1 + 2
            if (h1, w1) != f1.shape[:2]:
                g = np.zeros((h1, w1, 4), np.uint8)
                oy, ox = (h1 - f1.shape[0]) // 2, (w1 - f1.shape[1]) // 2
                g[oy:oy + f1.shape[0], ox:ox + f1.shape[1]] = f1
                f1 = g
            ones[tag].append((f1, round(secs * 1000, 3)))
            denses[tag].append(d)
    return ones, denses


def fx_sheet(fx):
    """{tag: [(frame, ms)]} of TARGET_FX: each tag's 1x frames (pixel_down.scale_fx, centred on its point) and their
    hd_ twins (Codex's own frames cut round the same point, round(FX_PPU x the 1x frame)), plus the empty `idle` /
    `hd_idle` pair hd_engine reads the sheet's FX_PPU from (20 x 20 and 33 x 33: 1.65 x 20 is whole)."""
    w1, wd = idle_pair()
    out = {"idle": [(np.zeros((w1, w1, 4), np.uint8), 100.0)]}
    dense = {"hd_idle": [(np.zeros((wd, wd, 4), np.uint8), 100.0)]}
    for name, (px, py) in TARGET_FX.items():
        frames, twins = [], []
        for a, secs in fx[name]:
            small, (nx, ny) = scale_fx(a, 1.0 / FX_PPU, (px, py))
            op = small[..., 3] > 0
            rx = ry = 1
            if op.any():
                ys, xs = np.nonzero(op)
                rx = int(np.ceil(max(nx - xs.min(), xs.max() + 1 - nx)))
                ry = int(np.ceil(max(ny - ys.min(), ys.max() + 1 - ny)))
            # the dense twin must hold Codex's whole picture round the same centre
            ys2, xs2 = np.nonzero(a[..., 3] > 0)
            if len(xs2):
                rx = max(rx, int(np.ceil(max(px - xs2.min(), xs2.max() + 1 - px) / FX_PPU)))
                ry = max(ry, int(np.ceil(max(py - ys2.min(), ys2.max() + 1 - py) / FX_PPU)))
            W, H = 2 * rx, 2 * ry
            f = np.zeros((H, W, 4), np.uint8)
            if op.any():
                f[ys - int(ny) + ry, xs - int(nx) + rx] = small[ys, xs]
            frames.append((f, round(secs * 1000, 3)))
            twins.append((dense_of(a, (px, py), (round(W * FX_PPU), round(H * FX_PPU))), round(secs * 1000, 3)))
        out[name] = frames
        dense["hd_" + name] = twins
    return {**out, **dense}


def scale_fx(a, k, pivot):
    """特效缩成 1 倍：设定里给了 SCALE_FX 就用它，不然 pixel_down.scale_fx。"""
    if SCALE_FX is not None:
        return SCALE_FX(a, k, pivot)
    return D.scale_fx(a, k, pivot, mote=0)


def proj_sheet(fx, own=None):
    """{tag: [(1x frame, ms)]} of PROJ_FX: a projectile's picture, centred on its position, at 1x (a projectile's picture is
    dense only where hd_engine's full door is on; at 1x it is right everywhere)."""
    out = {}
    if PROJ_IDLE:
        # 和效果图一样带一对空的 idle / hd_idle（塞拉斯照搬特效图；这对图只说明密度，弹道的画面本身还是 1 倍）
        w1, wd = idle_pair()
        out = {"idle": [(np.zeros((w1, w1, 4), np.uint8), 100.0)], "hd_idle": [(np.zeros((wd, wd, 4), np.uint8), 100.0)]}
    own = own or {}
    for name, (px, py) in PROJ_FX.items():
        frames = []
        # 按整数倍放大读进来的（EXTRA_FX 给了倍数的）用原来那张按它自己的密度缩，缩出来和放大前一模一样
        src, k = own.get(name, (fx[name], 1))
        for a, secs in src:
            small, (nx, ny) = scale_fx(a, k / FX_PPU, (px / k, py / k))
            op = small[..., 3] > 0
            rx = ry = 1
            if op.any():
                ys, xs = np.nonzero(op)
                rx = int(np.ceil(max(nx - xs.min(), xs.max() + 1 - nx)))
                ry = int(np.ceil(max(ny - ys.min(), ys.max() + 1 - ny)))
            f = np.zeros((2 * ry, 2 * rx, 4), np.uint8)
            if op.any():
                f[ys - int(ny) + ry, xs - int(nx) + rx] = small[ys, xs]
            frames.append((f, round(secs * 1000, 3)))
        out[name] = frames
    return out


def strip(frames):
    """Dense frames left to right, 1 px gaps (ppu_hd.drawn_strip's layout)."""
    W = sum(f.shape[1] for f in frames) + len(frames) - 1
    H = max(f.shape[0] for f in frames)
    s = np.zeros((H, W, 4), np.uint8)
    x = 0
    for f in frames:
        s[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    return s


def main(cfg, doc=None):
    setup(cfg)
    ap = argparse.ArgumentParser(description=doc or __doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if BANKS:
        body = {}
        for stem, names in BANKS:
            got = read(os.path.join(SRC, stem))
            body.update({names[t]: got[t] for t in names})
    else:
        body = read(os.path.join(SRC, BODY_STEM))
    fx = read(os.path.join(SRC, FX_STEM))
    own = {}
    for stem in EXTRA_FX:
        # 也可以给（路径, 倍数）：按最近邻放大整数倍再用（吕布的斩波：身体和特效是两倍的，它没重画）；
        # 当弹道图用的时候还是拿原来那张缩（proj_sheet）
        stem, k = stem if isinstance(stem, tuple) else (stem, 1)
        got = read(stem)
        if k != 1:
            own.update({t: (fr, k) for t, fr in got.items()})
            got = {t: [(np.repeat(np.repeat(a, k, 0), k, 1), d) for a, d in fr] for t, fr in got.items()}
        fx.update(got)
    if FX_MAKE is not None:
        fx.update(FX_MAKE(fx))
    ones, denses = hero_sheets(body, fx)
    fxs = fx_sheet(fx)
    if a.check:
        bad = 0
        for tag, frames in denses.items():
            p = os.path.join(PPU_DIR, f"{HERO}_{tag}.png")
            if not os.path.isfile(p) or not np.array_equal(np.asarray(Image.open(p).convert("RGBA")), strip(frames)):
                print(f"{p}: differs")
                bad += 1
        sys.exit(1 if bad else 0)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    os.makedirs(os.path.dirname(FX_SHEET), exist_ok=True)
    os.makedirs(PPU_DIR, exist_ok=True)
    w, h = G.write_sheet(SHEET, ones)
    for tag, frames in denses.items():
        Image.fromarray(strip(frames)).save(os.path.join(PPU_DIR, f"{HERO}_{tag}.png"))
    fw, fh = G.write_sheet(FX_SHEET, fxs)
    if PROJ_FX:
        G.write_sheet(PROJ_SHEET, proj_sheet(fx, own))
    print(f"{ID}#sheet.png {w}x{h} (1x), {ID}_fx#sheet.png {fw}x{fh}; dense strips in {PPU_DIR}")
    for tag in tags():
        f = ones[tag][0][0]
        print(f"  {tag:7s} {len(ones[tag]):2d} frames, 1x {f.shape[1]}x{f.shape[0]}, "
              f"{sum(ms for _, ms in ones[tag]) / 1000:.2f} s")



