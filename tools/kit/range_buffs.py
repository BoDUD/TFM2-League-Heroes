"""Attack range the pack's buffs give, through league.dll's native effect `league:range` (2026-11-07).

    python tools/kit/range_buffs.py --write   # addons/league_main/src/range_table.rs from RANGE_BUFFS
    python tools/kit/range_buffs.py --check   # (CI) that file is up to date; no buff of league/ or of an add-on's
                                              # override/ carries `range`; every attack that can read one has the node

Why: the game's AI stands a champion at its attack range + its `range` buffs, but starts the attack only within the
attack's own range, so a `range` buff parked the champion out of reach (league_ult_press.log, two launches: league_kogmaw
with W held at 78000 = 55000 + 18000 + both bodies in 60 of 82 holds, league_twitch with R at about 90000, league_senna
past her range in 81 of 130; marksmen without a range buff never). The official way to a longer reach is the action's
`growth_range` (per level) and `range_adjust` on its effect (stable API 0.6.4+: "every range check reads it, the AI's
included"): the base game's poison dart hunter and crossbowman lengthen their reach that way, never with a `range`
buff, and a `Combine` answers with the largest `range_adjust` of its effects (game_core's CombineEffect::range_adjust).

So league.dll registers `league:range`: its range_adjust is the sum of RANGE_BUFFS over the caster's buffs (every
instance counts: league_senna_mist and league_kindred_p_mark stack), its apply does nothing. The buffs carry no `range`
(they are the markers), and `apply()` puts the node last in the attack's top `Combine` (wrapping the attack's effect in
one when it is not a Combine), so the first effect - what the game's balance patches read - stays the attack's own.
`wrap()` does it to a kit script's `build()`; tools/kit/range_native_data.py did it once to the kits made by hand.

The node's second job (2026-11-13, `reach()`): an attack that runs an area effect on allies or on the caster himself at
cast time - `RangeEffect` with target AllyOnlySelf / AllyChampion / AllyNotSelf, the circle of radius 1000 round him
that the kits use for "on me": an automatic W, the essence count, the whole kit's polling aura - is hardly ever ordered
at a champion by the game's AI (0.7.2). league_ai_watch, 5 launches, the AI's own attacks at champions per alive
minute: of the 37 heroes measured with such an aura and no node 30 were under 1.75 (Aurelion Sol 0.06 in 168 games,
Azir 0.07, Ahri 0.13, Draven 0.16, Swain 0.21 in 357, Anivia 0.26, Kai'Sa 0.60, Sejuani 0.83 in 321), while all 7 with
the aura AND the node attacked like everybody else (Bel'Veth 5.26 with the very skeleton of Aurelion Sol's attack,
Senna 5.59, Seraphine 4.79, Wukong 4.65, Poppy 2.32, Rell 2.24; marksmen without either: 4.5-7). The in-game test of
2026-11-13: Draven's aura moved under his projectile's hit, nothing else changed: 0.16 -> 6.5. So the packers
(tools/package_mod.py, addons/league_addons/assemble.py) pass every league_ champion through `reach()`: an attack with
such an aura gets the node, last in its top `Combine`, where a marker's attack has it. The repository's files and their
generators stay as they are (129 make_override.py would each have to add it); `--check` lists what the packers add.
league_sylas is left out as above. What the engine reads from the aura was not found in its code (a range check that
takes the area's size for the attack's reach fits: ranged heroes were hit harder than melee ones).
"""
import argparse
import copy
import functools
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TABLE_RS = os.path.join(ROOT, "addons", "league_main", "src", "range_table.rs")

