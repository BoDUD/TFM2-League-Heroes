#!/usr/bin/env python3
"""Import a native-size redraw (assets/source/NATIVE_REDRAW.md) as the hero's game sprite.

    python tools/art/import_native.py [--hero lux --hero ashe] [--review DIR]

Source, assets/source/native/: <hero>_<tag>.png from the GPT/Codex run - every game pixel one exact
8x8 block, the frames in 56x64-pixel cells (or the size the cells table gives) read left to right,
top to bottom (native_refs.layout) - and <hero>_cells.json, written with the references by
native_refs.py (from round-1 game frames) or tools/lol/native_pose.py (straight from League's
clips): where each reference frame's pivot stood in its cell, and its duration. The redraw was drawn over those references, so each new
frame is cut out of its cell around that pivot and stands where the round-1 frame stood (head
tracks, lunges, the R wand inside the beam, the death knock-back), for the same time. The blocks are
read one pixel each: no resampling, no new palette, no added outline.
Two fixes for the loops, where every pixel of jitter shows:
  - idle and run: each frame moves sideways so its head sits at the strip's mean head column. The
    head is idle frame 1's top rows, found by exact match (Codex pasted one verified head into every
    frame); frames placed by their bounding box had it 1-2 px off.
  - ORDER: Lux's idle arrived breathing down, down, down, up, down, up; its frames 5 and 6 swap.
    Master Yi's raised sword is the top of every frame, so he is steadied on League's head joint, where
    his helmet was pasted (PASTED), and his one-frame idle on the frame it shows. Codex's Fiddlesticks
    (design B) holds his scythe over his head and redrew the head in every run frame: he is steadied on
    his eyes, the one colour nothing else uses (EYES; his run's eyes wandered 12 px about the pivot).
Then <hero>_retouch.json, when there is one, retouches single pixels of the cut frames (Lee Sin's mouth,
nose and face side; Lux's run, where her wand's gold end read as a gold foot): x, y from the pivot, the colour expected there and the new one. A pixel that no longer has
the expected colour stops the import, so edits made for one version of the strips never land on another.
Writes league/champions/league_<hero>. The effects still come from tools/art/import_<hero>.py, which
writes the round-1 body only with --body.
--review DIR writes <hero>_native.png: every frame at 4x around its pivot (pivot column, feet line).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import CELL, Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
HEAD_ROWS = 12                  # idle frame 1's top rows: the head
SURE = 0.9                      # share of the head's pixels that must match exactly
STEADY = ("idle", "run")
# hero: rows every frame moves down, but never past the soles row (SOLES under the pivot): a hero drawn floating
# who should stand on the ground. Nami floated 3 px like Janna, so in the collection grid (every hero's feet on one
# line) she sat high; the user: "整体下移 3 格、去掉浮空". Frames already on the ground stay (R's landing, her death).
SINK = {"nami": 3}
SOLES = 11
# (hero, tag): (y, slots) like BOB, for a neck drawn too long under the pasted head: in those slots everything at or
# above pivot row y moves down a row. Codex drew Nami's swimming body a row lower under the head in run 1-4 than
# in 5-8 and the design, so her neck stretched and shrank as she swam (the user: "一上一下的时候感觉身体要分离一样").
NECK = {("nami", "run"): (-21, [0, 1, 2, 3])}
# (hero, tag): (y, rows, cape), a walk's step: in frame k everything at or above pivot row y moves down rows[k] and is
# laid over what is below, so the leg tops tuck under the hips; a cape that streams behind her across row y goes along
# whole (below y: each row up to one past its last `cape` colour pixel, and the tip's runs hanging off that), or the
# seam folds it into a step. Codex redrew Fiora's walk with the head, neck and shoulders as one block (her pasted head
# had drifted a row off the body: "头和身体不协调"), but the block stood still over the striding legs. League's walk
# dips the whole upper body at the landing (frame 4, both feet wide) and carries it highest at 5-6: League's head and
# body centre move about 2 px at her size, its hip 3 (one 3-px snap from 4 to 5 read bouncy on a 40-px chibi). The
# drawing already stands a row higher in 6-8.
STEP = {("fiora", "run"): (-6, [1, 1, 0, 2, 0, 1, 2, 2], ["5C0522", "730928"])}
# (hero, tag): per frame (rows, left, right[, "fill"]) or None, the pasted head put back on its neck: the design's
# head moves up `rows` (the idle's head pixels round the eyes, down to the chin three rows under them) and the idle's
# rows under its chin - the neck and the collar - go under it, `left`..`right` columns from the eyes, where the frame
# is clear or had the head; "fill" also closes a clear gap under the chin with the idle's neck. Fiora's strips prompt
# said "no neck under the chin", so Codex seated the head on the shirt in every action frame: eyes 4-5 rows above the
# white shirt against the idle's 8, her short neck and tall gold collar gone (the user: "剑姬放技能的时候脖子又消失
# 没修复吗？", "还是漏了"). Rows and widths per frame from a judge per strip: the wide collar (7) where the shoulders
# are square to us, 5 where it would sit on a shoulder, cut on the side of a raised sword arm; the Q dash (2-3) stays
# (League shows no neck there), as do the death frames whose head hangs ahead of the body (2-4).
NECK_UP = {("fiora", "attack"): [(2, 7, 7), (1, 5, 4), (1, 5, 5, "fill"), (3, 7, 3), (3, 7, 3), None],
           ("fiora", "attack_e"): [(3, 7, 7), (2, 7, 7), (3, 7, 7), (3, 7, 7), (3, 7, 7), (3, 7, 7)],
           ("fiora", "skill"): [(3, 5, 5), None, None, (4, 5, 5), (4, 5, 5), (4, 5, 5)],
           ("fiora", "skill2"): [(3, 5, 5)] * 6 + [(4, 5, 5)],
           ("fiora", "ult"): [(4, 7, 7)] * 5,
           ("fiora", "hit"): [(2, 7, 7), (2, 7, 7)],
           ("fiora", "dead"): [(3, 7, 7), None, None, None, (4, 7, 7), (4, 7, 7), None, None]}
# (hero, tag, frame): the eyes (pivot row, column) where the EYES colour is missing - her wince, eyes shut
NECK_EYES = {("fiora", "hit", 0): (-19, 3)}
# heroes whose outline strips.complete_outline closes on the finished frames (the skill's art-spec "Close the
# outline": every hero from Nami on; the user: "后面英雄都要用的"; and the older ones whose outline CLEAN tidies, which
# needs it closed). Nothing goes under the soles row; a frame that already reaches lower (lying down) keeps its own
# bottom.
COMPLETE = {"nami", "veigar", "jax", "ahri", "taric", "tristana", "fiora", "diana", "leesin", "missfortune", "fizz", "shaco",
            "caitlyn", "nocturne", "blitzcrank", "kaisa"}
# hero: the luminance from which an edge pixel gets the outline (complete_outline's `dark`, default 70). Fiora's teal
# leggings (luminance ~58) and wine cape (~44) edge many action frames without black: tfm2_ase.py metrics counts only
# luminance < 40 as outline, so at 70 her Q frames read 83-89% (the bare rapier aside); at 40 they close too.
DARK = {"fiora": 40}
# heroes whose closed outline strips.clean_outline then tidies (one black ring, one pixel thick, no crumbs; the face
# box round the EYES colour untouched). Fiora's Codex frames mixed black with her darkest teal, wine and brown on
# the ring, doubled it inside and left loose black crumbs on the legs (the user: "黑色描边处理一下 弄干净点").
# Miss Fortune, Lee Sin, Ahri and Jax the same (2026-10-01: "顺便帮我清理一下厄运小姐的黑边部分 干净一点", "盲僧也要清理",
# "阿狸也清理一下", "贾克斯也清理一下"): their action frames' ring was a second near-black beside the idle's, with their
# materials' darkest shades on it (her dark red, teal and brown and gold left open; his navy, dark red and hair; her
# wine and navy; Jax's three near-blacks, his hood's and cape's darkest magenta and violet), doubled corners and crumbs.
CLEAN = {"fiora", "leesin", "missfortune", "ahri", "jax"}
# CLEAN heroes tidied by clean_outline's strict rules: a review of every frame found Fiora's rules cut their boot soles
# to points, peeled Lee Sin's black braid, blackened muzzles, hair tips and wrist stripes in place and broke interior
# lines drawn in their second near-black; strict only unifies the ring's near-blacks, never blackens a colour, and
# clears a corner only where it doubles a staircase (strips.clean_outline)
STRICT = {"leesin", "missfortune", "ahri", "jax"}
# hero: colours of a blade drawn as a bare one-pixel line; clean_outline clears the black caps complete_outline puts
# on the ends of every run of a slanted one (Fiora's rapier in Q, the crit and the salute read as a dashed line),
# and strips.straighten_lines redraws each long one as a straight pixel line from the hilt to the tip (Codex's
# slanted runs of 3, 2, 3, 2, 4 read as bent: "这两个剑也应该是直线的吧", the user)
BARE = {"fiora": [(0xE6, 0xE8, 0xF0)]}
ORDER = {("lux", "idle"): [0, 0, 0, 0, 0, 0],   # the step-2 idle is the design in all six (was 0 1 2 3 5 4)
         # League leans his upper body a square forward in idle 4-5 and back in 6, and every frame's head
         # is voted anew, so the face swung and changed shape as he breathed (the user). Frame 1 in every
         # slot, breathing through BOB instead.
         ("yasuo", "idle"): [0, 0, 0, 0, 0, 0],
         # the same one drawing for Leona (her face is pasted, and League's idle barely moves)
         ("leona", "idle"): [0, 0, 0, 0, 0, 0],
         # and for Teemo: his pasted head rode League's breath a row up and down while the body under it was
         # voted anew each frame (100-480 pixels changed between idle frames)
         ("teemo", "idle"): [0, 0, 0, 0, 0, 0],
         # and for Master Yi: one pasted helmet, and a body voted anew each frame would shimmer
         ("masteryi", "idle"): [0, 0, 0, 0, 0, 0],
         # and Annie, whose drawn head is pasted too
         ("annie", "idle"): [0, 0, 0, 0, 0, 0],
         # and Miss Fortune (a drawn head under a pasted tricorne)
         ("missfortune", "idle"): [0, 0, 0, 0, 0, 0],
         # and Janna (pasted head, a body restyled from League's idle)
         ("janna", "idle"): [0, 0, 0, 0, 0, 0],
         # and Malphite, whose drawn head sits on his shoulders (restyle "anchor")
         ("malphite", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ekko (a drawn head pasted on League's crouch)
         ("ekko", "idle"): [0, 0, 0, 0, 0, 0],
         # and Yone (a drawn masked head, a body restyled from League's idle)
         ("yone", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ezreal (a drawn head with goggles, a body restyled from League's idle)
         ("ezreal", "idle"): [0, 0, 0, 0, 0, 0],
         # and Thresh (a drawn skull pasted on a body restyled from League's idle)
         ("thresh", "idle"): [0, 0, 0, 0, 0, 0],
         # and Kayle (a drawn head pasted on League's hovering idle)
         ("kayle", "idle"): [0, 0, 0, 0, 0, 0],
         # and Fiddlesticks (Codex's redraw, design B: the six idle frames are one drawing)
         ("fiddlesticks", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ahri (a drawn head with fox ears pasted on a body restyled from League's idle)
         ("ahri", "idle"): [0, 0, 0, 0, 0, 0],
         # and Amumu (his step-2 idle is the design in all six)
         ("amumu", "idle"): [0, 0, 0, 0, 0, 0],
         # and Jinx (eight idle frames, all the design)
         ("jinx", "idle"): [0, 0, 0, 0, 0, 0, 0, 0],
         # and Garen (moved into this pipeline by the step-2 redraw; the idle is the design in all six)
         ("garen", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ashe (her step-2 idle is the design in all six)
         ("ashe", "idle"): [0, 0, 0, 0, 0, 0],
         # and Lucian (his redesign: Codex's strips with the design's head copied into every frame)
         ("lucian", "idle"): [0, 0, 0, 0, 0, 0],
         # and Morgana (the redesign A, which tools/art/tidy_morgana.py writes into all six)
         ("morgana", "idle"): [0, 0, 0, 0, 0, 0],
         # and Riven (the idle strip is the approved design on every pivot)
         ("riven", "idle"): [0, 0, 0, 0, 0, 0],
         # and Briar (the design B: Codex's strips with the design's head copied into every frame)
         ("briar", "idle"): [0, 0, 0, 0, 0, 0],
         # and Vayne (the design drawn by Codex at game size: the pack's idle is the design in all six)
         ("vayne", "idle"): [0, 0, 0, 0, 0, 0],
         # and Akali (the redo: the pack's idle is the design A40 in all six)
         ("akali", "idle"): [0, 0, 0, 0, 0, 0],
         ("nami", "idle"): [0, 0, 0, 0, 0, 0],
         ("diana", "idle"): [0, 0, 0, 0, 0, 0],
         # and Veigar (Codex's part rig on the approved design: the idle is the design in all six)
         ("veigar", "idle"): [0, 0, 0, 0, 0, 0],
         # and Jax (Codex's game-size design A41: the pack's idle is the design in all six)
         ("jax", "idle"): [0, 0, 0, 0, 0, 0],
         # and Taric (export_taric.py: Codex's idle frame, its face placed by hand, in all six)
         ("taric", "idle"): [0, 0, 0, 0, 0, 0],
         # and Tristana (Codex's game-size design A, 41 rows with the goggles)
         ("tristana", "idle"): [0, 0, 0, 0, 0, 0],
         # and Fiora (Codex's game-size design B40: the pack's idle is the design in all six)
         ("fiora", "idle"): [0, 0, 0, 0, 0, 0],
         # and Fizz (Codex's game-size design A read back, 32 rows: the pack's idle is the design in all six)
         ("fizz", "idle"): [0, 0, 0, 0, 0, 0],
         # and Shaco (Codex's 46-row design v4 A with its ruff patch: the pack's idle is the design in all six)
         ("shaco", "idle"): [0, 0, 0, 0, 0, 0],
         # and Caitlyn (Codex's chibi draft B cut to 42 rows, design_caitlyn.py: the pack's idle is the design in all six)
         ("caitlyn", "idle"): [0, 0, 0, 0, 0, 0],
         # her shots: Codex's 3rd attack frame (4th Headshot frame) throws the barrel up to 16.5 (12) px over the pivot
         # and the bullet, lifted there, fell 12 degrees onto the target's pivot ("平A出去的子弹看起来是歪的");
         # League fires from the hip. The shot frame is now the lowered barrel (6.5 / 8 px up), held two slots
         ("caitlyn", "attack"): [0, 1, 3, 3, 4, 5],
         ("caitlyn", "passive"): [0, 1, 2, 4, 4, 5],
         # and Nocturne (Codex's game-size design B cut to 40 rows: the pack's idle is the design in all six)
         ("nocturne", "idle"): [0, 0, 0, 0, 0, 0],
         # and Blitzcrank (Codex's game-size design B2, fixed by hand: the pack's idle is the design in all six)
         ("blitzcrank", "idle"): [0, 0, 0, 0, 0, 0],
         # and Kai'Sa (Codex's chibi draft B cut to 44 rows, design_kaisa.py: the pack's idle is the design in all six)
         ("kaisa", "idle"): [0, 0, 0, 0, 0, 0]}
# (hero, tag): (y, slots) - in those slots everything at or above pivot row y moves down a row (the row under
# it is covered): one frame breathing, the face the same drawing throughout. Leona's shield covers her from
# the chest to the ankles, so she sinks down to its tip and only the boots stay (a seam across the shield
# would cut it in two).
BOB = {("yasuo", "idle"): (-2, [2, 3, 4]),
       ("leona", "idle"): (8, [2, 3, 4]),
       # Teemo's boots are seven rows: the lowest five stay, the rest of him sinks (seam in the shins)
       ("teemo", "idle"): (6, [2, 3, 4]),
       ("masteryi", "idle"): (1, [2, 3, 4]),
       # Annie sinks down to her shins; the shoes and the lowest stripes of her leggings stay
       ("annie", "idle"): (6, [2, 3, 4]),
       # Miss Fortune's boots start four rows under the pivot: the seam runs through their shafts
       ("missfortune", "idle"): (6, [2, 3, 4]),
       # Janna floats: all of her, down to the soles 3 px above the ground, sinks a row and rises again
       ("janna", "idle"): (12, [2, 3, 4]),
       # Malphite's short legs: the seam across his shins, his rock feet stay
       ("malphite", "idle"): (6, [2, 3, 4]),
       # Ekko crouches: the seam across his shins, the boots stay
       ("ekko", "idle"): (6, [2, 3, 4]),
       # Yone's hakama reaches his ankles: the seam across its hem, his feet stay
       ("yone", "idle"): (6, [2, 3, 4]),
       # Ezreal: the seam across his shins, the boots stay
       ("ezreal", "idle"): (6, [2, 3, 4]),
       # Thresh's robe hangs to his shins: the seam across its hem, his boots stay
       ("thresh", "idle"): (6, [2, 3, 4]),
       # Kayle floats 3 px up like Janna and sinks a row down to her soles; only her sword's tip, on the
       # ground line, stays
       ("kayle", "idle"): (10, [2, 3, 4]),
       # Fiddlesticks: the seam across his stilts, the claw feet stay
       ("fiddlesticks", "idle"): (6, [2, 3, 4]),
       # Ahri: the seam across her boots' shafts; her soles and the tips of her tails stay
       ("ahri", "idle"): (6, [2, 3, 4]),
       # Amumu: the seam across his shins, his feet stay
       ("amumu", "idle"): (6, [2, 3, 4]),
       # Jinx: the seam across her boots' shafts, her soles stay
       ("jinx", "idle"): (6, [2, 3, 4, 5]),
       # Garen: the seam across his greaves, his sabatons stay
       ("garen", "idle"): (6, [2, 3, 4]),
       # Ashe: the seam across her boots' shafts, her soles stay. Codex's redraw hangs the cloak down to 8 rows
       # under the pivot and leaves 4 rows of boots: at 6 the seam cut the cloak's last row off her thighs and
       # the legs seemed to come apart ("腿像分开了一样"); at 9 the outline does not change (6 squares of colour)
       ("ashe", "idle"): (9, [2, 3, 4]),
       # Lux: the seam across her boots' shafts, her soles stay
       ("lux", "idle"): (6, [2, 3, 4]),
       # Lucian: the seam across his shins, where the outline hardly changes; the boots and the coat's tip stay
       ("lucian", "idle"): (4, [2, 3, 4]),
       # Morgana's gown reaches the ground: the seam five rows over its hem, where two rows differ only in
       # shading (8 squares); the hem and the train's lowest rows stay
       ("morgana", "idle"): (6, [2, 3, 4]),
       # Riven: the seam across her shins, seven rows over the soles, where two rows differ least (18 squares);
       # her boots and the broken blade's tip stay
       ("riven", "idle"): (4, [2, 3, 4]),
       # Briar: the seam across her shins, under the knees' gold bands; the shackle bands and the feet stay
       ("briar", "idle"): (5, [2, 3, 4]),
       # Vayne: the seam across her shins, where the silhouette changes by 4 squares; her boots stay
       ("vayne", "idle"): (5, [2, 3, 4]),
       # Akali (the redo, design A40): her short legs are the trousers from +4 to +8 and the wrapped ankles and shoes
       # under them; the seam across the trousers at the knees, where two rows differ least above the ankles (9
       # squares, 2 of the silhouette: the kunai's tip); the ankles and the shoes stay
       ("akali", "idle"): (5, [2, 3, 4]),
       # Nami (on the ground since SINK): all of her but the fin's tip and the staff's foot sinks a row and rises
       # again, as when she floated; the seam where two rows differ least (4 squares)
       ("nami", "idle"): (8, [2, 3, 4]),
       # the silver greaves' straight part (rows 7 and 8 under the pivot differ by one square): the boots stay
       ("diana", "idle"): (7, [2, 3, 4]),
       # Veigar: the seam low in his robe, over the spiked hem (two rows differing in 2 squares of outline and 5 of
       # colour); the hem, his short legs and the boots stay
       ("veigar", "idle"): (5, [2, 3, 4]),
       # Jax: the lantern of his lamppost hangs in the same rows as his legs, so every seam cuts both; at 4 (low in
       # the shins) the legs change in 18 squares with 2 of the outline and the lantern in 4 with none
       ("jax", "idle"): (4, [2, 3, 4]),
       # Taric: his mace hangs by his side down to the knees; the seam low in the boots (two rows differing in 3
       # squares of outline and 12 of colour), the boots' lowest two rows stay
       ("taric", "idle"): (8, [2, 3, 4]),
       # Tristana: her cannon hangs to the hips, so the seam runs low in the shins (rows 96/97: 1 square of opacity and 4
       # of outline differ); only her feet stay
       ("tristana", "idle"): (8, [2, 3, 4]),
       # Fiora: her lunge stance puts both legs on diagonals, so every row differs from the next; at 8 (the boot tops)
       # 3 squares of outline and 4 of colour change and the boots stay
       ("fiora", "idle"): (8, [2, 3, 4]),
       ("fizz", "idle"): (8, [2, 3, 4]),      # ankles: the row under the seam is the one above it, one px wider
       # Shaco (43 rows since shrink_shaco.py): the seam in the pantaloons' lowest band of checks (rows 91/92 under the
       # pivot are one band: 5 squares differ); lower down every row is a gold band, the spikes or the shoes
       ("shaco", "idle"): (3, [2, 3, 4]),
       # Caitlyn: the rifle's stock reaches her hips, so the seam runs in the boot shafts (rows 7/8 under the pivot: 2
       # squares of opacity and 5 of colour differ); the boots' feet stay
       ("caitlyn", "idle"): (7, [2, 3, 4]),
       # Nocturne floats on his smoke tail: all of him sinks a row and rises again, the seam in the tail's thin straight
       # part (rows 97/98 of the design: 2 squares differ, 1 of the outline); only the tail's tip stays on the ground
       ("nocturne", "idle"): (9, [2, 3, 4]),
       # Blitzcrank: his fists hang down beside his feet, so every seam over the soles cuts them and the pistons; across
       # the feet (rows 9/10: the same outline, 16 squares of shading) the body, the fists and the ankles sink a row
       ("blitzcrank", "idle"): (9, [2, 3, 4]),
       # Kai'Sa: the seam low in her shin plates (rows 6/7 under the pivot: 2 squares of opacity and 4 of colour differ);
       # the clawed boots stay
       ("kaisa", "idle"): (6, [2, 3, 4])}
CROWN = {"leesin"}              # heroes whose head template starts at the crown (a braid stands above it)
PASTED = {"masteryi"}            # steadied on the head restyle_native pasted: his raised sword is the top of every frame
# Codex's step-2 redraw (model_strips_18, tidied by tidy_codex18.py): the approved design's head (or face) is in every
# frame, so they are steadied on idle frame 1's head like the round-1 heroes - or on their eyes when they are in
# EYES - whatever their poses.json says
REDRAWN = {"thresh", "leona", "janna", "ekko", "darius", "leesin", "malphite", "annie", "amumu",
           "jinx", "missfortune", "yone", "garen", "ashe", "ahri", "lux"}
# heroes steadied on their eyes: (R, G, B) of a colour only the eyes use; the head column is the eyes' middle
EYES = {"fiddlesticks": (200, 224, 96),   # Codex's design B: the scythe's blade is the top of every frame
        "kayle": (226, 138, 8),           # Codex's redraw: her wings rise above her head, the amber is the eyes'
        "leona": (186, 88, 30),           # the design's face pasted back by tidy_codex18.py, its iris an eye-only shade
        "janna": (3, 51, 207),            # Codex pasted one face block into every frame: her blue iris
        "ekko": (213, 125, 34),           # the same for Ekko: the one amber square of his near eye
        "darius": (255, 247, 238),        # the design face pasted back by tidy_codex18.py: his eye white
        "leesin": (212, 34, 50),          # the same for Lee Sin: the blindfold band across his face
        "malphite": (245, 166, 8),        # his new design (the moss-stone golem): the bright orange of his eyes
        "annie": (51, 32, 63),            # the design face pasted back by tidy_codex18.py: her violet pupils
        "amumu": (243, 224, 80),          # the same for Amumu: his eye yellow, in an eye-only shade
        "jinx": (209, 46, 128),           # the same for Jinx: her pink iris, in an eye-only shade
        "missfortune": (44, 129, 226),    # the same for Miss Fortune: her blue irises, in an eye-only shade
        "yone": (70, 52, 94),             # the same for Yone (no eyes under the mask): the purple strand over his face
        "garen": (31, 62, 200),           # the same for Garen: his near eye's blue iris, in an eye-only shade
        "ashe": (59, 174, 240),           # the same for Ashe: her cyan eyes (the bow is cyan too), eye-only shade
        "ahri": (233, 162, 34),           # the same for Ahri: her amber eyes (her outfit has the amber too), eye-only
        "lux": (45, 111, 184),            # the same for Lux: her blue eyes (the pair the user picked), eye-only shade
        "lucian": (63, 106, 116),         # the redesign: his raised pistol is the top of every idle frame
        "morgana": (200, 60, 166),        # the redesign A: only her face is pasted, its pink-violet is the eyes'
        "riven": (62, 142, 72),           # the design's green eyes (#3E8E48), used nowhere else
        "briar": (240, 252, 255),         # the pillory's gem is the top of every frame; the ice-white is the eyes'
        "vayne": (248, 48, 60),           # the crossbow on her back tops the frame; the lenses' red is used nowhere else
        "akali": (212, 106, 10),          # the redo A40: her ponytail tops every frame; the amber is only in the eyes
        "nami": (242, 178, 51),           # her staff's orb is the top of most frames; the amber is only in her eyes
        "diana": (114, 17, 176),          # her blade's tip tops every frame; the dark violet is only in her eyes (both)
        "veigar": (255, 209, 50),         # his hat's tip leans with the pose; the yellow of the eyes is used nowhere else
        "veigar": (255, 209, 50),         # his hat's tip leans with the pose; the yellow of the eyes is used nowhere else
        "jax": (70, 240, 255),            # the four cyan lights on his mask; his plume or lamppost tops the frames
        "taric": (24, 44, 176),           # export_taric.py sets both eyes to this blue; his raised mace tops some frames
        "tristana": (246, 186, 48),       # the goggle cups top every frame; the amber is only in her eyes
        "fiora": (24, 180, 200),          # her raised rapier tops some frames; the teal is used only in her eyes
        "fizz": (32, 174, 86),            # the trident tops the attack, E and R frames; the green is only in his eyes
        "shaco": (3, 167, 233),           # the hat's horns top every frame; the ice cyan is used only in his eyes
        "caitlyn": (20, 84, 169),         # her top hat tops most frames (the rifle W, Q 1 and R 1); the blue is only in her eyes
        "nocturne": (255, 255, 255),      # the crest or a raised blade tops the frames; pure white only in his eyes
        "blitzcrank": (243, 164, 217),    # the smokestacks and the raised fists top the frames; the pink is the eyes
        "kaisa": (130, 62, 163)}          # her raised pods top every frame; the near iris' purple is only in her eyes


def blocks(path):
    """The image read one pixel per 8x8 block; exits if a block is not one flat colour."""
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    H, W = a.shape[:2]
    if H % Z or W % Z:
        sys.exit(f"{path}: {W}x{H} is not a multiple of {Z}")
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    op = out[..., 3] >= 128
    out[~op] = 0
    out[op, 3] = 255
    return out


def cells(hero, tag, n, cell=CELL):
    """The n frames of a strip, one RGBA array per cell (56x64 px unless the hero's cells table
    says otherwise: Lee Sin's are 64x72)."""
    a = blocks(os.path.join(SRC, f"{hero}_{tag}.png"))
    cols, rows = layout(n)
    if a.shape[:2] != (rows * cell[1], cols * cell[0]):
        sys.exit(f"{hero}_{tag}.png: expected {cols}x{rows} cells of {cell[0]}x{cell[1]} px at {Z}x")
    return [a[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]]
            for k in range(n)]


