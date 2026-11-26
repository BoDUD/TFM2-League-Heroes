#!/usr/bin/env python3
"""开膛手杰克（终末包 ragnarok_jack）的图：Codex 交的两倍密度身体和特效（assets/source/jack）。

    python tools/art/jack_fix.py                    # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_jack.py [--check]
    python tools/art/ppu_hd.py --hero jack          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero jack      # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-21 画的（jack_packs/outputs/jack_assets_done.zip，交接说明 assets/source/jack/HANDOFF.md）：动画第二季第四回合的
造型（酒红礼帽、白羽、单片镜、黑手套），一格 256，脚底 (128, 232)，8 个动作各 8 帧，人站直 115 格（连帽上的羽毛），
PPU 3.3 是 35 个游戏像素。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：扇形飞刀出手 0.286 秒、撑伞时伞前的护弧
0.194 秒、手套触物 0.346 秒都在身后（一组 200 格左右宽，画在前面会盖住脸和身子）；后撤时的雾 0.267 秒画在前面（他是
躲进雾里）。放在目标身上的：飞刀命中 knife_hit、收招 dear_god，还有大招起手单片镜那道异色的光 emotion_glint（Codex 画在
他眼睛上，一圈比他的头还大，放在被他看穿的人身上）。飞出去的那把刀：ragnarok/effects/ragnarok_jack_proj，1 倍
（PROJ_FX，跟着飞行方向转）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jack", "snapped")
ID = "ragnarok_jack"
HERO = "jack"
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = 2.75                  # 放大前 3.3；和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图不放大（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (576, 448, (288, 352))


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("skill", "knife_fan", 0.286, at(164, 149), None, FX_ORIGIN, "behind"),
    ("skill2", "umbrella_guard", 0.194, at(146, 147), None, FX_ORIGIN, "behind"),
    ("skill2", "veil_fog", 0.267, at(128, 180), None, FX_ORIGIN),
    ("ult", "artifact_touch", 0.346, at(160, 184), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"knife_hit": FX_ORIGIN, "dear_god": FX_ORIGIN, "emotion_glint": FX_ORIGIN}
PROJ_FX = {"knife_flight": FX_ORIGIN}

JACK = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
        "TARGET_FX": TARGET_FX, "PROJ_FX": PROJ_FX, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(JACK, __doc__)
