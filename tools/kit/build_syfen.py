"""Build tft_syfen.data_champion (the tft pack's twenty-first hero: Sy'fen, jungle, Melee) from the parameters P.

    python tools/kit/build_syfen.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Sy'fen (赛芬) is the shadow wyvern of Teamfight Tactics set 7.5 (Uncharted Realms): the 4-cost unit TFT7_DragonPurple
(Whispers / Bruiser / Dragon, an AD fighter, range 1, 1050 health, 90 AD, 0.85 attack speed, 65 armour and magic
resistance, 30/75 mana), a hunched wyvern whose arms are his wings. TFT gives him one ability (Rampage / 暴走: charge
toward the farthest enemy within 2.5 hexes, every enemy hit takes 145-220% AD and is stunned, then a bite of 350-525% AD
ignoring 33% armour) and the Whispers trait (his damage shrinks enemies: 20% shred and sunder; hitting shrunk enemies
stacks AD and AP). The rest is our own design (the user's pick, 2026-10-30: jungle, plan A 「暴走猎杀」):
  passive Whispers (幽影低语): his damage shrinks the enemy hit for p_t ticks (p_shred% less armour and magic
          resistance); hitting an enemy already shrunk adds a fury stack (p_ad attack each, p_max at most, all gone p_stack_t
          ticks after the last). tft.dll (below). --plain: every attack puts the shrink on its target for atk_cd ticks and
          an average fury (p_ad x p_plain) on him while he fights.
  attack  Wing Claw Combo (翼爪连击) on `Enemy` (towers too): a wing-claw rake (`attack`) and a tail lash (`attack2`),
          alternating (a_t ticks to land the next), a_pct% AD each.
  skill   Bite (噬咬), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): he rears and lunges onto the
          target (`MoveToTarget` q_speed after q_st ticks) and bites: q_dmg + q_ad% AD ignoring q_pen% armour (a 1-tick
          `defence_penetration` on him), healing q_heal + q_heal_ad% AD.
  skill2  Wing Sweep (翼刃横扫), `Targeting` on `EnemyWithoutTower` (e_range): his wings sweep closed round him: every
          enemy within e_r takes e_dmg + e_ad% AD and is e_slow% slower for e_slow_t ticks.
  ult     Rampage (暴走, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): a roar; after r_go ticks he
          charges (crowd-control immune until the bite) at the FARTHEST enemy champion within r_range
          (`tft_syfen:rampage`, tft.dll: r_speed a tick for at most r_t ticks): every enemy within r_w of his path takes
          r_dmg + r_ad% AD and is stunned r_stun ticks; at r_bite_t he bites the one he charged at (`tft_syfen:bite`):
          r_bite_dmg + r_bite_ad% AD ignoring r_pen% armour. --plain: a penetrating `RushTime` through the target (the
          same hits), then `MoveToTarget` back onto it and the bite.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/syfen.rs; the passive is tft_syfen:whisper,
params NATIVE_KEYS): the data cannot ask whether the target carries a buff, nor find the farthest enemy. A build of P
checks syfen.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_syfen"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's fighters; radii count the unit's collision radius (~15000) on top.
# Timings are placeholders until the strips exist (tools/art/rig_syfen.py). Stats start from the tft junglers'
# (tft_vander hp 1080 atk 78, tft_krug 1200 / 80, tft_smeech 940 / 90): Sy'fen is the 4-cost wyvern, a bruiser.
# Numbers = the 10-min classic-SDK simulations (C:/t/sf_sim with C:/t/al_sim/kd.py: jungle lane 1 against the base
# ninja, demon, hunter, werewolf and vampire, three lineups, both sides; 2026-10-30), all --plain: the draft (fury 6 a
# stack, 3 on average; bite 260%) +1.79 / +1.90 on seeds 1-8 / 9-16 (tft_vander --plain +1.73 / +1.48 on the same
# games); a full fury of 5 stacks +2.29 (seeds 1-16); fury 5 a stack (4 on average), bite 240% +1.59 = P.
P = {
    # stats (Melee, a jungle fighter with attack damage)
    "hp": 1150, "hp_g": 112, "atk": 84, "atk_g": 14, "apw": 0, "apw_g": 0, "def": 36, "def_g": 8, "mr": 28, "mr_g": 5,
    "ms": 1040, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 60, "atk_st": 12, "a_pct": 100, "a_t": 240,
    # passive Whispers (TFT's trait: 20% shred and sunder, stacking AD)
    "p_t": 240, "p_shred": 20, "p_ad": 5, "p_max": 5, "p_stack_t": 300, "p_plain": 4,
    # Bite (TFT's bite: 33% armour ignored)
    "q_cd": 480, "q_range": 32000, "q_dur": 40, "q_st": 14, "q_speed": 3500, "q_dmg": 40, "q_ad": 160, "q_pen": 33,
    "q_heal": 30, "q_heal_ad": 30,
    # Wing Sweep
    "e_cd": 600, "e_range": 30000, "e_dur": 36, "e_st": 16, "e_r": 42000, "e_dmg": 40, "e_ad": 100, "e_slow": 30,
    "e_slow_t": 90,
    # Rampage (TFT: 145 / 220% AD and a stun on the charge, 350 / 525% AD bite ignoring 33% armour, 2.5 hexes)
    "r_cd": 2400, "r_range": 72000, "r_dur": 54, "r_go": 14, "r_speed": 4500, "r_t": 16, "r_w": 20000,
    "r_dmg": 30, "r_ad": 140, "r_stun": 75, "r_bite_t": 34, "r_bite_dmg": 60, "r_bite_ad": 240, "r_pen": 33,
    "r_reach": 40000,
}
# what tft.dll reads from passive.params (addons/tft/src/syfen.rs)
NATIVE_KEYS = ("p_t", "p_shred", "p_ad", "p_max", "p_stack_t", "r_range", "r_speed", "r_t", "r_w", "r_dmg", "r_ad",
               "r_stun", "r_bite_dmg", "r_bite_ad", "r_pen", "r_reach")
# names syfen.rs uses that need no view: sounds (the death cry, the bite's hit) and the bite's hidden armour piercing
NATIVE_ONLY = {"d", "r_bite_hit", "r_pen"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def true_attack(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def stun(tick):
    return {"type": "Stun", "duration": tick}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ passive (--plain stand-ins)
    if is_native:
        shrink, fury = None, None
    else:   # the shrink on every attack's target for one attack's time; an average fury while he fights
        shrink = buff("p_shrink", p["atk_cd"], defence_mult=-p["p_shred"], magic_resistance_mult=-p["p_shred"])
        fury = when("p_rage", combine(), flag("p_rage", p["p_stack_t"], attack=p["p_ad"] * p["p_plain"]))

    # ------------------------------------------------------------------ attack: wing claw / tail lash
    def swing(tag):
        return combine(anim(tag, p["atk_dur"]) if tag != "attack" else None, sfx("a"), attack(0, p["a_pct"]), shrink,
                       fury, view("a_hit"), tsfx("a_hit"))
    combo = when("a_1", combine(unflag("a_1"), swing("attack2")), combine(flag("a_1", p["a_t"]), swing("attack")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combo, atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Bite
    bite = [flag("q_pen", 1, defence_penetration=p["q_pen"]), attack(p["q_dmg"], p["q_ad"]),
            heal(p["q_heal"], p["q_heal_ad"]), view("q_bite"), tsfx("q_bite"), tsfx("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_st"] - 1, {"type": "MoveToTarget", "speed": p["q_speed"],
                                                             "range": p["q_range"] + 40000, "end_effects": bite})))

    # ------------------------------------------------------------------ skill2: Wing Sweep
    sweep = delayed(p["e_st"] - 1, sfx("e_hit"), cview("e_sweep"),
                    around(p["e_r"], "EnemyWithoutTower", [
                        attack(p["e_dmg"], p["e_ad"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                        view("e_hit")]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), sweep))

    # ------------------------------------------------------------------ ult: Rampage
    ram = [attack(p["r_dmg"], p["r_ad"]), stun(p["r_stun"]), view("r_hit"), tsfx("r_hit")]
    chomp = [flag("r_pen", 1, defence_penetration=p["r_pen"]), attack(p["r_bite_dmg"], p["r_bite_ad"]), view("r_bite"),
             tsfx("r_bite_hit")]
    if is_native:   # tft.dll: the farthest enemy champion, the passers rammed; the bite on the one he charged at
        charge, finish = native("rampage"), native("bite")
    else:
        charge = {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_t"], "range": 1000,
                  "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": [T(e) for e in ram]}
        finish = {"type": "MoveToTarget", "speed": 6000, "range": p["r_range"] + 40000, "end_effects": chomp}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_roar"), cview("r"), flag("r_go", p["r_bite_t"] + 2, cc_immune=True),
                         delayed(p["r_go"] - 1, sfx("r_dash"), cview("r_dash"), charge),
                         delayed(p["r_bite_t"] - 1, sfx("r_bite"), finish)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the claws, the bites, the sweep's cuts and the rams burst on what they hit; the sweep's arcs and the roar's rings
    # play on him (symmetric); the kick-off dust stays on the ground where the charge starts; the slow, the shrink and
    # the fury are auras (all pictures symmetric: the client never mirrors them)
    views_e = [E("a_hit"), E("q_bite", FX, 3), E("e_sweep", BIG, 4), E("e_hit"), E("r", BIG, 4),
               E("r_dash", FX, 1, False), E("r_hit", FX, 3), E("r_bite", BIG, 4), E("p", FX, 3)]
    views_b = [B_("e_slow", FX, 3), B_("p_shrink", FX, 3), B_("p_rage", BIG, 3)]
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
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/syfen.rs): the shrink and the fury, Rampage's charge and bite
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:whisper", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/syfen.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every picture it puts on or plays has a view, and the passive it registers is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "syfen.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"syfen.rs Params::default() differs from P (syfen.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    views = {v["name"] for k in ("view_projectiles", "view_effects", "view_buffs") for v in kit[k]}
    used = set(re.findall(r'sf\("(\w+)"\)', src))
    unseen = sorted(x for x in used - NATIVE_ONLY if n(x) not in views)
    if not used or unseen:
        raise SystemExit(f"pictures syfen.rs plays or puts on have no view: {unseen}")
    for reg in ("whisper", "rampage", "bite"):
        if f'format!("{{ID}}:{reg}")' not in src:
            raise SystemExit(f"syfen.rs does not register tft_syfen:{reg}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no tft.dll passive (for the balance sims)")
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
