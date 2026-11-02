"""Build the step-0 pack for Codex (assets/source/thex/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_thex_picture.py --out D:/TFM2-Workshop/thex_packs/thex_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Elder Dragon, Rumble, Corki and
Crimson Raptor, 8x, cut from their sheets), then <out>.zip.
T-Hex (海克斯霸龙, a tft pack hero, 2026-11-02) is set 16's 5-cost HexMech / Piltover / Gunslinger unit (TFT16_THex,
ability 海克斯军械库 Hex Armory): a MECHANICAL T-REX - a dark navy-indigo robot body under COPPER armour plates, glowing
blue hextech panels and back spikes, a copper dinosaur helmet with two ear spikes, a toothy steel-blue jaw, blue eyes,
a GATLING GUN for one forearm (six barrels) and a clawed hand for the other, round gear joints at the hips, bird-like
clawed feet and a long armoured tail. TFTSet16.wad.client TFT16_THex_16.skn + .skl (89 joints; one submesh THex_Mat;
back covers L/R_Back_Cover1-3 open into missile pods). Its colour map and its eleven clips are linked by path hash
only; CLIPS below names them by what they show (rendered and read by eye, 2026-11-02). No unit art in the client: the
head close-ups stand in for it.
Two pictures at one square size: A = TFT's own idle (3/4, crouched, gun forward); B = the Hex Armory channel (the back
pods opened, the gun levelled). The user picks one.
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
CHAR = "assets/characters/tft16_thex/skins/base/"
SKN, SKL = CHAR + "tft16_thex_16.skn", CHAR + "tft16_thex_16.skl"
TEX = 12334908817254655355   # the skin bin's colour map, by path hash (512x512)
CLIPS = {   # path hashes only, named by what they show
    "idle": 8824798696755058735,       # 1.67 s: crouched, gun forward, breathing
    "idle2": 6790700784585736673,      # 1.67 s: the same with a head turn
    "run": 225055398918181973,         # 1.27 s: a forward-leaning bird-legged run, the tail level
    "attack": 6639678528991159503,     # 1.33 s: the gatling fires (body still, recoil)
    "spin": 4845118006930316524,       # 1.33 s: turns round on the spot, the tail sweeping
    "roar": 11802141918013670684,      # 1.40 s: rears up, the head thrown back (~800 ms)
    "channel": 1080708404105021354,    # 9.53 s: the back covers open into missile pods (~1500-8000 ms), gun levelled
    "channel2": 2455363994061899013,   # 4.33 s: a shorter pods-open loop
    "rise": 18099682950806658713,      # 0.33 s: crouched low -> standing (the pilot jumps in)
    "stand": 6979413861517350419,      # 6.67 s: upright, gun held out (a bench idle)
    "celebrate": 8199052082347386287,  # 2.00 s: rears upright and turns
    "death": 15915147689421067274,     # 3.67 s: staggers and collapses on its side
}
SQ = 11
SOLE = 1390
A_SQUARES = 46   # A: the helmet's ear spikes to its soles
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_thex_34": (35, "box", "idle@0"),           # A: TFT's idle, 3/4
    "2_thex_front": (0, "box", "idle@0"),         # front: helmet, jaw, the gun and the claw hand
    "3_thex_head": (25, "head", "idle@0"),        # the head close-up: helmet, eyes, teeth
    "4_thex_pods": (35, "box", "channel@3177"),   # B: the back pods open, gun levelled
    "5_thex_back": (180, "box", "idle@0"),        # the back: the spikes, the back covers, the tail
    "6_thex_head_front": (0, "head", "idle@0"),   # the face from the front: both eyes
    "7_thex_side": (90, "box", "idle@0"),         # true side: how long the tail is, the gatling's barrels
    "8_thex_roar": (35, "box", "roar@800"),       # ONLY how it rears and roars
    "9_thex_run": (35, "box", "run@420"),         # ONLY how it runs
}
HEAD_JOINTS = ("Head", "Jaw")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_elderdragon.png": (TFT, "tft_elderdragon", "hd_idle"),
    "12_style_rumble.png": (CHAMPS, "league_rumble", "hd_idle"),
    "13_style_corki.png": (CHAMPS, "league_corki", "hd_idle"),
    "14_style_raptor.png": (TFT, "tft_raptor", "hd_idle"),
}


class Model:
    """Its mesh on its own skeleton, one colour map; `head` marks the vertices its head and jaw carry most."""

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
    "head" crops round its head."""
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
    ima, sa = full["1_thex_34"]
    k = A_SQUARES * SQ / (ima.getbbox()[3] - ima.getbbox()[1])
    guide(ima, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; ear spikes to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    imb, sb = full["4_thex_pods"]
    guide(imb, os.path.join(refs, "10b_layout_B.png"), k * sa / sb,
          "B: back pods open, gun levelled, the SAME body scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "thex", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
