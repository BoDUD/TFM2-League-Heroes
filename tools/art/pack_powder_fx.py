#!/usr/bin/env python3
"""Build powder_fx_pack.zip: step 3 of Powder's sprite - Codex draws her effects and her three skill icons
(pack_zoe_fx.py's way, pack_rammus_fx's sheets reused).

    python tools/art/pack_powder_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name powder_fx_redo_pack]

References: C:/t/pw_work/fxref - the particle textures her TFT skin names (TFTSet13.wad.client, TFT13_Blue: the monkey
prop, the broken monkey bits, her bomb barrel, the hit stars, smoke, splashes) and monkey_model.png (her wind-up
monkey bomb, the skin's Monkey submesh) - Riot's art, local only.
The effects are the views the kit binds (tools/kit/build_powder.py): view_projectiles a_pop (the firecracker), q_monkey
(the monkey bomb), r_bag (the bag with the hex crystal); view_effects a_hit, q_blast, q_hit, e_smoke, e_blind, r_cast,
r_warn, r_fuse, r_blast, r_hit; view_buffs q_wound. Plus the skill icons icon_skill / icon_skill2 / icon_ult (64 x 64).
Arcane / TFT colours: her firecrackers and bombs are homemade (red-pink paper, brass, string), the monkey a blue
wind-up toy with brass cymbals and a peach face, her explosions orange-gold fire with pink and blue smoke, the hex
crystal cyan-blue light. Red side: the client never mirrors an effect picture, so every hit, buff and ground picture
is symmetric left to right; the three projectiles tumble in the air (any turn of the picture reads).
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/pw_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "powder", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "tft", "champions", "tft_powder")
NAME = "powder_fx_pack"

FIRE = "#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14"         # orange-gold fire
SMOKE = "#FFE6F4, #FFA8D8, #E066B8, #8E4AB8, #5A3A8C, #2E2246"        # Jinx's pink-violet smoke
PAPER = "#FFD8D8, #FF7A8A, #E23A52, #A21E36, #5E1220"                 # red-pink firecracker paper (solid: outlined)
BRASS = "#FFF2B0, #F2C850, #C8902A, #8A5A1A, #4A2E10"                 # brass cymbals, string, fuse caps (solid)
TOY = "#BFF0FF, #5ACBF5, #1E8ED8, #145AA8, #0C2E66"                   # the monkey's blue body (solid: outlined)
HEX = "#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80"          # the hex crystal's light
GREEN = "#F0FFE0, #B8FF7A, #5AE85A, #22A04A, #10582A"                 # the barrel's green swirl eyes, toxic splash
FI = f"an orange-gold fire ramp ({FIRE})"
SM = f"a pink-violet smoke ramp ({SMOKE})"
PA = f"a red-pink paper ramp ({PAPER})"
BR = f"a brass ramp ({BRASS})"
TO = f"a blue toy ramp ({TOY})"
HX = f"a cyan-blue hex crystal light ramp ({HEX})"
GR = f"a lime-green ramp ({GREEN})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the "
                       "firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline)")
LR = RF.LR
TUMBLE = ("TUMBLING through the air: each frame the object a quarter turn further round (so the game may turn the picture "
          "any way - it always reads), a short spark trail")
CENTER = RF.CENTER
HER = "the small girl stands in the middle, not drawn: 32 squares from her crown to the ground, about 18 squares wide"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack: the firecracker
    ("a_pop", "普攻：扔出去的小鞭炮（弹道，循环），4 帧", "view_projectiles `tft_powder_a_pop`（跟着弹道转向；翻滚）", "10 × 10",
     "她普攻扔出去的自制小鞭炮：一根短短的红粉色纸筒，一头扎着黄铜色的引线，引线头冒着金黄的小火星。**在空中翻滚**（每帧转四分之一圈，"
     "游戏怎么转这张图都对），4 帧循环。",
     f"{PA}, {BR} and {FI}",
     "A HOMEMADE FIRECRACKER, 4 frames, a seamless loop, " + TUMBLE + ": a short red-pink paper tube 6 squares long and 3 "
     "thick with a brass cap at each end and a lit fuse at one end throwing 3-4 gold spark squares.",
     row(4, 10, 10) + CENTER),
    ("a_hit", "普攻：小鞭炮炸开（目标身上），3 帧", "view_effects `tft_powder_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "小鞭炮在目标身上啪地炸开：一团金白色的小闪光，四周溅出几粒红粉色的纸屑和火星（参考 jinx_skin60_ba_hit_impact、tar_flashglow）。"
     "**左右对称**。",
     f"{FI} and {PA}",
     "A SMALL FIRECRACKER POP, 3 frames, " + LR + ": 1 a white-gold star flash 6 squares across; 2 the flash 9 across with 6 "
     "gold sparks and red-pink paper bits flying out; 3 only the bits and sparks further out, fading.",
     row(3, 12, 12) + CENTER),
    # ---- skill: Monkey Bomb
    ("q_monkey", "技能1 猴子炸弹：飞出去的猴子（弹道，循环），4 帧", "view_projectiles `tft_powder_q_monkey`（跟着弹道转向；翻滚）",
     "16 × 16",
     "她丢出去的发条猴子炸弹：一只蓝色的玩具猴，肉色的脸咧着大嘴笑，两只手各抓一片黄铜钹，背上一把发条钥匙，头顶一根点着的引线冒火星"
     "（参考 monkey_model、monkey_prop_tft13_blue）。**在空中翻滚**（每帧转四分之一圈），4 帧循环。",
     f"{TO}, {BR}, {FI} and a peach skin ramp (#FFE2C8, #F2B08A, #C87A5A)",
     "A WIND-UP TOY MONKEY BOMB, 4 frames, a seamless loop, " + TUMBLE + ": a chubby blue toy monkey 12 squares tall, a "
     "round peach face with a wide toothy grin and two black eyes, a brass cymbal in each hand, a brass wind-up key on its "
     "back, a lit fuse on its head spitting 3 gold spark squares; 1-square near-black outline round the monkey.",
     row(4, 16, 16) + CENTER),
    ("q_blast", "技能1：猴子炸弹爆炸（地上的点，不跟随，大图），6 帧", "view_effects `tft_powder_q_blast`（不跟随，画在人物上面 z 2；左右对称；大图表）",
     "40 × 34",
     "猴子炸弹落地爆炸：先一团白金色的大闪光，再炸成橙金色的火球，外面一圈粉紫色和蓝色的烟，碎钹、螺丝、玩具零件往外飞，最后烟散开"
     "（参考 broken_monkey_tft13_blue、olaf_skin16_explosion_smoke_mult、jinx_skin60_ba_hit_impact）。中心全额、外圈减半，所以爆炸要看得出"
     "一个亮的中心和一圈外围。**左右对称**，底部贴着地面。",
     f"{FI}, {SM}, {BR} and {TO}",
     "A TOY BOMB EXPLOSION on the ground, 6 frames, " + LR + ": 1 a white-gold flash 12 squares across on the ground; 2 an "
     "orange-gold fireball 24 across, a bright white core 8 across; 3 the fireball 32 across, a ring of pink-violet and "
     "blue smoke puffs round it, 6 flying toy bits (brass cymbal halves, screws, blue toy pieces with outlines) at "
     "mirrored places; 4 the smoke ring 38 across, the fire shrinking inside it, the bits further out; 5 the smoke "
     "rising and thinning, a few embers; 6 only thin pink smoke wisps.",
     row(6, 40, 34) + "; centered across, the blast's bottom on the cell's bottom row."),
    ("q_hit", "技能1：被炸到的敌人（他身上，跟随），4 帧", "view_effects `tft_powder_q_hit`（跟随目标，画在人物上面 z 2；左右对称）",
     "16 × 16",
     "被猴子炸弹炸到的敌人：身上一团火焰冒起来，夹着几粒绿色的毒液飞溅（她的炸弹桶里冒的绿光，参考 tft13_blue_base_toxic_splashes2）。"
     "**左右对称**。",
     f"{FI} and {GR}",
     "A BURNING HIT on a unit, 4 frames, " + LR + ": 1 a white-gold flash 8 squares across; 2 orange flames 12 across "
     "licking upward with 4 lime-green splash drops; 3 the flames 14 tall, flickering, the drops falling; 4 smaller "
     "flames and two green drops.",
     row(4, 16, 16) + CENTER),
    ("q_wound", "技能1：灼烧 + 重伤（敌人身上，循环），4 帧", "view_buffs `tft_powder_q_wound`（跟随，画在人物上面 z 3；左右对称；循环）",
     "14 × 10",
     "灼烧和重伤的 4 秒：敌人身上几小簇橙色的火苗一闪一闪，中间一个裂开的红色小十字（治疗被削弱）。**画在身体中段**，**左右对称**，4 帧循环。",
     f"{FI} and a red ramp (#FFB0B0, #FF4A4A, #B01E2A, #5E0E16)",
     "A BURN-AND-WOUND MARK, 4 frames, a seamless loop, " + LR + ": 3 small orange flames (3 squares wide, 4 tall) at mirrored "
     "places flickering in turn, and in the middle a small red cross 5 squares across with a crack through it (solid, "
     "near-black outline) that pulses brighter on frames 2 and 4.",
     row(4, 14, 10) + CENTER),
    # ---- skill2: Run, Powder!
    ("e_smoke", "技能2 快跑，爆爆！：脚下的闪光烟雾弹（她身上，跟随，大图），6 帧",
     "view_effects `tft_powder_e_smoke`（CasterViewEffect，跟随她，画在人物上面 z 2；左右对称；大图表）", "40 × 26",
     "她把闪光烟雾弹摔在脚下：先一下白色的闪光，再从她脚下往两边翻滚出一圈粉紫色、灰紫色的烟，几颗金色的火星迸出来，烟慢慢散开"
     "（参考 petchibikaisa_skin3_emote_smoke_trail、olaf_skin16_explosion_smoke_mult、tar_flashglow）。**只画在她脚下和两边，身体位置留空**，"
     "**左右对称**。",
     f"{SM} and {FI}",
     "A FLASH-SMOKE BOMB at a girl's feet, 6 frames, " + LR + " (" + HER + "): 1 a white flash 10 squares across on the "
     "ground at her feet; 2 a white-pink flash 18 across and the first pink-violet smoke puffs low at both sides; 3 a "
     "low rolling smoke bank 34 squares wide and 10 tall round her feet and legs (her body above it left clear), 6 gold "
     "spark squares at mirrored places; 4 the smoke 38 wide billowing up to 14 tall at the outer sides; 5 the smoke "
     "thinning into puffs; 6 only a few pale puffs.",
     row(6, 40, 26) + "; centered across, the smoke's bottom on the cell's bottom row."),
    ("e_blind", "技能2：致盲（敌人头上，跟随），4 帧", "view_effects `tft_powder_e_blind`（跟随目标，画在人物上面 z 3；左右对称）",
     "16 × 10",
     "被闪光烟雾弹致盲的敌人：眼睛高度一圈灰紫色的烟带，几颗白色的小星星在里面转（看不见、打不了普攻）。**画在头部**，**左右对称**。",
     f"{SM} and a white-gold sparkle ramp (#FFFFFF, #FFF4B8, #FFD24A)",
     "A BLINDING SMOKE BAND at a unit's eye level, 4 frames, " + LR + ": a band of grey-violet smoke 14 squares wide and 4 "
     "tall, 3 tiny white four-pointed stars circling inside it at mirrored places, the band swelling a square on frames 2 "
     "and 3 and thinning on 4.",
     row(4, 16, 10) + CENTER),
    # ---- ult: The Hex Crystal Bomb
    ("r_cast", "大招 海克斯水晶炸弹：举起包时手上的蓝光（她身上，跟随），3 帧",
     "view_effects `tft_powder_r_cast`（CasterViewEffect，跟随她，画在人物上面 z 3；左右对称）", "14 × 14",
     "她举起装着海克斯水晶的包的一下：一团青蓝色的水晶光闪起来，四周几粒蓝色的光点（参考 tft_set6_skin05_glow_64、energymote）。**左右对称**。",
     HX,
     "A HEX CRYSTAL GLINT, 3 frames, " + LR + ": 1 a small white-cyan diamond glint 5 squares tall; 2 a cyan-blue glow 10 "
     "across with a white core and 4 rays; 3 the glow fading, 6 blue motes drifting outward.",
     row(3, 14, 14) + CENTER),
    ("r_bag", "大招：飞出去的水晶包（弹道，循环），4 帧", "view_projectiles `tft_powder_r_bag`（跟着弹道转向；翻滚）", "16 × 16",
     "她丢出去的包：一个打着补丁的棕色帆布小包，袋口扎着绳子，缝隙里透出青蓝色的海克斯水晶光，绳头一根引线冒火星（参考 powder_prop_tft13_blue02）。"
     "**在空中翻滚**（每帧转四分之一圈），4 帧循环。",
     f"{HX}, {BR}, {FI} and a brown canvas ramp (#E8C89A, #B88A5A, #7A5434, #46301E)",
     "A HOMEMADE BOMB BAG, 4 frames, a seamless loop, " + TUMBLE + ": a lumpy brown canvas sack 11 squares across with a "
     "patch and a brass-tied neck, cyan-blue crystal light glowing out of its seams (white-cyan squares in the cracks), a "
     "short lit fuse at the neck spitting 3 gold sparks; 1-square near-black outline round the sack.",
     row(4, 16, 16) + CENTER),
    ("r_warn", "大招：落点的警示圈（地上，不跟随，循环），4 帧", "view_effects `tft_powder_r_warn`（ParabolicProjectile 的落点提示，画在人物下面 z -2；左右对称；大图表）",
     "44 × 16",
     "包飞在空中时落点上的警示圈：地面上一个青蓝色的虚线椭圆，里面一圈细细的六边形纹路一闪一闪（参考 arcs、tft12_galio_base_r_glow）。"
     "**只画在地面上**，**左右对称**，4 帧循环。",
     HX,
     "A GROUND WARNING RING, 4 frames, a seamless loop, " + LR + ": a flat dashed ellipse 42 squares wide and 12 tall drawn "
     "in cyan-blue dashes 3 squares long, inside it a thinner hexagon outline in pale cyan; each frame the dashes move a "
     "step round and the hexagon pulses brighter on frames 2 and 4.",
     row(4, 44, 16) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    ("r_fuse", "大招：落地后引线燃烧的包（地上的点，不跟随，循环），4 帧", "view_effects `tft_powder_r_fuse`（不跟随，画在人物下面 z -1；左右对称；每 9 tick 重放）",
     "16 × 18",
     "包落在地上、引线还在烧：棕色的帆布包坐在地上，缝里的青蓝光一闪一闪越来越亮，袋口的引线冒着金色火星往下烧，下面一小片青蓝色的光"
     "（参考 powder_prop_tft13_blue02）。**左右对称**，4 帧循环。",
     f"{HX}, {FI} and a brown canvas ramp (#E8C89A, #B88A5A, #7A5434, #46301E)",
     "A FIZZING BOMB BAG on the ground, 4 frames, a seamless loop, " + LR + ": the brown canvas sack 11 squares across sitting "
     "upright on the ground (1-square near-black outline), its seams glowing cyan-blue - dim on frame 1, brighter each "
     "frame, white-cyan on frame 4; a lit fuse straight up from its neck spitting 2-4 gold spark squares at mirrored "
     "places; a flat cyan glow ellipse 14 wide and 2 tall under it.",
     row(4, 16, 18) + "; centered across, the glow's bottom on the cell's bottom row."),
    ("r_blast", "大招：海克斯水晶大爆炸（地上的点，不跟随，大图），6 帧", "view_effects `tft_powder_r_blast`（不跟随，画在人物上面 z 2；左右对称；大图表）",
     "52 × 42",
     "那颗真炸了的炸弹：先一道白色的大闪光，再炸开一团巨大的青蓝色海克斯光球，蓝色的水晶碎片往外飞，外面一圈粉紫色的烟浪，地上一圈冲击波，"
     "最后蓝光散成光点（参考 tft_set6_skin05_lightningerosion03、tft_kennen_skin11_i_lightning03、olaf_skin16_explosion_smoke_mult）。"
     "**左右对称**，底部贴着地面，比猴子炸弹大得多、更亮。",
     f"{HX}, {SM} and {FI}",
     "A HEX CRYSTAL EXPLOSION on the ground, 6 frames, " + LR + ": 1 a white flash 16 squares across with 8 long rays; 2 a "
     "huge cyan-blue sphere of light 34 across, white core 14 across, crackling cyan arcs at its edge; 3 the sphere 44 "
     "across, 8 cyan crystal shards (solid diamonds with near-black outlines) flying out at mirrored places, a flat "
     "shockwave ellipse on the ground 50 wide; 4 a ring of pink-violet smoke 50 across round a fading blue core, shards "
     "further out; 5 the smoke rising and thinning, blue motes drifting up; 6 only motes and thin smoke.",
     row(6, 52, 42) + "; centered across, the blast's bottom on the cell's bottom row."),
    ("r_hit", "大招：被炸飞的敌人（他身上，跟随），3 帧", "view_effects `tft_powder_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 14",
     "被海克斯爆炸击飞的敌人：身上一团青蓝色的电火花炸开。**左右对称**。",
     HX,
     "A HEX SPARK HIT, 3 frames, " + LR + ": 1 a white-cyan flash 7 squares across; 2 cyan crackling sparks 12 across in 6 "
     "short jagged arcs; 3 only a few fading sparks.",
     row(3, 14, 14) + CENTER),
]
ICONS = [
    ("icon_skill", "技能1 图标：猴子炸弹", "蓝色发条猴子炸弹的头像（肉色的脸咧嘴笑，两片黄铜钹，头顶引线冒火星），背景暗橙色"),
    ("icon_skill2", "技能2 图标：快跑，爆爆！", "一颗砸在地上冒出粉紫色烟和白色闪光的烟雾弹，旁边一道往回跑的蓝色速度线，背景暗紫色"),
    ("icon_ult", "大招 图标：海克斯水晶炸弹", "一个透出青蓝色强光的棕色帆布包，缝里亮着海克斯水晶，引线冒火星，背景深蓝色"),
]
BIG_FX = ["q_blast", "e_smoke", "r_warn", "r_blast"]
FLYING = ["a_pop", "q_monkey", "r_bag"]
GROUPS = [
    ("a_pop a_hit", ["jinx_skin60_ba_hit_impact", "tar_flashglow", "lux_skin18_ba_bullet_front", "trail02"]),
    ("q_monkey q_blast q_hit q_wound", ["monkey_model", "monkey_prop_tft13_blue", "broken_monkey_tft13_blue",
                                        "olaf_skin16_explosion_smoke_mult", "tft13_blue_base_toxic_splashes2",
                                        "tft_base_firewall"]),
    ("e_smoke e_blind", ["petchibikaisa_skin3_emote_smoke_trail", "olaf_skin16_explosion_smoke_mult",
                         "alphaslice_bubbles_02", "energymote"]),
    ("r_cast r_bag r_warn r_fuse r_blast r_hit", ["powder_prop_tft13_blue02", "tft_set6_skin05_glow_64", "arcs",
                                                  "tft12_galio_base_r_glow", "tft_set6_skin05_lightningerosion03",
                                                  "tft_kennen_skin11_i_lightning03"]),
]
SHOTS = [("attack", 3, "a_pop：手一甩，小鞭炮飞出去；a_hit 在目标身上"),
         ("skill", 3, "q_monkey：下手往上一抛，猴子炸弹飞出去；q_blast 在落点"),
         ("skill2", 1, "e_smoke：摔在她脚下；e_blind 在附近敌人头上"),
         ("ult", 2, "r_cast：举包抡臂时在她身上"), ("ult", 4, "r_bag：甩出去；r_warn / r_fuse / r_blast 在落点"),
         ("idle", 1, "待机（大小参考，游戏里显示 90%）")]


def configure():
    """pack_rammus_fx's sheets drawn from Powder's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "爆爆"


