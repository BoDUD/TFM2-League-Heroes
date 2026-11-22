"""盐汐（边境巡团 border_yanxi，法师，中路）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_yanxi.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

盐晶法师，封走位。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    析晶：还站在盐带里的敌人每 p_tick 拍叠一层结晶（border_yanxi_crystal，最多 p_max 层，离开以后留 p_keep 拍），
          在带子里减速 p_slow%；叠到三层身上亮一簇盐晶。border.dll 记账（addons/border/src/yanxi.rs），盐带的位置挂在
          她身上（border_yanxi_band_*）。
  attack  盐晶 `Enemy`：弹道（a_speed）打中 100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）放出去。
  skill   撒线：`Targeting` EnemyWithoutTower（q_range）：q_hit 拍（第 3 帧，0.26 秒）以目标为中点、沿她到目标的方向铺一条长
          q_len、宽 q_w 的盐带，q_t 拍：带上的敌人当场 q_dmg + q_ap% 法强的魔法伤害、叠一层结晶。
  skill2  凝结：`Targeting` 敌方英雄（e_range）：e_hit 拍把 e_reach 内每个带结晶的敌人引爆：e_dmg + e_ap% 法强，每层再加
          e_kdmg + e_kap% 法强（魔法伤害），结晶清掉；结算完只给这次层数最高的那个敌方英雄定身 e_root 拍（一样多挑生命
          比例低的）。谁都没有结晶就只打目标，不定身。
  ult     退潮：`Targeting` 敌方英雄（r_range）：r_hit 拍（第 3 帧，0.40 秒）让她现在的盐带从远端朝她扫回来（没有盐带就先
          穿过目标铺一条）：一道晶浪（速度 r_speed、宽 r_w）沿带子往她这边走，扫到的敌人 r_dmg + r_ap% 法强的魔法伤害、
          叠 r_stack 层结晶、被往她这边带 r_pull（r_pull_t 拍）。晶浪的画面跟着走的方向转（朝左时换上下翻过的那张）。
          塞拉斯偷去的是数据版（sylas_ult）：在目标脚下掀起晶浪扫回他身边，不走 border.dll。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、撒线 / 凝结 0.56 秒（第 3 帧 0.26 秒）、退潮 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/yanxi.rs）：被动 border_yanxi:salt（析晶、盐带、配音），原生效果 border_yanxi:line / congeal /
ebb / ebb_hit / noop。--plain 给平衡模拟：盐带换成打中目标的伤害和减速，凝结按两层结晶算，退潮只打目标、往回拉。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_yanxi"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh yanxi 2 ...，中路 lane 2，600 秒，对手是五个原版中单，8 个种子），2026-11-22。
# 联盟中单中位数约 +2.5（终末包湿婆那一轮的对照）。初稿 -0.33，加法强成长和三个技能的伤害 +1.84，再加一点血、魔抗和射程（这份）
# +2.51。盐带的范围伤害、叠结晶和凝结只定身层数最多的人都在 border.dll 里，模拟里按目标单体、两到三层算。
P = {
    # 属性（法师，原版法师 hp 900 / 法强 40 左右）
    "hp": 900, "hp_g": 90, "atk": 78, "atk_g": 6, "apw": 45, "apw_g": 22, "def": 20, "def_g": 7, "mr": 24,
    "mr_g": 4, "ms": 960, "ms_g": 10,
    "atk_range": 60000, "atk_dur": 28, "atk_cd": 85, "atk_st": 13, "a_speed": 6000,
    # 被动：析晶
    "p_tick": 45, "p_max": 5, "p_keep": 240, "p_slow": 25,
    # 撒线
    "q_cd": 360, "q_range": 62000, "q_dur": 34, "q_hit": 16, "q_len": 50000, "q_w": 14000, "q_t": 240, "q_dmg": 80,
    "q_ap": 60,
    # 凝结
    "e_cd": 600, "e_range": 70000, "e_dur": 34, "e_hit": 16, "e_reach": 90000, "e_dmg": 70, "e_ap": 40,
    "e_kdmg": 25, "e_kap": 15, "e_root": 60,
    # 退潮
    "r_cd": 3000, "r_range": 70000, "r_dur": 52, "r_hit": 24, "r_speed": 3000, "r_w": 16000, "r_dmg": 220,
    "r_ap": 90, "r_stack": 2, "r_pull": 15000, "r_pull_t": 10,
    # 只给平衡模拟（--plain）：凝结时平均几层结晶
    "e_k_sim": 3,
}

NATIVE = ["p_tick", "p_max", "p_keep", "p_slow", "q_len", "q_w", "q_t", "q_dmg", "q_ap", "e_reach", "e_dmg", "e_ap",
          "e_kdmg", "e_kap", "e_root", "r_speed", "r_w", "r_dmg", "r_ap", "r_stack", "r_pull", "r_pull_t"]


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：盐晶
    shard = {"type": "TargetProjectile", "name": kit.n("a_shard"), "speed": p["a_speed"], "y_offset": -1500,
             "applied_target": "Enemy",
             "applied_effects": [{"casting_type": "Targeting",
                                  "effect": K.combine(K.attack(0, 100), kit.view("a_hit"))}]}
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(shard, {"type": "Sfx", "name": "ice_mage_attack"}),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：撒线
    if is_native:
        line = kit.native("line")
    else:
        line = K.combine(K.ap_attack(p["q_dmg"], p["q_ap"]), kit.slow("p_slow", p["p_slow"], 90))
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "ice_mage_skill"},
                                 K.delayed(p["q_hit"] - 1, kit.alive_only(line))))

    # ------------------------------------------------------------------ E：凝结
    if is_native:
        congeal = kit.native("congeal")
    else:
        k = p["e_k_sim"]
        congeal = K.combine(K.ap_attack(p["e_dmg"] + k * p["e_kdmg"], p["e_ap"] + k * p["e_kap"]),
                            {"type": "Bind", "duration": p["e_root"]}, kit.view("e_burst"))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "ice_mage_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(congeal))))

    # ------------------------------------------------------------------ R：退潮
    if is_native:
        ebb = kit.native("ebb")
    else:
        ebb = K.combine(K.ap_attack(p["r_dmg"], p["r_ap"]), {"type": "Pull", "speed": p["r_pull"] // p["r_pull_t"],
                                                              "tick": p["r_pull_t"]})
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "ice_mage_ult"},
                               K.delayed(p["r_hit"] - 1, kit.alive_only(ebb))))

    # ------------------------------------------------------------------ 画面
    # 打中的盐屑、凝结爆开的盐楔、被叠满的人身上的盐簇（tools/art/import_yanxi.py）；盐晶、盐带、晶浪是弹道画面
    views_e = kit.views([("a_hit", "a_hit"), ("e_burst", "e_burst"), ("p_crystal", "p_crystal")])
    views_p = kit.projectile_views([("a_shard", "a_shard"), ("q_band_r", "q_band_r"), ("q_band_l", "q_band_l"),
                                    ("r_wave_r", "r_wave_r"), ("r_wave_l", "r_wave_l")],
                                   once=("q_band_r", "q_band_l"))
    stat, growth = K.stats(p)
    tags = ["AP", "Magic", "CC", "Range"]
    if not is_native:
        return kit.shell("Magician", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Magician", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="salt",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的退潮（STOLEN）：他没有盐带，r_hit 拍在目标脚下掀起一道晶浪（kit.lob 丢过去），晶浪从那里扫回他身边
    （BackToCasterLinearProjectile 是从生成的地方飞回施法者的：直接在他脚下生成就原地不动，什么也不打），扫到的人吃伤害、
    被往回带。画面是盐汐朝右的晶浪（数据挑不了方向）。不靠 border.dll。"""
    p = dict(P) if p is None else p
    hit = K.combine(K.ap_attack(p["r_dmg"], p["r_ap"]),
                    {"type": "Pull", "speed": p["r_pull"] // p["r_pull_t"], "tick": p["r_pull_t"]}, kit.view("a_hit"))
    wave = {"type": "BackToCasterLinearProjectile", "name": kit.n("r_wave_r"), "speed": p["r_speed"], "range": 400000,
            "penetrate": True, "shape": {"Circle": {"radius": p["r_w"] // 2}}, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": hit}], "end_effects": []}
    return K.combine({"type": "Sfx", "name": "ice_mage_ult"},
                     K.delayed(p["r_hit"] - 1, kit.alive_only(kit.lob("r_lob", wave))))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
