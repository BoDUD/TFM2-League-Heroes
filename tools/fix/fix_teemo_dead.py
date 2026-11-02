"""Teemo R (Noxious Trap): nothing of a shroom goes off again after Teemo dies.

Each shroom's picture links (every 15 ticks, Delayed effects of the cast) play the burst - the cloud's picture and its
sound - behind the 30-tick caster flag `league_teemo_r_boom_<slot>`, and light `league_teemo_r_fire_<slot>` (3 ticks),
which the cloud zone reads to poison and slow everyone in it once. In the game a dead caster's Delayed effects run on
and his flags freeze (champion-data.md, "A dead caster"; league_riven R): killed within 30 ticks of a shroom popping,
`boom` stayed up and every later link played the burst and its sound again, every 15 ticks to the shroom's end; within
the 3 ticks of `fire`, the cloud poisoned every 2 ticks. Found 2026-11-02 with the user's 「挂在蔚奥莱身上的一个技能触发了
一直无限音效」 (league_maokai's sapling, the same frozen flags). Both now ask first whether he lives: a 1-tick flag from a
search that finds no dead caster, read and taken off at once (tools/kit/build_maokai.py `alive()`), inside the flag, so
the search runs only while it is up. The lying shroom's picture (behind `league_teemo_r_alive_<slot>`) is left as it is.

The add-on league_teemo_shrooms replaces the data shrooms with its own (addons/league_teemo_shrooms/make_override.py cuts
these branches), so this is for the main pack's Teemo and for league_sylas's copy of his R.

    python tools/fix/fix_teemo_dead.py [league/champion/league_teemo.data_champion] [--check]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
PATH = os.path.join(REPO, "league", "champion", "league_teemo.data_champion")
FLAG = "league_teemo_lives"
READS = re.compile(r"^league_teemo_r_(boom|fire)_[abc]$")
WANT = {"boom": 147, "fire": 3}


def guard(effect):
    """`effect` only while he lives."""
    return {"type": "Combine", "effects": [
        {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
         "effects": [{"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": 1}}},
                      "only_to_enemy": False}]},
        {"type": "SwitchByBuff", "buff_name": FLAG,
         "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": FLAG}, effect]},
         "effect_none": {"type": "Combine", "effects": []}},
        {"type": "RemoveCasterBuff", "name": FLAG}]}


def guarded(effect):
    first = effect.get("effects", [{}])[0] if effect.get("type") == "Combine" and effect.get("effects") else {}
    return first.get("type") == "RandomTarget" and json.dumps(first).count(FLAG) == 1


def fix(node, seen):
    if isinstance(node, dict):
        m = READS.match(node.get("buff_name", "")) if node.get("type") == "SwitchByBuff" else None
        if m:
            seen[m.group(1)] = seen.get(m.group(1), 0) + 1
            if not guarded(node["effect_buff"]):
                node["effect_buff"] = guard(node["effect_buff"])
                seen["changed"] = seen.get("changed", 0) + 1
        for v in node.values():
            fix(v, seen)
    elif isinstance(node, list):
        for v in node:
            fix(v, seen)


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    args = [a for a in sys.argv[1:] if a != "--check"]
    path = args[0] if args else PATH
    with open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    champion = json.loads(raw)
    if dumps(champion) != raw:
        sys.exit(f"{path}: not in this script's layout (indent 2, CRLF): look before writing")
    seen = {}
    fix(champion["ult"], seen)
    if {k: seen.get(k, 0) for k in WANT} != WANT:
        sys.exit(f"Teemo's R changed ({seen}, want {WANT}): update this script")
    if "--check" in sys.argv:
        print(f"{path}: {'up to date' if not seen.get('changed') else str(seen['changed']) + ' reads unguarded'}")
        sys.exit(1 if seen.get("changed") else 0)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(dumps(champion))
    print(f"{path}: {seen.get('changed', 0)} of {WANT['boom'] + WANT['fire']} reads guarded")


if __name__ == "__main__":
    main()
