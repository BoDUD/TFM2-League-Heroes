"""Build the add-on's copy of Kayle from the main pack (her ascension and its wings kept through death).

    python addons/league_kayle/make_override.py

Copies league/champion/league_kayle.data_champion to addons/league_kayle/override/league_kayle.data_champion with one
change: passive = the add-on's league_kayle:ascend (no params), which puts back the ranks she has reached - and their
wings - when death clears them (src/lib.rs). Checks first that the main pack's rank buffs carry the numbers the add-on
puts back (rank5 range 27500; rank12 attack speed 30, move speed 10, range 10000; rank8 and form3 nothing) and that
every action still reads the once-a-life flag league_kayle_life the add-on sets. The tooltip stays the main pack's
(it is at the details panel's length limit), so text/champion.i18n is empty. Run it again whenever the main pack's
Kayle changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kayle")
MOD_ID = "league_kayle"
# the buffs src/lib.rs puts back, as the main pack adds them
RANKS = {
    "league_kayle_rank5": {"range": 27500},
    "league_kayle_rank8": {},
    "league_kayle_rank12": {"attack_speed_mult": 30, "move_speed_mult": 10, "range": 10000},
    "league_kayle_form3": {},
}


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


def main():
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
    champion["passive"] = {"passive_ref": f"{MOD_ID}:ascend", "params": {}}

    out = os.path.join(ADDON, "override", "league_kayle.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    with open(lp(os.path.join(ADDON, "text", "champion.i18n")), "w", encoding="utf-8", newline="\n") as f:
        f.write("{}\n")
    print("wrote", os.path.relpath(out, ROOT), "- passive =", champion["passive"]["passive_ref"])


if __name__ == "__main__":
    main()
