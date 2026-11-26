"""league_nidalee's idle holds her spear upright (the user, 2026-11-19: 「豹女新模型待机动作也应该竖着拿枪啊 我只是改跑步时候
而已」): GPT's new model (e814e7982 .. bdbda7d47) drew the idle with the spear held across her body, the shaft from below
her screen-left hand at the hip up to the spearhead past her screen-right shoulder; the old model (main 099abf3b3) stood
it upright beside her. Only the idle's own pictures change - the four of idle_base (frame 0 = the idle's frame 0 and
every portrait / card measure, 1-3 her breathing loop); the run keeps the shoulder carry (nidalee_run_spear.py), the
attack, hit, dead and skills keep GPT's poses.

From each idle_base picture as SOURCE_REV holds it (GPT's, the same in every later revision until this tool):

1. the diagonal spear out: its centre line fitted through the shaft's clean stretches outside her body (a wood square
   with a dark one above and below, left of x 30 and at x 57-71; the line with the most squares within 1 of it over
   every pair, refitted), then the shaft-coloured squares within 2.3 of it up to x 66 and every opaque square within
   4.5 past it (binding and spearhead, clear of her). Where both sides along the line's normal are her body the square
   is filled, else cleared; a cleared square next to an uncovered light one becomes outline (the shaft was her edge
   there); bits of the spear cut off from her are cleared;
2. the strip it covered on her belly and waist filled again, with the shadow it cast there (a skin square next to it
   that is darker than the skin one step further): skin against skin is interpolated along the normal and snapped to
   the nearest skin colour around it, skin against her fur band takes the skin (the band's top edge lies under the
   shaft's far side - it does not grow into the strip), anything else takes the nearer side; a dark square left among
   light ones takes their commonest colour. Where the shaft lay right on her waist's left edge and the fur band's end
   (pictures 1 and 2) the squares in PATCH were set by hand, to the band's and the waist's shape in GPT's own drawing;
3. the upright spear drawn behind everything (her fist's fingers and her boot stay in front): GPT's own spearhead and
   binding colours (the bone blade lit on the left with its dark edge, the dark red binding with a cord groove), drawn
   square by square upright (a turned picture would be resampled), a three-square shaft of the wood colours down to
   the ground row, the tip at row TIP_ROW above her hair. It stands on the ground in the same place in all four
   pictures (MID_X: inside her screen-right fist in every one of them, though the fist moves 9 rows over her breathing
   loop - the hand slides on the planted shaft, the spear never jumps).

Every rect showing an idle_base picture gets it (frame 0's is the idle's and the BP reel's too). The lo_ frames are
sheetkit's (tools/fix/xinzhao_galio_1119/sheetkit.py) lo_ of the hd_ ones, square for square, so they are made again;
the 1x frames are not (GPT's own, 7-18 squares off sheetkit's), so they get only the change: the squares where
sheetkit's 1x of the new picture differs from its 1x of the old one. In the hd strips (assets/source/ppu[/orig]/
nidalee_*.png + .json sizes, 1 px apart) every frame that is an old picture square for square becomes the new one.

tools/art/hero_reels.json: her idle's snippets come from idle_base (the hand sliding up the shaft and back, a small
dip) instead of the attack's and the skill's first frames, which hold the spear across - run tools/art/hero_reels.py
--hero nidalee after this tool.

    python tools/fix/gpt784_review/nidalee_idle_spear.py
    python tools/fix/gpt784_review/nidalee_idle_spear.py --check
"""
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

SOURCE_REV = "bdbda7d47"
STEM = "league/champions/league_nidalee"
OUTLINE = (15, 8, 12)

# ------------------------------------------------------------------------------------------------ colours


def core(p):
    r, g, b, al = (int(v) for v in p)
    return al > 0 and 70 <= r <= 180 and r - b >= 40 and g <= 115


def dark(p):
    return p[3] > 0 and int(p[0]) + int(p[1]) + int(p[2]) < 100


def skinlike(p):
    r, g, b, al = (int(v) for v in p)
    return al > 0 and r >= 185


def skin(p):
    r, g, b = (float(v) for v in p[:3])
    return r >= 180 and 85 <= g <= 185 and 35 <= b <= 125 and r - b >= 105


def fur(p):
    r, g, b = (float(v) for v in p[:3])
    return r >= 170 and g >= 140 and b >= 100 and r - b < 105


def lum(p):
    return 0.3 * int(p[0]) + 0.59 * int(p[1]) + 0.11 * int(p[2])


# ------------------------------------------------------------------------------------------------ 1. the spear out


