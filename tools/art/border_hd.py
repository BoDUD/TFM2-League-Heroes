#!/usr/bin/env python3
"""边境巡团的身体帧照 Codex v0.9.0 的高清帧重出：PPU 2.5，稍微有点像素感。

    python tools/art/border_hd.py [--hero <英雄> ...] [--check] [--review <文件夹>]

用户（2026-11-22）：「几乎全部重做了 我的要求是你利用PPU在这个高清帧的图片的基础上 稍微有点像素感 而不是想之前那样去
缩小模型 你这边也进行全部重做吧」「你需要比终末更有像素感一点 我是这个意思」。

Codex 交的（Border_Patrol_Mirror_Sea_Anime_HD_Redraw_v0.9.0.zip，不在仓库里，路径见 SRC_ZIP，环境变量 BORDER_HD_ZIP 可以改；
交接说明和帧表拷在 assets/source/border/hd_v090/）：每人 80 帧上下的单张 512 格高清立绘（厚涂，脚底 (256, 430)），站高
325-347 格。每个动作组是分开画的、大小不一样（同一人待机 300 格、跑步 333 格、出招 260-280 格），hd_frames.json 给了每组
相对跑步组的比例 relative_ppu（受击没写，和待机同一组）。

做法：
- 大小：每组先除以 relative_ppu 拉成和跑步组一样大，再整体乘 K（站高 340 格的人 = 41.5 个游戏像素 x PPU 2.5 = 104 格），
  十二人之间的高矮照 Codex 的。所以每个动作的头、身子一样大（「模型不要变大变小」），游戏里和联盟英雄一样高。
- 取样：原图先轻轻锐化，再按面积取平均缩进 256 格（脚底 (128, 184)，和原来的格子一样）；深色线条（眼睛、眉毛、轮廓线）
  在一格里占到 INK_SHARE 就取线条自己的颜色，不被肤色、衣服平均掉；盖住一半以上的格子才算人物，透明度只有全透、不透。
- 画风往联盟、云顶、终末的像素画靠（用户：「怎么感觉人物模型和其他几个mod画风极其割裂啊」；它们都是一圈深色描边、
  颜色饱和、明暗分得开）：
  · 提饱和、提对比（OKLab 里色度乘 SAT、亮度绕 0.55 乘 CONTRAST）；
  · 每人全部帧共用一套 COLOURS 色调色板（中位切分，不抖动），明暗一档一档的；
  · 描边加在轮廓外面一圈（OUTLINE_L：挨着它的那格颜色压到这么暗、色度乘 0.7，深棕、深蓝这种，不是纯黑）。七头身的
    手臂只有两三格宽，描边画在轮廓里面会把手臂吃成一根黑棍；脚底那行以下不加（人不往地里陷）。
- 帧表：帧数、每帧时长照 hd_frames.json（就是 v0.7.2 的帧表）。

写 assets/source/border/hd/border_<英雄>#sheet.png + #anim.fanim（一行一个动作，每行最多 COLS 格），import_<英雄>.py 读这里。
--check 只重算一遍和仓库里的比，不写文件；--review 另出每人一张总览（放大 2 倍）。
"""
import argparse
import io
import json
import os
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from border_fix import to_lab, to_rgb  # noqa: E402  OKLab

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(ROOT, "assets", "source", "border")
OUT = os.path.join(BASE, "hd")
SRC_ZIP = os.environ.get("BORDER_HD_ZIP", r"D:\TFM2-Workshop\border_patrol_packs\Border_Patrol_Mirror_Sea_Anime_HD_Redraw_v0.9.0.zip")
META = "docs/border_patrol/hd_frames.json"
HEROES = ("cenlei", "xiaolun", "dengmi", "zhumo", "fusuo", "yanxi", "yindu", "lanti", "luxin", "jiyan", "zhongli", "wuling")
ACTIONS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
PPU = 2.5                     # 和 tools/art/border_art.py、ppu_hd.py、addons/border/src/hd.rs 一致
REF_HEIGHT = 340              # Codex 跑步组站高的中位数（格）
GAME_HEIGHT = 41.5            # 联盟英雄站高的中位数（游戏像素）
K = GAME_HEIGHT * PPU / REF_HEIGHT
CELL, SOLE = 256, (128, 184)
COLS = 8
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
SHARPEN = dict(radius=2, percent=80, threshold=2)
INK_L, INK_SHARE, COVER = 70, 0.34, 0.5
SAT, CONTRAST = 1.3, 1.12
COLOURS = 32
OUTLINE_L = 0.20


