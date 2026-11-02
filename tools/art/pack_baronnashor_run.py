#!/usr/bin/env python3
"""Baron Nashor's run pack for Codex (assets/source/baronnashor/RUN_PROMPTS.md): its run redrawn as 8 frames over one
whole cycle in which the two legs LEAD IN TURN and pass twice (Sevika's and Zippy's way: pack_sevika_run.py,
pack_zippy_run.py).

    python tools/art/pack_baronnashor_run.py [--out D:/TFM2-Workshop/baronnashor_packs/baronnashor_run_pack] [--lol "D:/Riot Games/League of Legends"]

What was wrong with the first run (pack_baronnashor_poses run1-8, Codex's baronnashor-pose-run1..8): its legs were
T-Hex's run (the model has none of its own), and T-Hex's run never swaps leads at the pack's camera - its far toe stays
8-45 squares ahead of the near one for the whole 1.27 s cycle (measured 2026-11-03, every 40 ms) - so Codex drew one
foot ahead in every frame: the legs never pass (「换腿不明显」, Sevika's and Violet's complaint). My skeleton's fault, not
Codex's.
Here the legs are made to take turns (the Caitlyn way: one leg's phases, the other the same four frames on): BOTH legs
follow T-Hex's FAR (L) leg's own stride about its own hip - the far leg at the frame's time, the near leg half a cycle
later - and hang from hips HIP_GAP squares apart (T-Hex's hips spread 3/4 view would put the far foot ahead all the time
again). The upper body is Baron's idle at the same time, its root on the hips (pack_baronnashor_poses' placing, the same
canvas, grid and scale); the lowest toe on the ground, so the body rides up and down with the stride.
The NEAR leg (the BLUE line) is the same leg in every frame: the design's own leg colours, over the other where they
overlap; the FAR leg (the RED line) a step darker in the design's own darker colours (FAR_COLOURS), behind.
Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png; per frame
<k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row); 0_old_run_wrong.png (the first run:
keep its upper body, not its legs); feet.json (each frame's toes, lift and which leg leads - the table in RUN_PROMPTS.md,
and what the delivery is checked against).
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
import pack_baronnashor_picture as BP  # noqa: E402
import pack_baronnashor_poses as PK  # noqa: E402
import pack_thex_picture as TP  # noqa: E402
from design_baronnashor_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "baronnashor")
OLD = os.path.join(SRC, "codex_poses", "baronnashor-poses")
CYCLE = 1270                     # T-Hex's run clip: one full cycle (both legs' steps)
# the eight times: the toes pass at ~255 ms (the far leg goes ahead) and ~915 ms (the near one does; measured every 10 ms,
# 2026-11-03), so run1 and run5 are the passings and three frames share each lead between them
RUN = [("run1", 255), ("run2", 420), ("run3", 590), ("run4", 755), ("run5", 915), ("run6", 1070), ("run7", 1225),
       ("run8", 1375)]
N = len(RUN)
MS = [(RUN[(k + 1) % N][1] - t) % CYCLE or CYCLE for k, (_n, t) in enumerate(RUN)]
LIFTED = 3                       # a foot this many squares over the lower one still counts as on the ground
HIP_GAP = (-3, 1)                # the near hip from the far one, squares (x, y): a little behind and lower (3/4 view)
LEG = ["L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_ToeB1"]
TOES = ["L_Foot", "L_ToeB1", "L_ToeB2", "L_ToeB3"]
PX, C, SOLE_Y = PK.PX, PK.CANVAS, PK.SOLE_Y
NEAR, FAR = "blue", "red"
FAR_COLOURS = ("the light purple #8336E4 becomes #5A117B, the main purple #5A117B becomes #390D57, the dark purple "
               "#390D57 becomes #200B38, the ivory toes #F9D590 become #D1AA65 and #D1AA65 becomes #907054")
FAR_COLOURS_ZH = ("亮紫 `#8336E4` 换成 `#5A117B`，主紫 `#5A117B` 换成 `#390D57`，暗紫 `#390D57` 换成 `#200B38`，象牙色脚趾 "
                  "`#F9D590` 换成 `#D1AA65`、`#D1AA65` 换成 `#907054`")


def leg_at(thex, t, st):
    """T-Hex's far leg at t ms: its chain and toe points about its own hip (canvas px, the pack's scale)."""
    _, j = thex.pose(f"run@{t % CYCLE}")
    xy, _ = PK.project(j, PK.YAW, st)
    hip = thex.at(xy, "L_Hip")
    return [thex.at(xy, n) - hip for n in LEG], [thex.at(xy, n) - hip for n in TOES]


def gap(f):
    """The near toe ahead of the far one (squares; negative = the far toe ahead)."""
    return f[NEAR]["toe"][0] - f[FAR]["toe"][0]


def up(f, colour):
    return round(f[colour]["lift"] - min(f["red"]["lift"], f["blue"]["lift"]))


LOOK = {"near": ("**亮的蓝腿（近侧）在前**", "the NEAR (BLUE, light) leg ahead"),
        "far": ("**暗的红腿（远侧）在前**", "the FAR (RED, darker) leg ahead"),
        "pass": ("**换腿**：两只脚尖几乎上下对齐，一只踩在身体下面，另一只抬着从旁边经过",
                 "THE PASSING: the two toes nearly one above the other, one foot planted under the body, the other "
                 "lifted and passing beside it")}


def prompts(feet):
    zh = {"red": "红腿", "blue": "蓝腿"}
    rows, lines = [], []
    for k, (name, t) in enumerate(RUN):
        f = feet[name]
        cells = []
        for colour in (NEAR, FAR):
            b = f[colour]
            u = up(f, colour)
            where = "**踩在地上**" if u <= LIFTED else f"**抬起来**（比另一只高约 {u} 格）"
            cells.append(f"脚尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        g = gap(f)
        lead = f["lead"]
        rows.append(f"| {k + 1} | `baronnashor-run-{name}.png` | {cells[0]} | {cells[1]} | "
                    f"{LOOK[lead][0]}（相差 {abs(g)} 格） |")
        parts = [f"the {c.upper()} leg's foot {'ON THE GROUND' if up(f, c) <= LIFTED else 'LIFTED'}, its toe at square "
                 f"({f[c]['toe'][0]}, {f[c]['toe'][1]})" for c in (NEAR, FAR)]
        lines.append(f"- {name}: `RUN {k + 1} of 8 - {LOOK[lead][1]}. " + ", ".join(parts)
                     + f"; the two toes {abs(g)} square{'' if abs(g) == 1 else 's'} apart.`")
    near_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if feet[n]["lead"] == "near")
    far_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if feet[n]["lead"] == "far")
    passing = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if feet[n]["lead"] == "pass")
    return f"""# 纳什男爵：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一版的跑步（`0_old_run_wrong.png`）**两条腿从来不换**：八帧里都是同一只脚一直在前、另一只一直在后，没有一帧两条腿交错经过。这是我给的骨架的问题（不是你画错了），这一版骨架改好了。
