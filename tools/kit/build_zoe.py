"""Build league_zoe.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_zoe.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-19: mid, layout A, with the add-on). TFM2 has three active slots: Paddle Star (Q) is
`skill`, Sleepy Trouble Bubble (E) `skill2`, Portal Jump (R) the `ult` and it throws a Paddle Star from the portal;
Spell Thief (W) has no slot - its missiles fly with every R (her "summoner spell" here).
  passive More Sparkles! (烟火四射！): each Q / E / R she casts lights `p_on` (p_t ticks); the next attack then deals
          p_dmg + p_ratio% AP more (Empowered_Attack's pose, `attack_p`).
  attack  a little star (100% AD), homing on `Enemy` (towers too), released on a_rel.
  skill   Q Paddle Star (飞星乱入！), `Targeting` on `EnemyWithoutTower` (q_range): a star flies straight at the target
          (non-penetrating, the first enemy on the line takes it). League's damage grows with the distance flown; data
          reads no distance, so the flight is timed: `q_n1` / `q_n2` caster flags laid at the release last q_d1 / q_d2
          worth of flight, and the hit deals the near (100%), middle (q_mid%) or far (q_far%) share of q_dmg +
          q_ratio% AP by which of them is still on. Its picture is a round star (symmetric every way).
  skill2  E Sleepy Trouble Bubble (催眠气泡), `Targeting` on `EnemyChampion` (e_range): a bubble flies at the target
          (champions only, non-penetrating): e_dmg + e_ratio% AP, drowsy (e_slow% for e_drowsy ticks), then asleep
          (a `Stun` of e_sleep ticks, the Zz picture). A bubble that reaches its end without a hit stays there as a trap
          for e_trap ticks (League's bubble lands and waits): the first enemy champion stepping in gets the same.
          Waking: while the target sleeps (caster flags `e_wait` off, `e_win` on), her first Q or R star on a champion
          deals its damage again (League doubles the first hit, capped) and ends the window. Damage breaking the sleep
          is the add-on's (League: any damage wakes).
  ult     R Portal Jump (折返跃迁), `Targeting` on `EnemyChampion` (r_range): an anchor holds the spot she stood on
          (league_ekko R's anchor), she jumps through a portal up to r_jump toward the target (a hidden line that stops
          about r_stop short of the first champion, `end_effects: [Teleport]`, league_ezreal E's blink), throws a
          Paddle Star from there at the far share's damage (r_dmg + r_ratio% AP, champions only), Spell Thief's three
          missiles follow (her toss `skill_w`, w_dmg + w_ratio% AP each, at the nearest enemies) and she gets w_ms% move
          speed for w_ms_t; r_back ticks after the jump she springs up out of the far end (`ult_exit`, r_exit ticks)
          and the anchor pulls her back (`ult_back`; death cancels it).
The add-on copy (--native, addons/league_zoe): the passive league_zoe:sparkles reads the hits - any damage wakes the
sleeper and its first hit is doubled (capped), Paddle Star scales with the real distance flown, and Spell Thief's
shards: an enemy champion's ult drops one where he stood; when she walks over it she fires the three missiles.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_zoe.data_champion")
ID = "league_zoe"
FX = "asset/league/effects/league_zoe_fx"
BIG = "asset/league/effects/league_zoe_big"

# League units x 100 = ours (attack range 550 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings from the strips (tools/art/rig_zoe.py MS): the attack's flick frame 3 from tick 9 (a_rel 10),
# Q's throw frame 4 from 12.6 (q_rel 13), E's kick frame 4 from 13.2 (e_rel 13), R's leap frame 2 from 4.8 (r_rel 8),
# the landing at 26 (r_throw 19 after the jump), W's toss frame 2 from 3.6 (w_rel 4) 22 ticks into the throw (after
# Q's held-low frame), the exit leap 200 ms (r_exit 12); r_back = r_throw + r_w + w_dur + r_exit. Numbers = the 10-min classic-SDK
# simulations (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both
# sides, 8 seeds, 2026-10-19): the draft (hp 880, Q 70 + 50% x1 / 1.6 / 2.2, P 30 + 40%, R 170 + 80% every 40 s landing
# 40000 short, W 35, sleep 1.5 s) -1.37 (league_ziggs +1.70 the same batch); Q 90 + 60%, R 50000 short, sleep 1.75 s
# +0.67; + hp 920, R every 30 s, W 45 +0.36; + Q x1.7 / 2.5, P 40 + 50% +1.07 / +1.18 (seeds 9-16); Q 105 +1.41 / +1.47
# = P (sleep 2 s with hp 960 the same, +1.48 / +1.44).
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Zoe:
    # 630 +106 hp, 21 armour, 30 mr, 340 move, 550 range, attack speed 0.658
    "hp": 920, "hp_g": 95, "atk": 76, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 920, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 88, "a_rel": 10, "a_speed": 4500,
    # passive More Sparkles! (League: 16-130 +20% AP on the next attack after a spell)
    "p_t": 300, "p_dmg": 40, "p_ratio": 50,
    # Q Paddle Star (League: 50-250 +60% AP, up to +150% by the distance flown, cd 8.5-6, missile 1200 -> 2500)
    "q_cd": 360, "q_range": 80000, "q_dur": 30, "q_rel": 13, "q_speed": 4000, "q_len": 95000, "q_w": 6000,
    "q_d1": 30000, "q_d2": 60000, "q_dmg": 105, "q_ratio": 60, "q_mid": 170, "q_far": 250,
    # E Sleepy Trouble Bubble (League: 800 range, 70-270 +45% AP, drowsy 1.4 s (slow 10-35%), sleep 2.25 s, trap
    # 5 s, cd 18-14)
    "e_cd": 900, "e_range": 75000, "e_dur": 27, "e_rel": 13, "e_speed": 3500, "e_len": 85000, "e_w": 7000,
    "e_dmg": 60, "e_ratio": 40, "e_slow": 30, "e_drowsy": 84, "e_sleep": 105, "e_trap": 300, "e_trap_r": 12000,
    "e_show": 15,
    # R Portal Jump (League: blink 575 for 1 s, cd 11-5) + the portal's Paddle Star (far share) + W Spell Thief's
    # missiles (League: 3 x 25-95 +33% AP, move speed 30-80% for 2-3.25 s)
    "r_cd": 1800, "r_range": 110000, "r_dur": 27, "r_rel": 8, "r_jump": 57500, "r_jspeed": 6000, "r_stop": 50000,
    "r_throw": 19, "r_speed": 5000, "r_len": 110000, "r_dmg": 170, "r_ratio": 80, "r_back": 72, "r_back_dur": 18,
    "r_exit": 12, "r_w": 22,
    "w_n": 3, "w_dur": 19, "w_rel": 4, "w_gap": 5, "w_dmg": 45, "w_ratio": 15, "w_speed": 4000, "w_ms": 40,
    "w_ms_t": 150,
    "vo_gap": 600,
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


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action: its estimate follows a SwitchByBuff by the flags she has while
    it reads, so a hit under alive() reads as nothing - and its battle plan divides an enemy's health by her attack's
    estimate (champion-data: "attempt to divide by zero", battle.rs:1938; league_gangplank's decoy). A flag she never
    has while it reads; on the cast the flag is up and the hit is skipped."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def trap(name, radius, tick, effects, target="EnemyChampion"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": 3,
            "first_delay": 3, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])
    spark = refresh("p_on", p["p_t"])       # More Sparkles! lit by every cast

    # ------------------------------------------------------------------ attack: the little star / the sparkly one
    plain = combine(sfx("a"), homing("a_star", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"]))
    sparkly = combine(*rm("p_on"), anim("attack_p", p["atk_dur"]), sfx("p"),
                      homing("p_star", "Enemy", [attack(0, 100), ap(p["p_dmg"], p["p_ratio"]), view("p_hit"),
                                                 tsfx("p_hit")], p["a_speed"]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(sw("p_on", sparkly, plain)))),
                      atype="BaseAttack", cancel=True)

    # waking: her first Q / R star on a champion while the target sleeps deals the hit again
    def wake(dmg, ratio):
        return sw("e_wait", NONE, sw("e_win", combine(*rm("e_win"), ap(dmg, ratio), view("e_wake"), tsfx("e_wake"))))

    # ------------------------------------------------------------------ skill: Q Paddle Star
    def share(pct):
        return p["q_dmg"] * pct // 100, p["q_ratio"] * pct // 100

    def by_distance(on_hit):
        """near / middle / far by which flight flag is still on (laid at the release)."""
        return sw("q_n1", on_hit(*share(100)), sw("q_n2", on_hit(*share(p["q_mid"])), on_hit(*share(p["q_far"]))))

    hit_q = by_distance(lambda d, r: combine(ap(d, r), view("q_hit"), tsfx("q_hit")))
    star = line("q_star", p["q_speed"], p["q_len"], p["q_w"], "EnemyWithoutTower", [hit_q])
    # the wake on a champion rides a hidden twin (a minion taking the star does not wake anyone)
    twin = line("q_twin", p["q_speed"], p["q_len"], p["q_w"], "EnemyChampion", [by_distance(wake)], y=5000)
    throw_q = combine(flag("q_n1", max(1, p["q_d1"] // p["q_speed"])), flag("q_n2", max(1, p["q_d2"] // p["q_speed"])),
                      star, sw("e_win", twin))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), spark, sfx("q"), voice("vo_q", p), delayed(p["q_rel"] - 1, alive(*rm("q_n1", "q_n2"),
                                                                                            throw_q, sfx("q_fly")))))

    # ------------------------------------------------------------------ skill2: E Sleepy Trouble Bubble
    slow = buff("e_drowsy", p["e_drowsy"], move_speed_mult=-p["e_slow"])
    asleep = delayed(p["e_drowsy"], {"type": "Stun", "duration": p["e_sleep"]}, buff("e_zz", p["e_sleep"]),
                     tsfx("e_sleep"))
    bubble_hit = [refresh("e_got", 2), refresh("e_wait", p["e_drowsy"]), refresh("e_win", p["e_drowsy"] + p["e_sleep"]),
                  ap(p["e_dmg"], p["e_ratio"]), slow, asleep, view("e_hit"), tsfx("e_hit")]
    caught = [sw("e_tdone", NONE, combine(flag("e_tdone", p["e_trap"]), *bubble_hit, sfx("e_pop")))]
    lying = [delayed(k, sw("e_tdone", NONE, view("e_trap"))) for k in range(0, p["e_trap"], p["e_show"])]
    left = sw("e_got", combine(*rm("e_got")), combine(trap("e_field", p["e_trap_r"], p["e_trap"], caught), *lying))
    bubble = line("e_bubble", p["e_speed"], p["e_len"], p["e_w"], "EnemyChampion", bubble_hit, end=[left])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), spark, sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(*rm("e_got", "e_tdone"), bubble, sfx("e_fly")))))

    # ------------------------------------------------------------------ ult: R Portal Jump + the portal's star + W
    star_r = line("r_star", p["r_speed"], p["r_len"], p["q_w"], "EnemyChampion",
                  [ap(p["r_dmg"], p["r_ratio"]), view("q_hit"), tsfx("q_hit"), wake(p["r_dmg"], p["r_ratio"])])
    if p["r_throw"] + p["r_w"] + p["w_dur"] > p["r_back"] - p["r_exit"]:
        raise SystemExit("the W toss must end before the exit leap")
    missiles = [delayed(p["w_rel"] - 1 + p["w_gap"] * k, alive(sfx("w_shot"), homing(
        "w_missile", "EnemyWithoutTower", [ap(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")], p["w_speed"])))
        for k in range(p["w_n"])]
    # the portal's star leaves on Paddle Star's throw frame; Spell Thief's toss (`skill_w`) follows the throw
    throw_r = combine(anim("skill", p["q_dur"]), sfx("q"), delayed(p["q_rel"] - 1, alive(star_r, sfx("q_fly"))),
                      delayed(p["r_w"], alive(anim("skill_w", p["w_dur"]), *missiles,
                                              refresh("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"]))))
    jump = line("r_jump", p["r_jspeed"], p["r_jump"], p["r_stop"], "EnemyChampion", [],
                end=[{"type": "Teleport"}, cview("r_portal_out")], y=5000)
    back = sw("r_on", combine(*rm("r_on"), cview("r_portal_back"), {"type": "Teleport"},
                              anim("ult_back", p["r_back_dur"]), sfx("r_back")))
    leave = sw("r_on", anim("ult_exit", p["r_exit"]))      # she springs up out of the far end first
    anchor = line("r_anchor", 1, 1, 1000, "EnemyChampion", [], end=[delayed(p["r_back"] - 1 - p["r_exit"], alive(leave)),
                                                                     delayed(p["r_back"] - 1, alive(back))], y=5000)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), spark, sfx("r"), voice("vo_r", p), refresh("r_on", p["r_rel"] + p["r_back"] + 10),
                         delayed(p["r_rel"] - 1, alive(cview("r_portal_in"), anchor, jump)),
                         delayed(p["r_rel"] - 1 + p["r_throw"], alive(throw_r))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    # a projectile's picture is turned with its flight: stars, the bubble and the missiles are round
    views_p = [Pj("a_star"), Pj("p_star"), Pj("q_star"), Pj("r_star", "q_star"), Pj("e_bubble"), Pj("w_missile")]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("e_hit"), E("e_wake"), E("e_trap", BIG, -1, False),
               E("w_hit"), E("r_portal_in", BIG, 3, False), E("r_portal_out", BIG, 3, False),
               E("r_portal_back", BIG, 3, False)]
    views_b = [B_("e_drowsy", FX, 3), B_("e_zz", FX, 3), B_("w_haste", FX, -1)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_zoe:sparkles", "params": {
            "q_d1": p["q_d1"], "q_d2": p["q_d2"], "q_far": p["q_far"], "e_sleep": p["e_sleep"],
            "w_dmg": p["w_dmg"], "w_ratio": p["w_ratio"]}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
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
