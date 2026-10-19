#!/usr/bin/env python3
"""Build zoe_fx_pack.zip: step 3 of Zoe's sprite - Codex draws her effects (pack_rammus_fx.py's way, its sheets reused).

    python <scratchpad>/fx_ref_zo.py           # League's particle textures -> C:/t/zo_work/fxref (Riot's art, local only)
    python tools/art/pack_zoe_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name zoe_fx_redo_pack]

The pack (C:/t/zo_work/fx/zoe_fx_pack, zipped into --out, default dist/zoe_packs) holds PROMPTS.md (also written to
assets/source/zoe/PROMPTS_FX.md), design/zoe_idle.png (her idle at 4x, the design's squares at PPU 1.5),
design/zoe_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/zoe_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Zoe grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_zoe.py): view_projectiles a_star, p_star, q_star (the portal's
star too), e_bubble, w_missile; view_effects a_hit, p_hit, q_hit, e_hit, e_wake, e_trap, w_hit, r_portal_in (the cast
and the far end on the way back), r_portal_out (the far end and home); view_buffs e_drowsy, e_zz, w_haste. League's
colours: her stars are gold-white starlight with pink-violet sparkles and blue stardust, the bubble an iridescent soap
bubble (blue, violet, pink), the portal a ring of white light round a deep-purple night sky full of stars, Spell Thief's
missiles sky blue. Red side: the client never mirrors an effect picture, so every hit, buff and ground picture is
symmetric left to right; a projectile's picture is turned with its flight (drawn flying right, the trail behind it on
the left), so it is symmetric top to bottom instead (it flies upside down to the left).
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

TMP = "C:/t/zo_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "zoe", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_zoe")
NAME = "zoe_fx_pack"

STAR = "#FFFFFF, #FFF6C8, #FFE07A, #F7B23C, #C8761E, #7A4214"        # gold-white starlight
COSMIC = "#FFFFFF, #FFD6F2, #FF8FD8, #D65AD8, #8E3CC8, #4A2280"      # pink-violet sparkles
DUST = "#FFFFFF, #CFE6FF, #7FB0FF, #6A5ACD, #3E2A8C, #1E1446"        # blue stardust, the portal's night sky
BUBBLE = "#FFFFFF, #E2F4FF, #A8D8FF, #9C8CFF, #E08CFF, #FF9CCB, #5A4AB8"  # the iridescent sleepy bubble
SKY = "#FFFFFF, #D8F6FF, #8EE2FF, #3EB4F0, #1E70C0, #123C78"          # Spell Thief's missiles
ST = f"a gold-white starlight ramp ({STAR})"
CO = f"a pink-violet sparkle ramp ({COSMIC})"
DU = f"a blue stardust / night-sky ramp ({DUST})"
BU = f"an iridescent soap-bubble ramp ({BUBBLE})"
SK = f"a sky-blue ramp ({SKY})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, energy, sparkles, mist, bubbles, rings or portals")
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
CHAMP = RF.CHAMP
HER = "the small girl stands in the middle, not drawn: 35 squares from her crown to the ground, about 24 squares wide"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack and More Sparkles!
    ("a_star", "普攻：飞出去的小星星（弹道，循环），4 帧",
     "view_projectiles `league_zoe_a_star`（跟着弹道转向；上下对称）", "12 × 8",
     "她普攻弹出去的一颗小星星：金白色的四角小星，后面拖着一小串粉紫色的星点（参考 ba_tar_star、zoe_baseq_sparkles）。"
     "**朝右飞，尾巴在左边，上下严格对称**（游戏按飞行方向转这张图，往左飞时是倒过来的），4 帧循环。",
     f"{ST} and {CO}",
     "A LITTLE FLYING STAR, 4 frames, a seamless loop, " + TB + ": a white-gold four-pointed star 5 squares across at the "
     "right, a short trail of 4-5 pink-violet sparkle squares behind it to the left; each frame the star twinkles (its "
     "points 1 square longer on frames 2 and 4) and the sparkles shift.",
     row(4, 12, 8) + "; the star's middle on the cell's middle row, 3 squares from its right edge."),
    ("a_hit", "普攻：小星星打中目标，3 帧", "view_effects `league_zoe_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "小星星打中目标的一下：一团金白色的小闪光，四周溅出几粒粉紫色的星点（参考 ba_tar_gather、z_spark）。**左右对称**，约 12 × 12 格。",
     f"{ST} and {CO}",
     "A SMALL STAR HIT, 3 frames, " + LR + ": 1 a white-gold four-pointed flash 6 squares across; 2 the flash 9 across "
     "with 6 pink-violet sparkle squares flying out; 3 only the sparkles further out, fading.",
     row(3, 12, 12) + CENTER),
    ("p_star", "烟火四射！：强化普攻的大星星（弹道，循环），4 帧",
     "view_projectiles `league_zoe_p_star`（跟着弹道转向；上下对称）", "16 × 10",
     "放过技能后的强化普攻：更大更亮的星星，金白色的芯外面一圈粉紫色的光，后面拖着一长串粉紫、天蓝的星点（参考 zoe_temp_ba_flare-sun_lightblue、"
     "stardust）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     f"{ST}, {CO} and {DU}",
     "A BIG SPARKLY STAR, 4 frames, a seamless loop, " + TB + ": a white-gold star 7 squares across with a pink-violet glow "
     "round it at the right, a trail of pink-violet and blue sparkle squares 8 squares long behind it to the left; each "
     "frame the star's points flash and the trail's sparkles twinkle.",
     row(4, 16, 10) + "; the star's middle on the cell's middle row, 4 squares from its right edge."),
    ("p_hit", "烟火四射！：大星星打中目标，4 帧", "view_effects `league_zoe_p_hit`（跟随目标，画在人物上面 z 2；左右对称）", "18 × 18",
     "强化普攻打中的一下：一团金白色的星形闪光炸开，一圈粉紫色、天蓝色的星点烟火往外散（参考 ba_tar_gather、zoe_baseq_sparkles）。"
     "**左右对称**，约 18 × 18 格。",
     f"{ST}, {CO} and {DU}",
     "A SPARKLE BURST, 4 frames, " + LR + ": 1 a white-gold star flash 8 squares across; 2 the flash 12 across and a ring "
     "of 8 pink-violet and blue sparkles; 3 the sparkles 16 across like a little firework, the flash fading; 4 only "
     "twinkling sparkles far out.",
     row(4, 18, 18) + CENTER),
    # ---- Q Paddle Star (also the portal's star of R)
    ("q_star", "Q 飞星乱入！：飞星（弹道，循环），4 帧",
     "view_projectiles `league_zoe_q_star`、`league_zoe_r_star`（跟着弹道转向；上下对称）", "24 × 14",
     "她踢出去的飞星：一颗大大的金白色星星，外面一圈蓝紫色的光晕，后面拖着长长的一串蓝紫、粉紫色的星尘（参考 q_mis_sphereshape、"
     "zoe_baseq_sparkles、stardust、r_beam_stars）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     f"{ST}, {DU} and {CO}",
     "A SHINING PADDLE STAR, 4 frames, a seamless loop, " + TB + ": a big white-gold five-pointed star 10 squares across "
     "inside a soft blue-violet glow ring at the right, a long trail of blue-violet and pink stardust squares 12 squares "
     "long behind it to the left, widest next to the star; each frame the star's points flash in turn (mirrored top and "
     "bottom) and the stardust drifts.",
     row(4, 24, 14) + "; the star's middle on the cell's middle row, 6 squares from its right edge."),
    ("q_hit", "Q：飞星打中目标，4 帧", "view_effects `league_zoe_q_hit`（跟随目标，画在人物上面 z 2；左右对称）", "20 × 20",
     "飞星砸中目标：一团金白色的星形大闪光，一圈蓝紫色的星尘环炸开，碎星往外飞（参考 q_impactglow、z_flash_01、stardust）。"
     "**左右对称**，约 20 × 20 格（飞得越远伤害越高，闪光是同一张）。",
     f"{ST}, {DU} and {CO}",
     "A STAR IMPACT, 4 frames, " + LR + ": 1 a white-gold star flash 10 squares across with 4 long rays; 2 the flash 14 "
     "across and a blue-violet stardust ring 16 across; 3 the ring 20 across, thinner, 8 pink and gold star chips flying "
     "out; 4 only fading chips and a faint ring.",
     row(4, 20, 20) + CENTER),
    # ---- E Sleepy Trouble Bubble
    ("e_bubble", "E 催眠气泡：飞出去的气泡（弹道，循环），4 帧",
     "view_projectiles `league_zoe_e_bubble`（跟着弹道转向；上下对称）", "14 × 14",
     "她踢出去的催眠气泡：一个圆圆的肥皂泡，泡壁是蓝、紫、粉的彩虹色，里面透明偏淡蓝，两边对称地各一点白色高光，后面拖两三粒小泡（参考 "
     "glow_distort、w_balloon_glow）。**朝右飞，上下严格对称**，4 帧循环（泡壁的颜色转动）。",
     BU,
     "A SLEEPY SOAP BUBBLE, 4 frames, a seamless loop, " + TB + ": a round bubble 11 squares across at the right, its rim 1-2 "
     "squares thick in iridescent blue, violet and pink, the inside pale see-through blue (light squares, not filled "
     "solid), two white highlight squares placed symmetric top and bottom; 2 tiny bubbles trailing behind it to the left; "
     "each frame the rim's colours move round it (symmetric top and bottom).",
     row(4, 14, 14) + "; the bubble's middle on the cell's middle row, 6 squares from its right edge."),
    ("e_hit", "E：气泡打中英雄（他身上，跟随），4 帧", "view_effects `league_zoe_e_hit`（跟随目标，画在人物上面 z 2；左右对称）", "20 × 20",
     "气泡打中敌方英雄：泡泡在他身上破开，散成一团粉紫色的梦雾和几个小泡泡（参考 glow_distort、e_blendglow）。**左右对称**，约 20 × 20 格。",
     f"{BU} and {CO}",
     "A BUBBLE POPPING INTO DREAM MIST, 4 frames, " + LR + ": 1 an iridescent bubble 12 squares across; 2 the bubble "
     "bursting into 8 rim shards flying out; 3 a soft cloud of pink-violet mist 16 squares across with 4 small bubbles "
     "rising; 4 only thin mist and 2 bubbles higher up.",
     row(4, 20, 20) + CENTER),
    ("e_drowsy", "E：困倦（敌人头上，循环），4 帧", "view_buffs `league_zoe_e_drowsy`（跟随，画在人物上面 z 3；左右对称；循环）", "14 × 10",
     "困倦的 1.4 秒：敌人头上一小团淡紫色的梦雾，里面几个小泡泡慢慢往上冒（参考 e_blendglow、glow_distort）。**画在头上**，**左右对称**，4 帧循环。",
     f"{BU} and {CO}",
     "DROWSY MIST over a unit's head, 4 frames, a seamless loop, " + LR + ": a low soft band of pale violet mist 12 squares "
     "wide and 3 tall, 3 small iridescent bubbles (2-3 squares) rising out of it at mirrored places; each frame the "
     "bubbles rise a square and a new one starts at the bottom.",
     row(4, 14, 10) + CENTER),
    ("e_zz", "E：昏睡（敌人头上，循环），4 帧", "view_buffs `league_zoe_e_zz`（跟随，画在人物上面 z 3；左右对称；循环）", "16 × 12",
     "昏睡中：敌人头上一个鼓起又缩小的大睡泡（像打呼噜吹的泡泡），两边对称地闪着小星星（参考 glow_distort、emote_skippingrope_star）。"
     "**画在头上**，**左右对称**，4 帧循环。",
     f"{BU} and {ST}",
     "A SNORE BUBBLE over a sleeping unit's head, 4 frames, a seamless loop, " + LR + ": a round iridescent bubble that "
     "swells and shrinks (7, 9, 11, 9 squares across), its rim violet-blue-pink with two white highlight squares at "
     "mirrored places, two tiny gold four-pointed stars at its left and right that twinkle in turn.",
     row(4, 16, 12) + CENTER),
    ("e_wake", "E：打醒的一下（加倍伤害，他身上），4 帧", "view_effects `league_zoe_e_wake`（跟随目标，画在人物上面 z 2；左右对称）",
     "24 × 24",
     "昏睡的敌人被她的飞星打醒、受到加倍伤害：睡泡砰地炸开，一团金白色的星形大闪光，粉紫色的泡壁碎片和星点四散（参考 q_impactglow、"
     "zoe_baseq_sparkles）。**左右对称**，约 24 × 24 格，比普通打中更大更亮。",
     f"{ST}, {BU} and {CO}",
     "A BIG WAKE-UP BURST, 4 frames, " + LR + ": 1 a white-gold star flash 12 squares across with 8 rays; 2 the flash 18 "
     "across, iridescent bubble shards bursting out round it; 3 a ring of pink-violet sparkles 22 across, the shards "
     "further out; 4 only twinkling sparkles at the edge.",
     row(4, 24, 24) + CENTER),
    ("e_trap", "E：没打中时留在地上的气泡（地上，循环），4 帧", "view_effects `league_zoe_e_trap`（不跟随，画在人物下面 z -1；左右对称；每 15 tick 重放）",
     "16 × 14",
     "气泡没打中任何人：落在地上的一个彩虹肥皂泡，贴着地面轻轻一上一下，下面一小片淡紫色的影子（参考 glow_distort、w_balloon_glow）。"
     "**左右对称**，4 帧循环。",
     BU,
     "A BUBBLE RESTING ON THE GROUND, 4 frames, a seamless loop, " + LR + ": a round iridescent bubble 11 squares across "
     "(rim violet-blue-pink, inside pale see-through blue, two white highlight squares at mirrored places) bobbing just "
     "above the ground (its bottom 1, 2, 2, 1 squares up), a flat pale violet glow ellipse 12 wide and 2 tall under it on "
     "the ground.",
     row(4, 16, 14) + "; centered across, the glow's bottom on the cell's bottom row."),
    # ---- W Spell Thief's missiles (fired with R)
    ("w_missile", "W 窃法巧手：飞弹（弹道，循环），4 帧", "view_projectiles `league_zoe_w_missile`（跟着弹道转向；上下对称）", "10 × 8",
     "跟着大招射出的 3 颗法术飞弹：天蓝色的小光球，白芯，后面拖一小段天蓝色的尾巴（参考 r_buff_body_glow、zoe_temp_ba_flare-sun_lightblue）。"
     "**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     SK,
     "A SKY-BLUE SPELL ORB, 4 frames, a seamless loop, " + TB + ": a round sky-blue orb 5 squares across with a white core "
     "at the right, a short tapering sky-blue trail 4 squares long behind it to the left; each frame the core flickers "
     "and the trail wavers (symmetric top and bottom).",
     row(4, 10, 8) + "; the orb's middle on the cell's middle row, 3 squares from its right edge."),
    ("w_hit", "W：飞弹打中，3 帧", "view_effects `league_zoe_w_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "飞弹打中：一团天蓝色的小闪光和几粒溅开的蓝色光点（参考 z_spark）。**左右对称**，约 12 × 12 格。",
     SK,
     "A SMALL SKY-BLUE HIT, 3 frames, " + LR + ": 1 a white-blue flash 6 squares across; 2 a sky-blue ring 9 across with 6 "
     "sparks; 3 only the sparks further out, fading.",
     row(3, 12, 12) + CENTER),
    ("w_haste", "W：加速（她脚下，循环），4 帧", "view_buffs `league_zoe_w_haste`（跟随，画在人物下面 z -1；左右对称；循环）", "26 × 8",
     "窃法巧手的加速：她脚下贴着地面转的一圈粉紫、天蓝色的星光条纹（参考 zoe_temp_r_bard_base_p_speed_swirl_mult、stardust）。"
     "**只画在脚下的地面上**，**左右对称**，4 帧循环。",
     f"{CO} and {SK}",
     "A SPEED SWIRL on the ground at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat ellipse 24 squares wide and "
     "6 tall drawn only as short curved streaks (2-4 squares long) of pink-violet and sky-blue light, mirrored, with a "
     "few white sparkle squares; each frame the streaks move round the ellipse.",
     row(4, 26, 8) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- R Portal Jump
    ("r_portal_in", "R 折返跃迁：她跳进去的传送门（地上，不跟随），6 帧",
     "view_effects `league_zoe_r_portal_in`、`league_zoe_r_portal_back`（不跟随，画在人物下面 z -1；左右对称；大图表）", "40 × 24",
     "她起跳钻进传送门：脚下的地面上打开一个椭圆的传送门——外圈一道白色、粉色、天蓝色的光环，里面是深紫色的夜空，满是小星星；门开大、"
     "星光往上冒，然后门收拢消失（参考 r_portal_ring_colors、r_portal_tex、zoe_hair_nightsky、r_beam_stars、z_portal_cover_black）。"
     "**只画在地面上（她站在中间，不画人）**，**左右对称**，6 帧。",
     f"{DU}, {CO} and {ST}",
     "A PORTAL OPENING AND CLOSING on the ground, 6 frames, " + LR + " (" + HER + "): 1 a small bright white-pink ring on "
     "the ground (an ellipse 12 wide and 4 tall); 2 the ring 26 wide and 9 tall, its inside a deep purple night sky with "
     "white and blue star squares; 3 the portal 36 wide and 13 tall, a rim of white, pink and sky-blue light 2 squares "
     "thick, 6 star sparks rising above it at mirrored places; 4 the same, the sparks higher; 5 the portal shrinking to "
     "24 wide and 8 tall; 6 only a thin fading ring 14 wide and a few sparks.",
     row(6, 40, 24) + "; centered across, the ellipse's middle 7 squares above the cell's bottom row."),
    ("r_portal_out", "R：她钻出来的传送门（地上，不跟随），6 帧",
     "view_effects `league_zoe_r_portal_out`（不跟随，画在人物下面 z -1；左右对称；大图表）", "40 × 24",
     "她从传送门钻出来落地：同样的夜空传送门在落点打开，一圈星光往外炸开，然后收拢（参考 r_portal_ring_colors、r_beam_01、stardust）。"
     "**只画在地面上（她落在中间，不画人）**，**左右对称**，6 帧。",
     f"{DU}, {CO} and {ST}",
     "A PORTAL BURSTING OPEN on the ground as someone drops out of it, 6 frames, " + LR + " (" + HER + "): 1 a white-gold "
     "flash on the ground 14 squares wide and 5 tall; 2 a portal 34 wide and 12 tall, a rim of white, pink and sky-blue "
     "light, a deep purple starry inside; 3 a ring of 10 star sparks bursting outward round it on the ground, the portal "
     "38 wide; 4 the portal shrinking to 26 wide, the sparks further out; 5 the portal 14 wide; 6 only fading sparks.",
     row(6, 40, 24) + "; centered across, the ellipse's middle 7 squares above the cell's bottom row."),
]
BIG_FX = ["r_portal_in", "r_portal_out"]
FLYING = ["a_star", "p_star", "q_star", "e_bubble", "w_missile"]
GROUPS = [
    ("a_star a_hit p_star p_hit", ["zoe_base_ba_tar_star", "zoe_base_ba_tar_gather", "zoe_temp_ba_flare-sun_lightblue",
                                   "zoe_base_z_spark", "zoe_base_stardust", "zoe_base_e_sparkhardedged"]),
    ("q_star q_hit", ["zoe_base_q_mis_sphereshape", "zoe_base_q_impactglow", "zoe_baseq_sparkles",
                      "zoe_base_z_flash_01", "zoe_base_r_beam_stars", "zoe_base_stardust"]),
    ("e_bubble e_hit e_drowsy e_zz e_wake e_trap", ["zoe_base_glow_distort", "zoe_base_w_balloon_glow",
                                                     "zoe_base_e_blendglow", "zoe_base_emote_skippingrope_star"]),
    ("w_missile w_hit w_haste", ["zoe_base_r_buff_body_glow", "zoe_base_z_spark",
                                 "zoe_temp_r_bard_base_p_speed_swirl_mult", "zoe_base_targonlines"]),
    ("r_portal_in r_portal_out", ["zoe_base_r_portal_ring_colors", "zoe_base_r_portal_tex", "zoe_hair_nightsky",
                                  "zoe_base_r_beam_stars", "zoe_base_r_beam_01", "zoe_base_z_meshwaves"]),
]
SHOTS = [("attack", 3, "a_star：手一扬，星星从手上飞出去；a_hit 在目标身上"), ("attack_p", 3, "p_star / p_hit：强化普攻"),
         ("skill", 4, "q_star：落地时把飞星甩出去（大招的飞星也从这里出）"), ("skill2", 4, "e_bubble：飞踢踢出气泡"),
         ("ult", 2, "r_portal_in：起跳时脚下的门"), ("ult", 5, "r_portal_out：落地时脚下的门"),
         ("skill_w", 2, "w_missile：手一扬，飞弹飞出去；w_haste 在脚下"), ("idle", 1, "待机（大小参考）")]


def configure():
    """pack_rammus_fx's sheets drawn from Zoe's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "佐伊"


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    import rig_zoe as Z
    F = Z.form()
    c = F.rig.finish(Z.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 暮光星灵 佐伊：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/zoe_idle.png`：3/4 正面朝右的 Q 版小女孩，深藏青色的长发夹着"
      f"青绿、金黄、珊瑚橙、粉红的星光彩带向身后飘，一紫一蓝的大眼睛，青绿围巾、深蓝短上衣、蓝色裹裙、金手镯）。她在游戏里是**高清**的"
      f"（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽（连头发）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/zoe_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/zoe_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里佐伊自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她的星星是金白色的星光，带粉紫色的星点和蓝色的星尘**，**催眠气泡是蓝、紫、粉的彩虹肥皂泡**，"
      "**传送门是一圈白色的光环围着深紫色的星空**，**窃法巧手的飞弹是天蓝色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、头上、脚下、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（星星、气泡、飞弹）"
      "**朝右飞、尾巴在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zoe_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/zoe_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「烟火四射！」在里面） | 弹出一颗小星星；放过技能后的下一下是大星星，多一段魔法伤害 | `a_star` · `a_hit` · `p_star` · `p_hit` |")
    a("| 技能 1 = Q「飞星乱入！」 | 飞星直线飞向敌人，飞得越远伤害越高 | `q_star` · `q_hit` |")
    a("| 技能 2 = E「催眠气泡」 | 气泡打中英雄：困倦减速，然后昏睡；没打中就留在地上；昏睡中被飞星打中伤害加倍 | `e_bubble` · `e_hit` · "
      "`e_drowsy` · `e_zz` · `e_wake` · `e_trap` |")
    a("| 大招「折返跃迁」+ W「窃法巧手」 | 跳进传送门闪向敌人，从门口扔一颗飞星，再射 3 颗飞弹并加速，之后跳回原地 | `r_portal_in` · "
      "`r_portal_out` · `q_star` · `q_hit` · `w_missile` · `w_hit` · `w_haste` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、星点、梦雾、泡泡、光环、传送门都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金白色的星光", STAR), ("粉紫色的星点", COSMIC), ("蓝色的星尘、传送门里的夜空", DUST), ("彩虹肥皂泡", BUBBLE),
                        ("天蓝色的飞弹", SKY)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（传送门、气泡的影子、加速的光圈）是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，飞星最远飞 95000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `zoe_fx_{name}.png`：{title}\n")
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
        a(f"| `zoe_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_zoe_fx`（小的）和 `league_zoe_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_zoe.py 的 views；`r_star` 用 `q_star` 的图，`r_portal_back` 用 `r_portal_in` 的图）。")
    a(f"- 弹道图（{'、'.join(FLYING)}）断言上下对称，其余断言左右对称；`e_trap` 不跟随（地上的点，每 15 tick 重放一次），"
      "传送门不跟随（起跳点、落点）。")
    a("- 用 `pixel_1x/` 切格（import_rammus_fx 的做法）；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回"
      "（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="zoe_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "zoe_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run fx_ref_zo.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "zoe_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "zoe_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "zoe_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"zoe_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "left-right"} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
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
