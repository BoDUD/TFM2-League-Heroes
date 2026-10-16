"""Build league_kalista.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_kalista.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-15: all the recommended options - W's Sentinel left out, Soul-Marked folded into the
attack; the hop in the main pack only backward, the add-on choosing forward or back
(「这个得做啊 附加包 往前还是往后灵活判断啊」); pro combos on):
  spears  Rend's stacks (撕裂之矛): every spear she lands (attack, Q) hangs instances on the unit it hits (towers
          excepted): a watcher (period 2, sp_t ticks) that bursts once when the caster flag e_pop rises (league_twitch's
          venom, league_ryze's Flux window) and a picture of the spear stuck in it (period sp_pic). Nothing removes an
          `AddCasted`, so the spears belong to a generation (caster flags g_a / g_b / none): a spear bursts only while
          its generation is the current one, and every Rend moves the generation on - the spears it ripped out never
          burst again (three generations: one would need three Rends within sp_t to come back). Her champion hits also
          climb a ladder h1..h<e_need> on her (sp_t ticks, refreshed by each one; e_ok at e_need, e_ok2 from 2): nothing
          reads a target's count, so the ladder decides when Rend is worth casting.
  attack  A spear thrown at the target (homing, physical a_ratio% AD: League's 90%), released on tick a_st; a twin on
          `EnemyWithoutTower` hangs the spear and, through a champion picked at its hit (`RandomTarget` 1000 from the
          projectile), the ladder, league_jinx's kill check and W.
  W       Soul-Marked (灵魂绑定, passive): her spear on an enemy champion that another allied champion stands within w_r
          of (fighting it with her) also deals w_hp% of its maximum health as true damage; w_cd ticks between procs
          (a caster flag: League's 6 s is per target).
  passive Martial Poise (武术姿态): after every spear (attack or Q), as in League, she hops straight away from her target
          (MoveBack hop_v x hop_t) - the pros' kiting (the user, 10-16: 「平A 前进后退的动作没了吗？这符合LOL的设定吗？」
          「前跳后跳」 - it hopped only with an enemy champion within hop_thr). The data cannot hop forward a set distance
          (MoveTo in a Targeting cast runs onto the target), so a forward hop is the add-on's.
  skill   Q Pierce (穿刺): a `Targeting` cast on `EnemyWithoutTower` (q_range); at q_rel a spear flies straight at where
          the target stands then (dodged by walking off the line), stops on the first unit it hits: q_dmg + q_ratio% AD
          and a spear in it. If that unit dies, the spear goes on along the line to the next (an unseen twin carries
          the damage). The hop follows as after an attack.
  skill2  E Rend (撕裂): the spear (attack or Q) that brings her ladder to e_need rips at once (from level 3), and a
          3-tick `Targeting` slot on `EnemyChampionRecentlyAttacked` (e_range) tried every e_try ticks rips with e_ok
          (her ladder at e_need or more) and the caster flag e_cd off: her pose, e_pop for 3 ticks
          (each live spear bursts once: e_dmg + e_ratio% AD and an e_slow% slow per spear for e_slow_t ticks), the
          generation moves on, the ladder clears; e_cd ticks. A champion it kills refunds it (league_jinx's kill
          check round every champion within e_reach): League's reset on a kill.
  ult     R Fate's Call (命运的召唤): a `Targeting` cast on `EnemyChampion` (r_range) when an allied champion stands
          within r_bind of her (else the cooldown is refunded: ult_cooldown_mult 4900). That ally (League's
          Oathsworn: a random one in reach - data keeps no bond) is grabbed to her (r_grab_v, again every 8 ticks) and held r_hold ticks,
          unseen by enemies and taking r_safe% less damage, stunned from 2 ticks before the launch (a stun on the grab's
          tick held it where it stood); then she hurls it at the target: a launch zone on the
          target's spot pulls every allied champion in CC (the held one) toward it (Pull r_v x r_fly); a catch zone
          there (r_catch) stops the first one in CC that reaches it and knocks up every enemy round it (r_kr): r_up
          ticks airborne and r_dmg + r_ratio% AD. Combo R -> E: with e_ok2 and E ready, Rend follows the landing.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_kalista.data_champion")
ID = "league_kalista"
FX = "asset/league/effects/league_kalista_fx"
BIG = "asset/league/effects/league_kalista_big"

# Numbers: the 10-min classic-SDK simulations (kl_sim/sim/kd.py --lane 3 against gunner, soldier, archer and gambler,
# three lineups, both sides, 8 seeds each, 2026-10-15/16): the League-ratio draft d0 -1.83; Rend from the attack at e_need
# and the slot tried every e_try 90 ticks -0.41..-0.92; e_need 3, Rend 15 + 40% a spear, Q 80 -> +0.03; hp 950 and W 10%
# -> +0.97; attack 104 +1.09, Q 7 s +1.17. Timed to the strips (attack and Q released on their third frame, Rend's yank
# on E's second, the hop 12 ticks, R's call 24 and throw 18) she fell to -0.41; 16 seeds from here: attack every 46
# ticks +0.95, every 44 +0.79; Q 100 and W 12% +1.19, with Q 110 +0.92, with hp 1000 +1.42 (here; Varus +1.63, Twitch
# +1.59).
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Kalista: 525 range,
    # 59 AD, 560 +114 hp, 24 armour, 330 move, attack speed 0.694, basic attacks 90% AD
    "hp": 1000, "hp_g": 88, "atk": 104, "atk_g": 20, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    # attack: the spear leaves her hand on a_st
    "atk_range": 52500, "atk_dur": 24, "atk_cd": 46, "a_st": 7, "a_ratio": 90, "spear_speed": 8000, "spear_y": -3000,
    # spears and the ladder
    "sp_t": 240, "sp_pic": 12, "e_need": 3,
    # W Soul-Marked (League: 14% max health magic, 6 s per target, needs the Oathsworn's hit too)
    "w_r": 45000, "w_hp": 12, "w_cd": 300,
    # passive Martial Poise (League: a hop of ~300 units after each attack)
    "hop_thr": 40000, "hop_v": 1800, "hop_t": 10, "k_hold": 40, "k_read": 4,
    # the hop waits hop_wait ticks after the release: the throw's release frame (90 ms) shows first (the user, 10-16 in
    # game: 「平A动作还是不对啊 不用武器啊」 - the hop's frames replaced the throw right on the release)
    "hop_wait": 5,
    # skill: Q Pierce (League: 1150 range, 20-120 + 105% AD, 0.25 s cast, width 80, passes through a unit it kills,
    # cd 8 s)
    "q_cd": 420, "q_range": 100000, "q_dur": 24, "q_rel": 7, "q_speed": 9000, "q_len": 115000,
    "q_rad": 5000, "q_y": -3000, "q_dmg": 100, "q_ratio": 105,
    # skill2: E Rend (League: 1100 range; 5-85 + 70% AD the first spear, 8-24 + 23-36% AD each more, slow 10-50% 2 s,
    # cd 14-6 s, reset on a kill)
    "e_cd": 600, "e_try": 90, "e_range": 100000, "e_reach": 110000, "e_anim": 23, "e_rel": 4,
    "e_dmg": 15, "e_ratio": 40, "e_slow": 8, "e_slow_t": 120,
    # ult: R Fate's Call (League: 1100 range, the Oathsworn drawn in up to 4 s, launched to knock up 1-1.5 s, cd 150 s)
    "r_cd": 4800, "r_range": 90000, "r_bind": 70000, "r_anim": 24, "r_throw": 18, "r_hold": 30, "r_grab_v": 4000, "r_safe": 90,
    "r_v": 3000, "r_fly": 40, "r_catch": 14000, "r_kr": 26000, "r_up": 75, "r_dmg": 80, "r_ratio": 60,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # the add-on's copy (addons/league_kalista/make_override.py): 1 = the hop and R's flight left to league_kalista:oath
    "native": 0, "r_fly_v": 4500, "r_poll": 44,
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


def hp_true(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


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


def catch(name, radius, tick, target, effects):
    return {"type": "ApplyInProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "follow_caster": False,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


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
    hs = [f"h{k}" for k in range(1, p["e_need"] + 1)]

    # ------------------------------------------------------------------ kill checks (league_jinx)
    def kill_check(src, reward):
        """On a hit enemy champion: the flag before, the living target's clear after, the read on her later."""
        k = f"k_{src}"
        return (refresh(k, p["k_hold"]),
                combine(casted(3, 1, *rm(k)), on_me(delayed(p["k_read"], sw(k, combine(*rm(k), reward))))))

    # ------------------------------------------------------------------ the ladder (her spears on champions)
    def step_to(k):
        out = [flag(hs[k], p["sp_t"])]
        if k + 1 >= 2:
            out.append(refresh("e_ok2", p["sp_t"]))
        if k + 1 >= p["e_need"]:
            out.append(refresh("e_ok", p["sp_t"]))
        return combine(*out)

    climb = step_to(0)
    for k in range(len(hs) - 1):
        climb = sw(hs[k], combine(*rm(hs[k]), step_to(k + 1)), climb)
    climb = sw(hs[-1], combine(*rm(hs[-1]), step_to(len(hs) - 1)), climb)

    # ------------------------------------------------------------------ spears: three generations
    burst = combine(attack(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                    view("e_rip"))

    def gen(live, watch):
        """Gate an effect on the generation: g_a, g_b, or neither."""
        if live == "a":
            return sw("g_a", watch)
        if live == "b":
            return sw("g_b", watch)
        return sw("g_a", NONE, sw("g_b", NONE, watch))

    def stuck(g):
        return [casted(p["sp_t"], 2, gen(g, sw("e_pop", burst)), kind="Bleed"),
                casted(p["sp_t"], p["sp_pic"], gen(g, sw("e_pop", NONE, view("sp_mark"))))]

    spear = sw("g_a", combine(*stuck("a")), sw("g_b", combine(*stuck("b")), combine(*stuck("c"))))
    rotate = sw("g_a", combine(*rm("g_a"), flag("g_b", None)),
                sw("g_b", combine(*rm("g_b")), flag("g_a", None)))

    # ------------------------------------------------------------------ E Rend
    reset_e = combine(*rm("e_cd"), cview("e_reset"), sfx("e_reset"))
    e_kill = around(p["e_reach"], "EnemyChampion", [refresh("k_e", p["k_hold"]), delayed(3, casted(3, 1, *rm("k_e")))])
    e_fire = combine(refresh("e_cd", p["e_cd"]), *rm(*hs, "e_ok", "e_ok2"), anim("skill2", p["e_anim"]), sfx("e"),
                     voice("vo_e", p),
                     on_me(delayed(p["e_rel"], cview("e_cast"), e_kill, refresh("e_pop", 3),
                                   delayed(3, *rm("e_pop"), rotate),
                                   delayed(p["k_read"] + 3, sw("k_e", combine(*rm("k_e"), reset_e))))))
    # an empty try plays 3 ticks of the idle, not a twitch of the cast (e_fire plays skill2 itself)
    skill2 = action("idle", 3, p["e_try"], 1, p["e_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                    sw("e_cd", NONE, sw("e_ok", e_fire)), key="skill2")

    # ------------------------------------------------------------------ W Soul-Marked and the champion's share of a hit
    soul = combine(*rm("w_near"), pick(p["w_r"], "AllyNotSelf", flag("w_near", 1), fp=True),
                   sw("w_near", sw("w_cd", NONE, combine(refresh("w_cd", p["w_cd"]), hp_true(p["w_hp"]), view("w_hit"),
                                                         tsfx("w_hit")))),
                   *rm("w_near"))

    # the spear that brings the ladder to e_need rips at once (from level 3, skill2's level), E ready
    rip_now = {"type": "SwitchByLevel3", "effect_start": NONE, "effect_level3": sw("e_cd", NONE, sw("e_ok", e_fire))}

    def champ_hit(src):
        k_set, k_read = kill_check(src, NONE)
        return pick(1000, "EnemyChampion", k_set, climb, soul, k_read, rip_now, fp=True)

    # ------------------------------------------------------------------ passive: the hop
    hop = combine(anim("hop_b", p["hop_t"] + 2), sfx("hop"), {"type": "MoveBack", "speed": p["hop_v"], "tick": p["hop_t"]})
    if p["native"]:
        # the add-on decides the way every tick (hop_f / hop_b on her) and moves her once hop_go is up
        # (no enemy champion near - minions, monsters: neither flag - the main pack's hop back from the target)
        hop = combine(sw("hop_f", combine(refresh("hop_go", 6), anim("hop_f", p["hop_t"] + 2), sfx("hop")),
                         sw("hop_b", combine(refresh("hop_go", 6), anim("hop_b", p["hop_t"] + 2), sfx("hop")), hop)))
    hop = delayed(p["hop_wait"], lives(hop))

    # ------------------------------------------------------------------ attack
    throw = combine(sfx("a_throw"),
                    homing("a_spear", p["spear_speed"], p["spear_y"], "Enemy",
                           [attack(0, p["a_ratio"]), view("a_hit"), tsfx("a_hit")]),
                    homing("a_twin", p["spear_speed"], p["spear_y"], "EnemyWithoutTower", [spear, champ_hit("a")]),
                    hop)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      throw, atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q Pierce
    # the spear seen stops on the first unit; an unseen twin flies the whole line and hurts a unit only while q_stop is
    # off: the first hit raises it, and it drops again 2 ticks later when that unit died (league_jinx's kill check:
    # q_k stays when no living target cleared it) - a second spear spawned where the first stopped flew from her
    # again and ended on the dead unit's spot (end_effects aim at the stop point)
    q_seen = line("q_spear", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower", False, [])
    q_hit = combine(refresh("q_stop", 40), refresh("q_k", 6), casted(3, 1, *rm("q_k")),
                    attack(p["q_dmg"], p["q_ratio"]), spear, view("q_hit"), tsfx("q_hit"), champ_hit("q"),
                    on_me(delayed(2, sw("q_k", combine(*rm("q_k", "q_stop"))))))
    q_line = line("q_pierce", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True,
                  [sw("q_stop", NONE, q_hit)])
    # released by start_timing (no Delayed: nothing to guard when she dies in the wind-up; attack speed shortens it)
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_rel"], p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(*rm("q_stop"), sfx("q"), voice("vo_q", p), q_seen, q_line, hop))

    # ------------------------------------------------------------------ R Fate's Call
    held = p["r_hold"] + p["r_fly"] + 4
    # the grab first (a stun on the same tick held the ally where it stood), the stun just before the launch: the launch
    # zone moves allied champions in CC only
    regrab = [delayed(k, {"type": "Grab", "speed": p["r_grab_v"]}) for k in range(8, p["r_hold"] - 2, 8)]
    take = [flag("r_got", 2), {"type": "Grab", "speed": p["r_grab_v"]}, *regrab,
            delayed(p["r_hold"] - 2, {"type": "Stun", "duration": p["r_fly"] + 6}), {"type": "Invisible", "tick": held},
            buff("r_safe", held, damaged_reduce=p["r_safe"]), view("r_take"), tsfx("r_take")]
    knock = zone("r_knock", p["r_kr"], "EnemyWithoutTower",
                 [{"type": "Airborne", "duration": p["r_up"]}, attack(p["r_dmg"], p["r_ratio"]), view("r_up")])
    land = [sw("r_fly", combine(*rm("r_fly"), {"type": "Airborne", "duration": 2},
                                lob("r_mark", 1, 1000, "AllyChampion", [], end=[knock, view("r_land")]),
                                tsfx("r_hit"),
                                on_me(delayed(p["r_up"] // 2, sw("e_cd", NONE, sw("e_ok2", e_fire))))))]
    launch = lob("r_aim", 1, 1000, "EnemyChampion", [],
                 end=[zone("r_launch", 400000, "AllyChampionInCC",
                           [{"type": "Pull", "speed": p["r_v"], "tick": p["r_fly"]}, view("r_fly")]),
                      catch("r_catch", p["r_catch"], p["r_fly"] + 4, "AllyChampionInCC", land)])
    fire = combine(anim("ult", p["r_anim"]), sfx("r"), voice("vo_r", p),
                   delayed(p["r_hold"], lives(refresh("r_fly", p["r_fly"] + 6), anim("ult2", p["r_throw"]), sfx("r_fly"),
                                              voice("vo_r_fly", p), launch)))
    refund = flag("r_refund", 3, ult_cooldown_mult=4900)
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(*rm("r_got"), pick(p["r_bind"], "AllyNotSelf", *take), sw("r_got", fire, refund)), key="ult")
    if p["native"]:
        # the copy: R cast on the Oathsworn (the add-on's AI hook picks him) when an enemy champion is in reach; the
        # take on him is the action's target; at the launch r_launch tells the add-on, which flies him to an enemy
        # champion and raises r_landed there: the knock-up round him (a 1-tick lob onto the action's target)
        land_n = combine(*rm("r_landed"), lob("r_mark", 1, 1000, "AllyChampion", [], end=[knock, view("r_land")]),
                         tsfx("r_hit"))
        polls = [delayed(p["r_hold"] + k, sw("r_landed", land_n)) for k in range(3, p["r_poll"] + 1, 3)]
        polls.append(on_me(delayed(p["r_hold"] + p["r_poll"] // 2, sw("e_cd", NONE, sw("e_ok2", e_fire)))))
        take_n = [{"type": "Grab", "speed": p["r_grab_v"]}, *regrab,
                  delayed(p["r_hold"] - 2, {"type": "Stun", "duration": p["r_poll"] + 4}),
                  {"type": "Invisible", "tick": p["r_hold"] + p["r_poll"]},
                  buff("r_safe", p["r_hold"] + p["r_poll"], damaged_reduce=p["r_safe"]), view("r_take"), tsfx("r_take")]
        fire_n = combine(*take_n, anim("ult", p["r_anim"]), sfx("r"), voice("vo_r", p),
                         delayed(p["r_hold"], lives(refresh("r_launch", 6), anim("ult2", p["r_throw"]), sfx("r_fly"),
                                                    voice("vo_r_fly", p))), *polls)
        ult = action("idle", 3, p["r_cd"], 1, p["r_bind"], "Targeting", "AllyNotSelf",
                     combine(*rm("r_foe"), pick(p["r_range"], "EnemyChampion", flag("r_foe", 2)),
                             sw("r_foe", fire_n, refund), *rm("r_foe")), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_spear"), P_("q_spear")]
    views_e = [E("a_hit"), E("sp_mark"), E("e_rip"), E("e_cast", BIG, -1, **LATE), E("e_reset", FX, 3, **LATE),
               E("w_hit"), E("q_hit"), E("r_take", BIG, 3), E("r_fly", BIG, 3), E("r_land", BIG, -1, **LATE),
               E("r_up")]
    views_b = [B_("e_slow", FX, -1), B_("r_safe", BIG, 3)]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": f"{ID}:oath",
                            "params": {k: p[k] for k in ("hop_thr", "hop_v", "hop_t", "atk_range", "r_bind", "r_range",
                                                         "r_fly_v", "r_catch", "sp_t", "e_dmg", "e_ratio")}}
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range"], **extra,
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
