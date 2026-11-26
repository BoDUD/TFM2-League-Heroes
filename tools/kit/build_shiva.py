"""湿婆（终末包第十个英雄 ragnarok_shiva，中路，Assassin）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_shiva.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第五回合的神方选手，和雷电为右卫门打的那个：破坏神，四只手臂，跳舞一样打架；燃尽心脏的轮回舞踊（Tandava Karma）
让他浑身燃烧。美术、图标、音频是 Codex 的（assets/source/shiva/，交接说明 assets/source/shiva/HANDOFF.md），技能照 Codex 的两套
动作做：常态和第 5 帧起燃烧的轮回舞踊形态（ragnarok_shiva_tandava 这个 buff，ragnarok.dll 的显示钩子换上 h_* 的帧）。
  被动    轮回舞踊（节拍）：舞有节拍，他每放一个技能（Q、E、R）记一拍（最多 p_max 拍），每拍攻击力 +p_atk%、攻速 +p_as%；p_t 拍里没再放
          技能就散掉（ragnarok.dll 认他放了技能、挂 buff）。写在普攻说明里（游戏只有三个技能图标位）。--plain 给平衡模拟用：
          模拟跑不了 DLL，从第一次放技能起一直按 p_max / 2 拍算。
  attack  四臂一扫打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.287 秒）打到；轮回舞踊里是火鞭，多 h_atk% 攻击力。
  skill   四臂连击：`Targeting` EnemyWithoutTower（q_range）：q_hit1 拍（第 4 帧）交叉一击、q_hit2 拍（第 6 帧）横扫一击，各打前方
          扇形（半径 q_r，左右各 acos(q_cone/1000)）里的敌人 q1_dmg + q1_ad% / q2_dmg + q2_ad% 物理伤害，第二下减速 q_slow%
          q_slow_t 拍；轮回舞踊里伤害乘 h_mul%。
  skill2  虎爪炎舞：`Targeting` 敌方英雄（e_range）：踏着舞步冲到他身上（e_speed），落脚那一下身边 e_r 里的敌人 e_dmg + e_ad%
          物理伤害、减速 e_slow% e_slow_t 拍；轮回舞踊里是火步，伤害乘 h_mul%。
  ult     轮回舞踊：`Targeting` 敌方英雄（r_range）：变身 r_dur 拍（到第 5 帧变过去之前不受控制、受到的伤害降低 r_dr%），
          r_switch 拍（0.51 秒）点燃，r_t 拍的燃烧形态：攻击力 +r_atk%、攻速 +r_as%、移速 +r_ms%。形态结束时最后一记高踢
          （h_ult，r_end_dur 拍，r_end_hit 拍踢到）：前方扇形（半径 r_end_r）里的敌人 r_end_dmg + r_end_ad%，击飞 r_end_up 拍。
          变身前、踢到前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.287 秒打到（燃烧形态的普攻、Q 按常态的节奏重排，import_shiva 的 RETIME），
连击 0.237 / 0.336 秒，舞步 0.292 秒落脚，变身 0.305 秒起势、0.51 秒点燃，高踢 0.258 秒抬腿、0.423 秒踢到；动作长度普攻 36 拍、
连击 35 拍、舞步 43 拍、变身 56 拍、高踢 48 拍。

ragnarok.dll（addons/ragnarok/src/shiva.rs）：被动 ragnarok_shiva:rhythm，参数取 P 里的 p_atk / p_as / p_max / p_t；配音、
倒地声，和轮回舞踊形态的显示钩子。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_shiva"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，中路 lane 2，600 秒，对手是五个原版中单），2026-11-22。联盟中单对照（劫 +3.76、永恩 +3.00、
# 泰隆 +2.75、阿狸 +2.67、亚索 +2.38、卡特琳娜 +2.17、菲兹 +1.49、阿卡丽 +0.03，中位数约 +2.5）。初稿 +0.24：伤害打不出来、舞步
# 一局才放 11 次；加技能伤害、舞步冷却缩到 8 秒 +0.43，燃烧形态更久更强 +0.96，再加属性（攻击 100、移速 1080、生命 1050）
# +2.40 / +1.58（两批种子）；定这一份（攻击 105、连击 65 / 75）：16 个种子 +2.25（K/D/A 4.3 / 2.0 / 3.5，一局普攻 99、连击 39、
# 舞步 13、轮回舞踊 6 次）。
# 2026-11-26 照原作改（E 虎爪炎舞：跳起来带火往下踢）以后：初版 +0.73；E 跳起来一路追到目标身上再踢、
# 伤害 90 + 102%（这份 P）+2.39，改之前 +2.25。
P = {
    # 属性（中路刺客）：四只手，身子不算硬
    "hp": 1050, "hp_g": 100, "atk": 105, "atk_g": 18, "apw": 0, "apw_g": 0, "def": 32, "def_g": 6, "mr": 28,
    "mr_g": 3, "ms": 1080, "ms_g": 11,
    "atk_range": 26000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17, "h_atk": 30,
    # 被动：节奏（ragnarok.dll）
    "p_atk": 4, "p_as": 6, "p_max": 4, "p_t": 240,
    # 四臂连击
    "q_cd": 360, "q_range": 28000, "q_dur": 35, "q_hit1": 14, "q_hit2": 20, "q_r": 34000, "q_cone": 700,
    "q1_dmg": 65, "q1_ad": 80, "q2_dmg": 75, "q2_ad": 95, "q_slow": 25, "q_slow_t": 60, "h_mul": 130,
    # 舞步
    # 虎爪炎舞（2026-11-26 Codex 补画：0.21 秒跳起、0.355 秒踢中、0.422 秒落地，46 拍）：跳起来往目标扑过去（RushTime，碰到就停）
    "e_cd": 480, "e_range": 45000, "e_dur": 46, "e_jump": 13, "e_speed": 5000, "e_t": 8, "e_kick": 21, "e_r": 30000,
    "e_chase": 1,
    "e_dmg": 90, "e_ad": 102, "e_slow": 30, "e_slow_t": 60,
    # 轮回舞踊
    "r_cd": 3000, "r_range": 30000, "r_dur": 56, "r_go": 18, "r_switch": 31, "r_dr": 40,
    "r_t": 480, "r_atk": 35, "r_as": 40, "r_ms": 15,
    "r_end_dur": 48, "r_end_go": 15, "r_end_hit": 25, "r_end_r": 40000, "r_end_cone": 600, "r_end_dmg": 150, "r_end_ad": 150,
    "r_end_up": 45,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/shiva.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_atk", "p_as", "p_max", "p_t")


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
    """Delayed 里的效果只给活着的湿婆（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def around(radius, effects):
    """他身边一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain：节奏按一半算，从第一次放技能起一直加着（模拟跑不了 ragnarok.dll）
    half = p["p_max"] // 2
    first = None if is_native else when(
        "p_on", combine(), combine(flag("p_on", None),
                                   flag("p_beat", None, attack_mult=p["p_atk"] * half, attack_speed_mult=p["p_as"] * half)))
    hm = lambda x: x * p["h_mul"] // 100

    # ------------------------------------------------------------------ 普攻：四臂一扫，轮回舞踊里是火鞭
    arms = combine(sfx("a"), attack(0, 100), view("a_hit"), tsfx("a_hit"))
    whip = combine(sfx("ha"), attack(0, 100 + p["h_atk"]), view("h_hit"), tsfx("ha_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      when("tandava", whip, arms), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：四臂连击
    def hit(dmg, ad, tag, *more):
        return cone(p["q_r"], p["q_cone"], [attack(dmg, ad), view(tag), *more])
    q_one = when("tandava", combine(sfx("q1"), hit(hm(p["q1_dmg"]), hm(p["q1_ad"]), "h_hit")),
                 combine(sfx("q1"), hit(p["q1_dmg"], p["q1_ad"], "a_hit")))
    q_two = when("tandava", combine(sfx("hq2"), hit(hm(p["q2_dmg"]), hm(p["q2_ad"]), "h_hit",
                                                    slow("q_slow", p["q_slow"], p["q_slow_t"])), tsfx("ha_hit")),
                 combine(sfx("q2"), hit(p["q2_dmg"], p["q2_ad"], "a_hit", slow("q_slow", p["q_slow"], p["q_slow_t"])),
                         tsfx("a_hit")))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, delayed(p["q_hit1"] - 1, q_one), delayed(p["q_hit2"] - 1, alive_only(q_two))))

    # ------------------------------------------------------------------ E：舞步（冲到他身上，落脚一圈）
    def step(mul, snd, tag):
        return combine(sfx(snd), around(p["e_r"], [attack(p["e_dmg"] * mul // 100, p["e_ad"] * mul // 100),
                                                   slow("e_slow", p["e_slow"], p["e_slow_t"]), view(tag)]))
    land = when("tandava", step(p["h_mul"], "he", "h_hit"), step(100, "e", "a_hit"))
    # 原作第五回合（クリッティヴァーサス）：跳起来带着火往下踢，从雷电的脸一直踢到肚脐
    leap = {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_t"], "range": 15000,
            "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": []}
    # e_chase：跳起来以后一路追到目标身上（MoveToTarget，原来舞步的做法），落到身上就踢；不然往前冲一段、第 e_kick 拍踢
    if p["e_chase"]:
        kick = delayed(p["e_jump"] - 1, alive_only({"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"],
                                                    "end_effects": [land, view("e_flame")]}))
    else:
        kick = combine(delayed(p["e_jump"] - 1, alive_only(leap)), delayed(p["e_kick"] - 1, alive_only(land, view("e_flame"))))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion", combine(first, kick))

    # ------------------------------------------------------------------ R：轮回舞踊
    guard = flag("r_guard", p["r_switch"] + 1, cc_immune=True, damaged_reduce=p["r_dr"])
    form = flag("tandava", p["r_t"], attack_mult=p["r_atk"], attack_speed_mult=p["r_as"], move_speed_mult=p["r_ms"])
    end = p["r_switch"] + p["r_t"]
    kick = cone(p["r_end_r"], p["r_end_cone"], [attack(p["r_end_dmg"], p["r_end_ad"]),
                                               {"type": "Airborne", "duration": p["r_end_up"]}, view("h_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, guard,
                         delayed(p["r_go"] - 1, alive_only(sfx("r1"))),
                         delayed(p["r_switch"] - 1, alive_only(sfx("r2"), form)),
                         delayed(end - 1, alive_only(anim("h_ult", p["r_end_dur"]), sfx("r_end"))),
                         delayed(end - 1 + p["r_end_hit"] - 1, alive_only(kick, sfx("r_end_hit")))))

    # ------------------------------------------------------------------ 画面
    # 拳风、交叉、舞步、点燃、火鞭、火步画在他自己的帧里（tools/art/import_shiva.py）；打在人身上的是银光和火焰命中
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "silver_hit"), E("h_hit", "final_hit"), E("e_flame", "flame_hit", 3)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/shiva.rs）：节奏、配音、轮回舞踊形态的显示
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:rhythm", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def check_dll(p):
    """addons/ragnarok/src/shiva.rs 的 Params::default() 和 P 里 DLL 读的那几个一样（DLL 读 passive.params，默认值是退路）。"""
    import re
    path = os.path.join(REPO, "addons", "ragnarok", "src", "shiva.rs")
    if not os.path.exists(lp(path)):
        return
    src = open(lp(path), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"shiva.rs Params::default() 和 P 不一样（shiva.rs, P）: {bad}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动，节奏按一半一直开着")
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
