#!/usr/bin/env python3
"""Build yorick_fx_pack.zip: step 3 of Yorick's sprite - Codex draws his effects (pack_illaoi_fx.py's way).

    python tools/lol/fx_ref_yorick.py           # League's particle textures -> C:/t/yo_work/fxref (Riot's art, local only)
    python tools/art/pack_yorick_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name yorick_fx_redo_pack]

The pack (C:/t/yo_work/fx/yorick_fx_pack, zipped into --out, default dist/yorick_packs) holds PROMPTS.md (also written to
assets/source/yorick/PROMPTS_FX.md), design/yorick_design.png (the idle and the summons, the Maiden of the Mist and a Mist
Walker, at 4x on their own squares), design/yorick_size.png (all three at game size, 4x, on the arena colour with the
ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png (League's own particle textures for Yorick and
his summons, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_yorick.py, the user's picks 2026-10-25: top, layout A - Q / E /
R, W in the passive): view_effects a_hit, q_hit, q_grave, k_spawn, k_swarm, k_bite, k_leap, w_wall, w_hit, e_hit,
e_cloud, r_spawn, r_maiden, r_claw, r_mark; view_projectiles e_mist; view_buffs e_mark, e_slow. The summons ride on the
unit they are raised on (data summons cannot walk), so the walkers and the Maiden ARE effect pictures, drawn from the
approved B-2 (hd/B-2.png) at game size: the walkers about 26 game px tall, the Maiden about his height.
League's colours: the BLACK MIST's sickly sea-green and near-black teal, his SPECTRAL CYAN (the eyes, the vial, souls),
the Maiden's VIOLET, grave DIRT and bone. Red side: the client never mirrors an effect picture, so every hit, buff,
ground and body picture is symmetric left to right (the walkers come in mirrored pairs, the Maiden faces the viewer); a
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

TMP = "C:/t/yo_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "yorick", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "yorick", "hd")
NAME = "yorick_fx_pack"
PPU = 1.75
B_SCALE = 12.1 / 10.3       # one B-2 square in A-2 squares (Codex drew B-2 on 12.1 px, A-2 on 10.3 px, one scale)

MIST = "#E8FFF4, #9CF0C8, #3CC090, #1A7A62, #0C3E38, #06201E"      # the Black Mist: sickly sea-green to near-black teal
SOUL = "#FFFFFF, #CFFFFF, #80F0FF, #2CC8E8, #1080A8"               # his spectral cyan: eyes, vial, souls, the Q glow
VIOLET = "#F4E0FF, #C89CF8, #9060E0, #5A30A8, #2C1458"             # the Maiden's violet
DIRT = "#D8C8A0, #A89070, #786048, #4C3C2C, #2A2018"               # grave dirt, stone, dust
BONE = "#FFFDF0, #E8DCB8, #B8A880"                                 # tombstone, fangs, claws
MI = f"a Black Mist ramp ({MIST})"
SO = f"a spectral cyan ramp ({SOUL})"
VI = f"a violet wraith ramp ({VIOLET})"
DI = f"a grave dirt and stone ramp ({DIRT})"
BO = f"a bone ramp ({BONE})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
ISLES = ("everything is the SHADOW ISLES' magic: the Black Mist in sickly sea-green and near-black teal, spectral cyan "
         "souls and glints, the Maiden's violet, grave dirt and pale bone; flat shades, crisp shapes; no smooth neon "
         "beams, no fire")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
WALKER = ("a MIST WALKER exactly as in design/yorick_design.png (the small right figure): a hunched ghoul, pale teal-blue "
          "skin, its whole head ONE HUGE GAPING MOUTH, purple inside, a ring of ivory fangs, long arms in purple-brown "
          "bandages ending in big ivory claws; about 26 squares tall, a 1-square near-black outline")
MAIDEN = ("the MAIDEN OF THE MIST exactly as in design/yorick_design.png (the tall middle figure) but seen from the FRONT: "
          "a hunched floating wraith woman, her body and ragged robe violet and blue-black, her head a GLOWING CYAN MIST "
          "VEIL (no face), a crown of bony claw spikes rising behind her shoulders, two thin arms with long bony claw "
          "fingers; about 48 squares tall, a 1-square near-black outline on her body (not on her glow)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：铲子砸中，3 帧", "view_effects `league_yorick_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "铲头砸在敌人身上：一个白色的闪光，几块土和青色的光屑往外弹。**左右对称**，3 帧。",
     SO + ", " + DI,
     "A SHOVEL STRIKE LANDING, 3 frames, " + LR + ": 1 a white-cyan flash 5 squares across; 2 a ring of short cyan "
     "shards and clods of dirt bursting out 11 across at mirrored places; 3 the shards further out, dimming. " + ISLES + ".",
     row(3, 12, 12) + CENTER),
    # ---- skill: Q Last Rites
    ("q_hit", "临终仪式：重铲砸中，4 帧", "view_effects `league_yorick_q_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "强化的一铲砸中：比普攻大的青色亮光炸开，几缕青色的魂火往上窜，土块飞起（参考 q1_swipe、q_impact_flash、q_flames05）。**左右对称**，4 帧。",
     SO + ", " + MI + ", " + DI,
     "A HEAVY SOUL-CHARGED SHOVEL STRIKE, 4 frames, " + LR + ": 1 a white-cyan flash 8 across; 2 a cyan burst 15 across "
     "with clods of dirt and a few cyan soul flames licking up at mirrored places; 3 the flames 6 squares tall, the burst "
     "breaking into shards; 4 thin cyan wisps and dark motes. " + ISLES + ".",
     row(4, 18, 18) + CENTER),
    ("q_grave", "临终仪式：挖出一座坟，6 帧", "view_effects `league_yorick_q_grave`（地上，z -1，不跟随；左右对称）", "18 × 20",
     "约里克这一铲挖出一座坟：地上的土往两边翻开，一块**白骨色的墓碑**从土里升起来，碑上一个青色发光的手印（参考 q_mark_crack、q_mark_hand），"
     "最后青光暗下去、留下墓碑和土堆。**左右对称**（墓碑正面朝外），6 帧。",
     BO + ", " + DI + ", " + SO,
     "A GRAVE BEING DUG, 6 frames, " + LR + ", the tombstone seen from the FRONT: 1 a crack in the ground 10 wide; 2 the "
     "dirt heaving up into a mound 14 wide, clods flying to both sides; 3 a small rounded pale-bone tombstone rising out of "
     "the mound, 8 wide and 9 tall; 4 the tombstone fully up (10 tall), a glowing cyan handprint on its face; 5 the "
     "handprint pulsing, a few cyan motes; 6 the tombstone on its dirt mound, the glow faded. " + ISLES + ".",
     row(6, 18, 20) + CENTER),
    # ---- passive: the Mist Walkers
    ("k_spawn", "唤醒：雾行者从坟里爬出来，6 帧", "view_effects `league_yorick_k_spawn`（跟随目标，z -1；左右对称）", "56 × 30",
     "坟里爬出雾行者：目标两边的地上各裂开一个口子冒出黑雾，**一对雾行者**（左右镜像，都朝着中间的目标）抓着地爬上来（参考 recall_dirtswipe、"
     "w_impactdirt）。**左右对称**，6 帧。",
     MI + ", " + DI + ", " + SO,
     "TWO MIST WALKERS CLAWING UP OUT OF THE GROUND, 6 frames, " + LR + ", the target in the middle not drawn (16 wide), "
     "one walker on each side mirrored, both turned toward the middle: " + WALKER + ". 1 two cracks in the ground 10 wide "
     "each, puffs of Black Mist; 2 claws and the tops of the mouths breaking out of the dirt; 3 the walkers out to the "
     "chest, dirt flying; 4 out to the knees; 5 crouched on the ground, mouths open; 6 ready to leap, the mist settling. "
     + ISLES + ".",
     row(6, 56, 30) + CENTER),
    ("k_swarm", "雾行者：围着目标啃咬，6 帧循环", "view_effects `league_yorick_k_swarm`（跟随目标，z -1；左右对称）", "56 × 30",
     "雾行者围着敌人咬（它们骑在目标身上走，目标死了就散）：**两边各一个雾行者**扑在目标身上，大嘴一张一合、爪子挥，脚下一层薄薄的黑雾。"
     "**左右对称**（左边那只和右边那只镜像），6 帧循环。",
     MI + ", " + BO,
     "TWO MIST WALKERS GNAWING AT A UNIT, 6 looping frames, " + LR + ", the target in the middle not drawn (16 wide, 36 "
     "tall), one walker on each side mirrored, leaping at it: " + WALKER + ". Frames 1-2 crouched, mouths closing; 3-4 "
     "lunging in, mouths wide, claws raised; 5-6 biting, then pulling back; a thin layer of Black Mist on the ground under "
     "them. " + ISLES + ".",
     row(6, 56, 30) + CENTER),
    ("k_bite", "雾行者咬中，3 帧", "view_effects `league_yorick_k_bite`（跟随目标，z 2；左右对称）", "14 × 14",
     "雾行者咬一口：一圈白骨色的尖牙印合上，迸出几点青光。**左右对称**，3 帧。",
     BO + ", " + SO,
     "A BITE, 3 frames, " + LR + ": 1 two rows of ivory fangs 12 across, open, above and below; 2 the fangs snapped "
     "shut, a white-cyan flash between them; 3 cyan motes and dark mist puffs. " + ISLES + ".",
     row(3, 14, 14) + CENTER),
    ("k_leap", "黑雾标记：雾行者扑上去，4 帧", "view_effects `league_yorick_k_leap`（跟随目标，z 2；左右对称）", "26 × 22",
     "黑雾打中英雄时，雾行者从两边**扑上去**：两道黑雾拖尾从左右两边冲向中间，中间炸开一圈爪痕。**左右对称**，4 帧。",
     MI + ", " + BO + ", " + SO,
     "WALKERS POUNCING FROM BOTH SIDES, 4 frames, " + LR + ": 1 two streaks of Black Mist with ivory claw tips coming in "
     "from the left and right edges; 2 the streaks meeting in the middle; 3 a burst of claw slashes 18 across (mirrored "
     "ivory arcs) with a cyan flash; 4 mist puffs and motes. " + ISLES + ".",
     row(4, 26, 22) + CENTER),
    # ---- passive: W Dark Procession (the cage)
    ("w_wall", "暗灵缠身：一圈灵魂墙围住，8 帧", "view_effects `league_yorick_w_wall`（大表，地上，z -1，不跟随；左右对称）", "46 × 28",
     "坟满时的唤醒：目标脚下一圈**灵魂墙**冒出来——一圈青绿色的鬼影立柱（像一排扭曲的人影）围成椭圆（参考 w_ground_aoe、w_dirt_rock、"
     "w_groundbreak），立一会儿后碎掉化成黑雾。**左右对称**，8 帧。",
     MI + ", " + SO + ", " + DI,
     "A RING OF SPIRITS RISING, 8 frames, " + LR + ", " + FEET + ", centred, a ring 42 squares wide and 14 tall: 1 a "
     "glowing sea-green crack ring on the ground; 2 dirt bursting up along it; 3 a ring of twisted ghostly pillars (like "
     "tall hunched spirits, sea-green with cyan edges) rising 6 squares; 4 the pillars at full height, 12 squares, the "
     "back half of the ring behind the middle, the front half in front of it, the middle left empty; 5-6 the wall holding, "
     "cyan glints flickering up and down it; 7 the pillars cracking and crumbling into Black Mist; 8 mist puffs and dirt. "
     + ISLES + ".",
     row(8, 46, 28) + CENTER),
    ("w_hit", "暗灵缠身：被围住的人，4 帧", "view_effects `league_yorick_w_hit`（跟随目标，z 2；左右对称）", "20 × 12",
     "被灵魂墙困住的英雄脚边：几只青绿色的鬼手从地里伸出来抓住他的脚。**左右对称**，4 帧。",
     MI + ", " + SO,
     "GHOSTLY HANDS GRABBING THE FEET, 4 frames, " + LR + ", at the feet of a standing unit (the cell's bottom on the "
     "ground): 1 two sea-green ghost hands breaking up out of the ground at mirrored places 12 apart; 2 the hands reaching "
     "up 6 squares, fingers spread; 3 the fingers closed round the ankles' places (the middle left empty); 4 the grip "
     "glowing cyan. " + ISLES + ".",
     row(4, 20, 12) + CENTER),
    # ---- skill2: E Mourning Mist
    ("e_mist", "哀伤之雾：飞出去的一团黑雾，4 帧循环", "view_projectiles `league_yorick_e_mist`（弹道，z 2；上下对称）", "16 × 10",
     "扔出去的一团**黑雾**：一团翻滚的暗青绿雾球，里面几点青光，后面拖着一缕雾尾（参考 e_mis_wind、e_soulwispsalpha2）。"
     "**朝右飞，上下对称**，4 帧循环。",
     MI + ", " + SO,
     "A GLOBULE OF BLACK MIST IN FLIGHT, 4 looping frames, " + TB + ": a churning ball of mist 7 squares across, "
     "sea-green on its rim and near-black teal inside, two cyan motes in it, a tapering mist trail 8 long behind it; the "
     "ball churns and the trail ripples a step each frame. " + ISLES + ".",
     row(4, 16, 10) + CENTER),
    ("e_cloud", "哀伤之雾：黑雾落地炸开，6 帧", "view_effects `league_yorick_e_cloud`（大表，地上，z -1，不跟随；左右对称）", "34 × 18",
     "黑雾落地：一团黑雾在地上炸开、铺成一片翻滚的雾（参考 e_puddle、e_blastshapes），几张模糊的鬼脸在雾里一闪。**左右对称**，6 帧。",
     MI + ", " + SO,
     "BLACK MIST SPLASHING DOWN, 6 frames, " + LR + ", " + FEET + ", centred: 1 a dark splash 8 wide; 2 the mist bursting "
     "out 22 wide and 8 tall, curls rolling to both sides; 3 a churning pool of mist 30 wide, two faint cyan ghost faces "
     "in it at mirrored places; 4 the pool 32 wide, curls rising 4 squares; 5 the mist thinning; 6 wisps on the ground. "
     + ISLES + ".",
     row(6, 34, 18) + CENTER),
    ("e_hit", "哀伤之雾：打中的人，3 帧", "view_effects `league_yorick_e_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被黑雾打中：一团暗青绿的雾在身上炸开，几点青光。**左右对称**，3 帧。",
     MI + ", " + SO,
     "A MIST BURST ON A UNIT, 3 frames, " + LR + ": 1 a dark teal puff 6 across with a cyan glint; 2 the mist bursting 13 "
     "across in curls at mirrored places; 3 curls thinning, motes. " + ISLES + ".",
     row(3, 14, 14) + CENTER),
    ("e_mark", "哀伤之雾：被标记的人头上，4 帧循环", "view_buffs `league_yorick_e_mark`（跟随，头顶，z 3；左右对称）", "12 × 12",
     "被黑雾标记（破甲）的敌人头顶：一个**青绿色发光的倒三角眼睛印记**一闪一闪（倒三角里一只眼睛，参考 e_mark），雾行者会冲他。**左右对称**，4 帧循环。",
     MI + ", " + SO,
     "A MOURNING MARK floating over a head, 4 looping frames, " + LR + ": a glowing sea-green sigil 9 squares "
     "wide and 8 tall: an EYE inside a downward-pointing TRIANGLE, the pupil cyan, wisps of mist curling up from it at mirrored places; it pulses brighter in "
     "frames 2-3. The cell's bottom sits on top of the head. " + ISLES + ".",
     row(4, 12, 12) + CENTER),
    ("e_slow", "哀伤之雾：脚下的黑雾减速，4 帧循环", "view_buffs `league_yorick_e_slow`（跟随，脚下，z -1；左右对称）", "16 × 8",
     "被黑雾减速的敌人脚下：一圈翻滚的黑雾缠着脚。**左右对称**，4 帧循环。",
     MI,
     "CLINGING BLACK MIST " + FEET + ", 4 looping frames, " + LR + ": a low band of mist 14 squares wide and 4 tall, "
     "sea-green curls on near-black teal, mirrored; the curls roll a step each frame. " + ISLES + ".",
     row(4, 16, 8) + CENTER),
    # ---- ult: R Eulogy of the Isles
    ("r_spawn", "海屿悼词：迷雾室女升起，7 帧", "view_effects `league_yorick_r_spawn`（大表，跟随目标，z -1；左右对称）", "50 × 58",
     "迷雾室女在敌方英雄身后升起：地上一圈紫色的雾（参考 r_gathershadow、r_spotlight），室女从雾里**正面**慢慢升起来，最后张开双臂、"
     "骨爪悬在目标上方。**目标在中间不画**（她在目标后面、比目标高）。**左右对称**，7 帧。",
     VI + ", " + SO + ", " + MI,
     "THE MAIDEN RISING behind a unit, 7 frames, " + LR + ", " + TARGET + " at the bottom middle, she is BEHIND it: " +
     MAIDEN + ". 1 a ring of violet mist on the ground 30 wide, a cyan spark in it; 2 the mist swirling up 12 squares; 3 "
     "her claw crown and glowing head rising out of it; 4 her shoulders and arms, folded; 5 her whole body hovering, the "
     "robe trailing into the mist; 6 her arms spreading wide, claws over the unit's place; 7 the same, the mist settling. "
     + ISLES + ".",
     row(7, 50, 58) + CENTER),
    ("r_maiden", "海屿悼词：室女跟着目标抓，6 帧循环", "view_effects `league_yorick_r_maiden`（大表，跟随目标，z -1；左右对称）", "50 × 58",
     "室女跟着敌方英雄（10 秒，目标死了就散）：她**正面**悬在目标身后，两只骨爪一起往下抓，袍子下摆飘着，头上的青光一闪一闪。"
     "**目标在中间不画**。**左右对称**（两只手的动作也镜像：一起举起、一起抓下），6 帧循环。",
     VI + ", " + SO,
     "THE MAIDEN HOVERING OVER A UNIT, 6 looping frames, " + LR + ", " + TARGET + " at the bottom middle, she is BEHIND "
     "it: " + MAIDEN + ". Frames 1-2 her arms raised wide, claws spread; 3-4 both claws raking down toward the unit's "
     "place; 5-6 pulling back up; her robe hem drifting and her cyan veil pulsing all the while. " + ISLES + ".",
     row(6, 50, 58) + CENTER),
    ("r_claw", "海屿悼词：室女抓中，3 帧", "view_effects `league_yorick_r_claw`（跟随目标，z 2；左右对称）", "16 × 16",
     "室女一爪抓中：两道交叉的紫色爪痕，迸出青光。**左右对称**，3 帧。",
     VI + ", " + SO,
     "A WRAITH CLAW RAKE, 3 frames, " + LR + ": 1 two mirrored violet claw arcs (three thin slashes each) crossing 14 "
     "across; 2 the slashes bright, a cyan flash where they cross; 3 the slashes fading to motes. " + ISLES + ".",
     row(3, 16, 16) + CENTER),
    ("r_mark", "海屿悼词：约里克打室女的目标加伤，3 帧", "view_effects `league_yorick_r_mark`（跟随目标，z 2；左右对称）", "14 × 14",
     "室女还在时约里克打中英雄：紫色和青色的光一起炸开（额外伤害）。**左右对称**，3 帧。",
     VI + ", " + SO,
     "A BONUS HIT, 3 frames, " + LR + ": 1 a violet-white flash 6 across; 2 a violet ring 12 across with cyan shards at "
     "mirrored places; 3 shards dimming. " + ISLES + ".",
     row(3, 14, 14) + CENTER),
]
BIG_FX = ["w_wall", "e_cloud", "r_spawn", "r_maiden"]
FLYING = ["e_mist"]
FORWARD = []

GROUPS = [
    ("a_hit q_hit (the shovel)", ["yorick_base_ba_hiteffect", "yorick_base_q1_swipe", "yorick_base_q_impact_flash",
                                  "yorick_base_q_flames05"]),
    ("q_grave (the grave)", ["yorick_base_q_mark_crack", "yorick_base_q_mark_hand", "yorick_base_q1_ground_impact_lights",
                             "yorick_base_w_dirt_rock"]),
    ("k_spawn k_swarm k_leap (walkers)", ["yorick_base_recall_dirtswipe_panner", "yorick_base_w_impactdirt",
                                          "yorick_base_joke_ghoulmelee", "yorick_base_q_soulwispsalpha"]),
    ("w_wall w_hit (the spirit wall)", ["yorick_base_w_ground_aoe", "yorick_base_w_ground_aoe_glow",
                                        "yorcik_base_w_groundbreak_mesh", "yorick_base_w_wavemult"]),
    ("e_mist e_cloud e_hit (the mist)", ["yorick_base_e_mis_wind", "yorick_base_e_puddle", "yorick_base_e_blastshapes",
                                         "yorick_base_e_soulwispsalpha2"]),
    ("e_mark e_slow", ["yorick_base_e_mark", "yorick_base_e_ring_purp_03", "yorick_base_e_softalphaball",
                       "yorick_base_e_brightspark"]),
    ("r_spawn r_maiden (the Maiden)", ["yorick_base_r_gathershadow", "yorick_base_r_spotlight",
                                       "yorick_base_r_shadowstreamers_mult", "yorick_base_r_aura_self"]),
    ("r_claw r_mark", ["yorick_base_r_sphereswipe", "yorick_base_r_wraithbeam_pulse", "yorick_base_r_flare-rainbow_purp_01",
                       "yorick_base_wraith_death_embers"]),
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
    """Yorick and his summons (the Maiden and a Walker, hd/B-2 on his scale) at game size next to the base fighter (4x),
    the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x(), design_1x("B-2", B_SCALE / PPU)]
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
    d.text((8, 36), f"约里克 {figs[0].shape[1]}×{figs[0].shape[0]} 格，室女 + 雾行者 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle and the summons (B-2) at 4x, their own squares."""
    ims = [np.asarray(Image.open(lp(os.path.join(HD, f"{n}.png"))).convert("RGBA")) for n in ("idle", "B-2")]
    W = sum(a.shape[1] * 4 + 32 for a in ims)
    H = max(a.shape[0] * 4 + 32 for a in ims)
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    x = 16
    for a in ims:
        bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (x, H - 16 - a.shape[0] * 4))
        x += a.shape[1] * 4 + 32
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 牧魂人 约里克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/yorick_design.png`：左边是约里克——Q 版掘墓人，深紫兜帽、青色发光的眼睛、"
      "灰白山羊胡、巨大的钢肩甲、破烂斗篷、长柄铲子；右边是你第 0 步画的 B-2：**迷雾室女**和**雾行者**）。"
      f"约里克在游戏里是**高清**的（每个游戏格子里 1.75×1.75 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/yorick_size.png`：约里克、室女和雾行者都缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。**雾行者约 26 格高，室女约 48 格高**（和约里克差不多）。")
    a("> - **雾行者和室女在这份里画**：游戏里召唤物不能自己走，它们是**跟着目标的特效图**（骑在被咬的人身上，目标死了就散），"
      "所以 `k_spawn`、`k_swarm`、`r_spawn`、`r_maiden` 要照 B-2 的样子把它们画出来（按游戏格子、1 格近黑描边，和约里克一个画风）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里约里克自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**约里克是暗影岛的牧魂人，所有特效都是暗影岛的魔法**：**黑雾**（病态的海绿到近黑的暗青）、**青色的魂光**（他眼睛、灯瓶的颜色）、"
      "室女的**紫色**、坟土和**白骨色**；不要光滑的霓虹光束，也不要火。")
    a("> - **特效要亮**：每道光、每团雾都有最亮一档或白色的高光，暗底上一眼能看见（黑雾的边用亮海绿勾出来）。")
    a("> - **光、雾、尘土没有黑描边**（土块也不要描黑边，用它自己最深的一档）；**只有雾行者、室女、墓碑这些“东西”有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有不飞的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——所以雾行者**左右各一只、镜像**，室女**正面**。"
      "**弹道**（`" + "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `yorick_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/yorick_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 抡铲子砸 | `a_hit` |")
    a("| 技能 1 =「临终仪式」 | 重重一铲 + 回血，打出一座坟；坟攒满 3 座，下一铲唤醒一群雾行者咬目标，同时冒出一圈灵魂墙困住附近的英雄 | "
      "`q_hit` · `q_grave` · `k_spawn` · `k_swarm` · `k_bite` · `w_wall` · `w_hit` |")
    a("| 被动「牧魂人」（并入 W 暗灵缠身） | 坟墓、雾行者、坟满时的灵魂墙 | （同上） |")
    a("| 技能 2 =「哀伤之雾」 | 扔一团黑雾：伤害、破甲、减速、标记；雾行者扑向被标记的英雄 | `e_mist` · `e_cloud` · `e_hit` · `e_mark` · "
      "`e_slow` · `k_leap` |")
    a("| 大招 =「海屿悼词」 | 迷雾室女在敌方英雄身后升起，带两只雾行者，跟着他抓 10 秒；约里克打他时加伤 | `r_spawn` · `r_maiden` · `r_claw` · "
      "`r_mark` |\n")
    a("连招：**哀伤之雾 → 雾行者扑上去 + 临终仪式马上好**，**灵魂墙困住 → 马上扔黑雾**，**海屿悼词 → 临终仪式刷新**，**坟满 → 唤醒雾行者**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（雾行者、室女、墓碑除外）。")
    a("- **都是暗影岛的魔法**：黑雾、青色魂光、紫色、坟土、白骨；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("黑雾·海绿到暗青", MIST), ("魂光·青", SOUL), ("室女·紫", VIOLET), ("坟土·石", DIRT), ("白骨", BONE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（坟土、灵魂墙、黑雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `yorick_fx_{name}.png`：{title}\n")
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
        a(f"| `yorick_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_yorick_fx`（小的）和 `league_yorick_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_yorick.py 的 views）。k_swarm 由 casted 每 60 tick 播一次（循环 1 秒）、r_maiden 同样跟随目标 10 秒。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称。")
    a("- 用 `pixel_1x/` 切格（import_ivern_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="yorick_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "yorick_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_yorick.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "yorick_design.png"))
    shape = size_sheet(os.path.join(out, "design", "yorick_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"yorick_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
