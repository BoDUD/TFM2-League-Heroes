#!/usr/bin/env python3
"""洛基（终末包 ragnarok_loki）的图：Codex 交的逻辑像素图集（assets/source/loki/atlases）。

    python tools/art/import_loki.py [--check]
    python tools/art/ppu_hd.py --hero loki           # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero loki       # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-26 画的（loki_packs/outputs/loki_final_assets.zip，提交 629e39838，交接说明 assets/source/loki/HANDOFF.md）：
动画角色设定的样子（绿发、紫色肩甲、银色交叉纹、深蓝长衣），Q 版像素画。一格 132×96 逻辑像素，脚底 (61, 87)，人站直 56 格；
特效格同样大，中心 (66, 48)。和冲田一样（tools/art/import_okita.py）：两倍最近邻读进来，PPU 8/3，站直 42 个游戏像素，特效和人
一个比例。

画进他自己帧里的（会跟着他左右翻），位置照 frames.json 的 fx_events（离脚底的偏移，逻辑像素，这里乘 2），时间照 cues：
- 普攻第 4 帧（0.279 秒）的幻刃 flick；
- 锁链钩（skill）第 2 帧（0.105 秒）的锁链聚势 hook_windup（一圈绿光越长越大，画在前面会从脸上划过去，画在身后）、
  第 4 帧（0.297 秒）钩刃飞出 hook（链子伸出去再收回来）；
- 迷雾诱饵（skill2）第 3 帧（0.2 秒）脚下的黑雾 shadow_veil（画在身后）。
放在别处的：诱饵显形 decoy、幻影军势 phantom_field 落在地上（技能放在哪里就在哪里，不跟着他翻）；命中 hook_hit、
幻影击中 phantom_hit 放在目标身上。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "loki")
ID = "ragnarok_loki"
HERO = "loki"
PPU = 2.667                 # 8/3，和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 2.667
SOLE = RA.scaled((61, 87))
FX_ORIGIN = RA.scaled((66, 48))
CANVAS = (480, 320, (200, 260))


def at(dx, dy):
    """Codex 的偏移（离脚底，逻辑像素）-> 放大后的偏移。"""
    return RA.scaled((dx, dy))


def on_unit(dx, dy):
    """挂在单位身上（或落在地上一点）的特效：中心在脚底 + (dx, dy)，游戏把特效中心放在枢轴上（脚底往上 FEET 个游戏像素）。"""
    ox, oy = at(dx, dy)
    return (FX_ORIGIN[0] - ox, round(FX_ORIGIN[1] - oy - A.FEET * FX_PPU))


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "flick", 0.279, at(22, -30), None, FX_ORIGIN),
    ("skill", "hook_windup", 0.105, at(15, -28), None, FX_ORIGIN, "behind"),
    ("skill", "hook", 0.297, at(35, -32), None, FX_ORIGIN),
    ("skill2", "shadow_veil", 0.2, at(7, -19), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"hook_hit": FX_ORIGIN, "phantom_hit": FX_ORIGIN, "decoy": on_unit(0, -20), "phantom_field": on_unit(0, -23),
             "shadow_veil": on_unit(0, -19)}

LOKI = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
        "TARGET_FX": TARGET_FX, "CANVAS": CANVAS, "READ": RA.reader(SRC, "loki", ID)}

if __name__ == "__main__":
    A.main(LOKI, __doc__)
