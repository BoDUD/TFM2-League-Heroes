"""Gangplank's walk, third way: Codex draws ONLY his legs along a guide per leg (league_camille's accepted way,
tools/art/pack_camille_legs.py). Two skin swaps over oppi runs (Swain's, then Lucian's) never swapped the legs - read back,
one boot stayed ~20 squares behind the hips and the other under them in every frame (the user: 「没有明显换腿的感觉？」).

    python tools/art/pack_gangplank_legs.py      # -> ak/dist/redo_packs/gangplank_legs_pack.zip

Each of 8 frames: the design above the legs (rows < CUT, plus the cutlass and the coat tails outside the leg columns),
bobbed a square down on the contact frames and up on the passing ones, and two guides - the near leg red, the far leg blue:
hip -> knee -> ankle -> toe, at the design's leg length (hip row CUT to the soles), the knee bent forward (two-bone IK).
The feet follow a plain walk cycle facing right: a planted foot slides back under the hips, the other lifts and swings
forward, the legs trading front and back every half cycle (STEP squares either side of the hips).
"""
import math
import os
import shutil
import zipfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
AK = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(AK, "assets", "source", "gangplank")
DIST = os.path.join(AK, "dist", "redo_packs")
TMP = "C:/t/ak_work/gplegs"
GREEN, GROUND = (0, 255, 0), (0, 128, 0)
NEAR_C, FAR_C = (255, 0, 0), (0, 60, 255)
Z = 6
CW, CH = 72, 78                     # a cell in squares
SOLE = 70                           # the ground row in a cell
CUT = 46                            # design rows from here down are the legs (redrawn)
LEG_X = (10, 40)                    # the leg columns cleared below CUT (the coat tails left of it, the cutlass right)
HIP = {"near": 28, "far": 23}       # hip columns in the design
THIGH, SHIN = 8.5, 8.5
# per frame: (near ankle dx from its hip, near lift), (far ...), body bob (+ = down)
NEAR = [(7, 0), (3, 0), (-1, 0), (-5, 0), (-7, 0), (-3, 2), (2, 3), (6, 1)]
FAR = NEAR[4:] + NEAR[:4]
BOB = [1, 0, -1, 0, 1, 0, -1, 0]

PROMPT = """# 普朗克 走路：只画腿（照引导线）

用户：「没有明显换腿的感觉？」。前两次换皮（斯维因、卢锡安的骨架）读回来量过：**每一帧都是一只靴子在胯后、一只在胯下，两条腿从来没有前后交换**。这次换一个办法（卡蜜尔的腿就是这样做好的）：**上身我已经摆好了，你只画腿**。

上传顺序：图1 = `1_模板_腿的引导线.png`，图2 = `2_角色定稿.png`。

---

图1 是普朗克走路的 8 帧（4×2，每格一帧，从左到右、从上到下），**上身已经画好、腿空着**。每帧有两条引导线：
- **红线 = 近侧的腿**（离我们近、画在前面），**蓝线 = 远侧的腿**（画在后面、暗一档）；
- 每条线：胯 → 膝盖 → 脚踝 → 脚尖。

请在每一帧**沿着引导线画出两条腿**：深灰绿裤子（膝盖弯的地方照线弯），棕色翻边靴子（金色翻边）——**靴子画在线的末端，脚尖朝线指的方向**；抬起的脚（离地面线有空隙的那只）鞋跟抬起、离地。两条腿的样子、颜色、粗细照图2 的腿，远侧那条暗一档。画完把红线、蓝线全部去掉（换成腿），深绿地面线也去掉。

**只改腿**：上身、帽子、手炮、弯刀、大衣衣摆都不要动、不要重画、不要移动；整张图的大小、每格的位置都不变。

像素画：方块大小和图1 一样（每个像素方块一样大，整齐对格），1–2 像素深色描边，不要抗锯齿、不要渐变、不要模糊。背景保持纯绿色 #00FF00。

交付：整张图（和图1一样大）`gangplank-legs.png`，放在 `outputs/gangplank-legs/`，原始生成图放 `raw/`，附 `generation-prompts.txt`，**最后**写 `HANDOFF.md`，再打包成 `outputs/gangplank_legs_done.zip`。

## Claude 收到后（给 Claude 看）

读回每格（模板的格子和 6 px 一格，Codex 若整体缩放就按它自己的格子），上身用模板原样盖回，只取腿；量每帧两只靴子相对胯部的位置是否和引导线一致（前后脚每半圈交换），再接进 `rig_gangplank.py`。
"""


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def knee(hip, ankle):
    """Two-bone IK, the knee forward (+x)."""
    dx, dy = ankle[0] - hip[0], ankle[1] - hip[1]
    d = min(math.hypot(dx, dy), THIGH + SHIN - 0.01)
    a = math.atan2(dy, dx)
    c = (THIGH ** 2 + d ** 2 - SHIN ** 2) / (2 * THIGH * d)
    b = math.acos(max(-1.0, min(1.0, c)))
    # two solutions a +- b; pick the knee further forward
    k1 = (hip[0] + THIGH * math.cos(a - b), hip[1] + THIGH * math.sin(a - b))
    k2 = (hip[0] + THIGH * math.cos(a + b), hip[1] + THIGH * math.sin(a + b))
    return max(k1, k2, key=lambda k: k[0])


