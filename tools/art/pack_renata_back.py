"""Renata's folded machine pack for Codex: the user, 2026-10-17, after the effects: 「感觉不放大招时候背后没武器有点奇怪啊 和
英雄联盟有点不一样」, then 「照原版大小，Codex 画折叠的机甲，你按原版每帧的位置摆进去」「不对缩小一点」.

League's Renata always carries her chemtech machine (skin0.bin hides only Wing, Q_Arm, Pocket, Recall_Jacket,
Q_Arm_Tubes and Potion at spawn; Weapon, Weapon_Glass, Canisters, Canister_Glass and Wing_Folded stay, every clip
animates their joints from Weapon_Ground_Root): a dark machine with a pink glass tank and a red spout, its two
mechanical wings folded up and back and a long spike hanging below, floating behind and above her head. It unfolds
only in her R (our ult frames already hold the unfolded machine, hd/machine.png). The reference renders hid it (my
mistake in assets/source/renata/poses.json), so the design never had it.

The pack: image 1 = our approved idle (the hd frame, her fine squares, 8x on green); image 2 = where and how big: League's
machine rendered at our head and body proportions (tools/lol/native_pose.py, chibi head 2.0, legs 0.85, 54 squares
crown to soles, the machine painted as its own part), SHRINK of its size about its middle, laid behind her where
League has it (soles and head column matched); image 3 = League's machine close up (the 8x render); image 4 = our ult's
unfolded machine (the same machine: its colours and materials). Codex draws the folded machine on image 1 in our pixel
style and delivers the idle with it and the machine alone at the same place; rig_renata.py then moves it whole frame
by frame where League's clips have it (tools/art/import_renata_back.py).

    python tools/lol/native_pose.py C:/t/rn_np/robot2_spec.json --out C:/t/rn_np/robot2 --alpha --parts
    python tools/art/pack_renata_back.py --league C:/t/rn_np/robot2
"""
import argparse
import json
import os
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig_renata as R  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rn_work", "back")
OUT = os.path.join(TMP, "renata_back_machine_pack")
ZIP = os.path.join(R.ROOT, "dist", "renata_packs", "renata_back_machine_pack.zip")
SHEET = os.path.join(R.ROOT, "league", "champions", "league_renata")
SHRINK = 0.8                     # the user: 「缩小一点」 (League's size was offered first)
Z = 8                            # screen px a square in the pack's pictures
KEY = (0, 255, 0)
TOP, SIDE, BOTTOM = 34, 14, 4    # clear squares round her idle for the machine

PROMPT = """# 烈娜塔 背后的折叠机甲（画到定稿待机上）

上传顺序：图1 = `1_定稿待机.png`，图2 = `2_位置和大小.png`，图3 = `3_原版机甲.png`，图4 = `4_大招机甲.png`。请把压缩包解压到一个新的文件夹，只用这个包里的图。

---

英雄联盟里烈娜塔**平时就带着她的化学科技机甲**：机甲悬浮在她**身后、头顶上方**，两只机械翼**折起来朝上、朝后**，机身下面垂着一根长尖杆；只有放大招时机翼才展开（我们大招动作里已经有展开的样子，见图4）。我们的定稿漏了这台机甲，请把它补上。

1. 在**图1**（定稿的待机，每格 8 像素，一格一种颜色）上，把**折叠状态的机甲**画在她**身后**：**位置和大小照图2**（图2是英雄联盟原版的机甲按我们的头身比例渲染、缩到 80% 后放在原版的位置上；只是位置大小参考，画风不要照它）。
2. 机甲的**样子照图3**（英雄联盟原版的折叠机甲）：深色的机身、粉色发光的玻璃罐、顶上一个红色尖罩、两只折起来朝上朝后的机械翼（白银色的爪子）、机身下垂着一根长尖杆、几根红金色的管子。
3. **颜色和材质照图4**（我们大招里展开的同一台机甲：金色甲片、深红、品红发光线条、深藏青）：折叠的机甲和展开的必须看得出是同一台。
4. 机甲在她**身后**：和她重叠的地方被她的头发、身体挡住（**烈娜塔本人一个格子都不要改**，她身上的每一格都和图1一模一样）。
5. 像素画：和图1同样的格子大小（每格 8 像素、整齐对格），1 格深色描边，不要抗锯齿、不要渐变、不要模糊；机甲的轮廓清楚，在游戏里很小也认得出。
6. 背景纯绿 `#00FF00`。

交付（放在 `outputs/renata-back/`，打包成 `renata_back_machine_done.zip`，附 `HANDOFF.md`）：
- `renata_idle_machine.png`：带机甲的待机，**和图1同样大小**（同样的画布、她在同样的位置）。
- `renata_machine_folded.png`：**只有机甲**，同样大小、同样位置，其余纯绿（被她挡住的那部分机甲也要画完整：我会把它放到她身后，每个动作里整块移动）。
"""


