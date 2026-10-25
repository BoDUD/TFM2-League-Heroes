"""The Codex pack for league_gwen's actions drawn whole at PPU 2.84 (assets/source/gwen/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Snip Snip! (skill), Skip 'n Slash + Hallowed Mist (skill2), Needlework (ult), hit and death a
new drawing of the approved design (hd/design.png: Codex's v2 picture as drawn, 93 x 116 squares - the user, 2026-10-25:
「用 2.84，按原图密度，继续做动作包」) in the pose of her OLD sheet's same frame (the timing the kit casts on) -
pack_annie_actions.py's way. Her old scissors (heart loops, the old effects baked into the frames) are not the new
ones: the prompt says so, and draws no effect.

    python tools/art/pack_gwen_actions.py --out C:/t/gw_actions [--old-sheet PNG --old-fanim FANIM]

A frame holding the same pose as an earlier one (SAME) is not drawn again. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: two cells of 768 x 1024 when both
frames' old pictures fit one (CELL_FIT), else one cell 1536 wide (her attack, Q and death reach far: the scissors
forward, lying on the ground). In each cell the old 1x frame scaled to her height (PPU squares a pixel, SQ px a square),
faded, as the pose to follow, standing on the ground line at the standing point, and a bar as tall as she stands.
refs/: the design at 6x and 1x, its palette, each sheet's old frames in colour. The old sheet comes from main (git show
<rev>:league/champions/league_gwen#sheet.png / #anim.fanim). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "gwen")
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
NAMES = {"run": "running (her move loop): a light skipping run, the scissors over her shoulder",
         "attack": "basic attack: the scissors swung down off her shoulder and thrust forward, a snip, back onto the shoulder",
         "skill": "Snip Snip!: the scissors held forward level, snipping open and shut again and again, one last big snip, "
                  "back onto the shoulder",
         "skill2": "Skip 'n Slash then Hallowed Mist: a quick dash forward, then the scissors raised up high and lowered",
         "ult": "Needlework: her free hand flicks needles forward, the scissors stay over her shoulder",
         "hit": "struck, flinching back",
         "dead": "death: she falls back and lies down, the scissors drop to the ground beside her"}
# what the scissors do in each sheet (the old frames draw her OLD scissors: never copy their shape)
SCISSORS = {"run": "The scissors stay CLOSED over her shoulder as in image 1, bobbing with her skip.",
            "attack": "The scissors stay CLOSED; they swing down and thrust forward, pointing to the right, where the pale "
                      "figure has them.",
            "skill": "The scissors point forward to the right, level, where the pale figure has them: OPEN where the pale "
                     "figure's two blades part in a V (the two blades open from the pivot like real scissors), CLOSED where "
                     "they are together.",
            "skill2": "The scissors stay CLOSED: over her shoulder while she dashes, raised up high where the pale figure "
                      "raises them.",
            "ult": "The scissors stay CLOSED over her shoulder as in image 1; only her free hand moves.",
            "hit": "The scissors stay CLOSED over her shoulder as in image 1.",
            "dead_1": "The scissors stay CLOSED in her hand, then slip from it as she falls.",
            "dead": "The scissors lie CLOSED on the ground beside her, still (where the pale figure has them)."}
# old frames that hold the same pose as an earlier one (their pixels differ only by the old baked effects; measured
# square by square): drawn once, the later frame takes the earlier's drawing (1-based)
SAME = {"run": {3: 2, 7: 6, 8: 4},
        "attack": {5: 4, 7: 6},
        "skill": {4: 3, 5: 2, 6: 2, 7: 3, 8: 3, 10: 9, 11: 9},
        "skill2": {5: 4, 8: 6, 9: 4},
        "ult": {3: 2},
        "dead": {8: 7}}
RELEASE = {"attack": 3, "skill": 11, "skill2": 0, "ult": 3}       # the frame the kit's hit / cast lands on (0-based)
SQ = 5.5                                 # px a design square in the templates
PPU = 2.84                               # design squares an old pixel
H = 1024
SHEET_W = 1536
GROUND = H - 120
STAND = 116                              # design rows from the ahoge's tip to her soles
OLD_SOLES = 11                           # old frames: the soles this many pixels under the frame's centre (its pivot)
MARGIN = 40
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


def span(frame):
    """Scaled width the old frame's drawing needs."""
    xs = np.nonzero(frame[..., 3].any(0))[0]
    return (xs.max() + 1 - xs.min()) * PPU * SQ


