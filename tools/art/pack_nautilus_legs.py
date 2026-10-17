#!/usr/bin/env python3
"""Build nautilus_legs_pack.zip: Codex redraws only Nautilus's legs - an 8-frame run that changes legs and an upright
idle - under the body that is already final (the user, 2026-10-11: 「走路的时候看着还有点怪」「待机动作你看了不奇怪吗」,
then picked 「让 Codex 重画腿」).

    python tools/art/pack_nautilus_legs.py [--out DIR]

Codex's side-on run (assets/source/nautilus/codex_strips2) keeps the same leg in front in all 8 frames; legs stitched
from those frames either jump across each other or stop for a frame (fix_nautilus_strips2.py steps 6-8), and the idle
stands on a copy of one of them. The pack gives Codex the final run body (frame 1's body, the straight carried anchor,
every row down to the belt) in each frame's place, a skeleton for every leg, the 23 colours, League's walk and the
current frames, and asks for the legs only. Writes assets/source/nautilus/LEGS_PROMPT.md and the zip in
dist/nautilus_packs.
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
import fix_nautilus_strips2 as F  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "nautilus")
DOC = os.path.join(SRC, "LEGS_PROMPT.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ROOT), "Temp", "nt_work")
REFS = {"lol_walk_legs.png": os.path.join(TMP, "review", "lol_run_legs8.png"),
        "oppi_nautilus_run.png": os.path.join(TMP, "review", "oppi_naut_run.png"),
        "oppi_nautilus_idle.png": os.path.join(TMP, "review", "oppi_naut_idle.png")}
CELL = 128
GROUND = 99                                   # the soles' outline row in every cell
# the skeleton, per frame: (near leg, far leg), each (knee, ankle) as (x from the standing point, row); the hip joint
# is (HIP_X, HIP_Y). Frames 1-4 the near leg leads, 5-8 the far one: contact, down, passing, up.
HIP_X, HIP_Y = -1, 88
LEAD = [((4, 92), (7, 96)), ((3, 93), (2, 97)), ((1, 93), (0, 97)), ((-1, 93), (-4, 97))]
TRAIL = [((-4, 93), (-9, 96)), ((-3, 93), (-8, 94)), ((2, 92), (-3, 95)), ((5, 91), (5, 95))]
RUN = [(LEAD[k], TRAIL[k]) for k in range(4)] + [(TRAIL[k], LEAD[k]) for k in range(4)]
IDLE = (((1, 93), (1, 97)), ((-4, 93), (-4, 97)))


def frames(tag, cells):
    a = np.asarray(Image.open(os.path.join(NATIVE, f"nautilus_{tag}.png")).convert("RGBA"))[::8, ::8]
    n = len(cells["tags"][tag])
    return [a[F.cell(k, n, CELL, CELL)].copy() for k in range(n)]


def body(f, belt):
    """The frame down to its belt, and the near fist's lowest squares under it."""
    out = f.copy()
    out[belt + 1:] = 0
    F.K.put(out, F.lower(f, belt)[1], 0, 0)
    return out


