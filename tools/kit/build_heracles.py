"""赫拉克勒斯（终末包第七个英雄 ragnarok_heracles，打野，Tank）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_heracles.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第四回合的神方选手，和开膛手杰克打的那个：神里唯一站在人类一边的正义之神。为了守护人类，他把十二御业
一个个用出来，每用一个，身上的刻印就往心脏爬一点，最后和冥府的看门犬刻耳柏洛斯订下契约（第十二御业）。美术、图标、
音频是 Codex 的（assets/source/heracles/，交接说明 assets/source/heracles/HANDOFF.md），技能照 Codex 的两套动作做：
常态拿狮头巨棒，第十二御业以后是空手、肩背骨爪的刻耳柏洛斯形态（ragnarok_heracles_cerberus 这个 buff，
ragnarok.dll 的显示钩子换上 c_* 的帧）。
  被动    十二御业的刻印：每放一个技能刻印爬一格（大招两格，最多 p_max 格），每格攻击力 +p_atk%、护甲和魔抗 +p_res；
          死了刻印消退（ragnarok.dll 认他放了技能、挂 buff）。写在普攻说明里（游戏只有三个技能图标位）。--plain 给平衡
          模拟用：模拟跑不了 DLL，从第一次放技能起一直按 p_max / 2 格算。
  attack  巨棒一击打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.33 秒）打到；刻耳柏洛斯形态是一拳，同一刻打到。
  skill   涅墨亚之狮：`Targeting` EnemyWithoutTower（q_range）：巨棒往前一顶，狮头冲出去，q_hit 拍（第 5 帧）前方扇形
          （半径 q_r，左右各 acos(q_cone/1000)）里的敌人 q_dmg + q_ad% 攻击力物理伤害、减速 q_slow% q_slow_t 拍。
          刻耳柏洛斯形态：一拳往前砸地，同一刻身前 cq_r 里的敌人 cq_dmg + cq_ad%，击飞 cq_up 拍。
  skill2  克里特公牛：`Targeting` EnemyWithoutTower（e_range）：巨棒砸地，e_hit 拍（第 5 帧）身前 e_r 里的敌人 e_dmg +
          e_ad% 攻击力物理伤害、眩晕 e_stun 拍。刻耳柏洛斯形态：护势，ce_go 拍起 ce_t 拍里受到的伤害降低 ce_dr%、反弹
          ce_ref%，身边 ce_r 里的敌人被嘲讽 ce_taunt 拍。
  ult     刻耳柏洛斯（第十二御业）：`Targeting` 敌方英雄（r_range）：变身 r_dur 拍（不受控制、受到的伤害降低 r_cdr%），
          r_switch 拍（第 5 帧，0.59 秒）变成刻耳柏洛斯形态，r_t 拍：攻击力 +r_atk%、攻速 +r_as%、移速 +r_ms%、受到的
          伤害降低 r_dr%、吸血 r_vamp%。形态结束时最后一记重拳砸地（c_ult，r_end_dur 拍，r_end_hit 拍砸到）：身边 r_end_r
          里的敌人 r_end_dmg + r_end_ad%，击飞 r_end_up 拍。变身前、砸地前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.33 秒打到（刻耳柏洛斯的拳按普攻的节奏重排，import_heracles 的
RETIME），涅墨亚之狮 0.317 秒放狮头、0.38 秒打到，克里特公牛 0.371 秒砸地，护势 0.218 秒，变身 0.32 秒起势、0.59 秒变，
形态结束的重拳 0.329 秒挥、0.401 秒砸地；动作长度普攻 40 拍、两个技能各 44 拍、变身 63 拍、重拳 47 拍。

ragnarok.dll（addons/ragnarok/src/heracles.rs）：被动 ragnarok_heracles:brand，参数取 P 里的 p_atk / p_res / p_max / p_ult；
配音、倒地声，和刻耳柏洛斯形态的显示钩子。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_heracles"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，打野 lane 1，600 秒，对手是五个原版打野，每批种子 240 局，8 个种子的击杀差标准误
# 约 ±0.45），2026-11-21。经典 SDK 没有 Tank 这个分类，模拟时写 Melee。联盟打野在这套对局里：蔚 +2.21、李青 +1.98、
# 瑟庄妮 +1.88、狼人 +0.57、扎克 +0.41、人马 -0.38（中位数约 +1.2）。初稿 +0.30（扛得多、打得少：一局伤害 4732，对手
# 7521）；技能伤害加三成 +0.82，再加攻击和刻耳柏洛斯形态 +1.02 / +1.14（两批种子），再加血和护甲（这份 P：血 1300、
# 护甲 50）+1.59 / +1.44；同底子只加攻击、Q 冷却 +1.73。
P = {
    # 属性（打野坦克）：大个子，耐打
    "hp": 1300, "hp_g": 120, "atk": 90, "atk_g": 14, "apw": 0, "apw_g": 0, "def": 50, "def_g": 8, "mr": 36,
    "mr_g": 4, "ms": 1040, "ms_g": 11,
    "atk_range": 27000, "atk_dur": 40, "atk_cd": 66, "atk_st": 20,
    # 被动：十二御业的刻印（ragnarok.dll）
    "p_atk": 1, "p_res": 2, "p_max": 12, "p_ult": 2,
    # 涅墨亚之狮（刻耳柏洛斯形态：砸地的一拳）
    "q_cd": 480, "q_range": 32000, "q_dur": 44, "q_hit": 23, "q_r": 42000, "q_cone": 600,
    "q_dmg": 80, "q_ad": 100, "q_slow": 30, "q_slow_t": 90,
    "cq_r": 30000, "cq_off": 12000, "cq_dmg": 90, "cq_ad": 120, "cq_up": 30,
    # 克里特公牛（刻耳柏洛斯形态：护势）
    "e_cd": 720, "e_range": 28000, "e_dur": 44, "e_hit": 22, "e_r": 30000, "e_off": 15000,
    "e_dmg": 70, "e_ad": 80, "e_stun": 45,
    "ce_go": 13, "ce_t": 150, "ce_dr": 35, "ce_ref": 20, "ce_r": 32000, "ce_taunt": 60,
    # 刻耳柏洛斯
    "r_cd": 3000, "r_range": 30000, "r_dur": 63, "r_go": 19, "r_switch": 35, "r_cdr": 40,
    "r_t": 480, "r_atk": 40, "r_as": 50, "r_ms": 15, "r_dr": 20, "r_vamp": 15,
    "r_end_dur": 47, "r_end_go": 20, "r_end_hit": 24, "r_end_r": 36000, "r_end_dmg": 140, "r_end_ad": 150,
    "r_end_up": 45,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/heracles.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_atk", "p_res", "p_max", "p_ult")


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
    """Delayed 里的效果只给活着的赫拉克勒斯（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def ahead(radius, offset, effects):
    """身前 offset 处一圈（半径 radius）。"""
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
    # --plain：刻印按一半算，从第一次放技能起一直加着（模拟跑不了 ragnarok.dll）
    half = p["p_max"] // 2
    first = None if is_native else when(
        "p_on", combine(), combine(flag("p_on", None),
                                   flag("p_brand", None, attack_mult=p["p_atk"] * half, defence=p["p_res"] * half,
                                        magic_resistance=p["p_res"] * half)))

    # ------------------------------------------------------------------ 普攻：巨棒，刻耳柏洛斯形态是拳
    club = combine(attack(0, 100), view("a_hit"), tsfx("a_hit"))
    fist = combine(attack(0, 100), view("ca_hit"), tsfx("ca_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(when("cerberus", sfx("ca"), sfx("a")), when("cerberus", fist, club)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：涅墨亚之狮 / 砸地的一拳
    lion = combine(sfx("q"), cone(p["q_r"], p["q_cone"], [attack(p["q_dmg"], p["q_ad"]),
                                                         slow("q_slow", p["q_slow"], p["q_slow_t"]), view("a_hit")]),
                   tsfx("q_hit"))
    fang = combine(sfx("cq"), ahead(p["cq_r"], p["cq_off"], [attack(p["cq_dmg"], p["cq_ad"]),
                                                            {"type": "Airborne", "duration": p["cq_up"]},
                                                            view("ca_hit")]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, delayed(p["q_hit"] - 1, when("cerberus", fang, lion))))

    # ------------------------------------------------------------------ E：克里特公牛 / 护势
    bull = combine(sfx("e"), ahead(p["e_r"], p["e_off"], [attack(p["e_dmg"], p["e_ad"]),
                                                         {"type": "Stun", "duration": p["e_stun"]}]))
    guard = combine(sfx("ce"), flag("ce_guard", p["ce_t"], damaged_reduce=p["ce_dr"], damage_reflect=p["ce_ref"]),
                    around(p["ce_r"], [{"type": "Taunt", "duration": p["ce_taunt"]}]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(first, when("cerberus", delayed(p["ce_go"] - 1, guard),
                                        delayed(p["e_hit"] - 1, bull))))

    # ------------------------------------------------------------------ R：刻耳柏洛斯
    change = flag("r_change", p["r_switch"] + 1, cc_immune=True, damaged_reduce=p["r_cdr"])
    form = flag("cerberus", p["r_t"], attack_mult=p["r_atk"], attack_speed_mult=p["r_as"], move_speed_mult=p["r_ms"],
                damaged_reduce=p["r_dr"], vamp=p["r_vamp"])
    end = p["r_switch"] + p["r_t"]
    slam = around(p["r_end_r"], [attack(p["r_end_dmg"], p["r_end_ad"]), {"type": "Airborne", "duration": p["r_end_up"]},
                                 view("ca_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, change,
                         delayed(p["r_go"] - 1, alive_only(sfx("r1"))),
                         delayed(p["r_switch"] - 1, alive_only(sfx("r2"), form)),
                         delayed(end - 1, alive_only(anim("c_ult", p["r_end_dur"]), sfx("r_end"))),
                         delayed(end - 1 + p["r_end_hit"] - 1, alive_only(slam))))

    # ------------------------------------------------------------------ 画面
    # 弧光、狮头、变身的光环、拳风、砸地的冲击画在他自己的帧里（tools/art/import_heracles.py）；打在人身上的是两种命中
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "club_hit"), E("ca_hit", "cerberus_hit")]
    kit = {
        # 经典 SDK（平衡模拟）没有 Tank 这个分类：--plain 写 Melee（宙斯的做法）
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/heracles.rs）：刻印、配音、刻耳柏洛斯形态的显示
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:brand", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def check_dll(p):
    """addons/ragnarok/src/heracles.rs 的 Params::default() 和 P 里 DLL 读的那几个一样（DLL 读 passive.params，默认值是退路）。"""
    import re
    path = os.path.join(REPO, "addons", "ragnarok", "src", "heracles.rs")
    if not os.path.exists(lp(path)):
        return
    src = open(lp(path), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"heracles.rs Params::default() 和 P 不一样（heracles.rs, P）: {bad}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动，刻印按一半一直开着")
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
