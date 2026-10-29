"""Build the step-0 pack for Codex (assets/source/sevika/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_sevika_picture.py --out C:/t/sv_work/sevika_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Vi, Jinx, Renni and Violet, 8x, cut
from their sheets), then <out>.zip.
Sevika (塞薇卡, the tft pack's fifteenth hero, 2026-10-29) is Arcane's Zaun enforcer turned chem-baron: a 5-cost of
Teamfight Tactics set 13 (TFT13_Lieutenant, 百变铁手 / 炼金男爵 / 搏击手), a broad-shouldered woman with dark brown
hair tied back and a huge brass mechanical left arm that Jinx painted over: teal plates, magenta spikes, a pair of
claws that open as a jaw, and a slot machine (three reels, little coloured lights) on its shoulder. Her model is in the
Riot client's TFTSet13.wad.client: tft13_lieutenant.skn + .skl (74 joints), two colour maps (the body's, and the arm's
tft13_lieutenant_base_arm_tx_cm.tex for submesh Arm_Mat); submesh BoxingBot_A is the extendo-punch fist, hidden until
her spell (it floats beside her in the idle). Her animation bin links its clips by path hash only: CLIPS below names
them by what they show (rendered and read by eye, 2026-10-29). Two pictures at one square size: A = the standing guard
(the arm hanging at her side, claws down); B = her fighting crouch (the arm raised in front). The user picks one.
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
WAD = ("Game", "DATA", "FINAL", "TFTSet13.wad.client")
CHAR = "assets/characters/tft13_lieutenant/skins/base/"
SKN, SKL = CHAR + "tft13_lieutenant.skn", CHAR + "tft13_lieutenant.skl"
TEX = CHAR + "tft13_lieutenant_base_tx_cm.tex"
ARM_TEX = CHAR + "tft13_lieutenant_base_arm_tx_cm.tex"   # the mechanical arm (submesh Arm_Mat)
HIDDEN = ("BoxingBot_A",)                                 # the extendo-punch fist, shown only by her spell
CLIPS = {
    "guard": 13633584421491154981,       # 1.17 s: punches; at 0 the standing guard, the arm low at her side
    "stance": 5946391157158447028,       # 1.17 s: a wide fighting crouch, the arm cocked up in front
    "run": 9969843373297983453,          # 1.87 s: a run, the arm swinging low
    "pose": 5863049780017196189,         # 1.83 s: standing, the arm raised across her (faces the camera side)
    "flame": 13505912701406831605,       # 0.67 s: wide stance, the arm held level forward (the flamethrower)
    "chomp": 5861350237958317307,        # 1.50 s: the arm raised high, the claws slammed down twice
    "punch": 10288371679822295472,       # 1.67 s: kneel, then the extendo punch thrown forward
    "intro": 17844170213200431742,       # 1.70 s: intro / celebration, the arm swung up
}
SQ = 11
SOLE = 1390
A_SQUARES = 54   # A: the top of her hair to her soles
# name -> (yaw, crop "box" / "head" / "arm", clip@ms)
RENDERS = {
    "1_sevika_34": (35, "box", "guard@0"),
    "2_sevika_front": (0, "box", "guard@0"),
    "3_sevika_head": (30, "head", "stance@0"),
    "4_sevika_arm": (35, "arm", "guard@0"),         # the arm alone: plates, spikes, claws, the slot machine
    "4b_sevika_arm_back": (-60, "arm", "guard@0"),  # the arm from her other side: the shoulder's slot machine
    "5_sevika_back": (180, "box", "guard@0"),
    "6_sevika_head_front": (0, "head", "guard@0"),
    "7_sevika_stance": (35, "box", "stance@0"),     # B
    "8_sevika_chomp": (35, "box", "chomp@900"),     # the claws open over the target (R's chomp)
    "9_sevika_flame": (35, "box", "flame@300"),     # the arm level forward (Q's flamethrower)
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_vi.png": (CHAMPS, "league_vi", "idle"),
    "12_style_jinx.png": (CHAMPS, "league_jinx", "idle"),
    "13_style_renni.png": (TFT, "tft_renni", "idle"),
    "14_style_violet.png": (TFT, "tft_violet", "idle"),
}


class Model:
    """Her mesh on her own skeleton: the body's colour map and the arm's own; the extendo fist hidden."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        tris, self.v = pose_ref.read_skn(b)
        self.tris = pose_ref.drop_submeshes(tris, pose_ref.skn_submeshes(b), set(HIDDEN))
        self.tex = pose_ref.read_tex(self.w.read_path(TEX))
        arm = pose_ref.read_tex(self.w.read_path(ARM_TEX))
        vmap = pose_ref.submesh_vertex_maps(b, len(self.v), [(["Arm_Mat"], 1)])
        which = vmap[self.tris[:, 0]]
        self.tri_tex = (which, [self.tex, arm])
        body, limb = which == 0, which == 1   # head close-ups leave the arm out: it covers her chin
        self.body = (self.tris[body], (which[body], [self.tex, arm]))
        self.arm = (self.tris[limb], (which[limb], [self.tex, arm]))
        self.joints, self.infl = pose_ref.read_skl(self.w.read_path(SKL))
        bind = pose_ref.globals_(self.joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]

    def posed(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.joints, [pose_ref.trs(*p) for p in local])
        pv = pose_ref.skin(self.v, self.infl, self.bind_inv, glob).copy()
        pv[:, 1] -= pv[:, 1].min()
        return pv


def render(m, name, spec, out, size=1600):
    """A mirrored 3/4 render facing image right, the figure 70% of the cell, on grey."""
    yaw, crop, clip = spec
    pv = m.posed(clip)
    h = pv[:, 1].max()
    tris, tri_tex = (m.tris, m.tri_tex)
    if crop == "head":
        size *= 2
        tris, tri_tex = m.body
    elif crop == "arm":
        tris, tri_tex = m.arm
    im = pose_ref.render_hq(pv, tris, m.v["uv"], m.tex, -yaw, 12, (size, size), size * 0.7 / h,
                            size * 0.86, tri_tex=tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # hair, face, neck: the top 20% of her
        hh = y1 - y0
        hx0, _, hx1, _ = im.crop((0, y0, im.width, y0 + round(hh * 0.2))).getbbox()
        mg = (hx1 - hx0) // 10
        can = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.2)))
    else:
        mg = max(x1 - x0, y1 - y0) // 12
        can = can.crop((max(0, x0 - mg), max(0, y0 - mg), min(im.width, x1 + mg), min(im.height, y1 + mg)))
    can.convert("RGB").save(os.path.join(out, name + ".png"))
    print(name, can.size)


def guide(m, clip, k, name, label):
    """The figure at k px per model unit (A's scale for both), the soles on SOLE, centred."""
    pv = m.posed(clip)
    big = pose_ref.render_hq(pv, m.tris, m.v["uv"], m.tex, -35, 12, (3072, 3072), k, 3000,
                             tri_tex=m.tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
    fig = big.crop(big.getbbox())
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
    for name, spec in RENDERS.items():
        render(m, name, spec, refs)
    # one scale for both: A's hair top to soles = A_SQUARES squares (a render's own height is its top, the arm too)
    body = m.body[0]
    h_a = m.posed("guard@0")[np.unique(body), 1].max()
    k = A_SQUARES * SQ / h_a
    guide(m, "guard@0", k, os.path.join(refs, "10a_layout_A.png"),
          f"A: the standing guard, the arm low at her side; hair top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(m, "stance@0", k, os.path.join(refs, "10b_layout_B.png"),
          "B: the fighting crouch, the arm raised in front; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "sevika", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
