"""Build the step-0 pack for Codex (assets/source/riftherald/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_riftherald_picture.py --out D:/TFM2-Workshop/riftherald_packs/riftherald_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Murk Wolf, Brambleback, Cho'Gath and
Rek'Sai, 8x, cut from their sheets), then <out>.zip.
The Rift Herald (峡谷先锋, a tft pack hero, 2026-11-02) is set 16's 4-cost Void Bruiser (TFT16_RiftHerald, ability 扭曲护甲
Warp Armor): a hunched VOID BEAST under a huge domed shell of faceted blue-violet crystal plates dotted with little glowing
eye spots, a dark plum body on two short thick hind legs, a long thin curling tail, two big front arms ending in heavy
crab-like pincer claws (two small rear arms behind them), a small face under the shell's front edge with glowing magenta
eyes and two big curved GOLDEN TUSKS, gold trims on the plates and claws, and a pink slit EYE on its back.
TFTSet16.wad.client TFT16_RiftHerald_16.skn + .skl (76 joints: Spine/Head/Jaw, L/R_Shell1-5, front + rear arms with
pincers, C_Tail1-5, L/R_Eye; one submesh RiftHerald_Mat). Its colour map and its ten clips are linked by path hash only;
CLIPS below names them by what they show (rendered and read by eye, 2026-11-02). No unit art in the client: the head
close-ups stand in for it.
Two pictures at one square size: A = TFT's own idle (3/4, hunched under the shell, claws low); B = reared up on its hind
legs, claws raised (Warp Armor's roar, the top of its spell). The user picks one.
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
CHAR = "assets/characters/tft16_riftherald/skins/base/"
SKN, SKL = CHAR + "tft16_riftherald_16.skn", CHAR + "tft16_riftherald_16.skl"
TEX = 6611892082330430841   # the skin bin's colour map (named right after the mesh), by path hash (512x512)
CLIPS = {   # path hashes only, named by what they show
    "idle": 15674594070850132681,      # 2.33 s+: hunched under the shell, breathing, claws low
    "run": 1642518257087985169,        # 1.17 s: a hunched scuttling run
    "attack": 14021918080705398372,    # 2.67 s: rears a claw up (~220 ms), lunges it down (~450 ms)
    "attack2": 18126258137014836722,   # 2.67 s: the same rear and lunge, the other claw
    "spin": 14033516799328715618,      # 1.07 s: spins round once, claws and tail out (TFT's SpinAttack)
    "spell": 6353154504403837659,      # 3.43 s: crouches, rears up on its hind legs, claws raised (~1.7-2.3 s), slams down (~2.6 s)
    "spell2": 9073151312039842669,     # = spell
    "charge": 13592930330753071868,    # 2.03 s: flips forward over its head (~340 ms) and charges shell first (the Herald's charge)
    "swing": 14337071300097046600,     # 3.57 s: winds a claw far back (~1.5 s) and sweeps it round low (~1.8 s)
    "death": 2818200962303393637,      # 1.02 s: topples over onto its shell
}
SQ = 11
SOLE = 1390
A_SQUARES = 42   # A: the top of the shell to its soles
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_herald_34": (50, "box", "idle@0"),          # A: TFT's idle, 3/4
    "2_herald_front": (0, "box", "idle@0"),        # front: the face under the shell, tusks, both claws
    "3_herald_head": (40, "head", "idle@0"),       # the face close-up: magenta eyes, golden tusks, the shell's rim
    "4_herald_rear": (45, "box", "spell@2000"),    # B: reared up on its hind legs, claws raised
    "5_herald_back": (180, "box", "idle@0"),       # the back: the pink slit eye in the shell
    "6_herald_head_front": (0, "head", "idle@0"),  # the face from the front: both eyes, both tusks
    "7_herald_side": (90, "box", "idle@0"),        # true side: the shell's dome, the tail
    "8_herald_charge": (70, "box", "charge@900"),  # ONLY how it charges shell first
    "9_herald_spin": (45, "box", "spin@200"),      # ONLY how it spins
}
HEAD_JOINTS = ("Head", "Jaw", "L_Eye", "R_Eye")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_murkwolf.png": (TFT, "tft_murkwolf", "hd_idle"),
    "12_style_brambleback.png": (TFT, "tft_brambleback", "hd_idle"),
    "13_style_chogath.png": (CHAMPS, "league_chogath", "hd_idle"),
    "14_style_reksai.png": (CHAMPS, "league_reksai", "hd_idle"),
}


class Model:
    """Its mesh on its own skeleton, one colour map; `head` marks the vertices its head carries most."""

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
    ima, sa = full["1_herald_34"]
    k = A_SQUARES * SQ / (ima.getbbox()[3] - ima.getbbox()[1])
    guide(ima, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: TFT idle, 3/4; shell top to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    imb, sb = full["4_herald_rear"]
    guide(imb, os.path.join(refs, "10b_layout_B.png"), k * sa / sb,
          "B: reared up, claws raised, the SAME body scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "riftherald", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
