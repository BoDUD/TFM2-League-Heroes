"""Build the step-0 pack for Codex (assets/source/steb/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_steb_picture.py --out C:/t/sb_work/steb_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Caitlyn, Fizz, Vi and Violet, 8x, cut
from their sheets), then <out>.zip.
Steb (斯特卜, the tft pack's sixteenth hero, 2026-10-29) is Arcane's fish-man enforcer: a 1-cost of Teamfight Tactics
set 13 (TFT13_Fish, 执法官 / 格斗家, APTank, ability 战地医疗 Field Medicine), a tall young man with pale sea-green skin,
pointed fin ears, teal scale freckles on his cheeks and a teal slicked-back quiff, in Piltover's blue enforcer uniform
(gold-trimmed high collar, a pale lavender chest plate, brown leather chest pouches and harness), grey trousers, dark
green gloves and boots, a big brown leather backpack (the field medic's kit), and two hextech side-handle batons
(tonfas: a blue steel tube, brass caps, glowing cyan runes, a wooden grip). His model is in the Riot client's
TFTSet13.wad.client: tft13_fish.skn + .skl (96 joints), three submeshes with their own colour maps (Body, Backpack,
Weapon = both batons). His animation bin links eight clips by path hash only: CLIPS below names them by what they show
(rendered and read by eye, 2026-10-29). Two pictures at one square size: A = his idle (one baton on his shoulder, the
other pointing down at his side); B = his fighting crouch (both batons held forward). The user picks one.
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
CHAR = "assets/characters/tft13_fish/skins/base/"
SKN, SKL = CHAR + "tft13_fish.skn", CHAR + "tft13_fish.skl"
TEX = CHAR + "tft13_fish_base_tx_cm.tex"
PART_TEX = {"Backpack": CHAR + "tft13_fish_base_backpack_tx_cm.tex",   # each submesh with its own map
            "Weapon": CHAR + "tft13_fish_base_weapon_tx_cm.tex"}
CLIPS = {
    "idle": 13018538065718426540,        # 1.97 s: standing, a baton on his shoulder, the other pointing down
    "stance": 5356066349845203418,       # 1.63 s: a swing into a wide fighting crouch, the batons held forward
    "combat": 9118729368212794473,       # 1.80 s: baton swings, then a hunched guard
    "run": 5057476057500924436,          # 1.30 s: a run, a baton on his shoulder
    "death": 14798793227916524658,       # 1.33 s: knocked down, the baton flies, lies flat
    "intro": 9781569442673553887,        # 2.17 s: intro, batons spun and planted
    "dance": 5829912437719379372,        # 0.97 s: batons crossed overhead, a squat
    "dance2": 3096066159677753460,       # 0.97 s: a baton twirled up
}
SQ = 11
SOLE = 1390
A_SQUARES = 54   # A: the top of his quiff to his soles
# name -> (yaw, crop "box" / "head" / "weapon" / "pack", clip@ms)
RENDERS = {
    "1_steb_34": (35, "box", "idle@0"),
    "2_steb_front": (0, "box", "idle@0"),
    "3_steb_head": (30, "head", "idle@0"),
    "4_steb_batons": (35, "weapon", "idle@0"),       # the two batons alone
    "5_steb_back": (180, "box", "idle@0"),           # the backpack
    "6_steb_head_front": (0, "head", "idle@0"),
    "7_steb_stance": (35, "box", "stance@1200"),     # B
    "8_steb_pack": (150, "pack", "idle@0"),          # the backpack alone, from behind and the side
    "9_steb_swing": (35, "box", "combat@500"),       # a baton swing: only the size of the batons next to him
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_caitlyn.png": (CHAMPS, "league_caitlyn", "idle"),
    "12_style_fizz.png": (CHAMPS, "league_fizz", "idle"),
    "13_style_vi.png": (CHAMPS, "league_vi", "idle"),
    "14_style_violet.png": (TFT, "tft_violet", "idle"),
}


class Model:
    """His mesh on his own skeleton, each submesh with its own colour map."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        texs = [pose_ref.read_tex(self.w.read_path(TEX))] + [pose_ref.read_tex(self.w.read_path(p))
                                                            for p in PART_TEX.values()]
        self.tex = texs[0]
        vmap = pose_ref.submesh_vertex_maps(b, len(self.v), [([n], i + 1) for i, n in enumerate(PART_TEX)])
        which = vmap[self.tris[:, 0]]
        self.tri_tex = (which, texs)
        self.parts = {k: (self.tris[sel], (which[sel], texs))
                      for k, sel in (("body", which == 0), ("pack", which == 1), ("weapon", which == 2))}
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
    if crop == "head":   # the batons and the pack left out: a baton lies over his shoulder
        size *= 2
        tris, tri_tex = m.parts["body"]
    elif crop in ("weapon", "pack"):
        tris, tri_tex = m.parts[crop]
    im = pose_ref.render_hq(pv, tris, m.v["uv"], m.tex, -yaw, 12, (size, size), size * 0.7 / h,
                            size * 0.86, tri_tex=tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # quiff, face, ears, collar: the top 22% of him
        hh = y1 - y0
        hx0, _, hx1, _ = im.crop((0, y0, im.width, y0 + round(hh * 0.22))).getbbox()
        mg = (hx1 - hx0) // 10
        can = can.crop((hx0 - mg, max(0, y0 - mg), hx1 + mg, y0 + round(hh * 0.22)))
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
    # one scale for both: A's quiff top to soles = A_SQUARES squares (a render's own height is its top, batons too)
    body = m.parts["body"][0]
    h_a = m.posed("idle@0")[np.unique(body), 1].max()
    k = A_SQUARES * SQ / h_a
    guide(m, "idle@0", k, os.path.join(refs, "10a_layout_A.png"),
          f"A: the idle, a baton on his shoulder, the other pointing down; quiff top to soles ~{A_SQUARES * SQ} px "
          f"({A_SQUARES} squares of {SQ}); layout only")
    guide(m, "stance@1200", k, os.path.join(refs, "10b_layout_B.png"),
          "B: the fighting crouch, the batons held forward; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "steb", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
