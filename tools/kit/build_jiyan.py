"""霁砚（边境巡团 border_jiyan，法师，中路）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_jiyan.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

远程炮台型的法师，拿着六分仪。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    定标：长刻打中的地方（第一个被打中的敌方英雄脚下，没有就是长刻的末端）留一个坐标（border_jiyan_mark_<x>_<y>，
          p_t 拍，最多 p_max 个），地上亮着星图记号。
  attack  星针 `Enemy`：弹道（a_speed）打中 100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）放出去。
  skill   长刻：`Targeting` EnemyWithoutTower（q_range）：q_hit 拍（第 3 帧）朝目标射一道细长的星束（长 q_len、宽 q_w），
          线上的敌人吃 q_dmg + q_ap% 法强的魔法伤害；星束经过她自己的坐标，坐标炸开一小圈（q_br 内 q_burst + q_bap% 法强），
          坐标用掉。
  skill2  照盘：`Targeting` 敌方英雄（e_range，最远的技能）：e_hit 拍在目标脚下放一个坐标（立起六分仪），e_delay 拍后它照一下：
          身边 e_r 内的敌人吃 e_dmg + e_ap% 法强、减速 e_slow%。
  ult     星历：`Targeting` 敌方英雄（r_range）：r_on 拍（第 3 帧，0.40 秒）沿她到目标的方向挑三处错开的落点（目标脚下、
          往前、往后各错开 r_spread；身边有她的坐标就落在坐标上），每处先亮一个独立的预警圈，r_warn 拍后（三处隔 r_gap 拍）
          落一枚星刻：r_r 内的敌人吃 r_dmg + r_ap% 法强的魔法伤害、减速 r_slow%。每处单独结算。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、长刻 / 照盘 0.56 秒（第 3 帧 0.26 秒）、星历 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/jiyan.rs）：被动 border_jiyan:chart（坐标），原生效果 border_jiyan:beam / chart / chart_pulse /
almanac / star / noop。--plain 和塞拉斯版：长刻是一条数据的直线，照盘、星历是丢到目标脚下的圈（kit.lob）；星历三枚都落在
目标脚下（时间错开），后两枚只算 r_side_sim% 的伤害：原版是沿方向错开落的，站着不动的人一般只吃中间那一枚。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_jiyan"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh jiyan 2 ...，中路 lane 2，600 秒，对手是五个原版中单，8 个种子），2026-11-22。
# 联盟中单中位数约 +2.5。初稿 -4.84：数据版的照盘、星历圈原来生成在她自己脚下，一下都打不中；改成丢到目标脚下（kit.lob）
# 后原值 +0.38。星历三枚都砸在目标身上时太强（+6 ~ +8），后两枚按 r_side_sim% 算（原版错开落下）后，照盘、星历早一点落、
# 圈大一点、三个技能伤害和法强成长加一点（这份）+2.52。
P = {
    # 属性（法师）
    "hp": 860, "hp_g": 90, "atk": 76, "atk_g": 6, "apw": 50, "apw_g": 24, "def": 20, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 940, "ms_g": 10,
    "atk_range": 64000, "atk_dur": 28, "atk_cd": 90, "atk_st": 13, "a_speed": 6500,
    # 被动：定标
    "p_t": 240, "p_max": 3,
    # 长刻
    "q_cd": 420, "q_range": 75000, "q_dur": 34, "q_hit": 16, "q_len": 85000, "q_w": 9000, "q_dmg": 95, "q_ap": 70,
    "q_burst": 60, "q_bap": 40, "q_br": 16000,
    # 照盘
    "e_cd": 540, "e_range": 90000, "e_dur": 34, "e_hit": 16, "e_delay": 30, "e_dmg": 60, "e_ap": 45, "e_r": 20000,
    "e_slow": 25, "e_slow_t": 60,
    # 星历
    "r_cd": 3000, "r_range": 90000, "r_dur": 52, "r_on": 24, "r_gap": 6, "r_warn": 22, "r_spread": 22000,
    "r_r": 22000, "r_dmg": 200, "r_ap": 85, "r_slow": 30, "r_slow_t": 60,
    # 只给平衡模拟（--plain）和塞拉斯版：星历后两枚的伤害按多少算（原版错开落下，主目标平均吃到的那一截）
    "r_side_sim": 40,
}

NATIVE = ["p_t", "p_max", "q_len", "q_w", "q_dmg", "q_ap", "q_burst", "q_bap", "q_br", "e_dmg", "e_ap", "e_r",
          "e_slow", "e_slow_t", "r_spread", "r_r", "r_dmg", "r_ap", "r_slow", "r_slow_t"]


def circle(name, radius, apply, effects):
    """数据版的圈：生成的地方往后 apply 拍结算。要放在目标脚下就装进 kit.lob 丢过去。"""
    return {"type": "RangeProjectile", "name": kit.n(name), "shape": {"Circle": {"radius": radius}},
            "delay": apply + 1, "apply": apply, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(*effects)}]}


def plain_almanac(p):
    """数据版的星历：三枚星刻都落在目标脚下，时间错开（每枚先在目标身上亮预警圈）；后两枚只算 r_side_sim% 的伤害。"""
    stars = []
    for k in range(3):
        apply = p["r_warn"] + k * p["r_gap"]
        m = 100 if k == 0 else p["r_side_sim"]
        star = circle(f"r_star{k}", p["r_r"], apply - k * p["r_gap"],
                      [K.ap_attack(p["r_dmg"] * m // 100, p["r_ap"] * m // 100),
                       kit.slow("r_slow", p["r_slow"], p["r_slow_t"]), kit.view("r_star")])
        stars.append(K.delayed(k * p["r_gap"], kit.view("r_warn"), kit.lob(f"r_lob{k}", star)))
    return K.combine(*stars)


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：星针
    bolt = {"type": "TargetProjectile", "name": kit.n("a_bolt"), "speed": p["a_speed"], "y_offset": -1500,
            "applied_target": "Enemy",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(K.attack(0, 100), kit.view("a_hit"))}]}
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(bolt, {"type": "Sfx", "name": "astrologer_attack"}), atype="BaseAttack",
                          cancel=True)

    # ------------------------------------------------------------------ Q：长刻
    if is_native:
        beam = kit.native("beam")
    else:
        beam = {"type": "LineRangeProjectile", "name": kit.n("q_line"), "width": p["q_w"], "length": p["q_len"],
                "delay": 2, "apply": 1, "applied_target": "EnemyWithoutTower",
                "applied_effects": [{"casting_type": "Targeting", "effect": K.ap_attack(p["q_dmg"], p["q_ap"])}]}
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "astrologer_skill1_impact"},
                                 K.delayed(p["q_hit"] - 1, kit.alive_only(beam))))

    # ------------------------------------------------------------------ E：照盘
    if is_native:
        chart = K.combine(K.delayed(p["e_hit"] - 1, kit.alive_only(kit.native("chart"))),
                          K.delayed(p["e_hit"] + p["e_delay"] - 1, kit.alive_only(kit.native("chart_pulse"))))
    else:
        chart = K.delayed(p["e_hit"] - 1, kit.lob("e_lob", circle("e_zone", p["e_r"], p["e_delay"],
                                                                  [K.ap_attack(p["e_dmg"], p["e_ap"]),
                                                                   kit.slow("e_slow", p["e_slow"], p["e_slow_t"])])))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "astrologer_skill2"}, chart))

    # ------------------------------------------------------------------ R：星历（三处）
    if is_native:
        stars = [K.delayed(p["r_on"] - 1, kit.alive_only(kit.native("almanac")))]
        for k in range(3):
            stars.append(K.delayed(p["r_on"] + p["r_warn"] + k * p["r_gap"] - 1, kit.native("star")))
        almanac = K.combine(*stars)
    else:
        almanac = K.delayed(p["r_on"] - 1, kit.alive_only(plain_almanac(p)))
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "astrologer_ult_burst"}, almanac))

    # ------------------------------------------------------------------ 画面
    views_e = kit.views([("a_hit", "a_hit")])
    views_e += kit.views([("p_mark", "p_mark"), ("e_chart", "e_chart"), ("r_warn", "r_warn"), ("r_star", "r_star")],
                         follow=False)
    views_p = kit.projectile_views([("a_bolt", "a_bolt"), ("q_beam_r", "q_beam_r"), ("q_beam_l", "q_beam_l")],
                                   once=("q_beam_r", "q_beam_l"))
    stat, growth = K.stats(p)
    tags = ["AP", "Magic", "Range"]
    if not is_native:
        return kit.shell("Magician", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Magician", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="chart",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的星历（STOLEN）：三枚星刻落在目标脚下（时间错开，每枚先亮预警圈，后两枚打折）。纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    return K.combine({"type": "Sfx", "name": "astrologer_ult_burst"},
                     K.delayed(p["r_on"] - 1, kit.alive_only(plain_almanac(p))))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
