"""league_nasus's ears drawn again and his outline cleaned, in every hd_ frame (the user, 2026-11-19: 「狗头的右耳朵我还感觉
少了一块」, 「狗头的耳朵画精致一点啊」, then 「还有狗头的黑边处理干净点」).

The ears. GPT's were two near-black spikes: the far one two or three squares wide, the near one a one-square line whose
outline lost squares in most frames (the piece the user missed). Now each form has one pair, drawn square by square
(EARS: the base form at PPU 1.2 and the bigger R form), in the frame's own colours:

- outlined, the far ear's fur inside, the near ear's inner ear in two dark reds - the darker above, the brighter at the
  base - as League's Nasus shows it from this side; where an ear is only two squares wide (by the tip) its front square
  is lit fur, not outline (an outline square there would have no body square beside it: tools/art/thin_outline.py
  clears those); the tips stay on the rows GPT's tips were on in the idle, so he is no taller;
- they stand on the head at one place for every frame of a form: the ears' base row BASE rows above his eye (the left
  square of the eye, found by matching the idle's head - crown, eye, snout - on each frame), so they never stretch or
  jump from frame to frame (GPT's stood one or two rows higher or lower from frame to frame);
- what GPT drew above the frame's own crown (its first row 6 squares wide, 7 in the R form) in the ears' columns and
  touching the head is cleared first; where the head reaches above the ears' base only the ears' inside colours are
  drawn over it (no outline inside the head), where it starts below, the base's inside colours are carried down to it;
- the colours are each frame's own: its darkest colour for the outline, its crown's fur for F / M (35th / 85th
  percentile of lightness), its colours nearest the inner-ear reds for I / J - the run frames are drawn in cooler greys
  than the others and keep them;
- the six frames where the head is bowed under the raised staff or thrown back (nasus_ears.json "kept") keep GPT's
  ears: his arms hide them.

The outline (clean()): GPT left the edge of the body without outline in places (the pauldrons' tops, the forearms,
the snout), the outline two squares deep where a near-black shade (Lab L under INK_L) lies under it, and lone squares
off the body. Until nothing changes:

1. a square on the edge of the figure (a clear square or the frame's border beside it) that is not outline becomes
   outline when the body goes on inside it (an inside square beside it), unless it glows (the staff's fire): a part one
   or two squares thin keeps its colour;
2. the outline more than one square from the body is cleared from the outside in (thin_outline.py's own pass), the
   near-black shades counted as outline for it: a band of outline and shade loses its outer square, so the outline is
   one square deep all round (thin_outline.json: KEEP 1 for his hd_ frames) - his silhouette shrinks by that square
   there, as thin_outline.py's own runs did for every hero;
3. inside a black area thicker than a line (a black square whose four neighbours are all outline or near-black shade:
   the shoulder and neck GPT painted solid black beside the head in the Q and attack blow, 「放Q的时候头部有个黑色阴影块
   没处理干净 头旁边」, 3-6 squares deep), each square takes the colour of the nearest lit body square (steps through the
   dark), DARKER Lab L darker, snapped to the frame's own lit colours: a shadow of what is round it, the black line round
   it kept;
4. a square with no neighbour at all goes, and a speck of at most SPECK squares off the body (not a spark of the
   staff's fire);
5. thin_outline.py's pass with his stored parameters, so its CI check stays as it was.

nasus_ears.json holds, for each picture with ears, its rects in the sheet (the idle and BP reels share them; the rects,
not tag frames, since tools/fix/gpt784_review/nasus_actions.py plays the pictures in other tags), the eye, the frame's
own crown row, the form and the colours, read once from GPT's frames. Only pictures some tag plays are touched. The 1x and lo_ frames are made from
the hd_ ones by other passes than tools/fix/xinzhao_galio_1119/sheetkit.py's (215 of his 342 differ from its
derivation by a few dozen squares: thin_outline.py), so they get only the change: the squares where sheetkit's 1x /
lo_ of the new hd_ frame differ from its 1x / lo_ of the old one. In the hd strips (assets/source/ppu[/orig]/nasus_*.png
+ .json sizes, 1 px apart) every frame that is one of the old pictures square for square becomes the new one: the
strips are not one per sheet tag (nasus_idle.png holds the 8 idle_base pictures, the sheet's idle is the 16-frame
reel), so a strip is never rewritten whole.

    python tools/fix/gpt784_review/nasus_clean.py            # from GPT's frames (the sheet as #784 left it)
    python tools/fix/gpt784_review/nasus_clean.py --check    # every hd_ picture clean, every picture with ears drawn
"""
import hashlib
import importlib.util
import json
import os
import sys

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nasus_ears.json")
OUTLINE = (4, 3, 1)
INK_L = 9.5        # Lab L under which a shade counts as outline when the band is thinned
DARKER = 6.0       # Lab L a filled black square is below the lit square it takes after
SPECK = 3          # squares a piece off the body may have and still go

