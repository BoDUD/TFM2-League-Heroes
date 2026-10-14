"""Build the step-0 pack for Codex (assets/source/milio/PICTURE_PROMPT.md): League references, a layout guide and
style pictures.

    python tools/art/pack_milio_picture.py --out dist/milio_packs/milio_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders, the loading-screen art and a layout guide pasted
from a render: Riot's, kept local, never committed) and <out>/style/10..12 (this pack's restyled PPU heroes at the
user's density, about 2.2 squares a game pixel: zeri, kindred, nilah hd_idle at 8x, assets/source/milio/style_ref),
then <out>.zip.
Milio is a cheerful Ixtali boy (the user's picks, 2026-10-15): dark curly hair, warm brown skin, a red tunic with
big golden puffed shoulder pads, a teal sash, a magenta skirt-like kilt, red-and-teal leg wraps and sandals. His
base model carries no backpack (the skin hides the Backpack and the fire-buddy meshes until recall / emotes:
--hide-submeshes). Version A = League's idle (fists at his chest, grinning); version B = the same boy with a small
glowing fire spirit (a fuemigo, the loading-screen art) floating behind his shoulder on the image left.
The renders: yaw 45 (3/4 facing right, no mirror). The look: the PPU heroes' one look (league_zeri's: stocky, about
2.2 squares a game pixel, a thick outline); a child, so shorter than the grown heroes: hair top to soles about 72
squares of 10 px on a 1024x1536 portrait canvas.
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
GREY = (225, 225, 225)
IDLE = "spell4_idle_in@600"  # his idle stance with the head nearly level (Idle01 looks up at the sky)
# name -> (frames, yaw, size, fit, ground, width, crop: None / "head" / fractions)
RENDERS = {
    "1_milio_front": ([IDLE], 45, 1000, 0.80, 0.94, 0.9, None),
    "2_milio_frontal": ([IDLE], 0, 1000, 0.80, 0.94, 0.9, None),
    "3_milio_head": ([IDLE], 40, 2600, 0.80, 0.94, 0.9, "head"),
    "4_milio_back": ([IDLE], 200, 1000, 0.80, 0.94, 0.9, None),
    "6_milio_actions": (["attack1@300", "spell1_0@400", "spell3_still_a@300", "run_alt_2@0"], 80, 800, 0.62, 0.95, 1.1,
                        None),
    "7_milio_side": ([IDLE], 90, 1000, 0.80, 0.94, 0.9, None),
    "8_milio_shoulders": ([IDLE], 45, 2400, 0.80, 0.94, 0.9, (0.18, 0.18, 0.88, 0.62)),
}
STYLE = {
    "10_style_zeri.png": os.path.join(SRC, "milio", "style_ref", "zeri_hd_idle_x8.png"),
    "11_style_kindred.png": os.path.join(SRC, "milio", "style_ref", "kindred_hd_idle_x8.png"),
    "12_style_nilah.png": os.path.join(SRC, "milio", "style_ref", "nilah_hd_idle_x8.png"),
}
# the layout guide on the 1024x1536 canvas: hair top to soles BOY_H px (72 squares of 10), soles on SOLE; the fire
# spirit a disc of BUDDY of his height, its middle at (dx, dy) fractions of BOY_H from his box's left / top
CANVAS = (1024, 1536)
BOY_H = 720
SOLE = 1340
BOY_X = 380
BUDDY = 0.20
GUIDE = dict(dx=-0.10, dy=0.30, label="B: the fire spirit floats behind his shoulder (layout only)")


def render(lol, name, spec, out):
    frames, yaw, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Milio",
           "--hq", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop == "head":  # the top 28% of the figure, a margin round it
        box = Image.open(path).convert("RGBA")
        full = _keyed(path).getbbox()
        h = round((full[3] - full[1]) * 0.28)
        m = 40
        box.crop((full[0] - m, full[1] - m, full[2] + m, full[1] + h + m)).convert("RGB").save(path)
    elif crop:
        im = Image.open(path)
        w, h = im.size
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)


def cut(path):
    """The figure of a grey-ground render, as RGBA cropped to its box."""
    im = _keyed(path)
    return im.crop(im.getbbox())


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def guide(refs):
    boy = cut(os.path.join(refs, "1_milio_front.png"))
    boy = boy.resize((round(boy.width * BOY_H / boy.height), BOY_H), Image.LANCZOS)
    top = SOLE - BOY_H
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    r = round(BUDDY * BOY_H / 2)
    cx, cy = BOY_X + round(GUIDE["dx"] * BOY_H), top + round(GUIDE["dy"] * BOY_H)
    d = ImageDraw.Draw(can)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 190, 60, 255), outline=(200, 90, 20, 255), width=6)
    d.ellipse((cx - r // 2, cy - r // 3, cx + r // 2, cy + r // 3), fill=(255, 235, 150, 255))
    can.alpha_composite(boy, (BOY_X, top))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), GUIDE["label"], fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "9_layout_B.png"))
    print("9_layout_B boy box", (BOY_X, top, BOY_X + boy.width, SOLE), "spirit", (cx - r, cy - r, cx + r, cy + r))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Milio.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/milio/skins/base/milioloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_milio_splash.png"))
    guide(refs)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "milio", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
