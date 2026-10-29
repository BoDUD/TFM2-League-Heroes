#!/usr/bin/env python3
"""The PPU heroes brought to one look - league_zeri's (2026-10-13).

    python tools/art/ppu_restyle.py --hero zeri [--hero karma ...] [--preview DIR] [--set key=value ...]

The user: 「这几个ppu英雄会导致人物体型很细 不协调 和其他像素风格的英雄不太搭」「太高清了看上去像动画贴图」, then on Zeri's
sample (her own dense art, head scaled up evenly, the body below the neck wider and shorter): 「泽丽完美」「泽丽是榜样
其他英雄都按照这种思路来改就行了」「画风要统一」. Every hero's dense frames are made from its current ones (kept in
assets/source/ppu/orig/ on the first run, read from there afterwards), in up to four steps (RESTYLE has each hero's):

1. proportions (`head`, `wide`, `short`): in every frame the head is found (the idle's face matched in the frame) and
   everything above the neck is scaled evenly by `head` round the neck, everything below it `wide` times wider round
   the pivot column and `short` times as tall up from the ground row (the soles stay); a band of `band` dense rows
   round the neck goes smoothly from one to the other (nothing tears). A lying frame (FRAMES: "lie", the head's side
   and its neck point) does the same along x: the head scaled round the neck, the body `short` times as long round the
   pivot and `wide` times as thick up from the ground. `ring` (Karma's halo): the halo's pixels are taken out first
   and put back `ring` times their size above the head where the warp sends them. Nearest on the dense grid.
2. size (`grow`): everything scaled evenly round the pivot and the ground row (league_corki: 「飞机像泽丽那样变大点」).
3. pixel density (`ppu`): the frames brought to a coarser grid - `ppu` squares a game pixel - each square the commonest
   colour of the dense pixels under it (a square a third or more outline takes the outline, so eyes and lines stay);
   the hero's PPU changes to `ppu` (ppu_hd.py PPU, addons/league_main/src/hd.rs HEROES).
4. outline (`edge`): the outer outline grown by `edge` squares.
Frames that come out bigger grow alike at both ends (the pivot kept, ppu_hd.py's drawn-strip rule); when an idle frame
would be wider than PPU x its 1x frame (the DLL needs hd_idle exactly that wide), the 1x idle frames get clear columns
at both sides. The champion_view face point moves with the head. Then `python tools/art/ppu_hd.py --hero <hero>`.
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, signal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
import strips as G  # noqa: E402
from pixel_down import despeckle, edge_colour, palette_of, pixelate, scale_fx, sizes_of  # noqa: E402,F401
import pixel_down as D  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ppu")
ORIG = os.path.join(SRC, "orig")
MOD = os.path.join(ROOT, "league")
FEET = 11.5                         # 1x pixels from the pivot down to the soles' bottom edge
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
WARPS = {}                          # (hero, tag, frame) -> the Warp used (the face point follows the idle's)

KARMA_RING = [(62, 138, 103), (92, 195, 142), (35, 95, 75), (129, 209, 157), (14, 52, 46), (5, 26, 30)]
# the PPU every hero's frames in assets/source/ppu/orig are drawn at (what its own tool writes there: rig_braum.py,
# rig_mordekaiser.py, rig_kassadin.py, rig_corki_hd.py, ppu_zeri.py, ppu_gragas.py, import_ppu_strips.py)
ORIG_PPU = {"zeri": 3, "karma": 3, "braum": 2.881, "mordekaiser": 5, "corki": 5, "kassadin": 3.622, "ashe": 5.4571,
            "vladimir": 2, "yasuo": 3, "garen": 3, "gragas": 2, "irelia": 2, "soraka": 3, "nidalee": 3.8313,
            "nilah": 2.5, "kindred": 154 / 34, "malzahar": 1.38, "milio": 2.2, "jayce": 1.5, "elise": 1.8, "katarina": 1.5,
            "tahmkench": 1.2, "kalista": 1.4, "drmundo": 1.5, "pantheon": 1.5, "orianna": 2.25, "aphelios": 1.5, "rell": 1.5, "urgot": 1.2, "reksai": 1.58, "swain": 1.5, "nasus": 1.2, "renata": 1.5, "anivia": 1.2, "jarvaniv": 1.5, "ziggs": 1.5, "maokai": 1.5, "gangplank": 1.5, "wukong": 1.53, "cassiopeia": 1.3, "akshan": 1.61, "poppy": 1.3, "volibear": 1.2, "rammus": 1.2,
            **{h: 1.5 for h in ('morgana', 'nami', 'janna', 'jax', 'xinzhao')}, "yunara": 1.5, "kaisa": 1.45, "camille": 1.5, "fiora": 1.5, "leblanc": 2.0, "darius": 1.45, "caitlyn": 1.45, "riven": 1.5, "zoe": 1.5, "quinn": 2.0, "yuumi": 1.5, "powder": 1.75, "chogath": 1.2, "karthus": 1.5, "vex": 1.5, "zyra": 1.7, "graves": 1.5, "warwick": 1.5, "gnar": 1.5, "sylas": 1.2, "mel": 1.5, "velkoz": 1.5, "shyvana": 1.5, "ornn": 1.5, "naafiri": 1.5, "xerath": 1.55, "heimerdinger": 1.5, "neeko": 2.5, "ksante": 1.5, "udyr": 1.5, "qiyana": 1.5, "hwei": 1.5, "ivern": 1.5, "illaoi": 1.5, "varus": 1.35, "aurora": 2.25, "nunu": 1.37, "azir": 1.5, "zac": 1.5, "jinx": 2.2, "lux": 2.2, "singed": 1.39, "belveth": 1.75, "taliyah": 1.75, "aurelionsol": 1.75, "sejuani": 2.0, "ahri": 2.2, "twitch": 2.2, "annie": 2.2, "kled": 2.0, "yorick": 1.75, "gwen": 2.84, "ambessa": 2.0, "rumble": 1.75, "trundle": 2.0, "samira": 2.84, "locke": 2.0, "draven": 2.2, "skarner": 1.75, "zaahen": 1.75, "alune": 2.0, "silco": 2.0, "maddie": 1.5, "loris": 2.0, "kobuko": 2.0, "vander": 2.0, "violet": 2.0, "krug": 2.0, "aoshin": 2.0, "scar": 2.0, "renni": 2.0, "smeech": 2.4, "leesin": 2.1, "vayne": 2.55, "lucian": 2.02, "rengar": 59 / 40, "syndra": 78 / 42, "akali": 72 / 40, "sivir": 81 / 36, "tristana": 87 / 34, "zed": 65 / 40}
# face: (row0, row1, col0, col1) of the face to match in the idle's first dense frame; neck: (col, row) there
RESTYLE = {
    "zeri": dict(face=(25, 41, 22, 42), neck=None, neck_row=35, head=1.3, wide=1.45, short=0.88, band=2, edge=1, face_to=(-1, -33)),
    # 「卡尔玛太壮了 还需要调」「头上的光环太大」「卡尔玛的像素还可以降一降吧？」
    "karma": dict(face=(38, 62, 33, 58), neck=(45, 64), head=1.2, wide=1.25, short=0.92, band=3, edge=1,
                  ring=0.6, ring_colours=KARMA_RING, ring_rows=40, ppu=2.2, max_err=2200, outline=(15, 3, 16)),
    # 「布隆铁男可以在壮点 太细了」 (their heads are Codex's own in many frames - not found reliably - so the body only,
    # every frame alike). Then, next to Alistar: 「铁男是你压缩的太厉害了吗 为什么模型看起来小啊 牛头那种就看起来很大 布隆
    # 也有这个看起来小的问题」「铁男再游戏里还是过于高清」 - picked from a size sheet (「按照你的建议选吧」): Braum 105 %
    # (hd.rs SIZES; 1.89 squares a game pixel), Mordekaiser 115 % at PPU 2.0 (1.74). Drawn bigger by league.dll round the
    # frame's centre, so the frames are lifted to keep the soles on the ground - by whole squares of the new grid (the
    # grid runs through the pivot: Braum's squares come out exactly as before, 4 rows higher). Braum's orig frames sit
    # rig_braum.py's SHIFT 4 lower (its 90 %): 11.5 x 2.881 x (1 + 4 / 33.13 - 1 / 1.05) = 5.6 orig rows = 3.8 squares
    # -> 4; Mordekaiser's (rig_mordekaiser.py SIZE 1.00, FEET 11): 11 x 5 x (1 - 1 / 1.15) = 7.2 orig rows = 2.9 -> 3.
    # The face points scale about the soles (champion_view: (7, -35) x 1.05 / 0.90, (1, -27) x 1.15)
    # then 「铁男感觉还是没泽丽那么像素啊」「飞机 布隆也是」「卡萨丁也是」: flat pixel art (crisp, picked from a preview:
    # 16 colours + lines; Mordekaiser keeps his teal glow as drawn and his dark armour unstretched -
    # 「铁男的眼睛完全看不到了」)
    # then 「铁男和布隆游戏里偏大了」: Mordekaiser 100 %, Braum 95 % (hd.rs SIZES, picked from a true-scale sheet) - the
    # frames as they were, moved down by whole squares after the downscale (lift_sq): 11 x 2.0 x (1 / 1.00 - 1 / 1.15)
    # = 2.9 -> 3, 11.5 x 1.98 x (1 / 0.95 - 1 / 1.05) = 2.3 -> 2; faces x 1.00 / 1.15 and x 0.95 / 1.05 about the soles
    # then (game 0.6.4, 2026-10-14) 「铁男模型太小」「铁男到110%吧」: Mordekaiser 110 % - 11 x 2.0 x (1 / 1.10 - 1 / 1.15)
    # = 0.9 -> 1 square down from the 115 % frames, face (1, -27) x 1.10 about the soles
    "braum": dict(body_only=True, head=1.0, wide=1.2, short=0.94, edge=0, ppu=1.98, crisp={},
                  lift=4 * 2.881 / 1.98 - 1e-6, lift_sq=-2, face_to=(2, -40)),  # (a hair under: the pivot's row keeps its square)
    # 「铁男的走路步伐感觉有点大啊」: Codex's run had the soles 42 and 47.5 game px apart in its two striding frames (the
    # idle's 31), brought together here (narrow) until 2026-10-22; the run rig_mordekaiser.py draws since (「铁男的走路也要
    # 改」: League's walk on the stand's own leg armour) keeps them within RUN_SPAN itself. palette_fit: the crisp palette
    # still fit on Codex's run as it was (its four frames, unnarrowed), so no other frame of his changes colour
    "mordekaiser": dict(body_only=True, head=1.0, wide=1.25, short=0.94, edge=0, ppu=2.0, lift=3 * 5 / 2.0, lift_sq=-1,
                        palette_fit={"run": "mordekaiser/codex_run/run_palette_orig"},
                        crisp=dict(contrast=1.0, keep="teal"),
                        face_to=(-1, -42)),   # helmet and eyes ((1, -30) cropped his chest, 2026-10-20)
    # 「飞机像泽丽那样变大点」
    "corki": dict(grow=1.2, edge=1, ppu=2.2, crisp={}, face_to=(3, -33)),
    # 「卡萨丁可以降低点像素之类的 ... 画风要统一」 (2.2 at his 110 %)
    # 「刀妹和卡萨丁感觉在游戏里偏大啊」: 100 % (hd.rs SIZES). rig_kassadin.py drew his frames RAISE 4 orig rows higher
    # for its 110 %; lowered 4 x 2.42 / 3.622 = 2.7 -> 3 squares after the downscale
    "kassadin": dict(edge=0, ppu=2.42, crisp=dict(keep="mask_face"), lift_sq=-3, face_to=(1, -36)),
    # Ashe: the 11 frames her first pack never finished (Codex's image service stopped) redrawn in the completion pack
    # dist/ppu_packs/ashe_fix (pack_ppu_strips.py --name ashe_fix), imported with import_ppu_strips.py --hero ashe
    # --delivery <it> --fill-from-sheet
    "ashe": dict(edge=1, ppu=2.2, fix={
        # the 11 frames of the completion pack (2026-10-13, 「修复寒冰」) came back 3-14 % small again:
        # each brought to 0.99 of its 1x frame's height, bow left out, like the frames around it
        ("run", 6): 1.08, ("q_attack", 0): 1.021, ("skill", 0): 1.10, ("skill", 2): 1.125, ("skill", 4): 1.151,
        ("skill", 5): 1.076, ("skill2", 0): 1.031, ("ult", 3): 1.076, ("ult", 7): 1.021, ("dead", 1): 1.112}),
    # 「吸血鬼我觉得只要降低点像素就好了」
    "vladimir": dict(edge=1, ppu=1.8, face_to=(-2, -34)),
    # 「其他英雄也差不多2.2」「画风要统一」
    "yasuo": dict(edge=0, ppu=2.2),
    # 「盖伦在游戏里还是他说 太小 像素太高」: 12 % bigger (37 -> 41 rows, Darius's 42), 1.9 squares a game pixel
    # 「盖伦也要调一下吧 像素」: the flat pixel art too, his face kept as drawn (the lines pass made his eyes a black band)
    "garen": dict(grow=1.12, edge=0, ppu=1.9, crisp=dict(keep="face")),
    # 2.2 at his 80 %
    # 「酒桶可以稍微放大点吧 现在也太小了」: 90 %, then 「还是太小啊」: 100 % (hd.rs SIZES). His orig frames sit ppu_gragas.py's
    # SHIFT 6 lower (its 80 %): 23 x (1 + 6 / 23 - 1 / 1.00) = 6 orig rows = 5.3 squares -> 5, lifted after the downscale
    # (lift_sq: pixels unchanged)
    # then 「是整体这个模型看着很矮 很小 应该是像素没降够的原因」: coarser, 1.45 squares a game pixel (picked from a
    # preview); then back to 90 % (「感觉又太大了？」 - the 100 % came from a preview GIF that drew him at 80 %): his frames
    # sit 3.4 orig rows low for it = 2.5 of these squares -> 2 (soles 11.8 game px under the pivot; 3 put them at 11.2)
    "gragas": dict(edge=0, ppu=1.45, lift_sq=2, face_to=(2, -40), shared_palette=True),
    # 「刀妹感觉是完美的不用改」, then 「刀妹在游戏里看着也太小了啊」 (「就用1.15」): drawn 15 % bigger by league.dll
    # (hd.rs SIZES 1.15), not resampled - the area resample darkened her navy hair and suit (「刀妹有点怪啊」); every frame
    # lifted 3 dense rows so the soles stay on the ground under the growth round the frame's centre (11.5 x 2 x
    # (1 - 1 / 1.15) = 3.0); her pixels untouched. Her face point: PR #246's (1, -38) on her head at 100 % (the old (0, -31)
    # cropped her chest), x 1.15 about the soles
    # then 「刀妹和卡萨丁感觉在游戏里偏大啊」: 105 % - lifted 11.5 x 2 x (1 - 1 / 1.05) = 1.1 -> 1 row
    "irelia": dict(lift=1, edge=0, face_to=(1, -40)),
    # 「下一个可以修正索拉卡」: Codex's PPU 3 redraw (design + 46 frames, the design brought to the actions' size at import),
    # to Zeri's look: Codex drew every head anew (none matches the idle's face), so the body only, every frame alike
    # (Braum's way): 1.25 wide, 0.92 tall, 2.2 squares a game pixel. Then 「稍微变大点」: drawn 110 % by league.dll (hd.rs
    # SIZES), the frames lifted 3 squares of the new grid (her restyled hooves sat a square low; 11.5 x 2.2 x (1 - 1 / 1.1) = 2.3 more) so the hooves stay on the
    # ground; face (6, -31) x 1.1 and the lift -> (7, -35)
    # Then flat pixel art like the others (crisp; 布隆's note on the user's new standard): her face kept as drawn (her
    # skin is blue - pixel_down KEEP "soraka": the light blue skin in the top third) and her thin gold staff (the
    # lines pass turned its 2-3 squares wide shaft black)
    "soraka": dict(body_only=True, head=1.0, wide=1.25, short=0.92, edge=1, ppu=2.2, lift=3 * 3 / 2.2,
                   face_to=(5, -32), crisp=dict(keep="soraka")),   # face point on her restyled face (#257)
    # league_nidalee (#97, 「按泽丽标准」): the huntress's head up, her body wider and shorter (Karma's way); the cougar keeps
    # its shape (FRAMES "none": already chunky) and only comes to the coarser grid
    # picked from three (「A 头 1.2 / 宽 1.3 / 矮 0.9」); max_err 8000: her Codex-drawn heads differ a little from the design's
    # and were missed at 1500 (the head then kept its size beside the idle's grown one); the lying and turned frames below
    # Then 「豹子形态太大了」「还有豹子的像素太高」: the cougar (tags c_*) picked from a true-scale sheet at 75 % (61 x 31 game
    # px standing -> 46 x 23, Rengar 41 x 40) on a coarser grid, 1.65 squares a game px (coarse: drawn, outlined and
    # crisped on that grid, then brought to the sheet's 2.2 by nearest - squares of one or two; the palette from the
    # frames as they were, so the human's stay as they are)
    "nidalee": dict(face=(33, 59, 51, 78), neck=(65, 61), head=1.2, wide=1.3, short=0.9, band=3, edge=1, ppu=2.2,
                    max_err=8000, crisp=dict(keep="head"), coarse=dict(prefix="c_", size=0.75, grid=1.65), face_to=(3, -36)),
    # league_nilah (#99, 「按泽丽标准」): drawn at the look already (Codex's picture read back square for square, PPU 2.5 -
    # the user's 「保留 99 格，PPU 2.5」), so only the outer outline grown to the others' two squares (about a game pixel;
    # hers was one) and every frame lowered for her 90 % (hd.rs SIZES, 「模型别太大」): 11.5 x 2.5 x (1 / 0.9 - 1) = 3.2 -> 3
    # squares; the face point at her crown (the 1x sheet's 40 px) x 0.9; fx: her whips and the dash's wake
    # (tools/art/fx_nilah.py, laid out by rig_nilah.py in orig/nilah_<tag>.over.png / .under.png) put on after the outline.
    # 2026-10-14 the user: 「尼拉好像也太高清了」 - from a sheet of densities picked 2.2 squares a shown game pixel (Ashe's,
    # Nidalee's): ppu 1.98 at her 90 % (it was 2.5 / 0.9 = 2.78); her whips brought to the same grid (scale_fx)
    "nilah": dict(edge=1, lift_sq=-3, face_to=(-1, -36), fx=True, ppu=1.98),
    # league_kindred (#101): Codex's picture B read back square for square (rig_kindred.py: 154 squares from the mask's
    # ear tips to the hooves = the 34 game rows the user picked, 「模型还得缩小」), brought to Zeri's density - her 3.0 at
    # 105 %, 2.86 squares a game pixel (the user: 「泽丽密度（最后统一重做）」); no proportion change (the approved design);
    # the outer outline grown to about a game pixel. 2026-10-14 the user: 「有点太高清了？降点像素」 - from a sheet of
    # densities picked 2.2 (Ashe's, Nidalee's, Yasuo's)
    "kindred": dict(ppu=2.2, edge=1),
    # league_malzahar (#103): Codex's drafts cut to the design's grid at the user's density (tools/art/
    # import_malzahar_strips.py, rig_malzahar.py: 2.2 first, then 「像素有点高 降低点需要」 -> 1.2 squares a shown game pixel
    # picked from a sheet = PPU 1.38 at his 115 %), so no proportion or density change here; the outer outline grown a
    # square like the others; drawn 115 % by league.dll (hd.rs SIZES) round the frame's centre, so every frame lifted
    # 11.5 x 1.38 x (1 - 1 / 1.15) = 2.1 -> 2 rows (the ground row stays on the ground)
    "malzahar": dict(ppu=1.38, edge=1, lift=2, face_to=(4, -41)),   # (4,-41) since #347 (2026-10-18): the eyes were on the top row
    # league_milio (#105): Codex's drafts read on their own grid and brought to the user's 2.2 squares a game pixel by
    # tools/art/rig_milio.py (the boy 32 game rows from his hair top to his soles; one head brought down once for every
    # frame), so no proportion or density change here; the outer outline grown a square like the others; the face
    # point at his crown (rig_milio.face_point)
    "milio": dict(ppu=2.2, edge=1, face_to=(0, -30)),
    # league_jayce (#106): Codex's strips (both forms) on the design's grid brought to the user's 1.5 squares a game pixel
    # by tools/art/rig_jayce.py (38 game rows crown to soles; one head brought down once for every frame), so no
    # proportion or density change here; the outer outline grown a square like the others; the face point at his crown
    # 2026-10-18 face (-1,-40): (0,-38) put his eyes on the 3rd-4th rows and the red scarf and chest below
    "jayce": dict(ppu=1.5, edge=1, face_to=(-1, -40)),
    # league_elise (#107): Codex's strips warped to the design's proportions and brought to the user's 1.8 squares a game
    # pixel by tools/art/import_elise_strips.py + rig_elise.py (38 game rows crown to toes), so only the outer outline
    # grown a square like the others; the face point at her crown
    "elise": dict(ppu=1.8, edge=1, face_to=(0, -37)),
    # league_katarina (#108): Codex's strips brought to the user's PPU by tools/art/rig_katarina.py (38 game rows crown
    # to soles; 1.5, then the design's own 1.7895 for the face, then back to 1.5: 「卡特琳娜太高清了 降低点像素」), so no
    # proportion or density change here; the outer outline grown a square like the others; the face point at her crown
    # 2026-10-18 face (1,-36): (0,-37) framed four rows of hair and cut the chin
    "katarina": dict(ppu=1.5, edge=1, face_to=(1, -36)),
    # league_tahmkench (#110): posed from the approved design's own squares and brought to the user's 1.2 squares a game
    # pixel by tools/art/rig_tahmkench.py (42 game rows hat to soles), so only the outer outline grown a square like the
    # others; the face point on his head's top under the hat
    # 2026-10-18 face (-1,-38): (-1,-36) put his eyes on the top two rows
    "tahmkench": dict(ppu=1.2, edge=1, face_to=(-1, -38)),
    # league_kalista (#109): Codex's strips (heads, sizes, run and death finished by tools/art/import_kalista_strips.py)
    # brought to the user's PPU 1.4 at 85 % by tools/art/rig_kalista.py (「大小 85%，PPU 1.4」), so no proportion or
    # density change here; the outer outline grown a square like the others; the face point at her helm
    # 2026-10-18 face (2,-34): (0,-39) framed only her purple crest; her glowing eye and cyan visor sit lower right
    "kalista": dict(ppu=1.4, edge=1, face_to=(2, -34)),
    # league_drmundo (#111): Codex's strips (sizes, places, the run and the death finished by
    # tools/art/import_drmundo_strips.py) brought to the user's PPU 1.5 by tools/art/rig_drmundo.py (「选 A，42 行，PPU
    # 1.5」), so no proportion or density change here; the outer outline grown a square like the others; the face point
    # by tfm2_ase.py face (his crown, a little ahead of the head centre)
    "drmundo": dict(ppu=1.5, edge=1, face_to=(-1, -38)),
    # league_pantheon (#112): Codex's strips drawn on the design's own grid at the user's 1.5 squares a game pixel
    # (「选A 40尺寸 PPU1.5」), ordered and moved by whole squares by tools/art/rig_pantheon.py, so no proportion or density
    # change here; the outer outline grown a square like the others; the face point at his helmet's crown
    "pantheon": dict(ppu=1.5, edge=1, face_to=(-3, -36)),
    # league_orianna (#113): the chibi redesign (2026-10-22) posed by tools/art/rig_orianna.py at 2.25 squares a game
    # pixel (86 squares bun to soles = the old 38 game rows), so no proportion or density change here; the outer
    # outline grown a square like the others; the face point at her crown (tfm2_ase.py face)
    "orianna": dict(ppu=2.25, edge=1, face_to=(0, -35)),
    # league_aphelios (#114): posed from the design's own squares at the user's 1.5 squares a game pixel (「选 A，40 行」,
    # Codex's step-1 take cut to 60 rows) by tools/art/rig_aphelios.py, so no proportion or density change here; the
    # outer outline grown a square like the others; drawn 90 % by league.dll (hd.rs SIZES, 「缩到 90%」) round the
    # frame's centre, so every frame lowered 11.5 x 1.5 x (1 / 0.9 - 1) = 1.9 -> 2 squares (league_nilah's way); the
    # face point at his hair's crown x 0.9
    # league_aphelios: the muzzle flashes drawn into his shot frames (rig_aphelios.py, orig/aphelios_a_<w>.over.png) laid on
    # after the outline (fx)
    "aphelios": dict(ppu=1.5, edge=1, lift_sq=-2, face_to=(-2, -38), fx=True),
    # league_rell (#115): posed by tools/art/rig_rell.py from the user's picks at 1.5 squares a game pixel (mounted: Codex's
    # take A-2 on its own grid, every frame pixelated onto design_A's grid, 44 game rows hair to hooves; on foot: take B-2
    # cut to 60 rows, 40 game rows), so no proportion or density change here; the outer outline grown a square like the
    # others; the face point at her crown (tfm2_ase.py face: 43 px over the hooves)
    "rell": dict(ppu=1.5, edge=1, face_to=(-2, -43)),
    # league_urgot (#116): his design (Codex's step-1 take 2 cut to 63 rows at the user's 1.5) brought to 1.2 once by
    # rig_urgot.py and every frame posed on that grid (the user, 2026-10-17, in game: 「现在像素太高 要降低点」, then 「1.2」
    # from a sheet of 1.5 / 1.3 / 1.2 / 1.0; each frame pixelated here on its own sampled the moved parts differently), so
    # no density change here; the outer outline grown a square like the others; the muzzle flashes drawn into his shot
    # frames (orig/urgot_<tag>.over.png) laid on after the outline (fx); the face point on his face (was (3, -24), which
    # cropped the face icons to his belly plate)
    "urgot": dict(ppu=1.2, edge=1, face_to=(1, -38), fx=True),
    # league_reksai (#117): posed by tools/art/rig_reksai.py from Codex's step-1 takes read back square for square (A 57
    # rows = the user's 36 game px: posed at 57 / 36 = 1.58), then pixelated to 1.2 (the user, 2026-10-17: 「雷克赛像素太高
    # 需要降低」, picked 1.2 from 1.58 / 1.4 / 1.3 / 1.2 / 1.0 - tools/art/review_reksai_ppu.py); no proportion change; the
    # outer outline grown a square like the others; the face point between her helmet and her mouth (she has no eyes;
    # the crown is the crest)
    "reksai": dict(ppu=1.2, edge=1, face_to=(15, -20)),
    # league_swain (#118): posed by tools/art/rig_swain.py from Codex's step-1 take A-1 cut to 60 rows (the user's 40 game
    # rows at 1.5), the demon form on the same body; no proportion or density change here; the outer outline grown a
    # square like the others; the face point 42 px over the soles (39 cut off his hair and showed his collar)
    "swain": dict(ppu=1.5, edge=1, face_to=(-1, -42)),
    # league_renata (#120): posed by tools/art/rig_renata.py from Codex's step-1 take 1 cut to 60 rows, then to 54 (36 game
    # rows at 1.5, the user's 「模型太大」; the R machine in her own ult frames); no proportion or density change here; the
    # outer outline grown a square like the others; the pistol's muzzle flash (Codex's a_flash, rig_renata.py,
    # orig/renata_attack.over.png) laid on after the outline (fx); the face point at her crown (tfm2_ase.py face: 36 px
    # over the soles)
    "renata": dict(ppu=1.5, edge=1, face_to=(1, -36), fx=True),
    # league_nasus (#121): posed by tools/art/rig_nasus.py from Codex's step-1 takes A-1 / B-1 cut to 53 / 71 rows (the
    # user's 44 / 59 game rows at 1.2), the big body (Fury of the Sands) its own design; no proportion or density change
    # here; the outer outline grown a square like the others; the face point on his glowing eye
    # 2026-10-25 face (7,-39): (7,-36) sat low: the eyes on the top rows, fangs and collar below
    "nasus": dict(ppu=1.2, edge=1, face_to=(7, -39)),
    # league_anivia (#123): posed by tools/art/rig_anivia.py from Codex's step-1 takes A-2 / B-1 cut to 46 / 23 rows (the
    # user's 38 game rows at 1.2, 「模型有点大」 from 44; in game 「凤凰的局内模型太大」 -> 31 rows, 37 / 19 cut); the wings
    # rigid (as drawn or mirrored); no proportion or density change here; the outer outline grown a square like the
    # others; the face point on her violet brow gem's row, between it and her magenta eye
    # 2026-10-25 face (2,-23): (2,-20) left the crest out, the purple eyes on top and body below
    "anivia": dict(ppu=1.2, edge=1, face_to=(2, -23)),
    # the 2026-10-16 redo from Codex's pictures, posed by tools/art/rig_<hero>_hd.py (tools/art/ppu_rig.py) at PPU 1.5 -
    # Nami after League's own clips (tools/lol/league_joints.py): only the outer outline grown a square, the face point
    # at the new head
    "morgana": dict(ppu=1.5, edge=1, face_to=(1, -34)),     # #310: framed on her face (was chin to chest)
    "nami": dict(ppu=1.5, edge=1, lift_sq=-2, face_to=(1, -38)),   # #310; 90 % in game (hd.rs SIZES): 2 squares lower, the face x 0.9 about the soles
    "janna": dict(ppu=1.5, edge=1, face_to=(1, -27)),       # #309: her eyes no longer on the frame's top edge
    # Jax: his glowing eyes in the hood (he looks front-right): (4, -32), as champion_view has had it since 8b34c700b -
    # (6, -29) put his eyes in the box's top-left corner and came back with every rerun of this table
    "jax": dict(ppu=1.5, edge=1, face_to=(4, -32)),
    # Xin Zhao (2026-10-18): Codex's chibi picture cut to 63 rows, posed after League's own clips by
    # tools/art/rig_xinzhao_hd.py (his run League's Runbase on drawn legs, the design's boots); the W slash and the R tell
    # baked into his frames (orig/xinzhao_<tag>.over.png) laid on after the outline (fx); the face point at the top of his
    # hair, under the topknot (tfm2_ase.py face: the head 3.9 px ahead of the pivot)
    # face moved to (4,-34) on 2026-10-18 (#351): (5,-36) framed mostly hair, the eyes on the portrait's bottom rows
    "xinzhao": dict(ppu=1.5, edge=1, face_to=(4, -34), fx=True),
    # Kai'Sa (2026-10-18): Codex's chibi picture read back on its own grid (42 x 61), posed after League's own clips by
    # tools/art/rig_kaisa_hd.py (the run's legs Codex's redraw, assets/source/kaisa/codex_walk); her shot, Q, W and R
    # effects baked into her frames (orig/kaisa_<tag>.over.png / .under.png) laid on after the outline (fx); the face
    # point at the top of her hair, between the pods (design row 8, 36.6 px over the soles; tfm2_ase.py face takes the
    # pods' tips for the crown)
    # face moved to (1,-34) on 2026-10-18: (1,-36) framed two thirds hair in the hd_idle, the eyes on rows 6-7 and the
    # chin cut; (1,-34) puts the eyes on the box's middle row
    "kaisa": dict(ppu=1.45, edge=1, face_to=(1, -34), fx=True),
    # Camille (2026-10-18): Codex's design picture read back on its own grid and cut to 69 rows (32 x 69), the upper body
    # posed after League's own clips by tools/art/rig_camille_hd.py, the legs of her kicks and leaps Codex's drawing
    # (assets/source/camille/codex_legs); the face point at the crown of her hair (tfm2_ase.py face)
    # 2026-10-18 face (-1,-45): (-2,-46) framed the hair above, the eyes on rows 6-7, the face off to the right
    "camille": dict(ppu=1.5, edge=1, face_to=(-1, -45)),
    # Fiora (2026-10-18): Codex's design picture read back on one fitted grid and cut to 60 rows with her whole head kept
    # (87 x 60), posed after League's own clips by tools/art/rig_fiora_hd.py - the sword arm and the guard turned
    # losslessly, the blade drawn straight level or upright, the legs of her steps and lunges drawn on League's bones
    # in the design's own colours with its knee guards and boots; the Q dash baked under skill_fx1 (fx)
    # 2026-10-18 face (2,-38): (1,-39) framed five rows of hair, the eyes on rows 6-7, the mouth on the last row
    "fiora": dict(ppu=1.5, edge=1, face_to=(2, -38), fx=True),
    # league_leblanc (2026-10-19, PPU redo): Codex's take A of 2026-10-02 as drawn, its staff straightened and the leg gaps
    # filled (tools/art/design_leblanc_hd.py; the user: 「其实这个就挺好的 你只要把法杖做好 利用PPU就行了」, 「PPU 2.0 原样」),
    # posed after League's clips by tools/art/rig_leblanc_hd.py (the run on Codex's legs, import_leblanc_legs.py), so no
    # proportion or density change here; the outer outline grown a square like the others; Q's flash, the W trails and
    # the cast flashes baked into her frames (orig/leblanc_<tag>.over/.under.png) laid on after the outline (fx); the face
    # point at her crown's tip as before
    "leblanc": dict(ppu=2.0, edge=1, face_to=(0, -31), fx=True),
    # Darius (2026-10-18): Codex's design picture read back on its own 17.2 x 16.45-px squares (56 x 61, nothing cut),
    # PPU 1.45 at his old 42 rows (「用 PPU 1.45，和现在一样高」), posed after League's own clips by
    # tools/art/rig_darius_hd.py - the axe hand and the axe turned losslessly, the legs as drawn, moved whole in the run;
    # the face point at the crown of his hair (tfm2_ase.py face), the card -8 (bp_card_audit.py's rule)
    # 2026-10-18 face (5,-38): the redo's point missed the face
    "darius": dict(ppu=1.45, edge=1, face_to=(5, -38)),
    # Riven (2026-10-18): Codex's design picture read back on its own 15.57 x 17.48-px squares (68 x 61), her sword one of
    # Codex's angle drawings (swords_riven_hd.py) in her fist; idle, run, ult, wind slash, hit and death posed after
    # League's clips by tools/art/rig_riven_hd.py, her three attacks, Broken Wings and Valor Codex's whole-frame
    # redraws (actions_riven_hd.py); effects baked (fx)
    "riven": dict(ppu=1.5, edge=1, face_to=(0, -34), fx=True),
    # Caitlyn (2026-10-23): Codex's design picture read back on its own grid (54 x 65), her actions Codex's whole-frame
    # redraws with the rifle drawn straight square by square (tools/art/rig_caitlyn_hd.py); effects baked at the muzzle
    # 2026-10-23 face (0,-38): (0,-40) framed the hat band and brim on top, the eyes low and the mouth cut
    # 2026-10-24: 90 % in game (「女警模型局内整体有点大 调小一点需要」, hd.rs SIZES): 11.5 x 1.45 x (1 / 0.9 - 1) = 1.9 -> 2
    # squares lower; the face point x 0.9 about the soles
    "caitlyn": dict(ppu=1.45, edge=1, lift_sq=-2, face_to=(0, -34), fx=True),
    # Varus (2026-10-23): Codex's design picture read back on its own grid (58 x 59, design_varus_hd.py), every action
    # posed from the design's own squares (tools/art/rig_varus_hd.py: the bow piece lifted, the near arm turned level,
    # drawn run / kneel legs sampled from the design's leg rows); the string and the arrow ride the effect layers (fx)
    "varus": dict(ppu=1.35, edge=1, face_to=(1, -39), fx=True),   # 1.5 -> 1.35: 「维鲁斯建模小了」
    # Jinx (2026-10-23): the user's own side-view picture read back at PPU 2.2 (82 rows, design_jinx_hd.py) with
    # Fishbones added, every action posed from the design's own squares (tools/art/rig_jinx_hd.py: arms never moved, the
    # run's thighs the design's stocking rows along the bone with its whole boots); the zapper's charge rides the
    # effect layer (fx)
    "jinx": dict(ppu=2.2, edge=0, face_to=(1, -36), fx=True),
    # Lux (2026-10-23): Codex's picture read back at PPU 2.2 (81 rows, design_lux_hd.py, the staff drawn straight); idle,
    # run, hit and death posed from the design's own squares (tools/art/rig_lux_hd.py), the casts Codex's whole-frame
    # redraw mended onto the design (tools/art/casts_lux_hd.py: the design's head and staff, its size)
    # 2026-10-23 face (0,-34): (-1,-37) framed the crown and headband on top, the eyes on the bottom rows and no mouth
    "lux": dict(ppu=2.2, edge=0, face_to=(0, -34)),
    # Ahri (2026-10-24): Codex's first picture read back at PPU 2.2 (78 x 88, design_ahri_hd.py, the eyes set by hand);
    # every action Codex's whole-frame redraw mended onto the design (tools/art/casts_ahri_hd.py: the design's head, her
    # size, the tails joined to her hair)
    # 2026-10-25 face (2,-33): (2,-36) framed the ears and hair on rows 1-5, the eyes on rows 7-8 and no mouth
    "ahri": dict(ppu=2.2, edge=0, face_to=(2, -33)),
    # Twitch (2026-10-24): the user's own picture read back at PPU 2.2 (71 rows, design_twitch_hd.py, the goggle and the
    # grin redrawn by hand); every action Codex's whole-frame redraw mended onto the design (casts_twitch_hd.py: the
    # design's head, his size), Venom Cask's third arm moved over his head (rig_twitch_hd.py); the attack's flash rides
    # the effect layer (fx)
    # 2026-10-25 face (7,-28): (5,-24) framed his mouth, neck and chest and cut the goggles off
    "twitch": dict(ppu=2.2, edge=0, face_to=(7, -28), fx=True),
    # Annie (2026-10-24): Codex's take A read back at PPU 2.2 (44 x 75, design_annie_hd.py, the face set by hand); every
    # action Codex's whole-frame redraw mended onto the design (tools/art/casts_annie_hd.py: the design's head, her size,
    # the ground), Tibbers in her near hand
    # face (-2,-28): (0,-30) framed the crown and fringe, her eyes on the bottom rows and no mouth (Lux's lesson)
    "annie": dict(ppu=2.2, edge=0, face_to=(-2, -28)),
    # Gwen (2026-10-25): Codex's v2 picture (the user's own Gemini picture redrawn) read as drawn at PPU 2.84 (93 x 116,
    # design_gwen_hd.py; 「用 2.84，按原图密度」); every action Codex's whole-frame redraw mended onto the design
    # (tools/art/casts_gwen_hd.py: the scissors full size and always in her right hand); the snips and the dash's mist
    # ride the effect layer (fx), moved to the new blade's tip (gwen_bake.json)
    # 2026-10-25 face (2,-33): (2,-38) was the old 1x point: on the PPU 2.84 redo it frames hair band and hair, the eyes on the bottom rows, no mouth
    "gwen": dict(ppu=2.84, edge=0, face_to=(2, -33), fx=True),
    # Samira (2026-10-25): Codex's v3 picture (League's look, the head made smaller) read on its own squares at PPU 2.84
    # (76 x 105, design_samira_hd.py, the greatsword straightened); every action Codex's whole-frame redraw read onto
    # the design (tools/art/casts_samira_hd.py); the muzzle flashes and sword arcs ride the effect layer (fx), moved to
    # the new muzzles (samira_bake.json). Then in game: 「我怎么感觉身体有点细啊 和原版画风不符」「感觉降低像素就行了」
    # 「泽丽之前也一样 但是后面调整好了」 - picked 2.2 from a 2.84 / 2.2 / 1.8 / 1.5 sheet (tools/art/review_samira_ppu.py,
    # 「用 2.2」): drawn at 2.84 (ORIG_PPU), brought to 2.2 squares a game pixel like Jinx, Lux, Ahri and Annie; the
    # 1-2 square holes the coarser grid closes round thin gaps (arm and waist, hair strands) filled. Then 「这嘴也太丑了」
    # (2.2 voted her lips into a dark slash and her one-pixel green eye away) and 「你可以其他地方模糊点 脸做好点啊」:
    # the frames stay on their 2.84 grid, everything laid back on it at 2.2 squares (look) but her face as drawn
    # (look_keep: tools/art/face_samira_hd.py) - the approved 2.84 face in a 2.2 body; the effects ride on as drawn
    "samira": dict(edge=0, face_to=(-4, -36), fx=True, look=2.2, look_holes=2, look_keep="face_samira_hd"),
    # Draven (2026-10-26): the user's own picture (「就用这个就行」, drawn at PPU 2.2 on 11-px squares) read back exactly
    # (114 x 76, design_draven_hd.py); every action Codex's whole-frame redraw of his old frame in its old pose
    # (「你照着旧动作做啊」) read onto the design (tools/art/casts_draven_hd.py); drawn at 2.2, so no density change
    # face (0,-33): a square under his crown as tfm2_ase face finds it from the skin (its crown search takes the raised
    # axe for the head), the hair spikes above, headband, eyes and mouth under it
    "draven": dict(ppu=2.2, edge=0, face_to=(0, -33)),
    # league_yunara (#119): posed from the design's own squares at the user's 1.5 squares a game pixel (「选 A，40 行」,
    # Codex's step-1 take 2 cut to 60 rows, her beads apart) by tools/art/rig_yunara.py, so no proportion or density
    # change here; the outer outline grown a square like the others; the face point at her ornaments' crown
    # (tfm2_ase.py face)
    "yunara": dict(ppu=1.5, edge=1, face_to=(1, -39)),
    # league_jarvaniv (#122): posed from the design's own squares at the user's 1.5 squares a game pixel (「身体 40」,
    # Codex's step-1 take A-2 cut to 60 rows) by tools/art/rig_jarvaniv.py, so no proportion or density change here;
    # the outer outline grown a square like the others; the face point between his eyes under the helmet's brim
    # 2026-10-25 face (1,-37): (1,-32) framed his breastplate with only the chin showing
    "jarvaniv": dict(ppu=1.5, edge=1, face_to=(1, -37)),
    # league_ziggs (#124): posed from the design's own squares at 1.5 squares a game pixel (「游戏里 32 像素高」, Codex's
    # step-1 take A-1 cut to 48 rows) by tools/art/rig_ziggs.py, then brought to 1.2 here (the user, 2026-10-18, on the
    # showcase: 「太高清了 降低点像素」 - shown 1.5 / 1.3 / 1.2 / 1.0 by tools/art/review_ziggs_ppu.py: 「降到 PPU 1.2」); the
    # outer outline grown a square like the others; the face point between his goggles
    # 2026-10-25 face (2,-27): (2,-26) cut the top of his goggles
    "ziggs": dict(ppu=1.2, edge=1, face_to=(2, -27)),
    # league_maokai (#125): posed from the design's own squares at 1.5 squares a game pixel (the user picked 40 game rows
    # at 1.2, then 「太模糊了 PPU调整一下像素」: Codex's step-1 take A-2 cut to 60 rows) by tools/art/rig_maokai.py, then
    # brought to 1.3 here (the user, 2026-10-18, on the PR: 「太高清了 降低点像素」 - shown 1.5 / 1.4 / 1.3 / 1.2 by
    # tools/art/review_maokai_ppu.py: 「1.3吧」); the outer outline grown a square like the others; the face point between
    # the eyes of the face in his trunk
    # 2026-10-25 face (8,-28): (8,-23) missed his eyes: mossy chin and hands only
    "maokai": dict(ppu=1.3, edge=1, face_to=(8, -28)),
    # league_gangplank (#126): posed from the design's own squares at the user's 1.5 squares a game pixel (Codex's
    # step-1 redo take A-2 read back uncut, 62 rows = 41 game rows: the 50-row cut for 1.2 broke the gun hand - 「拿枪的
    # 那个手啊」, 「PPU 用 1.5」) by tools/art/rig_gangplank.py, Q / R from Codex's gun-hand poses, so no proportion or
    # density change here; the outer outline grown a square like the others; the face point between his eyes
    # 2026-10-18 the user: 「船长猴子阿克尚波比蛇女像素太高需要降低 船长猴子局内太大」 -> PPU 1.2 and Wukong 85%; Gangplank 90% kept at 1.5 (「船长保留1.5 但是要缩小体型」)
    # Q's flash, W's orange and R's flare baked into his frames (orig/gangplank_<tag>.over.png) laid on after the outline
    # (fx; 2026-10-19 frame audit: without it the three never reached the game since #126)
    "gangplank": dict(ppu=1.5, grow=0.9, edge=1, lift_sq=-1, face_to=(2, -29), fx=True),
    # league_wukong (#127): posed from the design's own squares at the user's 1.5 squares a game pixel (「用 A，游戏里 38
    # 像素高」, then on the step-1 guide 「太模糊了 起码PPU1.5」: Codex's step-1 take A-1 cut to 57 rows hair to soles) by
    # tools/art/rig_wukong.py, so no proportion or density change here; the outer outline grown a square like the others;
    # the face point between his green eyes
    # 2026-10-20 「猴子现在太小了」: 115 % (hd.rs SIZES; 36 -> 41 game px, Lee Sin / Pantheon / Garen 41) round the frame's
    # centre, so every frame lifted 11.5 x 1.2 x (1 - 1 / 1.15) = 1.8 -> 2 rows of the new grid; face (3, -27) x 1.15 and the lift -> (3, -33)
    "wukong": dict(ppu=1.2, edge=1, lift_sq=2, face_to=(3, -33), shared_palette=True, shared_palette_skip=[("hit", 0)]),   # one palette over every frame (「猴子gif图里面怎么一直变色？」)   # 10-18 redo: Codex's new design and actions (rig_frames_1018.py), drawn at 85 % already
    # league_cassiopeia (#128): posed from the design's own squares at the user's 1.3 squares a game pixel (「44 ppu1.3 A」:
    # Codex's step-1 take A-2 cut to 57 rows crest to ground) by tools/art/rig_cassiopeia.py, so no proportion or density
    # change here; the outer outline grown a square like the others; the face point between her eyes
    "cassiopeia": dict(ppu=1.2, edge=1, face_to=(2, -29)),
    # league_akshan (#129): posed from the design's own squares at the user's 1.5 squares a game pixel (「用 A，游戏里 38
    # 像素高，PPU 1.5」: Codex's step-1 round-2 take A-1 cut to 57 rows hair to soles) by tools/art/rig_akshan.py, the
    # forward gun arm from Codex's pose and the walk from Codex's skin swap read on the same grid, so no proportion or
    # density change here; the outer outline grown a square like the others; the face point between his eyes
    "akshan": dict(ppu=1.2, edge=1, face_to=(4, -31)),   # 10-18 redo: the slim design and Codex's actions (rig_frames_1018.py)
    # league_poppy (#130): posed from the design's own squares at the user's 1.3 squares a game pixel (「用 B（锤子竖着），
    # 游戏里 36 像素高，PPU 1.3」: Codex's step-1 take B-2 cut to 47 rows pigtails to soles) by tools/art/rig_poppy.py, so no
    # proportion or density change here; the outer outline grown a square like the others; the face point between her eyes
    # 2026-10-19 the user: 「波比在游戏里体型也太大 需要缩小」 -> drawn 85 % by league.dll (hd.rs SIZES) round the frame's
    # centre (44 game px with the standing hammer against the yordles' 32-40), so every frame lowered
    # 11.5 x 1.2 x (1 / 0.85 - 1) = 2.4 -> 2 squares (league_aphelios's way); the face point (5, -22) taken with it
    "poppy": dict(ppu=1.2, edge=1, lift_sq=-2, face_to=(4, -17)),
    # league_volibear (#131): posed by tools/art/rig_volibear.py at the user's 1.2 squares a game pixel (「44 像素，PPU 1.2」:
    # Codex's step-1 take B-2, 54 rows ear top to soles; Codex's arm poses, walk and Q on the same grid), so no proportion or
    # density change here; the outer outline grown a square like the others; the face point between his eyes
    "volibear": dict(ppu=1.2, edge=1, face_to=(6, -27)),
    # league_rammus (#132): posed from the designs' own squares at the user's 1.2 squares a game pixel (「36 像素」「PPU 1.2」:
    # Codex's step-1 takes A-2 / S-1 / B / W read back on their own grids and cut to 43 rows spike tips to soles) by
    # tools/art/rig_rammus.py, so no proportion or density change here; the outer outline grown a square like the others;
    # the face point on the hood's lip over his eyes (lint_mod's 10 px under the crown)
    "rammus": dict(ppu=1.2, edge=1, face_to=(5, -19)),
    # league_zoe (#133): posed from the designs' own squares at the user's 1.5 squares a game pixel (「35 像素」「PPU 1.5」:
    # Codex's step-1 takes A-1 / S-1 read back on their own grids and cut to 53 rows crown to soles) by tools/art/rig_zoe.py,
    # so no proportion or density change here; the outer outline grown a square like the others; the face point between
    # her eyes
    "zoe": dict(ppu=1.5, edge=1, face_to=(1, -24)),
    # league_yuumi (#135): posed from the designs' own squares at the user's 1.5 squares a game pixel (「32 像素」「PPU 1.5」:
    # Codex's step-1 takes A-2 / S-1 / L-2 / R-2 / C-1 read back on their own grids and cut to 48 rows orb top to the
    # book's bottom) by tools/art/rig_yuumi.py, so no proportion or density change here; the outer outline grown a square
    # like the others. The user then: 「还有模型太大」 -> 「75%（24 像素）」: drawn 75 % by league.dll (hd.rs SIZES) round the
    # frame's centre, so every frame lowered 11.5 x 1.5 x (1 / 0.75 - 1) = 5.75 -> 6 squares (league_poppy's way); the
    # face point between her eyes, (7.5, -19) at full size, taken with it: 0.75 x (7.5, -19 + 11.5 + 4) - (0, 11.5)
    "yuumi": dict(ppu=1.5, edge=1, lift_sq=-6, face_to=(6, -14)),
    # league_quinn (#134): posed by tools/art/rig_quinn.py at 2.0 squares a game pixel (38 game px crest to soles: the
    # user's 1.3 picks redrawn by Codex on the finer grid, 「像素有点太低了 太多模糊的了 调一下PPU」, A-1 cut to 75 rows,
    # tools/art/design_quinn_grid.py), her legs drawn on League's bones in her own leg squares (tools/art/quinn_legs.py),
    # so no proportion or density change here; the outer outline grown a square like the others; the face point between
    # her eyes
    "quinn": dict(ppu=2.0, edge=1, face_to=(3, -31)),
    # league_chogath (#136): posed by tools/art/rig_chogath.py at the user's 1.2 squares a game pixel (「38 像素」「PPU 1.2」:
    # Codex's step-1 take A-1 cut to 46 rows, the side view redrawn on the grid, Codex's poses read back at its scale),
    # so no proportion or density change here; the outer outline grown a square like the others; the face point between
    # his eyes (his head hangs low: 16 game px over his soles)
    "chogath": dict(ppu=1.2, edge=1, face_to=(11, -5)),
    # league_karthus (#137): posed by tools/art/rig_karthus.py from Codex's step-1 takes at the user's 1.5 squares a game
    # pixel (「40 像素，PPU 1.5」: A-1 / side-1 cut to 60 rows crown to soles, one head, one staff), so no proportion or
    # density change here; the outer outline grown a square like the others; the face point on his skull (the 9x9 face
    # crop: the eyes, the teeth and the crown's gem)
    "karthus": dict(ppu=1.5, edge=1, face_to=(1, -30)),
    # league_vex (#138): posed from the designs' own squares at the user's 1.5 squares a game pixel (「34 像素」「PPU 1.5」:
    # Codex's step-1 takes A-2 / SA-2 read back on their own grids and cut to 63 rows, her Shadow's ear tips to her soles,
    # the faces redrawn) by tools/art/rig_vex.py, so no proportion or density change here; the outer outline grown a
    # square like the others; the face point between her eyes
    "vex": dict(ppu=1.5, edge=1, face_to=(1, -17)),
    # league_zyra (#140): posed by tools/art/rig_zyra.py on Codex's step-1 take A-1 at 1.7 squares a game pixel (the
    # user: 「44」, then 「提高点ppu像素吧」「脸部完全变形了啊」: A-1's own 74 rows hair to soles, Codex's own face; 「就用四分之三面
    # 来做啊」: every action on the 3/4 design), so no proportion or density change here; the outer outline grown a square
    # like the others; the face point between her eyes
    "zyra": dict(ppu=1.7, edge=1, face_to=(1, -32)),
    # league_graves (#139): posed by tools/art/rig_graves.py at the user's 1.5 squares a game pixel (「38 像素」「PPU 1.5」:
    # Codex's step-1 takes A-1 / side-2 cut to 57 rows with one head, Codex's seven poses on skeletons read back at the
    # side design's scale), so no proportion or density change here; the outer outline grown a square like the others;
    # the face point between his eyes; the muzzle blasts baked into his shot frames (orig/graves_<tag>.over.png, rig_graves
    # with_blasts) laid on after the outline (fx)
    "graves": dict(ppu=1.5, edge=1, face_to=(1, -31), fx=True),
    # league_warwick (#142): posed by tools/art/rig_warwick.py on Codex's step-1 take A-1, drawn at the count (the user:
    # 「选大一号的那个」 46 game px spike top to soles, 「PPU 1.5」: 69 rows; 「不做侧面 只做四分之三的侧面」「动作帧按照英雄联盟的自己做」:
    # posed by rig_warwick.py on the design and Codex's skeleton poses at 1.5), brought down to 1.2 squares a game pixel
    # (the user on the review: 「太高清了 降点像素」 - the beasts' density, league_volibear / league_nasus); the outer
    # outline grown a square like the others; the face point between his eyes (11 game px ahead of his standing point:
    # the hunched head is pushed out over his far foot)
    # 2026-10-23: 90 % in game (「狼人局内模型有点大了 开个pr缩小一点」, hd.rs SIZES): 11.5 x 1.2 x (1 / 0.9 - 1) = 1.5 -> 2
    # squares lower; the face point x 0.9 about the soles
    "warwick": dict(ppu=1.2, edge=1, lift_sq=-2, face_to=(10, -25)),
    # league_gnar (#141): posed by tools/art/rig_gnar.py at the user's 1.5 squares a game pixel (「迷你 32」「巨型 44」:
    # Codex's step-1 takes A-2 cut to 48 rows, M-1 and SM-2 as drawn / cut to 66, Mega's turned poses drawn again from
    # Codex's own picture), so no proportion or density change here; the outer outline grown a square like the others;
    # the face point between Mini's eyes (the cards and portraits show Mini)
    "gnar": dict(ppu=1.5, edge=1, face_to=(0, -19)),
    # league_sylas (#143): posed by tools/art/rig_sylas.py at the user's 1.2 squares a game pixel (「38」「PPU 1.2」: Codex's
    # step-1 take A-1 read back to 46 rows; 3/4 only; Codex's sixteen skeleton poses read back at the design's scale with
    # the design's head), so no proportion or density change here; the outer outline grown a square like the others; the
    # face point between his eyes (31 game px over his soles, 2 ahead of his standing point)
    "sylas": dict(ppu=1.2, edge=1, face_to=(2, -31)),
    # league_mel (#144): posed by tools/art/rig_mel.py on Codex's step-1 take A-3 at the user's 1.5 squares a game pixel
    # (「44」「PPU 1.5」: A-3's own 65 rows bun top to soles, Codex's own face: 「不用重画了…之前的」; 3/4 only, every action
    # posed after League's clips by me: 「我自己照英雄联盟摆」), so no proportion or density change here; the outer outline
    # grown a square like the others; the face point between her eyes
    "mel": dict(ppu=1.5, edge=1, face_to=(0, -30)),
    # league_velkoz (#145): posed by tools/art/rig_velkoz.py on Codex's step-1 take A-2 at the user's 1.5 squares a game
    # pixel (「36」「PPU 1.5」: 54 rows crest top to the lowest tentacle, Codex's own eyes; 3/4 only, every action rigged after
    # League's clips), so no proportion or density change here; the outer outline grown a square like the others; the face
    # point on his big eye (7 game px ahead of his standing point, 21 over the ground: he floats 4 squares up)
    "velkoz": dict(ppu=1.5, edge=1, face_to=(7, -21)),
    # league_ornn (#146): posed by tools/art/rig_ornn.py on Codex's step-1 take A-3 at the user's 1.5 squares a game pixel
    # (「44」「PPU 1.5」: 66 rows horn top to soles, Codex's own face; 3/4 only, Codex's eighteen skeleton poses with the
    # design's face), so no proportion or density change here; the outer outline grown a square like the others; the face
    # point between his eyes (28 game px over his soles, 2 ahead of his standing point); W's fire drawn into his breath
    # frames (orig/ornn_skill_w.over.png, rig_ornn with_fire) laid on after the outline (fx)
    "ornn": dict(ppu=1.5, edge=1, face_to=(2, -28), fx=True),
    # league_shyvana: posed by tools/art/rig_shyvana.py on Codex's step-1 takes at the user's 1.5 squares a game
    # pixel (「人42 龙48 PPU1.5」: A-2's 63 rows horn tips to soles, the dragon D-1 as drawn, 64 rows: 「龙就按画的大小」; 3/4
    # only; the dragon's actions rigged on its design, hers on Codex's fourteen skeleton poses with the design's head),
    # so no proportion or density change here; the outer outline grown a square like the others; Q's slashes baked into
    # skill / d_skill (orig/shyvana_<tag>.over/.under.png) laid on after the outline (fx); the face point between her
    # eyes (33 game px over her soles, 2 ahead of her standing point)
    "shyvana": dict(ppu=1.5, edge=1, face_to=(2, -33), fx=True),
    # league_naafiri (group F jungle): posed by tools/art/rig_naafiri.py on Codex's step-1 takes A-2 / P-2 and its key poses
    # at the user's 1.5 squares a game pixel (「30」「PPU 1.5」: 45 rows blade tip to paws; 3/4 only; her pack drawn into her
    # frames), so no proportion or density change here; the outer outline grown a square like the others; the face point
    # between her eyes (12 game px ahead of her standing point, 12 over the ground: a hound holds her head low)
    "naafiri": dict(ppu=1.5, edge=1, face_to=(12, -12)),
    # league_udyr (group G jungle): his four stances posed by tools/art/rig_udyr.py on Codex's step-1 takes A-1 / Q-1 / E-1 /
    # R-1 and its 29 key poses at the user's 1.5 squares a game pixel (「平常姿态 40 游戏像素，PPU 1.5，只做四分之三侧面」: 60
    # rows fists to soles), so no proportion or density change here; the outer outline grown a square like the others; the
    # face point between his eyes (2 game px ahead of his standing point, 33 over the ground)
    "udyr": dict(ppu=1.5, edge=1, face_to=(2, -33)),
    # league_qiyana (group G jungle): the design (Codex's step-1 A-1 cut to the user's 60 rows at 1.5 squares a game pixel:
    # 「40」「PPU 1.5」, 3/4 only) with Codex's 15 key poses (the design's head pasted back, the legs drawn again at the
    # design's chibi length) posed by tools/art/rig_qiyana.py after League's clips, so no proportion or density change here;
    # the outer outline grown a square like the others; the face point between her eyes (1 game px ahead of her standing
    # point, 27 over the ground); Q's sweeps and R's swing / burst baked into her frames (qiyana_bake.json:
    # orig/qiyana_<tag>.over.png / .under.png) laid on after the outline (fx)
    "qiyana": dict(ppu=1.5, edge=1, face_to=(1, -27), fx=True),
    # league_hwei (group G mid): the design (Codex's step-1 A-1, 60 rows hair to soles at 1.5 squares a game pixel:
    # 「头发顶到脚底 40 游戏像素，PPU 1.5，只做四分之三侧面」, the crescent of paint above) with Codex's key poses (the design's
    # head and brush put back, the legs drawn again at the design's chibi length) posed by tools/art/rig_hwei.py after
    # League's clips, so no proportion or density change here; the outer outline grown a square like the others; the face
    # point between his eyes (3 game px ahead of his standing point, 31 over the ground); then 85 % in game (2026-10-22,
    # 「画师局内有点大 可以调小一点」, hd.rs SIZES): 11.5 x 1.5 x (1 / 0.85 - 1) = 3.0 -> 3 squares lower, the face x 0.85
    # about the soles
    "hwei": dict(ppu=1.5, edge=1, lift_sq=-3, face_to=(3, -26)),
    # league_ivern (group G jungle): the design (Codex's step-1 A-2, 60 rows mushroom to soles at 1.5 squares a game
    # pixel: 「艾翁蘑菇顶到脚底 40 游戏像素 … PPU 1.5，只做四分之三侧面」) with Codex's key poses (the design's head put back,
    # the standing poses' legs drawn again at the design's chibi length) posed by tools/art/rig_ivern.py after League's
    # clips, so no proportion or density change here; the outer outline grown a square like the others; the face point
    # between his eyes (4 game px ahead of his standing point, 29 over the ground)
    "ivern": dict(ppu=1.5, edge=1, face_to=(4, -29)),
    # league_illaoi (group H top): the design (Codex's step-1 A-2, 63 rows bun to soles at 1.5 squares a game pixel:
    # 「俄洛伊发髻到脚底 42 游戏像素，PPU 1.5，触手 44，只做四分之三侧面」) with Codex's key poses (the design's head put
    # back, the long-legged poses' and the runs' legs drawn again at the design's length) posed by tools/art/rig_illaoi.py
    # after League's clips, so no proportion or density change here; the outer outline grown a square like the others;
    # the face point just over her eyes (3 game px ahead of her standing point, 35 over the ground)
    "illaoi": dict(ppu=1.5, edge=1, face_to=(3, -35)),
    # league_aurora (group H mid): the design (Codex's step-1 A-2 read on its fine squares at the user's 2.25 squares a game
    # pixel, 86 rows hat top to soles, the ears above: 「太模糊了 用PPU调下像素」 then A-2 / 2.25) with Codex's key poses (the
    # design's head put back, the long-legged poses' legs drawn again at the design's length) posed by
    # tools/art/rig_aurora.py after League's clips, so no proportion or density change here; the outer outline grown a
    # square like the others; the face point between her eyes behind the glasses (1 game px ahead of her standing point,
    # 27 over the ground)
    "aurora": dict(ppu=2.25, edge=1, face_to=(1, -27)),
    # league_nunu (group H jungle): the design (Codex's step-1 A-2, 63 rows pompom to soles as drawn, at the user's 1.37
    # squares a game pixel: 「努努用 A-2，PPU 1.37（46 游戏像素）」) with Codex's key poses (the design's Nunu head put back,
    # Willump's size set pose by pose) posed by tools/art/rig_nunu.py after League's clips, so no proportion or density
    # change here; the outer outline grown a square like the others; the face point between Nunu's eyes (the cards and
    # portraits show the boy, league_gnar's Mini the same way: 3 game px ahead of the standing point, 36 over the ground)
    "nunu": dict(ppu=1.37, edge=1, face_to=(3, -36)),
    # league_azir (group H mid): the design (Codex's step-1 A-2, 57 rows crest to soles at the user's 1.5 squares a game
    # pixel: 「38」「PPU 1.5」, 3/4 only; the sceptre straightened: 「法杖要做直了啊 下面有点歪」) with Codex's key poses (the
    # design's helmet put back, the bodies read at their skeletons' heights, the runs' passing legs cut to the contact
    # frames') posed by tools/art/rig_azir.py after League's clips, so no proportion or density change here; the outer
    # outline grown a square like the others; the face point on his helmet's glowing eye (2 game px ahead of his
    # standing point, 30 over the ground)
    "azir": dict(ppu=1.5, edge=1, face_to=(2, -30)),
    # league_zac (group H jungle): the design (Codex's step-1 A-1 cut to 66 rows at the user's 1.5 squares a game pixel:
    # 44 game px tendril top to soles, 3/4 only) with Codex's key poses after League's clips (read on their own grid, the
    # design's head and tendril put back on the eyes), posed by tools/art/rig_zac.py, so no proportion or density change
    # here; the outer outline grown a square like the others; the face point between his eyes (11 game px ahead of the
    # standing point - his head sits forward between the shoulders - 28 over the ground)
    # 2026-10-26: 85 % in game (「扎克的体型在这游戏里异常的大」, hd.rs SIZES): 11.5 x 1.5 x (1 / 0.85 - 1) = 3.0 -> 3
    # squares lower; the face point x 0.85 about the soles
    "zac": dict(ppu=1.5, edge=1, lift_sq=-3, face_to=(9, -24)),
    # league_singed (group I top): the design (Codex's step-1 A-2 as drawn: 45 x 62, 36 game px head top to soles at the
    # user's pick, PPU 1.39 = its own squares, 3/4 only) with Codex's key poses after League's clips (the design's head put
    # back, the bodies brought to the design's size), posed by tools/art/rig_singed.py, so no proportion or density change
    # here; the outer outline grown a square like the others; the face point between his eyes (3 game px ahead of the
    # standing point, 31 over the ground)
    "singed": dict(ppu=1.39, edge=1, face_to=(3, -31)),
    # league_belveth (group I jungle): the design (Codex's step-1 A-1 cut to 82 rows: 86 x 82, 40 game px head top to
    # claws at the user's pick, PPU 1.75, 3/4 only, the wing-arms folded like a cloak) with Codex's key poses after
    # League's clips (the design's head put back, the bodies brought to the design's size), posed by
    # tools/art/rig_belveth.py, so no proportion or density change here; the outer outline grown a square like the
    # others; the face point between her eyes (over the standing point, 34 game px over the ground)
    "belveth": dict(ppu=1.75, edge=1, face_to=(0, -34)),
    # league_taliyah (group I mid): the design (Codex's step-1 A-2 cut to 70 rows: 40 game px hair top to soles at the
    # user's PPU 1.75, 3/4 only) with Codex's key poses after League's clips (read at their bodies' scale, the design's
    # head put back), posed by tools/art/rig_taliyah.py, so no proportion or density change here; the outer outline grown
    # a square like the others; the face point between her eyes (1 game px ahead of the standing point, 28 over the
    # ground)
    "taliyah": dict(ppu=1.75, edge=1, face_to=(1, -28)),
    # league_aurelionsol (group I mid): the design (Codex's step-1 A-2 as drawn: 56 x 77, 44 game px crest to tail tip at
    # the user's pick, PPU 1.75, 3/4 only; the flight B-2 for the move) with Codex's key poses after League's clips (the
    # design's head put back, the bodies brought to the design's size), posed by tools/art/rig_aurelionsol.py (he hovers
    # 4 squares over the ground), so no proportion or density change here; the outer outline grown a square like the
    # others; the face point between his eyes (5 game px ahead of the standing point, 35 over the ground)
    "aurelionsol": dict(ppu=1.75, edge=1, face_to=(5, -35)),
    # league_sejuani (group I jungle): the design (Codex's PPU-2.0 redraw A-2: 82 x 72, 36 game px ice horn tip to hooves
    # at the user's picks 「36」「PPU 2.0」, 3/4 only, riding Bristle) with Codex's key poses after League's clips (her
    # design head put back, Bristle brought to the design's size), posed by tools/art/rig_sejuani.py, so no proportion or
    # density change here; the outer outline grown a square like the others; the face point between her eyes (3 game px
    # ahead of the standing point, 28 over the ground)
    "sejuani": dict(ppu=2.0, edge=1, face_to=(3, -28)),
    # league_kled (group J top): the designs (Codex's step-1 A-1 cut to 80 rows: 40 game px hat spike to Skaarl's claws at
    # the user's picks 「40」「PPU 2.0」, 3/4 only, riding Skaarl; on foot B-1 under A-1's head, 58 x 60) with Codex's key
    # poses after League's clips (the design's head put back, Skaarl and the on-foot bodies brought to the designs'
    # size), posed by tools/art/rig_kled.py, so no proportion or density change here; the outer outline grown a square
    # like the others; the face point between his eyes (2 game px ahead of the standing point, 28 over the ground)
    "kled": dict(ppu=2.0, edge=1, face_to=(2, -28)),
    # league_yorick (group J top): the design (Codex's step-0 A-2 taken as drawn: 74 x 83, 48 game px shovel tip to boots
    # at the user's picks 「48」「PPU 1.75」, 3/4 only) with Codex's key poses after League's clips (his design head put
    # back), posed by tools/art/rig_yorick.py, so no proportion or density change here; the outer outline grown a square
    # like the others; the face point between his eyes (3 game px ahead of the standing point, 31 over the ground)
    "yorick": dict(ppu=1.75, edge=1, face_to=(3, -31)),
    # league_ambessa (group J top): the design (Codex's step-1 A-1 with its head cut to 27 %: 117 x 96, 48 game px hair to
    # soles at the user's pick 「用这个」, 3/4 only) with Codex's key poses after League's clips (read at each body's own
    # scale, her design head put back), posed by tools/art/rig_ambessa.py, so no proportion or density change here; the
    # outer outline grown a square like the others; Cunning Sweep's half circle and the step's streaks drawn into her
    # frames (orig/ambessa_<tag>.over / .under) laid on after the outline (fx); the face point between her eyes (2 game
    # px ahead of the standing point, 41 over the ground)
    # 2026-10-25: 85 % in game (「太大了安倍萨 整体模型缩小一点可以吗」, hd.rs SIZES): 11.5 x 2.0 x (1 / 0.85 - 1) = 4.1 -> 4
    # squares lower; the face point x 0.85 about the soles
    "ambessa": dict(ppu=2.0, edge=1, lift_sq=-4, face_to=(2, -35), fx=True),
    # league_rumble (group J top): the design (Codex's step-1 B-1 taken as drawn: 92 x 62, 36 game px mohawk to the red
    # feet at PPU 1.75, 3/4 only) with Codex's key poses after League's clips (his design head put back, the bodies
    # Codex drew bigger read at the design's size), posed by tools/art/rig_rumble.py, so no proportion or density change
    # here; the outer outline grown a square like the others; the face point between his eyes (4 game px ahead of the
    # standing point, 26 over the ground); Flamespitter's fire baked into his skill frames (orig/rumble_skill.over.png,
    # rig_rumble's bake) laid on after the outline (fx); the one-square holes the grown outline closes in at diagonal
    # notches (specks of ground in the body: gap-check) filled with the outline (pinholes)
    "rumble": dict(ppu=1.75, edge=1, face_to=(4, -26), fx=True, pinholes=True),
    # league_trundle (group J jungle): the design (Codex's step-0 A-1 taken as drawn: 104 x 85, 42.5 game px mane to feet
    # at the user's picks 「A-1 原样 PPU 2.0」, 3/4 only) with Codex's key poses after League's clips (his design head put
    # back; run1 read from its raw draft, the export had shrunk it), posed by tools/art/rig_trundle.py, so no proportion
    # or density change here; the outer outline grown a square like the others; the face point between his eyes (5 game
    # px ahead of the standing point, 27 over the ground)
    "trundle": dict(ppu=2.0, edge=1, face_to=(5, -27)),
    # league_locke (2026's new champion, mid): the design (Codex's step-0 A-1 brought to 88 rows, 44 game px hair to soles,
    # at the user's picks 「A-1 44 PPU 2.0」, 3/4 only) with Codex's key poses after League's clips (his design head put
    # back, the bodies Codex drew ~14% bigger read at the design's size), posed by tools/art/rig_locke.py, his W look in
    # w_<tag> tags (the same frames recoloured), so no proportion or density change here; the outer outline grown a square
    # like the others; the face point between his lenses (4 game px ahead of the standing point, 37 over the ground)
    "locke": dict(ppu=2.0, edge=1, face_to=(4, -37)),
    "skarner": dict(ppu=1.75, edge=1, pinholes=True),
    # league_zaahen (the user's pick, top): the design (Codex's step-0 A-2 brought to 84 rows, 48 game px horn tips to
    # soles, PPU 1.75) and Codex's 20 poses on skeletons (their bodies brought to the design's size round the design's
    # head), posed by tools/art/rig_zaahen.py after League's clips: no proportion change here
    "zaahen": dict(ppu=1.75, edge=1, pinholes=True),
    # Lee Sin (2026-10-26, 「下一个英雄重做盲僧」): Codex's picture traced from his sprite read on its own squares (68 x 86,
    # design_leesin_hd.py: 86 rows / 2.1 = his 41); every action Codex's whole-frame redraw of his old frame read onto
    # the design at the zoom his head gives (tools/art/casts_leesin_hd.py), so no density change
    # face (-4,-31): on the blindfold as before (31 game px over the soles), over his head's middle now (tfm2_ase face:
    # the head 5.9 px behind the standing point). Then smaller in game (「模型有点太大了吧 缩小一点」: 90 %, then 「改成
    # 95%」, hd.rs SIZES); the face point x 0.95 about the soles. Then 「ppu像素太高了 降低点」: picked 1.5 of 2.1 / 1.8 / 1.5
    # / 1.2 (tools/art/review_leesin_ppu.py, 「用 1.5」) - drawn at 2.1 (ORIG_PPU), brought to 1.5 squares a game pixel
    # like Riven, Jax and Darius; 11.5 x 1.5 x (1 / 0.95 - 1) = 0.9 -> 1 square lower at his 95 %
    # 2026-10-26 face (1,-36): (-4,-29) framed his bare chest and white belt, not the blindfold. Then back to 100 %
    # in game (「盲僧在游戏里和其他英雄有点格格不入 感觉太小了」, hd.rs SIZES row gone): no square lower, the face
    # point / 0.95 about the soles -> (1,-38)
    "leesin": dict(ppu=1.5, edge=0, lift_sq=0, face_to=(1, -38)),
    # Rengar (2026-10-27, 「可以参考另外一个账号 利用PPU1.5重做一下狮子狗模型」): Codex's picture traced from his sprite read on
    # its own squares (76 x 59, design_rengar_hd.py: 59 rows / 1.475 = his 40); every action Codex's whole-frame redraw of
    # his old frame read onto the design at the zoom his head gives (tools/art/casts_rengar_hd.py), so no density change;
    # the face point stays (4, -36): he is as tall as before, the head where it was
    "rengar": dict(ppu=59 / 40, edge=0),
    # Syndra (2026-10-27, 「接下来可以重做辛德拉」, 「就用原样 1.86」): Codex's picture traced from her sprite read on its own
    # squares (54 x 78, design_syndra_hd.py: 78 rows / 1.857 = her 42); every frame the design moved as her old frame
    # moved, the far arm from Codex's pose pictures (tools/art/rig_syndra_hd.py), so no density change; the face point
    # stays: she is as tall as before, the head where it was
    "syndra": dict(ppu=78 / 42, edge=0),
    # Akali (2026-10-27, 「下一个英雄重做阿卡丽」, 「设计图通过，就用 1.8」): Codex's fourth take read as drawn (71 x 72,
    # design_akali_hd.py: 72 rows / 1.8 = her 40); every action Codex's whole-frame redraw of her old frame read onto it
    # (tools/art/casts_akali_hd.py), so no density change; the face point stays: she is as tall as before; fx: the E
    # recast's and R's dash pictures, baked on again (rig_akali_hd, Rig.bake)
    "akali": dict(ppu=72 / 40, edge=0, fx=True),
    # Sivir (2026-10-28, 「下一个英雄重做希维尔吧」, 「通过，用 2.25」): Codex's picture read as drawn (98 x 81,
    # design_sivir_hd.py: 81 rows / 2.25 = her 36); every action Codex's whole-frame redraw of her old frame read onto
    # it (tools/art/casts_sivir_hd.py), so no density change; the face point stays: she is as tall as before; fx: the
    # Q throw's, the W cast's and the catch's pictures, baked on again (rig_sivir_hd, Rig.bake)
    "sivir": dict(ppu=81 / 36, edge=0, fx=True),
    # Tristana (2026-10-28, 「下一个英雄重做崔丝塔娜」, 「通过，用 2.56」): Codex's raw read as drawn (103 x 87,
    # design_tristana_hd.py: 87 rows / 2.56 = her 34); every action Codex's whole-frame redraw of her old frame read onto
    # it (tools/art/casts_tristana_hd.py), so no density change; the face point stays: she is as tall as before; fx: the
    # shot, E, Q and R muzzle pictures, baked on again (rig_tristana_hd, Rig.bake)
    "tristana": dict(ppu=87 / 34, edge=0, fx=True),
    # Zed (2026-10-28, 「下一个英雄重做劫」, 「通过，用 1.62」): Codex's zed-A read as drawn (40 x 65, design_zed_hd.py:
    # 65 rows / 1.625 = his 40); every action Codex's whole-frame redraw of his old frame read onto it
    # (tools/art/casts_zed_hd.py), so no density change; the face point stays: he is as tall as before; nothing baked
    # (his shadows, the shuriken and the slashes are effect strips)
    "zed": dict(ppu=65 / 40, edge=0),
    # Vayne (2026-10-26, 「下一个英雄重做薇恩」): the user's own picture (「就用这个啊」) read on its own squares (85 x 102,
    # design_vayne_hd.py: 102 rows / 2.55 = her 40); every action Codex's whole-frame redraw of her old frame read onto
    # the design at the zoom her head gives (tools/art/casts_vayne_hd.py); drawn at 2.55 (ORIG_PPU), brought to 2.2
    # squares a game pixel like Jinx, Lux and Draven (「通过，用 2.2」 of 2.55 / 2.2 / 1.8 / 1.5); the face point between
    # her glasses (over her shoes' middle, 32 game px over the soles)
    # 2026-10-26 face (1,-36): (0,-32) framed her chin, the red collar and chest - the red glasses above the box
    "vayne": dict(ppu=2.2, edge=0, face_to=(1, -36)),
    # Lucian (2026-10-26, 「下一个英雄重做卢锡安 模型要和英雄联盟像一点」): Codex's picture after League's Lucian in his old
    # sprite's pose, read on its raw's own squares (111 x 93, design_lucian_hd.py: 93 rows / 46 = 2.02); every action
    # Codex's whole-frame redraw of his old frame read onto it at the zoom his head gives (tools/art/casts_lucian_hd.py);
    # kept at the density drawn (「通过，用 2.02 原样」), so no density change; the face point the portrait box's middle
    # as Vayne's fix (1,-36) taught: a game px under his crown (38 over the soles), a px ahead of his head's middle.
    # Then 「卢锡安的像素太高了调低一点 新模型」: picked 1.5 of 2.02 / 1.75 / 1.5 / 1.2 (tools/art/review_lucian_ppu.py,
    # 「卢锡安用 1.5」) - drawn at 2.02 (ORIG_PPU), brought to 1.5 squares a game pixel like Lee Sin, Riven and Jax
    "lucian": dict(ppu=1.5, edge=0, face_to=(-3, -37)),
    # league_heimerdinger: the design (Codex's step-1 A-2 cut to the user's 54 rows at 1.5 squares a game pixel: 「36」
    # 「PPU 1.5」, 3/4 only) with Codex's whole-body poses (the design's head pasted back) and the backpack crane / R's gear
    # props, posed by tools/art/rig_heimerdinger.py after League's clips, so no proportion change here; brought down to
    # 1.2 squares a game pixel (2026-10-22, the user: 「大发明家的像素太高了 可以调低一点」, 1.2 picked of 1.3 / 1.2 / 1.0); the
    # outer outline grown a square like the others; W's launch flash and the backpack's burst drawn into attack_w / dead
    # (orig/heimerdinger_<tag>.over.png) laid on after the outline (fx); the face point between his goggles (19 game px
    # over his soles, 4 ahead of his standing point)
    "heimerdinger": dict(ppu=1.2, edge=1, face_to=(4, -19), fx=True),
    # league_neeko (group F mid): posed by tools/art/rig_neeko.py on Codex's step-1 take A-1 and its key poses at the user's
    # 2.5 squares a game pixel (「40」, then 「1.5也挺糊的 还得往上调整吧」 -> 2.5: 100 rows quill tips to soles; 3/4 only), so
    # no proportion or density change here; the outer outline grown a square like the others; the face point between
    # her eyes (1 game px ahead of her standing point, 27 over the ground)
    "neeko": dict(ppu=2.5, edge=1, face_to=(1, -27)),
    # league_ksante (group G top): posed by tools/art/rig_ksante.py on Codex's step-1 takes A-2 (base) / O-1 (All Out, cut to
    # 56 rows: 「全盛裁到 56 格，和普通姿态身体一样大」) at the user's 1.5 squares a game pixel (「陀斧顶到脚底 48 游戏像素，PPU 1.5，
    # 只做四分之三侧面」: 72 rows ntofo tops to soles) and Codex's 27 skeleton poses with the design's head, so no proportion
    # change here; brought down to 1.2 squares a game pixel (2026-10-22, the user: 「奎桑提像素也太高了」, 1.2 picked); the outer outline grown a square like the others; the swings, Q's crack and burst and W's
    # dust baked into attack / skill* / skill2_dash and their All Out twins (orig/ksante_<tag>.over/.under.png) laid on
    # after the outline (fx); the face point between his eyes (36 game px over his soles, on his standing point)
    # 2026-10-22 evening: 90 % in game (「奎桑提的模型在游戏局内也太大了」, hd.rs SIZES): 11.5 x 1.2 x (1 / 0.9 - 1) = 1.5 -> 2
    # squares lower; the face point up from his eyes to just under his crown (「奎桑提的头像位置不对」: base heroes sit at the
    # crown; his hair top is 43.5 game px over his soles, -36 cut the portraits low) at -41, x 0.9 about the soles
    "ksante": dict(ppu=1.2, edge=1, lift_sq=-2, face_to=(1, -37), fx=True),
    # league_xerath (2026-10-21 PPU re-adjust, 「不是重做 是重新调整」): Codex's draft B read back on its own grid, slimmer
    # with a smaller head (tools/art/design_xerath_hd.py, the user's 「你选一个吧 反正游戏里别太大就行」), then shorter and a
    # little wider (「泽拉斯在游戏里身体太长了吧？」 -> take C: 35 x 62 squares, 1.55 squares a game pixel, 40 game px), posed
    # after League's clips by tools/art/rig_xerath_hd.py (his armour flying round the core in R), so no proportion or
    # density change here; the outer outline grown a square like the others; the attack / Q / E / R casts baked into his
    # frames (orig/xerath_<tag>.over.png) laid on after the outline (fx); the face point between his eyes (34 game px over
    # the ground: he floats 2 squares up)
    "xerath": dict(ppu=1.55, edge=1, face_to=(1, -34), fx=True),
    # tft_powder (the tft pack): the idle design (A-2) and Codex's skeleton poses with the one clean head, posed by
    # tools/art/rig_powder.py at 1.75 squares a game pixel (61 rows: 「35」, then 「PPU像素好低啊」 -> 1.75); shown at 90 % (the user:
    # 「人物模型太大 缩小一点」, league_main hd.rs SIZES), so the frames sit 2 squares lower (Poppy's way) to keep the
    # soles on the ground; the face point between her eyes
    "powder": dict(ppu=1.75, edge=1, lift_sq=-2, face_to=(0, -25)),
    # tft_norra (the tft pack's second hero, mid): the design (Codex's step-0 A-1 brought to 72 rows, 36 game px hat top to
    # soles, at the user's picks 「A-1 36px PPU2.0」, 3/4 only, the gold ring drawn into her near hand) with Codex's key
    # poses after the videos (the design's head put back), posed by tools/art/rig_norra.py, so no proportion or density
    # change here; the outer outline grown a square like the others - the channels it closes off (between a sleeve and
    # the robe, up to 12 squares) filled with the outline, the bigger gap it closed (her hand and head as she falls)
    # opened again, the one-square slits left in the outline closed (gap-check); the face point on her glasses' bridge, under the head wrap (her hat fills the top half of her:
    # 1 game px ahead of her standing point, 20 over the ground)
    "norra": dict(ppu=2.0, edge=1, face_to=(1, -20), pinholes=12, reopen=True, cracks=True),
    # tft_alune (the tft pack, mid): the design (Codex's step-0 A-1 riding the crescent, 90 rows, 46 game px horns to the
    # crescent's foot at the user's picks 「A-1 46 PPU 2.0」, 3/4 only) and Codex's key poses after her own TFT clips (the
    # design's head put back, the standing bodies Codex drew ~27% too big read at her skeletons' size), posed by
    # tools/art/rig_alune.py, so no proportion or density change here; the outer outline grown a square like the others;
    # the face point between her eyes (2 game px ahead of her standing point, 37 over the ground)
    "alune": dict(ppu=2.0, edge=1, face_to=(2, -37)),
    # tft_silco (the tft pack, mid): the design (Codex's step-0 A-1 leaning on his cane, 80 rows, 40 game px hair to
    # soles at the user's picks 「A-1 40 PPU 2.0」, 3/4 only, the scarred eye put back) and Codex's key poses after his
    # own TFT clips (the design's head put back, the bodies read at the design's build, gaps closed), posed by
    # tools/art/rig_silco.py, so no proportion or density change here; the outer outline grown a square like the others,
    # but not into the slits up to 3 squares wide where the cane passes a leg (open_slits: grown shut they turned into
    # black wedges); no pinholes: the loops the cane closes with his hand and boot are see-through and would be filled
    # whole (170+ squares); the one-square cracks in the outline and the gaps up to 15 squares the growth leaves between
    # an arm and the body filled (gap-check); the face point between his eyes (2 game px ahead of his standing point, 33
    # over the ground)
    "silco": dict(ppu=2.0, edge=1, face_to=(2, -33), slits=3, cracks=True, fill_holes=15),
    # tft_maddie (the tft pack, bot): the design (Codex's step-0 A-1 with the rifle on her shoulder, 57 rows, 38 game px
    # beret to soles at the user's picks 「A-1 38 PPU 1.5」, the far eye and mouth redrawn) and Codex's key poses after
    # her own TFT clips (drawn on the design's grid in its colours, the design's head put in, gaps closed), posed by
    # tools/art/rig_maddie.py with the muzzle flashes as over layers (orig/maddie_<tag>.over.png, laid on after the
    # outline: fx), so no proportion or density change here; the outer
    # outline grown a square like the others, its one-square cracks closed and the small holes filled (gap-check); the
    # face point between her eyes (1 game px ahead of her standing point, 31 over the ground)
    "maddie": dict(ppu=1.5, edge=1, face_to=(1, -31), cracks=True, fill_holes=15, fx=True),
    # tft_loris (the tft pack, support): the design (Codex's step-0 B-1 with the tower shield at his side, 84 rows, 42
    # game px hair to soles at the user's picks 「B-1 42 PPU 2.0」, the far eye drawn in) and Codex's key poses after his
    # own TFT clips (drawn on the design's grid, taken to its colours, the design's head put in, gaps closed), posed by
    # tools/art/rig_loris.py where Codex placed them, so no proportion or density change here; the outer outline grown a
    # square like the others, its one-square cracks closed and the small holes filled (gap-check); the face point
    # between his eyes (1 game px ahead of his standing point, 36 over the ground)
    "loris": dict(ppu=2.0, edge=1, face_to=(1, -36), cracks=True, fill_holes=15),
    # tft_kobuko (the tft pack, top): the design (Codex's step-0 A-1 stroking his beard, 80 rows, 40 game px topknot to
    # soles at the user's picks 「A-1 40 PPU 2.0」) and Codex's key poses after his own TFT clips (taken to its colours,
    # one size for all, the design's head put in, gaps closed; the run the heavy walk on the design), posed by
    # tools/art/rig_kobuko.py where Codex placed them, so no proportion or density change here; the outer outline grown
    # a square like the others, its one-square cracks closed and the small holes filled (gap-check); the face point at
    # his eye (1 game px behind his standing point, 33 over the ground)
    "kobuko": dict(ppu=2.0, edge=1, face_to=(-1, -33), cracks=True, fill_holes=15),
    # tft_vander (the tft pack, jungle): the design (Codex's step-0 B-2, the low fighting stance, 80 rows, 40 game px hair
    # to soles at the user's picks 「B-2 40 PPU 2.0」, the forehead's skin put back) and Codex's key poses after his own
    # TFT clips (taken to its colours, the design's head put in, gaps closed), posed by tools/art/rig_vander.py where
    # Codex placed them (the run Codex's redraw of his TFT run, RUN_PROMPTS.md), so no proportion or density change here; the
    # outer outline grown a square like the others, its one-square cracks closed and the small holes filled
    # (gap-check); the face point between his eyes (8 game px ahead of his standing point - the stance leans his head
    # forward - and 34 over the ground)
    "vander": dict(ppu=2.0, edge=1, face_to=(8, -34), cracks=True, fill_holes=15),
    # tft_violet (the tft pack, jungle): the design (Codex's step-0 B-1, the fighting stance with both gauntlets up, 76
    # rows, 38 game px hair to soles at the user's picks 「B-1 38 PPU 2.0」, the eyes and brows redrawn on the grid) and
    # Codex's key poses after her own TFT clips (read on Codex's own 10-12 px squares, taken to its colours, the
    # design's head put in, gaps closed), posed by tools/art/rig_violet.py, so no proportion or density change here; the
    # outer outline grown a square like the others, its one-square cracks closed and the small holes filled (the
    # openings between an arm and the body, 22-37 squares, are real and outlined); the face point between her eyes
    # (4 game px ahead of her standing point and 30 over the ground)
    "violet": dict(ppu=2.0, edge=1, face_to=(4, -30), cracks=True, fill_holes=15),
    # tft_krug (the tft pack, jungle): the design (Codex's step-0 A-1, hunched on all fours, 76 rows, 38 game px boulder
    # to soles at the user's picks 「A-1 38 PPU 2.0」) and Codex's key poses after his own TFT clips (one factor for all,
    # taken to its colours, gaps closed), posed by tools/art/rig_krug.py where Codex placed them, so no proportion or
    # density change here; the outer outline grown a square like the others, its one-square cracks closed and the small
    # holes filled (gap-check); the face point at his small shell face low at his front (10 game px ahead of his standing
    # point, 9 over the ground)
    "krug": dict(ppu=2.0, edge=1, face_to=(10, -9), cracks=True, fill_holes=15),
    # tft_aoshin (the tft pack, mid): the design (Codex's step-0 A-1, the storm dragon hovering upright, 76 rows, 38 game
    # px horns to the tail's lowest curl at the user's picks 「A-1 38 PPU 2.0」) and Codex's key poses after his own TFT
    # clips (read square for square: Codex kept the 12 px grid and the design's colours), posed by tools/art/rig_aoshin.py
    # by the pack's hip column, so no proportion or density change here; the outer outline grown a square like the
    # others, its one-square cracks closed and the small holes filled (gap-check); the face point between his eyes under
    # the gold mask (4 game px ahead of his standing point, 27 over the ground)
    "aoshin": dict(ppu=2.0, edge=1, face_to=(4, -27), cracks=True, fill_holes=15),
    # tft_scar (the tft pack, top): the design (Codex's step-0 B-1, the spear guard point forward, 76 rows, 38 game px
    # mohawk to soles at the user's picks 「B-1、38 游戏像素、PPU 2.0」) and Codex's key poses after his own TFT clips
    # (drawn on the design's 12 px squares with its head pasted; the falls given the design's head by
    # design_scar_poses.py), posed by tools/art/rig_scar.py, so no proportion or density change here; the outer outline
    # grown a square like the others, its one-square cracks closed and the small holes filled; the face point between
    # the mask's eye sockets (9 game px ahead of his standing point and 30 over the ground)
    "scar": dict(ppu=2.0, edge=1, face_to=(9, -30), cracks=True, fill_holes=15),
    # tft_renni (the tft pack, top): the design (Codex's step-0 B-1, the stance, the chainsaw level forward, 76 rows, 38
    # game px hair to soles at the user's picks 「B-1、38 像素、PPU 2.0」) and Codex's key poses after her own TFT clips
    # (read on the 12 px squares Codex drew them on, the design's head and collar laid over; the falls keep Codex's
    # tilted head: design_renni_poses.py), posed by tools/art/rig_renni.py, so no proportion or density change here; the
    # outer outline grown a square like the others, its one-square cracks closed and the small holes filled; the face
    # point between her eyes (5 game px ahead of her standing point and 28 over the ground)
    "renni": dict(ppu=2.0, edge=1, face_to=(5, -28), cracks=True, fill_holes=15),
    # tft_smeech (the tft pack, jungle): the design (Codex's step-0 B-1, the ambush crouch claws spread, 87 rows, 36 game
    # px hat to claw tips at the user's picks 「B-1 36像素 PPU2.4」, one square a pixel) and Codex's key poses after his
    # own TFT clips (read on the pack's 9 px squares, the design's head pasted on every standing pose by
    # design_smeech_poses.py), posed by tools/art/rig_smeech.py, so no proportion or density change here; the outer
    # outline grown a square like the others, its one-square cracks closed and the small holes filled; the face point
    # between his eyes (14 game px ahead of his standing point and 17 over the ground)
    "smeech": dict(ppu=2.4, edge=1, face_to=(14, -17), cracks=True, fill_holes=15),
}
NIDALEE_COUGAR = {"c_idle": 6, "c_run": 8, "c_attack": 4, "c_skill": 5, "c_pounce": 6, "c_swipe": 4, "c_transform": 3,
                  "c_hit": 2, "c_dead": 6}
# (hero, tag, frame) -> ("lie", "l" | "r", neck x, neck y from the pivot) | ("up", neck x, neck y from the pivot) |
# ("body",) (no head: the body's change only) | ("none",)
FRAMES = {
    **{("zeri", "dead", i): ("lie", "r", 36.5, 3.5) for i in (4, 5, 6, 7)},
    **{("karma", "dead", i): ("lie", "r", 7.5, 17.5) for i in (2, 3, 4, 5, 6, 7)},
    ("karma", "dead", 1): ("up", 20.5, 13.5),
    **{("nidalee", t, i): ("none",) for t, n in NIDALEE_COUGAR.items() for i in range(n)},
    # lying (dead 4-6) and the low lunge (skill 5): the body only; hit = the idle moved 4 / 2 back (its neck with it)
    **{("nidalee", "dead", i): ("body",) for i in (3, 4, 5)},
    ("nidalee", "skill", 4): ("body",),
    ("nidalee", "hit", 0): ("up", 1.5, -67.5),
    ("nidalee", "hit", 1): ("up", 3.5, -67.5),
}


# ----------------------------------------------------------------------------------------------- frames in and out
def read_orig(hero):
    """{tag: [(dense frame, ms)]} - the frames this tool starts from (saved from the sheet on the first run)."""
    sheet = P.read_sheet(P.stem_of(hero))
    tags = [t for t in sheet if P.plain(t)]
    os.makedirs(ORIG, exist_ok=True)
    out = {}
    for t in tags:
        png = os.path.join(ORIG, f"{hero}_{t}.png")
        side = os.path.join(ORIG, f"{hero}_{t}.json")
        hd = sheet.get(P.PREFIX + t) or sheet[t]          # (the 1x tag has the same timing)
        if not os.path.isfile(png):
            frames = [a for a, _ in hd]
            H = max(a.shape[0] for a in frames)
            strip = np.zeros((H, sum(a.shape[1] + 1 for a in frames) - 1, 4), np.uint8)
            x = 0
            for a in frames:
                strip[:a.shape[0], x:x + a.shape[1]] = a
                x += a.shape[1] + 1
            Image.fromarray(strip).save(png)
            with open(side, "w", encoding="utf-8", newline="\n") as f:
                json.dump({"sizes": [[a.shape[1], a.shape[0]] for a in frames], "ppu": P.PPU[hero]}, f)
        s = np.asarray(Image.open(png).convert("RGBA"))
        if os.path.isfile(side):
            with open(side, encoding="utf-8") as f:
                meta = json.load(f)
        else:                                   # a tool that writes no size list: each frame PPU x its 1x frame
            meta = {"sizes": [list(P.hd_size(a.shape[1], a.shape[0], ORIG_PPU[hero])) for a, _ in sheet[t]]}
        frames, x = [], 0
        for W, H in meta["sizes"]:
            frames.append(s[:H, x:x + W].copy())
            x += W + 1
        out[t] = [(a, ms) for a, (_, ms) in zip(frames, hd)]
    return out, sheet, ORIG_PPU.get(hero, meta.get("ppu", P.PPU[hero]))


def read_fx(hero, tag):
    """The effects a rig laid out for this tag's frames (orig/<hero>_<tag>.over.png / .under.png, cut like its frames):
    (over frames, under frames), a list of None for a strip that is not there."""
    side = os.path.join(ORIG, f"{hero}_{tag}.json")
    if not os.path.isfile(side):
        return None, None
    with open(side, encoding="utf-8") as f:
        sizes = json.load(f)["sizes"]
    out = []
    for suf in ("over", "under"):
        png = os.path.join(ORIG, f"{hero}_{tag}.{suf}.png")
        if not os.path.isfile(png):
            out.append([None] * len(sizes))
            continue
        s = np.asarray(Image.open(png).convert("RGBA"))
        frames, x = [], 0
        for W, H in sizes:
            a = s[:H, x:x + W].copy()
            frames.append(a if a[..., 3].any() else None)
            x += W + 1
        out.append(frames)
    return out


def put_fx(content, e, over, under):
    """The effects on a restyled frame: their squares as drawn on its frame before the restyle (the content is that
    frame grown e squares at each side by the outline)."""
    content = content.copy()
    for a, top in ((under, False), (over, True)):
        if a is None:
            continue
        a = np.pad(a, ((e, e), (e, e), (0, 0)))[:content.shape[0], :content.shape[1]]
        m = a[..., 3] > 0
        if not top:
            m &= content[..., 3] == 0
        content[m] = a[m]
    return content


# ----------------------------------------------------------------------------------------------- the head
def find_face(a, tpl):
    """(row, col) of the template's top-left where it fits `a` best, and the mean squared error there (per opaque
    template pixel and channel, a clear frame pixel counting as 255 off)."""
    m = (tpl[..., 3] > 0).astype(float)
    if a.shape[0] < tpl.shape[0] or a.shape[1] < tpl.shape[1]:
        return None, 1e9
    F = a[..., :3].astype(float) * (a[..., 3:] > 0)
    T = tpl[..., :3].astype(float)
    clear = (a[..., 3] == 0).astype(float)
    score = signal.correlate(clear, m, mode="valid", method="fft") * 3 * 255.0 ** 2
    for c in range(3):
        score += signal.correlate(F[..., c] ** 2, m, mode="valid", method="fft")
        score -= 2 * signal.correlate(F[..., c], m * T[..., c], mode="valid", method="fft")
        score += (m * T[..., c] ** 2).sum()
    score /= m.sum() * 3
    y, x = np.unravel_index(np.argmin(score), score.shape)
    return (int(y), int(x)), float(score[y, x])


# ----------------------------------------------------------------------------------------------- the warp
class Warp:
    """Source -> drawn positions (continuous pixel coordinates, the frame's own; the pivot at its centre). `reach`:
    upright, the body is widened only within `reach` dense columns of the pivot (the idle's own half width) - what
    sticks out further (a gun held out, an arm thrown forward) keeps its length and only moves out with the body."""

    def __init__(self, mode, side, nx, ny, px, gy, head, wide, short, band, reach=None):
        self.mode, self.side = mode, side
        self.nx, self.ny, self.px, self.gy = nx, ny, px, gy
        self.s, self.bx, self.by, self.t = head, wide, short, max(band, 1e-3)
        self.R = reach if reach else 1e9
        if mode == "up":
            self.nx2, self.ny2 = px + self.g(nx - px), gy + short * (ny - gy)
        else:
            self.nx2, self.ny2 = px + short * (nx - px), gy + wide * (ny - gy)

    def g(self, d):
        """The body's widening of a column d from the pivot: wide x within reach, 1 x beyond."""
        ad = np.abs(d)
        return np.sign(d) * (self.bx * np.minimum(ad, self.R) + np.maximum(ad - self.R, 0))

    def w(self, u):
        """1 in the head, 0 in the body, linear across the band (u: source row, or column when lying)."""
        if self.mode == "up":
            return np.clip((self.ny + self.t - u) / (2 * self.t), 0, 1)
        if self.side == "r":
            return np.clip((u - (self.nx - self.t)) / (2 * self.t), 0, 1)
        return np.clip(((self.nx + self.t) - u) / (2 * self.t), 0, 1)

    def along(self, u):
        """The drawn row (upright) / column (lying) of source row / column u."""
        w = self.w(u)
        if self.mode == "up":
            head = self.ny2 + self.s * (u - self.ny)
            body = self.gy + self.by * (u - self.gy)
        else:
            head = self.nx2 + self.s * (u - self.nx)
            body = self.px + self.by * (u - self.px)
        return w * head + (1 - w) * body

    def across(self, v, u):
        """The drawn column (upright: v a source column on source row u) / row (lying: v a source row, u a column)."""
        w = self.w(u)
        if self.mode == "up":
            head = self.nx2 + self.s * (v - self.nx)
            body = self.px + self.g(v - self.px)
        else:
            head = self.gy + self.s * (v - self.gy)
            body = self.gy + self.bx * (v - self.gy)
        return w * head + (1 - w) * body

    def forward(self, x, y):
        if self.mode == "up":
            return self.across(x, y), self.along(y)
        return self.along(x), self.across(y, x)

    def render(self, a, out_shape, off):
        """`a` drawn on a canvas of out_shape whose pixel (0, 0) is the source's (-off[1], -off[0])."""
        H, W = a.shape[:2]
        Ho, Wo = out_shape
        lim = max(H, W) * 2
        us = np.linspace(-lim, lim + max(H, W), 20000)
        al = self.along(us)
        if self.mode == "up":
            yc = np.arange(Ho) + 0.5 - off[0]
            ys = np.interp(yc, al, us)
            xc = np.arange(Wo) + 0.5 - off[1]
            vs = np.linspace(-W, 2 * W, 6 * W + 1)
            xs = np.empty((Ho, Wo))
            for r in range(Ho):
                xs[r] = np.interp(xc, self.across(vs, ys[r]), vs)
            ysg = np.broadcast_to(ys[:, None], xs.shape)
        else:
            xc = np.arange(Wo) + 0.5 - off[1]
            xs1 = np.interp(xc, al, us)
            w = self.w(xs1)
            S = w * self.s + (1 - w) * self.bx
            yc = np.arange(Ho) + 0.5 - off[0]
            ysg = self.gy + (yc[:, None] - self.gy) / S[None, :]
            xs = np.broadcast_to(xs1[None, :], ysg.shape)
        iy, ix = np.floor(ysg).astype(int), np.floor(xs).astype(int)
        ok = (iy >= 0) & (iy < H) & (ix >= 0) & (ix < W)
        out = np.zeros((Ho, Wo, 4), np.uint8)
        out[ok] = a[iy[ok], ix[ok]]
        return out


def scale_even(a, k):
    """Nearest, k times its size (k > 0)."""
    h, w = a.shape[:2]
    H, W = max(1, round(h * k)), max(1, round(w * k))
    ys = np.minimum(((np.arange(H) + 0.5) / k).astype(int), h - 1)
    xs = np.minimum(((np.arange(W) + 0.5) / k).astype(int), w - 1)
    return a[ys][:, xs]


# ----------------------------------------------------------------------------------------------- colours
def close_pinholes(grown, n, colour, most=2, before=None):
    """The enclosed holes of at most `most` squares in a frame grow_edge(.., n, ..) grew (a clear square the grown outline
    closed in at a diagonal notch: a speck of ground in the body) filled with the outline. The rigs' frames have no
    enclosed holes of their own (rig_rumble closes them), so every one this small is the growth's. With `before` (the
    frame before the growth), a bigger hole the growth closed off - open to the outside before it: a see-through gap of
    the pose, tft_norra's between her raised hand and her head as she falls - is opened again where the growth shut it:
    the grown squares on the shortest way out through the growth taken off with their grown neighbours (a mouth two or
    three squares wide, no one-square crack), the rest of the gap keeping its new outline. A bigger hole the growth did
    not close, or one with no way out through grown squares, is filled with the outline too."""
    op = grown[..., 3] > 0
    lb, k = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    if not k:
        return grown
    out = grown.copy()
    sizes = ndimage.sum(np.ones_like(op), lb, range(1, k + 1))
    if before is not None:
        was = np.pad(before[..., 3] > 0, n)
        free, _ = ndimage.label(~was)
        open_before = free == free[0, 0]
        ring = op & ~was
        now, _ = ndimage.label(~op)
        outside = now == now[0, 0]
    for j, sz in enumerate(sizes, 1):
        h = lb == j
        if sz > most and before is not None and (h & open_before).any():
            way = way_out(h, ring, outside)
            if way is not None:
                mouth = ndimage.binary_dilation(way, structure=CROSS) & ring
                out[mouth] = 0
                continue
        out[h, :3] = colour
        out[h, 3] = 255
    return out


def close_cracks(a, colour):
    """One-square cracks in the outline (a clear square between two outline squares, left and right or above and below:
    ground showing through a slit between a held ring and the sleeve - gap-check) filled with the outline."""
    line = (a[..., 3] > 0) & np.all(a[..., :3] == np.array(colour, a.dtype), -1)
    p = np.pad(line, 1)
    crack = (a[..., 3] == 0) & ((p[1:-1, :-2] & p[1:-1, 2:]) | (p[:-2, 1:-1] & p[2:, 1:-1]))
    out = a.copy()
    out[crack, :3] = colour
    out[crack, 3] = 255
    return out


def way_out(h, ring, outside):
    """The shortest 4-connected way from the hole `h` through `ring` squares to a square beside `outside`: its ring
    squares as a mask, or None."""
    from collections import deque
    H, W = h.shape
    prev = {p: None for p in zip(*np.nonzero(h))}
    q = deque(prev)
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < H and 0 <= nx < W) or (ny, nx) in prev:
                continue
            if outside[ny, nx]:
                way = np.zeros_like(h)
                p = (y, x)
                while p is not None:
                    if ring[p]:
                        way[p] = True
                    p = prev[p]
                return way
            if ring[ny, nx]:
                prev[(ny, nx)] = (y, x)
                q.append((ny, nx))
    return None


def fill_holes(a, most):
    """The enclosed clear holes of at most `most` squares (ground showing through the body where the coarser grid
    closed a thin gap round a speck of it - league_samira at 2.2) filled with the commonest colour round each."""
    op = a[..., 3] > 0
    lb, k = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = a.copy()
    for j in range(1, k + 1):
        h = lb == j
        if h.sum() > most:
            continue
        ring = ndimage.binary_dilation(h, structure=np.ones((3, 3), bool)) & ~h & op
        cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
        out[h, :3] = cols[cnt.argmax()]
        out[h, 3] = 255
    return out


def coarse_look(a, pivot, k, outline, holes=0, keep=None):
    """`a` brought to k times as many squares a side (pixelate) and laid back on its own grid - every pixel the colour
    of the coarse square it falls in - its enclosed holes of up to `holes` squares filled (and, laid back, any of
    up to 3 pixels), the pixels `keep` marks put back as drawn (league_samira: her face kept fine in a coarse
    body)."""
    c, pv = pixelate(a, k, pivot, outline)
    if holes:
        c = fill_holes(c, holes)
    H, W = a.shape[:2]
    cx = np.floor((np.arange(W) + 0.5 - pivot[0]) * k).astype(int) + pv[0]
    cy = np.floor((np.arange(H) + 0.5 - pivot[1]) * k).astype(int) + pv[1]
    okx, oky = (cx >= 0) & (cx < c.shape[1]), (cy >= 0) & (cy < c.shape[0])
    out = np.zeros_like(a)
    out[np.ix_(oky, okx)] = c[np.ix_(cy[oky], cx[okx])]
    if keep is not None:
        out[keep] = a[keep]
    return fill_holes(out, 3) if holes else out


def grow_edge(a, n, colour):
    if n <= 0:
        return a
    a = np.pad(a, ((n, n), (n, n), (0, 0)))
    op = a[..., 3] > 0
    ring = ndimage.binary_dilation(op, structure=CROSS, iterations=n) & ~op
    a = a.copy()
    a[ring, :3] = colour
    a[ring, 3] = 255
    return a


def open_slits(grown, before, n, w):
    """The squares grow_edge(.., n, ..) laid in a narrow slit between two parts (clear in `before`, with a part of the
    figure at most `w` squares away on both sides, left and right or above and below - tft_silco's cane passing a leg
    two or three squares apart) cleared again: both sides keep their own outline and the slit stays open, where the
    grown outline filled it shut into a black wedge."""
    was = np.pad(before[..., 3] > 0, n)
    p = np.pad(was, w)
    H, W = was.shape
    left = np.zeros_like(was)
    right = np.zeros_like(was)
    up = np.zeros_like(was)
    down = np.zeros_like(was)
    for k in range(1, w + 1):
        left |= p[w:w + H, w - k:w - k + W]
        right |= p[w:w + H, w + k:w + k + W]
        up |= p[w - k:w - k + H, w:w + W]
        down |= p[w + k:w + k + H, w:w + W]
    slit = ~was & ((left & right) | (up & down)) & (grown[..., 3] > 0)
    out = grown.copy()
    out[slit] = 0
    return out


def fit(content, pivot, W, H, exact_w=None):
    """`content` (its pivot at `pivot`) on a frame of at least W x H grown alike at both ends, the pivot at the centre;
    exact_w: the width it must have. -> frame (None when it does not fit exact_w)."""
    op = content[..., 3] > 0
    if not op.any():
        return np.zeros((H, W, 4), np.uint8)
    ys, xs = np.nonzero(op)
    hw = max(pivot[0] - xs.min(), xs.max() + 1 - pivot[0])
    hh = max(pivot[1] - ys.min(), ys.max() + 1 - pivot[1])
    Wn = W
    while Wn / 2 < hw:
        Wn += 2
    Hn = H
    while Hn / 2 < hh:
        Hn += 2
    if exact_w is not None:
        if Wn > exact_w:
            return None
        Wn = exact_w
    out = np.zeros((Hn, Wn, 4), np.uint8)
    dx, dy = Wn / 2 - pivot[0], Hn / 2 - pivot[1]
    ox, oy = int(np.floor(dx + 0.5)), int(np.floor(dy + 0.5))
    yy, xx = ys + oy, xs + ox
    ok = (yy >= 0) & (yy < Hn) & (xx >= 0) & (xx < Wn)
    out[yy[ok], xx[ok]] = content[ys[ok], xs[ok]]
    return out


# ----------------------------------------------------------------------------------------------- one frame
def restyle_frame(hero, tag, i, a, spec, ppu, tpl, neck_off, outline, reach=None, ring_tpl=None):
    """-> (content, pivot (x, y), note)."""
    fixk = spec.get("fix", {}).get((tag, i))
    if fixk:
        # a frame Codex drew smaller than the rest, brought to the others' size round the pivot and the ground row
        H0, W0 = a.shape[:2]
        big = scale_even(a, fixk)
        gy0 = H0 / 2 + FEET * ppu
        pvx, pvy = W0 / 2 * fixk, gy0 * fixk - FEET * ppu
        Hb, Wb = big.shape[:2]
        Wf, Hf = int(2 * np.ceil(max(pvx, Wb - pvx))) + 2, int(2 * np.ceil(max(pvy, Hb - pvy))) + 2
        can = np.zeros((Hf, Wf, 4), np.uint8)
        ox, oy = int(round(Wf / 2 - pvx)), int(round(Hf / 2 - pvy))
        can[oy:oy + Hb, ox:ox + Wb] = big
        a = can
    H, W = a.shape[:2]
    px, py = W / 2, H / 2
    gy = py + FEET * ppu
    content, pivot, note = a, (px, py), ""
    if spec.get("head", 1) != 1 or spec.get("wide", 1) != 1 or spec.get("short", 1) != 1:
        how = FRAMES.get((hero, tag, i))
        if how is None and spec.get("body_only"):
            how = ("body",)
        if how is None:
            (fy, fx), err = find_face(a, tpl)
            if err > spec.get("max_err", 1500):
                how = ("body",)
                note = f"no head (err {err:.0f})"
            else:
                how = ("up", fx + neck_off[0], fy + neck_off[1])
                note = f"head at {fx},{fy} err {err:.0f}"
        if how[0] == "none":
            warp = None
        elif how[0] == "body":
            warp = Warp("up", None, px, -1e6, px, gy, 1.0, spec["wide"], spec["short"], spec.get("band", 2), reach)
        elif how[0] == "up":
            nx, ny = (how[1], how[2]) if note else (px + how[1], py + how[2])
            warp = Warp("up", None, nx, ny, px, gy, spec["head"], spec["wide"], spec["short"],
                        spec.get("band", 2), reach)
        else:
            warp = Warp("lie", how[1], px + how[2], py + how[3], px, gy, spec["head"], spec["wide"], spec["short"],
                        spec.get("band", 2))
            note = f"lying, head {how[1]}"
        WARPS[(hero, tag, i)] = warp
        if warp is not None:
            ring = None
            if spec.get("ring") is not None and ring_tpl is not None and how[0] == "up":
                a, ring = take_ring(a, ring_tpl, spec)
                if ring is not None:
                    a = drop_specks(a, 24)
            m = int(max(H, W) * 0.6)
            Ho, Wo = H + 2 * m, W + 2 * m
            content = warp.render(a, (Ho, Wo), (m, m))
            pivot = (px + m, py + m)
            if ring is not None:
                put_ring(content, ring, warp, spec["ring"], (m, m))
    if spec.get("lift"):
        # moved up whole (lossless): a hero drawn bigger by hd.rs SIZES keeps its soles on the ground
        pivot = (pivot[0], pivot[1] + spec["lift"])
    if spec.get("grow", 1) != 1:
        # evenly bigger round the pivot column and the ground row (the soles stay FEET below the pivot)
        k = spec["grow"]
        gyc = pivot[1] + FEET * ppu
        if spec.get("ppu", ppu) == ppu:
            # no coarser grid follows to even it out: doubled exactly, then brought to k / 2 by area (pixel_down) -
            # every square the same size, none doubled (league_irelia)
            big = scale_even(content, 2)
            content, (qx, qy) = pixelate(big, k / 2, (pivot[0] * 2, pivot[1] * 2), outline)
            # the grid runs through the pivot, so the soles land FEET * ppu * k under it: the pivot taken that much
            # lower less FEET * ppu, so they sit FEET * ppu under it again
            pivot = (float(qx), float(qy) + FEET * ppu * (k - 1))
        else:
            content = scale_even(content, k)
            pivot = (pivot[0] * k, gyc * k - FEET * ppu)
    return content, pivot, note


def ring_template(first, spec):
    """Karma's halo in the idle's first frame: its colours (with the outline next to them, `ring_rows` rows from the
    top) -> (pixels, its top-left) - the same halo is pasted in every upright frame."""
    cols = np.array(spec["ring_colours"])
    rgb = first[..., :3].astype(int)
    op = first[..., 3] > 0
    jade = op & (np.abs(rgb[:, :, None, :] - cols[None, None]).sum(-1) == 0).any(-1)
    jade[spec["ring_rows"]:] = False
    lab, n = ndimage.label(jade, structure=np.ones((3, 3)))
    sizes = ndimage.sum(jade, lab, range(1, n + 1))
    core = lab == int(np.argmax(sizes)) + 1
    dark = op & (rgb.sum(-1) < 70)
    m = core | (dark & ndimage.binary_dilation(core, structure=np.ones((3, 3)), iterations=2))
    m[spec["ring_rows"]:] = False
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    pix = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    sub = m[y0:y1, x0:x1]
    pix[sub] = first[y0:y1, x0:x1][sub]
    return pix


def take_ring(a, tpl, spec):
    """The halo found in `a` (the template where the frame matches it best) and taken out: only the pixels equal to
    the template's go. -> (frame without it, (pixels, box)) or (a, None) when it is not there."""
    (ry, rx), err = find_face(a, tpl)
    if err > spec.get("ring_err", 800):
        return a, None
    h, w = tpl.shape[:2]
    win = a[ry:ry + h, rx:rx + w]
    same = (tpl[..., 3] > 0) & (np.abs(win.astype(int) - tpl.astype(int)).sum(-1) == 0)
    out = a.copy()
    out[ry:ry + h, rx:rx + w][same] = 0
    return out, (tpl, (ry, ry + h, rx, rx + w))


def drop_specks(a, most):
    """Pieces of at most `most` pixels standing apart from the rest (what is left of the halo's outline)."""
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n < 2:
        return a
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    small = np.isin(lab, np.nonzero(sizes <= most)[0] + 1)
    out = a.copy()
    out[small] = 0
    return out


def put_ring(content, ring, warp, k, off):
    """The halo back, k times its size, its bottom middle where the warp sends it, behind what is drawn there."""
    pix, (y0, y1, x0, x1) = ring
    ax, ay = (x0 + x1) / 2, y1
    bx, by = warp.forward(np.array(float(ax)), np.array(float(ay)))
    small = scale_even(pix, k)
    top = int(round(float(by) + off[0] - small.shape[0]))
    left = int(round(float(bx) + off[1] - small.shape[1] / 2))
    m = small[..., 3] > 0
    ys, xs = np.nonzero(m)
    yy, xx = ys + top, xs + left
    ok = (yy >= 0) & (yy < content.shape[0]) & (xx >= 0) & (xx < content.shape[1])
    yy, xx, ys, xs = yy[ok], xx[ok], ys[ok], xs[ok]
    behind = content[yy, xx, 3] == 0
    content[yy[behind], xx[behind]] = small[ys[behind], xs[behind]]



def narrow(a, y0, s):
    """A striding frame's legs brought together (league_mordekaiser's run: 「铁男的走路步伐感觉有点大啊」): every row from
    y0 down, the back leg's pixels move right and the front leg's left by s x (row - y0) / (soles - y0) dense pixels
    (rounded) - the soles 2 s nearer, each leg's pixels row for row (nothing squashed), the front leg drawn over the
    back one where they meet. The legs: the two largest 8-connected parts of the rows below the first row ys (>= y0)
    from which down they come apart; every other part there goes with the nearer leg; above ys (the hips, the skirt)
    a row splits at the middle of the gap between the two legs' tops."""
    op = a[..., 3] > 0
    sole = int(np.nonzero(op.any(1))[0].max())
    for ys in range(y0, sole):
        lab, n = ndimage.label(op[ys:sole + 1], structure=np.ones((3, 3)))
        if n < 2:
            continue
        sizes = ndimage.sum(np.ones_like(lab), lab, index=range(1, n + 1))
        big = np.argsort(sizes)[::-1][:2] + 1
        if sizes[big[1] - 1] >= 0.2 * sizes[big[0] - 1]:
            break
    else:
        return a
    cx = {k: np.nonzero(lab == k)[1].mean() for k in range(1, n + 1)}
    back, front = sorted(big, key=lambda k: cx[k])
    side = np.zeros(op.shape, np.int8)                      # 1 back leg, 2 front leg, 0 above ys / clear
    for k in range(1, n + 1):
        side[ys:sole + 1][lab == k] = 1 if abs(cx[k] - cx[back]) <= abs(cx[k] - cx[front]) else 2
    top_b = np.nonzero(lab[0] == back)[0]
    top_f = np.nonzero(lab[0] == front)[0]
    split = ((top_b.max() if len(top_b) else cx[back]) + (top_f.min() if len(top_f) else cx[front]) + 1) / 2.0
    cols = np.arange(op.shape[1])
    for y in range(y0, ys):
        side[y][op[y]] = np.where(cols[op[y]] < split, 1, 2)
    out = a.copy()
    W = op.shape[1]
    for y in range(y0, sole + 1):
        d = int(round(s * (y - y0) / max(1, sole - y0)))
        if not d:
            continue
        new = np.zeros_like(a[y])
        for leg, dx in ((1, d), (2, -d)):                   # the back leg first, the front one over it
            xs = np.nonzero(side[y] == leg)[0]
            to = xs + dx
            ok = (to >= 0) & (to < W)
            new[to[ok]] = a[y, xs[ok]]
        out[y] = new
    return out

# ----------------------------------------------------------------------------------------------- one hero
def restyle(hero, spec, write=True, only=None):
    frames, sheet, ppu = read_orig(hero)
    # legs brought together first (narrow); the frames as they were kept for the crisp palette (every other frame's
    # colours stay exactly as before)
    unnarrowed = {}
    for tag, (y0, shifts) in spec.get("stride", {}).items():
        for i, k in shifts.items():
            unnarrowed[(tag, i)] = frames[tag][i][0]
        frames[tag] = [(narrow(a, y0, shifts[i]) if shifts.get(i) else a, ms) for i, (a, ms) in enumerate(frames[tag])]
    new_ppu = spec.get("ppu", ppu)
    first = frames["idle"][0][0]
    outline = tuple(spec["outline"]) if spec.get("outline") else edge_colour(first)
    tpl = neck_off = None
    if "face" in spec:
        r0, r1, c0, c1 = spec["face"]
        tpl = first[r0:r1, c0:c1]
        if spec.get("neck"):
            nx, ny = spec["neck"]
        else:
            ny = spec["neck_row"]
            op = first[..., 3] > 0
            nx = np.nonzero(op[max(0, ny - 3):ny + 4])[1].mean() + 0.5
        neck_off = (nx - c0, ny - r0)
    # the body is widened within the idle's own half width round the pivot (spec "reach" overrides, in dense pixels)
    op = first[..., 3] > 0
    reach = spec.get("reach") or float(np.abs(np.nonzero(op)[1] + 0.5 - first.shape[1] / 2).max())
    ring_tpl = ring_template(first, spec) if spec.get("ring") is not None else None
    out, notes = {}, []
    # coarse (league_nidalee's cougar): those tags' frames drawn `size` times as big on a grid of `grid` squares a game
    # pixel, the soles kept FEET under the pivot; brought to new_ppu after the crisp. was: (tag, i) -> (the frame as it
    # would have been, its pivot): the crisp palette, and each frame's soles put back on the row they had there (the
    # coarse squares alone moved them up to 0.9 game px between frames)
    co, was = spec.get("coarse"), {}
    # shared_palette: every frame snaps to the commonest colours of all the hero's frames together, not only its own -
    # league_gragas's idle (the hand-finished design, 2597 colours) had no blue among its own 64 commonest, so his
    # trousers came out grey in the idle and blue in every action (「怎么裤子还变色啊」)
    # shared_palette_skip: (tag, frame) pairs kept out of it and snapped to their own colours - league_wukong's flashed
    # hit frame (its pale squares took places in the palette and turned gold squares grey in every other frame)
    shared = None
    skip = {tuple(k) for k in spec.get("shared_palette_skip", ())}
    if spec.get("shared_palette"):
        shared = np.unique(np.concatenate([palette_of(a) for t, fr in frames.items() for i, (a, _) in enumerate(fr)
                                           if (t, i) not in skip]), axis=0)
    for tag, fr in frames.items():
        if only and tag not in only:
            continue
        res = []
        for i, (a, ms) in enumerate(fr):
            content, pivot, note = restyle_frame(hero, tag, i, a, spec, ppu, tpl, neck_off, outline, reach, ring_tpl)
            e = spec.get("edge", 0)
            if co and tag.startswith(co["prefix"]):
                c0, p0 = pixelate(content, new_ppu / ppu, pivot, outline, pal=shared)
                was[(tag, i)] = (grow_edge(c0, e, outline), (p0[0] + e, p0[1] + e))
                content, pivot = pixelate(content, co["grid"] * co["size"] / ppu, pivot, outline, pal=shared)
                content = grow_edge(content, e, outline)
                pivot = (pivot[0] + e, pivot[1] + e + FEET * co["grid"] * (co["size"] - 1))
                res.append((content, pivot, ms))
                notes.append(f"{tag}[{i}] {note} coarse")
                continue
            pivot0 = pivot
            if new_ppu != ppu:
                content, pivot = pixelate(content, new_ppu / ppu, pivot, outline,
                                          pal=None if (tag, i) in skip else shared)
            before = content
            content = grow_edge(content, spec.get("edge", 0), outline)
            if spec.get("slits"):                          # narrow slits between parts kept open
                content = open_slits(content, before, spec.get("edge", 0), int(spec["slits"]))
            if spec.get("pinholes"):                       # the specks of ground the grown outline closed in
                most = 2 if spec["pinholes"] is True else int(spec["pinholes"])
                content = close_pinholes(content, spec.get("edge", 0), outline, most,
                                         before if spec.get("reopen") else None)
            if spec.get("cracks"):                         # the one-square slits left in the outline
                content = close_cracks(content, outline)
            if spec.get("fill_holes"):                    # specks of ground the coarser grid closed in
                content = fill_holes(content, int(spec["fill_holes"]))
            if spec.get("look"):                          # coarser to the eye, on the frame's own grid
                kept = None
                if spec.get("look_keep"):
                    import importlib
                    kept = importlib.import_module(spec["look_keep"]).keep(tag, i, content)
                content = coarse_look(content, pivot, spec["look"] / new_ppu, outline, int(spec.get("look_holes", 0)),
                                      kept)
            if spec.get("fx") and not spec.get("fix"):
                if i == 0:
                    fx = read_fx(hero, tag)
                over, under = fx[0][i], fx[1][i]
                if new_ppu != ppu:
                    # on the frame's own new grid (the same size, pivot and k as its pixelate), without its outline
                    over, under = (None if f_ is None else scale_fx(f_, new_ppu / ppu, pivot0, mote=4)[0] for f_ in (over, under))
                content = put_fx(content, e, over, under)
            pivot = (pivot[0] + e, pivot[1] + e + spec.get("lift_sq", 0))   # lift_sq: whole rows of the new grid
            res.append((content, pivot, ms))
            notes.append(f"{tag}[{i}] {note}")
        out[tag] = res
    if spec.get("grow", 1) != 1 and new_ppu == ppu and "idle" in out and not spec.get("lift"):
        # the even-grid growth rounds: put the soles back exactly where the idle's first frame had them
        a0 = frames["idle"][0][0]
        sole0 = np.nonzero(a0[..., 3].any(1))[0].max() + 1 - a0.shape[0] / 2
        c0, pv0, _ = out["idle"][0]
        now = np.nonzero(c0[..., 3].any(1))[0].max() + 1 - pv0[1]
        d = round(now + spec.get("lift_sq", 0) - sole0)   # a lift_sq asked for stays (league_gangplank's 90 %)
        if d:
            out = {t: [(c, (pv[0], pv[1] + d), m) for c, pv, m in r] for t, r in out.items()}
            notes.append(f"soles moved {-d} rows back onto the ground")
    if spec.get("crisp") is not None:
        # flat pixel art (pixel_down.crisp): one palette over every frame of the hero
        keys = [(t, i) for t, r in out.items() for i in range(len(r))]
        fit = None
        # palette_fit: tag -> a strip under assets/source (+ .json sizes) whose frames, restyled as that tag's, the
        # palette is fit on instead of the tag's own (a redrawn tag leaves every other frame's colours as they were)
        ref = {}
        for t, stem in spec.get("palette_fit", {}).items():
            base = os.path.join(ROOT, "assets", "source", *stem.split("/"))
            with open(base + ".json", encoding="utf-8") as f:
                sizes = json.load(f)["sizes"]
            strip = np.asarray(Image.open(base + ".png").convert("RGBA"))
            ref[t], x = [], 0
            for k, (W, H) in enumerate(sizes):
                c = restyle_frame(hero, t, k, strip[:H, x:x + W].copy(), spec, ppu, tpl, neck_off, outline, reach,
                                  ring_tpl)[0:2]
                x += W + 1
                if new_ppu != ppu:
                    c = pixelate(c[0], new_ppu / ppu, c[1], outline, pal=shared)
                ref[t].append(grow_edge(c[0], spec.get("edge", 0), outline))
        if unnarrowed or was or ref:
            fit = []
            for t, i in keys:
                if t in ref:
                    if i == 0:
                        fit.extend(ref[t])
                elif (t, i) in was:
                    fit.append(was[(t, i)][0])
                elif (t, i) in unnarrowed:
                    c = restyle_frame(hero, t, i, unnarrowed[(t, i)], spec, ppu, tpl, neck_off, outline, reach,
                                      ring_tpl)[0:2]
                    if new_ppu != ppu:
                        c = pixelate(c[0], new_ppu / ppu, c[1], outline, pal=shared)
                    fit.append(grow_edge(c[0], spec.get("edge", 0), outline))
                else:
                    fit.append(out[t][i][0])
        flat = D.crisp([out[t][i][0] for t, i in keys], fit=fit, **spec["crisp"])
        for (t, i), f in zip(keys, flat):
            c, pv, m = out[t][i]
            out[t][i] = (f, pv, m)
        notes.append(f"crisp {spec['crisp']}")
    sole = lambda a: np.nonzero(a[..., 3].any(1))[0].max() + 1
    for (t, i), (c0, p0) in was.items():
        k = new_ppu / co["grid"]
        c, pv, m = out[t][i]
        c = scale_even(c, k)
        out[t][i] = (c, (pv[0] * k, sole(c) - (sole(c0) - p0[1])), m)
    return out, sheet, ppu, new_ppu, notes, outline


# tags whose hd frames must be exactly PPU x as wide as their 1x frames: the DLL changes a table only when its hd_idle
# is (src/lookup.rs), and hero_reels.py's idle (the table the DLL reads) begins on idle_base's frame - league_varus's
# idle_base came out 43 -> 66 (64.5 +- 0.5 wanted): his encyclopedia card blank, the battlefield on 1x frames
EXACT = ("idle", "idle_base")


def framed(hero, out, sheet, new_ppu):
    """The restyled frames on their frames (the 1x idle padded where the idle needs more width). -> ({tag: frames},
    pad columns)."""
    k = new_ppu
    pad = 0
    while True:
        ok, res = True, {}
        for tag, fr in out.items():
            ones = sheet[tag]
            frames = []
            for (content, pivot, ms), (one, _) in zip(fr, ones):
                exact = tag in EXACT                # hero_reels' idle reel starts on idle_base's frame
                w1 = one.shape[1] + (2 * pad if exact else 0)
                W, H = P.hd_size(w1, one.shape[0], k)
                f = fit(content, pivot, W, H, exact_w=W if exact else None)
                if f is None:
                    ok = False
                    break
                frames.append((f, ms))
            if not ok:
                break
            res[tag] = frames
        if ok:
            return res, pad
        pad += 1


def moved_face(hero, spec, frames, ppu):
    """The champion_view face point (1x pixels from the pivot) where the idle's first frame's warp and growth send it
    (None when nothing moves)."""
    path = os.path.join(P.mod_dir(hero), "style", "champion_view.champion_view")
    cv = json.loads(open(path, "rb").read().decode("utf-8-sig"))
    entry = cv["entries"].get(P.hero_id(hero))
    if not entry or "face" not in entry:
        return None
    keep = os.path.join(ORIG, f"{hero}_face.json")        # the face point before any restyle (reruns start there)
    if not os.path.isfile(keep):
        with open(keep, "w", encoding="utf-8", newline=chr(10)) as f:
            json.dump(entry["face"], f)
    with open(keep, encoding="utf-8") as f:
        base = json.load(f)
    fx, fy = base["x"], base["y"]
    if spec.get("face_to"):
        new = {"x": spec["face_to"][0], "y": spec["face_to"][1]}
        return None if new == entry["face"] else (path, cv, entry, new)
    a = frames["idle"][0][0]
    px, py = a.shape[1] / 2, a.shape[0] / 2
    x, y = px + fx * ppu, py + fy * ppu
    warp = WARPS.get((hero, "idle", 0))
    if warp is not None:
        x, y = (float(v) for v in warp.forward(np.array(x), np.array(y)))
    rx, ry = (x - px) / ppu, (y - py) / ppu
    k = spec.get("grow", 1)
    rx, ry = rx * k, FEET + (ry - FEET) * k
    new = {"x": int(round(rx)), "y": int(round(ry))}
    return None if new == entry["face"] else (path, cv, entry, new)


def write_face(hero, moved):
    if not moved:
        return
    path, cv, entry, new = moved
    print(f"{hero}: champion_view face {entry['face']} -> {new}")
    entry["face"] = new
    text = json.dumps(cv, ensure_ascii=False, indent=2).replace(chr(10), chr(13) + chr(10)) + chr(13) + chr(10)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def write_hero(hero, res, sheet, pad, new_ppu):
    for tag, frames in res.items():
        H = max(f.shape[0] for f, _ in frames)
        strip = np.zeros((H, sum(f.shape[1] + 1 for f, _ in frames) - 1, 4), np.uint8)
        x = 0
        for f, _ in frames:
            strip[:f.shape[0], x:x + f.shape[1]] = f
            x += f.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(SRC, f"{hero}_{tag}.png"))
        with open(os.path.join(SRC, f"{hero}_{tag}.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sizes": [[f.shape[1], f.shape[0]] for f, _ in frames]}, fh)
    if pad:
        plain = {t: v for t, v in sheet.items() if P.plain(t)}
        for t in EXACT:
            if t in plain:
                plain[t] = [(np.pad(a, ((0, 0), (pad, pad), (0, 0))), ms) for a, ms in plain[t]]
        G.write_sheet(P.stem_of(hero), plain)


