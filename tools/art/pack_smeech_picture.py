"""Build the step-0 pack for Codex (assets/source/smeech/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_smeech_picture.py --out C:/t/sm_work/smeech_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Twitch, Kha'Zix, Scar and Violet, 8x,
cut from their sheets), then <out>.zip.
Smeech (史密奇, the tft pack's fourteenth hero, 2026-10-29) is a chem-baron of Arcane's Zaun: a 3-cost of Teamfight
Tactics set 13 (TFT13_Gremlin, 炼金男爵 / 伏击专家), a small grey-pink gremlin with huge pointed ears, a tall teal top hat
with a brass goggle, a purple waistcoat, two big olive-green mechanical arms ending in long brass claws and thin brass
stilt legs. His model is in the Riot client's TFTSet13.wad.client: tft13_gremlin.skn + .skl (106 joints), one colour
map (submesh `lambert1`, 36 vertices, is a hidden helper). His animation bin links its clips by path hash only: CLIPS
below names them by what they show (rendered and read by eye, 2026-10-29). Two pictures at one square size: A = TFT's
own idle (upright, one claw raised by his head); B = his ambush crouch (low, both claws spread). The user picks one.
"""
import argparse
import json
import os
import re
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
CHAR = "assets/characters/tft13_gremlin/skins/base/"
SKN, SKL = CHAR + "tft13_gremlin.skn", CHAR + "tft13_gremlin.skl"
TEX = CHAR + "tft13_gremlin_base_tx_cm.tex"
HIDE = {"lambert1"}
ARMS = re.compile(r"^[LR]_Clavicle$")   # head close-ups leave the arms out: the idle holds a claw by his head
CLIPS = {
    "idle": 10900990335982213967,        # 4.33 s: upright on his stilts, the near claw raised by his head, the far low
    "run": 5948713214957723904,          # 2.00 s: a long-legged stride, the claws swinging
    "crouch": 7334819074812565991,       # 2.03 s: leaps in to a low wide crouch, both claws spread (his combat loop)
    "slash": 6957054806472945297,        # 0.17 s: a quick crouched claw rake (attack)
    "leap": 14923403458757091775,        # 0.63 s: from the crouch springs up, claws high
    "pounce": 2480727939088304345,       # 0.50 s: a high leap that lands crouched, raking
    "stabs": 13338079495139900480,       # 1.73 s: lands and rakes, crouched, a claw thrust forward
    "death": 3593627491999115244,        # 1.17 s: stiffens, the hat flies off, falls on his back
    "spread": 3480799096908570845,       # 1.73 s: drops in from above to a crouch, claws torn wide to the sides
    "arms": 2057711140677436400,         # 1.00 s: both claws thrown up wide over his head (a cheer)
}
SQ = 11
SOLE = 1390
A_SQUARES = 56   # A: the top of his hat to his soles; B uses the same scale (the crouch is lower)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_smeech_34": (35, "box", "idle@0"),
    "2_smeech_front": (0, "box", "idle@0"),
    "3_smeech_head": (30, "head", "idle@0"),
    "4_smeech_side": (90, "box", "idle@0"),           # side on: the arm, the claws, the stilt legs
    "5_smeech_back": (180, "box", "idle@0"),
    "6_smeech_head_front": (0, "head", "idle@0"),
    "7_smeech_crouch": (35, "box", "crouch@1160"),    # B
    "8_smeech_leap": (35, "box", "pounce@210"),       # in the air, claws up (Q's leap)
    "9_smeech_rake": (35, "box", "stabs@900"),        # crouched, a claw thrust forward (Q's slashes)
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_twitch.png": (CHAMPS, "league_twitch", "idle"),
    "12_style_khazix.png": (CHAMPS, "league_khazix", "idle"),
    "13_style_scar.png": (TFT, "tft_scar", "idle"),
    "14_style_violet.png": (TFT, "tft_violet", "idle"),
}


class Model:
    """His mesh on his own skeleton, one colour map."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        tris, self.v = pose_ref.read_skn(b)
        self.tris = pose_ref.drop_submeshes(tris, pose_ref.skn_submeshes(b), HIDE)
        self.tex = pose_ref.read_tex(self.w.read_path(TEX))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(SKL))
        arm = pose_ref.chain_vertices(self.joints, self.infl, self.v, ARMS)
        self.no_arms = self.tris[~arm[self.tris].any(axis=1)]
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]

    def posed(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        return pose_ref.skin(self.v, self.infl, self.bind_inv, glob)


def render(m, name, spec, out, scale=None, size=1600):
    """A mirrored 3/4 render facing image right on grey; returns the full render and the scale used (the figure 70%
    of the cell, or `scale` to keep one size across renders)."""
    yaw, crop, clip = spec
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    h = pv[:, 1].max()
    tris = m.tris
    if crop == "head":
        size *= 2
        tris = m.no_arms
    k = scale if scale else size * 0.7 / h
    im = pose_ref.render_hq(pv, tris, m.v["uv"], m.tex, -yaw, 12, (size, size), k,
                            size * 0.86).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # hat, ears, face, hair, cravat: the top 36% of him
        hh = y1 - y0
        hx0, _, hx1, _ = im.crop((0, y0, im.width, y0 + round(hh * 0.36))).getbbox()
        mg = (hx1 - hx0) // 10
        can = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.36)))
    else:
        mg = max(x1 - x0, y1 - y0) // 12
        can = can.crop((max(0, x0 - mg), max(0, y0 - mg), min(im.width, x1 + mg), min(im.height, y1 + mg)))
    can.convert("RGB").save(os.path.join(out, name + ".png"))
    print(name, can.size)
    return im, k


def guide(fig_full, name, k, label):
    """The figure scaled by `k` (px per render px), the lowest point on SOLE, centred."""
    fig = fig_full.crop(fig_full.getbbox())
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
    full, scale = {}, None
    for name, spec in RENDERS.items():   # the body renders share the idle's scale: the crouch shows as low as it is
        im, k = render(m, name, spec, refs, scale if spec[1] == "box" and spec[0] != 90 else None)
        if name == "1_smeech_34":
            scale = k
        full[name] = im
    a_fig = full["1_smeech_34"]
    k = A_SQUARES * SQ / (a_fig.getbbox()[3] - a_fig.getbbox()[1])
    b_box = full["7_smeech_crouch"].getbbox()
    b_sq = round((b_box[3] - b_box[1]) * k / SQ)
    guide(a_fig, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, upright on his stilts; hat top to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); "
          f"layout only")
    guide(full["7_smeech_crouch"], os.path.join(refs, "10b_layout_B.png"), k,
          f"B: the ambush crouch at the same scale; hat top to soles ~{b_sq * SQ} px ({b_sq} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "smeech", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
