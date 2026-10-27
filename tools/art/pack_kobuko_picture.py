"""Build the step-0 pack for Codex (assets/source/kobuko/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_kobuko_picture.py --out C:/t/kb_work/kobuko_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Volibear, Yuumi, Braum and Loris, 8x,
cut from their sheets), then <out>.zip.
Kobuko (the tft pack's seventh hero, 2026-10-27) is the big kung-fu cat yordle, the old master. The client holds four
of him (set 14's cyber boss, set 15's mentor, set 16's with Yuumi, set 18's Fortune Yordle); the user picked set 15's
look: TFTSet15.wad.client TFT15_Kobuko_15.skn + .skl, one submesh (Kobuko_Set15_Body_Mat), one colour map. His
animation bin links its clips by path hash only: CLIPS below names them by what they show (rendered and read by eye,
2026-10-27). No unit art in the client (only the 64 px square): the head close-up stands in for it.
Two pictures at one square size: A = TFT's own idle (stooped a little, one paw stroking his beard); B = his kung-fu
salute (legs planted wide, both palms pressed together in front of his chest). The user picks one.
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
WAD = ("Game", "DATA", "FINAL", "TFTSet15.wad.client")
CHAR = "assets/characters/tft15_kobuko/skins/base/"
SKN, SKL = CHAR + "tft15_kobuko_15.skn", CHAR + "tft15_kobuko_15.skl"
TEX = CHAR + "tft15_kobuko_base_tx_cm.tex"
CLIPS = {
    "attack": 18280324247829311176,      # 1.87 s: a wound-up straight punch, the flaming paw thrust out
    "attack2": 4364530676104939554,      # 1.87 s: a wide open-palm strike
    "attack3": 10403877704971042905,     # 1.87 s: both palms pushed out low
    "death": 90445141234099937,          # 1.17 s: staggers, falls flat on his face
    "run": 3955763753304127550,          # 1.07 s: a waddling jog, the arms swinging
    "idle": 18059608280507388438,        # 4.33 s: standing tall, one paw stroking his beard
    "dance": 4959498569199180241,        # 4.33 s: a kung-fu kata (7938417382343848938 is the same clip)
    "spell": 11435117379888102304,       # 1.30 s: crouched, both arms swept up high, then spread wide
    "spell_end": 16539334345155014184,   # 0.77 s: from the arms up into the wide stance
    "spell2": 7350679012711790214,       # 1.00 s: arms spread like wings, then a palm thrust forward
    "leap": 4854041923670591047,         # 0.37 s: crouches and springs straight up out of sight
    "stance": 9245205664208522479,       # 1.07 s: a palm thrust, then both palms pressed together, legs wide
}
SQ = 11
SOLE = 1390
A_SQUARES = 56   # A: the top of his topknot to his soles
B_SQUARES = 62   # B: the same body scale (his model stands 228 high in the stance, 206 in the stooped idle)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_kobuko_34": (35, "box", "idle@0"),
    "2_kobuko_front": (0, "box", "idle@0"),
    "3_kobuko_head": (20, "head", "spell_end@770"),     # the arms spread: the face clear of his paws
    "4_kobuko_stance": (35, "box", "stance@1000"),      # B: the salute stance, palms pressed together
    "5_kobuko_back": (180, "box", "idle@0"),
    "6_kobuko_head_front": (0, "head", "spell_end@770"),
    "7_kobuko_arms": (0, "box", "spell_end@770"),       # the arms spread: the flame fur, the paws, the vest
    "8_kobuko_strike": (35, "box", "attack@800"),       # his punch: how far the arm reaches
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_volibear.png": (CHAMPS, "league_volibear", "hd_idle"),
    "12_style_yuumi.png": (CHAMPS, "league_yuumi", "hd_idle"),
    "13_style_braum.png": (CHAMPS, "league_braum", "hd_idle"),
    "14_style_loris.png": (TFT, "tft_loris", "hd_idle"),
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
    if crop == "head":   # topknot, ears, face, beard: the top 45% of him (a big chibi head)
        hh = y1 - y0
        hx0, _, hx1, _ = im.crop((0, y0, im.width, y0 + round(hh * 0.45))).getbbox()
        mg = (hx1 - hx0) // 10
        cut_ = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.45)))
        can = Image.new("RGBA", cut_.size, GREY + (255,))   # past the render's edge: grey, not black
        can.alpha_composite(cut_)
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
    guide(full["1_kobuko_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, standing tall, 3/4; topknot to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ});"
          " layout only")
    guide(full["4_kobuko_stance"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: the kung-fu salute, palms together; topknot to soles ~{B_SQUARES * SQ} px ({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "kobuko", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
