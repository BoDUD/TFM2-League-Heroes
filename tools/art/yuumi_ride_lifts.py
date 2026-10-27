#!/usr/bin/env python3
"""The crown of every champion this repo draws, for league_yuumi's ride picture (the user, 2026-10-28: 「猫还有个模型问题
比如附身在烬身上 烬的头部都被挡住了」): game px from the pivot up to the highest opaque square of the first idle frame
within 6 px either side of the frame's middle (the head, not a raised weapon or a wide hat brim), frames being centred on
the pivot. Writes addons/league_yuumi/src/lifts.rs; the add-on lifts the picture by `lift_for(crown)` (its tests).

    python tools/art/yuumi_ride_lifts.py
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
from build_yuumi import RIDE_LIFTS  # noqa: E402

OUT = os.path.join(ROOT, "addons", "league_yuumi", "src", "lifts.rs")
BAND = 6


def crown(fanim):
    a = json.loads(open(fanim, "rb").read().decode("utf-8").lstrip("﻿"))["anims"]
    if "idle" not in a:
        return None
    sh = Image.open(fanim.replace("#anim.fanim", "#sheet.png")).convert("RGBA")
    d = a["idle"]["frames"][0]["data"]
    x, y, w, h = (int(d[k]) for k in "xywh")
    op = np.asarray(sh.crop((x, y, x + w, y + h)))[..., 3] > 0
    mid = (w - 1) / 2
    band = op[:, max(0, int(mid - BAND)):int(mid + BAND + 1)]
    rows = np.nonzero(band.any(1))[0]
    return None if not len(rows) else int(round((h - 1) / 2 - rows.min()))


def main():
    rows = []
    for pack in ("league", "tft"):
        for f in sorted(glob.glob(os.path.join(ROOT, pack, "champions", "*#anim.fanim"))):
            c = crown(f)
            if c is not None:
                rows.append((os.path.basename(f).split("#")[0], c))
    body = "\n".join(f'    ("{n}", {c}),' for n, c in rows)
    lifts = ", ".join(str(k) for k in RIDE_LIFTS)
    text = f"""//! Written by tools/art/yuumi_ride_lifts.py - do not edit. Each champion's crown: game px from his pivot up to the top
//! of his head in his first idle frame; and the ride picture's lifts (tools/kit/build_yuumi.py RIDE_LIFTS).

pub const LIFTS: &[i32] = &[{lifts}];

pub const CROWNS: &[(&str, i32)] = &[
{body}
];
"""
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(OUT, len(rows), "champions")


if __name__ == "__main__":
    main()
