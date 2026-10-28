"""Build the step-0 pack for Codex (assets/source/scar/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_scar_picture.py --out C:/t/sc_work/scar_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Xin Zhao, Ekko, Vander and Violet, 8x,
cut from their sheets), then <out>.zip.
Scar (刀疤, the tft pack's eleventh hero, 2026-10-28) is the Firelights' lookout from Arcane, Ekko's right hand: a
3-cost of Teamfight Tactics set 13 (TFT13_FlyGuy, 野火帮 / 监察), a lanky purple-skinned Zaunite behind a white skull
mask, a blue mohawk and one red fin ear, with a long spear. His model is in the Riot client's TFTSet13.wad.client:
tft13_flyguy.skn + .skl (84 joints), one colour map. His animation bin links its clips by path hash only: CLIPS below
names them by what they show (rendered and read by eye, 2026-10-28). No unit art in the client: the head close-ups
stand in. Two pictures at one square size: A = TFT's own idle (stooped, the spear held low point down at his near
side); B = his guard (the spear across his body, point forward: his attack's first frame). The user picks one.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
TFT = os.path.join(REPO, "tft", "champions")
GREY = (225, 225, 225)
WAD = ("Game", "DATA", "FINAL", "TFTSet13.wad.client")
CHAR = "assets/characters/tft13_flyguy/skins/base/"
SKN, SKL = CHAR + "tft13_flyguy.skn", CHAR + "tft13_flyguy.skl"
TEX = CHAR + "tft13_flyguy_base_tx_cm.tex"
CLIPS = {
    "idle": 1430248861950089530,         # 3.00 s: stooped, swaying, the spear low at his near side, point down
    "run": 12986692863889239956,         # 1.07 s: a loping walk, the spear trailing low
    "attack": 12086636227999197628,      # 0.87 s: the spear swung across and thrust forward, a hop at the end
    "spell": 15948400272949335952,       # 1.20 s: TFT's bombs: rears back, flings with the free hand, holds a fist up
    "leap": 223869349070185787,          # 1.37 s: hops up and lands in a low crouch, the spear level
    "crouch": 14500478677605050632,      # 0.03 s: the low crouch held
    "death": 15588946928206091316,       # 1.03 s: thrown back, the spear flying off
    "kneel": 2192231566616823064,        # 1.97 s: drops to one knee, spear down (celebration)
    "kneel2": 12371201834867713225,      # 2.63 s: kneels, the spear raised upright (celebration)
}
SQ = 11
SOLE = 1390
A_SQUARES = 54   # A: the top of his mohawk to his soles (stooped)
B_SQUARES = 54   # B: the guard, as tall
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_scar_34": (35, "box", "idle@0"),
    "2_scar_front": (0, "box", "idle@0"),
    "3_scar_head": (30, "head", "attack@0"),
    "4_scar_spear": (0, "box", "attack@250"),        # the spear held level across him: its whole length and its blade
    "5_scar_back": (180, "box", "idle@0"),
    "6_scar_head_front": (0, "head", "attack@250"),
    "7_scar_guard": (35, "box", "attack@0"),         # B: the guard
    "8_scar_throw": (35, "box", "spell@340"),        # flinging a bomb (Q)
    "9_scar_crouch": (35, "box", "leap@1360"),       # the low crouch, the spear level (E / R landing)
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_xinzhao.png": (CHAMPS, "league_xinzhao", "hd_idle"),
    "12_style_ekko.png": (CHAMPS, "league_ekko", "idle"),
    "13_style_vander.png": (TFT, "tft_vander", "hd_idle"),
    "14_style_violet.png": (TFT, "tft_violet", "hd_idle"),
}


class Model:
    """His mesh on his own skeleton, one colour map."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.tex = pose_ref.read_tex(self.w.read_path(TEX))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(SKL))
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]

    def posed(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        return pose_ref.skin(self.v, self.infl, self.bind_inv, glob)


def render(m, name, spec, out, size=1600):
    """A mirrored 3/4 render facing image right, the figure 70% of the cell, on grey."""
    yaw, crop, clip = spec
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    h = pv[:, 1].max()
    if crop == "head":
        size *= 2
    im = pose_ref.render_hq(pv, m.tris, m.v["uv"], m.tex, -yaw, 12, (size, size), size * 0.7 / h,
                            size * 0.86).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # mohawk, mask, fin ear, collar: the top 22% of him
        hh = y1 - y0
        hx0, _, hx1, _ = im.crop((0, y0, im.width, y0 + round(hh * 0.22))).getbbox()
        mg = (hx1 - hx0) // 10
        can = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.22)))
    else:
        mg = max(x1 - x0, y1 - y0) // 12
        can = can.crop((max(0, x0 - mg), max(0, y0 - mg), min(im.width, x1 + mg), min(im.height, y1 + mg)))
    can.convert("RGB").save(os.path.join(out, name + ".png"))
    print(name, can.size)
    return im


def guide(fig_full, name, squares, label):
    """The figure scaled to `squares` squares of SQ tall, the lowest point on SOLE, centred."""
    fig = fig_full.crop(fig_full.getbbox())
    k = squares * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(768 - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height),
          "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))


def cut(folder, sheet_name, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(folder, f"{sheet_name}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(folder, f"{sheet_name}#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)
    print(os.path.basename(out), pad.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    m = Model(a.lol)
    full = {name: render(m, name, spec, refs) for name, spec in RENDERS.items()}
    guide(full["1_scar_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, stooped, spear low; mohawk top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(full["7_scar_guard"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: the guard, spear across, point forward; mohawk top to soles ~{B_SQUARES * SQ} px "
          f"({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "scar", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
