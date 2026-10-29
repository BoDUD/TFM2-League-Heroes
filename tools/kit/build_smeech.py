"""Build tft_smeech.data_champion (the tft pack's fourteenth hero: Smeech, jungle, Assassin) from the parameters P.

    python tools/kit/build_smeech.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Smeech is one of Arcane's chem-barons, a small bad-tempered gremlin of Zaun with two big mechanical arms ending in long
brass claws, on brass stilts: a 3-cost of Teamfight Tactics set 13 (TFT13_Gremlin, Chem-Baron / Ambusher, an AD
reaper, range 1, 777 health, 70 AD, 0.8 attack speed, 25% crit, 20/70 mana). TFT gives him one ability (Scrap Hacker /
废铁黑客: leap at the enemy with the fewest items within 4 hexes, slash it 3 times for 500% AD in all; if it dies,
leap again for 30% less) and two traits: Ambusher (abilities can crit, +25-55% crit chance and +10-25% crit damage)
and Chem-Baron (shimmer; nothing in a fight). The rest is our own design (the user's pick, 2026-10-29: jungle, plan A
「废铁伏击手」):
  passive Ambusher (伏击): crit_chance p_crit in his stats (his attacks crit the engine's way, 2x); his skills crit
          too - tft.dll rolls their slashes against his crit chance and a crit deals 200 + p_cdmg % (p_hit flash).
          --plain: every skill hit dealt at its expected size (x plain_k%, below), no roll.
  attack  Double Rip (双爪连撕) on `Enemy` (towers too): 100% AD on atk_st, the two claws in turn (`a2` flag:
          `attack` / `attack2` frames and sounds).
  skill   Scrap Hacker (废铁黑客), `Targeting` on `EnemyWithoutTower` (q_range, camps too): he springs up (`leap`
          frames); on q_jump tft.dll (tft_smeech:hack) lands him beside the lowest-health enemy within q_range
          (champions first, else the AI's target) and slashes it on q_s1 / q_s2 / q_s3 after, each q_dmg + q_ad% AD
          (`stabs` frames); if it dies he leaps once more at the next one, every slash at q_again%.
          --plain: `Teleport` onto the AI's target and the three slashes there.
  skill2  Scrap Rip (拆解), `Targeting` on `EnemyWithoutTower` (e_range): on e_st both claws rip the target: e_dmg +
          e_ad% AD (tft_smeech:rip, it can crit) and its armour torn, defence_mult -e_shred for e_t ticks.
  ult     Scrap Frenzy (废铁狂潮), `Targeting` on `EnemyChampion` (r_range): unstoppable (cc_immune, r_dr% damage
          reduction) for r_dur ticks, he leaps r_n times, r_gap ticks apart from r_st: each hop (tft_smeech:hop) lands
          him on the next enemy within r_reach of him that this ult has not hit yet (champions first, then the lowest
          health), r_dmg + r_ad% AD, and adds r_crit crit chance for r_t ticks (the hops stack it).
          --plain: each hop a `RandomTarget` champion within r_reach (repeats possible), `Teleport` and the strike,
          and the crit buff.

tft.dll (addons/tft/src/smeech.rs): the skill crits (passive tft_smeech:ambush only records his params), the leap's
target and re-leap (tft_smeech:hack, slash1-3), the rip (tft_smeech:rip), the hops (tft_smeech:hop). A build of P
checks smeech.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_smeech"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# Units: melee range 23000 like the pack's jungle assassins; radii count the unit's collision radius (~15000) on top.
# Timings are provisional until the strips are rigged (tools/art/rig_smeech.py): the rake lands at 167 ms (atk_st
# 10), the leap takes 233 ms (q_jump 14) and the three slashes follow 8 / 16 / 24 ticks later, the rip at 167 ms
# (e_st 10), the hops 12 ticks apart. Stats start from the pack's jungle assassins (league_khazix hp 880 +84, atk 88
# +16; league_rengar; tft_violet hp 940 +100, atk 82 +17).
P = {
    # stats (Assassin, jungle)
    "hp": 900, "hp_g": 90, "atk": 84, "atk_g": 16, "apw": 0, "apw_g": 0, "def": 28, "def_g": 8, "mr": 22, "mr_g": 4,
    "ms": 1100, "ms_g": 12,
    "atk_range": 23000, "atk_dur": 22, "atk_cd": 54, "atk_st": 10,
    # passive Ambusher (TFT: abilities can crit; 2 Ambushers +25% crit chance, +10% crit damage)
    "p_crit": 25, "p_cdmg": 20,
    # Scrap Hacker (TFT: 4 hexes, 3 slashes for 500% AD in all, a re-leap on a kill at -30%)
    "q_cd": 420, "q_range": 45000, "q_dur": 54, "q_jump": 14, "q_gap": 14000, "q_s1": 8, "q_s2": 16, "q_s3": 24,
    "q_dmg": 20, "q_ad": 55, "q_again": 70,
    # Scrap Rip
    "e_cd": 480, "e_range": 26000, "e_dur": 24, "e_st": 10, "e_dmg": 40, "e_ad": 90, "e_shred": 30, "e_t": 240,
    # Scrap Frenzy
    "r_cd": 3000, "r_range": 50000, "r_dur": 72, "r_st": 6, "r_gap": 12, "r_n": 5, "r_reach": 45000,
    "r_dmg": 50, "r_ad": 80, "r_crit": 10, "r_t": 300, "r_dr": 30,
}
# what tft.dll reads from passive.params (addons/tft/src/smeech.rs), and the names only it puts on (flags: no view)
NATIVE_ONLY = ("q_again", "q_weak", "r_mark", "r_crit")
NATIVE_KEYS = ("p_cdmg", "q_range", "q_gap", "q_s1", "q_s2", "q_s3", "q_dmg", "q_ad", "q_again", "e_dmg", "e_ad",
               "r_dur", "r_reach", "r_dmg", "r_ad", "r_crit", "r_t")


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
    """--plain: a skill hit at its expected size with Ambusher's crits (chance p_crit, 200 + p_cdmg % on a crit)."""
    return 100 + p["p_crit"] * (100 + p["p_cdmg"]) // 100


