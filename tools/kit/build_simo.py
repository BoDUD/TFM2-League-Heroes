#!/usr/bin/env python3
"""西蒙·海耶（终末包第十九个英雄 ragnarok_simo，下路，Range）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_simo.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第十一回合的人类方代表（漫画第 98-106 话）：史上最强的狙击手「白色死神」，和洛基打的那个。神器是瓦尔基里
拉丝格瑞丝变的莫辛-纳甘 M/28-30（机械瞄具，力量全在子弹上）。他用「死神的契约」把自己的器官换成弑神弹——肾、肝、脾、胰
各一发，四发「对神狙击术」：万花缭乱（半空炸成无数碎片）、天穿白鸟（螺旋钻头弹，连穿一列）、精灵的气息（0.5 秒的神速一枪）、
天空的残光（最快最强的一枪，打穿洛基的额头）。每开一枪就换个地方，落雪盖住脚印，连摄像机都跟丢。美术、图标、音频是 Codex 的
（assets/source/simo/，交接说明 assets/source/simo/HANDOFF.md）。位置是下路（包里只有杰克一个远程）。
  被动    死神的契约：技能打出去的是器官弹，每发先付 p_cost% 最大生命（ragnarok.dll 扣，最多扣到 1 点，不会自己打死自己）；
          放的顺序照原作（肾、肝、脾，大招是胰）。--plain 给平衡模拟用：模拟跑不了 DLL，不扣血。写在普攻说明里。
  attack  莫辛-纳甘一枪打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 4 帧）出枪，子弹 810 米每秒，一出膛就到。
  skill   对神狙击术：`Targeting` EnemyWithoutTower（q_range），q_load 拍装弹，q_go 拍（第 5 帧，0.44 秒）开枪，三发轮着来：
          1 万花缭乱（肾）：子弹在半空炸开，朝目标一大片扇形（半径 q1_r，左右各 acos(q1_cone/1000)）里的敌人 q1_dmg + q1_ad%；
          2 天穿白鸟（肝）：螺旋钻头弹朝目标穿过去（一条长 q2_len、半宽 q2_w），线上的敌人 q2_dmg + q2_ad%；后坐力把他往后推
            （q2_back 速度 q2_back_t 拍）；
          3 精灵的气息（脾）：一枪打穿目标 q3_dmg + q3_ad%。
          放完一发记下一发（施法者标记 q2 / q3，死了重新从万花缭乱开始）。
  skill2  雪中隐踪：`Targeting` EnemyWithoutTower（e_range，有人贴近），e_veil 拍扬起雪幕，e_step 拍往后一跃（MoveBack，e_back 速度
          e_back_t 拍），隐身 e_inv 拍，移速 +e_ms% e_ms_t 拍（落雪盖住脚印）。
  ult     天空的残光（胰）：`Targeting` 敌方英雄（r_range），r_load 拍装弹，r_go 拍（第 5 帧，0.5 秒）开枪：r_dmg + r_ad% 攻击力、
          加目标最大生命 r_thp% 的物理伤害。开枪前被打死就不开。

时间按 Codex 的 frames.json（一秒 60 拍）：普攻第 4 帧 0.269 秒（动作 0.68 秒，22 拍的普攻第 9 拍出枪），精确一击（Q）0.205 秒
装弹、0.44 秒开枪，雪幕步（E）0.1 秒雪幕、0.25 秒踏雪，白色死神（R）0.12 秒装弹、0.5 秒开枪；动作长度 Q 48 拍、E 42 拍、R 54 拍。

ragnarok.dll（addons/ragnarok/src/simo.rs）：被动 ragnarok_simo:contract（器官弹扣血，参数 p_cost），配音和倒地声。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_simo"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：1 个游戏像素 1000；一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，下路 lane 3，600 秒，对手是四个原版射手），联盟射手中位数约 +2.7，杰克 +1.85。
# 2026-11-26：初稿 +1.20（射程 6.8 万、三发和大招偏低）；三发、大招伤害各提一到两成 +1.77；再把射程拉到 7.2 万、Q 冷却 8 -> 7 秒
# （这份）+2.33。
P = {
    # 属性（下路射手）：个子小，手稳
    "hp": 880, "hp_g": 88, "atk": 100, "atk_g": 20, "apw": 0, "apw_g": 0, "def": 20, "def_g": 6, "mr": 15,
    "mr_g": 3, "ms": 930, "ms_g": 9,
    "atk_range": 72000, "atk_dur": 22, "atk_cd": 60, "atk_st": 9,
    # 被动：死神的契约（ragnarok.dll 扣血）
    "p_cost": 3,
    # 对神狙击术
    "q_cd": 420, "q_range": 62000, "q_dur": 48, "q_load": 13, "q_go": 27,
    "q1_r": 70000, "q1_cone": 900, "q1_dmg": 85, "q1_ad": 95,
    "q2_len": 90000, "q2_w": 7000, "q2_dmg": 105, "q2_ad": 125, "q2_back": 3000, "q2_back_t": 6,
    "q3_dmg": 130, "q3_ad": 160,
    # 雪中隐踪
    "e_cd": 720, "e_range": 35000, "e_dur": 42, "e_veil": 7, "e_step": 16, "e_back": 3500, "e_back_t": 10,
    "e_inv": 75, "e_ms": 30, "e_ms_t": 120,
    # 天空的残光
    "r_cd": 3000, "r_range": 100000, "r_dur": 54, "r_load": 8, "r_go": 31, "r_dmg": 300, "r_ad": 230, "r_thp": 10,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/simo.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_cost",)


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


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的海耶（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def line(name, length, width, effects):
    """朝目标一条线（吕布天喰的做法）：LineRangeProjectile 一下打完。"""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 2, "apply": 1,
            "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in effects if e is not None]}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 普攻：莫辛-纳甘
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：对神狙击术（万花缭乱 -> 天穿白鸟 -> 精灵的气息）
    ilmatar = combine(cone(p["q1_r"], p["q1_cone"], [attack(p["q1_dmg"], p["q1_ad"]), view("q1_hit"), tsfx("q_hit")]),
                      sfx("q1"), flag("q2", None))
    swan = combine(line("q_swan", p["q2_len"], p["q2_w"], [attack(p["q2_dmg"], p["q2_ad"]), view("q_hit"), tsfx("q_hit")]),
                   {"type": "MoveBack", "speed": p["q2_back"], "tick": p["q2_back_t"]}, sfx("q2"), unflag("q2"),
                   flag("q3", None))
    spirit = combine(attack(p["q3_dmg"], p["q3_ad"]), view("q_hit"), tsfx("q_hit"), sfx("q3"), unflag("q3"))
    shot = when("q3", spirit, when("q2", swan, ilmatar))
    # 轮到哪一发放哪一套画（2026-11-26 Codex 补的子弹特效，tools/art/import_simo.py 的 ALIAS）：万花缭乱 skill_lily（枪口炸开铃兰
    # 扇形）、天穿白鸟 skill_swan（长螺旋光、脚后的后坐光），精灵的气息就是动作自己的 skill
    look = when("q3", combine(), when("q2", anim("skill_swan", p["q_dur"]), anim("skill_lily", p["q_dur"])))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(look, delayed(p["q_load"] - 1, sfx("q_load")), delayed(p["q_go"] - 1, alive_only(shot))))

    # ------------------------------------------------------------------ E：雪中隐踪
    vanish = combine({"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]},
                     search_self({"type": "CasterInvisible", "tick": p["e_inv"]}),
                     flag("e_haste", p["e_ms_t"], move_speed_mult=p["e_ms"]), sfx("e_step"), view("e_step"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_veil"] - 1, sfx("e")), delayed(p["e_step"] - 1, alive_only(vanish))))

    # ------------------------------------------------------------------ R：天空的残光
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(delayed(p["r_load"] - 1, sfx("r_load")),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), attack(p["r_dmg"], p["r_ad"], p["r_thp"]),
                                                           view("r_hit"), tsfx("r_hit")))))

    # ------------------------------------------------------------------ 画面
    # 枪口焰、短弹道、对神狙击术三发子弹和天空的残光的光迹、雪幕画在他自己的帧里（tools/art/import_simo.py）；命中的雪晶、
    # 万花缭乱的碎片光、终结命中放在目标身上，踏雪放在他脚下
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "impact"), E("q_hit", "impact"), E("q1_hit", "lily_hit"), E("r_hit", "finisher_impact", 3),
               E("e_step", "snow_step", -1)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/simo.rs）：死神的契约（扣血）、配音
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:contract", "params": {k: p[k] for k in NATIVE_KEYS}},
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
