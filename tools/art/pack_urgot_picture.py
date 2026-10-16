"""Build the step-0 pack for Codex (assets/source/urgot/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_urgot_picture.py --out %TEMP%/ur_work/urgot_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.2-1.5 heroes at their dense frames, 8x, cut
from their sheets), then <out>.zip. Render into a short folder (%TEMP%): pose_ref's saves under ur/dist pass MAX_PATH.
Urgot (the user's picks, 2026-10-16: top, add-on, PPU 1.5) is a pale, bald, gas-masked man grown into a six-legged
bronze walker, a big shotgun-cannon arm held over his head. He is wider than tall, so both body pictures go on
1536x1536 squares: A = League's idle (Urgot_Idle: the cannon arm raised over his head, pointing forward), B = his shot
(Urgot_Attack1_InCombat_Fwd at 160 ms: the cannon swung down at the target, the body leaning in). Cannon top to leg
tips about 72 squares of 11 px (~40 game rows at 1.8 squares a game pixel; read back and brought to PPU 1.5 by the
restyle). The body is one submesh with one colour map (Urgot_Base.tex; pose_ref used to pick a particle _TX_CM).
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
IDLE = "Urgot_Idle@0"
SHOT = "Urgot_Attack1_InCombat_Fwd@160"
# name -> (frame, yaw, size, crop: "box" / (x0, y0, x1, y1) fractions of the full render)
RENDERS = {
    "1_urgot_idle": (IDLE, 45, 1600, "box"),
    "2_urgot_frontal": (IDLE, 0, 1600, "box"),
    "3_urgot_head": (IDLE, 30, 3200, (0.40, 0.10, 0.66, 0.36)),
    "4_urgot_back": (IDLE, 200, 1600, "box"),
    "6_urgot_shot": (SHOT, 45, 1600, "box"),
    "7_urgot_shot_side": (SHOT, 80, 1600, "box"),
    "9_urgot_legs": (IDLE, 45, 3200, (0.08, 0.40, 0.95, 0.92)),
}
# cannon top to leg tips CANNON_H px (72 squares of 11) on the 1536 square, leg tips on row SOLE, centred; the shot is
# scaled like the idle (one size for both)
CANNON_H = 792
SOLE = 1400
GUIDES = {
    "8a_layout_A.png": ("1_urgot_idle.png", "A: League's idle; cannon top to leg tips 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("6_urgot_shot.png", "B: his shot; same scale; layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_drmundo.png": ("drmundo", "hd_idle"),
    "12_style_tahmkench.png": ("tahmkench", "hd_idle"),
    "13_style_jayce.png": ("jayce", "hd_idle"),
    "14_style_pantheon.png": ("pantheon", "hd_idle"),
}
SIZE_W = 1.4    # cell width as a fraction of the size: he is wider than tall
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Urgot",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(SIZE_W), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    if crop == "box":
        x0, y0, x1, y1 = _keyed(path).getbbox()
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    else:
        fx0, fy0, fx1, fy1 = crop
        im = im.crop((round(fx0 * im.width), round(fy0 * im.height), round(fx1 * im.width), round(fy1 * im.height)))
    im.save(path)
    print(name, im.size)
    return path


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
    can.alpha_composite(fig, (x0, max(0, y0)))
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
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Urgot.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/urgot/skins/base/urgotloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_urgot_splash.png"))
    idle = _keyed(os.path.join(refs, "1_urgot_idle.png"))
    k = CANNON_H / idle.crop(idle.getbbox()).height
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)  # same camera size, so one scale for both
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "urgot", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
