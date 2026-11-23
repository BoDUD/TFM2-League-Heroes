"""列奥尼达斯（终末包第十七个英雄 ragnarok_leonidas，辅助，Tank）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_leonidas.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第九回合的人类方代表：斯巴达王，恨透了神，和阿波罗打的那个。神器是瓦尔基里格伊勒鲁尔变的圆盾（阿斯庇斯），能变形，
盾上刻着 Λ。美术、图标、音频是 Codex 的（assets/source/leonidas/，交接说明 assets/source/leonidas/HANDOFF.md），技能照 Codex 的
四个动作做。位置是辅助（用户 2026-11-23 定的，问的时候给的理由：举盾能替队友挡伤害、链盾能拉人、方阵冲锋能开团，辅助位只有雷电、
秦始皇两个）。斯巴达打仗靠方阵，一面盾护着自己也护着旁边的人，所以他的技能都带着身边的队友；控制是拉近和原地击飞（雷电那次的
经验：辅助把人推远，队友就够不着）。
  被动    方阵：他每放一个技能，身边 p_r 里的友方英雄（连他自己）护甲和魔抗 +p_res，p_t 拍。写在普攻说明里（游戏只有三个技能图标位），
          全在数据里。
  attack  盾击 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 5 帧，0.287 秒）砸到。
  skill   链盾：`Targeting` EnemyWithoutTower（q_range）：q_wind 拍抡盾，q_go 拍（第 4 帧，0.237 秒）连着钢链甩出去，q_hit 拍
          （0.285 秒）砸中：q_dmg + q_ad% 攻击力物理伤害、眩晕 q_stun 拍、减速 q_slow% q_slow_t 拍；q_back 拍（第 6 帧，0.336 秒）
          收链，把人往回拽（Pull，每拍 q_pull，q_pull_t 拍），q_catch 拍接回盾。
  skill2  举盾：`Targeting` EnemyWithoutTower（e_range，有人在身边）：e_go 拍（第 3 帧，0.217 秒）举盾，e_t 拍里身边 e_ar 里的友方
          英雄（连他自己）受到的伤害降低 e_adr%，他自己再降低 e_self%、打他的人挨 e_ref% 反伤（引擎的反伤每一下都算），身边 e_tr
          里的敌人被嘲讽 e_taunt 拍（过来打他的盾）；e_reflect 拍
          （第 5 帧，0.354 秒）光箭从盾上弹开（画在他自己的帧里），e_fade 拍收盾。
  ult     方阵冲锋：`Targeting` 敌方英雄（r_range）：起手就不受控制、受到的伤害降低 r_dr%（到撞上为止），r_show 拍（第 3 帧，
          0.305 秒）圆盾换成真理之盾，r_go 拍（第 4 帧，0.423 秒）顶着盾冲过去（RushTime，每拍 r_speed、r_t 拍，碰到人就停），
          r_hit 拍（第 5 帧，0.510 秒）撞上：身边 r_r 里的敌人 r_dmg + r_ad% 攻击力物理伤害、被击飞 r_up 拍（原地）。冲出去之前被
          打死就什么都不发生。

时间按 Codex 的 cues.json 和动画表（一秒 60 拍）：盾击 0.170 秒蓄力、0.236 秒挥盾、0.287 秒砸到，链盾 0.176 / 0.237 / 0.285 /
0.336 / 0.391 秒，举盾 0.217 / 0.354 / 0.502 秒，方阵冲锋 0.305 / 0.423 / 0.510 秒；动作长度盾击 36 拍、链盾 35 拍、举盾 43 拍、
方阵冲锋 56 拍。

ragnarok.dll（addons/ragnarok/src/leonidas.rs）：配音和倒地声（被动 ragnarok_leonidas:voice，没有参数）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_leonidas"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim，辅助 lane 4，600 秒，对手是五个原版辅助），2026-11-23。联盟辅助对照（诺提勒斯 +2.99、
# 洛 +1.21、锤石 +0.58、布隆 -0.07、蕾欧娜 -0.29、阿利斯塔 -0.60，中位数约 +0.25），雷电 +0.42、秦始皇 +0.69。
# 初稿 -2.05（链盾只减速拽人、举盾只减伤，没有硬控：K/D/A 0.6 / 2.0 / 3.6）；链盾砸中眩晕 0.5 秒、举盾嘲讽身边的敌人 0.75 秒
# -0.57；再加血加甲 -0.28，再加链盾和大招的伤害（链盾 60 + 60% -> 80 + 80%、大招 160 + 100% -> 200 + 120%）：
# +0.31 / L3_SECOND（这份）。
P = {
    # 属性（辅助坦克）
    "hp": 1180, "hp_g": 112, "atk": 70, "atk_g": 10, "apw": 0, "apw_g": 0, "def": 48, "def_g": 8, "mr": 34,
    "mr_g": 5, "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 36, "atk_cd": 66, "atk_st": 17,
    # 被动：方阵
    "p_r": 40000, "p_res": 15, "p_t": 180,
    # 链盾
    "q_cd": 600, "q_range": 42000, "q_dur": 35, "q_wind": 11, "q_go": 14, "q_hit": 17, "q_back": 20, "q_catch": 24,
    "q_dmg": 80, "q_ad": 80, "q_stun": 30, "q_slow": 30, "q_slow_t": 60, "q_pull": 1200, "q_pull_t": 8,
    # 举盾
    "e_cd": 720, "e_range": 30000, "e_dur": 43, "e_go": 13, "e_reflect": 21, "e_fade": 30, "e_t": 150, "e_ar": 40000,
    "e_adr": 20, "e_self": 15, "e_ref": 25, "e_tr": 32000, "e_taunt": 45,
    # 方阵冲锋
    "r_cd": 3000, "r_range": 40000, "r_dur": 56, "r_show": 18, "r_go": 25, "r_hit": 31, "r_dr": 40, "r_speed": 6000,
    "r_t": 6, "r_r": 36000, "r_dmg": 200, "r_ad": 120, "r_up": 50,
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


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的列奥尼达斯（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def around(radius, effects):
    """他身边一圈（半径 radius）里的敌人。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def allies(radius, effects):
    """他身边一圈（半径 radius）里的友方英雄，连他自己。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "AllyChampion",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 被动：方阵（放技能时身边的友方英雄加护甲和魔抗）
    phalanx = allies(p["p_r"], [buff("phalanx", p["p_t"], defence=p["p_res"], magic_resistance=p["p_res"])])

    # ------------------------------------------------------------------ 普攻：盾击
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：链盾（砸中、减速，收链把人拽回来）
    stun = {"type": "Stun", "duration": p["q_stun"]} if p["q_stun"] > 0 else None
    struck = combine(attack(p["q_dmg"], p["q_ad"]), stun, buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                     view("a_hit"), tsfx("q_hit"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(phalanx, delayed(p["q_wind"] - 1, sfx("q_wind")),
                           delayed(p["q_go"] - 1, alive_only(sfx("q"))),
                           delayed(p["q_hit"] - 1, alive_only(struck)),
                           delayed(p["q_back"] - 1, alive_only(sfx("q_back"),
                                                               {"type": "Pull", "speed": p["q_pull"], "tick": p["q_pull_t"]})),
                           delayed(p["q_catch"] - 1, alive_only(sfx("q_catch")))))

    # ------------------------------------------------------------------ E：举盾（身边的队友一起减伤，他自己再减一点、反伤）
    taunt = around(p["e_tr"], [{"type": "Taunt", "duration": p["e_taunt"]}]) if p["e_taunt"] > 0 else None
    guard = combine(sfx("e"), flag("e_guard", p["e_t"], damaged_reduce=p["e_self"], damage_reflect=p["e_ref"]),
                    allies(p["e_ar"], [buff("e_wall", p["e_t"], damaged_reduce=p["e_adr"])]), taunt)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(phalanx, delayed(p["e_go"] - 1, alive_only(guard)),
                            delayed(p["e_reflect"] - 1, alive_only(sfx("e_reflect"))),
                            delayed(p["e_fade"] - 1, alive_only(sfx("e_fade")))))

    # ------------------------------------------------------------------ R：方阵冲锋
    charge = {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_t"], "range": 15000,
              "casting_target": "EnemyWithoutTower", "penetrate": False, "applied_effects": []}
    slam = around(p["r_r"], [attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit"),
                             tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(phalanx, flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                         delayed(p["r_show"] - 1, alive_only(sfx("r_show"))),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), charge)),
                         delayed(p["r_hit"] - 1, alive_only(slam))))

    # ------------------------------------------------------------------ 画面
    # 钢弧、飞盘的尾迹、钢链回卷、盾沿的光、反弹的光箭、冲锋的尘土画在他自己的帧里（tools/art/import_leonidas.py）
    E = lambda name, tag, z=2: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": True}
    views_e = [E("a_hit", "shield_hit"), E("r_hit", "phalanx_hit", 3)]
    kit = {
        # Tank 是游戏 0.7.3 才有的定位，经典 SDK 的模拟不认：--plain 写成 Melee（雷电、秦始皇一样）
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
    if is_native:   # ragnarok.dll（addons/ragnarok/src/leonidas.rs）：配音、倒地声
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
