#!/usr/bin/env python3
"""终末包换成 Q 版像素画：把 Codex 重画的像素写进每个英雄的图集，帧表、PPU 都不动（FIT 的索尔例外：格子跟着画走）。

    python tools/art/ragnarok_q_pixel.py                  # 写 ragnarok/champions/<英雄>#sheet.png
    python tools/art/ragnarok_q_pixel.py --check          # 和现在的图集不一样就退出 1
    python tools/art/ragnarok_q_pixel.py --hero thor      # 只做这几个（可以给多个 --hero）

用户 2026-11-23：「女武神换成了Q版像素风格 帮我整体更换一下 还有BP格子也是 现在这个系列的就用Q版像素风格就行了 但是还是要用PPU
保持高清」。Codex 交的（assets/source/q_pixel，交接说明 HANDOFF.md，每个文件对过 checksums.json）：18 个英雄连 6 套形态的战斗图集，
1 倍、hd_、lo_ 三档都重画成 Q 版，以用户认过的阿波罗试画为准。它交的是 0.11.0 发行版那一版图集（tools/package_mod.py 打过包的：
相同的帧合成一格、挨着排），每个 #anim.fanim 和发行版逐字节相同，只换了像素。

仓库里的图集没打包（import_<英雄>.py、ppu_hd.py、hero_reels.py、ragnarok_run_pace.py 写的），帧放的位置不一样；打包只挪 x、y，所以
每个动作的帧数、每帧的大小和时长两边都一样：按「同一个动作的第几帧」把 Q 版那一格的像素拷到仓库那一格。高清帧（hd_）还是高清帧、
PPU 照旧（hd.rs 的表不动），选人格子和百科的界面图是打包时从这些帧重新拼的（ui_sheets/），跟着变成 Q 版。特效图、弹道图、技能图标、
选人立绘不在这次重画里，照旧。
两边帧表对不上的动作（比如以后 hero_reels.py 重挑的待机、选人片段：它们只引用别的动作已有的格子）跳过；仓库里每一个被引用的格子都得
从对得上的动作拿到像素，拿不到、或者同一格拿到两份不一样的像素，都报错不写。
导入（import_<英雄>.py）写的还是 Codex 原来那一版的画：重新导入一个英雄以后按顺序跑 ppu_hd.py、hero_reels.py、ragnarok_run_pace.py，
最后跑这个。

索尔（2026-11-26 起）：Codex 整个重画了一版（用户：「索尔的不用你修了 我让codex去全部重做了」「用codex原样」），
tools/art/thor_q_redo.py 原样（每帧以枢轴为中心切好）写进这里的 ragnarok_thor 图集。新画的锤子和特效比原来的格子大（按原来的格子贴要切掉三万多
个像素），所以他在 FIT 里：仓库的每一格换成 Q 版那一格的大小（都以枢轴为中心），整张图集按帧表里第一次出现的顺序重新排，帧表跟着
改写；别的英雄还是只换像素。原来那处修正（旧画的待机第 0 帧扛锤的手挡住半张脸，换成第 1 帧的画）新画用不着，去掉了。
阿波罗待机第 0 帧和别的帧不是同一版画（窄一圈，胸甲和腰带之间一道黑线），用户先说「阿波罗这里的黑线也处理下」，看了以后：「算了不用改了
就用黑线吧」——照 Codex 交的原样，不改。
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHEETS = os.path.join(ROOT, "ragnarok", "champions")
Q = os.path.join(ROOT, "assets", "source", "q_pixel", "champions")
# (英雄, 动作, 改哪一帧, 用哪一帧的画)：动作的 hd_ / lo_ 跟着一起改
FIX = []
# 格子跟着 Q 版的画走的英雄（见上面的说明）：仓库每一格的大小换成 Q 版那一格的，图集重新排、帧表改写
FIT = {"ragnarok_thor"}
FIT_W = 2048                # 重新排的时候一行最宽多少（一格比这还宽就按那一格）
# 2026-11-26 照原作补画的动作（assets/source/<英雄>/fidelity，Codex 交的就是 Q 版，import_<英雄>.py 直接导进来）：这些标签
# （连 hd_、lo_）的像素原样留着，不从 Q 版图集拿
KEEP = {
    "ragnarok_thor": ["skill2"],
    "ragnarok_jack": ["ult", "skill2"],
    "ragnarok_raiden": ["skill2"],
    "ragnarok_zerofuku": ["skill2", "h_skill", "h_ult"],
    "ragnarok_lubu": ["ult"],
    "ragnarok_poseidon": ["skill2"],
    "ragnarok_hades": ["skill"],
    "ragnarok_shiva": ["skill2"],
    "ragnarok_heracles": ["c_skill2"],
    "ragnarok_zeus": ["skill"],
}
# 挪了地方的动作：仓库的标签 -> (Q 版图集里的标签, 取它的哪几帧)。None 是整个动作，("tail", n) 是最后 n 帧
# （索尔原来 E 的扔锤、空手、接锤挪进大招「觉醒雷槌」，原来大招举锤过头砸下的后半段接在接锤后面）
RENAME = {
    "ragnarok_thor": {"ult": ("skill2", None), "ult_wait": ("skill2_wait", None), "ult_catch": ("skill2_catch", None),
                      "ult_slam": ("ult", ("tail", 12))},
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(stem):
    sheet = np.asarray(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    return sheet, anims


def rect(f):
    d = f["data"]
    return tuple(int(round(d[k])) for k in ("x", "y", "w", "h"))


# 一帧的大小最多差几格还算同一帧（按中心贴）：2026-11-26 加了补画的动作以后，全英雄共用的调色板变了一点，波塞冬普攻最后两帧
# 的 1 倍帧边上多出一行淡像素（131 -> 133 高）。帧以中心（枢轴）对齐，按中心贴 Q 版那一帧的像素就对得上
SLACK = 8


def same_shape(a, b):
    """两个动作的帧表除了位置都一样：帧数、每帧的大小（差 SLACK 格以内按中心贴；时长不比：2026-11-26 波旬的 h_skill2 为了
    和补画的斧爻岚阵一样长，最后一帧拉长了，像素还是那一帧的）。"""
    fa, fb = a["frames"], b["frames"]

    def same(x, y):
        if rect(x)[2:] == rect(y)[2:]:
            return True
        # 大小差几格的，时长也得一样（待机、选人片段是拼出来的，帧数碰巧一样也不能配上）
        return (abs(rect(x)[2] - rect(y)[2]) <= SLACK and abs(rect(x)[3] - rect(y)[3]) <= SLACK
                and abs(x["duration"] - y["duration"]) < 1e-6)
    return len(fa) == len(fb) and all(same(x, y) for x, y in zip(fa, fb))


def same_timing(a, b, renamed):
    """FIT 的英雄格子大小跟着 Q 版走，不比大小：帧数一样、每帧时长一样（拼出来的待机、选人片段靠这个对上）；挪过地方的
    动作（RENAME）时长是仓库自己的，只比帧数。"""
    fa, fb = a["frames"], b["frames"]
    return len(fa) == len(fb) and (renamed or all(abs(x["duration"] - y["duration"]) < 1e-6 for x, y in zip(fa, fb)))


def repack(anims, got):
    """FIT：{原来的格子: 像素} 按帧表里第一次出现的顺序一行一行重新排 -> (新图集, 新帧表)。顺序只看帧表，再跑一遍排出来一样。"""
    order = []
    for a in anims.values():
        for f in a["frames"]:
            if rect(f) not in order:
                order.append(rect(f))
    width = max([FIT_W] + [got[r].shape[1] for r in order])
    pos, x, y, row = {}, 0, 0, 0
    for r in order:
        h, w = got[r].shape[:2]
        if x and x + w > width:
            x, y, row = 0, y + row + 1, 0
        pos[r] = (x, y)
        x += w + 1
        row = max(row, h)
    W = max(pos[r][0] + got[r].shape[1] for r in order)
    H = max(pos[r][1] + got[r].shape[0] for r in order)
    sheet = np.zeros((H, W, 4), np.uint8)
    for r in order:
        px, py = pos[r]
        sheet[py:py + got[r].shape[0], px:px + got[r].shape[1]] = got[r]
    new = {}
    for tag, a in anims.items():
        new[tag] = {**a, "frames": [{**f, "data": {"x": float(pos[rect(f)][0]), "y": float(pos[rect(f)][1]),
                                                   "w": float(got[rect(f)].shape[1]), "h": float(got[rect(f)].shape[0])}}
                                    for f in a["frames"]]}
    return sheet, new


def centred(px, w, h):
    """Q 版一帧的像素按中心放进 w x h 的格子（大了切边、小了补透明）。"""
    out = np.zeros((h, w, 4), np.uint8)
    ph, pw = px.shape[:2]
    oy, ox = (h - ph) // 2, (w - pw) // 2
    sy0, sx0 = max(0, -oy), max(0, -ox)
    dy0, dx0 = max(0, oy), max(0, ox)
    hh, ww = min(ph - sy0, h - dy0), min(pw - sx0, w - dx0)
    out[dy0:dy0 + hh, dx0:dx0 + ww] = px[sy0:sy0 + hh, sx0:sx0 + ww]
    return out


def q_frames(qa, tag, hid):
    """仓库的一个标签在 Q 版图集里对应的帧表（RENAME 挪过的按它取），没有就 None。"""
    pre = next((p for p in ("hd_", "lo_") if tag.startswith(p)), "")
    plain = tag[len(pre):]
    q, part = RENAME.get(hid, {}).get(plain, (plain, None))
    a = qa.get(pre + q)
    if a is None:
        return None
    fr = a["frames"]
    if part is not None:
        fr = fr[-part[1]:]
    return {"frames": fr}


def q_sheet(hid):
    """一个英雄的仓库图集换成 Q 版的像素 -> (新图集, 用上的动作数, 跳过的动作, 新帧表：FIT 的英雄才有，别的 None)。"""
    sheet, anims = read(os.path.join(SHEETS, hid))
    qs, qa = read(os.path.join(Q, hid))
    fit = hid in FIT
    out = np.zeros_like(sheet)
    got = {}
    used, skipped = 0, []
    keep = {p + t for t in KEEP.get(hid, []) for p in ("", "hd_", "lo_")}
    for tag, a in anims.items():
        if tag in keep:
            used += 1
            for f in a["frames"]:
                x, y, w, h = rect(f)
                got[(x, y, w, h)] = sheet[y:y + h, x:x + w]
                out[y:y + h, x:x + w] = sheet[y:y + h, x:x + w]
    for tag, a in anims.items():
        if tag in keep:
            continue
        qt = q_frames(qa, tag, hid)
        renamed = tag[len(next((p for p in ("hd_", "lo_") if tag.startswith(p)), "")):] in RENAME.get(hid, {})
        if qt is None or not (same_timing(a, qt, renamed) if fit else same_shape(a, qt)):
            skipped.append(tag)
            continue
        used += 1
        for f, g in zip(a["frames"], qt["frames"]):
            x, y, w, h = rect(f)
            u, v, gw, gh = rect(g)
            px = qs[v:v + gh, u:u + gw]
            if (gw, gh) != (w, h) and not fit:
                px = centred(px, w, h)
            if (x, y, w, h) in got:
                if not np.array_equal(got[(x, y, w, h)], px):
                    raise SystemExit(f"{hid} {tag}: the cell at {(x, y, w, h)} gets two different Q pictures")
                continue
            got[(x, y, w, h)] = px
            if not fit:
                out[y:y + h, x:x + w] = px
    for tag, a in anims.items():
        for f in a["frames"]:
            if rect(f) not in got:
                raise SystemExit(f"{hid} {tag}: the cell at {rect(f)} has no Q picture (no matching tag holds it)")
    if fit:
        if any(fid == hid for fid, *_ in FIX):
            raise SystemExit(f"{hid}: a FIX row for a FIT hero")
        new, table = repack(anims, got)
        return new, used, skipped, table
    for fid, tag, dst, src in FIX:
        if fid != hid:
            continue
        for pre in ("", "hd_", "lo_"):
            fr = anims[pre + tag]["frames"]
            x, y, w, h = rect(fr[dst])
            sx, sy, sw, sh = rect(fr[src])
            if (w - sw) % 2 or (h - sh) % 2:
                raise SystemExit(f"{hid} {pre}{tag}: frames {dst} and {src} do not share a centre ({w}x{h} / {sw}x{sh})")
            cell = np.zeros((h, w, 4), np.uint8)
            ox, oy = (w - sw) // 2, (h - sh) // 2
            if ox < 0 or oy < 0:
                raise SystemExit(f"{hid} {pre}{tag}: frame {src} is bigger than frame {dst}")
            cell[oy:oy + sh, ox:ox + sw] = out[sy:sy + sh, sx:sx + sw]
            out[y:y + h, x:x + w] = cell
    return out, used, skipped, None


def heroes(only):
    ids = sorted(os.path.basename(p).split("#")[0] for p in os.listdir(Q) if p.endswith("#sheet.png"))
    if only:
        want = {h if h.startswith("ragnarok_") else "ragnarok_" + h for h in only}
        missing = want - set(ids)
        if missing:
            raise SystemExit(f"no Q sheet for {sorted(missing)}")
        ids = [i for i in ids if i in want]
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--hero", action="append")
    a = ap.parse_args()
    bad = 0
    for hid in heroes(a.hero):
        new, used, skipped, table = q_sheet(hid)
        path = os.path.join(SHEETS, hid + "#sheet.png")
        fpath = os.path.join(SHEETS, hid + "#anim.fanim")
        old = np.asarray(Image.open(lp(path)).convert("RGBA"))
        same_table = table is None or json.load(open(lp(fpath), encoding="utf-8-sig"))["anims"] == table
        if a.check:
            if not (old.shape == new.shape and np.array_equal(old, new) and same_table):
                print(f"{hid}: not the Q picture - run tools/art/ragnarok_q_pixel.py")
                bad += 1
            continue
        if not (old.shape == new.shape and np.array_equal(old, new)):
            Image.fromarray(new).save(lp(path))
        if not same_table:
            # 和 hero_reels.py、ragnarok_run_pace.py、导入写的一样
            with open(lp(fpath), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps({"anims": table}, ensure_ascii=False, separators=(",", ":")))
        print(f"{hid}: {used} tags from the Q sheet" + (f", skipped {', '.join(skipped)}" if skipped else ""))
    if a.check:
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
