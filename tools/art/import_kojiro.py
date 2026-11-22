#!/usr/bin/env python3
"""佐佐木小次郎（终末包 ragnarok_kojiro）的图：Codex 交的两倍密度身体、双刀待机和特效（assets/source/kojiro）。

    python tools/art/kojiro_fix.py                  # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_kojiro.py [--check]
    python tools/art/ppu_hd.py --hero kojiro        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero kojiro    # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-21 画的（kojiro_packs/outputs/kojiro_assets_done.zip，交接说明 assets/source/kojiro/HANDOFF.md）：动画第一季
第三回合的年长造型，一格 256，脚底 (128, 232)，单刀 8 个动作各 8 帧，人站直 112 格，PPU 3.3 是 34 个游戏像素（和波塞冬、
亚当一样高）。引擎是 tools/art/ragnarok_art.py。

三张图合成一张（BANKS）：单刀的 8 个动作原名；双刀待机 dual_idle 改名 niten_idle；大招（双刀两连斩）再放一份叫 niten_attack，
二天岩流之后的普攻：按普攻的节奏重排时长（RETIME：第一刀第 4 帧落在 0.24 秒，和单刀普攻出刀同一刻，总长和普攻一样 0.595 秒）。
ragnarok.dll（addons/ragnarok/src/kojiro.rs）的显示钩子在他身上有二天岩流的 buff 时把 idle / attack 换成这两个。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：燕返 0.275 秒的刀光；千手无双 0.18 秒的预判涟漪
（身子中间）；二天岩流 0.365 秒的双刀交错，双刀普攻 0.24 秒同一个。放在目标身上的：命中的金属火花 steel_impact。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kojiro", "snapped")
ID = "ragnarok_kojiro"
HERO = "kojiro"
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = 2.75                  # 放大前 3.3；和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图不放大（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (576, 448, (288, 352))

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
BANKS = [
    (f"{ID}_native", {t: t for t in ACTS}),
    (f"{ID}_niten_native", {"dual_idle": "niten_idle"}),
    (f"{ID}_native", {"ult": "niten_attack"}),
]
TAGS = list(ACTS) + ["niten_idle", "niten_attack"]
# 大招 150, 125, 90 | 60, 62, 65, 95, 145 毫秒：前三帧缩到 0.24 秒、后五帧缩到 0.355 秒
RETIME = {"niten_attack": [0.099, 0.082, 0.059, 0.050, 0.052, 0.054, 0.079, 0.120]}

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心)
# 都画在他身后（"behind"）：燕返的月牙是刀从脑后举起往前劈的轨迹，涟漪围着身子，双刀交错的一端扫过头，画在前面会盖住
# 头和脸（索尔大招的雷圈也是这样改的）；画在后面是从身后绕过，身前那截照样露出来
BAKE = [
    ("skill", "swallow_slash", 0.275, (155 - 128, 137 - 232), None, FX_ORIGIN, "behind"),
    ("skill2", "prediction_ring", 0.18, (128 - 128, 145 - 232), None, FX_ORIGIN, "behind"),
    ("ult", "dual_cross", 0.365, (163 - 128, 144 - 232), None, FX_ORIGIN, "behind"),
    ("niten_attack", "dual_cross", 0.24, (163 - 128, 144 - 232), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"steel_impact": FX_ORIGIN}

KOJIRO = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
          "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(KOJIRO, __doc__)
