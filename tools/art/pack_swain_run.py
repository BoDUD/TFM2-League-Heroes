"""Swain run skin-swap pack (the user's skeleton + skin method, 2026-10-17: 「用 oppi 斯维因的走路当骨架、我们的造型当皮」):
image 1 = oppi's Swain run from LoL Reborn (8 frames: the coat thrown back, both legs out in front in a scissor stride,
the body bobbing), scaled to our design's height; image 2 = our approved design A (the skin), same cell size; a short
Chinese prompt. -> swa/dist/swain_packs/swain_run_swap_pack.zip (oppi's frames never go into the repo).

    python tools/art/pack_swain_run.py
"""
import os
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SWA = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(SWA, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

OPPI = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/swain.aseprite"
DESIGN = os.path.join(SWA, "assets", "source", "swain", "hd", "design_A.png")
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "swa_work", "runswap")
OUT = os.path.join(TMP, "swain_run_swap_pack")
ZIP = os.path.join(SWA, "dist", "swain_packs", "swain_run_swap_pack.zip")
Z = 6
CW, CH = 80, 72                  # a cell in our squares (PPU 1.5: 1.5 a game pixel)
FEET = 67                        # the soles' row inside a cell
KEY = (0, 255, 0)

PROMPT = """# 斯维因 走路 换皮（骨架 + 皮囊）

上传顺序：图1 = `1_动作骨架_oppi走路.png`，图2 = `2_角色_斯维因定稿.png`。

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（诺克萨斯统领斯维因）。

1. 保留图1所有帧的位置、大小、排列顺序：4×2 共 8 帧，从左到右、从上到下；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作：长大衣往身后飘开，两条腿露在大衣前面，一前一后交叉迈步（剪刀步），往后收的腿弯膝、鞋跟抬起；身体上下起伏。
3. 身体结构、配色、特征完全换成图2：银白长发、脸、近黑紫灰长大衣和浅紫衣边、暗红内衬、古铜胸甲和肩甲、深色裤子和靴子；两只手臂都是图2里普通的大衣袖子（**不要画红色的恶魔手臂**），随步子轻轻前后摆；**图1肩上的乌鸦不要画**。体型和图2一样大（大约 61 格高），头和身体比例和图2一样，不要变大变小、变胖变瘦。
4. 像素画：方块大小和图2一样（每个像素方块一样大，整齐对格），1 像素深色描边，不要抗锯齿、不要渐变、不要模糊。

背景保持纯绿色 #00FF00（和角色差异最大的纯色），方便抠图。风格保持与原图一致。重点在于精准复刻原图的"动作骨架"，只是换了"皮囊"。

交付：8 帧的整张图（和图1一样 4×2 排列、一样大小），打包成 `swain_run_swap_done.zip`，附 `HANDOFF.md`。
"""


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def on_key(a):
    out = np.zeros(a.shape[:2] + (3,), np.uint8)
    out[:] = KEY
    m = a[..., 3] > 0
    out[m] = a[m][:, :3]
    return out


def main():
    s = T.load_sprite(OPPI)
    t = s.tag("run")
    run = [np.asarray(s.frames[i].convert("RGBA")) for i in range(t["frm"], t["to"] + 1)]
    idle = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    des = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(des[..., 3])
    d = des[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # oppi's idle body height (soles to the hair, without the raven: its rows above the head are counted too, so the
    # scale reads oppi's head-to-soles from the column of his face) -> our design's height
    iy, ix = np.nonzero(idle[..., 3])
    k = d.shape[0] / (iy.max() - iy.min() + 1)
    soles = iy.max()
    allm = np.zeros(run[0].shape[:2], bool)
    for f in run:
        allm |= f[..., 3] > 0
    yy, xx = np.nonzero(allm)
    x0, x1, y0 = xx.min(), xx.max() + 1, yy.min()
    sheet = np.zeros((2 * CH, 4 * CW, 4), np.uint8)
    for n, f in enumerate(run):
        crop = f[y0:soles + 1, x0:x1]
        im = Image.fromarray(crop).resize((round(crop.shape[1] * k), round(crop.shape[0] * k)), Image.NEAREST)
        a = np.asarray(im)
        h, w = a.shape[:2]
        Y, X = (n // 4) * CH + FEET - h + 1, (n % 4) * CW + (CW - w) // 2
        Y0 = max(Y, (n // 4) * CH)
        a = a[Y0 - Y:]
        m = a[..., 3] > 0
        sheet[Y0:Y0 + a.shape[0], X:X + w][m] = a[m]
    cell = np.zeros((CH, CW, 4), np.uint8)
    dy, dx = FEET - d.shape[0] + 1, (CW - d.shape[1]) // 2
    m = d[..., 3] > 0
    cell[dy:dy + d.shape[0], dx:dx + d.shape[1]][m] = d[m]
    os.makedirs(lp(OUT), exist_ok=True)
    up(on_key(sheet)).save(lp(os.path.join(OUT, "1_动作骨架_oppi走路.png")))
    up(on_key(cell)).save(lp(os.path.join(OUT, "2_角色_斯维因定稿.png")))
    with open(lp(os.path.join(OUT, "PROMPT.md")), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    os.makedirs(lp(os.path.dirname(ZIP)), exist_ok=True)
    with zipfile.ZipFile(lp(ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(lp(OUT))):
            z.write(lp(os.path.join(OUT, n)), "swain_run_swap_pack/" + n)
    print(ZIP, "scale", round(k, 3), "sheet", sheet.shape[:2], "x", Z, "design", d.shape[:2])


if __name__ == "__main__":
    main()
