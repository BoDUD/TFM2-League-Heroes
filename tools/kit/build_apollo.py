"""阿波罗（终末包第十八个英雄 ragnarok_apollo，中路刺客）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_apollo.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第九回合的神方代表：太阳神，「最美的神」，和列奥尼达斯打的那个。拳甲打近身，用双胞胎妹妹阿尔忒弥斯的丝缠人、
拉成光弓放箭，最后让阿尔忒弥斯的女神像拉开光索，把自己当成一支银箭射出去。美术、图标、音频是 Codex 的
（assets/source/apollo/，交接说明 assets/source/apollo/HANDOFF.md），技能照 Codex 的四个动作做。位置是中路（用户
2026-11-23：「位置你看着定就行 选最合适的位置」）：普攻是拳（近战），下路要的是远程普攻；光丝定身、光箭远程消耗、
银箭突进进场爆发，是中路刺客的打法（中路只有波塞冬、湿婆、别西卜三个）。伤害是物理（拳和箭）。
  被动    日轮：每放一个技能，p_t 拍里下一次日轮拳多打 p_dmg + p_ad% 攻击力物理伤害。写在普攻说明里（游戏只有三个技能
          图标位），全在数据里。
  attack  日轮拳 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.287 秒）打到；身上有日轮时多打一下（被动）。
  skill   阿尔忒弥斯之丝：`Targeting` EnemyWithoutTower（q_range）：q_charge 拍光丝汇聚，q_go 拍（第 4 帧，0.237 秒）投出，
          q_hit 拍（0.285 秒）缠住：q_dmg + q_ad% 攻击力物理伤害、定身 q_bind 拍；q_fade 拍光丝松开。
  skill2  光之矢：`Targeting` EnemyWithoutTower（e_range）：e_form 拍（第 3 帧，0.217 秒）光弓成形，e_draw 拍拉弦，e_go 拍
          （第 5 帧，0.354 秒）放箭（TargetProjectile，速度 e_speed，追着目标飞）：打到 e_dmg + e_ad% 攻击力物理伤害。
  ult     银箭突进：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到撞上为止），r_show 拍（第 3 帧，
          0.305 秒）女神像显现，r_load 拍光索蓄力，r_go 拍（第 5 帧，0.510 秒）把自己射出去（RushTime，每拍 r_speed、r_t 拍，
          碰到人就停）：撞上的敌人 r_dmg + r_ad% 攻击力物理伤害、眩晕 r_stun 拍。射出去之前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：日轮拳 0.236 秒出拳、0.287 秒打到，光丝 0.176 / 0.237 / 0.285 / 0.391 秒，
光之矢 0.217 / 0.292 / 0.354 秒，银箭突进 0.305 / 0.423 / 0.510 / 0.580 秒；动作长度日轮拳 36 拍、光丝 35 拍、光之矢 43 拍、
银箭突进 56 拍。

和列奥尼达斯：举盾时打他的人挨反伤（build_leonidas 的 e_ref，引擎的反伤每一下都算），光箭射在举着的盾上也一样被弹回来一部分；
真把弹道掉头射回去引擎做不到（没有能让弹道转向的效果），列奥尼达斯举盾的动作里画着光箭从盾上弹开。

ragnarok.dll（addons/ragnarok/src/apollo.rs）：配音和倒地声（被动 ragnarok_apollo:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_apollo"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
PROJ = f"asset/{MOD_ID}/effects/{ID}_proj"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，中路 lane 2，600 秒，对手是五个原版中单），2026-11-23。中路对照：中位数约 +2.5，湿婆 +2.25、
# 别西卜 +2.46。初稿 +0.89（输出 9200，对面中单 12700）；四段伤害都提（光丝 60 + 70% -> 80 + 90%、光箭 90 + 110% -> 110 + 140%、
# 银箭 200 + 160% -> 260 + 200%、日轮 30 + 40% -> 40 + 50%）：+2.59 / +2.43（这份，平均 +2.51，K/D/A 3.5 / 1.8 / 4.6）；再缩光丝、光箭的冷却 +2.95，太强。
# 光箭的高度：Codex 的离弦点在脚底上 82 格 = 29.8 个游戏像素（PPU 2.75），弹道画面在落点（脚底上 11.5）往北 5000 - y_offset 处：
# y_offset = 5000 - (29.8 - 11.5) x 1000 = -13300
P = {
    # 属性（中路刺客）
    "hp": 1000, "hp_g": 95, "atk": 100, "atk_g": 17, "apw": 0, "apw_g": 0, "def": 30, "def_g": 5, "mr": 30,
    "mr_g": 4, "ms": 1090, "ms_g": 11,
    "atk_range": 26000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
    # 被动：日轮
    "p_dmg": 40, "p_ad": 50, "p_t": 240,
    # 阿尔忒弥斯之丝
    "q_cd": 480, "q_range": 45000, "q_dur": 35, "q_charge": 11, "q_go": 14, "q_hit": 17, "q_fade": 23,
    "q_dmg": 80, "q_ad": 90, "q_bind": 60,
    # 光之矢
    "e_cd": 420, "e_range": 60000, "e_dur": 43, "e_form": 13, "e_draw": 18, "e_go": 21, "e_speed": 6000, "e_y": -13300,
    "e_dmg": 110, "e_ad": 140,
    # 银箭突进
    "r_cd": 3000, "r_range": 60000, "r_dur": 56, "r_show": 18, "r_load": 25, "r_go": 31, "r_dr": 30, "r_speed": 10000,
    "r_t": 8, "r_dmg": 260, "r_ad": 200, "r_stun": 30,
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
    """Delayed 里的效果只给活着的阿波罗（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：日轮（放技能以后下一拳多打一下）
    sun = flag("sun", p["p_t"])

    # ------------------------------------------------------------------ 普攻：日轮拳
    extra = combine(attack(p["p_dmg"], p["p_ad"]), unflag("sun"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), when("sun", extra, combine()), sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：阿尔忒弥斯之丝（缠住、定身）
    bound = combine(attack(p["q_dmg"], p["q_ad"]), {"type": "Bind", "duration": p["q_bind"]}, view("q_bind"),
                    tsfx("q_hit"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sun, delayed(p["q_charge"] - 1, sfx("q_charge")),
                           delayed(p["q_go"] - 1, alive_only(sfx("q"))),
                           delayed(p["q_hit"] - 1, alive_only(bound)),
                           delayed(p["q_fade"] - 1, alive_only(sfx("q_fade")))))

    # ------------------------------------------------------------------ E：光之矢（光弓放箭，追着目标飞）
    arrow = {"type": "TargetProjectile", "name": n("e_arrow"), "speed": p["e_speed"], "y_offset": p["e_y"],
             "applied_target": "Enemy",
             "applied_effects": [{"casting_type": "Targeting", "effect": combine(
                 attack(p["e_dmg"], p["e_ad"]), view("a_hit"), tsfx("e_hit"))}]}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sun, delayed(p["e_form"] - 1, sfx("e_form")),
                            delayed(p["e_draw"] - 1, alive_only(sfx("e_draw"))),
                            delayed(p["e_go"] - 1, alive_only(sfx("e"), arrow))))

    # ------------------------------------------------------------------ R：银箭突进（女神像拉开光索，把自己射出去）
    struck = [{"casting_type": "Targeting", "effect": e} for e in
              (attack(p["r_dmg"], p["r_ad"]), {"type": "Stun", "duration": p["r_stun"]}, view("a_hit"), tsfx("r_hit"))]
    dash = {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": struck}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sun, flag("r_guard", p["r_go"] + p["r_t"], cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_show"] - 1, alive_only(sfx("r_show"))),
                         delayed(p["r_load"] - 1, alive_only(sfx("r_load"))),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), dash))))

    # ------------------------------------------------------------------ 画面
    # 拳光、光丝投出、光弓成形和离弦的光、女神像显现的光、银箭的箭影画在他自己的帧里（tools/art/import_apollo.py）；
    # 光箭是弹道画面（1 倍，跟着飞的方向转）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    Pj = lambda name, tag: {"type": "Animated", "name": n(name), "anim": PROJ, "tag": tag, "repeat": True, "z": 1}
    views_e = [E("a_hit", "punch_hit"), E("q_bind", "thread_bind", 3)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [Pj("e_arrow", "light_arrow")], "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll（addons/ragnarok/src/apollo.rs）：配音、倒地声
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
