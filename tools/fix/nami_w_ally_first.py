#!/usr/bin/env python3
"""Nami's W (Ebb and Flow) heals first: an ally beside her, else herself, then the stream goes on to an enemy.

    python tools/fix/nami_w_ally_first.py [--check] [--path <data_champion>]

The user (2026-10-27): 「娜美是优先对敌人还是队友使用W技能吗？她一直在自己和敌人之间不停地来回弹这个技能 ... 感觉这更像是一个
消耗（poke）技能 ... 让它变成可以先命中队友然后再弹向敌人」, then picked 「有队友先奶队友，没有就先奶自己，再弹向敌人，不再弹回
娜美」. Until now the stream always hit an enemy first; a random other ally near that target was healed next, and with
nobody there it flew back to Nami and healed her, then looked for an enemy round her again - enemy, Nami, enemy.

The cast stays a `Targeting` on `EnemyWithoutTower` (range 60000): an ally-targeted heal goes out on cooldown, at full
health and out of fights (champion-data.md "Which ally gets an ally skill", league_janna E), so the AI still casts it
when an enemy is in reach. Then (league_janna E's way: a search round her and a caster flag):
  * an allied champion other than her within ALLY of her (`RandomTarget {AllyNotSelf}`, a 2-tick `w_ally` flag): the
    stream flies to that ally (a `TargetProjectile` on `AllyNotSelf`, league_milio E / league_lulu E) - heal 70 + 35% AP,
    Tidecaller's Blessing and Surging Tides' haste - and BOUNCE ticks later an enemy champion within BOUNCE_R of the
    ally takes 65 + 45% AP and the slow, its hit picture being the bounce (every projectile leaves from the caster,
    champion-data.md "A stream that bounces"). Two hits: nothing reads a buff on a unit (`SwitchByBuff` checks the
    caster), so a third hit could not keep off the ally healed first;
  * nobody beside her: she heals and blesses herself (`RangeEffect` on `AllyOnlySelf`), the stream flies from her to an
    enemy champion in reach (league_morgana Q's aim, kept out of the AI's estimate like tools/kit/hide_aim_twins.py)
    or the cast target, and BOUNCE ticks after it lands an allied champion other than her within BOUNCE_R of that
    enemy is healed and blessed - three different units, never back to her.
BOUNCE_R is League's bounce range (875) against her cast range (725): 87500 here for the cast's 60000. The champion-
first searches sit inside a 1-tick `<id>_ai_hide` flag so the AI reads one damage hit and one heal, as before.
Idempotent: the slot's effect is rebuilt from these constants; --check exits 1 when the file differs.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_nami.data_champion")
N = "league_nami_"
ALLY = 60000        # the ally searched round her: her cast range
BOUNCE_R = 87500    # the next unit searched round the one hit (League: 875 against the cast's 725)
BOUNCE = 9          # ticks from a hit to the bounce's hit (the old kit's)
SPEED = 4500
DMG, DMG_AP = 65, 45
HEAL, HEAL_AP = 70, 35
SLOW, SLOW_T = -25, 60
BLESS, BLESS_T = 15, 240
HASTE, HASTE_T = 20, 90


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": N + name, "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": N + name}


def switch(name, buff, none):
    return {"type": "SwitchByBuff", "buff_name": N + name, "effect_buff": buff, "effect_none": none}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def search(target, rng, effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": effects}


def hidden(*effects):
    """Run `effects` in game but keep them out of the AI's estimate (tools/kit/hide_aim_twins.py)."""
    return [flag("ai_hide", 1), switch("ai_hide", combine(*effects), combine()), unflag("ai_hide")]


def on_target(effects):
    return [{"casting_type": "Targeting", "effect": e} for e in effects]


def stream(target, applied):
    return {"type": "TargetProjectile", "name": N + "w_stream", "speed": SPEED, "y_offset": 2000,
            "applied_target": target, "applied_effects": on_target(applied)}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": dict({"name": N + name, "duration": {"Time": {"tick": tick}}}, **fields)}


def heal(kind):
    """The heal on an ally (`Ally`) or on her (`Caster`), Tidecaller's Blessing, Surging Tides' haste, picture, sound."""
    return [{"type": "Heal", "amount": HEAL, "attack_ratio": 0, "ap_ratio": HEAL_AP, "heal_type": kind},
            buff("e_blessing", BLESS_T, attack_mult=BLESS, magic_power_mult=BLESS),
            buff("p_haste", HASTE_T, move_speed_mult=HASTE),
            {"type": "ViewEffect", "name": N + "w_heal"}, {"type": "TargetSfx", "name": N + "w_heal"}]


def hit():
    """The damage on an enemy, the Blessing's slow, picture, sound."""
    return [{"type": "ApAttack", "damage": DMG, "attack_ratio": DMG_AP},
            buff("e_slow", SLOW_T, move_speed_mult=SLOW),
            {"type": "ViewEffect", "name": N + "w_hit"}, {"type": "TargetSfx", "name": N + "w_hit"}]


def bounce(target, effects):
    """BOUNCE ticks after a hit: a `target` unit within BOUNCE_R of the unit hit gets `effects`."""
    return search(target, BOUNCE_R, [{"type": "Delayed", "tick": BOUNCE, "effects": effects}], from_projectile=True)


def bounce_enemy():
    """From the ally: an enemy champion within BOUNCE_R first (a 1-tick `w_b` flag), else any enemy unit there."""
    champ = search("EnemyChampion", BOUNCE_R, [flag("w_b", 1), {"type": "Delayed", "tick": BOUNCE, "effects": hit()}],
                   from_projectile=True)
    return [champ, switch("w_b", combine(), bounce("EnemyWithoutTower", hit()))]


