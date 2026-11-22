#!/usr/bin/env python3
"""零福（ragnarok_zerofuku）没拿斧子的身体帧：从 Codex 的工作目录取出来，放进 assets/source/zerofuku/bare。只跑一次。

    python tools/art/zerofuku_bare.py [Codex 的工作目录]   # 默认 D:/TFM2-Workshop/zerofuku_packs/codex_zerofuku

Codex 交的常态 64 帧是两步出来的（它的 build.py + rigid_axe.py）：art/*_grip.png 里画的是空手握拳的身体，先按 build.artwork
排进 256 的格子，再把一把横着画的斧子（runtime/props/misery_cleaver.png）照 axe-registration.json 每帧的握点、角度、长度贴上去，
握柄的手再从身体那层盖回斧柄上面。斧子要改（tools/art/zerofuku_fix.py），就得有贴斧子之前的身体：这里用 Codex 自己的
build.artwork(equip=False) 取出来，排法和交付的图集一样（8 行动作、8 列帧，一格 256），存成 bare/ragnarok_zerofuku_bare_native。
取完先按它原来的表再贴一遍斧子，和交付的图集逐帧比，64 帧都一样才写文件。
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "zerofuku")
DELIVERED = os.path.join(SRC, "runtime", "sprites", "ragnarok_zerofuku_native")
OUT = os.path.join(SRC, "bare", "ragnarok_zerofuku_bare_native")


def main():
    codex = sys.argv[1] if len(sys.argv) > 1 else "D:/TFM2-Workshop/zerofuku_packs/codex_zerofuku"
    sys.path.insert(0, codex)
    import build as B          # noqa: E402  Codex 的
    import rigid_axe as X      # noqa: E402  Codex 的

    plan = json.loads(open(os.path.join(codex, "art", "axe_frames.json"), "rb").read())
    reg = json.load(open(os.path.join(SRC, "axe-registration.json"), encoding="utf-8"))
    if plan != reg["frames"]:
        sys.exit("art/axe_frames.json differs from the delivered axe-registration.json: not the working folder of the delivery")
    sheet = Image.open(DELIVERED + "#sheet.png").convert("RGBA")
    anims = json.load(open(DELIVERED + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    atlas = Image.new("RGBA", sheet.size)
    for tag, a in anims.items():
        bare = B.artwork(tag, equip=False)
        for i, f in enumerate(a["frames"]):
            d = f["data"]
            cell = sheet.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]))
            p = plan.get(tag, [None] * 8)[i]
            again = X.attach(bare[i], p) if p else bare[i]
            if not np.array_equal(np.asarray(again), np.asarray(cell)):
                sys.exit(f"{tag} frame {i + 1}: the axe pasted again from the plan differs from the delivery - nothing written")
            atlas.paste(bare[i], (d["x"], d["y"]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    atlas.save(OUT + "#sheet.png")
    shutil.copyfile(DELIVERED + "#anim.fanim", OUT + "#anim.fanim")
    print(f"{OUT}#sheet.png: 64 frames; pasted again from the plan they equal the delivery")


if __name__ == "__main__":
    main()
