#!/usr/bin/env python3
"""Idas's run pack for Codex (assets/source/idas/RUN_PROMPTS.md): her TFT run as 8 frames over its WHOLE cycle, with
clear leg swaps (the user, 2026-10-30: 「走路要有明显的腿部交换啊」). Steb's run pack's way (pack_steb_run.py: the
leading leg changes, the toe squares spelled out, real passing frames, the near and far legs in two tones), so the
glide is not drawn as one gliding body with the legs lost under the wings.

    python tools/art/pack_idas_run.py [--out D:/TFM2-Workshop/idas_packs/idas_run_pack] [--lol "D:/Riot Games/League of Legends"]

TFT's run clip (animations/tft7_dragongold_run.anm, 0.667 s) is a four-legged bound: the body level, the wing-claws on
the ground, the legs folded under the wings - no visible swap. So the walk is her own (pack_idas_poses.Poser.walk_mats):
her idle, the legs mirrored to one stance, the thighs swung half a cycle apart, the swinging knee bent; eight even
frames (walk@0..7) with both passings (run1, run6) and both widest splits (run3 far ahead, run7 near ahead); each frame
stands on its lower foot.
The same canvas, grid, scale and placing as the pose pack (pack_idas_poses: the design pose's height = the design's 98
rows at PX px a square, the lowest point on SOLE_Y, the root on the design's root column; the tail shortened to
TAIL_SCALE). The NEAR leg (her right leg, nearer the camera: the BLUE line) is the same leg in every frame: the
design's own leg colours, over the other where they overlap; the FAR leg (the RED line) a step darker in the design's
own darker colours (FAR_COLOURS), behind. Which leg LEADS changes twice a cycle.
Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png; per frame
<k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row); feet.json (each frame's feet: heel and
toe squares, lift, which leg leads - the table in RUN_PROMPTS.md, and what the delivery is checked against).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
import pose_ref  # noqa: E402
import pack_idas_poses as PK  # noqa: E402
from design_idas_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "idas")
RUN = [(f"run{k + 1}", k) for k in range(PK.WALK_N)]   # walk@k: frame k of her walk (pack_idas_poses.Poser.walk_mats)
LOOP_MS = 720                    # the game's loop: 8 even frames
MS = [LOOP_MS // len(RUN)] * len(RUN)
N = len(RUN)
LIFTED = 3                       # a foot this many squares over the lower one still counts as on the ground
PX = PK.PX
NEAR, FAR = "blue", "red"        # her right leg (R_, the blue line) is nearer the camera (hip depth, every run frame)
NEAR_COLOURS_ZH = ("金色腿甲 `#FCD612` / `#FABE0A` / `#F49802` / `#C96C01`、深紫褐色的脚踝和脚 `#442930` / `#241317`、"
                   "灰色爪子 `#C0BEE3` / `#878AA3` / `#646481`")
FAR_COLOURS = "the gold plates only #C96C01 and #9F5201, the ankles and feet all #241317, the claws all #646481"
FAR_COLOURS_ZH = "金色腿甲只用 `#C96C01` 和 `#9F5201`、脚踝和脚全用 `#241317`、爪子全用 `#646481`"
# how each frame's legs read (her TFT run, 0_run_cycle.png)
LOOK = {
    "run1": ("**换腿的一帧**：红腿（远侧、暗）抬着从蓝腿**后面**往前迈过去，两只脚几乎上下对齐，蓝腿踩在身体下方、盖在上面",
             "THE PASSING: the far (RED, darker) leg lifted, swinging forward BEHIND the planted near (BLUE) one, the two "
             "feet almost one above the other, the blue leg drawn over it"),
    "run2": ("红腿往前伸、快落地，蓝腿踩在后面", "the far (RED) leg reaching forward, about to land; the near (BLUE) foot planted behind"),
    "run3": ("**红腿在前**、两只脚分得最开，两只脚都踩在地上",
             "the far (RED) leg FORWARD - the widest split, both feet on the ground"),
    "run4": ("红腿踩在前面，蓝腿（近侧）在后面**抬起来**、准备往前摆",
             "the far (RED) foot planted ahead; the near (BLUE) leg LIFTED behind, about to swing forward"),
    "run5": ("蓝腿抬着往前摆、膝盖弯着，红腿踩在身体下方",
             "the near (BLUE) leg lifted and swinging forward, its knee bent; the far (RED) foot planted under her"),
    "run6": ("**交叉的一帧**：蓝腿（近侧）从红腿**前面**经过，两只脚上下对齐，蓝腿盖在红腿上面",
             "THE CROSSING: the near (BLUE) leg passing in front of the far (RED) one, the two feet one above the other, "
             "the blue leg drawn over it"),
    "run7": ("**蓝腿在前**往前伸，红腿在后面抬起来", "the near (BLUE) leg FORWARD, reaching out; the far (RED) leg lifting behind"),
    "run8": ("蓝腿踩在前面，红腿（远侧）在后面**抬得最高**、开始往前摆",
             "the near (BLUE) foot planted ahead; the far (RED) leg LIFTED high behind, starting to swing forward"),
}


def foot(jxy, names, side):
    """(heel square, toe square) of one leg: its foot and toe joints on the grid (x, y in squares)."""
    f, t = jxy[names[f"{side}_foot"]], jxy[names[f"{side}_toe"]]
    return [int(f[0] // PX), int(f[1] // PX)], [int(t[0] // PX), int(t[1] // PX)]


def gap(f):
    """The near toe ahead of the far one (squares; negative = the far toe ahead)."""
    return f[NEAR]["toe"][0] - f[FAR]["toe"][0]


def down(f, colour):
    return round(f[colour]["lift"] - min(f["red"]["lift"], f["blue"]["lift"])) <= LIFTED


def prompts(feet):
    C, S = PK.CANVAS, PK.SOLE_Y
    zh = {"red": "红腿", "blue": "蓝腿"}
    rows = []
    for k, (name, t) in enumerate(RUN):
        f = feet[name]
        cells = []
        for colour in (NEAR, FAR):
            b = f[colour]
            up = round(b["lift"] - min(f["red"]["lift"], f["blue"]["lift"]))
            where = "**踩在地上**" if up <= LIFTED else f"**抬起来**（比另一只高约 {up} 格）"
            cells.append(f"脚尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        g = gap(f)
        lead = ("两只脚尖上下对齐（交叉）" if abs(g) <= 2 else
                f"**{zh[NEAR]}（近侧）在前** {g} 格" if g > 0 else f"**{zh[FAR]}（远侧、暗）在前** {-g} 格")
        rows.append(f"| {k + 1} | `idas-run-{name}.png` | walk@{t} | {f['rows']} | {cells[0]} | {cells[1]} | {lead} | "
                    f"{LOOK[name][0]} |")
    near_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) > 2)
    far_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) < -2)
    passing = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if abs(gap(feet[n])) <= 2)
    lines = "\n".join(
        f"- {name}: `RUN {k + 1} of 8 - {LOOK[name][1]}. "
        + ", ".join(f"the {c.upper()} leg's foot {'ON THE GROUND' if down(feet[name], c) else 'LIFTED'}, its toe at "
                    f"square ({feet[name][c]['toe'][0]}, {feet[name][c]['toe'][1]})" for c in (NEAR, FAR))
        + f"; the two toes {abs(gap(feet[name]))} square{'' if abs(gap(feet[name])) == 1 else 's'} apart"
        + ("" if abs(gap(feet[name])) <= 2 else f", the {(NEAR if gap(feet[name]) > 0 else FAR).upper()} one ahead")
        + f"; about {feet[name]['rows']} squares tall.`"
        for k, (name, _t) in enumerate(RUN))
    return f"""# 艾达丝：走路（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。** 这一包**代替**动作包里原来的 8 帧移动（`idas_pose_pack` 已经去掉了 run1–run8）。
