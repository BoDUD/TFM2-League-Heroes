"""波塞冬（终末包第五个英雄 ragnarok_poseidon，中路，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_poseidon.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第三回合的神方选手，和佐佐木小次郎打的那个。海神，冷傲、不屑同伴（「无需同伴」「神无须依赖」），
三叉戟出手极快。美术、图标、音频是 Codex 的（assets/source/poseidon/，交接说明 assets/source/poseidon/README.md），
技能照 Codex 交接里的四个动作做：
  被动    神无须依赖：身边 p_r 以内没有友方英雄时，攻击力 +p_atk%、受到的伤害降低 p_dr%（ragnarok.dll 每隔几拍看一次，
          加上或去掉 ragnarok_poseidon_p_alone）。写在普攻说明里（游戏只有三个技能图标位）。--plain 给平衡模拟用：
          模拟跑不了 DLL，从第一次放技能起一直开着（对线时他本来就是一个人）。
  attack  水平突刺打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 4 帧，0.225 秒）出手，三叉戟比一般近战长（射程 atk_range）。
  skill   怒涛·安菲特里忒：`Targeting` EnemyWithoutTower（q_range）：q_go 拍起往目标踏进一段（RushTime，碰到敌人就停），
          q_hit 拍起每 q_gap 拍朝前刺一次，共 q_n 次，每次打前方扇形（半径 q_r，左右各 acos(q_cone/1000)）里的敌人
          q_dmg + q_ad% 攻击力物理伤害。
  skill2  降临荒海的神雷：`Targeting` EnemyWithoutTower（e_range）：抬戟（e_rise 拍）后斜着压下去，e_hit 拍在目标脚下
          半径 e_r 的圈里打 e_dmg + e_ad% 攻击力物理伤害，眩晕 e_stun 拍。
  ult     四十昼夜的大洪水：`Targeting` 敌方英雄（r_range）：蓄势 r_go 拍（受到的伤害降低 r_dr%），然后在目标脚下
          半径 r_r 的圈里，每 r_gap 拍一轮戟影连刺，共 r_n 轮，每轮 r_dmg + r_ad% 攻击力物理伤害；第一轮定身 r_root 拍。
          蓄势时被打死就不出手。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.225 秒、连刺 0.225 秒起刺、斜刺 0.18 秒抬戟 0.285 秒落下、
大洪水 0.38 秒放出；动作长度普攻 35 拍、连刺 36 拍、斜刺 37 拍、大招 47 拍。

ragnarok.dll（addons/ragnarok/src/poseidon.rs）：被动 ragnarok_poseidon:alone，参数取 P 里的 p_r / p_atk / p_dr，
另外管配音和倒地声。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_poseidon"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，中路 lane 2，对五个原版中单：火、冰、雷、风、白魔法师，600 秒，每批种子 240 局，
# 击杀差的标准误约 ±0.45，16 批 ±0.31），2026-11-21。对照（联盟的中单，同一套对局，--native 去掉原生代码）：劫 +3.76、
# 永恩 +3.00、泰隆 +2.75、阿狸 +2.67、亚索 +2.38、卡特琳娜 +2.17、菲兹 +1.49、阿卡丽 +0.03，中位数约 +2.5（联盟中单在
# 这套对局里比上单强：吕布那套上路对局里联盟战士的中位数约 +1.44）。初稿 -3.50（伤害 5455 对对手 12945，一局死 2.3 次）：加技能伤害
# -2.29、加属性 -2.87，两样一起 -0.91；伤害再加一档 +0.84，被动更强 +0.11（不用：模拟里被动一直开着，本来就比游戏里强）；
# 再耐打（血 1220、护甲 44、魔抗 36）+1.50 / +0.01（两批种子），再加攻击力 +1.82、技能冷却更短 +1.30（16 批），
# 伤害再加 15%（这份 P）+2.36（16 批，K/D/A 约 3.6 / 1.3 / 3.2，伤害 11399，一局普攻 93、连刺 38、斜刺 27、大洪水 8 次）。
# 被动在模拟里从第一次放技能起一直开着，游戏里身边有队友时没有，所以实战比这个数略弱一点。
# 2026-11-26 照原作改（E 荒海に降る神雷：跳起来往前、像雷雨一样往下刺三阵）以后：初版 +1.91；E 60 + 78%、
# Q 65 + 90%（这份 P）+2.13，改之前 +2.36。
P = {
    # 属性（中路近战）：神的身子，比吕布、宙斯耐打，出手快
    "hp": 1220, "hp_g": 104, "atk": 96, "atk_g": 18, "apw": 0, "apw_g": 0, "def": 44, "def_g": 7, "mr": 36,
    "mr_g": 4, "ms": 1040, "ms_g": 11,
    "atk_range": 30000, "atk_dur": 35, "atk_cd": 60, "atk_st": 14,
    # 被动：神无须依赖（ragnarok.dll）
    "p_r": 70000, "p_atk": 15, "p_dr": 10,
    # 怒涛连刺
    "q_cd": 480, "q_range": 45000, "q_dur": 36, "q_go": 6, "q_speed": 2400, "q_t": 7, "q_hit": 14, "q_n": 4,
    "q_gap": 3, "q_r": 42000, "q_cone": 900, "q_dmg": 65, "q_ad": 90,
    # 暴雨斜刺
    # 荒海に降る神雷（2026-11-26 Codex 补画：0.21 秒跳起、0.289 / 0.352 / 0.413 秒三阵下刺、0.475 秒落地，42 拍）：伤害分成三下，
    # 加起来和原来一下一样
    "e_cd": 600, "e_range": 34000, "e_dur": 42, "e_jump": 13, "e_speed": 2000, "e_t": 15, "e_s1": 17, "e_s2": 21,
    "e_s3": 25, "e_r": 20000, "e_dmg": 60, "e_ad": 78, "e_stun": 42,
    # 四十昼夜的大洪水
    "r_cd": 2400, "r_range": 42000, "r_dur": 47, "r_go": 23, "r_dr": 30, "r_n": 6, "r_gap": 4, "r_r": 22000,
    "r_dmg": 85, "r_ad": 115, "r_root": 45,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/poseidon.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_r", "p_atk", "p_dr")


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


def circle(r):
    return {"Circle": {"radius": r}}


def T(e):
    return {"casting_type": "Targeting", "effect": e}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的波塞冬（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain：被动从第一次放技能起一直开着（模拟跑不了 ragnarok.dll）
    alone = None if is_native else when(
        "p_on", combine(), combine(flag("p_on", None),
                                   flag("p_alone", None, attack_mult=p["p_atk"], damaged_reduce=p["p_dr"])))

    # ------------------------------------------------------------------ 普攻：水平突刺
    thrust = combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", thrust,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：怒涛连刺
    step = {"type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": []}
    cone = {"DirDot": {"radius": p["q_r"], "range": p["q_cone"]}}
    stab = {"type": "RangeEffect", "shape": cone, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}},
            "effects": [attack(p["q_dmg"], p["q_ad"]), view("q_hit")]}
    stabs = [delayed(p["q_hit"] - 1 + i * p["q_gap"], stab, tsfx("q_hit") if i == p["q_n"] - 1 else None)
             for i in range(p["q_n"])]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(alone, delayed(p["q_go"] - 1, sfx("q_step"), step), delayed(p["q_hit"] - 1, sfx("q")), *stabs))

    # ------------------------------------------------------------------ E：荒海に降る神雷
    # 原作第三回合：跳起来从上面像雷雨一样往下连刺，边刺边移动。e_jump 拍往前跳（RushTime，碰到就停），三阵下刺落在目标脚下，
    # 第三阵眩晕
    leap = {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": []}

    def rain(last):
        hit = [attack(p["e_dmg"], p["e_ad"]), view("e_hit")]
        if last:
            hit += [{"type": "Stun", "duration": p["e_stun"]}, tsfx("e_hit")]
        return {"type": "RangeProjectile", "name": n("e_fall"), "shape": circle(p["e_r"]), "delay": 1, "apply": 1,
                "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in hit]}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(alone, delayed(p["e_jump"] - 1, sfx("e_rise"), alive_only(leap)),
                            delayed(p["e_s1"] - 1, alive_only(sfx("e"), rain(False))),
                            delayed(p["e_s2"] - 1, alive_only(rain(False))),
                            delayed(p["e_s3"] - 1, alive_only(rain(True)))))

    # ------------------------------------------------------------------ R：四十昼夜的大洪水
    root = {"type": "Bind", "duration": p["r_root"]}
    first = {"type": "RangeProjectile", "name": n("r_first"), "shape": circle(p["r_r"]), "delay": 1, "apply": 1,
             "applied_target": "EnemyWithoutTower",
             "applied_effects": [T(e) for e in (attack(p["r_dmg"], p["r_ad"]), root, view("r_hit"))]}
    rest = {"type": "RangePeriodProjectile", "name": n("r_flood"), "shape": circle(p["r_r"]),
            "tick": (p["r_n"] - 1) * p["r_gap"] + 1, "period": p["r_gap"], "first_delay": p["r_gap"],
            "applied_target": "EnemyWithoutTower",
            "applied_effects": [T(e) for e in (attack(p["r_dmg"], p["r_ad"]), view("r_hit"))], "end_effects": []}
    guard = flag("r_guard", p["r_go"] + 2, damaged_reduce=p["r_dr"])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(alone, guard, sfx("r_charge"),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), view("r_barrage"), tsfx("r_hit"), first, rest))))

    # ------------------------------------------------------------------ 画面
    # 戟风、连刺的扇形、斜刺的升势和坠刺、大洪水的蓄势画在他自己的帧里（tools/art/import_poseidon.py）；打在人身上的
    # 命中水花、大洪水的环形戟影放在目标身上
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "thrust_hit"), E("q_hit", "flurry_hit"), E("e_hit", "thrust_hit"), E("r_hit", "flurry_hit"),
               E("r_barrage", "flood_barrage", 3)]
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/poseidon.rs）：被动神无须依赖、配音
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:alone", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def check_dll(p):
    """addons/ragnarok/src/poseidon.rs 的 Params::default() 和 P 里 DLL 读的那几个一样（DLL 读 passive.params，默认值是退路）。"""
    import re
    path = os.path.join(REPO, "addons", "ragnarok", "src", "poseidon.rs")
    if not os.path.exists(lp(path)):
        return
    src = open(lp(path), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"poseidon.rs Params::default() 和 P 不一样（poseidon.rs, P）: {bad}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动，被动一直开着")
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
    if not a.plain and not a.set and not a.params:
        check_dll(p)
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
