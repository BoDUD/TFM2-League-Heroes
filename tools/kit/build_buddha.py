"""释迦（终末包第十一个英雄 ragnarok_buddha，打野，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_buddha.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第六回合的人类方选手：背弃了神、站到人类这边的神。正觉阿赖耶识（未来视）读得到对手的灵魂，招还没出就看见了；
六道棍随他的心情变形（枪刃、观音盾），和零福合成的大圆寂刀·零斩断了波旬。美术、图标、音频是 Codex 的（assets/source/buddha/，
交接说明 assets/source/buddha/HANDOFF.md），技能照 Codex 的四个动作做：
  被动    未来视：他普攻、放枪刃时，冷却（p_cd 拍）好了就看穿接下来的招：p_t 拍里普攻打不疼他（base_attack_damaged_reduce
          100，亚当神虚视的做法），头上亮一下准星。写在普攻说明里（游戏只有三个技能图标位），全在数据里。
  attack  六道棍打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 6 帧，0.287 秒）打到。
  skill   十二天斧（原作没有枪形态，长戟横扫）：`Targeting` EnemyWithoutTower（q_range）：六道棍变成枪往前一刺，q_hit 拍（第 6 帧，0.285 秒）前方窄扇形（半径 q_r，
          左右各 acos(q_cone/1000)）里的敌人 q_dmg + q_ad% 攻击力物理伤害，护甲降低 q_shred% q_shred_t 拍。
  skill2  七难即灭之盾：`Targeting` EnemyWithoutTower（e_range，有人在身边）：未来视看见要挨的打，e_go 拍（第 4 帧，0.217 秒）举起
          观音盾：护盾 e_sh + e_sh_ad% 攻击力，e_t 拍；e_cc 拍不受控制。盾收起时（e_t 拍）莲光绽开，身边 e_r 里的敌人
          e_dmg + e_ad% 物理伤害、减速 e_slow% e_slow_t 拍。中间被打死就不绽开。
  ult     大圆寂刀·零：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到斩中为止），r_go 拍（0.305 秒）
          蓄势，r_show 拍（0.423 秒）刀显形，r_cut 拍（0.510 秒）斩出，r_hit 拍（0.580 秒）斩中：前方扇形（半径 r_r，左右各
          acos(r_cone/1000)）里的敌人 r_dmg + r_ad% 攻击力、加目标最大生命 r_thp% 的物理伤害，眩晕 r_stun 拍。斩出前被打死就
          什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.236 秒挥出、0.287 秒打到，枪刃 0.176 秒起手、0.237 秒刺出、0.285 秒
刺中，观音盾 0.122 秒聚焦、0.217 秒举盾，大圆寂刀 0.305 / 0.423 / 0.510 / 0.580 秒；动作长度普攻 36 拍、枪刃 35 拍、观音盾 43 拍、
大圆寂刀 56 拍。受击动作是未来视的撤步（Codex 画的），引擎自己放。

ragnarok.dll（addons/ragnarok/src/buddha.rs）：配音和倒地声（被动 ragnarok_buddha:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_buddha"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，打野 lane 1，600 秒，对手是原版打野），2026-11-22，和赫拉克勒斯同一套对局：联盟打野对照
# 蔚 +2.21、李青 +1.98、瑟庄妮 +1.88、狼人 +0.57、扎克 +0.41、人马 -0.38（中位数约 +1.2），赫拉克勒斯 +1.52。初稿就是这份：
# +1.46 / +1.43（两批种子，16 个种子 +1.45；K/D/A 2.0 / 1.0 / 4.5，输出和对手持平、死得少一半，一局普攻 175、枪刃 49、
# 观音盾 25、大圆寂刀 6 次）。
# 2026-11-26 照原作改了十二天斧横扫以后：初版 +2.05；Q 降到 60 + 85%（这份 P）+1.25，
# 改之前 +1.45。
P = {
    # 属性（打野战士）：棍子比拳头长一点
    "hp": 1250, "hp_g": 110, "atk": 92, "atk_g": 16, "apw": 0, "apw_g": 0, "def": 42, "def_g": 7, "mr": 32,
    "mr_g": 4, "ms": 1060, "ms_g": 11,
    "atk_range": 28000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
    # 被动：未来视
    "p_cd": 480, "p_t": 90,
    # 枪刃
    "q_cd": 420, "q_range": 38000, "q_dur": 35, "q_load": 11, "q_go": 14, "q_hit": 17, "q_r": 50000, "q_cone": 800,
    "q_dmg": 60, "q_ad": 85, "q_shred": 25, "q_shred_t": 240,
    # 观音盾
    "e_cd": 720, "e_range": 32000, "e_dur": 43, "e_eye": 7, "e_go": 13, "e_t": 150, "e_sh": 100, "e_sh_ad": 80,
    "e_cc": 60, "e_r": 36000, "e_dmg": 60, "e_ad": 60, "e_slow": 30, "e_slow_t": 90,
    # 大圆寂刀·零
    "r_cd": 2700, "r_range": 36000, "r_dur": 56, "r_go": 18, "r_show": 25, "r_cut": 31, "r_hit": 35, "r_dr": 40,
    "r_r": 54000, "r_cone": 600, "r_dmg": 200, "r_ad": 150, "r_thp": 8, "r_stun": 50,
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


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的释迦（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def around(radius, effects):
    """他身边一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：未来视（普攻和枪刃时看一眼）
    sight = when("sight_cd", combine(),
                 combine(flag("sight", p["p_t"], base_attack_damaged_reduce=100), flag("sight_cd", p["p_cd"]),
                         sfx("p"), cview("p_sight")))

    # ------------------------------------------------------------------ 普攻：六道棍
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit"), sight),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：枪刃
    thrust = cone(p["q_r"], p["q_cone"], [attack(p["q_dmg"], p["q_ad"]),
                                         debuff("q_shred", p["q_shred_t"], defence_mult=-p["q_shred"]),
                                         view("a_hit"), tsfx("q_hit")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sight, delayed(p["q_load"] - 1, sfx("q_load")), delayed(p["q_go"] - 1, sfx("q")),
                           delayed(p["q_hit"] - 1, alive_only(thrust))))

    # ------------------------------------------------------------------ E：观音盾
    shield = {"type": "Shield", "amount": p["e_sh"], "attack_ratio": p["e_sh_ad"], "ap_ratio": 0, "tick": p["e_t"]}
    bloom = around(p["e_r"], [attack(p["e_dmg"], p["e_ad"]),
                              debuff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                              view("e_hit"), tsfx("e_hit")])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_eye"] - 1, sfx("e_eye")),
                            delayed(p["e_go"] - 1, alive_only(sfx("e"), search_self(shield),
                                                              flag("e_guard", p["e_cc"], cc_immune=True))),
                            delayed(p["e_go"] + p["e_t"] - 1, alive_only(sfx("e_end"), cview("e_lotus"), bloom))))

    # ------------------------------------------------------------------ R：大圆寂刀·零
    slash = cone(p["r_r"], p["r_cone"], [attack(p["r_dmg"], p["r_ad"], p["r_thp"]),
                                        {"type": "Stun", "duration": p["r_stun"]}, view("r_hit"), tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_go"] - 1, alive_only(sfx("r_load"))),
                         delayed(p["r_show"] - 1, alive_only(sfx("r_show"))),
                         delayed(p["r_cut"] - 1, alive_only(sfx("r"))),
                         delayed(p["r_hit"] - 1, alive_only(slash))))

    # ------------------------------------------------------------------ 画面
    # 棍风、枪刃、未来视的准星（观音盾里）、莲光、撤步的气流、大圆寂刀的气和刀光画在他自己的帧里（tools/art/import_buddha.py）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "staff_impact"), E("e_hit", "shield_impact"), E("r_hit", "staff_impact", 3),
               E("p_sight", "future_sight", 3), E("e_lotus", "lotus_guard", 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Shield", "CC"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/buddha.rs）：配音、倒地声
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
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的配音被动")
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
