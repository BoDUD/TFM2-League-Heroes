"""The Codex pack for league_blitzcrank's actions drawn whole at PPU 1.80 (assets/source/blitzcrank/ACTIONS_PROMPT_PPU.md):
every frame of his actions - his attack, Q Rocket Grab (skill: the throw, q_pull: the pull - every frame of it is the
throw's - and q_hold: the hand back, holding), E Power Fist (skill2), R Static Field (ult), run, hit and death - a new
drawing of the approved design (hd/design.png: Codex's blitzcrank-A read on ~14.4-px squares, 80 x 79 - the user,
2026-11-05: 「卡兹克2.24 布里茨1.8 莉莉娅2.62 烬1.8」) in the pose of his OLD sheet's same frame, tools/art/pack_ryze_actions.py's
way, one PR with the other three.

    python tools/art/pack_blitzcrank_actions.py --out C:/t/blitzcrank_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
legs change over (RUN_LEGS, named from the start).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions). Old
frames that are another frame pixel for pixel are drawn once (SAME). Nothing is baked. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to his height (PPU
squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point, and a
bar as tall as he stands. refs/design_picture.png is Codex's own blitzcrank-A, the picture the design was read from (its
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

SRC = os.path.join(REPO, "assets", "source", "blitzcrank")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["run", "attack", "skill", "q_pull", "q_hold", "skill2", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into the body tags)
NAMES = {
    "run": ("running (his move loop): leaning forward on his short piston legs, the big fists swinging, the LEGS "
        "CHANGING OVER as the pale figure has them"),
    "attack": ("attack: he winds up, the near fist pulled back (frames 1-2), punches forward, the near arm stretched"
        " out to the fist (frames 3-4), and swings through (frame 5)"),
    "skill": ("Rocket Grab, the throw (Q): he cocks the near arm back (frames 1-2) and thrusts it forward, the hand"
        " open at its end (frame 3); the hand flies off - the arm ends in an EMPTY hexagonal socket (frames "
        "4-6) - and comes back onto it (frame 7)"),
    "q_pull": ("Rocket Grab, the pull (Q): every frame is a throw frame again"),
    "q_hold": ("Rocket Grab, holding (Q): the near arm stretched forward, the hand back at its end, closed on the "
        "grabbed foe (frames 1-2)"),
    "skill2": ("Power Fist (E): he crouches, winding up, the near fist low behind him (frames 1-3), swings it up in "
        "an uppercut (frame 4), the fist high over his head (frame 5), and brings it down (frame 6)"),
    "ult": ("Static Field (R): he hunches, charging (frames 1-2), curls in, the arms crossed before his body "
        "(frames 3-5), and flings both arms out wide as the field bursts (frame 6)"),
    "hit": ("struck: jolted back, his head knocked back (frame 1)"),
    "dead": ("death: struck (frame 1), he rears up, a fist raised (frames 2-3), slumps (frame 4), topples over "
        "backwards, a fist up (frames 5-6), and lies on his back (frames 7-8)"),
}
ARMS = ("HIS ARMS AND FISTS go where the pale figure has them, frame by frame (image 3 shows them in colour): the two"
        " massive golden arms with their big square fists, as big as in image 1 - pulled back, punching, swinging up "
        "or flung out as the pale figure holds them. In Rocket Grab, where the pale figure's arm ends in an EMPTY "
        "hexagonal socket (the hand flew off), draw the socket empty, no hand; where the hand is back, draw it. The "
        "fists are NOT legs: his two short piston legs with the golden feet carry him. Only him: no steam, no "
        "electric sparks or lightning, no chain; the eyes' pink stays inside the eyes.")
WEAPONS = {t: ARMS for t in NAMES}
# The run's legs, frame by frame - deferred to the pale figure, the old run taking its own steps (Talon's first run kept one leg in front in every frame: 「走路没有换腿」;
# so did Codex's first run of Senna's: named here from the start); he runs to the right, "back" is the image's left
RUN_LEGS = {
    1: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    2: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    3: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    4: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    5: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    6: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    7: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
    8: "the legs EXACTLY as the pale figure has them in this frame: which leg is in front and which behind, "
       "which foot is flat on the ground line and which is lifted (image 3: the near leg lighter, the far leg"
       " darker)",
}
RUN_SWAP = ("The two legs TAKE TURNS as in the old run: the near leg (the lighter one) and the far leg (the darker one) "
            "pass each other, the leg in front changing over the 8 frames - never the same leg in front in every frame "
            "(Senna's first run did that, and Talon's: 「走路没有换腿」). His big fists swing down near the ground but are NOT "
            "legs: his two short piston legs with the golden feet carry him.")
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once,
# here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"attack": {6: DESIGN}, "skill": {8: DESIGN}, "q_pull": {1: ('skill', 5), 2: ('skill', 6), 3: ('skill', 5)},
        "skill2": {7: DESIGN}, "ult": {7: DESIGN}, "hit": {2: DESIGN}}
SQ = 9                                   # px a design square in the templates (his 79 rows in the sheet)
SQ_OF = {"skill2": 7}   # (E's uppercut lifts his fist 67 old px over his soles)
PPU = 79 / 44                            # design squares an old pixel (hd/design.png: 79 rows, his 1x 44)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 79                               # design rows from the tops of his chimneys to his soles
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "his height standing (the tops of his chimneys)",
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/blitzcrank")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "blitzcrank-A.png"))).convert("RGBA")
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
