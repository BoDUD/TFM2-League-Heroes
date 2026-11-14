#!/usr/bin/env python3
"""Morgana's Dark Binding stops on the first enemy it meets - a minion or a monster too - and roots that one only
(League's rule; the user, 2026-11-14, on the list of differences from League: 「全改吧」).

    python tools/fix/morgana_q_first.py [--check] [--bind TICKS] [--ap PERCENT] [--cd TICKS] [--out FILE]

League (the wiki): Dark Binding "deals magic damage to the first enemy hit" and roots it 2 - 3 s. Here two projectiles
flew the same line: a hidden penetrating one that hurt everything on the way (league_morgana_q_path) and the visible
orb that passed minions and monsters and stopped on the first enemy champion to root it (league_morgana_q_orb) - the
first version's AI aimed at minions, so the orb was let through them. Now the orb itself stops on the first enemy
unit (`EnemyWithoutTower`): the damage and the root are that unit's, the penetrating twin is gone. What belonged to a
rooted champion stays a champion's (`RandomTarget` from the projectile, range 1 - league_senna W's test): Soul Siphon's
heal and the league_morgana_q_bound flag that lets Tormented Shadow fall under it.
BIND / AP / CD: the retune that came with it (the classic-engine simulations in docs/heroes/league_morgana.md) - the
root's ticks (League 2 - 3 s by rank), the damage's AP share (League 90%) and Q's cooldown; None leaves the number as
it is.
BLOCK: whom the orb stops on. True = any enemy unit (League's rule, the first version of this script); False = it flies
past minions and monsters to the first enemy champion, who alone takes the damage and the root - the user, the same
day, after the simulations showed the blocking orb catching far fewer champions (46 roots of 122 Qs -> 30 of 115):
「莫甘娜q也要穿过小兵」 (as Nautilus's anchor before it: 「泰坦的钩子恢复穿过小兵」). League's numbers stay.
Edits league/champion/league_morgana.data_champion and Q's five texts in league/text/champion.i18n in place.
Idempotent; --check only says whether it is there; --out writes the kit elsewhere (a simulation's variant) and
leaves the texts alone.
"""
import argparse
import json
import os
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_morgana.data_champion")
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
PATH, ORB = "league_morgana_q_path", "league_morgana_q_orb"
BIND = 180                       # the root's ticks after the change (it was 120; League 2 - 3 s by rank)
AP = 90                          # the damage's AP share after the change (it was 60; League 90%)
CD = None                        # Q's cooldown after the change (None: as it was, 540)
BLOCK = False                    # True: stops on any enemy unit; False: passes minions and monsters (the user's word)
TARGET = {True: "EnemyWithoutTower", False: "EnemyChampion"}
# lang -> (the damage's AP share, the root's seconds) as Q's text writes them: {} = the number
NUMBERS = {"zh-hans": ("<#a974ffff>{}% 法术强度<>", "<#ffb900ff>{}秒<>。每"),
           "zh-hant": ("<#a974ffff>{}% 魔法強度<>", "<#ffb900ff>{}秒<>。每"),
           "en": ("<#a974ffff>{}% Ability Power<> <#a974ffff>magic damage<> and", "<#ffb900ff>{}s<>. Every"),
           "ko": ("<#a974ffff>주문력의 {}%<> <#a974ffff>마법 피해<>를 입히고 ", "<#ffb900ff>{}초<> 동안"),
           "ja": ("<#a974ffff>魔力の{}%<>の<#a974ffff>魔法ダメージ<>を与え、", "<#ffb900ff>{}秒<>間")}
# lang -> [(old words, new words)] in Q's text
WORDS = {
    "zh-hans": [("，穿过小兵和野怪，对沿途敌人造成", "，对路上第一个敌人（小兵、野怪也算）造成"),
                ("，停在第一个敌方英雄身上并将其", "并将其"),
                ("同时在其脚下留下", "定住英雄时在其脚下留下")],
    "zh-hant": [("，穿過小兵和野怪，對沿途敵人造成", "，對路上第一個敵人（小兵、野怪也算）造成"),
                ("，停在第一個敵方英雄身上並將其", "並將其"),
                ("同時在其腳下留下", "禁錮英雄時在其腳下留下")],
    "en": [(" flies through minions and monsters, dealing ", " hits the first enemy in its way (minions and monsters too), dealing "),
           (" to every enemy it passes, and stops on the first enemy champion, ", " and "),
           (" under that champion:", " under a champion it roots:")],
    "ko": [("이 미니언과 몬스터를 관통하며 지나가는 모든 적에게 ", "이 처음 맞은 적(미니언·몬스터 포함)에게 "),
           ("를 입히고, 처음 맞은 적 챔피언에게서 멈춰 ", "를 입히고 "),
           ("마다 그 발밑에 ", "마다 속박된 챔피언의 발밑에 ")],
    "ja": [("はミニオンとモンスターを貫通し、通過した敵に", "は最初に当たった敵（ミニオン・モンスターも）に"),
           ("を与え、最初の敵チャンピオンで止まって", "を与え、"),
           ("毎にその足元に", "毎にスネアしたチャンピオンの足元に")],
}
# lang -> [(the blocking orb's words, the passing orb's words)], applied after WORDS when BLOCK is False
PASS_WORDS = {
    "zh-hans": [("，对路上第一个敌人（小兵、野怪也算）造成", "，穿过小兵和野怪，对第一个敌方英雄造成")],
    "zh-hant": [("，對路上第一個敵人（小兵、野怪也算）造成", "，穿過小兵和野怪，對第一個敵方英雄造成")],
    "en": [(" hits the first enemy in its way (minions and monsters too), dealing ",
            " flies through minions and monsters and hits the first enemy champion, dealing ")],
    "ko": [("이 처음 맞은 적(미니언·몬스터 포함)에게 ", "이 미니언과 몬스터를 통과해 처음 맞은 적 챔피언에게 ")],
    "ja": [("は最初に当たった敵（ミニオン・モンスターも）に", "はミニオンとモンスターを素通りし、最初に当たった敵チャンピオンに")],
}


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


