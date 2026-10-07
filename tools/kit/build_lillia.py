"""Build league_lillia.data_champion (jungle, Melee) from the parameters P.

    python tools/kit/build_lillia.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-07: Q alone / E -> W combo / Dream Dust and the real sleep in a native add-on, this pack
complete alone with the closest data can do / R drowsy then asleep on dusted champions, armed / pro combos):
  passive Dream-Laden Bough (梦满枝): every ability hit leaves Dream Dust (梦尘) on the unit - an `AddCasted Poison` of
          d_t ticks that runs every d_period ticks: magic d_dmg + d_ratio% AP on anything, and on champions a twin
          adding d_hp% of their maximum health as true damage each run (League: 5% magic over 3 s; `ApAttack` has no
          max-health part - the add-on deals it as magic) and healing her d_heal + d_heal_ratio% AP once per champion
          hit. The champion twin also listens for R (below). Every cast also climbs Prance (腾跃, League's Q passive):
          rungs p1..p4 on her (one at a time, pr_t ticks), each +pr_ms% move speed more.
  attack  A swing of her branch: physical 100% AD, a_st ticks in.
  skill   Q Blooming Blows (飞花挞): a `Targeting` cast on `EnemyWithoutTower` (q_range) - she spins at q_st: magic
          q_dmg + q_ratio% AP round her (q_r) and Dream Dust; the edge (outside q_in) adds the same again as true damage
          (an `ApAttack` under a 1-tick full magic penetration; the inner circle first gets a 1-tick damaged_reduce 99
          buff, the only way data can leave a ring's inside out).
  skill2  E Swirlseed (流涡种) -> W Watch Out! Eep! (惊惶木): a `Targeting` cast on s2_target (e_range).
          E: a seed lobbed at the target (e_travel ticks): magic e_dmg + e_ratio% AP, e_slow% slow for e_slow_t, dust.
          League's seed rolls on after a miss; a projectile started from a landing flies from her again (logged
          2026-10-07: the roll left her toward the landing point), so e_roll stays 0. W: once the throw is over she winds
          up (`skill2_w`) and a strike lands w_wind ticks after it was aimed where the target stood (its ring shows on
          the ground meanwhile): magic w_dmg + w_ratio% AP round it (w_r) and dust; the sweet spot (w_sweet) takes
          w_sweet_x times that (League x3) - a slowed target is still there. W keeps its own flag w_cd (w_cd_t).
  ult     R Lilting Lullaby (夜阑谣): a 3-tick `Targeting` cast on `EnemyChampion` (r_slot). Armed like league_seraphine R:
          it fires at once with two enemy champions within r_reach and dust on a champion lately (d_on), else it
          arms r_armed for r_arm ticks - each champion dust hit counts again and fires it, one is enough after r_hold
          - and refunds the cooldown when it lapses unused. Fire: a caster flag r_go for d_period ticks, so every Dream
          Dust on a champion meets it on its next run (league_ryze's flux): drowsy (r_slow% slow, r_drowsy ticks), then
          asleep - a stun of r_sleep (the add-on wakes them on damage, as League). Her own Q / W on a sleeper inside
          the window r_win wake it with r_wake + r_wake_ratio% AP more.
  combos  (「加」高手连招): E slow -> W on the sweet spot is the slot itself; R -> W: once they sleep (rw_wait after the
          fire), with w_cd off, the strike goes to a crowd-controlled champion in reach (asleep: the sweet spot and the
          wake); while R waits armed, skill2 throws E alone and keeps W for it; R only after dust, armed as
          above.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_lillia.data_champion")
ID = "league_lillia"
FX = "asset/league/effects/league_lillia_fx"
BIG = "asset/league/effects/league_lillia_big"

# Numbers = draft s0 (no simulation yet).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30, mr 25, move 1000, range 25000, cooldown 65;
    # league_diana 80/50 AP 950, league_evelynn 75/50 AP 880); League's Lillia: 605 +105 hp, 48 AD, 22 armour,
    # 330 move, 325 range
    "hp": 960, "hp_g": 95, "atk": 65, "atk_g": 8, "ap": 45, "ap_g": 20, "def": 28, "def_g": 8, "mr": 22, "mr_g": 4,
    "ms": 1050, "ms_g": 11,
    # attack: the branch swing
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 60, "a_st": 7,
    # passive: Dream Dust (League: 5% max HP magic over 3 s in 6 ticks, heal 25% of it on monsters, 100%? champions)
    "d_t": 181, "d_period": 45, "d_dmg": 4, "d_ratio": 3, "d_hp": 1, "d_heal": 12, "d_heal_ratio": 8,
    # the add-on (addons/league_lillia): + d_ap_bp / 10000 of maximum health per 100 AP each run (League +1.5% per 100
    # AP over the dust's 6 runs -> 0.3% a run of 5), the sleep n_sleep (League's 2 s: there any damage wakes them)
    "d_ap_bp": 30, "n_sleep": 120,
    # Prance (League: 1-7% x4 for 6.5 s)
    "pr_t": 390, "pr_ms": 5,
    # skill: Q Blooming Blows (League: radius 485, inner 225, 35-85 + 35% AP magic, the same as true on the edge, cd 6-4)
    "q_cd": 300, "q_range": 24000, "q_anim": 28, "q_st": 7, "q_r": 26000, "q_in": 12000, "q_dmg": 35, "q_ratio": 30,
    # skill2: E Swirlseed (League: 700 range, 60-185 + 50% AP, slow 40% 3 s, cd 12)
    "s2_target": "EnemyWithoutTower",
    "e_cd": 600, "e_range": 70000, "e_anim": 22, "e_rel": 7, "e_travel": 20, "e_r": 9000, "e_dmg": 45, "e_ratio": 40,
    "e_slow": 40, "e_slow_t": 180, "e_roll": 0, "e_roll_speed": 2500, "e_roll_len": 40000,
    # -> W Watch Out! Eep! (League: 500-700, radius 250, 80-180 + 35%? AP, sweet spot 65 x3, windup 0.6-0.75 s, cd 14-9)
    "w_cd_t": 600, "w_anim": 40, "w_wind": 30, "w_r": 22000, "w_sweet": 4000, "w_sweet_x": 3, "w_dmg": 40,
    "w_ratio": 30,
    # ult: R Lilting Lullaby (League: drowsy 1.5 s (slowing), asleep 2 s, wake 50-350 + ?% AP, cd 150/130/110)
    "r_cd": 4200, "r_slot": 80000, "r_reach": 70000, "r_arm": 600, "r_hold": 180, "r_anim": 30, "r_rel": 10,
    "r_drowsy": 90, "r_slow": 40, "r_sleep": 90, "r_wake": 80, "r_wake_ratio": 40,
    # combos
    "rw_wait": 10,
    # her spoken lines, at most one every vo_gap ticks
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
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "attack_effect_type": "Target"}


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def heal_me(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def alive(*effects):
    """Effects that run only while she lives (a dead caster's `Delayed` effects run on in the game)."""
    return pick(1, "AllyOnlySelf", *effects)


def casted(duration, period, *effects, kind="Poison"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, radius, target, effects, end=(), mark=""):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(radius), "range_effect_name": n(mark) if mark else "", "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False):
    """The kit; native=True is the add-on's copy (addons/league_lillia): the champion dust is a buff league_lillia_dust
    the add-on's passive league_lillia:dream reads (% max-health magic, R's drowsy and the sleep that breaks on damage
    with the wake damage), so the data's true part, R's listener and the wake twins go."""
    prs = ["p1", "p2", "p3", "p4"]

    # ------------------------------------------------------------------ Prance: one rung at a time, read from the top
    def pr_flag(k):
        return flag(prs[k], p["pr_t"], move_speed_mult=(k + 1) * p["pr_ms"])

    prance = pr_flag(0)
    for k in range(len(prs) - 1):
        prance = sw(prs[k], combine(*rm(prs[k]), pr_flag(k + 1)), prance)
    prance = sw(prs[-1], combine(*rm(prs[-1]), pr_flag(len(prs) - 1)), prance)

    # ------------------------------------------------------------------ R's pieces read by the dust
    def sleep():
        return combine(buff("drowsy", p["r_drowsy"], move_speed_mult=-p["r_slow"]), tsfx("drowsy"),
                       delayed(p["r_drowsy"], {"type": "Stun", "duration": p["r_sleep"]}, buff("sleep", p["r_sleep"]),
                               tsfx("sleep")))

    # the champion dust's run: its true part, and R's flag (only from a living Lillia: a dead caster's flags freeze)
    lull = combine(alive(refresh("lives", 1)), sw("lives", combine(*rm("lives"), sw("r_go", sleep()))))
    dust_all = casted(p["d_t"], p["d_period"], magic(p["d_dmg"], p["d_ratio"]))
    dust_champ_run = buff("dust", p["d_t"]) if native else casted(p["d_t"], p["d_period"], true_hp(p["d_hp"]), lull)

    # ------------------------------------------------------------------ R Lilting Lullaby
    def count():
        """2-tick flags u1 -> u2: two enemy champions within r_reach."""
        return combine(*rm("u1", "u2"),
                       around(p["r_reach"], "EnemyChampion", [sw("u1", refresh("u2", 2), refresh("u1", 2))]))

    def fire(slot):
        rel = p["r_rel"] if slot else 0
        win = p["r_drowsy"] + p["r_sleep"] + p["d_period"]
        lullaby = combine(refresh("r_go", p["d_period"]), refresh("r_win", win), cview("r_cast"), sfx("r_cast"))
        # R -> W: once they sleep, the strike goes to a crowd-controlled champion in reach (its dust twin is not armed,
        # so no R inside it)
        rw = delayed(rel + p["d_period"] // 2 + p["r_drowsy"] + p["rw_wait"],
                     alive(sw("w_cd", NONE, pick(p["e_range"], "EnemyChampionInCC", w_combo(False)))))
        out = [*rm("r_armed"), voice("vo_r", p), on_me(delayed(rel, alive(lullaby, prance)), rw)]
        if slot:
            out.append(anim("ult", p["r_anim"]))
        return combine(*out)

    # each champion hit by her dust: d_on (dust lately), the heal, and an armed R's check
    def go():
        near = pick(p["atk_range"] + 5000, "EnemyChampion", refresh("r_solo", 2))
        return sw("r_armed", combine(*rm("r_solo"), count(),
                                     sw("u2", refresh("r_solo", 2), sw("r_wait", NONE, near)),
                                     sw("r_solo", fire(False))))

    def dust_champ(armed=True):
        me = [refresh("d_on", p["d_t"])] + ([go()] if armed else [])
        return [dust_champ_run, heal_me(p["d_heal"], p["d_heal_ratio"]), on_me(*me)]

    def wake():
        return sw("r_win", combine(magic(p["r_wake"], p["r_wake_ratio"]), view("wake"), tsfx("wake")))

    def wakes(*effects):
        """The data's wake twins (the add-on wakes sleepers on any damage itself)."""
        return [] if native else list(effects)

    # ------------------------------------------------------------------ Q Blooming Blows
    def q_spin():
        edge = [magic(p["q_dmg"], p["q_ratio"])]  # no picture: it would also play on the inside
        return combine(
            sfx("q_hit"), prance,
            # the dust a tick later: its first run would come this tick, under the inside's damaged_reduce
            around(p["q_r"], "EnemyWithoutTower", [magic(p["q_dmg"], p["q_ratio"]), delayed(1, dust_all), view("q_hit")]),
            around(p["q_r"], "EnemyChampion", [delayed(1, dust_champ_run)] + dust_champ()[1:]),
            *wakes(around(p["q_r"], "EnemyChampionInCC", [wake()])),
            # the edge: the inside shrugs it off for this tick, the rest takes it through full magic penetration
            around(p["q_in"], "EnemyWithoutTower", [buff("q_in", 1, damaged_reduce=99)]),
            refresh("q_pen", 1, magic_resistance_penetration=100),
            around(p["q_r"], "EnemyWithoutTower", edge), *rm("q_pen"))

    # ------------------------------------------------------------------ skill2: E Swirlseed -> W Watch Out! Eep!
    def w_strike(armed=True):
        hit = [magic(p["w_dmg"], p["w_ratio"]), dust_all, view("w_hit")]
        sweet = [magic((p["w_sweet_x"] - 1) * p["w_dmg"], (p["w_sweet_x"] - 1) * p["w_ratio"]), view("w_sweet"),
                 tsfx("w_sweet")]
        return combine(
            lob("w_lob", p["w_wind"], p["w_r"], "EnemyWithoutTower", hit, end=[view("w_land"), sfx("w_hit")],
                mark="w_mark"),
            lob("w_sweet_lob", p["w_wind"], p["w_sweet"], "EnemyWithoutTower", sweet, end=[]),
            lob("w_champ", p["w_wind"], p["w_r"], "EnemyChampion", dust_champ(False)),
            *wakes(lob("w_wake", p["w_wind"], p["w_r"], "EnemyChampionInCC", [wake()])))

    def w_combo(armed=True):
        """W alone (the slot after E, and R -> W): the windup, the strike aimed now where the target stands."""
        return combine(refresh("w_cd", p["w_cd_t"]), anim("skill2_w", p["w_anim"]), sfx("w_cast"), voice("vo_w", p),
                       on_me(prance), w_strike(armed))

    def e_seed():
        seed_hit = [magic(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                    dust_all, view("e_hit"), tsfx("e_hit"), on_me(refresh("e_hit", 3))]
        roll = line("e_roll", p["e_roll_speed"], p["e_roll_len"], p["e_r"], 0, "EnemyWithoutTower", False,
                    seed_hit[:-1])
        end = [view("e_land")]
        if p["e_roll"]:
            end.append(delayed(1, sw("e_hit", NONE, roll)))
        return combine(*rm("e_hit"), sfx("e_cast"),
                       lob("e_seed", p["e_travel"], p["e_r"], "EnemyWithoutTower", seed_hit, end=end),
                       lob("e_champ", p["e_travel"], p["e_r"], "EnemyChampion", dust_champ()))

    skill = action("skill", p["q_anim"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_cast"), voice("vo_q", p), cview("q_spin"), delayed(p["q_st"] - 1, q_spin())))

    skill2 = action("skill2", p["e_anim"], p["e_cd"], 1, p["e_range"], "Targeting", p["s2_target"],
                    combine(voice("vo_e", p), delayed(p["e_rel"], e_seed(), on_me(prance)),
                            # armed R waiting: W is kept for the sleepers (R -> W)
                            delayed(p["e_anim"] - 1, sw("w_cd", NONE, sw("r_armed", NONE, w_combo())))))

    # ------------------------------------------------------------------ ult
    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(count(), sw("d_on", sw("u2", fire(True), arm), arm)))

    # ------------------------------------------------------------------ attack: the branch swing
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), attack(0, 100), view("a_hit")), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow her (the red side's mirroring); the
    # seed is drawn top-bottom symmetric, the buffs and late caster pictures left-right symmetric; W's ring and the
    # landings are ViewEffects on the point (never turned)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("e_seed")] + ([P_("e_roll")] if p["e_roll"] else [])
    views_e = [E("a_hit"), E("q_spin", BIG, -1), E("q_hit"), E("e_hit"), E("e_land", FX, -1, follow=False),
               E("w_mark", BIG, -2, follow=False), E("w_land", BIG, -1, follow=False), E("w_hit"), E("w_sweet"),
               E("r_cast", BIG, 3, **LATE), E("wake")]
    views_b = [B_(x, FX, -1, tag="prance") for x in prs] + [B_("drowsy", FX, 3), B_("sleep", FX, 3), B_("e_slow", FX, -1)]
    if native:
        views_b.append(B_("dust", FX, 2))           # the add-on's dust buff (the data pack's dust has no buff)
    kit = {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "CC", "Heal", "Dot"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2",
                        f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_lillia:dream", "params": native_params(p)}
    return kit


def native_params(p):
    """The add-on passive's numbers (non-negative integers): the dust per run as basis points of maximum health (the
    data's d_hp% true, now magic) plus d_ap_bp per 100 AP, R's drowsy, slow and sleep (N_SLEEP: League's 2 s, since
    any damage ends it), the wake damage, and the data dust's own magic run (d_dmg + d_ratio% AP), which must not wake
    a sleeper (the game log: a 6-point dust run woke all three 20 ticks into the sleep)."""
    return {"d_period": p["d_period"], "d_hp_bp": p["d_hp"] * 100, "d_ap_bp": p["d_ap_bp"], "r_drowsy": p["r_drowsy"],
            "r_slow": p["r_slow"], "r_sleep": p["n_sleep"], "r_wake": p["r_wake"], "r_wake_ratio": p["r_wake_ratio"],
            "d_dmg": p["d_dmg"], "d_ratio": p["d_ratio"]}


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
