#!/usr/bin/env python3
"""league_ahri made to play like League's current Ahri (the user, 2026-10-24: 「你分析分析有哪些地方和英雄联盟不一样的话
需要补附加包的话也补」; League wiki, patch 25.x):

  passive Essence Theft: League's current version instead of the old one (a charge per spell cast that hit; at three
          charges the next spell healed per enemy hit). Kills she lands on minions and monsters stack an essence; the
          ninth heals her (k_heal + k_ap% AP) - the kill check is league_jinx's ("Kill trigger"), on her basic
          attack's orb (champion-data: one twin of any unit; Orb of Deception's pass and the fires are not checked: a
          line hitting several units shares one flag, so a survivor hides the kills). An enemy champion she damaged
          dies within p_win ticks, by anyone's hand -> she heals t_heal + t_ap% AP (league_viego's takedown window:
          one per window). Her sixth essence shows the old essence picture (et_ready).
  ult     Spirit Rush: League's recast window instead of three charges refilled one by one. The first cast opens
          r_win ticks with two more casts; each cast while one is left caps the ult's cooldown at r_gap ticks
          (a 2-tick `ult_cooldown_mult`, champion-data section 5); the last cast, or the window running out, leaves
          the full cooltime. A takedown while the window is open keeps it open at least r_more ticks more and gives
          one more cast (three at most stored), its cooldown capped again.
  skill2  Charm: no damage amplification (League has none); the charmed champion is slowed e_slow% for the charm
          (League: 65%), walking slowly toward her.
  skill   Fox-Fire: the 40% move speed decays over w_haste ticks (League: 2 s; was 1.5 s).

The takedown window's reward runs from watchers the attack, the casts and the ult hang on her (a 2-tick `tk_go` flag
the window raises; the first watcher to see it takes it off and rewards), so the trees the game copies every tick
(skill, skill2) carry only the small per-hit mark. addons/league_ahri reads every kill and assist natively instead:
its copy drops the marks and the kill check and raises tk_go / k_go itself (make_override.py there).

    python tools/fix/ahri_league.py [--check] [--set key=value ...]

Run once on the old kit (it refuses a kit already converted, --check says which it is).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_ahri.data_champion")
N = "league_ahri_"
# Numbers = v4 of the classic-SDK simulations (C:/t/ar_sim, kd.py --lane 2 against the five base mages, both sides,
# 3 lineups, 2026-10-24): the old kit +3.17 on seeds 1-8; the pack's mid peers league_lux +3.12, league_annie +2.38,
# league_syndra +1.40 on the same games. This kit with r_cd 4200 and heals 60 / 120 +1.61 (her heal 1262 -> 853 a
# game), r_cd 3600 +1.93, plus heals 80 / 160 +2.67 (= P).
P = {
    # passive (League: 9 minion/monster kills -> 35-95 + 20% AP; a champion takedown within 3 s -> 75-165 + 30% AP)
    "k_heal": 80, "k_ap": 20, "t_heal": 160, "t_ap": 30, "p_win": 180,
    # ult (League: 3 casts within 15 s, 1 s apart; a takedown +1 cast, up to 10 s more; cd 140/120/100 s)
    "r_cd": 3600, "r_win": 900, "r_gap": 60, "r_more": 600,
    # Charm (League: 65% slow for the charm)
    "e_slow": 65,
    # Fox-Fire (League: 40% decaying over 2 s)
    "w_haste": 120,
}
NONE = {"type": "Combine", "effects": []}
GO = 60                         # ticks a reward flag waits for the next watcher (one hangs on every action of hers)
KILLS = ["et1", "et2", "et3", "et4", "et5", "et_ready", "et7", "et8"]      # essences 1..8; et_ready = the picture
OLD = ("et_heal", "et_ready", "et1", "et2", "et_lock_q", "et_lock_w", "et_lock_e", "et_lock_r", "et_heal_lock")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": N + buff, "effect_buff": yes, "effect_none": no or NONE}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": N + name}


def add(name, tick=None, **stats):
    state = {"name": N + name, "duration": {"Time": {"tick": tick}} if tick else "Permanent", **stats}
    return {"type": "AddCasterBuff", "buff_state": state, "only_to_enemy": False}


def readd(name, tick, **stats):
    return combine(rm(name), add(name, tick, **stats))


def on_self(*effects):
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
            "apply_type": "AroundCaster", "effects": list(effects)}


def casted(tick, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": tick, "period": 1, "effects": list(effects)}


def heal(amount, ap):
    return combine({"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"},
                   {"type": "CasterViewEffect", "name": N + "heal"}, {"type": "Sfx", "name": N + "heal"})


# ---------------------------------------------------------------- the old passive out
def is_old(o):
    """The old Essence Theft: a cast's spend (SwitchByBuff et_ready -> take the charges, open et_heal) or a hit's
    heal-or-count (SwitchByBuff et_heal)."""
    if not isinstance(o, dict) or o.get("type") != "SwitchByBuff":
        return False
    if o["buff_name"] == N + "et_heal":
        return True
    return o["buff_name"] == N + "et_ready" and N + "et_heal" in json.dumps(o["effect_buff"])


def strip(o):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if is_old(v):
                out[k] = NONE
            else:
                out[k] = strip(v)
        return out
    if isinstance(o, list):
        return [strip(v) for v in o if not is_old(v)]
    return o


# ---------------------------------------------------------------- the passive's new parts
def _counter(top):
    """SwitchByBuff et8 top (SwitchByBuff et7 +et8 (SwitchByBuff et_ready +et7 (... SwitchByBuff et1 +et2 +et1)))."""
    node = add(KILLS[0])
    for i in range(1, len(KILLS)):
        node = sw(KILLS[i - 1], add(KILLS[i]), node)
    return sw(KILLS[-1], top, node)


def kill_check(orb, reward):
    """league_jinx's kill check on any unit the orb strikes: a twin with the orb's flight."""
    flag = "kc"
    eff = combine(add(flag, 7),
                  {"type": "AddCasted", "casted_type": "Poison", "duration": 3, "period": 1, "effects": [rm(flag)]},
                  {"type": "WithSelf", "effects": [{"type": "Delayed", "tick": 4, "effects": [
                      sw(flag, combine(rm(flag), reward))]}]})
    return {"type": "TargetProjectile", "name": N + "kill_check", "speed": orb["speed"], "y_offset": orb["y_offset"],
            "applied_target": "Enemy", "applied_effects": [{"casting_type": "Targeting", "effect": eff}]}


def mark(p):
    """league_viego's takedown window from one champion hit: the champion keeps p_alive up while he lives; her watcher
    finds it lapsing inside the window (one per window, p_lock) and raises tk_go for the reward watchers."""
    w = p["p_win"]
    return combine(
        casted(w, readd("p_alive", 2)),
        on_self(readd("p_alive", 3),
                casted(w - 2, sw("p_alive", NONE, sw("p_lock", NONE, combine(
                    readd("p_lock", w), readd("p_alive", w), readd("tk_go", GO)))))))


def champion_twin_of(orb, effect):
    """An unseen twin of a homing orb that strikes only champions."""
    return {"type": "TargetProjectile", "name": N + "mark", "speed": orb["speed"], "y_offset": orb["y_offset"],
            "applied_target": "EnemyChampion", "applied_effects": [{"casting_type": "Targeting", "effect": effect}]}


def line_twin_of(line, effect):
    """An unseen twin of a line that strikes only champions (the same flight, no return)."""
    t = {k: v for k, v in line.items() if k not in ("applied_effects", "end_effects", "name", "applied_target")}
    t.update(name=N + "mark", applied_target="EnemyChampion",
             applied_effects=[{"casting_type": "Targeting", "effect": effect}], end_effects=[])
    return t


def takedown_reward(p):
    return combine(
        heal(p["t_heal"], p["t_ap"]),
        sw("r_win", combine(add("r_win", p["r_more"]),
                            sw("r_c2", add("r_c3"), sw("r_c1", add("r_c2"), add("r_c1"))),
                            cap(p))))


def cap(p):
    m = int(round(p["r_cd"] * 100 / p["r_gap"] - 100))
    return readd("r_cap", 2, ult_cooldown_mult=m)


def minion_reward(p):
    return combine(*[rm(k) for k in KILLS], heal(p["k_heal"], p["k_ap"]))


def watcher(p, tick):
    """A watcher hung on her: the first to see tk_go (a takedown) or k_go (the add-on's ninth essence) takes it off
    and rewards."""
    return on_self(casted(tick, combine(sw("tk_go", combine(rm("tk_go"), takedown_reward(p))),
                                        sw("k_go", combine(rm("k_go"), minion_reward(p))))))


# ---------------------------------------------------------------- edits
def projectiles(o, name, out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        if o.get("name") == N + name and "Projectile" in o.get("type", ""):
            out.append(o)
        for v in o.values():
            projectiles(v, name, out)
    elif isinstance(o, list):
        for v in o:
            projectiles(v, name, out)
    return out


def champion_fires(o, name, out=None):
    """Projectiles called `name` under a RandomTarget that picks enemy champions."""
    out = [] if out is None else out
    if isinstance(o, dict):
        if o.get("type") == "RandomTarget" and o.get("casting_target") in ("EnemyChampion", "EnemyChampionInCC"):
            out += [x for x in o["effects"] if x.get("name") == N + name]
        for v in o.values():
            champion_fires(v, name, out)
    elif isinstance(o, list):
        for v in o:
            champion_fires(v, name, out)
    return out


def first_effect(proj):
    return proj["applied_effects"][0]["effect"]


def append(proj, effect):
    e = first_effect(proj)
    assert e["type"] == "Combine", proj["name"]
    e["effects"].append(effect)


def convert(d, p):
    d = strip(d)
    assert not any(N + n in json.dumps(d[s]) for s in ("attack", "skill", "skill2", "ult")
                   for n in ("et_heal", "et_lock", "et2\"")), "old passive left"
    # attack: the kill check and the champion mark beside the orb, a watcher
    a = d["attack"]["effect"]["effects"]
    orb = [x for x in a if x.get("name") == N + "orb"][0]
    a.insert(a.index(orb) + 1, kill_check(orb, _counter(minion_reward(p))))
    a.insert(a.index(orb) + 2, champion_twin_of(orb, mark(p)))
    a.append(watcher(p, 150))
    # skill: a mark on every fire picked among champions, a champion twin beside each Orb of Deception, a watcher
    fires = champion_fires(d["skill"], "w_fire")
    assert len(fires) == 6, len(fires)
    for f in fires:
        append(f, mark(p))
    for holder in _holders(d["skill"], "q_out"):
        i = next(k for k, x in enumerate(holder) if x.get("name") == N + "q_out")
        holder.insert(i + 1, line_twin_of(holder[i], mark(p)))
    d["skill"]["effect"]["effects"].append(watcher(p, 200))
    _haste(d["skill"], p)
    # skill2: no damage amp, the slow; the mark (the kiss strikes champions only); a watcher
    kiss = projectiles(d["skill2"], "e_kiss")
    assert len(kiss) == 1
    e = first_effect(kiss[0])["effects"]
    amp = [x for x in e if x.get("type") == "AddBuff" and x["buff_state"]["name"] == N + "e_amp"]
    assert len(amp) == 1
    charm = [x for x in e if x.get("type") == "Charm"][0]
    amp[0]["buff_state"] = {"name": N + "e_slow", "duration": {"Time": {"tick": charm["tick"]}},
                            "move_speed_mult": -p["e_slow"]}
    e.append(mark(p))
    d["skill2"]["effect"]["effects"].append(watcher(p, 200))
    # ult: the recast window, a mark on every bolt picked among champions, a watcher
    u = d["ult"]
    u["cooltime"] = p["r_cd"]
    u.pop("cooltime_use_count", None)
    bolts = champion_fires(u, "r_bolt")
    assert len(bolts) == 3, len(bolts)
    for b in bolts:
        append(b, mark(p))
    window = combine(
        sw("r_win",
           sw("r_c3", rm("r_c3"), sw("r_c2", rm("r_c2"), rm("r_c1"))),
           combine(rm("r_c1"), rm("r_c2"), rm("r_c3"), readd("r_win", p["r_win"]), add("r_c1"), add("r_c2"))),
        {"type": "Delayed", "tick": 1, "effects": [sw("r_win", sw("r_c1", cap(p)))]})
    u["effect"]["effects"].insert(0, window)
    u["effect"]["effects"].append(watcher(p, 300))
    return d


def _holders(o, name, out=None):
    """Effect lists holding a projectile called `name`."""
    out = [] if out is None else out
    if isinstance(o, dict):
        for v in o.values():
            _holders(v, name, out)
    elif isinstance(o, list):
        if any(isinstance(x, dict) and x.get("name") == N + name for x in o):
            out.append(o)
        for v in o:
            _holders(v, name, out)
    return out


def _haste(o, p):
    """Fox-Fire's 20% + 20% move speed: the halves last w_haste and w_haste / 2 ticks."""
    found = []

    def walk(x):
        if isinstance(x, dict):
            b = x.get("buff_state")
            if isinstance(b, dict) and b.get("name") in (N + "w_haste1", N + "w_haste2"):
                found.append(b)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(o)
    assert len(found) == 2, len(found)
    for b in found:
        b["duration"] = {"Time": {"tick": p["w_haste"] if b["name"].endswith("1") else p["w_haste"] // 2}}


def done(d):
    return N + "r_win" in json.dumps(d["ult"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--src", default=PATH)
    ap.add_argument("--out", default=PATH)
    a = ap.parse_args()
    p = dict(P)
    for kv in a.set:
        k, v = kv.split("=")
        assert k in p, k
        p[k] = int(v)
    raw = open(lp(a.src), "rb").read()
    d = json.loads(raw.decode("utf-8-sig"))
    if a.check:
        print("converted" if done(d) else "old kit")
        return
    if done(d):
        sys.exit("already converted (run it on the old kit: git show <rev>:league/champion/league_ahri.data_champion)")
    d = convert(d, p)
    text = json.dumps(d, ensure_ascii=False, indent=2)
    if b"\r\n" in raw:
        text = text.replace("\n", "\r\n")
    open(lp(a.out), "wb").write(text.encode("utf-8"))
    for s in ("attack", "skill", "skill2", "ult"):
        print(s, nodes(d[s]["effect"]), "nodes")


def nodes(o):
    if isinstance(o, dict):
        return ("type" in o) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


if __name__ == "__main__":
    main()
