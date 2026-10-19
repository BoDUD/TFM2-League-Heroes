"""Build league_yuumi.data_champion (support, Util, the cat on a book) from the parameters P.

    python tools/kit/build_yuumi.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-19: support, layout A, the main pack's banish attach, an add-on for the real one):
TFM2 has three active slots: Prowling Projectile (Q) is `skill`, You and Me! (W) with Zoomies (E) folded in `skill2`,
Final Chapter (R) the `ult`.
  passive Feline Friendship (猫的博爱): every p_cd ticks her attack on a champion (a champion-only twin of the bolt)
          deals p_dmg + p_ap% AP more, heals her p_heal + p_hap% AP and keeps that heal (`p_carry`) for the next ally
          she attaches to.
  attack  a little book bolt (100% AD), homing on `Enemy` (towers too), released on start_timing.
  skill   Q Prowling Projectile (摸鱼飞弹), `Targeting` on `EnemyWithoutTower` (q_range): a missile flies straight at the
          target and stops on the first enemy (non-penetrating): q_dmg + q_ap% AP and q_slow% for q_slow_t. League's
          missile is empowered after 1.35 s of flight; data reads no distance, so the flight is timed: the caster flag
          `q_near` laid at the release lasts q_t1 ticks; a hit after it ends deals q_edmg + q_eap% AP and slows
          q_eslow% for q_eslow_t.
  skill2  W You and Me! (悠米出动！) + E Zoomies (旺盛精力), `Targeting` on `EnemyChampion` (e_range: only in fights, a
          shield cast on an ally goes out on cooldown otherwise - champion-data section 3). The host: first an ally
          within w_near of that enemy champion (the one being hit: a hidden lob onto the enemy looks round him), else
          one within w_ally_r of her, else nobody - then Zoomies on herself only. On the host: Zoomies (a shield of
          e_sh + e_ap% AP for e_t ticks, e_as% attack speed and e_ms% move speed for e_t), and she attaches: she
          teleports onto him and banishes herself for w_t ticks (nobody can pick or see her; she cannot act), a
          Teleport onto him every w_step ticks keeps her on him, the cat lying on her book rides his head (`w_ride`, a
          buff picture) and he heals w_heal + w_hap% AP every w_p ticks (+ the passive's kept heal on the jump).
          After w_t she jumps off beside him (`w_off`).
  ult     R Final Chapter (魔典终章), `Targeting` on `EnemyChampion` (r_range): she opens the book (`ult`, r_dur ticks)
          and r_n waves leave her every r_gap ticks toward the target (penetrating lines, r_w wide): each enemy hit
          takes r_dmg + r_ap% AP and r_slow% for r_slow_t, each ally on the line heals r_heal + r_hap% AP (a hidden
          twin). League roots on the third wave that hits the same enemy; data counts no hits per enemy, so the
          third wave roots (r_root ticks) whatever it hits. She may walk while the waves go on (League's channel).
The add-on copy (--native, addons/league_yuumi): the attach has no end - the add-on keeps her banished and on the
host, lifts the banish while she casts from his head (a_* frames) and drops her off when he dies or goes home.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_yuumi.data_champion")
ID = "league_yuumi"
FX = "asset/league/effects/league_yuumi_fx"
BIG = "asset/league/effects/league_yuumi_big"

# League units x 100 = ours (attack range 425 -> 50000, a step under the pack's 53000-60000 supports); radii count
# the unit's collision radius (~15000) on top. Timings from the strips (tools/art/rig_yuumi.py MS): the attack's reach
# frame 3 from 130 ms (atk_st 8, 480 ms in all), Q's flick frame 3 from 130 ms (q_st 8, 460 ms), W's leap away in frame 4
# from 180 ms (w_st 11: the jump-on lands then, 300 ms), the jump off 320 ms (w_off 19), R's book standing in frame 3
# from 140 ms (r_st 9, 500 ms). Numbers = the 10-min classic-SDK simulations (support lane 4 against priest, monk, bard,
# pythoness and spirit_caller, three lineups, both sides, 8 seeds, 2026-10-19): the draft (hp 880, Q 70 + 40% /
# 110 + 60%, W heal 15 + 6% a second, E 70 + 40%, R 60 + 25% a wave, attach 4 s every 10 s) -3.11 (league_milio -0.56
# the same batch); W heal 30 + 10%, E 100 + 50%, attack speed 35% -2.73; + Q 90 / 140, R 80, wave heal 40, hp 950
# -1.96; + W every 7 s -1.16; + W heal 45 + 15%, E 130 + 60%, every 6 s, hp 1000 -0.86; + Q 110 + 50% / 170 + 70%,
# R 110 + 35% heal 60, atk 82, passive 50 / heal 60 -0.36 / +0.27 (seeds 9-16; league_milio -1.74) = P.
P = {
    # stats (the pack's ranged supports: hp 880-950 +80-95, atk 75-85 +6, ap 30 +15, def 20-24, mr 20-24; League's
    # Yuumi: 500 +69 hp, 25 armour, 25 mr, 330 move, 425 range - the frailest champion, safe on her ally)
    "hp": 1000, "hp_g": 85, "atk": 82, "atk_g": 5, "ap": 35, "ap_g": 18, "def": 18, "def_g": 6, "mr": 22, "mr_g": 4,
    "ms": 980, "ms_g": 10,
    "atk_range": 50000, "atk_dur": 29, "atk_cd": 90, "atk_st": 8, "a_speed": 4000, "a_y": -2000,
    # passive Feline Friendship (League: every ~6 s an attack or spell on a champion: 20-110 +15% AP, heals 15-100 +25%
    # AP her and her next ally)
    "p_cd": 360, "p_dmg": 50, "p_ap": 25, "p_heal": 60, "p_hap": 20,
    # Q Prowling Projectile (League: 1150, 60-235 +20% AP, empowered after 1.35 s: 80-355 +30% AP, slow 20% / 47-65%,
    # missile 650 -> 950, cd 6.5)
    "q_cd": 420, "q_range": 80000, "q_dur": 28, "q_st": 8, "q_speed": 2500, "q_len": 100000, "q_w": 5000,
    "q_y": -3000, "q_t1": 20, "q_dmg": 110, "q_ap": 50, "q_slow": 20, "q_slow_t": 60,
    "q_edmg": 170, "q_eap": 70, "q_eslow": 50, "q_eslow_t": 120,
    # W You and Me! (League: 700 range dash, untargetable while attached, heal & shield power to the ally) + E
    # Zoomies (League: shield 75-225 +40% AP, attack speed 25-37.5%, move speed 20% decaying over 3 s, cd 10-7.5 s)
    "w_cd": 360, "e_range": 75000, "w_dur": 18, "w_st": 11, "w_near": 30000, "w_ally_r": 70000, "w_t": 240,
    "w_step": 6, "w_p": 60, "w_heal": 45, "w_hap": 15, "w_off": 19,
    "e_sh": 130, "e_ap": 60, "e_t": 180, "e_as": 35, "e_ms": 20,
    # R Final Chapter (League: 1100 long, 5 waves 0.75 s apart over 3.5 s, 60-300 +20% AP each (one wave per enemy at
    # full, -25% for more), slow 20-50%, root 1.25 s on three hits; heals allies 35-130 +12.5% AP a wave; cd 120-100 s)
    "r_cd": 2700, "r_range": 80000, "r_dur": 30, "r_st": 9, "r_n": 5, "r_gap": 45, "r_speed": 3000, "r_len": 100000,
    "r_w": 12000, "r_y": -3000, "r_dmg": 110, "r_ap": 35, "r_slow": 20, "r_slow_t": 45, "r_root_k": 3, "r_root": 75,
    "r_heal": 60, "r_hap": 10,
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
    if tick is None:
        return "Permanent"
    return tick if isinstance(tick, (str, dict)) else {"Time": {"tick": tick}}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields},
            "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields}}


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


def heal_ally(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Ally"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a target's or a projectile's list."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def alive(*effects):
    """Only while she lives and is in play (a dead caster's Delayed effects run in the game; the search finds no dead
    or banished caster)."""
    return pick(1, "AllyOnlySelf", *effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, target, *end):
    """A hidden lob onto the unit in hand (league_annie R): it lands where he stood when it left, its end_effects act
    on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "applied_target": target, "applied_effects": [], "end_effects": list(end)}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur_, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur_, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ attack + passive Feline Friendship
    friend = sw("p_cd", NONE, combine(
        flag("p_cd", p["p_cd"]), refresh("p_carry", None), magic(p["p_dmg"], p["p_ap"]), view("p_hit"), tsfx("p_hit"),
        on_me(heal_ally(p["p_heal"], p["p_hap"]), view("p_heal"))))
    twin = homing("a_twin", p["a_speed"], p["a_y"] + 5000, "EnemyChampion", [friend])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        sfx("a"), homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
        twin)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Prowling Projectile
    near = [magic(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), view("q_hit"),
            tsfx("q_hit")]
    far = [magic(p["q_edmg"], p["q_eap"]), buff("q_eslow", p["q_eslow_t"], move_speed_mult=-p["q_eslow"]),
           view("q_ehit"), tsfx("q_ehit")]
    missile = line("q_missile", p["q_speed"], p["q_len"], p["q_w"], p["q_y"], "EnemyWithoutTower", False,
                   [sw("q_near", combine(*near), combine(*far))])
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower", flat(combine(
        refresh("q_near", p["q_t1"]), sfx("q"), voice("vo_q", p), missile)))

    # ------------------------------------------------------------------ skill2: W You and Me! + E Zoomies
    zoomies = [shield(p["e_sh"], p["e_ap"], p["e_t"]), buff("e_on", "WithShield"),
               buff("e_haste", p["e_t"], move_speed_mult=p["e_ms"], attack_speed_mult=p["e_as"]), view("e_hit"),
               tsfx("e_hit")]
    if native:          # the add-on keeps her on the host until it drops her; the slot jumps on and gives Zoomies
        stay = [buff("w_host", 3)]
    else:
        # on the host for w_t: a Teleport onto him every w_step ticks, his heal every w_p (periodic casts on him)
        follow = casted(p["w_t"], p["w_step"], {"type": "Teleport"})
        mend = casted(p["w_t"], p["w_p"], heal_ally(p["w_heal"], p["w_hap"]), view("w_heal"))
        stay = [buff("w_ride", p["w_t"]), follow, mend,
                delayed(p["w_t"], {"type": "Teleport"}, on_me(anim("w_off", p["w_off"])), cview("w_land"), sfx("w_off"))]
    attach = [{"type": "Teleport"}, on_me({"type": "Banish", "duration": p["w_t"]}) if not native else NONE,
              *zoomies, sw("p_carry", combine(*rm("p_carry"), heal_ally(p["p_heal"], p["p_hap"]), view("p_heal"))),
              sfx("w_on"), *stay]

    def jump():
        return combine(flag("w_lock", 3), cview("w_jump"), homing("w_dash", 100000, -3000, "AllyNotSelf", attach))
    # first the ally beside the enemy champion (the one being hit), then one near her, else Zoomies on herself
    beside = lob("w_look", 1, "EnemyChampion", pick(p["w_near"], "AllyNotSelf", sw("w_lock", NONE, jump()), fp=True))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], p["w_st"] - 2, p["e_range"], "Targeting", "EnemyChampion", flat(combine(
        *rm("w_lock"), sfx("w"), voice("vo_w", p), beside,
        delayed(2, sw("w_lock", NONE, pick(p["w_ally_r"], "AllyNotSelf", jump())),
                sw("w_lock", NONE, on_me(*zoomies, delayed(p["e_t"], *rm("e_on"))))))))

    # ------------------------------------------------------------------ ult: R Final Chapter
    def wave(k):
        hit = [magic(p["r_dmg"], p["r_ap"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]), view("r_hit"),
               tsfx("r_hit")]
        if k + 1 == p["r_root_k"]:
            hit += [{"type": "Bind", "duration": p["r_root"]}, buff("r_root", p["r_root"])]
        foes = line("r_wave", p["r_speed"], p["r_len"], p["r_w"], p["r_y"], "EnemyWithoutTower", True, hit)
        friends = line("r_mend", p["r_speed"], p["r_len"], p["r_w"], p["r_y"] + 5000, "AllyNotSelf", True,
                       [heal_ally(p["r_heal"], p["r_hap"]), view("r_heal"), tsfx("r_heal")])
        return delayed(k * p["r_gap"], alive(foes, friends, sfx("r_wave"), on_me(heal_ally(p["r_heal"], p["r_hap"]))))
    ult = action("ult", p["r_dur"], p["r_cd"], p["r_st"], p["r_range"], "Targeting", "EnemyChampion", flat(combine(
        sfx("r"), voice("vo_r", p), cview("r_cast"), *[wave(k) for k in range(p["r_n"])])))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # projectiles are turned with their flight: the bolt and the missile point along it, a wave is an arc drawn the
    # same above and below its middle (turned half round it looks the same)
    views_p = [B_("a_bolt"), B_("q_missile"), B_("r_wave", BIG)]
    views_e = [E("a_hit"), E("p_hit"), E("p_heal"), E("q_hit"), E("q_ehit"), E("e_hit"), E("w_heal"),
               E("w_jump", FX, 2, False), E("w_land", FX, 2, False), E("r_cast", BIG, -1), E("r_hit"), E("r_heal")]
    # w_ride: the cat lying on her open book, drawn over the host's head (a buff picture is never mirrored)
    views_b = [B_("w_ride", BIG, 4), B_("e_haste", FX, -1), B_("q_slow", FX, 1), B_("q_eslow", FX, 1),
               B_("r_root", FX, 1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Range", "Heal", "Shield"],
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