> - **走路一定要看得出两条腿明显地前后交换**（用户：「走路要有明显的腿部交换啊」）。以前几个英雄的走路被退回过（「换腿不明显」「走路腿没有前后交换」）：八帧只画了半个循环、两条腿画成一样的颜色、腿被别的东西挡住。这次照下面做。
> - 她这样走（`0_run_cycle.png`，8 帧是**一个完整的循环**，迈两步；金铲铲原版是趴着往前扑、看不出换腿，所以用她自己的模型做了直立走路）：身子和待机一样微微前倾，两只翅膀手臂垂在身前，长尾巴在身后，**两条反关节腿轮流迈步**——第 {far_lead} 帧远侧那条腿在前，第 {passing} 帧两条腿交错经过（**换腿、交叉**），第 {near_lead} 帧近侧那条腿在前。
> - 请你画 **{N} 帧走路**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型摆出的这一帧走路，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **{PX} px**，画布 **{C} × {C}**，红线是地面（**脚底 y = {S}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。**请严格用每格 {PX} px**。
> - **样子、颜色、画法全照定稿** `0_design.png`：有棱角的金鳞甲、深棕胸腹、青蓝宝石；青蓝鬃冠和角、发光的青蓝眼睛；翅膀手臂上的金色羽刃翼和深灰三指爪；长尾巴和尾刃。**八帧的身体一样大**、跟着步子上下起伏 0–2 格。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体移动，不要转头。
> - **翅膀手臂和金翼不能挡住腿**：两条腿（从胯到脚）每帧都要整条看得见；翅膀照参考图放在身前、腿的上方。

