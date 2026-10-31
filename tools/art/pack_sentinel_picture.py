"""Build the step-0 pack for Codex (assets/source/sentinel/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_sentinel_picture.py --out D:/TFM2-Workshop/sentinel_packs/sentinel_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Krug, Galio, Ornn and Kobuko, 8x, cut
from their sheets), then <out>.zip.
The Blue Sentinel (苍蓝雕纹魔像, a tft pack hero, 2026-10-31) is set 18's 4-cost Rift Monster / Vanguard / Invoker tank
(DA_Sentinel18, ability 蔚蓝冲击波 Azure Shockwave): the Rift's blue-buff golem - a hunched hulk of dark slate-teal
stone, two HUGE rock arms with fists bigger than its body, pale sage boulders piled on its shoulders and back, a small
pale stone head sunk between the shoulders with ONE glowing cyan eye, glowing cyan seams at the chest, the waist and the
knees, spiral runes carved into its stones. TFTSet18.wad.client tft18_sentinel.skn + .skl (one submesh Blue_Golem_CM,
64 joints); the colour map has no path in the bins, only its hash; its animation bin links eight clips by path hash
only: CLIPS below names them by what they show (rendered and read by eye, 2026-10-31). Two pictures at one square size:
A = TFT's own idle at 3/4; B = the same idle side-on facing right. The user picks one.
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
CHAR = "assets/characters/tft18_sentinel/skins/base/"
SKN, SKL = CHAR + "tft18_sentinel.skn", CHAR + "tft18_sentinel.skl"
TEX = 17532955210135772828   # the colour map (Blue_Golem_CM): no path in the bins, only this hash (1024 x 1024)
CLIPS = {   # path hashes only (data/characters/da_sentinel18/animations/skin0.bin); named by what they show
    "idle": 2775890318190512109,          # 1.67 s: stands hunched, the huge fists hanging low, breathing
    "run": 8134263959341771911,           # 1.30 s: a heavy lumbering walk-run
    "attack": 13227130914041229844,       # 2.03 s: raises ONE fist high over the head and slams it down
    "attack2": 14610552604922702027,      # 2.03 s: winds up and swings a fist round and down
    "slam": 6307813205290992080,          # 2.03 s: raises BOTH fists high over the head and slams the ground
    "death": 13424982547992967425,        # 4.97 s: staggers, falls forward and crumbles into rocks
    "celebration": 4923694829718045277,   # 7.07 s
    "spawn": 10862577676306312221,        # 5.67 s: rises out of the ground and stands
}
SQ = 11
SOLE = 1390
A_SQUARES = 44   # A: the top of the shoulder boulders to the soles (the arms make it wider than tall)
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_sentinel_34": (35, "box", "idle@0"),
    "2_sentinel_front": (0, "box", "idle@0"),
    "3_sentinel_head": (35, "head", "idle@0"),          # the small pale head and its one cyan eye
    "4_sentinel_side": (85, "box", "idle@0"),           # B: the same idle side-on
    "5_sentinel_back": (180, "box", "idle@0"),          # the back: the boulders on the shoulders, the glowing waist band
    "6_sentinel_head_front": (0, "head", "idle@0"),
    "7_sentinel_run": (80, "box", "run@650"),           # the lumbering run, side-on: only how the legs and arms swing
    "8_sentinel_slam": (35, "box", "slam@406"),         # both fists high over the head: only how the arms rise
    "9_sentinel_fist": (80, "box", "attack@406"),       # one fist raised, side-on: only the arm and the fist
}
HEAD_JOINTS = ("Head",)
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_krug.png": (TFT, "tft_krug", "hd_idle"),
    "12_style_galio.png": (CHAMPS, "league_galio", "hd_idle"),
    "13_style_ornn.png": (CHAMPS, "league_ornn", "hd_idle"),
    "14_style_kobuko.png": (TFT, "tft_kobuko", "hd_idle"),
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
    fa = full["1_sentinel_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; shoulder boulders to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_sentinel_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same idle side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "sentinel", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