def w_effect():
    to_ally = stream("AllyNotSelf", heal("Ally") + bounce_enemy())
    to_enemy = stream("EnemyWithoutTower", hit() + [bounce("AllyNotSelf", heal("Ally"))])
    herself = {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
               "apply_type": "AroundCaster", "effects": heal("Caster")}
    alone = combine(herself,
                    *hidden(search("EnemyChampion", ALLY, [flag("w_aim", 1), to_enemy])),
                    switch("w_aim", combine(), to_enemy))
    return combine({"type": "Sfx", "name": N + "w_cast"},
                   *hidden(search("AllyNotSelf", ALLY, [flag("w_ally", 2), to_ally])),
                   switch("w_ally", combine(), alone))


TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
AP = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
P, G, O, Y, S = "<#a974ffff>", "<#6aff55ff>", "<#ff9028ff>", "<#ffb900ff>", "<#ef5350ff>"
E = "<>"
# W's tooltip in her five languages (the old one began with the enemy hit and named a 60 + 40% last hit)
SKILL = {
    "zh-hans": f"{O}冲击之潮{E}：水流先治疗身边一名友方英雄（没有则治疗自己）{G}{HEAL}{E} + {AP}{P}{HEAL_AP}% 法术强度{E}的"
               f"{G}生命值{E}，再弹向附近敌人造成{P}{DMG}{E} + {AP}{P}{DMG_AP}% 法术强度{E}的{P}魔法伤害{E}，不会弹回娜美。"
               f"{O}唤潮之佑{E}：被治疗者{Y}4秒{E}内攻击力和法术强度提高{BLESS}%，被击中者{S}减速25%{E}。",
    "zh-hant": f"{O}跳躍水柱{E}：水柱先治療身邊一名友方英雄（沒有則治療自己）{G}{HEAL}{E} + {AP}{P}{HEAL_AP}% 魔法強度{E}的"
               f"{G}生命{E}，再彈向附近敵人造成{P}{DMG}{E} + {AP}{P}{DMG_AP}% 魔法強度{E}的{P}魔法傷害{E}，不會彈回娜米。"
               f"{O}深海恩賜{E}：被治療者{Y}4秒{E}內攻擊力和魔法強度提高{BLESS}%，被擊中者{S}緩速25%{E}。",
    "en": f"{O}Ebb and Flow{E}: water first heals an allied champion beside Nami (herself if none) for {G}{HEAL}{E} + {AP}"
          f"{P}{HEAL_AP}% Ability Power{E}, then bounces to a nearby enemy for {P}{DMG}{E} + {AP}{P}{DMG_AP}% Ability "
          f"Power{E} {P}magic damage{E}; it never bounces back to Nami. {O}Tidecaller's Blessing{E}: the healed ally gains "
          f"{BLESS}% attack and Ability Power for {Y}4s{E}; enemies hit are {S}slowed{E} by 25%.",
    "ko": f"{O}밀물 썰물{E}: 물줄기가 먼저 곁의 아군 챔피언(없으면 나미 자신)의 {G}체력을 {HEAL}{E} + {AP}{P}주문력의 "
          f"{HEAL_AP}%{E} 회복하고, 근처 적에게 튕겨 {P}{DMG}{E} + {AP}{P}주문력의 {DMG_AP}%{E} {P}마법 피해{E}를 입힙니다. "
          f"나미에게 되돌아오지 않습니다. {O}파도 소환사의 축복{E}: 회복된 아군은 {Y}4초{E} 동안 공격력과 주문력이 {BLESS}% "
          f"증가하고, 맞은 적은 {S}25% 둔화{E}됩니다.",
    "ja": f"{O}潮の流れ{E}：水流がまず近くの味方チャンピオン（いなければ自分）の{G}体力を{HEAL}{E} + {AP}{P}魔力の"
          f"{HEAL_AP}%{E}回復し、跳ねて近くの敵に{P}{DMG}{E} + {AP}{P}魔力の{DMG_AP}%{E}の{P}魔法ダメージ{E}。"
          f"ナミには戻らない。{O}潮使いの祝福{E}：回復した味方は{Y}4秒{E}間攻撃力と魔力{BLESS}%増加、当たった敵は"
          f"{S}25%スロウ{E}。",
}


def apply(d):
    d["skill"]["effect"] = w_effect()
    # the stream no longer flies back to her: its picture goes too
    d["view_projectiles"] = [v for v in d["view_projectiles"] if v["name"] != N + "w_return"]
    return d


def apply_text(t):
    for lang, text in SKILL.items():
        t[lang]["description"]["league_nami"]["skill"] = text
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    ap.add_argument("--text", default=TEXT, help="champion.i18n to write W's tooltip into ('' to skip)")
    a = ap.parse_args()
    todo = [(a.path, apply)] + ([(a.text, apply_text)] if a.text else [])
    changed = []
    for path, fix in todo:
        with open(lp(path), "rb") as f:
            raw = f.read().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        bom = "﻿" if raw.startswith("﻿") else ""
        text = bom + json.dumps(fix(json.loads(raw.lstrip("﻿"))), ensure_ascii=False, indent=2).replace("\n", nl) + nl
        if text != raw:
            changed.append(path)
            if not a.check:
                with open(lp(path), "w", encoding="utf-8", newline="") as f:
                    f.write(text)
    if a.check:
        print("already done" if not changed else "Nami's ally-first W not applied: " + ", ".join(changed))
        sys.exit(1 if changed else 0)
    print(", ".join(changed) + f": W heals an ally within {ALLY} of her (else herself) first, then bounces to an enemy"
          if changed else "already done")


if __name__ == "__main__":
    main()
