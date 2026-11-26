#!/usr/bin/env python3
"""索尔 Q 版（Codex 2026-11-26 整个重画，assets/source/thor/q_redo）原样写进 Q 版图集和铁手套格挡的补画。

    python tools/art/thor_q_redo.py            # 写 assets/source/q_pixel/champions/ragnarok_thor#sheet.png + #anim.fanim
                                               # 和 assets/source/thor/fidelity/atlases/（格挡）
    python tools/art/thor_q_redo.py --check    # 和现在的文件不一样就退出 1

之后照常跑 import_thor.py、ppu_hd.py --hero thor、hero_reels.py --hero thor、ragnarok_run_pace.py、ragnarok_q_pixel.py。

用户 2026-11-26：「雷神彻底重做了 你看一下 有问题的地方你帮忙修复」。试过加密（PPU 2.75、3.34）、补描边、换成同一张脸，
最后定的是「用codex原样」（「算了不用改了」）。像素一格不动（三档都用 Codex 自己的：1 倍、hd_、lo_），PPU 照旧 2.225，
只做接进游戏要的：
- 每一帧以枢轴为中心（仓库的图集都这样：脚底在 (w/2, h/2 + 11.5 x PPU)，脚最下一行在 round(h/2 + 11.5 x PPU - 1)）。
  Codex 的格子是统一大格、脚底点在 registration.json 里；这里按它切成刚好装下的帧：1 倍是奇数大小，hd_ = round(2.225 x 1 倍)、
  lo_ = round(1.5 x 1 倍)（addons/ragnarok/src/hd.rs 要查待机第一帧的 hd_ 宽是不是 PPU 倍）。新画的锤子和特效比原来的格子大，
  tools/art/ragnarok_q_pixel.py 的 FIT 让仓库的格子跟着这里的大小走。
- 格挡（q_redo/thor_guard）：Codex 的角色图存成了两倍（每 2x2 一块，身体 78-88 格高），frames.json 却照旧写 hd_multiplier 2、
  格子 216x168、脚底点 (98, 148)，照读游戏里大一倍：每 2x2 取一格读回逻辑像素（格子 108x84、脚底点 (49, 74)；导入时再放大两倍
  就是 Codex 那张图，像素不变）。特效每帧的偏移用 Codex 这次跟着新手套重标的 fx_events（tools/art/ragnarok_atlas.py 的
  redraw_offset 读的是 fx 那一份，Codex 没改它）：抄到 fx 里。
"""
import argparse
import copy
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "thor", "q_redo")
OUT_Q = os.path.join(ROOT, "assets", "source", "q_pixel", "champions", "ragnarok_thor")
OUT_FID = os.path.join(ROOT, "assets", "source", "thor", "fidelity", "atlases")

PPU = 2.225
FEET = 11.5                 # 枢轴（格子中心）到脚底的游戏像素
TIERS = {"": 1.0, "hd_": PPU, "lo_": 1.5}
SHEET_W = 2048              # 输出图集一行最宽多少


def png(path):
    return np.asarray(Image.open(path).convert("RGBA"))


def rect(f):
    d = f["data"]
    return tuple(int(round(d[k])) for k in ("x", "y", "w", "h"))


def place(c, ground, ppu, w, h):
    """Codex 的一格（脚底点 ground）切成 w x h、以枢轴为中心的帧 -> (帧, 切掉的不透明像素数)。"""
    ox = int(round(ground[0] - w / 2))
    oy = (ground[1] - 1) - int(round(h / 2 + FEET * ppu - 1))
    out = np.zeros((h, w, 4), np.uint8)
    sy0, sx0 = max(0, oy), max(0, ox)
    sy1, sx1 = min(c.shape[0], oy + h), min(c.shape[1], ox + w)
    out[sy0 - oy:sy1 - oy, sx0 - ox:sx1 - ox] = c[sy0:sy1, sx0:sx1]
    return out, int((c[..., 3] > 0).sum() - (out[..., 3] > 0).sum())


def frames_of(cells, grounds):
    """一个画面的三档（{档: Codex 的格}）-> {档: 帧}：1 倍取能让三档都装得下的最小奇数大小。"""
    def fits(w1, h1):
        for t, ppu in TIERS.items():
            w, h = (w1, h1) if t == "" else (int(round(ppu * w1)), int(round(ppu * h1)))
            if place(cells[t], grounds[t], ppu, w, h)[1]:
                return False
        return True
    w1 = 1
    while not fits(w1, 999):
        w1 += 2
    h1 = 1
    while not fits(w1, h1):
        h1 += 2
    out = {}
    for t, ppu in TIERS.items():
        w, h = (w1, h1) if t == "" else (int(round(ppu * w1)), int(round(ppu * h1)))
        out[t] = place(cells[t], grounds[t], ppu, w, h)[0]
    return out


def pack(cells):
    """[图] -> (图集, [(x, y)])：一行一行排，行高按这一行最高的，行宽不过 SHEET_W。"""
    pos, x, y, row = [], 0, 0, 0
    for c in cells:
        h, w = c.shape[:2]
        if x and x + w > SHEET_W:
            x, y, row = 0, y + row + 1, 0
        pos.append((x, y))
        x += w + 1
        row = max(row, h)
    W = max(px + c.shape[1] for (px, _), c in zip(pos, cells))
    H = max(py + c.shape[0] for (_, py), c in zip(pos, cells))
    sheet = np.zeros((H, W, 4), np.uint8)
    for (px, py), c in zip(pos, cells):
        sheet[py:py + c.shape[0], px:px + c.shape[1]] = c
    return sheet, pos


