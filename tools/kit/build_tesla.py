"""尼古拉·特斯拉（终末包第十六个英雄 ragnarok_tesla，打野，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_tesla.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第八回合的人类方代表：天才发明家，穿着自己造的超人自动机兵 β 用双拳打。美术、图标、音频是 Codex 的
（assets/source/tesla/，交接说明 assets/source/tesla/HANDOFF.md），技能照 Codex 的四个动作做。位置是打野（用户 2026-11-23 定的）。
伤害是物理的（按攻击力），只有被动的等离子按他自己的法强（基础 apw、每级 +apw_g，ApAttack 的 attack_ratio 是法强的百分比）。
  被动    等离子脉冲：每一拳额外 p_dmg + p_ap% 法强的魔法伤害。写在普攻说明里（游戏只有三个技能图标位），全在数据里。
  attack  等离子脉冲拳 `Enemy`（塔也打）：100% 攻击力物理伤害，atk_st 拍（第 5 帧，0.287 秒）打到。
  skill   特斯拉步：`Targeting` EnemyWithoutTower（q_range）：q_lift 拍反重力启动、q_slide 拍起跳，q_go 拍（0.237 秒）离场（原地留下
          离场的闪光）：
          - 平时朝目标冲过去（RushTime，每拍 q_speed、q_t 拍，碰到就停）：碰到的敌人 q_dmg + q_ad% 攻击力物理伤害、减速
            q_slow% q_slow_t 拍；
          - 神之监狱还在的时候（他身上的 prison，e_t 拍）直接瞬移到目标身上（Teleport）：q2_dmg + q2_ad% 物理伤害、眩晕 q2_stun 拍。
  skill2  神之监狱：`Targeting` EnemyWithoutTower（e_range）：e_charge 拍蓄能，e_go 拍（0.292 秒）牢笼落在目标那里（RangeProjectile，
          半径 e_r）：里面的敌人 e_dmg + e_ad% 攻击力物理伤害、减速 e_slow% e_t 拍，身上套着牢笼（先展开 e_deploy_t 拍，再每
          e_loop_t 拍接着放一次循环，放到 e_t 拍为止（只放装得下的整圈）：都是跟着人的特效画面，走高清，不用 buff 的画面——那个游戏只画 1 倍，用户：
          「这个弄高清点」）；特斯拉身上挂 prison e_t 拍，这段时间特斯拉步变成瞬移。
  ult     双向电光拳：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到第二拳为止）；r_charge 拍双线圈充能，
          r_hit1 拍（0.423 秒）第一拳：前方扇形（半径 r1_r，左右各 acos(r1_cone/1000)）里的敌人 r1_dmg + r1_ad% 物理伤害、眩晕 r1_stun
          拍；r_hit2 拍（0.510 秒）第二拳打出一道电光（LineRangeProjectile，长 r_len、半宽 r_w）：线上的敌人 r2_dmg + r2_ad%
          物理伤害、原地击飞 r_up 拍。第一拳前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.236 秒出拳、0.287 秒打到，特斯拉步 0.098 秒启动、0.176 秒起跳、0.237 秒
离场、0.285 秒到达，神之监狱 0.217 秒蓄能、0.292 秒展开，双拳 0.305 秒充能、0.423 / 0.510 秒出拳；动作长度普攻 36 拍、
特斯拉步 35 拍、神之监狱 43 拍、双拳 56 拍。

ragnarok.dll（addons/ragnarok/src/tesla.rs）：配音和倒地声（被动 ragnarok_tesla:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_tesla"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，打野 lane 1，600 秒，对手是五个原版打野），2026-11-23。打野对照：中位数约 +1.2，哈迪斯 +1.17、
# 释迦 +1.45、赫拉克勒斯 +1.52。初稿 -0.94（刷野慢：cs 44，哈迪斯 49）；技能伤害提两到三成 +0.38，再缩冷却 +0.23、加血加甲
# +0.49、射程 30000 +0.49、攻击 96 +0.45，都只差一点；几样叠在一起（攻击 96、射程 30000、血 1250、护甲 44）+1.04，
# 再加攻速（普攻间隔 62 -> 56 拍）：+1.24 / +1.02（平均 +1.13，K/D/A 2.3 / 1.3 / 3.8），定下来的就是这份。
P = {
    # 属性（打野战士，机甲）：一点法强给等离子用
    "hp": 1250, "hp_g": 108, "atk": 96, "atk_g": 15, "apw": 20, "apw_g": 8, "def": 44, "def_g": 7, "mr": 30,
    "mr_g": 4, "ms": 1050, "ms_g": 11,
    "atk_range": 30000, "atk_dur": 36, "atk_cd": 56, "atk_st": 17,
    # 被动：等离子脉冲
    "p_dmg": 20, "p_ap": 60,
    # 特斯拉步
    "q_cd": 480, "q_range": 42000, "q_dur": 35, "q_lift": 6, "q_slide": 11, "q_go": 14, "q_land": 20, "q_speed": 4500, "q_t": 8,
    "q_dmg": 80, "q_ad": 110, "q_slow": 30, "q_slow_t": 60, "q2_dmg": 90, "q2_ad": 120, "q2_stun": 30,
    # 神之监狱
    "e_cd": 780, "e_range": 40000, "e_dur": 43, "e_charge": 13, "e_go": 18, "e_r": 20000, "e_t": 180,
    "e_dmg": 80, "e_ad": 90, "e_slow": 35, "e_deploy_t": 18, "e_loop_t": 40,
    # 双向电光拳
    "r_cd": 2700, "r_range": 32000, "r_dur": 56, "r_charge": 18, "r_hit1": 25, "r_hit2": 31, "r_dr": 30,
    "r1_r": 38000, "r1_cone": 800, "r1_dmg": 120, "r1_ad": 100, "r1_stun": 30,
    "r_len": 56000, "r_w": 10000, "r2_dmg": 180, "r2_ad": 140, "r_up": 45,
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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
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
    """Delayed 里的效果只给活着的特斯拉（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def around(radius, effects):
    """他身边一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


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
    # ------------------------------------------------------------------ 被动：等离子脉冲（每拳一点魔法伤害）
    plasma = magic(p["p_dmg"], p["p_ap"])

    # ------------------------------------------------------------------ 普攻：等离子脉冲拳
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), plasma, sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：特斯拉步（神之监狱还在时变成瞬移）
    passed = [{"casting_type": "Targeting", "effect": e} for e in
              (attack(p["q_dmg"], p["q_ad"]), debuff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
               view("a_hit"), tsfx("q_hit"))]
    dash = {"type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": passed}
    warp = combine({"type": "Teleport"}, attack(p["q2_dmg"], p["q2_ad"]), {"type": "Stun", "duration": p["q2_stun"]},
                   view("a_hit"), tsfx("q_hit"), sfx("q_warp"))
    depart = {"type": "CasterViewEffect", "name": n("q_depart")}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_lift"] - 1, sfx("q_lift")), delayed(p["q_slide"] - 1, sfx("q_slide")),
                           delayed(p["q_go"] - 1, alive_only(sfx("q"), depart, when("prison", warp, dash))),
                           delayed(p["q_land"] - 1, alive_only(sfx("q_land")))))

    # ------------------------------------------------------------------ E：神之监狱
    # 牢笼的画面：展开一次（zone_deploy，约 0.3 秒），接着每 e_loop_t 拍（循环一圈 0.675 秒）在他身上再放一次 zone_idle，放满 e_t 拍
    loops = [delayed(t, view("e_cage")) for t in range(p["e_deploy_t"], p["e_t"] - p["e_loop_t"] + 1, p["e_loop_t"])]
    cage = {"type": "RangeProjectile", "name": n("e_zone"), "shape": {"Circle": {"radius": p["e_r"]}}, "delay": 2,
            "apply": 1, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in (
                attack(p["e_dmg"], p["e_ad"]), debuff("e_slow", p["e_t"], move_speed_mult=-p["e_slow"]),
                view("e_deploy"), tsfx("e_hit"), *loops)]}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_charge"] - 1, sfx("e_charge")),
                            delayed(p["e_go"] - 1, alive_only(sfx("e"), cage, flag("prison", p["e_t"])))))

    # ------------------------------------------------------------------ R：双向电光拳
    first = cone(p["r1_r"], p["r1_cone"], [attack(p["r1_dmg"], p["r1_ad"]), {"type": "Stun", "duration": p["r1_stun"]},
                                          view("a_hit"), tsfx("r_hit1")])
    bolt = line("r_bolt", p["r_len"], p["r_w"], [attack(p["r2_dmg"], p["r2_ad"]), {"type": "Airborne", "duration": p["r_up"]},
                                                 view("r_hit"), tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_hit2"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_charge"] - 1, alive_only(sfx("r_load"))),
                         delayed(p["r_hit1"] - 1, alive_only(sfx("r1"), first)),
                         delayed(p["r_hit2"] - 1, alive_only(sfx("r2"), bolt))))

    # ------------------------------------------------------------------ 画面
    # 拳风、特斯拉步的拖痕和到达的闪光画在他自己的帧里（tools/art/import_tesla.py）；离场的闪光留在原地（不跟着走）；
    # 牢笼是被关的人身上一个接一个的特效画面（跟着人、不转方向、走高清）：展开 e_deploy，循环 e_cage
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    views_e = [E("a_hit", "punch_hit"), E("r_hit", "twin_impact", 3), E("q_depart", "warp_depart", 2, False),
               E("e_deploy", "zone_deploy", 3), E("e_cage", "zone_idle", 3)]
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/tesla.rs）：配音、倒地声
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
