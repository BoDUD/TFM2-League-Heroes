"""Build the step-0 pack for Codex (assets/source/alune/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_alune_picture.py --out C:/t/al_work/alune_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips, the unit art and
the layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Aphelios, Lux, Zoe and
Powder, 8x, cut from their sheets), then <out>.zip.
Alune (the tft pack's third hero, 2026-10-26) is Aphelios's sister, the moon priestess of Teamfight Tactics set 18
(DA_18_Alune, 5-cost, 月华神女 / 月蚀骑士 / 法师). Her model is in the Riot client's TFTSet18.wad.client (the WeGame
client stops at set 17): mesh TFT18_Alune.skn + .skl with submeshes Body / Legs / Accessory / Scarf / Skirt / Weapon;
Body / Legs / Accessory / Scarf use tft18_alune_base_tx_cm, Weapon and Skirt reuse set 11's maps
(tft11_alune_base_weapon_tx_cm / _skirt_tx_cm; the skin bin names none of them, the paths were found by hash). Her
animation bin links its nine clips by path hash only (no names): CLIPS below names them by what they show.
She floats SITTING on her weapon - a huge bronze crescent-moon glaive with blue blades and an inner spiral ring holding
a glowing moon orb - with her arms crossed; she never stands on the ground in her idle.
Two pictures at one square size: A = riding the crescent (TFT's own idle); B = standing on her feet, the crescent
glaive held upright in her near hand (an easier body for TFM2's actions). The user picks one.
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
WAD = ("Game", "DATA", "FINAL", "TFTSet18.wad.client")
CHAR = "assets/characters/tft18_alune/skins/base/"
SKN, SKL = CHAR + "tft18_alune.skn", CHAR + "tft18_alune.skl"
TEX_BODY = CHAR + "tft18_alune_base_tx_cm.tex"
TEX_WEAPON = "assets/characters/tft11_alune/skins/base/tft11_alune_base_weapon_tx_cm.tex"
TEX_SKIRT = "assets/characters/tft11_alune/skins/base/tft11_alune_base_skirt_tx_cm.tex"
# her animation bin's clips, by path hash: what each shows (rendered and read by eye, 2026-10-26)
CLIPS = {
    "idle": 12469321893979980437,      # 1.67 s: sitting on the crescent, arms crossed, floating
    "idle2": 7966476808059325458,      # 1.67 s: idle variant, one hand waving
    "death": 7391604195857774405,      # 1.67 s: falls backwards, the glaive breaks into rings
    "attack": 17888782102650701996,    # 1.33 s: stands, swings the spiral ring flat like a disc
    "spell": 11946670551696761899,     # 5.87 s: the ring raised behind her head like a halo, channelling
    "dance": 1894647713618011335,      # 13.6 s: celebration
    "run": 3503297707905851253,        # 0.63 s: standing upright on the crescent, gliding
    "to_run": 4495072253060600498,     # 0.87 s: idle -> run (steps off, the ring folds into the crescent)
    "to_idle": 8239692458849125302,    # 0.40 s: run -> idle (sits back down)
}
SQ = 11
SOLE = 1390
A_SQUARES = 60   # A: the top of her horn ornament to the lowest tip of the crescent
B_SQUARES = 52   # B: the top of the glaive (held upright) to her soles
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {   # her idle sits sideways on the crescent: yaw 270 is her profile facing right, 305 the 3/4, 340 the front
    "1_alune_34": (305, "box", "idle@0"),
    "2_alune_front": (340, "box", "idle@0"),
    "3_alune_head": (305, "head", "idle@0"),
    "4_alune_side": (270, "box", "idle@0"),
    "5_alune_back": (160, "box", "idle@0"),
    "7_alune_standing": (35, "box", "spell@2000"),    # standing on her feet, the spiral ring held up at her side
    "8_alune_attack": (35, "box", "attack@0"),        # standing, the glaive swung flat
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_aphelios.png": (CHAMPS, "league_aphelios", "hd_idle"),
    "12_style_lux.png": (CHAMPS, "league_lux", "hd_idle"),
    "13_style_zoe.png": (CHAMPS, "league_zoe", "hd_idle"),
    "14_style_powder.png": (TFT, "tft_powder", "hd_idle"),
}


class Model:
    """Her mesh on her own skeleton, each submesh with its own colour map."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        maps = [pose_ref.read_tex(self.w.read_path(p)) for p in (TEX_BODY, TEX_WEAPON, TEX_SKIRT)]
        vmap = pose_ref.submesh_vertex_maps(b, len(self.v), [({"Weapon"}, 1), ({"Skirt"}, 2)])
        self.tri_tex = (vmap[self.tris[:, 0]], maps)
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
    im = pose_ref.render_hq(pv, m.tris, m.v["uv"], None, -yaw, 12, (size, size), size * 0.7 / h, size * 0.86,
                            tri_tex=m.tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # the horn ornament, the hair, the face and the collar: the top 30% of her (the crescent is low)
        hh = y1 - y0
        im2 = im.crop((0, y0, im.width, y0 + round(hh * 0.3)))
        hx0, _, hx1, _ = im2.getbbox()
        mg = (hx1 - hx0) // 10
        can = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.3)))
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
    ap.add_argument("--art", default=r"C:\t\al_work\cd\tft18_alune_splash_tile_15.png",
                    help="the unit's tile art (CommunityDragon latest, images/tft18_alune_splash_tile_15.png)")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    m = Model(a.lol)
    full = {name: render(m, name, spec, refs) for name, spec in RENDERS.items()}
    art = Image.open(a.art).convert("RGB")
    art.resize((art.width * 3, art.height * 3), Image.LANCZOS).save(os.path.join(refs, "6_alune_art.png"))
    guide(full["1_alune_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: riding the crescent, 3/4; horn top to the crescent's lowest tip ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(full["7_alune_standing"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: standing, glaive upright; glaive top to soles ~{B_SQUARES * SQ} px ({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "alune", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
