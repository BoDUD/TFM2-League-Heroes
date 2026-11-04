"""The Codex pack for league_alistar's actions drawn whole at PPU 1.73 (assets/source/alistar/ACTIONS_PROMPT_PPU.md): every
frame of his actions - his attack, Q Pulverize (skill), W Headbutt (skill2; butt and slam are frames of skill2 and skill
again), R Unbreakable Will (ult), run, hit and death - a new drawing of the approved design (hd/design.png: Codex's
alistar-A read on ~15-px squares, 71 x 76 - the user, 2026-11-04: 「全部粗」) in the pose of his OLD sheet's same frame,
tools/art/pack_ryze_actions.py's way, one PR with the other three.

    python tools/art/pack_alistar_actions.py --out C:/t/alistar_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
legs change over (RUN_LEGS, named from the start).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions),
skill_fx1 / ult_fx1 (copies of skill / ult with E's ready glow: assets/source/native/alistar_bake.json lays it on
again). Old frames that are another frame pixel for pixel are drawn once (SAME). Nothing is baked. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to his height (PPU
squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point, and a
bar as tall as he stands. refs/design_picture.png is Codex's own alistar-A, the picture the design was read from (its
fine detail). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "alistar")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["run", "attack", "skill", "skill2", "butt", "slam", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into the body tags)
NAMES = {
    "run": ("running (his move loop): a heavy hunched charge, the arms swinging, the LEGS CHANGING OVER (9 "
        "frames)"),
    "attack": ("attack: he raises his near fist high (frames 2-3) and brings it down hard in front of him (frames "
        "4-5), then recovers (frame 6)"),
    "skill": ("Pulverize (Q): he crouches (frame 1), lifts both fists clasped high over his head (frames 2-3) and "
        "slams them into the ground (frames 4-5), then rises (frame 6)"),
    "skill2": ("Headbutt (W): head lowered, horns forward, he charges (frames 1-4), flings his head up to butt "
        "(frame 5) and recovers (frame 6)"),
    "butt": ("Headbutt's butt (W): the frames of skill2 5-6 again"),
    "slam": ("Headbutt into Pulverize (W then Q): the frames of skill 3-6 again"),
    "ult": ("Unbreakable Will (R): he gathers himself (frames 1-2), rises (frame 3) and stands up tall facing "
        "out, ROARING, both arms spread wide (frames 4-5), then drops back into his stance (frame 6)"),
    "hit": ("struck: jolted back, the arms flung out (frame 1), recovering (frame 2)"),
    "dead": ("death: struck, he rears up (frames 2-3), topples back (frames 4-5) and lies flat on his back (frames"
        " 6-7)"),
}
ARMS = ("HIS ARMS AND FISTS go where the pale figure has them, frame by frame (image 3 shows them in colour): the two"
        " massive arms with the wide dark grey shackles on the wrists, raised, swung, slammed or spread as the pale "
        "figure holds them; the cream horns and the icy blue crystal mane stay on his head and back. Only him: no "
        "dust, no cracks in the ground, no shockwaves, no glow; the icy blue stays on the mane.")
WEAPONS = {t: ARMS for t in NAMES}
# The run's legs, frame by frame (9 frames, read off the old run) (Talon's first run kept one leg in front in every frame: 「走路没有换腿」;
# so did Codex's first run of Senna's: named here from the start); he runs to the right, "back" is the image's left
RUN_LEGS = {
    1: "STRIDE: the FAR leg (the darker one) just landed in front (image right), its hoof flat; the NEAR leg "
       "(the lighter one) behind (image left), its hoof on the ground pushing off",
    2: "SUPPORT ON THE FAR LEG: the far leg planted under his hips; the NEAR leg lifted behind him, bent, its"
       " hoof off the ground",
    3: "SUPPORT ON THE FAR LEG: the far leg still planted, bending; the near leg swinging forward from "
       "behind, its hoof off the ground",
    4: "PASSING: both legs gathered under him; the NEAR leg passing forward close beside the planted far leg,"
       " its hoof just off the ground",
    5: "PASSING: the near leg coming down under his hips to take his weight; the far leg leaving the ground "
       "behind it",
    6: "SUPPORT ON THE NEAR LEG: now the NEAR leg (the lighter one) planted under his hips; the FAR leg (the "
       "darker one) kicked up behind him, bent, its hoof high off the ground",
    7: "SUPPORT ON THE NEAR LEG: the near leg still planted, bending; the far leg swinging down from behind, "
       "its hoof off the ground",
    8: "PASSING: the FAR leg passing forward close beside the planted near leg, its hoof just off the ground",
    9: "STRIDE: the FAR leg reaching forward (image right) to land, its hoof coming down; the NEAR leg behind"
       " (image left) pushing off",
}
RUN_SWAP = ("The two legs TAKE TURNS: in frames 1-3 the FAR leg (the darker one) carries him, in frames 5-7 the NEAR leg "
            "(the lighter one) - frames 2 and 6 must look different: a different leg planted, the other one kicked back. "
            "Never the same leg in front in every frame (Senna's first run did that, and Talon's: 「走路没有换腿」).")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once,
# here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"butt": {1: ('skill2', 5), 2: ('skill2', 6)}, "slam": {1: ('skill', 3), 2: ('skill', 4), 3: ('skill', 5), 4:
        ('skill', 6)}, "dead": {8: ('dead', 7)}}
SQ = 9                                   # px a design square in the templates (his 76 rows in the sheet)
SQ_OF = {"skill": 6, "slam": 6, "ult": 6, "dead": 7, "skill2": 8, "butt": 8}   # (the slam's raised fists, R's roar standing tall and the death's rearing up reach 1057-1290 px over the ground at 9: smaller to stay in the sheet)
PPU = 76 / 44                            # design squares an old pixel (hd/design.png: 76 rows, his 1x 44)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 76                               # design rows from the top of his mane to his soles
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
    """The old frame scaled to his height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "his height standing (the top of his mane)",
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
    """His idle pose on the old sheet: idle_base 1."""
    px = np.asarray(Image.open(PR.lp(os.path.join(SRC, "hd", "old", "sheet.png"))).convert("RGBA"))
    with open(PR.lp(os.path.join(SRC, "hd", "old", "anim.fanim")), encoding="utf-8-sig") as f:
        d = json.load(f)["anims"]["idle_base"]["frames"][0]["data"]
    x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
    return px[y:y + h, x:x + w]


def check_same(old):
    """Every SAME pair is the same picture on the old sheet - a later edit of SAME must not join two poses."""
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/alistar")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "alistar-A.png"))).convert("RGBA")
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
