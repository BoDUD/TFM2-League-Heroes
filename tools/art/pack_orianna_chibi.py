"""Build the chibi (Q版) redesign pack for Codex (assets/source/orianna/CHIBI_PROMPTS.md): League renders at chibi
proportions, layout guides on the game grid and style pictures.

    python tools/art/pack_orianna_chibi.py --out %TEMP%/or_q/orianna_chibi_pack [--lol D:/WeGameApps/lol]

The user (2026-10-21): 「我要的是Q版的 现在明显质量不行啊 还有动作少太多了」 - Orianna's PPU 2.2 design (assets/source/orianna/hd)
reads as a slender adult doll. This pack asks Codex for a chibi design drawn AT GAME SIZE (no big picture to shrink):
84 squares of 12 px from bun top to soles (38 game px at PPU 2.2), in two views of the same design - A 3/4 front
facing right (the idle), B side-on facing right (the actions are side-on) - and the ball alone; two takes (Q1 head a
third of her height, Q2 a little bigger).

Writes <out>/CHIBI_PROMPTS.md, <out>/refs/1..8 (League renders: Riot's, kept local, never committed), <out>/style/9..11
(base heroes, league_zeri and league_gwen at 8x), <out>/layout/12a..12c (the chibi renders on the 1536 canvas with the
12-px grid, the bun-top and sole lines), then <out>.zip.
Orianna's base skin bin names a cube map before her colour map, so every render passes
--submesh-texture lambert2=Particles/orianna_base_TX_CM (the earlier packs' renders came out untextured grey).
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
BALL = "Ball|Spinnig"
TEX = ["--submesh-texture", "lambert2=Particles/orianna_base_TX_CM"]
CHIBI = ["--head", "2.2", "--legs", "0.75"]
# name -> (champ, frame, yaw, size, crop: "box" / "head", hide the ball, chibi)
RENDERS = {
    "1_league_idle": ("Orianna", IDLE, 45, 1000, "box", False, False),
    "2_q_front": ("Orianna", IDLE, 45, 1000, "box", True, True),
    "3_q_side": ("Orianna", IDLE, 90, 1000, "box", True, True),
    "4_q_head": ("Orianna", IDLE, 40, 2400, "head", True, True),
    "5_q_back": ("Orianna", IDLE, 200, 1000, "box", True, True),
    "6_ball": ("OriannaBall", "orianna_ball_idle1@0", 45, 1000, "box", False, False),
}
# the game grid: 12-px squares on the 1536 square (128 x 128), bun top on row TOP, soles on row SOLE (84 rows)
SQ = 12
TOP, SOLE = 33, 117
GUIDES = {
    "12a_layout_front.png": ("2_q_front.png", "A: 3/4 front facing right. Bun top row 33 (green), soles row 117 (red). Layout only"),
    "12b_layout_side.png": ("3_q_side.png", "B: side-on facing right. Same rows. Layout only"),
}
BALL_D = 20  # squares across


def render(lol, name, spec, out):
    champ, frame, yaw, size, crop, hide, chibi = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Orianna", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", "0.6", "--ground", "0.8", "--width", "1.6", "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    if champ == "Orianna":
        cmd += TEX
    if hide:
        cmd += ["--hide-joints", BALL]
    if chibi:
        cmd += CHIBI
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    key = _keyed(path)
    x0, y0, x1, y1 = key.getbbox()
    if crop == "head":  # the head: bun top to the chin, round the bun's columns
        band = key.crop((0, y0, key.width, y0 + (y1 - y0) // 10))
        bx0, _, bx1, _ = band.getbbox()
        cx, s = (bx0 + bx1) // 2, (y1 - y0) // 4
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


def grid(can):
    d = ImageDraw.Draw(can)
    for i in range(0, 1537, SQ):
        c = (205, 205, 205, 255) if (i // SQ) % 5 else (180, 180, 180, 255)
        d.line([(i, 0), (i, 1536)], fill=c)
        d.line([(0, i), (1536, i)], fill=c)
    d.line([(0, TOP * SQ), (1536, TOP * SQ)], fill=(40, 170, 60, 255), width=2)
    d.line([(0, SOLE * SQ), (1536, SOLE * SQ)], fill=(210, 50, 50, 255), width=2)
    return d


def guide(refs, out, name, spec):
    src, label = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    k = (SOLE - TOP) * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    can = Image.new("RGBA", (1536, 1536), (238, 238, 238, 255))
    d = grid(can)
    x0 = (1536 - fig.width) // 2 // SQ * SQ
    can.alpha_composite(fig, (x0, SOLE * SQ - fig.height))
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(out, name))
    print(name, "figure", fig.size, "=", round(fig.width / SQ), "x", round(fig.height / SQ), "squares")


def ball_guide(refs, out):
    full = _keyed(os.path.join(refs, "6_ball.png"))
    ball = full.crop(full.getbbox())
    k = BALL_D * SQ / max(ball.size)
    ball = ball.resize((round(ball.width * k), round(ball.height * k)), Image.LANCZOS)
    can = Image.new("RGBA", (1536, 1536), (238, 238, 238, 255))
    d = grid(can)
    can.alpha_composite(ball, ((1536 - ball.width) // 2, (1536 - ball.height) // 2))
    d.text((24, 24), f"The ball alone: about {BALL_D} squares across, centred. Layout only", fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(out, "12c_layout_ball.png"))


def cut(hero, tag, out, z=8):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(CHAMPS, f"league_{hero}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(CHAMPS, f"league_{hero}#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST).save(out)
    print(os.path.basename(out), pad.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style, layout = (os.path.join(a.out, d) for d in ("refs", "style", "layout"))
    for d in (refs, style, layout):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Orianna.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/orianna/skins/base/oriannaloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "7_splash.png"))
    cut("orianna", "hd_idle", os.path.join(refs, "8_current_rejected.png"), z=6)
    for name, spec in GUIDES.items():
        guide(refs, layout, name, spec)
    ball_guide(refs, layout)
    subprocess.run([sys.executable, os.path.join(HERE, "native_refs.py"), "--out", style, "--style"], check=True,
                   capture_output=True)
    os.replace(os.path.join(style, "tfm2_style_ref_mage.png"), os.path.join(style, "9_base_heroes.png"))
    for f in os.listdir(style):
        if f.startswith("tfm2_style_ref"):
            os.remove(os.path.join(style, f))
    cut("zeri", "hd_idle", os.path.join(style, "10_zeri.png"))
    g = Image.open(os.path.join(SRC, "gwen", "codex_grid", "gwen-grid-A_1x.png")).convert("RGBA")
    g = g.crop(g.getbbox())
    pad = Image.new("RGBA", (g.width + 4, g.height + 4), GREY + (255,))
    pad.alpha_composite(g, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(os.path.join(style, "11_gwen.png"))
    shutil.copyfile(os.path.join(SRC, "orianna", "CHIBI_PROMPTS.md"), os.path.join(a.out, "CHIBI_PROMPTS.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
