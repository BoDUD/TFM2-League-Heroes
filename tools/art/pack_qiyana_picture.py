"""Build the step-0 pack for Codex (assets/source/qiyana/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_qiyana_picture.py --out C:/t/qy_work/qiyana_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Nilah, Irelia and Neeko, 8x, cut from their sheets),
then <out>.zip. Render into a short folder (C:/t).
Qiyana (group G jungle, 2026-10-22) is the Empress of the Elements: a proud young woman with tan-brown skin, long wavy
silver-white hair, a gold tiara with a teal gem under a tall white-jade crest, a teal strapless top with gold trim,
gold bracelets and a gold choker, dark brown leggings and purple-brown sandals, and her weapon - a huge ring blade
(dark brown-black outer blade, a teal inner rim with gold bands, two white-jade crystal heads with teal gems) held in
one hand beside her. Two pictures: A = League's idle (Qiyana_Base_Idle@0, the relaxed stand), 3/4 front facing right;
SA = the same idle seen from the SIDE facing right. Crest top to soles about 60 squares of 11 px (the ring inside the
same box). Her model: yaw 0 is the front, 35 the 3/4 view, 75 the side. Her skin bin hides the ring blade's submesh
(--hide-submeshes drops it): every render keeps it but the head close-up, which leaves it out to frame the face.
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
IDLE = "qiyana_base_idle@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_qiyana_idle": (IDLE, 35, 1600, 1.2, "box"),
    "2_qiyana_frontal": (IDLE, 0, 1600, 1.2, "box"),
    "3_qiyana_head": (IDLE, 35, 3200, 1.2, "head"),
    "4_qiyana_back": (IDLE, 200, 1600, 1.2, "box"),
    "6_qiyana_side": (IDLE, 75, 1600, 1.2, "box"),
    "7_qiyana_weapon": ("qiyana_base_idleready@0", 35, 1600, 1.2, "box"),
    "full_idle": (IDLE, 35, 1600, 1.2, "none"),
    "full_side": (IDLE, 75, 1600, 1.2, "none"),
}
# crest top to soles BODY_H px (60 squares of 11) on the 1536 square, soles on row SOLE, centred on CX
BODY_H = 660
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A: League's idle, 3/4 front; crest top to soles 660 px (60 squares of 11); "
                                         "the ring blade stands beside / behind her"),
    "8b_layout_side.png": ("full_side", "SA: the same idle from the side, facing right; same size and ground line"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_nilah.png": ("nilah", "hd_idle"),
    "12_style_irelia.png": ("irelia", "hd_idle"),
    "13_style_neeko.png": ("neeko", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Qiyana",
           *(["--hide-submeshes"] if crop == "head" else []), "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the crest, the tiara, the hair, the face: the top 30% of the figure (rendered without the ring)
        h = y1 - y0
        cx = (x0 + x1) // 2
        im = im.crop((cx - round(h * 0.2), max(0, y0 - h // 30), cx + round(h * 0.16), y0 + round(h * 0.3)))
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


def guide(src, name, label):
    """The whole figure scaled so crest top to soles is BODY_H, soles on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = BODY_H / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - BODY_H), (1536, SOLE - BODY_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Qiyana.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/qiyana/skins/base/qiyanaloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_qiyana_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "qiyana", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
