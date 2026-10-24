"""Build league_kled.data_champion (top, Melee fighter, AD: Kled, the Cantankerous Cavalier) from the parameters P.

    python tools/kit/build_kled.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-24: TOP, layout A - Q / E / R, Violent Tendencies (W) folded into the attack, the
dismount with the add-on; 「有连招要做连招」).
TFM2 has three active slots for League's four buttons: Bear Trap on a Rope (Q; on foot Pocket Pistol) is `skill`,
Jousting (E) `skill2`, Chaaaaaaaarge!!! (R) the `ult`. Q and E keep their cooldowns in flags (`q_cd`, `e_cd`;
league_sejuani's) so the combos can cast them and a cast on foot spends nothing; a slot cast while its flag is up does
nothing (a 3-tick idle). Flags die with him: every life starts mounted with Q and E ready.
  passive Skaarl, the Cowardly Lizard (怯战蜥蜴斯嘎尔): Skaarl's health is a shield on him (sk_hp + sk_ad% AD, as long
          as a life) and `sk` a `WithShield` flag beside it (league_malphite's granite); the first action of a life
          mounts him (`on`). When the controller finds `on` and no `sk`, Skaarl has fled: `ft` (on foot, permanent)
          with dm_atk% less attack; the actions play the on-foot tags (f_*), E does nothing and R waits (its
          cooldown capped at r_wait ticks, league_gnar's empty cast). Courage (勇气): each attack hit asks one step,
          a hit on a champion and each Pocket Pistol hit on one two, and the controller one every c_time ticks; the
          controller climbs the ladder c1..c<c_n - 1>; at the top he remounts: Skaarl back with re_hp + re_ad% AD,
          re_ms% move speed for re_ms_t ticks, the next attack starts Violent Tendencies (combo).
          (Any other shield on him - R's own - also holds `sk`: the add-on keeps Skaarl's health itself.)
  attack  An axe blow (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; mounted or on foot.
          Violent Tendencies (暴烈秉性, W): off `w_cd` the next attack starts `vt` (w_as% attack speed, w_t ticks);
          `w_cd` starts with it; its fourth hit adds w_dmg + w_ratio% AD and w_pct% of the target's maximum health.
  skill   Mounted: Q Bear Trap on a Rope (飞索捕熊器), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): on q_rel the
          trap flies (a line stopping on the first enemy): q_dmg + q_ratio% AD; on a champion it is shackled - q_slow%
          slower for q_teth ticks, then q2_dmg + q2_ratio% AD and yanked toward him (`Grab`, q_pull x q_pull_t).
          On foot: Pocket Pistol (随身手枪): a blast toward the target (p_len long, p_rad wide, through everything):
          p_dmg + p_ratio% AD, he hops back (`MoveBack`, p_back x p_back_t) and each champion hit gives two courage.
  skill2  E Jousting (比武), mounted only, `Targeting` on `EnemyWithoutTower` (e_range, `e_cd`): he dashes through the
          target (`RushMoveToBack`): e_dmg + e_ratio% AD, e_ms% move speed for e_ms_t ticks. Through a champion he
          may joust again: e_gap ticks later the controller dashes back through a champion within e_range2 (the
          same damage).
  ult     R Chaaaaaaaarge!!! (冲啊——！！), mounted only, `Targeting` on `EnemyChampion` within r_range: a shield
          (r_sh + r_sh_ad% AD, r_sh_t ticks), allies round him r_ms% faster for r_ms_t, and Skaarl charges at the
          champion (`MoveToTarget` r_speed): the ram r_dmg + r_ratio% AD + r_pct% of its maximum health, knocked back
          (r_kb x r_kb_t), allies round the ram faster too.
  combos  Q yank -> E at once (飞索接比武: the controller dashes at the yanked champion when E is ready). E through a
          champion -> E again (League's recast) and its second pass -> Violent Tendencies ready (`w_cd` off). R's ram
          -> Q ready and thrown at the champion (`q_go`). Remount -> Violent Tendencies ready.
  controller An AddCasted pulse on him every ctl_p ticks (league_sejuani's, hung by his attack and the ult, only for
          Kled himself: `own`): the dismount, courage and the remount, the combos' casts.
The add-on copy (--native, addons/league_kled: everything League does that the data cannot): Skaarl's own health pool
(the data's shield is only the stand-in), the shackle broken when the champion walks q_break away, the whole body on
foot while `ft` holds (idle, run, hit), courage from time out of fights.
Timings: drafts until the frames exist (tools/art/rig_kled.py retimes them).
Numbers: League 16.21 read into the top fighter range (league_gnar, league_renekton, league_ksante), balanced on the
classic-SDK simulations (kd.py --lane 0 against fighter, executioner, knight, berserker, lancer and pole_warrior,
C:/t/kl_sim, 2026-10-24; league_gnar --native +0.01 / +0.59 on seeds 1-8 / 9-16): the draft (hp 760, attack 88, Skaarl
360 + 120%, on foot -20%, Q 40 / 60 + 120%, E 40 + 65%, W 30, R 60) -3.36; hp 920, attack 94, on foot -10%, Skaarl 420,
Q 50 / 80, E 55, W 40, R 90 -1.44; hp 1000 +90, attack 98 +17, defence 32, Skaarl 480 + 140%, Q 60 / 90 + 140% every
480, E 60 + 80% every 540, W 50 + 6%, R 110 -0.22 / +0.08; with hp 1040, attack 100, Skaarl 500 = P +0.48 / +0.09 (mean +0.29; Gnar +0.30).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_kled.data_champion")
ID = "league_kled"
FX = "asset/league/effects/league_kled_fx"
BIG = "asset/league/effects/league_kled_big"

# League's Kled (16.21): Kled 410 +84 hp, Skaarl 400 +(level) hp (bonus health only to Skaarl), 65 AD +3.5, 35 armour
# +5.2, 28 mr +2.05, 345 move, 125 range, 0.625 attack speed. Dismounted: -20% damage to champions (roughly), courage
# from hits (champions more), remount at 50% Skaarl health and a burst of speed. Q: 800 trap, 30-130 + 65% bonus AD, on
# a champion a 1.75 s shackle (slowed 40%) then 52-234 + 195% bonus AD and yanked; cd 11-7. Pocket Pistol: 700 cone,
# 30-105 + 120% bonus AD (x5 pellets on one target, 5% each), knocks him back. W: 4 hits at +150% attack speed, the
# 4th 20-100 + 4.5-8.5% max hp (+5% per 100 bonus AD); cd 14-6. E: 550 dash, 35-135 + 65% bonus AD, +50% move 1 s,
# recast through a champion hit, cd 14-10. R: charge 3500-4500, shield up to 200-400 + 300% bonus AD, ram 4-12% (+%
# bonus AD) max hp, allies on the trail up to +50% move speed, cd 140-110.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, def 30, mr 25, move 1000; league_gnar 1000 / 90)
    "hp": 1040, "hp_g": 90, "atk": 100, "atk_g": 17, "def": 32, "def_g": 8, "mr": 22, "mr_g": 4,
    "ms": 1050, "ms_g": 12, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 64, "a_hit": 11,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: Skaarl (a shield as long as a life), on foot, courage, the remount
    "sk_hp": 500, "sk_ad": 140, "sk_t": 36000, "dm_atk": 10,
    "c_n": 10, "c_time": 120, "re_hp": 180, "re_ad": 60, "re_ms": 40, "re_ms_t": 120,
    # W Violent Tendencies (in the attack)
    "w_cd": 600, "w_t": 240, "w_as": 150, "w_dmg": 50, "w_ratio": 30, "w_pct": 6,
    # skill: Q Bear Trap on a Rope / Pocket Pistol
    "q_cd": 480, "q_range": 55000, "q_dur": 24, "q_rel": 8, "q_speed": 9000, "q_rad": 3000, "q_dmg": 60,
    "q_ratio": 60, "q_teth": 90, "q_slow": 40, "q2_dmg": 90, "q2_ratio": 140, "q_pull": 2500, "q_pull_t": 8,
    "p_dur": 24, "p_rel": 8, "p_len": 45000, "p_rad": 9000, "p_speed": 20000, "p_dmg": 40, "p_ratio": 100,
    "p_back": 2000, "p_back_t": 6,
    # skill2: E Jousting
    "e_cd": 540, "e_range": 40000, "e_range2": 60000, "e_dur": 24, "e_go": 5, "e_speed": 3500, "e_dmg": 60,
    "e_ratio": 80, "e_ms": 50, "e_ms_t": 60, "e_gap": 40, "e_win": 150,
    # ult: R Chaaaaaaaarge!!!
    "r_cd": 5400, "r_range": 90000, "r_dur": 40, "r_go": 12, "r_speed": 3000, "r_sh": 150, "r_sh_ad": 150,
    "r_sh_t": 240, "r_dmg": 110, "r_ratio": 60, "r_pct": 8, "r_kb": 1500, "r_kb_t": 6, "r_ally": 40000, "r_ms": 40,
    "r_ms_t": 120, "r_wait": 600,
    # his spoken lines, at most one every vo_gap ticks
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
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else ("WithShield" if tick == "shield" else {"Time": {"tick": tick}})
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


def attack(dmg, ratio, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def line(name, speed, rng, radius, target, effects, penetrate=True, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def build(p):
    ctl_p = p["ctl_p"]
    haste = lambda name, pct, t: buff(name, t, move_speed_mult=pct)

    # ------------------------------------------------------------------ passive: Skaarl, courage
    # Skaarl's health: the shield first, then the WithShield flag that finds it (league_malphite's granite)
    mount = combine(flag("on", None), shield(p["sk_hp"], p["sk_ad"], p["sk_t"]), flag("sk", "shield"))
    life = sw("on", NONE, mount)   # the first action of a life mounts him
    steps = [f"c{k}" for k in range(1, int(p["c_n"]))]
    remount = combine(*rm("ft", *steps), shield(p["re_hp"], p["re_ad"], p["sk_t"]), flag("sk", "shield"),
                      on_me(haste("re_ms", p["re_ms_t"], p["re_ms"])), *rm("w_cd"), cview("remount"), sfx("remount"),
                      voice("vo_mount", p))
    ladder = flag(steps[0], None)
    for k, name in enumerate(steps):
        nxt = remount if k == len(steps) - 1 else combine(*rm(name), flag(steps[k + 1], None))
        ladder = sw(name, nxt, ladder)
    courage = ladder
    dismount = combine(flag("ft", None, attack_mult=-p["dm_atk"]), cview("dismount"), sfx("dismount"),
                       voice("vo_off", p))

    def ask(k):
        """A hit asks the controller for k steps of courage (on foot only; read and cleared there)."""
        return sw("ft", refresh("cg2" if k == 2 else "cg", ctl_p + 2))

    # ------------------------------------------------------------------ attack (+ W Violent Tendencies)
    def blow(extra=()):
        return homing("a_blow", "Enemy", [attack(0, 100), *extra, view("a_hit"), tsfx("a_hit"), ask(1)])

    fourth = [attack(p["w_dmg"], p["w_ratio"], target_hp=p["w_pct"]), view("w_hit"), tsfx("w_hit")]
    champ = homing("a_tw", "EnemyChampion", [ask(2)])
    vt_on = refresh("vt", p["w_t"], attack_speed_mult=p["w_as"])
    # the four hits of Violent Tendencies: v1..v3 count the ones before (on him), the fourth ends it
    w_step = sw("v3", combine(*rm("vt", "v1", "v2", "v3"), blow(fourth), sfx("w_last")),
                sw("v2", combine(*rm("v2"), flag("v3", p["w_t"]), blow()),
                   sw("v1", combine(*rm("v1"), flag("v2", p["w_t"]), blow()),
                      combine(flag("v1", p["w_t"]), blow()))))
    w_start = combine(vt_on, refresh("w_cd", p["w_cd"]), flag("v1", p["w_t"]), cview("w_on"), sfx("w"), voice("vo_w", p), blow())
    swing = sw("vt", w_step, sw("w_cd", blow(), w_start))
    hit_now = delayed(p["a_hit"] - 1, alive(sfx("a"), swing, champ))
    foot = sw("ft", anim("f_attack", p["atk_dur"]))

    # ------------------------------------------------------------------ Q Bear Trap on a Rope / Pocket Pistol
    def q_cast():
        # the yank, in the shackled champion's context q_teth ticks on; Q -> E (`e_go` for the controller)
        yank = [attack(p["q2_dmg"], p["q2_ratio"]), {"type": "Grab", "speed": p["q_pull"], "tick": p["q_pull_t"]},
                view("q_yank"), tsfx("q_yank"), on_me(refresh("e_go", ctl_p + p["q_pull_t"] + 6))]
        shackle = homing("q_tw", "EnemyChampion", [buff("q_slow", p["q_teth"], move_speed_mult=-p["q_slow"]),
                                                   view("q_mark"), delayed(p["q_teth"], *yank)])
        trap = line("q_trap", p["q_speed"], p["q_range"], p["q_rad"], "EnemyWithoutTower",
                    [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"), shackle], penetrate=False)
        return combine(refresh("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                       delayed(p["q_rel"] - 1, alive(trap)))

    def pistol():
        blast = line("p_blast", p["p_speed"], p["p_len"], p["p_rad"], "EnemyWithoutTower",
                     [attack(p["p_dmg"], p["p_ratio"]), view("p_hit"), tsfx("p_hit"),
                      homing("p_tw", "EnemyChampion", [ask(2)])])
        return combine(refresh("q_cd", p["q_cd"]), anim("f_skill", p["p_dur"]), sfx("p"), voice("vo_p", p),
                       delayed(p["p_rel"] - 1, alive(cview("p_flash"), blast,
                                                     {"type": "MoveBack", "speed": p["p_back"],
                                                      "tick": p["p_back_t"]})))

    # ------------------------------------------------------------------ E Jousting
    def joust(second):
        hits = [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]
        # through a champion: the first pass opens the recast (e_wait, then e_go2), the second readies W
        twin = (on_me(*rm("w_cd"), cview("w_ready")) if second else
                on_me(refresh("e_wait", p["e_gap"]), refresh("e_go2", p["e_gap"] + p["e_win"])))
        rush = {"type": "RushMoveToBack", "speed": p["e_speed"],
                "applied_effects": hits + [homing("e_tw", "EnemyChampion", [twin])]}
        return combine(anim("skill2", p["e_dur"]), sfx("e2" if second else "e"),
                       on_me(haste("e_ms", p["e_ms_t"], p["e_ms"])),
                       delayed(p["e_go"] - 1, alive(cview("e_dust"), rush)))

    def e_cast():
        return combine(refresh("e_cd", p["e_cd"]), *rm("e_go2", "e_wait"), voice("vo_e", p), joust(False))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Kled
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    # one step a pulse, the ladder written once: time asks one (`c_tm`), a champion hit's second step waits for the
    # next pulse (`cg2` -> `cg`)
    gains = combine(sw("c_tm", NONE, combine(flag("c_tm", p["c_time"]), refresh("cg", ctl_p + 2))),
                    sw("cg", combine(*rm("cg"), courage)),
                    sw("cg2", combine(*rm("cg2"), refresh("cg", ctl_p + 2))))
    mounted_combos = combine(
        sw("e_go", combine(*rm("e_go"), sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion", e_cast())))),
        sw("e_go2", sw("e_wait", NONE, combine(*rm("e_go2"),
                                               pick(p["e_range2"], "EnemyChampion", joust(True))))))
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        sw("on", sw("sk", NONE, sw("ft", NONE, dismount))),
        sw("ft", gains, mounted_combos),
        sw("q_go", sw("q_cd", combine(*rm("q_go")),
                      pick(p["q_range"], "EnemyChampion", combine(*rm("q_go"), sw("ft", pistol(), q_cast()))))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Chaaaaaaaarge!!!
    # the ram (a hidden blow on arrival); R -> Q: q_cd off and the controller throws Q at it (Kled's own: `own`)
    ram = homing("r_ram", "EnemyChampion", [attack(p["r_dmg"], p["r_ratio"], target_hp=p["r_pct"]),
                                            {"type": "Knockback", "speed": p["r_kb"], "tick": p["r_kb_t"]},
                                            view("r_hit"), tsfx("r_hit"),
                                            sw("own", on_me(*rm("q_cd"), refresh("q_go", 30)))])
    rally = around(p["r_ally"], "AllyChampion", haste("r_ms", p["r_ms_t"], p["r_ms"]))
    charge = combine(on_me(shield(p["r_sh"], p["r_sh_ad"], p["r_sh_t"])), rally, anim("ult", p["r_dur"]), sfx("r"),
                     voice("vo_r", p),
                     delayed(p["r_go"] - 1, alive(cview("r_trail"), {
                         "type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000,
                         "end_effects": [ram, rally, cview("r_crash"), sfx("r_crash")]})))
    # on foot R waits: the empty cast's cooldown capped at r_wait ticks (league_gnar's), ready again soon after he
    # remounts
    wait_mult = -(-p["r_cd"] * 100 // p["r_wait"]) - 100
    r_go = sw("ft", flag("r_back", 2, ult_cooldown_mult=wait_mult), charge)

    # ------------------------------------------------------------------ the slots
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), life, sw("own", NONE, flag("own", None)), hang, foot, hit_now),
                      atype="BaseAttack", cancel=True)
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"]), life, hang, r_go), key="ult")
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"]), life, sw("q_cd", NONE, sw("ft", pistol(), q_cast()))),
                   key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"]), life, sw("ft", NONE, sw("e_cd", NONE, e_cast()))),
                    key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("q_trap"), Pj("p_blast")]
    views_e = [E("a_hit"), E("w_hit"), E("w_on", FX, 3), E("w_ready", FX, 3), E("q_hit"), E("q_mark"), E("q_yank"),
               E("p_flash", FX, 3), E("p_hit"), E("e_dust", FX, -1, False), E("e_hit"), E("r_trail", BIG, -1),
               E("r_crash", BIG, -1, False), E("r_hit"), E("dismount", BIG, 3, False), E("remount", BIG, 3)]
    views_b = [B_("vt", FX, -1, "w_aura"), B_("q_slow", FX, 3, "q_rope"), B_("e_ms", FX, -1, "haste"),
               B_("r_ms", FX, -1, "haste"), B_("re_ms", FX, -1, "haste")]
    extra = {}
    if p["native"]:   # addons/league_kled: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_kled:skaarl",
                            "params": {k: p[k] for k in ("sk_hp", "sk_ad", "re_hp", "re_ad", "q_teth", "c_n")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Shield"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
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
