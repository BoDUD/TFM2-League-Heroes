"""Build league_lissandra.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_lissandra.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-05: all the recommended options):
  attack  An ice bolt thrown at the target (homing, physical 100% AD, the pack mages' way).
  passive Iceborn Subjugation: an enemy champion her attack, Q, W or R kills becomes a frozen thrall where he fell; after
          p_delay ticks it shatters (p_dmg + p_ap% AP round it, p_slow% slow for p_slow_t ticks). Nothing fires on a kill:
          each source runs league_jinx's kill check (a caster flag k_<src> that a living target clears a tick later)
          and a 1-tick hidden lob onto the target fired in the same tick as the damage (a dying target runs no queued
          effect but pictures, so the spot is taken from the lob, which lands where he stood); the lob's end_effects
          read the flag a few ticks later at that spot. League's thrall walks toward enemies; this one stays put.
  skill   Q Ice Shard: a `Direction` cast on `EnemyWithoutTower`; at the release an enemy champion within q_aim gets the
          shard (a straight line at where he stands then: dodged by walking off it), else the cast's direction. One
          penetrating LinearProjectile (League's shard plus the shatter behind the first target): q_dmg + q_ap% AP and a
          q_slow% slow for q_slow_t ticks on every unit it passes.
  skill2  W Ring of Frost with E Glacial Path folded in: a `None` cast on `EnemyWithoutTower` (e_range):
          an enemy unit within w_r -> the ring at once (w_dmg + w_ap% AP, a w_root-tick root round her);
          else, E off its own cooldown (e_cd flag) and an enemy champion her team is fighting (EnemyChampionRecentlyAttacked)
          within e_range -> League's E -> W engage: the claw flies at him (e_dmg + e_ap% to every unit it passes), a
          hidden line on EnemyChampion stops e_stop short of him and she blinks there (Teleport), then the ring;
          else the claw alone at an enemy in reach (a poke that also clears waves and camps; no blink).
  ult     R Frozen Tomb, armed like league_kayle R: a 3-tick `None` cast on `EnemyChampion` (r_arm_range) adds r_armed for
          r_arm ticks; her attacks, Q and W check it: two or more enemy champions within r_self_r (League's low-health
          self-cast, read as "crowded" - nothing reads health) -> SELF: r_self_t ticks frozen in place (damaged_reduce
          100, cc immune), healed r_heal + r_heal_ap% AP over it; else an enemy champion her team is fighting within
          r_range -> ENEMY: stunned r_stun ticks, r_dmg + r_ap% AP. Either way the ice bursts round the tomb (r_sp +
          r_sp_ap% to the enemies there) and leaves a field (r_field_r, r_field_t ticks) that slows enemies r_slow%.
          Unused, the cooldown is refunded.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_lissandra.data_champion")
ID = "league_lissandra"
FX = "asset/league/effects/league_lissandra_fx"
BIG = "asset/league/effects/league_lissandra_big"

# Numbers = candidate c2 of the 10-min classic-SDK simulations (lz_sim/sim/kd.py, mid lane against the five base mages,
# both sides, 2026-10-05): +1.51 on seeds 1-24, +1.55 on seeds 25-48 (the pack's league_ryze +1.50). The draft c0 was
# -0.22 (deal 7915): every damage up (Q 90+80% -> 120+100% and cd 270 -> 240, W 70+60% -> 100+80%, E 60+50% -> 80+60%,
# R 150+75% -> 200+100%, thrall 100+50% -> 150+70%). A wider "crowded" check for the self tomb (r_self_r 40000) or more
# toughness (hp 980, def/mr 26: +2.04 on 12 seeds) did not help or overshot.
P = {
    # stats (Magician base: attack 80 +6, ability power 40 +20, hp 900 +100, defence 20 +7, mr 20 +3, move 900, range
    # 60000, attack interval 90); League's Lissandra: 550 range, a battle mage who stands in the fight
    "hp": 920, "hp_g": 100, "atk": 80, "atk_g": 6, "mp": 40, "mp_g": 20, "def": 22, "def_g": 7, "mr": 22, "mr_g": 3,
    "ms": 900, "ms_g": 10,
    # attack: the bolt leaves the hand on atk_st
    "atk_range": 55000, "atk_dur": 26, "atk_cd": 85, "atk_st": 13, "bolt_speed": 5000, "bolt_y": -8000,
    # passive: the kill flag lasts k_hold ticks; the thrall shatters p_delay ticks after it rises
    "k_hold": 40, "k_read": 3,
    "p_delay": 90, "p_r": 25000, "p_dmg": 150, "p_ap": 70, "p_slow": 25, "p_slow_t": 90,
    # skill: Q Ice Shard (League: 45-255 dmg, slow 16-40% 1.5 s, missile 2200/s 725 range, shards to 825, cd 8-4 s)
    "q_cd": 240, "q_range": 70000, "q_reach": 88000, "q_dur": 26, "q_st": 12, "q_speed": 5000, "q_rad": 7000,
    "q_y": -15000, "q_dmg": 120, "q_ap": 100, "q_slow": 25, "q_slow_t": 90, "q_aim": 80000,
    # skill2: W Ring of Frost (League: radius 450, root 1.25-1.65 s, 70-245, cd 10-8 s)
    "w_cd": 420, "w_dur": 24, "w_r": 26000, "w_root": 75, "w_dmg": 100, "w_ap": 80,
    # E Glacial Path (League: claw 1025 range at 850/s, 70-245, cd 24-15 s, recast = blink to the claw)
    "e_cd": 900, "e_range": 85000, "e_reach": 90000, "e_speed": 3500, "e_rad": 6000, "e_y": -1000, "e_dmg": 80,
    "e_ap": 60, "e_stop": 14000, "e_throw": 18, "e_land": 4,
    # ult: R Frozen Tomb (League: cd 120/100/80 s, enemy stun 1.5 s, self 2.5 s + heal, field 690 slow 45-75% 3 s,
    # 150-350 + 75% AP)
    "r_cd": 3600, "r_arm": 600, "r_arm_range": 90000, "r_range": 60000, "r_self_r": 30000, "r_stun": 90,
    "r_dmg": 200, "r_ap": 100, "r_sp": 80, "r_sp_ap": 40, "r_burst_r": 26000, "r_field_r": 30000, "r_field_t": 180,
    "r_slow": 40, "r_self_t": 150, "r_heal": 200, "r_heal_ap": 80, "r_anim": 30,
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
    duration = tick if isinstance(tick, str) else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": duration, **fields},
            "only_to_enemy": False}


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


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
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


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Iceborn Subjugation
    def thrall():
        """On the spot where a champion fell (a lob's end_effects): the thrall rises, then shatters."""
        burst = zone("p_area", p["p_r"], 1, 1, "EnemyWithoutTower",
                     [ap(p["p_dmg"], p["p_ap"]), slow("p_slow", p["p_slow"], p["p_slow_t"]), tsfx("p_hit")])
        return combine(view("p_thrall"), sfx("p_rise"), delayed(p["p_delay"], view("p_burst"), sfx("p_burst"), burst))

    def mark(src):
        """Before the damage, on a champion: the kill flag (a living target clears it a tick later)."""
        return refresh(f"k_{src}", p["k_hold"])

    def clear(src):
        """After the damage, on a champion: clears the flag while he lives (a dead one never runs it)."""
        return casted(3, 1, *rm(f"k_{src}"))

    def spot(src, wait):
        """A 1-tick hidden lob at the champion, fired with the damage: `wait` ticks after it lands a flag still there
        means he died - the thrall rises on that spot."""
        k = f"k_{src}"
        return lob(f"{src}_spot", 1, [delayed(wait, sw(k, combine(*rm(k), thrall())))])

    # ------------------------------------------------------------------ ult check (armed)
    def tomb_burst():
        """At the tomb's spot (a lob's end_effects): the burst and the slowing field."""
        hit = zone("r_area", p["r_burst_r"], 1, 1, "EnemyWithoutTower", [ap(p["r_sp"], p["r_sp_ap"]), tsfx("r_hit")])
        ice = field("r_field", p["r_field_r"], p["r_field_t"], 15, "EnemyWithoutTower",
                    [slow("r_slow", p["r_slow"], 20)])
        return [view("r_burst"), hit, ice]

    tomb_enemy = combine(*rm("r_armed"), anim("ult", p["r_anim"]), cview("r_cast"), sfx("r_cast"),
                         mark("r"), ap(p["r_dmg"], p["r_ap"]), {"type": "Stun", "duration": p["r_stun"]},
                         buff("r_tomb", p["r_stun"]), tsfx("r_tomb"), clear("r"),
                         lob("r_spot", 1, [*tomb_burst(), delayed(p["k_read"] + 1, sw("k_r", combine(*rm("k_r"),
                                                                                                 thrall())))]))
    tomb_self = combine(*rm("r_armed"), anim("ult_self", p["r_self_t"]), cview("r_self_cast"), sfx("r_self"),
                        flag("r_stasis", p["r_self_t"], damaged_reduce=100, cc_immune=True),
                        casted(p["r_self_t"], 30, heal(p["r_heal"] // 5, p["r_heal_ap"] // 5)),
                        on_me(lob("r_self_spot", 1, tomb_burst(), target="AllyChampion")))
    count = [*rm("r_n1", "r_n2"),
             around(p["r_self_r"], "EnemyChampion", [sw("r_n1", flag("r_n2", 3), flag("r_n1", 3))])]
    r_check = sw("r_armed", combine(*count, on_me(delayed(1, sw("r_armed", sw(
        "r_n2", tomb_self, pick(p["r_range"], "EnemyChampionRecentlyAttacked", tomb_enemy)))))))

    # ------------------------------------------------------------------ attack: the ice bolt
    # the bolt's longest flight: the AI starts attacks from up to ~75000 centre to centre, plus the target's body
    flight = -(-(p["atk_range"] + 40000) // p["bolt_speed"])
    bolt = homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    # the champion-only twin of the bolt, flying the same path: the kill flag
    twin = homing("a_twin", p["bolt_speed"], p["bolt_y"], "EnemyChampion", [mark("a"), clear("a")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(r_check, sfx("a_throw"), bolt, twin, spot("a", flight + p["k_read"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Ice Shard
    q_flight = -(-(p["q_reach"] + 10000) // p["q_speed"])
    shard = line("q_shard", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True,
                 [ap(p["q_dmg"], p["q_ap"]), slow("q_slow", p["q_slow"], p["q_slow_t"]), view("q_hit"), tsfx("q_hit")])
    q_twin = line("q_twin", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyChampion", True,
                  [mark("q"), clear("q")])
    shot = combine(*rm("q_champ"),
                   pick(p["q_aim"], "EnemyChampion", flag("q_champ", 1), shard, q_twin, spot("q", q_flight + p["k_read"])),
                   sw("q_champ", NONE, combine(shard, q_twin)))
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(r_check, sfx("q_cast"), cview("q_cast"), shot))

    # ------------------------------------------------------------------ skill2: W Ring of Frost + E Glacial Path
    def ring(late):
        """The ring round her: damage + root on every enemy unit, the champions' kill check."""
        pic = [cview("w_ring_late")] if late else [cview("w_ring")]
        return combine(*pic, sfx("w_ring"),
                       around(p["w_r"], "EnemyChampion", [mark("w")]),
                       around(p["w_r"], "EnemyWithoutTower", [ap(p["w_dmg"], p["w_ap"]), {"type": "Bind", "duration": p["w_root"]},
                                                             buff("w_root", p["w_root"]), view("w_hit"), tsfx("w_hit")]),
                       around(p["w_r"], "EnemyChampion", [clear("w"), spot("w", p["k_read"])]))

    claw_hit = [ap(p["e_dmg"], p["e_ap"]), view("e_hit"), tsfx("e_hit")]
    claw = line("e_claw", p["e_speed"], p["e_reach"], p["e_rad"], p["e_y"], "EnemyWithoutTower", True, claw_hit)
    # the blink: a hidden line on EnemyChampion that stops e_stop short of the first champion (or at its range)
    land = [{"type": "Teleport"}, cview("e_port"), sfx("e_port"),
            delayed(p["e_land"], anim("skill2", p["w_dur"]), ring(True))]
    path = line("e_path", p["e_speed"], p["e_reach"], p["e_stop"], 0, "EnemyChampion", False, [], land)
    engage = combine(flag("e_cd", p["e_cd"]), flag("e_go", 1), anim("skill2_e", p["e_throw"] + p["e_reach"] // p["e_speed"]),
                     cview("e_cast"), sfx("e_cast"), claw, path)
    poke = combine(anim("skill2_e", p["e_throw"]), cview("e_cast"), sfx("e_cast"), claw)
    w_or_e = combine(*rm("w_near", "e_go", "e_any"),
                     pick(p["w_r"], "EnemyWithoutTower", flag("w_near", 1)),
                     sw("w_near", ring(False),
                        combine(sw("e_cd", NONE, pick(p["e_range"], "EnemyChampionRecentlyAttacked", engage)),
                                sw("e_go", NONE, combine(
                                    pick(p["e_range"], "EnemyChampion", flag("e_any", 1), poke),
                                    sw("e_any", NONE, pick(p["e_range"], "EnemyWithoutTower", poke)))))))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["e_range"], "None", "EnemyWithoutTower",
                    combine(r_check, w_or_e))

    # ------------------------------------------------------------------ ult: arms the Frozen Tomb
    ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", combine(
        *rm("r_armed"), flag("r_armed", p["r_arm"]),
        on_me(delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900)))))),
        key="ult")

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow her (the red side's mirroring)
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1, repeat=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                    "repeat": repeat, "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bolt"), P_("q_shard"), P_("e_claw"), P_("r_field", BIG, -1)]
    views_e = [E("a_hit", FX, 2), E("q_cast"), E("q_hit", FX, 2), E("w_ring", BIG, -1), E("w_ring_late", BIG, -1, False),
               E("w_hit", FX, 2), E("e_cast"), E("e_hit", FX, 2), E("e_port", BIG, **LATE),
               E("r_cast", BIG, **LATE), E("r_self_cast", BIG, **LATE), E("r_burst", BIG, 1, False),
               E("p_thrall", BIG, 1, False), E("p_burst", BIG, 1, False)]
    views_b = [B_("q_slow", FX, -1), B_("w_root", FX, -1), B_("r_tomb", BIG, 2), B_("r_stasis", BIG, 2),
               B_("r_slow", FX, -1), B_("p_slow", FX, -1)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "CC"],
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
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
