"""Build league_rell.data_champion (support, Util tank, magic skills) from the parameters P.

    python tools/kit/build_rell.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-16: support, the main pack plus a native add-on addons/league_rell, PPU 1.5, every
recommended option - 「方案可以」). League's V26 Rell: Break the Mold, Shattering Strike, Ferromancy (Crash Down / Mount
Up), Full Tilt, Magnet Storm. The main pack draws her mounted (idle and run cannot change at runtime, form-switch-limits);
on foot is a state with its own armour picture; the add-on swaps the whole body while she is on foot.
  passive Break the Mold (溃敌沉力): every attack and ability that hits an enemy champion (champion-only twins) leaves a
          p_t-tick mark taking p_shred% of its armour and magic resistance, and gives her p_steal of each for as long
          (instances add up: at her attack rate about four or five live at once, League's cap of five). Her attacks
          also deal p_dmg + p_ap% AP + p_hp% of her maximum health as magic damage (League: a share of her armour and
          magic resistance - nothing in the data reads armour, so the tank stat it can read).
  attack  A lance thrust, slow (atk_cd: League's 0.625), the hit on atk_st. With e_ready the blow explodes (E).
  skill   Q Shattering Strike (裂阵) and E Full Tilt (全速冲锋) share the slot, each on its own cooldown (caster flags q_cd
          and e_cd; the slot waits only s1_cd). A `Targeting` cast on `EnemyWithoutTower` (e_trig):
          - E ready, the target a champion and an allied champion within e_ally: she and one allied champion near her
            gain e_ms1% move speed for e_t1 ticks, then e_ms2% for e_t2 (League: 15%, 30% toward enemies or each
            other); her next attack or Q within e_ready_t explodes on what it hits: e_dmg + e_ap% AP, and on a champion
            e_pct% of its maximum health (League: 5-7% max health as magic; a share of the target's health can only be
            true damage in the data).
          - Q ready and the target within q_reach: the strike is laid at the cast toward where the target stands (a
            line q_len x q_w that hits q_at ticks later: League's 0.4 s cast, walked out of to dodge): q_dmg + q_ap%
            AP and a q_stun-tick stun on every enemy on it (League: 0.65 s). Breaking shields is the add-on's.
  skill2  W Ferromancy (驭铁术), one slot, two forms (the `foot` flag). A `Targeting` cast on `EnemyChampion` (w_range):
          - Mounted, Crash Down (轰落): only with an allied champion within w_ally or the champion already within
            w_close of her (the moment: no lone dives). She leaps onto it (w_jump, then MoveToTarget w_speed) and
            crashes down: w_dmg + w_ap% AP and w_up ticks airborne on every enemy within w_r, a w_sh + w_sh_ap% AP shield
            for w_sh_t; then she is on foot for w_foot ticks: f_def% armour, f_mr% magic resistance, f_as% attack
            speed, f_range attack range, f_ms% move speed (League: +15% / +15% / +20% / +75, the mounted speed lost).
          - On foot, Mount Up (上马): the horse forms again (w2_ms% move speed for w2_ms_t), she charges the champion
            (MoveToTarget w2_speed): w2_dmg + w2_ap% AP, a w2_stun-tick stun and a fling (Knockback w2_kb_speed x
            w2_kb_t) (League: the next attack's charge, 0.6 s stun, 150 units). The foot state also ends by itself after
            w_foot ticks (she mounts without the charge).
          The game's AI scores the branch the flags pick between ticks (league_orianna 2026-10-16): the gate's flags are
          never there then, so the slot's scored branch is Crash Down's shield (w_x trick); Mount Up carries its damage.
  ult     R Magnet Storm (极涌), armed like league_pantheon R: the slot arms r_arm ticks; a poll every r_poll ticks fires
          it when r_need enemy champions are within r_r, or one in crowd control is with an allied champion within
          r_ally of her - and she is not in crowd control. Then she yanks every enemy within r_r to her (Grab r_yank)
          and for r_n pulses r_period apart drags them in (Grab r_drag x r_drag_t) and deals r_tick + r_tick_ap% AP
          (League: 2 s, 150-350 + 110% AP). Unused, the window ends with the cooldown capped (r_reset).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_rell.data_champion")
ID = "league_rell"
FX = "asset/league/effects/league_rell_fx"
BIG = "asset/league/effects/league_rell_big"

# Numbers: the first draft from League's ratios inside the pack's tank supports (league_alistar, league_braum,
# league_leona); balance from the 10-min classic-SDK simulations (Temp/rl_sim/sim/kd.py --lane 4 against the base
# priest, monk, bard, pythoness and spirit caller, three lineups, both sides, 2026-10-16): the draft r1 (hp 1150, atk 72,
# an attack every 90 ticks, Q / W 70, R 30 a pulse, W 36000 / 600) -1.32 on seeds 1-8 (league_alistar +0.27) - she
# attacked 68 times in a logged game against Alistar's 101 and crashed down 8 times; r2a (attack every 80, W 45000 /
# 480) -0.81; r2b (here: r2a + hp 1200, atk 76, Q / W 80, R 35) +1.13 on seeds 1-8, +0.05 on 9-24 (league_alistar
# +0.13; r2c with Q / W 75, R 32, atk 74 -0.56).
P = {
    # stats (league_alistar hp 1100 +120, def 38, mr 28, atk 80, interval 80; League's Rell: 620 +104 hp, 55 AD,
    # 30 +4 armour, 28 mr, 315 move, 175 range, 0.625 attacks a second)
    "hp": 1200, "hp_g": 120, "atk": 76, "atk_g": 6, "mp": 25, "mp_g": 15, "def": 40, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1010, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 80, "atk_st": 14,
    # passive Break the Mold (League: 3% armour / mr a stack, 5 stacks 5 s, hers as bonus resists; on-hit 5% of resists)
    "p_t": 300, "p_shred": 3, "p_steal": 3, "p_dmg": 6, "p_ap": 10, "p_hp": 1,
    # skill slot: Q + E
    # Q Shattering Strike (League: 520 forward, 150 wide, 0.4 s, 60-220 + 60% AP, stun 0.65 s, cd 11-9 s)
    "q_cd": 600, "q_reach": 38000, "q_len": 42000, "q_w": 5000, "q_at": 24, "q_anim": 30, "q_dmg": 80, "q_ap": 60,
    "q_stun": 39, "q_tail": 15,
    # E Full Tilt (League: 15% / 30% 3 s, next attack or Q within 5 s 5-7% max health, cd 14-10 s)
    "e_cd": 720, "e_ally": 60000, "e_ms1": 15, "e_t1": 60, "e_ms2": 30, "e_t2": 120,
    "e_ready_t": 300, "e_dmg": 20, "e_ap": 20, "e_pct": 5, "e_anim": 12,
    # W Crash Down (League: 450 range, 0.625 s, 60-180 + 60% AP, stun 0.8 + knock-up 0.4 s, shield 20-100 + 11% max hp)
    "w_cd": 480, "w_range": 45000, "w_ally": 50000, "w_close": 22000, "w_jump": 10, "w_speed": 3000, "w_r": 24000,
    "w_dmg": 80, "w_ap": 60, "w_up": 50, "w_sh": 90, "w_sh_ap": 40, "w_sh_t": 240, "w_anim": 38,
    "w_foot": 900, "f_def": 15, "f_mr": 15, "f_as": 20, "f_range": 6000, "f_ms": -8,
    # W Mount Up (League: 30% speed decaying 2 s, the charge: 10-70 + 40% AP, stun 0.6 s, fling 150)
    "w2_speed": 3500, "w2_dmg": 40, "w2_ap": 40, "w2_stun": 36, "w2_kb_speed": 1500, "w2_kb_t": 6, "w2_ms": 30,
    "w2_ms_t": 120, "w2_anim": 20,
    # R Magnet Storm (League: radius 450, pull, 2 s drag, 150-350 + 110% AP over 8 ticks, cd 120-80 s)
    "r_cd": 3600, "r_arm": 600, "r_poll": 10, "r_r": 34000, "r_need": 2, "r_ally": 50000, "r_anim": 30,
    "r_yank": 2000, "r_n": 8, "r_period": 15, "r_tick": 35, "r_tick_ap": 14, "r_drag": 500, "r_drag_t": 10,
    "r_reset": 4900,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_rell (the body swap on foot, shield breaking, per-champion stacks)
    "native": 0,
    # 1 = slot actions named skill2 / ult instead of idle (simulation logs only: the sheet has no such tags)
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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def true_pct(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


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


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def strike(name, length, width, apply, target, effects, tail=1):
    """A line laid now from her toward the target, hitting `apply - 1` ticks later (the aim locked at the cast), gone
    `tail` ticks after the hit (its picture plays the strike out meanwhile)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": apply + tail,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


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
    nat = bool(p["native"])

    # ------------------------------------------------------------------ passive: Break the Mold (on a champion hit)
    mold = [buff("p_shred", p["p_t"], defence_mult=-p["p_shred"], magic_resistance_mult=-p["p_shred"]),
            on_me(flag("p_steal", p["p_t"], defence=p["p_steal"], magic_resistance=p["p_steal"]))]
    if nat:   # the add-on keeps five stacks on each champion and snapshots its resists (League's rule)
        mold = [{"type": "Native", "effect_ref": f"{ID}:mold"}]
    # E's blast, on whatever the empowered attack or Q hits (the champion part through the champion-only twin)
    # (every unit Q's line strikes is blasted; e_ready goes 3 ticks after the blow, once the twin has hit too)
    blast = sw("e_ready", combine(magic(p["e_dmg"], p["e_ap"]), view("e_boom"), tsfx("e_boom")))
    blast_champ = sw("e_ready", true_pct(p["e_pct"]))
    spent = sw("e_ready", on_me(delayed(3, *rm("e_ready"))))

    # ------------------------------------------------------------------ attack
    twin = homing("a_twin", 1000000, "EnemyChampion", [*mold, blast_champ])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), twin, attack(0, 100), magic(p["p_dmg"], p["p_ap"], p["p_hp"]), blast,
                              spent, view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Shattering Strike + E Full Tilt
    q_hits = [magic(p["q_dmg"], p["q_ap"]), {"type": "Stun", "duration": p["q_stun"]}, buff("q_stun", p["q_stun"]),
              view("q_hit"), tsfx("q_hit")]
    if nat:
        q_hits.append({"type": "Native", "effect_ref": f"{ID}:shatter"})
    q_go = combine(sfx("q"), voice("vo_q", p),
                   strike("q_line", p["q_len"], p["q_w"], p["q_at"], "EnemyWithoutTower", [*q_hits, blast], p["q_tail"]),
                   strike("q_twin", p["q_len"], p["q_w"], p["q_at"], "EnemyChampion", [*mold, blast_champ]),
                   delayed(p["q_at"], spent))
    # the ramp (League: doubled toward enemies or each other); with native=1 the add-on adds the second half only while
    # they run toward them, so the copy keeps e_ms1 all along
    ms2 = p["e_ms1"] if nat else p["e_ms2"]
    haste = [buff("e_ms", p["e_t1"], move_speed_mult=p["e_ms1"]),
             delayed(p["e_t1"], buff("e_ms2", p["e_t2"], move_speed_mult=ms2))]
    e_go = combine(flag("e_cd", p["e_cd"]), refresh("e_ready", p["e_ready_t"]), cview("e_cast"), sfx("e"),
                   voice("vo_e", p),
                   on_me(refresh("e_ms", p["e_t1"], move_speed_mult=p["e_ms1"]),
                         delayed(p["e_t1"], refresh("e_ms2", p["e_t2"], move_speed_mult=ms2))),
                   pick(p["e_ally"], "AllyNotSelf", *haste))
    # E rides the cast when the target is a champion and an allied champion is near her (the probe hits the same tick)
    probe_c = homing("e_probe", 1000000, "EnemyChampion", [pick(p["e_ally"], "AllyNotSelf", refresh("e_ok", 3))])
    e_try = sw("e_cd", NONE, combine(*rm("e_ok"), probe_c, delayed(2, lives(sw("e_ok", e_go), *rm("e_ok")))))
    skill = action("skill", p["q_anim"], p["q_cd"], 1, p["q_reach"], "Targeting", "EnemyWithoutTower",
                   combine(e_try, q_go))

    # ------------------------------------------------------------------ skill2: W Crash Down / Mount Up
    foot_stats = dict(defence_mult=p["f_def"], magic_resistance_mult=p["f_mr"], attack_speed_mult=p["f_as"],
                      range=p["f_range"], move_speed_mult=p["f_ms"])
    crash = [view("w_crash"), sfx("w_land"),
             around(p["w_r"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_ap"]),
                                                    {"type": "Airborne", "duration": p["w_up"]}, view("w_hit")]),
             around(p["w_r"], "EnemyChampion", mold),
             on_me(shield(p["w_sh"], p["w_sh_ap"], p["w_sh_t"]), refresh("w_shield", p["w_sh_t"]),
                   refresh("foot", p["w_foot"], **foot_stats))]
    w1 = combine(anim("skill2", p["w_anim"]), cview("w_jump"), sfx("w"), voice("vo_w", p),
                 delayed(p["w_jump"], lives({"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"] + 40000,
                                             "end_effects": crash})))
    # the gate: an allied champion near her, or the champion already close (the probe's hit asks); either raises w_ok
    w_probe = homing("w_probe", 1000000, "EnemyChampion",
                     [pick(p["w_close"], "AllyOnlySelf", refresh("w_ok", 3), fp=True)])
    w1_try = combine(*rm("w_ok"), w_probe, pick(p["w_ally"], "AllyNotSelf", refresh("w_ok", 3)),
                     delayed(2, lives(sw("w_ok", w1), *rm("w_ok"))))
    charge = [magic(p["w2_dmg"], p["w2_ap"]), {"type": "Stun", "duration": p["w2_stun"]},
              {"type": "Knockback", "speed": p["w2_kb_speed"], "tick": p["w2_kb_t"]}, buff("w2_stun", p["w2_stun"]),
              view("w2_hit"), tsfx("w2_hit"), *mold, blast, blast_champ, spent]
    w2 = combine(*rm("foot"), anim("skill2_up", p["w2_anim"]), cview("w2_mount"), sfx("w2"), voice("vo_w2", p),
                 on_me(refresh("w2_ms", p["w2_ms_t"], move_speed_mult=p["w2_ms"])),
                 {"type": "MoveToTarget", "speed": p["w2_speed"], "range": p["w_range"] + 40000, "end_effects": charge})
    real2 = sw("foot", w2, w1_try)
    score2 = sw("foot", magic(p["w2_dmg"], p["w2_ap"]), on_me(shield(p["w_sh"], p["w_sh_ap"], p["w_sh_t"])))
    skill2 = action("skill2" if p["dbg"] else "idle", 3, p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(flag("w_x", 1), sw("w_x", combine(*rm("w_x"), real2), score2), *rm("w_x")), key="skill2")

    # ------------------------------------------------------------------ ult: R Magnet Storm (armed)
    pulse = lives(around(p["r_r"], "EnemyWithoutTower",
                         [magic(p["r_tick"], p["r_tick_ap"]),
                          {"type": "Grab", "speed": p["r_drag"], "tick": p["r_drag_t"]}, view("r_hit")]))
    fire = combine(*rm("r_arm"), anim("ult", p["r_anim"]), cview("r_cast"), sfx("r"), voice("vo_r", p),
                   around(p["r_r"], "EnemyWithoutTower", [{"type": "Grab", "speed": p["r_yank"]}, view("r_yank")]),
                   around(p["r_r"], "EnemyChampion", mold),
                   refresh("r_on", p["r_n"] * p["r_period"]),
                   on_me(casted(p["r_n"] * p["r_period"], p["r_period"], pulse)))
    count = combine(*rm("c1", "c2", "r_cc", "r_al", "r_me"),
                    around(p["r_r"], "EnemyChampion", [sw("c1", flag("c2", 1), flag("c1", 1))]),
                    pick(p["r_r"], "EnemyChampionInCC", flag("r_cc", 1)),
                    pick(p["r_ally"], "AllyNotSelf", flag("r_al", 1)),
                    pick(1, "AllyChampionInCC", flag("r_me", 1)),
                    sw("r_me", NONE, sw("c2", fire, sw("r_cc", sw("r_al", fire)))),
                    *rm("c1", "c2", "r_cc", "r_al", "r_me"))
    poll = sw("r_arm", count)
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_reset", 3, ult_cooldown_mult=p["r_reset"])))
    ult = action("ult" if p["dbg"] else "idle", 3, p["r_cd"], 1, p["r_r"] + 30000, "None", "EnemyChampion",
                 combine(refresh("r_arm", p["r_arm"]), poll,
                         on_me(casted(p["r_arm"], p["r_poll"], poll), delayed(p["r_arm"], reset))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the strike's picture plays once over the line's life (q_at + q_tail ticks: the guide, the strike on 0.38 s, the shards)
    views_p = [{**P_("q_line", BIG, 2), "repeat": False}]
    views_e = [E("a_hit"), E("q_hit"), E("e_cast", FX, 3), E("e_boom"), E("w_jump", BIG, 1, True),
               E("w_crash", BIG, -1, False), E("w_hit"), E("w2_mount", FX, 3), E("w2_hit"), E("r_cast", BIG, -1),
               E("r_yank"), E("r_hit")]
    views_b = [B_("p_shred", FX, 3), B_("q_stun", FX, 3), B_("w2_stun", FX, 3, "q_stun"), B_("e_ms", FX, -1),
               B_("e_ms2", FX, -1, "e_ms"), B_("e_ready", FX, 3), B_("w_shield", FX, 3), B_("foot", FX, 2),
               B_("r_on", BIG, -1)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if nat:
        kit["passive"] = {"passive_ref": f"{ID}:iron",
                          "params": {"p_t": p["p_t"], "p_shred": p["p_shred"], "p_steal": p["p_steal"],
                                     "e_toward": p["e_ms2"] - p["e_ms1"], "r_r": p["r_r"]}}
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
