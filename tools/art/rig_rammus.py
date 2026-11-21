#!/usr/bin/env python3
"""league_rammus's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way: no
Codex strips, lossless poses compared with League's clips).

    python tools/art/rig_rammus.py --parts DIR       # the side design with its parts tinted + pose tries (12x)
    python tools/art/rig_rammus.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_rammus.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_rammus.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_rammus_model.py, the user's picks 2026-10-19; 36 game px at PPU 1.2, one palette):
idle.png (A-2, 3/4 front, 41 x 42), side.png (S-1, side-on facing right, 39 x 43: every action's base), ball.png
(Powerball's spiked ball, 45 x 44) and curl.png (Defensive Ball Curl, side-on, 41 x 41). Every pose is lossless: parts
cut square by square from a design and only moved by whole squares, quarter turns about half-integer pivots and
mirrors. The side design is the rig's own (its standing point and ground); the other three stand on the same point and
ground.
滚球是唯一的例外（2026-11-21）：附加包的 b_run 和主包 Q 的 skill_roll 是球的设计图绕自己的重心每帧顺时针转 15 度、
24 帧一圈（像素画的转法，见 turned_ball）；R 跳起来的球还是整颗球四分之一转。
Parts of the side design: the near arm (hanging in front of the belly, claws at the bottom; it turns about its
shoulder), the two feet (the bottom rows, split between the claws); the rest is the body (the shell, the head, the
harness, the belly, the far arm).
The in-betweens (the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」,
「动画你觉得少的地方就想办法补」): every curl-up and uncurl passes through the crouch with the near arm swung forward (a
quarter turn about the shoulder, half way between hanging and the curl's raised claws); the lying death kicks its feet;
the curl's walk (c_run) steps the curl design's own feet (cut where they leave the body) instead of hopping the whole
curl.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet  # noqa: E402

HERO = "rammus"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "rammus", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def stand_col(d, rows=3):
    """The middle of the lowest `rows` rows' squares: where the design stands."""
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


# ------------------------------------------------------------------------------------------------- the side's parts
ARM_BOX = (21, 39, 17, 27)            # rows / cols the near arm lies in (the claws reach row 39)
SHOULDER = (22.5, 23.5)               # (x, y) the arm turns about
FOOT_ROW = 40                         # the feet: rows FOOT_ROW to the soles, split at FOOT_X
FOOT_X = 21
CURL_FOOT_ROW = 37                    # the curl design's feet: rows CURL_FOOT_ROW to the soles, split between the claws
CURL_FOOT_X = 26                      # (far foot up to this column, near foot right of it); laid under the rest
CURL_STRIDE = 3                       # columns each foot is ahead / behind on a step of the curl's walk


