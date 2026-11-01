"""Ban/pick grid card check for every League hero, the game's own math (0.6.4 exe, read 2026-10-17).

    python tools/art/bp_card_audit.py                          # a table: every hero's card value, the rule's, the head's gap
    python tools/art/bp_card_audit.py --mock out.png janna=-2,-3 galio=n,0 ...   # cards side by side (n = no value)
    python tools/art/bp_card_audit.py --legs                   # how much of each hero hides under the canvas (1x px)
    python tools/art/bp_card_audit.py --centers [tft]          # the encyclopedia card: each hero's center, the rule's

The grid card's top 131 x 88 px is a canvas: the idle frame's CENTRE goes to the canvas's bottom middle
+ 2.2 * banpick_center (game px, up negative), drawn 2.2x its size; HD heroes (lo_ frames) draw lo_idle at 2.2 / 1.5.
With a value the picture is clipped to the canvas; without one the hero stands like -12 and is not clipped (a tall one
sticks out over the card's top edge). Base's rule for tall heroes: y = -39 - top, top = the highest opaque row over the
frame centre on the highest-reaching idle frame (1x px), so the head sits 1 game px under the canvas top; a hero whose
top is at or above -28 needs a value (league_talon). Never a positive value (league_masteryi's +5 drew his card at 1x).
Measure the head, not a thin prop over it: the table's rule takes the highest row of anything, so a spear or sword tip
(league_jarvaniv -10, league_masteryi -4) shows as CLIPPED on purpose. Checked on the user's 1920 x 1080 screenshot of
league_janna's card (2026-10-18): the lo_idle frame matched at 2.2 / 1.5 with its centre where the formula puts it.

The encyclopedia's tier-list card (`champion_info_component/champion_slot`; the user, 2026-11-01: 「tft英雄在游戏百科里
都摆的不对 学习一下英雄联盟怎么摆的和设置的」), measured on the user's screenshot of 12 cards: the idle (lo_idle / 1.5,
the plain UI size, no UI_SIZES) is placed by its champion_view `center` - that point goes to a fixed spot about 37 game
px under the picture's top, and the tier dropdown hides everything from about 2 px under it. So `center` frames the
card. League keeps the idle's solid top (the first row at least CENTER_SOLID px wide, over the soles) a median 26.7 px
over its center: -12 for a 36-40 px hero, less deep for the low beasts (league_kogmaw, league_chogath, league_naafiri
-10), deeper only for the tall ones (-14 to -20). The TFT heroes had it at their bodies' middle (-15 to -22) and showed
4 to 13 px low, half under the dropdown; `--centers` gives the rule's value, round(solid top - League's median) within
League's own range CENTER_RANGE. In battle `center` is where hits land (the health bar hangs under the soles).
"""
import argparse
import json
import math
import os
import re

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
LEAGUE = os.path.normpath(os.path.join(HERE, "..", "..", "league"))
TFT = os.path.normpath(os.path.join(HERE, "..", "..", "tft"))
# the encyclopedia rule: the first row this wide (game px) is the idle's solid top; League's own range of center y
CENTER_SOLID = 8
CENTER_RANGE = (-20, -6)
CW, CH, S = 131, 88, 2.2
BG, OUT = (25, 41, 47, 255), (8, 8, 10, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def ui_sizes(league):
    """league.dll's UI_SIZES (addons/league_main/src/hd.rs): tall HD heroes drawn smaller in the UI."""
    rs = os.path.join(os.path.dirname(league), "addons", "league_main", "src", "hd.rs")
    src = open(lp(rs), encoding="utf-8").read()
    body = src[src.index("pub const UI_SIZES"):]
    body = body[:body.index("];")]
    return {h: float(k) for h, k in re.findall(r'\("(\w+)", ([0-9.]+)\)', body)}


def frames(league, hid, sized=True):
    """The idle frames the card draws and their scale to 1x (lo_idle / 1.5 for HD heroes, / 1.5 / UI_SIZES size for
    the tall ones league.dll draws smaller; `sized` False: the encyclopedia's plain UI size)."""
    fa = os.path.join(league, "champions", hid + "#anim.fanim")
    if not os.path.exists(lp(fa)):
        return None, None
    d = json.load(open(lp(fa), encoding="utf-8-sig"))["anims"]
    size = ui_sizes(league).get(hid, 1.0) if sized else 1.0
    tag, div = ("lo_idle", 1.5 / size) if "lo_idle" in d else ("idle", 1.0)
    sheet = Image.open(lp(os.path.join(league, "champions", hid + "#sheet.png"))).convert("RGBA")
    out = []
    for f in d[tag]["frames"]:
        b = f["data"]
        x, y, w, h = (int(round(b[k])) for k in ("x", "y", "w", "h"))
        out.append(sheet.crop((x, y, x + w, y + h)))
    return out, div


def reach(fr, div):
    """(top, bottom) of the opaque rows over the frame centre, 1x px (up negative)."""
    bb = fr.getchannel("A").point(lambda a: 255 if a > 128 else 0).getbbox()
    h = fr.size[1]
    return (bb[1] - h / 2) / div, (bb[3] - h / 2) / div


def solid_top(fr, div):
    """The idle's solid top over the soles (1x game px, up negative): the first row at least CENTER_SOLID px wide. The
    soles are 12 px under the frame centre (base's default center -12 is the frame centre)."""
    a = fr.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    w, h = a.size
    px = a.load()
    for y in range(h):
        if sum(1 for x in range(w) if px[x, y]) / div >= CENTER_SOLID:
            return (y - h / 2) / div - 12
    return None


def views(pack):
    view = json.load(open(lp(os.path.join(pack, "style", "champion_view.champion_view")), encoding="utf-8-sig"))
    return view["entries"]


def center_gap(league):
    """League's median of (solid top - center), game px: how far over its center a League hero's solid top sits."""
    gaps = []
    for hid, v in views(league).items():
        frs, div = frames(league, hid, sized=False) if hid.startswith("league_") else (None, None)
        top = solid_top(frs[0], div) if frs else None
        if top is not None:
            gaps.append(top - v["center"]["y"])
    gaps.sort()
    n = len(gaps)
    return (gaps[(n - 1) // 2] + gaps[n // 2]) / 2


def center_rule(top, gap):
    """center y for an idle whose solid top is `top`: framed like League's, within League's own range."""
    return max(CENTER_RANGE[0], min(CENTER_RANGE[1], round(top - gap)))


def centers(league, pack):
    gap = center_gap(league)
    print("League's solid top sits %.2f game px over its center (median); rule = round(solid - that), %d..%d"
          % (gap, *CENTER_RANGE))
    print("%-16s %5s %5s %7s  %s" % ("hero", "now", "rule", "solid", "flag"))
    for hid, v in sorted(views(pack).items()):
        frs, div = frames(pack, hid, sized=False)
        top = solid_top(frs[0], div) if frs else None
        if top is None:
            continue
        now, rule = v["center"]["y"], center_rule(top, gap)
        flag = "LOW" if now < rule - 1 else "HIGH" if now > rule + 1 else ""
        print("%-16s %5d %5d %7.1f  %s" % (hid, now, rule, top, flag))


def card(fr, div, y):
    """The card's canvas (and 40 px over it when there is no value) with the frame drawn the game's way."""
    pad = 0 if y is not None else 40
    img = Image.new("RGBA", (CW, CH + pad), OUT)
    img.paste(BG, (0, pad, CW, CH + pad))
    k = S / div
    big = fr.resize((max(1, round(fr.size[0] * k)), max(1, round(fr.size[1] * k))), Image.NEAREST)
    cy = pad + CH + S * (-12 if y is None else y)
    img.paste(big, (round(CW / 2 - big.size[0] / 2), round(cy - big.size[1] / 2)), big)
    return img


def heroes(league):
    view = json.load(open(lp(os.path.join(league, "style", "champion_view.champion_view")), encoding="utf-8-sig"))
    return {k: v for k, v in view["entries"].items() if k.startswith("league_")}


def table(league):
    print("%-14s %5s %5s %7s %8s  %s" % ("hero", "now", "rule", "top", "gap px", "flag"))
    for hid, v in sorted(heroes(league).items()):
        frs, div = frames(league, hid)
        if not frs:
            continue
        top = min(reach(f, div)[0] for f in frs)
        now = v.get("banpick_center", {}).get("y")
        rule = None if top > -28 else round(-39 - top)
        gap = CH + S * (-12 if now is None else now) + S * top      # the highest row's distance under the canvas top
        flag = []
        if gap < 0:
            flag.append("CLIPPED" if now is not None else "STICKS OUT")
        if now is not None and gap > 2.5 * S:
            flag.append("LOW")
        print("%-14s %5s %5s %7.1f %8.1f  %s" % (hid[7:], now, rule, top, gap, " ".join(flag)))


def legs(league, least=0.0):
    """Per hero: how much of the idle hides under the canvas (behind the name bar), 1x px - bottom + y."""
    sizes = ui_sizes(league)
    print("%-14s %5s %6s %7s %7s %7s" % ("hero", "now", "size", "top", "bottom", "hidden"))
    for hid, v in sorted(heroes(league).items()):
        frs, div = frames(league, hid)
        if not frs:
            continue
        top = min(reach(f, div)[0] for f in frs)
        bot = max(reach(f, div)[1] for f in frs)
        now = v.get("banpick_center", {}).get("y")
        hidden = bot + (-12 if now is None else now)
        if hidden >= least:
            print("%-14s %5s %6s %7.1f %7.1f %7.1f" % (hid[7:], now, sizes.get(hid, ""), top, bot, hidden))


def mock(league, out, specs, cols=5):
    items = [(h, ys.split(",")) for h, ys in (s.split("=") for s in specs)]
    pw, th = CW * 2 + 6, CH + 40
    sheet = Image.new("RGBA", (cols * (pw + 14), math.ceil(len(items) / cols) * (th + 16)), (40, 40, 44, 255))
    dr = ImageDraw.Draw(sheet)
    for k, (hid, ys) in enumerate(items):
        frs, div = frames(league, "league_" + hid)
        hi = min(range(len(frs)), key=lambda i: reach(frs[i], div)[0])
        x0, y0 = (k % cols) * (pw + 14), (k // cols) * (th + 16)
        dr.text((x0 + 2, y0 + 2), hid + "  " + " -> ".join("none" if y == "n" else y for y in ys), fill=(255, 255, 255, 255))
        for i, y in enumerate(ys[:2]):
            c = card(frs[hi], div, None if y == "n" else int(y))
            t = Image.new("RGBA", (CW, th), OUT)
            t.paste(c, (0, th - c.size[1]))
            sheet.paste(t, (x0 + i * (CW + 6), y0 + 16))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--league", default=LEAGUE)
    ap.add_argument("--mock", help="write before/after cards for hero=y1,y2 ... (n = no value)")
    ap.add_argument("--legs", nargs="?", type=float, const=0.0, help="rows hidden under the canvas (only those >= N)")
    ap.add_argument("--centers", nargs="?", const=TFT, help="the encyclopedia card's center, rule vs now (a pack folder)")
    ap.add_argument("specs", nargs="*")
    a = ap.parse_args()
    if a.mock:
        mock(a.league, a.mock, a.specs)
    elif a.legs is not None:
        legs(a.league, a.legs)
    elif a.centers:
        centers(a.league, a.centers)
    else:
        table(a.league)


if __name__ == "__main__":
    main()
