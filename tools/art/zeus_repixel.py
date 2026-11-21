#!/usr/bin/env python3
"""宙斯的像素图照 Codex 的原画按两倍密度重出：抠图和定位用 Codex 自己的 build_assets.py，取样和清理用
tools/art/ragnarok_repixel.py（亚当先这么做的，见 tools/art/adam_repixel.py）。

    python tools/art/zeus_repixel.py [--check] [--up 2] [--out-dir 文件夹]

为什么：亚当按两倍密度重出、用户看过以后，终末包四个英雄都这么出。Codex 的 build_assets.py 把 250-500 像素高的原画
按每种身体的站高（老人 51 格、膨胀 67 格、阿陀磨须 59 格）用最近邻缩进 128 格，每 4、5 个原画像素只取一个：描边断断续续，
皮肤、白袍上全是杂色点，眼睛的金色多半丢了。

做法：
- 位置：跑一遍 Codex 的 actor_forms / transition_frames，把它每帧调 render_actor 的参数（原画格、缩放、轴心、脚底行，
  还有它为了不出格做的横向平移）记下来，原画里对应的还是那一块，缩放乘 2。所以每帧和 Codex 的 128 格那帧放大两倍是
  同一个位置、同样大小（「模型不要变大变小」）。
- 切掉的拳头、脚接回来：Codex 按格子切原画，伸出格子的部分丢了（三种身体时间之拳打出那帧的拳头、膨胀普攻第 5 帧的
  拳头、倒地最后几帧的脚）。格子外和身体连着的像素接回来，位置、大小不动。
- 颜色：Codex 先把原画的颜色换成它定的 22 色（actor_colors；跑步的原画本来就是换过的颜色），这里也先换，部位就按这
  22 色分：深色线条、皮肤、白（白袍、头发、胡子和它们的蓝灰阴影）、金（眼睛、胡子上的珠子和它的暗红）。只改一处：
  白袍、头发阴影里的冷灰被它就近换成了皮肤色（白袍上一个个褐点），这种换成最近的白。三种身体和变身共用这套颜色。
- 描边：皮肤深红褐、白袍深蓝灰，都是 Codex 那 22 色里同色系最深的那档，不是一圈近黑。
- 脸：眼睛只有两三个原画像素，金色占到一点就留成金点，眼窝留近黑；别处的深色线（肌肉、脖子、头的轮廓）都换成所在
  部位最暗的那档（亚当那次：「身体上还是不干净啊」）。白袍上、袍子和头发边上零星的皮肤色，皮肤上零星的白点并进旁边，
  脸上不动。
- 变身三段的头尾两帧直接用两种身体待机的第一帧（和 Codex 一样，切换时接得上）。
- 特效照两倍用 Codex 自己的 isolated_fx / fixed_palette 出（原画格缩成 78 格那一步改成 78 x 2），身体和特效一样细。

ragnarok_repixel.py 没改：取样、清杂点、描边用它的 sample / settle / tidy，眼睛、脸、小块在这里另外做（frame）。

写 assets/source/zeus/repixel/ragnarok_zeus_{elder,muscle,adamas,transform,fx}_native（#sheet.png + #anim.fanim），
标签、帧序、时长照 codex_v01，格子坐标乘 2。--check 只重算一遍，和仓库里的比，不写文件（几个进程一起算，半分钟左右）。

Codex 的原画和工具不在仓库里，在它的本地仓库（提交 de2b95f），路径见 CODEX_REPO，环境变量 ZEUS_CODEX 可以改。
"""
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

ZEUS = os.path.join(ROOT, "assets", "source", "zeus")
CODEX_V01 = os.path.join(ZEUS, "codex_v01")
OUT_DIR = os.path.join(ZEUS, "repixel")
CODEX_REPO = os.environ.get(
    "ZEUS_CODEX", r"D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-zeus")
TOOL = os.path.join(CODEX_REPO, "design", "ragnarok_zeus", "tools", "build_assets.py")
FORMS = ("elder", "muscle", "adamas")
UP = 2.0

