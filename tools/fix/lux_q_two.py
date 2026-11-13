#!/usr/bin/env python3
"""Lux's Light Binding roots the first two enemies it meets, not every enemy on its path (League's rule; the user,
2026-11-14, on the list of differences from League: 「全改吧」).

    python tools/fix/lux_q_two.py [--check]

League (the wiki): the sphere deals its damage to "the first two enemies it hits" and roots them. Here the orb is a
penetrating `LinearProjectile` whose hit rooted everything on the line - a whole minion wave and the champions behind
it. A projectile cannot be removed and data counts no hits per cast, so the count is two caster flags: the cast clears
league_lux_q_n1 / _n2, each hit that still counts raises the next one (N_TICKS, the orb's whole flight), and with both up
the hit does nothing - the orb flies on as a picture. The damage stays in the branch the flags pick while none is up, so
the AI (hers and the enemies' dodging) reads the orb as before. The champion-only twin that opened the Q -> R combo
(league_lux_q_seen) is gone: a champion third in the line must open nothing, and a twin cannot tell (gated on a 1-tick
flag of the orb's hit it missed half the champions - whichever projectile the engine ran first that tick; classic
trace, 11 roots, 6 windows). The orb's own counted hit opens the window when the unit it rooted is a champion
(`RandomTarget` from the projectile, range 1: league_senna W's test).
Edits league/champion/league_lux.data_champion and Q's five texts in league/text/champion.i18n in place. Idempotent;
--check only says whether it is there. addons/league_marks' copy of Lux is built from this kit (its make_override.py).
"""
import argparse
import json
import os
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_lux.data_champion")
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
N1, N2 = "league_lux_q_n1", "league_lux_q_n2"
N_TICKS = 70                     # the orb flies 130000 at 2000 a tick: 65 ticks
WORDS = {"zh-hans": ("对路径上的每个敌人造成", "对路径上最先碰到的两个敌人造成"),
         "zh-hant": ("對路徑上的每個敵人造成", "對路徑上最先碰到的兩個敵人造成"),
         "en": ("to every enemy in its path and", "to the first two enemies in its path and"),
         "ko": ("경로 위의 모든 적에게", "경로에서 처음 맞은 두 적에게"),
         "ja": ("通過した敵すべてに", "最初に当たった敵2体に")}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    raw = open(lp(path), "rb").read().decode("utf-8")
    return json.loads(raw, object_pairs_hook=OrderedDict), raw


def dump(data, raw):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if "\r\n" in raw:
        text = text.replace("\n", "\r\n")
    return text + raw[len(raw.rstrip("\r\n")):]


def T(effect):
    return OrderedDict([("casting_type", "Targeting"), ("effect", effect)])


def flag(name, tick):
    return OrderedDict([("type", "AddCasterBuff"),
                        ("buff_state", OrderedDict([("name", name), ("duration", {"Time": {"tick": tick}})])),
                        ("only_to_enemy", False)])


def sw(name, yes, no):
    return OrderedDict([("type", "SwitchByBuff"), ("buff_name", name), ("effect_buff", yes), ("effect_none", no)])


def combine(*effects):
    return OrderedDict([("type", "Combine"), ("effects", list(effects))])


def patch_list(effects):
    """One effect list holding the orb and its twin: the count's flags cleared before the orb, its hit counted, the
    twin's effects (the combo window) moved into the counted hit on a champion, the twin dropped. -> 1 when patched."""
    k = next((i for i, e in enumerate(effects) if isinstance(e, dict) and e.get("name") == "league_lux_q_orb"), None)
    if k is None:
        return 0
    orb = effects[k]
    twin = next(e for e in effects if isinstance(e, dict) and e.get("name") == "league_lux_q_seen")
    hit = [a["effect"] for a in orb["applied_effects"]]
    count = sw(N1, flag(N2, N_TICKS), flag(N1, N_TICKS))
    window = OrderedDict([("type", "RandomTarget"), ("range", 1), ("casting_target", "EnemyChampion"),
                          ("from_projectile", True), ("effects", [a["effect"] for a in twin["applied_effects"]])])
    orb["applied_effects"] = [T(sw(N2, combine(), combine(count, *hit, window)))]
    effects.remove(twin)
    effects[k:k] = [OrderedDict([("type", "RemoveCasterBuff"), ("name", N1)]),
                    OrderedDict([("type", "RemoveCasterBuff"), ("name", N2)])]
    return 1


def walk(o):
    n = 0
    if isinstance(o, dict):
        for v in list(o.values()):
            n += walk(v)
    elif isinstance(o, list):
        n += patch_list(o)
        for v in o:
            n += walk(v)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    kit, raw = load(KIT)
    assert dump(kit, raw) == raw, "the kit is not in the form this script writes"
    done = N2 in raw
    text, traw = load(TEXT)
    assert dump(text, traw) == traw, "champion.i18n is not in the form this script writes"
    worded = all(new in text[lang]["description"]["league_lux"]["skill"] for lang, (_, new) in WORDS.items())
    if a.check:
        print("Light Binding roots two:", "there" if done and worded else "NOT there")
        sys.exit(0 if done and worded else 1)
    if not done:
        n = walk(kit["skill"]["effect"])
        if n != 2:
            sys.exit(f"{n} orbs patched, expected 2 (the combo's cast and the plain one): the kit changed")
        open(lp(KIT), "w", encoding="utf-8", newline="").write(dump(kit, raw))
    if not worded:
        for lang, (old, new) in WORDS.items():
            s = text[lang]["description"]["league_lux"]["skill"]
            if new in s:
                continue
            if s.count(old) != 1:
                sys.exit(f"{lang}: {old!r} not found once in Q's text")
            text[lang]["description"]["league_lux"]["skill"] = s.replace(old, new)
        open(lp(TEXT), "w", encoding="utf-8", newline="").write(dump(text, traw))
    print("Light Binding roots the first two enemies:", "already there" if done and worded else "written")


if __name__ == "__main__":
    main()
