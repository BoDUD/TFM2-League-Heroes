#!/usr/bin/env python3
"""亚当（终末包 ragnarok_adam）的图，来自 Codex 交的 assets/source/adam/runtime/sprites。

    python tools/art/import_adam.py [--check]
    python tools/art/ppu_hd.py --hero adam          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero adam      # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-21 画的（分支 codex/ragnarok-adam-assets，提交 35eaf0a86），和吕布、索尔、宙斯一样的 128 格，脚底点
(64, 116)，八个动作各 8 帧，人站着头顶离脚底 54 格，按索尔的 PPU 1.65 是 33 个游戏像素。各动作都站在同一个点上
（躯干中线 63-66），不用像索尔那样挪。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻）按 Codex 的 cues.json 放，锚点从 128 格换成离脚底的偏移：
普攻 0.225 秒的拳风；神虚视 0 秒睁眼的光（跟着头走，头在闪避时往下沉 8 格）和 0.17 秒的闪避气流；
模仿反击 0.1 秒的模仿标记（跟着身子走）和 0.235 秒拳头上的反击火花；超越时间之拳 0.05 秒的蓄势和 0.43 秒的释放。
放在目标身上的只有普攻的命中火花 jab_hit（对称的，不怕不翻）。反击火花 copy_hit 是朝右的，所以画在拳头上。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "adam", "runtime", "sprites")
ID = "ragnarok_adam"
HERO = "adam"
PPU = 1.65                  # 和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
SOLE = (64, 116)


def follow(track, base, ref):
    """按身体帧跟着走的锚点：track 是每帧头（或身子）相对待机的位移，base 是 Codex 给的锚点（在 ref 那帧量的）。"""
    rx, ry = track[ref]
    return [(base[0] + dx - rx, base[1] + dy - ry) for dx, dy in track]


# 每帧头相对待机第 1 帧的位移（拿待机的头去逐帧对出来的）：神虚视闪避时头往左下沉，模仿反击出拳时往前
SKILL_HEAD = [(3, 0), (2, 1), (-5, 4), (-3, 8), (0, 5), (-1, 2), (-3, 0), (-1, -1)]
SKILL2_HEAD = [(-1, 0), (1, 0), (0, 0), (0, 1), (4, 2), (2, 1), (-1, 0), (-1, -1)]
# Codex 的锚点（128 格里的坐标）减去脚底点
EYES = follow(SKILL_HEAD, (71 - 64, 74 - 116), 0)       # 0 秒，第 1 帧
MARK = follow(SKILL2_HEAD, (72 - 64, 80 - 116), 1)      # 0.1 秒，第 2 帧

# (动作, 特效, 开始秒, 离脚底的锚点或每帧一串, 每帧秒数（None 用特效自己的）)
BAKE = [
    ("attack", "jab_wind", 0.225, (88 - 64, 81 - 116), None),
    ("skill", "eyes_ready", 0.0, EYES, None),
    ("skill", "dodge_wind", 0.17, (58 - 64, 86 - 116), None),
    ("skill2", "copy_mark", 0.10, MARK, None),
    ("skill2", "copy_hit", 0.235, (96 - 64, 82 - 116), None),
    ("ult", "time_charge", 0.05, (73 - 64, 86 - 116), None),
    ("ult", "time_release", 0.43, (104 - 64, 82 - 116), None),
]
RETIME = {}
TARGET_FX = {"jab_hit": (64, 64)}

ADAM = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
        "TARGET_FX": TARGET_FX}

if __name__ == "__main__":
    A.main(ADAM, __doc__)
