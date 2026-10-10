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
nose and face side; Lux's staff below her hand and the brow row over her eyes, a table tools/art/lux_retouch.py
writes): x, y from the pivot, the colour expected there and the new one. A pixel that no longer has
the expected colour stops the import, so edits made for one version of the strips never land on another.
Then <hero>_bake.json, when there is one, draws effect pictures with a front and a back into the action frames (the
client mirrors the hero's frames with his facing, never an effect picture: league_jhin's muzzle flashes; bake()).
Writes league/champions/league_<hero>. The effects still come from tools/art/import_<hero>.py, which
writes the round-1 body only with --body.
--review DIR writes <hero>_native.png: every frame at 4x around its pivot (pivot column, feet line).
"""
import argparse
import glob
import importlib
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
import idle_breathe as IB  # noqa: E402
from native_refs import CELL, Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
HEAD_ROWS = 12                  # idle frame 1's top rows: the head
SURE = 0.9                      # share of the head's pixels that must match exactly
STEADY = ("idle", "run")
# (hero, tag) left as drawn: Rakan's run head rides on the body (tools/art/fix_rakan_strips.py SEAT, the user:
# 「移动的时候头和身体不协调」) - steadied on the head, the frames would slide the body back under a still head
UNSTEADY = {("rakan", "run"), ("kogmaw", "idle"), ("kogmaw", "run"), ("karma", "idle"), ("karma", "run"),
            ("hecarim", "run"), ("senna", "run")}   # kogmaw: his antennae sway in both (rig_kogmaw.py), so
# his top rows are no fixed head to steady on - steadied, the sway would turn into the whole body sliding
# karma: her jade ring floats above her head in the idle (rig_karma.py's bob), the same reason; her run is steadied on
# League's head track already (fix_karma_strips.py STEADY), which keeps League's 1-2 column sway; hecarim: his run is
# steadied on the rider's eyes along League's head track (fix_hecarim_strips.py STEADY), each frame's helm his own;
# senna: her run is steadied on its one pasted head already (fix_senna_strips.py STEADY, one pivot for every frame)
# idle_breathe.py makes every idle the design breathing (breathe_idle, run last); BREATHE_SKIP keeps an idle as drawn
# (Brand's idle is already six drawings of his burning body; Tristana, Jax and Pyke hold or lean on their weapon in a
# wide crouch, and after two rounds the user kept their old idles: 「小炮 夹克 派克 全用旧的吧」; Yone, Gwen and Kayle went
# back too: 「永恩 格温 凯尔 恢复到之前的」, then Alistar, Soraka, Blitzcrank: 「牛头 / 索拉卡 / 机器人恢复到之前的」,
# 2026-10-08), NO_NOD breathes without the head's late nod
# Xayah breathes in her own strip (rig_xayah.breath_frames: her striped leg wraps have no invisible row to cut - the
# shared cut shortened them, 「腿部还有变形」 - so the body sinks a row OVER the legs instead); Rengar too (rig_rengar BREATH:
# the shared lean smeared his toes, his carried blade went under the soles); Zed too (rig_zed BREATH: the shared cut ran
# through his wrist blades and shortened them); Olaf too (rig_olaf BREATH: the shared cut ran through his spiked greaves);
# Viktor too (fix_viktor_stand BREATH: the shared cut and lean put an orange square in his mirrored far boot);
# Talon too (his strips are League's own animation recoloured - tools/art/restyle_native.py - its idle moves already);
# Senna too: her cannon lies on her shoulder from over the hood down past her knee - every breathing cut would run
# through it (Draven's 「上下摆动武器变形」)
# Shen too (fix_shen_strips.breath: the body sinks over his legs - the shared cut shortened his trousers, boots,
# apron and tail hem)
BREATHE_SKIP = {"renekton", "sivir", "brand", "tristana", "jax", "pyke", "yone", "gwen", "kayle", "alistar", "soraka", "blitzcrank", "xayah", "rengar", "kogmaw", "zed", "karma", "olaf", "viktor", "talon", "draven", "senna", "shen"}   # sivir: the user's pick of a still idle (「希维尔改成静止不动吧」): every seam on her shrunk wide stance pulled her
# hips or her slanted boots
# renekton: the user's pick of a still idle after the 90% shrink (「C吧」, from main's / a shin breath / still)
# idle_breathe options per hero (the user's review of the first roster GIF, 2026-10-08: Akali, Alistar, Ashe, Briar and
# Ezreal "有问题"): mode "seam" nods with a full-width row under the chin instead of the head piece, deep lets the body's
# rows come from down to the shins
# cut zones forced into the shins where the default zone found a cheaper seam elsewhere: Kennen, LeBlanc, Janna and Twisted Fate are short or skirted (the zone rows landed in
# the skirt or the weapon); Renekton and Vayne crouch, their figure is squat and the 30% band started in the torso
# (「鳄鱼的脚有点怪」「薇恩有点怪」, 2026-10-08)
# Kennen's went lower still, to his boots (0.08): at 0.18 the cut ran through the gold bar on his coat's hem
# (「凯南待机时武器也变形」)
BREATHE_OPTS = {"kennen": {"zone": (0.08, 1)}, "leblanc": {"zone": (0.18, 1)},
                "janna": {"zone": (0.18, 1)}, "twistedfate": {"zone": (0.18, 1)},
                "vayne": {"zone": (0.20, 1)},
                "aatrox": {"sway": [0] * 8},   # his hand left the planted sword's hilt when the body leant
                # Samira's second design (2026-10-09): a wide stance - the lean moved her shins and boots (Sivir's
                # 「上下摆动时 希维尔的鞋变形了吧」); only the dip, the legs stand still
                "samira": {"sway": [0] * 8},
                # Draven's League idle (90 %, both axes out wide): the lean swung the far axe and sheared him over his
                # legs - 「游戏里左右晃动的太大了吧 模型都变形」; only the dip
                # and 「头和身体不协调」: his head no longer followed the dip a frame late (lag 0); then 「上下摆动武器变形」:
                # the dip's shin rows cut the near axe hanging by his knee - he does not breathe (BREATHE_SKIP)
                "draven": {"sway": [0] * 8, "lag": 0}}
# hero: [(colour set, box)] of the weapon in the hero's hands. idle_breathe would cut or hinge THROUGH a weapon that
# reaches the shins (the user's reviews, 2026-10-08: 「剑魔和盖伦武器有点变形」「锐雯武器变形」「莎米拉武器变形」「妖姬和
# 金克丝的武器也有点变形」「维鲁斯武器变形」, then 「小鱼人 凯隐 蛮王 艾希 烬武器变形」), so the weapon's pixels are lifted out
# before the breath and stamped back moved with the body, rigid: each frame's dip and lean. Frozen in place instead (the
# first try for the planted swords), the hands slid along the hilt and the blade kinked where it met them (「盖伦手拿武器
# 变形」「锐雯手拿武器变形」「莎米拉现在太怪异」); carried, a planted tip just dips 1-2 rows as the hero leans on it.
# The box is (row0, row1, col0, col1) relative to (the soles' row, the frame's centre); colours are the weapon's own,
# read from the design (charmaps), and the box keeps out the body parts that share them (Varus's trousers are his bow's
# violets, Jinx's boots her gun's greys, Kayn's sash his scythe's red).
WEAPON_CARRY = {
    # Xin Zhao's spear, held low across him: the head left of his back leg (all its colours there), the shaft's browns
    # between the head and his face (his belt's browns start a row lower), the butt by his head (「怎么武器也变形」)
    "xinzhao": [({(0xA7, 0xA5, 0xC0), (0xA7, 0x2D, 0xE2), (0x2A, 0x09, 0x41), (0x43, 0x0F, 0x67), (0x1E, 0x09, 0x2F), (0x34, 0x16, 0x20), (0x7F, 0x1B, 0xB5), (0xA4, 0x6E, 0x21), (0xEA, 0xB2, 0x41), (0x6E, 0x6A, 0x82), (0x0D, 0x0A, 0x19), (0x86, 0x52, 0x3F), (0x61, 0x32, 0x31)},
                 (-17, -1, -44, -19)),
                ({(0x86, 0x52, 0x3F), (0x61, 0x32, 0x31)}, (-32, -13, -21, 16)),
                ({(0xA7, 0xA5, 0xC0), (0xA7, 0x2D, 0xE2), (0x2A, 0x09, 0x41), (0x43, 0x0F, 0x67), (0x1E, 0x09, 0x2F), (0x34, 0x16, 0x20), (0x7F, 0x1B, 0xB5), (0xA4, 0x6E, 0x21), (0xEA, 0xB2, 0x41), (0x6E, 0x6A, 0x82), (0x0D, 0x0A, 0x19), (0x86, 0x52, 0x3F), (0x61, 0x32, 0x31)},
                 (-37, -27, 13, 23))],
    "garen": [({(0x9B, 0xAB, 0xC3), (0xA9, 0xB7, 0xCB), (0x8A, 0x8A, 0xA3), (0x28, 0x49, 0x65), (0x29, 0x63, 0x80),
                (0xFC, 0xFC, 0xFC)}, (-13, 0, -99, 99))],
    "riven": [({(0xD0, 0xBF, 0xB0), (0xBB, 0xAA, 0x9C), (0xA8, 0x95, 0x88), (0x86, 0x74, 0x69), (0x43, 0x4A, 0x46),
                (0x27, 0x27, 0x20), (0xF6, 0xEA, 0xDB), (0x24, 0x18, 0x1F)}, (-12, -1, 1, 99))],
    # Samira (second design, 2026-10-09): the greatsword's lower blade by the far boot and the far holster's pistol
    "samira": [({(0xB0, 0xB2, 0xBB), (0xC2, 0xC5, 0xD4), (0x34, 0x37, 0x43), (0x7E, 0x80, 0x86), (0xE6, 0xE5, 0xE0)},
                (-13, 0, 5, 99))],
    "aatrox": [({(0xBF, 0x16, 0x30), (0x8F, 0x0E, 0x2B), (0xF2, 0x32, 0x3B), (0xFF, 0x7A, 0x2A), (0x27, 0x0D, 0x28),
                 (0x42, 0x22, 0x4C), (0x68, 0x40, 0x7A)}, (-14, 0, -99, -10))],
    "leblanc": [({(0xF4, 0xAA, 0x45), (0xDE, 0x8D, 0x36), (0xFC, 0xC9, 0x67), (0xF9, 0xB9, 0x54), (0xFD, 0xE5, 0x9B),
                  (0x2B, 0x01, 0x0E), (0xC9, 0x0D, 0x33), (0xAA, 0x01, 0x1B), (0x7F, 0x00, 0x15), (0x39, 0x0C, 0x20),
                  (0xB8, 0x66, 0x2B), (0x2C, 0x40, 0xA3)}, (-40, 0, 10, 99))],
    "varus": [({(0xE8, 0x38, 0xF3), (0x3B, 0x18, 0x5F), (0xCA, 0x2B, 0xFB), (0xA1, 0x12, 0xF7), (0xD3, 0x20, 0x87),
                (0x65, 0x24, 0x93), (0x52, 0x04, 0xBA)}, (-34, -2, 4, 99))],
    "jinx": [({(0xBB, 0x21, 0x70), (0xFB, 0x95, 0xD7), (0x5A, 0x18, 0x41), (0x45, 0x3F, 0x51), (0xC7, 0xAA, 0x64),
               (0xCC, 0x94, 0x3A), (0x8B, 0x5E, 0x29), (0x31, 0x29, 0x33), (0x1B, 0x14, 0x20)}, (-16, -8, 3, 99))],
    "fizz": [({(0x81, 0x1C, 0x2C), (0xC5, 0x9B, 0x4C), (0x3D, 0x32, 0x23), (0x8A, 0x64, 0x31), (0x4C, 0x20, 0x29), (0x0A, 0x5B, 0x4A), (0x07, 0x8E, 0x76), (0x96, 0xB9, 0xC6)}, (-12, -10, -99, 99)),                # the shaft, across her
             ({(0x81, 0x1C, 0x2C), (0xC5, 0x9B, 0x4C), (0x3D, 0x32, 0x23), (0x8A, 0x64, 0x31), (0x4C, 0x20, 0x29), (0x0A, 0x5B, 0x4A), (0x07, 0x8E, 0x76), (0x96, 0xB9, 0xC6), (0xDE, 0xDF, 0xD5), (0x0F, 0x3B, 0x3C)}, (-18, -4, 16, 99)),   # the prongs
             ({(0x81, 0x1C, 0x2C), (0xC5, 0x9B, 0x4C), (0x3D, 0x32, 0x23), (0x8A, 0x64, 0x31), (0x4C, 0x20, 0x29), (0x0A, 0x5B, 0x4A), (0x07, 0x8E, 0x76), (0x96, 0xB9, 0xC6)}, (-14, -8, -99, -19))],                # the butt's ring
    "kayn": [({(0x38, 0xB1, 0xFD), (0xC6, 0x0F, 0x3E), (0x6E, 0x1F, 0x33), (0xFD, 0x20, 0x5B), (0x3A, 0x2C, 0x66), (0x5B, 0x3A, 0x8A), (0x14, 0x18, 0x26)}, (-25, -1, -99, -8)),
             ({(0x5B, 0x3A, 0x8A), (0xC6, 0x0F, 0x3E)}, (-13, -1, 9, 99))],     # the blade, and the haft's foot with its spike
    "tryndamere": [({(0xF5, 0xF6, 0xF8), (0xB9, 0xC2, 0xD8), (0x9A, 0xA5, 0xC2), (0x66, 0x6E, 0x90), (0x1F, 0x20, 0x30), (0x44, 0x4B, 0x6C), (0x81, 0x86, 0xA4), (0x2F, 0x34, 0x4C)},
                    (-16, 0, -99, -11))],
    "ashe": [({(0x00, 0x47, 0x84), (0x81, 0xDD, 0xEF), (0x03, 0x7C, 0xB4), (0x0F, 0xB3, 0xEB), (0x00, 0x18, 0x40), (0x28, 0x1E, 0x19), (0x01, 0x21, 0x55), (0x00, 0x14, 0x37)},
              (-25, -3, 5, 99))],
    "viktor": [({(0xF7, 0xD0, 0x4A), (0xC8, 0x40, 0x0A), (0xA8, 0x66, 0x2E), (0xD4, 0x9A, 0x1E), (0xFF, 0x8A, 0x1E), (0x1E, 0x86, 0xE0), (0x4A, 0xD8, 0xF8), (0x8A, 0x5A, 0x10), (0x5B, 0x61, 0x94), (0xA3, 0xAA, 0xD6), (0x6A, 0x4A, 0x5A), (0x7E, 0x86, 0xB8), (0x6F, 0x86, 0xAE), (0xA0, 0x20, 0x2A), (0x5A, 0x0A, 0x1E)},
                (-41, 0, -99, -6))],   # his staff, head to foot, left of his cloak's red (「维克托武器也变形」)
    "jhin": [({(0x26, 0x2A, 0x3A), (0x4A, 0x54, 0x70), (0xD8, 0x90, 0x2C), (0xA0, 0x58, 0x1A), (0xFF, 0xD8, 0x78), (0x74, 0x85, 0x9E), (0x5A, 0x2E, 0x10), (0xD2, 0xCA, 0xB0)},
              (-13, -1, 6, 99))],
    # Xayah's two feather blades hanging from the near hand (rig_xayah BLADES: rows -10..-5, columns +14..+19)
    "xayah": [({(0x5F, 0x0A, 0x3D), (0x76, 0x14, 0x81), (0xB2, 0x15, 0x90), (0xF0, 0x2D, 0x71)}, (-11, -4, 13, 20))],
    # Vladimir's steel claws hanging from both gauntlets at thigh height (rig_vladimir FAR / NEAR: the far hand's rows
    # -16..-9, columns -13..-7; the near hand's rows -12..-9, columns +7..+12) - the breath's seam would cut a claw short
    "vladimir": [({(0xD5, 0xE6, 0xF7), (0x87, 0xA1, 0xC6), (0x3D, 0x49, 0x6A)}, (-17, -8, -14, -6)),
                 ({(0xD5, 0xE6, 0xF7), (0x87, 0xA1, 0xC6), (0x3D, 0x49, 0x6A)}, (-13, -8, 6, 13))],
    # 「诺手待机动作武器变形」: the haft's top (the ball and the brown shaft over his pauldron) and the axe's head by his
    # feet, carried whole with his hands (the haft between runs behind his arm); the head dips like LeBlanc's staff foot
    "darius": [({(0x0B, 0x03, 0x12), (0x06, 0x02, 0x0B), (0x08, 0x03, 0x0E), (0xF2, 0xF3, 0xF4), (0xBA, 0xBF, 0xC9), (0x94, 0x9B, 0xAD), (0x32, 0x26, 0x2B), (0x37, 0x39, 0x44), (0x4F, 0x3C, 0x3A)},
                (-42, -30, -18, -14)),
               ({(0xF2, 0xF3, 0xF4), (0xBA, 0xBF, 0xC9), (0x94, 0x9B, 0xAD), (0x32, 0x26, 0x2B), (0x37, 0x39, 0x44), (0x38, 0x3B, 0x46), (0x22, 0x24, 0x2D), (0x7D, 0x10, 0x27), (0x55, 0x5B, 0x6C), (0x63, 0x68, 0x7C), (0x7A, 0x80, 0x91), (0x14, 0x14, 0x1C)},
                (-12, 0, -24, -10))],
    # Lulu's staff runs from over her hat down across her body to its foot between her boots (cols 0..+3): its three
    # woods carried down to the robe's hem only (rows -20..-4) - the foot stays planted between the boots, which share
    # the staff's darkest brown (carried, the foot and a square of the far boot sank under the soles: the boot came
    # apart, 2026-10-08); the boots' plum (#4E3040) and the hat's dark gold stay out
    "lulu": [({(0xB4, 0x7A, 0x4E), (0x5A, 0x2E, 0x1A), (0x2E, 0x16, 0x0E)}, (-20, -4, -3, 99))],
}


CARRY_FILL = {"darius"}


def shut_in(op):
    """The see-through squares of a frame no path through other see-through squares joins to its border."""
    h, w = op.shape
    out = np.zeros(op.shape, bool)
    out[0], out[-1], out[:, 0], out[:, -1] = ~op[0], ~op[-1], ~op[:, 0], ~op[:, -1]
    stack = list(zip(*np.nonzero(out)))
    while stack:
        y, x = stack.pop()
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < h and 0 <= xx < w and not op[yy, xx] and not out[yy, xx]:
                out[yy, xx] = True
                stack.append((yy, xx))
    return list(zip(*np.nonzero(~op & ~out)))


def weapon_mask(a, colours, box):
    """The weapon's pixels: every pixel of the weapon's own colours inside `box` (rows/columns relative to (the soles'
    row, the frame's centre), None = the whole frame), plus the dark outline squares that ring them. No flooding: a
    blade is colour patches split by its own outline, and a seed flood dies at the first outline it meets."""
    op = a[..., 3] > 0
    sole = int(np.nonzero(op.any(1))[0].max())
    cx = a.shape[1] // 2
    ins = np.zeros(op.shape, bool)
    if box is None:
        ins[:] = True
    else:
        r0, r1, c0, c1 = box
        ins[max(0, sole + r0):sole + r1 + 1, max(0, cx + c0):cx + c1 + 1] = True
    m = np.zeros(op.shape, bool)
    for y, x in zip(*np.nonzero(op & ins)):
        if (int(a[y, x, 0]), int(a[y, x, 1]), int(a[y, x, 2])) in colours:
            m[y, x] = True
    dark = (a[..., :3].astype(int).sum(-1) < 210) & op
    air = ~op
    for _ in range(4):                                       # the outline ring, grown to outline that belongs only to
        near = np.zeros(op.shape, bool)                      # the weapon (a blade tip is 1-2 bare outline pixels)
        near[1:] |= m[:-1]; near[:-1] |= m[1:]; near[:, 1:] |= m[:, :-1]; near[:, :-1] |= m[:, 1:]
        near[1:, 1:] |= m[:-1, :-1]; near[1:, :-1] |= m[:-1, 1:]; near[:-1, 1:] |= m[1:, :-1]; near[:-1, :-1] |= m[1:, 1:]
        grow = np.zeros(op.shape, bool)
        for y, x in zip(*np.nonzero(near & dark & ins & ~m)):
            if all(m[qy, qx] or dark[qy, qx] or air[qy, qx]
                   for qy in (y - 1, y, y + 1) for qx in (x - 1, x, x + 1)
                   if 0 <= qy < op.shape[0] and 0 <= qx < op.shape[1]):
                grow[y, x] = True
        if not grow.any():
            break
        m = m | grow
    return m


# heroes whose carried weapon crosses IN FRONT of the body: the squares behind it were never drawn, so once the body
# dips under the stamped-back weapon they showed as see-through slits (Lulu's staff over her robe, 2026-10-08: 「像素
# 缺失」). For them the lifted weapon's squares that lie inside the body are first filled with the body's own colour
# round them (fill_behind), then the body breathes.
CARRY_FILL |= {"lulu"}


def fill_behind(a, carried):
    """The lifted weapon's squares that lie inside the figure (drawn squares within 3 on both sides, across or up and
    down) take the most common non-outline colour among their drawn neighbours, a ring at a time."""
    a = a.copy()
    op = a[..., 3] > 0
    H, W = op.shape
    todo = {(int(y), int(x)) for y, x in zip(*np.nonzero(carried))}
    dark = lambda c: sum(c) < 120                                   # noqa: E731 - the outline
    for _ in range(8):
        done = []
        for y, x in sorted(todo):
            row, col = op[y], op[:, x]
            inside = ((row[max(0, x - 3):x].any() and row[x + 1:x + 4].any()) or
                      (col[max(0, y - 3):y].any() and col[y + 1:y + 4].any()))
            if not inside:
                continue
            cols = [tuple(int(v) for v in a[v_, u_, :3]) for v_ in (y - 1, y, y + 1) for u_ in (x - 1, x, x + 1)
                    if (v_, u_) != (y, x) and 0 <= v_ < H and 0 <= u_ < W and op[v_, u_]]
            body = [c for c in cols if not dark(c)]
            if len(body) >= 2:
                done.append((y, x, max(set(body), key=body.count)))
        if not done:
            break
        for y, x, c in done:
            a[y, x] = (*c, 255)
            op[y, x] = True
            todo.discard((y, x))
    return a


NO_NOD = {"kayn", "xinzhao"}   # with his scythe carried a cheap neck row turned up and his head began to nod; nobody else nods
    # the piece took his upper body
# hero: rows every frame moves down, but never past the soles row (SOLES under the pivot): a hero drawn floating
# who should stand on the ground. Nami floated 3 px like Janna, so in the collection grid (every hero's feet on one
# line) she sat high; the user: "整体下移 3 格、去掉浮空". Frames already on the ground stay (R's landing, her death).
SINK = {"nami": 3}
SOLES = 11
# (hero, tag): (y, slots) like BOB, for a neck drawn too long under the pasted head: in those slots everything at or
# above pivot row y moves down a row. Codex drew Nami's swimming body a row lower under the head in run 1-4 than
# in 5-8 and the design, so her neck stretched and shrank as she swam (the user: "一上一下的时候感觉身体要分离一样").
NECK = {("nami", "run"): (-21, [0, 1, 2, 3])}
# (hero, tag): (reference slot, {slot: (dx, dy)}, head box (row0, row1, col0, col1) from the EYES pixel) - the pasted
# head moved with the body: in the listed slots Codex drew the body (dx, dy) off the reference frame's while the head
# stayed put, so the head is moved by the same amount (its pixels: those of the box equal to the idle's head round
# the eye) and what it uncovers takes the reference frame's pixels at the same place on the body. Darius's run: the
# user, "原来的走路姿势是最好的 问题是头和身体不协调"; measured on the shoulders (best colour match against frame 8):
# frame 1's body 5 px further forward, frame 4's 3 px forward and a row lower, the others within a pixel.
HEAD_MOVE = {("darius", "run"): (7, {0: (5, 0), 3: (3, 1)}, (-9, 3, -8, 6))}
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
            "caitlyn", "nocturne", "blitzcrank", "camille", "leblanc", "kaisa", "sona", "kennen", "vi", "ryze", "jhin", "zilean",
            "aatrox", "kayn", "sivir", "twistedfate", "rakan", "evelynn", "sett", "lissandra", "varus", "alistar", "tryndamere",
            "xerath", "xinzhao", "samira", "pyke", "gwen", "khazix", "brand", "twitch", "renekton", "seraphine",
            "lillia", "viktor", "xayah", "lulu", "vladimir", "rengar", "kogmaw", "zed", "karma", "olaf", "hecarim",
            "draven", "senna", "shen"}
# hero: the luminance from which an edge pixel gets the outline (complete_outline's `dark`, default 70). Fiora's teal
# leggings (luminance ~58) and wine cape (~44) edge many action frames without black: tfm2_ase.py metrics counts only
# luminance < 40 as outline, so at 70 her Q frames read 83-89% (the bare rapier aside); at 40 they close too.
DARK = {"fiora": 40, "zed": 30}
# Zed (2026-10-10, 「模型说不出来的糊」): his blue steel, reds and dark red edge the silhouette; from 30 they get the
# outline too (design_zed2.DARK, rig_zed.DARK close it the same way), 98% of his edge black instead of 84%
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
# hero: rows over the soles whose own pinholes stay; every other pinhole (a clear pixel whose four neighbours are
# opaque), and one complete_outline made in those rows, gets the outline colour. Sona's design has one-pixel slits
# beside her cheeks: the completion closed their mouths and left a speck of ground on each side of the face in every
# frame, and her pasted arm (fix_sona_strips.py) left more between the hand, the shoulder and the hair. Her design's
# own pinholes, between the skirt panels and the legs, are 5-7 rows over the soles and stay
PLUG = {"sona": 9,
        # Jax: the idle's breathing seam (BOB, row 4) closes a notch at the near foot into a pinhole in slots 3-5;
        # every other hole in his frames is painted by tools/art/fix_jax_frames.py before the import
        "jax": 0,
        # Rakan: the completion closes 1-square slits between the cloak's feathers, the hands and the hair into
        # pinholes (23 in 15 frames); his design has none
        "rakan": 0}
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
         # and Caitlyn (the second design, design_caitlyn_v2.py: rig_caitlyn.py writes it into all six; her strips are
         # posed in display order, the shots from the hip held two slots as the first design's ORDER had them)
         ("caitlyn", "idle"): [0, 0, 0, 0, 0, 0],
         # and Nocturne (Codex's game-size design B cut to 40 rows: the pack's idle is the design in all six)
         ("nocturne", "idle"): [0, 0, 0, 0, 0, 0],
         # and Blitzcrank (Codex's game-size design B2, fixed by hand: the pack's idle is the design in all six)
         ("blitzcrank", "idle"): [0, 0, 0, 0, 0, 0],
         # and Camille (Codex's 65-row drawing cut to 46 rows, design C1: the pack's idle is the design in all six)
         ("camille", "idle"): [0, 0, 0, 0, 0, 0],
         # and LeBlanc (Codex's game-size design B cut to 43 rows: the pack's idle is the design in all six)
         ("leblanc", "idle"): [0, 0, 0, 0, 0, 0],
         # and Kai'Sa (Codex's chibi draft B cut to 44 rows, design_kaisa.py: the pack's idle is the design in all six)
         ("kaisa", "idle"): [0, 0, 0, 0, 0, 0],
         # and Sona (Codex's game-size design B, 40 rows: the pack's idle is the design in all six)
         ("sona", "idle"): [0, 0, 0, 0, 0, 0],
         # and Kennen (Codex's design A cut to 37 rows, design_kennen.py: the pack's idle is the design in all six)
         ("kennen", "idle"): [0, 0, 0, 0, 0, 0],
         # and Vi (the approved guard master read onto 40 rows, design_vi.py: strips_vi.py writes the design in all six)
         ("vi", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ryze (Codex's image-model draft A cut to 40 rows: the pack's idle is the design in all six)
         ("ryze", "idle"): [0, 0, 0, 0, 0, 0],
         # and Jhin (Codex's raw draft A cut to 41 rows, design_jhin.py: the pack's idle is the design in all six)
         ("jhin", "idle"): [0, 0, 0, 0, 0, 0],
         # and Zilean (Codex's image-model draft A_draft_02 cut to 40 rows: the pack's idle is the design in all six)
         ("zilean", "idle"): [0, 0, 0, 0, 0, 0],
         # and Aatrox (Codex's slim draft sampled to 40 rows, design_aatrox.py): rig_aatrox.py writes the design in all
         # six, its breath drawn in 3-5 (BREATH, instead of a BOB seam), so the six play in order
         ("aatrox", "idle"): [0, 1, 2, 3, 4, 5],
         # and Kayn (his draft read back at 40 rows, design_kayn.py: the pack's idle is the design in all six)
         ("kayn", "idle"): [0, 0, 0, 0, 0, 0],
         # and Sivir (Codex's second-round draft 2 read back and cut to 40 rows, design_sivir.py: the idle is the design)
         ("sivir", "idle"): [0, 0, 0, 0, 0, 0],
         # and Rakan (Codex's draft read back and cut to 40 rows, design_rakan.py: the idle is the design in all six)
         ("rakan", "idle"): [0, 0, 0, 0, 0, 0],
         # and Evelynn (Codex's draft A halved to 41 rows, design_evelynn.py: the idle is the design in all six)
         ("evelynn", "idle"): [0, 0, 0, 0, 0, 0],
         # and Sett (Codex's raw draft B read onto 42 rows, design_sett.py; strips_sett.py writes the design six times)
         ("sett", "idle"): [0, 0, 0, 0, 0, 0],
         # and Lissandra (Codex's skin swap B read back by cell majority, design_lissandra.py; rig_lissandra.py writes
         # the design six times)
         ("lissandra", "idle"): [0, 0, 0, 0, 0, 0],
         # and Varus (Codex's draft A area-voted to 40 rows, design_varus.py; rig_varus.py writes the design six times)
         ("varus", "idle"): [0, 0, 0, 0, 0, 0],
         # and Alistar (Codex's draft A halved to 44 rows, design_alistar.py: the idle is the design in all six)
         ("alistar", "idle"): [0, 0, 0, 0, 0, 0],
         # and Tryndamere (Codex's A_retry cut to 40 rows by whole lines, design_tryndamere.py; rig_tryndamere.py
         # writes the design six times)
         ("tryndamere", "idle"): [0, 0, 0, 0, 0, 0],
         # and Xerath (Codex's draft B cut to 44 rows by whole lines, design_xerath.py; Codex's step 2 writes the design
         # six times)
         ("xerath", "idle"): [0, 0, 0, 0, 0, 0],
         # and Xin Zhao (Codex's draft 03 cut to 42 rows by whole lines, design_xinzhao.py; rig_xinzhao.py writes the
         # design with its rebuilt straight spear six times)
         ("xinzhao", "idle"): [0, 0, 0, 0, 0, 0],
         # and Samira (Codex's draft A cut to 40 rows by whole lines, design_samira.py; rig_samira.py writes the design
         # six times - no breathing seam: her greatsword hangs to the soles beside the far boot, a seam would cut it)
         ("samira", "idle"): [0, 0, 0, 0, 0, 0],
         # and Pyke (Codex's draft A-second cut to 40 rows by whole lines, design_pyke.py; rig_pyke.py writes the design
         # six times)
         ("pyke", "idle"): [0, 0, 0, 0, 0, 0],
         # and Gwen (Codex's draft bd82 traced to 44 rows, design_gwen.py; rig_gwen.py writes the design with its breath
         # in 3-4 - the upper body and the scissors a row lower - so the six play in order, as Aatrox's)
         ("gwen", "idle"): [0, 1, 2, 3, 4, 5],
         # and Kha'Zix (Codex's own design A, the user's pick; fix_khazix_strips.py copies its idle of six designs)
         ("khazix", "idle"): [0, 0, 0, 0, 0, 0],
         # Brand (Codex's raw draft A cut to 37 rows by whole lines, design_brand.py; rig_brand.py writes the design
         # with its flames flickering through three states, so the six play in order)
         ("brand", "idle"): [0, 1, 2, 3, 4, 5],
         # Twitch (Codex's raw draft B cut to 38 rows, design_twitch.py; fix_twitch_strips.py keeps Codex's idle of six
         # designs)
         ("twitch", "idle"): [0, 0, 0, 0, 0, 0],
         # Renekton (Codex's raw draft B read back on its grid, the blade-and-tail columns cut to 65 x 41,
         # design_renekton.py; Codex's idle is the design six times)
         ("renekton", "idle"): [0, 0, 0, 0, 0, 0],
         # Seraphine (Codex's design_1 cut region by region to 52 rows, design_seraphine.py; rig_seraphine.py writes the
         # design six times, the back hair's tips streaming a square further in 3-4, so the six play in order)
         ("seraphine", "idle"): [0, 1, 2, 3, 4, 5],
         # Lillia (design_lillia.py step 10; rig_lillia.py writes the design six times, BOB breathes it)
         ("lillia", "idle"): [0, 0, 0, 0, 0, 0],

         # Viktor (Codex's design B, the staff straightened, design_viktor.py): fix_viktor_stand.py writes his breath, 8
         ("viktor", "idle"): [0, 1, 2, 3, 4, 5, 6, 7],
         # Lulu (Codex's design version 2 + the user's round face C3; the pack's idle is the design six times)
         ("lulu", "idle"): [0, 0, 0, 0, 0, 0]}
# (hero, tag): (y, slots) - in those slots everything at or above pivot row y moves down a row (the row under
# it is covered): one frame breathing, the face the same drawing throughout. Leona's shield covers her from
# the chest to the ankles, so she sinks down to its tip and only the boots stay (a seam across the shield
# would cut it in two).
BOB = {("yasuo", "idle"): (-2, [2, 3, 4]),
       # Lillia: the girl above her waist (and the bough's top, the lantern, the deer's raised tail) sinks a row onto
       # the leaf skirt; the deer and its legs stay
       ("lillia", "idle"): (-5, [2, 3, 4]),
       # Lissandra has no legs: everything down to the gown's straight part sinks, the crystal hem (rows 92-99) stays
       ("lissandra", "idle"): (3, [2, 3, 4]),
       # Xerath floats on two pointed legs: all of him down to the lower leg plates sinks a row, the tips stay
       ("xerath", "idle"): (8, [2, 3, 4]),
       # Pyke crouches: the seam across the tops of his boots (row 93), the boots stay
       ("pyke", "idle"): (5, [2, 3, 4]),
       # Kha'Zix crouches on insect legs: the seam across his shins (row 94), the toe claws stay
       ("khazix", "idle"): (6, [2, 3, 4]),
       # Brand's wide crouch: the seam across his bare shins under the trousers' torn hems (row 95), the feet stay
       ("brand", "idle"): (7, [2, 3, 4]),
       # Twitch: the seam under his coat's hem (row 95); the rat feet and their claws stay
       ("twitch", "idle"): (7, [2, 3, 4]),
       # Alistar: the seam in his furry shins (row 92); the hooves and the fur round them stay
       ("alistar", "idle"): (4, [2, 3, 4]),
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
       # Camille: the seam halfway down her leg blades (rows 93/94: the same silhouette, 3 squares of colour differ);
       # the blades' lower halves stay on the ground
       ("camille", "idle"): (5, [2, 3, 4]),
       # LeBlanc: her gown's diagonal trims change every row (13-18 squares from one row to the next); the seam runs
       # through the hem over her heels (rows 97/98 of the design), the staff's straight shaft one row shorter
       ("leblanc", "idle"): (9, [2, 3, 4]),
       # Kai'Sa: the seam low in her shin plates (rows 6/7 under the pivot: 2 squares of opacity and 4 of colour differ);
       # the clawed boots stay
       ("kaisa", "idle"): (6, [2, 3, 4]),
       # Sona: her skirt's panels run straight down; the seam in rows 94/95 of the design (the same width, 7 squares of
       # the outline move); the hem and the panels' lower ends stay on the ground
       ("sona", "idle"): (6, [2, 3, 4]),
       # Kennen: the seam low in the robe (rows 94/95 of the design: 2 squares of opacity and 9 of colour differ); his
       # shoes and the hem's last row stay
       ("kennen", "idle"): (6, [2, 3, 4]),
       # Vi: the seam across her shins (row 92 of the design, 4 under the pivot: both legs there are thin slanted
       # strokes, the near gauntlet's lowest row is 85), so her guard sinks a row and only the boots stay
       ("vi", "idle"): (4, [2, 3, 4]),
       # Ryze (second design, tools/art/design_ryze_v2.py): the seam in the boot shafts, rows 7/8 under the pivot (one
       # square differs); his hands hang to the belt
       ("ryze", "idle"): (7, [2, 3, 4]),
       # Jhin: the cane and Whisper reach the ground, so a seam in the legs cut them - at the knees the cane's bands
       # and Whisper's slanted barrel stepped a row each breath (the user: 「上下摆动导致模型变形 盖伦就没这问题」); the
       # seam under his shoulders that followed (the user's pick A of four) squeezed his arms and cape a row (「烬是模型
       # 上下摆动导致有点微小的变形」, 2026-10-04). Now Garen's way: the seam low in the boots (pivot rows 9/10: 1 square
       # of opacity and 3 of colour differ, the fewest under the hips), the soles stay, and the cane and Whisper go down
       # with his hands whole (BOB_CARRY)
       ("jhin", "idle"): (9, [2, 3, 4]),
       # Zilean floats: the seam low in the robe under the clock's pendulum (rows 94/95 of the design: the same width,
       # 11 squares of colour differ); the hem and his dangling feet stay
       ("zilean", "idle"): (6, [2, 3, 4]),
       # Kayn: Rhaast's crescent hangs to the soles on his left and its butt spike to his right, so a seam in the legs
       # cuts the blade's curve; across the soles (rows 97/98 of the design: 6 squares of opacity and 5 of colour differ,
       # the fewest under the hips) all of him and the scythe sink a row, only the soles' row stays
       ("kayn", "idle"): (9, [2, 3, 4]),
       # Rakan: his feather cloak trails to the ground on his left, so every seam over the soles cuts its slanted edge
       # (4-8 squares of opacity); the seam under the knees' red bands (rows 71/72 of the cell: 4 squares of opacity
       # and 9 of colour differ) keeps the bands whole, the boots lose their top row while he breathes
       ("rakan", "idle"): (7, [2, 3, 4])}
# (hero, tag): column ranges from the pivot (None: to the edge) that a BOB moves down whole, under its seam too - props
# held in the hands that reach the ground, apart from the legs below the seam. Jhin: the cane left of his legs (pivot
# columns -11 and less), Whisper's barrel right of them (+6 and more; the right sole ends at +5)
BOB_CARRY = {("jhin", "idle"): ((None, -11), (6, None))}
# (Aatrox had (8, [2, 3, 4]): his greatsword hangs to five rows over the soles, so every row seam over the boots cuts the
# blade, and the seam across the boots (rows 96/97) cut their middle row 97 out - both boots squashed and their lights
# blinked each breath (the frame audit, 2026-10-04). rig_aatrox.py now draws the breath in idle 3-5 with a seam per
# part - the blade whole, each leg losing one of its two equal shin rows - and ORDER plays the six.)
# Sivir does not breathe: the seam under her scarf cut the crossblade and the near shoulder every breath and the
# ban/pick card shook (the user: 「BP界面还是会上下摇动」); of a seam in the boots or none, the user picked none
# hero: a module in tools/art with tidy(tag, k, frame) -> frame, run on the finished frames (after the outline is closed
# and cleaned): the user's clean-up of dirty black blocks and stray squares inside the silhouette (2026-10-02:
# "盖伦把黑边清理干净 有杂的黑色的地方", "风女 莫甘娜 不干净的黑色块也太多了", "莫甘娜头部有很多多余的方块", "阿狸也是都给我清理干净")
TIDY = {"ahri": "clean_ahri", "janna": "clean_janna", "morgana": "clean_morgana",
        "xerath": "clean_xerath", "gwen": "clean_gwen"}   # gwen: heart-hole marker -> transparent (clean_gwen); 「顺便把泽拉斯脚上的黑边清理干净」: bare outline stalks under his leg tips
# heroes made smaller from their finished frames: whole rows and columns out, never resampled (shrink_frames.py); the idle
# before it breathes. A hero whose strips a rig builds from the design shrinks the design there instead (rig_xinzhao.py
# SCALE: cut from finished frames a diagonal spear's 1:2 shaft got uneven steps); SHRINK_KEEP: skin colours (hands)
# no line may cross, "!RRGGBB+up,down,left,right" a box no line may cross
SHRINK = {"senna": 0.85, "xerath": 0.9, "renekton": 0.9, "twitch": 0.85, "karma": 0.95}      # players (2026-10-08): 「泽拉斯 ... 体型偏大」「鳄鱼体型也偏大了」; karma: 「卡尔玛体型可以变小一点」 -> 90%, then 「缩小模型后有点奇怪了啊整体」: the head is cut in fix_karma_strips.py (HEAD_CUT, the same in every frame) and only two body rows go here (0.95, the head box and the boots kept)
# senna (2026-10-10): 「模型太大了 能缩小点吗」 -> 85% of the options (90 / 85; 46 -> 39 rows claws to soles), her face and
# head the same squares in every frame (SHRINK_HEAD), the boots whole
# no line through Xerath's face (his eyes' white-hot core) or Renekton's (his yellow eyes to his red jaw)
# "=RRGGBB": no row through a square of that colour (Renekton's blue knee guards: a row through them halved the guard
# and shifted his leg's stripes - 「这里是像素缺失吗」「在左脚啊」); not in his death, where the lying body's blue made
# every low row "knee" and the cut fell on his head
SHRINK_KEEP = {"senna": ["!77E3B3+12,5,11,11", "B46C47", "8F4C36"], "olaf": ["!0455A6+13,6,11,11"], "karma": ["!1BB663+1,9,16,10", "=222048", "C4815A", "825238"], "xerath": ["!FBFCFC"], "twitch": ["#FBFDF7", "!F94714+3,0,1,1"], "renekton": ["!F9D206+2,1,2,2", "!A8161F", "=0218B2", "=010E84"]}
SHRINK_KEEP_TAG = {"karma": {"dead": ["!1BB663+3,9,16,10", "=222048", "C4815A", "825238"]}, "renekton": {"dead": ["!F9D206+2,1,2,2", "!A8161F"]}}
# the lines follow the body from frame to frame, anchored on a colour only one feature has: cut at fixed canvas lines,
# a cast or an attack that moves him took different lines of him in each frame - 「缩小后放技能的时候模型有点变形」
# 「攻击时候也是」
SHRINK_ANCHOR = {"senna": "77E3B3", "olaf": "0455A6", "karma": "1BB663", "xerath": "FBFCFC", "twitch": "FBFDF7", "renekton": "F9D206"}
# actions whose body stands still while something over it floats: their lines are taken at the same place in every frame
# (shrink_frames' still) - Karma's ring bobs in her idle and carries a square of the anchor's gem green, so the anchor
# moved with it and her legs lost a row one higher in frames 3-4 (「待机动画效果的时候腿部变形啊」)
SHRINK_STILL = {"karma": ["idle"]}
# shrink_frames' ground: the rows under this one (from the pivot) follow the ground, not the anchor - Senna's head bobs
# 6 rows in her run and 9 in her attack's lunge, and leg rows taken at the head's offset fell under her soles (a row or
# two below the feet line in 9 frames)
SHRINK_GROUND = {"senna": 0}
# actions whose frames are planned in groups, each group's counts from its own first frame's size, not the idle's:
# Senna's death crumples to 31-37 rows against the idle's 46, and the idle's 7 rows out of it squashed her hood and
# cut her far boot off (dead 2: two pieces); the kneel she holds (frames 3-6) is one group, so it stays one shape
SHRINK_GROUPS = {"senna": {"dead": [[0], [1], [2, 3, 4, 5]]}}
# a head drawn the same on every frame loses the same lines in every action (shrink_frames.head_lines; window and keep
# from the top-left square of the hero's SHRINK_ANCHOR colour, rows / (left, right) columns to take) - cut by each
# action's own plan, Senna's hood lost other rows in each action and would change shape at every animation change;
# her whole head is in SHRINK_KEEP, so no other line crosses it
SHRINK_HEAD = {"senna": {"window": (-12, 6, -11, 18), "keep": (-4, 6, -4, 10), "rows": 2, "cols": (1, 1)}}
# rows (from the pivot) no action loses: Senna's stamped boots are three rows, the soles' two are kept anyway
SHRINK_KEEP_ROWS = {"senna": (9,)}
# heroes whose anchor colour marks a feature drawn the same in every frame: shifts from its corner square
# (shrink_frames.anchor_shifts robust) - Senna's eyes move 13 columns between two frames of her ult
SHRINK_ROBUST = {"senna"}
# single actions made smaller (the idle untouched), {hero: {scale: [tags]}}, with SHRINK_KEEP / SHRINK_ANCHOR as above:
# Olaf's idle is the slim design B, and Codex's redraw of his R, E and death kept bulkier bodies (area 1.2-1.7x the
# idle's) - after 「奥拉夫跑动时为什么变大一圈 好违和」 the user picked 「一起改」 (every action at the idle's size); his hit
# is the slim strips' (Codex's size redraw drew it thin: fix_olaf_strips TAG_SRC), eyes 33-39 rows over the soles
# against the idle's 28
SHRINK_TAGS = {"olaf": {0.85: ["ult", "dead"], 0.9: ["skill2"], 0.8: ["hit"]}}
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
        "morgana": (0x8A, 0x4F, 0xE0),    # the redesign A: only her face is pasted; the eyes' deep violet (fix_morgana_eyes.py,
                                          # each eye's inner square: the old pink's columns and first square in every frame)
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
        "camille": (2, 159, 217),         # her raised blade tops the kicks; the far eye was recoloured to this cyan
        "leblanc": (122, 0, 18),          # her staff's crystal or diadem tops the frames; the dark red is her near pupil's
        "kaisa": (0x8B, 0x17, 0xB2),      # the near iris of the 42-row design (tools/art/design_kaisa_v2.py): only in her eyes
        "sona": (34, 201, 184),           # her twin tails top the frames (the Etwahl in R); the teal is only in her irises
        "kennen": (63, 174, 248),         # the shuriken on his back tops every frame; the blue is only in his eyes
        "vi": (0, 108, 251),              # a raised gauntlet tops the E, R and uppercut frames; this blue is only her near
                                          # iris's top square (design_vi.py; the crystals use the other blues)
        "ryze": (251, 251, 253),          # the scroll or a raised hand tops the frames; the white is only in his eyes
        "jhin": (255, 110, 180),          # Whisper or the cannon tops the flourishes; the pink is only in his eyes
        "zilean": (246, 249, 250),        # the clock's roof tops every frame; this white is only in his eyes
        "kayn": (233, 173, 55),           # Rhaast or the spiky hair tops the frames; the gold is only his near eye's
        "sivir": (0x4F, 0xE6, 0xD2),      # the crossblade tops the raised frames; the mint is only in her eyes
        "twistedfate": (0x7A, 0xF4, 0xFF),   # the hat's brim tops every frame; the cyan is only in his one eye
        "evelynn": (0xFF, 0xD2, 0x1E),       # her hair or a raised lasher tops the frames; the yellow is only her eyes
        "sett": (0xC8, 0x70, 0x0A),       # his ears or a raised fist top the frames; the amber is only in his eyes
        "alistar": (0xFB, 0x12, 0x0D)}    # his mane, horns or raised fists top the frames; the red is only his eyes


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


# Form sheets: a hero's whole sheet again with the bodies the game plays by name (idle, run, hit, dead) taken from
# <hero>_<prefix><tag>.png. Kayn's full transform (addons/league_kayn_form) renames his view to league_kayd /
# league_kays, sent to these sheets; tools/art/rig_kayn_forms.py poses the bodies from the form designs' parts and
# outlines them (its death dissolves in a dither: no outline pass here, nor any other touch - the frames go in as drawn,
# centred on their pivots). Every other tag is the hero's own frames, as finished for his sheet.
FORM_SHEETS = {"kayn": {"kayn_darkin": "rh_", "kayn_shadow": "sh_"}}
FORM_BODY = ("idle", "run", "hit", "dead")
# the base actions the hero already has a form strip for (rh_attack ...): in a form sheet the base tag plays the form's
# frames too - the data plays "attack" on the action's first tick before its form switch picks "rh_attack", and in game
# the user saw that tick as the base Kayn (「攻击的时候还是会变回去」)
FORM_ACTIONS = ("attack", "skill", "skill2", "ult_exit")
FORM_REVERSED = {"ult": "ult_exit", "ult_fx1": "ult_exit"}
# the body animations the kit plays by CasterAnimation with no form strip of their own, drawn from the form's: the
# transformation (played from the form's sheet - the form buff is on by then - it showed the base Kayn for 36 ticks
# right after he turned) shows the form standing, the tf flash over it; the base W (skill2_fx1, played when no form
# buff is on) the form's W, spread over its timings: 「一帧变身后 又释放技能的时候突然变回去」
FORM_RETIMED = {"transform": "idle", "skill2_fx1": "skill2"}


# In-wall sheets: every frame of the hero's (and each form's) sheet as a see-through shadow - the Shadow Step through a
# wall (addons/league_kayn_form: the view's name ends in w / r / h while he stands in a wall cell). League shows Kayn
# inside terrain as a dark shadow only; the user: 「穿墙的效果要模仿LOL里面」. The outline stays, the body takes the
# smoke violets by its brightness with every other inside pixel left out (a checker), bright saturated pixels (his eyes,
# the scythe's eye) glow crimson.
WALL_SHEETS = {"kayn": "kayn_wall", "kayn_darkin": "kayn_darkin_wall", "kayn_shadow": "kayn_shadow_wall"}
WALL_SMOKE = [(0x2C, 0x22, 0x50), (0x46, 0x3A, 0x74), (0x6A, 0x5C, 0x9E), (0x9A, 0x8E, 0xC8)]
WALL_GLOW = (0xFF, 0x40, 0x58)


# Game 0.6.3: the add-on (addons/league_kayn_form, view.rs) swaps the playing animation's NAME, as the game's own
# demon does (run -> archfiend_run, both in the demon's sheet) - so the forms' bodies and the in-wall shadows also go
# into the hero's own sheet under a prefix: rh_idle / sh_idle ..., w_run / rw_run / hw_run ... (the separate form and
# wall sheets above stay for the 0.6.2 name swap).
FORM_INTO_BASE = FORM_BODY + tuple(FORM_REVERSED) + tuple(FORM_RETIMED)
WALL_PREFIX = {"kayn": "w_", "kayn_darkin": "rw_", "kayn_shadow": "hw_"}
WALL_INTO_BASE = ("idle", "run", "hit", "skill")


def shadow_frame(a):
    """One frame as the see-through in-wall shadow."""
    out = np.zeros_like(a)
    op = a[..., 3] > 0
    if not op.any():
        return out
    rgb = a[..., :3].astype(np.int32)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    keep = op & (edge | ((xs + ys) % 2 == 0))
    shade = np.clip((lum / 255.0 * len(WALL_SMOKE)).astype(int), 0, len(WALL_SMOKE) - 1)
    out[keep, :3] = np.array(WALL_SMOKE, np.uint8)[shade[keep]]
    dark = op & (lum < 40)
    out[dark & keep, :3] = a[dark & keep, :3]            # the outline as it was
    glow = op & (sat > 0.55) & (mx > 200)
    out[glow, :3] = WALL_GLOW
    out[keep | glow, 3] = 255
    return out


def wall_sheet(sheet):
    return {tag: [(shadow_frame(a), ms) for a, ms in frames] for tag, frames in sheet.items()}


def form_sheets(hero, sheet):
    """{form sheet name: sheet} for a hero with form bodies (FORM_SHEETS) whose strips are all there."""
    out = {}
    if hero not in FORM_SHEETS:
        return out
    with open(os.path.join(SRC, f"{hero}_cells.json"), encoding="utf-8") as f:
        spec = json.load(f)
    table, cell = spec["tags"], tuple(spec.get("cell", CELL))
    for name, prefix in FORM_SHEETS[hero].items():
        if not all(os.path.exists(os.path.join(SRC, f"{hero}_{prefix}{t}.png")) for t in FORM_BODY):
            continue
        fs = dict(sheet)
        for tag in FORM_BODY:
            rows = table[tag]
            fr = cells(hero, prefix + tag, len(rows), cell)
            fs[tag] = [(G.centre_frame(fr[k], -rows[k]["pivot"][0], -rows[k]["pivot"][1]), rows[k]["ms"])
                       for k in range(len(rows))]
        for tag in FORM_ACTIONS:
            if prefix + tag in sheet:
                fs[tag] = sheet[prefix + tag]
        # R's dive into the host has no form strip: the form's own exit played backwards (out of the host, reversed,
        # is into it), as many frames as the dive, on the dive's timings - else every R showed the base Kayn for a
        # moment (「变身后还有一定几率变回去」)
        for tag, src in FORM_REVERSED.items():
            if prefix + src in sheet and tag in sheet:
                back = [a for a, _ in reversed(sheet[prefix + src])]
                fs[tag] = [(back[k % len(back)], ms) for k, (_, ms) in enumerate(sheet[tag])]
        for tag, src in FORM_RETIMED.items():
            if tag in sheet and src in fs:
                pics, n = [a for a, _ in fs[src]], len(sheet[tag])
                fs[tag] = [(pics[k * len(pics) // n], ms) for k, (_, ms) in enumerate(sheet[tag])]
        out[name] = fs
    return out


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
        if tag in STEADY and (hero, tag) not in UNSTEADY and sure:
            target = round(sum(sure) / len(sure))
            dx = [0 if h is None else target - h for h in hx]
        order = ORDER.get((hero, tag), range(len(fr)))
        sheet[tag] = [(G.centre_frame(fr[k], dx[k] - rows[k]["pivot"][0], sunk(hero, fr[k], rows[k]["pivot"][1])),
                       rows[slot]["ms"]) for slot, k in enumerate(order)]
        report[tag] = [(None if hx[k] is None else hx[k] + dx[k], dx[k]) for k in order]
        if tag == "idle" and rows[order[0]].get("head"):         # the head point in idle slot 1's centred frame
            k, a = order[0], sheet[tag][0][0]
            u0, r0 = dx[k] - rows[k]["pivot"][0], sunk(hero, fr[k], rows[k]["pivot"][1])
            HEAD_AT[hero] = (a.shape[1] // 2 + rows[k]["head"][0] + u0, a.shape[0] // 2 + rows[k]["head"][1] + r0)
    return sheet, report


HEAD_AT = {}
SHRUNK = {}


def breathe_idle(hero, sheet):
    """idle_breathe.py: the idle becomes 8 frames of the design breathing (feet still, the body down 2 rows through
    the thighs and back, leaning a column, the head a frame late), drawn from idle slot 1 after every other step. The
    head point: the eye-only colour (EYES), else the cells' head point, else the middle of the top rows. Returns the
    rows used, or None."""
    if hero in BREATHE_SKIP or "idle" not in sheet:
        return None
    a = sheet["idle"][0][0]
    e = eye_at(hero, a) if hero in EYES else None
    if e is not None:
        head = (e[1] + 1.0, float(e[0]))
    elif hero in HEAD_AT:
        head = HEAD_AT[hero]
    else:
        ys, xs = np.nonzero(a[..., 3])
        head = (float(np.median(xs[ys < ys.min() + 8])), float(ys.min() + 7))
    carried = None
    if hero in WEAPON_CARRY:
        carried = np.zeros(a.shape[:2], bool)
        for colours, box in WEAPON_CARRY[hero]:
            carried |= weapon_mask(a, colours, box)
        a = a.copy()
        a[carried] = 0
        if hero in CARRY_FILL:
            a = fill_behind(a, carried)
    opts = BREATHE_OPTS.get(hero, {})
    frames, rows = IB.breathe(a, head, nod=hero not in NO_NOD, **opts)
    if carried is not None:
        src = sheet["idle"][0][0]
        cy, cx = np.nonzero(carried)
        body, sway = opts.get("body", IB.BODY), opts.get("sway", IB.SWAY)
        near = carried.copy()                                     # within 2 squares of the weapon
        for _ in range(2):
            g = near.copy()
            g[1:] |= near[:-1]; g[:-1] |= near[1:]; g[:, 1:] |= near[:, :-1]; g[:, :-1] |= near[:, 1:]
            near = g
        for k, f in enumerate(frames):
            f[cy + 2 + body[k], cx + 2 + sway[k]] = src[cy, cx]   # breathe pads its frames by 2 all round
            # a weapon moved off the standing legs (league_darius's axe head beside his shin) leaves see-through
            # squares shut in between them: the design's own squares there fill them (its own holes stay); only for
            # CARRY_FILL - the approved heroes keep their frames as they are
            for y, x in (shut_in(f[..., 3] > 0) if hero in CARRY_FILL else []):
                sy, sx = y - 2 - body[k], x - 2 - sway[k]
                if (0 <= sy < src.shape[0] and 0 <= sx < src.shape[1] and near[sy, sx]
                        and 0 <= y - 2 < src.shape[0] and 0 <= x - 2 < src.shape[1] and src[y - 2, x - 2, 3]):
                    f[y, x] = src[y - 2, x - 2]
        rows["carried"] = int(carried.sum())
    if os.environ.get("IDLE_DEBUG"):                     # the frames, for review sheets
        np.save(os.path.join(os.environ["IDLE_DEBUG"], f"{hero}.npy"), np.stack(frames))
    sheet["idle"] = [(f, IB.MS) for f in frames]
    return rows


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
    frame before it moves); BOB_CARRY's columns go down whole, under the seam too."""
    for (h, tag), (y0, slots) in list(BOB.items()) + list(NECK.items()):
        if h != hero or tag not in sheet:
            continue
        for k in slots:
            a, ms = sheet[tag][k]
            cut = a.shape[0] // 2 + y0 + 1           # array rows before `cut` sit at pivot rows <= y0
            b = a.copy()
            b[1:cut + 1] = a[0:cut]
            b[0] = 0
            if (h, tag) in BOB and (h, tag) in BOB_CARRY:
                pc = a.shape[1] // 2
                for lo, hi in BOB_CARRY[(h, tag)]:
                    c0 = 0 if lo is None else max(0, pc + lo)
                    c1 = a.shape[1] if hi is None else min(a.shape[1], pc + hi + 1)
                    b[1:, c0:c1] = a[:-1, c0:c1]
                    b[0, c0:c1] = 0
            sheet[tag][k] = (b, ms)


def canvas(arrs):
    """Frames centred on their pivots padded to one size: (arrays, centre row, centre column)."""
    hh = max(a.shape[0] // 2 for a in arrs)
    hw = max(a.shape[1] // 2 for a in arrs)
    return ([np.pad(a, ((hh - a.shape[0] // 2,) * 2, (hw - a.shape[1] // 2,) * 2, (0, 0))) for a in arrs],
            hh, hw)


def eye_at(hero, a):
    """(row, column) of the EYES colour's first pixel (top row, left column), or None (turned away, lying down)."""
    ys, xs = np.nonzero((a[..., :3] == np.array(EYES[hero], np.uint8)).all(-1) & (a[..., 3] > 0))
    return (int(ys.min()), int(xs[ys == ys.min()].min())) if len(ys) else None


def head_move(hero, sheet):
    """HEAD_MOVE: the head moved with the body in the listed slots; {tag: slots moved}."""
    done = {}
    for (h, tag), (ref, moves, (r0, r1, c0, c1)) in HEAD_MOVE.items():
        if h != hero or tag not in sheet:
            continue
        idle = sheet["idle"][0][0]
        ie = eye_at(hero, idle)
        arrs, cy, cx = canvas([np.pad(a, ((4, 4), (8, 8), (0, 0))) for a, _ in sheet[tag]])
        for k, (dx, dy) in moves.items():
            a = arrs[k]
            e = eye_at(hero, a)
            m = np.zeros(a.shape[:2], bool)
            for y in range(r0, r1 + 1):
                for x in range(c0, c1 + 1):
                    p, q = idle[ie[0] + y, ie[1] + x], a[e[0] + y, e[1] + x]
                    if p[3] and q[3] and (p == q).all():
                        m[e[0] + y, e[1] + x] = True
            ys, xs = np.nonzero(m)
            new = np.zeros_like(m)
            new[ys + dy, xs + dx] = True
            b = a.copy()
            for y, x in zip(*np.nonzero(m & ~new)):    # uncovered: the reference body at the same place on the body
                b[y, x] = arrs[ref][y - dy, x - dx]
            b[ys + dy, xs + dx] = a[ys, xs]
            sheet[tag][k] = (G.centre_frame(b, -cx, -cy), sheet[tag][k][1])
        done[tag] = sorted(moves)
    return done


def tidy_frames(hero, sheet, step="tidy"):
    """TIDY: the hero's own clean-up module on every finished frame (its function `step`); the pixels it changed."""
    if hero not in TIDY:
        return 0
    mod = importlib.import_module(TIDY[hero])
    if not hasattr(mod, step):
        return 0
    n = 0
    for tag, frames in sheet.items():
        for k, (a, ms) in enumerate(frames):
            p = np.pad(a, ((6, 6), (6, 6), (0, 0)))      # room round the frame (Morgana's pasted head template)
            b = getattr(mod, step)(tag, k, p.copy())
            n += int((b != p).any(-1).sum())
            frames[k] = (G.centre_frame(b, -(b.shape[1] // 2), -(b.shape[0] // 2)), ms)
    return n


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
            if not a[..., 3].any():                               # an empty frame (Kayn's r_hidden: R inside a foe)
                continue
            b = np.pad(a, ((1, 1), (1, 1), (0, 0)))              # room for an outline round the widest pixel
            c = b.shape[0] // 2
            low = int(np.nonzero(b[..., 3].any(1))[0].max())
            before = b
            b, n, d = G.complete_outline(b, color=colour, dark=DARK.get(hero, 70), feet=max(c + SOLES, low))
            if hero in PLUG:
                op = b[..., 3] > 0
                p, q = np.pad(op, 1), np.pad(op & (before[..., 3] == 0), 1)
                hole = ~op & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
                made = q[:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, :-2] | q[1:-1, 2:]     # next to a completion pixel
                hole[c + SOLES - PLUG[hero]:] &= made[c + SOLES - PLUG[hero]:]
                b = b.copy()
                b[hole] = (*colour, 255)
                tidy["plug"] = tidy.get("plug", 0) + int(hole.sum())
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


def slice_ms(frames, start, length=None):
    """The frames from `start` ms on (the first one shortened); with `length`, `length` ms of them, the tag looping
    (a CasterAnimation held longer than its tag plays it again: league_garen's spin)."""
    total = sum(ms for _, ms in frames)
    length = total - start if length is None else length
    out, t, end = [], 0, start + length
    while t < end:
        for a, ms in frames:
            lo, hi = max(t, start), min(t + ms, end)
            if hi > lo:
                out.append((a, hi - lo))
            t += ms
    return out


def overlay(frames, pic, t0, under=False):
    """frames with the picture's frames drawn over (or under) them from t0 ms on, both centred on the pivot; the
    frames are cut where a picture frame starts or ends (none past the last frame's end) and padded to one canvas,
    then the empty margin trimmed equally on both sides."""
    arrs, hh, hw = canvas([a for a, _ in frames] + [a for a, _ in pic])
    body = arrs[:len(frames)]
    total = sum(ms for _, ms in frames)
    cuts, t = {0, total}, 0
    for _, ms in frames:
        t += ms
        cuts.add(t)
    t = t0
    for _, ms in pic:
        cuts.add(t)
        t += ms
    cuts.add(t)
    cuts = sorted(c for c in cuts if 0 <= c <= total)

    def at(seq, t, t0=0):
        for k, (_, ms) in enumerate(seq):
            if t0 <= t < t0 + ms:
                return k
            t0 += ms
        return None
    out = []
    for a, b in zip(cuts, cuts[1:]):
        img = Image.fromarray(body[at(frames, a)])
        j = at(pic, a, t0)
        if j is not None:
            p = pic[j][0]
            top = Image.fromarray(np.pad(p, ((hh - p.shape[0] // 2,) * 2, (hw - p.shape[1] // 2,) * 2, (0, 0))))
            img = Image.alpha_composite(top, img) if under else Image.alpha_composite(img, top)
        out.append((np.asarray(img), b - a))
    al = np.max([a[..., 3] for a, _ in out], 0)
    ys, xs = np.nonzero(al)
    my = min(int(ys.min()), al.shape[0] - 1 - int(ys.max()))
    mx = min(int(xs.min()), al.shape[1] - 1 - int(xs.max()))
    return [(a[my:a.shape[0] - my, mx:a.shape[1] - mx], ms) for a, ms in out]


def offset(a, dx, dy):
    """The picture a moved dx columns right and dy rows down from the pivot it is centred on (padded on the far side)."""
    if not dx and not dy:
        return a
    return np.pad(a, ((2 * max(dy, 0), 2 * max(-dy, 0)), (2 * max(dx, 0), 2 * max(-dx, 0)), (0, 0)))


def bake(hero, sheet):
    """Apply <hero>_bake.json: draw effect pictures into the hero's own action frames. The client never mirrors a
    data effect picture (ViewEffect, CasterViewEffect: game_view's generate copies the view system's flip, which
    register_data_champion_views sets to false), but it mirrors the hero's frames with his facing, so a picture with
    a front and a back that rides on the hero belongs in his frames. {"fx": effect sheet, "items": [...]}, applied in
    order; an item {"tag", "into", "at_ms", "under", "fx"} draws the effect tag into the action tag from at_ms on,
    centred on the pivot as a CasterViewEffect is (both are drawn centred on the unit), under the body when "under",
    moved "dx" columns / "dy" rows when given (a picture drawn for a hand that a smaller body moved: league_gwen);
    with {"from", "slice_ms", "length_ms"} the tag `into` is made first as `from`'s frames from slice_ms on (for
    length_ms, looping, when given) - a copy a
    CasterAnimation plays from the moment the picture played, when only some plays of the action carry it
    (tools/fix/bake_caster_fx.py). Returns {action tag: effect tags}."""
    path = os.path.join(SRC, f"{hero}_bake.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    import tfm2_ase
    sheets, done = {}, {}
    # a copy is made once every picture drawn straight into its source is in (league_xerath's passive copy of his
    # attack carries the attack's flash): items go in order of how deep in a chain of copies their tag is
    src = {e["into"]: e["from"] for e in cfg["items"] if "from" in e}

    def depth(tag):
        return 0 if tag not in src else depth(src[tag]) + 1
    for e in sorted(cfg["items"], key=lambda e: depth(e["into"])):
        name = e.get("fx", cfg["fx"])
        if name not in sheets:
            sheets[name] = tfm2_ase.load_sprite(os.path.join(MOD, "effects", name + "#sheet.png"))
        fx = sheets[name]
        ids = fx.tag_frames(e["tag"])
        if not ids:
            sys.exit(f"{hero}_bake.json: {name} has no tag {e['tag']}")
        if "from" in e:
            if e["from"] not in sheet:
                sys.exit(f"{hero}_bake.json: no tag {e['from']} to copy {e['into']} from")
            if e["into"] not in sheet:
                sheet[e["into"]] = slice_ms(sheet[e["from"]], int(round(e["slice_ms"])), e.get("length_ms"))
        elif e.get("length_ms") and sum(ms for _, ms in sheet[e["into"]]) < e["length_ms"]:
            sheet[e["into"]] = slice_ms(sheet[e["into"]], 0, e["length_ms"])     # a held loop drawn out first
        dx, dy = e.get("dx", 0), e.get("dy", 0)
        pic = [(offset(np.asarray(fx.frames[i]), dx, dy), fx.durations[i]) for i in ids]
        sheet[e["into"]] = overlay(sheet[e["into"]], pic, int(round(e["at_ms"])), e.get("under", False))
        done.setdefault(e["into"], []).append(e["tag"])
    return done


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
        for tag, slots in head_move(hero, sheet).items():
            print(f"{hero}: the head moved with the body in {tag} slots " + " ".join(str(k + 1) for k in slots))
        added, darkened, tidy = close_outline(hero, sheet)
        if added or darkened:
            print(f"{hero}: outline closed with {added} pixels added, {darkened} darkened on the feet line")
        if tidy:
            print(f"{hero}: outline tidied: " + ", ".join(f"{k} {v}" for k, v in tidy.items()))
        tidied = tidy_frames(hero, sheet)
        if tidied:
            print(f"{hero}: {TIDY[hero]} changed {tidied} pixels")
        if hero in SHRINK:
            # the idle shrinks as drawn, BEFORE it breathes: shrunk after, the body sat 0-2 rows lower in each
            # breathing frame, so one removed row ran through a different part of him in every frame and the face and
            # shoulders changed shape as he bobbed (「怎么上下摆动模型变形？」)
            import shrink_frames as SF
            body0 = SF.body_of(sheet["idle"])
            a0 = sheet["idle"][0][0]
            head = None
            if hero in SHRINK_HEAD:
                hs = SHRINK_HEAD[hero]
                head = SF.head_lines(sheet, SHRINK_ANCHOR[hero], hs["window"], hs["rows"], hs["cols"], hs["keep"])
                print(f"{hero}: head lines from the eyes' corner: rows {head['rows']}, columns {head['cols']}")
            idle_plan = SF.shrink_sheet(sheet, SHRINK[hero], keep_colours=SHRINK_KEEP.get(hero, ()), keep_by_tag=SHRINK_KEEP_TAG.get(hero), body=body0,
                                        tags=["idle"], anchor=SHRINK_ANCHOR.get(hero), still=SHRINK_STILL.get(hero, ()),
                                        head=head, keep_rows=SHRINK_KEEP_ROWS.get(hero, ()),
                                        robust=hero in SHRINK_ROBUST)["idle"]
            if hero in HEAD_AT:
                hx, hy = HEAD_AT[hero]
                nx, ny = SF.move_point(idle_plan, hx - a0.shape[1] // 2, hy - a0.shape[0] // 2)
                a1 = sheet["idle"][0][0]
                HEAD_AT[hero] = (a1.shape[1] // 2 + nx, a1.shape[0] // 2 + ny)
        rows = breathe_idle(hero, sheet)
        if rows is not None:
            print(f"{hero}: idle breathes from the design ({len(sheet['idle'])} frames x {IB.MS} ms; cut px "
                  f"{rows['dip_cost']:.0f}, lean px {rows['lean_cost']:.0f}, "
                  f"nod {'px %.0f' % rows['neck_cost'] if rows['neck'] is not None else 'OFF'})")
        for tag, fx in bake(hero, sheet).items():
            print(f"{hero}_bake.json: {tag} carries {', '.join(fx)} ({len(sheet[tag])} frames)")
        if hero in SHRINK:
            import shrink_frames as SF
            bake_path = os.path.join(SRC, f"{hero}_bake.json")
            copies = {}
            if os.path.exists(bake_path):
                with open(bake_path, encoding="utf-8") as f:
                    copies = {e["into"]: e["from"] for e in json.load(f)["items"] if "from" in e}
            groups = SHRINK_GROUPS.get(hero, {})
            plans = {"idle": idle_plan, **SF.shrink_sheet(sheet, SHRINK[hero], same_as=copies, body=body0,
                                                         keep_colours=SHRINK_KEEP.get(hero, ()), keep_by_tag=SHRINK_KEEP_TAG.get(hero),
                                                         tags=[t for t in sheet if t != "idle" and t not in groups],
                                                         anchor=SHRINK_ANCHOR.get(hero), still=SHRINK_STILL.get(hero, ()),
                                                         ground=SHRINK_GROUND.get(hero), head=head,
                                                         keep_rows=SHRINK_KEEP_ROWS.get(hero, ()),
                                                         robust=hero in SHRINK_ROBUST)}
            for tag, parts in groups.items():
                if tag not in sheet:
                    continue
                frames = list(sheet[tag])
                for part in parts:
                    sub = {tag: [frames[i] for i in part]}
                    plan = SF.shrink_sheet(sub, SHRINK[hero], body=SF.body_of(sub[tag]),
                                           keep_colours=SHRINK_KEEP.get(hero, ()), keep_by_tag=SHRINK_KEEP_TAG.get(hero),
                                           tags=[tag], anchor=SHRINK_ANCHOR.get(hero), ground=SHRINK_GROUND.get(hero),
                                           head=head, keep_rows=SHRINK_KEEP_ROWS.get(hero, ()),
                                           robust=hero in SHRINK_ROBUST)[tag]
                    for j, i in enumerate(part):
                        frames[i] = sub[tag][j]
                    plans[f"{tag}{'+'.join(str(i + 1) for i in part)}"] = plan
                sheet[tag] = frames
            SHRUNK[hero] = plans
            print(f"{hero}: shrunk to {SHRINK[hero]:.0%} without resampling: " + ", ".join(
                f"{t} -{len(p['rows'])}r -{len(p['cols'])}c" for t, p in plans.items()))
            # a TIDY module's clean-up for the shrunk frames (tidy_shrunk): a removed row can take a tip's cap with
            # it (Xerath's far leg)
            tidy_frames(hero, sheet, "tidy_shrunk")
        if hero in SHRINK_TAGS:
            import shrink_frames as SF
            body0 = SF.body_of(sheet["idle"])
            done = []
            for scale, tags in SHRINK_TAGS[hero].items():
                plans = SF.shrink_sheet(sheet, scale, body=body0, keep_colours=SHRINK_KEEP.get(hero, ()),
                                        keep_by_tag=SHRINK_KEEP_TAG.get(hero), tags=[t for t in tags if t in sheet],
                                        anchor=SHRINK_ANCHOR.get(hero))
                done += [f"{t} {scale:.0%} -{len(p['rows'])}r -{len(p['cols'])}c" for t, p in plans.items()]
            print(f"{hero}: actions shrunk without resampling: " + ", ".join(done))
        forms = form_sheets(hero, sheet)
        base_tags = dict(sheet)
        for name, fsheet in forms.items():
            prefix = FORM_SHEETS[hero][name]
            for tag in FORM_INTO_BASE:
                if tag in fsheet and prefix + tag not in sheet:
                    sheet[prefix + tag] = fsheet[tag]
        for name, s in [(hero, base_tags)] + list(forms.items()):
            if name in WALL_PREFIX:
                wall = wall_sheet({t: s[t] for t in WALL_INTO_BASE if t in s})
                for tag, fr in wall.items():
                    sheet[WALL_PREFIX[name] + tag] = fr
        added = [t for t in sheet if t not in base_tags]
        if added:
            print(f"league/champions/league_{hero}: the forms' and in-wall tags added for the add-on's anim-name swap: "
                  f"{', '.join(added)}")
        w, h = G.write_sheet(os.path.join(MOD, "champions", f"league_{hero}"), sheet)
        for name, fsheet in forms.items():
            fw, fh = G.write_sheet(os.path.join(MOD, "champions", f"league_{name}"), fsheet)
            print(f"league/champions/league_{name}#sheet.png {fw}x{fh}: {hero}'s sheet with the form's "
                  f"{', '.join(FORM_BODY)}")
        for name, s in [(hero, base_tags)] + list(forms.items()):
            if name in WALL_SHEETS:
                ww, wh = G.write_sheet(os.path.join(MOD, "champions", f"league_{WALL_SHEETS[name]}"), wall_sheet(s))
                print(f"league/champions/league_{WALL_SHEETS[name]}#sheet.png {ww}x{wh}: {name} as the in-wall shadow")
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
