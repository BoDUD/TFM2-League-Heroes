"""The Codex pack for league_kaisa's PPU redo (assets/source/kaisa/PICTURE_PROMPT_PPU.md): one chibi design picture on
the 11-px grid at PPU 1.5, the way league_xinzhao was redone (tools/art/pack_xinzhao_ppu.py); the actions are posed
after League's clips afterwards (rig_xinzhao_hd.py's way), the effects stay.

    python tools/art/pack_kaisa_ppu.py --out C:/t/ks_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-18: 「接下来可以重做卡莎 还是按赵兴的步骤 让codex生成一下」.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of the big-head model in her idle with the Icathian
Rain pods raised, through tools/lol/pose_ref.py, the skin's hidden submeshes left out: Riot's, kept local, never
committed), refs/5 (the loading-screen art), refs/6 (Codex's approved picture B: the costume and colours to keep),
refs/7 (her game sprite now at 8x: the chibi size, the slim build and the facing), refs/8 (the layout guide) and
<out>/style/9..11 (this pack's Jax, Katarina and Xin Zhao at their PPU 1.5 hd_idle, 8x), then <out>.zip. Render into
a short folder.
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
IDLE = "kaisa_spell4_ready_loop@0"              # her idle with the pods raised (assets/source/kaisa/poses.json design)
# name -> (yaw, size, width, crop "box" or fractions of the figure's box), all mirrored: her chest toward the camera
RENDERS = {
    "1_kaisa_idle": (45, 1000, 1.0, "box"),
    "2_kaisa_side": (90, 1000, 1.0, "box"),
    "3_kaisa_head": (40, 2400, 1.0, (0.18, 0.0, 0.82, 0.42)),
    "4_kaisa_front": (10, 1000, 1.0, "box"),
}
# the raised pods' tips to her soles FULL_H px = 63 squares of 11 px (her 42 game rows x PPU 1.5), soles on row SOLE
CANVAS, SOLE, FULL_H = (1024, 1024), 960, 693


def lp(path):
    """Long-path form: the workspace sits under a long path, deep repo files need the \\\\?\\ prefix on Windows."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


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
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Kaisa", "--hq",
           "--mirror", "--hide-submeshes", "--head", "2.0", "--legs", "0.85", "--hair", "0.6", "--fit-all",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6", "--ground", "0.92",
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", IDLE]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop is None:
        return path
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


def sheet_frame(stem, tag, z):
    """Frame 0 of a sheet tag (stem#sheet.png / #anim.fanim) at z x on grey."""
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    f = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"][tag]["frames"][0]["data"]
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    return pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST)


def guide(refs, tmp, lol):
    """The idle render scaled so the pods' tips to the soles are FULL_H px, soles on row SOLE, centred, on the canvas."""
    full = keyed(render(lol, "full", (45, 1000, 1.0, None), tmp))
    x0, y0, x1, y1 = full.getbbox()
    k = FULL_H / (y1 - y0)
    full = full.resize((round(full.width * k), round(full.height * k)), Image.LANCZOS)
    ox = CANVAS[0] // 2 - round((x0 + x1) / 2 * k)
    oy = SOLE - round(y1 * k)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    can.alpha_composite(full, (ox, oy))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - FULL_H), (CANVAS[0], SOLE - FULL_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"pod tips to soles {FULL_H} px (63 squares of 11); layout only", fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, "8_layout.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    refs, style, tmp = (os.path.join(a.out, d) for d in ("refs", "style", "_tmp"))
    for d in (refs, style, tmp):
        os.makedirs(d, exist_ok=True)
    for name, spec in RENDERS.items():
        render(a.lol, name, spec, refs)
    from riot import Wad
    import pose_ref
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Kaisa.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Kaisa/Skins/Base/KaisaLoadScreen.tex")) \
        .convert("RGB").save(os.path.join(refs, "5_kaisa_splash.png"))
    design = Image.open(lp(os.path.join(SRC, "kaisa", "codex_picture", "kaisa-model-B.png"))).convert("RGBA")
    bg = Image.new("RGBA", design.size, GREY + (255,))
    bg.alpha_composite(design)
    bg.crop(design.getbbox()).convert("RGB").save(os.path.join(refs, "6_kaisa_picture.png"))
    sheet_frame(os.path.join(CHAMPS, "league_kaisa"), "idle", 8).save(os.path.join(refs, "7_kaisa_now.png"))
    guide(refs, tmp, a.lol)
    for n, hero in (("9_style_jax", "league_jax"), ("10_style_katarina", "league_katarina"),
                    ("11_style_xinzhao", "league_xinzhao")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.rmtree(tmp)
    shutil.copyfile(lp(os.path.join(SRC, "kaisa", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
