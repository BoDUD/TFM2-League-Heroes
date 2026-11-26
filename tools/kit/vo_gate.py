"""The spells' cast voice lines at most once every GAP ticks per hero and spell, at packing (2026-11-26).

    python tools/kit/vo_gate.py --check   # (CI) every gated spell sound is played somewhere, has its own voice sound
                                          # (both registered in league/mod.override_info) and the rewrite settles -
                                          # with slim.py and attack_self.py - on every champion file

Why. The 41 cast voice lines tools/lol/extract_missing_spell_vo.py found (league 0.469.0, PR 829) were wired as one more
clip in the spell's own .sound_info, so they played at every cast: Ezreal's Q (every 5 s) said its line all match long
(the user 2026-11-26: 「EZ的语音一直在重复」 - his Q's line - and 「放得勤的都一起改」). The kits' own voice lines are
played through a flag (`sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))` in 106 builders; league_ahri's
R: league_ahri_r_vo_cd, 600 ticks). Each of the 41 lines now has a .sound_info of its own, `league_<hero>_<slot>_vo` (the
line alone; the spell's .sound_info keeps its effect sounds; registered in league/mod.override_info as every sound - the
game finds a sound only through its `asset/base/sound/sfx/<name>` entry), and this rewrite plays it the kits' way wherever
the spell's sound plays:

    {"type": "Sfx", "name": S}   ->   {"type": "Sfx", "name": S},
                                      {"type": "SwitchByBuff", "buff_name": F, "effect_buff": {"type": "Combine", "effects": []},
                                       "effect_none": {"type": "Combine", "effects": [
                                           {"type": "AddCasterBuff", "buff_state": {"name": F, "duration": {"Time": {"tick": GAP}}},
                                            "only_to_enemy": false},
                                           {"type": "Sfx", "name": V}]}}

- In an effect list (slim.py's SEQ lists) the switch goes right after the sound; where the sound stands alone (an applied
  effect, a branch of a switch) the two go into a Combine of two - the shapes slim.py leaves as they are.
- TargetSfx the same: the line from where the sound was.
- F = league_<hero>_<slot>_vo_cd: SwitchByBuff reads the caster's buffs anywhere in a tree (docs: champion-data.md), so a
  sound under a hit's applied_effects is gated the same way, and attack_self.py already leaves `...vo_cd` out of its
  same-tick checks. GAP = 600 ticks (10 s), the kits' lines' gap. A sound played twice in one cast (Lee Sin's W shield
  for him and for the ally) says its line once.
- A spell whose cooldown is 10 s or more says its line at every cast as before; the frequent ones (Twisted Fate's Q 4 s,
  Ezreal / Vayne / Evelynn Q 5 s, the empowered attacks of Wukong, Kai'Sa, Sett ...) at most once in 10 s.

The sound -> line table is extract_missing_spell_vo.py's SPELLS (read with ast: that tool needs the League client's
readers). tools/package_mod.py and addons/league_addons/assemble.py run `gate()` after attack_self.py on every
.data_champion they pack (the add-ons' copies too), so the installed files carry it and the builders stay as they are.
"""
import argparse
import ast
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SPELLS_PY = os.path.join(REPO, "tools", "lol", "extract_missing_spell_vo.py")
GAP = 600
SOUNDS = ("Sfx", "TargetSfx")


