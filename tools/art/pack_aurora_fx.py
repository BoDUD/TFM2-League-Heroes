#!/usr/bin/env python3
"""Build aurora_fx_pack.zip: step 3 of Aurora's sprite - Codex draws her effects (pack_illaoi_fx.py's way).

    python tools/lol/fx_ref_aurora.py           # League's particle textures -> C:/t/au_work/fxref (Riot's art, local only)
    python tools/art/pack_aurora_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name aurora_fx_redo_pack]

The pack (C:/t/au_work/fx/aurora_fx_pack, zipped into --out, default dist/aurora_packs) holds PROMPTS.md (also written to
assets/source/aurora/PROMPTS_FX.md), design/aurora_design.png (the idle at 4x, its own squares), design/aurora_size.png
(at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Aurora, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_aurora.py, the user's picks 2026-10-23: mid, layout A - Q / E /
R, W in the passive): view_projectiles a_bolt, q_out (q_ball too), q_back, e_wave; view_effects a_hit, q_hit,
q_back_hit, p_spirit, p_heal, w_veil, e_burst, e_hit, r_shock and r_zone (big), r_hit, r_blink; view_buffs q_curse,
p_mark, w_haste, slow (e_slow, r_slow and r_slow1 share it).
League's colours: the SPIRIT REALM's icy BLUE and VIOLET light (her wand's glow, the hex, the realm), MAGENTA-PINK
accents, little BUNNY SPIRITS (blue-violet wisps with long ears), white sparkles and frost. Red side: the client never
mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right; a projectile is turned
with its flight, so it is drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/au_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "aurora", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "aurora", "hd")
NAME = "aurora_fx_pack"
PPU = 2.25

SPIRIT = "#FFFFFF, #D8F0FF, #8CC8FF, #4A86F0, #2A48C0, #18206A"   # the spirit realm's icy blue light
VIOLET = "#FFFFFF, #F0DCFF, #C49CFF, #8A5CE8, #5430A8, #2A1660"   # violet magic, the hex, the realm
PINK = "#FFFFFF, #FFD8F4, #FF94DC, #E04CB4, #8A1E70"              # magenta-pink accents, the curse
FROST = "#FFFFFF, #E8FAFF, #B4E8F8, #70B8DC"                      # white sparkles and frost
GOLD = "#FFFFFF, #FFF4B0, #FFD850, #E8A820, #9A6814"              # her wand's gold glints
HEAL = "#F4FFF0, #C8FFD8, #7CEAB0, #34B880, #146A48"              # the spirit's healing
SP = f"an icy spirit-blue ramp ({SPIRIT})"
VI = f"a violet magic ramp ({VIOLET})"
PK = f"a magenta-pink ramp ({PINK})"
FR = f"a white frost and sparkle ramp ({FROST})"
GO = f"a gold glint ramp ({GOLD})"
HE = f"a soft mint healing ramp ({HEAL})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
REALM = ("everything is SPIRIT-REALM magic of a bunny witch: icy blue and violet light, magenta-pink accents, white "
         "sparkles and frost, little glowing bunny spirits (round blobs with two long ears); flat shades, crisp shapes; "
         "no fire, no smooth neon beams")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HER = "she stands in the middle, not drawn: 24 squares wide and 46 tall (with the ears)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_bolt", "普攻：魔杖射出的灵光，4 帧循环", "view_projectiles `league_aurora_a_bolt`（弹道，z 2；上下对称）", "14 × 8",
     "魔杖点出去的一小团蓝紫色灵光：一个亮白核心的小光球，后面拖一条短短的蓝色光尾和几颗小星点。**朝右飞、上下对称**，4 帧循环。",
     SP + ", " + VI + ", " + FR,
     "A SMALL SPIRIT BOLT, 4 looping frames, " + TB + ": a white-cored round blue-violet light ball 4 squares across at "
     "the right, a short tapering icy blue trail 8 squares long behind it with two or three tiny white sparkles that "
     "move back frame to frame. " + REALM + ".",
     row(4, 14, 8) + CENTER),
    ("a_hit", "普攻：灵光打中，3 帧", "view_effects `league_aurora_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "灵光打中敌人：一个蓝白色的闪光，四周弹出几颗紫色和白色的星点。**左右对称**，3 帧。",
     SP + ", " + VI + ", " + FR,
     "A SPIRIT BOLT LANDING, 3 frames, " + LR + ": 1 a white-blue flash 5 squares across; 2 a ring of short violet and "
     "white star sparkles bursting out 11 across at mirrored places; 3 the sparkles further out, fading to their darkest "
     "shades. " + REALM + ".",
     row(3, 12, 12) + CENTER),
    # ---- skill: Q Twofold Hex
    ("q_out", "飞去来咒：飞出去的咒弹，4 帧循环", "view_projectiles `league_aurora_q_out`（弹道，z 2；上下对称；E→Q 连招的追踪咒弹也用它）",
     "22 × 12",
     "飞出去的诅咒弹（参考 q_mis、missilehead）：一个**紫色的菱形咒印**，中间一格白亮，前面尖、两边有两道弯弯的小钩，后面拖一条蓝紫色的光带和星点。"
     "**朝右飞、上下对称**，4 帧循环（咒印微微闪、光带抖动）。",
     VI + ", " + SP + ", " + PK,
     "A HEX MISSILE, 4 looping frames, " + TB + ": at the right a violet DIAMOND-SHAPED SIGIL 8 squares long with a white "
     "core square and two small curved hooks sweeping back above and below it (mirrored), a rippling blue-violet ribbon "
     "trail 12 squares long behind it with pink and white specks; the sigil flickers and the ribbon waves frame to frame. "
     + REALM + ".",
     row(4, 22, 12) + CENTER),
    ("q_back", "飞去来咒：收回来的咒弹，4 帧循环", "view_projectiles `league_aurora_q_back`（弹道，z 2；上下对称）", "24 × 12",
     "收回来的诅咒：和 q_out 同一个咒印，但**带着一团粉紫色的诅咒雾**往回飞，光带更粗、带几只小灵兔的影子。**朝右画（游戏按方向转）、上下对称**，4 帧循环。",
     PK + ", " + VI + ", " + SP,
     "A HEX RETURNING, 4 looping frames, " + TB + ": the same violet diamond sigil at the right, wrapped in a swirl of "
     "magenta-pink curse mist 10 squares across, a thicker violet-and-pink ribbon trail 14 squares long behind it with "
     "two tiny bunny-spirit silhouettes (round blobs with two long ears) in it at mirrored places. " + REALM + ".",
     row(4, 24, 12) + CENTER),
    ("q_hit", "飞去来咒：咒弹打中，4 帧", "view_effects `league_aurora_q_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "咒弹打中：一个紫色菱形咒印在敌人身上一闪张开，变成一圈紫色和蓝色的碎光往外散。**左右对称**，4 帧。",
     VI + ", " + SP + ", " + FR,
     "A HEX STRIKING, 4 frames, " + LR + ": 1 a white-cored violet diamond sigil 6 squares tall flashing; 2 the sigil "
     "opening into four violet points with blue light between; 3 a ring of violet and blue shards 15 across; 4 the "
     "shards scattered, dimming. " + REALM + ".",
     row(4, 16, 16) + CENTER),
    ("q_back_hit", "飞去来咒：诅咒被抽回时的爆开，4 帧", "view_effects `league_aurora_q_back_hit`（跟随目标，z 2；左右对称）",
     "18 × 22",
     "诅咒被抽回时打中：敌人身上一团**粉紫色的诅咒雾**猛地被扯碎，里面一只小灵兔的影子飞出来，白色星点四散。**左右对称**，4 帧。",
     PK + ", " + VI + ", " + FR,
     "A CURSE TORN OUT, 4 frames, " + LR + ": 1 a magenta-pink curse mist 10 squares across around the target's chest "
     "with a white flash; 2 the mist bursting outward, a small glowing bunny spirit (a round blob with two long ears, "
     "pale blue and violet) rising out of it in the middle; 3 the spirit higher, the mist in rags, white sparkles flying "
     "at mirrored places; 4 the rags fading. " + REALM + ".",
     row(4, 18, 22) + CENTER),
    ("q_curse", "飞去来咒：敌人身上的诅咒印，4 帧循环", "view_buffs `league_aurora_q_curse`（跟随，胸口，z 3；左右对称）", "12 × 12",
     "中了诅咒的敌人胸口：一个慢慢转的**粉紫色菱形咒印**（参考 qvulnerable），四个角上翘的小钩，一闪一闪。**左右对称**，4 帧循环。",
     PK + ", " + VI,
     "A CURSE MARK, 4 looping frames, " + LR + ": a magenta-pink and violet DIAMOND SIGIL 9 squares tall with four small "
     "hooked corners curling outward, a white core square pulsing bright and dim across the frames, two tiny sparkles "
     "orbiting at mirrored places. " + REALM + ".",
     row(4, 12, 12) + CENTER),
    # ---- passive: Spirit Abjuration
    ("p_mark", "驱灵奇术：敌人头上的驱灵层数，4 帧循环", "view_buffs `league_aurora_p_mark`（跟随，头顶，z 3；左右对称）", "12 × 8",
     "被打中的敌人头顶：一个小小的**蓝色灵光圈**（参考 passivering），圈上三颗小星点慢慢绕着转。**左右对称**，4 帧循环。",
     SP + ", " + FR,
     "A SPIRIT MARK OVER THE HEAD, 4 looping frames, " + LR + ": a flat icy blue ring 10 squares wide and 4 tall seen "
     "from above, three tiny white star sparkles riding around it (their places mirrored in every frame), the ring "
     "brightening and dimming. " + REALM + ".",
     row(4, 12, 8) + CENTER),
    ("p_spirit", "驱灵奇术：灵物被抽出来，6 帧", "view_effects `league_aurora_p_spirit`（跟随目标，z 3；左右对称）", "20 × 30",
     "第三下打中时：敌人身上冒出一只**发光的小灵兔**（参考 basespirit：蓝色身体、紫粉色的长耳朵，圆滚滚的），往上飘起来、转一圈，"
     "化成一串白色的星点。**左右对称**，6 帧。",
     SP + ", " + VI + ", " + PK + ", " + FR,
     "A SPIRIT EXORCISED, 6 frames, " + LR + ": 1 a white-blue flash on the target's chest; 2 a small glowing BUNNY SPIRIT "
     "(a round icy blue body 6 squares across, two long violet-pink ears, two white dot eyes) popping out; 3 the spirit "
     "rising above the target's head; 4 the spirit at the top of the cell, a ring of sparkles round it; 5 the spirit "
     "bursting into white star sparkles; 6 the sparkles fading. " + TARGET + ". " + REALM + ".",
     row(6, 20, 30) + CENTER),
    ("p_heal", "驱灵奇术：灵物回到她身边回血，6 帧", "view_effects `league_aurora_p_heal`（跟随她，z 3；左右对称）", "28 × 48",
     "灵物飞回她身上：两只小灵兔绕着她转一圈，留下薄荷绿和蓝色的光点往上升，脚下一个淡淡的光圈。**只画外圈，身体位置留空**，**左右对称**，6 帧。",
     HE + ", " + SP + ", " + FR,
     "A HEALING SPIRIT, 6 frames, " + LR + ": two small glowing bunny spirits (icy blue bodies, long violet ears) circling "
     "her at mirrored places - from her feet in frame 1 up past her waist to her head in frame 4, dissolving in 5-6 - "
     "leaving soft mint and blue plus-shaped sparkles that rise and fade; a faint mint ring on the ground under her in "
     "frames 1-3. " + HER + ". " + REALM + ".",
     row(6, 28, 48) + CENTER),
    # ---- passive: Across the Veil (W, folded in)
    ("w_veil", "灵纱洞开：后跳隐身的一阵灵雾，5 帧", "view_effects `league_aurora_w_veil`（在她起跳的地方，不跟随，z 3；左右对称）",
     "30 × 40",
     "她往后跳进灵界的一瞬间：原地一团**蓝紫色的灵雾**炸开，里面一圈垂下来的光帘（参考 w_rays），几片白色的霜花飘散。**左右对称**，5 帧。",
     VI + ", " + SP + ", " + FR,
     "A VEIL OPENING, 5 frames, " + LR + ": 1 a white-blue flash at her waist height; 2 a puff of violet and blue spirit "
     "mist 20 squares across with a curtain of thin vertical light rays falling through it; 3 the mist widest, 28 across, "
     "the rays brightest; 4 the mist thinning into wisps, white frost flakes drifting out at mirrored places; 5 a few "
     "wisps and flakes fading. " + HER + ". " + REALM + ".",
     row(5, 30, 40) + CENTER),
    ("w_haste", "灵纱洞开：加速时脚下的灵光，4 帧循环", "view_buffs `league_aurora_w_haste`（跟随她，脚下，z -1；左右对称）",
     "20 × 8",
     "隐身加速时她脚下：一圈淡蓝色的光，两边各有几道往后飘的小光条和霜点。**左右对称**，4 帧循环。",
     SP + ", " + FR,
     "A HASTE GLOW, 4 looping frames, " + LR + ": " + FEET + ", a faint icy blue ellipse 16 squares wide, short "
     "streaks of light and frost specks lifting off both of its ends (mirrored), flickering frame to frame. " + REALM + ".",
     row(4, 20, 8) + CENTER),
    # ---- skill2: E The Weirding
    ("e_wave", "怪奇喷涌：往前冲出去的灵魂冲击，4 帧循环", "view_projectiles `league_aurora_e_wave`（弹道，z 2；上下对称）", "30 × 22",
     "往前冲出去的一道**蓝紫色灵魂冲击**（参考 windblast、blastring）：前面一道弯弯的弧形光墙（凸向右），里面翻滚着灵雾和几只小灵兔的影子，"
     "后面拖着碎光。**朝右飞、上下对称**，4 帧循环。",
     VI + ", " + SP + ", " + FR,
     "A SPIRIT BLAST WAVE, 4 looping frames, " + TB + ": at the right a curved crescent wall of icy blue and violet light "
     "20 squares tall bulging to the right, 4 squares thick with a white leading edge; behind it churning violet spirit "
     "mist with two tiny bunny-spirit silhouettes at mirrored places and broken light trailing to the left; the wall "
     "ripples frame to frame. " + REALM + ".",
     row(4, 30, 22) + CENTER),
    ("e_burst", "怪奇喷涌：她身前张开的界域之窗，5 帧", "view_effects `league_aurora_e_burst`（在她身上，不跟随，z 3；左右对称）",
     "30 × 30",
     "她推出冲击的一瞬间：身前张开一个**圆形的界域之窗**（参考 r_ring：一圈带花纹钩的紫蓝色光环），从小到大张开再碎掉。"
     "**左右对称**（游戏不会翻转这张图，所以画成正对着看的圆窗），5 帧。",
     VI + ", " + SP + ", " + FR,
     "A REALM WINDOW OPENING, 5 frames, " + LR + ": a round ornate RING of violet and icy blue light seen face-on, with "
     "small curling hooks at four mirrored places on its rim, centred on her chest: 1 a 6-square ring with a white flash; "
     "2 the ring 16 across, its hooks unfurling; 3 the ring 26 across at its brightest, a violet glow inside; 4 the ring "
     "cracking into arcs; 5 the arcs scattering as sparkles. " + HER + ". " + REALM + ".",
     row(5, 30, 30) + CENTER),
    ("e_hit", "怪奇喷涌：打中，4 帧", "view_effects `league_aurora_e_hit`（跟随目标，z 2；左右对称）", "16 × 20",
     "冲击打中敌人：一阵蓝紫色的灵雾裹住他，几颗白色霜花溅开。**左右对称**，4 帧。",
     VI + ", " + SP + ", " + FR,
     "A BLAST STRIKING, 4 frames, " + LR + ": 1 a white flash at the target's chest; 2 a gust of violet and blue spirit "
     "mist wrapping round it 14 across; 3 frost flakes splashing out at mirrored places; 4 the mist thinning away. "
     + TARGET + ". " + REALM + ".",
     row(4, 16, 20) + CENTER),
    ("slow", "减速：脚下的霜雾，4 帧循环（E 和 R 的减速共用）", "view_buffs `league_aurora_e_slow` / `r_slow` / `r_slow1`（tag `slow`，跟随，脚下，z -1；左右对称）",
     "16 × 8",
     "被减速的人脚下：一圈缠着脚的**淡紫色霜雾**，几粒冰晶。**左右对称**，4 帧循环。",
     VI + ", " + FR,
     "A SLOWING FROST MIST, 4 looping frames, " + LR + ": " + FEET + ", a pale violet mist 14 squares wide coiling round "
     "the feet with a few white ice crystals glinting at mirrored places, drifting frame to frame. " + REALM + ".",
     row(4, 16, 8) + CENTER),
    # ---- ult: R Between Worlds
    ("r_shock", "双界合一：落地的冲击波，6 帧", "view_effects `league_aurora_r_shock`（大表，在她落地的地方，地上，z -1；左右对称）",
     "60 × 26",
     "她落地放出的冲击波（参考 leadingedge_ring、icecrack）：脚下一圈**蓝紫色的光环**飞快往外扩，地上裂开发光的冰裂纹，白色霜花往外溅。"
     "**地上的椭圆、左右对称**，6 帧。",
     SP + ", " + VI + ", " + FR,
     "A LANDING SHOCKWAVE, 6 frames, " + LR + ": " + FEET + ": 1 a white-blue flash 10 across at the centre; 2 a bright "
     "icy blue ring 24 wide racing out, glowing ice cracks spreading from the centre; 3 the ring 40 wide, violet behind "
     "its white edge; 4 the ring 54 wide, frost flakes thrown up along it; 5 the ring at the cell's edge, thin, the "
     "cracks dimming; 6 fading cracks and flakes only. " + REALM + ".",
     row(6, 60, 26) + CENTER),
    ("r_zone", "双界合一：两界交汇的领域，8 帧循环", "view_effects `league_aurora_r_zone`（大表，地上，z -1，不跟随；左右对称；放 3.5 秒）",
     "80 × 34",
     "地上张开的领域（参考 spiritwall、r_ring、ultcenter）：一个很大的**蓝紫色椭圆界域**，边缘是一圈垂直往上冒的**灵墙光帘**（像一圈矮矮的发光栅栏），"
     "里面地上淡淡的紫色雾和花纹，几只小灵兔在边缘慢慢绕。**地上的椭圆、左右对称**，8 帧循环（前 2 帧张开，后面循环）。",
     VI + ", " + SP + ", " + PK + ", " + FR,
     "THE REALM BETWEEN WORLDS, 8 looping frames, " + LR + ": " + FEET + ", a big violet and icy blue ellipse 76 squares "
     "wide: its rim a ring of short vertical SPIRIT-WALL light curtains rising 6-8 squares (like a low glowing fence), "
     "inside it a faint violet mist with a thin ornate circle pattern on the ground, three small bunny spirits drifting "
     "slowly round the rim at mirrored places; frames 1-2 the realm opening from the centre, 3-8 the curtains rippling "
     "and the spirits moving on. " + REALM + ".",
     row(8, 80, 34) + CENTER),
    ("r_hit", "双界合一：冲击波打中，4 帧", "view_effects `league_aurora_r_hit`（跟随目标，z 2；左右对称）", "16 × 20",
     "冲击波打中敌人：一道蓝白色的竖向光一闪，周围冰晶炸开。**左右对称**，4 帧。",
     SP + ", " + FR + ", " + VI,
     "A SHOCKWAVE STRIKING, 4 frames, " + LR + ": 1 a tall white-blue flash 4 squares wide through the target; 2 ice "
     "crystals and violet sparks bursting out 15 across; 3 the crystals further out; 4 fading. " + TARGET + ". "
     + REALM + ".",
     row(4, 16, 20) + CENTER),
    ("r_blink", "双界合一：领域里的传送，5 帧", "view_effects `league_aurora_r_blink`（在她传送到的敌人身边，z 3；左右对称）",
     "24 × 44",
     "她穿过领域传送过去的一闪：一个竖立的**椭圆形的门**（蓝紫色光边，中间白亮）一下张开又合上，周围飘出几颗星点和一只小灵兔。**左右对称**，5 帧。",
     VI + ", " + SP + ", " + FR,
     "A STEP BETWEEN WORLDS, 5 frames, " + LR + ": a tall upright oval PORTAL with a violet and icy blue rim and a white "
     "core: 1 a thin vertical white line 30 squares tall; 2 the portal opening 12 wide; 3 the portal widest, 18 wide, "
     "a small bunny spirit and sparkles spilling out at its sides (mirrored); 4 the portal closing to a line; 5 sparkles "
     "only. " + HER + ". " + REALM + ".",
     row(5, 24, 44) + CENTER),
]
BIG_FX = ["r_shock", "r_zone"]
FLYING = ["a_bolt", "q_out", "q_back", "e_wave"]
FORWARD = []

GROUPS = [
    ("a_bolt a_hit (the spirit bolt)", ["aurora_base_ba_trail2", "aurora_base_ba_speed_flash", "aurora_base_mis_sparkles",
                                        "aurora_specks"]),
    ("q_out q_back (Twofold Hex)", ["aurora_base_q_mis", "aurora_missilehead", "aurora_base_q_trail02",
                                    "aurora_base_q_glowspecks"]),
    ("q_hit q_back_hit q_curse", ["aurora_qvulnerable", "aurora_base_q_lightbeam", "aurora_base_q_smoke_erode",
                                  "aurora_base_q_flicker_04"]),
    ("p_mark p_spirit p_heal (Spirit Abjuration)", ["aurora_passivering01", "auroraspirits_basespirit1",
                                                     "aurora_base_spirits_2x2", "auroraspirits_basespirit2"]),
    ("w_veil w_haste (Across the Veil)", ["aurora_w_rays_mult", "aurora_base_p_tar_wispmult", "aurora_base_p_groundlight_01",
                                          "aurora_base_r_stardust"]),
    ("e_wave e_burst e_hit (The Weirding)", ["aurora_base_mult_windblast", "aurora_base_blastring", "aurora_base_e_decal01",
                                             "aurora_base_r_smoke_erode"]),
    ("r_shock r_hit (Between Worlds)", ["aurora_base_r_leadingedge_ring", "aurora_base_r_icecrack_01",
                                        "aurora_r_enhanced_pulsewave", "aurora_base_vgu_p_iceshards"]),
    ("r_zone r_blink slow", ["aurora_base_r_spiritwall", "aurora_r_ring", "aurora_ultcenter", "aurora_base_keyhole"]),
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
    """Aurora at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"阿萝拉 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 双界灵兔 阿萝拉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/aurora_design.png`：Q 版兔子女巫，铜红卷发、圆金框眼镜、紫蓝眼睛、"
      "青绿宽檐女巫帽和两只长兔耳朵、米白长外套和浅蓝毛边披肩、橙色兔尾巴，肩上扛着一根细长的魔杖）。"
      f"她在游戏里是**高清**的（每个游戏格子里 2.25×2.25 个细像素），{h} 格高、{w} 格宽（高×宽，连耳朵）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/aurora_size.png`：阿萝拉放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿萝拉自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**阿萝拉是穿行于两个世界的兔子女巫，所有特效都是灵界的魔法**：冰蓝和紫色的光、粉紫色的点缀、白色的星点和霜花，"
      "还有**发光的小灵兔**（圆滚滚的蓝色身体、两只紫粉色长耳朵、两个白点眼睛）；不要火，也不要光滑的霓虹光束。")
    a("> - **特效要亮**：每道光、每只小灵兔都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、雾、冲击波、光环都没有黑描边**（小灵兔也不要描黑边，用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aurora_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/aurora_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 魔杖点出一团灵光 | `a_bolt` · `a_hit` |")
    a("| 被动「驱灵奇术」 | 打中英雄叠驱灵层，第三下抽出灵物：额外伤害，灵物飞回她身上回血加速 | `p_mark` · `p_spirit` · `p_heal` |")
    a("| 被动里的「灵纱洞开」（W） | 残血又被贴身时往后一跳进入灵界：隐身、加速 | `w_veil` · `w_haste` |")
    a("| 技能 1 =「飞去来咒」 | 咒弹穿过敌人飞出去、留下诅咒，停一下再把诅咒抽回来，回程再打一次 | `q_out` · `q_hit` · `q_curse` · `q_back` · `q_back_hit` |")
    a("| 技能 2 =「怪奇喷涌」 | 身前打开界域之窗，往前喷出一道灵魂冲击：伤害、减速，然后她往后一跳 | `e_burst` · `e_wave` · `e_hit` · `slow` |")
    a("| 大招 =「双界合一」 | 跳到敌人身上落地放冲击波，地上张开两界交汇的领域减速；目标跑开时她穿过领域传送过去 | `r_shock` · `r_hit` · `r_zone` · `r_blink` · `slow` |\n")
    a("连招：**怪奇喷涌 → 飞去来咒**（冲击打中英雄马上补咒弹），**双界合一 → 怪奇喷涌**（落地马上喷），**飞去来咒去回两次都叠驱灵层**，"
      "**领域里传送追击**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **都是灵界的魔法**：冰蓝、紫色、粉紫、白色星点和霜花、小灵兔；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("灵界·冰蓝", SPIRIT), ("魔法·紫", VIOLET), ("诅咒·粉紫", PINK), ("星点霜花·白", FROST),
                        ("魔杖·金光", GOLD), ("回血·薄荷绿", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（冲击波、领域、脚下的光和雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `aurora_fx_{name}.png`：{title}\n")
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
        a(f"| `aurora_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_aurora_fx`（小的）和 `league_aurora_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_aurora.py 的 views；q_ball 用 q_out 的 tag，三个减速用 `slow`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；r_zone 放在地上 3.5 秒（循环），q_curse 跟随 70 帧左右，p_mark 4 秒。")
    a("- 用 `pixel_1x/` 切格（import_illaoi_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="aurora_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "aurora_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_aurora.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "aurora_design.png"))
    shape = size_sheet(os.path.join(out, "design", "aurora_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"aurora_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
