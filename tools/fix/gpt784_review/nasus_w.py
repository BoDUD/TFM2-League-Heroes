"""league_nasus's W (Wither, skill_w / b_skill_w) the way League's Nasus casts it (the user, 2026-11-19: 「狗头的平A动作不像
英雄联盟的 重改 包括释放其他技能时都要像英雄联盟的动作才行」): Nasus_Base_Spell2_Full raises his free hand high over his
head and holds it there, the staff low in the other hand. GPT's W pushed the free hand out in front with the staff
raised beside the head - no room there for a raised arm (it would cover his snout or the staff's blade).

His stance (idle_base[0] / b_idle_base[0]) already holds the staff low in his front hand alone; the back arm hangs
free beside him, apart from the body. Two pictures are made from it, nothing redrawn square by square:

- up: the hanging arm (ARM: its rows, its columns per row) turned up - mirrored top to bottom about FLIP, so its
  shoulder end sits behind the pauldron and the fist stands over his head, left of the ears; it goes behind the body
  (only clear squares take it). No square is rotated or scaled, so it keeps its shape;
- mid: the same arm swung back (turned 90 degrees about its shoulder, PIVOT), half way up.
Where the fist rested on the staff the staff's rear end stays: its near-black core squares (box KEEP) take the
shaft's dark brown (CORE), so the outline pass of tools/fix/gpt784_review/nasus_clean.py keeps the thin shaft; then
that pass (the arm's old place gets the body's outline). The 1x and lo_ frames of the two pictures are sheetkit's
(tools/fix/xinzhao_galio_1119/sheetkit.py), the same frame sizes as the stance's.

The W plays: the stance, the arm back, the arm up (held), the arm back, the stance - 300 ms like GPT's four frames
(data_champion plays it as an effect; its timing is the effect's own). The strips nasus_[b_]skill_w (assets/source/
ppu[/orig]) are written from the tags. Run after nasus_clean.py and nasus_actions.py.

    python tools/fix/gpt784_review/nasus_w.py [--check]
"""
import importlib.util
import json
import os
import sys

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

_spec = importlib.util.spec_from_file_location("nasus_clean", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                           "nasus_clean.py"))
nc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nc)

CORE = (47, 36, 35)
# per form: the stance tag, ARM (first row, last row, [(up to this row, first column, last column)]), FLIP (row = FLIP -
# row), PIVOT (row, column) of the swing back, KEEP (rows, columns) of the staff's rear end
FORMS = {
    "": ("idle_base", (24, 37, [(33, 26, 35), (37, 30, 36)]), 40, (24, 30), ((38, 42), (22, 38))),
    "b_": ("b_idle_base", (32, 50, [(45, 29, 40), (50, 33, 42)]), 52, (32, 35), ((51, 56), (24, 46))),
}
# (picture, ms): s stance, m arm back, u arm up
PLAY = [("s", 50), ("m", 50), ("u", 140), ("m", 30), ("s", 30)]


def arm(c, spec):
    r0, r1, parts = spec
    m = np.zeros(c.shape[:2], bool)
    for r in range(r0, r1 + 1):
        c0, c1 = next((a, b) for upto, a, b in parts if r <= upto)
        m[r, c0:c1 + 1] = True
    return m & (c[..., 3] > 0)


def pose(c, form, up):
    _, spec, flip, pivot, (rows, cols) = FORMS[form]
    m = arm(c, spec)
    out = c.copy()
    out[m] = 0
    ys, xs = np.nonzero(m)
    h, w = c.shape[:2]
    if up:
        ny, nx = flip - ys, xs
    else:
        py, px = pivot
        ny, nx = py - (xs - px), px - (ys - py)
    ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
    moved = np.zeros_like(out)
    moved[ny[ok], nx[ok]] = c[ys[ok], xs[ok]]
    behind = (moved[..., 3] > 0) & (out[..., 3] == 0)
    out[behind] = moved[behind]
    box = np.zeros(c.shape[:2], bool)
    box[rows[0]:rows[1] + 1, cols[0]:cols[1] + 1] = True
    core = box & (out[..., 3] > 0) & (nc.lab_l(out[..., :3]) < nc.INK_L) & ~(out[..., :3] == nc.OUTLINE).all(-1)
    out[core, :3] = CORE
    return nc.clean(out)


