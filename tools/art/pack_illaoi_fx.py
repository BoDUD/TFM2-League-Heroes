#!/usr/bin/env python3
"""Build illaoi_fx_pack.zip: step 3 of Illaoi's sprite - Codex (or Gemini) draws her effects (pack_ivern_fx.py's way).

    python tools/lol/fx_ref_illaoi.py           # League's particle textures -> C:/t/il_work/fxref (Riot's art, local only)
    python tools/art/pack_illaoi_fx.py [--no-zip] [--out DIR] [--only a_hit,p_hit --name illaoi_fx_redo_pack]

The pack (C:/t/il_work/fx/illaoi_fx_pack, zipped into --out, default dist/illaoi_packs) holds PROMPTS.md (also written to
assets/source/illaoi/PROMPTS_FX.md), design/illaoi_design.png (the idle and the tentacle at 4x, their own squares),
design/illaoi_size.png (at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter)
and refs/lol_fx_ref.png (League's own particle textures for Illaoi, grouped by the effect they inform).
The effects are the views the kit will bind (tools/kit/build_illaoi.py, the user's picks 2026-10-22: top, layout A - W /
E / R, Q in the passive): view_effects a_hit, p_hit, p_spawn and p_slam (laid under the tentacle's own frames, which come
from the pose pack), w_slam, e_break, r_slam, r_hit; view_projectiles e_grab; view_buffs p_heal, w_mark, e_spirit,
e_vessel, e_slow, r_aura.
League's colours: glowing TEAL-CYAN (the Old God's light in the cracks, the spirits, the tattoos), SEA GREEN bubbles (her
heal), GOLD (the idol's light, the W burst ring), cracked STONE and dust; the sea's white spray. Red side: the client
never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right; a projectile
is turned with its flight, so it is drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/il_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "illaoi", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "illaoi", "hd")
NAME = "illaoi_fx_pack"
PPU = 1.5

GLOW = "#FFFFFF, #C8FFF4, #6CF2E0, #20C8B8, #0E8A84, #064A4A"     # the Old God's teal light, spirits, cracks
SEA = "#F0FFE0, #A8F078, #4CC850, #1E8A3A, #0C4A22"               # sea-green bubbles, her heal
GOLD = "#FFFFFF, #FFF4B0, #FFD850, #E8A820, #9A6814"              # the idol's light, the W burst ring
STONE = "#E0D4BC, #B0A088, #807058, #50463A, #2C2620"             # cracked ground, stones, dust
GHOST = "#FFFFFF, #E0FFF8, #A8F0E4, #5CC8C0, #2A7A80"             # a torn-out spirit, pale and ghostly
FOAM = "#FFFFFF, #E4F6FF, #A8DCF0, #5CA8C8"                       # sea spray
GL = f"a glowing teal ramp ({GLOW})"
SE = f"a sea-green ramp ({SEA})"
GO = f"a gold light ramp ({GOLD})"
ST = f"a cracked stone and dust ramp ({STONE})"
GH = f"a pale ghost-teal ramp ({GHOST})"
FO = f"a sea-spray ramp ({FOAM})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
SEAGOD = ("everything is the OLD GOD OF THE SEA's magic: glowing teal spirals and cracks of light, sea-green bubbles, "
          "white sea spray, gold glints from the idol, cracked stone and dust; flat shades, crisp shapes; no smooth neon "
          "beams, no fire")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HER = "she stands in the middle, not drawn: 35 squares wide and 45 tall (with the idol)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：神像砸中，3 帧", "view_effects `league_illaoi_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "神像砸在敌人身上：一个金白色的闪光，几片青色的光屑往外弹。**左右对称**，3 帧。",
     GO + ", " + GL,
     "AN IDOL STRIKE LANDING, 3 frames, " + LR + ": 1 a gold-white flash 5 squares across; 2 a ring of short teal light "
     "shards and gold glints bursting out 11 across at mirrored places; 3 the shards further out, dimming to their "
     "darkest shades. " + SEAGOD + ".",
     row(3, 12, 12) + CENTER),
    # ---- passive: the tentacles (their bodies come from the pose pack; these lie under and on them)
    ("p_spawn", "古神先知：触手钻出地面的裂口，5 帧", "view_effects `league_illaoi_p_spawn`（大表，地上，z -1；左右对称）",
     "32 × 14",
     "触手从地里钻出来时脚下：地面裂开**发着青光的裂纹**（参考 p_tentaclespawnswipe、q_impactgroundcracks），碎石和水泡往两边弹，"
     "最后裂纹的光暗下去、留一圈碎石。**左右对称**，5 帧（触手的身体在姿势包里画，这张垫在它下面）。",
     GL + ", " + ST + ", " + SE,
     "THE GROUND CRACKING OPEN, 5 frames, " + LR + ", " + FEET + ", centred: 1 a bright teal crack-star on the ground 10 "
     "wide; 2 glowing teal cracks spreading 24 wide and 7 deep, a few stones and sea-green bubbles popping up at "
     "mirrored places; 3 the cracks 30 wide, stones at their highest (4 squares up); 4 the stones fallen, a ring of "
     "rubble 28 wide, the cracks dimming; 5 dark cracks and rubble only. " + SEAGOD + ".",
     row(5, 32, 14) + CENTER),
    ("p_slam", "古神先知：触手砸地的冲击，6 帧", "view_effects `league_illaoi_p_slam`（大表，地上，z -1；左右对称）", "40 × 20",
     "触手砸在地上那一下：地上一个**青色发光的冲击星**和一圈裂纹，**白色的海水浪花**往两边溅起，碎石和尘土飞起来（参考 q_impactground、"
     "q_impactspikes、q_smokepuffs）。**左右对称**，6 帧。",
     GL + ", " + FO + ", " + ST,
     "A TENTACLE SLAMMING THE GROUND, 6 frames, " + LR + ", " + FEET + ", centred: 1 a white-teal flash on the ground 14 "
     "wide; 2 a glowing teal crack-star 26 wide and 8 deep, two fans of white sea spray splashing up 8 squares to both "
     "sides; 3 the spray at its highest, stones and dust puffs flying out, the cracks 36 wide; 4 the spray falling in "
     "drops, the dust rolling out low; 5 a low ring of dust and wet stones 38 wide, the cracks dimming; 6 a few drops "
     "and wisps. " + SEAGOD + ".",
     row(6, 40, 20) + CENTER),
    ("p_hit", "触手打中，3 帧", "view_effects `league_illaoi_p_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "触手抽在敌人身上：一团白色浪花和青色光屑在身上溅开。**左右对称**，3 帧。",
     FO + ", " + GL,
     "A TENTACLE STRIKE ON A UNIT, 3 frames, " + LR + ": 1 a white flash 5 across; 2 a splash of white sea spray and "
     "teal light shards 13 across at mirrored places; 3 drops falling and shards dimming. " + SEAGOD + ".",
     row(3, 14, 14) + CENTER),
    ("p_heal", "触手打中英雄：俄洛伊回血，6 帧", "view_buffs `league_illaoi_p_heal`（跟随她，z 3；左右对称）", "36 × 46",
     "触手打中敌方英雄时俄洛伊回血：她身边冒起一串**绿色的水泡**往上飘（参考 p_healbubbles），脚下一圈淡绿的光。**只画在她身体外面，身体位置留空**。"
     "**左右对称**，6 帧。",
     SE + ", " + GL,
     "HEALING BUBBLES round her, 6 frames, " + LR + ", " + HER + ": a faint sea-green ring on the ground under her 30 "
     "wide and 6 tall; sea-green bubbles 1-3 squares across rising up both sides of her body at mirrored places, each "
     "with a white highlight square, a few teal motes between them; 1-2 the ring brightening and the first bubbles; 3-4 "
     "a column of bubbles up to her shoulders; 5-6 the bubbles above her head popping, the ring fading. The body's place "
     "left empty. " + SEAGOD + ".",
     row(6, 36, 46) + CENTER),
    # ---- skill: W Harsh Lesson
    ("w_slam", "严酷训诫：跳过去砸下的落点，6 帧", "view_effects `league_illaoi_w_slam`（大表，跟随目标，z -1；左右对称）",
     "44 × 22",
     "俄洛伊跳到敌人身上砸下：地上一圈**金色的光环**往外扩（参考 w_burstring），中间青色的裂纹，尘土和碎石飞起。**左右对称**，6 帧。",
     GO + ", " + GL + ", " + ST,
     "A LEAPING SMASH LANDING, 6 frames, " + LR + ", " + FEET + ", centred: 1 a gold-white flash on the ground 12 wide; "
     "2 a bright gold ring 24 wide and 8 deep, crackling, glowing teal cracks inside it; 3 the gold ring 38 wide, dust "
     "puffs and stones flying out to both sides; 4 the ring 42 wide and thinner, dust rolling; 5 a faint gold ring and a "
     "dust ring; 6 a few glints and wisps. " + SEAGOD + ".",
     row(6, 44, 22) + CENTER),
    ("w_mark", "严酷训诫：被教训的人头上的古神之眼，4 帧循环", "view_buffs `league_illaoi_w_mark`（跟随，头顶，z 3；左右对称）",
     "12 × 12",
     "被俄洛伊 W 打中的人头顶：一只**青色发光的螺旋眼**（古神的眼睛，参考 e_swirl、她神像上的螺旋眼）一闪一闪，"
     "提醒附近的触手都来抽他。**左右对称**，4 帧循环。",
     GL + ", " + GO,
     "AN ELDER GOD'S EYE floating over a head, 4 looping frames, " + LR + ": an eye-shaped sigil 10 squares wide and 7 "
     "tall drawn in glowing teal lines - a spiral for the iris in the middle, a gold-white glint in it - four small "
     "teal motes round it at mirrored places; the sigil pulses brighter in frames 2-3 and the motes turn a step. The "
     "cell's bottom sits on top of the head. " + SEAGOD + ".",
     row(4, 12, 12) + CENTER),
    # ---- skill2: E Test of Spirit
    ("e_grab", "灵魂试炼：飞出去抓灵魂的幽灵触手，4 帧循环", "view_projectiles `league_illaoi_e_grab`（弹道，z 2；上下对称）",
     "28 × 12",
     "神像里伸出一条**半透明的青色幽灵触手**飞向敌人（参考 e_tentaclegrab、e_tentacleglow），前头张开像一只手，后面一道青色的雾。"
     "**朝右飞，上下对称**，4 帧循环。",
     GH + ", " + GL,
     "A GHOSTLY TENTACLE REACHING OUT, 4 looping frames, " + TB + ": a pale glowing teal tentacle 3 squares thick and 22 "
     "long, at its front a spread grasping tip 6 squares across like an open hand with mirrored fingers above and below, "
     "spiral glow marks along it, a teal mist trail at its far end; it ripples, the wave moving a square along it each "
     "frame. " + SEAGOD + ".",
     row(4, 28, 12) + CENTER),
    ("e_spirit", "灵魂试炼：被扯出来的灵魂，6 帧循环", "view_buffs `league_illaoi_e_spirit`（跟随，z 3；左右对称）", "26 × 44",
     "被扯出灵魂的敌人：身体周围一圈**淡青色的幽灵轮廓**（像灵魂从身体里被拉出来，参考 e_spiritdissolve、e_spiritlink），往上飘着青色的游丝，"
     "胸口一个发光的小螺旋。**只画外圈和游丝，身体位置留空**。**左右对称**，6 帧循环（灵魂持续 7 秒）。",
     GH + ", " + GL,
     "A SPIRIT TORN HALF OUT, 6 looping frames, " + LR + ", " + TARGET + ": a pale ghostly teal outline 2 squares "
     "outside the body's edge all round (an upright shape 22 wide and 40 tall, drawn only as its glowing rim, the inside "
     "empty), wisps of pale teal rising from its top and shoulders, a small glowing spiral 4 squares across at chest "
     "height; the rim flickers and stretches a square up and down, the wisps drift up a step each frame. " + SEAGOD + ".",
     row(6, 26, 44) + CENTER),
    ("e_vessel", "灵魂试炼：变成躯壳的人脚下的印记，4 帧循环", "view_buffs `league_illaoi_e_vessel`（跟随，脚下，z -1；左右对称）",
     "22 × 10",
     "灵魂被打碎或被拉断后，敌人变成**躯壳**：脚下一圈暗绿的光环，中间一只青色螺旋眼的印记，几缕青色的游丝往上冒（参考 e_vesselwisps、"
     "e_timerringa）。触手会来抽他。**左右对称**，4 帧循环。",
     GL + ", " + SE,
     "A VESSEL'S BRAND " + FEET + ", 4 looping frames, " + LR + ": a dark teal ring 20 squares wide and 6 tall with a "
     "glowing teal spiral-eye sigil in the middle of the ground inside it, three thin teal wisps rising 3-4 squares from "
     "the ring at mirrored places; the sigil pulses and the wisps rise a step each frame. " + SEAGOD + ".",
     row(4, 22, 10) + CENTER),
    ("e_break", "灵魂试炼：灵魂碎掉，6 帧", "view_effects `league_illaoi_e_break`（跟随目标，z 3；左右对称）", "32 × 36",
     "灵魂被打碎（或拉得太远断掉）：淡青色的幽灵碎片和游丝从身上炸开往外飞（参考 e_beamshatter、e_spiritdissolve）。**左右对称**，6 帧。",
     GH + ", " + GL,
     "A SPIRIT SHATTERING, 6 frames, " + LR + ", centred on the chest of a standing unit: 1 a white-teal flash 8 across; "
     "2 the pale ghostly outline cracking into sharp shards, 20 across; 3 the shards flying out 30 across at mirrored "
     "places, wisps between them; 4 the shards smaller, turning to wisps; 5 drifting wisps; 6 a few motes. " + SEAGOD +
     ".",
     row(6, 32, 36) + CENTER),
    ("e_slow", "灵魂试炼：脚下的青色水雾减速，4 帧循环", "view_buffs `league_illaoi_e_slow`（跟随，脚下，z -1；左右对称）", "16 × 8",
     "被灵魂试炼减速的敌人脚下：一圈翻滚的青色水雾（参考 e_rollingmistcaustic）。**左右对称**，4 帧循环。",
     GL + ", " + FO,
     "ROLLING SEA MIST " + FEET + ", 4 looping frames, " + LR + ": a low band of teal mist 14 squares wide and 4 tall "
     "with white foam curls rolling round it, mirrored; the curls roll a step each frame. " + SEAGOD + ".",
     row(4, 16, 8) + CENTER),
    # ---- ult: Leap of Faith
    ("r_slam", "过界信仰：神像砸进地里，8 帧", "view_effects `league_illaoi_r_slam`（大表，地上，z -1；左右对称）", "64 × 30",
     "俄洛伊跳起来把神像砸进地里：一大片金白色的闪光，地上裂开一个**发着青光的大坑**，坑边一圈**青色的古神纹样**（螺旋，参考 r_craterb、"
     "r_tattoos），石板翘起来，尘土和碎石往外滚（参考 r_dirt_rock、r_dust）。**左右对称**，8 帧。",
     GO + ", " + GL + ", " + ST,
     "THE IDOL SMASHING INTO THE GROUND, 8 frames, " + LR + ", " + FEET + ", centred: 1 a huge gold-white flash 20 wide "
     "and 10 tall; 2 a crater 30 wide and 10 deep with glowing teal cracks branching out of it; 3 a ring of teal spiral "
     "glyphs round the crater 50 wide, stone slabs jutting up at its edge, dust puffs; 4 the glyph ring 60 wide, stones "
     "and dust flying out to both sides; 5 the stones falling, the dust rolling low; 6 the glyphs glowing steady, the "
     "dust settling; 7 the glyphs dimming, the crater dark; 8 dark cracks and a few motes. " + SEAGOD + ".",
     row(8, 64, 30) + CENTER),
    ("r_aura", "过界信仰：大招期间她脚下的古神纹样，6 帧循环", "view_buffs `league_illaoi_r_aura`（跟随她，脚下，z -1；左右对称）",
     "40 × 14",
     "大招的 8 秒里俄洛伊脚下：一圈**青色发光的螺旋纹样**慢慢转，几个光点往上飘（参考 r_aura_self）。**左右对称**，6 帧循环。",
     GL + ", " + GO,
     "AN ELDER GOD'S GLYPH UNDER HER " + FEET + ", 6 looping frames, " + LR + ": a ring 38 squares wide and 12 tall drawn "
     "in glowing teal lines with six spiral glyphs round it at mirrored places, a faint teal fill inside, gold motes "
     "rising 3-5 squares from the ring; the glyphs pulse in turn round the ring and the motes rise a step each frame. " +
     SEAGOD + ".",
     row(6, 40, 14) + CENTER),
    ("r_hit", "过界信仰：砸中的敌人，4 帧", "view_effects `league_illaoi_r_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被大招砸中的敌人身上：一团青色和金色的光炸开。**左右对称**，4 帧。",
     GL + ", " + GO,
     "A BURST ON A UNIT HIT, 4 frames, " + LR + ": 1 a white flash 5 across; 2 a teal burst 12 across with gold glints "
     "at mirrored places; 3 the burst 15 across breaking into shards; 4 shards dimming. " + SEAGOD + ".",
     row(4, 16, 16) + CENTER),
]
BIG_FX = ["p_spawn", "p_slam", "w_slam", "r_slam"]
FLYING = ["e_grab"]
FORWARD = []

GROUPS = [
    ("a_hit (the idol strike)", ["illaoi_base_ba_burst", "illaoi_base_ba_swipe", "illaoi_base_z_idollights",
                                 "illaoi_base_z_idolshapes"]),
    ("p_spawn p_slam p_hit (tentacles)", ["illaoi_base_p_tentaclespawnswipe", "illaoi_base_q_impactgroundcracks",
                                          "illaoi_base_q_impactground", "illaoi_base_q_impactspikes"]),
    ("p_slam p_heal", ["illaoi_base_q_smokepuffs", "illaoi_base_q_tentacleswipe", "illaoi_base_p_healbubbles",
                       "illaoi_base_p_spawnbubbles"]),
    ("w_slam w_mark (Harsh Lesson)", ["illaoi_base_w_burstring", "illaoi_base_w_jumpswipe", "illaoi_base_e_swirl",
                                      "illaoi_base_w_spark"]),
    ("e_grab e_spirit (Test of Spirit)", ["illaoi_base_e_tentaclegrab", "illaoi_base_e_tentacleglow", "illaoi_base_e_spiritdissolve",
                                          "illaoi_base_e_spiritlinka"]),
    ("e_vessel e_break e_slow", ["illaoi_base_e_vesselwisps", "illaoi_base_e_timerringa", "illaoi_base_e_beamshatter",
                                 "illaoi_base_e_rollingmistcaustic"]),
    ("r_slam (Leap of Faith)", ["illaoi_base_r_craterb", "illaoi_base_r_tattoos", "illaoi_base_r_dirt_rock",
                                "illaoi_base_r_dust"]),
    ("r_aura r_hit", ["illaoi_base_r_aura_self", "illaoi_base_r_impactflasha", "illaoi_base_r_sparks",
                      "illaoi_base_e_ring_highres"]),
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
    """Illaoi and her tentacle at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x(), design_1x("tentacle")]
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
    d.text((8, 36), f"俄洛伊 {figs[0].shape[1]}×{figs[0].shape[0]} 格，触手 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle and the tentacle at 4x, their own squares."""
    ims = [np.asarray(Image.open(lp(os.path.join(HD, f"{n}.png"))).convert("RGBA")) for n in ("idle", "tentacle")]
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
    a("# 海兽祭司 俄洛伊：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/illaoi_design.png`：左边是俄洛伊——Q 版女祭司，深棕皮肤、绿眼睛、金鼻环、"
      "黑发高发髻，金甲青布暗红腰布，肩上扛着大金色神像；右边是她召唤的触手，正面、深海绿、浅青螺旋纹）。"
      f"她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/illaoi_size.png`：俄洛伊、触手放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里俄洛伊自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**俄洛伊是海兽之神（古神）的女祭司，所有特效都是海和古神的魔法**：发光的**青色螺旋和裂纹**、**海绿色的水泡**、**白色的浪花**、"
      "神像的**金光**、裂开的**石头和尘土**，不要光滑的霓虹光束，也不要火。")
    a("> - **触手本身不在这份里**：它的身体动作在姿势包里画；这里只画它钻出地面的裂口、砸地的冲击、打中的浪花。")
    a("> - **特效要亮**：每道光、每个水泡都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、水、尘土、冲击波都没有黑描边**（碎石也不要描黑边，用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `illaoi_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/illaoi_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 抡神像砸 | `a_hit` |")
    a("| 被动「古神先知」（并入 Q 触手猛击） | 她身边会长出触手，抽她的目标；触手打中敌方英雄时她回血 | `p_spawn` · `p_slam` · `p_hit` · `p_heal`"
      "（触手本身在姿势包） |")
    a("| 技能 1 =「严酷训诫」 | 跳到目标身上砸下，按最大生命值造成伤害，附近的触手都来抽他 | `w_slam` · `w_mark` |")
    a("| 技能 2 =「灵魂试炼」 | 神像伸出幽灵触手扯出敌人的灵魂：减速、分担伤害；灵魂碎掉或拉断，敌人变成躯壳，身边长触手 | "
      "`e_grab` · `e_spirit` · `e_slow` · `e_break` · `e_vessel` |")
    a("| 大招 =「过界信仰」 | 跳起来把神像砸进地里，打中几个英雄就长几条触手，8 秒里她脚下有古神纹样、W 冷却减半 | `r_slam` · `r_hit` · `r_aura` |\n")
    a("连招：**灵魂试炼 → 严酷训诫**（扯出灵魂马上跳过去砸），**过界信仰 → 严酷训诫**（砸完接着跳），**严酷训诫 → 触手齐抽**（被 W 打中的人头上出现古神之眼，"
      "附近所有触手都抽他）。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、水、尘土、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **都是海和古神的魔法**：青色螺旋和裂纹、海绿水泡、白浪花、金光、碎石尘土；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("古神之光·青色", GLOW), ("水泡·海绿", SEA), ("神像·金光", GOLD), ("碎石尘土", STONE),
                        ("灵魂·淡青", GHOST), ("浪花·白", FOAM)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（裂口、冲击、大坑、纹样）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `illaoi_fx_{name}.png`：{title}\n")
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
        a(f"| `illaoi_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_illaoi_fx`（小的）和 `league_illaoi_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_illaoi.py 的 views）。触手的出现 / 待机 / 抽打 / 消失由姿势包的触手帧拼成（PPU 1.5，正面），"
      "p_spawn 垫在出现下面、p_slam 垫在抽打砸地那几帧下面、p_hit 是被抽中的人身上。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；e_spirit 跟随灵魂持续 7 秒（循环），r_aura 跟随她 8 秒（循环）。")
    a("- 用 `pixel_1x/` 切格（import_ivern_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="illaoi_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "illaoi_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_illaoi.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "illaoi_design.png"))
    shape = size_sheet(os.path.join(out, "design", "illaoi_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"illaoi_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
