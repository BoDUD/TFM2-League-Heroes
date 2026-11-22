"""殷渡（边境巡团 border_yindu，坦克，开团）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_yindu.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

主动开团的坦克，提着箱盾的水手。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    迎汐：朝 p_reach 内的敌方英雄推进（这一拍离最近的那个更近了）时攒潮势，每 p_step 拍一层，最多 p_max 层
          （border_yindu_tide）；不往前推 p_keep 拍就一层层退。下一次扣舷带着潮势：减速每层多 q_slow_k%。
  attack  一拳 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）打到。
  skill   扣舷：`Targeting` EnemyWithoutTower（q_range）：出手就朝目标短冲（强制位移，最多 q_len，速度 q_speed），路上
          第一个敌人挡住就停在他面前；q_hit 拍（第 3 帧）撞他：q_dmg + q_ad% 攻击力 + q_hp% 最大生命的物理伤害、眩晕
          q_stun 拍、减速 q_slow% + 每层潮势 q_slow_k% q_slow_t 拍，潮势用掉。撞角的光画在他自己的帧里。
  skill2  立标：`Targeting` 敌方英雄（e_range）：e_hit 拍在目标那一群敌人中间（目标身边 e_group 内敌方英雄的中点）插一个
          航标（地上一直立着，e_t 拍），航标落下时身边 e_r 内的敌人吃 e_dmg + e_hp% 最大生命、减速 e_slow%。
  ult     合汛：`Targeting` 敌方英雄（r_range）：r_on 拍（第 3 帧，0.40 秒）从航标两侧（他身边 r_beacon_r 内有自己的航标；
          没有就是目标脚下）掀起两道潮墙往中间合拢，地上先是预警，r_land 拍后在汇合点结算：r_r 内的敌人每人只推一次，
          被卷到汇合点（r_pull_t 拍的强制位移），吃 r_dmg + r_ad% 攻击力 + r_hp% 最大生命的物理伤害、眩晕 r_stun 拍。
          航标用掉。合汛的画面枢轴就在汇合点。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、扣舷 / 立标 0.56 秒（第 3 帧 0.26 秒）、合汛 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/yindu.rs）：被动 border_yindu:tide，原生效果 border_yindu:ram / ram_hit / beacon / tide / tide_hit。
--plain 和塞拉斯版：冲刺换成 MoveToTarget，航标换成目标身上的伤害减速，合汛在目标脚下结算（数据的 RangeProjectile）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_yindu"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh yindu 1 ...，打野 lane 1，600 秒，对手是五个原版打野，8 个种子），2026-11-22。
# 联盟打野对照（蔚 +2.21、李青 +1.98、瑟庄妮 +1.88、狼人 +0.57、扎克 +0.41、人马 -0.38，中位数约 +1.2）。初稿 -2.33：数据版的
# 合汛圈原来生成在他自己脚下；改成丢到目标脚下（kit.lob）后原值 +0.26。两个眩晕长一点、合汛落得快一点、圈大一点，三个技能
# 的伤害、血和护甲（这份）两组种子 +1.33 / +1.93。
P = {
    # 属性（坦克）
    "hp": 1270, "hp_g": 120, "atk": 87, "atk_g": 9, "apw": 0, "apw_g": 0, "def": 47, "def_g": 9, "mr": 32,
    "mr_g": 4, "ms": 1010, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 28, "atk_cd": 75, "atk_st": 13,
    # 被动：迎汐
    "p_step": 15, "p_max": 8, "p_reach": 90000, "p_keep": 120,
    # 扣舷
    "q_cd": 420, "q_range": 40000, "q_dur": 34, "q_hit": 16, "q_len": 40000, "q_w": 12000, "q_speed": 3500,
    "q_dmg": 95, "q_ad": 80, "q_hp": 4, "q_stun": 26, "q_slow": 25, "q_slow_k": 5, "q_slow_t": 90,
    # 立标
    "e_cd": 600, "e_range": 70000, "e_dur": 34, "e_hit": 16, "e_t": 360, "e_group": 30000, "e_dmg": 70, "e_hp": 4,
    "e_r": 25000, "e_slow": 20, "e_slow_t": 60,
    # 合汛
    "r_cd": 3000, "r_range": 70000, "r_dur": 52, "r_on": 24, "r_land": 12, "r_r": 38000, "r_dmg": 190, "r_ad": 60,
    "r_hp": 7, "r_stun": 57, "r_pull_t": 8, "r_beacon_r": 90000,
}

NATIVE = ["p_step", "p_max", "p_reach", "p_keep", "q_len", "q_w", "q_speed", "q_dur", "q_dmg", "q_ad", "q_hp",
          "q_stun", "q_slow", "q_slow_k", "q_slow_t", "e_t", "e_group", "e_dmg", "e_hp", "e_r", "e_slow", "e_slow_t",
          "r_land", "r_r", "r_dmg", "r_ad", "r_hp", "r_stun", "r_pull_t", "r_beacon_r"]


def plain_tide(p):
    """数据版的合汛（--plain、塞拉斯）：目标脚下一个圈，r_land 拍后结算：拉到圈心、伤害、眩晕，画面放在目标身上。"""
    zone = {"type": "RangeProjectile", "name": kit.n("r_zone"), "shape": {"Circle": {"radius": p["r_r"]}},
            "delay": p["r_land"] + 2, "apply": p["r_land"] + 1, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting",
                                 "effect": K.combine(K.attack(p["r_dmg"], p["r_ad"], hp=p["r_hp"]),
                                                     {"type": "Pull", "speed": 3000, "tick": p["r_pull_t"]},
                                                     K.delayed(p["r_pull_t"], K.stun(p["r_stun"])))}]}
    return K.combine(kit.view("r_tide"), kit.lob("r_lob", zone))


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(K.attack(0, 100), {"type": "Sfx", "name": "knight_attack"}, kit.view("a_hit")),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：扣舷
    if is_native:
        ram = K.combine(kit.native("ram"), K.delayed(p["q_hit"] - 1, kit.alive_only(kit.native("ram_hit"))))
    else:
        ram = {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_len"],
               "end_effects": [K.attack(p["q_dmg"], p["q_ad"], hp=p["q_hp"]), K.stun(p["q_stun"]),
                               kit.slow("q_slow", p["q_slow"] + 2 * p["q_slow_k"], p["q_slow_t"]), kit.view("a_hit")]}
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "cavalry_knight_skill1"}, ram))

    # ------------------------------------------------------------------ E：立标
    if is_native:
        beacon = kit.native("beacon")
    else:
        beacon = K.combine(K.attack(p["e_dmg"], 0, hp=p["e_hp"]), kit.slow("e_slow", p["e_slow"], p["e_slow_t"]))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "shield_bearer_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(beacon))))

    # ------------------------------------------------------------------ R：合汛
    if is_native:
        tide = K.combine(K.delayed(p["r_on"] - 1, kit.alive_only(kit.native("tide"))),
                         K.delayed(p["r_on"] + p["r_land"] - 1, kit.alive_only(kit.native("tide_hit"))))
    else:
        tide = K.delayed(p["r_on"] - 1, kit.alive_only(plain_tide(p)))
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "knight_ult"}, tide))

    # ------------------------------------------------------------------ 画面
    views_e = kit.views([("a_hit", "a_hit"), ("hit", "hit"), ("p_tide", "p_tide")])
    # 航标、潮墙立在地上，不跟着人走
    views_e += kit.views([("e_buoy", "e_buoy"), ("e_buoy_end", "e_buoy_end"), ("r_tide", "r_tide")], follow=False)
    views_p = []   # 数据版合汛的圈（r_zone）不要画面：画面是 r_tide
    stat, growth = K.stats(p)
    tags = ["AD", "Melee", "Tank", "CC"]
    if not is_native:
        return kit.shell("Melee", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Tank", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="tide",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的合汛（STOLEN）：他没有航标，就在目标脚下合拢；预警、汇合点结算（拉到圈心、伤害、眩晕）和原版一样。
    纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    return K.combine({"type": "Sfx", "name": "knight_ult"}, K.delayed(p["r_on"] - 1, kit.alive_only(plain_tide(p))))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
