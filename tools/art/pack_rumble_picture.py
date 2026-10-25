"""Build the step-0 pack for Codex (assets/source/rumble/PICTURE_PROMPT.md): League references of Rumble, layout guides
and style pictures.

    python tools/art/pack_rumble_picture.py --out C:/t/ru_work/rumble_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7b (League renders of Rumble, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Kled, Blitzcrank, Heimerdinger and
Urgot, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Rumble (group J, top, 2026-10-25) is the Mechanized Menace: a tiny yordle pilot (big ears, welding goggles pushed up, a
cheeky grin) in the open cockpit of a big home-made scrap-metal mech - one unit: a flamethrower arm, a steel claw arm,
exhaust pipes on its back, two short thick legs. Two pictures at the SAME square size and the SAME height (about 45
squares of 11 px): A = his idle 3/4 front facing right, chibi; B = the same, more chibi (the pilot's head bigger, the
mech shorter and rounder; its guide renders with pose_ref --head 1.8 --legs 0.8) - the choice is the proportion, since
the pilot's face is small at ~40 game px.
The clip names were not read when this was written (no League client here): find() picks each from the WAD's animation
list by pattern and prints the whole list when one is missing; --clip NAME=CLIP overrides one.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
SQ = 11
SOLE = 1390
CX = 768
FIT, GROUND = 0.45, 0.82
HEIGHT = 45   # squares, highest point (pipes or ears) to the steel feet
CHIBI = ["--head", "1.8", "--legs", "0.8"]
# clip patterns (searched in the .anm file names, lower case, first match in this order)
CLIPS = {
    "idle": [r"^rumble_idle1?$", r"idle_?(base|01|1)$", r"idle"],
    "q": [r"spell1$", r"spell1"],
    "e": [r"spell3$", r"spell3"],
    "r": [r"spell4$", r"spell4"],
}
# name -> (clip key, ms, yaw, size, width, crop, extra pose_ref args)
RENDERS = {
    "1_rumble_idle": ("idle", 0, 35, 1600, 1.5, "box", []),
    "2_rumble_frontal": ("idle", 0, 0, 1600, 1.5, "box", []),
    "3_rumble_head": ("idle", 0, 35, 3200, 1.5, "head", []),
    "4_rumble_back": ("idle", 0, 200, 1600, 1.5, "box", []),
    "6_rumble_q": ("q", 500, 35, 1600, 1.8, "box", []),
    "7_rumble_e": ("e", 300, 35, 1600, 1.8, "box", []),
    "7b_rumble_r": ("r", 400, 35, 1600, 1.8, "box", []),
    "full_rumble": ("idle", 0, 35, 1600, 1.5, "none", []),
    "full_rumble_chibi": ("idle", 0, 35, 1600, 1.5, "none", CHIBI),
}
GUIDES = {
    "9a_layout_rumble.png": ("full_rumble", "A: Rumble idle, 3/4 front; highest point to the feet ~500 px (45 squares of 11)"),
    "9b_layout_rumble_chibi.png": ("full_rumble_chibi", "B: the same, more chibi (pilot bigger, mech shorter); same height"),
}
CUT = {
    "10_style_kled.png": ("kled", "hd_idle"),
    "11_style_blitzcrank.png": ("blitzcrank", "idle"),
    "12_style_heimerdinger.png": ("heimerdinger", "hd_idle"),
    "13_style_urgot.png": ("urgot", "hd_idle"),
}


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(src, name, label):
    """The render scaled to HEIGHT squares, its lowest point on SOLE, centred on CX (A and B the same height)."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = HEIGHT * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height),
          "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))


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


def find(wad, overrides):
    """Clip key -> .anm name (without extension) from Rumble's animation bin."""
    blob = wad.read_path("data/characters/rumble/animations/skin0.bin")
    names = sorted({os.path.splitext(os.path.basename(m.decode("latin1")))[0].lower()
                    for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.anm", blob)})
    out = {}
    for key, pats in CLIPS.items():
        if key in overrides:
            out[key] = overrides[key]
            continue
        hit = next((c for p in pats for c in names if re.search(p, c)), None)
        if hit is None:
            raise SystemExit(f"no clip for {key!r} ({pats}); the clips: {', '.join(names)}; pass --clip {key}=<name>")
        out[key] = hit
    print("clips", out)
    return out


def render(lol, name, spec, clips, out):
    key, ms, yaw, size, width, crop, extra = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Rumble",
           "--fit-all", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", f"{clips[key]}@{ms}"] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    h = y1 - y0
    if crop == "head":   # the pilot, the goggles, the ears and the cockpit rim: the top half of the figure
        im = im.crop((x0, max(0, y0 - h // 30), x1, y0 + round(h * 0.5)))
    elif crop == "box":
        m = max(x1 - x0, h) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--clip", action="append", default=[], metavar="KEY=CLIP",
                    help="the .anm name for idle / q / e / r when the pattern picks a wrong one")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs and <out>_measure")
    a = ap.parse_args()
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        import pose_ref  # noqa: E402
        from riot import Wad  # noqa: E402
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Rumble.wad.client"))
        clips = find(wad, dict(x.split("=", 1) for x in a.clip))
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, clips, work if name.startswith("full_") else refs)
        splash = pose_ref.read_tex(wad.read_path("assets/characters/rumble/skins/base/rumbleloadscreen.tex")).convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_rumble_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "rumble", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
