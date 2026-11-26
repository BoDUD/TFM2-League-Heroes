#!/usr/bin/env python3
"""阿波罗（ragnarok_apollo）没拿弓、没有女神像的身体帧：从 Codex 的工作目录取出来，放进 assets/source/apollo/bare。只跑一次。

    python tools/art/apollo_bare.py [Codex 的工作目录]   # 默认 D:/TFM2-Workshop/apollo_packs/codex_apollo

Codex 交的 64 帧是两步出来的（它的 build.py + bow.py）：art/*.png 里画的是空手的身体，先按 build.art_action 排进 256 的格子，
再把光弓（runtime/props/artemis_bow.png，两条光弦 light_string.png）贴进光之矢的第 3-6 帧、把阿尔忒弥斯的女神像
（artemis_statue.png）贴进大招的第 3-5 帧，都照 bow-registration.json 每帧的位置和大小；弓盖在身体上面、握弓的手再盖回来，
女神像在身体后面。弓和像要改（tools/art/apollo_fix.py），就得有贴之前的身体：这里用 Codex 自己的
build.art_action(tag, equip=False) 取出来，排法和交付的图集一样（8 行动作、8 列帧，一格 256），存成
bare/ragnarok_apollo_bare_native。取完先按交付的表再贴一遍，和交付的图集逐帧比，64 帧都一样才写文件。
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "apollo")
DELIVERED = os.path.join(SRC, "runtime", "sprites", "ragnarok_apollo_native")
OUT = os.path.join(SRC, "bare", "ragnarok_apollo_bare_native")


def main():
    codex = sys.argv[1] if len(sys.argv) > 1 else "D:/TFM2-Workshop/apollo_packs/codex_apollo"
    sys.path.insert(0, codex)
    import build as B          # noqa: E402  Codex 的
    import bow as W            # noqa: E402  Codex 的

    reg = json.load(open(os.path.join(SRC, "bow-registration.json"), encoding="utf-8"))["layers"]
    sheet = Image.open(DELIVERED + "#sheet.png").convert("RGBA")
    anims = json.load(open(DELIVERED + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    atlas = Image.new("RGBA", sheet.size)
    for tag, a in anims.items():
        bare = B.art_action(tag, equip=False)
        for i, f in enumerate(a["frames"]):
            d = f["data"]
            cell = sheet.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]))
            given = reg.get(tag, [None] * 8)[i]
            plan = None if given is None else {k: v for k, v in given.items() if k != "attachment_sha256"}
            if W.point_plan(bare[i], tag, i) != plan:
                sys.exit(f"{tag} frame {i + 1}: Codex's bow.py plans another bow / statue than the delivered table - "
                         "not the working folder of the delivery")
            if not np.array_equal(np.asarray(W.hold(bare[i], plan)), np.asarray(cell)):
                sys.exit(f"{tag} frame {i + 1}: pasted again from the table it differs from the delivery - nothing written")
            atlas.paste(bare[i], (d["x"], d["y"]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    atlas.save(OUT + "#sheet.png")
    shutil.copyfile(DELIVERED + "#anim.fanim", OUT + "#anim.fanim")
    print(f"{OUT}#sheet.png: 64 frames; pasted again from the table they equal the delivery")


if __name__ == "__main__":
    main()
