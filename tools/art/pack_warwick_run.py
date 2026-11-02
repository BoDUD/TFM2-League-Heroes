"""The Codex pack for league_warwick's run drawn whole (assets/source/warwick/RUN_PROMPT_PPU.md): the user, 2026-11-01:
「还有狼人的走路姿势现在有点奇怪 让codex可以重做一下」. His run was posed by tools/art/rig_warwick.py on the design's own
legs (league_braum's walk: one leg lifted a few rows per frame, the body bobbing) - it reads as a shuffle in place. Now
Codex draws each of the 8 frames whole on the design (hd/idle.png, 94 x 69 at PPU 1.5 - spike top to soles 69 rows),
after League's own Warwick_Run (a loping, hunched bound, the legs taking turns), Senna's / Talon's run redo way.

    python tools/art/pack_warwick_run.py --out C:/t/ww_run [--lol D:/WeGameApps/lol]

Each template sheet (templates/run_<k>.png, 1536 x 1024) holds TWO frames: in each cell the run frame now (the orig
strip, assets/source/ppu/orig/warwick_run.png) at SQ px a design square, faded - only where he stands and how big he is;
its legs are the ones to redraw - on the ground line at the standing point, and a bar as tall as he stands.
refs/lol_run.png is League's Warwick_Run sampled at 8 times (Riot's, kept local, never committed); refs/old_run_<k>.png
the frames now in colour; refs/design.png the design at 6x, refs/design_picture.png Codex's own take A-1 it was read
from. Then <out>.zip.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "warwick")
ORIG = os.path.join(REPO, "assets", "source", "ppu", "orig", "warwick_run")
DESIGN = os.path.join(SRC, "hd", "idle.png")
PICTURE = os.path.join(SRC, "codex_model", "warwick-model-A-1.png")
SQ = 8                                   # px a design square in the templates
PPU = 1.5                                # the orig strips' squares a game pixel
FEET = 11.5 * PPU                        # orig frames: the soles this many squares under the frame's centre
STAND = 69                               # design rows from the spike on his gauntlet to his soles
H, SHEET_W = 1024, 1536
GROUND = H - 100
GREY = (225, 225, 225)
# the legs frame by frame (League's Warwick_Run: a loping bound, hunched, the arms swinging against the legs); he runs to
# the right, "back" is the image's left; the near leg is the lighter one, the far leg a step darker, partly behind it
RUN_LEGS = {
    1: "SUPPORT ON THE NEAR LEG: the NEAR leg planted under his hips, its clawed foot flat on the ground; the FAR leg "
       "kicked up and back behind him, bent, its foot high off the ground",
    2: "SUPPORT ON THE NEAR LEG: the near leg still planted, bending as he sinks; the far leg swinging down from behind",
    3: "PASSING: the far leg swinging forward past the planted near leg, its foot just off the ground; the body at its "
       "lowest",
    4: "STRIDE: the FAR leg reaching forward (image right) to land; the NEAR leg pushing off behind (image left), its "
       "toes on the ground; the body rising",
    5: "SUPPORT ON THE FAR LEG: now the FAR leg planted under his hips; the NEAR leg kicked up and back behind him, bent, "
       "its foot high off the ground",
    6: "SUPPORT ON THE FAR LEG: the far leg still planted, bending as he sinks; the near leg swinging down from behind",
    7: "PASSING: the near leg swinging forward past the planted far leg, its foot just off the ground; the body at its "
       "lowest",
    8: "STRIDE: the NEAR leg reaching forward to land; the FAR leg pushing off behind, its toes on the ground; the body "
       "rising",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg carries him and the FAR leg comes forward, in frames 5-8 "
            "the FAR leg carries him and the NEAR leg comes forward - frames 1 and 5 must look different. The pale "
            "figure's legs are the OLD ones (they hardly move): follow these words and image 3's League frames for the "
            "legs, the pale figure only for where he stands and how big he is.")
ARMS = ("THE ARMS swing against the legs, a hunched beast's run as image 3: when the near leg is forward the far arm "
        "reaches forward, and the other way; the near arm keeps its bronze gauntlet with the green vials and the "
        "tall spike, the far arm its open claws, both as large as in image 1. The tail streams out behind him, "
        "swaying. Only him: no dust, no speed lines, no afterimages, no blood.")


def strips():
    """The orig run frames: [(RGBA array, ms)]."""
    with open(PR.lp(ORIG + ".json"), encoding="utf-8") as f:
        sizes = json.load(f)["sizes"]
    a = np.asarray(Image.open(PR.lp(ORIG + ".png")).convert("RGBA"))
    out, x = [], 0
    for w, h in sizes:
        out.append(a[:h, x:x + w].copy())
        x += w
    return out


def placed(fr, x0, cw):
    """The frame at SQ px a square in the cell [x0, x0 + cw): its centre over the standing point, its soles (FEET under
    the centre) on the ground line."""
    h, w = fr.shape[:2]
    im = Image.fromarray(fr).resize((w * SQ, h * SQ), Image.NEAREST)
    return im, round(x0 + cw / 2 - w * SQ / 2), round(GROUND - (h / 2 + FEET) * SQ)


def template(path, frames, nums):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        a = np.asarray(im).astype(float)
        a[..., :3] = a[..., :3] * 0.35 + 255 * 0.65
        can.alpha_composite(Image.fromarray(a.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    for i in range(len(frames)):
        x0 = i * cw
        cx = x0 + cw / 2
        dr.rectangle([x0, 0, x0 + cw - 1, H - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + cw - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "his height standing (the spike on his gauntlet)", fill=(120, 120, 120),
                font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"frame now {nums[i]} (its legs are the ones to redraw)", fill=(0, 0, 0),
                font=PR.font(22))
    can.convert("RGB").save(out)


def lol_run(lol, out):
    work = out + "_work"
    os.makedirs(work, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Warwick",
                    "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--anim", "Warwick_Run",
                    "--frames", "8", "--size", "420", "--fit", "0.55", "--ground", "0.85", "--width", "1.0", "--yaw", "60",
                    "--pitch", "20", "--out", work], check=True, capture_output=True)
    im = Image.open(os.path.join(work, "Warwick_Run.png")).convert("RGB")
    dr = ImageDraw.Draw(im)
    cw = im.width / 8
    for k in range(8):
        dr.text((k * cw + 8, 8), f"League {k + 1}", fill=(0, 0, 0), font=PR.font(22))
    im.save(out)
    shutil.rmtree(work)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    frs = strips()
    sheets = []
    for n in range(4):
        nums = [2 * n + 1, 2 * n + 2]
        part = [frs[k - 1] for k in nums]
        name = f"run_{n + 1}"
        template(os.path.join(tpl, name + ".png"), part, nums)
        old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
        sheets.append(dict(tag="run", name=name, frames=nums, cells=2, square=SQ, weapons=ARMS,
                           legs=" ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP))
    des = Image.open(PR.lp(DESIGN)).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(DESIGN), os.path.join(refs, "design_1x.png"))
    pic = Image.open(PR.lp(PICTURE)).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 40, pic.height + 40), GREY + (255,))
    bg.alpha_composite(pic, (20, 20))
    bg.convert("RGB").save(os.path.join(refs, "design_picture.png"))
    d = np.asarray(des)
    PR.palette(np.unique(d[d[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    lol_run(a.lol, os.path.join(refs, "lol_run.png"))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "sheets": sheets}, f, indent=1,
                  ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, "RUN_PROMPT_PPU.md")), os.path.join(a.out, "RUN_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets, 8 frames; written", zp)


if __name__ == "__main__":
    main()