> - 这一版（`0_run_cycle.png`，8 帧是**一个完整的循环**，迈两步）：**两条腿轮流往前迈**——第 {near_lead} 帧亮的近侧那条腿在前，第 {far_lead} 帧暗的远侧那条腿在前，第 {passing} 帧两条腿交错经过（**换腿**）。
> - 请你画 **{N} 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（身体是纳什男爵模型自己的，腿只有骨架线：模型没有腿）。
> - 格子每格 **{PX} px**，画布 **{C} × {C}**，红线是地面（**最低点 y = {SOLE_Y}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。**请严格用每格 {PX} px**。
> - **样子、颜色、画法全照定稿** `0_design.png`；**上半身（头、头冠、两只小头、两只爪子、S 形身躯、腹甲）的大小和画法照上一版的跑步**（`0_old_run_wrong.png` 的上半身没问题），**八帧的上半身一样大、一样的姿势**，只跟着步子上下起伏 0–2 格；**要改的只是两条腿**。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体移动，不要转头。

## 最要紧的：两条腿看得出谁在前

骨架里 **蓝线 = 近侧的腿**（离镜头近），**红线 = 远侧的腿**。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（紫色粗腿：亮紫 `#8336E4`、主紫 `#5A117B`、暗紫 `#390D57`，象牙色三趾脚 `#F9D590` / `#D1AA65`），**永远画在另一条腿上面**（两条腿重叠的地方它盖住远侧那条）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：{FAR_COLOURS_ZH}；**永远在近侧那条腿后面**。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 {near_lead} 帧**亮的蓝腿在前**，第 {far_lead} 帧**暗的红腿在前**，第 {passing} 帧两只脚几乎上下对齐（换腿的那一刻）。

**每一帧画完，数格子核对两只脚**：脚尖（最前面那根脚趾的尖）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**谁在前照表**。没有哪只脚是一直在前的：两只脚轮流踩地、轮流抬起、轮流在前。

