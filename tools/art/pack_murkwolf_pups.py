#!/usr/bin/env python3
"""Murk Wolf's pup pack for Codex (assets/source/murkwolf/PUP_PROMPT.md): the two pups of Pack Attack drawn side-on so
they can face the enemy (the user, 2026-11-01: 「召唤出来的小狼应该面向敌人 参考沙皇怎么做的」「左右都可以面向敌人」).

    python tools/art/pack_murkwolf_pups.py [--out D:/TFM2-Workshop/murkwolf_packs/murkwolf_pup_pack] [--lol "D:/Riot Games/League of Legends"]

Codex's first pups (codex_fx r_pack) face the camera, so a picture cannot turn them. One pup is drawn here at the
design's own 3/4 angle facing right (yaw 35, as pack_murkwolf_poses), in six poses of the Rift's own small murk wolf
(Map11.wad.client sru_murkwolfmini: its skin bin links its colour map and clips by hash only; POSES names them): it
stands snarling, breathes, winds up, lunges with its jaws forward, comes back and settles. tft.dll shows the pair
facing the enemy (tft_murkwolf_r_pack_r / _l, the left one this mirrored) and starts the loop again on each of the
wolf's attacks, so the lunge lands with the pups' bites.
Writes <out>/ (and <out>.zip): PUP_PROMPT.md; 0_design.png (the approved wolf 4x: the style and colours);
1_front_pups.png (Codex's first pup 8x: its look - one head, the purple tuft, cyan eyes); 2_refs.png (the six poses
rendered on the sheet's own 3 x 2 cells, grid and ground lines: the layout Codex draws on); 2_refs_<k>_<name>.png
(each cell alone, bigger).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402
from design_murkwolf_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "murkwolf")
WAD = ("Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client")
CHAR = "assets/characters/sru_murkwolfmini/skins/base/sru_murkwolfmini."
TEX = 13420671269609466733                         # its colour map (by hash: the bin names no path)
SNARL, ATTACK = 13101259856837962997, 2773741144029627769   # 1.0 s crouched snarl loop, 1.67 s attack
# name -> (clip, seconds, what it is for (Chinese), the pose line (English))
POSES = {
    "stand": (SNARL, 0.0, "站着龇牙低吼", "STAND - crouched low on four legs, head forward, snarling with its fangs bared."),
    "breath": (SNARL, 0.5, "喘气（和站着几乎一样，身子微微起伏）",
               "BREATHE - the same stance, the chest a square lower, the mouth a little more open."),
    "crouch": (ATTACK, 0.15, "扑之前缩身蓄力", "WIND UP - drawn back on its hind legs, the head low, about to spring."),
    "lunge": (ATTACK, 0.6, "往前扑咬：身子拉长贴地，嘴张到最大", "LUNGE - stretched long and low toward the right, the jaws wide open at the front."),
    "recover": (ATTACK, 0.8, "咬完往回收", "PULL BACK - coming back from the lunge, the tail up, the mouth closing."),
    "settle": (ATTACK, 1.0, "站回原地", "SETTLE - back in its low stance, head forward."),
}
COLS, ROWS = 3, 2
CW, CH = 400, 300                # a cell, raw px
SQ = 12                          # raw px a square (the pup about 26 x 18 squares = game px)
GROUND = CH - 24                 # the ground line in each cell
PUP_W = 26                       # the stand pose's width in squares
YAW, PITCH = 35, 12
GREY = (225, 225, 225)


class Mini:
    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        self.tris, self.v = pose_ref.read_skn(self.w.read_path(CHAR + "skn"))
        self.tex = pose_ref.read_tex(self.w.read(TEX))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(CHAR + "skl"))
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]

    def posed(self, clip, t):
        local = pose_ref.local_pose(self.joints, pose_ref.read_anim(self.w.read(clip)), t)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        return pose_ref.skin(self.v, self.infl, self.bind_inv, glob)


def project_x(pv):
    """Mirrored screen x of the vertices at the pack's angle (render_hq's camera), unscaled."""
    y_ = np.radians(-YAW)
    cy, sy = np.cos(y_), np.sin(y_)
    return -(pv[:, 0] * cy + pv[:, 2] * sy)


def grid(d, x0, y0):
    for k in range(0, CW + 1, SQ):
        d.line([(x0 + k, y0), (x0 + k, y0 + CH)], fill=(212, 212, 212))
    for k in range(0, CH + 1, SQ):
        d.line([(x0, y0 + k), (x0 + CW, y0 + k)], fill=(212, 212, 212))
    d.line([(x0, y0 + GROUND), (x0 + CW, y0 + GROUND)], fill=(220, 40, 40), width=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\murkwolf_packs\murkwolf_pup_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    m = Mini(a.lol)
    # one scale for all: the stand pose PUP_W squares wide, its middle in the cell's middle
    pv0 = m.posed(*POSES["stand"][:2])
    xs = project_x(pv0)
    scale = PUP_W * SQ / np.ptp(xs)
    mid0 = (xs.min() + xs.max()) / 2
    sheet = Image.new("RGB", (CW * COLS, CH * ROWS), GREY)
    d = ImageDraw.Draw(sheet)
    for k, (name, (clip, t, _zh, _en)) in enumerate(POSES.items()):
        pv = m.posed(clip, t).copy()
        pv[:, 1] -= pv[:, 1].min()
        # every pose on the stand's middle (render_hq centres the model's origin; shift puts the stand mid there)
        im = pose_ref.render_hq(pv, m.tris, m.v["uv"], m.tex, -YAW, PITCH, (CW, CH), scale, GROUND,
                                shift=mid0 * scale / CW).transpose(Image.FLIP_LEFT_RIGHT)
        im = im.transform(im.size, Image.AFFINE, (1, 0, 0, 0, 1, im.getbbox()[3] - GROUND))   # the lowest paw on the line
        x0, y0 = (k % COLS) * CW, (k // COLS) * CH
        grid(d, x0, y0)
        sheet.paste(im, (x0, y0), im)
        d.text((x0 + 6, y0 + 4), f"{k + 1} {name}", fill=(0, 0, 0))
        cell = Image.new("RGB", (CW, CH), GREY)
        cd = ImageDraw.Draw(cell)
        grid(cd, 0, 0)
        cell.paste(im, (0, 0), im)
        cell.resize((CW * 2, CH * 2), Image.NEAREST).save(lp(os.path.join(a.out, f"2_refs_{k + 1}_{name}.png")))
    sheet.save(lp(os.path.join(a.out, "2_refs.png")))
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    bg = Image.new("RGBA", (design.width * 4 + 32, design.height * 4 + 32), GREY + (255,))
    bg.alpha_composite(design.resize((design.width * 4, design.height * 4), Image.NEAREST), (16, 16))
    bg.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    pups = Image.open(lp(os.path.join(SRC, "codex_fx", "murkwolf_fx", "pixel_1x", "murkwolf_fx_r_pack.png"))).convert("RGBA")
    pup = pups.crop((0, 0, 30, 40))
    pup = pup.crop(pup.getbbox())
    bg = Image.new("RGBA", (pup.width * 8 + 32, pup.height * 8 + 32), GREY + (255,))
    bg.alpha_composite(pup.resize((pup.width * 8, pup.height * 8), Image.NEAREST), (16, 16))
    bg.convert("RGB").save(lp(os.path.join(a.out, "1_front_pups.png")))
    shutil.copyfile(lp(os.path.join(SRC, "PUP_PROMPT.md")), lp(os.path.join(a.out, "PUP_PROMPT.md")))
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()
