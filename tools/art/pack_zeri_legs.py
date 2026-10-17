#!/usr/bin/env python3
"""Build zeri_legs_pack.zip: Codex redraws only Zeri's legs for an 8-frame run that changes legs, in the design's own
leg shapes, under the run body that stays (the user, 2026-10-11: 「泽丽走路时候模型怪的问题查了吗」「应该是腿部完全变形的
原因」).

    python tools/art/pack_zeri_legs.py [--out DIR]

rig_zeri.py draws the run's legs as bones on League's 3/4 run angles (rigkit.bone_arm): thin rubber legs, not the
design's, crossing and knotting (a boot standing on the other or vanishing behind it), the body thrown 3 rows up and
down by League's hops. Re-angling the bones keeps them thin, so the legs go to Codex like Nautilus's
(pack_nautilus_legs.py): the run body (rig_zeri's run_pieces body and the level rifle arm, bobbing a row) in every
frame's place, a near/far leg skeleton per frame, the design's legs and the idle as the legs to draw, the 26 colours.
Writes assets/source/zeri/LEGS_PROMPT.md and dist/nautilus_packs/zeri_legs_pack.zip.
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_zeri as Z  # noqa: E402

K = Z.K
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DOC = os.path.join(ROOT, "assets", "source", "zeri", "LEGS_PROMPT.md")
CW, CH = Z.CELL
PX, PY = Z.CELL_PIVOT                          # the standing point in a cell
GROUND = PY + Z.SOLES - Z.PIVOT[1]             # the soles' outline row in a cell
BOB = [0, 0, -1, -1, 0, 0, -1, -1]             # the body rises a row while the legs pass
# the skeleton, per frame: (near leg, far leg), each (knee, ankle) as (x from the standing point, rows under it);
# the hip joint (HIP_X, HIP_Y). Frames 1-4 the near leg leads, 5-8 the far one: contact, down, passing, up
HIP_X, HIP_Y = 0, -4
LEAD = [((5, 2), (9, 7)), ((3, 3), (2, 8)), ((1, 3), (0, 8)), ((-2, 3), (-6, 8))]
TRAIL = [((-4, 3), (-10, 6)), ((-3, 3), (-9, 3)), ((3, 2), (-3, 5)), ((6, 0), (7, 5))]
RUN = [(LEAD[k], TRAIL[k]) for k in range(4)] + [(TRAIL[k], LEAD[k]) for k in range(4)]


def to_cell(canvas):
    """The rig's 128 canvas (its standing point PIVOT) cut to a strip cell (its standing point CELL_PIVOT)."""
    x0, y0 = Z.PIVOT[0] - PX, Z.PIVOT[1] - PY
    return canvas[y0:y0 + CH, x0:x0 + CW].copy()


