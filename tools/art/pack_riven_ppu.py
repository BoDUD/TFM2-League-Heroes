"""The Codex pack for league_riven's PPU redo (assets/source/riven/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 1.5 in League's idle (the broken blade over her back), her proportions now (40 game rows), plus one
picture of the blade reforged (her R: the green energy blade grown out of the broken one) on the same grid, the way
league_darius and league_fiora were redone (tools/art/pack_darius_ppu.py); the actions are posed after League's clips
afterwards (rig_darius_hd.py's way), the effects stay.

    python tools/art/pack_riven_ppu.py --out C:/t/rv_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-18: 「下一个重做锐雯吧」.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of her idle, the head enlarged as poses.json's chibi
settings, through tools/lol/pose_ref.py: Riot's, kept local, never committed; 4 = her blade close up), refs/5 (the
loading-screen art), refs/6 (the approved design picture: assets/source/native/riven_native.png - the costume, the
colours, the blade), refs/7 (her game sprite now at 8x: the proportions), refs/8 (the layout guide: her sprite now as a
flat silhouette at the new size), refs/12 (her R-form attack frame now at 8x: the reforged blade) and
<out>/style/9..11 (this pack's Fiora, Kai'Sa and Camille at their PPU hd_idle, 8x), then <out>.zip.
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
IDLE = "riven_idle1@0"                          # the broken blade over her back pointing up-right (poses.json design)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box); not mirrored (poses.json camera)
RENDERS = {
    "1_riven_idle": (45, 1000, 1.2, "box"),
    "2_riven_side": (90, 1000, 1.2, "box"),
    "3_riven_head": (40, 2400, 1.2, (0.0, 0.0, 0.62, 0.42)),
    "4_riven_blade": (45, 2000, 1.2, (0.35, 0.1, 1.0, 0.55)),
}
# her hair's tips to her soles 40 game rows = 60 squares = FULL_H px, soles on row SOLE
CANVAS, SOLE, FULL_H = (1024, 1024), 960, 660


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
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Riven", "--hq",
           "--head", "2.6", "--legs", "0.8", "--hair", "0.5", "--pitch", "25",
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


def r_frame(z):
    """attack_r's 4th frame (the reforged blade held out) at z x on grey."""
    stem = os.path.join(CHAMPS, "league_riven")
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    f = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]["attack_r"]["frames"][3]["data"]
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    return pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST)


def guide(refs):
    """Her sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), soles on row SOLE, centred: the size
    and the place only."""
    spr = sheet_frame(os.path.join(CHAMPS, "league_riven"), "idle")
    k = FULL_H / spr.height
    a = spr.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    a = a.resize((round(spr.width * k), FULL_H), Image.NEAREST)
    sil = Image.new("RGBA", a.size, (150, 160, 185, 255))
    sil.putalpha(a)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    ox = (CANVAS[0] - a.width) // 2
    can.alpha_composite(sil, (ox, SOLE - FULL_H))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(110, 110, 110, 255), width=2)
    d.line([(0, SOLE - FULL_H), (CANVAS[0], SOLE - FULL_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"hair tips to soles {FULL_H} px (60 squares of 11); layout only, not the pose", fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "8_layout.png"))
    print("layout", a.size, "at", ox, SOLE - FULL_H)


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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Riven.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Riven/Skins/Base/RivenLoadScreen.tex")) \
        .convert("RGB").save(os.path.join(refs, "5_riven_splash.png"))
    pic = Image.open(lp(os.path.join(SRC, "native", "riven_native.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 24, pic.height + 24), GREY + (255,))
    bg.alpha_composite(pic, (12, 12))
    bg.convert("RGB").save(os.path.join(refs, "6_riven_picture.png"))
    sheet_frame(os.path.join(CHAMPS, "league_riven"), "idle", 8).save(os.path.join(refs, "7_riven_now.png"))
    r_frame(8).save(os.path.join(refs, "12_riven_r_blade_now.png"))
    guide(refs)
    for n, hero in (("9_style_fiora", "league_fiora"), ("10_style_kaisa", "league_kaisa"),
                    ("11_style_camille", "league_camille")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "riven", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
