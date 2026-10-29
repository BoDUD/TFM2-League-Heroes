#!/usr/bin/env python3
"""Sevika's run pack for Codex (assets/source/sevika/RUN_PROMPTS.md): her TFT run redrawn as 8 frames over its WHOLE
cycle, after the user's review of the first run (2026-10-29: 「走路感觉换腿不明显啊 之前发生过的问题」). Violet's way
(pack_violet_run.py, with what her two redraws taught: the leading leg changes, the toe gaps spelled out, real passing
frames).

    python tools/art/pack_sevika_run.py [--out C:/t/sv_work/sevika_run_pack] [--lol "D:/Riot Games/League of Legends"]

What was wrong with the first run (pack_sevika_poses run1-8 = run@0..817): her TFT run clip is 1.87 s for ONE cycle (two
steps), so 0..817 ms was only its first half - the far leg ahead in five frames, the legs together in two, the near leg
a little ahead in the last one, and then the loop jumped back to the far leg's wide stride: the legs never seemed to
swap. And Codex drew both legs in the same tones, so which leg led could not be seen.
Here: eight frames over the whole cycle at RUN's times (her clip measured 2026-10-29 by the toes: the far leg lands 15
squares ahead with the legs 35 apart, the near one lands 4 ahead, 13 apart; the near foot lands at ~700 ms where the
legs pass, the far leg swings through at ~1250 ms where they cross), both passings among them; MS gives each frame its
share of a 936 ms loop (as the clip spaces them). The same canvas, grid, scale and placing as the pose pack
(pack_sevika_poses: the design pose's body height = the design's 70 rows at PX px a square, the lowest point on SOLE_Y,
the pelvis on the design's PELVIS_COL). The NEAR leg (her right leg, nearer the camera: the BLUE line) is the same leg in
every frame: the design's own leg colours, over the other where they overlap; the FAR leg (the RED line) a step darker
in the design's own darker colours (FAR_COLOURS), behind. Which leg LEADS changes twice a cycle.
Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png; per frame
<k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row); 0_old_run_wrong.png (the first run,
what not to draw); feet.json (each frame's boots: heel and toe squares, lift, which leg leads - the table in
RUN_PROMPTS.md, and what the delivery is checked against).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
import pose_ref  # noqa: E402
import pack_sevika_poses as PK  # noqa: E402
from design_sevika_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sevika")
OLD = os.path.join(SRC, "codex_poses", "sevika-poses")
# (name, clip time in ms): the whole 1.87 s cycle, both passings in it
RUN = [("run1", 0), ("run2", 234), ("run3", 468), ("run4", 702), ("run5", 936), ("run6", 1092), ("run7", 1248),
       ("run8", 1560)]
CYCLE = 1870
LOOP_MS = 936                   # the game's loop: 8 frames, each its share of the clip's spacing
MS = [round(((RUN[(k + 1) % len(RUN)][1] - t) % CYCLE) * LOOP_MS / CYCLE) for k, (_n, t) in enumerate(RUN)]
N = len(RUN)
LIFTED = 3                       # a boot this many squares over the lower one still counts as on the ground
PX = PK.PX
NEAR, FAR = "blue", "red"        # her right leg (R_, the blue line) is nearer the camera (hip depth, the pose pack)
FAR_COLOURS = "trousers all #3D2629, knee pad all #292C48, the bare calf #CE6F51, the boot unchanged"
FAR_COLOURS_ZH = "裤子全用 `#3D2629`、护膝全用 `#292C48`、露出的小腿用 `#CE6F51`、靴子不变"
# how each frame's legs read (her TFT run, 0_run_cycle.png)
LOOK = {
    "run1": ("红腿（远侧、暗）在前面踩地，蓝腿（近侧）在后面**向后踢起**、小腿折起来，两只靴子分得最开",
             "the far (RED, darker) leg planted far ahead, the near (BLUE) leg kicked up behind, its shin folded - the widest split"),
    "run2": ("红腿还踩在前面（往身体下方收），蓝腿在后面抬着、开始往前摆",
             "the far (RED) foot still planted ahead, sliding back under her; the near (BLUE) leg lifted behind, starting to swing forward"),
    "run3": ("红腿踩在身体前下方，蓝腿（近侧）膝盖往前摆、靴子低低地从后面往前",
             "the far (RED) foot planted a little ahead; the near (BLUE) knee swinging forward, its boot low, coming through from behind"),
    "run4": ("**换腿的一帧**：蓝靴（近侧）落地、和红靴几乎上下对齐，红腿开始抬起",
             "THE PASSING: the near (BLUE) boot lands right beside the far (RED) one, the red heel lifting"),
    "run5": ("**蓝腿（近侧）在前**踩地，红腿（远侧、暗）在后面向后踢起、小腿折起",
             "the near (BLUE) leg FORWARD, planted; the far (RED, darker) leg kicked up behind, folded"),
    "run6": ("蓝腿踩在身体下方，红腿（远侧）在后面抬得最高、开始往前摆",
             "the near (BLUE) foot planted under her; the far (RED) leg lifted high behind, starting to swing forward"),
    "run7": ("**交叉的一帧**：红腿（远侧、暗）抬着从蓝腿**后面**往前迈过去，两只靴尖上下对齐，蓝腿在上面盖住它",
             "THE CROSSING: the far (RED) leg swinging forward BEHIND the planted near (BLUE) leg, the two toes one above the other, the blue leg drawn over it"),
    "run8": ("红腿（远侧）往前伸、快落地，蓝腿在后面蹬地、脚跟抬起",
             "the far (RED) leg reaching forward, about to land; the near (BLUE) leg pushing off behind, its heel up"),
}


def boot(jxy, names, side):
    """(heel square, toe square) of one leg: its Foot and Toe joints on the grid (x, y in squares)."""
    f, t = jxy[names[f"{side}_Foot"]], jxy[names[f"{side}_Toe"]]
    return [int(f[0] // PX), int(f[1] // PX)], [int(t[0] // PX), int(t[1] // PX)]


def gap(f):
    """The near toe ahead of the far one (squares; negative = the far toe ahead)."""
    return f[NEAR]["toe"][0] - f[FAR]["toe"][0]


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
            cells.append(f"靴尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        g = gap(f)
        lead = ("两只靴尖上下对齐" if abs(g) <= 2 else
                f"**{zh[NEAR]}（近侧）在前** {g} 格" if g > 0 else f"**{zh[FAR]}（远侧、暗）在前** {-g} 格")
        rows.append(f"| {k + 1} | `sevika-run-{name}.png` | run@{t} | {f['rows']} | {cells[0]} | {cells[1]} | {lead} | "
                    f"{LOOK[name][0]} |")
    near_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) > 2)
    far_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) < -2)
    passing = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if abs(gap(feet[n])) <= 2)
    lines = "\n".join(
        f"- {name}: `RUN {k + 1} of 8 - {LOOK[name][1]}. "
        + ", ".join(
            f"the {c.upper()} leg's boot {'ON THE GROUND' if round(feet[name][c]['lift'] - min(feet[name]['red']['lift'], feet[name]['blue']['lift'])) <= LIFTED else 'LIFTED'}, its toe at square ({feet[name][c]['toe'][0]}, {feet[name][c]['toe'][1]})"
            for c in (NEAR, FAR))
        + f"; the two toes {abs(gap(feet[name]))} square{'' if abs(gap(feet[name])) == 1 else 's'} apart"
        + ("" if abs(gap(feet[name])) <= 2 else f", the {(NEAR if gap(feet[name]) > 0 else FAR).upper()} one ahead")
        + f"; about {feet[name]['rows']} squares tall.`"
        for k, (name, _t) in enumerate(RUN))
    return f"""# 塞薇卡：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「走路感觉换腿不明显」**。上一版（`0_old_run_wrong.png`）有两个问题：① 八帧只画了金铲铲跑步动画的**前半个循环**（她的跑步一个循环 1.87 秒、迈两步），所以几乎每帧都是同一条腿在前，播放到最后一帧又一下子跳回第一帧；② **两条腿画成一样的颜色**，看不出哪条腿在前。
