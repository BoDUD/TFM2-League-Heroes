"""The Codex pack for league_xinzhao's PPU redo (assets/source/xinzhao/PICTURE_PROMPT_PPU.md): one chibi design picture
on the 11-px grid at PPU 1.5, the way league_jax was redone (tools/art/pack_jax_picture.py); the actions are posed
after League's clips afterwards (rig_jax_hd.py's way), the effects stay.

    python tools/art/pack_xinzhao_ppu.py --out C:/t/xz_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-18: 「我想用PPU重做一下赵信的模型 还是Q版的 怎么让GPT生成模型 给我写好提示词」.
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of the big-head model through tools/lol/pose_ref.py,
the skin's hidden 'Hair' submesh left out - it draws a dark lump with gold horns over his head: Riot's, kept local,
never committed), refs/5 (the loading-screen art: the topknot), refs/6 (Codex's approved picture A: the costume, colours and spear to keep),
refs/7 (his game sprite now at 8x: the size and the facing), refs/8 (the layout guide) and <out>/style/9..11 (this
pack's Jax, Katarina and Pantheon at their PPU 1.5 hd_idle, 8x), then <out>.zip. Render into a short folder.
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
IDLE = "Idlebase@0"
# name -> (yaw, size, width, crop "box" or fractions of the figure's box), all mirrored: his chest toward the camera
RENDERS = {
    "1_xinzhao_idle": (45, 1000, 1.6, "box"),
    "2_xinzhao_side": (90, 1000, 1.6, "box"),
    "3_xinzhao_head": (40, 2400, 1.6, (0.30, 0.0, 0.70, 0.36)),
    "4_xinzhao_front": (10, 1000, 1.6, "box"),
}
# topknot top to soles FULL_H px = 63 squares of 11 px (his 42 game rows x PPU 1.5), soles on row SOLE
CANVAS, SOLE, FULL_H = (1536, 1024), 960, 693


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


def render(lol, name, spec, out, body_only=False):
    yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "XinZhao", "--hq",
           "--mirror", "--hide-submesh", "Hair", "--head", "2.0", "--legs", "0.8", "--fit-all",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", "0.6", "--ground", "0.92",
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", IDLE]
    if body_only:
        cmd += ["--hide-submesh", "Weapon"]
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
    """The idle render (spear in) scaled so the body without the spear is FULL_H px topknot to soles, soles on row SOLE,
    the body centred, on the 1536x1024 canvas."""
    body = keyed(render(lol, "body", (45, 1000, 1.6, None), tmp, body_only=True))
    full = keyed(render(lol, "full", (45, 1000, 1.6, None), tmp))
    bx0, by0, bx1, by1 = body.getbbox()
    k = FULL_H / (by1 - by0)
    full = full.resize((round(full.width * k), round(full.height * k)), Image.LANCZOS)
    ox = CANVAS[0] // 2 - round((bx0 + bx1) / 2 * k)
    oy = SOLE - round(by1 * k)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    can.alpha_composite(full, (ox, oy))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - FULL_H), (CANVAS[0], SOLE - FULL_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), f"topknot top to soles {FULL_H} px (63 squares of 11); layout only", fill=(60, 60, 60, 255))
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "XinZhao.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/XinZhao/Skins/Base/XinZhaoReworkLoadScreen_0.tex")) \
        .convert("RGB").save(os.path.join(refs, "5_xinzhao_splash.png"))
    design = Image.open(lp(os.path.join(SRC, "xinzhao", "codex_picture", "xinzhao-model-A.png"))).convert("RGBA")
    bg = Image.new("RGBA", design.size, GREY + (255,))
    bg.alpha_composite(design)
    bg.crop(design.getbbox()).convert("RGB").save(os.path.join(refs, "6_xinzhao_picture.png"))
    sheet_frame(os.path.join(CHAMPS, "league_xinzhao"), "idle", 8).save(os.path.join(refs, "7_xinzhao_now.png"))
    guide(refs, tmp, a.lol)
    for n, hero in (("9_style_jax", "league_jax"), ("10_style_katarina", "league_katarina"),
                    ("11_style_pantheon", "league_pantheon")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.rmtree(tmp)
    shutil.copyfile(lp(os.path.join(SRC, "xinzhao", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
