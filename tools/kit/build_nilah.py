"""Build league_nilah.data_champion (bottom lane, melee marksman) from the parameters P.

    python tools/kit/build_nilah.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-13: bottom lane melee ADC; Q as skill, E first and W while E is spent as skill2, R as ult;
the passive's healing in the main pack, the heal / shield boost near allies in the add-on addons/league_nilah; the pros'
combos):
  passive Joy Unending (喜色川流): the main pack's part is the healing - Formless Blade's empowered attacks heal for
          q_vamp% of their damage, Apotheosis heals and shields the allies round her. With native=1 (the add-on's
          copy) the passive league_nilah:joy adds League's part the data cannot read: heals and shields that allied
          champions within p_r give her, and that she gives them, are p_amp% bigger.
  attack  The whip-blade at the target (atk_range, a little over the melee 25000; the hit on a_st). While `q_on` lasts
          (Formless Blade's 4 s) the reach is q_add longer (a `range` caster buff: the AI also starts attacking from
          there), the swing is attack_q, and the whip cuts a cone (`DirDot` q_cone, `Forward`) through the target:
          q_spl% AD more to every enemy in it, the target too; q_vamp% life steal.
  skill   Q Formless Blade (游刃万变): a `Direction` cast on `EnemyWithoutTower` (q_range, waves and camps too): the whip
          lashes down the cast line - a hidden penetrating line (q_len, width q_w, speed q_speed; the whip is in her
          own frames) - q_dmg + q_ratio% AD to everyone on it, then `q_on` for q_t ticks. Within eq_t ticks of a
          Slipstream landing (`eq_on`) it is the spin instead (League's E -> Q): q_dmg + q_ratio% AD round her
          (q_spin_r). The cooldown is the caster flag `q_cd` (the slot's own is 60 ticks), so a spin set off by E or R
          spends it too.
  skill2  E Slipstream (纵情逐流) first: a `Targeting` cast on `EnemyChampion` (e_range). Two charges (`e_x1`, `e_x2`, each
          e_rc ticks: League's ammo) and e_gap ticks between two dashes. She dashes through the champion
          (`RushMoveToBack`, e_speed) and lands behind it: e_dmg + e_ratio% AD round her (e_rad), `eq_on` for eq_t
          ticks, and - the pros' E -> Q - with Formless Blade ready the spin at once. With both charges spent, W
          Jubilant Veil (轻纱飞漾, its cooldown w_cd): for w_t ticks no basic attack hurts her
          (`base_attack_damaged_reduce` 100, league_shen W's way), w_mred% less from skills (League: magic) and
          w_ms% move speed; allied champions within w_r at the cast get the same for w_ally_t ticks (League's touch).
  ult     R Apotheosis (神恩激荡): a `Targeting` cast on `EnemyChampion` (r_range). She spins r_t ticks (`CasterAnimation`
          ult): every r_per ticks r_tdmg + r_tratio% AD round her (r_rad); at the end r_dmg + r_ratio% AD and every
          enemy in r_rad is pulled to her (`Grab`, r_pull a tick: it stops at her); allied champions within r_ally (she
          too) heal r_heal + r_heal_ad% AD and get a r_sh + r_sh_ad% AD shield for r_sh_t ticks (League turns her
          damage into heals and shields). The pros' R -> Q: with Formless Blade ready the spin follows the pull.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_nilah.data_champion")
ID = "league_nilah"
FX = "asset/league/effects/league_nilah_fx"
BIG = "asset/league/effects/league_nilah_big"

# Draft timings until the strips: attack 24 ticks, the whip lands on tick 10; Formless Blade 22 (the lash on 9), the spin
# 20 (on 8); Slipstream's dash 9 ticks; Jubilant Veil 14; Apotheosis 60.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9; league_samira 112 / 1030 / 26;
    # Melee base hp 1000 def 30 mr 25 move 1000); League's Nilah: 570 +101 hp, 58 AD, 27 armour, 32 mr, 340 move,
    # 225 range (melee 125-175), attack speed 0.697
    "hp": 1000, "hp_g": 95, "atk": 104, "atk_g": 21, "def": 26, "def_g": 7, "mr": 18, "mr_g": 3, "ms": 1000, "ms_g": 10,
    "atk_range": 30000, "atk_dur": 24, "atk_cd": 56, "a_st": 10,
    # Q Formless Blade (League: 600 line, -10..50 + 100% AD, cd 4 s; then 4 s +125 range, the attacks cut a cone and heal
    # (20% crit-scaled); after E a spin round her)
    "q_cd": 300, "q_range": 60000, "q_dur": 22, "q_at": 9, "q_len": 62000, "q_w": 6000, "q_speed": 15000,
    "q_dmg": 40, "q_ratio": 110, "q_t": 240, "q_add": 12500, "q_vamp": 18, "q_spl": 40, "q_cone": 700,
    "q_spin_dur": 20, "q_spin_at": 8, "q_spin_r": 28000, "eq_t": 90,
    # E Slipstream (League: 2 charges, 26-16 s each, 550 range, dash 600 through the target at 2200, 50-110 + 20% AD)
    "s2_cd": 60, "e_range": 55000, "e_rc": 540, "e_gap": 40, "e_speed": 8000, "e_tick": 9, "e_dmg": 60, "e_ratio": 60,
    "e_rad": 16000,
    # W Jubilant Veil (League: 2.25 s dodges every attack, 25% less magic damage, 12.5-27.5% move speed; allies she
    # touches 1.5 s; cd 26-22 s)
    "w_cd": 1200, "w_t": 135, "w_ms": 20, "w_mred": 25, "w_ally_t": 90, "w_r": 18000, "w_dur": 14,
    # R Apotheosis (League: 1 s, 6 ticks of 15-35 + 18% bonus AD, the last 125-325 + 120% bonus AD and the pull, 400
    # radius; the damage on champions heals / shields allies; cd 110-80 s)
    "r_cd": 2400, "r_range": 35000, "r_rad": 38000, "r_t": 60, "r_per": 10, "r_tdmg": 12, "r_tratio": 20,
    "r_dmg": 100, "r_ratio": 110, "r_pull": 2500, "r_ally": 50000, "r_heal": 60, "r_heal_ad": 30, "r_sh": 60,
    "r_sh_ad": 30, "r_sh_t": 180,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # Joy Unending's heal / shield boost in the add-on (League: 7.5% heals, 15% shields, 1000 units)
    "p_amp": 15, "p_r": 100000,
    # 1 = the copy for addons/league_nilah: passive league_nilah:joy
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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def around(shape, target, effects, forward=None):
    return {"type": "RangeEffect", "shape": circle(shape) if isinstance(shape, int) else shape, "target": target,
            "apply_type": "AroundCaster" if forward is None else {"Forward": {"offset": forward}},
            "effects": list(effects)}


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


def build(p):
    # ------------------------------------------------------------------ Formless Blade's window
    q_on = refresh("q_on", p["q_t"], range=p["q_add"], vamp=p["q_vamp"])

    def spin(at=0):
        """Formless Blade as a spin round her (after Slipstream or Apotheosis); spends Q's cooldown."""
        hits = [attack(p["q_dmg"], p["q_ratio"]), view("eq_hit"), tsfx("eq_hit")]
        return combine(flag("q_cd", p["q_cd"]), *rm("eq_on"), anim("q_spin", p["q_spin_dur"]), sfx("eq"),
                       cview("eq_spin"), q_on,
                       delayed(at + p["q_spin_at"] - 1, around(p["q_spin_r"], "EnemyWithoutTower", hits)))

    # ------------------------------------------------------------------ attack
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    plain = combine(sfx("a_swing"), delayed(p["a_st"] - 1, homing("a_whip", 100000, "Enemy", hit)))
    cone = {"DirDot": {"radius": p["atk_range"] + p["q_add"] + 6000, "range": p["q_cone"]}}
    empowered = combine(anim("attack_q", p["atk_dur"]), sfx("qa_swing"),
                        delayed(p["a_st"] - 1, homing("qa_whip", 100000, "Enemy", hit),
                                around(cone, "EnemyWithoutTower",
                                       [attack(0, p["q_spl"]), view("qa_hit"), tsfx("qa_hit")], forward=1000)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      sw("q_on", empowered, plain), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Formless Blade
    lash_hits = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]
    lash = combine(flag("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p), q_on,
                   delayed(p["q_at"] - 1, line("q_lash", p["q_speed"], p["q_len"], p["q_w"], "EnemyWithoutTower",
                                               lash_hits)))
    skill = action("idle", 3, 60, 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   sw("q_cd", NONE, sw("eq_on", spin(), lash)), key="skill")

    # ------------------------------------------------------------------ skill2: E Slipstream, W Jubilant Veil
    def dash(charge):
        land = [around(p["e_rad"], "EnemyWithoutTower", [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]),
                refresh("eq_on", p["eq_t"]), sw("q_cd", NONE, spin())]
        return combine(flag(charge, p["e_rc"]), refresh("e_gap", p["e_gap"]), anim("skill2", p["e_tick"] + 2),
                       sfx("e"), voice("vo_e", p), cview("e_trail"),
                       {"type": "RushMoveToBack", "speed": p["e_speed"], "applied_effects": []},
                       delayed(p["e_tick"], *land))
    veil = dict(base_attack_damaged_reduce=100, skill_damaged_reduce=p["w_mred"], move_speed_mult=p["w_ms"])
    w_cast = combine(flag("w_cd", p["w_cd"]), anim("w_cast", p["w_dur"]), sfx("w"), voice("vo_w", p),
                     refresh("w_on", p["w_t"], **veil),
                     around(p["w_r"], "AllyNotSelf", [buff("w_ally", p["w_ally_t"], **veil), view("w_ally"),
                                                      tsfx("w_ally")]))
    veil_or_none = sw("w_cd", NONE, w_cast)
    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    sw("e_gap", NONE, sw("e_x1", sw("e_x2", veil_or_none, dash("e_x2")), dash("e_x1"))), key="skill2")

    # ------------------------------------------------------------------ ult: R Apotheosis
    tick_hits = [attack(p["r_tdmg"], p["r_tratio"]), view("r_hit"), tsfx("r_hit")]
    ticks = [delayed(k * p["r_per"], around(p["r_rad"], "EnemyWithoutTower", tick_hits))
             for k in range(1, p["r_t"] // p["r_per"])]
    finale = delayed(p["r_t"] - 1,
                     around(p["r_rad"], "EnemyWithoutTower",
                            [attack(p["r_dmg"], p["r_ratio"]), {"type": "Grab", "speed": p["r_pull"]},
                             view("r_pull"), tsfx("r_pull")]),
                     around(p["r_ally"], "AllyChampion",
                            [{"type": "Heal", "amount": p["r_heal"], "attack_ratio": p["r_heal_ad"], "ap_ratio": 0,
                              "heal_type": "Ally"},
                             {"type": "Shield", "amount": p["r_sh"], "attack_ratio": p["r_sh_ad"], "ap_ratio": 0,
                              "tick": p["r_sh_t"]},
                             view("r_heal"), tsfx("r_heal")]),
                     cview("r_burst"),
                     sw("q_cd", NONE, spin(1)))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(anim("ult", p["r_t"]), sfx("r"), voice("vo_r", p), cview("r_spin"), *ticks, finale),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_e = [E("a_hit"), E("qa_hit"), E("q_hit"), E("eq_hit"), E("eq_spin", BIG, 3), E("e_hit"), E("e_trail", FX, 1),
               E("w_ally"), E("r_hit"), E("r_pull"), E("r_heal"), E("r_spin", BIG, 3), E("r_burst", BIG, 3)]
    views_b = [B_("q_on", FX, 3), B_("w_on", BIG, 3), B_("w_ally", BIG, 3)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Melee", "Heal", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if p["native"]:
        kit["passive"] = {"passive_ref": "league_nilah:joy", "params": {"amp": p["p_amp"], "near": p["p_r"]}}
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
