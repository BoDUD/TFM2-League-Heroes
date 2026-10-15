"""Build the step-0 pack for Codex (assets/source/elise/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_elise_picture.py --out dist/elise_packs/elise_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders, the loading-screen art and two layout guides pasted
from renders: Riot's, kept local, never committed) and <out>/style/10..15 (this pack's heroes at the density Elise gets,
1.5 squares a game pixel, 8x: league_galio's hd_idle and the lo_idle of braum, zeri and nidalee from
assets/source/bard/style_ref, plus league_nidalee's cougar lo_c_idle - the size of a beast form - and league_jayce's
lo_idle - the latest hero at this density - cut from their sheets), then <out>.zip.
Elise (the user's picks, 2026-10-15: jungle AP assassin, both forms from level 1, PPU 1.5) is drawn as four pictures:
human A (League's idle: the tiptoe hover, clawed hands forward) and B (planted feet apart, one hand raised casting) on
1024x1536 portraits, crown to toe tips about 57 squares of 12 px (38 game rows); spider A (3/4 view facing right) and B
(exactly side-on facing right) on 1536x1024 landscapes, carapace top to leg tips about 45 squares (30 game rows, the
size of league_nidalee's cougar: 61 x 30 game px). League keeps the forms as two characters in Elise.wad.client: Elise
and EliseSpider (pose_ref --champ EliseSpider --wad Elise). Renders without --mirror show her front facing right.
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
HUMAN = "Elise_idle1@0"
SPIDER = "EliseSpider_Idle1@0"
# name -> (champ, frames, yaw, mirror, size, fit, ground, width, crop: None / "head" / fractions)
RENDERS = {
    "1_elise_human": ("Elise", [HUMAN], 45, False, 1000, 0.60, 0.94, 0.9, "box"),
    "2_elise_human_frontal": ("Elise", [HUMAN], 0, False, 1000, 0.60, 0.94, 0.9, "box"),
    "3_elise_head": ("Elise", [HUMAN], 40, False, 2600, 0.80, 0.94, 0.9, "head"),
    "4_elise_back": ("Elise", [HUMAN], 200, False, 1000, 0.60, 0.94, 0.9, "box"),
    "6_spider_34": ("EliseSpider", [SPIDER], 45, False, 1000, 0.36, 0.86, 1.5, "box"),
    "7_spider_side": ("EliseSpider", [SPIDER], 90, False, 1000, 0.36, 0.86, 1.5, "box"),
    "8_spider_front": ("EliseSpider", [SPIDER], 10, False, 1000, 0.36, 0.86, 1.5, "box"),
    "9_spider_head": ("EliseSpider", [SPIDER], 20, False, 2200, 0.36, 0.86, 1.5, "front"),
}
# the layout guides: the human's crown to toe tips HUMAN_H px (57 squares of 12), the spider's carapace top to leg tips
# SPIDER_H px (45 squares); the figure's full box (the back legs and horns stand about 12% above her crown) scaled so
GUIDES = {
    "5a_layout_human.png": ("1_elise_human.png", (1024, 1536), 1340, None, 684 * 1.12,
                            "human A / B: crown to toe tips 684 px (57 squares of 12); layout only"),
    "5b_layout_spider.png": ("6_spider_34.png", (1536, 1024), 900, None, 540,
                             "spider A / B: carapace top to leg tips 540 px (45 squares of 12); layout only"),
}
STYLE = {
    "10_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "11_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
    "12_style_zeri.png": os.path.join(SRC, "bard", "style_ref", "zeri_lo_idle_x8.png"),
    "13_style_nidalee.png": os.path.join(SRC, "bard", "style_ref", "nidalee_lo_idle_x8.png"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "14_style_nidalee_cougar.png": ("nidalee", "lo_c_idle"),
    "15_style_jayce.png": ("jayce", "lo_idle"),
}


def render(lol, name, spec, out):
    champ, frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Elise", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    if mirror:
        cmd.append("--mirror")
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop == "head":  # the head: a box round the top of the body under the raised back legs
        im = Image.open(path).convert("RGB")
        full = _keyed(path).getbbox()
        h = full[3] - full[1]
        w = im.width
        im.crop((int(w * 0.36), full[1] + int(h * 0.06), int(w * 0.68), full[1] + int(h * 0.32))).save(path)
    elif crop in ("box", "front"):  # the figure's box with a margin; "front": its front (image right) upper part
        im = Image.open(path).convert("RGB")
        x0, y0, x1, y1 = _keyed(path).getbbox()
        if crop == "front":  # seen from the front the face sits under the carapace, in the middle
            w_, h_ = x1 - x0, y1 - y0
            x0, x1, y0 = x0 + w_ * 28 // 100, x0 + w_ * 72 // 100, y0 + h_ * 25 // 100
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
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
    """The render with its full box FULL_H px tall, the lowest point on the canvas row SOLE, centred."""
    src, canvas, sole, x0, full_h, label = spec
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    k = full_h / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (canvas[0] - fig.width) // 2 if x0 is None else x0
    y0 = sole - fig.height
    can = Image.new("RGBA", canvas, GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, sole), (canvas[0], sole)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, name))
    print(name, "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of the lo_ density)."""
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Elise.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/elise/skins/base/eliseloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_elise_splash.png"))
    for name, spec in GUIDES.items():
        guide(refs, name, spec)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "elise", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
