#!/usr/bin/env python3
"""图奇（league_twitch）跑步给 Codex 重画的素材包（用户 2026-11-22：「老鼠的跑步姿势有点怪 让codex帮忙重做一下」）。

游戏里现在的 run（rig_twitch_hd.py：Codex 早先整帧重画、casts_twitch_hd.py 贴回设计图，每帧换上设计图的头、
「the run's head steady」）：头、背包、弩八帧钉在一个地方，弩一直平端；两条腿在斗篷下只挪小碎步，脚尖吊着点地；
第 7 帧整个人往上窜一截。英雄联盟的 run（twitch_base_run，我们的镜头）是压低身子往前蹿：身子前倾、两步一圈，
腿大步交替，远侧那只手往后甩，尾巴和破斗篷在身后甩。

设计图（hd/design.png，PPU 2.2，109 x 71，用户自己那张画读回来的）和英雄联盟的模型比例差得多（设计姿势贴合度 0.60：
联盟的耳朵更高，我们的头更靠前、弩更长、尾巴卷得多），联盟的剪影不能直接当影子。所以模板里的影子只放设计图的
头（casts_twitch_hd.HEAD_POLY：耳朵、护目镜、咧着的嘴）和弩（BOW_POLY，连握弩的手和弩上的绿药罐），按联盟每帧
头的前后（native_pose 量的「head x from the design pose」）和起伏（轮廓顶的高低，减半）挪；身子前倾、腿、手、
斗篷、尾巴让 Codex 照联盟同一帧画。

    python tools/lol/native_pose.py assets/source/twitch/poses.json --out <work>/native --alpha --tag run
    python tools/art/pack_twitch_run.py --native <work>/native --out <pack>

写出 <pack>/：templates/run_1.png、run_2.png（各 2048 x 1920，2 x 2 格，每格 1024 x 960，一格设计图 = 8 像素），
refs/ 四张图，以及 <pack> 旁边的 twitch_run_pack.zip（提示词 assets/source/twitch/RUN_PROMPT.md 一起放进去）。
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

SRC = os.path.join(ROOT, "assets", "source", "twitch")
DESIGN = os.path.join(SRC, "hd", "design.png")
PICTURE = os.path.join(SRC, "hd", "raw", "twitch-user.png")
SQ = 8                                   # 模板里一格设计图多少像素
CELL = (1024, 960)
PIVOT = (64, 60)                         # 十字所在的格：站位点，也是游戏里这一帧的中心
GROUND = PIVOT[1] + 25                   # 地面线所在的格：站位点往下 11.5 游戏像素 x PPU 2.2 = 25 格（ppu_rig.FEET）
PIVOT_COL = 53                           # 设计图里站的那一列（casts_twitch_hd.PIVOT_COL）
SOLE_ROW = 70                            # 设计图最低一行脚爪（casts_twitch_hd.GROUND = 71 是它下面一行）
HEAD_POLY = [(43, 0), (56, 0), (57, 7), (65, 4), (77, 0), (79, 12), (85, 19), (85, 29), (80, 37), (70, 37),
             (63, 33), (57, 29), (52, 24), (43, 22)]
# 弩：胸前握把往右到弩头，连上面的绿药罐、握弩的手和往右伸的弩弦
BOW_POLY = [(54, 38), (64, 36), (75, 33), (85, 35), (96, 37), (109, 37), (109, 57), (92, 57), (80, 55), (66, 50),
            (56, 48), (54, 44)]
# 每帧头和弩往前（DX）、往下（DY）挪几格。DX：native_pose 量的联盟 run 每帧头比设计姿势靠前多少
# （+1.4 +2.4 +2.7 +2.7 +2.7 +2.3 +1.2 +0.8 游戏像素）x 2.25 格（设计图 71 行对联盟设计姿势 31.6 像素高）；
# DY：联盟每帧轮廓顶比最高那帧低多少（0.5 0 3.4 4.1 0.6 0.3 3.4 4.0 像素）x 2.25 再减半，两步一圈两高两低
DX = [3, 5, 6, 6, 6, 5, 3, 2]
DY = [1, 0, 4, 5, 1, 0, 4, 5]


def font(n):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", n)
    except OSError:
        return ImageFont.load_default()


def poly(pts, shape):
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    return np.array(img, bool)


def ghost(d):
    """设计图里头和弩那些方块，冲淡成浅灰（留一点明暗，看得出护目镜、牙和弩的结构）。"""
    op = d[..., 3] > 0
    m = (poly(HEAD_POLY, d.shape) | poly(BOW_POLY, d.shape)) & op
    lum = d[..., :3].astype(float) @ np.array([0.3, 0.55, 0.15])
    g = (200 + lum / 255.0 * 45).astype(np.uint8)
    out = np.zeros(d.shape, np.uint8)
    out[m, 0] = out[m, 1] = out[m, 2] = g[m]
    out[m, 3] = 255
    return out


def cell(g, k):
    im = Image.new("RGBA", CELL, (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CELL[0] - 1, CELL[1] - 1], outline=(170, 170, 170))
    d.text((10, 8), str(k + 1), fill=(120, 120, 120), font=font(14))
    gy = GROUND * SQ
    # 设计图：站的那一列对十字，最低一行脚爪在地面线上面一行；头和弩再按这一帧挪
    ox = PIVOT[0] - PIVOT_COL + DX[k]
    oy = GROUND - 1 - SOLE_ROW + DY[k]
    big = Image.fromarray(g).resize((g.shape[1] * SQ, g.shape[0] * SQ), Image.NEAREST)
    im.alpha_composite(big, (ox * SQ, oy * SQ))
    d.line([(0, gy), (CELL[0], gy)], fill=(70, 70, 70), width=3)
    cx, cy = PIVOT[0] * SQ, PIVOT[1] * SQ
    d.line([(cx - 12, cy), (cx + 12, cy)], fill=(90, 90, 90), width=2)
    d.line([(cx, cy - 12), (cx, cy + 12)], fill=(90, 90, 90), width=2)
    return im


def sheet(cells):
    im = Image.new("RGBA", (CELL[0] * 2, CELL[1] * 2), (255, 255, 255, 255))
    for i, c in enumerate(cells):
        im.alpha_composite(c, ((i % 2) * CELL[0], (i // 2) * CELL[1]))
    return im


def on(im, z, bg=(255, 255, 255, 255)):
    b = Image.new("RGBA", im.size, bg)
    b.alpha_composite(im)
    return b.resize((im.width * z, im.height * z), Image.NEAREST)


def run_now():
    """游戏里现在的 hd_run 8 帧（league/champions/league_twitch：每帧以站位点为中心切的），并排、底对齐站位点。"""
    stem = os.path.join(ROOT, "league", "champions", "league_twitch")
    an = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"]["hd_run"]["frames"]
    px = Image.open(stem + "#sheet.png").convert("RGBA")
    tiles = []
    for f in an:
        x, y, w, h = (int(round(f["data"][q])) for q in "xywh")
        tiles.append(px.crop((x, y, x + w, y + h)))
    W = max(t.width for t in tiles)
    H = max(t.height for t in tiles)
    row = Image.new("RGBA", ((W + 4) * len(tiles), H), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        row.alpha_composite(t, (i * (W + 4) + (W - t.width) // 2, (H - t.height) // 2))
    return on(row, 3, (200, 205, 195, 255))


def league_frames(native):
    """英雄联盟 run 的 8 帧（native_pose.py 的 8 倍渲染，4 x 2 格），8 帧一起裁到人在的范围、标上号。"""
    im = Image.open(os.path.join(native, "twitch_pose_run.png")).convert("RGBA")
    a = np.array(im)
    cw, ch = im.width // 4, im.height // 2
    boxes = []
    for k in range(8):
        cx, cy = (k % 4) * cw, (k // 4) * ch
        ys, xs = np.nonzero(a[cy:cy + ch, cx:cx + cw, 3] > 0)
        boxes.append((xs.min(), xs.max(), ys.min(), ys.max()))
    x0, x1 = min(b[0] for b in boxes) - 24, max(b[1] for b in boxes) + 24
    y0, y1 = min(b[2] for b in boxes) - 24, max(b[3] for b in boxes) + 24
    tiles = []
    for k in range(8):
        cx, cy = (k % 4) * cw, (k // 4) * ch
        t = im.crop((cx + x0, cy + y0, cx + x1, cy + y1))
        b = Image.new("RGBA", t.size, (240, 240, 236, 255))
        b.alpha_composite(t)
        ImageDraw.Draw(b).text((10, 6), str(k + 1), fill=(0, 0, 0), font=font(28))
        tiles.append(b)
    w, h = tiles[0].size
    out = Image.new("RGBA", (w * 4 + 12, h * 2 + 4), (255, 255, 255, 255))
    for i, t in enumerate(tiles):
        out.alpha_composite(t, ((i % 4) * (w + 4), (i // 4) * (h + 4)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True, help="native_pose.py 渲的 run")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = np.array(Image.open(DESIGN).convert("RGBA"))
    g = ghost(d)
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "templates"))
    os.makedirs(os.path.join(out, "refs"))
    cells = [cell(g, k) for k in range(8)]
    sheet(cells[:4]).save(os.path.join(out, "templates", "run_1.png"))
    sheet(cells[4:]).save(os.path.join(out, "templates", "run_2.png"))
    on(Image.fromarray(d), SQ).save(os.path.join(out, "refs", "1_twitch_design_8x.png"))
    pic = Image.open(PICTURE).convert("RGBA")
    on(pic, 1).save(os.path.join(out, "refs", "2_twitch_picture_large.png"))
    league_frames(a.native).save(os.path.join(out, "refs", "3_league_run_8_frames.png"))
    run_now().save(os.path.join(out, "refs", "4_twitch_run_in_game_now_DONT_COPY.png"))
    prompt = os.path.join(SRC, "RUN_PROMPT.md")
    if os.path.isfile(prompt):
        shutil.copy(prompt, os.path.join(out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(os.path.join(os.path.dirname(os.path.abspath(out)), "twitch_run_pack"), "zip", out)
    print("pack:", out, "zip:", zp)


if __name__ == "__main__":
    main()
