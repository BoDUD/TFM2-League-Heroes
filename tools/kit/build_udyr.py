"""Build league_udyr.data_champion (jungle, Melee: the Spirit Walker, four stances) from the parameters P.

    python tools/kit/build_udyr.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-22: JUNGLE, layout A - Q / E / R, Iron Mantle (W) folded into the passive, one action
set per stance; 「有连招要做连招」). TFM2 has three active slots: Wilding Claw (Q, the Bear) is `skill`, Blazing Stampede
(E, the Ram) `skill2`, Wingborne Storm (R, the Phoenix) the `ult`. A stance is a permanent caster flag (`st_q` /
`st_e` / `st_r`; none = his plain guard, League's Boar), set by its ability and taken off by the others; death clears
it. Every action reads it and plays the stance's own tags (q_* / e_* / r_*, CasterAnimation); idle, run, hit and death
are the add-on's view swap (league_gnar's way). Awakened (League's recast with ultimate benefits): Q or E cast while he
already stands in its stance (a 2-tick `*_wk` flag says so, so the branch is written once).
  passive Bridge Between (众灵纽带): every ability gives his next two attacks p_as% attack speed (`p2` -> `p1`, p_t
          ticks). Iron Mantle (坚铁甲胄, W, the Boar): the first ability after w_icd ticks (`w_icd` caster flag) also
          shields him w_sh + w_sh_r% AD for w_sh_t ticks and his next two attacks heal him w_heal + w_heal_r% AD each
          (`w2` -> `w1`). League casts W on demand; no data effect reads health, so the add-on moves it to low health.
  attack  A punch (100% AD on `Enemy`, a hidden homing strike), the stance's own swing (attack / q_attack / e_attack /
          r_attack). The charges are spent on the hit tick (so the swing's cooldown still has the attack speed).
  skill   Q Wilding Claw (狂暴爪击, the Bear, cooldown q_cd): a `Targeting` cast on `EnemyWithoutTower` (q_range: camps
          too). q_as% attack speed for q_t ticks and his next two attacks (`q2` -> `q1`) deal q_dmg + q_ratio% AD +
          q_thp% of the target's max health more. Awakened: q_as2% attack speed and both attacks call lightning on the
          target (`q_lit`): a splash of q2_dmg + q2_ratio% AD magic damage round it (q2_r).
  skill2  E Blazing Stampede (踏火蛮冲, the Ram, cooldown e_cd): a `Targeting` cast on `EnemyChampion` (e_range). e_ms%
          move speed for e_t ticks, he charges onto the champion (`MoveToTarget`) and his ramming blow stuns it
          (e_stun ticks; League: the first attack on each target stuns 0.75 s): e_dmg + 100% AD; the charge plays
          e_charge (the ram's run with its fire trail drawn in). Awakened: e_ms2% and
          `cc_immune` for e_imm ticks (League: immune to immobilizing effects).
  ult     R Wingborne Storm (极凌飓风, the Phoenix, cooldown r_cd): a `Targeting` cast on `EnemyChampion` (r_range). A
          glacial storm whirls round him for r_t ticks (`r_storm`): every r_gap ticks r_dmg + r_ratio% AD magic damage
          to every enemy within r_r and a r_slow% slow; when it ends the storm is unleashed (League's awakened R) at
          an enemy champion within r2_range: a splash of r2_dmg + r2_ratio% AD and a r2_slow% slow.
  combos  E -> Q (踏火蛮冲晕眩接狂暴爪击): the stun opens `q_go` for win_q ticks and a Q cast in it is awakened (League's
          Ram stun, then the awakened Bear on the stunned champion). Q -> R (狂暴爪击接极凌飓风): an empowered claw
          that hits a champion opens `r_go` for win_r ticks; R cast in it whirls faster (r_fast between pulses).
          The same stance twice is awakened (Q -> Q, E -> E). Every ability arms the passive's two quick attacks.
Pictures: the step-3 effects pack (tools/art/pack_udyr_fx.py: q_swipe and e_trail drawn into q_attack / e_run).
The add-on copy (--native, addons/league_udyr): Iron Mantle by his health - no ability triggers it; the passive
league_udyr:mantle shields him and arms the two healing attacks when his health falls under w_hp% (w_icd between), as
League's W is cast when he is hurt; the add-on also shows each stance's idle, run, hit and death (its view swap).
Timings: drafts until the frames exist (tools/art/rig_udyr.py MS; a frame's start in ticks = ms x 0.06): a_hit, q_dur,
e_go, e_hit, r_at.
Numbers: League 16.20 (CommunityDragon udyr.bin) read into the Melee jungle range; balanced on the classic-SDK
simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/ud_sim).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_udyr.data_champion")
ID = "league_udyr"
FX = "asset/league/effects/league_udyr_fx"
BIG = "asset/league/effects/league_udyr_big"

# League's Udyr (16.20, CommunityDragon udyr.bin): 664 +92 hp, 62 AD, 31 +4.7 armour, 32 +2.05 mr, 350 move, 125
# range, attack speed 0.65. P: after an ability his next two attacks +attack speed (1.5 s windows), a recast for the
# awakened version. Q: 20-80% attack speed 4 s, two attacks +3-8% of the target's max health; awakened: two lightning
# bolts of 1-2% max health splashing. W: 45-145 + 1.2% max health shield 4 s (+50% when awakened), two attacks heal
# 2-3.5% max health. E: 25-55% move speed 4 s, the first attack on each target stuns 0.75 s; awakened 1.5 s immune to
# immobilizing effects. R: a 370 storm 4 s, 20-100 magic a second and 15-30% slow; awakened it chases enemies and hits
# harder. Every ability cd 6 s.
P = {
    # stats (Melee jungle: league_warwick 1120 +105 hp, 92 +18 attack, 36 +7 def; the base junglers 120 +30, hp 900 +80)
    "hp": 1120, "hp_g": 100, "atk": 86, "atk_g": 16, "def": 36, "def_g": 7, "mr": 25, "mr_g": 4, "ms": 1050, "ms_g": 12,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 64, "a_hit": 9, "a_speed": 20000,
    # passive Bridge Between + Iron Mantle (W)
    "p_as": 30, "p_t": 180,
    "w_icd": 720, "w_sh": 70, "w_sh_r": 40, "w_sh_t": 240, "w_heal": 15, "w_heal_r": 20, "w_t": 300,
    "w_hp": 50,                     # the add-on: Iron Mantle when his health falls under this % (league_udyr:mantle)
    # Q Wilding Claw (the Bear)
    "q_cd": 360, "q_range": 30000, "q_dur": 12, "q_as": 30, "q_as2": 60, "q_t": 240,
    "q_dmg": 15, "q_ratio": 35, "q_thp": 4, "q2_dmg": 25, "q2_ratio": 35, "q2_r": 9000, "q2_speed": 30000,
    # E Blazing Stampede (the Ram)
    "e_cd": 600, "e_range": 50000, "e_dur": 10, "e_go": 6, "e_ms": 35, "e_ms2": 60, "e_t": 180, "e_imm": 90,
    "e_speed": 3500, "e_dash": 24, "e_hit_dur": 24, "e_hit": 8, "e_dmg": 25, "e_stun": 45,
    # R Wingborne Storm (the Phoenix)
    "r_cd": 2400, "r_range": 35000, "r_dur": 24, "r_at": 10, "r_t": 240, "r_gap": 30, "r_fast": 20, "r_r": 17000,
    "r_dmg": 18, "r_ratio": 22, "r_slow": 25, "r_slow_t": 40,
    "r2_range": 60000, "r2_speed": 6000, "r2_r": 12000, "r2_dmg": 60, "r2_ratio": 60, "r2_slow": 40, "r2_slow_t": 90,
    # the combo windows (E -> Q, Q -> R)
    "win_q": 300, "win_r": 240,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
}
STANCES = ("st_q", "st_e", "st_r")


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


def attack(dmg, ratio, hp=0, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def splash(name, speed, rng, effects):
    return {"type": "TargetSplashProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 5000,
            "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def by_stance(q, e, r, plain):
    """The bear's version while `st_q` holds, the ram's under `st_e`, the phoenix's under `st_r`, else his guard's."""
    return sw("st_q", q, sw("st_e", e, sw("st_r", r, plain)))


def enter(st):
    """Into a stance: the others off, this one on for good (death clears it)."""
    return combine(*rm(*[s for s in STANCES if s != st]), sw(st, NONE, flag(st, None)))


def spend(x, t, each, last=()):
    """One of two charges (`<x>2` -> `<x>1`, t ticks) spent: `each` runs for either, `last` with the second."""
    return sw(x + "2", combine(*rm(x + "2"), flag(x + "1", t), *each),
              sw(x + "1", combine(*rm(x + "1"), *each, *last)))


def awake(st, wk, extra=None):
    """A 2-tick `wk` flag when he already stands in `st` (or `extra`, a combo window, holds): read once below."""
    return combine(sw(st, flag(wk, 2)), sw(extra, flag(wk, 2)) if extra else None)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False):
    """native: the add-on's copy (addons/league_udyr) - Iron Mantle by his health there."""
    # ------------------------------------------------------------------ passive: Bridge Between + Iron Mantle
    quick = refresh("p2", p["p_t"], attack_speed_mult=p["p_as"])
    mantle = sw("w_icd", NONE, combine(flag("w_icd", p["w_icd"]), on_me(shield(p["w_sh"], p["w_sh_r"], p["w_sh_t"])),
                                       refresh("w_sh", p["w_sh_t"]), *rm("w1"), refresh("w2", p["w_t"]),
                                       cview("w_on"), sfx("w")))
    ability = combine(*rm("p1"), quick, None if native else mantle)   # every ability

    # ------------------------------------------------------------------ attack
    quick_spent = sw("p2", combine(*rm("p2"), flag("p1", p["p_t"], attack_speed_mult=p["p_as"])), combine(*rm("p1")))
    mend = spend("w", p["w_t"], [on_me(heal(p["w_heal"], p["w_heal_r"])), cview("w_heal")])
    plain = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    bolt = splash("q_bolt", p["q2_speed"], p["q2_r"], [magic(p["q2_dmg"], p["q2_ratio"]), view("q_bolt_hit"),
                                                       tsfx("q_bolt_hit")])
    claw = [homing("a_q", p["a_speed"], "Enemy", [attack(p["q_dmg"], 100 + p["q_ratio"], 0, p["q_thp"]),
                                                   view("q_hit"), tsfx("q_hit")]),
            homing("a_qc", p["a_speed"], "EnemyChampion", [refresh("r_go", p["win_r"])]),   # Q -> R
            sw("q_lit", combine(bolt, sfx("q_bolt")))]
    hit = sw("q2", NONE, sw("q1", NONE, homing("a_hit", p["a_speed"], "Enemy", plain)))
    swing = delayed(p["a_hit"] - 1, hit, spend("q", p["q_t"], claw, rm("q_lit")), mend, quick_spent)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(by_stance(combine(anim("q_attack", p["atk_dur"]), sfx("a_q")),
                                        combine(anim("e_attack", p["atk_dur"]), sfx("a_e")),
                                        combine(anim("r_attack", p["atk_dur"]), sfx("a_r")), sfx("a")), swing),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q Wilding Claw (the Bear)
    claws = lambda as_: combine(refresh("q_as", p["q_t"], attack_speed_mult=as_), *rm("q1"), refresh("q2", p["q_t"]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(awake("st_q", "q_wk", "q_go"), *rm("q_go"),
                           sw("q_wk", combine(claws(p["q_as2"]), refresh("q_lit", p["q_t"]), cview("q_wake"),
                                              sfx("q_wake")),
                              combine(claws(p["q_as"]), *rm("q_lit"), cview("q_on"), sfx("q"))),
                           *rm("q_wk"), enter("st_q"), ability, voice("vo_q", p)))

    # ------------------------------------------------------------------ E Blazing Stampede (the Ram)
    ram = [attack(p["e_dmg"], 100), {"type": "Stun", "duration": p["e_stun"]}, buff("e_stun", p["e_stun"]),
           view("e_hit"), tsfx("e_hit"), refresh("q_go", p["win_q"])]   # E -> Q
    land = [anim("e_stun", p["e_hit_dur"]), sfx("e_hit_swing"),
            delayed(p["e_hit"] - 1, alive(homing("e_ram", p["a_speed"], "EnemyChampion", ram)))]
    charge = alive(anim("e_charge", p["e_dash"]), sfx("e_dash"),
                   {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 20000, "end_effects": land})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(awake("st_e", "e_wk"),
                            sw("e_wk", combine(refresh("e_ms", p["e_t"], move_speed_mult=p["e_ms2"]),
                                               refresh("e_imm", p["e_imm"], cc_immune=True), cview("e_wake"),
                                               sfx("e_wake")),
                               combine(refresh("e_ms", p["e_t"], move_speed_mult=p["e_ms"]), cview("e_on"), sfx("e"))),
                            *rm("e_wk"), enter("st_e"), ability, voice("vo_e", p),
                            delayed(p["e_go"] - 1, charge)))

    # ------------------------------------------------------------------ R Wingborne Storm (the Phoenix)
    struck = [magic(p["r_dmg"], p["r_ratio"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
              view("r_hit"), tsfx("r_hit")]
    pulse = alive(around(p["r_r"], "EnemyWithoutTower", struck), sfx("r_pulse"))
    unleash = alive(pick(p["r2_range"], "EnemyChampion",
                         splash("r_rel", p["r2_speed"], p["r2_r"],
                                [magic(p["r2_dmg"], p["r2_ratio"]),
                                 buff("r2_slow", p["r2_slow_t"], move_speed_mult=-p["r2_slow"]),
                                 view("r_rel_hit"), tsfx("r_rel_hit")])), sfx("r_rel"))

    def storm(gap):
        k = p["r_t"] // gap
        return combine(refresh("r_storm", k * gap), *[delayed(p["r_at"] - 1 + i * gap, pulse) for i in range(k)],
                       delayed(p["r_at"] - 1 + k * gap, unleash))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(anim("ult", p["r_dur"]), sfx("r"), cview("r_on"), voice("vo_r", p), enter("st_r"), ability,
                         sw("r_go", combine(*rm("r_go"), storm(p["r_fast"])), storm(p["r_gap"]))))

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_bolt"), P_("r_rel", BIG)]
    views_e = [E("a_hit"), E("q_hit"), E("q_bolt_hit", BIG), E("q_on", FX, 3), E("q_wake", BIG, 3), E("e_on", FX, 3),
               E("e_wake", BIG, 3), E("e_hit"), E("r_on", FX, 3), E("r_hit"), E("r_rel_hit", BIG), E("w_on", BIG, 3),
               E("w_heal", FX, 3)]
    views_b = [B_("q_as", FX, -1), B_("e_ms", FX, -1), B_("e_imm", FX, 3), B_("e_stun", FX, 3), B_("r_storm", BIG, 3),
               B_("r_slow", FX, -1), B_("r2_slow", FX, -1, "r_slow"), B_("w_sh", BIG, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "Shield", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_udyr:mantle",
                          "params": {k: int(p[k]) for k in ("w_hp", "w_icd", "w_sh", "w_sh_r", "w_sh_t", "w_t")}}
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (addons/league_udyr)")
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