def meta():
    with zipfile.ZipFile(SRC_ZIP) as z:
        return json.loads(z.read(META))["heroes"]


def scale_of(m, f):
    """这一帧的缩放：K / 这一组的 relative_ppu（受击没写，跟待机一组）。"""
    rel = f.get("relative_ppu")
    if rel is None:
        rel = next(x["relative_ppu"] for x in m["frames"]["idle"] if "relative_ppu" in x)
    return K / rel


def down(img, ax, ay, s):
    """512 格高清帧 -> 256 格：脚底 (ax, ay) 落到 SOLE，缩 s 倍；面积平均，深色线条按占比单独取色，透明度二值。"""
    a = np.asarray(img.convert("RGBA")).astype(np.float64)
    box = (ax - SOLE[0] / s, ay - SOLE[1] / s, ax + (CELL - SOLE[0]) / s, ay + (CELL - SOLE[1]) / s)
    pad = int(np.ceil(max(0, -box[0], -box[1], box[2] - a.shape[1], box[3] - a.shape[0]))) + 2
    a = np.pad(a, ((pad, pad), (pad, pad), (0, 0)))
    box = tuple(v + pad for v in box)
    al = a[..., 3] / 255
    lum = a[..., :3] @ np.array([0.30, 0.59, 0.11])
    ink = (lum < INK_L) & (al > 0.5)
    pm = a[..., :3] * al[..., None]

    def rs(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), "F").resize((CELL, CELL), Image.BOX, box=box)).astype(np.float64)
    cov = rs(al)
    col = np.dstack([rs(pm[..., k]) for k in range(3)])
    inkc = rs(ink * al)
    inkcol = np.dstack([rs(np.where(ink, pm[..., k], 0)) for k in range(3)])
    rgb = col / np.maximum(cov, 1e-6)[..., None]
    use_ink = inkc > INK_SHARE * np.maximum(cov, 1e-6)
    rgb = np.where(use_ink[..., None], inkcol / np.maximum(inkc, 1e-6)[..., None], rgb)
    out = np.zeros((CELL, CELL, 4), np.uint8)
    on = cov >= COVER
    out[on, :3] = np.clip(np.round(rgb[on]), 0, 255).astype(np.uint8)
    out[on, 3] = 255
    return out


def frame_job(args):
    """一帧：读 zip 里的 PNG，锐化，取样。（进程池里跑）"""
    path, ax, ay, s = args
    with zipfile.ZipFile(SRC_ZIP) as z:
        img = Image.open(io.BytesIO(z.read(path))).convert("RGBA")
    rgb = img.convert("RGB").filter(ImageFilter.UnsharpMask(**SHARPEN))
    img = Image.merge("RGBA", (*rgb.split(), img.getchannel("A")))
    return down(img, ax, ay, s)


def palette_of(frames, n=COLOURS):
    """全部帧的不透明像素一起取 n 色（中位切分，不抖动）-> 调色板图。"""
    pool = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames])
    side = int(np.ceil(np.sqrt(len(pool))))
    flat = np.zeros((side * side, 3), np.uint8)
    flat[:len(pool)] = pool
    flat[len(pool):] = pool[0]
    return Image.fromarray(flat.reshape(side, side, 3)).quantize(colors=n, method=Image.Quantize.MEDIANCUT,
                                                                   dither=Image.Dither.NONE)


def punch(f):
    """提饱和、提对比（OKLab）。"""
    on = f[..., 3] > 0
    if not on.any():
        return f
    lab = to_lab(f[on][:, :3].astype(np.float64))
    lab[:, 0] = np.clip(0.55 + (lab[:, 0] - 0.55) * CONTRAST, 0, 1)
    lab[:, 1:] *= SAT
    g = f.copy()
    g[on, :3] = np.clip(to_rgb(lab), 0, 255).astype(np.uint8)
    return g


