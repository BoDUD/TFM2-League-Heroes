"""Two follow-up Codex packs after the skin-swap actions (the user, 2026-10-18: 「阿克尚枪会换手、猴子的 R 转圈还没做…这个要做啊」):

- akshan_gunhand: Akshan's idle and Q again (oppi Lucian's idle / skill1 skeletons from pack_swap_1018) with the gun in
  the SAME hand as his walk, attack, E and R (the front hand, the one that shoots); read back, the idle and Q's wind-up /
  return had it raised in the back hand, so every idle -> walk / attack switch flipped the gun to the other side.
- wukong_spin: Wukong's R Cyclone, 8 frames of a full turn over League's own clip (monkeyking_spell4, 0.3 s, rendered
  by tools/lol/pose_ref.py: the staff held level in both hands, extended both ways, the body turning round), on a 4 x 2
  template of 5 px squares at his action sheets' density.

    python tools/art/pack_fix_1018.py      # -> ak/dist/redo_packs/akshan_gunhand_pack.zip, wukong_spin_pack.zip
"""
import os
import shutil
import zipfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
AK = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(AK, "assets", "source")
DIST = os.path.join(AK, "dist", "redo_packs")
SWAP = "C:/t/ak_work/swap"
TMP = "C:/t/ak_work/fix"
GREEN = (0, 255, 0)
DELIV_AK = "C:/Users/OWNER/Documents/Codex/2026-10-18/new-chat-14/outputs/akshan-actions"
DELIV_WK = "C:/Users/OWNER/Documents/Codex/2026-10-18/new-chat-16/outputs/wukong-actions"
SPIN_REF = "C:/t/ak_work/redo/refs/wkspin/monkeyking_spell4_60fps.png"
Z = 5
SPIN_CW, SPIN_CH, SPIN_SOLE = 100, 80, 72       # a spin cell in squares; the ground row in it

AK_PROMPT = """# 阿克尚 待机和 Q：枪换到和其他动作同一只手

用户看了阿克尚的新动作：「阿克尚枪会换手」要改。量过：**走路、平 A、E、R、挨打**里枪都在**前面那只手**（离我们近、开枪的那只手，枪在身体前侧）；只有**待机**和 **Q 的起手 / 收手**把枪举在**后面那只手**（枪在身体后侧的头边）。游戏里从待机切到走路或平 A 时，枪会突然跳到另一边。

这次只重画两张：**待机**（5 帧）和 **Q**（5 帧），**枪一直在前面那只手**，和 `3_参考_走路_枪在前手.png`、`4_参考_平A_枪在前手.png` 一样。

每张单独生成。上传：图1 = 骨架（`1_1_骨架_idle.png` 或 `1_2_骨架_skill1.png`），图2 = `2_角色定稿.png`（只看服装、颜色、体型），图3、图4 = 他现在的走路、平 A（**枪在哪只手照它们**），图5 = `5_现在的待机_枪在后手_不要.png`（**不要画成这样**）。

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（影哨 阿克尚）。

1. 保留图1所有帧的位置、大小、排列顺序（从左到右、从上到下）；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作。
3. 身体、服装、配色、体型（瘦、腿长）照图2，和图3、图4 一样大。
4. **枪只在前面那只手**（和图3、图4 同一只手、同一侧）：
   - 待机：前手把枪举在头前侧、枪口朝上，后手叉腰；轻轻呼吸。
   - Q（扔回旋镖）：起手时前手把枪收到肩边蓄力，然后往前甩出去，最后收回到待机的样子（枪还在前手）。
5. 不要画任何特效。
6. 像素画：方块大小和图2一样，1–2 像素深色描边，不要抗锯齿、不要渐变、不要模糊。背景纯绿色 #00FF00。

交付：两张整图 `akshan-idle.png`、`akshan-skill1.png`（和各自的图1 一样排列、一样大小），放在 `outputs/akshan-gunhand/`，原始生成图放 `raw/`，附 `generation-prompts.txt`，**最后**写 `HANDOFF.md`，再打包成 `outputs/akshan_gunhand_done.zip`。

## Claude 收到后（给 Claude 看）

import_swap_1018.py 读回（换成这次的两张），量枪在胯部的哪一侧（应和走路、平 A 同侧）。
"""

