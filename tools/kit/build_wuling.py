"""雾绫（边境巡团 border_wuling，辅助）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_wuling.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

控场辅助，铃与纱幕。美术、图标、配音是 Codex 的（assets/source/border/），技能照 Codex 的角色合同：
  被动    闻铃：敌人第一次碰到她的技能区域（地铃响、穿过纱幕、被合幕卷进去）就被标记（border_wuling_bell，p_t 拍，身上
          挂一只小铃）；被标记的人掉血时，离他 p_ally_r 内的友方英雄移速 +p_ms% p_ms_t 拍（打中他的那几个人都在旁边）。
  attack  铃音 `Enemy`：弹道（a_speed）打中 100% 攻击力的物理伤害，再加 a_ap% 法强的魔法伤害。
  skill   系铃：`Targeting` EnemyWithoutTower（q_range）：q_hit 拍在目标脚下放一只地铃（q_t 拍）；有敌人走到它 q_trig 内就响：
          q_r 内的敌人吃 q_dmg + q_ap% 法强的魔法伤害、减速 q_slow% q_slow_t 拍、被标记。放在人身上的下一拍就响。
  skill2  挪幕：`Targeting` 敌方英雄（e_range，交战时才放）：e_hit 拍在她和目标之间（e_frac% 处）竖起一道短幕（长 e_len，和
          她到目标的方向垂直，e_t 拍）：友方英雄穿过去移速 +e_ms% e_ms_t 拍（每人每道幕一次）；敌人穿过去被标记、减速
          e_slow%。纱幕是竖着的，画面不转。
  ult     合幕：`Targeting` 敌方英雄（r_range）：r_on 拍（第 3 帧，0.40 秒）在目标脚下两侧拉起两道幕往中间合，r_land 拍后合上：
          r_r 内的敌人每人只结算一次：r_dmg + r_ap% 法强的魔法伤害、减速 r_slow%，再定身 r_root 拍，被标记。

时间按 Codex 的 art_index.json（一秒 60 拍）：普攻 0.46 秒、系铃 / 挪幕 0.56 秒（第 3 帧 0.26 秒）、合幕 0.87 秒（第 3 帧 0.40 秒）。

border.dll（addons/border/src/wuling.rs）：被动 border_wuling:bell（闻铃、地铃、纱幕的穿越），原生效果 border_wuling:bell_drop /
curtain / close / close_hit。--plain 和塞拉斯版：地铃、合幕是目标脚下的数据圈，纱幕换成她身边友军的移速。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_kit as K  # noqa: E402

ID = "border_wuling"
OUT = os.path.join(K.REPO, K.MOD_ID, "champion", f"{ID}.data_champion")
kit = K.Kit(ID)

# 数值：经典 SDK 模拟（C:/t/lb_sim/border_var.sh wuling 4 ...，辅助 lane 4，600 秒，对手是五个原版辅助，8 个种子），2026-11-22。
# 联盟辅助（阿利斯塔 -0.60、蕾欧娜 -0.29、布隆 -0.07、锤石 +0.58、洛 +1.21、诺提勒斯 +2.99，中位数约 +0.26）。初稿 -5.02：
# 数据版的地铃、纱幕、合幕原来生成在她自己脚下，整局一下都没打中；改成丢到目标脚下（kit.lob）后原值 -1.44。合幕落得快一点、
# 圈大一点、定身长一点，三个技能的减速和伤害、一点血和双抗（这份）两组种子 +0.54 / +0.65。
P = {
    # 属性（辅助）
    "hp": 930, "hp_g": 88, "atk": 78, "atk_g": 6, "apw": 35, "apw_g": 16, "def": 24, "def_g": 7, "mr": 25, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 85, "atk_st": 13, "a_speed": 5500, "a_ap": 25,
    # 被动：闻铃
    "p_t": 300, "p_ms": 15, "p_ms_t": 60, "p_ally_r": 60000,
    # 系铃
    "q_cd": 420, "q_range": 60000, "q_dur": 34, "q_hit": 16, "q_t": 300, "q_trig": 16000, "q_r": 26000, "q_dmg": 75,
    "q_ap": 60, "q_slow": 50, "q_slow_t": 90,
    # 挪幕
    "e_cd": 600, "e_range": 60000, "e_dur": 34, "e_hit": 16, "e_len": 30000, "e_t": 240, "e_ms": 30, "e_ms_t": 120,
    "e_frac": 40, "e_slow": 30, "e_slow_t": 60,
    # 合幕
    "r_cd": 3000, "r_range": 65000, "r_dur": 52, "r_on": 24, "r_land": 12, "r_r": 33000, "r_dmg": 160, "r_ap": 80,
    "r_slow": 45, "r_slow_t": 30, "r_root": 75,
}

NATIVE = ["p_t", "p_ms", "p_ms_t", "p_ally_r", "q_t", "q_trig", "q_r", "q_dmg", "q_ap", "q_slow", "q_slow_t", "e_len",
          "e_t", "e_ms", "e_ms_t", "e_frac", "e_slow", "e_slow_t", "r_land", "r_r", "r_dmg", "r_ap", "r_slow",
          "r_slow_t", "r_root"]


def circle(name, radius, apply, effects):
    """数据版的圈：生成的地方往后 apply 拍结算。要放在目标脚下就装进 kit.lob 丢过去。"""
    return {"type": "RangeProjectile", "name": kit.n(name), "shape": {"Circle": {"radius": radius}},
            "delay": apply + 1, "apply": apply, "applied_target": "EnemyWithoutTower",
            "applied_effects": [{"casting_type": "Targeting", "effect": K.combine(*effects)}]}


def plain_close(p):
    """数据版的合幕：目标脚下的圈，r_land 拍后合上（伤害、减速、定身），画面放在目标身上。"""
    zone = circle("r_zone", p["r_r"], p["r_land"] + 1,
                  [K.ap_attack(p["r_dmg"], p["r_ap"]), kit.slow("r_slow", p["r_slow"], p["r_slow_t"]),
                   {"type": "Bind", "duration": p["r_root"]}])
    return K.combine(kit.view("r_close"), kit.lob("r_lob", zone))


def build(p, is_native=True):
    # ------------------------------------------------------------------ 普攻：铃音
    bolt = {"type": "TargetProjectile", "name": kit.n("a_bolt"), "speed": p["a_speed"], "y_offset": -1500,
            "applied_target": "Enemy",
            "applied_effects": [{"casting_type": "Targeting",
                                 "effect": K.combine(K.attack(0, 100), K.ap_attack(0, p["a_ap"]), kit.view("a_hit"))}]}
    attack_a = kit.action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                          K.combine(bolt, {"type": "Sfx", "name": "bard_attack"}), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：系铃
    if is_native:
        bell = kit.native("bell_drop")
    else:
        bell = kit.lob("q_lob", circle("q_zone", p["q_r"], 2, [K.ap_attack(p["q_dmg"], p["q_ap"]),
                                                               kit.slow("q_slow", p["q_slow"], p["q_slow_t"])]))
    skill = kit.action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                       K.combine({"type": "Sfx", "name": "bard_skill1"},
                                 K.delayed(p["q_hit"] - 1, kit.alive_only(bell))))

    # ------------------------------------------------------------------ E：挪幕
    if is_native:
        curtain = kit.native("curtain")
    else:
        curtain = K.combine({"type": "RangeEffect", "shape": {"Circle": {"radius": 40000}}, "target": "AllyChampion",
                             "apply_type": "AroundCaster",
                             "effects": [kit.buff("e_ms", p["e_ms_t"], move_speed_mult=p["e_ms"])]},
                            kit.lob("e_lob", circle("e_zone", 20000, 2,
                                                    [kit.slow("e_slow", p["e_slow"], p["e_slow_t"])])))
    skill2 = kit.action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                        K.combine({"type": "Sfx", "name": "bard_skill2"},
                                  K.delayed(p["e_hit"] - 1, kit.alive_only(curtain))))

    # ------------------------------------------------------------------ R：合幕
    if is_native:
        close = K.combine(K.delayed(p["r_on"] - 1, kit.alive_only(kit.native("close"))),
                          K.delayed(p["r_on"] + p["r_land"] - 1, kit.alive_only(kit.native("close_hit"))))
    else:
        close = K.delayed(p["r_on"] - 1, kit.alive_only(plain_close(p)))
    ult = kit.action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                     K.combine({"type": "Sfx", "name": "enchanter_ult"}, close))

    # ------------------------------------------------------------------ 画面
    views_e = kit.views([("a_hit", "a_hit"), ("p_bell", "p_bell")])
    views_e += kit.views([("q_bell", "q_bell"), ("q_ripple", "q_ripple"), ("e_curtain", "e_curtain"),
                          ("r_close", "r_close")], follow=False)
    views_p = kit.projectile_views([("a_bolt", "a_bolt")])
    stat, growth = K.stats(p)
    tags = ["AP", "Magic", "CC", "Range"]
    if not is_native:
        return kit.shell("Util", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p)
    return kit.shell("Util", tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p, passive="bell",
                     params={k: p[k] for k in sorted(NATIVE)})


def sylas_ult(p=None):
    """塞拉斯偷到的合幕（STOLEN）：目标脚下合上两道幕（伤害、减速、定身）。纯数据：不靠 border.dll。"""
    p = dict(P) if p is None else p
    return K.combine({"type": "Sfx", "name": "enchanter_ult"}, K.delayed(p["r_on"] - 1, kit.alive_only(plain_close(p))))


if __name__ == "__main__":
    K.main(P, build, OUT, __doc__)