def q_sheet():
    """-> (#sheet.png 的像素, #anim.fanim 的文本)。"""
    reg = json.load(open(os.path.join(SRC, "registration.json"), encoding="utf-8"))["tracks"]
    grounds = {"": tuple(reg["base"]["ground"]), "hd_": tuple(reg["hd_"]["ground"]), "lo_": tuple(reg["lo_"]["ground"])}
    stem = os.path.join(SRC, "q_sheets", "ragnarok_thor")
    sheet = png(stem + "#sheet.png")
    anims = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    plain = [t for t in anims if not t.startswith(("hd_", "lo_"))]
    index, tiers, plan = {}, {t: [] for t in TIERS}, {}
    for tag in plain:
        durs = [[f["duration"] for f in anims[t + tag]["frames"]] for t in TIERS]
        if any(d != durs[0] for d in durs):
            raise SystemExit(f"{tag}: the three tiers' frames differ")
        plan[tag] = []
        for i, d in enumerate(durs[0]):
            cells = {}
            for t in TIERS:
                x, y, w, h = rect(anims[t + tag]["frames"][i])
                cells[t] = sheet[y:y + h, x:x + w]
            key = b"".join(cells[t].tobytes() for t in TIERS)
            if key not in index:
                fr = frames_of(cells, grounds)
                index[key] = len(tiers["hd_"])
                for t in TIERS:
                    tiers[t].append(fr[t])
            plan[tag].append((index[key], d))
    blocks, offs, y = [], {}, 0
    for t in ("", "hd_", "lo_"):
        s, pos = pack(tiers[t])
        offs[t] = [(px, py + y) for px, py in pos]
        blocks.append((s, y))
        y += s.shape[0] + 1
    W = max(s.shape[1] for s, _ in blocks)
    out = np.zeros((y - 1, W, 4), np.uint8)
    for s, yy in blocks:
        out[yy:yy + s.shape[0], :s.shape[1]] = s
    fanim = {"anims": {}}
    for tag in anims:
        t = next((p for p in ("hd_", "lo_") if tag.startswith(p)), "")
        fanim["anims"][tag] = {"frames": [
            {"duration": d, "data": {"x": float(offs[t][i][0]), "y": float(offs[t][i][1]),
                                     "w": float(tiers[t][i].shape[1]), "h": float(tiers[t][i].shape[0])}}
            for i, d in plan[tag[len(t):]]]}
    return out, json.dumps(fanim, ensure_ascii=False, separators=(",", ":"))


def guard():
    """-> (actor 像素, fx 像素, frames.json 的文本)。"""
    root = os.path.join(SRC, "thor_guard", "atlases")
    m = json.load(open(os.path.join(root, "frames.json"), encoding="utf-8"))
    actor, fxs = png(os.path.join(root, "thor_actor.png")), png(os.path.join(root, "thor_fx.png"))
    if not (actor[::2, ::2].repeat(2, 0).repeat(2, 1) == actor).all() or any(v % 2 for v in m["cell"] + m["ground"]):
        raise SystemExit("guard: thor_actor.png is no longer the 2x2 of a logical picture - read it as it is")
    n = copy.deepcopy(m)
    n["cell"] = [m["cell"][0] // 2, m["cell"][1] // 2]
    n["ground"] = [m["ground"][0] // 2, m["ground"][1] // 2]
    for f in n["actor"]["skill2"]["frames"]:
        for k in ("x", "y", "w", "h"):
            f[k] //= 2
    for nm, ev in m.get("fx_events", {}).items():
        n["fx"][nm]["offset"] = list(ev["offset"])
        n["fx"][nm]["frame_offsets"] = {k: list(v) for k, v in ev["frame_offsets"].items()}
    n["q_redo"] = {"tool": "tools/art/thor_q_redo.py", "from": "assets/source/thor/q_redo/thor_guard",
                   "note": "角色图每 2x2 取一格读回逻辑像素（Codex 存成了两倍，frames.json 按逻辑像素写）；"
                           "fx 的偏移抄自 fx_events；baseline 里的数是 Codex 的"}
    return actor[::2, ::2], fxs, json.dumps(n, ensure_ascii=False, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sheet, fanim = q_sheet()
    actor, fx, meta = guard()
    want = {OUT_Q + "#sheet.png": sheet, OUT_Q + "#anim.fanim": fanim,
            os.path.join(OUT_FID, "thor_actor.png"): actor, os.path.join(OUT_FID, "thor_fx.png"): fx,
            os.path.join(OUT_FID, "frames.json"): meta}
    bad = 0
    for path, v in want.items():
        if isinstance(v, str):
            have = open(path, encoding="utf-8-sig").read() if os.path.isfile(path) else None
            same = have is not None and json.loads(have) == json.loads(v)
        else:
            same = os.path.isfile(path) and np.array_equal(png(path), v)
        if a.check:
            if not same:
                print(f"{os.path.relpath(path, ROOT)}: not what thor_q_redo.py makes")
                bad += 1
            continue
        if not same:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if isinstance(v, str):
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(v)
            else:
                Image.fromarray(v).save(path)
        print(os.path.relpath(path, ROOT) + ("" if same else " (written)"))
    if a.check:
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
