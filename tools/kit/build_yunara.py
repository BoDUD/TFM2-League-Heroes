"""Build league_yunara.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_yunara.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-17: 「方案可以，全按推荐做（下路 ADC，基础暴击 10%，做附加包，R 形态换待机/跑步，PPU 1.5）」).
TFM2 has three slots, so Q is folded into the attack:
  passive Vow of the First Lands (初生之誓, crits deal bonus magic): nothing tells the data whether a hit crit, so every
          bead also carries a small magic part that rolls its own crit (`ApAttack can_crit`, the same chance: the same
          damage on average); she starts with crit_chance 10.
  attack  Cultivation of Spirit's passive (灵蕴拳): a bead thrown at the target (homing, physical a_ratio% AD) plus the
          magic part (p_dmg + p_ap% AP). A hidden twin on `EnemyWithoutTower` climbs her Unleash ladder (u1..u3 caster
          flags, u_t ticks each, refreshed by each climb): an enemy champion a full step, anything else half a step
          (the flag u_half). The step past u3 switches Q on by itself (League players press it at once): q_on for q_t
          ticks, attack_speed_mult q_as, and the ladder clears. Under q_on the bead deals q_dmg more magic and spreads:
          a 1-tick lob onto the unit hit opens a zone of q_sp_r round it (every enemy there, the unit too, takes q_sp%
          AD physical), so the bead itself deals a_ratio - q_sp%: the unit hit keeps its total, the ones round it get
          League's 30%.
  skill   W Arc of Judgment (善恶轮): a `Targeting` cast on `EnemyWithoutTower`; w_lock ticks before the release a hidden
          lob marks where the target stands, and the bead flies there and on (penetrating, w_len): w_dmg + w_ratio% AD
          physical on everyone it passes and a slow decaying over 1.5 s (three slows, 30 / 60 / 90 ticks); where it
          stops it spins w_linger ticks (a zone hitting every w_per ticks for w_dps + w_dps_r% AD).
          In R: Arc of Ruin (寂灭掌), a laser along the cast's line (`LineRangeProjectile`, shown at once, hitting
          rw_apply ticks later: dodgeable): rw_dmg + rw_ratio% AD and a slow decaying over 1 s.
  skill2  E Kanmei's Steps (明踪步): a `Targeting` cast on `EnemyChampion` (e_range): e_ms% move speed for e_t ticks, or
          e_ms2% when no enemy champion stands within her attack range (she is chasing: League's bonus toward a champion).
          In R: Untouchable Shadow (夜影翻): with an enemy champion within e_close she dashes straight away from her target
          (MoveBack re_v x re_t); else the chasing speed as above. The add-on picks the way of the dash.
  ult     R Transcend One's Self (定圣诀): a `Targeting` cast on `EnemyChampion` (r_range), only in a fight: two or more
          enemy champions within r_count, or an enemy champion in CC within r_range (else the cooldown comes back:
          ult_cooldown_mult 4900). r_t ticks: Q on for the whole time (no Unleash needed), W the laser, E the dash, and a
          3-tick skill_cooldown_mult 400 brings W and E to at most 20% of their cooldown (League's 80% on W).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_yunara.data_champion")
ID = "league_yunara"
FX = "asset/league/effects/league_yunara_fx"
BIG = "asset/league/effects/league_yunara_big"

# Numbers: the 10-min classic-SDK simulations (Temp/yu_sim, sim/kd.py --lane 3 against gunner, soldier, archer and
# gambler, three lineups, both sides, 12 seeds each, 2026-10-17): the League-ratio draft y0 (atk 106, Q 45% AS, W 90,
# laser 200, hp 1000) +2.47; y1 atk 100 + Q 40% +2.72 (noise); y2 + W 70, laser 160 +2.30; y3 + hp 950 +1.73 and +1.48
# on seeds 13-24 (+1.61 over 24, here); y4 Q 35% + W 60 +1.43 / +0.80.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Yunara: 575 range,
    # 55 AD, 590 +110 hp, 25 armour, 325 move, attack speed 0.65
    "hp": 950, "hp_g": 90, "atk": 100, "atk_g": 19, "def": 22, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    "crit": 10,
    # attack: the bead leaves her hand on a_st
    # (the strip: 67 + 66 ms of the beads rising into their arc, the push on frame 3 at 133 ms = tick 8)
    "atk_range": 57500, "atk_dur": 24, "atk_cd": 50, "a_st": 8, "a_ratio": 100, "bead_speed": 7000, "bead_y": -3000,
    # passive magic part (League: Q's passive 3-28 + 20% AP on-hit; the crit's bonus magic)
    "p_dmg": 18, "p_ap": 20,
    # Unleash (League: 2 a champion hit, 1 else, 8 to fill, 6 s before it drains) and Q (5 s, 10-70% AS, 3-28 + 20% AP
    # more on-hit, 30% AD to enemies within 300)
    "u_t": 360, "q_t": 300, "q_as": 40, "q_dmg": 18, "q_sp": 30, "q_sp_r": 30000,
    # skill: W (League: 1150 range, 0.45 s cast, 55-255 + 85% bonus AD + 50% AP, slow 99% decaying over 1.5 s, spins 1 s
    # at the end for 60% of that a second, cd 10 s)
    "w_cd": 600, "w_range": 90000, "w_dur": 27, "w_rel": 15, "w_lock": 8, "w_speed": 3600, "w_len": 110000,
    "w_rad": 6000, "w_y": -3000, "w_dmg": 70, "w_ratio": 85, "w_slow": (45, 30, 20),
    "w_linger": 60, "w_per": 15, "w_zone": 12000, "w_dps": 14, "w_dps_r": 12,
    # R's W: the laser (League: 0.6 s cast, 160-480 + 120% bonus AD + 75% AP, slow 99% decaying over 1 s)
    "rw_dur": 40, "rw_apply": 34, "rw_len": 120000, "rw_w": 9000, "rw_dmg": 160, "rw_ratio": 120, "rw_slow": (50, 30),
    # skill2: E (League: 1.5 s, 25-55% MS, x1.5 toward an enemy champion, ghosted, cd 9 s); R's E: a dash
    # (1200-2100 speed; about 350 units)
    "e_cd": 540, "e_range": 80000, "e_t": 90, "e_ms": 40, "e_ms2": 60, "e_close": 35000, "re_v": 2600, "re_t": 14,
    # ult: R (League: 15 s, cd 100/90/80 s)
    "r_cd": 4200, "r_range": 70000, "r_count": 75000, "r_t": 900, "r_anim": 30,     # r_anim: the ult strip, 500 ms
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # the add-on's copy (addons/league_yunara/make_override.py): 1 = R's dash direction left to league_yunara:faith
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
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


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


def magic(dmg, ratio, crit=False):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": crit}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(radius), "range_effect_name": "", "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1, apply=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, life, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": life, "period": period,
            "first_delay": period, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def beam(name, length, width, delay, apply, target, effects):
    return {"type": "LineRangeProjectile", "name": n(name), "length": length, "width": width, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def slows(name, parts):
    """A slow that decays: one buff per part, the k-th lasting 30 (k + 1) ticks."""
    return [buff(f"{name}{k}", 30 * (k + 1), move_speed_mult=-s) for k, s in enumerate(parts)]


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def lives(*effects):
    """A `Delayed` chain's effects only while she lives (a dead caster's Delayed effects run in the game): a 1-tick
    flag from a search that finds no dead caster; the copy in the search is what the AI reads (champion-data 5)."""
    return combine(pick(1, "AllyOnlySelf", flag("live", 1)),
                   sw("live", combine(*effects), pick(1, "AllyOnlySelf", *effects)), *rm("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ Q: on by itself at full Unleash, or by R
    def q_start(tick):
        return combine(refresh("q_on", tick, attack_speed_mult=p["q_as"]), sfx("q_on"), cview("q_burst"))

    us = ["u1", "u2", "u3"]
    full = combine(*rm(*us, "u_half"), q_start(p["q_t"]), voice("vo_q", p))
    climb = flag("u1", p["u_t"])
    for k in range(len(us) - 1):
        climb = sw(us[k], combine(*rm(us[k]), flag(us[k + 1], p["u_t"])), climb)
    climb = sw(us[-1], full, climb)
    half = sw("u_half", combine(*rm("u_half"), climb), flag("u_half", p["u_t"]))
    unleash = sw("q_on", NONE, combine(*rm("u_champ"), pick(1000, "EnemyChampion", flag("u_champ", 1), fp=True),
                                       sw("u_champ", climb, half), *rm("u_champ")))

    # ------------------------------------------------------------------ attack
    plain = homing("a_bead", p["bead_speed"], p["bead_y"], "Enemy",
                   [attack(0, p["a_ratio"]), magic(p["p_dmg"], p["p_ap"], crit=True), view("a_hit"), tsfx("a_hit")])
    spread = delayed(1, lob("q_aim", 1, 1000, "Enemy", [],
                            end=[zone("q_spread", p["q_sp_r"], "EnemyWithoutTower",
                                      [attack(0, p["q_sp"]), view("q_sp_hit")]),
                                 view("q_spread")]))
    strong = homing("q_bead", p["bead_speed"], p["bead_y"], "Enemy",
                    [attack(0, p["a_ratio"] - p["q_sp"]), magic(p["p_dmg"] + p["q_dmg"], p["p_ap"] * 2, crit=True),
                     view("q_hit"), tsfx("q_hit"), spread])
    twin = homing("a_twin", p["bead_speed"], p["bead_y"], "EnemyWithoutTower", [unleash])
    throw = combine(sw("q_on", combine(sfx("q_a"), strong), combine(sfx("a"), plain)), twin)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      throw, atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ W: the bead, or R's laser
    bead_hit = [attack(p["w_dmg"], p["w_ratio"]), *slows("w_slow", p["w_slow"]), view("w_hit"), tsfx("w_hit")]
    spin = field("w_spin", p["w_zone"], p["w_linger"], p["w_per"], "EnemyWithoutTower",
                 [attack(p["w_dps"], p["w_dps_r"]), view("w_tick")])
    w_line = line("w_bead", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyWithoutTower", True, bead_hit,
                  end=[spin, view("w_end"), sfx("w_end")])
    # the lob lands on the release tick: the aim is where the target stood w_lock ticks before
    w_bead = combine(sfx("w"), voice("vo_w", p),
                     lob("w_aim", p["w_lock"], 1000, "EnemyWithoutTower", [], end=[w_line, sfx("w_fly")]))
    laser = combine(anim("skill_r", p["rw_dur"]), sfx("rw"), voice("vo_rw", p), cview("rw_charge"),
                    beam("rw_beam", p["rw_len"], p["rw_w"], p["rw_apply"] + 4, p["rw_apply"], "EnemyWithoutTower",
                         [attack(p["rw_dmg"], p["rw_ratio"]), *slows("rw_slow", p["rw_slow"]), view("rw_hit"),
                          tsfx("rw_hit")]),
                    delayed(p["rw_apply"] - 1, sfx("rw_beam")))
    # both start on the action's first tick: the laser's strip (skill_r, a CasterAnimation) at once, the bead's lob
    # w_lock ticks before the release (a Delayed, guarded: a dead caster's Delayed effects run)
    skill = action("skill", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                   sw("r_on", laser, delayed(p["w_rel"] - p["w_lock"] - 1, lives(w_bead))))

    # ------------------------------------------------------------------ E: the speed, or R's dash
    def speed(pct):
        return combine(refresh("e_ms", p["e_t"], move_speed_mult=pct), cview("e_cast"), sfx("e"), voice("vo_e", p))

    near = combine(*rm("e_near"), around(p["atk_range"], "EnemyChampion", [flag("e_near", 1)]))
    plain_e = combine(near, sw("e_near", speed(p["e_ms"]), speed(p["e_ms2"])), *rm("e_near"))
    dash = combine(anim("skill2_r", p["re_t"] + 2), sfx("re"), voice("vo_e", p), cview("re_trail"),
                   {"type": "MoveBack", "speed": p["re_v"], "tick": p["re_t"]})
    close = combine(*rm("e_close"), around(p["e_close"], "EnemyChampion", [flag("e_close", 1)]))
    r_e = combine(close, sw("e_close", dash, speed(p["e_ms2"])), *rm("e_close"))
    skill2 = action("skill2", 12, p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion", sw("r_on", r_e, plain_e))

    # ------------------------------------------------------------------ R: only in a fight
    count = around(p["r_count"], "EnemyChampion", [sw("r_n1", flag("r_n2", 1), flag("r_n1", 1))])
    in_cc = pick(p["r_range"], "EnemyChampionInCC", flag("r_cc", 1))
    fire = combine(refresh("r_on", p["r_t"]), q_start(p["r_t"]), *rm(*us, "u_half"),
                   flag("r_cdr", 3, skill_cooldown_mult=400), anim("ult", p["r_anim"]), sfx("r"), voice("vo_r", p),
                   cview("r_burst"))
    refund = flag("r_refund", 3, ult_cooldown_mult=4900)
    # a 3-tick action (an empty try costs 3 ticks of the idle, league_kalista's gate); the fire plays the ult strip
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(*rm("r_n1", "r_n2", "r_cc"), count, in_cc, sw("r_n2", fire, sw("r_cc", fire, refund)),
                         *rm("r_n1", "r_n2", "r_cc")), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bead"), P_("q_bead"), P_("w_bead"), P_("rw_beam", BIG, 3)]
    views_e = [E("a_hit"), E("q_hit"), E("q_sp_hit"), E("q_spread", FX, -1, **LATE), E("q_burst", FX, 3),
               E("w_hit"), E("w_end", FX, -1, **LATE), E("w_tick", FX, 2, **LATE), E("rw_charge", FX, 3),
               E("rw_hit"), E("e_cast", FX, -1), E("re_trail", FX, -1), E("r_burst", BIG, 3)]
    views_b = [B_("q_on", FX, 3), B_("r_on", BIG, -1), B_("e_ms", FX, -1), B_("w_slow0", FX, -1),
               B_("rw_slow0", FX, -1)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": p["crit"]},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
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
    ap_.add_argument("--set", nargs="*", default=[])
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
        p[k] = json.loads(v) if isinstance(p[k], (list, tuple)) else (type(p[k])(float(v)) if isinstance(p[k], int)
                                                                      else float(v))
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
