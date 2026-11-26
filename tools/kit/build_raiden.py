"""雷电为右卫门（终末包第九个英雄 ragnarok_raiden，辅助，Tank）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_raiden.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第五回合的人类方选手，和湿婆打的那个：史上最强的力士，肌肉强到撕裂自己的身体，一辈子都在压着力气相扑，
直到瓦尔基里的神器（肌肉拘束）让他能控制全身的肌肉。美术、图标、音频是 Codex 的（assets/source/raiden/，交接说明
assets/source/raiden/HANDOFF.md），技能照 Codex 的四个动作和肌肉解放的过渡做：
  被动    百闭解放：每条命第一次放八咫乌之前，先扭开胸肌破开「百闭」（小时候长出来压住肌肉、免得撑断骨头的那层肌肉壳），把压了一辈子的肌肉放开（muscle_release，rel_dur 拍，不受控制、受到的
          伤害降低 rel_dr%），之后这条命一直是放开的：攻击力 +p_atk%、护甲和魔抗 +p_res、攻速 +p_as%；以后的八咫乌直接出。
          写在普攻说明里（游戏只有三个技能图标位），全在数据里。
  attack  一掌打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.314 秒）打到。
  skill   连掌（张手）：`Targeting` EnemyWithoutTower（q_range）：q_hit1 拍（第 4 帧）第一掌 q1_dmg + q1_ad% 攻击力物理伤害，
          q_hit2 拍（第 6 帧）第二掌 q2_dmg + q2_ad%，打得人一个踉跄（眩晕 q_stun 拍）、减速 q_slow% q_slow_t 拍。
          不推开：辅助把人推走，队友就够不着了（初稿推开，模拟里比联盟辅助差得多）。
  skill2  狮子舞（2026-11-26 照原作改：「四股」在原作不是招式名。原作第五回合：双手撑地倒立，整个人往前倒，用两只脚掌跺下去）：
          `Targeting` EnemyWithoutTower（e_range，有人在身边）。Codex 补画的动作（assets/source/raiden/fidelity，0.75 秒）：
          e_plant 拍（第 2 帧）双手撑地，e_flip 拍（第 5 帧）往前倒（RushTime，e_step 速度 e_step_t 拍，碰到就停），e_land 拍
          （第 6 帧）双脚跺下：身前 e_off 处 e_r 里的敌人 e_dmg + e_ad% 物理伤害、眩晕 e_stun 拍；e_pulse 拍余震，更大一圈 e_r2
          里的敌人减速 e_slow% e_slow_t 拍。
  ult     八咫乌：`Targeting` 敌方英雄（r_range）：r_go 拍（第 3 帧）蓄劲，到出掌前不受控制、受到的伤害降低 r_dr%；r_hit 拍
          （第 5 帧）一掌推出，前方扇形（半径 r_r，左右各 acos(r_cone/1000)）里的敌人 r_dmg + r_ad% 物理伤害，被冲击波震飞
          在原地（击飞 r_up 拍，不推远，队友跟得上）。这条命第一次放时先播肌肉解放（见被动）。出掌前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.314 秒打到，连掌 0.269 / 0.371 秒，四股 0.229 秒抬脚、0.398 秒落地、
0.464 秒余震，八咫乌 0.282 秒蓄劲、0.474 秒出掌，肌肉解放 0.391 秒发动；动作长度普攻 40 拍、连掌 38 拍、四股 47 拍、
八咫乌 51 拍、肌肉解放 55 拍。

ragnarok.dll（addons/ragnarok/src/raiden.rs）：配音和倒地声（被动 ragnarok_raiden:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_raiden"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，辅助 lane 4，600 秒，对手是五个原版辅助），2026-11-22。联盟辅助对照（诺提勒斯 +2.99、
# 洛 +1.21、锤石 +0.58、布隆 -0.07、蕾欧娜 -0.29、阿利斯塔 -0.60，中位数约 +0.25）。初稿 -3.00：连掌和八咫乌把人推远，队友
# 够不着；改成踉跄和原地震飞 -1.12，加技能伤害 -0.29 / -0.92（两批种子），伤害再加也不更好（-0.82），更耐打 +0.25、够得更远
# +0.22，控制更长（这份：连掌踉跄 0.67 秒、四股眩晕 1 秒）+0.42（16 个种子，K/D/A 1.3 / 1.8 / 4.1）。
# 2026-11-26 照原作改了以后：初版 +1.03 偏强；E 眩晕缩到 40 拍、伤害 55 + 55%（这份 P）
# +0.48，改之前 +0.42。
P = {
    # 属性（辅助坦克）：力士，最耐打
    "hp": 1300, "hp_g": 120, "atk": 72, "atk_g": 11, "apw": 0, "apw_g": 0, "def": 50, "def_g": 9, "mr": 40,
    "mr_g": 5, "ms": 1000, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 40, "atk_cd": 70, "atk_st": 19,
    # 被动：肌肉解放（数据）
    "rel_dur": 55, "rel_go": 23, "rel_dr": 50, "p_atk": 20, "p_res": 20, "p_as": 20,
    # 连掌
    "q_cd": 480, "q_range": 28000, "q_dur": 38, "q_hit1": 16, "q_hit2": 22,
    "q1_dmg": 55, "q1_ad": 80, "q2_dmg": 80, "q2_ad": 105, "q_stun": 40, "q_slow": 30, "q_slow_t": 60,
    # 四股
    "e_cd": 780, "e_range": 24000, "e_dur": 45, "e_plant": 7, "e_flip": 22, "e_step": 4000, "e_step_t": 4, "e_land": 26,
    "e_pulse": 30, "e_off": 6000, "e_r": 34000, "e_r2": 44000, "e_dmg": 55, "e_ad": 55, "e_stun": 40, "e_slow": 30,
    "e_slow_t": 90,
    # 八咫乌
    "r_cd": 3000, "r_range": 45000, "r_dur": 51, "r_go": 17, "r_hit": 28, "r_dr": 40, "r_r": 48000, "r_cone": 700,
    "r_speed": 8000, "r_t": 4,
    "r_dmg": 200, "r_ad": 160, "r_up": 45,
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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def slow(name, pct, tick):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}},
                                              "move_speed_mult": -pct}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的雷电（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def ahead(radius, offset, effects):
    """他身前 offset 处一圈（半径 radius）里的敌人（朝动作的目标）。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": offset}}, "effects": [e for e in effects if e is not None]}


