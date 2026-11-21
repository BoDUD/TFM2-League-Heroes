#!/usr/bin/env python3
"""炼金（league_singed）跑步重画的 Codex 素材包：游戏里的跑步 8 帧两只脚钉在原地、只有前脚跟抬一下，药罐、盾、拿药瓶的手
8 帧几乎不动（用户 2026-11-21：「炼金的跑步动作是不是让codex重画一下比较好」）。照锐雯跑步那一包（pack_riven_actions.py）的
做法：英雄联盟的跑步骨架按我们设计图的身材缩放，画成模板，Codex 按设计图逐帧重画。

    python tools/lol/league_joints.py assets/source/singed/poses.json --out <work>/joints --tag run
    python tools/lol/native_pose.py assets/source/singed/poses.json --out <work>/native --alpha
    python tools/art/pack_singed_run.py --work <work> --out <pack> [--game <游戏目录>]

设计图就是游戏里现在的高清待机第 0 帧（`hd_idle`，PPU 1.39，51 x 95，药罐盖子到脚底 62 格）：没有单独的高清设计稿，
游戏里这一帧就是用户认可过的样子。一格设计图 = 模板里 SQ 像素。

和英雄联盟不一样的地方：英雄联盟里近侧手拿药瓶前后摆、远侧手把带刺的盾举在身前；我们的设计（MODEL_PROMPTS.md）是近侧
（画面左）的手竖着举盾、远侧（画面右）的手拿绿色药瓶。所以模板里拿药瓶的手照英雄联盟药瓶那只手（L）的摆法，从我们远侧
的肩膀算；盾不画标记，提示词里说它跟着身体走、一直竖着。

写出 <pack>/：templates/run_<k>.png（每张三格，最后一张两格）、refs/（设计图 8 倍和 1 倍、调色板、英雄联盟同几帧的渲染、
锐雯认可过的跑步当画法参考）、sheets.json，以及 <pack>.zip。提示词另写（SINGED_RUN_PROMPT.md）。
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
GAME = r"D:\steam\steamapps\common\Teamfight Manager2"

SQ = 8                                   # 模板里一格设计图多少像素
CELL = (512, 1024)
GROUND = 1024 - 150                      # 地面线在格子里的行
PER_SHEET = 3
GREY = (225, 225, 225)
NEAR, FAR = (40, 120, 230), (150, 150, 150)
VIAL = (0, 170, 60)

# 设计图（高清待机第 0 帧）上量的：脚底第 62 行（地面线在它下面一行），骨盆 (26, 45)，脖子 (27, 26)，光头中心 (27.5, 18.5)
# 半径 5.5，远侧肩膀 (33, 27)，药瓶中心 (40, 40.5) 半径 4；药罐盖子顶第 1 行
SOLE_ROW = 62
PELVIS = (26.0, 45.0)
STAND = 62                               # 药罐盖子顶到脚底
STAND_HEAD = 51                          # 光头顶到脚底
HEAD_UP, HEAD_R = 7.5, 5.5
FAR_SHOULDER = (6.0, 1.0)                # 远侧肩膀离脖子的格数
VIAL_R = 4.0
# 英雄联盟待机姿势（singed_idle1@0，游戏像素）对设计图：腿按骨盆高（18 格 / 27.9），躯干按骨盆到脖子（19 格 / 11.3），
# 手臂按臂长（15.2 格 / 13.5）
K_LEG, K_UP, K_ARM = 0.64, 1.69, 1.13
LUNGE = 0.5                              # 骨盆前后的晃动留一半（锐雯同）
# 药瓶手：设计图里在远侧肩膀前下方 (7, 13.5) 格；跑步时照英雄联盟 L 手（药瓶那只）相对待机的摆动，摆幅留 SWING
VIAL_AT = (7.0, 13.5)
ELBOW_AT = (2.0, 7.0)
SWING = 0.6
LEG_BONES = [("pelvis", "l_hip"), ("pelvis", "r_hip"), ("l_hip", "l_knee"), ("l_knee", "l_foot"), ("l_foot", "l_toe"),
             ("r_hip", "r_knee"), ("r_knee", "r_foot"), ("r_foot", "r_toe")]


def font(n):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", n)
    except OSError:
        return ImageFont.load_default()


def his_joints(j, idle):
    """一帧英雄联盟的关节（游戏像素，x 朝前，y 朝下，从站位点算）换成设计图的格数：腿按 K_LEG，躯干按 K_UP，头在脖子
    往上 HEAD_UP 格（顺着英雄联盟脖子的方向）。拿药瓶的手在设计图的位置上，照英雄联盟 L 手（药瓶那只）比待机多出来的
    摆动前后摆（乘 K_ARM 和 SWING）：我们设计里药瓶在远侧手，整条照搬会甩到身体和盾后面看不见。"""
    v = {n: np.array(x[:2], float) for n, x in j.items() if isinstance(x, list)}
    d = {n: np.array(x[:2], float) for n, x in idle.items() if isinstance(x, list)}
    pel = v["pelvis"] * K_LEG * np.array((LUNGE, 1.0))
    out = {"pelvis": pel}
    for n in ("l_hip", "r_hip", "l_knee", "r_knee", "l_foot", "r_foot", "l_toe", "r_toe"):
        out[n] = pel + (v[n] - v["pelvis"]) * K_LEG
    out["neck"] = pel + (v["chest"] - v["pelvis"]) * K_UP
    nk = v["head"] - v["chest"]
    up = nk / (np.linalg.norm(nk) or 1)
    if up[1] > -0.5:                     # 英雄联盟的脖子太短、方向不稳时就直着往上
        up = np.array((0.0, -1.0))
    out["head"] = out["neck"] + up * HEAD_UP
    out["shoulder"] = out["neck"] + np.array(FAR_SHOULDER)
    for n, at in (("elbow", ELBOW_AT), ("vial", VIAL_AT)):
        sw = ((v[f"l_{'elbow' if n == 'elbow' else 'hand'}"] - v["l_shoulder"])
              - (d[f"l_{'elbow' if n == 'elbow' else 'hand'}"] - d["l_shoulder"])) * K_ARM * SWING
        out[n] = out["shoulder"] + np.array(at) + sw
    return out


def template(path, frames, k0, idle):
    """一张模板三格：每格地面线、站位点、站直时的高度条、骨架（腿近蓝远灰、躯干深灰）、头的圈、药瓶手的绿圈。"""
    can = Image.new("RGB", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        Q = his_joints(fr["j"], idle)
        # 高度照英雄联盟：每帧最低的那一点已经贴着地面（native_pose 的 flat 放法），脚踝离地多高就画多高
        P = {n: (cx + q[0] * SQ, GROUND + q[1] * SQ) for n, q in Q.items()}
        dr.rectangle([x0, 0, x0 + CELL[0] - 1, CELL[1] - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + CELL[0] - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 20
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.line([(bx - 8, GROUND - STAND_HEAD * SQ), (bx + 8, GROUND - STAND_HEAD * SQ)], fill=(160, 160, 160), width=3)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "tank cap (standing)", fill=(120, 120, 120), font=font(18))
        dr.text((bx + 12, GROUND - STAND_HEAD * SQ - 10), "top of head", fill=(120, 120, 120), font=font(18))
        for a, b in LEG_BONES:
            near = a.startswith("l_") or b.startswith("l_")
            far = a.startswith("r_") or b.startswith("r_")
            col = NEAR if near and not far else FAR if far and not near else (60, 60, 60)
            dr.line([P[a], P[b]], fill=col, width=6)
        dr.line([P["pelvis"], P["neck"]], fill=(60, 60, 60), width=6)
        dr.line([P["neck"], P["shoulder"]], fill=(60, 60, 60), width=3)
        dr.line([P["shoulder"], P["elbow"]], fill=(120, 200, 140), width=4)
        dr.line([P["elbow"], P["vial"]], fill=(120, 200, 140), width=4)
        hx, hy = P["head"]
        r = HEAD_R * SQ
        dr.ellipse([hx - r, hy - r, hx + r, hy + r], outline=(0, 0, 0), width=3)
        vx, vy = P["vial"]
        r = VIAL_R * SQ
        dr.ellipse([vx - r, vy - r, vx + r, vy + r], outline=VIAL, width=4)
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}", fill=(0, 0, 0), font=font(28))
    can.save(path)


def sheet_frames(game, hero, tag):
    """游戏装着的图集里某个标签的帧（按 fanim 的矩形切）。"""
    base = os.path.join(game, "mods", "league", "champions", hero)
    an = json.load(open(base + "#anim.fanim", encoding="utf-8-sig"))["anims"][tag]["frames"]
    px = Image.open(base + "#sheet.png").convert("RGBA")
    out = []
    for f in an:
        d = f["data"]
        x, y, w, h = (int(round(d[q])) for q in "xywh")
        out.append(px.crop((x, y, x + w, y + h)))
    return out


def design_refs(game, refs):
    """设计图：高清待机第 0 帧，8 倍放在浅灰底上 + 1 倍原图 + 全部颜色。"""
    im = sheet_frames(game, "league_singed", "hd_idle")[0]
    bb = im.getbbox()
    im = im.crop(bb)
    im.save(os.path.join(refs, "design_1x.png"))
    bg = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    bg.alpha_composite(im, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, "design_8x.png"))
    a = np.array(im)
    cols = np.unique(a[a[..., 3] > 0][:, :3], axis=0)
    cols = sorted(cols.tolist(), key=lambda c: sum(c))
    per = 8
    pal = Image.new("RGB", (per * 150, (len(cols) + per - 1) // per * 60), (255, 255, 255))
    dr = ImageDraw.Draw(pal)
    for i, c in enumerate(cols):
        x, y = (i % per) * 150, (i // per) * 60
        dr.rectangle([x + 4, y + 4, x + 50, y + 50], fill=tuple(c), outline=(0, 0, 0))
        dr.text((x + 56, y + 20), "#%02X%02X%02X" % tuple(c), fill=(0, 0, 0), font=font(16))
    pal.save(os.path.join(refs, "design_palette.png"))
    return len(cols)


def style_ref(game, refs):
    """画法参考：锐雯认可过的跑步（Codex 重画、用户点过头的那一版），8 帧 4 倍。"""
    frs = sheet_frames(game, "league_riven", "hd_run")
    w = max(f.width for f in frs)
    h = max(f.height for f in frs)
    can = Image.new("RGBA", ((w + 2) * len(frs), h), GREY + (255,))
    for k, f in enumerate(frs):
        can.alpha_composite(f, (k * (w + 2) + (w - f.width) // 2, h - f.height))
    can.convert("RGB").resize((can.width * 4, can.height * 4), Image.NEAREST).save(os.path.join(refs, "style_run.png"))


def league_frames(pose_png, idx, out, cell=768):
    """native_pose 8 倍渲染图（每行 4 格、每格 cell 像素）里的几帧，裁掉空白排成一行。"""
    im = Image.open(pose_png).convert("RGBA")
    ncol = im.width // cell
    crops = []
    for k in idx:
        c = im.crop(((k % ncol) * cell, (k // ncol) * cell, (k % ncol + 1) * cell, (k // ncol + 1) * cell))
        bb = c.getbbox()
        crops.append(c.crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(cell, bb[2] + 30), min(cell, bb[3] + 30))))
    h = max(c.height for c in crops)
    can = Image.new("RGBA", (sum(c.width for c in crops) + 20 * len(crops), h + 50), GREY + (255,))
    dr = ImageDraw.Draw(can)
    x = 0
    for k, c in zip(idx, crops):
        can.alpha_composite(c, (x, 50 + h - c.height))
        dr.text((x + 10, 8), f"frame {k + 1}", fill=(0, 0, 0), font=font(28))
        x += c.width + 20
    can.convert("RGB").save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="league_joints.py / native_pose.py 的输出目录（joints/、native/）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--game", default=GAME)
    ap.add_argument("--prompt", default=os.path.join(REPO, "assets", "source", "singed", "RUN_PROMPT.md"))
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    joints = json.load(open(os.path.join(a.work, "joints", "singed_joints.json"), encoding="utf-8"))
    frs = joints["tags"]["run"]
    n = design_refs(a.game, refs)
    style_ref(a.game, refs)
    sheets = []
    for k0 in range(0, len(frs), PER_SHEET):
        idx = list(range(k0, min(k0 + PER_SHEET, len(frs))))
        name = f"run_{k0 // PER_SHEET + 1}"
        template(os.path.join(tpl, name + ".png"), [frs[k] for k in idx], k0, joints["design"])
        league_frames(os.path.join(a.work, "native", "singed_pose_run.png"), idx, os.path.join(refs, f"league_{name}.png"))
        sheets.append(dict(name=name, frames=[k + 1 for k in idx], ms=[frs[k]["ms"] for k in idx],
                           league=[frs[k]["frame"] for k in idx]))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET, "design": "hd_idle frame 0",
                   "sheets": sheets}, f, indent=1)
    if os.path.isfile(a.prompt):
        shutil.copyfile(a.prompt, os.path.join(a.out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(f"{len(sheets)} templates, {n} colours in the design; written {zp}")


if __name__ == "__main__":
    main()
