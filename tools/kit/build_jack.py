"""开膛手杰克（终末包第八个英雄 ragnarok_jack，下路，Range）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_jack.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第四回合的人类方选手，和赫拉克勒斯打的那个：伦敦的绅士，看得见人心的颜色，戴着能把碰到的东西都变成神器的
手套「Dear God」。美术、图标、音频是 Codex 的（assets/source/jack/，交接说明 assets/source/jack/HANDOFF.md），技能照 Codex
的四个动作做：
  被动    心之色：他看得见人心的颜色，恐惧藏不住：对生命低于 p_hp% 的敌方英雄，普攻和技能的伤害 +p_dmg%
          （ragnarok.dll 改每一下的伤害）。写在普攻说明里（游戏只有三个技能图标位）。--plain 给平衡模拟用：模拟跑不了 DLL，
          攻击力一直 +p_dmg / 2 %（差不多一半的时候对手是低血）。
  attack  飞刀打 `Enemy`（塔也打）：atk_st 拍（第 4 帧，0.237 秒）出手，一把飞刀（a_speed）追着目标飞，打到 100% 攻击力。
  skill   扇形飞刀：`Targeting` EnemyWithoutTower（q_range）：q_go 拍（第 4 帧）一扇飞刀出手，q_hit 拍（第 6 帧）前方扇形
          （半径 q_r，左右各 acos(q_cone/1000)）里的敌人 q_dmg + q_ad% 攻击力物理伤害、减速 q_slow% q_slow_t 拍。
  skill2  伦敦之雾：`Targeting` 敌方英雄（e_range，有人贴上来）：e_open 拍（第 3 帧）撑开被手套变成神器的伞，到收伞
          （e_close 拍）受到的伤害降低 e_dr%；e_back_go 拍（第 4 帧）往后退（e_back 速度 e_back_t 拍）进雾里，隐身 e_inv 拍，
          之后 e_as_t 拍攻速 +e_as%。
  ult     亲爱的神（Dear God）：`Targeting` 敌方英雄（r_range）：r_glint 拍（第 2 帧）单片镜后的眼睛看穿对方（对方身上
          一道异色的光），r_touch 拍（第 4 帧）手套碰过的刀成了神器，飞出去（r_speed），打到 r_dmg + r_ad% 攻击力物理
          伤害，之后 r_t 拍里对方受到的伤害增加 r_amp%（谁打都算）。出手前被打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：普攻 0.237 秒出手，扇形飞刀 0.286 秒出手、0.392 秒打到，伦敦之雾 0.194 秒
撑伞、0.267 秒后撤、0.484 秒收伞，亲爱的神 0.14 秒看穿、0.346 秒触物；动作长度普攻 36 拍、扇形飞刀 41 拍、伦敦之雾
43 拍、亲爱的神 48 拍。飞刀从他手的高度出去（y_offset：出手那一帧手在脚底上 86 格 = 26 个游戏像素，枢轴在脚底上 11.5，
弹道从枢轴往北 5000 - y_offset）。

ragnarok.dll（addons/ragnarok/src/jack.rs）：被动 ragnarok_jack:colour，参数取 P 里的 p_hp / p_dmg；配音和倒地声。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_jack"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
PROJ = f"asset/{MOD_ID}/effects/{ID}_proj"

# 单位：1 个游戏像素 1000；一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，下路 lane 3，600 秒，对手是四个原版射手，每批种子 192 局，8 个种子的击杀差标准误
# 约 ±0.5），2026-11-21。联盟射手在这套对局里：金克丝 +5.57、伊泽瑞尔 +3.02、女警 +2.73、卡莎 +2.62、薇恩 +2.40、
# 艾希 +2.10（中位数约 +2.7）。初稿 -1.88（攻击 92、普攻 36 拍第 14 拍出手、射程 5.6 万）；照联盟射手的底子（攻击
# 100 + 20、普攻短、射程 6 万）-0.06，加技能伤害 +1.53 / +1.09；加血加甲反而更弱（+0.28），E 放远（一局只放三次，
# 放远也就五次）也不更强；射程 6.5 万、22 拍的普攻、被动 30% +1.89 / +1.59（第 4 拍出手）、+1.85（第 9 拍出手，
# 对上动画里甩刀那一帧，就用这个），再加 Q 伤害（这份 P）+2.33 / +1.67，Q 再加一档 16 个种子 +1.88（不更强）。
P = {
    # 属性（下路射手）：绅士身板单薄，手长
    "hp": 900, "hp_g": 90, "atk": 100, "atk_g": 20, "apw": 0, "apw_g": 0, "def": 20, "def_g": 6, "mr": 15,
    "mr_g": 3, "ms": 930, "ms_g": 9,
    # 普攻动画 607 毫秒、甩刀在第 4 帧（39% 处）：22 拍的动作第 9 拍出手
    "atk_range": 65000, "atk_dur": 22, "atk_cd": 60, "atk_st": 9, "a_speed": 9000, "a_y": -9500,
    # 被动：心之色（ragnarok.dll）
    "p_hp": 50, "p_dmg": 30,
    # 扇形飞刀
    "q_cd": 420, "q_range": 52000, "q_dur": 41, "q_go": 17, "q_hit": 24, "q_r": 58000, "q_cone": 820,
    "q_dmg": 80, "q_ad": 105, "q_slow": 25, "q_slow_t": 60,
    # 伦敦之雾
    "e_cd": 780, "e_range": 30000, "e_dur": 43, "e_open": 12, "e_close": 29, "e_dr": 40,
    "e_back_go": 16, "e_back": 3500, "e_back_t": 10, "e_inv": 90, "e_as": 40, "e_as_t": 180,
    # 亲爱的神
    "r_cd": 2700, "r_range": 62000, "r_dur": 48, "r_glint": 8, "r_touch": 21, "r_speed": 14000,
    "r_dmg": 200, "r_ad": 180, "r_amp": 20, "r_t": 240,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/jack.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_hp", "p_dmg")


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


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的杰克（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def knife(name, speed, y, effects):
    """追着目标飞的一把刀，打到时对目标放 effects。"""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": "Enemy",
            "applied_effects": [{"casting_type": "Targeting", "effect": combine(*effects)}]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain：心之色按一半算，攻击力一直加着（模拟跑不了 ragnarok.dll）
    plain = None if is_native else when(
        "p_on", combine(), combine(flag("p_on", None), flag("p_colour", None, attack_mult=p["p_dmg"] // 2)))

    # ------------------------------------------------------------------ 普攻：飞刀
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(plain, sfx("a"), knife("a_knife", p["a_speed"], p["a_y"],
                                                     [attack(0, 100), view("a_hit"), tsfx("a_hit")])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：扇形飞刀
    fan = cone(p["q_r"], p["q_cone"], [attack(p["q_dmg"], p["q_ad"]), buff("q_slow", p["q_slow_t"],
                                                                         move_speed_mult=-p["q_slow"]),
                                       view("q_hit")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_go"] - 1, sfx("q")), delayed(p["q_hit"] - 1, fan, tsfx("q_hit"))))

    # ------------------------------------------------------------------ E：伦敦之雾
    umbrella = flag("e_guard", p["e_close"] - p["e_open"] + 1, damaged_reduce=p["e_dr"])
    retreat = combine({"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]},
                      search_self({"type": "CasterInvisible", "tick": p["e_inv"]}),
                      flag("e_haste", p["e_inv"] + p["e_as_t"], attack_speed_mult=p["e_as"]), sfx("e_back"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(delayed(p["e_open"] - 1, sfx("e"), umbrella),
                            delayed(p["e_back_go"] - 1, alive_only(retreat)),
                            delayed(p["e_close"] - 1, sfx("e_close"))))

    # ------------------------------------------------------------------ R：亲爱的神
    divine = knife("r_knife", p["r_speed"], p["a_y"],
                   [attack(p["r_dmg"], p["r_ad"]), buff("r_mark", p["r_t"], damaged_amplify=p["r_amp"]), view("r_hit"),
                    tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(delayed(p["r_glint"] - 1, sfx("r1"), view("r_glint")),
                         delayed(p["r_touch"] - 1, alive_only(sfx("r2"), divine))))

    # ------------------------------------------------------------------ 画面
    # 扇形飞刀、护弧、雾、手套触物画在他自己的帧里（tools/art/import_jack.py）；飞出去的刀是 ragnarok_jack_proj（1 倍，
    # 跟着飞行方向转）；打在人身上的是命中、收招和那道异色的光
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    Pj = lambda name, tag: {"type": "Animated", "name": n(name), "anim": PROJ, "tag": tag, "repeat": True, "z": 1}
    views_e = [E("a_hit", "knife_hit"), E("q_hit", "knife_hit"), E("r_glint", "emotion_glint", 3),
               E("r_hit", "dear_god")]
    views_p = [Pj("a_knife", "knife_flight"), Pj("r_knife", "knife_flight")]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/jack.rs）：心之色、配音
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:colour", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def check_dll(p):
    """addons/ragnarok/src/jack.rs 的 Params::default() 和 P 里 DLL 读的那几个一样（DLL 读 passive.params，默认值是退路）。"""
    import re
    path = os.path.join(REPO, "addons", "ragnarok", "src", "jack.rs")
    if not os.path.exists(lp(path)):
        return
    src = open(lp(path), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"jack.rs Params::default() 和 P 不一样（jack.rs, P）: {bad}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动，心之色按一半一直开着")
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
