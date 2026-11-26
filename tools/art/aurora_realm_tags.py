#!/usr/bin/env python3
"""阿萝拉领域的光圈拆成开场和一圈：league_aurora_big 里的 r_zone_in / r_zone_loop（和 hd_ 版）。

    python -I tools/art/aurora_realm_tags.py            # 在现有的表上补（或更新）这四个标签
    python -I tools/art/aurora_realm_tags.py --check    # 只核对，不一样就退出 1

2026-11-26（附加包 league_aurora 0.4.0）：副本的领域按等级只开 2.25–3.25 秒、还会提前关，整段的 r_zone 却固定放满
3.25 秒，关了以后光圈还在地上留一两秒，看着像她没穿边界就走出了领域。r_zone 的 30 帧是开场 2 帧加同一段 6 帧循环了
4.67 遍，所以不用画新图，拆成两个标签：

- r_zone_in：r_zone 的第 1、2 帧；
- r_zone_loop：第 3–8 帧，一圈；
- hd_r_zone_in / hd_r_zone_loop：hd_r_zone 同样位置的格子。

格子都是表里原来的，不加像素；r_zone 本身不动，主包还在用。附加包成形时放 r_zone_in，之后一圈接一圈放 r_zone_loop，
关了就不再放下一圈（addons/league_aurora/src/rift.rs 的 zone_view，那边的单元测试读这张表核对帧长）。

帧长按 tick 对齐（一 tick 1/60 秒）：每帧 0.1 秒 = 6 tick（r_zone 是 0.09 / 0.11），开场 12 tick、一圈 36 tick。每个
标签最后接一小段下一圈的第一帧（r_zone 的第 3 帧）：最后一帧提前 0.3 tick 结束，接上的这一帧盖住接缝那一 tick 再多
一点，而新的一圈在这一 tick 开始放的也是这张图——客户端早一帧、晚一帧换下旧的，都不会空一帧，也不会叠出两张不一样的图
（这些图只有全透明和不透明两种像素，同一张图叠两层和一层一样）。

import_aurora_fx.py 整个重新导入时最后会调这里（那时只有 1 倍的）；densify_fx.py 重新生成 hd_ 帧以后再跑一次本工具。
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FANIM = os.path.join(ROOT, "league", "effects", "league_aurora_big#anim.fanim")

# 秒
FRAME = 0.1
LAST = 0.095
TAIL = 0.021667


def realm_tags(anims):
    """r_zone_in / r_zone_loop（有 hd_r_zone 时连同 hd_ 版），取 r_zone 第 1–2 帧、第 3–8 帧原来的格子。"""
    out = {}
    for pre in ("", "hd_"):
        if pre + "r_zone" not in anims:
            continue
        fr = anims[pre + "r_zone"]["frames"]

        def tag(ks):
            frames = [{"duration": FRAME, "data": dict(fr[k]["data"])} for k in ks]
            frames[-1]["duration"] = LAST
            frames.append({"duration": TAIL, "data": dict(fr[2]["data"])})
            return {"frames": frames}

        out[pre + "r_zone_in"] = tag([0, 1])
        out[pre + "r_zone_loop"] = tag(range(2, 8))
    return out


def with_realm_tags(anims):
    """anims 加上 realm_tags（各自排在 r_zone / hd_r_zone 后面），别的标签原样、顺序不变。"""
    new = realm_tags(anims)
    out = {}
    for k, v in anims.items():
        if k in new:
            continue
        out[k] = v
        if k in ("r_zone", "hd_r_zone"):
            pre = k[:-len("r_zone")]
            out[pre + "r_zone_in"] = new[pre + "r_zone_in"]
            out[pre + "r_zone_loop"] = new[pre + "r_zone_loop"]
    return out


def realm_file(check, path=FANIM):
    """补上（check 时只核对）表里的光圈标签；表的写法照 strips.write_sheet（紧凑的 JSON）。"""
    raw = open(path, encoding="utf-8").read()
    anims = json.loads(raw)["anims"]
    text = json.dumps({"anims": with_realm_tags(anims)}, separators=(",", ":"))
    name = os.path.relpath(path, ROOT).replace("\\", "/")
    if check:
        if text != raw:
            sys.exit(f"{name}: r_zone_in / r_zone_loop are not the ones r_zone gives "
                     "(python -I tools/art/aurora_realm_tags.py)")
        print(f"{name}: r_zone_in / r_zone_loop and their hd_ twins up to date")
        return
    if text != raw:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    print(f"{name}: {', '.join(realm_tags(anims))}" + ("" if text != raw else " (unchanged)"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只核对，不写")
    a = ap.parse_args()
    realm_file(a.check)


if __name__ == "__main__":
    main()
