"""哈迪斯（终末包第十三个英雄 ragnarok_hades，打野，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_hades.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第七回合的神方代表：冥界之王，宙斯和波塞冬的长兄。双叉枪在手，最后割开自己的手，用神的血（伊科尔）把枪头锻成
德斯莫斯。美术、图标、音频是 Codex 的（assets/source/hades/，交接说明 assets/source/hades/HANDOFF.md），技能照 Codex 的四个
动作做：
  被动    伊科尔：放完技能（Q、E、R），枪上带着他的血：p_t 拍里下一次普攻额外 p_dmg + p_ad% 攻击力物理伤害（命中是德斯莫斯的
          血光）。写在普攻说明里（游戏只有三个技能图标位），全在数据里。
  attack  双叉枪直刺 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.287 秒）刺到。枪长，射程比一般近战远。
  skill   冥府的铁锤（珀耳塞福涅·卡利科伦）：`Targeting` EnemyWithoutTower（q_range）：q_load 拍运枪、q_go 拍挥出，q_hit 拍（第 6 帧，0.285 秒）
          风压扫过前方扇形（半径 q_r，左右各 acos(q_cone/1000)）：敌人 q_dmg + q_ad% 攻击力物理伤害、减速 q_slow% q_slow_t 拍。
  skill2  大地崩碎者（珀耳塞福涅·提坦）：`Targeting` EnemyWithoutTower（e_range，有人在身边）：e_lift 拍抬枪，e_hit 拍（第 6 帧，0.354 秒）双叉枪砸在
          身前 e_off 处，那一圈（半径 e_r）里的敌人 e_dmg + e_ad% 攻击力物理伤害、被震飞 e_air 拍（原地，不推远）；e_dust 拍碎石落地。
  ult     血之引导曙光（伊科尔·厄俄斯，枪是宿命之四血枪）：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到突刺完为止），r_go 拍（0.305 秒）
          用血锻出强化枪头，r_hit 拍（0.510 秒）朝目标直线突刺（RushTime，速度 r_speed、r_t 拍，穿过去）：路上的敌人 r_dmg +
          r_ad% 攻击力、加目标最大生命 r_thp% 的物理伤害，眩晕 r_stun 拍。突刺前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.236 秒出刺、0.287 秒刺到，风压斩 0.176 秒运枪、0.237 秒挥出、0.285 秒
扫到，重砸 0.292 秒抬枪、0.354 秒砸地、0.425 秒碎石，德斯莫斯 0.305 秒锻枪头、0.510 秒突刺；动作长度普攻 36 拍、风压斩 35 拍、
重砸 43 拍、德斯莫斯 56 拍。

ragnarok.dll（addons/ragnarok/src/hades.rs）：配音和倒地声（被动 ragnarok_hades:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_hades"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，打野 lane 1，600 秒，对手是原版打野），2026-11-22。联盟打野对照（蔚 +2.21、李青 +1.98、
# 瑟庄妮 +1.88、狼人 +0.57、扎克 +0.41、人马 -0.38，中位数约 +1.2），赫拉克勒斯 +1.52，释迦 +1.45。初稿 +2.97（伊科尔每放
# 一个技能就多一下 30 + 50%，技能也偏高）；伊科尔减到 20 + 30%、三个技能伤害各降一成 +2.08，再降属性 +1.72，改成拉长 Q、E 的
# 冷却（7 -> 8 秒、10 -> 12 秒）+1.40 / +2.00（两批 32 个种子差得多）；定下来的这份是冷却拉长再降一点属性（攻击力 88、
# 生命 1150、护甲 38）：+1.15 / +1.18（平均 +1.17，K/D/A 2.2 / 1.4 / 4.3）。
P = {
    # 属性（打野战士）：枪比棍子还长
    "hp": 1150, "hp_g": 110, "atk": 88, "atk_g": 16, "apw": 0, "apw_g": 0, "def": 38, "def_g": 7, "mr": 32,
    "mr_g": 4, "ms": 1060, "ms_g": 11,
    "atk_range": 30000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
    # 被动：伊科尔
    "p_t": 180, "p_dmg": 20, "p_ad": 30,
    # 珀耳塞福涅·风压斩
    # 冥府の鉄槌（2026-11-26 Codex 补画：0.21 秒跳起、0.38 秒往下刺进地、地面炸开甩出风刃，47 拍）：落点一圈 + 往前一条风刃
    "q_cd": 480, "q_range": 42000, "q_dur": 47, "q_load": 13, "q_go": 19, "q_hit": 23, "q_off": 14000, "q_r": 30000,
    "q_len": 62000, "q_w": 8000, "q_dmg": 60, "q_ad": 90, "q2_dmg": 30, "q2_ad": 45, "q_slow": 25, "q_slow_t": 60,
    # 冥府重砸
    "e_cd": 720, "e_range": 34000, "e_dur": 43, "e_lift": 18, "e_hit": 21, "e_dust": 26, "e_off": 22000, "e_r": 30000,
    "e_dmg": 70, "e_ad": 80, "e_air": 30,
    # 伊科尔·德斯莫斯
    "r_cd": 2700, "r_range": 48000, "r_dur": 56, "r_go": 18, "r_hit": 31, "r_dr": 30, "r_speed": 6000, "r_t": 8,
    "r_w": 15000, "r_dmg": 160, "r_ad": 120, "r_thp": 8, "r_stun": 45,
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
    """Delayed 里的效果只给活着的哈迪斯（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def ahead(offset, radius, effects):
    """他身前 offset 处的一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": offset}}, "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：伊科尔（放完技能，下一次普攻带血）
    ichor = flag("ichor", p["p_t"])
    blood = when("ichor", combine(attack(p["p_dmg"], p["p_ad"]), unflag("ichor"), view("p_hit"), tsfx("p_hit")),
                 combine())

    # ------------------------------------------------------------------ 普攻：双叉枪直刺
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit"), blood),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：珀耳塞福涅·风压斩
    # 原作第七回合（ペルセポネ・カリコロン）：跳起来往下刺，地面炸开、甩出风刃：落枪处一圈（身前 q_off、半径 q_r）减速，
    # 风刃再打往前一条（长 q_len、半宽 q_w）
    burst = ahead(p["q_off"], p["q_r"], [attack(p["q_dmg"], p["q_ad"]),
                                         debuff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                                         view("q_hit"), tsfx("q_hit")])
    edge = {"type": "LineRangeProjectile", "name": n("q_edge"), "width": p["q_w"], "length": p["q_len"], "delay": 2,
            "apply": 1, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e}
                                for e in (attack(p["q2_dmg"], p["q2_ad"]), view("q_hit"))]}
    wind = combine(burst, edge)
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_load"] - 1, sfx("q_load")), delayed(p["q_go"] - 1, alive_only(sfx("q"))),
                           delayed(p["q_hit"] - 1, alive_only(wind, ichor))))

    # ------------------------------------------------------------------ E：冥府重砸
    slam = ahead(p["e_off"], p["e_r"], [attack(p["e_dmg"], p["e_ad"]), {"type": "Airborne", "duration": p["e_air"]},
                                        view("e_hit"), tsfx("e_hit")])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(p["e_lift"] - 1, sfx("e_lift")),
                            delayed(p["e_hit"] - 1, alive_only(sfx("e"), slam, ichor)),
                            delayed(p["e_dust"] - 1, alive_only(sfx("e_dust")))))

    # ------------------------------------------------------------------ R：伊科尔·德斯莫斯
    passed = [{"casting_type": "Targeting", "effect": e} for e in
              (attack(p["r_dmg"], p["r_ad"], p["r_thp"]), {"type": "Stun", "duration": p["r_stun"]}, view("r_hit"),
               tsfx("r_hit"))]
    thrust = {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_t"], "range": p["r_w"],
              "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": passed}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_hit"] + p["r_t"], cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_go"] - 1, alive_only(sfx("r_load"))),
                         delayed(p["r_hit"] - 1, alive_only(sfx("r"), thrust, ichor))))

    # ------------------------------------------------------------------ 画面
    # 枪风、风压斩、砸地的地面和碎石、伊科尔觉醒、德斯莫斯的突刺画在他自己的帧里（tools/art/import_hades.py）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "thrust_hit"), E("q_hit", "thrust_hit"), E("e_hit", "thrust_hit"), E("p_hit", "desmos_hit"),
               E("r_hit", "desmos_hit", 3)]
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/hades.rs）：配音、倒地声
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
