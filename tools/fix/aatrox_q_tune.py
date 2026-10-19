#!/usr/bin/env python3
"""Aatrox's Darkin Blade: less burst at low levels, 10% more reach (the user, 2026-10-20: 「剑魔（亚托克斯）前期 Q 技能
直接秒人，这个有可能改一下吗？另外，要是能稍微增加一点技能范围就更好了」).

    python tools/fix/aatrox_q_tune.py [--check] [--file league/champion/league_aatrox.data_champion]
                                      [--ratio R] [--flat F] [--out file]

league_aatrox has no generator (the JSON is hand-kept), so this script edits it, idempotently: every value it touches
is either the old value (changed) or already the new one (left), anything else stops it. It also
rewrites Q's tooltip (league/text/champion.i18n, five languages: the first cast's damage). Run
addons/league_aatrox_chain/make_override.py after it (the add-on's copy) and tools/art/warn_aatrox.py +
tools/art/import_aatrox.py (the ground warnings are drawn at the shapes' sizes: warn_aatrox.RANGE).

Damage. Each Q hit was flat + ratio% attack: Q1 100 + 160%, Q2 125 + 200%, Q3 150 + 240%, the sweet spot 60% of it
more (60 + 96% ...). At level 1 (attack 100) the three bodies dealt 260 + 325 + 390 = 975, the sweet spots 1560 - a
1100-health top laner from full. The flat parts go (FLAT 0) and the ratios are scaled by RATIO, so the early hits
lose most and the late ones little (level 12, attack 342: the flat part was 15% of a body hit). The heals on champion
hits (E's 18%, 27% in World Ender) are the same share of the new damage, so they scale the same way.

Reach. Every Q shape 10% bigger (RANGE): Q1's line 45000 -> 49500 long and 6500 -> 7150 wide with its sweet spot
(the tip 41000 -> 45100, radius 4500 -> 4950), Q2's 26000 x 14000 (tip 31000, radius 5000), Q3's circle 14500 ahead
(radius 21800, its middle 13100), the cast range 40000 -> 44000, and the reaches E reads inside Q to dash in or back
(15000 / 22000 / 25000 / 45000 / 50000 / 51000 to an enemy champion). The attack Q chains into keeps its 26000.

Classic-SDK balance (Temp/yr_sim, kd.py 600 s 16 seeds, top lane against the six base top laners, three lineups, both
sides), all with RANGE 1.1: the old kit +1.45; FLAT 0 with RATIO 1.0 +0.64, 0.9375 -0.03, 1.1 +1.55 - the pick (level 1:
the three bodies 660 instead of 975, the sweet spots 1056 instead of 1560; level 12: 2257 instead of 2427).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE = os.path.join(ROOT, "league", "champion", "league_aatrox.data_champion")
RANGE = 1.1
FLAT = 0.0
RATIO = 1.1

# the old Q damage (flat, ratio) of the Attack nodes and the heals that follow them (normal, World Ender)
OLD_ATTACKS = [(100, 160), (60, 96), (125, 200), (75, 120), (150, 240), (90, 144)]
OLD_HEALS = [(18, 29), (27, 44), (11, 17), (16, 26), (22, 36), (33, 54), (14, 22), (21, 33), (27, 43), (40, 64), (24, 39)]
OLD_LINES = {"q1": (6500, 45000), "q2": (14000, 26000)}
OLD_TIPS = {"league_aatrox_q1_tip": 41000, "league_aatrox_q2_tip": 31000, "league_aatrox_q3_at": 14500,
            "league_aatrox_q3_tele_at": 14500}
OLD_CIRCLES = {"q1_edge": 4500, "q2_edge": 5000, "q3_area": 21800, "q3_champ": 21800, "q3_edge": 13100}
OLD_E_REACH = [15000, 22000, 25000, 45000, 50000, 51000]
OLD_CAST = 40000


def r100(x):
    return int(round(x / 100.0)) * 100


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


class Tune:
    def __init__(self, flat, ratio, scale):
        self.flat, self.ratio, self.scale = flat, ratio, scale
        self.changed = 0
        self.kept = 0

    def pair(self, old):
        return (int(round(old[0] * self.flat)), int(round(old[1] * self.ratio)))

    def set(self, o, key, old, new, what):
        v = o[key]
        if v == new:
            self.kept += 1
        elif v == old:
            o[key] = new
            self.changed += 1
        else:
            sys.exit(f"{what}: {key} is {v}, neither the old {old} nor the new {new} - the kit changed, look again")

    def walk(self, o, in_skill):
        if isinstance(o, list):
            for v in o:
                self.walk(v, in_skill)
            return
        if not isinstance(o, dict):
            return
        t = o.get("type")
        name = o.get("name", "")
        if t == "Attack" and (o["damage"], o["attack_ratio"]) != (0, 100):
            olds = {self.pair(p): p for p in OLD_ATTACKS}
            cur = (o["damage"], o["attack_ratio"])
            old = cur if cur in OLD_ATTACKS else olds.get(cur)
            if old is None:
                sys.exit(f"Q damage {cur} unknown")
            new = self.pair(old)
            self.set(o, "damage", old[0], new[0], "Attack")
            self.set(o, "attack_ratio", old[1], new[1], "Attack")
        elif t == "Heal":
            cur = (o["amount"], o["attack_ratio"])
            olds = {self.pair(p): p for p in OLD_HEALS}
            old = cur if cur in OLD_HEALS else olds.get(cur)
            if old is None:
                sys.exit(f"Q heal {cur} unknown")
            new = self.pair(old)
            self.set(o, "amount", old[0], new[0], "Heal")
            self.set(o, "attack_ratio", old[1], new[1], "Heal")
        elif t == "LineRangeProjectile" and name.startswith("league_aatrox_q"):
            w, length = OLD_LINES[name.split("_")[2]]
            self.set(o, "width", w, r100(w * self.scale), name)
            self.set(o, "length", length, r100(length * self.scale), name)
        elif t == "LinearProjectile" and name in OLD_TIPS:
            self.set(o, "range", OLD_TIPS[name], r100(OLD_TIPS[name] * self.scale), name)
        elif t == "RangeProjectile" and name.startswith("league_aatrox_q"):
            key = "_".join(name.split("_")[2:4])
            old = OLD_CIRCLES[key]
            self.set(o["shape"]["Circle"], "radius", old, r100(old * self.scale), name)
        elif t == "RandomTarget" and o.get("casting_target") == "EnemyChampion":
            v = o["range"]
            news = {r100(x * self.scale): x for x in OLD_E_REACH}
            old = v if v in OLD_E_REACH else news.get(v)
            if old is None:
                sys.exit(f"E reach {v} unknown")
            self.set(o, "range", old, r100(old * self.scale), "E reach")
        for v in o.values():
            if isinstance(v, (dict, list)):
                self.walk(v, in_skill)


TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
AD_ICON = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
OLD_TIP = "<#ff9028ff>100<> + " + AD_ICON + "<#ff9028ff>160%<>"


def tooltip(ratio, flat, check):
    """Q's tooltip (description.league_aatrox.skill, five languages) shows the first cast's damage: 100 + 160% -> the
    new pair (no flat part: the ratio alone). Only Aatrox's own entries: another hero's text has the same numbers.
    Returns how many entries are still old."""
    f, r = int(round(100 * flat)), int(round(160 * ratio))
    new = (f"<#ff9028ff>{f}<> + " if f else "") + AD_ICON + f"<#ff9028ff>{r}%<>"
    with open(lp(TEXT), "rb") as fh:
        raw = fh.read().decode("utf-8-sig")
    d = json.loads(raw)
    left = 0
    for lang, t in d.items():
        old = t.get("description", {}).get("league_aatrox", {}).get("skill", "")
        if OLD_TIP not in old or new == OLD_TIP:
            continue
        left += 1
        enc_old, enc_new = json.dumps(old, ensure_ascii=False), json.dumps(old.replace(OLD_TIP, new), ensure_ascii=False)
        if raw.count(enc_old) != 1:
            sys.exit(f"{lang}: Aatrox's Q text is not once in the file as written - edit it by hand")
        raw = raw.replace(enc_old, enc_new)
    if left and not check:
        with open(lp(TEXT), "w", encoding="utf-8", newline="") as fh:
            fh.write(raw)
    return left


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--file", default=FILE)
    ap.add_argument("--out")
    ap.add_argument("--flat", type=float, default=FLAT)
    ap.add_argument("--ratio", type=float, default=RATIO)
    ap.add_argument("--range", type=float, default=RANGE, dest="scale")
    a = ap.parse_args()
    with open(lp(a.file), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    tune = Tune(a.flat, a.ratio, a.scale)
    tune.walk(d["skill"], True)
    tune.set(d["skill"], "range", OLD_CAST, r100(OLD_CAST * a.scale), "skill")
    if a.check:
        left = tooltip(a.ratio, a.flat, True) if not a.out else 0
        print(f"{tune.changed} values still old, {tune.kept} already new; Q's tooltip: {left} places still old")
        sys.exit(1 if tune.changed or left else 0)
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.out or a.file), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.out or a.file}: {tune.changed} values changed, {tune.kept} already new")
    if not a.out:
        print(f"{TEXT}: Q's tooltip changed in {tooltip(a.ratio, a.flat, False)} places")


if __name__ == "__main__":
    main()
