"""Build the step-0 pack for Codex (assets/source/krug/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_krug_picture.py --out C:/t/kr_work/krug_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Galio, Skarner, Rammus and Kobuko,
8x, cut from their sheets), then <out>.zip.
The Ancient Krug (远古石甲虫, the tft pack's tenth hero, 2026-10-28) is set 18's 3-cost Rift Monster brawler (DA_Krug18):
a hunched stone beast under a huge sandstone boulder of a back, glowing orange cracks, a small face low at the front
with two pincers. TFTSet18.wad.client tft18_krug.skn + .skl (46 joints), one colour map; its animation bin
(data/characters/da_krug18/animations/skin0.bin) links its seven clips by path hash only: CLIPS below names them by
what they show (rendered and read by eye, 2026-10-28). No unit art in the client: the head close-ups stand in for it.
Two pictures at one square size: A = TFT's own idle (hunched on all fours, the boulder back high); B = reared up on
his hind legs, the forearms raised for a slam (his attack's top). The user picks one.
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
CHAR = "assets/characters/tft18_krug/skins/base/"
SKN, SKL = CHAR + "tft18_krug.skn", CHAR + "tft18_krug.skl"
TEX = CHAR + "tft18_krug_base_tx_cm.tex"
CLIPS = {
    "attack": 517940498216468385,        # 1.63 s: rears up on the hind legs, both forearms high, slams them down
    "attack2": 17236224866499112347,     # 1.63 s: a low lunge forward, the boulder back first
    "attack3": 13876342866451377775,     # 1.63 s: the rear-up slam again
    "run": 5008545310143145245,          # 0.63 s: a heavy bounding gallop on all fours
    "spawn": 15313678053125843736,       # 1.33 s: rolls in curled up as a boulder, unfolds, stands
    "death": 9175045367771708377,        # 3.97 s: sinks, the back boulder cracks and falls apart
    "idle": 11006277501740147080,        # 0.60 s: hunched on all fours, breathing
}
SQ = 11
SOLE = 1390
A_SQUARES = 50   # A: the top of his boulder back to his soles (about as wide as tall)
B_SQUARES = 54   # B: the same body scale reared up (the model stands 185 high reared, 172 in the idle)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_krug_34": (35, "box", "idle@0"),
    "2_krug_front": (0, "box", "idle@0"),
    "3_krug_head": (55, "head", "attack@950"),       # the face, reared up so the boulder does not hide it: eyes, pincers
    "4_krug_rear": (35, "box", "attack@950"),         # B: reared up, the forearms raised
    "5_krug_back": (180, "box", "idle@0"),
    "6_krug_head_front": (0, "head", "attack@950"),   # reared, from the front: the face, the pincers, the belly plates
    "7_krug_side": (90, "box", "idle@0"),             # side view: how far the boulder overhangs, the four limbs
    "8_krug_belly": (0, "box", "attack@950"),         # reared, the front: belly plates and the orange seams
}
HEAD_JOINTS = ("Head", "L_Pincer", "R_Pincer", "L_Pincer2", "R_Pincer2")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_galio.png": (CHAMPS, "league_galio", "hd_idle"),
    "12_style_skarner.png": (CHAMPS, "league_skarner", "hd_idle"),
    "13_style_rammus.png": (CHAMPS, "league_rammus", "hd_idle"),
    "14_style_kobuko.png": (TFT, "tft_kobuko", "hd_idle"),
}


class Model:
    """His mesh on his own skeleton, one colour map; `head` marks the vertices his head and pincers carry most."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.tex = pose_ref.read_tex(self.w.read_path(TEX))
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
    "head" crops round his head and pincers (low at his front: never the top of the figure)."""
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
    guide(full["1_krug_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, hunched on all fours, 3/4; boulder top to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ});"
          " layout only")
    guide(full["4_krug_rear"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: reared up, forearms raised; top to soles ~{B_SQUARES * SQ} px ({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "krug", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
