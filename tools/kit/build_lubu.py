"""Build ragnarok_lubu.data_champion (the ragnarok pack's first hero: Lu Bu, top lane, Melee) from the parameters P.

    python tools/kit/build_lubu.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

吕布奉先 (Lu Bu Fengxian) of Record of Ragnarok (终末的女武神), humanity's first fighter, the strongest man of his age,
with the Sky Piercer halberd (方天画戟). The ragnarok pack (mod_id ragnarok, data in ragnarok/, code in
addons/ragnarok -> ragnarok.dll) is its own mod (the user, 2026-11-20: 「开始做新的mod了」). Art, icons and audio are
Codex's (assets/source/lubu/, the user's split: 「技能代码逻辑之类的都需要你来做」); the kit is ours, after the four
skills Codex's icons and the handoff name:
  passive Shield Breaker (盾牌破坏者): his blows ignore p_pen% of the target's armour (a Permanent buff each life,
          ragnarok.dll; --plain puts it on with his first skill), and they count p_shield% more against shields:
          ragnarok.dll adds to a hit on a shielded unit just what that takes off its shield (never past it into
          health), and when one of his hits leaves a shield broken - read back from the target a tick later, the
          shield really gone - the shield shatters (the shield_break picture and sound) and the target takes
          p_break% of his attack as physical damage. --plain has no shield part (the classic engine runs no DLL code).
  attack  a heavy halberd blow on `Enemy` (towers too): 100% AD on atk_st, the swing and the spark on the target.
  skill   Sweep (横扫), `Targeting` on `EnemyWithoutTower` (q_range): on q_hit the halberd sweeps a cone in front of him
          (radius q_r, half-angle acos(q_cone / 1000)): q_dmg + q_ad% AD and a q_slow% slow for q_slow_t ticks.
  skill2  Formation Breaker (破阵), `Targeting` on `EnemyWithoutTower` (e_range): on e_go he lunges e_speed x e_t toward
          the target and through it (`RushTime`, penetrate; the engine's own dash, so walls stop it as they stop every
          dash), every enemy he passes within e_r takes e_dmg + e_ad% AD and is thrown up e_air ticks.
  ult     Sky Eater (天喰), `Targeting` on `EnemyChampion` (r_range): he raises the halberd and gathers himself for
          r_go ticks - unstoppable (cc_immune) and taking r_dr% less damage meanwhile - then cuts once along a line
          r_len long toward the target (`LineRangeProjectile`, half-width r_w): r_dmg + r_ad% AD and a r_stun-tick
          stun to every enemy on it. One cut, no beam (the handoff: 「不要做持续激光」). A Lu Bu killed during the
          charge cuts nothing (the slash runs inside the alive search, champion-data "A dead caster").

Timings are the frames' (Codex's asset_manifest_v02.json presentation_events, 60 ticks a second): the attack's blow on
frame 4 (0.32 s), the sweep's release on frame 4 (0.42 s), the lunge on frame 4 (0.34 s, frames 4-5 = the lunge
pose), the cut on frame 5 (1.18 s).

ragnarok.dll (addons/ragnarok/src/lubu.rs): the passive ragnarok_lubu:breaker (armour each life, the shield rules,
his voice lines). A build of P checks lubu.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_lubu"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# Units: melee range 25000 for the base fighters, his halberd a little longer (league_syfen's 30000, league_jax's
# polearm); radii count the unit's collision radius (~15000) on top. Ticks: 60 a second.
# Numbers = the 10-min classic-SDK simulations (C:/t/lb_sim, the kept balance sim: top lane against the base fighter,
# executioner, knight, berserker, lancer and pole warrior, three lineups, both sides, 288 games a batch; 2026-11-20),
# all --plain (no shield part; the armour from his first skill). Controls on the same games: base fighter +1.33 / +1.78
# (seeds 1-8 / 9-16), executioner -1.84 / -1.38, league_darius +1.50 / +0.18, league_garen -0.09 / -0.42, league_jax
# +1.51 / +0.77, league_aatrox +2.10 / +1.39, league_renekton +2.15, league_sett +2.07. The draft (atk 94, Sweep 50 +
# 110% / 25% slow, Formation Breaker every 9 s / 0.4 s up, Sky Eater 160 + 240%) -0.15 / -0.40: the most damage of the
# lane and the least crowd control (the base fighter stuns 1 s from 80000 every 5 s). Tankier (hp 1150, def 36) did not
# help (-0.28 with the next change); Formation Breaker every 7 s for 0.6 s and a 40% slow +0.02 / +0.02; + atk 100,
# Sweep 130% +0.70; + Sky Eater 200 + 280% = P: +1.48 / +1.38, the pack's middle (a 1 s stun +1.88, too much).
P = {
    # stats (Melee, top): the base fighters' middle (atk 95 +19, hp 1000 +100, def 30, mr 25, move 1000)
    "hp": 1060, "hp_g": 105, "atk": 100, "atk_g": 19, "apw": 0, "apw_g": 0, "def": 32, "def_g": 8, "mr": 25,
    "mr_g": 4, "ms": 1020, "ms_g": 11,
    "atk_range": 28000, "atk_dur": 30, "atk_cd": 72, "atk_st": 18,
    # passive Shield Breaker
    "p_pen": 15, "p_shield": 100, "p_break": 30,
    # Sweep
    "q_cd": 360, "q_range": 32000, "q_dur": 46, "q_hit": 26, "q_r": 38000, "q_cone": 400, "q_dmg": 50, "q_ad": 130,
    "q_slow": 40, "q_slow_t": 90,
    # Formation Breaker
    "e_cd": 420, "e_range": 45000, "e_dur": 40, "e_go": 21, "e_speed": 3200, "e_t": 11, "e_r": 15000, "e_dmg": 40,
    "e_ad": 100, "e_air": 36,
    # Sky Eater
    "r_cd": 3000, "r_range": 45000, "r_dur": 96, "r_go": 72, "r_len": 75000, "r_w": 10000, "r_dmg": 200, "r_ad": 280,
    "r_stun": 48, "r_dr": 30,
}
# what ragnarok.dll reads from passive.params (addons/ragnarok/src/lubu.rs)
NATIVE_KEYS = ("p_pen", "p_shield", "p_break")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def on_self(*effects):
    """Effects on him alone (a WithSelf would hit the action's target too, champion-data section 4)."""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
            "apply_type": "AroundCaster", "effects": list(effects)}


