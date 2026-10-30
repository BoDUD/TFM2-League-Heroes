#!/usr/bin/env python3
"""Zippy's run pack for Codex (assets/source/zippy/RUN_PROMPTS.md): its TFT sprint redrawn as 8 frames over its WHOLE
cycle, after the user's review of the first run (2026-10-31: 「感觉走路换腿有点问题啊」). Sevika's way
(pack_sevika_run.py: the leading leg changes, the toe gaps spelled out, real passing frames).

    python tools/art/pack_zippy_run.py [--out D:/TFM2-Workshop/zippy_packs/zippy_run_pack] [--lol "D:/Riot Games/League of Legends"]

What was wrong with the first run (pack_zippy_poses run1-8, Codex's zippy-pose-run1..8): the pack's eight times did
cover the whole 0.8 s cycle with both passings (260 and 740 ms), but Codex drew every frame with the legs split, one
ahead and one behind - no frame where they pass - and the near leg (its big light thigh) ahead in seven of the eight;
the far leg barely darker. So the same leg seemed to lead all the time and the legs never crossed.
Here: eight frames at RUN's times (its clip measured 2026-10-31 by the toes on this pack's grid: the near foot leads by up
to 13.5 squares at ~120 ms, the far one by up to 30 at ~520 ms; the feet pass at ~255 and ~740 ms - the far leg leads
the longer part of the cycle, as TFT has it); MS gives each frame its share of the 800 ms loop. The same canvas, grid,
scale and placing as the pose pack (pack_zippy_poses: the design pose's height = the design's 83 rows at PX px a square,
the lowest point on SOLE_Y, the root on the design's root column). The NEAR leg (its right leg, nearer the camera in
every frame: the BLUE line) is the same leg in every frame: the design's own leg colours, over the other where they
overlap; the FAR leg (the RED line) a step darker in the design's own darker colours (FAR_COLOURS), behind. Which leg
LEADS changes twice a cycle.
Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png; per frame
<k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row); 0_old_run_wrong.png (the first run:
keep its upper body, not its legs); feet.json (each frame's feet: heel and toe squares, lift, which leg leads - the
table in RUN_PROMPTS.md, and what the delivery is checked against).
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
import pack_zippy_poses as PK  # noqa: E402
from design_zippy_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zippy")
OLD = os.path.join(SRC, "codex_poses", "zippy-poses")
# (name, clip time in ms): the whole 0.8 s cycle, both passings in it
RUN = [("run1", 0), ("run2", 120), ("run3", 255), ("run4", 360), ("run5", 440), ("run6", 520), ("run7", 620),
       ("run8", 740)]
CYCLE = 800
LOOP_MS = 800                    # the game's loop: 8 frames, each its share of the clip's spacing
MS = [round(((RUN[(k + 1) % len(RUN)][1] - t) % CYCLE) * LOOP_MS / CYCLE) for k, (_n, t) in enumerate(RUN)]
N = len(RUN)
LIFTED = 4                       # a foot this many squares over the lower one still counts as on the ground
PX = PK.PX
NEAR, FAR = "blue", "red"        # its right leg (Mount_R_, the blue line) is nearer the camera in every run frame
FAR_COLOURS = ("the thigh and shin all #883713 with #66250A in the shade, the ankle band #5F1868 with #3D0942, the claws "
               "unchanged")
FAR_COLOURS_ZH = "大腿和小腿全用 `#883713`、暗面 `#66250A`，脚踝绑带用 `#5F1868`、暗面 `#3D0942`，黑爪不变"
# how each frame's legs read (its TFT sprint, 0_run_cycle.png)
LOOK = {
    "run1": ("蓝腿（近侧）**在空中往前伸**、快要落地，红腿（远侧、暗）在后面踩地往后蹬",
             "the near (BLUE) leg swinging forward in the air, reaching ahead, about to land; the far (RED, darker) foot "
             "planted behind, pushing off"),
    "run2": ("蓝腿（近侧）**在前面踩地**（近侧这一步迈得最开），红腿在后面脚跟抬起、刚要离地",
             "the near (BLUE) foot planted ahead - the near leg's widest stride; the far (RED) foot behind, its heel up, "
             "just leaving the ground"),
    "run3": ("**换腿的一帧**：蓝腿踩在身体正下方，红腿（远侧、暗）抬起来、膝盖往前，红脚从蓝腿**后面**经过，两只脚尖上下对齐",
             "THE PASSING: the near (BLUE) foot planted right under the body; the far (RED, darker) leg lifted, knee "
             "forward, its foot passing BEHIND the blue leg - the two toes one above the other, the blue leg drawn over it"),
    "run4": ("**红腿（远侧、暗）在前**：红腿在空中往前伸，蓝腿踩在身体后下方往后蹬",
             "the far (RED, darker) leg now FORWARD, swinging ahead in the air; the near (BLUE) foot planted under the "
             "back of the body, pushing back"),
    "run5": ("红腿在空中伸得更远，蓝腿在后面蹬地、脚跟抬起",
             "the far (RED) leg reaching further ahead in the air; the near (BLUE) foot pushing off behind, its heel up"),
    "run6": ("红腿**在最前面落地**（远侧这一步迈得最开，两只脚分得最开），蓝腿在后面刚离地",
             "the far (RED) foot landing far ahead - the widest split of the cycle; the near (BLUE) foot just leaving the "
             "ground behind"),
    "run7": ("红腿踩在前面、往身体下方收，蓝腿（近侧）在后面抬起、膝盖往前摆",
             "the far (RED) foot planted ahead, sliding back under the chest; the near (BLUE) leg lifted behind, its knee "
             "swinging forward"),
    "run8": ("**换腿的一帧**：红腿踩在身体正下方，蓝腿（近侧）抬着从红腿**前面**往前迈，两只脚尖上下对齐，蓝腿盖在上面",
             "THE PASSING: the far (RED) foot planted under the body; the near (BLUE) leg lifted, passing IN FRONT of it, "
             "the two toes one above the other, the blue leg drawn over the red"),
}


def foot(jxy, names, side):
    """(heel square, toe square) of one leg: its Foot and Toe joints on the grid (x, y in squares)."""
    f, t = jxy[names[f"Mount_{side}_Foot"]], jxy[names[f"Mount_{side}_Toe"]]
    return [int(f[0] // PX), int(f[1] // PX)], [int(t[0] // PX), int(t[1] // PX)]


def gap(f):
    """The near toe ahead of the far one (squares; negative = the far toe ahead)."""
    return f[NEAR]["toe"][0] - f[FAR]["toe"][0]


def up(f, colour):
    """A foot's height over the lower of the two (squares)."""
    return round(f[colour]["lift"] - min(f["red"]["lift"], f["blue"]["lift"]))


