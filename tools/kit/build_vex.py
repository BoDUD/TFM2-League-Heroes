"""按参数表 P 生成 league_vex.data_champion（中单，Magician）。

    python tools/kit/build_vex.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

技能方案（用户 2026-10-20：中单、方案 A——Q / E / R，W 进普攻，做附加包）。团战经理只有三个主动技能位：寒心波云（Q）是 `skill`，
溟濛渐染（E）是 `skill2`，愁煞（R）是 `ult`；生人勿近（W）在普攻里：她普攻时 w_r 内有敌方英雄、W 的冷却好了，这一下就放 W。
2026-11-26 照英雄联盟 V26.13 核对了一遍（docs/heroes/league_vex.md 的开发记录）：
  被动 终焉暮气  终焉：`p_wait` 不在时就绪（开局、用掉 p_cd tick 后）；下一个 Q、E 或 W 用掉它，这一下打中的敌人恐惧 p_fear tick，
          恐惧时减速 p_fslow%（英雄联盟：恐惧都带减速，按离她的远近 60%–99%）；恐惧前先 p_down tick 的击飞（英雄联盟的击倒：
          打断冲刺，引擎里击飞会取消冲刺）。终焉回来时她头上睁开影子的眼睛（`p_ready`）。
          暮气：溟濛渐染打中的敌人挂 `g_mark`（g_t tick）。英雄联盟里她下一次普攻或 Q / W 打中这个人就引爆。数据读不到敌人身上的
          buff，主包的替代做法：E 打中英雄后她身上开一个窗口 `g_win`，窗口里她第一下打中英雄的普攻、Q 或 W 补暮气伤害
          （g_dmg + g_ratio% 法强）；附加包照英雄联盟做。
  普攻   一团暗影弹（100% 攻击），追着 `Enemy`（防御塔也打），a_rel 出手。
  W      生人勿近，在普攻里：护盾 w_sh + w_sh_ratio% 法强（w_sh_t tick），身边 w_r 内的敌人受 w_dmg + w_ratio% 法强。
  skill  Q 寒心波云，`Targeting`（q_dir=0；1 是 `Direction`）施放在 `EnemyWithoutTower`（q_range）。英雄联盟的波先慢后快、
          先宽后窄：这里是两条线，宽的 `q_wave` 以 q_s1 飞到 q_l1（半径 q_w1，看得见），窄的 `q_dart` 晚一点出手、以 q_s2 飞到
          q_len（半径 q_w），宽的那条飞完时窄的正好在它前面 q_gap（两条线判定的边贴着），宽的飞完（它的 end_effects 给她挂
          `q_far`）才放开窄的打人：一个人不会被两条都打到。打中 q_dmg + q_ratio% 法强。英雄联盟出手就定死方向，这里 AI 不会
          预判，定死方向（Direction）打中英雄的比例掉一截，所以指向目标：窄的那条对准它出手时目标的位置。
  skill2 E 溟濛渐染，`Targeting` 在 `EnemyWithoutTower`（e_range）：影子（e_fly tick 的抛物线）飞到目标脚下扩散，半径 e_r：
          e_dmg + e_ratio% 法强，减速 e_slow% e_slow_t tick，挂暮气。
  ult    R 愁煞，`Targeting` 在 `EnemyChampion`（r_range）：影子飞弹追着英雄打：先挂标记 `r_mark`，再 r_dmg + r_ratio% 法强；
          r_wait tick 后她冲过去（`ult_dash`），r_into=0 停在他 r_stop 外（佐伊大招的跳），1 冲到他身上（冲刺时免控，到了再打），
          一击 r2_dmg + r2_ratio% 法强；生人勿近好了就落地放一次（英雄联盟的 R → W）。
附加包的副本（--native，addons/league_vex）：被动 league_vex:gloom 读打中的标记——暮气挂在每个敌人身上（E 打中的、她 p_dash_r 内
突进 / 闪现的英雄和野怪），她的普攻、Q、W 打中就引爆（伤害按等级，对英雄和对非英雄分开，终焉等待缩短 g_cut% / g_cut_u%）；
终焉的冷却和恐惧时长按等级；恐惧由附加包放（E 的从 E 的中心往外跑，减速按离她的远近），击倒照旧是数据的；
E 打死人也缩短终焉；愁煞冲不冲到他身上由附加包看能不能杀（`r_in`）；被标记的英雄 r_reset tick 内阵亡就刷新愁煞。
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_vex.data_champion")
ID = "league_vex"
FX = "asset/league/effects/league_vex_fx"
BIG = "asset/league/effects/league_vex_big"

# League units x 100 = ours (attack range 550 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings from the strips (tools/art/rig_vex.py MS): the attack's fling frame 2 from 80 ms (a_rel 6), Q's
# lunge frame 3 from 150 ms (q_rel 10), Personal Space's slam frame 3 from 130 ms (w_rel 9), E's kick frame 2 from 80 ms
# (e_rel 6), R's throw frame 3 from 150 ms (r_rel 10); each action as long as its strip. Numbers = the 10-min classic-SDK simulations
# (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides,
# 2026-10-20): the draft (hp 900, Q 70 + 60%, E 60 + 50% every 12 s, R 80 + 20% then a surge onto him 160 + 60% every
# 40 s) -4.69 (league_zoe +1.17 the same batch): the surge put her in the middle of the enemies (3.7 deaths a game; no
# surge -1.56, R only on champions hit lately -4.01). R landing with Personal Space and Q 95 + 70%, E 80 + 60%, the
# surge 200 + 70%, hp 960 -1.47 (no surge +0.48); the surge stopping r_stop short of the champion (league_zoe R's
# jump) 40000 +0.36, 48000 +0.77; + Gloom 60 + 30%, E every 10 s +0.65 / -0.02 (seeds 1-8 / 9-16); + R every 35 s
# +1.44 / +0.97 (about +1.2, league_zoe +1.17, league_volibear +1.39). Timed to the strips (the releases earlier, W's
# burst on its slam frame) +0.40 / +0.87; Q 105 +1.29 / +0.48, + the surge 230 +1.85 / +1.73, 215 +0.73 / +1.02, 225
# +0.97 / +1.17 (about +1.1) = P.
# 2026-11-26 照英雄联盟 V26.13 改（伤害、护盾、减速按英雄联盟各技能的比例，结果见开发记录）。
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Vex:
    # 590 +104 hp, 23 armour, 28 mr, 335 move, 550 range, attack speed 0.669
    "hp": 960, "hp_g": 95, "atk": 72, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 910, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 86, "a_rel": 6, "a_speed": 4500,
    # 被动（英雄联盟：终焉 25/22/19/16 秒、恐惧 0.75–1.5 秒按等级，恐惧时减速 60%–99%；暮气 6 秒，40–162.94 + 25% 法强）。
    # 主包读不到等级，用 1 级的数；附加包按等级（见下面附加包那几行）
    "p_cd": 900, "p_fear": 45, "p_fslow": 80, "p_down": 2, "g_t": 360, "g_dmg": 66, "g_ratio": 25,
    # W 生人勿近（英雄联盟：半径 475，80–240 + 30% 法强，护盾 50–150 + 75% 法强 2.5 秒，冷却 16–12 秒）
    "w_r": 40000, "w_cd": 720, "w_dur": 27, "w_rel": 9, "w_dmg": 105, "w_ratio": 30, "w_sh": 66, "w_sh_ratio": 75,
    "w_sh_t": 150,
    # Q 寒心波云（英雄联盟：射程 1200，70–250 + 70% 法强，冷却 8–4 秒；先 600 的速度、360 宽飞 500，再 3200、160 宽）。
    # 慢的一段 q_l1，快的那条飞完时在慢的前面 q_gap = 两条的半径 + 两个身位（判定边贴着，不重叠也不漏）
    "q_cd": 360, "q_range": 80000, "q_dur": 30, "q_rel": 10, "q_dir": 0,
    "q_s1": 2100, "q_w1": 18000, "q_l1": 39800, "q_s2": 10750, "q_w": 8000, "q_len": 95000, "q_gap": 46000,
    "q_dmg": 105, "q_ratio": 70,
    # E 溟濛渐染（英雄联盟：射程 800，半径 200–300 随施放距离，50–130 + 40–60% 法强，减速 30–50% 2 秒，冷却 12 秒（V26.13 从 13 改））
    "e_cd": 554, "e_range": 70000, "e_dur": 30, "e_rel": 6, "e_fly": 18, "e_r": 25000, "e_dmg": 59, "e_ratio": 50,
    "e_slow": 40, "e_slow_t": 120,
    # R 愁煞（英雄联盟：射程 2000–3000，飞弹 75–175 + 20% 法强，冲过去 150–350 + 50% 法强，冷却 140–100 秒）
    "r_cd": 2100, "r_range": 110000, "r_dur": 27, "r_rel": 10, "r_speed": 5000, "r_dmg": 82, "r_ratio": 20,
    # 冲到他身上时到了以后第 r_hit_at tick 打（ult_hit 第 2 帧砸下，100 ms）
    "r_wait": 8, "r_dash": 4500, "r_dash_anim": 24, "r2_dmg": 164, "r2_ratio": 50, "r_hit_dur": 24, "r_hit_at": 6,
    "r_surge": 1, "r_recent": 0, "r_w": 1, "r_stop": 48000, "r_jspeed": 6000, "r_into": 0,
    "vo_gap": 600,
    # 附加包（addons/league_vex）：终焉冷却 1 级 p_cd1，按英雄联盟的比例随等级缩短（一局下来平均和主包的 p_cd 差不多），
    # 恐惧 p_fear 到 p_fear4 按等级，恐惧减速离她
    # 越远越大（p_fs_lo% 到 p_fs_hi%，p_fs_d 外都是 p_fs_hi%）；暮气挂在 p_dash_r 内突进 / 闪现的人身上，引爆伤害 g_lo 到 g_hi
    # （按等级）+ g_ratio%，对非英雄打 g_u_lo% 到 g_u_hi%，缩短终焉等待 g_cut% / g_cut_u%；E 打死英雄 / 别的缩短 e_cut_c% /
    # e_cut%；愁煞标记后 r_reset tick 内阵亡，r_free tick 后能再放
    "p_cd1": 1200, "p_fear4": 90, "p_fs_lo": 60, "p_fs_hi": 99, "p_fs_d": 80000,
    "p_dash_r": 160000, "g_lo": 26, "g_hi": 107, "g_u_lo": 40, "g_u_hi": 60, "g_cut": 25, "g_cut_u": 10,
    "e_cut": 10, "e_cut_c": 25, "r_reset": 480, "r_free": 30, "r_kill": 100, "r_crowd": 1,
    # 副本里愁煞的冷却（附加包能刷新它）
    "r_cd_c": 2520,
    "native": 0,
}
# 附加包被动读的参数（passive.params，全是非负整数）
NATIVE_PARAMS = ("p_cd1", "p_fear", "p_fear4", "p_fs_lo", "p_fs_hi", "p_fs_d", "p_dash_r", "g_t", "g_lo", "g_hi",
                 "g_ratio", "g_u_lo", "g_u_hi", "g_cut", "g_cut_u", "e_cut", "e_cut_c", "e_r", "e_fly", "r_reset",
                 "r_free", "r_wait", "r_kill", "r_crowd", "r2_dmg", "r2_ratio", "w_dmg", "w_ratio")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def fear(tick):
    return {"type": "Fear", "tick": tick}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def around(r, target, effects):
    return {"type": "RangeEffect", "shape": circle(r), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def lob(name, travel, end):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def q_timing(p):
    """寒心波云两条线的时间：(宽的飞几 tick，窄的晚几 tick 出手，窄的飞完时宽的停在哪 / 窄的在哪)。
    一条线从出手那 tick 起每 tick 走 speed（第 k tick 在 speed × (k + 1)），飞到 range 就停。"""
    t1 = math.ceil(p["q_l1"] / p["q_s1"])          # 宽的第 t1 - 1 tick 到头
    t2 = math.ceil((p["q_l1"] + p["q_gap"]) / p["q_s2"])
    lag = t1 - t2
    if lag < 0:
        raise SystemExit("q_s2 too slow: the dart cannot reach q_l1 + q_gap while the wave flies")
    return t1, lag, p["q_l1"], p["q_s2"] * t2


def build(p):
    native = bool(p["native"])
    # Doom: spent by the cast that finds `p_wait` off; the Shadow's eyes flash on her when it is back
    spend = combine(sfx("p_fear"), flag("p_wait", p["p_cd"]), delayed(p["p_cd"], cview("p_ready"), sfx("p_ready")))
    # 附加包的副本：她的普攻、Q、W 打中的单位挂 2 tick 的 `v_hit`（E 和 R 不引爆暮气），终焉回来的画面由附加包放（等待会被缩短）
    vh = [buff("v_hit", 2)] if native else []
    if native:
        spend = combine(sfx("p_fear"), flag("p_wait", p["p_cd1"]))

    def doomed(plain, feared):
        """`plain` normally; with Doom ready `feared` (the same cast with a fear) and Doom spent."""
        return sw("p_wait", plain, combine(spend, feared))

    def scare(kind):
        """终焉：先击倒（2 tick 的击飞，打断冲刺），再恐惧。主包是数据的恐惧加减速；副本只挂个标记，附加包按等级放恐惧
        （`f_e`：从 E 的中心往外跑）。"""
        down = {"type": "Airborne", "duration": p["p_down"]}
        if native:
            return [down, buff("f_e" if kind == "e" else "f_q", 2)]
        return [down, fear(p["p_fear"]), buff("p_fslow", p["p_fear"], move_speed_mult=-p["p_fslow"])]

    # 暮气（主包的替代做法）：E 开的窗口里，她第一下打中英雄的普攻、Q 或 W 补暮气伤害
    pop = NONE if native else sw("g_win", combine(*rm("g_win"), ap(p["g_dmg"], p["g_ratio"]), view("g_pop"),
                                                  tsfx("g_pop")))

    # ------------------------------------------------------------------ attack: the dark bolt / W Personal Space
    bolt_a = homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")] + vh, p["a_speed"])
    # 主包：暮气窗口里普攻打中英雄也引爆（一颗只打英雄、看不见的同路弹）
    plain = combine(sfx("a"), bolt_a) if native else combine(
        sfx("a"), bolt_a, sw("g_win", homing("a_twin", "EnemyChampion", [pop], p["a_speed"])))

    def wave(scared):
        hit = [ap(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")] + vh + (scare("w") if scared else [])
        return combine(around(p["w_r"], "EnemyWithoutTower", hit), around(p["w_r"], "EnemyChampion", [pop]))

    def space(*pose, at=0):
        """Personal Space: the shield and the wave `at` ticks after its pose starts (skill_w's slam, frame 3)."""
        burst = combine(sfx("w"), voice("vo_w", p),
                        # on her: a Shield goes to the action's target (an enemy here, league_annie W's lesson)
                        pick(1, "AllyOnlySelf", {"type": "Shield", "amount": p["w_sh"], "attack_ratio": 0,
                                                 "ap_ratio": p["w_sh_ratio"], "tick": p["w_sh_t"]}),
                        cview("w_shield"), cview("w_ring"),
                        doomed(wave(False), wave(True)))
        return combine(*pose, flag("w_cd", p["w_cd"]), delayed(at, alive(burst)) if at else burst)

    personal = space(anim("skill_w", p["w_dur"]), at=p["w_rel"] - 1)
    near = combine(pick(p["w_r"], "EnemyChampion", flag("w_near", 1)),
                   sw("w_near", combine(*rm("w_near"), sw("w_cd", plain, personal)), plain))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(near))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Mistral Bolt
    # 宽的慢波先出手；它飞完（end_effects）给她挂 `q_far`，窄的快波这时才打人。窄的晚 lag tick 出手，宽的飞完那 tick
    # 它在宽的前面 q_gap：宽的判定边在 q_l1 + q_w1 + 身位，窄的从 q_l1 + q_gap - q_w - 身位 起打，正好接上
    t1, lag, _, _ = q_timing(p)

    def bolt_hits(scared):
        return [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")] + vh + (scare("q") if scared else [])

    def slow_wave(scared):
        out = [line("q_wave", p["q_s1"], p["q_l1"], p["q_w1"], "EnemyWithoutTower", bolt_hits(scared),
                    end=[flag("q_far", 3)], penetrate=True, y=5000)]
        if not native:      # the Gloom on a champion rides a hidden champion-only twin
            out.append(sw("g_win", line("q_twin", p["q_s1"], p["q_l1"], p["q_w1"], "EnemyChampion", [pop],
                                        penetrate=True, y=5000)))
        return combine(*out)

    def fast_dart(scared):
        out = [line("q_dart", p["q_s2"], p["q_len"], p["q_w"], "EnemyWithoutTower",
                    [sw("q_far", combine(*bolt_hits(scared)))], penetrate=True, y=5000)]
        if not native:
            out.append(sw("g_win", line("q_twin2", p["q_s2"], p["q_len"], p["q_w"], "EnemyChampion",
                                        [sw("q_far", pop)], penetrate=True, y=5000)))
        return combine(*out)

    # 终焉在宽的出手那一下用掉，给她挂 `q_scare`；窄的出手时照它带不带恐惧
    q_go = alive(doomed(slow_wave(False), combine(slow_wave(True), flag("q_scare", lag + 2))), sfx("q_fly"))
    q_dart_go = alive(sw("q_scare", combine(*rm("q_scare"), fast_dart(True)), fast_dart(False)))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Direction" if p["q_dir"] else "Targeting",
                   "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, q_go), delayed(p["q_rel"] - 1 + lag, q_dart_go)))

    # ------------------------------------------------------------------ skill2: E Looming Darkness
    def darkness(scared):
        hit = [ap(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
               buff("g_mark", p["g_t"]), tsfx("e_hit")] + (scare("e") if scared else [])
        land = [view("e_land"), sfx("e_land"), zone("e_zone", p["e_r"], hit)]
        if not native:
            land.append(zone("e_gloom", p["e_r"], [refresh("g_win", p["g_t"])], "EnemyChampion"))
        # 副本：出手时给目标挂 `e_aim`，附加包记下影子落在哪（恐惧往外跑的中心、打死人缩短终焉）
        aim = [buff("e_aim", 2)] if native else []
        return combine(cview("e_cast"), *aim, lob("e_fly", p["e_fly"], land))

    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(doomed(darkness(False), darkness(True))))))

    # ------------------------------------------------------------------ ult: R Shadow Surge
    # 生人勿近好了就落地放一次（英雄联盟的 R → W）；愁煞自己不引爆暮气（英雄联盟只有普攻和 Q、W）
    strike = [ap(p["r2_dmg"], p["r2_ratio"]), view("r_hit"), tsfx("r_hit")] + (
        [sw("w_cd", NONE, space())] if p["r_w"] else [])
    # 停在他 r_stop 外：佐伊大招的跳——一条看不见的线碰到第一个英雄就停、终点把她放过去，再从那里打
    surge_out = combine(anim("ult_dash", p["r_dash_anim"]), sfx("r_dash"),
                        line("r_surge", p["r_jspeed"], p["r_range"] + 30000, p["r_stop"], "EnemyChampion", [],
                             end=[{"type": "Teleport"}, anim("ult_hit", p["r_hit_dur"])], y=5000),
                        delayed(p["r_dash_anim"] // 2, *strike))
    # 冲到他身上（英雄联盟）：一直追，冲刺时免控，到了才打
    surge_in = combine(flag("r_safe", p["r_dash_anim"] + 6, cc_immune=True), anim("ult_dash", p["r_dash_anim"]),
                       sfx("r_dash"),
                       {"type": "MoveToTarget", "speed": p["r_dash"], "range": 400000,
                        "end_effects": [*rm("r_safe"), anim("ult_hit", p["r_hit_dur"]),
                                        delayed(p["r_hit_at"], *strike)]})
    if native:
        surge = sw("r_in", combine(*rm("r_in"), surge_in), surge_out)
    else:
        surge = surge_in if p["r_into"] else surge_out
    # 标记先挂上再扣血：飞弹自己打死他也算（附加包看得到标记）
    marked = [buff("r_mark", p["r_wait"] + 30), ap(p["r_dmg"], p["r_ratio"]), tsfx("r_mark"),
              delayed(p["r_wait"], alive(surge)) if p["r_surge"] else delayed(p["r_wait"], *strike)]
    ult = action("ult", p["r_dur"], p["r_cd_c"] if native else p["r_cd"], 1, p["r_range"], "Targeting",
                 "EnemyChampionRecentlyAttacked" if p["r_recent"] else "EnemyChampion",
                 combine(decoy(p["r_dmg"] + p["r2_dmg"], p["r_ratio"] + p["r2_ratio"], ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive(homing("r_missile", "EnemyChampion", marked, p["r_speed"]),
                                                       sfx("r_fly")))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    views_p = [Pj("a_bolt"), Pj("q_wave"), Pj("q_dart"), Pj("r_missile")]
    views_e = [E("a_hit"), E("q_hit"), E("w_hit"), E("w_ring", BIG, -1), E("w_shield", FX, 3), E("e_cast", FX, 3),
               E("e_land", BIG, -1, False), E("r_hit"), E("p_ready", FX, 3)]
    if not native:
        views_e.append(E("g_pop"))
    views_b = [B_("e_slow", FX, -1), B_("g_mark", FX, 3), B_("r_mark", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_vex:gloom", "params": {k: p[k] for k in NATIVE_PARAMS}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC", "Shield"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--native", action="store_true", help="the add-on's copy")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    if a.native:
        p["native"] = 1
    kit = build(p)
    if a.nodes:
        for s in ("attack", "skill", "skill2", "ult"):
            print(f"{s:7s} {nodes(kit[s]['effect']):4d} nodes")
    text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    with open(lp(a.out), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(a.out, len(text))


if __name__ == "__main__":
    main()
