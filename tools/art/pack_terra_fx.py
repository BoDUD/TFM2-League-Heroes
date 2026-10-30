#!/usr/bin/env python3
"""Build terra_fx_pack.zip: step 3 of Terra's sprite - Codex draws her effects and her three skill icons
(the tft dragons' way).

    python tools/lol/fx_ref_terra.py            # the particle references -> C:/t/te_work/fxref
    python tools/art/pack_terra_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name terra_fx_redo_pack]

The pack (C:/t/te_work/fx/terra_fx_pack, zipped into --out, default D:/TFM2-Workshop/terra_packs) holds PROMPTS.md
(also written to assets/source/terra/PROMPTS_FX.md), design/terra_design.png (the approved idle at 4x on its own
squares), design/terra_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (her own set-7 particle textures and Malphite's - grey shapes the game
tints, grouped by the effect they inform). The effects are the views the kit binds (tools/kit/build_terra.py, the
user's picks 2026-10-31: top, plan A 「地震巨岩」): view_effects a_hit, q_hit, e, r, r_quake, r_hit; view_buffs q_slow,
e_taunt, e_shield, r_res. Plus the three skill icons.
Her colours: the grey-green stone of her plates, the gold-orange glowing cracks of TFT's Earthquake crater, brown
earth and dust, a little moss green.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture).
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

TMP = "C:/t/te_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "terra", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "terra", "hd")
NAME = "terra_fx_pack"
PPU = 1.45

STONE = "#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E"           # her rock plates: pale stone to deep olive
EMBER = "#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08"           # the glowing cracks of her quake: cream-yellow to deep orange
DUST = "#E6D9BE, #BBA680, #8B7452, #5B4732"                     # earth and dust
MOSS = "#A9C474, #73923F, #48622B"                              # the moss on her plates
ST = f"a stone ramp ({STONE})"
EM = f"an ember-gold ramp ({EMBER})"
DU = f"an earth-dust ramp ({DUST})"
MO = f"a moss ramp ({MOSS})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING "
         "GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat "
         "shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams")
HER = "the dragon stands in the middle, not drawn: 60 squares wide and 36 tall, crouched on all fours, her head at the right"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-stone frame with little "
        "gold corners, a deep brown-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px "
        "a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「岩爪」：石爪打中，4 帧", "view_effects `tft_terra_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "岩爪打中：一下金橙色的闪光，两组交叉成 X 的石色爪痕，几块灰绿碎石往两边崩开。**左右对称**，4 帧。",
     ST + ", " + EM,
     "A ROCK CLAW HIT, 4 frames, " + LR + ": 1 a cream-yellow flash 4 squares across; 2 two sets of three thick "
     "stone-grey claw marks crossing in an X, 14 squares across, gold-orange along their middles; 3 the marks breaking "
     "into small grey-green stone chips flying out to both sides (mirrored); 4 a few falling chips and a puff of brown "
     "dust. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_hit", "技能 1「裂地咬」：石牙咬下，5 帧", "view_effects `tft_terra_q_hit`（跟随目标，z 3；左右对称）", "22 × 22",
     "咬中：上下两排**米白色的石牙虚影**从上下合拢咬在一起，咬合的一下金橙色光爆开，地面一样的裂纹从咬合处往外裂开，"
     "几块碎石崩出去。**左右对称**，5 帧。",
     ST + ", " + EM,
     "A STONE BITE, 5 frames, " + LR + ": 1 two glowing jaw outlines open wide, an upper row of 5 cream stone fangs "
     "pointing down at the top and a lower row of 5 pointing up at the bottom, 20 squares wide; 2 the jaws snapping "
     "half shut; 3 the fangs meeting in the middle with a bright gold-orange burst 12 squares across, thin glowing "
     "cracks shooting out from it; 4 grey-green stone chips flying out to both sides (mirrored), the fangs fading; "
     "5 a few fading chips and dust. " + MAGIC + ".",
     row(5, 22, 22) + CENTER),
    ("q_slow", "技能 1「裂地咬」：减速，6 帧循环", "view_buffs `tft_terra_q_slow`（跟随被减速的人，脚下地面，z 3；左右对称）", "20 × 8",
     "被减速：脚下地面裂开（从斜上方看的椭圆，宽是高的 3 倍），几道金橙色的细裂纹在发光，几块小碎石缠在脚边一起一落。**左右对称**，6 帧循环。",
     DU + ", " + EM + ", " + ST,
     "A CRACKED-GROUND SNARE, 6 looping frames, " + LR + ": on the GROUND round the unit's feet, an ellipse seen from "
     "above, about 18 squares wide and 6 tall, of cracked brown earth; a few thin gold-orange glowing cracks in it "
     "pulsing brighter and dimmer; two or three small grey-green stone chips at its edge rising a square or two and "
     "dropping back (keep every frame left-right symmetric). Nothing above the feet. " + MAGIC + ".",
     row(6, 20, 8) + CENTER),
    ("e", "技能 2「龙威咆哮」：咆哮冲击波，6 帧", "view_effects `tft_terra_e`（大表，跟随她，z 4；左右对称）", "72 × 48",
     "她仰头咆哮的一下：从她身上往外**一圈圈扩散的金橙色声浪环**（从斜上方看的椭圆，一圈比一圈大），地面上一圈尘土被吹开，"
     "两侧几块碎石被震飞。**身体位置留空**（只画外面的环、脚下和两侧）。**左右对称**，6 帧。",
     EM + ", " + DU + ", " + ST,
     "A ROAR SHOCKWAVE, 6 frames, " + LR + ": round " + HER + ": 1 a gold flash ring on the ground under her (an "
     "ellipse 48 squares wide, 12 tall); 2-4 three concentric gold-orange SOUND-WAVE RINGS (ellipses, each 2 squares "
     "thick, cream-yellow on their front edge, deep orange behind) bursting outward from her one after another, the "
     "outer one reaching the cell edge; brown dust blown out low to both sides, a few stone chips tossed up; 5 the rings "
     "thinning; 6 the last ring fading. The middle of the cell (her body) stays EMPTY. " + MAGIC + ".",
     row(6, 72, 48) + CENTER),
    ("e_taunt", "技能 2「龙威咆哮」：被嘲讽，6 帧循环", "view_buffs `tft_terra_e_taunt`（跟随被嘲讽的人，头顶上方，z 3；左右对称）", "14 × 10",
     "被嘲讽的人头顶上：一个**金橙色发光的龙爪印 / 裂纹印记**（三道爪痕组成，像被巨龙盯上），一闪一闪地脉动。**左右对称**，6 帧循环。",
     EM + ", " + ST,
     "A TAUNT MARK, 6 looping frames, " + LR + ": above a unit's head, in the cell's upper part: a small glowing "
     "gold-orange mark of three claw slashes side by side (the middle one longest), 10 squares wide, inside a thin "
     "stone-grey cracked frame; frames 1-6 it pulses brighter and dimmer, a cream-yellow core on the brightest frames "
     "(every frame left-right symmetric). " + MAGIC + ".",
     row(6, 14, 10) + CENTER),
    ("e_shield", "技能 2「龙威咆哮」：岩石护盾，6 帧循环", "view_buffs `tft_terra_e_shield`（大表，跟随她，z 3；左右对称）", "72 × 48",
     "她的岩石护盾：身体**两侧**各浮着三四块灰绿色的岩石板（边缘金橙色描一圈光），上下缓缓浮动，地上一圈淡淡的金光。"
     "**身体位置留空**。**左右对称**，6 帧循环。",
     ST + ", " + EM + ", " + MO,
     "A FLOATING ROCK-SLAB SHIELD, 6 looping frames, " + LR + ": round " + HER + ": three or four grey-green stone "
     "slabs floating on EACH side of her (mirrored), each 6-9 squares tall with a 1-square gold-orange glowing rim and a "
     "fleck of moss, slowly bobbing up and down; a faint gold ring on the ground under her (an ellipse 48 squares wide, "
     "12 tall); frames 1-6 the slabs bobbing (every frame left-right symmetric). The middle of the cell (her body) stays "
     "EMPTY. " + MAGIC + ".",
     row(6, 72, 48) + CENTER),
    ("r", "大招「地震」：抬身时脚下裂开，4 帧", "view_effects `tft_terra_r`（跟随她，脚下地面，z 3；左右对称）", "56 × 14",
     "她抬起前身的一下：脚下地面**金橙色的裂纹一下亮起来**往两边蔓延，几缕尘土从裂缝里冒出来。**只在地面上**。**左右对称**，4 帧。",
     EM + ", " + DU,
     "THE GROUND WAKING, 4 frames, " + LR + ": on the GROUND only (the bottom of the cell), an ellipse about 54 "
     "squares wide and 12 tall under her: 1 a gold glint at the middle; 2 thin gold-orange glowing cracks running out "
     "to both sides (mirrored); 3 the cracks branching, cream-yellow at their joins, small brown dust puffs rising "
     "from them; 4 the glow dimming. " + MAGIC + ".",
     row(4, 56, 14) + CENTER),
    ("r_quake", "大招「地震」：一圈地震，7 帧", "view_effects `tft_terra_r_quake`（大表，每一踏放在她脚下的地面上，不跟随，z -1；左右对称）",
     "112 × 48",
     "每一踏掀起的一圈地震：以她为中心，**地面裂成一圈陨坑**（从斜上方看的大椭圆，宽是高的 3 倍），金橙色的裂纹从中间往外放射，"
     "椭圆外沿一圈**石块和土墙往上掀起**，碎石飞起、尘土翻滚，再落下去。**中间她站的地方留空**。**左右对称**，7 帧。",
     EM + ", " + ST + ", " + DU,
     "AN EARTHQUAKE RING, 7 frames, " + LR + ": round " + HER + ", on and just above the GROUND: 1 glowing gold-orange "
     "cracks shooting out from under her across an ellipse 104 squares wide and 34 tall, like a cracked crater seen from "
     "above; 2 the cracks reaching the ellipse's edge, a ring of broken earth lifting there; 3 along the WHOLE outer "
     "edge of the ellipse a low wall of grey-green rock slabs and brown earth heaving up (up to 10 squares high at the "
     "back and the sides, lower at the front), cream-yellow glow in the cracks; 4 stone chips flying up out of the ring "
     "(mirrored), brown dust rolling outward; 5 the slabs falling back, the dust spreading; 6 the cracks dimming, dust "
     "settling; 7 faint cracks only. The middle of the cell where she stands stays EMPTY (only cracks on the ground "
     "under her). " + MAGIC + ".",
     row(7, 112, 48) + CENTER),
    ("r_hit", "大招「地震」：被震到，5 帧", "view_effects `tft_terra_r_hit`（跟随被打中的人，z 3；左右对称）", "20 × 20",
     "被地震打中：脚下一下金光，一圈尖尖的石刺从地下往上戳出来又碎掉，尘土往两边扬。**左右对称**，5 帧。",
     ST + ", " + EM + ", " + DU,
     "A ROCK SPIKE ERUPTION, 5 frames, " + LR + ": round a unit standing in the middle (not drawn): 1 a gold-orange "
     "crack flash on the ground under it; 2 a ring of five sharp grey-green stone spikes jabbing up from the ground "
     "round it (mirrored, the middle one tallest, up to 16 squares), cream-yellow light at their bases; 3 the spikes "
     "cracking; 4 the spikes shattering into falling chips, brown dust puffing out to both sides; 5 dust settling. "
     + MAGIC + ".",
     row(5, 20, 20) + CENTER),
    ("r_res", "大招「地震」之后：岩甲发光，6 帧循环", "view_buffs `tft_terra_r_res`（大表，跟随她，z 3；左右对称）", "72 × 48",
     "地震之后她的岩甲：身体**两侧**和背上方飘起一点点金橙色的光尘往上升，脚下一圈金色的符文裂纹环慢慢亮暗（和护盾不一样：没有浮着的石板）。"
     "**身体位置留空**。**左右对称**，6 帧循环。",
     EM + ", " + ST,
     "A STONE ARMOUR GLOW, 6 looping frames, " + LR + ": round " + HER + ": small gold-orange light motes and tiny "
     "stone flecks rising slowly along BOTH sides of her and above her back (mirrored), cream-yellow on the brightest; a "
     "ring of glowing gold crack runes on the ground under her (an ellipse 52 squares wide, 13 tall) pulsing; frames 1-6 "
     "the motes drifting up and the ring breathing (every frame left-right symmetric; no floating slabs). The middle of "
     "the cell (her body) stays EMPTY. " + MAGIC + ".",
     row(6, 72, 48) + CENTER),
]
ICONS = [
    ("skill", "技能 1「裂地咬」图标", "skill_icons[0] `asset/tft/icons/tft_terra_skill`",
     ICON + ": a rock dragon's grey-green stone head from the side, jaws with cream stone fangs snapping shut low over "
               "cracked ground, gold-orange glowing cracks and flying stone chips under the bite."),
    ("skill2", "技能 2「龙威咆哮」图标", "skill_icons[1] `asset/tft/icons/tft_terra_skill2`",
     ICON + ": a rock dragon's head roaring upward with its jaws wide open, glowing yellow eye, three gold-orange "
               "sound-wave arcs coming out of its mouth, a grey-green rock slab shield behind it."),
    ("ult", "大招「地震」图标", "skill_icons[2] `asset/tft/icons/tft_terra_ult`",
     ICON + ": a huge clawed dark-brown dragon foot stomping down onto the ground, the ground split by glowing "
               "gold-orange cracks in a ring, grey-green rock slabs heaving up around it, dust."),
]
BIG_FX = ["e", "e_shield", "r_quake", "r_res"]
FLYING = ()

GROUPS = [
    ("a_hit q_hit r_hit (claws, the bite, the rock spikes)",
     ["malphite_base_r_rock_debris", "tft7_dragonearth_base_r_rocks", "malphite_base_z_seismicshard",
      "tft7_dragonearth_base_particles_1_12"]),
    ("r_quake r q_slow (the crater and its glowing cracks)",
     ["tft7_dragonearth_base_crater_mesh", "tft7_dragonearth_base_crater_mesh_glow", "tft6_colossus_cracks_glow_v04",
      "malphite_base_z_furrow"]),
    ("e (the roar's waves)",
     ["tft7_dragonearth_base_r_swoop", "tft7_dragonearth_base_air_swoosh", "malphite_base_p_swoop",
      "tft7_dragonearth_base_tendril_trail"]),
    ("e_shield r_res e_taunt (the shield, the armour glow)",
     ["malphite_base_p_shield_circle", "tft7_dragonearth_base_vertical_streaks", "tft7_malphite_base_idle_rocks",
      "tft7_dragonearth_base_smoke_64x64"]),
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
    """Terra at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"泰拉 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 泰拉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/terra_design.png`："
      "3/4 朝右、四条腿趴伏的大地巨龙：灰绿色的大块岩石甲板（几片苔藓绿）、黄色发光的眼睛、两排米白石牙；"
      "米白石骨 + 橙色翼膜的翅膀收在背上；红褐色的肚子、四条粗腿和深色大爪；细长的尾巴末端一簇灰绿石刺）。"
      f"泰拉在游戏里是**高清**的（每个游戏格子里约 1.45×1.45 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/terra_size.png`：泰拉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里泰拉自己的特效贴图（地震的陨坑和发光裂纹、碎石、声浪、护盾光）和熔岩巨兽的碎石"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **泰拉是大地巨龙，特效都是大地的力量**：灰绿色的石块和石板、裂开的地面里**发光的金橙色裂纹**（最亮处奶黄色）、"
      "褐色的尘土、一点点苔藓绿；不要火焰、不要蓝色紫色、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶黄色的芯，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**（石块可以有深色描边）。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `terra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `terra_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「岩爪」 | 前爪一拍、张嘴一咬 | `a_hit` |")
    a("| 被动「巨岩之躯」 | 受到的伤害永久减少 18%（不用画） | — |")
    a("| 技能 1 =「裂地咬」 | 低头扑上去猛咬一口，伤害吃护甲魔抗，被咬的减速 | `q_hit` · `q_slow` |")
    a("| 技能 2 =「龙威咆哮」 | 仰头咆哮，身边的敌人被嘲讽过来打她，自己套一层岩石护盾 | `e` · `e_taunt` · `e_shield` |")
    a("| 大招 =「地震」 | 抬身重踏三次，每一踏一圈地震；结束后岩甲发光，护甲魔抗大涨 8 秒 | `r` · `r_quake` · `r_hit` · `r_res` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（石块、石板可以用石头最深一档描边）。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("石头（她的岩甲）", STONE), ("金橙（发光的裂纹）", EMBER), ("土和尘", DUST),
                        ("苔藓", MOSS)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `terra_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `terra_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `terra_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `terra_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_terra_fx`（小的）和 `tft_terra_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- e 是她身上的一下（跟随她，z 4）；r 是她脚下地面的一下（跟随她，z 3）；r_quake 每一踏放在她脚下的地面上（不跟随，z -1）；"
      "e_shield、r_res 是她身上的 caster buff（z 3）；q_slow 是敌人脚下的 buff，e_taunt 是敌人头上的 buff（z 3）；"
      "a_hit、q_hit、r_hit 打在目标身上。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="terra_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/terra_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_terra.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "terra_design.png"))
    shape = size_sheet(os.path.join(out, "design", "terra_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"terra_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"terra_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
