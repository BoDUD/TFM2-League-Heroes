"""Build league_aphelios.data_champion (bottom ADC, the five moonstone weapons of Alune) from the parameters P.

    python tools/kit/build_aphelios.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-16: bottom-lane ADC, an add-on later, PPU 1.5; 「方案可以，全按推荐做」):
  weapons Five weapons, one in the main hand and one in the off hand, the other three waiting on a fixed cycle
          Calibrum -> Severum -> Gravitum -> Infernum -> Crescendum -> Calibrum. Main = one permanent caster buff
          mw_<w> (it carries the weapon's own stat: Calibrum's range, Severum's lifesteal and attack speed), off hand
          = ow_<w>. His first attack after every spawn (death clears data buffs) sets Calibrum / Severum and a full
          magazine (init). Ammo: a 5-bit counter b0..b4 (ammo shots, League 50); every attack takes 1 and a Q
          (q_spent, read at his next attack) q_cost more; empty -> the main hand takes the next weapon of the cycle
          that is not in the off hand (League's queue is first-in first-out: the same order until W swaps, the
          add-on keeps the real queue) and the magazine refills. All of it runs in the attack (the engine does not
          copy the attack's tree every tick).
  passive The Hitman and the Seer (杀手与先知): his growth (Alune's gifts: attack and attack speed) in the stats.
  attack  The main weapon's shot (each its own strip via `CasterAnimation` on tick 1, league_jinx's way):
          Calibrum (a_cal): range +c_range. Severum (a_sev): vamp sev_vamp%, attack speed +sev_as%.
          Gravitum (a_grav): the hit slows grav_slow% for grav_slow_t and marks the unit (an AddCasted grav_mark_t long,
          added at most every grav_mk_cd ticks) for Binding Eclipse; any mark sets g_any. Infernum (a_inf): the target
          takes inf_main% AD, every enemy within inf_r of it inf_splash% (the splash's cone in League). Crescendum
          (a_cre): every hit adds a chakram (cre, attack +cre_ad% for cre_t ticks, each its own timer: they add up).
  skill   Q, the main weapon's own ability, each on its own cooldown (caster flags qcd_<w>; the slot waits s_cd):
          Calibrum Moonshot (通碧·狙杀): aimed q_c_lock ticks before the shot (a hidden lob, league_caitlyn's lock),
            a line to that spot hitting the first enemy: q_c_dmg + q_c_ad% AD, then the mark is shot off from afar
            q_c_pop ticks later (q_p_dmg + q_p_ad% AD).
          Severum Onslaught (断魄·恒月强袭): move speed +q_s_ms% for q_s_t; q_s_n shots at random enemies within q_s_r,
            q_s_dmg + q_s_ad% AD each and a heal of q_s_heal + q_s_hr% AD; every second shot is the off-hand weapon's.
          Gravitum Binding Eclipse (坠明·引力枷锁): only with a Gravitum mark alive (g_any): every marked unit is rooted
            q_g_root ticks and takes q_g_dmg + q_g_ad% AD per mark on it.
          Infernum Duskwave (荧焰·余晖波): a cone before him (q_i_r, DirDot q_i_cone): q_i_dmg + q_i_ad% AD, then each
            unit hit gets a shot of the off-hand weapon (q_off_ad% AD + its on-hit).
          Crescendum Sentry (折镜·驻灵哨卫): a turret on the target's spot for q_r_t ticks; every q_r_per ticks it shoots
            every enemy within q_r_r with the off-hand weapon: q_r_dmg + q_r_ad% AD + its on-hit.
  skill2  W Phase (月相轮转): main and off hand swap - only when the main hand's Q is cooling down and the off hand's is
          ready, an enemy champion within w_range (the AI then casts the new main hand's Q: League's W -> Q).
  ult     R Moonlight Vigil (清辉夜凝): the slot arms the ult for r_arm ticks; a poll every r_poll ticks fires at a
          champion his team fights (EnemyChampionRecentlyAttacked) within r_range with another enemy champion within
          r_rad of it, or at one in crowd control. The aim is locked on the champion's spot (a hidden lob), the shot
          flies to it and bursts on the first champion it meets: r_dmg + r_ad% AD within r_rad, then the main weapon's
          gift on every unit hit: Calibrum another shot each (r_c_ad% AD), Severum a heal (r_s_heal + r_s_hr% AD),
          Gravitum r_g_slow% slow for r_g_t and a Gravitum mark, Infernum r_i_ad% AD more, Crescendum r_cre chakrams.
          Unused, the window ends with the cooldown capped (r_reset).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_aphelios.data_champion")
ID = "league_aphelios"
FX = "asset/league/effects/league_aphelios_fx"
BIG = "asset/league/effects/league_aphelios_big"
WEAPONS = ["cal", "sev", "grav", "inf", "cre"]     # the cycle's order

# Numbers: the first draft from League's ratios inside the pack's ADC ranges (league_jinx / league_kaisa 100 +20 attack,
# 900 +90 hp, range 55000, an attack every 56-60 ticks). League's Aphelios: 600 +102 hp, 55 AD +2.3, 26 armour +4.2,
# 30 mr, 325 move, 550 range (Calibrum +100), 0.665 attack speed; Q cds 9-10 s, R 120-100 s.
# Balance (work/sim/kd.py 900 s, bottom lane against the five base ADCs, three lineups, both sides): the draft -1.27
# (seeds 1-12; league_xayah +2.20, league_jinx +5.44); without skills -0.48, so the skills were weak: Q / R x~1.6, cast
# ranges = the attack's, attack 104 +0.37; shorter Q / R casts (a long hold cost attacks) and hp 980, armour 24 +1.57 /
# +0.68 (seeds 1-12 / 13-24; xayah +2.20 / +1.79); then attack 107, hp 1020 +1.44 (seeds 1-24; attack 108 alone +1.45
# but -1.02 against the gunner, Q / R +20% +0.99) and +1.50 on seeds 25-36 (xayah +2.13). Yasuo's R: 0.29 a game with
# him bottom (base archer 0.62, league_jinx 1.00) - league_yasuo unchanged.
P = {
    "hp": 1020, "hp_g": 88, "atk": 107, "atk_g": 22, "def": 24, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 58, "a_st": 6, "a_speed": 9000, "a_y": -3000,
    # magazine (League 50 shots, Q 10)
    "ammo": 20, "q_cost": 4,
    # the weapons' attacks
    "c_range": 10000, "sev_vamp": 10, "sev_as": 20, "grav_slow": 25, "grav_slow_t": 60, "grav_mark_t": 150,
    "grav_mk_cd": 50, "inf_main": 85, "inf_splash": 25, "inf_r": 14000, "cre_ad": 5, "cre_t": 240,
    # the off hand's on-hit (Severum Q's every second shot, Infernum Q's follow-ups, the sentry)
    "off_c_ad": 20, "off_s_heal": 8, "off_s_hr": 4, "off_g_slow": 20, "off_i_ad": 20,
    # skill slot
    "s_cd": 60, "s_range": 55000,
    # Calibrum Moonshot (League 60-160 + 42-60% bonus AD, 1450 range; the mark 15 + 20% bonus AD)
    "qcd_cal": 540, "q_c_anim": 20, "q_c_lock": 10, "q_c_speed": 8000, "q_c_len": 120000, "q_c_w": 4000, "q_c_y": -3000,
    "q_c_dmg": 110, "q_c_ad": 100, "q_c_pop": 6, "q_p_dmg": 40, "q_p_ad": 60,
    # Severum Onslaught (League 1.75 s, +20% move, 10-25 + 20-35% bonus AD a shot, heal on each)
    "qcd_sev": 540, "q_s_anim": 14, "q_s_ms": 20, "q_s_t": 105, "q_s_n": 8, "q_s_r": 50000, "q_s_dmg": 15, "q_s_ad": 45,
    "q_s_heal": 6, "q_s_hr": 3,
    # Gravitum Binding Eclipse (League 50-130 + 26-50% bonus AD magic, root 1 s, cd 12-10 s)
    "qcd_grav": 600, "q_g_anim": 14, "q_g_at": 8, "q_g_root": 60, "q_g_dmg": 50, "q_g_ad": 50,
    # Infernum Duskwave (League 25-65 + 56-80% bonus AD, then the off-hand shots, cd 9-6 s)
    "qcd_inf": 480, "q_i_anim": 18, "q_i_at": 10, "q_i_r": 45000, "q_i_cone": 600, "q_i_wv": 1000, "q_i_wt": 18, "q_i_wy": -5000, "q_i_dmg": 50, "q_i_ad": 100,
    "q_off_ad": 70,
    # Crescendum Sentry (League 31-90 + 40% AD a shot, ~5.5 s, cd 9-6 s)
    "qcd_cre": 540, "q_r_anim": 16, "q_r_at": 10, "q_r_t": 300, "q_r_per": 30, "q_r_r": 35000, "q_r_dmg": 20,
    "q_r_ad": 40,
    # W Phase
    "s2_cd": 90, "w_range": 55000, "w_anim": 18,
    # R Moonlight Vigil (League 125-225 + 20% bonus AD + 100% AP, radius 400, 1300 range)
    "r_cd": 1500, "r_arm": 360, "r_poll": 15, "r_range": 90000, "r_reset": 300, "r_anim": 24, "r_at": 14,
    "r_speed": 9000, "r_w": 5000, "r_y": -3000, "r_rad": 22000, "r_dmg": 160, "r_ad": 120,
    "r_c_ad": 60, "r_s_heal": 60, "r_s_hr": 30, "r_g_slow": 90, "r_g_t": 90, "r_i_ad": 50, "r_cre": 3,
    # his spoken lines (Alune's), at most one every vo_gap ticks
    "vo_gap": 600,
    # the add-on (addons/league_aphelios): Severum swapped to the main hand below low_hp% health with an enemy champion
    # within low_near, at most once every low_cd ticks; native = 1 builds its copy (passive league_aphelios:queue)
    "low_hp": 35, "low_near": 60000, "low_cd": 360, "native": 0,
    # test builds: 1..5 = that weapon only in the main hand (no rotation, no W); off = 1 no Q, 2 no W / R, 3 neither
    "lock": 0, "off": 0,
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


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(shape, target, effects, forward=None):
    apply = {"Forward": {"offset": forward}} if forward is not None else "AroundCaster"
    return {"type": "RangeEffect", "shape": shape, "target": target, "apply_type": apply, "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(circle(1000), "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def splash(name, speed, y, rng, effects):
    return {"type": "TargetSplashProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, target, end):
    """A hidden ParabolicProjectile onto the target's spot as it is now; its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 960000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, target, effects):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def turret(name, radius, tick, period, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def lives(*effects):
    """Effects only while he lives (a dead caster's Delayed effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (champion-data 5). Only inside Delayed chains, lobs and zones,
    which the AI does not score, so the effects are not copied into the search as league_pantheon's lives() does."""
    return combine(pick(1, "AllyOnlySelf", flag("live", 1)), sw("live", combine(*effects)), *rm("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def by_main(p, effects):
    """effects[w] for the main weapon (no flag yet = Calibrum, his start)."""
    out = effects["cal"]
    for w in reversed(WEAPONS[1:]):
        out = sw(f"mw_{w}", effects[w], out)
    return out if not p["lock"] else effects[WEAPONS[p["lock"] - 1]]


def by_off(effects):
    """effects[w] for the off-hand weapon (no flag yet = Severum)."""
    out = effects["sev"]
    for w in reversed([w for w in WEAPONS if w != "sev"]):
        out = sw(f"ow_{w}", effects[w], out)
    return out


def build(p):
    main_fields = {"cal": {"range": p["c_range"]}, "sev": {"vamp": p["sev_vamp"], "attack_speed_mult": p["sev_as"]},
                   "grav": {}, "inf": {}, "cre": {}}

    def set_main(w, sound=True):
        return combine(*rm(*[f"mw_{x}" for x in WEAPONS]), flag(f"mw_{w}", None, **main_fields[w]),
                       sfx(f"swap_{w}") if sound else None)

    def set_off(w):
        return combine(*rm(*[f"ow_{x}" for x in WEAPONS]), flag(f"ow_{w}", None))

    # ------------------------------------------------------------------ the magazine (5-bit counter b0..b4)
    bits = [f"b{i}" for i in range(5)]

    def fill():
        return combine(*rm(*bits), *[flag(b, None) for i, b in enumerate(bits) if p["ammo"] >> i & 1])

    def dec(i=0):
        """One shot off: the lowest set bit goes, the ones under it come on; below zero sets `empty`."""
        if i == 5:
            return flag("empty", None)
        return sw(bits[i], combine(*rm(bits[i])), combine(flag(bits[i], None), dec(i + 1)))

    def zero(i=0):
        return flag("empty", None) if i == 5 else sw(bits[i], NONE, zero(i + 1))

    def rotate():
        """The emptied main hand takes the cycle's next weapon that is not in the off hand."""
        nxt = lambda w: WEAPONS[(WEAPONS.index(w) + 1) % 5]
        pieces = {w: sw(f"ow_{nxt(w)}", set_main(nxt(nxt(w))), set_main(nxt(w))) for w in WEAPONS}
        return combine(by_main(dict(p, lock=0), pieces), cview("swap"))

    magazine = combine(dec(), sw("q_spent", combine(*rm("q_spent"), *[dec() for _ in range(p["q_cost"])])), zero(),
                       sw("empty", combine(*rm("empty"), rotate(), fill())))
    if p["lock"]:
        magazine = NONE
    init = sw("init", NONE, combine(flag("init", None),
                                    set_main(WEAPONS[p["lock"] - 1] if p["lock"] else "cal", False), set_off("sev"),
                                    fill()))

    # ------------------------------------------------------------------ the weapons' hits
    mark = casted(p["grav_mark_t"], 1, sw("g_bind", combine(
        {"type": "Bind", "duration": p["q_g_root"]}, attack(p["q_g_dmg"], p["q_g_ad"]), view("q_g_hit"), tsfx("q_g_hit"))),
        kind="Poison")

    def grav_mark():
        """A Gravitum mark on the unit hit, at most one every grav_mk_cd ticks; g_any: some mark is alive."""
        return sw("g_mk", NONE, combine(flag("g_mk", p["grav_mk_cd"]), refresh("g_any", p["grav_mark_t"]), mark))

    off_hit = {
        "cal": attack(0, p["off_c_ad"]),
        "sev": heal(p["off_s_heal"], p["off_s_hr"]),
        "grav": combine(buff("g_slow", p["grav_slow_t"], move_speed_mult=-p["off_g_slow"]), grav_mark()),
        "inf": attack(0, p["off_i_ad"]),
        "cre": flag("cre", p["cre_t"], attack_mult=p["cre_ad"]),
    }

    def shot(ratio, w):
        return [attack(0, ratio), view("a_hit"), tsfx(f"a_{w}_hit")]

    a = p["a_st"] - 1
    attacks = {
        "cal": combine(anim("a_cal", p["atk_dur"]), sfx("a_cal"), delayed(a, homing("a_cal", p["a_speed"], p["a_y"], "Enemy", shot(100, "cal")))),
        "sev": combine(anim("a_sev", p["atk_dur"]), sfx("a_sev"),
                       delayed(a, homing("a_sev", p["a_speed"], p["a_y"], "Enemy", shot(100, "sev")))),
        "grav": combine(anim("a_grav", p["atk_dur"]), sfx("a_grav"), delayed(a, homing(
            "a_grav", p["a_speed"], p["a_y"], "Enemy",
            shot(100, "grav") + [buff("g_slow", p["grav_slow_t"], move_speed_mult=-p["grav_slow"]), grav_mark()]))),
        "inf": combine(anim("a_inf", p["atk_dur"]), sfx("a_inf"), delayed(
            a, homing("a_inf", p["a_speed"], p["a_y"], "Enemy", shot(p["inf_main"] - p["inf_splash"], "inf")),
            splash("a_inf_s", p["a_speed"], p["a_y"], p["inf_r"], [attack(0, p["inf_splash"])]))),
        "cre": combine(anim("a_cre", p["atk_dur"]), sfx("a_cre"), delayed(a, homing(
            "a_cre", p["a_speed"], p["a_y"], "Enemy", shot(100, "cre") + [flag("cre", p["cre_t"], attack_mult=p["cre_ad"])]))),
    }
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(init, by_main(p, attacks), magazine), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: the main weapon's Q
    def q_start(w, tick):
        return combine(flag(f"qcd_{w}", p[f"qcd_{w}"]), flag("q_spent", None), anim(f"q_{w}", tick), sfx(f"q_{w}"),
                       voice(f"vo_q_{w}", p))

    # the add-on's copy (native): the mark is shot off with the main weapon's on-hit at that moment - the add-on swaps
    # the off hand in as Moonshot leaves (League's Calibrum Q -> W: the mark popped by the other gun, Gravitum's slow and
    # mark ready for Binding Eclipse); Calibrum itself adds nothing (the main pack's pop unchanged)
    pop_gift = [by_main(p, dict(off_hit, cal=NONE))] if p["native"] else []
    pop = delayed(p["q_c_pop"], lives(homing("q_c_pop", 20000, p["a_y"], "Enemy",
                                             [attack(p["q_p_dmg"], p["q_p_ad"]), view("q_c_pop"), tsfx("q_c_pop")]
                                             + pop_gift)))
    moonshot = line("q_c_shot", p["q_c_speed"], p["q_c_len"], p["q_c_w"], p["q_c_y"], "EnemyWithoutTower", False,
                    [attack(p["q_c_dmg"], p["q_c_ad"]), view("q_c_hit"), tsfx("q_c_hit"), pop])
    q_cal = combine(q_start("cal", p["q_c_anim"]), lob("q_c_lock", p["q_c_lock"], "Enemy", [lives(moonshot)]))

    sev_hit = [attack(p["q_s_dmg"], p["q_s_ad"]), heal(p["q_s_heal"], p["q_s_hr"]), view("q_s_hit")]
    per = p["q_s_t"] // p["q_s_n"]
    q_sev = combine(q_start("sev", p["q_s_anim"]), refresh("q_s_haste", p["q_s_t"], move_speed_mult=p["q_s_ms"]),
                    cview("q_s_on"),
                    on_me(casted(p["q_s_t"], 2 * per, pick(p["q_s_r"], "EnemyWithoutTower", homing(
                        "q_s_bolt", 20000, p["a_y"], "Enemy", sev_hit))),
                          delayed(per, casted(p["q_s_t"] - per, 2 * per, pick(p["q_s_r"], "EnemyWithoutTower", homing(
                              "q_s_off", 20000, p["a_y"], "Enemy", sev_hit[:1] + [by_off(off_hit), view("q_s_hit")]))))))

    q_grav = sw("g_any", combine(q_start("grav", p["q_g_anim"]), cview("q_g_cast"),
                                 delayed(p["q_g_at"] - 1, refresh("g_bind", 1))))

    off_shot = homing("q_i_off", 20000, p["a_y"], "Enemy", [attack(0, p["q_off_ad"]), by_off(off_hit), view("a_hit")])
    duskwave = around({"DirDot": {"radius": p["q_i_r"], "range": p["q_i_cone"]}}, "EnemyWithoutTower",
                      [attack(p["q_i_dmg"], p["q_i_ad"]), view("q_i_hit"), off_shot], forward=1000)
    # the wave's picture rides a view-only LinearProjectile crawling toward the target (q_i_wv a tick for q_i_wt ticks,
    # lifted to his gun by q_i_wy): a projectile's picture turns with it, a caster picture would point right on the red
    # side too (the client never mirrors one: SKILL.md "Both sides"); the picture is symmetric top to bottom
    wave = line("q_i_wave", p["q_i_wv"], p["q_i_wv"] * p["q_i_wt"], 1, p["q_i_wy"], "Enemy", True, [])
    q_inf = combine(q_start("inf", p["q_i_anim"]), delayed(p["q_i_at"] - 1, lives(wave, duskwave)))

    sentry = turret("q_r_turret", p["q_r_r"], p["q_r_t"], p["q_r_per"],
                    [lives(attack(p["q_r_dmg"], p["q_r_ad"]), by_off(off_hit), view("q_r_hit"))])
    # the sentry's picture: a ViewEffect on the landing point (never turned; a zone's own picture is turned half round
    # when cast leftward - lint), its tag looping for the sentry's q_r_t ticks
    q_cre = combine(q_start("cre", p["q_r_anim"]), lob("q_r_drop", p["q_r_at"], "Enemy",
                                                         [sentry, view("q_r_sentry"), sfx("q_r_land")]))

    qs = {"cal": q_cal, "sev": q_sev, "grav": q_grav, "inf": q_inf, "cre": q_cre}
    skill = action("idle", 3, p["s_cd"], 1, p["s_range"], "Targeting", "EnemyWithoutTower",
                   by_main(p, {w: sw(f"qcd_{w}", NONE, qs[w]) for w in WEAPONS}) if not p["off"] & 1 else NONE,
                   key="skill")

    # ------------------------------------------------------------------ skill2: W Phase
    main_cd = by_main(dict(p, lock=0), {w: sw(f"qcd_{w}", flag("m_cd", 1)) for w in WEAPONS})
    off_cd = by_off({w: sw(f"qcd_{w}", flag("o_cd", 1)) for w in WEAPONS})
    # the swap, weapon by weapon in the cycle's order: the main hand's goes to the off hand, the off hand's to the main
    # hand. Exactly one mw_ and one ow_ flag are on here, never of the same weapon (init sets Calibrum / Severum, the
    # magazine's rotate takes a weapon not in the off hand, this swap exchanges them, the add-on's queue and low swap
    # replace one flag of a hand by another weapon's), so each step touches only its own weapon's flags and the flags
    # come back in the same order as with the temp flags t_m_ / t_o_ the swap used to lay, clear and read (58 nodes
    # instead of 113; the game copies skill2 every tick: skill-tree slimming, 2026-10-18)
    swap = combine(*[sw(f"mw_{w}", combine(*rm(f"mw_{w}"), flag(f"ow_{w}", None)),
                        sw(f"ow_{w}", combine(*rm(f"ow_{w}"), flag(f"mw_{w}", None, **main_fields[w]),
                                              sfx(f"swap_{w}"))))
                     for w in WEAPONS],
                   anim("skill2", p["w_anim"]), cview("swap"), voice("vo_w", p))
    phase = combine(*rm("m_cd", "o_cd"), main_cd, off_cd, sw("m_cd", sw("o_cd", NONE, swap)), *rm("m_cd", "o_cd"))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    sw("init", phase) if not p["lock"] else NONE, key="skill2")

    # ------------------------------------------------------------------ ult: R Moonlight Vigil, armed
    gifts = {
        "cal": delayed(4, lives(homing("r_c_shot", 20000, p["a_y"], "Enemy", [attack(0, p["r_c_ad"]), view("a_hit")]))),
        "sev": heal(p["r_s_heal"], p["r_s_hr"]),
        "grav": combine(buff("r_slow", p["r_g_t"], move_speed_mult=-p["r_g_slow"]), refresh("g_any", p["grav_mark_t"]),
                        mark),
        "inf": attack(0, p["r_i_ad"]),
        "cre": combine(*[flag("cre", p["cre_t"], attack_mult=p["cre_ad"]) for _ in range(p["r_cre"])]),
    }
    blast = [attack(p["r_dmg"], p["r_ad"]), view("r_hit"), by_main(p, gifts)]
    burst = delayed(1, lob("r_burst", 1, "EnemyChampion", [zone("r_area", p["r_rad"], "EnemyWithoutTower", blast),
                                                           view("r_boom"), sfx("r_boom")]))
    moon = line("r_moon", p["r_speed"], 160000, p["r_w"], p["r_y"], "EnemyChampion", False, [burst])

    def fire():
        """At the locked spot (a hidden lob's end): the cast now, the moonlight from him to that spot on r_at."""
        return combine(*rm("r_arm"), flag("r_go", p["r_anim"]),
                       on_me(anim("ult", p["r_anim"]), cview("r_cast"), sfx("r"), voice("vo_r", p)),
                       delayed(p["r_at"] - 1, lives(sfx("r_shot"), moon)))

    count = zone("r_count", p["r_rad"], "EnemyChampion", [sw("n1", flag("n2", 3), flag("n1", 3))])
    crowd = lob("r_look", 1, "EnemyChampion", [count, delayed(2, sw("n2", sw("r_go", NONE, fire()))), *rm()])
    held = lob("r_look_cc", 1, "EnemyChampion", [sw("r_go", NONE, fire())])
    look = combine(*rm("n1", "n2"), pick(p["r_range"], "EnemyChampionInCC", held),
                   sw("r_go", NONE, pick(p["r_range"], "EnemyChampionRecentlyAttacked", crowd)))
    poll = sw("r_arm", sw("r_go", NONE, look))
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_reset", 3, ult_cooldown_mult=p["r_reset"])))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
                 combine(refresh("r_arm", p["r_arm"]), on_me(casted(p["r_arm"], p["r_poll"], poll),
                                                            delayed(p["r_arm"], reset))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                             "tag": tag or name, "z": z, "is_follow": follow}
    # the bullets: repeat false - their strips start with empty ticks (unseen until past the muzzle) and hold the last
    # frame (tools/art/import_aphelios_fx.py flight); the sentry loops
    P_ = lambda name, anim_=FX, z=1, tag=None, rep=False: {"type": "Animated", "name": n(name), "anim": anim_,
                                                          "tag": tag or name, "repeat": rep, "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_(f"a_{w}") for w in WEAPONS] + [P_("a_inf_s"), P_("q_c_shot", BIG), P_("q_c_pop"),
                                                  P_("q_s_bolt"), P_("q_s_off", FX, 1, "off_bolt"),
                                                  P_("q_i_off", FX, 1, "off_bolt"), P_("q_i_wave", BIG, 3),
                                                  P_("r_c_shot", FX, 1, "q_c_pop"), P_("r_moon", BIG)]
    views_e = [E("a_hit"), E("swap", FX, 3), E("q_c_hit"), E("q_c_pop", FX, 2, True, "q_c_pop_b"), E("q_s_on", FX, -1),
               E("q_s_hit"), E("q_g_cast", BIG, -1), E("q_g_hit"), E("q_i_hit"),
               E("q_r_hit"), E("r_cast", BIG, -1), E("r_hit"), E("r_boom", BIG, 2, False),
               E("q_r_sentry", BIG, 0, False, "q_r_turret")]
    views_b = [B_(f"mw_{w}", FX, -1) for w in WEAPONS] + [B_("g_slow", FX, -1), B_("r_slow", FX, -1, "g_slow"),
                                                         B_("q_s_haste", FX, -1), B_("cre", FX, 3)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if p["native"]:
        kit["passive"] = {"passive_ref": f"{ID}:queue",
                          "params": {"c_range": p["c_range"], "sev_vamp": p["sev_vamp"], "sev_as": p["sev_as"],
                                     "low_hp": p["low_hp"], "near": p["low_near"], "low_cd": p["low_cd"]}}
    if p["off"] & 2:
        kit["skill2"]["effect"] = NONE
        kit["ult"]["effect"] = NONE
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
