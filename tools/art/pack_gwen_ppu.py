"""The Codex pack for league_gwen's PPU redo (assets/source/gwen/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 2.2, TRACED from her game sprite now (the pose with the scissors over her shoulder, the costume, the
colours, the proportions), only denser - and her eyes redrawn as League's big round eyes. The user, 2026-10-25:
「接下来可以优化格温 格温感觉只要利用PPU调高像素 还有眼睛那里改一下就可以了」, then picked the whole body redrawn dense
(not only the head) and League's big round eyes.

    python tools/art/pack_gwen_ppu.py --out C:/t/gw_pack [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders through tools/lol/pose_ref.py with
assets/source/gwen/poses.json's chibi settings, mirrored so she faces right as the sprite does: 1 = her run's carry
(the sprite's pose), 2 = her head close up (the eyes), 3 = her idle (the costume), 4 = from behind; Riot's, kept local,
never committed), refs/5 (the loading-screen art), refs/6 (Codex's earlier picture of her, assets/source/gwen/
codex_picture/gwen-model-A.png: the face and the eyes), refs/7 (her game sprite now at 8x: THE picture to trace),
refs/8 (the layout guide: her sprite now as a flat silhouette at the new size) and <out>/style/9..11 (this pack's
Annie, Ahri and Lux at their PPU 2.2 hd_idle, 8x), then <out>.zip.
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
IDLE = "idle@0"
CARRY = "run@150"                                    # her run's carry: the sprite's pose                                     # League's idle: the design pose (poses.json "design")
# name -> (yaw, size, width, crop "box" or fractions of the figure's box, frame); mirrored like poses.json's camera
# (she faces right as the sprite does)
RENDERS = {
    "1_gwen_carry": (35, 1000, 1.4, "box", CARRY),
    "2_gwen_head": (35, 2400, 1.2, (0.15, 0.0, 0.85, 0.42), IDLE),
    "3_gwen_idle": (35, 1000, 1.4, "box", IDLE),
    "4_gwen_back": (150, 1000, 1.4, "box", IDLE),
}
CANVAS = (1024, 1536)
SOLE = 1472                                      # the soles' row
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
    yaw, size, width, crop, frame = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Gwen",
           "--hq", "--head", "2.4", "--legs", "0.85", "--hair", "0.6", "--pitch", "20", "--mirror",
           "--hide-submesh", "Doll", "--hide-submesh", "Needle", "--hide-submesh", "Scissors_A_Smear",
           "--submesh-texture", "Scissors=Weapon",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6", "--ground", "0.92",
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", frame]
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
    """Her sprite now as a flat silhouette at PPU 2.2 (each game pixel 24.2 px), soles on row SOLE, centred: the size
    and the place only."""
    spr = sheet_frame(os.path.join(CHAMPS, "league_gwen"), "idle")
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
    d.text((24, 24), f"blade tip to soles {full} px ({round(rows * PPU)} squares of {SQ}); layout only, not the pose",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Gwen.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Gwen/Skins/Base/GwenLoadScreen_0.tex".lower())) \
        .convert("RGB").save(os.path.join(refs, "5_gwen_splash.png"))
    pic = Image.open(lp(os.path.join(SRC, "gwen", "codex_picture", "gwen-model-A.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 4, pic.height + 4), GREY + (255,))
    bg.alpha_composite(pic, (2, 2))
    z = max(1, round(600 / bg.height))
    bg.convert("RGB").resize((bg.width * z, bg.height * z), Image.NEAREST).save(os.path.join(refs, "6_gwen_codex_picture.png"))
    now = sheet_frame(os.path.join(CHAMPS, "league_gwen"), "idle")
    sheet_frame(os.path.join(CHAMPS, "league_gwen"), "idle", 8).save(os.path.join(refs, "7_gwen_now.png"))
    guide(refs, now.height)
    for n, hero in (("9_style_annie", "league_annie"), ("10_style_ahri", "league_ahri"),
                    ("11_style_lux", "league_lux")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "gwen", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp, "| her sprite now", now.size)


if __name__ == "__main__":
    main()
