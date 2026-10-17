#!/usr/bin/env python3
"""Build braum_fx_pack.zip: step 3 of Braum's sprite - Codex draws his effects (after tools/art/pack_kassadin_fx.py).

    python tools/art/pack_braum_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name braum_fx_redo_pack]

The pack (%TEMP%/br_work/fx/braum_fx_pack, zipped into --out, default dist/braum_packs) holds PROMPTS.md (also written to
assets/source/braum/PROMPTS_FX.md), design/braum_idle.png (his dense 3/4 front design at 3x), design/braum_size.png (the
1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter beside him),
design/braum_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Braum, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/br_work/fxref, extracted from Braum.wad.client's base-skin particles by %TEMP%/br_work/fx/fx_ref_br.py).
The effects are the views the kit binds (tools/kit/build_braum.py: view_projectiles q_ice, r_wave; view_effects a_hit,
p_proc, p_extra, q_hit, e_raise, w_dash, w_land, r_slam, r_crack, r_hit; view_buffs p_mark, p_stun, q_slow, e_on,
e_ally, w_guard - w_self takes w_guard's picture, r_slow q_slow's).
League's colours: ice blue light with white cores, pale frost and snow, the shield's gold glints; light gets no outline.
Red side: the ice shard (q_ice) and the fissure's wave (r_wave) symmetric top to bottom (they turn with the cast), every
picture on a unit, on him or on the ground and every buff symmetric left to right.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "br_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "braum", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_braum")
HD_FRONT = os.path.join(ROOT, "assets", "source", "braum", "hd", "front.png")   # the approved dense design
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ICE = "#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1"     # ice light: white core to deep blue
FROST = "#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6"             # pale frost, snow, mist
GOLD = "#FFF6C8, #FFE07A, #F2B83C, #B98322"                       # the shield's gold glints (e_raise, w_guard only)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
IC = f"an ice-blue ramp ({ICE})"
FR = f"a pale frost ramp ({FROST})"
GD = f"a gold ramp used only for small glints ({GOLD})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_braum_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "盾击打中：目标身上一圈白蓝色的冲击光环一闪（参考 BA_Ring、BA_Flash），外面几根短短的冰刺往外弹（参考 BA_spikes）。**左右对称**。约 12 格，居中画。",
     f"{IC} and {FR}",
     f"a FROSTY SHIELD-BASH HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a thin ice-blue ring 10 squares "
     "across with a white rim and a white core; 3 the ring 12 squares across, 4 short ice spikes pointing outward at "
     "mirrored places; 4 a few fading frost sparks.",
     row(4, 14, 14) + "; centered in every cell."),
    ("p_mark", "被动 震荡猛击：层数标记（被叠层的英雄头顶，循环），4 帧", "view_buffs `league_braum_p_mark`（跟随，画在人物上面；左右对称）",
     "10 × 8",
     "被布隆打中的英雄头顶出现一个小小的冰蓝色拳头印记（一个圆形的冰徽，中间一个白色的拳头形状，参考 P_Cooldowntimer、P_ice_shards），一闪一闪。每多一层就多叠一个同样的标记（游戏里同一位置重叠），所以**每帧都画一个**。**左右对称**。画在格子上部（人头上方）。",
     f"{IC} and {FR}",
     f"a FROST FIST MARK over a head, 4 frames, a seamless loop, {LR}: a round ice-blue badge 8 squares across with a "
     "white fist shape in it, pulsing brighter and dimmer, two 1-square white sparkles at its sides.",
     row(4, 12, 48) + "; the badge's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty."),
    ("p_stun", "被动 第 4 层：眩晕（被眩晕的人头顶，循环），4 帧", "view_buffs `league_braum_p_stun`（跟随，画在人物上面；左右对称）",
     "14 × 8",
     "第 4 层眩晕：头顶一圈转着的小冰晶（三四颗白蓝色的小雪花沿一个扁椭圆转圈），一闪一闪。**左右对称**（每帧逐格对称：转圈靠亮暗交替表现，不要画成不对称）。画在格子上部。",
     f"{IC} and {FR}",
     f"STUN SNOWFLAKES over a head, 4 frames, a seamless loop, {LR}: 4 small white-blue snowflakes 3 squares across "
     "placed on a flat ellipse 14 squares wide and 5 tall at mirrored places, the near ones brighter, the pairs taking "
     "turns to flash white.",
     row(4, 16, 48) + "; the ellipse's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty."),
    ("p_proc", "被动 第 4 层：眩晕炸开（目标身上），5 帧", "view_effects `league_braum_p_proc`（跟随，画在人物上面；左右对称）", "20",
     "叠满 4 层的一下：目标身上冻住一下又炸开——一团冰晶包住他（大块冰蓝色冰片拼成的菱形外壳），然后碎成冰片往外飞（参考 P_Flash、P_ice_shards）。**左右对称**，中间人形位置在第 2 帧以后留空。约 20 格。",
     f"{IC} and {FR}",
     f"an ICE SHELL SHATTERING round a unit, 5 frames, {LR}, its middle EMPTY from frame 2 (a clear upright area 12 "
     "squares wide and 24 tall): 1 a white star flash 8 squares across; 2 sharp ice-blue crystal plates with white "
     "edges round the empty middle, 20 squares wide and 30 tall; 3 the plates cracking (white lines); 4 the plates "
     "flying outward as shards at mirrored places; 5 small fading shards and frost.",
     row(5, 22, 32) + "; centered across, the shell's bottom 2 squares above the cell's bottom."),
    ("p_extra", "被动：眩晕后的追加伤害（目标身上），3 帧", "view_effects `league_braum_p_extra`（跟随，画在人物上面；左右对称）", "8",
     "眩晕后几秒内布隆普攻的追加魔法伤害：目标身上一个小小的冰蓝色十字星光一闪。**左右对称**。约 8 格。",
     IC,
     f"a SMALL ICE STAR, 3 frames, {LR}: 1 a white dot 2 squares; 2 a four-point ice-blue star 8 squares across with a "
     "white core; 3 the star fading to a few sparkles.",
     row(3, 10, 10) + "; centered in every cell."),
    # ---- Q Winter's Bite
    ("q_ice", "Q 寒冬之咬：飞出去的冰（朝目标飞，循环），4 帧",
     "view_projectiles `league_braum_q_ice`（朝飞行方向转，画成朝右飞；上下对称）", "14 × 10",
     "从盾里甩出去的一大块冰：前面一颗尖尖的白蓝色冰晶（像一颗冰牙），后面拖一条冰雾尾巴和几粒冰屑（参考 Q_frost_tail、Q_End_spark）。**上下对称**。",
     f"{IC} and {FR}",
     f"an ICE CHUNK flying to the RIGHT, 4 frames, a seamless loop, {TB}: a pointed ice crystal 7 squares long and 5 tall "
     "(white core, ice-blue facets, pointing right); a frost tail 6 squares long behind it to the left, tapering, with "
     "2-3 small ice flakes (mirrored top to bottom) flickering in turn.",
     row(4, 16, 12) + "; the crystal's tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_hit", "Q 打中（目标身上），5 帧", "view_effects `league_braum_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "冰打中目标：一圈冰蓝色的霜雾炸开（白芯），几块冰片往外溅（参考 Q_hit_tar_slow）。**左右对称**。约 16 格。",
     f"{IC} and {FR}",
     f"an ICE BURST on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 an ice-blue frost puff 10 squares across with "
     "a white core; 3 the puff 16 squares across, 4 ice shards flying out at mirrored places; 4 the shards farther, the "
     "frost thinning; 5 a few fading flakes.",
     row(5, 18, 18) + "; centered in every cell."),
    ("q_slow", "Q / R 减速（被减速的人脚下，循环），4 帧", "view_buffs `league_braum_q_slow`（跟随，画在人物下面；左右对称；R 裂隙的减速也用这张）",
     "16 × 6",
     "脚下一圈结冰的地面（从斜上方看的扁椭圆），冰面上几根小冰刺冒出来又缩回去，冒一点白色冷气。**左右对称**。4 帧无缝循环。",
     f"{IC} and {FR}",
     f"FROZEN GROUND under a figure's feet, 4 frames, a seamless loop, {LR}: an ellipse 16 squares wide and 5 tall - pale "
     "ice with an ice-blue rim - and 2-4 small ice spikes at mirrored places rising one square and sinking in turn, a "
     "wisp of white frost.",
     row(4, 18, 8) + "; centered in every cell."),
    # ---- E Unbreakable
    ("e_raise", "E 坚不可摧：举盾的一刻（他身上），5 帧", "view_effects `league_braum_e_raise`（跟随，画在人物上面；左右对称）",
     "36 × 44",
     "举盾那一下：他周围一圈冰蓝色的寒气猛地一冲（像一阵冰风往外扩的大椭圆边），边上几块冰片和几点金色火花（盾上的金边反光，参考 E_shield_inchant、E_ice）。**中间人形位置留空**（不要盖住他）。**左右对称**。",
     f"{IC}, {FR} and {GD}",
     f"a BURST OF COLD round a broad figure, 5 frames, {LR}, its inside EMPTY (a clear upright area 30 squares wide and "
     "38 tall in the middle): 1 a faint ice-blue rim at the figure's sides; 2 the rim of a wide ellipse 36 squares wide "
     "and 42 tall, 2 squares thick, white inner edge; 3 ice flakes and 3-4 small gold glints flying off the rim at "
     "mirrored places; 4 the rim breaking into flakes; 5 fading frost.",
     row(5, 38, 46) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    ("e_on", "E 举盾期间（他身上，循环），4 帧", "view_buffs `league_braum_e_on`（跟随，画在人物上面；左右对称）", "36 × 44",
     "举盾的几秒里：他周围一层淡淡的冰蓝色冰壳（只画外轮廓的一圈弧线和几块六边形的冰片亮光），冰片轮流闪光。**中间人形位置留空**。**左右对称**。4 帧无缝循环。",
     f"{IC} and {FR}",
     f"an ICE SHELL round a broad figure, 4 frames, a seamless loop, {LR}, its inside EMPTY (a clear upright area 30 "
     "squares wide and 38 tall): only the rim of a wide ellipse 36 squares wide and 42 tall - a thin ice-blue arc 1-2 "
     "squares thick with a white inner edge - and 4-6 small hexagonal ice glints on it at mirrored places, twinkling in "
     "turn.",
     row(4, 38, 46) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    ("e_ally", "E 盾后的队友（队友头顶，循环），4 帧", "view_buffs `league_braum_e_ally`（跟随，画在人物上面；左右对称）", "10 × 10",
     "躲在布隆盾后面的队友受到的伤害降低：头顶一个小小的冰蓝色盾牌徽记（门板一样的方盾轮廓，中间一点白光），一闪一闪。**左右对称**。画在格子上部。",
     f"{IC} and {FR}",
     f"a SMALL SHIELD SIGIL over a head, 4 frames, a seamless loop, {LR}: an ice-blue square shield outline 8 squares "
     "wide and 9 tall with a white core in its middle, pulsing brighter and dimmer.",
     row(4, 12, 48) + "; the sigil's middle 6 squares from the TOP of the cell, centered; the rest of the cell empty."),
    # ---- W Stand Behind Me
    ("w_dash", "W 挺身而出：跳向队友（他身上，跟着他），4 帧", "view_effects `league_braum_w_dash`（跟随，画在人物下面；左右对称）",
     "30 × 12",
     "跳起来的一瞬间：他脚下一圈被踩碎的冰雪往两边飞溅（扁椭圆的雪雾，几块冰屑往上弹）。**左右对称**（不要画成往一个方向拖的尾巴：红色方不会镜像）。",
     f"{FR} and {IC}",
     f"a SNOW KICK-UP under a jumping figure's feet, 4 frames, {LR}: 1 a flat snow puff 12 squares wide and 4 tall; "
     "2 the puff 24 squares wide, ice chips flying up and outward at mirrored places; 3 the puff 30 squares wide and "
     "thin, the chips higher; 4 fading flakes.",
     row(4, 32, 14) + "; centered across, the puff's middle 3 squares above the cell's bottom."),
    ("w_land", "W 落在队友身边（队友身上），5 帧", "view_effects `league_braum_w_land`（跟随，画在人物上面；左右对称）", "26 × 18",
     "落地的一下：队友脚下一圈冰蓝色的冲击环往外扩（扁椭圆，白边），几块冰片弹起。**左右对称**，中间人形位置留空。",
     f"{IC} and {FR}",
     f"a LANDING RING on the ground round a figure, 5 frames, {LR}, the middle above the ring EMPTY (a clear upright area "
     "10 squares wide and 14 tall): 1 a white flash on the ground 6 squares wide; 2 a flat ice-blue ring 14 squares wide "
     "and 5 tall with a white rim; 3 the ring 24 x 8, ice chips flying up at mirrored places; 4 the ring breaking into "
     "flakes; 5 fading frost.",
     row(5, 28, 20) + "; centered across, the ring's middle 4 squares above the cell's bottom."),
    ("w_guard", "W 护甲魔抗加成（布隆和队友身上，循环），4 帧", "view_buffs `league_braum_w_guard`（跟随，画在人物上面；左右对称；布隆自己的 w_self 也用这张）",
     "14 × 6",
     "两人护甲魔抗提高的几秒：胸口高度一圈淡淡的冰蓝色环（扁椭圆，几块冰片亮光、一点金色火花），慢慢闪。**左右对称**，中间留空。4 帧无缝循环。",
     f"{IC}, {FR} and {GD}",
     f"a GUARD RING round a figure's chest, 4 frames, a seamless loop, {LR}: a thin flat ice-blue ring 14 squares wide and "
     "5 tall (the middle empty), 2 small ice glints and 2 tiny gold glints on it at mirrored places twinkling in turn.",
     row(4, 16, 48) + "; the ring's middle 22 squares above the cell's bottom, centered; the rest of the cell empty."),
    # ---- R Glacial Fissure
    ("r_slam", "R 冰川裂隙：砸地（他身前，不跟随），6 帧", "view_effects `league_braum_r_slam`（不跟随，画在人物下面；左右对称）",
     "48 × 22",
     "盾砸到地上的一下：地面一圈大大的冰蓝色冲击波往外炸开（扁椭圆，白边，参考 R_ground_nova、R_Frozen_ground），冰块和雪雾往上飞，地面结一层冰。**左右对称**。",
     f"{IC} and {FR}",
     f"a GROUND NOVA, 6 frames, {LR}: 1 a white flash on the ground 10 squares wide; 2 a flat ice-blue shock ring 24 "
     "squares wide and 8 tall with a white rim, frozen ground inside it; 3 the ring 44 x 14, ice chunks flying up at "
     "mirrored places; 4 the ring breaking, the chunks highest, snow mist rising; 5 the mist spreading, chunks falling; 6 "
     "fading frost on the ground.",
     row(6, 50, 26) + "; centered across, the ring's middle 6 squares above the cell's bottom."),
    ("r_wave", "R 冰川裂隙：沿直线冲出去的冰（朝施放方向，循环），4 帧",
     "view_projectiles `league_braum_r_wave`（朝飞行方向转，画成朝右跑；上下对称）", "22 × 18",
     "沿着直线往前冲的冰：一排从地里拱出来的冰刺（中间高两边低，像一道往前推的冰浪），前面最高最亮，后面的在缩回去（参考 R_flying_shards、W_Ice_shard）。**上下对称**（游戏会把它转向，往左时上下翻）。",
     f"{IC} and {FR}",
     f"a RUSH OF ICE SPIKES moving RIGHT, 4 frames, a seamless loop, {TB}: a cluster of sharp ice spikes bursting from the "
     "middle row, the front (right) ones tallest and brightest (white tips), shorter toward the back (left), spreading "
     "above and below the middle row the same; the spikes taking turns to grow and sink; frost mist trailing behind.",
     row(4, 24, 20) + "; the front spike 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_crack", "R 留下的裂隙（地上，一段一段，约 4 秒），8 帧", "view_effects `league_braum_r_crack`（不跟随，画在地上；左右对称；沿直线每 20 格放一段）",
     "24 × 10",
     "裂隙的一段：地上一道冰蓝色的裂缝（参考 I_Ground_Crack、R_Frozen_ground），从中间裂开、发亮、结霜，最后慢慢暗下去消失。游戏沿着直线每隔 20 格放一段，几段连起来就是一整条冰川裂隙。**左右对称**，扁的（从斜上方看地面）。第 4 帧会停很久（裂隙持续约 4 秒），最后两帧是消失。",
     f"{IC} and {FR}",
     f"a GLOWING ICE CRACK in the ground, 8 frames, {LR}: a flat jagged crack 22 squares wide and 7 tall seen from above "
     "at an angle (zigzag branches), white-blue glowing inside, pale frost round it; 1 a short crack 6 squares; 2 the crack "
     "14 squares; 3 the full crack, brightest; 4 the full crack steady (this frame is held for seconds); 5 the same with "
     "fresh frost; 6 the glow dimming; 7 only frost and a thin dark-blue line; 8 a few frost specks.",
     row(8, 26, 12) + "; centered in every cell."),
    ("r_hit", "R 击飞（被打中的人身上），4 帧", "view_effects `league_braum_r_hit`（跟随，画在人物上面；左右对称）", "16",
     "被冰川裂隙击飞：一团冰蓝色的冰片和雪雾从下往上溅（中心白光）。**左右对称**。约 16 格。",
     f"{IC} and {FR}",
     f"an ICE ERUPTION HIT on a unit, 4 frames, {LR}: 1 a white-blue flash 6 squares; 2 ice shards and frost bursting "
     "upward 14 squares across, a white core; 3 the shards higher at mirrored places; 4 fading flakes.",
     row(4, 18, 18) + "; centered in every cell."),
]

GROUPS = [
    ("a_hit p_*", ["Braum_Base_BA_Ring_tar", "Braum_Base_BA_spikes_tar", "Braum_Base_BA_Flash_tar", "Braum_Base_P_Flash_tar",
                   "Braum_Base_P_ice_shards", "Braum_Base_P_Cooldowntimer"]),
    ("q_*", ["Braum_Base_Q_frost_tail_mult_mis", "Braum_Base_Q_End_spark_mis", "Braum_Base_Q_hit_tar_slow",
             "Braum_Base_E_shield_ice_smoke", "Braum_Base_I_smoke_seq", "Braum_Base_W_Ice_shard_RGBA"]),
    ("e_* w_*", ["Braum_Base_E_shield_inchant_flash", "Braum_Base_E_shield_inchant_mult", "Braum_Base_E_shield_first_block_shatter",
                 "Braum_Base_E_ice_RGB", "Braum_Base_I_shield_trail", "Braum_Base_BA_solar_circle"]),
    ("r_*", ["Braum_Base_R_ground_nova", "Braum_Base_R_Frozen_ground", "Braum_Base_R_flying_shards",
             "Braum_Base_I_Ground_Crack_4x1", "Braum_base_R_smoke_mult", "Braum_Base_R_Dirt_Spatter"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 4, "a_hit：盾击打到的地方（画在目标身上）"),
         ("skill", 3, "q_ice：冰从盾里甩出去"),
         ("skill2", 2, "e_raise / e_on：举盾，围着他"),
         ("w_leap", 4, "w_land：落地"),
         ("ult", 5, "r_slam：盾砸到地上；r_wave 从这里往右冲"),
         ("idle", 1, "q_slow / p_mark：站位点")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Braum_Base_", "").replace("Braum_base_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def idle_1x():
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = idle_1x()
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    img = Image.new("RGBA", (max(W * Z, 420), (pad + max(fig.shape[0], kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fig.shape[0], kn.shape[0])
    img.alpha_composite(Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST),
                        (pad * Z, (base - fig.shape[0]) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fig.shape[1]) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.shape[1] + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"布隆 {fig.shape[1]}×{fig.shape[0]} 格（连盾），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (the imported sheet), his standing point as a cyan cross."""
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    px = sp.w // 2 + PAD
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 330), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 弗雷尔卓德之心 布隆：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/braum_idle.png`：游戏里的 3/4 正面待机，盾立在他身前画面右边）。他在游戏里是**高清**的（PPU：每个游戏格子里 2.88×2.88 个细像素，这张图是高清造型放大 3 倍），连盾 {h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/braum_size.png`：待机放大 4 倍，鞋底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/braum_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里布隆自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**冰蓝色的光（白芯）、淡淡的霜雾和雪**；E 和 W 的加成里可以有几点**盾上金边的金色反光**。")
    a("> - **特效要亮**：每道光、每块冰都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的冰壳、冲击环只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的冰 `q_ice` 和沿直线冲出去的冰刺 `r_wave` 画成朝右，**上下对称**（往左放时会上下翻）。"
      "其余所有画面（打中、身上、脚下、头顶、地上的裂隙、砸地）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `braum_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `braum_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「震荡猛击」 | 盾击；普攻和 Q 给英雄叠层，第 4 层眩晕，之后几秒普攻追加伤害 | `a_hit` · `p_mark` · `p_stun` · `p_proc` · `p_extra` |")
    a("| 技能 1 = Q「寒冬之咬」 | 从盾里甩出寒冰，打中的人减速 | `q_ice` · `q_hit` · `q_slow` |")
    a("| 技能 2 = E「坚不可摧」+ W「挺身而出」 | 举盾减伤，盾后的队友也减伤；跳到队友身边，两人加护甲魔抗 | `e_raise` · `e_on` · `e_ally` · `w_dash` · `w_land` · `w_guard` |")
    a("| 大招 = R「冰川裂隙」 | 盾砸地，冰沿直线冲出去击飞敌人，留下减速的裂隙 | `r_slam` · `r_wave` · `r_crack` · `r_hit` · `q_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冰、霜、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("冰蓝光", ICE), ("霜雾和雪", FROST), ("金色反光（只用于 E、W 的小亮点）", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "R 的直线长 80000、半宽 9000，裂隙每段减速半径 10000、沿线每 20000 一段，E 盾后队友范围 25000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `braum_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `braum_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_braum_fx`（小的）和 `league_braum_big`（e_on、r_wave、r_slam、r_crack），tag = 名字（build_braum.py 的 views；w_self 用 w_guard 的画、r_slow 用 q_slow 的画）。")
    a("- `q_ice`、`r_wave` 是飞行投射物，画面朝飞行方向转；`r_slam`、`r_crack` 不跟随；`q_slow` 脚下 buff（z -1）；`p_mark`、`p_stun`、`e_ally` 头顶（z 3）；`e_on`、`e_raise` 跟随画在人物上面，中间必须是空的；`r_crack` 第 4 帧拉长到裂隙的 4 秒。")
    a("- 用 `pixel_1x/` 切格（import_kassadin / import_gragas 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="braum_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "braum_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/br_work/fx/fx_ref_br.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 3, 0), 3, 1)).save(os.path.join(out, "design", "braum_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "braum_size.png"))
    shots_sheet(os.path.join(out, "design", "braum_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"braum_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
