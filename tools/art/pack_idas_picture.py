"""Build the step-0 pack for Codex (assets/source/idas/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_idas_picture.py --out D:/TFM2-Workshop/idas_packs/idas_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Shyvana in dragon form, Galio, Ao Shin
and Nomsy, 8x, cut from their sheets), then <out>.zip.
Idas (艾达丝, the tft pack's eighteenth hero, 2026-10-30) is set 7's 4-cost Shimmerscale / Dragon / Guardian tank
(TFT7_DragonGold, ability 黄金龙鳞 Golden Scales): a golden dragon standing UPRIGHT on two digitigrade legs, her wings
grown on her arms (a clawed hand at each wing's wrist), gold faceted scale armour over a dark brown body, a long tail
ending in a curved blade, a cyan crest on her horned head. TFTSet7.wad.client tft7_dragongold.skn + .skl (56 joints,
Shyvana's dragon rig: l_wing / R_Wing on the hands, Tail_a..g), one colour map; her clips are linked by path
(animations/tft7_dragongold_<name>.anm, found 2026-10-30). Two pictures at one square size: A = TFT's own idle at 3/4;
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
CHAR = "assets/characters/tft7_dragongold/skins/base/"
SKN, SKL = CHAR + "tft7_dragongold.skn", CHAR + "tft7_dragongold.skl"
TEX = CHAR + "tft7_dragongold_base_tx_cm.tex"
CLIPS = {   # animations/tft7_dragongold_<name>.anm
    "idle": 4024780355865970163,         # 3.33 s: upright, knees bent, the wing-arms hanging forward, the tail curled behind
    "run": 10647197814858116021,         # 0.67 s: a low glide, the wings spread
    "attack1": 2904218791960871564,      # 1.00 s: wings flung wide, then a lunging claw swipe
    "attack2": 8003095587599825519,      # 1.00 s: a spinning wing slash
    "death": 2538740090046230419,        # 3.00 s: rears up, collapses on her side
    "celebration": 17368986247314000247, # 3.73 s: wings spread wide, a roar
    "crouch": 9022013867775355442,       # 9.00 s, no name in her bins: from the idle down into a crouch, wings in front
    "crouch_loop": 11273100081070397211, # 1.00 s, no name: crouched, the wings folded in front of her face
}
SQ = 11
SOLE = 1390
A_SQUARES = 50   # A: the crest to her soles (TFT's idle stands about 0.9x as wide as tall)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_idas_34": (35, "box", "idle@0"),
    "2_idas_front": (0, "box", "idle@0"),
    "3_idas_head": (35, "head", "idle@0"),
    "4_idas_side": (80, "box", "idle@0"),             # B: the same idle side-on
    "5_idas_back": (180, "box", "idle@0"),            # the back, the folded wing membranes, the tail
    "6_idas_head_side": (90, "head", "idle@0"),
    "7_idas_wings": (20, "box", "celebration@1244"),  # the wings spread: only how the wings are made
    "8_idas_claws": (35, "box", "attack1@166"),       # the arms flung wide: only the clawed hands at the wing wrists
    "9_idas_profile": (90, "box", "idle@0"),          # straight from the side: the tail's length and its blade
}
HEAD_JOINTS = ("head", "jaw")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_shyvana_dragon.png": (CHAMPS, "league_shyvana", "hd_d_idle"),
    "12_style_galio.png": (CHAMPS, "league_galio", "hd_idle"),
    "13_style_aoshin.png": (TFT, "tft_aoshin", "hd_idle"),
    "14_style_nomsy.png": (TFT, "tft_nomsy", "hd_idle"),
}


class Model:
    """Her mesh on her own skeleton, one colour map; `head` marks the vertices her head and jaw carry most."""

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
    "head" crops round her head and jaw (at her front: the tail can be the top of the figure)."""
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
    fa = full["1_idas_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle standing upright, 3/4; crest to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ});"
          " layout only")
    guide(full["4_idas_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "idas", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
