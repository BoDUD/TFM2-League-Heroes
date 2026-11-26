#!/usr/bin/env python3
"""须佐之男命（终末包第二十二个英雄 ragnarok_susanoo，上路，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_susanoo.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第十回合的神方代表（漫画第 86-96 话）：剑之神，千年来学会了人类所有的剑术流派，和冲田总司打的那个。刀是用人类和神的
铁匠重锻天丛云剑打成的鬼切天丛云。「神罗八百万」：普通的正眼构，能用人类有过的任何剑技回应；「奥义·天魔反」：右臂后拉、刀竖着、
左掌张开向前追着对手，对手一进距离就挥刀，空气被切成月牙形的真空刃，远远超出刀长、越远越弱；「天魔反·无间」：不蓄力，更快更弱；
「无装剑」：刀断了以后空手举着像握刀，一把看不见的无之剑隔空只砍身体里面的骨头，他每挥一次都在磨损自己的生命和灵魂。
美术、图标、音效是 Codex 的（assets/source/susanoo/，交接说明 assets/source/susanoo/HANDOFF.md；没有配音）。
位置是上路战士（用户 2026-11-26 定的）。
  被动    天魔反·无间：每第三下普攻不蓄力地带出一道真空刃：朝目标一条（长 p_len、半宽 p_w）上的敌人 p_dmg + p_ad%（普攻那一下
          另算）。计数是施法者标记 a1 / a2，死了重新数。写在普攻说明里，全在数据里。
  attack  一刀 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 4 帧，0.28 秒）出刀，刀长（射程 atk_range）。
  skill   奥义·天魔反：`Targeting` EnemyWithoutTower（q_range）：摆出天魔反的架势蓄势，q_go 拍（第 5 帧，0.3 秒）挥刀，月牙真空刃
          朝目标飞出去：一条（长 q_len、半宽 q_w）上的敌人 q_dmg + q_ad%；身前（半径 q_near、左右各 acos(q_cone/1000)）的敌人
          离得近，再吃 q2_dmg + q2_ad%（越远越弱）。
  skill2  神罗八百万：`Targeting` EnemyWithoutTower（e_range，有人在身边）：e_set 拍（第 2 帧）摆出正眼构，到 e_go 拍（第 5 帧）
          为止普攻打不疼他（base_attack_damaged_reduce 100）、技能伤害降低 e_sdr%；e_go 拍用接下来的剑技回应：前方扇形（半径 e_r，
          左右各 acos(e_cone/1000)）里的敌人 e_dmg + e_ad%，眩晕 e_stun 拍。
  ult     无装剑：`Targeting` 敌方英雄（r_range，隔空）：空手举起看不见的剑，到挥下为止不受控制；r_go 拍（第 4 帧，0.3 秒）挥下，
          只砍骨头：r_dmg + r_ad% 攻击力、加目标最大生命 r_thp% 的真实伤害（不看护甲），r_t 拍里移速 -r_slow%、攻击力 -r_atk%
          （手骨腿骨断了）。每挥一次磨损他自己的生命：ragnarok.dll 扣 r_cost% 最大生命（最多扣到 1 点）。挥下前被打死就什么都不发生。

时间按 Codex 的 frames.json（一秒 60 拍）：普攻第 4 帧 0.28 秒，天魔反 0 秒蓄势、0.3 秒剑压，异形架势 0.105 秒剑气、0.39 秒释放，
无装剑 0 秒蓄势、0.3 秒裂光；动作长度普攻 0.735 秒、Q 42 拍、E 49 拍、R 47 拍。

ragnarok.dll（addons/ragnarok/src/susanoo.rs）：被动 ragnarok_susanoo:musou（无装剑的代价，参数 r_cost）和倒地声。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_susanoo"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，上路 lane 0，600 秒，对手是原版上单），小次郎、吕布作对照。
# 2026-11-26 新英雄（上路）：初版 +0.56；Q 真空刃 80 + 90%、贴身再吃 50 + 60%，
# 被动 40 + 50%，R 150 + 110%（这份 P）+1.38，和吕布（+1.71）、索尔（+1.07）
# 一档；再加血量、攻击 +2.14 太强。
P = {
    # 属性（上路战士）
    "hp": 1150, "hp_g": 105, "atk": 92, "atk_g": 16, "apw": 0, "apw_g": 0, "def": 38, "def_g": 6, "mr": 32,
    "mr_g": 4, "ms": 1060, "ms_g": 10,
    "atk_range": 28000, "atk_dur": 36, "atk_cd": 60, "atk_st": 14,
    # 被动：天魔反·无间
    "p_len": 45000, "p_w": 6000, "p_dmg": 40, "p_ad": 50,
    # 奥义·天魔反
    "q_cd": 480, "q_range": 48000, "q_dur": 42, "q_go": 18, "q_len": 70000, "q_w": 9000, "q_dmg": 80, "q_ad": 90,
    "q_near": 32000, "q_cone": 820, "q2_dmg": 50, "q2_ad": 60,
    # 神罗八百万
    "e_cd": 720, "e_range": 30000, "e_dur": 49, "e_set": 7, "e_go": 24, "e_sdr": 40, "e_r": 36000, "e_cone": 600,
    "e_dmg": 70, "e_ad": 80, "e_stun": 45,
    # 无装剑
    "r_cd": 3000, "r_range": 45000, "r_dur": 47, "r_go": 18, "r_dmg": 150, "r_ad": 110, "r_thp": 8, "r_t": 180,
    "r_slow": 30, "r_atk": 20, "r_cost": 5,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/susanoo.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("r_cost",)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def true_dmg(dmg, ratio, thp=0):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的须佐之男（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def line(name, length, width, effects):
    """朝目标一条（吕布天喰的做法：两拍的判定线，打到线上每个敌人一次）。"""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 2, "apply": 1,
            "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 普攻 + 被动：天魔反·无间（每第三刀带一道真空刃）
    mugen = combine(line("p_mugen", p["p_len"], p["p_w"], [attack(p["p_dmg"], p["p_ad"]), view("a_hit")]), sfx("p"),
                    unflag("a1"), unflag("a2"))
    count = when("a2", mugen, when("a1", flag("a2", None), flag("a1", None)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), count, sfx("a"), view("a_hit"), tsfx("a_hit")), atype="BaseAttack",
                      cancel=True)

    # ------------------------------------------------------------------ Q：奥义·天魔反（月牙真空刃，越远越弱）
    wave = combine(line("q_wave", p["q_len"], p["q_w"], [attack(p["q_dmg"], p["q_ad"]), view("a_hit")]),
                   cone(p["q_near"], p["q_cone"], [attack(p["q2_dmg"], p["q2_ad"])]), sfx("q"), tsfx("q_hit"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_load"), delayed(p["q_go"] - 1, alive_only(wave))))

    # ------------------------------------------------------------------ E：神罗八百万（正眼构接招，再回应）
    guard = flag("e_guard", p["e_go"] - p["e_set"] + 1, base_attack_damaged_reduce=100, damaged_reduce=p["e_sdr"])
    answer = cone(p["e_r"], p["e_cone"], [attack(p["e_dmg"], p["e_ad"]), {"type": "Stun", "duration": p["e_stun"]},
                                          view("a_hit")])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_set"] - 1, sfx("e"), guard),
                            delayed(p["e_go"] - 1, alive_only(sfx("e_go"), answer, tsfx("e_hit")))))

    # ------------------------------------------------------------------ R：无装剑（隔空只砍骨头，真实伤害）
    cut = combine(true_dmg(p["r_dmg"], p["r_ad"], p["r_thp"]),
                  debuff("r_bone", p["r_t"], move_speed_mult=-p["r_slow"], attack_mult=-p["r_atk"]), view("r_hit"),
                  tsfx("r_hit"))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_go"], cc_immune=True), sfx("r_load"),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), cut))))

    # ------------------------------------------------------------------ 画面
    # 刀光、天魔反的蓄势和剑压、架势的剑气和释放、无装剑的蓄势和裂光画在他自己的帧里（tools/art/import_susanoo.py）；
    # 命中的火花在目标身上
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "hit_spark"), E("r_hit", "hit_spark", 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll（addons/ragnarok/src/susanoo.rs）：无装剑的代价、倒地声
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:musou", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, not a.plain)
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