def search_self(*effects):
    """Runs only while he lives: the search finds no dead caster (champion-data "A dead caster")."""
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """A Delayed's effects that use the action's target, kept to a living Lu Bu: a 1-tick flag from the search, the
    effects behind it, and the same effects inside a search for the AI to read while the flag is down (the second
    shape of champion-data "Which chains need the guard")."""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain: the armour part of the passive from his first skill (ragnarok.dll puts it on each life at once)
    first = None if is_native else when(
        "p_on", combine(), combine(flag("p_on", None), flag("p_pen", None, defence_penetration=p["p_pen"])))

    # ------------------------------------------------------------------ attack: the halberd blow
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Sweep
    cone = {"DirDot": {"radius": p["q_r"], "range": p["q_cone"]}}
    swept = [attack(p["q_dmg"], p["q_ad"]),
             {"type": "AddBuff", "buff_state": {"name": n("q_slow"), "duration": {"Time": {"tick": p["q_slow_t"]}},
                                                "move_speed_mult": -p["q_slow"]}},
             view("q_hit")]
    sweep = {"type": "RangeEffect", "shape": cone, "target": "EnemyWithoutTower",
             "apply_type": {"Forward": {"offset": 1000}}, "effects": swept}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, delayed(p["q_hit"] - 1, sfx("q_swing"), sweep, tsfx("q_hit"))))

    # ------------------------------------------------------------------ skill2: Formation Breaker
    passed = [{"casting_type": "Targeting", "effect": e} for e in
              (attack(p["e_dmg"], p["e_ad"]), {"type": "Airborne", "duration": p["e_air"]}, view("e_hit"),
               tsfx("e_hit"))]
    rush = {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_t"], "range": p["e_r"],
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": passed}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(first, delayed(p["e_go"] - 1, sfx("e"), rush)))

    # ------------------------------------------------------------------ ult: Sky Eater
    cut = {"type": "LineRangeProjectile", "name": n("r_cut"), "width": p["r_w"], "length": p["r_len"], "delay": 2,
           "apply": 1, "applied_target": "EnemyWithoutTower",
           "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in
                               (attack(p["r_dmg"], p["r_ad"]), {"type": "Stun", "duration": p["r_stun"]},
                                view("r_hit"), tsfx("r_hit"))]}
    guard = flag("r_guard", p["r_go"] + 2, cc_immune=True, damaged_reduce=p["r_dr"])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, guard, sfx("r"), sfx("r_vo"),
                         delayed(p["r_go"] - 1, alive_only(sfx("r_slash"), cut))))

    # ------------------------------------------------------------------ views
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    # the swing pictures (swipe, sweep, thrust, the charge and the cut) are drawn into his own frames
    # (tools/art/import_lubu.py): the client never mirrors an effect picture, his frames are mirrored
    views_e = [E("a_hit", "hit_spark"), E("q_hit", "hit_spark"), E("e_hit", "hit_spark"), E("r_hit", "ult_impact"),
               E("p_break", "shield_break", 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll (addons/ragnarok/src/lubu.rs): the armour each life, the shields, the voice
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:breaker", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def names(o):
    """Every `name` in a tree: the buffs, flags, pictures and sounds the kit sets or plays."""
    if isinstance(o, dict):
        return ({o["name"]} if isinstance(o.get("name"), str) else set()).union(*(names(v) for v in o.values()))
    if isinstance(o, list):
        return set().union(*(names(v) for v in o))
    return set()


def check_dll(p, kit):
    """addons/ragnarok/src/lubu.rs's Params::default() holds P's numbers (ragnarok.dll reads passive.params; the
    defaults are its fallback), every picture it plays (`vo("...")` in a play_view_effect) is a view of the kit, and
    the passive the kit names is the one it registers."""
    import re
    path = os.path.join(REPO, "addons", "ragnarok", "src", "lubu.rs")
    if not os.path.exists(lp(path)):
        return
    src = open(lp(path), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"lubu.rs Params::default() differs from P (lubu.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    shown = set(re.findall(r'play_view_effect\(&vo\("(\w+)"\)', src))
    views = {v["name"] for v in kit["view_effects"]}
    if not shown or any(n(x) not in views for x in shown):
        raise SystemExit(f"lubu.rs plays pictures the kit has no view for: {sorted(x for x in shown if n(x) not in views)}")
    if f'"{{ID}}:breaker"' not in src.replace("format!(", "") and 'format!("{ID}:breaker")' not in src:
        raise SystemExit("lubu.rs does not register ragnarok_lubu:breaker")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no ragnarok.dll calls (for the balance sims)")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, not a.plain)
    if not a.set and not a.params:
        check_dll(p, build(p, True))
    if a.nodes:
        for s in ("attack", "skill", "skill2", "ult"):
            print(f"{s:7s} {nodes(kit[s]['effect']):4d} nodes")
    text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    with open(lp(a.out), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(a.out, len(text))


if __name__ == "__main__":
    main()