| 帧 | 文件 | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 |
|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）、`0_old_run_wrong.png`（上半身照它，腿不要照它）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {C}x{C} canvas with {PX} px squares (its soles on y {SOLE_Y}) - a VOID SERPENT MONSTER on TWO SHORT THICK PURPLE LEGS with ivory three-toed feet: an S-curved purple body with a TEAL-GREEN SEGMENTED BELLY, a BLUE-VIOLET ARMOURED HEAD with yellow eyes, a red mouth and ivory tusks, a crown of PURPLE CREST FINS with MAGENTA TIPS, TWO SMALL SERPENT HEADS on thin arms, TWO BIG CURVED IVORY CLAWS. Image A stands - copy only its look. B its HEAD shown 8x. C a 3D RENDER of this same creature's own game model (its body only: the model has NO legs) in THIS FRAME OF ITS RUN, on the same {C} canvas and grid, already placed where the picture must be, its two legs drawn as lines. D the SKELETON of that frame, exactly over C: green = the body, the BLUE line = its NEAR leg, the RED line = its FAR leg, PINK and CYAN = the small heads, YELLOW and ORANGE = the claws, GREY BOX = where the head goes, the red horizontal line = the ground. E its whole run cycle, 8 frames in a row. F its OLD run: copy its UPPER BODY - the head, the crest, the small heads, the claws, the body and the belly, their size and drawing; NOT its legs (crossed out: wrong).
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY {PX} px, aligned on one straight grid from the canvas corner; its lowest point on y {SOLE_Y}.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (the purples #8336E4, #5A117B, #390D57, the ivory toes #F9D590, #D1AA65), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design ({FAR_COLOURS}), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the two PASSING frames the toes are nearly one above the other: one foot planted under the body, the other lifted beside it. Each foot exactly where D puts it; one foot on the ground, the other lifted unless the line says both are down.
COUNT THE SQUARES: the same body size in every frame and the same as image F's upper body; the legs as thick and the feet as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned. Nothing covers the face.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

""" + "\n".join(lines) + f"""

## 交回

- 每帧一张：`outputs/baronnashor-run/baronnashor-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/baronnashor-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**两帧换腿是不是真的交错**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**、**八帧上半身一样大**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **{N} 帧都画完再交**，最后写 `outputs/baronnashor-run/HANDOFF.md`，再打包成 `outputs/baronnashor_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/baronnashor/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的脸（design_baronnashor_poses.py 的读法），逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身八帧一致（必要时一个上半身用到八帧，design_sevika_run.py / design_steb_run.py 的做法）。
- 每帧在游戏里的时长（ms，按片段的间隔分 {CYCLE} ms 一个循环）：{MS}。
- 这份提示词和参考图由 `tools/art/pack_baronnashor_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\baronnashor_packs\baronnashor_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    baron = PK.Rig(BP.Model(a.lol), PK.BARON_CLIPS)
    thex = PK.Rig(TP.Model(a.lol), TP.CLIPS)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    # the pose pack's scales and the design's place (pack_baronnashor_poses.main)
    bv, _ = baron.pose(PK.DESIGN)
    sb = PK.HIP_ROW * PX / -PK.project(bv, PK.YAW, 1.0)[0][:, 1].min()
    _, tj = thex.pose("idle@0")
    txy = PK.project(tj, PK.YAW, 1.0)[0]
    low = max(thex.at(txy, s)[1] for s in PK.SOLES)
    st = (PK.ROWS - PK.HIP_ROW) * PX / (low - thex.at(txy, "Pelvis")[1])
    dx = (C - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - PK.ROWS * PX
    hip_x = dx + PK.HIP_COL * PX + PX // 2
    can = Image.new("RGBA", (C, C), PK.GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, PK.ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(PK.HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, PK.GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "0_head.png")))
    hj0 = None
    feet, refs, box = {}, [], [C, C, 0, 0]
    for k, (name, t) in enumerate([("design", 0)] + RUN):
        verts, joints = baron.pose(f"idle@{t}")
        jxy, jz = PK.project(joints, PK.YAW, sb)
        far, far_toes = leg_at(thex, t, st)
        near, near_toes = leg_at(thex, t + CYCLE // 2, st)
        hips = {FAR: np.array([0.0, 0.0]), NEAR: np.array(HIP_GAP, float) * PX}
        lowest = max(max(p[1] for p in far_toes), max(p[1] + hips[NEAR][1] for p in near_toes))
        hip_y = SOLE_Y - lowest
        base = np.array([hip_x, hip_y])
        legs = {FAR: [base + p for p in far], NEAR: [base + hips[NEAR] + p for p in near]}
        toes = {FAR: [base + p for p in far_toes], NEAR: [base + hips[NEAR] + p for p in near_toes]}
        shift = np.array([hip_x, hip_y], dtype=float)
        jxy = jxy + shift
        chains = [(PK.COL["L_leg"], [tuple(base)] + [tuple(p) for p in legs[FAR]], 1.0),
                  (PK.COL["R_leg"], [tuple(base)] + [tuple(p) for p in legs[NEAR]], -1.0)]
        for c, names in PK.BARON.items():
            pts = [tuple(baron.at(jxy, n)) for n in names]
            if c == "spine":
                pts = [tuple(shift)] + pts
            chains.append((PK.COL[c], pts, float(np.mean([jz[baron.names[n]] for n in names]))))
        hj = baron.at(jxy, "Head")
        if hj0 is None:
            hj0 = hj.copy()
        hbox = (dx + PK.HEAD_BOX[0] * PX + hj[0] - hj0[0], dy + PK.HEAD_BOX[1] * PX + hj[1] - hj0[1],
                dx + PK.HEAD_BOX[2] * PX + hj[0] - hj0[0], dy + PK.HEAD_BOX[3] * PX + hj[1] - hj0[1])
        stem = "0_design" if name == "design" else f"{k}_{name}"
        sk = Image.new("RGB", (C, C), PK.GREY)
        d = ImageDraw.Draw(sk)
        PK.grid(d)
        if name == "design":
            sk = Image.blend(sk, can.convert("RGB"), 0.55)
            d = ImageDraw.Draw(sk)
        d.rectangle(hbox, outline=(110, 110, 110), width=3)
        PK.draw_bones(d, chains)
        sk.save(lp(os.path.join(a.out, f"{stem}_skeleton.png")))
        if name == "design":
            continue
        im = pose_ref.render_hq(verts.copy(), baron.m.tris, baron.m.v["uv"], baron.m.tex, -PK.YAW, PK.PITCH, (C, C),
                                sb, shift[1], shift=0.5 - shift[0] / C).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (C, C), PK.GREY + (255,))
        d = ImageDraw.Draw(ref)
        PK.grid(d)
        ref.alpha_composite(im)
        d = ImageDraw.Draw(ref)
        PK.draw_bones(d, chains[:2])
        ref = ref.convert("RGB")
        ref.save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        refs.append(ref)
        xs = [p[0] for c in chains for p in c[1]]
        ys = [p[1] for c in chains for p in c[1]]
        box = [min(box[0], min(xs)), min(box[1], min(ys)), max(box[2], max(xs)), max(box[3], max(ys))]
        f = {"ms": MS[k - 1]}
        for colour in (NEAR, FAR):
            tip = max(toes[colour], key=lambda p: p[0])          # the foremost toe
            lo = max(p[1] for p in toes[colour])
            f[colour] = {"toe": [int(tip[0] // PX), int(tip[1] // PX)], "lift": round(float((SOLE_Y - lo) / PX), 1)}
        g = gap(f)
        f["lead"] = "pass" if abs(g) <= 3 else ("near" if g > 0 else "far")
        f["t"] = t
        feet[name] = f
        print(stem, f"t {t}", "gap", g, "lead", f["lead"], "lift near", f[NEAR]["lift"], "far", f[FAR]["lift"])

    band = (int(box[0]) - 140, int(box[1]) - 60, int(box[2]) + 140, SOLE_Y + 20)
    w, h = band[2] - band[0], band[3] - band[1]
    strip = Image.new("RGB", (N * w // 2 + (N - 1) * 6, h // 2 + 40), (255, 255, 255))
    d = ImageDraw.Draw(strip)
    for k, r in enumerate(refs):
        strip.paste(r.crop(band).resize((w // 2, h // 2), Image.LANCZOS), (k * (w // 2 + 6), 40))
        lab = {"pass": "PASS", "near": "near (blue) ahead", "far": "far (red) ahead"}[feet[RUN[k][0]]["lead"]]
        d.text((k * (w // 2 + 6) + 8, 10), f"run{k + 1}  {lab}", fill=(0, 0, 0))
    strip.save(lp(os.path.join(a.out, "0_run_cycle.png")))

    old = [Image.open(lp(os.path.join(OLD, f"baronnashor-pose-run{k}.png"))).convert("RGBA") for k in range(1, 9)]
    cut = [o.crop(o.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()) for o in old]
    hh = max(c.height for c in cut)
    sheet = Image.new("RGBA", (sum(c.width for c in cut) + 30 * 9, hh + 90), (255, 255, 255, 255))
    x = 30
    for c in cut:
        sheet.alpha_composite(c, (x, 90 + hh - c.height))
        x += c.width + 30
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
    d.text((30, 4), "OLD RUN: keep the UPPER BODY (head, crest, small heads, claws, body, belly) - its size and drawing.",
           fill=(0, 120, 0), font=font)
    d.text((30, 44), "WRONG LEGS: the same foot ahead in every frame, never passing - do not copy.",
           fill=(200, 0, 0), font=font)
    leg_top = 90 + hh - round(hh * 0.3)
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
