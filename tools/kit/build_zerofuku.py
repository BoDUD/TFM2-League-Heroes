"""零福／波旬（终末包第十二个英雄 ragnarok_zerofuku，上路，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_zerofuku.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第六回合的神方选手：七福神合在一起的不幸之神零福，斧爻吸了人的不幸越长越大；输给释迦时，藏在他里面的第六天
魔王波旬把他吞掉、破茧而出。美术、图标、音频是 Codex 的（assets/source/zerofuku/，交接说明 assets/source/zerofuku/HANDOFF.md；
斧爻在 tools/art/zerofuku_fix.py 里重贴过），技能照 Codex 的两套动作做：零福，和破茧以后的波旬（这条命一直是波旬，死了复活
又是零福）。形态是一个 buff（hajun，一直挂到死）：每个技能按它分两版（SwitchByBuff），ragnarok.dll 的显示钩子按它换上 h_* 的帧。
  被动    不幸（零福）：普攻和不幸斧爻打中的敌人挂上不幸 p_t 拍：受到的伤害增加 p_amp%（谁打都算），身上绕着不幸的黑气。
          吞噬（波旬）：吸血 h_vamp%（形态的 buff 上）。两个都写在普攻说明里（游戏只有三个技能图标位）。
  attack  零福：斧爻横砍 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.287 秒）打到，挂不幸。
          波旬：前臂化刃横斩，100% 攻击力，一样的时刻（h_attack 按零福的节奏重排过）。
  skill   零福·不幸斧爻：`Targeting` EnemyWithoutTower（q_range）：q_load 拍（第 3 帧）斧爻吸聚不幸、斧刃变大，q_hit 拍（第 5 帧）
          落斧：前方扇形（半径 q_r，左右各 acos(q_cone/1000)）里的敌人 q_dmg + q_ad% 攻击力物理伤害、减速 q_slow% q_slow_t 拍，
          挂不幸。
          波旬·魔钻：前臂化成螺旋魔钻，q_hit 拍朝目标直线冲过去（RushTime，穿过去，吕布破阵的做法，速度 q2_speed、q2_t 拍）：
          路上 q2_r 里的敌人 q2_dmg + q2_ad% 物理伤害、击飞 q2_air 拍。
  skill2  零福·怨气冲击：`Targeting` EnemyWithoutTower（e_range）：低姿架斧，e_go 拍（第 4 帧）怨气从脚下往前涌，e_hit 拍（第 5 帧）
          打到：朝目标一条（长 e_len、半宽 e_w）里的敌人 e_dmg + e_ad% 物理伤害、击飞 e_air 拍。
          波旬·魔刃碎击：单臂化成厚刃从上往下砸，e_hit 拍：前方扇形（半径 e2_r，左右各 acos(e2_cone/1000)）里的敌人
          e2_dmg + e2_ad% 物理伤害、眩晕 e2_stun 拍。
  ult     零福·破茧：`Targeting` 敌方英雄（r_range）：被暗茧吞没，整个动作不受控制、受到的伤害降低 r_dr%；r_shell 拍茧合上，
          r_open 拍（第 6 帧，0.58 秒）波旬破茧而出：回复 r_heal + r_heal_ad% 攻击力的生命，这条命一直是波旬：攻击力 +h_atk%、
          攻速 +h_as%、移速 +h_ms%、护甲和魔抗 +h_res、吸血 h_vamp%。破茧前被打死就什么都不发生。
          波旬·魔臂横断（形态里再放）：起手到斩中不受控制、受到的伤害降低 r_dr%，重臂刃蓄势，r2_hit 拍（第 5 帧，0.423 秒）横断：
          前方扇形（半径 r2_r，左右各 acos(r2_cone/1000)）里的敌人 r2_dmg + r2_ad% 攻击力、加目标最大生命 r2_thp% 的物理伤害，
          击飞 r2_air 拍。斩中前被打死就什么都不发生。动作是 h_ult（CasterAnimation；显示钩子不换 ult，破茧那段照放）。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.236 秒挥出、0.287 秒打到，不幸斧爻 0.176 秒吸聚、0.285 秒落斧，
怨气冲击 0.292 秒涌出、0.354 秒打到，破茧 0.305 秒合茧、0.58 秒破茧，魔臂横断 0.423 秒斩中；动作长度普攻 36 拍、Q 35 拍、
E 43 拍、大招 56 拍（波旬的 h_attack / h_skill / h_ult 在 tools/art/import_zerofuku.py 里按这些长度重排过）。

ragnarok.dll（addons/ragnarok/src/zerofuku.rs）：配音、倒地声和波旬形态的显示（被动 ragnarok_zerofuku:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_zerofuku"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，上路 lane 0，600 秒，对手和吕布、小次郎同一套：基础战士和另外五个原版上单，每批种子
# 288 局，16 个种子的击杀差标准误约 ±0.30，两批之间差得不少，都看 32 个种子），2026-11-22。这套对局里联盟战士的中位数约
# +1.44，终末包的上单：吕布 1.43、亚当 1.38、宙斯 1.24、索尔 1.09、小次郎约 1.5。初稿 +3.61（波旬形态攻击、攻速 +30%、
# 吸血 15%，一直到死；一局回血 6800）；形态减半 +2.38；再把技能伤害降两成 +1.11；形态 +20% 加技能降两成 +1.44 / +0.68
# （32 个种子 +1.06）；技能伤害取中间 +1.74 / +1.13（+1.44）；形态 +20% 加伤害取中间 +2.02 / +1.75（+1.89）。这份（形态
# 攻击、攻速 +15%，技能伤害取中间，零福的血、攻击、双抗小降：零福自己不算强，破茧以后明显变强）+1.41 / +1.56（+1.49，
# K/D/A 2.2 / 1.3 / 4.1，一局普攻 128、Q 39、E 28、大招 6 次）。
P = {
    # 属性（上路战士）：零福瘦，斧子长
    "hp": 1100, "hp_g": 108, "atk": 93, "atk_g": 17, "apw": 0, "apw_g": 0, "def": 34, "def_g": 7, "mr": 27,
    "mr_g": 4, "ms": 1030, "ms_g": 11,
    "atk_range": 28000, "atk_dur": 36, "atk_cd": 66, "atk_st": 17,
    # 被动：不幸
    "p_t": 240, "p_amp": 8,
    # 不幸斧爻 / 魔钻
    "q_cd": 480, "q_range": 40000, "q_dur": 35, "q_load": 11, "q_hit": 17, "q_r": 42000, "q_cone": 600,
    "q_dmg": 62, "q_ad": 110, "q_slow": 30, "q_slow_t": 90,
    "q2_speed": 3200, "q2_t": 11, "q2_r": 15000, "q2_dmg": 55, "q2_ad": 100, "q2_air": 30,
    # 怨气冲击 / 魔刃碎击
    "e_cd": 600, "e_range": 32000, "e_dur": 43, "e_go": 18, "e_hit": 21, "e_len": 48000, "e_w": 9000,
    "e_dmg": 55, "e_ad": 72, "e_air": 36,
    "e2_r": 38000, "e2_cone": 500, "e2_dmg": 62, "e2_ad": 90, "e2_stun": 45,
    # 破茧 / 魔臂横断
    "r_cd": 2400, "r_range": 40000, "r_dur": 56, "r_shell": 18, "r_open": 35, "r_dr": 40,
    "r_heal": 100, "r_heal_ad": 50, "h_atk": 15, "h_as": 15, "h_ms": 5, "h_res": 10, "h_vamp": 8,
    "r2_hit": 25, "r2_r": 54000, "r2_cone": 600, "r2_dmg": 165, "r2_ad": 125, "r2_thp": 6, "r2_air": 40,
}


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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的零福（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def line(name, length, width, effects):
    """朝目标一条（长 length、半宽 width，吕布天喰的做法：两拍的判定线，打到线上每个敌人一次）。"""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 2, "apply": 1,
            "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    mark = debuff("mark", p["p_t"], damaged_amplify=p["p_amp"])

    # ------------------------------------------------------------------ 普攻：斧爻 / 臂刃
    zero_a = combine(attack(0, 100), mark, sfx("a"), view("a_hit"), tsfx("a_hit"))
    hajun_a = combine(attack(0, 100), sfx("ha"), view("ha_hit"), tsfx("ha_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      when("hajun", hajun_a, zero_a), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：不幸斧爻 / 魔钻
    smash = cone(p["q_r"], p["q_cone"], [attack(p["q_dmg"], p["q_ad"]),
                                        debuff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), mark,
                                        view("q_hit"), tsfx("q_hit")])
    cleaver = combine(delayed(p["q_load"] - 1, sfx("q_load")), delayed(p["q_hit"] - 1, alive_only(sfx("q"), smash)))
    passed = [{"casting_type": "Targeting", "effect": e} for e in
              (attack(p["q2_dmg"], p["q2_ad"]), {"type": "Airborne", "duration": p["q2_air"]}, view("hq_hit"),
               tsfx("hq_hit"))]
    rush = {"type": "RushTime", "speed": p["q2_speed"], "tick": p["q2_t"], "range": p["q2_r"],
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": passed}
    drill = combine(delayed(p["q_load"] - 1, sfx("hq_load")), delayed(p["q_hit"] - 1, sfx("hq"), rush))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   when("hajun", drill, cleaver))

    # ------------------------------------------------------------------ E：怨气冲击 / 魔刃碎击
    surge = line("e_line", p["e_len"], p["e_w"], [attack(p["e_dmg"], p["e_ad"]),
                                                  {"type": "Airborne", "duration": p["e_air"]},
                                                  view("e_hit"), tsfx("e_hit")])
    grudge = combine(delayed(p["e_go"] - 1, alive_only(sfx("e"))), delayed(p["e_hit"] - 1, alive_only(surge)))
    crush_hit = cone(p["e2_r"], p["e2_cone"], [attack(p["e2_dmg"], p["e2_ad"]), {"type": "Stun", "duration": p["e2_stun"]},
                                              view("he_hit"), tsfx("he_hit")])
    crush = combine(delayed(p["e_hit"] - 1, alive_only(sfx("he"), crush_hit)))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    when("hajun", crush, grudge))

    # ------------------------------------------------------------------ R：破茧 / 魔臂横断
    hajun = flag("hajun", None, attack_mult=p["h_atk"], attack_speed_mult=p["h_as"], move_speed_mult=p["h_ms"],
                 defence=p["h_res"], magic_resistance=p["h_res"], vamp=p["h_vamp"])
    heal = {"type": "Heal", "amount": p["r_heal"], "attack_ratio": p["r_heal_ad"], "ap_ratio": 0, "heal_type": "Caster"}
    cocoon = combine(flag("r_guard", p["r_dur"], cc_immune=True, damaged_reduce=p["r_dr"]),
                     delayed(p["r_shell"] - 1, alive_only(sfx("r_shell"))),
                     delayed(p["r_open"] - 1, alive_only(sfx("r_open"), heal, hajun)))
    cut = cone(p["r2_r"], p["r2_cone"], [attack(p["r2_dmg"], p["r2_ad"], p["r2_thp"]),
                                        {"type": "Airborne", "duration": p["r2_air"]}, view("r2_hit"), tsfx("r2_hit")])
    sever = combine(anim("h_ult", p["r_dur"]),
                    flag("r_guard", p["r2_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                    delayed(p["r2_hit"] - 1, alive_only(sfx("r2"), cut)))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 when("hajun", sever, cocoon))

    # ------------------------------------------------------------------ 画面
    # 斧爻和臂刃的斩痕、Q 吸聚的不幸、魔钻的螺旋、怨气、破茧的碎壳画在他自己的帧里（tools/art/import_zerofuku.py）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "cleaver_impact"), E("q_hit", "cleaver_impact"), E("e_hit", "cleaver_impact"),
               E("ha_hit", "demon_impact"), E("hq_hit", "demon_impact"), E("he_hit", "demon_impact"),
               E("r2_hit", "demon_impact", 3)]
    # 挂着不幸的敌人身上绕着不幸的黑气（buff 在就一直放）
    views_b = [{"type": "Animated", "name": n("mark"), "anim": FX, "tag": "misfortune", "repeat": True, "z": 1}]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Heal"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # ragnarok.dll（addons/ragnarok/src/zerofuku.rs）：配音、倒地声、波旬形态的显示
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:voice", "params": {}},
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
