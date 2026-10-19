"""Build tft_powder.data_champion (the tft pack's first hero: Powder, mid, Magician) from the parameters P.

    python tools/kit/build_powder.py [--set key=value ...] [--out file] [--params json] [--nodes]

The tft pack (mod_id tft, folder tft/) holds Teamfight Tactics' own units - heroes League of Legends does not have.
Powder is young Jinx from Arcane (TFT set 13, Into the Arcane: Family / Scrap / Ambusher; her ability throws a monkey
bomb at the biggest group of enemies, less damage farther from the blast, and wounds and burns them). TFT gives her
one ability, so the kit is our own design (the user's pick, 2026-10-19: plan A 「猴子炸弹」 - three skills and a passive):
  passive Ambusher - "This one's gonna work!" (伏击者·这次一定能成): her skill bombs can crit (p_crit% chance, a crit is
          always 2x in this game). A crit only rolls on `ApAttack {can_crit: true}`; the chance is a 1-tick caster buff
          laid right before each skill hit (it counts in the tick it is added, champion-data section 4), so her basic
          attacks never crit (TFT: Ambushers' abilities crit). It is taken off and laid again for each unit hit: added
          per hit, a blast on five units stacked it to 125% and every bomb crit (sim +7.5 against +1.7 without).
  attack  a homemade firecracker (100% AD), a homing projectile on `Enemy` (towers too) released on a_rel.
  skill   Monkey Bomb (猴子炸弹, TFT's ability), `Targeting` on `EnemyWithoutTower` (q_range): the wind-up monkey is
          lobbed onto the spot the target stood on (q_travel ticks). The blast falls off: everyone within q_r takes
          q_dmg + q_ratio% AP, and within the centre q_cr the same again (the centre takes it twice: full, the ring half);
          everyone hit burns (q_burn + q_burn_r% AP every q_burn_p ticks for q_burn_t) and is wounded (heal_reduce
          q_wound% for q_wound_t). TFM2 has no "biggest group" target: the bomb goes where her target stands.
  skill2  Run, Powder! (快跑，爆爆！), `Targeting` on `EnemyChampion` within e_range (the AI casts it as a champion
          closes in): a flash-smoke bomb at her feet - e_dmg + e_ratio% AP within e_r, every enemy there blinded
          (`BlockAttack`, e_blind ticks: no basic attacks) - and she hops back from that champion (MoveBack).
  ult     The Hex Crystal Bomb (海克斯水晶炸弹 - the one that finally worked, Arcane episode 3), `Targeting` on
          `EnemyChampion` (r_range): the bag with the crystal is lobbed to the champion's spot (r_travel), its fuse
          burns r_fuse ticks (a blue ring on the spot from the throw), then a blue blast: r_dmg + r_ratio% AP within
          r_r, everyone there knocked up (Airborne r_up ticks).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_powder"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are
# the strips' (tools/art/rig_powder.py MS): the attack's throw frame 3 from 180 ms (a_rel 11, 380 ms), Q's toss frame 3
# from 200 ms (q_rel 12), E's slam frame 2 from 70 ms (e_rel 5), R's throw frame 4 from 300 ms (r_rel 18, 620 ms). Numbers = the 10-min
# classic-SDK simulations (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three
# lineups, both sides, 8 seeds, 2026-10-19; league_ziggs +1.70 on seeds 1-8): the draft (Q 55 + 45%, E 60 + 40%,
# R 230 + 90%, burn 6 + 6%) +5.31 (deal 20514; without the crit +1.71 - a 25% crit is +25% of her damage);
# Q 38 + 30%, E 45 + 30%, R 170 + 65%, burn 5 + 5% +1.34 / +1.38 (seeds 9-16; deal 15036); on the strips' timings
# +1.77 / +2.29; Q 35 + 27% +0.65 / +0.57, with R 160 + 60% +0.79 / +1.23; Q 36 + 28% +1.55 / +0.72 (about +1.1) = P.
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9); she is a child:
    # a little less health, a little quicker
    "hp": 860, "hp_g": 95, "atk": 76, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 930, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 11, "a_speed": 4000,
    # passive Ambusher (TFT 2-5 Ambushers: 20-55% crit chance)
    "p_crit": 25,
    # Monkey Bomb
    "q_cd": 330, "q_range": 70000, "q_dur": 29, "q_rel": 12, "q_travel": 30, "q_r": 32000, "q_cr": 16000,
    "q_dmg": 36, "q_ratio": 28, "q_burn": 5, "q_burn_r": 5, "q_burn_p": 30, "q_burn_t": 180,
    "q_wound": 40, "q_wound_t": 240,
    # Run, Powder!
    "e_cd": 600, "e_range": 24000, "e_dur": 24, "e_rel": 5, "e_r": 28000, "e_dmg": 45, "e_ratio": 30,
    "e_blind": 60, "e_hop": 4000, "e_hop_t": 10,
    # The Hex Crystal Bomb
    "r_cd": 3000, "r_range": 75000, "r_dur": 37, "r_rel": 18, "r_travel": 36, "r_fuse": 54, "r_show": 9,
    "r_r": 42000, "r_dmg": 170, "r_ratio": 65, "r_up": 45,
}


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


def refresh(name, tick, **fields):
    return combine({"type": "RemoveCasterBuff", "name": n(name)}, flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio, crit=False):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": crit}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point (a `Delayed`
    there keeps it); `seen` = the telegraph played on the landing point the whole flight."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # passive: a skill hit rolls a crit at p_crit% (the 1-tick buff counts for the hit in its own tick)
    def bomb(dmg, ratio):
        return [refresh("crit", 1, crit_chance=p["p_crit"]), ap(dmg, ratio, crit=True)]

    # ------------------------------------------------------------------ attack: the firecracker
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_pop", "Enemy",
                                                                [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                                                p["a_speed"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Monkey Bomb
    burn = {"type": "AddCasted", "casted_type": "Fire", "duration": p["q_burn_t"], "period": p["q_burn_p"],
            "effects": [ap(p["q_burn"], p["q_burn_r"])]}
    wound = buff("q_wound", p["q_wound_t"], heal_reduce=p["q_wound"])
    ring = zone("q_ring", p["q_r"], bomb(p["q_dmg"], p["q_ratio"]) + [burn, wound, view("q_hit"), tsfx("q_hit")])
    core = zone("q_core", p["q_cr"], bomb(p["q_dmg"], p["q_ratio"]))
    monkey = lob("q_monkey", p["q_travel"], [view("q_blast"), sfx("q_blast"), ring, core])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_rel"] - 1, monkey)))

    # ------------------------------------------------------------------ skill2: Run, Powder!
    flash = bomb(p["e_dmg"], p["e_ratio"]) + [{"type": "BlockAttack", "tick": p["e_blind"]}, view("e_blind"),
                                              tsfx("e_hit")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sfx("e"), delayed(p["e_rel"] - 1, cview("e_smoke"), sfx("e_pop"),
                                              around(p["e_r"], "EnemyWithoutTower", flash),
                                              {"type": "MoveBack", "speed": p["e_hop"], "tick": p["e_hop_t"]})))

    # ------------------------------------------------------------------ ult: The Hex Crystal Bomb
    blast = zone("r_blast", p["r_r"], bomb(p["r_dmg"], p["r_ratio"]) + [{"type": "Airborne", "duration": p["r_up"]},
                                                                        view("r_hit"), tsfx("r_hit")])
    fuse = [view("r_fuse")] + [delayed(k, view("r_fuse")) for k in range(p["r_show"], p["r_fuse"], p["r_show"])]
    land = [sfx("r_fuse")] + fuse + [delayed(p["r_fuse"], view("r_blast"), sfx("r_blast"), blast)]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), cview("r_cast"),
                         delayed(p["r_rel"] - 1, lob("r_bag", p["r_travel"], land, target="EnemyChampion",
                                                     seen="r_warn"))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    # a projectile's picture is turned with its flight: the firecracker, the monkey and the bag tumble (any turn reads)
    views_p = [Pj("a_pop"), Pj("q_monkey"), Pj("r_bag")]
    views_e = [E("a_hit"), E("q_blast", BIG, 2, False), E("q_hit"), E("e_smoke", BIG, 2), E("e_blind"),
               E("r_cast", FX, 3), E("r_warn", BIG, -2, False), E("r_fuse", FX, -1, False),
               E("r_blast", BIG, 2, False), E("r_hit")]
    views_b = [B_("q_wound", FX, 3)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range"],
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
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p)
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
