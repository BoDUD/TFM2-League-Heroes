#!/usr/bin/env python3
"""Build meepsie_fx_pack.zip: step 3 of Meepsie's sprite - Codex draws its effects and its three skill icons (the tft
heroes' way, pack_sentinel_fx.py's).

    python tools/lol/fx_ref_meepsie.py            # the particle references -> C:/t/mp_work/fxref
    python tools/art/pack_meepsie_fx.py [--no-zip] [--out DIR] [--only a_hit,r_slam --name meepsie_fx_redo_pack]

The pack (C:/t/mp_work/fx/meepsie_fx_pack, zipped into --out, default D:/TFM2-Workshop/meepsie_packs) holds PROMPTS.md
(also written to assets/source/meepsie/PROMPTS_FX.md), design/meepsie_design.png (the approved idle at 4x on its own
squares), design/meepsie_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (its own set-17 particle textures, Daisy's (Ivern's golem: her slam and
shockwave), Ivern's and Bard's - grey shapes the game tints, grouped by the effect they inform). The effects are the
views the kit binds (tools/kit/build_meepsie.py, the user's picks 2026-11-01: support, plan A 「木灵守护」):
view_projectiles q_wave, e_meep (tft.dll's homing meeps); view_effects a_hit, q_hit, e_cast, r_slam, r_up (tft.dll's
knock-up); view_buffs q_slow, e_hot. Plus the three skill icons.
Its colours: pale moon rock and moon dust, the purple-violet starlight of its belt and mushrooms, the lime green of the
meep pilot (the heals).
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying dust wave and the flying meep are symmetric top to bottom, pointing right.
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/mp_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "meepsie", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "meepsie", "hd")
NAME = "meepsie_fx_pack"
PPU = 2.875

MOON = "#FFFFFF, #E6F4FF, #B8D8F2, #86A8D6, #5A6EA8, #353E70"    # its pale cratered moon rock
DUST = "#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A"             # the moon dust its fists throw up
STAR = "#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A"    # purple-violet starlight (its belt, its mushrooms)
MEEP = "#FAFFE2, #E2F78C, #B6E04C, #7EB82E, #4C8A22, #2A5418"    # the lime-green meeps, the heals
MO = f"a moon-rock ramp ({MOON})"
DU = f"a moon-dust ramp ({DUST})"
ST = f"a violet starlight ramp ({STAR})"
ME = f"a lime meep-green ramp ({MEEP})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, "
         "purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, "
         "crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams")
HIM = ("the golem stands in the middle, not drawn: about 48 squares wide and 40 tall, its two huge fists low at its "
       "sides, its leaf-and-mushroom cap on top, its crater cockpit with the little meep at the upper right")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark indigo frame with little "
        "violet star corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art "
        "at 2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「月岩重拳」+ 被动「木灵驾驶员」：拳头砸中，4 帧", "view_effects `tft_meepsie_a_hit`（跟随目标，z 2；左右对称）",
     "16 × 14",
     "拳头砸中：一团浅蓝白的**月尘**往两边崩开，几块带陨石坑的小月岩飞出去，中间一下**紫色的小星星闪光**"
     "（小木灵附带的魔法伤害）。**左右对称**，4 帧。",
     DU + ", " + MO + ", " + ST,
     "A MOON-ROCK PUNCH, 4 frames, " + LR + ": 1 a pale white-blue flash 5 squares across with a small violet "
     "FIVE-POINT STAR in its middle; 2 a puff of pale moon dust bursting out to both sides, 12 squares across, a few "
     "small cratered moon-rock chips flying out (mirrored), the violet star at its brightest; 3 the chips falling "
     "outward, the dust spreading low, two tiny violet sparkles; 4 the last dust and one chip on each side. "
     + MAGIC + ".",
     row(4, 16, 14) + CENTER),
    ("q_wave", "技能 1「月尘震地」：往前推的月尘震波，6 帧循环", "view_projectiles `tft_meepsie_q_wave`（大表，一道从它拳头指向前方的线，"
     "随方向旋转；上下对称、朝右）", "60 × 26",
     "拳头砸地后，地面上**一股月尘震波往右推开**：左端（拳头砸地的地方）窄，往右越来越宽，像扇形；"
     "一路上小月岩一块块跳起来又落下，前沿是一道翻滚的浅蓝白尘浪，里面夹着几点紫色星光。**上下对称、朝右**，6 帧循环。",
     DU + ", " + MO + ", " + ST,
     "A MOON-DUST QUAKE WAVE, 6 looping frames, " + TB + ": on the ground, seen from above at a slant: a FAN of rolling "
     "pale moon dust spreading from the LEFT edge (6 squares wide there, where the fist struck) to the RIGHT (24 squares "
     "wide at the right edge), its front a curling wave of white-blue dust; small cratered moon-rock chips hopping up "
     "and dropping along it (mirrored top and bottom), a few tiny violet star sparkles inside the dust; frames 1-6 the "
     "dust rolling forward, the chips hopping in turn, the front wave curling (every frame top-bottom symmetric). "
     + MAGIC + ".",
     row(6, 60, 26) + CENTER),
    ("q_hit", "技能 1「月尘震地」：被震中，4 帧", "view_effects `tft_meepsie_q_hit`（跟随被震中的人，z 3；左右对称）", "22 × 18",
     "被震波打中的人：脚下的地面**一下震起一圈月尘**，几块小月岩跳起来，一点紫色星光一闪。**人站的地方留空**。**左右对称**，4 帧。",
     DU + ", " + MO + ", " + ST,
     "A QUAKE JOLT, 4 frames, " + LR + ": round the FEET and lower legs of " + CHAMP + ": 1 a pale flash on the ground "
     "under its feet with a small violet star; 2 a ring of moon dust jumping up round its feet (an ellipse 20 squares "
     "wide, 6 tall), three small moon-rock chips hopping up beside its legs (mirrored); 3 the dust high as its knees, "
     "the chips at their highest; 4 the dust settling, the chips dropping. The middle of the cell (its body) stays "
     "EMPTY. " + MAGIC + ".",
     row(4, 22, 18) + CENTER),
    ("q_slow", "技能 1「月尘震地」：减速，6 帧循环", "view_buffs `tft_meepsie_q_slow`（跟随被减速的人，脚下，z 3；左右对称）", "24 × 8",
     "被减速的人：脚边**一层沉沉的月尘**粘着脚踝，几块小月岩在脚边滚，像踩在月球表面一样走不动。很淡、只在脚下。**左右对称**，6 帧循环。",
     DU + ", " + MO,
     "MOON-DUST DRAG, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): a heavy low haze "
     "of pale moon dust clinging round the ankle line, on EACH side (mirrored) two small cratered moon-rock pebbles "
     "rolling slowly; frames 1-6 the dust swelling and sinking a square, the pebbles rolling a square (every frame "
     "left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("e_cast", "技能 2「治疗木灵」：木灵飞出，5 帧", "view_effects `tft_meepsie_e_cast`（大表，跟随它，z 3；左右对称）", "60 × 52",
     "驾驶员一招手，**四只绿色小木灵从它身上蹦出来**，往左右两边飞起（左边两只、右边两只，对称），身后拖着绿色亮点和几颗紫色小星星，"
     "最后化成光点往上飘。**它的身体位置留空**。**左右对称**，5 帧。",
     ME + ", " + ST,
     "MEEPS POPPING OUT, 5 frames, " + LR + ": round " + HIM + ": 1 a ring of small lime-green sparkles appearing round "
     "the top of its body; 2 FOUR little lime-green MEEPS (round bean bodies 5 squares across, two big black eye "
     "squares, a tiny antenna) popping up from its top edge, two flying out to the LEFT and two to the RIGHT (mirrored), "
     "a trail of green sparkles behind each; 3 the meeps higher and further out, small violet stars twinkling round "
     "them; 4 the meeps at the cell's upper corners, the trails fading; 5 only green and violet motes drifting UP. The "
     "middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(5, 60, 52) + CENTER),
    ("e_meep", "技能 2「治疗木灵」：飞向队友的小木灵，4 帧循环", "view_projectiles `tft_meepsie_e_meep`（tft.dll 放的追踪弹道，"
     "随飞行方向旋转；上下对称、朝右）", "14 × 8",
     "飞去治疗队友的小木灵：**一只缩成一团的绿色小木灵，裹在绿色光球里**往右飞，身后一道短短的绿色亮点尾巴，夹着一两颗紫色小星星。"
     "**上下对称、朝右**，4 帧循环。",
     ME + ", " + ST,
     "A FLYING MEEP, 4 looping frames, " + TB + ": a little lime-green meep curled up into a round GLOWING BALL 6 squares "
     "across at the RIGHT, a near-white core, a soft lime glow ring round it, a short trail of lime sparkles behind it "
     "to the LEFT with one tiny violet star; frames 1-4 the ball pulsing and the sparkles trailing (every frame "
     "top-bottom symmetric). " + MAGIC + ".",
     row(4, 14, 8) + CENTER),
    ("e_hot", "技能 2「治疗木灵」：持续治疗，6 帧循环", "view_buffs `tft_meepsie_e_hot`（跟随被治疗的人，z 3；左右对称）", "24 × 32",
     "被小木灵治疗的人：脚下一圈**淡绿色的小光环**，绿色的光点和几片小叶子沿着身子两侧往上飘，头顶偶尔一颗紫色小星星。"
     "**人站的地方留空**。**左右对称**，6 帧循环。",
     ME + ", " + ST,
     "A MEEP MENDING GLOW, 6 looping frames, " + LR + ": round " + CHAMP + ": a thin lime-green ring on the ground at "
     "its feet (an ellipse 20 squares wide, 6 tall); small lime motes (2x2 and 1x1 squares) and tiny green leaves "
     "rising up both sides of the body (mirrored), one small violet star twinkling above its head; frames 1-6 the motes "
     "and leaves rising and fading at the top, new ones from the ring, the ring breathing (every frame left-right "
     "symmetric). The middle (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 24, 32) + CENTER),
    ("r_slam", "大招「宇宙大爆炸」：落地爆炸，6 帧", "view_effects `tft_meepsie_r_slam`（大表，放在它落地的地面上，不跟随，z -1；左右对称）",
     "96 × 44",
     "它从天上砸回地面：一下巨大的白紫色闪光，地面上**一个很大的星光冲击环**炸开（从斜上方看的椭圆），"
     "环上全是紫色星光和浅蓝白月尘，大块月岩翘起、碎石往两边飞，空中散开一片紫色星云和小星星。**只在地面和低处**。**左右对称**，6 帧。",
     ST + ", " + DU + ", " + MO,
     "THE BIG BANG, 6 frames, " + LR + ": on the GROUND and low above it, seen from above at a slant: 1 a huge "
     "white-violet flash at the middle bottom, 24 squares wide, a burst of short star rays; 2 a thick bright violet "
     "STARLIGHT SHOCKWAVE RING bursting open on the ground (an ellipse 50 squares wide, 16 tall), pale moon dust rolling "
     "out with it, big cratered moon-rock slabs tilting up on both sides (mirrored), small five-point stars flung up; "
     "3 the ring 84 squares wide, a low violet NEBULA puff over the middle, stars and chips flying out; 4 the ring at "
     "the cell's edge and thinning, the slabs sinking, the stars twinkling as they fall; 5 the settling dust and a few "
     "stars; 6 the last sparkles. " + MAGIC + ".",
     row(6, 96, 44) + CENTER),
    ("r_up", "大招「宇宙大爆炸」：被击飞，5 帧", "view_effects `tft_meepsie_r_up`（跟随被击飞的人，z 3；左右对称）", "22 × 28",
     "离落点最近、被击飞的人：身边**一圈紫色星星绕着转**着往上飞，脚下一下月尘冲起来。**人站的地方留空**。**左右对称**，5 帧。",
     ST + ", " + DU,
     "A STARRY KNOCK-UP, 5 frames, " + LR + ": round " + CHAMP + ": 1 a puff of moon dust shooting up under its feet; "
     "2 a ring of small violet five-point STARS round its waist (mirrored), a thin violet streak up each side; 3 the "
     "stars swirled up to its chest and head, bright; 4 the stars above its head, twinkling; 5 the last two stars and "
     "falling dust. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(5, 22, 28) + CENTER),
]
ICONS = [
    ("skill", "技能 1「月尘震地」图标", "skill_icons[0] `asset/tft/icons/tft_meepsie_skill`",
     ICON + ": a huge pale cratered moon-rock fist smashed into the ground at the lower left, a fan of moon dust and "
               "hopping rock chips rolling out toward the upper right, a few violet star sparkles in it."),
    ("skill2", "技能 2「治疗木灵」图标", "skill_icons[1] `asset/tft/icons/tft_meepsie_skill2`",
     ICON + ": three little lime-green meeps (big black eyes, tiny antennae) flying in an arc, each in a soft green glow, "
               "a green heal cross sparkle between them."),
    ("ult", "大招「宇宙大爆炸」图标", "skill_icons[2] `asset/tft/icons/tft_meepsie_ult`",
     ICON + ": a pale moon-rock golem crashing down fists first into a bursting violet starlight explosion, a ring of "
               "stars and moon dust flying out, a tiny green meep in its chest cockpit."),
]
BIG_FX = ["q_wave", "e_cast", "r_slam"]
FLYING = ("q_wave", "e_meep")

GROUPS = [
    ("a_hit q_hit (the punch, the jolt)",
     ["ivernminion_base_ba_flash", "ivernminion_base_ba_flash_core", "tft17_hit_tar_a", "tft16_pebbles_2x2",
      "tft_base_dust"]),
    ("q_wave q_slow r_slam (the quake, the big bang)",
     ["ivern_base_r_shockwave_ground", "ivern_base_r_shockwave_rock", "ivern_base_r_dust_ring", "tft16_shockwave_01",
      "sru_groundcracks_3x1", "ivern_base_r_dirt_splatter"]),
    ("e_cast e_meep e_hot (the meeps, the heal)",
     ["bard_base_m_meep_override", "tft17_bardfollower_base_body1_tx_cm", "tft17_bardfollower_base_eyes_tx_cm",
      "ivern_base_r_petals", "ivern_base_p_leaf_finished", "tft17_starglow_1x2_a"]),
    ("r_slam r_up (the stars)",
     ["tft17_poppy_base_star", "tft17_starglownoglowinside_1x2_a", "jhin_skin05_stars",
      "portal2_ninjascroll_tft_journeys_sparkles_2x2", "ivernminion_base_r_stacks_glow"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The golem at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x()]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] for f in figs)
    img = Image.new("RGBA", (max(W * Z, 560), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
    x = pad
    for f in figs:
        img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                            (x * Z, (base - f.shape[0]) * Z + 64))
        x += f.shape[1] + pad
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"小木灵 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 小木灵：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/meepsie_design.png`："
      "3/4 朝右、没有脑袋的浅蓝白月岩巨像：带陨石坑的大石块、两只巨拳、靛蓝短腿、紫色腰带；头顶和背上长着绿叶和紫蘑菇；"
      "胸口高处的白边陨石坑驾驶舱里坐着绿色小木灵）。"
      f"小木灵在游戏里是**高清**的（每个游戏格子里约 2.9×2.9 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/meepsie_size.png`：小木灵缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是它自己（金铲铲第 17 季）、小菊（艾翁的石头巨像：砸地、冲击波）、艾翁和巴德（小木灵）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **小木灵是月岩巨像加一只绿色小木灵驾驶员，特效都是它的味道**：浅蓝白的月尘、带陨石坑的小月岩、"
      "紫色的星光和五角小星星（大招是「宇宙大爆炸」）、治疗用小木灵的嫩绿色光；不要火焰、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了往前推的月尘震波 `q_wave` 和飞行的小木灵 `e_meep`（上下对称、朝右），所有画面都**严格左右对称**"
      "（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `meepsie_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `meepsie_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「月岩重拳」+ 被动「木灵驾驶员」 | 一拳砸下，小木灵每拳附带魔法伤害 | `a_hit` |")
    a("| 技能 1 =「月尘震地」 | 一拳砸地，月尘震波往前扇形推开：魔法伤害、减速 | `q_wave` · `q_hit` · `q_slow` |")
    a("| 技能 2 =「治疗木灵」 | 四只小木灵飞向血量最低的队友（和它自己），持续治疗 | `e_cast` · `e_meep` · `e_hot` |")
    a("| 大招 =「宇宙大爆炸」 | 跳到敌人最多的地方砸地：中心伤害最高、往外递减，最近的三个敌人被击飞 | `r_slam` · `r_up` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("月岩（浅蓝白）", MOON), ("月尘", DUST), ("星光紫（它的腰带和蘑菇）", STAR), ("木灵绿（治疗）", MEEP)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `meepsie_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `meepsie_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `meepsie_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `meepsie_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_meepsie_fx`（小的）和 `tft_meepsie_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- q_wave、e_meep 断言上下对称（朝右），其余断言左右对称。")
    a("- q_wave 是从它拳头出发的一条只有画面的线（它的左端对着拳头）；e_meep 是 tft.dll 放的追踪弹道（飞向队友）；"
      "r_slam 放在它落地的地面上（不跟随，z -1）；e_cast 是它身上的 caster 画面；a_hit、q_hit 是打中的画面；"
      "r_up 是 tft.dll 在被击飞的人身上播的；q_slow 是敌人身上的 buff，e_hot 是队友身上的 buff。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="meepsie_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/meepsie_packs", help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    RF.REF, RF.GROUPS = REF, GROUPS
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_meepsie.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "meepsie_design.png"))
    shape = size_sheet(os.path.join(out, "design", "meepsie_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"meepsie_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"meepsie_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
                   if not a.only else []), f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(lp(zpath)):
            os.remove(lp(zpath))
        with zipfile.ZipFile(lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
