"""The Codex pack for league_leblanc's PPU redo (assets/source/leblanc/PICTURE_PROMPT_PPU.md): one design picture on the
11-px grid at PPU 1.5, her proportions now (the big-headed sprite: 43 game rows crown to soles, the staff standing
beside her), the way league_fiora, league_darius and league_riven were redone on 2026-10-18 (tools/art/pack_fiora_ppu.py);
the actions are posed after League's clips afterwards (rig_fiora_hd.py's way), the effects stay.

    python tools/art/pack_leblanc_ppu.py --out C:/t/lb_pack [--lol D:/WeGameApps/lol]

The user, 2026-10-19: 「利用PPU我们重做一下妖姬 昨天那个账号示范了怎么重做的 先让codex生成」 (on 2026-10-16 her redo picture
came back life-sized, 「剑姬赵兴妖姬贾克斯要做成Q版的 现在太逼真了」, so this pack asks for the sprite's own chibi
proportions).
Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..4 (League renders of her idle with the head enlarged as poses.json's chibi
settings, through tools/lol/pose_ref.py: Riot's, kept local, never committed; 4 = her staff arm close up), refs/5 (the
loading-screen art), refs/6 (Codex's approved picture A of 2026-10-02: the costume and colours to keep), refs/7 (her
game sprite now at 8x: the proportions, the staff and the facing), refs/8 (the layout guide: her sprite now as a flat
silhouette at the new size) and <out>/style/9..11 (this pack's Fiora, Riven and Kai'Sa at their PPU hd_idle, 8x), then
<out>.zip. Render into a short folder.
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
IDLE = "idle1@0"                                # standing with the staff (poses.json design)
# poses.json's chibi head and legs; the staff (Weapon) and the cape shown (--hide-submeshes and the old cape joints
# took both away)
CHIBI = ["--head", "2.3", "--legs", "0.8", "--submesh-texture", "Weapon=Weapon_TX"]
# name -> (yaw, size, width, crop "box" or fractions of the figure's box); not mirrored (poses.json camera)
RENDERS = {
    "1_leblanc_idle": (45, 1000, 1.2, "box"),
    "2_leblanc_side": (90, 1000, 1.2, "box"),
    "3_leblanc_head": (40, 2400, 1.2, (0.0, 0.0, 0.6, 0.4)),
    "4_leblanc_staff_arm": (45, 2000, 1.2, (0.35, 0.15, 1.0, 0.65)),
}
PPU, SQ = 1.5, 11                               # each game pixel 1.5 squares of 11 px
# her crown's tip to her soles 43 game rows = 65 squares = FULL_H px, soles on row SOLE
CANVAS, SOLE, FULL_H = (1024, 1024), 960, 715


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
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Leblanc", "--hq", *CHIBI, "--fit-all", "--pitch", "20",
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
    """Her sprite now as a flat silhouette at PPU 1.5 (each game pixel 16.5 px), soles on row SOLE, centred: the size
    and the place only."""
    spr = sheet_frame(os.path.join(CHAMPS, "league_leblanc"), "idle")
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
    d.text((24, 24), f"crown tip to soles {FULL_H} px (65 squares of 11); layout only", fill=(60, 60, 60, 255))
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Leblanc.wad.client"))
    pose_ref.read_tex(wad.read_path("ASSETS/Characters/Leblanc/Skins/Base/LeblancLoadScreen_0.tex")) \
        .convert("RGB").save(os.path.join(refs, "5_leblanc_splash.png"))
    pic = Image.open(lp(os.path.join(SRC, "leblanc", "codex_picture", "leblanc-model-A.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 24, pic.height + 24), GREY + (255,))
    bg.alpha_composite(pic, (12, 12))
    bg.convert("RGB").save(os.path.join(refs, "6_leblanc_picture.png"))
    sheet_frame(os.path.join(CHAMPS, "league_leblanc"), "idle", 8).save(os.path.join(refs, "7_leblanc_now.png"))
    guide(refs)
    for n, hero in (("9_style_fiora", "league_fiora"), ("10_style_riven", "league_riven"),
                    ("11_style_kaisa", "league_kaisa")):
        sheet_frame(os.path.join(CHAMPS, hero), "hd_idle", 8).save(os.path.join(style, n + ".png"))
    shutil.copyfile(lp(os.path.join(SRC, "leblanc", "PICTURE_PROMPT_PPU.md")), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
