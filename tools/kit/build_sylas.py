"""Build league_sylas.data_champion (mid, Melee AP: the Unshackled) from the parameters P.

    python tools/kit/build_sylas.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: layout A - Q / E / R, the passive and W in the attack -, mid, R in two steps (steal,
then cast), an add-on with the stolen ult by the victim's class and the AI's combos; 「有连招要做连招」):
  passive Petricite Burst (破敌禁法): every spell he casts (Q, E, R and W's stab) stores a charge (`p_1`, `p_2`: two at
          most, p_t ticks; League stores one per cast); while he holds one he attacks p_as% faster, and his next attack
          spends one: he whirls his chains (`attack_p`) - the hit plus p_dmg + p_ratio% AP magic to every enemy within
          p_r of him.
  W       Kingslayer (弑君突刺), no slot of its own: when an enemy champion is within w_r of him and `w_cd` is off, his
          attack becomes the stab (`skill_w`): w_dmg + w_ratio% AP magic to that champion and w_heal + w_heal_r% AP
          healing (League heals up to 150% more with his missing health: no data effect reads health, the add-on's
          copy heals by it), then w_cd ticks of cooldown. A W cast stores a charge too.
  attack  The chain swing: a hidden homing strike (100% AD), or the whirl / the stab above.
  skill   Q Chain Lash (锁链鞭击), `Targeting` on `EnemyWithoutTower` (q_range; waves and camps too): his chains lash out
          and cross on the target's spot - every enemy on the lash (q_len long, q_w wide) takes q_dmg + q_ratio% AP and
          a q_slow% slow for q_slow_t ticks; q_wait ticks after the chains land (a hidden lob of q_fly ticks) the
          crossing bursts: q2_dmg + q2_ratio% AP to every enemy within q_r of it (a RangeProjectile whose `apply` is
          the wait).
  skill2  E Abscond / Abduct (潜掠/强掳), `Direction` on `EnemyChampion` (e_range): he dashes e_dash toward the champion
          (Abscond), then e_wind ticks later throws a chain (e_len) that stops on the FIRST enemy champion: e_dmg +
          e_ratio% AP, knocked up e_up ticks, and he pulls himself onto it (`MoveToTarget` from the hit, league_warwick
          R's way). League's chain stops on the first enemy of any kind; here only champions, so the AI never wastes it
          on a minion. COMBO E -> W: landing with Kingslayer ready, he stabs at once (the stab and its cooldown).
  ult     R Hijack (其人之道), two steps (no data effect copies another champion's ult):
          1. the steal: `Targeting` on `EnemyChampion` (r_range): a chain flies at the champion (r_dmg + r_ratio% AP,
             stunned r_stun ticks) and he holds "a stolen ult" (`r_have`, r_keep ticks); r_dur + 1 ticks later a
             3-tick `ult_cooldown_mult` caps the ult's cooldown at r_recast (league_khazix R's recast way), so it is
             ready again 1-2 s later;
          2. the stolen ult: with `r_have`, R hurls the stolen power at the champion's spot - every enemy within r2_r
             takes r2_dmg + r2_ratio% AP and is knocked up r2_up ticks - and the full cooldown runs. The same blast
             whoever was robbed; the add-on's copy picks one of five by the victim's class (league_viego_soul's
             classes: melee / range / mage / util / assassin).
The combos the AI cannot press from data (E -> Q on the champion he lands on, R kept for two or more champions, Q
first on a fleeing champion) are the add-on's AI hook league_sylas:combo (addons/league_sylas).
Timings: from tools/art/rig_sylas.py MS (a frame's start in ticks = ms x 0.06): the lash from 160 ms (a_rel 10), the
whirl from 100 ms (p_rel 7), the stab from 100 ms (w_rel 7), the slam from 110 ms (q_rel 7), the throw from 100 ms
(r_rel 7), the stolen ult's slam from 270 ms (r2_rel 17); each action as long as its strip.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_sylas.data_champion")
ID = "league_sylas"
FX = "asset/league/effects/league_sylas_fx"
BIG = "asset/league/effects/league_sylas_big"
CLASSES = ("melee", "range", "mage", "util", "assassin")

# League units x 100 = ours; radii count the unit's collision radius (~15000) on top.
P = {
    # stats (Melee AP like league_kassadin / league_diana / league_ekko: attack 80 +10, mp 50 +20, hp 920-950; Sylas is
    # a bruiser-mage: a little more health and armour); League's Sylas: 600 +122 hp, 61 AD, 29 armour, 32 mr, 340 move,
    # 175 range, attack speed 0.645
    "hp": 980, "hp_g": 96, "atk": 78, "atk_g": 9, "mp": 50, "mp_g": 20, "def": 28, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1100, "ms_g": 10,
    # attack (the chain swing)
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 58, "a_rel": 10, "a_speed": 20000,
    # passive Petricite Burst (League: one charge per cast, 4 s; +125% attack speed with a charge; the whirl 1.3 AD +
    # 25% AP magic around him)
    "p_t": 240, "p_as": 40, "p_dmg": 20, "p_ratio": 35, "p_r": 30000, "p_dur": 30, "p_rel": 7,
    # W Kingslayer (League: 400 range, 65-205 + 85% AP, heal 25-125 + 40% AP (+ up to 150% by missing health), cd 13-7 s)
    "w_cd": 540, "w_r": 34000, "w_dur": 30, "w_rel": 7, "w_dmg": 80, "w_ratio": 70, "w_heal": 40, "w_heal_r": 35,
    # Q Chain Lash (League: 775 range, 40-120 + 40% AP and 15-35% slow 1.5 s on the lash, 60-180? + 80% AP burst after
    # 0.6 s; cd 10-6 s)
    "q_cd": 420, "q_range": 60000, "q_dur": 30, "q_rel": 7, "q_len": 64000, "q_w": 7000, "q_speed": 6000,
    "q_dmg": 50, "q_ratio": 35, "q_slow": 25, "q_slow_t": 90, "q_fly": 8, "q_wait": 36, "q_r": 18000,
    "q2_dmg": 90, "q2_ratio": 65,
    # E Abscond / Abduct (League: a 400 dash, then an 800 chain: 65-205 + 100%? AP, knocked up 0.5 s, pulls him in;
    # cd 13-9 s)
    "e_cd": 660, "e_range": 70000, "e_dur": 34, "e_dash": 22000, "e_dspeed": 3500, "e_wind": 6, "e_len": 62000,
    "e_speed": 6000, "e_w": 7000, "e_dmg": 80, "e_ratio": 70, "e_up": 30, "e_fly": 4500, "e_pull_dur": 18,
    # R Hijack (League: 950 range; steals the ult, cd 80-30 s, the stolen ult's own cooldown after)
    "r_cd": 2700, "r_range": 70000, "r_dur": 30, "r_rel": 7, "r_speed": 6000, "r_dmg": 40, "r_ratio": 20,
    "r_stun": 30, "r_keep": 600, "r_recast": 90,
    "r2_dur": 36, "r2_rel": 17, "r2_fly": 12, "r2_r": 32000, "r2_dmg": 200, "r2_ratio": 80, "r2_up": 40,
    # the add-on's stolen ults by class (melee: a leap and a stunning slam; range: a long piercing arrow that slows;
    # util: a song that heals and shields the allies round him and slows the enemies; assassin: a blink onto the
    # champion, one heavy strike and a moment hidden; mage: the blast above), same damage budget
    "r2_leap": 6000, "r2_leap_t": 14, "r2_slam_r": 24000, "r2_stun": 60,
    "r2_aspeed": 7000, "r2_alen": 120000, "r2_aw": 9000, "r2_slow": 40, "r2_slow_t": 90,
    "r2_song_r": 45000, "r2_heal": 120, "r2_heal_r": 40, "r2_sh": 100, "r2_sh_r": 30, "r2_sh_t": 180,
    "r2_kill": 125, "r2_hide": 60,
    # the add-on: Kingslayer's heal grows up to w_miss% more with his missing health (League: up to 150% more)
    "w_miss": 150,
    # the add-on's real Hijack: while a robbed League champion's own ult plays, r2_ad% of his ability power is added to
    # his attack for r2_ad_t ticks (League converts a stolen ult's AD ratios to Sylas's AP)
    "r2_ad": 60, "r2_ad_t": 300,
    # his spoken lines, at most one every vo_gap ticks
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


def heal(amount, ap_ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap_ratio, "heal_type": "Caster"}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def around(r, target, effects):
    return {"type": "RangeEffect", "shape": circle(r), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=ap):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end=(), penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(width), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def lob(name, travel, end):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, wait=1, target="EnemyWithoutTower"):
    """A one-off circle on the spot; it hits `wait` ticks after it appears (champion-data: apply - 1)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": wait + 1, "apply": wait,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False, own=()):
    """native: the add-on's copy (addons/league_sylas) - Kingslayer's heal by missing health and the stolen ult by the
    victim's class; own: [(hero, ult effect)] the copy's real Hijack picks from (the League champions' own ults)."""
    # ------------------------------------------------------------------ the passive's charges
    charge = combine(sw("p_1", refresh("p_2", p["p_t"])), refresh("p_1", p["p_t"], attack_speed_mult=p["p_as"]))
    spend = sw("p_2", combine(*rm("p_2")), combine(*rm("p_1")))

    # ------------------------------------------------------------------ W Kingslayer (the stab)
    def stab(pose=True):
        """The stab on a champion within w_r; `pose` = with its own animation (not after E's pull, which plays it)."""
        mend = (on_me({"type": "Native", "effect_ref": "league_sylas:kingslayer"}) if native
                else on_me(heal(p["w_heal"], p["w_heal_r"])))
        hit = combine(sfx("w"), voice("vo_w", p), cview("w_heal"), mend,
                      pick(p["w_r"], "EnemyChampion", ap(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")))
        return combine(*([anim("skill_w", p["w_dur"])] if pose else []), flag("w_cd", p["w_cd"]), charge,
                       delayed(p["w_rel"] - 1, alive(hit)) if pose else hit)

    # ------------------------------------------------------------------ attack: the chain swing / the whirl / the stab
    strike = homing("a_chain", p["a_speed"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    plain = combine(sfx("a"), delayed(p["a_rel"] - 1, alive(strike)))
    whirl = combine(anim("attack_p", p["p_dur"]), sfx("p"),
                    delayed(p["p_rel"] - 1, alive(spend, strike, cview("p_spin"),
                                                  around(p["p_r"], "EnemyWithoutTower",
                                                         [ap(p["p_dmg"], p["p_ratio"]), view("p_hit")]))))
    swing = sw("p_1", whirl, plain)
    near = combine(pick(p["w_r"], "EnemyChampion", flag("w_near", 1)),
                   sw("w_near", combine(*rm("w_near"), sw("w_cd", swing, stab())), swing))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), near), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Chain Lash
    lash = [ap(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), view("q_hit"),
            tsfx("q_hit")]
    burst = [ap(p["q2_dmg"], p["q2_ratio"]), view("q_hit2")]
    cross = lob("q_mark", p["q_fly"], [view("q_cross"), sfx("q_boom"), zone("q_boom", p["q_r"], burst, p["q_wait"])])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] + p["q2_dmg"], p["q_ratio"] + p["q2_ratio"]), anim("skill", p["q_dur"]),
                           sfx("q"), voice("vo_q", p), charge,
                           delayed(p["q_rel"] - 1, alive(line("q_chain", p["q_speed"], p["q_len"], p["q_w"],
                                                              "EnemyWithoutTower", lash, penetrate=True), cross))))

    # ------------------------------------------------------------------ skill2: E Abscond / Abduct (+ E -> W)
    dash_t = -(-p["e_dash"] // p["e_dspeed"])
    land = [sw("w_cd", NONE, stab(pose=False))]
    caught = [ap(p["e_dmg"], p["e_ratio"]), {"type": "Airborne", "duration": p["e_up"]}, view("e_hit"), tsfx("e_hit"),
              anim("skill2_pull", p["e_pull_dur"]),
              {"type": "MoveToTarget", "speed": p["e_fly"], "range": p["e_len"] + 30000, "end_effects": land}]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Direction", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                            charge, {"type": "MoveTo", "speed": p["e_dspeed"], "range": p["e_dash"], "end_effects": []},
                            delayed(dash_t + p["e_wind"],
                                    alive(sfx("e2"), line("e_chain", p["e_speed"], p["e_len"], p["e_w"],
                                                          "EnemyChampion", caught)))))

    # ------------------------------------------------------------------ ult: R Hijack (steal, then the stolen ult)
    refund = refresh("r_ref", 3, ult_cooldown_mult=p["r_cd"] * 100 // p["r_recast"] - 100)
    stolen = [ap(p["r_dmg"], p["r_ratio"]), {"type": "Stun", "duration": p["r_stun"]}, view("r_steal"), tsfx("r_steal"),
              *([buff("r_mark", 3)] if native else []),
              on_me(refresh("r_have", p["r_keep"]), cview("r_got"))]
    steal = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                    delayed(p["r_rel"] - 1, alive(homing("r_hook", p["r_speed"], "EnemyChampion", stolen))),
                    delayed(p["r_dur"] + 1, sw("r_have", refund)))

    def blast():
        """The stolen ult hurled at the champion's spot (the main pack's one for everybody, the add-on's mage one)."""
        hit = [ap(p["r2_dmg"], p["r2_ratio"]), {"type": "Airborne", "duration": p["r2_up"]}, view("r2_hit")]
        return combine(sfx("r2"), lob("r2_fly", p["r2_fly"], [view("r2_boom"), sfx("r2_boom"),
                                                               zone("r2_zone", p["r2_r"], hit)]))

    def by_class():
        """The add-on's copy: the stolen ult by the robbed champion's class (`cls_<class>`, laid by the add-on's
        passive when the steal's chain lands), the mage one (the blast) when none is known."""
        k = p["r2_ratio"]
        melee = combine(sfx("r2"), anim("ult_dash", p["r2_leap_t"]),
                        {"type": "MoveToTarget", "speed": p["r2_leap"], "range": p["r_range"] + 30000,
                         "end_effects": [view("r2_slam"), sfx("r2_boom"),
                                         around(p["r2_slam_r"], "EnemyWithoutTower",
                                                [ap(p["r2_dmg"], k), {"type": "Stun", "duration": p["r2_stun"]},
                                                 view("r2_hit")])]})
        rng = combine(sfx("r2"), line("r2_arrow", p["r2_aspeed"], p["r2_alen"], p["r2_aw"], "EnemyWithoutTower",
                                      [ap(p["r2_dmg"], k), buff("r2_slow", p["r2_slow_t"],
                                                                move_speed_mult=-p["r2_slow"]), view("r2_hit")],
                                      penetrate=True))
        util = combine(sfx("r2"), cview("r2_song"),
                       around(p["r2_song_r"], "AllyChampion",
                              [{"type": "Heal", "amount": p["r2_heal"], "attack_ratio": 0, "ap_ratio": p["r2_heal_r"],
                                "heal_type": "Ally"},
                               {"type": "Shield", "amount": p["r2_sh"], "attack_ratio": 0, "ap_ratio": p["r2_sh_r"],
                                "tick": p["r2_sh_t"]}]),
                       around(p["r2_song_r"], "EnemyWithoutTower",
                              [ap(p["r2_dmg"] // 2, k // 2), buff("r2_slow", p["r2_slow_t"],
                                                                 move_speed_mult=-p["r2_slow"]), view("r2_hit")]))
        assassin = combine(sfx("r2"), {"type": "Teleport"}, cview("r2_blink"), sfx("r2_boom"),
                           ap(p["r2_dmg"] * p["r2_kill"] // 100, k * p["r2_kill"] // 100), view("r2_hit"),
                           on_me({"type": "CasterInvisible", "tick": p["r2_hide"]}))
        out = blast()
        for cls, eff in (("assassin", assassin), ("util", util), ("range", rng), ("melee", melee)):
            out = sw("cls_" + cls, eff, out)
        return combine(out, *rm(*("cls_" + c for c in CLASSES)))

    if native and own:
        # the add-on's real Hijack: the robbed League champion's own ult (`steal_<hero>`, laid with `r_real` by the
        # add-on's passive), its effect tree as he wrote it (addons/league_sylas/make_override.py), else by class;
        # `r_power_go` asks the passive for the ratio conversion (his AP as AD for the cast, League's way)
        theirs = combine(flag("r_power_go", 2), *[sw("steal_" + sid, eff) for sid, eff in own])
        after = sw("r_real", theirs, delayed(p["r2_rel"] - 1, alive(by_class())))
    else:
        after = delayed(p["r2_rel"] - 1, alive(by_class() if native else blast()))
    cast = combine(*rm("r_have"), anim("ult_cast", p["r2_dur"]), voice("vo_r2", p), after)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r2_dmg"], p["r2_ratio"]), charge, sw("r_have", cast, steal)))

    # ------------------------------------------------------------------ views (tools/art/pack_sylas_fx.py)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    views_p = [Pj("q_chain"), Pj("e_chain"), Pj("r_hook")]
    views_e = [E("a_hit"), E("p_spin", BIG, -1), E("p_hit"), E("w_hit"), E("w_heal", FX, 3), E("q_hit"),
               E("q_cross", BIG, -1, False), E("q_hit2"), E("e_hit"), E("r_steal"), E("r_got", FX, 3),
               E("r2_boom", BIG, -1, False), E("r2_hit")]
    views_b = [B_("p_1", FX, 3), B_("q_slow", FX, -1), B_("r_have", FX, 3)]
    if native:
        views_p.append(Pj("r2_arrow"))
        views_e += [E("r2_slam", BIG, -1, False), E("r2_song", BIG, -1), E("r2_blink", FX, 3)]
        views_b.append(dict(B_("r2_slow", FX, -1), tag="q_slow"))   # the slow ring of Chain Lash
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Melee", "CC", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_sylas:hijack",
                          "params": {k: int(p[k]) for k in ("w_heal", "w_heal_r", "w_miss", "w_r", "w_cd", "atk_range",
                                                            "q_range", "e_range", "e_dur", "r_range", "r_keep",
                                                            "r2_r", "r_cd", "r_dur", "r2_ad", "r2_ad_t")}}
    return kit


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
    kit = build(p, native=a.native)
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
