#!/usr/bin/env python3
"""Before / after pictures of the red-side effect fixes (2026-10-05), one GIF per hero.

    python tools/art/red_side_gifs.py [--base <git ref>] [--hero leona ...]   # docs/preview/red_side/<hero>.gif

Each GIF plays the hero's actions that carry a fixed picture, in three panels: the blue side (facing right), the red
side as it was drawn before the fix and the red side now (facing left). The panels are put together from the hero's
own sheets by the rules the client follows (champion-data.md section 6), not recorded in game:
- a zone's or a projectile's picture (view_projectiles) is turned to its direction - half round when cast leftward;
- a ViewEffect is drawn unturned on its point, a CasterViewEffect on the caster, mirrored by the caster's facing,
  except one with is_follow that starts after the action's first tick: the client draws it unmirrored;
- the picture's time is the action's start_timing plus the Delayed ticks over it (a lob's end_effects after its
  travel_time); a projectile flies at its speed;
- a picture stamped along a flight (league_yasuo's Q3 whirlwind since 2026-10-05: `ViewEffect`s in the end_effects
  of hidden projectiles that stop on its path, tools/fix/fix_yasuo_q3_stamps.py) is each stamp drawn unturned on its
  stop point, from the tick its projectile stops (SDK simulation: travel speed x (tick + 1) from the third tick).
"Before" reads the kit and the effect sheets at --base (default: where this branch left main), "now" the working tree.
"""
import argparse
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "docs", "preview", "red_side")
TPS = 60                                          # ticks a second
STEP = 2                                          # ticks a GIF frame (30 fps)
PANEL = (150, 116)                                # game px
Z = 3
PIVOT_Y = 84
REACH = 58                                        # a cast point this far ahead of the hero (px)
ARENA = (92, 104, 88)
FONT = "C:/Windows/Fonts/msyh.ttc"
SLOTS = ("attack", "skill", "skill2", "ult")
ZONES = ("RangeProjectile", "RangePeriodProjectile", "ApplyInProjectile", "LineRangeProjectile")
FLYING = ("LinearProjectile", "TargetProjectile", "ParabolicProjectile")
VISUAL = ("ViewEffect", "CasterViewEffect") + ZONES + FLYING
# {hero: [effect names fixed on the red side]}
FIXED = {
    "leona": ["r_flare"], "soraka": ["q_star", "e_field"], "lux": ["e_burst"], "lissandra": ["r_field"],
    "sona": ["q_aura", "w_aura", "e_aura"], "yasuo": ["q3_tornado"],
    "caitlyn": ["shot", "hs_shot", "q_muzzle", "e_shot", "r_muzzle"],
    "jhin": ["a_cast", "a_muzzle", "a4_muzzle", "w_muzzle", "r_muzzle"],
    "kaisa": ["w_muzzle", "r_trail"], "leblanc": ["a_cast", "e_cast", "re_cast", "rq_cast"],
    "kennen": ["q_cast"], "ryze": ["q_cast"], "diana": ["p_cleave"], "vi": ["r_trail"], "tristana": ["q_cast"],
    "riven": ["r_on_back", "r_on_front", "r_slash_back"],
}
# a picture played under another name now (the attack's non-following copies of Riven's R layers)
NOW_NAME = {("riven", "r_on_back"): "r_on_back_atk", ("riven", "r_on_front"): "r_on_front_atk"}
# a flying picture stamped along its path now, by the prefix of the stamps' names
STAMPED = {("yasuo", "q3_tornado"): "q3_tornado_"}


def git_bytes(ref, path):
    return subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{path}"], capture_output=True, check=True).stdout


def read(ref, path):
    if ref is None:
        with open(os.path.join(ROOT, path), "rb") as f:
            return f.read()
    return git_bytes(ref, path)


def kit(ref, hero):
    return json.loads(read(ref, f"league/champion/league_{hero}.data_champion").decode("utf-8"))


SHEETS = {}


def anim(ref, asset, tag):
    """[(rgba array, ms)] of a tag of an asset path (asset/league/<dir>/<name>)."""
    key = (ref, asset)
    if key not in SHEETS:
        stem = "league/" + asset.split("asset/league/", 1)[1]
        sh = np.asarray(Image.open(io.BytesIO(read(ref, stem + "#sheet.png"))).convert("RGBA"))
        SHEETS[key] = (sh, json.loads(read(ref, stem + "#anim.fanim").decode("utf-8"))["anims"])
    sh, an = SHEETS[key]
    out = []
    for f in an[tag]["frames"]:
        x, y, w, h = (int(f["data"][k]) for k in "xywh")
        out.append((sh[y:y + h, x:x + w], f["duration"] * 1000.0))
    return out


def views(k):
    return {v["name"]: (kind, v) for kind in ("view_effects", "view_projectiles", "view_buffs") for v in k.get(kind, [])}


