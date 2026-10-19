"""Build league_nasus.data_champion (top, Melee) from the parameters P.

    python tools/kit/build_nasus.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-17: top, layout A, the add-on league_nasus, PPU 1.2, R as a bigger body - 「全按推荐」).
TFM2 has three active slots: Siphoning Strike is `skill`, Spirit Fire `skill2`, Fury of the Sands the `ult`; Wither (W)
has no slot - the watch casts it on its own (league_swain's W the same way).
  passive Soul Eater (吞噬灵魂): p_vamp% life steal, a Permanent caster buff laid at each life's first attack or R press.
  attack  a staff blow (100% AD), struck by a hidden homing hit on a_hit; its champion-only twin marks the fight
          (`fight`, f_t ticks; a hit inside it marks the duel, `duel`, d_t ticks).
  skill   Q Siphoning Strike (汲魂痛击), `Targeting` on `EnemyWithoutTower` (q_range, League's +50 range): on q_hit
          q_dmg + q_ratio% AD physical, plus the stacks as magic damage (ApAttack 100% AP: no effect scales with a
          count, so each stack is ability power - a Permanent caster buff `q_stack` with `magic_power`; he has no other
          ability power and nothing else of his reads it). League's kill trigger (league_jinx) on the hit: a unit it
          kills adds q_s, a champion q_sc (its champion-only twin). Buffs die with him, so the main pack's stacks last
          a life (the tooltip says so); the add-on keeps them (league_veigar_power's way).
  skill2  E Spirit Fire (灵魂烈焰), `Targeting` on `EnemyWithoutTower` (e_range): a hidden lob lands where the target
          stood (walking out dodges it): e_dmg + e_hp% of his max health magic damage in e_r at once, then every e_p
          ticks for e_t ticks e_dot + e_dot_hp% max health and e_shred% armour (defence_mult) while standing in it.
  W       Wither (枯萎), automatic: in a fight (`fight`), with w_cd off, the watch picks an enemy champion recently
          in a fight within w_range: a 5-s slow growing w_s0 -> w_s0 + 4 x w_ds % and attack speed w_a0 -> w_a0 +
          4 x w_da % (five buffs laid a second apart, each lasting to the end).
  ult     R Fury of the Sands (死神降临): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only arms the
          ult for r_arm ticks (league_swain's R); the watch raises it once the moment is right (the user's rule
          「看好时机」): two enemy champions within r_cnt, or a fight (`fight`; `duel` with r_duel) with an enemy
          champion within r_cnt. Unused,
          the window ends with the cooldown capped at 60 ticks (`r_retry`). r_t ticks of `r_on`: +r_hp health (and as
          much healed), +r_def armour and magic resistance, +r_rng attack range, skill_cooldown_mult 100 (Q's
          cooldown halved; data can't pick one slot, so E's too - the add-on halves only Q; not R's own: the same buff's
          ult_cooldown_mult -100 offsets it, 2026-10-19), and every r_p ticks
          r_pct% of each enemy's max health within r_r (FixedAttack: ApAttack has no target share). While `r_on` lasts
          his attack, Q and E play the big body's strips (b_attack, b_skill, b_skill2); idle / run / hit can't change
          in data - the add-on swaps the whole body; the sandstorm (`r_on`'s view) follows him.
  watch   A life-long `AddCasted` started by his first attack or R press of each life (`init`), every watch_p ticks:
          counts enemy champions within r_r (c_e1, c_e2); raises R when the window is open and r_ok holds; casts W.
The add-on copy (--native): the passive `league_nasus:soul_eater` keeps the stacks after death and halves only Q's
cooldown while `r_on` lasts (the copy's `r_on` has no skill_cooldown_mult: E keeps its own); the add-on's display hook
swaps the whole body to the big one; the data keeps every hit, picture and sound.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_nasus.data_champion")
ID = "league_nasus"
FX = "asset/league/effects/league_nasus_fx"
BIG = "asset/league/effects/league_nasus_big"

# Timings from the strips (tools/art/rig_nasus.py): the attack's blow lands on tick 9 (frame 3 from tick 8.4), Q's slam on
# tick 10 (frame 4 from 9.6), E's staff points on tick 9, W's hand on tick 7, R's big body from tick 12 (frame 4).
# Numbers = the 10-min classic-SDK simulations (top lane 0 against fighter, executioner, lancer, pole_warrior, knight and
# berserker, three lineups, both sides, 8 seeds, 2026-10-17): the draft c0 (Q 30 + 100% AD + 3 / 10 stacks, attack 82,
# hp 1050, R 1% a pulse, R only in a duel) +0.33 (league_darius +1.99 in the same batch); Q 50 + 4 stacks (c1) -0.35;
# + attack 90, hp 1100 (c2) +0.50; + R 2% and Q every 4 s (c3) +0.98 - but R rose 0-4 times a game (the duel rule too
# strict); R in any fight (fight flag, r_cnt 40000) with a 10-s window (c4) +1.55, 5 rises a game; c4 + attack 95 and
# E 70 + 4% (c5) +2.67 (too strong). P = c4.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Nasus:
    # 67 AD +4, 650 +104 hp, 34 armour, 350 move, attack speed 0.638 (slow)
    "hp": 1100, "hp_g": 110, "atk": 90, "atk_g": 16, "def": 32, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 980, "ms_g": 10,
    # attack: the blow lands on a_hit
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 72, "a_hit": 9, "f_t": 180, "d_t": 120,
    # passive: Soul Eater (League: 10-20% life steal)
    "p_vamp": 12,
    # skill: Q Siphoning Strike (League: +30-110 + stacks, +50 range, +4 a kill, +10 a champion / large unit, cd 7.5-3.5)
    "q_cd": 240, "q_range": 31000, "q_dur": 24, "q_hit": 10, "q_dmg": 50, "q_ratio": 100, "q_s": 4, "q_sc": 10,
    # skill2: E Spirit Fire (League: 650 range, r 400, 50-170 + 60% AP, then 10-34 + 12% AP a second for 5 s, armour
    # -30-50% inside, cd 12)
    "e_cd": 600, "e_range": 50000, "e_dur": 24, "e_rel": 10, "e_travel": 8, "e_r": 28000, "e_dmg": 50, "e_hp": 3,
    "e_p": 60, "e_t": 300, "e_dot": 10, "e_dot_hp": 1, "e_shred": 30,
    # W Wither (League: 700 range, 5 s, slow 35% growing to 47-95%, attack speed -75% of it, cd 15-11)
    "w_cd": 720, "w_range": 50000, "w_dur": 18, "w_rel": 7, "w_t": 300, "w_s0": 35, "w_ds": 10, "w_a0": 25, "w_da": 6,
    # ult: R Fury of the Sands (League: 15 s, +300-600 hp, +40-70 armour / MR, +50 range, aura r 400 1.5-2.5% max hp
    # every 0.5 s, Q cd halved, cd 120/100/80)
    "r_cd": 3600, "r_range": 50000, "r_arm": 600, "r_dur": 30, "r_on_at": 12, "r_r": 30000, "r_t": 900, "r_hp": 300,
    "r_def": 40, "r_rng": 4000, "r_p": 30, "r_pct": 2, "r_cnt": 40000, "r_duel": 0,
    # the watch
    "watch_p": 12,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_nasus (its native passive)
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


def ap(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def true_pct(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def heal(amount):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed=40000):
    """A hidden blow: at this speed it reaches a melee target on the next tick."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # a champion struck: the fight (W's and R's moment), a hit inside it the duel
    marked = [sw("fight", refresh("duel", p["d_t"])), refresh("fight", p["f_t"])]

    # ------------------------------------------------------------------ W: Wither (cast by the watch)
    w_hit = [view("w_hit"), tsfx("w_hit"), buff("w_slow", p["w_t"], move_speed_mult=-p["w_s0"],
                                                  attack_speed_mult=-p["w_a0"])]
    for k in range(1, 5):
        w_hit.append(delayed(60 * k, buff(f"w_slow{k}", p["w_t"] - 60 * k, move_speed_mult=-p["w_ds"],
                                          attack_speed_mult=-p["w_da"])))
    wither = combine(flag("w_cd", p["w_cd"]), sw("r_on", anim("b_skill_w", p["w_dur"]), anim("skill_w", p["w_dur"])),
                     sfx("w"), voice("vo_w", p),
                     delayed(p["w_rel"] - 1, homing("w_bolt", "EnemyChampion", w_hit, speed=6000)))

    # ------------------------------------------------------------------ ult: R Fury of the Sands
    storm = around(p["r_r"], "EnemyWithoutTower", [true_pct(p["r_pct"]), view("r_hit")])
    rise = combine(anim("ult", p["r_dur"]), cview("r_cast"), sfx("r"), voice("vo_r", p),
                   delayed(p["r_on_at"] - 1, sfx("r_storm"),
                           refresh("r_on", p["r_t"], hp=p["r_hp"], defence=p["r_def"], magic_resistance=p["r_def"],
                                   range=p["r_rng"], **({} if native else {"skill_cooldown_mult": 100, "ult_cooldown_mult": -100})),
                           heal(p["r_hp"]), on_me(casted(p["r_t"], p["r_p"], storm))))

    # ------------------------------------------------------------------ the watch (R's moment, W)
    tick = p["watch_p"]
    p_fight = "duel" if p["r_duel"] else "fight"
    count = combine(*rm("c_e1", "c_e2"),
                    around(p["r_cnt"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]))
    ok = combine(refresh("r_ok", tick + 2), sw("r_arm", flag("r_go", 1)))
    arm = sw("c_e2", ok, sw(p_fight, sw("c_e1", ok)))
    fire = sw("r_go", combine(*rm("r_go", "r_arm"), rise))
    cast_w = sw("w_cd", NONE, sw("fight", pick(p["w_range"], "EnemyChampionRecentlyAttacked", wither)))
    watch = on_me(casted(1000000, tick, count, delayed(1, arm, fire, cast_w)))
    life = sw("init", NONE, combine(flag("init", None), flag("p_vamp", None, vamp=p["p_vamp"]), watch))

    # ------------------------------------------------------------------ attack: the staff blow
    blow = combine(sfx("a_swing"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   homing("a_twin", "EnemyChampion", marked))
    a_eff = combine(life, sw("r_on", anim("b_attack", p["atk_dur"])), delayed(p["a_hit"] - 1, blow))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", a_eff,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Siphoning Strike
    # the kill trigger (league_jinx): a flag on him, cleared next tick by a casted on a living target; still there
    # q_chk ticks later = the strike killed. The champion-only twin's own flag picks the bigger reward.
    def soul(k):
        return combine(flag("q_stack", None, magic_power=k), cview("q_soul"), sfx("q_soul"))

    check = delayed(5, sw("q_kc", combine(*rm("q_kc", "q_k"), soul(p["q_sc"])),
                          sw("q_k", combine(*rm("q_k"), soul(p["q_s"])))))
    q_hit = [attack(p["q_dmg"], p["q_ratio"]), ap(0, 100), view("q_hit"), tsfx("q_hit"),
             refresh("q_k", 8), casted(3, 1, *rm("q_k")), on_me(check)]
    q_twin = marked + [refresh("q_kc", 8), casted(3, 1, *rm("q_kc"))]
    strike = combine(sw("r_on", anim("b_skill", p["q_dur"])), sfx("q"), voice("vo_q", p),
                     delayed(p["q_hit"] - 1, homing("q_blow", "EnemyWithoutTower", q_hit),
                             homing("q_twin", "EnemyChampion", q_twin)))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", strike)

    # ------------------------------------------------------------------ skill2: E Spirit Fire
    burst = [ap(p["e_dmg"], 0, p["e_hp"]), view("e_hit"), tsfx("e_hit")]
    burn = [ap(p["e_dot"], 0, p["e_dot_hp"]), buff("e_shred", p["e_p"], defence_mult=-p["e_shred"])]
    fire_ = [view("e_fire"), sfx("e_fire"), zone("e_burst", p["e_r"], burst),
             field("e_burn", p["e_r"], p["e_t"], p["e_p"], burn)]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sw("r_on", anim("b_skill2", p["e_dur"])), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, lob("e_lob", p["e_travel"], fire_))))

    # ------------------------------------------------------------------ ult: the slot arms the window
    # unused, it ends with the cooldown capped at 60 ticks (cooltime x 100 / (100 + mult), league_tahmkench's r_retry)
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_arm"], reset)))
    # league_orianna's x trick: the AI scores the branch the flags pick between ticks - r_x is never there then, so it
    # reads a hit; when the slot runs, the flag is up and the window opens
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), attack(100, 100)), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(life, scored),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = []        # every blow flies unseen (the swing is in his frames)
    views_e = [E("a_hit"), E("q_hit"), E("q_soul", FX, 3), E("e_fire", BIG, -1, False), E("e_hit"), E("w_hit"),
               E("r_cast", BIG, 2, False), E("r_hit")]
    views_b = [B_("w_slow", FX, 3), B_("e_shred", FX, 3), B_("r_on", BIG, -1)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_nasus:soul_eater", "params": {"q_s": p["q_s"], "q_sc": p["q_sc"],
                                                                                   "r_r": p["r_r"]}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank"], **extra,
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
    ap_.add_argument("--set", nargs="*", default=[])
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
