"""Build league_brand.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_brand.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-06: all the recommended options, plus 「加入高手的连招」):
  passive Blaze (炽热之焰): every spell hit sets the unit ablaze (烈焰焚身): an `AddCasted` Fire burn of p_burn +
          p_burn_ap% AP magic damage every p_period ticks for p_t ticks and p_hp% of its maximum health as TRUE damage
          every p_hp_period ticks (nothing magic reads max health). Stacks: nothing reads a buff on another unit, so the
          count lives on him (league_kennen / league_varus): two caster flags b_1 -> b_2 (b_keep ticks, refreshed by every
          climb), climbed once per source per cast (a 3-tick lock) by his spell hits on enemy CHAMPIONS. A champion hit
          while b_2 holds is the third stack: it turns unstable and p_wait ticks later detonates where it stands - p_det +
          p_det_ap% AP magic damage and p_det_hp% max health true damage to every enemy within p_det_r, setting them
          ablaze - and the count starts over. The pips (1-3) show over the champion hit. A native add-on may later count
          real stacks per enemy (the main pack is complete alone).
  attack  A homing fireball (100% AD).
  skill   W Pillar of Flame (烈焰之柱): a `Targeting` cast on `EnemyWithoutTower` (w_range). At the release a hidden
          1-tick lob marks the target's spot (the ground lights up) and w_delay ticks later the pillar hits round it
          (w_r): w_dmg + w_ap% AP magic damage, w_bonus% more while he has a stack (a burning champion near), ablaze.
          Dodgeable. The slot's effect is empty while the caster flag w_cd (W's cooldown, shared with the combo) runs.
  skill2  E Conflagration (烈火燃烧) -> Q Sear (火焰烙印), League's combo: a `Targeting` cast on `EnemyChampion`
          (c_range; W clears the waves - a stun combo on a minion is wasted). E: a blaze on the unit that spreads round it
          (e_r; e_r_wide while he has a stack - League's wider spread from a burning unit): e_dmg + e_ap% AP, ablaze.
          q_rel ticks later Q: a fireball (non-penetrating, the first enemy on its line at where the unit stands then):
          q_dmg + q_ap% AP, ablaze, and a q_stun-tick stun (the unit burns from E).
          Combo E -> Q -> W (the pros' full combo): a Q that hit a champion with W ready (the caster flag w_cd, which W's
          slot shares: its empty branch the AI does not cast, league_leblanc W) goes on into W on the stunned champion -
          three hits, the third stack: Blaze detonates. The combo's pillar lands on a champion in crowd control.
  ult     R Pyroclasm (烈焰风暴): a `Targeting` cast on `EnemyChampion` (r_range). Cast only in a fight: a hidden lob onto
          the target counts the enemy units within r_b round it (u_1 -> u_2); with fewer than two (the target alone) the
          cast is called off and a 3-tick ult_cooldown_mult 4900 brings R back within 60 ticks (league_taric's refund).
          Else a fireball flies at the target, then bounces r_n - 1 times, r_gap ticks apart, among the enemies within
          r_b of the spot it first hit (every projectile leaves from the caster, so a bounce is a search round that spot
          and a fireball falling on the unit picked, league_nami W): enemy champions first; after a champion it bounces
          to another champion only when two stand there, else to any unit (back onto the first is possible, as in
          League). Every hit: r_dmg + r_ap% AP, ablaze, a r_slow% slow for r_slow_t ticks; champion hits count stacks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_brand.data_champion")
ID = "league_brand"
FX = "asset/league/effects/league_brand_fx"
BIG = "asset/league/effects/league_brand_big"

# Numbers = candidate c4 of the 10-min classic-SDK simulations (tr_sim's kd.py copied to Temp/bd_sim, mid lane against
# the five base mages, three lineups, both sides, 2026-10-06): +1.40 on seeds 1-24 (league_xerath +1.51, league_lissandra
# +1.23 in the draft's batch). The draft c0 was +5.62: the burn's % max-health true damage (on every bounce of R too)
# went, the spells came down, the stun 75 -> 50 ticks, hp 860 -> 820 (+2.34), then the cooldowns (E->Q 9 -> 11 s, W 7 ->
# 8 s). Timings from the strips' release frames (assets/source/brand/poses.json): attack, W and R frame 4 at tick 11, E
# frame 3 at tick 6, Q frame 6 at tick 17.
P = {
    # stats (Magician base like league_xerath: attack 78 +6, magic power 42 +21, hp 860 +95); League's Brand: 570 +105
    # hp, 550 range, a burst mage
    "hp": 820, "hp_g": 95, "atk": 78, "atk_g": 6, "mp": 42, "mp_g": 21, "def": 18, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    # attack (League 550 range); the bolt leaves the throwing hand 2 px over the pivot (5000 - y_offset above it), the
    # Q fireball and the R seed 13 px up (a straight shot from higher leans onto its end)
    "atk_range": 52000, "atk_dur": 28, "atk_cd": 90, "atk_st": 11, "bolt_speed": 4500, "bolt_y": 3000,
    # passive Blaze (League: 3% max HP magic over 4 s, 3 stacks -> 2 s later 9-13% max HP round the target)
    "p_t": 240, "p_period": 60, "p_burn": 6, "p_burn_ap": 4, "p_hp_period": 120, "p_hp": 0,
    "b_keep": 240, "p_wait": 120, "p_det_r": 26000, "p_det": 50, "p_det_ap": 30, "p_det_hp": 4,
    # skill: W Pillar of Flame (League: 900 range, 0.625 s delay, radius 240, 75-255 + 60% AP, +25% on ablaze,
    # cd 10.5-8 s)
    "w_cd": 480, "w_range": 85000, "w_dur": 20, "w_rel": 11, "w_delay": 36, "w_r": 23000, "w_dmg": 70, "w_ap": 55,
    "w_bonus": 25,
    # skill2: E Conflagration (League: 675 range, 70-170 + 45% AP, spread 300 / 600 from ablaze, cd 13-9 s) -> Q Sear
    # (League: 1100 range at 1600/s, width 60, 80-240 + 55% AP, stun 1.5 s on ablaze, cd 8.5-6 s)
    "c_cd": 660, "c_range": 60000, "c_dur": 32, "e_rel": 6, "e_r": 24000, "e_r_wide": 40000, "e_dmg": 45, "e_ap": 35,
    "q_rel": 17, "q_speed": 8000, "q_reach": 95000, "q_rad": 7000, "q_y": -8000, "q_dmg": 60, "q_ap": 45,
    "q_stun": 50, "cw_wait": 6,
    # ult: R Pyroclasm (League: 750 range, 5 bounces, radius 600, 100-300 + 25% AP each, slow 30-60% 0.25 s on
    # ablaze, cd 105/90/75 s)
    "r_cd": 2700, "r_range": 65000, "r_b": 55000, "r_n": 5, "r_gap": 16, "r_fall": 6, "r_rel": 11, "r_anim": 30,
    "r_speed": 4000, "r_y": -8000, "r_dmg": 60, "r_ap": 20, "r_slow": 35, "r_slow_t": 30,
    # his spoken lines: one every vo_gap ticks at most
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
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields},
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


def true(dmg, hp=0):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Fire"):
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


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, end, travel=1):
    """A hidden lob: it lands on the unit's spot `travel` ticks after it is fired; `end` runs on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": "EnemyWithoutTower",
            "applied_effects": [], "end_effects": list(end)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Blaze
    def ignite():
        """On every unit a spell hits: the burn (its own instance, as League's re-applied Blaze)."""
        return combine(casted(p["p_t"], p["p_period"], ap(p["p_burn"], p["p_burn_ap"])),
                       casted(p["p_t"], p["p_hp_period"], true(0, p["p_hp"])), buff("p_burn", p["p_t"]))

    detonation = lob("p_lob", [
        view("p_boom"), sfx("p_boom"),
        zone("p_det", p["p_det_r"], 1, 1, "EnemyWithoutTower",
             [ap(p["p_det"], p["p_det_ap"]), true(0, p["p_det_hp"]), view("p_hit")])])

    def mark(src):
        """On an enemy champion a spell of his hit: the third stack detonates it, the pips, the count a tick later."""
        keep = p["b_keep"]
        climb = sw("b_2", combine(*rm("b_1", "b_2")),
                   sw("b_1", combine(refresh("b_1", keep), refresh("b_2", keep)), refresh("b_1", keep)))
        lock = f"lk_{src}"
        return combine(sw("b_2", combine(buff("p_unstable", p["p_wait"]), delayed(p["p_wait"], detonation))),
                       sw("b_2", view("p_s3"), sw("b_1", view("p_s2"), view("p_s1"))),
                       on_me(delayed(1, sw(lock, NONE, combine(flag(lock, 3), climb)))))

    # ------------------------------------------------------------------ attack: the fireball
    bolt = homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_cast"), bolt), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: W Pillar of Flame
    w_t = p["w_delay"] + 1
    big = 100 + p["w_bonus"]
    pillar = lob("w_lob", [
        view("w_mark"), sfx("w_cast"),
        zone("w_blast", p["w_r"], w_t, w_t, "EnemyWithoutTower",
             [sw("b_1", ap(p["w_dmg"] * big // 100, p["w_ap"] * big // 100), ap(p["w_dmg"], p["w_ap"])), ignite(),
              view("w_hit")]),
        zone("w_blast_c", p["w_r"], w_t, w_t, "EnemyChampion", [mark("w")]),
        delayed(p["w_delay"] - 4, view("w_pillar"), sfx("w_blast"))])

    def w_cast():
        return combine(refresh("w_cd", p["w_cd"]), anim("skill", p["w_dur"]), voice("vo_w", p))

    skill = action("skill", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                   sw("w_cd", NONE, combine(w_cast(), delayed(p["w_rel"], pillar))))

    # ------------------------------------------------------------------ skill2: E Conflagration -> Q Sear (-> W)
    def spread(r):
        return [zone("e_zone", r, 1, 1, "EnemyWithoutTower",
                     [ap(p["e_dmg"], p["e_ap"]), ignite(), view("e_hit"), tsfx("e_hit")]),
                zone("e_zone_c", r, 1, 1, "EnemyChampion", [mark("e")])]

    blaze = lob("e_lob", [view("e_flare"), sw("b_1", combine(*spread(p["e_r_wide"])), combine(*spread(p["e_r"])))])
    sear = line("q_ball", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyWithoutTower", False,
                [ap(p["q_dmg"], p["q_ap"]), ignite(), {"type": "Stun", "duration": p["q_stun"]},
                 buff("q_stun", p["q_stun"]), view("q_hit"), tsfx("q_hit"),
                 pick(1, "EnemyChampion", refresh("q_champ", 20), mark("q"), fp=True)])
    combo_w = pick(p["w_range"], "EnemyChampionInCC", w_cast(), delayed(p["w_rel"], pillar))
    body = combine(delayed(p["e_rel"], sfx("e_cast"), blaze),
                   delayed(p["q_rel"], sfx("q_cast"), voice("vo_q", p), sear))
    skill2 = action("skill2", p["c_dur"], p["c_cd"], 1, p["c_range"], "Targeting", "EnemyChampion", combine(
        *rm("q_champ"), anim("skill2", p["c_dur"]), voice("vo_e", p), body,
        on_me(delayed(p["q_rel"] + p["cw_wait"], sw("q_champ", sw("w_cd", NONE, combo_w))))))

    # ------------------------------------------------------------------ ult: R Pyroclasm
    long_ = p["r_n"] * p["r_gap"] + 60

    def hit(champ):
        out = [ap(p["r_dmg"], p["r_ap"]), ignite(), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
               view("r_hit"), tsfx("r_hit")]
        return out + [mark("r")] if champ else out

    def bounce(champ):
        """On the unit a bounce picked: the fireball falls on it, the hit; whether it was a champion, on him."""
        return [view("r_drop"), sfx("r_bounce"), delayed(p["r_fall"], *hit(champ)),
                on_me(refresh("r_pc", long_) if champ else combine(*rm("r_pc")))]

    def choose():
        """At the first hit's spot: a champion first; after a champion another only when two stand there."""
        return combine(*rm("r_go", "r_skip"),
                       sw("r_pc", sw("r_n2", NONE, flag("r_skip", 1))),
                       sw("r_skip", NONE, pick(p["r_b"], "EnemyChampion", flag("r_go", 1), *bounce(True), fp=True)),
                       sw("r_go", NONE, pick(p["r_b"], "EnemyWithoutTower", *bounce(False), fp=True)))

    hops = None
    for k in range(p["r_n"] - 1, 0, -1):      # innermost (last) bounce first
        end = [choose()] + ([hops] if hops else [])
        hops = lob(f"r_hop{k}", end, travel=p["r_gap"])
    count_c = zone("r_cnt_c", p["r_b"], 1, 1, "EnemyChampion",
                   [on_me(sw("r_n1", refresh("r_n2", long_), refresh("r_n1", long_)))])
    first = homing("r_ball", p["r_speed"], p["r_y"], "EnemyChampion",
                   [*hit(True), on_me(refresh("r_pc", long_)), delayed(1, lob("r_spot", [count_c, hops]))])
    go = combine(anim("ult", p["r_anim"]), cview("r_cast"), sfx("r_cast"), voice("vo_r", p),
                 delayed(p["r_rel"], sfx("r_bounce"), first))
    count_u = lob("r_cnt", [zone("r_cnt_u", p["r_b"], 1, 1, "EnemyWithoutTower",
                                 [on_me(sw("u_1", refresh("u_2", 6), refresh("u_1", 6)))])])
    # the refund waits for the cast to end: a cap laid while the action runs comes before its cooldown starts
    refund = on_me(delayed(6, refresh("r_ref", 3, ult_cooldown_mult=4900)))
    ult = action("ult", 6, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(
        *rm("u_1", "u_2", "r_n1", "r_n2", "r_pc"), count_u, delayed(4, sw("u_2", go, refund))))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # the pillar, the spread and the detonation play as ViewEffects on their points, never turned
    views_p = [P_("a_bolt"), P_("q_ball"), P_("r_ball")]
    views_e = [E("a_hit"), E("w_mark", BIG, -1, False), E("w_pillar", BIG, 2, False), E("w_hit"),
               E("e_flare", BIG, 2, False), E("e_hit"), E("q_hit"), E("r_cast", FX, 2, **LATE), E("r_drop"),
               E("r_hit"), E("p_s1", FX, 3), E("p_s2", FX, 3), E("p_s3", FX, 3), E("p_boom", BIG, 2, False),
               E("p_hit")]
    views_b = [B_("p_burn", FX, 2), B_("p_unstable", FX, 3), B_("q_stun", FX, 3), B_("r_slow", FX, -1)]
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
