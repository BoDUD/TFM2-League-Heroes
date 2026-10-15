"""Build the step-0 pack for Codex (assets/source/katarina/PICTURE_PROMPT.md): League references, a layout guide and
style pictures.

    python tools/art/pack_katarina_picture.py --out dist/katarina_packs/katarina_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and a layout guide pasted
from a render: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's heroes at the density Katarina
gets, 1.5 squares a game pixel: league_galio's hd_idle and the lo_idle of braum, zeri and nidalee at 8x, the same
pictures as assets/source/bard/style_ref), then <out>.zip.
Katarina (the user's picks, 2026-10-15: mid AP assassin, Q+E / W+E slots, add-on, pro combos, PPU 1.5) is drawn twice
from the same prompt (K1 / K2, the user picks one): League's idle1, a dagger held up by the face in one hand and the
other low and forward. Renders at yaw 45 WITH --mirror (without it she shows her back). Squares of 12 px, crown to
soles about 57 squares (38 game rows at 1.5).
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
IDLE = "katarina_idle1@0"
# name -> (frames, yaw, mirror, size, fit, ground, width, crop: None / fractions of the picture)
RENDERS = {
    "1_katarina_front": ([IDLE], 45, True, 1000, 0.62, 0.94, 0.9, None),
    "2_katarina_frontal": ([IDLE], 10, True, 1000, 0.62, 0.94, 0.9, None),
    "3_katarina_head": ([IDLE], 40, True, 2600, 0.62, 0.94, 0.9, "head"),
    "4_katarina_back": ([IDLE], 200, True, 1000, 0.62, 0.94, 0.9, None),
    "6_katarina_actions": (["katarina_attack1@230", "katarina_spell1@200", "katarina_spell2_throw@120",
                            "katarina_spell3@150", "katarina_channel@250", "katarina_run@0"],
                           80, False, 700, 0.58, 0.95, 1.2, None),
    "7_katarina_side": ([IDLE], 90, False, 1000, 0.62, 0.94, 0.9, None),
    "8_katarina_upper": ([IDLE], 45, True, 2400, 0.62, 0.94, 0.9, (0.22, 0.30, 0.86, 0.66)),
}
STYLE = {
    "10_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "11_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
    "12_style_zeri.png": os.path.join(SRC, "bard", "style_ref", "zeri_lo_idle_x8.png"),
    "13_style_nidalee.png": os.path.join(SRC, "bard", "style_ref", "nidalee_lo_idle_x8.png"),
}
# the layout guide: crown to soles BODY_H px (57 squares of 12), soles on the canvas row SOLE, the figure's box left at X0
CANVAS = (1024, 1536)
BODY_H = 684
SOLE = 1340
X0 = 260


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Katarina",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    if mirror:
        cmd.append("--mirror")
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop == "head":  # the head: the top fifth of the figure, round the face
        im = Image.open(path).convert("RGB")
        full = _keyed(path).getbbox()
        h = full[3] - full[1]
        cx = (full[0] + full[2]) // 2
        im.crop((cx - int(h * 0.16), full[1] - int(h * 0.02), cx + int(h * 0.16), full[1] + int(h * 0.24))).save(path)
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


def guide(refs):
    """The 3/4 render scaled so the figure's crown to soles is BODY_H, the soles on SOLE (the raised dagger may top
    the crown: the figure's box is measured without it, by the soles and the hair top from the head crop's scale)."""
    full = _keyed(os.path.join(refs, "1_katarina_front.png"))
    box = full.getbbox()
    fig = full.crop(box)
    k = BODY_H / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    can.alpha_composite(fig, (X0, SOLE - fig.height))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - BODY_H), (CANVAS[0], SOLE - BODY_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), "layout only: top of the figure to the soles 684 px (57 squares of 12); grey line = ground",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "9_layout.png"))
    print("9_layout.png figure box", (X0, SOLE - fig.height, X0 + fig.width, SOLE))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Katarina.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/katarina/skins/base/katarinaloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(
            os.path.join(refs, "5_katarina_splash.png"))
    guide(refs)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "katarina", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
