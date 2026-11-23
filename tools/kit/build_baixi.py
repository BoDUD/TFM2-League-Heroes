#!/usr/bin/env python3
"""Build all 5 Baixi champions' .data_champion files from tunable parameter tables.

    python baixi_dev/tools/build_baixi_kits.py [--plain] [--out-dir DIR] [--hero NAME] [--set k=v ...]
"""
import argparse
import json
import os

WS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MOD_ID = "baixi"
OUT_DIR = os.path.join(WS, MOD_ID, "champion")

# ======================================================================
# Parameter tables (initial drafts from 百戏设计书.pdf, tuned by lb_sim)
# Ticks: 60 / sec. Melee range ~26000-27000, Range ~50000-60000.
# ======================================================================

P_DIANJING = {
    # Top Melee Fighter (target kill diff: +1.4)
    "hp": 1188, "hp_g": 108, "atk": 96, "atk_g": 17, "apw": 0, "apw_g": 0,
    "def": 40, "def_g": 7, "mr": 32, "mr_g": 5, "ms": 1046, "ms_g": 11,
    "atk_range": 27000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
    # Passive 鼓点 (every 3rd AA -> Lion Bite)
    "p_dmg": 39, "p_ad": 59, "p_heal": 64, "p_heal_ad": 17,
    # Q 采青 (leap + bite + slow + cabbage heal)
    "q_cd": 490, "q_range": 45000, "q_dur": 36, "q_speed": 6500,
    "q_dmg": 69, "q_ad": 106, "q_slow": 30, "q_slow_t": 90, "q_heal": 37, "q_heal_ad": 27,
    # W 狮被旋 (30k spin + 3s shield)
    "e_cd": 600, "e_range": 30000, "e_dur": 42, "e_hit": 16,
    "e_r": 30000, "e_dmg": 59, "e_ad": 79, "e_sh": 158, "e_sh_ad": 36, "e_sh_t": 180,
    # R 醒狮 (35k roar + 1s taunt + 5s 29% DR & +39% AS)
    "r_cd": 3000, "r_range": 35000, "r_dur": 54, "r_hit": 18,
    "r_r": 35000, "r_dmg": 98, "r_ad": 98, "r_taunt": 60,
    "r_t": 300, "r_dr": 29, "r_as": 39,
}

P_SANGENG = {
    # Jungle Assassin (target kill diff: +1.2)
    "hp": 1055, "hp_g": 100, "atk": 99, "atk_g": 17, "apw": 0, "apw_g": 0,
    "def": 35, "def_g": 6, "mr": 30, "mr_g": 4, "ms": 1090, "ms_g": 11,
    "atk_range": 26000, "atk_dur": 36, "atk_cd": 55, "atk_st": 17,
    # Passive 影随形 (after skill, 4s next AA hits twice with shadow)
    "p_t": 240, "p_dmg": 43, "p_ad": 53,
    # Q 过影 (shadow dash through target, line damage + 25% slow 1s)
    "q_cd": 410, "q_range": 41000, "q_dur": 36, "q_speed": 5100, "q_tick": 9,
    "q_dmg": 84, "q_ad": 103, "q_slow": 25, "q_slow_t": 60,
    # W 隔幕 (step behind screen, 2s stealth + 30% MS, first hit out deals bonus dmg)
    "e_cd": 820, "e_range": 42000, "e_dur": 42, "e_invis": 120, "e_ms": 30,
    "e_dmg": 64, "e_ad": 82, "e_win": 240,
    # R 灯灭 (blink behind enemy, 0.6s stealth/untargetable-guard, 3 rapid slashes, 3rd silences 1s)
    "r_cd": 2940, "r_range": 55000, "r_dur": 54, "r_invis": 36, "r_dr": 60,
    "r_dmg": 63, "r_ad": 73, "r_sil": 60,
}

P_MAIYA = {
    # Mid Magician (target kill diff: +2.5)
    "hp": 912, "hp_g": 88, "atk": 68, "atk_g": 8, "apw": 49, "apw_g": 17,
    "def": 26, "def_g": 5, "mr": 30, "mr_g": 4, "ms": 966, "ms_g": 10,
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 70, "atk_st": 13, "atk_speed": 6200, "atk_y": -8500,
    # Passive 甜头 (after skill, next AA deals bonus magic dmg + 30% slow 1s)
    "p_t": 240, "p_dmg": 36, "p_ap": 36, "p_slow": 30, "p_slow_t": 60,
    # Q 浇糖 (25k AoE + 2s steaming hot sugar puddle slow & scald)
    "q_cd": 388, "q_range": 59200, "q_dur": 30, "q_r": 25000,
    "q_dmg": 77, "q_ap": 66, "q_dot": 14, "q_dot_ap": 12, "q_puddle_t": 120, "q_slow": 30,
    # W 拉糖丝 (linear skillshot root 1.25s)
    "e_cd": 596, "e_range": 64200, "e_dur": 34, "e_speed": 6800,
    "e_dmg": 71, "e_ap": 56, "e_bind": 75,
    # R 转糖 (Dragon -> Phoenix -> Fish cycle)
    "r_cd": 3290, "r_range": 66200, "r_dur": 46,
    "rd_len": 70200, "rd_w": 22000, "rd_dmg": 145, "rd_ap": 87, "rd_up": 45,
    "rp_r": 32200, "rp_dmg": 124, "rp_ap": 76, "rp_sh": 108, "rp_sh_ap": 56, "rp_sh_t": 180,
    "rf_r": 36200, "rf_dmg": 139, "rf_ap": 82, "rf_slow": 45, "rf_slow_t": 120,
}

