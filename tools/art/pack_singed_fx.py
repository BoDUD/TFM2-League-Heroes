#!/usr/bin/env python3
"""Build singed_fx_pack.zip: step 3 of Singed's sprite - Codex draws his effects (pack_zac_fx.py's way).

    python tools/lol/fx_ref_singed.py              # League's particle textures -> C:/t/si_work/fxref (Riot's art, local only)
    python tools/art/pack_singed_fx.py [--no-zip] [--out DIR] [--only a_hit,e_hit --name singed_fx_redo_pack]

The pack (C:/t/si_work/fx/singed_fx_pack, zipped into --out, default dist/singed_packs) holds PROMPTS.md (also written to
assets/source/singed/PROMPTS_FX.md), design/singed_design.png (the idle at 4x, its own squares), design/singed_size.png (at
game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Singed, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_singed.py, the user's picks 2026-10-23: top, layout A - E / W / R,
Q's trail and the slipstream in the passive): view_projectiles w_vial; view_effects a_hit, e_hit, e_land, e_root,
w_glue (big), q_cloud (big), q_cloud_r (big), r_drink, p_fast; view_buffs slow (w_slow), gw (q_gw), r_aura (r_on), haste
(p_fast). League's colours: Singed's chemistry - TOXIC GREEN poison smoke (lime highlights, murky green body, dark green
depths), the Mega Adhesive's PALE AMBER-YELLOW glue (sticky strands, yellow crystal chunks), the potion's green-yellow
froth. Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left
to right; a projectile is turned with its flight, so it is drawn flying right and symmetric top to bottom.
Lasting pictures (the clouds, the glue) are a few frames the import stretches to the zone's life (an opening, a loop, a
fade: league_aurora's r_zone).
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

TMP = "C:/t/si_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "singed", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "singed", "hd")
NAME = "singed_fx_pack"
PPU = 1.39

POISON = "#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814"   # the toxic poison: lime highlights to deep green
SMOKE = "#C4DC98, #92B468, #64844A, #3E5A32, #24361E"            # the murky green smoke body
GLUE = "#FFF8D2, #F4DC8C, #DAB858, #AC863C, #725628"             # the Mega Adhesive: pale amber-yellow
FLASH = "#FFFFFF, #F6FFE2, #E0F6AA"                              # white-green flashes and glints
VIOLET = "#ECCEFF, #BC84EC, #8048BE, #4A2672"                    # the grievous wounds' sickly violet
DUST = "#E6E0C8, #BDB394, #8C8466, #5E5844"                      # the ground's dust where a body lands
PO = f"a toxic green poison ramp ({POISON})"
SM = f"a murky green smoke ramp ({SMOKE})"
GL = f"a pale amber glue ramp ({GLUE})"
FL = f"a white-green flash ramp ({FLASH})"
VI = f"a sickly violet ramp ({VIOLET})"
DU = f"a pale dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
CHEM = ("everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green "
        "depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams")
STICKY = ("the glue is THICK STICKY ADHESIVE: pale amber-yellow, glossy, with stretched strands, drips, a few small yellow "
          "crystal chunks and round bubbles; flat shades, crisp shapes")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = "Singed stands in the middle, not drawn: 32 squares wide and 45 tall (to the tank's cap)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：盾板砸中，3 帧", "view_effects `league_singed_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "盾板砸中敌人：中间一个白绿色的闪光，四周飞出几块碎屑和两三颗绿色的毒液滴。**左右对称**，3 帧。",
     FL + ", " + PO,
     "A HEAVY BASH LANDING, 3 frames, " + LR + ": 1 a white-green impact flash 6 squares across, a short cross of light; "
     "2 a burst ring 13 across with grey-green metal chips and green droplets flying out at mirrored places; 3 the chips "
     "and droplets further out and smaller, dimming to their darker shades. " + CHEM + ".",
     row(3, 14, 14) + CENTER),
    # ---- passive: Poison Trail's clouds
    ("q_cloud", "剧毒踪迹：他身后的一团毒雾，6 帧（约 3 秒）",
     "view_effects `league_singed_q_cloud`（大表，在他走过的地上，不跟随，z -1；左右对称；冒出 → 飘着 → 散掉，3 秒）", "26 × 18",
     "剧毒踪迹（参考 q_smoke、smoke_clouds、q_breathtrail）：辛吉德走过的地方留下**一团贴着地面的绿色毒雾**——几团圆圆的烟团挤在一起，"
     "上面亮黄绿、下面暗绿，里面冒一两个小泡。第 1 帧冒出来（小、亮），2–4 帧胀大慢慢翻滚（这三帧会循环），5–6 帧变淡、散成几小团。"
     "**左右对称**，6 帧。毒雾贴着地，顶部不超过 18 格。",
     PO + ", " + SM,
     "A POISON CLOUD ON THE GROUND, 6 frames, " + LR + ": 1 a small bright puff of toxic green smoke 10 squares wide sitting "
     "on the ground; 2 it swelling into a low cloud of five round smoke puffs 24 wide and 14 tall, lime-yellow on top, "
     "murky green below, a dark green base " + FEET + "; 3 and 4 the puffs rolling slowly - the same size, the puffs and two "
     "small bubbles shifting at mirrored places (frames 2-4 loop); 5 the cloud thinner and paler, breaking into three "
     "puffs; 6 two faint wisps. " + CHEM + ".",
     row(6, 26, 18) + CENTER),
    ("q_cloud_r", "疯狂药剂期间的毒雾：更大更浓、带紫色，6 帧（约 3 秒）",
     "view_effects `league_singed_q_cloud_r`（大表，在地上，不跟随，z -1；左右对称；3 秒）", "32 × 22",
     "开了大招以后的毒雾（重伤）：和上一张一样的毒雾，但**更大、更浓**，烟团之间夹着**紫色的毒丝和气泡**（附带重伤），冒的泡更多。"
     "**左右对称**，6 帧（2–4 帧循环）。",
     PO + ", " + SM + ", " + VI,
     "A THICKER POISON CLOUD, 6 frames, " + LR + ": the same as the poison cloud but bigger and denser - 1 a bright puff 12 "
     "wide; 2 a low cloud of six round toxic green puffs 30 wide and 18 tall with sickly violet streaks and violet "
     "bubbles between them " + FEET + "; 3 and 4 rolling, the bubbles rising and popping at mirrored places (frames 2-4 "
     "loop); 5 thinner and paler, breaking up; 6 faint wisps. " + CHEM + ".",
     row(6, 32, 22) + CENTER),
    # ---- E Fling
    ("e_hit", "过肩摔：抓住，3 帧", "view_effects `league_singed_e_hit`（跟随目标，z 2；左右对称）", "16 × 18",
     "过肩摔抓住敌人：敌人身上一下白绿色闪光，一圈短短的冲击线往外，几滴绿色毒液溅开。**左右对称**，3 帧。",
     FL + ", " + PO,
     "A GRAB AND HEAVE, 3 frames, " + LR + ": 1 a white-green flash 6 squares across on the target's chest; 2 a ring of short "
     "impact streaks 15 across with green droplets thrown out at mirrored places; 3 the droplets falling, fading. " +
     TARGET + ".",
     row(3, 16, 18) + CENTER),
    ("e_land", "过肩摔：摔在地上，4 帧", "view_effects `league_singed_e_land`（在落地的人脚下，不跟随，z -1；左右对称）", "30 × 12",
     "被扔到辛吉德身后的敌人落地：脚下砸起**一圈尘土**，地上一圈浅浅的冲击波往外推。**左右对称**，4 帧。",
     DU + ", " + FL,
     "A BODY HITTING THE GROUND, 4 frames, " + LR + ": 1 a white impact flash 10 squares wide " + FEET + "; 2 pale dust "
     "bursting up at both sides and a shock ring 22 wide on the ground; 3 the ring 28 wide, the dust puffs rising and "
     "spreading at mirrored places; 4 settling dust, fading. Flat shades, crisp shapes.",
     row(4, 30, 12) + CENTER),
    ("e_root", "过肩摔：摔进胶里被粘住，4 帧", "view_effects `league_singed_e_root`（跟随目标，脚下，z 2；左右对称；约 1 秒）",
     "20 × 14",
     "落进强力粘胶被禁锢（参考 w_root_slime、goo_strands）：敌人脚下的黏胶**一下子往上包住他的脚**——几根黄色的黏胶丝往上拉起来缠住小腿，"
     "胶面冒泡。**左右对称**，4 帧（第 4 帧停住，会持续约 1 秒）。",
     GL + ", " + FL,
     "STUCK IN THE GLUE, 4 frames, " + LR + ": 1 a splash of pale amber glue round the target's feet 16 wide " + FEET + "; "
     "2 thick glue strands rising from it at mirrored places up to the target's knees, 10 squares tall; 3 the strands "
     "wrapping in, glossy highlights, two bubbles on the glue; 4 the same, holding (the frame that stays). " + STICKY +
     ". " + TARGET + ".",
     row(4, 20, 14) + CENTER),
    # ---- W Mega Adhesive
    ("w_vial", "强力粘胶：飞出去的药瓶，4 帧循环", "view_projectiles `league_singed_w_vial`（抛物线弹道，z 2；上下对称）", "10 × 8",
     "扔出去的强力粘胶药瓶（参考 w_bottle、w_mis_blur）：一个**圆圆的玻璃瓶**，里面是黄色的黏胶，瓶口深灰，转着往前飞，后面拖一两滴黏胶。"
     "**朝右飞、上下对称**，4 帧循环（瓶子转一圈：瓶口朝右、朝上下……要上下对称就画成瓶口朝右、朝左、侧着的轮流）。",
     GL + ", " + FL,
     "A SPINNING GLASS VIAL, 4 looping frames, " + TB + ": a round glass bottle 6 squares across full of pale amber glue with "
     "a white glint, its dark grey neck pointing right in frame 1, toward the viewer (a round cap in the middle) in frame "
     "2, left in frame 3, toward the viewer again in frame 4; two small glue drops trailing on the left. " + STICKY + ".",
     row(4, 10, 8) + CENTER),
    ("w_glue", "强力粘胶：地上一大摊胶，8 帧（约 3 秒）",
     "view_effects `league_singed_w_glue`（大表，在落点的地上，不跟随，z -1；左右对称；溅开 → 躺着冒泡 → 干掉，3 秒）", "44 × 18",
     "强力粘胶落地（参考 w_singed_experiment_glue、megaadhesive、w_aoe_petals、splat_dissolve）：药瓶砸碎，**地上溅开一大摊黄色的黏胶**"
     "（椭圆，边缘一个个圆鼓鼓的瓣，像溅开的蜂蜜），胶面有光泽，冒几个泡，边上散着几小块黄色的结晶碎片。第 1–2 帧溅开（玻璃碎片和白光），"
     "3–6 帧躺在地上冒泡（循环），7–8 帧变暗变小干掉。**左右对称**，8 帧。",
     GL + ", " + FL,
     "A POOL OF GLUE ON THE GROUND, 8 frames, " + LR + ": 1 a white flash and glass shards where the vial bursts, a glue "
     "splash 20 wide " + FEET + "; 2 the glue spreading into a wide pool 40 wide and 14 tall with round petal-like lobes on "
     "its rim, a few small yellow crystal chunks at mirrored places; 3, 4, 5 and 6 the pool lying still and glossy, two or "
     "three bubbles swelling and popping at mirrored places, a highlight sliding across (frames 3-6 loop); 7 the pool "
     "darker and a little smaller; 8 a dull thin film, fading. " + STICKY + ".",
     row(8, 44, 18) + CENTER),
    ("slow", "强力粘胶：脚下粘着的胶，4 帧循环", "view_buffs `league_singed_w_slow`（tag `slow`，跟随，脚下，z -1；左右对称）",
     "18 × 7",
     "被粘胶减速、缚地的敌人脚下：一小滩**黄色的黏胶**粘着脚，拉出两根短短的黏丝，冒一个小泡。**左右对称**，4 帧循环。",
     GL,
     "A STICKY GLUE PATCH, 4 looping frames, " + LR + ": a flat glossy pale amber glue patch " + FEET + " 16 wide and 5 tall "
     "with a darker rim, two short sticky strands at mirrored places that stretch and shorten, a small bubble swelling "
     "and popping in turn. " + STICKY + ".",
     row(4, 18, 7) + CENTER),
    # ---- R Insanity Potion
    ("r_drink", "疯狂药剂：一口喝下，5 帧", "view_effects `league_singed_r_drink`（跟随他，z 2；左右对称）", "40 × 50",
     "疯狂药剂（参考 color-potionfroth、color-insanity-strand、ult_spatter）：辛吉德一口喝下，**全身爆出一圈黄绿色的药剂泡沫和蒸汽**——"
     "先是身上一下亮光，然后黄绿色的泡泡、水滴和几缕蒸汽从他身边往四周和往上冒。辛吉德在中间不画，**身体的位置留空**。**左右对称**，5 帧。",
     PO + ", " + FL,
     "A POTION RUSH, 5 frames, " + LR + "; " + HIM + " - leave his body's place EMPTY: 1 a green-white glow hugging his "
     "outline; 2 a ring of green-yellow froth bursting out round him, round bubbles 1 to 3 squares at mirrored places; "
     "3 the bubbles and droplets flying out and up, three curls of green steam rising from his shoulders; 4 the steam "
     "higher, the bubbles popping at the cell's edge; 5 a few bubbles and wisps fading. " + CHEM + ".",
     row(5, 40, 50) + CENTER),
    ("r_aura", "疯狂药剂：喝完后身上一直冒的蒸汽，4 帧循环",
     "view_buffs `league_singed_r_on`（tag `r_aura`，跟随他，z -1，在他身后；左右对称；约 25 秒）", "36 × 50",
     "疯狂药剂生效期间：辛吉德身边一直**冒着几缕绿色的蒸汽和小泡泡**往上飘（从肩膀、背后的药罐往上），脚下一圈淡淡的绿色光。"
     "辛吉德在中间不画，**身体的位置留空**；画在他身后，要淡一点。**左右对称**，4 帧循环。",
     PO + ", " + SM,
     "A LINGERING POTION STEAM, 4 looping frames, " + LR + "; " + HIM + " - leave his body's place EMPTY: three thin curls of "
     "pale green steam rising from the shoulders and the top of the body at mirrored places, small bubbles drifting up "
     "between them, a faint green glow ring " + FEET + " 30 wide; the curls and bubbles rising frame to frame so the "
     "loop flows upward. Sparse and light - it plays behind him for 25 seconds. " + CHEM + ".",
     row(4, 36, 50) + CENTER),
    ("gw", "重伤：头上的紫绿色标记，4 帧循环", "view_buffs `league_singed_q_gw`（tag `gw`，跟随，头上，z 3；左右对称）", "10 × 10",
     "被大招毒雾附上重伤的敌人头上：一个**裂开的紫色小十字**（治疗被削弱的标记），上面挂着一滴绿色毒液，一闪一闪。**左右对称**，4 帧循环。",
     VI + ", " + PO,
     "A GRIEVOUS WOUND MARK, 4 looping frames, " + LR + ": a small violet plus sign 7 squares across cracked down its middle "
     "with a dark violet crack, a green poison drop hanging under it; it pulses - brighter, then dimmer - and the drop "
     "swells and falls in turn. " + CHEM + ".",
     row(4, 10, 10) + CENTER),
    # ---- passive: Noxious Slipstream
    ("p_fast", "剧毒冲流：加速的一下，3 帧", "view_effects `league_singed_p_fast`（跟随他，脚下，z -1；左右对称）", "34 × 12",
     "剧毒冲流（参考 p_wispy、q_breathtrail）：从敌方英雄身边冲过去时一下加速——**脚下一圈绿色的气流往两边冲开**，几缕毒雾被甩开。**左右对称**，3 帧。",
     PO + ", " + SM,
     "A BURST OF SPEED, 3 frames, " + LR + ": 1 a flat green swirl " + FEET + " 16 wide; 2 two sweeping gusts of toxic green "
     "wisps rushing out to both sides 30 wide, small puffs at their tips; 3 the gusts thin and fading. " + CHEM + ".",
     row(3, 34, 12) + CENTER),
    ("haste", "剧毒冲流：加速期间脚下的气流，4 帧循环", "view_buffs `league_singed_p_fast`（tag `haste`，跟随，脚下，z -1；左右对称）",
     "24 × 8",
     "加速期间：辛吉德脚下**两缕绿色的气流**一闪一闪往两边飘（左右对称，不分前后）。**左右对称**，4 帧循环。",
     PO + ", " + SM,
     "A SPEED WISP, 4 looping frames, " + LR + ": two thin toxic green wisps curling out from under the feet to both sides "
     + FEET + " 22 wide, small puffs drifting off their ends; the wisps flicker and shift frame to frame. " + CHEM + ".",
     row(4, 24, 8) + CENTER),
]
BIG_FX = ["q_cloud", "q_cloud_r", "w_glue"]
FLYING = ["w_vial"]
FORWARD = []

GROUPS = [
    ("a_hit e_hit e_land (the bash, the fling)", ["singed_ult_spatter", "dirtbits", "common_hiteffect", "singed_goodrops"]),
    ("q_cloud q_cloud_r (Poison Trail)", ["singed_base_q_smoke_01", "smoke_clouds_2x2", "singed_base_q_breathtrail",
                                          "color-goop"]),
    ("w_vial w_glue slow e_root (Mega Adhesive)", ["singed_base_w_bottle", "singed_base_w_singed_experiment_glue",
                                                   "singed_base_w_root_slime", "singed_base_w_aoe_petals"]),
    ("w_glue colours", ["singed_megaadhesive_color32", "singed_base_w_splat_dissolve", "singed_goo_strands",
                        "singed_base_w_acid_purple"]),
    ("r_drink r_aura gw (Insanity Potion)", ["color-potionfroth", "color-insanity-strand", "singed_base_idle_chembubble",
                                             "singed_base_idle_steam_01"]),
    ("p_fast haste (Noxious Slipstream)", ["singed_p_wispy", "singed_base_q_breathtrail", "singed_p_ring", "smokepuffs"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", ppu=PPU):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / ppu, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Singed at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"辛吉德 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 炼金术士 辛吉德：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/singed_design.png`：又高又瘦的驼背光头老头，灰绿蒙脸布，红夹克金扣带，"
      "带刺的护肩，背上发光的亮绿药罐，近侧手臂上一块带刺的灰绿盾板，远侧手里一个绿药瓶，深蓝细腿，大红棕靴子）。"
      f"他在游戏里是**高清**的（每个游戏格子里约 1.4×1.4 个细像素），{h} 格高、{w} 格宽（高×宽，连药罐）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/singed_size.png`：辛吉德放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里辛吉德自己的特效贴图（大多是灰度或绿色的形状），按用在我们哪张特效分好了行，只在本地用。"
      "**辛吉德是疯狂炼金术士**：毒雾是**一团团圆圆的毒绿色烟**（上面亮黄绿、下面暗绿），强力粘胶是**浅琥珀黄的黏胶**（有光泽、拉丝、冒泡、"
      "几块黄色的结晶碎片），疯狂药剂是**黄绿色的药剂泡沫和蒸汽**，重伤是**紫色**；不要火、不要电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。")
    a("> - **毒雾、黏胶、蒸汽、冲击波、尘土都没有黑描边**（用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - **持续的画面**（毒雾 3 秒、地上的胶 3 秒、粘住 1 秒）只画几帧：开头、中间循环的几帧、结尾，Claude 导入时按时长拉开循环。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `singed_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/singed_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 用盾板砸 | `a_hit` |")
    a("| 被动「剧毒踪迹」+「剧毒冲流」 | 走过的地方一直留下毒雾，踩在里面的敌人持续掉血；从敌方英雄身边冲过时加速 | `q_cloud` · `p_fast` · `haste` |")
    a("| 技能 1 =「过肩摔」 | 抓住敌人从肩膀上扔到身后；落进强力粘胶里就被粘住（禁锢） | `e_hit` · `e_land` · `e_root` |")
    a("| 技能 2 =「强力粘胶」 | 扔出一瓶粘胶，地上一大摊胶，里面的敌人减速、不能位移 | `w_vial` · `w_glue` · `slow` |")
    a("| 大招 =「疯狂药剂」 | 喝下药剂，25 秒内各项属性大涨，毒雾更大更浓、附带重伤 | `r_drink` · `r_aura` · `q_cloud_r` · `gw` |\n")
    a("连招：**粘胶 → 过肩摔**（把人扔进胶里粘住），**过肩摔 → 加速**（扔完马上冲过去），**喝药 → 马上扔粘胶**，**药效期间毒雾变强**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**毒雾、黏胶、蒸汽、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的亮点。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("毒雾·毒绿", POISON), ("烟·暗绿", SMOKE), ("粘胶·琥珀黄", GLUE), ("闪光·白绿", FLASH), ("重伤·紫", VIOLET),
                        ("尘土·浅灰黄", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的东西（毒雾的底、胶、冲击波、脚下的胶）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `singed_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `singed_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_singed_fx`（小的）和 `league_singed_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_singed.py 的 views；w_slow 用 `slow`，q_gw 用 `gw`，r_on 用 `r_aura`，p_fast 的 buff 用 `haste`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称。q_cloud / q_cloud_r 拉到 q_t（180 tick）：1 开 + 2–4 循环 + 5–6 散；"
      "w_glue 拉到 w_t（180 tick）：1–2 开 + 3–6 循环 + 7–8 散；e_root 第 4 帧停到 e_root（60 tick）；r_aura 循环 r_t。")
    a("- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="singed_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "singed_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_singed.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "singed_design.png"))
    shape = size_sheet(os.path.join(out, "design", "singed_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"singed_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