def rect(k, tag, i):
    return list(k.rect(tag, i))


def main():
    check = "--check" in sys.argv
    k = Kit(ROOT, "league", "nasus")
    ears = {tuple(r) for e in json.load(open(nc.TABLE, encoding="utf-8"))["frames"] for r in e["rects"]}
    bad = []
    for form, (stance, *_rest) in FORMS.items():
        tag = form + "skill_w"
        s = {pre: rect(k, pre + stance, 0) for pre in ("hd_", "", "lo_")}
        hd = k.cell("hd_" + stance, 0)
        one_shape = k.cell(stance, 0).shape
        pics = {"m": pose(hd, form, False), "u": pose(hd, form, True)}
        # where the two pictures live: the rects the tag already gives them (same size), else new ones
        cur = k.anims["hd_" + tag]["frames"]
        others = {tuple(int(round(f["data"][q])) for q in "xywh") for t, a in k.anims.items()
                  if t.startswith("hd_") and t != "hd_" + tag for f in a["frames"]}
        have = {}
        for (key, _), f in zip(PLAY, cur):
            r = [int(round(f["data"][q])) for q in "xywh"]
            # a rect this tool made before: only this tag shows it, and GPT's sheet had no picture with ears there
            if key in pics and key not in have and r != s["hd_"] and (r[3], r[2]) == pics[key].shape[:2] and                     tuple(r) not in others and tuple(r) not in ears:
                have[key] = {pre: [int(round(k.anims[pre + tag]["frames"][cur.index(f)]["data"][q])) for q in "xywh"]
                             for pre in ("hd_", "", "lo_")}
        same = len(cur) == len(PLAY) and all(abs(f["duration"] - ms / 1000) < 1e-6 for f, (_, ms) in zip(cur, PLAY))
        for key, pic in pics.items():
            if key in have:
                x, y, w, h = have[key]["hd_"]
                same &= np.array_equal(k.sheet[y:y + h, x:x + w], pic)
            else:
                same = False
        same &= all([int(round(f["data"][q])) for q in "xywh"] == s["hd_"] for f, (key, _) in zip(cur, PLAY) if key == "s")
        if same:
            continue
        bad.append(tag)
        if check:
            continue
        frames = {pre: [] for pre in ("hd_", "", "lo_")}
        for key, ms in PLAY:
            for pre in frames:
                frames[pre].append({"duration": round(ms / 1000, 6), "data": {q: float(v) for q, v in
                                                                              zip("xywh", s[pre])}})
        for pre in frames:
            k.anims[pre + tag] = {"frames": frames[pre]}
        for i, (key, _) in enumerate(PLAY):
            if key == "s":
                continue
            pic = pics[key]
            one, lo = k.one_of(one_shape, pic), k.lo_of(one_shape, pic)
            if key in have:
                for pre, p in (("hd_", pic), ("", one), ("lo_", lo)):
                    x, y, w, h = have[key][pre]
                    if (h, w) != p.shape[:2]:
                        raise SystemExit(f"nasus w: {pre}{tag} {key} changed size")
                    k.sheet[y:y + h, x:x + w] = p
                    k.anims[pre + tag]["frames"][i]["data"] = {q: float(v) for q, v in zip("xywh", have[key][pre])}
            else:
                first = next(j for j, (kk, _) in enumerate(PLAY) if kk == key)
                if first == i:
                    k.extra += [("hd_" + tag, i, pic), (tag, i, one), ("lo_" + tag, i, lo)]
    if check:
        print("nasus w: OK" if not bad else f"nasus w: {', '.join(bad)} not as this tool leaves them")
        sys.exit(1 if bad else 0)
    if not bad:
        print("nasus w: nothing to do")
        return
    k.save()
    # a picture used twice in the play: the later frames take the rects k.save() gave the first
    for form in FORMS:
        tag = form + "skill_w"
        for pre in ("hd_", "", "lo_"):
            fr = k.anims[pre + tag]["frames"]
            for i, (key, _) in enumerate(PLAY):
                first = next(j for j, (kk, _) in enumerate(PLAY) if kk == key)
                if key != "s" and first != i:
                    fr[i]["data"] = dict(fr[first]["data"])
    k.save()
    for form in FORMS:
        k.strip(form + "skill_w")
    print(f"nasus w: {', '.join(bad)} written")


if __name__ == "__main__":
    main()
