"""伏梭（边境巡团 border_fusuo，刺客，打野）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_fusuo.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

银梭斥候，专抓落单的刺客。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    数步：敌方英雄离开自己的队友（最近的队友在 p_alone 外）还在越走越远，连着 p_steps 拍就被他盯上
          （border_fusuo_track，离开那种状态以后还留 p_keep 拍），脚下亮一串脚印；他打被盯上的人伤害
          +p_dmg%。border.dll 记账（addons/border/src/fusuo.rs）。
  attack  一刀 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）打到。
  skill   掠阶：`Targeting` EnemyWithoutTower（q_range）：出手就朝目标冲（q_reach 内有被盯上的敌方英雄就改冲他），冲到离他
          q_stop 处（强制位移，速度 q_speed，撞墙就停）；q_hit 拍（第 3 帧，0.26 秒）砍那个人 q_dmg + q_ad% 攻击力物理伤害，
          被盯上的再加 q_track%。银线划过的光画在他自己的帧里。
  skill2  留扣：`Targeting` 敌方英雄（e_range，交战时才放）：e_set 拍（第 2 帧）在脚下留一个回撤点（地上一直亮着第 2 帧），
          移速 +e_ms% e_ms_t 拍；e_win 拍内他危险了（生命低于 e_low%、一秒内掉了最大生命的 e_burst% 以上，或者身边
          e_crowd 个以上敌方英雄）就闪回回撤点（强制位移，速度 e_back），回来时受到的伤害降低 e_dr% e_dr_t 拍。没危险就
          留着，到时消失。
  ult     错拍：`Targeting` 敌方英雄（r_range）：出手第 1 拍在他和目标之间、一直延伸到目标身后，铺一条宽 r_w、长 r_len 的
          斩线（先是一道细线的预警），第 2 帧（r_dash 拍）他穿过目标冲到身后，r_apply 拍斩线在同一条线上结算：还在线上的
          敌人 r_dmg + r_ad% 攻击力物理伤害。及时横着走开的就躲掉了。全在数据里（塞拉斯偷去一样）。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、掠阶 / 留扣 0.56 秒（第 3 帧 0.26 秒）、错拍 0.87 秒。

border.dll（addons/border/src/fusuo.rs）：被动 border_fusuo:steps（数步、留扣的回撤、配音），原生效果
border_fusuo:skim / skim_hit / clasp。--plain 给平衡模拟：冲刺换成数据的 MoveToTarget，留扣换成移速和一点减伤。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_fusuo"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh fusuo 1 ...，打野 lane 1，600 秒，对手是五个原版打野，8 个种子），2026-11-22。
# 联盟打野对照（蔚 +2.21、李青 +1.98、瑟庄妮 +1.88、狼人 +0.57、扎克 +0.41、人马 -0.38，中位数约 +1.2）。初稿 -2.33（伤害只有
# 对手的七成），加攻击、Q、R 伤害 -0.10，再快一点的普攻、留扣更值钱 +0.45，再加血、攻击和 Q +1.00。错拍那条线原来宽
# 14000（引擎的判定还要再宽 15000 左右），几乎躲不开，收到 6000 后 +0.50，补 R、Q 的伤害、攻击力、一点血和护甲（这份）+1.57。
# 被动盯上落单的人加伤、掠阶改冲被盯上的人只在 border.dll 里，模拟里没有。
P = {
    # 属性（刺客，原版刺客 hp 900 / 攻击 120 左右）
    "hp": 1080, "hp_g": 90, "atk": 128, "atk_g": 28, "apw": 0, "apw_g": 0, "def": 32, "def_g": 7, "mr": 18,
    "mr_g": 3, "ms": 1080, "ms_g": 12,
    "atk_range": 23000, "atk_dur": 28, "atk_cd": 50, "atk_st": 13,
    # 被动：数步
    "p_alone": 50000, "p_steps": 60, "p_keep": 180, "p_dmg": 15,
    # 掠阶
    "q_cd": 360, "q_range": 45000, "q_dur": 34, "q_hit": 16, "q_reach": 60000, "q_speed": 4000, "q_stop": 14000,
    "q_dmg": 110, "q_ad": 160, "q_track": 30, "q_hit_r": 32000,
    # 留扣
    "e_cd": 720, "e_range": 60000, "e_dur": 34, "e_set": 8, "e_win": 240, "e_ms": 35, "e_ms_t": 90, "e_low": 35,
    "e_burst": 25, "e_crowd": 3, "e_back": 8000, "e_dr": 30, "e_dr_t": 30,
    # 错拍
    "r_cd": 3000, "r_range": 50000, "r_dur": 52, "r_w": 6000, "r_len": 75000, "r_life": 46, "r_apply": 35,
    "r_dash": 8, "r_speed": 4500, "r_dmg": 380, "r_ad": 210,
    # 只给平衡模拟（--plain）：留扣的平均减伤（闪回躲掉的那一截）
    "e_dr_sim": 25,
}

NATIVE = ["p_alone", "p_steps", "p_keep", "p_dmg", "q_reach", "q_speed", "q_stop", "q_dmg", "q_ad", "q_track",
          "q_hit_r", "q_dur", "e_win", "e_ms", "e_ms_t", "e_low", "e_burst", "e_crowd", "e_back", "e_dr", "e_dr_t"]


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：一刀
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(K.attack(0, 100), {"type": "Sfx", "name": "dual_blader_attack"}, kit.view("a_hit")),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：掠阶
    if is_native:
        skim = K.combine(kit.native("skim"), K.delayed(p["q_hit"] - 1, kit.alive_only(kit.native("skim_hit"))))
    else:
        skim = {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"],
                "end_effects": [K.attack(p["q_dmg"], p["q_ad"]), kit.view("a_hit")]}
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "ninja_skill2_dash"}, skim))

    # ------------------------------------------------------------------ E：留扣
    if is_native:
        clasp = kit.native("clasp")
    else:
        clasp = kit.flag("e_clasp", p["e_win"] // 2, move_speed_mult=p["e_ms"], damaged_reduce=p["e_dr_sim"])
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "hitman_skill2"},
                                  K.delayed(p["e_set"] - 1, kit.alive_only(clasp))))

    # ------------------------------------------------------------------ R：错拍（预警和结算是同一条线）
    line = {"type": "LineRangeProjectile", "name": kit.n("r_line"), "width": p["r_w"], "length": p["r_len"],
            "delay": p["r_life"], "apply": p["r_apply"], "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.attack(p["r_dmg"], p["r_ad"])},
                                {"casting_type": "Targeting", "effect": kit.view("a_hit")}]}
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine(line, {"type": "Sfx", "name": "inquisitor_skill1_pre"},
                               K.delayed(p["r_dash"] - 1, kit.alive_only({"type": "RushMoveToBack",
                                                                          "speed": p["r_speed"],
                                                                          "applied_effects": []})),
                               K.delayed(p["r_apply"] - 2, {"type": "Sfx", "name": "dual_blader_ult"})))

    # ------------------------------------------------------------------ 画面
    # 打中的银屑、挨打的碎光、被盯上的人脚下的脚印、留在地上的回撤点和闪回（tools/art/import_fusuo.py）；斩线是弹道画面
    views_e = kit.views([("a_hit", "a_hit"), ("hit", "hit"), ("p_track", "p_track"), ("e_anchor", "e_anchor"),
                         ("e_recall", "e_recall")])
    # 回撤点留在地上，不跟着他走
    for v in views_e:
        if v["name"] == kit.n("e_anchor"):
            v["is_follow"] = False
    views_p = kit.projectile_views([("r_line", "r_line")], once=("r_line",))
    stat, growth = K.stats(p)
    tags = ["AD", "Melee"]
    if not is_native:
        return kit.shell("Assassin", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Assassin", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="steps",
                     params={k: p[k] for k in sorted(NATIVE)})


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
