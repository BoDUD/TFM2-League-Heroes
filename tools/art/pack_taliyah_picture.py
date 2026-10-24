"""Build the step-0 pack for Codex (assets/source/taliyah/PICTURE_PROMPT.md): League references of Taliyah, layout
guides and style pictures.

    python tools/art/pack_taliyah_picture.py --out C:/t/ta_work/taliyah_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Taliyah, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Qiyana, Azir, Zoe and Aurora,
8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Taliyah (group I, mid, 2026-10-24) is the Stoneweaver: a young Shuriman girl with tanned skin and a big swept-up mass of
brown hair with a small gold ornament on top, a cream stone-plated mantle round her shoulders, a long red coat with gold
trim whose two long front panels end in grey stones, a dark indigo tunic and leggings, purple sleeves with cream cuffs
and brown boots. Her skin hides three props (SurfRock, RecallRock, TauntRock): the idles drop them all, the surf keeps
SurfRock, the boulder she rides on her passive (Run_Passive).
Two pictures: A = her standing idle, B = surfing on her boulder, both 3/4 front facing right. Every render frames on all
vertices (--fit-all, the props too), so the two guides share one scale: about 54 squares of 11 px from the hair top to
the soles in A; B's boulder sits on the same ground line. Yaw 0 front, 35 the 3/4 view.
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
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "taliyah_idle1@0"
SURF = "taliyah_run_passive@500"
PROPS = ["--hide-submeshes"]   # the idles: SurfRock, RecallRock and TauntRock all hidden
SURF_PROPS = ["--hide-submesh", "TauntRock", "--hide-submesh", "RecallRock"]
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none", props)
RENDERS = {
    "1_taliyah_idle": (IDLE, 35, 1600, 1.2, "box", PROPS),
    "2_taliyah_frontal": (IDLE, 0, 1600, 1.2, "box", PROPS),
    "3_taliyah_head": (IDLE, 35, 3200, 1.2, "head", PROPS),
    "4_taliyah_back": (IDLE, 200, 1600, 1.2, "box", PROPS),
    "6_taliyah_surf": (SURF, 35, 1600, 1.2, "box", SURF_PROPS),
    "7_taliyah_run": ("taliyah_run1@300", 35, 1600, 1.2, "box", PROPS),
    "8_taliyah_cast": ("taliyah_spell1_0@400", 35, 1600, 1.2, "box", PROPS),
    "full_taliyah_idle": (IDLE, 35, 1600, 1.2, "none", PROPS),
    "full_taliyah_surf": (SURF, 35, 1600, 1.2, "none", SURF_PROPS),
}
HEAD_FRAC = 0.30   # the head close-up: the swept-up hair and its ornament, the face and the stone mantle
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label); both drawn at the scale that makes A's hair top to soles ANCHOR squares
    "9a_layout_taliyah.png": ("full_taliyah_idle", "A: Taliyah standing, 3/4 front; hair top to soles ~594 px (54 squares of 11)"),
    "9b_layout_taliyah_surf.png": ("full_taliyah_surf", "B: Taliyah surfing on her boulder; the SAME scale as A, the boulder on the ground line"),
}
ANCHOR = ("full_taliyah_idle", 54)
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_qiyana.png": ("qiyana", "hd_idle"),
    "11_style_azir.png": ("azir", "hd_idle"),
    "12_style_zoe.png": ("zoe", "hd_idle"),
    "13_style_aurora.png": ("aurora", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop, props = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Taliyah", "--fit-all",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + props
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hair, the face and the mantle
        h = y1 - y0
        cx = (x0 + x1) // 2
        im = im.crop((cx - round(h * 0.33), max(0, y0 - h // 30), cx + round(h * 0.33), y0 + round(h * HEAD_FRAC)))
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(src, name, k, label):
    """The render scaled by k (one scale for every guide), the figure's lowest point on SOLE (the soles in A, the
    boulder's bottom in B: the surf floats above the model's own ground), centred on CX."""
    full = _keyed(src)
    x0, y0, x1, y1 = full.getbbox()
    fig = full.crop((x0, y0, x1, y1))
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height), "top", round((SOLE - py) / SQ, 1), "squares over the ground")


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Taliyah.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/taliyah/skins/base/taliyahloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_taliyah_splash.png"))
    anchor = _keyed(os.path.join(work, ANCHOR[0] + ".png"))
    x0, y0, x1, y1 = anchor.getbbox()
    k = ANCHOR[1] * SQ / (y1 - y0)
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), k, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "taliyah", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
