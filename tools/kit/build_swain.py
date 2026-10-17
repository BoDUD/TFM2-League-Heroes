"""Build league_swain.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_swain.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-17: mid, W folded into the passive, the add-on league_swain, PPU 1.5 - 「全按推荐」).
TFM2 has three active slots: Death's Hand is `skill`, Nevermove `skill2`, Demonic Ascension the `ult`; Vision of Empire
(W) has no slot - the passive's watch casts it on its own (Rek'Sai's E rides her attack the same way).
  passive Ravenous Flock (狂食鸦群): a Soul Fragment (`frag`) heals him p_heal + p_heal_ap% AP (League: 6% of max
          health; no heal reads max health) and gives p_hp maximum health for the rest of the life (a Permanent caster
          buff with `hp`, one per fragment: same-name buffs add up). Fragments: a champion hit by Vision of Empire, a
          champion pulled by Nevermove, an enemy champion he damaged dying within p_win ticks (league_viego's takedown
          window: League's dropped fragments the ravens bring back). Buffs die with him, so the main pack's fragments
          last a life (the tooltip says so); the add-on keeps them (league_veigar_power's way).
  attack  a raven bolt from the demon hand (homing), 100% AD physical like every mage's attack in the pack; its
          champion-only twin opens the takedown window.
  skill   Q Death's Hand (解脱之触), `Targeting` on `EnemyWithoutTower` (q_range): five bolts fly out in a fan (one
          penetrating LinearProjectile with the fan's picture, aimed where the target stood on the release tick); the
          hits are cones in front of him on that tick (league_darius E's Forward + DirDot, aim locked): every enemy in
          the long cone (q_len, q_dot) takes q_dmg + q_ap% AP, one in the short cone (q_near) the extra bolts' q_dmg2 +
          q_ap2% AP more (League: more bolts on a close target, more damage).
  skill2  E Nevermove (永不复行), `Targeting` on `EnemyWithoutTower` (e_range): the demon hand flies out to where the
          target stood (e_len, a LinearProjectile, nothing hit), turns and comes back to him (a
          BackToCasterLinearProjectile from its end): every enemy it meets takes e_dmg + e_ap% AP and is rooted e_root
          ticks (Bind). A champion rooted is pulled e_pull_d toward him e_pull_at ticks later (a Grab, League's
          recast) and gives a fragment. Dodgeable: the out-flight is aimed once.
  W       Vision of Empire (帝国视界), automatic: every w_cd ticks the watch picks an enemy champion recently in a fight
          (`EnemyChampionRecentlyAttacked`) within w_range and opens the eye at its feet (a hidden lob lands there):
          w_delay ticks later the eye bursts (w_r): w_dmg + w_ap% AP, w_slow% slow for w_slow_t ticks; each champion
          hit gives a fragment. The eye does not follow - walking out dodges it.
  ult     R Demonic Ascension (恶魔升华), `Targeting` on `EnemyChampion` (r_range), armed by the watch (`r_ok`, the
          user's rule 「看好时机」): two enemy champions within r_r of him, or an enemy champion in CC within r_range
          while an allied champion stands within r_ally. He rises as the demon (`ult`, `r_on` for r_t0 ticks); every
          r_pulse ticks while `r_on` lasts he drains every enemy within r_r: r_dmg + r_ap% AP, healing r_heal +
          r_heal_ap% AP per champion and r_heal_m per minion or monster; each pulse that reaches a champion keeps the
          form r_keep ticks longer (League: the form lasts while he drains champions), r_max at most. From r_flare_at
          ticks on, Demonflare (恶魔耀光) bursts whenever an enemy champion is within r_r and it is off cooldown
          (r_flare_cd): r_fl + r_fl_ap% AP round him, r_fl_slow% slow for r_fl_slow_t ticks. While `r_on` lasts his
          attack, Q and E play the demon's strips (r_attack, r_skill, r_skill2; idle / run / hit can't change in data -
          the add-on swaps the whole body) and the wings aura (`r_on`'s view) follows him.
  watch   A life-long `AddCasted` started by his first action of each life (`init`; buffs die with him), every
          watch_p ticks: counts enemy champions within r_r (c_e1, c_e2), allied champions within r_ally (c_a1, c_a2 =
          one besides him), an enemy champion in CC within r_range (c_cc); sets r_ok; casts W when it is ready.
The add-on copy (--native): the passive `league_swain:flock` keeps the fragments after death, swaps the whole body to
the demon while `r_on` lasts and arms R on his real health too; the data keeps every hit, picture and sound.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_swain.data_champion")
ID = "league_swain"
FX = "asset/league/effects/league_swain_fx"
BIG = "asset/league/effects/league_swain_big"

# Timings: placeholders until the strips (tools/art/rig_swain.py) fix the release frames.
P = {
    # stats (Magician base: attack 80 +6, ability power 40 +20, hp 900 +100, defence 20 +7, mr 20 +3, move 900);
    # League's Swain: 595 +99 hp, 525 range, a drain mage who stays in the fight
    "hp": 940, "hp_g": 105, "atk": 76, "atk_g": 6, "mp": 40, "mp_g": 20, "def": 22, "def_g": 7, "mr": 22, "mr_g": 3,
    "ms": 900, "ms_g": 9,
    # attack: the raven bolt leaves the demon hand on a_rel
    "atk_range": 52000, "atk_dur": 26, "atk_cd": 90, "a_rel": 11, "bolt_speed": 5000, "bolt_y": -3000,
    # passive: Ravenous Flock (League: +15 max health a fragment, heal 6% max health; fragments from W, E2, deaths)
    "p_hp": 15, "p_heal": 45, "p_heal_ap": 20, "p_win": 180,
    # skill: Q Death's Hand (League: 725 range, 32 deg, 5 bolts, 60-180 + 45% AP, +25% a further bolt up to 2x, cd 7-3)
    "q_cd": 300, "q_range": 55000, "q_dur": 24, "q_rel": 9, "q_len": 62000, "q_dot": 940, "q_near": 32000,
    "q_dmg": 70, "q_ap": 50, "q_dmg2": 45, "q_ap2": 35, "q_speed": 9000,
    # skill2: E Nevermove (League: 850 range, out 1125-1800, back 2000-2800, 90-250 + 70% AP, root 1.5 s, recast pull
    # 290 + fragment, cd 12-10)
    "e_cd": 600, "e_range": 65000, "e_dur": 26, "e_rel": 9, "e_len": 70000, "e_out": 4000, "e_back": 5000,
    "e_rad": 9000, "e_dmg": 80, "e_ap": 60, "e_root": 90, "e_pull_at": 30, "e_pull_d": 29000, "e_pull_v": 1500,
    # W Vision of Empire (League: 1.5 s fuse, 325 radius, 70-250 + 60% AP, 50% slow 1.5 s, fragment, cd 20-16)
    "w_cd": 960, "w_range": 100000, "w_travel": 15, "w_delay": 90, "w_r": 30000, "w_dmg": 60, "w_ap": 50,
    "w_slow": 50, "w_slow_t": 90,
    # ult: R Demonic Ascension (League: 650 radius, drain every 0.5 s 7.5-17.5 + 2% AP, heal 7.5-22.5 + 2.5% AP a
    # champion (10% vs minions), energy 50 lasting ~5 s alone, kept while draining champions; Demonflare after 2 s,
    # 8 s cd, 675 radius, 150-350 + 40% AP, 50% slow decaying 1.5 s; cd 120)
    "r_cd": 3600, "r_range": 55000, "r_dur": 30, "r_r": 60000, "r_ally": 45000, "r_t0": 240, "r_keep": 120,
    "r_max": 900, "r_pulse": 30, "r_dmg": 15, "r_ap": 5, "r_heal": 15, "r_heal_ap": 5, "r_heal_m": 2,
    "r_flare_at": 120, "r_flare_cd": 480, "r_fl": 120, "r_fl_ap": 50, "r_fl_slow": 50, "r_fl_slow_t": 90,
    "r_fl_dur": 16,
    # the watch
    "watch_p": 12,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_swain (its native passive)
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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ap_ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap_ratio, "heal_type": "Caster"}


def slow(name, pct, tick):
    return buff(name, tick, move_speed_mult=-pct)


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def cone(radius, dot, target, effects):
    """In front of him toward the cast's target: within radius, at most acos(dot / 1000) off the aim."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": dot}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, rng, radius, target, effects):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": rng,
            "shape": circle(radius), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive: Ravenous Flock
    def frag():
        """A Soul Fragment: the ravens bring it to him - heal, + p_hp max health for the life."""
        return combine(flag("frag", None, hp=p["p_hp"]), heal(p["p_heal"], p["p_heal_ap"]), cview("p_frag"),
                       sfx("p_frag"))

    # the takedown window (league_viego): a champion he damaged dying within p_win ticks drops a fragment for him
    watch_death = sw("p_alive", NONE, sw("p_lock", NONE, combine(refresh("p_lock", p["p_win"]),
                                                                  refresh("p_alive", p["p_win"]), frag())))

    def track():
        """On a champion he hit: keeps p_alive up while it lives; a watcher on him sees it lapse = a takedown."""
        return combine(casted(p["p_win"], 1, refresh("p_alive", 2)),
                       on_me(refresh("p_alive", 3), casted(p["p_win"] - 2, 1, watch_death)))

    # ------------------------------------------------------------------ W: Vision of Empire (cast by the watch)
    eye_hit = [ap(p["w_dmg"], p["w_ap"]), slow("w_slow", p["w_slow"], p["w_slow_t"]), view("w_hit"), tsfx("w_hit")]
    eye = [view("w_eye"), sfx("w_open"),
           zone("w_burst", p["w_r"], p["w_delay"] + 1, p["w_delay"], "EnemyWithoutTower", eye_hit),
           zone("w_soul", p["w_r"], p["w_delay"] + 1, p["w_delay"], "EnemyChampion", [frag(), track()])]
    vision = combine(flag("w_cd", p["w_cd"]), voice("vo_w", p), sfx("w_cast"), lob("w_lob", p["w_travel"], eye,
                                                                                    "EnemyChampion"))

    # ------------------------------------------------------------------ the watch (R's arming, W)
    tick = p["watch_p"]
    count = combine(*rm("c_e1", "c_e2", "c_a1", "c_a2", "c_cc"),
                    around(p["r_r"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]),
                    around(p["r_ally"], "AllyChampion", [sw("c_a1", flag("c_a2", 3), flag("c_a1", 3))]),
                    pick(p["r_range"], "EnemyChampionInCC", flag("c_cc", 3)))
    arm = sw("c_e2", refresh("r_ok", tick + 2), sw("c_cc", sw("c_a2", refresh("r_ok", tick + 2))))
    cast_w = sw("w_cd", NONE, pick(p["w_range"], "EnemyChampionRecentlyAttacked", vision))
    watch = on_me(casted(1000000, tick, count, delayed(1, arm, cast_w)))
    life = sw("init", NONE, combine(flag("init", None), watch))

    # ------------------------------------------------------------------ attack: the raven bolt
    bolt = combine(homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy", [attack(0, 100), view("a_hit"),
                                                                          tsfx("a_hit")]),
                   homing("a_twin", p["bolt_speed"], p["bolt_y"], "EnemyChampion", [track()]))
    a_eff = combine(life, sw("r_on", anim("r_attack", p["atk_dur"])), sfx("a_cast"),
                    delayed(p["a_rel"] - 1, bolt))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", a_eff,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Death's Hand
    q_hit = [ap(p["q_dmg"], p["q_ap"]), view("q_hit"), tsfx("q_hit")]
    q_more = [ap(p["q_dmg2"], p["q_ap2"])]
    fan = combine(line("q_bolts", p["q_speed"], p["q_len"], 1, -2000, "Enemy", True, []),
                  cone(p["q_len"], p["q_dot"], "EnemyWithoutTower", q_hit),
                  cone(p["q_near"], p["q_dot"], "EnemyWithoutTower", q_more),
                  cone(p["q_len"], p["q_dot"], "EnemyChampion", [track()]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(life, sw("r_on", anim("r_skill", p["q_dur"]), anim("skill", p["q_dur"])), sfx("q"),
                           voice("vo_q", p), delayed(p["q_rel"] - 1, fan)))

    # ------------------------------------------------------------------ skill2: E Nevermove
    pull = {"type": "Grab", "speed": p["e_pull_v"], "tick": p["e_pull_d"] // p["e_pull_v"]}
    e_hit = [ap(p["e_dmg"], p["e_ap"]), {"type": "Bind", "duration": p["e_root"]}, view("e_hit"), tsfx("e_hit")]
    e_champ = [track(), delayed(p["e_pull_at"], pull, view("e_pull"), tsfx("e_pull"), frag())]
    hand_back = [back("e_back", p["e_back"], p["e_len"] + 20000, p["e_rad"], "EnemyWithoutTower", e_hit),
                 back("e_twin", p["e_back"], p["e_len"] + 20000, p["e_rad"], "EnemyChampion", e_champ)]
    hand = line("e_out", p["e_out"], p["e_len"], 1, -2000, "Enemy", True, [], end=hand_back)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(life, sw("r_on", anim("r_skill2", p["e_dur"]), anim("skill2", p["e_dur"])), sfx("e"),
                            voice("vo_e", p), delayed(p["e_rel"] - 1, hand)))

    # ------------------------------------------------------------------ ult: R Demonic Ascension
    drain_m = [ap(p["r_dmg"], p["r_ap"]), heal(p["r_heal_m"], 0), view("r_drain")]
    drain_c = [heal(p["r_heal"], p["r_heal_ap"]), refresh("r_hit", 3)]
    flare = combine(refresh("r_fcd", p["r_flare_cd"]), anim("r_flare", p["r_fl_dur"]), cview("r_flare"), sfx("r_flare"),
                    voice("vo_r2", p),
                    around(p["r_r"], "EnemyWithoutTower", [ap(p["r_fl"], p["r_fl_ap"]),
                                                          slow("r_slow", p["r_fl_slow"], p["r_fl_slow_t"]), view("r_fl_hit"),
                                                          tsfx("r_fl_hit")]),
                    around(p["r_r"], "EnemyChampion", [track()]))
    pulse = sw("r_on", combine(
        around(p["r_r"], "EnemyWithoutTower", drain_m),
        around(p["r_r"], "EnemyChampion", drain_c + [track()]),
        delayed(1, sw("r_hit", combine(
            # the form lasts while he drains a champion: r_on renewed to r_keep once the first r_t0 is that short
            # (r_hold), so never shortened; the pulses stop after r_max and r_on runs out
            sw("r_hold", NONE, refresh("r_on", p["r_keep"])),
            sw("r_early", NONE, sw("r_fcd", NONE, flare)))))))
    rise = combine(anim("ult", p["r_dur"]), cview("r_cast"), sfx("r"), voice("vo_r", p),
                   *rm("r_fcd", "r_hold", "r_early"), refresh("r_on", p["r_t0"]), flag("r_early", p["r_flare_at"]),
                   flag("r_hold", p["r_t0"] - p["r_keep"]),
                   on_me(casted(p["r_max"], p["r_pulse"], pulse)))
    # league_orianna's x trick: the game's AI scores the branch the flags pick between ticks, and the drain sits in an
    # AddCasted it does not count - r_x is never there between ticks, so the AI reads Demonflare's burst; when the slot
    # runs, the flag is up and the real branch goes
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), rise), ap(p["r_fl"], p["r_fl_ap"])), *rm("r_x"))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(life, sw("r_ok", scored)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    views_p = [{"type": "Animated", "name": n("a_bolt"), "anim": FX, "tag": "a_bolt", "repeat": True, "z": 2},
               {"type": "Animated", "name": n("q_bolts"), "anim": FX, "tag": "q_bolts", "repeat": False, "z": 2},
               {"type": "Animated", "name": n("e_out"), "anim": FX, "tag": "e_out", "repeat": True, "z": 2},
               {"type": "Animated", "name": n("e_back"), "anim": FX, "tag": "e_back", "repeat": True, "z": 2}]
    views_e = [E("a_hit"), E("q_hit"), E("e_hit"), E("e_pull"), E("w_eye", BIG, -1, False), E("w_hit"),
               E("p_frag", FX, 3), E("r_cast", BIG, 2), E("r_drain"), E("r_flare", BIG, 2), E("r_fl_hit")]
    views_b = [{"type": "Animated", "name": n("r_on"), "anim": BIG, "tag": "r_wings", "repeat": True, "z": -1}]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_swain:flock",
                            "params": {k: p[k] for k in ("p_hp", "r_r", "r_range")}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "CC", "Heal"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