def grid(cells_imgs, cols):
    rows = (len(cells_imgs) + cols - 1) // cols
    out = np.zeros((rows * CELL, cols * CELL, 4), np.uint8)
    for k, c in enumerate(cells_imgs):
        out[(k // cols) * CELL:(k // cols + 1) * CELL, (k % cols) * CELL:(k % cols + 1) * CELL] = c
    return Image.fromarray(out)


def guide(bodies, pivots, legs, cols, z=6):
    """Each cell 6x: the body faint, the ground line, the near leg orange and the far leg blue (hip - knee - ankle)."""
    tiles = []
    for b, px, (near, far) in zip(bodies, pivots, legs):
        crop = b[36:104, px - 34:px + 30]
        t = Image.new("RGBA", (crop.shape[1] * z, crop.shape[0] * z), (150, 160, 150, 255))
        faint = crop.copy()
        faint[..., 3] = (faint[..., 3] * 0.55).astype(np.uint8)
        t.alpha_composite(Image.fromarray(np.ascontiguousarray(faint)).resize(t.size, Image.NEAREST))
        d = ImageDraw.Draw(t)

        def pt(x, y):
            return ((x + 34 + 0.5) * z, (y - 36 + 0.5) * z)
        d.line([pt(-34, GROUND), pt(30, GROUND)], fill=(200, 0, 0, 255), width=2)
        for (knee, ankle), colour in ((far, (40, 90, 230, 255)), (near, (255, 140, 0, 255))):
            d.line([pt(HIP_X, HIP_Y), pt(*knee), pt(*ankle)], fill=colour, width=z)
            d.ellipse([pt(*ankle)[0] - z, pt(*ankle)[1] - z, pt(*ankle)[0] + z, pt(*ankle)[1] + z], fill=colour)
        tiles.append(t)
    W, H = tiles[0].size
    out = Image.new("RGB", (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (40, 40, 40))
    for k, t in enumerate(tiles):
        d = ImageDraw.Draw(t)
        d.text((4, 4), str(k + 1), fill=(0, 0, 0, 255))
        out.paste(t.convert("RGB"), ((k % cols) * (W + 6), (k // cols) * (H + 6)))
    return out


def palette_png():
    items = sorted(F.L.items())
    out = Image.new("RGB", (len(items) * 40, 60), (255, 255, 255))
    d = ImageDraw.Draw(out)
    for i, (k, c) in enumerate(items):
        d.rectangle([i * 40, 0, i * 40 + 39, 39], fill=tuple(int(v) for v in c))
        d.text((i * 40 + 4, 42), "#%02X%02X%02X" % tuple(int(v) for v in c), fill=(0, 0, 0))
    return out


DOC_TEXT = """# 诺提勒斯：只重画腿——跑步 8 帧换腿 + 待机直立（给 Codex 的提示词）

> **为什么重画**：上一轮的侧身跑步 8 帧里**始终是同一条腿在前**（像小跳步），没有换腿的画面；用这些帧拼出来的换腿，
> 要么一帧之内腿从后面跳到前面，要么跑到一半两腿并拢像停下来站了一下；待机也只能拿其中一条腿复制一份。
> 用户：「走路压根看不出换腿」「这交叉步看着好怪啊」「走路的时候看着还有点怪」「待机动作你看了不奇怪吗」
> 「待机时腿不要岔开啊 直立站那不就行了 你看oppi的泰坦啊」。
> **上半身（头盔、胸甲肩甲、两只手、背上的锚）已经定稿，一个像素都不要动。只画腰带以下：胯、大腿、护膝、小腿、靴子。**

## 交给你的文件

- `inputs/body_run_1x.png`：跑步 8 帧（4 列 x 2 行，每格 128x128，1 像素 = 游戏里 1 格），**每格里已经放好了这一帧的上半身**，
  画到腰带（青色灯带那一行）为止，下面是空的——你在下面画腿。上半身随步伐上下浮动 1 行，已经放在正确的高度。
- `inputs/body_idle_1x.png`：待机 1 格，上半身同上。
- `inputs/guide_run.png`、`inputs/guide_idle.png`：每一帧两条腿该在哪里——**橙色线是近侧腿，蓝色线是远侧腿**
  （胯 → 膝盖 → 脚踝，圆点是脚踝），**红线是地面**（靴底的黑色描边落在这一行，第 99 行）。
- `inputs/now_run_1x.png`、`inputs/now_idle_1x.png`：现在的样子（腿的颜色、粗细、靴子的画法照这个，**换腿的方式不要照这个**）。
- `inputs/palette.png`：只用这 23 种颜色。
- `refs/lol_walk_legs.png`：英雄联盟里诺提勒斯走路的腿（沉重、步子不大、抬膝跺脚）；
  `refs/oppi_nautilus_run.png`、`refs/oppi_nautilus_idle.png`：oppi 画的诺提勒斯（待机两腿并拢直立）。

## 要求

1. **只画腰带以下**；腰带那一行和以上（包括锚、手）的像素原样保留。胯部要和上半身的下边缘严丝合缝（没有缝、没有台阶、不歪）。
2. **腿就是现在这双腿**：深灰黑的潜水服、膝盖正面的青铜护膝、巨大的潜水靴（厚青铜鞋底，鞋尖朝画面右边）；
   粗细、长短和 `now_run_1x.png` 一样，每一帧都一样（不压扁、不拉长、不变形）；膝盖弯就画成弯的腿。
3. **跑步是真正的换腿**（侧身朝右）：第 1-4 帧近侧腿领先——1 着地（近侧脚在前落地，远侧腿在后蹬地）、2 下沉（近侧脚踩在身下，远侧脚在后面抬起）、
   3 交错（近侧腿直立在身下，远侧腿弯着从身下向前摆，脚离地）、4 腾起（近侧腿在后蹬，远侧腿膝盖抬起向前伸）；
   **第 5-8 帧同样的动作换成远侧腿领先**。按 `guide_run.png` 的骨架画，两条腿每帧都只移动一点，连起来是顺的，不能一帧之内跳过去。
4. **近侧腿用现在近侧腿的颜色，远侧腿整条暗一档**（同一套颜色里往暗一级），两腿重叠的地方远侧腿在后面被挡住。
5. **落地的脚靴底描边在第 99 行**，抬起的脚离地 2-4 行；步子不比现在第 1 帧更大，沉重、短促，像英雄联盟里那样。
6. **待机**：两腿并拢直立（近侧腿在前一点，远侧腿紧挨在后面，两只靴子都平踩在第 99 行），不岔开，像 oppi 的诺提勒斯；静止的一帧。
7. 像素风规则：1 像素 = 1 格，1 像素黑色描边（#070211），不要抗锯齿、不要半透明、不要新颜色。

## 交付

- `run_1x.png`：512x256（4 列 x 2 行，每格 128x128），8 帧完整画面（你的腿 + 原样的上半身），透明背景；
- `idle_1x.png`：128x128，同上；
- 再各给一张放大 8 倍的预览图，方便我对照。

## Prompt (English)

Redraw ONLY the legs of this pixel-art character (Nautilus in a heavy diving suit, side view facing right), 1 px = 1 game
pixel, the 23 colours of palette.png only, 1-px outline #070211, no anti-aliasing. Every cell of body_run_1x.png already
holds the finished upper body down to the belt (the teal light): keep every one of those pixels; draw the hips, thighs,
bronze knee guards, shins and big diving boots below it, joined to the body's lower edge without a gap or a step. The
legs are the legs of now_run_1x.png (same colours, thickness, length, boots pointing right), but the run must CHANGE LEGS:
frames 1-4 the near leg leads (1 contact: near foot forward on the ground, far leg pushing off behind; 2 down: near foot
planted under him, far foot lifting behind; 3 passing: near leg straight under him, far leg swinging forward under the
body with the knee bent, foot off the ground; 4 up: near leg pushing off behind, far knee raised reaching forward),
frames 5-8 the same with the far leg leading - follow guide_run.png (orange = near leg, blue = far leg, red = the ground,
row 99). Small steps every frame so the cycle plays smoothly, heavy and short like League's Nautilus (lol_walk_legs.png).
The near leg in the current near-leg colours, the far leg one shade darker and behind it where they overlap. Planted
soles on row 99, lifted feet 2-4 rows up. Idle (body_idle_1x.png, guide_idle.png): one frame standing upright, legs
straight and together, the near leg a little in front, both boots flat on row 99 - like oppi's Nautilus. Deliver
run_1x.png (512x256, 4x2 cells of 128x128) and idle_1x.png (128x128), transparent, plus 8x previews.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "nautilus_packs"))
    a = ap.parse_args()
    with open(os.path.join(NATIVE, "nautilus_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    run, idle = frames("run", cells), frames("idle", cells)
    piv_run = [int(p["pivot"][0]) for p in cells["tags"]["run"]]
    piv_idle = int(cells["tags"]["idle"][0]["pivot"][0])
    belts = [F.BELT[k % 4] for k in range(8)]
    bodies = [body(f, b) for f, b in zip(run, belts)]
    idle_body = body(idle[0], F.BELT[0])
    pack = os.path.join(a.out, "nautilus_legs_pack")
    shutil.rmtree(pack, ignore_errors=True)
    os.makedirs(os.path.join(pack, "inputs"))
    os.makedirs(os.path.join(pack, "refs"))
    grid(bodies, 4).save(os.path.join(pack, "inputs", "body_run_1x.png"))
    grid([idle_body], 1).save(os.path.join(pack, "inputs", "body_idle_1x.png"))
    grid(run, 4).save(os.path.join(pack, "inputs", "now_run_1x.png"))
    grid(idle[:1], 1).save(os.path.join(pack, "inputs", "now_idle_1x.png"))
    guide(bodies, piv_run, RUN, 4).save(os.path.join(pack, "inputs", "guide_run.png"))
    guide([idle_body], [piv_idle], [IDLE], 1).save(os.path.join(pack, "inputs", "guide_idle.png"))
    palette_png().save(os.path.join(pack, "inputs", "palette.png"))
    for name, path in REFS.items():
        shutil.copy(path, os.path.join(pack, "refs", name))
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(DOC_TEXT)
    shutil.copy(DOC, os.path.join(pack, "LEGS_PROMPT.md"))
    zpath = os.path.join(a.out, "nautilus_legs_pack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(pack):
            for name in files:
                full = os.path.join(base, name)
                z.write(full, os.path.relpath(full, pack))
    print(zpath)


if __name__ == "__main__":
    main()