> - 金铲铲里她是这样跑的（`0_run_cycle.png`，这次 8 帧是**一个完整的循环**）：机械臂沉沉地垂在身前，**两条腿轮流迈步**——第 {far_lead} 帧远侧那条腿在前，第 {passing} 帧两条腿交错经过（**换腿**），第 {near_lead} 帧近侧那条腿在前。
> - 请你画 **{N} 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **{PX} px**，画布 **{C} × {C}**，红线是地面（**脚底 y = {S}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。**请严格用每格 {PX} px**。
> - **样子、颜色、画法全照定稿** `0_design.png`，**上半身（头、躯干、两条胳膊、机械臂、老虎机）的大小和画法照上一版的跑步**（`0_old_run_wrong.png` 上面一排：用户看过、没有意见的就是上半身），**八帧的上半身一样大**、跟着步子上下起伏 0–2 格；要改的只是腿。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。机械臂不要挡住脸。

## 最要紧的：两条腿看得出谁在前

骨架里 **蓝线 = 近侧的腿**（她的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（深棕裤子 `#604345` 带暗面、藏青护膝 `#454E77` 带高光、小腿露出的浅肤色、深色靴子和金色靴头），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：{FAR_COLOURS_ZH}；**永远在近侧那条腿后面**。
- 机械臂垂在身前，会挡住一部分腿：照参考图挡，**但两只靴子每帧都要露出来**。