WK_PROMPT = """# 孙悟空 大招 R（大闹天宫）：转圈

用户：「猴子的 R 转圈还没做…这个要做啊」。英雄联盟里悟空的 R 是**双手横握金箍棒、棍子两头伸长，整个人原地转圈**，把周围的人打飞（`1_英雄联盟悟空_R转圈.png` 是英雄联盟原版这个动作的 8 个瞬间，0.3 秒转一圈）。

上传：图1 = `1_英雄联盟悟空_R转圈.png`（动作），图2 = `2_角色定稿.png`（服装、颜色、体型），图3 = `3_参考_悟空平A.png`（他现在的动作帧，**格子大小、画风照它**），图4 = `4_模板.png`（格子和地面线）。

---

画悟空转圈的 **8 帧**，排成 4×2，放在图4 的格子里（每格一帧，从左到右、从上到下；**每格 500×400 px，每个像素方块 5 px**，和图3 一样）：

1. **动作照图1**：双手握住金箍棒中段，棍子**横着、两头伸长**（比平时长一些，两边都伸出身体很远），**整个人原地转一圈**：第 1 帧面朝右（3/4 侧面），第 3 帧侧身，第 5 帧背对我们（看到背后、尾巴），第 7 帧侧身，第 8 帧回到快面朝右；身体略微下蹲，脚在原地小步转。棍子跟着转：有时横在前面，有时斜着、有时朝我们这边伸（变短）。
2. **每帧的脚底都踩在图4 的深绿地面线上**，人在格子中间，不要跑出格子。
3. 服装、颜色、体型照图2、图3：棕色猴毛、头顶翘起的深棕头发、绿眼睛、大红围巾、金红护臂、金色胸甲和鳞纹前摆、暗栗色袍裙、紫色鞋、**身后卷起的尾巴**（转到背面时尾巴在前面看得到）。金箍棒：橙红棒头、金箍、红色两端、灰色钢段，**笔直**。
4. 大小和图3 的悟空一样（不要变大变小）。
5. 不要画特效（不要风、不要光圈）——转圈的风我们另外加。
6. 像素画：方块大小和图3一样（每格 5 px，整齐对格），1–2 像素深色描边，不要抗锯齿、不要渐变、不要模糊。背景纯绿色 #00FF00，地面线也去掉。

交付：整张图 `wukong-spin.png`（2000×800，4×2），放在 `outputs/wukong-spin/`，原始生成图放 `raw/`，附 `generation-prompts.txt`，**最后**写 `HANDOFF.md`，再打包成 `outputs/wukong_spin_done.zip`。

## Claude 收到后（给 Claude 看）

import_swap_1018.py 的 cells() 读回（8 格，4×2），金箍棒检查直不直；接成游戏的 spin 标签（4–8 帧循环）。
"""


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def zip_dir(folder, name):
    os.makedirs(lp(DIST), exist_ok=True)
    zp = os.path.join(DIST, name + ".zip")
    with zipfile.ZipFile(lp(zp), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(folder)):
            z.write(os.path.join(folder, n), name + "/" + n)
    print(zp)


def fresh(name):
    out = os.path.join(TMP, name)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    return out


def akshan():
    out = fresh("akshan_gunhand_pack")
    sw = os.path.join(SWAP, "akshan_actions")
    shutil.copyfile(os.path.join(sw, "1_1_骨架_idle.png"), os.path.join(out, "1_1_骨架_idle.png"))
    shutil.copyfile(os.path.join(sw, "1_4_骨架_skill1.png"), os.path.join(out, "1_2_骨架_skill1.png"))
    shutil.copyfile(os.path.join(sw, "2_角色定稿.png"), os.path.join(out, "2_角色定稿.png"))
    shutil.copyfile(os.path.join(DELIV_AK, "akshan-run.png"), os.path.join(out, "3_参考_走路_枪在前手.png"))
    shutil.copyfile(os.path.join(DELIV_AK, "akshan-attack.png"), os.path.join(out, "4_参考_平A_枪在前手.png"))
    shutil.copyfile(os.path.join(DELIV_AK, "akshan-idle.png"), os.path.join(out, "5_现在的待机_枪在后手_不要.png"))
    with open(os.path.join(out, "PROMPT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(AK_PROMPT)
    shutil.copyfile(os.path.join(out, "PROMPT.md"), lp(os.path.join(DIST, "AKSHAN_GUNHAND_PROMPT.md")))
    zip_dir(out, "akshan_gunhand_pack")


def wukong():
    out = fresh("wukong_spin_pack")
    shutil.copyfile(SPIN_REF, os.path.join(out, "1_英雄联盟悟空_R转圈.png"))
    shutil.copyfile(os.path.join(SWAP, "wukong_actions", "2_角色定稿.png"), os.path.join(out, "2_角色定稿.png"))
    shutil.copyfile(os.path.join(DELIV_WK, "wukong-attack.png"), os.path.join(out, "3_参考_悟空平A.png"))
    can = Image.new("RGB", (4 * SPIN_CW * Z, 2 * SPIN_CH * Z), GREEN)
    d = ImageDraw.Draw(can)
    for i in range(8):
        cx, cy = (i % 4) * SPIN_CW * Z, (i // 4) * SPIN_CH * Z
        d.rectangle([cx, cy, cx + SPIN_CW * Z - 1, cy + SPIN_CH * Z - 1], outline=(0, 200, 0))
        d.rectangle([cx + 10, cy + SPIN_SOLE * Z, cx + SPIN_CW * Z - 11, cy + SPIN_SOLE * Z + Z - 1], fill=(0, 128, 0))
        d.text((cx + 6, cy + 4), str(i + 1), fill=(0, 90, 0))
    can.save(os.path.join(out, "4_模板.png"))
    with open(os.path.join(out, "PROMPT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(WK_PROMPT)
    shutil.copyfile(os.path.join(out, "PROMPT.md"), lp(os.path.join(DIST, "WUKONG_SPIN_PROMPT.md")))
    zip_dir(out, "wukong_spin_pack")


if __name__ == "__main__":
    akshan()
    wukong()
