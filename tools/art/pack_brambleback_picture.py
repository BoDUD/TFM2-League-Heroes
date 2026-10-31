"""Build the step-0 pack for Codex (assets/source/brambleback/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_brambleback_picture.py --out D:/TFM2-Workshop/brambleback_packs/brambleback_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Krug, Maokai, Ivern and Warwick, 8x,
cut from their sheets), then <out>.zip.
The Crimson Brambleback (绯红印记树怪, a tft pack hero, 2026-10-31) is set 18's 4-cost Rift Monster / Berserker
(DA_Brambleback18, ability 猩红之怒 Crimson Fury): the Rift's red-buff beast - a hunched four-limbed hulk of dark
reddish-brown bark plates, two long front arms ending in huge three-clawed hands tipped red, short back legs with red
claws, curling dark branches like antlers on its back, a crown of green leaves round its shoulders, a glowing
red-orange core in its chest (shown when it rears up), a small beaked bark head low at the front with glowing eyes.
TFTSet18.wad.client tft18_brambleback.skn + .skl (one submesh RedBuff_TX, 69 joints); the colour map has no path in the
bins, only its hash; its animation bin links eight clips by path hash only: CLIPS below names them by what they show
(rendered and read by eye, 2026-10-31). Two pictures at one square size: A = TFT's own idle at 3/4; B = the same idle
side-on facing right. The user picks one.
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
CHAR = "assets/characters/tft18_brambleback/skins/base/"
SKN, SKL = CHAR + "tft18_brambleback.skn", CHAR + "tft18_brambleback.skl"
TEX = 5276590769905959617   # the colour map (RedBuff_TX): no path in the bins, only this hash (1024 x 1024)
CLIPS = {   # path hashes only (data/characters/da_brambleback18/animations/skin0.bin); named by what they show
    "idle": 11623886175171599207,         # 2.67 s: crouches on all fours, the claws on the ground, breathing
    "run": 5813951225545438759,           # 1.07 s: a loping four-limbed gallop
    "attack": 12953196681246505397,       # 1.67 s: rises and swipes one clawed arm down and across
    "slam": 2678273373129578508,          # 1.67 s: rears up high on its back legs and slams both claws down
    "leap": 7036908425555712213,          # 1.67 s: springs high into the air and lands crouched
    "death": 10269090642676670285,        # 2.73 s: rears, then collapses flat and sinks away
    "roar": 2203232121449085267,          # 2.87 s: rears up chest out (the red core shows), then crouches low
    "roar2": 16577701067173027686,        # 2.87 s: the same as roar (celebration / spawn)
}
SQ = 11
SOLE = 1390
A_SQUARES = 40   # A: the top of the back branches to the claws on the ground (wider than tall)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_brambleback_34": (35, "box", "idle@0"),
    "2_brambleback_front": (0, "box", "idle@0"),
    "3_brambleback_head": (35, "head", "idle@0"),          # the small beaked bark head and its glowing eyes
    "4_brambleback_side": (85, "box", "idle@0"),           # B: the same idle side-on
    "5_brambleback_back": (180, "box", "idle@0"),          # the back: the branches, the leaves
    "6_brambleback_head_front": (0, "head", "idle@0"),
    "7_brambleback_run": (80, "box", "run@430"),           # the loping gallop, side-on: only how the limbs swing
    "8_brambleback_rear": (35, "box", "roar@700"),         # reared up, chest out: the glowing red core
    "9_brambleback_swipe": (80, "box", "attack@330"),      # one claw raised, side-on: only the arm and the claws
}
HEAD_JOINTS = ("Head",)
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_krug.png": (TFT, "tft_krug", "hd_idle"),
    "12_style_maokai.png": (CHAMPS, "league_maokai", "hd_idle"),
    "13_style_ivern.png": (CHAMPS, "league_ivern", "hd_idle"),
    "14_style_warwick.png": (CHAMPS, "league_warwick", "hd_idle"),
}


class Model:
    """Its mesh on its own skeleton, one colour map; `head` marks the vertices its small head carries most."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.tex = pose_ref.read_tex(self.w.read(TEX))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(SKL))
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]
        names = [j["name"] for j in self.joints]
        heads = {names.index(n) for n in HEAD_JOINTS}
        top = np.array(self.infl)[self.v["bones"].astype(np.int64)][np.arange(len(self.v)), np.argmax(self.v["w"], axis=1)]
        self.head = np.isin(top, list(heads))

    def posed(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        return pose_ref.skin(self.v, self.infl, self.bind_inv, glob)


def render(m, name, spec, out, size=1600):
    """A mirrored 3/4 render facing image right, the figure 70% of the cell (its height or its width), on grey.
    "head" crops round the head."""
    yaw, crop, clip = spec
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    span = max(np.ptp(pv[:, 1]), np.hypot(np.ptp(pv[:, 0]), np.ptp(pv[:, 2])))
    if crop == "head":
        size *= 2
    scale, ground = size * 0.7 / span, size * 0.86
    im = pose_ref.render_hq(pv, m.tris, m.v["uv"], m.tex, -yaw, 12, (size, size), scale,
                            ground).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    if crop == "head":   # the projected box of the head's own vertices (render_hq's transform), mirrored
        cy, sy = np.cos(np.radians(-yaw)), np.sin(np.radians(-yaw))
        cp, sp = np.cos(np.radians(12)), np.sin(np.radians(12))
        rot = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        v = pv[m.head] @ rot.T
        xs, ys = size - (v[:, 0] * scale + size * 0.5), ground - v[:, 1] * scale
        mg = (xs.max() - xs.min()) * 0.35
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
    return im


def guide(fig_full, name, k, label):
    """The figure at k times its render size (A's scale for both), the lowest point on SOLE, centred."""
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
    # A and B are rendered from the same pose at one scale (render() fits the larger of height / horizontal span, the
    # same for both), so one k puts both on A's squares
    full = {name: render(m, name, spec, refs) for name, spec in RENDERS.items()}
    fa = full["1_brambleback_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; back branches to the claws on the ground ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_brambleback_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "brambleback", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
