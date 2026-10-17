"""Build khazix_strips_pack.zip: step 2 of Kha'Zix's sprite - Codex draws the action strips from the approved design
(step 1: Codex's own design A, 42 x 45, assets/source/native/khazix_native.png; the user's pick 「用这个吧」).

    python tools/art/pack_khazix_strips.py [--render] [--no-zip] [--out DIR]

--render first runs tools/lol/native_pose.py on assets/source/khazix/poses.json into %TEMP%/pk_work/pose (League's clips
at game size and as 8x renders, khazix_cells.json; camera yaw 30 mirrored, the chibi head 1.6; his final form: the
W spikes taken from Khazix_evo_overrides, the "layer" of poses.json).
The pack (%TEMP%/pk_work/strips/khazix_strips_pack, zipped next to it or into --out):
  MODEL_STRIPS.md               the prompts (also written to assets/source/khazix/MODEL_STRIPS.md)
  design/khazix_design.png, _1x    the approved design at 8x (FIRST image of every prompt) and at 1x
  design/khazix_head.png, _1x    the head alone (the blue face plate, the antenna roots, the eye, the red jaw)
  design/khazix_palette.png        its colours, darkest first, with their hex codes
  khazix_idle.png                  the idle strip, already built: every frame the design at its standing point
  now/khazix_now_<tag>.png         League's clip sampled at game size, 8x (SECOND image)
  pose/lol_pose_<tag>.png        the same frames rendered at 8x (THIRD image; Riot's model: local only)
  guide/khazix_guide_<tag>.png     cells, standing points, the feet line and the no-draw band under it
  khazix_cells.json                standing points and durations (import_native.py cuts the frames with it)
  refs/khazix_picture.png, refs/khazix_draft_codex.png
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
VR = os.path.dirname(os.path.dirname(HERE))                     # the repo
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "kz_work")
POSE = os.path.join(TMP, "pose_n")
PACK = os.path.join(TMP, "strips", "khazix_strips_pack")
ZIP = os.path.join(TMP, "strips", "khazix_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "khazix")
DESIGN = os.path.join(VR, "assets", "source", "native", "khazix_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
PICTURE = os.path.join(SRC, "codex_picture", "khazix-model-B.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "A_pixel_generated.png")
Z = 8
FEET = 11                       # the leg tip's row under the pivot (base sprites' soles)
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99, column 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
RELEASE = {}                    # 1-based frame where the blow lands / the shout goes, per tag (filled from poses.json)
# the head on the design's canvas, by shape: the blue face plate with the antenna roots, the eye and the red jaw - not the
# shoulder plate with its red spots beside it
HEAD_BOXES = [(66, 74, 69, 76), (75, 81, 70, 77)]   # rows r0..r1, columns c0..c1 (inclusive)


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


def parts(des):
    """The head: every opaque square in HEAD_BOXES."""
    op = des[..., 3] > 0
    head = np.zeros(op.shape, bool)
    for r0, r1, c0, c1 in HEAD_BOXES:
        head[r0:r1 + 1, c0:c1 + 1] = op[r0:r1 + 1, c0:c1 + 1]
    return head


def palette_img(cols):
    font = ImageFont.load_default(size=22) if hasattr(ImageFont, "load_default") else None
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
    font = ImageFont.load_default(size=40) if hasattr(ImageFont, "load_default") else None
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack)")
    a = ap.parse_args()
    global ZIP
    if a.out:
        ZIP = os.path.join(a.out, "khazix_strips_pack.zip")
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "khazix_cells.json"), encoding="utf-8") as f:
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
    pal = sorted({tuple(int(v) for v in c[:3]) for c in des[op]}, key=lambda c: (sum(c), c))
    pal = [hexs(c) for c in pal]
    hm = parts(des)
    up(des).save(os.path.join(PACK, "design", "khazix_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "khazix_design_1x.png"))
    for name, m in (("head", hm),):
        part = np.zeros_like(des)
        part[m] = des[m]
        Image.fromarray(part).save(os.path.join(PACK, "design", f"khazix_{name}_1x.png"))
        up(part).save(os.path.join(PACK, "design", f"khazix_{name}.png"))
    hy, hx = np.nonzero(hm)
    hbox = (hx.min(), hy.min(), hx.max(), hy.max())
    palette_img(pal).save(os.path.join(PACK, "design", "khazix_palette.png"))

    # the idle strip: the design at every idle frame's standing point
    frs = cells["tags"]["idle"]
    cols, rows = layout(len(frs))
    idle = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    crop = des[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    for i, fr in enumerate(frs):
        ox, oy = (i % cols) * cw + fr["pivot"][0] - PIVOT[0], (i // cols) * ch + fr["pivot"][1] - PIVOT[1]
        tx, ty = ox + xs.min(), oy + ys.min()
        assert tx >= (i % cols) * cw and ty >= (i // cols) * ch
        assert tx + crop.shape[1] <= (i % cols + 1) * cw and ty + crop.shape[0] <= (i // cols + 1) * ch
        reg = idle[ty:ty + crop.shape[0], tx:tx + crop.shape[1]]
        m = crop[..., 3] > 0
        reg[m] = crop[m]
    up(idle).save(os.path.join(PACK, "khazix_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"khazix_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"khazix_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"khazix_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(
            os.path.join(PACK, "guide", f"khazix_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None)
    with open(os.path.join(PACK, "khazix_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(PICTURE), os.path.join(PACK, "refs", "khazix_picture.png"))
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "khazix_draft_codex.png"))

    doc = document(pal, tags, (crop.shape[1], crop.shape[0]), (cw, ch), hbox)
    for path in (os.path.join(PACK, "MODEL_STRIPS.md"), DOC):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    for tag, t in tags.items():
        print(f"{tag:9s} {t['n']} frames {t['ms']} {t['cols']}x{t['rows']} {t['size'][0]}x{t['size'][1]} R {t['R']}"
              + (f" release frame {t['release']} tick {t['tick']}" if t["release"] else ""))
    if not a.no_zip:
        if os.path.exists(ZIP):
            os.remove(ZIP)
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(PACK):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join("khazix_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
        print(ZIP, os.path.getsize(ZIP) // 1024, "KB")


LEGS_TXT = ("the legs are the design's own insect legs - violet chitin bending BACKWARD at the knee, thin long shins, brown "
            "toe claws - square for square in every standing frame (idle, the attack, Q, W's throw, R, hit): crouched and "
            "apart as in the design, never redrawn as human legs; a cast may move the WHOLE figure 1-3 squares forward or "
            "back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's leap and the "
            "death change them. In the run the legs cross (one in front of the other, the far leg one shade darker so the "
            "two do not melt together), the hips stay under the body, the body bobs 1 row with each landing, and the legs "
            "keep the design's chitin colours and the brown toe claws")
ORB_TXT = ("the pale yellow-green wings, the blue-teal back shell, the brown spiky neck frill and the shoulder plates with "
           "their red-ringed spots stay on him in every frame, the same shapes and sizes as in the design (the wings may "
           "open wider in W and R, as one piece each)")
ARMS_TXT = ("the arms are the design's arms: violet chitin, the same thickness as in the design (never thinner, never "
            "1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); an arm moves as "
            "ONE piece with its scythe claw, turned whole in steps of 45 degrees - never bent like a rubber hose, never "
            "shifted row by row; the far arm is drawn under the body; the claws and their bone-white serrated edges are "
            "NEVER hidden behind the body in any frame and keep the design's size and colours")
ANIM = {
    "run": "RUN, 8 frames, one seamless loop (League's run, a 1.0 s stride): a low, prowling insect run, the body leaning "
           "forward; the legs CROSS: in frames 1 and 5 the feet are furthest apart (frame 1 the near leg in front, frame "
           "5 the far leg in front), in frames 3 and 7 the legs pass each other under the body; the body bobs 1 row with "
           "each landing (down in 1 and 5, up in 3 and 7); the claws held low in front swing a little against the legs, "
           "the wings folded on the back; his head keeps the same place across the cell relative to the standing point "
           "in all 8 frames; frame 8 flows into frame 1.",
    "attack": "BASIC ATTACK (a claw slash), 6 frames: 1 the front claw drawn back and up; 2 raised high over the head; 3 "
              "swinging down and forward; 4 THE HIT (the blow lands here): the front scythe swept down to the image "
              "right at chest height, the whole figure lunging 2-3 squares forward; 5 the follow-through, the claw low; "
              "6 back toward the idle stance. Legs: the design's legs.",
    "skill": "TASTE THEIR FEAR (Q), 6 frames, a long stabbing lunge: 1 coiling back, both claws pulled in; 2 the front arm "
             "cocked back; 3 starting the thrust; 4 THE STAB (the hit lands here): the front arm driven straight out to "
             "the image right at shoulder height, the scythe pointing forward, the whole figure lunging 3-4 squares "
             "forward; 5 holding it; 6 back toward the idle stance. Legs: the design's legs.",
    "skill2": "LEAP -> VOID SPIKE (E then W), 7 frames: 1 crouching lower, about to spring; 2-3 THE LEAP: the whole figure "
              "airborne 4-6 squares higher, the legs drawn up under him, the wings spread wide, the claws forward; 4 "
              "landing in a deep crouch; 5 the wings flared, the back arm wound back; 6 THE THROW (the spike leaves "
              "here): the back arm flung forward to the image right at shoulder height, the claw open (the spike is a "
              "separate effect - do NOT draw it); 7 back toward the idle stance. Never upside down, never his back.",
    "ult": "VOID ASSAULT (R), 3 frames: 1 rearing up a little, the wings flared open; 2 crouching low, the wings snapping "
           "shut, the claws crossed in front (he vanishes here); 3 back toward the idle stance. The stealth shimmer is an "
           "effect.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the "
           "claws flung a little out; 2 recovering toward the idle stance. The design's legs.",
    "dead": "DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 knocked back 2-3 squares, the claws flung out; 3-4 the "
            "WHOLE body (legs included, as one piece) tipping over backwards: frame 3 turned 45 degrees back (falling to "
            "the image left), frame 4 further; 5-6 lying on his back on the ground (the whole body turned 90 degrees, "
            "the head to the image left, the legs to the image right, the legs curled), the wings crumpled under him; 7 "
            "and 8 the same as 6, still. Nothing below the feet line.",
}
ZH = {"idle": "待机", "run": "跑步（交叉步）", "attack": "普攻（镰爪下劈）", "skill": "Q 品尝恐惧（伸臂突刺）",
      "skill2": "E→W 跃击接虚空突刺（腾空、落地、甩刺）", "ult": "R 虚空来袭（展翅、收翅隐身）",
      "hit": "受击", "dead": "死亡（向后倒、仰躺）"}


def document(pal, tags, size, cell, hbox):
    w, h = size
    cw, ch = cell
    pal_txt = " ".join(pal)
    rows = []
    for tag in TAGS:
        t = tags[tag]
        ms = f"{t['n']} × {t['ms'][0]}" if len(set(t["ms"])) == 1 else f"{t['n']} 帧：" + " ".join(map(str, t["ms"]))
        rel = f"第 {t['release']} 帧（tick {t['tick']}）" if t["release"] else "—"
        lay = f"{t['cols']} 列 × {t['rows']} 行，{t['size'][0]}×{t['size'][1]}" + (f"，最后 {t['empty']} 格空" if t["empty"] else "")
        anim = "**已做好，不用画**" if tag == "idle" else f"`{ANIM[tag]}`"
        rows.append(f"| `khazix_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    table = "\n".join(rows)
    hx0, hy0, hx1, hy1 = hbox
    n = len(pal)
    return DOC_TEXT.format(**locals(), PIVOT=PIVOT, FEET=FEET, Z=Z, LEGS_TXT=LEGS_TXT, ORB_TXT=ORB_TXT,
                           ARMS_TXT=ARMS_TXT, cwZ=cw * Z, chZ=ch * Z, sole=PIVOT[1] + FEET,
                           a_tick=tags["attack"]["tick"], q_tick=tags["skill"]["tick"], w_tick=tags["skill2"]["tick"],
                           r_tick=tags["ult"]["tick"])


DOC_TEXT = """# 卡兹克：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/khazix_design.png`（放大 8 倍，1024×1024；{h} 行高、{w} 格宽，{n} 色；脚底在第 {sole} 行，站位点在第 {PIVOT[0]} 列）——就是你上一轮交的 `khazix_design_A.png`（用户：「用这个吧」）。**造型图就是标准**：蓝紫甲壳和青蓝高光、青蓝面甲和两根触角、发黄白光的眼睛、红色下颚和白牙、棕色刺状颈饰、护肩上的红圈斑点、锯齿骨白刃口的大镰刀爪、背上的黄绿虫翼和青蓝背甲、反关节的腿和棕色脚爪，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`khazix_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/khazix_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色，已经是进化后的样子）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**，参考图里朝左的挥动只是往后蓄力。
> - **放技能时的身体就是待机的身体**（同一套像素）：甲壳、背甲、翅膀、颈饰、护肩、腿的形状和大小不能变，只动手臂和镰刀爪（W、R 翅膀可以整片张开）；整个人可以前倾后仰、前后挪 1–3 格。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的面甲、眼睛和红下颚**，**不画背影**（只有死亡仰躺时整个人连头转 90°）；③ **腿**：{LEGS_TXT}；④ **手臂和镰刀爪**：{ARMS_TXT}；⑤ {ORB_TXT}。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/khazix_now_<动作>.png`（骨架），图2 = `design/khazix_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/khazix-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧爪尖的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`khazix_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/khazix_palette.png`，或直接读 `design/khazix_design_1x.png`）。
4. **贴头**：把造型图的头（`design/khazix_head_1x.png` 里不透明的格子：青蓝面甲、触角根、眼睛、红下颚和牙；不含旁边带红斑的护肩；在 128×128 画布上的范围 x {hx0}–{hx1}、y {hy0}–{hy1}，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡仰躺的两帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `khazix_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/khazix_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 ({PIVOT[0]}, {PIVOT[1]})，脚底线第 {sole} 行 | 每张动作图的第一张附图 |
| `design/khazix_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/khazix_head.png`、`_1x.png` | 要贴进每一帧的头（面甲、眼睛、红下颚） | 贴头 |
| `design/khazix_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `khazix_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/khazix_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、翅膀和身体的动作 |
| `guide/khazix_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `khazix_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/khazix_picture.png`、`refs/khazix_draft_codex.png` | 用户选的原画 B 和你上一轮的生图原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：{LEGS_TXT}。
- **手臂和镰刀爪**：{ARMS_TXT}。
- **身上**：{ORB_TXT}。
- **头每帧都是造型图的头**（面甲、眼睛、红下颚逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），爪尖也不能低于这条线。
- **跑步循环**：每帧头相对站位点的横向位置不变；两腿交叉迈步；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色本身**：飞出去的尖刺、紫色虚空能量、隐身的闪光、落地的冲击都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/khazix_design.png`，第二张 `now/khazix_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `khazix_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same blue-teal face plate with the two antennae, the glowing yellow-white eye, the red jaw with white teeth, the brown spiky neck frill, the violet chitin with blue-teal lit edges, the shoulder plates with red-ringed spots, the two big scythe claws with serrated bone-white edges, the pale yellow-green wings and the blue-teal back shell, the backward-bending insect legs with brown toe claws, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the wings and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own body and legs; every blow goes to the RIGHT of the image; never draw him from the back or upside down.
The character: Kha'Zix, the Voidreaver (a mantis-like Void insect with scythe claws and wings).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every standing frame the chitin body, the back shell, the wings, the neck frill, the shoulder plates and the legs keep the FIRST image's shapes and sizes square for square; only the arms and the claws move (the wings may open as whole pieces in W and R), and the whole figure may lean or move 1-3 squares.
Legs: {LEGS_TXT}.
The arms and the claws: {ARMS_TXT}.
The body parts: {ORB_TXT}.
The head (the blue-teal face plate with the antenna roots, the glowing eye, the red jaw and teeth) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the two death frames where he lies on his back is it turned 90 degrees with the whole body). Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in khazix_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every blow, stab and throw goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (the flying spike, void energy, the stealth shimmer, the landing shockwave) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell {cw}x{ch} squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the claws never behind the body, the standing frames on the FIRST image's own body and legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、镰刀爪、翅膀和身体的方向和姿势照图1（出招都朝图的右边）；站着的帧身体和腿用图2自己的。
3. 长相、配色、细节全部换成图2：青蓝面甲和两根触角、发黄白光的眼睛、红下颚和白牙、棕色颈饰、蓝紫甲壳和青蓝高光、护肩红圈斑点、锯齿骨白刃口的大镰刀爪、黄绿虫翼、青蓝背甲、反关节腿和棕色脚爪。
4. 手臂从肩膀外侧长出来，镰刀爪任何一帧都不能藏在身体后面。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
{table}

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样大；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（甲壳、背甲、翅膀、颈饰、护肩、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩膀外侧长出来；镰刀爪没有藏在身体后面；
- [ ] 跑步两腿交叉、远侧腿暗一档、腿的颜色和脚爪和待机一样；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；甩尖刺那一帧爪里是空的；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `khazix_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂和镰刀爪整块按 45° / 90° 转，整个人前倾后仰）。
- 放进 `assets/source/native/`，`khazix_cells.json` 用包里这份，`khazix_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；红色方：朝向特效烘进动作帧（`khazix_bake.json`）。
- 按出手帧核对技能数据的时机（普攻 tick {a_tick}、Q tick {q_tick}、W 甩刺 tick {w_tick}、R tick {r_tick}），量尖刺出手点和头像截取点，重跑模拟，做预览 GIF。
"""

if __name__ == "__main__":
    main()
