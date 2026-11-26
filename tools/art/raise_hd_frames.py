#!/usr/bin/env python3
"""高清英雄的战场帧画高一点：hd.rs 的 SIZES 把他放大，而他的帧不是 ppu_restyle.py 出的（lower_hd_frames.py 的反过来）。

    python tools/art/raise_hd_frames.py league/champions/league_tryndamere --rows 5 [--check]

游戏按帧的中心画，SIZES 大于 1 的英雄从中心往外放大，脚底就陷到地面下面。这里给每个高清帧的框在底下加 rows 行空行：
中心往下 rows / 2 格，画面相对中心就高 rows / 2 格，像素一个不改。行数：脚底在中心下 c 格、放大到 s，
2 × c × (1 - 1 / s)，取整。

和 lower_hd_frames.py 不一样，选人卡片的 hd_bp / hd_idle_base 也一起加：hero_reels.py 的待机和卡片都是从同一批帧里剪的，
卡片不跟着加的话，下次跑 hero_reels 会把没加过的 idle_base 帧放回战场的待机里（站着时一跳一跳）。代价是卡片里人高
rows / 2 格（没有 banpick_center 的英雄不裁边）。

框底下的 rows 行在图里本来就全透明时只改 .fanim；不透明（挨着别的帧）的那几帧连同加的空行一起抄到图的最下面，
框指过去（同一个框的帧只抄一份）。只跑一次：再跑一次又会往上挪。
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image

def main():
    # 日文 Windows 的控制台是 cp932，打不出简体字
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", help="图的路径，不带 #anim.fanim / #sheet.png")
    ap.add_argument("--rows", type=int, required=True, help="框底下加几行空行（画面高 rows / 2 格）")
    ap.add_argument("--check", action="store_true", help="只说会怎么改")
    a = ap.parse_args()
    if a.rows <= 0:
        sys.exit("--rows 要大于 0（往下画用 lower_hd_frames.py）")
    anim_path, sheet_path = f"{a.base}#anim.fanim", f"{a.base}#sheet.png"
    with open(anim_path, encoding="utf-8-sig") as f:
        doc = json.load(f)
    sheet = np.asarray(Image.open(sheet_path).convert("RGBA"))
    H, W = sheet.shape[:2]
    moved = {}    # 原来的框 -> 抄到底下以后的新框（同一个框只抄一份）
    later = []    # 要抄到底下的（原来的框, 加了空行的图）
    n = in_place = 0
    for tag, anim in doc["anims"].items():
        if not tag.startswith("hd_"):
            continue
        for fr in anim["frames"]:
            r = fr["data"]
            x, y, w, h = (int(r[k]) for k in ("x", "y", "w", "h"))
            n += 1
            below = sheet[y + h:y + h + a.rows, x:x + w]
            if y + h + a.rows <= H and not (below[..., 3] > 0).any():
                r["h"] = float(h + a.rows)
                in_place += 1
                continue
            key = (x, y, w, h)
            if key not in moved:
                pic = np.zeros((h + a.rows, w, 4), np.uint8)
                pic[:h] = sheet[y:y + h, x:x + w]
                moved[key] = None
                later.append((key, pic))
            fr["data"] = key    # 先记着原来的框，排好位置后再换
    # 抄到底下：一排排往右摆，帧之间空 1 像素（sheetkit.Kit.save 的摆法）
    if later:
        top = H + 1
        cx, cy, rh = 0, top, 0
        place = []
        for key, pic in later:
            if cx + pic.shape[1] > W:
                cx, cy, rh = 0, cy + rh + 1, 0
            place.append((key, pic, cx, cy))
            moved[key] = {"x": float(cx), "y": float(cy), "w": float(pic.shape[1]), "h": float(pic.shape[0])}
            cx += pic.shape[1] + 1
            rh = max(rh, pic.shape[0])
        big = np.zeros((cy + rh, W, 4), np.uint8)
        big[:H] = sheet
        for key, pic, px, py in place:
            big[py:py + pic.shape[0], px:px + pic.shape[1]] = pic
        sheet = big
        for tag, anim in doc["anims"].items():
            for fr in anim["frames"]:
                if isinstance(fr["data"], tuple):
                    fr["data"] = dict(moved[fr["data"]])
    print(f"{anim_path}: {n} 个高清帧的框底下加 {a.rows} 行（画面高 {a.rows / 2} 格）："
          f"{in_place} 个原地加长，{n - in_place} 个抄到图底下（{len(later)} 份）" + ("（--check：没写）" if a.check else ""))
    if not a.check:
        with open(anim_path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
        if later:
            Image.fromarray(sheet).save(sheet_path)


if __name__ == "__main__":
    main()
