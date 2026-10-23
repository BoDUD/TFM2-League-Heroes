#!/usr/bin/env python3
"""Build azir_fx_pack.zip: step 3 of Azir's sprite - Codex draws his effects (pack_aurora_fx.py's way).

    python tools/lol/fx_ref_azir.py           # League's particle textures -> C:/t/az_work/fxref (Riot's art, local only)
    python tools/art/pack_azir_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name azir_fx_redo_pack]

The pack (C:/t/az_work/fx/azir_fx_pack, zipped into --out, default dist/azir_packs) holds PROMPTS.md (also written to
assets/source/azir/PROMPTS_FX.md), design/azir_design.png (the idle at 4x, its own squares), design/azir_size.png (at
game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Azir, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_azir.py, the user's picks 2026-10-23: mid, layout C - Q / E /
R, the soldiers and the Sun Disc in the passive): view_projectiles a_bolt, q_wave; view_effects a_hit, s_stab, s_spawn,
q_land, q_hit, e_shield, e_land, e_hit, r_rise (big), r_hit, r_dust; view_buffs slow (q_slow); and the Sun Disc's for the
add-on: d_rise, d_beam (big), d_glow. The soldier and the guard themselves are sprite sheets from the pose round, not
effects.
League's colours: the SAND of Shurima - pale gold, ochre and brown dust, glittering grains - with the Emperor's SUN-GOLD
light (white-gold flares and rays) and TEAL glints (his gems); the Sun Disc's beam a white-gold solar ray. Red side: the
client never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right; a
projectile is turned with its flight, so it is drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/az_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "azir", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "azir", "hd")
NAME = "azir_fx_pack"
PPU = 1.5

SANDR = "#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418"   # Shurima's sand: pale gold to brown dust
SUN = "#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12"              # the Emperor's sun-gold light
TEAL = "#FFFFFF, #D4FFFA, #74F0E6, #22B8C8, #106878"             # his gems' teal glints
DUST = "#E8D8B8, #C4A878, #8C7048, #5A4630"                      # dull dust and grit
SA = f"a Shurima sand ramp ({SANDR})"
SU = f"a sun-gold light ramp ({SUN})"
TE = f"a teal glint ramp ({TEAL})"
DU = f"a dull dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
EMPIRE = ("everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, "
          "white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = "he stands in the middle, not drawn: 34 squares wide and 40 tall (the sceptre not counted)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack (his own bolt, when no soldier stabs)
    ("a_bolt", "普攻：权杖射出的一道沙光，4 帧循环", "view_projectiles `league_azir_a_bolt`（弹道，z 2；上下对称）", "14 × 8",
     "没有沙兵能刺时，他权杖射出的一小道金色沙光：亮白金的核心，后面拖一条旋转的沙粒尾巴。**朝右飞、上下对称**，4 帧循环。",
     SU + ", " + SA,
     "A SMALL SAND BOLT, 4 looping frames, " + TB + ": a white-gold core 4 squares across at the right, a short tapering "
     "trail of swirling pale-gold sand grains 9 squares long behind it, the grains moving back frame to frame. " + EMPIRE + ".",
     row(4, 14, 8) + CENTER),
    ("a_hit", "普攻：沙光打中，3 帧", "view_effects `league_azir_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "沙光打中：一个白金色的闪光，四周喷出一圈沙粒。**左右对称**，3 帧。",
     SU + ", " + SA,
     "A SAND BOLT LANDING, 3 frames, " + LR + ": 1 a white-gold flash 5 squares across; 2 a ring of pale-gold sand grains "
     "bursting out 11 across at mirrored places; 3 the grains further out, fading to ochre. " + EMPIRE + ".",
     row(3, 12, 12) + CENTER),
    # ---- passive: Arise! (the soldiers)
    ("s_spawn", "沙兵现身：地上隆起的沙堆，5 帧", "view_effects `league_azir_s_spawn`（在沙兵站的地方，地上，z 1，不跟随；左右对称）",
     "24 × 12",
     "沙兵出现的地方（参考 sandmound、blowing_sand）：地上一圈沙子打旋隆起成一个小沙堆，几颗亮晶晶的沙粒弹起来，然后散开落下。"
     "**画在地上（从斜上方看的椭圆）、左右对称**，5 帧。沙兵本人另画，不要画人。",
     SA + ", " + SU + ", " + DU,
     "SAND RISING, 5 frames, " + LR + ", on the GROUND (an ellipse seen from above, three times as wide as tall): 1 a "
     "small swirl of pale-gold sand 10 squares wide; 2 the swirl widening to 20, the sand heaping up in the middle into a "
     "mound 5 squares tall; 3 the mound at its highest with glittering grains and two white-gold glints jumping up; 4 "
     "the mound sinking and spreading; 5 a thin ring of settling dust. No soldier drawn. " + EMPIRE + ".",
     row(5, 24, 12) + CENTER),
    ("s_stab", "沙兵刺中：一根沙矛刺在敌人身上，4 帧", "view_effects `league_azir_s_stab`（跟随目标，z 3；左右对称）", "14 × 30",
     "沙兵刺中敌人（参考 soldier_spear、ba_yellow_ray）：一根**金色的沙矛**从上往下刺到敌人身上，矛尖一闪，刺中的地方炸开一圈沙粒。"
     "**竖直、左右对称**（游戏不会翻转它），4 帧。",
     SU + ", " + SA + ", " + TE,
     "A SAND SPEAR STRIKING, 4 frames, " + LR + ": 1 a vertical gold spear of packed sand 3 squares wide stabbing down "
     "from the top of the cell, its leaf-shaped white-gold tip at the target's chest; 2 the tip flashing white with a "
     "teal glint; 3 a burst of sand grains around the tip 12 squares across at mirrored places, the spear crumbling "
     "into sand from the top; 4 only falling grains. " + TARGET + ". " + EMPIRE + ".",
     row(4, 14, 30) + CENTER),
    # ---- skill: Q Conquering Sands
    ("q_wave", "狂沙猛攻：冲出去的一道沙浪，4 帧循环", "view_projectiles `league_azir_q_wave`（弹道，z 2；上下对称）", "26 × 12",
     "沙兵冲锋时卷起的一道沙浪（参考 soldiersandtrail、wisps_mis）：前面一个尖尖的金色沙头，后面翻滚的沙尘带和亮晶晶的沙粒。"
     "**朝右飞、上下对称**，4 帧循环（沙浪翻滚）。",
     SA + ", " + SU + ", " + DU,
     "A SAND RUSH, 4 looping frames, " + TB + ": at the right a pointed white-gold head of packed sand 6 squares long, "
     "behind it a rolling band of pale-gold and ochre sand 18 squares long, wavy at its edges with glittering grains, the "
     "waves rolling back frame to frame. " + EMPIRE + ".",
     row(4, 26, 12) + CENTER),
    ("q_land", "狂沙猛攻：沙兵落地扬起的沙尘，5 帧", "view_effects `league_azir_q_land`（在落点，地上，z 1，不跟随；左右对称）",
     "36 × 14",
     "沙兵冲到落点时扬起的一大圈沙尘（参考 q_end、q_dust）：地上一圈沙子往外喷开，几道金光闪一下，沙尘慢慢落下。**地上的椭圆、左右对称**，5 帧。",
     SA + ", " + SU + ", " + DU,
     "SAND CRASHING DOWN, 5 frames, " + LR + ", on the GROUND (an ellipse three times as wide as tall): 1 a white-gold "
     "flash 8 squares wide in the middle; 2 a ring of sand spraying out 24 wide with a few short gold rays; 3 the ring at "
     "34 wide, puffs of ochre dust rising at mirrored places; 4 the dust drifting, thinning; 5 a faint ring settling. "
     + EMPIRE + ".",
     row(5, 36, 14) + CENTER),
    ("q_hit", "狂沙猛攻：打中，4 帧", "view_effects `league_azir_q_hit`（跟随目标，z 2；左右对称）", "16 × 18",
     "沙浪打中敌人：一团金色沙子撞上去炸开，沙粒四散。**左右对称**，4 帧。",
     SA + ", " + SU,
     "A SAND RUSH STRIKING, 4 frames, " + LR + ": 1 a white-gold flash 6 squares across on the target's chest; 2 a burst "
     "of pale-gold sand 14 across; 3 sand grains flying out at mirrored places; 4 the grains falling, fading to ochre. "
     + TARGET + ". " + EMPIRE + ".",
     row(4, 16, 18) + CENTER),
    ("slow", "狂沙猛攻：减速，脚下流沙，4 帧循环", "view_buffs `league_azir_q_slow`（tag `slow`，跟随，脚下，z -1；左右对称）", "16 × 8",
     "被减速的敌人脚下：一圈慢慢打旋的流沙。**左右对称**，4 帧循环。",
     SA + ", " + DU,
     "QUICKSAND, 4 looping frames, " + LR + ", on the GROUND under the feet (an ellipse 14 squares wide and 5 tall): a "
     "slowly swirling ring of pale-gold and ochre sand, two sand ripples turning round it at mirrored places. "
     + EMPIRE + ".",
     row(4, 16, 8) + CENTER),
    # ---- skill2: E Shifting Sands
    ("e_shield", "流沙移形：身上的沙之护盾，4 帧", "view_effects `league_azir_e_shield`（在他身上，跟随，z 3；左右对称）", "40 × 46",
     "冲刺时他身上套的一层沙之护盾（参考 e_shield_base、outerring）：围着他一圈旋转的金色沙流，外圈一道亮金色的弧，上下两头有几颗青色的闪光。"
     "**只画外圈，身体位置留空，左右对称**，4 帧。",
     SA + ", " + SU + ", " + TE,
     "A SAND SHIELD, 4 frames, " + LR + ": a shell of swirling pale-gold sand streams around the body, 38 squares wide "
     "and 44 tall, a bright white-gold arc along its outer edge, two teal glints at the top and the bottom; the streams "
     "turning round frame to frame; the middle 30 x 38 squares left EMPTY for his body. " + HIM + ". " + EMPIRE + ".",
     row(4, 40, 46) + CENTER),
    ("e_land", "流沙移形：冲到落点喷起的沙柱，5 帧", "view_effects `league_azir_e_land`（在他落地的地方，地上，z 1，不跟随；左右对称）",
     "30 × 24",
     "他化沙冲到敌人身上时，脚下喷起一圈沙柱（参考 e_geyser）：地上一圈沙子猛地往上喷，然后落下。**左右对称**，5 帧。",
     SA + ", " + SU + ", " + DU,
     "A SAND GEYSER, 5 frames, " + LR + ": 1 a ring of sand on the ground 16 wide (an ellipse); 2 columns of sand bursting "
     "up 16 squares tall around the ring with a white-gold flash in the middle; 3 the columns at their highest, grains "
     "flying out at mirrored places; 4 the sand falling back; 5 a ring of settling dust 28 wide. " + EMPIRE + ".",
     row(5, 30, 24) + CENTER),
    ("e_hit", "流沙移形：撞中，4 帧", "view_effects `league_azir_e_hit`（跟随目标，z 2；左右对称）", "16 × 20",
     "冲刺撞中敌人：一团沙子炸开，几道金光。**左右对称**，4 帧。",
     SA + ", " + SU,
     "A SAND DASH STRIKING, 4 frames, " + LR + ": 1 a white-gold flash on the target's chest; 2 a burst of sand 14 across "
     "with four short gold rays at mirrored angles; 3 the sand flying out; 4 the grains falling. " + TARGET + ". "
     + EMPIRE + ".",
     row(4, 16, 20) + CENTER),
    # ---- ult: R Emperor's Divide
    ("r_rise", "禁军之墙：一排沙墙从地里升起，6 帧", "view_effects `league_azir_r_rise`（大表，在他前面，地上，z 1，不跟随；左右对称）",
     "70 × 30",
     "禁军出现的地方：地上一长条沙子猛地往上翻涌成一道沙墙（禁军从里面冲出来，禁军本人另画），然后沙墙塌落成沙尘。"
     "**横着的一长条、左右对称**，6 帧。",
     SA + ", " + SU + ", " + DU,
     "A WALL OF SAND RISING, 6 frames, " + LR + ": 1 a long line of churning sand on the ground 60 squares wide and 4 tall; "
     "2 the sand surging up into a ragged wall 14 squares tall all along the line, white-gold glints on its crest; 3 the "
     "wall at its highest, 24 tall, grains blowing off its top; 4 the wall breaking apart into sand curtains; 5 the "
     "curtains falling; 6 a long low band of settling dust. No soldiers drawn. " + EMPIRE + ".",
     row(6, 70, 30) + CENTER),
    ("r_dust", "禁军之墙：冲锋时脚下扬起的沙尘，4 帧", "view_effects `league_azir_r_dust`（在冲锋的禁军脚下，地上，z 1，不跟随；左右对称）",
     "30 × 12",
     "禁军冲锋时脚下踢起的沙尘：地上一团团沙尘往两边扬起。**左右对称**，4 帧。",
     SA + ", " + DU,
     "CHARGE DUST, 4 frames, " + LR + ", on the GROUND: 1 two puffs of ochre and pale-gold dust 8 squares wide at mirrored "
     "places; 2 the puffs growing and rising to 10 squares tall with grains kicked up; 3 the puffs drifting apart, "
     "thinning; 4 faint wisps. " + EMPIRE + ".",
     row(4, 30, 12) + CENTER),
    ("r_hit", "禁军之墙：撞飞，4 帧", "view_effects `league_azir_r_hit`（跟随目标，z 2；左右对称）", "18 × 22",
     "禁军的盾撞中敌人：一个白金色的大冲击闪光，沙粒和金光向四面炸开。**左右对称**，4 帧。",
     SU + ", " + SA,
     "A SHIELD SLAM, 4 frames, " + LR + ": 1 a big white-gold impact flash 10 squares across on the target's chest; 2 a "
     "star of six short gold rays 18 across at mirrored angles with sand bursting between them; 3 the sand flying out; "
     "4 the grains falling, fading to ochre. " + TARGET + ". " + EMPIRE + ".",
     row(4, 18, 22) + CENTER),
    # ---- passive: the Sun Disc (the add-on)
    ("d_rise", "太阳圆盘：从沙里升起，6 帧", "view_effects `league_azir_d_rise`（大表，在我方塔的废墟上，地上，z 1，不跟随；左右对称；附加包放）",
     "56 × 26",
     "太阳圆盘立起来的地方（参考 towersandbib、solarflare）：地上一大圈沙子打旋，中间一道金光冲天，沙子往外翻开。圆盘本人另画。**左右对称**，6 帧。",
     SA + ", " + SU + ", " + TE,
     "THE SUN DISC RISING, 6 frames, " + LR + ": 1 a wide swirl of sand on the ground 30 squares across (an ellipse); 2 "
     "the swirl at 50 across, a column of white-gold light 6 wide shooting up from its middle to the top of the cell; 3 "
     "the light at its brightest with teal glints, sand spraying out at mirrored places; 4 the column thinning; 5 the "
     "sand settling in a ring; 6 a faint gold ring. No disc drawn. " + EMPIRE + ".",
     row(6, 56, 26) + CENTER),
    ("d_beam", "太阳圆盘：射下来的太阳光束，5 帧", "view_effects `league_azir_d_beam`（大表，跟随目标，z 3；左右对称；附加包放）",
     "16 × 60",
     "太阳圆盘攻击敌人（参考 z_beam_core、beam_outer）：一道从天上直直打下来的白金色光柱，打在敌人身上炸开一圈金光。**竖直、左右对称**，5 帧。",
     SU + ", " + TE,
     "A SOLAR RAY, 5 frames, " + LR + ": 1 a thin white-gold line 2 squares wide from the top of the cell down to the "
     "target's chest; 2 the ray 8 squares wide, a white core and sun-gold edges, a flash where it lands; 3 the ray at "
     "its widest, 12, a ring of gold light 14 across at its foot with two teal glints; 4 the ray thinning; 5 sparks "
     "fading at the foot. " + TARGET + " at the bottom of the cell. " + EMPIRE + ".",
     row(5, 16, 60) + CENTER),
    ("d_glow", "太阳圆盘：脚下的光环，6 帧循环", "view_effects `league_azir_d_glow`（在圆盘脚下，地上，z -1，不跟随；左右对称；附加包放）",
     "40 × 14",
     "太阳圆盘立着的时候，它脚下地上一圈慢慢转的金色光环和沙粒。**左右对称**，6 帧循环。",
     SU + ", " + SA,
     "A SOLAR RING, 6 looping frames, " + LR + ", on the GROUND (an ellipse 38 squares wide and 12 tall): a thin ring of "
     "sun-gold light with four short rays pointing out at mirrored angles, glittering grains drifting round it, the "
     "ring brightening and dimming. " + EMPIRE + ".",
     row(6, 40, 14) + CENTER),
]
BIG_FX = ["r_rise", "d_rise", "d_beam"]
FLYING = ["a_bolt", "q_wave"]
FORWARD = []

GROUPS = [
    ("a_bolt a_hit (his own bolt)", ["azir_base_ba_beam_1x3", "azir_base_ba_hit", "azir_base_ba_twirl",
                                     "azir_base_ba_yellow_ray"]),
    ("s_spawn s_stab (the soldiers)", ["azir_base_w_sandmound", "azir_base_w_soldier_spear", "azir_base_w_blowing_sand",
                                       "azir_base_w_glint"]),
    ("q_wave q_land q_hit slow (Conquering Sands)", ["azir_base_q_soldiersandtrail02", "azir_base_q_wisps_mis",
                                                     "azir_base_q_dust_rgba", "azir_base_q_end"]),
    ("e_shield e_land e_hit (Shifting Sands)", ["azir_base_e_shield_base", "azir_base_e_shield_outerring",
                                                "azir_base_e_geyser_rgba", "azir_base_e_hit"]),
    ("r_rise r_dust r_hit (Emperor's Divide)", ["azir_base_r_buff_swirl", "azir_base_r_sanddots", "azir_base_e_dust_rgba",
                                                "azir_base_z_dust"]),
    ("d_rise d_beam d_glow (the Sun Disc)", ["azir_base_z_beam_core", "azir_base_z_beam_outer", "azir_base_z_solarflare",
                                             "azir_base_w_towersandbib"]),
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
    """Azir, the soldier and the disc at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x(), design_1x("soldier"), design_1x("disc")]
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
    d.text((8, 36), f"阿兹尔 {figs[0].shape[1]}×{figs[0].shape[0]} 格、沙兵、太阳圆盘，原版斗士 {figs[3].shape[1]}×{figs[3].shape[0]} 格（4 倍）",
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
    a("# 沙漠皇帝 阿兹尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/azir_design.png`：Q 版沙漠皇帝，鹰首金盔、金甲青蓝宝石、深紫袍子披风、"
      "手里一根竖直的长权杖）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连权杖 {h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。沙兵、禁军、太阳圆盘本人是另外的图，**特效里不要画他们**。")
    a("> - 大小对照 `design/azir_size.png`：阿兹尔、沙兵、太阳圆盘放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿兹尔自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**阿兹尔是恕瑞玛的沙漠皇帝，所有特效都是黄沙的魔法**：打旋的浅金色沙子、赭黄的沙尘、亮晶晶的沙粒、白金色的太阳光芒，"
      "点缀几颗青色的闪光（他宝石的颜色）；不要火，也不要光滑的霓虹光束。")
    a("> - **特效要亮**：每股沙流、每道光都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、沙、尘、冲击、光环都没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `azir_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/azir_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 权杖一指，身边的沙兵替他刺；没有沙兵能刺时他自己射一道沙光 | `a_bolt` · `a_hit` · `s_stab` |")
    a("| 被动「沙兵现身」 | 普攻时在目标身边从沙里召出黄沙士兵（最多 3 个） | `s_spawn` · `s_stab` |")
    a("| 被动「太阳圆盘」（附加包） | 每局一次，在我方倒下的塔的废墟上立起太阳圆盘，向敌人射太阳光束 | `d_rise` · `d_beam` · `d_glow` |")
    a("| 技能 1 =「狂沙猛攻」 | 沙兵卷起沙浪冲向目标，落地马上刺：伤害、减速 | `q_wave` · `q_hit` · `q_land` · `slow` |")
    a("| 技能 2 =「流沙移形」 | 套上沙之护盾化沙冲向敌人（被贴身时往后跳），撞中时多召一个沙兵 | `e_shield` · `e_land` · `e_hit` |")
    a("| 大招 =「禁军之墙」 | 一排禁军从沙墙里冲出，撞飞敌人；正推把人推远，反推（E 之后）把人推回我方 | `r_rise` · `r_dust` · `r_hit` |\n")
    a("连招：**流沙移形撞中英雄 → 禁军之墙反推**，**狂沙猛攻落地 → 沙兵马上刺**，**禁军之墙撞飞 → 狂沙猛攻**，**流沙移形撞中 → 多一个沙兵**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙、尘没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **都是黄沙的魔法**：浅金、赭黄、棕色沙尘、白金色的光、几颗青色闪光；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("恕瑞玛·黄沙", SANDR), ("太阳·金光", SUN), ("宝石·青", TEAL), ("沙尘·灰棕", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（沙堆、沙尘、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `azir_fx_{name}.png`：{title}\n")
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
        a(f"| `azir_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_azir_fx`（小的）和 `league_azir_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_azir.py 的 views；q_slow 用 `slow`）。沙兵 `league_azir_soldier`（tags soldier_a/b/c + 刺）、禁军 `league_azir_guard`"
      "（charge 朝右 / 朝左翻一份）、太阳圆盘是姿势那一轮的图做的表。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；d_glow 在圆盘立着时一直循环。")
    a("- 用 `pixel_1x/` 切格（import_aurora_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="azir_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "azir_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_azir.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "azir_design.png"))
    shape = size_sheet(os.path.join(out, "design", "azir_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"azir_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
