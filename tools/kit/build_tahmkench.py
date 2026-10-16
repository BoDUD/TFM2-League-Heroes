"""Build league_tahmkench.data_champion (support, Melee tank) from the parameters P.

    python tools/kit/build_tahmkench.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-15: support tank; League's current layout - Q Tongue Lash as skill, W Abyssal Dive as
skill2, R Devour as the ult, E Thick Skin folded into the passive; R saves an ally only when he is in danger
(「塔姆的R救队友的时候灵活判断 别乱放」); a native add-on addons/league_tahmkench):
  passive An Acquired Taste (培养品味): his attacks deal p_dmg + p_hp% of his maximum health as magic damage (League:
          8-60 + 2.5% bonus health); his attacks, Tongue Lash and Abyssal Dive on enemy champions add a stack (League:
          on the champion, 3 at most, 5 s). The data reads no stacks on a target, so the count is his (league_braum's
          Concussive Blows / league_varus Blight's way): champion-only hits climb t1 -> t2 -> t3 (p_hold ticks each,
          refreshed), the pips drawn on the champion (t_pip1-3, one picture per slot: k pips at k stacks). With
          native=1 the add-on keeps the stacks on each champion.
          Thick Skin (厚实表皮, League's E: a share of the damage taken stored as grey health, healed back out of combat
          or turned into a shield): every life starts with a permanent e_red% damage reduction (the stored part); with
          two or more enemy champions within e_near when he acts and e_cd gone, the store becomes a shield
          (e_sh + e_sh_ap% AP for e_t ticks). With native=1 the add-on stores the real damage and decides.
  attack  A tongue slap (atk_range: League's 175 reach against 125), the hit on atk_st.
  skill   Q Tongue Lash (巨舌鞭笞): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too); on q_at the
          tongue leaves for where the target stood 8 ticks before (dodgeable, league_caitlyn Q's lock) and stops on the
          first unit: q_dmg + q_ap% AP + q_hp% of his maximum health, slow q_slow% for q_slow_t. When that first unit
          is a champion (a champion-only twin on the same line, its flag read a tick after the hit) he heals
          q_heal + q_heal_ap% AP and the champion gets a stack - at three stacks the tongue stuns q_stun ticks and eats
          them, unless Devour is armed (then the stacks stay for it, the pros' Q -> R).
  skill2  W Abyssal Dive (深渊潜航), only at a good moment (the user: 「W也别乱放 看好时机」): a `Targeting` cast on the
          champion his team is fighting (EnemyChampionRecentlyAttacked), never without an allied champion within
          w_ally_r: with one only when that champion is in crowd control (the knock-up chains it), with two or more
          anyway; else nothing and the slot (s2_cd) checks again. With native=1 the add-on's AI hook picks. On the chosen champion (w_range) he sinks (w_sink ticks), banished
          (nobody can target him) for w_up ticks while bubbles mark the spot where the champion stood when he went
          under, then comes up there (Teleport by a hidden lob locked at the dive): w_dmg + w_ap% AP + w_hp% of his
          maximum health and a knock-up w_air ticks round the landing (w_rad), a stack on the champions hit (one a dive).
  ult     R Devour (大快朵颐): League swallows an enemy champion at three stacks (suppressed, damaged) or an ally
          (protected, shielded). Nothing reads current health, so the slot only arms it (league_kayle R's way): a 3-tick
          cast adds r_armed (r_arm ticks), and the cast and every attack, Q and W check while it lasts:
          1. an allied champion (not him) in crowd control within r_ally_r while two or more enemy champions stand
             within r_n of him: that ally is swallowed - banished r_ally_t ticks (untargetable, no harm can reach him),
             spat out at the spot with an r_sh + r_sh_ap% AP shield (r_sh_t ticks);
          2. else with three stacks, an enemy champion his team hit recently within r_reach: swallowed - banished
             r_t ticks, r_dmg + r_ap% AP + r_hp% of his maximum health magic and r_thp% of its maximum health true
             damage, the stacks eaten;
          3. else nothing. An unused window ends with a 3-tick ult_cooldown_mult that caps the cooldown at 60 ticks.
          With native=1 the add-on's AI hook picks by real health (an ally low or bursting with enemies near, an
          enemy with three real stacks), carries the swallowed unit and spits it behind him.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_tahmkench.data_champion")
ID = "league_tahmkench"
FX = "asset/league/effects/league_tahmkench_fx"
BIG = "asset/league/effects/league_tahmkench_big"

# Timings from the frames (tools/art/rig_tahmkench.py, league/champions/league_tahmkench#anim.fanim): the slap 440 ms,
# landing on frame 3 (tick 11); Tongue Lash 450 ms, the tongue leaving on frame 4 (tick 15); the dive 400 ms, nearly
# under on frame 4 (tick 18: the banish starts there), the burst out 340 ms; the devour 500 ms.
# Numbers: the first draft from league_braum's b3 (the pack's tank supports) was -4.1 a game in the support lane (classic
# SDK, priest / monk / bard / pythoness / spirit caller, 3 lineups, both sides); the gated W and g6 (hp 1750, def 50,
# mr 32, atk 85, Q 140, W 130, passive 20 + 2%, Thick Skin 15% and a 120 shield, R 180, Q 6 s, W 15 s): -0.85 on seeds
# 1-12 (league_braum -0.21 / -0.26 in the same batches). To be re-run after the strips retime his casts.
P = {
    # stats (League's Tahm Kench: 640 +103 hp, 56 AD, 39 armour, 32 mr, 335 move, 175 range)
    "hp": 1750, "hp_g": 120, "atk": 85, "atk_g": 6, "mp": 25, "mp_g": 15, "def": 50, "def_g": 7, "mr": 32, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 28000, "atk_dur": 26, "atk_cd": 80, "atk_st": 11,
    # passive An Acquired Taste (League: 8-60 + 2.5% bonus hp on attacks; stacks 5 s, 3 at most)
    "p_dmg": 20, "p_hp": 2, "p_hold": 300,
    # Thick Skin folded in (League: 15-27% of damage stored, shield = the store, cd 3 s)
    "e_red": 15, "e_cd": 720, "e_near": 35000, "e_sh": 120, "e_sh_ap": 80, "e_t": 150,
    # Q Tongue Lash (League: 900 range, speed 2800, 80-280 + 70% AP, slow 40% 2 s, heal 10-30 + 3% missing hp on a
    # champion, stun 1.25 s at 3 stacks, cd 7-5 s)
    "q_cd": 360, "q_range": 60000, "q_dur": 27, "q_at": 15, "q_speed": 6000, "q_w": 3000, "q_dmg": 140, "q_ap": 60,
    "q_hp": 2, "q_slow": 40, "q_slow_t": 90, "q_heal": 40, "q_heal_ap": 30, "q_stun": 75,
    # W Abyssal Dive (League: 1000-1200 range, 1.35 s under, 100-250 + 100% AP, knock-up 1 s in 275, cd 21-17 s)
    "w_cd": 900, "w_range": 70000, "w_anim": 24, "w_sink": 18, "w_up": 60, "w_land": 20, "w_rad": 14000,
    "w_dmg": 130, "w_ap": 70, "w_hp": 2, "w_air": 60, "s2_cd": 60, "w_ally_r": 50000,
    # R Devour (League: enemy 2.5 s, 100-400 + 15% AP + 5-9% target max hp; ally 2.5 s, shield 400-1000 + 100% AP;
    # cd 120-80 s)
    "r_cd": 3600, "r_range": 50000, "r_arm": 900, "r_anim": 30, "r_reach": 30000, "r_ally_r": 40000, "r_n": 50000,
    "r_t": 150, "r_dmg": 180, "r_ap": 50, "r_hp": 3, "r_thp": 6,
    "r_ally_t": 150, "r_sh": 150, "r_sh_ap": 100, "r_sh_t": 180,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_tahmkench: per-champion stacks, real grey health, the devour target picked and
    # carried by the add-on
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
    """dmg + ratio% AP + hp% of HIS maximum health as magic damage."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def maxhp(pct):
    """pct% of the target's maximum health as true damage (no magic effect has a target-health part)."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def lob(name, travel, rng, target, end):
    """A hidden ParabolicProjectile onto the target's spot as it is now: its end_effects start there."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": rng,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, target, effects):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = bool(p["native"])
    h = p["p_hold"]

    # ------------------------------------------------------------------ passive: the stacks (his count) + Thick Skin
    eat = combine(*rm("t1", "t2", "t3"))

    def gulp(voice_name, sound):
        return combine(anim("ult", p["r_anim"]), cview("r_gulp"), sfx(sound), voice(voice_name, p))

    enemy_in = [{"type": "Banish", "duration": p["r_t"]}, magic(p["r_dmg"], p["r_ap"], p["r_hp"]), maxhp(p["r_thp"]),
                buff("r_enemy", p["r_t"]), view("r_in"), delayed(p["r_t"], view("r_spit"), tsfx("r_spit"))]
    # Devour armed when a hit brings the champion to three stacks (or lands on three): that very champion is eaten
    eat_here = sw("r_armed", sw("r_lock", NONE, combine(flag("r_lock", 3), *rm("r_armed"), eat,
                                                        on_me(gulp("vo_r", "r_enemy"), refresh("r_full", p["r_t"])),
                                                        *enemy_in)))
    pips = lambda k: [buff(f"t_pip{i}", h) for i in range(1, k + 1)]
    climb = sw("t3", combine(refresh("t3", h), refresh("t2", h), refresh("t1", h), *pips(3), eat_here),
               sw("t2", combine(refresh("t3", h), refresh("t2", h), refresh("t1", h), *pips(3), tsfx("p_stack"),
                                eat_here),
                  sw("t1", combine(refresh("t2", h), refresh("t1", h), *pips(2)),
                     combine(refresh("t1", h), *pips(1)))))
    if nat:     # the add-on keeps the stacks on each champion
        climb = {"type": "Native", "effect_ref": "league_tahmkench:taste"}
    # every life starts with the stored share of the damage taken off (the add-on stores the real damage instead)
    life = sw("life", NONE, combine(flag("life", None), None if nat else flag("skin", None, damaged_reduce=p["e_red"])))
    # Thick Skin's shield: two or more enemy champions close when he acts
    skin = combine(*rm("e_n1", "e_n2"),
                   around(p["e_near"], "EnemyChampion", [sw("e_n1", flag("e_n2", 3), flag("e_n1", 3))]),
                   delayed(1, sw("e_n2", combine(flag("e_cd", p["e_cd"]), on_me(shield(p["e_sh"], p["e_sh_ap"], p["e_t"])),
                                                 cview("e_shield"), sfx("e_shield"), voice("vo_e", p)))))
    skin = NONE if nat else sw("e_cd", NONE, skin)

    # ------------------------------------------------------------------ ult: R Devour (armed, checked from his actions)
    ally_in = [buff("r_ally", p["r_ally_t"]), {"type": "Banish", "duration": p["r_ally_t"]}, view("r_in"),
               delayed(p["r_ally_t"], shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"]), view("r_spit"), tsfx("r_spit"))]
    eat_ally = combine(flag("r_lock", 3), *rm("r_armed"), on_me(gulp("vo_r", "r_ally"),
                                                                refresh("r_full", p["r_ally_t"])),
                       *ally_in)
    eat_enemy = combine(*rm("r_armed"), eat, gulp("vo_r", "r_enemy"), refresh("r_full", p["r_t"]),
                        pick(p["r_reach"], "EnemyChampionRecentlyAttacked", *enemy_in))
    # 1. an ally (never him: the probe lands on AllyNotSelf only) in crowd control with two enemy champions near him
    ally_probe = pick(p["r_ally_r"], "AllyChampionInCC", homing("r_probe", 100000, "AllyNotSelf", [eat_ally]))
    count = combine(*rm("r_n1", "r_n2"),
                    around(p["r_n"], "EnemyChampion", [sw("r_n1", flag("r_n2", 3), flag("r_n1", 3))]))
    # 2. three stacks and an enemy champion in reach (the probe flag first: RandomTarget finds nobody -> nothing)
    enemy_probe = combine(*rm("r_e"), pick(p["r_reach"], "EnemyChampionRecentlyAttacked", flag("r_e", 3)),
                          sw("r_e", eat_enemy))
    check = combine(flag("r_busy", 3), count,
                    delayed(1, sw("r_n2", ally_probe)),
                    delayed(3, sw("r_lock", NONE, sw("r_armed", sw("t3", enemy_probe)))))
    if nat:     # the add-on's AI hook picks the unit (the cast's target) - the slot itself devours it
        r_check = NONE
    else:
        r_check = sw("r_armed", sw("r_busy", NONE, check))

    # ------------------------------------------------------------------ attack (the champion-only twin stacks)
    twin = homing("a_twin", 30000, "EnemyChampion", [climb])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, skin, r_check, sfx("a_swing"),
                              delayed(p["atk_st"] - 1, attack(0, 100), magic(p["p_dmg"], 0, p["p_hp"]), view("a_hit"),
                                      tsfx("a_hit"), twin)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Tongue Lash
    stun = combine(eat, {"type": "Stun", "duration": p["q_stun"]}, view("q_stun"), tsfx("q_stun"))
    on_champ = combine(*rm("q_c"), on_me({"type": "Heal", "amount": p["q_heal"], "attack_ratio": 0,
                                          "ap_ratio": p["q_heal_ap"], "heal_type": "Caster"}, cview("q_heal")),
                       sfx("q_heal"), climb if nat else sw("t3", sw("r_armed", eat_here, stun), climb))
    q_hits = [magic(p["q_dmg"], p["q_ap"], p["q_hp"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
              view("q_hit"), tsfx("q_hit"), delayed(1, sw("q_c", on_champ))]
    rng = p["q_range"] + 10000
    tongue = combine(line("q_tongue", p["q_speed"], rng, p["q_w"], "EnemyWithoutTower", False, q_hits),
                     line("q_twin", p["q_speed"], rng, p["q_w"], "EnemyChampion", False, [on_me(flag("q_c", 2))]))
    aim = lob("q_aim", 8, rng, "EnemyWithoutTower", [tongue])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(life, skin, r_check, sfx("q"), voice("vo_q", p), delayed(p["q_at"] - 9, aim)))

    # ------------------------------------------------------------------ skill2: W Abyssal Dive
    one = sw("w_one", NONE, combine(flag("w_one", 3), climb))
    landing = [{"type": "Teleport"}, anim("w_land", p["w_land"]), cview("w_up"), sfx("w_land"),
               zone("w_hit", p["w_rad"], "EnemyWithoutTower",
                    [magic(p["w_dmg"], p["w_ap"], p["w_hp"]), {"type": "Airborne", "duration": p["w_air"]},
                     view("w_hit")]),
               zone("w_champ", p["w_rad"], "EnemyChampion", [one]), r_check]
    dive = combine(lob("w_warn", 1, p["w_range"] + 20000, "EnemyChampion", [view("w_warn"), sfx("w_warn")]),
                   lob("w_go", p["w_up"], p["w_range"] + 20000, "EnemyChampion", landing),
                   on_me({"type": "Banish", "duration": p["w_up"]}))
    go = combine(flag("w_cd", p["w_cd"]), anim("skill2", p["w_anim"]), cview("w_down"), sfx("w"), voice("vo_w", p),
                 delayed(p["w_sink"], dive))
    if nat:     # the add-on's AI hook picks the champion (or refuses the dive) - the slot dives on the cast's target
        skill2 = action("idle", 3, p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion", combine(life, skin, go),
                        key="skill2")
    else:
        # never alone, only at a good moment (「W也别乱放 看好时机」), on the champion his team is fighting: with an allied
        # champion within w_ally_r only when that champion is in crowd control (the knock-up chains it: a homing probe
        # whose applied_target EnemyChampionInCC is tested on the hit), with two or more allies anyway; else nothing
        # and the slot (s2_cd) checks again. Allies are counted with AllyChampion (him too: n allies = a{n+1}).
        allies = combine(*rm("a1", "a2", "a3"),
                         around(p["w_ally_r"], "AllyChampion", [sw("a2", flag("a3", 3), sw("a1", flag("a2", 3),
                                                                                             flag("a1", 3)))]))
        probe = combine(*rm("w_cc", "w_ok"), homing("w_probe", 100000, "EnemyChampionInCC", [on_me(flag("w_cc", 3))]))
        ok = sw("a2", sw("w_cc", flag("w_ok", 3), sw("a3", flag("w_ok", 3))))
        skill2 = action("idle", 3, p["s2_cd"], 1, p["w_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                        combine(life, skin, sw("w_cd", NONE, combine(allies, probe, delayed(2, ok),
                                                                     delayed(3, sw("w_ok", go))))),
                        key="skill2")

    # ------------------------------------------------------------------ ult: arm (and check at once)
    retry = p["r_cd"] * 100 // 60 - 100      # cooltime x 100 / (100 + mult) = 60 ticks
    arm = combine(life, refresh("r_armed", p["r_arm"]), r_check,
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                flag("r_retry", 3, ult_cooldown_mult=retry)))))
    if nat:     # the hook's pick: an ally (protected) or an enemy (eaten), both on the cast's own target
        devour = {"type": "Native", "effect_ref": "league_tahmkench:devour"}
        ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "BothChampion", combine(life, devour), key="ult")
    else:
        ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", arm, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_tongue")]
    views_e = [E("a_hit"), E("q_hit"), E("q_stun"), E("q_heal", FX, 3), E("e_shield", FX, 3),
               E("w_down", BIG, 1), E("w_warn", BIG, -1, False), E("w_up", BIG, 1), E("w_hit"),
               E("r_gulp", FX, 3), E("r_in"), E("r_spit")]
    views_b = [B_("t_pip1", FX, 3), B_("t_pip2", FX, 3), B_("t_pip3", FX, 3), B_("q_slow", FX, -1),
               B_("r_full", FX, 3), B_("r_ally", FX, 3, "r_bubble"), B_("r_enemy", FX, 3, "r_bubble")]
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
        kit["passive"] = {"passive_ref": "league_tahmkench:skin",
                          "params": {"hold": p["p_hold"], "e_red": p["e_red"], "e_sh": p["e_sh"], "e_sh_ap": p["e_sh_ap"],
                                     "e_t": p["e_t"], "r_t": p["r_t"], "r_ally_t": p["r_ally_t"], "r_dmg": p["r_dmg"],
                                     "r_ap": p["r_ap"], "r_hp": p["r_hp"], "r_thp": p["r_thp"], "r_sh": p["r_sh"],
                                     "r_sh_ap": p["r_sh_ap"], "r_sh_t": p["r_sh_t"], "q_stun": p["q_stun"]}}
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
