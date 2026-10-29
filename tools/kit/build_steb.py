"""Build tft_steb.data_champion (the tft pack's sixteenth hero: Steb, support, Util) from the parameters P.

    python tools/kit/build_steb.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Steb is Arcane's fish-man enforcer of Piltover, the squad's field medic: a 1-cost of Teamfight Tactics set 13
(TFT13_Fish, Enforcer / Bruiser, an AP tank, range 1, 650 health, 55 AD, 0.55 attack speed, 25/75 mana), two hextech
side-handle batons and a big medic's backpack. TFT gives him one ability (Field Medicine / 战地医疗: passive, when he
is healed the 2 nearest allies heal 25% of it; active, heal himself 260-430 (AP) and strike the target for 260-780
magic) and the Enforcer trait (the highest-health enemies are WANTED; a Wanted kill gives the Enforcers 30% attack
speed). The rest is our own design (the user's pick, 2026-10-29: support lane, plan A 「战地军医」):
  passive Field Medicine (战地医疗): whenever he is healed (any heal: his own, an ally's, life steal), the p_n allied
          champions nearest him within p_r heal p_share% of it (tft.dll reads his health every tick: the data reads
          none). --plain: Q's and R's heals on him also heal every ally within p_r for p_share% of the same base.
  attack  Twin Batons (双警棍连击) on `Enemy` (towers too): 100% AD on atk_st, the two batons in turn (`a2` flag:
          `attack` / `attack2` frames and sounds).
  skill   Field Medicine (战地医疗), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): a shot of
          medicine on q_heal_at heals him q_heal + q_heal_ap% AP (the passive passes it on), then on q_st a baton
          strike on the target, q_dmg + q_ap% AP magic, stunned q_stun ticks.
  skill2  Wanted (通缉令), `None` on `EnemyChampion` (e_range, only in fights): tft.dll (tft_steb:wanted) marks the
          enemy champion with the most health within e_r: it takes e_amp% more damage from everyone for e_t ticks; if
          it dies while Wanted, every allied champion within e_kr of Steb gets e_as% attack speed for e_as_t ticks.
          --plain: a random enemy champion within e_r, no kill reward.
  ult     Medic's Pack (医疗背包), `None` on `EnemyChampion` (r_range): he swings the pack down and opens it; on r_at
          he and every allied champion within r_r get a shield of r_sh + r_sh_ap% AP for r_sh_t ticks, he takes r_red%
          less damage for r_t ticks, and from r_at every r_every ticks, r_n times, he and every ally within r_r heal
          r_hot + r_hot_ap% AP (his own pulses pass on through the passive too).

tft.dll (addons/tft/src/steb.rs): the shared heals and the Wanted kill reward (passive tft_steb:medic), the Wanted pick
(tft_steb:wanted). A build of P checks steb.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_steb"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's tank supports (tft_loris, league_braum); radii count the unit's collision
# radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_steb.py). Stats start from
# tft_loris's (hp 1250 +115, atk 74, apw 30 +15, def 42, mr 30): Steb is the cheaper, softer medic of the two.
# Numbers = the 10-min classic-SDK simulations (C:/t/sb_sim with C:/t/al_sim/kd.py: support lane against the base
# priest, monk, bard, enchanter and taoist, three lineups, both sides; 2026-10-29), all --plain (the passive's share to
# every ally within p_r, Wanted on a random champion): the draft (Q 80 + 70% every 7 s, E +15%, R every 50 s) -2.46 on
# seeds 1-8 (tft_loris --plain +1.40); Q 170 + 120% every 5.5 s, E +25%, R every 40 s, apw 45, Q heal 120, R shield 120
# -0.55 (his damage now Loris's, but no crowd control); + a 0.75 s stun on Q's strike +1.82 = P (1 s and R every 35 s
# +2.12). P on seeds 9-16: +0.93.
P = {
    # stats (Util, the healing supports)
    "hp": 1150, "hp_g": 110, "atk": 68, "atk_g": 6, "apw": 45, "apw_g": 16, "def": 38, "def_g": 7, "mr": 30, "mr_g": 4,
    "ms": 980, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 90, "atk_st": 14,
    # passive Field Medicine (TFT: the 2 nearest allies, 25%)
    "p_n": 2, "p_share": 25, "p_r": 60000,
    # Field Medicine (TFT: heal 260-430, strike 260-780 magic)
    "q_cd": 330, "q_range": 30000, "q_dur": 36, "q_heal_at": 8, "q_st": 22, "q_heal": 120, "q_heal_ap": 60,
    "q_dmg": 170, "q_ap": 120, "q_stun": 45,
    # Wanted (TFT's Enforcer trait: the highest-health enemy; +30% attack speed on a Wanted kill)
    "e_cd": 600, "e_range": 60000, "e_dur": 24, "e_st": 10, "e_r": 80000, "e_amp": 25, "e_t": 300, "e_kr": 70000,
    "e_as": 30, "e_as_t": 300,
    # Medic's Pack
    "r_cd": 2400, "r_range": 50000, "r_dur": 42, "r_at": 24, "r_r": 40000, "r_sh": 120, "r_sh_ap": 50, "r_sh_t": 240,
    "r_red": 30, "r_t": 240, "r_every": 30, "r_n": 6, "r_hot": 25, "r_hot_ap": 12,
}
# what tft.dll reads from passive.params (addons/tft/src/steb.rs)
NATIVE_KEYS = ("p_n", "p_share", "p_r", "e_r", "e_amp", "e_t", "e_kr", "e_as", "e_as_t")


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


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def heal(amount, ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": kind}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    def mend(amount, ratio):
        """A heal on him; --plain also gives the allies within p_r the passive's share of it."""
        share = None if is_native else around(p["p_r"], "AllyNotSelf",
                                              [heal(amount * p["p_share"] // 100, ratio * p["p_share"] // 100, "Ally")])
        return combine(on_me(heal(amount, ratio)), share)

    # ------------------------------------------------------------------ attack: the two batons in turn
    hit = delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      when("a2", combine(unflag("a2"), anim("attack2", p["atk_dur"]), sfx("a2"), hit, tsfx("a2_hit")),
                           combine(flag("a2", None), sfx("a"), hit, tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Field Medicine
    stun = [{"type": "Stun", "duration": p["q_stun"]}, buff("q_stun", p["q_stun"])] if p["q_stun"] else []
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), sfx("q_vo"),
                           delayed(p["q_heal_at"] - 1, sfx("q_heal"), cview("q_heal"), mend(p["q_heal"], p["q_heal_ap"])),
                           delayed(p["q_st"] - 1, ap(p["q_dmg"], p["q_ap"]), view("q_hit"), tsfx("q_hit"), *stun)))

    # ------------------------------------------------------------------ skill2: Wanted
    if is_native:   # tft.dll: the enemy champion with the most health, the mark, the kill reward
        mark = native("wanted")
    else:
        mark = pick(p["e_r"], "EnemyChampion", buff("e_wanted", p["e_t"], damaged_amplify=p["e_amp"]), view("e_mark"),
                    tsfx("e_hit"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "None", "EnemyChampion",
                    combine(sfx("e"), delayed(p["e_st"] - 1, sfx("e_mark"), mark)))

    # ------------------------------------------------------------------ ult: Medic's Pack
    pulse = combine(mend(p["r_hot"], p["r_hot_ap"]),
                    around(p["r_r"], "AllyNotSelf", [heal(p["r_hot"], p["r_hot_ap"], "Ally"), view("r_heal")]),
                    cview("r_heal"))
    pulses = [delayed(p["r_at"] - 1 + k * p["r_every"], pulse, sfx("r_heal") if k == 0 else None)
              for k in range(p["r_n"])]
    opened = combine(sfx("r_shield"), cview("r_pack"),
                     on_me(shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"]), flag("r_guard", p["r_t"], damaged_reduce=p["r_red"])),
                     around(p["r_r"], "AllyNotSelf", [shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"]),
                                                      buff("r_shield", p["r_sh_t"])]))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
                 combine(sfx("r"), delayed(p["r_at"] - 1, opened), *pulses))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the pack's ring of light lies on the ground round him (z -1), drawn round so it reads the same on both sides.
    # tft.dll plays the shared heal (p_heal) on each ally it reaches and the Wanted kill's burst (e_kill)
    views_e = [E("a_hit"), E("q_heal", FX, 3), E("q_hit"), E("e_mark", FX, 4), E("r_pack", BIG, -1, False),
               E("r_heal", FX, 3)]
    if is_native:
        views_e += [E("p_heal", FX, 3), E("e_kill", FX, 3)]
    views_b = [B_("q_stun", FX, 3), B_("e_wanted", FX, 4), B_("r_guard", FX, 3), B_("r_shield", FX, 3)]
    if is_native:
        views_b += [B_("e_rush", FX, 3)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "Heal", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/steb.rs): the shared heals, the Wanted pick and its kill reward
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:medic", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Medic's Pack as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so nothing of it can be tft.dll's: the kit's --plain ult (its heals
    on him also give the allies near him their share, the passive's way without the passive). The views are the kit's
    own (tft_steb_*); make_override copies them and their sheets."""
    p = dict(P) if p is None else p
    return build(p, False)["ult"]["effect"]


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
    """addons/tft/src/steb.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every name it plays or puts on (`sb("...")`) is the kit's, and every Native the kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "steb.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"steb.rs Params::default() differs from P (steb.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sb\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"steb.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_steb:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects steb.rs does not register: {sorted(called - registered)}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no tft.dll calls (for the balance sims)")
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
