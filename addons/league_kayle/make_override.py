"""Build the add-on's copy of Kayle from the main pack (her ascension and its wings kept through death).

    python addons/league_kayle/make_override.py

Copies league/champion/league_kayle.data_champion to addons/league_kayle/override/league_kayle.data_champion with two
changes:
  1. passive = the add-on's league_kayle:ascend (no params), which lays the level flags below by her real level and puts
     back the ranks she has reached - and their wings - when death clears them (src/lib.rs);
  2. every level probe becomes a read of a level flag. The main pack tells her level from her maximum health (a shield
     of 123 / 151 / 189 against a hit of 10% of it, then a 100 shield against 99 for damage amplification), so health
     the level table does not hold (items), an enemy hit landing in the probe's 2 ticks or a crit gave a stage early (game
     logs 10-24: rank5 at level 3 9 times of 23, rank12 at levels 6-10 every time, never at 12). Each probe - from its
     WithShield flag `probe_shielded` to the `SwitchByBuff probe_amp` that gives the stage - is replaced by
     `SwitchByBuff league_kayle_lv5 / lv8 / lv12` with the same two branches, so the stage, its ascent picture and
     voice and the next probe come as before, only at the level and 6 ticks sooner (no shields, no hits on herself).
Checks first that the main pack's rank buffs carry the numbers the add-on puts back (rank5 range 27500; rank12 attack
speed 30, move speed 10, range 10000; rank8 and form3 nothing), that every action still reads the once-a-life flag
league_kayle_life the add-on sets and that no probe is left after the rewrite. The tooltip stays the main pack's (it
is at the details panel's length limit), so text/champion.i18n is empty. Run it again whenever the main pack's Kayle
changes.

    python addons/league_kayle/make_override.py --check    # CI: fail if the committed copy is out of date
"""
import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kayle")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import generated  # noqa: E402  --check
MOD_ID = "league_kayle"
# the buffs src/lib.rs puts back, as the main pack adds them
RANKS = {
    "league_kayle_rank5": {"range": 27500},
    "league_kayle_rank8": {},
    "league_kayle_rank12": {"attack_speed_mult": 30, "move_speed_mult": 10, "range": 10000},
    "league_kayle_form3": {},
}
# the probe's shield -> the level flag src/lib.rs lays (LEVEL_FLAGS there)
PROBE_SHIELDS = {123: "league_kayle_lv5", 151: "league_kayle_lv8", 189: "league_kayle_lv12"}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def buff_states(node, out):
    if isinstance(node, dict):
        if node.get("type") == "AddCasterBuff":
            out.append(node["buff_state"])
        for v in node.values():
            buff_states(v, out)
    elif isinstance(node, list):
        for v in node:
            buff_states(v, out)
    return out


def is_add(node, name):
    return isinstance(node, dict) and node.get("type") == "AddCasterBuff" and node["buff_state"]["name"] == name


def switch(node, name):
    if not (isinstance(node, dict) and node.get("type") == "SwitchByBuff" and node["buff_name"] == name):
        sys.exit(f"a level probe is not shaped as it was (wanted SwitchByBuff {name}): update this script")
    return node


def only(node, tick):
    if not (node.get("type") == "Delayed" and node["tick"] == tick and len(node["effects"]) == 1):
        sys.exit("a level probe is not shaped as it was (its Delayed): update this script")
    return node["effects"][0]


def flag_reads(node, count):
    """`node` with every level probe in it replaced by a SwitchByBuff on the level flag (see the docstring, 2)."""
    if isinstance(node, list):
        return [flag_reads(v, count) for v in node]
    if not isinstance(node, dict):
        return node
    effects = node.get("effects")
    if node.get("type") == "Combine" and len(effects or []) == 2 and is_add(effects[0], "league_kayle_probe_shielded"):
        # flag, 2 ticks: no shield of an ally -> [shield S + soak + probeN flag] [10% hit] 2 ticks: shield broken ->
        # [shield 100 + soak + amp flag] [99 hit] 2 ticks: SwitchByBuff amp = the stage / nothing
        probe = switch(only(effects[1], 2), "league_kayle_probe_shielded")["effect_none"]["effects"]
        shield = [x["amount"] for x in probe[0]["effects"] if x.get("type") == "Shield" and x["amount"] in PROBE_SHIELDS]
        amp = switch(only(probe[2], 2), f"league_kayle_probe{PROBE_SHIELDS[shield[0]][len('league_kayle_lv'):]}")
        amp = switch(only(amp["effect_none"]["effects"][2], 2), "league_kayle_probe_amp")
        count[PROBE_SHIELDS[shield[0]]] += 1
        return {"type": "SwitchByBuff", "buff_name": PROBE_SHIELDS[shield[0]],
                "effect_buff": flag_reads(amp["effect_buff"], count), "effect_none": flag_reads(amp["effect_none"], count)}
    return {k: flag_reads(v, count) for k, v in node.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="CI: rebuild the copy and fail if the committed files differ")
    a = ap.parse_args()
    with open(lp(os.path.join(ROOT, "league", "champion", "league_kayle.data_champion")), encoding="utf-8") as f:
        champion = json.load(f)
    if "passive" in champion:
        sys.exit("the main pack's Kayle has a passive now: update this script")
    states = buff_states([champion[s] for s in ("attack", "skill", "skill2", "ult")], [])
    for name, stats in RANKS.items():
        found = {json.dumps({k: v for k, v in b.items() if k not in ("name", "duration")}, sort_keys=True)
                 for b in states if b["name"] == name}
        if found != {json.dumps(stats, sort_keys=True)} or any(
                b["duration"] != "Permanent" for b in states if b["name"] == name):
            sys.exit(f"{name} in the main pack is {sorted(found)}, the add-on puts back {stats}: update src/lib.rs")
    for slot in ("attack", "skill", "skill2", "ult"):
        if '"buff_name": "league_kayle_life"' not in json.dumps(champion[slot]):
            sys.exit(f"{slot} no longer reads league_kayle_life: update src/lib.rs")
    count = collections.Counter()
    for slot in ("attack", "skill", "skill2", "ult"):
        champion[slot] = flag_reads(champion[slot], count)
    left = sorted({w for w in json.dumps(champion).replace('"', " ").split() if w.startswith("league_kayle_probe")})
    if left != ["league_kayle_probe_cd"] or not all(count[f] for f in PROBE_SHIELDS.values()):
        sys.exit(f"probes left after the rewrite: {left}, flags read: {dict(count)}: update this script")
    champion["passive"] = {"passive_ref": f"{MOD_ID}:ascend", "params": {}}

    out = os.path.join(ADDON, "override", "league_kayle.data_champion")
    outs = [(out, json.dumps(champion, ensure_ascii=False, indent=2) + "\n"),
            (os.path.join(ADDON, "text", "champion.i18n"), "{}\n")]
    if a.check:
        generated.check(MOD_ID, outs)
        return
    for path, text in outs:
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("wrote", os.path.relpath(out, ROOT), "- passive =", champion["passive"]["passive_ref"], "- probes read as flags:",
          ", ".join(f"{f} {n}" for f, n in sorted(count.items())))


if __name__ == "__main__":
    main()
