"""Build the step-0 pack for Codex (assets/source/orianna/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_orianna_picture.py --out %TEMP%/or_work/orianna_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides pasted
from renders: Riot's, kept local, never committed) and <out>/style/9..12 (this pack's heroes at their dense frames, 8x:
league_elise's and league_katarina's hd_idle cut from their sheets, league_galio's hd_idle from
assets/source/bard/style_ref, league_kalista's hd_idle), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's
saves under or/dist pass MAX_PATH.
Orianna is drawn as two pictures on 1536x1536 squares: A = League's idle (Orianna_idle1) and B = commanding the ball
(Orianna_attack1 at 400 ms: the near hand raised toward it). The ball is skinned into her own mesh (joints Ball*,
Spinnig*Ridge): the frontal, head and back renders leave it out (pose_ref --hide-joints), the ball render is the
OriannaBall character of her WAD. In both pictures the ball floats beside her apart from her body, so it can be cut
out: in the game it is its own picture (it leaves her for Q / E). Bun top to soles about 72 squares of 11 px (~40 game
rows at 1.8 squares a game pixel; read back and brought to the chosen PPU by step 1).
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
IDLE = "Orianna_idle1@0"
COMMAND = "Orianna_attack1@400"
BALL = "Ball|Spinnig"
# name -> (champ, frames, yaw, size, fit, ground, width, crop: "box" / "head", hide the ball)
RENDERS = {
    "1_orianna_idle": ("Orianna", [IDLE], 45, 1000, 0.60, 0.80, 1.6, "box", False),
    "2_orianna_frontal": ("Orianna", [IDLE], 0, 1000, 0.60, 0.80, 1.6, "box", True),
    "3_orianna_head": ("Orianna", [IDLE], 40, 2400, 0.60, 0.80, 1.6, "head", True),
    "4_orianna_back": ("Orianna", [IDLE], 200, 1000, 0.60, 0.80, 1.6, "box", True),
    "6_orianna_command": ("Orianna", [COMMAND], 45, 1000, 0.60, 0.80, 1.6, "box", False),
    "7_orianna_ball": ("OriannaBall", ["orianna_ball_idle1@0"], 45, 1000, 0.50, 0.75, 1.0, "box", False),
}
# the layout guides: the render's bun top to soles FIG_H px (72 squares of 11) on the 1536 square, soles on row SOLE,
# centred; B is scaled like A (one size for both)
FIG_H = 792
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": ("1_orianna_idle.png", "A: League's idle; bun top to soles 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("6_orianna_command.png", "B: commanding the ball; same scale; layout only"),
}
STYLE = {
    "11_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "9_style_elise.png": ("elise", "hd_idle"),
    "10_style_katarina.png": ("katarina", "hd_idle"),
    "12_style_kalista.png": ("kalista", "hd_idle"),
}


def render(lol, name, spec, out):
    champ, frames, yaw, size, fit, ground, width, crop, hide = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Orianna", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    if hide:
        cmd += ["--hide-joints", BALL]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    key = _keyed(path)
    x0, y0, x1, y1 = key.getbbox()
    if crop == "head":  # the head: the top fifth of the figure, round the bun's columns
        band = key.crop((0, y0, key.width, y0 + (y1 - y0) // 10))
        bx0, _, bx1, _ = band.getbbox()
        cx, s = (bx0 + bx1) // 2, (y1 - y0) // 7
        im.crop((max(0, cx - s), max(0, y0 - s // 8), min(im.width, cx + s), y0 + s + s // 2)).save(path)
    else:
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
    src, label = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (1536 - fig.width) // 2
    y0 = SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Orianna.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/orianna/skins/base/oriannaloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(
            os.path.join(refs, "5_orianna_splash.png"))
    idle = _keyed(os.path.join(refs, "1_orianna_idle.png"))
    k = FIG_H / idle.crop(idle.getbbox()).height
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "orianna", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
