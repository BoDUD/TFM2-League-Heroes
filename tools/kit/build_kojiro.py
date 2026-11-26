"""佐佐木小次郎（终末包第六个英雄 ragnarok_kojiro，上路，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_kojiro.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第三回合的人类方选手，和波塞冬打的那个：「史上最强的败者」，一辈子没赢过，却把每个打败他的人都记在心里，
在脑子里和他们打了千万遍。美术、图标、音频是 Codex 的（assets/source/kojiro/，交接说明 assets/source/kojiro/HANDOFF.md），
技能照 Codex 交接里的四个动作做：
  被动    预判：每打中一个敌方英雄一次，就记下他一招（每个人最多 p_max 招），之后对他的伤害每招 +p_per%；死了重新记
          （ragnarok.dll 记每个对手各自的招数，改每一下的伤害）。写在普攻说明里（游戏只有三个技能图标位）。--plain 给平衡
          模拟用：模拟跑不了 DLL，从第一次放技能起攻击力一直 +p_per x p_max / 2 %（记到一半的样子，对线时他打的总是同一个人）。
  attack  单刀一斩打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 4 帧，0.24 秒）出刀，备前长光刀身长（射程 atk_range）。
          二天岩流之后（身上有 ragnarok_kojiro_niten）是双刀：先一刀 100%，过 a2_gap 拍交错一刀 r_extra% 攻击力。
  skill   燕返：`Targeting` EnemyWithoutTower（q_range）：q_hit1 拍（第 4 帧）往前斩下，前方扇形（半径 q_r，左右各
          acos(q_cone/1000)）里的敌人 q1_dmg + q1_ad% 攻击力物理伤害；q_hit2 拍（第 6 帧）反刃上撩，同一个扇形
          q2_dmg + q2_ad%，减速 q_slow% q_slow_t 拍（燕子躲不开第二刀）。
  skill2  千手无双：`Targeting` 敌方英雄（e_range）：e_go 拍（第 3 帧）预判，之后 e_t 拍里受到的伤害降低 e_dr%、攻速 +e_as%
          （一千种走法都看过了，侧身让开、出刀更快）。
  ult     二天岩流：`Targeting` 敌方英雄（r_range）：起手到第一刀（r_hit1 拍）受到的伤害降低 r_dr%、不受控制，r_hit1 拍
          双刀斩下，前方扇形 r1_dmg + r1_ad%；r_hit2 拍双刀交错，r2_dmg + r2_ad%、眩晕 r_stun 拍；然后 r_form 拍拿着两把刀
          （ragnarok_kojiro_niten：攻速 +r_as%，普攻变双刀）。出刀前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.24 秒出刀，燕返 0.275 / 0.38 秒，千手无双 0.18 秒预判、0.245 秒侧避，
二天岩流 0.365 / 0.487 秒；动作长度普攻 36 拍、燕返 38 拍、千手无双 41 拍、二天岩流 48 拍。

ragnarok.dll（addons/ragnarok/src/kojiro.rs）：被动 ragnarok_kojiro:predict，参数取 P 里的 p_per / p_max；配音、倒地声，和二天岩流
时把待机、普攻换成双刀的显示钩子。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_kojiro"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，上路 lane 0，600 秒，对手和吕布、宙斯、亚当同一套：基础战士和另外五个原版上单，每批种子
# 288 局，16 批的击杀差标准误约 ±0.28），2026-11-21。这套对局里联盟战士的中位数约 +1.44；终末包两批种子的平均：吕布 1.43、
# 亚当 1.38、宙斯 1.24、索尔 1.09。初稿 +0.67（血 1060、护甲 34、魔抗 28）；技能伤害加三成 +2.02，伤害和属性各加一半 +2.16
# （太强）；只加属性（这份 P：血 1200、护甲 40、魔抗 32）+1.46 / +1.70（两批 16 种子，K/D/A 约 2.7 / 0.9 / 3.5，一局普攻 134、
# 燕返 40、千手无双 12、二天岩流 6 次），比它少一点（血 1180、护甲 39、魔抗 31）+0.93 / +1.39。
P = {
    # 属性（上路剑客）：老剑客，耐打
    "hp": 1200, "hp_g": 110, "atk": 98, "atk_g": 18, "apw": 0, "apw_g": 0, "def": 40, "def_g": 8, "mr": 32,
    "mr_g": 4, "ms": 1050, "ms_g": 11,
    "atk_range": 28000, "atk_dur": 36, "atk_cd": 60, "atk_st": 14,
    # 被动：预判（ragnarok.dll）
    "p_per": 3, "p_max": 8,
    # 燕返
    "q_cd": 420, "q_range": 30000, "q_dur": 38, "q_hit1": 17, "q_hit2": 23, "q_r": 36000, "q_cone": 700,
    "q1_dmg": 40, "q1_ad": 60, "q2_dmg": 60, "q2_ad": 90, "q_slow": 35, "q_slow_t": 60,
    # 千手无双
    "e_cd": 720, "e_range": 40000, "e_dur": 41, "e_go": 11, "e_dodge": 15, "e_t": 150, "e_dr": 30, "e_as": 50,
    # 二天岩流
    "r_cd": 2700, "r_range": 32000, "r_dur": 48, "r_hit1": 22, "r_hit2": 29, "r_r": 38000, "r_cone": 600,
    "r1_dmg": 80, "r1_ad": 100, "r2_dmg": 120, "r2_ad": 140, "r_stun": 36, "r_dr": 30,
    "r_form": 480, "r_as": 30, "r_extra": 40, "a2_gap": 6,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/kojiro.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_per", "p_max")


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


def slow(name, pct, tick):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}},
                                              "move_speed_mult": -pct}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的小次郎（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cut(radius, cone, effects):
    """前方扇形一刀（半径 radius，左右各 acos(cone/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cone}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain：被动按记到一半算，从第一次放技能起攻击力一直加着（模拟跑不了 ragnarok.dll）
    first = None if is_native else when(
        "p_on", combine(), combine(flag("p_on", None),
                                   flag("p_learn", None, attack_mult=p["p_per"] * p["p_max"] // 2)))

    # ------------------------------------------------------------------ 普攻：单刀一斩，二天岩流之后双刀
    single = combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit"))
    double = combine(attack(0, 100), sfx("a2"), view("a_hit"), tsfx("a_hit"),
                     delayed(p["a2_gap"], attack(0, p["r_extra"]), view("a_hit"), tsfx("a_hit2")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      when("niten", double, single), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：燕返
    down = cut(p["q_r"], p["q_cone"], [attack(p["q1_dmg"], p["q1_ad"]), view("q_hit")])
    up = cut(p["q_r"], p["q_cone"], [attack(p["q2_dmg"], p["q2_ad"]), slow("q_slow", p["q_slow"], p["q_slow_t"]),
                                     view("q_hit")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, delayed(p["q_hit1"] - 1, sfx("q1"), down),
                           delayed(p["q_hit2"] - 1, sfx("q2"), up, tsfx("q_hit"))))

    # ------------------------------------------------------------------ E：千手无双
    read = flag("e_read", p["e_t"], damaged_reduce=p["e_dr"], attack_speed_mult=p["e_as"])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(first, delayed(p["e_go"] - 1, sfx("e"), read), delayed(p["e_dodge"] - 1, sfx("e_dodge"))))

    # ------------------------------------------------------------------ R：二天岩流
    guard = flag("r_guard", p["r_hit1"] + 1, cc_immune=True, damaged_reduce=p["r_dr"])
    first_cut = cut(p["r_r"], p["r_cone"], [attack(p["r1_dmg"], p["r1_ad"]), view("r_hit")])
    cross = cut(p["r_r"], p["r_cone"], [attack(p["r2_dmg"], p["r2_ad"]), {"type": "Stun", "duration": p["r_stun"]},
                                        view("r_hit")])
    niten = flag("niten", p["r_form"], attack_speed_mult=p["r_as"])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, guard,
                         delayed(p["r_hit1"] - 1, alive_only(sfx("r1"), first_cut)),
                         delayed(p["r_hit2"] - 1, alive_only(sfx("r2"), cross, tsfx("r_hit"), niten))))

    # ------------------------------------------------------------------ 画面
    # 燕返刀光、预判涟漪、双刀交错画在他自己的帧里（tools/art/import_kojiro.py）；打在人身上的是金属火花
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "steel_impact"), E("q_hit", "steel_impact"), E("r_hit", "steel_impact")]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/kojiro.rs）：被动预判、配音、双刀的显示
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:predict", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def check_dll(p):
    """addons/ragnarok/src/kojiro.rs 的 Params::default() 和 P 里 DLL 读的那几个一样（DLL 读 passive.params，默认值是退路）。"""
    import re
    path = os.path.join(REPO, "addons", "ragnarok", "src", "kojiro.rs")
    if not os.path.exists(lp(path)):
        return
    src = open(lp(path), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"kojiro.rs Params::default() 和 P 不一样（kojiro.rs, P）: {bad}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动，被动按记到一半一直开着")
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
