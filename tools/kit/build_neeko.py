"""Build league_neeko.data_champion (mid, Magician: the Curious Chameleon) from the parameters P.

    python tools/kit/build_neeko.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-21: MID (the plan had her support), layout A - Q / E / R, W's passive on her attacks,
the passive Inherent Glamour as an add-on; 「有连招要做连招」). TFM2 has three active slots: Blooming Burst (Q) is
`skill`, Tangle-Barbs (E) `skill2`, Pop Blossom (R) the `ult`.
  passive Inherent Glamour (天生幻魅): League's disguise as an allied champion. Data cannot change her look: the add-on
          (addons/league_neeko, the --native copy) dresses her in an ally's frames and drops it on a damaging cast,
          crowd control or a big hit. Without the add-on she has no passive.
  attack  A magic bolt (homing on `Enemy`, physical 100% AD), released on a_rel. Shapesplitter's passive (两生花影, W):
          every third attack (the caster flags w1, w2 count them) adds w_dmg + w_ratio% AP magic damage and gives her
          +w_ms% move speed for w_ms_t ticks.
  skill   Q Blooming Burst (盛开花种, one cooldown q_cd, the slot's and the flag `q_cd` R -> Q reads): a `Targeting` cast on
          `EnemyWithoutTower` (q_range). A seed lobbed onto the target's spot (q_travel ticks) bursts there (q_r):
          q_dmg + q_ratio% AP. A champion in the burst makes it bloom again q_rep ticks later on the same spot (a
          champion-only twin of the zone lays the caster flag q_b1 / q_b2), q2_dmg + q2_ratio% AP, at most twice
          (League: blooms up to two more times when it hits a champion or kills a unit - nothing reads a kill).
  skill2  E Tangle-Barbs (缠结倒刺, one cooldown e_cd): a `Targeting` cast on `EnemyWithoutTower` (e_range): a ball of
          barbs runs straight at the target and on (penetrating, e_len): e_dmg + e_ratio% AP and a root of e_root
          ticks on every enemy on the line. Past a champion it grows stronger (League: bigger, faster, a longer
          root): a champion-only twin lays `e_big` on its first champion, and every later champion it reaches is
          rooted e_add ticks more (a second `Bind` when the first ends).
  ult     R Pop Blossom (怒放): a `Targeting` cast on `EnemyChampion` (r_range). She gathers herself for r_charge
          ticks, shielded r_sh + r_sh_r% AP and r_sh_c more for every enemy champion within r_r (League: a shield
          for each champion near); then she springs up - the enemies round her are knocked up r_air ticks - and
          lands on the champion's spot (`MoveToTarget`): r_dmg + r_ratio% AP and a r_stun-tick stun round her (r_r).
  combos  E -> Q (缠结倒刺禁锢 -> 盛开花种): the barbs' champion twin opens `e_combo` for e_combo ticks; a Q cast in it is
          lobbed onto a champion in crowd control (normally the one just rooted) and bursts in q_fast ticks.
          R -> Q (怒放落地 -> 盛开花种): the landing throws the seed at once onto a stunned champion if Q is ready.
          The bloom's twin, the stun and the root keep the champion in the burst for the second and third bloom.
Timings: provisional (Zyra's frames) until her rig (tools/art/rig_neeko.py) sets them: every action releases on tick 10.
Numbers: the draft from league_zyra's balanced values (mid lane 2, 2026-10-20) - the simulation sets them.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_neeko.data_champion")
ID = "league_neeko"
FX = "asset/league/effects/league_neeko_fx"
BIG = "asset/league/effects/league_neeko_big"

# League's Neeko (16.20, CommunityDragon neeko.bin): 610 +104 hp, 48 AD, 21 +5.2 armour, 30 mr, 340 move, 550 range,
# attack speed 0.625. Q: 800 range, 80-280 + 50% AP, blooms twice more 40-160 + 20% AP each, 0.75 s apart; cd 9-7. W
# passive: every third attack +50-200 + 60% AP magic and 10-47.5% move speed 1 s. E: 1000 range, 80-255 + 60% AP, root
# 0.7-1.7 s, 2.0-3.25 s once it passed a champion; cd 12-10. R: 1.25 s charge, a shield 75-200 + 40-140 a champion,
# 0.6 s leap knocking up, 150-1150 + 120% AP? (bin: 150/350/550 + ...) and a 0.75 s stun round her; cd 120-90.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9; league_zyra 900 +95
    # hp, 70 +6 attack, 18 +7 def)
    "hp": 880, "hp_g": 95, "atk": 70, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 17, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 92, "a_rel": 10, "a_speed": 4500, "a_y": -4000,
    # W Shapesplitter's passive: every third attack
    "w_dmg": 35, "w_ratio": 40, "w_ms": 30, "w_ms_t": 60,
    # Q Blooming Burst
    "q_cd": 420, "q_range": 80000, "q_dur": 30, "q_rel": 10, "q_travel": 25, "q_fast": 4, "q_r": 22000,
    "q_dmg": 75, "q_ratio": 50, "q_rep": 45, "q2_dmg": 30, "q2_ratio": 20,
    # the E -> Q window after the barbs reach a champion (the root's length)
    "e_combo": 60,
    # E Tangle-Barbs
    "e_cd": 660, "e_range": 90000, "e_dur": 30, "e_rel": 10, "e_speed": 2000, "e_len": 100000, "e_w": 7000,
    "e_dmg": 70, "e_ratio": 45, "e_root": 60, "e_add": 45, "e_y": 5000,
    # R Pop Blossom
    "r_cd": 2100, "r_range": 45000, "r_charge": 45, "r_dur": 30, "r_speed": 3500, "r_at": 2, "r_r": 40000,
    "r_sh": 80, "r_sh_r": 30, "r_sh_c": 40, "r_sh_t": 150, "r_air": 20, "r_dmg": 170, "r_ratio": 75, "r_stun": 50,
    "vo_gap": 600,
    # 1 = the copy for addons/league_neeko: the passive league_neeko:glamour (the disguise)
    "native": 0,
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
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def lob(name, travel, end):
    """A 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ attack: the bolt, every third one empowered
    bolt = lambda extra: homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit"), *extra],
                                p["a_speed"], p["a_y"])
    third = combine(*rm("w2"), sfx("w"), on_me(refresh("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"])),
                    bolt([ap(p["w_dmg"], p["w_ratio"]), view("w_hit")]))
    count = sw("w2", third, sw("w1", combine(*rm("w1"), flag("w2", None), bolt([])), combine(flag("w1", None), bolt([]))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("w2", anim("attack_w", p["atk_dur"])),
                              delayed(p["a_rel"] - 1, alive(sfx("a"), count))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Blooming Burst
    def bloom(k):
        """The k-th burst on the seed's spot (0 the first); a champion in it lays q_b<k+1> and the next one follows."""
        dmg, ratio = (p["q_dmg"], p["q_ratio"]) if k == 0 else (p["q2_dmg"], p["q2_ratio"])
        nxt = None
        if k < 2:
            b = f"q_b{k + 1}"
            nxt = [zone(f"q_twin{k}", p["q_r"], [refresh(b, p["q_rep"] + 2)], "EnemyChampion"),
                   delayed(p["q_rep"], sw(b, combine(*rm(b), *bloom(k + 1))))]
        return [view("q_burst" if k == 0 else "q_bloom"), sfx("q_burst" if k == 0 else "q_bloom"),
                zone(f"q_hit{k}", p["q_r"], [ap(dmg, ratio), view("q_hit"), tsfx("q_hit")]), *(nxt or [])]

    burst = bloom(0)
    # E -> Q / R -> Q: a champion in crowd control within reach gets the seed in q_fast ticks; q_go (1 tick) says found
    quick = pick(p["q_range"] + 10000, "EnemyChampionInCC", flag("q_go", 1), lob("q_seed", p["q_fast"], burst))

    def q_cast(fast_only):
        """Q's body: the cooldown flag, the throw, the seed (to a held champion when `fast_only` or in E's window)."""
        seed = (quick if fast_only else
                combine(*rm("q_go"), sw("e_combo", combine(*rm("e_combo"), quick)),
                        sw("q_go", NONE, lob("q_seed", p["q_travel"], burst))))
        return combine(*rm("q_go"), refresh("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q"),
                       voice("vo_q", p), delayed(p["q_rel"] - 1, alive(seed)))

    skill = action("idle", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), sw("q_cd", NONE, q_cast(False))), key="skill")

    # ------------------------------------------------------------------ skill2: E Tangle-Barbs
    rooted = [ap(p["e_dmg"], p["e_ratio"]), {"type": "Bind", "duration": p["e_root"]}, buff("e_bound", p["e_root"]),
              view("e_hit"), tsfx("e_hit")]
    longer = delayed(p["e_root"], {"type": "Bind", "duration": p["e_add"]}, buff("e_bound", p["e_add"]))
    grown = [sw("e_big", longer, refresh("e_big", p["e_len"] // p["e_speed"] + 5)), refresh("e_combo", p["e_combo"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), *rm("e_big"), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(
                                line("e_barbs", p["e_speed"], p["e_len"], p["e_w"], "EnemyWithoutTower", rooted,
                                     penetrate=True, y=p["e_y"]),
                                line("e_twin", p["e_speed"], p["e_len"], p["e_w"], "EnemyChampion", grown,
                                     penetrate=True, y=p["e_y"])))))

    # ------------------------------------------------------------------ ult: R Pop Blossom
    land = [cview("r_land"), sfx("r_land"),
            around(p["r_r"], "EnemyWithoutTower", [ap(p["r_dmg"], p["r_ratio"]), {"type": "Stun", "duration": p["r_stun"]},
                                                   view("r_hit"), tsfx("r_hit")]),
            delayed(2, sw("q_cd", NONE, combine(                            # R -> Q, only with a held champion near
                *rm("q_go"), pick(p["q_range"] + 10000, "EnemyChampionInCC", flag("q_go", 1)),
                sw("q_go", q_cast(True)))))]
    leap = combine(anim("ult_b", p["r_dur"]), sfx("r_jump"), cview("r_jump"),
                   around(p["r_r"], "EnemyWithoutTower", [{"type": "Airborne", "duration": p["r_air"]}]),
                   {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 20000,
                    "end_effects": [delayed(p["r_at"], alive(*land))]})
    ult = action("ult", p["r_charge"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), sfx("r"), sfx("r_sh"), voice("vo_r", p), cview("r_charge"),
                         on_me(shield(p["r_sh"], p["r_sh_r"], p["r_sh_t"])),
                         around(p["r_r"], "EnemyChampion", [on_me(shield(p["r_sh_c"], 0, p["r_sh_t"]))]),
                         delayed(p["r_charge"] - 1, alive(leap))))

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [Pj("a_bolt"), Pj("q_seed"), Pj("e_barbs")]
    views_e = [E("a_hit"), E("w_hit"), E("q_burst", BIG, -1, False), E("q_bloom", BIG, -1, False), E("q_hit"),
               E("e_hit"), E("r_charge", BIG, 3), E("r_jump", BIG, 3), E("r_land", BIG, -1, False), E("r_hit")]
    views_b = [B_("e_bound", FX, 3), B_("w_haste", FX, -1)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_neeko:glamour", "params": {}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    if a.native:
        p["native"] = 1
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
