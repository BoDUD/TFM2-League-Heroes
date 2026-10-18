"""Build league_gangplank.data_champion (top, Melee) from the parameters P.

    python tools/kit/build_gangplank.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-18: top, layout A with the add-on league_gangplank - 「技能方案按 A 做」; PPU 1.5). TFM2
has three active slots: Parrrley is `skill`, Powder Keg `skill2`, Cannon Barrage the `ult`; Remove Scurvy (W) has no
slot - the watch eats the orange (league_jarvaniv's / league_ziggs's W the same way).
  passive Trial by Fire (烈火审讯): with `p_cd` off his next attack or Parrrley sets the unit hit on fire - p_dmg +
          p_ratio% AD true damage over p_burn ticks (`AddCasted` Fire, champion and minion alike, never towers) - and
          he runs p_ms% faster for p_ms_t; then `p_cd` p_t ticks. Every keg that blows takes `p_cd` off (League: 15 s,
          a keg explosion resets it).
  attack  a cutlass slash (100% AD) struck by a hidden homing hit on `Enemy` (towers too) on a_hit; its champion-only
          twin marks the fight. The hit also lights `a_fire` (2 ticks) for the kegs.
  skill   Q Parrrley (枪火谈判), `Targeting` on `EnemyWithoutTower` (q_range), `attack_type: BaseAttack` (it crits, as
          League's does): a bullet on q_rel, q_dmg + q_ratio% AD and the passive. The hit lights `q_fire` for e_arm
          ticks: every ripe keg with an enemy in it blows (League: Q shoots the keg; nothing can aim at a zone, so the
          bullet goes to the enemy and the keg near it goes off - a shot up to e_arm ticks before a keg ripens still
          sets it off the moment it ripens, League's decaying keg health).
  skill2  E Powder Keg (火药桶), `Targeting` on `EnemyChampion` (e_range): the cast only raises `e_go`; the keg
          itself is thrown by the fast watch (2 ticks) at an enemy champion within e_range + 20000, landing e_travel
          ticks later where it stood (champions only: a second throw for minions would copy the whole keg again). Every keg - its pictures, zones and e_t / e_link
          links - lives in the ATTACK tree that way, not in skill2: the game copies skill / skill2 every tick
          (docs/perf.md), the attack it does not. Two slots (k1 / k2, the first free one), each keg e_t ticks, ripe
          e_arm ticks after it lands. A ripe keg blows when, with an enemy within e_r of it, `q_fire` is on, or
          `a_fire` with him within e_near of the keg (a melee hit beside it), or the other keg just blew (chain, data
          version: only a keg with an enemy in it). The blast (the next link, <= e_link ticks): e_dmg + e_ratio% AD
          to every enemy within e_r, e_champ more on champions, e_pen% armour ignored (a 1-tick caster
          `defence_penetration`), e_slow% slower for e_slow_t; `p_cd` off.
  W       Remove Scurvy (坏血病疗法), eaten by the watch from level 3 with `w_cd` off: when he is crowd-controlled
          (`AllyChampionInCC` within 1) or crowded (two enemy champions within w_crowd, league_blitzcrank's Mana
          Barrier): heal w_heal + w_ratio% AD and `cc_immune` for w_imm ticks (League: 45-145 + 13% missing health
          and a cleanse; nothing reads health, and data cannot end a stun already on him - the add-on can).
  ult     R Cannon Barrage (加农炮幕): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only arms the ult
          for r_arm ticks (league_ziggs R); the watch calls it on an enemy champion in crowd control anywhere, or -
          after r_wait ticks of the window - on one his team hit recently (League's map-wide help). A flare marks the
          spot for r_call ticks (where the champion stood when the call left), then r_waves waves r_p ticks apart:
          r_dmg + r_ratio% AD to every enemy within r_r, r_slow% slower for r_slow_t (League: 12 waves in 4 clusters,
          40-100 + 10% AP each, r 580, slow 30% 0.5 s). Unused, the window ends with the cooldown capped (`r_retry`).
  watch   A life-long `AddCasted` started by his first attack or R press of each life (`init`): every watch_p ticks
          the ult's moment and W; every 2 ticks (a second `AddCasted`) the keg throw.
The add-on copy (--native, addons/league_gangplank): the passive league_gangplank:scurvy ends the crowd control on
him the tick W is eaten (`w_now`, sim.entity_clear_cc - League's cleanse) and raises `w_low` below w_low% health so
the watch eats it then too; league_gangplank:kegs chains kegs - when one blows, the other ripe keg within e_chain
blows a tick later even with no enemy in it. The add-on presses no key.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_gangplank.data_champion")
ID = "league_gangplank"
FX = "asset/league/effects/league_gangplank_fx"
BIG = "asset/league/effects/league_gangplank_big"

# League units x 100 = ours (Q range 625 -> 62500); radii count the unit's collision radius (~15000) on top. Timings
# match the strips (tools/art/rig_gangplank.py MS: attack 433 ms = 26 ticks, Q 24, E 22, W 20, R 24).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Gangplank:
    # 64 AD +4.2, 630 +114 hp, 31 armour, 345 move, 125 range, attack speed 0.658 +3.2%
    "hp": 1000, "hp_g": 108, "atk": 82, "atk_g": 16, "def": 30, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000,
    "ms_g": 11,
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 60, "a_hit": 9, "f_t": 180,
    # passive Trial by Fire (League: 50-250 +100% bonus AD true over 2.5 s, +15-30% move speed 2 s, every 15 s)
    "p_t": 720, "p_dmg": 60, "p_ratio": 60, "p_burn": 150, "p_per": 15, "p_ms": 20, "p_ms_t": 120,
    # Q Parrrley (League: 625 range, 10-130 +100% AD, crits, cd 4.5)
    "q_cd": 270, "q_range": 62500, "q_dur": 24, "q_rel": 10, "q_speed": 6000, "q_dmg": 30, "q_ratio": 100,
    # E Powder Keg (League: 1000 range, r 345, 25 s, 3-5 charges every 17-13 s, ripe after 4-1 s, slow 40-80% 2 s,
    # +75-155 to champions, 40% armour ignored)
    "e_cd": 480, "e_range": 70000, "e_dur": 22, "e_rel": 9, "e_travel": 16, "e_t": 480, "e_arm": 60, "e_link": 10,
    "e_r": 30000, "e_near": 30000, "e_dmg": 40, "e_ratio": 100, "e_champ": 60, "e_pen": 40, "e_slow": 40,
    "e_slow_t": 120, "e_chain": 70000,
    # W Remove Scurvy (League: 45-145 +13% missing health, cleanse, cd 22-14)
    "w_cd": 900, "w_dur": 20, "w_rel": 10, "w_heal": 80, "w_ratio": 60, "w_imm": 60, "w_crowd": 35000, "w_low": 40,
    # R Cannon Barrage (League: global, r 580 (inner 170), 12 waves 40-100 + 10% AP, slow 30% 0.5 s, cd 160-120)
    "r_cd": 3600, "r_range": 400000, "r_arm": 600, "r_wait": 300, "r_dur": 24, "r_rel": 10, "r_call": 60,
    "r_waves": 12, "r_p": 30, "r_r": 44000, "r_dmg": 30, "r_ratio": 25, "r_slow": 30, "r_slow_t": 30,
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


def true_dmg(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, here=False):
    """`here`: measured from the projectile (a zone's centre) instead of from him."""
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": here,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action: its estimate follows a SwitchByBuff by the flags he has while
    it reads, so a hit under alive() reads as nothing - and its battle plan divides an enemy's health by his attack's
    estimate (sim 10-18: "attempt to divide by zero", battle.rs:1938 / utils.rs:1539, games hung). A flag he never
    has while it reads; on the cast the flag is up and the hit is skipped (the ult's `scored` the same way)."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed=40000):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


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


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def keg(p, s, native, ms):
    """Slot s's keg: everything at the landing point of the throw (its end_effects keep the point). The trigger zone
    is the blast: with the keg ripe and a reason to blow, every enemy inside is hit on that one application and the
    keg goes out a tick later; the links only draw it (the keg, the lit keg, the explosion - at most e_link late)."""
    o = 3 - s
    live, ripe, blew, chain, busy = f"k{s}_live", f"k{s}_ripe", f"k{s}_blew", f"k{s}_chain", f"k{s}_busy"
    life = p["e_t"]
    slow = buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"])
    pen = flag("e_pen", 1, defence_penetration=p["e_pen"])
    out = delayed(1, *rm(live, ripe, "p_cd"), ms, *([refresh(f"k{s}_now", 2)] if native else []))
    hit = combine(pen, attack(p["e_dmg"], p["e_ratio"]), slow, view("e_hit"), tsfx("e_hit"),
                  refresh(blew, p["e_link"] + 1), refresh(chain, 3), out)
    bonus = combine(pen, attack(p["e_champ"], 0))

    def why(blow):   # a shot, a hit beside it or the other keg's blast
        return sw(ripe, sw("q_fire", blow, sw(f"k{o}_chain", blow, sw("a_fire", pick(
            p["e_near"], "AllyOnlySelf", flag(f"k{s}_near", 1), here=True)))))

    near_blow = lambda blow: sw(f"k{s}_near", combine(*rm(f"k{s}_near"), blow))
    trigger = field(f"k{s}_trig", p["e_r"], life, 1, [why(hit), near_blow(hit)], first=1)
    champ = field(f"k{s}_champ", p["e_r"], life, 1, [sw(ripe, sw("q_fire", bonus, sw(f"k{o}_chain", bonus, sw(
        "a_fire", pick(p["e_near"], "AllyOnlySelf", bonus, here=True)))))], target="EnemyChampion", first=1)
    links = [delayed(t, sw(blew, combine(*rm(blew), view("e_boom"), sfx("e_boom")),
                           sw(ripe, view("e_keg_lit"), sw(live, view("e_keg")))))
             for t in range(0, life, p["e_link"])]
    end = [sfx("e_land"), view("e_land"), refresh(live, life), delayed(p["e_arm"], sw(live, refresh(ripe, life))),
           champ, trigger] + links
    throw = lob(f"e_throw{s}", p["e_travel"], end)
    take = combine(*rm("e_go"), refresh(busy, p["e_travel"] + life + p["e_link"]))
    return pick(p["e_range"] + 20000, "EnemyChampion", take, throw)


def build(p):
    native = bool(p["native"])
    marked = [refresh("fight", p["f_t"])]

    # ------------------------------------------------------------------ passive: Trial by Fire
    burn = casted(p["p_burn"] + 1, p["p_per"], true_dmg(p["p_dmg"] * p["p_per"] // p["p_burn"],
                                                        p["p_ratio"] * p["p_per"] // p["p_burn"]), kind="Fire")
    fire_on = [burn, view("p_hit"), tsfx("p_hit")]
    ms = refresh("p_ms", p["p_ms_t"], move_speed_mult=p["p_ms"])
    lit = combine(flag("p_cd", p["p_t"]), ms)

    # ------------------------------------------------------------------ W: Remove Scurvy (eaten by the watch)
    eat = combine(flag("w_cd", p["w_cd"]), anim("skill_w", p["w_dur"]), sfx("w"), voice("vo_w", p),
                  flag("w_imm", p["w_imm"], cc_immune=True), *([refresh("w_now", 2)] if native else []),
                  delayed(p["w_rel"] - 1, alive(cview("w_cast"), on_me(heal(p["w_heal"], p["w_ratio"]))),
                          sfx("w_eat")))
    count = combine(*rm("c_e1", "c_e2"),
                    around(p["w_crowd"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]))
    # w_go lives 3 ticks: set on tick 0 (crowd control) or 1 (crowded, low health), read on tick 2
    want = combine(*rm("w_go"), pick(1, "AllyChampionInCC", flag("w_go", 3)), count, delayed(
        1, sw("c_e2", flag("w_go", 3)), *([sw("w_low", flag("w_go", 3))] if native else []),
        delayed(1, sw("w_go", combine(*rm("w_go"), eat)))))
    cast_w = {"type": "SwitchByLevel3", "effect_start": NONE, "effect_level3": sw("w_cd", NONE, want)}

    # ------------------------------------------------------------------ ult: R Cannon Barrage
    wave = combine(view("r_wave"), sfx("r_wave"), zone("r_z", p["r_r"], [
        attack(p["r_dmg"], p["r_ratio"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
        view("r_hit")]))
    barrage = [sfx("r_call")] + [delayed(k * p["r_p"], wave) for k in range(p["r_waves"])]
    call = combine(*rm("r_arm", "r_late"), refresh("r_fired", 4), refresh("busy", p["r_dur"]),
                   anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                   delayed(p["r_rel"] - 1, alive(cview("r_cast"), lob("r_flare", p["r_call"], barrage,
                                                                      target="EnemyChampion", seen="r_warn"))))
    fire_r = sw("r_arm", combine(pick(p["r_range"], "EnemyChampionInCC", call),
                                 delayed(1, sw("r_fired", NONE, sw("r_late", pick(p["r_range"],
                                                                                  "EnemyChampionRecentlyAttacked",
                                                                                  call))))))

    # ------------------------------------------------------------------ E: the kegs (thrown by the fast watch)
    kegs = sw("e_go", sw("k1_busy", sw("k2_busy", combine(*rm("e_go")), keg(p, 2, native, ms)), keg(p, 1, native, ms)))

    watch = on_me(casted(1000000, p["watch_p"], fire_r, delayed(2, cast_w)), casted(1000000, 2, kegs))
    life = sw("init", NONE, combine(flag("init", None), watch))

    # ------------------------------------------------------------------ attack: the cutlass
    plain_c = marked
    blow = combine(sfx("a_swing"),
                   homing("a_blow", "Enemy", [attack(0, 100), refresh("a_fire", 2), view("a_hit"), tsfx("a_hit")]),
                   sw("p_cd", NONE, combine(lit, homing("a_burn", "EnemyWithoutTower", fire_on))),
                   homing("a_twin", "EnemyChampion", plain_c))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, decoy(0, 100), delayed(p["a_hit"] - 1, alive(blow))), atype="BaseAttack",
                      cancel=True)

    # ------------------------------------------------------------------ skill: Q Parrrley
    shot = [attack(p["q_dmg"], p["q_ratio"]), refresh("q_fire", p["e_arm"]), view("q_hit"), tsfx("q_hit")]
    bang = combine(cview("q_flash"), sfx("q_shot"),
                   sw("p_cd", homing("q_bullet", "EnemyWithoutTower", shot, p["q_speed"]),
                      combine(lit, homing("q_bullet_p", "EnemyWithoutTower", shot + fire_on, p["q_speed"]))),
                   homing("q_twin", "EnemyChampion", marked, p["q_speed"]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(refresh("busy", p["q_dur"]), decoy(p["q_dmg"], p["q_ratio"]), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(bang))),
                   atype="BaseAttack")

    # ------------------------------------------------------------------ skill2: E Powder Keg (the cast)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(refresh("busy", p["e_dur"]), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, refresh("e_go", 6))))

    # ------------------------------------------------------------------ ult slot: arms the window
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm", "r_late"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_wait"], sw("r_arm", refresh("r_late", 600))),
                                                        delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), attack(100, 100)), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", scored,
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    # a projectile's picture is turned with its flight: the bullet is symmetric top to bottom, the keg round
    views_p = [Pj("q_bullet", "q_bullet"), Pj("q_bullet_p", "q_bullet"), Pj("e_throw1", "e_throw"),
               Pj("e_throw2", "e_throw")]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("q_flash", FX, 3), E("e_land", BIG, -1, False),
               E("e_keg", BIG, 1, False), E("e_keg_lit", BIG, 1, False), E("e_boom", BIG, 2, False), E("e_hit"),
               E("w_cast", FX, 3), E("r_cast", BIG, 3), E("r_warn", BIG, -2, False), E("r_wave", BIG, 2, False),
               E("r_hit")]
    views_b = [B_("e_slow", FX, 3), B_("r_slow", FX, 3), B_("p_ms", FX, -1), B_("w_imm", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_gangplank:scurvy", "params": {
            "w_low": p["w_low"], "e_chain": p["e_chain"]}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
