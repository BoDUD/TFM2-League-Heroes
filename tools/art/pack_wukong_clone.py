"""Wukong's W clone pictures in his new design (the user, 2026-10-18: 「猴子gif图里面怎么一直变色？」 - besides the
per-frame palettes, the decoy still showed the OLD design: w_clone, w_clone_atk and w_clone_spin are effect pictures from
the first FX pack). Effect pictures are never mirrored on the red side, so the clone is drawn FRONT-ON and left-right
symmetric (memory red-side-caster-pictures) - the new side-view action frames cannot stand in. A skin swap: image 1 the
old clone sheets scaled to 85 % (his new size) at 8 px a square, image 2 the new design, image 3 his new spin frames.

    python tools/art/pack_wukong_clone.py      # -> dist/redo_packs/wukong_clone_pack.zip
"""
import os
import shutil
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
AK = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(AK, "assets", "source", "wukong")
DIST = os.path.join(AK, "dist", "redo_packs")
TMP = "C:/t/wkc_work/clone_pack"
Z = 8
K = 0.85
NAMES = {"w_clone": "1_骨架_分身站立", "w_clone_atk": "2_骨架_分身挥棍", "w_clone_spin": "3_骨架_分身转圈"}
CELLS = {"w_clone": (44, 48), "w_clone_atk": (48, 60), "w_clone_spin": (84, 48)}

PROMPT = """# 孙悟空 W 真假猴王的分身：换成新造型（正面、左右对称）

用户：「猴子gif图里面怎么一直变色？」。除了颜色，**W 放出的分身还是旧造型**（旧的分身图是第一次特效包画的）。分身是放在地上的特效图，**游戏在红色方不会把它翻转**，所以分身一直画成**正面、左右完全对称**的样子。这次把三组分身图换成新造型。

每组单独生成一张（共 3 张）。上传：图1 = 这一组的骨架（旧造型的分身，已经缩到新大小，每个像素方块 8 px），图2 = `4_新造型定稿.png`（新造型，侧身），图3 = `5_新造型转圈.png`（新造型转圈的帧，里面有正面、背面，**看正面长什么样**）。

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2、图3 的新造型（齐天大圣 孙悟空）。

1. 保留图1所有帧的位置、大小、排列顺序（4 帧，从左到右）；每帧角色在格子里的位置和脚底高度都不变；大小和图1一样（不要变大）。
2. 保留每帧的动作：站立轻轻起伏 / 举棍挥下 / 横握金箍棒转圈（转圈那组的**金色旋风圈照图1 保留**）。
3. **正面朝我们，左右完全对称**（左边和右边是镜像：两只眼睛、两只护臂、两只脚一样），金箍棒横着时两头一样长。
4. 新造型的样子（照图2、图3）：棕色猴毛、头顶往上翘的深棕头发（**不是**图1 头顶那根棕色长柱子）、浅粉的脸心、**两只绿眼睛**、圆耳朵、大红围巾、金红大护臂、金色胸甲和鳞纹前摆、暗栗色袍裙、暗钢色护膝、紫色鞋子；尾巴从身后一侧露出来也可以，但要对称就藏在身后。金箍棒：橙红棒头、金箍、红色两端、灰色钢段，笔直。
5. 像素画：方块大小和图1一样（每格 8 px，整齐对格），1–2 格深色描边，不要抗锯齿、不要渐变、不要模糊。背景纯绿色 #00FF00。

交付：3 张整图 `wukong-w_clone.png`、`wukong-w_clone_atk.png`、`wukong-w_clone_spin.png`（和各自的图1 一样大），放在 `outputs/wukong-clone/`，原始生成图放 `raw/`，附 `generation-prompts.txt`，**最后**写 `HANDOFF.md`，再打包成 `outputs/wukong_clone_done.zip`。

## Claude 收到后（给 Claude 看）

8 px 一格读回成 1 倍，左右按中线镜像成严格对称，颜色归到动作帧的调色板（palette_act_1018.py 那套），替换 import_wukong_fx.py 的三组分身。
"""


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def on_green(a):
    o = np.zeros(a.shape[:2] + (3,), np.uint8)
    o[:] = (0, 255, 0)
    m = a[..., 3] > 0
    o[m] = a[m][:, :3]
    return o


def main():
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    for name, label in NAMES.items():
        a = Image.open(lp(os.path.join(SRC, "codex_fx", "pixel_1x", f"wukong_fx_{name}.png"))).convert("RGBA")
        cw, ch = CELLS[name]
        cells = []
        for k in range(4):
            c = a.crop((k * cw, 0, (k + 1) * cw, ch))
            nw, nh = round(cw * K), round(ch * K)
            small = c.resize((nw, nh), Image.NEAREST)
            can = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            can.alpha_composite(small, ((cw - nw) // 2, ch - nh))      # feet stay on the cell's bottom
            cells.append(np.asarray(can))
        sheet = np.concatenate(cells, 1)
        Image.fromarray(np.repeat(np.repeat(on_green(sheet), Z, 0), Z, 1)).save(os.path.join(TMP, label + ".png"))
    des = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "redo2.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(on_green(des), 6, 0), 6, 1)).save(os.path.join(TMP, "4_新造型定稿.png"))
    spins = [np.asarray(Image.open(lp(os.path.join(SRC, "hd", "act", f"spin_{i}.png"))).convert("RGBA")) for i in range(8)]
    H = max(s.shape[0] for s in spins)
    row = np.zeros((H, sum(s.shape[1] + 4 for s in spins), 4), np.uint8)
    x = 0
    for s in spins:
        row[H - s.shape[0]:, x:x + s.shape[1]] = s
        x += s.shape[1] + 4
    Image.fromarray(np.repeat(np.repeat(on_green(row), 4, 0), 4, 1)).save(os.path.join(TMP, "5_新造型转圈.png"))
    with open(os.path.join(TMP, "PROMPT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    os.makedirs(lp(DIST), exist_ok=True)
    zp = os.path.join(DIST, "wukong_clone_pack.zip")
    with zipfile.ZipFile(lp(zp), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(TMP)):
            z.write(os.path.join(TMP, n), "wukong_clone_pack/" + n)
    shutil.copyfile(os.path.join(TMP, "PROMPT.md"), lp(os.path.join(DIST, "WUKONG_CLONE_PROMPT.md")))
    print(zp)


if __name__ == "__main__":
    main()
