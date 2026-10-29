#!/usr/bin/env python3
"""Build steb_fx_pack.zip: step 3 of Steb's sprite - Codex draws his effects and his three skill icons
(pack_sevika_fx.py's way).

    python tools/lol/fx_ref_steb.py           # his TFT particle textures -> C:/t/sb_work/fxref
    python tools/art/pack_steb_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name steb_fx_redo_pack]

The pack (C:/t/sb_work/fx/steb_fx_pack, zipped into --out, default D:/TFM2-Workshop/steb_packs) holds PROMPTS.md (also
written to assets/source/steb/PROMPTS_FX.md), design/steb_design.png (the approved idle at 4x on its own squares),
design/steb_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (his own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_steb.py, the user's picks 2026-10-29: support,
plan A 「战地军医」): view_effects a_hit, q_heal, q_hit, e_mark, e_kill, p_heal, r_pack, r_heal; view_buffs q_stun,
e_wanted, e_rush, r_guard, r_shield. No projectiles. Plus the three skill icons. The baton swings, the dose at his chest,
the call and the squat are in his own frames.
His colours: Piltover's HEXTECH cyan (his batons' runes), the field medic's GREEN healing light with white crosses,
the enforcers' BLUE and GOLD (their badge), the bounty's RED crosshair.
Red side: every effect picture is symmetric left to right (the client never mirrors an effect picture).
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

TMP = "C:/t/sb_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "steb", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "steb", "hd")
NAME = "steb_fx_pack"
PPU = 2.6

HEX = "#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A"              # the batons' hextech runes
MEDIC = "#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C"            # the field medic's healing light
GOLD = "#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08"             # the enforcers' gold, the bounty
BLUE = "#E0ECFF, #8AB0FF, #3E6CE8, #2238A0, #101C50"             # the enforcers' blue
RED = "#FFE0D8, #FF8A70, #E8402A, #A01818, #500A0A"              # WANTED: the crosshair
RUSH = "#FFF4D0, #FFC860, #F08A20, #B04E0C, #5A2406"             # the bounty's attack speed
HX = f"a hextech cyan ramp ({HEX})"
ME = f"a healing green ramp ({MEDIC})"
GO = f"a gold ramp ({GOLD})"
BL = f"an enforcer blue ramp ({BLUE})"
RE = f"a crosshair red ramp ({RED})"
RU = f"an orange speed ramp ({RUSH})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a "
         "medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a "
         "RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic")
HIM = "the tall enforcer stands in the middle, not drawn: 31 squares wide and 41 tall"
ALLY = "a champion stands in the middle, not drawn: 20 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little gold "
        "corner rivets, a deep blue-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px "
        "a square (32 x 32 squares), chunky and readable at 64 px")
BATON = ("a blue steel SIDE-HANDLE BATON (a tonfa: a brass head with glowing cyan runes at one end, a silver-grey rod at "
         "the other, a wooden side grip)")
CROSS = "a WHITE CROSS (a plus sign, 3 squares across, a 1-square bar each way)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：警棍打中，4 帧", "view_effects `tft_steb_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "警棍打在人身上：一个白色的**冲击闪光**，一圈**青色的海克斯火花环**，几点金色火星往两边崩开。**左右对称**，4 帧。",
     HX + ", " + GO,
     "A BATON IMPACT, 4 frames, " + LR + ": 1 a white flash 6 squares across; 2 a cyan hextech spark ring 14 squares "
     "wide and 6 tall, a few gold sparks (1-2 squares) knocked out to both sides (mirrored); 3 the ring wider and "
     "thinner, the sparks farther; 4 the last sparks fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_heal", "技能1 战地医疗：给自己打一针，6 帧", "view_effects `tft_steb_q_heal`（跟随他，z 3；左右对称）", "36 × 44",
     "他把警棍按在胸口给自己打一针：胸口一个**绿色的闪光**（小，只在胸前正中），然后一圈绿光从脚下亮起，几个**白色小十字**和绿色光点绕着他往上飘。身体其余位置留空。**左右对称**，6 帧。",
     ME + ", " + HX,
     "A FIELD MEDICINE DOSE, 6 frames, " + LR + ", " + HIM + ": 1 a small bright green flash 6 squares across at his "
     "chest (the middle of the cell, a little above the centre) with a cyan glint; 2 a green light ring " + GROUND_E +
     " 28 squares wide and 8 tall at the bottom, a few green motes; 3 several " + CROSS + " and green motes rising at "
     "both sides of him (mirrored); 4 the crosses higher, a faint green glow along his outline at both sides; 5 the "
     "crosses near the top, fading; 6 the last glints. The body left empty except the small chest flash. " + MAGIC + ".",
     row(6, 36, 44) + CENTER),
    ("q_hit", "技能1：警棍重击打中，6 帧", "view_effects `tft_steb_q_hit`（跟随目标，z 2；左右对称）", "24 × 24",
     "一警棍重重砸在目标身上：一个大的白色闪光，一圈**粗的青色海克斯冲击波**，几条青色的符文碎光和金色火星往两边飞。**左右对称**，6 帧。",
     HX + ", " + GO + ", " + BL,
     "A HEAVY HEXTECH BATON STRIKE, 6 frames, " + LR + ": 1 a big white flash 12 squares across; 2 a thick cyan "
     "hextech shock ring 20 squares wide and 8 tall, short cyan rune shards and gold sparks thrown out to both sides "
     "(mirrored); 3 the ring wider and thinner, a few blue glints; 4 the shards falling; 5 a faint cyan haze; 6 the "
     "last specks. " + MAGIC + ".",
     row(6, 24, 24) + CENTER),
    ("q_stun", "技能1：被砸晕，6 帧循环", "view_buffs `tft_steb_q_stun`（跟随被晕的人，头顶，z 3；左右对称）", "20 × 10",
     "被砸晕的人头顶：几个**青色的小齿轮 / 星星**转圈。**左右对称**，6 帧循环。",
     HX + ", " + GO,
     "A STUN OVER THE HEAD, 6 looping frames, " + LR + ": three small symmetric shapes (3 squares: a cyan cog, a gold "
     "star, a cyan star) circling on a flat ring 16 squares wide and 4 tall; frames 1-6 them going round. " + MAGIC + ".",
     row(6, 20, 10) + CENTER),
    ("e_mark", "技能2 通缉令：贴上通缉，6 帧", "view_effects `tft_steb_e_mark`（跟随目标，头顶，z 4；左右对称）", "22 × 22",
     "通缉令打在目标身上：头顶上方猛地落下一个**红色的准星**（一个圆圈 + 上下左右四道短线），落定时闪一下，中间一个**金色的执法官徽章**亮起。**左右对称**，6 帧。",
     RE + ", " + GO,
     "A WANTED MARK SLAMMING DOWN, 6 frames, " + LR + ": 1 a big thin RED crosshair (a ring 18 squares across with "
     "four short ticks pointing in, up, down, left and right) high in the cell; 2 it shrinking and dropping to the "
     "middle, 12 squares across, bright; 3 it locks: a white flash at its centre; 4 a small GOLD shield-shaped badge (5 "
     "squares wide, 6 tall) shining in its centre; 5 the crosshair and badge steady; 6 dimmer. " + MAGIC + ".",
     row(6, 22, 22) + CENTER),
    ("e_wanted", "通缉中：头顶的准星，6 帧循环", "view_buffs `tft_steb_e_wanted`（跟随被通缉的人，头顶，z 4；左右对称）", "14 × 14",
     "被通缉的人头顶一直挂着一个小小的**红色准星 + 金色徽章**，一亮一暗地跳动。**左右对称**，6 帧循环。",
     RE + ", " + GO,
     "A WANTED MARK HANGING OVER THE HEAD, 6 looping frames, " + LR + ": a small RED crosshair (a ring 10 squares "
     "across with four short ticks) around a tiny GOLD badge (3 squares wide, 4 tall); frames 1-6 it pulsing - "
     "brighter, a little bigger, back. " + MAGIC + ".",
     row(6, 14, 14) + CENTER),
    ("e_kill", "通缉犯倒下：领赏，8 帧", "view_effects `tft_steb_e_kill`（跟随他，z 3；左右对称）", "40 × 44",
     "被通缉的人倒下了：他头顶闪出一个**大的金色执法官徽章**，徽章四周炸开金光和金色火花，两边几道**橙色的速度光**往上冲。身体位置留空。**左右对称**，8 帧。",
     GO + ", " + RU + ", " + RE,
     "A BOUNTY CLAIMED, 8 frames, " + LR + ", " + HIM + ": 1 a gold flash 8 squares across over his head; 2 a big "
     "GOLD shield-shaped ENFORCER BADGE (10 squares wide, 12 tall, a blue gem in its middle) bursting out over his "
     "head with a ring of gold sparks; 3 the badge bright, short ORANGE speed streaks (1 square wide, 6-10 tall) "
     "shooting up at both sides of him (mirrored); 4 more streaks, a red crosshair breaking apart behind the badge; "
     "5-6 the streaks rising, the badge glinting; 7 the badge fading; 8 the last glints. The middle (the body) left "
     "empty. " + MAGIC + ".",
     row(8, 40, 44) + CENTER),
    ("e_rush", "领赏后：攻速提升，6 帧循环", "view_buffs `tft_steb_e_rush`（跟随队友，身上，z 3；左右对称）", "30 × 40",
     "领了赏的队友身上：身体两侧几道**橙色的速度光**一闪一闪往上窜，脚下一圈淡淡的橙光。身体位置留空。**左右对称**，6 帧循环。",
     RU + ", " + GO,
     "AN ATTACK SPEED RUSH, 6 looping frames, " + LR + ", " + ALLY + ": at both sides (mirrored) short ORANGE speed "
     "streaks (1 square wide, 5-8 tall) flicking upward along the outline, a faint orange ring " + GROUND_E + " 24 "
     "squares wide and 6 tall at the bottom, a few gold sparks; frames 1-6 the streaks rising and flickering. The "
     "middle (the body) left empty. " + MAGIC + ".",
     row(6, 30, 40) + CENTER),
    ("p_heal", "被动 战地医疗：分到治疗，6 帧", "view_effects `tft_steb_p_heal`（跟随队友，z 3；左右对称）", "24 × 32",
     "他受到治疗时，最近的队友也回一点血：那个队友身上冒出两三个**白色小十字**和绿色光点往上飘，脚下一个小小的绿圈。身体位置留空。**左右对称**，6 帧。",
     ME,
     "A SHARED HEAL, 6 frames, " + LR + ", " + ALLY + " (smaller cell: the crosses at both sides): 1 a small green "
     "ring " + GROUND_E + " 18 squares wide and 5 tall at the bottom; 2 two " + CROSS + " appearing at both sides of "
     "the body (mirrored), green motes; 3-4 them rising and a third one over the head; 5 fading at the top; 6 the last "
     "motes. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 24, 32) + CENTER),
    ("r_pack", "大招 医疗背包：地上的医疗圈，8 帧", "view_effects `tft_steb_r_pack`（大表，在他脚下的地上，z -1；左右对称）", "84 × 30",
     "他打开背包：脚下的地上亮起一个**大的绿色医疗圈**（从斜上方看的椭圆），圈上一圈小的**白色十字**和青色的海克斯刻度，圈里铺着淡淡的绿光，从中间往外扩。**左右对称**，8 帧（地上的图，不画人）。",
     ME + ", " + HX,
     "A MEDIC'S CIRCLE ON THE GROUND, 8 frames, " + LR + ", lying " + GROUND_E + ": 1 a bright green ring 20 squares "
     "wide and 7 tall in the middle; 2 it spreading to 50 x 17, a white flash along it; 3 the full ring 80 squares wide "
     "and 26 tall, a thin second ring inside, eight small " + CROSS + " evenly round it (mirrored), cyan hextech tick "
     "marks between them, a faint green fill; 4-6 the ring steady, the crosses glinting one pair after another, green "
     "motes rising a little from the ring; 7 dimmer; 8 only the crosses glinting. " + MAGIC + ".",
     row(8, 84, 30) + CENTER),
    ("r_heal", "大招：一次治疗脉冲，5 帧", "view_effects `tft_steb_r_heal`（跟随他和每个队友，z 3；左右对称）", "30 × 40",
     "医疗背包每隔一会儿治疗一次：人身上一圈**绿光从脚下往上扫过**，几个白色小十字跟着往上飘。身体位置留空（只画外圈和脚下）。**左右对称**，5 帧。",
     ME,
     "A HEALING PULSE, 5 frames, " + LR + ", " + ALLY + ": 1 a green ring " + GROUND_E + " 24 squares wide and 7 tall "
     "at the bottom; 2 a band of green light sweeping up both sides of the outline (mirrored), two " + CROSS + "; 3 the "
     "band at the shoulders, more crosses; 4 crosses over the head; 5 fading motes. The middle (the body) left empty. "
     + MAGIC + ".",
     row(5, 30, 40) + CENTER),
    ("r_guard", "大招：他自己减伤，6 帧循环", "view_buffs `tft_steb_r_guard`（跟随他，z 3；左右对称）", "40 × 44",
     "打开背包时他自己减伤：身体两侧各立着一块半透明的**蓝色执法官盾牌**的轮廓（金边、上面一道青色的海克斯光纹），一闪一闪。身体位置留空。**左右对称**，6 帧循环。",
     BL + ", " + GO + ", " + HX,
     "AN ENFORCER GUARD, 6 looping frames, " + LR + ", " + HIM + ": at both sides of him (mirrored) a tall riot SHIELD "
     "outline 6 squares wide and 26 tall - a BLUE rim with GOLD corners and a thin cyan hextech line down its middle, "
     "only the rim and the line drawn (see-through inside); frames 1-6 a glint running up each shield and the cyan "
     "line pulsing. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 40, 44) + CENTER),
    ("r_shield", "大招：队友的护盾，6 帧循环", "view_buffs `tft_steb_r_shield`（跟随队友，z 3；左右对称）", "30 × 40",
     "队友身上的护盾：一圈淡淡的**青绿色海克斯护罩**的边（只画外圈的六边形格子边），几格六边形一闪一闪。身体位置留空。**左右对称**，6 帧循环。",
     HX + ", " + ME,
     "A HEXTECH BARRIER, 6 looping frames, " + LR + ", " + ALLY + ": the RIM of a rounded barrier 28 squares wide and "
     "38 tall around the unit, drawn as a band of small hexagon cells 2 squares wide in cyan with a hint of green, "
     "only the rim (the middle and the body left empty); frames 1-6 a few hexagons on both sides lighting up in turn "
     "(mirrored), a glint running round. " + MAGIC + ".",
     row(6, 30, 40) + CENTER),
]
ICONS = [
    ("skill", "技能 1「战地医疗」图标", "skill_icons[0] `asset/tft/icons/tft_steb_skill`",
     ICON + ": " + BATON + " lying diagonally from the lower left to the upper right, its glowing brass head at the "
     "upper right, crossed behind by a big bright green MEDICAL CROSS with a white core, a few cyan sparks; colours "
     "from " + HX + ", " + ME + ", " + GO + "."),
    ("skill2", "技能 2「通缉令」图标", "skill_icons[1] `asset/tft/icons/tft_steb_skill2`",
     ICON + ": a big RED CROSSHAIR (a ring with four ticks) over a GOLD shield-shaped ENFORCER BADGE with a blue gem in "
     "its middle, a white glint on the badge; colours from " + RE + ", " + GO + ", " + BL + "."),
    ("ult", "大招「医疗背包」图标", "skill_icons[2] `asset/tft/icons/tft_steb_ult`",
     ICON + ": a big BROWN LEATHER BACKPACK seen from the front, its flap thrown open, bright GREEN light and two WHITE "
     "CROSSES spilling up out of it, gold buckles; colours from a brown leather ramp (#E8B070, #B07038, #7A4420, "
     "#4A2610), " + ME + ", " + GO + "."),
]
BIG_FX = ["r_pack"]

GROUPS = [
    ("a_hit q_hit q_stun (the hextech batons)", ["tft13_fish_base_ba_animeshapesmesh01", "tft12_jax_base_spark",
                                                 "tft12_jax_base_shockwave01b", "jayce_skin05_animeshapes02",
                                                 "tft13_fish_base_hextech_pattern"]),
    ("q_heal p_heal r_heal (the medic's light)", ["tft12_galio_base_r_glow", "3026_items_lensflare01",
                                                  "tft13_fish_base_ba_item_3161_shield_rampdown_multlittle",
                                                  "tft13_fish_gear_glow", "tft_energy_ray"]),
    ("r_pack r_guard r_shield (the pack, the guard)", ["tft13_fish_base_r_decal_02", "tft13_fish_base_q_erosion",
                                                        "tft13_fish_base_ba_smoke01_mult", "samira_base_flare_ray",
                                                        "tft13_fish_trail"]),
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
    """Steb at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"斯特卜 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 斯特卜：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/steb_design.png`："
      "皮尔特沃夫的鱼人执法官、战地军医，浅海绿皮肤、青绿飞机头、鱼鳍耳，蓝色制服，背着大棕皮背包，两根带黄铜头和青色符文的侧把手警棍）。"
      f"斯特卜在游戏里是**高清**的（每个游戏格子里约 2.6×2.6 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/steb_size.png`：斯特卜缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里斯特卜自己的特效贴图（**灰色的形状，游戏里再染色**：警棍的海克斯火花、冲击环、治疗的光、地上的圈），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **斯特卜的特效是执法官军医的装备**：警棍上**青色的海克斯火花和符文光**、军医的**绿色治疗光和白色小十字**、执法官的**蓝色和金色徽章**、"
      "通缉令的**红色准星**；不要火焰，不要闪电，不要黑魔法。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、冲击波、光圈没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：每张都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。这一份没有会飞的图。"
      "挥警棍、打针、举棍、下蹲的动作都画在他自己的动作帧里，这里不画。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `steb_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `steb_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「战地医疗」 | 他受到治疗时，最近的两名队友也回复这次治疗量的 25% | `p_heal` |")
    a("| 普攻「双警棍连击」 | 左右两根警棍轮流往前抡 | `a_hit` |")
    a("| 技能 1 =「战地医疗」 | 给自己打一针回血，然后一警棍砸在目标身上：魔法伤害 + 短暂眩晕 | `q_heal` · `q_hit` · `q_stun` |")
    a("| 技能 2 =「通缉令」 | 给生命值最高的敌人挂上通缉：它受到的伤害更高；它倒下后，他和附近队友攻速提升 | `e_mark` · `e_wanted` · `e_kill` · `e_rush` |")
    a("| 大招 =「医疗背包」 | 打开背包：他和周围队友得到护盾，他自己减伤，之后每隔一会儿治疗一次（治疗还会经被动分出去） | `r_pack` · `r_heal` · `r_guard` · `r_shield` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、光圈没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海克斯青（警棍符文）", HEX), ("治疗绿", MEDIC), ("金色（徽章、赏金）", GOLD), ("执法官蓝", BLUE),
                        ("通缉红（准星）", RED), ("速度橙（攻速）", RUSH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 不要文字、字母、数字（通缉令用准星和徽章表示，不写 WANTED 字样）。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `steb_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `steb_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `steb_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `steb_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_steb_fx`（小的）和 `tft_steb_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。r_pack 在地上（z -1，不跟随）。")
    a("- p_heal、e_kill、e_rush 由 tft.dll 播 / 挂上（--plain 的数据没有：分享治疗按范围给、没有赏金）。")
    a("- 用 `pixel_1x/` 切格（import_renni_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="steb_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/steb_packs", help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_steb.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "steb_design.png"))
    shape = size_sheet(os.path.join(out, "design", "steb_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"steb_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"steb_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
