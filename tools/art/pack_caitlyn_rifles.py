"""The Codex pack for league_caitlyn's rifle drawn straight at four angles (assets/source/caitlyn/RIFLES_PROMPT_PPU.md):
level, climbing 1 square in 2 (26.6 degrees), falling 1 in 2, and climbing 1 in 1 (45 degrees) - the slopes whose
pixel steps are even, so the barrel reads as one straight line. Turned a quarter (losslessly) and mirrored left-right
they give her 16 ways (0, 26.6, 45, 63.4, 90 ... degrees); every redrawn action frame's rifle is replaced by the one
nearest the way Codex's points (tools/art/actions_caitlyn_hd.py).

    python tools/art/pack_caitlyn_rifles.py --out C:/t/ct_rifles [--lol D:/WeGameApps/lol]

The user, 2026-10-23: 「还有枪别做歪」. Sizes from her approved design (hd/design.png): the rifle RIFLE squares long
(stock's end to muzzle). Writes <out>/RIFLES_PROMPT.md, <out>/templates/rifles.png (1536 x 1024, 2 x 2 cells of
768 x 512, each cell one angle: a red line stock to muzzle on squares of SQ px, ticks every 2 squares so the steps can
be counted), <out>/refs/ (the design's rifle at 8x, the whole design at 8x, League's rifle close up - Riot's, local
only), then <out>.zip.
"""
import argparse
import math
import os
import shutil
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "caitlyn")
GREEN, GREY = (0, 255, 0), (225, 225, 225)
SLOPES = [("1_level", 1, 0), ("2_up_1in2", 2, 1), ("3_down_1in2", 2, -1), ("4_up_1in1", 1, 1)]   # (across, up)
SQ = 8
RIFLE = 59
CANVAS, CELL = (1536, 1024), (768, 512)
DESIGN_RIFLE = (2, 8, 54, 49)          # the design's rifle box (x0, y0, x1, y1 squares)


def template(path):
    can = Image.new("RGB", CANVAS, GREEN)
    dr = ImageDraw.Draw(can)
    for i, (name, ax, up) in enumerate(SLOPES):
        cx, cy = (i % 2) * CELL[0] + CELL[0] / 2, (i // 2) * CELL[1] + CELL[1] / 2
        n = math.hypot(ax, up)
        u = (ax / n, -up / n)
        L = RIFLE * SQ
        p0 = (cx - u[0] * L / 2, cy - u[1] * L / 2)
        p1 = (cx + u[0] * L / 2, cy + u[1] * L / 2)
        dr.line([p0, p1], fill=(255, 0, 0), width=3)
        for k in range(0, RIFLE + 1, 2):
            t = k * SQ * n / max(abs(ax), 1) if False else k * SQ
            q = (p0[0] + u[0] * t, p0[1] + u[1] * t)
            dr.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(160, 0, 0))
        slope = "level" if up == 0 else f"{'up' if up > 0 else 'down'} 1 square every {ax} across"
        dr.text(((i % 2) * CELL[0] + 10, (i // 2) * CELL[1] + 8), f"{i + 1}: {slope}", fill=(0, 0, 0), font=PR.font(22))
        dr.text((p0[0] - 40, p0[1] + 8), "stock", fill=(0, 0, 0), font=PR.font(18))
        dr.text((p1[0] - 20, p1[1] - 30), "muzzle", fill=(0, 0, 0), font=PR.font(18))
        dr.rectangle([(i % 2) * CELL[0], (i // 2) * CELL[1], (i % 2 + 1) * CELL[0] - 1, (i // 2 + 1) * CELL[1] - 1],
                     outline=(0, 160, 0))
    can.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    template(os.path.join(tpl, "rifles.png"))
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    for name, im in (("1_design", des), ("2_design_rifle", des.crop(DESIGN_RIFLE))):
        bg = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
        bg.alpha_composite(im, (2, 2))
        bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, name + ".png"))
    import pack_caitlyn_ppu as PP                  # League's idle, close on the rifle (the step-0 pack's crop)
    PP.render(a.lol, "3_league_rifle", PP.RENDERS["4_caitlyn_rifle"], refs)
    shutil.copyfile(PR.lp(os.path.join(SRC, "RIFLES_PROMPT_PPU.md")), os.path.join(a.out, "RIFLES_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