## 最要紧的：两条腿看得出谁在前、有交叉步

骨架里 **蓝线 = 近侧的腿**（她的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。腿是反关节的（像鸟腿：大腿往前，膝盖往后弯，下面是细长的跗骨和三趾的脚）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（{NEAR_COLOURS_ZH}），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：{FAR_COLOURS_ZH}；**永远在近侧那条腿后面**。
- 两只脚每帧都要露出来，脚和爪子和定稿一样大。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 {far_lead} 帧**暗的红腿在前**，第 {near_lead} 帧**亮的蓝腿在前**，第 {passing} 帧两只脚几乎上下对齐（换腿的那一刻，两条腿**交叉**：一条从另一条旁边经过，蓝腿盖在上面）。

**每一帧画完，数格子核对两只脚**：脚尖（爪子最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只脚尖之间的距离照表**。没有哪只脚是一直不动的：两只脚轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, side view facing right, on a {C}x{C} canvas with {PX} px squares (her feet on y {S}) - a GOLDEN DRAGON on two backward-bending (digitigrade) legs: angular faceted gold scale plates, a dark brown chest and belly, cyan gems; the head thrust forward with a cyan fan crest, swept-back cyan horns, a crescent pale-cyan cheek horn, a snout horn, a glowing cyan eye; her arms are her wings, each gold forearm carrying a golden feather-blade wing and ending in a dark grey three-taloned claw; a long gold tail with a dark grey-violet blade. Her LEGS: gold thigh plates, dark mauve-brown ankles and feet, grey claws. Image A stands idle - copy only her look. B her HEAD shown 8x. C a 3D RENDER of this same creature's own game model in THIS FRAME OF HER WALK, on the same {C} canvas and grid, already scaled and placed where the picture must be (copy the pose of the body, the wing-arms and the legs, never its 3D shading; the head already enlarged). D the SKELETON of that frame, exactly over C: green = the spine, PURPLE / ORANGE = the near / far wing-arm (the big dot = the claw), the BLUE line = her NEAR leg, the RED line = her FAR leg, BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole walk cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY {PX} px, aligned on one straight grid from the canvas corner; her lowest point on y {S}.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A, in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design ({FAR_COLOURS}), and always BEHIND the near one. Each leg bends BACKWARD at its knee like a bird's, along its line. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the PASSING / CROSSING frames the two legs cross: one passes beside the other, the near leg drawn over it. Each foot exactly where D puts it; one foot on the ground, the other lifted unless the line says both are down. Both legs WHOLE and visible, from the hip to the claws - the wing-arms and the wings never cover them.
COUNT THE SQUARES: the same body size in every frame and the same as image A; the feet and claws as big as in A; legs never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

{lines}

## 交回

