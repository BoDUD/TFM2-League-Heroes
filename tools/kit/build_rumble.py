"""Build league_rumble.data_champion (top, Melee fighter, AP: Rumble, the Mechanized Menace) from the parameters P.

    python tools/kit/build_rumble.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (draft, 2026-10-25: TOP, layout A - Q / E / R, Scrap Shield (W) folded into the passive's controller; 「有连招要做连招」).
TFM2 has three active slots for League's four buttons: Flamespitter (Q) is `skill`, Electro-Harpoon (E) `skill2`, The
Equalizer (R) the `ult`. Q, E and W keep their cooldowns in flags (`q_cd`, `e_cd`, `w_cd`; league_sejuani's) so the
combos can cast them; a slot cast while its flag is up, or while he is Overheated, does nothing (a 3-tick idle).
Flags die with him: every life starts cold with Q, E and W ready.
  passive Junkyard Titan (heat, 热量): heat in steps of 10 kept as a ladder of caster flags h1..h9 (league_kled's
          courage). Q and W ask two steps, each harpoon one (`ha`, `ha2`: the controller climbs one step a pulse);
          every ask holds the heat for h_hold ticks (`hot`), after that it cools one step every h_decay ticks.
          Danger Zone (危险地带, 50 heat and up, `dz`): Q, E and W at dz_k% (League +50%).
          Overheat (过热, the step past 90): the ladder clears and for oh_t ticks (`oh`) he is silenced - Q, E and W do
          nothing, R waits (its cooldown capped at r_wait ticks, league_kled's on foot) - and his attacks gain oh_as%
          attack speed and oh_dmg + oh_ap% AP magic damage, on champions also oh_thp% of their maximum health (true,
          `FixedAttack`: magic has no max-health field). Heat starts again from 0.
  W       Scrap Shield (破碎护盾), in the controller: off `w_cd`, not Overheated, with an enemy champion within w_near:
          a shield of w_sh + w_ap% AP for w_sh_t ticks and w_ms% move speed for w_ms_t (both x dz_k% in the Danger
          Zone), two steps of heat. No animation of its own (League's W does not stop him): the shield is a picture
          on him, made left-right symmetric (it plays while he walks).
  attack  A blow of the claw (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; Overheated, the
          blow burns (above).
  skill   Q Flamespitter (纵火盛宴), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): he flames a cone ahead for
          q_t ticks: q_n pulses every q_gap ticks of q_dmg + q_ap% AP to every enemy in the cone (q_len long,
          `DirDot` range q_cone; league_ornn W's), x dz_k% when cast in the Danger Zone (`q_dz` for the whole burst).
          League lets him walk while it burns for 3 s; the flame has a front and a back and rides on him, so it is
          drawn into his own skill frames (the client never mirrors an effect picture) and he stands for the burst.
          The cone reaches as far as the fire is drawn (2026-10-25: his cannon's muzzle is 35 px ahead of him in the
          frame and the fire pours 42 px on from it, so q_len 72 px), and he casts it from q_range 45 px.
  skill2  E Electro-Harpoon (电子鱼叉), `Targeting` on `EnemyWithoutTower` (e_range, `e_cd`): a harpoon (a line
          stopping on the first enemy, e_speed <= 2 x e_rad): e_dmg + e_ap% AP and e_slow% slower for e_slow_t
          ticks, x dz_k% in the Danger Zone.
  ult     R The Equalizer (恒温灼烧), `Targeting` on `EnemyChampion` (r_range): he fires the rockets on r_rel; r_n
          hidden lines run toward the champion and end r_first, r_first + r_step, ... away (League's line laid
          along his aim; data has no perpendicular line), each landing a burning zone of radius r_r for r_t ticks:
          every r_p ticks r_dmg + r_ap% AP and r_slow% slower. The launch (r_launch) is drawn behind him (z -1: the
          rockets leave the pods on his back, their smoke behind his body). The rockets' fall and the fire are one `ViewEffect` on
          each landing point, its tag as long as the zone (never turned: an upright picture on a zone would stand on
          its head on the red side).
  combos  E -> E2 (League's second charge): a harpoon through a champion opens the recast - e_gap ticks later the
          controller fires a second harpoon at a champion within e_range (e2_k% damage, e2_slow% slow: League's
          stacking slow and the second harpoon's bonus on the same target).
          E2 -> Q: the second harpoon on a champion within q_go readies Q's burst at it (`q_go`, if Q is ready).
          R -> E: the rockets' landing takes E off its cooldown and the controller harpoons a champion in reach
          (`e_go`; the slow of the fire and the harpoon stack).
          Danger Zone -> W: climbing into the Danger Zone takes W off its cooldown, so with an enemy champion near
          the shield goes up at once, already x dz_k% (League's heat management: W to keep the heat up in a fight).
          Overheat -> his attacks (above).
  controller An AddCasted pulse on him every ctl_p ticks (league_sejuani's, hung by his attack and the ult, only for
          Rumble himself: `own`): heat, cooling, Overheat, W and the combos' casts.
Not built (data cannot): Q while walking; a perpendicular R line; heat from casting outside fights cooling slower
(League's heat decays only out of combat - here any h_hold ticks without a cast).
Timings: drafts until the frames exist (tools/art/rig_rumble.py retimes them).
Numbers: League (16.21 read at draft time, to recheck) into the top fighter range (league_kled, league_singed,
league_gnar); not balanced yet (kd.py --lane 0, C:/t/ru_sim).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_rumble.data_champion")
ID = "league_rumble"
FX = "asset/league/effects/league_rumble_fx"
BIG = "asset/league/effects/league_rumble_big"

# League's Rumble (approximate, to recheck against 16.21): 655 +105 hp, 64 AD +3.2, 36 armour +4.7, 28 mr +2.05, 345
# move, 125 range, 0.644 attack speed. Heat: 10 per ability, Danger Zone at 50 (+50% effects), Overheat at 100: silenced
# ~5.5 s, attacks +5-40 (+25% AP) + 6% max health magic and bonus attack speed. Q: a 3 s cone, 135-315 (+110% AP) in
# all, cd 6. W: shield 60-160 (+45% AP) 1.5 s, +10-30% move speed, cd 6. E: 850 harpoon, 60-180 (+40% AP), 15-35% slow,
# two charges (the second on the same target +25%, the slow stacking), cd 6. R: 1700 range, a 1000 line of rockets
# burning 5 s, about 140-280 (+17.5% AP) a second and 35% slow, cd 140-100.
P = {
    # stats (Melee fighters: league_kled 760 / 88, league_singed 1260 / 66 + 30 AP)
    "hp": 1080, "hp_g": 100, "atk": 70, "atk_g": 5, "apw": 30, "apw_g": 14, "def": 30, "def_g": 7, "mr": 25, "mr_g": 4,
    "ms": 1050, "ms_g": 11,
    "atk_range": 20000, "atk_dur": 28, "atk_cd": 68, "a_hit": 11,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: heat (steps of 10), the Danger Zone, Overheat
    "h_hold": 240, "h_decay": 30, "dz_k": 150,
    "oh_t": 300, "oh_as": 60, "oh_dmg": 20, "oh_ap": 25, "oh_thp": 3,
    # W Scrap Shield (in the controller)
    "w_cd": 420, "w_near": 45000, "w_sh": 60, "w_ap": 45, "w_sh_t": 90, "w_ms": 20, "w_ms_t": 60,
    # skill: Q Flamespitter
    "q_cd": 360, "q_range": 45000, "q_t": 90, "q_n": 6, "q_gap": 15, "q_first": 8, "q_len": 72000, "q_cone": 700,
    "q_dmg": 18, "q_ap": 18, "q_go": 30000,
    # skill2: E Electro-Harpoon (+ the second harpoon)
    "e_cd": 480, "e_range": 55000, "e_dur": 24, "e_rel": 8, "e_speed": 6000, "e_rad": 3000, "e_dmg": 50, "e_ap": 40,
    "e_slow": 20, "e_slow_t": 120, "e_gap": 30, "e_win": 150, "e2_k": 125, "e2_slow": 35,
    # ult: R The Equalizer
    "r_cd": 5400, "r_range": 60000, "r_dur": 36, "r_rel": 14, "r_n": 6, "r_first": 20000, "r_step": 14000,
    "r_speed": 6000, "r_r": 7000, "r_t": 240, "r_p": 30, "r_dmg": 25, "r_ap": 15, "r_slow": 35,
    "r_wait": 330,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
}
H = 9   # heat flags h1..h9 (10..90); the step past h9 overheats


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
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio, k=100):
    return {"type": "ApAttack", "damage": dmg * k // 100, "attack_ratio": ratio * k // 100, "hp_ratio": 0,
            "can_crit": False}


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def shield(amount, ap_ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap_ratio, "tick": tick}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(radius, cone, target, *effects):
    """A cone ahead of him toward the action's target (league_darius E's Forward DirDot, league_ornn W)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cone}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def alive_aimed(*effects):
    """The same guard for effects that use the action's target or direction (league_ornn's; champion-data
    section 5): the effects as the flag's branch, a copy inside the search as the other so the AI still reads them."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)),
                   sw("lives", combine(*effects), pick(1, "AllyOnlySelf", *effects)), *rm("lives"))


def decoy(dmg, ratio, kind=ap):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, penetrate=True, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    ctl_p = p["ctl_p"]
    dz = p["dz_k"]
    haste = lambda name, pct_, t: buff(name, t, move_speed_mult=pct_)

    def heat(k):
        """k steps of heat asked of the controller (read and cleared there); every ask holds the heat."""
        return combine(refresh("hot", p["h_hold"]), refresh("ha", ctl_p + 2),
                       refresh("ha2", ctl_p + 2) if k == 2 else None)

    # ------------------------------------------------------------------ W Scrap Shield (cast by the controller)
    def w_shield(k):
        return combine(shield(p["w_sh"] * k // 100, p["w_ap"] * k // 100, p["w_sh_t"]),
                       haste("w_ms", p["w_ms_t"], p["w_ms"] * k // 100))
    w_now = combine(refresh("w_cd", p["w_cd"]), heat(2), sfx("w"), voice("vo_w", p),
                    on_me(sw("dz", w_shield(dz), w_shield(100)), refresh("w_shown", p["w_sh_t"])))

    # ------------------------------------------------------------------ passive: heat, the Danger Zone, Overheat
    steps = [f"h{k}" for k in range(1, H + 1)]
    overheat = combine(*rm(steps[-1], "dz", "ha", "ha2", "hot"),
                       refresh("oh", p["oh_t"], attack_speed_mult=p["oh_as"]), cview("oh_on"), sfx("oh"),
                       voice("vo_oh", p))
    # Danger Zone -> W: into the zone, W is ready again (cast at once with an enemy champion near, already stronger)
    into_dz = combine(flag("dz", None), cview("dz_on"), sfx("dz"), *rm("w_cd"))
    up = flag(steps[0], None)
    for k, name in enumerate(steps):
        nxt = overheat if k == H - 1 else combine(*rm(name), flag(steps[k + 1], None), into_dz if k == 3 else None)
        up = sw(name, nxt, up)
    down = NONE
    for k, name in reversed(list(enumerate(steps))):
        prev = None if k == 0 else flag(steps[k - 1], None)
        down = sw(name, combine(*rm(name), prev, *(rm("dz") if k == 4 else [])), down)
    heat_ctl = sw("oh", combine(*rm("ha", "ha2")), combine(
        sw("ha", combine(*rm("ha"), up)),
        sw("ha2", combine(*rm("ha2"), refresh("ha", ctl_p + 2))),
        sw("hot", NONE, sw("h_dk", NONE, combine(refresh("h_dk", p["h_decay"]), down)))))

    # ------------------------------------------------------------------ attack (+ Overheat's burn)
    burn = [ap(p["oh_dmg"], p["oh_ap"]), view("oh_hit"), tsfx("oh_hit")]
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   sw("oh", combine(homing("oh_blow", "Enemy", burn), homing("oh_tw", "EnemyChampion",
                                                                             [pct(p["oh_thp"])]))))

    # ------------------------------------------------------------------ Q Flamespitter
    def q_cast():
        def pulse(k):
            hit = [sw("q_dz", ap(p["q_dmg"], p["q_ap"], dz), ap(p["q_dmg"], p["q_ap"])), view("q_hit"),
                   tsfx("q_hit")]
            return delayed(p["q_first"] + k * p["q_gap"] - 1,
                           alive_aimed(ahead(p["q_len"], p["q_cone"], "EnemyWithoutTower", *hit)))
        # (the flame itself is drawn into his skill frames: tools/art/rig_rumble.py)
        return combine(refresh("q_cd", p["q_cd"]), sw("dz", refresh("q_dz", p["q_t"])), heat(2),
                       anim("skill", p["q_t"]), sfx("q"), voice("vo_q", p), *[pulse(k) for k in range(p["q_n"])])

    # ------------------------------------------------------------------ E Electro-Harpoon (+ the second)
    def harpoon(second):
        k = p["e2_k"] if second else 100
        slow = p["e2_slow"] if second else p["e_slow"]
        hit = lambda m: [ap(p["e_dmg"], p["e_ap"], k * m // 100),
                         buff("e_slow", p["e_slow_t"], move_speed_mult=-slow * m // 100),
                         view("e2_hit" if second else "e_hit"), tsfx("e_hit")]
        # through a champion: the first opens the recast (e_wait, then e_go2), the second readies Q (E2 -> Q)
        twin = (on_me(refresh("q_go", ctl_p + 6)) if second else
                on_me(refresh("e_wait", p["e_gap"]), refresh("e_go2", p["e_gap"] + p["e_win"])))
        effects = [sw("dz", combine(*hit(dz)), combine(*hit(100))), homing("e_tw", "EnemyChampion", [twin])]
        return combine(anim("skill2", p["e_dur"]), sfx("e2" if second else "e"), heat(1),
                       delayed(p["e_rel"] - 1, alive_aimed(
                           line("e_harpoon", p["e_speed"], p["e_range"] + 10000, p["e_rad"], "EnemyWithoutTower",
                                effects, penetrate=False))))

    def e_cast():
        return combine(refresh("e_cd", p["e_cd"]), *rm("e_go2", "e_wait"), voice("vo_e", p), harpoon(False))

    # ------------------------------------------------------------------ R The Equalizer
    def landing(k):
        burn_ = [ap(p["r_dmg"], p["r_ap"]), buff("r_slow", p["r_p"] + 6, move_speed_mult=-p["r_slow"]), tsfx("r_hit")]
        end = [field("r_zone", p["r_r"], p["r_t"], p["r_p"], burn_, first=0), view("r_fall"), sfx("r_fall")]
        if k == 0:   # R -> E: the first rocket down takes E off its cooldown and the controller harpoons
            end.append(sw("own", combine(*rm("e_cd"), refresh("e_go", 30))))
        return line(f"r_rocket{k}", p["r_speed"], p["r_first"] + k * p["r_step"], 1000, "Ally", [], end=end)
    rockets = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                      delayed(p["r_rel"] - 1, alive_aimed(cview("r_launch"), *[landing(k) for k in range(p["r_n"])])))
    # Overheated R waits: the empty cast's cooldown capped at r_wait ticks (league_kled's on foot)
    wait_mult = -(-p["r_cd"] * 100 // p["r_wait"]) - 100
    r_go = sw("oh", flag("r_back", 2, ult_cooldown_mult=wait_mult), rockets)

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Rumble
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    casts = sw("oh", NONE, combine(
        sw("w_cd", NONE, pick(p["w_near"], "EnemyChampion", w_now)),
        sw("e_go", combine(*rm("e_go"), sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion", e_cast())))),
        sw("e_go2", sw("e_wait", NONE, combine(*rm("e_go2"),
                                               pick(p["e_range"], "EnemyChampion", harpoon(True))))),
        sw("q_go", combine(*rm("q_go"), sw("q_cd", NONE, pick(p["q_go"], "EnemyChampion", q_cast()))))))
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(heat_ctl, casts)))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ the slots
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"] * 4, p["r_ap"] * 4), hang, r_go), key="ult")
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] * p["q_n"], p["q_ap"] * p["q_n"]),
                           sw("oh", NONE, sw("q_cd", NONE, q_cast()))), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ap"]), sw("oh", NONE, sw("e_cd", NONE, e_cast()))), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("e_harpoon")]
    views_e = [E("a_hit"), E("oh_hit"), E("q_hit"), E("e_hit"), E("e2_hit"), E("dz_on", FX, 3), E("oh_on", BIG, 3),
               E("r_launch", BIG, -1), E("r_fall", BIG, -1, False)]
    # the Danger Zone's steam and Overheat's smoke rise from behind him (z -1: drawn over him they covered his face)
    views_b = [B_("w_shown", FX, 3, "w_shield"), B_("w_ms", FX, -1, "haste"), B_("dz", FX, -1, "dz_steam"),
               B_("oh", FX, -1, "oh_smoke"), B_("e_slow", FX, 3, "e_zap"), B_("r_slow", FX, -1, "burn")]
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Shield"],
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
