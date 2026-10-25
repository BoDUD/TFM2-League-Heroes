#!/usr/bin/env python3
"""Build trundle_fx_pack.zip: step 3 of Trundle's sprite - Codex draws his effects (pack_yorick_fx.py's way).

    python tools/lol/fx_ref_trundle.py          # League's particle textures -> C:/t/tr_work/fxref (Riot's art, local only)
    python tools/art/pack_trundle_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name trundle_fx_redo_pack]

The pack (C:/t/tr_work/fx/trundle_fx_pack, zipped into --out, default dist/trundle_packs) holds PROMPTS.md (also written
to assets/source/trundle/PROMPTS_FX.md), design/trundle_design.png (the approved idle at 4x on its own squares),
design/trundle_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/lol_fx_ref.png (League's own particle textures for Trundle, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_trundle.py, the user's picks 2026-10-25: jungle, layout A - Q /
E / R, W in the passive): view_effects a_hit, p_heal, q_hit, w_hop, w_domain, e_pillar, e_hit, r_hit, r_tick, r_chain;
view_buffs w_aura (the domain under him: w_on, the add-on's w_in), slow (q_slow, e_slow), q_buff (q_ad, the add-on's
q_take), q_sap (q_sap, the add-on's q_lose), r_sap (r_sap, the add-on's r_drain). No projectiles.
The pillar stands e_t ticks (4 s) from ONE ViewEffect: its rise, a standing frame the import holds, its crumble.
League's colours: his ICE (pale blue to deep ice blue, white facets), FROST dust and snow, the troll's RAGE red for the
strength he steals, the DRAIN's cold violet-blue for Subjugate, a pale troll-green for King's Tribute. Red side: the
client never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right.
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

TMP = "C:/t/tr_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "trundle", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "trundle", "hd")
NAME = "trundle_fx_pack"
PPU = 2.0

ICE = "#FFFFFF, #D8F8FF, #9EE6FF, #52BFF0, #2A80C8, #164C8C"    # his ice: white facets to deep ice blue
FROST = "#FFFFFF, #E4F4FA, #B8D8E8, #7EA8C4"                     # frost dust, snow, cold breath
RAGE = "#FFE0C8, #FF9A6A, #F0485A, #B81E3C, #6E0E26"             # the strength he steals: a troll's red rage
DRAIN = "#F0ECFF, #B8B0FF, #7A70E8, #4A3CB0, #261C68"            # Subjugate's cold violet-blue drain
HEAL = "#F0FFE8, #B8F0A8, #6CD080, #2E8C56"                      # King's Tribute: a pale troll-green heal
IC = f"an ice ramp ({ICE})"
FR = f"a frost and snow ramp ({FROST})"
RA = f"a red rage ramp ({RAGE})"
DR = f"a cold violet-blue drain ramp ({DRAIN})"
HE = f"a pale green heal ramp ({HEAL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
FREL = ("everything is the FRELJORD'S ICE and a TROLL KING'S brute strength: faceted pale-blue ice with white facets and "
        "deep-blue shade, frost dust and snow, red for the strength he steals, a cold violet-blue for Subjugate's drain; "
        "flat shades, crisp angular shapes; no smooth neon beams, no fire")
TARGET = "the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = "Trundle stands in the middle, not drawn: about 52 squares wide (with his club) and 43 tall"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：冰棒砸中，3 帧", "view_effects `league_trundle_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "冰狼牙棒砸在敌人身上：一个白色的闪光，一圈碎冰碴往外崩（参考 common_hiteffect、weapon_trail）。**左右对称**，3 帧。",
     IC + ", " + FR,
     "AN ICE CLUB STRIKE LANDING, 3 frames, " + LR + ": 1 a white-blue flash 6 squares across; 2 a ring of angular ice "
     "shards bursting out 12 across at mirrored places; 3 the shards further out, dimming into frost dust. " + FREL + ".",
     row(3, 14, 14) + CENTER),
    # ---- passive: King's Tribute
    ("p_heal", "国王的贡品：附近有人死、回血，5 帧", "view_effects `league_trundle_p_heal`（跟随特朗德尔，z 2；左右对称）", "40 × 44",
     "附近的敌人倒下，特朗德尔吸走一点生命：几缕淡绿色的光从脚下绕着他升起来，头顶几点亮光（参考 r_heal_trail）。光只画在他身体外圈和头顶，"
     "**身体位置留空**。**左右对称**，5 帧。",
     HE + ", " + FR,
     "A HEALING TRIBUTE ON A BIG TROLL, 5 frames, " + LR + ", " + HIM + ": 1 a few pale green motes on the ground at his "
     "feet, at both sides; 2 two thin green wisps curling up both sides of him; 3 the wisps at his shoulders, small plus "
     "sparkles; 4 a ring of green and white sparkles above his head; 5 the last motes fading. The middle (his body) left "
     "empty. " + FREL + ".",
     row(5, 40, 44) + CENTER),
    # ---- skill: Q Chomp
    ("q_hit", "利齿撕咬：咬中，4 帧", "view_effects `league_trundle_q_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "特朗德尔一口咬下去：上下两排**米白的大獠牙**咬合（参考 q_teeth、q_bite_marks），中间一下白光，迸出冰碴和一点红色（他吸走对方的力气）。"
     "**左右对称**，4 帧。",
     IC + ", " + RA + ", " + FR,
     "A TROLL'S BITE, 4 frames, " + LR + ": 1 two rows of big cream-white troll teeth 14 across, wide open above and "
     "below; 2 the jaws snapped shut with a white-blue flash between them; 3 a burst of ice shards and a few red sparks "
     "flying out at mirrored places, two faint red bite marks; 4 frost dust and dimming red motes. " + FREL + ".",
     row(4, 18, 18) + CENTER),
    ("q_buff", "利齿撕咬：特朗德尔变强，4 帧循环", "view_buffs `league_trundle_q_ad`（跟随特朗德尔，头顶，z 3；左右对称）", "14 × 10",
     "咬到人以后特朗德尔攻击力变高（4 秒）：头顶一个小小的**红色獠牙标记**，往上冒几点红光，一闪一闪。**左右对称**，4 帧循环。",
     RA,
     "A SMALL STRENGTH MARK OVER HIS HEAD, 4 looping frames, " + LR + ": two small upward red troll tusks side by side, 8 "
     "squares across, with a bright core; frames 1-4 the tusks pulsing brighter and dimmer and a few red motes rising "
     "from them. " + FREL + ".",
     row(4, 14, 10) + CENTER),
    ("q_sap", "利齿撕咬：被咬的人变弱，4 帧循环", "view_buffs `league_trundle_q_sap`（跟随目标，头顶，z 3；左右对称）", "12 × 10",
     "被咬的人攻击力变低：头顶一个**裂开的暗红獠牙**，往下滴冰蓝色的碎屑。**左右对称**，4 帧循环。",
     RA + ", " + IC,
     "A WEAKENED MARK OVER THE HEAD, 4 looping frames, " + LR + ": one dull dark-red tusk 6 squares tall with a crack down "
     "it, pointing down; frames 1-4 small ice-blue flakes dripping down from it and fading. " + FREL + ".",
     row(4, 12, 10) + CENTER),
    ("slow", "减速：脚下一圈寒霜，4 帧循环", "view_buffs `league_trundle_q_slow` / `league_trundle_e_slow`（跟随，脚下，z -1；左右对称）",
     "16 × 8",
     "被冻慢了：脚下一圈薄薄的白霜和冰晶，几点雪花往上飘。**左右对称**，4 帧循环。",
     FR + ", " + IC,
     "A FROST SLOW AT THE FEET, 4 looping frames, " + LR + ", " + FEET + ": a thin ellipse of white frost 14 wide with "
     "small ice crystals on it; frames 1-4 the crystals glinting in turn and a few snowflakes drifting up. " + FREL + ".",
     row(4, 16, 8) + CENTER),
    # ---- passive: W Frozen Domain
    ("w_hop", "冰封领域：跳起落地的寒霜冲击，4 帧", "view_effects `league_trundle_w_hop`（地上，z -1，不跟随；左右对称）", "36 × 14",
     "特朗德尔跳起来落地：脚下一圈白色的寒霜冲击波往外推开，带起雪尘（参考 w_shockwave_scroll、w_nova_snow_edge）。**左右对称**，4 帧。",
     FR + ", " + IC,
     "A FROST SHOCKWAVE ON LANDING, 4 frames, " + LR + ", " + FEET + ": 1 a white-blue flash ellipse 10 wide; 2 a ring of "
     "frost and snow dust 22 wide pushing out; 3 the ring 32 wide, breaking into puffs of snow; 4 the last snow puffs "
     "fading at both ends. " + FREL + ".",
     row(4, 36, 14) + CENTER),
    ("w_domain", "冰封领域：地面冻起来，8 帧", "view_effects `league_trundle_w_domain`（大表，地上，z -1，不跟随；左右对称）", "64 × 24",
     "他的领地：从他脚下往外**冻出一大片冰面**——蓝白的冰往四周铺开，冰面上有裂纹，边上冒出一圈小冰刺（参考 w_ground、w_ground_cracks、"
     "w_speedbuff_ground_glow），最后一帧是铺满的冰面（之后由脚下的 w_aura 接着循环）。**左右对称**，8 帧。",
     IC + ", " + FR,
     "THE GROUND FREEZING OVER, 8 frames, " + LR + ", " + FEET + ", centred, the field growing to an ellipse 60 squares "
     "wide and 20 tall: 1 a bright white-blue crack star 10 wide; 2 pale-blue ice spreading 24 wide with white cracks; 3 "
     "the ice 40 wide, frost smoke at its edge; 4 the ice 56 wide, a ring of small ice spikes (3-4 squares tall) popping up "
     "along its rim; 5 the spikes at full height, the cracks glowing white; 6-7 the frost smoke settling, a few glints; 8 "
     "the full frozen ellipse 60 x 20 with its cracks and a thin rim of spikes, calm. " + FREL + ".",
     row(8, 64, 24) + CENTER),
    ("w_aura", "冰封领域：脚下的冰面，6 帧循环", "view_buffs `league_trundle_w_on`（跟随特朗德尔，脚下，z -1；左右对称）", "48 × 16",
     "领地生效时（8 秒）他脚下一直有一片冰面：蓝白的冰、白色的裂纹一闪一闪，边上几缕寒气往上飘（他在冰面上攻速、移速更快）。**左右对称**，6 帧循环。",
     IC + ", " + FR,
     "A FROZEN PATCH UNDER HIM, 6 looping frames, " + LR + ", " + FEET + ": an ellipse of pale-blue ice 44 wide and 14 "
     "tall with white cracks; frames 1-6 the cracks glinting in turn around the ellipse, thin wisps of frost smoke rising "
     "from its rim. " + FREL + ".",
     row(6, 48, 16) + CENTER),
    # ---- skill2: E Pillar of Ice
    ("e_pillar", "寒冰之柱：冰柱冒出、立着、碎掉，8 帧", "view_effects `league_trundle_e_pillar`（大表，地上，z 1，不跟随；左右对称）", "26 × 58",
     "在目标处的地面上**冒出一根巨大的冰柱**（英雄联盟里是挡路的地形）：先是地面裂开冒寒气，一根粗大的多面体冰柱从地里猛地顶上来（深蓝的冰、"
     "白色的棱面、底下一圈碎冰和白霜，参考 e_pillar_base、e_pillar_glow、e_pillar_rays、e_pillar_smoke），立着（这一帧导入时会停 3 秒多），"
     "最后裂开碎成冰块倒下。**正面看，左右对称**，8 帧。",
     IC + ", " + FR,
     "A HUGE ICE PILLAR ERUPTING FROM THE GROUND, 8 frames, " + LR + ", seen from the FRONT, standing on the ground line at "
     "the bottom of the cell: 1 a white-blue crack in the ground 14 wide, frost smoke; 2 jagged ice tips breaking out 10 "
     "squares tall; 3 a thick faceted ice pillar shooting up 40 squares tall, 16 wide, deep-blue body with white facets, "
     "a ring of broken ice and frost at its foot; 4 the pillar at full height 52 squares, a white flash on its tip; 5 the "
     "pillar standing (frost glinting on its facets); 6 the same, standing still (THIS frame is held while it stands); 7 "
     "deep cracks running down it, chunks breaking off; 8 it collapsing into a heap of ice chunks and frost smoke. Every "
     "ice part has a 1-square near-black outline (it is a solid thing), the frost smoke none. " + FREL + ".",
     row(8, 26, 58) + CENTER),
    ("e_hit", "寒冰之柱：冰柱旁边的人，4 帧", "view_effects `league_trundle_e_hit`（跟随目标，z 2；左右对称）", "22 × 16",
     "冰柱冒出来时站在旁边的英雄：脚下一圈冰刺扎起来、寒气冲上来（他被冻住、跑不动）。**左右对称**，4 帧。",
     IC + ", " + FR,
     "ICE SPIKES BURSTING AROUND A UNIT'S FEET, 4 frames, " + LR + ", " + TARGET + ": 1 a white crack ring at the feet; 2 "
     "short ice spikes (4-6 squares) stabbing up in a ring 20 wide around the feet; 3 frost smoke rising 10 squares at both "
     "sides; 4 the spikes crumbling into frost. " + FREL + ".",
     row(4, 22, 16) + CENTER),
    # ---- ult: R Subjugate
    ("r_hit", "强权至上：抓住目标吸取，5 帧", "view_effects `league_trundle_r_hit`（跟随目标，z 2；左右对称）", "26 × 30",
     "特朗德尔伸手把敌人的生命和护甲吸过来：目标身上炸开一圈冷冷的紫蓝色光，一圈冰晶符文合拢，光往上一冲（参考 r_swirl、r_glow、r_wispy_big_scroll、"
     "r_cast_wisp）。光只画在外圈，**身体位置留空**。**左右对称**，5 帧。",
     DR + ", " + IC,
     "A COLD DRAIN SEIZING A UNIT, 5 frames, " + LR + ", " + TARGET + ": 1 a violet-blue flash at the middle 8 across; 2 a "
     "ring of angular ice runes 24 wide closing in around the unit; 3 the runes locked, cold violet light flaring up 20 "
     "squares at both sides; 4 wisps of violet light streaming up out of the unit; 5 the last motes and a faint ring. The "
     "middle (the body) left empty. " + FREL + ".",
     row(5, 26, 30) + CENTER),
    ("r_tick", "强权至上：每秒吸一口，3 帧", "view_effects `league_trundle_r_tick`（跟随目标，z 2；左右对称）", "14 × 14",
     "大招持续吸取的每一下：几点紫蓝色的光点从目标身上往上被抽走。**左右对称**，3 帧。",
     DR,
     "A DRAIN PULSE, 3 frames, " + LR + ": 1 a small violet-blue flash 5 across; 2 four bright motes pulled up and out "
     "at mirrored places; 3 the motes higher, fading. " + FREL + ".",
     row(3, 14, 14) + CENTER),
    ("r_chain", "强权至上：被吸着的目标身上，6 帧循环", "view_effects `league_trundle_r_chain`（跟随目标，z 2；左右对称）", "26 × 34",
     "被吸取的 4 秒里目标身上一直缠着**一圈冰晶锁链**，紫蓝的光往上飘（他的力量正被抽走）。锁链只在身体外圈，**身体位置留空**。**左右对称**，6 帧循环。",
     DR + ", " + IC,
     "ICE SHACKLES ON A DRAINED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": a loose ring of angular pale-blue ice "
     "chain links around the unit's middle, 24 wide, seen slightly from above; frames 1-6 the links glinting in turn and "
     "thin streams of violet-blue light rising off the unit at both sides. The middle (the body) left empty. " + FREL + ".",
     row(6, 26, 34) + CENTER),
    ("r_sap", "强权至上：被偷走护甲的人头上，4 帧循环", "view_buffs `league_trundle_r_sap`（跟随目标，头顶，z 3；左右对称）", "12 × 12",
     "被偷走护甲、魔抗的人：头顶一个**裂成两半的冰蓝盾牌**，紫光一闪一闪。**左右对称**，4 帧循环。",
     DR + ", " + IC,
     "A BROKEN SHIELD MARK OVER THE HEAD, 4 looping frames, " + LR + ": a small pale-blue shield 8 squares tall split "
     "down the middle, the halves a square apart; frames 1-4 a violet glow pulsing in the crack and a few motes drifting "
     "away. " + FREL + ".",
     row(4, 12, 12) + CENTER),
]
BIG_FX = ["w_domain", "e_pillar"]
FLYING = []
FORWARD = []

GROUPS = [
    ("a_hit (the ice club)", ["common_hiteffect", "trundle_weapon_trail", "common_sparks32", "trundle_rocks"]),
    ("p_heal (King's Tribute)", ["trundle_r_heal_trail", "common_fivedotcircle32", "common_teardrop", "trundle_ember"]),
    ("q_hit q_buff q_sap (the bite)", ["trundle_q_teeth", "trundle_q_bite_marks", "trundle_base_q_hitflash_rgba",
                                       "trundle_q_shockwave"]),
    ("q (frost breath)", ["trundle_q_frost_fire", "trundle_q_trollsmash_breathe", "trundle_q_glow", "trundle_q_ribbon"]),
    ("w_hop w_domain w_aura (the domain)", ["trundle_w_ground", "trundle_w_ground_cracks", "trundle_w_nova_snow_edge",
                                            "trundle_w_shockwave_scroll"]),
    ("w_aura slow (frost)", ["trundle_w_speedbuff_ground_glow", "trundle_w_frost_smoke", "trundle_w_overdrive_buff",
                             "trundle_w_smoke_vert"]),
    ("e_pillar e_hit (the pillar)", ["trundle_e_pillar_base", "trundle_e_pillar_glow", "trundle_e_pillar_rays",
                                     "trundle_e_pillar_smoke_2x2"]),
    ("r_hit r_tick r_chain r_sap (the drain)", ["trundle_r_swirl", "trundle_r_glow", "trundle_r_wispy_big_scroll",
                                                "trundle_r_cast_wisp"]),
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
    """Trundle at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"特朗德尔 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 巨魔之王 特朗德尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/trundle_design.png`：Q 版冰霜巨魔，炸开的红头发和红胡子、亮蓝眼睛、"
      "骨头鼻子和獠牙、白毛领、青绿宝石肩甲、灰蓝皮肤、巨大的寒冰狼牙棒）。"
      f"特朗德尔在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽，含冰棒）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/trundle_size.png`：特朗德尔缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里特朗德尔自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**特朗德尔是弗雷尔卓德的巨魔之王，特效都是冰和蛮力**：**冰**（浅蓝到深冰蓝、白色棱面）、**寒霜和雪**、他偷走力气时的**红色**、"
      "大招吸取的**冷紫蓝色**、被动回血的**淡绿色**；不要光滑的霓虹光束，也不要火。")
    a("> - **特效要亮**：每道光、每块冰都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、寒气、雪尘没有黑描边**（碎冰碴也不要描黑边，用它自己最深的一档）；**只有冰柱（`e_pillar`）这个“东西”有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——冰柱**正面**看。这次没有弹道。")
    a("> - **冰柱**（`e_pillar`）在游戏里要立 4 秒：第 6 帧是「立着」的那一帧，导入时会让它停 3 秒多，所以第 5、6 帧要是完整、稳定的冰柱。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `trundle_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/trundle_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 抡冰狼牙棒砸 | `a_hit` |")
    a("| 被动「国王的贡品」（并入 W 冰封领域） | 附近敌人死亡时回血；Q 咬中英雄时跳起冻住地面，冰面上攻速、移速更快 | `p_heal` · `w_hop` · `w_domain` · `w_aura` |")
    a("| 技能 1 =「利齿撕咬」 | 咬一口：伤害、减速、偷对方的攻击力 | `q_hit` · `q_buff` · `q_sap` · `slow` |")
    a("| 技能 2 =「寒冰之柱」 | 在敌方英雄处冒出一根冰柱，周围减速（附加包里冰柱是挡路的地形） | `e_pillar` · `e_hit` · `slow` |")
    a("| 大招 =「强权至上」 | 抓住敌方英雄吸取生命、护甲和魔抗 4 秒，顺带在他那冒一根冰柱 | `r_hit` · `r_tick` · `r_chain` · `r_sap` |\n")
    a("连招：**冰柱 → 利齿撕咬马上好**，**咬中英雄 → 冻住地面**，**强权至上 → 利齿撕咬刷新 + 冰柱**，**冰面上击杀 → 回血加倍**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、寒气、雪尘没有黑描边，也不要用最深的颜色给形状描一圈边**（冰柱除外）。")
    a("- **都是冰和蛮力**：冰、寒霜、红、紫蓝、淡绿；每个形状 2–3 档平涂，冰块用棱角分明的几何面。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("冰", ICE), ("寒霜·雪", FROST), ("力气·红", RAGE), ("吸取·紫蓝", DRAIN), ("回血·淡绿", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（冰面、寒霜）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `trundle_fx_{name}.png`：{title}\n")
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
        a(f"| `trundle_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_trundle_fx`（小的）和 `league_trundle_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_trundle.py 的 views；buff 的 tag：w_on → w_aura、q_slow / e_slow → slow、q_ad → q_buff）。"
      "e_pillar 的第 6 帧拉长到冰柱立满 e_t（240 tick）；r_chain 由 casted 每 60 tick 播一次（循环 1 秒）。")
    a("- 全部断言左右对称。")
    a("- 用 `pixel_1x/` 切格（import_yorick_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="trundle_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "trundle_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_trundle.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "trundle_design.png"))
    shape = size_sheet(os.path.join(out, "design", "trundle_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"trundle_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
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