def occurrences(node, name, tick=0, late=False):
    """(tick, effect dict, late) of every effect named `name` under node, Delayed ticks and lobs' travel added; late:
    under a Delayed or an AddCasted (what the client plays after the action's first tick, as lint_mod.py reads it)."""
    if isinstance(node, list):
        for e in node:
            yield from occurrences(e, name, tick, late)
        return
    if not isinstance(node, dict):
        return
    if node.get("name") == name and node.get("type") in VISUAL:     # (an Sfx may share the picture's name)
        yield tick, node, late
    t = node.get("type")
    for key, v in node.items():
        if not isinstance(v, (dict, list)) or key in ("buff_state", "shape"):
            continue
        add = 0
        if t == "Delayed" and key == "effects":
            add = node.get("tick", 0)
        elif key == "end_effects" and t == "ParabolicProjectile":
            add = node.get("travel_time", 0)
        yield from occurrences(v, name, tick + add, late or t in ("Delayed", "AddCasted"))


def find(k, full):
    """(slot, tick from the action's start, effect dict, late) of the place `full` plays - a late one first (the fixes
    are about those: league_ryze's Q flash also plays at Q's start, where it was right)."""
    found = []
    for slot in SLOTS:
        if slot not in k:
            continue
        act = k[slot]
        for tick, eff, late in occurrences(act.get("effect"), full):
            found.append((not late, SLOTS.index(slot), slot, act.get("start_timing", 0) + tick, eff, late))
    if not found:
        return None
    _, _, slot, tick, eff, late = min(found, key=lambda q: (q[0], q[1]))
    return slot, tick, eff, late


def stop_tick(rng, speed):
    """The tick of its flight a LinearProjectile stops on (fix_yasuo_q3_stamps.py: travel speed x (tick + 1) from the
    third tick, speed x tick before)."""
    n = 1
    while (speed * (n + 1) if n >= 3 else speed * n) < rng:
        n += 1
    return n


def stamps(k, prefix):
    """[(slot, tick from the action's start, view name, distance in px)] of every ViewEffect named prefix* played
    where a LinearProjectile stops."""
    out = []

    def walk(node, slot, tick):
        if isinstance(node, list):
            for e in node:
                walk(e, slot, tick)
            return
        if not isinstance(node, dict):
            return
        t = node.get("type")
        if t == "LinearProjectile":
            for e in node.get("end_effects", []):
                if e.get("type") == "ViewEffect" and e.get("name", "").startswith(prefix):
                    out.append((slot, tick + stop_tick(node["range"], node["speed"]), e["name"], node["range"] / 1000.0))
        for key, v in node.items():
            if isinstance(v, (dict, list)) and key not in ("buff_state", "shape", "end_effects"):
                walk(v, slot, tick + (node.get("tick", 0) if t == "Delayed" and key == "effects" else 0))

    for slot in SLOTS:
        if slot in k:
            walk(k[slot].get("effect"), slot, k[slot].get("start_timing", 0))
    return out


class Shot:
    """One action of the hero with the fixed pictures it plays."""

    def __init__(self, hero, slot, base_kit, now_kit):
        self.hero, self.slot = hero, slot
        self.action = now_kit[slot]
        self.pics = []          # (when: "before"/"now", tick, frames, z, place, rule, flight)

    def length(self):
        end = self.action.get("duration", 60)
        for _, tick, frames, *_ in self.pics:
            end = max(end, tick + int(sum(ms for _, ms in frames) * TPS / 1000) + 4)
        return end + 10


def hero_frames(hero, tag):
    stem = f"league/champions/league_{hero}"
    sh = np.asarray(Image.open(os.path.join(ROOT, stem + "#sheet.png")).convert("RGBA"))
    with open(os.path.join(ROOT, stem + "#anim.fanim"), encoding="utf-8") as f:
        an = json.load(f)["anims"]
    tag = tag if tag in an else "idle"
    return [(sh[int(f["data"]["y"]):int(f["data"]["y"] + f["data"]["h"]),
               int(f["data"]["x"]):int(f["data"]["x"] + f["data"]["w"])], f["duration"] * 1000.0)
            for f in an[tag]["frames"]]


def at(frames, ms, loop=False):
    total = sum(d for _, d in frames)
    if ms < 0 or (ms >= total and not loop):
        return None
    ms = ms % total if loop else ms
    for a, d in frames:
        if ms < d:
            return a
        ms -= d
    return frames[-1][0]


def paste(can, a, cx, cy):
    """a (odd-sized, centred on its pivot) onto can with its centre on (cx, cy)."""
    h, w = a.shape[:2]
    x0, y0 = int(round(cx - (w - 1) / 2)), int(round(cy - (h - 1) / 2))
    for yy in range(h):
        Y = y0 + yy
        if not 0 <= Y < can.shape[0]:
            continue
        for xx in range(w):
            X = x0 + xx
            if 0 <= X < can.shape[1] and a[yy, xx, 3]:
                can[Y, X] = a[yy, xx]


