#!/usr/bin/env python3
"""洛基（终末包第二十个英雄 ragnarok_loki，中路，Magician）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_loki.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第十一回合的神方代表（漫画第 98-106 话）：骗术之神，和西蒙·海耶打的那个。手套掌心的黑圈是门，伸出双链钩；
「道化师之环」（海姆斯克林拉）碰过的东西都能复制——指尖「封闭者」记下，掌心「欺瞒之种」从黑雾里造出来，复制体不说话、听他的；
还藏着三招：「虚伪之神影」（一个满力、自己会打、会用他招式的分身）、「九界的窥视孔」、「回生之门」（和连着的复制体换位置）。
美术、图标、音频是 Codex 的（assets/source/loki/，交接说明 assets/source/loki/HANDOFF.md；六句是动画洛基的声优松冈禎丞的原声）。
位置是中路法师（用户 2026-11-26 定的）：包里第二个打魔法伤害的，技能按法术强度（ApAttack 的 attack_ratio 是法强的百分比）。
  被动    虚伪之神影：他满力的分身照着他出招——锁链钩打中的敌人，p_delay 拍后分身的钩子从黑雾里再挥一下：p_dmg + p_ap% 法强
          魔法伤害。写在普攻说明里（游戏只有三个技能图标位），全在数据里。
  attack  幻刃 `Enemy`（塔也打）：atk_st 拍（第 4 帧）从手套里弹出一道幻刃飞向目标（a_speed），打到 100% 攻击力物理伤害。
  skill   锁链钩：`Targeting` EnemyWithoutTower（q_range）：q_wind 拍掌心开门垂下锁链，q_go 拍（第 4 帧，0.297 秒）钩刃甩出去：
          q_dmg + q_ap% 法强魔法伤害、减速 q_slow% q_slow_t 拍（被动的分身跟着再挥一钩）。
  skill2  欺瞒之种·回生之门：`Targeting` 敌方英雄（e_range，有人贴近）：e_mist 拍脚下涌出黑雾，e_decoy 拍（第 4 帧）黑雾里造出一个
          他的复制体留在原地、他和更远处的复制体换了位置（往后飘 e_back 速度 e_back_t 拍），隐身 e_inv 拍，移速 +e_ms% e_ms_t 拍。
  ult     道化师之环：`Targeting` 敌方英雄（r_range）：r_load 拍蓄势（不受控制，到放出为止），r_go 拍（第 5 帧，0.46 秒）目标周围
          冒出一片复制出来的神兵（幻影军势），每 r_gap 拍打一轮、共 r_n 轮：半径 r_r 里的敌人每轮 r_dmg + r_ap% 法强魔法伤害，
          减速 r_slow% 到打完。放出前被打死就什么都不发生。

时间按 Codex 的 frames.json（一秒 60 拍）：普攻第 4 帧 0.279 秒，锁链钩 0.105 秒垂链、0.297 秒甩出，迷雾诱饵 0.2 秒黑雾、0.287 秒
诱饵显形，幻影军势 0.12 秒蓄势、0.46 秒放出；动作长度 Q 45 拍、E 48 拍、R 54 拍。

ragnarok.dll（addons/ragnarok/src/loki.rs）：配音和倒地声（被动 ragnarok_loki:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_loki"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：1 个游戏像素 1000；一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，中路 lane 2，600 秒，对手是原版中单），联盟中单中位数约 +2.5，别西卜 +2.46。
# 幻刃的高度：Codex 的出手点在脚底上 30 格 = 60 / (8/3) = 22.5 个游戏像素，弹道画面在落点（脚底上 11.5）往北 5000 - y_offset：
# y_offset = 5000 - (22.5 - 11.5) x 1000 = -6000
# 2026-11-26 新英雄（中路）：初版 -4.25；Q 只钩英雄、冷却 3 秒、170 + 140%，R 打四轮、每轮 280 + 130%、第一轮眩晕 30 拍，
# 被动 50 + 50%，身板和攻击各加一档（这份 P）+2.66，中路中位数约 +2.5。
P = {
    # 属性（远程法师）
    "hp": 960, "hp_g": 88, "atk": 75, "atk_g": 9, "apw": 70, "apw_g": 25, "def": 26, "def_g": 5, "mr": 28,
    "mr_g": 4, "ms": 1050, "ms_g": 10,
    "atk_range": 50000, "atk_dur": 36, "atk_cd": 66, "atk_st": 15, "a_speed": 9000, "a_y": -6000,
    # 被动：虚伪之神影
    "p_delay": 18, "p_dmg": 50, "p_ap": 50,
    # 锁链钩
    "q_cd": 300, "q_range": 50000, "q_dur": 45, "q_wind": 7, "q_go": 18, "q_dmg": 170, "q_ap": 140, "q_slow": 30,
    "q_slow_t": 60, "q_champ": 1, "q_line": 0, "q_len": 55000, "q_w": 9000,
    # 欺瞒之种·回生之门
    "e_cd": 780, "e_range": 50000, "e_dur": 48, "e_mist": 13, "e_decoy": 18, "e_back": 4000, "e_back_t": 10,
    "e_inv": 90, "e_ms": 25, "e_ms_t": 120, "e_sh": 0, "e_sh_ap": 0, "e_sh_t": 150,
    # 道化师之环
    "r_cd": 3000, "r_range": 52000, "r_dur": 54, "r_load": 8, "r_go": 28, "r_r": 30000, "r_n": 4, "r_gap": 24,
    "r_dmg": 280, "r_ap": 130, "r_slow": 30, "r_stun": 30,
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


def magic(dmg, ap):
    """魔法伤害：dmg + ap% 法强（ApAttack 的 attack_ratio 是法强的百分比）。"""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "attack_effect_type": "Target"}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的洛基（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def zone(name, radius, effects):
    """目标那里一圈（半径 radius）里的敌人（特斯拉神之监狱的做法：RangeProjectile 落在目标身上）。"""
    return {"type": "RangeProjectile", "name": n(name), "shape": {"Circle": {"radius": radius}}, "delay": 2, "apply": 1,
            "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 普攻：幻刃
    blade = {"type": "TargetProjectile", "name": n("a_blade"), "speed": p["a_speed"], "y_offset": p["a_y"],
             "applied_target": "Enemy",
             "applied_effects": [{"casting_type": "Targeting", "effect": combine(attack(0, 100), view("a_hit"),
                                                                                  tsfx("a_hit"))}]}
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), blade), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：锁链钩（被动：分身再挥一钩）
    double = delayed(p["p_delay"], magic(p["p_dmg"], p["p_ap"]), view("p_hit"), tsfx("p_hit"))
    hooked = combine(magic(p["q_dmg"], p["q_ap"]), debuff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                     view("q_hit"), tsfx("q_hit"), double)
    q_target = "EnemyChampion" if p["q_champ"] else "EnemyWithoutTower"
    # q_line：钩刃顺着链子一路钩过去，朝目标一条线上的敌人都挨（LineRangeProjectile，打到线上每个敌人一次）
    lash = ({"type": "LineRangeProjectile", "name": n("q_lash"), "width": p["q_w"], "length": p["q_len"], "delay": 2,
             "apply": 1, "applied_target": "EnemyWithoutTower",
             "applied_effects": [{"casting_type": "Targeting", "effect": hooked}]} if p["q_line"] else hooked)
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", q_target,
                   combine(delayed(p["q_wind"] - 1, sfx("q_wind")), delayed(p["q_go"] - 1, alive_only(sfx("q"), lash))))

    # ------------------------------------------------------------------ E：欺瞒之种·回生之门
    # e_sh：斯库尔德之盾（原作里他复制出来的石墙和华丽的门，挡了天穿白鸟几秒），换位时挡在身前
    skuld = ({"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_sh_ap"], "tick": p["e_sh_t"]}
             if p["e_sh"] else None)
    swap = combine(search_self(skuld) if skuld else None, {"type": "CasterViewEffect", "name": n("e_decoy")},
                   {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]},
                   search_self({"type": "CasterInvisible", "tick": p["e_inv"]}),
                   flag("e_haste", p["e_ms_t"], move_speed_mult=p["e_ms"]), sfx("e_decoy"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(delayed(p["e_mist"] - 1, sfx("e")), delayed(p["e_decoy"] - 1, alive_only(swap))))

    # ------------------------------------------------------------------ R：道化师之环（幻影军势）
    strikes = []
    for k in range(p["r_n"]):
        stun = {"type": "Stun", "duration": p["r_stun"]} if k == 0 and p["r_stun"] else None
        hit = zone(f"r_wave{k + 1}", p["r_r"], [magic(p["r_dmg"], p["r_ap"]), stun,
                                                debuff("r_slow", p["r_gap"] * (p["r_n"] - k), move_speed_mult=-p["r_slow"]),
                                                view("r_hit")])
        strikes.append(delayed(p["r_go"] - 1 + k * p["r_gap"], alive_only(hit, tsfx("r_hit") if k == 0 else None)))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_go"], cc_immune=True),
                         delayed(p["r_load"] - 1, alive_only(sfx("r_load"))),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), view("r_field"))), *strikes))

    # ------------------------------------------------------------------ 画面
    # 幻刃的出手、锁链聚势、钩刃飞出、脚下的黑雾画在他自己的帧里（tools/art/import_loki.py）；诱饵留在他原来站的地方（不跟着走），
    # 幻影军势冒在目标身上，命中都在目标身上
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    views_e = [E("a_hit", "hook_hit"), E("q_hit", "hook_hit"), E("p_hit", "phantom_hit"), E("r_hit", "phantom_hit", 3),
               E("e_decoy", "decoy", 1, False), E("r_field", "phantom_field", 1)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/loki.rs）：配音、倒地声
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
