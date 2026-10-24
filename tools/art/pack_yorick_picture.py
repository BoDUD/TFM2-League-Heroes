"""Build the step-0 pack for Codex (assets/source/yorick/PICTURE_PROMPT.md): League references of Yorick and his
summons, layout guides and style pictures.

    python tools/art/pack_yorick_picture.py --out C:/t/yo_work/yorick_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art), <out>/refs/9a..9b (layout
guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Mordekaiser, Darius, Illaoi and
Karthus, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Yorick (group J, 2026-10-25) is the Shepherd of Souls: a huge grim gravedigger priest of the Shadow Isles with a
shovel, a lantern, a purple-black hood over pale blue-grey skin, a coffin-like pauldron, and summons - Mist Walkers
(small ghouls) and the Maiden of the Mist (a tall wraith). Two pictures: A = Yorick's idle 3/4 front facing right,
B = the Maiden and one Mist Walker side by side at the SAME square size (they become effect pictures later).
His cape (submesh Yorick_Cape) is cloth simulated in League: unsimulated it lies flat on the ground, so the renders
hide it and the prompt describes it. Summon heights in B are set by eye from the game (Maiden about his height
floating, a Walker ~0.55x); the bind-pose heights (284 / 172 / 102 units) carry no skin scale.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
SQ = 11
SOLE = 1390
CX = 768
FIT, GROUND = 0.45, 0.82
NOCAPE = ["--hide-submesh", "Yorick_Cape"]
WALKER_TEX = ["--submesh-texture", "Ghouls_MAT=YorickGhoulMelee.tex"]   # its skin bin names no colour map
IDLE = "yorick_idle1@0"
MAIDEN = "yorick_wraith_idle01@0"
GHOUL = "Yorick_ghoul_idle@0"
# name -> (champ, frame, yaw, size, width, crop)
RENDERS = {
    "1_yorick_idle": ("Yorick", IDLE, 35, 1600, 1.5, "box"),
    "2_yorick_frontal": ("Yorick", IDLE, 0, 1600, 1.5, "box"),
    "3_yorick_head": ("Yorick", IDLE, 35, 3200, 1.5, "head"),
    "4_yorick_back": ("Yorick", IDLE, 200, 1600, 1.5, "box"),
    "6_maiden": ("YorickBigGhoul", MAIDEN, 35, 1600, 1.5, "box"),
    "7_mist_walker": ("YorickGhoulMelee", GHOUL, 35, 1600, 1.5, "box"),
    "8_yorick_q": ("Yorick", "yorick_spell1@500", 35, 1600, 1.6, "box"),
    "8b_yorick_e": ("Yorick", "yorick_spell3@400", 35, 1600, 1.6, "box"),
    "full_yorick": ("Yorick", IDLE, 35, 1600, 1.5, "none"),
    "full_maiden": ("YorickBigGhoul", MAIDEN, 35, 1600, 1.5, "none"),
    "full_walker": ("YorickGhoulMelee", GHOUL, 35, 1600, 1.5, "none"),
}
ANCHOR = ("full_yorick", 50)   # hood top to soles (the shovel blade stands higher)
B_SIZE = {"full_maiden": 1.0, "full_walker": 0.55}   # heights against Yorick's
CUT = {
    "10_style_mordekaiser.png": ("mordekaiser", "hd_idle"),
    "11_style_darius.png": ("darius", "hd_idle"),
    "12_style_illaoi.png": ("illaoi", "hd_idle"),
    "13_style_karthus.png": ("karthus", "hd_idle"),
}


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(src, name, k, label):
    """The render scaled by k (one scale for every guide), the lowest claw / boot on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height),
          "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(CHAMPS, f"league_{hero}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(CHAMPS, f"league_{hero}#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))   # on grey like the other style pictures
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)
    print(os.path.basename(out), pad.size)


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ, "--wad", "Yorick",
           "--fit-all", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + {"Yorick": NOCAPE, "YorickGhoulMelee": WALKER_TEX}.get(champ, [])
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    h = y1 - y0
    if crop == "head":   # hood, face, beard, the pauldron
        im = im.crop((x0, max(0, y0 - h // 30), x1, y0 + round(h * 0.42)))
    elif crop == "box":
        m = max(x1 - x0, h) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)


def guide_b(work, name, h_yorick, label):
    """The Maiden (image left) and a Walker (image right) at their heights against Yorick's, soles on SOLE."""
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    figs = []
    for src, f in B_SIZE.items():
        full = _keyed(os.path.join(work, src + ".png"))
        fig = full.crop(full.getbbox())
        k = h_yorick * f / fig.height
        figs.append(fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS))
    gap = 4 * SQ
    x = round(CX - (sum(f.width for f in figs) + gap) / 2)
    d = ImageDraw.Draw(can)
    for fig in figs:
        can.alpha_composite(fig, (x, SOLE - fig.height))
        print(os.path.basename(name), "figure", (x, SOLE - fig.height, x + fig.width, SOLE),
              "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))
        x += fig.width + gap
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, work if name.startswith("full_") else refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Yorick.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/yorick/skins/base/yorickloadscreen.tex")).convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_yorick_splash.png"))
    anchor = _keyed(os.path.join(work, ANCHOR[0] + ".png"))
    x0, y0, x1, y1 = anchor.getbbox()
    k = ANCHOR[1] * SQ / (y1 - y0)
    guide(os.path.join(work, "full_yorick.png"), os.path.join(refs, "9a_layout_yorick.png"), k,
            "A: Yorick idle, 3/4 front; shovel tip to soles ~550 px (50 squares of 11)")
    guide_b(work, os.path.join(refs, "9b_layout_summons.png"), ANCHOR[1] * SQ,
            "B: the Maiden (left) and a Mist Walker (right); the SAME square size as A")
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "yorick", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
