"""Build league_rengar.data_champion (jungle, Assassin) from the parameters P.

    python tools/kit/build_rengar.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-08/09: jungle, Assassin, kit A - League's whole kit; 「还有草丛可以跳跃」 (the brush leap: a
native add-on, addons/league_rengar_bush, the main pack keeps a stand-in), the Kha'Zix easter egg both ways, 「加入高手连招」).
TFM2 has three active slots: League's Savagery (an empowered attack) runs on its own, Battle Roar is `skill`, Bola Strike
`skill2`, Thrill of the Hunt the `ult`.
  passive Unseen Predator (无形潜行): `ready` (its eye over his head) adds leap_range to his attack range; his next
          attack is the pounce (the `leap` strip): a dash onto the target (MoveToTarget from tick leap_go) and the landing
          rake on tick leap_at, a Ferocity point. Nothing in data reads brush, so it readies at each life's start, after
          `quiet` ticks without an action of his (league_evelynn's shade: every action renews `fight` and queues a check
          that finds it gone only after the last one) and from R. The add-on sets `ready` while he stands in a bush.
  Ferocity (凶残值): f1..f4 caster stacks (fero_t ticks, renewed by each gain): a point for each Savagery, roar, bola
          and pounce; at four the next Savagery / roar / bola is empowered and spends them.
  attack  The blade swing, the hit on tick a_st. Savagery (野蛮打击, automatic): the first attack after q_cd is the Q
          strip - a slam on tick q_slam_at (q_s_dmg + q_s_ratio% AD) and the rip on q_rip_at (q_dmg + q_ratio% AD) -
          then q_as% attack speed for q_as_t ticks. Empowered: qe_dmg + qe_ratio% AD and qe_as% for qe_as_t.
  skill   W Battle Roar (战吼): a roar on `EnemyWithoutTower` within w_r (so he roars on camps too): w_dmg + w_ratio% AD
          to every enemy round him, a heal of w_heal + w_heal_r% AD (League heals a share of the damage he just took;
          nothing reads that, so it is a flat heal). Empowered: the heal x we_heal% and we_cc_t ticks of cc_immune
          (League's empowered roar breaks crowd control; no data effect removes it, so it keeps it off him).
  skill2  E Bola Strike (套索打击): a bola thrown on tick e_at toward the target (a line, the first unit it meets - a
          skillshot, dodgeable): e_dmg + e_ratio% AD and e_slow% slow for e_slow_t ticks. Empowered: rooted (`Bind`)
          e_root_t ticks.
  ult     R Thrill of the Hunt (狩猎律动): on `EnemyChampionRecentlyAttacked` within r_range (league_xayah's rule: the
          ult not wasted on a full-health champion): camouflage (CasterInvisible r_inv ticks), r_ms% move speed, the
          passive ready and `r_hunt`: the pounce out of it is the crit - r_dmg + r_ratio% AD more and r_shred% less
          defence on the target for r_shred_t ticks. The target carries the hunter's eye (r_mark) while he stalks.
  combos (the pros' Rengar, slot-played like league_leesin's: a combo never spends another slot's cooldown)
          Air Q (空中Q): a pounce with Savagery ready lands as Savagery (its rip and attack speed on the landing).
          Triple Q (三Q): the Savagery that fills Ferocity keeps its cooldown on `q_hold` (not `q_cd`), which holds
                  back a plain Savagery only: the next attack is the empowered Savagery at once.
          Leap -> E (扑脸定身): a pounce that lands on a champion opens `lp_on` (lp_t ticks); a bola in it is thrown at
                  once and homes in (it cannot miss) and roots e_combo_t ticks (empowered: e_root_t).
          R one-shot (R一套): the R pounce opens the same window (R -> E root -> Savagery).
  easter egg (Kha'Zix, the user: 「狮子狗螳螂碰到后的彩蛋」) - data reads only the caster's own buffs, so the two kits tell
          each other: his champion hits mark the target `league_rengar_rival_hit`; league_khazix's actions, finding that
          on himself, give the enemy champions round him `league_khazix_seen` (Rengar, who just hit him, reads it); his
          kill check (league_jinx's) on a champion while he holds `league_khazix_seen` is the Kha'Zix kill: the trophy
          (Kha'Zix's head, t_bonus% attack until he dies) and its picture. The other way round league_khazix marks his
          own targets `league_khazix_rival_hit`, Rengar's actions answer with `league_rengar_seen`, and Kha'Zix's kill
          check reads it (an extra evolution). Each first sight of the other (`league_khazix_near`, given by Kha'Zix's
          actions round him) plays the rivals' line and the anger mark, once a life.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_rengar.data_champion")
ID = "league_rengar"
FX = "asset/league/effects/league_rengar_fx"
BIG = "asset/league/effects/league_rengar_big"

# Timings from the strips (assets/source/native/rengar_cells.json, rig_rengar.py): the swing's hit on tick 11 (attack
# frame 4), the pounce lands on tick 17 (leap frame 6), Savagery's slam on 13 and rip on 16 (skill frames 5 and 6), the
# bola leaves on 13 (skill2 frame 4), the roar on 8 (skill_w frame 3), the camouflage on 10 (ult frame 3).
P = {
    # stats (Assassin base: attack 120 +30, hp 900 +80, defence 25, mr 15, move 1100, range 23000); League's Rengar:
    # 590 +104 hp, 68 AD +3, 34 armour, 345 move, 125 range
    "hp": 950, "hp_g": 88, "atk": 100, "atk_g": 16, "def": 28, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    # attack: the blade swing
    "atk_range": 23000, "atk_dur": 25, "atk_cd": 55, "a_st": 11,
    # passive: Unseen Predator (League: a 725-range leap from brush or camouflage)
    "leap_range": 25000, "leap_dur": 31, "leap_go": 5, "leap_at": 17, "leap_speed": 4500, "leap_dmg": 20,
    "leap_ratio": 50, "quiet": 180,
    # Ferocity (League: 4 stacks, lost one by one out of combat)
    "fero_t": 720,
    # Savagery (League: next attack +30-150 + 0-40% AD, 40% attack speed 3 s, cd 6-4.5 s; empowered 30-240 + 30% AD,
    # 50-101% attack speed 5 s)
    "q_cd": 300, "q_dur": 29, "q_slam_at": 13, "q_rip_at": 16, "q_s_dmg": 10, "q_s_ratio": 30, "q_dmg": 30,
    "q_ratio": 90, "q_as": 40, "q_as_t": 180, "qe_dmg": 50, "qe_ratio": 140, "qe_as": 80, "qe_as_t": 300,
    # skill: W Battle Roar (League: 450 radius, 50-190 + 80% AP magic, heal 50% of the damage taken in 1.5 s, cd 16-10 s;
    # empowered: cleanse, heal 50-195 + 10% bonus hp... )
    "w_cd": 540, "w_dur": 37, "w_at": 8, "w_r": 22000, "w_dmg": 40, "w_ratio": 50, "w_heal": 40, "w_heal_r": 50,
    "we_heal": 200, "we_cc_t": 90,
    # skill2: E Bola Strike (League: 1000 range, 1500 speed, 55-255 + 80% bonus AD, slow 30-50% 1.75 s, cd 10 s;
    # empowered root 1.75 s)
    "e_cd": 600, "e_dur": 28, "e_at": 13, "e_range": 50000, "e_speed": 7000, "e_len": 60000, "e_rad": 5000,
    "e_y": 3000, "e_dmg": 40, "e_ratio": 60, "e_slow": 40, "e_slow_t": 105, "e_root_t": 105,
    # ult: R Thrill of the Hunt (League: camouflage 12-20 s, +40% move speed, the leap a guaranteed crit and 12-36
    # armour shred 4 s, cd 110-70 s)
    "r_cd": 3600, "r_dur": 25, "r_at": 10, "r_range": 90000, "r_inv": 300, "r_ms": 40, "r_dmg": 60, "r_ratio": 80,
    "r_shred": 25, "r_shred_t": 240,
    # combos
    "lp_t": 90, "e_combo_t": 60, "e_combo_speed": 12000,
    # the easter egg: the marks' life, the trophy's attack, how near the rival must be
    "rv_t": 40, "seen_t": 60, "t_bonus": 15, "near_r": 60000,
    # takedowns: league_jinx's kill check
    "k_hold": 40, "k_read": 4,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_rengar_bush: its native passive readies the pounce in brush; the out-of-combat
    # stand-in goes (life start and R still ready it)
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


def sw(buff, yes, no=None, raw=False):
    return {"type": "SwitchByBuff", "buff_name": buff if raw else n(buff), "effect_buff": yes,
            "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, raw=False, **fields):
    return {"type": "AddBuff", "buff_state": {"name": name if raw else n(name), "duration": {"Time": {"tick": tick}},
                                              **fields}}


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
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ Ferocity
    def gain():
        top = combine(*rm("f3"), refresh("f4", p["fero_t"]), sfx("vo_fero"))
        return sw("f4", NONE, sw("f3", top, sw("f2", combine(*rm("f2"), refresh("f3", p["fero_t"])),
                                               sw("f1", combine(*rm("f1"), refresh("f2", p["fero_t"])),
                                                  refresh("f1", p["fero_t"])))))

    spend = combine(*rm("f1", "f2", "f3", "f4"))

    # ------------------------------------------------------------------ the passive's readiness
    ready = sw("ready", NONE, flag("ready", None, range=p["leap_range"]))
    # an action of his renews `fight`; the check queued by the last one finds it gone (league_evelynn's shade)
    act = NONE if p["native"] else combine(refresh("fight", p["quiet"]),
                                           on_me(delayed(p["quiet"] + 2, sw("fight", NONE, ready))))
    life = sw("init", NONE, combine(flag("init", None), ready))

    # ------------------------------------------------------------------ the easter egg: the rivals
    # Kha'Zix hit me lately (his mark on me): tell the enemy champions round me that I was hit by him; Kha'Zix near me
    # (his actions mark the champions round him): the rivals' line and the anger mark, once a life
    rival = combine(sw("league_khazix_rival_hit", around(p["near_r"], "EnemyChampion",
                                                         [buff("league_rengar_seen", p["seen_t"], raw=True)]), raw=True),
                    sw("met", NONE, sw("league_khazix_near", combine(flag("met", None), cview("k_meet"),
                                                                     sfx("vo_khazix")), raw=True)),
                    around(p["near_r"], "EnemyChampion", [buff("league_rengar_near", p["seen_t"], raw=True)]))
    trophy = sw("league_khazix_seen", sw("trophy", NONE, combine(flag("trophy", None, attack_mult=p["t_bonus"]),
                                                                 cview("t_trophy"), sfx("vo_khazix"))), raw=True)
    rival_mark = buff("league_rengar_rival_hit", p["rv_t"], raw=True)

    def kill_check(src, read=True):
        """On a hit enemy champion, around its damage: the flag before, the living target's clear after, the read on
        him later (a Kha'Zix kill gives the trophy). Each source keeps its own flag (league_tristana W); read=False
        leaves the read to the action (one for all of the attack's branches)."""
        k = f"k_{src}"
        after = [casted(3, 1, *rm(k))]
        if read:
            after.append(on_me(delayed(p["k_read"], kill_read(src))))
        return refresh(k, p["k_hold"]), combine(*after)

    def kill_read(src):
        return sw(f"k_{src}", combine(*rm(f"k_{src}"), trophy))

    def champ_twin(name, src, extra=(), read=True):
        """An invisible twin of a hit that reaches only champions: the rival's mark, the kill check, extras."""
        ks, kr = kill_check(src, read)
        return homing(name, 100000, 0, "EnemyChampion", [rival_mark, ks, *extra, kr])

    # ------------------------------------------------------------------ Savagery (the Q strip)
    def savagery(emp, lead=0):
        """The slam and the rip on the attack's target, attack speed after; emp = Ferocity's (spends it, Q's cooldown
        untouched); a plain one starts q_cd and gains a point (the fourth opens the triple Q)."""
        dmg, ratio = (p["qe_dmg"], p["qe_ratio"]) if emp else (p["q_dmg"], p["q_ratio"])
        speed = refresh("qe_as", p["qe_as_t"], attack_speed_mult=p["qe_as"]) if emp else \
            refresh("q_as", p["q_as_t"], attack_speed_mult=p["q_as"])
        return combine(anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                       delayed(lead + p["q_slam_at"] - 1, homing("q_slam", 100000, 0, "EnemyWithoutTower",
                                                                  [attack(p["q_s_dmg"], p["q_s_ratio"]), view("q_slam"),
                                                                   tsfx("q_hit")])),
                       delayed(lead + p["q_rip_at"] - 1, homing("q_rip", 100000, 0, "EnemyWithoutTower",
                                                                 [attack(dmg, ratio), view("q_rip"),
                                                                  tsfx("q_emp" if emp else "q_hit")]),
                               champ_twin("q_twin", "a", read=False), speed),
                       spend if emp else sw("f3", flag("q_hold", p["q_cd"]), flag("q_cd", p["q_cd"])),
                       NONE if emp else gain())

    # ------------------------------------------------------------------ the pounce (passive, R)
    lp_open = on_me(refresh("lp_on", p["lp_t"]))
    hunt = sw("r_hunt", combine(*rm("r_hunt"), attack(p["r_dmg"], p["r_ratio"]),
                                buff("r_shred", p["r_shred_t"], defence_mult=-p["r_shred"]), view("r_hit"),
                                tsfx("r_hit")))
    air_q = sw("q_cd", NONE, sw("q_hold", NONE, combine(attack(p["q_dmg"], p["q_ratio"]), view("q_rip"), tsfx("q_hit"),
                                     on_me(flag("q_cd", p["q_cd"]),
                                           refresh("q_as", p["q_as_t"], attack_speed_mult=p["q_as"])))))
    land_hit = [attack(p["leap_dmg"], 100 + p["leap_ratio"]), view("l_hit"), tsfx("leap_hit"), hunt, air_q]
    pounce = combine(*rm("ready"), anim("leap", p["leap_dur"]), sfx("leap"), cview("l_dust"),
                     delayed(p["leap_go"] - 1, {"type": "MoveToTarget", "speed": p["leap_speed"],
                                                "range": p["atk_range"] + p["leap_range"] + 20000, "end_effects": []}),
                     delayed(p["leap_at"] - 1, homing("l_land", 100000, 0, "EnemyWithoutTower", land_hit),
                             champ_twin("l_twin", "a", [lp_open], read=False), cview("l_dust"), gain()))

    # ------------------------------------------------------------------ the attack
    swing = combine(sfx("a_swing"), delayed(p["a_st"] - 1, homing("a_hit", 100000, 0, "EnemyWithoutTower",
                                                                 [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                                         champ_twin("a_twin", "a", read=False)))
    # the triple Q: the Savagery that fills Ferocity keeps its cooldown on `q_hold`, which stops a plain Savagery only,
    # so the next attack is the empowered one
    choose = sw("ready", pounce, sw("q_cd", swing, sw("f4", savagery(True), sw("q_hold", swing, savagery(False)))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, act, rival, choose,
                              delayed(max(p["a_st"], p["q_rip_at"], p["leap_at"]) + p["k_read"], kill_read("a"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: W Battle Roar
    def roar(emp):
        h = p["we_heal"] if emp else 100
        return combine(cview("w_roar"), sfx("w_emp" if emp else "w"),
                       around(p["w_r"], "EnemyWithoutTower", [attack(p["w_dmg"], p["w_ratio"]), view("a_hit")]),
                       around(p["w_r"], "EnemyChampion", [rival_mark]),
                       heal(p["w_heal"] * h // 100, p["w_heal_r"] * h // 100), cview("w_heal"),
                       *([refresh("we_cc", p["we_cc_t"], cc_immune=True), spend] if emp else [gain()]))

    skill = action("skill_w", p["w_dur"], p["w_cd"], 1, p["w_r"], "Targeting", "EnemyWithoutTower",
                   combine(act, rival, anim("skill_w", p["w_dur"]), voice("vo_w", p),
                           delayed(p["w_at"] - 1, sw("f4", roar(True), roar(False)))), key="skill")

    # ------------------------------------------------------------------ skill2: E Bola Strike
    def bola_hit(root):
        hold = [{"type": "Bind", "duration": root}, buff("e_root", root), tsfx("e_emp_hit")] if root else \
            [buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), tsfx("e_hit")]
        return [attack(p["e_dmg"], p["e_ratio"]), *hold]

    def throw(emp):
        root = p["e_root_t"] if emp else 0
        plain = line("e_bola", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyWithoutTower", False,
                     bola_hit(root))
        sure = homing("e_bola", p["e_combo_speed"], p["e_y"], "EnemyWithoutTower",
                      bola_hit(root or p["e_combo_t"]))
        return combine(sfx("e"), sw("lp_on", combine(*rm("lp_on"), sure), plain),
                       champ_twin("e_twin", "e"), spend if emp else gain())

    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(act, rival, anim("skill2", p["e_dur"]), voice("vo_e", p),
                            delayed(p["e_at"] - 1, sw("f4", throw(True), throw(False)))))

    # ------------------------------------------------------------------ ult: R Thrill of the Hunt
    stalk = combine({"type": "CasterInvisible", "tick": p["r_inv"]},
                    refresh("r_on", p["r_inv"], move_speed_mult=p["r_ms"]),
                    refresh("r_hunt", p["r_inv"] + 60), *rm("ready"),
                    flag("ready", None, range=p["leap_range"]), cview("r_smoke"), sfx("r"), voice("vo_r", p),
                    homing("r_tag", 100000, 0, "EnemyChampion", [buff("r_mark", p["r_inv"])]))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(act, rival, anim("ult", p["r_dur"]), delayed(p["r_at"] - 1, stalk)))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring); every
    # picture here is left-right symmetric
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, tag=None, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("e_bola")]
    views_e = [E("a_hit"), E("l_hit"), E("l_dust", FX, -1, False), E("q_slam", FX, -1, False), E("q_rip"),
               E("w_roar", BIG, -1, False), E("w_heal", FX, 3, False), E("r_smoke", BIG, 3, False), E("r_hit", BIG),
               E("t_trophy", FX, 4, False), E("k_meet", FX, 4, False)]
    views_b = [B_("ready", "p_ready", FX, 4), B_("f1", "f1", FX, 4), B_("f2", "f2", FX, 4), B_("f3", "f3", FX, 4),
               B_("f4", "f4", FX, 4), B_("q_as", "q_buff", FX, -1), B_("qe_as", "q_emp", BIG, 3),
               B_("we_cc", "w_emp", BIG, 3), B_("e_slow", "e_slow", FX, 3), B_("e_root", "e_root", FX, 3),
               B_("r_mark", "r_mark", FX, 4)]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": "league_rengar_bush:bush", "params": {"leap_range": p["leap_range"]}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee", "CC"], **extra,
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (the brush passive)")
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