**哪条腿在前（靴子更靠画面右边）每半个循环换一次**：第 {far_lead} 帧**暗的红腿在前**，第 {near_lead} 帧**亮的蓝腿在前**，第 {passing} 帧两只靴子几乎上下对齐（换腿的那一刻）。第 7 帧是**交叉**：暗的红腿从亮的蓝腿后面往前迈，蓝腿盖在上面。

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只靴尖之间的距离照表**（上一版的毛病就是距离不对、谁在前不对）。没有哪只靴子是一直不动的：两只靴子轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）、`0_old_run_wrong.png`（上半身照它，腿不要照它）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {C}x{C} canvas with {PX} px squares (her soles on y {S}) - a BROAD-SHOULDERED, STURDY WOMAN with dark brown hair combed back, a warm square face, thick dark brows, grey eyes; a dark navy short-sleeved top with gold diamond shoulder badges, a brown leather cropped vest (bare midriff), a brown belt with a small grey pouch, dark brown trousers ending at mid-calf with NAVY KNEE PADS, a strip of bare calf, dark boots with GOLD TOE CAPS; her LEFT ARM a HUGE BRASS MECHANICAL ARM (a slot machine on its shoulder, teal plates with magenta spikes, bright cyan claws). Image A stands in a guard - copy only her look. B her HEAD shown 8x. C a 3D RENDER of this same character's own game model in THIS FRAME OF HER RUN, on the same {C} canvas and grid, already scaled and placed where the picture must be (copy the pose of the legs, never its 3D shading). D the SKELETON of that frame, exactly over C: green = the spine, ORANGE = her flesh right arm, CYAN = the mechanical arm (the PURPLE line with a GOLD TRIANGLE = its claws, the PURPLE RING = the slot machine), the BLUE line = her NEAR leg, the RED line = her FAR leg, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole run cycle, 8 frames in a row. F her OLD run (top row): copy its UPPER BODY - the head, torso, both arms and the mechanical arm, their size and drawing; NOT its legs (crossed out: wrong).
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY {PX} px, aligned on one straight grid from the canvas corner; her lowest point on y {S}.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (brown trousers, navy knee pad with its light shade, the bare calf, the boot with its gold toe cap), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design ({FAR_COLOURS}), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. Each boot exactly where D puts it; one boot on the ground, the other lifted unless the line says both are down. Both boots always visible below the mechanical arm.
COUNT THE SQUARES: the same body size in every frame and the same as image F's upper body; the boots as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. Nothing covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

