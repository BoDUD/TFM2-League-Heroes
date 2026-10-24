"""The Codex pack for league_annie's actions drawn whole at PPU 2.2 (assets/source/annie/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Disintegrate (skill), Incinerate + Molten Shield (skill2), Summon: Tibbers (ult), hit and death
a new drawing of the approved design (hd/design.png, take A, 44 x 75 squares: Tibbers hanging from her NEAR hand, the
far hand free) in the pose of her OLD sheet's same frame (the timing the kit casts on), with oppi's Annie as the
drawing-style reference - Ahri's way (tools/art/pack_ahri_actions.py). The user, 2026-10-24: 「按这个方案做，写动作包给我」
(the plan: the far, free hand casts every spell; Tibbers stays in the near hand and swings with her, thrown only by R).

    python tools/art/pack_annie_actions.py --out C:/t/an_actions [--old-sheet PNG --old-fanim FANIM] [--oppi DIR]

Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds TWO frames in cells of 768 x 1024 on squares of SQ px
(one design square): the old 1x frame scaled to her height (PPU 2.2 squares a pixel), faded, as the pose to follow,
standing on the ground line at the standing point, and a bar as tall as she stands. The old sheet hugs Tibbers in
front, so the prompt and each sheet's note say where Tibbers goes instead. refs/: the design at 8x and 1x, its palette,
each sheet's old frames in colour, oppi's Annie of that action (style only; local, never committed). The old sheet comes
from main (git show <rev>:league/champions/league_annie#sheet.png / #anim.fanim). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "annie")
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
NAMES = {"run": "running (her move loop), Tibbers swinging in her near hand",
         "attack": "basic attack, a small fireball flicked from her far (free) hand at the foe",
         "skill": "Disintegrate: the far hand swung down from over her head, a big fireball thrown forward, half a step in",
         "skill2": "Incinerate: the far palm pushed forward, leaning in, holding while a cone of fire pours out",
         "ult": "Summon: Tibbers - the near hand throws Tibbers forward and up, then both hands empty, the far hand points",
         "hit": "struck, flinching back, Tibbers jerked up in her near hand",
         "dead": "death: knocked back, Tibbers flies out of her hand, she falls on her back, Tibbers lies beside her"}
# where Tibbers is in each sheet (the old sheet hugs him in front: never copy that)
TIBBERS = {"run": "TIBBERS hangs from her NEAR hand (image left, behind her) by one arm and swings back and forth with "
                  "that arm as she runs.",
           "attack": "TIBBERS stays hanging from her NEAR hand (image left) the whole time; only the FAR hand moves.",
           "skill": "TIBBERS stays hanging from her NEAR hand (image left) the whole time; only the FAR hand throws.",
           "skill2": "TIBBERS stays hanging from her NEAR hand (image left) the whole time; the FAR palm pushes forward.",
           "ult_1": "Frames 1-2: she swings TIBBERS from her NEAR hand back and up, about to throw him forward.",
           "ult_2": "Frame 3: TIBBERS LEAVES HER NEAR HAND, flying forward and up (the pale figure shows where); "
                    "frame 4: Tibbers is gone, BOTH HANDS EMPTY.",
           "ult": "TIBBERS IS GONE (thrown): BOTH HANDS EMPTY; do not draw him.",
           "hit": "TIBBERS hangs from her NEAR hand (image left), jerked up by the blow.",
           "dead_1": "Frames 1-2: TIBBERS flies out of her NEAR hand, tumbling up and back (where the pale figure shows him).",
           "dead": "TIBBERS (the same bear, the same size as in image 1) lies on the ground next to her, still."}
RELEASE = {"attack": 3, "skill": 3, "skill2": 2, "ult": 2}       # the frame the kit casts on (0-based)
SQ = 7                                   # px a design square in the templates
PPU = 2.2                                # design squares an old pixel
CELL = (768, 1024)
GROUND = 1024 - 150
PER_SHEET = 2
STAND = 75                               # design rows from her cat-ear tips to her soles
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
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (cat-ear tips)", fill=(120, 120, 120),
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
    ap.add_argument("--old-sheet", default="C:/t/an_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/an_old/anim.fanim")
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
            sheets.append((tag, name, list(range(k0, k0 + len(part))), [ms for _, ms in part],
                           TIBBERS.get(name, TIBBERS[tag])))
        r = subprocess.run([sys.executable, ase, "render", os.path.join(a.oppi, "champions", "cf_annie.aseprite"),
                            "--out", os.path.join(refs, f"oppi_{tag}.png"), "--scale", "4", "--tag", tag],
                           capture_output=True)
        if r.returncode:
            print("oppi: no tag", tag)
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], action=NAMES[t], ms=ms, tibbers=tb)
                              for t, n, idx, ms, tb in sheets]}, f, indent=1)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets; written", zp)


if __name__ == "__main__":
    main()
