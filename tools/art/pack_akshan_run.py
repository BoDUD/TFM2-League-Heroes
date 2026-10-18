"""Akshan run skin-swap pack (the user, 2026-10-18: 「走路没交叉步啊 你做不了就让codex做」; Swain's accepted way, memory
swain-session: a long coat's walk = Codex's skin swap over oppi's run): image 1 = oppi's Swain run from LoL Reborn (8
frames: the coat thrown back, both legs out in front in a scissor stride, the body bobbing - the nearest long-coat run;
oppi has no Akshan), scaled so his body matches our design's 57 rows hair to soles; image 2 = our approved design (the
skin), same cell size; image 3 = League's own Akshan run (the gun held up before his face, the cape flying, a forward
lean); a short Chinese prompt. -> ak/dist/akshan_packs/akshan_run_swap_pack.zip (oppi's frames and League's renders never
go into the repo).

    python tools/art/pack_akshan_run.py

My rig walk (only the boots stepping under the cape) had no crossing step: the design's legs stand 16+ squares apart
under the cape, so they cannot cross from its own squares (memory run-crossing-root-causes, cause 1).
"""
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
AK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(AK, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

OPPI = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/swain.aseprite"
DESIGN = os.path.join(AK, "assets", "source", "akshan", "hd", "design.png")
LOL_RUN = "C:/t/ak_work/look/Run.png"
TMP = "C:/t/ak_work/runswap"
OUT = os.path.join(TMP, "akshan_run_swap_pack")
ZIP = os.path.join(AK, "dist", "akshan_packs", "akshan_run_swap_pack.zip")
Z = 6
CW, CH = 84, 76                  # a cell in our squares (PPU 1.5)
FEET = 73                        # the soles' row inside a cell
BODY = 57                        # our design: hair top to soles
OPPI_BODY = 32                   # oppi's Swain idle: head top to soles (the raven's two rows above not counted)
KEY = (0, 255, 0)

PROMPT = """# 阿克尚 走路 换皮（骨架 + 皮囊）

上传顺序：图1 = `1_动作骨架_oppi走路.png`，图2 = `2_角色_阿克尚定稿.png`，图3 = `3_英雄联盟阿克尚跑步.png`（只看动作）。

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（影哨 阿克尚）。

1. 保留图1所有帧的位置、大小、排列顺序：4×2 共 8 帧，从左到右、从上到下；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作：披风往身后飘开，两条腿露在披风前面，**一前一后交叉迈步（剪刀步）**，往后收的腿弯膝、鞋跟抬起，两腿每半圈换一次前后；身体上下起伏、稍微前倾（图3 是英雄联盟原版的跑步，可以对照）。
3. 身体结构、配色、特征完全换成图2：深棕长卷发和小发髻、棕色的脸和短胡子、浅蓝白围巾、灰色金边护肩、赤膊、斜挎的橙红饰带和金箍、暗红长披风（背面浅蓝边）、青绿腰带和青绿长布片（金环，随步子摆动）、深灰黑裤子、黑色高筒靴（金色饰纹）。
4. 手：**拿枪的手（图2 左边）和图2一样把回旋镖手枪举在头边、枪口朝上**（图3 里他跑步时也把枪举在脸前），枪的大小、颜色、两道弯钩和图2 完全一样，跟着身体上下动，不要变形；另一只手不叉腰了，握拳随步子前后摆。**图1 肩上的乌鸦和红色恶魔手臂都不要画**。
5. 体型和图2一样大（头顶到鞋底约 57 格），头和身体比例和图2一样，不要变大变小、变胖变瘦；两条腿的颜色一样（裤子、靴子都和图2一样），远处那条腿可以暗一档。
6. 像素画：方块大小和图2一样（每个像素方块一样大，整齐对格），1–2 像素深色描边，不要抗锯齿、不要渐变、不要模糊。

背景保持纯绿色 #00FF00（和角色差异最大的纯色），方便抠图。风格保持与原图一致。重点在于精准复刻原图的"动作骨架"，只是换了"皮囊"。

交付：8 帧的整张图（和图1一样 4×2 排列、一样大小），放在 `outputs/akshan-run/`，原始生成图放 `raw/`，附 `generation-prompts.txt`，**最后**写 `HANDOFF.md`，再打包成 `outputs/akshan_run_done.zip`。
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
    k = BODY / OPPI_BODY
    soles = np.nonzero(idle[..., 3])[0].max()
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
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    up(on_key(sheet)).save(os.path.join(OUT, "1_动作骨架_oppi走路.png"))
    up(on_key(cell)).save(os.path.join(OUT, "2_角色_阿克尚定稿.png"))
    shutil.copyfile(LOL_RUN, os.path.join(OUT, "3_英雄联盟阿克尚跑步.png"))
    with open(os.path.join(OUT, "PROMPT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    os.makedirs(lp(os.path.dirname(ZIP)), exist_ok=True)
    with zipfile.ZipFile(lp(ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(OUT)):
            z.write(os.path.join(OUT, n), "akshan_run_swap_pack/" + n)
    shutil.copyfile(os.path.join(OUT, "PROMPT.md"), lp(os.path.join(os.path.dirname(ZIP), "RUN_PROMPT.md")))
    print(ZIP, "scale", round(k, 3), "sheet", sheet.shape[:2], "x", Z, "design", d.shape[:2])


if __name__ == "__main__":
    main()
