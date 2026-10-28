#!/usr/bin/env python3
"""Violet's run pack for Codex (assets/source/violet/RUN_PROMPTS.md): her TFT run redrawn as 8 frames, after the user's
review of the first run (2026-10-28: 「走路腿没有前后交换啊 codex做错你也做错」 - Codex's run1-4 drew every frame's leading
leg the same way, the near one in full tone over the other, so the legs never seemed to swap; recolouring the far leg
did not do; the user: 「你让codex重画吧」). Vander's way (pack_vander_run.py).

    python tools/art/pack_violet_run.py [--out C:/t/vo_work/violet_run_pack] [--lol "D:/Riot Games/League of Legends"]

The same canvas, grid, scale and placing as the pose pack (pack_violet_poses: the design pose's height = the design's
76 rows at PX px a square, the lowest point on SOLE_Y, the pelvis on the design's PELVIS_COL), her run clip at eight
even times (RUN). Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png; per
frame <k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row: the whole cycle at a glance);
0_old_run_wrong.png (the first run, what not to draw); feet.json (each frame's boots: heel and toe squares, on the
ground or not, which leg leads - the table in RUN_PROMPTS.md, and what the delivery is checked against).
The NEAR leg (the one nearer the camera in the design pose, the navy thigh patch) is the same leg in every frame: drawn
in full tone and over the other where they cross; the far leg a step darker, behind. Which leg LEADS (its boot further
forward) changes every half cycle - that is the swap the first run lacked.
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
import pack_violet_poses as PK  # noqa: E402
from design_violet_hd import lp  # noqa: E402

SRC = PK.SRC
CYCLE = 933                      # her run clip's length in ms
N = 8
RUN = [(f"run{k + 1}", f"run@{round(CYCLE * k / N)}") for k in range(N)]
LIFTED = 3                       # a boot this many squares over the lower one still counts as on the ground
PX = PK.PX                       # 12 px squares, the pose pack's: upright she is about as tall as the crouched design


def boot(jxy, names, side):
    """(heel square, toe square) of one leg: its Foot and Toe joints on the grid (x, y in squares)."""
    f, t = jxy[names[f"{side}_Foot"]], jxy[names[f"{side}_Toe"]]
    return [int(f[0] // PX), int(f[1] // PX)], [int(t[0] // PX), int(t[1] // PX)]


def prompts(feet, near):
    """RUN_PROMPTS.md: the brief, the frame table with each boot's squares, the prompt."""
    C, S = PK.CANVAS, PK.SOLE_Y
    far = "blue" if near == "red" else "red"
    zh = {"red": "红腿", "blue": "蓝腿"}
    rows = []
    for k, (name, clip) in enumerate(RUN):
        f = feet[name]
        cells = []
        for colour in ("red", "blue"):
            b = f[colour]
            up = round(b["lift"] - min(f["red"]["lift"], f["blue"]["lift"]))
            where = "**踩在地上**" if up <= LIFTED else f"**抬起来**（比另一只高约 {up} 格）"
            cells.append(f"靴尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        lead = zh[f["lead"]] + ("（近侧，藏青大腿）" if f["lead"] == near else "（远侧，暗一档）")
        rows.append(f"| {k + 1} | `violet-run-{name}.png` | {clip} | {f['rows']} | {cells[0]} | {cells[1]} | {lead} |")
    halves = {}
    for k, (name, _c) in enumerate(RUN):
        halves.setdefault(feet[name]["lead"], []).append(k + 1)
    lead_near = "、".join(str(k) for k in halves.get(near, []))
    lead_far = "、".join(str(k) for k in halves.get(far, []))
    return f"""# 蔚奥莱：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「走路腿没有前后交换啊」**。上一版（`0_old_run_wrong.png`）**四帧在前面的那条腿都画成同一个样子**：都是近侧那条（颜色亮、画在另一条腿上面、大腿有藏青补丁），所以看起来永远是同一条腿在前，两条腿从来没有交换过。
> - 金铲铲里她是这样跑的（`0_run_cycle.png`，8 帧一个完整循环）：双拳套举在胸前小跑，**两条腿一前一后轮流迈步**：前半个循环一条腿在前，后半个循环换另一条腿在前。
> - 请你画 **{N} 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **{PX} px**，画布 **{C} × {C}**，红线是地面（**脚底 y = {S}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。**请严格用每格 {PX} px**（上一版实际画成了 9–11 px，大小每帧都不一样）。
> - **样子、颜色、画法全照定稿** `0_design.png`：洋红色斜垂的头发、上挑的眉毛、浅蓝眼睛；酒红短马甲、红兜帽、浅灰绿衬衫和胸前绷带、深棕腰带、深紫褐宽裤、橄榄绿绑腿、深棕短靴；**两只手都戴着大铁拳套**（蓝灰钢板、金黄方框拳头），跑步时举在胸前。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。
> - **大小照参考图**：下表「高」那一列是每帧从头顶到脚底的格数；头（含头发）约 28 × 27 格、每只拳套连前臂约 20 × 18 格、靴子和定稿一样大。**八帧的身体大小要一样**。

## 最要紧的：两条腿轮流在前

骨架里 **{zh[near]} = 近侧的腿**（离镜头近），**{zh[far]} = 远侧的腿**。这两条腿的画法**每一帧都固定**：

- **{zh[near]}（近侧）**：**大腿上是深藏青色的补丁**（和定稿画面右边那条腿一样），绑腿亮一档，**永远画在另一条腿上面**（两条腿在胯下交叉、重叠的地方，它盖住远侧的腿）。
- **{zh[far]}（远侧）**：**整条腿暗一档**（深紫褐色，没有藏青补丁），绑腿也暗一档，**永远在近侧那条腿后面**。

**哪条腿在前（靴子更靠画面右边）每半个循环换一次**：

- 第 {lead_near} 帧：**{zh[near]}（近侧、藏青大腿）在前**，远侧的暗腿在后面；
- 第 {lead_far} 帧：**{zh[far]}（远侧、暗腿）在前**，近侧的藏青大腿那条在后面——**这几帧在前面的是暗的那条腿，藏青补丁那条在后面，但胯下重叠的地方仍然是藏青那条盖在上面**。上一版就是这几帧画错了。

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以）。**没有哪只靴子是一直不动的**：两只靴子轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 红腿 | 蓝腿 | 在前的腿 |
|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {C}x{C} canvas with {PX} px squares (her soles on y {S}) - a lean TEENAGE GIRL street fighter: magenta-pink hair swooping over the far side of her face, dark brown brows tilted up, pale blue eyes; a short wine-red vest with a red hood behind the neck, a pale grey-green shirt with chest wraps, a dark brown belt, baggy dark purple-brown trousers, a DARK NAVY PATCH on the NEAR thigh, olive leg wraps, dark brown boots; a HUGE IRON GAUNTLET on EACH hand (blue-grey steel plates, a square gold-yellow fist frame). Image A stands in a fighting stance - copy only her look. B her HEAD shown 8x (about 28 squares wide, 27 tall). C a 3D RENDER of this same character's own game model in THIS FRAME OF HER RUN, on the same {C} canvas and grid, already scaled and placed where the picture must be (copy the pose, never its 3D shading or its small gauntlets). D the SKELETON of that frame, exactly over C: green = the spine, ORANGE and CYAN = the arms (the big dots = the hands, the GOLD rings = the gauntlets), the {near.upper()} line = her NEAR leg, the {far.upper()} line = her FAR leg, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY {PX} px, aligned on one straight grid from the canvas corner; her lowest point on y {S}.
THE LEGS: the NEAR leg ({near.upper()} line) always has the dark NAVY thigh patch, light olive wraps, full tone, and is drawn OVER the far leg where they cross at the hips. The FAR leg ({far.upper()} line) is a step darker all over (dark purple-brown, no navy, dark wraps) and always BEHIND the near one. Which leg is FORWARD changes: follow C and D - in this frame the {{LEAD}} leg is the forward one. Each boot exactly where C and D put it (the frame's line below gives each toe's square); one boot on the ground, the other lifted unless the line says both are down.
COUNT THE SQUARES: the head with the hair about 28 x 27, each gauntlet with its forearm about 20 x 18, the boots as big as in A, the same body size in every frame. Both gauntlets up at her chest as in C.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. No gauntlet covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文，`{{LEAD}}` 换成这一行写的那条腿）：

""" + "\n".join(
        f"- {name}: `RUN {k + 1} of 8 - the {feet[name]['lead'].upper()} leg "
        + ("(the NEAR one, navy thigh)" if feet[name]["lead"] == near else "(the FAR, darker one - the navy-thigh near leg is BEHIND it but still drawn over it at the hips)")
        + " is FORWARD; "
        + ", ".join(
            f"the {c.upper()} leg's boot {'ON THE GROUND' if round(feet[name][c]['lift'] - min(feet[name]['red']['lift'], feet[name]['blue']['lift'])) <= LIFTED else 'LIFTED'}, its toe at square ({feet[name][c]['toe'][0]}, {feet[name][c]['toe'][1]})"
            for c in ("red", "blue"))
        + f"; about {feet[name]['rows']} squares tall.`"
        for k, (name, _c) in enumerate(RUN)) + f"""

## 交回

- 每帧一张：`outputs/violet-run/violet-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/violet-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只靴尖的格子（上表）、**哪条腿在前**、**藏青补丁在近侧那条腿上并且画在上面**，不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格、哪条腿在前。
- **{N} 帧都画完再交**，最后写 `outputs/violet-run/HANDOFF.md`，再打包成 `outputs/violet_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/violet/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头（design_violet_poses.py），逐帧对 `feet.json` 量两只靴尖、看哪条腿在前，连起来播放看有没有滑步、两条腿有没有轮流在前。
- 这份提示词和参考图由 `tools/art/pack_violet_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\vo_work\violet_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    poser = PK.Poser(a.lol)
    hv = PK.head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    rows = PK.ROWS
    C, SOLE_Y = PK.CANVAS, PK.SOLE_Y

    # the pose pack's scale and the design's place (pack_violet_poses.main)
    iv, ij = poser.pose(PK.DESIGN)
    (pxy, _) = PK.Poser.project(iv, PK.YAW, 1.0, 0.0, 0.0)
    scale = rows * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Pelvis"]
    dx = (C - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - rows * PX
    pelvis_x = dx + PK.PELVIS_COL * PX + PX // 2
    can = Image.new("RGBA", (C, C), PK.GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, rows * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(PK.HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, PK.GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "0_head.png")))
    ixy, _ = PK.Poser.project(iv, PK.YAW, scale, 0.0, 0.0)
    jxy0, jz0 = PK.Poser.project(ij, PK.YAW, scale, 0.0, 0.0)
    ground0 = SOLE_Y - ixy[:, 1].max()
    jxy0[:, 0] += pelvis_x - jxy0[pel, 0]
    jxy0[:, 1] += ground0
    PK.skeleton(poser, ij, jxy0, jz0, (0, 0, 0, 0), os.path.join(a.out, "0_design_skeleton.png"), can)
    # the near leg: nearer the camera in the design pose (the navy patch) - the same leg in every frame
    zl0 = np.mean([jz0[poser.names[n]] for n in PK.CHAINS["L_leg"]])
    zr0 = np.mean([jz0[poser.names[n]] for n in PK.CHAINS["R_leg"]])
    near = "red" if zl0 > zr0 else "blue"

    feet, refs = {}, []
    for k, (name, clip) in enumerate(RUN):
        verts, joints = poser.pose(clip)
        xy, z = PK.Poser.project(verts, PK.YAW, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = PK.Poser.project(joints, PK.YAW, scale, 0.0, 0.0)
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
                    os.path.join(a.out, f"{stem}_skeleton.png"))
        im = pose_ref.render_hq(verts, poser.tris, poser.m.v["uv"], poser.m.tex, -PK.YAW, PK.PITCH, (C, C), scale,
                                ground, shift=-shift / C - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (C, C), PK.GREY + (255,))
        PK.grid(ImageDraw.Draw(ref))
        ref.alpha_composite(im)
        ref = ref.convert("RGB")
        ref.save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        refs.append(ref)
        # each boot: heel and toe squares, its lowest point on the ground or lifted (squares above the ground line)
        f = {"rows": int(SOLE_Y // PX) - top}
        for side, colour in (("L", "red"), ("R", "blue")):
            heel, toe = boot(jxy, poser.names, side)
            low = max(jxy[poser.names[f"{side}_Foot"], 1], jxy[poser.names[f"{side}_Toe"], 1])
            lift = (SOLE_Y - low) / PX
            f[colour] = {"heel": heel, "toe": toe, "lift": round(float(lift), 1)}
        # the leading leg: its foot further forward (image right)
        f["lead"] = "red" if jxy[poser.names["L_Foot"], 0] > jxy[poser.names["R_Foot"], 0] else "blue"
        f["near_leg"] = near
        f["clip"] = clip
        feet[name] = f
        print(stem, clip, f)

    # the whole cycle at a glance: each ref cropped round the figure's column band, in a row
    band = (C // 2 - 360, 60, C // 2 + 360, SOLE_Y + 20)
    w, h = band[2] - band[0], band[3] - band[1]
    strip = Image.new("RGB", (N * w // 2 + (N - 1) * 6, h // 2 + 40), (255, 255, 255))
    d = ImageDraw.Draw(strip)
    for k, r in enumerate(refs):
        strip.paste(r.crop(band).resize((w // 2, h // 2), Image.LANCZOS), (k * (w // 2 + 6), 40))
        d.text((k * (w // 2 + 6) + 8, 10), f"run{k + 1}  lead: {feet[RUN[k][0]]['lead']}", fill=(0, 0, 0))
    strip.save(lp(os.path.join(a.out, "0_run_cycle.png")))

    # the first run, what not to draw
    old = [Image.open(lp(os.path.join(SRC, "codex_poses", "violet-poses", f"violet-pose-run{k}.png"))).convert("RGBA")
           for k in range(1, 5)]
    cut = [o.crop(o.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()) for o in old]
    hh = max(c.height for c in cut)
    sheet = Image.new("RGBA", (sum(c.width for c in cut) + 30 * 5, hh + 80), (255, 255, 255, 255))
    x = 30
    for c in cut:
        sheet.alpha_composite(c, (x, 80 + hh - c.height))
        x += c.width + 30
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "WRONG (the first run): in all four the forward leg is drawn the same (the near one, bright, on top) - "
           "the legs never swap", fill=(200, 0, 0))
    d.line([(0, 0), (sheet.width, sheet.height)], fill=(220, 0, 0), width=8)
    d.line([(0, sheet.height), (sheet.width, 0)], fill=(220, 0, 0), width=8)
    sheet.convert("RGB").resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(
        lp(os.path.join(a.out, "0_old_run_wrong.png")))

    with open(lp(os.path.join(a.out, "feet.json")), "w", encoding="utf-8") as fp:
        json.dump(feet, fp, indent=1)
    text = prompts(feet, near)
    for path in (os.path.join(SRC, "RUN_PROMPTS.md"), os.path.join(a.out, "RUN_PROMPTS.md")):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as fp:
            fp.write(text)
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