# buff name -> attack range it gives (each instance), as the kits gave it with a `range` field
RANGE_BUFFS = {
    "league_akali_p_ready": 24000,       # Assassin's Mark: the empowered attack's reach
    "league_aphelios_mw_cal": 10000,     # Calibrum in the main hand (league_aphelios c_range)
    "league_belveth_r_on": 6000,         # True Form
    "league_elise_hu": 27000,            # human form (the spider is the 23000 melee)
    "league_evelynn_e_range": 20000,     # Demon Shade's empowered Whiplash
    "league_gnar_mi": 17000,             # Mini Gnar (Mega is the 25000 melee)
    "league_gwen_e_on": 7500,            # Skip 'n Slash
    "league_jayce_cn": 25000,            # Mercury Cannon (the hammer is the 25000 melee)
    "league_kayle_rank5": 27500,         # Aflame (level 6 in League): ranged
    "league_kayle_rank12": 10000,        # Starfire Spellblade
    "league_khazix_s1": 6000,            # Evolved Reaper Claws
    "league_kindred_p_mark": 1500,       # each Mark of the Kindred
    "league_kogmaw_w_on": 18000,         # Bio-Arcane Barrage (65000 attack and no W range from #702 until this)
    "league_milio_w_range": 7000,        # Cozy Campfire on an ally (only attacks with the node read it)
    "league_nasus_r_on": 4000,           # Fury of the Sands
    "league_nidalee_hu": 27000,          # human form (the cougar is the 23000 melee)
    "league_nilah_q_on": 12500,          # Formless Blade
    "league_poppy_p_rdy": 30000,         # Iron Ambassador: the thrown buckler
    "league_qiyana_el_on": 1500,         # an element on her ring (league_qiyana w_range)
    "league_rell_foot": 6000,            # dismounted
    "league_rengar_ready": 25000,        # the leap (league_rengar_bush leap_range)
    "league_riven_r": 8000,              # Blade of the Exile
    "league_senna_mist": 100,            # each Mist
    "league_seraphine_n1": 3000,         # the notes
    "league_seraphine_n2": 3000,
    "league_seraphine_n3": 3000,
    "league_seraphine_n4": 3000,
    "league_shyvana_dg": 10000,          # dragon form
    "league_twitch_r_on": 30000,         # Spray and Pray
    "league_viego_soul_mage": 25000,     # league_viego_soul: a ranged soul (s_range)
    "league_viego_soul_range": 25000,
    "league_viego_soul_util": 25000,
    "league_volibear_r_form": 5000,      # Stormbringer
    "league_wukong_q_rng": 12000,        # Crushing Blow
}

NODE_REF = "league:range"
NODE = {"type": "Native", "effect_ref": NODE_REF}


def _buff_states(o):
    if isinstance(o, dict):
        bs = o.get("buff_state")
        if isinstance(bs, dict):
            yield bs
        for v in o.values():
            yield from _buff_states(v)
    elif isinstance(o, list):
        for v in o:
            yield from _buff_states(v)


def _has_node(eff):
    """The node is the effect itself or reached through Combines only: a Combine answers range_adjust with its
    effects' largest, every other effect (SwitchByBuff, Delayed, ...) with 0."""
    if not isinstance(eff, dict):
        return False
    if eff.get("type") == "Native" and eff.get("effect_ref") == NODE_REF:
        return True
    return eff.get("type") == "Combine" and any(_has_node(e) for e in eff.get("effects", []))


def reads_range(champ):
    """The champion lays one of RANGE_BUFFS (and so its attack needs the node)."""
    return any(bs.get("name") in RANGE_BUFFS for bs in _buff_states(champ))


def apply(champ, force=False):
    """The kit with its RANGE_BUFFS as markers (no `range`) and the node in its attack. A marked buff whose `range`
    is not the table's fails (the kit and the table drifted); a `range` on a buff not in the table fails too."""
    for bs in _buff_states(champ):
        name = bs.get("name")
        if "range" not in bs:
            continue
        if name not in RANGE_BUFFS:
            raise ValueError(f"{champ.get('id')}: buff {name} has range {bs['range']}, not in tools/kit/range_buffs.py")
        if bs["range"] != RANGE_BUFFS[name]:
            raise ValueError(f"{champ.get('id')}: buff {name} has range {bs['range']}, the table {RANGE_BUFFS[name]}")
        del bs["range"]
    if force or reads_range(champ):
        attack = champ["attack"]
        eff = attack.get("effect")
        if not _has_node(eff):
            if isinstance(eff, dict) and eff.get("type") == "Combine":
                eff["effects"] = list(eff.get("effects", [])) + [copy.deepcopy(NODE)]
            else:
                attack["effect"] = {"type": "Combine", "effects": ([eff] if eff else []) + [copy.deepcopy(NODE)]}
    return champ


# no node by `reach()`: league_sylas (see problems(): a stolen reach would be his to keep)
NO_REACH = ("league_sylas",)


def aura_at_cast(eff):
    """The effect tree runs, outside every projectile's hit, a `RangeEffect` on allies or on the caster (target
    Ally* / *Self): at cast time, also behind a Delayed, a SwitchByBuff, a RandomTarget or inside another area."""
    if isinstance(eff, list):
        return any(aura_at_cast(e) for e in eff)
    if not isinstance(eff, dict):
        return False
    kind = str(eff.get("type", ""))
    if kind.endswith("Projectile"):
        return False                      # what a projectile does when it lands is not the cast
    if kind == "RangeEffect":
        target = str(eff.get("target", ""))
        if "Ally" in target or "Self" in target:
            return True
    return any(aura_at_cast(v) for v in eff.values() if isinstance(v, (dict, list)))