def is_skin(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return g > r + 20 and g >= b - 10


def is_claw(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return r > 200 and g > 190 and b > 110


def design():
    d = load("side.png")
    D = CutDesign(d, px=stand_col(d))
    y0, y1, x0, x1 = ARM_BOX
    arm = np.zeros((D.H, D.W), bool)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = d[y, x]
            if c[3] and (is_skin(c) or (y >= 35 and is_claw(c))):
                arm[y, x] = True
    # the arm's own outline: dark squares beside it inside the box
    box = D.box(y0, y1, x0, x1)
    dark = (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 70)
    arm |= ndimage.binary_dilation(arm, structure=R.CROSS) & dark & box
    lbl, n = ndimage.label(arm, structure=np.ones((3, 3)))
    if n > 1:
        big = 1 + int(np.argmax(ndimage.sum(arm, lbl, range(1, n + 1))))
        arm = lbl == big
    D.part("arm", arm)
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    feet = D.box(FOOT_ROW, D.H - 1, 0, D.W - 1) & ~D.parts["arm"]
    D.part("far_foot", feet & (xx <= FOOT_X))
    D.part("near_foot", feet & (xx > FOOT_X))
    D.part("body", D.rest())
    return D


TINT = {"arm": (60, 120, 255), "far_foot": (255, 220, 0), "near_foot": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


class Form:
    """The designs' layers; pose() / whole designs -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.other = {n: self.placed(load(f"{n}.png")) for n in ("idle", "ball", "curl")}
        curl = load("curl.png")
        yy, xx = np.mgrid[0:curl.shape[0], 0:curl.shape[1]]
        feet = yy >= CURL_FOOT_ROW
        cut = {"far": feet & (xx <= CURL_FOOT_X), "near": feet & (xx > CURL_FOOT_X), "rest": ~feet}
        self.curl_parts = {k: self.placed(np.where(m[..., None], curl, 0).astype(np.uint8), ref=curl)
                           for k, m in cut.items()}

    def placed(self, d, ref=None, m=0):
        """Another design in a padded layer of the side design's size, standing on the same point and ground (ref: the
        whole design a part `d` was cut from, which places it)."""
        # m：d 比 ref 四边各多出 m 格（转过的球，turned_ball 留的边），照 ref 的位置放
        ref = d if ref is None else ref
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((ref[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1) - m
        left = P + self.D.px - stand_col(ref) - m
        lay[top:top + d.shape[0], left:left + d.shape[1]] = d
        return lay

    def curl_step(self, body, near, far):
        """The curl design with its feet stepped: the far and near feet (CURL_FOOT_ROW down, split at CURL_FOOT_X)
        moved (dx, dy) each, the rest moved `body` and laid over them."""
        L = self.curl_parts
        return R.compose(self.rig, [(L["far"], dict(dx=far[0], dy=far[1])), (L["near"], dict(dx=near[0], dy=near[1])),
                                    (L["rest"], dict(dx=body[0], dy=body[1]))])

    def pose(self, crouch=0, whole=(0, 0), arm=(0, 0), arm_rot=0, feet=None, fill=True):
        """crouch: rows the body (with the arm) sets down onto the feet; whole: the whole figure; arm: the near arm
        moved, arm_rot quarter turns counter-clockwise about SHOULDER (1: pointing forward); feet: ((near dx, dy),
        (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the feet")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nx, ny), (fx, fy) = feet or ((0, 0), (0, 0))
        L = self.L
        layers = [(L["far_foot"], dict(dx=wx + fx, dy=wy + fy)), (L["near_foot"], dict(dx=wx + nx, dy=wy + ny)),
                  (L["body"], dict(dx=ux, dy=uy)),
                  (L["arm"], dict(dx=ux + arm[0], dy=uy + arm[1], rot=arm_rot, about=SHOULDER))]
        moved = arm != (0, 0) or arm_rot % 4
        # where the arm hung, the belly and harness it hid are filled from the squares round them (drawn anew: shown
        # to the user before it ships)
        can = R.compose(self.rig, layers, fill=[("arm", (ux, uy))] if moved and fill else ())
        if moved and fill:
            can = self.fill_vacated(can, ux, uy)
        return self.close_holes(can) if fill else can

    def fill_vacated(self, can, ux, uy):
        """Clear squares left inside the figure where the arm hung (ringed by outline, so fill_under cannot reach
        them): the colour of the nearest light square."""
        rig = self.rig
        allow = np.zeros(can.shape[:2], bool)
        allow[rig.oy:rig.oy + self.D.H, rig.ox:rig.ox + self.D.W] = self.D.parts["arm"]
        allow = np.roll(np.roll(allow, uy, 0), ux, 1)
        op = can[..., 3] > 0
        shut = ndimage.binary_closing(np.pad(op, 3), structure=np.ones((3, 3)), iterations=2)[3:-3, 3:-3]
        left = allow & ndimage.binary_fill_holes(shut | op) & ~op
        if not left.any():
            return can
        out = can.copy()
        rgb = can[..., :3].astype(int)
        # the belly's tan and the harness's red, not the outline nor the grey studs (they would smear)
        src = op & (rgb.sum(-1) >= 70) & ((rgb.max(-1) - rgb.min(-1)) > 50)
        _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
        out[left] = out[iy[left], ix[left]]
        return out

    def whole(self, name, dx=0, dy=0, flash=False):
        can = R.compose(self.rig, [(self.other[name], dict(dx=dx, dy=dy))])
        return R.flash(can) if flash else can

    def ball(self, k=0, dx=0, up=0, flash=False):
        """The ball turned k quarter turns counter-clockwise (k = 3: a quarter rolled to the right), on the ground
        (up rows above it), centred dx columns from the standing point."""
        can = self.whole("ball")
        if k % 4:
            can = R.lie(self.rig, can, k % 4, dx=0, sink=0)
            can = shift(can, self.ball_dx(can), 0)
        can = shift(can, dx, -up)
        return R.flash(can) if flash else can

    def ball_dx(self, can):
        """Columns that bring a turned ball's middle back onto the standing ball's middle."""
        if not hasattr(self, "_bx"):
            b = self.whole("ball")
            xs = np.nonzero(b[..., 3].any(0))[0]
            self._bx = (xs.min() + xs.max() + 1) / 2
        xs = np.nonzero(can[..., 3].any(0))[0]
        return int(round(self._bx - (xs.min() + xs.max() + 1) / 2))

    def rolled(self, deg):
        """滚球的一帧：球的设计图绕自己的重心顺时针转 deg 度（turned_ball），放在 ball() 放球的地方，所以 0 度就是 ball()、
        每帧的球心都在同一点。"""
        if not hasattr(self, "_roll"):
            b = load("ball.png")
            b[b[..., 3] == 0] = 0
            ys, xs = np.nonzero(b[..., 3] > 0)
            # 球心 = 设计图不透明格的重心（设计图的格坐标）；外框的中心偏了大半格（上面的刺比下面的长），绕它转球会晃
            self._roll = (b, magnified(b), (xs.mean() + 0.5, ys.mean() + 0.5))
        b, big, about = self._roll
        t = turned_ball(b, big, deg, about, ROLL_PAD, self.D.outline)
        return R.compose(self.rig, [(self.placed(t, ref=b, m=ROLL_PAD), {})])

    ref_holes = None
    close_holes = _Form.close_holes                   # small enclosed holes the side lacks, filled (league_wukong)
    MOST = _Form.MOST


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


# ------------------------------------------------------------------------------------------------- 滚球：小角度转
ROLL_UP = 8                           # 先放大 8 倍（Scale2x 做三次）再转
ROLL_PAD = 6                          # 转过的刺会伸出设计图的边：四边各多留 6 格


def scale2x(k):
    """Scale2x（EPX）：每格放大成 2 x 2，台阶状的斜边按上下左右的邻格补成斜线，只用原来就有的颜色。
    k：每格一个 uint32（RGBA 四个字节当一个数比较）。"""
    p = np.pad(k, 1, mode="edge")
    a, d, c, b = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]       # 上、下、左、右
    out = np.empty((2 * k.shape[0], 2 * k.shape[1]), np.uint32)
    out[0::2, 0::2] = np.where((c == a) & (c != d) & (a != b), a, k)
    out[0::2, 1::2] = np.where((a == b) & (a != c) & (b != d), b, k)
    out[1::2, 0::2] = np.where((d == c) & (d != b) & (c != a), c, k)
    out[1::2, 1::2] = np.where((b == d) & (b != a) & (d != c), d, k)
    return out


def magnified(d):
    """设计图放大 ROLL_UP 倍（Scale2x 反复做），外面先垫两格透明（边上的格也有邻格）。-> 每格一个 uint32。"""
    k = np.ascontiguousarray(np.pad(d, ((2, 2), (2, 2), (0, 0)))).view(np.uint32)[..., 0]
    for _ in range(int(round(math.log2(ROLL_UP)))):
        k = scale2x(k)
    return k


def turned_ball(d, big, deg, about, m, outline):
    """设计图 d 绕 about（d 的格坐标）顺时针转 deg 度，四边各多留 m 格。像素画的转法（RotSprite 一类）：放大 8 倍的图
    （magnified，斜边已经磨平）最近邻地转，再按格取回——每格取它的中心转回去落在放大图里的那一小格的颜色。只转不缩放，
    不出新颜色。转完露在外面的浅色格（描边在那儿断了）原地涂成描边色：描边补上，轮廓不往外长。0 度原样返回。"""
    if deg % 360 == 0:
        return np.pad(d, ((m, m), (m, m), (0, 0)))
    H, W = d.shape[:2]
    cx, cy = about
    t = math.radians(deg)
    co, si = math.cos(t), math.sin(t)
    yy, xx = np.mgrid[0:H + 2 * m, 0:W + 2 * m]
    dx, dy = xx + 0.5 - m - cx, yy + 0.5 - m - cy
    # 屏幕上 y 朝下：转回去（逆时针 deg 度）找它在设计图里的点；+2 是 magnified 垫的两格
    sx = (cx + co * dx + si * dy + 2) * ROLL_UP
    sy = (cy - si * dx + co * dy + 2) * ROLL_UP
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    ok = (ix >= 0) & (iy >= 0) & (ix < big.shape[1]) & (iy < big.shape[0])
    k = np.zeros(xx.shape, np.uint32)
    k[ok] = big[iy[ok], ix[ok]]
    out = k.view(np.uint8).reshape(k.shape + (4,)).copy()
    op = out[..., 3] > 0
    lbl, _ = ndimage.label(~op)
    edge = set(np.r_[lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]].tolist()) - {0}
    outside = np.isin(lbl, list(edge))
    gap = op & (R.G.lum(out[..., :3]) >= 70) & ndimage.binary_dilation(outside, structure=R.CROSS)
    out[gap, :3] = outline
    return out


def form():
    return Form(design(), rig_pad=(40, 40, 50, 20))


def tries(F):
    p = F.pose
    return [p(), p(arm_rot=1, arm=(0, 8)), p(arm_rot=3, arm=(-1, 4)), p(crouch=2), F.whole("idle"),
            F.whole("curl"), F.ball(), F.ball(3)]


# ------------------------------------------------------------------------------------------------- the actions
FWD = dict(arm_rot=1, arm=(0, 8))     # the near arm swung forward, level under his face (never across it)
BACK = dict(arm_rot=3, arm=(-1, 6))   # the near arm drawn back, level behind the belly
DEAD_KICK = 3                         # columns the lying death's feet kick to either side
# 滚球（b_run：附加包滚着走时播；skill_roll：主包 Q 冲刺时播）：球每帧顺时针转 ROLL_STEP 度，ROLL_N 帧转一整圈。
# 刺大约 45 度一根，以前一帧转 90 度，转完和上一帧几乎一样，局内看着是原地闪的球（2026-11-21 用户：「Q技能目前看起来不会
# 在局内滚动」）；一帧转 15 度是刺间距的三分之一，看得出往哪边滚。
# 转速照他在地上滚的速度、不打滑（滚一圈走过的路 = 周长）：一个游戏像素 = 1000 单位（addons/league_dragons/src/world.rs
# UNITS_PER_PX），附加包日志里一次滚了 69 tick、91390 单位 = 每 tick 1.32 游戏像素；球身（不算刺）半径约 18.4 格 = 15.3
# 游戏像素（PPU 1.2，hd.rs 没有他的 SIZES），周长 96 游戏像素，1.21 秒一圈 -> 每帧 50 毫秒（24 帧 1.2 秒）。50 毫秒也是
# 一帧最短的时长：日志里别的几次滚得更快（每 tick 1500-2100 单位），主包 Q 冲刺每 tick 4000，照理还要转得更快，都取 1.2 秒
ROLL_STEP = 15
ROLL_N = 360 // ROLL_STEP
ROLL_MS = 50

# ms per frame; the kit's ticks (tools/kit/build_rammus.py) come from these. The in-betweens (2026-11-14) keep every
# action's length and the ticks the kit reads: Q still curls in 200 (now 4 x 50: crouch, arm forward, curl, ball), E
# still rears up at 70 (the rearing curl's 100 now 50 + the arm-forward crouch 50 on the way down), W still 267, the
# uncurls (skill_hit, ult_land) still 233 with the ball's 80 first
# （skill_roll 在技能数据里是 anim("skill_roll", q_roll) 握着放到撞上为止，不按帧数计时，帧数可以变）
MS = {"idle": [150] * 8, "run": [100] * 8, "attack": [90, 90, 60, 80, 80, 100],
      "skill": [50, 50, 50, 50], "skill_roll": [ROLL_MS] * ROLL_N, "skill_hit": [80, 50, 50, 53],
      "skill2": [70, 70, 50, 50, 93], "skill_w": [80, 60, 127],
      "ult": [100, 100, 100, 100, 100, 100], "ult_land": [80, 50, 50, 53],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500],
      "b_idle": [200, 200], "b_run": [ROLL_MS] * ROLL_N, "b_hit": [100, 100],
      "c_idle": [300, 300], "c_run": [100] * 4, "c_hit": [100, 100]}
IDLE_LEG_ROW = 35                     # the idle design's legs: rows from here down stay while the body breathes


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle (League's rammus_idle1: he breathes under the shell): the 3/4 design's body sets down a row onto its legs
    idle = F.other["idle"]
    legs = idle.copy()
    top = idle.copy()
    ys = np.nonzero(idle[..., 3].any(1))[0]
    cut_row = ys.max() + 1 - (F.D.ground - IDLE_LEG_ROW)
    legs[:cut_row] = 0
    top[cut_row:] = 0

    def breathe(c):
        return R.compose(rig, [(legs, dict(dy=0)), (top, dict(dy=c))])
    out["idle"] = [breathe(c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # auto attack (League's rammus_attack1: he tucks in and throws himself forward head over heels, the shell slamming
    # into the target, and lands back on his feet; the user: 「普攻和英雄联盟不一样吧？」 - it was an arm swipe): crouched,
    # the whole figure a quarter turn forward (clockwise) in the air, upside down on the target (the blow, frame 3),
    # three quarters round, back on his feet, standing
    def tumble(k, dx, up):
        return shift(R.lie(rig, p(), k, dx=dx, sink=0), 0, -up)
    out["attack"] = [p(crouch=2, whole=(-1, 0)), tumble(3, 3, 4), tumble(2, 6, 3), tumble(1, 5, 1), p(whole=(2, 0)),
                     p()]
    # Q Powerball (League's rammus_spell1_windup: he tucks in and curls up into the ball): crouched, the near arm swung
    # forward on its way up (the in-between, 2026-11-14), curled, the ball
    out["skill"] = [p(crouch=2), p(crouch=2, **FWD), F.whole("curl"), F.ball()]
    # 滚球：每帧顺时针转 ROLL_STEP 度（往右滚；朝左时游戏整张镜像），第 0 帧就是上一帧的球（ball()），接得上
    roll = [F.rolled(ROLL_STEP * i) for i in range(ROLL_N)]
    out["skill_roll"] = roll
    # the hit: the ball bounces back off the target, he uncurls (the arm coming down through forward), standing
    out["skill_hit"] = [F.ball(3, dx=-2, up=4), F.whole("curl", dx=-1), p(crouch=2, whole=(-1, 0), **FWD),
                        p(whole=(-1, 0))]
    # E Frenzying Taunt (League's rammus_spell3: he rears up with his claws raised): crouched, reared up in the curl's
    # raised arms (the taunt, frame 2), higher, the arm coming down through forward, down
    out["skill2"] = [p(crouch=2), F.whole("curl", dy=-2), F.whole("curl", dy=-3), p(crouch=2, **FWD), p()]
    # W Defensive Ball Curl (League's Rammus_channel): crouched, the arm swung forward, curled and held (the add-on's
    # c_idle goes on from it)
    out["skill_w"] = [p(crouch=2), p(crouch=2, **FWD), F.whole("curl")]
    # R Soaring Slam (League's Spell4_Jump: he curls up, leaps high as the ball and comes down on them)
    out["ult"] = [p(crouch=2), F.whole("curl"), F.ball(0, up=6), F.ball(3, up=12), F.ball(2, up=16),
                  F.ball(1, up=10)]
    out["ult_land"] = [F.ball(0), F.whole("curl"), p(crouch=2, **FWD), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]

    # the death (League's rammus_death: he topples back onto his shell, belly up): staggering, crouched, falling back
    # (a quarter turn), on his back (half a turn, the spikes in the ground), a bounce, his feet kicking in the air both
    # ways (whole squares sideways: the in-betweens, 2026-11-14 - before, the same lying picture three times), lying
    def lying(k, sink, dx, feet=None):
        return R.lie(rig, p(fill=True, feet=feet), k, dx=dx, sink=sink)
    kick = DEAD_KICK
    out["dead"] = [p(whole=(-1, 0)), p(crouch=2, whole=(-2, 0)), lying(1, 0, -4), lying(2, 8, -5), lying(2, 6, -5),
                   lying(2, 8, -5, feet=((kick, 0), (-kick, 0))), lying(2, 8, -5, feet=((-kick, 0), (kick, 0))),
                   lying(2, 8, -5)]
    # the add-on's forms (addons/league_rammus): the ball standing / rolling / hit, the curl standing / walking / hit
    out["b_idle"] = [F.ball(), F.ball()]
    out["b_run"] = list(roll)                       # 和主包 Q 的滚球同一套帧
    out["b_hit"] = [F.ball(dx=-2, flash=True), F.ball(dx=-1)]
    out["c_idle"] = [F.whole("curl"), F.whole("curl")]
    # the curl's walk: the curl rocking as before (up a row and a column forward / back on the passing frames), its
    # own feet stepping under it (2026-11-14; it was the whole curl hopping, one picture): the near foot ahead and the
    # far one behind, passing (the far one lifted a row), the other way round, passing (the near one lifted); a planted
    # foot goes up with the rock as the whole curl did, so the bottom row moves as before
    s = CURL_STRIDE
    out["c_run"] = [F.curl_step((0, 0), (s, 0), (-s, 0)), F.curl_step((1, -1), (0, -1), (1, -2)),
                    F.curl_step((0, 0), (-s, 0), (s, 0)), F.curl_step((-1, -1), (-1, -2), (0, -1))]
    out["c_hit"] = [F.whole("curl", dx=-2, flash=True), F.whole("curl", dx=-1)]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# League's rammus_run: a waddle under the shell. The design's own feet step whole under the body that stays (each
# planted and sliding back, then lifted and carried forward, the far one half a cycle later), the body set down a row
# on each contact (league_wukong's walk).
from rig_wukong import _steps  # noqa: E402

WALK_STEP = dict(_steps(2, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    for (ndx, nup), (fdx, fup), bob, up_ in zip(st["near"], st["far"], st["bob"], st["rise"]):
        out.append(F.pose(whole=(0, bob - up_), feet=((ndx, -nup), (fdx, -fup))))
    return out


def biggest(F, fr):
    """一个动作所有帧里最大的 1x 半宽、半高（ppu_rig.Rig.export 的算法）。滚球每帧转出来的刺伸得不一样远，帧有大有小，
    按中心对准站的点画时会差半格、球心一帧一帧地晃：都按最大那帧切（Rig.least），也就是 ball() 那张的大小。"""
    rig = F.rig
    px, py = float(rig.CX), rig.GY - R.FEET * PPU
    hw = hh = 0
    for can, _ in fr:
        ys, xs = np.nonzero(rig.finish(can)[..., 3] > 0)
        hw = max(hw, int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5)))
        hh = max(hh, int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5)))
    return hw, hh


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": walk(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if not (a.audit or a.review or a.parts):
        F = form()
        acts = frames(F)
        F.rig.least = {t: biggest(F, acts[t]) for t in ("skill_roll", "b_run")}
        F.rig.export(acts)
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            import rig_wukong as RW
            RW.HERO = HERO
            RW.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)
    F = form()
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()