def lp(p):
    return R.lp(p)


def up(a, z=Z):
    return Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))


def on_key(a):
    out = np.zeros(a.shape[:2] + (3,), np.uint8)
    out[:] = KEY
    m = a[..., 3] > 0
    out[m] = a[m][:, :3]
    return out


def trim(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def our_idle():
    """The hd idle's first frame as the game shows it (fine squares), trimmed."""
    an = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = np.asarray(Image.open(lp(SHEET + "#sheet.png")).convert("RGBA"))
    r = an["hd_idle"]["frames"][0]["data"]
    x, y, w, h = int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"])
    return trim(sh[y:y + h, x:x + w].copy())


def league(path):
    """League's idle (first frame) at our proportions: (her pixels, machine pixels, machine mask, head x, soles row) on
    the render's native grid (one cell)."""
    c = json.load(open(os.path.join(path, "renata_cells.json")))
    CW, CH = c["cell"]
    zz = c["scale"]
    fr = c["tags"]["idle"][0]
    nat = np.asarray(Image.open(os.path.join(path, "renata_native_idle.png")).convert("RGBA"))[:CH * zz, :CW * zz]
    parts = np.asarray(Image.open(os.path.join(path, "renata_parts_idle.png")).convert("RGBA"))[:CH * zz, :CW * zz]
    cell = nat[zz // 2::zz, zz // 2::zz].copy()
    bg = cell[1, 1, :3].astype(int)
    cell[np.abs(cell[..., :3].astype(int) - bg).sum(-1) < 12] = 0
    g = (parts[..., 1] > 200) & (parts[..., 0] < 60) & (parts[..., 2] < 60) & (parts[..., 3] > 128)
    gm = g.reshape(CH, zz, CW, zz).mean(axis=(1, 3)) >= 0.5
    ys = np.nonzero(cell[..., 3] > 0)[0]
    return cell, gm, fr["head"][0], int(ys.max()) + 1


def shrink(px, mask, k):
    """The machine's pixels scaled by k about their middle (nearest: every source square kept whole or dropped)."""
    ys, xs = np.nonzero(mask)
    cy, cx = ys.mean(), xs.mean()
    sub = np.zeros_like(px)
    sub[mask] = px[mask]
    H, W = mask.shape
    yy, xx = np.mgrid[0:H, 0:W]
    sy = np.clip(np.round(cy + (yy - cy) / k).astype(int), 0, H - 1)
    sx = np.clip(np.round(cx + (xx - cx) / k).astype(int), 0, W - 1)
    out = sub[sy, sx]
    out[~mask[sy, sx]] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--league", required=True, help="native_pose.py's output for C:/t/rn_np/robot2_spec.json")
    a = ap.parse_args()
    her = our_idle()
    cell, gm, head_x, soles = league(a.league)
    machine = shrink(cell, gm, SHRINK)
    # League's figure without the machine, to find its head column like ours: the head joint's column
    h, w = her.shape[:2]
    can = np.zeros((h + TOP + BOTTOM, w + 2 * SIDE, 4), np.uint8)
    # our head's middle column: the design's head rows (0..12 of the body) in the trimmed frame
    hy0 = 0
    hcols = np.nonzero(her[hy0:hy0 + 13, :, 3].any(0))[0]
    our_head_x = SIDE + (hcols.min() + hcols.max()) / 2.0
    our_soles = TOP + h
    ys, xs = np.nonzero(machine[..., 3] > 0)
    dx = int(round(our_head_x - head_x))
    dy = int(round(our_soles - soles))
    for y, x in zip(ys, xs):
        Y, X = y + dy, x + dx
        if 0 <= Y < can.shape[0] and 0 <= X < can.shape[1]:
            can[Y, X] = machine[y, x]
    guide = can.copy()
    m = her[..., 3] > 0
    guide[TOP:TOP + h, SIDE:SIDE + w][m] = her[m]
    plain = np.zeros_like(can)
    plain[TOP:TOP + h, SIDE:SIDE + w][m] = her[m]
    mys, mxs = np.nonzero(can[..., 3] > 0)
    print(f"canvas {can.shape[1]}x{can.shape[0]} squares; her {w}x{h}; the machine {mxs.max() - mxs.min() + 1}x"
          f"{mys.max() - mys.min() + 1} squares at x {mxs.min()}-{mxs.max()}, y {mys.min()}-{mys.max()} (x{SHRINK})")
    if mys.min() < 1 or mxs.min() < 1 or mxs.max() > can.shape[1] - 2:
        sys.exit("the machine runs off the canvas: widen TOP / SIDE")
    os.makedirs(lp(OUT), exist_ok=True)
    up(on_key(plain)).save(lp(os.path.join(OUT, "1_定稿待机.png")))
    up(on_key(guide)).save(lp(os.path.join(OUT, "2_位置和大小.png")))
    # League's machine close up: the 8x render of the idle's first cell, the machine's box
    c = json.load(open(os.path.join(a.league, "renata_cells.json")))
    CW, CH = c["cell"]
    zz = c["scale"]
    pose = np.asarray(Image.open(os.path.join(a.league, "renata_pose_idle.png")).convert("RGBA"))[:CH * zz, :CW * zz]
    gys, gxs = np.nonzero(gm)
    crop = pose[max(0, gys.min() * zz - 40):(gys.max() + 1) * zz + 40, max(0, gxs.min() * zz - 40):(gxs.max() + 1) * zz + 40]
    bg = Image.new("RGBA", (crop.shape[1], crop.shape[0]), (104, 112, 72, 255))
    bg.alpha_composite(Image.fromarray(np.ascontiguousarray(crop)))
    bg.convert("RGB").save(lp(os.path.join(OUT, "3_原版机甲.png")))
    up(on_key(trim(R.MACHINE.copy())), 6).save(lp(os.path.join(OUT, "4_大招机甲.png")))
    with open(lp(os.path.join(OUT, "PROMPT.md")), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    with open(lp(os.path.join(OUT, "place.json")), "w", encoding="utf-8") as f:
        json.dump({"canvas": [can.shape[1], can.shape[0]], "her_at": [SIDE, TOP], "her": [w, h], "shrink": SHRINK,
                   "machine_box": [int(mxs.min()), int(mys.min()), int(mxs.max()), int(mys.max())]}, f, indent=1)
    os.makedirs(lp(os.path.dirname(ZIP)), exist_ok=True)
    with zipfile.ZipFile(lp(ZIP), "w", zipfile.ZIP_DEFLATED) as zf:
        for n in sorted(os.listdir(lp(OUT))):
            zf.write(lp(os.path.join(OUT, n)), "renata_back_machine_pack/" + n)
    print(ZIP)


if __name__ == "__main__":
    main()