def needs_reach(champ):
    """A league_ champion whose attack has such an aura and no node (the packers add it: `reach()`)."""
    attack = champ.get("attack")
    if not isinstance(attack, dict) or not str(champ.get("id", "")).startswith("league_") or champ.get("id") in NO_REACH:
        return False
    eff = attack.get("effect")
    return aura_at_cast(eff) and not _has_node(eff)


def _with_node(attack):
    eff = attack.get("effect")
    if isinstance(eff, dict) and eff.get("type") == "Combine":
        return dict(attack, effect=dict(eff, effects=list(eff.get("effects", [])) + [copy.deepcopy(NODE)]))
    return dict(attack, effect={"type": "Combine", "effects": ([eff] if eff else []) + [copy.deepcopy(NODE)]})


def reach(champ):
    """What the packers ship: the champion itself, or a copy with the node in its attack when `needs_reach` (see the
    module's text). Nothing else changes; a second pass changes nothing."""
    if not needs_reach(champ):
        return champ
    return dict(champ, attack=_with_node(champ["attack"]))


def wrap(build):
    """`build = range_buffs.wrap(build)` under a kit script's build(): every caller gets the kit with the markers."""
    @functools.wraps(build)
    def built(*a, **k):
        return apply(build(*a, **k))
    return built


def table_rs():
    lines = ["//! The attack range each marker buff gives through `league:range` (src/range.rs): generated by",
             "//! tools/kit/range_buffs.py from its RANGE_BUFFS - do not edit by hand.", "",
             f"pub const RANGE_BUFFS: [(&str, u64); {len(RANGE_BUFFS)}] = ["]
    lines += [f'    ("{k}", {v}),' for k, v in sorted(RANGE_BUFFS.items())]
    lines += ["];", ""]
    return "\n".join(lines)


def load(path):
    return json.loads(open(path, "rb").read().decode("utf-8-sig"))


def problems():
    """What --check finds: stray `range` buffs and attacks without (or with a needless) node, in league/ and in the
    add-ons' copies."""
    out = []
    # league_sylas: his stolen ults lay other heroes' markers, his attack has no node on purpose (make_override.py
    # no_lasting_reach): a stolen reach would be his to keep
    files = sorted(glob.glob(os.path.join(ROOT, "league", "champion", "*.data_champion")) +
                   glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion")))
    for path in files:
        rel = os.path.relpath(path, ROOT)
        c = load(path)
        for bs in _buff_states(c):
            if "range" in bs and bs.get("range"):
                out.append(f"{rel}: buff {bs.get('name')} still has range {bs['range']}")
        if "attack" in c and reads_range(c) and not _has_node(c["attack"].get("effect")) and c.get("id") != "league_sylas":
            out.append(f"{rel}: lays a range marker but its attack has no {NODE_REF} node")
        shipped = reach(c)
        if needs_reach(shipped) or reach(shipped) != shipped:
            out.append(f"{rel}: reach() does not settle (an aura at cast time and still no node)")
        if shipped is not c and {k: v for k, v in shipped.items() if k != "attack"} != {k: v for k, v in c.items() if k != "attack"}:
            out.append(f"{rel}: reach() changed more than the attack")
    return out


def reached():
    """The champions the packers add the node to (ids, sorted): the installed copy of each - an add-on's override
    when there is one, else the main pack's file."""
    final = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "league", "champion", "*.data_champion"))):
        final[os.path.basename(path)] = path
    for path in sorted(glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion"))):
        final[os.path.basename(path)] = path
    return sorted(c["id"] for c in map(load, final.values()) if needs_reach(c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.write:
        with open(TABLE_RS, "w", encoding="utf-8", newline="\n") as f:
            f.write(table_rs())
        print("wrote", os.path.relpath(TABLE_RS, ROOT), len(RANGE_BUFFS), "buffs")
    if a.check:
        bad = problems()
        have = open(TABLE_RS, encoding="utf-8").read().replace("\r\n", "\n") if os.path.exists(TABLE_RS) else ""
        if have != table_rs():
            bad.append(f"{os.path.relpath(TABLE_RS, ROOT)} is out of date: python tools/kit/range_buffs.py --write")
        for b in bad:
            print(b)
        if bad:
            sys.exit(f"{len(bad)} problem(s)")
        print("range buffs: table up to date, no `range` buff left, every marked attack has the node")
        ids = reached()
        print(f"reach: the packers add the node to {len(ids)} attacks with an aura at cast time: "
              + ", ".join(i[len("league_"):] for i in ids))


if __name__ == "__main__":
    main()
