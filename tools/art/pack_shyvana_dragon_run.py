#!/usr/bin/env python3
"""龙女龙形态跑步（d_run）给 Codex 重画的素材包（用户 2026-11-22：「龙女变形的龙的跑步姿势也可以让codex重画一下 现在也很僵硬」）。

游戏里的 d_run 是 rig_shyvana.py 拿设计图的方块挪出来的：身子原样不动，四只爪各自挪 3 格，翅膀转几度，看上去像在原地蹭。
英雄联盟的 run1 是一蹦一蹦的：前后腿轮流着地，身子前后起伏，尾巴上下卷，远侧翅膀前后扫。

我们的设计图（hd/d_idle.png，PPU 1.5，107 x 64）是 Codex 照联盟画的，比例和联盟的模型差得不少（尾巴更长、身子更低、
近侧翅膀矮一截），联盟的剪影直接当影子会把翅膀拉高。所以模板里的影子只放设计图的头、下巴、身子和两只翅膀，按联盟每帧
胸口和骨盆的起伏上下挪（BOB）、前后挪一点（SURGE）；四条腿和尾巴不放，让 Codex 照联盟同一帧（附图 3）画。

    python tools/lol/native_pose.py <work>/poses_dragon_tall.json --out <work>/native_tall --alpha --tag d_run
    python tools/art/pack_shyvana_dragon_run.py --native <work>/native_tall --out <pack>

<work>/poses_dragon_tall.json = assets/source/shyvana/poses_dragon.json 只留 d_run，格子加高到 [200, 150, 14]
（原来 112 高，近侧翅膀顶被切掉）。写出 <pack>/：templates/run_1.png、run_2.png（各 2048 x 1920，2 x 2 格，每格
1024 x 960，一格设计图 = 8 像素），refs/ 四张图，以及 <pack>.zip（提示词 DRAGON_RUN_PROMPT.md 一起放进去）。
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_shyvana as RS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shyvana")
SQ = 8                                   # 模板里一格设计图多少像素
CELL = (1024, 960)
PIVOT = (CELL[0] // 2, CELL[1] // 2)     # 十字：站位点，也是游戏里这一帧的中心
GROUND = 17                              # 地面线在站位点下面多少格（设计图最低一行脚爪在它上面一行）
# 联盟 run1 每帧（run1@0 起每 117 毫秒一帧）胸口和骨盆平均高度减去 8 帧的平均，乘 0.64（联盟一游戏像素 = 设计图 0.64 格，
# 对齐 idle2@0 和设计图翅膀以下的轮廓量的），往下为正；前后只留一半（胸口前后晃 ±3 格，精灵图跟着晃会像在地上滑）
BOB = [0, 2, 0, -1, 0, 2, -1, -1]
SURGE = [1, 0, -1, -1, 0, 0, 1, 1]
GHOST_PARTS = ("head", "jaw", "body", "near_wing", "far_wing")      # 不放四条腿和尾巴
BELLY = 52                               # 设计图这一行往下是腿和爪（头、下巴除外）


def font(n):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", n)
    except OSError:
        return ImageFont.load_default()


def ghost(f):
    """设计图里头、下巴、身子、两只翅膀那些方块，冲淡成浅灰（留一点明暗，看得出翅膀骨和鬃毛）。身子那块还带着腿根
    和远侧前爪的爪尖（腿的框没框到）：肚子以下（BELLY 行起）只留头和下巴，再只留最大的那一块连着的。"""
    m = np.zeros((f.H, f.W), bool)
    for n in GHOST_PARTS:
        m |= f.masks[n]
    yy = np.mgrid[0:f.H, 0:f.W][0]
    m &= (yy < BELLY) | f.masks["head"] | f.masks["jaw"]
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    lum = f.d[..., :3].astype(float) @ np.array([0.3, 0.55, 0.15])
    g = (200 + lum / 255.0 * 45).astype(np.uint8)
    out = np.zeros((f.H, f.W, 4), np.uint8)
    out[m, 0] = out[m, 1] = out[m, 2] = g[m]
    out[m, 3] = 255
    return out


def cell(f, g, k):
    im = Image.new("RGBA", CELL, (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CELL[0] - 1, CELL[1] - 1], outline=(170, 170, 170))
    d.text((10, 8), str(k + 1), fill=(120, 120, 120), font=font(14))
    gy = PIVOT[1] + GROUND * SQ
    # 设计图：站的那一列（D_STAND）对十字，最低一行脚爪在地面线上面一行
    ox = PIVOT[0] // SQ - RS.D_STAND + SURGE[k]
    oy = gy // SQ - f.H + BOB[k]
    big = Image.fromarray(g).resize((f.W * SQ, f.H * SQ), Image.NEAREST)
    im.alpha_composite(big, (ox * SQ, oy * SQ))
    d.line([(0, gy), (CELL[0], gy)], fill=(70, 70, 70), width=3)
    cx, cy = PIVOT
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


def run_now(f):
    """游戏里现在的 d_run 8 帧（assets/source/ppu/orig/shyvana_d_run.png：每帧之间空一列，帧顶对齐）。"""
    import json
    a = Image.open(os.path.join(ROOT, "assets", "source", "ppu", "orig", "shyvana_d_run.png")).convert("RGBA")
    sizes = json.load(open(os.path.join(ROOT, "assets", "source", "ppu", "orig", "shyvana_d_run.json")))["sizes"]
    x, tiles = 0, []
    for w, h in sizes:
        tiles.append(a.crop((x, 0, x + w, 70)))
        x += w + 1
    row = Image.new("RGBA", (sum(t.width + 4 for t in tiles), 70), (0, 0, 0, 0))
    x = 0
    for t in tiles:
        row.alpha_composite(t, (x, 0))
        x += t.width + 4
    return on(row, 3)


def league_frames(native):
    """联盟 run1 的 8 帧（native_pose.py 的 8 倍渲染，4 x 2 格，每格 1600 x 1200），每帧裁掉四周空白、缩到 40%、标上号。"""
    im = Image.open(os.path.join(native, "shyvana_dragon_pose_d_run.png")).convert("RGBA")
    cw, ch = im.width // 4, im.height // 2
    tiles = []
    for k in range(8):
        cx, cy = (k % 4) * cw, (k // 4) * ch
        t = im.crop((cx + 150, cy + 80, cx + cw - 150, cy + ch - 40))
        b = Image.new("RGBA", t.size, (240, 240, 236, 255))
        b.alpha_composite(t)
        b = b.resize((b.width * 2 // 5, b.height * 2 // 5), Image.LANCZOS)
        ImageDraw.Draw(b).text((10, 6), str(k + 1), fill=(0, 0, 0), font=font(28))
        tiles.append(b)
    w, h = tiles[0].size
    out = Image.new("RGBA", (w * 4 + 12, h * 2 + 4), (255, 255, 255, 255))
    for i, t in enumerate(tiles):
        out.alpha_composite(t, ((i % 4) * (w + 4), (i // 4) * (h + 4)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True, help="native_pose.py 渲的 d_run（加高格子的那份）")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f = RS.dragon_form()
    g = ghost(f)
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "templates"))
    os.makedirs(os.path.join(out, "refs"))
    cells = [cell(f, g, k) for k in range(8)]
    sheet(cells[:4]).save(os.path.join(out, "templates", "run_1.png"))
    sheet(cells[4:]).save(os.path.join(out, "templates", "run_2.png"))
    on(Image.fromarray(f.d), SQ).save(os.path.join(out, "refs", "1_dragon_design_8x.png"))
    shutil.copy(os.path.join(SRC, "codex_model", "shyvana-model-D-1.png"),
                os.path.join(out, "refs", "2_dragon_design_full_size.png"))
    league_frames(a.native).save(os.path.join(out, "refs", "3_league_run1_8_frames.png"))
    run_now(f).save(os.path.join(out, "refs", "4_dragon_run_in_game_now_DONT_COPY.png"))
    prompt = os.path.join(SRC, "DRAGON_RUN_PROMPT.md")
    if os.path.isfile(prompt):
        shutil.copy(prompt, os.path.join(out, "DRAGON_RUN_PROMPT.md"))
    zp = shutil.make_archive(os.path.join(os.path.dirname(os.path.abspath(out)), "shyvana_dragon_run_pack"), "zip", out)
    print("pack:", out, "zip:", zp)


if __name__ == "__main__":
    main()
