"""Build league_qiyana.data_champion (jungle, Assassin: the Empress of the Elements) from the parameters P.

    python tools/kit/build_qiyana.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-22: JUNGLE, layout A - Q / E+W / R, the element chosen by the add-on by the situation;
「有连招要做连招」). TFM2 has three active slots: Edge of Ixtal (Q) is `skill`, Audacity (E) with Terrashape (W) folded in
`skill2`, Supreme Display of Talent (R) the `ult`. TFM2 has no terrain, so her element is a caster flag (`el_g` grass,
`el_w` river, `el_r` rock, each with `el_on`, Permanent until her Q spends it; League's enchant lasts until it is used
or changed), given by Terrashape.
  passive Royal Privilege (凌人贵气): her first hit on an enemy deals rp_dmg + rp_ratio% AD more. `SwitchByBuff` reads
          only the caster, so the main pack's rest is hers (league_ekko's way): a proc starts `rp_cd` (rp_cd ticks)
          and no hit procs while it runs. The add-on copy (--native) keeps League's per-target rule natively
          (league_qiyana:royal: each enemy once per rp_rest ticks).
          Terrashape's passive: while an element is on (`el_on`) she has w_as% attack speed and her attacks deal
          w_on + w_on_r% AD magic damage more.
  attack  A swing of the ring blade (100% AD on `Enemy`, a hidden homing strike on a_hit), the passive's proc.
  skill   Q Edge of Ixtal (以绪塔尔之锋, cooldown flag `q_cd`): a `Targeting` cast on `EnemyWithoutTower` (q_range: camps
          and waves too). The ring sweeps a cone in front of her (`DirDot` q_cone, `Forward`): q_dmg + q_ratio% AD to
          every enemy in it. With an element it is Elemental Wrath and spends it: river - a q_root-tick root, then a
          q_slow% slow for q_slow_t (League: 0.5 s root, then 20% 1 s); rock - q_rock + q_rock_r% AD more (League: more
          damage to enemies under 50% health: the add-on copy's league_qiyana:rock gives twice that, only under q_exec%
          health); grass - camouflage (`CasterInvisible` q_inv ticks) and q_ms% move speed (League: 3 s camouflage,
          20% haste).
  skill2  E Audacity (天纵之勇, cooldown flag `e_cd`) with W Terrashape (方圆塑令): a `Targeting` cast on
          `EnemyWithoutTower` (e_range). She dashes onto the target (`MoveToTarget`): e_dmg + e_ratio% AD, and the
          dash enchants her ring (League's W): the next element of the cycle grass -> river -> rock (pointer flags
          `nx_w`, `nx_r`; the add-on copy's league_qiyana:element picks it by the situation instead) and Q's cooldown
          is refreshed (League: W resets Q).
  ult     R Supreme Display of Talent (惊才绝景): a `Targeting` cast on `EnemyChampion` (r_range). She swings the ring and
          a shockwave runs at the champion (a hidden penetrating line, r_len, width r_w): r_dmg + r_ratio% AD to every
          enemy on it, knocked back (`Knockback` r_kb_speed x r_kb_t) and then stunned r_stun ticks (League stuns the
          ones that hit terrain or her elements; no terrain here, so every one).
  combos  E -> Q (天纵之勇 + 方圆塑令 -> 以绪塔尔之锋): the dash's landing casts the enchanted Q at once (the element just given,
          Q's cooldown just refreshed: League's E -> W -> Q). R -> E -> Q (惊才绝景 -> 天纵之勇 -> 以绪塔尔之锋): the shockwave's
          champion hit dashes her onto the stunned champion if E is ready (and so the enchanted Q), else Q at once if it
          is ready and the champion within reach.
Pictures: the step-3 effects pack (assets/source/qiyana/PROMPTS_FX.md; Gemini's, tools/art/import_qiyana_fx.py). The
forward ones - Q's sweep in four looks (none / river / rock / grass) and R's swing and ground burst - are drawn into her
frames (assets/source/native/qiyana_bake.json): the Q cast plays skill / skill_w / skill_r / skill_g by the element on
her ring at the cast.
The add-on copy (--native, addons/league_qiyana): the element by the situation, Royal Privilege per enemy, Edge of
Ixtal's rock execute.
Timings: drafts until the frames exist (a frame's start in ticks = ms x 0.06): a_hit, q_at, e_at, r_at.
Numbers: League 16.20 (CommunityDragon qiyana.bin) read into the Assassin jungle range; balanced on the classic-SDK
simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/qy_sim, 2026-10-22): candidate v2
+1.54 on seeds 1-8 and +1.95 on 9-16 (league_naafiri +1.60 on 1-8 the same day). The draft v0 (attack 100, Q 40 + 85%,
E 45 + 55%, R 90 + 90%, the passive 25 + 35% every 300 ticks) was -1.34, v1 (halfway) +0.34.
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
# range, attack speed 0.688. Passive: the first attack or ability on each enemy deals bonus damage. Q: 70-190 (+ bonus
# AD), cd 7 s, 525; river root 0.5 s then 20% slow 1 s, rock more damage under 50% health, grass camouflage 3 s and
# 20% haste. W: a 300 dash, Q's cooldown reset, while enchanted 15-35% attack speed and on-hit 8-40 + 20% bonus AD
# magic; cd 7 s. E: a 650 dash onto an enemy, 50-210 + 50% bonus AD, cd 11-7 s. R: a 950 shockwave, knock back, 0.5-1 s
# stun on terrain, 100-500 + 10% max health from the detonated terrain; cd 120 s.
P = {
    # stats (Assassin jungle: league_naafiri 940 +88 hp, 100 +18 attack, 26 +8 def; the base assassins 120 +30, 900 +80)
    "hp": 980, "hp_g": 88, "atk": 110, "atk_g": 20, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    "atk_range": 25000, "atk_dur": 25, "atk_cd": 58, "a_hit": 10, "a_speed": 20000,
    # passive Royal Privilege; Terrashape's enchant
    "rp_dmg": 40, "rp_ratio": 50, "rp_cd": 240, "rp_rest": 600,
    "w_as": 25, "w_on": 15, "w_on_r": 25,
    # skill: Q Edge of Ixtal
    "s_cd": 60, "q_cd": 360, "q_range": 30000, "q_dur": 24, "q_at": 10, "q_cone": 500, "q_reach": 34000,
    "q_dmg": 60, "q_ratio": 110,
    "q_root": 30, "q_slow": 25, "q_slow_t": 60,
    "q_rock": 25, "q_rock_r": 40, "q_exec": 50,
    "q_inv": 150, "q_ms": 25, "q_ms_t": 150,
    # skill2: E Audacity with W Terrashape
    "s2_cd": 60, "e_cd": 540, "e_range": 42000, "e_dur": 20, "e_speed": 4500, "e_at": 3, "e_dmg": 60, "e_ratio": 70,
    # ult: R Supreme Display of Talent
    "r_cd": 2700, "r_range": 45000, "r_dur": 40, "r_at": 16, "r_speed": 9000, "r_len": 60000, "r_w": 13000,
    "r_dmg": 120, "r_ratio": 120, "r_kb_speed": 2500, "r_kb_t": 10, "r_stun": 54, "r_q_reach": 33000,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_qiyana (Native effects for the element, Royal Privilege and the rock execute)
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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
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


def line(name, speed, rng, radius, target, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


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

    # ------------------------------------------------------------------ passive: Royal Privilege
    def royal():
        """The bonus on a unit already hit: once per rp_cd ticks (her own rest), the add-on copy per enemy."""
        if nat:
            return native("royal")
        return sw("rp_cd", NONE, combine(refresh("rp_cd", p["rp_cd"]), attack(p["rp_dmg"], p["rp_ratio"]),
                                         view("p_hit"), tsfx("p_hit")))

    # ------------------------------------------------------------------ Terrashape: the element (folded into E)
    def element(fields):
        return [*rm(*ELEMENTS, "el_on"), flag("el_on", None, attack_speed_mult=p["w_as"])] + fields

    def enchant():
        """The next element on her ring; Q's cooldown refreshed (League: W resets Q)."""
        if nat:
            give = native("element")      # the add-on picks it by the situation and adds the flags
        else:   # the cycle grass -> river -> rock (pointer flags: Q spends the element, not the pointer)
            give = sw("nx_w", combine(*element([flag("el_w", None)]), *rm("nx_w"), flag("nx_r", None)),
                      sw("nx_r", combine(*element([flag("el_r", None)]), *rm("nx_r")),
                         combine(*element([flag("el_g", None)]), flag("nx_w", None))))
        return combine(give, *rm("q_cd"), cview("w_on"), sfx("w_on"))

    # ------------------------------------------------------------------ skill: Q Edge of Ixtal
    cone = {"DirDot": {"radius": p["q_reach"], "range": p["q_cone"]}}

    def sweep(*extra, hit="q_hit"):
        return around(cone, "EnemyWithoutTower", [attack(p["q_dmg"], p["q_ratio"]), *extra, royal(), view(hit),
                                                   tsfx(hit)], forward=1000)

    rock_hit = native("rock") if nat else attack(p["q_rock"], p["q_rock_r"])
    wrath = sw("el_w", combine(sweep({"type": "Bind", "duration": p["q_root"]},
                                     buff("q_slow", p["q_root"] + p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                                     hit="q_w_hit")),
               sw("el_r", sweep(rock_hit, hit="q_r_hit"),
                  sw("el_g", combine(sweep(hit="q_g_hit"),
                                     on_me({"type": "CasterInvisible", "tick": p["q_inv"]}),
                                     refresh("q_haste", p["q_ms_t"], move_speed_mult=p["q_ms"])),
                     sweep())))
    # the sweep in front of her is drawn into her frames (it points forward: the client never mirrors an effect
    # picture), one copy of the cast per element: skill (none), skill_w (river), skill_r (rock), skill_g (grass),
    # picked at the cast - the element is already on her ring (assets/source/native/qiyana_bake.json)
    swing = sw("el_w", combine(anim("skill_w", p["q_dur"]), sfx("q_w")),
               sw("el_r", combine(anim("skill_r", p["q_dur"]), sfx("q_r")),
                  sw("el_g", combine(anim("skill_g", p["q_dur"]), sfx("q_g")),
                     combine(anim("skill", p["q_dur"]), sfx("q")))))

    def q_cast():
        return combine(refresh("q_cd", p["q_cd"]), swing, voice("vo_q", p),
                       delayed(p["q_at"] - 1, alive(wrath, *rm(*ELEMENTS, "el_on"))))

    skill = action("idle", 3, p["s_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q_cast()), key="skill")

    # ------------------------------------------------------------------ skill2: E Audacity + W Terrashape
    def e_body():
        land = [homing("e_hit", 100000, "EnemyWithoutTower",
                       [attack(p["e_dmg"], p["e_ratio"]), royal(), view("e_hit"), tsfx("e_hit")]),
                enchant(),
                q_cast()]                                  # the combo: the enchanted Q at once (E -> W -> Q)
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                       {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 20000,
                        "end_effects": [delayed(p["e_at"], alive(*land))]})

    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    sw("e_cd", NONE, e_body()), key="skill2")

    # ------------------------------------------------------------------ attack
    on_hit = sw("el_on", combine(magic(p["w_on"], p["w_on_r"]), view("w_hit")))
    a_hit = homing("a_hit", p["a_speed"], "Enemy", [attack(0, 100), on_hit, royal(), view("a_hit"), tsfx("a_hit")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["a_hit"] - 1, a_hit)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ ult: R Supreme Display of Talent
    struck = [attack(p["r_dmg"], p["r_ratio"]), {"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb_t"]},
              delayed(p["r_kb_t"], {"type": "Stun", "duration": p["r_stun"]}), royal(), view("r_hit"), tsfx("r_hit")]
    # the combo R -> E -> Q: the champion struck gets her dash (and so the enchanted Q), else Q if it is in reach
    follow = combine(refresh("r_go", 2),
                     delayed(p["r_kb_t"], alive(sw("e_cd", sw("q_cd", NONE, pick(p["r_q_reach"], "EnemyChampionInCC",
                                                                                 flag("r_near", 2))),
                                                   e_body()))))
    wave = line("r_wave", p["r_speed"], p["r_len"], p["r_w"], "EnemyWithoutTower", struck)
    wave_c = line("r_wave_c", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion",
                  [sw("r_go", NONE, follow)])
    q_near = delayed(p["r_kb_t"] + 2, alive(sw("r_near", combine(*rm("r_near"), q_cast()))))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),       # the swing and the burst: in her frames
                         delayed(p["r_at"] - 1, alive(wave, wave_c, sfx("r_burst"))),
                         delayed(p["r_at"] + 1, q_near)), key="ult")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("r_wave", BIG, 0)]
    views_e = [E("a_hit"), E("w_hit"), E("p_hit"), E("w_on", FX, 3), E("q_hit"), E("q_w_hit"), E("q_r_hit"),
               E("q_g_hit"), E("e_hit"), E("r_hit")]
    views_b = [B_("el_g", FX, 3), B_("el_w", FX, 3), B_("el_r", FX, 3), B_("q_slow", FX, 3), B_("q_haste", FX, -1)]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:empress",
                            "params": {k: int(p[k]) for k in ("rp_dmg", "rp_ratio", "rp_rest", "q_rock", "q_rock_r",
                                                              "q_exec", "w_as")}}
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
