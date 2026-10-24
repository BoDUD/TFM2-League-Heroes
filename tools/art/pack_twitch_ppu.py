"""The Codex pack for league_twitch's PPU redo (assets/source/twitch/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 2.2 in his crossbow stance (League's attack pose, the approved design B), at his proportions now -
the way Ahri and Lux were redone (tools/art/pack_ahri_ppu.py on ahri-ppu22, tools/art/pack_lux_ppu.py; Codex's raw
picture read back by design_lux_hd.py's way).

    python tools/art/pack_twitch_ppu.py --out C:/t/tw_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-24: 「我们利用PPU可以重做一下图奇 有不少英雄已经重做过了 可以参考一下经验」.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of his stance, the head enlarged to a chibi's, through
tools/lol/pose_ref.py with assets/source/twitch/poses.json's camera and chibi settings: Riot's, kept local, never
committed; 2 = more from the side, 3 = his head close up, 4 = from behind: the backpack and the tail), refs/5 (the
loading-screen art), refs/6 (his approved picture B: assets/source/twitch/codex_picture/twitch-model-B.png - the
costume, the colours, the crossbow), refs/7 (his game sprite now at 8x: the proportions), refs/8 (the layout guide:
his sprite now as a flat silhouette at the new size) and <out>/style/9..11 (this pack's Caitlyn, Jinx and Varus at
their PPU hd_idle, 8x), then <out>.zip.
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
STANCE = "twitch_base_attack1@0"                     # the design pose (poses.json "design"): the crossbow levelled
# name -> (yaw, size, width, crop "box" or fractions of the figure's box); mirrored like poses.json's camera (he faces
# right as the sprite does, his chest to the front)
RENDERS = {
    "1_twitch_stance": (30, 1000, 1.6, "box"),
    "2_twitch_side": (70, 1000, 1.6, "box"),
    "3_twitch_head": (30, 2400, 1.6, (0.3, 0.0, 0.9, 0.5)),
    "4_twitch_back": (150, 1000, 1.6, "box"),
}
CANVAS = (1536, 1024)
SOLE = 960                                      # the soles' row
SQ = 11                                         # px a square
PPU = 2.2


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
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Twitch",
           "--hq", "--head", "1.5", "--pitch", "20", "--mirror", "--hide-submeshes",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6", "--ground", "0.92",
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", STANCE]
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


def guide(refs, spr):
    """His sprite now as a flat silhouette at PPU 2.2 (each game pixel 24.2 px), soles on row SOLE, centred: the size
    and the place only."""
    full = round(spr.height * PPU * SQ)
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
    d.text((24, 24), f"top of the backpack to soles {full} px ({round(spr.height * PPU)} squares of {SQ}); "
                     "layout only, not the pose", fill=(60, 60, 60, 255))
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Twitch.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Twitch/Skins/Base/TwitchLoadScreen.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "5_twitch_splash.png"))
    pic = Image.open(lp(os.path.join(SRC, "twitch", "codex_picture", "twitch-model-B.png"))).convert("RGB")
    lum = pic.convert("L").point(lambda v: 255 if v >= 40 else 0)
    pic.crop(lum.getbbox()).save(os.path.join(refs, "6_twitch_picture.png"))
    now = sheet_frame(os.path.join(CHAMPS, "league_twitch"), "idle_base")
    sheet_frame(os.path.join(CHAMPS, "league_twitch"), "idle_base", 8).save(os.path.join(refs, "7_twitch_now.png"))
    guide(refs, now)
    for n, hero in (("9_style_caitlyn", "league_caitlyn"), ("10_style_jinx", "league_jinx"),
                    ("11_style_varus", "league_varus")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "twitch", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| his sprite now", now.size)


if __name__ == "__main__":
    main()