# Codex 的换色表（build_assets.py 的 COLOR_MAP，原画的颜色 -> 它定的 22 色，codex_tool() 里核对）
COLOR_MAP = [
    ((22, 20, 20), (22, 17, 20)), ((54, 50, 50), (42, 32, 37)),
    ((81, 76, 75), (75, 54, 54)), ((103, 92, 86), (99, 69, 60)), ((118, 105, 97), (115, 79, 66)),
    ((137, 122, 111), (140, 98, 77)), ((159, 144, 134), (164, 119, 97)), ((182, 163, 153), (191, 143, 117)),
    ((200, 183, 170), (222, 176, 145)), ((216, 199, 183), (240, 200, 167)),
    ((82, 84, 89), (62, 65, 83)), ((107, 110, 115), (85, 92, 112)), ((135, 139, 144), (111, 122, 142)),
    ((159, 161, 167), (145, 154, 173)), ((184, 187, 190), (181, 192, 207)), ((202, 205, 210), (212, 222, 233)),
    ((222, 220, 220), (246, 239, 224)), ((240, 238, 235), (255, 250, 236)),
    ((124, 96, 49), (166, 104, 32)), ((170, 137, 60), (208, 157, 51)), ((219, 188, 71), (250, 217, 95)),
    ((122, 72, 69), (130, 69, 66))]
OLD = np.array([o for o, _ in COLOR_MAP], np.int32)
PALETTE = np.array([n for _, n in COLOR_MAP], np.int32)
# 部位：0 透明、1 深色线条、2 皮肤、3 白（袍子、头发、胡子和蓝灰阴影）、4 金（眼睛、珠子和它的暗红）
INK, SKIN, WHITE, GOLD = 1, 2, 3, 4
GROUP = np.array([0] + [INK] * 2 + [SKIN] * 8 + [WHITE] * 8 + [GOLD] * 4, np.uint8)
# 每个部位用哪几档（PALETTE 的行，从暗到亮）
RAMP = {INK: (0, 1), SKIN: (2, 3, 4, 5, 6, 7, 8, 9), WHITE: (10, 11, 12, 13, 14, 15, 16, 17), GOLD: (21, 18, 19, 20)}
# 描边：同色系最深的那档（皮肤深红褐、白袍深蓝灰），不用一圈近黑的线（亚当那次用户说「身体周围那个描边还是太厚了
# 太浓了」）；往里一格是深色线条、金色的按皮肤算
OUTLINE_ROW = {INK: 2, SKIN: 2, WHITE: 10, GOLD: 2}
# 白袍、头发阴影里的冷灰：红比蓝多不到 8、四周 9x9 的不透明像素里一半以上是白的「皮肤」像素（真的皮肤红比蓝多
# 17 以上）
COOL_RB, COOL_AROUND = 8, 0.5
# 眼睛：格子里金色（不算珠子的暗红）有两个原画像素、占到这么多就是金色
EYE_SHARE = 0.2
# 眼窝：头顶往下这么多行（按 128 格算）里、离眼睛的金点不超过 2 格的深色留着近黑
HEAD_ROWS = {"elder": 22, "muscle": 28, "adamas": 24, "transform": 28}
# 旁边不透明的格子全是白的、不超过这么多格的皮肤色小块并进白；脸（离眼睛 FACE_REACH 格以内，按 128 格算）不动
SPECK, FACE_REACH = 6, 8
# 身体碰到 Codex 切格子的左右边：往格子外最多这么多原画像素接回和身体连着的部分（拳头、脚）
REACH = 60
# 取样的左上角加的一点点（原画像素），见 bodies
EPS = 1e-6


def codex_tool():
    B = R.load(TOOL, "zeus_build_assets")
    assert [tuple(map(tuple, p)) for p in B.COLOR_MAP] == COLOR_MAP, "Codex 的 COLOR_MAP 变了"
    return B


def nearest(rgb, pal):
    """每个像素最近的是 pal 的第几行。"""
    return ((rgb[..., None, :].astype(np.int32) - pal) ** 2).sum(-1).argmin(-1)


