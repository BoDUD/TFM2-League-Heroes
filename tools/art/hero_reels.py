"""Every hero's idle and ban/pick card reel cut from the frames the sheet already has (the user, 2026-10-22:
「BP页面的动图可以随便切动画帧里面的动作来做吧 包括待机的时候」, then 「待机时候那个上下摆动也可以换成这个BP界面的思路了吧」).

    python tools/art/hero_reels.py                      # write every hero's idle / bp tags (league/ and tft/)
    python tools/art/hero_reels.py --hero garen,jinx    # only these
    python tools/art/hero_reels.py --check              # exit 1 when a .fanim is not what this would write
    python tools/art/hero_reels.py --list               # each hero's picks (snippets, card actions, held frames)
    python tools/art/hero_reels.py --preview out.gif --hero garen,jinx [--card]   # the idles (or the cards) as a GIF

No pixel is drawn or moved: a new tag is a list of rects the sheet already holds, so every frame looks exactly as it does
in its own action. Per hero, and per form idle (c_idle, m_idle ... with that form's actions):

- `idle_base` (c_idle_base ...): the idle as it was drawn - the breathing loop, no longer played (the user, 2026-10-22:
  「上下摆动全不要了啊」). Written once; every later run starts from it, so the tool can run again after a sheet is
  rebuilt or repacked.
- `idle`: the idle's frame 0 held 0.8-3.2 s, a snippet, five times in one cycle, the holds and the order of the snippets
  shuffled per hero (fixed by a hash of its id) so they pop up like League's idle variants. A snippet is a few frames of
  one of the hero's actions that stay where the idle stands - feet on the idle's ground row, the legs over the idle's
  legs, nothing wider than the idle +- 8 px or higher than its top + 12 (a raised weapon) - played in, held, played
  back out (a sword lifted and lowered, a gun checked); the first is near the idle (a cut, not a jump). Frame 0 stays
  the idle's frame 0 (portraits, face crops, the cards' measures read it).
- `bp`: what the ban/pick grid card plays instead of the idle (league.dll src/lookup.rs): frame 0 held, an action (attack,
  skill, skill2, ult in turn, each hero starting at a different one so a page of cards does not strike at once), then
  frame 0, a snippet, ... Card math as tools/art/bp_card_audit.py (131 x 88 canvas, 2.2x, banpick_center; hd_ frames at
  the hero's UI size): an action frame that spills out of the card more than the idle does holds the frame before it;
  an action whose first frame or more than 40 % of frames spill is left out.

A hero's first run adds tags to its .fanim (idle_base, bp and their hd_ / lo_ copies): run
addons/league_viego_soul/make_override.py after it, so Viego's soul table lists them (its test
every_soul_has_its_sheets_tags wants each sheet's tags exactly).

Dense heroes get the same lists in hd_ and lo_ (the frames' own rects there; every tag has the same frames in all
three). tools/art/hero_reels.json holds the picks made by eye where the rules pick badly:
`{"league_x": {"idle": [["skill", [0, 1]], ...], "c_idle": [...], "bp": ["attack", "ult"], "bp_cut": {"ult": [3, 4]}}}`
- a list of [action, frames] snippets for an idle ([action, frames, "fwd"]: played forward only; [] keeps frame 0 alone), the card's actions in order, and
action frames held on the card besides the spilling ones.
"""
import argparse
import hashlib
import json
import random
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PACKS = ("league", "tft")
PICKS = os.path.join(HERE, "hero_reels.json")
PREFIXES = ("", "hd_", "lo_")
CORE = ("attack", "skill", "skill2", "ult")
CW, CH, S = 131, 88, 2.2          # the ban/pick card's canvas and scale (bp_card_audit.py)
# a card frame may lose this much more past the card's sides than the idle does, and this much over its top (a weapon's
# tip; a leap loses more): (a card that clips its picture - banpick_center set -, one that does not and so draws over
# its neighbours and the row above)
ASIDE = {True: 0.12, False: 0.03}
ABOVE = {True: 0.25, False: 0.15}
STILL_S = 1.5                     # the idle's frame 0 held between card actions, seconds
IDLE_TURNS = 5                    # snippets in one idle cycle (holds of 0.8-3.2 s before each)
HOLD_S = 0.45                     # a snippet's last frame held
MIN_DUR = 0.12                    # a snippet frame at least this long (the idle is calm)
# tags never cut into an idle: they move the hero away, are effects, or are not the hero standing
NOT_SNIPPET = re.compile(r"(^|_)(run|hit|dead|idle|walk|fly|transform|revert|hatch|egg|land|dash|leap|hop|blink|exit|"
                         r"back|passive|possess|base|bp|roll|flip|pounce|ride|arrive|gate|charge)($|_)|fx\d|^tf_|^t_")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hd_rs():
    """league.dll's dense heroes {id: PPU} and UI_SIZES {id: size} (addons/league_main/src/hd.rs)."""
    src = open(lp(os.path.join(REPO, "addons", "league_main", "src", "hd.rs")), encoding="utf-8").read()
    ppu = {h: float(p) for h, p in re.findall(r'\("((?:league|tft)_\w+)", ([0-9.]+), include_str!\("[^"]*/champions/', src)}
    body = src[src.index("pub const UI_SIZES"):]
    body = body[:body.index("];")]
    return ppu, {h: float(k) for h, k in re.findall(r'\("(\w+)", ([0-9.]+)\)', body)}


