"""Build tft_norra.data_champion (the tft pack's second hero: Norra, mid, Magician) from the parameters P.

    python tools/kit/build_norra.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Norra is the yordle portal mage of Bandle City - in Teamfight Tactics set 12 the unit "Norra & Yuumi", and since
2026-02 a champion of League of Legends: Wild Rift (英雄联盟手游), its first one of its own. Her kit follows Wild Rift's
(the user, 2026-10-26: 「你要参照手游的技能啊」「参照金铲铲的干嘛」 - TFT's ability and Yuumi dropped), what the data
cannot do in the add-on (「不一致的地方就做附加包」: addons/tft_norra, the copy built with --native). TFM2 has three
active slots: Memory Surge (Q) is `skill`, Threads of Homecoming (E) `skill2`, Portalpalooza! (R) the `ult`; Journey to
Nowhere (W) is folded into the passive with Beloved Trinkets (the user's pick: layout A - W as her lifeline).
  passive Beloved Trinkets (寄情琐物): every p_cd ticks her next Q or E leaves trinkets where it lands (Wild Rift: 2-4
          scattered, 4 s): here one field of them, p_tr wide, for p_life ticks (`ApplyInProjectile`: each enemy champion
          that walks in is hit once): p_dmg + p_ratio% AP magic damage and the Threads. While a field lies there (flag
          p_live) a Q landing beside it primes it (Wild Rift: a full charge detonates every trinket): enemy champions within
          q_prime_r of the blast take the trinkets' hit.
          Journey to Nowhere (奇异旅程, folded): when she attacks with an enemy champion within w_r of her and w_cd is off,
          a portal opens under it: w_dmg + w_ratio% AP and banished w_t ticks (Wild Rift 2.25 s: cast out of the fight,
          nothing reaches it, it does nothing), the portal humming where it stood (Banish lock picture) and spitting it
          out (end picture); w_cd ticks to the next.
  attack  a star bolt off her pointing finger (100% AD), homing on `Enemy` (towers too), released on a_rel.
  skill   Memory Surge (回忆涌现), `Targeting` on `EnemyWithoutTower` (q_range): she gathers her memories (the charge,
          q_rel ticks: she stands in the cast) and flings a bolt of them, recoiling a step (MoveBack q_hop); it lands where
          the target stood (q_travel): q_dmg + q_ratio% AP within q_r, the Threads on champions; the trinkets primed when
          a field lies there; this Q leaves a field when the passive is ready. Wild Rift charges for range and damage
          (55-220 + 60% to 77-308 + 84%) and stops on the first champion: the AI's cast is one full charge.
  skill2  Threads of Homecoming (思乡线缕), `Targeting` on `EnemyWithoutTower` (e_range): two portals open at the target's
          sides and e_delay ticks later threads shoot between them: e_dmg + e_ratio% AP within e_r (Wild Rift: a 700 x
          200 band between the portals; here a circle) and the Threads on every enemy hit; leaves trinkets when ready.
  ult     Portalpalooza! (传送门欢腾！), `Targeting` on `EnemyChampion` (r_range): a rift opens on the champion's spot
          (r_r) and four volleys of yarn balls cross it, r_gap ticks apart: each enemy champion inside takes r_dmg +
          r_ratio% AP and is slowed r_slow% for r_slow_t ticks; the fourth volley hits r_last% more (Wild Rift: 140%).
          Wild Rift sends each ball along a path the player swipes, the first champion it meets slowed: the add-on's.
  Threads (线缕): bigger (radius_mult t_size%: Wild Rift +100% hitbox, easier to hit) and damaged_amplify t_amp% for
          t_t ticks (Wild Rift: Memory Surge deals 1-2.5% max health more to them - the data reads no max health of the
          target), slowed t_slow% for t_slow_t ticks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_norra"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid (Wild Rift 550); radii count the unit's collision radius (~15000) on top.
# Timings are the strips' (tools/art/rig_norra.py MS): the attack 400 ms, the bolt off her pointing finger at 133 ms
# (a_rel 9 -> tick 8); Memory Surge 767 ms, gathered 400 ms, the bolt flung at its end (q_rel 25 -> tick 24); Threads of
# Homecoming 433 ms, the portals as the ring goes up at 133 ms (e_rel 9); Portalpalooza! 667 ms, the rift sent as she
# pushes down at 400 ms (r_rel 25). Numbers = the 10-min classic-SDK simulations (C:/t/nr_sim, a copy of the balance
# sim: mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides;
# league_ziggs +1.38 / +2.22 on seeds 1-8 / 9-16, 2026-10-26): the Wild Rift draft (Q 50 + 40%, E 45 + 35%, the Threads
# +50% size and +8% damage taken, R 50 + 25% a volley on r 45000, W banishing 135 ticks every 1200 within 22000) +7.07;
# R 30 + 15% on 35000 +5.86 and W 90 ticks every 1500 within 18000 +5.82 (neither moved it); Q 38 + 30%, E 35 + 26%,
# the Threads +30% size and no damage taken +2.02; the same without the size +1.47; +15% size and Q 35 + 28% +1.30 /
# +1.98 = P (the Threads' size is what she leans on: every Q and E lands surer on them).
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9); a small yordle
    "hp": 860, "hp_g": 95, "atk": 74, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 20, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 9, "a_speed": 4000,
    # Beloved Trinkets (Wild Rift: cd 21-12 s, 20-90 + 20% AP, trinkets for 4 s)
    "p_cd": 600, "p_tr": 26000, "p_life": 240, "p_dmg": 30, "p_ratio": 20, "p_show": 60,
    # Journey to Nowhere, folded (Wild Rift: cd 23-20 s, 65-185 + 40% AP, banished 2.25 s)
    "w_cd": 1500, "w_r": 18000, "w_dmg": 40, "w_ratio": 30, "w_t": 90,
    # Memory Surge
    "q_cd": 330, "q_range": 90000, "q_dur": 46, "q_rel": 25, "q_travel": 20, "q_r": 18000,
    "q_dmg": 35, "q_ratio": 28, "q_hop": 2000, "q_hop_t": 12, "q_prime_r": 45000,
    # Threads of Homecoming (Wild Rift: cd 12-7.5 s, 70-220 + 60% AP after 0.3 s)
    "e_cd": 600, "e_range": 85000, "e_dur": 26, "e_rel": 9, "e_delay": 18, "e_r": 28000, "e_dmg": 35, "e_ratio": 26,
    # the Threads (Wild Rift: +100% hitbox 4 s, slowed 20% 2 s)
    "t_t": 240, "t_size": 15, "t_amp": 0, "t_slow": 20, "t_slow_t": 120,
    # Portalpalooza! (Wild Rift: cd 105-85 s, 4 balls of 100-180 + 55% AP, the 4th 140%, 1st champion slowed 80% 0.5 s)
    "r_cd": 3000, "r_range": 100000, "r_dur": 40, "r_rel": 25, "r_travel": 10, "r_r": 35000, "r_gap": 30,
    "r_dmg": 30, "r_ratio": 15, "r_last": 40, "r_slow": 80, "r_slow_t": 30, "r_show": 30,
}
# what the add-on reads from passive.params (addons/tft_norra)
NATIVE_KEYS = ("p_cd", "p_tr", "p_life", "p_dmg", "p_ratio", "q_prime_r", "t_t", "t_size", "t_amp", "t_slow",
               "t_slow_t", "r_r", "r_gap", "r_dmg", "r_ratio", "r_last", "r_slow", "r_slow_t")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def refresh(name, tick, **fields):
    return combine(unflag(name), flag(name, tick, **fields))


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pick(rng, target, effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point (a `Delayed`
    there keeps it); `seen` = the picture played on the landing point the tick it is fired."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def once(name, radius, tick, effects, target="EnemyChampion"):
    """Each unit hit once over the zone's whole life, on the tick it first touches it (league_thresh R)."""
    return {"type": "ApplyInProjectile", "name": n(name), "shape": circle(radius), "tick": tick,
            "follow_caster": False, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ the Threads (E, the trinkets, Q)
    threads = [buff("t_mark", p["t_t"], radius_mult=p["t_size"], damaged_amplify=p["t_amp"]),
               buff("t_slow", p["t_slow_t"], move_speed_mult=-p["t_slow"])]

    # ------------------------------------------------------------------ passive: Beloved Trinkets
    burst = [ap(p["p_dmg"], p["p_ratio"]), view("p_burst"), tsfx("p_burst")] + threads
    # the field of trinkets where a ready Q / E lands: seen every p_show ticks (an upright picture, never turned)
    shows = [view("p_trinkets")] + [delayed(k, view("p_trinkets")) for k in range(p["p_show"], p["p_life"], p["p_show"])]
    trinkets = combine(flag("p_cd", p["p_cd"]), refresh("p_live", p["p_life"]), sfx("p_drop"),
                       once("p_field", p["p_tr"], p["p_life"], burst), *shows)
    leave = when("p_cd", combine(), trinkets)
    # the add-on scatters real trinkets instead (each one taken by the first enemy champion that steps on it): the copy
    # only marks where and when (p_drop on her for 2 ticks)
    if is_native:
        leave = when("p_cd", combine(), combine(flag("p_cd", p["p_cd"]), flag("p_drop", 2)))

    # Journey to Nowhere, folded into her attack: a close enemy champion banished
    banish = {"type": "Banish", "duration": p["w_t"], "lock_effect_name": n("w_lock"), "end_effect_name": n("w_out")}
    journey = pick(p["w_r"], "EnemyChampion", [flag("w_cd", p["w_cd"]), ap(p["w_dmg"], p["w_ratio"]), view("w_in"),
                                               tsfx("w"), banish])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(when("w_cd", combine(), journey),
                              delayed(p["a_rel"] - 1, sfx("a"),
                                      homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                             p["a_speed"]))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Memory Surge
    prime = zone("q_prime", p["q_prime_r"], burst, target="EnemyChampion")
    blast = [view("q_blast"), sfx("q_blast"),
             zone("q_hit", p["q_r"], [ap(p["q_dmg"], p["q_ratio"]), view("q_hit")]),
             zone("q_thread", p["q_r"], threads, target="EnemyChampion")]
    if is_native:                             # the add-on detonates the real trinkets near the blast instead
        blast.append(flag("q_prime", 2))
    else:
        blast.append(when("p_live", prime, combine()))
    blast.append(leave)
    bolt = lob("q_bolt", p["q_travel"], blast)
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_rel"] - 1, sfx("q_fire"), bolt,
                                             {"type": "MoveBack", "speed": p["q_hop"], "tick": p["q_hop_t"]})))

    # ------------------------------------------------------------------ skill2: Threads of Homecoming
    weave = lob("e_gate", p["e_delay"], [sfx("e_hit"),
                                         zone("e_hit", p["e_r"], [ap(p["e_dmg"], p["e_ratio"]), view("t_hit")] + threads),
                                         leave],
                seen="e_threads")
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    delayed(p["e_rel"] - 1, sfx("e"), weave))

    # ------------------------------------------------------------------ ult: Portalpalooza!
    def volley(k, last=False):
        bonus = 100 + (p["r_last"] if last else 0)
        hit = [ap(p["r_dmg"] * bonus // 100, p["r_ratio"] * bonus // 100),
               buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]), view("r_hit"), tsfx("r_hit")]
        return delayed(k, view("r_yarn"), sfx("r_ball"), zone(f"r_v{k}", p["r_r"], hit, target="EnemyChampion"))
    gaps = [p["r_gap"] * (i + 1) for i in range(4)]
    rift = [view("r_rift"), sfx("r_open")] + [delayed(k, view("r_rift")) for k in range(p["r_show"], gaps[-1] + 1,
                                                                                         p["r_show"])]
    if is_native:                             # the add-on sends the yarn balls along their paths instead
        rift.append(flag("r_open", gaps[-1] + 2))
    else:
        rift += [volley(k, last=(i == 3)) for i, k in enumerate(gaps)]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), delayed(p["r_rel"] - 1, lob("r_gate", p["r_travel"], rift, target="EnemyChampion"))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # a_bolt and q_bolt (the memory ball) are turned with their flight, both symmetric top to bottom; e_gate, r_gate
    # and the zones fly / lie hidden: their pictures are upright ViewEffects on the spot (never turned)
    views_p = [Pj("a_bolt"), Pj("q_bolt")]
    views_e = [E("a_hit"), E("p_trinkets", BIG, -1, False), E("p_burst"), E("w_in", FX, 2, False),
               E("w_lock", FX, 2, False), E("w_out", FX, 2, False), E("q_blast", BIG, 2, False), E("q_hit"),
               E("e_threads", BIG, 2, False), E("t_hit"), E("r_rift", BIG, -2, False), E("r_yarn", BIG, 2, False),
               E("r_hit")]
    views_b = [B_("t_mark", FX, 3), B_("r_slow", FX, 3)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"],
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
    if is_native:
        kit["passive"] = {"name": f"{ID}:trinkets", "params": json.dumps({k: p[k] for k in NATIVE_KEYS},
                                                                       separators=(",", ":"))}
    return kit


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (addons/tft_norra)")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, a.native)
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
