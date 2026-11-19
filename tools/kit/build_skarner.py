"""Build league_skarner.data_champion (jungle, Melee tank-fighter, AD: Skarner, the Primordial Sovereign) from the parameters P.

    python tools/kit/build_skarner.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-26: JUNGLE, layout A - Q / E / R, Seismic Bastion (W) folded into the passive; combos all
four: R with the boulder up throws Upheaval first, E's carry ending -> Q ready, R's suppression -> Quaking at full
stacks, Q's third hit (or the throw) on a champion -> E back within e_cut ticks; League's differences in the add-on).
2026-11-20 照英雄联盟改（用户：「按照你的建议改吧」）：W 成了自己的技能、自己的冷却，从普攻里放，不再跟着 E 拖人结束；
举着巨石时，Q 的目标在普攻够不着的地方就马上扔。
TFM2 has three active slots for League's four buttons: Shattered Earth (Q) is `skill`, Ixtal's Impact (E) `skill2`,
Impale (R) the `ult`. Q and E keep their cooldowns in flags (`q_cd`, `e_cd`; league_trundle's) so the combos can ready
them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with him: a respawned Skarner has both.
  passive Threads of Vibration (战栗): his attacks, the boulder and Impale on a champion apply Quaking. Nothing reads a
          buff count on the target, so the stacks are his (league_varus Blight's ladder): caster flags qk1 -> qk2 (p_t
          ticks, refreshed by every hit, a 3-tick lock so one swing counts once); a champion hit on qk2 sets it quaking
          (an AddCasted Fire: p_pct% of its maximum health as true damage every p_p ticks for p_t ticks; nothing magic
          reads max health) and the ladder clears.
          震地壁垒（W）：2026-11-20 起是他自己的技能（英雄联盟里 W 有自己的键，想放就放）。三个技能栏都占了，所以从普攻
          里放：普攻打中东西（什么都行）时身上没有 `w_cd`、w_r 内有敌方英雄（`RandomTarget`，同阿兹尔的普攻召兵）就放：
          挂 w_cd 拍的 `w_cd`，当场得 w_sh + w_sh_r% 攻击力的护盾 w_sh_t 拍，摆起身砸地的 `w` 动作（盖掉普攻的收招），
          到 w_rel 那一帧周围（w_r）震地：w_dmg + w_ratio% 攻击力，减速 w_slow% w_slow_t 拍。放在普攻那一下隐形命中里，
          不放在普攻出手的那一刻：出手时对自己放范围效果，游戏的 AI 就不太让他打英雄（tools/kit/attack_self.py）。
  attack  A pincer blow (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; its champion-only twin climbs
          Quaking. Holding the boulder (`rock`, below) the blow also splashes. 这一下也放 W（见上）。
  skill   Q Shattered Earth / Upheaval (撼地 / 擎天), `Targeting` on `EnemyWithoutTower` within q_range (`q_cd`): he rips a
          boulder out of the ground (`rock` for q_t ticks: q_as% attack speed); his next three attacks on the unit and
          every enemy within q_r of it deal q_dmg + q_ratio% AD (a 1-tick lob on the unit hit), the third q_hp% of their
          maximum health more and q_slow% slower for q_slow_t ticks, and the boulder is spent (League: three charges;
          counted rk1 -> rk2). After q_hold ticks still holding it, the slot throws it instead (Upheaval, League's
          recast): a lob onto the unit, the same third-hit damage round where it lands. 2026-11-20 起举着巨石时 Q 的目标
          在普攻够不着的地方就马上扔（英雄联盟的再按一下，够不着时用）：先往目标打一发隐形的探针，命中时问他在不在
          它 atk_range 以内（`RandomTarget AllyOnlySelf from_projectile`，两边身体都算，跟普攻的够不够得着一个量法）。
  skill2  E Ixtal's Impact (以绪塔尔冲击), `Targeting` on `EnemyChampion` (e_range): he charges (MoveToTarget e_speed);
          on contact he carries the champion (Knockback e_kb_speed x e_kb_t, his dash after it). The data cannot see
          walls: the main pack slams it at the end of every carry - e_dmg + e_ratio% AD and a e_stun-tick stun; the
          add-on carries it on until a wall (League) and stuns only there.
  ult     R Impale (毒刺贯体), `Targeting` on `EnemyChampion` (r_range): the tails lash down a line toward it (r_len, r_w,
          the first r_n champions in the add-on; every champion on it in the main pack): r_dmg + r_ratio% AD, suppressed
          for r_sup ticks (`Stun`) and dragged after him (a `Grab` toward him every r_drag ticks while it lasts); he gains
          r_ms% move speed for r_ms_t ticks.
  combos  R -> Upheaval: R cast holding the boulder throws it at the target first (League). E -> Q: the carry's end
          takes `q_cd` off (the boulder at once, its three hits on the stunned champion); 拖完照旧摆 `w` 砸一下，但
          2026-11-20 起不再出 W 的护盾和震地. R -> Quaking: every champion
          impaled starts quaking at once. Q -> E: the boulder's last hit (or the throw) on a champion brings E back
          within e_cut ticks (E sets `e_far` for e_cd - e_cut ticks with `e_cd`; the hit swaps a running `e_far` for an
          e_cut-tick `e_cd`, so a cooldown already under e_cut is left alone).
The add-on copy (--native, addons/league_skarner: every place the data is not League's): E's contact is
league_skarner:impact (the carry runs on to a wall, the stun and its damage only there; he passes through terrain while
he charges); Quaking counts per champion (league_skarner:quake: stacks of a buff named for this Skarner on the target,
3 to burst, as league_brand's blaze); Impale takes the first r_n champions on the line and keeps them behind him while he
moves (league_skarner:impale).
Timings: tools/art/rig_skarner.py's MS (the throw on q_toss_rel, the slam's quake on w_rel, the lash on r_rel).
Numbers: League 16.21 read into the jungle fighter range (league_trundle, league_sejuani, league_warwick); balance on the
classic-SDK simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/sk_sim, 2026-10-26;
league_warwick --native the control: +0.57 on seeds 1-8): the draft (hp 1150, attack 80, Quaking 2% x 4, E stun 60, W
120 + 60% shield and 40 + 60% quake, Q +50% attack speed and 20 + 40% / 6% max hp, R 90-tick suppression and 120 + 100%)
+4.99 (1-8); no single cut moved it more than 0.7 (E off +2.40), every cut together +0.31; P = those cuts with hp 1100,
attack 76 and a 40-tick E stun +0.75 (1-16; Quaking 2% and a 45-tick stun on top +1.33). The add-on's rules cannot run in
that engine (Native effects dropped).
2026-11-20（W 单独放、擎天够不着就扔）：C:/t/skq_sim 的 kds.py（kd.py 加上数他的音效；经典引擎没有 Tank，类别按 Melee
跑），种子 1-24：改前 +0.27；W 范围 16000 是 -0.28（W 一局 5.9 次，原来跟着 E 9.9 次），20000 是 +0.33，25000 是 +0.20，
定 20000。种子 25-48：改前 +0.77，改后 +0.06。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_skarner.data_champion")
ID = "league_skarner"
FX = "asset/league/effects/league_skarner_fx"
BIG = "asset/league/effects/league_skarner_big"

# League's Skarner (16.21): 630 +110 hp, 63 AD, 33 armour +4.5, 32 mr +2.05, 335 move, 150 range, 0.625 attack speed.
# Passive: 3 stacks of Quaking (attacks, Q, R), at 3: 6-10% max hp magic over 4 s. Q: a boulder for 3 attacks / 5 s,
# +30-70% attack speed, 10-30 + 40% bonus AD round the target, the 3rd + 9-15% max hp... (scaled), slow 40% 1 s; recast
# throws it (the same damage), cd 8-3. W: shield 8% max hp 3 s, quake 40-160 + 80% AP + 8% max hp magic, 30% slow 1.5 s,
# cd 10-6. E: a 1700-range charge, carries a champion, a wall: 60-220 + 6% max hp physical and a 1.25 s stun, cd 22-18.
# R: the first 3 champions in front of him: 150-350 + 100% AP magic, suppressed 1.5 s and dragged, +40% ms, cd 120-90.
P = {
    # stats (base fighters: attack 90 +12, hp 1000 +100, defence 35 +8; league_trundle, league_sejuani)
    "hp": 1100, "hp_g": 110, "atk": 76, "atk_g": 12, "apw": 10, "apw_g": 5, "def": 32, "def_g": 9, "mr": 30, "mr_g": 4,
    "ms": 1000, "ms_g": 10, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 80, "a_hit": 12,
    # passive: Quaking
    "p_t": 240, "p_p": 60, "p_pct": 1,
    # W 震地壁垒：2026-11-20 起自己一个技能，从普攻里放，冷却 w_cd（英雄联盟 10-6 秒）。震地范围 w_r 16000 -> 20000：
    # 英雄联盟 W 的范围 600-700，按这套数值里 Q 的换算（溅射 300 = q_r 9000，擎天 1050 = q_range 30000）是 20000 上下；
    # 16000 时 W 单独放只有 5.9 次一局、-0.28（改前 +0.27），20000 是 +0.33
    "w_dur": 16, "w_rel": 7, "w_cd": 600, "w_sh": 40, "w_sh_r": 20, "w_sh_t": 180, "w_r": 20000, "w_dmg": 20,
    "w_ratio": 30, "w_slow": 30, "w_slow_t": 90,
    # skill: Q Shattered Earth / Upheaval
    "q_cd": 420, "q_range": 30000, "q_dur": 30, "q_t": 360, "q_hold": 180, "q_as": 20, "q_r": 9000, "q_dmg": 10,
    "q_ratio": 20, "q_hp": 3, "q_slow": 40, "q_slow_t": 60, "q_toss": 24, "q_toss_rel": 9, "q_travel": 16, "q_toss_dmg": 50,
    "q_toss_ratio": 80,
    # skill2: E Ixtal's Impact
    "e_cd": 900, "e_cut": 240, "e_range": 60000, "e_speed": 3000, "e_kb_speed": 2500, "e_kb_t": 20, "e_dmg": 60,
    "e_ratio": 80, "e_stun": 40, "e_anim": 24,
    # ult: R Impale
    "r_cd": 4800, "r_range": 50000, "r_dur": 36, "r_rel": 14, "r_len": 52000, "r_w": 7000, "r_speed": 6000, "r_n": 3,
    "r_dmg": 60, "r_ratio": 50, "r_sup": 45, "r_drag": 3, "r_grab": 3000, "r_ms": 30, "r_ms_t": 150,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_skarner (League's rules the data cannot read, see the docstring); its parameters
    "native": 0, "p_n": 3, "e_wall_dmg": 60, "e_wall_hp": 6,
}


# the numbers addons/league_skarner reads from passive.params (its Params, in this order)
NATIVE_KEYS = ("p_n", "p_t", "p_p", "p_pct", "e_kb_speed", "e_kb_t", "e_stun", "e_wall_dmg", "e_ratio", "e_wall_hp",
               "r_n", "r_sup", "r_dmg", "r_ratio")


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


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
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
            "applied_effects": [T(e) for e in effects if e is not None]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=(), y=5000):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = p["native"]

    # ------------------------------------------------------------------ passive: Quaking (counted on him)
    def quake(full=False):
        """Run on a champion hit (a champion-only effect): one stack, or the quake on qk2 (at once when `full`)."""
        burst = combine(*rm("qk1", "qk2"), casted(p["p_t"], p["p_p"], pct(p["p_pct"]), kind="Fire"),
                        buff("p_quake", p["p_t"]), view("p_burst"), tsfx("p_burst"))
        if nat:   # the add-on counts per champion (stacks of a buff named for him on the target); Impale's own native
            return native("quake")  # quakes its champions at once
        if full:
            return burst
        climb = sw("qk2", burst, sw("qk1", combine(refresh("qk2", p["p_t"]), refresh("qk1", p["p_t"])),
                                    refresh("qk1", p["p_t"])))
        return sw("qk_lock", NONE, combine(refresh("qk_lock", 3), climb))

    # ------------------------------------------------------------------ Q -> E: E back within e_cut ticks
    q_to_e = sw("e_far", combine(*rm("e_far"), refresh("e_cd", p["e_cut"])))

    # ------------------------------------------------------------------ Q Shattered Earth / Upheaval
    third = [attack(p["q_dmg"], p["q_ratio"], p["q_hp"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
             view("q_hit"), tsfx("q_hit")]

    def rock_hit():
        """The boulder's splash round the unit his attack hits: rk1 -> rk2 -> the third (spent), on a 1-tick lob."""
        splash = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit")]
        last = combine(*rm("rock", "rock_v", "rk1", "rk2", "q_toss"),
                       lob("q_smash", 1, p["q_r"], "EnemyWithoutTower", third,
                           end=[zone("q_sc", p["q_r"], "EnemyChampion", [quake(), q_to_e])]))
        mid = combine(refresh("rk2", p["q_t"]), lob("q_split", 1, p["q_r"], "EnemyWithoutTower", splash))
        first = combine(refresh("rk1", p["q_t"]), lob("q_split", 1, p["q_r"], "EnemyWithoutTower", splash))
        return sw("rk2", last, sw("rk1", mid, first))

    def toss(delay=0):
        """Upheaval: the boulder thrown on the unit in hand (`delay` ticks on: the throw frame of skill_toss), the third
        hit's damage round where it lands; the boulder is spent at once."""
        hit = [attack(p["q_toss_dmg"], p["q_toss_ratio"], p["q_hp"]),
               buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), view("q_hit"), tsfx("q_hit")]
        throw = combine(sfx("q_toss"), lob("q_throw", p["q_travel"], p["q_r"], "EnemyWithoutTower", hit,
                                           end=[view("q_land"), sfx("q_land"),
                                                zone("q_tc", p["q_r"], "EnemyChampion", [quake(), q_to_e])]))
        return combine(*rm("rock", "rock_v", "rk1", "rk2", "q_toss"), delayed(delay - 1, alive(throw)) if delay else throw)

    def q_pickup():
        # the boulder's picture over his back (`rock_v`, the effect q_held) from the pickup's end: its two frames draw it
        # in his tails themselves; only while he still holds it
        shown = delayed(p["q_dur"] - 1, sw("rock", refresh("rock_v", p["q_t"] - p["q_dur"])))
        return combine(refresh("q_cd", p["q_cd"]), refresh("rock", p["q_t"], attack_speed_mult=p["q_as"]),
                       refresh("q_toss", p["q_hold"]), *rm("rk1", "rk2"), anim("skill", p["q_dur"]), sfx("q"),
                       voice("vo_q", p), shown)

    # the slot: holding the boulder past q_hold -> throw it; else the pickup when Q is ready
    # 2026-11-20：还没举满 q_hold 时，目标在普攻够不着的地方也马上扔（英雄联盟的再按一下）。往目标打一发隐形探针，
    # 命中时问他在不在它 atk_range 以内，跟普攻一个量法（两边身体都算），3 拍后看结果。举满了的照旧扔，也等这 3 拍：
    # 扔的那一段只写一份（技能树每拍都要复制一遍）。旗子挂 6 拍，看完就摘
    probe = homing("q_probe", "EnemyWithoutTower",
                   [combine(flag("q_seen", 6), pick(p["atk_range"], "AllyOnlySelf", flag("q_near", 6),
                                                    from_projectile=True))], speed=60000)
    decide = combine(sw("q_seen", combine(*rm("q_seen"), sw("q_near", NONE, flag("q_go", 6)))), *rm("q_near"),
                     sw("q_go", combine(*rm("q_go"), anim("skill_toss", p["q_toss"]), toss(p["q_toss_rel"]))))
    holding = combine(*rm("q_seen", "q_near", "q_go"), sw("q_toss", probe, flag("q_go", 6)),
                      delayed(3, alive(sw("rock", decide, combine(*rm("q_seen", "q_near", "q_go"))))))
    q_slot = sw("rock", holding, sw("q_cd", NONE, q_pickup()))

    # ------------------------------------------------------------------ W Seismic Bastion（自己的技能）
    # 2026-11-20：W 不再跟着 E 拖人结束出，是自己的技能、自己的冷却 w_cd。技能栏没有空的，从普攻那一下命中里放：
    # 身上没有 w_cd、w_r 内有敌方英雄就放。护盾当场给，摆起身砸地的 w 动作，到 w_rel 那一帧才震地
    shield = on_me({"type": "Shield", "amount": p["w_sh"], "attack_ratio": p["w_sh_r"], "ap_ratio": 0,
                    "tick": p["w_sh_t"]}, flag("w_on", p["w_sh_t"]))
    quake_ring = around(p["w_r"], "EnemyWithoutTower", attack(p["w_dmg"], p["w_ratio"]),
                        buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit"))
    # 震地那一下挂在他自己身上等（on_me 里的 Delayed）：挂在普攻打中的那个单位上的话，它被这一下打死，后面的就可能
    # 不来了（卡莎 E 的教训，champion-data.md）
    w_cast = combine(refresh("w_cd", p["w_cd"]), anim("w", p["w_dur"]), shield,
                     on_me(delayed(p["w_rel"] - 1, alive(view("w_quake"), sfx("w"), quake_ring))))
    w_try = sw("w_cd", NONE, combine(*rm("w_go"), pick(p["w_r"], "EnemyChampion", flag("w_go", 1)),
                                     sw("w_go", combine(*rm("w_go"), w_cast))))

    # ------------------------------------------------------------------ E Ixtal's Impact
    # the carry's end (the main pack's slam, the add-on's wall check): E -> Q (q_cd off), the bounce and slam (tag `w`)
    # 2026-11-20 起这里不再出 W 的护盾和震地（W 自己放了），E -> Q 照旧
    carry_end = combine(anim("w", p["w_dur"]), *rm("q_cd"))
    if nat:
        slam = [native("impact")]
    else:
        slam = [delayed(p["e_kb_t"], attack(p["e_dmg"], p["e_ratio"]), {"type": "Stun", "duration": p["e_stun"]},
                        buff("e_stun", p["e_stun"]), view("e_slam"), tsfx("e_slam"))]
    push = [] if nat else [{"type": "Knockback", "speed": p["e_kb_speed"], "tick": p["e_kb_t"]}]
    contact = [anim("grab", p["e_kb_t"]), view("e_hit"), tsfx("e_hit"), *push, *slam,
               on_me(delayed(p["e_kb_t"], alive(carry_end)))]
    follow = {"type": "MoveToTarget", "speed": p["e_kb_speed"], "range": p["e_kb_speed"] * p["e_kb_t"] + 20000,
              "end_effects": []}
    charge = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
              "end_effects": [*contact, delayed(2, follow)]}
    # he passes through terrain while he charges (League; both packs)
    e_cast = combine(refresh("e_cd", p["e_cd"]), refresh("e_far", p["e_cd"] - p["e_cut"]),
                     refresh("e_ghost", p["e_anim"] + p["e_kb_t"], ignore_wall=True),
                     anim("skill2", p["e_anim"] + p["e_kb_t"]), sfx("e"), voice("vo_e", p), charge)

    # ------------------------------------------------------------------ R Impale
    haste = on_me(refresh("r_haste", p["r_ms_t"], move_speed_mult=p["r_ms"]))
    if nat:   # the add-on: the first r_n champions, magic damage, suppressed and kept beside him, quaking at once
        struck = [native("impale"), view("r_hit"), tsfx("r_hit"), haste]
    else:
        drag = casted(p["r_sup"], p["r_drag"], {"type": "Grab", "speed": p["r_grab"], "tick": 2})
        struck = [attack(p["r_dmg"], p["r_ratio"]), {"type": "Stun", "duration": p["r_sup"]}, drag,
                  buff("r_held", p["r_sup"]), view("r_hit"), tsfx("r_hit"), quake(True), haste]
    lash = line("r_lash", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion", True, struck)
    # R -> Upheaval: holding the boulder, it flies at the target first (League)
    r_cast = combine(sw("rock", toss()), anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                     delayed(p["r_rel"] - 1, alive(lash)))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit"),
                                                        sw("rock", rock_hit()), w_try]),
                   homing("a_tw", "EnemyChampion", [quake()]))
    # holding the boulder the tails keep it up and the claw strikes (League's BaseAttack1_Rock): attack_rock swapped in
    # at the first tick (the attack tag opens on the idle, so no tail stab shows before it)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("rock", anim("attack_rock", p["atk_dur"] - 1)),
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"]), r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_toss_dmg"], p["q_toss_ratio"]), q_slot), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"]), sw("e_cd", NONE, e_cast)), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_e = [E("a_hit"), E("p_burst"), E("q_hit"), E("q_land", FX, 1, False), E("w_quake", BIG, -1, False),
               E("w_hit"), E("e_hit"), E("e_slam"), E("r_hit")]
    views_b = [B_("p_quake", FX, 3, "p_quake"), B_("q_slow", FX, -1, "slow"), B_("w_slow", FX, -1, "slow"),
               B_("w_on", FX, 3, "w_shield"), B_("e_stun", FX, 3, "stun"), B_("r_held", FX, 3, "r_held"),
               B_("r_haste", FX, -1, "r_haste"), B_("rock_v", BIG, 3, "q_held")]
    views_p = [B_("q_throw", FX, 2, "q_rock"), B_("r_lash", BIG, 2, "r_spike")]
    extra = {}
    if nat:   # addons/league_skarner: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_skarner:sovereign", "params": {k: p[k] for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Tank", "tags": ["AD", "Melee", "Tank", "CC"], **extra,
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
