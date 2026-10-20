#!/usr/bin/env python3
"""Caitlyn's League combos W -> Q and E -> Q: Piltover Peacemaker locks on the trapped or netted champion.

    python tools/fix/combo_caitlyn.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Caitlyn follows a snapped trap or a landed net with Q on that
champion: rooted (or slowed by the net) it cannot step out of the shot. Here the trap's bite and the net already arm
the Headshot of her next attack, but Q - a `Direction` cast on `EnemyWithoutTower`, its aim locked 8 ticks before the
shot on `RandomTarget {100000, EnemyChampion}` (champion-data.md section 7, "A piercing round at where a champion
stood") - picked any champion in reach at random, so it often went past the one she had just caught.

Design (pure data, the slot plays it; league_morgana Q's tiers of `RandomTarget`, Fox-Fire's w_pick checks):
  * The net's hit (`league_caitlyn_e_net`, champion-only, inside her attack) adds the caster flag
    `league_caitlyn_q_net` for NET_T ticks, beside `hs_net` (which the Headshot spends; this one is Q's alone). The
    trap's bite already adds `league_caitlyn_hs_trap` for the root (90 ticks): Q reads it, nobody else's flag moves.
  * Q's aim (its `Delayed 15`, the lock) asks three times, each only while nothing was picked (the 10-tick `q_aim`
    flag the pick sets, read on the same tick):
      1. trap window (`hs_trap`): `RandomTarget {100000, EnemyChampionInCC}` - the rooted champion;
      2. net window (`q_net`): `RandomTarget {NET_RANGE, EnemyChampionRecentlyAttacked}` - the champion her team has
         just hurt within her attack range: the one the net hit (she hops 30000 away from it, it is slowed 50%);
      3. otherwise the old `RandomTarget {100000, EnemyChampion}`, and with no champion the bolt still takes the
         cast's way on tick 23 (`SwitchByBuff q_aim`, unchanged).
So Q, which the AI casts as soon as it is ready (any enemy within 120000), goes to the caught champion while the trap
or the net holds; outside the two windows nothing changes.
Why it is safe: no damage, timing or cooldown changes; Q always fires one bolt (the AI never casts a no-op), aimed the
same way (the hidden lob, dodgeable). The new flag is invisible (no `view_buffs` entry), timed, and death clears it.
The only copies are the lob with its bolt (about 13 nodes each, two more; Q is small). Caitlyn has no add-on copy (no
addons/league_caitlyn*) and no other script rebuilds Q or the net. Idempotent: the lock and the net's entry are
rebuilt from the lob on every run, so a second run writes the same bytes; --check exits 1 when the file differs from
what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_caitlyn.data_champion")
N = "league_caitlyn_"
NET = N + "q_net"
TRAP = N + "hs_trap"
AIM_FLAG = N + "q_aim"
NET_T = 108        # ticks from the net's hit (= hs_net, 1.8 s): her net action is 34 ticks, Q locks 15 into its cast
NET_RANGE = 65000  # her attack range: the netted champion is within it after the hop
REACH = 100000     # the kit's lock reach
LOCK_AT = 15
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def find(o, pred, acc):
    if isinstance(o, dict):
        if pred(o):
            acc.append(o)
        for v in o.values():
            find(v, pred, acc)
    elif isinstance(o, list):
        for v in o:
            find(v, pred, acc)
    return acc


def is_ours(x):
    return NET in json.dumps(x)


def pick(rng, target, body):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": copy(body)}


def unless_aimed(effect):
    return {"type": "SwitchByBuff", "buff_name": AIM_FLAG, "effect_buff": copy(NONE), "effect_none": effect}


def lock(body):
    """The three tiers; `body` is the pick's effects: the 10-tick q_aim flag and the hidden lob carrying the bolt."""
    return [{"type": "SwitchByBuff", "buff_name": TRAP, "effect_buff": pick(REACH, "EnemyChampionInCC", body),
             "effect_none": copy(NONE)},
            unless_aimed({"type": "SwitchByBuff", "buff_name": NET,
                          "effect_buff": pick(NET_RANGE, "EnemyChampionRecentlyAttacked", body),
                          "effect_none": copy(NONE)}),
            unless_aimed(pick(REACH, "EnemyChampion", body))]


def body_of(effects):
    """The champion pick's effects, from the original single pick or from this script's last tier."""
    if len(effects) == 1:
        p = effects[0]
        assert p["type"] == "RandomTarget" and p["casting_target"] == "EnemyChampion" and p["range"] == REACH
        body = p["effects"]
    else:
        assert len(effects) == 3 and effects[0]["buff_name"] == TRAP, "unknown Q lock"
        body = effects[2]["effect_none"]["effects"]
        assert effects[0]["effect_buff"]["effects"] == body, "Q's tiers differ"
        assert effects[1]["effect_none"]["effect_buff"]["effects"] == body, "Q's tiers differ"
    assert [x["type"] for x in body] == ["AddCasterBuff", "ParabolicProjectile"], [x["type"] for x in body]
    assert body[0]["buff_state"]["name"] == AIM_FLAG and body[0]["buff_state"]["duration"]["Time"]["tick"] >= 1
    return body


def fix_q(d):
    fx = d["skill"]["effect"]["effects"]
    locks = [x for x in fx if x.get("type") == "Delayed" and x["tick"] == LOCK_AT]
    assert len(locks) == 1, "Q's lock (Delayed 15) not found"
    locks[0]["effects"] = lock(body_of(locks[0]["effects"]))


def fix_net(d):
    nets = find(d["attack"], lambda o: o.get("type") == "TargetProjectile" and o.get("name") == N + "e_net", [])
    assert len(nets) == 1, "the net not found"
    net = nets[0]
    assert net["applied_target"] == "EnemyChampion"
    hit = [a for a in net["applied_effects"] if not is_ours(a)]
    assert any(a["effect"].get("type") == "AddCasterBuff" and a["effect"]["buff_state"]["name"] == N + "hs_net"
               for a in hit), "the net no longer arms the Headshot"
    net["applied_effects"] = hit + [{"casting_type": "Targeting", "effect": {
        "type": "AddCasterBuff", "buff_state": {"name": NET, "duration": {"Time": {"tick": NET_T}}},
        "only_to_enemy": False}}]


def apply(d):
    traps = find(d, lambda o: o.get("type") == "AddCasterBuff" and o["buff_state"]["name"] == TRAP, [])
    assert traps, "the trap's bite no longer adds hs_trap"
    fix_net(d)
    fix_q(d)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(apply(json.loads(raw)), ensure_ascii=False, indent=2).replace("\n", nl) + nl
    if a.check:
        done = text == raw
        print("already done" if done else "W -> Q / E -> Q combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: Q locks on the trapped champion (hs_trap), then the netted one ({NET}, {NET_T} ticks, "
          f"within {NET_RANGE}), then any champion as before")


if __name__ == "__main__":
    main()
