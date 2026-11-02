"""Build the step-0 pack for Codex (assets/source/mightymech/PICTURE_PROMPT.md): TFT model references, layout guides
and style pictures.

    python tools/art/pack_mightymech_picture.py --out D:/TFM2-Workshop/mightymech_packs/mightymech_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's T-Hex, Galio, Rumble and Camille, 8x,
cut from their sheets), then <out>.zip.
The Mighty Mech (超级机甲, a tft pack hero, 2026-11-03) is set 17's 4-cost Mecha / Voyager unit (TFT17_Galio, ability
引力矩阵 Gravity Matrix; Mecha units transform into an Ultimate form): a RED, SILVER and BLACK SUPER ROBOT - a small
helmeted head with a V crest and yellow eyes, a broad red chest with a hexagonal core, a SILVER LION-HEAD shoulder
plate, big blocky fists, red armoured shins, a black whip tail, and a fan of RED BLADE-WINGS on its back; its Ultimate
form draws a GIANT RED-AND-SILVER SWORD (glowing orange core).
TFTSet17.wad.client TFT17_Galio_17.skn + .skl (85 joints, ten submeshes; the skin bin hides "Sword" until a clip shows
it). Its colour map and its twenty clips are linked by path hash only; CLIPS below names the ones used by what they show
(rendered and read by eye, 2026-11-03). Clip roots differ: the yaws below are by eye, the 3/4 facing right.
No unit art in the client: the head and chest close-ups stand in for it.
Two pictures at one square size: A = the normal form standing (3/4, no sword); B = the Ultimate form holding the
giant sword forward. A is the game look, B the sword the ult draws (and a candidate look). The user picks.
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
WAD = ("Game", "DATA", "FINAL", "TFTSet17.wad.client")
CHAR = "assets/characters/tft17_galio/skins/base/"
SKN, SKL = CHAR + "tft17_galio_17.skn", CHAR + "tft17_galio_17.skl"
TEX = 6132341876412541033   # the skin bin's colour map, by path hash (512x512)
CLIPS = {   # path hashes only, named by what they show
    "idle_crouch": 15941245260434065807,  # 2.00 s: a crouched fighting idle
    "stand": 1786330062792952226,         # 3.00 s: stands tall, fists down, wings fanned behind (our idle)
    "punch": 11061586702332699475,        # 0.97 s: a two-fisted punch (~200 wind-up, ~400 hit)
    "stance": 5327156661758399621,        # 2.63 s: Gravity Matrix - wings spread round it, braced
    "leap": 1204604533815365710,          # 1.57 s: crouches and leaps up out of sight
    "land": 18369402489358106289,         # 1.77 s: comes down and lands
    "swing": 13908815542147322937,        # 1.67 s: a sword swing (~554 raised)
    "sword_idle": 6343491170590145789,    # 1.13 s: the Ultimate form idle, the giant sword held forward
    "summon": 3704933640300576163,        # 2.80 s: the sword falls from the sky into its raised hand (~466-932)
    "transform": 2796505497128703427,     # 1.97 s: transforms, the blade-wings flare out (~982)
    "death": 6865834360333618748,         # 1.00 s: falls apart
}
SQ = 11
SOLE = 1390
A_SQUARES = 46   # A: the wing tips to the soles
# name -> (yaw, crop "box" / joints to crop round, clip@ms, sword shown)
RENDERS = {
    "1_mech_34": (0, "box", "stand@0", False),           # A: standing, 3/4
    "2_mech_front": (-35, "box", "stand@0", False),      # front: chest core, both shoulders, fists
    "3_mech_head": (0, ("Head", "Neck"), "stand@0", False),     # the head close-up: helmet, V crest, yellow eyes
    "4_mech_sword": (20, "box", "sword_idle@500", True),  # B: the Ultimate form with the giant sword
    "5_mech_back": (145, "box", "stand@0", False),       # the back: the blade-wings
    "6_mech_chest": (-35, ("Spine3", "L_ClaviclePad", "R_ClaviclePad", "L_ShoulderPad", "R_ShoulderPad"),
                     "stand@0", False),                  # the chest close-up: the core, the lion shoulder
    "7_mech_side": (-90, "box", "stand@0", False),       # true side: how deep the chest and the wings are
    "8_mech_summon": (0, "box", "summon@700", True),     # ONLY how it raises its hand for the sword
    "9_mech_stance": (0, "box", "stance@876", False),    # ONLY how the wings spread in its stance
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_thex.png": (TFT, "tft_thex", "hd_idle"),
    "12_style_galio.png": (CHAMPS, "league_galio", "hd_idle"),
    "13_style_rumble.png": (CHAMPS, "league_rumble", "hd_idle"),
    "14_style_camille.png": (CHAMPS, "league_camille", "hd_idle"),
}


class Model:
    """Its mesh on its own skeleton, one colour map; the sword only when a render asks for it."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.no_sword = pose_ref.drop_submeshes(self.tris, pose_ref.skn_submeshes(b), {"Sword"})
        self.tex = pose_ref.read_tex(self.w.read(TEX))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(SKL))
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]
        self.names = [j["name"] for j in self.joints]
        self.top = np.array(self.infl)[self.v["bones"].astype(np.int64)][np.arange(len(self.v)),
                                                                          np.argmax(self.v["w"], axis=1)]

    def part(self, joints):
        return np.isin(self.top, [self.names.index(n) for n in joints])

    def posed(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        return pose_ref.skin(self.v, self.infl, self.bind_inv, glob)


def render(m, name, spec, out, size=1600):
    """A mirrored render facing image right, the figure 70% of the cell (its height or its width), on grey. A joint
    list crops round the vertices those joints carry most."""
    yaw, crop, clip, sword = spec
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    span = max(np.ptp(pv[:, 1]), np.hypot(np.ptp(pv[:, 0]), np.ptp(pv[:, 2])))
    if crop != "box":
        size *= 2
    scale, ground = size * 0.7 / span, size * 0.86
    im = pose_ref.render_hq(pv, m.tris if sword else m.no_sword, m.v["uv"], m.tex, -yaw, 12, (size, size), scale,
                            ground).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    if crop != "box":   # the projected box of the part's own vertices (render_hq's transform), mirrored
        cy, sy = np.cos(np.radians(-yaw)), np.sin(np.radians(-yaw))
        cp, sp = np.cos(np.radians(12)), np.sin(np.radians(12))
        rot = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        v = pv[m.part(crop)] @ rot.T
        xs, ys = size - (v[:, 0] * scale + size * 0.5), ground - v[:, 1] * scale
        mg = (xs.max() - xs.min()) * (0.9 if len(crop) < 3 else 0.35)   # the small head gets more room
        box = (int(xs.min() - mg), int(ys.min() - mg), int(xs.max() + mg), int(ys.max() + mg))
        cut_ = can.crop(box)
        can = Image.new("RGBA", cut_.size, GREY + (255,))   # past the render's edge: grey, not black
        can.alpha_composite(cut_)
    else:
        x0, y0, x1, y1 = im.getbbox()
        mg = max(x1 - x0, y1 - y0) // 12
        can = can.crop((max(0, x0 - mg), max(0, y0 - mg), min(im.width, x1 + mg), min(im.height, y1 + mg)))
    can.convert("RGB").save(os.path.join(out, name + ".png"))
    print(name, can.size)
    return im, scale


def guide(fig_full, name, k, label):
    """The figure at k times its render size, the lowest point on SOLE, centred."""
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
    full = {name: render(m, name, spec, refs) for name, spec in RENDERS.items()}
    ima, sa = full["1_mech_34"]
    k = A_SQUARES * SQ / (ima.getbbox()[3] - ima.getbbox()[1])
    guide(ima, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: standing, 3/4; wing tips to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    imb, sb = full["4_mech_sword"]
    guide(imb, os.path.join(refs, "10b_layout_B.png"), k * sa / sb,
          "B: the Ultimate form with the sword, the SAME body scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "mightymech", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
