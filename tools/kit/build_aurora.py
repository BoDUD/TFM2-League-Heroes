"""Build league_aurora.data_champion (mid, Magician: the Witch Between Worlds) from the parameters P.

    python tools/kit/build_aurora.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-23: MID, layout A - Twofold Hex / The Weirding / Between Worlds, Across the Veil folded
into the passive; combos E -> Q, R -> E, Q's two passes stacking the passive, the teleport across the zone; 「有连招要做连招」).
TFM2 has three active slots: Twofold Hex (Q) is `skill`, The Weirding (E) `skill2`, Between Worlds (R) the `ult`.
  passive Spirit Abjuration (驱灵奇术): every champion hit of hers (attack, Q out, Q back, E, R) counts on a caster ladder
          s_1 -> s_2 (p_t ticks, refreshed by every count; league_kennen's marks: the count is hers, not the target's),
          one count per source and cast (2-tick locks; Q's two passes are two sources, so one Q can count twice); the
          third exorcises the spirit: p_dmg + p_ratio% AP and p_hp% of the target's max health, and the spirit heals
          her p_heal + p_heal_r% AP and hastens her p_ms% for p_ms_t (League: 1% max health, a spirit that heals and
          gives move speed).
          Across the Veil (灵纱洞开), folded in: low on health (the add-on league_aurora's 2-tick flag `low`; w_gate 1
          reads instead "an enemy champion within w_near", the stand-in the classic simulation can run) and with an
          enemy champion within w_near, her next attack or E first hops her away from it (MoveBack w_back x w_back_t),
          turns her invisible w_inv ticks and hastens her w_ms% for w_ms_t; then w_cd ticks before the next.
  attack  A spirit bolt (homing on `Enemy`, 100% AD) released on a_rel; a champion-only twin counts the passive.
  skill   Twofold Hex (飞去来咒, cooldown q_cd, the flag `q_cd` the combos read): a `Direction` cast on
          `EnemyWithoutTower` (q_range). The hex flies q_len through everything (q_dmg + q_ratio% AP, the curse picture
          for q_hold + 30 ticks), stops, and q_hold ticks later the curses are drawn back: the return flies to her through
          everything again, q2_dmg + q2_ratio% AP (League's recast; the curse pulled through the ones on the way).
  skill2  The Weirding (怪奇喷涌, cooldown e_cd, the flag `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range): a
          blast in a cone toward the target (e_len, cone e_cone), e_dmg + e_ratio% AP and a slow that decays (e_slow1%
          for e_slow1_t, e_slow2% for e_slow2_t), then she hops back e_back x e_back_t (League's 250 units).
  ult     Between Worlds (双界合一): a `Targeting` cast on `EnemyChampion` (r_range): she leaps onto it (MoveToTarget) and
          the shockwave round her lands r_dmg + r_ratio% AP and r_slow1% for r_slow1_t; the realm (r_zone) stays r_t
          ticks on the target's spot, slowing r_slow% every r_per.
  combos  E -> Q (the user: E 命中 -> Q): a champion the blast hits gets the hex eq_gap ticks later if Twofold Hex is ready
          (its cooldown flag taken): a homing hex (q_dmg) and, q_hold ticks later, its curse drawn back (q2_dmg).
          R -> E: the shockwave's first champion gets The Weirding re_gap ticks later if it is ready: the blast round her
          (she is on top of them) and the hop back.
          Q -> passive: the out pass and the return count separately, so one hex through a champion is two of the three.
          Teleport across the realm (领域内传送追击): at r_tp_at, 2 x r_tp_at and 3 x r_tp_at ticks into the realm, with no
          enemy champion within r_close of her, a hidden bolt seeks the ult's champion; if it is within r_tp_max of her
          she steps through to it (Teleport) - League's crossing from one edge of the realm to the other.
Action tags (the art): idle run attack hit dead skill skill2 ult veil.
Numbers: League 16.20 (CommunityDragon aurora.bin) read into the Magician mid range (league_hwei, league_neeko).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_aurora.data_champion")
ID = "league_aurora"
FX = "asset/league/effects/league_aurora_fx"
BIG = "asset/league/effects/league_aurora_big"

# League's Aurora (16.20, CommunityDragon aurora.bin): 607 +110 hp, 53 AD, 23 armour, 30 mr, 335 move, 550 range.
# Passive: 4 s debuff, 1% max health, spirits heal, +5% (+2% per spirit) move speed. Q 900 range, 45-145 out and
# 45-145 back (+ up to 50% by missing health), 3.5 s mark, cd 9-7. W 300 hop, 1-1.6 s invisible, 20-40% speed, cd
# 22-18. E 825 x 175 blast, 80-240, 80% slow decaying over 1 s, 250 hop back, cd 15-11. R 250 jump, 175-375, 30% slow,
# a 700 realm for 3-4 s (she crosses its edges), cd 140-100.
P = {
    # stats (Magician mid: league_hwei 940 +94 hp, 70 +6 attack, 40 +20 ap, 20 +7 def)
    "hp": 900, "hp_g": 90, "atk": 68, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 6, "mr": 22, "mr_g": 4,
    "ms": 920, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 90, "a_rel": 10, "a_speed": 4500, "a_y": -4000,
    # passive: Spirit Abjuration; Across the Veil folded in
    "p_t": 240, "p_dmg": 25, "p_ratio": 20, "p_hp": 2, "p_heal": 30, "p_heal_r": 15, "p_ms": 15, "p_ms_t": 90,
    "w_gate": 0, "w_cd": 1200, "w_near": 35000, "w_back": 4000, "w_back_t": 6, "w_inv": 75, "w_ms": 30, "w_ms_t": 120,
    # skill: Twofold Hex
    "q_cd": 450, "q_range": 85000, "q_dur": 30, "q_rel": 12, "q_speed": 4000, "q_len": 85000, "q_rad": 8000,
    "q_dmg": 60, "q_ratio": 40, "q_hold": 40, "q_back_speed": 4500, "q2_dmg": 60, "q2_ratio": 40, "q_ball_speed": 4500,
    # skill2: The Weirding
    "e_cd": 780, "e_range": 70000, "e_dur": 30, "e_rel": 12, "e_len": 75000, "e_cone": 900, "e_dmg": 100,
    "e_ratio": 60, "e_slow1": 60, "e_slow1_t": 30, "e_slow2": 25, "e_slow2_t": 60, "e_back": 3000, "e_back_t": 8,
    "e_wave_speed": 6000, "eq_gap": 6, "e_near_r": 30000,
    # ult: Between Worlds
    "r_cd": 2100, "r_range": 60000, "r_dur": 36, "r_rel": 14, "r_speed": 3500, "r_r1": 28000, "r_dmg": 200,
    "r_ratio": 70, "r_slow1": 40, "r_slow1_t": 60, "r_zone": 38000, "r_t": 210, "r_per": 15, "r_slow": 30,
    "re_gap": 8, "r_tp_at": 60, "r_close": 30000, "r_tp_max": 70000,
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
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def maxhp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def cone(length, c, target, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": length, "range": c}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end, y=0, through=True):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": through, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def back(name, speed, radius, target, effects):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": 400000,
            "penetrate": True, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def lob(name, travel, end):
    """A 1-radius lob onto the target's spot (league_annie R's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def field(name, radius, tick, period, first, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Spirit Abjuration (champions only)
    def mark(src):
        """One count of the ladder on the champion these effects run on; the third exorcises its spirit."""
        spirit = combine(ap(p["p_dmg"], p["p_ratio"]), maxhp(p["p_hp"]), view("p_spirit"), tsfx("p_spirit"),
                         on_me(heal(p["p_heal"], p["p_heal_r"]), cview("p_heal"),
                               refresh("p_haste", p["p_ms_t"], move_speed_mult=p["p_ms"])),
                         *rm("s_1", "s_2"))
        count = sw("s_1", combine(refresh("s_1", p["p_t"]), refresh("s_2", p["p_t"])), refresh("s_1", p["p_t"]))
        return sw(f"lk_{src}", NONE, combine(flag(f"lk_{src}", 2), buff("p_mark", p["p_t"]),
                                             sw("s_2", spirit, count)))

    # Across the Veil: low (the add-on's flag, or w_gate 1's stand-in) and a champion within w_near
    def veil():
        hop = pick(p["w_near"], "EnemyChampion", flag("w_cd", p["w_cd"]), anim("veil", 12), sfx("w"), cview("w_veil"),
                   {"type": "MoveBack", "speed": p["w_back"], "tick": p["w_back_t"]},
                   on_me({"type": "CasterInvisible", "tick": p["w_inv"]},
                         refresh("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"])))
        return sw("w_cd", NONE, hop if p["w_gate"] else sw("low", hop))

    # ------------------------------------------------------------------ attack: a spirit bolt
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), veil(), delayed(p["a_rel"] - 1, alive(
                          sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                           p["a_speed"], p["a_y"]),
                          homing("a_twin", "EnemyChampion", [mark("a")], p["a_speed"], p["a_y"])))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Twofold Hex
    hex_hit = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"), buff("q_curse", p["q_hold"] + 30)]
    back_hit = [ap(p["q2_dmg"], p["q2_ratio"]), view("q_back_hit"), tsfx("q_back_hit")]
    hex_ = line("q_out", p["q_speed"], p["q_len"], p["q_rad"], "EnemyWithoutTower", hex_hit,
                [delayed(p["q_hold"], sfx("q_back"),
                         back("q_back", p["q_back_speed"], p["q_rad"], "EnemyWithoutTower", back_hit),
                         back("q_back_twin", p["q_back_speed"], p["q_rad"], "EnemyChampion", [mark("q2")]))],
                p["a_y"])
    hex_twin = line("q_out_twin", p["q_speed"], p["q_len"], p["q_rad"], "EnemyChampion", [mark("q")], [], p["a_y"])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap),
                           sw("q_cd", NONE, combine(refresh("q_cd", p["q_cd"]), voice("vo_q", p), sfx("q"),
                                                    delayed(p["q_rel"] - 1, alive(hex_, hex_twin))))))

    # ------------------------------------------------------------------ skill2: The Weirding
    def hex_on():
        """E -> Q: the hex on this champion if Twofold Hex is ready."""
        drawn = delayed(p["q_hold"], view("q_back_hit"), tsfx("q_back_hit"), ap(p["q2_dmg"], p["q2_ratio"]), mark("q2"))
        return delayed(p["eq_gap"], sw("q_cd", NONE, combine(
            refresh("q_cd", p["q_cd"]), sfx("q"),
            homing("q_ball", "EnemyChampion", [*hex_hit, mark("q"), drawn], p["q_ball_speed"], p["a_y"]))))

    slows = [buff("e_slow", p["e_slow1_t"], move_speed_mult=-p["e_slow1"]),
             buff("e_slow2", p["e_slow2_t"], move_speed_mult=-p["e_slow2"])]
    blast_hit = [ap(p["e_dmg"], p["e_ratio"]), *slows, view("e_hit"), tsfx("e_hit")]
    hop_back = {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]}
    weirding = combine(
        cview("e_burst"), sfx("e"),
        line("e_wave", p["e_wave_speed"], p["e_len"], 1000, "EnemyChampion", [], []),
        cone(p["e_len"], p["e_cone"], "EnemyWithoutTower", blast_hit),
        cone(p["e_len"], p["e_cone"], "EnemyChampion", [mark("e"), hex_on()]),
        delayed(2, hop_back))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), veil(),
                            sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]), voice("vo_e", p),
                                                     delayed(p["e_rel"] - 1, alive(weirding))))))

    # ------------------------------------------------------------------ ult: Between Worlds
    def weird_on():
        """R -> E: The Weirding round her (she landed on them) if it is ready, then the hop back."""
        return delayed(p["re_gap"], sw("e_cd", NONE, combine(
            refresh("e_cd", p["e_cd"]), cview("e_burst"), sfx("e"),
            around(p["e_near_r"], "EnemyWithoutTower", blast_hit),
            around(p["e_near_r"], "EnemyChampion", [mark("e")]), delayed(2, hop_back))))

    def cross(k):
        """The teleport across the realm, k x r_tp_at ticks in: to the ult's champion when nobody is on top of her."""
        step = homing("r_seek", "EnemyChampion", [
            pick(p["r_tp_max"], "AllyOnlySelf", flag("r_ok", 1), from_projectile=True),
            sw("r_ok", combine(*rm("r_ok"), view("r_blink"), tsfx("r_blink"), {"type": "Teleport"}))], 20000)
        return delayed(k * p["r_tp_at"], alive(*rm("r_near"), pick(p["r_close"], "EnemyChampion", flag("r_near", 1)),
                                               sw("r_near", combine(*rm("r_near")), step)))

    shock_hit = [ap(p["r_dmg"], p["r_ratio"]), buff("r_slow1", p["r_slow1_t"], move_speed_mult=-p["r_slow1"]),
                 view("r_hit"), tsfx("r_hit")]
    realm = lob("r_anchor", 1, [view("r_zone"), sfx("r_zone"),
                                field("r_field", p["r_zone"], p["r_t"], p["r_per"], p["r_per"],
                                      [buff("r_slow", p["r_per"] + 5, move_speed_mult=-p["r_slow"])])])
    landing = [cview("r_shock"), sfx("r_land"),
               around(p["r_r1"], "EnemyWithoutTower", shock_hit),
               around(p["r_r1"], "EnemyChampion", [mark("r")]),
               weird_on(), realm]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive({"type": "MoveToTarget", "speed": p["r_speed"],
                                                        "range": p["r_range"], "end_effects": landing})),
                         cross(1), cross(2), cross(3)))

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_bolt"), Pj("q_out"), Pj("q_back"), Pj("q_ball", "q_out"), Pj("e_wave")]
    views_e = [E("a_hit"), E("q_hit"), E("q_back_hit"), E("p_spirit"), E("p_heal"), E("w_veil", FX, 3, False),
               E("e_burst", FX, 3, False), E("e_hit"), E("r_shock", BIG, -1, False), E("r_zone", BIG, -1, False),
               E("r_hit"), E("r_blink")]
    views_b = [B_("q_curse", FX, 3), B_("p_mark", FX, 3), B_("w_haste", FX, -1), B_("e_slow", FX, -1, "slow"),
               B_("r_slow", FX, -1, "slow"), B_("r_slow1", FX, -1, "slow")]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "Mobility"],
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
