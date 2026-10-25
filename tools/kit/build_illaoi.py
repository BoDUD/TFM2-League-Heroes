"""Build league_illaoi.data_champion (top, Melee fighter: the Kraken Priestess) from the parameters P.

    python tools/kit/build_illaoi.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-22: TOP, layout A - W / E / R, Q folded into the passive; 「有连招要做连招」; the add-on
「附加包就按这四项做」). TFM2 has three active slots: Harsh Lesson (W) is `skill`, Test of Spirit (E) `skill2`, Leap of
Faith (R) the `ult`.
  passive Prophet of an Elder God (古神先知, Tentacle Smash's Q folded in): tentacles. Data has no summons: a tentacle is
          zones on its spot for t_life ticks (league_heimerdinger's turrets), its picture one `ViewEffect` whose tag
          lasts that life. Four slots a-d (`t<s>_busy`): a new tentacle takes the first free one, so at most four
          stand. A slot strikes every t_per ticks at ONE enemy within t_r: two zones on the same spot, `EnemyChampion`
          first, then `EnemyWithoutTower`; the first that reaches an enemy lays the slot's 1-tick `t<s>_shot`, the
          others read it. A strike: t_dmg + t_ratio% AD (Tentacle Smash's damage and amp in it) and, on a champion,
          she heals p_heal + p_heal_r% AD (League: 5% of her missing health; no effect reads missing health).
          She grows one in front of her (t_place toward her target) on an attack at most every p_cd ticks (flag
          `p_cd`; League: every 20-10 s on terrain near her).
  attack  The idol swung down (100% AD on `Enemy`, a_hit ticks in).
  skill   W Harsh Lesson (严酷训诫, cooldown flag `w_cd`): a `Targeting` cast on `EnemyWithoutTower` (w_range). She
          leaps onto the target (`MoveToTarget`) and smashes it: w_dmg + w_ratio% AD + w_thp% of its max health (League:
          3-5% of the target's max health + 3.5% per 100 AD); every standing tentacle lashes it too (the data's stand-in
          for "nearby tentacles slam the target": one strike a slot, w_gap ticks apart). The target is marked `w_mark`
          for w_mark_t (the add-on's tentacles go for it first).
  skill2  E Test of Spirit (灵魂试炼, cooldown flag `e_cd`): a `Targeting` cast on `EnemyChampion` (e_range). A ghostly
          tentacle flies from the idol (a homing projectile): the champion's spirit is torn out for e_t ticks
          (`e_spirit`): damaged_amplify e_echo% (League: 25-45% of the spirit's damage echoed to the body) and slowed
          e_slow% for e_slow_t; when the spirit ends the champion is a Vessel for e_vt ticks (`e_vessel`) and a
          tentacle grows on its spot. The add-on copy makes the spirit real: echo on the hits it takes, the Vessel at
          once when the champion walks e_leash away from where its spirit was torn out.
  ult     R Leap of Faith (过界信仰): a `Targeting` cast on `EnemyChampion` (r_range). She leaps and smashes the idol into
          the ground: r_dmg + r_ratio% AD to every enemy within r_r, and a tentacle grows on each champion hit (free
          slots allowing). For r_on ticks (`r_on`) her tentacles strike every r_per ticks instead of t_per (League: 50%
          faster) and W's cooldown is w_cd_r (League: 2 s).
  combos  E -> W (灵魂试炼接严酷训诫): the spirit landing opens `w_go` for win_w ticks and W's cooldown left drops to a
          tenth (skill_cooldown_mult, league_ksante's R -> W refund) - she leaps at the champion she just pulled.
          R -> W (过界信仰接严酷训诫): the smash does the same. W -> tentacles (严酷训诫接触手齐抽): every tentacle lashes
          the leap's target.
The add-on copy (--native, addons/league_illaoi): the passive league_illaoi:prophet stands every new tentacle on the edge
of the map's walls nearest the spot the data chose (camille_wall's grid; in the open, where the data put it), makes the
spirit a real one (the echo and the leash) and turns every tentacle's strike to a Harsh-Lesson-marked or Vessel enemy in
reach first.
Timings: drafts until the frames exist (a frame's start in ticks = ms x 0.06): a_hit, w_dash, w_hit, e_rel, r_at.
Numbers: League 16.20 (CommunityDragon illaoi.bin) read into the Melee fighter range; balanced on the classic-SDK
simulations (kd.py --lane 0 against fighter, executioner, knight, berserker, lancer and pole_warrior, C:/t/il_sim).
2026-10-25: R's 40 s really waits now (the E -> W refund at its landing capped it to 4 s, 9.5 casts a game -> 5.2):
r_dmg 90 + 60% -> 160 + 95% AD, w_cd_r 120 -> 100: +1.39 / +1.08 -> +1.32 / +1.68 (seeds 1-8 / 9-16).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_illaoi.data_champion")
ID = "league_illaoi"
FX = "asset/league/effects/league_illaoi_fx"
BIG = "asset/league/effects/league_illaoi_big"
TENTACLE = "asset/league/effects/league_illaoi_tentacle"   # a tentacle's life: rising, idle sway, sinking (dense, PPU 1.5)
LASH = "asset/league/effects/league_illaoi_lash"           # a tentacle rearing and slamming down on its target (dense)
SOULS = "asset/league/effects/league_illaoi_souls"         # every League champion's spirit, tag = its id (illaoi_souls.py)

# League's Illaoi (16.20): 656 +115 hp, 65 AD, 35 +5 armour, 32 +2.05 mr, 350 move, 125 range, attack speed 0.625.
# Passive: tentacles 9-180 + 120% AD (Q: +10-30% tentacle damage), heal 5% missing health on a champion hit.
# W: 3-5% (+3.5% per 100 AD) of the target's max health, min 20-60, cd 4 s (2 s during R); leap 400 (225 + her range).
# E: 950 range, spirit 7 s, 25-45% echo, 80% slow 1.5 s, Vessel 4 s, leash 1500, cd 16-12 s.
# R: 150-550 + 50% bonus AD within 500, a tentacle per champion hit, 8 s of 50% faster tentacles, cd 120-70 s.
P = {
    # stats (Melee: league_ksante 1220 +115 hp, 82 +9 attack, 42 armour; league_renekton 940 +105, 77 +17)
    "hp": 1150, "hp_g": 110, "atk": 80, "atk_g": 10, "def": 36, "def_g": 7, "mr": 28, "mr_g": 4, "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 80, "a_hit": 14,
    # passive: tentacles
    "p_cd": 360, "p_reach": 60000, "t_place": 15000, "t_speed": 6000, "t_life": 360, "t_per": 90, "t_first": 40, "t_r": 30000,
    "t_dmg": 10, "t_ratio": 35, "p_heal": 6, "p_heal_r": 6,
    # the add-on's tentacles, League's way (the user, 2026-10-23: 「俄洛伊触手乱长 和英雄联盟逻辑不一样」, picked: on the walls,
    # else beside her; they strike only Harsh Lesson's target, spirits and Vessels): one grows every p_cd_1 ticks at level 1
    # down to p_cd_18 at 18 (League 20 - 10 s), lives t_long (League 60 s), at most t_most stand; Tentacle Smash folded
    # in: the nearest one lashes her attack's target once every q_cd (League Q 10 - 6 s); the spirit stands e_pull from
    # its body toward her, tethered
    "p_cd_1": 1200, "p_cd_18": 600, "t_long": 3600, "t_most": 4, "q_cd": 480, "e_pull": 40000,
    # skill: W Harsh Lesson
    "w_cd": 300, "w_cd_r": 100, "w_range": 45000, "w_dur": 30, "w_dash": 12, "w_speed": 6000, "w_hit": 6,
    "w_dmg": 30, "w_ratio": 50, "w_thp": 2, "w_gap": 6, "w_mark_t": 240,
    # skill2: E Test of Spirit
    "e_cd": 840, "e_range": 80000, "e_dur": 30, "e_rel": 12, "e_speed": 5000, "e_dmg": 20, "e_ratio": 20,
    "e_t": 300, "e_echo": 15, "e_slow": 50, "e_slow_t": 90, "e_vt": 240, "e_leash": 150000,
    # ult: R Leap of Faith
    "r_cd": 2400, "r_range": 40000, "r_dur": 40, "r_at": 26, "r_r": 45000, "r_dmg": 160, "r_ratio": 95, "r_on": 480,
    "r_per": 60,
    # combos
    "win_w": 90, "w_refund": 900,
    "vo_gap": 600,
    # 1 = the copy for addons/league_illaoi
    "native": 0,
}
SLOTS = "abcd"
NATIVE_KEYS = ("t_r", "t_life", "t_per", "t_first", "r_per", "t_dmg", "t_ratio", "p_heal", "p_heal_r", "r_r", "e_t",
               "e_echo", "e_leash", "e_vt", "w_mark_t", "w_gap", "p_reach", "t_place", "p_cd_1", "p_cd_18", "t_long",
               "t_most", "q_cd", "e_pull")


def soul_ids():
    """The champions league/effects/league_illaoi_souls holds (its tags), sorted."""
    with open(lp(os.path.join(REPO, "league", "effects", "league_illaoi_souls#anim.fanim")), encoding="utf-8-sig") as f:
        return sorted(t for t in json.load(f)["anims"] if not t.endswith("_l"))


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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, thp=0):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio, thp)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def place(name, speed, rng, end):
    """A hidden bolt that flies rng toward the target and hits nothing: its end_effects run where it stops
    (league_heimerdinger's turret)."""
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 0, "penetrate": True,
            "shape": circle(1), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, life, period, first, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": life, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive: the tentacles
    def strike(champ):
        """One tentacle strike on the zone's target (the lash drawn on it); a champion heals her."""
        return [attack(p["t_dmg"], p["t_ratio"]), view("lash"), view("p_slam"), view("p_hit"), tsfx("p_hit"),
                *([heal(p["p_heal"], p["p_heal_r"]), on_me(buff("p_heal", 36))] if champ else [])]

    def tentacle(s):
        """Slot s's tentacle on this spot: its picture, then two zones (champions first) striking one enemy a period;
        a second pair at R's faster period strikes instead while `r_on` lasts (the first pair waits it out)."""
        shot = f"t{s}_shot"
        fire = lambda champ: sw("r_on", NONE, sw(shot, NONE, combine(flag(shot, 1), *strike(champ))))
        fast = lambda champ: sw("r_on", sw(shot, NONE, combine(flag(shot, 1), *strike(champ))))
        out = [view("tentacle"), view("p_spawn"), sfx("p_spawn")]
        if native:
            out.append(flag(f"t{s}_new", 2))     # the add-on reads the spot (league_illaoi:prophet)
        out += [field(f"t{s}_ch", p["t_r"], p["t_life"], p["t_per"], p["t_first"], [fire(True)], "EnemyChampion"),
                field(f"t{s}_all", p["t_r"], p["t_life"], p["t_per"], p["t_first"], [fire(False)]),
                field(f"t{s}_rch", p["t_r"], p["t_life"], p["r_per"], p["t_first"], [fast(True)], "EnemyChampion"),
                field(f"t{s}_rall", p["t_r"], p["t_life"], p["r_per"], p["t_first"], [fast(False)])]
        return out

    def grow(where, kind, i=0):
        """A tentacle in the first free slot (all four up: none); `where` puts its effects on the spot. The add-on copy
        raises a 2-tick `<kind>_new` on her instead (league_illaoi:prophet stands the tentacle: p by her, r on every
        champion round her; the Vessel's own is the add-on's)."""
        if native:
            return flag(f"{kind}_new", 2) if kind != "v" else NONE
        s = SLOTS[i]
        put = combine(flag(f"t{s}_busy", p["t_life"]), where(tentacle(s)))
        return sw(f"t{s}_busy", NONE if i == len(SLOTS) - 1 else grow(where, kind, i + 1), put)

    ahead = lambda effects: place("t_place", p["t_speed"], p["t_place"], effects)
    on_spot = lambda target: (lambda effects: lob("t_lob", 1, effects, target))

    # ------------------------------------------------------------------ attack: the idol swung down
    # the add-on copy grows none here: league_illaoi:prophet grows them on its own timer, on the walls
    spawn = NONE if native else sw("p_cd", NONE, combine(flag("p_cd", p["p_cd"]), grow(ahead, "p")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sfx("a"), delayed(p["a_hit"] - 1, alive(
                          homing("a_hit_mis", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], 20000), spawn))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: W Harsh Lesson
    def lashes():
        """W -> tentacles: every standing tentacle lashes the leap's target, w_gap ticks apart."""
        return [delayed(1 + k * p["w_gap"], sw(f"t{s}_busy", combine(*strike(True))))
                for k, s in enumerate(SLOTS)]

    w_land = [attack(p["w_dmg"], p["w_ratio"], p["w_thp"]), view("w_slam"), tsfx("w_hit"),
              buff("w_mark", p["w_mark_t"]), *([] if native else lashes())]   # the add-on's tentacles lash the mark
    w_cast = combine(sw("r_on", refresh("w_cd", p["w_cd_r"]), refresh("w_cd", p["w_cd"])), *rm("w_go"),
                     {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"],
                      "end_effects": [delayed(p["w_hit"], alive(*w_land))]})
    skill = action("idle", 3, 60, 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["w_dmg"], p["w_ratio"], p["w_thp"]),
                           sw("w_cd", NONE, combine(anim("skill", p["w_dur"]), sfx("w"), voice("vo_w", p),
                                                    delayed(p["w_dash"] - 1, alive(w_cast))))),
                   key="skill")

    # ------------------------------------------------------------------ skill2: E Test of Spirit
    # the refund's skill_cooldown_mult caps the ult's remaining cooldown as well unless ult_cooldown_mult offsets it: R's
    # landing opened it too and Leap of Faith's 40 s fell to 4 (the user, 2026-10-25: 「俄洛伊大招释放进冷却之后直接从40秒
    # 一下跳到4秒」). W's real cooldown is the flag `w_cd` (its slot only idles 3 ticks), so the cut is the flag's too.
    open_w = combine(refresh("w_go", p["win_w"]),
                     refresh("w_ref", 2, skill_cooldown_mult=p["w_refund"], ult_cooldown_mult=-p["w_refund"]),
                     sw("w_cd", refresh("w_cd", p["w_cd"] * 100 // (100 + p["w_refund"]))))
    vessel = [buff("e_vessel", p["e_vt"]), view("e_break"), tsfx("e_break"), grow(on_spot("EnemyChampion"), "v")]
    spirit = buff("e_spirit", p["e_t"]) if native else buff("e_spirit", p["e_t"], damaged_amplify=p["e_echo"])
    e_hit = [attack(p["e_dmg"], p["e_ratio"]), spirit,
             buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), tsfx("e_hit"), open_w,
             *([] if native else [{"type": "AddCasted", "casted_type": "Bleed", "duration": p["e_t"] + 1,
                                   "period": p["e_t"], "effects": vessel}])]
    if native:
        e_hit.append(flag("e_new", 2))     # the add-on keeps the spirit: its spot, the echo, the leash, the Vessel
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"]),
                            sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"),
                                                     voice("vo_e", p),
                                                     delayed(p["e_rel"] - 1, alive(
                                                         homing("e_grab", "EnemyChampion", e_hit, p["e_speed"])))))),
                    key="skill2")

    # ------------------------------------------------------------------ ult: R Leap of Faith
    r_land = [view("r_slam"), sfx("r_slam"), refresh("r_on", p["r_on"]), on_me(buff("r_aura", p["r_on"])), open_w,
              around(p["r_r"], "EnemyWithoutTower", [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]),
              (flag("r_new", 2) if native else around(p["r_r"], "EnemyChampion", [grow(on_spot("EnemyChampion"), "r")]))]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"]), sfx("r"), voice("vo_r", p),
                         delayed(p["r_at"] - 1, alive(*r_land))))

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("e_grab")]     # the attack's 1-tick strike (a_hit_mis) has no picture
    views_e = [E("a_hit"), E("p_hit"), E("p_spawn", BIG, -2, False), E("p_slam", BIG, -2, False), E("w_slam", BIG, -2), E("e_break", FX, 3),
               E("r_slam", BIG, -2, False), E("r_hit"),
               {"type": "Animation", "name": n("tentacle"), "anim": TENTACLE, "tag": "idle", "z": 1,
                "is_follow": False},
               {"type": "Animation", "name": n("lash"), "anim": LASH, "tag": "idle", "z": 3, "is_follow": False},
               # the add-on's minute-long tentacle in parts (rising, a sway it plays again, sinking) and the torn-out
               # spirit standing on its own spot (league_illaoi:prophet plays them on a position)
               *[{"type": "Animation", "name": n(f"tentacle_{k}"), "anim": TENTACLE, "tag": k, "z": 1, "is_follow": False}
                 for k in ("rise", "sway", "sink")],
               E("e_soul", FX, 3, False) | {"tag": "e_spirit"},
               # the spirit struck: its flash on the spirit's spot (the add-on, with a pulse down the tether)
               E("e_echo", FX, 3, False)]
    views_p.append(Pj("e_tether"))     # a link of the spirit's tether (the add-on spawns a chain every tick)
    # the copy's spirit stands apart (e_soul, played by the add-on), not drawn over the body it was torn from
    views_b = [B_("p_heal", FX, 3), B_("w_mark", FX, 3), *([] if native else [B_("e_spirit", FX, 3)]),
               B_("e_vessel", FX, -1), B_("e_slow", FX, -1), B_("r_aura", BIG, -1)]
    extra = {}
    if native:
        # the copy: every League champion's own spirit (the user: 「灵魂能雕刻出每个英雄的形状吗」「只要做英雄联盟的」); the add-on
        # plays league_illaoi_soul_<id> on the spirit's spot, e_soul for a champion of another mod
        # (and its mirror <id>_l: an effect never turns with the unit, the add-on picks the side the body faces)
        views_e += [{"type": "Animation", "name": n(f"soul_{h}{side}"), "anim": SOULS, "tag": h + side, "z": 3,
                     "is_follow": False} for h in soul_ids() for side in ("", "_l")]
        extra["passive"] = {"passive_ref": f"{ID}:prophet", "params": {k: int(p[k]) for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Melee", **extra, "tags": ["AD", "Melee", "Tank", "Heal", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (native=1)")
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