_spec = importlib.util.spec_from_file_location("thin_outline", os.path.join(ROOT, "tools", "art", "thin_outline.py"))
th = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(th)
TP = th.load_state()["league_nasus"]

# tip row first, the ears' base row last; column 0 is DX0 squares left of the eye. O outline, F fur, M lit fur,
# I inner ear, J brighter inner ear, . the frame's own square
EARS = {
    "n": [
        "...O...O..",
        "..OF..OM..",
        "..OF.OIM..",
        ".OFM.OIM..",
        ".OFMOIJM..",
        "OFFMOIJO..",
    ],
    "b": [
        "....O...OO..",
        "...OFM.OIM..",
        "..OFFM.OIM..",
        "..OFFMOIIM..",
        ".OFFFMOIJM..",
        ".OFFFMOIJM..",
        "OFFFFMOIJO..",
    ],
}
DX0 = {"n": -5, "b": -7}
BASE = {"n": 4, "b": 6}
CLEAR_ABOVE = 6    # rows above the tips still cleared (GPT's tips stood up to two rows higher)
CARRY = 4          # at most this many rows the base is carried down to a head that starts lower


def label(mask):
    """8-connected components of a boolean mask -> labels (0 = background)."""
    h, w = mask.shape
    lab = np.zeros((h, w), int)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        stack = [(y0, x0)]
        while stack:
            y, x = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
    return lab


def draw(c, ex, ey, own, form, pal):
    """Frame c with the ears of `form` on the head whose eye is (ex, ey); own: the frame's crown row."""
    rows = EARS[form]
    out = c.copy()
    h, w = c.shape[:2]
    base = ey - BASE[form]
    top = base - (len(rows) - 1)
    x0, x1 = max(0, ex + DX0[form] - 2), min(w, ex + DX0[form] + len(rows[0]) + 2)
    zone = np.zeros((h, w), bool)
    zone[max(0, min(top, own) - CLEAR_ABOVE):own, x0:x1] = True
    opaque = c[..., 3] > 0
    lab = label(opaque & (zone | (np.arange(h)[:, None] == own)))
    head = set(lab[own, x0:x1][lab[own, x0:x1] > 0].tolist())
    out[zone & opaque & np.isin(lab, list(head))] = 0
    body = out[..., 3] > 0
    for r, line in enumerate(rows):
        y = top + r
        for k, role in enumerate(line):
            x = ex + DX0[form] + k
            if role == "." or not (0 <= y < h and 0 <= x < w) or (body[y, x] and role == "O"):
                continue
            out[y, x] = (*pal[role], 255)
            if r == len(rows) - 1 and role != "O":
                yy = y + 1
                while yy < h and yy <= y + CARRY and not body[yy, x]:
                    out[yy, x] = (*pal[role], 255)
                    yy += 1
    return out


