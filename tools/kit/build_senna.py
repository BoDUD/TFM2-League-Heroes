"""Build league_senna.data_champion (support, Range) from the parameters P.

    python tools/kit/build_senna.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-10: support, Range, League's whole kit with the pros' play). TFM2 has three active
slots: Piercing Darkness is `skill`, Last Embrace `skill2`, Dawning Shadow the `ult`; Curse of the Black Mist runs on
its own (League's E is her escape, pressed when a diver reaches her).
  passive Absolution (赦除): her attacks and spells mark an enemy champion (p_mark ticks); her next attack on a champion
          while the mark holds takes its Mist: p_hp% of the target's maximum health as bonus physical damage and one
          Mist (League: current health, which nothing reads), and no new mark for p_lock ticks. Every p_wave ticks one
          of her attacks also draws in a wraith of the Black Mist (League: units that die near her leave one), and a
          champion her attack kills leaves one. Each Mist is one `Permanent` caster buff `mist`: +p_atk attack and
          +p_rng range, every second one +1% critical chance too (League: 0.75 AD each, every 20 +20 range and 10%
          crit). Death clears a mod's buffs (champion-data section 5), so the Mist starts again each life in this pack;
          the optional add-on addons/league_senna_mist gives it back after she respawns (League's Mist is kept).
          Relic Cannon: every attack gives her p_ms% move speed for p_ms_t ticks.
  attack  A shot from the relic cannon (homing, 100% AD), slow and heavy (League: 0.625 attacks a second); its sound is
          league_senna_attack, which the engine plays by itself on every attack.
  skill   Q Piercing Darkness (黑暗洞灭): a `Targeting` cast on `EnemyWithoutTower`: a beam from the cannon through the
          target to q_len: q_dmg + q_ratio% AD and a q_slow% slow (q_slow_t) to every enemy on it, q_heal +
          q_hratio% AD healed to every allied champion on it (she stands behind her team, so the beam crosses them).
          League's attacks take 1 s off its cooldown; nothing can subtract from a cooldown, so q_cd is the cooldown
          she gets with that refund in a fight.
  skill2  W Last Embrace (无尽厮守): a `Direction` cast on `EnemyWithoutTower`, aimed at an enemy champion in reach
          when one is (league_morgana Q's aim): the Black Mist flies to the first enemy (w_speed, dodgeable), deals
          w_dmg + w_ratio% AD and clings to it; w_wait ticks later it spreads: every enemy within w_r of it is rooted
          for w_root ticks.
  E       Curse of the Black Mist (黑雾咒附, automatic): an enemy champion within e_near of her with e_cd off ->
          the mist: she and every allied champion within e_r turn invisible (camouflage: enemies right beside them
          still see them) and get e_ms% move speed for e_t ticks.
  ult     R Dawning Shadow (暗影燎原): a `Direction` cast on `EnemyChampionRecentlyAttacked` from as far as r_range;
          r_rel ticks of charging, then the light rolls down the line: the dark core (r_rad) deals r_dmg + r_ratio% AD
          to every enemy champion, the wide light (r_wide) shields her and every allied champion r_sh + r_sratio% AD
          for r_sh_t ticks. It is aimed when it leaves, at where a fighting champion stands then (League's beam crosses
          the map in a blink after a 1 s cast; aimed at the cast, c1's 3 beams a game struck no champion: the target
          had walked off), else down the cast's line; it still flies some ticks, so a champion far off can step aside.
  combos  (「加入高手连招」)
          A-Q-A (普攻穿插 Q 收魂): Q's beam marks the champion, so the next attack takes its Mist at once.
          W -> R (定身接大招): when R fires, a champion in crowd control anywhere in reach (her W's root, an ally's
                  stun) gets the light first - it cannot step out.
          E -> 先手 (雾中突进): the mist hastes her side while they walk in hidden.
--native: the copy for the add-on (addons/league_senna_mist/make_override.py): `passive` = league_senna_mist:keep (it
copies the Mist layers it saw, so it needs no numbers); the kit is otherwise the same.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_senna.data_champion")
ID = "league_senna"
FX = "asset/league/effects/league_senna_fx"
BIG = "asset/league/effects/league_senna_big"

# Numbers = candidate c3d of the 10-min classic-SDK simulations (se_sim/sim/kd.py --lane 4 against priest, bard,
# enchanter, monk and taoist, three lineups, both sides, 2026-10-10): +0.65 on seeds 1-12, +0.95 on 25-36. The draft c0
# was +0.53 / +0.81 with R aimed at the cast (it struck nobody) and E almost never on; aimed when it leaves and E at
# 45000 (c2) it went to +1.67 / +2.94. R 200 + 100% -> 150 + 75% alone +1.33, E 6 s -> 4 s alone +1.59, attack 80 ->
# 75 alone +1.31 / +2.23; all three (c3d) kept. league_karma in the same batches: -0.29 / -0.51.
# League's Senna: 530 + 89 hp, 50 AD (+0, the Mist is her growth), 600 range, 0.625 attacks a second (windup 31%),
# 25 + 4 armour, 330 move.
P = {
    "hp": 880, "hp_g": 86, "atk": 75, "atk_g": 9, "def": 20, "def_g": 6, "mr": 22, "mr_g": 3, "ms": 950, "ms_g": 9,
    # attack: the shot leaves the cannon on a_st; a_y: the shots (and W) fly 4 px over the pivot, at the 85% sprite's
    # muzzles (attack 2 px, W 5 px up)
    "atk_range": 62000, "atk_dur": 34, "atk_cd": 96, "a_st": 18, "a_speed": 7000, "a_y": 1000,
    # passive Absolution (League: mark 4 s, 1-10% current hp, 0.75 AD a Mist, +20 range and 10% crit every 20)
    "p_mark": 240, "p_lock": 180, "p_hp": 3, "p_wave": 360, "p_atk": 1, "p_rng": 100, "p_ms": 15, "p_ms_t": 30,
    # Q Piercing Darkness (League: 1300 long, 100-280 wide, 30-130 + 60% bonus AD, heal 40-120 + 40% bonus AD,
    # 15% slow 1-2 s, cd 15 s minus 1 s an attack)
    "q_cd": 540, "q_range": 62000, "q_dur": 30, "q_st": 18, "q_len": 130000, "q_w": 6000, "q_dmg": 60, "q_ratio": 50,
    "q_heal": 70, "q_hratio": 35, "q_slow": 20, "q_slow_t": 75,
    # W Last Embrace (League: 1300 range at 1200/s, 70-230 + 90% bonus AD, 1 s on the target, radius 280, root
    # 1.25-2.25 s, cd 11 s)
    "w_cd": 660, "w_range": 90000, "w_dur": 24, "w_st": 12, "w_aim": 85000, "w_speed": 4500, "w_len": 110000,
    "w_rad": 5000, "w_dmg": 70, "w_ratio": 60, "w_wait": 60, "w_r": 28000, "w_root": 90,
    # E Curse of the Black Mist (League: 6-8 s, radius 400, +20% move speed, cd 26-20 s)
    "e_cd": 1320, "e_near": 45000, "e_r": 40000, "e_t": 240, "e_ms": 20,
    # R Dawning Shadow (League: global, 1 s cast, core 320 wide 250-550 + 115% bonus AD, light 2400 wide, shield
    # 120-200 + 150% Mist 3 s, cd 140-100 s); r_len: the longest line the map's clamp leaves straight
    "r_cd": 3000, "r_range": 250000, "r_dur": 60, "r_rel": 45, "r_speed": 30000, "r_len": 260000, "r_rad": 7500,
    "r_wide": 100000, "r_dmg": 150, "r_ratio": 75, "r_sh": 120, "r_sratio": 40, "r_sh_t": 180,
    # her spoken lines, at most one every vo_gap ticks
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


def flat(node):
    """The tree with every Combine that sits straight in a Combine's, a Delayed's or a RandomTarget's `effects`
    spliced into that list (the same effects in the same order, fewer nodes for the game's per-tick copy)."""
    if isinstance(node, list):
        return [flat(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: flat(v) for k, v in node.items()}
    if out.get("type") in ("Combine", "Delayed", "RandomTarget"):
        eff = []
        for x in out["effects"]:
            if isinstance(x, dict) and x.get("type") == "Combine":
                eff.extend(x["effects"])
            else:
                eff.append(x)
        out["effects"] = eff
    return out


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
    d = tick if isinstance(tick, str) else {"Time": {"tick": tick}}
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": d, **fields}}


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def heal_ally(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Ally"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Bleed"):
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


def beam(name, width, length, delay, apply_, target, effects):
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply_, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, end, target="EnemyWithoutTower", travel=1):
    """A hidden lob onto the unit in hand: `end` runs on its landing spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": flat(effect)}


def kill_check(src, reward):
    """On a hit champion, around its damage: the flag before, the living target's clear after, the read on her later
    (league_jinx Get Excited!; a dead target's `Delayed` adds nothing, so the flag stays)."""
    k = f"k_{src}"
    return (combine(*rm(k), flag(k, 40)),
            combine(casted(3, 1, *rm(k)), on_me(delayed(4, sw(k, combine(*rm(k), reward))))))


def mist_buff(p, crit):
    fields = {"attack": p["p_atk"], "range": p["p_rng"]}
    if crit:
        fields["crit_chance"] = 1
    return flag("mist", None, **fields)


def build(p, native=False):
    # ------------------------------------------------------------------ passive: Absolution
    def gain():
        """One Mist: a `Permanent` instance of `mist` (instances add up); every second one carries 1% crit."""
        return combine(sw("m_odd", combine(*rm("m_odd"), mist_buff(p, True)),
                          combine(flag("m_odd", None), mist_buff(p, False))),
                       cview("p_gain"), sfx("p_gain"))

    def mark():
        """A spell or an attack on an enemy champion: the mark, unless one was just taken."""
        return sw("p_lock", NONE, refresh("p_mark", p["p_mark"]))

    take = combine(*rm("p_mark"), refresh("p_lock", p["p_lock"]), attack(0, 0, p["p_hp"]), view("p_take"),
                   tsfx("p_take"), gain())
    k_set, k_read = kill_check("a", gain())

    # ------------------------------------------------------------------ E Curse of the Black Mist (automatic)
    hide = [{"type": "Invisible", "tick": p["e_t"]}, buff("e_ms", p["e_t"], move_speed_mult=p["e_ms"])]
    curse = combine(refresh("e_cd", p["e_cd"]), cview("e_mist"), sfx("e"), voice("vo_e", p),
                    around(p["e_r"], "AllyChampion", hide))
    e_check = sw("e_cd", NONE, combine(around(p["e_near"], "EnemyChampion", [flag("e_dive", 1)]),
                                       sw("e_dive", combine(*rm("e_dive"), curse))))

    # ------------------------------------------------------------------ attack: the relic cannon
    a_hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    twin = homing("a_twin", p["a_speed"], p["a_y"], "EnemyChampion", [k_set, sw("p_mark", take, mark()), k_read])
    wave = sw("p_wcd", NONE, combine(flag("p_wcd", p["p_wave"]), gain()))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy", combine(
        homing("a_shot", p["a_speed"], p["a_y"], "Enemy", a_hit), twin, wave,
        refresh("a_ms", p["p_ms_t"], move_speed_mult=p["p_ms"]), e_check), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Piercing Darkness
    q_hit = [attack(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
             view("q_hit"), tsfx("q_hit")]
    q_heal = [heal_ally(p["q_heal"], p["q_hratio"]), view("q_heal"), tsfx("q_heal")]
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower", combine(
        sfx("q"), voice("vo_q", p),
        # the beam hits on its 2nd tick and stays 18 (300 ms) for its picture (import_senna.py: line, beam, fading)
        beam("q_beam", p["q_w"], p["q_len"], 18, 2, "EnemyWithoutTower", q_hit),
        beam("q_mark", p["q_w"], p["q_len"], 2, 2, "EnemyChampion", [mark()]),
        beam("q_light", p["q_w"], p["q_len"], 2, 2, "AllyChampion", q_heal)))

    # ------------------------------------------------------------------ skill2: W Last Embrace
    spread = lob("w_spread", [view("w_burst"), sfx("w_root"), zone("w_zone", p["w_r"], 2, 1, "EnemyWithoutTower", [
        {"type": "Bind", "duration": p["w_root"]}, buff("w_root", p["w_root"]), tsfx("w_hit")])])
    w_hit = [attack(p["w_dmg"], p["w_ratio"]), buff("w_cling", p["w_wait"]), view("w_hit"), tsfx("w_hit"),
             pick(1, "EnemyChampion", mark(), fp=True), delayed(p["w_wait"], spread)]

    def shot():
        return line("w_mist", p["w_speed"], p["w_len"], p["w_rad"], p["a_y"], "EnemyWithoutTower", False, w_hit)

    skill2 = action("skill2", p["w_dur"], p["w_cd"], p["w_st"], p["w_range"], "Direction", "EnemyWithoutTower", combine(
        sfx("w"), voice("vo_w", p),
        pick(p["w_aim"], "EnemyChampion", flag("w_aim", 1), shot()),
        sw("w_aim", combine(*rm("w_aim")), shot())))

    # ------------------------------------------------------------------ ult: R Dawning Shadow
    r_hit = [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"), mark()]
    r_guard = [shield(p["r_sh"], p["r_sratio"], p["r_sh_t"]), buff("r_shield", "WithShield"), view("r_sh"), tsfx("r_sh")]

    def light():
        return combine(line("r_core", p["r_speed"], p["r_len"], p["r_rad"], 0, "EnemyChampion", True, r_hit),
                       line("r_light", p["r_speed"], p["r_len"], p["r_wide"], 0, "AllyChampion", True, r_guard))

    # the charge plays from the cast; the light leaves r_rel ticks in (a short `Delayed` chain, left unguarded like
    # the other ones under 1.7 s: champion-data section 5)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Direction", "EnemyChampionRecentlyAttacked",
                 combine(sfx("r_cast"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, sfx("r_fire"),
                                 pick(p["r_range"], "EnemyChampionInCC", flag("r_aim", 1), light()),
                                 sw("r_aim", combine(*rm("r_aim")), combine(
                                     pick(p["r_range"], "EnemyChampionRecentlyAttacked", flag("r_aim2", 1), light()),
                                     sw("r_aim2", combine(*rm("r_aim2")), light()))))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_shot"), P_("q_beam", BIG, 2), P_("w_mist"), P_("r_core", BIG, 2), P_("r_light", BIG, 1)]
    views_e = [E("a_hit"), E("p_take"), E("p_gain", FX, 3), E("q_hit"), E("q_heal"), E("w_hit"),
               E("w_burst", BIG, 2, False), E("e_mist", BIG, -1, False), E("r_hit"), E("r_sh")]
    views_b = [P_("q_slow", FX, -1), P_("w_cling", FX, 2), P_("w_root", FX, -1), P_("e_ms", FX, -1),
               P_("r_shield", FX, 2), P_("p_mark", FX, 3)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Heal", "Shield", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit = {**{k: kit[k] for k in ("id", "category", "tags", "sprite", "anim_prefix", "skill_icons", "stat",
                                       "growth")},
               "passive": {"passive_ref": "league_senna_mist:keep", "params": {}},
               **{k: kit[k] for k in ("attack", "skill", "skill2", "ult", "view_projectiles", "view_effects",
                                      "view_buffs")}}
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
    ap_.add_argument("--native", action="store_true")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, a.native)
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