def retarget(o, target):
    """Every orb's applied_target set to `target` -> (orbs found, orbs changed)."""
    found = changed = 0
    if isinstance(o, dict):
        if o.get("name") == ORB and "applied_target" in o:
            found += 1
            if o["applied_target"] != target:
                o["applied_target"] = target
                changed += 1
        for v in o.values():
            f, c = retarget(v, target)
            found, changed = found + f, changed + c
    elif isinstance(o, list):
        for v in o:
            f, c = retarget(v, target)
            found, changed = found + f, changed + c
    return found, changed


def patch_list(effects, bind, ap):
    """One effect list holding the twin and the orb: the orb takes the twin's damage and stops on any enemy unit, the
    champion's extras behind the champion test, the twin dropped. -> 1 when patched."""
    path = next((e for e in effects if isinstance(e, dict) and e.get("name") == PATH), None)
    orb = next((e for e in effects if isinstance(e, dict) and e.get("name") == ORB), None)
    if path is None or orb is None:
        return 0
    hurt = path["applied_effects"][0]["effect"]["effect_none"]["effects"]       # the damage and its picture
    old = [a["effect"] for a in orb["applied_effects"]]
    kinds = [e["type"] for e in old]
    if kinds != ["Bind", "ViewEffect", "TargetSfx", "Heal", "Delayed"] or [e["type"] for e in hurt] != ["ApAttack", "ViewEffect"]:
        sys.exit(f"Dark Binding's hit changed ({kinds}): update this script")
    root, picture, sound, siphon, bound = old
    if bind is not None:
        root["duration"] = bind
    if ap is not None:
        hurt[0]["attack_ratio"] = ap
    champion = OrderedDict([("type", "RandomTarget"), ("range", 1), ("casting_target", "EnemyChampion"),
                            ("from_projectile", True), ("effects", [siphon, bound])])
    orb["applied_target"] = "EnemyWithoutTower"
    orb["applied_effects"] = [T(e) for e in (*hurt, root, picture, sound, champion)]
    effects.remove(path)
    return 1


def walk(o, bind, ap):
    n = 0
    if isinstance(o, dict):
        for v in list(o.values()):
            n += walk(v, bind, ap)
    elif isinstance(o, list):
        n += patch_list(o, bind, ap)
        for v in o:
            n += walk(v, bind, ap)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--bind", type=int, default=BIND)
    ap.add_argument("--ap", type=int, default=AP)
    ap.add_argument("--cd", type=int, default=CD)
    ap.add_argument("--out")
    a = ap.parse_args()
    kit, raw = load(KIT)
    assert dump(kit, raw) == raw, "the kit is not in the form this script writes"
    done = PATH not in json.dumps(kit["skill"])
    text, traw = load(TEXT)
    assert dump(text, traw) == traw, "champion.i18n is not in the form this script writes"
    q = {lang: text[lang]["description"]["league_morgana"]["skill"] for lang in WORDS}
    olds = [old for pairs in WORDS.values() for old, _ in pairs]
    if not BLOCK:
        olds += [old for pairs in PASS_WORDS.values() for old, _ in pairs]
    worded = all(old not in q[lang] for lang in WORDS for old in olds) and (
        a.bind is None or all(NUMBERS[lang][1].format(f"{a.bind / 60:g}") in q[lang] for lang in WORDS))
    aimed = retarget(json.loads(json.dumps(kit["skill"])), TARGET[BLOCK]) == (2, 0)
    if a.check:
        ok = done and worded and aimed
        print("Dark Binding as this script writes it:", "there" if ok else "NOT there")
        sys.exit(0 if ok else 1)
    if not done:
        n = walk(kit["skill"]["effect"], a.bind, a.ap)
        if n != 2:
            sys.exit(f"{n} orbs patched, expected 2 (aimed at a champion, and down the cast's line): the kit changed")
        if a.cd is not None:
            kit["skill"]["cooltime"] = a.cd
    if not done or not aimed:
        found, _ = retarget(kit["skill"], TARGET[BLOCK])
        if found != 2:
            sys.exit(f"{found} orbs found, expected 2: the kit changed")
        open(lp(a.out or KIT), "w", encoding="utf-8", newline="").write(dump(kit, raw))
    if not worded and not a.out:
        for lang, pairs in WORDS.items():
            s = q[lang]
            for old, new in pairs + ([] if BLOCK else PASS_WORDS[lang]):
                if old not in s:         # this piece is rewritten already
                    continue
                if s.count(old) != 1:
                    sys.exit(f"{lang}: {old!r} not found once in Q's text")
                s = s.replace(old, new)
            # the numbers the retune changed: the damage's AP share and the root's seconds
            share, secs = NUMBERS[lang]
            for form, was, now in ((share, 60, a.ap), (secs, "2", None if a.bind is None else f"{a.bind / 60:g}")):
                if now is None or form.format(now) in s:
                    continue
                if s.count(form.format(was)) != 1:
                    sys.exit(f"{lang}: {form.format(was)!r} not found once in Q's text")
                s = s.replace(form.format(was), form.format(now))
            text[lang]["description"]["league_morgana"]["skill"] = s
        open(lp(TEXT), "w", encoding="utf-8", newline="").write(dump(text, traw))
    print("Dark Binding as this script writes it:", "already there" if done and worded and aimed else "written",
          a.out or "")


if __name__ == "__main__":
    main()
