#!/usr/bin/env python3
"""Diana's actions from the waist down: the tassets and the idle's legs (the run's pieces) under Codex's upper bodies.

    python tools/art/diana_action_legs.py [--src assets/source/diana/codex_strips] [--out assets/source/diana/action_legs]
                                          [--tags attack,skill,...]

After the run was rebuilt with the idle's long skirt and leg pieces (tools/art/diana_run_legs.py) the user: "你既然改了
释放技能的时候腿部也要弄成一样的吧 我怎么看到有不一样的部分了". Codex's action frames wear a short teal skirt over long
dark legs, in Q and W only 1-2 squares wide. Per frame, assets/source/diana/action_legs.json gives where the waist
and the legs are (read off Codex's own frame - its stance fits its upper body - or League's pose where Codex's legs
were sticks); this tool then
  - drops Codex's pixels from the belt row down (cut) except the blade (its light pieces, as tidy_diana finds them),
    the keep boxes (things in front of the new skirt: a hand on the hilt, the forearm across it) and the hair colours
    in the hair boxes, then puts every other pixel of Codex's frame back wherever nothing new is drawn - hands, the
    blade's dark edges, ponytail tips and the cape beside the skirt (a first version cleared the rows full width and
    cut them: a review found floating blades and hands) - except its old legs (leg_zone: below the new skirt, across
    the new legs' columns) and the drop boxes (old knees left beside the skirt);
  - puts the tassets (diana_run_legs.TASSET, the idle's since "按样稿换成短裙甲") with their belt at belt=[x, y] (x =
    the stamp's middle column), lean moving the hem that many columns forward (rows in between in proportion); width
    drops columns (NARROW) for a body seen from the side;
  - draws the legs with diana_run_legs.draw_leg, one outline round both and one seam where they touch: hips inside the skirt (belt + 2.5 rows, the near one
    1.75 columns forward), knee and ankle per leg ("near" is drawn over "far"), the boot along toe (default forward);
    an ankle on row 78 puts the boot's sole outline on the soles row 79; px sets single squares (palette letters);
  - dy first moves Codex's frame down (the hit frames stood on the blade's tip, their feet 3 rows up; what goes below
    the soles row is cut); "skirt": false keeps Codex's skirt (cut below it) and only redraws the legs;
  - frames listed nowhere, or with "keep_codex": true, stay Codex's;
  - then every frame's outline is made one square thick (tidy_diana.clean).
Frames first move down like tidy_diana.ground (not AIRBORNE / LYING), so the json's rows are the in-game rows.
Writes <out>/native/diana_<tag>_1x.png and <out>/manifest.json (eye marks moved with the frame) for tidy_diana.py --legs.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diana_run_legs as rl  # noqa: E402
import tidy_diana as td  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
SOURCE = os.path.join(ROOT, "assets", "source")
CONFIG = os.path.join(SOURCE, "diana", "action_legs.json")
HIP_DOWN, HIP_GAP = 2.5, 3.5
BLADE_LEAST = 10                             # smaller pale pieces below the cut are Codex's shins, not the blade
NARROW = [8, 4, 9]                           # the tassets' columns to go in a narrow skirt (the gaps, the side flap)
PALETTE = rl.PALETTE
HAIRS = {(0xF2, 0xE6, 0xCF), (0xC7, 0xB8, 0xA2), (0x55, 0x47, 0x43), (0xB9, 0xB6, 0x90), (0x81, 0x87, 0x68)}
lp = rl.lp


def skirt(idle, cx, y, lean, width=None):
    """The tassets (diana_run_legs.TASSET): belt top row y, middle column cx, the hem lean columns forward; width
    drops columns in NARROW's order (a body seen from the side)."""
    drop = NARROW[:len(rl.TASSET[0]) - width] if width else ()
    return rl.place_tassets(cx, y, lean, drop=drop)


def boxes(shape, bs):
    m = np.zeros(shape[:2], bool)
    for x0, y0, x1, y1 in bs or []:
        m[y0:y1 + 1, x0:x1 + 1] = True
    return m


def upper(f, cut, keep, drop, least=BLADE_LEAST, hair=None):
    """Codex's frame above the cut row, plus the blade, the keep boxes and the hair in the hair boxes (its colours and
    the outline round them) below it, minus the drop boxes."""
    h, w = f.shape[:2]
    m = np.zeros((h, w), bool)
    m[:cut] = True
    line = np.array([[f[y, x, 3] > 0 and td.key(f[y, x]) in td.LINE for x in range(w)] for y in range(h)])
    for part in td.blade_parts(f, least):
        m |= part | (td.around(part) & line)
    m |= boxes(f.shape, keep)
    hb = boxes(f.shape, hair)
    hm = hb & np.array([[f[y, x, 3] > 0 and td.key(f[y, x]) in HAIRS for x in range(w)] for y in range(h)])
    m |= hm | (hb & td.around(hm) & line)
    m &= ~boxes(f.shape, drop)
    out = np.zeros_like(f)
    out[m] = f[m]
    return out


def leg(spec, hip):
    knee, ankle = np.array(spec["knee"], float), np.array(spec["ankle"], float)
    toe = rl.unit(spec.get("toe", [1, 0]))
    return hip, knee, ankle, toe


