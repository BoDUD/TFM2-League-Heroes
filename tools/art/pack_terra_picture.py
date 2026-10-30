"""Build the step-0 pack for Codex (assets/source/terra/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_terra_picture.py --out D:/TFM2-Workshop/terra_packs/terra_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Idas, Sy'fen, Shi Oh Yu and Nomsy,
8x, cut from their sheets), then <out>.zip.
Terra (泰拉, the tft pack's twenty-third hero, 2026-10-31) is set 7's 5-cost Monolith / Dragon tank (TFT7_DragonEarth,
ability 地震 Earthquake): a FOUR-LEGGED EARTH DRAGON - a mossy green rock back and head, a brown underside and legs,
orange wing membranes folded at her sides, a dark tail ending in a rock club, yellow eyes. TFTSet7.wad.client
tft7_dragonearth.skn + .skl (106 joints: Spine1-4, Neck/Neck1/Head + Jaw + gills, L/R_Paw front legs, L/R_Hip hind legs,
Tail1-6, wings L/R_Wing_* with four WingFing each); her clips are linked by path hash: idle is
animations/idle.anm (no prefix), the others animations/tft7_dragonearth_<name>.anm, and one 2.0 s clip with no known
name (a low lunging bite). Two pictures at one square size: A = TFT's own idle (wings folded, crouched) at 3/4;
B = the same idle turned to the side (side-on, facing right). The user picks one.
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
WAD = ("Game", "DATA", "FINAL", "TFTSet7.wad.client")
CHAR = "assets/characters/tft7_dragonearth/skins/base/"
SKN, SKL, TEX = (CHAR + "tft7_dragonearth.skn", CHAR + "tft7_dragonearth.skl",
                 CHAR + "tft7_dragonearth_base_tx_cm.tex")
CLIPS = {   # path hashes from her animation bin (assets/characters/tft7_dragonearth/skins/base/animations/...)
    "idle": 8644172206544828823,          # idle.anm 3.0 s: crouched on four legs, wings folded at her sides, tail behind
    "run": 3094192283162194282,           # tft7_dragonearth_run 2.33 s: she FLIES, the wings beating
    "attack": 8682691624062354565,        # _attack1 2.0 s: stands up, wings spread, the head rises, tail club up
    "bite": 1352555594545409976,          # 2.0 s, name unknown: wings spread, the head drops low, the jaw open
    "spell": 14989306320753717206,        # _spell 3.0 s: rears up and stomps (Earthquake)
    "death": 6722602106483199574,         # _death 8.47 s
    "celebration": 3351176266373766361,   # _celebration 4.07 s: rises from the crouch and spreads the wings
}
SQ = 11
SOLE = 1390
A_SQUARES = 40   # A: the top of the folded wings / the head to the soles (her idle is much wider than tall)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_terra_34": (35, "box", "idle@0"),
    "2_terra_front": (0, "box", "idle@0"),
    "3_terra_head": (35, "head", "idle@0"),
    "4_terra_side": (80, "box", "idle@0"),            # B: the same idle side-on
    "5_terra_back": (180, "box", "idle@0"),           # the back: the rock plates, the folded wings, the tail and its club
    "6_terra_head_side": (90, "head", "idle@0"),
    "7_terra_wings": (35, "box", "attack@1000"),      # wings spread: only how the wing arms, fingers and membranes are built
    "8_terra_fly": (80, "box", "run@0"),              # she flies: only the wings and the tail in the air
    "9_terra_tail": (100, "box", "attack@0"),         # side-on, the tail raised high: only the tail and its rock club
}
HEAD_JOINTS = ("Head", "Jaw", "L_Gill1", "L_Gill2", "L_Gill3", "R_Gill1", "R_Gill2", "R_Gill3")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_idas.png": (TFT, "tft_idas", "hd_idle"),
    "12_style_syfen.png": (TFT, "tft_syfen", "hd_idle"),
    "13_style_shiohyu.png": (TFT, "tft_shiohyu", "hd_idle"),
    "14_style_nomsy.png": (TFT, "tft_nomsy", "hd_idle"),
}
class Model:
    """Her mesh on her own skeleton, one colour map; `head` marks the vertices her head carries most."""

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
    "head" crops round her head."""
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
    fa = full["1_terra_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; top to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_terra_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "terra", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