PPU, UI_SIZES = hd_rs()


class Hero:
    def __init__(self, pack, hid):
        self.pack, self.id = pack, hid
        cdir = os.path.join(REPO, pack, "champions")
        self.fanim = os.path.join(cdir, hid + "#anim.fanim")
        self.raw = open(lp(self.fanim), "rb").read()
        self.anims = json.loads(self.raw.decode("utf-8-sig"))["anims"]
        self.sheet = np.array(Image.open(lp(os.path.join(cdir, hid + "#sheet.png"))).convert("RGBA"))
        self.dense = hid in PPU
        view = views(pack).get(hid, {})
        bc = view.get("banpick_center")
        self.by, self.clip = (bc["y"], True) if bc else (-12, False)
        self.card = S * UI_SIZES.get(hid, 1.0)       # 1x frames' pixels -> card pixels
        self.forms = sorted({t[:-4] for t in self.anims if t.endswith("_idle") and not t.startswith(("hd_", "lo_"))
                             and t != "idle"} - {""}, key=len, reverse=True)
        self._masks = {}

    def frames(self, tag):
        return self.anims[tag]["frames"]

    def base(self, idle):
        return idle + "_base" if idle + "_base" in self.anims else idle

    def family(self, idle):
        """The plain action tags of an idle's form ("" = the hero's own form: tags of no other form)."""
        form = idle[:-len("idle")]
        out = []
        for t in self.anims:
            if t.startswith(("hd_", "lo_")):
                continue
            if form:
                if not t.startswith(form) or NOT_SNIPPET.search(t[len(form):]):
                    continue
            elif any(t.startswith(f) for f in self.forms) or NOT_SNIPPET.search(t):
                continue
            out.append(t)
        return out

    def mask(self, tag, i, c=200):
        """Frame i of a plain (1x) tag: its alpha on a c x c canvas, the frame's centre (the pivot) at the middle."""
        key = (tag, i)
        if key not in self._masks:
            d = self.frames(tag)[i]["data"]
            x, y, w, h = (int(round(d[k])) for k in "xywh")
            al = self.sheet[y:y + h, x:x + w, 3] > 0
            out = np.zeros((c, c), bool)
            ox, oy = c // 2 - w // 2, c // 2 - h // 2
            part = al[max(0, -oy):, max(0, -ox):][:c - max(oy, 0), :c - max(ox, 0)]
            out[max(oy, 0):max(oy, 0) + part.shape[0], max(ox, 0):max(ox, 0) + part.shape[1]] = part
            self._masks[key] = out
        return self._masks[key]

    def spill(self, tag, i):
        """(aside, above): the shares of frame i's opaque pixels the ban/pick card loses past its sides (+-4) and over
        its top (clipped: the canvas top; not clipped: 20 px over the card). Feet under the name bar do not count."""
        m = self.mask(tag, i)
        ys, xs = np.nonzero(m)
        if not len(xs):
            return 0.0, 0.0
        c = m.shape[0] / 2
        cx = CW / 2 + (xs + 0.5 - c) * self.card
        cy = CH + S * self.by + (ys + 0.5 - c) * self.card
        return float(((cx < -4) | (cx > CW + 4)).mean()), float(((cy < 0) if self.clip else (cy < -20)).mean())


