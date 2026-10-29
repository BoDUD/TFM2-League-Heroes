"""The Codex pack for league_taric's actions drawn whole at PPU 1.55 (assets/source/taric/ACTIONS_PROMPT_PPU.md):
every frame of his run, attack, Bravado strike (attack_p), E Dazzle (skill), Q Starlight's Touch (skill2), R Cosmic
Radiance (ult), hit and death a new drawing of the approved design (hd/design.png: Codex's taric-A read as drawn,
48 x 62 squares - the user, 2026-10-29: 「通过，用 1.55」) in the pose of his OLD sheet's same frame,
tools/art/pack_zed_actions.py's way.

    python tools/art/pack_taric_actions.py --out C:/t/ta_actions

The hammer goes where the old frame has it: hanging head down in his near hand, swung back, overhead, out in front,
flung away and lying on the ground in the death. The run's legs are named frame by frame from the start (RUN_LEGS).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill2 and
ult). No old frame is another one's picture nor his idle pose itself (checked on the old sheet: SAME is empty), so all
49 are drawn. Nothing is baked into his body tags (his starlight, beams and shields are effect strips, taric_fx_*).
Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame
scaled to his height (PPU squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line
at the standing point, and a bar as tall as he stands. Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "taric")
TAGS = ["run", "attack", "attack_p", "skill", "skill2", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into his body tags)
NAMES = {"run": "running (his move loop): a strong upright stride, the hammer trailing low behind him in his near "
                "hand, the bare far arm swinging, the LEGS STEPPING IN TURN, the cape and the hair swaying",
         "attack": "attack: he draws the hammer back, then sweeps it out in front of him to the right at chest "
                   "height, carries it across his body and settles",
         "attack_p": "Bravado strike (the empowered attack): he lifts the hammer behind his shoulder, raises it high "
                     "over his head, lunges low and smashes it down in front of him to the right, then rises",
         "skill": "Dazzle (E): he draws the hammer back, then thrusts it out straight in front of him to the right, "
                  "the bare far hand raised up behind him, and settles",
         "skill2": "Starlight's Touch (Q): he raises the bare far hand high above his head, palm open, then lowers "
                   "it; the hammer stays low in his near hand",
         "ult": "Cosmic Radiance (R): he raises the hammer high over his head in his near hand, the bare far hand "
                "open in front of him, holds it, and settles",
         "hit": "struck: jolted back, the far arm flung out",
         "dead": "death: struck back, he flings the hammer away, sinks to his knees and slumps forward on the ground, "
                 "the hammer lying on the ground in front of him"}
HAMMER = ("THE HAMMER goes where the pale figure has it, frame by frame (image 3 shows it in colour): held in his NEAR "
          "hand (the gauntleted one), hanging head DOWN by his feet unless the pale figure swings, raises or thrusts "
          "it - then its head goes where the pale figure's does. Only ONE hammer, the design's (two curved "
          "silver-white blades with a violet-blue gem between them). His FAR arm stays BARE in every frame.")
WEAPONS = {t: HAMMER for t in NAMES}
WEAPONS["dead"] = ("As the pale figure: in frames 2-4 the hammer flies away from his hand through the air, in frames "
                   "5-8 it lies on the ground in front of him - drawn where the pale figure has it, only one hammer. "
                   "His FAR arm stays BARE.")
# The run's legs frame by frame, read off the old run (the pale figures: the bottom rows of each old frame, the near
# leg's silver greave light, the far leg's dark) - named from the start (Akali's first run kept the legs stretched apart
# in every frame); he runs to the right, "back" is the picture's left
RUN_LEGS = {
    1: "the NEAR foot (the lighter leg) planted on the ground AHEAD of his hips (right); the FAR leg (the darker one) "
       "kicked up BEHIND him (left), its foot off the ground",
    2: "PASSING: the near foot planted right under his hips; the far leg comes through in front of it, its knee "
       "lifted, its foot off the ground",
    3: "the near foot now BEHIND his hips (left); the far leg reaching forward (right), its foot just off the ground",
    4: "the FAR foot planted AHEAD (right); the NEAR leg kicked up behind him (left), its foot off the ground",
    5: "PASSING: the far foot planted under his hips; the near leg comes through in front of it, its knee lifted, its "
       "foot off the ground",
    6: "PASSING: the same, the near knee a little further forward, its foot off the ground",
    7: "the far foot now BEHIND his hips (left); the near leg reaching forward (right), its foot just off the ground",
    8: "the NEAR foot planted AHEAD again (right); the far leg kicked up behind him (left), its foot off the ground - "
       "flowing into frame 1",
}
RUN_SWAP = ("The two legs TAKE TURNS: the near (lighter) foot is on the ground in frames 1-3 and 8, the far (darker) "
            "foot in frames 4-7. Follow the pale figure's LEGS exactly - every frame has one foot off the ground; "
            "never the same leg pose in every frame.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: his idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {}                                # (none: every old frame is its own picture)
SQ = 8                                   # px a design square in the templates (two run frames a sheet)
PPU = 62 / 40                            # design squares an old pixel (hd/design.png: 62 rows, his 1x 40)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 62                               # design rows from the top of his hair to his soles
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


def cell_fit(frame):
    xs = np.nonzero(frame[0][..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * SQ + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw):
    """The old frame scaled to his height in a cell [x0, x0 + cw): its pivot on the standing point (the cell's middle),
    its soles on the ground line, kept inside the cell. -> (RGBA image, left, top)."""
    a, _, (pvx, pvy) = frame
    k = PPU * SQ
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
            raise SystemExit(f"a frame reaches {8 - top - bb[1]} px over the template's top: lower SQ")
    return im, left, top


def template(path, frames, nums):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
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
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "his height standing (the top of his hair)",
                fill=(120, 120, 120), font=PR.font(16))
        dr.text((x0 + 14, 12), f"frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, fr in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, skip):
    """[([numbers], [frames])] of the frames to draw (none in `skip`): two to a sheet while both fit a half."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in skip]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1]) and cell_fit(todo[k + 1][1]):
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/taric")
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
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in (a.only.split(",") if a.only else TAGS):
        for n, (nums, part) in enumerate(groups(old[tag], set(SAME.get(tag, {})))):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == "run":
                sheets[-1]["legs"] = " ".join(f"Frame {k}: {RUN_LEGS[k]}." for k in nums) + " " + RUN_SWAP
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "same": same, "baked_body_frames": BAKED,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
