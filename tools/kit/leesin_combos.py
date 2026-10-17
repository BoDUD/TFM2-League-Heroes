#!/usr/bin/env python3
"""Lee Sin's combos (the user, 2026-10-02: "盲僧我们加点绝招 比如QRQ 回旋踢 QQAE RQQ ... 因为现在不能摸眼瞬移", then
"盲僧连招帮我全加进去吧").

    python tools/kit/leesin_combos.py [--check]

The AI casts one slot at a time, so each combo is played by the slot whose skill it spends, shaped by what came
before it:
- QQAE: when Sonic Wave's dash (Q2) lands with an enemy champion in reach, Lee opens a window (q2_on, 150 ticks);
  Tempest (E) cast in it punches first - the attack's pose with a 100% AD hit on a champion beside him - then plays
  E's pose and E itself (damage, slow, Iron Will).
- QRQ (the roundhouse kick): Dragon's Rage (R) cast while Q is on cooldown (he threw it within 6 s: q_cd, a flag of
  Q's cooldown that Q's casts set) kicks as R always does and then dashes after the champion while it flies (a homing
  dash at 7000 a tick: the kicked champion flies 3000 a tick for 18 ticks) for a follow-up strike with Q2's picture
  and sound. A window after Q2 would hardly ever meet R: in 12 simulated games R was ready at 6 of 53 Q2 landings,
  and the AI cast it about 4.5 s later.
- RQQ: R cast while Q is ready throws Sonic Wave right after the kick (q_throw, the palm of Q's animation alone:
  tools/art/leesin_throw_tag.py) at the champion in the air - a homing wave, so it cannot miss the kicked target -
  and dashes after it on the hit.
So every R ends in QRQ's chase or RQQ's wave.
No slot is held by a flag: the AI casts a slot whose branch is empty anyway (in a first version that held E and R
for the skills a combo spent, the simulation showed empty 40-tick E casts in fights and an empty ult after every
QRQ, each also starting the slot's real cooldown). So the combos never spend another slot's cooldown, the slots
unlock with their levels as before (E at 3, R at 5), and RQQ's wave does not put Q on cooldown.
E branches on start_timing 1 (its effects follow 16 ticks later, on its tick 17 as before), so the punch's pose
replaces E's before it shows; every step plays its own animation (CasterAnimation holds him meanwhile), its hit on
the frame that shows it. The kit file was hand-written; the script refuses to run twice (the flags mark a combo
kit). --check only verifies that the file holds the combos.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_leesin.data_champion")
P = "league_leesin_"
Q_CD = 360                                   # Q's cooldown, mirrored by the q_cd flag
WINDOW = 150                                 # q2_on: E cast this long after Q2 lands plays QQAE
REACH = 12000                                # + both radii: a champion beside Lee where Q2 landed
CHASE = 7000                                 # the dashes after a kicked champion (it flies 3000 a tick for 18)
FOLLOW = (30, 60)                            # QRQ's strike after the chase (Q2 itself is 50 + 100%)
WAVE = 8000                                  # RQQ's homing Sonic Wave (Q's line flies 4500)
# animation ticks (league_leesin#anim.fanim): attack hits on its 12th, skill2 stomps on its 17th, ult kicks on its
# 18th, q_throw's palm shows on its 4th
PUNCH, STOMP, KICK, PALM = 12, 17, 18, 4


def n(x):
    return P + x


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


NONE = combine()


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def canim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def beside(*effects):
    """The effects on one enemy champion in reach (a search: its effects act on the champion found)."""
    return {"type": "RandomTarget", "range": REACH, "casting_target": "EnemyChampion", "from_projectile": False,
            "effects": list(effects)}


def dash(end):
    return {"type": "MoveToTarget", "speed": CHASE, "range": 110000, "end_effects": end}


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def build(k):
    q, e, r = k["skill"], k["skill2"], k["ult"]
    # ---- what the combos borrow, read before anything changes
    flurry = [x for x in q["effect"]["effects"] if x.get("type") == "AddCasterBuff"]
    assert [x["buff_state"]["name"] for x in flurry] == [n("flurry"), n("flurry_2")]
    assert e["start_timing"] == STOMP and e["effect"]["type"] == "Combine"
    stomp, w = e["effect"]["effects"][:-1], e["effect"]["effects"][-1]
    assert [x["type"] for x in stomp] == ["Sfx", "Sfx", "CasterViewEffect", "AddCasterBuff", "AddCasterBuff",
                                         "RangeEffect", "AddCasterBuff"], stomp
    assert w["type"] == "SwitchByBuff" and w["buff_name"] == n("w_cd")      # Safeguard, checked by every action
    kick = next(x for x in r["effect"]["effects"] if x.get("type") == "Delayed" and x["tick"] == KICK - 1)["effects"]
    assert [x["type"] for x in kick] == ["Attack", "Knockback", "ViewEffect", "TargetSfx", "SwitchByBuff"]
    assert r["start_timing"] == 1
    q_line = find(q["effect"], lambda o: o.get("name") == n("q_wave"))
    q_hit = [a["effect"] for a in q_line["applied_effects"][:3]]
    assert [x["type"] for x in q_hit] == ["Attack", "ViewEffect", "TargetSfx"]
    q2 = find(q["effect"], lambda o: o.get("type") == "MoveToTarget")
    q2_end = list(q2["end_effects"])
    assert [x["type"] for x in q2_end] == ["Attack", "ViewEffect", "TargetSfx", "AddCasterBuff", "AddCasterBuff"]

    # ---- Q: its casts set q_cd (read by R); Q2 landing beside an enemy champion opens E's window
    q["effect"]["effects"].insert(0, flag("q_cd", Q_CD))
    q2["end_effects"] = q2_end + [unflag("q2_on"), beside(flag("q2_on", WINDOW))]

    # ---- E: in the window, the punch and then the stomp (QQAE); else E on its tick 17 as before. Safeguard's check
    # stays on tick 17 either way, written once (the game copies skill and skill2 whole every tick: keep them small)
    qqae = combine(canim("attack", 20),
                   delayed(PUNCH - 1, beside(attack(0, 100), view("hit"), tsfx("attack_hit"))),
                   delayed(21, canim("skill2", 40)),
                   delayed(21 + STOMP, *stomp))
    e["start_timing"] = 1
    e["effect"] = combine(sw("q2_on", qqae, delayed(STOMP - 1, *stomp)), delayed(STOMP - 1, w))

    # ---- R (effects on its tick 1, the kick on 18): with Q on cooldown the chase (QRQ); with Q ready the palm and a
    # homing wave right after the kick, the dash on the hit (RQQ)
    qrq = delayed(25, canim("q2", 31), sfx("q2_cast"),
                  dash([attack(*FOLLOW), view("q2_hit"), tsfx("q2_hit"), *flurry]))
    wave = {"type": "TargetProjectile", "name": n("q_wave"), "speed": WAVE, "y_offset": 5000,
            "applied_target": "EnemyChampion", "applied_effects": [{"casting_type": "Targeting", "effect": x} for x in [
                *q_hit, delayed(8, sfx("q2_cast"), canim("q2", 31), dash(q2_end))]]}
    rqq = delayed(22, canim("q_throw", 20), sfx("q_cast"), delayed(PALM, wave))
    r["effect"]["effects"].append(sw("q_cd", qrq, rqq))
    return k


def has_combos(k):
    s = json.dumps(k)
    return all(n(x) in s for x in ("q_cd", "q2_on")) and '"q_throw"' in s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        ok = has_combos(k)
        print("league_leesin.data_champion:", "combos in" if ok else "NO combos")
        sys.exit(0 if ok else 1)
    if has_combos(k):
        sys.exit("league_leesin.data_champion already has the combos")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_leesin.data_champion with QQAE, QRQ and RQQ")


if __name__ == "__main__":
    main()
