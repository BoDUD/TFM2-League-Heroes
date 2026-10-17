"""Build xinzhao_strips_pack.zip: step 2 of Xin Zhao's sprite - Codex draws the action strips from the approved design
(step 1, tools/art/design_xinzhao.py -> assets/source/native/xinzhao_native.png: Codex's draft 03 shrunk to 42 rows by
whole lines, the user's pick). After league_tryndamere's pack (tools/art/pack_tryndamere_strips.py, the same layout).

    python tools/art/pack_xinzhao_strips.py [--render] [--no-zip] [--out DIR]

--render first runs tools/lol/native_pose.py on assets/source/xinzhao/poses.json into %TEMP%/xz_work/pose (League's clips
at game size and as 8x renders, xinzhao_cells.json; camera yaw 60 mirrored: the chest and face toward the viewer, as the
design; the hair chain Hair1-8 - the topknot's ribbons, rendered as a dark lump - left out: the design's head is pasted).
The pack (%TEMP%/xz_work/strips/xinzhao_strips_pack, zipped next to it or into --out):
  MODEL_STRIPS.md                 the prompts (also written to assets/source/xinzhao/MODEL_STRIPS.md)
  design/xinzhao_design.png, _1x  the approved design at 8x (FIRST image of every prompt) and at 1x
  design/xinzhao_head.png, _1x    the head alone (the topknot and gold crown, the hair with its silver streaks, the face;
                                  the purple ribbons left out: they swing with him)
  design/xinzhao_palette.png      its colours, darkest first, with their hex codes
  xinzhao_idle.png                the idle strip, already built: every frame the design at its standing point
  now/xinzhao_now_<tag>.png       League's clip sampled at game size, 8x (SECOND image)
  pose/lol_pose_<tag>.png         the same frames rendered at 8x (THIRD image; Riot's model: local only)
  guide/xinzhao_guide_<tag>.png   cells, standing points, the feet line and the no-draw band under it
  xinzhao_cells.json              standing points and durations (import_native.py cuts the frames with it)
  refs/xinzhao_picture.png, refs/xinzhao_draft_codex.png
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "xz_work")
POSE = os.path.join(TMP, "pose")
PACK = os.path.join(TMP, "strips", "xinzhao_strips_pack")
ZIP = os.path.join(TMP, "strips", "xinzhao_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "xinzhao")
DESIGN = os.path.join(VR, "assets", "source", "native", "xinzhao_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
PICTURE = os.path.join(SRC, "codex_picture", "xinzhao-model-A.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "03.png")
Z = 8
FEET = 11                       # the soles' row under the pivot (base sprites' soles)
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99, column 64)
TAGS = ["idle", "run", "attack", "attack_p", "q1", "q2", "q3", "skill", "skill2", "ult", "hit", "dead"]
RELEASE = {}                    # 1-based frame where the blow lands / the shout goes, per tag (filled from poses.json)
# the head on the design's canvas, by shape: the topknot and its gold crown, the black hair with the silver streaks, the
# face to the chin - not the purple ribbons (they swing with him), the gold shoulder guard nor the neck under the chin
HEAD_BOXES = [(58, 62, 58, 64), (63, 70, 57, 73), (71, 75, 61, 70)]   # rows r0..r1, columns c0..c1 (inclusive)


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
        ZIP = os.path.join(a.out, "xinzhao_strips_pack.zip")
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "xinzhao_cells.json"), encoding="utf-8") as f:
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
    up(des).save(os.path.join(PACK, "design", "xinzhao_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "xinzhao_design_1x.png"))
    for name, m in (("head", hm),):
        part = np.zeros_like(des)
        part[m] = des[m]
        Image.fromarray(part).save(os.path.join(PACK, "design", f"xinzhao_{name}_1x.png"))
        up(part).save(os.path.join(PACK, "design", f"xinzhao_{name}.png"))
    hy, hx = np.nonzero(hm)
    hbox = (hx.min(), hy.min(), hx.max(), hy.max())
    palette_img(pal).save(os.path.join(PACK, "design", "xinzhao_palette.png"))

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
    up(idle).save(os.path.join(PACK, "xinzhao_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"xinzhao_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"xinzhao_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"xinzhao_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(
            os.path.join(PACK, "guide", f"xinzhao_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None)
    with open(os.path.join(PACK, "xinzhao_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(PICTURE), os.path.join(PACK, "refs", "xinzhao_picture.png"))
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "xinzhao_draft_codex.png"))

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
                    z.write(p, os.path.join("xinzhao_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
        print(ZIP, os.path.getsize(ZIP) // 1024, "KB")



LEGS_TXT = ("in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the "
            "same wide stance, the same pale lavender trousers, silver hip plates and dark steel boots with gold trim, never "
            "spread wider, never crossed, never shorter; in the thrusts and swings (the attacks, Q, W, R) he may step or "
            "lunge as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves "
            "with them, never the upper body alone over still legs); only the run steps, only E leaps and only the death "
            "falls")
SPEAR_TXT = ("the long spear is the design's own - its head a PURPLE blade with a SILVER CRESCENT HOOK and a purple streamer, "
             "a dark brown shaft with gold rings, a short iron butt spike - at the design's length in every frame (it may "
             "turn with the motion: level for a thrust, upright, over his head; never shrink, never bend, never break into "
             "pieces), held in his hands as the THIRD image shows; it is never dropped except in the death")
ARMS_TXT = ("the arms are the design's arms: brown leather forearm guards and dark fingerless gloves, the purple sleeve, the "
            "same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; "
            "the gold shoulder guard stays on his back shoulder, the silver pauldron with its bright blue insets on his front "
            "shoulder, the silver breastplate, the brown belt and the purple coat with its gold trim stay on him")
ANIM = {
    "run": "RUN, 8 frames, one seamless loop (League's run, 1.04 s a cycle): the design's legs swing from the hips, left and "
           "right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot "
           "on the feet line; the body leans a little forward, bobbing at most 1 square; the spear carried in the back hand "
           "slanting behind him as in the design (its purple blade low behind, the butt up past his shoulder), swinging a "
           "little; the free arm swings; the purple ribbons stream back; his head keeps the same place across the cell "
           "relative to the standing point in all 8 frames; frame 8 flows into frame 1.",
    "attack": "BASIC ATTACK (a spear thrust), 6 frames: 1 the spear drawn back low at his side, the blade pointing down and "
              "forward; 2-3 the spear sweeping low forward, the body turning into it; 4 THE BLOW (the hit lands here): the "
              "spear thrust out level to the image right at waist height, the body lunging forward 1-2 squares; 5 the spear "
              "still held out level; 6 back toward the idle stance. The thrust's streak is an effect - do not draw it.",
    "attack_p": "DETERMINATION (every third attack, a big two-handed swing), 6 frames: 1 the spear lifted, slanting up "
                "behind him; 2 swung up higher; 3 swung round level at head height; 4 THE BLOW (the hit lands here): the "
                "spear brought round and down in front of him, the body crouched into it; 5 the spear slanting low behind "
                "him; 6 back toward the idle stance. The arc is an effect.",
    "q1": "THREE TALON STRIKE, FIRST THRUST (Q1), 6 frames: 1 the spear raised up behind him; 2 swung over his head; 3 "
          "the thrust starting, the spear coming level; 4 THE THRUST (the hit lands here): lunging forward, the spear driven "
          "straight out level to the image right; 5 holding the thrust; 6 the spear brought upright, back toward the idle "
          "stance.",
    "q2": "THREE TALON STRIKE, SECOND STRIKE (Q2, a sweep), 6 frames: 1 the spear held level at his chest; 2 the spear "
          "twirled upright; 3 swept down and forward in an arc; 4 THE SWEEP (the hit lands here): the spear swung up "
          "diagonally in front of him, the body lunging; 5 the spear slanting up the other way; 6 back toward the idle "
          "stance.",
    "q3": "THREE TALON STRIKE, THIRD STRIKE (Q3, the knock-up), 7 frames: 1 a crouch, the spear upright; 2 the spear level "
          "at his chest; 3 the spear swept up in an arc; 4 THE KNOCK-UP (the hit lands here): the spear swung up from low in "
          "front to high, lifting; 5-6 the spear held LEVEL OVER HIS HEAD with both hands (League's pose, the picture's "
          "version B); 7 back toward the idle stance. The upward slash is an effect.",
    "skill": "AUDACIOUS CHARGE (E, a leaping charge), 6 frames: 1 a crouch, about to leap; 2-3 flying forward low to the "
             "image right, the body stretched out, the spear held level ahead (a row or two above the feet line, inside the "
             "cell); 4 THE LANDING (the hit lands here): landing on both feet, the spear driven down and forward; 5 the "
             "spear thrust out level; 6 back toward the idle stance. The charge's trail and the ground burst are effects.",
    "skill2": "WIND BECOMES LIGHTNING (W, a slash then a thrust), 7 frames: 1 the spear swung back slanting; 2 the spear "
              "spun upright in front of him; 3 upright at his side; 4 THE SLASH (it lands here): the spear swept out wide "
              "and level across his front; 5-6 THE THRUST (it goes out on 5): lunging low forward, the spear driven out "
              "level to the image right; 7 back toward the idle stance. The slash arc and the thrust's wind are effects.",
    "ult": "CRESCENT GUARD (R, a sweep all round him), 7 frames: 1 the spear held low across his body; 2 the spear swung "
           "level behind him; 3 THE SWEEP (it lands here): spinning, the spear swept out round him; 4-6 the spear swung "
           "round him, out to the image left, then to the image right, the body turning with it (the head still the "
           "design's 3/4 head); 7 the spear brought upright at his side (its butt above the feet line). The crescent and the "
           "guard's glow are effects.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the "
           "ribbons swinging, the spear still in hand; 2 recovering toward the idle stance. The design's legs.",
    "dead": "DEATH, 8 frames (League's death: he sinks to one knee on his spear, then falls): 1 struck, he staggers back; 2-5 "
            "sinking onto one knee, leaning on the upright spear, the head bowed; 6 tipping forward; 7-8 lying face down on "
            "the ground, the spear fallen beside him; 7 and 8 the same pose. The head is the design's head turned with the "
            "body, never upside down. Nothing below the feet line.",
}
ZH = {"idle": "待机", "run": "跑步", "attack": "普攻（直刺）", "attack_p": "被动第三下（双手大挥）", "q1": "Q 第一下（突刺）",
      "q2": "Q 第二下（横扫）", "q3": "Q 第三下（上挑击飞、横举过头）", "skill": "E 无畏冲锋（飞身突刺落地）",
      "skill2": "W 风斩电刺（横扫再直刺）", "ult": "R 新月护卫（绕身横扫）", "hit": "受击", "dead": "死亡（单膝跪地后倒下）"}


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
        rows.append(f"| `xinzhao_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    table = "\n".join(rows)
    hx0, hy0, hx1, hy1 = hbox
    n = len(pal)
    ticks_txt = "、".join(f"{ZH[k].split('（')[0]} tick {tags[k]['tick']}" for k in TAGS if tags[k]["tick"] is not None)
    return DOC_TEXT.format(**locals(), PIVOT=PIVOT, FEET=FEET, Z=Z, LEGS_TXT=LEGS_TXT, SPEAR_TXT=SPEAR_TXT,
                           ARMS_TXT=ARMS_TXT, cwZ=cw * Z, chZ=ch * Z, sole=PIVOT[1] + FEET)


DOC_TEXT = """# 赵信：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/xinzhao_design.png`（放大 8 倍，1024×1024；发髻顶到脚底 {h} 行，{w} 格宽（连枪），{n} 色；脚底在第 {sole} 行，两脚中间在第 64 列）。它是你上一轮生图原稿 03（`refs/xinzhao_draft_codex.png`）按格子读回、整行整列删到 42 行的版本（每一格都是原稿的像素），用户选的「42 行、枪保持原稿长度」。**造型图就是标准**：黑色发髻和金发冠、两条深紫发带、黑发和额前的银白挑染、脸和眼睛、银白胸甲、皇家紫长战袍和金边、后肩金护肩、前肩带亮蓝饰的银护肩、棕色护臂和露指手套、棕色腰带、浅紫宽裤和胯边银甲片、深钢色靴子、紫刃银月牙钩的长枪（深棕枪杆、金箍、枪尾尖锥），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`xinzhao_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 11 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/xinzhao_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、枪和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（{h} 行高、头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸**，**不画背影**（参考渲染里身体会转过去，我们的头不转）；参考渲染里**头顶没有发髻和发带**（渲染坏了，已经去掉），发髻、金冠照造型图贴上去，两条紫发带你自己画，跟着动作飘；③ **腿**：{LEGS_TXT}；④ 长枪：{SPEAR_TXT}；⑤ 手臂：{ARMS_TXT}。
> - 出招方向：**突刺、横扫、冲锋都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/xinzhao_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/xinzhao_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/xinzhao-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧枪尖和握枪那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`xinzhao_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/xinzhao_palette.png`，或直接读 `design/xinzhao_design_1x.png`）。
4. **贴头**：把造型图的头（`design/xinzhao_head_1x.png` 里不透明的格子：发髻和金冠、黑发和银白挑染、脸和眼睛、下巴；不含两条紫发带和金护肩；在 128×128 画布上的范围 x {hx0}–{hx1}、y {hy0}–{hy1}，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边；发带接在发髻后面，跟着动作飘。
5. 对位：每帧按 `xinzhao_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/xinzhao_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 ({PIVOT[0]}, {PIVOT[1]})，脚底线第 {sole} 行 | 每张动作图的第一张附图 |
| `design/xinzhao_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/xinzhao_head.png`、`_1x.png` | 要贴进每一帧的头（发髻和金冠、黑发和银白挑染、脸、下巴） | 贴头 |
| `design/xinzhao_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `xinzhao_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/xinzhao_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、枪和身体的动作 |
| `guide/xinzhao_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `xinzhao_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/xinzhao_picture.png`、`refs/xinzhao_draft_codex.png` | 用户选的原画 A 和你的生图原稿 03（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（发髻顶到脚底 {h} 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：{LEGS_TXT}。
- **长枪**：{SPEAR_TXT}。
- **手臂**：{ARMS_TXT}。
- **头每帧都是造型图的头**（发髻、金冠、黑发、银白挑染、脸和眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条），枪也不能伸到线下。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和他的枪**：刀光、突刺的风、冲锋的拖尾、横扫的月牙、护盾的光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/xinzhao_design.png`，第二张 `now/xinzhao_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `xinzhao_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, armour, spear and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same black topknot with its gold crown and two dark purple ribbons, the black hair with silver-white streaks, the face with both eyes and the brows, the silver breastplate, the long royal purple coat with gold trim, the gold shoulder guard on his back shoulder, the silver pauldron with bright blue insets on his front shoulder, the brown leather forearm guards and dark gloves, the brown belt, the pale lavender trousers with silver hip plates, the dark steel boots, the long spear with its purple blade, silver crescent hook, brown shaft with gold rings and iron butt spike, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the spear and the body from it, but keep the FIRST image's proportions ({h} squares tall, a big head); its head has no topknot (removed from the render): the FIRST image's head with its topknot goes there; never draw him from the back or upside down.
The character: Xin Zhao, the Seneschal of Demacia (a stern spear warrior with a black topknot, a royal purple coat over silver armour and a long purple-bladed spear).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size ({h} squares from the top of the topknot to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: {LEGS_TXT}.
The spear: {SPEAR_TXT}.
The arms: {ARMS_TXT}.
The head (the topknot with its gold crown, the black hair with the silver streaks, the face with the eyes and brows, the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it; the two purple ribbons join the back of the topknot and swing with the motion.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in xinzhao_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every thrust, sweep and charge goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash arcs, the thrust's wind, the charge's trail, the crescent, the guard's glow) - only the character and his spear. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell {cw}x{ch} squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the whole spear with its purple blade and crescent hook, both shoulder pieces and both arms in every frame, the legs the design's legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、长枪、身体的方向和姿势照图1；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：黑色发髻和金冠、两条深紫发带、黑发和银白挑染、脸和眼睛、银白胸甲、紫金长战袍、后肩金护肩、前肩蓝饰银护肩、棕色护臂、棕色腰带、浅紫宽裤和银甲片、深钢色靴子、紫刃银月牙钩的长枪（深棕枪杆、金箍、枪尾尖锥）。
4. 动作：[animation]
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
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；两条紫发带接在发髻后面；
- [ ] 每帧都有整杆长枪（紫刃、银月牙钩、金箍、枪尾尖锥）、两块护肩、两只手臂和棕色护臂；腿和造型图一样的材质和粗细；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `xinzhao_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`xinzhao_cells.json` 用包里这份，`xinzhao_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（{ticks_txt}），量枪尖和头像截取点，重跑模拟，做预览 GIF。
"""

if __name__ == "__main__":
    main()
