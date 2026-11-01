"""The Codex pack for league_senna's actions drawn whole at PPU 1.87 (assets/source/senna/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Q Piercing Darkness (skill), W Last Embrace (skill2), R Dawning Shadow (ult), hit and death a
new drawing of the approved design (hd/design.png: Codex's senna-A read on its own ~14.4-px squares, 82 x 73 - the
user, 2026-11-01: 「用 A 1.87」) in the pose of her OLD sheet's same frame, tools/art/pack_missfortune_actions.py's way.

    python tools/art/pack_senna_actions.py --out C:/t/sn_actions

The Relic Cannon goes where the old frame has it: on her shoulder, levelled forward to fire, swung up to the sky,
pointed down or resting on the ground as the pale figure holds it - one cannon, whole and straight, never bent or cut.
The run's legs change over (RUN_LEGS: Talon's lesson, named from the start).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill2 and
skill). Three old frames are another frame pixel for pixel (SAME: ult 8 = ult 7, dead 4 = dead 3, dead 6 = dead 5),
so 38 are drawn. Nothing is baked. Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO
frames: in each cell the old 1x frame scaled to her height (PPU squares a pixel, SQ px a square), faded, as the pose to
follow, standing on the ground line at the standing point, and a bar as tall as she stands. refs/design_picture.png is
Codex's own senna-A, the picture the design was read from (its fine eyes, lips and gold). Then <out>.zip.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "senna")
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into the body tags)
NAMES = {"run": "running (her move loop): a light, quick run, the Relic Cannon carried slanting across her body, the "
                "hood's sash and the locs flying, the LEGS CHANGING OVER",
         "attack": "attack: she levels the cannon forward at her hip and FIRES (frames 1-4), the recoil kicking its "
                   "head up to the sky (frame 5), then levels it again (frame 6)",
         "skill": "Piercing Darkness (Q): she crouches, gathering (frames 1-2), swings the cannon down (frame 3), then "
                  "levels it forward and FIRES (frames 4-6)",
         "skill2": "Last Embrace (W): the cannon swung low, its head down to the ground in front (frames 1-2), then "
                   "levelled forward and FIRED (frames 3-4), then lowered as she straightens up (frames 5-6)",
         "ult": "Dawning Shadow (R): she crouches with the cannon low (frame 1), heaves it up to the sky (frame 2), "
                "levels it forward and FIRES (frames 3-4), the recoil dipping its head down (frame 5), then holds it "
                "level, firing (frames 6-7)",
         "hit": "struck: jolted back, the cannon swung up",
         "dead": "death: struck, she staggers (frame 1), sinks to her knees, the cannon sliding down in front of her "
                 "(frame 2), and kneels with the cannon lying on the ground before her (frames 3 and 5)"}
CANNON = ("THE RELIC CANNON goes where the pale figure has it, frame by frame (image 3 shows it in colour): ONE cannon, "
          "WHOLE and STRAIGHT, as large as in image 1 - the gold claw grip, the gold ring with its dark round eye, the "
          "pale ice-blue crystal blade, the wine-red wing panel with its gold ribs - in her hands, on her shoulder, "
          "levelled forward, swung up or pointed down as the pale figure holds it; the blade end is the muzzle, the "
          "gold claw is the grip; never bent, cut, shortened or a second cannon. Only the cannon: no beam, no muzzle "
          "flash, no black mist, no souls.")
WEAPONS = {t: CANNON for t in NAMES}
WEAPONS["dead"] = CANNON + " Where the pale figure has let it fall, draw it lying on the ground before her."
# The run's legs, frame by frame (Talon's first run kept one leg in front in every frame: 「走路没有换腿」;
# so did Codex's first run of hers, its heads and bodies drawn at other sizes than her other actions' too: redone with
# --only run --prompt RUN_REDO_PROMPT_PPU.md); she runs to the right, "back" is the image's left
RUN_LEGS = {
    1: "SUPPORT ON THE NEAR LEG: the NEAR leg (the lighter one) planted straight down under her hips, its foot flat on "
       "the ground; the FAR leg (the darker one) kicked up and back behind her, bent, its foot high off the ground",
    2: "SUPPORT ON THE NEAR LEG: the near leg still planted under her hips, bending; the far leg swinging down from "
       "behind, its foot off the ground behind the planted one",
    3: "PASSING: both legs gathered under her, knees bent; the FAR leg passing forward close beside the planted near "
       "leg, its foot just off the ground",
    4: "STRIDE: the FAR leg reaching forward (image right) to land, its heel coming down; the NEAR leg behind (image "
       "left) pushing off, its toes on the ground",
    5: "SUPPORT ON THE FAR LEG: now the FAR leg (the darker one) planted straight down under her hips, its foot flat on "
       "the ground; the NEAR leg (the lighter one) kicked up and back behind her, bent, its foot high off the ground",
    6: "SUPPORT ON THE FAR LEG: the far leg still planted under her hips, bending; the near leg swinging down from "
       "behind, its foot off the ground behind the planted one",
    7: "PASSING: both legs gathered under her, knees bent; the NEAR leg passing forward close beside the planted far "
       "leg, its foot just off the ground",
    8: "STRIDE: the NEAR leg reaching forward (image right) to land, its heel coming down; the FAR leg behind (image "
       "left) pushing off, its toes on the ground",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-4 the NEAR leg (the lighter one) carries her and the FAR leg comes "
            "forward, in frames 5-8 the FAR leg (the darker one) carries her and the NEAR leg comes forward - frames 1 "
            "and 5 must look different: a different leg planted, the other one kicked back. Never the same leg in "
            "front in every frame (her first run did that, and Talon's: 「走路没有换腿」).")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once,
# here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"ult": {8: ("ult", 7)}, "dead": {4: ("dead", 3), 6: ("dead", 5)}}
SQ = 8                                   # px a design square in the templates (her 73 rows in the sheet)
SQ_OF = {}                               # (tags drawn at smaller squares to stay in the sheet)
PPU = 73 / 39                            # design squares an old pixel (hd/design.png: 73 rows, her 1x 39)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 73                               # design rows from the top of the cannon's claw to her soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in TAGS:
        fr = []
        for f_ in anims[tag]["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000), (w / 2, h / 2 + OLD_SOLES)))
        out[tag] = fr
    return out


def cell_fit(frame, sq):
    xs = np.nonzero(frame[0][..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * sq + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw, sq):
    """The old frame scaled to her height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
    its soles on the ground line, kept inside the cell. -> (RGBA image, left, top)."""
    a, _, (pvx, pvy) = frame
    k = PPU * sq
    h, w = a.shape[:2]
    im = Image.fromarray(a).resize((round(w * k), round(h * k)), Image.NEAREST)
    left = round(x0 + cw / 2 - pvx * k)
    top = round(GROUND - pvy * k)
    bb = im.getbbox()
    if bb:
        lo, hi = left + bb[0], left + bb[2]
        if lo < x0 + MARGIN:
            left += x0 + MARGIN - lo
        elif hi > x0 + cw - 14:
            left -= hi - (x0 + cw - 14)
        if top + bb[1] < 8:
            raise SystemExit(f"a frame reaches {8 - top - bb[1]} px over the template's top: lower SQ_OF")
    return im, left, top


def template(path, frames, nums, sq):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw, sq)
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    for i in range(len(frames)):
        x0 = i * cw
        cx = x0 + cw / 2
        dr.rectangle([x0, 0, x0 + cw - 1, H - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + cw - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * sq)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * sq - 4), "her height standing (the top of the cannon's claw)",
                fill=(120, 120, 120), font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out, sq):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw, sq)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, skip, sq):
    """[([numbers], [frames])] of the frames to draw (none in `skip`): two to a sheet while both fit a half."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in skip]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1], sq) and cell_fit(todo[k + 1][1], sq):
            pair = todo[k:k + 2]
            k += 2
        else:
            pair = todo[k:k + 1]
            k += 1
        out.append(([n for n, _ in pair], [f for _, f in pair]))
    return out


