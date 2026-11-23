#!/usr/bin/env python3
"""列奥尼达斯（ragnarok_leonidas）没拿盾的身体帧：从 Codex 的工作目录取出来，放进 assets/source/leonidas/bare。只跑一次。

    python tools/art/leonidas_bare.py [Codex 的工作目录]   # 默认 D:/TFM2-Workshop/leonidas_packs/codex_leonidas

Codex 交的 64 帧是两步出来的（它的 build.py + shield.py）：art/*.png 里画的是空手的身体，先按 build.art_action 排进 256 的
格子，再把盾（runtime/props/round_shield.png，大招第 3-7 帧换 truth_shield.png；链盾飞出去那三帧再加一条 chain.png）照
shield-registration.json 每帧的中心、角度、大小贴上去，盾盖在身体上面（倒地后的盾在身体下面）。盾要改（tools/art/leonidas_fix.py），
就得有贴盾之前的身体：这里用 Codex 自己的 build.art_action(tag, equip=False) 取出来，排法和交付的图集一样（8 行动作、8 列帧，
一格 256），存成 bare/ragnarok_leonidas_bare_native。取完先按交付的表再贴一遍盾，和交付的图集逐帧比，64 帧都一样才写文件；
链盾那一行还要和它另交的 runtime/sprites/ragnarok_leonidas_throw_body_native（同一组没拿盾的身体）一样。
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "leonidas")
DELIVERED = os.path.join(SRC, "runtime", "sprites", "ragnarok_leonidas_native")
THROW = os.path.join(SRC, "runtime", "sprites", "ragnarok_leonidas_throw_body_native")
OUT = os.path.join(SRC, "bare", "ragnarok_leonidas_bare_native")


def main():
    codex = sys.argv[1] if len(sys.argv) > 1 else "D:/TFM2-Workshop/leonidas_packs/codex_leonidas"
    sys.path.insert(0, codex)
    import build as B          # noqa: E402  Codex 的
    import shield as S         # noqa: E402  Codex 的

    reg = json.load(open(os.path.join(SRC, "shield-registration.json"), encoding="utf-8"))["frames"]
    sheet = Image.open(DELIVERED + "#sheet.png").convert("RGBA")
    anims = json.load(open(DELIVERED + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    throw = Image.open(THROW + "#sheet.png").convert("RGBA")
    throw_anims = json.load(open(THROW + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    atlas = Image.new("RGBA", sheet.size)
    for tag, a in anims.items():
        bare = B.art_action(tag, equip=False)
        for i, f in enumerate(a["frames"]):
            d = f["data"]
            cell = sheet.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]))
            plan = {k: v for k, v in reg[tag][i].items() if k != "attachment_sha256"}
            if S.pose_plan(bare[i], tag, i) != plan:
                sys.exit(f"{tag} frame {i + 1}: Codex's shield.py plans another shield than the delivered table - "
                         "not the working folder of the delivery")
            if not np.array_equal(np.asarray(S.hold(bare[i], plan)), np.asarray(cell)):
                sys.exit(f"{tag} frame {i + 1}: the shield pasted again from the table differs from the delivery - nothing written")
            if tag == "skill":
                t = throw_anims["skill"]["frames"][i]["data"]
                body = throw.crop((t["x"], t["y"], t["x"] + t["w"], t["y"] + t["h"]))
                if not np.array_equal(np.asarray(body), np.asarray(bare[i])):
                    sys.exit(f"skill frame {i + 1}: differs from the delivered throw body - nothing written")
            atlas.paste(bare[i], (d["x"], d["y"]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    atlas.save(OUT + "#sheet.png")
    shutil.copyfile(DELIVERED + "#anim.fanim", OUT + "#anim.fanim")
    print(f"{OUT}#sheet.png: 64 frames; pasted again from the table they equal the delivery")


if __name__ == "__main__":
    main()