def cell_fit(frame):
    return span(frame) + 2 * MARGIN <= SHEET_W / 2


def placed(frame, x0, cw):
    """The old frame scaled to her height in a cell [x0, x0 + cw): its pivot (the frame's centre) on the standing point
    (the cell's middle), kept inside the cell. -> (RGBA image, left, top)."""
    k = PPU * SQ
    h, w = frame.shape[:2]
    im = Image.fromarray(frame).resize((round(w * k), round(h * k)), Image.NEAREST)
    left = round(x0 + cw / 2 - (w / 2) * k)
    top = round(GROUND - OLD_SOLES * k - (h / 2) * k)
    bb = im.getbbox()
    if bb:
        lo, hi = left + bb[0], left + bb[2]
        if lo < x0 + MARGIN:
            left += x0 + MARGIN - lo
        elif hi > x0 + cw - 14:
            left -= hi - (x0 + cw - 14)
    return im, left, top


def template(path, frames, nums, release, also):
    """One or two frames (their 1-based numbers nums): per cell the old frame faded as the pose, ground, standing point,
    her height."""
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), (255, 255, 255, 255))
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        x0 = i * cw
        cx = x0 + cw / 2
        dr.rectangle([x0, 0, x0 + cw - 1, H - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + cw - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (ahoge tip)", fill=(120, 120, 120),
                font=PR.font(16))
        note = "  (the hit / cast lands now)" if nums[i] - 1 == release else ""
        dr.text((x0 + 14, 12), f"frame {nums[i]}{note}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(path)


def old_ref(frames, nums, out):
    """The sheet's old frames in colour at the same scale and place."""
    cw = SHEET_W // len(frames)
    can = Image.new("RGBA", (SHEET_W, H), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * cw, cw)
        can.alpha_composite(im, (left, top))
        dr.text((i * cw + 14, 12), f"old frame {nums[i]}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def groups(frs, same):
    """[([numbers], [frames])] of the frames to draw (none in `same`): two to a sheet while both fit a half, else one."""
    todo = [(k + 1, f) for k, f in enumerate(frs) if k + 1 not in same]
    out, k = [], 0
    while k < len(todo):
        if k + 1 < len(todo) and cell_fit(todo[k][1][0]) and cell_fit(todo[k + 1][1][0]):
            pair = todo[k:k + 2]
            k += 2
        else:
            pair = todo[k:k + 1]
            k += 1
        out.append(([n for n, _ in pair], [f for _, f in pair]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default="C:/t/gw_old/sheet.png")
    ap.add_argument("--old-fanim", default="C:/t/gw_old/anim.fanim")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(a.old_sheet, a.old_fanim)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in TAGS:
        same = SAME.get(tag, {})
        for n, (nums, part) in enumerate(groups(old[tag], same)):
            name = f"{tag}_{n + 1}"
            template(os.path.join(tpl, name + ".png"), part, nums, RELEASE.get(tag, -1), same)
            old_ref(part, nums, os.path.join(refs, f"old_{name}.png"))
            sheets.append(dict(tag=tag, name=name, frames=nums,
                               cells=len(part), action=NAMES[tag], ms=[ms for _, ms in part],
                               scissors=SCISSORS.get(name, SCISSORS[tag])))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "sheet": [SHEET_W, H], "ground": GROUND, "same": SAME, "sheets": sheets}, f, indent=1,
                  ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets,", sum(len(s["frames"]) for s in sheets), "frames; written", zp)


if __name__ == "__main__":
    main()
