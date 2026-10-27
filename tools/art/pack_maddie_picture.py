"""Build the step-0 pack for Codex (assets/source/maddie/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_maddie_picture.py --out C:/t/md_work/maddie_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips, the unit art and
the layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Caitlyn, Jayce, Jinx and
Powder, 8x, cut from their sheets), then <out>.zip.
Maddie (the tft pack's fifth hero, 2026-10-27) is the Piltover enforcer and sharpshooter from Arcane, a 1-cost of
Teamfight Tactics set 13 (TFT13_Shooter, 执法官 / 狙神). Her model is in the Riot client's TFTSet13.wad.client:
TFT13_Shooter.skn + .skl, one colour map, submeshes Maddie_Mat (her) / Maddie_Weapon_Mat (the long hextech rifle).
Her animation bin links its seven clips by path hash only: CLIPS below names them by what they show (rendered and read
by eye, 2026-10-27).
Two pictures at one square size: A = TFT's own idle (the rifle resting on her shoulder, pointing back); B = the rifle
held level at her hip in both hands, ready to shoot (the pose her attack and spell start from). The user picks one.
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
CHAR = "assets/characters/tft13_shooter/skins/base/"
SKN, SKL = CHAR + "tft13_shooter.skn", CHAR + "tft13_shooter.skl"
TEX = CHAR + "tft13_shooter_base_tx_cm.tex"
CLIPS = {
    "attack": 9442017117116323456,     # 1.80 s: fires from the hip, the rifle kicks up overhead, brought back down
    "attack2": 4917163218412586985,    # 1.63 s: the same shot, crouched lower, the rifle kicked up to her far side
    "death": 7615907492795903732,      # 0.70 s: thrown backwards off her feet
    "run": 920374298908057164,         # 0.77 s: a jog, the rifle held low across her hips
    "idle": 1279733149212293106,       # 2.57 s: standing tall, the rifle resting on her near shoulder, muzzle back
    "spell": 1629561796695040463,      # 1.60 s: crouched, the rifle at her cheek, fanning six quick shots
    "dance": 15727121626644832222,     # 3.27 s: the celebration (the rifle floats free: not used)
}
SQ = 11
SOLE = 1390
A_SQUARES = 56   # A: the top of her beret to her soles
B_SQUARES = 56   # B: the same body, the rifle at her hip
# name -> (yaw, crop "box" / "head", clip@ms, hidden submeshes)
RENDERS = {
    "1_maddie_34": (35, "box", "idle@0", set()),
    "2_maddie_front": (0, "box", "idle@0", set()),
    "3_maddie_head": (20, "head", "idle@0", set()),
    "4_maddie_side": (90, "box", "idle@0", set()),
    "5_maddie_back": (200, "box", "idle@0", set()),
    "7_maddie_rifle": (90, "box", "idle@0", {"Maddie_Mat"}),     # the rifle alone, side on
    "8_maddie_ready": (35, "box", "attack@0", set()),           # B: the rifle level at her hip
    "9_maddie_spell": (35, "box", "spell@500", set()),          # her crouched rapid fire: arm and rifle lengths
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_caitlyn.png": (CHAMPS, "league_caitlyn", "hd_idle"),
    "12_style_jayce.png": (CHAMPS, "league_jayce", "hd_idle"),
    "13_style_jinx.png": (CHAMPS, "league_jinx", "hd_idle"),
    "14_style_powder.png": (TFT, "tft_powder", "hd_idle"),
}


class Model:
    """Her mesh on her own skeleton, one colour map."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.subs = pose_ref.skn_submeshes(b)
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
    yaw, crop, clip, hide = spec
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    h = pv[:, 1].max()
    tris = pose_ref.drop_submeshes(m.tris, m.subs, hide)
    if crop == "head":
        size *= 2
    im = pose_ref.render_hq(pv, tris, m.v["uv"], m.tex, -yaw, 12, (size, size), size * 0.7 / h,
                            size * 0.86).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # beret, hair, face, collar: the top 26% of her (the rifle on the shoulder cut away)
        hh = y1 - y0
        im2 = pose_ref.render_hq(pv, pose_ref.drop_submeshes(m.tris, m.subs, {"Maddie_Weapon_Mat"}), m.v["uv"],
                                 m.tex, -yaw, 12, (size, size), size * 0.7 / h, size * 0.86).transpose(Image.FLIP_LEFT_RIGHT)
        can = Image.new("RGBA", im2.size, GREY + (255,))
        can.alpha_composite(im2)
        _, y0, _, y1 = im2.getbbox()
        hh = y1 - y0
        hx0, _, hx1, _ = im2.crop((0, y0, im2.width, y0 + round(hh * 0.26))).getbbox()
        mg = (hx1 - hx0) // 10
        can = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.26)))
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
    ap.add_argument("--art", default=r"C:\t\md_work\tft13_maddie_mobile.png",
                    help="the unit's art (CommunityDragon latest, tft13_shooter/skins/base/images/tft13_shooter_mobile.png)")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    m = Model(a.lol)
    full = {name: render(m, name, spec, refs) for name, spec in RENDERS.items()}
    art = Image.open(a.art).convert("RGB")
    art.resize((art.width * 2, art.height * 2), Image.LANCZOS).save(os.path.join(refs, "6_maddie_art.png"))
    guide(full["1_maddie_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, the rifle on her shoulder, 3/4; beret top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(full["8_maddie_ready"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: the rifle level at her hip; beret top to soles ~{B_SQUARES * SQ} px ({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "maddie", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
