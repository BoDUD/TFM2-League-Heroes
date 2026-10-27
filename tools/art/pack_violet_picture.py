"""Build the step-0 pack for Codex (assets/source/violet/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_violet_picture.py --out C:/t/vo_work/violet_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Vi, Vander, Powder and Silco, 8x, cut
from their sheets), then <out>.zip.
Violet (the tft pack's ninth hero, 2026-10-28) is young Vi from Arcane's first act, Powder's big sister and Vander's
adopted daughter, a Zaun street fighter with two huge mismatched gauntlets, a 1-cost of Teamfight Tactics set 13
(TFT13_Red, 家人 / 搏击手). Her model is in the Riot client's TFTSet13.wad.client: tft13_red.skn + .skl, one colour map.
Her animation bin links its clips by path hash only: CLIPS below names them by what they show (rendered and read by
eye, 2026-10-28). The client holds no unit art for her (only a 128 px hud square): the head close-up stands in.
Two pictures at one square size: A = TFT's own idle (a wide brawler's stance, both gauntlets hanging low); B = her
fighting stance (fists up, the near gauntlet forward: the pose her combo starts from). The user picks one.
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
CHAR = "assets/characters/tft13_red/skins/base/"
SKN, SKL = CHAR + "tft13_red.skn", CHAR + "tft13_red.skl"
TEX = CHAR + "tft13_red_base_tx_cm.tex"
CLIPS = {
    "attack": 16191572733092226030,      # 1.67 s: winds up, lunges low onto the front leg with a straight punch
    "attack2": 6942115555056490602,      # 1.70 s: a lunging jab, then a jumping uppercut (@1214)
    "spell": 15683852769271390814,       # 3.43 s: TFT's 1-2-3: a jab, a wind-up, a jumping uppercut (@1471), lands
    "run": 2551755895439607214,          # 0.93 s: a jog, both gauntlets up
    "idle": 4829535862184344165,         # 2.33 s: a wide brawler's stance, both gauntlets hanging low
    "dance": 16474994073858986069,       # 4.83 s: fist pumps (celebration)
    "death": 8954725231413388605,        # 0.87 s: knocked back, falls on her back
}
SQ = 11
SOLE = 1390
A_SQUARES = 54   # A: the top of her hair to her soles (a wide, low stance)
B_SQUARES = 54   # B: the fighting stance, as tall
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_violet_34": (35, "box", "idle@0"),
    "2_violet_front": (0, "box", "idle@0"),
    "3_violet_head": (20, "head", "idle@0"),
    "4_violet_gauntlets": (0, "box", "dance@690"),     # a gauntlet raised over her head, its face seen
    "5_violet_back": (180, "box", "idle@0"),
    "6_violet_head_front": (0, "head", "idle@0"),
    "7_violet_stance": (35, "box", "spell@0"),       # B: the fighting stance
    "8_violet_uppercut": (35, "box", "spell@1471"),  # the jumping uppercut (Q)
    "9_violet_punch": (35, "box", "attack@476"),     # the lunging punch
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_vi.png": (CHAMPS, "league_vi", "idle"),
    "12_style_vander.png": (TFT, "tft_vander", "hd_idle"),
    "13_style_powder.png": (TFT, "tft_powder", "hd_idle"),
    "14_style_silco.png": (TFT, "tft_silco", "hd_idle"),
}


class Model:
    """Her mesh on her own skeleton, one colour map."""

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
    if crop == "head":   # hair, face, collar: the top 22% of her
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
    guide(full["1_violet_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, the wide brawler stance, 3/4; hair top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(full["7_violet_stance"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: the fighting stance, fists up; hair top to soles ~{B_SQUARES * SQ} px "
          f"({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "violet", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