def legs_layer(far_leg, near_leg):
    """Far leg, near leg over it, one outline round both and a single seam where they touch or overlap (on the far
    leg's side) - two legs side by side had two black lines between them."""
    far, near = rl.draw_leg(*far_leg, far=True), rl.draw_leg(*near_leg, far=False)
    fm, nm = far[..., 3] > 0, near[..., 3] > 0
    out = np.zeros_like(far)
    out[fm] = far[fm]
    out[nm] = near[nm]
    out[fm & ~nm & rl.ring(nm)] = rl.INK
    out[rl.ring(fm | nm)] = rl.INK
    return out


def leg_zone(legs, top, pad=2):
    """Where Codex's own legs were: below the new skirt, across the new legs' columns and pad more each side."""
    m = np.zeros(legs.shape[:2], bool)
    cols = np.nonzero((legs[top:, :, 3] > 0).any(0))[0]
    if len(cols):
        m[top:, max(0, cols.min() - pad):cols.max() + pad + 1] = True
    return m


def build_frame(f, cfg, idle):
    cx, by = cfg["belt"]
    hips = cfg.get("hips")
    near_hip = np.array(hips[0] if hips else [cx + HIP_GAP / 2, by + HIP_DOWN], float)
    far_hip = np.array(hips[1] if hips else [cx - HIP_GAP / 2, by + HIP_DOWN], float)
    out = np.zeros_like(f)
    legs = legs_layer(leg(cfg["far"], far_hip), leg(cfg["near"], near_hip))
    rl.over(out, legs)
    n = len(rl.TASSET)
    if cfg.get("skirt", True):
        rl.over(out, skirt(idle, cx, by, cfg.get("lean", 0), cfg.get("width")))
    rl.over(out, upper(f, cfg.get("cut", by), cfg.get("keep"), cfg.get("drop"), cfg.get("blade_least", BLADE_LEAST),
                         cfg.get("hair")))
    # everything else of Codex's frame comes back where nothing new is drawn (hands, the blade, the ponytail and the
    # cape beside the skirt), except its old legs under the skirt and the drop boxes
    back = (out[..., 3] == 0) & (f[..., 3] > 0) & ~leg_zone(legs, by + n) & ~boxes(f.shape, cfg.get("drop"))
    back[rl.SOLES + 1:] = False
    out[back] = f[back]
    for x, y, c in cfg.get("px", []):                                  # single squares, palette letters ('.' clear)
        out[y, x] = (0, 0, 0, 0) if c == "." else (*PALETTE[c], 255)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(SOURCE, "diana", "codex_strips"))
    ap.add_argument("--out", default=os.path.join(SOURCE, "diana", "action_legs"))
    ap.add_argument("--tags")
    a = ap.parse_args()
    with open(lp(CONFIG), encoding="utf-8") as f:
        conf = json.load(f)["tags"]
    with open(lp(os.path.join(a.src, "manifest.json")), encoding="utf-8") as f:
        man = json.load(f)
    idle = np.asarray(Image.open(lp(os.path.join(SOURCE, "native", "diana_idle.png"))).convert("RGBA"))[::8, ::8][:96, :96]
    tags = a.tags.split(",") if a.tags else list(conf)
    os.makedirs(lp(os.path.join(a.out, "native")), exist_ok=True)
    out_path = os.path.join(a.out, "manifest.json")
    anims = {}
    if os.path.exists(lp(out_path)):
        with open(lp(out_path), encoding="utf-8") as f:
            anims = json.load(f)["animations"]
    for tag in tags:
        an = man["animations"][tag]
        strip = np.asarray(Image.open(lp(os.path.join(a.src, an["native_file"]))).convert("RGBA")).copy()
        strip[strip[..., 3] < 128] = 0
        strip[strip[..., 3] > 0, 3] = 255
        cols = strip.shape[1] // 96
        frames = [dict(fr) for fr in an["frames"]]
        notes = []
        for k, fr in enumerate(frames):
            y0, x0 = (k // cols) * 96, (k % cols) * 96
            f = strip[y0:y0 + 96, x0:x0 + 96]
            n = 0
            if (tag, k) not in td.AIRBORNE and (tag, k) not in td.LYING:
                f, n = td.ground(f, fr["pivot"][1])
            cfg = conf.get(tag, {}).get(str(k + 1))
            if cfg and cfg.get("dy"):                        # feet held up by a blade tip on the ground: body down
                f = rl.shifted(f, cfg["dy"])
                f[rl.SOLES + 1:] = 0
                n += cfg["dy"]
            if cfg and not cfg.get("keep_codex"):
                f = td.clean(build_frame(f, cfg, idle))
                low = int(np.nonzero(f[..., 3].any(1))[0].max())
                notes.append(f"{k + 1}:legs(low {low})")
            else:
                f = td.clean(f)
                notes.append(f"{k + 1}:codex")
            if fr.get("eye_mark"):
                fr["eye_mark"] = [fr["eye_mark"][0], fr["eye_mark"][1] + n]
            strip[y0:y0 + 96, x0:x0 + 96] = f
        Image.fromarray(strip).save(lp(os.path.join(a.out, "native", f"diana_{tag}_1x.png")))
        anims[tag] = dict(an, frames=frames, native_file=f"native/diana_{tag}_1x.png")
        print(tag.ljust(9), " ".join(notes))
    with open(lp(out_path), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"note": "waist down rebuilt by tools/art/diana_action_legs.py (assets/source/diana/action_legs.json): "
                           "the idle's skirt and legs under Codex's upper bodies; frames already grounded",
                   "animations": anims}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
