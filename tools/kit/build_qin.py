"""秦始皇（终末包第十四个英雄 ragnarok_qin，辅助，Tank）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_qin.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第七回合的人类方代表：中国第一个皇帝。天生的镜触共感，别人的痛他都感同身受，所以戴着眼罩；看得见对手身上的「星」
（气的破绽）。始皇的武术是接住对方的力再还回去（神罗铠袖、承力天凤），最后拔出始皇勾践剑。美术、图标、音频是 Codex 的
（assets/source/qin/，交接说明 assets/source/qin/HANDOFF.md），技能照 Codex 的四个动作做。位置是辅助（用户 2026-11-22 定的：
「辅助」，问过理由以后）：护住身边的人、用控制开团，伤害压低（雷电那次的经验：辅助把人推远，队友就够不着，所以这里都是原地的
眩晕和击飞）。
  被动    星：他的技能打中的敌人露出「星」：p_t 拍里受到的伤害 +p_amp%（所有人打都算）。写在普攻说明里（游戏只有三个技能图标位），
          全在数据里。
  attack  指爪 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.287 秒）抓到。
  skill   蚩尤弩式·波流龟：`Targeting` EnemyWithoutTower（q_range）：q_load 拍吸一口气，q_go 拍（0.237 秒）吐出气弹（TargetProjectile，
          速度 q_speed，追着目标飞）：打到时炸开，目标 q_dmg + q_ad% 攻击力物理伤害、眩晕 q_stun 拍，露出星。
  skill2  神罗铠袖·承力天凤：`Targeting` EnemyWithoutTower（e_range，有人在身边）：e_go 拍（第 4 帧，0.217 秒）举起神罗铠袖：
          e_t 拍里受到的伤害降低 e_dr%、不受控制，身边 e_ar 里的友方英雄（连他自己）得到护盾 e_sh + e_sh_ad% 攻击力，e_sh_t 拍；
          e_block 拍承力，e_hit 拍（第 6 帧，0.354 秒）把力推回去：前方扇形（半径 e_r，左右各 acos(e_cone/1000)）里的敌人
          e_dmg + e_ad% 攻击力物理伤害、眩晕 e_stun 拍，露出星。中间被打死就不推。
  ult     始皇承力燕斩（始皇勾践剑）：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到斩中为止），r_go 拍（0.305 秒）
          剑显形，r_cut 拍（0.510 秒）斩出，r_hit 拍（0.580 秒）斩中：前方大扇形（半径 r_r，左右各 acos(r_cone/1000)）里的敌人
          r_dmg + r_ad% 攻击力物理伤害、被击飞 r_up 拍（原地），露出星。斩出前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.236 秒出爪、0.287 秒抓到，气弹 0.176 秒吸气、0.237 秒吐出，
神罗铠袖 0.217 秒举袖、0.292 秒承力、0.354 秒推回，勾践剑 0.305 / 0.510 / 0.580 秒；动作长度普攻 36 拍、气弹 35 拍、
神罗铠袖 43 拍、勾践剑 56 拍。

ragnarok.dll（addons/ragnarok/src/qin.rs）：配音和倒地声（被动 ragnarok_qin:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_qin"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
PROJ = f"asset/{MOD_ID}/effects/{ID}_proj"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，辅助 lane 4，600 秒，对手是五个原版辅助），2026-11-22。联盟辅助对照（诺提勒斯 +2.99、
# 洛 +1.21、锤石 +0.58、布隆 -0.07、蕾欧娜 -0.29、阿利斯塔 -0.60，中位数约 +0.25），雷电 +0.42。初稿 +1.04（气弹眩晕 0.83 秒、
# 推回眩晕 0.75 秒）；伤害降两成没变（+1.16：强在控制，不在伤害），眩晕缩到 0.67 / 0.5 秒掉到 +0.05，星的增伤减到 6% +0.83；
# 定下来的这份眩晕取中间（气弹 0.75 秒、推回 0.67 秒）：+0.57 / +0.81（平均 +0.69，K/D/A 1.0 / 1.7 / 4.9），星 8% 也一样（+0.58）。
# 气弹的高度：Codex 的锚点在脚底上 89 格 = 32.4 个游戏像素（PPU 2.75），弹道画面在落点（脚底上 11.5）往北 5000 - y_offset 处：
# y_offset = 5000 - (32.4 - 11.5) x 1000 = -15900
P = {
    # 属性（辅助坦克）
    "hp": 1200, "hp_g": 115, "atk": 74, "atk_g": 11, "apw": 0, "apw_g": 0, "def": 46, "def_g": 8, "mr": 36,
    "mr_g": 5, "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 36, "atk_cd": 66, "atk_st": 17,
    # 被动：星
    "p_amp": 10, "p_t": 180,
    # 波流龟气弹
    "q_cd": 540, "q_range": 50000, "q_dur": 35, "q_load": 11, "q_go": 14, "q_speed": 3800, "q_y": -15900,
    "q_dmg": 60, "q_ad": 60, "q_stun": 24, "q_weak": 25, "q_weak_t": 180,
    # 神罗铠袖·承力天凤
    "e_cd": 720, "e_range": 30000, "e_dur": 43, "e_go": 13, "e_block": 18, "e_hit": 21, "e_t": 60, "e_dr": 40,
    "e_ar": 40000, "e_sh": 80, "e_sh_ad": 50, "e_sh_t": 150, "e_r": 40000, "e_cone": 600, "e_dmg": 60, "e_ad": 60,
    "e_stun": 40,
    # 始皇勾践剑
    "r_cd": 3000, "r_range": 36000, "r_dur": 56, "r_go": 18, "r_cut": 31, "r_hit": 35, "r_dr": 40, "r_r": 56000,
    "r_cone": 500, "r_dmg": 180, "r_ad": 120, "r_up": 50, "r_store": 100, "r_cap": 25,
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


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的秦始皇（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def allies(radius, effects):
    """他身边一圈（半径 radius）里的友方英雄，连他自己。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "AllyChampion",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：星（技能打中的敌人受到的伤害加深）
    star = debuff("star", p["p_t"], damaged_amplify=p["p_amp"])

    # ------------------------------------------------------------------ 普攻：指爪
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：蚩尤弩式·波流龟（对着「星」吹一口看不见的气：打断一下、
    # 削弱对方的招，原作第七回合用它削弱、偏转哈迪斯的招式）
    bubble = {"type": "TargetProjectile", "name": n("q_bubble"), "speed": p["q_speed"], "y_offset": p["q_y"],
              "applied_target": "Enemy",
              "applied_effects": [{"casting_type": "Targeting", "effect": combine(
                  attack(p["q_dmg"], p["q_ad"]), {"type": "Stun", "duration": p["q_stun"]},
                  debuff("q_weak", p["q_weak_t"], attack_mult=-p["q_weak"], magic_power_mult=-p["q_weak"]), star, view("q_hit"),
                  tsfx("q_hit"))}]}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_load"] - 1, sfx("q_load")), delayed(p["q_go"] - 1, alive_only(sfx("q"), bubble))))

    # ------------------------------------------------------------------ E：神罗铠袖·承力天凤
    shield = {"type": "Shield", "amount": p["e_sh"], "attack_ratio": p["e_sh_ad"], "ap_ratio": 0, "tick": p["e_sh_t"]}
    guard = combine(sfx("e"), flag("e_guard", p["e_t"], cc_immune=True, damaged_reduce=p["e_dr"]),
                    allies(p["e_ar"], [shield]))
    push = cone(p["e_r"], p["e_cone"], [attack(p["e_dmg"], p["e_ad"]), {"type": "Stun", "duration": p["e_stun"]}, star,
                                       view("e_hit"), tsfx("e_hit")])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_go"] - 1, alive_only(guard)),
                            delayed(p["e_block"] - 1, alive_only(sfx("e_block"))),
                            delayed(p["e_hit"] - 1, alive_only(sfx("e_push"), push))))

    # ------------------------------------------------------------------ R：始皇承力燕斩（始皇勾践剑；把挨的打存进剑里再还回去：
    # ragnarok.dll 的 qin.rs）
    slash = cone(p["r_r"], p["r_cone"], [attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]}, star,
                                        view("r_hit"), tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_go"] - 1, alive_only(sfx("r_show"))),
                         delayed(p["r_cut"] - 1, alive_only(sfx("r"))),
                         delayed(p["r_hit"] - 1, alive_only(slash))))

    # ------------------------------------------------------------------ 画面
    # 爪痕、神罗铠袖的护势、天凤回推、勾践剑的剑光和剑痕画在他自己的帧里（tools/art/import_qin.py）；气弹是弹道画面
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    Pj = lambda name, tag: {"type": "Animated", "name": n(name), "anim": PROJ, "tag": tag, "repeat": True, "z": 1}
    views_e = [E("a_hit", "claw_impact"), E("q_hit", "star_pop", 3), E("e_hit", "claw_impact"),
               E("r_hit", "claw_impact", 3)]
    kit = {
        # Tank 是游戏 0.7.3 才有的定位，经典 SDK 的模拟不认：--plain 写成 Melee（雷电、赫拉克勒斯一样）
        "id": ID, "category": "Tank" if is_native else "Melee", "tags": ["AD", "Melee", "Tank", "Shield", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [Pj("q_bubble", "air_bubble")], "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll（addons/ragnarok/src/qin.rs）：配音、倒地声
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:voice", "params": {"r_hit": p["r_hit"], "r_store": p["r_store"],
                                                                        "r_cap": p["r_cap"]}},
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
