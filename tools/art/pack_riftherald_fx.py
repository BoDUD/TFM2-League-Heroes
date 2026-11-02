#!/usr/bin/env python3
"""Build riftherald_fx_pack.zip: step 3 of the Rift Herald's (峡谷先锋) sprite - Codex draws its effects and its three
skill icons (the tft heroes' way).

    python tools/lol/fx_ref_riftherald.py            # the particle references -> C:/t/rh_work/fxref
    python tools/art/pack_riftherald_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name riftherald_fx_redo_pack]

The pack (C:/t/rh_work/fx/riftherald_fx_pack, zipped into --out, default D:/TFM2-Workshop/riftherald_packs) holds
PROMPTS.md (also written to assets/source/riftherald/PROMPTS_FX.md), design/riftherald_design.png (the approved idle
at 4x on its own squares), design/riftherald_size.png (it at game size, 4x, on the arena colour with the ground line,
a 10-px ruler and the base fighter) and refs/tft_fx_ref.png (its own set-16 particles, the Rift Herald's and Cho'Gath's
void - grey shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds
(tools/kit/build_riftherald.py, the user's OK 2026-11-02: top, the proposed kit): view_effects a_hit, q_spin, q_hit,
e_hit, e_crash, r_roar, r_slam; view_buffs q_slow, e_stun, r_armor. Plus the three skill icons.
Its colours: the magenta void glow of its eyes and shell spots, its blue-violet crystal shell, its gold tusks and thorns,
its dark plum body.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture); it has no flying one.
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

TMP = "C:/t/rh_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "riftherald", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "riftherald", "hd")
NAME = "riftherald_fx_pack"
PPU = 2.0

VOID = "#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260"            # its glowing eyes and shell spots: the void
SHELL = "#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52"           # its blue-violet crystal shell
GOLD = "#FFF2A6, #EAC254, #B28A32, #6C4E1C"                     # its tusks, thorns and claw tips
PLUM = "#7A5084, #563460, #3A203F, #22122A"                     # its dark plum body
DUST = "#B4A8BC, #847494, #5A4C68, #362C42"                     # the dust and rock it throws up
VO = f"a void magenta ramp ({VOID})"
SH = f"a crystal shell ramp ({SHELL})"
GO = f"a gold ramp ({GOLD})"
PL = f"a dark plum ramp ({PLUM})"
DU = f"a violet dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its "
         "shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat "
         "shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams")
HIM = ("the beast stands in the middle, not drawn: about 52 squares wide and 44 tall from its shell's top to the ground, "
       "hunched under a big domed shell, its face and pincers at the front right")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little "
        "gold thorn corners, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art "
        "at 2 px a square (32 x 32 squares), chunky and readable at 64 px")
GROUND = "a flat ellipse on the ground seen from above at a slant (about 3 times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「裂钳」：钳爪砸中，4 帧", "view_effects `tft_riftherald_a_hit`（跟随目标，z 2；左右对称）", "16 × 14",
     "钳爪砸中：一下洋红色的闪光，**两道交叉的粗爪痕**（像蟹钳夹过），几块蓝紫晶体碎片和金色火星往两边飞。**左右对称**，4 帧。",
     VO + ", " + SH + ", " + GO,
     "A PINCER STRIKE, 4 frames, " + LR + ": 1 a small hot pink-white flash 5 squares across; 2 TWO thick curved CLAW "
     "GASHES crossing in an X, 10 squares tall, magenta with pale pink cores, small blue-violet crystal chips and gold "
     "sparks flying out to both sides; 3 the gashes fading to dark violet, the chips falling outward; 4 the last chips "
     "and sparks. " + MAGIC + ".",
     row(4, 16, 14) + CENTER),
    ("q_spin", "技能 1「回旋横扫」：转一圈扫过地面，6 帧",
     "view_effects `tft_riftherald_q_spin`（大表，它脚下的地面，z -1，不跟随；左右对称）", "76 × 28",
     "它原地转一圈：**脚下一圈洋红色的横扫弧光贴着地面转开**，像钳爪和尾巴扫出的刀光，夹着蓝紫晶体碎屑和尘土往外甩，最后散成一圈尘土。"
     "**中间它站的地方留空**。**左右对称**（逐帧左右对称：左右两边的弧同时扫出），6 帧。",
     VO + ", " + SH + ", " + DU,
     "A GROUND SWEEP, 6 frames, " + LR + ": " + GROUND + " round " + HIM + " (leave its feet's middle empty): 1 two short "
     "magenta SWIPE ARCS starting at its sides on the ground; 2-3 the arcs sweeping out round both sides into a full "
     "ring 70 squares wide and 22 tall, thick bright magenta with pink-white leading edges, small blue-violet crystal "
     "chips and dust flung out of it; 4 the ring at full size, beginning to break; 5 the ring breaking into dark violet "
     "arcs and a ring of violet dust; 6 the last dust. " + MAGIC + ".",
     row(6, 76, 28) + CENTER),
    ("q_hit", "技能 1「回旋横扫」：被扫中，4 帧", "view_effects `tft_riftherald_q_hit`（跟随目标，z 3；左右对称）", "14 × 12",
     "被扫中：一道**横着的洋红扫痕**划过身体中间，两边飞出晶体碎屑。**左右对称**，4 帧。",
     VO + ", " + SH,
     "A SWEEP HIT, 4 frames, " + LR + ": 1 a flat horizontal magenta SLASH 12 squares wide across the middle, a pink-"
     "white core; 2 the slash at full brightness, small blue-violet crystal chips flying out to both sides; 3 the slash "
     "fading to dark violet, chips falling; 4 the last chips. " + MAGIC + ".",
     row(4, 14, 12) + CENTER),
    ("q_slow", "技能 1「回旋横扫」：减速，6 帧循环", "view_buffs `tft_riftherald_q_slow`（跟随被减速的人，脚下，z 3；左右对称）",
     "18 × 8",
     "被减速的人脚下：**一圈贴地的紫色虚空小触须**从地上冒出来缠着脚，几颗洋红光点往上飘。**中间人站的地方留空**。**左右对称**，6 帧循环。",
     VO + ", " + PL,
     "A VOID DRAG, 6 looping frames, " + LR + ": " + GROUND + " 16 squares wide under a unit's feet (its feet's middle "
     "empty): small dark plum and magenta VOID TENDRILS 2-4 squares tall curling up from the ground round the feet "
     "(mirrored), two or three single magenta motes rising; frames 1-6 the tendrils swaying in and out in turn and the "
     "motes rising. Small. " + MAGIC + ".",
     row(6, 18, 8) + CENTER),
    ("e_hit", "技能 2「虚空冲锋」：被撞中，5 帧", "view_effects `tft_riftherald_e_hit`（跟随被撞的人，z 3；左右对称）", "22 × 20",
     "被冲锋撞中：**一下很重的撞击**：洋红色的冲击星爆开，一圈蓝紫晶体碎片和碎石往外飞。**左右对称**，5 帧。",
     VO + ", " + SH + ", " + DU,
     "A RAM IMPACT, 5 frames, " + LR + ": 1 a hot pink-white flash 6 squares across; 2 a jagged magenta IMPACT STAR 18 "
     "squares across with a pale core, blue-violet crystal shards and grey rock chips bursting out; 3 the star breaking "
     "into shards flying outward and down; 4 the shards and a little dust falling; 5 the last dust. " + MAGIC + ".",
     row(5, 22, 20) + CENTER),
    ("e_crash", "技能 2「虚空冲锋」：冲锋撞停的地面，6 帧",
     "view_effects `tft_riftherald_e_crash`（大表，它撞停的地方，地面上，z -1，不跟随；左右对称）", "56 × 26",
     "冲锋撞停的地方：**地面裂开几道发洋红光的裂缝**，一圈尘土和碎石往两边喷起再落下，最后留一点发光的裂缝慢慢熄灭。**左右对称**，6 帧。",
     VO + ", " + DU,
     "A CRASH LANDING, 6 frames, " + LR + ": " + GROUND + ": 1 a flat violet DUST BURST along the ground 30 squares wide; "
     "2 a ring of dust and grey-violet rock chunks thrown up and out to both sides, 50 squares wide, and short glowing "
     "magenta CRACKS opening in the ground from the middle; 3 the dust at its highest, the cracks at full glow; 4 the "
     "rocks falling back, the dust settling; 5 a thin dust ring and the cracks dimming to dark violet; 6 the last faint "
     "cracks. " + MAGIC + ".",
     row(6, 56, 26) + CENTER),
    ("e_stun", "技能 2「虚空冲锋」：被晕眩，6 帧循环", "view_buffs `tft_riftherald_e_stun`（跟随被晕的人，头顶上方，z 3；左右对称）",
     "16 × 8",
     "被撞晕的人头顶：**三颗小小的洋红色虚空眼睛绕圈转**（像峡谷先锋甲壳上的小眼睛）。**左右对称**（逐帧对称），6 帧循环。",
     VO + ", " + SH,
     "A STUN RING, 6 looping frames, " + LR + ": above a unit's head, " + GROUND + " 14 squares wide: three small "
     "magenta VOID EYES (a 3x2 diamond each, a pale pink centre, like the eyes on its shell) circling round it; every "
     "frame left-right symmetric (one eye in front at the middle, two at the sides, the far ones a step darker and "
     "smaller), the eyes blinking in turn. " + MAGIC + ".",
     row(6, 16, 8) + CENTER),
    ("r_roar", "大招「扭曲护甲」：长啸变大，6 帧", "view_effects `tft_riftherald_r_roar`（大表，跟随它，z 3；左右对称）",
     "68 × 56",
     "它直立长啸、身体变大：**从它身上往外扩散两三圈洋红色的声波环**，几块蓝紫晶体碎片往外飞。"
     "**它的身体位置留空**，只画身体外面一圈和边缘。**左右对称**，6 帧。",
     VO + ", " + SH,
     "A VOID ROAR, 6 frames, " + LR + ": round " + HIM + " (rearing up, about 60 squares tall in this frame): 1 a thin "
     "magenta glow along the body's outline; 2-4 two or three jagged magenta SOUND RINGS expanding outward from the body "
     "(each an open ring broken into thick arcs, pink-white leading edges), small blue-violet crystal shards flying out "
     "with them; 5 the rings reaching the cell's edges and thinning to dark violet; 6 the last arcs at the edges. INSIDE "
     "stays EMPTY (its body). " + MAGIC + ".",
     row(6, 68, 56) + CENTER),
    ("r_slam", "大招「扭曲护甲」：猛击地面，7 帧",
     "view_effects `tft_riftherald_r_slam`（大表，砸的地方，地面上，z -1，不跟随；左右对称）", "88 × 34",
     "两只钳爪一起砸地：**一个大的洋红冲击环在地上炸开**，地面裂成放射状的发光裂缝，碎石和蓝紫晶体碎块往上喷，最后裂缝慢慢熄灭。**左右对称**，7 帧。",
     VO + ", " + SH + ", " + DU,
     "A VOID SLAM, 7 frames, " + LR + ": " + GROUND + ": 1 a hot pink-white flash 10 squares across on the ground; 2 a "
     "thick magenta SHOCK RING 40 squares wide bursting out, glowing magenta CRACKS radiating from the middle; 3 the ring "
     "84 squares wide and 30 tall, rock chunks and blue-violet crystal shards thrown up above it; 4 the ring thinning and "
     "breaking into arcs, the chunks at their highest; 5 the chunks falling, a ring of violet dust; 6 the dust settling, "
     "the cracks dimming; 7 the last faint cracks. " + MAGIC + ".",
     row(7, 88, 34) + CENTER),
    ("r_armor", "大招「扭曲护甲」：护甲，6 帧循环", "view_buffs `tft_riftherald_r_armor`（大表，跟随它，z 3；左右对称）",
     "64 × 52",
     "扭曲护甲生效的 4 秒：**它身体外面浮着一圈蓝紫晶体甲片**（像它甲壳的甲片，一片片围在身体两侧和头顶），甲片中间的洋红小眼睛一闪一闪，"
     "偶尔一道洋红光沿着甲片边缘流过。**它的身体位置留空**，只画外面一圈。**左右对称**，6 帧循环。",
     SH + ", " + VO,
     "A WARP ARMOR, 6 looping frames, " + LR + ": round " + HIM + ": a loose ring of floating faceted BLUE-VIOLET CRYSTAL "
     "PLATES (6-8 squares each, like its shell plates, each with a small magenta diamond) hovering just outside its "
     "outline - along both sides and over the top (mirrored); frames 1-6 the plates bobbing a square up and down in turn, "
     "their magenta diamonds blinking, a magenta glint running round the ring's edges. INSIDE stays EMPTY (its body). "
     + MAGIC + ".",
     row(6, 64, 52) + CENTER),
]
ICONS = [
    ("skill", "技能 1「回旋横扫」图标", "skill_icons[0] `asset/tft/icons/tft_riftherald_skill`",
     ICON + ": a big curved magenta sweep arc going round in a circle like a whirl, a blue-violet crab pincer at its head "
            "and a tail at its end, crystal chips flying."),
    ("skill2", "技能 2「虚空冲锋」图标", "skill_icons[1] `asset/tft/icons/tft_riftherald_skill2`",
     ICON + ": a domed blue-violet crystal shell with magenta spots charging to the right, speed lines and a magenta "
            "impact star where it rams, two golden tusks at its front."),
    ("ult", "大招「扭曲护甲」图标", "skill_icons[2] `asset/tft/icons/tft_riftherald_ult`",
     ICON + ": a roaring void beast's face under a domed crystal shell, two big golden tusks, glowing magenta eyes, "
            "magenta sound rings around it."),
]
BIG_FX = ["q_spin", "e_crash", "r_roar", "r_slam", "r_armor"]
FLYING = ()

GROUPS = [
    ("a_hit q_spin q_hit (the swipes)",
     ["tft16_riftherald_base_fistswipe", "spinattack_swipe", "sru_riftherald_spinattack_swipespikes",
      "sru_riftherald_spinattack_arms", "sru_riftherald_directional_flash"]),
    ("e_hit e_crash (the charge)",
     ["sru_riftherald_dash_cone", "sru_riftherald_dash_wake", "sru_riftherald_rock_debris", "sru_riftherald_smoke_dust",
      "sru_riftherald_pebbles_4x4"]),
    ("r_roar r_slam (the slam)",
     ["tft16_riftherald_base_crackglows_center", "tft16_riftherald_base_riftherald_grounddecal",
      "chogath_base_w_cas_soundring_2x2", "sru_riftherald_relic_lightcracks", "sru_riftherald_death_void_bits_2x2"]),
    ("q_slow e_stun r_armor (the void)",
     ["sru_riftherald_buff_tentacles_light", "sru_riftherald_eye_wisps", "sru_riftherald_relic_pieces_pink",
      "sru_riftherald_portalring", "chogath_base_r_tar_voidwisps"]),
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
    """The beast at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"峡谷先锋 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 峡谷先锋：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/riftherald_design.png`："
      "3/4 朝右、弓着背缩在大圆顶甲壳下的虚空巨兽：蓝紫色晶体甲片拼成的甲壳，每块甲片中间一个洋红小菱形，前沿一圈金色小尖刺；"
      "深紫色身体、两条短粗后腿、细长卷尾；两只大蟹钳；脸在甲壳前沿下面，洋红眼睛、金色獠牙）。"
      f"它在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/riftherald_size.png`：它缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是它自己的特效贴图（金铲铲第 16 赛季的钳爪刀光、砸地裂缝，召唤师峡谷峡谷先锋的旋转攻击、冲锋、碎石、虚空）"
      "和科加斯的虚空声波（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **峡谷先锋是虚空巨兽，特效都是它的味道**：**洋红色的虚空光**（它的眼睛和甲壳上的小眼睛）、**蓝紫色的晶体碎片**（像它的甲片）、"
      "一点**金色火星**（像它的獠牙）、**灰紫色的碎石和尘土**；又重又有力；不要闪电、不要火焰、不要绿色、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每道虚空光都有最亮一档的粉白色芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**（晶体碎片和碎石可以有深色的边）。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 交付方式：")
    a(">   - 每张生成后按格子取回（每格取多数颜色）。")
    a(">   - 交付 8 倍的 `riftherald_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。")
    if n_ic:
        a(">   - 图标交付 `riftherald_icon_<名字>.png`（64×64）。")
    a(">   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。")
    a(f">   - 都放在 `outputs/{NAME.replace('_pack', '')}/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。")
    a("> - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「裂钳」 | 钳爪举起往前砸 | `a_hit` |")
    a("| 被动「虚空甲壳」 | 身边每有一名敌方英雄，受到的伤害少一点（不需要画面） | — |")
    a("| 技能 1「回旋横扫」 | 原地转一圈，扫过身边一圈的敌人：伤害 + 减速 | `q_spin` · `q_hit` · `q_slow` |")
    a("| 技能 2「虚空冲锋」 | 直立蓄力，翻身用甲壳冲撞：沿途撞开，撞到的英雄晕眩 | `e_hit` · `e_crash` · `e_stun` |")
    a("| 大招「扭曲护甲」 | 长啸变大，猛击前方地面；4 秒内伤害减免 | `r_roar` · `r_slam` · `r_armor` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空洋红（它的眼睛和甲壳上的小眼睛）", VOID), ("晶体甲壳（蓝紫）", SHELL), ("金色（獠牙、尖刺、爪尖）", GOLD),
                        ("身体（深紫）", PLUM), ("尘土和碎石", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `riftherald_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `riftherald_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `riftherald_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `riftherald_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_riftherald_fx`（小的）和 `tft_riftherald_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称（没有飞行弹道）。")
    a("- a_hit、q_hit、e_hit 跟随目标；q_spin 在它脚下的地面（caster 画面，不跟随），e_crash 在它冲锋撞停的地方（caster 画面），"
      "r_slam 在它砸的地方（ViewEffect，地面）；r_roar 是它身上的 caster 画面；r_armor 是它身上的 buff；q_slow、e_stun 是敌人身上的 buff。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="riftherald_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/riftherald_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_riftherald.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "riftherald_design.png"))
    shape = size_sheet(os.path.join(out, "design", "riftherald_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"riftherald_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"riftherald_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
