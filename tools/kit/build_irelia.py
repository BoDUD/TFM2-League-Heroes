"""Build league_irelia.data_champion (top, Melee) from the parameters P.

    python tools/kit/build_irelia.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-11, all the recommended options; the real mark / kill reset of Q goes into the add-on
addons/league_irelia, which swaps in build(p, native=True)):
  passive Ionian Fervor (艾欧尼亚热诚): a ladder of four exclusive caster flags pv1..pv4 (league_twitch's venom ladder),
          each +p_as% attack speed a rung, p_t ticks: every unit Q hits climbs a rung, every champion E, W or R hits
          one more (League: a stack for each). At pv4 (League's four stacks) the flag renews itself and her attacks hit
          p_dmg + p_ratio% AD more (League's on-hit magic) and the blades glow (view p_full).
  attack  A melee slash (100% AD); while R is armed it fires R when the reach check passes.
  skill   Q Bladesurge (利刃冲击): a `Targeting` cast on `EnemyWithoutTower` (q_range): `MoveToTarget` at the target,
          landing for q_dmg + q_ratio% AD, healing her q_heal + q_heal_r% AD and climbing a rung. League refreshes Q
          on a marked target or a kill; nothing reads a buff on the target, so (league_diana R's way) the refresh is
          another dash inside the same cast: a mark she laid (the caster flag mk, from E or R hitting a champion) is
          spent at the cast when an enemy champion is within q_range and opens q_again; a unit the dash kills opens
          it too (league_jinx's kill trigger: a flag q_k the dash lays, a 3-tick casted on the target that takes it
          off while the target lives: still there once q_kt's 5 ticks are gone = the target died). The landing only
          lays flags (q_land, q_k, q_kt); a poll on her (q_poll ticks, every 3) spends q_again
          once the dash and q_gap ticks have passed (and climbs the passive for every landing): the next dash goes at a crowd-controlled champion, else any
          champion, else the nearest unit within q_range - at most q_n dashes a cast. With the add-on (native=True)
          the mark is a real buff on the target and the passive league_irelia:surge decides the refresh natively.
  skill2  E Flawless Duet (比翼双刃) with W Defiant Dance (距破之舞) folded in on its own cooldown: a `Targeting` cast on
          `EnemyChampion` (e_range) whose own cooldown is short; the flags e_cd / w_cd are the real ones. E first: two
          blades thrown (her blade at her feet, the other behind the target), meeting after e_rel ticks: a
          `LineRangeProjectile` from her through the target (e_len, half-width e_w) for e_dmg + e_ratio% AD and an
          e_stun stun to every enemy on it, and on every champion a mark (5 s picture) + mk + a passive rung. The pro
          combo E -> Q needs no extra branch: the AI casts Q as soon as it is ready, and mk makes it dash twice (a Q
          copy here doubled skill2's tree). E cooling down: W (League's is a line of 775 too) - w_charge ticks of guard (base_attack_damaged_reduce w_dr, League's 50% physical
          damage reduction) then a slash along a line toward the target (w_len, w_w) for w_dmg + w_ratio% AD (League's
          fully charged strike), a rung for each champion.
  ult     R Vanguard's Edge (先锋之刃): a 3-tick cast on `EnemyChampion` (r_slot), armed like league_twitch R: two enemy
          champions within r_count, or one in crowd control, fire it at once; else it arms r_armed for r_arm ticks
          (each attack checks again, one champion within r_reach is enough after r_hold) and refunds the cooldown when
          it lapses. Fire: the cast pose and on r_rel a volley of blades at an enemy champion within r_range (picked then: the
          cast's target may have died) (`LinearProjectile` on `EnemyChampion`, stopping
          on the first champion: minions let it through, as in League). Where it stops: a cone through and behind that
          champion (r_cone) for r_dmg + r_ratio% AD, a r_slow% slow and r_dis ticks of disarm (`BlockAttack`) to every
          enemy in it, marks on the champions; then the blade wall: a zone (r_wall, r_wall_t ticks) that slows every
          enemy inside by r_wslow% (renewed every r_wper ticks) - League's ring cuts only those crossing it and
          nothing in data tells crossing from standing, so the disc stands for it; the burst carries the disarm.
          Combo R -> E: R fired from the slot throws E (when ready) at a champion in reach; E's own Q then follows.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_irelia.data_champion")
ID = "league_irelia"
FX = "asset/league/effects/league_irelia_fx"
BIG = "asset/league/effects/league_irelia_big"

# Numbers = draft d0 (before the simulation).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Irelia:
    # 65 AD +4 (bonus AS 2.5%), 630 +115 hp, 36 armour, 335 move, attack speed 0.656, range 200
    "hp": 960, "hp_g": 102, "atk": 80, "atk_g": 17, "def": 32, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    # attack
    "atk_range": 25000, "atk_dur": 22, "atk_cd": 62, "atk_st": 8,
    # passive: Ionian Fervor (League: 4 stacks 6 s, +7.5-15% AS each (30-60%), full: 7-19 + 20% bonus AD magic on hit)
    "p_n": 4, "p_t": 360, "p_as": 9, "p_dmg": 12, "p_ratio": 20,
    # skill: Q Bladesurge (League: 600 range, 5-105 + 60% AD, heal 9-14% AD, dash 1400 + MS, cd 11-3 s, refresh on a
    # marked target or a kill)
    "q_cd": 420, "q_range": 45000, "q_dur": 16, "q_speed": 5000, "q_dmg": 25, "q_ratio": 70, "q_heal": 10,
    "q_heal_r": 12, "q_n": 3, "q_gap": 6, "q_poll": 150, "q_k": 12,
    # skill2: E Flawless Duet (League: 775, 30-270 + 80% AP magic, stun 0.75 s, mark 5 s, cd 16-10 s) with W Defiant
    # Dance (League: 1.5 s charge, 50% physical damage reduction, 10-60 -> 30-180 + 120% AD at full charge, cd 20-10 s)
    "s2_cd": 300, "e_cd": 720, "e_range": 50000, "e_dur": 22, "e_rel": 18, "e_len": 80000, "e_w": 5000,
    "e_dmg": 50, "e_ratio": 60, "e_stun": 45, "mark_t": 300,
    "w_cd": 720, "w_dur": 44, "w_charge": 32, "w_dr": 50, "w_len": 55000, "w_w": 6000,
    "w_dmg": 40, "w_ratio": 110,
    # ult: R Vanguard's Edge (League: 1000 range, speed 2000, 125-375 + 70% AP magic, mark 5 s, wall 2.5 s: slow 90%
    # 1.5 s + disarm on crossing, cd 125/105/85 s)
    "r_cd": 3600, "r_slot": 70000, "r_count": 70000, "r_reach": 55000, "r_arm": 600, "r_hold": 180, "r_anim": 26,
    "r_rel": 10, "r_speed": 6000, "r_range": 85000, "r_r": 8000, "r_cone": 35000, "r_cos": 700, "r_dmg": 110,
    "r_ratio": 80, "r_slow": 70, "r_slow_t": 60, "r_dis": 60, "r_wall": 30000, "r_wall_t": 150, "r_wper": 10,
    "r_wslow": 40,
    # her spoken lines, at most one every vo_gap ticks
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


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def strip(name, length, width, delay, apply, target, effects):
    """A line from her toward the target: a unit is hit within about width + 15000 of it (champion-data, Ashe W)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def cone(name, radius, cos, delay, apply, target, effects):
    """A wedge opening away from her on the point a projectile stopped at (league_viktor E's hit)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": {"DirDot": {"radius": radius, "range": cos}},
            "delay": delay, "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def zone(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def ladder(names, top, last=None):
    """One flag of names at a time, read from the top: names[-1] runs `last` (default: nothing more), names[k] steps up
    to names[k+1], none starts names[0]; `top` builds the flag added for a rung (name -> effect)."""
    out = top(names[0])
    for k in range(len(names) - 1):
        out = sw(names[k], combine(*rm(names[k]), top(names[k + 1])), out)
    return sw(names[-1], last or NONE, out)


def build(p, native=False):
    # ------------------------------------------------------------------ passive: Ionian Fervor
    pv = [f"pv{k}" for k in range(1, p["p_n"] + 1)]

    def rung(name):
        k = pv.index(name) + 1
        out = flag(name, p["p_t"], attack_speed_mult=p["p_as"] * k)
        if k == len(pv):
            return combine(out, sfx("p_max"))
        return out

    climb = ladder(pv, rung, last=refresh(pv[-1], p["p_t"], attack_speed_mult=p["p_as"] * len(pv)))

    def mark():
        """On a champion hit: the mark's picture on it, the caster flag Q reads, a passive rung."""
        if native:     # the add-on reads the mark on the target itself
            return combine(buff("mark", p["mark_t"]), climb)
        return combine(buff("mark", p["mark_t"]), refresh("mk", p["mark_t"]), climb)

    # ------------------------------------------------------------------ Q Bladesurge
    # the landing lays flags only; the poll on her reads them (one copy of the ladder and the kill check in the tree)
    q_hit = [attack(p["q_dmg"], p["q_ratio"]), heal(p["q_heal"], p["q_heal_r"]), view("q_hit"), tsfx("q_hit"),
             refresh("q_land", 4)]
    if not native:     # a kill opens one more dash (league_jinx's kill trigger: q_k outlives q_kt only on a dead target)
        q_hit += [refresh("q_k", p["q_k"]), refresh("q_kt", 5), casted(3, 1, *rm("q_k"), kind="Poison")]

    def dash():
        return combine(anim("skill", p["q_dur"]), sfx("q_cast"), refresh("q_dash", p["q_dur"] + p["q_gap"]),
                       {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] * 2, "end_effects": q_hit})

    qn = [f"qn{k}" for k in range(2, p["q_n"] + 1)]
    again = combine(*rm("q_again", "q_aim"), sfx("q_reset"),
                    pick(p["q_range"], "EnemyChampionInCC", flag("q_aim", 1), dash()),
                    sw("q_aim", NONE, combine(pick(p["q_range"], "EnemyChampion", flag("q_aim", 1), dash()),
                                              sw("q_aim", NONE, pick(p["q_range"], "EnemyWithoutTower", dash())))),
                    *rm("q_aim"))
    # the poll: a landing climbs a rung, a kill opens q_again, spent once the dash has landed (at most q_n a cast)
    poll = combine(sw("q_land", combine(*rm("q_land"), climb)),
                   sw("q_kt", NONE, sw("q_k", combine(*rm("q_k"), refresh("q_again", p["q_poll"])))),
                   sw("q_again", sw("q_dash", NONE, ladder(qn, lambda q: combine(flag(q, p["q_poll"]), again),
                                                            last=combine(*rm("q_again"))))))

    def q_fire():
        out = [refresh("q_cd", p["q_cd"]), *rm("q_again", "q_k", *qn), voice("vo_q", p)]
        if not native:     # a mark she laid is spent on a champion in reach: one more dash
            out.append(sw("mk", combine(*rm("u1"), around(p["q_range"], "EnemyChampion", [refresh("u1", 2)]),
                                        sw("u1", combine(*rm("mk", "u1"), refresh("q_again", p["q_poll"]))))))
        out += [dash(), on_me(casted(p["q_poll"], 3, poll))]
        return combine(*out)

    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q_fire()))

    # ------------------------------------------------------------------ skill2: E Flawless Duet / W Defiant Dance
    def e_fire():
        stun = [attack(p["e_dmg"], p["e_ratio"]), {"type": "Stun", "duration": p["e_stun"]},
                buff("e_stun", p["e_stun"]), view("e_hit"), tsfx("e_hit")]
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e_cast"), voice("vo_e", p),
                       cview("e_cast"), delayed(p["e_rel"] - 4, sfx("e_stop")),
                       strip("e_line", p["e_len"], p["e_w"], p["e_rel"] + 6, p["e_rel"], "EnemyWithoutTower", stun),
                       strip("e_mark", p["e_len"], p["e_w"], p["e_rel"] + 1, p["e_rel"], "EnemyChampion", [mark()]))

    def w_fire():
        hit = [attack(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")]
        return combine(refresh("w_cd", p["w_cd"]), anim("skill2_w", p["w_dur"]), sfx("w_cast"), voice("vo_w", p),
                       refresh("w_on", p["w_charge"], base_attack_damaged_reduce=p["w_dr"]),
                       delayed(p["w_charge"], sfx("w_slash"), cview("w_slash"),
                               strip("w_line", p["w_len"], p["w_w"], 4, 2, "EnemyWithoutTower", hit),
                               strip("w_champ", p["w_len"], p["w_w"], 3, 2, "EnemyChampion", [climb])))

    w_try = sw("w_cd", NONE, w_fire())
    skill2 = action("skill2", p["e_dur"], p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    sw("e_cd", w_try, e_fire()))

    # ------------------------------------------------------------------ R Vanguard's Edge
    burst = cone("r_burst", p["r_cone"], p["r_cos"], 4, 2, "EnemyWithoutTower",
                 [attack(p["r_dmg"], p["r_ratio"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
                  {"type": "BlockAttack", "tick": p["r_dis"]}, view("r_hit")])
    burst_c = cone("r_mark", p["r_cone"], p["r_cos"], 3, 2, "EnemyChampion", [mark()])
    wall = zone("r_wall", p["r_wall"], p["r_wall_t"], p["r_wper"], "EnemyWithoutTower",
                [buff("r_wslow", p["r_wper"] + 6, move_speed_mult=-p["r_wslow"])])
    volley = line("r_blades", p["r_speed"], p["r_range"], p["r_r"], 0, "EnemyChampion", False,
                  [tsfx("r_hit")], end=[burst, burst_c, wall, view("r_wall_v"), sfx("r_wall")])

    def count():
        """The 2-tick flag rg: two enemy champions within r_count (u1 -> rg) or one in crowd control."""
        return combine(*rm("u1", "rg"),
                       around(p["r_count"], "EnemyChampion", [sw("u1", refresh("rg", 2), refresh("u1", 2))]),
                       around(p["r_count"], "EnemyChampionInCC", [refresh("rg", 2)]))

    def fire(slot):
        out = [*rm("r_armed", "u1", "rg"), voice("vo_r", p), sfx("r_cast"), anim("ult", p["r_anim"]),
               delayed(p["r_rel"], pick(p["r_range"], "EnemyChampion", sfx("r_launch"), volley))]
        if slot:     # R -> E (E's own Q follows)
            out.append(delayed(p["r_anim"], sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion", e_fire()))))
        return combine(*out)

    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(count(), sw("rg", fire(True), arm)))

    # armed: two champions or a crowd-controlled one fire it from an attack, or one in reach after r_hold ticks
    go = sw("r_armed", combine(count(), sw("r_wait", NONE, pick(p["r_reach"], "EnemyChampion", refresh("rg", 2))),
                               sw("rg", fire(False))))

    # ------------------------------------------------------------------ attack
    swing = combine(sfx("swing"), attack(0, 100), view("a_hit"), tsfx("hit"),
                    sw(pv[-1], combine(attack(p["p_dmg"], p["p_ratio"]), view("p_hit"))), go)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", swing,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # E's and W's lines and R's volley are pictures turned with the cast: drawn top-bottom symmetric; marks, hits and
    # buffs left-right symmetric; R's wall a ViewEffect on the stop point (never turned); E's throw a caster picture
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("e_line", BIG, 2), P_("w_line", BIG, 2), P_("r_blades", BIG, 2)]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("e_cast", FX, 3), E("e_hit"), E("w_slash", BIG, 2, **LATE),
               E("w_hit"), E("r_hit"), E("r_wall_v", BIG, -1, **LATE)]
    views_b = [B_(pv[-1], FX, 3), B_("mark", FX, 3), B_("e_stun", FX, 3), B_("w_on", FX, 3), B_("r_slow", FX, -1),
               B_("r_wslow", FX, -1)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_irelia:surge",
                          "params": {"poll": p["q_poll"], "q_dmg": p["q_dmg"], "q_ratio": p["q_ratio"],
                                     "q_range": p["q_range"], "q_dur": p["q_dur"], "hop": 1,
                                     "hop_reach": p["q_range"] * 2, "hop_hp": 40}}
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
    ap_.add_argument("--set", nargs="*", default=[])
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (addons/league_irelia/make_override.py)")
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
