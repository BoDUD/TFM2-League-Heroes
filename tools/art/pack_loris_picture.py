"""Build the step-0 pack for Codex (assets/source/loris/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_loris_picture.py --out C:/t/lo_work/loris_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips, the unit art and
the layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Braum, Jayce, Caitlyn and
Silco, 8x, cut from their sheets), then <out>.zip.
Loris (the tft pack's sixth hero, 2026-10-27) is the bearded Piltover enforcer with the great tower shield from Arcane,
a 3-cost of Teamfight Tactics set 16 (TFT16_Loris, 皮尔特沃夫 / 神盾使; set 13's TFT13_Beardy before). His model is in
the Riot client's TFTSet16.wad.client: TFT16_Loris_16.skn + .skl, one colour map, two unnamed submeshes (0 = him,
1 = the shield). His animation bin links its clips by path hash only: CLIPS below names them by what they show
(rendered and read by eye, 2026-10-27).
Two pictures at one square size: A = TFT's own idle (the shield planted on the ground in front of him, his head and
shoulders over it); B = the shield held upright on his far arm at his side, his body free (the pose his attack starts
from). The user picks one.
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
WAD = ("Game", "DATA", "FINAL", "TFTSet16.wad.client")
CHAR = "assets/characters/tft16_loris/skins/base/"
SKN, SKL = CHAR + "tft16_loris_16.skn", CHAR + "tft16_loris_16.skl"
TEX = CHAR + "tft16_loris_base_tx_cm.tex"
BODY, SHIELD = 0, 1      # submesh indices (the skn leaves their names empty)
CLIPS = {
    "attack": 10680338520223139564,      # 1.73 s: the shield swung round from his side, a fist thrown over it
    "attack2": 1183213148910997707,      # 1.80 s: crouched behind the shield, swept across in front of him
    "death": 11171404641411295609,       # 1.53 s: the shield dropped, he falls
    "run": 15324113982854757819,         # 1.13 s: a heavy jog, the shield carried at his side
    "idle": 2958271957709796360,         # 3.00 s: the shield planted in front, arms crossed over its top
    "spell": 14255222247491399669,       # 0.83 s: the shield slammed forward, then planted
    "charge": 3008479304577312229,       # 0.53 s: running behind the raised shield
    "charge_end": 16552090908063375930,  # 0.50 s: from the charge back to the idle
    "dance": 6492246160559248704,        # 0.93 s: the celebration kicks (not used)
}
SQ = 11
SOLE = 1390
A_SQUARES = 58   # A: the top of his hair to his soles
B_SQUARES = 58   # B: the same body, the shield at his side
# name -> (yaw, crop "box" / "head", clip@ms, hidden submeshes)
RENDERS = {
    "1_loris_34": (35, "box", "idle@0", set()),
    "2_loris_front": (0, "box", "attack@0", set()),           # the body seen whole, the shield off to the side
    "3_loris_head": (20, "head", "attack@0", {SHIELD}),
    "4_loris_body": (35, "box", "idle@0", {SHIELD}),           # the body behind the planted shield
    "5_loris_back": (180, "box", "idle@0", set()),
    "7_loris_shield": (0, "box", "idle@0", {BODY}),            # the shield alone, its face
    "8_loris_side": (35, "box", "attack@0", set()),            # B: the shield upright at his side
    "9_loris_charge": (35, "box", "charge@250", set()),        # his charge: how big the shield is held up
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_braum.png": (CHAMPS, "league_braum", "hd_idle"),
    "12_style_jayce.png": (CHAMPS, "league_jayce", "hd_idle"),
    "13_style_caitlyn.png": (CHAMPS, "league_caitlyn", "hd_idle"),
    "14_style_silco.png": (TFT, "tft_silco", "hd_idle"),
}


def drop(tris, subs, hide):
    """The triangles of the submeshes not in `hide` (by index: the names are empty)."""
    return np.concatenate([tris[si // 3:(si + ic) // 3] for i, (_n, si, ic) in enumerate(subs) if i not in hide])


class Model:
    """His mesh on his own skeleton, one colour map."""

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
    tris = drop(m.tris, m.subs, hide)
    if crop == "head":
        size *= 2
    im = pose_ref.render_hq(pv, tris, m.v["uv"], m.tex, -yaw, 12, (size, size), size * 0.7 / h,
                            size * 0.86).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # hair, headband, face, beard, collar: the top 22% of him
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
    ap.add_argument("--art", default=r"C:\t\lo_work\tft13_beardy_mobile.png",
                    help="the unit's art (CommunityDragon latest, tft13_beardy/skins/base/images/tft13_beardy_mobile.png;"
                         " set 16's own splash is only 256 px)")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    m = Model(a.lol)
    full = {name: render(m, name, spec, refs) for name, spec in RENDERS.items()}
    art = Image.open(a.art).convert("RGB")
    art.resize((art.width * 2, art.height * 2), Image.LANCZOS).save(os.path.join(refs, "6_loris_art.png"))
    guide(full["1_loris_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, the shield planted in front, 3/4; hair top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(full["8_loris_side"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: the shield upright at his side; hair top to soles ~{B_SQUARES * SQ} px ({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "loris", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
