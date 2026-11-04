"""Build league_qiyana.data_champion (jungle, Assassin: the Empress of the Elements) from the parameters P.

    python tools/kit/build_qiyana.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-22: JUNGLE, layout A - Q / E+W / R; 「有连招要做连招」; 2026-11-04 reworked toward League
V26.21: 「奇亚娜很多机制和英雄联盟不一样 你仔细对比看看怎么改吧」). TFM2 has three active slots: Edge of Ixtal (Q) is
`skill`, Audacity (E) `skill2`, Supreme Display of Talent (R) the `ult`. Her element is a caster flag (`el_g` grass,
`el_w` river, `el_r` rock, each with `el_on`, Permanent until her Q spends it; League's enchant lasts until it is used
or changed). The main pack is data only (no terrain, no health, no 4th slot), so Terrashape (W) rides in E there; the
add-on copy (--native, addons/league_qiyana) has W as its own ability and reads the map.
  passive Royal Privilege (凌人贵气): her attacks and basic abilities (Q, E - not R) deal rp_dmg + rp_ratio% AD more to
          a unit not hit lately. `SwitchByBuff` reads only the caster, so the main pack's rest is hers (league_ekko's
          way): a proc starts `rp_cd` (rp_cd ticks) and no hit procs while it runs; a new element (Terrashape's enchant)
          clears it (League: gathering an element resets the rest for enemies procced with another one - the main
          pack's cycle always brings another). The add-on keeps League's rule natively: each enemy once per rp_rest
          ticks, cleared for the ones last procced with an element other than the one gathered.
          Terrashape's passive: while an element is on (`el_on`) she has w_as% attack speed and w_range more attack
          range, and her attacks and abilities deal w_on magic damage more (main pack: ApAttack, its ratio w_on_ap% is
          ability power; the add-on adds w_on_r% AD natively).
  attack  A swing of the ring blade (100% AD on `Enemy`, a hidden homing strike on a_hit), the passive's proc.
  skill   Q Edge of Ixtal (以绪塔尔之锋, cooldown flag `q_cd`): a `Targeting` cast on `EnemyWithoutTower` (q_range: camps
          and waves too). Plain: a line in front of her (`LineRangeProjectile` q_len, a band about q_hw + 10000 to
          either side): q_far% of q_dmg + q_ratio% AD to every enemy on it, the rest on the action's target (League:
          75% beyond the first). With an element it is Elemental Wrath and spends it: she hurls the blade (a
          non-penetrating `LinearProjectile` q2_len, picture `q_blade`) that blasts where it stops - the first enemy or
          its end - (a q2_blast circle: q_far% to all in it, the rest on the first): river - a q_root-tick root, then a
          q_slow% slow for q_slow_t (League: 0.5 s root, then 20% 1 s); rock - q_rock + q_rock_r% AD more (League:
          60% more under half health: the add-on reads health); grass - camouflage (`CasterInvisible` q_inv ticks)
          and q_ms% move speed (League: a field of grass for 3 s that ends when she acts or leaves it: the add-on).
  skill2  E Audacity (天纵之勇, cooldown flag `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range). She dashes onto
          the target (`MoveToTarget`): e_dmg + e_ratio% AD. Main pack: the dash also enchants her ring (W Terrashape,
          方圆塑令): the next element of the cycle grass -> river -> rock (pointer flags `nx_w`, `nx_r`) and Q's cooldown
          is refreshed (League: W resets Q). Add-on: plain Audacity (damage only with the target within e_reach at the
          landing), W by itself.
  ult     R Supreme Display of Talent (惊才绝景): a `Targeting` cast on `EnemyChampion` (r_range). Main pack: she swings
          the ring and a shockwave runs at the champion (a hidden penetrating line, r_len, width r_w): r_dmg +
          r_ratio% AD to every enemy on it and r_hp% of their maximum health to champions (a champion-only twin; the
          data cannot cap it on monsters), knocked back (`Knockback` r_kb_speed x r_kb_t) and then stunned r_stun ticks
          (League stuns only along the terrain it reaches: no terrain here, so every one). Add-on: League's windblast -
          knock-back only, stopped by the first wall, the shockwave along the brush and river it crossed and the wall's
          border (league_qiyana:r), cast only where that catches a champion.
  combos  E -> Q (天纵之勇 -> 以绪塔尔之锋): the dash's landing casts Q at once (main pack: the element just given, Q's
          cooldown just refreshed: League's E -> W -> Q; add-on: W first when it is ready, Q when ready). R -> E -> Q
          (惊才绝景 -> 天纵之勇 -> 以绪塔尔之锋): a champion struck (add-on: stunned by the shockwave) gets her dash if E is
          ready (and so Q), else Q at once if it is ready and the champion within reach.
Pictures: the step-3 effects pack (assets/source/qiyana/PROMPTS_FX.md; Gemini's, tools/art/import_qiyana_fx.py). The
forward ones - Q's sweep in four looks (none / river / rock / grass) and R's swing and ground burst - are drawn into her
frames (assets/source/native/qiyana_bake.json): the Q cast plays skill / skill_w / skill_r / skill_g by the element on
her ring at the cast. The thrown blade flies with R's ring (`league_qiyana_big` r_swing, a round ring: the same turned).
The add-on copy (--native, addons/league_qiyana): Q, E's hit, the attack's on-hit, W and R are native (league_qiyana:q,
:e, :hit, :r and the passive :empress, which also runs W Terrashape); the numbers ride in passive.params.
Timings: drafts until the frames exist (a frame's start in ticks = ms x 0.06): a_hit, q_at, e_at, r_at.
Numbers: League 16.20 (CommunityDragon qiyana.bin) read into the Assassin jungle range; balanced on the classic-SDK
simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/qy_sim, 2026-10-22): candidate v2
+1.54 on seeds 1-8 and +1.95 on 9-16 (league_naafiri +1.60 on 1-8 the same day). The draft v0 (attack 100, Q 40 + 85%,
E 45 + 55%, R 90 + 90%, the passive 25 + 35% every 300 ticks) was -1.34, v1 (halfway) +0.34. The 2026-11-04 rework
(main pack: the line and the thrown blade, R 50 + 90% and 10% of a champion's health for 120 + 120% and no Royal
Privilege on it, the element clearing the rest, the enchant's range and its magic on Q and E, river slow and grass haste
20%) on the same simulations (C:/t/al_sim, the old kit +1.54 / +1.95 again): +1.59 on seeds 1-8, +1.93 on 9-16 with
Royal Privilege still 40 + 50%; raised to 45 + 55% for the add-on's 25 s rest per enemy (League's rule, 10 s before) it is
+2.07 / +1.17, the same within the noise (+-0.5). The add-on (native code, not simulated) trades the 25 s rest, the line's
75%, Audacity's reach and R's terrain for W's own Q resets, the enchant's magic scaling with AD on every hit and 160% on
monsters.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_qiyana.data_champion")
ID = "league_qiyana"
FX = "asset/league/effects/league_qiyana_fx"
BIG = "asset/league/effects/league_qiyana_big"

# League's Qiyana (16.20, CommunityDragon qiyana.bin): 590 +115 hp, 64 AD, 31 +4.5 armour, 32 +2.05 mr, 335 move, 150
# range, attack speed 0.688. V26.21: Passive: her attacks and basic abilities deal 15-91 (+25% bonus AD) more to an enemy,
# once per 25 s each (gathering another element resets it). Q: 70-190 (+90% bonus AD), cd 7 s, a 525 x 140 line (75%
# beyond the first, 160% to monsters); with an element the blade is thrown 865 and blasts (250 wide) at the first enemy:
# river root 0.5 s then 20% slow 1 s, rock 60% more under 50% health (35% beyond the first), grass a field of
# camouflage and 20% haste for 3 s. W: a 300 dash gathering the element of the terrain targeted, Q's cooldown reset, cd
# 7 s; while enchanted 15-35% attack speed, +25 range and 8-40 (+20% bonus AD) (+45% AP) magic on attacks and abilities.
# E: a 650 dash at an enemy, 50-210 + 50% bonus AD if it is within 250 at the arrival, cd 11-7 s. R: an 875 windblast
# knocks back 375 (no damage), stops at terrain and detonates the river and brush it crossed and the terrain's border:
# 100-300 (+125% bonus AD) (+10% max health, capped on monsters) and a 0.5-1 s stun by proximity; cd 120 s.
P = {
    # stats (Assassin jungle: league_naafiri 940 +88 hp, 100 +18 attack, 26 +8 def; the base assassins 120 +30, 900 +80)
    "hp": 980, "hp_g": 88, "atk": 110, "atk_g": 20, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    "atk_range": 25000, "atk_dur": 25, "atk_cd": 58, "a_hit": 10, "a_speed": 20000,
    # passive Royal Privilege (main pack: her own rest rp_cd; add-on: each enemy once per rp_rest, 25 s)
    "rp_dmg": 45, "rp_ratio": 55, "rp_cd": 240, "rp_rest": 1500,
    # Terrashape's enchant (el_on): attack speed, attack range (League +25), magic on hits (+ w_on_r% AD in the add-on,
    # + w_on_ap% AP: the main pack's ApAttack ratio)
    "w_as": 25, "w_range": 1500, "w_on": 15, "w_on_r": 15, "w_on_ap": 45,
    # W Terrashape, the add-on's own ability: cooldown, dash, terrain reach, dash speed, a fight this near, out-of-combat
    # haste near the element held (League 3-11%)
    "w_cd": 420, "w_dash": 18000, "w_reach": 64000, "w_speed": 4500, "w_fight": 60000, "w_oc_ms": 8,
    # skill: Q Edge of Ixtal - the plain line (q_len; q_hw the half band beyond the body), Elemental Wrath's blade
    # (q2_len, q2_speed, q2_bw its radius beyond the body, q2_blast the blast's circle) and the add-on's action range
    "s_cd": 60, "q_cd": 360, "q_range": 30000, "q2_range": 46000, "q_dur": 24, "q_at": 10,
    "q_len": 31500, "q_hw": 7000, "q2_len": 52000, "q2_speed": 9000, "q2_bw": 4000, "q2_blast": 10000,
    "q_dmg": 60, "q_ratio": 110, "q_far": 75, "q_mon": 160,
    "q_root": 30, "q_slow": 20, "q_slow_t": 60,
    "q_rock": 25, "q_rock_r": 40, "q_exec": 50, "q_rock_pct": 60, "q_rock_far": 35,
    "q_inv": 150, "q_ms": 20, "q_ms_t": 150, "q_field_t": 180, "q_field_r": 30000,
    # skill2: E Audacity (with W Terrashape in the main pack)
    "s2_cd": 60, "e_cd": 540, "e_range": 42000, "e_dur": 20, "e_speed": 4500, "e_at": 3, "e_dmg": 60, "e_ratio": 70,
    "e_reach": 15000,
    # ult: R Supreme Display of Talent (r_stun the main pack's; the add-on's r_stun_min..r_stun_max by proximity, the
    # shockwave r_det ticks after the windblast, r_border off the wall, r_span along the terrain)
    "r_cd": 2700, "r_range": 45000, "r_dur": 40, "r_at": 16, "r_speed": 9000, "r_len": 60000, "r_w": 13000,
    "r_dmg": 50, "r_ratio": 90, "r_hp": 10, "r_mon_cap": 300, "r_kb_speed": 2500, "r_kb_t": 10, "r_stun": 54,
    "r_stun_min": 30, "r_stun_max": 60, "r_det": 16, "r_border": 12000, "r_span": 96000, "r_q_reach": 33000,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_qiyana (Native Q, E's hit, the attack's on-hit, W and R; numbers in passive.params)
    "native": 0,
}
# the numbers the add-on's natives read (passive.params; src/lib.rs `params!` has the same defaults)
NATIVE_PARAMS = ("rp_dmg", "rp_ratio", "rp_rest", "w_as", "w_range", "w_on", "w_on_r", "w_on_ap", "w_cd", "w_dash",
                 "w_reach", "w_speed", "w_fight", "w_oc_ms", "q_len", "q_hw", "q2_len", "q2_speed", "q2_bw", "q2_blast",
                 "q_dmg", "q_ratio", "q_far", "q_mon", "q_root", "q_slow", "q_slow_t", "q_exec", "q_rock_pct",
                 "q_rock_far", "q_ms", "q_field_t", "q_field_r", "e_dmg", "e_ratio", "e_reach", "r_len", "r_w",
                 "r_speed", "r_dmg", "r_ratio", "r_hp", "r_mon_cap", "r_kb_speed", "r_kb_t", "r_stun", "r_stun_min",
                 "r_stun_max", "r_det", "r_border", "r_span")


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


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def around(shape, target, effects, forward=None):
    return {"type": "RangeEffect", "shape": circle(shape) if isinstance(shape, int) else shape, "target": target,
            "apply_type": "AroundCaster" if forward is None else {"Forward": {"offset": forward}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, penetrate=True, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def band(name, length, width, target, effects):
    """A line from her through the action's target, hitting once the tick it appears (a `LineRangeProjectile` in a
    `Targeting` cast: a band about width + 15000 to either side of it, champion-data "Cone / fan")."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 2, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def zone(name, radius, target, effects):
    """A circle hitting once where it appears (a `RangeProjectile` in a projectile's `end_effects`)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


ELEMENTS = ("el_g", "el_w", "el_r")


def build(p):
    nat = bool(p["native"])
    far = p["q_far"]

    def split(d, r):
        """(the q_far% part every unit takes, the rest the first one takes)."""
        d1, r1 = d * far // 100, r * far // 100
        return (d1, r1), (d - d1, r - r1)

    # ------------------------------------------------------------------ passive: Royal Privilege
    def royal():
        """The bonus on a unit not hit lately: once per rp_cd ticks (her own rest). The add-on's natives keep League's
        rule (each enemy once per rp_rest)."""
        return sw("rp_cd", NONE, combine(refresh("rp_cd", p["rp_cd"]), attack(p["rp_dmg"], p["rp_ratio"]),
                                         view("p_hit"), tsfx("p_hit")))

    def w_magic():
        """Terrashape's magic on a hit while an element is on (ApAttack: its ratio is ability power)."""
        return sw("el_on", magic(p["w_on"], p["w_on_ap"]))

    # ------------------------------------------------------------------ Terrashape: the element (in E, main pack)
    def element(fields):
        return [*rm(*ELEMENTS, "el_on"), flag("el_on", None, attack_speed_mult=p["w_as"], range=p["w_range"])] + fields

    def enchant():
        """The next element on her ring (the cycle grass -> river -> rock; pointer flags: Q spends the element, not the
        pointer); Q's cooldown refreshed (League: W resets Q) and Royal Privilege's rest cleared (a new element)."""
        give = sw("nx_w", combine(*element([flag("el_w", None)]), *rm("nx_w"), flag("nx_r", None)),
                  sw("nx_r", combine(*element([flag("el_r", None)]), *rm("nx_r")),
                     combine(*element([flag("el_g", None)]), flag("nx_w", None))))
        return combine(give, *rm("q_cd", "rp_cd"), cview("w_on"), sfx("w_on"))

    # ------------------------------------------------------------------ skill: Q Edge of Ixtal
    (q1d, q1r), (q0d, q0r) = split(p["q_dmg"], p["q_ratio"])
    # plain: the line in front, q_far% to all on it and the rest to the action's target (League: 75% beyond the first)
    plain = combine(band("q_line", p["q_len"], max(p["q_hw"] - 5000, 0), "EnemyWithoutTower",
                         [attack(q1d, q1r), royal(), view("q_hit"), tsfx("q_hit")]),
                    attack(q0d, q0r))

    def blade(hit, *extra):
        """Elemental Wrath: the thrown blade stops on the first enemy (the rest of the damage) or at its end, and
        blasts there (q_far% to all in the circle, the element's effects, the enchant's magic)."""
        blast = zone("q_blast", p["q2_blast"], "EnemyWithoutTower",
                     [attack(q1d, q1r), *extra, w_magic(), royal(), view(hit), tsfx(hit)])
        return line("q_blade", p["q2_speed"], p["q2_len"], p["q2_bw"], "EnemyWithoutTower", [attack(q0d, q0r)],
                    penetrate=False, end=[blast])

    wrath = sw("el_w", blade("q_w_hit", {"type": "Bind", "duration": p["q_root"]},
                             buff("q_slow", p["q_root"] + p["q_slow_t"], move_speed_mult=-p["q_slow"])),
               sw("el_r", blade("q_r_hit", attack(p["q_rock"], p["q_rock_r"])),
                  sw("el_g", combine(blade("q_g_hit"), on_me({"type": "CasterInvisible", "tick": p["q_inv"]}),
                                     refresh("q_haste", p["q_ms_t"], move_speed_mult=p["q_ms"])),
                     plain)))
    # the sweep in front of her is drawn into her frames (it points forward: the client never mirrors an effect
    # picture), one copy of the cast per element: skill (none), skill_w (river), skill_r (rock), skill_g (grass),
    # picked at the cast - the element is already on her ring (assets/source/native/qiyana_bake.json)
    swing = sw("el_w", combine(anim("skill_w", p["q_dur"]), sfx("q_w")),
               sw("el_r", combine(anim("skill_r", p["q_dur"]), sfx("q_r")),
                  sw("el_g", combine(anim("skill_g", p["q_dur"]), sfx("q_g")),
                     combine(anim("skill", p["q_dur"]), sfx("q")))))

    def q_cast():
        # the add-on: league_qiyana:q reads the element and strikes (the line, or the blade and its blast)
        hit = native("q") if nat else wrath
        return combine(refresh("q_cd", p["q_cd"]), swing, voice("vo_q", p),
                       delayed(p["q_at"] - 1, alive(hit, *rm(*ELEMENTS, "el_on"))))

    # the add-on's range is Elemental Wrath's (its AI hook holds a plain Q until the target is in the line's reach)
    skill = action("idle", 3, p["s_cd"], 1, p["q2_range"] if nat else p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q_cast()), key="skill")

    # ------------------------------------------------------------------ skill2: E Audacity (+ W Terrashape)
    def e_body():
        if nat:
            # league_qiyana:e strikes (if the target is still in reach) and runs W when it is ready; Q if it is ready
            land = [native("e"), sw("q_cd", NONE, q_cast())]
        else:
            land = [homing("e_hit", 100000, "EnemyWithoutTower",
                           [attack(p["e_dmg"], p["e_ratio"]), w_magic(), royal(), view("e_hit"), tsfx("e_hit")]),
                    enchant(),
                    q_cast()]                              # the combo: the enchanted Q at once (E -> W -> Q)
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                       {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 20000,
                        "end_effects": [delayed(p["e_at"], alive(*land))]})

    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    sw("e_cd", NONE, e_body()), key="skill2")

    # ------------------------------------------------------------------ attack
    if nat:     # league_qiyana:hit: the enchant's magic, Royal Privilege per enemy, the grass field broken
        struck_a = [attack(0, 100), native("hit"), view("a_hit"), tsfx("a_hit")]
    else:
        struck_a = [attack(0, 100), sw("el_on", combine(magic(p["w_on"], p["w_on_ap"]), view("w_hit"))), royal(),
                    view("a_hit"), tsfx("a_hit")]
    a_hit = homing("a_hit", p["a_speed"], "Enemy", struck_a)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["a_hit"] - 1, a_hit)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ ult: R Supreme Display of Talent
    def follow_on():
        """The combo R -> E -> Q: the champion struck gets her dash (and so Q), else Q if it is in reach."""
        return sw("e_cd", sw("q_cd", NONE, pick(p["r_q_reach"], "EnemyChampionInCC", flag("r_near", 2))), e_body())

    if nat:
        # league_qiyana:r: the windblast (knock-back only, stopped by the first wall) and r_det ticks later the
        # shockwave along the terrain; a champion it stuns lays r_go on her, read here a tick or two after it (r_near,
        # a 2-tick flag, the tick after that)
        t_go = p["r_at"] - 1 + p["r_det"] + 2
        ult_eff = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),        # the swing and the burst: in her frames
                          delayed(p["r_at"] - 1, alive(native("r"), sfx("r_burst"))),
                          delayed(t_go, alive(sw("r_go", combine(*rm("r_go"), follow_on())))),
                          delayed(t_go + 1, alive(sw("r_near", combine(*rm("r_near"), q_cast())))))
    else:
        struck = [attack(p["r_dmg"], p["r_ratio"]),
                  {"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb_t"]},
                  delayed(p["r_kb_t"], {"type": "Stun", "duration": p["r_stun"]}), view("r_hit"), tsfx("r_hit")]
        follow = combine(refresh("r_go", 2), delayed(p["r_kb_t"], alive(follow_on())))
        wave = line("r_wave", p["r_speed"], p["r_len"], p["r_w"], "EnemyWithoutTower", struck)
        # the champion-only twin: r_hp% of the champion's maximum health (none on monsters: the data cannot cap it)
        wave_c = line("r_wave_c", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion",
                      [attack(0, 0, p["r_hp"]), sw("r_go", NONE, follow)])
        q_near = delayed(p["r_kb_t"] + 2, alive(sw("r_near", combine(*rm("r_near"), q_cast()))))
        ult_eff = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),        # the swing and the burst: in her frames
                          delayed(p["r_at"] - 1, alive(wave, wave_c, sfx("r_burst"))),
                          delayed(p["r_at"] + 1, q_near))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", ult_eff, key="ult")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the thrown blade: R's ring (round, so the same turned any way)
    views_p = [P_("r_wave", BIG, 0), P_("q_blade", BIG, 2, tag="r_swing")]
    views_e = [E("a_hit"), E("w_hit"), E("p_hit"), E("w_on", FX, 3), E("q_hit"), E("q_w_hit"), E("q_r_hit"),
               E("q_g_hit"), E("e_hit"), E("r_hit")]
    views_b = [B_("el_g", FX, 3), B_("el_w", FX, 3), B_("el_r", FX, 3), B_("q_slow", FX, 3), B_("q_haste", FX, -1)]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:empress", "params": {k: int(p[k]) for k in NATIVE_PARAMS}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"], **extra,
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
