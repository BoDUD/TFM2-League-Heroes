"""Build seraphine_strips_pack.zip: step 2 of Seraphine's sprite - Codex draws the action strips from the approved design
(step 1: Codex's design_1 read back on its own grid, cut region by region to 52 rows, the face and the legs redrawn after
Gwen's, 38 x 52 with the stage, assets/source/native/seraphine_native.png; the user: 「可以 没问题了」).

    python tools/art/pack_seraphine_strips.py [--render] [--no-zip] [--out DIR]

--render first runs tools/lol/native_pose.py on assets/source/seraphine/poses.json into %TEMP%/sr_work/pose_n (League's
clips at game size and as 8x renders, seraphine_cells.json; camera yaw 30 mirrored, the chibi head 2.2; the legs are the
Platform joint: her floating stage is her lowest point; the design pose is League's idle_in, standing on the stage; the
microphone, the ult speakers, the bar and the plane hidden, the hair with its own map).
League's Q, W and death leave the stage (she leaps up, the death throws her off and flips it): the prompts keep her on
the design's legs on the stage for every cast, and the death is Sivir's accepted fall onto the stage. Her run is
League's glide: the stage carries her, the legs stay, the hair and the skirt stream.
The pack (%TEMP%/sr_work/strips/seraphine_strips_pack, zipped next to it or into --out):
  MODEL_STRIPS.md                  the prompts (also written to assets/source/seraphine/MODEL_STRIPS.md)
  design/seraphine_design.png, _1x the approved design at 8x (FIRST image of every prompt) and at 1x
  design/seraphine_head.png, _1x   the head alone (the curl, the bangs, the face, the blue fins beside it)
  design/seraphine_palette.png     its colours, darkest first, with their hex codes
  seraphine_idle.png               the idle strip, already built: every frame the design at its standing point
  now/seraphine_now_<tag>.png      League's clip sampled at game size, 8x (SECOND image)
  pose/lol_pose_<tag>.png          the same frames rendered at 8x (THIRD image; Riot's model: local only)
  guide/seraphine_guide_<tag>.png  cells, standing points, the feet line and the no-draw band under it
  seraphine_cells.json             standing points and durations (import_native.py cuts the frames with it)
  refs/seraphine_picture.png, refs/seraphine_draft_codex.png
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sr_work")
POSE = os.path.join(TMP, "pose_n")
PACK = os.path.join(TMP, "strips", "seraphine_strips_pack")
ZIP = os.path.join(TMP, "strips", "seraphine_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "seraphine")
DESIGN = os.path.join(VR, "assets", "source", "native", "seraphine_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
PICTURE = os.path.join(SRC, "codex_picture", "seraphine-model-A.png")
DRAFT = os.path.join(SRC, "codex_model", "seraphine_design_1.png")
Z = 8
FEET = 11                       # the stage's bottom row under the pivot (base sprites' soles)
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the stage's bottom on row 99, column 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
RELEASE = {}                    # 1-based frame where the note / wave goes, per tag (filled from poses.json)
RELEASE2 = {}                   # skill2's second one (W's song after E's wave)
# the head on the design's canvas, by shape: the curl, the bangs, the face and the two blue crystal fins beside it - not
# the gloved hand raised at her ear (columns 75-79 under row 62) nor the long back hair
HEAD_BOXES = [(48, 61, 55, 75), (62, 67, 57, 74), (55, 61, 50, 54), (55, 61, 76, 80)]   # rows r0..r1, cols c0..c1


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
        ZIP = os.path.join(a.out, "seraphine_strips_pack.zip")
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "seraphine_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    with open(lp(SPEC), encoding="utf-8") as f:
        spec = json.load(f)
    for tag, t in spec["tags"].items():
        if "release" in t:
            RELEASE[tag] = t["release"]
        if "release2" in t:
            RELEASE2[tag] = t["release2"]
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
    up(des).save(os.path.join(PACK, "design", "seraphine_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "seraphine_design_1x.png"))
    for name, m in (("head", hm),):
        part = np.zeros_like(des)
        part[m] = des[m]
        Image.fromarray(part).save(os.path.join(PACK, "design", f"seraphine_{name}_1x.png"))
        up(part).save(os.path.join(PACK, "design", f"seraphine_{name}.png"))
    hy, hx = np.nonzero(hm)
    hbox = (hx.min(), hy.min(), hx.max(), hy.max())
    palette_img(pal).save(os.path.join(PACK, "design", "seraphine_palette.png"))

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
    up(idle).save(os.path.join(PACK, "seraphine_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"seraphine_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"seraphine_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"seraphine_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(
            os.path.join(PACK, "guide", f"seraphine_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None,
                         release2=RELEASE2.get(tag), tick2=ticks(ms, RELEASE2[tag]) if tag in RELEASE2 else None)
    with open(os.path.join(PACK, "seraphine_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(PICTURE), os.path.join(PACK, "refs", "seraphine_picture.png"))
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "seraphine_draft_codex.png"))

    doc = document(pal, tags, (crop.shape[1], crop.shape[0]), (cw, ch), hbox)
    for path in (os.path.join(PACK, "MODEL_STRIPS.md"), DOC):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    for tag, t in tags.items():
        print(f"{tag:9s} {t['n']} frames {t['ms']} {t['cols']}x{t['rows']} {t['size'][0]}x{t['size'][1]} R {t['R']}"
              + (f" release frame {t['release']} tick {t['tick']}" if t["release"] else "")
              + (f", second {t['release2']} tick {t['tick2']}" if t["release2"] else ""))
    if not a.no_zip:
        if os.path.exists(ZIP):
            os.remove(ZIP)
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(PACK):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join("seraphine_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
        print(ZIP, os.path.getsize(ZIP) // 1024, "KB")


LEGS_TXT = ("she always stands on her floating STAGE (the gold-rimmed hover board with the teal deck, the blue flower "
            "medallion, the pink orb and the two blue crystals): the stage is in EVERY frame, the same shape and size as in "
            "the design, its bottom on the feet line, level (never tilted, never flipped, never left behind); her legs are "
            "the design's own legs - the silver-lilac near stocking with the gold curl, the white far stocking, the brown "
            "boots with gold cuffs - square for square in every frame but the death, both boots on the deck; she never "
            "leaps off the stage (League's Q and W jumps are drawn on the stage: only the arms, the hair and the body's "
            "lean move); a cast may move the WHOLE figure with its stage 1-3 squares forward or back, never the upper body "
            "alone over still legs")
ORB_TXT = ("the long pink hair, the curl, the two blue crystal fins beside her head, the white puffy sleeves, the violet "
           "top, the belt with the gold clasp and the striped dark-blue skirt with its white frill stay on her in every "
           "frame, the same shapes, colours and sizes as in the design; the long back hair is one mass that may stream "
           "and swing with the motion (further back in the run, flung up in the casts) but never splits into loose "
           "strands or specks")
ARMS_TXT = ("the arms are the design's arms: fair skin with WHITE GLOVES, the same thickness as in the design (never thinner, "
            "never 1-pixel sticks), each growing from the OUTER corner of its shoulder under the white puffy sleeve (never "
            "from the chest); the near arm over the body, the far arm drawn under it; an arm turns WHOLE from the shoulder "
            "in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the white gloves are NEVER "
            "hidden behind the body, the head or the hair; where an arm moves away, the body behind it is filled with "
            "the body's own colours (the violet top, the white sleeve, the hair)")
ANIM = {
    "run": "GLIDE (the run), 8 frames, one seamless loop (League's run, 1.07 s): she does NOT walk - she stands on her "
           "floating stage, which carries her forward; the stage and her legs stay as in the design in all 8 frames; "
           "the whole figure with the stage bobs 1 row up and down twice in the loop (up in frames 2-3 and 6-7, down in "
           "4 and 8); the long pink hair streams back to the image left and waves (its tips lift and fall a row or two "
           "from frame to frame), the skirt's frill flutters back by one square; the raised hand stays at her ear as in "
           "the design; her head keeps the same place across the cell relative to the standing point in all frames; "
           "frame 8 flows into frame 1.",
    "attack": "BASIC ATTACK (a note sung at the target), 6 frames: 1 the design's stance; 2 the near arm lifts from the "
              "hip, palm up; 3 the near arm raised high above the head, the body leaning a little back; 4 THE NOTE (the "
              "sound bolt leaves here): the near arm flung forward to the image right, the glove open, the body leaning "
              "1 square forward, the hair swinging back; 5 the arm coming back; 6 back to the design's stance. The flying "
              "note is a separate effect - do not draw it.",
    "skill": "HIGH NOTE (Q), 6 frames: 1 the design's stance; 2 the near arm sweeps up and back; 3 both arms raised, the "
             "body arching back, the face up (singing the high note); 4 THE CAST (the note is thrown here): the near arm "
             "flung forward and up to the image right, the body leaning forward 1-2 squares, the hair flung up behind "
             "her; 5 coming back; 6 back to the design's stance. Both boots stay on the stage (League leaps - we do not).",
    "skill2": "BEAT DROP then SURROUND SOUND (E -> W), 8 frames: 1 the design's stance; 2 bending forward a little, the near "
              "arm drawn back; 3 THE WAVE (E's sound wave leaves here): the near arm swept forward low to the image "
              "right, palm out, the body leaning forward 1-2 squares, the hair whipping forward over the shoulder; 4 "
              "straightening up; 5 both arms lowered to her sides, palms out; 6 THE SONG (W's shield goes out here): "
              "both arms spread wide and up to both sides, the face up, singing, the hair lifted behind her; 7 the arms "
              "coming down; 8 back to the design's stance. Both boots stay on the stage.",
    "ult": "ENCORE (R), 4 frames: 1 crouching a little on the stage, the near arm drawn back, gathering; 2 the deepest "
           "crouch, the head down, both arms close; 3 THE ENCORE (the great sound wave leaves here): standing up tall, the "
           "near arm flung forward and up to the image right, the glove open, the far arm back, the face up singing "
           "loudly, the hair streaming back; 4 coming back toward the design's stance. The wave and the speakers are "
           "effects.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left), the "
           "stage under her; 2 recovering toward the design's stance.",
    "dead": "DEATH, 8 frames (Sivir's fall): 1 struck: jolted back as in the hit; 2 knocked back 1-2 squares, staggering "
            "on the stage; 3 the WHOLE body (legs, arms, hair and head as one piece) tipping over backwards, turned about "
            "20 degrees (falling to the image left); 4 turned about 45 degrees; 5 turned 90 degrees, lying on her back on "
            "the stage's deck (the head to the image left, the feet to the image right), the hair spread under her; 6-8 "
            "the same as 5, still. The stage stays level under her, its bottom on the feet line, in all 8 frames.",
}
ZH = {"idle": "待机", "run": "滑行（踩着舞台，不迈步）", "attack": "普攻（抬手甩出音符）", "skill": "Q 清籁穿云（举手高唱再甩出）",
      "skill2": "E→W 增幅节拍→聚和心声（前甩声波，再张开双臂唱）", "ult": "R 炫音返场（蹲下蓄力，起身甩手高唱）",
      "hit": "受击", "dead": "死亡（照希维尔：向后倒、仰躺在舞台上）"}


def document(pal, tags, size, cell, hbox):
    w, h = size
    cw, ch = cell
    pal_txt = " ".join(pal)
    rows = []
    for tag in TAGS:
        t = tags[tag]
        ms = f"{t['n']} × {t['ms'][0]}" if len(set(t["ms"])) == 1 else f"{t['n']} 帧：" + " ".join(map(str, t["ms"]))
        rel = f"第 {t['release']} 帧（tick {t['tick']}）" if t["release"] else "—"
        if t["release2"]:
            rel += f"；第 {t['release2']} 帧（tick {t['tick2']}）"
        lay = f"{t['cols']} 列 × {t['rows']} 行，{t['size'][0]}×{t['size'][1]}" + (f"，最后 {t['empty']} 格空" if t["empty"] else "")
        anim = "**已做好，不用画**" if tag == "idle" else f"`{ANIM[tag]}`"
        rows.append(f"| `seraphine_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    table = "\n".join(rows)
    hx0, hy0, hx1, hy1 = hbox
    n = len(pal)
    return DOC_TEXT.format(
        **locals(), PIVOT=PIVOT, FEET=FEET, Z=Z, LEGS_TXT=LEGS_TXT, ORB_TXT=ORB_TXT, ARMS_TXT=ARMS_TXT, cwZ=cw * Z,
        chZ=ch * Z, sole=PIVOT[1] + FEET)



DOC_TEXT = """# 萨勒芬妮：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/seraphine_design.png`（放大 8 倍，1024×1024；{h} 行高、{w} 格宽，{n} 色；舞台底在第 {sole} 行，站位点在第 {PIVOT[0]} 列）——是按你上一轮 design_1 生图原稿自己的格子取回、分区整行整列删到 52 行、再把脸和腿照格温的画法重画过的版本（用户：「可以 没问题了」）。**造型图就是标准**：亮粉长发和呆毛、头两侧的蓝色水晶羽片、蓝紫大眼睛和腮红、白泡泡袖、紫上衣、白手套、棕皮带和金菱形扣、深蓝彩条短裙和白褶边、银紫亮片袜（金弯纹）和白袜、棕靴金边、脚下金边青台面的浮空小舞台（蓝花徽章、粉色发光球、两颗蓝水晶），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`seraphine_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/seraphine_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。英雄联盟的 Q、W 是跳离舞台、死亡是被甩下舞台、舞台翻过来，**我们不照这些**：放技能一直站在舞台上，死亡照表里写的向后倒、仰躺在舞台上。
> - **舞台每一帧都在她脚下**：大小、形状、颜色和造型图一样，底边落在脚底线上，水平，不倾斜、不翻转。**跑步就是踩着舞台滑行**（英雄联盟就是这样），腿不迈步，只有头发和裙摆往后飘、整个人连舞台上下浮 1 格。
> - **放技能时的身体就是待机的身体**（同一套像素）：腿、靴子、舞台、裙子、上衣、袖子的形状和大小不能变，只动手臂、头发和身体的前倾后仰；整个人连舞台可以前后挪 1–3 格。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（Q 版大头）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的呆毛、刘海、脸和两侧蓝羽片**，**不画背影**（只有死亡仰躺时整个人连头转 90°）；③ **腿和舞台**：{LEGS_TXT}；④ **手臂**：{ARMS_TXT}；⑤ {ORB_TXT}。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/seraphine_now_<动作>.png`（骨架），图2 = `design/seraphine_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/seraphine-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`seraphine_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/seraphine_palette.png`，或直接读 `design/seraphine_design_1x.png`）。
4. **贴头**：把造型图的头（`design/seraphine_head_1x.png` 里不透明的格子：呆毛、刘海、脸、两侧蓝羽片；不含抬到耳边的白手套和身后的长发；在 128×128 画布上的范围 x {hx0}–{hx1}、y {hy0}–{hy1}，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡仰躺的帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. **贴舞台**：舞台（造型图最下面 10 行：青色台面、金色船底、蓝花徽章和粉球、两颗蓝水晶）每帧原样贴在脚下（只平移），不要自己重画。
6. 对位：每帧按 `seraphine_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），舞台底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/seraphine_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 ({PIVOT[0]}, {PIVOT[1]})，舞台底在第 {sole} 行 | 每张动作图的第一张附图 |
| `design/seraphine_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头、贴舞台 |
| `design/seraphine_head.png`、`_1x.png` | 要贴进每一帧的头（呆毛、刘海、脸、两侧蓝羽片） | 贴头 |
| `design/seraphine_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `seraphine_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/seraphine_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、头发和身体的动作 |
| `guide/seraphine_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `seraphine_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/seraphine_picture.png`、`refs/seraphine_draft_codex.png` | 用户选的原画 A 和你上一轮的生图原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿和舞台**：{LEGS_TXT}。
- **手臂**：{ARMS_TXT}。
- **身上**：{ORB_TXT}。
- **头每帧都是造型图的头**（呆毛、刘海、眼睛、腮红、嘴、两侧蓝羽片逐格一样），只平移。
- **脚底线（舞台底）以下什么都不能有**（游戏在这条线下画血条），头发也不能低于舞台台面。
- **滑行循环**：每帧头相对站位点的横向位置不变；腿不迈步；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不跳离舞台**。**只画角色本身**：飞出去的音符、声波、护盾光圈、大招的音箱和音波都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/seraphine_design.png`，第二张 `now/seraphine_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `seraphine_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same long pink hair and curl, the blue crystal fins beside the head, the big blue-violet eyes with blush, the white puffy sleeves, the violet top, the white gloves, the brown belt with the gold clasp, the striped dark-blue skirt with the white frill, the silver-lilac near stocking with the gold curl and the white far stocking, the brown boots with gold cuffs, and her floating STAGE under the boots (gold-rimmed hover board, teal deck, blue flower medallion with a pink orb, two blue crystals), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the hair and the body from it, but keep the FIRST image's proportions and, in every frame but the death, the FIRST image's own legs standing on the stage; every cast goes to the RIGHT of the image; never draw her from the back, upside down or leaping off the stage.
The character: Seraphine, the Starry-Eyed Songstress (a young singer standing on a floating stage).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every frame but the death the stage, the boots, the legs, the skirt, the top and the sleeves keep the FIRST image's shapes and sizes square for square; only the arms, the hair and the body's lean move, and the whole figure with its stage may move 1-3 squares.
Legs and stage: {LEGS_TXT}.
The arms: {ARMS_TXT}.
The body parts: {ORB_TXT}.
The head (the curl, the bangs, the face with the eyes, blush and mouth, the two blue fins beside it) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the death frames where she lies on her back is it turned with the whole body). Erase your own head before pasting it, so no extra outline is left beside it. The stage is COPIED from the FIRST image the same way.
Feet line: in every cell the stage's bottom is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in seraphine_cells.json). In the glide her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never her back, never upside down, never off the stage. Do not draw effects (notes, sound waves, shield rings, the ult's speakers and wave) - only the character and her stage. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell {cw}x{ch} squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head and the stage identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the gloves never behind the body or the hair, the legs and boots of the FIRST image on the stage in every frame but the death, no loose pieces of hair, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、头发和身体的方向和姿势照图1（出招都朝图的右边，不跳离舞台）；腿、靴子和脚下的浮空舞台用图2自己的，每帧都在。
3. 长相、配色、细节全部换成图2：亮粉长发和呆毛、两侧蓝羽片、蓝紫大眼睛和腮红、白泡泡袖、紫上衣、白手套、棕皮带和金扣、深蓝彩条短裙和白褶边、银紫亮片袜和白袜、棕靴金边、金边青台面的浮空小舞台。
4. 手臂从肩膀外侧长出来，白手套任何一帧都不能藏在身体或头发后面。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
{table}

## 交回前自查

- [ ] 每张和 now 条同样大小、同样格子，帧 N 在同一格；舞台底都在 `[R]` 行，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、只用造型图的 {n} 色、描边只有一种近黑；
- [ ] 每帧的头（呆毛、刘海、脸、两侧蓝羽片）和舞台都是造型图原样平移的；
- [ ] 除死亡外，每帧的腿和靴子都是造型图的、站在舞台上；滑行不迈步、上下浮最多 1 格、首尾接得上；
- [ ] 两只手臂都从肩膀外侧长出来，白手套没有藏在身体或头发后面；长发没有散成碎块；
- [ ] 出招朝右；没有画音符、声波、光圈等特效；不画背影、不跳离舞台；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 用 `tools/art/import_native.py` 按 `seraphine_cells.json` 切帧；造型的头和舞台再按 HEAD_BOXES / 最下面 10 行贴回去核对；腿、手臂不对的地方照格温 / 布兰德的做法自己修（rig_seraphine.py），用户审。
- 按出手帧改技能时机：普攻、Q、R 的出手 tick 和 E→W 的两个 tick（build_seraphine.py 的 a_st、q_rel、e_rel、w_rel、r_rel、各动作时长）。
"""

if __name__ == "__main__":
    main()