def fit(c):
    """y = a + b x of the diagonal shaft's centre line."""
    pts = []
    for x in range(8, 72):
        if 30 <= x < 57:
            continue
        for y in (range(55, 81) if x < 30 else range(25, 51)):
            if core(c[y, x]) and dark(c[y - 1, x]) and dark(c[y + 1, x]):
                pts.append((x, y))
    P = np.array(pts, float)
    best = None
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            (x1, y1), (x2, y2) = P[i], P[j]
            if abs(x2 - x1) < 20:
                continue
            b = (y2 - y1) / (x2 - x1)
            inl = np.abs(P[:, 1] - (y1 - b * x1 + b * P[:, 0])) <= 1.0
            if best is None or inl.sum() > best.sum():
                best = inl
    b, a = np.polyfit(P[best, 0], P[best, 1], 1)
    return a, b


def mask_of(c, a, b, W=2.3, HEAD_X=66, HEAD_W=4.5):
    h, w = c.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = (yy - a - b * xx) / np.sqrt(1 + b * b)
    op = c[..., 3] > 0
    shafty = np.zeros((h, w), bool)
    for y, x in zip(*np.nonzero(op & (np.abs(d) <= W))):
        p = c[y, x]
        shafty[y, x] = (dark(p) or core(p)) and not skinlike(p)
    return (shafty & (xx >= 4) & (xx <= HEAD_X)) | (op & (np.abs(d) <= HEAD_W) & (xx > HEAD_X)), d


def components(mask):
    lab = np.zeros(mask.shape, int)
    sizes, n = {}, 0
    h, w = mask.shape
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        st, cnt = [(y0, x0)], 0
        while st:
            y, x = st.pop()
            cnt += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        st.append((yy, xx))
        sizes[n] = cnt
    return lab, sizes