def around(radius, effects):
    """他身边一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 普攻：一掌
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：连掌
    first = combine(sfx("q1"), attack(p["q1_dmg"], p["q1_ad"]), view("a_hit"), tsfx("q_hit"))
    second = combine(sfx("q2"), attack(p["q2_dmg"], p["q2_ad"]), {"type": "Stun", "duration": p["q_stun"]},
                     slow("q_slow", p["q_slow"], p["q_slow_t"]), view("a_hit"), tsfx("q_hit2"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_hit1"] - 1, first), delayed(p["q_hit2"] - 1, alive_only(second))))

    # ------------------------------------------------------------------ E：狮子舞（倒立、往前倒、双脚跺下）
    flip = {"type": "RushTime", "speed": p["e_step"], "tick": p["e_step_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": []}
    land = ahead(p["e_r"], p["e_off"], [attack(p["e_dmg"], p["e_ad"]), {"type": "Stun", "duration": p["e_stun"]}])
    pulse = ahead(p["e_r2"], p["e_off"], [slow("e_slow", p["e_slow"], p["e_slow_t"])])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_plant"] - 1, sfx("e_lift")),
                            delayed(p["e_flip"] - 1, alive_only(flip)),
                            delayed(p["e_land"] - 1, alive_only(sfx("e"), land)),
                            delayed(p["e_pulse"] - 1, alive_only(sfx("e2"), pulse))))

    # ------------------------------------------------------------------ R：八咫乌（这条命第一次先放开肌肉）
    strike = cone(p["r_r"], p["r_cone"], [attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]},
                                         view("r_hit")])
    released = flag("released", None, attack_mult=p["p_atk"], defence=p["p_res"], magic_resistance=p["p_res"],
                    attack_speed_mult=p["p_as"])

    # 原作（第五回合）：八咫乌是铁炮掌的极致——肌肉先挪到腿上一下贴近，再挪到出掌的手上。蓄劲那一拍朝目标冲过去（碰到就停）
    close_in = {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_t"], "range": 15000,
                "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": []}

    def yatagarasu(go):
        """go 拍以后出八咫乌：蓄劲到出掌不受控制、减伤，蓄劲时一下贴近，出掌那一刻震飞前方扇形。"""
        return combine(delayed(go, flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"])) if go
                       else flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                       delayed(go + p["r_go"] - 1, alive_only(sfx("r1"), close_in)),
                       delayed(go + p["r_hit"] - 1, alive_only(sfx("r2"), strike, tsfx("r_hit"))))

    release_first = combine(anim("muscle_release", p["rel_dur"]),
                            flag("rel_guard", p["rel_dur"] + 1, cc_immune=True, damaged_reduce=p["rel_dr"]),
                            delayed(p["rel_go"] - 1, alive_only(sfx("rel"), released)),
                            delayed(p["rel_dur"] - 1, alive_only(anim("ult", p["r_dur"]))),
                            yatagarasu(p["rel_dur"]))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 when("released", yatagarasu(0), release_first))

    # ------------------------------------------------------------------ 画面
    # 掌风、四股的尘土和震环、八咫乌的气和冲击波、肌肉解放的红纹画在他自己的帧里（tools/art/import_raiden.py）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "palm_contact"), E("r_hit", "yatagarasu_impact")]
    kit = {
        # 经典 SDK（平衡模拟）没有 Tank 这个分类：--plain 写 Melee（宙斯、赫拉克勒斯的做法）
        "id": ID, "category": "Tank" if is_native else "Melee", "tags": ["AD", "Melee", "Tank", "CC"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/raiden.rs）：配音、倒地声
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
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的配音被动，分类写 Melee")
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
