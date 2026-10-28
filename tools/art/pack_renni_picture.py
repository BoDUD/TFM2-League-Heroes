"""Build the step-0 pack for Codex (assets/source/renni/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_renni_picture.py --out C:/t/rn_work/renni_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Sett, Vi, Scar and Violet, 8x, cut
from their sheets), then <out>.zip.
Renni (荏妮, the tft pack's thirteenth hero, 2026-10-29) is a chem-baron of Arcane's Zaun: a 3-cost of Teamfight Tactics
set 13 (TFT13_Chainsaw, 炼金男爵 / 格斗家), a red-haired woman with a glowing green respirator over her mouth, a ruff of
dark green-black feathers, purple clothes and a huge brass chainsaw. Her model is in the Riot client's
TFTSet13.wad.client: tft13_chainsaw.skn + .skl (107 joints), two colour maps (the body's, and the saw's own by path hash
only). Her animation bin links its clips by path hash only: CLIPS below names them by what they show (rendered and read
by eye, 2026-10-29). Two pictures at one square size: A = TFT's own idle (the saw upright over her shoulder); B = her
fighting stance (the saw held level, pointing forward). The user picks one.
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
CHAR = "assets/characters/tft13_chainsaw/skins/base/"
SKN, SKL = CHAR + "tft13_chainsaw.skn", CHAR + "tft13_chainsaw.skl"
TEX = CHAR + "tft13_chainsaw_base_tx_cm.tex"
SAW_TEX = 11745584107417945725       # the chainsaw's colour map (256x256; the skin bin names it by hash only)
TEETH = ("WeaponBotTeeth", "WeaponRightTeeth", "WeaponLeftTeeth")   # hidden until her spell
CLIPS = {
    "idle": 13964740436261919456,        # 1.73 s: feet wide, the saw upright over her near shoulder, breathing
    "stance": 9093078845524720128,       # 1.27 s: the saw held level forward at the hip, revving (her attack loop)
    "run": 2500085982701353139,          # 1.13 s: a hunched run, the saw low at her side
    "intro": 12098856479311403935,       # 3.00 s: the saw raised, a low crouch, then the stance
    "death": 7638630921857068434,        # 1.17 s: thrown up and back, lands flat
    "lift": 4073066626161846832,         # 1.40 s: her spell: rams the saw forward, then heaves it up overhead
    "lift_fast": 143525122915255582,     # 0.57 s: the same, quicker
    "hold": 7832275817039968118,         # 0.40 s: the saw held straight up overhead (loop)
    "slam": 1608444182459498967,         # 1.10 s: from overhead the saw slammed to the ground, back to the stance
}
SQ = 11
SOLE = 1390
A_SQUARES = 54   # A: the top of her hair to her soles
B_SQUARES = 54   # B: the stance, as tall
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_renni_34": (35, "box", "idle@0"),
    "2_renni_front": (0, "box", "idle@0"),
    "3_renni_head": (30, "head", "stance@0"),
    "4_renni_saw": (90, "box", "stance@0"),         # side on: the saw's whole length, the engine and the blade
    "5_renni_back": (180, "box", "idle@0"),
    "6_renni_head_front": (0, "head", "idle@0"),
    "7_renni_stance": (35, "box", "stance@0"),      # B
    "8_renni_lift": (35, "box", "hold@0"),          # the saw heaved up overhead (R's lift)
    "9_renni_slam": (35, "box", "slam@627"),        # the saw slammed into the ground (R's slam)
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_sett.png": (CHAMPS, "league_sett", "idle"),
    "12_style_vi.png": (CHAMPS, "league_vi", "idle"),
    "13_style_scar.png": (TFT, "tft_scar", "idle"),
    "14_style_violet.png": (TFT, "tft_violet", "idle"),
}


class Model:
    """Her mesh on her own skeleton: the body's colour map, the chainsaw's own (its submesh `Weapon`; the three teeth
    submeshes are hidden until her spell shows them)."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        tris, self.v = pose_ref.read_skn(b)
        self.tris = pose_ref.drop_submeshes(tris, pose_ref.skn_submeshes(b), set(TEETH))
        self.tex = pose_ref.read_tex(self.w.read_path(TEX))
        saw = pose_ref.read_tex(self.w.read(SAW_TEX))
        vmap = pose_ref.submesh_vertex_maps(b, len(self.v), [(["Weapon"], 1)])
        self.tri_tex = (vmap[self.tris[:, 0]], [self.tex, saw])
        body = self.tri_tex[0] == 0          # head close-ups leave the saw out: it stands over her head
        self.body = (self.tris[body], (self.tri_tex[0][body], [self.tex, saw]))
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
    tris, tri_tex = (m.tris, m.tri_tex)
    if crop == "head":
        size *= 2
        tris, tri_tex = m.body
    im = pose_ref.render_hq(pv, tris, m.v["uv"], m.tex, -yaw, 12, (size, size), size * 0.7 / h,
                            size * 0.86, tri_tex=tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # hair, face, respirator, feather ruff: the top 22% of her
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
    guide(full["1_renni_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, the saw upright over her shoulder; hair top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(full["7_renni_stance"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: the stance, the saw level forward; hair top to soles ~{B_SQUARES * SQ} px "
          f"({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "renni", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
