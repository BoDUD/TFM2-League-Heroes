"""The Codex pack for league_jinx's PPU redo (assets/source/jinx/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 1.5 in League's idle (Pow-Pow the minigun held at her hip), at her proportions now, the way
league_caitlyn and league_varus were redone (tools/art/pack_caitlyn_ppu.py, pack_varus_ppu.py).

    python tools/art/pack_jinx_ppu.py --out C:/t/jx_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-23: 「接下来可以重做金克丝」.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of her idle, the head enlarged as poses.json's chibi
settings, through tools/lol/pose_ref.py: Riot's, kept local, never committed; 3 = her head close up, 4 = the minigun),
refs/5 (the loading-screen art), refs/6 (her approved design picture: assets/source/native/jinx_native.png - the
costume, the colours, the guns), refs/7 (her game sprite now at 8x: the proportions), refs/8 (the layout guide: her
sprite now as a flat silhouette at the new size) and <out>/style/9..11 (this pack's Caitlyn, Varus and Riven at their
PPU hd_idle, 8x), then <out>.zip.
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
SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "Jinx_minigun_idle1@0"                               # poses.json's design pose
# name -> (yaw, size, width, crop "box" or fractions of the figure's box); unmirrored like poses.json's camera (she
# faces right as the sprite does)
RENDERS = {
    "1_jinx_idle": (45, 1000, 1.2, "box"),
    "2_jinx_side": (85, 1000, 1.2, "box"),
    "3_jinx_head": (45, 2400, 1.2, (0.1, 0.0, 0.9, 0.45)),
    "4_jinx_minigun": (45, 2000, 1.4, (0.2, 0.3, 1.0, 0.85)),
}
CANVAS = (1024, 1024)
SOLE = 960                                      # the soles' row
SQ = 11                                         # px a square
PPU = 1.5


def lp(path):
    """Long-path form: the workspace sits under a long path, deep repo files need the \\\\?\\ prefix on Windows."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


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
    yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Jinx",
           "--hq", "--head", "2.0", "--legs", "0.8", "--hair", "0.5", "--pitch", "25",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6", "--ground", "0.92",
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", IDLE]
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
    return path


def sheet_frame(stem, tag, z=None):
    """Frame 0 of a sheet tag (stem#sheet.png / #anim.fanim), cropped; at z x on grey when z is given."""
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    f = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"][tag]["frames"][0]["data"]
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    if z is None:
        return im
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    return pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST)


def guide(refs, rows):
    """Her sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), soles on row SOLE, centred: the size
    and the place only."""
    spr = sheet_frame(os.path.join(CHAMPS, "league_jinx"), "idle")
    full = round(rows * PPU * SQ)
    k = full / spr.height
    a = spr.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    a = a.resize((round(spr.width * k), full), Image.NEAREST)
    sil = Image.new("RGBA", a.size, (150, 160, 185, 255))
    sil.putalpha(a)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    ox = (CANVAS[0] - a.width) // 2
    can.alpha_composite(sil, (ox, SOLE - full))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(110, 110, 110, 255), width=2)
    d.line([(0, SOLE - full), (CANVAS[0], SOLE - full)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"hair top to soles {full} px ({round(rows * PPU)} squares of {SQ}); layout only, not the pose",
           fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "8_layout.png"))
    print("layout", a.size, "at", ox, SOLE - full)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    refs, style = (os.path.join(a.out, d) for d in ("refs", "style"))
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    for name, spec in RENDERS.items():
        render(a.lol, name, spec, refs)
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Jinx.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Jinx/Skins/Base/JinxLoadScreen.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "5_jinx_splash.png"))
    pic = Image.open(lp(os.path.join(SRC, "native", "jinx_native.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 4, pic.height + 4), GREY + (255,))
    bg.alpha_composite(pic, (2, 2))
    z = max(1, round(600 / bg.height))
    bg.convert("RGB").resize((bg.width * z, bg.height * z), Image.NEAREST).save(os.path.join(refs, "6_jinx_picture.png"))
    now = sheet_frame(os.path.join(CHAMPS, "league_jinx"), "idle")
    sheet_frame(os.path.join(CHAMPS, "league_jinx"), "idle", 8).save(os.path.join(refs, "7_jinx_now.png"))
    guide(refs, now.height)
    for n, hero in (("9_style_caitlyn", "league_caitlyn"), ("10_style_varus", "league_varus"),
                    ("11_style_riven", "league_riven")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "jinx", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| her sprite now", now.size)


if __name__ == "__main__":
    main()
