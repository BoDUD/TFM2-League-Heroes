"""澜缇（边境巡团 border_lanti，战士，上路）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_lanti.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

反击型的战士，翠绿拳套。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    折纹：只标记最近一个用技能伤到她的敌方英雄（border_lanti_mark，p_t 拍；换人就摘掉旧的），他身上裂开一道镜纹。
          怎么算「用技能」：伤到她的那一刻他正在放技能（施法动作还在播），或者技能刚进冷却（p_window 拍内）。
  attack  一拳 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）打到。
  skill   双棱：`Targeting` EnemyWithoutTower（q_range）：q_hit1 拍第一拳 q1_dmg + q1_ad%，q_hit2 拍（第 3 帧）第二拳 q2_dmg +
          q2_ad%（物理伤害）；第二拳打到带镜纹的人，镜纹用掉，这一拳 +q_mark%、减速 q_slow%。每一拳实际打中才在他身上
          亮一下拳光。
  skill2  候击：`Targeting` 敌方英雄（e_range，交战时才放）：e_hit 拍起架（e_t 拍，受到的技能伤害降低 e_dr%）；架着的时候
          挨了一下技能就算成功：架子收起，双棱的冷却刷新，挡下的伤害记进还响。
  ult     还响：`Targeting` 敌方英雄（r_range）：r_hit 拍（第 3 帧，0.40 秒）朝目标推出一道玻璃波（直线弹道，长 r_len、宽
          r_w，速度 r_speed，穿过去每人一下）：r_dmg + r_ad% 攻击力，加上最近 r_window 拍里她挡下的伤害（候击挡的、
          减伤减掉的）的 r_k%，最多加 r_cap；减速 r_slow% r_slow_t 拍。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、双棱 / 候击 0.56 秒（第 3 帧 0.26 秒）、还响 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/lanti.rs）：被动 border_lanti:fracture（折纹、候击的成功、挡下的伤害），原生效果
border_lanti:prism1 / prism2 / guard / echo / echo_hit。--plain 和塞拉斯版：第二拳按平均加成算，还响是一条数据的直线弹道；
--plain 的双棱冷却是 q_cd_sim（候击刷新双棱的平均效果）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_lanti"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh lanti 0 ...，上路 lane 0，600 秒，对手是六个原版上单，8 个种子），2026-11-22。
# 联盟上单对照（鳄鱼 +2.15、剑魔 +2.10、瑟提 +2.07、贾克斯 +1.51、诺手 +1.50、盖伦 -0.09，中位数约 +1.6）。初稿 -2.11，加两拳
# 和还响的伤害、攻击力、血 -1.31 / -0.20，数据版的双棱冷却按候击刷新的平均算短一截（q_cd_sim）、再加攻击成长和护甲（这份）+1.26。
P = {
    # 属性（战士）
    "hp": 1200, "hp_g": 108, "atk": 115, "atk_g": 22, "apw": 0, "apw_g": 0, "def": 44, "def_g": 8, "mr": 28,
    "mr_g": 4, "ms": 1010, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 62, "atk_st": 13,
    # 被动：折纹
    "p_t": 300, "p_window": 30,
    # 双棱
    "q_cd": 360, "q_range": 26000, "q_dur": 34, "q_hit1": 9, "q_hit2": 16, "q1_dmg": 50, "q1_ad": 80, "q2_dmg": 80,
    "q2_ad": 130, "q_mark": 60, "q_slow": 20, "q_slow_t": 45,
    # 候击
    "e_cd": 480, "e_range": 40000, "e_dur": 34, "e_hit": 8, "e_dr": 50, "e_t": 150,
    # 还响
    "r_cd": 3000, "r_range": 40000, "r_dur": 52, "r_hit": 24, "r_len": 45000, "r_w": 16000, "r_speed": 6000,
    "r_dmg": 260, "r_ad": 160, "r_k": 60, "r_cap": 300, "r_window": 480, "r_slow": 30, "r_slow_t": 60,
    # 只给平衡模拟（--plain）：第二拳平均加成多少、还响平均多出多少、双棱的冷却（原版候击架住一下就刷新双棱，数据版没有，
    # 冷却按平均算短一截）
    "q_mark_sim": 40, "r_bonus_sim": 150, "q_cd_sim": 300,
}

NATIVE = ["p_t", "p_window", "q1_dmg", "q1_ad", "q2_dmg", "q2_ad", "q_mark", "q_slow", "q_slow_t", "e_dr", "e_t",
          "r_len", "r_w", "r_speed", "r_dmg", "r_ad", "r_k", "r_cap", "r_window", "r_slow", "r_slow_t"]


def plain_echo(p, bonus):
    """数据版的还响：朝目标一条穿透的直线弹道（画面 r_wave，跟着方向转）。"""
    return {"type": "LinearProjectile", "name": kit.n("r_wave"), "speed": p["r_speed"], "range": p["r_len"],
            "penetrate": True, "shape": {"Circle": {"radius": p["r_w"] // 2}}, "y_offset": 0,
            "applied_target": "EnemyWithoutTower", "end_effects": [],
            "applied_effects": [{"casting_type": "Targeting",
                                 "effect": K.combine(K.attack(p["r_dmg"] + bonus, p["r_ad"]),
                                                     kit.slow("r_slow", p["r_slow"], p["r_slow_t"]))}]}


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(K.attack(0, 100), {"type": "Sfx", "name": "gladiator_attack"}, kit.view("a_hit")),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：双棱（两拳）
    if is_native:
        first, second = kit.native("prism1"), kit.native("prism2")
    else:
        first = K.combine(K.attack(p["q1_dmg"], p["q1_ad"]), kit.view("q_punch"))
        m = 100 + p["q_mark_sim"]
        second = K.combine(K.attack(p["q2_dmg"] * m // 100, p["q2_ad"] * m // 100),
                           kit.slow("q_slow", p["q_slow"], p["q_slow_t"]), kit.view("q_punch"))
    skill = kit.action("skill", p["q_dur"], p["q_cd"] if is_native else p["q_cd_sim"], 1, p["q_range"], "Targeting",
                       "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "gladiator_attack_hit"},
                                 K.delayed(p["q_hit1"] - 1, kit.alive_only(first)),
                                 K.delayed(p["q_hit2"] - 1, kit.alive_only(second))))

    # ------------------------------------------------------------------ E：候击
    guard = kit.native("guard") if is_native else kit.flag("e_guard", p["e_t"], skill_damaged_reduce=p["e_dr"])
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "magic_knight_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(guard))))

    # ------------------------------------------------------------------ R：还响
    echo = kit.native("echo") if is_native else plain_echo(p, p["r_bonus_sim"])
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "gladiator_ult_hit"},
                               K.delayed(p["r_hit"] - 1, kit.alive_only(echo))))

    # ------------------------------------------------------------------ 画面
    # 拳光朝右画的；她往左打时 border.dll 放左右翻过的 q_punch_l
    views_e = kit.views([("a_hit", "a_hit"), ("hit", "hit"), ("p_mark", "p_mark"), ("q_punch", "q_punch"),
                         ("q_punch_l", "q_punch_l"), ("e_guard", "e_guard")])
    views_p = kit.projectile_views([("r_wave", "r_wave"), ("r_wave_l", "r_wave_l")])
    stat, growth = K.stats(p)
    tags = ["AD", "Melee"]
    if not is_native:
        return kit.shell("Melee", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Melee", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="fracture",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的还响（STOLEN）：他没挡下什么（按 0 算），一道玻璃波朝目标推出去。纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    return K.combine({"type": "Sfx", "name": "gladiator_ult_hit"},
                     K.delayed(p["r_hit"] - 1, kit.alive_only(plain_echo(p, 0))))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