def build_shots(hero, base):
    bk, nk = kit(base, hero), kit(None, hero)
    bv, nv = views(bk), views(nk)
    shots = {}
    for short in FIXED[hero]:
        old = f"league_{hero}_{short}"
        new = f"league_{hero}_" + NOW_NAME.get((hero, short), short)
        for when, k, v, name, ref in (("before", bk, bv, old, base), ("now", nk, nv, new, None)):
            if when == "now" and (hero, short) in STAMPED:
                for slot, tick, stamp, dist in stamps(k, f"league_{hero}_" + STAMPED[(hero, short)]):
                    view = v[stamp][1]
                    shots.setdefault(slot, Shot(hero, slot, bk, nk)).pics.append(
                        (when, tick, anim(ref, view["anim"], view["tag"]), view.get("z", 0), dist, "upright", None))
                continue
            hit = find(k, name)
            if hit is None:
                continue
            slot, tick, eff, late = hit
            kind, view = v[name]
            frames = anim(ref, view["anim"], view["tag"])
            if kind == "view_projectiles":
                rule = "turned"
            elif eff["type"] == "CasterViewEffect":
                rule = "unmirrored" if (view.get("is_follow") and late) else "mirrored"
            else:
                rule = "upright"
            place = "caster" if (eff["type"] in ("CasterViewEffect", "ApplyInProjectile") or
                                 eff.get("follow_caster") or k[slot].get("casting_type") == "None") else "point"
            flight = None
            if eff["type"] in FLYING and eff.get("speed"):
                flight = (eff["speed"] / 1000.0, eff.get("range", 80000) / 1000.0)
                place = "caster"
            shots.setdefault(slot, Shot(hero, slot, bk, nk)).pics.append(
                (when, tick, frames, view.get("z", 0), place, rule, flight))
    return [shots[s] for s in SLOTS if s in shots]


def panel(shot, t, side, when):
    """One panel at tick t: side "blue" / "red", when "before" / "now"."""
    can = np.zeros((PANEL[1], PANEL[0], 4), np.uint8)
    can[...] = ARENA + (255,)
    face = 1 if side == "blue" else -1
    hx = 42 if side == "blue" else PANEL[0] - 42
    body = at(hero_frames(shot.hero, shot.action.get("action_name", shot.slot)), t * 1000 / TPS, loop=True)
    pics = [p for p in shot.pics if p[0] == when]
    layers = []
    for _, tick, frames, z, place, rule, flight in pics:
        a = at(frames, (t - tick) * 1000 / TPS, loop=flight is not None and t >= tick)
        if a is None:
            continue
        if side == "red":
            if rule == "turned":
                a = a[::-1, ::-1]               # half round about its pivot
            elif rule == "mirrored":
                a = a[:, ::-1]
        x, y = hx, PIVOT_Y
        if place == "point":
            x += face * REACH
        elif isinstance(place, float):          # a stamp: its distance along the flight
            x += face * place
        if flight is not None:
            run = min(flight[1], flight[0] * (t - tick))
            x += face * run
        layers.append((z, a, x, y))
    for z, a, x, y in sorted(layers, key=lambda q: q[0]):
        if z < 0:
            paste(can, a, x, y)
    if body is not None:
        paste(can, body if face > 0 else body[:, ::-1], hx, PIVOT_Y)
    for z, a, x, y in sorted(layers, key=lambda q: q[0]):
        if z >= 0:
            paste(can, a, x, y)
    return can


def gif(hero, base):
    shots = build_shots(hero, base)
    font = ImageFont.truetype(FONT, 18)
    W, H = PANEL[0] * Z, PANEL[1] * Z
    titles = [("蓝色方（现在）", "blue", "now"), ("红色方 · 改前", "red", "before"), ("红色方 · 改后", "red", "now")]
    images, durs = [], []
    for shot in shots:
        for t in range(0, shot.length(), STEP):
            img = Image.new("RGB", (W * 3 + 16, H + 30), (34, 36, 40))
            d = ImageDraw.Draw(img)
            for i, (title, side, when) in enumerate(titles):
                can = panel(shot, t, side, when)
                img.paste(Image.fromarray(can).convert("RGB").resize((W, H), Image.NEAREST), (i * (W + 8), 30))
                d.text((i * (W + 8) + 6, 4), title, font=font, fill=(255, 120, 120) if when == "before" else (235, 235, 235))
            images.append(img)
            durs.append(int(STEP * 1000 / TPS))
        durs[-1] += 400
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{hero}.gif")
    images[0].save(path, save_all=True, append_images=images[1:], duration=durs, loop=0, optimize=True)
    return path, len(images), [(s.slot, len(s.pics)) for s in shots]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base")
    ap.add_argument("--hero", action="append")
    a = ap.parse_args()
    base = a.base or subprocess.run(["git", "-C", ROOT, "merge-base", "origin/main", "HEAD"], capture_output=True,
                                    text=True, check=True).stdout.strip()
    for hero in a.hero or FIXED:
        path, n, shots = gif(hero, base)
        print(f"{os.path.relpath(path, ROOT)}  {n} frames  {shots}")


if __name__ == "__main__":
    sys.exit(main())
