"""The Codex pack for league_ahri's actions drawn whole at PPU 2.2 (assets/source/ahri/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Orb of Deception (skill), Charm (skill2), Spirit Rush (ult), hit and death a new drawing of
the approved design (hd/design.png, 78 x 88 squares) in the pose of her OLD sheet's same frame - the motion the user
approved before - with oppi's Ahri as the drawing-style reference. My own rig of these actions was rejected (the
user, 2026-10-24: 「尾巴和身体分离 不及格」, 「放大招也这动作？」, 「你这变形也太严重了」, then 「你让codex帮忙把 整理整理 给我动作包吧」).

    python tools/art/pack_ahri_actions.py --out C:/t/ar_actions [--old-sheet PNG --old-fanim FANIM] [--oppi DIR]

Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds TWO frames in cells of 768 x 1024 on squares of SQ px
(one design square): the old 1x frame scaled to her height (PPU 2.2 squares a pixel), faded, as the pose to follow,
standing on the ground line at the standing point, and a bar as tall as she stands. refs/: the design at 8x and 1x,
its palette, each sheet's old frames in colour, oppi's Ahri of that action (style only; local, never committed). The
old sheet comes from main (git show <rev>:league/champions/league_ahri#sheet.png / #anim.fanim). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "ahri")
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
NAMES = {"run": "running (her move loop)",
         "attack": "basic attack, a spirit orb flicked from her hand at the foe",
         "skill": "Orb of Deception: a crouch, a spring up with the hand raised, the orb thrown forward in the air, the landing",
         "skill2": "Charm: the hand to her lips, a kiss blown forward at the foe",
         "ult": "Spirit Rush: a leap into a LEVEL FLIGHT forward, head up in front, hair and tails streaming behind, then the landing",
         "hit": "struck, knocked back a little",
         "dead": "death: knocked back, she drops sitting, props up, then lies down"}
RELEASE = {"attack": 3, "skill": 3, "skill2": 2, "ult": 1}       # the frame the kit casts on (0-based)
SQ = 6                                   # px a design square in the templates
PPU = 2.2                                # design squares an old pixel
CELL = (768, 1024)
GROUND = 1024 - 150
PER_SHEET = 2
STAND = 88                               # design rows from her ear tips to her soles
OLD_SOLES = 11                           # old frames: the soles this many pixels under the frame's centre (its pivot)
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in TAGS:
        fr = []
        for f_ in anims[tag]["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000)))
        out[tag] = fr
    return out


def placed(frame, x0):
    """The old frame scaled to her height in a cell starting at x0: its pivot (the frame's centre) on the standing
    point, kept inside the cell. -> (RGBA image, left, top)."""
    k = PPU * SQ
    h, w = frame.shape[:2]
    im = Image.fromarray(frame).resize((round(w * k), round(h * k)), Image.NEAREST)
    cx = x0 + CELL[0] / 2
    left = round(cx - (w / 2) * k)
    top = round(GROUND - OLD_SOLES * k - (h / 2) * k)
    bb = im.getbbox()
    if bb:
        lo, hi = left + bb[0], left + bb[2]
        if lo < x0 + 40:
            left += x0 + 40 - lo
        elif hi > x0 + CELL[0] - 14:
            left -= hi - (x0 + CELL[0] - 14)
    return im, left, top


def template(path, frames, k0, release):
    """TWO frames: per cell the old frame faded as the pose, ground, standing point, her height."""
    can = Image.new("RGBA", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255, 255))
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * CELL[0])
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    f = PR.font(26)
    for i, (fr, ms) in enumerate(frames):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        dr.rectangle([x0, 0, x0 + CELL[0] - 1, CELL[1] - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + CELL[0] - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (ear tips)", fill=(120, 120, 120),
                font=PR.font(16))
        note = "  (the cast leaves now)" if k0 + i == release else ""
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}, {ms} ms{note}", fill=(0, 0, 0), font=f)
    can.convert("RGB").save(path)


def old_ref(frames, k0, out):
    """The sheet's old frames in colour at the same scale, side by side."""
    can = Image.new("RGBA", (CELL[0] * len(frames), CELL[1]), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * CELL[0])
        can.alpha_composite(im, (left, top))
        dr.text((i * CELL[0] + 14, 12), f"old frame {k0 + i + 1}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default="C:/t/ar_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/ar_old/anim.fanim")
    ap.add_argument("--oppi", default=r"D:\steam\steamapps\workshop\content\3009300\3774304166")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(a.old_sheet, a.old_fanim)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    ase = os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts", "tfm2_ase.py")
    sheets = []
    for tag in TAGS:
        frs = old[tag]
        for k0 in range(0, len(frs), PER_SHEET):
            part = frs[k0:k0 + PER_SHEET]
            name = f"{tag}_{k0 // PER_SHEET + 1}"
            template(os.path.join(tpl, name + ".png"), part, k0, RELEASE.get(tag, -1))
            old_ref(part, k0, os.path.join(refs, f"old_{name}.png"))
            sheets.append((tag, name, list(range(k0, k0 + len(part))), [ms for _, ms in part]))
        r = subprocess.run([sys.executable, ase, "render", os.path.join(a.oppi, "champions", "cf_ahri.aseprite"),
                            "--out", os.path.join(refs, f"oppi_{tag}.png"), "--scale", "4", "--tag", tag],
                           capture_output=True)
        if r.returncode:
            print("oppi: no tag", tag)
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], action=NAMES[t], ms=ms)
                              for t, n, idx, ms in sheets]}, f, indent=1)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets; written", zp)


if __name__ == "__main__":
    main()
