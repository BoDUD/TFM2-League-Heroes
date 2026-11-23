#!/usr/bin/env python3
"""Codex 交来的选人立绘原图 -> 游戏用的立绘卡（league/、tft/ 或 ragnarok/ 下的 banpick_illustrations/<英雄id>.png）。

    python -I tools/art/bp_illustrations.py <交付的 zip 或文件夹> [--write] [--sheet 检查图.png]

- 交付里每张 `league_xxx.png` / `tft_xxx.png` / `ragnarok_xxx.png`（raw/ 里的不算）就是一个英雄的原图，生图工具给的竖版尺寸，不缩不裁。
- 按卡片的比例 304:357 裁：宽度全留，多出来的高度上面裁 25%、下面裁 75%（头留着，裁掉的是腿和下面的背景）。
  不拉伸：2026-11-20 试点时 Codex 自己把 1062×1481 硬拉成 1216×1428，人横着宽了约 19%。
- LANCZOS 缩到 304×357，贴到 304×405 透明画布的 y=48（照公主连结的立绘，上面 48 行全透明；
  tools/ci/bp_illustrations.py 会查）。
- 不加 --write 只列出会写哪些文件；--sheet 把转好的卡排成一张图，方便逐张看造型和裁切。
"""
import argparse
import io
import os
import sys
import zipfile

from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = "banpick_illustrations"
CARD = (304, 357)
CANVAS = (304, 405)
TOP = 48
TOP_SHARE = 0.25


def originals(src):
    """交付里的原图：[(英雄id, 图)]。"""
    found = []

    def want(name):
        parts = name.replace("\\", "/").split("/")
        f = parts[-1]
        return "raw" not in parts[:-1] and f.endswith(".png") and f.startswith(("league_", "tft_", "ragnarok_", "baixi_"))

    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in sorted(z.namelist()):
                if want(n):
                    found.append((os.path.basename(n)[:-4], Image.open(io.BytesIO(z.read(n)))))
    else:
        for dp, dn, fn in os.walk(src):
            dn[:] = sorted(d for d in dn if d != "raw")
            for f in sorted(fn):
                if want(f):
                    found.append((f[:-4], Image.open(os.path.join(dp, f))))
    return found


def card(im):
    """原图 -> 304×405 的立绘卡。"""
    im = im.convert("RGB")
    w, h = im.size
    ch = round(w * CARD[1] / CARD[0])
    if ch <= h:
        top = round((h - ch) * TOP_SHARE)
        im = im.crop((0, top, w, top + ch))
    else:  # 比卡片还宽：两边各裁一半
        cw = round(h * CARD[0] / CARD[1])
        x0 = (w - cw) // 2
        im = im.crop((x0, 0, x0 + cw, h))
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    out.paste(im.resize(CARD, Image.LANCZOS).convert("RGBA"), (0, TOP))
    return out


def pack_of(cid):
    return cid.split("_", 1)[0] if cid.startswith(("tft_", "ragnarok_", "baixi_")) else "league"


def sheet(cards, path):
    """转好的卡排成一张检查图（每行 8 张，下面写英雄id）。"""
    cols = 8
    rows = (len(cards) + cols - 1) // cols
    cw, chh = CARD[0] // 2, CARD[1] // 2
    o = Image.new("RGB", (cols * (cw + 8) + 8, rows * (chh + 26) + 8), (24, 26, 32))
    d = ImageDraw.Draw(o)
    for k, (cid, c) in enumerate(cards):
        x, y = 8 + (k % cols) * (cw + 8), 8 + (k // cols) * (chh + 26)
        o.paste(c.crop((0, TOP, CANVAS[0], CANVAS[1])).convert("RGB").resize((cw, chh), Image.LANCZOS), (x, y))
        d.text((x, y + chh + 4), cid, fill=(230, 230, 230))
    o.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="Codex 交付的 zip 或解压后的文件夹")
    ap.add_argument("--write", action="store_true", help="写进各包（league/、tft/、ragnarok/）的 banpick_illustrations/")
    ap.add_argument("--sheet", help="转好的卡排成一张检查图，写到这里")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # 控制台不是 UTF-8 时中文也能打印
    done, bad = [], []
    for cid, im in originals(a.src):
        if not os.path.isfile(os.path.join(REPO, pack_of(cid), "champion", cid + ".data_champion")):
            bad.append(f"{cid}：包里没有这个英雄")
            continue
        c = card(im)
        dst = os.path.join(REPO, pack_of(cid), DIR, cid + ".png")
        print(f"{cid}: {im.size[0]}×{im.size[1]} -> {pack_of(cid)}/{DIR}/{cid}.png"
              + ("（覆盖）" if os.path.exists(dst) else ""))
        if a.write:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            c.save(dst, optimize=True)
        done.append((cid, c))
    if a.sheet and done:
        sheet(done, a.sheet)
    for b in bad:
        print("跳过：" + b)
    print(f"{len(done)} 张" + ("已写入" if a.write else "（没加 --write，没写）"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
