"""Build the step-0 pack for Codex (assets/source/cassiopeia/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_cassiopeia_picture.py --out %TEMP%/cs_work/cassiopeia_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8b (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Nami, Morgana and Elise, 8x, cut from their sheets),
then <out>.zip. Render into a short folder (%TEMP%).
Cassiopeia (#128, mid, 2026-10-18) is a serpent woman: a human upper body (tan skin, a gold-and-emerald bra and arm
bands, gold claw gloves) on a long dark-green scaled snake tail with a lighter belly, a gold-and-green snake-hood
helmet with a gold crest over her face, dark teal hair falling behind. Two pictures, the user picks one: A = League's
idle (cassiopeia_idle1: the tail curving down and lying out behind her on the ground), B = the tail coiled under her
in a loop (narrower). A chibi head (about a third of the height from the crest to the bottom of the coil).
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
IDLE = "cassiopeia_idle1@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_cass_idle": (IDLE, 45, 1600, 1.6, "box"),
    "2_cass_frontal": (IDLE, 0, 1600, 1.6, "box"),
    "3_cass_head": (IDLE, 40, 3200, 1.6, "head"),
    "4_cass_back": (IDLE, 200, 1600, 1.6, "box"),
    "6_cass_gaze": ("cassiopeia_spell4@1100", 45, 1600, 1.8, "box"),
    "7_cass_side": (IDLE, 80, 1600, 1.6, "box"),
    "full_idle": (IDLE, 45, 1600, 1.6, "none", ["--fit-all"]),
}
# crest top to the lowest scale BODY_H px (70 squares of 11) on the 1536 square, ground on row SOLE, centred
BODY_H = 770
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": "A: League's idle, the tail lying out behind her; crest top to ground 770 px (70 squares of 11); layout only",
    "8b_layout_B.png": "B: same height and ground line; the tail COILED under her in a loop (see the text); size only",
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_nami.png": ("nami", "hd_idle"),
    "12_style_morgana.png": ("morgana", "hd_idle"),
    "13_style_elise.png": ("elise", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec[:5]
    extra = list(spec[5]) if len(spec) > 5 else []
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Cassiopeia",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hood, the crest, the face and the hair: the top 30% of the figure
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + round(h * 0.30))).getbbox()
        m = (hx1 - hx0) // 8
        im = im.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(h * 0.30)))
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


def guide(src, name, label, fade=False, body=None):
    """The whole figure scaled so crest top to the lowest scale (`body`, the same render) is BODY_H, the ground on SOLE,
    centred (B: faded - size only)."""
    full = _keyed(src)
    fb = full.getbbox()
    fig = full.crop(fb)
    bb = _keyed(body).getbbox()
    k = BODY_H / (bb[3] - bb[1])
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    if fade:
        a = np.asarray(fig).copy()
        a[..., 3] = (a[..., 3] * 0.35).astype(np.uint8)
        fig = Image.fromarray(a)
    x0, y0 = round(768 - fig.width / 2), SOLE - fig.height
    print("  crest to ground", fig.height, "px")
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Cassiopeia.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/cassiopeia/skins/base/cassiopeialoadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_cass_splash.png"))
    full = os.path.join(work, "full_idle.png")
    for i, (name, label) in enumerate(GUIDES.items()):
        guide(full, os.path.join(refs, name), label, fade=i == 1, body=full)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "cassiopeia", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