P_HUOSHU = {
    # Bot ADC Marksman (target kill diff: +2.5)
    "hp": 905, "hp_g": 87, "atk": 95, "atk_g": 19, "apw": 0, "apw_g": 0,
    "def": 23, "def_g": 5, "mr": 20, "mr_g": 3, "ms": 941, "ms_g": 10,
    "atk_range": 59600, "atk_dur": 27, "atk_cd": 57, "atk_st": 12, "atk_speed": 6500, "atk_y": -9500,
    # Passive 连珠炮 (every 4th AA triggers 16.8k 2-stage splash explosion)
    "p_r": 16800, "p_dmg": 44, "p_ad": 62,
    # Q 窜天猴 (3 homing rockets)
    "q_cd": 384, "q_range": 63500, "q_dur": 32, "q_speed": 6500,
    "q_dmg": 34, "q_ad": 45,
    # W 地老鼠 (backhop 18k + leave 2s spinning 19.2k zone ticking every 0.5s, 30% slow)
    "e_cd": 715, "e_range": 50200, "e_dur": 36, "e_hop_spd": 2250, "e_hop_t": 8,
    "e_r": 19200, "e_t": 120, "e_period": 30, "e_dmg": 27, "e_ad": 31, "e_slow": 30,
    # R 火树银花 (1s cast then 2s barrage every 0.25s in 34.5k + grand finale)
    "r_cd": 3570, "r_range": 67500, "r_dur": 54, "r_r": 34500,
    "r_first": 25, "r_t": 120, "r_period": 15, "r_dmg": 31, "r_ad": 37,
    "r_fin_dmg": 115, "r_fin_ad": 108,
}

P_FUMIAN = {
    # Support Enchanter/Engage Util (target kill diff: +0.4)
    "hp": 1140, "hp_g": 108, "atk": 62, "atk_g": 8, "apw": 42, "apw_g": 14,
    "def": 40, "def_g": 7, "mr": 33, "mr_g": 5, "ms": 1012, "ms_g": 10,
    "atk_range": 51200, "atk_dur": 35, "atk_cd": 82, "atk_st": 16, "atk_speed": 5400, "atk_y": -8500,
    # Passive 脸谱 (Red->Black->Gold per skill)
    "p_r": 32200, "p_sh": 66, "p_sh_ap": 51, "p_sh_t": 135,
    "p_stun": 31, "p_heal": 53, "p_heal_ap": 41,
    # Q 亮相 (47k cone magic dmg + 31% slow 1.5s)
    "q_cd": 396, "q_range": 47200, "q_dur": 35, "q_hit": 15,
    "q_dmg": 84, "q_ap": 61, "q_slow": 31, "q_slow_t": 90,
    # W 甩袖 (57k linear silk hook -> pull + 0.8s stun)
    "e_cd": 758, "e_range": 57200, "e_dur": 40, "e_speed": 5500,
    "e_dmg": 72, "e_ap": 51, "e_stun": 49,
    # R 变脸 (36k all 3 faces: enemy dmg+1s stun, ally shield 3s + heal)
    "r_cd": 3270, "r_range": 36200, "r_dur": 52, "r_hit": 18, "r_r": 36200,
    "r_dmg": 98, "r_ap": 73, "r_stun": 60,
    "r_sh": 129, "r_sh_ap": 94, "r_sh_t": 180, "r_heal": 67, "r_heal_ap": 51,
}

ALL_PARAMS = {
    "dianjing": P_DIANJING,
    "sangeng": P_SANGENG,
    "maiya": P_MAIYA,
    "huoshu": P_HUOSHU,
    "fumian": P_FUMIAN,
}


# ======================================================================
# Common Effect Builders
# ======================================================================

