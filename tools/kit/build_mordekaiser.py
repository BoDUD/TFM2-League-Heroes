"""Build league_mordekaiser.data_champion (top, melee AP fighter) from the parameters P.

    python tools/kit/build_mordekaiser.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-12, all the recommended options: top / melee AP fighter; Q as skill, E with W folded in
as skill2, R a cursed duel (stats stolen, a taunt, a tether), the passive in the main pack, the pros' combos, a native
add-on addons/league_mordekaiser for the real 10% steal, the tether and W's real damage-to-shield):
  passive Darkness Rise (黑暗起兮): his attacks, Q and E hitting an enemy champion stack it (p_s1 -> p_s2 -> p_on, each
          p_t ticks, renewed by every hit). At three (p_on) he moves p_ms% faster and burns the enemies round him: a
          train of pulses (league_amumu's Despair way: every action starts one unless one runs; each pulse asks whether
          he lives and whether p_on still holds) every p_per ticks deals p_dmg + p_ap% AP + p_hp% of his max health
          magic within p_r (the train starts with his next action after the third stack). His attacks deal a_ap% AP magic on top (League's 40%). E's passive, magic penetration
          (League 2.5-17.5%), is a permanent caster buff p_pen.
  attack  A mace swing, the hit a_st ticks in: 100% AD physical + a_ap% AP magic; a champion-only twin stacks the passive.
  skill   Q Obliterate (破灭之锤): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too): q_at ticks in
          the mace slams a line from him through the target (q_len, half-width q_w). A counting line on the same tick
          sets q_i1, then q_i2 for a second unit hit; the damage line a tick later reads them: q_dmg + q_ap% AP magic,
          or alone (League's isolation: one enemy hit) q_iso_dmg + q_iso_ap% AP. A champion hit stacks the passive.
          Its pictures stand upright on points of the line, never turned (Q_STAMPS, tools/art/fx_mordekaiser_q.py):
          the blow where the mace head lands, three eruptions back along the line a tick apart.
  skill2  E Death's Grasp (断魂一扼) with W Indestructible (不坏之身) folded in on its own cooldown: a `Targeting` cast on
          `EnemyChampion` (e_range) whose own cooldown s2_cd is short; the caster flags e_cd / w_cd are the real
          cooldowns (league_corki's E/W). E: e_at ticks in a claw line from him through the target (e_len, e_w) deals
          e_dmg + e_ap% AP magic and drags every enemy on it to him (`Grab`, e_pull a tick, stopping at him); a
          champion hit stacks the passive and opens e_combo. E cooling down and an enemy champion within w_trig: W, a
          shield of w_sh + w_ap% AP for w_t ticks; w_heal_at ticks in, while that shield still holds, he consumes it
          for a heal of w_heal + w_heal_ap% AP (League: a share of what is left; the data reads no shield amount).
  ult     R Realm of Death (轮回绝境): a `Targeting` cast on `EnemyChampion` (r_range). r_at ticks in the target is
          cursed for r_t ticks (League's 7 s realm): it loses r_steal% attack, ability power, armour, magic resistance
          and max health and he gains r_ad attack, r_mp ability power, r_def armour, r_mr magic resistance and r_hp
          health (League steals 10%; the data cannot read the target's stats, the add-on can); no taunt (League has
          none - the user: 「嘲讽不做啊 和英雄联盟一样」); every r_per ticks an `AddCasted` on it (its effects run with him as the caster)
          lands a 1-tick zone of r_leash on the target that marks him if he stands inside - no mark means the target
          got away: it is pulled back to him (`Pull` r_pull x r_pull_t). Another `AddCasted` keeps a 2-tick flag up
          while the target lives (league_viego's window): it dying inside the realm heals him r_kill + r_kill_ap% AP
          and lets him keep the stolen stats r_keep ticks more (League: until it respawns). With native=1
          league_mordekaiser:realm takes the carry in reach into the realm instead: both banished r_t ticks (out of
          everyone's reach and sight, a vortex r_realm where they stood), the duel fought by the add-on.
  combos  E -> Q: a Q cast within e_combo of a champion dragged slams at once (q_fast: the pros chain the pull into the
          isolated slam). R -> E: an E cast within r_combo of the curse throws the claw at once. The AI's ult target
          is its own; with native=1 league_mordekaiser:realm picks the enemy carry (the highest attack + ability power).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_mordekaiser.data_champion")
ID = "league_mordekaiser"
FX = "asset/league/effects/league_mordekaiser_fx"
BIG = "asset/league/effects/league_mordekaiser_big"

# Timings fitted to the frames (tools/art/rig_mordekaiser.py): the swing's hit on tick 10 of 24 (the strike frame), Q's
# slam on 10 of 26, E's claw on 8 of 24 (the grasp held 3-19), R's curse on 8 of 30.
# Numbers = d8 of the balance runs (Temp/mk_sim, kd.py 600 24 --lane 0 against fighter, executioner, lancer,
# pole_warrior, knight and berserker): +1.60 on seeds 1-24 against league_irelia +1.67, league_renekton +1.78,
# league_gwen +1.33. History: d0 (with R's taunt) +1.98 / +2.71; d1 (hp 980, shield 50, heal 30) +1.11 / +1.42; the
# taunt taken out (the user: 「嘲讽不做啊 和英雄联盟一样」) d5 +0.41 / +0.44; d7 (d0's numbers) +1.34; d8 = d7 + Q 80 (112).
P = {
    # stats (a melee fighter like league_renekton / league_darius / league_gwen, with ability power growth):
    # League's Mordekaiser 645 +104 hp, 61 AD, 37 armour, 32 mr, 335 move, 175 range, AS 0.625
    "hp": 1040, "hp_g": 104, "atk": 74, "atk_g": 9, "mp": 50, "mp_g": 20, "def": 32, "def_g": 8, "mr": 25, "mr_g": 4,
    "ms": 980, "ms_g": 11,
    # attack (League: +40% AP magic on hit from Darkness Rise)
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 64, "a_st": 10, "a_ap": 40,
    # passive Darkness Rise (League: 3 stacks from champion hits, 4 s; aura r 375 every second 5-? + 30% AP + 1-5%
    # max health magic, +3% move speed)
    "p_t": 240, "p_ms": 3, "p_per": 30, "p_train": 120, "p_r": 24000, "p_dmg": 4, "p_ap": 15, "p_hp": 1,
    "p_pen": 10,
    # Q Obliterate (League: 625 long, 160 wide, 45-255 + 70% AP, isolated +25..55%, cd 8-4 s)
    "q_cd": 360, "q_range": 38000, "q_dur": 26, "q_at": 10, "q_fast": 2, "q_len": 42000, "q_w": 6000,
    "q_dmg": 80, "q_ap": 70, "q_iso_dmg": 112, "q_iso_ap": 98,
    # E Death's Grasp (League: 700 range, 40-160 + 60% AP, pull, cd 18-10 s)
    "s2_cd": 120, "s2_dur": 2, "e_cd": 780, "e_range": 50000, "e_dur": 24, "e_at": 8, "e_len": 54000, "e_w": 6000,
    "e_dmg": 60, "e_ap": 60, "e_pull": 3000, "e_combo": 120,
    # W Indestructible (League: shield from damage dealt and taken up to 30% max health, recast heals 32.5-47.5% of
    # what is left, cd 12-8 s)
    "w_trig": 40000, "w_cd": 720, "w_dur": 20, "w_sh": 70, "w_ap": 60, "w_t": 180, "w_heal_at": 150,
    "w_heal": 40, "w_heal_ap": 40,
    # R Realm of Death (League: 650 range, 7 s, steals 10% of the target's stats, cd 140-80 s)
    "r_cd": 3600, "r_range": 48000, "r_dur": 30, "r_at": 8, "r_t": 420, "r_steal": 10, "r_ad": 12, "r_mp": 25,
    "r_def": 8, "r_mr": 6, "r_hp": 150, "r_per": 30, "r_leash": 45000, "r_pull": 2000, "r_pull_t": 8,
    "r_kill": 150, "r_kill_ap": 50, "r_keep": 900, "r_combo": 120,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_mordekaiser: the realm's real steal, tether and target, W's real shield
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


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    if tick is None:
        dur = "Permanent"
    elif tick == "shield":
        dur = "WithShield"
    else:
        dur = {"Time": {"tick": tick}}
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


def heal(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Poison"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def strip(name, length, width, delay, apply, target, effects):
    """A line from him through the target (league_irelia E's way)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def sign(name, length, width, tick):
    """A picture along a line from him through the target that hits nothing (league_darius E's sweep): the damage
    lines live 2-3 ticks, too short to see."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": tick,
            "apply": tick, "applied_target": "EnemyWithoutTower", "applied_effects": []}


# Obliterate's pictures on the line to the target: (ticks after the slam, picture, game px ahead x 1000). The mace head
# lands 40 px ahead in his slam frame (at hd.rs SIZES 1.15); the eruptions run back toward him (the user, 2026-10-13:
# 「铁男1技能的特效感觉也不足」 - Codex's slam at his feet and its crack, a line picture turned with the cast, were small
# for him and the crack floated above the line on the red side)
Q_STAMPS = [(0, "q_slam", 40000), (0, "q_burst", 32000), (1, "q_burst", 22000), (2, "q_burst", 12000)]


def stamp(name, ahead):
    """A picture standing upright `ahead` along the line to the target, never turned (league_yasuo Q3's stamps): a
    hidden projectile that stops there on its first tick (speed over its range) and plays the picture where it
    stopped."""
    return {"type": "LinearProjectile", "name": n("q_step"), "speed": 60000, "range": ahead,
            "shape": circle(0), "penetrate": True, "y_offset": 0, "applied_target": "EnemyChampion",
            "applied_effects": [], "end_effects": [{"type": "ViewEffect", "name": n(name)}]}


def twin(target, effects):
    """A champion-only twin of a melee hit: an invisible projectile reaching the target the same tick."""
    return {"type": "TargetProjectile", "name": n("twin"), "speed": 100000, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, end):
    """A hidden 1-tick lob onto the target's current spot; its end_effects start a zone there (league_annie R)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000, "shape": circle(1000),
            "range_effect_name": "", "applied_target": "Enemy", "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lives(*effects):
    """Effects only while he lives: a dead caster adds no buff, so a 1-tick flag he adds is missing."""
    return combine(flag("lives", 1), sw("lives", combine(*effects)))


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive Darkness Rise
    def pulse():
        return lives(sw("p_on", combine(cview("p_aura"),
                                        around(p["p_r"], "EnemyWithoutTower",
                                               [magic(p["p_dmg"], p["p_ap"], p["p_hp"]), view("p_hit")]))))

    def train():
        """A run of aura pulses unless one runs (league_amumu's Despair)."""
        return sw("p_on", sw("p_train", NONE, combine(
            flag("p_train", p["p_train"]),
            *[delayed(k, pulse()) if k else pulse() for k in range(0, p["p_train"], p["p_per"])])))

    on = combine(refresh("p_on", p["p_t"], move_speed_mult=p["p_ms"]), sfx("p_on"))
    stack = on_me(sw("p_on", refresh("p_on", p["p_t"], move_speed_mult=p["p_ms"]),
                     sw("p_s2", combine(*rm("p_s1", "p_s2"), on),
                        sw("p_s1", combine(refresh("p_s1", p["p_t"]), refresh("p_s2", p["p_t"])),
                           refresh("p_s1", p["p_t"])))))
    pen = sw("p_pen", NONE, flag("p_pen", None, magic_resistance_penetration=p["p_pen"]))
    start = combine(pen, train())

    # ------------------------------------------------------------------ attack
    def hit():
        return combine(attack(0, 100), magic(0, p["a_ap"]), view("a_hit"), tsfx("a_hit"),
                       twin("EnemyChampion", [stack]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(start, sfx("a_swing"), delayed(p["a_st"] - 1, hit())), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Obliterate
    count = on_me(sw("q_i1", refresh("q_i2", 4), refresh("q_i1", 4)))
    plain = [magic(p["q_dmg"], p["q_ap"]), view("q_hit"), tsfx("q_hit")]
    lonely = [magic(p["q_iso_dmg"], p["q_iso_ap"]), view("q_iso_hit"), tsfx("q_hit")]
    slam_hit = sw("q_i2", combine(*plain), combine(*lonely))

    def slam():
        pics = [delayed(t, stamp(name, ahead)) if t else stamp(name, ahead) for t, name, ahead in Q_STAMPS]
        return combine(sfx("q"), *pics,
                       strip("q_count", p["q_len"], p["q_w"], 2, 1, "EnemyWithoutTower", [count]),
                       strip("q_line", p["q_len"], p["q_w"], 3, 2, "EnemyWithoutTower", [slam_hit]),
                       strip("q_champ", p["q_len"], p["q_w"], 3, 2, "EnemyChampion", [stack]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(start, *rm("q_i1", "q_i2"), voice("vo_q", p),
                           sw("e_combo", combine(*rm("e_combo"), delayed(p["q_fast"] - 1, slam())),
                              delayed(p["q_at"] - 1, slam()))))

    # ------------------------------------------------------------------ skill2: E Death's Grasp / W Indestructible
    grasp_hits = [magic(p["e_dmg"], p["e_ap"]), {"type": "Grab", "speed": p["e_pull"]}, view("e_hit"), tsfx("e_hit")]

    def claw():
        return combine(sfx("e"), sign("e_beam", p["e_len"], p["e_w"], 18),
                       strip("e_line", p["e_len"], p["e_w"], 6, 2, "EnemyWithoutTower", grasp_hits),
                       strip("e_champ", p["e_len"], p["e_w"], 3, 2, "EnemyChampion",
                             [stack, on_me(refresh("e_combo", p["e_combo"]))]))

    def e_fire():
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), voice("vo_e", p),
                       sw("r_combo", combine(*rm("r_combo"), claw()), delayed(p["e_at"] - 1, claw())))

    def w_fire():
        shield = {"type": "Shield", "amount": p["w_sh"], "attack_ratio": 0, "ap_ratio": p["w_ap"], "tick": p["w_t"]}
        if native:
            guard = {"type": "Native", "effect_ref": "league_mordekaiser:indestructible"}
        else:
            guard = combine(on_me(shield), refresh("w_on", "shield"),
                            delayed(p["w_t"], *rm("w_on")),
                            delayed(p["w_heal_at"], sw("w_on", combine(heal(p["w_heal"], p["w_heal_ap"]),
                                                                       cview("w_heal"), sfx("w_heal")))))
        return combine(refresh("w_cd", p["w_cd"]), anim("skill2_w", p["w_dur"]), sfx("w"), voice("vo_w", p),
                       cview("w_shield"), guard)

    w_try = sw("w_cd", NONE, pick(p["w_trig"], "EnemyChampion", w_fire()))
    skill2 = action("skill2", p["s2_dur"], p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(start, sw("e_cd", w_try, e_fire())))

    # ------------------------------------------------------------------ ult: R Realm of Death
    s = p["r_steal"]
    curse = buff("r_curse", p["r_t"], attack_mult=-s, magic_power_mult=-s, defence_mult=-s,
                 magic_resistance_mult=-s, hp_mult=-s)
    gain = dict(attack=p["r_ad"], magic_power=p["r_mp"], defence=p["r_def"], magic_resistance=p["r_mr"], hp=p["r_hp"])
    leash = casted(p["r_t"], p["r_per"], lives(
        lob("r_probe", [zone("r_leash", p["r_leash"], "AllyOnlySelf", [refresh("r_near", 3)])]),
        delayed(3, sw("r_near", combine(*rm("r_near")),
                      combine({"type": "Pull", "speed": p["r_pull"], "tick": p["r_pull_t"]}, view("r_pull"))))))
    alive = casted(p["r_t"], 1, refresh("r_alive", 2), kind="Bleed")
    won = combine(flag("r_won", p["r_t"]), heal(p["r_kill"], p["r_kill_ap"]), cview("r_win"), sfx("r_win"),
                  refresh("r_keep", p["r_keep"], **gain))
    watch = on_me(delayed(2, casted(p["r_t"] - 4, 1, sw("r_alive", NONE, sw("r_won", NONE, won)))))
    if native:
        realm = combine({"type": "Native", "effect_ref": "league_mordekaiser:realm"}, view("r_mark"))
    else:
        realm = combine(curse, view("r_mark"), leash, alive,
                        on_me(refresh("r_steal", p["r_t"], **gain), *rm("r_won")), watch)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(start, voice("vo_r", p),
                         delayed(p["r_at"] - 1, sfx("r"), cview("r_cast"), realm,
                                 on_me(refresh("r_combo", p["r_combo"])))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("e_beam", BIG, 2)]
    views_e = [E("a_hit"), E("p_aura", BIG, -1), E("p_hit"), E("q_slam", BIG, 1, False), E("q_burst", BIG, 1, False), E("q_hit"),
               E("q_iso_hit"), E("e_hit"), E("w_shield"), E("w_heal"), E("r_cast", BIG, 2, False), E("r_mark"), E("r_realm", BIG, -1, False), E("r_realm_loop", BIG, -1, False),
               E("r_pull"), E("r_win")]
    views_b = [B_("r_curse", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Shield", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_mordekaiser:revenant",
                          "params": {"kill": p["r_kill"], "kill_ap": p["r_kill_ap"], "keep": p["r_keep"],
                                     "w_dealt": 45, "w_taken": 15, "w_cap": 30, "w_heal": 40}}
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (native=1)")
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
