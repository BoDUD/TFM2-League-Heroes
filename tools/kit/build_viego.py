"""Build league_viego.data_champion (jungle, Melee) from the parameters P.

    python tools/kit/build_viego.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-10: jungle, Melee; Q alone, W with E's mist folded in, the pros' E -> W -> Q -> double
strike -> R; the possession approximated in data and done for real by the add-on addons/league_viego_soul; R the
Darius way on a champion his team has been hitting).
TFM2 has three active slots: Blade of the Ruined King is `skill`, Spectral Maw (opened by Harrowed Path's mist) `skill2`,
Heartbreaker the `ult`; Sovereign's Domination runs on its own.
  passive Sovereign's Domination (君命已决): an enemy champion he damaged dies within p_win ticks -> he takes its soul:
          p_inv ticks untouchable (no damage, no crowd control), heals p_heal + p_heal_ratio% AD, and for p_t ticks is
          possessed: the soul's mist round him, p_ad% attack, p_as% attack speed and p_ms% move speed borrowed, Q and W
          ready again (and the ult's cooldown cut to (100 - p_ult share)). Casting Heartbreaker ends it.
          How the data sees a takedown (champion-data section 7, "Kill trigger", stretched to a window): each champion
          hit puts an `AddCasted` (p_win ticks, every tick) on the champion that keeps a 2-tick caster flag p_alive
          up while it lives, and one on him that watches the flag for p_win - 2 ticks; the flag lapsing inside the
          window = the champion died (the latest hit's champion casted always outlives the watchers, so a window
          running out is never read as a death). Two champions hit in the same window: only the last one to die
          is seen (the other keeps the flag up) - the add-on reads deaths natively and sees each one.
  attack  The sword, the hit on tick atk_st; champions also take a_pct% of their maximum health (League: % current
          health on hit). After Q marked a champion, the next attack strikes twice: d_at ticks later d_dmg + d_ratio%
          AD more and he heals d_heal + d_heal_ratio% AD.
  skill   Q Blade of the Ruined King (破败王剑): a `Targeting` cast on `EnemyWithoutTower` (q_range): on tick q_at a
          thrust (a fast line, q_len) through everything: q_dmg + q_ratio% AD; a champion hit is marked (q_mark ticks).
  skill2  W Spectral Maw (千载幽咽) opened by E Harrowed Path (茫茫焦土): a `Targeting` cast on `EnemyChampion`
          (w_range, an engage): the mist rises round him first - e_t ticks of e_ms% move speed and e_as% attack speed,
          hidden (CasterInvisible) for e_inv ticks while he charges - then on tick w_wind he dashes w_dash and
          spits the maw (w_len, stops on the first enemy): w_dmg + w_ratio% AD and a w_stun-tick stun. The pros'
          W -> Q: the maw stunning a champion with Q ready thrusts Q at it as soon as he lands.
  ult     R Heartbreaker (痛贯天灵): a `Targeting` cast on `EnemyChampionRecentlyAttacked` (league_darius R: the
          closest thing to "the lowest health" the data has): the target is slowed r_slow% while he leaps onto it
          (MoveToTarget), on tick r_hit it takes r_dmg + r_ratio% AD + r_hp% of its maximum health (League: of its
          missing health), every other enemy round the landing is knocked back. Ends a possession.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_viego.data_champion")
ID = "league_viego"
FX = "asset/league/effects/league_viego_fx"
BIG = "asset/league/effects/league_viego_big"

# Timings: placeholders until the strips are in (assets/source/viego/poses.json).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Viego: 630 +109
    # hp, 57 AD +3.5, 34 armour, 32 mr, 345 move, 200 range - a skirmisher who lives on resets
    "hp": 980, "hp_g": 105, "atk": 92, "atk_g": 18, "def": 30, "def_g": 8, "mr": 26, "mr_g": 4, "ms": 1010, "ms_g": 11,
    # attack: the sword (League's Q passive: 2-7% current health on hit, at least 10-35; here % max health on champions)
    "atk_range": 26000, "atk_dur": 24, "atk_cd": 64, "atk_st": 10, "a_pct": 2,
    # the double strike after Q's mark (League: the second hit 20% AD + 15% AP, heals 145% of it on champions)
    "d_at": 6, "d_dmg": 20, "d_ratio": 60, "d_heal": 40, "d_heal_ratio": 40,
    # Q Blade of the Ruined King (League: 600 x 125 thrust, 10-100 + 70% AD, cd 5-3 s, mark 4 s)
    "q_cd": 330, "q_range": 36000, "q_dur": 18, "q_at": 8, "q_len": 40000, "q_speed": 8000, "q_rad": 6500,
    "q_y": 4000, "q_dmg": 50, "q_ratio": 70, "q_mark": 240,
    # skill2: E Harrowed Path's mist (League: 8 s, 22.5-37.5% move speed, 25-55% attack speed, camouflage; cd 14-6 s)
    "w_cd": 600, "w_range": 46000, "w_dur": 46, "e_t": 300, "e_ms": 30, "e_as": 40, "e_inv": 45,
    # then W Spectral Maw (League: charge to 1 s, dash 300, missile 500-900, 25-355 + 100% AP, stun 0.25-1.25 s; cd 8 s)
    "w_wind": 24, "w_dash": 18000, "w_dspeed": 3000, "w_len": 42000, "w_speed": 4000, "w_rad": 6000, "w_y": 4000,
    "w_dmg": 90, "w_ratio": 70, "w_stun": 66,
    # R Heartbreaker (League: 500 range leap, 120% AD + 12-20% missing hp (+ crit), 99% slow 0.25 s, cd 120-80 s)
    "r_cd": 3000, "r_range": 42000, "r_dur": 36, "r_speed": 5000, "r_reach": 60000, "r_slow": 99, "r_slow_t": 18,
    "r_hit": 18, "r_dmg": 120, "r_ratio": 120, "r_hp": 12, "r_kb_r": 18000, "r_kb_speed": 2500, "r_kb_t": 12,
    # passive Sovereign's Domination (League: takedown window 3 s, possession 10 s, untouchable 1 s while taking the
    # soul, heal 2% + of the champion's max health)
    "p_win": 180, "p_t": 600, "p_inv": 60, "p_anim": 24, "p_heal": 60, "p_heal_ratio": 50,
    "p_ad": 25, "p_as": 30, "p_ms": 15,
    # cooldown caps when a soul is taken: skill_cooldown_mult on both skills; the ult gets skill + ult share (0 = none)
    "p_skill": 10000, "p_ult": 0,
    # the add-on's soul kits (native=1 only): bolts, the slam ring, the piercing shot, heals, stuns
    "s_bolt_speed": 5000, "s_y": 4000, "s_a_dmg": 20, "s_q_dmg": 70, "s_q_ratio": 80, "s_e_dmg": 90, "s_e_ratio": 80,
    "s_e_at": 10, "s_stun": 50, "s_slow": 30, "s_slow_t": 120, "s_ring_r": 20000, "s_line_len": 50000, "s_heal": 60,
    "s_heal_ratio": 40,
    # the add-on's soul: picked up within soul_r of the body, kept soul_t ticks; ranged souls lengthen his attack
    "soul_r": 35000, "soul_t": 480, "s_range": 25000,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_viego_soul: its native passive reads deaths and sets p_go on him
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


def cview(name, follow=True):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `WithSelf` would also hit the action's target)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


SOULS = ("melee", "range", "mage", "util", "assassin")


def soul_kits(p, track):
    """The add-on's possession (native=1): five generic kits by the possessed champion's category, played through
    his attack / Q / W slots while the add-on's buff league_viego_soul_<category> is on him (the slots' ranges and
    targets stay Viego's; the body is the victim's, drawn by the add-on). Each: (attack, skill, skill2) effects."""
    hit = [view("s_hit"), tsfx("a_hit")]
    bolt = lambda target, effects: homing("s_bolt", p["s_bolt_speed"], p["s_y"], target, effects)
    champ = homing("s_twin", 100000, 0, "EnemyChampion", [track()])
    slow = buff("s_slow", p["s_slow_t"], move_speed_mult=-p["s_slow"])
    ring = lambda r, effects: on_me(cview("s_ring"), around(r, "EnemyWithoutTower", effects))
    kits = {
        # fighters and tanks: a heavy cleave; a slam round him that slows; a charge onto the target that stuns
        "melee": (combine(attack(p["s_a_dmg"], 100), champ, *hit),
                  combine(anim("skill", p["q_dur"]), sfx("q"),
                          delayed(p["q_at"] - 1, ring(p["s_ring_r"], [attack(p["s_q_dmg"], p["s_q_ratio"]), slow, *hit]))),
                  combine(anim("skill2", p["w_dur"]), sfx("w"),
                          {"type": "MoveToTarget", "speed": p["w_dspeed"], "range": p["w_range"], "end_effects": []},
                          delayed(p["s_e_at"], attack(p["s_e_dmg"], p["s_e_ratio"]),
                                  {"type": "Stun", "duration": p["s_stun"]}, champ, *hit))),
        # marksmen: bolts from afar; a piercing shot; three bolts at enemies near
        "range": (bolt("Enemy", [attack(0, 100), *hit]),
                  combine(anim("skill", p["q_dur"]), sfx("q"),
                          delayed(p["q_at"] - 1, line("s_line", p["q_speed"], p["s_line_len"], p["q_rad"], p["s_y"],
                                                      "EnemyWithoutTower", True,
                                                      [attack(p["s_q_dmg"], p["s_q_ratio"]), *hit]))),
                  combine(anim("skill2", p["w_dur"]), sfx("w"),
                          *[delayed(p["s_e_at"] + 4 * k,
                                    {"type": "RandomTarget", "range": p["w_range"], "casting_target": "EnemyWithoutTower",
                                     "from_projectile": False,
                                     "effects": [bolt("EnemyWithoutTower",
                                                      [attack(p["s_e_dmg"] // 3, p["s_e_ratio"] // 3), *hit])]})
                            for k in range(3)])),
        # mages: a bolt; a burst on the target that splashes; a bolt that roots
        "mage": (bolt("Enemy", [attack(0, 100), *hit]),
                 combine(anim("skill", p["q_dur"]), sfx("q"),
                         delayed(p["q_at"] - 1, {"type": "TargetSplashProjectile", "name": n("s_bolt"),
                                                 "speed": p["s_bolt_speed"], "range": p["s_ring_r"], "y_offset": p["s_y"],
                                                 "applied_target": "EnemyWithoutTower",
                                                 "applied_effects": [T(e) for e in [attack(p["s_q_dmg"], p["s_q_ratio"]),
                                                                                    view("s_burst"), tsfx("q_hit")]]})),
                 combine(anim("skill2", p["w_dur"]), sfx("w"),
                         delayed(p["s_e_at"], bolt("EnemyWithoutTower",
                                                   [attack(p["s_e_dmg"], p["s_e_ratio"]),
                                                    {"type": "Bind", "duration": p["s_stun"]}, *hit]), champ))),
        # supports: a bolt; heals the allied champions round him; slows the enemies round him and speeds him up
        "util": (bolt("Enemy", [attack(0, 100), *hit]),
                 combine(anim("skill", p["q_dur"]), sfx("q"),
                         delayed(p["q_at"] - 1, on_me(cview("s_ring"),
                                                      around(p["s_ring_r"], "AllyChampion",
                                                             [{"type": "Heal", "amount": p["s_heal"],
                                                               "attack_ratio": p["s_heal_ratio"], "ap_ratio": 0,
                                                               "heal_type": "Ally"}, buff("s_heal", 30)])))),
                 combine(anim("skill2", p["w_dur"]), sfx("w"),
                         delayed(p["s_e_at"], ring(p["s_ring_r"], [attack(p["s_e_dmg"] // 2, p["s_e_ratio"] // 2), slow, *hit]),
                                 refresh("s_haste", p["s_slow_t"], move_speed_mult=p["s_slow"])))),
        # assassins: a swift cut that hits harder; a blink onto the target; vanishing for a moment
        "assassin": (combine(attack(p["s_a_dmg"], 115), champ, *hit),
                     combine(anim("skill", p["q_dur"]), sfx("q"),
                             {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["q_range"] + 20000, "end_effects": []},
                             delayed(p["q_at"], attack(p["s_q_dmg"], p["s_q_ratio"] + 30), champ, *hit)),
                     combine(anim("skill2", p["w_dur"]), sfx("e"), cview("e_mist"),
                             {"type": "CasterInvisible", "tick": p["s_slow_t"]},
                             refresh("s_haste", p["s_slow_t"], move_speed_mult=p["s_slow"],
                                     attack_speed_mult=p["s_slow"]))),
    }
    return kits


def by_soul(kits, slot, own):
    """His own effect, or the possessed category's while the add-on's buff is on him."""
    out = own
    for cat in reversed(SOULS):
        out = sw(f"soul_{cat}", kits[cat][slot], out)
    return out


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive: Sovereign's Domination
    def end():
        """Back to himself (the possession's time is up, or Heartbreaker)."""
        return combine(*rm("p_on", "p_new"), cview("p_end"), sfx("p_end"))

    def soul():
        """A soul taken: untouchable a moment, healed, possessed for p_t ticks; Q and W ready again."""
        cdr = {"skill_cooldown_mult": p["p_skill"], "ult_cooldown_mult": p["p_ult"] - p["p_skill"]}
        return combine(refresh("p_lock", p["p_win"]), refresh("p_alive", p["p_win"]),
                       refresh("p_safe", p["p_inv"], damaged_reduce=100, cc_immune=True),
                       refresh("p_on", p["p_t"], attack_mult=p["p_ad"], attack_speed_mult=p["p_as"],
                               move_speed_mult=p["p_ms"]),
                       refresh("p_new", p["p_t"] - 1), refresh("p_cdr", 2, **cdr),
                       heal(p["p_heal"], p["p_heal_ratio"]), anim("possess", p["p_anim"]), cview("p_take"),
                       sfx("p"), sfx("p_hit"), voice("vo_p", p),
                       delayed(p["p_t"], sw("p_new", NONE, sw("p_on", end()))))

    if native:
        def track():
            """The add-on's credit: a mark on the champion he hit (it reads deaths itself)."""
            return buff("mark", p["p_win"])
        # the add-on puts the possession's state on him itself (its buffs, the heal, the cooldowns) and sets p_go /
        # p_off for the pictures and sounds, played by his next action
        show = combine(anim("possess", p["p_anim"]), cview("p_take"), sfx("p"), sfx("p_hit"), voice("vo_p", p))
        take = combine(sw("p_go", combine(*rm("p_go"), show)),
                       sw("p_off", combine(*rm("p_off"), cview("p_end"), sfx("p_end"))))
    else:
        watch = sw("p_alive", NONE, sw("p_lock", NONE, soul()))

        def track():
            """On a champion he hit: keeps p_alive up while it lives; a watcher on him sees it lapse = a takedown."""
            return combine(casted(p["p_win"], 1, refresh("p_alive", 2)),
                           on_me(refresh("p_alive", 3), casted(p["p_win"] - 2, 1, watch)))
        take = NONE

    # ------------------------------------------------------------------ attack (+ the marked double strike)
    hit_champ = homing("a_twin", 100000, 0, "EnemyChampion", [attack(0, 0, p["a_pct"]), track()])
    double = combine(*rm("q_mark"), sfx("a_double"),
                     delayed(p["d_at"], attack(p["d_dmg"], p["d_ratio"]), heal(p["d_heal"], p["d_heal_ratio"]),
                             view("a_double"), tsfx("a_double")))
    swing = combine(attack(0, 100), hit_champ, view("a_hit"), tsfx("a_hit"), sw("q_mark", double))
    kits = soul_kits(p, track) if native else None
    if native:
        swing = by_soul(kits, 0, swing)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), take, swing), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Blade of the Ruined King
    q_hit = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]
    q_champ = [buff("q_marked", p["q_mark"]), on_me(refresh("q_mark", p["q_mark"])), track()]

    def thrust():
        return combine(line("q_thrust", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True,
                            q_hit),
                       line("q_twin", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyChampion", True, q_champ))

    q_use = combine(refresh("q_cd", p["q_cd"]), refresh("q_skip", p["q_cd"] // 2))
    q_own = combine(anim("skill", p["q_dur"]), q_use, sfx("q"), voice("vo_q", p), delayed(p["q_at"] - 1, thrust()))
    if native:
        q_own = combine(take, by_soul(kits, 1, q_own))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_skip", combine(*rm("q_skip")), q_own))

    # ------------------------------------------------------------------ skill2: E's mist, then W Spectral Maw
    dash_t = -(-p["w_dash"] // p["w_dspeed"])
    fly_t = -(-p["w_len"] // p["w_speed"])
    w_hit = [attack(p["w_dmg"], p["w_ratio"]), {"type": "Stun", "duration": p["w_stun"]}, buff("w_stun", p["w_stun"]),
             view("w_hit"), tsfx("w_hit")]
    w_champ = [on_me(refresh("w_got", fly_t + 6)), track()]
    combo = sw("w_got", sw("q_cd", NONE, combine(*rm("w_got"), anim("skill", p["q_dur"]), q_use, sfx("q"),
                                                 delayed(p["q_at"] - 1, thrust()))))
    maw = combine(sfx("w"), voice("vo_w", p),
                  {"type": "MoveTo", "speed": p["w_dspeed"], "range": p["w_dash"], "end_effects": []},
                  delayed(dash_t, line("w_maw", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyWithoutTower",
                                       False, w_hit),
                          line("w_twin", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyChampion", False,
                               w_champ)),
                  delayed(dash_t + fly_t + 1, combo))
    mist = combine(refresh("e_on", p["e_t"], move_speed_mult=p["e_ms"], attack_speed_mult=p["e_as"]),
                   {"type": "CasterInvisible", "tick": p["e_inv"]}, cview("e_mist"), sfx("e"), sfx("e_mist"),
                   voice("vo_e", p))
    w_own = combine(anim("skill2", p["w_dur"]), mist, sfx("w_charge"), delayed(p["w_wind"] - 1, maw))
    if native:
        w_own = combine(take, by_soul(kits, 2, w_own))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion", w_own)

    # ------------------------------------------------------------------ ult: R Heartbreaker
    kb = around(p["r_kb_r"], "EnemyWithoutTower", [{"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb_t"]}])
    land = [attack(p["r_dmg"], p["r_ratio"], p["r_hp"]), view("r_hit"), tsfx("r_hit"), track(),
            on_me(cview("r_land"), sfx("r_land"), kb)]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(anim("ult", p["r_dur"]), take, sw("p_on", end()), sfx("r"), voice("vo_r", p), cview("r_cast"),
                         buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"], cc_immune=True),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_reach"], "end_effects": []},
                         delayed(p["r_hit"] - 1, *land)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_thrust"), P_("w_maw")]
    views_e = [E("a_hit"), E("a_double"), E("q_hit"), E("w_hit"), E("e_mist", BIG, -1, False), E("p_take", BIG, 3),
               E("p_end", FX, 3), E("r_cast", FX, 3), E("r_hit", BIG, 3), E("r_land", BIG, -1, False)]
    views_b = [B_("q_marked", FX, 3), B_("w_stun", FX, 3), B_("e_on", FX, 3), B_("p_on", BIG, 3), B_("p_safe", FX, 3)]
    extra = {}
    if native:
        views_p += [P_("s_bolt"), P_("s_line")]
        views_e += [E("s_hit"), E("s_burst", BIG, 3), E("s_ring", BIG, -1)]
        views_b += [B_("s_slow", FX, 3), B_("s_heal", FX, 3), B_("s_haste", FX, 3)]
        extra["passive"] = {"passive_ref": "league_viego_soul:possess",
                            "params": {k: p[k] for k in ("p_t", "p_inv", "p_heal", "p_heal_ratio", "p_ad", "p_as", "p_ms",
                                                         "p_skill", "p_ult", "p_win", "soul_r", "soul_t", "s_range")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Heal"], **extra,
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (deaths read natively)")
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
