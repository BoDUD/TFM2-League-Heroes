#!/usr/bin/env python3
"""坂田金时（终末包 ragnarok_kintoki）的图：Codex 交的逻辑像素图集，换过头的那份（assets/source/kintoki/fix）。

    python tools/art/ragnarok_atlas_fix.py      # 先修 Codex 的图集（同一个头、待机第 3 帧）-> fix/
    python tools/art/import_kintoki.py [--check]
    python tools/art/ppu_hd.py --hero kintoki   # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero kintoki   # 待机和选人动图
    python tools/art/ragnarok_run_pace.py       # 最后把跑步放慢到一圈 0.92 秒

Codex 2026-11-27 画的（kintoki_packs/outputs/kintoki_final_assets.zip，交接说明 assets/source/kintoki/HANDOFF.md）：动画的
金发、黑底金纹头带、眼侧红纹、红金深色衣服，漫画第十二回合的巨型单刃斧、右手的神性之证。一格 120×112，脚底 (51, 94)，
人站直 44 格。tools/art/ragnarok_atlas_fix.py 只在 Codex 的像素上整格地换头（待机、跑步各一个头，没有缩放）；这里按两倍
最近邻读进来（像素画只按整数倍放大），PPU 2.4：一个像素 0.83 个游戏像素（全包是 0.73），连斧 37.5 个游戏像素，和
赫拉克勒斯一样高。用户先看了按 1.25 倍重出像素、PPU 2.75 的一版：「codex画出来的美术质量很高啊 为什么你像素处理后质量这么差
这两个英雄」，再在 Codex 原样的三种 PPU 里选了 2.4。

画进他自己帧里的（会跟着他左右翻），位置照 frames.json 的 cues（离脚底的偏移，逻辑像素，这里乘 2）：
- 普攻第 4 帧（0.285 秒）的横扫弧 sweep；
- 下劈（skill）第 6 帧（0.58 秒）斧落地的碎岩 cleave_hit（第 5 帧劈下的那道光 cleave_cast 不画进帧里：照 Codex 的位置
  它悬在斧头上方慢慢落下，像飘着的火；改成飞出去的光刃的画面，见下）；
- 踏步突进（skill2）第 3 帧（0.18 秒）起的拖尾 rush_trail，画在身后；
- 终结技（ult）第 1 帧（0 秒）右手的神性之证 divinity、第 6 帧（0.67 秒）大斧落地 final_hit（画在身后：它有 104 格宽，
  画在前面把他腰以下整个盖住）。
打在人身上的：横扫命中 sweep_hit、突进命中 rush_hit、光刃一路炸开的 cleave_hit；飞出去的光刃（烈煌闪）是弹道画面
ragnarok_kintoki_proj（cleave_cast 那道光，跟着飞行方向转）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kintoki", "fix")
ID = "ragnarok_kintoki"
HERO = "kintoki"
PPU = 2.4                   # 和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 2.4                # 特效和人一个比例（hd.rs 的 EFFECTS）
META = RA.meta(SRC)
SOLE = RA.scaled(tuple(META["ground"]))
FX_ORIGIN = tuple(round(v * RA.ZOOM) for v in META["fx_cell_anchor"])
CANVAS = (380, 300, (160, 250))
CUES = {(t, c["fx"]): c for t, cs in META["cues"].items() for c in cs}


def at(tag, fx):
    """Codex 的偏移（离脚底，逻辑像素）-> 放大后的偏移。"""
    dx, dy = CUES[(tag, fx)]["offset"]
    return (round(dx * RA.ZOOM), round(dy * RA.ZOOM))


def t0(tag, fx):
    return CUES[(tag, fx)]["time_s"]


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "sweep", t0("attack", "sweep"), at("attack", "sweep"), None, FX_ORIGIN),
    ("skill", "cleave_hit", t0("skill", "cleave_hit"), at("skill", "cleave_hit"), None, FX_ORIGIN),
    ("skill2", "rush_trail", t0("skill2", "rush_trail"), at("skill2", "rush_trail"), None, FX_ORIGIN, "behind"),
    ("ult", "divinity", t0("ult", "divinity"), at("ult", "divinity"), None, FX_ORIGIN),
    ("ult", "final_hit", t0("ult", "final_hit"), at("ult", "final_hit"), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"sweep_hit": FX_ORIGIN, "rush_hit": FX_ORIGIN, "cleave_hit": FX_ORIGIN}
# 飞出去的光刃：cleave_cast 前 4 帧（又高又亮的那段）循环，画面中心在光的中间（逻辑像素，乘 2）
FX_SLICE = {"slash": ("cleave_cast", 0, 4)}
PROJ_FX = {"slash": RA.scaled((79, 63))}

KINTOKI = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
           "TARGET_FX": TARGET_FX, "PROJ_FX": PROJ_FX, "FX_SLICE": FX_SLICE, "CANVAS": CANVAS,
           "READ": RA.reader(SRC, "kintoki", ID)}

if __name__ == "__main__":
    A.main(KINTOKI, __doc__)
