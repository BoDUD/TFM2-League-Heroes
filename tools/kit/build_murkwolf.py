"""Build tft_murkwolf.data_champion (a tft pack hero: the Murk Wolf, jungle, Assassin) from the parameters P.

    python tools/kit/build_murkwolf.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Murk Wolf (暗影狼; en Murkwolf) is Teamfight Tactics set 18's 2-cost Rift Monster / Slayer (DA_Murkwolf18, range 1,
700 health, 50 AD, 0.75 attack speed, 40 armour and magic resistance, 0/40 mana, 25% crit): Rending Claws / 撕裂之爪 -
it leaps at the lowest-health enemy within a few hexes for physical damage, then its next attacks gain attack speed and
bonus physical damage; Gray Buff / 灰霸符: its abilities can crit, and its crit chance rises with its missing health.
Slayer / 狂战士: omnivamp, and bonus damage doubled against units under half health. A two-headed wolf; the Rift's camp
is one big wolf and two pups. The kit is our own design from that (the user's pick, 2026-11-01: jungle, plan A
「撕裂之爪」):
  passive Gray Buff (灰霸符): crit_chance p_crit in its stats (attacks crit the engine's way), and up to p_bonus more as
          its health falls (p_bonus x missing health %, the `p_gray` buff tft.dll keeps every CHECK ticks); its skill
          hits crit too - tft.dll rolls them against its crit chance, 200 + p_cdmg % on a crit (p_hit).
          --plain: half of p_bonus in its stats, skill hits at their expected crit size (plain_k).
  attack  Twin Bite (双头撕咬) on `Enemy` (towers too): both heads bite, 100% AD on atk_st; tft.dll (tft_murkwolf:bite,
          on every attack) adds the Rending Claws bonus and sends the pups.
  skill   Rending Claws (撕裂之爪, TFT's), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): it springs
          (`leap` frames, crowd-control immune in the air); on q_jump tft.dll (tft_murkwolf:rend) lands it beside the
          lowest-health enemy within q_range (champions first; else the AI's target) and rends it: q_dmg + q_ad% AD (it
          can crit); its next q_n attacks within q_t ticks have q_as% more attack speed (`q_emp`) and each deals
          q_emp_dmg + q_emp_ad% AD more (`q_n1`, `q_n2` count them). --plain: `Teleport` onto the AI's target, the
          rend, and `q_emp` for q_t ticks (every attack meanwhile gets the bonus).
  skill2  Slayer's Howl (狂战士之嚎), `Targeting` on `EnemyWithoutTower` (e_range, a fight close): both heads howl:
          for e_t ticks (`e_howl`) it has e_vamp% omnivamp and deals e_amp% more damage, 2 x e_amp% to units under
          e_line% health (tft.dll's on_attack, every hit of its own). --plain: attack_mult e_plain% instead.
  ult     Pack Attack (狼群攻击, the Rift camp's), `Targeting` on `EnemyChampion` (r_range, only in fights): its call
          brings two Murk Wolf pups (`r_pack`, drawn round it) for r_t ticks; on r_st they pounce at the target
          (tft_murkwolf:pounce: r_leap_dmg + r_leap_ad% AD), then each of its attacks meanwhile they bite the same
          enemy r_n times r_gap ticks apart (tft_murkwolf:pup), r_dmg + r_ad% AD each. --plain: the pounce and the
          bites as data, the bites by an attack switch on `r_pack`.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/murkwolf.rs; the passive is
tft_murkwolf:gray, params NATIVE_KEYS): no health-scaled crit, no target picked by health, no counted attacks, no
damage by the target's health. A build of P checks murkwolf.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_murkwolf"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 23000 like the pack's jungle assassins; radii count the unit's collision radius (~15000) on top.
# Timings are provisional until the strips are rigged (tools/art/rig_murkwolf.py): the bite lands at 167 ms (atk_st
# 10), the leap takes 233 ms (q_jump 14), the howl 333 ms (e_st 20), the call 200 ms (r_st 12). Stats start from the
# pack's jungle assassins (tft_smeech hp 940 +90, atk 90 +16, crit 25; league_warwick; league_khazix), a step under
# them for a 2-cost.
# Numbers = the 10-min classic-SDK simulations (C:/t/mw_sim with C:/t/al_sim/kd.py: jungle against the base ninja,
# demon, hunter, werewolf and vampire, three lineups, both sides; 2026-11-01), --plain (skill hits at their expected
# crit size, half of Gray Buff in its stats, Q on the AI's target, the howl a flat attack_mult): the draft = P +1.32 /
# +1.09 on seeds 1-8 / 9-16 against tft_smeech --plain +1.24 / +1.25: kept - in game tft.dll picks the weakest prey
# and doubles the howl on low-health units, which the plain sims cannot.
P = {
    # stats (Assassin, jungle)
    "hp": 920, "hp_g": 88, "atk": 86, "atk_g": 15, "apw": 0, "apw_g": 0, "def": 28, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1100, "ms_g": 12,
    "atk_range": 23000, "atk_dur": 22, "atk_cd": 56, "atk_st": 10,
    # passive Gray Buff (TFT: abilities crit; 25% crit chance, more with missing health)
    "p_crit": 25, "p_bonus": 30, "p_cdmg": 0,
    # Rending Claws (TFT: leap to the lowest-health enemy, then empowered attacks)
    "q_cd": 420, "q_range": 45000, "q_dur": 30, "q_jump": 14, "q_gap": 20000, "q_dmg": 40, "q_ad": 110,
    "q_n": 3, "q_t": 240, "q_as": 60, "q_emp_dmg": 10, "q_emp_ad": 30,
    # Slayer's Howl (TFT Slayer: omnivamp, bonus damage doubled under half health)
    "e_cd": 600, "e_range": 30000, "e_dur": 30, "e_st": 20, "e_t": 300, "e_vamp": 20, "e_amp": 15, "e_line": 50,
    "e_plain": 20,
    # Pack Attack (the Rift camp: one big wolf and two pups)
    "r_cd": 2700, "r_range": 50000, "r_dur": 30, "r_st": 12, "r_t": 360, "r_leap_dmg": 40, "r_leap_ad": 60,
    "r_n": 2, "r_gap": 4, "r_dmg": 12, "r_ad": 25,
}
# what tft.dll reads from passive.params (addons/tft/src/murkwolf.rs)
NATIVE_KEYS = ("p_bonus", "p_cdmg", "q_range", "q_gap", "q_dmg", "q_ad", "q_n", "q_emp_dmg", "q_emp_ad",
               "e_amp", "e_line", "r_leap_dmg", "r_leap_ad", "r_n", "r_gap", "r_dmg", "r_ad")
# names murkwolf.rs uses that the data need not have: the crit buff, the attack counters, the sounds it plays itself
NATIVE_ONLY = {"p_gray", "q_n1", "p", "e_hit", "d"}


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
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def plain_k(p):
    """--plain: a skill hit at its expected size with Gray Buff's crits (chance p_crit + half p_bonus, 200 + p_cdmg %)."""
    return 100 + (p["p_crit"] + p["p_bonus"] // 2) * (100 + p["p_cdmg"]) // 100


def build(p, is_native=False):
    k = plain_k(p)
    strike = lambda dmg, ad: attack(dmg * k // 100, ad * k // 100)   # --plain's skill hit

    # ------------------------------------------------------------------ attack: Twin Bite
    if is_native:   # tft.dll: Rending Claws' bonus and count, the pups' bites
        extra = native("bite")
    else:
        emp = combine(attack(p["q_emp_dmg"], p["q_emp_ad"]), tsfx("q_emp"))
        pups = combine(*[delayed(p["r_gap"] * (i + 1), attack(p["r_dmg"], p["r_ad"]), view("r_bite"), tsfx("r_bite"))
                         for i in range(p["r_n"])])
        extra = combine(when("q_emp", emp, combine()), when("r_pack", pups, combine()))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), anim("attack", p["atk_dur"]),
                              delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"), extra)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Rending Claws
    if is_native:   # tft.dll: the lowest-health target, the landing, the rend, the counted empowered attacks
        rend = native("rend")
    else:
        rend = combine({"type": "Teleport"}, cview("q_land"), strike(p["q_dmg"], p["q_ad"]),
                       view("q_hit"), tsfx("q_hit"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), sfx("q_vo"), anim("leap", p["q_jump"]), flag("q_air", p["q_jump"], cc_immune=True),
                           delayed(p["q_jump"] - 1, rend, anim("rend", p["q_dur"] - p["q_jump"]),
                                   flag("q_emp", p["q_t"], attack_speed_mult=p["q_as"]))))

    # ------------------------------------------------------------------ skill2: Slayer's Howl
    howl = (flag("e_howl", p["e_t"], vamp=p["e_vamp"]) if is_native
            else flag("e_howl", p["e_t"], vamp=p["e_vamp"], attack_mult=p["e_plain"]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), sfx("e_vo"), anim("howl", p["e_dur"]), delayed(p["e_st"] - 1, howl)))

    # ------------------------------------------------------------------ ult: Pack Attack
    pounce = (native("pounce") if is_native
              else combine(attack(p["r_leap_dmg"], p["r_leap_ad"]), view("r_hit"), tsfx("r_bite")))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_vo"), anim("ult", p["r_dur"]), flag("r_pack", p["r_t"]),
                         delayed(p["r_st"] - 1, sfx("r_leap"), pounce),
                         delayed(p["r_t"] - 2, sfx("r_end"))))

    # ------------------------------------------------------------------ views
    E = lambda name, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": name, "z": z,
                                        "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # every hit picture sits on the unit hit and is drawn symmetric (both sides); the landing dust lies round its feet
    # (z -1). tft.dll plays q_land, q_hit, r_hit, r_bite and p_hit (a skill crit) itself; the sounds q_hit, e_hit, r_bite, p and d too
    views_e = [E("a_hit"), E("q_land", -1, False), E("q_hit"), E("r_hit"), E("r_bite")]
    if is_native:
        views_e.append(E("p_hit", 3))
    views_b = [B_("q_emp", FX, 3), B_("e_howl", FX, 3), B_("r_pack", BIG, -1)]   # the pups stand beside it (z -1)
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0,
                 "crit_chance": p["p_crit"] if is_native else p["p_crit"] + p["p_bonus"] // 2},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/murkwolf.rs): Gray Buff, the rend, the bites, the howl's damage
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:gray", "params": {k_: p[k_] for k_ in NATIVE_KEYS}},
               **{k_: v for k_, v in kit.items() if k_ not in ("id", "category", "tags")}}
    return kit


