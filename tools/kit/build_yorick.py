"""Build league_yorick.data_champion (top, Melee fighter-tank, AD: Yorick, the Shepherd of Souls) from the parameters P.

    python tools/kit/build_yorick.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-25: TOP, layout A - Q / E / R; combos all four: E's mark -> the walkers pounce and Q is
ready, W's wall -> E at once, R's Maiden -> Q ready, Q's graves -> walkers). TFM2 has three active slots for League's
four buttons: Last Rites (Q) is `skill`, Mourning Mist (E) `skill2`, Eulogy of the Isles (R) the `ult`; Dark Procession
(W) has no slot - the controller casts it in fights (league_rammus's W, league_jarvaniv's Golden Aegis the same way).
Q, E and W keep their cooldowns in flags (`q_cd`, `e_cd`, `w_cd`; league_sejuani's) so the combos can cast them; a slot
cast while its flag is up does nothing (a 3-tick idle). Flags die with him: a respawned Yorick has Q, E and W ready -
and no graves.
Summons cannot walk or attack in data (champion-data "A summon that follows its target"): the Mist Walkers ride on the
unit they are raised on (league_malzahar's voidlings): an `AddCasted` on it bites every k_p ticks and plays their
pictures there; its death ends them. The Maiden follows Yorick as a picture on him (an `AddCasted` on him: it ends with
his death, as League's Maiden does).

2026-11-22（用户：「之前玩掘墓我也发现没完美还原 没有那个地形框出来的技能 其他我不知道 你再核对一下」）照英雄联盟现在的
约里克（V25.07 重做后的样子）改：暗灵缠身从唤醒里拆出来，单独做成一圈墙；坟最多 4 座、唤醒按坟数出雾行者；哀伤之雾以目标最大
生命为主；室女跟着他、远程攻击、挂标记。
  passive Shepherd of Souls (牧魂人): graves - Q on a champion digs one, Q on anything else every second time (League:
          a kill or a champion / large monster; the data cannot read a kill on the spot). They are counted on him
          (hidden caster buffs g1..g4, League's at most 4): 每挖一座，已有的几座一起重新计时 g_t（英雄联盟的坟没有时限，
          他走远或阵亡才没；这里坟只是他身上的计数，用 g_t 代替「走远」），所以 g1..gk 总是一起在、一起没，技能栏的坟数就是
          最高的那一级。With g_n (3) or more graves his next Q raises one walker a grave (Awakening, League's Q2; his
          `awaken` tag instead of `skill`): 3 or 4 walkers on the target for k_t ticks, each bite k_dmg + k_ratio% AD.
          英雄联盟里满 3 座就能再按 Q 唤醒，玩家常攒到 4 座：这里 4 座就唤醒，3 座时 q_near 以内有敌方英雄才唤醒，清线时
          接着挖第 4 座。
  W       暗灵缠身 (Dark Procession), 由控制器放（没有技能格）：w_cd 好了、w_range 内有敌方英雄就放——铲子插进地里（`awaken`
          的前 w_dur tick），一个 1 tick 的隐藏抛射落在那名英雄脚下，地上先裂开一圈（w_wall 的画面），w_delay tick
          （英雄联盟 0.75 秒）后墙立起来 w_t tick（英雄联盟 4 秒；主包 1 秒、附加包 w_tn = 2 秒，见下面的数值）。
          数据造不了地形，主包这样近似：
          * 立墙那一 tick：离圆心 w_in 以内（算上身体）的敌方英雄挂 3 tick 免控，下一 tick w_out 以内的敌方英雄被往圆心
            拉 w_ps x w_pt（站在墙线上的被拉进圈里；英雄联盟里墙线外侧的会被推出去，数据推不出去，一律拉进来），
            同时脚下冒出抓脚的鬼手（w_hit），哀伤之雾冷却清零并扔向被困的英雄（W -> E）；
          * 之后每 tick：w_in 以内的敌方英雄加速 w_slow%，w_out 以内的敌方英雄减速 w_slow%、不能用位移技能（不同名的
            buff 也相加：圈里两个抵消，只有墙那一圈净减速 99%）——圈里的走到墙边就走不动、也冲不出去，圈外的走到墙边也
            进不来；约里克和队友不受影响。
          圈外的冲刺、闪现数据挡不住；小兵、野怪不挡（只挡英雄）。附加包是真的墙（见下）。唤醒不再定身。
          数值（经典引擎模拟，2026-11-22）：墙立 w_t = 1 秒（英雄联盟 4 秒，但敌方英雄普攻 2–4 下就塌；游戏的 AI 不打墙，主包
          又做不了打塌，不能打塌的墙困 4 秒击杀差 +5、2 秒 +2、1 秒和不放 W 差不多），冷却 w_cd = 20 秒（英雄联盟 20 -> 12 秒
          取最长那一级）。W -> E 每 w_ccd = 120 秒最多一次（以前的笼子跟着唤醒，一局约 4 次；现在 W 每 20 秒就有，每次都清 E
          冷却的话击杀差多 +3）。附加包的真墙能打塌，最多立 w_tn = 2 秒：附加包副本在经典引擎里（C:/t/yo_sim 的 sim3yo，
          src/yo_emul.rs 照附加包做墙、坟、回复、加速、标记）立 4 秒击杀差 +1.59 / +1.21、2 秒 +0.88 / +0.45、1.5 秒
          -0.21 / +0.15（改前主包 +0.67 / +0.55）。
  attack  A shovel blow (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; 室女的标记在他身上（r_mk）时，
          打中英雄消耗标记：英雄最大生命 r_pct% 的真实伤害（英雄联盟：魔法伤害，只打有标记的那个英雄；数据读不到目标身上
          的标记，主包是打中的任何英雄）。
  skill   Q Last Rites (临终仪式), `Targeting` on `EnemyWithoutTower` in melee reach (q_range, `q_cd`): on q_hit a heavy
          blow q_dmg + q_ratio% AD and he heals q_heal + q_heal_r% AD (英雄联盟按已损失生命回复，数据读不到生命；附加包照
          英雄联盟); the grave as above.
  skill2  E Mourning Mist (哀伤之雾), `Targeting` on `EnemyWithoutTower` (e_range, `e_cd`): on e_rel a globule of mist is
          lobbed at the target (e_fly ticks); every enemy within e_r of where it lands takes e_dmg + e_ratio% AD +
          e_hp% of its maximum health（以最大生命为主，英雄联盟 6-8%；数据里按最大生命算的伤害做不成魔法，这里是物理）,
          e_arm% less defence for e_t ticks (the mark) and e_slow% slower for e_slow_t. 打中英雄时约里克 e_t tick 内移速
          +e_ms%（英雄联盟：朝被标记的英雄走时 +18-30%；数据读不到朝向，标记在的这段时间都算）；室女的标记在时也消耗它。
  ult     R Eulogy of the Isles (海屿悼词), `Targeting` on `EnemyChampion` within r_range: on r_rel r_n walkers rise on the
          champion and the Maiden rises behind him (r_rise): 她跟着约里克 r_t tick（一个挂在他身上的 AddCasted：他阵亡就
          一起没），每 r_p tick 朝他 r_reach 以内的一个敌方英雄（没有就打别的敌人）放一道魂弹（r_bolt，r_dmg + r_ratio%
          攻击力），打中英雄就给约里克挂上标记 r_mk（r_mk_t tick，目标头上有画面 r_mkv）。While she stands (`r_on`) Q
          comes back in q_cd_r ticks instead of q_cd.
  combos  E -> walkers + Q: the mist on an enemy champion makes the walkers he has raised (`k_on`) pounce on it (k_jmp +
          k_jmp_r% AD) and takes `q_cd` off; the controller strikes Q at the first champion in reach (`q_go`, q_go_t ticks).
          W -> E: the wall takes `e_cd` off and the controller throws the mist at a champion in reach (`e_go`).
          R -> Q: the Maiden's rising takes `q_cd` off (`q_go` for r_go_t ticks), and while she stands Q comes back in
          q_cd_r ticks instead of q_cd. Q -> walkers: the graves above.
  controller An AddCasted pulse on him every ctl_p ticks (league_sejuani's, hung by his attack and the ult, only for
          Yorick himself: `own`): the combos' casts and W.
The add-on copy (--native, addons/league_yorick 0.3.0) - 英雄联盟的规则，数据读不到的部分由附加包做:
  * passive league_yorick:shepherd (params from P: r_pct g_t w_r w_half w_t w_delay);
  * Q：这一铲给他挂 q_win（附加包给这一铲打死的每个单位挖坟，不再「每两下」）和 q_hl（附加包按已损失生命回复，打英雄全额，
    别的一半），数据自己的回复去掉；唤醒出手时去掉 k_unit、给目标挂 k_ask（3 座坟）或 k_ask4（4 座），挂在目标身上的雾行者
    只在约里克身上没有 k_unit 时放（附加包生成了真的雾行者就挂上它）；
  * W：落点那名英雄挂 w_ask（附加包记下圆心），立墙那一 tick 约里克挂 w_up（附加包立起真的墙：只挡敌人，拨开墙线上的人，
    闪现放过）；没有主包的拉人、加减速；
  * E：打中的英雄挂 e_ask（附加包让雾行者扑过去）和 3 tick 的 hit（附加包消耗室女的标记）；没有数据的加速（附加包按「朝被
    标记的英雄走」给约里克、雾行者、室女加速）；
  * R：出手时去掉 m_unit、给目标挂 m_ask；挂着的室女、她的魂弹和两只雾行者只在约里克身上没有 m_unit 时放（附加包生成了
    真的室女就挂上它）；普攻打中英雄挂 3 tick 的 hit（附加包消耗室女挂在那名英雄身上的标记）。
Timings: frames by tools/art/rig_yorick.py (attack 500 ms, Q / the Awakening 500, E 433, R 567 ms; W plays the first
350 ms of `awaken`: the shovel planted).
Numbers: League 16.21 read into the top fighter range (league_kled, league_darius, league_illaoi), balanced on the
classic-SDK simulations (kd.py --lane 0 against fighter, executioner, knight, berserker, lancer and pole_warrior,
C:/t/yo_sim, 2026-10-25; league_gnar --native the control: +0.01 / +0.59 on seeds 1-8 / 9-16): the draft (hp 1080,
attack 90, Q 40 + 140% every 300, walkers 8 + 12%, E 60 + 60%, R 40%) +0.05 / -0.98; hp 1140, attack 94, defence 36, Q 55
every 270, walkers 10 + 14%, E 70 + 70%, R 50% +1.70 (1-16); P (hp 1100, attack 91, defence 35, Q 45 every 285, walkers
9 + 13%, E 65 + 65%, R 45%) +0.44 (1-16; league_kled +0.29). 2026-11-22 的数值见 docs/heroes/league_yorick.md 的开发记录。
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stack_nums  # noqa: E402  (技能栏的坟数，tools/kit/stack_nums.py)

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_yorick.data_champion")
ID = "league_yorick"
FX = "asset/league/effects/league_yorick_fx"
BIG = "asset/league/effects/league_yorick_big"

# League's Yorick (16.21): 650 +114 hp, 62 AD +5, 36 armour +4.5, 32 mr +2.05, 340 move, 175 range, 0.625 attack speed.
# Passive: graves from Q (champion / large monster / kill) and every Nth death near him, max 4; walkers 100-331 hp,
# 15-113 AD. Q: next attack 30-110 + 50% AD, heals 10-78 + 6-10% missing hp, cd 6-4; Awakening (3+ graves) one walker a
# grave. W: a ring of 18 spirits 4 s after 0.75 s, impassable to enemies, cd 20-12. E: mist 6-8% max hp magic, slow 30%,
# armour -13-25% and haste toward the marked 4 s. R: the Maiden + 2-4 walkers, she follows him, attacks from 600 and marks
# champions: his next attack / E on the marked deals 2-3% max hp magic, cd 160-100.
P = {
    # stats (base fighters: attack 90 +12, hp 1000 +100, defence 35 +8; league_kled 1040 / 100, league_darius)
    "hp": 1100, "hp_g": 100, "atk": 91, "atk_g": 14, "apw": 10, "apw_g": 5, "def": 35, "def_g": 8, "mr": 26, "mr_g": 4,
    "ms": 1000, "ms_g": 10, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 80, "a_hit": 12,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: graves (g1..g4; g_n of them wake the walkers, one walker a grave) and the walkers
    "g_t": 1800, "g_n": 3, "k_t": 360, "k_p": 60, "k_dmg": 9, "k_ratio": 13,
    "k_jmp": 20, "k_jmp_r": 30,
    # W Dark Procession, cast by the controller: the ring's line w_r (30 px, tools/art/yorick_wall_ring.py), a champion's
    # centre kept within w_r - w_half inside and beyond w_r + w_half outside (20000 / 40000). The main pack's zones count
    # the unit's body (a champion's ~15000: classic sim, the trapped one stopped 15600 past the zone): free inside w_in
    # (20000 - 15000), the wall's band to w_out (40000 - 15000), the pull onto the inside at the rise (w_ps x w_pt = the
    # band's 20000), w_slow% each way; w_cage: the champions the wall caught (the add-on copy's W -> E and the hands:
    # League pulls in what stands within 210 of the line's 225, 28000 here)
    "w_cd": 1200, "w_range": 40000, "w_dur": 21, "w_rel": 17, "w_delay": 45, "w_t": 60, "w_r": 30000, "w_in": 5000,
    "w_out": 25000, "w_slow": 99, "w_ps": 2000, "w_pt": 10, "w_cage": 13000, "w_block": 1, "w_combo": 1, "w_ccd": 7200,
    # skill: Q Last Rites
    "q_cd": 285, "q_cd_r": 150, "q_range": 25000, "q_dur": 30, "q_hit": 14, "q_dmg": 45, "q_ratio": 140,
    "q_heal": 30, "q_heal_r": 20, "q_go_t": 120, "q_near": 45000,
    # skill2: E Mourning Mist
    "e_cd": 540, "e_range": 55000, "e_dur": 26, "e_rel": 12, "e_fly": 16, "e_r": 15000, "e_dmg": 40, "e_ratio": 25,
    "e_hp": 5, "e_arm": 25, "e_t": 240, "e_slow": 30, "e_slow_t": 90, "e_go_t": 60, "e_ms": 20,
    # ult: R Eulogy of the Isles - the Maiden follows him (her rising r_up ticks, then a bolt every r_p ticks at an enemy
    # within r_reach of him, r_bolt a tick), r_n walkers ride the champion
    "r_cd": 4800, "r_range": 40000, "r_dur": 34, "r_rel": 16, "r_t": 600, "r_p": 60, "r_dmg": 20, "r_ratio": 45,
    "r_n": 2, "r_pct": 3, "r_go_t": 120, "r_up": 42, "r_reach": 40000, "r_bolt": 3500, "r_mk_t": 240,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_yorick (League's rules the data cannot read; see the docstring); w_half: the real
    # wall's half thickness (the add-on), w_tn: its ticks (League's 4 s; the champions it holds break it there, the
    # main pack's w_t stands for that; 2 s here: 附加包副本在经典引擎里模拟 4 秒 +1.40、2 秒 +0.67、1.5 秒 -0.03，
    # 改前主包 +0.61), q_win: ticks of the flag that tells the add-on a unit died to Last Rites
    "native": 0, "q_win": 4, "w_half": 10000, "w_tn": 120,
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1, apply=1):
    """A one-shot area (champion-data section 4: it hits apply - 1 ticks after it appears, gone at delay - 1)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects, first=1):
    """A standing area: every `period` ticks for `tick` ticks (first_delay 1: from the tick it appears when a Delayed
    starts it, champion-data section 4)."""
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    ctl_p = p["ctl_p"]
    native = bool(p["native"])

    def unless(name, *effects):
        """附加包副本：约里克身上有 `name`（附加包生成了真的单位）时不放这些挂着的画面和伤害。"""
        return sw(name, NONE, combine(*effects))

    # ------------------------------------------------------------------ the walkers (on the unit in hand)
    def walkers(k):
        """k Mist Walkers on this unit for k_t ticks: one bite of all of them every k_p ticks, their pictures on it."""
        return combine(refresh("k_on", p["k_t"]), view("k_spawn"), tsfx("k_spawn"),
                       casted(p["k_t"], p["k_p"], attack(p["k_dmg"] * k, p["k_ratio"] * k), view("k_bite"),
                              tsfx("k_bite"), kind="Fire"),
                       casted(p["k_t"], 60, view("k_swarm")))

    # ------------------------------------------------------------------ passive: graves (g1..g4, counted on him)
    def graves(k):
        # 挖一座坟：g1..gk 一起重新计时（一起在、一起没，技能栏的坟数就是最高那一级）
        return combine(*[refresh(f"g{i}", p["g_t"]) for i in range(1, k + 1)])
    grave = combine(view("q_grave"), tsfx("q_grave"),
                    sw("g3", graves(4), sw("g2", graves(3), sw("g1", graves(2), graves(1)))))

    def awake(k):
        # 唤醒：坟都用掉，每座坟一只雾行者（附加包副本：约里克身上有 k_unit 时是真的单位，挂着的不放）
        ride = walkers(k)
        if native:
            ride = unless("k_unit", ride)
        return combine(*rm("g1", "g2", "g3", "g4"), sfx("q_awake"), homing("q_raise", "EnemyWithoutTower", [ride]))
    awaken = sw("q_awk", sw("g4", awake(4), awake(3)))
    # 什么时候唤醒（英雄联盟里 3 座以上就能再按 Q，玩家常攒到 4 座）：4 座就唤醒；3 座时 q_near 以内有敌方英雄才唤醒，
    # 没有（清线）就接着挖第 4 座。出手那一拍定下来（q_awk 留到这一铲落地），动作和落地都看它
    decide = combine(*rm("q_awk"), sw("g4", flag("q_awk", p["q_hit"] + 2),
                                      sw("g3", around(p["q_near"], "EnemyChampion", refresh("q_awk", p["q_hit"] + 2)))))

    # ------------------------------------------------------------------ Q Last Rites
    def q_cast():
        # a grave: on a champion always (its twin), on anything else every second Q (`q_half`); the check waits a tick
        # for the twin's `q_ch`
        champ = homing("q_tw", "EnemyChampion", [refresh("q_ch", 3), grave])
        other = sw("q_ch", NONE, sw("q_half", combine(*rm("q_half"), pick(p["q_range"], "EnemyWithoutTower", grave)),
                                   flag("q_half", None)))
        win, late, mend = None, delayed(2, alive(other)), heal(p["q_heal"], p["q_heal_r"])
        if native:      # the add-on digs a grave for each unit the blow kills (League), not every second blow:
            # `q_win` goes up with the blow, before it lands (the homing blow lands on the next tick; raised 2 ticks
            # later, as the main pack's check, it came after the kill - 11-03 night logs: 6 lives, 0 GRAVE)
            # 回复也交给附加包（按已损失生命）：q_hl 和这一铲同一拍挂上，打英雄时孪生弹下一拍挂上 q_ch
            win, late, mend = refresh("q_win", p["q_win"]), None, refresh("q_hl", 4)
        blow = combine(sfx("q_hit"), mend, win,
                       homing("q_blow", "EnemyWithoutTower", [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"),
                                                              tsfx("q_hit")]),
                       awaken, champ, late)
        start = anim("awaken", p["q_dur"])
        if native:      # 唤醒出手：去掉上一次的 k_unit，给目标挂 k_ask / k_ask4（附加包生成 3 / 4 只真的雾行者）
            start = combine(start, *rm("k_unit"), sw("g4", buff("k_ask4", 3), buff("k_ask", 3)))
        return combine(sw("r_on", refresh("q_cd", p["q_cd_r"]), refresh("q_cd", p["q_cd"])), *rm("q_go", "q_ch"),
                       refresh("busy", p["q_dur"]), decide, sw("q_awk", start, anim("skill", p["q_dur"])), sfx("q"),
                       voice("vo_q", p), delayed(p["q_hit"] - 1, alive(blow)))

    def spend():
        """The Maiden's mark on him spent on the champion in hand: r_pct% of its maximum health (true damage)."""
        return sw("r_mk", combine(*rm("r_mk"), pct(p["r_pct"]), view("r_mark"), tsfx("r_claw")))

    # ------------------------------------------------------------------ E Mourning Mist
    def e_cast():
        # E -> walkers + Q: on a champion the walkers he has raised pounce on it, and Q is ready (`q_go`); the Maiden's
        # mark on him is spent (the main pack: on whichever champion the mist strikes)
        once = [flag("e_lk", p["e_fly"] + 4), sw("k_on", combine(attack(p["k_jmp"], p["k_jmp_r"]), view("k_leap"),
                                                                tsfx("k_leap"))),
                *rm("q_cd"), refresh("q_go", p["q_go_t"]), spend()]
        if native:      # 附加包：雾行者扑过去（e_ask）、室女的标记在这名英雄身上就消耗（hit）；加速由附加包按朝向给
            once += [buff("e_ask", 3), buff("hit", 3)]
        else:
            once.append(refresh("e_ms", p["e_t"], move_speed_mult=p["e_ms"]))
        champ = homing("e_tw", "EnemyChampion", [sw("e_lk", NONE, combine(*once))], speed=4000)
        hit = [attack(p["e_dmg"], p["e_ratio"], p["e_hp"]), buff("e_mark", p["e_t"], defence_mult=-p["e_arm"]),
               buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"), tsfx("e_hit")]
        mist = lob("e_mist", p["e_fly"], p["e_r"], "EnemyWithoutTower", hit, end=[view("e_cloud"), sfx("e_land")])
        return combine(refresh("e_cd", p["e_cd"]), *rm("e_go", "e_lk"), refresh("busy", p["e_dur"]),
                       anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                       delayed(p["e_rel"] - 1, alive(mist, champ)))

    # ------------------------------------------------------------------ W Dark Procession (the controller casts it)
    def w_cast():
        combo = [*rm("e_cd"), refresh("e_go", p["e_go_t"])]
        if p["w_ccd"]:      # W -> E 最多每 w_ccd tick 一次（墙困住几个英雄也只清一次）
            combo = [sw("w_ccd", NONE, combine(flag("w_ccd", p["w_ccd"]), *combo))]
        if native:      # 附加包立真的墙：落点的英雄挂 w_ask（附加包记圆心），立墙那一 tick 他挂 w_up
            ask, rise = [buff("w_ask", 3)], [
                sfx("w_wall"), refresh("w_up", 3),
                zone("w_cage", p["w_cage"], "EnemyChampion", [view("w_hit"), tsfx("w_hit"),
                                                              *(combo if p["w_combo"] else [])])]
        else:           # 主包：圈里的先免控 3 tick，墙线上的拉进圈里，之后圈里不减速、墙那一圈减速 w_slow%
            ask, rise = [], [
                sfx("w_wall"),
                zone("w_safe", p["w_in"], "EnemyChampion", [buff("w_safe", 3, cc_immune=True)]),
                zone("w_cage", p["w_out"], "EnemyChampion", [{"type": "Pull", "speed": p["w_ps"], "tick": p["w_pt"]},
                                                             view("w_hit"), tsfx("w_hit"), *(combo if p["w_combo"] else [])],
                     delay=2, apply=2),
                field("w_free", p["w_in"], p["w_t"], 1, "EnemyChampion",
                      [buff("w_free", 2, move_speed_mult=p["w_slow"])]),
                field("w_band", p["w_out"], p["w_t"], 1, "EnemyChampion",
                      [buff("w_band", 2, move_speed_mult=-p["w_slow"])] +
                      ([{"type": "BlockMoveSkill", "tick": 2}] if p["w_block"] else []))]
        # 画面一段一段放（tools/art/yorick_wall_ring.py）：落地时 w_wall（地上裂一圈 0.75 秒 + 升起 0.25 秒），之后每 30 tick
        # 一段站着的 w_stand，最后 w_fall 塌掉。附加包副本：附加包把墙打塌时给他挂 w_down，下一段换成塌掉（只放一次：w_fell）
        wt = p["w_tn"] if native else p["w_t"]
        n_up = round((wt - 35) / 30)
        pics = [view("w_wall")]
        for k in range(n_up + 1):
            at = p["w_delay"] + 15 + 30 * k
            if not native:
                pics.append(delayed(at, view("w_fall" if k == n_up else "w_stand")))
            elif k < n_up:
                pics.append(delayed(at, sw("w_down", sw("w_fell", NONE, combine(flag("w_fell", wt), view("w_fall"))),
                                           view("w_stand"))))
            else:
                pics.append(delayed(at, sw("w_fell", combine(*rm("w_fell")), view("w_fall"))))
        drop = lob("w_drop", 1, 1000, "EnemyChampion", ask, end=[*pics, delayed(p["w_delay"], *rise)])
        return combine(refresh("w_cd", p["w_cd"]), refresh("busy", p["w_dur"]), anim("awaken", p["w_dur"]), sfx("q"),
                       delayed(p["w_rel"] - 1, alive(drop)))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Yorick
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        sw("q_go", sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_cast()))),
        sw("e_go", sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion", e_cast()))),
        sw("w_cd", NONE, sw("busy", NONE, pick(p["w_range"], "EnemyChampion", w_cast()))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Eulogy of the Isles
    # 室女跟着他：她在他身后升起（r_rise），r_up tick 后起一个挂在他身上的 AddCasted（他阵亡就停）：每 r_p tick 画一次她
    # （r_follow）、朝 r_reach 以内的敌方英雄放一道魂弹（没有英雄就打别的敌人），打中英雄给他挂标记 r_mk
    def bolt(target):
        hit = [attack(p["r_dmg"], p["r_ratio"]), view("r_claw"), tsfx("r_claw")]
        mark = [refresh("r_mk", p["r_mk_t"]), buff("r_mkv", p["r_mk_t"])]
        return combine(homing("r_bolt", target, hit, speed=p["r_bolt"]),
                       homing("r_btw", "EnemyChampion", mark, speed=p["r_bolt"]))
    shoot = combine(pick(p["r_reach"], "EnemyChampion", flag("r_shot", 1), bolt("EnemyChampion")),
                    sw("r_shot", combine(*rm("r_shot")),
                       pick(p["r_reach"], "EnemyWithoutTower", bolt("EnemyWithoutTower"))))
    follow = on_me(view("r_rise"), delayed(p["r_up"], casted(p["r_t"] - p["r_up"], p["r_p"], view("r_follow"), shoot)))
    rising = [homing("r_walk", "EnemyChampion", [walkers(p["r_n"])]), follow, sfx("r_spawn")]
    if native:      # 附加包副本：约里克身上有 m_unit（附加包生成了真的室女）时不放挂着的室女、魂弹和两只雾行者
        rising = [unless("m_unit", *rising)]
    maiden = [*rising, sw("own", combine(*rm("q_cd"), refresh("q_go", p["r_go_t"])))]
    r_cast = combine(refresh("r_on", p["r_t"]), *rm("r_mk"), refresh("busy", p["r_dur"]), anim("ult", p["r_dur"]),
                     sfx("r"), voice("vo_r", p), delayed(p["r_rel"] - 1, alive(*maiden)))
    if native:      # 出手时去掉上一次的 m_unit，给目标挂 m_ask（附加包生成真的室女和她的雾行者）
        r_cast = combine(r_cast, *rm("m_unit"), buff("m_ask", 3))

    # ------------------------------------------------------------------ attack
    # 室女的标记在他身上时，普攻打中英雄消耗它（附加包副本另外给英雄挂 3 tick 的 hit：附加包只在那名英雄身上真有标记时加伤）
    twin = sw("r_mk", homing("a_tw", "EnemyChampion", [spend()]))
    if native:
        twin = sw("r_on", homing("a_tw", "EnemyChampion", [buff("hit", 3), spend()]))
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]), twin)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"] * 4, p["r_ratio"] * 4), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"]), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"]), sw("e_cd", NONE, e_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # w_wall / w_stand / w_fall：整圈墙（tools/art/yorick_wall_ring.py：地上裂一圈 -> 升起 -> 站着 -> 塌掉），画在单位下面——
    # 墙段只有十来格高，人离墙线最近也隔着墙的半厚加身体，画在下面前后都对得上（见那个脚本的说明）。室女跟着他：
    # r_rise / r_follow 是 r_spawn / r_maiden 挪到他身后上方、画在他下面
    views_p = [Pj("e_mist"), Pj("r_bolt")]
    views_e = [E("a_hit"), E("q_hit"), E("q_grave", FX, -1, False), E("k_spawn", FX, -1), E("k_swarm", FX, -1),
               E("k_bite"), E("k_leap"), E("w_wall", BIG, -1, False, "w_ring_up"), E("w_stand", BIG, -1, False, "w_ring"),
               E("w_fall", BIG, -1, False, "w_ring_fall"), E("w_hit"), E("e_hit"),
               E("e_cloud", BIG, -1, False), E("r_rise", BIG, -1), E("r_follow", BIG, -1), E("r_claw"), E("r_mark")]
    views_b = [B_("e_mark", FX, -1, "e_mark"), B_("e_slow", FX, -1, "slow"), B_("r_mkv", FX, 3, "r_mkv")]
    extra = {}
    if native:   # addons/league_yorick: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_yorick:shepherd",
                            "params": {**{k: p[k] for k in ("r_pct", "g_t", "w_r", "w_half", "w_delay")}, "w_t": p["w_tn"]}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }


# 技能栏的坟数（tools/kit/stack_nums.py 的 STACKS：梯子 g1..g4，图标是技能1）
build = stack_nums.wrap(build)


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[])
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
