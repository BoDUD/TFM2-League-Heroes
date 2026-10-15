"""Build the step-0 pack for Codex (assets/source/jayce/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_jayce_picture.py --out dist/jayce_packs/jayce_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and two layout guides pasted
from renders: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's heroes at the density Jayce gets,
1.5 squares a game pixel: league_galio's hd_idle and the lo_idle of braum, zeri and nidalee at 8x, the same pictures as
assets/source/bard/style_ref), then <out>.zip.
Jayce (the user's picks, 2026-10-15: top AD fighter, both forms from level 1, PPU 1.5) is drawn twice, the same man at
the same size: A = the Mercury Hammer (League's melee idle, the hammer held up before his chest, its golden head above
his shoulder) on a 1024x1536 portrait; B = the Mercury Cannon (League's ranged idle, the hammer folded into a cannon held
at the hip, the muzzle pointing image right) on a 1536x1024 landscape. One model in League: the hammer's blocks swing
into the cannon on its own bones, no submesh is hidden. Renders: the hammer at yaw 45 (no mirror), the cannon at yaw 45
WITH --mirror (without it he shows his back). Squares of 12 px, crown to soles about 57 squares (38 game rows at 1.5).
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
HAMMER = "jayce_melee_idle1@0"
CANNON = "jayce_ranged_idle1@0"
# name -> (frames, yaw, mirror, size, fit, ground, width, crop: None / "head" / fractions)
RENDERS = {
    "1_jayce_hammer": ([HAMMER], 45, False, 1000, 0.62, 0.94, 0.9, None),
    "2_jayce_hammer_frontal": ([HAMMER], 0, False, 1000, 0.62, 0.94, 0.9, None),
    "3_jayce_head": ([HAMMER], 40, False, 2600, 0.80, 0.94, 0.9, "head"),
    "4_jayce_back": ([HAMMER], 200, False, 1000, 0.62, 0.94, 0.9, None),
    "6_jayce_cannon": ([CANNON], 45, True, 1000, 0.62, 0.94, 1.3, None),
    "7_jayce_cannon_frontal": ([CANNON], 10, True, 1000, 0.62, 0.94, 1.3, None),
    "8_jayce_actions": (["jayce_melee_attack1@250", "jayce_melee_spell1@500", "jayce_melee_spell3@250",
                         "jayce_ranged_attack1@100", "jayce_ranged_spell1@250", "jayce_melee_run1@0"],
                        80, False, 700, 0.58, 0.95, 1.2, None),
    "9_jayce_side": ([HAMMER, CANNON], 90, False, 1000, 0.62, 0.94, 1.1, None),
    "10_jayce_upper": ([HAMMER], 45, False, 2400, 0.62, 0.94, 0.9, (0.15, 0.10, 0.85, 0.55)),
}
STYLE = {
    "11_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "12_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
    "13_style_zeri.png": os.path.join(SRC, "bard", "style_ref", "zeri_lo_idle_x8.png"),
    "14_style_nidalee.png": os.path.join(SRC, "bard", "style_ref", "nidalee_lo_idle_x8.png"),
}
# the layout guides: crown to soles BODY_H px (57 squares of 12), soles on the canvas row SOLE, the body's box left at X
BODY_H = 684
# the hammer idle's crown-to-soles is 564 px at BODY_H / (fit x size) (the bind pose stands taller): measured on 5a
CROWN_FIX = 684 / 564
GUIDES = {
    "5a_layout_A_hammer.png": ("1_jayce_hammer.png", (1024, 1536), 1340, 300,
                               "A: hammer - crown to soles 684 px (57 squares of 12); layout only"),
    "5b_layout_B_cannon.png": ("6_jayce_cannon.png", (1536, 1024), 900, 380,
                               "B: cannon - the same man at the same scale (crouched, so lower); layout only"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Jayce",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    if mirror:
        cmd.append("--mirror")
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop == "head":  # the head: a box round the top of the body below the raised hammer
        im = Image.open(path).convert("RGB")
        full = _keyed(path).getbbox()
        h = full[3] - full[1]
        w = im.width
        im.crop((int(w * 0.38), full[1] + int(h * 0.20), int(w * 0.66), full[1] + int(h * 0.42))).save(path)
    elif crop:
        im = Image.open(path)
        w, h = im.size
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def guide(refs, name, spec):
    """The render at one scale for both (one man): the hammer idle's crown to soles BODY_H, the soles on the canvas row
    SOLE, the figure's box left at x0."""
    src, canvas, sole, x0, label = spec
    fit, size = 0.62, 1000
    k = BODY_H / (fit * size) * CROWN_FIX
    full = _keyed(os.path.join(refs, src))
    box = full.getbbox()
    fig = full.crop(box)
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    y0 = sole - fig.height  # the soles on the ground line
    can = Image.new("RGBA", canvas, GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, sole), (canvas[0], sole)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, name))
    print(name, "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Jayce.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/jayce/skins/base/jayceloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_jayce_splash.png"))
    for name, spec in GUIDES.items():
        guide(refs, name, spec)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "jayce", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