SY_WAVES, SY_GAP = 4, 50


def sylas_ult(p=None):
    """Pack Attack as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, and the kit's bites ride its own attack, so in his hands the pups
    would only pounce; his pups pounce at his target and bite it SY_WAVES times SY_GAP ticks apart instead (r_n bites
    each, r_dmg + r_ad% AD), then run off. The views are the kit's own (tft_murkwolf_*); make_override copies them and
    their sheets."""
    p = dict(P) if p is None else p
    bite = lambda: combine(attack(p["r_dmg"], p["r_ad"]), view("r_bite"), tsfx("r_bite"))
    waves = [delayed(p["r_st"] + (w + 1) * SY_GAP + i * p["r_gap"] - 1, bite())
             for w in range(SY_WAVES) for i in range(p["r_n"])]
    t = p["r_st"] + (SY_WAVES + 1) * SY_GAP
    return combine(sfx("r"), sfx("r_vo"), flag("r_pack", t),
                   delayed(p["r_st"] - 1, sfx("r_leap"), attack(p["r_leap_dmg"], p["r_leap_ad"]), view("r_hit"),
                           tsfx("r_bite")),
                   *waves, delayed(t - 2, sfx("r_end")))


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
    """addons/tft/src/murkwolf.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`mw("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "murkwolf.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"murkwolf.rs Params::default() differs from P (murkwolf.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'mw\("(\w+)"\)', src)) - set(NATIVE_ONLY)
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"murkwolf.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_murkwolf:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects murkwolf.rs does not register: {sorted(called - registered)}")


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
