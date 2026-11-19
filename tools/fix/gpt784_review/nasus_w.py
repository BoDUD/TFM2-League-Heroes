"""league_nasus's W (Wither, skill_w / b_skill_w) the way League's Nasus casts it (the user, 2026-11-19: 「狗头的平A动作不像
英雄联盟的 重改 包括释放其他技能时都要像英雄联盟的动作才行」, then on the first try, an arm turned upside down: 「左手变形了啊
武器也变形 你自己不review的吗」): Nasus_Base_Spell2_Full raises his free hand high over his head and holds it there, the
staff low in the other hand. GPT's W pushed the free hand out in front with the staff raised beside the head.

His stance (idle_base[0] / b_idle_base[0]) already holds the staff low in his front hand alone; the back arm hangs
free beside him. The up picture: that hanging arm (HANG: its rows, its columns per row) taken away, and in its place
GPT's own W arm raised - the forearm GPT drew pointing forward (FORE) turned a quarter to point up (no square scaled
or redrawn: a quarter turn keeps every square), the open hand at its end (HAND: fingers up, as GPT drew it) left as it
is on top - rising from behind the pauldron (only clear squares take it: the pauldron and the head stay in front). The
mid picture is the same arm DROP rows lower, the hand just over the pauldron: the arm comes up, it never changes shape.
Where the arm hung the body's bare edge is outlined (nasus_clean.py's first step only: its band pass, which counts
near-black shade as outline, would take the thin staff end the fist hid), then tools/art/thin_outline.py's own pass
(pure outline only); the staff, the head and the rest stay the stance's squares.

The W plays: the stance, half up, up (held), half up, the stance - 300 ms like GPT's four frames. The 1x and lo_
frames of the two pictures are sheetkit's (tools/fix/xinzhao_galio_1119/sheetkit.py), the stance's frame sizes. The
strips nasus_[b_]skill_w (assets/source/ppu[/orig]) are written from the tags. Run after nasus_clean.py and
nasus_actions.py; nasus_clean.py leaves the two pictures alone (only skill_w tags show them).

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

# per form: the stance tag; GPT's W picture (its rect: GPT's skill_w[2] / b_skill_w[2], no tag plays it since); HANG
# (first row, last row, [(up to row, first column, last column)]); FORE and HAND (rows, columns) in GPT's W picture;
# PLACE (top row, left column of the raised arm, the hand's shift right of the forearm, rows the hand overlaps it); DROP
FORMS = {
    "": ("idle_base", (0, 3609, 88, 85), (24, 37, [(33, 26, 35), (37, 30, 36)]), ((21, 26), (53, 63)),
         ((16, 25), (64, 71)), (0, 28, 0, 3), 7),
    "b_": ("b_idle_base", (219, 4542, 104, 116), (32, 50, [(45, 29, 40), (50, 33, 42)]), ((26, 34), (63, 80)),
           ((21, 34), (80, 89)), (0, 33, -1, 8), 9),
}
# (picture, ms): s stance, m half up, u up
PLAY = [("s", 50), ("m", 50), ("u", 140), ("m", 30), ("s", 30)]


def raised_arm(w, fore, hand, dx, overlap):
    """GPT's W forearm turned to point up, the hand on top -> RGBA patch, the forearm's column offset in it."""
    (fy0, fy1), (fx0, fx1) = fore
    (hy0, hy1), (hx0, hx1) = hand
    fp = w[fy0:fy1 + 1, fx0:fx1 + 1]
    hp = w[hy0:hy1 + 1, hx0:hx1 + 1]
    fv = np.rot90(fp, 1)                       # a quarter turn: its wrist end (right) on top
    fx = max(0, -dx)
    out = np.zeros((hp.shape[0] - overlap + fv.shape[0], max(fx + fv.shape[1], fx + dx + hp.shape[1]), 4), np.uint8)
    y = hp.shape[0] - overlap
    sub = out[y:y + fv.shape[0], fx:fx + fv.shape[1]]
    out[y:y + fv.shape[0], fx:fx + fv.shape[1]] = np.where(fv[..., 3:] > 0, fv, sub)
    sub = out[:hp.shape[0], fx + dx:fx + dx + hp.shape[1]]
    out[:hp.shape[0], fx + dx:fx + dx + hp.shape[1]] = np.where(hp[..., 3:] > 0, hp, sub)
    return out


def edge_outline(a):
    """nasus_clean.py's first step alone: the body's bare edge outlined where the body goes on inside it."""
    a = a.copy()
    op = a[..., 3] > 0
    is_o = op & (a[..., :3] == nc.OUTLINE).all(-1)
    edge = op & nc.four(~op, True)
    a[edge & ~is_o & ~nc.glows(a) & nc.four(op & ~edge, False), :3] = nc.OUTLINE
    return a


def pose(c, w, form, drop):
    _, _, (r0, r1, parts), fore, hand, (top, left, dx, overlap), _ = FORMS[form]
    out = c.copy()
    for r in range(r0, r1 + 1):
        c0, c1 = next((a, b) for upto, a, b in parts if r <= upto)
        out[r, c0:c1 + 1] = 0
    arm = raised_arm(w, fore, hand, dx, overlap)
    h, wd = out.shape[:2]
    ys, xs = np.nonzero(arm[..., 3] > 0)
    for y, x in zip(ys, xs):
        Y, X = top + drop + y, left + x
        if 0 <= Y < h and 0 <= X < wd and out[Y, X, 3] == 0:
            out[Y, X] = arm[y, x]
    # thin_outline.py's own pass (outline = pure (4, 3, 1) only, so the staff's near-black end stays) for its CI check
    return nc.th.change_fixed(edge_outline(out), nc.TP["hd"], nc.TP["outline"], nc.TP["grow"])[0]


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
        x, y, w, h = FORMS[form][1]
        src = k.sheet[y:y + h, x:x + w]
        pics = {"m": pose(hd, src, form, FORMS[form][6]), "u": pose(hd, src, form, 0)}
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