{lines}

## 交回

- 每帧一张：`outputs/sevika-run/sevika-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/sevika-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只靴尖的格子和距离（上表）、**谁在前**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**，不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格、谁在前。
- **{N} 帧都画完再交**，最后写 `outputs/sevika-run/HANDOFF.md`，再打包成 `outputs/sevika_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sevika/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头（下巴对下巴，design_sevika_poses.py），逐帧对 `feet.json` 量两只靴尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 {LOOP_MS} ms 一个循环）：{MS}。
- 这份提示词和参考图由 `tools/art/pack_sevika_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sv_work\sevika_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    poser = PK.Poser(a.lol)
    names = poser.names
    hv = PK.vertices_of(poser, PK.HEAD_JOINTS)
    sv = PK.arm_vertices(poser)
    cv = PK.vertices_of(poser, ("L_Clamp",))
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    C, SOLE_Y = PK.CANVAS, PK.SOLE_Y

    # the pose pack's scale and the design's place (pack_sevika_poses.main)
    iv, ij = poser.pose(PK.DESIGN)
    pxy, _ = PK.Poser.project(iv, PK.YAW, 1.0, 0.0, 0.0)
    scale = PK.ROWS * PX / (pxy[~sv, 1].max() - pxy[~sv, 1].min())
    pel = names["Pelvis"]
    dx = (C - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - design.height * PX
    pelvis_x = dx + PK.PELVIS_COL * PX + PX // 2
    can = Image.new("RGBA", (C, C), PK.GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, design.height * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(PK.HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, PK.GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "0_head.png")))
    # the design pose's skeleton over the design (as the pose pack draws it)
    ixy, _ = PK.Poser.project(iv, PK.YAW, scale, 0.0, 0.0)
    jxy0, jz0 = PK.Poser.project(ij, PK.YAW, scale, 0.0, 0.0)
    ground0 = SOLE_Y - ixy[:, 1].max()
    shift0 = pelvis_x - jxy0[pel, 0]
    ixy[:, 0] += shift0
    ixy[:, 1] += ground0
    jxy0[:, 0] += shift0
    jxy0[:, 1] += ground0
    PK.skeleton(poser, ij, jxy0, jz0, (0, 0, 0, 0), os.path.join(a.out, "0_design_skeleton.png"),
                PK.claw_line(ixy, cv, jxy0[names["L_Hand"]]), tuple(jxy0[names["L_ShoulderArmor"]]), can)
    feet, refs = {}, []
    for k, (name, t) in enumerate(RUN):
        clip = f"run@{t}"
        verts, joints = poser.pose(clip)
        xy, z = PK.Poser.project(verts, PK.YAW, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = PK.Poser.project(joints, PK.YAW, scale, 0.0, 0.0)
        # the near leg: the hip nearer the camera (the larger depth) - her right one in every frame of the run (the
        # guard pose of the design is turned the other way, so the run's own frames decide)
        if not jz[names["R_Hip"]] > jz[names["L_Hip"]]:
            sys.exit(f"{name}: the near leg is not her right one: NEAR / FAR and the prompt's colours are wrong")
        shift = pelvis_x - jxy[pel, 0]
        xy[:, 0] += shift
        xy[:, 1] += ground
        if xy[:, 1].min() < 40:
            sys.exit(f"{name}: the head {xy[:, 1].min():.0f} px from the top (fewer px a square)")
        top = int(xy[:, 1].min() // PX)
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        stem = f"{k + 1}_{name}"
        PK.skeleton(poser, joints, jxy, jz, (hx.min(), hy.min(), hx.max(), hy.max()),
                    os.path.join(a.out, f"{stem}_skeleton.png"), PK.claw_line(xy, cv, jxy[names["L_Hand"]]),
                    tuple(jxy[names["L_ShoulderArmor"]]))
        im = pose_ref.render_hq(verts, poser.tris, poser.m.v["uv"], poser.m.tex, -PK.YAW, PK.PITCH, (C, C), scale,
                                ground, shift=-shift / C - 0.5, tri_tex=poser.m.tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (C, C), PK.GREY + (255,))
        PK.grid(ImageDraw.Draw(ref))
        ref.alpha_composite(im)
        ref = ref.convert("RGB")
        ref.save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        refs.append(ref)
        # each boot: heel and toe squares, its lowest point on the ground or lifted (squares above the ground line)
        f = {"rows": int(SOLE_Y // PX) - top, "ms": MS[k]}
        for side, colour in (("L", "red"), ("R", "blue")):
            heel, toe = boot(jxy, names, side)
            low = max(jxy[names[f"{side}_Foot"], 1], jxy[names[f"{side}_Toe"], 1])
            f[colour] = {"heel": heel, "toe": toe, "lift": round(float((SOLE_Y - low) / PX), 1)}
        f["lead"] = "red" if jxy[names["L_Toe"], 0] > jxy[names["R_Toe"], 0] else "blue"
        f["near_leg"], f["clip"] = NEAR, clip
        feet[name] = f
        print(stem, clip, "gap", gap(f), "lead", f["lead"], "lift", f["blue"]["lift"], f["red"]["lift"], "rows", f["rows"])

    # the whole cycle at a glance: each ref cropped round the figure's column band, in a row
    band = (C // 2 - 380, 60, C // 2 + 380, SOLE_Y + 20)
    w, h = band[2] - band[0], band[3] - band[1]
    strip = Image.new("RGB", (N * w // 2 + (N - 1) * 6, h // 2 + 40), (255, 255, 255))
    d = ImageDraw.Draw(strip)
    for k, r in enumerate(refs):
        strip.paste(r.crop(band).resize((w // 2, h // 2), Image.LANCZOS), (k * (w // 2 + 6), 40))
        g = gap(feet[RUN[k][0]])
        lab = "pass" if abs(g) <= 2 else ("near (blue) ahead" if g > 0 else "far (red) ahead")
        d.text((k * (w // 2 + 6) + 8, 10), f"run{k + 1}  {lab}", fill=(0, 0, 0))
    strip.save(lp(os.path.join(a.out, "0_run_cycle.png")))

    # the first run, what not to draw (its legs; its upper body is the one to keep)
    old = [Image.open(lp(os.path.join(OLD, f"sevika-pose-run{k}.png"))).convert("RGBA") for k in range(1, 9)]
    cut = [o.crop(o.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()) for o in old]
    hh = max(c.height for c in cut)
    sheet = Image.new("RGBA", (sum(c.width for c in cut) + 30 * 9, hh + 90), (255, 255, 255, 255))
    x = 30
    for c in cut:
        sheet.alpha_composite(c, (x, 90 + hh - c.height))
        x += c.width + 30
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
    d.text((30, 4), "OLD RUN: keep the UPPER BODY (head, torso, arms, mechanical arm) - its size and drawing.",
           fill=(0, 120, 0), font=font)
    d.text((30, 44), "WRONG LEGS: only half the cycle, the same leg ahead, both legs the same colour - do not copy the legs.",
           fill=(200, 0, 0), font=font)
    leg_top = 90 + hh - round(hh * 0.42)
    d.line([(0, leg_top), (sheet.width, sheet.height)], fill=(220, 0, 0), width=8)
    d.line([(0, sheet.height), (sheet.width, leg_top)], fill=(220, 0, 0), width=8)
    sheet.convert("RGB").resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(
        lp(os.path.join(a.out, "0_old_run_wrong.png")))

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