def prompts(feet):
    C, S = PK.CANVAS, PK.SOLE_Y
    zh = {"red": "红腿", "blue": "蓝腿"}
    rows = []
    for k, (name, t) in enumerate(RUN):
        f = feet[name]
        cells = []
        for colour in (NEAR, FAR):
            b = f[colour]
            u = up(f, colour)
            where = "**踩在地上**" if u <= LIFTED else f"**抬起来**（比另一只高约 {u} 格）"
            cells.append(f"脚尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        g = gap(f)
        lead = ("**两只脚尖上下对齐（换腿）**" if abs(g) <= 2 else
                f"**{zh[NEAR]}（近侧）在前** {g} 格" if g > 0 else f"**{zh[FAR]}（远侧、暗）在前** {-g} 格")
        rows.append(f"| {k + 1} | `zippy-run-{name}.png` | run@{t} | {cells[0]} | {cells[1]} | {lead} | {LOOK[name][0]} |")
    near_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) > 2)
    far_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) < -2)
    passing = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if abs(gap(feet[n])) <= 2)

    def line(k, name):
        f = feet[name]
        parts = [f"the {c.upper()} leg's foot {'ON THE GROUND' if up(f, c) <= LIFTED else 'LIFTED'}, its toe at square "
                 f"({f[c]['toe'][0]}, {f[c]['toe'][1]})" for c in (NEAR, FAR)]
        g = gap(f)
        lead = "" if abs(g) <= 2 else f", the {(NEAR if g > 0 else FAR).upper()} one ahead"
        return (f"- {name}: `RUN {k + 1} of 8 - {LOOK[name][1]}. " + ", ".join(parts)
                + f"; the two toes {abs(g)} square{'' if abs(g) == 1 else 's'} apart{lead}.`")
    lines = "\n".join(line(k, name) for k, (name, _t) in enumerate(RUN))
    return f"""# 呲呲：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「感觉走路换腿有点问题」**。上一版（`0_old_run_wrong.png`）的毛病：① **八帧都是两条腿一前一后分开**，没有一帧两条腿交错经过（换腿）；② **亮的近侧那条腿七帧都在前面**，远侧那条腿也没有明显变暗——看起来像同一条腿一直在前，两条腿从不交换。
> - 金铲铲里它是这样跑的（`0_run_cycle.png`，这 8 帧是**一个完整的循环**，迈两步）：身子前倾、尾巴往后伸直，**两条腿轮流往前迈**——第 {near_lead} 帧近侧那条腿在前，第 {far_lead} 帧远侧那条腿在前，第 {passing} 帧两条腿交错经过（**换腿**）。
> - 请你画 **{N} 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（它金铲铲模型自己的跑步动画那一帧，和画布、格子、位置都对好了）。
> - 格子每格 **{PX} px**，画布 **{C} × {C}**，红线是地面（**最低点 y = {S}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。**请严格用每格 {PX} px**。
> - **样子、颜色、画法全照定稿** `0_design.png`；**上半身（头、玫红长羽毛、紫色围兜、马鞍、身子、尾巴）的大小和画法照上一版的跑步**（`0_old_run_wrong.png`：用户没有意见的就是上半身），**八帧的上半身一样大**、跟着步子上下起伏 0–2 格；要改的只是两条腿。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体移动，不要转头。

## 最要紧的：两条腿看得出谁在前

骨架里 **蓝线 = 近侧的腿**（它的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（橙褐色大腿带亮面 `#EF7528` / `#B44E1C`、紫色脚踝绑带带高光 `#992CA8`、深褐色脚、三根黑色大弯爪），**永远画在另一条腿上面**（两条腿在胯下或交错时重叠的地方，它盖住远侧那条腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：{FAR_COLOURS_ZH}；**永远在近侧那条腿后面**。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 {near_lead} 帧**亮的蓝腿在前**，第 {far_lead} 帧**暗的红腿在前**，第 {passing} 帧两只脚几乎上下对齐（换腿的那一刻：一只脚踩在身体正下方，另一只抬起来从旁边经过）。

**每一帧画完，数格子核对两只脚**：脚尖（爪子最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只脚尖之间的距离和谁在前照表**（上一版的毛病就是谁在前不对、从没有交错）。没有哪只脚是一直在前的：两只脚轮流踩地、轮流抬起、轮流在前。

| 帧 | 文件 | 片段 | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）、`0_old_run_wrong.png`（上半身照它，腿不要照它）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {C}x{C} canvas with {PX} px squares (its soles on y {S}) - a small BIPEDAL RAPTOR: a ROUND ORANGE-BROWN HEAD with HOT-PINK SPIKES on top, a frill of BLACK SHARDS round the face, BIG HALF-CLOSED PURPLE EYES; one DEEP PURPLE BIB down the front of the neck; LONG HOT-PINK FEATHER LOCKS at both sides of the neck; a MAGENTA SADDLE with gold trim and a gold ring; orange-brown body and thighs, PURPLE ANKLE BANDS, three-toed BLACK CLAWS; an orange-brown tail with PINK SPINES. Image A stands - copy only its look. B its HEAD shown 8x. C a 3D RENDER of this same creature's own game model in THIS FRAME OF ITS RUN, on the same {C} canvas and grid, already scaled and placed where the picture must be (copy the pose of the legs, never its 3D shading). D the SKELETON of that frame, exactly over C: green = the spine, the BLUE line = its NEAR leg, the RED line = its FAR leg, BROWN = the tail, PINK and CYAN = the feather locks, GREY BOX = where the head goes, the red horizontal line = the ground. E its whole run cycle, 8 frames in a row. F its OLD run: copy its UPPER BODY - the head, the feathers, the bib, the saddle, the body and the tail, their size and drawing; NOT its legs (crossed out: wrong).
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY {PX} px, aligned on one straight grid from the canvas corner; its lowest point on y {S}.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (the orange-brown thigh with its light orange, the purple ankle band with its light purple, the dark brown foot, the black claws), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design ({FAR_COLOURS}), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the two PASSING frames the toes are one above the other: one foot planted under the body, the other lifted beside it. Each foot exactly where D puts it; one foot on the ground, the other lifted unless the line says both are down.
COUNT THE SQUARES: the same body size in every frame and the same as image F's upper body; the feet as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned. Nothing covers the face.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

{lines}

## 交回

- 每帧一张：`outputs/zippy-run/zippy-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/zippy-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**两帧换腿是不是真的交错**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **{N} 帧都画完再交**，最后写 `outputs/zippy-run/HANDOFF.md`，再打包成 `outputs/zippy_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/zippy/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的脸（design_zippy_poses.py 的读法），逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身大小八帧一致（必要时一个上半身用到八帧，design_sevika_run.py 的做法）。
- 每帧在游戏里的时长（ms，按片段的间隔分 {LOOP_MS} ms 一个循环）：{MS}。
- 这份提示词和参考图由 `tools/art/pack_zippy_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\zippy_packs\zippy_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    poser = PK.Poser(a.lol)
    names = poser.names
    hv = PK.head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    C, SOLE_Y = PK.CANVAS, PK.SOLE_Y

    # the pose pack's scale and the design's place (pack_zippy_poses.main)
    iv, ij = poser.pose(PK.DESIGN)
    pxy, _ = PK.Poser.project(iv, PK.YAW, 1.0, 0.0, 0.0)
    scale = PK.ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = names["Mount_Root"]
    dx = (C - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - PK.ROWS * PX
    ix = PK.Poser.project(iv, PK.YAW, scale, 0.0, 0.0)[0][:, 0]
    jx = PK.Poser.project(ij, PK.YAW, scale, 0.0, 0.0)[0][pel, 0]
    x0, _, x1, _ = design.getbbox()
    col = x0 + (jx - ix.min()) / (ix.max() - ix.min()) * (x1 - x0)
    pelvis_x = dx + round(col * PX)
    can = Image.new("RGBA", (C, C), PK.GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, PK.ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(PK.HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, PK.GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "0_head.png")))
    # the design pose's skeleton over the design (as the pose pack draws it)
    ixy, _ = PK.Poser.project(iv, PK.YAW, scale, 0.0, 0.0)
    jxy0, jz0 = PK.Poser.project(ij, PK.YAW, scale, 0.0, 0.0)
    ground0 = SOLE_Y - ixy[:, 1].max()
    shift0 = pelvis_x - jxy0[pel, 0]
    jxy0[:, 0] += shift0
    jxy0[:, 1] += ground0
    PK.skeleton(poser, jxy0, jz0, (0, 0, 0, 0), os.path.join(a.out, "0_design_skeleton.png"), can)
    feet, refs, box = {}, [], [C, C, 0, 0]
    for k, (name, t) in enumerate(RUN):
        clip = f"run@{t}"
        verts, joints = poser.pose(clip)
        xy, _ = PK.Poser.project(verts, PK.YAW, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = PK.Poser.project(joints, PK.YAW, scale, 0.0, 0.0)
        # the near leg: the hip nearer the camera (the larger depth) - its right one in every frame of the run
        if not jz[names["Mount_R_Hip"]] > jz[names["Mount_L_Hip"]]:
            sys.exit(f"{name}: the near leg is not its right one: NEAR / FAR and the prompt's colours are wrong")
        shift = pelvis_x - jxy[pel, 0]
        xy[:, 0] += shift
        xy[:, 1] += ground
        box = [min(box[0], xy[:, 0].min()), min(box[1], xy[:, 1].min()), max(box[2], xy[:, 0].max()),
               max(box[3], xy[:, 1].max())]
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        stem = f"{k + 1}_{name}"
        PK.skeleton(poser, jxy, jz, (hx.min(), hy.min(), hx.max(), hy.max()), os.path.join(a.out, f"{stem}_skeleton.png"))
        im = pose_ref.render_hq(verts, poser.tris, poser.m.v["uv"], poser.m.tex, -PK.YAW, PK.PITCH, (C, C), scale,
                                ground, shift=-shift / C - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (C, C), PK.GREY + (255,))
        PK.grid(ImageDraw.Draw(ref))
        ref.alpha_composite(im)
        ref = ref.convert("RGB")
        ref.save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        refs.append(ref)
        # each foot: heel and toe squares, its lowest point on the ground or lifted (squares above the ground line)
        f = {"ms": MS[k]}
        for side, colour in (("L", "red"), ("R", "blue")):
            heel, toe = foot(jxy, names, side)
            low = max(jxy[names[f"Mount_{side}_Foot"], 1], jxy[names[f"Mount_{side}_Toe"], 1])
            f[colour] = {"heel": heel, "toe": toe, "lift": round(float((SOLE_Y - low) / PX), 1)}
        f["lead"] = "pass" if abs(gap(f)) <= 2 else ("blue" if gap(f) > 0 else "red")
        f["near_leg"], f["clip"] = NEAR, clip
        feet[name] = f
        print(stem, clip, "gap", gap(f), "lead", f["lead"], "lift blue", f["blue"]["lift"], "red", f["red"]["lift"])

    # the whole cycle at a glance: each ref cropped round the figures' joint box, in a row
    band = (int(box[0]) - 30, int(box[1]) - 30, int(box[2]) + 30, SOLE_Y + 20)
    w, h = band[2] - band[0], band[3] - band[1]
    strip = Image.new("RGB", (N * w // 2 + (N - 1) * 6, h // 2 + 40), (255, 255, 255))
    d = ImageDraw.Draw(strip)
    for k, r in enumerate(refs):
        strip.paste(r.crop(band).resize((w // 2, h // 2), Image.LANCZOS), (k * (w // 2 + 6), 40))
        g = gap(feet[RUN[k][0]])
        lab = "PASS" if abs(g) <= 2 else ("near (blue) ahead" if g > 0 else "far (red) ahead")
        d.text((k * (w // 2 + 6) + 8, 10), f"run{k + 1}  {lab}", fill=(0, 0, 0))
    strip.save(lp(os.path.join(a.out, "0_run_cycle.png")))

    # the first run, what not to draw (its legs; its upper body is the one to keep)
    old = [Image.open(lp(os.path.join(OLD, f"zippy-pose-run{k}.png"))).convert("RGBA") for k in range(1, 9)]
    cut = [o.crop(o.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()) for o in old]
    hh = max(c.height for c in cut)
    sheet = Image.new("RGBA", (sum(c.width for c in cut) + 30 * 9, hh + 90), (255, 255, 255, 255))
    x = 30
    for c in cut:
        sheet.alpha_composite(c, (x, 90 + hh - c.height))
        x += c.width + 30
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
    d.text((30, 4), "OLD RUN: keep the UPPER BODY (head, feathers, bib, saddle, body, tail) - its size and drawing.",
           fill=(0, 120, 0), font=font)
    d.text((30, 44), "WRONG LEGS: never crossing, the near (light) leg ahead in 7 of 8, the far leg not darker - do not copy.",
           fill=(200, 0, 0), font=font)
    leg_top = 90 + hh - round(hh * 0.45)
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
