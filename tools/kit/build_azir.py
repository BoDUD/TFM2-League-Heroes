"""Build league_azir.data_champion (mid, Magician: the Emperor of the Sands) from the parameters P.

    python tools/kit/build_azir.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-23: MID, layout C - Conquering Sands / Shifting Sands / Emperor's Divide, Arise! and the
Sun Disc in the passive; combos E -> R, Q's landing -> the soldiers stab, R -> Q, E's hit -> one more soldier; R pushes
both ways: 「还有要会正会推和反面推 可以推回来英雄 大招」). TFM2 has three active slots: Conquering Sands (Q) is `skill`,
Shifting Sands (E) `skill2`, Emperor's Divide (R) the `ult`.
  passive Arise! (沙兵现身, W folded in): sand soldiers. Data has no summons: a soldier is a spot - a hidden lob's landing
          - holding a flat list of checkpoints every s_step ticks that re-stamp its picture (league_orianna's lying ball)
          and two stab zones (`RangePeriodProjectile`, champions first, league_illaoi's tentacles) for s_life ticks. Three
          slots a-c (`b<s>`, s_life ticks): a new soldier takes the first free one, so at most three stand. His attack
          raises `cmd` for cmd_t ticks: every soldier with an enemy within s_r stabs ONE of them then (the slot's lock
          `k<s>`), s_dmg + s_ap% AP; when no soldier stabbed (`stabbed`) his own sand bolt flies instead (100% AD;
          League: soldiers attack for him when the target is in their reach). An attack with p_cd off raises a soldier on
          its target's spot (League: W, two charges, 10 s soldiers).
          Generations: every soldier belongs to the generation that was up when it rose - gA, gB or neither (C) - and
          its checkpoints and zones go on only while that generation is up. Q moves the soldiers by starting the next
          generation (A -> B -> C -> A): the old ones stop at their next checkpoint and new ones rise where Q lands. A
          generation comes back after two Qs, and its old soldiers are gone by then while s_life <= q_cd + the R refund
          (build() checks it).
          The Sun Disc (太阳圆盘): the add-on's copy only (--native, the passive league_azir:disc - a tower ruin of his
          team; data cannot see towers).
  The controller. skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on the hero is not
          (league_orianna): his attacks hang one on him (ctl_t ticks, period ctl_p) unless `polling` says one runs. It
          runs Q's move (q_go) and E's soldier (e_go); the slots only raise those flags. With no controller yet in this
          life Q is the sand wave alone and E brings no soldier.
  attack  A sceptre point (`Targeting` on `Enemy`): the soldiers stab, else his bolt (a_rel).
  skill   Q Conquering Sands (狂沙猛攻, the slot's cooltime q_cd): a `Targeting` cast on `EnemyWithoutTower` (q_range). A
          sand wave flies at the target through everything, q_dmg + q_ap% AP and q_slow% for q_slow_t (League: the
          soldiers' paths, 25% slow 1 s). At an enemy champion the controller then moves every standing soldier to that
          champion's spot (with none standing it raises one there), and they stab at once (Q -> stab).
  skill2  E Shifting Sands (流沙移形, cooldown flag `e_cd`): a `Targeting` cast on `EnemyChampion` (e_range), only with
          a soldier standing (League: the dash goes to a soldier). A champion within e_self of him: he hops away
          (MoveBack) behind a shield. Else, with R ready (no `r_cd`), he dashes onto the champion behind e_sh + e_ap% AP of
          shield for e_t: e_dmg + e_ratio% AP round him on arrival, a soldier rises on the champion (E hit -> one more
          soldier) and `r_win` opens for win_r ticks (E -> R).
  ult     R Emperor's Divide (禁军之墙): a `Targeting` cast on `EnemyChampion` (r_range). A wall of guards charges from him
          toward the champion: r_dmg + r_ratio% AP and a Knockback (r_kb_speed x r_kb, away from him) on every enemy it
          meets. Two pushes: with `r_win` up (he just dashed onto the champion with E) he first rushes through it
          (`RushMoveToBack`, r_rush_at - league_leesin's insec) and the wall pushes it back toward his team (反推);
          otherwise the wall pushes them away from him (正推: peels a diver, or shoves a fight apart). Every champion the
          wall meets refunds Q (`q_ref`, skill_cooldown_mult q_refund for 2 ticks: R -> Q).
The add-on copy (--native, addons/league_azir): the passive league_azir:disc raises the Sun Disc on a fallen tower of his.
Action tags (the art): idle run attack hit dead skill skill2 ult.
Numbers: League 16.20 (CommunityDragon azir.bin) read into the Magician mid range (league_hwei, league_orianna);
balanced on the classic-SDK simulations (kd.py --lane 2, C:/t/az_sim, 2026-10-23; league_hwei +1.16 on the same games): the
draft -3.77 (the soldiers stab, every slot casts, too little damage); without E -2.30 against -2.08 (E about even), without
R -2.88 (R worth ~0.8); the stab is the lever (25+45% -> 65+90% AP), then reach 36000, a soldier every 150 ticks, attacks
every 80, more health and armour: +0.45 seeds 1-8, +1.53 seeds 9-16.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_azir.data_champion")
ID = "league_azir"
FX = "asset/league/effects/league_azir_fx"
BIG = "asset/league/effects/league_azir_big"
SOLDIER = "asset/league/effects/league_azir_soldier"   # a soldier standing (tags soldier_a/b/c: three places round a spot)
GUARD = "asset/league/effects/league_azir_guard"       # R's guards, front view (never turned or mirrored)

# League's Azir (16.20, CommunityDragon azir.bin): 575 +119 hp, 52 AD, 19 armour, 30 mr, 335 move, 525 range.
# W: soldiers 10 s, 2 charges, stab 50-170 + 55% AP (more soldiers on one target 25% each), reach 325. Q 740 range,
# 70-310 + 30% AP, 25% slow 1 s, cd 14-6. E 1100 dash, shield 80-320 + 70% AP 1.5 s, 60-260 + 40% AP, cd 22-16; a
# champion hit stops him and readies a soldier. R 200-600 + 75% AP, wall 600 wide pushed 250 forward, cd 120-90.
P = {
    # stats (Magician mid: league_hwei 940 +94 hp, league_orianna 860 +95, 76 +6 attack, 40 +20 ap)
    "hp": 1100, "hp_g": 92, "atk": 62, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 27, "def_g": 6, "mr": 28, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 52500, "atk_dur": 27, "atk_cd": 80, "a_rel": 10, "a_speed": 4500, "a_y": -3000,
    # passive: the soldiers
    "p_cd": 150, "s_life": 480, "s_step": 40, "s_r": 36000, "s_per": 2, "cmd_t": 2, "s_dmg": 65, "s_ap": 90,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # skill: Q Conquering Sands
    "q_cd": 480, "q_range": 75000, "q_dur": 24, "q_rel": 8, "q_speed": 5000, "q_w": 9000, "q_dmg": 110, "q_ap": 65,
    "q_slow": 25, "q_slow_t": 60, "q_travel": 12,
    # skill2: E Shifting Sands
    "e_cd": 900, "e_range": 55000, "e_dur": 24, "e_go_at": 6, "e_speed": 5000, "e_self": 25000, "e_back": 3500,
    "e_back_t": 8, "e_sh": 80, "e_ap": 60, "e_t": 90, "e_r": 18000, "e_dmg": 90, "e_ratio": 55, "e_near": 20000,
    "win_r": 90,
    # ult: R Emperor's Divide
    "r_cd": 2400, "r_range": 40000, "r_dur": 36, "r_at": 16, "r_rush_at": 6, "r_rush": 8000, "r_speed": 3000,
    "r_len": 60000, "r_w": 20000, "r_dmg": 260, "r_ratio": 90, "r_kb_speed": 3000, "r_kb": 18, "r_stamps": 5,
    "q_refund": 900,
    "vo_gap": 600,
    # 1 = the copy for addons/league_azir
    "native": 0,
}
SLOTS = "abc"
GENS = "ABC"
NATIVE_KEYS = ("s_life",)


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


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*rm("lives"), *effects)),
                   *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": True, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def place(name, speed, rng, end):
    """A hidden bolt that flies rng toward the target and hits nothing: its end_effects run where it stops."""
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 0, "penetrate": True,
            "shape": circle(1), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden 1-radius lob onto the target's spot: its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def field(name, radius, life, period, first, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": life, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def gate(g, effect):
    """Only while generation g is up: A = gA, B = gB, C = neither."""
    if g == "A":
        return sw("gA", effect)
    if g == "B":
        return sw("gB", effect)
    return sw("gA", NONE, sw("gB", NONE, effect))


def by_gen(make):
    """make(g) for the generation up now."""
    return sw("gA", make("A"), sw("gB", make("B"), make("C")))


NEXT = {"A": "B", "B": "C", "C": "A"}


def to_gen(g):
    """Start generation g (the old one's soldiers stop at their next checkpoint)."""
    return combine(*rm("gA", "gB"), *([flag("g" + g, None)] if g != "C" else []))


def build(p):
    if p["s_life"] > p["q_cd"] + p["s_step"]:
        raise SystemExit("s_life > q_cd + s_step: a generation could come back while its old soldiers stand")

    # ------------------------------------------------------------------ passive: the soldiers
    stab = [ap(p["s_dmg"], p["s_ap"]), view("s_stab"), tsfx("s_stab"), refresh("stabbed", 6)]

    def soldier(s, g):
        """Slot s's soldier of generation g on this spot (a landing's end_effects): its picture re-stamped every
        s_step ticks and two stab zones (champions first), all only while g is up."""
        poke = lambda: gate(g, sw("cmd", sw(f"k{s}", NONE, combine(flag(f"k{s}", p["cmd_t"] + 1), *stab))))
        out = [view("s_spawn"), sfx("s_spawn"), gate(g, view(f"sold_{s}"))]
        out += [delayed(t, gate(g, view(f"sold_{s}"))) for t in range(p["s_step"], p["s_life"], p["s_step"])]
        out += [field(f"s{s}_ch", p["s_r"], p["s_life"], p["s_per"], 1, [poke()], "EnemyChampion"),
                field(f"s{s}_all", p["s_r"], p["s_life"], p["s_per"], 1, [poke()])]
        return out

    def put(s, g, where):
        return combine(refresh(f"b{s}", p["s_life"]), where(soldier(s, g)))

    def rise(where, g, i=0):
        """A soldier of generation g in the first free slot (all three up: none)."""
        s = SLOTS[i]
        return sw(f"b{s}", NONE if i == len(SLOTS) - 1 else rise(where, g, i + 1), put(s, g, where))

    def any_up(name):
        """`name` up for a tick when a soldier stands."""
        return combine(*rm(name), *[sw(f"b{s}", refresh(name, 1)) for s in SLOTS])

    on_spot = lambda target: (lambda effects: lob("s_lob", 1, effects, target))

    # ------------------------------------------------------------------ the controller: Q's move, E's soldier
    def move(g):
        """Q at a champion from generation g: every standing soldier moves to its spot as generation NEXT[g] (none
        standing: one rises there), then they stab at once."""
        h = NEXT[g]
        land = [sw(f"m{s}", combine(*rm(f"m{s}"), *soldier(s, h))) for s in SLOTS]
        land += [view("q_land"), sfx("q_land"), delayed(2, refresh("cmd", p["cmd_t"]))]
        marks = [sw(f"b{s}", combine(refresh(f"m{s}", p["q_travel"] + 4), refresh(f"b{s}", p["s_life"])))
                 for s in SLOTS]
        none = combine(refresh("ma", p["q_travel"] + 4), refresh("ba", p["s_life"]))
        return combine(any_up("up"), sw("up", combine(*rm("up"), *marks), none), to_gen(h),
                       lob("q_move", p["q_travel"], land, "EnemyChampion"))

    q_move = pick(p["q_range"], "EnemyChampion", by_gen(move))
    e_soldier = pick(p["e_near"], "EnemyChampion", by_gen(lambda g: rise(on_spot("EnemyChampion"), g)))
    ctl = combine(refresh("polling", p["ctl_p"] + 2),
                  sw("q_go", combine(*rm("q_go"), q_move)),
                  sw("e_go", combine(*rm("e_go"), e_soldier)))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", p["ctl_p"] + 2), casted(p["ctl_t"], p["ctl_p"], ctl))))

    # ------------------------------------------------------------------ attack: the sceptre points
    spawn = sw("p_cd", NONE, combine(flag("p_cd", p["p_cd"]), by_gen(lambda g: rise(on_spot("Enemy"), g))))
    bolt = homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"], p["a_y"])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), hang, alive(spawn),
                              delayed(p["a_rel"] - 1, alive(sfx("a"), refresh("cmd", p["cmd_t"]))),
                              delayed(p["a_rel"] + p["cmd_t"] + 1, alive(sw("stabbed", NONE, bolt)))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Conquering Sands
    wave = line("q_wave", p["q_speed"], p["q_range"], p["q_w"], "EnemyWithoutTower",
                [ap(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                 view("q_hit"), tsfx("q_hit")])
    champ = combine(*rm("q_ch"), pick(p["q_range"], "EnemyChampion", flag("q_ch", 1)),
                    sw("q_ch", combine(*rm("q_ch"), sw("polling", refresh("q_go", 4)))))
    # the slot's own cooltime is Q's cooldown: R's refund (skill_cooldown_mult) shortens it
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ap"], ap), voice("vo_q", p), sfx("q"),
                           delayed(p["q_rel"] - 1, alive(wave, champ))))

    # ------------------------------------------------------------------ skill2: E Shifting Sands
    guard_ = combine(on_me(shield(p["e_sh"], p["e_ap"], p["e_t"])), cview("e_shield"))
    hop = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), guard_,
                  {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]})
    arrive = [cview("e_land"), sfx("e_land"),
              around(p["e_r"], "EnemyWithoutTower", [ap(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]),
              refresh("r_win", p["win_r"]), sw("polling", refresh("e_go", 4))]
    dash = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p), guard_,
                   delayed(p["e_go_at"] - 1, alive({"type": "MoveToTarget", "speed": p["e_speed"],
                                                    "range": p["e_range"], "end_effects": arrive})))
    near = combine(*rm("e_me"), pick(p["e_self"], "EnemyChampion", flag("e_me", 1)))
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap),
                            sw("e_cd", NONE, combine(any_up("e_up"), sw("e_up", combine(
                                *rm("e_up"), near,
                                sw("e_me", combine(*rm("e_me"), hop), sw("r_cd", NONE, dash))))))),
                    key="skill2")

    # ------------------------------------------------------------------ ult: R Emperor's Divide
    k = p["r_stamps"]
    stamps = [place(f"r_st{i}", p["r_speed"], p["r_len"] * i // k, [view("r_guards")]) for i in range(1, k + 1)]
    wall = combine(sfx("r_wall"), view("r_rise"),
                   line("r_wall", p["r_speed"], p["r_len"], p["r_w"], "EnemyWithoutTower",
                        [ap(p["r_dmg"], p["r_ratio"]), {"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb"]},
                         view("r_hit"), tsfx("r_hit")]),
                   line("r_wall_ch", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion",
                        [refresh("q_ref", 2, skill_cooldown_mult=p["q_refund"])]),
                   *stamps)
    behind = delayed(p["r_rush_at"] - 1, alive({"type": "RushMoveToBack", "speed": p["r_rush"], "applied_effects": []}))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), refresh("r_cd", p["r_cd"]), sfx("r"), voice("vo_r", p),
                         sw("r_win", combine(*rm("r_win"), behind)),
                         delayed(p["r_at"] - 1, alive(wall))))

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_bolt"), Pj("q_wave")]
    views_e = [E("a_hit"), E("s_stab", FX, 3), E("s_spawn", FX, 1, False), E("q_land", FX, 1, False), E("q_hit"),
               E("e_shield", FX, 3), E("e_land", FX, 1, False), E("e_hit"), E("r_rise", BIG, 1, False),
               E("r_guards", GUARD, 2, False, "charge"), E("r_hit")]
    views_e += [E(f"sold_{s}", SOLDIER, 1, False, f"soldier_{s}") for s in SLOTS]
    views_b = [B_("q_slow", FX, -1, "slow")]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": f"{ID}:disc", "params": {k_: int(p[k_]) for k_ in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Magician", **extra, "tags": ["AP", "Magic", "Range", "CC", "Shield"],
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (native=1)")
    a = ap_.parse_args()
    p = dict(P)
    if a.native:
        p["native"] = 1
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
