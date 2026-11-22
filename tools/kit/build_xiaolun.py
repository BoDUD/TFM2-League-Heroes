"""绡轮（边境巡团 border_xiaolun，射手，下路）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_xiaolun.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

薄荷蓝头发的潮弩信使，边走边射的射手。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    走弦：按她实际走过的距离上弦（每走 p_full / 10 一层，十层满），满了弦绷紧（border_xiaolun_taut），下一发普攻
          多 p_dmg + p_ad% 攻击力的物理伤害并减速 p_slow% p_slow_t 拍。被击退、自己侧移也算走过的路，一 tick 跳得太远
          （复活、传送）不算。border.dll 记账（addons/border/src/xiaolun.rs），层数是她身上的 border_xiaolun_tension。
  attack  弩箭 `Enemy`：弹道（a_speed）打中 100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）放出去。弦绷紧时这一箭带着上面的
          加成，打中才把弦放掉（放掉的效果在弹道里，不在出手时：champion-data 第 3 节，出手时动自己会让 AI 少打普攻）。
  skill   切角：`Targeting` EnemyWithoutTower（q_range）：一出手就朝目标的侧面短移 q_step（q_step_t 拍的强制位移，碰到墙
          就停：只走得通的路），挑离别的敌方英雄远的那一边；q_shot 拍（第 3 帧，0.26 秒）朝目标射一箭：q_dmg + q_ad%
          攻击力物理伤害。侧移的路也上弦。
  skill2  放扣：`Targeting` 敌方英雄（e_range，交战时才放）：e_hit 拍把弦上的张力全放掉，换 e_t 拍攻速 +e_as% 再加每层
          +e_as_k%（满弦 +e_as + 10 x e_as_k）。弦绷紧也一起放掉。
  ult     满弧：`Targeting` 敌方英雄（r_range）：第 3 帧起 r_shot1 拍、再隔 r_gap、r_gap 拍各放一支星弧箭，每支在放的那一刻
          重新挑目标：原来的目标还活着、选得中、在 r_reach 内就射他，不然射 r_reach 内生命比例最低的敌方英雄，再不然最近
          的敌方单位；每支 r_dmg + r_ad% 攻击力物理伤害。被控住的那一下不放。箭飞出去以后是普通的弹道。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、切角 / 放扣 0.56 秒（第 3 帧 0.26 秒）、满弧 0.87 秒（第 3 帧
0.40 秒）。

border.dll（addons/border/src/xiaolun.rs）：被动 border_xiaolun:string（走弦、配音），原生效果 border_xiaolun:sidestep /
latch / arc / arc_hit。--plain 给平衡模拟：经典引擎跑不了 border.dll，走弦按每 p_share_sim% 的普攻带加成算，侧移换成
后跳，放扣按一半的弦，满弧三支随机挑敌方英雄。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_xiaolun"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh xiaolun 3 ...，下路 lane 3，600 秒，对手是四个原版射手，8 个种子），2026-11-22。
# 联盟下路对照（金克丝 +5.57、伊泽瑞尔 +3.02、女警 +2.73、卡莎 +2.62、薇恩 +2.40、艾希 +2.10，中位数约 +2.6）。初稿 +0.54，加攻击、
# 射程、切角、放扣和满弧 +2.05，普攻快一点（这份）+2.01；再快到 55、满弦按四成算 +3.65（太强）。满弧每支重新挑目标只在
# border.dll 里，模拟里随机挑。
P = {
    # 属性（射手，原版射手 hp 900 / 攻击 100 左右）
    "hp": 880, "hp_g": 88, "atk": 100, "atk_g": 20, "apw": 0, "apw_g": 0, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3,
    "ms": 1000, "ms_g": 10,
    "atk_range": 62000, "atk_dur": 28, "atk_cd": 57, "atk_st": 13, "a_speed": 7000,
    # 被动：走弦
    "p_full": 100000, "p_dmg": 40, "p_ad": 60, "p_slow": 20, "p_slow_t": 60,
    # 切角
    "q_cd": 480, "q_range": 60000, "q_dur": 34, "q_shot": 16, "q_step": 18000, "q_step_t": 12, "q_dmg": 50,
    "q_ad": 130, "q_speed": 8000,
    # 放扣
    "e_cd": 600, "e_range": 62000, "e_dur": 34, "e_hit": 16, "e_as": 35, "e_as_k": 5, "e_t": 180,
    # 满弧
    "r_cd": 3000, "r_range": 70000, "r_dur": 52, "r_shot1": 24, "r_gap": 8, "r_reach": 78000, "r_dmg": 120,
    "r_ad": 90, "r_speed": 9000,
    # 只给平衡模拟（--plain）：多少普攻算带着满弦
    "p_share_sim": 30,
}

NATIVE = ["p_full", "q_step", "q_step_t", "q_dur", "e_as", "e_as_k", "e_t", "r_reach", "r_dmg", "r_ad", "r_speed"]


def bolt(name, speed, effects):
    return {"type": "TargetProjectile", "name": kit.n(name), "speed": speed, "y_offset": -1800,
            "applied_target": "Enemy",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(*effects)}]}


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：弩箭（满弦那一箭打中才放弦）
    plain_hit = [K.attack(0, 100), kit.view("a_hit")]
    taut_hit = [K.attack(p["p_dmg"], 100 + p["p_ad"]), kit.slow("p_slow", p["p_slow"], p["p_slow_t"]),
                kit.unflag("taut"), kit.view("a_hit")]
    if is_native:
        shot = kit.when("taut", bolt("a_bolt", p["a_speed"], taut_hit), bolt("a_bolt", p["a_speed"], plain_hit))
    else:
        s = p["p_share_sim"]
        shot = bolt("a_bolt", p["a_speed"], [K.attack(p["p_dmg"] * s // 100, 100 + p["p_ad"] * s // 100),
                                              kit.view("a_hit")])
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(shot, {"type": "Sfx", "name": "crossbowman_attack"}),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：切角（侧移的拖影画在她自己的帧里）
    step = kit.native("sidestep") if is_native else {"type": "MoveBack", "speed": p["q_step"] // p["q_step_t"],
                                                       "tick": p["q_step_t"]}
    q_bolt = bolt("a_bolt", p["q_speed"], [K.attack(p["q_dmg"], p["q_ad"]), kit.view("a_hit")])
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine(step, {"type": "Sfx", "name": "crossbowman_skill1"},
                                 K.delayed(p["q_shot"] - 1, kit.alive_only(q_bolt))))

    # ------------------------------------------------------------------ E：放扣（扣环碎开的光画在她自己的帧里）
    if is_native:
        latch = kit.native("latch")
    else:
        latch = kit.flag("latch_as", p["e_t"], attack_speed_mult=p["e_as"] + 5 * p["e_as_k"])
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "gunner_skill2_on"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(latch))))

    # ------------------------------------------------------------------ R：满弧（三支星弧箭，每支放的时候重新挑目标）
    shots = []
    for k in range(3):
        t = p["r_shot1"] + k * p["r_gap"]
        if is_native:
            one = kit.native("arc")
        else:
            one = {"type": "RandomTarget", "range": p["r_reach"], "casting_target": "EnemyChampion",
                   "from_projectile": False,
                   "effects": [bolt("r_arrow", p["r_speed"], [K.attack(p["r_dmg"], p["r_ad"]), kit.view("a_hit")])]}
        shots.append(K.delayed(t - 1, kit.alive_only(one, {"type": "Sfx", "name": "crossbowman_ult"})))
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", K.combine(*shots))

    # ------------------------------------------------------------------ 画面
    # 打中的碎光、满弦时弩上绕起的玻璃环（tools/art/import_xiaolun.py）；飞出去的弩箭、星弧箭是弹道画面
    views_e = kit.views([("a_hit", "a_hit"), ("p_ring", "p_ring")])
    views_p = kit.projectile_views([("a_bolt", "a_bolt"), ("r_arrow", "r_arrow")])
    stat, growth = K.stats(p)
    tags = ["AD", "Range"]
    if not is_native:
        return kit.shell("Range", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Range", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="string",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的满弧（STOLEN）：三支星弧箭，第一支射他选的目标，后两支在射出的那一刻从 r_reach 内的敌方英雄里重新挑
    （纯数据只能随机挑，border.dll 的版本挑原目标、生命比例最低的）。不靠 border.dll。"""
    p = dict(P) if p is None else p
    arrow = bolt("r_arrow", p["r_speed"], [K.attack(p["r_dmg"], p["r_ad"]), kit.view("a_hit")])
    again = {"type": "RandomTarget", "range": p["r_reach"], "casting_target": "EnemyChampion", "from_projectile": False,
             "effects": [bolt("r_arrow", p["r_speed"], [K.attack(p["r_dmg"], p["r_ad"]), kit.view("a_hit")])]}
    shots = []
    for k, one in enumerate((arrow, again, again)):
        t = p["r_shot1"] + k * p["r_gap"]
        shots.append(K.delayed(t - 1, kit.alive_only(one, {"type": "Sfx", "name": "crossbowman_ult"})))
    return K.combine(*shots)


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
