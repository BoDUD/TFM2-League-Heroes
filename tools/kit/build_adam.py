"""亚当（终末包第四个英雄 ragnarok_adam，上路，Melee）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_adam.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第二回合的人类代表，和宙斯打的那个。神虚视：神的动作看一眼就读得出来，躲开，再照着打回去，连宙斯的
超越时间之拳也学了过来。美术、图标、音频是 Codex 的（assets/source/adam/，交接说明 assets/source/adam/README.md），
技能是照 Codex 的提案做的：神虚视读招闪避、模仿反击用掉一次记录、超越时间之拳蓄势后打出。
  被动    神虚视的记录：神虚视（Q）读过一次就记下一招（施法者标记 rec，q_rec 拍），有记录时模仿反击复刻那一招。
          写在普攻说明里（游戏只有三个技能图标位）。
  attack  快拳打 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 4 帧，0.225 秒）出手，拳风画在他的帧里。
  skill   神虚视：`Targeting` 敌方英雄（q_range 内才放，交手时用）：睁眼闪身（动作 q_dur 拍），q_t 拍里普攻打不疼他
          （base_attack_damaged_reduce 100，贾克斯 E 的做法），技能伤害降低 q_sdr%，并记下一招（rec，q_rec 拍）。
          闪避结束时眼睛吃力（只是声音）。
  skill2  复刻·黄昏流星群（模仿反击）：`Targeting` EnemyWithoutTower（e_range）：e_hit 拍（0.235 秒）一拳 e_dmg + e_ad% 攻击力物理伤害；
          有记录时复刻那一招：再加 e_cdmg 和目标最大生命 e_hp% 的伤害、眩晕 e_stun 拍，用掉记录。
  ult     超越时间之拳：`Targeting` 敌方英雄（r_range）：r_go 拍蓄势（不受控制、减伤 r_dr%），然后朝目标打出一条
          长 r_len、宽 r_w 的拳劲：r_dmg + r_ad% 攻击力物理伤害，击飞 r_up 拍。蓄势时被打死就不出拳。

时间按 Codex 的 cues.json（一秒 60 拍）：普攻 0.225 秒、闪避 0.17 秒、反击 0.235 秒、时间之拳 0.43 秒出手。

ragnarok.dll（addons/ragnarok/src/adam.rs）：被动 ragnarok_adam:voice，只管配音和倒地声。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_adam"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，上路，600 秒，每批 288 局，击杀差的标准误约 ±0.4），2026-11-21，对手和吕布、宙斯同一套
# （基础战士和另外五个原版上单；吕布 +1.48 / +1.38，联盟战士的中位数约 +1.44）。初稿 -3.30 / -2.02：伤害打不出来（6811 对
# 对手 9331）、死得多，神虚视一局才放 12 次。加属性 -1.95、神虚视更常用 -2.51、加伤害 -2.03，三样一起 +0.05；在那上面
# 普攻更快 +0.07、神虚视加攻速 +0.20、反击更常用 +0.26，更耐打 +0.99（和宙斯一样，耐打最管用）；耐打加反击 +0.85 / +1.20，
# 再耐打一些 +1.42 / +1.68（偏强），耐打加攻击力（这份 P）+1.32 / +1.44（K/D/A 约 2.4 / 0.9 / 3.8，一局普攻 170、反击 47、
# 神虚视 21、超越时间之拳 6 次）。
P = {
    # 属性（上路战士）：人类，靠躲和反击，身子要扛得住
    "hp": 1400, "hp_g": 110, "atk": 100, "atk_g": 18, "apw": 0, "apw_g": 0, "def": 46, "def_g": 8, "mr": 30,
    "mr_g": 4, "ms": 1040, "ms_g": 11,
    "atk_range": 25000, "atk_dur": 35, "atk_cd": 58, "atk_st": 14,
    # 神虚视
    "q_cd": 420, "q_range": 40000, "q_dur": 36, "q_t": 150, "q_sdr": 50, "q_rec": 300,
    # 模仿反击
    "e_cd": 300, "e_range": 27000, "e_dur": 37, "e_hit": 14, "e_dmg": 70, "e_ad": 100, "e_cdmg": 60, "e_hp": 8,
    "e_stun": 60,
    # 超越时间之拳
    "r_cd": 2400, "r_range": 30000, "r_dur": 47, "r_go": 26, "r_dr": 50, "r_w": 14000, "r_len": 50000,
    "r_dmg": 220, "r_ad": 150, "r_up": 48,
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
    """Delayed 里的效果只给活着的亚当（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 普攻：快拳
    jab = combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", jab,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：神虚视
    read = flag("eye", p["q_t"], base_attack_damaged_reduce=100, skill_damaged_reduce=p["q_sdr"])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyChampion",
                   combine(read, flag("rec", p["q_rec"]), sfx("q"), delayed(9, sfx("q_dodge")),
                           delayed(p["q_t"], sfx("q_strain"))))

    # ------------------------------------------------------------------ E：模仿反击
    plain = combine(attack(p["e_dmg"], p["e_ad"]), sfx("e"), tsfx("e_hit"))
    copy = combine(unflag("rec"), attack(p["e_dmg"] + p["e_cdmg"], p["e_ad"], p["e_hp"]),
                   {"type": "Stun", "duration": p["e_stun"]}, sfx("e"), tsfx("e_hit"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(delayed(5, sfx("e_mark")), delayed(p["e_hit"] - 1, when("rec", copy, plain))))

    # ------------------------------------------------------------------ R：超越时间之拳
    line = {"type": "LineRangeProjectile", "name": n("r_line"), "width": p["r_w"], "length": p["r_len"], "delay": 2,
            "apply": 1, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in
                                (attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]},
                                 view("r_hit"), tsfx("r_hit"))]}
    guard = flag("guard", p["r_go"] + 2, cc_immune=True, damaged_reduce=p["r_dr"])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(guard, delayed(2, sfx("r_charge")), delayed(p["r_go"] - 1, alive_only(sfx("r"), line))))

    # ------------------------------------------------------------------ 画面
    # 拳风、睁眼、闪避气流、模仿标记、反击火花、时间之拳都画在他自己的帧里（tools/art/import_adam.py），这里只有打在人身上的火花
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "jab_hit"), E("r_hit", "jab_hit", 3)]
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/adam.rs）：配音，规则全在数据里
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
