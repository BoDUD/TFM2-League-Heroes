"""Build syndra_strips_pack.zip: step 2 of Syndra's sprite - Codex draws the action strips from the approved design
(step 1: Codex's draft 3 cut to 42 rows league_tryndamere's way, tools/art/design_syndra.py ->
assets/source/native/syndra_native.png; the user: 「第三稿→42」).

    python tools/art/pack_syndra_strips.py [--render] [--no-zip] [--out DIR]

--render first runs tools/lol/native_pose.py on assets/source/syndra/poses.json into %TEMP%/sy_work/pose_n (League's
clips at game size and as 8x renders, syndra_cells.json; camera yaw 30 mirrored, the chibi head 1.8, height 45 so the
design pose is 42 rows with the horns; submeshes hidden; the design pose is League's idle1 at 0 ms: floating, arms
spread down, one knee bent). She floats: no crossing steps - the run is League's glide (legs trailing, skirt panels
flowing); the spheres, the waves and the volley are effects (step 3).
The pack (%TEMP%/sy_work/strips/syndra_strips_pack, zipped next to it or into --out): MODEL_STRIPS.md, design/,
syndra_idle.png (already built), now/, pose/ (Riot's model: local only), guide/, syndra_cells.json, refs/.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sy_work")
POSE = os.path.join(TMP, "pose_n")
PACK = os.path.join(TMP, "strips", "syndra_strips_pack")
ZIP = os.path.join(TMP, "strips", "syndra_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "syndra")
DESIGN = os.path.join(VR, "assets", "source", "native", "syndra_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
PICTURE = os.path.join(SRC, "codex_picture", "syndra-model-A.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "generation-3.png")
Z = 8
FEET = 11                       # the soles' row under the pivot (base sprites' soles)
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99, column 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
RELEASE = {}                    # 1-based frame where the shot / throw / burst goes, per tag (filled from poses.json)
# the head on the design's canvas, by shape: the horns, the helmet with its gem, the face (magenta eyes, red lips) and
# the hair framing it - not the long hair falling past her shoulders
HEAD_BOXES = [(58, 67, 54, 73), (68, 76, 59, 72)]   # rows r0..r1, columns c0..c1 (inclusive)


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
        ZIP = os.path.join(a.out, "syndra_strips_pack.zip")
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "syndra_cells.json"), encoding="utf-8") as f:
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
    up(des).save(os.path.join(PACK, "design", "syndra_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "syndra_design_1x.png"))
    for name, m in (("head", hm),):
        part = np.zeros_like(des)
        part[m] = des[m]
        Image.fromarray(part).save(os.path.join(PACK, "design", f"syndra_{name}_1x.png"))
        up(part).save(os.path.join(PACK, "design", f"syndra_{name}.png"))
    hy, hx = np.nonzero(hm)
    hbox = (hx.min(), hy.min(), hx.max(), hy.max())
    palette_img(pal).save(os.path.join(PACK, "design", "syndra_palette.png"))

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
    up(idle).save(os.path.join(PACK, "syndra_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"syndra_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"syndra_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"syndra_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(
            os.path.join(PACK, "guide", f"syndra_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None)
    with open(os.path.join(PACK, "syndra_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(PICTURE), os.path.join(PACK, "refs", "syndra_picture.png"))
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "syndra_draft_codex.png"))

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
                    z.write(p, os.path.join("syndra_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
        print(ZIP, os.path.getsize(ZIP) // 1024, "KB")


LEGS_TXT = ("she FLOATS: the legs are the design's own floating legs - the knee on the image-right side bent, the other leg hanging with its "
            "toes pointing down, black-violet thigh-high boots with gold tops, bare tan thighs - square for square in "
            "every frame but the run, R and the death; a cast may move the WHOLE figure 1-2 squares forward, back or up "
            "(a lean or a lift of the whole body), never the upper body alone over still legs. In the run she GLIDES (no "
            "steps, no crossing): the legs trail a little behind her, swinging 1 square back and forth with the bob, the "
            "skirt panels stream behind; the lowest toe stays on the feet line; the legs keep the design's own leg "
            "squares (never flattened, squashed or missing squares)")
ORB_TXT = ("the violet pauldrons, the dark corset with its magenta belt and gold buckle, the two long skirt panels with "
           "their gold edges and the long silver hair stay on her in every frame, the same shapes and sizes as in the "
           "design (the skirt panels and the hair may stream behind her in the run and the casts, each as one piece, "
           "their shapes the same)")
ARMS_TXT = ("the arms are the design's arms: violet bracers, magenta gloves and black-violet claws on each hand, the same "
            "thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its "
            "shoulder (never from the chest), the arm on the image-left side in front of the hair, the arm on the image-right side leading toward the target; each arm "
            "moves as ONE rigid piece turned about its shoulder (never bent into a rubber curve, never shifted row by "
            "row); the hands and claws are NEVER hidden behind the body or the hair in any frame and keep the design's "
            "size and colours; where an arm moves away, the body behind it is filled with the body's own colours. She "
            "holds nothing: the dark spheres, the force and the waves are effects")
ANIM = {
    "run": "RUN, 8 frames, one seamless loop (League's glide, 1.07 s): she floats forward without steps, the body leaning "
           "a little forward, both arms spread low and a little back as in the design, the claws open; the legs trail "
           "behind and swing 1 square back and forth (frames 1 and 5 the two extremes); the skirt panels and the hair "
           "stream behind her toward image left; the whole figure bobs 1 row (up in frames 2-3, down in 6-7); her head "
           "keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into 1.",
    "attack": "BASIC ATTACK (a dark bolt flicked from her hand), 5 frames: 1 the design's stance; 2 the wind-up: the leading "
              "(image-right) hand drawn up and back beside her shoulder, the claws curled; 3 THE FLICK (the bolt leaves here): the leading "
              "arm thrust forward to the image right at chest height, the open claws pointing at the target, the whole "
              "figure leaning 1 square forward; 4 the arm held out; 5 back to the design's stance. The bolt is an effect.",
    "skill": "DARK SPHERE (Q, a sphere called down onto the target), 4 frames: 1 the leading (image-right) hand lifting; 2 the leading (image-right) hand "
             "raised high above her shoulder, palm up, claws spread; 3 THE CALL (the sphere forms here): the leading (image-right) arm "
             "swept forward and down to the image right, palm down, claws spread, the body leaning forward 1 square; "
             "4 back to the design's stance. The sphere is an effect.",
    "skill2": "FORCE OF WILL (W, grab and throw), 5 frames: 1 both hands reaching forward; 2 THE GRAB: both arms raised "
              "high, claws clenched as if lifting something heavy above her head, the body leaning back 1 square; 3 THE "
              "THROW (the sphere is thrown here): both arms flung forward and down to the image right, the body leaning "
              "forward 1-2 squares; 4 the arms following through low; 5 back to the design's stance. What she throws is "
              "an effect.",
    "skill2_e": "SCATTER THE WEAK (E, a pushing wave), 4 frames: 1 both hands drawn back to her chest; 2 the leading (image-right) arm "
                "pulled back, the far arm forward, the body twisting back 1 square; 3 THE PUSH (the wave goes here): "
                "the leading (image-right) arm swept straight forward to the image right with the palm open and the claws spread, the "
                "skirt panels and hair blown back, the body leaning forward 1 square; 4 back to the design's stance. "
                "The wave is an effect.",
    "ult": "UNLEASHED POWER (R), 5 frames: 1 rising 1 row, both arms lifting; 2 floating 2 rows higher, both arms "
           "spread wide and up, claws open, the hair and skirt panels flaring; 3 THE VOLLEY (the spheres fly here): "
           "both arms thrust forward to the image right, palms open toward the target; 4 holding, the arms forward; "
           "5 coming down back to the design's stance. The spheres are effects.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left); 2 "
           "recovering toward the design's stance. The design's legs.",
    "dead": "DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 her floating fails, sinking down, the arms falling; "
            "3 the WHOLE body (legs and horns included, as one piece) tipping over, turned 45 degrees; 4 turned 90 "
            "degrees, lying on her side on the ground, the hair and skirt panels spread beside her; 5-8 the same as 4, "
            "still. Nothing below the feet line.",
}
ZH = {"idle": "待机", "run": "跑动（悬浮飘行）", "attack": "普攻（近侧手前甩）", "skill": "Q 暗黑法球（举手召唤、向前按下）",
      "skill2": "W 驱使念力（双手举起抓取、向前掷出）", "skill2_e": "E 弱者退散（向前推掌）", "ult": "R 能量倾泻（浮起、双手前推）",
      "hit": "受击", "dead": "死亡（坠落、侧躺）"}


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
        rows.append(f"| `syndra_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    table = "\n".join(rows)
    hx0, hy0, hx1, hy1 = hbox
    n = len(pal)
    return DOC_TEXT.format(**locals(), PIVOT=PIVOT, FEET=FEET, Z=Z, LEGS_TXT=LEGS_TXT, ORB_TXT=ORB_TXT,
                           ARMS_TXT=ARMS_TXT, cwZ=cw * Z, chZ=ch * Z, sole=PIVOT[1] + FEET,
                           a_tick=tags["attack"]["tick"], q_tick=tags["skill"]["tick"], w_tick=tags["skill2"]["tick"],
                           e_tick=tags["skill2_e"]["tick"], r_tick=tags["ult"]["tick"])


DOC_TEXT = """# 辛德拉：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/syndra_design.png`（放大 8 倍，1024×1024；{h} 行高、{w} 格宽，{n} 色；最低的脚尖在第 {sole} 行，站位点在第 {PIVOT[0]} 列）——就是你上一轮第三稿（generation-3）按它自己的格子读回、整行整列删到 42 行（用户：「第三稿→42」）。**造型图就是标准**：紫色弯角头盔 + 洋红宝石、洋红眼睛、红唇、银白长发、紫护肩、黑紫胸甲 + 洋红腰带金扣、小麦色皮肤、两片长裙摆（金边）、黑紫长靴、紫护臂 + 洋红手套 + 黑紫爪子，颜色、明暗，每一帧都照它，只改姿势。
> - **她是悬浮的**：最低的脚尖就是"脚底"，落在脚底线上；**跑动是飘行**（不迈步、不交叉），腿在身后轻轻摆，裙摆和头发往后飘。
> - **待机条已经做好**（`syndra_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/syndra_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **放技能时的身体就是待机的身体**（同一套像素）：护肩、胸甲、腰带、裙摆、头发、腿的形状和大小不能变，只动手臂；整个人可以前倾后仰、上下前后挪 1–3 格。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的弯角头盔、脸和两侧头发**，**不画背影**（只有死亡侧躺时整个人连头转 90°）；③ **腿**：{LEGS_TXT}；④ **手臂**：{ARMS_TXT}；⑤ {ORB_TXT}。
> - **法球、念力、推波、光都是特效（第 3 步单独画）**：手里不画球。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/syndra_now_<动作>.png`（骨架），图2 = `design/syndra_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/syndra-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`syndra_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/syndra_palette.png`，或直接读 `design/syndra_design_1x.png`）。
4. **贴头**：把造型图的头（`design/syndra_head_1x.png` 里不透明的格子：弯角、头盔和宝石、脸、眼睛、红唇、脸两侧的头发；不含垂到肩膀以下的长发；在 128×128 画布上的范围 x {hx0}–{hx1}、y {hy0}–{hy1}，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；R 浮起的几帧整块往上挪；死亡侧躺的帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `syndra_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），最低的脚尖落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/syndra_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 ({PIVOT[0]}, {PIVOT[1]})，脚底线第 {sole} 行 | 每张动作图的第一张附图 |
| `design/syndra_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/syndra_head.png`、`_1x.png` | 要贴进每一帧的头（弯角、头盔、脸、两侧头发） | 贴头 |
| `design/syndra_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `syndra_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/syndra_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/syndra_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `syndra_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/syndra_picture.png`、`refs/syndra_draft_codex.png` | 用户选的原画 A 和你上一轮的第三稿原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点，**不要在脸上和身上留零散的黑格**；外轮廓 1 格近黑描边。
- **腿**：{LEGS_TXT}。
- **手臂**：{ARMS_TXT}。
- **身上**：{ORB_TXT}。
- **头每帧都是造型图的头**（弯角、头盔、脸、两侧头发逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），裙摆和头发也不能低于这条线。
- **跑动循环**：每帧头相对站位点的横向位置不变；飘行（不迈步），腿在身后摆 1 格；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不趴在地上**。**只画角色本身**：法球、念力、推波、光晕都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/syndra_design.png`，第二张 `now/syndra_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `syndra_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same violet helmet with two curved horns and a magenta gem, the magenta eyes and red lips, the long silver hair, the violet pauldrons, the dark corset with its magenta belt and gold buckle, the bare tan midriff and thighs, the two long dark violet skirt panels with gold edges, the black-violet thigh-high boots, the violet bracers, magenta gloves and black-violet claws, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms and the body from it, but keep the FIRST image's proportions and, in every frame but the run, R and the death, the FIRST image's own body and legs; every cast goes to the RIGHT of the image; never draw her from the back, upside down or lying flat on the ground (except the death).
The character: Syndra, the Dark Sovereign (a floating dark sorceress with a horned helmet and clawed gloves).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added, no stray black squares on the face or the body.
The body is the idle body: in every frame but the run, R and the death the pauldrons, the corset and belt, the skirt panels, the hair and the legs keep the FIRST image's shapes and sizes square for square; only the arms move, and the whole figure may lean or move 1-3 squares.
Legs: {LEGS_TXT}.
The arms: {ARMS_TXT}.
The body parts: {ORB_TXT}.
The head (the horns, the helmet with its gem, the face with the magenta eyes and red lips, the hair beside the face) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the death frames where she lies on her side is it turned 90 degrees with the whole body). Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell her lowest toe is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in syndra_cells.json). In the run her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (dark spheres, bolts, the force, the wave, glows, sparks) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell {cw}x{ch} squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the hands and claws never behind the body or the hair, the frames but the run, R and the death on the FIRST image's own body and legs, the run a glide without steps, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；她是悬浮的，腿保持图2的姿势（一膝弯起、一腿垂下），跑动是飘行不迈步。
3. 长相、配色、细节全部换成图2：紫色弯角头盔和洋红宝石、洋红眼睛、红唇、银白长发、紫护肩、黑紫胸甲和洋红腰带金扣、小麦色皮肤、两片长裙摆（金边）、黑紫长靴、紫护臂、洋红手套、黑紫爪子。
4. 手臂从肩膀外侧长出来，整条手臂整块转动，手和爪子任何一帧都不能藏在身体或头发后面；手里不画法球（法球是特效）；脸上身上不要零散的黑格。
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
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点和零散黑格；
- [ ] 待机姿态时和造型图一样大；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（护肩、胸甲腰带、裙摆、头发、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩膀外侧长出来；手和爪子没有藏在身体或头发后面；
- [ ] 跑动是飘行（不迈步），腿在身后摆、颜色和待机一样、没有缺格子；
- [ ] 脚底线以下没有任何像素；黑边干净；
- [ ] 没有背影、没有倒立、没有趴在地上；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效（法球、念力、推波）、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `syndra_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂整块转，整个人前倾后仰）。
- 放进 `assets/source/native/`，`syndra_cells.json` 用包里这份，`syndra_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；红色方：有前后之分、贴在她身上的特效烘进动作帧（`syndra_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick {a_tick}、Q tick {q_tick}、W tick {w_tick}、E tick {e_tick}、R tick {r_tick}），量头像截取点，重跑模拟，做预览 GIF。
"""



if __name__ == "__main__":
    main()
