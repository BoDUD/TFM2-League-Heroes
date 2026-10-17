"""Build nautilus_strips_pack.zip: step 2 of Nautilus's sprite - Codex draws the action strips from the approved design
(step 1: Codex's raw draft A_simple read back on its own grid and cut by whole rows and columns, every row in proportion:
p35, 39 x 48, the anchor 11 rows above the helmet, tools/art/design_nautilus.py -> assets/source/native/nautilus_native.png;
the user: 「用这个吧 感觉这个最还原」, and kept it over the smaller-helmet redraw 1b: 「还是用 p35」).

    python tools/art/pack_nautilus_strips.py [--render] [--no-zip] [--out DIR]

--render first runs tools/lol/native_pose.py on assets/source/nautilus/poses.json into %TEMP%/nt_work/pose_n (League's
clips at game size and as 8x renders, nautilus_cells.json; camera yaw 30 mirrored, chibi head 1.2; the design pose is
League's idle at 0 ms: the anchor on his back, as the design). The anchor is the root joint Weapon (with the chain):
after Q's throw it is left out of the frames (frame "hide": it flies as the projectile's picture) until he is pulled in.
League's attack sweeps the anchor along the floor and R slams it into the ground: the prompts stop it at the feet line.
The pack (%TEMP%/nt_work/strips/nautilus_strips_pack, zipped next to it or into --out): MODEL_STRIPS.md, design/,
nautilus_idle.png (already built), now/, pose/ (Riot's model: local only), guide/, nautilus_cells.json, refs/.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "nt_work")
POSE = os.path.join(TMP, "pose_n")
PACK = os.path.join(TMP, "strips", "nautilus_strips_pack")
ZIP = os.path.join(TMP, "strips", "nautilus_strips_pack.zip")
SRC = os.path.join(VR, "assets", "source", "nautilus")
DESIGN = os.path.join(VR, "assets", "source", "native", "nautilus_native.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
PICTURE = os.path.join(SRC, "codex_picture", "nautilus-model-A.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "A_simple.png")
Z = 8
FEET = 11                       # the soles' row under the pivot (base sprites' soles)
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas (the soles on row 99, column 64)
TAGS = ["idle", "run", "attack", "skill", "skill_pull", "skill2", "ult", "hit", "dead"]
RELEASE = {}                    # 1-based frame where the shot / throw / burst goes, per tag (filled from poses.json)
# the head on the design's canvas: the helmet - the pipe hood, the dome with its three vent holes, the viewing slit with the
# red eyes and the jaw guard down to its sea-green seam - not the anchor's shank left of it nor its flukes above it
HEAD_BOXES = [(63, 86, 56, 74)]   # rows r0..r1, columns c0..c1 (inclusive)


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
        ZIP = os.path.join(a.out, "nautilus_strips_pack.zip")
    if a.render:
        subprocess.run([sys.executable, os.path.join(VR, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE],
                       check=True, cwd=VR)
    with open(os.path.join(POSE, "nautilus_cells.json"), encoding="utf-8") as f:
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
    up(des).save(os.path.join(PACK, "design", "nautilus_design.png"))
    Image.fromarray(des).save(os.path.join(PACK, "design", "nautilus_design_1x.png"))
    for name, m in (("head", hm),):
        part = np.zeros_like(des)
        part[m] = des[m]
        Image.fromarray(part).save(os.path.join(PACK, "design", f"nautilus_{name}_1x.png"))
        up(part).save(os.path.join(PACK, "design", f"nautilus_{name}.png"))
    hy, hx = np.nonzero(hm)
    hbox = (hx.min(), hy.min(), hx.max(), hy.max())
    palette_img(pal).save(os.path.join(PACK, "design", "nautilus_palette.png"))

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
    up(idle).save(os.path.join(PACK, "nautilus_idle.png"))

    tags = {}
    for tag in TAGS:
        now = Image.open(os.path.join(POSE, f"nautilus_native_{tag}.png"))
        now.save(os.path.join(PACK, "now", f"nautilus_now_{tag}.png"))
        shutil.copyfile(os.path.join(POSE, f"nautilus_pose_{tag}.png"), os.path.join(PACK, "pose", f"lol_pose_{tag}.png"))
        guide(cells, tag, up(idle) if tag == "idle" else now).save(
            os.path.join(PACK, "guide", f"nautilus_guide_{tag}.png"))
        frs = cells["tags"][tag]
        c, r = layout(len(frs))
        feet = sorted({fr["pivot"][1] + FEET for fr in frs})
        assert len(feet) == 1, (tag, feet)
        ms = [fr["ms"] for fr in frs]
        tags[tag] = dict(n=len(frs), ms=ms, cols=c, rows=r, size=(c * cw * Z, r * ch * Z), empty=c * r - len(frs),
                         R=feet[0], release=RELEASE.get(tag), tick=ticks(ms, RELEASE[tag]) if tag in RELEASE else None)
    with open(os.path.join(PACK, "nautilus_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    shutil.copyfile(lp(PICTURE), os.path.join(PACK, "refs", "nautilus_picture.png"))
    shutil.copyfile(lp(DRAFT), os.path.join(PACK, "refs", "nautilus_draft_codex.png"))

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
                    z.write(p, os.path.join("nautilus_strips_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
        print(ZIP, os.path.getsize(ZIP) // 1024, "KB")


LEGS_TXT = ("the legs are the design's own legs - the dark grey-black suit, the bronze knee guards and the huge diving boots "
            "with thick bronze soles - square for square in every standing frame (the attack's wind-up, Q's throw, hit): as in "
            "the design, never redrawn; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge or a lean of the "
            "whole body), never the upper body alone over still legs; the lunges (the attack's sweep, Q's throw, R's slam) bend "
            "the knees and step the front foot forward as in the THIRD image. In the run the legs CROSS: every half cycle the "
            "two boots swap front and back, the lifted boot 1-2 rows up passing BESIDE the other one; both legs in the design's "
            "own colours; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own "
            "leg squares (never flattened, squashed or missing squares)")
ORB_TXT = ("the round bronze helmet with its pipe hood, the three vent holes, the viewing slit with the two red eyes and the "
           "square jaw guard, the bronze chest and shoulder plates with their sea-green seams stay on him in every frame, the "
           "same shapes and sizes as in the design")
ARMS_TXT = ("the arms are the design's arms: thick dark grey-black suit arms with bronze bracers and big grey gloves, the same "
            "thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its "
            "shoulder plate (never from the chest); the ANCHOR (the grey stone-iron anchor: the shank with its red band and "
            "brown rope, the round ring, the wide crown with its pale mark and the two hooked flukes) is ONE rigid piece: "
            "carried on his back as in the design, or held by the shank in his near hand where the animation swings it - "
            "turned whole, never bent, never shortened, never thinner, the flukes always the same; the iron chain runs from "
            "his near hand to the anchor's ring; the hand holding it is NEVER hidden behind the body; where an arm moves away, "
            "the body behind it is filled with the body's own colours")
ANIM = {
    "run": "RUN, 8 frames, one seamless loop (League's run, 0.93 s): the anchor stays ON HIS BACK exactly as in the design "
           "(League keeps it there too), the near hand with the chain and the far fist swinging a little; the legs CROSS: in "
           "frames 1 and 5 the boots are furthest apart (frame 1 the near leg in front, frame 5 the far leg in front), in "
           "frames 3 and 7 the lifted boot passes BESIDE the other 1-2 rows up; the body bobs 1 row with each landing; his "
           "helmet keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into "
           "frame 1.",
    "attack": "BASIC ATTACK (a sweep of the anchor), 6 frames: 1 the design's stance, the near hand taking the anchor off "
              "his back; 2 the anchor swung down and back behind him, low, held by the shank, the body coiled; 3 the anchor "
              "swinging forward along the ground (its flukes just ABOVE the feet line); 4 THE SWEEP (the blow lands here): "
              "lunging forward, front knee bent, the anchor swung out level to the image right at knee height, held by the "
              "shank at arm's length; 5 the anchor coming back up in front of him; 6 back toward the design's stance, the "
              "anchor going onto his back.",
    "skill": "DREDGE LINE (Q, the anchor thrown), 6 frames: 1 the anchor lifted off his back; 2 the anchor swung up over his "
             "head, held by the shank; 3 the anchor drawn back behind his head, the body leaning back; 4 swinging it forward "
             "over his head, the body leaning forward; 5 THE THROW (the anchor leaves his hand here): the near arm flung out "
             "forward to the image right, the hand open, the chain running from the hand out of the cell to the right - NO "
             "anchor in this frame (it flies as an effect); 6 holding the throw: braced, leaning back a little, both hands on "
             "the taut chain in front of him (no anchor).",
    "skill_pull": "DREDGE LINE, PULLED IN (after the anchor hooks), 4 frames: 1 pulled forward along the chain: the whole "
                  "body leaning far forward to the image right, both hands on the chain in front of him, the boots trailing "
                  "(no anchor); 2 the same, lower, the boots just above the feet line (no anchor); 3 landing, the anchor back "
                  "in his near hand, held low in front of him; 4 the design's stance, the anchor on his back.",
    "skill2": "TITAN'S WRATH + RIPTIDE (W then E: a shield, then a slam), 6 frames: 1 the design's stance, the fists "
              "clenched (the shield is an effect, do not draw it); 2 the far fist raised high; 3 THE SLAM (the riptide "
              "bursts here): crouching, the far fist punched DOWN onto the ground in front of him (the fist on the feet "
              "line), the anchor still on his back; 4 rising, the fist coming up; 5 standing braced, fists clenched; 6 back "
              "to the design's stance.",
    "ult": "DEPTH CHARGE (R, the anchor slammed into the ground), 8 frames: 1 the near hand taking the anchor off his back; "
           "2 the anchor raised high over his head, held by the shank in both hands; 3 the anchor drawn back behind him, the "
           "body arched back; 4 swinging it over his head, the body leaning forward; 5 THE SLAM (the shockwave leaves here): "
           "crouched low, the anchor driven straight DOWN into the ground in front of him to the image right (its crown and "
           "flukes ON the feet line - the part in the ground is not drawn); 6 holding the slam, the anchor upright in the "
           "ground; 7 pulling the anchor up; 8 back toward the design's stance, the anchor going onto his back.",
    "hit": "HIT, 2 frames: 1 jolted back by a blow: his whole body and helmet pushed back 1-2 squares (to the left); 2 "
           "recovering toward the design's stance. The design's legs.",
    "dead": "DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 the anchor slipping off his back and thudding upright "
            "onto the ground beside him (image left), the chain still in his hand; 3 staggering, slumping forward; 4-6 "
            "sinking down to sit against the anchor, the helmet bowed, the red eyes dimmed; 7-8 the same, still, lying "
            "back against the anchor. Nothing below the feet line.",
}
ZH = {"idle": "待机", "run": "跑步（交叉步，锚背在背上）", "attack": "普攻（抡锚横扫）", "skill": "Q 疏通航道（抛锚）",
      "skill_pull": "Q 疏通航道（锚钩中后被拉过去）", "skill2": "W 泰坦之怒 + E 暗流涌动（护盾、捶地）",
      "ult": "R 深海冲击（把锚砸进地里）", "hit": "受击", "dead": "死亡（靠着锚倒下）"}


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
        rows.append(f"| `nautilus_{tag}.png`（{ZH[tag]}） | {ms} | {rel} | {lay} | 第 {t['R']} 行 | {anim} |")
    table = "\n".join(rows)
    hx0, hy0, hx1, hy1 = hbox
    n = len(pal)
    return DOC_TEXT.format(**locals(), PIVOT=PIVOT, FEET=FEET, Z=Z, LEGS_TXT=LEGS_TXT, ORB_TXT=ORB_TXT,
                           ARMS_TXT=ARMS_TXT, cwZ=cw * Z, chZ=ch * Z, sole=PIVOT[1] + FEET,
                           a_tick=tags["attack"]["tick"], q_tick=tags["skill"]["tick"], w_tick=tags["skill2"]["tick"],
                           r_tick=tags["ult"]["tick"])


DOC_TEXT = """# 诺提勒斯：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/nautilus_design.png`（放大 8 倍，1024×1024；{h} 行高、{w} 格宽，{n} 色；脚底在第 {sole} 行，站位点在第 {PIVOT[0]} 列）——从你上一轮第二次的生图原稿 `A_simple` 按格子取回、整行整列按比例删到头盔顶到脚底 37 行（锚再高出 11 行）（用户：「用这个吧 感觉这个最还原」；头盔缩小的重画 1b 没有采用：「还是用 p35」）。**造型图就是标准**：圆铜潜水头盔（锈红铜管兜帽、顶上三个通气孔、黑色观察窗里两只红橙眼睛、方形铜护颌）、锈铜胸甲肩甲 + 海绿发光缝线、深灰黑潜水服、大灰手套、铜护膝、厚底潜水靴、近侧手握的粗铁链、背在背上的灰色大锚（红箍、棕绳、两只弯钩锚爪），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`nautilus_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/nautilus_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、锚和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **放技能时的身体就是待机的身体**（同一套像素）：头盔、胸甲肩甲、腿的形状和大小不能变，只动手臂和锚；整个人可以前倾后仰、前冲、下蹲。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头盔大、身体短）；② 头盔是贴上去的（见下），**头盔每帧不变形、不旋转、始终是造型图的头盔和两只红眼**，**不画背影**；③ **腿**：{LEGS_TXT}；④ **手臂和锚**：{ARMS_TXT}；⑤ {ORB_TXT}；⑥ 锚和铁链**永远不低于脚底线**（英雄联盟里锚扫过地面、砸进地里，我们只画到地面为止）；⑦ **Q 抛出去以后的帧里没有锚**（锚是飞出去的特效），被拉过去落地时锚才回到手里。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/nautilus_now_<动作>.png`（骨架），图2 = `design/nautilus_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。**整条画糊了就一帧一帧单独生成**（每帧一张图，最后拼回格子）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/nautilus-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧握锚的手和锚冠的位置）和所有生图原稿（`raw/`，不要重采样），最好打成一个 zip（`nautilus_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/nautilus_palette.png`，或直接读 `design/nautilus_design_1x.png`）。
4. **贴头盔**：把造型图的头盔（`design/nautilus_head_1x.png` 里不透明的格子：铜管兜帽、带三个通气孔的圆顶、黑色观察窗和两只红眼、方形护颌到它下面的海绿缝线；不含左边的锚杆和上面的锚爪；在 128×128 画布上的范围 x {hx0}–{hx1}、y {hy0}–{hy1}，**按图里的形状贴，不是整个方框**）原样贴进每一帧头盔的位置（只平移；死亡低头的几帧也只平移）。贴之前先擦掉你自己画的头盔，不要在头盔旁边留下多余的描边。
5. 对位：每帧按 `nautilus_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/nautilus_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 ({PIVOT[0]}, {PIVOT[1]})，脚底线第 {sole} 行 | 每张动作图的第一张附图 |
| `design/nautilus_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头盔 |
| `design/nautilus_head.png`、`_1x.png` | 要贴进每一帧的头盔（兜帽、圆顶、通气孔、观察窗、红眼、护颌） | 贴头盔 |
| `design/nautilus_palette.png` | 造型图的全部 {n} 色（暗到亮） | 色板 |
| `nautilus_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/nautilus_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、锚和身体的动作 |
| `guide/nautilus_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `nautilus_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/nautilus_picture.png`、`refs/nautilus_draft_codex.png` | 用户选的原画 A 和你上一轮第二次的生图原稿 A_simple（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 {n} 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：{LEGS_TXT}。
- **手臂和锚**：{ARMS_TXT}。
- **身上**：{ORB_TXT}。
- **头盔每帧都是造型图的头盔**（兜帽、通气孔、观察窗、红眼、护颌逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），锚和铁链也不能低于这条线。
- **跑步循环**：锚一直背在背上；每帧头盔相对站位点的横向位置不变；两腿真正交叉（每半个周期两只靴子交换前后）；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不趴在地上**。**只画角色本身**：护盾、水花、漩涡、冲击波、飞出去的锚都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/nautilus_design.png`，第二张 `now/nautilus_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `nautilus_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, helmet, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same round bronze diving helmet with its rusty-red pipe hood, three vent holes, black viewing slit with two red-orange eyes and square jaw guard, the rusted bronze chest and shoulder plates with glowing sea-green seams, the dark grey-black suit, the big grey gloves, the bronze knee guards, the huge diving boots, the thick iron chain in his near hand and the grey stone-iron anchor on his back (red band, brown rope, two hooked flukes), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the anchor and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own body and legs; every cast goes to the RIGHT of the image; never draw him from the back, upside down or lying flat on the ground.
The character: Nautilus, the Titan of the Depths (a heavy giant in an ancient rusted bronze diving suit with a huge stone anchor).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the {n} colors of the FIRST image, no new colors: {pal_txt}. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every frame the helmet, the chest and shoulder plates and the legs keep the FIRST image's shapes and sizes square for square; only the arms and the anchor move, and the whole figure may lean, lunge or crouch.
Legs: {LEGS_TXT}.
The arms and the anchor: {ARMS_TXT}.
The body parts: {ORB_TXT}.
The helmet (the pipe hood, the dome with three vent holes, the black viewing slit with the two red-orange eyes, the jaw guard) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own helmet before pasting it, so no extra outline is left beside it.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there - the anchor and the chain too. His place across the cell follows the SECOND image (each frame's standing point is in nautilus_cells.json). In the run his helmet keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (shields, water, splashes, whirlpools, shockwaves, a flying anchor, glows, sparks) - only the character. Every animation starts and ends near the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell {cw}x{ch} squares ({cwZ}x{chZ} px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the helmet identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the hand holding the anchor never behind the body, the anchor rigid, full size with both flukes, no anchor after Q's throw until he lands, the standing frames on the FIRST image's own body and legs, the run's boots swapping front and back, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、锚和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；头盔、身体和腿用图2自己的。
3. 长相、配色、细节全部换成图2：圆铜潜水头盔（铜管兜帽、三个通气孔、黑色观察窗和两只红橙眼睛、方形护颌）、锈铜胸甲肩甲和海绿缝线、深灰黑潜水服、大灰手套、铜护膝、厚底潜水靴、粗铁链、灰色大锚（红箍、棕绳、两只弯钩锚爪）。
4. 手臂从肩甲外侧长出来，握锚的手任何一帧都不能藏在身体后面，锚始终是一整块、大小不变；锚和铁链不能低于脚底线；Q 抛出去以后到落地前的帧里没有锚。
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
- [ ] 待机姿态时和造型图一样大；头盔就是造型图的头盔（逐格一样，只平移），头盔旁边没有多余的描边；
- [ ] 每帧身体（头盔、胸甲肩甲、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩甲外侧长出来；握锚的手没有藏在身体后面，锚是一整块、没有变小变形，两只锚爪完整；
- [ ] 跑步锚一直背在背上，两腿真正交叉（每半个周期两只靴子交换前后、抬起的靴子从另一只旁边越过），腿的颜色和待机一样，没有缺格子；
- [ ] Q 抛出那一帧起到被拉过去落地前没有锚；
- [ ] 脚底线以下没有任何像素（锚、铁链也不行）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有趴在地上；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `nautilus_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头盔不对的帧换回造型图的头盔；身体不是待机身体的帧用造型图的部件重摆（rigkit：锚和握锚的手整块只平移和 90° 整转，整个人前倾、前冲、下蹲；不按任意角度转）。
- 放进 `assets/source/native/`，`nautilus_cells.json` 用包里这份，待机由 `import_native.py` 的 idle_breathe 从造型图生成。
- `import_native.py`：ORDER 待机，COMPLETE 补描边；红色方：有前后之分、贴在他身上的特效烘进动作帧（`nautilus_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick {a_tick}、Q 抛出 tick {q_tick}、W+E 捶地 tick {w_tick}、R 砸地 tick {r_tick}；skill_pull 由锚钩中时的 CasterAnimation 播放），量头像截取点，重跑模拟，做预览 GIF。
"""


if __name__ == "__main__":
    main()