def unspear(c, a, b):
    """-> (picture without the spear, the squares filled from her body)."""
    m, d = mask_of(c, a, b)
    h, w = c.shape[:2]
    out = c.copy()
    n = np.array([-b, 1.0]) / np.sqrt(1 + b * b)
    body = (c[..., 3] > 0) & ~m

    def probe(y, x, sgn, hi=7):
        got = None
        for s_ in range(1, hi):
            xx, yy = int(round(x + sgn * n[0] * s_)), int(round(y + sgn * n[1] * s_))
            if not (0 <= yy < h and 0 <= xx < w):
                return got
            if m[yy, xx]:
                continue
            if not body[yy, xx]:
                return got if got else ("clear", s_)
            if got is None:
                got = ("body", yy, xx, s_)
                if not dark(c[yy, xx]):
                    return got
            elif not dark(c[yy, xx]) and s_ - got[3] <= 2:
                return ("body", yy, xx, s_)
            else:
                return got
        return got

    inside = np.zeros((h, w), bool)
    src = {}
    for y, x in zip(*np.nonzero(m)):
        up, dn = probe(y, x, -1), probe(y, x, +1)
        if up and dn and up[0] == "body" and dn[0] == "body":
            inside[y, x] = True
            near, far = (dn, up) if d[y, x] > 0 else (up, dn)
            pick = far if abs(d[y, x]) < 0.5 and far[3] < near[3] else near
            src[(y, x)] = (pick[1], pick[2])
    erase = m & ~inside
    out[erase] = 0
    for (y, x), (sy, sx) in src.items():
        out[y, x] = c[sy, sx]
    for (y, x) in list(src):
        if not dark(out[y, x]):
            continue
        nb = [tuple(int(v) for v in out[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
              if (dy or dx) and 0 <= y + dy < h and 0 <= x + dx < w]
        light = [q for q in nb if q[3] > 0 and not dark(q)]
        if len(light) >= 6:
            vals, cnt = np.unique(np.array(light), axis=0, return_counts=True)
            out[y, x] = vals[np.argmax(cnt)]
    lab, sizes = components(out[..., 3] > 0)
    main = max(sizes, key=sizes.get)
    bits = (lab > 0) & (lab != main) & np.isin(lab, [k for k, v in sizes.items() if v <= 12]) & (np.abs(d) <= 5)
    out[bits] = 0
    erase |= bits
    op = out[..., 3] > 0
    add = []
    for y, x in zip(*np.nonzero(erase)):
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and op[yy, xx] and not dark(out[yy, xx]):
                add.append((y, x))
                break
    for y, x in add:
        out[y, x] = (*OUTLINE, 255)
    return out, inside


# ------------------------------------------------------------------------------------------------ 2. her belly again


def refill(out, inside, a, b, ring=1, reach=7):
    h, w = out.shape[:2]
    n = np.array([-b, 1.0]) / np.sqrt(1 + b * b)
    region = inside.copy()
    for y, x in zip(*np.nonzero(inside)):
        for sgn in (-1, 1):
            for s in range(1, ring + 1):
                xx, yy = int(round(x + sgn * n[0] * s)), int(round(y + sgn * n[1] * s))
                x2, y2 = int(round(x + sgn * n[0] * (s + 1))), int(round(y + sgn * n[1] * (s + 1)))
                if not (0 <= yy < h and 0 <= xx < w and 0 <= y2 < h and 0 <= x2 < w) or inside[yy, xx]:
                    continue
                p, q = out[yy, xx], out[y2, x2]
                if p[3] and q[3] and skin(p) and skin(q) and lum(p) < lum(q) - 18:
                    region[yy, xx] = True
    res = out.copy()

    def around(y, x, r, keep):
        y0, y1, x0, x1 = max(0, y - r), min(h, y + r + 1), max(0, x - r), min(w, x + r + 1)
        nb = out[y0:y1, x0:x1][~region[y0:y1, x0:x1] & (out[y0:y1, x0:x1, 3] > 0)][:, :3]
        return [q for q in nb if keep(q)]

    for y, x in zip(*np.nonzero(region)):
        ends = []
        for sgn in (-1, 1):
            for s in range(1, reach):
                xx, yy = int(round(x + sgn * n[0] * s)), int(round(y + sgn * n[1] * s))
                if not (0 <= yy < h and 0 <= xx < w):
                    break
                if region[yy, xx]:
                    continue
                if out[yy, xx, 3] == 0:
                    break
                ends.append((s, out[yy, xx, :3].astype(float)))
                break
        if len(ends) == 1 and fur(ends[0][1]):
            nb = around(y, x, 3, skin)
            if nb:
                vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True)
                res[y, x] = (*vals[np.argmax(cnt)], 255)
            continue
        if len(ends) < 2:
            continue
        (s1, c1), (s2, c2) = ends
        if (skin(c1) and fur(c2)) or (fur(c1) and skin(c2)):
            c1 = c2 = c1 if skin(c1) else c2
        if not (skin(c1) and skin(c2)):
            res[y, x] = (*(c1 if s1 <= s2 else c2), 255)
            continue
        col = (c1 * s2 + c2 * s1) / (s1 + s2)
        nb = np.array(around(y, x, 5, skin), float)
        if len(nb):
            res[y, x] = (*nb[np.argmin(((nb - col) ** 2).sum(1))], 255)
    return res


OO, C4 = (15, 8, 12), (174, 146, 108)
W1, S9, S8, S7, S6, S5 = (111, 59, 28), (131, 60, 31), (168, 75, 40), (189, 92, 52), (208, 103, 60), (221, 121, 76)
PATCH = {   # idle_base picture -> {(x, y): colour, None = clear}
    1: {(41, 51): W1, (42, 51): S8, (40, 52): OO, (41, 52): S9, (42, 52): S8, (42, 53): S7, (43, 53): S6, (44, 53): S5,
        (41, 54): S8, (42, 54): S7, (43, 54): S6, (40, 55): OO, (41, 55): C4},
    2: {(41, 52): OO, (42, 52): S7, (43, 52): S6, (40, 53): None, (41, 53): OO, (43, 53): S6, (45, 53): S5,
        (43, 54): S6, (44, 54): S5, (41, 55): OO},
}

# ------------------------------------------------------------------------------------------------ 3. the spear upright

PAL = {"O": (15, 8, 12), "W": (251, 242, 212), "L": (248, 230, 195), "M": (228, 197, 153), "S": (174, 146, 108),
       "D": (82, 59, 58), "H": (192, 70, 40), "R": (140, 29, 20), "K": (95, 31, 20), "G": (62, 21, 14)}
HEAD = [
    "...O...",
    "..OWO..",
    "..OWO..",
    ".OWWMO.",
    ".OLWMO.",
    ".OLMSO.",
    "OLWMMSO",
    "OLMMMSO",
    "OLMMSDO",
    ".OMMSO.",
    ".OMSDO.",
    "..OSO..",
    "..ODO..",
    ".OHRKO.",
    ".ORRKO.",
    ".OGGGO.",
    ".OHRKO.",
    ".ORRKO.",
    ".OKKKO.",
]
WOOD = [(153, 80, 32), (153, 80, 32), (171, 101, 40), (153, 80, 32), (135, 78, 33), (135, 78, 33), (111, 59, 28),
        (135, 78, 33), (153, 80, 32), (144, 97, 47), (153, 80, 32), (135, 78, 33)]
TIP_ROW, MID_X, GROUND = 1, 68, 99


def upright(c):
    s = np.zeros_like(c)
    for r, line in enumerate(HEAD):
        for k, ch in enumerate(line):
            if ch != ".":
                s[TIP_ROW + r, MID_X - 3 + k] = (*PAL[ch], 255)
    for y in range(TIP_ROW + len(HEAD), GROUND + 1):
        s[y, MID_X - 1] = s[y, MID_X + 1] = (*PAL["O"], 255)
        s[y, MID_X] = (*WOOD[(y - TIP_ROW - len(HEAD)) % len(WOOD)], 255)
    s[GROUND, MID_X] = (*PAL["O"], 255)
    out = c.copy()
    free = (c[..., 3] == 0) & (s[..., 3] > 0)
    out[free] = s[free]
    return out


def redraw(c, i):
    """GPT's idle_base picture i -> the one with the spear upright."""
    a, b = fit(c)
    out, inside = unspear(c, a, b)
    out = refill(out, inside, a, b)
    for (x, y), col in PATCH.get(i, {}).items():
        out[y, x] = (0, 0, 0, 0) if col is None else (*col, 255)
    return upright(out)


# ------------------------------------------------------------------------------------------------ the sheet


def source():
    """SOURCE_REV's sheet pixels and anims."""
    def show(path):
        return subprocess.run(["git", "show", f"{SOURCE_REV}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout
    px = np.asarray(Image.open(io.BytesIO(show(STEM + "#sheet.png"))).convert("RGBA"))
    return px, json.loads(show(STEM + "#anim.fanim").decode("utf-8-sig"))["anims"]


def cell(px, anims, tag, i):
    d = anims[tag]["frames"][i]["data"]
    x, y, w, h = (int(round(d[q])) for q in "xywh")
    return px[y:y + h, x:x + w].copy()


def strips(swap):
    done = []
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        for fn in sorted(os.listdir(d)):
            if not (fn.startswith("nidalee_") and fn.endswith(".png")):
                continue
            path = os.path.join(d, fn)
            st = np.asarray(Image.open(path).convert("RGBA")).copy()
            x, n = 0, 0
            for w, h in json.load(open(path[:-4] + ".json"))["sizes"]:
                new = swap.get((st[:h, x:x + w].tobytes(), (h, w)))
                if new is not None:
                    st[:h, x:x + w] = new
                    n += 1
                x += w + 1
            if n:
                Image.fromarray(st).save(path)
                done.append(f"{sub + '/' if sub else ''}{fn[:-4]} {n}")
    return done


def main():
    check = "--check" in sys.argv
    k = Kit(ROOT, "league", "nidalee")
    spx, san = source()
    wrong, swap, first = [], {}, {}
    for i in range(len(k.anims["hd_idle_base"]["frames"])):
        old = cell(spx, san, "hd_idle_base", i)
        key = (old.tobytes(), old.shape[:2])
        first.setdefault(key, i)                    # idle_base[4] / [5] are [1] / [0] again: PATCH by the first
        new = redraw(old, first[key])
        swap[key] = new
        one_shape = k.cell("idle_base", i).shape
        want = {"hd_idle_base": new}
        for lo, tag in ((False, "idle_base"), (True, "lo_idle_base")):
            f = k.lo_of if lo else k.one_of
            a, b = f(one_shape, old), f(one_shape, new)
            if a.shape != b.shape:
                sys.exit(f"nidalee idle spear: {tag}[{i}] changed size ({a.shape} -> {b.shape})")
            pic = cell(spx, san, tag, i)
            if pic.shape != b.shape:
                sys.exit(f"nidalee idle spear: {tag}[{i}] is {pic.shape[:2]}, sheetkit makes {b.shape[:2]}")
            moved = (a != b).any(-1)
            pic[moved] = b[moved]
            want[tag] = pic
        for tag, pic in want.items():
            if not np.array_equal(k.cell(tag, i), pic):
                wrong.append(f"{tag}[{i}]")
                if not check:
                    k.put(tag, i, pic)
    if check:
        print("nidalee idle spear: OK" if not wrong else f"nidalee idle spear: {len(wrong)} frames not drawn yet "
              f"({', '.join(wrong[:6])}) - run tools/fix/gpt784_review/nidalee_idle_spear.py")
        sys.exit(1 if wrong else 0)
    if wrong:
        k.save()
    print(f"nidalee idle spear: {len(wrong)} frames written ({', '.join(wrong)})")
    print("nidalee idle spear: strips " + (", ".join(strips(swap)) or "already done"))


if __name__ == "__main__":
    main()