def design_sheet(path):
    """Her idle at 4x, the design's own squares (the hd_idle frame: PPU 1.5)."""
    f = RF.sheet_frames("hd_idle")[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    t = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.ascontiguousarray(np.repeat(np.repeat(t, 4, 0), 4, 1))), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 爆爆（金铲铲之战 · 双城之战）：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图和 {len(ICONS)} 个技能图标。** 造型和动作已定（`design/powder_idle.png`：3/4 正面朝右的 Q 版"
      f"小女孩，亮蓝色乱蓬蓬的短发、两个金色 X 发夹、两条小辫子，青绿上衣、粉色袖子、深棕护臂、腰后一袋蓝色小炸弹、紫色裤袜、棕靴子）。"
      f"她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽，游戏里显示成 90%；**特效照常按游戏格子画**"
      f"（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/powder_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/powder_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里爆爆自己的特效贴图和她的猴子炸弹模型，按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色：**她的鞭炮和炸弹都是自制的**（红粉色的纸、黄铜、绳子），**猴子是蓝色的发条玩具**（黄铜钹、肉色的脸），**她的爆炸是橙金色的火加粉紫、"
      "蓝色的烟**，**海克斯水晶是青蓝色的光**。")
    a("> - **特效要亮**：每团光、每团火都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、头上、脚下、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（小鞭炮、猴子、水晶包）"
      "**在空中翻滚**：每帧转四分之一圈，游戏按飞行方向转这张图时怎么转都对。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `powder_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/powder_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「伏击者」：技能炸弹可以暴击） | 扔一个自制小鞭炮 | `a_pop` · `a_hit` |")
    a("| 技能 1「猴子炸弹」 | 把发条猴子炸弹丢到目标脚下，中心全额、外圈减半，被炸到的灼烧 + 重伤 | `q_monkey` · `q_blast` · `q_hit` · "
      "`q_wound` |")
    a("| 技能 2「快跑，爆爆！」 | 敌方英雄靠近时摔下闪光烟雾弹，周围敌人致盲，自己向后跳开 | `e_smoke` · `e_blind` |")
    a("| 大招「海克斯水晶炸弹」 | 把装着海克斯水晶的包丢向敌方英雄，引线烧完蓝光大爆炸，击飞 | `r_cast` · `r_bag` · `r_warn` · `r_fuse` · "
      "`r_blast` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火星、烟、光圈、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**；"
      "**实物**（鞭炮、猴子、包、飞出去的零件和水晶碎片）有 1 格近黑描边。")
    a("- **要亮**：每个光或火的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("橙金色的火", FIRE), ("粉紫色的烟", SMOKE), ("红粉色的鞭炮纸", PAPER), ("黄铜", BRASS), ("蓝色的玩具猴", TOY),
                        ("青蓝色的海克斯水晶光", HEX), ("绿色的毒液 / 漩涡眼", GREEN)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（警示圈、光、冲击波）是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，猴子炸弹的爆炸半径 32000，"
      "水晶炸弹 42000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `powder_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a(f"## 技能图标（{len(ICONS)} 个）\n")
    a("每个图标一张 **64 × 64** 的像素画（**32 × 32 格、每格 2 px**），方形、画满整张、不透明背景，和游戏里技能图标一样：一个清楚的主体占"
      "中间大半，暗色的背景，1 格近黑描边，2–3 档平涂，不要文字。交付 `pixel_1x/powder_icon_<名字>.png`（64 × 64）。\n")
    for k, (name, title, zh) in enumerate(ICONS, 1):
        a(f"### {k}. `powder_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a("Pixel art skill icon for a small tactics game, 64x64 px (a 32x32 grid of 2-px squares), square, filled edge to "
          "edge with an opaque dark background, one clear bold subject filling most of it, a 1-square near-black outline "
          "on the subject, 2-3 flat shades a material, a white or brightest highlight, no text, no border, no "
          f"anti-aliasing. Subject: {zh_to_en(name)}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `powder_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_powder_fx`（小的）和 `tft_powder_big`（{'、'.join(BIG_FX)}），tag = 名字（build_powder.py 的 views）。")
    a(f"- 弹道图（{'、'.join(FLYING)}）翻滚不查对称，其余断言左右对称；`r_fuse` 不跟随（每 9 tick 重放），`q_blast` / `r_blast` 不跟随。")
    a("- 图标：`tft/icons/tft_powder_skill.png` / `_skill2` / `_ult`（64 × 64）。")
    a("- 用 `pixel_1x/` 切格（import_rammus_fx 的做法）；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回"
      "（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def zh_to_en(name):
    return {"icon_skill": "the head of a blue wind-up toy monkey bomb - a peach face with a wide toothy grin, a brass cymbal "
                          "on each side, a lit fuse on top spitting gold sparks - on a dark orange background",
            "icon_skill2": "a smoke bomb smashing on the ground in a burst of pink-violet smoke and a white flash, a blue "
                           "speed streak running away from it to the left - on a dark violet background",
            "icon_ult": "a lumpy brown canvas bomb bag blazing with cyan-blue hex crystal light out of its seams, a lit fuse "
                        "spitting gold sparks - on a deep blue background"}[name]


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="powder_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(TMP, "packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no TFT references in {REF}")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "powder_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "powder_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "powder_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"powder_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "tumbling" if x[0] in FLYING else "left-right"} for x in FX]
                  + [{"file": f"powder_{n}.png", "binding": "skill icon 64x64"} for n, _, _ in ICONS], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects +", len(ICONS), "icons;", DOC, shape)
    if not a.no_zip:
        os.makedirs(RF.lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(RF.lp(zpath)):
            os.remove(RF.lp(zpath))
        with zipfile.ZipFile(RF.lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(RF.lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
