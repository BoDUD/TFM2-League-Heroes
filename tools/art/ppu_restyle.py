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
            "tahmkench": 1.2, "kalista": 1.4, "drmundo": 1.5, "pantheon": 1.5, "orianna": 2.2, "aphelios": 1.5, "rell": 1.5, "urgot": 1.2, "reksai": 1.58, "swain": 1.5, "nasus": 1.2, "renata": 1.5, "anivia": 1.2, "jarvaniv": 1.5, "ziggs": 1.5, "maokai": 1.5,
            **{h: 1.5 for h in ('morgana', 'nami', 'janna', 'jax', 'xinzhao')}, "yunara": 1.5}
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
    # 「铁男的走路步伐感觉有点大啊」: the run's two striding frames had the soles 42 and 47.5 game px apart (the idle's 31):
    # their legs brought together from the hips down (narrow: 25 and 40 orig px nearer on each side at the soles)
    "mordekaiser": dict(body_only=True, head=1.0, wide=1.25, short=0.94, edge=0, ppu=2.0, lift=3 * 5 / 2.0, lift_sq=-1,
                        stride={"run": (165, {0: 25, 2: 40})},
                        crisp=dict(contrast=1.0, keep="teal"),
                        face_to=(1, -30)),
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
    "malzahar": dict(ppu=1.38, edge=1, lift=2, face_to=(4, -39)),
    # league_milio (#105): Codex's drafts read on their own grid and brought to the user's 2.2 squares a game pixel by
    # tools/art/rig_milio.py (the boy 32 game rows from his hair top to his soles; one head brought down once for every
    # frame), so no proportion or density change here; the outer outline grown a square like the others; the face
    # point at his crown (rig_milio.face_point)
    "milio": dict(ppu=2.2, edge=1, face_to=(0, -30)),
    # league_jayce (#106): Codex's strips (both forms) on the design's grid brought to the user's 1.5 squares a game pixel
    # by tools/art/rig_jayce.py (38 game rows crown to soles; one head brought down once for every frame), so no
    # proportion or density change here; the outer outline grown a square like the others; the face point at his crown
    "jayce": dict(ppu=1.5, edge=1, face_to=(0, -38)),
    # league_elise (#107): Codex's strips warped to the design's proportions and brought to the user's 1.8 squares a game
    # pixel by tools/art/import_elise_strips.py + rig_elise.py (38 game rows crown to toes), so only the outer outline
    # grown a square like the others; the face point at her crown
    "elise": dict(ppu=1.8, edge=1, face_to=(0, -37)),
    # league_katarina (#108): Codex's strips brought to the user's PPU by tools/art/rig_katarina.py (38 game rows crown
    # to soles; 1.5, then the design's own 1.7895 for the face, then back to 1.5: 「卡特琳娜太高清了 降低点像素」), so no
    # proportion or density change here; the outer outline grown a square like the others; the face point at her crown
    "katarina": dict(ppu=1.5, edge=1, face_to=(0, -37)),
    # league_tahmkench (#110): posed from the approved design's own squares and brought to the user's 1.2 squares a game
    # pixel by tools/art/rig_tahmkench.py (42 game rows hat to soles), so only the outer outline grown a square like the
    # others; the face point on his head's top under the hat
    "tahmkench": dict(ppu=1.2, edge=1, face_to=(1, -36)),
    # league_kalista (#109): Codex's strips (heads, sizes, run and death finished by tools/art/import_kalista_strips.py)
    # brought to the user's PPU 1.4 at 85 % by tools/art/rig_kalista.py (「大小 85%，PPU 1.4」), so no proportion or
    # density change here; the outer outline grown a square like the others; the face point at her helm
    "kalista": dict(ppu=1.4, edge=1, face_to=(0, -39)),
    # league_drmundo (#111): Codex's strips (sizes, places, the run and the death finished by
    # tools/art/import_drmundo_strips.py) brought to the user's PPU 1.5 by tools/art/rig_drmundo.py (「选 A，42 行，PPU
    # 1.5」), so no proportion or density change here; the outer outline grown a square like the others; the face point
    # by tfm2_ase.py face (his crown, a little ahead of the head centre)
    "drmundo": dict(ppu=1.5, edge=1, face_to=(-1, -38)),
    # league_pantheon (#112): Codex's strips drawn on the design's own grid at the user's 1.5 squares a game pixel
    # (「选A 40尺寸 PPU1.5」), ordered and moved by whole squares by tools/art/rig_pantheon.py, so no proportion or density
    # change here; the outer outline grown a square like the others; the face point at his helmet's crown
    "pantheon": dict(ppu=1.5, edge=1, face_to=(-3, -36)),
    # league_orianna (#113): posed from the approved design's own squares at the user's 2.2 squares a game pixel by
    # tools/art/rig_orianna.py (「PPU 2.2（84 行）」, 38 game rows bun to soles), so no proportion or density change
    # here; the outer outline grown a square like the others; the face point at her crown (tfm2_ase.py face)
    "orianna": dict(ppu=2.2, edge=1, face_to=(-4, -37)),
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
    # frames (orig/urgot_<tag>.over.png) laid on after the outline (fx); the face point at his bald crown
    "urgot": dict(ppu=1.2, edge=1, face_to=(3, -24), fx=True),
    # league_reksai (#117): posed by tools/art/rig_reksai.py from Codex's step-1 takes read back square for square (A 57
    # rows = the user's 36 game px: posed at 57 / 36 = 1.58), then pixelated to 1.2 (the user, 2026-10-17: 「雷克赛像素太高
    # 需要降低」, picked 1.2 from 1.58 / 1.4 / 1.3 / 1.2 / 1.0 - tools/art/review_reksai_ppu.py); no proportion change; the
    # outer outline grown a square like the others; the face point between her helmet and her mouth (she has no eyes;
    # the crown is the crest)
    "reksai": dict(ppu=1.2, edge=1, face_to=(15, -20)),
    # league_swain (#118): posed by tools/art/rig_swain.py from Codex's step-1 take A-1 cut to 60 rows (the user's 40 game
    # rows at 1.5), the demon form on the same body; no proportion or density change here; the outer outline grown a
    # square like the others; the face point at his crown (tfm2_ase.py face: 39 px over the soles)
    "swain": dict(ppu=1.5, edge=1, face_to=(-1, -39)),
    # league_renata (#120): posed by tools/art/rig_renata.py from Codex's step-1 take 1 cut to 60 rows, then to 54 (36 game
    # rows at 1.5, the user's 「模型太大」; the R machine in her own ult frames); no proportion or density change here; the
    # outer outline grown a square like the others; the pistol's muzzle flash (Codex's a_flash, rig_renata.py,
    # orig/renata_attack.over.png) laid on after the outline (fx); the face point at her crown (tfm2_ase.py face: 36 px
    # over the soles)
    "renata": dict(ppu=1.5, edge=1, face_to=(1, -36), fx=True),
    # league_nasus (#121): posed by tools/art/rig_nasus.py from Codex's step-1 takes A-1 / B-1 cut to 53 / 71 rows (the
    # user's 44 / 59 game rows at 1.2), the big body (Fury of the Sands) its own design; no proportion or density change
    # here; the outer outline grown a square like the others; the face point on his glowing eye
    "nasus": dict(ppu=1.2, edge=1, face_to=(7, -36)),
    # league_anivia (#123): posed by tools/art/rig_anivia.py from Codex's step-1 takes A-2 / B-1 cut to 46 / 23 rows (the
    # user's 38 game rows at 1.2, 「模型有点大」 from 44; in game 「凤凰的局内模型太大」 -> 31 rows, 37 / 19 cut); the wings
    # rigid (as drawn or mirrored); no proportion or density change here; the outer outline grown a square like the
    # others; the face point on her violet brow gem's row, between it and her magenta eye
    "anivia": dict(ppu=1.2, edge=1, face_to=(2, -20)),
    # the 2026-10-16 redo from Codex's pictures, posed by tools/art/rig_<hero>_hd.py (tools/art/ppu_rig.py) at PPU 1.5 -
    # Nami after League's own clips (tools/lol/league_joints.py): only the outer outline grown a square, the face point
    # at the new head
    "morgana": dict(ppu=1.5, edge=1, face_to=(1, -34)),     # #310: framed on her face (was chin to chest)
    "nami": dict(ppu=1.5, edge=1, face_to=(1, -43)),        # #310
    "janna": dict(ppu=1.5, edge=1, face_to=(1, -27)),       # #309: her eyes no longer on the frame's top edge
    # Jax: the forehead of his mask, right in the hood (he looks front-right; his eyes 26 px over the soles, the hood's
    # top 32)
    "jax": dict(ppu=1.5, edge=1, face_to=(6, -29)),
    # Xin Zhao (2026-10-18): Codex's chibi picture cut to 63 rows, posed after League's own clips by
    # tools/art/rig_xinzhao_hd.py (his run League's Runbase on drawn legs, the design's boots); the W slash and the R tell
    # baked into his frames (orig/xinzhao_<tag>.over.png) laid on after the outline (fx); the face point at the top of his
    # hair, under the topknot (tfm2_ase.py face: the head 3.9 px ahead of the pivot)
    "xinzhao": dict(ppu=1.5, edge=1, face_to=(5, -36), fx=True),
    # league_yunara (#119): posed from the design's own squares at the user's 1.5 squares a game pixel (「选 A，40 行」,
    # Codex's step-1 take 2 cut to 60 rows, her beads apart) by tools/art/rig_yunara.py, so no proportion or density
    # change here; the outer outline grown a square like the others; the face point at her ornaments' crown
    # (tfm2_ase.py face)
    "yunara": dict(ppu=1.5, edge=1, face_to=(1, -39)),
    # league_jarvaniv (#122): posed from the design's own squares at the user's 1.5 squares a game pixel (「身体 40」,
    # Codex's step-1 take A-2 cut to 60 rows) by tools/art/rig_jarvaniv.py, so no proportion or density change here;
    # the outer outline grown a square like the others; the face point between his eyes under the helmet's brim
    "jarvaniv": dict(ppu=1.5, edge=1, face_to=(1, -32)),
    # league_ziggs (#124): posed from the design's own squares at 1.5 squares a game pixel (「游戏里 32 像素高」, Codex's
    # step-1 take A-1 cut to 48 rows) by tools/art/rig_ziggs.py, then brought to 1.2 here (the user, 2026-10-18, on the
    # showcase: 「太高清了 降低点像素」 - shown 1.5 / 1.3 / 1.2 / 1.0 by tools/art/review_ziggs_ppu.py: 「降到 PPU 1.2」); the
    # outer outline grown a square like the others; the face point between his goggles
    "ziggs": dict(ppu=1.2, edge=1, face_to=(2, -26)),
    # league_maokai (#125): posed from the design's own squares at 1.5 squares a game pixel (the user picked 40 game rows
    # at 1.2, then 「太模糊了 PPU调整一下像素」: Codex's step-1 take A-2 cut to 60 rows) by tools/art/rig_maokai.py, then
    # brought to 1.3 here (the user, 2026-10-18, on the PR: 「太高清了 降低点像素」 - shown 1.5 / 1.4 / 1.3 / 1.2 by
    # tools/art/review_maokai_ppu.py: 「1.3吧」); the outer outline grown a square like the others; the face point between
    # the eyes of the face in his trunk
    "maokai": dict(ppu=1.3, edge=1, face_to=(8, -23)),
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
    sheet = P.read_sheet(os.path.join(MOD, "champions", f"league_{hero}"))
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
    shared = None
    if spec.get("shared_palette"):
        shared = np.unique(np.concatenate([palette_of(a) for fr in frames.values() for a, _ in fr]), axis=0)
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
                content, pivot = pixelate(content, new_ppu / ppu, pivot, outline, pal=shared)
            content = grow_edge(content, spec.get("edge", 0), outline)
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
        was = np.nonzero(a0[..., 3].any(1))[0].max() + 1 - a0.shape[0] / 2
        c0, pv0, _ = out["idle"][0]
        now = np.nonzero(c0[..., 3].any(1))[0].max() + 1 - pv0[1]
        d = round(now - was)
        if d:
            out = {t: [(c, (pv[0], pv[1] + d), m) for c, pv, m in r] for t, r in out.items()}
            notes.append(f"soles moved {-d} rows back onto the ground")
    if spec.get("crisp") is not None:
        # flat pixel art (pixel_down.crisp): one palette over every frame of the hero
        keys = [(t, i) for t, r in out.items() for i in range(len(r))]
        fit = None
        if unnarrowed or was:
            fit = []
            for t, i in keys:
                if (t, i) in was:
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
                w1 = one.shape[1] + (2 * pad if tag == "idle" else 0)
                W, H = P.hd_size(w1, one.shape[0], k)
                f = fit(content, pivot, W, H, exact_w=W if tag == "idle" else None)
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
    path = os.path.join(MOD, "style", "champion_view.champion_view")
    cv = json.loads(open(path, "rb").read().decode("utf-8-sig"))
    entry = cv["entries"].get(f"league_{hero}")
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
        plain["idle"] = [(np.pad(a, ((0, 0), (pad, pad), (0, 0))), ms) for a, ms in plain["idle"]]
        G.write_sheet(os.path.join(MOD, "champions", f"league_{hero}"), plain)


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
