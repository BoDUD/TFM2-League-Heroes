#!/usr/bin/env python3
"""Build sentinel_fx_pack.zip: step 3 of the Blue Sentinel's sprite - Codex draws its effects and its three skill
icons (the tft heroes' way).

    python tools/lol/fx_ref_sentinel.py            # the particle references -> C:/t/bg_work/fxref
    python tools/art/pack_sentinel_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name sentinel_fx_redo_pack]

The pack (C:/t/bg_work/fx/sentinel_fx_pack, zipped into --out, default D:/TFM2-Workshop/sentinel_packs) holds PROMPTS.md
(also written to assets/source/sentinel/PROMPTS_FX.md), design/sentinel_design.png (the approved idle at 4x on its
own squares), design/sentinel_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler
and the base fighter) and refs/tft_fx_ref.png (the Rift's Blue Sentinel's particle textures and Malphite's and
Ornn's - grey shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds
(tools/kit/build_sentinel.py, the user's picks 2026-10-31: jungle, plan A 「蔚蓝冲击波」): view_effects a_hit,
q_hit, e_cast, r_slam; view_projectiles r_crack (tft.dll's fissure); view_buffs p_blue, q_slow, e_shield (also the
ult's shield), e_taunt, r_hit, r_reave, r_seal (tft.dll's). Plus the three skill icons.
Its colours: the cyan of its eye and glowing seams, its slate-teal and pale sage stone, grey-brown dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying fissure is symmetric top to bottom, pointing right.
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

TMP = "C:/t/bg_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "sentinel", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "sentinel", "hd")
NAME = "sentinel_fx_pack"
PPU = 1.7

CYAN = "#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86"            # its eye, its glowing seams and runes
STONE = "#DDE0C6, #AEB497, #73898A, #45606A, #263840"           # pale sage boulders to dark slate-teal rock
DUST = "#E2DACA, #B3A992, #7D7464, #4C473E"                     # the dust its slams throw up
CY = f"a rune-cyan light ramp ({CYAN})"
ST = f"a stone ramp ({STONE})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of "
         "light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, "
         "crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams")
HIM = ("the golem stands in the middle, not drawn: about 58 squares wide and 40 tall, hunched, its two huge fists low at "
       "its sides, its small head at the upper right")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan "
        "rune corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「岩拳猛击」：石拳砸中，4 帧", "view_effects `tft_sentinel_a_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "石拳砸中：一下青白色的闪光，几块青灰色的碎石和一圈尘土往两边崩开，一两点青色的符文火星。**左右对称**，4 帧。",
     CY + ", " + ST + ", " + DU,
     "A STONE FIST IMPACT, 4 frames, " + LR + ": 1 a pale cyan-white flash 5 squares across; 2 a short burst of "
     "cyan light with four stubby rays, 12 squares across, a few slate stone chips flying out to both sides "
     "(mirrored); 3 the chips falling outward, a low puff of grey-brown dust at the bottom, two tiny cyan sparks; "
     "4 the last dust and one falling chip on each side. " + MAGIC + ".",
     row(4, 18, 16) + CENTER),
    ("q_hit", "技能 1「双拳重砸」：砸地冲击环，6 帧", "view_effects `tft_sentinel_q_hit`（大表，放在它砸地的地面上，不跟随，z -1；左右对称）",
     "76 × 26",
     "双拳砸地：它身前地面上一下青色的闪光，**一圈带裂缝的冲击环**往外推开（从斜上方看的椭圆，宽是高的 3 倍），"
     "环上一道道短裂缝透着青光，碎石和尘土往外翻。**只在地面上**。**左右对称**，6 帧。",
     CY + ", " + ST + ", " + DU,
     "A GROUND POUND RING, 6 frames, " + LR + ": on the GROUND only, seen from above at a slant: 1 a bright cyan-white "
     "flash in the middle, 12 squares wide; 2 a ring of short jagged CRACKS glowing cyan bursting outward (an ellipse "
     "40 squares wide, 13 tall), stone chips jumping up along it; 3 the ring 60 squares wide, its cracks longer, grey "
     "dust rolling out on both sides (mirrored); 4 the ring at 72 squares wide and thinner, the chips falling; 5 only "
     "the cracks' cyan glow fading and settling dust; 6 a few dim cracks. The middle stays clear after frame 2. "
     + MAGIC + ".",
     row(6, 76, 26) + CENTER),
    ("q_slow", "技能 1「双拳重砸」：减速，6 帧循环", "view_buffs `tft_sentinel_q_slow`（跟随被减速的人，脚下，z 3；左右对称）", "24 × 8",
     "被减速的人：脚边**几块青灰色的小石块缠着脚踝**，石缝里一点青光，像脚被石头拖住。很淡、只在脚下。**左右对称**，6 帧循环。",
     ST + ", " + CY,
     "STONE SHACKLES, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): on EACH side "
     "(mirrored) two or three small slate-teal stone chunks hugging the ankle line, a thin cyan glint in the seam "
     "between them, a faint low dust haze; frames 1-6 the chunks grinding a square up and down and the glints moving "
     "(every frame left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("e_cast", "技能 2「雕纹石肤」：符文亮起，5 帧", "view_effects `tft_sentinel_e_cast`（大表，跟随它，z 3；左右对称）", "64 × 46",
     "它身上的螺旋符文一下亮起：身体四周**一圈青色螺旋符文**往外闪开（像刻在石头上的花纹发光飞起），最后化成青色光点往上飘。"
     "**它的身体位置留空**。**左右对称**，5 帧。",
     CY,
     "A RUNE FLARE, 5 frames, " + LR + ": round " + HIM + ": 1 a few cyan sparks at its edges; 2 six to eight glowing "
     "cyan SPIRAL RUNE GLYPHS (each a small square spiral 5 squares across, near-white in their middle line) appearing "
     "all round the edge of its body, mirrored; 3 the glyphs bright, pushed a little outward, short cyan rays between "
     "them; 4 the glyphs breaking into cyan motes drifting UP; 5 the last motes at the top. The middle of the cell (its "
     "body) stays EMPTY. " + MAGIC + ".",
     row(5, 64, 46) + CENTER),
    ("e_shield", "技能 2「雕纹石肤」/ 大招护盾：石肤护盾，6 帧循环", "view_buffs `tft_sentinel_e_shield` / `tft_sentinel_r_shield`"
     "（大表，跟随它，z 3；左右对称）", "70 × 50",
     "它的护盾：身子外面**一圈刻着符文的石板**围成的护壳（竖着的椭圆，只画外圈：一块块浅灰绿的石板，每块上一个发青光的螺旋符文），"
     "符文一闪一闪地轮流亮。**里面它的身体位置留空**。**左右对称**，6 帧循环。",
     ST + ", " + CY,
     "A RUNE STONE SHELL, 6 looping frames, " + LR + ": round " + HIM + ": a ring of CARVED STONE PLATES (an upright "
     "ellipse 66 squares wide and 46 tall, only its 3-square rim drawn, made of eight to ten pale sage stone slabs with "
     "dark seams), each slab with a small glowing CYAN SPIRAL RUNE; a thin cyan light line along the inner edge; frames "
     "1-6 the runes lighting up in turn round the ring (mirrored pairs) and the inner line breathing (every frame "
     "left-right symmetric). INSIDE the ring stays EMPTY (its body). " + MAGIC + ".",
     row(6, 70, 50) + CENTER),
    ("e_taunt", "技能 2「雕纹石肤」：被嘲讽，6 帧循环", "view_buffs `tft_sentinel_e_taunt`（跟随被嘲讽的人，头顶上方，z 4；左右对称）",
     "12 × 12",
     "被嘲讽的人头顶：一个**青色的发光独眼符文**（一个圆圈里一只眼睛，像魔像的眼睛盯着你），一跳一跳地发光。**左右对称**，6 帧循环。",
     CY + ", " + ST,
     "A TAUNT GLYPH, 6 looping frames, " + LR + ": above a unit's head: a round slate stone disc 10 squares across with a "
     "glowing CYAN EYE glyph cut into it (an almond eye, a near-white pupil square), a thin cyan ring round the disc; "
     "frames 1-6 the eye pulsing brighter and dimmer and the disc bobbing one square up and down. " + MAGIC + ".",
     row(6, 12, 12) + CENTER),
    ("r_slam", "大招「蔚蓝冲击波」：猛砸地面，6 帧", "view_effects `tft_sentinel_r_slam`（大表，放在它砸地的地面上，不跟随，z -1；左右对称）",
     "96 × 40",
     "它双拳砸进地面：一下巨大的青白闪光，地面上**一个很大的青色冲击波环**炸开，大块的石板翘起、碎石和尘土往两边飞，"
     "地上留下一圈发青光的裂缝。**只在地面和低处**。**左右对称**，6 帧。",
     CY + ", " + ST + ", " + DU,
     "A HUGE RUNE SHOCKWAVE, 6 frames, " + LR + ": on the GROUND and low above it, seen from above at a slant: 1 a big "
     "cyan-white flash at the middle bottom, 20 squares wide, short rays; 2 a thick bright cyan SHOCKWAVE RING bursting "
     "open on the ground (an ellipse 50 squares wide, 16 tall, 3 squares thick), big slate STONE SLABS tilting up out of "
     "the ground on both sides (mirrored), chips flying; 3 the ring 84 squares wide, a ring of glowing cyan CRACKS left "
     "inside it, grey dust billowing out low; 4 the ring at the cell's edge and thinning, the slabs sinking, the chips "
     "falling; 5 the cracks' glow and the settling dust; 6 a few dim cracks. " + MAGIC + ".",
     row(6, 96, 40) + CENTER),
    ("r_crack", "大招「蔚蓝冲击波」：往前跑的裂隙，6 帧循环", "view_projectiles `tft_sentinel_r_crack`（大表，tft.dll 放的直线弹道，"
     "随飞行方向旋转；上下对称、朝右）", "40 × 18",
     "裂隙的最前端：地面被撕开**一道往右冲的青色裂缝**，裂缝最前面石头往上崩起、尖尖的石刺一根根冒出来又落下，后面拖着发光的裂缝。"
     "**上下对称、朝右**，6 帧循环。",
     CY + ", " + ST + ", " + DU,
     "A RUNNING FISSURE HEAD, 6 looping frames, " + TB + ": on the ground, seen from above: a jagged CRACK of bright "
     "cyan light running from the left edge to the right, 6 squares wide at the left and splitting into forks at the "
     "front (the right third), near-white along its middle; at its front end slate STONE SPIKES and chips bursting up "
     "on both sides of the crack (mirrored top and bottom), grey dust round them; frames 1-6 the spikes rising and "
     "falling in turn and the forks flickering forward, the glow pulsing along the crack (every frame top-bottom "
     "symmetric). " + MAGIC + ".",
     row(6, 40, 18) + CENTER),
    ("r_hit", "大招「蔚蓝冲击波」：被裂隙击飞，5 帧", "view_buffs `tft_sentinel_r_hit`（跟随被击飞的人，z 3；左右对称）", "22 × 26",
     "被裂隙击中的人：脚下**石刺一下冲上来**、一道青光往上喷，碎石往两边飞。**人站的地方留空**。**左右对称**，5 帧。",
     CY + ", " + ST + ", " + DU,
     "A ROCK ERUPTION, 5 frames, " + LR + ": round " + CHAMP + ": 1 a cyan crack flash on the ground under its feet; "
     "2 three sharp slate STONE SPIKES shooting up beside its feet (one each side, one small in front, mirrored), a "
     "column of cyan light rising up its sides; 3 the spikes at their tallest (10 squares), chips flying out; 4 the "
     "spikes crumbling, the light fading upward; 5 falling chips and dust. The middle of the cell (its body) stays "
     "EMPTY. " + MAGIC + ".",
     row(5, 22, 26) + CENTER),
    ("r_reave", "大招「蔚蓝冲击波」：破法标记，6 帧循环", "view_buffs `tft_sentinel_r_reave`（跟随被破法的人，头顶上方，z 4；左右对称）",
     "14 × 12",
     "被破法的人头顶：**一颗裂开的青色符文水晶**（菱形，中间一道裂缝），缓缓上下浮动、一闪一闪。**左右对称**，6 帧循环。",
     CY,
     "A CRACKED MANA RUNE, 6 looping frames, " + LR + ": above a unit's head: a cyan diamond crystal 8 squares wide and "
     "10 tall, a near-white spiral rune in it, a dark CRACK running down its middle splitting it in two halves a square "
     "apart; frames 1-6 it bobbing one square up and down, the halves glowing brighter and dimmer, one tiny shard "
     "falling from the crack. " + MAGIC + ".",
     row(6, 14, 12) + CENTER),
    ("r_seal", "大招「蔚蓝冲击波」：破法封印，6 帧循环", "view_buffs `tft_sentinel_r_seal`（跟随被封住的人，头顶上方，z 4；左右对称）",
     "18 × 14",
     "被封住技能的人头顶：**一圈青色的符文锁环**（一个转着的符文圆环，中间一个石头小锁），表示技能被封。**左右对称**，6 帧循环。",
     CY + ", " + ST,
     "A RUNE SEAL, 6 looping frames, " + LR + ": above a unit's head: a flat ring of glowing cyan rune marks (an ellipse "
     "16 squares wide, 6 tall) with a small slate STONE PADLOCK 6 squares tall hanging in its middle, a cyan spiral on "
     "the lock; frames 1-6 the rune marks moving round the ring (mirrored) and the lock glinting. " + MAGIC + ".",
     row(6, 18, 14) + CENTER),
    ("p_blue", "被动「蓝霸符」：友军冷却加快，6 帧", "view_buffs `tft_sentinel_p_blue`（跟随拿到的友军，z 3；左右对称）", "26 × 34",
     "队友拿到蓝霸符：脚下一圈**青色的符文小光环**，几颗青色的小符文光点沿着身子两侧往上升（像英雄联盟里蓝 buff 的感觉）。"
     "**人站的地方留空**。**左右对称**，6 帧。",
     CY,
     "A BLUE BUFF GLOW, 6 frames, " + LR + ": round " + CHAMP + ": 1 a thin cyan ring appearing on the ground at its "
     "feet (an ellipse 22 squares wide, 6 tall); 2 the ring bright, small cyan rune motes (2x2 and 1x1 squares) rising "
     "from it up both sides of the body (mirrored); 3-4 the motes rising higher, one small spiral glyph above its head; "
     "5 the motes fading near the top, the ring dimming; 6 the last motes. The middle (its body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 26, 34) + CENTER),
]
ICONS = [
    ("skill", "技能 1「双拳重砸」图标", "skill_icons[0] `asset/tft/icons/tft_sentinel_skill`",
     ICON + ": two huge slate-teal stone fists smashing down together into the ground, a ring of glowing cyan cracks and "
               "stone chips bursting out under them."),
    ("skill2", "技能 2「雕纹石肤」图标", "skill_icons[1] `asset/tft/icons/tft_sentinel_skill2`",
     ICON + ": a round shield of carved pale sage stone plates with a big glowing cyan spiral rune in its middle, small "
               "cyan rune sparks round it."),
    ("ult", "大招「蔚蓝冲击波」图标", "skill_icons[2] `asset/tft/icons/tft_sentinel_ult`",
     ICON + ": a jagged bright cyan fissure tearing across the ground from the lower left to the upper right, stone "
               "spikes bursting up along it, a small one-eyed stone golem head glowing cyan in the lower left corner."),
]
BIG_FX = ["q_hit", "e_cast", "e_shield", "r_slam", "r_crack"]
FLYING = ("r_crack",)

GROUPS = [
    ("a_hit r_hit (the fist and the eruption)",
     ["malphite_base_z_sparks", "malphite_base_x_small_stone", "ornn_base_q_hit_flash", "ornn_base_q_hit3_spikes",
      "ornn_base__z_rockdebris"]),
    ("q_hit r_slam (the ground pounds)",
     ["ornn_base_e_explosion_groundcrack", "ornn_base_r_impact_wave", "ornn_base_q_nova_ground",
      "malphite_base_r_rock_debris", "ornn_base_q_dustcloud"]),
    ("r_crack (the fissure)",
     ["ornn_base_q_cracks2", "ornn_base_q_cracks2_missile", "ornn_base_q_cracks3", "ornn_base_q_pillar_spike",
      "malphite_skin16_q_crack_dissolve"]),
    ("e_shield e_cast (the carved stone skin)",
     ["malphite_base_p_shield_circle", "malphite_base_p_shield_refresh_overlay", "malphite_base_p_rocks",
      "malphite_base_p_swoop", "ornn_base_w_braum_skin01_e_first_block_shield"]),
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
    """The golem at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"魔像 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 苍蓝雕纹魔像：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/sentinel_design.png`："
      "3/4 朝右、弓着背的深青灰岩石巨人：两只比脑袋大得多的巨拳垂在身前两侧；肩背上堆着浅灰绿大石块；浅色八角石墩小脑袋半埋在两肩之间，"
      "深色缺口里一只青色独眼；胸口 V 形青光、腰上青色带子；石块上刻着螺旋符文）。"
      f"魔像在游戏里是**高清**的（每个游戏格子里约 1.7×1.7 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sentinel_size.png`：魔像缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是熔岩巨兽（石头护盾、碎石、砸地）和奥恩（地面裂缝、冲击波、石刺）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **魔像是古老的符文石头巨人，特效都是它的味道**：发青光的螺旋符文、地面上透着青光的裂缝、"
      "成块的青灰色和浅灰绿色碎石石板、灰褐色的尘土；不要火焰、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了往前跑的裂隙 `r_crack`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sentinel_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `sentinel_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「岩拳猛击」 | 一只巨拳举过头顶砸下 | `a_hit` |")
    a("| 被动「蓝霸符」 | 它每放一个技能，身边友军的技能冷却立刻缩短 | `p_blue` |")
    a("| 技能 1 =「双拳重砸」 | 双拳砸在身前地面，周围敌人受伤并减速 | `q_hit` · `q_slow` |")
    a("| 技能 2 =「雕纹石肤」 | 符文亮起，获得护盾，嘲讽身边的敌人 | `e_cast` · `e_shield` · `e_taunt` |")
    a("| 大招 =「蔚蓝冲击波」 | 护盾，双拳过顶猛砸地面，朝敌人最多的方向裂开一道裂隙：击飞、魔法伤害、破法（下一个技能被封） | "
      "`r_slam` · `r_crack` · `r_hit` · `r_reave` · `r_seal` · `e_shield` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("符文青（它的眼睛、发光的缝和符文）", CYAN), ("石头（浅灰绿到深青灰）", STONE), ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sentinel_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `sentinel_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `sentinel_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `sentinel_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_sentinel_fx`（小的）和 `tft_sentinel_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- r_crack 断言上下对称（朝右），其余断言左右对称。")
    a("- q_hit、r_slam 放在它砸地的地面上（不跟随，z -1）；e_cast、e_shield 是它身上的 caster 画面（e_shield 也给大招护盾用）；"
      "p_blue 是友军身上的 buff；q_slow、e_taunt 是敌人身上的 buff；r_crack 是 tft.dll 放的裂隙弹道，r_hit、r_reave、r_seal 是 tft.dll 给的 buff。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sentinel_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/sentinel_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_sentinel.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "sentinel_design.png"))
    shape = size_sheet(os.path.join(out, "design", "sentinel_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sentinel_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"sentinel_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
