"""Build tryndamere_strips_pack.zip: step 2 of Tryndamere's sprite - Codex draws the action strips from the approved design
(step 1, tools/art/design_tryndamere.py -> assets/source/native/tryndamere_native.png; the user: 「40 行原样 继续下一步」).
After league_varus's pack (the 韦鲁斯 session's strips pack).

    python tools/art/pack_tryndamere_strips.py [--render] [--no-zip] [--out DIR]

--render first runs tools/lol/native_pose.py on assets/source/tryndamere/poses.json into %TEMP%/tr_work/pose (League's clips
at game size and as 8x renders, tryndamere_cells.json; camera yaw 60 mirrored: the chest and face toward the viewer, as the
design - yaw 45 showed his back; the chibi hair at 0.5 so the long ponytail does not cover him).
The pack (%TEMP%/tr_work/strips/tryndamere_strips_pack, zipped next to it or into --out):
  MODEL_STRIPS.md                 the prompts (also written to assets/source/tryndamere/MODEL_STRIPS.md)
  design/tryndamere_design.png, _1x    the approved design at 8x (FIRST image of every prompt) and at 1x
  design/tryndamere_head.png, _1x      the head alone (the horns, the helmet and its gem, the face and beard; the long hair left out)
  design/tryndamere_palette.png        its colours, darkest first, with their hex codes
  tryndamere_idle.png                  the idle strip, already built: every frame the design at its standing point
  now/tryndamere_now_<tag>.png         League's clip sampled at game size, 8x (SECOND image)
  pose/lol_pose_<tag>.png         the same frames rendered at 8x (THIRD image; Riot's model: local only)
  guide/tryndamere_guide_<tag>.png     cells, standing points, the feet line and the no-draw band under it
  tryndamere_cells.json                standing points and durations (import_native.py cuts the frames with it)
  refs/tryndamere_picture.png, refs/tryndamere_draft_codex.png
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "tr_work")
POSE = os.path.join(TMP, "pose")
PACK = os.path.join(TMP, "strips", "tryndamere_strips_pack")
ZIP = os.path.join(TMP, "strips", "tryndamere_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "tryndamere")
DESIGN = os.path.join(VR, "assets", "source", "native", "tryndamere_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
PICTURE = os.path.join(SRC, "codex_picture", "tryndamere-model-A.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "A_retry.png")
Z = 8
FEET = 11                       # the soles' row under the pivot (base sprites' soles)
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99, column 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill_q", "ult", "hit", "dead"]
RELEASE = {}                    # 1-based frame where the blow lands / the shout goes, per tag (filled from poses.json)
# the head on the design's canvas, by shape: the horns, the helmet and its gem, the cheek guard, the face, the beard to its
# lowest square - not the long hair behind it (it moves with him) nor the pauldron beside the beard
HEAD_BOXES = [(60, 69, 70, 83), (70, 73, 72, 81), (74, 75, 76, 81)]   # rows r0..r1, columns c0..c1 (inclusive)


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
        ZIP = os.path.join(a.out, "tryndamere_strips_pack.zip")
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "tryndamere_cells.json"), encoding="utf-8") as f:
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
    up(des).save(os.path.join(PACK, "design", "tryndamere_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "tryndamere_design_1x.png"))
    for name, m in (("head", hm),):
        part = np.zeros_like(des)
        part[m] = des[m]
        Image.fromarray(part).save(os.path.join(PACK, "design", f"tryndamere_{name}_1x.png"))
        up(part).save(os.path.join(PACK, "design", f"tryndamere_{name}.png"))
    hy, hx = np.nonzero(hm)
    hbox = (hx.min(), hy.min(), hx.max(), hy.max())
    palette_img(pal).save(os.path.join(PACK, "design", "tryndamere_palette.png"))

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
    up(idle).save(os.path.join(PACK, "tryndamere_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"tryndamere_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"tryndamere_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"tryndamere_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(
            os.path.join(PACK, "guide", f"tryndamere_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None)
    with open(os.path.join(PACK, "tryndamere_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(PICTURE), os.path.join(PACK, "refs", "tryndamere_picture.png"))
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "tryndamere_draft_codex.png"))

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
                    z.write(p, os.path.join("tryndamere_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
        print(ZIP, os.path.getsize(ZIP) // 1024, "KB")



LEGS_TXT = ("in every standing frame (idle, the attack's wind-up and blow, W, Q, R, hit) he stands on the design's OWN legs "
            "square for square - the same wide, low stance, the same dark armoured boots and the teal scale skirt, never "
            "spread wider, never crossed, never shorter; the arms, the sword and the shoulders move, the legs stay (a blow may "
            "move the WHOLE figure, legs included, 1-2 squares forward, never the upper body alone over still legs); only the "
            "run steps, only E spins (the legs turning with the body) and only the death falls")
SWORD_TXT = ("the huge dark grey greatsword with its serrated back, silver edge and the two teal orbs (a big one at the "
             "guard, a small one at the pommel) is held in his BACK hand (image left) by its grip as in the design, the "
             "design's size and shape in every frame (it may turn with the swing, never shrink, never bend, never break "
             "into pieces); it is never dropped except in the death")
ARMS_TXT = ("the arms are the design's arms: thick bronze arms with the grey-white cloth wraps and dark bracers, the same "
            "thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the "
            "free hand is the design's open clawed hand; the big pauldron with its teal gem stays on his front shoulder, the "
            "brown chest strap, the white sash and the beast-head plate with its teal gem stay on him")
ANIM = {
    "run": "RUN, 8 frames, one seamless loop (League's run, 1.0 s a cycle): the design's legs swing from the hips, left and "
           "right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot "
           "on the feet line; the body leans a little forward, bobbing at most 1 square; the greatsword is carried low in "
           "the back hand, trailing behind him, swinging a little; the free arm swings; the long black hair streams back; his "
           "head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into "
           "frame 1.",
    "attack": "BASIC ATTACK (an overhead chop with the greatsword), 6 frames: 1 the sword swings back low behind him; 2 it "
              "comes up behind his back; 3-4 raised high over his head with both hands near the grip, the body rearing "
              "back; 5 THE BLOW (the hit lands here): the sword chopped down and forward to the image right at chest "
              "height, the body lunging forward 1-2 squares, the free arm flung back; 6 the sword trailing back down toward "
              "the idle stance. The slash arc is an effect - do not draw it. Legs: the design's legs.",
    "skill": "SPINNING SLASH (E, he spins through his enemies), 6 frames, one fast turn: the greatsword held out flat at "
             "chest height and swept round him - 1 the sword out to the image left behind him, 2 the body turning, the "
             "sword passing behind his back, 3 the sword out to the image right in front of him, 4 his back half turned "
             "(the sword still out, the head still the design's 3/4 head), 5 the sword round to the left again, 6 coming "
             "out of the spin toward the idle stance. Every frame the sword at its full length, flat; the whirl trail is "
             "an effect. Legs: turning with the body, the design's leg materials, both feet on the line.",
    "skill2": "MOCKING SHOUT (W), 6 frames: 1 he crouches a little, the sword low; 2 the shoulders pulled back, the chest "
              "out; 3 drawing breath, the head back; 4 THE SHOUT (it goes out here): the free arm thrust forward to the "
              "image right with the hand open, palm out, mocking, the mouth wide open; 5 holding it; 6 back toward the idle "
              "stance. The shout's ring is an effect. Legs: the design's legs.",
    "skill_q": "BLOODLUST (Q, he drinks his fury and heals), 5 frames: 1 he straightens a little and clenches the free fist "
               "in front of his chest; 2 the fist pulled to his chest, the shoulders tensed, the head bowed; 3 the whole "
               "body tensed, the arms flexed; 4 the head comes up; 5 back toward the idle stance. The red healing glow is "
               "an effect. Legs: the design's legs.",
    "ult": "UNDYING RAGE (R), 6 frames, League's roar: 1 the chest thrust out and up, the shoulders pulled back; 2 THE ROAR "
           "(it starts here): the head thrown back, the mouth wide open, the free fist clenched at his side, the sword low "
           "behind him; 3-5 holding the roar, the shoulders shaking a square; 6 back toward the idle stance. The red fury "
           "aura is an effect. Legs: the design's legs.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the hair "
           "swinging, the sword still in hand; 2 recovering toward the idle stance. The design's legs.",
    "dead": "DEATH, 8 frames (League's death: the greatsword flies up and sticks in the ground): 1 struck, he staggers back; "
            "2-3 the sword flung up from his hand (draw it high in the cell, inside the cell), he falls back; 4-5 falling "
            "onto his back, the head still the design's head turned with the body, never upside down; 6-8 lying on the "
            "ground, the sword stuck point-down in the ground beside him, standing upright; 7 and 8 the same pose. Nothing "
            "below the feet line.",
}
ZH = {"idle": "待机", "run": "跑步", "attack": "普攻（举刀下劈）", "skill": "E 旋风斩（转一圈）", "skill2": "W 蔑视（怒吼嘲讽）",
      "skill_q": "Q 嗜血杀戮（握拳回血）", "ult": "R 无尽怒火（仰头怒吼）", "hit": "受击", "dead": "死亡（刀飞起插地、倒下）"}


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
        rows.append(f"| `tryndamere_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    table = "\n".join(rows)
    hx0, hy0, hx1, hy1 = hbox
    n = len(pal)
    return DOC_TEXT.format(**locals(), PIVOT=PIVOT, FEET=FEET, Z=Z, LEGS_TXT=LEGS_TXT, SWORD_TXT=SWORD_TXT,
                           ARMS_TXT=ARMS_TXT, cwZ=cw * Z, chZ=ch * Z, sole=PIVOT[1] + FEET,
                           a_tick=tags["attack"]["tick"], w_tick=tags["skill2"]["tick"])


DOC_TEXT = """# 泰达米尔（蛮王）：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/tryndamere_design.png`（放大 8 倍，1024×1024；盔角尖到脚底 {h} 行，{w} 格宽（连刀），{n} 色；脚底在第 {sole} 行，两脚中间在第 64 列）。它是你上一轮生图原稿 A_retry（`refs/tryndamere_draft_codex.png`）按格子读回、整行整列删到 40 行的版本（每一格都是原稿的像素），用户选的「40 行原样」。**造型图就是标准**：角盔和额头青宝石、侧脸的眼睛、短黑胡子和红色的嘴、身后的黑色长发、古铜色赤膊、前肩带青宝石的大肩甲、白布缠手和深色护腕、斜挎皮带、白布腰带和兽首护裆（青宝石）、层叠深灰甲裙和深青鳞甲裙、深灰甲靴、后手拖着的锯齿大弯刀和两颗青珠，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`tryndamere_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/tryndamere_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、刀和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（{h} 行高、宽弓步）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸**，**不画背影**（参考渲染里头盔会转过去，我们不转）；③ **腿**：站着的动作**每帧都是造型图自己的腿**，逐格一样，不能叉得更开、不能交叉、不能变短；出手时可以**整个人连腿一起**前后挪 1–2 格，**不能只挪上半身压在腿上**；只有跑步迈腿、E 转身、死亡倒下；④ 大刀：{SWORD_TXT}；⑤ 手臂：{ARMS_TXT}。
> - 出招方向：**劈砍、嘲讽都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/tryndamere_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/tryndamere_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/tryndamere-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧刀尖和握刀那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`tryndamere_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/tryndamere_palette.png`，或直接读 `design/tryndamere_design_1x.png`）。
4. **贴头**：把造型图的头（`design/tryndamere_head_1x.png` 里不透明的格子：两只角、头盔和额头青宝石、护颊、脸和眼睛、胡子和红嘴；不含身后的长发和旁边的肩甲；在 128×128 画布上的范围 x {hx0}–{hx1}、y {hy0}–{hy1}，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边；长发接在头盔后面，跟着动作飘。
5. 对位：每帧按 `tryndamere_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/tryndamere_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 ({PIVOT[0]}, {PIVOT[1]})，脚底线第 {sole} 行 | 每张动作图的第一张附图 |
| `design/tryndamere_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/tryndamere_head.png`、`_1x.png` | 要贴进每一帧的头（角、头盔和宝石、护颊、脸、胡子和嘴） | 贴头 |
| `design/tryndamere_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `tryndamere_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/tryndamere_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、刀和身体的动作 |
| `guide/tryndamere_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `tryndamere_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/tryndamere_picture.png`、`refs/tryndamere_draft_codex.png` | 用户选的原画 A 和你的生图原稿 A_retry（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（盔角尖到脚底 {h} 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：{LEGS_TXT}。
- **大刀**：{SWORD_TXT}。
- **手臂**：{ARMS_TXT}。
- **头每帧都是造型图的头**（角、头盔、宝石、脸、眼睛、胡子和嘴逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和他的刀**：刀光、旋风、怒吼的冲击、怒火和回血的光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/tryndamere_design.png`，第二张 `now/tryndamere_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `tryndamere_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, armour, sword and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same dark horned helmet with the teal forehead gem, the face with the eye, the short black beard and the red mouth, the long black hair behind, the bronze bare chest and thick arms with grey-white cloth wraps and dark bracers, the big pauldron with a teal gem, the brown chest strap, the white sash with the beast-head plate and its teal gem, the layered dark grey plate skirt over the teal scale skirt, the dark armoured boots, the huge serrated dark grey greatsword with two teal orbs, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the sword and the body from it, but keep the FIRST image's proportions ({h} squares tall, a wide low stance) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Tryndamere, the Barbarian King (a huge bare-chested barbarian with a horned helmet, a black beard, long black hair and a giant serrated greatsword).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size ({h} squares from the horn tips to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: {LEGS_TXT}.
The greatsword: {SWORD_TXT}.
The arms: {ARMS_TXT}.
The head (the horns, the helmet with the gem, the cheek guard, the face with the eye, the beard and the red mouth) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it; the long hair joins the back of the helmet and swings with the motion.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in tryndamere_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every blow and the shout go to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash arcs, the whirl, the shout's ring, the fury aura, the healing glow) - only the character and his sword. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell {cw}x{ch} squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the greatsword with both orbs, the pauldron and both arms in every frame, the standing frames on the FIRST image's own legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、大刀、身体的方向和姿势照图1；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：角盔和额头青宝石、侧脸的眼睛、短黑胡子和红嘴、身后的黑色长发、古铜色赤膊、带青宝石的大肩甲、白布缠手、斜挎皮带、白布腰带和兽首护裆、层叠深灰甲裙和深青鳞甲裙、深灰甲靴、后手的锯齿大弯刀和两颗青珠。
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
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；
- [ ] 每帧都有大刀（两颗青珠）、肩甲、两只手臂和白布缠手；站着的动作是造型图自己的腿（逐格一样），手臂和造型图一样粗；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `tryndamere_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`tryndamere_cells.json` 用包里这份，`tryndamere_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick {a_tick}、W tick {w_tick}），量刀尖和头像截取点，重跑模拟，做预览 GIF。
"""

if __name__ == "__main__":
    main()
