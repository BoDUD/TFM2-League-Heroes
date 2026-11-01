"""Build the step-0 pack for Codex (assets/source/meepsie/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_meepsie_picture.py --out D:/TFM2-Workshop/meepsie_packs/meepsie_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Sentinel, Krug, Terra and Ivern, 8x,
cut from their sheets), then <out>.zip.
Meepsie (小木灵, a tft pack hero, 2026-11-01) is set 17's 2-cost Meeple / Shepherd / Voyager (TFT17_IvernMinion, APFighter,
ability 宇宙大爆炸 The Big Bang): a big moon-rock golem - pale blue-white cratered rock boulders for the chest, shoulders and
fists, dark indigo rock legs and forearms, purple trims and a purple belt, a cap of green leaves and purple mushrooms on its
top and back - piloted by a small green meep (antennae, big black eyes) who sits in a round crater cockpit high on its
chest. TFTSet17.wad.client tft17_ivernminion_17.skn + .skl (87 joints: the golem's humanoid skeleton, Flower_A-C,
Meep_* for the pilot), one colour map. Its animation bin links ten clips by path hash only: CLIPS below names them by what
they show (rendered and read by eye, 2026-11-01). Two pictures at one square size: A = the idle at 3/4; B = the idle
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
WAD = ("Game", "DATA", "FINAL", "TFTSet17.wad.client")
CHAR = "assets/characters/tft17_ivernminion/skins/base/"
SKN, SKL = CHAR + "tft17_ivernminion_17.skn", CHAR + "tft17_ivernminion_17.skl"
TEX = CHAR + "tft17_ivernminion_base_tx_cm.tex"
CLIPS = {   # path hashes only (data/characters/tft17_ivernminion/animations/skin0.bin), named by what they show
    "idle": 1856546103226341009,       # 6.67 s: standing, fists low at its sides, the meep looking out of the cockpit
    "idle2": 6878984456181345223,      # 1.67 s: a hunched idle, leaning forward
    "run": 16529955601862501921,       # 1.30 s: a lumbering walk
    "attack": 5803710254584196060,     # 2.03 s: an arm up (~450 ms), a punch down (~700-900 ms)
    "attack2": 9343878069632924081,    # 2.03 s: an overhead smash
    "crouch": 13086669243409484763,    # 0.30 s: crouched low
    "death": 4655428051062738740,      # 1.17 s: falls forward on its face
    "fist": 5546218531107833431,       # 0.53 s: a fist raised high, looping
    "slam": 17335348994647646797,      # 2.17 s: both arms overhead (~480 ms), a slam down (~720-1200 ms)
    "spell": 6373782339399518719,      # 3.60 s: leaps off (~400-800 ms out of view), lands in a slam (~1200-2000 ms)
}
SQ = 11
SOLE = 1390
A_SQUARES = 40   # A: the top of its mushroom cap to its soles
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_meepsie_34": (35, "box", "idle@0"),
    "2_meepsie_front": (0, "box", "idle@0"),
    "3_meepsie_meep": (30, "head", "idle@0"),        # the meep pilot in its crater cockpit
    "4_meepsie_side": (85, "box", "idle@0"),         # B: the same idle side-on
    "5_meepsie_back": (180, "box", "idle@0"),        # the leaves and mushrooms on its back
    "6_meepsie_meep_front": (0, "head", "idle@0"),
    "7_meepsie_punch": (35, "box", "attack@900"),    # a punch: ONLY how big the fists are next to it
    "8_meepsie_slam": (35, "box", "slam@480"),       # both arms overhead: ONLY the arms and fists
    "9_meepsie_top": (35, "box", "attack@1128"),     # bent forward: ONLY the leaf and mushroom cap from above
}
HEAD_JOINTS = ("Meep_Root", "Meep_Chest", "Meep_Head", "Meep_Hair", "Meep_Hair1", "Meep_Hair2", "Meep_L_Eye", "Meep_R_Eye",
               "Meep_L_Shoulder", "Meep_L_Hand", "Meep_R_Shoulder", "Meep_R_Hand", "Meep_L_Hip", "Meep_L_Knee",
               "Meep_R_Hip", "Meep_R_Knee")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_sentinel.png": (TFT, "tft_sentinel", "hd_idle"),
    "12_style_krug.png": (TFT, "tft_krug", "hd_idle"),
    "13_style_terra.png": (TFT, "tft_terra", "hd_idle"),
    "14_style_ivern.png": (CHAMPS, "league_ivern", "hd_idle"),
}
class Model:
    """Its mesh on its own skeleton, one colour map; `head` marks the vertices the meep pilot's joints carry most."""

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
    fa = full["1_meepsie_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: idle, 3/4; mushroom cap to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_meepsie_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "meepsie", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
