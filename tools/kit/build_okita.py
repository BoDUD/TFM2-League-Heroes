#!/usr/bin/env python3
"""冲田总司（终末包第二十一个英雄 ragnarok_okita，打野，Assassin）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_okita.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第十回合的人类方代表（漫画第 86-96 话）：新选组一番队队长，天然理心流的天才剑士，和须佐之男打的那个，赢了。
神器是瓦尔基里斯卡尔莫尔德变的武士刀，性质是「剑之刻」——把他过去、现在、和没生病本该有的未来的剑技压进一刻，把身体改造成
配合这把剑。极度兴奋时变成「鬼子」：心脏泵三倍的血、眼睛发红、快到留下残影、一次出好几刀。终结技「天翔散段突」：极快地突进、
三刺，刺到刀够不到的地方。美术、图标、音频是 Codex 的（assets/source/okita/，交接说明 assets/source/okita/HANDOFF.md；
六句日语台词是 Codex 用语音合成做的，用户 2026-11-26 说要用）。位置是打野刺客（用户 2026-11-26 定的）。
  被动    剑之刻：每放一个技能，p_t 拍里攻速 +p_as%（剑越出越快）。写在普攻说明里，全在数据里。
  attack  一刀 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.335 秒）出刀。
  skill   天然理心流奥义·三段突：`Targeting` EnemyWithoutTower（q_range）：第 2、4、6 帧（q1 / q2 / q3 拍）神速三刺，每刺打前方窄扇形
          （半径 q_r，左右各 acos(q_cone/1000)）里的敌人 q_dmg + q_ad%，第三刺再加 q3_dmg + q3_ad%。
  skill2  鬼子：`Targeting` 敌方英雄（e_range），e_charge 拍心跳加速，e_go 拍（第 5 帧，0.39 秒）眼睛变红：e_t 拍里攻击力 +e_atk%、
          攻速 +e_as%、移速 +e_ms%（残影、一次几刀），身上一圈红气。
  ult     天翔散段突：`Targeting` 敌方英雄（r_range）：r_charge 拍蓄势（不受控制，到刺完为止），r_go 拍（第 4 帧，0.3 秒）极快地
          冲过去（RushTime，r_speed x r_t 拍，碰到就停），刺中的人连吃三刺（每隔 r_gap 拍）：r_dmg + r_ad%，第三刺再加目标最大
          生命 r_thp%（刺要害）。冲出去前被打死就什么都不发生。

时间按 Codex 的 frames.json（一秒 60 拍）：普攻第 5 帧 0.335 秒，三连刺 0.105 / 0.245 / 0.39 秒，鬼子 0.105 秒蓄势、0.39 秒启动，
终结突刺 0.12 秒蓄势、0.3 秒出刀；动作长度普攻 0.735 秒、Q 42 拍、E 49 拍、R 47 拍。

ragnarok.dll（addons/ragnarok/src/okita.rs）：配音和倒地声（被动 ragnarok_okita:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_okita"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，打野 lane 1，600 秒，对手是原版打野），联盟打野中位数约 +1.2，哈迪斯 +1.17、特斯拉 +1.13。
P = {
    # 属性（打野刺客）：脚快
    "hp": 1000, "hp_g": 95, "atk": 96, "atk_g": 17, "apw": 0, "apw_g": 0, "def": 30, "def_g": 5, "mr": 30,
    "mr_g": 4, "ms": 1090, "ms_g": 11,
    "atk_range": 26000, "atk_dur": 36, "atk_cd": 58, "atk_st": 16,
    # 被动：剑之刻
    "p_t": 180, "p_as": 30,
    # 三段突
    "q_cd": 420, "q_range": 34000, "q_dur": 42, "q1": 7, "q2": 15, "q3": 24, "q_r": 40000, "q_cone": 940,
    "q_dmg": 30, "q_ad": 45, "q3_dmg": 30, "q3_ad": 30,
    # 鬼子
    "e_cd": 900, "e_range": 40000, "e_dur": 49, "e_charge": 7, "e_go": 24, "e_t": 300, "e_atk": 20, "e_as": 30,
    "e_ms": 15,
    # 天翔散段突
    "r_cd": 2700, "r_range": 45000, "r_dur": 47, "r_charge": 8, "r_go": 18, "r_speed": 9000, "r_t": 6, "r_gap": 5,
    "r_dmg": 70, "r_ad": 70, "r_thp": 10,
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


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的冲田（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：剑之刻（放技能以后攻速变快）
    sword_time = flag("p_time", p["p_t"], attack_speed_mult=p["p_as"])

    # ------------------------------------------------------------------ 普攻：一刀
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：三段突（第 2、4、6 帧各一刺）
    def thrust(k, extra=None):
        return delayed(p[f"q{k}"] - 1, alive_only(sfx(f"q{k}"), cone(p["q_r"], p["q_cone"], [
            attack(p["q_dmg"], p["q_ad"]), extra, view("a_hit"), tsfx("q_hit")])))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sword_time, thrust(1), thrust(2), thrust(3, attack(p["q3_dmg"], p["q3_ad"]))))

    # ------------------------------------------------------------------ E：鬼子
    oni = combine(flag("oni", p["e_t"], attack_mult=p["e_atk"], attack_speed_mult=p["e_as"], move_speed_mult=p["e_ms"]),
                  sfx("e"), *[delayed(t, view("e_aura")) for t in range(0, p["e_t"] - 45, 46)])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sword_time, delayed(p["e_charge"] - 1, sfx("e_charge")),
                            delayed(p["e_go"] - 1, alive_only(search_self(oni)))))

    # ------------------------------------------------------------------ R：天翔散段突（突进 + 三刺）
    stabs = [attack(p["r_dmg"], p["r_ad"]), view("r_hit"), tsfx("r_hit"),
             delayed(p["r_gap"], attack(p["r_dmg"], p["r_ad"]), view("a_hit")),
             delayed(2 * p["r_gap"], attack(p["r_dmg"], p["r_ad"], p["r_thp"]), view("r_hit"), tsfx("r_hit"))]
    dash = {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False,
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in stabs]}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sword_time, flag("r_guard", p["r_go"] + p["r_t"] + 2 * p["r_gap"], cc_immune=True),
                         delayed(p["r_charge"] - 1, alive_only(sfx("r_load"))),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), {"type": "CasterViewEffect", "name": n("r_step")},
                                                           dash))))

    # ------------------------------------------------------------------ 画面
    # 刀光、三段突的突刺光、鬼子启动的红光、终结突刺的光柱画在他自己的帧里（tools/art/import_okita.py）；鬼子的红气挂在他身上
    # （46 拍一圈：8 帧 x 0.095 秒 = 0.76 秒），突进起步的踏步残影留在原地，命中在目标身上
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    views_e = [E("a_hit", "sword_hit"), E("r_hit", "finisher_hit", 3), E("e_aura", "oni_aura", -1),
               E("r_step", "quick_step", -1, False)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/okita.rs）：配音、倒地声
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
