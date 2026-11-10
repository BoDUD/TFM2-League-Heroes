#!/usr/bin/env python3
"""Xerath's R (Rite of the Arcane) ends when there is nothing left to shoot, and refunds half its cooldown when no shell
was fired (League's rule). Player report 2026-11-10: 「泽拉斯开大后如果范围内英雄死了或者没英雄会原地罚站很久」.
Patches league/champion/league_xerath.data_champion in place (tools/kit/build_xerath.py is stale against the data: not
to be rerun); then run addons/league_sylas/make_override.py (Sylas's stolen copy of the ult).

    python -I tools/kit/xerath_r_end.py           # idempotent: a patched file is left as it is

Before: the channel (r_chan 360 ticks, ult_loop 330) fired from a 6-tick AddCasted at a RandomTarget enemy champion
within 220000; with none (all dead, out of range) nothing fired and nothing ended it - he stood out the whole 6 s.
After, in the same AddCasted, before the shot:
- r_any: a 1-tick flag set by a RandomTarget enemy champion within the shot's reach (read in the same tick, as r_go is);
- found: the miss streak (r_miss / r_grace) is cleared;
- none: the first miss starts the streak (r_miss for the channel, r_grace GRACE ticks); a miss with r_miss up and
  r_grace gone (a flag of n ticks is seen on n - 1 of them: the miss GRACE ticks after the first) ends the channel the
  way crowd control does (r_end picture and sound);
- an end with no shell fired (no r_s1, which the first shell sets) puts a 3-tick r_refund flag on him with
  ult_cooldown_mult 100: the ult's remaining cooldown capped at cooltime / 2 (the other kits' refunds use 4900 the same
  way). Crowd control breaking a channel before its first shell refunds too (League: "ends without any recasts").
"""
import json
import os
import sys

ID = "league_xerath"
GRACE = 30          # ticks with no enemy champion in reach before the channel ends
REACH = 220000      # the shot's RandomTarget range
REFUND_MULT = 100   # 3-tick ult_cooldown_mult: remaining cooldown <= cooltime / (1 + 100 / 100)
REFUND_T = 3


def n(x):
    return f"{ID}_{x}"


def rm(x):
    return {"type": "RemoveCasterBuff", "name": n(x)}


def flag(x, t, **extra):
    st = {"name": n(x), "duration": {"Time": {"tick": t}}}
    st.update(extra)
    return {"type": "AddCasterBuff", "buff_state": st, "only_to_enemy": False}


def sw(x, yes, no):
    return {"type": "SwitchByBuff", "buff_name": n(x), "effect_buff": yes, "effect_none": no}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def refund_if_no_shot():
    return sw("r_s1", combine(), flag("r_refund", REFUND_T, ult_cooldown_mult=REFUND_MULT))


def main(repo):
    path = os.path.join(repo, "league", "champion", f"{ID}.data_champion")
    raw = open(path, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    ult = d["ult"]["effect"]["effects"]
    text = json.dumps(d["ult"])
    if n("r_miss") in text:
        print("already patched:", path)
        return 0
    # the cast clears the new flags too
    first_add = next(i for i, e in enumerate(ult) if e.get("type") == "AddCasterBuff"
                     and e["buff_state"]["name"] == n("r_chan"))
    ult[first_add:first_add] = [rm("r_miss"), rm("r_grace"), rm("r_any")]
    rng = next(e for e in ult if e.get("type") == "RangeEffect")
    loop = rng["effects"][0]                       # Delayed 30: the channel's loop
    assert loop["type"] == "Delayed" and loop["tick"] == 30, loop["type"]
    body = loop["effects"][0]["effect_buff"]["effects"]
    casted = next(e for e in body if e.get("type") == "AddCasted")
    assert casted["period"] == 6, casted["period"]
    per = casted["effects"]
    assert len(per) == 2, len(per)
    cc, shot = per
    # crowd control's end: the end Combine inside the AllyChampionInCC RandomTarget
    cc_end = cc["effect_buff"]["effects"][0]
    assert cc["effect_buff"]["type"] == "RandomTarget" and cc["effect_buff"]["casting_target"] == "AllyChampionInCC"
    assert cc_end["type"] == "Combine" and cc_end["effects"][0] == rm("r_chan"), cc_end["effects"][0]
    end_tail = [e for e in cc_end["effects"]]
    cc_end["effects"] = [refund_if_no_shot(), *end_tail, rm("r_miss"), rm("r_grace")]
    # the no-target end: the same end as crowd control's
    no_target_end = combine(refund_if_no_shot(), *[json.loads(json.dumps(e)) for e in end_tail], rm("r_miss"),
                            rm("r_grace"))
    probe = combine(
        rm("r_any"),
        {"type": "RandomTarget", "range": REACH, "casting_target": "EnemyChampion", "from_projectile": False,
         "effects": [flag("r_any", 1)]},
        sw("r_any",
           combine(rm("r_miss"), rm("r_grace")),
           sw("r_miss",
              sw("r_grace", combine(), no_target_end),
              combine(flag("r_miss", 360), flag("r_grace", GRACE)))))
    per[:] = [cc, sw("r_chan", probe, combine()), shot]
    # a shell fired: the miss streak is over
    go = shot["effect_buff"]["effect_none"]["effects"]
    fired = next(e for e in go if e.get("type") == "SwitchByBuff" and e["buff_name"] == n("r_go")
                 and e["effect_buff"].get("effects"))
    fired["effect_buff"]["effects"][0:0] = [rm("r_miss"), rm("r_grace")]
    out = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    open(path, "wb").write(out.encode("utf-8"))
    print("patched:", path)
    return 0


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else REPO))
