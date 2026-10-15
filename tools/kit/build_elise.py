"""Build league_elise.data_champion (jungle, AP assassin, human / spider forms) from the parameters P.

    python tools/kit/build_elise.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-15: jungle AP assassin; the forms switch like League's R from level 1 - the switch is in
the attack slot (league_nidalee's way), the ult slot (level 5) is the cocoon hunt; human Neurotoxin / spider Venomous
Bite as skill, human Cocoon + Volatile Spiderling and spider Rappel + Skittering Frenzy sharing skill2; the passive's
spiderlings in the main pack as pictures and bites on her target; the whole-body spider and the target picks in the
add-on; the pros' combos):
  forms   Human (default, after every respawn): a ranged venom spit (atk_range + h_add: the permanent caster buff `hu` -
          a range buff cannot be negative, so the bare reach is the spider's and every action puts `hu` back when she
          has neither form). Spider: the caster buff `sp` (permanent, melee reach, +sp_ms% move speed), every action
          plays the spider's own tags (c_*; idle, run, hit and death are the spider only with the add-on).
          Spider Form (蜘蛛形态, the switch): each attack's first tick, with the switch ready (no `r_cd`), checks the rules;
          a switch replaces that attack with the transform (tf_dur ticks, no hit) and starts r_cd (League: 4 s).
          Human -> spider: an enemy champion in crowd control within c_near (her cocoon landed, or an ally's stun), or
          an enemy within c_near while Neurotoxin (and from level 3 the Cocoon) is on cooldown.
          Spider -> human: Venomous Bite on cooldown and, from level 3, Rappel on cooldown too; and Neurotoxin (or from
          level 3 the Cocoon) ready.
  passive Spider Queen (蜘蛛女皇): a human ability hit (Neurotoxin, the spiderling, the cocoon) on an enemy adds a
          spiderling (caster flags sl1 -> sl2 -> sl3, at most 3, gone at death). In spider form every attack also
          deals c_dmg + c_ap% AP magic and heals her c_heal + c_hap% AP (League's Spider Form bonus), and each
          spiderling bites the target for sl_dmg + sl_ap% AP magic (x sl_fz% during Skittering Frenzy), drawn on
          the target (league_annie Tibbers' way: the pictures ride on the unit, there is no unit of their own).
  attack  Human: the venom spit (released on a_st, homing). Spider: the bite (c_atk_st) with the bonus above.
  skill   Human: Neurotoxin (神经毒素), a homing venom bolt on `EnemyWithoutTower` (camps too): q_dmg + q_ap% AP magic
          and q_hp% of the target's maximum health as true damage (League: % CURRENT health, the data reads no current
          health; league_jayce's E way). Spider: Venomous Bite (剧毒之蜇), a leap onto an enemy within cq_r:
          cq_dmg + cq_ap% AP magic and cq_hp% max health true damage (League: % MISSING health).
  skill2  Human: Cocoon (结茧) first - a line on the target's spot locked at the cast (the first unit it meets, a
          skillshot), e_dmg + e_ap% AP magic and a stun e_stun ticks; while it cools down, Volatile Spiderling
          (自爆蜘蛛): a spiderling crawling on a line toward the target (stops on the first unit), w_dmg + w_ap% AP
          magic round the hit. Spider: Rappel (盘丝) first - on an enemy champion within ce_r: she rises out of reach
          (a self-Banish ce_up ticks: nobody can target her; a banished unit gives no vision, league_masteryi Q) and
          drops onto the champion (Teleport), ce_dmg + ce_ap% AP round the landing; while it cools down, Skittering
          Frenzy (掠行狂暴) with an enemy within cw_near: +cw_as% attack speed for cw_t ticks, the spiderlings bite
          harder (sl_fz%).
  ult     Cocoon hunt (茧缚猎杀, level 5): on an enemy champion (in crowd control first, else the last one she hit)
          within r_range: in human form she spits a cocoon at it (the Cocoon line, aimed at the cast), turns into the
          spider at once (no transform action), every spider cooldown resets, and r_go ticks later Rappels onto it
          (banish r_up ticks, Teleport) for r_dmg + r_ap% AP round the landing and bites (Venomous Bite) - the pros'
          E -> R -> E(Rappel) -> Q. In spider form only the Rappel and the bite.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_elise.data_champion")
ID = "league_elise"
FX = "asset/league/effects/league_elise_fx"
BIG = "asset/league/effects/league_elise_big"

# Timings from the strips (league/champions/league_elise#anim.fanim, Codex's step 2 after League's clips): the spit
# 440 ms, released on frame 3 (tick 10); Neurotoxin and the Cocoon / Spiderling cast 450 ms, released on frame 3 (tick
# 10); the turns 270 ms; the bite 330 ms, the hit on frame 3 (tick 9); Venomous Bite 410 ms, off the ground on frame 2
# (tick 4); Rappel's rise 300 ms, at the top on frame 4 (tick 13: the banish starts there), the drop 250 ms.
# Numbers: the first draft from league_nidalee's d11 (the pack's AP junglers); balance runs below the P table.
P = {
    # stats (League's Elise: 650 +109 hp, 55 AD, 30 armour, 30 mr, 330 move, 550 range (spider 125))
    "hp": 990, "hp_g": 100, "atk": 108, "atk_g": 24, "mp": 50, "mp_g": 20, "def": 28, "def_g": 7, "mr": 24, "mr_g": 4,
    "ms": 1080, "ms_g": 12,
    "atk_range": 23000, "atk_dur": 26, "atk_cd": 52, "a_st": 10, "a_speed": 4500,
    # spider form (League: +move speed 10-25, melee 125, attacks +10-50 + 30% AP magic and heal 4-8 + 10% AP)
    "h_add": 27000, "c_atk_dur": 20, "c_atk_st": 9, "c_near": 32000, "tf_dur": 16, "r_cd_t": 240, "sp_ms": 10,
    "c_dmg": 20, "c_ap": 25, "c_heal": 6, "c_hap": 10,
    # passive spiderlings (League: 2-4, each 10-70 + 15% AP magic a bite)
    "sl_dmg": 12, "sl_ap": 10, "sl_fz": 150,
    # Q Neurotoxin (League: 575 range, 40-200 + 4% (+3% per 100 AP) current health, cd 6 s)
    "q_cd": 360, "q_range": 55000, "q_dur": 27, "q_at": 10, "q_speed": 4500, "q_dmg": 70, "q_ap": 60, "q_hp": 3,
    # Venomous Bite (League: 475 leap, 70-270 + 8% (+3% per 100 AP) missing health, cd 6 s)
    "cq_cd": 360, "cq_r": 35000, "cq_dur": 25, "cq_go": 4, "cq_speed": 5000, "cq_dmg": 80, "cq_ap": 70, "cq_hp": 5,
    # skill2 slot
    "s2_cd": 60, "s2_range": 75000,
    # E Cocoon (League: 1100 range, 60 width, 55-235 + 80% AP, stun 1.6-2.4 s, cd 12-10 s)
    "e_cd": 660, "e_range": 75000, "e_anim": 27, "e_at": 10, "e_speed": 4500, "e_w": 2500, "e_dmg": 60, "e_ap": 50,
    "e_stun": 100,
    # W Volatile Spiderling (League: 950 range, 60-220 + 95% AP, cd 12 s)
    "w_cd": 720, "w_range": 65000, "w_anim": 27, "w_at": 10, "w_speed": 2500, "w_w": 3000, "w_rad": 10000,
    "w_dmg": 70, "w_ap": 70,
    # Rappel (League: up 2 s, descends within 750, cd 22-14 s)
    "ce_cd": 900, "ce_r": 50000, "ce_anim": 18, "ce_rise": 13, "ce_up": 45, "cl_anim": 15, "ce_rad": 12000, "ce_dmg": 40, "ce_ap": 30,
    # Skittering Frenzy (League: +60-100% attack speed 3 s, cd 10 s)
    "cw_cd": 600, "cw_near": 25000, "cw_as": 60, "cw_t": 180,
    # ult: the cocoon hunt
    "r_cd": 1200, "r_range": 75000, "r_go": 16, "r_up": 30, "r_dmg": 120, "r_ap": 70,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_elise: passive league_elise:queen; skill2 and the ult cast on the target the add-on's
    # AI hook picks (the Cocoon and Rappel go at it instead of a random champion in reach)
    "native": 0,
    # test builds for the balance runs: 1 = human only, 2 = spider from the first attack on
    "lock": 0,
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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def maxhp(pct):
    """pct% of the target's maximum health as true damage (no magic effect has a target-health part)."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit."""
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


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = bool(p["native"])
    # ------------------------------------------------------------------ passive: the spiderlings
    # a human ability hit adds one (sl1 -> sl2 -> sl3); permanent flags, cleared by her death
    grow = on_me(sw("sl3", NONE, sw("sl2", flag("sl3", None), sw("sl1", flag("sl2", None), flag("sl1", None)))))

    def bites(k):
        dmg = p["sl_dmg"] * k
        ap = p["sl_ap"] * k
        hurt = sw("cw_on", magic(dmg * p["sl_fz"] // 100, ap * p["sl_fz"] // 100), magic(dmg, ap))
        return combine(hurt, view(f"sl_bite{k}"), tsfx("sl_bite"))
    spiderlings = sw("sl3", bites(3), sw("sl2", bites(2), sw("sl1", bites(1))))

    # ------------------------------------------------------------------ the forms
    # the human's reach is a caster buff (`hu`, +h_add): ranges cannot be cut, so the spider is the bare melee reach and
    # every action first puts `hu` back when she has neither form (each life starts human)
    human = sw("sp", NONE, sw("hu", NONE, flag("hu", None, range=p["h_add"])))
    spider_on = lambda: combine(*rm("hu"), flag("sp", None, move_speed_mult=p["sp_ms"]), refresh("r_cd", p["r_cd_t"]))
    to_spider = combine(spider_on(), anim("transform", p["tf_dur"]), cview("tf_spider"), sfx("tf_spider"),
                        voice("vo_spider", p))
    to_human = combine(*rm("sp"), flag("hu", None, range=p["h_add"]), refresh("r_cd", p["r_cd_t"]),
                       anim("c_transform", p["tf_dur"]), cview("tf_human"), sfx("tf_human"), voice("vo_human", p))
    instant_spider = sw("sp", NONE, combine(spider_on(), cview("tf_spider"), sfx("tf_spider")))

    # ------------------------------------------------------------------ attack
    human_hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    human_atk = combine(sfx("a_spit"),
                        delayed(p["a_st"] - 1, homing("a_spit", p["a_speed"], "Enemy", human_hit)))
    spider_hit = [attack(0, 100), magic(p["c_dmg"], p["c_ap"]), spiderlings, view("c_hit"), tsfx("c_hit"),
                  on_me({"type": "Heal", "amount": p["c_heal"], "attack_ratio": 0, "ap_ratio": p["c_hap"],
                         "heal_type": "Caster"})]
    spider_atk = combine(anim("c_attack", p["c_atk_dur"]), sfx("c_swing"),
                         delayed(p["c_atk_st"] - 1, homing("c_bite", 100000, "Enemy", spider_hit)))
    # the switch's rules (only with r_cd gone) lay `tf`; one branch then plays the transform or the attack
    tf = flag("tf", 2)
    lv3 = lambda low, high: {"type": "SwitchByLevel3", "effect_start": low, "effect_level3": high}
    probe = combine(*rm("near", "cc"), pick(p["c_near"], "EnemyWithoutTower", flag("near", 2)),
                    pick(p["c_near"], "EnemyChampionInCC", flag("cc", 2)))
    # human -> spider: a champion in crowd control close (her cocoon, or an ally's stun), or an enemy close with the
    # human spells spent (Neurotoxin; from level 3 the Cocoon as well)
    spent = sw("q_cd", lv3(tf, sw("e_cd", tf)))
    go = combine(probe, sw("cc", tf, sw("near", spent)))
    # spider -> human: Venomous Bite spent (from level 3 Rappel too), with Neurotoxin or (level 3+) the Cocoon ready
    ready = lv3(sw("q_cd", NONE, tf), sw("q_cd", sw("e_cd", NONE, tf), tf))
    back = sw("cq_cd", lv3(ready, sw("ce_cd", ready)))
    rules = combine(*rm("tf"), sw("r_cd", NONE, sw("sp", back, go)))
    if p["lock"] == 1:      # test builds only: never switch (human) / switch once and stay (spider)
        rules = NONE
    elif p["lock"] == 2:
        rules = combine(*rm("tf"), sw("sp", NONE, tf))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(human, rules, sw("tf", sw("sp", to_human, to_spider), sw("sp", spider_atk, human_atk))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Neurotoxin / Venomous Bite
    q_hit = [magic(p["q_dmg"], p["q_ap"]), maxhp(p["q_hp"]), view("q_hit"), tsfx("q_hit"), grow]
    neuro = combine(flag("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                    delayed(p["q_at"] - 1, homing("q_bolt", p["q_speed"], "EnemyWithoutTower", q_hit)))

    def bite(rng, target, extra=()):
        hit = [magic(p["cq_dmg"], p["cq_ap"]), maxhp(p["cq_hp"]), view("cq_hit"), tsfx("cq_hit"), *extra]
        return pick(rng, target, combine(anim("c_skill", p["cq_dur"]), sfx("cq"), voice("vo_cq", p),
                                         delayed(p["cq_go"] - 1, {"type": "MoveToTarget", "speed": p["cq_speed"],
                                                                  "range": rng + 30000, "end_effects": hit})))
    in_bite = combine(*rm("q_in"), pick(p["cq_r"], "EnemyWithoutTower", flag("q_in", 1)),
                      sw("q_in", combine(flag("cq_cd", p["cq_cd"]), bite(p["cq_r"], "EnemyWithoutTower"))))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(human, sw("sp", sw("cq_cd", NONE, in_bite), sw("q_cd", NONE, neuro))), key="skill")

    # ------------------------------------------------------------------ skill2: Cocoon + Spiderling / Rappel + Frenzy
    def aimed(rng, target, at, shot, direct=False):
        """The shot leaves on tick `at` toward where the target stood 8 ticks before (league_caitlyn Q's lock): a hidden
        8-tick lob onto that spot starts it, so a champion who keeps walking dodges it. `direct`: at the cast's own
        target (the add-on's copy), else at a random `target` in reach."""
        lob = {"type": "ParabolicProjectile", "name": n("aim"), "travel_time": 8, "range": rng + 10000,
               "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
               "end_effects": [shot]}
        return delayed(at - 9, lob if direct else pick(rng, target, lob))

    def cocoon_line():
        hits = [magic(p["e_dmg"], p["e_ap"]), {"type": "Stun", "duration": p["e_stun"]}, view("e_hit"),
                tsfx("e_hit"), grow]
        return line("e_web", p["e_speed"], p["e_range"] + 10000, p["e_w"], "EnemyWithoutTower", False, hits)

    e_cast = combine(flag("e_cd", p["e_cd"]), anim("skill2", p["e_anim"]), sfx("e"), voice("vo_e", p),
                     aimed(p["e_range"], "EnemyChampion", p["e_at"], cocoon_line(), direct=nat))
    w_hit = [around(p["w_rad"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_ap"]), view("w_hit"), grow]),
             view("w_boom"), tsfx("w_boom")]
    w_line = line("w_spider", p["w_speed"], p["w_range"] + 10000, p["w_w"], "EnemyWithoutTower", False, w_hit)
    w_cast = combine(flag("w_cd", p["w_cd"]), anim("skill2", p["w_anim"]), sfx("w"), voice("vo_w", p),
                     aimed(p["w_range"], "EnemyWithoutTower", p["w_at"], w_line))
    # the cocoon only on a champion in reach (probe), the spiderling on anything
    c_in = combine(*rm("e_in"), pick(p["e_range"], "EnemyChampion", flag("e_in", 1)))
    human_s2 = combine(c_in, sw("e_cd", sw("w_cd", NONE, w_cast), sw("e_in", e_cast, sw("w_cd", NONE, w_cast))))

    def rappel(up, dmg, ap, extra=()):
        land = [anim("c_land", p["cl_anim"]),
                around(p["ce_rad"], "EnemyWithoutTower", [magic(dmg, ap), view("ce_hit"), tsfx("ce_hit")]),
                cview("ce_land"), sfx("ce_land"), *extra]
        # rise: banished (untargetable) where she stands; drop: Teleport onto the target the cast picked
        return combine(anim("c_skill2", p["ce_anim"]), sfx("ce"), cview("ce_up"), voice("vo_ce", p),
                       delayed(p["ce_rise"], on_me({"type": "Banish", "duration": up})),
                       delayed(p["ce_rise"] + up, {"type": "Teleport"}, *land))
    frenzy = combine(flag("cw_cd", p["cw_cd"]), refresh("cw_on", p["cw_t"], attack_speed_mult=p["cw_as"]),
                     cview("cw_frenzy"), sfx("cw"), voice("vo_cw", p))
    s_probe = combine(*rm("e_in", "w_in"), pick(p["ce_r"], "EnemyChampion", flag("e_in", 1)),
                      pick(p["cw_near"], "EnemyWithoutTower", flag("w_in", 1)))
    drop_on = rappel(p["ce_up"], p["ce_dmg"], p["ce_ap"])
    go_rappel = combine(flag("ce_cd", p["ce_cd"]), drop_on if nat else pick(p["ce_r"], "EnemyChampion", drop_on))
    spider_s2 = combine(s_probe, sw("ce_cd", sw("cw_cd", NONE, sw("w_in", frenzy)),
                                    sw("e_in", go_rappel, sw("cw_cd", NONE, sw("w_in", frenzy)))))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["s2_range"], "Targeting" if nat else "None", "EnemyWithoutTower",
                    combine(human, sw("sp", spider_s2, human_s2)), key="skill2")

    # ------------------------------------------------------------------ ult: the cocoon hunt
    def hunt(target):
        # the cast's target: the cocoon flies at it, the rappel and the bite land on it
        bite_hit = [magic(p["cq_dmg"], p["cq_ap"]), maxhp(p["cq_hp"]), view("cq_hit"), tsfx("cq_hit")]
        human_open = sw("sp", NONE, combine(anim("skill2", p["e_anim"]), sfx("e"), flag("e_cd", p["e_cd"]),
                                            aimed(p["r_range"], target, p["e_at"], cocoon_line(), direct=nat)))
        drop = combine(*rm("cq_cd", "ce_cd", "cw_cd"), flag("ce_cd", p["ce_cd"]), flag("cq_cd", p["cq_cd"]),
                       rappel(p["r_up"], p["r_dmg"], p["r_ap"],
                              [anim("c_skill", p["cq_dur"]), sfx("cq"),
                               delayed(p["cq_go"], *bite_hit)]))
        body = combine(human_open, cview("r_cast"), sfx("r"), voice("vo_r", p), delayed(p["r_go"], instant_spider, drop))
        return body if nat else pick(p["r_range"], target, body)
    if nat:     # the add-on's AI hook picks the champion (in crowd control first, else the lowest health)
        ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", hunt("EnemyChampion"), key="ult")
    else:
        r_go = combine(*rm("r_cc"), pick(p["r_range"], "EnemyChampionInCC", flag("r_cc", 1)),
                       sw("r_cc", hunt("EnemyChampionInCC"), hunt("EnemyChampionRecentlyAttacked")))
        ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "None", "EnemyChampionRecentlyAttacked", r_go, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("a_spit"), P_("q_bolt"), P_("e_web"), P_("w_spider")]
    views_e = [E("a_hit"), E("c_hit"), E("sl_bite1"), E("sl_bite2"), E("sl_bite3"), E("q_hit"), E("cq_hit"),
               E("e_hit"), E("w_boom", BIG, 2, False), E("w_hit"), E("ce_up", BIG, 3), E("ce_land", BIG, -1, False),
               E("ce_hit"), E("cw_frenzy", FX, 3), E("tf_spider", BIG, 3), E("tf_human", BIG, 3), E("r_cast", BIG, 3)]
    views_b = [B_("cw_on", FX, -1)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Range", "Melee", "CC"],
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
        kit["passive"] = {"passive_ref": "league_elise:queen",
                          "params": {"ce_r": p["ce_r"], "e_range": p["e_range"], "e_w": p["e_w"], "r_range": p["r_range"]}}
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
