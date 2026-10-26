"""Build tft_norra.data_champion (the tft pack's second hero: Norra & Yuumi, mid, Magician) from the parameters P.

    python tools/kit/build_norra.py [--set key=value ...] [--out file] [--params json] [--nodes]

Norra is the yordle portal mage of Teamfight Tactics set 12 (Magic n' Mayhem): the 5-cost unit "Norra & Yuumi"
(Portal / Best Friends / Mage). TFT gives her one ability (Portalpalooza: a ball at her target explodes and paints the
ground, the paint burns; a ball landing on paint bounces to a new spot within two hexes first) and a trait (Best
Friends: Yuumi rides an ally, heals it and shares Norra's ability power). The rest is our own design (the user's pick,
2026-10-26: mid lane, plan A 「次元门」):
  passive Best Friends (最佳好友): every p_cd ticks her attack also sends Yuumi to an ally within p_r (a random one,
          `RandomTarget AllyNotSelf`): it heals p_heal + p_heal_r% AP and gains p_ap ability power and p_ad attack while
          she rides it (p_ride ticks, the cat on her book over its head: `view_buffs` p_yuumi); with nobody there she
          rides Norra herself (a lock flag, league_janna E's way). The attack is no skill slot: the game copies skill
          and skill2 every tick, so the passive lives here.
  attack  a bolt out of a small portal at her hand (100% AD), homing on `Enemy` (towers too), released on a_rel.
  skill   Portalpalooza (次元门狂欢, TFT's ability), `Targeting` on `EnemyWithoutTower` (q_range): a portal ball is lobbed
          onto the spot the target stood on (q_travel): q_dmg + q_ratio% AP within q_r, and the ground there is painted
          for q_paint_t ticks (a field burning q_dot + q_dot_r% AP every q_paint_p, its picture the splash of paint). Data
          cannot ask whether a spot is painted, so "the ball lands on paint" is "her last paint still lasts" (the flag
          q_live, laid with each paint): then the ball bounces - a search round the landing spot (q_b_r, about two TFT
          hexes) picks another enemy and q_b_t ticks later a second blast and a second paint go off where it stands.
  skill2  Otherworld Delivery (异界来物), `Targeting` on `EnemyChampion` (e_range, only in fights): a portal opens by an
          ally within e_ally_r (else by herself) and shields it (e_sh + e_sh_r% AP for e_sh_t ticks); out of a portal
          over the enemy champion falls what comes next of three (permanent flags e_s1 / e_s2 count the casts):
          an anvil (e_dmg + e_ratio% AP within e_r, stunned e_stun ticks), a potion (instead: Norra and every allied
          champion within e_pot_r heal e_heal + e_heal_r% AP), a giant book (e_dmg + e_ratio% AP within e_r, knocked up
          e_up ticks).
  ult     The Book of Thresholds (门槛之书), `Targeting` on `EnemyChampion` (r_range): a great portal opens over the
          champion's spot (a warning ring for r_open ticks) and the book's page falls through it: every enemy within
          r_r takes r_dmg + r_ratio% AP, is stunned r_stun ticks and stays "paper" (damaged_amplify r_amp% for
          r_paper_t ticks); every allied champion there is shielded r_sh + r_sh_r% AP for r_sh_t ticks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_norra"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"
RIDE = f"asset/{MOD_ID}/effects/{ID}_yuumi"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are a
# draft until the strips exist (a_rel, q_rel, e_rel, r_rel then come from tools/art/rig_norra.py MS).
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9); a small yordle
    "hp": 860, "hp_g": 95, "atk": 74, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 10, "a_speed": 4000,
    # passive Best Friends (TFT: Yuumi heals 100/150/200 every 4 s, shares 10% of Norra's AP)
    "p_cd": 240, "p_r": 70000, "p_heal": 30, "p_heal_r": 15, "p_ap": 15, "p_ad": 8, "p_ride": 250,
    # Portalpalooza (TFT: 3 s paint)
    "q_cd": 270, "q_range": 70000, "q_dur": 30, "q_rel": 12, "q_travel": 26, "q_r": 30000,
    "q_dmg": 40, "q_ratio": 30, "q_paint_t": 300, "q_paint_p": 30, "q_dot": 6, "q_dot_r": 5,
    "q_b_r": 36000, "q_b_t": 14,
    # Otherworld Delivery
    "e_cd": 540, "e_range": 60000, "e_dur": 26, "e_rel": 10, "e_ally_r": 50000, "e_sh": 60, "e_sh_r": 35,
    "e_sh_t": 180, "e_travel": 18, "e_r": 20000, "e_dmg": 50, "e_ratio": 35, "e_stun": 50, "e_up": 40,
    "e_pot_r": 45000, "e_heal": 50, "e_heal_r": 30,
    # The Book of Thresholds
    "r_cd": 3000, "r_range": 75000, "r_dur": 40, "r_rel": 20, "r_open": 40, "r_r": 45000,
    "r_dmg": 150, "r_ratio": 60, "r_stun": 90, "r_amp": 20, "r_paper_t": 240,
    "r_sh": 80, "r_sh_r": 40, "r_sh_t": 180,
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


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def refresh(name, tick, **fields):
    return combine(unflag(name), flag(name, tick, **fields))


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Ally"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def pick(rng, target, effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point (a `Delayed`
    there keeps it); `seen` = the telegraph played on the landing point the whole flight."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ attack + passive Best Friends
    ride = [heal(p["p_heal"], p["p_heal_r"]), buff("p_yuumi", p["p_ride"], magic_power=p["p_ap"], attack=p["p_ad"]),
            view("p_heal"), tsfx("p_heal")]
    yuumi = combine(flag("p_cd", p["p_cd"]),
                    pick(p["p_r"], "AllyNotSelf", [flag("p_lock", 2)] + ride),
                    delayed(1, when("p_lock", combine(), around(1, "AllyOnlySelf", ride))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"),
                              homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"]),
                              when("p_cd", combine(), yuumi)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Portalpalooza
    def burst(name):
        return [view(f"{name}_blast"), sfx("q_blast"),
                zone(f"{name}_hit", p["q_r"], [ap(p["q_dmg"], p["q_ratio"]), view("q_hit")]),
                field(f"{name}_paint", p["q_r"], p["q_paint_t"], p["q_paint_p"], [ap(p["q_dot"], p["q_dot_r"])])]
    bounce = pick(p["q_b_r"], "EnemyWithoutTower",
                  [delayed(1, lob("q_hop", p["q_b_t"], burst("q2")))], fp=True)
    ball = lob("q_ball", p["q_travel"],
               burst("q") + [when("q_live", bounce, combine()), refresh("q_live", p["q_paint_t"])])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_rel"] - 1, ball)))

    # ------------------------------------------------------------------ skill2: Otherworld Delivery
    guard = [shield(p["e_sh"], p["e_sh_r"], p["e_sh_t"]), buff("e_guard", p["e_sh_t"]), tsfx("e_shield")]
    portal = combine(sfx("e"), pick(p["e_ally_r"], "AllyNotSelf", [flag("e_lock", 2)] + guard),
                     delayed(1, when("e_lock", combine(), around(1, "AllyOnlySelf", guard))))
    anvil = lob("e_anvil", p["e_travel"], [view("e_anvil_hit"), sfx("e_anvil"),
                                           zone("e_anvil_zone", p["e_r"], [ap(p["e_dmg"], p["e_ratio"]),
                                                                          {"type": "Stun", "duration": p["e_stun"]}])],
                target="EnemyChampion")
    book = lob("e_book", p["e_travel"], [view("e_book_hit"), sfx("e_book"),
                                         zone("e_book_zone", p["e_r"], [ap(p["e_dmg"], p["e_ratio"]),
                                                                       {"type": "Airborne", "duration": p["e_up"]}])],
               target="EnemyChampion")
    potion = combine(sfx("e_potion"), around(p["e_pot_r"], "AllyChampion",
                                             [heal(p["e_heal"], p["e_heal_r"]), view("e_potion")]))
    cycle = when("e_s1", combine(unflag("e_s1"), flag("e_s2", None), potion),
                 when("e_s2", combine(unflag("e_s2"), book), combine(flag("e_s1", None), anvil)))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    delayed(p["e_rel"] - 1, portal, cycle))

    # ------------------------------------------------------------------ ult: The Book of Thresholds
    page = [view("r_book"), sfx("r_blast"),
            zone("r_hit", p["r_r"], [ap(p["r_dmg"], p["r_ratio"]), {"type": "Stun", "duration": p["r_stun"]},
                                     buff("r_paper", p["r_paper_t"], damaged_amplify=p["r_amp"]), view("r_hit"),
                                     tsfx("r_hit")]),
            zone("r_ward", p["r_r"], [shield(p["r_sh"], p["r_sh_r"], p["r_sh_t"]), buff("e_guard", p["r_sh_t"])],
                 target="AllyChampion")]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), delayed(p["r_rel"] - 1, lob("r_gate", p["r_open"], page, target="EnemyChampion",
                                                               seen="r_warn"))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    Pj = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    Ev = lambda name, tag, anim_=FX, z=2, follow=True: {**E(name, anim_, z, follow), "tag": tag}
    # a_bolt and q_ball are turned with their flight (both symmetric top to bottom); the paint is a splash under the
    # pivot, the same turned half round (the bounce's paint shares its picture); e_anvil, e_book, q_hop and r_gate fly
    # hidden: the anvil and the book fall out of a portal over the target inside e_anvil_hit / e_book_hit (upright
    # pictures: ViewEffects, never turned), the bounce shows as its blast, the gate as its warning ring
    views_p = [Pj("a_bolt"), Pj("q_ball"), Pj("q_paint", BIG, -2), Pj("q2_paint", BIG, -2, "q_paint")]
    views_e = [E("a_hit"), E("q_blast", BIG, 2, False), Ev("q2_blast", "q_blast", BIG, 2, False), E("q_hit"),
               E("e_anvil_hit", BIG, 2, False), E("e_book_hit", BIG, 2, False), E("e_potion"), E("p_heal"),
               E("r_warn", BIG, -2, False), E("r_book", BIG, 3, False), E("r_hit")]
    views_b = [B_("p_yuumi", RIDE, 4, "idle"), B_("e_guard", FX, 3), B_("r_paper", FX, 3)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "Heal", "Shield", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
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