def parts_of(rgb):
    """每个像素按最近的那个 Codex 颜色分部位。"""
    return GROUP[nearest(rgb, PALETTE) + 1]


def recolour(a, run):
    """Codex 的 actor_colors：每个像素换成最近的那个原画颜色对应的 22 色之一（跑步的原画本来就是换过的，直接找最近的
    22 色）。只改一处：白袍、头发阴影里的冷灰（COOL_RB、COOL_AROUND）被它换成了皮肤色，这种换成最近的白。"""
    from scipy import ndimage
    a = np.array(a)
    on = a[..., 3] > 0
    rgb = a[..., :3].astype(np.int32)
    src = PALETTE if run else OLD
    idx = nearest(rgb, src)
    grp = np.where(on, GROUP[idx + 1], 0)
    # 四周不透明的像素里白的占多少（头发尖那种细的地方四周多是透明的，不算进去）
    around = ndimage.uniform_filter((grp == WHITE).astype(np.float32), 9) / np.maximum(
        ndimage.uniform_filter(on.astype(np.float32), 9), 1e-6)
    cool = (grp == SKIN) & (rgb[..., 0] - rgb[..., 2] < COOL_RB) & (around > COOL_AROUND)
    rows = np.nonzero(GROUP[1:] == WHITE)[0]
    idx[cool] = rows[nearest(rgb[cool], src[rows])]
    a[on, :3] = PALETTE[idx[on]]
    a[~on] = 0
    return a


def style(up):
    """共用的设定。头顶几行留深色的那一套不用（head_rows=0），眼睛、眼窝另外算（frame）。"""
    ramp = {k: PALETTE[list(rows)] for k, rows in RAMP.items()}
    outline = {k: tuple(int(v) for v in PALETTE[r]) for k, r in OUTLINE_ROW.items()}
    st = R.Style(parts_of, {k: len(v) for k, v in ramp.items()}, INK, outline, up=up, head_rows=0)
    return st, ramp


def cell_sums(a, scale, x0, y0, cell):
    """和 R.sample 一样切格，每格里 a 的和（积分图）。"""
    H, W = a.shape[:2]
    step = 1 / scale
    ey = np.clip(np.floor(y0 + np.arange(cell + 1) * step).astype(int), 0, H)
    ex = np.clip(np.floor(x0 + np.arange(cell + 1) * step).astype(int), 0, W)
    s = np.zeros((H + 1, W + 1) + a.shape[2:], np.float64)
    s[1:, 1:] = a.astype(np.float64).cumsum(0).cumsum(1)
    return s[ey[1:]][:, ex[1:]] - s[ey[:-1]][:, ex[1:]] - s[ey[1:]][:, ex[:-1]] + s[ey[:-1]][:, ex[:-1]]


def eyes(a, scale, x0, y0, cell, part, tone, body, ramp):
    """眼睛的金色：格子里金色（不算暗红）有两个以上、占到 EYE_SHARE 就算金色，颜色取这些金色像素的平均。
    原地改 part / tone，返回改了哪些格子。"""
    on = a[..., 3] > 0
    gold = on & np.isin(nearest(a[..., :3], PALETTE), (18, 19, 20))
    n_on = cell_sums(on, scale, x0, y0, cell)
    n_gold = cell_sums(gold, scale, x0, y0, cell)
    s_gold = cell_sums(np.where(gold[..., None], a[..., :3], 0), scale, x0, y0, cell)
    hit = body & (n_gold >= 2) & (n_gold >= EYE_SHARE * np.maximum(n_on, 1))
    for v, u in zip(*np.nonzero(hit)):
        part[v, u] = GOLD
        tone[v, u] = int(np.argmin(((ramp[GOLD] - s_gold[v, u] / n_gold[v, u]) ** 2).sum(1)))
    return hit


def head_rows(bank, body, up):
    """头顶往下 HEAD_ROWS 行。"""
    ys = np.nonzero(body.any(1))[0]
    head = np.zeros_like(body)
    head[ys.min():ys.min() + round(HEAD_ROWS[bank] * up)] = True
    return head


