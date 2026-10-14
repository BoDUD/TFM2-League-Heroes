"""Build league_kindred.data_champion (jungle, ranged marksman: Lamb and Wolf) from the parameters P.

    python tools/kit/build_kindred.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-14: jungle ADC; Q as skill, E first and W while E is spent as skill2, R as ult; the marks
in the main pack as far as the data reaches, League's mark rules in an add-on later; the pros' combos). The Wolf is drawn
into Lamb's frames; his bites and his pounce are pictures on the targets.
  passive Mark of the Kindred (千珏之印): an enemy champion she hit dies within p_win ticks (a takedown, league_viego's
          window: the hit champion keeps a 2-tick flag p_alive up while it lives, a watcher on her sees it lapse), or her
          arrow kills one (league_jinx's kill check, seen even while another hit champion keeps the flag up) -> a mark:
          one more `Permanent` instance of p_mark (+p_range attack range, +p_as% attack speed, +1 ability power - the
          gauge Mounting Dread's pounce reads; nothing else of hers reads ability power and she buys none), the mark's
          picture (p_stack) and sound. Death clears data buffs, so the marks last one life here; the add-on is to keep them.
  attack  Lamb's arrow (a homing projectile, released on a_st) at the target; its champion-only twin carries the mark
          tracking. Her arrow hits climb Mounting Dread's count; with R armed the release also checks the danger.
  skill   Q Dance of Arrows (乱箭之舞): a `Targeting` cast on `EnemyWithoutTower` (q_range: waves and camps too). The
          leap on q_go (q_move_t ticks, the skill tag's frames 2-4): away from an enemy champion within q_near (q_dash,
          the pros' kite when dived), else a hop back from the target (q_hop) when it stands within q_close of her (a
          hidden instant shot at it asks from there, league_samira's reach probe), else a hop toward it (q_hop): the
          target stays in the arrows' reach. On q_at the arrows: at most three, one to each of the first three enemies
          within q_r (entity order: champions first), q_dmg + q_ratio% AD each; q_as% attack speed for q_as_t ticks. In
          her own Wolf's Frenzy (w_in, refreshed by the zone while she stands in it) Q's cooldown is capped at
          100 / (100 + w_cdr) of q_cd (League's shorter cooldown; the cap's -w_cdr on the ult keeps R's own).
  skill2  E Mounting Dread (横生惧意) first: a `Targeting` cast on `EnemyWithoutTower` (e_range). The marking arrow leaves
          on e_at - at an enemy champion her team hit lately (`EnemyChampionRecentlyAttacked`, the data's "wounded"),
          else at the cast target: e_slow% slow for e_slow_t ticks and the mark for e_t ticks (league_tristana E: a poll
          on the marked unit every 2 ticks, the count on her). Her third arrow hit while the mark lasts makes the Wolf
          pounce on the marked unit wherever it is: e_dmg + e_ratio% AD (+ e_hp% of its maximum health on champions -
          League's missing health is unreadable; monsters only the flat part), + e_mark_ap% ability power as magic
          (the marks' share). W Wolf's Frenzy (狼灵狂热) while E is spent - or first, when both are ready and an enemy
          champion is within w_fight (the pros' W -> Q in the zone -> E): the zone lies where she stands for w_t ticks
          (Ekko's anchor, radius w_r); every w_per ticks the Wolf bites the first enemy in it (champions first):
          w_dmg + w_ratio% AD.
  ult     R Lamb's Respite (羊灵生息), armed (league_lulu R): a 3-tick cast on the idle tag (`EnemyChampion` within
          r_arm_range) arms r_armed for r_arm ticks; her arrows check the danger while it lasts. Nothing in the data reads
          health, so the main pack waits for the dangers it can see (the user: 「千珏r大招逻辑不要乱放」), each through
          its own hidden lob onto the allied champion in question, whose landing counts the enemy champions within r_near
          of him and whose 2-tick-later read on him saves: an allied champion in crowd control within r_reach with at
          least one enemy champion within r_near of him (r_cprobe / r_ccount / r_c1); or, once the fight has gone on (her
          last r_fight champion hits each within f_t ticks of the one before), a random allied champion within r_reach
          (her too) with r_need or more enemy champions within r_near of him (r_probe / r_count / r_n1 -> r_n2). The save:
          the zone round her on r_at (r_r, r_t ticks): every r_per ticks the allied champions in it get r_per + 2 ticks
          of `undying` (League: health stops at 10%); when it ends, every allied champion in it heals r_heal +
          r_heal_ad% AD. Unused, the cooldown is refunded. r_now=1 is addons/league_kindred's copy, whose hook casts R
          when someone in the circle is about to die (it reads health): the slot saves at once - no arming, no refund,
          no check in her attack.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_kindred.data_champion")
ID = "league_kindred"
FX = "asset/league/effects/league_kindred_fx"
BIG = "asset/league/effects/league_kindred_big"

# Timings from the sheet (tools/art/rig_kindred.py TIMING, checked frame by frame by the parent session, 2026-10-14;
# ticks = ms x 0.06): attack 440 ms (26 ticks), frames 1-3 draw the string, the arrow leaves as frame 4 starts (250 ms:
# start_timing 14, the effect on tick 15); Q 420 ms (25), airborne on frames 3-4 (120-240 ms: the leap from +4 over 10
# ticks), the three arrows as frame 6 starts (320 ms: +19); E 440 ms (26), the marking arrow on frame 4 (250 ms: +15);
# W 360 ms (22), the zone on frame 2 (the raised arm, 80 ms: +5); R 540 ms (32), the zone on frame 5 (the raised bow,
# 340 ms: +20). Arrow heights from the bow grip on the release frames of the 1x sheet (lift = 5000 - y_offset, 1000
# units a px): attack frame 4 11.5 px (a_y -6500), skill2 frame 4 and skill frame 6 7.5 px (e_y, q_y -2500); every
# champion-only twin flies with its arrow's speed and height, so both land on the same tick.
# The slots' own actions are 3-tick casts that force the tag (league_nilah's way): Wolf's Frenzy's skill_cooldown_mult
# also speeds skill actions, and a forced animation keeps its length.
# Numbers = candidate d6 of the 10-min classic-SDK simulations (Temp/kn_sim/sim/kd.py --lane 1 against the base demon,
# circus blade, hunter, inquisitor and ninja, three lineups, both sides, 2026-10-14): +1.18 on seeds 1-24, +1.18 on 25-48
# (league_evelynn +1.38 / +1.30, league_lillia +1.33 / +1.77, league_khazix +0.97 / +1.16, league_nidalee +1.56 / +0.97:
# peers' average +1.31 / +1.30), damage dealt 9476 / 9327 (peers 6990-9951). The draft d1 (attack 100 +22, arrows on
# placeholder ticks 10 / +10 / +14) was +2.85 / +2.15; one change each from it on seeds 1-24: attack 92 +19 +1.13 (d2e,
# +1.47 on 25-48), 95 +20 +1.83 (+1.32), the Range base's stats (hp 900 +90, defence 20, mr 15, move 1000, attack
# every 60) +1.58, no range / attack speed on the marks +1.76, the Wolf's bite 15 + 15% +2.08, Q's arrows 30 + 50%
# +2.41. Retimed to the sheet's release frames and bow heights (d4 = d2e retimed) +1.64 / +1.69; then attack 90 +19
# (d5a) +1.38 / +1.17, attack growth 18 (d5b) +1.70 / +0.55. d6 = d5a with R's stricter danger (the crowd-controlled
# ally needs an enemy champion near him, the fight branch two): 0.23 saves a game instead of 0.81 (120 logged games).
# The add-on's rule (addons/league_kindred: R when someone in the circle is about to die, on the r_now=1 copy) in a
# PlayerInputAi hook of the same simulator (Temp/kn_sim/sim/kn_hook.rs, kd_hook.py): +2.09 / +1.96.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9, range 60000, cd 60; the base
    # junglers 120 +30 every 50, hp 900 +80, move 1100 +14); League's Kindred: 595 +104 hp, 65 AD, 29 armour, 33 mr,
    # 325 move, 500 range (55000 here, as league_samira / league_lucian), attack speed 0.625
    "hp": 940, "hp_g": 92, "atk": 90, "atk_g": 19, "def": 24, "def_g": 7, "mr": 18, "mr_g": 3, "ms": 1020, "ms_g": 11,
    "atk_range": 55000, "atk_dur": 26, "atk_cd": 56, "a_st": 14, "a_speed": 6000, "a_y": -6500,
    # passive Mark of the Kindred (League: marks from hunted champions and monsters; at 4 marks +75 range, +25 every 3
    # more; Dance of Arrows +5% attack speed a mark, Mounting Dread +0.5% missing health a mark)
    "p_win": 180, "p_range": 1500, "p_as": 4, "p_ap": 1, "p_show": 90,
    # Q Dance of Arrows (League: dash 300, arrows at up to 3 enemies, 40-140 + bonus AD, +35% attack speed 4 s; cd 9 s,
    # 4-2 s in Wolf's Frenzy)
    "q_cd": 480, "q_range": 60000, "q_anim": 25, "q_go": 4, "q_move_t": 10, "q_at": 19, "q_near": 20000,
    "q_close": 25000, "q_dash": 30000, "q_hop": 15000, "q_r": 55000, "q_speed": 6000, "q_y": -2500, "q_dmg": 45,
    "q_ratio": 65, "q_as": 35, "q_as_t": 240,
    # skill2 slot (E first, W while E is spent; both cooldowns are caster flags)
    "s2_cd": 90, "e_range": 55000,
    # E Mounting Dread (League: 500 range, 30% slow 1 s, mark 4 s, the 4th hit (3 attacks) - Wolf pounces: 50-230 + 100%
    # bonus AD + 5% missing health (crit x), 200 cap on monsters; cd 14-8 s)
    "e_cd": 600, "e_anim": 26, "e_at": 15, "e_speed": 6000, "e_y": -2500, "e_slow": 30, "e_slow_t": 60, "e_t": 240,
    "e_pic": 20, "e_dmg": 60, "e_ratio": 90, "e_hp": 4, "e_mark_ap": 800,
    # W Wolf's Frenzy (League: 8.5 s, 800 radius, the Wolf bites 25-45 + 20% AD + 1.5% current health; cd 18-14 s)
    "w_cd": 960, "w_anim": 22, "w_at": 5, "w_fight": 70000, "w_t": 510, "w_r": 60000, "w_per": 60, "w_first": 30,
    "w_dmg": 25, "w_ratio": 25, "w_home": 10, "w_cdr": 100,
    # R Lamb's Respite (League: 530 radius round her, 4 s, nobody under 10% health, then heals 225-375; cd 160-120 s)
    "r_cd": 3000, "r_arm": 900, "r_arm_range": 70000, "r_reach": 50000, "r_near": 25000, "r_need": 2,
    "r_anim": 32, "r_at": 20, "r_r": 50000, "r_t": 240, "r_per": 6, "r_heal": 150, "r_heal_ad": 40,
    # the fight branch's gate: her last r_fight champion hits came less than f_t ticks apart (0 = no gate)
    "r_fight": 3, "f_t": 150,
    # 1 = the copy for addons/league_kindred (its hook casts R when someone in the circle is about to die): the ult slot
    # saves at once, no arming window, no refund, no danger check in her attack
    "r_now": 0,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # test builds for the simulator's logs only: 1 = unbound ViewEffects (dbg_*) mark which branch ran
    "dbg": 0,
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


def flat(node):
    """The tree with every Combine that sits straight in a Combine's, a Delayed's or a RandomTarget's `effects`
    spliced into that list (the same effects in the same order, fewer nodes for the game's per-tick copy)."""
    if isinstance(node, list):
        return [flat(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: flat(v) for k, v in node.items()}
    if out.get("type") in ("Combine", "Delayed", "RandomTarget"):
        eff = []
        for x in out["effects"]:
            if isinstance(x, dict) and x.get("type") == "Combine":
                eff.extend(x["effects"])
            else:
                eff.append(x)
        out["effects"] = eff
    return out


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


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
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def heal_ally(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Ally"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `WithSelf` would also hit the action's target)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def anchor(name, zones):
    """Ekko's anchor (league_viego's mist, league_camille R): a 1-unit line from her own spot whose end_effects start
    the zones there. A zone put straight into an action is never created."""
    return {"type": "LinearProjectile", "name": n(name), "speed": 1, "range": 1, "y_offset": 5000, "penetrate": True,
            "shape": circle(1000), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(zones)}


def field(name, radius, tick, period, first, target, effects, end=()):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": [T(e) for e in end]}


def drop(name, *end, hit=()):
    """A hidden one-tick lob onto the unit in hand (league_annie R): its end_effects start a zone on that spot,
    `hit` runs on the unit itself (a Delayed there is queued on him)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": "AllyChampion",
            "applied_effects": [T(e) for e in hit], "end_effects": list(end)}


def zone1(name, radius, target, effects):
    """A one-tick area on the lob's landing spot."""
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
    dbg = (lambda name: view("dbg_" + name)) if p["dbg"] else (lambda name: None)

    def mark(effect, name):
        """The effect, and in a test build (dbg=1) an unbound ViewEffect beside it that the logs count."""
        return combine(effect, dbg(name)) if p["dbg"] else effect

    # ------------------------------------------------------------------ passive: Mark of the Kindred
    gain = combine(refresh("p_lock", p["p_win"]), refresh("p_alive", p["p_win"]),
                   flag("p_mark", None, range=p["p_range"], attack_speed_mult=p["p_as"], magic_power=p["p_ap"]),
                   sw("p_has", NONE, flag("p_has", None)), refresh("p_stack", p["p_show"]), sfx("p"))
    watch = sw("p_alive", NONE, sw("p_lock", NONE, mark(gain, "p_window")))
    # on a champion she hit: its casted keeps p_alive up while it lives; the watcher on her sees it lapse = a takedown
    track = combine(casted(p["p_win"], 1, refresh("p_alive", 2), kind="Bleed"),
                    on_me(refresh("p_alive", 3), casted(p["p_win"] - 2, 1, watch)))
    # her own killing blow (league_jinx Get Excited!): the flag before, the living target's clear, the read 4 ticks on
    k_set = refresh("k_a", 40)
    k_read = combine(casted(3, 1, *rm("k_a"), kind="Bleed"),
                     on_me(delayed(4, sw("k_a", combine(*rm("k_a"), sw("p_lock", NONE, mark(gain, "p_kill")))))))

    # ------------------------------------------------------------------ R Lamb's Respite (the save; armed or at once)
    safe = field("r_field", p["r_r"], p["r_t"], p["r_per"], 0, "AllyChampion",
                 [buff("r_safe", p["r_per"] + 2, undying=True)],
                 end=[heal_ally(p["r_heal"], p["r_heal_ad"]), view("r_heal"), tsfx("r_heal")])
    save = on_me(anim("ult", p["r_anim"]), sfx("r"), voice("vo_r", p),
                 delayed(p["r_at"], cview("r_zone"), anchor("r_anchor", [safe])))
    go = combine(*rm("r_armed"), save)

    def danger(lob, zone, count, need_flag, name):
        """A hidden one-tick lob onto the allied champion in hand: its landing counts the enemy champions within r_near
        of him (`count` runs once per enemy champion there), and 2 ticks later, on him, `need_flag` on her with R still
        armed is the save (the first probe to save removes r_armed, so a second one that tick finds it gone)."""
        return drop(lob, zone1(zone, p["r_near"], "EnemyChampion", [count]),
                    hit=[delayed(2, sw("r_armed", sw(need_flag, mark(go, name))))])
    # the crowd-control branch: an allied champion in crowd control within r_reach, with an enemy champion within
    # r_near of him (its own lob, zone and flag: r_cprobe / r_ccount / r_c1)
    cc_probe = danger("r_cprobe", "r_ccount", flag("r_c1", 4), "r_c1", "r_cc")
    # the fight branch, once the fight has gone on: a random allied champion within r_reach (her too) with r_need or
    # more enemy champions within r_near of him (r_probe / r_count / the climb r_n1 -> r_n2)
    need = "r_n2" if p["r_need"] >= 2 else "r_n1"
    fight_probe = danger("r_probe", "r_count", sw("r_n1", flag("r_n2", 4), flag("r_n1", 4)), need, "r_probe")
    fights = [f"f_{k}" for k in range(1, p["r_fight"] + 1)] if not p["r_now"] else []

    def fight_up():
        """One more of her champion hits: f_1..f_k all on, renewed (league_veigar R's rungs), the top one kept."""
        out = combine(*rm(*fights), flag("f_1", p["f_t"]))
        for k in range(1, p["r_fight"]):
            out = sw(f"f_{k}", combine(*rm(*fights), *[flag(f"f_{j}", p["f_t"]) for j in range(1, k + 2)]), out)
        return sw(f"f_{p['r_fight']}", combine(*rm(*fights), *[flag(f, p["f_t"]) for f in fights]), out)
    ally_probe = pick(p["r_reach"], "AllyChampion", fight_probe)
    # r_now=1 (addons/league_kindred's copy: its hook casts R when someone in the circle is about to die): no check
    # anywhere, the ult slot saves at once
    r_check = None if p["r_now"] else sw("r_armed", combine(
        *rm("r_c1", "r_n1", "r_n2"), pick(p["r_reach"], "AllyChampionInCC", cc_probe),
        sw(fights[-1], ally_probe) if fights else ally_probe))

    # ------------------------------------------------------------------ attack
    # Mounting Dread's count: her arrow hits while the mark lasts; the third sets e_boom for the poll on the marked unit
    e_climb = sw("e_live", sw("e_2", combine(*rm("e_1", "e_2", "e_live"), flag("e_boom", 4)),
                              sw("e_1", combine(*rm("e_1"), flag("e_2", p["e_t"])), flag("e_1", p["e_t"]))))
    shot = homing("a_arrow", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit"), e_climb])
    twin = homing("a_twin", p["a_speed"], p["a_y"], "EnemyChampion",
                  [k_set, track, k_read] + ([fight_up()] if fights else []))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      flat(combine(sfx("a_shot"), r_check, shot, twin)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Dance of Arrows
    def arrow(step):
        return combine(flag(step, 2), homing("q_arrow", p["q_speed"], p["q_y"], "EnemyWithoutTower",
                                             [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]))
    volley = combine(*rm("q_n1", "q_n2", "q_n3"), sfx("q_arrows"),
                     around(p["q_r"], "EnemyWithoutTower",
                            [sw("q_n3", NONE, sw("q_n2", arrow("q_n3"), sw("q_n1", arrow("q_n2"), arrow("q_n1"))))]))
    t = p["q_move_t"]
    back = {"type": "MoveBack", "speed": p["q_dash"] // t, "tick": t}
    hop = {"type": "MoveBack", "speed": p["q_hop"] // t, "tick": t}
    fwd = {"type": "RushTime", "speed": p["q_hop"] // t, "tick": t, "range": 20000, "casting_target": "EnemyWithoutTower",
           "penetrate": True, "applied_effects": []}
    # where the target stands: a hidden instant shot at it asks from there whether she is within q_close (league_samira's
    # reach probe; both bodies count), so the hop keeps the target in the arrows' reach
    probe_q = homing("q_probe", 100000, 5000, "EnemyWithoutTower",
                     [pick(p["q_close"], "AllyOnlySelf", flag("q_in", p["q_go"] + 2), fp=True)])
    leap = combine(*rm("q_dived"), cview("q_dash"),
                   pick(p["q_near"], "EnemyChampion", flag("q_dived", 1), back, dbg("q_back")),
                   sw("q_dived", NONE, sw("q_in", mark(hop, "q_hop"), mark(fwd, "q_fwd"))))
    skill = action("skill", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   flat(combine(anim("skill", p["q_anim"]), sfx("q"), voice("vo_q", p), *rm("q_in"), probe_q,
                                sw("w_in", dbg("q_zone")) if p["dbg"] else None,
                                refresh("q_as", p["q_as_t"], attack_speed_mult=p["q_as"]),
                                delayed(p["q_go"], leap), delayed(p["q_at"], volley))))

    # ------------------------------------------------------------------ skill2: E Mounting Dread / W Wolf's Frenzy
    pounce = combine(*rm("e_boom", "e_live"),
                     sw("e_champ", attack(p["e_dmg"], p["e_ratio"], p["e_hp"]), attack(p["e_dmg"], p["e_ratio"])),
                     sw("p_has", magic(0, p["e_mark_ap"])), view("e_bite"), tsfx("e_bite"))
    poll = combine(sw("e_boom", pounce),
                   sw("e_live", sw("e_pic", NONE, combine(flag("e_pic", p["e_pic"]), view("e_mark")))))
    marked = [buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"), tsfx("e_hit"),
              *rm("e_1", "e_2", "e_boom", "e_pic"), refresh("e_live", p["e_t"]),
              casted(p["e_t"] + 4, 2, poll, kind="Bleed")]

    def e_fire():
        return combine(sfx("e_shot"), homing("e_arrow", p["e_speed"], p["e_y"], "EnemyWithoutTower", marked),
                       homing("e_twin", p["e_speed"], p["e_y"], "EnemyChampion", [refresh("e_champ", p["e_t"])]))
    e_shot = combine(*rm("e_aim", "e_champ"),
                     pick(p["e_range"], "EnemyChampionRecentlyAttacked", flag("e_aim", 1), e_fire(), dbg("e_champ")),
                     sw("e_aim", NONE, mark(e_fire(), "e_target")))
    e_cast = combine(flag("e_cd", p["e_cd"]), anim("skill2", p["e_anim"]), sfx("e"), voice("vo_e", p),
                     delayed(p["e_at"], e_shot))

    bite = sw("w_lock", NONE, combine(flag("w_lock", 2), attack(p["w_dmg"], p["w_ratio"]), view("w_bite"),
                                      tsfx("w_bite")))
    home = pick(p["w_r"], "AllyOnlySelf",
                refresh("w_in", p["w_home"] + 2, skill_cooldown_mult=p["w_cdr"], ult_cooldown_mult=-p["w_cdr"]), fp=True)
    w_cast = combine(flag("w_cd", p["w_cd"]), anim("w_cast", p["w_anim"]), sfx("w"), voice("vo_w", p),
                     delayed(p["w_at"], cview("w_zone"),
                             anchor("w_anchor", [field("w_field", p["w_r"], p["w_t"], p["w_per"], p["w_first"],
                                                       "EnemyWithoutTower", [bite]),
                                                 field("w_home", p["w_r"], p["w_t"], p["w_home"], 0, "AllyChampion",
                                                       [home])])))
    # W now: W ready and E spent, or both ready with an enemy champion within w_fight (the pros' W first); else E when
    # ready. One-tick flags pick the branch first, so each cast is written once (the game copies skill2 every tick).
    pick_w = combine(*rm("w_go", "s2_fight"),
                     sw("w_cd", NONE, sw("e_cd", flag("w_go", 1),
                                         combine(pick(p["w_fight"], "EnemyChampion", flag("s2_fight", 1)),
                                                 sw("s2_fight", mark(flag("w_go", 1), "w_first"))))))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    flat(combine(pick_w, sw("w_go", w_cast, sw("e_cd", dbg("s2_empty") or NONE, e_cast)))), key="skill2")

    # ------------------------------------------------------------------ ult: arms Lamb's Respite (r_now=1: saves at once)
    if p["r_now"]:
        ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", flat(combine(save)), key="ult")
    else:
        ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", flat(combine(
            *rm("r_armed"), flag("r_armed", p["r_arm"]), dbg("r_arm"), r_check,
            delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900)))))),
            key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_arrow"), P_("q_arrow"), P_("e_arrow")]
    # the zones' pictures are caster pictures left on her spot (a ViewEffect on her own spot never shows, league_thresh R;
    # a zone's own picture would be turned half round, league_camille R), each tag as long as its zone
    views_e = [E("a_hit"), E("q_hit"), E("q_dash", FX, -1, False), E("e_hit"), E("e_mark", FX, 3), E("e_bite", BIG, 3),
               E("w_zone", BIG, -1, False), E("w_bite", FX, 3), E("r_zone", BIG, -1, False), E("r_heal", FX, 3)]
    views_b = [B_("p_stack", FX, 3)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Heal"],
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