def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def flag(cid, name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": f"{cid}_{name}", "duration": dur, **fields}, "only_to_enemy": False}


def unflag(cid, name):
    return {"type": "RemoveCasterBuff", "name": f"{cid}_{name}"}


def when(cid, name, has, none):
    return {"type": "SwitchByBuff", "buff_name": f"{cid}_{name}", "effect_buff": has, "effect_none": none}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(cid, *effects):
    return combine(search_self(flag(cid, "live", 1)),
                   when(cid, "live", combine(*effects), search_self(*effects)),
                   unflag(cid, "live"))


def phys_atk(dmg, ratio, hp=0, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def magic_atk(dmg, ap_ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap_ratio, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def slow(cid, name, pct, tick):
    return {"type": "AddBuff", "buff_state": {"name": f"{cid}_{name}", "duration": {"Time": {"tick": tick}},
                                              "move_speed_mult": -pct}}


def shield(amt, ad_r=0, ap_r=0, tick=180):
    return {"type": "Shield", "amount": amt, "attack_ratio": ad_r, "ap_ratio": ap_r, "tick": tick}


def heal_self(amt, ad_r=0, ap_r=0):
    return {"type": "Heal", "amount": amt, "attack_ratio": ad_r, "ap_ratio": ap_r, "heal_type": "Caster"}


def heal_ally(amt, ad_r=0, ap_r=0):
    return {"type": "Heal", "amount": amt, "attack_ratio": ad_r, "ap_ratio": ap_r, "heal_type": "Ally"}


def view(cid, name):
    return {"type": "ViewEffect", "name": f"{cid}_{name}"}


def cview(cid, name):
    return {"type": "CasterViewEffect", "name": f"{cid}_{name}"}


def sfx(cid, name):
    return {"type": "Sfx", "name": f"{cid}_{name}"}


def tsfx(cid, name):
    return {"type": "TargetSfx", "name": f"{cid}_{name}"}


def action(cid, name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{cid}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def wrap_t(e):
    return {"casting_type": "Targeting", "effect": e}


def at_target(name, end_effects, travel_time=1):
    """Convert a Targeting context into a Position context so RangeProjectile /
    RangePeriodProjectile spawn reliably (both on the hero and when stolen by Sylas)."""
    return {
        "type": "ParabolicProjectile", "name": name, "travel_time": travel_time,
        "range": 400000, "range_effect_name": "", "shape": {"Circle": {"radius": 1}},
        "applied_target": "EnemyWithoutTower", "applied_effects": [],
        "end_effects": [e for e in end_effects if e is not None],
    }


def base_kit(cid, category, tags, p, attack_a, skill, skill2, ult, v_proj, v_fx, v_buff, passive_ref=None, is_native=True):
    kit = {
        "id": cid, "category": category, "tags": tags,
        "sprite": f"asset/{MOD_ID}/champions/{cid}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{cid}_skill", f"asset/{MOD_ID}/icons/{cid}_skill2",
                        f"asset/{MOD_ID}/icons/{cid}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": v_proj, "view_effects": v_fx, "view_buffs": v_buff,
    }
    if is_native and passive_ref:
        kit = {"id": cid, "category": category, "tags": tags,
               "passive": {"passive_ref": passive_ref, "params": {}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


# ======================================================================
# 1. 点睛 (baixi_dianjing) · 醒狮 · 上路战士
# ======================================================================

def build_dianjing(p, is_native=True):
    cid = "baixi_dianjing"
    fx = f"asset/{MOD_ID}/effects/{cid}_fx"
    # Passive 鼓点: every 3rd AA -> Lion Bite (+bonus dmg + self heal + bite VFX)
    bite_hit = combine(
        unflag(cid, "c2"),
        phys_atk(p["p_dmg"], p["p_ad"]),
        heal_self(p["p_heal"], p["p_heal_ad"], 0),
        view(cid, "p_bite"),
        tsfx(cid, "bite"),
    )
    step2 = combine(unflag(cid, "c1"), flag(cid, "c2", None))
    step1 = flag(cid, "c1", None)
    atk_eff = combine(
        phys_atk(0, 100),
        sfx(cid, "a"),
        when(cid, "c2", bite_hit, when(cid, "c1", step2, step1)),
    )
    attack_a = action(cid, "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"],
                      "Targeting", "Enemy", atk_eff, atype="BaseAttack", cancel=True)

    # Q 采青: leap onto enemy -> bite + 30% slow + green cabbage heal
    q_land = [
        phys_atk(p["q_dmg"], p["q_ad"]),
        slow(cid, "q_slow", p["q_slow"], p["q_slow_t"]),
        heal_self(p["q_heal"], p["q_heal_ad"], 0),
        view(cid, "q_dust"),
        view(cid, "q_leaves"),
        tsfx(cid, "q_hit"),
    ]
    q_eff = combine(
        sfx(cid, "q"),
        {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"], "end_effects": q_land},
    )
    skill = action(cid, "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", q_eff)

    # W 狮被旋: 30k spin + 3s shield
    e_spin = {
        "type": "RangeEffect", "shape": {"Circle": {"radius": p["e_r"]}},
        "target": "EnemyWithoutTower", "apply_type": "AroundCaster",
        "effects": [phys_atk(p["e_dmg"], p["e_ad"]), view(cid, "p_bite")],
    }
    e_eff = combine(
        sfx(cid, "e"),
        search_self(shield(p["e_sh"], p["e_sh_ad"], 0, p["e_sh_t"])),
        flag(cid, "e_guard", p["e_sh_t"]),
        delayed(p["e_hit"] - 1, alive_only(cid, cview(cid, "e_cape"), e_spin)),
    )
    skill2 = action(cid, "skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower", e_eff)

    # R 醒狮: 35k roar + 1s taunt + 5s 30% DR & +40% AS + golden eye glow
    r_aoe = {
        "type": "RangeEffect", "shape": {"Circle": {"radius": p["r_r"]}},
        "target": "EnemyWithoutTower", "apply_type": "AroundCaster",
        "effects": [phys_atk(p["r_dmg"], p["r_ad"]), {"type": "Taunt", "duration": p["r_taunt"]}, view(cid, "p_bite")],
    }
    r_awake = flag(cid, "r_awake", p["r_t"], damaged_reduce=p["r_dr"], attack_speed_mult=p["r_as"])
    r_eff = combine(
        flag(cid, "r_cast", p["r_hit"] + 4, cc_immune=True, damaged_reduce=30),
        cview(cid, "r_mirror"),
        sfx(cid, "r"),
        delayed(p["r_hit"] - 1, alive_only(cid, cview(cid, "r_sound"), r_aoe, r_awake)),
    )
    ult = action(cid, "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_eff)

    E = lambda name, tag, z=2, fol=True: {"type": "Animation", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "z": z, "is_follow": fol}
    B = lambda name, tag, z=2: {"type": "Animated", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "repeat": True, "z": z}
    v_fx = [E("p_bite", "bite", 3), E("q_dust", "dust", 1, False), E("q_leaves", "leaves", 3, False),
            E("e_cape", "cape", 1, True), E("r_sound", "sound", 2, True), E("r_mirror", "mirror", 3, True)]
    v_buff = [B("r_awake", "eyes", 3), B("e_guard", "guard", 1)]
    return base_kit(cid, "Melee", ["AD", "Melee", "CC", "Shield"], p, attack_a, skill, skill2, ult,
                    [], v_fx, v_buff, f"{cid}:voice", is_native)


# ======================================================================
# 2. 三更 (baixi_sangeng) · 皮影 · 打野刺客
# ======================================================================

def build_sangeng(p, is_native=True):
    cid = "baixi_sangeng"
    fx = f"asset/{MOD_ID}/effects/{cid}_fx"
    # Passive 影随形: after skill, 4s next AA strikes twice (2nd strike is shadow)
    # Also W stealth ambush bonus on first hit out of stealth!
    arm_p = flag(cid, "p_shadow", p["p_t"])
    shadow_2nd = combine(
        unflag(cid, "p_shadow"),
        delayed(7, alive_only(cid, phys_atk(p["p_dmg"], p["p_ad"]), view(cid, "p_slash"), tsfx(cid, "shadow"))),
    )
    ambush_hit = combine(
        unflag(cid, "e_ambush"),
        phys_atk(p["e_dmg"], p["e_ad"]),
        view(cid, "e_rivets"),
    )
    atk_eff = combine(
        phys_atk(0, 100),
        sfx(cid, "a"),
        view(cid, "a_hit"),
        when(cid, "e_ambush", ambush_hit, combine()),
        when(cid, "p_shadow", shadow_2nd, combine()),
    )
    attack_a = action(cid, "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"],
                      "Targeting", "Enemy", atk_eff, atype="BaseAttack", cancel=True)

    # Q 过影: dash through target dealing line damage + 25% slow 1s
    q_hit = [
        wrap_t(phys_atk(p["q_dmg"], p["q_ad"])),
        wrap_t(slow(cid, "q_slow", p["q_slow"], p["q_slow_t"])),
        wrap_t(view(cid, "a_hit")),
    ]
    q_eff = combine(
        arm_p,
        sfx(cid, "q"),
        cview(cid, "q_shadow"),
        delayed(6, alive_only(cid, {
            "type": "RushTime", "speed": p["q_speed"], "tick": p["q_tick"], "range": 16000,
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": q_hit,
        })),
    )
    skill = action(cid, "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", q_eff)

    # W 隔幕: step behind glowing puppet screen -> 2s stealth + 30% MS + ambush empowerment
    e_eff = combine(
        arm_p,
        sfx(cid, "e"),
        cview(cid, "e_screen"),
        {"type": "MoveBack", "speed": 1800, "tick": 6},
        search_self({"type": "CasterInvisible", "tick": p["e_invis"]}),
        flag(cid, "e_ms", p["e_invis"], move_speed_mult=p["e_ms"]),
        flag(cid, "e_ambush", p["e_win"]),
    )
    skill2 = action(cid, "skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion", e_eff)

    # R 灯灭: blow out lamp, flash behind enemy, invisible 0.6s + 3 rapid slashes, 3rd silences 1s
    slash12 = combine(phys_atk(p["r_dmg"], p["r_ad"]), view(cid, "r_slashes"), tsfx(cid, "r_slash"))
    slash3 = combine(phys_atk(p["r_dmg"], p["r_ad"]), {"type": "BlockSkill", "tick": p["r_sil"]},
                     view(cid, "r_slashes"), tsfx(cid, "r_slash"))
    r_eff = combine(
        arm_p,
        sfx(cid, "r"),
        cview(cid, "r_lamp"),
        flag(cid, "r_guard", p["r_invis"], cc_immune=True, damaged_reduce=p["r_dr"]),
        search_self({"type": "CasterInvisible", "tick": p["r_invis"]}),
        {"type": "RushMoveToBack", "speed": 12000, "applied_effects": []},
        delayed(8, alive_only(cid, view(cid, "r_dark"))),
        delayed(14, alive_only(cid, slash12)),
        delayed(24, alive_only(cid, slash12)),
        delayed(34, alive_only(cid, slash3)),
    )
    ult = action(cid, "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_eff)

    E = lambda name, tag, z=2, fol=True: {"type": "Animation", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "z": z, "is_follow": fol}
    v_fx = [E("a_hit", "hit", 2), E("p_slash", "slash", 3), E("q_shadow", "shadow", 1, False),
            E("e_screen", "screen", 1, False), E("e_rivets", "rivets", 3),
            E("r_lamp", "lamp", 3, True), E("r_dark", "darkness", 0, False), E("r_slashes", "three_slashes", 3)]
    return base_kit(cid, "Assassin", ["AD", "Melee", "CC"], p, attack_a, skill, skill2, ult,
                    [], v_fx, [], f"{cid}:voice", is_native)


# ======================================================================
# 3. 麦芽 (baixi_maiya) · 糖画 · 中路法师
# ======================================================================

def build_maiya(p, is_native=True):
    cid = "baixi_maiya"
    fx = f"asset/{MOD_ID}/effects/{cid}_fx"
    proj = f"asset/{MOD_ID}/effects/{cid}_proj"
    arm_p = flag(cid, "p_sweet", p["p_t"])

    # Passive 甜头: next AA after skill adds bonus magic dmg + 30% slow 1s
    sweet_bonus = combine(
        unflag(cid, "p_sweet"),
        magic_atk(p["p_dmg"], p["p_ap"]),
        slow(cid, "p_slow", p["p_slow"], p["p_slow_t"]),
        view(cid, "q_arc"),
    )
    aa_proj = {
        "type": "TargetProjectile", "name": f"{cid}_a_drop", "speed": p["atk_speed"], "y_offset": p["atk_y"],
        "applied_target": "Enemy",
        "applied_effects": [wrap_t(combine(
            phys_atk(0, 100),
            when(cid, "p_sweet", sweet_bonus, combine()),
        ))],
    }
    attack_a = action(cid, "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"],
                      "Targeting", "Enemy", combine(sfx(cid, "a"), aa_proj), atype="BaseAttack", cancel=True)

    # Q 浇糖: 26k AoE magic dmg + 2s steaming hot sugar puddle (slow + scald DoT)
    q_burst = {
        "type": "RangeProjectile", "name": f"{cid}_q_arc_p", "shape": {"Circle": {"radius": p["q_r"]}},
        "delay": 1, "apply": 1, "applied_target": "EnemyWithoutTower",
        "applied_effects": [wrap_t(magic_atk(p["q_dmg"], p["q_ap"])), wrap_t(tsfx(cid, "q_hit"))],
    }
    q_puddle = {
        "type": "RangePeriodProjectile", "name": f"{cid}_q_puddle", "shape": {"Circle": {"radius": p["q_r"]}},
        "tick": p["q_puddle_t"], "period": 30, "first_delay": 15, "applied_target": "EnemyWithoutTower",
        "applied_effects": [wrap_t(combine(
            magic_atk(p["q_dot"], p["q_dot_ap"]),
            slow(cid, "q_slow", p["q_slow"], 36),
        ))],
        "end_effects": [],
    }
    q_drop = at_target(f"{cid}_q_lob", [view(cid, "q_arc"), q_burst, q_puddle], travel_time=6)
    skill = action(cid, "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(arm_p, sfx(cid, "q"), q_drop))

    # W 拉糖丝: linear sugar thread rooting first enemy hit for 1.25s
    e_proj = {
        "type": "LinearProjectile", "name": f"{cid}_e_thread", "speed": p["e_speed"], "range": p["e_range"],
        "shape": {"Circle": {"radius": 10000}}, "penetrate": False, "y_offset": -8000,
        "applied_target": "EnemyWithoutTower",
        "applied_effects": [wrap_t(combine(
            magic_atk(p["e_dmg"], p["e_ap"]),
            {"type": "Bind", "duration": p["e_bind"]},
            view(cid, "e_bind"),
            tsfx(cid, "e_hit"),
        ))],
        "end_effects": [],
    }
    skill2 = action(cid, "skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Direction", "EnemyWithoutTower",
                    combine(arm_p, sfx(cid, "e"), delayed(6, alive_only(cid, e_proj))))

    # R 转糖: strict rotation Dragon -> Phoenix -> Fish -> Dragon!
    # State buffs (Permanent): none/wheel_dragon = Dragon, wheel_phoenix = Phoenix, wheel_fish = Fish
    cast_dragon = combine(
        unflag(cid, "wheel_dragon"),
        flag(cid, "wheel_phoenix", None),
        sfx(cid, "r_dragon"),
        delayed(8, alive_only(cid,
            {"type": "LinearProjectile", "name": f"{cid}_r_dragon_fly", "speed": 5200, "range": p["rd_len"],
             "shape": {"Circle": {"radius": 10000}}, "penetrate": True, "y_offset": -8000,
             "applied_target": "EnemyWithoutTower", "applied_effects": [], "end_effects": []},
            {"type": "LineRangeProjectile", "name": f"{cid}_r_dragon_line", "width": p["rd_w"], "length": p["rd_len"],
             "delay": 2, "apply": 1, "applied_target": "EnemyWithoutTower",
             "applied_effects": [
                 wrap_t(magic_atk(p["rd_dmg"], p["rd_ap"])),
                 wrap_t({"type": "Airborne", "duration": p["rd_up"]}),
                 wrap_t(view(cid, "r_dragon_hit")),
             ]},
        )),
    )
    cast_phoenix = combine(
        unflag(cid, "wheel_phoenix"),
        flag(cid, "wheel_fish", None),
        sfx(cid, "r_phoenix"),
        delayed(8, alive_only(cid, at_target(f"{cid}_r_phoenix_lob", [
            {"type": "RangeProjectile", "name": f"{cid}_r_phoenix_fx", "shape": {"Circle": {"radius": p["rp_r"]}},
             "delay": 2, "apply": 1, "applied_target": "EnemyWithoutTower",
             "applied_effects": [wrap_t(magic_atk(p["rp_dmg"], p["rp_ap"])), wrap_t(view(cid, "r_phoenix_hit"))]},
            {"type": "RangeProjectile", "name": f"{cid}_r_phoenix_sh", "shape": {"Circle": {"radius": p["rp_r"]}},
             "delay": 2, "apply": 1, "applied_target": "AllyChampion",
             "applied_effects": [wrap_t(shield(p["rp_sh"], 0, p["rp_sh_ap"], p["rp_sh_t"]))]},
        ]))),
    )
    cast_fish = combine(
        unflag(cid, "wheel_fish"),
        flag(cid, "wheel_dragon", None),
        sfx(cid, "r_fish"),
        delayed(10, alive_only(cid, at_target(f"{cid}_r_fish_lob", [
            {"type": "RangeProjectile", "name": f"{cid}_r_fish_fx", "shape": {"Circle": {"radius": p["rf_r"]}},
             "delay": 2, "apply": 1, "applied_target": "EnemyWithoutTower",
             "applied_effects": [
                 wrap_t(magic_atk(p["rf_dmg"], p["rf_ap"])),
                 wrap_t(slow(cid, "rf_slow", p["rf_slow"], p["rf_slow_t"])),
                 wrap_t(view(cid, "r_fish_hit")),
             ]},
        ]))),
    )
    r_eff = combine(
        arm_p,
        when(cid, "wheel_fish", cast_fish,
             when(cid, "wheel_phoenix", cast_phoenix, cast_dragon)),
    )
    ult = action(cid, "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_eff)

    E = lambda name, tag, z=2, fol=True: {"type": "Animation", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "z": z, "is_follow": fol}
    Pj = lambda name, tag, z=2: {"type": "Animated", "name": f"{cid}_{name}", "anim": proj, "tag": tag, "repeat": True, "z": z}
    PjF = lambda name, tag, z=1: {"type": "Animated", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "repeat": True, "z": z}
    B = lambda name, tag, z=3: {"type": "Animated", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "repeat": True, "z": z}

    v_proj = [
        Pj("a_drop", "drop"), Pj("e_thread", "thread"), Pj("r_dragon_fly", "dragon", 3),
        PjF("q_puddle", "puddle", 0), PjF("r_phoenix_fx", "phoenix", 2), PjF("r_fish_fx", "fish", 3),
    ]
    v_fx = [
        E("q_arc", "arc", 2), E("e_bind", "bind", 3),
        E("r_dragon_hit", "dragon", 3), E("r_phoenix_hit", "phoenix", 3), E("r_fish_hit", "fish", 3),
    ]
    v_buff = [
        B("wheel_dragon", "wheel_dragon", 4),
        B("wheel_phoenix", "wheel_phoenix", 4),
        B("wheel_fish", "wheel_fish", 4),
    ]
    return base_kit(cid, "Magician", ["AP", "Magic", "Range", "CC", "Shield"], p, attack_a, skill, skill2, ult,
                    v_proj, v_fx, v_buff, f"{cid}:voice", is_native)


# ======================================================================
# 4. 火树 (baixi_huoshu) · 烟花 · 下路射手
# ======================================================================

def build_huoshu(p, is_native=True):
    cid = "baixi_huoshu"
    fx = f"asset/{MOD_ID}/effects/{cid}_fx"
    proj = f"asset/{MOD_ID}/effects/{cid}_proj"

    # Passive 连珠炮: every 4th AA fires Two-Stage Firecracker (100% AD + 15k splash 40+60% AD)
    aa_norm = {
        "type": "TargetProjectile", "name": f"{cid}_a_fire", "speed": p["atk_speed"], "y_offset": p["atk_y"],
        "applied_target": "Enemy",
        "applied_effects": [wrap_t(phys_atk(0, 100))],
    }
    aa_4th = combine(
        unflag(cid, "c3"),
        aa_norm,
        {"type": "TargetSplashProjectile", "name": f"{cid}_p_splash", "speed": p["atk_speed"], "range": p["p_r"],
         "y_offset": p["atk_y"], "applied_target": "EnemyWithoutTower",
         "applied_effects": [wrap_t(combine(
             phys_atk(p["p_dmg"], p["p_ad"]),
             view(cid, "p_twopop"),
             tsfx(cid, "twopop"),
         ))]},
    )
    atk_eff = combine(
        sfx(cid, "a"),
        when(cid, "c3", aa_4th,
             when(cid, "c2", combine(unflag(cid, "c2"), flag(cid, "c3", None), aa_norm),
                  when(cid, "c1", combine(unflag(cid, "c1"), flag(cid, "c2", None), aa_norm),
                       combine(flag(cid, "c1", None), aa_norm)))),
    )
    attack_a = action(cid, "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"],
                      "Targeting", "Enemy", atk_eff, atype="BaseAttack", cancel=True)

    # Q 窜天猴: 3 rapid homing rockets
    rocket = {
        "type": "TargetProjectile", "name": f"{cid}_q_rocket", "speed": p["q_speed"], "y_offset": p["atk_y"],
        "applied_target": "Enemy",
        "applied_effects": [wrap_t(combine(phys_atk(p["q_dmg"], p["q_ad"]), view(cid, "p_twopop")))],
    }
    q_eff = combine(
        sfx(cid, "q"),
        delayed(9, alive_only(cid, rocket)),
        delayed(17, alive_only(cid, rocket)),
        delayed(25, alive_only(cid, rocket)),
    )
    skill = action(cid, "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", q_eff)

    # W 地老鼠: drop 2s spinning ground-mouse at feet, then backhop 18k!
    ground_mouse = {
        "type": "RangePeriodProjectile", "name": f"{cid}_e_ground", "shape": {"Circle": {"radius": p["e_r"]}},
        "tick": p["e_t"], "period": p["e_period"], "first_delay": 1, "applied_target": "EnemyWithoutTower",
        "applied_effects": [wrap_t(combine(
            phys_atk(p["e_dmg"], p["e_ad"]),
            slow(cid, "e_slow", p["e_slow"], 36),
        ))],
        "end_effects": [],
    }
    e_eff = combine(
        sfx(cid, "e"),
        search_self(at_target(f"{cid}_e_drop", [ground_mouse])),
        {"type": "MoveBack", "speed": p["e_hop_spd"], "tick": p["e_hop_t"]},
    )
    skill2 = action(cid, "skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower", e_eff)

    # R 火树银花: 1s ignite then free to move while 2s barrage (every 0.25s) + grand finale fall on target area!
    r_barrage = {
        "type": "RangePeriodProjectile", "name": f"{cid}_r_barrage", "shape": {"Circle": {"radius": p["r_r"]}},
        "tick": p["r_t"], "period": p["r_period"], "first_delay": p["r_first"], "applied_target": "EnemyWithoutTower",
        "applied_effects": [wrap_t(combine(phys_atk(p["r_dmg"], p["r_ad"]), view(cid, "p_twopop"), tsfx(cid, "r_boom")))],
        "end_effects": [],
    }
    r_finale = {
        "type": "RangeProjectile", "name": f"{cid}_r_finale_p", "shape": {"Circle": {"radius": p["r_r"]}},
        "delay": p["r_first"] + p["r_t"], "apply": 1, "applied_target": "EnemyWithoutTower",
        "applied_effects": [wrap_t(combine(
            phys_atk(p["r_fin_dmg"], p["r_fin_ad"]),
            view(cid, "r_finale"),
            tsfx(cid, "r_finale"),
        ))],
    }
    r_eff = combine(sfx(cid, "r"), at_target(f"{cid}_r_lob", [r_barrage, r_finale]))
    ult = action(cid, "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_eff)

    E = lambda name, tag, z=2, fol=True: {"type": "Animation", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "z": z, "is_follow": fol}
    Pj = lambda name, tag, z=2: {"type": "Animated", "name": f"{cid}_{name}", "anim": proj, "tag": tag, "repeat": True, "z": z}
    PjF = lambda name, tag, z=1: {"type": "Animated", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "repeat": True, "z": z}
    v_proj = [
        Pj("a_fire", "firecracker"), Pj("q_rocket", "rocket"),
        PjF("e_ground", "ground", 0), PjF("r_barrage", "barrage", 2), PjF("r_finale_p", "finale", 3),
    ]
    v_fx = [E("p_twopop", "twopop", 3), E("r_finale", "finale", 3, False)]
    return base_kit(cid, "Range", ["AD", "Range"], p, attack_a, skill, skill2, ult,
                    v_proj, v_fx, [], f"{cid}:voice", is_native)


# ======================================================================
# 5. 拂面 (baixi_fumian) · 川剧变脸 · 辅助
# ======================================================================

def build_fumian(p, is_native=True):
    cid = "baixi_fumian"
    fx = f"asset/{MOD_ID}/effects/{cid}_fx"
    proj = f"asset/{MOD_ID}/effects/{cid}_proj"

    # AA 扇风: ranged colorful wind projectile
    aa_proj = {
        "type": "TargetProjectile", "name": f"{cid}_a_gust", "speed": p["atk_speed"], "y_offset": p["atk_y"],
        "applied_target": "Enemy",
        "applied_effects": [wrap_t(phys_atk(0, 100))],
    }
    attack_a = action(cid, "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"],
                      "Targeting", "Enemy", combine(sfx(cid, "a"), aa_proj), atype="BaseAttack", cancel=True)

    # Passive 脸谱 helpers:
    # State buffs (Permanent): neither = Red, face_blk = Black, face_gld = Gold
    red_ally_shield = {
        "type": "RangeEffect", "shape": {"Circle": {"radius": p["p_r"]}},
        "target": "AllyChampion", "apply_type": "AroundCaster",
        "effects": [shield(p["p_sh"], 0, p["p_sh_ap"], p["p_sh_t"]), view(cid, "p_shield")],
    }
    gold_ally_heal = {
        "type": "RangeEffect", "shape": {"Circle": {"radius": p["p_r"]}},
        "target": "AllyChampion", "apply_type": "AroundCaster",
        "effects": [heal_ally(p["p_heal"], 0, p["p_heal_ap"]), view(cid, "p_heal")],
    }
    # Shift face AFTER casting: Red -> Black, Black -> Gold, Gold -> Red
    shift_face = combine(
        cview(cid, "p_smoke"),
        sfx(cid, "shift"),
        when(cid, "face_gld",
             combine(gold_ally_heal, unflag(cid, "face_gld")),
             when(cid, "face_blk",
                  combine(unflag(cid, "face_blk"), flag(cid, "face_gld", None)),
                  combine(red_ally_shield, flag(cid, "face_blk", None)))),
    )

    # Q 亮相: forward cone 45k magic dmg + 30% slow 1.5s (+0.5s stun if Black face!)
    q_cone = lambda extra_stun: {
        "type": "RangeEffect", "shape": {"DirDot": {"radius": p["q_range"], "range": 500}},
        "target": "EnemyWithoutTower", "apply_type": {"Forward": {"offset": 1000}},
        "effects": [
            magic_atk(p["q_dmg"], p["q_ap"]),
            slow(cid, "q_slow", p["q_slow"], p["q_slow_t"]),
            *([{"type": "Stun", "duration": p["p_stun"]}] if extra_stun else []),
            view(cid, "q_fan"),
        ],
    }
    q_eff = combine(
        sfx(cid, "q"),
        delayed(p["q_hit"] - 1, alive_only(cid,
            when(cid, "face_blk", q_cone(True), q_cone(False)),
            shift_face,
        )),
    )
    skill = action(cid, "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", q_eff)

    # W 甩袖: 55k silk sleeve linear hook -> pull enemy to front + dmg + 0.75s stun (+0.5s if Black face!)
    def make_silk(stun_t):
        return {
            "type": "LinearProjectile", "name": f"{cid}_e_silk", "speed": p["e_speed"], "range": p["e_range"],
            "shape": {"Circle": {"radius": 9000}}, "penetrate": False, "y_offset": -9000,
            "applied_target": "EnemyChampion",
            "applied_effects": [wrap_t(combine(
                magic_atk(p["e_dmg"], p["e_ap"]),
                {"type": "Grab", "speed": 2800, "tick": 8},
                {"type": "Stun", "duration": stun_t},
                view(cid, "e_bind"),
                tsfx(cid, "e_hit"),
            ))],
            "end_effects": [],
        }

    e_eff = combine(
        sfx(cid, "e"),
        delayed(14, alive_only(cid,
            when(cid, "face_blk", make_silk(p["e_stun"] + p["p_stun"]), make_silk(p["e_stun"])),
            shift_face,
        )),
    )
    skill2 = action(cid, "skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Direction", "EnemyChampion", e_eff)

    # R 变脸: flash all 3 faces -> 35k enemy dmg + 1s stun, ally shield 3s + heal!
    r_enemies = {
        "type": "RangeEffect", "shape": {"Circle": {"radius": p["r_r"]}},
        "target": "EnemyWithoutTower", "apply_type": "AroundCaster",
        "effects": [magic_atk(p["r_dmg"], p["r_ap"]), {"type": "Stun", "duration": p["r_stun"]}, view(cid, "r_finale")],
    }
    r_allies = {
        "type": "RangeEffect", "shape": {"Circle": {"radius": p["r_r"]}},
        "target": "AllyChampion", "apply_type": "AroundCaster",
        "effects": [
            shield(p["r_sh"], 0, p["r_sh_ap"], p["r_sh_t"]),
            heal_ally(p["r_heal"], 0, p["r_heal_ap"]),
            view(cid, "p_shield"),
            view(cid, "p_heal"),
        ],
    }
    r_eff = combine(
        sfx(cid, "r"),
        cview(cid, "p_smoke"),
        flag(cid, "r_cast", p["r_hit"] + 4, cc_immune=True, damaged_reduce=25),
        delayed(p["r_hit"] - 1, alive_only(cid, cview(cid, "r_finale"), r_enemies, r_allies)),
    )
    ult = action(cid, "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_eff)

    E = lambda name, tag, z=2, fol=True: {"type": "Animation", "name": f"{cid}_{name}", "anim": fx, "tag": tag, "z": z, "is_follow": fol}
    Pj = lambda name, tag, z=2: {"type": "Animated", "name": f"{cid}_{name}", "anim": proj, "tag": tag, "repeat": True, "z": z}
    v_proj = [Pj("a_gust", "gust"), Pj("e_silk", "silk")]
    v_fx = [E("q_fan", "fan", 2), E("e_bind", "bind", 3), E("p_smoke", "smoke", 3),
            E("p_shield", "shield", 2), E("p_heal", "healing", 2), E("r_finale", "finale", 3)]
    return base_kit(cid, "Util", ["AP", "Magic", "Range", "CC", "Shield", "Heal"], p, attack_a, skill, skill2, ult,
                    v_proj, v_fx, [], f"{cid}:voice", is_native)


BUILDERS = {
    "dianjing": build_dianjing,
    "sangeng": build_sangeng,
    "maiya": build_maiya,
    "huoshu": build_huoshu,
    "fumian": build_fumian,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", default="all", help="dianjing,sangeng,maiya,huoshu,fumian or all")
    ap.add_argument("--plain", action="store_true", help="omit native passive for classic SDK lb_sim")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--set", nargs="*", default=[], help="key=val overrides (only when single --hero)")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    heroes = list(BUILDERS) if a.hero == "all" else a.hero.split(",")
    for h in heroes:
        p = dict(ALL_PARAMS[h])
        if a.set:
            for kv in a.set:
                k, v = kv.split("=", 1)
                if k not in p:
                    raise SystemExit(f"{h}: unknown param {k}")
                p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
        kit = BUILDERS[h](p, is_native=not a.plain)
        out = os.path.join(a.out_dir, f"baixi_{h}.data_champion")
        text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"wrote {out} ({len(text)} bytes, native={not a.plain})")


if __name__ == "__main__":
    main()