# ----------------------------------------------------------------------------------------------- previews
def crop(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def shown(a, k):
    im = Image.fromarray(crop(a))
    size = (max(1, round(im.width * k)), max(1, round(im.height * k)))
    return im.resize(size, Image.NEAREST if k >= 1 else Image.BOX)


def preview(hero, res, ppu_old, new_ppu, path, Z=3):
    """Every frame before / after at game size x Z, tag by tag."""
    size = sizes_of().get(hero, 1.0)
    frames, _, _ = read_orig(hero)
    rows = []
    for tag, fr in res.items():
        before = [shown(a, Z * size / ppu_old) for a, _ in frames[tag]]
        after = [shown(f, Z * size / new_ppu) for f, _ in fr]
        cw = max(im.width for im in before + after) + 6
        ch = max(im.height for im in before + after)
        im = Image.new("RGB", (110 + cw * len(after), 2 * ch + 30), (88, 104, 88))
        d = ImageDraw.Draw(im)
        d.text((2, 4), tag, fill=(255, 255, 255))
        d.text((2, ch // 2 + 10), "now", fill=(200, 200, 200))
        d.text((2, ch + ch // 2 + 20), "new", fill=(255, 255, 0))
        for i, (b, n) in enumerate(zip(before, after)):
            x = 110 + i * cw
            im.paste(b, (x, 6 + ch - b.height), b)
            im.paste(n, (x, 24 + 2 * ch - n.height), n)
        rows.append(im)
    W = max(r.width for r in rows)
    can = Image.new("RGB", (W, sum(r.height for r in rows)), (60, 70, 60))
    y = 0
    for r in rows:
        can.paste(r, (0, y))
        y += r.height
    can.save(path)
    return can.size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", required=True)
    ap.add_argument("--preview", help="write <hero>_restyle.png here, change nothing")
    ap.add_argument("--only", help="tags (comma separated) for a quick preview")
    ap.add_argument("--set", nargs="*", default=[], help="key=value over RESTYLE[hero] (numbers)")
    a = ap.parse_args()
    for hero in a.hero:
        spec = dict(RESTYLE[hero])
        for kv in a.set:
            k, v = kv.split("=", 1)
            spec[k] = float(v)
        out, sheet, ppu, new_ppu, notes, outline = restyle(hero, spec, only=a.only.split(",") if a.only else None)
        res, pad = framed(hero, out, sheet, new_ppu)
        bad = [n for n in notes if "no head" in n]
        print(f"{hero}: PPU {ppu} -> {new_ppu}, outline {outline}, 1x idle padded {pad}; frames without a head: "
              f"{', '.join(bad) or 'none'}")
        if a.preview:
            os.makedirs(a.preview, exist_ok=True)
            print(preview(hero, res, ppu, new_ppu, os.path.join(a.preview, f"{hero}_restyle.png")))
            continue
        write_hero(hero, res, sheet, pad, new_ppu)
        frames, _, _ = read_orig(hero)
        write_face(hero, moved_face(hero, spec, frames, ppu))
        print(f"{hero}: strips written; set PPU {hero} {new_ppu} in ppu_hd.py / hd.rs if it changed, then "
              f"python tools/art/ppu_hd.py --hero {hero}")


if __name__ == "__main__":
    main()