def sockets(bank, part, body, eye, up):
    """眼窝：头顶往下 HEAD_ROWS 行里、离眼睛的金点不超过 2 格的深色。"""
    from scipy import ndimage
    head = head_rows(bank, body, up)
    near = ndimage.binary_dilation(eye & head, structure=np.ones((3, 3), bool), iterations=2)
    return (part == INK) & body & near & head


def despeck(part, tone, body, protect):
    """零星的小块并进四周：旁边不透明的格子全是另一个部位的（被它包住，或者长在它的边上），皮肤色不超过 SPECK 格
    （白袍上的褐点、头发尖和袍子边上的褐点，留着描边会一段褐一段蓝灰），白色不超过 2 格（皮肤上的蓝灰点），档取旁边
    最多的那档。金色（眼睛、珠子）和 protect 里（脸）的不动。原地改。"""
    from scipy import ndimage
    for k, most in ((SKIN, SPECK), (WHITE, 2)):
        lab, _ = ndimage.label((part == k) & body, structure=np.ones((3, 3), bool))
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            y0, x0 = max(0, sl[0].start - 1), max(0, sl[1].start - 1)
            win = (slice(y0, sl[0].stop + 1), slice(x0, sl[1].stop + 1))
            m = lab[win] == i
            if m.sum() > most or (m & protect[win]).any():
                continue
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & ~m & body[win]
            around = part[win][ring]
            if not ring.any() or len(set(around.tolist())) != 1 or around[0] in (GOLD, INK):
                continue
            part[win][m] = around[0]
            tone[win][m] = Counter(tone[win][ring].tolist()).most_common(1)[0][0]


def despeck_after(out, protect):
    """描好边以后再看一遍：被另一个部位整个包住（八个方向都是它）的小块（修轮廓、描边时剩下的）并进去，颜色取四周最多
    的那个；大小、不动的地方和 despeck 一样。原地改。"""
    from scipy import ndimage
    on = out[..., 3] > 0
    part = np.where(on, parts_of(out[..., :3]), 0)
    for k, most in ((SKIN, SPECK), (WHITE, 2)):
        lab, _ = ndimage.label(part == k, structure=np.ones((3, 3), bool))
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            y0, x0 = max(0, sl[0].start - 1), max(0, sl[1].start - 1)
            win = (slice(y0, sl[0].stop + 1), slice(x0, sl[1].stop + 1))
            m = lab[win] == i
            if m.sum() > most or (m & protect[win]).any():
                continue
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & ~m
            around = part[win][ring]
            if not on[win][ring].all() or len(set(around.tolist())) != 1 or around[0] in (GOLD, INK):
                continue
            out[win][m, :3] = Counter(map(tuple, out[win][ring][:, :3].tolist())).most_common(1)[0][0]


def lone_ink(part, tone, body, keep):
    """R.settle 只换旁边有别的部位的深色线；旁边全是深色或透明的（头发尖上那种）也换掉：部位取 5x5 里最多的那个，
    用它最暗的那档。原地改。"""
    for y, x in zip(*np.nonzero((part == INK) & body & ~keep)):
        win = part[max(0, y - 2):y + 3, max(0, x - 2):x + 3].ravel().tolist()
        around = [k for k in win if k not in (0, INK)]
        part[y, x] = Counter(around).most_common(1)[0][0] if around else SKIN
        tone[y, x] = 0


def face_zone(bank, body, eye, up):
    """脸：离头顶几行里的眼睛金点 FACE_REACH 格以内（胡子上的珠子不算）；这帧没找到眼睛就用头顶那几行。"""
    from scipy import ndimage
    head = head_rows(bank, body, up)
    if (eye & head).any():
        return ndimage.binary_dilation(eye & head, structure=np.ones((3, 3), bool), iterations=round(FACE_REACH * up))
    return head


