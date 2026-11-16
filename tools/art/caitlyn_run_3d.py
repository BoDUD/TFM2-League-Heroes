#!/usr/bin/env python3
"""league_caitlyn's run: League's own Run clip moving OUR model of her (the user, 2026-11-15, after the drawn and cut-out
runs: 「你之前那拳头客户端进去处理的人物最自然 但是模型质量不高 所以我在想 拿我们已经做好的图片模型进去处理不是更好么」 -
League's motion was the most natural, its model not ours: put our own model through it; then 「可以，继续调」).

    python tools/art/caitlyn_run_3d.py            # run / hd_run / lo_run into the sheet (+ the PPU strips)
    python tools/art/caitlyn_run_3d.py --check    # exit 1 when the sheet's run tags are not what it makes
    python tools/art/caitlyn_run_3d.py --dry      # make them, write nothing

The frames (assets/source/caitlyn/hd/caitlyn_run_3d.png + .json) come from a pipeline outside the repo: Blender with
League's skeleton and Run clip, which stay local (Riot's files are never committed). On that skeleton her body is
built from rigid pieces of OUR design - torso, a skirt of eight panels (the front ones hinged at the waist, lifting
with the forward thigh so a raised knee stays under the hem), stocking thighs, knee-high brown boots with her gold
bands, sleeves and shoulder pads, feet: each piece on one bone, so it only moves and turns, never changes shape -
coloured flat from her palette by a three-step light, the far (left) leg its own layer one shade darker (dark gold on
its boot), one outline two squares wide; on it our drawn pieces: the head (hd_idle_base[0]'s, in one column, bobbing
three squares), the back hair cut in four rigid pieces hanging from the head (each one follows the head's bob a little
later, the tips the latest; they swing a square with the stride) and the rifle unit (frame 0's rifle with its gripping
hand, cuff and glove, held with the head), the arms reaching for its grip and glove. 14 frames, 0.90 s; a planted
foot moves back exactly as fast as the ground at her move speed. The json keeps League's motion only as numbers
(joints, stance, the skirt's hinges, the drawn pieces' places). This tool writes the frames into her sheet:
- hd_run: the frames as they are (each frame's centre its pivot: the soles' outline 19.5 squares under it - the
  standing frame's ground - and the head in the column hd_idle_base has it);
- run: the 1x frames at 1 / 1.5 (ONE: her idle, attack and old run 1x frames are her hd_ ones at 1 / 1.5, not
  1 / PPU), tools/art/ppu_one.py's one_frame;
- lo_run: tools/art/ppu_hd.py's add_lo;
and the strips tools/art/ppu_hd.py / ppu_restyle.py read (assets/source/ppu/caitlyn_run.png and orig/) the same dense
frames. Her frames feed no derived art (illaoi_souls reads hd_idle_base / hd_idle, hero_reels other tags).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import run_fix as F  # noqa: E402
import thin_outline as T  # noqa: E402

HERO = "league_caitlyn"
SOURCE = os.path.join(ROOT, "assets", "source", "caitlyn", "hd", "caitlyn_run_3d")
ONE = 1.5                 # her hd_ squares a 1x pixel in her 1x tags (idle, attack, the old run: measured)


def lp(path):
    return F.lp(path)


def source():
    """The source strip -> ([dense frames], [ms])."""
    with open(lp(SOURCE + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    px = np.asarray(Image.open(lp(SOURCE + ".png")).convert("RGBA"))
    out, x = [], 0
    for w, h in meta["sizes"]:
        out.append(px[:h, x:x + w].copy())
        x += w + 1
    return out, meta["ms"]


def make():
    """-> {"hd_run", "run", "lo_run": [(frame, ms)]}. Each density on its own ground line, as tools/art/run_fix.py puts
    frames (the 1x and lo_ frames are not the dense ones' squares scaled to the pixel): the dense frames' planted feet
    are on hd_idle_base's; the 1x and lo_ frames all moved by one whole number of rows that puts their planted feet
    on idle_base's / lo_idle_base's (the bob and the flight frames keep their lift)."""
    import ppu_hd
    import ppu_one
    hid, pack, _ppu, _size = T.resolve(HERO, T.all_heroes())
    an, px = F.read_sheet(hid, pack)
    dense, ms = source()
    g_hd = F.ground_of(an, px, "hd_run")
    planted = [k for k, b in enumerate(dense) if abs(F.measure(b)["bottom"] - g_hd) < 0.25]
    if not planted:
        sys.exit(f"{HERO}: no frame of the source has its feet on hd_idle_base's ground ({g_hd})")
    one = []
    for b in dense:
        w, h = int(np.ceil(b.shape[1] / ONE)), int(np.ceil(b.shape[0] / ONE))
        h += 1 - h % 2                        # odd: every frame's feet the same half row off its centre
        f, off = ppu_one.one_frame(b, w, h, 1.0 / ONE, [w + 2 * k for k in range(6)], [h + 2 * k for k in range(6)])
        if off:
            sys.exit(f"{HERO}: a 1x frame loses {off} squares off its rect")
        one.append(f)

    def grounded(frames, tag):
        g = F.ground_of(an, px, tag)
        d = int(round(g - float(np.median([F.measure(frames[k])["bottom"] for k in planted]))))
        return [F.shifted(f, d) for f in frames]
    one = grounded(one, "run")
    mini = {"run": list(zip(one, ms)), "hd_run": list(zip(dense, ms))}
    ppu_hd.add_lo(hid.split("_", 1)[1], mini)
    lo = grounded([f for f, _ in mini["lo_run"]], "lo_run")
    return {"hd_run": list(zip(dense, ms)), "run": list(zip(one, ms)), "lo_run": list(zip(lo, ms))}


def strips(dense):
    """assets/source/ppu/caitlyn_run.png (+ .json) and its orig/ twin: these frames (tools/art/ppu_hd.py's strip)."""
    for folder in (os.path.join(ROOT, "assets", "source", "ppu"), os.path.join(ROOT, "assets", "source", "ppu", "orig")):
        png, js = (os.path.join(folder, "caitlyn_run." + e) for e in ("png", "json"))
        H = max(a.shape[0] for a in dense)
        out = np.zeros((H, sum(a.shape[1] + 1 for a in dense) - 1, 4), np.uint8)
        x = 0
        for a in dense:
            out[:a.shape[0], x:x + a.shape[1]] = a
            x += a.shape[1] + 1
        Image.fromarray(out, "RGBA").save(lp(png), optimize=True)
        meta = {}
        if os.path.exists(lp(js)):
            with open(lp(js), encoding="utf-8") as f:
                meta = json.load(f)
        meta["sizes"] = [[a.shape[1], a.shape[0]] for a in dense]
        with open(lp(js), "w", encoding="utf-8", newline="\n") as f:
            json.dump(meta, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    new = make()
    hid, pack, _, _ = T.resolve(HERO, T.all_heroes())
    an, px = F.read_sheet(hid, pack)
    if a.check:
        bad = []
        for t, fr in new.items():
            cur = F.frames_of(an, px, t)
            if len(cur) != len(fr) or any(c[1] != m or not np.array_equal(c[0], f) for c, (f, m) in zip(cur, fr)):
                bad.append(t)
        if bad:
            sys.exit(f"{HERO}: {', '.join(bad)} not as tools/art/caitlyn_run_3d.py makes them")
        print(f"ok: {HERO} run tags as made")
        return
    if a.dry:
        print({t: len(v) for t, v in new.items()})
        return
    F.write(hid, pack, an, px, new)
    strips([f for f, _ in new["hd_run"]])
    print(f"{HERO}: run / hd_run / lo_run {len(new['hd_run'])} frames written")


if __name__ == "__main__":
    main()