def finish(f, pal):
    """套调色板；轮廓外面加一圈深色描边（挨着的那格颜色压暗），脚底那行以下不加。"""
    g = f.copy()
    on = f[..., 3] > 0
    q = np.asarray(Image.fromarray(f[..., :3]).quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB"))
    g[on, :3] = q[on]
    ring = ndimage.binary_dilation(on, structure=CROSS) & ~on
    ring[SOLE[1]:] = False
    if ring.any():
        iy, ix = ndimage.distance_transform_edt(~on, return_distances=False, return_indices=True)
        lab = to_lab(g[iy[ring], ix[ring], :3].astype(np.float64))
        lab[:, 0] = np.minimum(lab[:, 0], OUTLINE_L)
        lab[:, 1:] *= 0.7
        g[ring, :3] = np.clip(to_rgb(lab), 0, 255).astype(np.uint8)
        g[ring, 3] = 255
    return g


def build(hero, m, pool):
    ax, ay = m["foot_anchor"]
    jobs, durs = [], []
    for t in ACTIONS:
        for f in m["frames"][t]:
            jobs.append((f["path"], ax, ay, scale_of(m, f)))
            durs.append((t, f["duration_ms"] / 1000))
    raw = [punch(f) for f in pool.map(frame_job, jobs)]
    pal = palette_of(raw)
    frames = [finish(f, pal) for f in raw]
    # 排表：一行一个动作，每行最多 COLS 格
    rows, anims, y = [], {}, 0
    k = 0
    for t in ACTIONS:
        n = len(m["frames"][t])
        nrows = (n + COLS - 1) // COLS
        anims[t] = {"frames": []}
        for i in range(n):
            x, yy = (i % COLS) * CELL, (y + i // COLS) * CELL
            anims[t]["frames"].append({"duration": round(durs[k][1], 4), "data": {"x": x, "y": yy, "w": CELL, "h": CELL}})
            rows.append((frames[k], x, yy))
            k += 1
        y += nrows
    sheet = np.zeros((y * CELL, COLS * CELL, 4), np.uint8)
    for f, x, yy in rows:
        sheet[yy:yy + CELL, x:x + CELL] = f
    return sheet, {"anims": anims}


def review(hero, sheet, doc, folder, S=2):
    """每个动作一行，每帧人物那一块放大 S 倍。"""
    cells = []
    for t, a in doc["anims"].items():
        row = [sheet[f["data"]["y"]:f["data"]["y"] + CELL, f["data"]["x"]:f["data"]["x"] + CELL] for f in a["frames"]]
        cells.append((t, row))
    box = (40, 40, 216, 200)
    w, h = (box[2] - box[0]) * S, (box[3] - box[1]) * S
    W = max(len(r) for _, r in cells) * (w + 4)
    img = Image.new("RGBA", (W, len(cells) * (h + 16)), (30, 30, 30, 255))
    d = ImageDraw.Draw(img)
    for r, (t, row) in enumerate(cells):
        for i, f in enumerate(row):
            bg = Image.new("RGBA", (CELL, CELL), (112, 128, 104, 255))
            bg.alpha_composite(Image.fromarray(f))
            img.paste(bg.crop(box).resize((w, h), Image.NEAREST), (i * (w + 4), r * (h + 16) + 14))
            d.text((i * (w + 4) + 2, r * (h + 16)), f"{t} {i + 1}", fill=(255, 255, 255, 255))
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, f"hd_{hero}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hero", nargs="*", default=list(HEROES))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    ms = meta()
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    with ProcessPoolExecutor() as pool:
        for hero in a.hero:
            sheet, doc = build(hero, ms[hero], pool)
            stem = os.path.join(OUT, f"border_{hero}")
            text = json.dumps(doc, ensure_ascii=False, indent=1)
            if a.check:
                same = (os.path.exists(stem + "#sheet.png")
                        and np.array_equal(np.asarray(Image.open(stem + "#sheet.png").convert("RGBA")), sheet)
                        and open(stem + "#anim.fanim", encoding="utf-8-sig").read() == text)
                print(hero, "same" if same else "DIFFERENT")
                bad += not same
                continue
            Image.fromarray(sheet).save(stem + "#sheet.png", optimize=True)
            with open(stem + "#anim.fanim", "w", encoding="utf-8") as f:
                f.write(text)
            ys = np.nonzero((sheet[:CELL, :CELL, 3] > 0).any(1))[0]
            print(hero, "frames", sum(len(v["frames"]) for v in doc["anims"].values()),
                  "idle height", ys.max() - ys.min() + 1, "sheet", sheet.shape[1], "x", sheet.shape[0])
            if a.review:
                review(hero, sheet, doc, a.review)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