def frame(bank, tile, run, scale, x0, y0, cell, up):
    """一帧：换色，R.sample 取样，补上眼睛，R.settle 清杂点、把深色线换掉（眼窝再放回去），并掉零星的小块，
    R.tidy 修轮廓、描边，眼睛的金点放回去（tidy 会把四面都是眼窝的单个金点当杂点），最后再并一遍零星的小块。"""
    st, ramp = style(up)
    a = recolour(tile, run)
    part, tone, body = R.sample(st, a, scale, x0, y0, cell, ramp)
    eye = eyes(a, scale, x0, y0, cell, part, tone, body, ramp)
    keep = sockets(bank, part, body, eye, up) | eye
    p0, t0 = part.copy(), tone.copy()
    part, tone = R.settle(st, part, tone, body)
    part[keep], tone[keep] = p0[keep], t0[keep]
    lone_ink(part, tone, body, keep)
    face = face_zone(bank, body, eye, up)
    despeck(part, tone, body, face)
    painted = R.paint(part, tone, ramp)
    out = R.tidy(st, painted)
    back = eye & ~R.dilate4(out[..., 3] == 0)
    out[back] = painted[back]
    despeck_after(out, face)
    return out


def one(job):
    """进程池里算一帧。"""
    return frame(*job)


def placements(B):
    """跑一遍 Codex 的 actor_forms 和 transition_frames，记下它每帧 render_actor 的参数（原画格另记它在哪张原画的
    哪一格）。返回 {身体或 transform: {动作: [(原画格, 缩放, 轴心, 脚底行) 或者 (身体名,) 表示那个身体待机的第一帧]}}。"""
    real, real_grid = B.render_actor, B.source_grid

    def record(im, scale, pivot, ground=B.FOOT):
        out = real(im, scale, pivot, ground)
        out.zeus_place = (im, scale, pivot, ground)
        return out

    def grid(file, columns, rows):
        tiles = real_grid(file, columns, rows)
        size = Image.open(B.SOURCE / file).size
        for t, box in zip(tiles, B.tile_boxes(*size, columns, rows)):
            t.zeus_src = (file, box)
        return tiles
    B.render_actor, B.source_grid = record, grid
    try:
        actors, _ = B.actor_forms()
        trans = B.transition_frames(actors)
    finally:
        B.render_actor, B.source_grid = real, real_grid
    banks = {form: {a: [f.zeus_place for f in frames] for a, frames in acts.items()} for form, acts in actors.items()}
    firsts = {id(actors[f]["idle"][0]): f for f in actors}
    banks["transform"] = {a: [(firsts[id(f)],) if id(f) in firsts else f.zeus_place for f in frames]
                          for a, frames in trans.items()}
    return banks


def uncut(B, im):
    """Codex 按格子切原画，伸出格子的拳头、脚被切掉了（时间之拳打出那帧、膨胀普攻第 5 帧、倒地最后几帧的脚）。身体碰到
    格子左右边的，在格子外 REACH 个原画像素里把和身体连着的像素接回来（照 dominant_actor 的标准：不透明度 126 以上，
    去掉贴边的暗色半透明）。上下边不接：脚底就是地面那行，接了人会往下沉。返回（原画格 RGBA 数组、左边多出几列）。"""
    from scipy import ndimage
    a = np.asarray(im)
    on = a[..., 3] > 0
    left, right = on[:, 0].any(), on[:, -1].any()
    if not (left or right):
        return a, 0
    file, box = im.zeus_src
    sheet = Image.open(B.SOURCE / file).convert("RGBA")
    big = (max(0, box[0] - REACH * left), box[1], min(sheet.width, box[2] + REACH * right), box[3])
    lx = box[0] - big[0]
    raw = np.array(sheet.crop(big))
    alpha, colour = raw[..., 3], raw[..., :3].max(2)
    mask = alpha >= 126
    mask &= ~((ndimage.distance_transform_edt(mask) <= 4) & (colour < 38) & (alpha < 219))
    inside = np.zeros_like(mask)
    inside[:, lx:lx + a.shape[1]] = True
    seed = np.zeros_like(mask)
    seed[:, lx:lx + a.shape[1]] = on
    lab, _ = ndimage.label((mask & ~inside) | seed, structure=np.ones((3, 3), bool))
    add = np.isin(lab, np.unique(lab[seed])) & ~inside
    out = np.zeros_like(raw)
    out[:, lx:lx + a.shape[1]] = a
    out[add, :3] = raw[add, :3]
    out[add, 3] = 255
    return out, lx


