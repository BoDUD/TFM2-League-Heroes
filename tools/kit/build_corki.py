"""Build league_corki.data_champion (mid, ranged hybrid) from the parameters P.

    python tools/kit/build_corki.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-12, all the recommended options: mid / ranged hybrid; Q as skill, E with W folded in
as skill2, R with its ammunition as the ult, the passive and the Package in the main pack, the pros' combos, a native
add-on for the missiles' aim and Valkyrie's way out):
  passive Hextech Munitions (海克斯科技军备): p_true% of every attack's damage is true damage (League's 20%).
          Special Delivery (特别快递): the Package is his while the caster flag pk_cd is missing - at the start, after
          each respawn (the respawned unit carries no buffs) and pk_cd ticks after the last one (League: 45 s at the
          fountain). The next Valkyrie is the Package (below).
  attack  A shot (`TargetProjectile`, a_speed) on the a_st tick: (100 - p_true)% AD physical + p_true% AD true.
  skill   Q Phosphorus Bomb (磷光炸弹): a `Position` cast on `EnemyWithoutTower` (q_range): the bomb is lobbed (q_fly
          ticks) to where the unit stood and bursts: every enemy within q_r takes q_dmg + q_ap% AP magic and q_ad% AD
          physical; an enemy champion hit opens q_mark (q_mark ticks) for the combo.
  skill2  E Gatling Gun (格林机枪) with W Valkyrie (瓦尔基里俯冲) folded in on its own cooldown: a `Targeting` cast on
          `EnemyWithoutTower` (e_range) whose own cooldown s2_cd is short; the caster flags e_cd / w_cd are the real
          cooldowns (league_irelia's E/W). E: a short spin-up pose, then for e_t ticks an `AddCasted` on him sprays
          every e_per ticks a cone (`DirDot`, e_cone / e_cos, `Forward`) at an enemy champion within e_reach, else at
          any enemy unit there (League sprays where he faces, mostly his target): e_dmg + e_ad% AD physical and e_ap%
          AP magic, and a shred buff (defence and magic resistance -e_shred, e_shred_t ticks): hits every e_per ticks
          stack it to e_shred_t / e_per at most (League's 4). He moves and attacks meanwhile.
          E cooling down and an enemy champion within w_trig: W, a back-dash away from that champion (`MoveBack`,
          w_speed x w_tick) leaving fire: every w_gap ticks an anchor where he is (league_ekko's 1-tick line) lays a
          fire zone (w_fire_r, w_fire_t ticks, every w_per: w_dmg + w_ap% AP magic) under an upright flame picture.
          With the Package (pk_cd missing): the blast at take-off knocks the champions within pk_kb_r away
          (`Knockback` pk_kb x pk_kb_t) and burns pk_dmg + pk_ap% AP, the dash is pk_tick ticks at pk_speed, the fire
          zones are wider (pk_fire_r) and last pk_fire_t, and he flies off pk_ms% faster for pk_ms_t ticks; pk_cd
          starts. With native=1 (the copy for addons/league_corki) league_corki:escape picks the way out.
  ult     R Missile Barrage (火箭轰击): a `Targeting` cast on `EnemyChampion` (r_range) with r_n charges
          (`cooltime_use_count`; one comes back every r_cd / r_n ticks, League's ammunition): a missile
          (`LinearProjectile`, r_speed) stopping on the first enemy, bursting there: every enemy within r_r takes
          r_dmg + r_ap% AP magic and r_ad% AD physical. Every third missile is the Big One (a counter r_c1 -> r_c2):
          r_big_r radius, r_big% damage. With native=1 league_corki:aim aims every missile.
  combos  Q hit a champion (q_mark) -> the missiles go at a champion his team just struck
          (`EnemyChampionRecentlyAttacked`) - the bombed one, as League's players follow the bomb; the Big One always
          looks for one first (the shredded target of the gatling is one too). W escape -> the AI fires the next
          missile as soon as a champion is within r_range after the landing (no data forces a cast).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_corki.data_champion")
ID = "league_corki"
FX = "asset/league/effects/league_corki_fx"
BIG = "asset/league/effects/league_corki_big"

# Timings from the dense frames (tools/art/rig_corki_hd.py): the shot on tick 8 of 24, the bomb leaves on tick 6 of 22 (the
# lift's peak), the gatling spins up from tick 6, the missile on tick 6 of 16; the bullets and missiles leave the gun's
# mouth 1 game px under the pivot (y_offset 6000: a projectile starts 5000 - y_offset over the caster's pivot).
# Numbers: d4 of the balance runs (Temp/cr_sim, kd.py 600 24 --lane 2, seeds 1-24 and 25-48): +1.18 / +2.08 against
# league_xerath +1.51 / +1.04, league_viktor +1.27 / +1.68, league_syndra +1.62 / +1.53 (d0 was -0.43).
P = {
    # stats (between Range 100/900 hp and Magician 80 + 40 AP): League's Corki 610 +100 hp, 52 AD, 550 range,
    # AS 0.644, Marksman/Mage
    "hp": 900, "hp_g": 92, "atk": 88, "atk_g": 15, "mp": 25, "mp_g": 10, "def": 20, "def_g": 7, "mr": 18, "mr_g": 4,
    "ms": 920, "ms_g": 10,
    # attack: a shot from the gun under the nose
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 62, "a_st": 8, "a_speed": 6000, "a_y": 6000,
    # passive Hextech Munitions (League: 20% of the attack as true damage); Special Delivery every 45 s
    "p_true": 20, "pk_cd": 2700,
    # Q Phosphorus Bomb (League: 825 range, radius 250, 75-275 + 70% bonus AD + 50% AP?, cd 9-7 s)
    "q_cd": 450, "q_range": 58000, "q_dur": 22, "q_at": 6, "q_fly": 18, "q_r": 17000,
    "q_dmg": 95, "q_ap": 70, "q_ad": 55, "q_mark": 150,
    # E Gatling Gun (League: cone 725 / 28 deg, 4 s, 4 shots a second, shred -10..-22 armour and MR at 4 stacks, cd 12 s)
    "s2_cd": 120, "s2_dur": 2, "e_cd": 720, "e_range": 45000, "e_dur": 18, "e_at": 6, "e_t": 240, "e_per": 15,
    "e_reach": 50000, "e_cone": 48000, "e_cos": 850, "e_off": 1000,
    "e_dmg": 9, "e_ad": 16, "e_ap": 9, "e_shred": 3, "e_shred_t": 60,
    # W Valkyrie (League: dash 600 at 650+, fire 2.5 s, 2 hits a second, 60-210 + 100% AP over it, cd 20-12 s)
    "w_trig": 30000, "w_cd": 1080, "w_dur": 24, "w_at": 4, "w_speed": 4500, "w_tick": 9, "w_gap": 3,
    "w_fire_r": 9000, "w_fire_t": 150, "w_per": 30, "w_dmg": 15, "w_ap": 12,
    # the Package (League: 1800 range, knock-back at take-off, wider fire 5 s, +40% move speed)
    "pk_tick": 13, "pk_speed": 5000, "pk_kb_r": 20000, "pk_kb": 2500, "pk_kb_t": 8, "pk_dmg": 40, "pk_ap": 30,
    "pk_fire_r": 13000, "pk_fire_t": 240, "pk_ms": 30, "pk_ms_t": 180,
    # R Missile Barrage (League: 1300 range, radius 200, 80-230 + 15-120% AD + 12% AP, every 3rd x2 r 300; ammo 4,
    # 12-8 s each)
    "r_cd": 2400, "r_n": 4, "r_range": 84000, "r_dur": 16, "r_at": 6, "r_speed": 6000, "r_y": 6000, "r_w": 3000,
    "r_dmg": 75, "r_ap": 42, "r_ad": 52, "r_r": 13000, "r_big_r": 20000, "r_big": 200,

    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_corki: the missiles aim and Valkyrie escapes where league_corki:* says
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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def true_ad(ratio):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


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


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, fly, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": fly, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, apply, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": apply, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def anchor(name, *end):
    """A 1-tick line where he stands: its end_effects run on that spot (league_ekko R's anchor)."""
    return line(name, 1, 1, 1000, 5000, "Ally", True, [], end)


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None, uses=None):
    a = {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
         "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
         "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}
    if uses:
        a["cooltime_use_count"] = uses
    return a


def build(p):
    native = bool(p["native"])
    # ------------------------------------------------------------------ attack (Hextech Munitions)
    shot = {"type": "TargetProjectile", "name": n("a_bolt"), "speed": p["a_speed"], "y_offset": p["a_y"],
            "applied_target": "Enemy",
            "applied_effects": [T(e) for e in (attack(0, 100 - p["p_true"]), true_ad(p["p_true"]), view("a_hit"),
                                               tsfx("a_hit"))]}
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_fire"), shot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Phosphorus Bomb
    blast = [magic(p["q_dmg"], p["q_ap"]), attack(0, p["q_ad"]), view("q_hit")]
    bomb = lob("q_bomb", p["q_fly"], "EnemyWithoutTower",
               [view("q_boom"), sfx("q_boom"), zone("q_blast", p["q_r"], 1, "EnemyWithoutTower", blast),
                zone("q_champ", p["q_r"], 1, "EnemyChampion", [on_me(refresh("q_mark", p["q_mark"]))])])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(voice("vo_q", p), delayed(p["q_at"], sfx("q"), bomb)))

    # ------------------------------------------------------------------ skill2: E Gatling Gun / W Valkyrie
    shred = buff("e_shred", p["e_shred_t"], defence=-p["e_shred"], magic_resistance=-p["e_shred"])
    spray_hits = [attack(p["e_dmg"], p["e_ad"]), magic(0, p["e_ap"]), shred, view("e_hit")]
    spray = {"type": "RangeEffect", "shape": {"DirDot": {"radius": p["e_cone"], "range": p["e_cos"]}},
             "target": "EnemyWithoutTower", "apply_type": {"Forward": {"offset": p["e_off"]}}, "effects": spray_hits}
    pulse = combine(pick(p["e_reach"], "EnemyChampion", on_me(flag("e_aim", 1)), spray),
                    sw("e_aim", combine(*rm("e_aim")), pick(p["e_reach"], "EnemyWithoutTower", spray)))

    def e_fire():
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), voice("vo_e", p),
                       delayed(p["e_at"], sfx("e"), on_me(refresh("e_on", p["e_t"]),
                                                          casted(p["e_t"], p["e_per"], pulse))))

    def fire_trail(ticks, radius, life):
        burn = [magic(p["w_dmg"], p["w_ap"]), view("w_burn")]
        spot = anchor("w_anchor", view("w_fire_big" if radius > p["w_fire_r"] else "w_fire"),
                      field("w_field", radius, life, p["w_per"], "EnemyWithoutTower", burn))
        return [delayed(k, spot) for k in range(1, ticks + 1, p["w_gap"])]

    def valkyrie():
        dash = {"type": "MoveBack", "speed": p["w_speed"], "tick": p["w_tick"]}
        go = [dash] if not native else [{"type": "Native", "effect_ref": "league_corki:escape"}]
        return combine(anim("skill2_w", p["w_dur"]), sfx("w"),
                       delayed(p["w_at"], *go, on_me(*fire_trail(p["w_tick"], p["w_fire_r"], p["w_fire_t"])),
                               delayed(p["w_tick"], sfx("w_boom"))))

    def package():
        dash = {"type": "MoveBack", "speed": p["pk_speed"], "tick": p["pk_tick"]}
        go = [dash] if not native else [{"type": "Native", "effect_ref": "league_corki:package"}]
        kb = around(p["pk_kb_r"], "EnemyChampion", [magic(p["pk_dmg"], p["pk_ap"]),
                                                     {"type": "Knockback", "speed": p["pk_kb"], "tick": p["pk_kb_t"]},
                                                     view("pk_hit"), tsfx("w_pkg_hit")])
        return combine(refresh("pk_cd", p["pk_cd"]), anim("skill2_w", p["w_dur"]), sfx("w_pkg"), voice("vo_w", p),
                       cview("pk_blast"), kb,
                       delayed(p["w_at"], *go, on_me(refresh("pk_ms", p["pk_ms_t"], move_speed_mult=p["pk_ms"]),
                                                     *fire_trail(p["pk_tick"], p["pk_fire_r"], p["pk_fire_t"])),
                               delayed(p["pk_tick"], sfx("w_boom"))))

    def w_fire():
        return combine(refresh("w_cd", p["w_cd"]), sw("pk_cd", valkyrie(), package()))

    w_try = sw("w_cd", NONE, pick(p["w_trig"], "EnemyChampion", w_fire()))
    skill2 = action("skill2", p["s2_dur"], p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    sw("e_cd", w_try, e_fire()))

    # ------------------------------------------------------------------ ult: R Missile Barrage
    def missile(big):
        k = "r_big" if big else "r"
        r = p["r_big_r"] if big else p["r_r"]
        mult = p["r_big"] if big else 100
        hits = [magic(p["r_dmg"] * mult // 100, p["r_ap"] * mult // 100), attack(0, p["r_ad"] * mult // 100),
                view("r_hit")]
        end = [view(k + "_boom"), sfx(k + "_boom"), zone(k + "_blast", r, 1, "EnemyWithoutTower", hits)]
        return combine(sfx(k), line(k + "_missile", p["r_speed"], p["r_range"] + 10000, p["r_w"], p["r_y"],
                                    "EnemyWithoutTower", False, [], end))

    def aimed(big, focus):
        """At a champion his team just struck when there is one (the combo), else at the cast target."""
        m = missile(big)
        if not focus:
            return m
        return combine(pick(p["r_range"], "EnemyChampionRecentlyAttacked", on_me(flag("r_aim", 1)), m),
                       sw("r_aim", combine(*rm("r_aim")), m))

    if native:
        fire = combine(sw("r_c2", combine(*rm("r_c2"), {"type": "Native", "effect_ref": "league_corki:big"}),
                          combine(sw("r_c1", combine(*rm("r_c1"), flag("r_c2", None)), flag("r_c1", None)),
                                  {"type": "Native", "effect_ref": "league_corki:aim"})))
    else:
        normal = sw("q_mark", aimed(False, True), aimed(False, False))
        fire = sw("r_c2", combine(*rm("r_c2"), aimed(True, True)),
                  combine(sw("r_c1", combine(*rm("r_c1"), flag("r_c2", None)), flag("r_c1", None)), normal))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(voice("vo_r", p), delayed(p["r_at"], fire)), uses=p["r_n"])

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bolt"), P_("q_bomb"), P_("r_missile"), P_("r_big_missile", BIG)]
    views_e = [E("a_hit"), E("q_hit"), E("q_boom", BIG, 2, False), E("e_hit"), E("w_fire", FX, -1, False),
               E("w_fire_big", BIG, -1, False), E("w_burn"), E("pk_blast", BIG, 2, False), E("pk_hit"), E("r_hit"),
               E("r_boom", FX, 2, False), E("r_big_boom", BIG, 2, False)]
    views_b = [B_("e_shred", FX, 3)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "AP", "Range", "Magic"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (native=1)")
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