_VIEWS = {}


def views(pack):
    if pack not in _VIEWS:
        p = os.path.join(REPO, pack, "style", "champion_view.champion_view")
        _VIEWS[pack] = json.load(open(lp(p), encoding="utf-8-sig")).get("entries", {}) if os.path.exists(lp(p)) else {}
    return _VIEWS[pack]


def box(m):
    ys, xs = np.nonzero(m)
    return xs.min(), xs.max(), ys.min(), ys.max()


def assess(h, idle):
    """{action: [(fits, change)]} for an idle's form: whether each frame stays where the idle stands (feet on the
    idle's ground row +-1, 55 % of the idle's leg rows covered, within the idle +-8 px aside and its top + 12, changing
    at most 60 % of the picture) and how much of the idle's frame 0 it changes."""
    base = h.base(idle)
    B = [h.mask(base, i) for i in range(len(h.frames(base)))]
    i0 = B[0]
    if not i0.any():
        return {}                                 # an idle with nothing drawn (league_yuumi attached)
    ux0, ux1, uy0, uy1 = box(np.logical_or.reduce(B))
    y1 = box(i0)[3]
    legs = i0[y1 - 9:y1 + 1]
    n0 = max(i0.sum(), 1)
    out = {}
    for t in h.family(idle):
        rows = []
        for i in range(len(h.frames(t))):
            m = h.mask(t, i)
            if not m.any():
                rows.append((False, 1.0))
                continue
            x0, x1, y0, fy1 = box(m)
            band = m[y1 - 9:y1 + 1]
            band = band | np.roll(band, 1, 1) | np.roll(band, -1, 1)
            recall = (band & legs).sum() / max(legs.sum(), 1)
            d = float((m ^ i0).sum() / n0)
            rows.append((bool(abs(fy1 - y1) <= 1 and recall >= 0.55 and x0 >= ux0 - 8 and x1 <= ux1 + 8
                              and y0 >= uy0 - 12 and d <= 0.6), d))
        out[t] = rows
    return out


def snippets(h, idle):
    """The rules' snippets for an idle: [(action, [frames])], the two best of different actions - a run of up to 4
    fitting frames starting near the idle (change <= 35 %), scored by its largest change (>= 12 %) and its length."""
    best = []
    for t, rows in assess(h, idle).items():
        pick = None
        for s in range(len(rows)):
            if not rows[s][0] or rows[s][1] > 0.35:
                continue
            e = s
            while e + 1 < len(rows) and rows[e + 1][0] and e + 1 - s < 4:
                e += 1
            run = list(range(s, e + 1))
            peak = max(rows[k][1] for k in run)
            if peak < 0.12:
                continue
            score = peak + 0.1 * min(len(run), 3)
            if pick is None or score > pick[0]:
                pick = (score, t, run)
        if pick:
            best.append(pick)
    best.sort(key=lambda p: -p[0])
    return [(t, run) for _, t, run in best[:2]]


def card_actions(h, picks, k):
    """[(action, [(frame shown, its own duration)])] for the card, rotated to start at the hero's k-th action."""
    base = h.base("idle")
    aside = max(h.spill(base, i)[0] for i in range(len(h.frames(base)))) + ASIDE[h.clip]
    names = picks.get("bp") or [t for t in CORE if t in h.anims]
    cut = picks.get("bp_cut", {})
    out = []
    for t in names:
        fr = h.frames(t)
        bad = {i for i in range(len(fr)) if h.spill(t, i)[0] > aside or h.spill(t, i)[1] > ABOVE[h.clip]}
        bad |= set(cut.get(t, []))
        if not picks.get("bp") and (0 in bad or len(bad) > 0.4 * len(fr)):
            continue
        shown, last = [], next((i for i in range(len(fr)) if i not in bad), 0)
        for i, f in enumerate(fr):
            last = last if i in bad else i
            shown.append((last, f["duration"]))
        out.append((t, shown))
    if out:
        k %= len(out)
        out = out[k:] + out[:k]
    return out


def still(h, idle, secs=None):
    """The idle's first frame held (STILL_S unless given): no breathing (the user, 2026-10-22: 「上下摆动全不要了啊」)."""
    return [(h.base(idle), 0, STILL_S if secs is None else secs)]