def main():
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")).copy()
    H, W = d.shape[:2]
    up = d.copy()
    up[CUT:, LEG_X[0]:LEG_X[1]] = 0
    ground_d = H                                    # the design's ground row (under the soles)
    ox = (CW - W) // 2
    oy = SOLE - ground_d
    can = Image.new("RGB", (4 * CW * Z, 2 * CH * Z), GREEN)
    dr = ImageDraw.Draw(can)
    guides = []
    for i in range(8):
        cx, cy = (i % 4) * CW, (i // 4) * CH
        bob = BOB[i]
        tile = np.zeros((CH, CW, 4), np.uint8)
        tile[oy + bob:oy + bob + H, ox:ox + W] = up
        m = tile[..., 3] > 0
        rgb = np.zeros((CH, CW, 3), np.uint8)
        rgb[:] = GREEN
        rgb[m] = tile[m][:, :3]
        can.paste(Image.fromarray(np.repeat(np.repeat(rgb, Z, 0), Z, 1)), (cx * Z, cy * Z))
        dr.rectangle([cx * Z + 8, (cy + SOLE) * Z, (cx + CW) * Z - 9, (cy + SOLE) * Z + Z - 1], fill=GROUND)
        g = {}
        for side, steps, col in (("far", FAR, FAR_C), ("near", NEAR, NEAR_C)):
            dx, lift = steps[i]
            hip = (ox + HIP[side] + 0.5, oy + bob + CUT + 0.5)
            ankle = (hip[0] + dx, SOLE - 2.5 - lift)
            kn = knee(hip, ankle)
            toe = (ankle[0] + 3, ankle[1] + 1.5)
            pts = [hip, kn, ankle, toe]
            g[side] = [(round(p[0], 1), round(p[1], 1)) for p in pts]
            dr.line([((cx + p[0]) * Z, (cy + p[1]) * Z) for p in pts], fill=col, width=Z)
            for p in pts:
                x, y = (cx + p[0]) * Z, (cy + p[1]) * Z
                dr.ellipse([x - Z, y - Z, x + Z, y + Z], fill=col)
        guides.append(g)
        dr.text((cx * Z + 6, cy * Z + 4), str(i + 1), fill=(0, 90, 0))
    out = os.path.join(TMP, "gangplank_legs_pack")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    can.save(os.path.join(out, "1_模板_腿的引导线.png"))
    dd = np.zeros((H + 8, W + 8, 3), np.uint8)
    dd[:] = GREEN
    m = d[..., 3] > 0
    dd[4:4 + H, 4:4 + W][m] = d[m][:, :3]
    Image.fromarray(np.repeat(np.repeat(dd, Z, 0), Z, 1)).save(os.path.join(out, "2_角色定稿.png"))
    with open(os.path.join(out, "PROMPT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    import json
    with open(os.path.join(SRC, "hd", "legs_guides.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(Z=Z, CW=CW, CH=CH, SOLE=SOLE, CUT=CUT, LEG_X=LEG_X, ox=ox, oy=oy, BOB=BOB, guides=guides), f)
    os.makedirs(lp(DIST), exist_ok=True)
    zp = os.path.join(DIST, "gangplank_legs_pack.zip")
    with zipfile.ZipFile(lp(zp), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(out)):
            z.write(os.path.join(out, n), "gangplank_legs_pack/" + n)
    shutil.copyfile(os.path.join(out, "PROMPT.md"), lp(os.path.join(DIST, "GANGPLANK_LEGS_PROMPT.md")))
    print(zp, can.size)


if __name__ == "__main__":
    main()
