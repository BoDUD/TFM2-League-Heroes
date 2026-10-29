"""The Codex pack for league_kayle's actions drawn whole at PPU 2.29 (assets/source/kayle/ACTIONS_PROMPT_PPU.md):
every frame of her flight, ranged and melee attacks, Q Radiant Blast (skill), E Starfire Spellblade (skill2), R Divine
Judgment (ult), hit and death a new drawing of the approved design (hd/design.png: Codex's kayle-A read as drawn,
66 x 112 squares - the user, 2026-10-29: 「通过，用 2.29」) in the pose of her OLD sheet's same frame,
tools/art/pack_taric_actions.py's way.

    python tools/art/pack_kayle_actions.py --out C:/t/ka_actions

The sword goes where the old frame has it: low in her far hand, swung back, thrust out, raised overhead, thrown up
high above her in R's frame 6 (her hands empty in frame 7) and gone from the death's frame 2 on. She never touches
the ground: the run is a flight loop, its wing beats named (RUN_WINGS).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from skill2 and
skill). No old action frame is another one's picture nor her idle pose itself (checked on the old sheet: SAME is
empty), so all 57 are drawn. Nothing is baked into her body tags (her fire, waves and blades are effect strips,
kayle_fx_*). Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the
old 1x frame scaled to her height (PPU squares a pixel, SQ px a square - R's flight to 89 px over her soles at SQ_OF's
smaller squares), faded, as the pose to follow, on the ground line at the standing point, and a bar as tall as she
stands. Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "kayle")
TAGS = ["run", "attack", "attack_melee", "skill", "skill2", "ult", "hit", "dead"]
BAKED = []                              # (nothing baked into her body tags)
NAMES = {"run": "flying (her move loop): she flies forward leaning in, never touching the ground, her legs trailing "
                "bent behind her, her WINGS BEATING, the sword held low behind her in her far hand, her hair "
                "streaming back",
         "attack": "ranged attack (after she ascends): she swings the sword back over her shoulder, swoops forward "
                   "and thrusts it out ahead of her to the right, rising, and settles",
         "attack_melee": "melee attack (before she ascends): she thrusts the sword straight out ahead, raises it high "
                         "over her head, lunges and slashes it out ahead of her at chest height, and settles",
         "skill": "Radiant Blast (Q): she spreads her wings, dives forward almost level, curls round and turns back, "
                  "the sword low, and settles",
         "skill2": "Starfire Spellblade (E): she draws the sword back over her shoulder, then slashes it down ahead "
                   "of her to the right and settles",
         "ult": "Divine Judgment (R): she crouches with her wings spread, rises high into the air raising the sword "
                "straight up over her head, flings it up far above her (frame 6), comes down empty-handed (frame 7) "
                "and lands with the sword back in her hand (frame 8)",
         "hit": "struck: jolted back in the air",
         "dead": "death: struck back, she loses the sword, sinks to her knees and falls forward, lying face down on "
                 "the ground with her wings over her"}
SWORD = ("THE SWORD goes where the pale figure has it, frame by frame (image 3 shows it in colour): held in her FAR "
         "hand (image right) by its gold hilt, the cyan flame blade pointing where the pale figure's does - low down "
         "to the right unless she swings, raises or thrusts it. Only ONE sword, the design's. Both WINGS as the pale "
         "figure: spread, raised or swept back.")
WEAPONS = {t: SWORD for t in NAMES}
WEAPONS["ult"] = ("As the pale figure: the sword in her far hand, raised straight up over her head in frames 3-5; in "
                  "frame 6 it FLIES UP ON ITS OWN far above her (draw it there, point up, separate from her, her hands "
                  "empty); in frame 7 NO sword at all, her hands empty; in frame 8 back in her far hand, low. Only one "
                  "sword. Both WINGS as the pale figure.")
WEAPONS["dead"] = ("As the pale figure: the sword in her far hand in frame 1 only; from frame 2 on there is NO sword "
                   "at all (she has lost it). Both WINGS as the pale figure, lying over her in the last frames.")
# The flight's wings frame by frame, read off the old run (two beats in 16 frames); she flies to the right
RUN_WINGS = {1: "swept back level", 2: "swept back and down", 3: "raised", 4: "raised high", 5: "raised",
             6: "raised high (the top of the beat), her body lifting", 7: "swept back level", 8: "swept back",
             9: "swept back and down", 10: "swept back level", 11: "raised", 12: "raised", 13: "raised high",
             14: "swept back, spread", 15: "swept back, spread", 16: "swept back level"}
RUN_FLIGHT = ("She FLIES the whole loop: no foot ever touches the ground, the legs trailing bent behind her as the "
              "pale figure; the body bobs up and down with the beats. Follow the pale figure's WINGS exactly - never "
              "the same wing pose in every frame.")
# old frames that are another frame pixel for pixel (checked on the old sheet / the native cells, cropped to the
# figure): drawn once, here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {}                                # (none: every old action frame is its own picture)
SQ = 7                                   # px a design square in the templates (her run 54 px over her soles)
SQ_OF = {"ult": 4}                       # R rises 89 px over her soles: smaller squares to stay in the sheet
PPU = 112 / 49                           # design squares an old pixel (hd/design.png: 112 rows, her 1x 49)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 112                              # design rows from her wing tips to the sword's tip
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "her height (wing tips to sword tip)",
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/kayle")
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
        sq = SQ_OF.get(tag, SQ)
        for n, (nums, part) in enumerate(groups(old[tag], set(SAME.get(tag, {})), sq)):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums, sq)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"), sq)
            sheets.append(dict(tag=tag, name=name, frames=nums, cells=len(part), square=sq, action=NAMES[tag],
                               ms=[ms for _, ms, _ in part], weapons=WEAPONS[tag]))
            if tag == "run":
                sheets[-1]["wings"] = " ".join(f"Frame {k}: wings {RUN_WINGS[k]}." for k in nums) + " " + RUN_FLIGHT
    same = {t: {str(k): f"{t2} {k2}" for k, (t2, k2) in m.items()} for t, m in SAME.items()}
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "square_of": SQ_OF, "sheet": [SHEET_W, H], "ground": GROUND, "same": same,
                   "baked_body_frames": BAKED,
                   "sheets": sheets}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, a.prompt)), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
