#!/usr/bin/env python3
"""CI：选人立绘（league/ 和 tft/ 下的 banpick_illustrations/）。

游戏 0.7.3 自己读每个 mod 的 `banpick_illustrations/<英雄id>.png`，在选人和英雄交换界面显示（原版的在
asset/base/ui/banpick/illustrations）。照公主连结的立绘：304×405 RGBA，最上面 48 行全透明，下面 304×357 满版不透明
（交换界面显示的就是这一块）。

    python -I tools/ci/bp_illustrations.py

查的是：文件名就是这个包里的英雄id（名字对不上游戏就不显示）、尺寸、上面 48 行全透明、下面全不透明。
有问题退出 1。没有立绘的英雄只报个数，不算错（还在一批批补）。
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import package_mod as pm  # noqa: E402

DIR = "banpick_illustrations"
SIZE = (304, 405)
TOP = 48


def check(path):
    """一张立绘的问题（没问题返回空列表）。"""
    try:
        im = Image.open(path)
        im.load()
    except Exception as e:  # 读不了的图
        return [f"读不出来：{e}"]
    out = []
    if im.format != "PNG":
        out.append(f"不是 PNG（{im.format}）")
    if im.size != SIZE:
        out.append(f"尺寸 {im.size[0]}×{im.size[1]}，应为 {SIZE[0]}×{SIZE[1]}")
        return out
    if im.mode != "RGBA":
        out.append(f"模式 {im.mode}，应为 RGBA")
        return out
    a = im.getchannel("A")
    top = a.crop((0, 0, SIZE[0], TOP)).getextrema()
    body = a.crop((0, TOP, SIZE[0], SIZE[1])).getextrema()
    if top != (0, 0):
        out.append(f"上面 {TOP} 行不是全透明（alpha {top}）")
    if body != (255, 255):
        out.append(f"下面 {SIZE[0]}×{SIZE[1] - TOP} 不是全不透明（alpha {body}）")
    return out


def main():
    # CI 的 Windows 机器上 python -I 按系统编码输出，中文会报错
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    bad, have, total = [], 0, 0
    for pack in ("league", "tft", "ragnarok", "baixi"):
        src = os.path.join(pm.REPO, pack)
        heroes = set(pm.hero_ids(src))
        total += len(heroes)
        folder = os.path.join(src, DIR)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            rel = f"{pack}/{DIR}/{f}"
            stem, ext = os.path.splitext(f)
            if ext.lower() != ".png":
                bad.append(f"{rel}：不是 .png 文件")
                continue
            if stem not in heroes:
                bad.append(f"{rel}：{pack} 里没有英雄 {stem}（文件名必须就是英雄id）")
                continue
            have += 1
            bad += [f"{rel}：{p}" for p in check(os.path.join(folder, f))]
    print(f"选人立绘：{have} / {total} 个英雄有")
    for b in bad:
        print("错误：" + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
