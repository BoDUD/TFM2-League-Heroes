"""战场特效图集 <-> 一帧一张 PNG（给画师重画用，用户 2026-11-26：「小龙的特效也借这次机会重做怎么样 让codex 一起重新再整理一下」）。

大小龙（league_dragons）和海克斯大乱斗（league_hextech）的战场特效都是一张图集（`effects/<mod>_fx#sheet.png`）加一张表
（`src/fx_atlas.rs`：每段动画在图上的位置、帧大小、帧数、锚点、每帧几 tick）加编进 DLL 的横条（`src/fx_runs.bin`）。
画师不碰图集：拆成 `frames/<动画>/<动画>_<第几帧>.png` 和 `spec.json`，照格子重画，再拼回去。只用 numpy 和 Pillow。

  python tools/art/fx_frames.py dump  --mod league_dragons --out <文件夹> [--what what.json] [--preview p.png]
  python tools/art/fx_frames.py build --mod league_dragons --frames <文件夹> [--check]

build 按 spec.json 的顺序和大小拼：每段动画一行（宽过 --sheet-w 就折行，和生成脚本一样），表头照抄现在的 fx_atlas.rs（每个模组
自己的说明），横条照 dragons_soul_fx.py / hextech_fx.py 的格式；`--two-tone 名字,…` 的动画在横条里只用深浅两色（大小龙的草丛：
画不了贴图时一格一格画，六个色阶一帧两千多条，两色一千条上下；图集里照旧是画师画的颜色）。
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

ANIM_RE = re.compile(r'Anim \{ name: "(\w+)", x: (\d+), y: (\d+), w: (\d+), h: (\d+), frames: (\d+), per_row: (\d+), '
                     r'ax: (\d+), ay: (\d+), ticks: (\d+) \}')
#: 一个模组的图集最宽多少（生成脚本里的 SHEET_W）
SHEET_W = {"league_dragons": 1056, "league_hextech": 1024}
#: 横条只用两色的（大小龙的两种草丛）
TWO_TONE = {"league_dragons": ["brush_ocean", "brush_chem"], "league_hextech": []}


def paths(mod):
    base = os.path.join(ROOT, "addons", mod)
    return (os.path.join(base, "effects", f"{mod}_fx#sheet.png"), os.path.join(base, "src", "fx_atlas.rs"),
            os.path.join(base, "src", "fx_runs.bin"))


def read_table(atlas):
    text = open(atlas, encoding="utf-8").read()
    rows = [(m[0], *map(int, m[1:])) for m in ANIM_RE.findall(text)]
    assert rows, f"no animations in {atlas}"
    return text, rows


def dump(mod, out, what=None, preview_to=None):
    sheet_path, atlas, _ = paths(mod)
    sheet = np.array(Image.open(sheet_path).convert("RGBA"))
    _, rows = read_table(atlas)
    notes = json.load(open(what, encoding="utf-8")) if what else {}
    spec, anims = [], []
    for name, x, y, w, h, n, per_row, ax, ay, ticks in rows:
        d = os.path.join(out, "frames", name)
        os.makedirs(d, exist_ok=True)
        frames = []
        for k in range(n):
            fx, fy = x + (k % per_row) * w, y + (k // per_row) * h
            f = sheet[fy:fy + h, fx:fx + w].copy()
            frames.append(f)
            Image.fromarray(f, "RGBA").save(os.path.join(d, f"{name}_{k}.png"))
        note = notes.get(name, {})
        if isinstance(note, str):
            note = {"what": note}
        spec.append({"name": name, "w": w, "h": h, "anchor": [ax, ay], "frames": n, "ticks": ticks,
                     "seconds": round(n * ticks / 60, 3), **note})
        anims.append((name, w, h, (ax, ay), ticks, frames))
    with open(os.path.join(out, "spec.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    if preview_to:
        preview(anims, preview_to)
    return spec


def load(src):
    """画师交回来的帧：大小、帧数照 spec.json；透明度压成 0 / 255（透明的格子颜色清零）。"""
    spec = json.load(open(os.path.join(src, "spec.json"), encoding="utf-8"))
    anims = []
    for s in spec:
        frames = []
        for k in range(s["frames"]):
            img = np.array(Image.open(os.path.join(src, "frames", s["name"], f"{s['name']}_{k}.png")).convert("RGBA"))
            assert img.shape == (s["h"], s["w"], 4), f"{s['name']} {k}: {img.shape[1]}x{img.shape[0]}, want {s['w']}x{s['h']}"
            img[..., 3] = np.where(img[..., 3] >= 128, 255, 0)
            img[img[..., 3] == 0] = 0
            assert img[..., 3].any(), f"{s['name']} {k}: an empty frame"
            frames.append(img)
        anims.append((s["name"], s["w"], s["h"], tuple(s["anchor"]), s["ticks"], frames))
    return anims


def pack(anims, sheet_w):
    rows, y = [], 0
    for name, w, h, anchor, ticks, frames in anims:
        per_row = min(len(frames), sheet_w // w)
        lines = -(-len(frames) // per_row)
        rows.append((name, 0, y, w, h, len(frames), per_row, anchor[0], anchor[1], ticks))
        y += lines * h
    width = -(-max(r[6] * r[3] for r in rows) // 4) * 4
    height = -(-y // 4) * 4
    sheet = np.zeros((height, width, 4), np.uint8)
    for (name, x0, y0, w, h, n, per_row, _, _, _), (_, _, _, _, _, frames) in zip(rows, anims):
        for k, f in enumerate(frames):
            x, yy = x0 + (k % per_row) * w, y0 + (k // per_row) * h
            sheet[yy:yy + h, x:x + w] = f
    return sheet, rows


def two_tone(f):
    """深浅两色：按亮度分两半，深的一半涂成其中最常见的深色，亮的一半涂成最常见的亮色。"""
    out = f.copy()
    m = out[..., 3] > 0
    if not m.any():
        return out
    lum = out[..., 0].astype(int) * 3 + out[..., 1].astype(int) * 6 + out[..., 2].astype(int)
    cut = np.median(lum[m])
    for half in (m & (lum <= cut), m & (lum > cut)):
        if not half.any():
            continue
        cols, counts = np.unique(out[half][:, :3], axis=0, return_counts=True)
        out[half, :3] = cols[counts.argmax()]
    return out


def runs_of(anims, two=()):
    palette, body = {}, bytearray()
    for name, w, h, anchor, ticks, frames in anims:
        assert w <= 255 and h <= 255 and len(frames) <= 255, name
        body.append(len(frames))
        for f in frames:
            if name in two:
                f = two_tone(f)
            runs, n = bytearray(), 0
            for y in range(h):
                x = 0
                while x < w:
                    if f[y, x, 3] == 0:
                        x += 1
                        continue
                    c = tuple(int(v) for v in f[y, x, :3])
                    x0 = x
                    while x < w and f[y, x, 3] and tuple(int(v) for v in f[y, x, :3]) == c:
                        x += 1
                    k = palette.setdefault(c, len(palette))
                    assert k <= 255, "more than 256 colours"
                    runs += bytes((x0, y, x - x0, k))
                    n += 1
            body += n.to_bytes(2, "little") + runs
    out = bytearray(b"DFXR") + len(palette).to_bytes(2, "little")
    for c in palette:
        out += bytes(c) + bytes([255])
    out += len(anims).to_bytes(2, "little") + body
    return bytes(out)


def table(old_text, rows, size):
    """表头照抄现在的表（`pub const SHEET` 之前的部分），后面按新的位置写。"""
    head = old_text[:old_text.index("pub const SHEET")]
    # 表头最后一行是 SHEET 的说明（/// …），要紧挨着它
    lines = [head.rstrip("\n"), f"pub const SHEET: (u16, u16) = ({size[0]}, {size[1]});", "",
             f"pub const ANIMS: [Anim; {len(rows)}] = ["]
    for name, x, y, w, h, n, per_row, ax, ay, ticks in rows:
        lines.append(f'    Anim {{ name: "{name}", x: {x}, y: {y}, w: {w}, h: {h}, frames: {n}, per_row: {per_row}, ax: {ax}, '
                     f"ay: {ay}, ticks: {ticks} }},")
    lines.append("];")
    return "\n".join(lines) + "\n"


def build(mod, src, check=False, preview_to=None):
    sheet_path, atlas, runs_path = paths(mod)
    old_text, old_rows = read_table(atlas)
    anims = load(src)
    # 动画的名字和顺序不能变（DLL 里按名字找，测试按表核对）
    assert [a[0] for a in anims] == [r[0] for r in old_rows], "the animations' names or order changed"
    for a, r in zip(anims, old_rows):
        assert (a[1], a[2], len(a[5]), a[3], a[4]) == (r[3], r[4], r[5], (r[7], r[8]), r[9]), \
            f"{a[0]}: size / frames / anchor / ticks changed"
    sheet, rows = pack(anims, SHEET_W[mod])
    text = table(old_text, rows, (sheet.shape[1], sheet.shape[0]))
    runs = runs_of(anims, TWO_TONE[mod])
    if preview_to:
        preview(anims, preview_to)
    colours = len({tuple(c) for _, _, _, _, _, fr in anims for f in fr for c in f[f[..., 3] > 0][:, :3]})
    if check:
        bad = []
        old = np.array(Image.open(sheet_path).convert("RGBA"))
        if old.shape != sheet.shape or (old != sheet).any():
            bad.append(sheet_path)
        if open(atlas, encoding="utf-8").read().replace("\r\n", "\n") != text:
            bad.append(atlas)
        if open(runs_path, "rb").read() != runs:
            bad.append(runs_path)
        print("differs: " + ", ".join(bad) if bad else "the same as the installed tree's files")
        return not bad
    Image.fromarray(sheet, "RGBA").save(sheet_path, optimize=True)
    with open(atlas, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(runs_path, "wb") as f:
        f.write(runs)
    print(f"{mod}: {len(anims)} animations, sheet {sheet.shape[1]}x{sheet.shape[0]}, {colours} colours, runs {len(runs)} bytes")
    return True


def preview(anims, path, scale=4):
    pad = 6
    width = max(len(fr) * (w + pad) for _, w, h, _, _, fr in anims) + pad
    height = sum(h + pad for _, w, h, _, _, fr in anims) + pad
    img = np.zeros((height, width, 4), np.uint8)
    img[..., :3] = (52, 92, 52)
    img[..., 3] = 255
    y = pad
    for name, w, h, anchor, ticks, frames in anims:
        x = pad
        for f in frames:
            m = f[..., 3] > 0
            img[y:y + h, x:x + w][m] = f[m]
            img[y + anchor[1], x + anchor[0], :3] = (0, 0, 0)
            x += w + pad
        y += h + pad
    Image.fromarray(img, "RGBA").resize((width * scale, height * scale), Image.NEAREST).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["dump", "build"])
    ap.add_argument("--mod", required=True, choices=sorted(SHEET_W))
    ap.add_argument("--out", help="dump: the folder to write frames/ and spec.json into")
    ap.add_argument("--frames", help="build: the folder with frames/ and spec.json")
    ap.add_argument("--what-file", help="dump: a JSON of {animation: what to draw} put into spec.json")
    ap.add_argument("--preview", help="also write every frame 4x on the map's green")
    ap.add_argument("--check", action="store_true", help="build: compare with the files instead of writing them")
    a = ap.parse_args()
    if a.what == "dump":
        spec = dump(a.mod, a.out, a.what_file, a.preview)
        print(f"{a.mod}: {len(spec)} animations, {sum(s['frames'] for s in spec)} frames -> {a.out}")
    else:
        ok = build(a.mod, a.frames, a.check, a.preview)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
