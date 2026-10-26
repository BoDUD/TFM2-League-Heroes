"""Build league_chogath.data_champion (top, Melee tank-mage, AP) from the parameters P.

    python tools/kit/build_chogath.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-19: top, layout A, the add-on league_chogath, Feast stacks 「变大可以无限 加生命」). TFM2
has three active slots for League's four buttons: Rupture is `skill`, Feral Scream `skill2`, Feast the `ult`; Vorpal
Spikes (League: three empowered attacks on a 8-4 s cooldown) and the passive ride in his attack.
  passive Carnivore (肉食者): a unit his attack kills heals him p_heal + p_ap% AP (League: 20-71 by level; the kill
          check of league_jinx on the attack's own hit, so any unit counts).
  attack  a claw swipe (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit.
  E       Vorpal Spikes (恐惧之刺, in the attack): with e_cd off he gets e_n charges for e_t ticks (e_cd counts from
          then); while a charge is up his attack is `attack_e` and also throws a line of spikes at the target (e_len
          long, e_w wide, through everything): e_dmg + e_ap% AP magic, e_slow% slow for e_slow_t, and on champions
          e_hp% of their max health as true damage (ApAttack has no target-health field; the add-on pays it as
          magic from the real max health).
  skill   Q Rupture (破裂), `Position` on `EnemyWithoutTower` (q_range): on q_rel the ground cracks at the point,
          q_delay ticks later the spikes burst out (radius q_r): q_dmg + q_ap% AP magic, knocked up q_up ticks and
          q_slow% slow for q_slow_t.
  skill2  W Feral Scream (野性尖叫), `Targeting` on `EnemyChampion` (w_range): on w_rel a cone (w_cone long,
          w_cos / 1000 = the cosine of its half angle) in front: w_dmg + w_ap% AP magic, silenced w_sil ticks.
  ult     R Feast (盛宴), `Targeting` on `EnemyChampionRecentlyAttacked` (r_range: not wasted on a champion at full
          health - league_darius R): he bites on r_rel: r_dmg + r_hp% of his max health true damage, plus r_ap% AP as
          magic through all magic resistance (league_ahri's true AP). A champion the bite kills is eaten: one more
          stack (a Permanent caster buff `r_stack` with r_stack_hp health, healed at once; no cap, the user's pick),
          and league.dll draws his body r_grow% bigger per stack (src/view.rs, the display counts `r_stack` on him).
          Permanent buffs end with his death (section 5), so the main pack loses the stacks when he dies.
  combos  Q -> W (-> R), League's Rupture into Feral Scream (the user: 「有连招要做连招」「都要帮我补」): Q's spikes
          throwing up an enemy champion open q_combo (a caster flag, q_combo ticks: the knock-up and a little more);
          W cast inside it screams at once (on tick w_fast, not w_rel - no rear-up wait), so the silence lands while
          the champion is still in the air, and the window is spent. Nothing else changes: W keeps its own slot and
          cooldown (the AI casts it when it is ready, as before), the damage is the same. R needs no window: Q's and
          W's hits make the champion `EnemyChampionRecentlyAttacked`, Feast's target (with the add-on only when the
          bite kills).
The add-on copy (addons/league_chogath/make_override.py): this same kit with the add-on's passive league_chogath:keep
(every Feast stack given back after his death, League's way); its AI hook league_chogath:feast presses R only when the
bite kills (real health and shields). The data needs no native effect: target_hp_ratio already reads the real maximum
health and the kill check finds the eaten.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_chogath.data_champion")
ID = "league_chogath"
FX = "asset/league/effects/league_chogath_fx"
BIG = "asset/league/effects/league_chogath_big"

# League units x 100 = ours for skill ranges (the pack's melee attack is 25000 against League's 125). League 16.20
# (Chogath.bin, rank 5 / 3): 644 +94 hp, 69 AD, 38 +4.5 armour, 32 +2.05 MR, 345 move, attack speed 0.658, range 125.
# Q Rupture 80-300 + 100% AP r 250 at 950, 0.627 s delay, knock-up 1 s, slow 60% 1.5 s, cd 6; W Feral Scream 80-280 + 70%
# AP, 60-degree cone 650, silence 1.6-2.4 s, cd 13-9; E Vorpal Spikes 3 attacks in 6 s, 22-82 + 30% AP + 3-4.25% max hp
# magic (+0.5% a Feast stack), slow 30-50% 1.5 s, cd 8-4; R Feast 300-650 + 50% AP + 10% bonus hp true on champions
# (1200 on monsters and minions), a kill +80-160 hp a stack and a bigger body (minion stacks up to 6), cd 80-60;
# passive Carnivore 20-71 hp on any kill.
# Numbers = the 10-min classic-SDK simulations (top lane 0 against fighter, executioner, lancer, pole_warrior, knight and
# berserker, three lineups, both sides, 2026-10-19): the draft (Q 90 +100% cd 7 s up 1 s, E 30 +30% +3%, W 80 +70%)
# +5.20 (base knight +0.39 in the same batch); Q 50 +60% cd 9 s up 0.75 s, E 20 +20% +2%, W 60 +50% = P: +1.72 / +1.83
# (seeds 1-8 / 9-16; league_volibear +1.39, league_gangplank +1.67). Ticks are a draft until the strips exist
# (rig_chogath.MS). Retimed to the strips (rig_chogath.MS, 2026-10-19): the attack's slam lands on tick 14 (frame 4,
# 230 ms), the spiked attack's too; Q ducks and stamps on tick 5 (frame 2 at 70 ms; 590 ms in all); W screams from the
# rear on tick 8 (frame 3; 650 ms); R bites on tick 6 (the lunge, frame 2 at 80 ms; 680 ms).
# Retimed: +1.81 / +2.02 (seeds 1-8 / 9-16), the numbers kept.
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5)
    "hp": 1150, "hp_g": 115, "atk": 80, "atk_g": 6, "mp": 30, "mp_g": 15, "def": 38, "def_g": 9, "mr": 30, "mr_g": 4,
    "ms": 980, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 30, "atk_cd": 76, "a_hit": 14,
    # passive Carnivore
    "p_heal": 35, "p_ap": 15,
    # E Vorpal Spikes (in the attack)
    "e_cd": 360, "e_n": 3, "e_t": 360, "e_dur": 30, "e_hit": 14, "e_len": 50000, "e_w": 17000, "e_dmg": 20, "e_ap": 20,
    "e_hp": 2, "e_slow": 35, "e_slow_t": 90,
    # the picture-only lines (Vorpal Spikes' volley, Feral Scream's cone) last as long as their pictures play
    # (tools/art/import_chogath_fx.py: e_pic 4 frames, 250 ms; w_wave 5 frames, 400 ms)
    "e_pic_t": 15, "w_pic_t": 24,
    # the pictures on him play while his body is down on all fours, the middle of it on his pivot (the user: 「特效对对
    # 齐啊」 - Vorpal Spikes' arc over his back came as he reared up, Feast's ring round his feet as he stood swallowing):
    # the arc on the spiked attack's last crouch (attack_e frame 6 from 410 ms), the ring once Feast's rear-up is over
    # (its crouch from 580 ms: the eat comes 10-13 ticks into the cast, the bite's flight and the kill check's 4)
    "e_arm_at": 25, "r_grow_at": 25,
    # Q Rupture
    "q_cd": 540, "q_range": 90000, "q_dur": 36, "q_rel": 5, "q_delay": 36, "q_r": 25000, "q_dmg": 50, "q_ap": 60,
    "q_up": 45, "q_slow": 60, "q_slow_t": 90,
    # W Feral Scream
    "w_cd": 660, "w_range": 45000, "w_dur": 39, "w_rel": 8, "w_cone": 55000, "w_cos": 866, "w_dmg": 60, "w_ap": 50,
    "w_sil": 108,
    # combo Q -> W: Q's burst on an enemy champion opens q_combo for q_combo ticks (the q_up knock-up + 15); W cast
    # inside it screams on tick w_fast (League: W while the Rupture's knock-up holds them)
    "q_combo": 60, "w_fast": 2,
    # R Feast
    "r_cd": 3600, "r_range": 30000, "r_dur": 41, "r_rel": 6, "r_dmg": 300, "r_hp": 5, "r_ap": 50,
    "r_stack_hp": 70, "r_grow": 30,
    # his sounds, at most one every vo_gap ticks
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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true(dmg, mine=0, hp=0):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": mine, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def heal(amount, ap_ratio=0):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap_ratio, "heal_type": "Caster"}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def cone(radius, cos, target, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, length, width, target, effects, delay=2):
    """A line from him to the attack's target (a `LineRangeProjectile` in a `Targeting` cast points at it), hitting
    once a tick after it appears."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a `Position` cast's point)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def kill_check(src, reward):
    """On a hit unit, around its damage: the flag before, the living target's clear after, the read on him later
    (league_jinx Get Excited!; a dead target's `Delayed` adds nothing, so the flag stays)."""
    k = f"k_{src}"
    return (combine(*rm(k), flag(k, 40)),
            combine(casted(3, 1, *rm(k)), on_me(delayed(4, sw(k, combine(*rm(k), reward))))))


