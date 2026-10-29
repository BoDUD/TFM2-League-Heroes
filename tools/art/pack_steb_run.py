#!/usr/bin/env python3
"""Steb's run pack for Codex (assets/source/steb/RUN_PROMPTS.md): his TFT run as 8 frames over its WHOLE cycle, with
real crossing steps (the user, 2026-10-29: 「走路要有交叉步啊 别做错了」). Sevika's redrawn run's way
(pack_sevika_run.py: the leading leg changes, the toe squares spelled out, real passing frames, the near and far legs in
two tones) from the first pack on, so the first run is not the half-cycle one-tone run the user turned down for
Sevika and Violet.

    python tools/art/pack_steb_run.py [--out C:/t/sb_work/steb_run_pack] [--lol "D:/Riot Games/League of Legends"]

His run clip is ONE whole cycle in 1.30 s (measured 2026-10-29 by the toes at the pack's yaw, C:/t/sb_work/gait.py: the
far L toe 100 model units ahead at 0, the legs passing at ~500 ms, the near R toe 33 ahead at ~650-800, passing again at
~950, the far toe ahead again by 1100). RUN takes eight frames over the whole cycle with both passings among them; MS
gives each frame its share of a LOOP_MS loop (as the clip spaces them). The same canvas, grid, scale and placing as the
pose pack (pack_steb_poses: the design pose's body height = the design's 106 rows at PX px a square, the lowest point
on SOLE_Y, the pelvis on the design's PELVIS_COL). The NEAR leg (his right leg, nearer the camera: the BLUE line) is the
same leg in every frame: the design's own leg colours, over the other where they overlap; the FAR leg (the RED line) a
step darker in the design's own darker colours (FAR_COLOURS), behind. Which leg LEADS changes twice a cycle.
Writes <out>/ (and <out>.zip): RUN_PROMPTS.md; 0_design.png, 0_design_skeleton.png, 0_head.png; per frame
<k>_run<k>_ref.png and _skeleton.png; 0_run_cycle.png (the eight refs in a row); feet.json (each frame's boots: heel and
toe squares, lift, which leg leads - the table in RUN_PROMPTS.md, and what the delivery is checked against).
"""
import argparse
import json
import os
import shutil
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
import pose_ref  # noqa: E402
import pack_steb_poses as PK  # noqa: E402
from design_steb_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "steb")
RUN = [(f"run{k + 1}", t) for k, t in enumerate(PK.RUN_MS)]
CYCLE = 1300
LOOP_MS = 880                    # the game's loop: 8 frames, each its share of the clip's spacing
MS = [round(((RUN[(k + 1) % len(RUN)][1] - t) % CYCLE) * LOOP_MS / CYCLE) for k, (_n, t) in enumerate(RUN)]
N = len(RUN)
LIFTED = 3                       # a boot this many squares over the lower one still counts as on the ground
PX = PK.PX
NEAR, FAR = "blue", "red"        # his right leg (R_, the blue line) is nearer the camera (hip depth, every run frame)
NEAR_COLOURS_ZH = "灰紫裤子 `#564A68` 带暗面 `#2E2A4A`、墨绿靴子 `#364A42` / `#17282F`、靴口和脚踝的金环"
FAR_COLOURS = "trousers all #2E2A4A, boots all #17282F, the gold rings all #A46222"
FAR_COLOURS_ZH = "裤子全用 `#2E2A4A`、靴子全用 `#17282F`、金环全用 `#A46222`"
# how each frame's legs read (his TFT run, 0_run_cycle.png)
LOOK = {
    "run1": ("红腿（远侧、暗）大步迈在前面，蓝腿（近侧）在后面蹬地，两只靴子分得最开",
             "the far (RED, darker) leg striding far ahead, the near (BLUE) leg pushing off behind - the widest split"),
    "run2": ("红腿踩在前面（往身体下方收），蓝腿在后面**抬起来**、小腿折起",
             "the far (RED) foot planted ahead, sliding back under him; the near (BLUE) leg LIFTED behind, its shin folded"),
    "run3": ("红腿踩在身体前下方，蓝腿（近侧）膝盖往前摆、靴子从后面往前",
             "the far (RED) foot planted a little ahead; the near (BLUE) knee swinging forward, its boot coming through"),
    "run4": ("**换腿的一帧**：蓝靴（近侧）从红腿旁边经过、和红靴几乎上下对齐，两条腿**交叉**在一起",
             "THE PASSING: the near (BLUE) boot passes right beside the far (RED) one, the toes one above the other, "
             "the legs crossing"),
    "run5": ("**蓝腿（近侧）在前**踩地，红腿（远侧、暗）在后面",
             "the near (BLUE) leg FORWARD, planted; the far (RED, darker) leg behind"),
    "run6": ("蓝腿踩在身体下方，红腿（远侧）在后面**抬得最高**、开始往前摆",
             "the near (BLUE) foot planted under him; the far (RED) leg LIFTED high behind, starting to swing forward"),
    "run7": ("**交叉的一帧**：红腿（远侧、暗）抬着从蓝腿**后面**往前迈过去，两只靴尖上下对齐，蓝腿在上面盖住它",
             "THE CROSSING: the far (RED) leg swinging forward BEHIND the planted near (BLUE) leg, the two toes one "
             "above the other, the blue leg drawn over it"),
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
            cells.append(f"靴尖 ({b['toe'][0]}, {b['toe'][1]})，{where}")
        g = gap(f)
        lead = ("两只靴尖上下对齐（交叉）" if abs(g) <= 2 else
                f"**{zh[NEAR]}（近侧）在前** {g} 格" if g > 0 else f"**{zh[FAR]}（远侧、暗）在前** {-g} 格")
        rows.append(f"| {k + 1} | `steb-run-{name}.png` | run@{t} | {f['rows']} | {cells[0]} | {cells[1]} | {lead} | "
                    f"{LOOK[name][0]} |")
    near_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) > 2)
    far_lead = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if gap(feet[n]) < -2)
    passing = "、".join(str(k + 1) for k, (n, _t) in enumerate(RUN) if abs(gap(feet[n])) <= 2)
    lines = "\n".join(
        f"- {name}: `RUN {k + 1} of 8 - {LOOK[name][1]}. "
        + ", ".join(f"the {c.upper()} leg's boot {'ON THE GROUND' if down(feet[name], c) else 'LIFTED'}, its toe at "
                    f"square ({feet[name][c]['toe'][0]}, {feet[name][c]['toe'][1]})" for c in (NEAR, FAR))
        + f"; the two toes {abs(gap(feet[name]))} square{'' if abs(gap(feet[name])) == 1 else 's'} apart"
        + ("" if abs(gap(feet[name])) <= 2 else f", the {(NEAR if gap(feet[name]) > 0 else FAR).upper()} one ahead")
        + f"; about {feet[name]['rows']} squares tall.`"
        for k, (name, _t) in enumerate(RUN))
    return f"""# 斯特卜：跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - **跑步一定要有交叉步、看得出两条腿轮流在前**。以前几个英雄的跑步被用户退回过（「换腿不明显」「走路腿没有前后交换」）：八帧只画了半个循环、两条腿画成一样的颜色。这次照下面做。
> - 金铲铲里他是这样跑的（`0_run_cycle.png`，8 帧是**一个完整的循环**，1.30 秒迈两步）：身体前倾，两手握着警棍随步子摆，**两条腿轮流迈步**——第 {far_lead} 帧远侧那条腿在前，第 {passing} 帧两条腿交错经过（**换腿、交叉**），第 {near_lead} 帧近侧那条腿在前。
> - 请你画 **{N} 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（他金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **{PX} px**，画布 **{C} × {C}**，红线是地面（**脚底 y = {S}**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 {PX} px 放在这张画布上。**请严格用每格 {PX} px**。
> - **样子、颜色、画法全照定稿** `0_design.png`：浅海绿皮肤、青绿飞机头、鱼鳍耳、蓝色执法官制服、胸前药包、背后的大棕皮背包、两根蓝钢警棍（跑的时候两只手各握一根，照参考图随步子摆）。**八帧的上半身一样大**、跟着步子上下起伏 0–2 格。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。警棍不要挡住脸。

## 最要紧的：两条腿看得出谁在前、有交叉步

骨架里 **蓝线 = 近侧的腿**（他的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（{NEAR_COLOURS_ZH}），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：{FAR_COLOURS_ZH}；**永远在近侧那条腿后面**。
- 两只靴子每帧都要露出来。

**哪条腿在前（靴子更靠画面右边）每半个循环换一次**：第 {far_lead} 帧**暗的红腿在前**，第 {near_lead} 帧**亮的蓝腿在前**，第 {passing} 帧两只靴子几乎上下对齐（换腿的那一刻，两条腿**交叉**：一条从另一条后面经过，蓝腿盖在上面）。

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只靴尖之间的距离照表**。没有哪只靴子是一直不动的：两只靴子轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {C}x{C} canvas with {PX} px squares (his soles on y {S}) - a TALL, LEAN BUT STURDY YOUNG FISH-FOLK MAN: pale sea-green skin, a teal quiff, pointed green fin ears, pale cyan eyes; a BLUE ENFORCER UNIFORM with gold trim, brown leather medicine pouches on crossed straps, a dark brown belt, GREY-PURPLE TROUSERS, DARK BOTTLE-GREEN TALL BOOTS with GOLD RINGS at the top and the ankle; a BIG BROWN LEATHER BACKPACK on his back; TWO blue steel SIDE-HANDLE BATONS with brass heads (while running one in each hand, swinging as in C). Image A stands idle - copy only his look. B his HEAD shown 8x. C a 3D RENDER of this same character's own game model in THIS FRAME OF HIS RUN, on the same {C} canvas and grid, already scaled and placed where the picture must be (copy the pose of the body and legs, never its 3D shading). D the SKELETON of that frame, exactly over C: green = the spine, ORANGE = his right arm, CYAN = his left arm, PURPLE bars = the batons (GOLD DOT = the brass head), BROWN outline = the backpack, the BLUE line = his NEAR leg, the RED line = his FAR leg, GREY BOX = where the head goes, the red horizontal line = the ground. E his whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {C}x{C} PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY {PX} px, aligned on one straight grid from the canvas corner; his lowest point on y {S}.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (grey-purple trousers with their shade, the bottle-green boot with its gold rings), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design ({FAR_COLOURS}), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the PASSING / CROSSING frames the two legs cross: one passes behind the other, the near leg drawn over it. Each boot exactly where D puts it; one boot on the ground, the other lifted unless the line says both are down. Both boots always visible.
COUNT THE SQUARES: the same body size in every frame and the same as image A; the boots as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. Nothing covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

{lines}

## 交回

- 每帧一张：`outputs/steb-run/steb-run-<名字>.png`（`run1` … `run{N}`，{C} × {C}、真透明背景、每格 {PX} px）；原始生成图原样放进 `outputs/steb-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只靴尖的格子和距离（上表）、**谁在前**、**交叉的帧两条腿真的交叉**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**，不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格、谁在前。
- **{N} 帧都画完再交**，最后写 `outputs/steb-run/HANDOFF.md`，再打包成 `outputs/steb_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/steb/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头，逐帧对 `feet.json` 量两只靴尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 {LOOP_MS} ms 一个循环）：{MS}。
- 这份提示词和参考图由 `tools/art/pack_steb_run.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sb_work\steb_run_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    poser = PK.Poser(a.lol)
    names = poser.names
    body = PK.part_vertices(poser, "body")
    hv = PK.vertices_of(poser, PK.HEAD_JOINTS) & body
    packv = PK.part_vertices(poser, "pack")
    sticks_v = PK.batons(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    C, SOLE_Y = PK.CANVAS, PK.SOLE_Y

    # the pose pack's scale and the design's place (pack_steb_poses.main)
    iv, ij = poser.pose(PK.DESIGN)
    pxy, _ = PK.Poser.project(iv, PK.YAW, 1.0, 0.0, 0.0)
    scale = PK.ROWS * PX / (pxy[body, 1].max() - pxy[body, 1].min())
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

    def placed(verts, joints):
        xy, z = PK.Poser.project(verts, PK.YAW, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = PK.Poser.project(joints, PK.YAW, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        return xy, jxy, jz, ground, shift

    xy0, jxy0, jz0, _, _ = placed(iv, ij)
    PK.skeleton(poser, jxy0, jz0, (0, 0, 0, 0), os.path.join(a.out, "0_design_skeleton.png"),
                [PK.baton_line(xy0, s, y) for s, y in sticks_v], PK.hull(xy0[packv]), can)
    feet, refs = {}, []
    for k, (name, t) in enumerate(RUN):
        clip = f"run@{t}"
        verts, joints = poser.pose(clip)
        xy, jxy, jz, ground, shift = placed(verts, joints)
        # the near leg: the hip nearer the camera (the larger depth) - his right one in every frame of the run
        if not jz[names["R_Hip"]] > jz[names["L_Hip"]]:
            sys.exit(f"{name}: the near leg is not his right one: NEAR / FAR and the prompt's colours are wrong")
        if xy[body, 1].min() < 40:
            sys.exit(f"{name}: the head {xy[body, 1].min():.0f} px from the top (fewer px a square)")
        top = int(xy[body, 1].min() // PX)
        hx, hy = xy[hv, 0], xy[hv, 1]
        stem = f"{k + 1}_{name}"
        PK.skeleton(poser, jxy, jz, (hx.min(), hy.min(), hx.max(), hy.max()),
                    os.path.join(a.out, f"{stem}_skeleton.png"), [PK.baton_line(xy, s, y) for s, y in sticks_v],
                    PK.hull(xy[packv]))
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
        lab = "PASS / CROSS" if abs(g) <= 2 else ("near (blue) ahead" if g > 0 else "far (red) ahead")
        d.text((k * (w // 2 + 6) + 8, 10), f"run{k + 1}  {lab}", fill=(0, 0, 0))
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
