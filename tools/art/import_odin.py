#!/usr/bin/env python3
"""奥丁（终末包 ragnarok_odin）的图：Codex 交的逻辑像素图集（assets/source/odin/atlases），原样。

    python tools/art/import_odin.py [--check]
    python tools/art/ppu_hd.py --hero odin          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero odin      # 待机和选人动图
    python tools/art/ragnarok_run_pace.py           # 最后把跑步放慢到一圈 0.92 秒

Codex 2026-11-27 画的（odin_packs/outputs/odin_final_assets.zip，交接说明 assets/source/odin/HANDOFF.md）：第三季动画的老年外观
（黑发黑须、深色长袍、眼罩），冈格尼尔、绕身五盾的神环封壁、呪歌照漫画第十二回合。一格 120×112，脚底 (51, 94)，人站直 48 格
（各帧本来就一致，不用修）。这里按两倍最近邻读进来，PPU 2.4（和金时一样，用户选的；见 tools/art/import_kintoki.py）：
连枪 44 个游戏像素。

画进他自己帧里的（会跟着他左右翻），位置照 frames.json 的 cues（离脚底的偏移，逻辑像素，这里乘 2）：
- 普攻第 4 帧（0.315 秒）出枪的光 thrust；
- 咒歌（ult）第 2 帧（0.14 秒）起绕着上身的符文环 chant，画在身后（画在前面，环和里面的白光从他脸上划过）；
- 咒歌第 6 帧（0.62 秒）顿地的符文场 field，画在身后（见 BAKE）。
放在别处的：刺击命中 thrust_hit、冈格尼尔命中 spear_hit 在目标身上；神环封壁的五面盾 ward 是盾还在的时候挂在他身上的循环
（ragnarok.dll 的 src/odin.rs 按盾的数量放）；身后的双鸦 ravens 也是 src/odin.rs 一直挂着的循环（Codex 说是独立的一层、
放在他身后）；咒歌缠住的敌人身上也挂 chant。飞出去的冈格尼尔是弹道画面 ragnarok_odin_proj（spear_flight，跟着飞行方向转）：
投枪第 4-7 帧他是空手的，第 8 帧枪回到手上（Codex：冈格尼尔离手、命中、回收的时间照这个约定）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "odin")
ID = "ragnarok_odin"
HERO = "odin"
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


def on_unit(tag, fx):
    """挂在单位身上的特效：Codex 说它的中心在脚底 + 偏移；游戏把特效的中心放在单位的枢轴上（脚底往上 FEET 个游戏像素），
    所以特效格里对着枢轴的那一点要挪开同样的距离。"""
    ox, oy = at(tag, fx)
    return (FX_ORIGIN[0] - ox, round(FX_ORIGIN[1] - oy - A.FEET * FX_PPU))


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "thrust", t0("attack", "thrust"), at("attack", "thrust"), None, FX_ORIGIN),
    ("ult", "chant", t0("ult", "chant"), at("ult", "chant"), None, FX_ORIGIN, "behind"),
    # 顿地的符文场：不是左右对称的（枪画在一边），游戏不给数据特效镜像，只能画进他的帧里；Codex 的 8 帧 0.64 秒，这里压进
    # 大招剩下的 0.395 秒（每帧 0.049 秒），画在身后（地上那一圈在脚下，前半圈不盖他的腿）
    ("ult", "field", t0("ult", "field"), at("ult", "field"), 0.049, FX_ORIGIN, "behind"),
]
TARGET_FX = {"thrust_hit": FX_ORIGIN, "spear_hit": FX_ORIGIN, "ward": on_unit("skill2", "ward"),
             "ravens": on_unit("idle", "ravens"), "chant": on_unit("ult", "chant")}
# 飞出去的冈格尼尔：画面中心在枪头（逻辑像素，乘 2），打中时枪头在目标身上
PROJ_FX = {"spear_flight": RA.scaled((79, 65))}

ODIN = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
        "TARGET_FX": TARGET_FX, "PROJ_FX": PROJ_FX, "CANVAS": CANVAS, "READ": RA.reader(SRC, "odin", ID)}

if __name__ == "__main__":
    A.main(ODIN, __doc__)
