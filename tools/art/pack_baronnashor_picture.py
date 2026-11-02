"""Build the step-0 pack for Codex (assets/source/baronnashor/PICTURE_PROMPT.md): TFT model references, layout guides
and style pictures.

    python tools/art/pack_baronnashor_picture.py --out D:/TFM2-Workshop/baronnashor_packs/baronnashor_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Rift Herald, Elder Dragon, Cho'Gath and
Rek'Sai, 8x, cut from their sheets), then <out>.zip.
Baron Nashor (纳什男爵, a tft pack hero, 2026-11-03) is set 16's 5-cost Void / Baron Nashor unit (TFT16_BaronNashor,
ability 虚空之怒 Void's Wrath): a huge VOID SERPENT rearing out of the ground - a tall S-curved purple neck with a
TEAL-GREEN segmented belly, a blue-violet armoured head with yellow eyes, ivory fangs and tusks, a crown of big
MAGENTA-tipped crest fins, two small "mini baron" heads on thin side arms, and two clawed arms low on the column.
TFTSet16.wad.client TFT16_BaronNashor_16.skn + .skl (103 joints; one submesh Baron_Mat). Its colour map and its thirteen
clips are linked by path hash only; CLIPS below names them by what they show (rendered and read by eye, 2026-11-03).
The skin bin names two 512 maps: TEX is the first (the familiar purple + teal Baron; the second is a darker variant).
No unit art in the client: the head close-ups stand in for it.
Two pictures at one square size: A = TFT's own idle (3/4, reared up, S-curved neck); B = the Void's Wrath wind-up
(rears up tall, the crest fins raised, before it slams). The user picks one.
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
CHAR = "assets/characters/tft16_baronnashor/skins/base/"
SKN, SKL = CHAR + "tft16_baronnashor_16.skn", CHAR + "tft16_baronnashor_16.skl"
TEX = 9151324242242210696   # the skin bin's first colour map, by path hash (512x512)
CLIPS = {   # path hashes only, named by what they show
    "idle": 4988058337701547574,       # 8.00 s: reared up, the S-curved neck swaying
    "idle2": 14413648277603115509,     # 2.23 s: the same, the head turning
    "attack": 8977912037954495251,     # 1.67 s: rears back (~416 ms) and strikes down (~624 ms)
    "attack2": 16372227599749877705,   # 0.27 s: a short head snap
    "spell": 14265223969971790385,     # 3.83 s: Void's Wrath - rears up (~478), slams down (~957-1436), sprays acid (~1900-3300)
    "spell2": 2731322251854803392,     # 3.83 s: a variant of spell
    "roar": 9571649648901343386,       # 3.33 s: turns away, the head thrown back (~2660)
    "flinch": 4558953113585880009,     # 0.40 s: a small nod
    "spawn": 7563171152524631238,      # 2.97 s: rises out of the ground, faces front and roars (~1185)
    "burrow": 4535098681094460876,     # 0.67 s: dives into the ground (~530 gone)
    "burrowed": 11834509095720882544,  # 0.80 s: under the ground, only the crest fins above it (TFT's move)
    "unburrow": 9044370650031673910,   # 1.00 s: bursts out of the ground (~400 up)
    "death": 4820199350106086237,      # 1.17 s: sways and crashes down on its side
}
SQ = 11
SOLE = 1390
A_SQUARES = 48   # A: the crest fins' tips to the column's base
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_baron_34": (35, "box", "idle@0"),            # A: TFT's idle, 3/4
    "2_baron_front": (0, "box", "idle@0"),          # front: the head, both mini heads, the two clawed arms
    "3_baron_head": (25, "head", "idle@0"),         # the head close-up: eyes, fangs, tusks, crest
    "4_baron_rear": (35, "box", "spell@478"),       # B: reared up before the slam
    "5_baron_back": (180, "box", "idle@0"),         # the back: the purple scales, the crest from behind
    "6_baron_head_front": (0, "head", "idle@0"),    # the face from the front: the eyes, the fangs
    "7_baron_side": (90, "box", "idle@0"),          # true side: how the neck curves, how far the head leans out
    "8_baron_slam": (35, "box", "spell@1200"),      # ONLY how it slams down
    "9_baron_strike": (35, "box", "attack@624"),    # ONLY how it strikes
}
HEAD_JOINTS = ("Head", "Face", "Jaw", "L_Tooth1", "L_Tooth2", "R_Tooth1", "R_Tooth2", "L_JawTooth1", "L_JawTooth2",
               "R_JawTooth1", "R_JawTooth2", "L_Eye_Front", "R_Eye_Front", "L_Eye_Rear", "R_Eye_Rear", "C_Eye")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_riftherald.png": (TFT, "tft_riftherald", "hd_idle"),
    "12_style_elderdragon.png": (TFT, "tft_elderdragon", "hd_idle"),
    "13_style_chogath.png": (CHAMPS, "league_chogath", "hd_idle"),
    "14_style_reksai.png": (CHAMPS, "league_reksai", "hd_idle"),
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
    ima, sa = full["1_baron_34"]
    k = A_SQUARES * SQ / (ima.getbbox()[3] - ima.getbbox()[1])
    guide(ima, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; crest tips to the base ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    imb, sb = full["4_baron_rear"]
    guide(imb, os.path.join(refs, "10b_layout_B.png"), k * sa / sb,
          "B: reared up before the slam, the SAME body scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "baronnashor", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
