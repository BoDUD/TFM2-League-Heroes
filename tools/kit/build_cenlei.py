"""岑垒（边境巡团 border_cenlei，坦克，辅助位）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_cenlei.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

珊瑚盾卫，成年男性，护后排的坦克。美术、图标、配音是 Codex 的（assets/source/border/，交接说明
assets/source/border/CLAUDE_HANDOFF.md），技能照 Codex 的角色合同做：
  被动    背压：接肩替队友挨的伤害，他实际挨了多少就攒多少背压（最多他最大生命的 p_cap%），分十层，每层护甲和魔抗
          +p_res / 10（满了 +p_res）。死了清零。写在普攻说明里（游戏只有三个技能图标位）。border.dll 记账
          （addons/border/src/cenlei.rs），层数是他身上的 border_cenlei_pressure，卸城读它。
  attack  盾击 `Enemy`（塔也打）：100% 攻击力 + a_hp% 他的最大生命，atk_st 拍（第 3 帧，0.21 秒）打到。
  skill   横楔：`Targeting` EnemyWithoutTower（q_range）：q_hit 拍（第 3 帧，0.26 秒）朝前方扇形扫一下（半径 q_r，左右各
          acos(q_cos/1000)），扇形里的敌人 q_dmg + q_ad% 攻击力 + q_hp% 他的最大生命的物理伤害、减速 q_slow% q_slow_t 拍；
          扇形里的人都眩晕 q_stun_all 拍，正在施法的敌方英雄被打断（眩晕 q_stun 拍）。优先打断：身前半边 q_seek 内有正在施法的敌方英雄，扇形朝最近的那个扫。
  skill2  接肩：`Targeting` 敌方英雄（e_range，交战时才放）：q_hit 拍挑身边 e_reach 内最受威胁的队友（身边的敌方英雄、
          掉的血、被控），给他贴上珊瑚盾板（border_cenlei_ward，受到的伤害降低 e_share%，最多 e_time 拍）：他接下来
          e_hits 次挨打，少挨的那部分岑垒替他挨（真实伤害，不会因此倒下），攒成背压。身边没有受威胁的队友就自己顶住
          （受到的伤害降低 e_self% e_self_t 拍）。转移只在 border.dll 里算一次：盾板减下来的伤害按掉血反推，岑垒挨的
          不再算到任何人头上，不会转来转去。
  ult     卸城：`Targeting` 敌方英雄（r_range）：起手到出手不受控制、受到的伤害降低 r_dr%；r_hit 拍（第 3 帧，0.40 秒）把
          背压全放出去：前方扇形（半径 r_r，左右各 acos(r_cos/1000)）里的敌人每人只吃一下：r_dmg + r_ad% 攻击力 + 背压的
          r_p% 物理伤害，被推开（r_push x r_push_t），减速 r_slow% r_slow_t 拍；他得到放出的背压 r_sh% 的护盾 r_sh_t 拍。
          三道楔浪是同一下的画面（画在他自己的帧里）。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒（第 3 帧 0.21 秒打到）、横楔 / 接肩 0.56 秒（第 3 帧 0.26 秒）、
卸城 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/cenlei.rs）：被动 border_cenlei:pressure（背压、接肩的转移、配音），原生效果
border_cenlei:wedge / shoulder / release（横楔、接肩、卸城的选目标和结算）。--plain 给平衡模拟：经典引擎跑不了
border.dll，换成数据近似（扇形、随机给一个队友减伤、背压按 r_p_sim 算一个平均值）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_cenlei"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 单位：近战射程 25000；范围按单位的碰撞半径（约 10000）另算。一秒 60 拍。
# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh cenlei 4 ...，辅助 lane 4，600 秒，对手是五个原版辅助，8 个种子），2026-11-22。
# 联盟辅助对照（诺提勒斯 +2.99、锤石 +0.58、布隆 -0.07、蕾欧娜 -0.29、阿利斯塔 -0.60，中位数约 0 到 +0.25）。初稿 -3.43（走上路也
# -3.43），少推开、不算转移的代价 -2.50，再加伤害和血量 -2.73（没用）；和雷电一样靠控制：横楔给扫到的英雄都晕一下、卸城推开后
# 再晕 -1.54，范围再大一点 -0.95，晕得更久 -1.32，再加血、护甲和更久的减速（这份）+0.69。推开只推一小段（r_push x r_push_t）：
# 辅助把人推远了，队友就够不着。
P = {
    # 属性（坦克，原版坦克 hp 1100 / 护甲 40 / 魔抗 30 左右）
    "hp": 1250, "hp_g": 118, "atk": 74, "atk_g": 7, "apw": 0, "apw_g": 0, "def": 46, "def_g": 9, "mr": 30,
    "mr_g": 4, "ms": 1000, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 28, "atk_cd": 75, "atk_st": 13, "a_hp": 1,
    # 被动：背压
    "p_cap": 25, "p_res": 20,
    # 横楔
    "q_cd": 360, "q_range": 34000, "q_dur": 34, "q_hit": 16, "q_r": 45000, "q_cos": 570, "q_dmg": 60, "q_ad": 90,
    "q_hp": 4, "q_slow": 35, "q_slow_t": 90, "q_stun": 60, "q_seek": 45000, "q_stun_all": 40,
    # 接肩
    "e_cd": 600, "e_range": 70000, "e_dur": 34, "e_hit": 16, "e_reach": 55000, "e_share": 40, "e_hits": 2,
    "e_time": 240, "e_self": 20, "e_self_t": 120,
    # 卸城
    "r_cd": 3000, "r_range": 36000, "r_dur": 52, "r_hit": 24, "r_dr": 30, "r_r": 50000, "r_cos": 420, "r_dmg": 150,
    "r_ad": 100, "r_p": 60, "r_push": 1000, "r_push_t": 6, "r_slow": 30, "r_slow_t": 90, "r_sh": 50, "r_sh_t": 180,
    "r_stun": 60,
    # 只给平衡模拟（--plain）：扇形里的人都吃的短眩晕（代替打断施法）、接肩时他挨的生命百分比、背压的平均伤害
    "q_stun_sim": 6, "e_cost_sim": 0, "r_p_sim": 60,
}

# border.dll 读的参数（数据的 passive.params）：cenlei.rs 的 Params 一个不差
NATIVE = ["p_cap", "p_res", "q_r", "q_cos", "q_dmg", "q_ad", "q_hp", "q_slow", "q_slow_t", "q_stun", "q_seek",
          "q_stun_all", "e_reach", "e_share", "e_hits", "e_time", "e_self", "e_self_t", "r_r", "r_cos", "r_dmg", "r_ad",
          "r_p", "r_push", "r_push_t", "r_slow", "r_slow_t", "r_sh", "r_sh_t", "r_stun"]


def cone(radius, cos, effects):
    """前方扇形（半径 radius，左右各 acos(cos/1000)），从他身前 1000 起算（只给 --plain）。"""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": 1000}}, "effects": [e for e in effects if e is not None]}


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：盾击
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(K.attack(0, 100, hp=p["a_hp"]), {"type": "Sfx", "name": "shield_bearer_attack"},
                                    kit.view("a_hit")),
                          atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：横楔（扫的画面画在他自己的帧里）
    if is_native:
        wedge = kit.native("wedge")
    else:
        wedge = cone(p["q_r"], p["q_cos"], [K.attack(p["q_dmg"], p["q_ad"], hp=p["q_hp"]),
                                            kit.slow("q_slow", p["q_slow"], p["q_slow_t"]),
                                            K.stun(p["q_stun_sim"] + p["q_stun_all"])])
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "knight_skill"},
                                 K.delayed(p["q_hit"] - 1, kit.alive_only(wedge,
                                                                          {"type": "Sfx", "name": "fighter_skill_hit"}))))

    # ------------------------------------------------------------------ E：接肩
    if is_native:
        shoulder = kit.native("shoulder")
    else:
        ward = kit.buff("ward", p["e_time"] // 2, damaged_reduce=p["e_share"])
        shoulder = K.combine({"type": "RandomTarget", "range": p["e_reach"], "casting_target": "AllyNotSelf",
                              "from_projectile": False, "effects": [ward, kit.view("e_ward")]},
                             K.on_self(K.attack(0, 0, target_hp=p["e_cost_sim"]) | {"type": "FixedAttack"}))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "shield_bearer_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(shoulder))))

    # ------------------------------------------------------------------ R：卸城（三道楔浪画在他自己的帧里）
    if is_native:
        release = kit.native("release")
    else:
        release = cone(p["r_r"], p["r_cos"], [K.attack(p["r_dmg"] + p["r_p_sim"], p["r_ad"]),
                                              K.knockback(p["r_push"], p["r_push_t"]),
                                              kit.slow("r_slow", p["r_slow"], p["r_slow_t"]),
                                              K.delayed(p["r_push_t"], K.stun(p["r_stun"])) if p["r_stun"] else None])
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine(kit.flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                               {"type": "Sfx", "name": "knight_ult"},
                               K.delayed(p["r_hit"] - 1, kit.alive_only(release,
                                                                        {"type": "Sfx", "name": "shield_bearer_ult"}))))

    # ------------------------------------------------------------------ 画面
    # 打在人身上的珊瑚碎片、贴在队友身上的盾板、背压满一层时聚成的珍珠、替人挨打时身上的碎壳（tools/art/import_cenlei.py）
    views_e = kit.views([("a_hit", "a_hit"), ("e_ward", "e_ward"), ("p_pearl", "p_pearl"), ("hit", "hit")])
    # 楔浪的弹道画面只给塞拉斯偷去的卸城用（他自己的画在身体帧里）
    views_p = kit.projectile_views([("r_fan", "r_fan")], once=("r_fan",))
    stat, growth = K.stats(p)
    tags = ["AD", "Melee", "Tank", "CC", "Shield"]
    if not is_native:   # 经典 SDK（平衡模拟）没有 Tank 这个分类，写 Melee（终末包宙斯、赫拉克勒斯的做法）
        return kit.shell("Melee", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Tank", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="pressure",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的卸城（addons/league_sylas/make_override.py 的 STOLEN）：他没有背压（按 0 算），别的和原版一样：起手
    不受控制、减伤，r_hit 拍前方扇形每个敌人一下（伤害、推开、减速）。三道楔浪画在岑垒自己的帧里，塞拉斯身上没有，所以
    同一拍放一条不打人的线（r_fan，引擎把画面转到施法方向）当楔浪的画面。纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    release = cone(p["r_r"], p["r_cos"], [K.attack(p["r_dmg"], p["r_ad"]), K.knockback(p["r_push"], p["r_push_t"]),
                                          kit.slow("r_slow", p["r_slow"], p["r_slow_t"]),
                                          K.delayed(p["r_push_t"], K.stun(p["r_stun"])) if p["r_stun"] else None])
    fan = {"type": "LineRangeProjectile", "name": kit.n("r_fan"), "width": 1000, "length": p["r_r"], "delay": 25,
           "apply": 30, "applied_target": "EnemyChampion", "applied_effects": []}
    return K.combine(kit.flag("r_guard", p["r_hit"] + 1, cc_immune=True, damaged_reduce=p["r_dr"]),
                     {"type": "Sfx", "name": "knight_ult"},
                     K.delayed(p["r_hit"] - 1, kit.alive_only(fan, release, {"type": "Sfx", "name": "shield_bearer_ult"})))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
