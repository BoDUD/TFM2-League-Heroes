"""鹭芯（边境巡团 border_luxin，刺客，打野）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_luxin.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

追击型的刺客，翠羽。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    追羽：被她打过（p_window 拍内）的敌方英雄还在离她越走越远，每 p_every 拍在他脚下留一段羽迹（他逃的方向记在他
          身上：border_luxin_trail_<方向>，p_t 拍，最多两段）。贴风、收线顺着羽迹追。
  attack  一刀 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）打到。
  skill   贴风：`Targeting` EnemyWithoutTower（q_range）：出手就顺着目标逃的方向（有羽迹按羽迹，没有就直冲）追过去，提前
          q_lead，冲到离他 q_stop 处（强制位移，速度 q_speed）；q_hit 拍（第 3 帧）切他 q_dmg + q_ad% 攻击力物理伤害。
          风痕画在她自己的帧里。
  skill2  折鸢：`Targeting` 敌方英雄（e_range）：e_hit 拍在目标脚下横着拉一道风线（和他逃的方向垂直，长 e_len，e_t 拍）；
          之后哪个敌人穿过这道线，就吃 e_dmg + e_ad% 攻击力、减速 e_slow% e_slow_t 拍（每人每条线一次）。
  ult     收线：`Targeting` 敌方英雄（r_range）：第 3 帧（r_cut1 拍）顺着目标的第一段羽迹（没有就从她这边）穿过他切第一刀，
          r_cut2 拍顺着第二段羽迹（没有就反方向）穿回来切第二刀；每刀 r_dmg + r_ad% 攻击力，第二刀按他已经掉的生命比例
          加成（最多 +r_low%），他身上每段羽迹再 +r_trail%。每一刀沿实际冲的方向亮一道切光。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、贴风 / 折鸢 0.56 秒（第 3 帧 0.26 秒）、收线 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/luxin.rs）：被动 border_luxin:feather（追羽、风线的穿越），原生效果 border_luxin:cling /
cling_hit / kite / reel1 / reel2 / noop。--plain 和塞拉斯版：冲刺换成 MoveToTarget，收线是两次 RushMoveToBack 加伤害。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_luxin"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh luxin 1 ...，打野 lane 1，600 秒，对手是五个原版打野），2026-11-22。
# 联盟打野对照（蔚 +2.21、李青 +1.98、瑟庄妮 +1.88、狼人 +0.57、扎克 +0.41、人马 -0.38，中位数约 +1.2）。初稿就到了：种子 1-8
# +1.02、9-16 +1.24，没改。顺着羽迹追、收线顺着羽迹切只在 border.dll 里，模拟里是直冲、直切。
P = {
    # 属性（刺客）
    "hp": 950, "hp_g": 90, "atk": 120, "atk_g": 27, "apw": 0, "apw_g": 0, "def": 26, "def_g": 7, "mr": 18, "mr_g": 3,
    "ms": 1090, "ms_g": 12,
    "atk_range": 23000, "atk_dur": 28, "atk_cd": 52, "atk_st": 13,
    # 被动：追羽
    "p_window": 240, "p_away": 300, "p_t": 240, "p_every": 30,
    # 贴风
    "q_cd": 360, "q_range": 50000, "q_dur": 34, "q_hit": 16, "q_lead": 8000, "q_speed": 4500, "q_stop": 12000,
    "q_dmg": 80, "q_ad": 130, "q_hit_r": 30000,
    # 折鸢
    "e_cd": 600, "e_range": 60000, "e_dur": 34, "e_hit": 16, "e_len": 40000, "e_t": 240, "e_slow": 40,
    "e_slow_t": 90, "e_dmg": 40, "e_ad": 60,
    # 收线
    "r_cd": 3000, "r_range": 45000, "r_dur": 52, "r_cut1": 24, "r_cut2": 40, "r_through": 18000, "r_speed": 6000,
    "r_dmg": 120, "r_ad": 100, "r_low": 60, "r_trail": 20,
}

NATIVE = ["p_window", "p_away", "p_t", "p_every", "q_lead", "q_speed", "q_stop", "q_dmg", "q_ad", "q_hit_r", "q_dur",
          "e_len", "e_t", "e_slow", "e_slow_t", "e_dmg", "e_ad", "r_through", "r_speed", "r_dmg", "r_ad", "r_low",
          "r_trail"]


def plain_reel(p, first):
    """数据版的一刀：穿过目标冲到他身后（RushMoveToBack），碰到他时切；第二刀伤害按平均加 30%。"""
    m = 100 if first else 130
    return {"type": "RushMoveToBack", "speed": p["r_speed"],
            "applied_effects": [K.combine(K.attack(p["r_dmg"] * m // 100, p["r_ad"] * m // 100), kit.view("a_hit"))]}


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(K.attack(0, 100), {"type": "Sfx", "name": "ninja_attack"}, kit.view("a_hit")),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：贴风
    if is_native:
        cling = K.combine(kit.native("cling"), K.delayed(p["q_hit"] - 1, kit.alive_only(kit.native("cling_hit"))))
    else:
        cling = {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"],
                 "end_effects": [K.attack(p["q_dmg"], p["q_ad"]), kit.view("a_hit")]}
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "ninja_skill2_dash"}, cling))

    # ------------------------------------------------------------------ E：折鸢
    if is_native:
        kite = kit.native("kite")
    else:
        kite = K.combine(K.attack(p["e_dmg"], p["e_ad"]), kit.slow("e_slow", p["e_slow"], p["e_slow_t"]))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "whip_master_skill1"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(kite))))

    # ------------------------------------------------------------------ R：收线（两刀）
    if is_native:
        cuts = [K.delayed(p["r_cut1"] - 1, kit.alive_only(kit.native("reel1"))),
                K.delayed(p["r_cut2"] - 1, kit.alive_only(kit.native("reel2")))]
    else:
        cuts = [K.delayed(p["r_cut1"] - 1, kit.alive_only(plain_reel(p, True))),
                K.delayed(p["r_cut2"] - 1, kit.alive_only(plain_reel(p, False)))]
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "ninja_ult_attack"}, *cuts))

    # ------------------------------------------------------------------ 画面
    views_e = kit.views([("a_hit", "a_hit"), ("hit", "hit")])
    views_e += kit.views([("p_feather", "p_feather")], follow=False)
    views_p = kit.projectile_views([("e_kite_r", "e_kite_r"), ("e_kite_l", "e_kite_l"), ("r_cut_r", "r_cut_r"),
                                    ("r_cut_l", "r_cut_l")], once=("e_kite_r", "e_kite_l", "r_cut_r", "r_cut_l"))
    stat, growth = K.stats(p)
    tags = ["AD", "Melee"]
    if not is_native:
        return kit.shell("Assassin", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Assassin", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="feather",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的收线（STOLEN）：没有羽迹，两次穿过目标各切一刀（第二刀按平均加成）。纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    return K.combine({"type": "Sfx", "name": "ninja_ult_attack"},
                     K.delayed(p["r_cut1"] - 1, kit.alive_only(plain_reel(p, True))),
                     K.delayed(p["r_cut2"] - 1, kit.alive_only(plain_reel(p, False))))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
