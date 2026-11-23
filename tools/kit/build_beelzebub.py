"""别西卜（终末包第十五个英雄 ragnarok_beelzebub，中路，Magician）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_beelzebub.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第八回合的神方代表：苍蝇之王，研究「振动」的天才，手里是骸骨杖阿波弥俄斯。美术、图标、音频是 Codex 的
（assets/source/beelzebub/，交接说明 assets/source/beelzebub/HANDOFF.md），技能照 Codex 的四个动作做。位置是中路法师（用户
2026-11-23 定的：「中路法师」）：包里第一个打魔法伤害的，技能全按法术强度（ApAttack 的 attack_ratio 是法强的百分比）。
  被动    振动：他的技能打中的敌人跟着振动，p_t 拍里魔抗 -p_mr%（magic_resistance_mult）。写在普攻说明里（游戏只有三个技能图标位），
          全在数据里。
  attack  振动掌 `Enemy`（塔也打）：100% 攻击力物理伤害，再加 a_dmg + a_ap% 法强的魔法伤害，atk_st 拍（第 5 帧，0.287 秒）打到。
  skill   暴食的堕天使：`Targeting` EnemyWithoutTower（q_range）：q_load 拍杖头蓄能，q_go 拍（0.237 秒）放出振动波：朝目标一条
          （长 q_len、半宽 q_w，吕布天喰的做法）上的敌人 q_dmg + q_ap% 法强魔法伤害、减速 q_slow% q_slow_t 拍，振动（被动）。
  skill2  地狱之门：`Targeting` EnemyWithoutTower（e_range，有人在身边）：e_go 拍（0.217 秒）展开振动屏障：护盾 e_sh + e_sh_ap% 法强，
          e_t 拍；e_cc 拍不受控制。e_hit 拍（0.354 秒）屏障震开：身边 e_r 里的敌人 e_dmg + e_ap% 法强魔法伤害、减速 e_slow%
          e_slow_t 拍，振动。中间被打死就不震。
  ult     虚神〈混沌〉：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到爆发为止）；r_go 拍（0.305 秒）黑核
          压缩，把身边 r_pull_r 里的敌人往他这边拉（Pull，每拍 r_pull_speed、r_pull_t 拍）；r_hit 拍（0.510 秒）爆发：身边 r_r
          里的敌人 r_dmg + r_ap% 法强魔法伤害、眩晕 r_stun 拍，振动。爆发前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.236 秒出掌、0.287 秒打到，振动波 0.176 秒蓄能、0.237 秒放出，地狱之门
0.217 秒展开、0.354 秒格挡涟漪，混沌 0.305 秒黑核、0.510 秒爆发；动作长度普攻 36 拍、振动波 35 拍、地狱之门 43 拍、混沌 56 拍。

ragnarok.dll（addons/ragnarok/src/beelzebub.rs）：配音和倒地声（被动 ragnarok_beelzebub:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_beelzebub"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 属性照联盟的近战法师（黛安娜、艾克、塞拉斯：生命 950 上下、法强 50、每级 +20）。
# 数值：经典 SDK 模拟（C:/t/lb_sim，中路 lane 2，600 秒，对手是原版中单），2026-11-23。联盟中单中位数约 +2.5，湿婆 +2.25。
# 初稿 +0.65（输出 9800 对面法师 12900）；四段伤害都提（振动波 85 + 90%、震开 70 + 60%、混沌 220 + 110%、普攻 20 + 30%）
# +2.18；再把振动波的冷却缩到 6 秒（这份）+2.42 / +2.50（平均 +2.46，K/D/A 3.4 / 1.5 / 4.6）；再加法强 +3.01，太强。
P = {
    # 属性（近战法师）
    "hp": 980, "hp_g": 95, "atk": 70, "atk_g": 8, "apw": 55, "apw_g": 20, "def": 28, "def_g": 5, "mr": 26,
    "mr_g": 4, "ms": 1060, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 36, "atk_cd": 66, "atk_st": 17, "a_dmg": 20, "a_ap": 30,
    # 被动：振动
    "p_mr": 20, "p_t": 240,
    # 暴食的堕天使
    "q_cd": 360, "q_range": 50000, "q_dur": 35, "q_load": 11, "q_go": 14, "q_len": 62000, "q_w": 10000,
    "q_ripple": 17, "q_dmg": 85, "q_ap": 90, "q_slow": 30, "q_slow_t": 60,
    # 地狱之门
    "e_cd": 720, "e_range": 30000, "e_dur": 43, "e_go": 13, "e_hit": 21, "e_t": 150, "e_sh": 80, "e_sh_ap": 60,
    "e_cc": 60, "e_fade": 30, "e_r": 36000, "e_dmg": 70, "e_ap": 60, "e_slow": 30, "e_slow_t": 60,
    # 虚神〈混沌〉
    "r_cd": 3000, "r_range": 35000, "r_dur": 56, "r_go": 18, "r_hit": 31, "r_dr": 30, "r_pull_r": 50000,
    "r_pull_speed": 1500, "r_pull_t": 10, "r_r": 36000, "r_dmg": 220, "r_ap": 110, "r_stun": 50,
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
    """Delayed 里的效果只给活着的别西卜（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def around(radius, effects):
    """他身边一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


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
    # ------------------------------------------------------------------ 被动：振动（技能打中降魔抗）
    shake = debuff("shake", p["p_t"], magic_resistance_mult=-p["p_mr"])

    # ------------------------------------------------------------------ 普攻：振动掌
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), magic(p["a_dmg"], p["a_ap"]), sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：暴食的堕天使
    wave = line("q_wave", p["q_len"], p["q_w"], [magic(p["q_dmg"], p["q_ap"]),
                                                 debuff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), shake,
                                                 view("q_hit"), tsfx("q_hit")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_load"] - 1, sfx("q_load")), delayed(p["q_go"] - 1, alive_only(sfx("q"), wave)),
                           delayed(p["q_ripple"] - 1, alive_only(sfx("q_ripple")))))

    # ------------------------------------------------------------------ E：地狱之门
    shield = {"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_sh_ap"], "tick": p["e_t"]}
    burst = around(p["e_r"], [magic(p["e_dmg"], p["e_ap"]), debuff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                              shake, view("e_hit"), tsfx("e_hit")])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_go"] - 1, alive_only(sfx("e"), search_self(shield),
                                                              flag("e_guard", p["e_cc"], cc_immune=True))),
                            delayed(p["e_hit"] - 1, alive_only(sfx("e_block"), burst)),
                            delayed(p["e_fade"] - 1, alive_only(sfx("e_fade")))))

    # ------------------------------------------------------------------ R：虚神〈混沌〉
    pull = around(p["r_pull_r"], [{"type": "Pull", "speed": p["r_pull_speed"], "tick": p["r_pull_t"]}])
    chaos = around(p["r_r"], [magic(p["r_dmg"], p["r_ap"]), {"type": "Stun", "duration": p["r_stun"]}, shake,
                              view("r_hit"), tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_go"] - 1, alive_only(sfx("r_load"), pull)),
                         delayed(p["r_hit"] - 1, alive_only(sfx("r"), chaos))))

    # ------------------------------------------------------------------ 画面
    # 掌风、振动波、波纹、屏障、格挡涟漪、混沌的黑核和爆发画在他自己的帧里（tools/art/import_beelzebub.py）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "palm_hit"), E("q_hit", "palm_hit"), E("e_hit", "palm_hit"), E("r_hit", "palm_hit", 3)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Melee", "Shield", "CC"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/beelzebub.rs）：配音、倒地声
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
