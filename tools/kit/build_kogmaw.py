"""Build league_kogmaw.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_kogmaw.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-09: ADC, Range, kit A - League's whole kit - and 「加入高手连招」). TFM2 has three
active slots: Caustic Spittle is `skill`, Void Ooze `skill2`, Living Artillery the `ult`; Bio-Arcane Barrage turns
itself on (League's W has no cast time) and Icathian Surprise watches for his death.
  passive Icathian Surprise (艾卡西亚的惊喜): nothing in the data runs on a death, so each life's first action starts a
          watch on him: an `AddCasted` (period p_watch) lobs a hidden lob onto him that flies p_watch ticks; where it
          lands it asks `RandomTarget {range: 1, AllyOnlySelf}` (which finds no dead caster) whether he lives. The
          AddCasted stops with him, so exactly one lob in the air finds him dead: there the void form wakes (his `dead`
          strip: he rises, swells and glows) and p_fuse ticks later it bursts - p_dmg + p_ratio% AD true damage to every
          enemy within p_r. League's form walks at the nearest enemy for 4 s; a dead body cannot walk in data, so it
          bursts where he fell (the burst's ring shows from the start, so enemies can step out).
  attack  A glob of spit (homing, physical 100% AD). Every attack turns Bio-Arcane Barrage on when it is ready.
  W       Bio-Arcane Barrage (生化弹幕, automatic): w_t ticks of +w_range attack range and w_hp% of the target's maximum
          health on every attack (`base_attack_enemy_max_hp_damage`), then w_cd. Its glow is a view buff.
  skill   Q Caustic Spittle (腐蚀唾液): a `Targeting` cast on `EnemyWithoutTower` (q_range); at the release a straight
          shot at where the target stands then (a skillshot: it stops on the first enemy it meets): q_dmg + q_ratio% AD
          and q_shred% less armour and magic resistance for q_shred_t ticks. Passive: q_as% attack speed while he lives.
  skill2  E Void Ooze (虚空淤泥): a `Direction` cast on `EnemyWithoutTower` (e_range); at the release a piercing ooze
          (e_dmg + e_ratio% AD, e_slow% slow) that leaves a trail for e_trail ticks (league_nocturne Q's anchors: hidden
          lines of growing length each start a slowing zone where they stop; the trail's picture is a line on `Ally`).
  ult     R Living Artillery (活体大炮): a `Targeting` cast on `EnemyChampionRecentlyAttacked` (r_range; the ult not
          wasted on a champion at full health). Each cast is one shell: the target's spot is marked at the release and
          r_delay ticks later it bursts (r_r): r_dmg + r_ratio% AD, and on champions League's "more against the
          wounded" as league_pyke R's execute - r_x + r_x_ratio% AD true damage, healed back a tick later on whoever
          lives through it. Volleys: the first shell locks the ult for r_lock ticks and opens r_vol; the slot's own
          cooldown is only r_gap, so the AI fires again while the volley lasts - three shells at most.
  combos  (「加入高手连招」)
          E -> R (减速接大炮): a champion the ooze hits gets a shell e_r_wait ticks later, slowed, when a shell is
                  available (the volley rules above).
          W -> Q (开W接Q破甲): when the barrage turns on with an enemy champion within its reach and Q is ready, the
                  spittle follows the attack at that champion (its armour shred then feeds the barrage).
          R execute (大炮收割): R's execute share (above).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_kogmaw.data_champion")
ID = "league_kogmaw"
FX = "asset/league/effects/league_kogmaw_fx"
BIG = "asset/league/effects/league_kogmaw_big"

P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Kog'Maw: 500
    # range, 61 AD +3.1, 635 +99 hp, 32 armour, 330 move (slow), attack speed 0.665
    "hp": 880, "hp_g": 88, "atk": 90, "atk_g": 18, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 870, "ms_g": 9,
    # attack: the glob leaves the mouth on a_st (retimed to the strips later)
    "atk_range": 50000, "atk_dur": 24, "atk_cd": 54, "a_st": 8, "glob_speed": 6500, "glob_y": 0,
    # passive: Icathian Surprise (League: 4 s, 125 + 25 a level true damage, radius ~?)
    "p_watch": 6, "p_life": 216000, "p_seek": 70000, "p_speed": 1800, "p_r": 12000, "p_dmg": 80, "p_ratio": 100,
    # W Bio-Arcane Barrage (League: 8 s, +130-210 range, 3-7% max health on-hit, cd 17 s)
    "w_t": 480, "w_cd": 1020, "w_range": 18000, "w_hp": 4,
    # skill: Q Caustic Spittle (League: 1200 range, 90-290 + 70% AP magic, shred 16-24% 4 s, cd 8 s; passive
    # +15-35% attack speed)
    "q_cd": 480, "q_range": 95000, "q_dur": 24, "q_rel": 9, "q_speed": 5000, "q_len": 105000, "q_rad": 5000,
    "q_y": 0, "q_dmg": 60, "q_ratio": 70, "q_shred": 20, "q_shred_t": 240, "q_as": 15,
    # skill2: E Void Ooze (League: 1360 range, 75-255 + 50% AP magic, slow 20-40% decaying, trail 4 s, cd 12 s)
    "e_cd": 720, "e_range": 100000, "e_dur": 30, "e_rel": 12, "e_speed": 4000, "e_len": 110000, "e_rad": 7000,
    "e_y": 0, "e_dmg": 50, "e_ratio": 60, "e_slow": 35, "e_slow_t": 60, "e_trail": 240, "e_zone_r": 9000,
    "e_step": 20000,
    # ult: R Living Artillery (League: 1300-1800 range, 1.1 s delay, radius 240, 100-180 + 65% bonus AD + 35% AP,
    # x2 below 40% health, cd 2-1.5 s with a growing mana cost)
    "r_lock": 1200, "r_gap": 50, "r_win": 360, "r_range": 130000, "r_dur": 24, "r_rel": 10, "r_delay": 40,
    "r_r": 15000, "r_dmg": 70, "r_ratio": 65, "r_x": 50, "r_x_ratio": 35,
    # combos
    "e_r_wait": 10,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def true_dmg(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal_any(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Any"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


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


def lob(name, travel, target, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def band(name, length, width, tick):
    """A picture-only rectangle on `Ally` (the enemy AI does not dodge it)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": tick,
            "apply": tick, "applied_target": "Ally", "applied_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Icathian Surprise
    # the void form: a visible homing form at a champion near the body, and a hidden splash beside it at the same
    # speed for the burst (league_jinx's rocket: a projectile cannot start a zone from its hit)
    burst = [true_dmg(p["p_dmg"], p["p_ratio"]), view("p_hit"), tsfx("p_hit")]
    splash = {"type": "TargetSplashProjectile", "name": n("p_burst"), "speed": p["p_speed"], "range": p["p_r"],
              "y_offset": 5000, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in burst]}
    wake = combine(view("p_wake"), sfx("p_wake"),
                   pick(p["p_seek"], "EnemyChampion",
                        homing("p_form", p["p_speed"], 5000, "EnemyChampion", [view("p_boom"), tsfx("p_boom")]),
                        splash, fp=True))
    check = combine(pick(1, "AllyOnlySelf", flag("p_live", 1)), sw("p_live", combine(*rm("p_live")), wake))
    watch = casted(p["p_life"], p["p_watch"], lob("p_watch", p["p_watch"] + 1, "AllyOnlySelf", [check]))
    # each life's first action: the watch and Caustic Spittle's passive attack speed (death clears both)
    life = sw("init", NONE, combine(flag("init", None), flag("q_pas", None, attack_speed_mult=p["q_as"]),
                                    on_me(watch)))

    # ------------------------------------------------------------------ Q Caustic Spittle
    spit_hit = [attack(p["q_dmg"], p["q_ratio"]),
                buff("q_shred", p["q_shred_t"], defence_mult=-p["q_shred"], magic_resistance_mult=-p["q_shred"]),
                view("q_hit"), tsfx("q_hit")]

    def q_fire():
        return combine(refresh("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q_cast"), voice("vo_q", p),
                       delayed(p["q_rel"], sfx("q_shot"),
                               line("q_spit", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower",
                                    False, spit_hit)))

    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(life, sw("q_cd", NONE, q_fire())))

    # ------------------------------------------------------------------ W Bio-Arcane Barrage (automatic)
    def w_on(combo):
        out = [refresh("w_cd", p["w_cd"]),
               refresh("w_on", p["w_t"], range=p["w_range"], base_attack_enemy_max_hp_damage=p["w_hp"]),
               cview("w_cast"), sfx("w_cast"), voice("vo_w", p)]
        if combo:   # W -> Q: the spittle follows this attack at a champion within the barrage's reach
            out.append(sw("q_cd", NONE, delayed(p["atk_dur"], pick(p["atk_range"] + p["w_range"], "EnemyChampion",
                                                                     q_fire()))))
        return combine(*out)

    # ------------------------------------------------------------------ R Living Artillery: one shell a cast
    execute = [true_dmg(p["r_x"], p["r_x_ratio"]), delayed(1, heal_any(p["r_x"], p["r_x_ratio"]))]

    def shell(travel=1):
        """A lob onto the target's spot; the mark there, the burst r_delay ticks later."""
        return lob("r_lob", travel, "EnemyWithoutTower", [
            view("r_mark"), sfx("r_land"),
            zone("r_blast", p["r_r"], p["r_delay"], p["r_delay"], "EnemyWithoutTower",
                 [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]),
            zone("r_exec", p["r_r"], p["r_delay"], p["r_delay"], "EnemyChampion", execute),
            delayed(p["r_delay"] - 8, view("r_fall"), sfx("r_fall"))])

    def volley(fire):
        """Shell 1 locks the ult and opens the volley, shell 2 counts, shell 3 ends it; outside a volley while the
        lock lasts nothing (the empty branch keeps the AI from casting)."""
        first = combine(refresh("r_lock", p["r_lock"]), refresh("r_vol", p["r_win"]), fire)
        inside = sw("r_c1", combine(*rm("r_c1", "r_vol"), fire), combine(refresh("r_c1", p["r_win"]), fire))
        return sw("r_lock", sw("r_vol", inside), combine(*rm("r_c1"), first))

    r_cast = combine(anim("ult", p["r_dur"]), sfx("r_cast"), voice("vo_r", p),
                     delayed(p["r_rel"], sfx("r_shot"), shell()))
    ult = action("ult", p["r_dur"], p["r_gap"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(life, volley(r_cast)))

    # ------------------------------------------------------------------ E Void Ooze
    slow = buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"])
    anchors = [line("e_anchor", p["e_speed"], d, 1000, 0, "Ally", False, [],
                    end=[field("e_zone", p["e_zone_r"], p["e_trail"], 15, "EnemyWithoutTower",
                               [buff("e_slow", 16, move_speed_mult=-p["e_slow"])])])
               for d in range(p["e_step"] // 2, p["e_len"] + 1, p["e_step"])]
    # E -> R: a champion the ooze hits gets a shell when one is available (the volley rules)
    e_r = delayed(p["e_r_wait"], volley(combine(sfx("r_shot"), shell())))
    e_fire = combine(anim("skill2", p["e_dur"]), sfx("e_cast"), voice("vo_e", p),
                     delayed(p["e_rel"], sfx("e_shot"), band("e_trail", p["e_len"], p["e_zone_r"] * 2, p["e_trail"]),
                             line("e_ooze", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyWithoutTower", True,
                                  [attack(p["e_dmg"], p["e_ratio"]), slow, view("e_hit"), tsfx("e_hit")]),
                             line("e_twin", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyChampion", True,
                                  [e_r]),
                             *anchors))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Direction", "EnemyWithoutTower",
                    combine(life, e_fire))

    # ------------------------------------------------------------------ attack: the glob (+ W turning on)
    glob = combine(sfx("a_shot"), homing("a_glob", p["glob_speed"], p["glob_y"], "Enemy",
                                         [attack(0, 100), view("a_hit"), tsfx("a_hit")]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, sw("w_cd", NONE, w_on(True)), delayed(p["a_st"], glob)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # pictures with an up and down on a cast point are ViewEffects (never turned); the trail is a line drawn along
    # its own direction and symmetric top to bottom
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_glob"), P_("q_spit"), P_("e_ooze"), P_("e_trail", BIG, -1), P_("p_form", BIG, 2)]
    views_e = [E("a_hit"), E("q_hit"), E("e_hit"), E("w_cast", FX, 3), E("r_mark", BIG, -1, False),
               E("r_fall", BIG, 2, False), E("r_hit"), E("p_wake", BIG, 2, False), E("p_boom", BIG, 2),
               E("p_hit")]
    views_b = [B_("w_on", FX, 2), B_("q_shred", FX, 3), B_("e_slow", FX, -1)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Dot"],
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
