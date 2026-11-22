"""灯弥（边境巡团 border_dengmi，辅助）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_dengmi.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

杏紫色的提灯师，救急的辅助（鳍翼在立绘里展开，跑图时收在背后）。美术、图标、配音是 Codex 的（assets/source/border/），
技能照 Codex 的角色合同：
  被动    存光：身边 p_reach 内的友军（连她自己）挨的技能伤害攒成灯火：每挨掉最大生命的 1% 攒 p_gain / 100 点，最多 100
          点，分十层（border_dengmi_light）。怎么算技能伤害：掉血那一刻他附近 p_near 内有敌方英雄正在施法（放技能的动作
          还在播，或者技能刚进冷却），或者一下掉了最大生命的 p_burst% 以上。border.dll 记账（addons/border/src/dengmi.rs），
          它还每一拍挑出身边最承压的友军（最近掉的血、身边的敌人、生命比例），挂 2 拍的 border_dengmi_focus，递灯认它。
  attack  灯火 `Enemy`：弹道（a_speed）打中 100% 攻击力，atk_st 拍（第 3 帧，0.21 秒）放出去。
  attack  灯火 `Enemy`：弹道（a_speed）打中 100% 攻击力的物理伤害，再加 a_ap% 法强的魔法伤害。
  skill   递灯：`Targeting` 敌方英雄（q_range，交战时才放，原版的护盾谁都算满分，champion-data 第 3 节）：q_hit 拍（第 3 帧，
          0.26 秒）把灯递给最承压的友军（border_dengmi_focus；没有就 q_reach 内生命比例最低的，连她自己）：护盾 q_sh +
          q_ap% 法强 + q_hp% 对方最大生命，q_t 拍；灯一亮，他身边 q_flare_r 内的敌人晃眼减速 q_flare_slow% q_flare_t 拍。
  skill2  引路：`Targeting` 敌方英雄（e_range）：e_hit 拍给 e_reach 内生命比例最低的友军（连她自己）点一条路：移速
          +e_ms%，生命低于 e_low% 时再 +e_ms_low%，e_t 拍；她自己也 +e_self%。
  ult     收灯：`Targeting` 友方英雄（r_range；治疗量让 AI 等有人掉了血才放）：把灯火收回来分两次放出去。r_hit1 拍（第 3 帧，
          0.40 秒）第一脉冲治疗选中的主目标 r_heal + r_ap% 法强（数据的 Heal，AI 看得见），灯火每层再加 r_light / 10%
          （border.dll 补上）；r_hit2 拍第二脉冲在主目标身边 r_near 内挑生命比例最低的有效友军（有别人先挑别人），同样多。
          每个受治疗的人脚下放一次套环脉冲，脉冲的光炸开：他身边 r_burst_r 内的敌人吃 r_burst + r_burst_ap% 法强的魔法
          伤害、减速 r_burst_slow% 1 秒。放完灯火清零。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、递灯 / 引路 0.56 秒（第 3 帧 0.26 秒）、收灯 0.87 秒（第 3 帧
0.40 秒）。

border.dll（addons/border/src/dengmi.rs）：被动 border_dengmi:light（存光、挑承压的友军、配音），原生效果
border_dengmi:lamp / path / pulse1 / pulse2。--plain 给平衡模拟：经典引擎跑不了 border.dll，递灯和引路随机给一个友军
（递灯的护盾按 q_focus_sim% 算，补上原版挑最承压的人那一截），灯火按 r_light_sim% 的平均加成算，第二脉冲随机挑一个友军。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_dengmi"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh dengmi 4 ...，辅助 lane 4，600 秒，对手是五个原版辅助），2026-11-22。
# 联盟辅助（阿利斯塔 -0.60、蕾欧娜 -0.29、布隆 -0.07、锤石 +0.58、洛 +1.21、诺提勒斯 +2.99，中位数约 +0.26）。初稿 -4.19，
# 护盾、治疗、射程、普攻带法强、递灯的晃眼和收灯的光炸 -1.73 ~ -0.80；加护盾、加治疗、缩冷却都不动（-0.6 ~ -1.1）。
# 数据版的晃眼和光炸原来炸在她自己身边（她站在后排，几乎扫不到人），改成丢到目标身边炸（原版在受护盾、受治疗的人
# 身边）之后（这份）两组种子 -0.29 / +0.88。
P = {
    # 属性（辅助，原版辅助 hp 900 / 法强 30 左右）
    "hp": 1000, "hp_g": 88, "atk": 80, "atk_g": 6, "apw": 40, "apw_g": 15, "def": 26, "def_g": 7, "mr": 28,
    "mr_g": 4, "ms": 1000, "ms_g": 10,
    "atk_range": 60000, "atk_dur": 28, "atk_cd": 75, "atk_st": 13, "a_speed": 5000, "a_ap": 60,
    # 被动：存光
    "p_reach": 60000, "p_near": 90000, "p_gain": 100, "p_burst": 8,
    # 递灯
    "q_cd": 360, "q_range": 60000, "q_dur": 34, "q_hit": 16, "q_reach": 60000, "q_sh": 110, "q_ap": 70, "q_hp": 6,
    "q_t": 150, "q_flare_r": 30000, "q_flare_slow": 50, "q_flare_t": 90,
    # 引路
    "e_cd": 420, "e_range": 60000, "e_dur": 34, "e_hit": 16, "e_reach": 60000, "e_ms": 35, "e_low": 50,
    "e_ms_low": 20, "e_t": 150, "e_self": 15,
    # 收灯
    "r_cd": 3000, "r_range": 70000, "r_dur": 52, "r_hit1": 24, "r_hit2": 38, "r_heal": 180, "r_ap": 80,
    "r_light": 100, "r_near": 40000, "r_reach": 75000, "r_burst": 90, "r_burst_ap": 45, "r_burst_r": 35000,
    "r_burst_slow": 30,
    # 只给平衡模拟（--plain）：灯火的平均加成；递灯的护盾按多少算（原版递给最承压的那个人，数据版只能随机挑一个友军，
    # 常常落在没人打的人身上）；对方最大生命按 1500 折成定值
    "r_light_sim": 60, "q_focus_sim": 150,
}

NATIVE = ["p_reach", "p_near", "p_gain", "p_burst", "q_reach", "q_sh", "q_ap", "q_hp", "q_t", "q_flare_r",
          "q_flare_slow", "q_flare_t", "e_reach", "e_ms", "e_low", "e_ms_low", "e_t", "e_self", "r_heal", "r_ap",
          "r_light", "r_near", "r_reach", "r_burst", "r_burst_ap", "r_burst_r", "r_burst_slow"]


def mote(effects):
    return {"type": "TargetProjectile", "name": kit.n("a_mote"), "speed": 0, "y_offset": 1500,
            "applied_target": "Enemy",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(*effects)}]}


def burst_at(name, radius, effects):
    """丢到目标脚下炸一圈光，只打敌人（只给 --plain 和塞拉斯版：kit.lob 落点上的圈；border.dll 的版本在受护盾、受治疗的
    人身边炸）。"""
    zone = {"type": "RangeProjectile", "name": kit.n(name), "shape": {"Circle": {"radius": radius}}, "delay": 2,
            "apply": 1, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(*effects)}]}
    return kit.lob(name + "_lob", zone)


def heal(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Ally"}


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：灯火
    shot = mote([K.attack(0, 100), K.ap_attack(0, p["a_ap"]), kit.view("a_hit")])
    shot["speed"] = p["a_speed"]
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(shot, {"type": "Sfx", "name": "enchanter_attack"}),
                          atype="BaseAttack", cancel=True)

    def to_ally(reach, effects):
        """--plain：随机一个友军（连她自己，AllyChampion）。"""
        return {"type": "RandomTarget", "range": reach, "casting_target": "AllyChampion", "from_projectile": False,
                "effects": effects}

    # ------------------------------------------------------------------ Q：递灯
    if is_native:
        lamp = kit.native("lamp")
    else:
        f = p["q_focus_sim"]
        lamp = K.combine(to_ally(p["q_reach"], [{"type": "Shield", "amount": (p["q_sh"] + p["q_hp"] * 15) * f // 100,
                                                 "attack_ratio": 0, "ap_ratio": p["q_ap"] * f // 100, "tick": p["q_t"]},
                                                kit.view("q_shield")]),
                         # 晃眼的光炸在她递灯时对着的那个敌方英雄身边（原版在受护盾的人身边，围着他的就是这些人）
                         burst_at("q_flare_zone", p["q_flare_r"],
                                  [kit.slow("q_flare", p["q_flare_slow"], p["q_flare_t"])]))
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyChampion",
                       K.combine({"type": "Sfx", "name": "priest_skill"},
                                 K.delayed(p["q_hit"] - 1, kit.alive_only(lamp))))

    # ------------------------------------------------------------------ E：引路
    if is_native:
        path = kit.native("path")
    else:
        path = K.combine(to_ally(p["e_reach"], [kit.buff("e_path", p["e_t"], move_speed_mult=p["e_ms"]),
                                                kit.view("e_path")]),
                         kit.flag("e_lead", p["e_t"], move_speed_mult=p["e_self"]))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "priest_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(path))))

    # ------------------------------------------------------------------ R：收灯（两个脉冲）
    if is_native:
        first = K.combine(heal(p["r_heal"], p["r_ap"]), kit.native("pulse1"))
        second = kit.native("pulse2")
    else:
        bonus = 100 + p["r_light_sim"]
        flash = [K.ap_attack(p["r_burst"], p["r_burst_ap"]), kit.slow("r_flash", p["r_burst_slow"], 60)]
        first = K.combine(heal(p["r_heal"] * bonus // 100, p["r_ap"] * bonus // 100), kit.view("r_ring"),
                          burst_at("r_flash1", p["r_burst_r"], flash))
        second = to_ally(p["r_near"], [heal(p["r_heal"] * bonus // 100, p["r_ap"] * bonus // 100), kit.view("r_ring"),
                                       burst_at("r_flash2", p["r_burst_r"], flash)])
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "AllyChampion",
                     K.combine({"type": "Sfx", "name": "enchanter_ult"},
                               K.delayed(p["r_hit1"] - 1, kit.alive_only(first, {"type": "Sfx", "name": "priest_ult"})),
                               K.delayed(p["r_hit2"] - 1, kit.alive_only(second,
                                                                         {"type": "Sfx", "name": "white_mage_ult_hit"}))))

    # ------------------------------------------------------------------ 画面
    # 打中的火星、递给队友的六角灯盾、引路的脚印、脚下的套环脉冲、灯火攒满一截时的水母灯（tools/art/import_dengmi.py）；
    # 飞出去的灯火是弹道画面
    views_e = kit.views([("a_hit", "a_hit"), ("q_shield", "q_shield"), ("e_path", "e_path"), ("r_ring", "r_ring"),
                         ("p_glow", "p_glow")])
    views_p = kit.projectile_views([("a_mote", "a_mote")])
    stat, growth = K.stats(p)
    tags = ["AP", "Heal", "Shield", "Range"]
    if not is_native:
        return kit.shell("Util", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Util", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="light",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的收灯（STOLEN）：他没有灯火（按 0 算）。第一脉冲治疗他选的友军，第二脉冲从他身边 r_near 内的友军里
    随机挑一个（纯数据挑不出生命最低的），每个人脚下一个套环；每道脉冲在受治疗的人身边炸一下光（伤害、减速）。不靠 border.dll。"""
    p = dict(P) if p is None else p
    flash = [K.ap_attack(p["r_burst"], p["r_burst_ap"]), kit.slow("r_flash", p["r_burst_slow"], 60)]
    first = K.combine(heal(p["r_heal"], p["r_ap"]), kit.view("r_ring"), burst_at("r_flash1", p["r_burst_r"], flash))
    second = {"type": "RandomTarget", "range": p["r_near"], "casting_target": "AllyChampion", "from_projectile": False,
              "effects": [heal(p["r_heal"], p["r_ap"]), kit.view("r_ring"), burst_at("r_flash2", p["r_burst_r"], flash)]}
    return K.combine({"type": "Sfx", "name": "enchanter_ult"},
                     K.delayed(p["r_hit1"] - 1, kit.alive_only(first, {"type": "Sfx", "name": "priest_ult"})),
                     K.delayed(p["r_hit2"] - 1, kit.alive_only(second, {"type": "Sfx", "name": "white_mage_ult_hit"})))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
