"""Build the step-0 pack for Codex (assets/source/gromp/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_gromp_picture.py --out D:/TFM2-Workshop/gromp_packs/gromp_pack0 [--lol "D:/Riot Games/League of Legends"]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (renders of TFT's own model posed by its own clips and the layout
guides: Riot's, kept local, never committed) and <out>/style/11..14 (this repo's Murk Wolf, Krug, Tahm Kench and Kog'Maw,
8x, cut from their sheets), then <out>.zip.
Gromp (魔沼蛙, a tft pack hero, 2026-11-01) is set 18's 2-cost Rift Monster / Adaptor (DA_Gromp18_AP, ability 打嗝泡泡
Belchy Bubble): a huge squat TOAD - dark purple skin, a giant round olive-brown belly with plate-like folds, an orange
warty brow over two yellow-green eyes, a wide mouth with a long pink-purple tongue, purple / blue mushrooms growing on
its back, yellow-green warts. TFTSet18.wad.client tft18_gromp.skn + .skl (82 joints: Head Jaw Lips Eyes Tongue1-6,
mushrooms, plus a hidden mini Gromp and a spawn mesh: the skin hides SRU_Gromp_mini_mat and Toad_Spawn_Mat). Its
animation bin (data/characters/da_gromp18_ap/animations/skin0.bin) links seven clips by path hash only; LoL's Map11
sru_gromp bin has 21 more on the same skeleton. CLIPS below names them by what they show (rendered and read by eye,
2026-11-01).
Two pictures at one square size: A = the idle stance at 3/4; B = the same stance side-on facing right. The user picks one.
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
MAP11 = ("Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client")
CHAR = "assets/characters/tft18_gromp/skins/base/"
SKN, SKL, TEX = CHAR + "tft18_gromp.skn", CHAR + "tft18_gromp.skl", CHAR + "tft18_gromp_base_tx_cm.tex"
HIDE = {"Toad_Spawn_Mat", "SRU_Gromp_mini_mat"}   # the skin's initialSubmeshToHide
CLIPS = {   # path hashes only, named by what they show
    "idle": (WAD, 5835574239009137522),      # 3.27 s: squatting, the belly breathing
    "attack": (WAD, 10617488626617775394),   # 1.6 s: leans forward, the tongue lashes out (~456 ms)
    "attack2": (WAD, 13545875977261574124),  # 1.6 s: the same, the tongue lower
    "death": (WAD, 12965322446202076333),    # 5.0 s: sinks into the ground
    "run": (WAD, 14446475540929667257),      # 0.53 s: one big hop, stretched out at ~228-304 ms
    "puff": (WAD, 8908363383003671965),      # 0.93 s: the belly puffs up
    "roar": (MAP11, 3250657539129483045),    # 1.6 s (LoL): rears up, the mouth WIDE open (~456 ms)
}
SQ = 11
SOLE = 1390
A_SQUARES = 32   # A: the highest point (a mushroom cap) to the soles
# name -> (yaw, crop "box" / "head", clip@ms)
RENDERS = {
    "1_gromp_34": (35, "box", "idle@0"),
    "2_gromp_front": (0, "box", "idle@0"),
    "3_gromp_head": (35, "head", "idle@0"),       # the head: orange warty brow, yellow-green eyes, the wide mouth
    "4_gromp_side": (85, "box", "idle@0"),        # B: the same stance side-on
    "5_gromp_back": (150, "box", "idle@0"),       # the back: the purple / blue mushrooms, the warts
    "6_gromp_head_front": (0, "head", "idle@0"),
    "7_gromp_hop": (85, "box", "run@266"),        # ONLY how it stretches out in a hop
    "8_gromp_tongue": (35, "box", "attack@456"),  # ONLY the tongue lashing out
    "9_gromp_belch": (35, "box", "roar@456"),     # ONLY the mouth wide open, reared up
}
HEAD_JOINTS = ("Jaw", "Upper_Lip", "L_Lip", "R_Lip", "L_Eye", "R_Eye")
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_murkwolf.png": (TFT, "tft_murkwolf", "hd_idle"),
    "12_style_krug.png": (TFT, "tft_krug", "hd_idle"),
    "13_style_tahmkench.png": (CHAMPS, "league_tahmkench", "hd_idle"),
    "14_style_kogmaw.png": (CHAMPS, "league_kogmaw", "idle"),
}
class Model:
    """Its mesh on its own skeleton (the hidden submeshes dropped), one colour map; `head` marks the vertices its
    jaw, lips and eyes carry most (not Head: it carries half the body)."""

    def __init__(self, lol):
        self.w = Wad(os.path.join(lol, *WAD))
        self.wads = {WAD: self.w, MAP11: Wad(os.path.join(lol, *MAP11))}
        b = self.w.read_path(SKN)
        self.tris, self.v = pose_ref.read_skn(b)
        self.tris = pose_ref.drop_submeshes(self.tris, pose_ref.skn_submeshes(b), HIDE)
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
        wad, h = CLIPS[name]
        anim = pose_ref.read_anim(self.wads[wad].read(h))
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
    fa = full["1_gromp_34"]
    k = A_SQUARES * SQ / (fa.getbbox()[3] - fa.getbbox()[1])
    guide(fa, os.path.join(refs, "10a_layout_A.png"), k,
          f"A: idle stance, 3/4; top to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["4_gromp_side"], os.path.join(refs, "10b_layout_B.png"), k,
          "B: the same stance side-on; the same scale as A; size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "gromp", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
