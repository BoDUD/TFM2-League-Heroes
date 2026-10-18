"""The Codex pack for league_riven's swords at PPU 1.5 (assets/source/riven/SWORDS_PROMPT_PPU.md): her broken blade and
her reforged R blade, each drawn at ANGLES (8 directions 22.5 degrees apart from League's idle hold, 35.5 degrees; the
other 8 are their mirror images), so the rig turns her sword by choosing the drawing nearest League's angle instead of
quarter-turning one huge blade.

    python tools/art/pack_riven_swords.py --out C:/t/rv_swords [--lol D:/WeGameApps/lol]

The user, 2026-10-18, on the first PPU rig (whose sword was Codex's design blade, R-sized): 「锐雯的剑有这么大？开大才有这么
打吧 还有打的时候一套姿势吗？还不如老版模型的锐雯啊 还有武器挥打遮挡脸部？」, then 「按你说的重做：给 Codex 新包，设计图换正常大小
的断剑，再画平时和开大两把剑各 8 个角度，加上不挡脸」. Her figure stays the approved design (hd/design.png); only the swords
are new. Sizes from her old 1x sprite x PPU: the broken sword NORMAL_LEN squares pommel to tip, NORMAL_W wide; the
reforged one R_LEN long.

Writes <out>/SWORDS_PROMPT.md, <out>/templates/{normal,reforged}_{1,2}.png (1536 x 1024, 2 x 2 cells of 768 x 512, each
cell one angle: a blue circle where her fist holds the grip, a red line from the pommel's end to the tip, a tick where
the guard is; squares of SQ px), <out>/refs/ (her old sprite's sword and R sword at 10x, League's blade close up -
Riot's, kept local, never committed - and the approved design picture for the colours), then <out>.zip.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
SRC = os.path.join(REPO, "assets", "source", "riven")
GREEN, GREY = (0, 255, 0), (225, 225, 225)
ANGLES = [13.0, 35.5, 58.0, 80.5, 103.0, 125.5, 148.0, 170.5]   # degrees, counter-clockwise from pointing right
SQ = 8                                       # px a square in the templates
NORMAL_LEN, NORMAL_W, NORMAL_GRIP = 31, 10, 7   # squares: pommel to tip, the blade's width, pommel + grip
R_LEN = 52
CANVAS, CELL = (1536, 1024), (768, 512)
BLUE, RED = (0, 60, 255), (255, 0, 0)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def template(path, angles, length):
    """Four angles on one sheet: per cell the pommel's end, the tip and the fist (NORMAL_GRIP / 2 squares from the
    pommel's end) on one straight line, the whole sword centred in its cell."""
    can = Image.new("RGB", CANVAS, GREEN)
    dr = ImageDraw.Draw(can)
    for i, a in enumerate(angles):
        cx, cy = (i % 2) * CELL[0] + CELL[0] / 2, (i // 2) * CELL[1] + CELL[1] / 2
        u = (math.cos(math.radians(a)), -math.sin(math.radians(a)))
        L = length * SQ
        p0 = (cx - u[0] * L / 2, cy - u[1] * L / 2)
        p1 = (cx + u[0] * L / 2, cy + u[1] * L / 2)
        dr.line([p0, p1], fill=RED, width=3)
        g = NORMAL_GRIP * SQ
        fist = (p0[0] + u[0] * g / 2, p0[1] + u[1] * g / 2)
        dr.ellipse([fist[0] - 14, fist[1] - 14, fist[0] + 14, fist[1] + 14], outline=BLUE, width=3)
        guard = (p0[0] + u[0] * g, p0[1] + u[1] * g)
        n = (-u[1], u[0])
        dr.line([(guard[0] - n[0] * 30, guard[1] - n[1] * 30), (guard[0] + n[0] * 30, guard[1] + n[1] * 30)],
                fill=RED, width=3)
        dr.text(((i % 2) * CELL[0] + 10, (i // 2) * CELL[1] + 8), f"{i + 1}: {a:g} deg", fill=(0, 0, 0))
        dr.rectangle([(i % 2) * CELL[0], (i // 2) * CELL[1], (i % 2 + 1) * CELL[0] - 1, (i // 2 + 1) * CELL[1] - 1],
                     outline=(0, 160, 0))
    can.save(path)


def old_frame(tag, i, z, out):
    """A frame of her sprite on main before the PPU redo (git show origin/main), at z x on grey."""
    sheet = subprocess.run(["git", "-C", REPO, "show", "origin/main:league/champions/league_riven#sheet.png"],
                           capture_output=True, check=True).stdout
    anim = subprocess.run(["git", "-C", REPO, "show", "origin/main:league/champions/league_riven#anim.fanim"],
                          capture_output=True, check=True).stdout
    import io
    sh = Image.open(io.BytesIO(sheet)).convert("RGBA")
    f = json.loads(anim.decode("utf-8-sig"))["anims"][tag]["frames"][i]["data"]
    im = sh.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * z, pad.height * z), Image.NEAREST).save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    os.makedirs(tpl, exist_ok=True)
    os.makedirs(refs, exist_ok=True)
    for name, length in (("normal", NORMAL_LEN), ("reforged", R_LEN)):
        template(os.path.join(tpl, f"{name}_1.png"), ANGLES[:4], length)
        template(os.path.join(tpl, f"{name}_2.png"), ANGLES[4:], length)
    old_frame("attack", 3, 10, os.path.join(refs, "1_old_sword.png"))
    old_frame("attack_r", 3, 10, os.path.join(refs, "2_old_reforged.png"))
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ", "Riven", "--hq",
           "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1400", "--fit", "0.6", "--ground", "0.92",
           "--width", "1.2", "--yaw", "45", "--pitch", "25", "--name", "3_league_blade", "--out", refs,
           "--only-joints", "WEAPON", "--frame", "riven_idle1@0"]
    subprocess.run(cmd, check=True, capture_output=True)
    p = os.path.join(refs, "3_league_blade.png")
    im = Image.open(p).convert("RGB")
    px = im.load()
    xs, ys = [], []
    for y in range(0, im.height, 2):          # the blade = neither the grey ground nor the black frame round it
        for x in range(0, im.width, 2):
            c = px[x, y]
            if max(abs(c[k] - GREY[k]) for k in range(3)) > 12 and max(c) > 8:
                xs.append(x)
                ys.append(y)
    if xs:
        im.crop((max(0, min(xs) - 30), max(0, min(ys) - 30), max(xs) + 30, max(ys) + 30)).save(p)
    d = Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (d.width + 4, d.height + 4), GREY + (255,))
    bg.alpha_composite(d, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, "4_design_colours.png"))
    r = Image.open(lp(os.path.join(SRC, "hd", "codex_r_blade.png"))).convert("RGBA")
    r = r.crop(r.getbbox())
    bg = Image.new("RGBA", (r.width + 40, r.height + 40), GREY + (255,))
    bg.alpha_composite(r, (20, 20))
    bg.convert("RGB").save(os.path.join(refs, "5_reforged_style.png"))
    shutil.copyfile(lp(os.path.join(SRC, "SWORDS_PROMPT_PPU.md")), os.path.join(a.out, "SWORDS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
