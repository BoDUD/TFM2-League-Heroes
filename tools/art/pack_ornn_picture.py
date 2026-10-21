"""Build the step-0 pack for Codex (assets/source/ornn/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_ornn_picture.py --out C:/t/on_work/ornn_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guide: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Volibear, Gragas and Cho'Gath, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (C:/t).
Ornn (#146, 2026-10-21) is the Fire below the Mountain: a huge hunched ram-horned demigod smith with slate blue-grey
skin - two enormous curled dark-iron horns with red rune grooves and glowing red tips, a shaggy crimson mane and beard
(braids in steel rings) with glowing red-orange eyes, a bronze chest plate cast with ram horns, leather harness straps
with bronze buckles, a belt with tongs and a plum apron, short legs in plum boots; the near arm in a big bronze
pauldron holding his big steel forge hammer low, the far arm molten from the elbow down with a smaller hammer. His skin
keeps the passive's forge props (a barrel, a sword, the forge) as submeshes shown only by their animations, so every
render hides them. Two pictures, both 3/4 front facing right (like the latest heroes: only the 3/4 view): A = League's
idle and proportions, B = the horns curled tighter round the head and both hammers smaller (a narrower sprite). Horn
top to soles about 66 squares of 11 px. His model: yaw 0 is the front, 35 the 3/4 view, 75 the side.
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
IDLE = "ornn_idle1@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none"[, fit: the hammer raised over his head needs room])
RENDERS = {
    "1_ornn_idle": (IDLE, 35, 1600, 1.4, "box"),
    "2_ornn_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_ornn_head": (IDLE, 25, 3200, 1.4, "head"),
    "4_ornn_back": (IDLE, 200, 1600, 1.4, "box"),
    "6_ornn_slam": ("ornn_spell1@133", 35, 1600, 1.6, "box", 0.36),
    "7_ornn_side": (IDLE, 75, 1600, 1.4, "box"),
    "full_idle": (IDLE, 35, 1600, 1.6, "none"),
}
# horn top to soles BODY_H px (66 squares of 11) on the 1536 square, soles on row SOLE, the box (hammer included)
# centred on CX
BODY_H = 726
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A / B: League's idle, 3/4 front; horn top to soles 726 px (66 squares of 11); "
                                         "B: horns curled tighter, hammer smaller"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_volibear.png": ("volibear", "hd_idle"),
    "12_style_gragas.png": ("gragas", "hd_idle"),
    "13_style_chogath.png": ("chogath", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84
SPLASH = ("assets/characters/ornn/skins/base/ornnloadscreen.tex", "assets/characters/ornn/skins/base/ornnloadscreen_0.tex")


def render(lol, name, spec, out):
    frame, yaw, size, width, crop, *fit = spec
    # --hide-submeshes: the forge's props (a barrel, a sword: his passive's items) hang in the skin until shown
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Ornn",
           "--hide-submeshes", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(fit[0] if fit else FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the horns, the mane, the face and the beard: from the horn tops down 55%
        top = y0
        h = y1 - top
        hx0, _, hx1, _ = _keyed(path).crop((0, top, im.width, top + round(h * 0.55))).getbbox()
        m = (hx1 - hx0) // 10
        im = im.crop((hx0 - m, max(0, top - m), hx1 + m, top + round(h * 0.55)))
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
    """The whole figure scaled so horn top to soles is BODY_H, soles on SOLE, its box (hammer included) centred on CX."""
    full = _keyed(src)
    box = full.getbbox()
    fig = full.crop(box)
    k = BODY_H / (box[3] - box[1])
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Ornn.wad.client"))
        for path in SPLASH:
            try:
                splash = pose_ref.read_tex(wad.read_path(path)).convert("RGB")
            except Exception:  # noqa: BLE001 - the other name
                continue
            splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(
                os.path.join(refs, "5_ornn_splash.png"))
            break
        else:
            raise SystemExit("no loading-screen art found")
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "ornn", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
