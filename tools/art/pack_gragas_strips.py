#!/usr/bin/env python3
"""Build gragas_strips_pack.zip: step 2 of Gragas's sprite - Codex draws the action strips from the approved design
(design/front.txt -> assets/source/native/gragas_native.png, tools/art/trace_gragas.py + patch_gragas_front.py; the user:
「没问题 可以下一步」).

    python tools/art/pack_gragas_strips.py [--render] [--out DIR]

Every action in the 3/4 FRONT view of the design (the user, 2026-10-12: 「全部 3/4 正面」 - not side-on like the pack's
other heroes), drawn straight at game size (「直接画游戏尺寸」): one 8x8 block per game pixel, the design's 22 colours.
--render first runs tools/lol/native_pose.py on assets/source/gragas/poses.json into %TEMP%/gr_work/pose_n (League's
clips at game size and as 8x renders, gragas_cells.json; camera yaw 30 mirrored as the design, chibi head 1.2, the design
pose is League's idle1 at 0 ms). The keg stays on his back except where the prompts say (W's drink: hoisted to his
mouth); the barrels he throws (Q, R) are effects, not drawn.
The pack (%TEMP%/gr_work/strips/gragas_strips_pack, zipped next to it or into --out): MODEL_STRIPS.md, design/,
gragas_idle.png (already built), now/, pose/ (Riot's model: local only), guide/, gragas_cells.json, refs/.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VR = os.path.dirname(os.path.dirname(HERE))
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gr_work")
NT = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "nt_work")      # oppi's sprites and the pack views (Nautilus)
POSE = os.path.join(TMP, "pose_n")
PACK = os.path.join(TMP, "strips", "gragas_strips_pack")
ZIP = os.path.join(TMP, "strips", "gragas_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "gragas")
DESIGN = os.path.join(VR, "assets", "source", "native", "gragas_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
DRAFT = os.path.join(SRC, "codex_model", "raw", "gragas-front-A-raw.png")   # the raw the design is traced from (2:1)
Z = 8
FEET = 11                       # the soles' row under the pivot
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99, column 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
RELEASE = {}
# the head on the canvas (table row r, column c -> canvas (56 + r, 44 + c)): the bald dome, the brows, the eyes, the nose
# and the moustache (table rows 1-10, columns 14-29) - not the beard below it nor the keg
HEAD_BOXES = [(57, 66, 58, 73)]
REFS = {
    "style_oppi_galio.png": os.path.join(NT, "oppi", "galio_z5.png"),
    "style_oppi_sion.png": os.path.join(NT, "oppi", "sion_z.png"),
    "style_oppi_alistar.png": os.path.join(NT, "oppi", "ali_z.png"),
    "style_oppi_cho.png": os.path.join(NT, "oppi", "cho_z.png"),
    "style_oppi_vi.png": os.path.join(NT, "oppi", "vi_z.png"),
    "style_pack_heroes.png": os.path.join(NT, "review", "pack_views.png"),
}
# League's turned body: (tag, 0-based frame) cells cut from the pose renders
TURNED = [("idle", 0), ("run", 1), ("attack", 2), ("skill", 2), ("skill2", 2), ("skill2", 5), ("ult", 2), ("dead", 3)]


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def at1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def hexs(c):
    return "#%02X%02X%02X" % tuple(int(v) for v in c[:3])


def rgb(h):
    return np.array([int(h[k:k + 2], 16) for k in (1, 3, 5)], np.uint8)


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def palette_img(cols):
    font = ImageFont.load_default(size=22)
    rows = (len(cols) + 5) // 6
    im = Image.new("RGB", (6 * 170, rows * 70), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(cols):
        x, y = (i % 6) * 170, (i // 6) * 70
        d.rectangle([x + 6, y + 6, x + 60, y + 60], fill=tuple(int(v) for v in rgb(c)), outline=(0, 0, 0))
        d.text((x + 68, y + 22), c, fill=(0, 0, 0), font=font)
    return im


def guide(cells, tag, shadow):
    """Cells, standing points (blue), the feet line (red, the band under it may not be drawn on) and the frame numbers,
    over a faint shadow of the reference."""
    cw, ch = cells["cell"]
    frs = cells["tags"][tag]
    cols, rows = layout(len(frs))
    out = Image.new("RGBA", (cols * cw * Z, rows * ch * Z), (255, 255, 255, 255))
    d = ImageDraw.Draw(out)
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * cw * Z, (i // cols) * ch * Z
        fy = Y + (fr["pivot"][1] + FEET + 1) * Z
        d.rectangle([X, fy, X + cw * Z - 1, Y + ch * Z - 1], fill=(255, 214, 214, 255))
        d.line([X, fy, X + cw * Z - 1, fy], fill=(220, 30, 30, 255), width=4)
    sh = np.asarray(shadow.convert("RGBA")).copy()
    bg = (np.abs(sh[..., :3].astype(int) - 225).sum(-1) == 0) | (sh[..., 3] == 0)
    sh[..., :3] = 90
    sh[..., 3] = np.where(bg, 0, 60)
    out.alpha_composite(Image.fromarray(sh))
    d = ImageDraw.Draw(out)
    font = ImageFont.load_default(size=40)
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * cw * Z, (i // cols) * ch * Z
        d.rectangle([X, Y, X + cw * Z - 1, Y + ch * Z - 1], outline=(40, 40, 40, 255), width=3)
        px, py = X + fr["pivot"][0] * Z + Z // 2, Y + fr["pivot"][1] * Z + Z // 2
        d.line([px - 40, py, px + 40, py], fill=(30, 90, 220, 255), width=4)
        d.line([px, py - 40, px, py + 40], fill=(30, 90, 220, 255), width=4)
        d.text((X + 16, Y + 10), f"{i + 1:02d}", fill=(40, 40, 40, 255), font=font)
    return out.convert("RGB")


def ticks(ms_list, k):
    """The tick (60 per second) frame k (1-based) starts on."""
    return int(round(sum(ms_list[:k - 1]) * 60 / 1000))


def turned(cells):
    """League's frames side by side (the body turned to the right in every action), cut from the pose renders."""
    cw, ch = cells["cell"]
    tiles = []
    for tag, k in TURNED:
        im = Image.open(os.path.join(POSE, f"gragas_pose_{tag}.png")).convert("RGB")
        cols, _ = layout(len(cells["tags"][tag]))
        X, Y = (k % cols) * cw * Z, (k // cols) * ch * Z
        t = im.crop((X + 192, Y + 160, X + cw * Z - 192, Y + ch * Z - 120))
        tiles.append((f"{tag} {k + 1}", t.resize((t.width // 2, t.height // 2), Image.LANCZOS)))
    out = Image.new("RGB", (sum(t.width for _, t in tiles), tiles[0][1].height + 30), (225, 225, 225))
    d = ImageDraw.Draw(out)
    font = ImageFont.load_default(size=20)
    x = 0
    for name, t in tiles:
        out.paste(t, (x, 30))
        d.text((x + 8, 4), name, fill=(0, 0, 0), font=font)
        x += t.width
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack)")
    a = ap.parse_args()
    zpath = os.path.join(a.out, os.path.basename(ZIP)) if a.out else ZIP
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "gragas_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    with open(lp(SPEC), encoding="utf-8") as f:
        spec = json.load(f)
    for tag, t in spec["tags"].items():
        if "release" in t:
            RELEASE[tag] = t["release"]
    cw, ch = cells["cell"]
    if os.path.exists(PACK):
        shutil.rmtree(PACK)
    for sub in ("design", "now", "pose", "guide", "refs"):
        os.makedirs(os.path.join(PACK, sub))

    des = at1x(DESIGN)
    op = des[..., 3] > 0
    ys, xs = np.nonzero(op)
    assert ys.max() == PIVOT[1] + FEET, ys.max()
    pal = [hexs(c) for c in sorted({tuple(int(v) for v in c[:3]) for c in des[op]}, key=lambda c: (sum(c), c))]
    head = np.zeros(op.shape, bool)
    for r0, r1, c0, c1 in HEAD_BOXES:
        head[r0:r1 + 1, c0:c1 + 1] = op[r0:r1 + 1, c0:c1 + 1]
    up(des).save(os.path.join(PACK, "design", "gragas_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "gragas_design_1x.png"))
    part = np.zeros_like(des)
    part[head] = des[head]
    up(part).save(os.path.join(PACK, "design", "gragas_head.png"))
    palette_img(pal).save(os.path.join(PACK, "design", "gragas_palette.png"))

    # the idle strip: the design at every idle frame's standing point
    frs = cells["tags"]["idle"]
    cols, rows = layout(len(frs))
    idle = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    crop = des[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    for i, fr in enumerate(frs):
        tx = (i % cols) * cw + fr["pivot"][0] - PIVOT[0] + xs.min()
        ty = (i // cols) * ch + fr["pivot"][1] - PIVOT[1] + ys.min()
        reg = idle[ty:ty + crop.shape[0], tx:tx + crop.shape[1]]
        m = crop[..., 3] > 0
        reg[m] = crop[m]
    up(idle).save(os.path.join(PACK, "gragas_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"gragas_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"gragas_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"gragas_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(os.path.join(PACK, "guide", f"gragas_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None)
    with open(os.path.join(PACK, "gragas_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "gragas_draft_codex.png"))
    for name, src in REFS.items():
        shutil.copyfile(lp(src), os.path.join(PACK, "refs", name))
    turned(cells).save(os.path.join(PACK, "refs", "lol_turned_body.png"))

    doc = document(pal, tags, (crop.shape[1], crop.shape[0]), (cw, ch))
    for path in (os.path.join(PACK, "MODEL_STRIPS.md"), DOC):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    for tag, t in tags.items():
        print(f"{tag:9s} {t['n']} frames {t['ms']} {t['cols']}x{t['rows']} {t['size'][0]}x{t['size'][1]} R {t['R']}"
              + (f" release frame {t['release']} tick {t['tick']}" if t["release"] else ""))
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(PACK):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                zf.write(p, os.path.join("gragas_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
    print(zpath, os.path.getsize(zpath) // 1024, "KB")


LEGS_TXT = ("the design's own legs in the design's 3/4 FRONT view - short thick bare legs with the brown rope tied under each "
            "knee and big bare feet with clear toes, the near leg on the image left, the far leg on the image right a shade "
            "darker - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken "
            "into scraps); a bent knee is drawn as a bent leg; standing or braced frames plant both feet flat on the feet line, "
            "a lunge steps the front foot forward to the image right")
BODY_TXT = ("the head keeps the design's size, colours and details (the bald dome with its highlight, the bushy orange-red "
            "brows, the eyes - a white and a dark pupil each, looking right - the big nose, the moustache) and the SAME 3/4 "
            "front angle as the design in every frame, turned a little more to the right only when he lunges; the huge round "
            "belly with its red X scar, the long orange-red beard with its silver ring, the rope across his chest, the "
            "dark-blue ragged shorts stay on him in every frame; the design's body is never redrawn thinner or taller")
ARMS_TXT = ("the arms are the design's arms - very thick bare arms with the brown rope round the forearms and wrists and the "
            "HUGE fists - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its "
            "shoulder; the KEG on his back is ONE rigid object with exactly the design's shape and size (warm brown staves, the "
            "grey iron hoops, the round lid with its iron ring and the square cork): it stays on his back in every frame "
            "except the drink (W), where it is moved and turned whole, drawn clean at every angle like oppi draws Sion's axe "
            "(refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; the "
            "barrels he THROWS (Q, R) fly as effects and are NOT drawn")
ANIM = {
    "run": "RUN, 8 frames, one seamless loop (League's run, 0.92 s), in the design's 3/4 front view: a heavy waddle - the "
           "keg bouncing on his back, the belly and the beard swinging a little, the fists pumping at his sides; the legs "
           "STEP: in frames 1 and 5 the feet are furthest apart (frame 1 the near foot forward, frame 5 the far foot forward), "
           "in frames 3 and 7 the lifted foot passes beside the other 1-2 rows up with the knee bent; the body bobs 1 row with "
           "each landing; his head keeps the same place across the cell relative to the standing point in all 8 frames; "
           "frame 8 flows into frame 1.",
    "attack": "BASIC ATTACK (a big right hook), 5 frames: 1 turning his shoulders to the right, the near fist drawn back by "
              "his hip; 2 winding up, the near fist swung back and up behind his shoulder, the belly leaning back; 3 THE PUNCH "
              "(the blow lands here): lunging to the image right, the front knee bent, the near fist thrown forward to the "
              "right at chest height, the arm the design's length; 4 following through, the fist past the target, the belly "
              "swinging after it; 5 back toward the stance.",
    "skill": "BARREL ROLL (Q, a barrel thrown), 5 frames: 1 reaching back with the near hand as if taking a small barrel from "
             "the keg (the hand empty: the barrel is an effect); 2 winding up, the near arm drawn back and down behind him, "
             "the body crouched and twisted; 3 THE THROW (the barrel leaves here): the near arm swung forward and up to the "
             "image right underhand, the hand open and empty, the front foot stepping forward; 4 following through, the arm "
             "high in front of him; 5 back toward the stance. The keg stays on his back in every frame.",
    "skill2": "BODY SLAM then DRUNKEN RAGE (E, then W), 8 frames: 1 crouching, the near shoulder lowered toward the image "
              "right; 2 CHARGING: the whole body thrown forward to the right, belly first, the near shoulder leading, the "
              "back leg pushing; 3 THE SLAM (the hit lands here): the belly and the near shoulder slammed forward, the body "
              "squashed a little forward (the same size), the beard flying; 4 rebounding upright; 5 reaching back and lifting "
              "the KEG off his back over his far shoulder; 6-7 DRINKING: the keg tipped up over his head and shoulder, its "
              "open end at his mouth (League's W: the keg hoisted, both hands on it), the head tilted back; 8 lowering the keg "
              "back onto his back, toward the stance.",
    "ult": "EXPLOSIVE CASK (R, a cask hurled), 5 frames: 1 both fists raised, the body rearing back; 2 winding up, the near "
           "arm drawn far back over his shoulder as if holding a cask (the hand empty: the cask is an effect), the belly "
           "out, the far hand forward; 3 THE HURL (the cask leaves here): the near arm whipped forward and down to the image "
           "right, the hand open, the body lunging; 4 following through, bent forward; 5 rising toward the stance. The keg "
           "stays on his back.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the belly "
           "wobbling; 2 recovering toward the stance. The design's legs.",
    "dead": "DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 staggering, a hand on his belly; 3-4 sinking to his knees, "
            "dizzy; 5-6 toppling over backward onto his back, the keg rolling off beside him; 7-8 lying still on his back, the "
            "belly up, the keg on the ground beside him. Nothing below the feet line, never upside down.",
}
ZH = {"idle": "待机", "run": "跑步（3/4 正面，酒桶在背上颠）", "attack": "普攻（右勾拳）", "skill": "Q 滚动酒桶（下手抛出，桶是特效）",
      "skill2": "E 肉弹冲击（肚子撞）+ W 醉酒狂暴（扛桶喝）", "ult": "R 爆破酒桶（抡臂掷出，桶是特效）",
      "hit": "受击", "dead": "死亡（仰面倒地）"}


def document(pal, tags, size, cell):
    w, h = size
    cw, ch = cell
    rows = []
    for tag in TAGS:
        t = tags[tag]
        ms = f"{t['n']} × {t['ms'][0]}" if len(set(t["ms"])) == 1 else f"{t['n']} 帧：" + " ".join(map(str, t["ms"]))
        rel = f"第 {t['release']} 帧（tick {t['tick']}）" if t["release"] else "—"
        lay = f"{t['cols']} 列 × {t['rows']} 行，{t['size'][0]}×{t['size'][1]}" + (f"，最后 {t['empty']} 格空" if t["empty"] else "")
        anim = "**已做好，不用画**" if tag == "idle" else f"`{ANIM[tag]}`"
        rows.append(f"| `gragas_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    return DOC_TEXT.format(table="\n".join(rows), pal_txt=" ".join(pal), n=len(pal), w=w, h=h, cwZ=cw * Z, chZ=ch * Z,
                           LEGS_TXT=LEGS_TXT, BODY_TXT=BODY_TXT, ARMS_TXT=ARMS_TXT, sole=PIVOT[1] + FEET,
                           a_tick=tags["attack"]["tick"], q_tick=tags["skill"]["tick"], e_tick=tags["skill2"]["tick"],
                           r_tick=tags["ult"]["tick"])


DOC_TEXT = """# 古拉加斯（酒桶）：按定稿造型画动作帧——3/4 正面版（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户定稿的是 `design/gragas_design.png`（放大 8 倍，1024×1024；{w} 格宽、{h} 行高，{n} 色；脚底在第 {sole} 行，站位点在第 64 列）——从你上一轮画的原稿 `refs/gragas_draft_codex.png`（front-A）按 2:1 逐格描下来的（用户：「没问题 可以下一步」）。**造型图就是标准**：光头（头顶一格高光）、橙红浓眉、一格眼白一格瞳孔的眯眼（看向右边）、大鼻子、橙红长胡子（带银环）、超大圆肚子和红色 X 疤、胸前斜挂的棕绳、手臂和膝下缠的棕绳、超大拳头、深蓝锯齿短裤、光脚；背上一只大木酒桶（暖棕木板、灰铁箍、带铁环和方木塞的圆桶盖）。颜色、明暗，每一帧都照它，只改姿势。
> **这个英雄所有动作都是 3/4 正面朝右**（和造型图同一个角度，用户：「全部 3/4 正面」），**不要转成侧身**：头、肚子、胡子都和造型图一样朝向观众偏右，出招都朝图的右边。英雄联盟的动作就是这个角度渲染的（`pose/`）。
> **直接画游戏尺寸**（用户：「直接画游戏尺寸」）：和造型图一样大，每个游戏像素就是一个 8×8 纯色块。**不要先画大图再缩**——前几轮你的生图原稿都画成每格 12–15 px 的大图，缩回来全是糊的碎点；这一轮**生成后先量格子大小**，不是 8 px 一格（在 1024 的格子里）就重画，或者一帧一帧单独生成。
> - **待机条已经做好**（`gragas_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/gragas_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、身体和酒桶的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **和参考图不一样、以造型图为准的地方**：① 照造型图的比例（头比英雄联盟的大一点，肚子一样大）；② **酒桶一直背在背上**，只有 W 喝酒时整只桶举到嘴边；**Q 和 R 扔出去的桶是特效，不画**（手是空的）；③ **不画背影、不倒立、不转侧身**；④ **腿**：{LEGS_TXT}；⑤ **手臂和酒桶**：{ARMS_TXT}；⑥ **身上**：{BODY_TXT}；⑦ 脚底线以下什么都不能有。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/gragas_now_<动作>.png`（骨架），图2 = `design/gragas_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/gragas-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和所有生图原稿（`raw/`，不要重采样），最好打成一个 zip（`gragas_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/gragas_palette.png`，或直接读 `design/gragas_design_1x.png`）。
4. 对位：每帧按 `gragas_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
5. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/gragas_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 {sole} 行 | 每张动作图的第一张附图 |
| `design/gragas_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板 |
| `design/gragas_head.png` | 造型图的头（光头、眉、眼、鼻、胡子上沿），8 倍 | 看头的大小和细节 |
| `design/gragas_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `gragas_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/gragas_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、身体和酒桶的动作 |
| `guide/gragas_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `gragas_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/gragas_draft_codex.png` | 你上一轮画的原稿 front-A（造型就是从它描的） | 长相参考（大小以定稿为准） |
| `refs/style_oppi_*.png`、`refs/style_pack_heroes.png` | oppi 的手绘精灵、本包已经做好的英雄：**要学的标准**——每帧同一个人、同样大小，道具每个角度都是同一件（这个英雄不转侧身） | 风格 |
| `refs/lol_turned_body.png` | 英雄联盟里酒桶的待机和各动作 | 动作的样子 |

## 规则（每张都一样）

- **和造型图一样的像素**：和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：{LEGS_TXT}。
- **手臂和酒桶**：{ARMS_TXT}。
- **身上**：{BODY_TXT}。
- **脚底线以下什么都不能有**（游戏在这条线下画血条）。
- **跑步循环**：酒桶一直在背上；每帧头相对站位点的横向位置不变；两只脚真正交替前后；上下起伏最多 1 格；首尾能无缝接上。
- 出招朝图的右边，**3/4 正面、不画背影、不画倒立、不转侧身**。**只画角色本身**：扔出去的桶、酒水、泡沫、冲击、发光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/gragas_design.png`，第二张 `now/gragas_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `gragas_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, keg, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose, drawn by hand like oppi's sprites, in the SAME 3/4 FRONT VIEW as the FIRST image (facing the viewer, turned a little to the image right) - NOT side-on. The same bald head with its highlight, bushy orange-red brows, squinting eyes (a white and a dark pupil each, looking right), big nose, the long orange-red beard with its silver ring, the huge round belly with the red X scar, the brown rope across his chest and round his forearms, wrists and below the knees, the HUGE fists, the dark-blue ragged shorts, the bare feet, and the big wooden keg on his back (warm brown staves, grey iron hoops, a round lid with an iron ring and a square cork), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the body and the keg from it, with the FIRST image's proportions, colours and details; every cast goes to the RIGHT of the image; never draw him from the back, side-on or upside down.
The character: Gragas, the Rabble Rouser (a huge, jolly, drunken brawler with a keg on his back).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. Draw at this game size directly: never draw bigger and shrink.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Consistency: within an animation the head, the body, the legs, the arms and the keg keep the same size and shape in every frame; the whole figure may lean, lunge, crouch or rear back.
Legs: {LEGS_TXT}.
The arms and the keg: {ARMS_TXT}.
The body: {BODY_TXT}.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in gragas_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 front view facing the image right as in the FIRST image; every cast goes to the RIGHT of the image; never his back, never side-on, never upside down. Do not draw effects (thrown barrels or casks, beer, foam, impact rings, sparks, glows) - only the character and his keg. Every animation starts and ends near the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x128 squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, every frame in the 3/4 front view, the head the design's size, both arms growing from the shoulders in every frame and never longer than the design's, the fists empty when he throws, the keg rigid and full size on his back (in his hands only for the drink), the legs the same thickness in every frame, the run's feet swapping front and back, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小，直接画这个尺寸，不要先画大图再缩。
2. 保留每一帧的动作：角度和图2一样是 3/4 正面朝右（不转侧身），手臂、身体和酒桶的方向和姿势照图1（出招都朝图的右边，不画背影、不倒立）；头、身体和腿的颜色、细节、大小用图2的。
3. 长相、配色、细节全部换成图2：光头、橙红浓眉、一格眼白一格瞳孔的眯眼、大鼻子、橙红长胡子和银环、超大圆肚子和红色 X 疤、胸前斜挂的棕绳、手臂和膝下的棕绳、超大拳头、深蓝锯齿短裤、光脚、背上的大木酒桶（灰铁箍、圆桶盖、方木塞）。
4. 手臂从肩膀长出来，和图2一样粗、不比图2长；酒桶是一整块、大小形状不变，一直背在背上，只有喝酒（W）时举到嘴边；Q 和 R 扔出去的桶不画，手是空的；任何东西不能低于脚底线。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
{table}

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块（在 1024 的格子里量过），透明度只有 0 和 255；**不是先画大图再缩的**；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 每帧都是 3/4 正面朝右，没有侧身、背影、倒立；头和造型图一样大、细节一样；同一个动作里各部件大小形状不变；
- [ ] 两只手臂都在、和造型图一样粗、不比造型图的手臂长，从肩膀长出来；扔东西的手是空的；酒桶是一整块、没有变小变形，除了喝酒都在背上；
- [ ] 跑步两只脚交替前后、膝盖弯曲，腿每帧一样粗、没有碎块、没有缺格子；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 出招都朝图的右边；出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `gragas_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；身体变形的帧用造型图的部件重摆（酒桶整只只平移和 90° 整转，整个人前倾、前冲、下蹲；不按任意角度转）。
- 放进 `assets/source/native/`，`gragas_cells.json` 用包里这份；待机就是造型图（不加呼吸，BREATHE_SKIP）。
- `import_native.py`：ORDER 待机，COMPLETE 补描边；红色方：有前后之分、贴在他身上的特效烘进动作帧（`gragas_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick {a_tick}、Q tick {q_tick}、E 撞上 tick {e_tick}、R tick {r_tick}），量头像截取点，重跑模拟，做预览 GIF。
"""


if __name__ == "__main__":
    main()
