"""The Codex pack for league_lissandra's actions drawn whole at PPU 1.81 (assets/source/lissandra/ACTIONS_PROMPT_PPU.md):
every frame of her actions - her attack, Q Ice Shard (skill), W Ring of Frost (skill2), E Glacial Path (skill2_e), R
Frozen Tomb on a foe and on herself (ult, ult_self), her glide, hit and death - a new drawing of the approved design
(hd/design.png: Codex's lissandra-A read on ~15-px squares, 47 x 76 - the user, 2026-11-03: 「凯南1.81 梦魇1.8 剑魔2.27
丽桑卓1.81」) in the pose of her OLD sheet's same frame, tools/art/pack_ryze_actions.py's way, one PR with the other seven.

    python tools/art/pack_lissandra_actions.py --out C:/t/lissandra_actions

The weapon and hands go where the old frame has them (WEAPONS); the old frames' baked effects are not drawn. The run's
legs change over (RUN_LEGS, named from the start).

Not drawn: idle_base (the design, held still), idle and bp (tools/art/hero_reels.json cuts them from the actions),
ult_fx1 / skill2_e_fx1 / skill2_e_fx2 (copies of ult / skill2_e with their casts:
assets/source/native/lissandra_bake.json lays them on again). Old frames that are another frame pixel for pixel are
drawn once (SAME). BAKED: the old skill carries Q's cast picture (lissandra_bake.json q_cast): its native body cells are
drawn (pack_akali_actions.py's way: assets/source/native/lissandra_cells.json, at 1x on their own pivots). Each template
sheet (templates/<tag>_<k>.png, 1536 x 1024) holds ONE or TWO frames: in each cell the old 1x frame scaled to her height
(PPU squares a pixel, SQ px a square), faded, as the pose to follow, standing on the ground line at the standing point,
and a bar as tall as she stands. refs/design_picture.png is Codex's own lissandra-A, the picture the design was read
from (its fine detail). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "lissandra")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["run", "attack", "skill", "skill2", "skill2_e", "ult", "ult_self", "hit", "dead"]
BAKED = ["skill"]    # the old skill carries Q's cast picture (lissandra_bake.json q_cast): the native body cells
NAMES = {
    "run": ("gliding forward (her move loop): leaning ahead, the gown's hem sweeping, the arms swaying; no legs "
        "seen"),
    "attack": ("attack: she raises her near hand and casts forward, the arm stretched out (frames 2-6)"),
    "skill": ("Ice Shard (Q): she draws her hand in and thrusts it forward, casting, frame by frame as the pale "
        "figure"),
    "skill2": ("Ring of Frost (W): she spreads her hands, frame by frame as the pale figure (frames 1-5)"),
    "skill2_e": ("Glacial Path (E): she thrusts a hand forward, casting (frames 1-3, 5-6)"),
    "ult": ("Frozen Tomb (R): she raises a hand high and brings it down at the target (frames 1-5)"),
    "ult_self": ("Frozen Tomb on herself (R): her hand raised, frame by frame as the pale figure (frames 1, 2, 4)"),
    "hit": ("struck: jolted back"),
    "dead": ("death: struck (frames 1-2), she sinks as her gown freezes into ice spikes rising round her (frames "
        "3-7)"),
}
ARMS = ("HER HANDS go where the pale figure has them, frame by frame (image 3 shows them in colour): pale blue hands "
        "with icy cuffs, raised, thrust forward or spread as the pale figure holds them; the wide ice crown stays on "
        "her head. The pale figure's flying ice shards and frost are the old frame's effects: do NOT draw them (in "
        "the death the ice spikes rising round her gown ARE her body: draw them). Only her: no frost mist, no flying "
        "shards, no afterimages.")
WEAPONS = {t: ARMS for t in NAMES}
# The run has no legs to change over: her gown's hem sways as the old frame's
RUN_LEGS = {k: "NO LEGS SEEN: she glides; her long gown's hem with its ice spikes sweeps as the pale figure's, frame by frame" for k in range(1, 9)}
RUN_SWAP = "Her legs are hidden in her gown: only the hem sways as the pale figure's (do not draw legs or feet)."
# old frames that are another frame pixel for pixel (checked on the old sheet, cropped to the figure): drawn once,
# here (tag, frame), 1-based; DESIGN: her idle pose itself (the old idle_base 1)
DESIGN = ("design", 0)
SAME = {"run": {4: ('run', 3), 5: ('run', 1)}, "attack": {1: DESIGN}, "skill2_e": {4: ('skill2_e', 3)}, "ult_self": {3:
        ('ult_self', 1), 5: ('ult_self', 1)}, "hit": {2: DESIGN}, "dead": {8: ('dead', 7)}}
SQ = 9                                   # px a design square in the templates (her 76 rows in the sheet)
SQ_OF = {}                               # (tags drawn at smaller squares to stay in the sheet)
PPU = 76 / 42                            # design squares an old pixel (hd/design.png: 76 rows, her 1x 42)
H = 1024
SHEET_W = 1536
GROUND = H - 100
STAND = 76                               # design rows from the top of her crown to her soles
OLD_SOLES = 11.5                         # old frames: the soles this many pixels under the frame's centre (its pivot)
CELL_SOLES = 12                          # native cells: their pivot is the frame's centre too, the soles 12 px under it
MARGIN = 30
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    """{tag: [(frame, ms, (pivot x, soles y))]}: the old sheet's frames (pivot: the frame's centre, the soles OLD_SOLES
    under it), BAKED tags from their native body cells at 1x (each cell's own pivot, lissandra_cells.json, the soles
    CELL_SOLES under it)."""
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    with open(os.path.join(NATIVE, "lissandra_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for tag in TAGS:
        fr = []
        if tag in BAKED:
            strip = Image.open(PR.lp(os.path.join(NATIVE, f"lissandra_{tag}.png"))).convert("RGBA")
            cw, ch = (v * cells.get("scale", 8) for v in cells["cell"])   # (8 when the cells json leaves it out: kennen_cells.json)
            per_row = strip.width // cw
            for k, c in enumerate(cells["tags"][tag]):
                r, q = divmod(k, per_row)
                a = np.asarray(strip.crop((q * cw, r * ch, (q + 1) * cw, (r + 1) * ch))
                               .resize(tuple(cells["cell"]), Image.BOX)).copy()
                a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
                a[a[..., 3] == 0] = 0
                fr.append((a, c["ms"], (c["pivot"][0], c["pivot"][1] + CELL_SOLES)))
        else:
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
        dr.text((bx + 8, GROUND - STAND * sq - 4), "her height standing (the top of her crown)",
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
    ap.add_argument("--prompt", default="ACTIONS_PROMPT_PPU.md", help="the prompt file in assets/source/lissandra")
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
    pic = Image.open(PR.lp(os.path.join(SRC, "hd", "raw", "lissandra-A.png"))).convert("RGBA")
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
