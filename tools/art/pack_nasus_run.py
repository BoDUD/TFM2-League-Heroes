"""Nasus run skin-swap pack (the skeleton + skin method that fixed league_swain's walk, 2026-10-17: 「用 oppi 的走路当骨架、我们的
造型当皮」): oppi has no Nasus, so the skeleton is oppi's Sion run from LoL Reborn (9 frames: a big upright brute, the
legs crossing in a clear stride, the body bobbing, the axe held low across the hips like Nasus's staff) - Nasus's own
stance is too wide to cross the legs by moving the design's squares (feet 17 columns apart, memory
run-crossing-root-causes). Two sheets: A (his normal body, 53 rows) and B (Fury of the Sands, 71 rows), each 3 x 3 cells
of the skeleton scaled to that body's height, plus the design in one cell at the same scale; a short Chinese prompt.
-> ns/dist/nasus_packs/nasus_run_swap_pack.zip (oppi's frames never go into the repo).

    python tools/art/pack_nasus_run.py
"""
import os
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

OPPI = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/cf_sion.aseprite"
SRC = os.path.join(REPO, "assets", "source", "nasus", "hd")
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "nas_work", "runswap")
OUT = os.path.join(TMP, "nasus_run_swap_pack")
ZIP = os.path.join(REPO, "dist", "nasus_packs", "nasus_run_swap_pack.zip")
Z = 4
KEY = (0, 255, 0)
# form -> (design, cell width, cell height, the soles' row inside a cell)
FORMS = {"A": ("design_A.png", 96, 62, 59), "B": ("design_B.png", 116, 82, 79)}

PROMPT = """# 内瑟斯 走路 换皮（骨架 + 皮囊）

一共两组，每组两张图，分开画：
- A 组：图1 = `A1_动作骨架_走路.png`，图2 = `A2_角色_内瑟斯定稿.png` → 交 `nasus_run_A.png`
- B 组：图1 = `B1_动作骨架_走路.png`，图2 = `B2_角色_内瑟斯大招形态.png` → 交 `nasus_run_B.png`

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（豺狼头战士内瑟斯）。

1. 保留图1所有帧的位置、大小、排列顺序：3×3 共 9 帧，从左到右、从上到下；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作：两条腿一前一后交叉迈步，往后收的腿弯膝、脚跟抬起；身体上下起伏；手臂跟着步子摆动。
3. 身体结构、配色、特征完全换成图2：金色豺狼头冠、两只竖起的长耳朵（近侧耳朵里面暗红）、长嘴和白色尖牙、发光的眼睛、黑褐色的毛、金色大肩甲和金色护臂、金色长靴、青绿色宝石、深蓝腰带、青绿长腰布、灰白条纹布条。
4. 法杖：两只手握着图2的长法杖，放在身体前面偏下，像图1拿斧头的位置，杖身斜着横在腰前；**月牙斧刃在前面（画面右边）**，比脚高，不要碰到地面，也不要挡住腿；杖尾斜向身后。法杖的长度、粗细、斧刃的形状和图2一样，**不要变短、不要变形**，每一帧都完整。
5. 体型和图2一样大（A 组约 53 格高，B 组约 71 格高），头和身体比例和图2一样，不要变大变小、变胖变瘦。B 组的眼睛和所有青绿宝石是亮青白色（和图2一样）。
6. 像素画：方块大小和图2一样（每个像素方块一样大，整齐对格），1 像素深色描边，不要抗锯齿、不要渐变、不要模糊。

背景保持纯绿色 #00FF00（和角色差异最大的纯色），方便抠图。风格保持与原图一致。重点在于精准复刻原图的"动作骨架"，只是换了"皮囊"。

交付：`nasus_run_A.png`、`nasus_run_B.png`（每张都是 9 帧的整张图，和各自的图1一样 3×3 排列、一样大小），放在 `outputs/nasus-run/`，附 `HANDOFF.md`，打包成 `outputs/nasus_run_swap_done.zip`。
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
    iy, ix = np.nonzero(idle[..., 3])
    soles = iy.max()
    allm = np.zeros(run[0].shape[:2], bool)
    for f in run:
        allm |= f[..., 3] > 0
    yy, xx = np.nonzero(allm)
    x0, x1, y0 = xx.min(), xx.max() + 1, yy.min()
    os.makedirs(lp(OUT), exist_ok=True)
    for form, (design, CW, CH, FEET) in FORMS.items():
        des = np.asarray(Image.open(lp(os.path.join(SRC, design))).convert("RGBA"))
        ys, xs = np.nonzero(des[..., 3])
        d = des[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        k = d.shape[0] / (iy.max() - iy.min() + 1)          # oppi's idle head-to-soles -> our design's
        sheet = np.zeros((3 * CH, 3 * CW, 4), np.uint8)
        for n, f in enumerate(run):
            crop = f[y0:soles + 1, x0:x1]
            im = Image.fromarray(crop).resize((round(crop.shape[1] * k), round(crop.shape[0] * k)), Image.NEAREST)
            a = np.asarray(im)
            h, w = a.shape[:2]
            Y, X = (n // 3) * CH + FEET - h + 1, (n % 3) * CW + (CW - w) // 2
            Y0 = max(Y, (n // 3) * CH)
            a = a[Y0 - Y:]
            m = a[..., 3] > 0
            sheet[Y0:Y0 + a.shape[0], X:X + w][m] = a[m]
        cell = np.zeros((CH, CW, 4), np.uint8)
        dy, dx = FEET - d.shape[0] + 1, (CW - d.shape[1]) // 2
        m = d[..., 3] > 0
        cell[dy:dy + d.shape[0], dx:dx + d.shape[1]][m] = d[m]
        name2 = "A2_角色_内瑟斯定稿.png" if form == "A" else "B2_角色_内瑟斯大招形态.png"
        up(on_key(sheet)).save(lp(os.path.join(OUT, f"{form}1_动作骨架_走路.png")))
        up(on_key(cell)).save(lp(os.path.join(OUT, name2)))
        print(form, "scale", round(k, 3), "sheet", sheet.shape[:2], "x", Z, "design", d.shape[:2])
    with open(lp(os.path.join(OUT, "PROMPT.md")), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    os.makedirs(lp(os.path.dirname(ZIP)), exist_ok=True)
    with zipfile.ZipFile(lp(ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(lp(OUT))):
            z.write(lp(os.path.join(OUT, n)), "nasus_run_swap_pack/" + n)
    print(ZIP)


if __name__ == "__main__":
    main()
