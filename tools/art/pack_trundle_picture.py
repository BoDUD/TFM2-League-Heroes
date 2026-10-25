"""Build the step-0 pack for Codex (assets/source/trundle/PICTURE_PROMPT.md): League references of Trundle, layout
guides and style pictures.

    python tools/art/pack_trundle_picture.py --out C:/t/tr_work/trundle_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art), <out>/refs/9a..9b (layout
guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Volibear, Braum, Ornn and Nunu, 8x,
cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Trundle (group J, 2026-10-25) is the Troll King of the Freljord: a big hunched blue-grey ice troll with a wild crimson
mane and beard, tusks, a white fur collar, teal-and-gold armour plates and a huge club of blue ice (Boneshiver) in
his right hand. Two pictures at the same square size: A = his idle 3/4 front facing right (hunched, the club hanging
by his side), B = his ult (Subjugate) pose standing up, his free hand reaching out - the user picks one as the design.
The ice pillar (TrundleWall) is a blank PlagueBlock in the WAD: the pillar is particles only, so it waits for the FX.
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
IDLE = "trundle_2013_idle1@0"
ULT = "trundle_2013_spell4@500"
# name -> (frame, yaw, size, width, crop)
RENDERS = {
    "1_trundle_idle": (IDLE, 35, 1600, 1.6, "box"),
    "2_trundle_frontal": (IDLE, 0, 1600, 1.6, "box"),
    "3_trundle_head": (IDLE, 35, 3200, 1.6, "head"),
    "4_trundle_back": (IDLE, 200, 1600, 1.6, "box"),
    "6_trundle_ult": (ULT, 35, 1600, 1.6, "box"),
    "7_trundle_q": ("trundle_2013_bite@500", 35, 1600, 1.6, "box"),
    "8_trundle_attack": ("trundle_2013_Attack1@300", 35, 1600, 1.6, "box"),
    "full_idle": (IDLE, 35, 1600, 1.6, "none"),
    "full_ult": (ULT, 35, 1600, 1.6, "none"),
}
A_SQUARES = 44   # A: mane top to the lowest point (hunched; the club's tip hangs near his feet)
CUT = {
    "10_style_volibear.png": ("volibear", "hd_idle"),
    "11_style_braum.png": ("braum", "hd_idle"),
    "12_style_ornn.png": ("ornn", "hd_idle"),
    "13_style_nunu.png": ("nunu", "hd_idle"),
}


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(src, name, k, label):
    """The render scaled by k (one scale for both guides), the lowest point on SOLE, centred on CX."""
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
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Trundle",
           "--fit-all", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    h = y1 - y0
    if crop == "head":   # mane, face, tusks, the fur collar; the club stays out (image left)
        w = x1 - x0
        im = im.crop((x0 + round(w * 0.30), max(0, y0 - h // 30), x1, y0 + round(h * 0.50)))
    elif crop == "box":
        m = max(x1 - x0, h) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Trundle.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/trundle/skins/base/trundleloadscreen.tex")).convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_trundle_splash.png"))
    idle = _keyed(os.path.join(work, "full_idle.png"))
    x0, y0, x1, y1 = idle.getbbox()
    k = A_SQUARES * SQ / (y1 - y0)   # both guides on A's scale: the renders share one camera fit (--fit-all)
    guide(os.path.join(work, "full_idle.png"), os.path.join(refs, "9a_layout_idle.png"), k,
          f"A: Trundle idle, 3/4 front; mane top to the lowest point ~{A_SQUARES * SQ} px ({A_SQUARES} squares of 11)")
    guide(os.path.join(work, "full_ult.png"), os.path.join(refs, "9b_layout_ult.png"), k,
          "B: Trundle's ult pose standing up, 3/4 front; the SAME square size as A")
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "trundle", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
