"""Build the step-0 pack for Codex (assets/source/gangplank/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_gangplank_picture.py --out %TEMP%/gp_work/gangplank_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Miss Fortune, Swain and Jarvan IV, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (%TEMP%).
Gangplank (#126, top, group B of the 10-17 plan) is the Bilgewater pirate captain: a big black crescent tricorn hat,
a grey-brown beard braided at the chin with a red tie, a heavy moustache, a scowl, a bare tattooed chest and belly under
a teal-green harness collar, red forearm wraps, a red sash and a brown belt with a gold buckle, a long dark-purple coat
hanging behind him in torn tails with gold trim, dark grey-green trousers, brown cuffed boots; a golden flintlock hand
cannon and a dark serrated cutlass with an orange-hot edge. Two pictures of the same Gangplank for the user to pick the
idle from: A = League's idle (the hand cannon on his near shoulder, the hand beside the face, not over it; the cutlass
down and forward), B = a ready stance (the hand cannon low at his hip pointing forward, the cutlass held down in front).
Hat top to soles about 72 squares of 11 px. The crate / barrel submeshes are hidden (--hide-submeshes).
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
IDLE = "Gangplank_Idle1@1600"
SHOT = "Gangplank_spell1@222"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_gangplank_idle": (IDLE, 20, 1600, 1.4, "box"),
    "2_gangplank_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_gangplank_head": ("Gangplank_Idle1@0", 0, 3200, 1.2, "head"),
    "4_gangplank_back": (IDLE, 200, 1600, 1.4, "box"),
    "6_gangplank_shot": (SHOT, 30, 1600, 1.6, "box"),
    "7_gangplank_side": (IDLE, 80, 1600, 1.4, "box"),
    "full_idle": (IDLE, 20, 1600, 1.4, "none"),
}
# hat top to soles BODY_H px (72 squares of 11) on the 1536 square, soles on row SOLE, centred
BODY_H = 792
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": "A: League's idle, hand cannon on the near shoulder; hat top to soles 792 px (72 squares of 11); layout only",
    "8b_layout_B.png": "B: same size and ground line; hand cannon low at the hip, cutlass down in front (see the text); layout only",
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_missfortune.png": ("missfortune", "idle"),
    "12_style_swain.png": ("swain", "hd_idle"),
    "13_style_jarvaniv.png": ("jarvaniv", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Gangplank",
           "--hq", "--mirror", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # hat, face and beard: the top 32% of the figure
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + round(h * 0.32))).getbbox()
        m = (hx1 - hx0) // 8
        im = im.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(h * 0.32)))
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


def guide(src, name, label, fade=False):
    """The whole figure scaled so helmet top to soles is BODY_H, soles on SOLE, centred (B: faded - size only)."""
    full = _keyed(src)
    fb = full.getbbox()
    fig = full.crop(fb)
    k = BODY_H / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    if fade:
        a = np.asarray(fig).copy()
        a[..., 3] = (a[..., 3] * 0.35).astype(np.uint8)
        fig = Image.fromarray(a)
    x0, y0 = round(768 - fig.width / 2), SOLE - fig.height
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Gangplank.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/gangplank/skins/base/gangplankloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_gangplank_splash.png"))
    full = os.path.join(work, "full_idle.png")
    for i, (name, label) in enumerate(GUIDES.items()):
        guide(full, os.path.join(refs, name), label, fade=i == 1)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "gangplank", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
