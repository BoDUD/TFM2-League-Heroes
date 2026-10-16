"""Build the step-0 pack for Codex (assets/source/kalista/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_kalista_picture.py --out dist/kalista_packs/kalista_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7 (League renders, the loading-screen art and the layout guides pasted
from renders: Riot's, kept local, never committed) and <out>/style/10..14 (this pack's heroes at about the density
Kalista gets, 8x: league_elise's and league_vladimir's hd_idle - PPU 1.8, Kalista's - and league_nidalee's lo_idle,
cut from their sheets, plus galio's hd_idle and zeri's lo_idle from assets/source/bard/style_ref), then <out>.zip.
Kalista (the user's picks, 2026-10-15: ADC, PPU 1.8) is drawn as two pictures on 1536x1536 squares (her spear is about
as long as she is tall): A = League's idle (Kalista_Idle1: crouched low, the spear held low pointing back past her near
side, the free hand clawed forward) and B = the upright stance of Kalista_Spell4_Throw at 167 ms (standing tall, the
spear held diagonally down behind her). Crown to soles standing about 72 squares of 12 px = 40 game rows at PPU 1.8.
Renders without --mirror show her front facing right.
"""
import argparse
import json
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
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "Kalista_Idle1@0"
STAND = "Kalista_Spell4_Throw@167"
SIZE, FIT = 1000, 0.60     # bind pose FIT x SIZE px tall in the full-figure renders
# name -> (frames, yaw, size, fit, ground, width, crop: "head" / "box")
RENDERS = {
    "1_kalista_idle": ([IDLE], 45, SIZE, FIT, 0.80, 1.6, "box"),
    "2_kalista_frontal": ([IDLE], 0, SIZE, FIT, 0.80, 1.6, "box"),
    "3_kalista_head": ([STAND], 50, 2600, 0.80, 0.94, 0.9, "head"),
    "4_kalista_back": ([IDLE], 200, SIZE, FIT, 0.80, 1.6, "box"),
    "6_kalista_stand": ([STAND], 45, SIZE, FIT, 0.80, 1.6, "box"),
    "7_kalista_stand_side": ([STAND], 80, SIZE, FIT, 0.80, 1.6, "box"),
}
# B (upright) from the crest's top to the soles FULL_B px - her helm's top to the soles then about 72 squares of 12 px
# (40 game rows at PPU 1.8); A is scaled alike (the same render size), so both pictures show her at one size. The
# figure's right edge (her front) RIGHT px from the canvas's right side: the spear reaches back to the left.
FULL_B = 980
RIGHT = 170
GUIDES = {
    "5a_layout_A.png": ("1_kalista_idle.png", (1536, 1536), 1340, "A: League's idle; layout only (size, the spear's place)"),
    "5b_layout_B.png": ("6_kalista_stand.png", (1536, 1536), 1340,
                        "B: upright, helm top to soles about 864 px (72 squares of 12); layout only"),
}
STYLE = {
    "13_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "14_style_zeri.png": os.path.join(SRC, "bard", "style_ref", "zeri_lo_idle_x8.png"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_elise.png": ("elise", "hd_idle"),
    "11_style_vladimir.png": ("vladimir", "hd_idle"),
    "12_style_nidalee.png": ("nidalee", "lo_idle"),
}


def render(lol, name, spec, out):
    frames, yaw, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Kalista",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    key = _keyed(path)
    x0, y0, x1, y1 = key.getbbox()
    if crop == "head":  # the top of the figure: crest, helm and face, the columns that hold them
        h = y1 - y0
        band = key.crop((0, y0, key.width, y0 + int(h * 0.22)))
        bx0, _, bx1, _ = band.getbbox()
        m = (bx1 - bx0) // 8
        im.crop((max(0, bx0 - m), max(0, y0 - m), min(im.width, bx1 + m), y0 + int(h * 0.26))).save(path)
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
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


def guide(refs, name, spec, k):
    """The render scaled by k, its lowest point on the canvas row SOLE, its front RIGHT px from the right side."""
    src, canvas, sole, label = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = canvas[0] - RIGHT - fig.width
    y0 = sole - fig.height
    can = Image.new("RGBA", canvas, GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, sole), (canvas[0], sole)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, name))
    print(name, "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Kalista.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/kalista/skins/base/kalistaloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(
            os.path.join(refs, "5_kalista_splash.png"))
    b = _keyed(os.path.join(refs, "6_kalista_stand.png")).getbbox()
    k = FULL_B / (b[3] - b[1])
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "kalista", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
