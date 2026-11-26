#!/usr/bin/env python3
"""亚当 Codex 照动画第一季重画的身体帧（assets/source/adam/rebuild）的修整：一个头、接好脖子、蓝眼睛、指虎一样大。

    python tools/art/adam_rebuild_fix.py            # 读 rebuild/codex/ 的原样，写 rebuild/ragnarok_adam_native#sheet.png
    python tools/art/adam_rebuild_fix.py --check    # 和现在的 rebuild/ 不一样就退出 1
    然后 tools/art/import_adam.py、ppu_hd.py --hero adam、hero_reels.py --hero adam

Codex 交的原样（2026-11-21，64 帧的哈希和 rebuild/checks.csv 对得上）放在 rebuild/codex/，这里只读它，不改它。
Codex 说每帧都用了同一个头（rebuild/head_master.png），实际上只有待机第 1 帧是，其余 63 帧的头都是各画各的：
头发轮廓、呆毛、脸型逐帧在变（和第 1 帧比，同一位置的像素有 66-83% 不一样），动起来就是用户说的脸和模型在变形；
受击第 3-5 帧往后仰的头和肩膀之间空着一道缝（透明的），脖子没接上。所以：

1. 头：每帧把 head_master 贴到 Codex 那帧头的位置（POSE：逐帧拿 head_master 去对 Codex 的头量出来的位置和角度），
   旧头清掉（连成一片的旧头发整块清，脸前面、下巴底下伸出来的旧脸也清）。角度只在头真歪的时候用（受击后仰、
   神虚视低头、倒地），相邻帧差不多的用同一个角度，其余都是 0 度，也就是和待机第 1 帧一模一样的像素。
   转角度用 RotSprite 的做法（Scale2x 放大 8 倍、转、取格子中心），不出新颜色。
2. 脖子：头下面的脖子从 head_master 自己的脖子往下接到身子（只补透明的地方，身子画在前面的不动），边上描边；
   身子顶上原来对着空缝的那道描边换成脖子的颜色，免得脖子底下横一道黑线像领子。
3. 眼睛：head_master 的眼睛是一道深色睫毛下面一点暗青，游戏里看着像一条黑带；换成白眼底 + 蓝眼珠
   （用户要的「蓝眼」），睫毛不动。倒地第 3 帧起闭眼（只留睫毛那一道）。
4. 指虎：技能二、大招里 Codex 画成一整块深灰铁块，比别的动作的大一倍，也没有指环；换成普攻等动作里
   方向最接近的那块（原样的像素，三个亮环），铁块多出来的地方用拳头旁边的皮肤颜色补上，挨着透明的补描边。
5. 收色：整张图收到 64 色（snap_palette），不然 lo_（选人、百科）和 1 倍帧的颜色全乱。
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DIR = os.path.join(ROOT, "assets", "source", "adam", "rebuild")
CODEX = os.path.join(DIR, "codex", "ragnarok_adam_native")      # Codex 交的原样
OUT = os.path.join(DIR, "ragnarok_adam_native")
MASTER = os.path.join(DIR, "head_master.png")
ACTS = ("idle", "run", "attack", "hit", "skill", "skill2", "ult", "dead")
CELL = 256
MC = (15.5, 17.0)          # head_master 上转角度的中心
CW = 60                    # 转出来的头放在 60x60 的格子里，格子中心对准 POSE 的位置
OUTLINE = np.array([0x66, 0x45, 0x3E, 255], np.uint8)    # 身子的描边色（补脖子边用）
FIST_LINE = np.array([0x5E, 0x3A, 0x36], np.uint8)       # 拳头的描边色（补指虎边用）

# 每帧头的（角度，格子中心 x，y）：角度为正是往后仰（脸朝上），为负是低头
POSE = {
    "idle": [(0, 130, 141), (0, 129, 140), (0, 131, 140), (0, 131, 139), (0, 129, 139), (0, 130, 141), (0, 129, 142), (0, 128, 141)],
    "run": [(0, 145, 143), (0, 142, 143), (0, 143, 144), (0, 142, 142), (0, 137, 144), (0, 136, 143), (0, 132, 143), (0, 142, 142)],
    "attack": [(0, 132, 140), (0, 134, 141), (0, 137, 144), (0, 142, 143), (0, 140, 144), (0, 134, 142), (0, 132, 141), (0, 130, 141)],
    "hit": [(0, 130, 138), (20, 113, 140), (30, 119, 140), (30, 118, 137), (40, 111, 142), (10, 122, 143), (0, 123, 141), (0, 128, 141)],
    "skill": [(0, 133, 138), (0, 133, 144), (-7.5, 122, 149), (-15, 128, 156), (-7.5, 130, 152), (-7.5, 126, 145), (0, 122, 142), (0, 127, 142)],
    "skill2": [(0, 132, 143), (0, 129, 142), (0, 128, 141), (0, 132, 144), (0, 134, 143), (0, 132, 142), (0, 127, 140), (0, 131, 140)],
    "ult": [(0, 131, 140), (10, 127, 142), (-10, 132, 147), (-10, 135, 152), (0, 144, 150), (0, 140, 147), (0, 130, 145), (0, 132, 142)],
    "dead": [(0, 132, 136), (-7.5, 132, 146), (-15, 144, 163), (-20, 142, 173), (-15, 134, 175), (-15, 145, 182), (-25, 153, 192), (-50, 184, 207)],
}
# 个别帧的设置：倒地第 3 帧起闭眼；最后一帧脸趴在小臂上，小臂和肩膀不清，不接脖子
SPEC = {("dead", f): {"eyes": "closed"} for f in range(2, 7)}
SPEC[("dead", 7)] = {"eyes": "closed", "neck": False, "noclear": [(140, 219, 205, 235), (140, 190, 166, 235)]}
# 指虎：出拳那几帧用普攻出拳的指虎（侧面看三个环），别的按方向自动挑
DUSTER_FROM = {("skill2", 3): ("attack", 3), ("skill2", 4): ("attack", 4), ("ult", 4): ("attack", 3), ("ult", 5): ("attack", 4)}


def hx(s):
    return [int(s[i:i + 2], 16) for i in (0, 2, 4)]


def cell(sheet, act, f):
    r = ACTS.index(act)
    return sheet[r * CELL:(r + 1) * CELL, f * CELL:(f + 1) * CELL]


def lum(px):
    return 0.299 * px[..., 0].astype(float) + 0.587 * px[..., 1] + 0.114 * px[..., 2]


def edge4(al):
    """挨着透明（上下左右）的位置"""
    nb = np.zeros_like(al)
    nb[1:] |= ~al[:-1]
    nb[:-1] |= ~al[1:]
    nb[:, 1:] |= ~al[:, :-1]
    nb[:, :-1] |= ~al[:, 1:]
    return nb


# ---------- 头 ----------

def master(eyes):
    """head_master 换眼睛：open 白眼底蓝眼珠，closed 闭眼（眼底眼珠换成脸色，只留睫毛）"""
    M = np.asarray(Image.open(MASTER).convert("RGBA")).copy()

    def put(x, y, c):
        M[y, x, :3] = hx(c)
        M[y, x, 3] = 255
    if eyes == "open":
        put(18, 23, "e6e3ec"), put(19, 23, "d2d0dc"), put(20, 23, "4a8fd2"), put(21, 23, "13243f")
        put(20, 24, "8cc4ec"), put(21, 24, "3f7fc0")
    else:
        for x, c in ((18, "f3cbbd"), (19, "f6cfc3"), (20, "f4c9bc"), (21, "eec3b5")):
            put(x, 23, c)
        put(20, 24, "f2c6b8"), put(21, 24, "f0c8bc")
    return M


def labels(M):
    """1 头，2 下巴底下那一截脖子（下颌那道暗线左下边）"""
    H, W = M.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    op = M[..., 3] > 0
    lab = np.zeros((H, W), np.uint8)
    lab[op] = 1
    lab[op & (xx <= 18) & (yy >= 28) & (yy - 27 > (xx - 12) * 5 / 6)] = 2
    return lab


def scale2x(a):
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    E, B, D, F, H = p[1:-1, 1:-1], p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1]

    def eq(x, y):
        return np.all(x == y, axis=-1)
    out = np.zeros((2 * a.shape[0], 2 * a.shape[1], a.shape[2]), a.dtype)
    out[0::2, 0::2] = np.where((eq(D, B) & ~eq(B, F) & ~eq(D, H))[..., None], D, E)
    out[0::2, 1::2] = np.where((eq(B, F) & ~eq(B, D) & ~eq(F, H))[..., None], F, E)
    out[1::2, 0::2] = np.where((eq(D, H) & ~eq(D, B) & ~eq(H, F))[..., None], D, E)
    out[1::2, 1::2] = np.where((eq(H, F) & ~eq(D, H) & ~eq(B, F))[..., None], F, E)
    return out


def rotate(a, deg):
    """RotSprite：Scale2x 三次放大 8 倍，按角度取最近的那格（屏幕上逆时针为正），放进 CW x CW、MC 在中心"""
    big = scale2x(scale2x(scale2x(a)))
    H, W = a.shape[:2]
    t = np.deg2rad(deg)
    c, s = np.cos(t), np.sin(t)
    ys, xs = np.mgrid[0:CW, 0:CW]
    u, v = xs + 0.5 - CW / 2, ys + 0.5 - CW / 2
    bx = np.floor((c * u - s * v + MC[0]) * 8).astype(int)
    by = np.floor((s * u + c * v + MC[1]) * 8).astype(int)
    ok = (bx >= 0) & (by >= 0) & (bx < W * 8) & (by < H * 8)
    out = np.zeros((CW, CW, a.shape[2]), a.dtype)
    out[ok] = big[by[ok], bx[ok]]
    return out


def to_master(deg, cx, cy, xs, ys):
    """帧里的位置 -> head_master 上的位置"""
    t = np.deg2rad(deg)
    c, s = np.cos(t), np.sin(t)
    u, v = xs - cx + 0.5, ys - cy + 0.5
    return c * u - s * v + MC[0], s * u + c * v + MC[1]


def to_frame(deg, cx, cy, mx, my):
    t = np.deg2rad(deg)
    c, s = np.cos(t), np.sin(t)
    a, b = mx - MC[0], my - MC[1]
    return c * a + s * b + cx - 0.5, -s * a + c * b + cy - 0.5


def kinds(px):
    """粗分：0 透明，1 深色（描边），2 头发，3 皮肤，4 眼睛的蓝，5 其他"""
    r, g, b, a = [px[..., i].astype(int) for i in range(4)]
    L = lum(px)
    out = np.zeros(r.shape, np.int8)
    o = a > 0
    out[o] = 5
    out[o & (L < 80)] = 1
    skin = o & (L >= 80) & (r - g >= 28) & (r - b >= 28)
    hair = o & (L >= 80) & ~skin & (r >= g - 4) & (g - b >= 10)
    out[skin] = 3
    out[hair] = 2
    out[o & (b >= r + 8) & (L >= 40)] = 4
    return out


def neck_colours(M):
    """head_master 脖子最下面一行每列的颜色，往下接脖子就照着它"""
    cols = {}
    for x in range(10, 20):
        for y in (32, 31, 30):
            if M[y, x, 3] > 0:
                cols[x] = M[y, x].copy()
                break
    return cols


def place_head(frame, deg, cx, cy, eyes="open", neck=True, noclear=()):
    M = master(eyes)
    img, lab = rotate(M, deg), rotate(np.dstack([labels(M)] * 3 + [(M[..., 3] > 0) * 255]).astype(np.uint8), deg)[..., 0]
    F = frame.copy()
    head = np.zeros(F.shape[:2], bool)
    stub = np.zeros(F.shape[:2], bool)
    NEW = np.zeros_like(F)
    ys, xs = np.nonzero(lab > 0)
    fx, fy = xs + cx - CW // 2, ys + cy - CW // 2
    ok = (fx >= 0) & (fy >= 0) & (fx < CELL) & (fy < CELL)
    NEW[fy[ok], fx[ok]] = img[ys[ok], xs[ok]]
    head[fy[ok], fx[ok]] = lab[ys[ok], xs[ok]] == 1
    stub[fy[ok], fx[ok]] = lab[ys[ok], xs[ok]] == 2
    gy, gx = np.mgrid[0:CELL, 0:CELL]
    mx, my = to_master(deg, cx, cy, gx, gy)
    above = my < 30                                        # 下巴以上（head_master 上量）
    k = kinds(F)
    dist = ndimage.distance_transform_edt(~head)
    # 旧头发（头发色、挨着头发的深色描边、旧眼睛）：碰到新头的那几片整片清（26 格以内），其余 12 格以内清
    hair = k == 2
    hairish = hair | ((k == 1) & ndimage.binary_dilation(hair, iterations=2)) | (k == 4)
    clear = hairish & (dist <= 12) & above
    lab_h, n = ndimage.label(hairish, np.ones((3, 3)))
    if n:
        touch = np.unique(lab_h[(dist <= 6) & hairish])
        clear |= np.isin(lab_h, touch[touch > 0]) & (dist <= 26) & above
    # 旧脸：新头边上 3 格以内、耳朵往前的；脸前面和下巴底下伸出来的一条不管什么颜色都清
    clear |= (k > 0) & (dist <= 3) & above & (mx >= 12)
    clear |= (k > 0) & (((mx >= 24) & (mx <= 27.5) & (my >= 12) & (my <= 30)) |
                        ((mx >= 20.5) & (mx <= 27.5) & (my >= 28) & (my <= 32.5)))
    for x0, y0, x1, y1 in noclear:
        clear[y0:y1, x0:x1] = False
    F[clear] = 0
    pasted = head | stub
    F[pasted] = NEW[pasted]
    if neck:
        cols = neck_colours(M)
        filled = np.zeros_like(head)
        Ys = np.arange(30.0, 32.0 + 16, 0.25)
        for X in np.arange(10.25, 19.0, 0.25):
            col = cols.get(int(np.floor(X)))
            if col is None:
                continue
            side = X < 11.0 or X >= 18.0
            for i, Y in enumerate(Ys):
                px, py = (int(np.floor(v + 0.5)) for v in to_frame(deg, cx, cy, X, Y))
                if not (0 <= px < CELL and 0 <= py < CELL):
                    break
                if pasted[py, px] or filled[py, px]:
                    continue
                if F[py, px, 3] == 0:                       # 头和身子之间空着：补脖子
                    F[py, px] = OUTLINE if side else col
                    filled[py, px] = True
                    continue
                if Y <= 32.0:
                    continue
                # 接到身子了：身子顶上原来对着空缝的那道描边（最多 3 格）换成脖子的颜色
                if 11.5 <= X <= 17.5:
                    seen = []
                    for Y2 in Ys[i:i + 16]:
                        q = tuple(int(np.floor(v + 0.5)) for v in to_frame(deg, cx, cy, X, Y2))
                        if q in seen:
                            continue
                        seen.append(q)
                        qx, qy = q
                        if not (0 <= qx < CELL and 0 <= qy < CELL) or F[qy, qx, 3] == 0:
                            break
                        if lum(F[qy, qx]) < 150 and len(seen) <= 3:
                            F[qy, qx] = col
                            filled[qy, qx] = True
                        else:
                            break
                break
        al = F[..., 3] > 0
        F[(filled | stub) & al & edge4(al)] = OUTLINE        # 脖子挨着透明的一圈描边
    # 头附近和身子不连着的碎块（旧头发的尖）去掉
    al = F[..., 3] > 0
    near = ndimage.distance_transform_edt(~pasted) <= 26
    lab_o, n = ndimage.label(al, np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(al, lab_o, range(1, n + 1))
        for i, size in enumerate(sizes, 1):
            m = lab_o == i
            if size < 24 and (near & m).any():
                F[m] = 0
    # 清旧头时在脖子、下巴边上漏出来的小洞（原来没有的）用旁边最近的皮肤色补上
    al = F[..., 3] > 0
    was = frame[..., 3] > 0
    holes = ndimage.binary_fill_holes(al) & ~al & ~(ndimage.binary_fill_holes(was) & ~was) & near
    if holes.any():
        light = al & (lum(F) >= 120)
        _, (iy, ix) = ndimage.distance_transform_edt(~light, return_indices=True)
        F[holes] = F[iy[holes], ix[holes]]
    return F


# ---------- 指虎 ----------

def metal(c):
    r, g, b = [c[..., i].astype(int) for i in range(3)]
    return (c[..., 3] > 0) & (np.abs(r - g) < 16) & (np.abs(g - b) < 16) & (np.abs(r - b) < 22) & (lum(c) > 55)


def duster(c):
    """最大那块金属：(遮罩, 中心, 长边方向的角度)"""
    m = metal(c)
    lab, n = ndimage.label(m, np.ones((3, 3)))
    if not n:
        return None
    k = int(np.argmax(ndimage.sum(m, lab, range(1, n + 1)))) + 1
    s = lab == k
    ys, xs = np.nonzero(s)
    P = np.stack([xs - xs.mean(), ys - ys.mean()], 1)
    u = np.linalg.eigh(P.T @ P)[1][:, 1]
    return s, (xs.mean(), ys.mean()), np.degrees(np.arctan2(u[1], u[0])) % 180


def swap_duster(T, sheet, pick=None):
    """T 里那块大铁块换成 sheet 里方向最接近的那块指虎（只在待机、跑、普攻、受击、神虚视里找；pick 指定就用它）"""
    T = T.copy()
    got = duster(T)
    if got is None:
        return T, None
    slab, (cx, cy), ang = got
    best = None
    for a in ("idle", "attack", "hit", "run", "skill"):
        for f in range(8):
            if pick and (a, f) != pick:
                continue
            s = duster(cell(sheet, a, f))
            if s is None:
                continue
            d = min(abs(ang - s[2]), 180 - abs(ang - s[2]))
            if best is None or d < best[0]:
                best = (d, a, f, s)
    _, a, f, (m2, (x2, y2), _) = best
    S = cell(sheet, a, f)
    al = T[..., 3] > 0
    r, g, b = [T[..., i].astype(int) for i in range(3)]
    sat = np.maximum(np.maximum(np.abs(r - g), np.abs(g - b)), np.abs(r - b))
    grey = al & (sat < 24) & (lum(T) > 30)
    big = slab.copy()
    for _ in range(2):                                     # 铁块边上暗一点的灰也算
        big |= ndimage.binary_dilation(big) & grey
    skin = al & ~grey & (lum(T) > 120) & (r - b > 25)
    _, (iy, ix) = ndimage.distance_transform_edt(~skin, return_indices=True)
    nb = edge4(al)
    fill = big & ~nb
    T[fill, :3] = T[iy[fill], ix[fill], :3]               # 铁块的地方先接上旁边拳头的颜色
    T[big & nb, :3] = FIST_LINE
    ys, xs = np.nonzero(m2)
    box = np.zeros_like(m2)
    box[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    ys, xs = np.nonzero(box & metal(S))                    # 源指虎连同亮环之间的暗线
    dx, dy = int(round(cx - x2)), int(round(cy - y2))
    tx, ty = xs + dx, ys + dy
    ok = (tx >= 0) & (ty >= 0) & (tx < CELL) & (ty < CELL)
    ok[ok] &= al[ty[ok], tx[ok]]
    T[ty[ok], tx[ok]] = S[ys[ok], xs[ok]]
    return T, (a, f)


# ---------- 收色 ----------

EYE_COLOURS = ("e6e3ec", "d2d0dc", "4a8fd2", "13243f", "8cc4ec", "3f7fc0")   # master(open) 新画的眼睛，原样留着


def median_cut(cols, n):
    q = Image.fromarray(cols.reshape(1, -1, 3).astype(np.uint8)).quantize(
        colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:3 * n]).reshape(-1, 3)
    return pal[np.unique(np.asarray(q).ravel())]


def snap_palette(sheet, rest=52, grey=6):
    """整张图收到 64 色：指虎的灰单独 6 色、新画的眼睛 6 色原样、其余 52 色（都是中位切分，不抖动）。
    Codex 这版是缩小的手绘，8 万多种颜色；ppu_hd.py 出 lo_（选人、百科、BP 用的）和 ragnarok_art.py 出 1 倍帧都拿
    「这一帧最常见的 64 / 96 种颜色」当调色板，颜色一散，挑出来的全是皮肤色，绿短裤成了棕的、有几帧整个人一片粉。
    收到 64 色以后 3 倍看和原来几乎一样，每帧的颜色都在调色板里。"""
    out = sheet.copy()
    c = sheet[..., :3].astype(int)
    op = sheet[..., 3] > 0
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    sat = np.maximum(np.maximum(np.abs(r - g), np.abs(g - b)), np.abs(r - b))
    eye = np.zeros(op.shape, bool)
    for s in EYE_COLOURS:
        eye |= (c == hx(s)).all(-1)
    metal_px = op & ~eye & (sat < 24) & (lum(sheet) > 55)
    rest_px = op & ~eye & ~metal_px
    for mask, n in ((metal_px, grey), (rest_px, rest)):
        pal = median_cut(c[mask], n)
        cols = c[mask]
        snapped = np.empty_like(cols)
        for i in range(0, len(cols), 20000):        # 分块算最近的颜色，省内存
            d = ((cols[i:i + 20000, None, :] - pal[None]) ** 2).sum(-1)
            snapped[i:i + 20000] = pal[np.argmin(d, 1)]
        out[mask, :3] = snapped
    return out


def build():
    src = np.asarray(Image.open(CODEX + "#sheet.png").convert("RGBA"))
    sheet = src.copy()
    for r, act in enumerate(ACTS):
        for f in range(8):
            deg, cx, cy = POSE[act][f]
            sheet[r * CELL:(r + 1) * CELL, f * CELL:(f + 1) * CELL] = place_head(cell(src, act, f), deg, cx, cy,
                                                                               **SPEC.get((act, f), {}))
    heads = sheet.copy()
    picks = {}
    for act in ("skill2", "ult"):
        r = ACTS.index(act)
        for f in range(8):
            T, picks[(act, f)] = swap_duster(cell(heads, act, f), heads, DUSTER_FROM.get((act, f)))
            sheet[r * CELL:(r + 1) * CELL, f * CELL:(f + 1) * CELL] = T
    return snap_palette(sheet), picks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sheet, picks = build()
    if a.check:
        same = os.path.isfile(OUT + "#sheet.png") and np.array_equal(
            np.asarray(Image.open(OUT + "#sheet.png").convert("RGBA")), sheet)
        with open(CODEX + "#anim.fanim", "rb") as f1, open(OUT + "#anim.fanim", "rb") as f2:
            same = same and f1.read() == f2.read()
        if not same:
            print(f"{OUT}#sheet.png: differs")
        sys.exit(0 if same else 1)
    Image.fromarray(sheet).save(OUT + "#sheet.png")
    shutil.copyfile(CODEX + "#anim.fanim", OUT + "#anim.fanim")
    print(f"{OUT}#sheet.png written")
    for (act, f), src in picks.items():
        print(f"  {act} {f + 1}: 指虎取自 {src[0]} {src[1] + 1}")


if __name__ == "__main__":
    main()
