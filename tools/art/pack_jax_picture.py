"""The Codex pack for league_jax's new design (assets/source/jax/PICTURE_PROMPT.md): the 2026-10-16 chibi from Codex's
picture faced the camera, not front-right like the pack's heroes (the user: 「你不应该学其他已经完美的英雄四分之三站姿吗」,
then on the mirrored copy 「这是右前方？」, and picked a Codex redraw of the design; the actions stay posed after League's
clips by tools/art/rig_jax_hd.py).

    python tools/art/pack_jax_picture.py --out dist/jax_packs/jax_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of the chibi model through tools/lol/pose_ref.py: Riot's,
kept local, never committed), <out>/refs/5 (assets/source/jax/hd/chibi.png, the chibi design it replaced: the costume to
keep), 6 (the old 1x sprite at 8x: the
facing and the lamp held low ahead), 7 (the layout guide) and <out>/style/8..9 (this pack's Darius and Riven at their
PPU 1.5 hd_idle, 8x), then <out>.zip.
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
SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "Idle1_v04@0"
# name -> (frames, yaw, size, fit, ground, width, crop)
RENDERS = {
    "1_jax_idle": ([IDLE], 45, 1000, 0.60, 0.92, 1.0, "box"),
    "2_jax_side": ([IDLE], 90, 1000, 0.60, 0.92, 1.0, "box"),
    "3_jax_head": ([IDLE], 40, 2000, 0.60, 0.92, 1.0, (0.25, 0.0, 0.80, 0.42)),
    "4_jax_front": ([IDLE], 0, 1000, 0.60, 0.92, 1.0, "box"),
}
CANVAS, SOLE, FULL_H = (1536, 1024), 960, 594         # hood top to soles 54 squares of 11 px (36 game rows x 1.5)


def keyed(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def render(lol, name, spec, out):
    frames, yaw, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Jax",
           "--submesh-texture", "Weapon=Weapon", "--hide-submesh", "Bluefish", "--hide-submesh", "Goldfish",
           "--head", "2.0", "--legs", "0.8", "--hair", "0.6", "--hq", "--bg", ",".join(map(str, GREY)),
           "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground), "--width", str(width),
           "--yaw", str(yaw), "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = keyed(path).getbbox()
    if crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))).save(path)
    else:
        w, h = x1 - x0, y1 - y0
        im.crop((x0 + int(crop[0] * w), y0 + int(crop[1] * h), x0 + int(crop[2] * w), y0 + int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)


def sheet_frame(stem, tag, z, ref=None):
    """Frame 0 of a sheet tag (stem#sheet.png / #anim.fanim; ref: a git revision) at z x on grey."""
    if ref:
        png = subprocess.run(["git", "show", f"{ref}:league/champions/{os.path.basename(stem)}#sheet.png"],
                             cwd=REPO, capture_output=True, check=True).stdout
        fan = subprocess.run(["git", "show", f"{ref}:league/champions/{os.path.basename(stem)}#anim.fanim"],
                             cwd=REPO, capture_output=True, check=True).stdout
        import io
        sheet = Image.open(io.BytesIO(png)).convert("RGBA")
        anims = json.loads(fan.decode("utf-8-sig"))["anims"]
    else:
        sheet = Image.open(stem + "#sheet.png").convert("RGBA")
        anims = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    return pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST)


def guide(refs):
    """The idle render with its hood top to soles FULL_H px, the soles on row SOLE, centred, on the 1536x1024 canvas."""
    full = keyed(os.path.join(refs, "1_jax_idle.png"))
    fig = full.crop(full.getbbox())
    k = FULL_H / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = (CANVAS[0] - fig.width) // 2, SOLE - fig.height
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(150, 150, 150, 255), width=2)
    d.text((24, 24), f"hood top to soles {FULL_H} px (54 squares of 11); layout only", fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "7_layout.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
    chibi = Image.open(os.path.join(SRC, "jax", "hd", "chibi.png")).convert("RGBA")
    bg = Image.new("RGBA", chibi.size, GREY + (255,))
    bg.alpha_composite(chibi)
    bg.convert("RGB").save(os.path.join(refs, "5_jax_costume.png"))
    sheet_frame(os.path.join(CHAMPS, "league_jax"), "idle", 8, ref="origin/main").save(
        os.path.join(refs, "6_jax_old_sprite.png"))
    guide(refs)
    sheet_frame(os.path.join(CHAMPS, "league_darius"), "hd_idle", 8).save(os.path.join(style, "8_style_darius.png"))
    sheet_frame(os.path.join(CHAMPS, "league_riven"), "hd_idle", 8).save(os.path.join(style, "9_style_riven.png"))
    shutil.copyfile(os.path.join(SRC, "jax", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