- 每帧一张：`outputs/idas-run/idas-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/idas-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**交叉的帧两条腿真的交叉**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**、**两条腿整条露出来**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **{N} 帧都画完再交**，最后写 `outputs/idas-run/HANDOFF.md`，再打包成 `outputs/idas_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/idas/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头，逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；身体大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 {LOOP_MS} ms 一个循环）：{MS}。
- 这份提示词和参考图由 `tools/art/pack_idas_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\idas_packs\idas_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    poser = PK.Poser(a.lol)
    names = poser.names
    names.update({"R_foot": names["R_Foot"], "R_toe": names["R_Toe"]})
    hv = PK.head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    C, SOLE_Y = PK.CANVAS, PK.SOLE_Y

    # the pose pack's scale and the design's place (pack_idas_poses.main)
    iv, ij = poser.pose(PK.DESIGN)
    pxy, _ = PK.Poser.project(iv, PK.YAW, 1.0, 0.0, 0.0)
    scale = PK.ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = names["Root"]
    dx = (C - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - design.height * PX
    ix = PK.Poser.project(iv, PK.YAW, scale, 0.0, 0.0)[0][:, 0]
    jx = PK.Poser.project(ij, PK.YAW, scale, 0.0, 0.0)[0][pel, 0]
    x0, _, x1, _ = design.getbbox()
    pelvis_x = dx + round((x0 + (jx - ix.min()) / (ix.max() - ix.min()) * (x1 - x0)) * PX)
    can = Image.new("RGBA", (C, C), PK.GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, design.height * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(PK.HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, PK.GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "0_head.png")))

    # her feet: the vertices the foot, toe and claw joints carry most (the walk stands on its lower foot, not on the
    # tail or a hanging claw)
    joint_of = np.array(poser.m.infl)[poser.m.v["bones"].astype(np.int64)]
    main_j = joint_of[np.arange(len(poser.m.v)), np.argmax(poser.m.v["w"], axis=1)]
    feet_v = np.isin(main_j, [names[j] for j in ("l_foot", "l_toe", "l_tip", "R_Foot", "R_Toe", "R_Tip")])

    def placed(verts, joints, on_feet=False):
        xy, z = PK.Poser.project(verts, PK.YAW, scale, 0.0, 0.0)
        ground = SOLE_Y - (xy[feet_v, 1].max() if on_feet else xy[:, 1].max())
        jxy, jz = PK.Poser.project(joints, PK.YAW, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        lo, hi = xy[:, 0].min() + shift, xy[:, 0].max() + shift
        shift += max(0, PK.MARGIN - lo) - max(0, hi - (C - PK.MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        return xy, jxy, jz, ground, shift

    _, jxy0, jz0, _, _ = placed(iv, ij)
    PK.skeleton(poser, jxy0, jz0, (0, 0, 0, 0), os.path.join(a.out, "0_design_skeleton.png"), can)
    feet, refs = {}, []
    for k, (name, t) in enumerate(RUN):
        clip = f"walk@{t}"
        verts, joints = poser.pose(clip)
        xy, jxy, jz, ground, shift = placed(verts, joints, on_feet=True)
        if xy[:, 1].max() > SOLE_Y + PX:
            sys.exit(f"{name}: something hangs {(xy[:, 1].max() - SOLE_Y) / PX:.1f} squares under the ground (the tail?)")
        # the near leg: the hip nearer the camera (the larger depth) - her right one in every frame of the run
        if not jz[names["R_Thigh"]] > jz[names["l_thigh"]]:
            sys.exit(f"{name}: the near leg is not her right one: NEAR / FAR and the prompt's colours are wrong")
        top = int(xy[:, 1].min() // PX)
        hx, hy = xy[hv, 0], xy[hv, 1]
        stem = f"{k + 1}_{name}"
        PK.skeleton(poser, jxy, jz, (hx.min(), hy.min(), hx.max(), hy.max()), os.path.join(a.out, f"{stem}_skeleton.png"))
        im = pose_ref.render_hq(verts.copy(), poser.tris, poser.m.v["uv"], poser.m.tex, -PK.YAW, PK.PITCH, (C, C),
                                scale, ground, shift=-shift / C - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (C, C), PK.GREY + (255,))
        PK.grid(ImageDraw.Draw(ref))
        ref.alpha_composite(im)
        ref = ref.convert("RGB")
        ref.save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        refs.append(ref)
        # each foot: heel and toe squares, its lowest point on the ground or lifted (squares above the ground line)
        f = {"rows": int(SOLE_Y // PX) - top, "ms": MS[k]}
        side_v = {"l": np.isin(main_j, [names[j] for j in ("l_foot", "l_toe", "l_tip")]),
                  "R": np.isin(main_j, [names[j] for j in ("R_Foot", "R_Toe", "R_Tip")])}
        for side, colour in (("l", "red"), ("R", "blue")):
            heel, toe = foot(jxy, names, side)
            low = xy[feet_v & side_v[side], 1].max()
            f[colour] = {"heel": heel, "toe": toe, "lift": round(float((SOLE_Y - low) / PX), 1)}
        f["lead"] = "red" if jxy[names["l_toe"], 0] > jxy[names["R_toe"], 0] else "blue"
        f["near_leg"], f["clip"] = NEAR, clip
        feet[name] = f
        print(stem, clip, "gap", gap(f), "lead", f["lead"], "lift", f["blue"]["lift"], f["red"]["lift"], "rows", f["rows"])

    # the whole cycle at a glance: each ref cropped round the figure's band, in a row
    band = (60, 420, C - 60, SOLE_Y + 20)
    w, h = band[2] - band[0], band[3] - band[1]
    strip = Image.new("RGB", (N * w // 3 + (N - 1) * 6, h // 3 + 40), (255, 255, 255))
    d = ImageDraw.Draw(strip)
    for k, r in enumerate(refs):
        strip.paste(r.crop(band).resize((w // 3, h // 3), Image.LANCZOS), (k * (w // 3 + 6), 40))
        g = gap(feet[RUN[k][0]])
        lab = "PASS / CROSS" if abs(g) <= 2 else ("near (blue) ahead" if g > 0 else "far (red) ahead")
        d.text((k * (w // 3 + 6) + 8, 10), f"run{k + 1}  {lab}", fill=(0, 0, 0))
    strip.save(lp(os.path.join(a.out, "0_run_cycle.png")))

    with open(lp(os.path.join(a.out, "feet.json")), "w", encoding="utf-8") as fp:
        json.dump(feet, fp, indent=1)
    text = prompts(feet)
    for path in (os.path.join(SRC, "RUN_PROMPTS.md"), os.path.join(a.out, "RUN_PROMPTS.md")):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as fp:
            fp.write(text)
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "MS", MS)


if __name__ == "__main__":
    main()
