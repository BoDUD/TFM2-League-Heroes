#!/usr/bin/env python3
"""坂田金时（终末包第二十三个英雄 ragnarok_kintoki，上路，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_kintoki.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第十二回合的人类方代表（漫画第 107 话起）：平安时代最强的斩鬼人、「人类史上最可爱的汉子」，金太郎长大的样子，
母亲是鬼（八重），祖上是原初神戈尔尼尔和光之女神艾琳。和奥丁打的那个。右手背的达格兹符文「神性之证」是艾琳的符文，叫出来时
金光裹住他和大斧；神器是斯可德加（第十二位瓦尔基里）和他原来的斧头融成的。原作的招：
- 金光雷斧・烈煌閃（第 110 话）：点亮符文，斧刃伸出巨大的斧形光刃，一斧挥出去把光刃打向对手；
- 鬼剛閃・供犠（第 123 话）：踏稳前脚、蓄住腿，斧扛肩上，一下窜到对手身后，途中一记沉重的横斩；
- 秘技・鬼仰轟雷槌 / 絶技・金光轟雷斧（第 126 话）：斧头全力砸地、借势腾空的一击；金光版借斯可德加的力量，一下击碎奥丁的
  神环封壁、让奥丁跪了下来；
- 徒手接住冈格尼尔（第 116 话）：看准第二次投枪，相扑的架势用手掌把枪按进地里，奥丁召回时借着枪的力道反掷回去，第一次让
  奥丁见了血；
- 「我身上流着老妈的鬼之血，还没完呢！」：越伤越能使出比全盛时还大的力气（漫画里他说是背着全人类的心意）。
美术、图标、音效是 Codex 的（assets/source/kintoki/，交接说明 assets/source/kintoki/HANDOFF.md；官方日语配音找不到，没有配音）。
位置是上路战士（用户 2026-11-27 定的）。
  被动    鬼之血（ragnarok.dll）：每损失 1% 生命，攻击力 +p_per/10%，最多 +p_max%。写在普攻说明里。
  attack  横扫一斧 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 4 帧，0.285 秒）出斧，斧长（射程 atk_range）。
  skill   金光雷斧・烈煌閃：`Targeting` EnemyWithoutTower（q_range）：举斧蓄势，q_go 拍（第 5 帧，0.52 秒）一斧劈下把斧形光刃打出去
          （LinearProjectile，每拍 q_speed、长 q_len、半径 q_r，穿过一路的敌人）：q_dmg + q_ad%；q_land 拍（第 6 帧，0.58 秒）
          斧头落地，身前（离他 q2_off、半径 q2_r）的敌人再吃 q2_dmg + q2_ad%（第二段，原作是跳过去反手再一斧）。
  skill2  鬼剛閃・供犠：`Targeting` 敌方英雄（e_range）：e_go 拍（第 3 帧，0.18 秒）一下窜过目标到它身后（RushMoveToBack，
          每拍 e_speed），碰到目标时横斩：e_dmg + e_ad%，e_slow_t 拍里移速 -e_slow%。
  ult     絶技・金光轟雷斧：`Targeting` 敌方英雄（r_range）：右手的神性之证亮起，到斧头落地为止不受控制；r_go 拍（第 6 帧，0.67 秒）
          金光大斧砸地：身前（离他 r_off、半径 r_r）的敌人 r_dmg + r_ad%、击飞 r_up 拍，身上的护盾先被击碎（ragnarok.dll：
          打中时目标带着 r_shatter 的标记，护盾清零；奥丁的神环封壁也一起碎掉）。砸下前被打死就什么都不发生。
  宿敌    被奥丁的冈格尼尔打中时徒手接住（ragnarok.dll）：这一下只吃 100 - k_catch%，然后把枪掷回奥丁：真的飞回去，到了
          造成冈格尼尔那一下 k_back% 的真实伤害，冈格尼尔连奥丁自己的神环封壁和护盾也穿过去。

时间按 Codex 的 frames.json（一秒 60 拍）：普攻第 4 帧 0.285 秒，下劈 0.52 秒放、0.58 秒落地，突进 0.18 秒起步、0.38 秒挥斧，
终结技 0 秒神纹、0.67 秒落地；动作长度普攻 0.75 秒、Q 56 拍、E 44 拍、R 64 拍。

ragnarok.dll（addons/ragnarok/src/kintoki.rs）：被动 ragnarok_kintoki:oni（鬼之血、击碎护盾、接住冈格尼尔，参数 NATIVE_KEYS）、
倒地声。经典 SDK 跑不了 DLL：平衡模拟用 --plain（鬼之血换成一开始就有的平均加成 p_plain%，没有击碎护盾和接枪）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_kintoki"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
PROJ = f"asset/{MOD_ID}/effects/{ID}_proj"
ODIN_PROJ = f"asset/{MOD_ID}/effects/ragnarok_odin_proj"
ODIN_FX = f"asset/{MOD_ID}/effects/ragnarok_odin_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，上路 lane 0，600 秒，对手是原版上单，32 个种子），须佐之男 +1.38、吕布 +1.71 作对照。
# 2026-11-27 初版（Q 90 + 100%、E 70 + 90%、R 200 + 150%）-0.48；三个技能各加一档 +1.21；再加生命 1200、攻击 97（这份 P）+1.46。
P = {
    # 属性（上路战士）
    "hp": 1200, "hp_g": 105, "atk": 97, "atk_g": 16, "apw": 0, "apw_g": 0, "def": 36, "def_g": 6, "mr": 32,
    "mr_g": 4, "ms": 1070, "ms_g": 10,
    "atk_range": 30000, "atk_dur": 36, "atk_cd": 60, "atk_st": 14,
    # 被动：鬼之血（ragnarok.dll；p_plain 只给 --plain 的平衡模拟用）
    "p_per": 4, "p_max": 30, "p_plain": 10,
    # 金光雷斧・烈煌閃
    "q_cd": 420, "q_range": 50000, "q_dur": 56, "q_go": 31, "q_land": 35, "q_speed": 3000, "q_len": 70000,
    "q_r": 9000, "q_y": -3500, "q_dmg": 120, "q_ad": 120, "q2_r": 28000, "q2_off": 14000, "q2_dmg": 60, "q2_ad": 60,
    # 鬼剛閃・供犠
    "e_cd": 600, "e_range": 45000, "e_dur": 44, "e_go": 11, "e_speed": 3500, "e_dmg": 100, "e_ad": 110, "e_slow": 30,
    "e_slow_t": 60,
    # 絶技・金光轟雷斧
    "r_cd": 3000, "r_range": 40000, "r_dur": 64, "r_go": 40, "r_r": 34000, "r_off": 14000, "r_dmg": 250, "r_ad": 170,
    "r_up": 45,
    # 宿敌：徒手接住冈格尼尔（ragnarok.dll）
    "k_catch": 50, "k_back": 100,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/kintoki.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_per", "p_max", "k_catch", "k_back")


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
    """Delayed 里的效果只给活着的金时（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def ahead(radius, off, effects):
    """朝目标那边 off 处的一个圆。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": off}}, "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：鬼之血
    # 游戏里是 ragnarok.dll 按损失的生命每拍改攻击力；平衡模拟（--plain）里换成每个动作都确认一遍的平均加成
    plain_oni = None if is_native else when("p_plain", combine(), flag("p_plain", None, attack_mult=p["p_plain"]))

    # ------------------------------------------------------------------ 普攻：横扫一斧
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(plain_oni, attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")), atype="BaseAttack",
                      cancel=True)

    # ------------------------------------------------------------------ Q：金光雷斧・烈煌閃（光刃打出去，斧落地再一下）
    slash = {"type": "LinearProjectile", "name": n("q_slash"), "speed": p["q_speed"], "range": p["q_len"],
             "shape": {"Circle": {"radius": p["q_r"]}}, "penetrate": True, "end_effects": [], "y_offset": p["q_y"],
             "applied_target": "EnemyWithoutTower",
             "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in
                                 (attack(p["q_dmg"], p["q_ad"]), view("q_hit"), tsfx("q_hit"))]}
    land = ahead(p["q2_r"], p["q2_off"], [attack(p["q2_dmg"], p["q2_ad"]), view("a_hit")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(plain_oni, delayed(p["q_go"] - 1, alive_only(sfx("q"), slash)),
                           delayed(p["q_land"] - 1, alive_only(sfx("q_land"), land))))

    # ------------------------------------------------------------------ E：鬼剛閃・供犠（窜到身后，途中横斩）
    rush = {"type": "RushMoveToBack", "speed": p["e_speed"],
            "applied_effects": [attack(p["e_dmg"], p["e_ad"]),
                                debuff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"),
                                tsfx("e_hit")]}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(plain_oni, delayed(p["e_go"] - 1, alive_only(sfx("e"), rush))))

    # ------------------------------------------------------------------ R：絶技・金光轟雷斧（神纹亮起，金光大斧砸地）
    # r_shatter 先挂上，同一拍的伤害里 ragnarok.dll 认出来，把护盾清零再打
    blow = ahead(p["r_r"], p["r_off"], [debuff("r_shatter", 2), attack(p["r_dmg"], p["r_ad"]),
                                        {"type": "Airborne", "duration": p["r_up"]}, view("r_hit"), tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(plain_oni, flag("r_guard", p["r_go"], cc_immune=True), sfx("r_rune"),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), blow))))

    # ------------------------------------------------------------------ 画面
    # 横扫弧、斧落地的碎岩、突进的拖尾、神性之证和大斧落地画在他自己的帧里（tools/art/import_kintoki.py）；
    # 命中在目标身上；飞出去的光刃是弹道画面（跟着飞行方向转）
    E = lambda name, tag, z=2, anim=FX: {"type": "Animation", "name": n(name), "anim": anim, "tag": tag, "z": z,
                                         "is_follow": True}
    views_e = [E("a_hit", "sweep_hit"), E("q_hit", "cleave_hit"), E("e_hit", "rush_hit", 3), E("r_hit", "cleave_hit", 3),
               E("k_back_hit", "spear_hit", 3, ODIN_FX)]
    views_p = [{"type": "Animated", "name": n("q_slash"), "anim": PROJ, "tag": "slash", "repeat": True, "z": 2},
               # 接住的冈格尼尔掷回奥丁（ragnarok.dll 放的弹道，画面借奥丁的）
               {"type": "Animated", "name": n("k_back"), "anim": ODIN_PROJ, "tag": "spear_flight", "repeat": True,
                "z": 2}]
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
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll（addons/ragnarok/src/kintoki.rs）：鬼之血、击碎护盾、接住冈格尼尔、倒地声
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:oni", "params": {k: p[k] for k in NATIVE_KEYS}},
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
