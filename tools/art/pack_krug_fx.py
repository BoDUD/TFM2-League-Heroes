#!/usr/bin/env python3
"""Build krug_fx_pack.zip: step 3 of the Ancient Krug's sprite - Codex draws his effects and his three skill icons
(pack_kobuko_fx.py's way).

    python tools/lol/fx_ref_krug.py            # the particle references -> C:/t/kr_work/fxref
    python tools/art/pack_krug_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name krug_fx_redo_pack]

The pack (C:/t/kr_work/fx/krug_fx_pack, zipped into --out, default dist/krug_packs) holds PROMPTS.md (also written to
assets/source/krug/PROMPTS_FX.md), design/krug_design.png (the approved idle at 4x on its own squares),
design/krug_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (the particle textures of the Rift's Krug, Rammus and Malphite - set 18 ships none of
his own - grey shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds
(tools/kit/build_krug.py, the user's picks 2026-10-28: jungle, plan A 「岩之摇滚」): view_effects a_hit, q_shield, q_hit,
e_cast, r_jump, r_mark, r_slam, r_hit, r_rocks, r_rock_hit and tft.dll's p_burst, p_up; view_buffs e_shell, e_taunt,
p_mini. Plus the three skill icons. He throws nothing: no projectile pictures.
His colours: the glowing LAVA orange-gold of the cracks in his boulder, the pale SANDSTONE of the boulder itself, the
dark violet-brown STONE of his body, dust where he lands and rolls.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture; nothing here points).
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

TMP = "C:/t/kr_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "krug", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "krug", "hd")
NAME = "krug_fx_pack"
PPU = 2.0

LAVA = "#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408"              # the glowing cracks of his boulder
SAND = "#F2E6BE, #D2C08C, #A8946A, #74644A"                       # the sandstone boulder, its chips
STONE = "#9A8A84, #6E5E5A, #4A3C3C, #2C2228"                      # his dark body stone, heavy rocks
DUST = "#F0E2C8, #C8AE88, #9A7E5C, #64503A"                       # dust
LV = f"a glowing lava orange-gold ramp ({LAVA})"
SD = f"a pale sandstone ramp ({SAND})"
ST = f"a dark violet-brown stone ramp ({STONE})"
DS = f"a dust brown ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold "
         "cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, "
         "crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles")
HIM = "the hunched boulder beast stands in the middle, not drawn: 43 squares wide and 38 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark STONE frame cracked with "
        "glowing orange-gold seams at the corners, a deep warm brown inside, the symbol big and centred, lit from the "
        "upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：岩拳砸中，4 帧", "view_effects `tft_krug_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "石拳砸中：一下白黄色的闪光，几块尖尖的碎石往两边崩开，一圈尘土。**左右对称**，4 帧。",
     LV + ", " + SD + ", " + DS,
     "A HEAVY STONE FIST IMPACT, 4 frames, " + LR + ": 1 a white-yellow star flash 8 squares across; 2 a short burst "
     "of angular sandstone chips (2-3 squares each) flying out to both sides (mirrored), a dust puff 12 squares wide "
     "and 5 tall at the bottom; 3 the chips farther and falling, the dust wider; 4 the last dust fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_shield", "岩之摇滚：身上包上一层石头（护盾），5 帧", "view_effects `tft_krug_q_shield`（跟随他，z 3；左右对称）", "48 × 44",
     "放技能 1 时：一圈棱角分明的**石块**从地上飞起、贴到他身上，石块之间亮着橙金色的光缝，最后只剩一圈石块描出的外轮廓。"
     "身体位置留空（只画外圈）。**左右对称**，5 帧。",
     SD + ", " + ST + ", " + LV,
     "A STONE ARMOUR SNAPPING ON, 5 frames, " + LR + ", " + HIM + ": 1 a ring of angular rocks (3-5 squares each) "
     "rising from the ground at both sides; 2 the rocks flying in around his outline, glowing orange-gold seams between "
     "them; 3 the rocks set into a jagged shell outline 46 squares wide and 42 tall around him (2-3 squares thick), the "
     "seams bright; 4 a white-yellow glint running along the seams; 5 settling to a thin outline of rocks with faint "
     "glowing seams. Only the outer edge: the middle (the body) left empty. " + MAGIC + ".",
     row(5, 48, 44) + CENTER),
    ("q_hit", "岩之摇滚：滚过来撞上，5 帧", "view_effects `tft_krug_q_hit`（跟随被撞的人，z 2；左右对称）", "28 × 24",
     "大石球撞上目标：一下大的白黄闪光，一圈尘土和碎石往两边炸开，中间亮出一道橙金色的裂纹星。比普攻狠得多。**左右对称**，5 帧。",
     LV + ", " + SD + ", " + DS,
     "A ROLLING BOULDER SMASHING INTO A UNIT, 5 frames, " + LR + ": 1 a big white-yellow flash 14 squares across; 2 a "
     "glowing orange-gold CRACK STAR (jagged lines) 14 squares across in the middle, sandstone chips and dust bursting "
     "out to both sides (mirrored); 3 a wide dust cloud 26 squares wide and 10 tall at the bottom, the chips farther; 4 "
     "the crack star fading, the chips falling; 5 the last dust. " + MAGIC + ".",
     row(5, 28, 24) + CENTER),
    ("e_cast", "坚岩外壳：缩进巨石（震地），5 帧", "view_effects `tft_krug_e_cast`（跟随他，z 3；左右对称）", "50 × 20",
     "缩进巨石的一下：脚下「咚」地一圈尘土往外推开，地上裂开几道橙金色的光缝，几块小石子跳起来。画在**地上**（扁椭圆），中心在格子底部中间。**左右对称**，5 帧。",
     DS + ", " + LV + ", " + SD,
     "A SHELL STOMP, 5 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell: 1 a "
     "dust ring 20 squares wide and 6 tall; 2 the ring 36 wide and 10 tall, four short glowing orange-gold CRACKS "
     "running out on the ground (mirrored), little pebbles hopping up; 3 the ring 48 wide, thinner, the cracks bright; 4 "
     "the cracks dimming, the pebbles down; 5 the last thin dust. " + MAGIC + ".",
     row(5, 50, 20) + CENTER),
    ("e_shell", "坚岩外壳：石壳护着（双抗），6 帧循环", "view_buffs `tft_krug_e_shell`（跟随他，z 3；左右对称）", "48 × 44",
     "缩在石壳里的时候：身体外面一圈若隐若现的**石块外壳**（和 q_shield 最后一帧差不多，但更淡），光缝一明一暗，脚边偶尔掉一点碎屑。"
     "身体位置留空。不要太显眼。**左右对称**，6 帧循环。",
     SD + ", " + LV,
     "A STONE SHELL HELD, 6 looping frames, " + LR + ", " + HIM + ": a faint jagged outline of rocks 46 squares wide "
     "and 42 tall around him (1-2 squares thick, half of it shown at a time), the glowing seams between the rocks "
     "pulsing brighter and dimmer in turn; a few tiny sandstone flakes dropping at his feet (mirrored). The middle (the "
     "body) left empty. Subtle. " + MAGIC + ".",
     row(6, 48, 44) + CENTER),
    ("e_taunt", "嘲讽：被嘲讽的人头上冒火，6 帧循环", "view_buffs `tft_krug_e_taunt`（跟随被嘲讽的人，z 4；左右对称）", "18 × 44",
     "被石甲虫嘲讽（坚岩外壳、碎岩重生都会）：头顶上一个**橙金色的怒气符号**（两道交叉的裂纹，像石头裂开）一跳一跳。"
     "身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。",
     LV + ", " + ST,
     "A TAUNTED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 10 squares of the cell) an "
     "ANGER MARK made of two crossed glowing orange-gold CRACKS (each 7 squares long, outlined dark stone), with two "
     "tiny rock chips beside it (mirrored); frames 1-6 it throbbing bigger and smaller, the chips bobbing. The rest of "
     "the cell empty. " + MAGIC + ".",
     row(6, 18, 44) + CENTER),
    ("r_jump", "远古崩落：起跳的尘土，5 帧", "view_effects `tft_krug_r_jump`（留在起跳的地上，z 1；左右对称）", "40 × 30",
     "他一跃而起的地方：地上一圈尘土喷起来，两边几块碎石飞起，地上留下一圈浅浅的裂纹。中心在格子底部中间。**左右对称**，5 帧。",
     DS + ", " + SD + ", " + LV,
     "A HEAVY JUMP-OFF, 5 frames, " + LR + ": 1 a dust ring " + GROUND_E + " 20 squares wide and 6 tall at the bottom "
     "middle, two dust jets shooting up from it 20 squares high (mirrored); 2 the ring 34 wide, sandstone chips flying "
     "up at both sides; 3 the jets spreading and thinning, the chips at the top; 4 the chips falling, a faint glowing "
     "crack ring on the ground; 5 the last dust. " + MAGIC + ".",
     row(5, 40, 30) + CENTER),
    ("r_mark", "远古崩落：落点预警，6 帧", "view_effects `tft_krug_r_mark`（跟随被砸的目标，z -1；左右对称）", "36 × 14",
     "大招起跳后、砸下来之前：目标脚下的地面一圈**裂开的橙金色光圈**一点点亮起来，裂纹往中间爬。画在**地上**（扁椭圆）。**左右对称**，6 帧。",
     LV + ", " + ST,
     "A LANDING WARNING, 6 frames, " + LR + ": everything " + GROUND_E + ", centred in the cell: 1 a thin dark crack "
     "ring 34 squares wide and 12 tall; 2 orange-gold light starting to glow in its cracks; 3 six short cracks running "
     "in toward the middle (mirrored); 4 the cracks reaching the middle, brighter; 5 the whole ring glowing, a white-"
     "yellow edge; 6 at its brightest. " + MAGIC + ".",
     row(6, 36, 14) + CENTER),
    ("r_slam", "远古崩落：砸地的冲击波，8 帧", "view_effects `tft_krug_r_slam`（大表，留在他砸落的地上，z -1；左右对称）", "96 × 34",
     "他从天上砸进敌群：地面**「轰」地裂开**，一圈巨大的尘土冲击环往外推开，地上裂出一圈发光的橙金色裂缝，大块碎石往两边飞起再落下。"
     "画在**地上**（扁椭圆），中心在格子底部中间。这是全套最大的特效。**左右对称**，8 帧。",
     LV + ", " + SD + ", " + ST + ", " + DS,
     "A MASSIVE GROUND SLAM, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the "
     "cell: 1 a white-yellow flash 30 squares wide; 2 a dust shock ring 50 squares wide and 16 tall, the ground under it "
     "SPLIT by glowing orange-gold cracks running out (mirrored); 3 the ring 74 wide and 24 tall, big angular rocks (4-6 "
     "squares) and sandstone chips flung up at both sides; 4 the ring 90 wide, the cracks at their brightest, the rocks "
     "high; 5 the ring thinner, the rocks falling; 6 the rocks landing, small dust puffs; 7 the cracks dimming to "
     "dark, dust settling; 8 the last faint glow in the cracks. " + MAGIC + ".",
     row(8, 96, 34) + CENTER),
    ("r_hit", "远古崩落：被砸飞，4 帧", "view_effects `tft_krug_r_hit`（跟随被击飞的人，z 2；左右对称）", "20 × 24",
     "被砸飞的人：脚下一下橙金色的闪光，尘土和碎石往上喷。**左右对称**，4 帧。",
     LV + ", " + DS + ", " + SD,
     "A UNIT THROWN UP, 4 frames, " + LR + ": 1 a white-yellow flash at the bottom middle 10 squares wide; 2 a jet of "
     "dust shooting upward 18 squares high, small sandstone chips to both sides (mirrored); 3 the dust spreading and "
     "thinning; 4 the last wisps. " + MAGIC + ".",
     row(4, 20, 24) + CENTER),
    ("r_rocks", "远古崩落：落石，8 帧", "view_effects `tft_krug_r_rocks`（大表，留在他身边的地上，z 3；左右对称）", "80 × 60",
     "砸地后半秒，被震下来的大石头从天上掉下来：五六块棱角分明的大石头（带橙金色的裂缝）从格子上方落下来，砸在他周围的地上碎开、扬起尘土。"
     "石头落在格子底部的地上（中间留出他的位置）。**左右对称**，8 帧。",
     SD + ", " + ST + ", " + LV + ", " + DS,
     "FALLING ROCKS, 8 frames, " + LR + ": six big angular ROCKS (5-8 squares each, sandstone with a glowing orange-gold "
     "crack, a dark stone outline) falling from the top of the cell at mirrored places around the middle (the middle 30 "
     "squares at the bottom left free for him): 1 the rocks at the top; 2-3 falling (a short dust trail above each); 4 "
     "the first two hitting the ground at the bottom, bursting into chips and dust; 5-6 the others hitting; 7 dust "
     "clouds at the six spots; 8 the last dust. " + MAGIC + ".",
     row(8, 80, 60) + CENTER),
    ("r_rock_hit", "远古崩落：被落石砸中，4 帧", "view_effects `tft_krug_r_rock_hit`（跟随被砸的人，z 2；左右对称）", "18 × 30",
     "被落石砸中的人：一块石头从头顶落下砸碎，碎石往两边崩开。**左右对称**，4 帧。",
     SD + ", " + LV + ", " + DS,
     "A ROCK FALLING ON A UNIT, 4 frames, " + LR + ": 1 an angular rock 6 squares across at the top of the cell; 2 the "
     "rock at the middle, about to hit; 3 the rock bursting into sandstone chips flying out to both sides (mirrored), "
     "a white-yellow flash; 4 the chips falling, a little dust. " + MAGIC + ".",
     row(4, 18, 30) + CENTER),
    ("p_burst", "碎岩重生：碎裂，6 帧", "view_effects `tft_krug_p_burst`（留在他倒下的地方，z 3；左右对称）", "52 × 46",
     "受到致命伤害时：他「砰」地碎开——一道橙金色的闪光从身体中间炸开，大大小小的砂岩碎块往四周飞散，扬起一大团尘土，"
     "碎块落回地上堆着。**左右对称**，6 帧。",
     LV + ", " + SD + ", " + ST + ", " + DS,
     "A STONE BODY SHATTERING, 6 frames, " + LR + ", " + HIM + ": 1 a bright orange-gold flash bursting out from his "
     "middle with jagged glowing cracks; 2 big sandstone chunks (4-6 squares) and dark stone pieces flying out in every "
     "direction (mirrored), a big dust cloud; 3 the chunks at their widest (50 squares across), the dust thick; 4 the "
     "chunks falling; 5 the chunks landing at the bottom in a heap round the middle, the dust thinning; 6 the last dust, "
     "a faint glow between the pieces. " + MAGIC + ".",
     row(6, 52, 46) + CENTER),
    ("p_up", "碎岩重生：重新站起来（小石甲虫），6 帧", "view_effects `tft_krug_p_up`（跟随他，z 3；左右对称）", "44 × 40",
     "碎块重新聚起来：地上的碎石和尘土往中间吸，一圈橙金色的光缝亮起来，然后「轰」地一下尘土往外推开（这时周围的敌人被嘲讽）。**左右对称**，6 帧。",
     LV + ", " + SD + ", " + DS,
     "A STONE BODY REFORMING, 6 frames, " + LR + ": 1 small sandstone chips lying round the bottom middle, glowing seams "
     "between them; 2 the chips pulled up and inward toward the middle (mirrored); 3 an orange-gold glow ring 30 squares "
     "wide and 10 tall " + GROUND_E + " at the bottom; 4 a burst: a dust ring pushed out 42 squares wide and a white-"
     "yellow flash in the middle; 5 the dust thinning, little pebbles falling; 6 the last dust. " + MAGIC + ".",
     row(6, 44, 40) + CENTER),
    ("p_mini", "碎岩重生：小石甲虫（剩下这条命），6 帧循环", "view_buffs `tft_krug_p_mini`（跟随他，z -1；左右对称）", "34 × 10",
     "重生后的小石甲虫：脚下一圈若隐若现的**橙金色裂纹圈**，一明一暗，偶尔有小石子掉下。画在**地上**（扁椭圆），不要太显眼。**左右对称**，6 帧循环。",
     LV + ", " + SD,
     "A REBORN STONE AURA, 6 looping frames, " + LR + ": everything " + GROUND_E + ", centred in the cell: a thin ring "
     "of glowing orange-gold CRACKS 32 squares wide and 8 tall, broken into segments; frames 1-6 the segments glowing "
     "brighter and dimmer in turn (mirrored), a tiny pebble or two at the edge. Subtle. " + MAGIC + ".",
     row(6, 34, 10) + CENTER),
]
ICONS = [
    ("skill", "技能 1「岩之摇滚」图标", "skill_icons[0] `asset/tft/icons/tft_krug_skill`",
     "大石球：一块带橙金裂缝的圆形砂岩巨石正往右滚，后面拖着尘土和速度线。",
     ICON + ": a big round SANDSTONE BOULDER with glowing orange-gold cracks rolling to the right, a trail of dust and "
     "two short speed streaks behind it at the left."),
    ("skill2", "技能 2「坚岩外壳」图标", "skill_icons[1] `asset/tft/icons/tft_krug_skill2`",
     "石壳：一块厚厚的棱角巨石像盾牌一样挡在中间，下面露出一只发光的琥珀色眼睛。",
     ICON + ": a thick angular sandstone BOULDER SHELL like a shield in the middle, glowing orange-gold seams on it, "
     "one glowing amber eye peeking out from under its lower edge."),
    ("ult", "大招「远古崩落」图标", "skill_icons[2] `asset/tft/icons/tft_krug_ult`",
     "崩落：一只大石拳从上往下砸进地面，地面裂开发光，碎石往两边飞。",
     ICON + ": a huge dark STONE FIST slammed down from above into the ground at the centre, the ground split by "
     "glowing orange-gold cracks, angular rocks flying out to both sides."),
]
BIG_FX = ["r_slam", "r_rocks"]

GROUPS = [
    ("q_shield e_shell (stone armour)", ["malphite_base_p_shield_circle", "malphite_base_p_shield_refresh_overlay",
                                        "malphite_base_x_small_stone", "malphite_base_p_rocks"]),
    ("a_hit q_hit r_rock_hit (stone impacts)", ["sru_krug_ba_impactpuffs_2x2", "siege_siegecannon_impactillaoi_base_ba_dirt_rock",
                                                "malphite_base_z_seismicshard", "malphite_base_z_sparks"]),
    ("r_slam r_mark e_cast (ground cracks)", ["malphite_base_z_furrow", "malphite_skin16_q_crack_dissolve",
                                             "malphite_base_p_lava_pan", "malphite_base_r_rock_debris"]),
    ("p_burst p_up r_rocks (shattering)", ["sru_krug_death_dustspikes_6x1", "sru_krug_death_pebbles_4x4",
                                          "sru_krug_death_dustpuffs_2x2", "malphite_base_r_rock_debris_blur"]),
    ("dust smoke (r_jump r_hit)", ["sru_krug_spawn_smoke", "malphite_base_r_smoke01", "malphite_base_w_smokeerode",
                                   "malphite_base_z_smoke08"]),
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
    """The Ancient Krug at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"远古石甲虫 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 远古石甲虫：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/krug_design.png`："
      "四肢着地、驼着砂岩巨石背的石头巨兽，巨石上发光的橙金裂缝，深紫褐的石头身体和大石拳，右下方小小的硬壳脸和两只琥珀眼睛）。"
      f"远古石甲虫在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/krug_size.png`：他缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是英雄联盟里峡谷石甲虫、墨菲特的特效贴图（金铲铲第 18 赛季的石甲虫没有自己的特效贴图；**灰色的形状，游戏里再染色**：石甲、石块冲击、地面裂缝、碎裂的碎石、尘土），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **远古石甲虫是一块会动的岩石，特效都是石头**：棱角分明的**石块和砂岩碎片**、发光的**橙金色裂缝**（和他巨石背上的裂缝一样）、"
      "滚动和砸地时的尘土；不要蓝色，不要魔法符文，不要光滑的霓虹光束，不要软软的圆泡泡。")
    a("> - **特效要亮**：每道光、每道裂缝都有最亮一档或白黄色的高光，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**（石块、碎片、怒气符号这些实物可以有一圈深色描边）。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `krug_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `krug_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「碎岩重生」 | 每条命第一次受到致命伤害时碎成一堆石头，片刻后以小石甲虫站起来（部分血量、攻速提高），嘲讽周围的敌人 | `p_burst` · `p_up` · `p_mini` · `e_taunt` |")
    a("| 普攻 | 立起身子，两只石拳砸下去 | `a_hit` |")
    a("| 技能 1 =「岩之摇滚」 | 身上包上一层石头（护盾），缩成大石球滚向目标，撞上造成伤害并击退 | `q_shield` · `q_hit` |")
    a("| 技能 2 =「坚岩外壳」 | 缩进巨石里，护甲魔抗大增，嘲讽周围的敌人 | `e_cast` · `e_shell` · `e_taunt` |")
    a("| 大招 =「远古崩落」 | 一跃而起（目标脚下出现落点圈），砸进敌群：冲击波击飞周围的敌人，半秒后天上落下碎石 | `r_jump` · `r_mark` · `r_slam` · `r_hit` · `r_rocks` · `r_rock_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、护盾、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("发光的橙金裂缝（裂纹、光缝、闪光、怒气符号）", LAVA), ("砂岩（石块、碎片、图标里的巨石）", SAND),
                        ("深色石头（大石块、石拳、描边）", STONE), ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `krug_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, zh, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `krug_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `krug_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `krug_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_krug_fx`（小的）和 `tft_krug_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- p_burst、p_up 由 tft.dll 在碎岩重生时播（p_mini、e_taunt 是它挂的 buff）；q_shield 在技能 1 出手时播；r_jump 在大招起跳时留在原地，r_mark 跟着目标，r_rocks 在砸地后 30 tick 播。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="krug_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "krug_packs"), help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_krug.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "krug_design.png"))
    shape = size_sheet(os.path.join(out, "design", "krug_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"krug_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"krug_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