def lab_l(c):
    c = np.asarray(c, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    y = c @ np.array([0.2126, 0.7152, 0.0722])
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def glows(a):
    r, g, b = (a[..., k].astype(int) for k in range(3))
    return (a[..., 3] > 0) & (r > 120) & (r - b > 70) & (g > 45)


def four(m, pad):
    """For each square: any of its four neighbours set (outside the frame counts as `pad`)."""
    p = np.pad(m, 1, constant_values=pad)
    return p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def fill_black(a):
    """The inside of thick black areas -> the dark of the nearest lit body colour (step 3)."""
    op = a[..., 3] > 0
    ink = op & (lab_l(a[..., :3]) < INK_L)
    p = np.pad(ink, 1, constant_values=False)
    inside = op & (a[..., :3] == OUTLINE).all(-1) & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    if not inside.any():
        return a
    lit = op & ~ink
    h, w = op.shape
    src = np.full((h, w, 2), -1, int)
    ys, xs = np.nonzero(lit)
    src[ys, xs, 0], src[ys, xs, 1] = ys, xs
    front, seen = lit.copy(), lit.copy()
    while front.any():
        nxt = np.zeros_like(front)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            moved_f = np.zeros_like(front)
            moved_s = np.full_like(src, -1)
            ys0, ys1 = max(0, dy), h + min(0, dy)
            xs0, xs1 = max(0, dx), w + min(0, dx)
            moved_f[ys0:ys1, xs0:xs1] = front[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            moved_s[ys0:ys1, xs0:xs1] = src[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
            new = moved_f & ~seen & ink
            src[new] = moved_s[new]
            seen |= new
            nxt |= new
        front = nxt
    pal = np.unique(a[lit][:, :3], axis=0)
    if not len(pal):
        return a
    pl = lab(pal)
    out = a.copy()
    for y, x in zip(*np.nonzero(inside)):
        sy, sx = src[y, x]
        if sy < 0:
            continue
        t = lab(a[sy, sx, :3])
        t[0] = max(0.0, t[0] - DARKER)
        out[y, x, :3] = pal[int(np.argmin(((pl - t) ** 2 * np.array([1.0, 0.5, 0.5])).sum(1)))]
    return out


def specks(a):
    """Opaque pieces of at most SPECK squares off the figure's biggest piece, none of them fire."""
    op = a[..., 3] > 0
    lab_ = label(op)
    n = lab_.max()
    if n < 2:
        return a
    sizes = np.bincount(lab_.ravel())
    sizes[0] = 0
    g = glows(a)
    out = a.copy()
    for k in range(1, n + 1):
        if sizes[k] <= SPECK and k != int(np.argmax(sizes)) and not (g & (lab_ == k)).any():
            out[lab_ == k] = 0
    return out


def clean_once(a):
    a = a.copy()
    op = a[..., 3] > 0
    is_o = op & (a[..., :3] == OUTLINE).all(-1)
    edge = op & four(~op, True)
    # 1. the body's edge becomes outline where the body goes on inside it
    to_o = edge & ~is_o & ~glows(a) & four(op & ~edge, False)
    a[to_o, :3] = OUTLINE
    # 2. outline (and near-black shade) more than one square from the body goes, from the outside in
    shade = op & (lab_l(a[..., :3]) < INK_L) & ~(a[..., :3] == OUTLINE).all(-1)
    cols = [list(OUTLINE)] + [list(map(int, c)) for c in np.unique(a[shade][:, :3], axis=0)]
    a = th.thin_ring(a, cols, TP["hd"]["keep"], TP["hd"]["deep"])[0]
    # 3. the inside of thick black areas
    a = fill_black(a)
    # 4. a square with no neighbour at all, a speck off the body
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    n8 = sum(p[1 + dy:1 + dy + op.shape[0], 1 + dx:1 + dx + op.shape[1]].astype(int)
             for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    a[op & (n8 == 0) & ~glows(a)] = 0
    a = specks(a)
    # 5. thin_outline.py's own pass
    return th.change_fixed(a, TP["hd"], TP["outline"], TP["grow"])[0]


def clean(a):
    for _ in range(16):
        b = clean_once(a)
        if np.array_equal(a, b):
            return b
        a = b
    raise SystemExit("nasus clean: the outline pass reaches no fixed point")


def moved(k, one_shape, old, new, lo):
    """sheetkit's 1x (or lo_) frame of `new` where it differs from that of `old`: (mask, picture)."""
    f = k.lo_of if lo else k.one_of
    a, b = f(one_shape, old), f(one_shape, new)
    if a.shape != b.shape:
        raise SystemExit(f"nasus clean: the {'lo_' if lo else '1x'} frame changed size ({a.shape} -> {b.shape})")
    return (a != b).any(-1), b


def strips(swap):
    """Every strip frame that is a key of swap ((bytes, shape) of an old picture) -> its new picture."""
    from PIL import Image
    done = []
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        for fn in sorted(os.listdir(d)):
            if not (fn.startswith("nasus_") and fn.endswith(".png")):
                continue
            path = os.path.join(d, fn)
            st = np.asarray(Image.open(path).convert("RGBA")).copy()
            sizes = json.load(open(path[:-4] + ".json"))["sizes"]
            x, n = 0, 0
            for w, h in sizes:
                new = swap.get((st[:h, x:x + w].tobytes(), (h, w)))
                if new is not None:
                    st[:h, x:x + w] = new
                    n += 1
                x += w + 1
            if n:
                Image.fromarray(st).save(path)
                done.append(f"{sub + '/' if sub else ''}{fn[:-4]} {n}")
    return done


def pictures(k):
    """[[(tag, frame) of the hd_ frames showing one picture]], in the sheet's tag order."""
    seen = {}
    for t in sorted(k.anims):
        if t.startswith("hd_"):
            for i in range(len(k.anims[t]["frames"])):
                c = k.cell(t, i)
                seen.setdefault(hashlib.sha1(c.tobytes() + bytes(str(c.shape), "ascii")).hexdigest(), []).append((t, i))
    return list(seen.values())


def main():
    check = "--check" in sys.argv
    k = Kit(ROOT, "league", "nasus")
    table = json.load(open(TABLE, encoding="utf-8"))
    ears = {tuple(r): e for e in table["frames"] for r in e["rects"]}
    todo, swap, tags, squares = 0, {}, set(), 0
    for rects in pictures(k):
        if all(t in ("hd_skill_w", "hd_b_skill_w") for t, _ in rects) and                 not any(k.rect(t, i) in ears for t, i in rects):
            continue                     # nasus_w.py's raised-arm pictures: that tool cleans them its own way
        old = k.cell(*rects[0])
        e = next((ears[k.rect(t, i)] for t, i in rects if k.rect(t, i) in ears), None)
        new = draw(old, *e["eye"], e["own"], e["form"], {r: tuple(v) for r, v in e["pal"].items()}) if e else old
        new = clean(new)
        if np.array_equal(old, new):
            continue
        todo += 1
        squares += int((old != new).any(-1).sum())
        swap[(old.tobytes(), old.shape[:2])] = new
        if check:
            continue
        for t, i in rects:
            k.put(t, i, new)
            plain = t[3:]
            one_shape = k.cell(plain, i).shape
            for lo, tag in ((False, plain), (True, "lo_" + plain)):
                mask, pic = moved(k, one_shape, old, new, lo)
                cur = k.cell(tag, i)
                if cur.shape != pic.shape:
                    raise SystemExit(f"nasus clean: {tag}[{i}] is {cur.shape[:2]}, sheetkit makes {pic.shape[:2]}")
                cur[mask] = pic[mask]
                k.put(tag, i, cur)
            tags.add(plain)
    if check:
        print("nasus clean: OK" if not todo else f"nasus clean: {todo} pictures not done - run "
              "tools/fix/gpt784_review/nasus_clean.py")
        sys.exit(1 if todo else 0)
    k.save()
    print(f"nasus clean: {todo} pictures, {squares} hd squares changed; tags {', '.join(sorted(tags))}")
    print("nasus clean: strips " + ", ".join(strips(swap)))


if __name__ == "__main__":
    main()
