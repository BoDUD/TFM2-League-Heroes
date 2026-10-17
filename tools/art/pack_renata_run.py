"""Renata run skin-swap pack (league_swain's skeleton + skin method, tools/art/pack_swain_run.py): the user on the first
action review, 2026-10-17: 「走路姿势很奇怪」 - her walk posed from the design's own legs stayed a jumble (both hands hang
at her hips over short chibi legs, the near leg hides under the mechanical hand). oppi's pack has no Renata, so the
skeleton is League's own: her Run rendered at our square scale with our head-to-body proportions
(tools/lol/native_pose.py, height 54, head x2, legs x0.85), 8 frames of one 1067 ms cycle; image 2 = our approved idle
(tools/art/rig_renata.py: hands empty, the pistol tucked muzzle down at her far hip), same cell size; a short Chinese
prompt. -> rn/dist/renata_packs/renata_run_swap_pack.zip (League's renders never go into the repo).

    python tools/lol/native_pose.py <spec> --out C:/t/rn_np/skel --tag run   (the spec: assets/source/renata/poses.json
        with height 54, chibi head 2.0 / legs 0.85, cell [72, 72, 6])
    python tools/art/pack_renata_run.py --skel C:/t/rn_np/skel/renata_native_run.png
"""
import argparse
import os
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig_renata as R  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rn_work", "runswap")
OUT = os.path.join(TMP, "renata_run_swap_pack")
ZIP = os.path.join(R.ROOT, "dist", "renata_packs", "renata_run_swap_pack.zip")
Z = 6                            # screen px a square
NATIVE_CELL, NATIVE_Z = 72, 8    # native_pose's cells (squares) and its zoom
CW, CH = 60, 64                  # a cell in our squares (PPU 1.5: 1.5 a game pixel)
FEET = 60                        # the soles' row inside a cell
KEY = (0, 255, 0)

PROMPT = """# 烈娜塔 走路 换皮（骨架 + 皮囊）

上传顺序：图1 = `1_动作骨架_联盟走路.png`，图2 = `2_角色_烈娜塔定稿.png`。

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（炼金男爵烈娜塔）。

1. 保留图1所有帧的位置、大小、排列顺序：4×2 共 8 帧，从左到右、从上到下；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作：一前一后交叉迈步（像走秀的猫步，前脚落在后脚前面），往后收的腿弯膝、鞋跟抬起；长发往身后飘；两条手臂随步子一前一后摆动（和同侧的腿相反）。
3. 身体结构、配色、特征完全换成图2：黑紫长发和额前银蓝挑染、棕色皮肤、品红眼睛、银色面罩和金环、白色短披肩（金边、品红里衬）、深藏青马甲和金扣、品红衬衫和领带、白色喇叭长裤、黑色短靴（金鞋尖、金鞋跟）。
   - **近侧（画面左边）是金色机械臂**（品红线条、金爪），**远侧的手戴黑手套，手里不拿枪**。
   - **深色手枪枪口朝下插在远侧胯部**，和图2一样。
   - 体型和图2一样大（大约 54 格高），头和身体比例和图2一样，不要变大变小、变胖变瘦。
4. 两条喇叭裤腿每一帧都要完整画出来：近侧的腿在前面时盖住远侧的腿；裤脚喇叭口、靴子和图2一样；脚底落在格子的地面线上。
5. 像素画：方块大小和图2一样（每个像素方块一样大，整齐对格），1 像素深色描边，不要抗锯齿、不要渐变、不要模糊。

背景保持纯绿色 #00FF00（和角色差异最大的纯色），方便抠图。风格保持与原图一致。重点在于精准复刻原图的"动作骨架"，只是换了"皮囊"。

交付：8 帧的整张图 `renata_run_swap.png`（和图1一样 4×2 排列、一样大小），放在 `outputs/renata-run/`，打包成 `renata_run_swap_done.zip`，附 `HANDOFF.md`。
"""


def lp(p):
    return R.lp(p)


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def on_key(a):
    out = np.zeros(a.shape[:2] + (3,), np.uint8)
    out[:] = KEY
    m = a[..., 3] > 0
    out[m] = a[m][:, :3]
    return out


def native_frames(path, n=8, cols=4):
    """The native_pose strip's frames at one square a pixel, each cut to its cell; the background (the render's flat
    grey) keyed out."""
    im = np.asarray(Image.open(lp(path)).convert("RGBA"))
    c = NATIVE_CELL * NATIVE_Z
    out = []
    for k in range(n):
        cell = im[(k // cols) * c:(k // cols + 1) * c, (k % cols) * c:(k % cols + 1) * c]
        cell = cell[NATIVE_Z // 2::NATIVE_Z, NATIVE_Z // 2::NATIVE_Z].copy()
        bg = cell[1, 1, :3].astype(int)
        key = np.abs(cell[..., :3].astype(int) - bg).sum(-1) < 12
        cell[key] = 0
        out.append(cell)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skel", required=True, help="native_pose's renata_native_run.png")
    a = ap.parse_args()
    run = native_frames(a.skel)
    sheet = np.zeros((2 * CH, 4 * CW, 4), np.uint8)
    for n, f in enumerate(run):
        ys, xs = np.nonzero(f[..., 3] > 0)
        crop = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        h, w = crop.shape[:2]
        Y, X = (n // 4) * CH + FEET - h + 1, (n % 4) * CW + (CW - w) // 2
        m = crop[..., 3] > 0
        sheet[Y:Y + h, X:X + w][m] = crop[m]
    # our idle (hands empty, the pistol tucked), its first frame, in the same cell
    acts, _ = R.actions()
    d = acts["idle"][0][0]
    ys, xs = np.nonzero(d[..., 3])
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cell = np.zeros((CH, CW, 4), np.uint8)
    dy, dx = FEET - d.shape[0] + 1, (CW - d.shape[1]) // 2
    m = d[..., 3] > 0
    cell[dy:dy + d.shape[0], dx:dx + d.shape[1]][m] = d[m]
    os.makedirs(lp(OUT), exist_ok=True)
    up(on_key(sheet)).save(lp(os.path.join(OUT, "1_动作骨架_联盟走路.png")))
    up(on_key(cell)).save(lp(os.path.join(OUT, "2_角色_烈娜塔定稿.png")))
    with open(lp(os.path.join(OUT, "PROMPT.md")), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    os.makedirs(lp(os.path.dirname(ZIP)), exist_ok=True)
    with zipfile.ZipFile(lp(ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(lp(OUT))):
            z.write(lp(os.path.join(OUT, n)), "renata_run_swap_pack/" + n)
    print(ZIP, "sheet", sheet.shape[:2], "x", Z, "design", d.shape[:2])


if __name__ == "__main__":
    main()