def figure(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def idle_sheet():
    """Her idle pose on the old sheet: idle_base 1."""
    px = np.asarray(Image.open(PR.lp(os.path.join(SRC, "hd", "old", "sheet.png"))).convert("RGBA"))
    with open(PR.lp(os.path.join(SRC, "hd", "old", "anim.fanim")), encoding="utf-8-sig") as f:
        d = json.load(f)["anims"]["idle_base"]["frames"][0]["data"]
    x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
    return px[y:y + h, x:x + w]


def check_same(old):
    """Every SAME pair is the same picture on the old sheet (a later edit of SAME must not join two poses)."""
    for tag, m in SAME.items():
        for k, (t2, k2) in m.items():
            a = figure(old[tag][k - 1][0])
            bs = [figure(idle_sheet())] if (t2, k2) == DESIGN else [figure(old[t2][k2 - 1][0])]
            if not any(a.shape == b.shape and (a == b).all() for b in bs):
                sys.exit(f"SAME {tag} {k} = {t2} {k2}: not the same old frame")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default=os.path.join(SRC, "hd", "old", "sheet.png"))
    ap.add_argument("--old-fanim", default=os.path.join(SRC, "hd", "old", "anim.fanim"))
    ap.add_argument("--only", help="tags to pack, comma-separated (the redo of one action: --only run)")
    ap.add_argument("--sheets", help="of those, only these sheets, comma-separated (the redo: run_1,...,skill_1)")
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/senna")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(PR.lp(a.old_sheet), PR.lp(a.old_fanim))
    check_same(old)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "senna-A.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    pic = pic.crop(pic.getbbox())
    bg = Image.new("RGBA", (pic.width + 40, pic.height + 40), GREY + (255,))
    bg.alpha_composite(pic, (20, 20))
    bg.convert("RGB").save(os.path.join(refs, "design_picture.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in (a.only.split(",") if a.only else TAGS):
        sq = SQ_OF.get(tag, SQ)
        for n, (nums, part) in enumerate(groups(old[tag], set(SAME.get(tag, {})), sq)):
            name = f"{tag}_{n + 1}"
            if a.sheets and name not in a.sheets.split(","):
                continue
            template(os.path.join(tpl, name + ".png"), part, nums, sq)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"), sq)
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), square=sq, action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == "run":
                sheets[-1]["legs"] = " ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "square_of": SQ_OF, "sheet": [SHEET_W, H], "ground": GROUND, "same": same, "baked_body_frames": BAKED,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
