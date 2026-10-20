"""Build league_ziggs.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_ziggs.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-18: mid, layout A, a small add-on, PPU 1.5 - 「可以」). TFM2 has three active slots:
Bouncing Bomb is `skill`, Hexplosive Minefield `skill2`, Mega Inferno Bomb the `ult`; Satchel Charge (W) has no slot -
the watch throws it (league_jarvaniv's W the same way).
  passive Short Fuse (一触即发): every p_t ticks his next attack deals p_dmg + p_ratio% AP more. Each skill he casts (Q,
          W, E, R) cuts the wait by a third (League: 12 s, -4 s a cast). Nothing takes time off a buff, so the wait is
          three flags laid at once (p_a / p_b / p_c, a third, two thirds and all of p_t: league_xerath's Mana Surge
          way); the empowered attack needs none left, and each cast removes the longest one still on.
  attack  a small bomb (100% AD), a homing bomb on `Enemy` (towers too) released on a_rel; its champion-only twin
          marks the fight. Empowered: a big bomb and the passive's damage on the same target.
  skill   Q Bouncing Bomb (弹跳炸弹), `Targeting` on `EnemyWithoutTower` (q_range): the bomb lands three times along
          the line toward the target (q_l1 / q_l2 / q_l3 from him, at q_t1 / +q_t2 / +q_t3 ticks): each landing blows
          up if an enemy stands within q_r (q_dmg + q_ratio% AP to every enemy there) and the bomb stops; the third
          always blows up. Projectiles start at the caster (champion-data: nothing flies on from a landing point), so
          each landing is a hidden line from him whose end_effects act where it stops, all spawned on the release
          tick (one aim, locked); the bomb in the air is stamped on its path (q_air<h>, a frame a stamp, its height
          above the ground drawn into the picture - left-right symmetric, so both sides read).
  skill2  E Hexplosive Minefield (海克斯爆破雷区), `Position` on `EnemyWithoutTower` (e_range): the mines land where the
          target stood (e_travel ticks) and lie e_t ticks in e_r, armed after e_arm. The first mine an enemy sets off
          is whole (e_dmg + e_ratio% AP: an `ApplyInProjectile` hits each unit once for its whole life - League's
          per-target falloff), every e_p ticks after that while he stays in, one more at e_low% of it; each mine slows
          e_slow% for e_slow_t ticks. The mines lie as one field (League's vanish one by one).
  W       Satchel Charge (定点爆破), cast by the watch from level 3: an enemy champion within w_trig, w_cd off, not busy
          -> the satchel goes off at his feet on w_rel: w_dmg + w_ratio% AP within w_r, every enemy there knocked away
          from him (w_kb a tick for w_kb_t), and he is blown back (MoveBack w_hop x w_hop_t) from the champion that
          came at him. League throws it anywhere and pushes from the blast point; data pushes only away from the
          caster (champion-data: Knockback), which is the at-his-feet escape. Tower hexplode: the add-on.
  ult     R Mega Inferno Bomb (科学的地狱火炮): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only
          arms the ult for r_arm ticks (league_anivia / league_swain); the watch throws it at an enemy champion in crowd
          control within r_range, or - after r_wait ticks of the window - at one his team hit recently
          (`EnemyChampionRecentlyAttacked`, anywhere in reach: League's map-wide help). The bomb lands where the champion
          stood when it left (r_travel ticks, a red ring on the spot the whole flight): r_dmg + r_ratio% AP within r_r,
          and the centre (r_cr) r_cdmg + r_cratio% more (League: 65% outside). Unused, the window ends with the
          cooldown capped at 60 ticks (`r_retry`).
  watch   A life-long `AddCasted` started by his first attack or R press of each life (`init`), every watch_p ticks:
          throws R when the moment holds, sets off W.
The add-on copy (--native, addons/league_ziggs): the passive league_ziggs:hexplode reads towers' health - with W off
cooldown it blows up an enemy tower within w_hex_r below w_ex% of its health (League: 25-35%) and puts W on cooldown;
Short Fuse's bomb (the copy raises `p_now` on him as it hits) deals p_tower% to towers.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_ziggs.data_champion")
ID = "league_ziggs"
FX = "asset/league/effects/league_ziggs_fx"
BIG = "asset/league/effects/league_ziggs_big"

# League units x 100 = ours (attack range 550 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings from the strips (tools/art/rig_ziggs.py MS): the attack's throw frame 3 from tick 9.6 (a_rel 10),
# Q's frame 4 from 13.2 (q_rel 13), E's frame 3 from 9 (e_rel 9), W's blast frame 3 from 8.4 (w_rel 8), R's heave frame 4
# from 15.6 (r_rel 16). Numbers = the 10-min classic-SDK simulations (mid lane 2 against pyromancer, ice_mage,
# lightning_mage, wind_mage and white_mage, three lineups, both sides, 8 seeds, 2026-10-18; league_syndra +1.17): the
# draft (Q 75 + 60% every 5 s, E 45 + 30%, W 60 + 40%, R 190 + 65% / centre 100 + 35%, P 30 + 50%, hp 880) +0.01
# (deal 8772); +25% +0.14; +40% with Q every 4.5 s and hp 900 +1.06 (deal 10739) = P.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Ziggs:
    # 606 +106 hp, 21 armour, 30 mr, 325 move, 550 range, attack speed 0.656
    "hp": 900, "hp_g": 95, "atk": 76, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 88, "a_rel": 10, "a_speed": 4000, "f_t": 180,
    # passive Short Fuse (League: 20-184 +50% AP, every 12 s, -4/5/6 s a cast, x1.75 on structures)
    "p_t": 720, "p_dmg": 40, "p_ratio": 60, "p_tower": 175,
    # Q Bouncing Bomb (League: 850 range (1400 with the bounces), 80-280 +60-80% AP, r 240, bounces 0.495 s each,
    # cd 6-4)
    "q_cd": 270, "q_range": 80000, "q_dur": 31, "q_rel": 13, "q_l1": 40000, "q_l2": 62000, "q_l3": 84000,
    "q_t1": 26, "q_t2": 30, "q_t3": 30, "q_r": 20000, "q_dmg": 105, "q_ratio": 85, "q_h1": 18, "q_h2": 10, "q_h3": 6,
    "q_step": 3,
    # E Hexplosive Minefield (League: 900 range, 11 mines r 335 for 10 s, armed 0.5 s, 30-190 +25-45% AP, later
    # mines 40%, slow 10-50% 1.5 s, cd 16)
    "e_cd": 720, "e_range": 75000, "e_dur": 27, "e_rel": 9, "e_travel": 20, "e_r": 30000, "e_t": 300, "e_arm": 30,
    "e_p": 30, "e_dmg": 65, "e_ratio": 45, "e_low": 40, "e_slow": 30, "e_slow_t": 90, "e_show": 15,
    # W Satchel Charge (League: 70-210 +50% AP, r 325, knockback 500 / 0.5 s, self 825, cd 20-12)
    "w_cd": 900, "w_trig": 22000, "w_r": 30000, "w_dur": 24, "w_rel": 8, "w_dmg": 80, "w_ratio": 50,
    "w_kb": 3000, "w_kb_t": 10, "w_hop": 4000, "w_hop_t": 10, "w_ex": 30, "w_hex_r": 60000,
    # R Mega Inferno Bomb (League: 5000 range, r 525 (centre 250), 300-700 +100% AP at the centre, 65% outside,
    # cd 120-70)
    "r_cd": 3600, "r_range": 220000, "r_arm": 600, "r_wait": 300, "r_dur": 36, "r_rel": 16, "r_travel": 70,
    "r_r": 55000, "r_cr": 25000, "r_dmg": 250, "r_ratio": 85, "r_cdmg": 135, "r_cratio": 45,
    "watch_p": 12,
    "vo_gap": 600,
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


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def mover(name, rng, ticks, end):
    """A hidden line from him toward the action's target, stopping rng away after about `ticks`; its end_effects act
    on that point (a `Delayed` there keeps it)."""
    return {"type": "LinearProjectile", "name": n(name), "speed": max(1, round(rng / ticks)), "range": rng,
            "y_offset": 5000, "penetrate": True, "shape": circle(1000), "applied_target": "EnemyChampion",
            "applied_effects": [], "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point; `seen` = the
    telegraph played on the landing point the whole flight."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def once(name, radius, tick, effects, target="EnemyWithoutTower"):
    """Each unit hit once over the zone's whole life, on the tick it first touches it (league_thresh R)."""
    return {"type": "ApplyInProjectile", "name": n(name), "shape": circle(radius), "tick": tick,
            "follow_caster": False, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def air_heights(p):
    """Every stamp of the bomb in the air: (k, distance from him, tick after the release, height in game px)."""
    out, t0, d0 = [], 0, 0
    for k, (d1, t, h) in enumerate(((p["q_l1"], p["q_t1"], p["q_h1"]), (p["q_l2"], p["q_t2"], p["q_h2"]),
                                    (p["q_l3"], p["q_t3"], p["q_h3"])), 1):
        for s in range(p["q_step"], t, p["q_step"]):
            f = s / t
            out.append((k, round(d0 + (d1 - d0) * f), t0 + s, round(4 * h * f * (1 - f))))
        t0, d0 = t0 + t, d1
    return out


def build(p):
    native = bool(p["native"])
    marked = [refresh("fight", p["f_t"])]

    # ------------------------------------------------------------------ passive: Short Fuse (the wait = 3 flags)
    third = p["p_t"] // 3
    fuse_lit = combine(flag("p_a", third), flag("p_b", 2 * third), flag("p_c", p["p_t"]))
    # each skill cast takes a third off: the longest flag still on goes
    cut = sw("p_c", combine(*rm("p_c")), sw("p_b", combine(*rm("p_b")), sw("p_a", combine(*rm("p_a")))))
    ready = lambda yes, no: sw("p_a", no, sw("p_b", no, sw("p_c", no, yes)))

    # ------------------------------------------------------------------ attack: the small bomb / Short Fuse's big one
    plain = combine(sfx("a"), homing("a_bomb", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"]),
                    homing("a_twin", "EnemyChampion", marked, p["a_speed"]))
    big = [attack(0, 100), ap(p["p_dmg"], p["p_ratio"]), view("p_hit"), tsfx("p_hit")]
    if native:      # the add-on scales the passive's bomb on towers (its on_attack sees `p_now` on him)
        big = [refresh("p_now", 2)] + big
    fused = combine(sfx("p"), fuse_lit, homing("p_bomb", "Enemy", big, p["a_speed"]),
                    homing("p_twin", "EnemyChampion", marked, p["a_speed"]))

    # ------------------------------------------------------------------ W: Satchel Charge (cast by the watch)
    blast_w = [ap(p["w_dmg"], p["w_ratio"]), {"type": "Knockback", "speed": p["w_kb"], "tick": p["w_kb_t"]},
               view("w_hit"), tsfx("w_hit")]
    hop = pick(p["w_trig"] + 20000, "EnemyChampion", {"type": "MoveBack", "speed": p["w_hop"], "tick": p["w_hop_t"]})
    satchel = combine(flag("w_cd", p["w_cd"]), refresh("busy", p["w_dur"]), anim("skill_w", p["w_dur"]), sfx("w"),
                      voice("vo_w", p), cut,
                      delayed(p["w_rel"] - 1, alive(
                          cview("w_blast"), sfx("w_blast"), around(p["w_r"], "EnemyWithoutTower", blast_w),
                          *([refresh("w_now", 2)] if native else []), hop)))
    cast_w = {"type": "SwitchByLevel3", "effect_start": NONE,
              "effect_level3": sw("w_cd", NONE, sw("busy", NONE, pick(p["w_trig"], "EnemyChampion", satchel)))}

    # ------------------------------------------------------------------ ult: R Mega Inferno Bomb
    boom = [view("r_boom"), sfx("r_boom"),
            zone("r_blast", p["r_r"], [ap(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]),
            zone("r_core", p["r_cr"], [ap(p["r_cdmg"], p["r_cratio"])])]
    throw = combine(*rm("r_arm", "r_late"), refresh("r_fired", 4), refresh("busy", p["r_dur"]), anim("ult", p["r_dur"]),
                    cview("r_cast"), sfx("r"), voice("vo_r", p), cut,
                    delayed(p["r_rel"] - 1, alive(lob("r_bomb", p["r_travel"], boom, target="EnemyChampion",
                                                      seen="r_warn"))))

    # ------------------------------------------------------------------ the watch (R's moment, W)
    fire = sw("r_arm", combine(pick(p["r_range"], "EnemyChampionInCC", throw),
                               delayed(1, sw("r_fired", NONE, sw("r_late", pick(p["r_range"],
                                                                                "EnemyChampionRecentlyAttacked",
                                                                                throw))))))
    watch = on_me(casted(1000000, p["watch_p"], fire, delayed(2, cast_w)))
    life = sw("init", NONE, combine(flag("init", None), watch))

    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, delayed(p["a_rel"] - 1, ready(fused, plain))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Bouncing Bomb
    def landing(k, last):
        hit = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"), refresh("q_boom", 2)]
        then = sw("q_boom", combine(*rm("q_boom"), refresh("q_done", 90), view("q_blast"), sfx("q_blast")),
                  combine(view("q_blast"), sfx("q_blast")) if last else combine(view("q_bounce"), sfx("q_bounce")))
        return mover(f"q_l{k}", p[f"q_l{k}"], sum(p[f"q_t{i}"] for i in range(1, k + 1)),
                     [sw("q_done", NONE, combine(zone(f"q_z{k}", p["q_r"], hit), delayed(2, then)))])

    stamps = [mover(f"q_s{i}", d, t, [sw("q_done", NONE, view(f"q_air{min(h, 18) // 2 * 2}"))])
              for i, (k, d, t, h) in enumerate(air_heights(p))]
    bomb = combine(*rm("q_done", "q_boom"), *stamps, landing(1, False), landing(2, False), landing(3, True))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(refresh("busy", p["q_dur"]), sfx("q"), voice("vo_q", p), cut,
                           delayed(p["q_rel"] - 1, alive(bomb))))

    # ------------------------------------------------------------------ skill2: E Hexplosive Minefield
    slow = buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"])
    low = p["e_low"]
    mines = [delayed(p["e_arm"],
                     once("e_first", p["e_r"], p["e_t"] - p["e_arm"],
                          [ap(p["e_dmg"], p["e_ratio"]), slow, view("e_hit"), tsfx("e_hit")]),
                     field("e_more", p["e_r"], p["e_t"] - p["e_arm"], p["e_p"],
                           [ap(p["e_dmg"] * low // 100, p["e_ratio"] * low // 100), slow, view("e_hit"),
                            tsfx("e_hit")]))]
    lying = [delayed(k, view("e_field")) for k in range(0, p["e_t"], p["e_show"])]
    minefield = lob("e_throw", p["e_travel"], [sfx("e_land"), view("e_land")] + mines)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Position", "EnemyWithoutTower",
                    combine(refresh("busy", p["e_dur"]), sfx("e"), voice("vo_e", p), cut,
                            delayed(p["e_rel"] - 1, alive(minefield)),
                            delayed(p["e_rel"] - 1 + p["e_travel"], *lying)))

    # ------------------------------------------------------------------ ult slot: arms the window
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm", "r_late"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_wait"], sw("r_arm", refresh("r_late", 600))),
                                                        delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), ap(100, 100)), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(life, scored),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    # a projectile's picture is turned with its flight: the bombs are round (symmetric every way)
    views_p = [Pj("a_bomb"), Pj("p_bomb"), Pj("e_throw"), Pj("r_bomb", anim_=BIG)]
    heights = sorted({min(h, 18) // 2 * 2 for _, _, _, h in air_heights(p)})
    views_e = ([E("a_hit"), E("p_hit"), E("q_hit"), E("q_bounce", FX, 1, False), E("q_blast", BIG, 2, False)]
               + [E(f"q_air{h}", FX, 3, False) for h in heights]
               + [E("e_land", BIG, -1, False), E("e_field", BIG, -1, False), E("e_hit"),
                  E("w_blast", BIG, 2, False), E("w_hit"), E("r_cast", BIG, 3), E("r_warn", BIG, -2, False),
                  E("r_boom", BIG, 2, False), E("r_hit")])
    views_b = [B_("e_slow", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_ziggs:hexplode", "params": {
            "w_ex": p["w_ex"], "w_hex_r": p["w_hex_r"], "w_cd": p["w_cd"], "p_tower": p["p_tower"]}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--native", action="store_true", help="the add-on's copy")
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
