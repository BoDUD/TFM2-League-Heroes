"""Build league_malzahar.data_champion (mid, Magician, ranged AP) from the parameters P.

    python tools/kit/build_malzahar.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-14: E + W in skill, Q in skill2, R the ult; voidlings as pictures on the target; the
passive a shield; combos E -> W, R -> Q, Q -> E, R on an E'd champion; the add-on addons/league_malzahar makes E's jump
and the passive exact):
  passive Void Shift (League: 90% less damage from the first hit and no crowd control, back after 30-14 s unhurt by
          champions): every action starts with league_malphite's Granite Shield ladder - the `p_shift` buff
          (duration `WithShield`, `cc_immune`) over a p_sh + p_ap% AP shield; broken, it comes back p_cd ticks later
          (at his first action after that), and every life starts with it.
  attack  a void bolt (homing, physical).
  skill   E Malefic Visions + W Void Swarm: a `Targeting` cast on `EnemyWithoutTower` (e_range) sends the vision
          (homing, e_speed) - on the unit it hits an `AddCasted` (Poison, e_t ticks, a run every e_p) deals
          e_dmg + e_ap% AP magic damage in e_t / e_p equal parts (League: 45-255 + 75% AP over 4 s) - and the voidlings
          ride with it (league_annie Tibbers' way: summons cannot walk or attack in data): an `AddCasted` on the same
          unit bites every w_p ticks for w_t ticks (w_dmg + w_ap% AP magic a bite, the swarm's picture played on him
          every 60 ticks) - so they bite the E'd target first by construction. The vision moves on when its target
          dies (League: to the nearest enemy, refunding the cooldown): every run raises a caster flag `e_alive` for
          e_p + 2 ticks and lobs a hidden 1-tick projectile onto the target; e_p + 3 ticks after it lands, a missing
          `e_alive` (the target did not run the next part: dead) with `e_on` still up (the vision's own time) starts a
          zone on the landing spot that gives a new vision (and voidlings) to one enemy champion within e_jump, else
          to one other enemy (league_lissandra passive's death spot, league_jinx's kill flag). Depth e_jumps (the tree
          is finite); a death in the vision's last run or two is missed; a second vision running at the same time
          can hide a death. The add-on reads deaths natively and moves it at once (+ the refund).
          Q -> E: within q_combo ticks of Q silencing a champion the vision leaves at once (no e_lag wind-up).
  skill2  Q Call of the Void: a `Targeting` cast on `EnemyWithoutTower` (q_range): two rifts open beside the target's
          spot (a hidden 1-tick lob marks it; the rifts' picture is drawn there, upright) and q_lag ticks later the
          beams meet: q_dmg + q_ap% AP magic damage and a q_sil-tick silence (`BlockSkill`) to every enemy within q_r
          of the spot (League: 70-245 + 55% AP, silence 1-2.25 s, 0.6 s + flight). R -> Q: within r_combo ticks of
          the grasp's end the beams meet at once.
  ult     R Nether Grasp: a `Targeting` cast on `EnemyChampion` (r_range). With a vision running on a champion
          (`e_champ`, set by the vision's champion-only twin) it arms `r_armed` for r_wait ticks and the vision's
          champion takes the grasp at his next run (League pros ult the E'd target); else, or if nothing took it by
          then, the action's own target does. The grasp (League: suppression 2.5 s, 125-500 + 80% AP, a 5 s zone): TFM2
          has no suppression, so a stun renewed every r_p ticks while Malzahar channels (`CasterAnimation ult`, flag
          `r_ch`): r_t / r_p waves of r_dmg + r_ap% AP magic damage in equal parts; crowd control on him ends the
          channel at the next check (league_galio R's breaks queued on him) and the stun runs out within r_p ticks.
          Under the target a null zone (r_zone_t ticks, every r_zp ticks z_dmg + z_ap% AP magic damage in r_zr).
          The beam between them (the user: 「大招没连接线啊」): league_nocturne E's chain - every r_lp ticks while the
          channel holds a hidden bolt lands on him, a 1-tick lob on his spot, and from there a link (r_link,
          r_lspeed a tick, r_lspeed x r_lp / 1000 = 16 px long: one beam end to end) flies back to Malzahar.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_malzahar.data_champion")
ID = "league_malzahar"
FX = "asset/league/effects/league_malzahar_fx"
BIG = "asset/league/effects/league_malzahar_big"

# Timing (2026-10-14) from the frames (assets/source/malzahar/frames, tools/art/import_malzahar_strips.py): the attack's
# bolt leaves as frame 3 starts (tick 9 of 26), E's vision on frame 3 (tick 9 of 26), Q's hands meet on frame 3 (tick 9
# of 28: the rifts open), R's start is 21 ticks (4 frames) and its channel loops ult_loop (4 frames, 29 ticks).
# Numbers: the pack's mid mages' stats (league_syndra: hp 860 +92, atk 76 +7, ap 40 +20, def 18, mr 20); candidate d1 of
# the 10-min classic-SDK simulations (Temp/mz_sim, sim/kd.py --lane 2 against the five base mages, both sides, 3
# lineups, 2026-10-14): +1.27 on seeds 1-24, +1.50 on seeds 25-48 (league_syndra +1.62 / +1.53, league_viktor +1.27 /
# +1.68, league_xerath +1.51 / +1.04, league_annie +1.54 / +1.32). The draft d0 (Q 85 + 55%) was +2.69 / +2.24; E and
# the voidlings cut instead (d3: E 140 + 65%, bites 11 + 6%) +1.51 / +1.02, both cut (d4) +0.48 on 12 seeds.
# Retimed to the frames (r1, the same numbers): +1.63 / +1.61 - inside the peers' spread, kept.
P = {
    # stats
    "hp": 860, "hp_g": 92, "atk": 76, "atk_g": 7, "ap": 40, "ap_g": 20, "def": 18, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 910, "ms_g": 9,
    # attack (League 500 range)
    "atk_range": 52000, "atk_dur": 26, "atk_cd": 90, "atk_st": 9, "a_speed": 4500, "a_y": -3000,
    # passive: Void Shift
    "p_sh": 90, "p_ap": 40, "p_cd": 720,
    # 1 = the copy for addons/league_malzahar: its passive league_malzahar:void owns Void Shift as League has it (the
    # first non-minion hit and the p_linger ticks after it lose p_dr %, no crowd control while it holds; back after
    # p_cd ticks without champion damage) and every vision's death watch (its native effect league_malzahar:vision on
    # each unit the bolt hits: dead before e_t is out -> a new vision on the nearest enemy, champions first, e_jump)
    "native": 0, "p_linger": 15, "p_dr": 90,
    # skill: E Malefic Visions (League: 650, 45-255 + 75% AP over 4 s, cd 11-7 s) + W voidlings (League: 8-10 s)
    "e_cd": 540, "e_range": 65000, "e_dur": 26, "e_st": 1, "e_lag": 9, "e_speed": 5000, "e_y": -3000,
    "e_t": 240, "e_p": 15, "e_dmg": 170, "e_ap": 80, "e_jump": 40000, "e_jumps": 1, "e_land": 18,
    "w_t": 240, "w_p": 30, "w_dmg": 14, "w_ap": 8,
    # skill2: Q Call of the Void (League: 900, 70-245 + 55% AP, silence 1-2.25 s, cd 6 s)
    "q_cd": 420, "q_range": 80000, "q_dur": 28, "q_st": 1, "q_wind": 9, "q_lag": 24, "q_r": 18000,
    "q_dmg": 70, "q_ap": 45, "q_sil": 90, "q_combo": 120,
    # ult: R Nether Grasp (League: 700, 2.5 s, 125-500 + 80% AP, zone 5 s; cd 140-80 s)
    "r_cd": 4200, "r_range": 70000, "r_wait": 16, "r_anim": 21, "r_t": 150, "r_p": 15, "r_brk": 10, "r_dmg": 220, "r_ap": 80,
    "r_zone_t": 300, "r_zp": 30, "r_zr": 20000, "z_dmg": 10, "z_ap": 5, "r_combo": 120, "r_lp": 5, "r_lspeed": 3200,
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
    """Effects on him alone, also from a target's or a projectile's list (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Fire"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def drop(name, *end, target="EnemyWithoutTower", hit=()):
    """A hidden one-tick lob onto the unit in hand (league_annie R): its end_effects act on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000,
            "shape": circle(1000), "applied_target": target, "applied_effects": [T(e) for e in hit],
            "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur_, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur_, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Void Shift (Granite Shield's ladder)
    shift = combine(around(1000, "AllyOnlySelf", [{"type": "Shield", "amount": p["p_sh"], "attack_ratio": 0,
                                                   "ap_ratio": p["p_ap"], "tick": 36000}]),
                    flag("p_shift", "WithShield", cc_immune=True), sfx("p_shift"))
    passive = NONE if p["native"] else sw("p_shift", NONE, sw("p_init", sw("p_cd", NONE, sw("p_wait", combine(shift, *rm("p_wait")), combine(
        flag("p_cd", p["p_cd"]), flag("p_wait", "Permanent")))), combine(shift, flag("p_init", "Permanent"))))

    # ------------------------------------------------------------------ ult: R Nether Grasp
    runs = p["r_t"] // p["r_p"]
    # crowd control on him ends the channel at the next check (league_galio R's breaks, one AddCasted on him)
    breaks = casted(p["r_t"], p["r_brk"], pick(1, "AllyChampionInCC", *rm("r_ch"),
                                               {"type": "RemoveCasterAnimation", "name": "ult"},
                                               {"type": "RemoveCasterAnimation", "name": "ult_loop"}), kind="Heal")
    null_zone = {"type": "RangePeriodProjectile", "name": n("r_zone"), "shape": circle(p["r_zr"]), "tick": p["r_zone_t"],
                 "period": p["r_zp"], "first_delay": 0, "applied_target": "EnemyWithoutTower",
                 "applied_effects": [T(magic(p["z_dmg"], p["z_ap"]))], "end_effects": []}

    # the beam: a link from his spot back to Malzahar every r_lp ticks while he channels (league_nocturne E's chain)
    link = sw("r_ch", homing("r_tie", 100000, 0, "EnemyChampion", [
        {"type": "ParabolicProjectile", "name": n("r_spot"), "travel_time": 1, "range": 400000, "shape": circle(0),
         "applied_target": "EnemyChampion", "applied_effects": [],
         "end_effects": [{"type": "BackToCasterLinearProjectile", "name": n("r_link"), "speed": p["r_lspeed"],
                          "range": p["r_range"] + 50000, "penetrate": True, "shape": circle(0),
                          "applied_target": "EnemyChampion", "applied_effects": []}]}]))

    def grasp():
        """On the champion it takes: a stun renewed by every wave while the channel flag holds."""
        # r_grasp: the void's hands round him, a 15-tick loop played by every wave (gone when the channel breaks)
        wave = sw("r_ch", combine({"type": "Stun", "duration": p["r_p"] + 1},
                                  magic(round(p["r_dmg"] / runs), round(p["r_ap"] / runs)), tsfx("r_tick"),
                                  view("r_grasp")))
        return combine(*rm("r_armed"), refresh("r_ch", p["r_t"] + 1), sfx("r_cast"), sfx("vo_r"),
                       wave, casted(p["r_t"] - 1, p["r_p"], wave), link, casted(p["r_t"] - 1, p["r_lp"], link),
                       drop("r_drop", view("r_pool"), sfx("r_pool"), null_zone),
                       on_me(anim("ult", p["r_anim"]), delayed(p["r_anim"], sw("r_ch", anim("ult_loop", p["r_t"] - p["r_anim"]))),
                             breaks, delayed(p["r_t"], refresh("r_combo", p["r_combo"]))))

    # ------------------------------------------------------------------ skill: E Malefic Visions + W voidlings
    runs_e = p["e_t"] // p["e_p"]

    def swarm():
        return combine(casted(p["w_t"], p["w_p"], magic(p["w_dmg"], p["w_ap"]), view("w_bite"), tsfx("w_bite")),
                       casted(p["w_t"], 60, view("w_swarm")), view("w_spawn"), tsfx("w_spawn"))

    def vision(depth):
        """On the unit the vision reaches: the burn, the voidlings, the death watch (jump while depth < e_jumps)."""
        part = [magic(round(p["e_dmg"] / runs_e), round(p["e_ap"] / runs_e))]
        if depth < p["e_jumps"] and not p["native"]:
            part += [refresh("e_alive", p["e_p"] + 2),
                     drop("e_watch", delayed(p["e_p"] + 3, sw("e_on", sw("e_alive", NONE, jump(depth + 1)))))]
        watch = [{"type": "Native", "effect_ref": f"{ID}:vision"}] if p["native"] else []
        return combine(refresh("e_on", p["e_t"]), casted(p["e_t"], p["e_p"], *part, kind="Poison"),
                       casted(p["e_t"], 60, view("e_mark")), view("e_hit"), tsfx("e_hit"), swarm(), *watch)

    def champ():
        """On a champion the vision reaches (its champion-only twin): R takes him while r_armed."""
        return combine(refresh("e_champ", p["e_t"]), casted(p["e_t"], p["e_p"], sw("r_armed", grasp()), kind="Fire"))

    def jump(depth):
        """On the dead target's spot: one enemy champion within e_jump, else one other enemy, takes a new vision."""
        once = lambda *extra: sw("e_got", NONE, combine(flag("e_got", 2), vision(depth), *extra))
        return combine(*rm("e_got", "e_on"), zone("e_jump_c", p["e_jump"], "EnemyChampion", [once(champ())]),
                       zone("e_jump_o", p["e_jump"], "EnemyWithoutTower", [once()], delay=2), sfx("e_jump"))

    def throw():
        return combine(sfx("e_cast"), sfx("vo_e"),
                       homing("e_twin", p["e_speed"], p["e_y"], "EnemyChampion", [champ()]),
                       homing("e_bolt", p["e_speed"], p["e_y"], "EnemyWithoutTower", [vision(0)]))
    # every unit takes the visible bolt's vision; a champion also the twin's grasp hook
    skill = action("skill", p["e_dur"], p["e_cd"], p["e_st"], p["e_range"], "Targeting", "EnemyWithoutTower", flat(combine(
        passive, anim("skill", p["e_dur"]), sw("q_hit", combine(*rm("q_hit"), throw()), delayed(p["e_lag"], throw())))))

    # ------------------------------------------------------------------ skill2: Q Call of the Void
    def beams(lag):
        hit = [magic(p["q_dmg"], p["q_ap"]), {"type": "BlockSkill", "tick": p["q_sil"]}, view("q_hit"), tsfx("q_hit")]
        champ = [refresh("q_hit", p["q_combo"])]
        return drop("q_mark", view("q_rift"), delayed(lag, sfx("q_close"),
                                                       zone("q_beam", p["q_r"], "EnemyWithoutTower", hit),
                                                       zone("q_champ", p["q_r"], "EnemyChampion", champ)))
    skill2 = action("skill2", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower", flat(combine(
        passive, anim("skill2", p["q_dur"]), sfx("vo_q"),
        delayed(p["q_wind"], sfx("q_cast"), sw("r_combo", combine(*rm("r_combo"), beams(2)), beams(p["q_lag"]))))))

    # ------------------------------------------------------------------ ult action
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", flat(combine(
        passive, sw("e_champ", combine(refresh("r_armed", p["r_wait"] + 2), delayed(p["r_wait"], sw("r_armed", grasp()))),
                    grasp()))), key="ult")

    # ------------------------------------------------------------------ attack
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        passive, sfx("a_cast"), homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"),
                                                                                   tsfx("a_hit")]))),
        atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    # the null zone has no picture of its own (a zone's picture turns with the cast: upside down cast leftward); its
    # ground picture r_pool is a ViewEffect where the lob lands (never turned)
    views_p = [P_("a_bolt"), P_("e_bolt"), P_("r_link")]
    views_e = [E("a_hit", FX, 2), E("e_hit", FX, 2), E("e_mark", FX, 2), E("w_spawn", FX, 2), E("w_swarm", FX, -1),
               E("w_bite", FX, 2), E("q_rift", BIG, 2, False), E("q_hit", FX, 2), E("r_grasp", BIG, 2),
               E("r_pool", BIG, -2, False)]
    # e_markb: the add-on's jumped vision (a buff picture: pictures played from native code never showed in game)
    views_b = [P_("p_shift", FX, 2), {"type": "Animated", "name": n("e_markb"), "anim": FX, "tag": "e_mark",
                                      "repeat": True, "z": 2}]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": f"{ID}:void",
                            "params": {k: p[k] for k in ("p_cd", "p_linger", "p_dr", "e_t", "e_p", "e_dmg", "e_ap",
                                                         "e_jump")}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
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
