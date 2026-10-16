"""Build the step-0 pack for Codex (assets/source/drmundo/PICTURE_PROMPT.md): League references, a layout guide
and style pictures.

    python tools/art/pack_drmundo_picture.py --out dist/drmundo_packs/drmundo_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guide pasted
from a render: Riot's, kept local, never committed) and <out>/style/9..12 (this pack's big heroes at their dense
frames, 8x: league_galio's hd_idle, league_braum's lo_idle, league_gragas's and league_elise's hd_idle), then <out>.zip.
Dr. Mundo (the user's picks, 2026-10-16: top, add-on) is drawn as two pictures on 1536x1024 landscapes: A = League's
idle (DrMundo_Idle01, the bone saw hanging in the near hand), B = the attack wind-up (DrMundo_Attack2, the saw raised
over his head); hair top to soles about 78 squares of 11 px (~43 game rows at PPU 1.8). No chibi head
(head-share-like-oppi): a small head sunk between huge shoulders, League's own proportions.
The skin hides its ult body, the capacitors, the toe tag, the clipboard and the bag props until an animation shows
them (HIDE); the saw takes the weapon map.
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
IDLE = "DrMundo_Idle01@0"
SWING = "DrMundo_Attack2@250"
HIDE = ["Tongue", "BodyUlt", "Clipboard", "ToeTag", "L_Capacitor", "R_Capacitor", "L_CapacitorUlt", "R_CapacitorUlt",
        "WeaponUlt", "BagProps"]
# name -> (champ, frames, yaw, mirror, size, fit, ground, width, crop: None / "head" / fractions)
RENDERS = {
    "1_mundo_idle": ("DrMundo", [IDLE], 45, False, 1000, 0.60, 0.92, 1.0, "box"),
    "2_mundo_frontal": ("DrMundo", [IDLE], 0, False, 1000, 0.60, 0.92, 1.0, "box"),
    "3_mundo_head": ("DrMundo", [IDLE], 40, False, 2000, 0.60, 0.92, 1.0, (0.30, 0.0, 0.78, 0.30)),
    "4_mundo_back": ("DrMundo", [IDLE], 200, False, 1000, 0.60, 0.92, 1.0, "box"),
    "6_mundo_swing": ("DrMundo", [SWING], 45, False, 1000, 0.60, 0.92, 1.0, "box"),
    "7_mundo_side": ("DrMundo", [IDLE], 90, False, 1000, 0.60, 0.92, 1.0, "box"),
}
# the layout guide: hat top to soles FULL_H px (76 squares of 11) on the 1536x1024 landscape, soles on row SOLE
GUIDES = {
    "8_layout.png": ("1_mundo_idle.png", (1536, 1024), 960, None, 858,
                     "A: hair top to soles 858 px (78 squares of 11); layout only"),
}
STYLE = {
    "9_style_galio.png": os.path.join(SRC, "bard", "style_ref", "galio_hd_idle_x8.png"),
    "10_style_braum.png": os.path.join(SRC, "bard", "style_ref", "braum_lo_idle_x8.png"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_gragas.png": ("gragas", "hd_idle"),
    "12_style_elise.png": ("elise", "hd_idle"),
}


def render(lol, name, spec, out):
    champ, frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "DrMundo", "--submesh-texture", "Weapon=Weapon_TX", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    for s in HIDE:
        cmd += ["--hide-submesh", s]
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
    elif crop:  # fractions of the figure's box
        im = Image.open(path).convert("RGB")
        x0, y0, x1, y1 = _keyed(path).getbbox()
        w, h = x1 - x0, y1 - y0
        im.crop((x0 + int(crop[0] * w), y0 + int(crop[1] * h), x0 + int(crop[2] * w), y0 + int(crop[3] * h))).save(path)
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "DrMundo.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/drmundo/skins/base/drmundoloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_mundo_splash.png"))
    for name, spec in GUIDES.items():
        guide(refs, name, spec)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "drmundo", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
