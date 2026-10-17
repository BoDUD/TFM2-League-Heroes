"""Build the step-0 pack for Codex (assets/source/kindred/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_kindred_picture.py --out dist/kindred_packs/kindred_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..13 (League renders, the loading-screen art and two layout guides
pasted from the renders: Riot's, kept local, never committed) and <out>/style/14..16 (this pack's restyled PPU
heroes: zeri, nilah, nidalee hd_idle at 8x, assets/source/kindred/style_ref), then <out>.zip.
Kindred is two figures drawn as ONE sprite (the user's pick, 2026-10-14): Lamb, a slim white-furred huntress in a
dark violet lamb mask with glowing teal eyes, white fur hood and mane, blue-violet goat legs ending in black hooves,
holding a curled spectral bow (dark violet limbs with teal swirls and pale teal hook tips); and Wolf, a floating
dark-indigo wolf HEAD whose shaggy mane streams back into ragged smoke (no body, no legs) with a white bone mask over
the brow and one glowing blue eye. The wolf rides in her frames: version A = League's idle (Lamb on one hoof, bow
upright) with Wolf floating behind her at shoulder height on the image left; version B = Lamb on both hooves, bow
held low in the front hand, Wolf low behind her hips.
The renders: Lamb at yaw 45 (no mirror: Kindred's models face image right at yaw 45-90), Wolf the same.
The look: the PPU heroes' one look of 2026-10-13 (league_zeri's: stocky, about 2.2 squares a game pixel, a thick
outline): Lamb's mask-ear tips to hooves about 84 squares of 8 px, on a 1536x1024 landscape canvas.
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
# name -> (champ, frames, yaw, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_kindred_lamb_front": ("Kindred", ["Lamb_Idle_loop@0"], 45, 1000, 0.80, 0.94, 1.0, None),
    "2_kindred_lamb_frontal": ("Kindred", ["Lamb_Idle_loop@0"], 0, 1000, 0.80, 0.94, 1.0, None),
    "3_kindred_lamb_head": ("Kindred", ["Lamb_Idle_loop@0"], 40, 2600, 0.80, 0.94, 0.9, "head"),
    "4_kindred_lamb_back": ("Kindred", ["Lamb_Idle_loop@0"], 200, 1000, 0.80, 0.94, 1.0, None),
    "6_kindred_lamb_actions": ("Kindred", ["Lamb_Attack1@911", "Lamb_Spell3@778", "Lamb_Spell4@689", "Lamb_run@0"],
                               80, 800, 0.55, 0.95, 1.6, None),
    "7_kindred_lamb_bow": ("Kindred", ["Lamb_Idle_loop@0"], 45, 2400, 0.80, 0.94, 0.9, (0.38, 0.10, 0.90, 0.80)),
    "8_kindred_lamb_side": ("Kindred", ["Lamb_Idle_loop@0"], 90, 1000, 0.80, 0.94, 1.0, None),
    "9_kindred_wolf_front": ("KindredWolf", ["Wolf_Idle_base_movement@0"], 70, 900, 0.60, 0.90, 1.3, None),
    "10_kindred_wolf_side": ("KindredWolf", ["Wolf_Idle_base_movement@0"], 100, 900, 0.60, 0.90, 1.3, None),
    "11_kindred_wolf_head": ("KindredWolf", ["Wolf_Idle_base_movement@0"], 60, 2000, 0.60, 0.90, 1.3,
                             (0.45, 0.10, 0.95, 0.75)),
}
# the 2026-10-13 one look of the PPU heroes (league_zeri's, PR #249 ppu-chunky, tools/art/ppu_restyle.py): their
# restyled hd_idle frames at 8x (one square = one dense pixel), assets/source/kindred/style_ref
STYLE = {
    "14_style_zeri.png": os.path.join(SRC, "kindred", "style_ref", "zeri_hd_idle_x8.png"),
    "15_style_nilah.png": os.path.join(SRC, "kindred", "style_ref", "nilah_hd_idle_x8.png"),
    "16_style_nidalee.png": os.path.join(SRC, "kindred", "style_ref", "nidalee_hd_idle_x8.png"),
}
# layout guides on the 1536x1024 canvas: Lamb's mask-ear tips to hooves LAMB_H px (84 squares of 8), soles on SOLE;
# the wolf's snout-to-mane-tip length as a fraction of LAMB_H and where its box sits (left, top as fractions of LAMB_H
# from Lamb's box: negative left = behind her on the image left)
CANVAS = (1536, 1024)
LAMB_H = 672
SOLE = 900
LAMB_X = 760
WOLF_LEN = 0.72
GUIDES = {
    "12_layout_A.png": dict(wolf_dx=-0.62, wolf_top=0.10, label="A: League idle, Wolf floats behind her at shoulder height"),
    "13_layout_B.png": dict(wolf_dx=-0.66, wolf_top=0.48, label="B: Wolf floats low behind her hips"),
}


def render(lol, name, spec, out):
    champ, frames, yaw, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Kindred", "--hq", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop == "head":  # the top 30% of the figure, a margin round it
        fig = cut(path)
        box = Image.open(path).convert("RGBA")
        full = cut_box(path)
        top = full[1]
        h = round((full[3] - full[1]) * 0.30)
        band = fig.crop((0, 0, fig.width, h)).getbbox()
        x0, x1 = full[0] + band[0], full[0] + band[2]
        m = 40
        can = Image.new("RGBA", (x1 - x0 + 2 * m, h + 2 * m), GREY + (255,))
        can.alpha_composite(box.crop((max(0, x0 - m), max(0, top - m), x1 + m, top + h + m)),
                            (max(0, x0 - m) - (x0 - m), max(0, top - m) - (top - m)))
        can.convert("RGB").save(path)
    elif crop:
        im = Image.open(path)
        w, h = im.size
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)


def cut_box(path):
    return _keyed(path).getbbox()


def cut(path):
    """The figure of a grey-ground render, as RGBA cropped to its box."""
    im = _keyed(path)
    return im.crop(im.getbbox())


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def guides(refs):
    lamb = cut(os.path.join(refs, "1_kindred_lamb_front.png"))
    lamb = lamb.resize((round(lamb.width * LAMB_H / lamb.height), LAMB_H), Image.LANCZOS)
    wolf = cut(os.path.join(refs, "9_kindred_wolf_front.png"))
    wl = round(LAMB_H * WOLF_LEN)
    wolf = wolf.resize((wl, round(wolf.height * wl / wolf.width)), Image.LANCZOS)
    top = SOLE - LAMB_H
    for name, g in GUIDES.items():
        can = Image.new("RGBA", CANVAS, GREY + (255,))
        wx = LAMB_X + round(g["wolf_dx"] * LAMB_H)
        wy = top + round(g["wolf_top"] * LAMB_H)
        can.alpha_composite(wolf, (wx, wy))  # behind her
        can.alpha_composite(lamb, (LAMB_X, top))
        d = ImageDraw.Draw(can)
        d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(150, 150, 150, 255), width=2)
        d.text((24, 24), g["label"] + "  (layout only: where the two figures go, how big they are)",
               fill=(60, 60, 60, 255))
        can.convert("RGB").save(os.path.join(refs, name))
        print(name, "wolf box", (wx, wy, wx + wolf.width, wy + wolf.height), "lamb box",
              (LAMB_X, top, LAMB_X + lamb.width, SOLE))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Kindred.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/kindred/skins/base/kindredloadscreen.tex"))
        splash.convert("RGB").save(os.path.join(refs, "5_kindred_splash.png"))
    guides(refs)
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "kindred", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
