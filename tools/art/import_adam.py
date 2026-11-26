#!/usr/bin/env python3
"""亚当（终末包 ragnarok_adam）的图：身体是 Codex 照动画第一季重画的两倍帧（assets/source/adam/rebuild，
tools/art/adam_rebuild_fix.py 修过头、脖子、眼睛和指虎），特效是 tools/art/adam_repixel.py 两倍重出的那套
（rebuild/ 里那份和 repixel/ 的一样）。

    python tools/art/adam_repixel.py                # 先重出特效（还有旧的身体，现在不用）
    python tools/art/adam_rebuild_fix.py            # 再修 Codex 重画的身体帧
    python tools/art/import_adam.py [--check]
    python tools/art/ppu_hd.py --hero adam          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero adam      # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-21 画的第一版（分支 codex/ragnarok-adam-assets，提交 35eaf0a86）是 128 格、站高 54 格、PPU 1.65 的像素图，
用户嫌它糊、描边断、手臂细（「我要像素图风格但是你这种也太模糊了」「用PPU提高像素后再处理吧」，看过 1.5 倍和两倍的
对比后「亚当就3.3吧」），所以按两倍出：一格 256、脚底点 (128, 232)、站高 108 格，游戏里 PPU 3.3，个子还是 33 个
游戏像素。重画的这版格子、脚底点、帧数和时长都和原来一样，各动作都站在同一个点上，不用像索尔那样挪。
引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻）：普攻 0.225 秒的拳风；神虚视 0 秒睁眼的光（逐帧跟着眼睛，闪避时头往下沉）和
0.17 秒的闪避气流；模仿反击 0.1 秒的模仿标记（逐帧跟着脸）和 0.235 秒拳头前的反击火花；超越时间之拳 0.05 秒的蓄势和
0.43 秒的释放。锚点都在重画的帧上重新量过（下面 BAKE 前面写了怎么量的）。
放在目标身上的只有普攻的命中火花 jab_hit（对称的，不怕不翻）。反击火花 copy_hit 是朝右的，所以画在拳头前面。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "adam", "rebuild")
ID = "ragnarok_adam"
HERO = "adam"
UP = 2.0                    # 和 tools/art/adam_repixel.py 的 UP 一样
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = round(1.65 * UP / 1.2, 3)   # 2.75（放大前 3.3）
FX_PPU = round(1.65 * UP, 3)     # 3.3：特效图不放大
SOLE = (round(64 * UP), round(116 * UP))
FX_ORIGIN = (round(64 * UP), round(64 * UP))      # 特效格的中心
CANVAS = (round(288 * UP), round(224 * UP), (round(144 * UP), round(176 * UP)))


# 锚点：离脚底点的偏移（两倍帧里的像素，往右往下为正），2026-11-21 在 adam_rebuild_fix.py 修过的帧上量的。
# 拳头上的三个：先量出拳那帧拳头最前面（指虎那几行最右边的像素），再加上 Codex 原来那版锚点离拳头的距离
# （原来的帧是照同样的动作画的，特效的位置关系不变）：普攻第 4 帧拳头在 (171, 161)，拳风再往前 7、往下 2；
# 模仿反击第 4 帧拳头 (168, 162)，反击火花往前 28、往下 4；大招第 5 帧拳头 (178, 168)，释放的那道墙正好在拳头上
# （特效中心往前 36、往上 2）。
# 睁眼的光：每帧蓝眼珠的中心（贴的头只有眼珠是这种蓝）；模仿标记：眼珠往右 2、往下 12（Codex 原来的位置关系，
# 两个括号夹着下半张脸）。闪避气流和蓄势跟身子：新帧的身子比原来的往右挪了 4 格（神虚视第 3-5 帧）、往左 1 格
# （大招第 1-4 帧），锚点跟着挪。
EYES = [(9, -87), (9, -81), (-2, -75), (3, -68), (6, -72), (2, -79), (-2, -83), (3, -83)]     # 神虚视 8 帧
MARK = [(10, -70), (7, -71), (6, -72), (10, -69), (12, -70), (10, -71), (5, -73), (9, -73)]   # 模仿反击 8 帧

# (动作, 特效, 开始秒, 离脚底的锚点或每帧一串, 每帧秒数（None 用特效自己的）, 特效格里的原点)
BAKE = [
    ("attack", "jab_wind", 0.225, (50, -69), None, FX_ORIGIN),
    ("skill", "eyes_ready", 0.0, EYES, None, FX_ORIGIN),
    ("skill", "dodge_wind", 0.17, (-8, -60), None, FX_ORIGIN),
    ("skill2", "copy_mark", 0.10, MARK, None, FX_ORIGIN),
    ("skill2", "copy_hit", 0.235, (68, -66), None, FX_ORIGIN),
    ("ult", "time_charge", 0.05, (17, -60), None, FX_ORIGIN),
    ("ult", "time_release", 0.43, (86, -66), None, FX_ORIGIN),
]
RETIME = {}
TARGET_FX = {"jab_hit": FX_ORIGIN}
# 跑步逐帧左右挪（只挪不画）：Codex 重画的跑步，人在格子里前后晃，蓝眼珠离落点 21.5、18.5、20、18、13.5、12、8.5、18 格，
# 前四帧往前、第 5-7 帧往后缩，相差 13 格（约 4 个游戏像素），跑起来身子一抖一抖；128 格那版同样八帧头只差 2 格（放大后 4 格）。
# 挪成和 128 格那版一样的起伏（各帧离平均的差照它）
SHIFT = {"run": [-4, -1, -4, 0, 0, 4, 5, 0]}

ADAM = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
        "TARGET_FX": TARGET_FX, "CANVAS": CANVAS, "SHIFT": SHIFT}

if __name__ == "__main__":
    A.main(ADAM, __doc__)
