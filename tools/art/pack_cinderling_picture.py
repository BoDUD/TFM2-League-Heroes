"""Build the step-0 pack for Codex (assets/source/cinderling/PICTURE_PROMPT.md): TFT model references, layout guides
and style pictures.

    python tools/art/pack_cinderling_picture.py --out D:/TFM2-Workshop/cinderling_packs/cinderling_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Crimson Brambleback, Meepsie, Murk Wolf
and Ivern, 8x, cut from their sheets), then <out>.zip.
The Cinderling (绯红树怪, a tft pack hero, 2026-11-02) is set 18's 1-cost Rift Monster / Hunter (DA_Cinderling18, ability
刃叶 Razor Leaves): the Red Brambleback's little one - a squat four-legged critter of dark brown-black bark, its front
paws and back feet tipped with dark claws, a big WOODEN MASK for a face (warm brown bark plates, an orange spiral carved
on the brow, glowing red-orange eyes, a jagged glowing mouth), a mane of tall green leaves standing up like spikes along
its back, mossy green patches on its shoulders. TFTSet18.wad.client tft18_cinderling.skn + .skl (one submesh lambert3,
73 joints: four legs, Head, Jaw, L/R_Mask, L/R/C_Leaf1-2, Tail1); the skin borrows SRU_RedMini. Its skin bin
(data/characters/da_cinderling18/skins/skin0.bin) gives the colour map by path hash only, its animation bin seven clips
by path hash only: CLIPS below names them by what they show (rendered and read by eye, 2026-11-02). It has NO run clip.
Two pictures at one square size: A = TFT's own idle at 3/4, leaves up; B = the same idle side-on facing right. The user
picks one.
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
CHAR = "assets/characters/tft18_cinderling/skins/base/"
SKN, SKL = CHAR + "tft18_cinderling.skn", CHAR + "tft18_cinderling.skl"
TEX = 3430592831157173216   # the colour map: no path in the skin bin, only this hash (512 x 512)
CLIPS = {   # path hashes only (data/characters/da_cinderling18/animations/skin0.bin); named by what they show
    "idle": 3896288373748851414,          # 4.00 s: crouched on all fours; the leaf mane stands up, lies down, stands up
    "idle2": 4077248461602483578,         # 2.00 s: crouched, the leaf mane up the whole time
    "attack": 13222769210799313850,       # 1.67 s: crouches, hops forward with the leaves flung up (~620 ms), lands
    "attack2": 6487722580226075904,       # 1.67 s: the same as attack
    "rear": 29579516087819070,            # 0.90 s: rears up on its back legs, front paws out (anmd)
    "spawn": 17901162839825691832,        # 2.00 s: buried, bursts up out of the ground (~1250 ms), lands
    "death": 11055278892440438250,        # 2.00 s: flips over on to its back and lies there
}
SQ = 11
SOLE = 1390
A_SQUARES = 32   # A: the tip of the tallest leaf to the claws on the ground
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_cinderling_34": (40, "box", "idle@0"),
    "2_cinderling_front": (0, "box", "idle@0"),
    "3_cinderling_head": (40, "head", "idle@0"),          # the wooden mask: the brow spiral, the eyes, the mouth
    "4_cinderling_side": (85, "box", "idle@0"),           # B: the same idle side-on
    "5_cinderling_back": (160, "box", "idle@0"),          # the back: the leaf mane, the moss
    "6_cinderling_head_front": (0, "head", "idle@0"),
    "7_cinderling_hop": (80, "box", "attack@624"),        # the hop forward, leaves flung up: only the body and the legs
    "8_cinderling_rear": (40, "box", "rear@562"),         # reared up on its back legs: only how it stands up
    "9_cinderling_leaves_down": (40, "box", "idle@2000"),  # the leaves lying down: how the mane folds
}
HEAD_JOINTS = ("Head", "Jaw", "L_Mask", "R_Mask")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_brambleback.png": (TFT, "tft_brambleback", "hd_idle"),
    "12_style_meepsie.png": (TFT, "tft_meepsie", "hd_idle"),
    "13_style_murkwolf.png": (TFT, "tft_murkwolf", "hd_idle"),
    "14_style_ivern.png": (CHAMPS, "league_ivern", "hd_idle"),
}


class Model:
    """Its mesh on its own skeleton, one colour map; `head` marks the vertices its mask and jaw carry most."""

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
    "head" crops round the mask."""
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
    if crop == "head":   # the projected box of the mask's own vertices (render_hq's transform), mirrored
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
    fa = full["1_cinderling_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; tallest leaf to the claws on the ground ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_cinderling_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "cinderling", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
