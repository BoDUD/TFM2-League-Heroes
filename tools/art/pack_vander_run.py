#!/usr/bin/env python3
"""Vander's run pack for Codex (assets/source/vander/RUN_PROMPTS.md): his TFT run redrawn as 8 frames, after the user's
review of the first run (2026-10-27: 「跑步姿势不像啊」 - the Titan / Braum walk on the design kept his crouched
fighting stance; Codex's run1-4 were hunched and kept the front boot planted in all four).

    python tools/art/pack_vander_run.py [--out C:/t/vd_work/vander_run_pack] [--lol "D:/Riot Games/League of Legends"]

The same canvas, grid, scale and placing as the pose pack (pack_vander_poses: the design pose's height = the design's
80 rows at PX px a square, the lowest point on SOLE_Y, the pelvis on the design pose's pelvis column), his run clip at
eight even times (RUN). Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png;
per frame <k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row: the whole cycle at a glance);
0_old_run_wrong.png (the first run, what not to draw); feet.json (each frame's boots: heel and toe squares, on the
ground or not - the table in RUN_PROMPTS.md, and what the delivery is checked against).
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
import pack_vander_poses as PK  # noqa: E402
from design_vander_hd import lp  # noqa: E402

SRC = PK.SRC
CYCLE = 1066                     # his run clip's length in ms
N = 8
RUN = [(f"run{k + 1}", f"run@{round(CYCLE * k / N)}") for k in range(N)]
LIFTED = 3                       # a boot this many squares over the lower one's joints still counts as on the ground
PX = 9                           # squares of 9 px, not the pose pack's 12: upright he is ~1.45x the crouched design's
                                 # 80 rows (~117), which at 12 or 10 px runs off the top of the canvas


def boot(jxy, names, side):
    """(heel square, toe square) of one leg: its Foot and Toe joints on the grid (x, y in squares)."""
    f, t = jxy[names[f"{side}_Foot"]], jxy[names[f"{side}_Toe"]]
    return [int(f[0] // PK.PX), int(f[1] // PK.PX)], [int(t[0] // PK.PX), int(t[1] // PK.PX)]


def prompts(feet):
    """RUN_PROMPTS.md: the brief, the frame table with each boot's squares, the prompt."""
    C, S = PK.CANVAS, PK.SOLE_Y
    rows = []
    for k, (name, clip) in enumerate(RUN):
        f = feet[name]
        cells = []
        for colour, zh in (("red", "红腿"), ("blue", "蓝腿")):
            b = f[colour]
            up = round(b["lift"] - min(f["red"]["lift"], f["blue"]["lift"]))
            where = "**踩在地上**" if up <= LIFTED else f"**抬起来**（比另一只高约 {up} 格）"
            cells.append(f"{zh}靴尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        near = "红腿" if f["near_leg"] == "red" else "蓝腿"
        arm = "青（绷带拳）" if f["near_arm"].startswith("CYAN") else "橙（拳套）"
        rows.append(f"| {k + 1} | `vander-run-{name}.png` | {clip} | {f['rows']} | {cells[0]} | {cells[1]} | {near} | {arm} |")
    return f"""# 范德尔：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「跑步姿势不像啊」**：不像他在金铲铲里的跑法。上一版（`0_old_run_wrong.png`）**弓着背缩着身子，像格斗架势**，而且**前面那只靴子四帧都钉在地上不动**，看起来是在滑。
> - 金铲铲里他是这样跑的（`0_run_cycle.png`，8 帧一个完整循环）：**身子直起来、微微前倾地小跑**，拳套举在胸口 / 肩前（画面左边），缠绷带的拳头在身前（画面右边），**两条腿一前一后轮流迈大步，后面那只脚抬起来往后踢，脚跟离地很高**。
> - 请你画 **{N} 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（他金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - **这一包的格子是每格 {PX} px**（不是上一包的 12 px：直起身子跑他比蹲着的定稿高很多，12 px 放不下）。画布 **{C} × {C}**，红线是地面（**脚底 y = {S}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。
> - **样子、颜色、画法全照定稿** `0_design.png`：往后梳的深色头发、粗黑浓眉、短络腮胡；焦橙色皮夹克、米白竖条纹马甲、青绿领口、暗红腰带黄铜扣、深藏青牛仔裤、黑工装靴；**画面左边那只手戴着铁拳套**（黄铜八角框、两块红面板、金色六角螺栓，接紫色护臂），另一只手是缠灰白绷带的拳头。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。
> - **身高照参考图**：他直着身子跑，**下表「高」那一列是每帧从头顶到脚底的格数**（约 {min(feet[n]['rows'] for n, _ in RUN)}–{max(feet[n]['rows'] for n, _ in RUN)} 格），**不要缩成定稿那样的蹲姿**（定稿只有 80 格高）。头（含头发）约 26 × 22 格、拳套约 12 × 12 格、靴子和定稿一样大——这些和定稿一样，变高的是**腿伸直了、背直起来了**。

## 最要紧的：两只靴子

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以）。骨架里**红线 = 一条腿，蓝线 = 另一条腿**，「前面的腿」是离镜头近、要画在另一条腿上面的那条（颜色亮一档），后面那条暗一档。

- 第 1–3 帧：**蓝腿踩地**撑着身体往后蹬，**红腿抬起来**从后面往前收；
- 第 4 帧：红腿往前落地，蓝腿在后面脚尖点地；
- 第 5–7 帧：**红腿踩地**，**蓝腿抬起来**从后面往前收；
- 第 8 帧：两腿交错，回到第 1 帧。
- **没有哪只靴子是一直不动的**：两只靴子轮流踩地、轮流抬起，每帧都照下表的格子换位置。

| 帧 | 文件 | 片段 | 高（格） | 红腿 | 蓝腿 | 前面的腿 | 前面的手臂 |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {C}x{C} canvas with {PX} px squares (his soles on y {S}) - a big, burly middle-aged BRAWLER: swept-back dark hair, thick black brows, a short grey-brown beard; a burnt-orange leather jacket, a cream striped waistcoat, a teal collar, a dark red belt with brass buckles, dark navy jeans, black work boots; on the image-left hand a big IRON GAUNTLET (an octagonal brass frame, two red panels, gold hexagonal bolts) joined to a purple bracer, the other hand a fist wrapped in grey-white bandages. Image A is crouched in a fighting stance - DO NOT copy that crouch, copy only his look. B his HEAD shown 8x (about 26 squares wide, 22 tall). C a 3D RENDER of this same character's own game model in THIS FRAME OF HIS RUN, on the same {C} canvas and grid, already scaled and placed where the picture must be. D the SKELETON of that frame, exactly over C: green = the spine, ORANGE = the GAUNTLET arm, CYAN = the BANDAGED arm (the big dot = the hand), RED and BLUE = his two legs, GOLD ring = the gauntlet, GREY BOX = where the head goes, the red line = the ground. E his whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square exactly {PX} px, aligned on one straight grid from the canvas corner; his lowest point on y {S}.
HE IS RUNNING UPRIGHT: the back straight and leaning slightly forward, the legs long and striding, as tall as C (not crouched, not hunched). Copy C's pose exactly: where the hips are, where each knee and each boot is, which boot is on the ground and which is lifted high behind him, where the gauntlet and the bandaged fist are.
THE BOOTS: the RED leg's boot and the BLUE leg's boot exactly where C and D put them (the frame's line below gives each toe's square). One boot on the ground, the other lifted off it unless the line says both are down. The nearer leg in full tone drawn over the other, the far leg a step darker.
COUNT THE SQUARES: the head with the hair about 26 x 22, the gauntlet about 12 x 12, each arm about 16 squares from the shoulder to the fist, the boots as big as in A; a broad, strong body. The gauntlet always on the ORANGE arm's hand; the CYAN arm's hand always the bandaged fist.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. No fist or gauntlet covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

""" + "\n".join(
        f"- {name}: `RUN {k + 1} of 8 - "
        + ", ".join(
            f"the {c.upper()} leg's boot {'ON THE GROUND' if round(feet[name][c]['lift'] - min(feet[name]['red']['lift'], feet[name]['blue']['lift'])) <= LIFTED else 'LIFTED high behind him'}, its toe at square ({feet[name][c]['toe'][0]}, {feet[name][c]['toe'][1]})"
            for c in ("red", "blue"))
        + f"; the {feet[name]['near_leg'].upper()} leg nearer; about {feet[name]['rows']} squares tall.`"
        for k, (name, _c) in enumerate(RUN)) + f"""

## 交回

- 每帧一张：`outputs/vander-run/vander-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/vander-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对两只靴子的格子**（上表），不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格。
- **{N} 帧都画完再交**，最后写 `outputs/vander-run/HANDOFF.md`，再打包成 `outputs/vander_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/vander/codex_run/`，按 {PX} px 的格子读回、换成定稿的颜色、贴定稿的头（design_vander_poses.py），逐帧对 `feet.json` 量两只靴尖，连起来播放看有没有滑步。
- 这份提示词和参考图由 `tools/art/pack_vander_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\vd_work\vander_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    PK.PX = PX                   # pack_vander_poses' grid and skeleton drawing use its PX
    poser = PK.Poser(a.lol)
    hv = PK.head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    rows = PK.ROWS
    C, SOLE_Y = PK.CANVAS, PK.SOLE_Y

    # the pose pack's scale and the design's place (pack_vander_poses.main)
    iv, ij = poser.pose(PK.DESIGN)
    (pxy, _) = PK.Poser.project(iv, PK.YAW, 1.0, 0.0, 0.0)
    scale = rows * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Pelvis"]
    dx = (C - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - rows * PX
    ixy, _ = PK.Poser.project(iv, PK.YAW, scale, 0.0, 0.0)
    pelvis_x = dx + (ixy[pel, 0] - ixy[:, 0].min()) / (ixy[:, 0].max() - ixy[:, 0].min()) * design.width * PX
    can = Image.new("RGBA", (C, C), PK.GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, rows * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(PK.HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, PK.GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "0_head.png")))
    jxy0, jz0 = PK.Poser.project(ij, PK.YAW, scale, 0.0, 0.0)
    ground0 = SOLE_Y - ixy[:, 1].max()
    jxy0[:, 0] += pelvis_x - jxy0[pel, 0]
    jxy0[:, 1] += ground0
    PK.skeleton(poser, ij, jxy0, jz0, (0, 0, 0, 0), os.path.join(a.out, "0_design_skeleton.png"), can)

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
        zl = np.mean([jz[poser.names[n]] for n in PK.CHAINS["L_leg"]])
        zr = np.mean([jz[poser.names[n]] for n in PK.CHAINS["R_leg"]])
        f["near_leg"] = "red" if zl > zr else "blue"
        f["near_arm"] = PK.near_arm(jz, poser)
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
        d.text((k * (w // 2 + 6) + 8, 10), f"run{k + 1}", fill=(0, 0, 0))
    strip.save(lp(os.path.join(a.out, "0_run_cycle.png")))

    # the first run, what not to draw
    old = [Image.open(lp(os.path.join(SRC, "codex_poses", "vander-poses", f"vander-pose-run{k}.png"))).convert("RGBA")
           for k in range(1, 5)]
    cut = [o.crop(o.getbbox()) for o in old]
    hh = max(c.height for c in cut)
    sheet = Image.new("RGBA", (sum(c.width for c in cut) + 30 * 5, hh + 80), (255, 255, 255, 255))
    x = 30
    for c in cut:
        sheet.alpha_composite(c, (x, 80 + hh - c.height))
        x += c.width + 30
    d = ImageDraw.Draw(sheet)
    d.text((30, 20), "WRONG (the first run): hunched like the fighting stance, the front boot never leaves the ground",
           fill=(200, 0, 0))
    d.line([(0, 0), (sheet.width, sheet.height)], fill=(220, 0, 0), width=8)
    d.line([(0, sheet.height), (sheet.width, 0)], fill=(220, 0, 0), width=8)
    sheet.convert("RGB").resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(
        lp(os.path.join(a.out, "0_old_run_wrong.png")))

    with open(lp(os.path.join(a.out, "feet.json")), "w", encoding="utf-8") as fp:
        json.dump(feet, fp, indent=1)
    text = prompts(feet)
    for path in (os.path.join(SRC, "RUN_PROMPTS.md"), os.path.join(a.out, "RUN_PROMPTS.md")):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as fp:
            fp.write(text)
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
