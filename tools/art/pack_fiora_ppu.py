"""The Codex pack for league_fiora's PPU redo (assets/source/fiora/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 1.5, her proportions now (40 game rows hair top to soles, the rapier held straight out), the way
league_kaisa and league_camille were redone (tools/art/pack_camille_ppu.py); the actions are posed after League's
clips afterwards (rig_camille_hd.py's way), the effects stay.

    python tools/art/pack_fiora_ppu.py --out C:/t/fi_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-18: 「继续重做剑姬吧」.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of her idle, the head enlarged as poses.json's chibi
settings, through tools/lol/pose_ref.py: Riot's, kept local, never committed; 4 = her sword arm close up), refs/5
(the loading-screen art), refs/6 (Codex's approved design picture B: the costume and colours to keep), refs/7 (her
game sprite now at 8x: the proportions, the rapier's length and the facing), refs/8 (the layout guide: her sprite
now as a flat silhouette at the new size) and <out>/style/9..11 (this pack's Xin Zhao, Kai'Sa and Camille at their
PPU hd_idle, 8x), then <out>.zip. Render into a short folder.
Her rapier is long (the sprite is 62 game px wide, 93 squares at PPU 1.5), so the canvas is 1536x1024.
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
IDLE = "Fiora_Idle1@0"                          # en garde, the rapier held out to the front (poses.json design)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box); not mirrored (poses.json camera)
RENDERS = {
    "1_fiora_idle": (45, 1000, 1.4, "box"),
    "2_fiora_side": (90, 1000, 1.4, "box"),
    "3_fiora_head": (40, 2400, 1.4, (0.0, 0.0, 0.5, 0.36)),
    "4_fiora_sword_arm": (45, 2000, 1.4, (0.3, 0.28, 1.0, 0.62)),
}
PPU, SQ = 1.5, 11                               # each game pixel 1.5 squares of 11 px
# her hair's top to her soles 40 game rows = 60 squares = FULL_H px, soles on row SOLE
CANVAS, SOLE, FULL_H = (1536, 1024), 960, 660


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
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Fiora", "--hq",
           "--hide-submeshes", "--head", "2.3", "--legs", "0.8", "--hair", "0.6", "--fit-all", "--pitch", "25",
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


def guide(refs):
    """Her sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), soles on row SOLE, the body a
    little left of centre so the rapier fits: the size and the place only."""
    spr = sheet_frame(os.path.join(CHAMPS, "league_fiora"), "idle")
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
    d.text((24, 24), f"hair top to soles {FULL_H} px (60 squares of 11); rapier tip at x {ox + a.width}; "
                     "layout only", fill=(60, 60, 60, 255))
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Fiora.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Fiora/Skins/Base/FioraLoadScreen.tex")) \
        .convert("RGB").save(os.path.join(refs, "5_fiora_splash.png"))
    pic = Image.open(lp(os.path.join(SRC, "fiora", "codex_model", "fiora_design_B.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 24, pic.height + 24), GREY + (255,))
    bg.alpha_composite(pic, (12, 12))
    bg.convert("RGB").save(os.path.join(refs, "6_fiora_picture.png"))
    sheet_frame(os.path.join(CHAMPS, "league_fiora"), "idle", 8).save(os.path.join(refs, "7_fiora_now.png"))
    guide(refs)
    for n, hero in (("9_style_xinzhao", "league_xinzhao"), ("10_style_kaisa", "league_kaisa"),
                    ("11_style_camille", "league_camille")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "fiora", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
