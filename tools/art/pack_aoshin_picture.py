"""Build the step-0 pack for Codex (assets/source/aoshin/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_aoshin_picture.py --out C:/t/ao_work/aoshin_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Aurelion Sol, Shyvana's dragon, Volibear
and Krug, 8x, cut from their sheets), then <out>.zip.
Ao Shin (敖兴, the tft pack's twelfth hero and the first of set 7, 2026-10-28) is set 7's 5-cost Tempest / Dragon mage
(TFT7_AoShin): a serpent-bodied storm dragon in cyan scales, a gold horned mask over the face, gold and brown armour on
the chest and shoulders, blue clawed hands, two small hind legs and a long spiked tail; he hovers, never walks.
TFTSet7.wad.client tft7_aoshin.skn + .skl (104 joints), one colour map; its animation bin
(data/characters/tft7_aoshin/animations/skin0.bin) links its clips by path hash only: CLIPS below names them by what
they show (rendered and read by eye, 2026-10-28). No unit art in the client: the head close-ups stand in for it.
Two pictures at one square size: A = TFT's own idle (hovering upright, the tail curled under him); B = his attack's
lunge (the body leaning forward, the claws out, the jaw open). The user picks one.
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
CHAR = "assets/characters/tft7_aoshin/skins/base/"
SKN, SKL = CHAR + "tft7_aoshin.skn", CHAR + "tft7_aoshin.skl"
TEX = CHAR + "tft7_aoshin_base_tx_cm.tex"
CLIPS = {
    "attack": 10076759650309673864,      # 0.67 s: a lunge forward, the claws and the jaw first
    "attack2": 5107744909032693866,      # 0.67 s: the same lunge, the other side
    "attack3": 6283108413356127956,      # 0.67 s: the same lunge again
    "run": 450512938564156409,           # 0.53 s: flies forward, the body low and long
    "spell": 10838584927521685892,       # 1.33 s: rears up, the arms spread, calls the storm
    "spell_loop": 12962086268276459415,  # 9.00 s: hovers upright, arms out, sways (the barrage's channel)
    "idle": 13789440517452193812,        # 6.00 s: hovers upright, the tail curled under him, breathing
    "death": 16160367859219638880,       # 3.03 s: tips back and falls, the tail last
    "idle2": 1534384414361311339,        # 3.97 s: an idle variation (looks round)
    "idle3": 17986791870736877451,       # 3.97 s: an idle variation
    "celebrate": 9515899634868409338,    # 4.27 s: rears up and spins
}
SQ = 11
SOLE = 1390
A_SQUARES = 52   # A: the tip of his horns to the lowest curl of his tail (about as wide as tall)
# B is drawn at A's body scale: its height in squares follows from the model's own heights (main())
A_POSE, B_POSE = "idle@0", "attack@190"
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_aoshin_34": (35, "box", A_POSE),
    "2_aoshin_front": (0, "box", A_POSE),
    "3_aoshin_head": (35, "head", A_POSE),          # the gold mask, the horns, the eyes, the cyan mane
    "4_aoshin_lunge": (35, "box", B_POSE),          # B: lunging forward, the claws out
    "5_aoshin_back": (180, "box", A_POSE),
    "6_aoshin_head_front": (0, "head", A_POSE),     # the mask from the front: the brow crest, both eyes, the jaw
    "7_aoshin_side": (90, "box", A_POSE),           # side view: how the body curls, where the arms, legs and tail are
    "8_aoshin_lunge_side": (90, "box", B_POSE),     # B from the side: the long body, the head forward
}
HEAD_JOINTS = ("Head", "Jaw", "Jaw_Upper", "L_Horn", "R_Horn", "Hair_Front")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_aurelionsol.png": (CHAMPS, "league_aurelionsol", "hd_idle"),
    "12_style_shyvana_dragon.png": (CHAMPS, "league_shyvana", "hd_d_idle"),
    "13_style_alune.png": (TFT, "tft_alune", "hd_idle"),
    "14_style_krug.png": (TFT, "tft_krug", "hd_idle"),
}


class Model:
    """His mesh on his own skeleton, one colour map; `head` marks the vertices his head, jaw and horns carry most."""

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
    "head" crops round his head, jaw and horns."""
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
    ha, hb = (np.ptp(m.posed(c)[:, 1]) for c in (A_POSE, B_POSE))
    b_squares = round(A_SQUARES * hb / ha)
    print("model heights A", round(ha, 1), "B", round(hb, 1), "-> B squares", b_squares)
    guide(full["1_aoshin_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: TFT idle, hovering upright, 3/4; horns to tail ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_aoshin_lunge"], os.path.join(refs, "10b_layout_B.png"), b_squares,
          f"B: the attack's lunge, 3/4; top to bottom ~{b_squares * SQ} px ({b_squares} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "aoshin", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
