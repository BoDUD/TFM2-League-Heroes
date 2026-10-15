"""Build league_katarina.data_champion (mid, Assassin, melee AP) from the parameters P.

    python tools/kit/build_katarina.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-15: mid AP assassin; skill = Q + Shunpo onto the dagger, skill2 = W + Shunpo in first;
E owns no slot, its cooldown is a caster flag; the add-on addons/league_katarina; the pros' combos; PPU 1.5):
  passive Voracity (贪婪): an enemy champion she damaged dies within p_win ticks (by anyone's hand) -> Q's and W's
          cooldowns are capped to nothing (a 2-tick `skill_cooldown_mult` p_cdr, `ult_cooldown_mult` -p_cdr keeps the
          ult's) and Shunpo's flag `e_cd` goes. The takedown window is league_viego's (champion-data "A takedown
          window"): every champion hit puts an `AddCasted` on the champion keeping a 2-tick flag `p_alive` up while he
          lives and a watcher on her; the flag lapsing inside the window = a takedown. One reset per window (`p_lock`);
          the add-on sees every death.
          Sheathed Blades (匕首): a dagger lies d_life ticks where it lands (Q behind the first target, W at her feet);
          walking over it (pick_r) picks it up: the spin - p_dmg + p_ap% AP magic damage to every enemy within p_r - and
          Shunpo's remaining cooldown drops to e_short ticks (League: -78%). Three daggers may lie at once (flags
          dag_a / dag_b / dag_c, the next slot by gen_a / gen_b). The spin's own effects run from a watcher her attack
          hangs on her (`AddCasted`, period 1: the pick only raises `spin_go`), so the per-tick copy of the Q and W
          trees stays small (champion-data, skill-tree size).
  attack  The dagger stab, the hit on tick atk_st (physical).
  skill   Q Bouncing Blade (弹射之刃) + Shunpo onto the dagger: a `Targeting` cast on `EnemyWithoutTower` (q_range). On
          tick q_at the spinning blade flies at the target (homing): q_dmg + q_ap% AP magic damage, then q_bn bounces
          q_blag ticks apart to a unit within q_b of the one it hit (a `RandomTarget`: it may take the same unit again).
          The dagger lands q_fall ticks after the blade struck, on the spot the first target stood (a hidden lob
          from her; League: 350 behind it, ~1 s later); with Shunpo ready and an enemy within p_r of the dagger
          she blinks onto it at once (`Teleport` from the landing's own `Delayed`) and picks it up.
  skill2  W Preparation (伺机待发) + Shunpo in: a `Targeting` cast on `EnemyChampion` (w_range). With Shunpo ready she
          first blinks onto the champion (`Teleport`; e_dmg + e_ap% AP magic damage) and `e_cd` starts; then she tosses
          a dagger up: it lands at her feet w_fall ticks later (a 1-tick anchor at her feet, its landing a `Delayed`
          there), and she gains w_ms% move speed fading in three steps over w_fall ticks.
  ult     R Death Lotus (死亡莲华): a `Targeting` cast on `EnemyChampionRecentlyAttacked` (r_range). She channels r_t
          ticks (`CasterAnimation` holds her): every r_p ticks a dagger flies at each enemy champion within r_r: r_dmg +
          r_ap% AP magic damage in r_t / r_p equal parts and r_gw% healing cut (grievous wounds) for r_gw_t. Crowd
          control on her ends the channel at the next check (league_malzahar R's breaks); so does nobody in reach for
          two volleys running (the champions walked out: League's player would move on). Cast only within r_range
          (30000: after Shunpo in, League's pros' E-W-R).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_katarina.data_champion")
ID = "league_katarina"
FX = "asset/league/effects/league_katarina_fx"
BIG = "asset/league/effects/league_katarina_big"

# Timings are placeholders until the strips (the attack's stab on tick 8, Q's throw on 8, W's toss on 8).
P = {
    # stats (the pack's mid assassins: league_talon hp 930 +88, atk 122 +25, def 26 +8, mr 18 +4, ms 1100 +13)
    "hp": 1020, "hp_g": 86, "atk": 105, "atk_g": 13, "ap": 40, "ap_g": 22, "def": 32, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1100, "ms_g": 13,
    # attack (League 125 range)
    "atk_range": 23000, "atk_dur": 24, "atk_cd": 55, "atk_st": 8,
    # passive Voracity (League: takedown within 3 s -> basic cooldowns -15 s)
    "p_win": 180, "p_cdr": 10000,
    # Sheathed Blades (League: 340 radius, 68-308 + 60% bonus AD + 70-100% AP; Shunpo -78%; daggers last 4 s)
    "d_life": 240, "d_step": 40, "pick_r": 9000, "p_r": 30000, "p_dmg": 110, "p_ap": 80, "p_anim": 12,
    # skill: Q Bouncing Blade (League: 625, 80-200 + 35% AP, 2 bounces, the dagger lands 350 behind ~1.1 s later)
    "q_cd": 480, "q_range": 62500, "q_dur": 24, "q_at": 8, "q_speed": 5000, "q_y": -3000, "q_dmg": 120, "q_ap": 50,
    "q_bn": 2, "q_b": 30000, "q_blag": 6, "q_fall": 40,
    # E Shunpo (League: 725, 20-80 + 40% AD + 25% AP, cd 14-8 s)
    "e_cd": 600, "e_short": 120, "e_dmg": 60, "e_ap": 30, "e_anim": 8,
    # skill2: W Preparation (League: 50-90% move speed fading over 1.25 s, the dagger lands after 1.25 s, cd 15-11 s)
    "w_cd": 660, "w_range": 55000, "w_dur": 20, "w_at": 6, "w_fall": 75, "w_ms": 60,
    # ult: R Death Lotus (League: 550 radius, 2.5 s, 15 daggers at up to 3 champions, 25-50 + 19% AP each, 60% GW)
    "r_cd": 3600, "r_range": 30000, "r_tgt": "EnemyChampion", "r_r": 50000, "r_t": 150, "r_p": 10, "r_brk": 10, "r_dmg": 520, "r_ap": 280,
    "r_gw": 60, "r_gw_t": 180, "r_speed": 6000, "r_y": -3000, "r_track": 30, "r_ring": 30,
    # voice
    "vo_gap": 240,
    # 1 = the copy for addons/league_katarina: no takedown window (its passive league_katarina:blades resets Q, W and
    # Shunpo on every kill and assist) and Shunpo onto the daggers on the ground when it decides (e_low: % health
    # under which it blinks away instead)
    "native": 0, "e_low": 30,
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


def dur(tick):
    return tick if isinstance(tick, (str, dict)) else {"Time": {"tick": tick}}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields},
            "only_to_enemy": False}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields}}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


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


def magic(dmg, ap):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": 0, "can_crit": False}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a target's or a projectile's list (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, end, target="EnemyWithoutTower"):
    """A hidden line that hits nothing: its end_effects act on the point it stops at."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(1), "y_offset": 0}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden lob from her onto the unit in hand: its end_effects act on the spot it lands on."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 1000000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def pzone(name, r, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(r), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur_, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur_, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Voracity (the takedown window)
    def reset():
        """A takedown: Q and W ready, Shunpo ready; one per window."""
        cdr = {"skill_cooldown_mult": p["p_cdr"], "ult_cooldown_mult": -p["p_cdr"]}
        return combine(refresh("p_lock", p["p_win"]), refresh("p_alive", p["p_win"]), refresh("p_cdr", 2, **cdr),
                       *rm("e_cd"), cview("p_reset"), sfx("reset"))

    watch = sw("p_alive", NONE, sw("p_lock", NONE, reset()))

    def track():
        """On a champion she hit: keeps p_alive up while he lives; a watcher on her sees it lapse = a takedown (the
        add-on's copy reads kills and assists natively instead)."""
        if p["native"]:
            return NONE
        return combine(casted(p["p_win"], 1, refresh("p_alive", 2)),
                       on_me(refresh("p_alive", 3), casted(p["p_win"] - 2, 1, watch)))

    # ------------------------------------------------------------------ Sheathed Blades: the daggers and the spin
    def spin():
        """The pick-up: a slash round her, Shunpo's cooldown cut (run by the watcher on her)."""
        return combine(around(p["p_r"], "EnemyWithoutTower", [magic(p["p_dmg"], p["p_ap"]), view("p_hit")]),
                       around(p["p_r"], "EnemyChampion", [track()]), anim("spin", p["p_anim"]), cview("spin"),
                       sfx("pick"), sw("e_cd", combine(*rm("e_cd"), flag("e_cd", p["e_short"]))))

    # the watcher every action of hers hangs on her (at most one at a time): the spin's effects live here, not in the Q / W trees
    arm = sw("watch", NONE, combine(flag("watch", 598), on_me(casted(600, 1, sw("spin_go", combine(*rm("spin_go"),
                                                                                                      spin()))))))

    def stuck(g):
        """On the dagger's landing point: the fall, the dagger in the ground while dag_<g> holds, the pick-up zone."""
        got = pick(p["pick_r"], "AllyOnlySelf", sw(f"dag_{g}", combine(*rm(f"dag_{g}"), refresh("spin_go", 3))),
                   fp=True)
        shown = [delayed(t, sw(f"dag_{g}", view("d_stuck"))) for t in range(p["d_step"], p["d_life"], p["d_step"])]
        return [view("d_fall"), sfx("q_land"), view("d_stuck"),
                pzone("d_zone", p["pick_r"], p["d_life"], 3, "AllyChampion", [got]), *shown]

    def dagger(make):
        """The next of three dagger slots; make(g, landing effects) throws it."""
        def go(g):
            return combine(refresh(f"dag_{g}", p["d_life"] + p["w_fall"] + p["q_fall"]), make(g, stuck(g)))
        return sw("gen_b", combine(*rm("gen_a", "gen_b"), go("c")),
                  sw("gen_a", combine(*rm("gen_a"), flag("gen_b", "Permanent"), go("b")),
                     combine(flag("gen_a", "Permanent"), go("a"))))

    # ------------------------------------------------------------------ E Shunpo
    def blink_out():
        return combine(cview("e_out"), sfx("e_blink"), voice("vo_e", p), refresh("e_cd", p["e_cd"]))

    def blink_in():
        return combine(cview("e_in"), anim("blink", p["e_anim"]))

    # ------------------------------------------------------------------ skill: Q Bouncing Blade (+ Shunpo onto it)
    hit_q = [magic(p["q_dmg"], p["q_ap"]), view("q_hit"), tsfx("q_hit")]
    bounces = [delayed(p["q_blag"] * (k + 1), pick(p["q_b"], "EnemyWithoutTower", *hit_q, fp=True))
               for k in range(p["q_bn"])]
    twin = homing("q_twin", p["q_speed"], p["q_y"], "EnemyChampion", [track()])
    # Shunpo onto the landed dagger: an enemy near it (a zone at the point raises qe_go) and e_cd off
    qe = [zone("qe_probe", p["p_r"], "EnemyWithoutTower", [refresh("qe_go", 4)]),
          delayed(2, sw("qe_go", sw("e_cd", NONE, combine(*rm("qe_go"), blink_out(), {"type": "Teleport"},
                                                             on_me(blink_in())))))]

    def q_dagger(g, land):
        """A hidden lob from her onto the spot the blade struck (League: 350 behind the first target), q_fall ticks."""
        return lob("q_dagger", p["q_fall"], land + qe)

    blade = homing("q_blade", p["q_speed"], p["q_y"], "EnemyWithoutTower",
                   hit_q + [view("q_arc"), sfx("q_arc"), dagger(q_dagger)] + bounces)

    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", flat(combine(
        arm, anim("skill", p["q_dur"]), voice("vo_q", p),
        delayed(p["q_at"] - 1, sfx("q_cast"), sfx("q_blade"), blade, twin))))

    # ------------------------------------------------------------------ skill2: W Preparation (+ Shunpo in)
    def w_dagger(g, land):
        return line("w_anchor", 1, 1, [delayed(p["w_fall"], *land)])

    third = p["w_fall"] // 3
    haste = combine(refresh("w_ms", third, move_speed_mult=p["w_ms"]),
                    delayed(third, refresh("w_ms", third, move_speed_mult=p["w_ms"] * 2 // 3)),
                    delayed(2 * third, refresh("w_ms", third, move_speed_mult=p["w_ms"] // 3)))

    def tossed(lag):
        """Her toss lag ticks into the action: the throw's picture and sound."""
        return combine(anim("skill2", p["w_dur"]) if lag == 0 else NONE,
                       delayed(lag + p["w_at"] - 1, cview("w_toss"), sfx("w_toss")))

    shunpo_in = combine(blink_out(), {"type": "Teleport"}, magic(p["e_dmg"], p["e_ap"]), view("e_hit"), tsfx("e_hit"),
                        track(), on_me(blink_in(), delayed(p["e_anim"], anim("skill2", p["w_dur"]))), tossed(p["e_anim"]))
    # one dagger in the tree (the per-tick copy of skill2 stays small): its anchor leaves e_anim + w_at ticks in either
    # way - without the blink she stands in the toss meanwhile, on the same spot
    skill2 = action("skill2", p["w_dur"] + p["e_anim"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    flat(combine(arm, sw("e_cd", tossed(0), shunpo_in), voice("vo_w", p), haste,
                                 delayed(p["e_anim"] + p["w_at"] - 1, dagger(w_dagger)))))

    # ------------------------------------------------------------------ ult: R Death Lotus
    runs = p["r_t"] // p["r_p"]
    breaks = casted(p["r_t"], p["r_brk"], pick(1, "AllyChampionInCC", *rm("r_ch"),
                                               {"type": "RemoveCasterAnimation", "name": "ult"}))
    knife = homing("r_dagger", p["r_speed"], p["r_y"], "EnemyChampion",
                   [magic(round(p["r_dmg"] / runs), round(p["r_ap"] / runs)),
                    buff("r_gw", p["r_gw_t"], heal_reduce=p["r_gw"]), view("r_hit"), tsfx("r_hit")])
    # every volley that finds a champion keeps r_seen up two volleys long; a check every r_p ticks from the second
    # volley on ends the channel when it lapsed (nobody in reach twice running: the champions walked out - League's
    # player would move and cancel it; the AI would stand there spinning at nothing)
    volley = sw("r_ch", around(p["r_r"], "EnemyChampion", [knife, refresh("r_seen", 2 * p["r_p"] + 1)]))
    stop = combine(*rm("r_ch"), {"type": "RemoveCasterAnimation", "name": "ult"})
    idle_end = sw("r_ch", sw("r_seen", NONE, stop))
    marks = sw("r_ch", around(p["r_r"], "EnemyChampion", [track()]))
    ring = sw("r_ch", cview("r_lotus"))
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", p["r_tgt"], flat(combine(
        arm, refresh("r_ch", p["r_t"] + 1), anim("ult", p["r_t"]), sfx("r_lotus"), sfx("vo_r"),
        on_me(volley, casted(p["r_t"] - 1, p["r_p"], volley), marks, casted(p["r_t"] - 1, p["r_track"], marks),
              ring, casted(p["r_t"] - 1, p["r_ring"], ring), breaks,
              delayed(2 * p["r_p"] - 1, idle_end, casted(p["r_t"] - 2 * p["r_p"], p["r_p"], idle_end))))), key="ult")

    # ------------------------------------------------------------------ attack
    a_twin = homing("a_twin", 100000, 0, "EnemyChampion", [track()])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        arm, sfx("a_swing"), attack(0, 100), view("a_hit"), tsfx("a_hit"), a_twin)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    # the hidden lob (q_dagger), the anchor (w_anchor) and the twins have no picture
    views_p = [P_("q_blade"), P_("r_dagger")]
    views_e = [E("a_hit", FX, 2), E("q_hit", FX, 2), E("q_arc", FX, 2, False), E("d_fall", FX, 1, False),
               E("d_stuck", FX, -1, False), E("p_hit", FX, 2), E("spin", BIG, 2, False), E("e_out", FX, 2, False),
               E("e_in", FX, 2, False), E("e_hit", FX, 2), E("w_toss", FX, 2, False), E("p_reset", FX, 2),
               E("r_hit", FX, 2), E("r_lotus", BIG, 2)]
    views_b = [P_("w_ms", FX, -1), P_("r_gw", FX, 2)]
    extra = {}
    if p["native"]:
        e_range = p["w_range"] + 17500          # League's Shunpo reach (725) over W's cast range
        extra["passive"] = {"passive_ref": f"{ID}:blades",
                            "params": {**{k: p[k] for k in ("e_cd", "e_dmg", "e_ap", "e_anim", "e_low", "p_r", "pick_r",
                                                             "d_life", "vo_gap")}, "e_range": e_range}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Melee"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
