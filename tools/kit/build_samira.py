"""Build league_samira.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_samira.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-06: Q / E -> W combo / the spin cuts the hits she takes / R stands and spins in the
data pack - walking while it fires goes to a native add-on - / the passive's dash at immobilized champions):
  passive Daredevil Impulse (悍勇本色): the Style grade E -> S (g1..g6, one caster flag at a time, each g_t ticks,
          refreshed by every hit on an enemy champion, so it drops after g_t ticks without one; League's 6 s). A hit on a
          champion climbs a grade when its kind differs from the last one that hit a champion (l_a / l_q / l_e / l_w:
          her attack, Q, E's dash, W's spin); the same kind again only keeps the grade. Each grade adds g_ms% move
          speed (League's per-grade bonus). Her sword (attacks and Q in melee range, W's spin, the juggle) adds pm_dmg +
          pm_ratio% AD magic damage (League's melee bonus; it grows with missing health there - nothing reads health).
          Her attack at a champion in crowd control (`EnemyChampionInCC`, League's immobilized) dashes her onto it and
          keeps it up j_up ticks (a sword hit, `Airborne`), once every j_cd ticks: League's juggle, which would chain
          forever on her own knock-up here.
  attack  Tick 1 a hidden probe flies at the target: within pm_reach of her (`RandomTarget AllyOnlySelf` from the hit,
          league_morgana's reach check) it sets a_close, a champion in crowd control a_cc; a_read ticks later the
          attack picks its strip: the juggle, the sword (attack_m, the hit a_hit_m ticks on) or the gun (attack, the
          bullet a_shot ticks on). Every hit carries a champion-only twin (the Style climb and league_jinx's kill check).
  skill   Q Flair (交火): a `Direction` cast on `EnemyWithoutTower` (q_range). An enemy within q_close of her ->
          the sword: a cone in front (q_cone_r, `DirDot` 0 = a half circle) of q_dmg + q_ratio% AD and the melee bonus;
          else the gun: a bullet down the cast line (q_len, speed q_speed) that stops on the first enemy it hits.
  skill2  E Wild Rush (狂飙) -> W Blade Whirl (锋旋): a `Targeting` cast on `EnemyWithoutTower` (e_range). Its cooldown
          is the caster buff e_cd (the slot's own is 60 ticks; the AI does not cast the empty branch, league_caitlyn W),
          so her champion kills (the kill check on every champion hit within k_hold ticks) take it off: League's
          takedown reset. She dashes e_speed x e_tick toward the target and through it (`RushTime`, radius e_rad), e_dmg
          + e_ratio% AD magic damage to every enemy passed, then gains e_as% attack speed for e_as_t. On landing W: she
          spins w_t ticks taking w_red% less damage from attacks (League's spin destroys missiles; nothing blocks a
          projectile here), cutting everyone within w_r on w1_at and w2_at (w_dmg + w_ratio% AD each, the melee bonus).
  ult     R Inferno Trigger (炼狱扳机): a 3-tick `Targeting` cast on `EnemyChampion` (r_range) whose effect is empty
          below Style S (the AI does not cast it until then). At S: the grade is spent, `CasterAnimation ult` holds her
          r_t ticks (the native add-on lets her walk instead), r_vamp% life steal for r_t, and every r_period ticks a
          bullet to every enemy within r_rad: r_dmg + r_ratio% AD. The shots run on her own `AddCasted`: crowd control
          stops the spin, not the shots (League's R keeps firing).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_samira.data_champion")
ID = "league_samira"
FX = "asset/league/effects/league_samira_fx"
BIG = "asset/league/effects/league_samira_big"

# Numbers = candidate c12 of the 10-min classic-SDK simulations (tr_sim/sim/kd.py, bottom lane against gunner, soldier,
# archer and gambler, three lineups, both sides, 24 seeds a batch, 2026-10-06): +1.36 on seeds 1-24, +1.19 on 25-48
# (league_varus +1.63 / +1.91, league_jhin +1.43 / +2.08). The draft was -2.72: E onto champions only and to just behind
# the target (a fixed RushTime left her in the wave), Style 9 s and the sword's attacks a kind of their own (S was rare),
# then attack 100 -> 112, hp 920 -> 1030, defence 22 -> 26, range 50000 -> 55000, Q 110% -> 130%, E 50 -> 70, W 50% -> 70%
# (range +0.37, hp +0.57, the skills +0.72 alone). Timings fitted to the strips (tools/art/rig_samira.py MS): the gun's
# bullet on tick 12 inside its firing frame (180-250 ms), the sword's cut on 12 (frame 12.4), Q's shot on 9 (frame
# 7.2-12.6) and slash on 10 (frame 10.4), R's 120 ticks = the strip's 2002 ms. The sword strip keeps 22 ticks (2 past
# the attack): ending it with the attack (20) went +0.30 / +1.18 on the same seeds against +1.36 / +1.19.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Samira: 500 range
    # (Varus 575 = 57500 here), 57 AD +3.3, 630 +108 hp, 26 armour, 335 move
    "hp": 1030, "hp_g": 92, "atk": 112, "atk_g": 20, "def": 26, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    # attack: probe at tick 1, the strip picked a_read ticks later
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 58, "a_read": 2, "a_shot": 8, "a_hit_m": 8, "a_anim": 22,
    "bullet_speed": 8000, "bullet_y": -3000, "pm_reach": 8000,
    # passive: Style grades, melee bonus, the juggle
    "g_n": 6, "g_t": 540, "split_a": 1, "g_ms": 3, "pm_dmg": 15, "pm_ratio": 20, "j_cd": 360, "j_up": 30, "j_speed": 6000,
    "k_hold": 40, "k_read": 4, "reset_mult": 10000, "a_climb": 18,
    # skill: Q Flair (League: gun 0-? + 110% AD at 950 range, sword the same at 325, cd 6-2 s)
    "q_cd": 300, "q_range": 90000, "q_dur": 22, "q_close": 28000, "q_shot_at": 7, "q_slash_at": 8, "q_anim": 20,
    "q_speed": 9000, "q_len": 95000, "q_rad": 5000, "q_dmg": 30, "q_ratio": 130, "q_cone_r": 32000, "q_cone": 0,
    "q_climb": 24,
    # skill2: E Wild Rush (League: 650 units at 1600/s through the target, 50-100 + 20% bonus AD magic, +20-45% attack
    # speed 3 s, cd 20-10 s, takedown reset) -> W Blade Whirl (League: 0.75 s, two hits 20-80 + 80% bonus AD, radius 325,
    # destroys missiles, cd 30-20 s)
    "e_cd": 720, "e_range": 60000, "e_target": "EnemyChampion", "e_speed": 8000, "e_tick": 10, "e_rad": 22000, "e_dmg": 70, "e_ratio": 40,
    "e_as": 30, "e_as_t": 300, "w_t": 45, "w_r": 32000, "w1_at": 8, "w2_at": 40, "w_dmg": 25, "w_ratio": 70,
    "w_red": 60,
    # ult: R Inferno Trigger (League: Style S, 10 shots over 2 s at every enemy within 600, 0-? + 50% AD each, life
    # steal, cd 5 s)
    "r_cd": 300, "r_arm": 330, "r_range": 50000, "r_rad": 55000, "r_t": 120, "r_period": 12, "r_dmg": 10, "r_ratio": 40,
    "r_vamp": 40, "r_bullet": 12000,
}
GRADES = "EDCBAS"


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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def around(shape, target, effects, forward=None):
    return {"type": "RangeEffect", "shape": circle(shape) if isinstance(shape, int) else shape, "target": target,
            "apply_type": "AroundCaster" if forward is None else {"Forward": {"offset": forward}},
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


def line(name, speed, rng, radius, y, target, penetrate, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    g_n = p["g_n"]

    # ------------------------------------------------------------------ E's reset: league_jinx's kill check
    # a 2-tick skill_cooldown_mult caps every cooldown at once (section 5): Q's and R's go with E's
    reset = combine(*rm("reset"), flag("reset", 2, skill_cooldown_mult=p["reset_mult"]), cview("e_reset"),
                    sfx("e_reset"))

    def kill_check(src):
        """On a hit enemy champion, around its damage: the flag before, the living target's clear after, the read on
        her later. Each source keeps its own flag (league_tristana W)."""
        k = f"k_{src}"
        return (refresh(k, p["k_hold"]),
                combine(casted(3, 1, *rm(k)), on_me(delayed(p["k_read"], sw(k, combine(*rm(k), reset))))))

    # ------------------------------------------------------------------ passive: Style
    # The grades g1..g6 are permanent flags (one at a time, each with its move speed); g_live (g_t ticks) runs again on
    # every champion hit, and the first look at the grade after it ran out drops it (her next attack, climb or R). A hit
    # only sets a short flag c_<kind>; one read per action climbs, so the ladder is written once an action.
    grades = [f"g{k}" for k in range(1, g_n + 1)]
    kinds = ("a", "m", "q", "e", "w") if p["split_a"] else ("a", "q", "e", "w")
    mk = "m" if p["split_a"] else "a"
    lasts = [f"l_{x}" for x in kinds]
    lapse = sw("g_live", NONE, combine(*rm(*grades, *lasts)))

    # ------------------------------------------------------------------ ult: R Inferno Trigger, armed (league_evelynn R)
    # The AI casts an ult slot on any champion in reach (an empty branch below S went out and cost the cooldown), so the
    # slot only arms r_armed for r_arm ticks (refunded through ult_cooldown_mult when it lapses unused) - or fires at
    # once when she holds S - and while armed her next attack at S is the ult.
    kr_set, kr_read = kill_check("r")
    shell = around(p["r_rad"], "EnemyWithoutTower", [
        homing("r_bullet", p["r_bullet"], p["bullet_y"], "EnemyWithoutTower",
               [pick(1000, "EnemyChampion", kr_set, fp=True), attack(p["r_dmg"], p["r_ratio"]), view("r_hit"),
                tsfx("r_hit"), pick(1000, "EnemyChampion", kr_read, fp=True)])])
    fire = combine(*rm(*grades, *lasts, "g_live", "r_armed"),
                   anim("ult", p["r_t"]), sfx("r_cast"), sfx("r_loop"), sfx("vo_r"),
                   refresh("r_on", p["r_t"], vamp=p["r_vamp"]),
                   on_me(casted(p["r_t"], p["r_period"], shell, sfx("r_shot"))))
    arm = combine(refresh("r_armed", p["r_arm"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 sw("g_live", sw(f"g{g_n}", fire, arm), arm), key="ult")

    def up():
        out = combine(flag("g1", None, move_speed_mult=p["g_ms"]), cview("g_up"), sfx("g_up"))
        for k in range(1, g_n):
            top = k + 1 == g_n
            nxt = combine(*rm(f"g{k}"), flag(f"g{k + 1}", None, move_speed_mult=p["g_ms"] * (k + 1)),
                          cview("g_s" if top else "g_up"), sfx("g_s" if top else "g_up"))
            out = sw(f"g{k}", nxt, out)
        return sw(f"g{g_n}", NONE, out)

    def climb(kind):
        """Read once an action, after its hits: c_<kind> was set by a hit on an enemy champion. A new kind climbs a
        grade, the same one only keeps it (g_live runs again)."""
        return sw(f"c_{kind}", combine(*rm(f"c_{kind}"), lapse, refresh("g_live", p["g_t"]),
                                       sw(f"l_{kind}", NONE, combine(*rm(*[x for x in lasts if x != f"l_{kind}"]),
                                                                     flag(f"l_{kind}", None), up()))))

    def hit(kind):
        return refresh(f"c_{kind}", 30)

    def champ(src, kind):
        """The champion-only twin's effects: the kill check and the Style mark."""
        k_set, k_read = kill_check(src)
        return [k_set, hit(kind), k_read]

    melee = ap(p["pm_dmg"], p["pm_ratio"])

    # ------------------------------------------------------------------ attack: probe, then juggle / sword / gun
    probe = [homing("a_probe", 100000, 0, "Enemy",
                    [pick(p["pm_reach"], "AllyOnlySelf", flag("a_close", p["a_read"] + 2), fp=True)]),
             homing("a_probe_cc", 100000, 0, "EnemyChampionInCC", [flag("a_cc", p["a_read"] + 2)])]

    def cut(extra=()):
        """A sword hit on the attack's target: a 1-tick hidden blow and its champion twin."""
        return [homing("a_cut", 100000, 0, "Enemy",
                       [attack(0, 100), melee, *extra, view("a_slash_hit"), tsfx("a_slash_hit")]),
                homing("a_cut_c", 100000, 0, "EnemyChampion", champ("a", mk))]

    sword = combine(anim("attack_m", p["a_anim"]), sfx("a_swing"), delayed(p["a_hit_m"], *cut()))
    juggle = combine(*rm("j_cd"), flag("j_cd", p["j_cd"]), anim("attack_m", p["a_anim"]), sfx("a_swing"),
                     sfx("j_dash"), {"type": "MoveToTarget", "speed": p["j_speed"], "range": p["atk_range"] + 10000,
                                     "end_effects": []},
                     delayed(p["a_hit_m"], *cut([{"type": "Airborne", "duration": p["j_up"]}, view("j_up")])))
    gun = delayed(p["a_shot"], sfx("a_shot"),
                  homing("a_bullet", p["bullet_speed"], p["bullet_y"], "Enemy",
                         [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                  homing("a_bullet_c", p["bullet_speed"], p["bullet_y"], "EnemyChampion", champ("a", "a")))
    choose = sw("a_cc", sw("j_cd", sw("a_close", sword, gun), juggle), sw("a_close", sword, gun))
    normal = combine(*rm("a_close", "a_cc"), *probe, delayed(p["a_read"], choose),
                     delayed(p["a_climb"], climb("a"), *([climb("m")] if p["split_a"] else [])))
    # armed and at S: this attack is the ult (league_evelynn R's attacks fire it)
    go = combine(*rm("r_go"), sw("r_armed", sw("g_live", sw(f"g{g_n}", flag("r_go", 1)))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(lapse, go, sw("r_go", fire, normal)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Flair
    cone = {"DirDot": {"radius": p["q_cone_r"], "range": p["q_cone"]}}
    slash = combine(anim("skill_m", p["q_anim"]), sfx("q_swing"), sfx("vo_q2"), cview("q_slash"),
                    delayed(p["q_slash_at"],
                            around(cone, "EnemyChampion", champ("q", "q"), forward=1000),
                            around(cone, "EnemyWithoutTower",
                                   [attack(p["q_dmg"], p["q_ratio"]), melee, view("q_slash_hit"), tsfx("q_slash_hit")],
                                   forward=1000)))
    kq_set, kq_read = kill_check("q")
    bullet = line("q_bullet", p["q_speed"], p["q_len"], p["q_rad"], p["bullet_y"], "EnemyWithoutTower", False,
                  [pick(1000, "EnemyChampion", kq_set, hit("q"), fp=True),
                   attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"),
                   pick(1000, "EnemyChampion", kq_read, fp=True)])
    shot = combine(sfx("q_cock"), sfx("vo_q"), delayed(p["q_shot_at"], sfx("q_shot"), bullet))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(*rm("q_close"), pick(p["q_close"], "Enemy", flag("q_close", 2)),
                           sw("q_close", slash, shot), delayed(p["q_climb"], climb("q"))))

    # ------------------------------------------------------------------ skill2: E Wild Rush -> W Blade Whirl
    # League's dash is a fixed 650 units through the target; here she ends just behind it (`RushMoveToBack`, 15000 past
    # the spot it stood on): a `RushTime` of fixed length left her deep in the wave or short of the target. The slash on
    # the way lands on her arrival round her (e_rad) - the target and whoever stands by it.
    rush = {"type": "RushMoveToBack", "speed": p["e_speed"], "applied_effects": []}
    slash_e = combine(around(p["e_rad"], "EnemyChampion", [hit("e")]),
                      around(p["e_rad"], "EnemyWithoutTower", [ap(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]))

    def spin_hit():
        return combine(sfx("w_slash"),
                       around(p["w_r"], "EnemyChampion", champ("w", "w")),
                       around(p["w_r"], "EnemyWithoutTower",
                              [attack(p["w_dmg"], p["w_ratio"]), melee, view("w_hit"), tsfx("w_hit")]))

    spin = [slash_e, refresh("w_spin", p["w_t"], base_attack_damaged_reduce=p["w_red"]), sfx("w_cast"),
            *rm("e_as"), flag("e_as", p["e_as_t"], attack_speed_mult=p["e_as"]), climb("e"),
            delayed(p["w1_at"], spin_hit()), delayed(p["w2_at"], spin_hit()), delayed(p["w2_at"] + 2, climb("w"))]
    combo = combine(anim("skill2", p["e_tick"] + p["w_t"]), sfx("e_cast"), sfx("vo_e"), cview("e_dash"),
                    rush, delayed(p["e_tick"] + 1, *spin))
    skill2 = action("skill2", p["e_tick"] + 1, p["e_cd"], 1, p["e_range"], "Targeting", p["e_target"], combo)

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bullet"), P_("q_bullet"), P_("r_bullet")]
    views_e = [E("a_hit"), E("a_slash_hit"), E("j_up"), E("q_hit"), E("q_slash_hit"), E("q_slash", BIG),
               E("e_dash", BIG), E("e_hit"), E("e_reset", FX, 3, **LATE), E("w_hit"), E("r_hit"),
               E("g_up", FX, 3, **LATE), E("g_s", FX, 3, **LATE)]
    views_b = [B_(f"g{k}", FX, 3) for k in range(1, g_n + 1)] + [B_("w_spin", BIG, 2), B_("r_on", BIG, 2)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
