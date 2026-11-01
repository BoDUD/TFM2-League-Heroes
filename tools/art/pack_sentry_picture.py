"""Build the step-0 pack for Codex (assets/source/sentry/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_sentry_picture.py --out D:/TFM2-Workshop/sentry_packs/sentry_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Blue Sentinel, Krug, Skarner and Xerath,
8x, cut from their sheets), then <out>.zip.
The Sentry (苍蓝哨戒, en Pebbles, a tft pack hero, 2026-11-02) is set 18's 1-cost Rift Monster / Oracle (DA_18_Sentry,
ability 蔚蓝激光 Azure Laser): TWO tall crystal shards floating side by side - pale sage tops, dark navy-violet lower
halves, a red-violet seam - with a ROUND HOLE between them where its blue glow sits; no limbs, no face. TFTSet18.wad.client
tft18_sentry.skn + .skl (19 joints: Root, C_Rock, R_Rock, L_Rock, L_Rock_Top and buffbones; the skin borrows SRU_BlueMini).
Its colour map and its six clips are linked by path hash only; CLIPS below names them by what they show (rendered and
read by eye, 2026-11-02).
Two pictures at one square size: A = the idle at a slight 3/4 (the hole round and open); B = more side-on (the hole an
oval at the right). The user picks one.
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
CHAR = "assets/characters/tft18_sentry/skins/base/"
SKN, SKL = CHAR + "tft18_sentry.skn", CHAR + "tft18_sentry.skl"
TEX = 2798593494025323103   # the skin bin's colour map, by path hash (512x512)
CLIPS = {   # path hashes only, named by what they show
    "idle": 6140386580987279701,      # 1.6 s: floating, a slow bob
    "attack": 954806770894003221,     # 1.6 s: rises and tips forward, the hole opening (~300 ms)
    "death": 13100204868325690087,    # 3.0 s: tips over and the two halves fall apart
    "idle2": 3268164834747627537,     # 2.0 s: idle variants
    "idle3": 9596423471698500819,
    "idle4": 6317090249844304129,
}
SQ = 11
SOLE = 1390
A_SQUARES = 34   # A: the highest point (the left shard's tip) to the lowest point (the shards' bottom tips)
# name -> (yaw, pitch, crop "box" / "hole", clip@ms)
RENDERS = {
    "1_sentry_34": (20, 12, "box", "idle@0"),       # A: a slight 3/4, the hole round and open
    "2_sentry_front": (0, 12, "box", "idle@0"),     # front: the two halves and the whole round hole
    "3_sentry_hole": (20, 12, "hole", "idle@0"),    # the hole close-up: the rims, the blue inside
    "4_sentry_side": (50, 12, "box", "idle@0"),     # B: more side-on, the hole an oval at the right
    "5_sentry_back": (150, 12, "box", "idle@0"),    # the back
    "6_sentry_top": (180, 60, "box", "idle@0"),     # from above: two halves, the gap between them
    "7_sentry_attack": (35, 12, "box", "attack@300"),   # ONLY how it rises and tips when it fires
    "8_sentry_death": (35, 12, "box", "death@375"),     # ONLY how the two halves split when it dies
    "9_sentry_profile": (90, 12, "box", "idle@0"),      # true side: how thin the shards are
}
HOLE_BAND = (60.0, 112.0)   # model height band around the hole (bind pose: 11 .. 147)
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_sentinel.png": (TFT, "tft_sentinel", "hd_idle"),
    "12_style_krug.png": (TFT, "tft_krug", "hd_idle"),
    "13_style_skarner.png": (CHAMPS, "league_skarner", "hd_idle"),
    "14_style_xerath.png": (CHAMPS, "league_xerath", "hd_idle"),
}


class Model:
    """Its mesh on its own skeleton, one colour map; `head` marks the vertices in the band round the hole (it has no
    head: the hole and its glow are its face)."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.tex = pose_ref.read_tex(self.w.read(TEX))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(SKL))
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]
        rest = pose_ref.skin(self.v, self.infl, self.bind_inv, bind)
        self.head = (rest[:, 1] > HOLE_BAND[0]) & (rest[:, 1] < HOLE_BAND[1])

    def posed(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        return pose_ref.skin(self.v, self.infl, self.bind_inv, glob)


def render(m, name, spec, out, size=1600):
    """A mirrored 3/4 render facing image right, the figure 70% of the cell (its height or its width), on grey.
    "hole" crops round the hole."""
    yaw, pitch, crop, clip = spec
    pv = m.posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    span = max(np.ptp(pv[:, 1]), np.hypot(np.ptp(pv[:, 0]), np.ptp(pv[:, 2])))
    if crop == "hole":
        size *= 2
    scale, ground = size * 0.7 / span, size * 0.86
    im = pose_ref.render_hq(pv, m.tris, m.v["uv"], m.tex, -yaw, pitch, (size, size), scale,
                            ground).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    if crop == "hole":   # the projected box of the hole band's vertices (render_hq's transform), mirrored
        cy, sy = np.cos(np.radians(-yaw)), np.sin(np.radians(-yaw))
        cp, sp = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
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
    fa = full["1_sentry_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: idle, slight 3/4; top to the lowest tip ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_sentry_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle more side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "sentry", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