def build(p, is_native=False):
    k = plain_k(p)
    strike = lambda dmg, ad: attack(dmg * k // 100, ad * k // 100)   # --plain's skill hit

    # ------------------------------------------------------------------ attack: the two claws in turn
    rake = lambda tag, s: combine(sfx(s), anim(tag, p["atk_dur"]),
                                  delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx(s + "_hit")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      when("a2", combine(unflag("a2"), rake("attack2", "a2")),
                           combine(flag("a2", None), rake("attack", "a"))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Scrap Hacker
    if is_native:   # tft.dll: the lowest-health target, the landing, the three slashes, the re-leap
        hack = native("hack")
    else:
        slash = lambda: combine(strike(p["q_dmg"], p["q_ad"]), view("q_hit"), tsfx("q_hit"))
        hack = combine({"type": "Teleport"}, cview("q_land"), sfx("q_land"),
                       *[delayed(p[s] - 1, slash()) for s in ("q_s1", "q_s2", "q_s3")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), sfx("q_vo"), anim("leap", p["q_jump"]), flag("q_air", p["q_jump"], cc_immune=True),
                           delayed(p["q_jump"] - 1, hack, anim("stabs", p["q_dur"] - p["q_jump"]))))

    # ------------------------------------------------------------------ skill2: Scrap Rip
    rip = native("rip") if is_native else strike(p["e_dmg"], p["e_ad"])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), delayed(p["e_st"] - 1, rip, buff("e_shred", p["e_t"], defence_mult=-p["e_shred"]),
                                              view("e_hit"), tsfx("e_hit"), tsfx("e_shred"))))

    # ------------------------------------------------------------------ ult: Scrap Frenzy
    if is_native:   # tft.dll: the next enemy not hit yet, the landing, the strike, the crit stack
        hop = lambda: native("hop")
    else:
        hop = lambda: combine({"type": "RandomTarget", "range": p["r_reach"], "casting_target": "EnemyChampion",
                               "from_projectile": False,
                               "effects": [{"type": "Teleport"}, strike(p["r_dmg"], p["r_ad"]), view("r_hit"),
                                           tsfx("r_hit")]},
                              flag("r_crit", p["r_t"], crit_chance=p["r_crit"]))
    hops = [delayed(p["r_st"] + i * p["r_gap"] - 1, sfx("r_leap"), hop()) for i in range(p["r_n"])]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), anim("ult", p["r_dur"]),
                         flag("r_frenzy", p["r_dur"], cc_immune=True, damaged_reduce=p["r_dr"]), *hops,
                         delayed(p["r_dur"] - 2, sfx("r_end"))))

    # ------------------------------------------------------------------ views
    E = lambda name, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": name, "z": z,
                                        "is_follow": follow}
    B_ = lambda name, z=2: {"type": "Animated", "name": n(name), "anim": FX, "tag": name, "repeat": True, "z": z}
    # every hit picture sits on the unit hit and is drawn symmetric (both sides); the landing dust lies round his
    # feet (z -1). tft.dll plays q_land, q_hit, r_hit and p_hit (a skill crit) itself
    views_e = [E("a_hit"), E("q_land", -1, False), E("q_hit"), E("e_hit"), E("r_hit")]
    if is_native:
        views_e.append(E("p_hit", 3))
    views_b = [B_("e_shred", 3), B_("r_frenzy", 3)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0,
                 "crit_chance": p["p_crit"]},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/smeech.rs): the skill crits, the leap, the rip, the hops
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:ambush", "params": {k_: p[k_] for k_ in NATIVE_KEYS}},
               **{k_: v for k_, v in kit.items() if k_ not in ("id", "category", "tags")}}
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
    """addons/tft/src/smeech.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`sm("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "smeech.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"smeech.rs Params::default() differs from P (smeech.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sm\("(\w+)"\)', src)) - set(NATIVE_ONLY)
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"smeech.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_smeech:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects smeech.rs does not register: {sorted(called - registered)}")


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
