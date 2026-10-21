"""Build league_naafiri.data_champion (jungle, Assassin: the Hound of a Hundred Bites) from the parameters P.

    python tools/kit/build_naafiri.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (group F, 2026-10-21; JUNGLE - the user: 「改打野啊」 (League plays her mid too); League 16.20's Naafiri; layout A - Q / E / R, the passive in every hit, W folded into
the ult; 「有连招要做连招」). TFM2 has three active slots: Darkin Daggers (Q) is `skill`, Eviscerate (E) `skill2`,
Hounds' Pursuit (League's R key, NaafiriW in the bins) the `ult`, opened by The Call of the Pack (League's W key,
NaafiriR), as the pros cast them (W -> R).
  passive We Are More (狂烈种群): League's packmates are units that follow her and bite her targets. Summons cannot
          walk or attack in data (champion-data "A summon that follows its target"), so the pack is pictures and
          damage riding on her hits: every attack hit and every ability hit on an enemy is also a pack bite (pk_dmg +
          pk_ratio% AD, the pack's picture on the target; non-champions take pk_minion% of it, League's 50%). While the
          Call of the Pack holds (`pack4`) the pack is four and every bite twice as strong (League: +2 packmates).
  attack  A lunge and a bite, the hit on tick a_hit (attack, then the pack's bite).
  skill   Q Darkin Daggers (暗裔犬牙, one cooldown `q_cd`): a `Targeting` cast on `EnemyWithoutTower` (camps and waves
          too). She flings the first dagger: q_dmg + q_ratio% AD and a bleed of q_b_dmg + q_b_ratio% AD over q_bleed
          ticks; a champion it hits is leapt on by the pack (League: packmates leap to the champion or monster hit) -
          the pack rides on it for pk_ride ticks and bites every pk_period (Tibbers' way: an `AddCasted` on the
          target, its pictures `is_follow`; its death ends the ride). COMBO (League's recast): for q_win ticks her next
          attack is the second dagger instead - q2_dmg + q2_ratio% AD (League's "bonus damage when it already bleeds":
          the first dagger just made it bleed), and a champion it hits heals her q_heal + q_heal_r% AD (League's
          second-cast heal). League's execute (more damage on low health) reads the target's health: not in data.
  skill2  E Eviscerate (剔骨本能, one cooldown `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range). She dashes
          onto the target (`MoveToTarget`) and shreds everything round her twice (e_r): e_dmg + e_ratio% AD, then
          e2_dmg + e2_ratio% AD; the pack, called back to her, bites the target as she lands.
  ult     R Hounds' Pursuit (猎狗血性) opened by W The Call of the Pack (暴吼): a `Targeting` cast on `EnemyChampion`
          within r_range. The roar first: untargetable for r_imm ticks (`damaged_reduce` 100 + `cc_immune`, the
          champion-data "Untargetable window" way: she stays in the fight), and `pack4` for roar_t ticks: +roar_ad%
          attack, +roar_ms% move speed, the pack doubled. r_roar ticks later she and the pack pounce on the champion
          (`MoveToTarget`): r_dmg + r_ratio% AD, a r_slow% slow for r_slow_t and -r_shred% armour for r_shred_t (League's
          shred), the pack's bite. A takedown within r_win ticks of the pounce (league_viego's takedown window: a casted
          effect on the champion keeps a 2-tick flag up, one on her reads it) lets her cast it once more (`r_again`,
          r_recast ticks; the cooldown capped by a 2-tick `ult_cooldown_mult`): the recast is the pounce alone, with a
          shield of r_sh + r_sh_r% AD for r_sh_t ticks (League's second cast).
  combos  R -> Q -> Q2 -> E (猎狗血性扑上去 -> 暗裔犬牙 -> 第二把匕首 -> 剔骨本能): the pounce's landing throws the first dagger at
          once if Q is ready; the second dagger rides her next attack; its hit runs Eviscerate at once if E is ready
          (the dash is already on the target). A takedown in the window: the pounce again onto the next champion.
Timings: drafts until the frames exist (a_hit, q_rel, e_at / e2_at, r_roar / r_at). Numbers: candidate g2 of the
classic-SDK simulations (C:/t/nf_sim, kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, 2026-10-21):
+1.48 on seeds 1-8 and +1.25 on 9-16 (league_graves +1.57 / +0.02, league_warwick +0.57 on 1-8 the same day). The
draft g1 (attack 112 +22, the pack 10 + 16%, the bleed 40 + 60%, the pounce 80 + 80%) was +5.07 mid (league_talon
+2.75) and +3.90 in the jungle; g3 (all of g2's cuts and more) -1.26. The draft also panicked the engine in 170 of
240 games until the decoys (below) gave her second dagger a damage the AI can read.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_naafiri.data_champion")
ID = "league_naafiri"
FX = "asset/league/effects/league_naafiri_fx"
BIG = "asset/league/effects/league_naafiri_big"

# League's Naafiri (16.20, CommunityDragon naafiri.bin): 610 +105 hp, 55 AD +2, 28 +4.7 armour, 340 move, 125 range.
# Passive: packmates bite with 4% bonus AD each (non-champions 50%), leap 75-1200. Q: 35-55 + 20% bonus AD and a bleed
# 35-185 + 80% bonus AD over 5 s, the recast 30-? + 40% bonus AD (x2 on low health) and a heal 45-75 + 40% bonus AD,
# recast within 4 s; cd 9-7 s. W (her R key) Hounds' Pursuit: 125-275 damage, 1800 dash, 99% slow 0.25 s, armour shred
# 3 s, a takedown within 7 s recasts it within 12 s with a 100-200 shield; cd 110-80 s. R (her W key) The Call of the
# Pack: +2 packmates, untargetable 1 s, 20-25% move speed and +20% AD 5 s; cd 26-18 s. E Eviscerate: a 350 dash and
# two shreds round her, the pack recalled and healed; cd 11-7 s.
P = {
    # stats (Assassin base: attack 120 +30, hp 900 +80, defence 25, mr 15, move 1100, range 23000; league_talon 122 +25,
    # 930 +88 hp, 26 +8 def)
    "hp": 940, "hp_g": 88, "atk": 100, "atk_g": 18, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    "atk_range": 23000, "atk_dur": 25, "atk_cd": 58, "a_hit": 8, "a_speed": 20000,
    # passive: the pack's bite on every hit (two packmates; four in `pack4`)
    "pk_dmg": 8, "pk_ratio": 12, "pk_minion": 50, "pk_ride": 180, "pk_period": 45,
    # skill: Q Darkin Daggers
    "s_cd": 60, "q_cd": 480, "q_range": 50000, "q_dur": 22, "q_rel": 8, "q_speed": 5000,
    "q_dmg": 30, "q_ratio": 25, "q_b_dmg": 30, "q_b_ratio": 45, "q_bleed": 300, "q_b_period": 30,
    "q_win": 240, "q2_dur": 22, "q2_rel": 8, "q2_dmg": 35, "q2_ratio": 55, "q_heal": 35, "q_heal_r": 30,
    # skill2: E Eviscerate
    "s2_cd": 60, "e_cd": 600, "e_range": 32000, "e_dur": 26, "e_speed": 4500, "e_at": 4, "e2_at": 12, "e_r": 18000,
    "e_dmg": 35, "e_ratio": 50, "e2_dmg": 25, "e2_ratio": 40,
    # ult: R Hounds' Pursuit opened by W The Call of the Pack
    "r_cd": 3000, "r_range": 60000, "r_roar": 24, "r_imm": 45, "roar_t": 300, "roar_ad": 20, "roar_ms": 20,
    "r_dur": 22, "r_speed": 4500, "r_at": 2, "r_dmg": 70, "r_ratio": 65, "r_slow": 99, "r_slow_t": 15,
    "r_shred": 20, "r_shred_t": 180, "r_win": 420, "r_recast": 720, "r_sh": 70, "r_sh_r": 40, "r_sh_t": 180,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_naafiri: the second dagger's hit is its Native execute (up to q_exec% more damage
    # by the target's missing health), the pounce arms `r_armed` for r_win ticks instead of the takedown window and the
    # add-on's passive league_naafiri:pack gives the recast on any champion takedown (on_kill / on_assist)
    "native": 0, "q_exec": 100,
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


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


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


def heal(amount, ratio=0):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action (build_gangplank.py's way): its estimate follows a SwitchByBuff by
    the flags she has while it reads, and its battle plan divides an enemy's health by her attack's estimate - with
    every hit behind the alive guard her second dagger read 0 (classic simulator, 2026-10-21: "attempt to divide by
    zero" at game_core plan_legacy/sub_plan/battle.rs:1938 in 170 of 240 games). A flag she never has while it reads;
    on the cast the flag is up and the hit is skipped, so nothing she does changes."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: the pack's bite
    def bite_on(target_kind):
        """The pack's bite as effects on a unit already hit: full on champions, pk_minion% on the rest; doubled in
        `pack4` (League's two extra packmates)."""
        k = p["pk_minion"] / 100 if target_kind == "minion" else 1
        one = attack(round(p["pk_dmg"] * k), round(p["pk_ratio"] * k))
        two = attack(round(2 * p["pk_dmg"] * k), round(2 * p["pk_ratio"] * k))
        return sw("pack4", combine(two, view("pk_bite4")), combine(one, view("pk_bite")))

    # one homing pair carries every pack bite: the champion twin bites in full, the `Enemy` one a non-champion (a
    # champion is skipped there by the `pk_seen` flag its twin raised: both fly at 100000 and the champion twin,
    # spawned first, hits first in the same tick, champion-data section 4)
    def pack_bite():
        champ = homing("pk_c", 100000, "EnemyChampion",
                       [refresh("pk_seen", 2), bite_on("champion"), tsfx("pk_bite")])
        rest = homing("pk_m", 100000, "Enemy", [sw("pk_seen", NONE, combine(bite_on("minion"), tsfx("pk_bite")))])
        return combine(champ, rest)

    # the ride (League: packmates leap to the champion the daggers hit): Tibbers' way, a casted effect on the champion
    ride = casted(p["pk_ride"] + 1, p["pk_period"],
                  sw("pack4", attack(2 * p["pk_dmg"], 2 * p["pk_ratio"]), attack(p["pk_dmg"], p["pk_ratio"])),
                  view("pk_ride"), tsfx("pk_bite"), kind="Bleed")

    # ------------------------------------------------------------------ skill2: E Eviscerate (the body, reused by Q2)
    def e_body():
        shred = lambda dmg, ratio: around(p["e_r"], "EnemyWithoutTower", [attack(dmg, ratio), view("e_hit"),
                                                                             tsfx("e_hit")])
        land = [cview("e_slash"), sfx("e_slash"), shred(p["e_dmg"], p["e_ratio"]), pack_bite(),
                delayed(p["e2_at"] - p["e_at"], alive(cview("e_slash2"), sfx("e_slash2"),
                                                     shred(p["e2_dmg"], p["e2_ratio"])))]
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                       {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 20000,
                        "end_effects": [delayed(p["e_at"], alive(*land))]})

    # ------------------------------------------------------------------ skill: Q Darkin Daggers (the first dagger)
    k = p["q_bleed"] // p["q_b_period"]
    bleed = casted(p["q_bleed"] + 1, p["q_b_period"], attack(p["q_b_dmg"] // k, p["q_b_ratio"] // k), view("q_bleed"),
                   kind="Bleed")
    dagger1 = homing("q_dagger", p["q_speed"], "EnemyWithoutTower",
                     [attack(p["q_dmg"], p["q_ratio"]), bleed, view("q_hit"), tsfx("q_hit")])
    leap = homing("q_leap", p["q_speed"], "EnemyChampion", [ride, view("pk_leap"), tsfx("pk_leap")])   # the champion twin: the ride

    def q1():
        return combine(refresh("q_cd", p["q_cd"]), refresh("q2", p["q_win"]), decoy(p["q_dmg"], p["q_ratio"]),
                       anim("skill", p["q_dur"]), sfx("q"),
                       voice("vo_q", p), delayed(p["q_rel"] - 1, alive(dagger1, leap, pack_bite())))

    skill = action("idle", 3, p["s_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q1()), key="skill")

    # ------------------------------------------------------------------ attack (and Q's second dagger)
    a_bite = homing("a_bite", p["a_speed"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    attack_plain = combine(sfx("a"), delayed(p["a_hit"] - 1, a_bite, pack_bite()))
    # the second dagger; its champion hit heals her and opens Eviscerate at once when E is ready (the combo)
    q2_hit = {"type": "Native", "effect_ref": "league_naafiri:q2"} if p["native"] else attack(p["q2_dmg"], p["q2_ratio"])
    dagger2 = homing("q2_dagger", p["q_speed"], "EnemyWithoutTower", [q2_hit, view("q2_hit"), tsfx("q2_hit")])
    heal2 = homing("q2_heal", p["q_speed"], "EnemyChampion",
                   [on_me(heal(p["q_heal"], p["q_heal_r"]), cview("q_heal")), refresh("q2_land", 2)])
    q2_atk = combine(*rm("q2"), decoy(p["q2_dmg"], p["q2_ratio"]), anim("skill", p["q2_dur"]), sfx("q2"),
                     delayed(p["q2_rel"] - 1, alive(dagger2, heal2, pack_bite())),
                     delayed(p["q2_rel"] + 1, alive(sw("e_cd", NONE, e_body()))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      sw("q2", q2_atk, attack_plain), atype="BaseAttack", cancel=True)

    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    sw("e_cd", NONE, e_body()), key="skill2")

    # ------------------------------------------------------------------ ult: W The Call of the Pack -> R Hounds' Pursuit
    # takedown window (league_viego's): the champion pounced on keeps `r_alive` (2 ticks) up while it lives; her
    # watcher, two ticks behind, reads it every tick and a lapse inside the window is a takedown -> the recast
    reset = combine(*rm("r_watch"), refresh("r_again", p["r_recast"]),
                    refresh("r_reset", 2, ult_cooldown_mult=10000), cview("r_reset"), sfx("r_reset"))
    watch = combine(refresh("r_watch", p["r_win"]),
                    on_me(delayed(2, casted(p["r_win"] - 2, 1, sw("r_watch", sw("r_alive", NONE, reset))))))
    pounce_hit = [attack(p["r_dmg"], p["r_ratio"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
                  buff("r_shred", p["r_shred_t"], defence_mult=-p["r_shred"]), view("r_hit"), tsfx("r_hit")]

    def pounce(first):
        """The pounce on the champion; the first cast arms the takedown window, the recast shields her instead."""
        hit = pounce_hit + ([casted(p["r_win"], 1, flag("r_alive", 2))] if first and not p["native"] else [])
        armed = refresh("r_armed", p["r_win"]) if p["native"] else watch  # the add-on's passive reads the takedowns
        land = [homing("r_bite", 100000, "EnemyChampion", hit), pack_bite(),
                armed if first else None,                               # the window opens on the landing
                sw("q_cd", NONE, q1())]                                 # the combo: the first dagger at once
        return combine(anim("ult_b", p["r_dur"]), sfx("r_dash"),
                       None if first else combine(*rm("r_again"), on_me(shield(p["r_sh"], p["r_sh_r"], p["r_sh_t"])),
                                                  flag("r_shield", p["r_sh_t"])),
                       {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 30000,
                        "end_effects": [delayed(p["r_at"], alive(*[e for e in land if e is not None]))]})

    roar = combine(anim("ult", p["r_roar"]), sfx("r_roar"), voice("vo_r", p), cview("r_roar"),
                   refresh("r_imm", p["r_imm"], damaged_reduce=100, cc_immune=True),
                   refresh("pack4", p["roar_t"], attack_mult=p["roar_ad"], move_speed_mult=p["roar_ms"]),
                   delayed(p["r_roar"], alive(pounce(True))))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 sw("r_again", pounce(False), roar), key="ult")

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_dagger"), P_("q2_dagger"), P_("q_leap", FX, 0)]
    views_e = [E("a_hit"), E("pk_bite"), E("pk_bite4", BIG), E("pk_leap"), E("pk_ride", BIG, -1), E("q_hit"),
               E("q_bleed"), E("q2_hit"), E("q_heal", FX, 3), E("e_slash", BIG, -1), E("e_slash2", BIG, -1),
               E("e_hit"), E("r_roar", BIG, 3), E("r_hit"), E("r_reset", FX, 3)]
    views_b = [B_("pack4", BIG, -1, "pack_aura"), B_("r_shred", FX, 3), B_("r_shield", FX, 3)]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": "league_naafiri:pack",
                            "params": {k: int(p[k]) for k in ("r_recast", "r_win", "q2_dmg", "q2_ratio", "q_exec")}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"], **extra,
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
