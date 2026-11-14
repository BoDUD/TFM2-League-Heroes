"""league_ekko Q Timewinder: the device stops and opens its field on the first enemy champion (League: "It expands at max
range or upon hitting an enemy champion"); until now it always flew its whole 65000 and opened at the far end.

    python tools/fix/parity_ekko_q.py [<worktree>] [--out file]

The kit is hand-written JSON. In skill's effect:
  * `league_ekko_q_out` (the device with the picture) becomes a non-penetrating line on `EnemyChampion` with no applied
    effects: it flies through minions and monsters, stops on the first enemy champion or at its range, and its
    end_effects (unchanged: the field's picture, sound and zone, the return 45 ticks later) run where it stopped. One
    more end effect: a Delayed 1 raises the caster flag `league_ekko_q_stop` (STOP_T ticks, the rest of any flight);
  * the damage on the way out moves to a hidden twin on the same line, `league_ekko_q_wave` (the old projectile's
    speed, range, circle, target and applied effects, penetrating, no picture): it hits everything the device passes,
    the champion it stops on too (same tick: the flag comes a tick later), and behind `league_ekko_q_stop` nothing -
    what stands past the stopped device is not hit on the way out, as in League;
  * the cast takes `league_ekko_q_stop` off first.
Run again it finds the twin already there and changes nothing.
"""
import argparse
import copy
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import parity_jsonio as jsonio  # noqa: E402

ID = "league_ekko"
STOP_T = 22   # the twin's whole flight is 65000 / 3500 = 19 ticks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree", nargs="?", default=ROOT)
    ap.add_argument("--out")
    a = ap.parse_args()
    path = f"{a.worktree}/league/champion/{ID}.data_champion"
    kit, meta = jsonio.load(path)
    eff = kit["skill"]["effect"]["effects"]
    if any(e.get("name") == f"{ID}_q_wave" for e in eff):
        print("already done")
        return
    assert [e["type"] for e in eff] == ["Sfx", "LinearProjectile"], [e["type"] for e in eff]
    out = eff[1]
    assert out["name"] == f"{ID}_q_out" and out["penetrate"] is True and out["applied_target"] == "EnemyWithoutTower"
    assert STOP_T > out["range"] // out["speed"] + 2
    wave = OrderedDict()
    for k, v in out.items():
        if k == "name":
            wave[k] = f"{ID}_q_wave"
        elif k == "applied_effects":
            wave[k] = [OrderedDict([("casting_type", "Targeting"), ("effect", OrderedDict([
                ("type", "SwitchByBuff"), ("buff_name", f"{ID}_q_stop"),
                ("effect_buff", OrderedDict([("type", "Combine"), ("effects", [])])),
                ("effect_none", copy.deepcopy(x["effect"]))]))]) for x in v]
        elif k == "end_effects":
            wave[k] = []
        else:
            wave[k] = copy.deepcopy(v)
    out["penetrate"] = False
    out["applied_target"] = "EnemyChampion"
    out["applied_effects"] = []
    out["end_effects"].append(OrderedDict([("type", "Delayed"), ("tick", 1), ("effects", [OrderedDict([
        ("type", "AddCasterBuff"),
        ("buff_state", OrderedDict([("name", f"{ID}_q_stop"), ("duration", OrderedDict([("Time", OrderedDict([("tick", STOP_T)]))]))])),
        ("only_to_enemy", False)])])]))
    kit["skill"]["effect"]["effects"] = [eff[0], OrderedDict([("type", "RemoveCasterBuff"), ("name", f"{ID}_q_stop")]),
                                         wave, out]
    jsonio.save(a.out or path, kit, meta)
    print("written", a.out or path)


if __name__ == "__main__":
    main()