def window(B, im, scale, pivot, ground):
    """render_actor 那一帧在原画里的左上角（含它为了不出格做的横向平移）。"""
    box = im.getbbox()
    half = B.CELL / 2
    x_min = half + (box[0] - pivot) * scale
    x_max = half + (box[2] - pivot) * scale
    dx = max(0.0, 3 - x_min) - max(0.0, x_max - (B.CELL - 3))
    return pivot - (half + dx) / scale, box[3] - ground / scale


def bodies(B, up):
    """{身体或 transform: {动作: [帧]}}。"""
    banks = placements(B)
    cell = round(B.CELL * up)
    jobs, keys = [], []
    for bank, acts in banks.items():
        for action, places in acts.items():
            for i, pl in enumerate(places):
                if len(pl) == 1:
                    continue
                im, scale, pivot, ground = pl
                tile, lx = uncut(B, im)
                x0, y0 = window(B, im, scale, pivot, ground)
                # 格子边正好落在整数上的（脚底那行就是）加一点点，免得浮点误差把最后一行原画分到脚底下面那格，人往下沉一格
                jobs.append((bank, tile, action == "run", scale * up, x0 + lx + EPS, y0 + EPS, cell, up))
                keys.append((bank, action, i))
    with ProcessPoolExecutor(min(16, os.cpu_count() or 1)) as pool:
        flat = list(pool.map(one, jobs))
    out = {bank: {a: [None] * len(p) for a, p in acts.items()} for bank, acts in banks.items()}
    for (bank, action, i), f in zip(keys, flat):
        out[bank][action][i] = f
    for action, places in banks["transform"].items():
        for i, pl in enumerate(places):
            if len(pl) == 1:
                out["transform"][action][i] = out[pl[0]]["idle"][0]
    return out


def isolated_fx(B, file, up):
    """Codex 的 isolated_fx，缩成 78 格那一步换成 78 x up，格子用 B.CELL x up。"""
    im = Image.open(B.SOURCE / file).convert("RGBA")
    cell = round(B.CELL * up)
    results = []
    for box in B.tile_boxes(im.width, im.height, 4, 4):
        tile = im.crop(box)
        arr = np.array(tile)
        alpha = arr[:, :, 3]
        mask = alpha >= 162
        border = max(3, round(min(tile.size) * .035))
        mask[:border] = mask[-border:] = False
        mask[:, :border] = mask[:, -border:] = False
        arr[:, :, 3] = mask.astype(np.uint8) * 255
        arr[~mask] = 0
        tile = Image.fromarray(arr)
        ratio = 78 * up / max(tile.size)
        tile = tile.resize(tuple(round(n * ratio) for n in tile.size), Image.Resampling.NEAREST)
        output = Image.new("RGBA", (cell, cell))
        output.paste(tile, ((cell - tile.width) // 2, (cell - tile.height) // 2))
        assert output.getbbox(), (file, box)
        results.append(output)
    return results


def effects(B, up):
    """{特效: [8 帧]}，按 Codex 的 EFFECTS 顺序，每张原画 32 色（Codex 的 fixed_palette）。"""
    out = {}
    for source, (first, second) in B.EFFECTS.items():
        images = [np.asarray(f) for f in B.fixed_palette(isolated_fx(B, source + ".png", up), 32)]
        out[first], out[second] = images[:8], images[8:]
    return out


def make(up):
    B = codex_tool()
    frames = bodies(B, up)
    outs = []
    for bank in FORMS + ("transform",):
        stem = f"ragnarok_zeus_{bank}_native"
        outs.append((os.path.join(OUT_DIR, stem), *R.sheet_of(frames[bank], os.path.join(CODEX_V01, stem), up)))
    stem = "ragnarok_zeus_fx_native"
    outs.append((os.path.join(OUT_DIR, stem), *R.sheet_of(effects(B, up), os.path.join(CODEX_V01, stem), up)))
    return outs


if __name__ == "__main__":
    R.run(__doc__, make, UP)