def strip_cells(tag, cells):
    a = np.asarray(Image.open(os.path.join(NATIVE, f"zeri_{tag}.png")).convert("RGBA"))[::8, ::8]
    cols = a.shape[1] // CW
    return [a[(k // cols) * CH:(k // cols + 1) * CH, (k % cols) * CW:(k % cols + 1) * CW].copy()
            for k in range(len(cells["tags"][tag]))]


def grid(imgs, cols):
    rows = (len(imgs) + cols - 1) // cols
    out = np.zeros((rows * CH, cols * CW, 4), np.uint8)
    for k, c in enumerate(imgs):
        out[(k // cols) * CH:(k // cols + 1) * CH, (k % cols) * CW:(k % cols + 1) * CW] = c
    return Image.fromarray(out)


def guide(bodies, legs, cols, z=7):
    tiles = []
    for b, (near, far) in zip(bodies, legs):
        t = Image.new("RGBA", (CW * z, CH * z), (150, 160, 150, 255))
        faint = b.copy()
        faint[..., 3] = (faint[..., 3] * 0.55).astype(np.uint8)
        t.alpha_composite(Image.fromarray(np.ascontiguousarray(faint)).resize(t.size, Image.NEAREST))
        d = ImageDraw.Draw(t)

        def pt(x, y):
            return ((PX + x + 0.5) * z, (PY + y + 0.5) * z)
        d.line([pt(-PX, GROUND - PY), pt(CW - PX, GROUND - PY)], fill=(200, 0, 0, 255), width=2)
        for (knee, ankle), colour in ((far, (40, 90, 230, 255)), (near, (255, 140, 0, 255))):
            d.line([pt(HIP_X, HIP_Y), pt(*knee), pt(*ankle)], fill=colour, width=z)
            ax, ay = pt(*ankle)
            d.ellipse([ax - z, ay - z, ax + z, ay + z], fill=colour)
        tiles.append(t)
    W, H = tiles[0].size
    out = Image.new("RGB", (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (40, 40, 40))
    for k, t in enumerate(tiles):
        ImageDraw.Draw(t).text((4, 4), str(k + 1), fill=(0, 0, 0, 255))
        out.paste(t.convert("RGB"), ((k % cols) * (W + 6), (k // cols) * (H + 6)))
    return out


def palette_png(a):
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]},
                  key=lambda c: -(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]))
    out = Image.new("RGB", (len(cols) * 40, 60), (255, 255, 255))
    d = ImageDraw.Draw(out)
    for i, c in enumerate(cols):
        d.rectangle([i * 40, 0, i * 40 + 39, 39], fill=c)
        d.text((i * 40 + 2, 42), "#%02X%02X%02X" % c, fill=(0, 0, 0))
    return out


DOC_TEXT = """# 泽丽：只重画跑步的腿——8 帧换腿，腿要是设计稿那双腿（给 Codex 的提示词）

> **为什么重画**：现在的跑步腿是程序按英雄联盟斜侧视角的关节角度「画骨头」画出来的细腿，**跟设计稿的腿完全不是一个形状**，
> 投影到侧面后两条腿交叉打结、一只靴子踩在另一只上或整个被挡住，身体还跟着英雄联盟的跳步上下跳 3 行。
> 用户：「泽丽走路时候模型怪」「应该是腿部完全变形的原因」。
> **上半身（头、头发、外套、两只手、端平的枪）已经定稿，一个像素都不要动。只画腰带以下的腿：紧身裤、膝盖上的浅色补丁、靴子。**

## 交给你的文件

- `inputs/body_run_1x.png`：跑步 8 帧（4 列 x 2 行，每格 96x80，1 像素 = 游戏里 1 格），**每格已经放好这一帧的上半身**
  （外套下摆的两片和垂着的手也在），腰带以下是空的——你在下面画腿。上半身在第 3、4、7、8 帧抬高 1 行，已经放好。
- `inputs/design_legs.png`（放大 16 倍）、`inputs/idle_1x.png`：**设计稿的腿就是这双腿**——深酒红色紧身裤（亮/暗两层），近侧膝盖一块浅棕色补丁，
  棕色靴子（橙黄色鞋扣和鞋底高光），粗细、长短、靴子的形状照这个画，每一帧都一样。
- `inputs/guide_run.png`：每一帧两条腿该在哪里——**橙色线是近侧腿，蓝色线是远侧腿**（胯 → 膝盖 → 脚踝），**红线是地面**
  （靴底的黑色描边落在这一行）。
- `inputs/now_run_1x.png`：现在的样子（错误示范：细腿、打结、靴子叠在一起）。
- `inputs/palette.png`：只用这 26 种颜色。

## 要求

1. **只画腰带以下**，上半身的像素原样保留；外套下摆在腿的前面，腿从下摆下面伸出来；胯和腰带严丝合缝。
2. **腿就是设计稿那双腿**：紧身裤的粗细和设计稿一样（不细成一根线、不像橡皮筋一样弯），靴子是设计稿的整只靴子、形状不变；
   弯膝盖就画成弯的腿，但大腿、小腿的粗细不变。
3. **跑步是真正的换腿**（身体朝右的侧身跑）：第 1-4 帧近侧腿领先——1 着地（近侧脚在前落地，远侧腿在后蹬地）、
   2 下沉（近侧脚踩在身下，远侧脚在后面抬起）、3 交错（近侧腿直立在身下，远侧腿弯着从身下向前摆，脚离地）、
   4 腾起（近侧腿在后蹬，远侧腿膝盖抬起向前伸）；**第 5-8 帧同样的动作换成远侧腿领先**。按 `guide_run.png` 画，
   每帧只移动一点，连起来是顺的。
4. **近侧腿用设计稿的颜色（膝盖补丁在近侧腿上），远侧腿整条暗一档**，两腿重叠的地方远侧腿在后面被挡住；**两只靴子不能叠在一起**。
5. **落地的脚靴底描边在红线那一行**，抬起的脚离地 2-3 行；步子轻快，不要大劈叉。
6. 像素风规则：1 像素 = 1 格，1 像素黑色描边（#0A0411），不要抗锯齿、不要半透明、不要新颜色。

## 交付

- `run_1x.png`：384x160（4 列 x 2 行，每格 96x80），8 帧完整画面（你的腿 + 原样的上半身），透明背景；
- 再给一张放大 8 倍的预览图。

## Prompt (English)

Redraw ONLY the legs of this pixel-art girl (Zeri, side view facing right, rifle held level), 1 px = 1 game pixel, the
26 colours of palette.png only, 1-px outline #0A0411, no anti-aliasing. Every cell of body_run_1x.png already holds the
finished upper body (the coat's two hanging panels and the hanging hand included): keep every one of those pixels and
draw the legs under the belt, coming out from under the coat. The legs must be the DESIGN's legs (design_legs.png,
idle_1x.png): dark wine-red leggings in their two shades and the design's thickness (never thin lines or rubber bends),
the tan patch on the near knee, the design's whole brown boots with their orange-yellow buckle and sole. The run must
CHANGE LEGS: frames 1-4 the near leg leads (1 contact: near foot forward on the ground, far leg pushing off behind;
2 down: near foot planted under her, far foot lifting behind; 3 passing: near leg straight under her, far leg swinging
forward under the body with the knee bent, foot off the ground; 4 up: near leg pushing off behind, far knee raised
reaching forward), frames 5-8 the same with the far leg leading - follow guide_run.png (orange = near leg, blue = far
leg, red = the ground row). The far leg one shade darker and behind the near one where they overlap; the two boots never
stack on each other. Planted soles on the red row, lifted feet 2-3 rows up, light quick steps. Deliver run_1x.png
(384x160, 4x2 cells of 96x80), transparent, plus an 8x preview.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "nautilus_packs"))
    a = ap.parse_args()
    with open(os.path.join(NATIVE, "zeri_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    rig = Z.Rig()
    body, _ = rig.run_pieces()
    bodies = []
    for bob in BOB:
        c = np.zeros_like(rig.a)
        K.put(c, K.shifted(body, 0, bob), 0, 0)
        rig.level_arm(c, bob)
        bodies.append(to_cell(c))
    pack = os.path.join(a.out, "zeri_legs_pack")
    shutil.rmtree(pack, ignore_errors=True)
    os.makedirs(os.path.join(pack, "inputs"))
    grid(bodies, 4).save(os.path.join(pack, "inputs", "body_run_1x.png"))
    grid(strip_cells("run", cells), 4).save(os.path.join(pack, "inputs", "now_run_1x.png"))
    idle = strip_cells("idle", cells)[0]
    grid([idle], 1).save(os.path.join(pack, "inputs", "idle_1x.png"))
    legs = to_cell(rig.a)
    legs[:PY + (Z.OY + int(Z.Rw(25))) - Z.PIVOT[1]] = 0
    ys, xs = np.nonzero(legs[..., 3])
    legs = legs[max(ys.min() - 2, 0):ys.max() + 3, max(xs.min() - 2, 0):xs.max() + 3]
    Image.fromarray(np.ascontiguousarray(legs)).resize((legs.shape[1] * 16, legs.shape[0] * 16), Image.NEAREST).save(
        os.path.join(pack, "inputs", "design_legs.png"))
    guide(bodies, RUN, 4).save(os.path.join(pack, "inputs", "guide_run.png"))
    palette_png(rig.a).save(os.path.join(pack, "inputs", "palette.png"))
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(DOC_TEXT)
    shutil.copy(DOC, os.path.join(pack, "LEGS_PROMPT.md"))
    zpath = os.path.join(a.out, "zeri_legs_pack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(pack):
            for name in files:
                full = os.path.join(base, name)
                z.write(full, os.path.relpath(full, pack))
    print(zpath)


if __name__ == "__main__":
    main()