def _spells():
    tree = ast.parse(open(SPELLS_PY, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SPELLS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(f"{SPELLS_PY}: no SPELLS")


def voice_name(slug, slot):
    """The line's own .sound_info."""
    return f"league_{slug}_{slot}_vo"


def flag_name(slug, slot):
    """The caster's flag while the line rests."""
    return f"league_{slug}_{slot}_vo_cd"


# spell sound -> (the line's .sound_info, the flag)
TABLE = {s[3]: (voice_name(s[0], s[2]), flag_name(s[0], s[2])) for s in _spells()}
SEQ = ("effects", "end_effects")


def _switch(name):
    voice, flag = TABLE[name]
    return {"type": "SwitchByBuff", "buff_name": flag, "effect_buff": {"type": "Combine", "effects": []},
            "effect_none": {"type": "Combine", "effects": [
                {"type": "AddCasterBuff", "buff_state": {"name": flag, "duration": {"Time": {"tick": GAP}}},
                 "only_to_enemy": False},
                {"type": "Sfx", "name": voice}]}}


def _voiced(sound, voice_type):
    """The switch for `sound` (an Sfx / TargetSfx of a gated spell sound), its line played the same way."""
    sw = _switch(sound["name"])
    sw["effect_none"]["effects"][1]["type"] = voice_type
    return sw


def _is_gated(sound, nxt):
    return (isinstance(nxt, dict) and nxt.get("type") == "SwitchByBuff"
            and nxt.get("buff_name") == TABLE[sound["name"]][1])


def _gated_sound(o):
    return isinstance(o, dict) and o.get("type") in SOUNDS and o.get("name") in TABLE


def _walk(o):
    if isinstance(o, list):
        return [_walk(x) for x in o]
    if not isinstance(o, dict):
        return o
    out = {}
    for k, v in o.items():
        if k in SEQ and isinstance(v, list):
            lst = []
            for i, x in enumerate(v):
                lst.append(_walk(x))
                if _gated_sound(x) and not _is_gated(x, v[i + 1] if i + 1 < len(v) else None):
                    lst.append(_voiced(x, x["type"]))
            out[k] = lst
        elif _gated_sound(v):
            # alone where one effect is expected (an applied effect, a switch's branch): the sound and its switch
            out[k] = {"type": "Combine", "effects": [dict(v), _voiced(v, v["type"])]}
        else:
            out[k] = _walk(v)
    return out


def gate(champ):
    """A parsed .data_champion with every play of a gated spell sound followed by its line's switch (a new object;
    gate(gate(x)) == gate(x))."""
    return _walk(champ)


def _files():
    return sorted(glob.glob(os.path.join(REPO, "league", "champion", "*.data_champion"))
                  + glob.glob(os.path.join(REPO, "addons", "*", "override", "*.data_champion")))


def check():
    sys.path.insert(0, HERE)
    import attack_self
    import slim
    sfx = os.path.join(REPO, "league", "sound", "sfx")
    # the game finds a sound only through the pack's override entry (a .sound_info without one never plays)
    ov = json.load(open(os.path.join(REPO, "league", "mod.override_info"), encoding="utf-8-sig"))
    bad = []
    voices = {}
    for spell, (voice, _flag) in TABLE.items():
        for name in (spell, voice):
            if not os.path.exists(os.path.join(sfx, name + ".sound_info")):
                bad.append(f"no league/sound/sfx/{name}.sound_info")
            if ov.get(f"asset/base/sound/sfx/{name}") != {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}:
                bad.append(f"no league/mod.override_info entry asset/base/sound/sfx/{name} -> asset/league/sound/sfx/{name}")
        if os.path.exists(os.path.join(sfx, voice + ".sound_info")):
            plays = json.load(open(os.path.join(sfx, voice + ".sound_info"), encoding="utf-8-sig"))["plays"]
            voices[voice] = [p["clip"] for p in plays]
        if os.path.exists(os.path.join(sfx, spell + ".sound_info")):
            own = [p["clip"] for p in json.load(open(os.path.join(sfx, spell + ".sound_info"), encoding="utf-8-sig"))["plays"]]
            if any(c in own for c in voices.get(voice, [])):
                bad.append(f"{spell}.sound_info still plays its line {voices[voice]}")
    seen, rewritten = set(), 0
    for path in _files():
        kit = json.load(open(path, encoding="utf-8-sig"))
        lean = gate(attack_self.settle(slim.slim_champion(kit)))
        if gate(attack_self.settle(slim.slim_champion(lean))) != lean or gate(lean) != lean:
            bad.append(f"{os.path.relpath(path, REPO)}: the gated kit does not settle")
        txt = json.dumps(lean)
        hit = [s for s in TABLE if f'"{s}"' in txt]
        seen.update(hit)
        rewritten += bool(hit)
    for s in sorted(set(TABLE) - seen):
        bad.append(f"{s}: played by no champion file")
    for b in bad:
        print("FAIL", b)
    print(f"{len(TABLE)} gated spell sounds, {len(seen)} played, {rewritten} of {len(_files())} champion files rewritten, "
          f"gap {GAP} ticks: {'ok' if not bad else str(len(bad)) + ' problem(s)'}")
    return not bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(0 if check() else 1)
    for s, (v, f) in sorted(TABLE.items()):
        print(f"{s:30s} -> {v:28s} {f}")


if __name__ == "__main__":
    main()
