#!/usr/bin/env python3
"""Build norra_fx_pack.zip: step 3 of Norra's sprite - Codex draws her effects (pack_locke_fx.py's way).

    python tools/lol/fx_ref_norra.py            # her TFT particle textures -> C:/t/nr_work/fxref (Riot's art, local only)
    python tools/art/pack_norra_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name norra_fx_redo_pack]

The pack (C:/t/nr_work/fx/norra_fx_pack, zipped into --out, default dist/norra_packs) holds PROMPTS.md (also written to
assets/source/norra/PROMPTS_FX.md), design/norra_design.png (the approved idle at 4x on its own squares, the gold ring
in her near hand), design/norra_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler
and the base fighter), refs/tft_fx_ref.png (her own TFT particle textures, grouped by the effect they inform) and
refs/video_*.jpg (frames of her cast in Riot's TFT reveal and of her ult's gold portal rings in Wild Rift; the user:
「按视频做骨架包和特效包」). The effects are the views the kit binds (tools/kit/build_norra.py, the user's picks
2026-10-26: mid, layout A 「次元门」): view_projectiles a_bolt, q_ball, q_paint (also the bounce's q2_paint); view_effects
a_hit, q_blast (also q2_blast), q_hit, e_anvil_hit, e_book_hit, e_potion, p_heal, r_warn, r_book, r_hit; view_buffs
e_guard, r_paper (Yuumi's ride picture p_yuumi is her own sheet, from hd/yuumi.png, not here).
TFT's colours: the GOLD filigree of her portal rings, the VIOLET swirl inside them, PINK-gold little stars, the TEAL
ring of the Portal trait's prop, and for the paint (TFT's "Paperfied" ground) cream PAPER with bright INK swirls.
Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to
right; the two flying projectiles point right and are symmetric top to bottom (the game turns them); the paint is a
zone's picture, turned half round on a leftward cast, so it is symmetric both ways.
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

TMP = "C:/t/nr_work"
REF = os.path.join(TMP, "fxref")
VIDEO = os.path.join(TMP, "video_refs")
DOC = os.path.join(ROOT, "assets", "source", "norra", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "norra", "hd")
NAME = "norra_fx_pack"
PPU = 2.0

GOLD = "#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410"     # the filigree of her portal rings
PORTAL = "#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E"   # the violet swirl inside a portal
PINK = "#FFE8F4, #FF9CCB, #F05A9E, #B02A6E"                       # little pink-gold stars
TEAL = "#E6FFFF, #8FF0F0, #44C8D2, #1E8C9E, #0E4E60"              # the Portal trait's teal ring
PAPER = "#FFFDF4, #F2E6CC, #D8C6A0, #A8906A"                      # cream paper (the paint, the paper look)
INK = "#F05A9E, #44C8D2, #9A62F0, #FFD95A"                        # the paint's bright inks
IRON = "#E8EEF2, #A8B4BE, #6E7A86, #3E4650, #1E2228"              # the anvil (solid: outlined)
BOOK = "#F2DCA8, #C4472E, #8A2A1C, #4E160E, #FFD95A, #C77A16"     # the giant book: pages, red-brown leather, gold corners
HEAL = "#FFFFFF, #FFF0C8, #C8F0A0, #7CD87A, #FF9CCB"              # Yuumi's heal: warm white, soft green, a pink heart
GO = f"a gold filigree ramp ({GOLD})"
PO = f"a violet portal ramp ({PORTAL})"
PI = f"a pink star ramp ({PINK})"
TE = f"a teal ring ramp ({TEAL})"
PA = f"a cream paper ramp ({PAPER})"
IN = f"bright ink colours ({INK})"
IR = f"an iron ramp ({IRON})"
BO = f"a book ramp ({BOOK})"
HE = f"a soft heal ramp ({HEAL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
TB = "pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight)"
BOTH = ("SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (it lies on the ground and the game "
        "may turn it half round)")
MAGIC = ("everything is a YORDLE PORTAL MAGE'S whimsical magic: GOLD FILIGREE portal rings with curling vines, a VIOLET "
         "SWIRL inside each portal, little pink-gold STARS and sparkles, and for the paint cream PAPER with bright ink "
         "swirls; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke")
TARGET = "the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack and passive
    ("a_bolt", "普攻：魔法弹，4 帧循环", "view_projectiles `tft_norra_a_bolt`（弹道，z 2；朝右、上下对称）", "12 × 8",
     "她手指一指飞出去的**魔法弹**：一颗金色的四角小星星，后面拖着一小条紫色的彗尾和两三粒粉色星屑（视频里普攻是一道金光；参考 starsprite、"
     "vex_comet）。**朝右飞，上下对称**，4 帧循环。",
     GO + ", " + PO + ", " + PI,
     "A STAR BOLT, 4 looping frames, " + TB + ": a bright gold four-point star 5 squares across at the right with a white "
     "core, a tapering violet comet tail 6 squares long behind it, two pink sparkle flecks in the tail; frames 1-4 the "
     "star twinkling and the tail flickering. " + MAGIC + ".",
     row(4, 12, 8) + CENTER),
    ("a_hit", "普攻：打中，3 帧", "view_effects `tft_norra_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "魔法弹打中：一圈金色的小花纹门环一闪，迸出几颗粉金色小星星（参考 basicattack_portal、starsprite）。**左右对称**，3 帧。",
     GO + ", " + PI,
     "A STAR HIT, 3 frames, " + LR + ": 1 a white-gold star flash 6 squares across; 2 a thin gold filigree ring 10 across "
     "with little curls, four small pink-gold stars popping out at mirrored places; 3 the ring fading, the stars further "
     "out and smaller. " + MAGIC + ".",
     row(3, 14, 14) + CENTER),
    ("p_heal", "最佳好友：悠米的治疗，4 帧", "view_effects `tft_norra_p_heal`（跟随被治疗的人，z 2；左右对称）", "12 × 16",
     "悠米每隔几秒给她骑着的队友回血：一颗粉色的小爱心和几颗暖白、浅绿的光点往上飘。**左右对称**，4 帧。",
     HE + ", " + PI,
     "A LITTLE HEAL, 4 frames, " + LR + ": 1 a small pink heart 3 squares across low in the middle with two warm white "
     "plus sparkles at its sides; 2 the heart rising, soft green light dots around it; 3 the heart higher and paler, the "
     "dots spreading; 4 the last dots fading. " + MAGIC + ".",
     row(4, 12, 16) + CENTER),
    # ---- skill: Portalpalooza
    ("q_ball", "次元门狂欢：抛出去的次元球，4 帧循环", "view_projectiles `tft_norra_q_ball`（抛物线弹道，z 2；朝右、上下对称）", "16 × 16",
     "抛出去的**次元球**：一个紫色的漩涡球（里面一圈圈往里转），外面套着一圈金色的花纹门环，几颗小星星绕着转（参考 mask、mask_swirl、"
     "basicattack_portal；视频里施法时她身边那团紫光）。它在空中转着飞，**上下对称**（朝右飞），4 帧循环。",
     PO + ", " + GO + ", " + PI,
     "A PORTAL BALL, 4 looping frames, " + TB + ": a round violet swirl ball 10 squares across (a spiral of lighter violet "
     "turning inward to a white-violet core) inside a thin gold filigree ring 14 across with little curls, two tiny "
     "pink-gold stars orbiting at mirrored places; frames 1-4 the spiral turning and the stars moving round. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_blast", "次元门狂欢：次元球爆开，7 帧", "view_effects `tft_norra_q_blast`（大表，落点，z 2，不跟随；左右对称）", "48 × 40",
     "次元球落地爆开：先一下紫白的闪光，紫色漩涡和金色门环往外炸开，**四周甩出一团团彩色颜料**（品红、青、紫、金黄）和几片米色纸屑，"
     "最后颜料落到地上（地上的纸画是另一张 `q_paint`）。爆炸中心在格子下部（地面），往上炸起来。**左右对称**，7 帧。",
     PO + ", " + GO + ", " + IN + ", " + PA,
     "A PORTAL BURST WITH PAINT, 7 frames, " + LR + ": the burst sits on the ground line 6 squares above the bottom. 1 a "
     "white-violet flash 10 squares across; 2 a violet swirl blast 22 across with a gold filigree ring round it; 3 the "
     "blast 34 across, blobs of bright ink (magenta, teal, violet, gold) flung out at mirrored places, cream paper scraps; "
     "4 the ink blobs 44 across and falling, the swirl breaking up; 5 the blobs splashing down near the ground line, "
     "little stars; 6 paint drops and paper scraps settling; 7 a few fading sparkles. " + MAGIC + ".",
     row(7, 48, 40) + CENTER),
    ("q_hit", "次元门狂欢：被砸中，3 帧", "view_effects `tft_norra_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被次元球的爆炸打中：身上溅了一团彩色颜料，一颗小星星。**左右对称**，3 帧。",
     IN + ", " + PI,
     "A PAINT SPLAT HIT, 3 frames, " + LR + ": 1 a small magenta-and-teal ink splat 6 squares across with a white core; 2 "
     "the splat 10 across with drops at mirrored places and a little gold star; 3 the drops falling and fading. " + MAGIC + ".",
     row(3, 14, 14) + CENTER),
    ("q_paint", "次元门狂欢：地上的纸画，6 帧循环", "view_projectiles `tft_norra_q_paint` / `tft_norra_q2_paint`（大表，地面区域，z -2；"
     "左右、上下都对称）", "64 × 22",
     "被涂色的地面（金铲铲里叫「纸化」，诺拉来自班德尔城的绘本世界）：**地上铺开一大片米色纸**，上面用彩色颜料画出卷卷的漩涡和星星（品红、青、紫、金黄），"
     "边缘是纸撕开的毛边，颜色慢慢流动、星星一闪一闪（站在上面的敌人一直掉血）。这是地上区域的图，游戏会把它转半圈，"
     "所以**左右、上下都要对称**。最大 **横 60 格、纵 20 格**。6 帧循环。",
     PA + ", " + IN + ", " + GO,
     "A PAINTED PAPER GROUND, 6 looping frames, " + BOTH + ", " + GROUND_E + ": a big ellipse of cream paper 60 squares "
     "wide and 20 tall with a torn, wavy paper edge, painted with bright ink swirls - magenta, teal, violet and gold "
     "curls and small spirals - and a few little gold stars; frames 1-6 the ink swirls slowly turning and the stars "
     "twinkling in turn. Flat colours, crisp pixel shapes. " + MAGIC + ".",
     row(6, 64, 22) + CENTER),
    # ---- skill2: Otherworld Delivery
    ("e_anvil_hit", "异界来物：铁砧从次元门掉下来，8 帧", "view_effects `tft_norra_e_anvil_hit`（大表，目标脚下，z 2，不跟随；左右对称）",
     "36 × 64",
     "目标头顶高处打开一个**金色花纹的小次元门**（横着的椭圆，里面紫色漩涡），一个**铁砧**从门里掉下来，砸在目标站的地方，"
     "砸出一圈灰尘和金色小星星（被砸的人晕一下）。铁砧正面看、左右对称，**有 1 格近黑描边**（它是个东西）；门、光、灰尘、星星没有描边。"
     "砸的地方在格子底部往上 6 格。**左右对称**，8 帧。",
     GO + ", " + PO + ", " + IR + ", " + PI,
     "AN ANVIL OUT OF A PORTAL, 8 frames, " + LR + ": 1 a small gold filigree portal (a flat ellipse 16 squares wide and 5 "
     "tall with a violet swirl inside) opening near the top of the cell; 2 an iron anvil seen from the FRONT (12 wide, 8 "
     "tall, flat top, narrow waist, wide base; grey iron with a 1-square near-black outline) coming out of the portal; 3-4 "
     "the anvil falling straight down; 5 the anvil slamming onto the ground line 6 squares above the bottom, a white "
     "flash and a ring of dust 24 wide at its foot; 6 dust puffs at both sides and little gold stars spinning above it; 7 "
     "the portal closing; 8 the anvil and the dust fading. " + MAGIC + ".",
     row(8, 36, 64) + CENTER),
    ("e_book_hit", "异界来物：巨书从次元门掉下来，8 帧", "view_effects `tft_norra_e_book_hit`（大表，目标脚下，z 2，不跟随；左右对称）",
     "40 × 64",
     "同样一个**金色次元门**在目标头顶打开，一本**合着的巨大厚书**（正面看：棕红皮面、金色包角和搭扣，像悠米的书）掉下来，"
     "砸到地上啪地**摊开**，书页和纸屑往上翻飞（被砸的人被击飞）。书有 1 格近黑描边。砸的地方在格子底部往上 6 格。**左右对称**，8 帧。",
     GO + ", " + PO + ", " + BO + ", " + PA,
     "A GIANT BOOK OUT OF A PORTAL, 8 frames, " + LR + ": 1 a small gold filigree portal (a flat ellipse 16 squares wide "
     "and 5 tall with a violet swirl inside) opening near the top of the cell; 2 a giant closed book seen from the FRONT "
     "cover (14 wide, 18 tall, red-brown leather, gold corners and a gold clasp in the middle, a 1-square near-black "
     "outline) coming out; 3-4 the book falling straight down; 5 the book slamming onto the ground line 6 squares above "
     "the bottom and bursting OPEN flat (now 30 wide and 8 tall, cream pages fanned up in the middle), a white flash; 6 "
     "pages and paper scraps flying up at both sides; 7 the portal closing, scraps falling; 8 the book and scraps fading. "
     + MAGIC + ".",
     row(8, 40, 64) + CENTER),
    ("e_potion", "异界来物：药水，6 帧", "view_effects `tft_norra_e_potion`（跟随每个被治疗的队友，z 2；左右对称）", "14 × 26",
     "次元门里掉出一瓶药水：队友头顶一个小小的金色门环里掉出**一个圆肚小药瓶**（粉色药水、软木塞，有描边），落到头上啪地碎成粉色、浅绿的光点洒下来（回血）。"
     "**左右对称**，6 帧。",
     GO + ", " + PI + ", " + HE,
     "A POTION POPS, 6 frames, " + LR + ": 1 a tiny gold filigree ring 8 squares wide near the top of the cell; 2 a little "
     "round potion bottle (4 wide, 5 tall, pink liquid, a cork, a 1-square near-black outline) dropping out of it; 3 the "
     "bottle lower, over the unit's head (the middle of the cell); 4 the bottle bursting into pink and soft green light "
     "drops and a white flash; 5 the drops raining down at both sides; 6 the last drops fading. The bottom half (the "
     "unit's body) mostly empty. " + MAGIC + ".",
     row(6, 14, 26) + CENTER),
    ("e_guard", "异界来物 / 门槛之书：次元门护盾，6 帧循环", "view_buffs `tft_norra_e_guard`（跟随有护盾的人，z 3；左右对称）", "26 × 42",
     "护盾：人身上套着一圈**金色花纹的门环**（从斜上方看的椭圆，围着腰），身体外圈一层淡紫色的光膜轮廓，几颗小星星绕着转。"
     "**身体位置留空**。**左右对称**，6 帧循环。",
     GO + ", " + PO + ", " + PI,
     "A PORTAL RING SHIELD, 6 looping frames, " + LR + ", " + TARGET + ": a thin gold filigree ring 24 squares wide and 7 "
     "tall around the unit's waist (seen slightly from above, its back half behind the unit's place), a faint violet "
     "outline like a bubble around the whole unit 22 wide and 40 tall, three tiny pink-gold stars circling; frames 1-6 "
     "the ring's curls glinting in turn and the stars moving round. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 26, 42) + CENTER),
    # ---- ult: The Book of Thresholds
    ("r_warn", "门槛之书：地上的预警圈，6 帧", "view_effects `tft_norra_r_warn`（大表，落点，地面，z -2，不跟随；左右对称）", "60 × 22",
     "大招要落下的地方：地上一圈圈**同心的金色门环**慢慢亮起来、往里转（视频里手游大招的金色同心圈；参考 basicattack_portal、ring_00_erosion）。"
     "最大 **横 54 格、纵 18 格**。**左右对称**，6 帧。",
     GO + ", " + PO,
     "A WARNING OF CONCENTRIC PORTAL RINGS, 6 frames, " + LR + ", " + GROUND_E + ": 1 a thin gold ring 20 squares wide; 2 "
     "a second, wider gold filigree ring 36 wide around it; 3 three concentric gold rings, the widest 54 wide and 18 tall, "
     "with little curls on them and a faint violet glow between them; 4-6 the rings brightening in turn from the outside "
     "in, small gold sparks rising. Flat colours, crisp pixel shapes. " + MAGIC + ".",
     row(6, 60, 22) + CENTER),
    ("r_book", "门槛之书：天上的大门和落下的书页，10 帧", "view_effects `tft_norra_r_book`（大表，落点，z 3，不跟随；左右对称）", "70 × 84",
     "大招：目标头顶高处打开**两三圈同心的巨大金色次元门**（正面略微从下往上看的椭圆，金色花纹、中间紫色漩涡，像视频里手游大招的金色圆环），"
     "**一张巨大的发光书页**（米色纸、金边，上面有卷卷的花纹）从门里**直直落下来**，一道金光柱跟着砸到地上，地面炸开一圈纸屑和金色冲击波"
     "（范围里的敌人被「纸化」眩晕）。砸的地方在格子底部往上 8 格。**左右对称**，10 帧。",
     GO + ", " + PO + ", " + PA + ", " + PI,
     "THE BOOK OF THRESHOLDS, 10 frames, " + LR + ": 1 a gold filigree ring 24 squares wide and 8 tall opening high in the "
     "cell (its middle 14 squares below the top); 2 two more concentric gold rings around it, the widest 60 wide and 20 "
     "tall, a violet swirl in the middle; 3 the rings glowing, a giant glowing PAGE (cream paper 20 wide and 26 tall with "
     "a gold border and gold curls on it, seen from the front, upright) coming out of the middle; 4-5 the page falling "
     "straight down inside a wide pillar of gold light 22 wide; 6 the page slamming onto the ground line 8 squares above "
     "the bottom, a white-gold flash 40 wide; 7 a gold shockwave ellipse 64 wide and 16 tall on the ground, paper scraps "
     "flying up at both sides; 8 scraps falling, the rings above fading; 9 the light pillar thinning; 10 the last scraps "
     "and sparkles. Frames 6-8 MUST fill 60 squares across. " + MAGIC + ".",
     row(10, 70, 84) + CENTER),
    ("r_hit", "门槛之书：被砸中，4 帧", "view_effects `tft_norra_r_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被书页砸中：一下金白的闪光，几片米色纸屑和金色小星星往外飞。**左右对称**，4 帧。",
     GO + ", " + PA + ", " + PI,
     "A PAGE HIT, 4 frames, " + LR + ": 1 a white-gold flash 8 squares across; 2 cream paper scraps and gold stars 14 "
     "across flying out at mirrored places; 3 the scraps further out, turning; 4 fading scraps. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("r_paper", "门槛之书：被「纸化」，6 帧循环", "view_buffs `tft_norra_r_paper`（跟随目标，z 3；左右对称）", "24 × 42",
     "被纸化的人（眩晕、受到的伤害变多）：身体外圈一圈**米色纸片的轮廓**，像被剪成纸人贴在一张纸上，纸边有折痕，四周几片小纸屑慢慢飘，"
     "头顶一个小小的纸折星星。**身体位置留空**。**左右对称**，6 帧循环。",
     PA + ", " + IN,
     "A PAPER-CUT LOOK, 6 looping frames, " + LR + ", " + TARGET + ": a cream paper frame around the unit 22 wide and 40 "
     "tall like the edge of a paper cut-out (a thick wavy paper border with a few fold lines, the inside left empty), "
     "four small paper scraps drifting at mirrored places and a little folded paper star with a magenta ink dot over "
     "its head; frames 1-6 the scraps drifting and turning, the star bobbing. The middle (the body) left empty. "
     + MAGIC + ".",
     row(6, 24, 42) + CENTER),
]
BIG_FX = ["q_blast", "q_paint", "e_anvil_hit", "e_book_hit", "r_warn", "r_book"]
FLYING = ["a_bolt", "q_ball"]
BOTH_FX = ["q_paint"]

GROUPS = [
    ("a_bolt a_hit (the bolt)", ["tft12_norra_base_starsprite", "tft12_vex_base_comet_flipped", "tft12_norra_base_basicattack_portal",
                                 "tft12_norra_base_em_hand_brightglow"]),
    ("q_ball q_blast (the portal ball)", ["tft12_norra_base_mask", "tft12_norra_base_mask_swirl", "tft12_norra_base_swirl04",
                                          "tft12_norra_base_splosionsphereero", "ahri_orbswirl"]),
    ("q_paint q_hit (the paint)", ["tft12_norra_base_swirltext01", "tft12_norra_base_mask_swirl", "tft12_norra_base_spell_sparkles"]),
    ("e_* r_warn e_guard (portal rings)", ["tft12_norra_base_mask_outside_noring", "tft12_norra_base_basicattack_portal",
                                           "tft12_norra_base_ring_00_erosion", "tft12_portalprop_base"]),
    ("r_book r_hit (the light)", ["base_line_2", "base_fire_trail_up", "tft12_norra_base_flame_trail_gradient",
                                  "tft12_norra_base_spell_sparkles", "tft12_norra_base_starsprite"]),
]
VIDEO_REFS = {"video_tft_cast.jpg": "tft_attack_cast_49-56s.jpg", "video_wr_ult.jpg": "wr_ult_portals.jpg"}


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
    """Norra at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"诺拉 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 诺拉与悠米：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/norra_design.png`：约德尔小法师，高高的青绿礼帽、粉框大圆眼镜、两只垂耳、"
      "蓝紫长袍红腰带，近侧手里握着一个**金色小圆环**——她的次元门）。"
      f"诺拉在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/norra_size.png`：诺拉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里诺拉自己的特效贴图（金色花纹门环、紫色漩涡、金色螺旋、小星星、青色传送门圈），"
      "按用在我们哪张特效分好了行；`refs/video_tft_cast.jpg` 是金铲铲视频里她施法（紫光）、普攻（金色光弹）的样子，"
      "`refs/video_wr_ult.jpg` 是英雄联盟手游里她大招的**金色同心次元门**。只在本地用。")
    a("> - **诺拉是班德尔城的次元门法师，特效都是童话风的魔法**：**金色花纹的门环**（带卷卷的藤蔓花纹）、门里**紫色的漩涡**、"
      "**粉金色的小星星**、Q 的**纸画颜料**（米色纸上的品红、青、紫、金黄颜料漩涡）；不要光滑的霓虹光束，也不要写实的火和烟。")
    a("> - **特效要亮**：每道光、每个门环都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、门环、颜料、星星没有黑描边**；**只有“东西”（铁砧、巨书、药瓶）有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了两个弹道和地上的纸画，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——铁砧、巨书、药瓶都**正面**看。"
      "**弹道**（`" + "`、`".join(FLYING) + "`）**朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。"
      "**地上的纸画 `q_paint` 左右、上下都要对称**（它是地面区域，游戏可能把它转半圈）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `norra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 手指一指，从金环里射出一颗金色魔法弹 | `a_bolt` · `a_hit` |")
    a("| 被动「最佳好友」 | 悠米趴在书上骑在一个队友头上（悠米的图另外做），每隔几秒给他回血、分他法强 | `p_heal` |")
    a("| 技能 1 =「次元门狂欢」 | 抛出次元球，落地爆炸、把地面涂成纸画持续掉血；上一片纸画还在时，球会再弹到附近另一个敌人那里炸一次 | `q_ball` · `q_blast` · `q_hit` · `q_paint` |")
    a("| 技能 2 =「异界来物」 | 在队友身边开门给他护盾；敌人头顶开门，轮流掉下铁砧（眩晕）/ 药水（给自己人回血）/ 巨书（击飞） | `e_guard` · `e_anvil_hit` · `e_potion` · `e_book_hit` |")
    a("| 大招 =「门槛之书」 | 敌人头顶打开同心的大次元门，巨大书页落下：伤害、眩晕、「纸化」（受到的伤害变多）；范围里的队友得到护盾 | `r_warn` · `r_book` · `r_hit` · `r_paper` · `e_guard` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、门环、颜料没有黑描边，也不要用最深的颜色给形状描一圈边**（铁砧、巨书、药瓶除外）。")
    a("- **都是童话风的次元门魔法**：金色花纹门环、紫色漩涡、粉金小星星、纸和颜料；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色花纹", GOLD), ("紫色漩涡", PORTAL), ("粉金星星", PINK), ("青色门圈", TEAL), ("米色纸", PAPER),
                        ("颜料", INK), ("铁砧", IRON), ("巨书", BOOK), ("治疗", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（预警圈、纸画、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `norra_fx_{name}.png`：{title}\n")
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
        a(f"| `norra_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_norra_fx`（小的）和 `tft_norra_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_norra.py 的 views：q2_paint → q_paint、q2_blast → q_blast）；悠米 `tft_norra_yuumi` 是 hd/yuumi.png 做的单独一张表。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；{'、'.join(BOTH_FX)} 断言两个方向都对称；其余断言左右对称。")
    a("- r_warn 在 R 的门飞行的 r_open 帧里一直显示（拉长到那么长）。")
    a("- 用 `pixel_1x/` 切格（import_locke_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="norra_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "norra_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_norra.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "norra_design.png"))
    shape = size_sheet(os.path.join(out, "design", "norra_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    for dst, src in VIDEO_REFS.items():
        if os.path.isfile(os.path.join(VIDEO, src)):
            shutil.copyfile(os.path.join(VIDEO, src), os.path.join(out, "refs", dst))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"norra_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "both" if x[0] in BOTH_FX else "left-right"}
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
