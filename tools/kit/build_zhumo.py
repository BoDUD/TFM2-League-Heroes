"""铸沫（边境巡团 border_zhumo，战士，上路）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_zhumo.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

铜火锻匠，持续缠斗的战士。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    余温：每一下实际打中的普攻攒 p_gain 点热量（最多 100，分十层 border_zhumo_heat，每层攻速 +p_as%），p_idle 拍
          没打中东西就每秒掉 p_decay 点。border.dll 记账（addons/border/src/zhumo.rs）。
  attack  锤击 `Enemy`（塔也打）：100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）打到。
  skill   压坯：`Targeting` EnemyWithoutTower（q_range）：q_hit 拍（第 3 帧，0.26 秒落锤）重击目标 q_dmg + q_ad% 攻击力，热量
          每层再加 q_heat% 攻击力（物理伤害），减速 q_slow% q_slow_t 拍；热量 q_stun_heat 层以上再眩晕 q_stun 拍；目标身边
          q_splash 内别的敌人吃 q_splash_pct%。热量不消耗。落锤的熔流和地面火星画在他自己的帧里。
  skill2  回火：`Targeting` 敌方英雄（e_range，交战时才放）：e_hit 拍把身上的热量全部用掉，换 e_t 拍受到的伤害降低 e_dr% 再加
          每层 e_k%（满热 e_dr + 10 x e_k），回火的金属环贴着他。
  ult     开炉：`Targeting` 敌方英雄（r_range）：第 3 帧（0.40 秒）炉门一开，脚下 r_burst_r 内的敌人吃 r_burst + r_burst_ad% 攻击力
          物理伤害；r_t 拍攻速 +r_as%；第 3 帧起每秒一次（border_zhumo:furnace）：热量 +r_gain
          层、脚下炉圈亮一下，再看情况：生命低于 r_low%（或身边两个以上敌方英雄、生命低于 70%）而回火在冷却，回火冷却减
          r_cdr 拍（AI 就会回火防守）；不然热量 r_smash 层以上、r_reach 内有敌方英雄而压坯在冷却，压坯冷却减 r_cdr 拍（AI 就会
          重击）。塞拉斯偷去也一样：读的是施法的人自己的冷却和热量。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、压坯 / 回火 0.56 秒（第 3 帧 0.26 秒）、开炉 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/zhumo.rs）：被动 border_zhumo:heat（余温、配音），原生效果 border_zhumo:press / temper / furnace。
--plain 给平衡模拟：经典引擎跑不了 border.dll，热量按 q_heat_sim 层的平均值算，开炉的回火 / 重击换成技能冷却加速。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_zhumo"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh zhumo 0 ...，上路 lane 0，600 秒，对手是六个原版上单，8 个种子），2026-11-22。
# 联盟上单对照（鳄鱼 +2.15、剑魔 +2.10、瑟提 +2.07、贾克斯 +1.51、诺手 +1.50、盖伦 -0.09，中位数约 +1.6）。初稿 -4.04（伤害
# 只有对手的一半），加攻击和压坯 -2.30，再加血、护甲 -1.44，开炉加一下炉门的爆发、压坯更疼、回火更硬 +1.20，热量攻速、开炉
# 攻速和双抗再高一点（这份）+1.69。
P = {
    # 属性（战士，原版近战 hp 1000 / 攻击 95 左右）
    "hp": 1150, "hp_g": 105, "atk": 100, "atk_g": 20, "apw": 0, "apw_g": 0, "def": 45, "def_g": 8, "mr": 32,
    "mr_g": 4, "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 60, "atk_st": 13,
    # 被动：余温
    "p_gain": 12, "p_as": 3, "p_idle": 180, "p_decay": 10,
    # 压坯
    "q_cd": 300, "q_range": 26000, "q_dur": 34, "q_hit": 16, "q_dmg": 70, "q_ad": 140, "q_heat": 10,
    "q_splash": 18000, "q_splash_pct": 50, "q_slow": 30, "q_slow_t": 60, "q_stun_heat": 5, "q_stun": 24,
    # 回火
    "e_cd": 600, "e_range": 40000, "e_dur": 34, "e_hit": 16, "e_dr": 25, "e_k": 4, "e_t": 150,
    # 开炉
    "r_cd": 3000, "r_range": 35000, "r_dur": 52, "r_on": 24, "r_t": 300, "r_as": 60, "r_gain": 2, "r_low": 40,
    "r_reach": 30000, "r_smash": 6, "r_cdr": 240, "r_burst": 180, "r_burst_ad": 120, "r_burst_r": 30000,
    # 只给平衡模拟（--plain）：平均的热量层数、开炉时技能冷却快多少
    "q_heat_sim": 6, "r_cdm_sim": 60,
}

NATIVE = ["p_gain", "p_as", "p_idle", "p_decay", "q_dmg", "q_ad", "q_heat", "q_splash", "q_splash_pct", "q_slow",
          "q_slow_t", "q_stun_heat", "q_stun", "e_dr", "e_k", "e_t", "r_gain", "r_low", "r_reach", "r_smash", "r_cdr"]


def burst(p):
    """开炉那一下：脚下一圈的敌人吃伤害（炉圈的画面由 furnace 原生效果 / 塞拉斯版的 CasterViewEffect 放）。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": p["r_burst_r"]}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [K.attack(p["r_burst"], p["r_burst_ad"])]}


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：锤击
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(K.attack(0, 100), {"type": "Sfx", "name": "hammerer_attack"}, kit.view("a_hit")),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：压坯（落锤的熔流画在他自己的帧里）
    if is_native:
        press = kit.native("press")
    else:
        press = K.combine(K.attack(p["q_dmg"], p["q_ad"] + p["q_heat"] * p["q_heat_sim"]),
                          kit.slow("q_slow", p["q_slow"], p["q_slow_t"]),
                          K.stun(p["q_stun"]) if p["q_heat_sim"] >= p["q_stun_heat"] else None, kit.view("a_hit"))
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "hammerer_skill"},
                                 K.delayed(p["q_hit"] - 1, kit.alive_only(press))))

    # ------------------------------------------------------------------ E：回火
    if is_native:
        temper = kit.native("temper")
    else:
        temper = kit.flag("e_temper", p["e_t"], damaged_reduce=p["e_dr"] + p["e_k"] * p["q_heat_sim"])
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "hammerer_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(temper))))

    # ------------------------------------------------------------------ R：开炉（每秒一次 border_zhumo:furnace）
    furnace = {"attack_speed_mult": p["r_as"]}
    if not is_native:
        furnace["skill_cooldown_mult"] = p["r_cdm_sim"]
    beats = []
    if is_native:
        for t in range(p["r_on"], p["r_t"] + 1, 60):
            beats.append(K.delayed(t - 1, kit.alive_only(kit.native("furnace"))))
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine(kit.flag("furnace", p["r_t"], **furnace), {"type": "Sfx", "name": "siege_breaker_ult"},
                               K.delayed(p["r_on"] - 1, kit.alive_only(burst(p))), *beats))

    # ------------------------------------------------------------------ 画面
    # 打中的火星、挨打的铜屑、回火的金属环、脚下的炉圈、锤头上的余烬（tools/art/import_zhumo.py）
    views_e = kit.views([("a_hit", "a_hit"), ("hit", "hit"), ("e_temper", "e_temper"), ("r_furnace", "r_furnace"),
                         ("p_heat", "p_heat")])
    stat, growth = K.stats(p)
    tags = ["AD", "Melee"]
    if not is_native:
        return kit.shell("Melee", tags, stat, growth, attack_a, skill, skill2, ult, views_e)
    return kit.shell("Melee", tags, stat, growth, attack_a, skill, skill2, ult, views_e, passive="heat",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的开炉（STOLEN）：他没有余温，开炉 r_t 拍攻速 +r_as%、技能冷却加快 r_cdm_sim%（代替铸沫那边按情况加快
    回火、压坯），每秒脚下炉圈亮一下。不靠 border.dll。"""
    p = dict(P) if p is None else p
    beats = [K.delayed(t - 1, kit.alive_only({"type": "CasterViewEffect", "name": kit.n("r_furnace")}))
             for t in range(p["r_on"], p["r_t"] + 1, 60)]
    return K.combine(kit.flag("furnace", p["r_t"], attack_speed_mult=p["r_as"], skill_cooldown_mult=p["r_cdm_sim"]),
                     {"type": "Sfx", "name": "siege_breaker_ult"}, K.delayed(p["r_on"] - 1, kit.alive_only(burst(p))),
                     *beats)


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