def schedule(hid, idle, n):
    """[(hold seconds, snippet index)] for one idle cycle: IDLE_TURNS snippets after holds of 0.8-3.2 s, in an order
    that does not repeat a snippet twice running - fixed per hero and idle (a hash of the names), so the cycle is the
    same every run but no two heroes fidget in step (the user: 「随便冒出来个动作 和英雄联盟一样」)."""
    seed = int(hashlib.sha1(f"{hid}/{idle}".encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    out, last = [], None
    for _ in range(IDLE_TURNS):
        k = rnd.randrange(n)
        if n > 1 and k == last:
            k = (k + 1 + rnd.randrange(n - 1)) % n
        out.append((round(rnd.uniform(0.8, 3.2), 2), k))
        last = k
    return out


def played(h, tag, run, how=""):
    """A snippet: its frames in (each at least MIN_DUR), the last held HOLD_S more, then back out; "fwd": forward only,
    nothing held (a cycle such as league_draven's axe juggle, which would spin backwards played back)."""
    fr = h.frames(tag)
    seq = [(tag, i, max(fr[i]["duration"], MIN_DUR)) for i in run]
    if how == "fwd":
        return seq
    seq[-1] = (tag, run[-1], seq[-1][2] + HOLD_S)
    seq += [(tag, i, max(fr[i]["duration"], MIN_DUR)) for i in reversed(run[:-1])]
    return seq


def plan(h, picks, k):
    """{tag: [(source tag, frame, duration)]} - the hero's new idles (and their _base copies) and its bp."""
    out = {}
    idles = ["idle"] + [f + "idle" for f in h.forms]
    snips = {}
    for idle in idles:
        base = h.base(idle)
        sn = picks.get(idle)
        sn = [(e[0], list(e[1]), *e[2:]) for e in sn] if sn is not None else snippets(h, idle)
        snips[idle] = sn
        out[idle + "_base"] = [(base, i, f["duration"]) for i, f in enumerate(h.frames(base))]
        seq = []
        for hold, k in schedule(h.id, idle, len(sn)) if sn else []:
            t, run, *how = sn[k]
            seq += still(h, idle, hold) + played(h, t, run, *how)
        out[idle] = seq or still(h, idle)
    acts = card_actions(h, picks, k)
    bp = []
    sn = snips["idle"]
    for j, (t, shown) in enumerate(acts):
        bp += still(h, "idle") + [(t, i, d) for i, d in shown] + still(h, "idle")
        if sn:
            tt, run, *how = sn[j % len(sn)]
            bp += played(h, tt, run, *how)
    out["bp"] = bp or out["idle"]
    return out, snips, acts


def frames_for(h, seq, prefix):
    out = []
    for tag, i, d in seq:
        data = dict(h.frames(prefix + tag)[i]["data"])
        out.append({"duration": round(d, 6), "data": data})
    return out


def rewrite(h, p):
    """The hero's .fanim text with the plan's tags written (in place where they exist, at the end where new)."""
    anims = dict(h.anims)
    for tag, seq in p.items():
        for pre in PREFIXES:
            if pre and pre + "idle" not in h.anims:
                continue
            anims[pre + tag] = {"frames": frames_for(h, seq, pre)}
    return json.dumps({"anims": anims}, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def heroes(only=None):
    out = []
    for pack in PACKS:
        cdir = os.path.join(REPO, pack, "champions")
        if not os.path.isdir(lp(cdir)):
            continue
        for fn in sorted(os.listdir(lp(cdir))):
            if fn.endswith("#anim.fanim"):
                hid = fn.split("#")[0]
                if only is None or hid in only or hid.split("_", 1)[1] in only:
                    out.append((pack, hid))
    return out


def all_ids():
    return [hid for _, hid in heroes()]


def preview(items, out, card):
    """The idles (1x frames at 3x) or the cards (bp, card math) of the heroes side by side as one GIF."""
    tick = 0.04
    cols = 4
    cells = []
    for h, p in items:
        seq = p["bp"] if card else p["idle"]
        pre = "hd_" if (card and h.dense) else ""
        scale = (h.card / PPU[h.id]) if pre else (h.card if card else 3.0)
        t, times = 0.0, []
        for tag, i, d in seq:
            times.append((t, tag, i))
            t += d
        cells.append((h, times, t, pre, scale))
    cw, ch = (CW, CH + 60) if card else (200, 200)
    W = cols * (cw + 8) + 8
    H = ((len(cells) + cols - 1) // cols) * (ch + 22) + 8
    total = min(24.0, max(c[2] for c in cells))
    frames = []
    crops = {}
    for s in range(int(total / tick)):
        now = s * tick
        img = Image.new("RGBA", (W, H), (14, 20, 26, 255))
        for k, (h, times, length, pre, scale) in enumerate(cells):
            x0 = 8 + (k % cols) * (cw + 8)
            y0 = 8 + (k // cols) * (ch + 22)
            cur = times[0]
            for e in times:
                if e[0] <= now % length:
                    cur = e
                else:
                    break
            key = (h.id, pre, cur[1], cur[2])
            if key not in crops:
                d = h.frames(pre + cur[1])[cur[2]]["data"]
                x, y, w, hh = (int(round(d[q])) for q in "xywh")
                im = Image.fromarray(h.sheet[y:y + hh, x:x + w])
                crops[key] = im.resize((max(1, round(w * scale)), max(1, round(hh * scale))), Image.NEAREST)
            im = crops[key]
            layer = Image.new("RGBA", (W, H))
            dr = ImageDraw.Draw(img)
            if card:
                top = y0 + 60
                dr.rectangle([x0, top, x0 + CW - 1, top + CH - 1], fill=(25, 41, 47, 255))
                px, py = x0 + CW / 2 - im.width / 2, top + CH + S * h.by - im.height / 2
                layer.paste(im, (round(px), round(py)))
                if h.clip:
                    m = Image.new("L", (W, H), 0)
                    ImageDraw.Draw(m).rectangle([x0, top, x0 + CW - 1, top + CH - 1], fill=255)
                    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (W, H), 0), m))
                img.alpha_composite(layer)
                dr = ImageDraw.Draw(img)
                dr.rectangle([x0, top + CH - 2, x0 + CW - 1, top + CH + 18], fill=(40, 52, 70, 255))
                label_y = top + CH + 4
            else:
                dr.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], fill=(25, 41, 47, 255))
                px, py = x0 + cw / 2 - im.width / 2, y0 + ch * 0.62 - im.height / 2
                layer.paste(im, (round(px), round(py)))
                img.alpha_composite(layer)
                dr = ImageDraw.Draw(img)
                label_y = y0 + ch + 4
            dr.text((x0 + 2, label_y), f"{h.id.split('_', 1)[1]} {cur[1]}", fill=(230, 230, 230, 255))
        frames.append(img.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(tick * 1000), loop=0, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hero", help="comma-separated ids (league_garen or garen)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--card", action="store_true", help="--preview the ban/pick cards instead of the idles")
    a = ap.parse_args()
    only = set(a.hero.split(",")) if a.hero else None
    picks = json.load(open(lp(PICKS), encoding="utf-8")) if os.path.exists(lp(PICKS)) else {}
    order = {hid: k for k, hid in enumerate(all_ids())}
    stale, items = [], []
    for pack, hid in heroes(only):
        h = Hero(pack, hid)
        p, snips, acts = plan(h, picks.get(hid, {}), order[hid])
        if a.list:
            held = {t: sum(1 for i, (s, _) in enumerate(sh) if s != i) for t, sh in acts}
            print(f"{hid:28s} " + " | ".join(f"{idle}: {sn}" for idle, sn in snips.items())
                  + f" || card: {[t + (f'(-{held[t]})' if held[t] else '') for t, _ in acts]}")
        if a.preview:
            items.append((h, p))
            continue
        new = rewrite(h, p)
        if new != h.raw:
            stale.append(hid)
            if not a.check and not a.list:
                with open(lp(h.fanim), "wb") as f:
                    f.write(new)
    if a.preview:
        preview(items, a.preview, a.card)
        print("wrote", a.preview)
    elif a.check:
        print(f"{len(stale)} .fanim not as hero_reels.py writes them" + (": " + ", ".join(stale) if stale else ""))
        sys.exit(1 if stale else 0)
    elif not a.list:
        print(f"wrote {len(stale)} .fanim")


if __name__ == "__main__":
    main()
