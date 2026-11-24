#!/usr/bin/env python3
"""Abyss Pact (渊契) 5-champion skill kit & combo generator.

    python tools/kit/build_abysspact.py [--hero oathbreaker|faceless|whisperer|bonebow|corvus]
                                        [--plain] [--out file] [--set k=v ...] [--nodes]

Champions:
  1. abysspact_oathbreaker (断誓 · 上路战士 Melee)     - 血誓烧血增幅、W誓链→Q黑焰斩连招、R断誓6秒不死裁决
  2. abysspact_faceless    (无面 · 打野刺客 Assassin)   - 夺面换脸变身、W无相隐身→Q割影→A恐惧→R撕面25%斩杀连招
  3. abysspact_whisperer   (呓语 · 中路法师 Magician)   - 疯狂3层恐惧连锁爆炸、W睁眼→Q低语→R众口群疯连招
  4. abysspact_bonebow     (骸弦 · 下路射手 Range)      - 亡兵真实骷髅兵召唤、Q穿骨起兵/R亡军列阵→W葬礼全军自爆连招
  5. abysspact_corvus      (鸦医 · 辅助 Util)           - 传染疫雾蔓延回血、W渡鸦肩头护盾啄击、Q瘴瓶/R隔离区控场连招
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "abysspact"
OUT_DIR = os.path.join(REPO, MOD_ID, "champion")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


# ---------------------------------------------------------------------------
# Tunable parameter tables (initialized from design.txt; tuned via kd.py)
# ---------------------------------------------------------------------------
PARAMS = {
    "oathbreaker": {
        "hp": 1220, "hp_g": 112, "atk": 92, "atk_g": 16, "apw": 0, "apw_g": 0,
        "def": 37, "def_g": 7, "mr": 30, "mr_g": 5, "ms": 1050, "ms_g": 10,
        "atk_range": 28000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
        "q_cd": 420, "q_range": 35000, "q_dur": 38, "q_go": 14, "q_hit": 19,
        "q_r": 38000, "q_cone": 350, "q_dmg": 72, "q_ad": 112,
        "q_slow": 30, "q_slow_t": 90, "q_heal": 44, "q_heal_r": 30,
        "q_combo_dmg": 20, "q_combo_ad": 20,
        "w_cd": 720, "w_range": 50000, "w_dur": 40, "w_go": 15,
        "w_speed": 7500, "w_w": 11000, "w_dmg": 60, "w_ad": 80,
        "w_grab_speed": 3200, "w_grab_t": 12, "w_bind": 30,
        "r_cd": 4200, "r_range": 35000, "r_dur": 42, "r_go": 16,
        "r_t": 360, "r_vamp": 40, "r_as": 15, "r_burst_r": 28000,
        "r_burst_dmg": 48, "r_burst_ad": 42,
        "r_onhit_ap": 40, "r_onhit_ad": 30,
        "plain_ad_mult": 14, "plain_as_mult": 18,
    },
    "faceless": {
        "hp": 1000, "hp_g": 96, "atk": 100, "atk_g": 18, "apw": 0, "apw_g": 0,
        "def": 32, "def_g": 6, "mr": 30, "mr_g": 4, "ms": 1090, "ms_g": 11,
        "atk_range": 26000, "atk_dur": 34, "atk_cd": 56, "atk_st": 17,
        "q_cd": 390, "q_range": 40000, "q_dur": 34, "q_go": 10,
        "q_speed": 5600, "q_t": 10, "q_rad": 13000,
        "q_dmg": 90, "q_ad": 115, "q_slow": 30, "q_slow_t": 60,
        "w_cd": 660, "w_range": 45000, "w_dur": 28, "w_go": 10,
        "w_inv": 90, "w_ms": 20, "w_ambush_t": 180,
        "w_fear": 54, "w_bonus_dmg": 55, "w_bonus_ad": 50,
        "r_cd": 3300, "r_range": 45000, "r_dur": 42, "r_go": 15,
        "r_dmg": 290, "r_ad": 165, "r_plain_thp": 14,
        "plain_shroud_ad": 14, "plain_shroud_as": 18, "plain_shroud_t": 240,
    },
    "whisperer": {
        "hp": 880, "hp_g": 88, "atk": 66, "atk_g": 8, "apw": 60, "apw_g": 21,
        "def": 24, "def_g": 5, "mr": 30, "mr_g": 4, "ms": 950, "ms_g": 9,
        "atk_range": 52000, "atk_dur": 34, "atk_cd": 84, "atk_st": 16,
        "a_speed": 7500, "a_y": -10000,
        "q_cd": 360, "q_range": 60000, "q_dur": 36, "q_go": 14,
        "q_speed": 6800, "q_w": 11000, "q_dmg": 80, "q_ap": 70,
        "w_cd": 660, "w_range": 55000, "w_dur": 38, "w_go": 15,
        "w_r": 22000, "w_t": 180, "w_p": 60, "w_dmg": 28, "w_ap": 22,
        "w_slow": 22, "w_slow_t": 70,
        "r_cd": 3600, "r_range": 60000, "r_dur": 44, "r_go": 18,
        "r_r": 40000, "r_dmg": 215, "r_ap": 108, "r_fear": 66,
        "plain_burst_dmg": 85, "plain_burst_ap": 62, "plain_burst_r": 16000,
    },
    "bonebow": {
        "hp": 900, "hp_g": 88, "atk": 98, "atk_g": 18, "apw": 0, "apw_g": 0,
        "def": 22, "def_g": 6, "mr": 18, "mr_g": 3, "ms": 930, "ms_g": 9,
        "atk_range": 62500, "atk_dur": 24, "atk_cd": 58, "atk_st": 10,
        "a_speed": 9500, "a_y": -9500,
        "q_cd": 470, "q_range": 70000, "q_dur": 36, "q_go": 15,
        "q_speed": 9000, "q_w": 10000, "q_dmg": 75, "q_ad": 105,
        "w_cd": 600, "w_range": 65000, "w_dur": 32, "w_go": 12,
        "w_r": 16000, "w_base_dmg": 40, "w_base_ad": 38,
        "w_plain_dmg": 102, "w_plain_ad": 120,
        "w_slow": 30, "w_slow_t": 60,
        "r_cd": 3900, "r_range": 70000, "r_dur": 44, "r_go": 16,
        "r_travel": 12, "r_r": 35000, "r_dmg": 132, "r_ad": 88,
        "r_slow": 25, "r_slow_t": 90,
        "r_plain_tick_dmg": 47, "r_plain_tick_ad": 47, "r_plain_t": 240, "r_plain_p": 60,
        "plain_p_dmg": 34, "plain_p_ad": 37,
    },
    "corvus": {
        "hp": 1000, "hp_g": 95, "atk": 62, "atk_g": 8, "apw": 42, "apw_g": 15,
        "def": 30, "def_g": 6, "mr": 32, "mr_g": 5, "ms": 990, "ms_g": 10,
        "atk_range": 50000, "atk_dur": 36, "atk_cd": 84, "atk_st": 17,
        "a_speed": 7000, "a_y": -10000,
        "q_cd": 480, "q_range": 55000, "q_dur": 38, "q_go": 14,
        "q_travel": 14, "q_r": 20000, "q_dmg": 52, "q_ap": 42,
        "q_slow": 30, "q_slow_t": 90,
        "q_plain_dot": 28, "q_plain_dot_ap": 15, "q_plain_heal": 24,
        "w_cd": 700, "w_range": 55000, "w_dur": 36, "w_go": 14,
        "w_speed": 6500, "w_sh": 85, "w_sh_ap": 60, "w_t": 240,
        "w_plain_dmg": 48, "w_plain_ap": 30, "w_plain_r": 28000,
        "r_cd": 4200, "r_range": 50000, "r_dur": 44, "r_go": 16,
        "r_r": 40000, "r_t": 300, "r_p": 60,
        "r_init_dmg": 92, "r_init_ap": 65, "r_stun": 40,
        "r_tick_dmg": 35, "r_tick_ap": 25, "r_slow": 40, "r_slow_t": 70,
        "r_heal": 55, "r_heal_ap": 25,
    },
}


# ---------------------------------------------------------------------------
# Shared JSON node builders
# ---------------------------------------------------------------------------
def mk_helpers(cid):
    fx_path = f"asset/{MOD_ID}/effects/{cid}_fx"
    proj_path = f"asset/{MOD_ID}/effects/{cid}_proj"

    def n(x):
        return f"{cid}_{x}"

    def combine(*effects):
        return {"type": "Combine", "effects": [e for e in effects if e is not None]}

    def delayed(tick, *effects):
        return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}

    def flag(name, tick, **fields):
        dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
        return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields},
                "only_to_enemy": False}

    def unflag(name):
        return {"type": "RemoveCasterBuff", "name": n(name)}

    def buff(name, tick, **fields):
        return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}

    def when(name, has, none=None):
        return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has,
                "effect_none": none if none is not None else combine()}

    def view(name):
        return {"type": "ViewEffect", "name": n(name)}

    def sfx(name):
        return {"type": "Sfx", "name": n(name)}

    def tsfx(name):
        return {"type": "TargetSfx", "name": n(name)}

    def attack(dmg, ratio, thp=0):
        return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0,
                "target_hp_ratio": thp, "attack_effect_type": "Target"}

    def ap_atk(dmg, ratio):
        return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}

    def heal(amount, ad_ratio=0, ap_ratio=0, kind="Caster"):
        return {"type": "Heal", "amount": amount, "attack_ratio": ad_ratio, "ap_ratio": ap_ratio, "heal_type": kind}

    def shield(amount, ad_ratio=0, ap_ratio=0, tick=180):
        return {"type": "Shield", "amount": amount, "attack_ratio": ad_ratio, "ap_ratio": ap_ratio, "tick": tick}

    def fear(tick):
        return {"type": "Fear", "tick": tick}

    def stun(dur):
        return {"type": "Stun", "duration": dur}

    def bind(dur):
        return {"type": "Bind", "duration": dur}

    def grab(speed, tick):
        return {"type": "Grab", "speed": speed, "tick": tick}

    def circle(r):
        return {"Circle": {"radius": r}}

    def T(e):
        return {"casting_type": "Targeting", "effect": e}

    def search_self(*effects):
        return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf",
                "from_projectile": False, "effects": [e for e in effects if e is not None]}

    def alive_only(*effects):
        return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                       unflag("live"))

    def cone(radius, cos, effects, target="EnemyWithoutTower"):
        return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}},
                "target": target, "apply_type": {"Forward": {"offset": 1000}},
                "effects": [e for e in effects if e is not None]}

    def around(radius, effects, target="EnemyWithoutTower"):
        return {"type": "RangeEffect", "shape": circle(radius), "target": target,
                "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}

    def homing(name, speed, effects, target="Enemy", y=0):
        return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}

    def linear(name, speed, rng, width, effects, target="EnemyWithoutTower", penetrate=False, end=None, y=0):
        return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng,
                "shape": circle(width), "penetrate": penetrate, "y_offset": y,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None],
                "end_effects": list(end or [])}

    def lob(name, travel, end_effects, target="EnemyWithoutTower"):
        """Always wraps RangeProjectile / RangePeriodProjectile so Position context is guaranteed
        (works on both hero casts and Sylas stolen ults!)."""
        return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
                "range_effect_name": "", "shape": circle(1), "applied_target": target,
                "applied_effects": [], "end_effects": [e for e in end_effects if e is not None]}

    def zone(name, radius, effects, target="EnemyWithoutTower"):
        return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}

    def field(name, radius, tick, period, effects, first=1, target="EnemyWithoutTower"):
        return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius),
                "tick": tick, "period": period, "first_delay": first,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None],
                "end_effects": []}

    def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
        return {"action_name": name, "description": f"#asset/base/text/champion?description.{cid}.{name}",
                "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
                "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}

    def V_eff(name, tag, z=2, follow=True):
        return {"type": "Animation", "name": n(name), "anim": fx_path, "tag": tag, "z": z, "is_follow": follow}

    def V_buf(name, tag, z=2):
        return {"type": "Animated", "name": n(name), "anim": fx_path, "tag": tag, "repeat": True, "z": z}

    def V_proj(name, tag, z=2):
        return {"type": "Animated", "name": n(name), "anim": proj_path, "tag": tag, "repeat": True, "z": z}

    return dict(
        n=n, combine=combine, delayed=delayed, flag=flag, unflag=unflag, buff=buff, when=when,
        view=view, sfx=sfx, tsfx=tsfx, attack=attack, ap_atk=ap_atk, heal=heal, shield=shield,
        fear=fear, stun=stun, bind=bind, grab=grab, circle=circle, T=T, search_self=search_self,
        alive_only=alive_only, cone=cone, around=around, homing=homing, linear=linear, lob=lob,
        zone=zone, field=field, action=action, V_eff=V_eff, V_buf=V_buf, V_proj=V_proj,
    )


def wrap_kit(cid, category, tags, p, attack_a, skill, skill2, ult, views_p, views_e, views_b,
             is_native, passive_ref):
    kit = {
        "id": cid, "category": category, "tags": tags,
        "sprite": f"asset/{MOD_ID}/champions/{cid}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{cid}_skill",
                        f"asset/{MOD_ID}/icons/{cid}_skill2",
                        f"asset/{MOD_ID}/icons/{cid}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:
        kit = {"id": cid, "category": category, "tags": tags,
               "passive": {"passive_ref": passive_ref, "params": {}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


# ===========================================================================
# 1. 断誓 (abysspact_oathbreaker) · 上路战士
# ===========================================================================
def build_oathbreaker(p, is_native=True):
    cid = "abysspact_oathbreaker"
    H = mk_helpers(cid)
    burn_ask = H["flag"]("burn_ask", 3) if is_native else None
    plain_oath = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](H["flag"]("p_on", None),
                     H["flag"]("p_oath", None, attack_mult=p["plain_ad_mult"], attack_speed_mult=p["plain_as_mult"])))

    # Auto: 断剑 (during R adds bonus 40 + 30% AD black-flame strike)
    r_bonus = H["combine"](H["ap_atk"](p["r_onhit_ap"], 0), H["attack"](0, p["r_onhit_ad"]), H["view"]("impact"))
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_oath, H["attack"](0, 100),
                     H["when"]("r_undying", r_bonus),
                     H["sfx"]("a"), H["view"]("impact"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 黑焰斩 — 扇形斩击 + 减速 + 命中敌方英雄回血 + 命中W链目标额外爆发连招
    q_combo = H["when"]("w_chained", H["combine"](H["attack"](p["q_combo_dmg"], p["q_combo_ad"]),
                                                  H["unflag"]("w_chained"), H["view"]("impact")))
    q_hit = [H["attack"](p["q_dmg"], p["q_ad"]),
             H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
             H["view"]("impact"), H["tsfx"]("q_hit")]
    q_champ_heal = [H["heal"](p["q_heal"], ad_ratio=p["q_heal_r"], kind="Caster")]
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            burn_ask,
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), H["view"]("cleave"))),
            H["delayed"](p["q_hit"] - 1, H["alive_only"](
                H["cone"](p["q_r"], p["q_cone"], q_hit, "EnemyWithoutTower"),
                H["cone"](p["q_r"], p["q_cone"], q_champ_heal, "EnemyChampion"),
                q_combo)),
        ),
    )

    # W: 誓链 — 锁链直飞勾中首个敌方英雄拽回身前 + 定身 0.5s + 挂连招标记
    w_hit = [H["attack"](p["w_dmg"], p["w_ad"]),
             H["grab"](p["w_grab_speed"], p["w_grab_t"]),
             H["bind"](p["w_bind"]),
             H["flag"]("w_chained", 150),
             H["view"]("impact"), H["tsfx"]("w_pull")]
    w_chain = H["linear"]("w_chain", p["w_speed"], p["w_range"] + 6000, p["w_w"],
                          w_hit, target="EnemyChampion", penetrate=False, y=-8000)
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["combine"](
            burn_ask,
            H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_cast"), w_chain)),
        ),
    )

    # R: 断誓 — 6秒不死 + 40%全能吸血 + 脚下黑火喷发 (Sylas也能完整偷到6秒不死+吸血+爆发!)
    r_buff = H["flag"]("r_undying", p["r_t"], undying=True, vamp=p["r_vamp"], attack_speed_mult=p["r_as"])
    r_burst = H["around"](p["r_burst_r"], [H["attack"](p["r_burst_dmg"], p["r_burst_ad"]),
                                           H["view"]("impact"), H["tsfx"]("q_hit")])
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            burn_ask,
            H["sfx"]("r_plant"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                r_buff, H["sfx"]("r_erupt"), H["view"]("footfire"), r_burst)),
        ),
    )

    views_p = [H["V_proj"]("w_chain", "chain")]
    views_e = [
        H["V_eff"]("impact", "impact", 2),
        H["V_eff"]("cleave", "cleave", 2),
        H["V_eff"]("footfire", "footfire", -1),
    ]
    views_b = [
        H["V_buf"]("r_undying", "eruption", 2),
        H["V_buf"]("oath_low", "oath_low", 1),
        H["V_buf"]("oath_mid", "oath_mid", 1),
        H["V_buf"]("oath_high", "oath_high", 2),
    ]
    return wrap_kit(cid, "Melee", ["AD", "Melee", "CC", "Heal"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:blood")


# ===========================================================================
# 2. 无面 (abysspact_faceless) · 打野刺客
# ===========================================================================
def build_faceless(p, is_native=True):
    cid = "abysspact_faceless"
    H = mk_helpers(cid)

    # W ambush bonus proc: Fear 0.75s + bonus damage + empty porcelain mask VFX
    ambush_proc = H["combine"](
        H["attack"](p["w_bonus_dmg"], p["w_bonus_ad"]),
        H["fear"](p["w_fear"]),
        H["unflag"]("w_ambush"),
        H["view"]("fear"),
        H["tsfx"]("w_fear"),
    )

    # Borrowed face auto-attack adaptation (when Face-Steal copied a ranged/mage hero, fire phantom bolt!)
    ranged_bolt = H["homing"]("p_bolt", 8500, [H["attack"](0, 100), H["tsfx"]("a_hit")], target="Enemy", y=-9000)
    cls_auto = H["when"](
        "cls_range", ranged_bolt,
        H["when"]("cls_mage", ranged_bolt, H["attack"](0, 100)))
    base_hit = cls_auto if is_native else H["attack"](0, 100)

    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](
            base_hit,
            H["when"]("w_ambush", ambush_proc),
            H["sfx"]("a"), H["tsfx"]("a_hit"),
        ),
        atype="BaseAttack", cancel=True,
    )

    # Q: 割影 — 穿透目标冲到身后 + 减速 + 隐身突袭连招可触发恐惧
    q_hit = [
        H["attack"](p["q_dmg"], p["q_ad"]),
        H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        H["when"]("w_ambush", ambush_proc),
        H["tsfx"]("q_pass"),
    ]
    q_rush = {
        "type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": p["q_rad"],
        "casting_target": "EnemyWithoutTower", "penetrate": True,
        "applied_effects": [H["T"](e) for e in q_hit],
    }
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_dash"), H["view"]("dash"), q_rush)),
        ),
    )

    # W: 无相 — 隐身 1.5s + 移速提升 + 武装下一次出手恐惧 0.75s
    w_cast = H["combine"](
        H["sfx"]("w_hide"),
        H["view"]("mist"),
        H["search_self"]({"type": "CasterInvisible", "tick": p["w_inv"]}),
        H["flag"]("w_haste", p["w_inv"], move_speed_mult=p["w_ms"]),
        H["flag"]("w_ambush", p["w_ambush_t"]),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](w_cast)),
        ),
    )

    # R: 撕面 — 大黑手按住撕面：高额爆发 + <=25%直接真伤撕死并立刻夺面!
    r_exec_ask = H["buff"]("r_exec_ask", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    plain_shroud = None if is_native else H["flag"](
        "shroud", p["plain_shroud_t"], attack_mult=p["plain_shroud_ad"], attack_speed_mult=p["plain_shroud_as"])
    r_return = H["homing"]("r_mask", 7500, [H["tsfx"]("r_return")], target="EnemyChampion", y=-9000)
    r_strike = H["combine"](
        H["attack"](p["r_dmg"], p["r_ad"], thp=0 if is_native else p["r_plain_thp"]),
        r_exec_ask,
        plain_shroud,
        H["view"]("grasp"),
        H["tsfx"]("r_grasp"),
        r_return,
    )
    # If wearing a stolen face (r_stolen), casting R unleashes a bonus borrowed-ult surge & consumes charge
    stolen_bonus = H["combine"](
        H["attack"](100, 75),
        H["unflag"]("r_stolen"),
        H["view"]("shards"),
        H["sfx"]("mask_crack"),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_grasp"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                r_strike,
                H["when"]("r_stolen", stolen_bonus) if is_native else None)),
        ),
    )

    views_p = [
        H["V_proj"]("r_mask", "mask_return"),
        H["V_proj"]("p_bolt", "mask_return"),
    ]
    views_e = [
        H["V_eff"]("dash", "dash", 2),
        H["V_eff"]("mist", "mist", 2),
        H["V_eff"]("fear", "fear", 3),
        H["V_eff"]("grasp", "grasp", 3),
        H["V_eff"]("shards", "shards", 3),
    ]
    views_b = [
        H["V_buf"]("shroud", "shroud", 1),
        H["V_buf"]("cracks", "cracks", 2),
    ]
    return wrap_kit(cid, "Assassin", ["AD", "Melee", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:mask")


# ===========================================================================
# 3. 呓语 (abysspact_whisperer) · 中路法师
# ===========================================================================
def build_whisperer(p, is_native=True):
    cid = "abysspact_whisperer"
    H = mk_helpers(cid)

    mad1 = H["buff"]("mad_ask1", 4) if is_native else None
    mad3 = H["buff"]("mad_ask3", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # In --plain mode, simulate 3-stack madness burst in data so kd.py reflects passive AoE output
    plain_mad_step = None if is_native else H["when"](
        "pm2",
        H["combine"](H["unflag"]("pm2"), H["unflag"]("pm1"),
                     H["ap_atk"](p["plain_burst_dmg"], p["plain_burst_ap"]),
                     H["fear"](50), H["view"]("burst"), H["tsfx"]("madness_burst")),
        H["when"]("pm1", H["flag"]("pm2", 240), H["flag"]("pm1", 240)),
    )

    # Auto: 念 (飞出念珠)
    a_bead = H["homing"]("a_bead", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_bead),
        atype="BaseAttack", cancel=True,
    )

    # Q: 低语 — 直线穿透紫色低语波 + 叠1层疯狂
    q_hit = [H["ap_atk"](p["q_dmg"], p["q_ap"]), mad1, plain_mad_step, H["view"]("haze"), H["tsfx"]("q_pass")]
    q_line = H["linear"]("q_wave", p["q_speed"], p["q_range"] + 6000, p["q_w"],
                         q_hit, target="EnemyWithoutTower", penetrate=True, y=-10000)
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), q_line)),
        ),
    )

    # W: 睁眼 — 1-tick lob 锚定目标脚下睁开巨眼3秒：每秒伤+减速+叠1层疯狂
    w_tick = [
        H["ap_atk"](p["w_dmg"], p["w_ap"]),
        H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
        mad1, plain_mad_step,
        H["tsfx"]("w_blink"),
    ]
    w_zone = H["lob"]("w_lob", 1, [
        H["view"]("ground_eye"),
        H["sfx"]("w_open"),
        H["field"]("w_eye", p["w_r"], p["w_t"], p["w_p"], w_tick, first=1, target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](w_zone)),
        ),
    )

    # R: 众口 — 1-tick lob 锚定目标处裂开4万半径众口：巨额法伤 + 直接叠满3层集体发狂连锁炸!
    # Also includes data Fear + burst shockwave so Sylas stealing R gets full AoE fear & blast!
    r_hit = [
        H["ap_atk"](p["r_dmg"], p["r_ap"]),
        mad3,
        H["fear"](p["r_fear"]) if not is_native else None,
        H["ap_atk"](p["plain_burst_dmg"], p["plain_burst_ap"]) if not is_native else None,
        H["view"]("burst"),
        H["tsfx"]("madness_burst"),
    ]
    # Give Sylas & native-off clients a reliable fear even without DLL:
    # Actually in native mode, whisperer.rs applies 90-tick Fear + chain explosion on mad_ask3;
    # for Sylas stealing R, Sylas doesn't have WhispererPassive! So put a 45-tick baseline Fear in R directly
    # (in native mode whisperer.rs overlays the full 90-tick Fear + chain burst).
    r_hit_all = [
        H["ap_atk"](p["r_dmg"], p["r_ap"]),
        H["fear"](p["r_fear"]),
        mad3,
        H["ap_atk"](p["plain_burst_dmg"], p["plain_burst_ap"]) if not is_native else None,
        H["view"]("burst"),
        H["tsfx"]("madness_burst"),
    ]
    r_field = H["lob"]("r_lob", 1, [
        H["view"]("mouths"),
        H["sfx"]("r_pulse"),
        H["zone"]("r_mouths", p["r_r"], r_hit_all, target="EnemyWithoutTower"),
    ], target="EnemyChampion")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_open"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_field)),
        ),
    )

    views_p = [
        H["V_proj"]("a_bead", "bead"),
        H["V_proj"]("q_wave", "whisper"),
    ]
    views_e = [
        H["V_eff"]("haze", "haze", 2),
        H["V_eff"]("burst", "burst", 3),
        H["V_eff"]("ground_eye", "ground_eye", -1, follow=False),
        H["V_eff"]("mouths", "mouths", -1, follow=False),
    ]
    views_b = [
        H["V_buf"]("madness_1", "madness_1", 3),
        H["V_buf"]("madness_2", "madness_2", 3),
        H["V_buf"]("madness_3", "madness_3", 3),
        H["V_buf"]("mad_runes", "runes", 3),
    ]
    return wrap_kit(cid, "Magician", ["AP", "Magic", "Range", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:madness")


# ===========================================================================
# 4. 骸弦 (abysspact_bonebow) · 下路射手
# ===========================================================================
def build_bonebow(p, is_native=True):
    cid = "abysspact_bonebow"
    H = mk_helpers(cid)

    # In --plain mode, every 4th auto triggers a bonus bone-soldier volley approximating skeleton DPS
    plain_4th = None if is_native else H["when"](
        "s3",
        H["combine"](H["unflag"]("s3"), H["unflag"]("s2"), H["unflag"]("s1"),
                     H["attack"](p["plain_p_dmg"], p["plain_p_ad"]), H["view"]("soul")),
        H["when"]("s2", H["flag"]("s3", 600),
                  H["when"]("s1", H["flag"]("s2", 600), H["flag"]("s1", 600))),
    )

    # Auto: 骨箭
    a_proj = H["homing"]("a_arrow", p["a_speed"],
                         [H["attack"](0, 100), plain_4th, H["view"]("soul"), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_proj),
        atype="BaseAttack", cancel=True,
    )

    # Q: 穿骨 — 直线穿透骨箭 + 每命中一名敌方英雄在其脚下爬出1名真实骷髅兵
    q_hit = [H["attack"](p["q_dmg"], p["q_ad"]), H["view"]("pierce_flash"), H["tsfx"]("q_hit")]
    q_champ_spawn = [H["buff"]("q_hit_ask", 4)] if is_native else [H["attack"](p["plain_p_dmg"], p["plain_p_ad"])]
    q_line = H["combine"](
        H["linear"]("q_piercer", p["q_speed"], p["q_range"] + 6000, p["q_w"],
                    q_hit, target="EnemyWithoutTower", penetrate=True, y=p["a_y"]),
        H["linear"]("q_raise", p["q_speed"], p["q_range"] + 6000, p["q_w"],
                    q_champ_spawn, target="EnemyChampion", penetrate=True, y=p["a_y"]),
    )
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["sfx"]("q_draw"),
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_release"), q_line)),
        ),
    )

    # W: 葬礼 — 命令所有活着的骷髅兵冲向目标并自爆 (+ 保底骨片炸圈确保无兵或连招时稳定生效)
    w_dmg = p["w_base_dmg"] if is_native else p["w_plain_dmg"]
    w_ad = p["w_base_ad"] if is_native else p["w_plain_ad"]
    w_blast = H["lob"]("w_lob", 1, [
        H["view"]("bone_burst"),
        H["sfx"]("funeral_burst"),
        H["zone"]("w_zone", p["w_r"], [
            H["attack"](w_dmg, w_ad),
            H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
            H["view"]("soul"),
        ], target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["buff"]("w_mark", 18) if is_native else None,
            H["delayed"](p["w_go"] - 1, H["alive_only"](
                H["flag"]("w_cmd", 4) if is_native else None,
                w_blast)),
        ),
    )

    # R: 亡军 — 朝天射箭，落下一片3.5万半径骨箭雨 + 地里爬出5个骷髅兵活8秒!
    # Also spawns a 4-tick follow-up arrow barrage in data when --plain or stolen by Sylas
    r_ask_enemy = H["buff"]("r_ask", 6) if is_native else None
    r_ask_self = H["flag"]("r_ask", 6) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    r_rain_hit = [
        H["attack"](p["r_dmg"], p["r_ad"]),
        H["buff"]("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
        r_ask_enemy,
        H["view"]("soul"),
        H["tsfx"]("a_hit"),
    ]
    r_follow = H["field"]("r_barrage", p["r_r"], p["r_plain_t"], p["r_plain_p"], [
        H["attack"](p["r_plain_tick_dmg"], p["r_plain_tick_ad"]),
        H["view"]("soul"),
    ], first=p["r_plain_p"], target="EnemyWithoutTower") if not is_native else None
    r_lob = H["lob"]("r_lob", p["r_travel"], [
        H["view"]("rain"),
        H["view"]("army_ring"),
        H["sfx"]("r_rain"),
        H["zone"]("r_zone", p["r_r"], r_rain_hit, target="EnemyWithoutTower"),
        r_follow,
    ], target="EnemyChampion")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_launch"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_ask_self, r_lob)),
        ),
    )

    views_p = [
        H["V_proj"]("a_arrow", "arrow"),
        H["V_proj"]("q_piercer", "piercer"),
    ]
    views_e = [
        H["V_eff"]("soul", "soul", 2),
        H["V_eff"]("pierce_flash", "pierce_flash", 2),
        H["V_eff"]("crypt", "crypt", 1, follow=False),
        H["V_eff"]("bone_burst", "bone_burst", 3, follow=False),
        H["V_eff"]("rain", "rain", 3, follow=False),
        H["V_eff"]("army_ring", "army_ring", -1, follow=False),
    ]
    views_b = []
    return wrap_kit(cid, "Range", ["AD", "Range"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:skeletons")


# ===========================================================================
# 5. 鸦医 (abysspact_corvus) · 辅助
# ===========================================================================
def build_corvus(p, is_native=True):
    cid = "abysspact_corvus"
    H = mk_helpers(cid)

    plague_ask = H["buff"]("plague_ask", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # Auto: 药瓶
    a_vial = H["homing"]("a_vial", p["a_speed"],
                         [H["attack"](0, 100), H["view"]("break"), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_vial),
        atype="BaseAttack", cancel=True,
    )

    # Q: 瘴瓶 — 抛投大瘴气瓶，2万内造成法伤+减速30% 1.5s+全部染病!
    q_hit = [
        H["ap_atk"](p["q_dmg"], p["q_ap"]),
        H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        plague_ask,
        H["view"]("break"),
    ]
    q_plain_dot = H["field"]("q_dot", p["q_r"], 240, 60, [
        H["ap_atk"](p["q_plain_dot"], p["q_plain_dot_ap"]),
    ], first=60, target="EnemyWithoutTower") if not is_native else None
    q_plain_heal = H["field"]("q_heal", p["q_r"] + 6000, 180, 60, [
        H["heal"](p["q_plain_heal"], ap_ratio=10, kind="Ally"),
    ], first=60, target="AllyChampion") if not is_native else None
    q_lob = H["lob"]("q_vial", p["q_travel"], [
        H["view"]("miasma"),
        H["sfx"]("q_ring"),
        H["zone"]("q_zone", p["q_r"], q_hit, target="EnemyWithoutTower"),
        q_plain_dot, q_plain_heal,
    ], target="EnemyWithoutTower")
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), q_lob)),
        ),
    )

    # W: 渡鸦 — 肩上乌鸦飞向队友停4秒：护盾 + 肩头乌鸦贴图 + 每秒自动啄击附近敌人染病
    w_plain_peel = H["lob"]("w_peel", 1, [
        H["zone"]("w_peck_z", p["w_plain_r"], [
            H["ap_atk"](p["w_plain_dmg"], p["w_plain_ap"]),
            H["buff"]("w_slow", 60, move_speed_mult=-20),
        ], target="EnemyWithoutTower"),
    ], target="AllyChampion") if not is_native else None
    w_land = [
        H["shield"](p["w_sh"], ap_ratio=p["w_sh_ap"], tick=p["w_t"]),
        H["buff"]("raven_perch", p["w_t"]),
        H["view"]("shield"),
        H["tsfx"]("w_wing"),
        w_plain_peel,
    ]
    w_raven = H["homing"]("w_raven", p["w_speed"], w_land, target="AllyChampion", y=-12000)
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "AllyChampion",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_cast"), w_raven)),
        ),
    )

    # R: 隔离区 — 拐杖画4万半径粉笔圈5秒：落地瞬晕0.75s+开场瘴伤，每秒圈内敌人染病减速40%、队友回血!
    r_open_hit = [
        H["ap_atk"](p["r_init_dmg"], p["r_init_ap"]),
        H["stun"](p["r_stun"]),
        plague_ask,
        H["view"]("break"),
    ]
    r_enemy_tick = [
        H["ap_atk"](p["r_tick_dmg"], p["r_tick_ap"]),
        H["buff"]("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
        plague_ask,
    ]
    r_ally_tick = [
        H["heal"](p["r_heal"], ap_ratio=p["r_heal_ap"], kind="Ally"),
        H["view"]("heal"),
    ]
    r_lob = H["lob"]("r_lob", 1, [
        H["view"]("quarantine"),
        H["sfx"]("r_cast"),
        H["zone"]("r_stun_z", p["r_r"], r_open_hit, target="EnemyWithoutTower"),
        H["field"]("r_foe_f", p["r_r"], p["r_t"], p["r_p"], r_enemy_tick, first=p["r_p"], target="EnemyWithoutTower"),
        H["field"]("r_ally_f", p["r_r"], p["r_t"], p["r_p"], r_ally_tick, first=1, target="AllyChampion"),
    ], target="EnemyChampion")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_cane"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_lob)),
        ),
    )

    views_p = [
        H["V_proj"]("a_vial", "vial"),
        H["V_proj"]("q_vial", "vial"),
        H["V_proj"]("w_raven", "raven_fly"),
    ]
    views_e = [
        H["V_eff"]("break", "break", 2),
        H["V_eff"]("miasma", "miasma", -1, follow=False),
        H["V_eff"]("transmit", "transmit", 2),
        H["V_eff"]("heal", "heal", 2),
        H["V_eff"]("shield", "shield", 2),
        H["V_eff"]("quarantine", "quarantine", -1, follow=False),
    ]
    views_b = [
        H["V_buf"]("plague", "bubbles", 2),
        H["V_buf"]("raven_perch", "raven_perch", 3),
    ]
    return wrap_kit(cid, "Util", ["AP", "Magic", "Heal", "Shield", "Dot", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:plague")


BUILDERS = {
    "oathbreaker": ("abysspact_oathbreaker", build_oathbreaker),
    "faceless":    ("abysspact_faceless",    build_faceless),
    "whisperer":   ("abysspact_whisperer",   build_whisperer),
    "bonebow":     ("abysspact_bonebow",     build_bonebow),
    "corvus":      ("abysspact_corvus",      build_corvus),
}


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", choices=list(BUILDERS.keys()), help="Build one hero (default: all 5)")
    ap.add_argument("--plain", action="store_true", help="Plain data-only mode for classic balance sim (kd.py)")
    ap.add_argument("--out", help="Output path (only valid with --hero)")
    ap.add_argument("--set", nargs="*", default=[], help="Override parameters key=value (with --hero)")
    ap.add_argument("--nodes", action="store_true")
    args = ap.parse_args()

    targets = [args.hero] if args.hero else list(BUILDERS.keys())
    for key in targets:
        cid, fn = BUILDERS[key]
        p = dict(PARAMS[key])
        if args.hero:
            for kv in args.set:
                k, v = kv.split("=", 1)
                if k not in p:
                    sys.exit(f"unknown parameter {k} for {key}")
                p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
        kit = fn(p, is_native=not args.plain)
        if args.nodes:
            print(cid, " ".join(f"{s}:{nodes(kit[s]['effect'])}" for s in ("attack", "skill", "skill2", "ult")))
        out_path = args.out if (args.hero and args.out) else os.path.join(OUT_DIR, f"{cid}.data_champion")
        os.makedirs(os.path.dirname(lp(out_path)), exist_ok=True)
        text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
        with open(lp(out_path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"wrote {out_path} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