def head_of(frame, crown=False):
    """The top HEAD_ROWS rows of the frame. crown=True starts at the crown instead - the first row
    at least half as wide as the widest of the rows below it - for a hero with a thin braid standing
    above the head (Lee Sin): its tip moves a pixel between idle frames and matched one frame 1 px
    off. (Lux and Ashe keep the old rule; the crown rule would move a Lux idle frame.)"""
    op = frame[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    top = ys[0]
    if crown:
        widths = [op[y].sum() for y in range(ys[0], min(ys[0] + 16, ys[-1] + 1))]
        top = ys[0] + next(i for i, w in enumerate(widths) if w >= 0.5 * max(widths))
    band = frame[top:top + HEAD_ROWS]
    xs = np.nonzero(band[..., 3].any(0))[0]
    return band[:, xs[0]:xs[-1] + 1]


def pasted_head(hero):
    """The head restyle_native.py pastes into every frame (the design sheet's head rect without its
    cut pixels), for a hero whose hair swings above it ("hair_part" in its poses.json: Yasuo's
    ponytail is the top of every frame and changes each time) or whose head is pasted on the torso
    (restyle "anchor": Malphite's back spikes, voted anew each frame, are the top of every frame); None
    for everyone else. A hero in PASTED
    is steadied on League's head joint, where its head was pasted (Master Yi's sword crosses his helmet
    in most run frames, so the helmet is not found whole)."""
    if hero in PASTED:
        return "joint"
    if hero in REDRAWN:
        return None
    path = os.path.join(ROOT, "assets", "source", hero, "poses.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    if "restyle" not in spec or not (spec.get("hair_part") or spec["restyle"]["head"].get("anchor")):
        return None
    if spec["restyle"]["head"].get("mode") == "voted":
        return "joint"      # no two heads alike: steady on League's head joint from the cells table
    x0, y0, w, h = spec["restyle"]["head"]["rect"]
    tpl = blocks(os.path.join(SRC, f"{hero}_native.png"))[y0:y0 + h, x0:x0 + w].copy()
    for x, y in spec["restyle"]["head"].get("cut", []):
        tpl[y - y0, x - x0] = 0
    return tpl


def eye_column(frame, rgb):
    """The middle column of the pixels of colour rgb (a hero's eyes), rounded; None when there are none."""
    m = (frame[..., 3] > 0) & (frame[..., :3] == np.array(rgb, np.uint8)).all(-1)
    xs = np.nonzero(m)[1]
    return int(np.floor(xs.mean() + 0.5)) if len(xs) else None


def find(frame, tpl):
    """(share of tpl's pixels matched exactly, x, y) at the best spot."""
    th, tw = tpl.shape[:2]
    m = tpl[..., 3] > 0
    best = (0.0, 0, 0)
    for y in range(frame.shape[0] - th + 1):
        for x in range(frame.shape[1] - tw + 1):
            s = ((frame[y:y + th, x:x + tw] == tpl).all(-1) & m).sum() / m.sum()
            if s > best[0]:
                best = (s, x, y)
    return best


def build(hero):
    """{tag: [(frame centred on its pivot, ms)]} and {tag: [(head column from the pivot, moved)]}."""
    with open(os.path.join(SRC, f"{hero}_cells.json"), encoding="utf-8") as f:
        spec = json.load(f)
    table, cell = spec["tags"], tuple(spec.get("cell", CELL))
    head = pasted_head(hero)
    joint = isinstance(head, str)
    if head is None and hero not in EYES:
        head = head_of(cells(hero, "idle", len(table["idle"]), cell)[0], crown=hero in CROWN)
    sheet, report = {}, {}
    for tag, rows in table.items():
        fr = cells(hero, tag, len(rows), cell)
        if joint:
            hx = [int(np.floor(r["head"][0] + 0.5)) - r["pivot"][0] for r in rows]
        elif hero in EYES:
            cols = [eye_column(f, EYES[hero]) for f in fr]
            hx = [None if c is None else c - r["pivot"][0] for c, r in zip(cols, rows)]
        else:
            found = [find(f, head) for f in fr]
            hx = [x - r["pivot"][0] if s >= SURE else None for (s, x, _), r in zip(found, rows)]
        dx = [0] * len(fr)
        # a PASTED hero's idle is one frame (ORDER): steady on the frames shown, or it moves off its pivot
        used = sorted(set(ORDER.get((hero, tag), range(len(fr))))) if hero in PASTED else range(len(fr))
        sure = [hx[k] for k in used if hx[k] is not None]
        if tag in STEADY and sure:
            target = round(sum(sure) / len(sure))
            dx = [0 if h is None else target - h for h in hx]
        order = ORDER.get((hero, tag), range(len(fr)))
        sheet[tag] = [(G.centre_frame(fr[k], dx[k] - rows[k]["pivot"][0], sunk(hero, fr[k], rows[k]["pivot"][1])),
                       rows[slot]["ms"]) for slot, k in enumerate(order)]
        report[tag] = [(None if hx[k] is None else hx[k] + dx[k], dx[k]) for k in order]
    return sheet, report


def sunk(hero, frame, py):
    """The frame's row offset for centre_frame: -py, plus the rows SINK moves it down (as far as the soles row lets
    its lowest pixel go)."""
    n = SINK.get(hero, 0)
    ys = np.nonzero(frame[..., 3].any(1))[0]
    if n and len(ys):
        n = max(0, min(n, SOLES - (ys[-1] - py)))
    return -py + n


def touch_up(hero, sheet):
    """Apply <hero>_retouch.json to the cut frames in place; the number of pixels changed."""
    path = os.path.join(SRC, f"{hero}_retouch.json")
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    pal = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in spec["palette"].items()}
    n = 0
    for tag, frames in spec["frames"].items():
        for k, pixels in enumerate(frames):
            a = sheet[tag][k][0]
            hh, hw = a.shape[0] // 2, a.shape[1] // 2
            for x, y, was, now in pixels:
                r, c = hh + y, hw + x
                p = a[r, c] if 0 <= r < a.shape[0] and 0 <= c < a.shape[1] else None
                if p is None or (p[3] != 0 if was == "." else p[3] == 0 or tuple(p[:3]) != pal[was]):
                    sys.exit(f"{os.path.basename(path)}: {tag} frame {k + 1} at ({x}, {y}) is not '{was}' any more")
                a[r, c] = (0, 0, 0, 0) if now == "." else pal[now] + (255,)
                n += 1
    return n


def neck_up(hero, sheet):
    """NECK_UP: the pasted head up its rows with the idle's neck and collar under it; the frames changed."""
    changed = 0
    if not any(h == hero for h, _ in NECK_UP):
        return 0
    eye = np.array(EYES[hero])
    idle = sheet["idle"][0][0]
    ys, xs = np.nonzero((idle[..., :3] == eye).all(-1) & (idle[..., 3] > 0))
    iey, iex = int(ys.max()), int(round(xs.mean()))
    head = [(y - iey, x - iex) for y, x in zip(*np.nonzero(idle[..., 3] > 0)) if y <= iey + 3 and abs(x - iex) <= 9]
    for (h, tag), plan in NECK_UP.items():
        if h != hero or tag not in sheet:
            continue
        for k, todo in enumerate(plan):
            if not todo:
                continue
            rows, left, right = todo[:3]
            a, ms = sheet[tag][k]
            pad = rows + 16
            c = np.pad(a, ((pad, pad), (pad, pad), (0, 0)))
            cy, cx = c.shape[0] // 2, c.shape[1] // 2
            if (hero, tag, k) in NECK_EYES:
                dy, dx = NECK_EYES[(hero, tag, k)]
                ey, ex = cy + dy, cx + dx
            else:
                ys, xs = np.nonzero((c[..., :3] == eye).all(-1) & (c[..., 3] > 0))
                ey, ex = int(ys.max()), int(round(xs.mean()))
            mine = [(dy, dx) for dy, dx in head if c[ey + dy, ex + dx, 3]
                    and (c[ey + dy, ex + dx, :3] == idle[iey + dy, iex + dx, :3]).all()]
            pix = {q: c[ey + q[0], ex + q[1]].copy() for q in mine}
            for dy, dx in mine:
                c[ey + dy, ex + dx] = 0
            ney = ey - rows
            for dy in range(4, 4 + rows):                       # the idle's neck and collar under the new chin
                for dx in range(-left, right + 1):
                    q = idle[iey + dy, iex + dx] if 0 <= iex + dx < idle.shape[1] else (0, 0, 0, 0)
                    if q[3] and (c[ney + dy, ex + dx, 3] == 0 or ney + dy <= ey + 3):
                        c[ney + dy, ex + dx] = q
            for (dy, dx), p in pix.items():
                c[ney + dy, ex + dx] = p
            if "fill" in todo[3:]:                               # a clear gap under the chin: the idle's neck
                for dy in range(4 + rows, 6 + rows):
                    for dx in (-1, 0, 1):
                        q = idle[iey + dy, iex + dx]
                        if c[ney + dy, ex + dx, 3] == 0 and q[3]:
                            c[ney + dy, ex + dx] = q
            for dy, dx in mine:                                  # left open where the head was
                y, x = ey + dy, ex + dx
                if c[y, x, 3] == 0:
                    near = [tuple(int(v) for v in c[y + yy, x + xx, :3]) for yy, xx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                            if c[y + yy, x + xx, 3]]
                    if len(near) >= 3:
                        c[y, x, :3] = max(set(near), key=near.count)
                        c[y, x, 3] = 255
            op = c[..., 3] > 0
            pp = np.pad(op, 1)
            shut = ~op & pp[:-2, 1:-1] & pp[2:, 1:-1] & pp[1:-1, :-2] & pp[1:-1, 2:]
            shut[:max(0, ney - 14)] = False
            shut[ney + 12:] = False
            for y, x in zip(*np.nonzero(shut)):                  # clear pixels shut in on four sides
                near = [tuple(int(v) for v in c[y + yy, x + xx, :3]) for yy, xx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
                c[y, x, :3] = max(set(near), key=near.count)
                c[y, x, 3] = 255
            sheet[tag][k] = (G.centre_frame(c, -cx, -cy), ms)
            changed += 1
    return changed


def step(hero, sheet):
    """STEP: move the upper body of each frame, with its cape, down its rows over the legs; the frames moved."""
    moved = 0
    for (h, tag), (y0, rows, cape) in STEP.items():
        if h != hero or tag not in sheet:
            continue
        wine = np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for c in cape])
        for k, d in enumerate(rows):
            if not d:
                continue
            a, ms = sheet[tag][k]
            cy = a.shape[0] // 2
            cut = cy + y0 + 1                        # array rows before `cut` sit at pivot rows <= y0
            op = a[..., 3] > 0
            block = np.zeros(op.shape, bool)
            block[:cut] = op[:cut]
            for r in range(cut, a.shape[0]):         # the cape under the seam
                cols = np.nonzero(op[r] & (a[r, :, None, :3] == wine).all(-1).any(-1))[0]
                if len(cols):
                    block[r, :cols.max() + 2] = op[r, :cols.max() + 2]
                    continue
                c, hang = 0, False
                while c < a.shape[1]:                # its tip: the runs touching the cape in the row above
                    if not op[r, c]:
                        c += 1
                        continue
                    e = c
                    while e < a.shape[1] and op[r, e]:
                        e += 1
                    if r > cut and block[r - 1, max(0, c - 1):e + 1].any() and (r - 1 >= cut):
                        block[r, c:e] = True
                        hang = True
                    c = e
                if not hang:
                    break
            b = np.pad(a, ((0, d), (0, 0), (0, 0)))
            upper = np.zeros_like(b)
            upper[d:a.shape[0] + d][block] = a[block]
            b[:a.shape[0]][block] = 0
            m = upper[..., 3] > 0
            b[m] = upper[m]
            # a clear pixel the move closes in on all four sides (the cape's edge come down beside a leg) takes its
            # commonest neighbour
            def shut(o):
                p = np.pad(o, 1)
                return ~o & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
            was = shut(np.pad(op, ((0, d), (0, 0))))
            for y, x in zip(*np.nonzero(shut(b[..., 3] > 0) & ~was)):
                near = [tuple(int(v) for v in b[y + dy, x + dx, :3]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
                b[y, x, :3] = max(set(near), key=near.count)
                b[y, x, 3] = 255
            sheet[tag][k] = (G.centre_frame(b, -(b.shape[1] // 2), -cy), ms)
            moved += 1
    return moved


def breathe(hero, sheet):
    """BOB and NECK: move the upper body of the listed slots down a row (after the retouch, which is drawn on the
    frame before it moves)."""
    for (h, tag), (y0, slots) in list(BOB.items()) + list(NECK.items()):
        if h != hero or tag not in sheet:
            continue
        for k in slots:
            a, ms = sheet[tag][k]
            cut = a.shape[0] // 2 + y0 + 1           # array rows before `cut` sit at pivot rows <= y0
            b = a.copy()
            b[1:cut + 1] = a[0:cut]
            b[0] = 0
            sheet[tag][k] = (b, ms)


def close_outline(hero, sheet):
    """COMPLETE: strips.complete_outline on every frame, in idle frame 1's outline colour, then CLEAN:
    strips.clean_outline; (added, darkened, {clean rule: pixels})."""
    if hero not in COMPLETE:
        return 0, 0, {}
    first = sheet["idle"][0][0]
    op = first[..., 3] > 0
    p = np.pad(op, 1)
    edge = op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    dark = [tuple(int(v) for v in c) for c in first[edge & (G.lum(first[..., :3]) < 70)][:, :3]]   # the commonest
    colour = max(set(dark), key=dark.count)
    added = darkened = 0
    tidy = {}
    for tag, frames in sheet.items():
        for k, (a, ms) in enumerate(frames):
            b = np.pad(a, ((1, 1), (1, 1), (0, 0)))              # room for an outline round the widest pixel
            c = b.shape[0] // 2
            low = int(np.nonzero(b[..., 3].any(1))[0].max())
            before = b
            b, n, d = G.complete_outline(b, color=colour, dark=DARK.get(hero, 70), feet=max(c + SOLES, low))
            if hero in CLEAN:
                face = np.zeros(b.shape[:2], bool)
                ys, xs = np.nonzero((b[..., :3] == EYES[hero]).all(-1) & (b[..., 3] > 0))
                if len(ys):
                    cy, cx = int(ys.mean()), int(xs.mean())
                    face[max(0, cy - 6):cy + 6, max(0, cx - 7):cx + 7] = True
                elif hero in STRICT:                         # no eyes to find the face by (lying, turned away): the
                    face[:] = True                           # tidy would take an eye's dark pixel for a crumb
                new_px = (b[..., 3] > 0) & (before[..., 3] == 0)
                b, counts = G.clean_outline(b, colour, dark=DARK.get(hero, 70), keep=face, bare=BARE.get(hero, ()),
                                            strict=hero in STRICT, added=new_px)
                for rule, v in counts.items():
                    tidy[rule] = tidy.get(rule, 0) + v
                if hero in BARE:
                    b, m = G.straighten_lines(b, BARE[hero])
                    tidy["straight"] = tidy.get("straight", 0) + m
            frames[k] = (G.centre_frame(b, -(b.shape[1] // 2), -c), ms)
            added += n
            darkened += d
    return added, darkened, tidy


def flatness(frames):
    """Share of opaque pixels whose right neighbour is opaque and the same colour."""
    same = n = 0
    for a in frames:
        op = a[..., 3] > 0
        pair = op[:, :-1] & op[:, 1:]
        same += (pair & (a[:, :-1, :3] == a[:, 1:, :3]).all(-1)).sum()
        n += op.sum()
    return same / n


def review(hero, sheet, out, z=4):
    hw = max(a.shape[1] // 2 for fr in sheet.values() for a, _ in fr)
    hh = max(a.shape[0] // 2 for fr in sheet.values() for a, _ in fr)
    W, H = 2 * hw + 1, 2 * hh + 1
    cols = max(len(fr) for fr in sheet.values())
    img = Image.new("RGBA", (cols * (W + 2) * z, len(sheet) * (H + 2) * z), (72, 76, 84, 255))
    for j, fr in enumerate(sheet.values()):
        for i, (a, _) in enumerate(fr):
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            guide = np.zeros((H, W, 4), np.uint8)
            guide[hh + 12, :] = (96, 160, 96, 255)          # the row under the soles
            guide[:, hw] = (96, 160, 96, 255)               # the pivot column
            c.alpha_composite(Image.fromarray(guide, "RGBA"))
            c.alpha_composite(Image.fromarray(a, "RGBA"), (hw - a.shape[1] // 2, hh - a.shape[0] // 2))
            img.alpha_composite(c.resize((W * z, H * z), Image.NEAREST), (i * (W + 2) * z, j * (H + 2) * z))
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, f"{hero}_native.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", help="default: every <hero>_cells.json in assets/source/native")
    ap.add_argument("--review", help="write a frame sheet per hero to this folder")
    args = ap.parse_args()
    heroes = args.hero or sorted(os.path.basename(p)[:-len("_cells.json")]
                                 for p in glob.glob(os.path.join(SRC, "*_cells.json")))
    for hero in heroes:
        sheet, report = build(hero)
        necks = neck_up(hero, sheet)
        if necks:
            print(f"{hero}: pasted head put back on its neck in {necks} frames")
        touched = touch_up(hero, sheet)
        if touched:
            print(f"{hero}_retouch.json: {touched} pixels retouched")
        stepped = step(hero, sheet)
        if stepped:
            print(f"{hero}: walk step on {stepped} frames")
        breathe(hero, sheet)
        added, darkened, tidy = close_outline(hero, sheet)
        if added or darkened:
            print(f"{hero}: outline closed with {added} pixels added, {darkened} darkened on the feet line")
        if tidy:
            print(f"{hero}: outline tidied: " + ", ".join(f"{k} {v}" for k, v in tidy.items()))
        w, h = G.write_sheet(os.path.join(MOD, "champions", f"league_{hero}"), sheet)
        frames = [a for fr in sheet.values() for a, _ in fr]
        colours = len(np.unique(np.concatenate([a[a[..., 3] > 0][:, :3] for a in frames]), axis=0))
        print(f"league/champions/league_{hero}#sheet.png {w}x{h}: {len(frames)} frames, {colours} colours, "
              f"{flatness(frames):.0%} of pixels match their right neighbour")
        for tag, r in report.items():
            moved = [d for _, d in r]
            print(f"  {tag:8s} head column " + " ".join("  ?" if c is None else f"{c:+3d}" for c, _ in r) +
                  (f"   moved {' '.join(f'{d:+d}' for d in moved)}" if any(moved) else "") +
                  (f"   order {ORDER[(hero, tag)]}" if (hero, tag) in ORDER else ""))
        if args.review:
            review(hero, sheet, args.review)


if __name__ == "__main__":
    main()
