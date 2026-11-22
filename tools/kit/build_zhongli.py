"""钟砾（边境巡团 border_zhongli，射手，下路）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_zhongli.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

站桩型的射手，铜色机械臂炮。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    定脚：连着 p_still 拍没怎么挪（一拍挪不到 300）就站稳，之后每 p_step 拍多一档（最多 p_levels 档，每档攻速
          +p_as%，border_zhongli_plant）；累计挪开 p_move 就全部解除。站稳时脚下的支架落地。
  attack  弹丸 `Enemy`：弹道（a_speed）打中 100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）放出去。压簧上好时这一发多 q_dmg +
          q_ad% 攻击力，站稳着还无视 q_pen% 护甲（打中那一拍的穿甲）。
  skill   压簧：`Targeting` EnemyWithoutTower（攻击距离）：压上弹簧（border_zhongli_spring，等下一发普攻用掉），前臂的弹簧和
          琥珀光画在他自己的帧里。
  skill2  落架：`Targeting` 敌方英雄（e_range，交战时才放）：e_hit 拍架起支架：护盾 e_sh + e_hp% 最大生命 e_t 拍，定脚直接满档；
          支架 e_stand 拍内他一走开（挪开 p_move）就收起（满档跟着解除）。
  ult     齐鸣：`Targeting` 敌方英雄（r_range）：方向在出手那一刻定死，r_shot1 拍起每隔 r_gap 拍朝那个方向放一发（共四发，
          每发一个单独的右向弹丸，直线、打到第一个敌人停），每发 r_dmg + r_ad% 攻击力，最后一发 r_last%。他被控住、
          或者离开出手的位置 r_move 以上，后面的不放了。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、压簧 / 落架 0.56 秒（第 3 帧 0.26 秒）、齐鸣 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/zhongli.rs）：被动 border_zhongli:plant（定脚、支架），原生效果 border_zhongli:stand / aim /
volley / volley_last / volley_hit / volley_hit_last。--plain 和塞拉斯版：定脚按 p_as_sim% 的平均攻速算，齐鸣是四发数据的直线弹道。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_zhongli"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh zhongli 3 ...，下路 lane 3，600 秒，8 个种子），2026-11-22。联盟下路中位数约
# +2.6。初稿 -0.36，加攻击、压簧和齐鸣（这份）+2.15。定脚在模拟里按平均 +p_as_sim% 攻速算（border.dll 里站稳才有，最多
# +p_as x p_levels）。
P = {
    # 属性（射手）
    "hp": 900, "hp_g": 90, "atk": 105, "atk_g": 21, "apw": 0, "apw_g": 0, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3,
    "ms": 930, "ms_g": 9,
    "atk_range": 62000, "atk_dur": 28, "atk_cd": 62, "atk_st": 13, "a_speed": 7500,
    # 被动：定脚
    "p_still": 45, "p_move": 3000, "p_as": 12, "p_levels": 4, "p_step": 30,
    # 压簧
    "q_cd": 360, "q_dur": 34, "q_dmg": 80, "q_ad": 110, "q_pen": 35,
    # 落架
    "e_cd": 720, "e_range": 65000, "e_dur": 34, "e_hit": 16, "e_sh": 90, "e_hp": 8, "e_t": 150, "e_stand": 240,
    # 齐鸣
    "r_cd": 3000, "r_range": 75000, "r_dur": 52, "r_shot1": 20, "r_gap": 9, "r_len": 90000, "r_speed": 9000,
    "r_w": 9000, "r_dmg": 110, "r_ad": 85, "r_last": 200, "r_move": 4000,
    # 只给平衡模拟（--plain）：平均的定脚攻速
    "p_as_sim": 25,
}

NATIVE = ["p_still", "p_move", "p_as", "p_levels", "p_step", "e_sh", "e_hp", "e_t", "e_stand", "r_len", "r_speed",
          "r_w", "r_dmg", "r_ad", "r_last", "r_move", "r_dur"]


def shot(name, speed, effects):
    return {"type": "TargetProjectile", "name": kit.n(name), "speed": speed, "y_offset": -1800,
            "applied_target": "Enemy",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(*effects)}]}


def plain_volley(p):
    """数据版的齐鸣：四发朝目标的直线弹丸（打到第一个敌人停），最后一发 r_last%。"""
    out = []
    for k in range(4):
        m = p["r_last"] if k == 3 else 100
        line = {"type": "LinearProjectile", "name": kit.n("r_bolt"), "speed": p["r_speed"], "range": p["r_len"],
                "penetrate": False, "shape": {"Circle": {"radius": p["r_w"] // 2}}, "y_offset": -1800,
                "applied_target": "EnemyWithoutTower", "end_effects": [],
                "applied_effects": [{"casting_type": "Targeting",
                                     "effect": K.combine(K.attack(p["r_dmg"] * m // 100, p["r_ad"] * m // 100),
                                                         kit.view("a_hit"))}]}
        out.append(K.delayed(p["r_shot1"] + k * p["r_gap"] - 1, kit.alive_only(line, {"type": "Sfx", "name": "gunner_ult"})))
    return K.combine(*out)


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：弹丸（压簧上好时加成，站稳着穿甲）
    plain_hit = [K.attack(0, 100), kit.view("a_hit")]
    pen = kit.flag("pen", 1, defence_penetration=p["q_pen"])
    # 站稳着（被动挂的 border_zhongli_plant）这一发打中那一拍穿甲：buff 在加上的那一拍就算（champion-data 第 4 节）
    spring_hit = [kit.when("plant", pen, K.combine()), K.attack(p["q_dmg"], 100 + p["q_ad"]), kit.unflag("spring"),
                  kit.view("a_hit")]
    fire = kit.when("spring", shot("a_bolt", p["a_speed"], spring_hit), shot("a_bolt", p["a_speed"], plain_hit))
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(fire, {"type": "Sfx", "name": "gunner_attack"}), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：压簧
    spring = kit.flag("spring", None)
    if not is_native:   # 模拟里没有 border.dll 的定脚：第一次压簧起挂一个永久的平均攻速（先摘掉，不叠）
        spring = K.combine(spring, kit.unflag("plant_sim"),
                           kit.flag("plant_sim", None, attack_speed_mult=p["p_as_sim"]))
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["atk_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "gunner_skill2_on"}, spring))

    # ------------------------------------------------------------------ E：落架
    if is_native:
        stand = kit.native("stand")
    else:
        stand = K.combine(K.on_self({"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": 0,
                                     "tick": p["e_t"]}),
                          kit.flag("e_stand", p["e_t"], attack_speed_mult=p["p_as"] * p["p_levels"] - p["p_as_sim"]))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "gunner_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(stand))))

    # ------------------------------------------------------------------ R：齐鸣
    if is_native:
        shots = [kit.native("aim")]
        for k in range(4):
            shots.append(K.delayed(p["r_shot1"] + k * p["r_gap"] - 1,
                                   kit.alive_only(kit.native("volley_last" if k == 3 else "volley"))))
        volley = K.combine(K.anim("ult", p["r_shot1"] + 3 * p["r_gap"] + 6), *shots)
    else:
        volley = plain_volley(p)
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "gunner_skill2_on"}, volley))

    # ------------------------------------------------------------------ 画面
    views_e = kit.views([("a_hit", "a_hit"), ("p_feet", "p_feet"), ("e_shield", "e_shield")])
    views_p = kit.projectile_views([("a_bolt", "a_bolt"), ("r_bolt", "r_bolt")])
    stat, growth = K.stats(p)
    tags = ["AD", "Range"]
    if not is_native:
        return kit.shell("Range", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Range", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="plant",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的齐鸣（STOLEN）：四发朝目标的直线弹丸（打到第一个敌人停），最后一发最强；数据版不会因为他走开而停。
    纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    return K.combine({"type": "Sfx", "name": "gunner_skill2_on"}, plain_volley(p))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
