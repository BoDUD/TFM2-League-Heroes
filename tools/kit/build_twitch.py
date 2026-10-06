"""Build league_twitch.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_twitch.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-07, all the recommended options: Q / W -> E combo / venom stacks on the enemies /
Evelynn's camouflage broken by his first shot / piercing bolts in R, armed until two champions stand in reach;
plus the pro combos):
  passive Deadly Venom (死亡毒液): every bolt (and the cask, its puddle and R's bolts) hangs one stack of venom on the
          unit it hits (towers excepted): an `AddCasted Poison` of v_t ticks (the game's poison icon) dealing v_dmg +
          v_ratio% AD true damage every v_period. Each stack is its own instance and nothing caps the count (League's
          6): fast attacks can put more on. Next to it a second instance per stack (period 2) waits for the caster flag
          `e_pop` (3 ticks: league_ryze's window, each mark bursts once): Contaminate bursts every stack once,
          so every enemy takes damage for its own stack count
          (league_ryze's Flux marks). His champion hits also climb a ladder h1..h6 on him (v_t ticks, refreshed by
          each one) - nothing reads a target's count, so the ladder only decides when the combos throw E.
  attack  A crossbow bolt (homing, physical 100% AD); a twin on `EnemyWithoutTower` carries the venom, and through a
          champion picked at its hit (`RandomTarget` 1000 from the projectile) the ladder and league_jinx's kill check.
          While R runs the bolt is a piercing line instead (below); a tower still gets the plain bolt (a tick-1 probe on
          `EnemyWithoutTower` decides).
  skill   Q Ambush (埋伏): a `Targeting` cast on `EnemyChampion` within q_range (farther than his attack): q_on for
          q_t ticks and an `AddCasted` poll on him that renews `CasterInvisible` and q_ms% move speed every q_poll
          ticks while q_on holds (league_evelynn's camouflage). His next attack, skill or ult takes q_on off - the
          camouflage lapses within a poll - and gives q_as% attack speed for q_as_t (also when q_t runs out). A takedown
          of an enemy champion (the kill checks on his bolts and on Contaminate) resets Q: a 2-tick skill_cooldown_mult,
          the ult keeping its cap (league_khazix).
  skill2  W Venom Cask (剧毒之桶) -> E Contaminate (毒性爆发): a `Targeting` cast on `EnemyWithoutTower` (w_range). The slot's
          cooldown is W's; every throw also lays the caster flag w_cd, so the combos throw it only when it is ready and a
          slot cast while a combo's cask is still cooling down is E alone (or nothing). The cask is a lob onto where the target stood (w_travel
          ticks, dodgeable): one stack and a w_slow% slow round it (w_r), then a puddle w_pool ticks that slows whoever
          stands in it (renewed every 15 ticks for 15, so it never adds up) and adds a stack every 60. e_wait ticks
          after the landing, with E's own flag e_cd off, E follows (the cask and its puddle add stacks): its pose, e_pop, the
          ladder cleared.
  ult     R Spray and Pray (火力全开): a 3-tick `Targeting` cast on `EnemyChampion` (r_slot). Armed like league_samira R:
          with two enemy champions within r_reach it fires at once, else it arms r_armed for r_arm ticks - each of his
          attacks counts again and fires it, and after r_hold ticks one champion in his attack's reach is enough - and refunds the cooldown (ult_cooldown_mult 4900) when it lapses unused.
          Fire: r_on for r_t ticks (+r_bonus attack range, +r_ad attack); his bolts fly as piercing lines (r_len,
          r_speed) on `EnemyWithoutTower`: the first unit full damage, each one after it r_fall% less, down to r_min%.
  combos  (「加入高手的连招」): Q -> W: the shot out of the camouflage throws the cask at its target when w_cd is off;
          R -> W -> bolts: R fired from the slot throws the cask first when it is ready; R's end -> E: e_lead ticks
          before R ends, with e_cd off and the ladder at h<e_need>, Contaminate cashes the stacks in.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_twitch.data_champion")
ID = "league_twitch"
FX = "asset/league/effects/league_twitch_fx"
BIG = "asset/league/effects/league_twitch_big"

# Numbers = candidate c10 of the 10-min classic-SDK simulations (tw_sim/sim/kd.py --lane 3 against gunner, soldier, archer
# and gambler, three lineups, both sides, 2026-10-07): +1.59 on seeds 1-24 and +1.59 on 25-48 (league_samira +1.36 /
# +1.19, league_varus +1.63 / +1.91 on the same seeds). The draft c3 was +3.41: cutting E (12 + 28% -> 8 + 20% a stack)
# and the venom (2 -> 1 + 2%) changed nothing (+3.40); attack 98 -> 94, Q's attack speed 45 -> 35% and R's +25 -> +15
# attack with E at 6 + 16%: +2.33; the cask's slow is the big lever (35 -> 20% and a 2 s puddle: +0.08), 30% here.
# Q's stealth 2.5 s (+1.66) or attack 88 / hp 850 (+1.61) did as much; League's 5 s stealth kept. Retimed to the strips
# (the bolt on tick 7, W's throw 21 ticks, E's burst on tick 10 of 25): +1.62 / +1.35. The bolts fly at the pivot's
# height (bolt_y 0): the crossbow's tip in the attack's release frame is 19 px in front, 11 up = the pivot's row.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Twitch: 550 range,
    # 59 AD, 630 +98 hp, 27 armour, 330 move, attack speed 0.679
    "hp": 900, "hp_g": 88, "atk": 94, "atk_g": 19, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    # attack: the bolt leaves the crossbow on a_st
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 54, "a_st": 7, "bolt_speed": 7500, "bolt_y": 0, "a_read": 2,
    # passive: Deadly Venom (League: 6 stacks, 6 s, 1-5? true damage a stack a second by level + 3% AP)
    "v_t": 360, "v_period": 60, "v_dmg": 1, "v_ratio": 2, "h_n": 6,
    # skill: Q Ambush (League: camouflage 10-14 s after a 1 s fade, +10% move speed (+30% hidden near enemies),
    # +40-60% attack speed 6 s on leaving it, cd 16 s, reset when a poisoned champion dies)
    "q_cd": 900, "q_range": 90000, "q_anim": 18, "q_t": 300, "q_poll": 6, "q_ms": 20, "q_as": 35, "q_as_t": 360,
    "k_hold": 40, "k_read": 4, "reset_mult": 10000,
    # skill2: W Venom Cask (League: 950 range, radius 300, slow 30-50% 3 s, puddle 3 s, cd 13-9 s)
    "w_cd": 660, "w_range": 90000, "w_dur": 21, "w_rel": 9, "w_travel": 14, "w_r": 28000,
    "w_slow": 30, "w_slow_t": 60, "w_pool": 180,
    # -> E Contaminate (League: 10-70 + 15-35 a stack + 35% bonus AD a stack, cd 12-8 s)
    "e_cd": 600, "e_wait": 45, "e_need": 3, "e_anim": 25, "e_rel": 10, "e_dmg": 6, "e_ratio": 16, "e_reach": 120000,
    # ult: R Spray and Pray (League: 6 s, +300 range, +15-? AD, pierce -10% a unit down to 60%, cd 90 s)
    "r_cd": 3600, "r_slot": 70000, "r_reach": 85000, "r_arm": 600, "r_hold": 180, "r_anim": 18, "r_t": 360, "r_bonus": 30000,
    "r_ad": 15, "r_len": 115000, "r_speed": 10000, "r_rad": 6000, "r_fall": 10, "r_min": 60, "e_lead": 30,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def true_dmg(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(radius), "range_effect_name": "", "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    hs = [f"h{k}" for k in range(1, p["h_n"] + 1)]

    # ------------------------------------------------------------------ takedowns: league_jinx's kill check -> Q reset
    reset = combine(refresh("q_reset", 2, skill_cooldown_mult=p["reset_mult"], ult_cooldown_mult=-p["reset_mult"]),
                    cview("q_reset"), sfx("q_reset"))

    def kill_check(src):
        """On a hit enemy champion, around its damage: the flag before, the living target's clear after, the read on
        him later. Each source keeps its own flag (league_tristana W)."""
        k = f"k_{src}"
        return (refresh(k, p["k_hold"]),
                combine(casted(3, 1, *rm(k)), on_me(delayed(p["k_read"], sw(k, combine(*rm(k), reset))))))

    # ------------------------------------------------------------------ passive: Deadly Venom
    # one flag at a time, read from the top: h6 renews itself, h<k> steps up to h<k+1>, none starts h1
    climb = flag(hs[0], p["v_t"])
    for k in range(len(hs) - 1):
        climb = sw(hs[k], combine(*rm(hs[k]), flag(hs[k + 1], p["v_t"])), climb)
    climb = sw(hs[-1], refresh(hs[-1], p["v_t"]), climb)
    burst = combine(attack(p["e_dmg"], p["e_ratio"]), view("v_pop"))
    venom = [casted(p["v_t"], p["v_period"], true_dmg(p["v_dmg"], p["v_ratio"]), kind="Poison"),
             casted(p["v_t"], 2, sw("e_pop", burst), kind="Poison")]

    def champ_hit(src):
        """A champion's share of a hit: the kill check around nothing (the damage lands beside it) and the ladder."""
        k_set, k_read = kill_check(src)
        return pick(1000, "EnemyChampion", k_set, climb, k_read, fp=True)

    # ------------------------------------------------------------------ skill2's E (also thrown by the combos)
    k_e = "k_e"
    e_kill = around(p["e_reach"], "EnemyChampion", [refresh(k_e, p["k_hold"]), delayed(3, casted(3, 1, *rm(k_e)))])
    e_fire = combine(refresh("e_cd", p["e_cd"]), *rm(*hs), anim("skill2_e", p["e_anim"]), sfx("e_cast"),
                     voice("vo_e", p),
                     delayed(p["e_rel"], cview("e_cast"), sfx("e_pop"), e_kill, refresh("e_pop", 3),
                             on_me(delayed(p["k_read"] + 3, sw(k_e, combine(*rm(k_e), reset))))))
    e_ready = sw("e_cd", NONE, e_fire)
    e_try = sw("e_cd", NONE, sw(hs[p["e_need"] - 1], e_fire))

    # ------------------------------------------------------------------ W Venom Cask
    slow_hit = buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"])
    pool = [field("w_pool", p["w_r"], p["w_pool"], 15, "EnemyWithoutTower",
                  [buff("w_slow", 16, move_speed_mult=-p["w_slow"])]),
            field("w_pool_v", p["w_r"], p["w_pool"], 60, "EnemyWithoutTower", [*venom, champ_hit("w")])]
    cask = lob("w_cask", p["w_travel"], p["w_r"], "EnemyWithoutTower",
               [*venom, slow_hit, view("w_hit"), champ_hit("w")], end=pool)

    def throw(follow_e):
        out = [refresh("w_cd", p["w_cd"]), anim("skill2", p["w_dur"]), sfx("w_cast"), voice("vo_w", p),
               delayed(p["w_rel"], sfx("w_throw"), cask, delayed(p["w_travel"], sfx("w_land")))]
        if follow_e:     # after the slot's cask E follows whenever it is ready: the cask and its puddle add stacks
            out.append(delayed(p["w_rel"] + p["w_travel"] + p["e_wait"], e_ready))
        return combine(*out)

    # ------------------------------------------------------------------ Q Ambush
    as_bonus = combine(refresh("q_as", p["q_as_t"], attack_speed_mult=p["q_as"]), cview("q_out"), sfx("q_out"))
    reveal = sw("q_on", combine(*rm("q_on"), as_bonus))
    poll = sw("q_on", combine({"type": "CasterInvisible", "tick": p["q_poll"] + 2},
                              refresh("q_ms", p["q_poll"] + 2, move_speed_mult=p["q_ms"])))
    skill = action("skill", p["q_anim"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyChampion",
                   combine(refresh("q_on", p["q_t"]), anim("skill", p["q_anim"]), cview("q_cast"), sfx("q_cast"),
                           voice("vo_q", p),
                           on_me(casted(p["q_t"], p["q_poll"], poll),
                                 delayed(p["q_t"], reveal))))

    # ------------------------------------------------------------------ R Spray and Pray
    def count():
        """2-tick flags u1 -> u2: two enemy champions within r_reach."""
        return combine(*rm("u1", "u2"),
                       around(p["r_reach"], "EnemyChampion", [sw("u1", refresh("u2", 2), refresh("u1", 2))]))

    def fire(slot):
        out = [*rm("r_armed"), refresh("r_on", p["r_t"], range=p["r_bonus"], attack=p["r_ad"]), sfx("r_cast"),
               voice("vo_r", p), on_me(delayed(p["r_t"] - p["e_lead"], sw("r_on", e_try)))]
        if slot:     # the cast pose, then the cask when it is ready (R -> W -> bolts)
            out += [anim("ult", p["r_anim"]), cview("r_cast"),
                    sw("w_cd", NONE, delayed(p["r_anim"], pick(p["r_reach"], "EnemyChampion", throw(False))))]
        else:
            out.append(cview("r_cast"))
        return combine(*out)

    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(reveal, count(), sw("u2", fire(True), arm)))

    # ------------------------------------------------------------------ attack: the bolt, or R's piercing bolt
    ka_set, ka_read = kill_check("a")
    bolt = combine(sfx("a_shot"),
                   homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy", [attack(0, 100), view("a_hit"),
                                                                           tsfx("a_hit")]),
                   homing("a_twin", p["bolt_speed"], p["bolt_y"], "EnemyWithoutTower",
                          [*venom, pick(1000, "EnemyChampion", ka_set, climb, ka_read, fp=True)]))
    falls = [f"f{k}" for k in range(1, (100 - p["r_min"]) // p["r_fall"] + 1)]
    kr_set, kr_read = kill_check("r")

    def r_ladder():
        """The damage of a piercing bolt's n-th unit: flags f1.. (one at a time) count the units this bolt has hit;
        none -> full damage and f1, f<k> -> 100 - k x r_fall% and f<k+1>, the last -> the floor r_min%."""
        out = combine(attack(0, 100), flag(falls[0], 30))
        for k in range(len(falls)):
            pct = max(p["r_min"], 100 - p["r_fall"] * (k + 1))
            step = combine(*rm(falls[k]), flag(falls[k + 1], 30)) if k + 1 < len(falls) else NONE
            out = sw(falls[k], combine(attack(0, pct), step), out)
        return out

    spray = combine(sfx("r_shot"), *rm(*falls),
                    line("r_bolt", p["r_speed"], p["r_len"], p["r_rad"], p["bolt_y"], "EnemyWithoutTower", True,
                         [r_ladder(), *venom, view("r_hit"), tsfx("r_hit"),
                          pick(1000, "EnemyChampion", kr_set, climb, kr_read, fp=True)]))
    probe = homing("a_probe", 100000, 0, "EnemyWithoutTower", [on_me(flag("a_unit", p["a_st"] + 2))])
    shoot = sw("r_on", combine(*rm("a_unit"), probe, delayed(p["a_st"], sw("a_unit", spray, bolt))),
               delayed(p["a_st"], bolt))
    # Q -> W: the shot out of the camouflage throws the cask at its target
    out_of_hiding = sw("q_on", combine(*rm("q_on"), as_bonus,
                                       sw("w_cd", NONE, delayed(p["atk_dur"], throw(False)))))
    # armed: two champions in reach fire it, or one in his attack's reach once r_hold ticks have passed
    solo = combine(*rm("r_solo"), pick(p["atk_range"] + 5000, "EnemyChampion", flag("r_solo", 2)),
                   sw("r_solo", fire(False)))
    go = sw("r_armed", combine(count(), sw("u2", fire(False), sw("r_wait", NONE, solo))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(out_of_hiding, go, shoot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill2: W -> E
    # the slot's own cooldown is W's; a combo's throw lays w_cd too, and a slot cast inside it is E alone (or nothing)
    skill2 = action("skill2", p["w_rel"] + 1, p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                    combine(reveal, sw("w_cd", e_try, throw(True))))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring); the bolts
    # and the cask are drawn top-bottom symmetric, the buffs left-right symmetric
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bolt"), P_("r_bolt"), P_("w_cask", FX, 2), P_("w_pool", BIG, -1)]
    views_e = [E("a_hit"), E("v_pop", BIG), E("w_hit"), E("q_cast", FX, 3), E("q_out", FX, 3, **LATE),
               E("q_reset", FX, 3, **LATE), E("e_cast", BIG, -1, **LATE), E("r_cast", BIG, 3, **LATE), E("r_hit")]
    views_b = [B_("w_slow", FX, -1), B_("q_as", FX, 3), B_("r_on", BIG, 2)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Dot"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
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
