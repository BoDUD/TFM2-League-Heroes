"""Build league_akshan.data_champion (bottom, Range) from the parameters P.

    python tools/kit/build_akshan.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's pick, 2026-10-18: layout A with the add-on league_akshan, and W's revive for real - 「做成复活队友的吧」):
  passive Dirty Fighting (无所不用): every attack fires two shots (league_lucian's Lightslinger): the first a_ratio% AD,
          the second 50% AD on champions and 100% on minions and monsters (the shot's own champion check, a 1-tick
          flag read a tick later). Every hit of his - both shots, Q out and back, each E shot, each R bullet - counts:
          the third within p_t ticks deals p_dmg + p_ratio% AD more and, on a champion, shields him for p_sh +
          p_sh_r% AD over p_sh_t (p_scd between shields). The main pack counts his hits on anyone (league_vayne's
          ladder); the add-on counts them per target (league_vayne_bolts) and raises `p_go` for the third.
  attack  The double shot above.
  skill   Q Avengerang (去而复还): a `Direction` cast on `EnemyWithoutTower` (q_cast). Two ticks in, a champion within
          q_lock gets the aim locked on where it stands (league_sivir Q: an 8-tick hidden lob lands there, then the
          boomerang flies) - it can be walked out of; with no champion the boomerang flies the cast direction. Out
          q_range at q_speed through everything, back to him at q_back: q_dmg + q_ratio% AD each way; a champion hit
          gives him q_ms% move speed for q_ms_t. League's extra range per hit is left out.
  skill2  E Heroic Swing (骄行荡寇): a `Targeting` cast on `EnemyChampion` (e_range). He throws the hook (e_hook ticks),
          swings toward the target in e_n pulses (each a short slow MoveToTarget, the arc of League's swing as straight
          steps - data moves nothing along a curve), shooting the nearest enemy
          (champions first) every e_every ticks for e_dmg + e_ratio% AD, then rolls off away from the target with a
          last shot. The add-on also refreshes the cooldown on a champion takedown.
  W       Going Rogue (赴险夺人), no slot of its own: every attack counts the enemy champions within w_rad; two or more
          (and no `w_cd`) -> camouflage (`CasterInvisible` w_inv) and w_ms% move speed for w_inv (league_leblanc's
          count). The add-on adds the Scoundrel marks and the revive (addons/league_akshan).
  ult     R Comeuppance (恩怨相抵): a `Targeting` cast on `EnemyChampionRecentlyAttacked` (r_range: the stand-in for "a
          wounded champion", champion-data section 3). He channels r_ch ticks storing a bullet every r_store (r_n at
          most), crowd control breaks it (league_jhin's 6-tick poll); then the stored bullets go one every r_gap,
          each aimed where the champion stands (a 6-tick hidden lob, dodgeable) and flying r_speed until the FIRST
          enemy it meets (non-penetrating, `Enemy`: minions and towers block). Main pack: r_dmg + r_ratio% AD, every
          bullet that hit before adds r_up% (League's missing-health growth, approximated by the hits); the add-on
          deals the damage from the target's missing health instead and decides when to cast and when to fire.
Timings are placeholders until the strips exist (a_hit1 / a_hit2 from League's Attack1: two shots 0.12 s apart).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_akshan.data_champion")
ID = "league_akshan"
FX = "asset/league/effects/league_akshan_fx"
BIG = "asset/league/effects/league_akshan_big"

# Numbers = the 10-min classic-SDK simulations (bottom against archer, gunner, boomerang_hunter, poison_dart_hunter and
# bomber, three lineups, both sides, seeds 1-8, 2026-10-18, placeholder timings): the draft (attack 92, Q 70%, E 15 +30%,
# R 30 +20%) -1.92; attack 100 -0.29; + E 25 +60% +0.30; + R 60 +40% and Q 90% +1.37 (league_lucian +1.58).
P = {
    # stats (Range base: league_lucian 100 +20 attack, 900 +90 hp, 20 +7 defence, 15 +3 mr, 900 +9 move); League's
    # Akshan: 52 AD +3, 610 +107 hp, 26 +4.7 armour, 33 mr, 330 move, attack speed 0.638 +4%, range 500
    "hp": 900, "hp_g": 92, "atk": 100, "atk_g": 20, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    "regen": 0, "regen_g": 0,
    # attack: the double shot (League: second shot 50% AD on champions, 100% on minions)
    "atk_range": 55000, "atk_dur": 26, "atk_cd": 64, "a_hit1": 5, "a_hit2": 12, "a_speed": 7000, "a_y": -8000,
    "a_ratio": 100, "a2_ratio": 50,
    # passive Dirty Fighting (League: 3 hits in 5 s -> 15-150 +60% AP magic; champion -> shield 40-280 +35% bonus AD
    # 2 s, cd 16-4 s by level)
    "p_t": 300, "p_dmg": 20, "p_ratio": 30, "p_sh": 40, "p_sh_r": 35, "p_sh_t": 120, "p_scd": 600,
    # skill: Q Avengerang (League: 850 range, 45-165 +70% bonus AD each way, cd 9-5 s, 20% ms on a champion hit 1 s)
    "q_cd": 420, "q_cast": 95000, "q_lock": 110000, "q_dur": 24, "q_aim": 8, "q_range": 100000, "q_speed": 6500,
    "q_back": 7000, "q_w": 8000, "q_dmg": 45, "q_ratio": 90, "q_ms": 20, "q_ms_t": 60,
    # skill2: E Heroic Swing (League: 800 range, a shot every 0.231 s for 8-40 +25% AD, cd 18-12 s)
    "e_cd": 900, "e_range": 80000, "e_dur": 12, "e_hook": 8, "e_n": 6, "e_every": 14, "e_speed": 1500,
    "e_step": 40000, "e_seek": 60000, "e_dmg": 25, "e_ratio": 60, "e_back": 3000, "e_back_t": 10, "e_shot": 9000,
    # W Going Rogue (League: camouflage 2 s, +80-120 ms toward Scoundrels, cd 18-2 s)
    "w_rad": 40000, "w_inv": 120, "w_ms": 40, "w_cd": 1080,
    # ult: R Comeuppance (League: 2500 range, 2.5 s channel, 5/6/7 bullets, 25-45 +15% AD to 3x on missing health,
    # cd 100-70 s)
    "r_cd": 3000, "r_range": 160000, "r_dur": 6, "r_ch": 150, "r_store": 30, "r_n": 5, "r_gap": 6, "r_aim": 6,
    "r_speed": 20000, "r_reach": 220000, "r_w": 6000, "r_dmg": 60, "r_ratio": 40, "r_up": 30,
    # the add-on (addons/league_akshan): bullets from min to r_max x min as the target's missing health goes 0 -> r_full%
    "r_max": 3, "r_full": 67,
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


def unanim(*names):
    return [{"type": "RemoveCasterAnimation", "name": x} for x in names]


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def is_champ(*effects):
    """Inside a projectile's applied effects: the unit it hit, when that is a champion (league_sivir Q)."""
    return pick(1, "EnemyChampion", *effects, fp=True)


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end=(), penetrate=True, back=False):
    return {"type": "BackToCasterLinearProjectile" if back else "LinearProjectile", "name": n(name),
            "penetrate": penetrate, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": list(end), "speed": speed, "range": rng, "shape": circle(width)}


def lob(name, ticks, end):
    """A hidden 1-radius lob onto the target's spot: the aim is locked when it starts (league_sivir Q)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": ticks, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyChampion", "applied_effects": [],
            "end_effects": list(end)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False):
    """native: the add-on's copy (addons/league_akshan) - Dirty Fighting counted per target, R's bullets from the
    target's missing health, E's arc and refresh, the Scoundrel marks and the revive."""
    # ------------------------------------------------------------------ passive: the third hit
    proc = combine(attack(p["p_dmg"], p["p_ratio"]), view("p_hit"), tsfx("p_hit"),
                   is_champ(sw("p_scd", NONE, combine(
                       flag("p_scd", p["p_scd"]),
                       on_me({"type": "Shield", "amount": p["p_sh"], "attack_ratio": p["p_sh_r"], "ap_ratio": 0,
                              "tick": p["p_sh_t"]}, *rm("p_sh"), flag("p_sh", p["p_sh_t"]))))))
    if native:
        # the add-on counts on the unit hit and raises p_go (3 ticks) for the third; read it now and a tick later
        def count():
            return combine({"type": "Native", "effect_ref": "league_akshan:hit"},
                           sw("p_go", combine(*rm("p_go"), proc),
                              delayed(1, sw("p_go", combine(*rm("p_go"), proc)))))
    else:
        def count():
            return sw("p_2", combine(*rm("p_1", "p_2"), proc),
                      sw("p_1", combine(*rm("p_2"), flag("p_2", p["p_t"])), combine(*rm("p_1"), flag("p_1", p["p_t"]))))

    # ------------------------------------------------------------------ W Going Rogue: camouflage when outnumbered
    camo = combine(flag("w_cd", p["w_cd"]), on_me({"type": "CasterInvisible", "tick": p["w_inv"]}),
                   *rm("w_ms"), flag("w_ms", p["w_inv"], move_speed_mult=p["w_ms"]), cview("w_camo"), sfx("w_cast"))
    rogue = sw("w_cd", NONE, combine(
        around(p["w_rad"], "EnemyChampion", [sw("w_1", flag("w_2", 2), flag("w_1", 2))]),
        delayed(1, sw("w_2", combine(*rm("w_1", "w_2"), camo), combine(*rm("w_1"))))))

    # ------------------------------------------------------------------ attack: the double shot
    shot1 = homing("a_shot", p["a_speed"], p["a_y"], "Enemy",
                   [attack(0, p["a_ratio"]), view("a_hit"), tsfx("a_hit"), count()])
    rest = p["a_ratio"] - p["a2_ratio"]
    shot2 = homing("a_shot2", p["a_speed"], p["a_y"], "Enemy",
                   [attack(0, p["a2_ratio"]), view("a_hit"), tsfx("a_hit2"), count(),
                    is_champ(flag("a_ch", 2)),
                    delayed(1, sw("a_ch", combine(*rm("a_ch")), attack(0, rest)))])
    root = combine(sfx("a_shot"), delayed(p["a_hit1"], shot1), delayed(p["a_hit2"], sfx("a_shot2"), shot2), rogue)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", root,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Avengerang
    hit_q = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"), count(),
             is_champ(*rm("q_ms"), flag("q_ms", p["q_ms_t"], move_speed_mult=p["q_ms"]))]
    back = line("q_back", p["q_back"], 400000, p["q_w"], "EnemyWithoutTower", hit_q,
                end=[view("q_catch")], back=True)
    out = line("q_out", p["q_speed"], p["q_range"], p["q_w"], "EnemyWithoutTower", hit_q,
               end=[sfx("q_turn"), back])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_cast"], "Direction", "EnemyWithoutTower", combine(
        *rm("q_go"), anim("skill", p["q_dur"]), sfx("q_cast"),
        delayed(2, pick(p["q_lock"], "EnemyChampion", flag("q_go", 10), lob("q_aim", p["q_aim"], [out]))),
        delayed(3, sw("q_go", NONE, out))))

    # ------------------------------------------------------------------ skill2: E Heroic Swing
    def nearest(*effects):
        """The nearest enemy, champions first (league_lucian R's rings)."""
        spec = [(p["e_seek"], "EnemyChampion"), (p["e_seek"], "EnemyWithoutTower")]
        node = None
        for i in range(len(spec) - 1, -1, -1):
            rng, target = spec[i]
            r = pick(rng, target, *([] if node is None else [flag("e_found", 1)]), *effects)
            node = r if node is None else combine(*rm("e_found"), r, sw("e_found", NONE, node))
        return node

    e_hit = [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit"), count()]
    e_fire = nearest(homing("e_shot", p["e_shot"], p["a_y"], "EnemyWithoutTower", e_hit), sfx("e_shot"))
    t_end = p["e_hook"] + p["e_n"] * p["e_every"]
    swing_t = t_end - p["e_hook"]
    # one copy of the step and the shot, run every e_every ticks by a poll on him (league_jhin R's channel)
    step = pick(p["e_step"], "EnemyChampion",
                {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_step"], "end_effects": []})
    swing = on_me({"type": "AddCasted", "casted_type": "Heal", "duration": swing_t, "period": p["e_every"],
                   "effects": [step, e_fire]})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion", combine(
        anim("skill2", p["e_hook"]), cview("e_hook"), sfx("e_cast"),
        delayed(max(1, p["e_hook"] - p["e_every"]), swing),
        delayed(p["e_hook"], anim("e_swing", swing_t), sfx("e_swing")),
        delayed(t_end, anim("e_roll", p["e_back_t"] + 4), {"type": "MoveBack", "speed": p["e_back"],
                                                          "tick": p["e_back_t"]}, e_fire, sfx("e_roll"))))

    # ------------------------------------------------------------------ ult: R Comeuppance
    stored = [f"r_s{i}" for i in range(1, p["r_n"] + 1)]
    hits = [f"r_h{i}" for i in range(1, p["r_n"])]

    def bullet_hit():
        if native:
            dmg = [{"type": "Native", "effect_ref": "league_akshan:bullet"}]
        else:
            # every earlier hit adds r_up%: r_h1..r_h{n-1} walked from the top
            ladder = attack(p["r_dmg"], p["r_ratio"])
            for i in range(1, p["r_n"]):
                k = 100 + p["r_up"] * i
                ladder = sw(f"r_h{i}", attack(p["r_dmg"] * k // 100, p["r_ratio"] * k // 100), ladder)
            # then count this hit on the next free rung
            cnt = flag("r_h1", p["r_ch"] + 120)
            for i in range(2, p["r_n"]):
                cnt = sw(f"r_h{i - 1}", flag(f"r_h{i}", p["r_ch"] + 120), cnt)
            dmg = [ladder, delayed(1, cnt)]
        return dmg + [view("r_hit"), tsfx("r_hit"), count()]

    bullet = line("r_bullet", p["r_speed"], p["r_reach"], p["r_w"], "Enemy", bullet_hit(), penetrate=False)

    def fire_one():
        return pick(p["r_reach"], "EnemyChampionRecentlyAttacked", flag("r_aimed", 1),
                    lob("r_aim", p["r_aim"], [bullet]))

    def fire():
        """One stored bullet: the champion he locked (the recently hurt one in reach), else any champion."""
        return combine(*rm("r_aimed"), fire_one(),
                       sw("r_aimed", NONE, pick(p["r_reach"], "EnemyChampion", lob("r_aim", p["r_aim"], [bullet]))),
                       anim("ult_shot", p["r_gap"] + 2), sfx("r_shot"))

    def store(k):
        return sw("r_chan", sw("r_open", NONE, combine(flag(stored[k], p["r_ch"] + 60), sfx("r_store"))))

    # one poll on him every r_gap ticks for the whole channel: crowd control ends it (league_jhin R); once the firing is
    # open (the channel full, or `r_fire` - the add-on's early release) every poll spends the highest stored bullet
    spend = NONE
    for k in range(p["r_n"]):
        spend = sw(stored[k], combine(*rm(stored[k]), flag("r_go", 1)), spend)
    fire_now = combine(*rm("r_go"), spend, sw("r_go", fire()))
    total = p["r_ch"] + p["r_n"] * p["r_gap"]
    open_ = combine(flag("r_open", total), *unanim("ult_ch"))
    stop = combine(*rm("r_chan", "r_open", "r_fire", *stored, *hits), *unanim("ult", "ult_ch", "ult_shot"))
    poll = on_me({"type": "AddCasted", "casted_type": "Heal", "duration": total + 2, "period": p["r_gap"],
                  "effects": [pick(1, "AllyChampionInCC", stop),
                              sw("r_chan", combine(sw("r_fire", sw("r_open", NONE, open_)), sw("r_open", fire_now)))]})
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked", combine(
        *rm("r_chan", "r_open", "r_fire", *stored, *hits), flag("r_chan", total + 4),
        anim("ult", 8), delayed(8, sw("r_chan", anim("ult_ch", p["r_ch"] - 8))), sfx("r_cast"), cview("r_lock"),
        poll, *[delayed(p["r_store"] * (k + 1) - 1, store(k)) for k in range(p["r_n"])],
        delayed(p["r_ch"] - 1, sw("r_chan", sw("r_open", NONE, open_))), delayed(total + 3, stop)))

    # ------------------------------------------------------------------ views
    # pictures (tools/art/pack_akshan_fx.py): one picture serves several names where League shows the same thing - the
    # attack's two shots and E's shots one bullet, the boomerang going out and coming back one spinning blade, E's hits
    # the attack's
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 1}
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("q_catch"), E("e_hit", tag="a_hit"), E("r_hit"),
               E("e_hook", BIG, 2, **LATE), E("w_camo", BIG, 2, **LATE), E("r_lock", BIG, 2, **LATE)]
    views_p = [Pj("a_shot"), Pj("a_shot2", "a_shot"), Pj("q_out", "q_rang"), Pj("q_back", "q_rang"),
               Pj("e_shot", "a_shot"), Pj("r_bullet")]
    views_b = [{"type": "Animated", "name": n("p_sh"), "anim": FX, "tag": "p_sh", "repeat": True, "z": 2},
               {"type": "Animated", "name": n("w_ms"), "anim": FX, "tag": "w_ms", "repeat": True, "z": -1},
               # the add-on's Scoundrel mark over an enemy champion (league_akshan; never laid by the main pack)
               {"type": "Animated", "name": n("w_mark"), "anim": FX, "tag": "w_mark", "repeat": True, "z": 3}]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_akshan:rogue",
                          "params": {"r_dmg": int(p["r_dmg"]), "r_ratio": int(p["r_ratio"]), "r_max": int(p["r_max"]),
                                     "r_full": int(p["r_full"]), "p_t": int(p["p_t"])}}
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
    kit = build(p, native=a.native)
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