def build(p):
    # ------------------------------------------------------------------ passive Carnivore + attack
    p_set, p_read = kill_check("a", combine(on_me(heal(p["p_heal"], p["p_ap"]), cview("p_heal")), sfx("p_heal")))
    blow = homing("a_blow", "Enemy", [p_set, attack(0, 100), view("a_hit"), tsfx("a_hit"), p_read], 8000)

    # ------------------------------------------------------------------ E Vorpal Spikes (in the attack)
    charges = [f"e{k}" for k in range(1, p["e_n"] + 1)]
    spiked = [magic(p["e_dmg"], p["e_ap"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
              view("e_hit"), tsfx("e_hit")]
    champ = [true(0, hp=p["e_hp"])]
    spikes = combine(sfx("e_spikes"), line("e_line", p["e_len"], p["e_w"], "EnemyWithoutTower", spiked),
                     line("e_champ", p["e_len"], p["e_w"], "EnemyChampion", champ),
                     line("e_pic", p["e_len"], p["e_w"], "Ally", [], delay=p["e_pic_t"]))
    # the charge used is taken from the top (e3 .. e1), the attack strip chosen as the attack starts
    spend = NONE
    for c in charges:                         # built inside out: the outermost switch asks for the highest charge
        spend = sw(c, combine(*rm(c)), spend)
    e_attack = combine(spend, anim("attack_e", p["e_dur"]), voice("vo_e", p),
                       delayed(p["e_hit"] - 1, sfx("a_swing"), blow, spikes))
    plain = delayed(p["a_hit"] - 1, sfx("a_swing"), blow)
    arm = sw("e_cd", NONE, combine(flag("e_cd", p["e_cd"]), *[flag(c, p["e_t"]) for c in charges],
                                   delayed(p["e_arm_at"], cview("e_arm"))))
    pick_attack = sw(charges[0], e_attack, plain)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(arm, pick_attack), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Rupture
    burst = [magic(p["q_dmg"], p["q_ap"]), {"type": "Airborne", "duration": p["q_up"]},
             buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), view("q_hit"), tsfx("q_hit")]
    # its champion-only twin (the same spot and tick) opens the Q -> W window on him
    combo = [on_me(refresh("q_combo", p["q_combo"]))]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, view("q_crack"), sfx("q_crack")),
                           delayed(p["q_rel"] - 1 + p["q_delay"], view("q_spikes"), sfx("q_burst"),
                                   zone("q_z", p["q_r"], burst), zone("q_zc", p["q_r"], combo, "EnemyChampion"))))

    # ------------------------------------------------------------------ skill2: W Feral Scream
    scream = [magic(p["w_dmg"], p["w_ap"]), {"type": "BlockSkill", "tick": p["w_sil"]}, buff("w_sil", p["w_sil"]),
              view("w_hit"), tsfx("w_hit")]
    def shout(at):
        return delayed(at - 1, sfx("w"), line("w_wave", p["w_cone"], 30000, "Ally", [], delay=p["w_pic_t"]),
                       cone(p["w_cone"], p["w_cos"], "EnemyWithoutTower", scream))
    # inside the Q -> W window the scream comes at once (the window spent), else on the rear-up's tick
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(voice("vo_w", p),
                            sw("q_combo", combine(*rm("q_combo"), shout(p["w_fast"])), shout(p["w_rel"]))))

    # ------------------------------------------------------------------ ult: R Feast
    grow = combine(flag("r_stack", None, hp=p["r_stack_hp"]),
                   on_me(heal(p["r_stack_hp"]), delayed(p["r_grow_at"], cview("r_grow"))),
                   delayed(p["r_grow_at"], sfx("r_grow")))
    r_set, r_read = kill_check("r", grow)
    bite = homing("r_bite", "EnemyChampion",
                  [r_set, on_me(flag("r_pen", 1, magic_resistance_penetration=100)), true(p["r_dmg"], mine=p["r_hp"]),
                   magic(0, p["r_ap"]), view("r_hit"), tsfx("r_hit"), r_read], 8000)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(sfx("r"), voice("vo_r", p), delayed(p["r_rel"] - 1, sfx("r_bite"), bite)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": False,
                                      "z": z}
    views_p = [Pj("e_pic"), Pj("w_wave", BIG)]
    views_e = [E("a_hit"), E("p_heal"), E("e_arm"), E("e_hit"), E("q_crack", BIG, -1, False),
               E("q_spikes", BIG, 3, False), E("q_hit"), E("w_hit"), E("r_hit", BIG),
               E("r_grow", BIG, -1)]            # the ring round his feet under him: his body hides its far side
    views_b = [B_("e_slow"), B_("q_slow"), B_("w_sil")]
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
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
