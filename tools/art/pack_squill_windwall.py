#!/usr/bin/env python3
"""Build squill_windwall_pack.zip: Codex draws Lulu's polymorph critter (League's Squill) and Yasuo's Wind Wall effects.

    python tools/art/pack_squill_windwall.py [--no-zip] [--out DIR]

Step 1 (the user reviews): the Squill design, three options A / B / C at game size; step 2 once one is picked: the
polymorph's in / loop / out strips; and Yasuo's Wind Wall: the wall (a projectile picture), the cast gust, the block
puff, the fade. The pack (C:/t/lu_yw/squill_windwall_pack, zipped into --out, default dist/squill_windwall_packs) holds
PROMPTS.md (also written to assets/source/lulu/PROMPTS_SQUILL_WINDWALL.md) and refs/:
  01_lol_squill.png   League's LuluPolymorphCritter (pose_ref.py --champ LuluPolymorphCritter --wad Lulu): four angles
                      and its idle - Riot's model, local only;
  02_now_poly.png     the polymorph now (league_lulu_fx w_poly_in / w_poly / w_poly_out) next to a champion at game size;
  03_size.png         game-size champions (base fighter, Garen, Lulu, Yasuo, Sejuani) on the arena colour with a ruler;
  04_lol_windwall.png League's Wind Wall particle textures (Yasuo.wad: *_W_*) - Riot's art, local only;
  05_yasuo.png        Yasuo's idle at game size, 4x.
Riot's renders and textures stay out of the repo (C:/t only).
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
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
TMP = "C:/t/lu_yw"
NAME = "squill_windwall_pack"
DOC = os.path.join(ROOT, "assets", "source", "lulu", "PROMPTS_SQUILL_WINDWALL.md")
ARENA = (104, 112, 72, 255)
PRE = chr(92) * 2 + "?" + chr(92)

FUR = "#F4ECFF, #DCC8FF, #BE9CF8, #9C74EC, #7A50D4, #5634A8, #38206E"      # the Squill's lilac-purple fur
WHITE = "#FFFFFF, #F0F0FA, #D2D4EA, #A8ACCE"                              # face, muzzle, belly, tail tips
PINK = "#FFD6F0, #FF9ADA, #F05AC0, #B82A94"                               # inner ears, nose
EYE = "#120A1E (the eye) and #FFFFFF (one 1-square shine)"
PAW = "#2A1440"                                                           # paws
OUTLINE = "#24123A"
MAGIC = "#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8"            # Lulu's pink magic puff
VIOLET = "#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8"
WIND = "#FFFFFF, #E6FAFF, #B4EEFA, #78D8F0, #3CB0DC, #1E7AB4, #134A7A"     # Yasuo's wind: white to steel blue
STEEL = "#DCE6F0, #A8B8CC, #74869E"                                       # grey-blue wind dust

CRITTER_LEAD = ("Pixel art game sprite for a small tactics game, drawn AT GAME SIZE: chunky square pixels (one square = one "
                "game pixel, 16 px a square in this image), hard edges, no anti-aliasing, no blur; ONE 1-square outline "
                f"in {OUTLINE} round the critter (never a second black ring), 3-4 flat shades per material, no specks, "
                "details at least 2 squares; colours only: fur " + FUR + "; white " + WHITE + "; pink " + PINK +
                "; eyes " + EYE + "; paws " + PAW + ".")
FX_LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels (16 px a square), hard edges, "
           "no anti-aliasing, NO outline around light, wind, smoke or glitter, BRIGHT colours (each shape lit with its "
           "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
SQUILL = ("League of Legends' polymorph critter (Lulu's Whimsy, the 'Squill', image 1): a chubby lilac-purple squirrel-"
          "like critter seen FROM THE FRONT, facing the viewer: a big round head with two huge pointed ears (pink "
          "inside with a white fringe), two huge glossy black eyes with a white shine, a white face and muzzle with a "
          "tiny pink nose and a small happy mouth, a white belly, stubby legs with dark paws, and TWO big fluffy tails "
          "rising behind it in a V, lilac with white tips")


def lp(p):
    p = os.path.abspath(p)
    return PRE + p if os.name == "nt" and not p.startswith(PRE) else p


def font(n=16):
    return ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", n)


def frames(path, tag):
    anims = json.load(open(lp(path + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(path + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def crop(f):
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def champ_1x(hero):
    return crop(frames(os.path.join(ROOT, "league", "champions", hero), "idle")[0])


def fighter_1x():
    import tfm2_ase as T
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    return crop(np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA")))


def up(a, z):
    return Image.fromarray(np.ascontiguousarray(a)).resize((a.shape[1] * z, a.shape[0] * z), Image.NEAREST)


def lol_squill(path):
    ref = os.path.join(TMP, "ref")
    os.makedirs(ref, exist_ok=True)
    py = sys.executable
    for y in (0, 30, 90):
        subprocess.run([py, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--champ", "LuluPolymorphCritter", "--wad",
                        "Lulu", "--frame", "lulu_squill_idle@0", "--hq", "--yaw", str(y), "--pitch", "20", "--size", "420",
                        "--width", "1.0", "--fit", "0.6", "--fit-all", "--no-labels", "--name", f"squill_yaw{y}",
                        "--out", ref], check=True, capture_output=True)
    subprocess.run([py, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--champ", "LuluPolymorphCritter", "--wad",
                    "Lulu", "--anim", "idle", "--frames", "6", "--hq", "--yaw", "0", "--fit-all", "--no-labels",
                    "--out", ref], check=True, capture_output=True)
    views = [Image.open(os.path.join(ref, f"squill_yaw{y}.png")).convert("RGB") for y in (0, 30, 90)]
    idle = Image.open(os.path.join(ref, "lulu_squill_idle.png")).convert("RGB")
    W = max(sum(v.width for v in views), idle.width)
    img = Image.new("RGB", (W, views[0].height + idle.height + 60), (60, 64, 50))
    d = ImageDraw.Draw(img)
    d.text((8, 4), "图1：英雄联盟的变形小动物（LuluPolymorphCritter）：正面、斜前、侧面；下面是它的待机（正面）", fill=(255, 255, 255),
           font=font(18))
    x = 0
    for v in views:
        img.paste(v, (x, 30))
        x += v.width
    img.paste(idle, (0, 60 + views[0].height))
    img.save(path)


def now_poly(path):
    fx = os.path.join(ROOT, "league", "effects", "league_lulu_fx")
    hero = champ_1x("league_garen")
    Z = 6
    tiles = []
    for tag, k in (("w_poly_in", 3), ("w_poly", 0), ("w_poly", 3), ("w_poly_out", 1)):
        f = crop(frames(fx, tag)[k])
        H = max(hero.shape[0], f.shape[0]) + 4
        Wd = max(hero.shape[1], f.shape[1]) + 4
        canvas = Image.new("RGBA", (Wd * Z, H * Z), ARENA)
        canvas.alpha_composite(up(hero, Z), (((Wd - hero.shape[1]) // 2) * Z, (H - 2 - hero.shape[0]) * Z))
        canvas.alpha_composite(up(f, Z), (((Wd - f.shape[1]) // 2) * Z, (H - 2 - f.shape[0]) * Z))
        tiles.append((f"{tag} {k + 1}", canvas))
    W = sum(t.width + 12 for _, t in tiles)
    img = Image.new("RGB", (W, max(t.height for _, t in tiles) + 40), (60, 64, 50))
    d = ImageDraw.Draw(img)
    d.text((8, 4), "图2：现在的变形（盖在盖伦身上，游戏尺寸 6 倍）：一团烟 + 一只小松鼠，人还露在外面", fill=(255, 255, 255), font=font(18))
    x = 0
    for name, t in tiles:
        img.paste(t.convert("RGB"), (x, 36))
        d.text((x + 4, 40), name, fill=(255, 255, 255), font=font(14))
        x += t.width + 12
    img.save(path)


def size_sheet(path):
    figs = [("原版斗士", fighter_1x()), ("盖伦", champ_1x("league_garen")), ("璐璐", champ_1x("league_lulu")),
            ("亚索", champ_1x("league_yasuo")), ("瑟庄妮", champ_1x("league_sejuani"))]
    boxes = [("A 36×40", 36, 40), ("B 46×42", 46, 42), ("C 34×30", 34, 30)]
    Z, pad = 6, 6
    W = pad + sum(f.shape[1] + pad for _, f in figs) + sum(b[1] + pad for b in boxes)
    top = max([f.shape[0] for _, f in figs] + [b[2] for b in boxes])
    img = Image.new("RGBA", (W * Z, (pad + top + 6) * Z + 70), ARENA)
    base = (pad + top) * Z + 70
    x = pad
    d = ImageDraw.Draw(img)
    for name, f in figs:
        img.alpha_composite(up(f, Z), (x * Z, base - f.shape[0] * Z))
        d.text((x * Z, base + 4), f"{name} {f.shape[1]}×{f.shape[0]}", fill=(255, 255, 255, 255), font=font(14))
        x += f.shape[1] + pad
    for name, bw, bh in boxes:
        d.rectangle([x * Z, base - bh * Z, (x + bw) * Z, base], outline=(255, 80, 200, 255), width=3)
        d.text((x * Z + 4, base - bh * Z - 20), name, fill=(255, 200, 240, 255), font=font(14))
        x += bw + pad
    d.line([(0, base), (img.width, base)], fill=(220, 40, 40, 255), width=2)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font(14))
    d.text((8, 36), "图3：游戏尺寸（6 倍，1 格 = 1 个游戏像素）：几个英雄和三种小动物的大小（粉框）", fill=(255, 255, 255, 255), font=font(16))
    img.convert("RGB").save(path)


def lol_wall(path):
    src = os.path.join(TMP, "fxref")
    names = ["yasuo_w_windwall_main", "yasuo_w_windwall_main_02", "yasuo_w_wind_wall_mult", "yasuo_w_wind_wispy",
             "yasuo_base_w_windwall_block_impact", "color_yasuo_w_windwall_impact_smoke"]
    ims = []
    for n in names:
        p = os.path.join(src, n + ".png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            s = 280 / max(im.size)
            ims.append((n, im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))))
    W = sum(i.width + 10 for _, i in ims) + 10
    img = Image.new("RGB", (max(W, 900), max(i.height for _, i in ims) + 60), (30, 30, 34))
    d = ImageDraw.Draw(img)
    d.text((8, 4), "图4：英雄联盟风之障壁的贴图（墙身是一道道往上卷的风，蓝白色；挡住东西时一道青白的竖光）", fill=(255, 255, 255), font=font(18))
    x = 10
    for n, i in ims:
        img.paste(i, (x, 50))
        d.text((x, 32), n[:32], fill=(200, 200, 200), font=font(12))
        x += i.width + 10
    img.save(path)


def yasuo_sheet(path):
    f = champ_1x("league_yasuo")
    img = Image.new("RGBA", (f.shape[1] * 4 + 40, f.shape[0] * 4 + 60), ARENA)
    img.alpha_composite(up(f, 4), (20, 40))
    ImageDraw.Draw(img).text((8, 6), f"图5：亚索，游戏尺寸 {f.shape[1]}×{f.shape[0]}（4 倍）", fill=(255, 255, 255, 255), font=font(16))
    img.convert("RGB").save(path)


def cells(n, cw, ch):
    return (f"one horizontal row of {n} equal cells, image size {n * cw * 16}x{ch * 16} (each cell {cw * 16}x{ch * 16}, "
            "16 px a square)")


def document():
    L = []
    a = L.append
    a("# 璐璐的变形小动物 + 亚索的风之障壁（给 Codex）")
    a("")
    a("用户 2026-10-24：「接着做璐璐变形：先出小动物的设计给我审」「还有个亚索风墙吧？但是亚索风墙要智能点放啊」"
      "「你要做风墙的特效也一起把压缩包整理了」。")
    a("")
    a("**顺序**：先画第 1 张（小动物的三种设计 A / B / C），交给用户挑；挑好之后再画第 2-4 张（变形的出现、循环、散开，照挑中的那只画）。"
      "亚索的四张（第 5-8 张）和小动物无关，可以和第 1 张一起画。每张一个 PNG，按下面的文件名交付。")
    a("")
    a("**参考图**（按编号上传）：图1 英雄联盟的变形小动物（正面、斜前、侧面、待机），图2 现在的变形（一团烟 + 小松鼠，人还露在外面），"
      "图3 游戏尺寸对照（几个英雄和三种小动物的大小），图4 英雄联盟风之障壁的贴图，图5 亚索的游戏尺寸。")
    a("")
    a("**为什么要盖住人**：游戏换不了被变形的敌人的模型（引擎不给改别的英雄的贴图），只能在他身上叠一张跟着他走的图。"
      "所以小动物要**大到能把人盖住**（A、B），或者像现在这样小、坐在一团烟上（C）。**画面挂在人身上，左右必须对称**"
      "（游戏在红方不翻转特效）：小动物**正面朝着我们**，不画侧面。")
    a("")
    a("---")
    a("")
    a("## 1. `squill_design.png`：小动物的三种设计（游戏尺寸），给用户挑")
    a("")
    a("三格并排（游戏里的英雄约 35-48 格宽、34-42 格高，见图3）：**A 盖住人**——英雄联盟那只小动物正面站着，连两条竖起来的大尾巴约 36 格宽、40 格高，"
      "把一般英雄的头和身体大半挡住；**B 盖住人 + 魔法烟**——同一只小动物约 30 × 32，坐在一团粉紫魔法烟上（烟约 46 格宽、14 格高，在脚下），合起来约 46 × 42，"
      "拿大剑、骑野猪的宽英雄也能挡住大半；**C 小一点**——同一只小动物约 20 × 22，坐在一团大烟雾前面（同现在的做法，烟约 34 × 30），"
      "小动物照英雄联盟的样子重画。三只都是**正面、左右对称**。")
    a("")
    a("```text")
    a(CRITTER_LEAD + " Lulu's pink magic puff (B and C only, no outline): " + MAGIC + "; violet: " + VIOLET + ".")
    a("Subject: " + SQUILL + ". Three design options side by side, each " + LR + ":")
    a("A) the critter standing, 36 squares wide and 40 tall from the tails' tips to its paws, big enough to hide most of a "
      "champion about 40 squares wide and 40 tall standing behind it (head and body in the middle 26 squares, the tails in "
      "a V above and behind the head);")
    a("B) the same critter 30 wide and 32 tall sitting on a puffy cloud of pink and violet magic smoke 46 squares wide and "
      "14 tall at its feet (glitter in the smoke, no outline on the smoke), 46 x 42 together;")
    a("C) the same critter small, 20 wide and 22 tall, sitting in front of a big billowing cloud of pink and violet magic "
      "smoke 34 squares wide and 30 tall that fills the cell's lower middle.")
    a("Match image 1's look (colours, the huge glossy eyes, the pink-lined ears, the two white-tipped tails); the face must "
      "read at game size: 2x2-square eye whites at least, the eyes the darkest thing on it. Nothing below the feet line.")
    a("Layout: " + cells(3, 50, 48) + "; the feet (or the smoke's bottom) 2 squares above each cell's bottom, centered. " + TAIL)
    a("```")
    a("")
    a("## 2-4. 变形的三段（用户挑好设计后再画；把挑中的那一格作为第一张参考图）")
    a("")
    a("游戏里叫 `league_lulu_w_poly`（ThreePhase：出现 `w_poly_in` → 循环 `w_poly` → 散开 `w_poly_out`），挂在被变形的敌人身上，跟着他走，"
      "1.75 秒。格子和第 1 张一样大，人的脚在格子底上 2 格、水平居中。三段都**左右对称**。")
    a("")
    for i, (fname, n, what, en) in enumerate([
        ("lulu_fx_w_poly_in.png", 4, "砰地一下：白粉闪光，一团粉紫魔法烟罩住人，最后一帧烟里蹦出挑中的那只小动物（和循环第 1 帧一样大、一样的位置）",
         "1 a white-pink flash in the middle; 2 a round puff of pink and violet magic smoke bursts out, as big as the "
         "chosen design's whole shape; 3 the puff at full size, glitter in it; 4 the chosen critter popping out of the "
         "thinning puff, exactly where and as big as in the loop's first frame"),
        ("lulu_fx_w_poly.png", 6, "无缝循环：挑中的那只小动物一跳一跳（身体上下 1 格）、两条尾巴左右摇、耳朵抖一下，头上冒两三颗小星星；有烟的设计烟慢慢翻滚",
         "a seamless loop of the chosen design: the critter bobs 1 square up and down, its two tails sway left and right "
         "(mirrored, so it stays symmetric), its ears twitch once, 2-3 tiny pink stars twinkle over its head; any smoke "
         "rolls slowly"),
        ("lulu_fx_w_poly_out.png", 4, "变形结束：小动物噗地变成一团闪粉，烟往四周散开，露出下面的人",
         "1 a white-pink flash where the critter is, the critter gone; 2 a puff bursting outward; 3 the puff breaking into "
         "pink and violet glitter at the cell's edges, the middle empty; 4 a few fading specks"),
    ], start=2):
        a(f"### {i}. `{fname}`，{n} 帧")
        a("")
        a(what + "。")
        a("")
        a("```text")
        a(CRITTER_LEAD + " Pink magic (no outline): " + MAGIC + "; violet: " + VIOLET + ".")
        a(f"The POLYMORPH of a champion into the critter of image 1 (the design the user picked) - {n} frames, " + LR +
          ": " + en + ". Do not draw the champion: the critter (and smoke) hides him.")
        a("Layout: " + cells(n, 50, 48) + "; the feet 2 squares above each cell's bottom, centered. " + TAIL)
        a("```")
        a("")
    a("---")
    a("")
    a("## 5-8. 亚索的风之障壁")
    a("")
    a("英雄联盟的 W：亚索在身前竖起一面风墙，4 秒，挡掉敌人飞过来的东西（普攻的弹、技能弹）。游戏里：墙是一个慢慢往前飘的投射物，"
      "**投射物的图会跟着飞行方向转**，所以墙画成**朝右飞**的样子——一道**竖着**的风墙（飞行方向朝右，墙面上下展开），**上下对称**；"
      "其他三张（出手的风、挡住东西的一下、墙散掉）不会转，画成**左右对称**。颜色照英雄联盟：白色到浅蓝、钢蓝的风（参考图4）。")
    a("")
    walls = [
        ("yasuo_w_wall.png", "墙身（投射物，循环），6 帧", 16, 52,
         "a WIND WALL seen as it flies RIGHT: a vertical curtain of swirling wind 6-8 squares thick (left to right) and 48 "
         "squares tall (top to bottom), bulging slightly to the RIGHT in the middle (a shallow arc), made of white and "
         "pale blue wind streaks curling upward, a bright white core line down its middle, small wisps peeling off its "
         "right face; 6 frames, a seamless loop (the streaks crawl upward); SYMMETRIC TOP TO BOTTOM in every frame, square "
         "for square (the game turns the picture with its flight)", WIND + "; grey-blue dust " + STEEL,
         "墙厚 6-8 格（左右）、高 48 格（上下），中间稍微往右鼓；风一道道往上卷，中间一条白色的芯，右边（朝敌人那面）飘出小风丝；6 帧无缝循环，上下对称"),
        ("yasuo_w_cast.png", "出手的风（亚索脚下），4 帧", 32, 24,
         "a GUST at a swordsman's feet as he flicks up a wall of wind: 1 a white flash at the middle bottom; 2 two curls of "
         "wind sweeping up and out to both sides, 26 squares wide and 18 tall; 3 the curls at full size, dust at the "
         "bottom; 4 fading wisps. " + LR, WIND + "; grey-blue dust " + STEEL,
         "亚索竖墙时脚下卷起的一阵风：白光一闪，两道风往两边往上卷开（约 26 × 18），带一点地上的灰，最后散成风丝；左右对称"),
        ("yasuo_w_block.png", "挡住东西的一下，4 帧", 16, 20,
         "a BLOCK FLASH where a missile hits the wind wall: 1 a white vertical spark 4 squares wide and 14 tall; 2 a pale "
         "cyan diamond flare 10 wide and 16 tall with a white core (like image 4's block impact); 3 the flare breaking into "
         "small wind wisps; 4 two fading wisps. " + LR, WIND,
         "飞过来的弹撞在墙上被挡掉：一道白色竖光、青白色的菱形光（参考图4的 block_impact），然后散成小风丝；左右对称，约 10 × 16"),
        ("yasuo_w_fade.png", "墙散掉，4 帧", 28, 28,
         "the WIND WALL DISPERSING (round, because the game cannot turn this one): 1 a ring of white and pale blue wind "
         "wisps 24 squares across; 2 the wisps spiralling outward and thinning; 3 a few wisps; 4 two fading specks. " + LR +
         " and top to bottom", WIND,
         "墙到时间散掉：一圈白蓝色的风丝往外旋开、变淡（画成圆的：这张图不会跟着墙转）；左右上下都对称，约 24 × 24"),
    ]
    for i, (fname, title, cw, ch, en, ramps, zh) in enumerate(walls, start=5):
        a(f"### {i}. `{fname}`：{title}")
        a("")
        a(zh + "。")
        a("")
        a("```text")
        a(FX_LEAD.format(ramps="a wind ramp (" + ramps + ")"))
        a("Effect: " + en + ".")
        n = 6 if "wall.png" in fname else 4
        a("Layout: " + cells(n, cw, ch) + "; centered in every cell. " + TAIL)
        a("```")
        a("")
    a("---")
    a("")
    a("交付：8 个 PNG（文件名照上面），透明背景，格子严格对齐。")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "squill_windwall_packs"))
    a = ap.parse_args()
    pack = os.path.join(TMP, NAME)
    shutil.rmtree(pack, ignore_errors=True)
    os.makedirs(os.path.join(pack, "refs"))
    lol_squill(os.path.join(pack, "refs", "01_lol_squill.png"))
    now_poly(os.path.join(pack, "refs", "02_now_poly.png"))
    size_sheet(os.path.join(pack, "refs", "03_size.png"))
    lol_wall(os.path.join(pack, "refs", "04_lol_windwall.png"))
    yasuo_sheet(os.path.join(pack, "refs", "05_yasuo.png"))
    doc = document()
    open(os.path.join(pack, "PROMPTS.md"), "w", encoding="utf-8", newline="\n").write(doc)
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    open(lp(DOC), "w", encoding="utf-8", newline="\n").write(doc)
    if not a.no_zip:
        os.makedirs(a.out, exist_ok=True)
        z = os.path.join(a.out, NAME + ".zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for d, _, fs in os.walk(pack):
                for f in fs:
                    p = os.path.join(d, f)
                    zf.write(p, os.path.relpath(p, os.path.dirname(pack)))
        print("wrote", z)
    print("pack", pack)


if __name__ == "__main__":
    main()
