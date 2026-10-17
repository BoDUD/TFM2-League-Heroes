"""Build league_renata.data_champion (support, Util) from the parameters P.

    python tools/kit/build_renata.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-17: 「方案可以，全按推荐做（辅助、Util，布局 A，做扩展包，PPU 1.5）」). TFM2 has three slots,
so W is fired by the passive controller (league_swain's W, league_zilean's armed rune):
  passive Leverage (物尽其用): her shot on an enemy champion (a hidden champion-only twin) deals p_hp% of its maximum
          health as true damage (League's bonus magic % max health; `ApAttack` has no target % part) and marks it for
          p_t ticks. The data cannot hear an ally's hit, so the mark (an `AddCasted` polling every p_per ticks: a 1-tick
          lob onto the carrier, a zone round it counting allied champions) pops when two allied champions stand within
          p_reach of it - she and one more, the one hitting it - at most once every p_gap ticks: p_pop + p_pop_ap% AP
          magic plus p_pop_hp% of its maximum health as true damage. The add-on pops it on real allied hits instead.
  attack  her pistol: a homing shot, a_ratio% AD.
  W       Bailout (及时救难), no slot of its own: every attack and every E checks (at most once every w_cd ticks) for an
          allied champion in crowd control within w_range, else - two enemy champions within w_near of her - any allied
          champion within w_r2; it gets w_as% attack speed and w_ms% move speed for w_t ticks and cannot drop below 1
          health meanwhile (`undying`), and a tick before the end w_heal + w_heal_ap% AP back. Data cannot see a
          takedown or read health, so League's "restored, then dies unless it gets a takedown" is the add-on's.
  skill   E Loyalty Program (忠诚激励): a `Targeting` cast on `EnemyWithoutTower` (e_range), the aim locked e_lock ticks
          before the release: the pair of missiles (one line, drawn as two) stops on the first enemy and bursts in
          e_r: e_dmg + e_ap% AP magic and an e_slow% slow for e_slow_t; a twin line passing through allies shields
          every allied champion it crosses (e_sh + e_sh_ap% AP for e_sh_t).
  skill2  Q Handshake (铁腕竞合): a `Targeting` cast on `EnemyChampion` (q_range), the aim locked q_lock ticks before the
          release: the hand stops on the first enemy (minions block, as in League): q_dmg + q_ap% AP magic and a root
          of q_root; then (an `AddCasted` on it, so the pull heads for her) it is flung through her, q_pull x q_pull_t
          units toward and past her (into her team), and where it lands every enemy within q_land_r takes q2_dmg +
          q2_ap% AP and, when the thrown one is a champion, a q_stun stun.
  ult     R Hostile Takeover (恶意收购): a 3-tick gate (league_yunara's) on `EnemyChampion` (r_range): two or more enemy
          champions within r_count, or an enemy champion in CC within r_range, fires it (else the cooldown comes back).
          A wide slow wave (penetrating, r_len) sends every enemy champion it crosses berserk for r_t ticks: it cannot
          attack her team or cast (disarm + silence), and every r_per ticks it lashes out at its own side - r_hit +
          r_hit_ap% AP magic on every enemy of hers within r_lash_r of it, itself guarded by a 4-tick 100% damage
          reduction. The add-on makes it walk to its nearest ally and hit with its own attack damage instead.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_renata.data_champion")
ID = "league_renata"
FX = "asset/league/effects/league_renata_fx"
BIG = "asset/league/effects/league_renata_big"

# Numbers: draft r0 from League's ratios scaled to the pack's supports (league_nami / janna / karma / lulu).
P = {
    # stats (Util, the pack's supports: attack 75-90 +6, ap 30 +15, hp 880-1000 +85); League's Renata: 550 range, 49 AD,
    # 545 +94 hp, 27 armour, 330 move, attack speed 0.625
    "hp": 900, "hp_g": 85, "atk": 80, "atk_g": 6, "ap": 30, "ap_g": 15, "def": 20, "def_g": 8, "mr": 22, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    # attack (tools/art/rig_renata.py: 60 + 60 ms of the pistol coming down level, the shot on frame 3 at 120 ms; a
    # projectile is drawn 5000 - y_offset over the pivot: the muzzle is 4.5 game px up, 24.5 forward)
    "atk_range": 55000, "atk_dur": 30, "atk_cd": 90, "a_st": 8, "a_ratio": 100, "shot_speed": 6000, "shot_y": 500,
    # passive Leverage (League: 1-6% max health + 2% per 100 AP on her hits; the same again when an ally pops the mark,
    # mark 4 s? -> p_t)
    "p_hp": 2, "p_t": 240, "p_per": 15, "p_reach": 60000, "p_gap": 45, "p_pop": 30, "p_pop_ap": 20, "p_pop_hp": 3,
    # W Bailout (League: cd 28-24 s, 5 s buff, AS 20-40% ramping, MS 20% toward enemies; on death restored to full, dies
    # 3 s later unless a takedown)
    "w_cd": 1500, "w_range": 80000, "w_r2": 60000, "w_t": 300, "w_as": 30, "w_ms": 20,
    "w_heal": 150, "w_heal_ap": 60, "w_anim": 18,
    # skill: E (League: 800 range, 65-245 + 55% AP, slow 30% 2 s, shield 50-230 + 50% AP 3 s, cd 14-10 s)
    # (the strip: 70 ms crouch, 80 ms the arm swept up, the missiles leave as it is thrown forward on frame 3, 150 ms)
    # (the missiles at the mechanical hand's height on frame 3: 13 game px up)
    "e_cd": 600, "e_range": 80000, "e_dur": 26, "e_rel": 9, "e_lock": 8, "e_speed": 4000, "e_len": 80000,
    "e_rad": 5000, "e_y": -8000, "e_r": 12000, "e_dmg": 70, "e_ap": 50, "e_slow": 30, "e_slow_t": 120,
    "e_sh": 90, "e_sh_ap": 50, "e_sh_t": 180,
    # skill2: Q (League: 900 range, 80-280 + 100% AP, root 1 s, recast throws ~400 units: 80-280 + 100% AP to what it
    # hits, stun 0.5 s if a champion was thrown, cd 16 s)
    "q_cd": 900, "q_range": 85000, "q_dur": 30, "q_rel": 12, "q_lock": 8, "q_speed": 4500, "q_len": 90000,
    "q_rad": 5000, "q_y": -5500, "q_dmg": 80, "q_ap": 70, "q_root": 50, "q_pull": 3000, "q_pull_t": 12,
    "q_land_r": 14000, "q2_dmg": 60, "q2_ap": 50, "q_stun": 30,
    # (the strip: the lunge's thrust on frame 3 at 200 ms = q_rel, the hand 10.5 game px up; the fling plays
    # skill2_fling, 400 ms)
    "q_fling_anim": 24,
    # ult: R (League: 2000 range, berserk 1.25 / 1.75 / 2.25 s, cd 150-110 s)
    "r_cd": 4800, "r_range": 75000, "r_arm": 360, "r_ally": 45000, "fight_r": 70000, "watch_p": 15, "r_anim": 40, "r_rel": 18, "r_speed": 2000, "r_len": 100000,
    "r_w": 14000, "r_t": 105, "r_per": 30, "r_lash_r": 25000, "r_hit": 55, "r_hit_ap": 40,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # the add-on's copy: 1 = Leverage, Bailout and the berserk left to league_renata:glasc
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


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def casted(dur, period, *effects, kind="Bleed"):
    """Effects run on a unit every `period` ticks for `dur` (its caster is still her: a pull heads for her, a projectile
    flies from her to the carrier)."""
    return {"type": "AddCasted", "casted_type": kind, "duration": dur, "period": period, "effects": list(effects)}


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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


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


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def lives(*effects):
    """A `Delayed` chain's effects only while she lives (a dead caster's Delayed effects run in the game): a 1-tick
    flag from a search that finds no dead caster; the copy in the search is what the AI reads (champion-data 5)."""
    return combine(pick(1, "AllyOnlySelf", flag("live", 1)),
                   sw("live", combine(*effects), pick(1, "AllyOnlySelf", *effects)), *rm("live"))


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Leverage's mark
    pop = combine(flag("p_gap", p["p_gap"]), magic(p["p_pop"], p["p_pop_ap"]), true_hp(p["p_pop_hp"]),
                  view("p_pop"), tsfx("p_pop"))
    # every p_per ticks: a lob onto the marked champion; round where it lands, count her allied champions (the
    # scan hits on the zone's first tick), then the pop zone (two ticks later, the carrier alone at its centre)
    probe = lob("p_probe", 1, 1000, "Enemy", [], end=[
        zone("p_scan", p["p_reach"], "AllyChampion", [sw("p_n1", flag("p_n2", 3), flag("p_n1", 3))]),
        zone("p_hit", 3000, "EnemyChampion", [sw("p_n2", sw("p_gap", NONE, pop)), *rm("p_n1", "p_n2")], delay=3)])
    mark = combine(true_hp(p["p_hp"]), buff("p_mark", p["p_t"]), tsfx("p_hit"), casted(p["p_t"], p["p_per"], probe))
    if p["native"]:
        mark = combine(true_hp(p["p_hp"]), buff("p_mark", p["p_t"]))   # the add-on pops it on allied hits

    # ------------------------------------------------------------------ W: Bailout, fired by the controller
    def bail():
        return combine(flag("w_cd", p["w_cd"]),
                       buff("w_buff", p["w_t"], attack_speed_mult=p["w_as"], move_speed_mult=p["w_ms"],
                            undying=True),
                       view("w_cast"), tsfx("w_buff"), anim("skill_w", p["w_anim"]), sfx("w"), voice("vo_w", p),
                       delayed(p["w_t"] - 1, {"type": "Heal", "amount": p["w_heal"], "attack_ratio": 0,
                                              "ap_ratio": p["w_heal_ap"], "heal_type": "Ally"}, view("w_save"),
                               tsfx("w_save")))

    # League's Bailout never goes on herself: AllyChampion would pick her, AllyNotSelf also minions - so a hidden
    # homing shot at an AllyNotSelf unit that only takes on an allied champion (w_cd is set on that hit; a minion
    # picked costs nothing, the watch tries again)
    def bail_on(rng, target):
        return pick(rng, target, homing("w_bolt", 20000, 0, "AllyChampion", [sw("w_cd", NONE, bail())]))

    # ------------------------------------------------------------------ the watch (W's and R's moments)
    # a life-long AddCasted on her (league_swain's), started by her first attack or R press of each life: every
    # watch_p ticks it counts enemy champions within fight_r (c_e1, c_e2), allied champions within r_ally (c_a1, c_a2 =
    # one besides her) and an enemy champion in CC within r_range (c_cc)
    tick = p["watch_p"]
    count = combine(*rm("c_e1", "c_e2", "c_a1", "c_a2", "c_cc"),
                    around(p["fight_r"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]),
                    around(p["r_ally"], "AllyChampion", [sw("c_a1", flag("c_a2", 3), flag("c_a1", 3))]),
                    pick(p["r_range"], "EnemyChampionInCC", flag("c_cc", 3)))
    # W: an allied champion in CC within w_range first, else in a fight (two enemy champions close) one near her
    danger = combine(*rm("w_cc"), pick(p["w_range"], "AllyChampionInCC", flag("w_cc", 1)),
                     sw("w_cc", bail_on(p["w_range"], "AllyChampionInCC"),
                        sw("c_e2", bail_on(p["w_r2"], "AllyNotSelf"))), *rm("w_cc"))
    cast_w = NONE if p["native"] else sw("w_cd", NONE, danger)
    # ------------------------------------------------------------------ attack
    shot = homing("a_shot", p["shot_speed"], p["shot_y"], "Enemy",
                  [attack(0, p["a_ratio"]), view("a_hit"), tsfx("a_hit")])
    twin = homing("a_twin", p["shot_speed"], p["shot_y"], "EnemyChampion", [mark])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), shot, twin), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ E: Loyalty Program
    burst = zone("e_burst", p["e_r"], "EnemyWithoutTower",
                 [magic(p["e_dmg"], p["e_ap"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                  view("e_hit"), tsfx("e_hit")])
    missiles = line("e_missile", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyWithoutTower", False, [],
                    end=[burst, view("e_boom"), sfx("e_boom")])
    friends = line("e_ally", p["e_speed"], p["e_len"], p["e_rad"] * 2, p["e_y"], "AllyNotSelf", True,
                   [{"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_sh_ap"],
                     "tick": p["e_sh_t"]}, view("e_shield"), tsfx("e_shield")])
    e_cast = combine(sfx("e"), voice("vo_e", p),
                     lob("e_aim", p["e_lock"], 1000, "EnemyWithoutTower", [], end=[missiles, friends, sfx("e_fly")]))
    skill = action("skill", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                   delayed(p["e_rel"] - p["e_lock"] - 1, lives(e_cast)))

    # ------------------------------------------------------------------ Q: Handshake
    crash = zone("q_crash", p["q_land_r"], "EnemyWithoutTower",
                 [magic(p["q2_dmg"], p["q2_ap"]), sw("q_champ", {"type": "Stun", "duration": p["q_stun"]}),
                  view("q_crash_hit"), tsfx("q_crash")])
    land = lob("q_land", 1, 1000, "Enemy", [], end=[crash, view("q_land")])
    # the fling: the pull through her, and her yank (the skill2_fling strip; the casted effect's caster is still her)
    fling = combine({"type": "Pull", "speed": p["q_pull"], "tick": p["q_pull_t"]}, view("q_fling"), tsfx("q_fling"),
                    anim("skill2_fling", p["q_fling_anim"]))
    caught = [magic(p["q_dmg"], p["q_ap"]), {"type": "Bind", "duration": p["q_root"]}, view("q_hit"), tsfx("q_hit"),
              pick(1000, "EnemyChampion", flag("q_champ", p["q_root"] + p["q_pull_t"] + 6), fp=True),
              casted(p["q_root"], p["q_root"], fling),
              casted(p["q_root"] + p["q_pull_t"], p["q_root"] + p["q_pull_t"], land)]
    hand = line("q_hand", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower", False, caught)
    q_cast = combine(sfx("q"), voice("vo_q", p),
                     lob("q_aim", p["q_lock"], 1000, "EnemyWithoutTower", [], end=[hand, sfx("q_fly")]))
    skill2 = action("skill2", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyChampion",
                    delayed(p["q_rel"] - p["q_lock"] - 1, lives(q_cast)))

    # ------------------------------------------------------------------ R: Hostile Takeover
    lash = combine(buff("r_guard", 4, damaged_reduce=100),
                   lob("r_lash", 1, 1000, "Enemy", [],
                       end=[zone("r_lash_hit", p["r_lash_r"], "EnemyWithoutTower",
                                 [magic(p["r_hit"], p["r_hit_ap"]), view("r_lash_hit")]), view("r_lash")]))
    berserk = [{"type": "BlockAttack", "tick": p["r_t"]}, {"type": "BlockSkill", "tick": p["r_t"]},
               buff("r_berserk", p["r_t"]), view("r_hit"), tsfx("r_hit")]
    if not p["native"]:
        berserk.append(casted(p["r_t"], p["r_per"], lash))
    wave = line("r_wave", p["r_speed"], p["r_len"], p["r_w"], 0, "EnemyChampion", True, berserk)
    # from the watch the wave needs a target: an enemy champion in CC within r_range first, else any there
    aim = lob("r_aim", 1, 1000, "EnemyChampion", [], end=[wave])
    release = combine(sfx("r_wave"), *rm("r_aimed"), pick(p["r_range"], "EnemyChampionInCC", flag("r_aimed", 2), aim),
                      sw("r_aimed", NONE, pick(p["r_range"], "EnemyChampion", aim)), *rm("r_aimed"))
    fire = sw("r_go", combine(*rm("r_go", "r_arm"), anim("ult", p["r_anim"]), sfx("r"), voice("vo_r", p),
                              cview("r_cast"), delayed(p["r_rel"] - 1, lives(release))))
    # r_ok: two enemy champions close, or an enemy champion in CC with an ally of hers near; with the window open, R
    ok = sw("r_arm", flag("r_go", 1))
    arm = sw("c_e2", ok, sw("c_cc", sw("c_a2", ok)))
    watch = on_me(casted(1000000, tick, count, delayed(1, cast_w, arm, fire)))
    life = sw("init", NONE, combine(flag("init", None), watch))
    attack_a["effect"]["effects"].insert(0, life)
    # the slot only arms R for r_arm ticks; unused, the window ends with the cooldown capped at 60 ticks
    # (cooltime x 100 / (100 + mult), league_tahmkench's r_retry); league_orianna's x trick makes the game's AI score
    # the lash's damage instead of a bare flag
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(*rm("r_arm"), flag("r_arm", p["r_arm"]), on_me(delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), magic(p["r_hit"] * 3, p["r_hit_ap"] * 3)),
                     *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(life, scored),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_shot"), P_("e_missile"), P_("q_hand"), P_("r_wave", BIG, 3)]
    views_e = [E("a_hit"), E("p_pop"), E("w_cast"), E("w_save", FX, 3), E("e_hit"), E("e_boom", FX, 2, **LATE),
               E("e_shield"), E("q_hit"), E("q_fling"), E("q_land", FX, -1, **LATE), E("q_crash_hit"),
               E("r_cast", BIG, -1), E("r_hit"), E("r_lash", FX, -1, **LATE), E("r_lash_hit")]
    views_b = [B_("p_mark", FX, 3), B_("w_buff", FX, -1), B_("e_slow", FX, -1), B_("r_berserk", FX, 3)]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": f"{ID}:glasc",
                            "params": {k: p[k] for k in ("p_t", "p_pop", "p_pop_ap", "p_pop_hp", "w_cd", "w_t",
                                                         "w_as", "w_ms", "r_t", "r_per")}}
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "CC", "Shield"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
        p[k] = json.loads(v) if isinstance(p[k], (list, tuple)) else (type(p[k])(float(v)) if isinstance(p[k], int)
                                                                      else float(v))
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
