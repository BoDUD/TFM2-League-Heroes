"""Build tft_scuttlecrab.data_champion (a tft pack hero: the Scuttle Crab, support, Util) from the parameters P.

    python tools/kit/build_scuttlecrab.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Scuttle Crab (迅捷蟹; official 峡谷迅捷蟹) is Teamfight Tactics set 18's 2-cost Riftbeast / Juggernaut
(DA_Scuttlecrab18, range 1, 950 health, 50 attack, 45 armour and magic resistance, 40/100 mana). TFT gives it one ability,
Can You Dig It? / 这种快乐你懂吗？ - passive: its attacks are a dance that strikes every adjacent enemy; active: it burrows,
taking less damage and healing over the burrow; Green Buff: allies who fall under a health line restore a share of their
maximum health. The rest is our own design (the user: 「技能也要自己设」; picks 2026-11-01: support lane, plan A 「河道守护」),
from League's river crab (its speed shrine, its shield that breaks into a slow):
  passive Green Buff (绿霸符, TFT's trait): an allied champion within p_r (itself too) who falls under p_low% health
          heals p_pct% of its maximum health, then not again for p_cd ticks (each one its own cooldown; tft.dll's
          `tft_scuttlecrab:greenbuff`). --plain: Speed Shrine's cast heals itself and the allies within p_r p_plain,
          off a p_cd lockout (the data reads no health).
  attack  Crab Dance (螃蟹舞, TFT's) on `Enemy` (towers too): at atk_st every enemy within a_r of it takes 100% AD.
  skill   Speed Shrine (疾行神龛), `None` on `EnemyWithoutTower` (q_range: waves and camps too): at q_st a shrine q_r
          wide stays at its feet for q_t ticks, its water splashing every enemy within q_r as it rises (q_dmg + q_ap% AP
          magic damage, q_slow% slower for q_slow_t ticks); every q_every ticks the allied champions in it (itself too)
          get q_ms% move speed and q_as% attack speed for q_buff_t ticks.
  skill2  Shell Shield (蟹壳护盾), `None` on `EnemyChampion` (e_range): it pulls everything into the shell (e_dur ticks)
          and gets an e_sh + e_sh_ap% AP shield for e_t ticks; when the shield is spent or runs out the shell bursts:
          every enemy within e_r takes e_dmg + e_dmg_ap% AP magic damage, is stunned e_stun ticks and e_slow% slower
          for e_slow_t ticks (tft.dll's passive watches the shield). --plain: the burst comes when e_t runs out.
  ult     Can You Dig It? (你挖得动吗？, TFT's), `None` on `EnemyChampion` (r_range): it burrows for r_t ticks taking
          r_red% less damage, immune to crowd control, healing r_heal + r_heal_ap% AP over the burrow (r_n pulses);
          then it bursts out: every enemy within r_r takes r_dmg + r_ad% AD physical damage and is knocked up r_up ticks.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/scuttlecrab.rs; params NATIVE_KEYS): the data
reads no health and no shield, so it cannot heal whoever falls low nor break the shell when the shield is spent. A build of
P checks scuttlecrab.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_scuttlecrab"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's tank supports (tft_idas, tft_meepsie, tft_loris); radii count the unit's
# collision radius (~15000) on top. Timings are placeholders until the strips are rigged (tools/art/rig_scuttlecrab.py).
# Stats start from tft_meepsie's (hp 1250 +118, atk 66, apw 30 +15, def 44, mr 40): the 2-cost crab, quick on its legs
# (迅捷: ms 1000).
# Numbers = the 10-min classic-SDK simulations (C:/t/sc_sim with C:/t/al_sim/kd.py: support lane 4 against the base
# priest, monk, bard, enchanter and taoist, three lineups, both sides; 2026-11-01), --plain (the Green Buff on the shrine's
# cast, the shell bursting when e_t runs out): the draft (no damage on Q, no stun on E, attack 58 every 90) -3.73 (+-0.44)
# on seeds 1-8 - very tanky (10616 taken, 3968 healed) but nothing to kill with; + the shrine's splash (80 + 60%, 40%
# slow), the shell's 0.5 s stun, shorter cooldowns -1.25 .. -0.81; the ult cast only ~5 times a game (in reach 30000):
# r_range 50000, E every 6 s from 60000, the dance 35000 wide +0.26 / -0.25 (seeds 9-16); its attack every 80 ticks and
# the shrine 55000 wide +0.44 (+-0.33) on seeds 1-16 = P; tft_idas --plain +1.23 / +1.20 on the same games.
P = {
    # stats (Util, the tank supports)
    "hp": 1200, "hp_g": 115, "atk": 70, "atk_g": 5, "apw": 30, "apw_g": 15, "def": 44, "def_g": 8, "mr": 40, "mr_g": 6,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 80, "atk_st": 15, "a_r": 35000,
    # passive Green Buff (TFT's: allies under a health line restore a share of their maximum health)
    "p_low": 40, "p_pct": 12, "p_r": 70000, "p_cd": 600, "p_plain": 120,
    # Speed Shrine (League's crab shrine)
    "q_cd": 420, "q_range": 60000, "q_dur": 30, "q_st": 12, "q_r": 55000, "q_t": 240, "q_every": 15, "q_buff_t": 24,
    "q_ms": 30, "q_as": 25, "q_dmg": 80, "q_ap": 60, "q_slow": 40, "q_slow_t": 90,
    # Shell Shield (League's crab shield: when it breaks, the crab is slowed - here the enemies round it are)
    "e_cd": 360, "e_range": 60000, "e_dur": 36, "e_st": 8, "e_sh": 120, "e_sh_ap": 60, "e_t": 120, "e_r": 40000,
    "e_dmg": 80, "e_dmg_ap": 60, "e_slow": 40, "e_slow_t": 90, "e_stun": 30,
    # Can You Dig It? (TFT: burrow, durability, heal over the burrow)
    "r_cd": 1500, "r_range": 50000, "r_t": 150, "r_out": 24, "r_red": 50, "r_heal": 250, "r_heal_ap": 80, "r_n": 5,
    "r_r": 50000, "r_dmg": 160, "r_ad": 60, "r_up": 90,
}
# what tft.dll reads from passive.params (addons/tft/src/scuttlecrab.rs)
NATIVE_KEYS = ("p_low", "p_pct", "p_r", "p_cd", "e_t", "e_r", "e_dmg", "e_dmg_ap", "e_slow", "e_slow_t", "e_stun")
# names scuttlecrab.rs uses that need no view: sounds (the Green Buff's heal, the shell bursting, the death)
NATIVE_ONLY = {"p", "e_break", "d"}


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


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    dur = "WithShield" if tick == "WithShield" else {"Time": {"tick": tick}}
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": dur, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


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
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": kind}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on it alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}



def shrine(name, radius, tick, period, effects):
    """A zone at its feet (a `None` cast) ticking on its allied champions. No view: a zone's picture turns with its
    direction (red side: upside down, the ring under it thrown over it), so the ring is a CasterViewEffect beside it."""
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": "AllyChampion", "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the dance
    dance = around(p["a_r"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, dance)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Speed Shrine
    green = None
    if not is_native:   # the sims: the Green Buff on the shrine's cast, off a p_cd lockout (the data reads no health)
        mend = [heal(p["p_plain"], 0, "Ally"), view("p_heal")]
        green = when("p_cd", combine(), combine(flag("p_cd", p["p_cd"]), sfx("p"),
                                                on_me(heal(p["p_plain"], 0), view("p_heal")),
                                                around(p["p_r"], "AllyNotSelf", mend)))
    haste = [buff("q_haste", p["q_buff_t"], move_speed_mult=p["q_ms"], attack_speed_mult=p["q_as"])]
    splash = None
    if p["q_dmg"] or p["q_ap"]:   # the shrine's water splashes the enemies round it as it rises
        splash = around(p["q_r"], "EnemyWithoutTower", [ap(p["q_dmg"], p["q_ap"]),
                                                        buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"])])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "None", "EnemyWithoutTower" if splash else "EnemyChampion",
                   combine(sfx("q"), delayed(p["q_st"] - 1, sfx("q_buff"), cview("q_shrine"),
                                             shrine("q_shrine", p["q_r"], p["q_t"], p["q_every"], haste), splash, green)))

    # ------------------------------------------------------------------ skill2: Shell Shield
    shell = [shield(p["e_sh"], p["e_sh_ap"], p["e_t"]), flag("e_shell", p["e_t"])]
    burst = None
    if not is_native:   # the sims: the shell bursts when e_t runs out (tft.dll: as soon as the shield is spent)
        shards = [ap(p["e_dmg"], p["e_dmg_ap"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                  {"type": "Stun", "duration": p["e_stun"]} if p["e_stun"] else None]
        burst = delayed(p["e_st"] + p["e_t"] - 2, sfx("e_break"), cview("e_burst"),
                        around(p["e_r"], "EnemyWithoutTower", shards))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "None", "EnemyChampion",
                    combine(sfx("e"), delayed(p["e_st"] - 1, on_me(*shell)), burst))

    # ------------------------------------------------------------------ ult: Can You Dig It?
    every = p["r_t"] // p["r_n"]
    pulses = [delayed(k * every - 1, on_me(heal(p["r_heal"] // p["r_n"], p["r_heal_ap"] // p["r_n"])),
                      sfx("r_heal") if k == 1 else None) for k in range(1, p["r_n"] + 1)]
    struck = [attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_up")]
    out = combine(sfx("r_up"), sfx("r_hit"), cview("r_burst"), around(p["r_r"], "EnemyWithoutTower", struck))
    ult = action("ult", p["r_t"] + p["r_out"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
                 combine(sfx("r"), cview("r_dig"), flag("r_burrow", p["r_t"], damaged_reduce=p["r_red"], cc_immune=True),
                         *pulses, delayed(p["r_t"] - 1, out)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # q_shrine is the water ring of the shrine on the ground where it was cast (not following, its frames cover the
    # zone's q_t); e_burst / r_dig / r_burst ride on it, drawn left-right symmetric (the client never mirrors a picture);
    # the haste, the slows (the shrine's splash wears the shell's wet ground too) and the shell glow are buff pictures on
    # whoever holds them
    views_p = []
    views_e = [E("a_hit"), E("p_heal", FX, 3), E("q_shrine", BIG, -1, False), E("e_burst", BIG, 3), E("r_dig", BIG, -1),
               E("r_burst", BIG, 3), E("r_up", FX, 3)]
    views_b = [B_("q_haste", FX, 3), B_("e_slow", FX, 3), B_("q_slow", FX, 3, "e_slow"), B_("e_shell", FX, 3)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "Heal", "Shield", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/scuttlecrab.rs): the Green Buff, the shell bursting, the death sound
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:greenbuff", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Can You Dig It? as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): the ult is
    data alone, the same as the kit's (its views tft_scuttlecrab_*, copied with their sheets by make_override)."""
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
    """addons/tft/src/scuttlecrab.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every name it plays or puts on (`sc("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "scuttlecrab.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"scuttlecrab.rs Params::default() differs from P (scuttlecrab.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'\bsc\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"scuttlecrab.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_scuttlecrab:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code scuttlecrab.rs does not register: {sorted(called - registered)}")


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
