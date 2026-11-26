"""Build league_aurora.data_champion (mid, Magician: the Witch Between Worlds) from the parameters P.

    python tools/kit/build_aurora.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-23: MID, layout A - Twofold Hex / The Weirding / Between Worlds, Across the Veil folded
into the passive; combos E -> Q, R -> E, Q's two passes stacking the passive; 「有连招要做连招」). The ult follows League's
Between Worlds since 2026-11-04 (the user: 「阿罗拉的大招机制逻辑也是不太一样」): the teleport across the zone onto the ult's
champion is gone, League's border (in the add-on) took its place.
TFM2 has three active slots: Twofold Hex (Q) is `skill`, The Weirding (E) `skill2`, Between Worlds (R) the `ult`.
  passive Spirit Abjuration (驱灵奇术): every champion hit of hers (attack, Q out, Q back, E, R) counts on a caster ladder
          s_1 -> s_2 (p_t ticks, refreshed by every count; league_kennen's marks: the count is hers, not the target's),
          one count per source and cast (2-tick locks; Q's two passes are two sources, so one Q can count twice); the
          third exorcises the spirit: p_dmg + p_ratio% AP and p_hp% of the target's max health, and the spirit heals
          her p_heal + p_heal_r% AP a second for p_heal_t (an AddCasted; League V26.22: 3-20 + 2% AP a second for 4 s,
          and no haste since V14.23 - p_ms 0 leaves it out). The add-on's copy counts on each enemy instead
          (league_aurora:mark_<source>: League's 1% + 2.7% per 100 AP of his max health, the spirits by her level,
          addons/league_aurora/src/spirit.rs).
          Across the Veil (灵纱洞开), folded in: with an enemy champion within w_near (and, in the add-on's copy, low on
          health: below w_low% - the flag `low` its passive league_aurora:veil raises every tick; data reads no health,
          so the main pack's stand-in is the champion alone, w_gate 1), her next attack or E first hops her away from it
          (MoveBack w_back x w_back_t), turns her invisible w_inv ticks and hastens her w_ms% for w_ms_t (League's 4 s
          of Realm Hopper); then w_cd ticks before the next (the add-on's copy: a takedown of hers resets it).
  attack  A spirit bolt (homing on `Enemy`, 100% AD) released on a_rel; a champion-only twin counts the passive.
  skill   Twofold Hex (飞去来咒, cooldown q_cd, the flag `q_cd` the combos read): a `Direction` cast on
          `EnemyWithoutTower` (q_range). The hex flies q_len through everything (q_dmg + q_ratio% AP, the curse picture
          for q_hold + 30 ticks), stops, and q_hold ticks later the curses are drawn back: the return flies to her through
          everything again, q2_dmg + q2_ratio% AP (League's recast; the curse pulled through the ones on the way). The
          add-on's copy deals the return by league_aurora:hex_back: + up to q2_miss% by the target's missing health,
          q2_minion% to minions, q2_monster% to monsters, q2_again% for a second hex on one enemy within q2_again_t.
  skill2  The Weirding (怪奇喷涌, cooldown e_cd, the flag `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range): a
          blast in a cone toward the target (e_len, cone e_cone), e_dmg + e_ratio% AP and a slow of e_slow% that fades in
          e_slow_n steps over e_slow_t (League: 80% decaying over 1 s), then she hops back e_back x e_back_t (League's
          250 units). e_line 1 is League's straight band instead (e_len long, e_wid either side): tried 2026-11-26, the
          AI's E is mostly cast at minions and the band hit champions 4.3 times a game against the cone's 10.0 (kill
          diff -1.63 against +0.54 in the add-on's copy, -0.78 against +1.07 in the main pack), so the cone stays.
  ult     Between Worlds (双界合一, League V26.22): a `Targeting` cast on `EnemyChampion` (r_range) - the champion gives the
          direction. On the jump frame she leaps r_leap toward it (`RushTime`, r_leap_t ticks, through it when it is
          nearer; League's 25-250 units), immune to crowd control for the leap (League: to displacement), and gains
          Realm Hopper: r_ms% move speed for r_ms_t (League 3.25 / 3.75 / 4.25 s at the W rank's 15-40%; the add-on's
          copy sets r_ms_t1..3 by her level; no ghosting in TFM2). Landing, the
          shockwave goes off r_ahead in front of her (League's 425; a `RangeEffect` `Forward`, radius r_r1 + both
          bodies = the rift's ring): r_dmg + r_ratio% AP and r_slow1% for r_slow1_t (League 30% for 2 s). It leaves the
          rift there: a hidden line r_ahead long ends on the shockwave's centre and starts the rift's picture (r_zone,
          the ring League's 700) for r_t ticks (League 2.25-3.25 s). The main pack's AI casts it at a champion within
          r_ai_range when set (else r_range), on EnemyChampionRecentlyAttacked when r_recent - the copy keeps r_range
          and any champion, its AI hook picks the moment and the aim.
          Main pack (data cannot find the rift's border or move her across it): every r_per ticks the enemies in the
          rift are slowed r_slow% - only while she stands in it and lives (a search from the zone, league_ekko W's);
          the first check that misses her shuts it for good (`r_shut`, League: it closes when she leaves or dies).
          The add-on's copy (league_aurora:rift on the line's end, the passive league_aurora:veil): League's border -
          an enemy touching it is slowed r_edge% for r_edge_t once per crossing, she crosses to the opposite side over
          r_wrap_t ticks when she touches it (so she cannot walk out; her own hops, marked `own_hop` in the copy, cross
          it too, an enemy's knockback does not), it closes when she dies or gets out (a blink, carried out), and her
          AI kites inside it (addons/league_aurora/src/rift.rs, realm.rs). Since 0.4.0 (V26.22): the shockwave spreads
          r_grow ticks before the rift forms (its picture and sound then, played by the add-on), the rift lasts
          r_t1 / r_t2 / r_t3 by her level (r_lv2, r_lv3), the border's slow r_edge_t1..3, and r_recast ticks after the
          shockwave an empty rift is closed for her (League's recast).
  combos  E -> Q (the user: E 命中 -> Q): a champion the blast hits gets the hex eq_gap ticks later if Twofold Hex is ready
          (its cooldown flag taken): a homing hex (q_dmg) and, q_hold ticks later, its curse drawn back (q2_dmg).
          R -> E: re_gap ticks after the shockwave, if The Weirding is ready, its blast toward the ult's champion (the
          ones the shockwave caught) - without the hop back: from r_ahead behind the rift's centre the hop (e_back x
          e_back_t) would carry her out of her own rift (2026-11-04; it was the blast round her, landed on them). With
          re_hex (2026-11-26) that blast brings its E -> Q hex as The Weirding's own does: R -> E -> Q in the data.
          Q -> passive: the out pass and the return count separately, so one hex through a champion is two of the three.
The add-on copy (--native, addons/league_aurora): w_gate 0 and the passive league_aurora:veil (params NATIVE_PARAMS) -
the hop needs her real low health as well (the user's pick: 残血时跳开); the rift's border as above; the passive's marks
and Q's return by the add-on's natives.
Action tags (the art): idle run attack hit dead skill skill2 ult veil.
Numbers: League 16.20 (CommunityDragon aurora.bin) read into the Magician mid range (league_hwei, league_neeko); balanced on
the classic-SDK simulations (kd.py --lane 2, C:/t/au_sim, 2026-10-23, w_gate 1 as the veil's stand-in): the draft -2.31
on seeds 1-8 (league_hwei +1.16 on the same games); more damage, health and armour -0.05; the teleport across the realm
cost about 0.8 (she stepped onto champions deep in their team: off +0.72), so it reaches only r_tp_max 45000: +0.93.
2026-11-04 (League's Between Worlds, no simulation: the classic SDK runs no add-on): damage, cooldown, range and the
main pack's rift slow kept; the shockwave's slow 40% 1 s -> League's 30% 2 s, the rift 3.5 s -> League's top 3.25 s,
Realm Hopper (30% for 4.5 s) new - for the leap that no longer lands on the target and the teleport onto it gone.
2026-11-26（V26.22，附加包 0.4.0）：模拟器把附加包的钩子、领域和原生效果编进去（C:/t/au_sim），种子 1-24 各 720 局：
主包 +1.56 -> +0.80（灵物慢慢回血、不再加速，E 的减速逐渐减弱，后跳 15000，Realm Hopper 3.75 秒，AI 只在 r_ai_range
48000 内放 R），副本 0.3.1 的 -0.74 -> +0.55。+0.80 在当初定的 +0.93 / +1.01 附近，没再调数。
"""
import argparse
import json
import os
import stack_nums  # noqa: E402  (league.dll 的技能栏层数格：tools/kit/stack_nums.py)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_aurora.data_champion")
ID = "league_aurora"
FX = "asset/league/effects/league_aurora_fx"
BIG = "asset/league/effects/league_aurora_big"

# League's Aurora (16.20, CommunityDragon aurora.bin): 607 +110 hp, 53 AD, 23 armour, 30 mr, 335 move, 550 range.
# Passive: 4 s debuff, 1% max health, spirits heal, +5% (+2% per spirit) move speed. Q 900 range, 45-145 out and
# 45-145 back (+ up to 50% by missing health), 3.5 s mark, cd 9-7. W 300 hop, 1-1.6 s invisible, 20-40% speed, cd
# 22-18. E 825 x 175 blast, 80-240, 80% slow decaying over 1 s, 250 hop back, cd 15-11. R 250 jump, 175-375, 30% slow,
# a 700 realm for 3-4 s (she crosses its edges), cd 140-100.
# V26.21 Between Worlds: a 25-250 leap (0.4 s, immune to displacement), Realm Hopper (ghosted, 15-40% move speed, 4-5 s),
# the shockwave 425 in front of her expanding over 0.75 s (175/275/375 + 70% AP, 30% slow 2 s), a 700 rift for
# 2.25/2.75/3.25 s: Aurora touching its border dashes to the opposite side over 0.4 s, enemies touching it are slowed 50%
# for 1.5-2 s (once a crossing); it closes when she dies, leaves it or is not in it; a recast after 1 s closes it.
P = {
    # stats (Magician mid: league_hwei 940 +94 hp, 70 +6 attack, 40 +20 ap, 20 +7 def)
    "hp": 960, "hp_g": 90, "atk": 68, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 21, "def_g": 6, "mr": 26, "mr_g": 4,
    "ms": 920, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 90, "a_rel": 10, "a_speed": 4500, "a_y": -4000,
    # passive: Spirit Abjuration; Across the Veil folded in
    "p_t": 240, "p_dmg": 40, "p_ratio": 30, "p_hp": 2, "p_heal": 12, "p_heal_r": 2, "p_heal_t": 240, "p_ms": 0, "p_ms_t": 90,
    "p_hp_pm": 10, "p_hp_ap_pm": 27, "sp0": 3, "sp1": 20, "sp_ap": 2, "sp_t": 240, "sp_max": 4,
    "w_gate": 1, "w_low": 35, "native": 0, "w_cd": 1200, "w_near": 35000, "w_back": 4000, "w_back_t": 6, "w_inv": 75, "w_ms": 30, "w_ms_t": 240,
    # skill: Twofold Hex
    "q_cd": 450, "q_range": 85000, "q_dur": 30, "q_rel": 12, "q_speed": 4000, "q_len": 85000, "q_rad": 8000,
    "q_dmg": 100, "q_ratio": 55, "q_hold": 40, "q_back_speed": 4500, "q2_dmg": 100, "q2_ratio": 55, "q_ball_speed": 4500,
    "q2_miss": 50, "q2_minion": 40, "q2_monster": 50, "q2_again": 20, "q2_again_t": 60,
    # skill2: The Weirding
    "e_cd": 780, "e_range": 70000, "e_dur": 30, "e_rel": 12, "e_len": 75000, "e_cone": 900, "e_dmg": 150,
    "e_ratio": 80, "e_slow": 80, "e_slow_n": 4, "e_slow_t": 60, "e_back": 3000, "e_back_t": 5, "e_line": 0,
    "e_wid": 5250, "e_line_speed": 25000,
    "e_wave_speed": 6000, "eq_gap": 6,
    # ult: Between Worlds (the leap on the ult tag's jump frame, ticks 13-27 of 36; League's 425 / 700 x 60)
    "r_cd": 2100, "r_range": 60000, "r_dur": 36, "r_rel": 14, "r_leap": 15000, "r_leap_t": 14, "r_ahead": 25500,
    "r_r1": 28000, "r_dmg": 260, "r_ratio": 80, "r_slow1": 30, "r_slow1_t": 120, "r_ms": 30, "r_ms_t": 225,
    "r_zone": 38000, "r_t": 195, "r_per": 15, "r_slow": 30, "r_edge": 50, "r_wrap_t": 24,
    "r_grow": 45, "r_t1": 135, "r_t2": 165, "r_t3": 195, "r_lv2": 8, "r_lv3": 11, "r_edge_t1": 90, "r_edge_t2": 105,
    "r_edge_t3": 120, "r_ms_t1": 195, "r_ms_t2": 225, "r_ms_t3": 255, "r_recast": 60, "re_hex": 1,
    "r_ai_range": 48000, "r_recent": 0,
    "re_gap": 8,
    "vo_gap": 600,
}


# 附加包被动的 passive.params（addons/league_aurora/src/lib.rs 的 Params，默认值由 make_override.py 核对）
NATIVE_PARAMS = ("w_low", "r_grow", "r_t1", "r_t2", "r_t3", "r_lv2", "r_lv3", "r_edge", "r_edge_t1", "r_edge_t2",
                 "r_edge_t3", "r_wrap_t", "r_ms", "r_ms_t1", "r_ms_t2", "r_ms_t3", "r_leap_t", "r_recast", "p_t",
                 "p_hp_pm", "p_hp_ap_pm", "sp0", "sp1", "sp_ap", "sp_t", "sp_max", "q2_dmg", "q2_ratio", "q2_miss",
                 "q2_minion", "q2_monster", "q2_again", "q2_again_t")


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
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def maxhp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def cone(length, c, target, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": length, "range": c}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end, y=0, through=True):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": through, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def back(name, speed, radius, target, effects):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": 400000,
            "penetrate": True, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def lob(name, travel, end):
    """A 1-radius lob onto the target's spot (league_annie R's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def field(name, radius, tick, period, first, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Spirit Abjuration (champions only)
    def mark(src):
        """One count of the ladder on the champion these effects run on; the third exorcises its spirit. The add-on's
        copy counts on each enemy instead (league_aurora:mark_<src>, addons/league_aurora/src/spirit.rs)."""
        if p["native"]:
            return {"type": "Native", "effect_ref": f"{ID}:mark_{src}"}
        # 灵物在 p_heal_t 里慢慢回血（英雄联盟每秒 3-20 + 2% 法强，4 秒）；加速英雄联盟 V14.23 就删了
        hot = {"type": "AddCasted", "casted_type": "Heal", "duration": p["p_heal_t"], "period": 60,
               "effects": [heal(p["p_heal"], p["p_heal_r"])]}
        haste = [refresh("p_haste", p["p_ms_t"], move_speed_mult=p["p_ms"])] if p["p_ms"] else []
        spirit = combine(ap(p["p_dmg"], p["p_ratio"]), maxhp(p["p_hp"]), view("p_spirit"), tsfx("p_spirit"),
                         on_me(hot, cview("p_heal"), *haste),
                         *rm("s_1", "s_2"))
        count = sw("s_1", combine(refresh("s_1", p["p_t"]), refresh("s_2", p["p_t"])), refresh("s_1", p["p_t"]))
        return sw(f"lk_{src}", NONE, combine(flag(f"lk_{src}", 2), buff("p_mark", p["p_t"]),
                                             sw("s_2", spirit, count)))

    def own(t):
        """The add-on's copy marks her own hops (`own_hop`, the hop's ticks + 2): one that carries her into the rift's
        border takes her across it, an enemy's knockback or pull does not (src/rift.rs)."""
        return refresh("own_hop", t + 2) if p["native"] else None

    # Across the Veil: low (the add-on's flag, or w_gate 1's stand-in) and a champion within w_near
    def veil():
        hop = pick(p["w_near"], "EnemyChampion", flag("w_cd", p["w_cd"]), anim("veil", 12), sfx("w"), cview("w_veil"),
                   own(p["w_back_t"]), {"type": "MoveBack", "speed": p["w_back"], "tick": p["w_back_t"]},
                   on_me({"type": "CasterInvisible", "tick": p["w_inv"]},
                         refresh("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"])))
        return sw("w_cd", NONE, hop if p["w_gate"] and not p["native"] else sw("low", hop))

    # ------------------------------------------------------------------ attack: a spirit bolt
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), veil(), delayed(p["a_rel"] - 1, alive(
                          sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                           p["a_speed"], p["a_y"]),
                          homing("a_twin", "EnemyChampion", [mark("a")], p["a_speed"], p["a_y"])))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Twofold Hex
    hex_hit = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"), buff("q_curse", p["q_hold"] + 30)]
    # 回程伤害：副本用 league_aurora:hex_back（英雄联盟：按已损失生命最多加 q2_miss%，小兵 q2_minion%、
    # 野怪 q2_monster%，同一个人第二颗 q2_again%），主包就是固定的
    drawn_dmg = {"type": "Native", "effect_ref": f"{ID}:hex_back"} if p["native"] else ap(p["q2_dmg"], p["q2_ratio"])
    back_hit = [drawn_dmg, view("q_back_hit"), tsfx("q_back_hit")]
    hex_ = line("q_out", p["q_speed"], p["q_len"], p["q_rad"], "EnemyWithoutTower", hex_hit,
                [delayed(p["q_hold"], sfx("q_back"),
                         back("q_back", p["q_back_speed"], p["q_rad"], "EnemyWithoutTower", back_hit),
                         back("q_back_twin", p["q_back_speed"], p["q_rad"], "EnemyChampion", [mark("q2")]))],
                p["a_y"])
    hex_twin = line("q_out_twin", p["q_speed"], p["q_len"], p["q_rad"], "EnemyChampion", [mark("q")], [], p["a_y"])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap),
                           sw("q_cd", NONE, combine(refresh("q_cd", p["q_cd"]), voice("vo_q", p), sfx("q"),
                                                    delayed(p["q_rel"] - 1, alive(hex_, hex_twin))))))

    # ------------------------------------------------------------------ skill2: The Weirding
    def hex_on():
        """E -> Q: the hex on this champion if Twofold Hex is ready."""
        drawn = delayed(p["q_hold"], view("q_back_hit"), tsfx("q_back_hit"), drawn_dmg, mark("q2"))
        return delayed(p["eq_gap"], sw("q_cd", NONE, combine(
            refresh("q_cd", p["q_cd"]), sfx("q"),
            homing("q_ball", "EnemyChampion", [*hex_hit, mark("q"), drawn], p["q_ball_speed"], p["a_y"]))))

    # 英雄联盟是 80% 在 1 秒里减弱；TFM2 的减速会相加，所以拆成 e_slow_n 层、每层 e_slow / e_slow_n %，一层层先后结束
    # （最长的那层带霜雾画面）
    k = p["e_slow_n"]
    slows = [buff("e_slow" if i == k else f"e_slow{i}", p["e_slow_t"] * i // k, move_speed_mult=-(p["e_slow"] // k))
             for i in range(k, 0, -1)]
    blast_hit = [ap(p["e_dmg"], p["e_ratio"]), *slows, view("e_hit"), tsfx("e_hit")]
    hop_back = {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]}

    def blast(hex_too=True):
        """The Weirding's blast toward the action's target: the E's own (with E -> Q) and R -> E's (re_hex: with it).
        e_line 1: League's straight band (e_len long, e_wid either side: a hidden piercing bolt as fast as it is
        long), otherwise the cone (e_cone)."""
        champ = [mark("e"), hex_on()] if hex_too else [mark("e")]
        if p["e_line"]:
            hit = [line("e_band", p["e_line_speed"], p["e_len"], p["e_wid"], "EnemyWithoutTower", blast_hit, []),
                   line("e_band_twin", p["e_line_speed"], p["e_len"], p["e_wid"], "EnemyChampion", champ, [])]
        else:
            hit = [cone(p["e_len"], p["e_cone"], "EnemyWithoutTower", blast_hit),
                   cone(p["e_len"], p["e_cone"], "EnemyChampion", champ)]
        return [cview("e_burst"), sfx("e"),
                line("e_wave", p["e_wave_speed"], p["e_len"], 1000, "EnemyChampion", [], []), *hit]
    weirding = combine(*blast(), delayed(2, own(p["e_back_t"]), hop_back))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), veil(),
                            sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]), voice("vo_e", p),
                                                     delayed(p["e_rel"] - 1, alive(weirding))))))

    # ------------------------------------------------------------------ ult: Between Worlds
    def weird_on():
        """R -> E: The Weirding's blast toward the ult's champion if it is ready - no hop back (from r_ahead behind the
        rift's centre it would carry her out of her own rift); guarded, a dead caster's Delayed runs in the game."""
        return delayed(p["re_gap"], alive(sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]), *blast(bool(p["re_hex"]))))))

    def ahead(target, effects):
        """The shockwave: a circle r_ahead in front of her toward the ult's champion (r_r1 + both bodies across)."""
        return {"type": "RangeEffect", "shape": circle(p["r_r1"]), "target": target,
                "apply_type": {"Forward": {"offset": p["r_ahead"]}}, "effects": list(effects)}

    if p["native"]:
        # the add-on's passive keeps the rift (League's border): it gets the centre from league_aurora:rift
        rift_rule = [{"type": "Native", "effect_ref": f"{ID}:rift"}]
    else:
        # the data finds no border: the enemies in the rift slowed while she is in it (the search from the zone finds
        # no dead caster either); the first check that misses her shuts it until the next cast
        inside = combine(*rm("r_in"), pick(p["r_zone"] - 10000, "AllyOnlySelf", flag("r_in", 1), from_projectile=True))
        slow = buff("r_slow", p["r_per"] + 5, move_speed_mult=-p["r_slow"])
        held = sw("r_shut", NONE, combine(inside, sw("r_in", combine(*rm("r_in"), slow), flag("r_shut", p["r_t"]))))
        rift_rule = [field("r_field", p["r_zone"], p["r_t"], p["r_per"], p["r_per"], [held])]
    # a hidden line as fast as it is long from her pivot (y_offset 5000, league_draven's): it ends on the shockwave's
    # centre the tick it starts, and its end_effects run on that point - the pictures, the rift
    rift = {"type": "LinearProjectile", "name": n("r_rift"), "speed": p["r_ahead"], "range": p["r_ahead"],
            "y_offset": 5000, "penetrate": True, "shape": circle(1), "applied_target": "EnemyChampion",
            "applied_effects": [], "end_effects": [view("r_shock"), *([] if p["native"] else [view("r_zone"), sfx("r_zone")]),
                                                   *rift_rule]}
    shock_hit = [ap(p["r_dmg"], p["r_ratio"]), buff("r_slow1", p["r_slow1_t"], move_speed_mult=-p["r_slow1"]),
                 view("r_hit"), tsfx("r_hit")]
    landing = combine(sfx("r_land"), *([] if p["native"] else rm("r_shut")),
                      ahead("EnemyWithoutTower", shock_hit), ahead("EnemyChampion", [mark("r")]), rift, weird_on())
    leap = combine(refresh("r_hop", p["r_ms_t"], move_speed_mult=p["r_ms"]),
                   refresh("r_leap", p["r_leap_t"] + 2, cc_immune=True),
                   {"type": "RushTime", "speed": p["r_leap"] // p["r_leap_t"], "tick": p["r_leap_t"], "range": 20000,
                    "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": []})
    # 主包的 AI 只要射程里有英雄就放 R：r_ai_range（设了的话）把距离收到冲击波炸得到他的地方，r_recent 只对刚被
    # 队友打过的英雄放；附加包的副本保留整个射程、任何英雄，什么时候放、朝哪放由它的 AI 钩子（realm.rs）挑
    r_reach = p["r_ai_range"] if p["r_ai_range"] and not p["native"] else p["r_range"]
    r_on = "EnemyChampionRecentlyAttacked" if p["r_recent"] and not p["native"] else "EnemyChampion"
    ult = action("ult", p["r_dur"], p["r_cd"], 1, r_reach, "Targeting", r_on,
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive(leap)),
                         delayed(p["r_rel"] - 1 + p["r_leap_t"], alive(landing))))

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_bolt"), Pj("q_out"), Pj("q_back"), Pj("q_ball", "q_out"), Pj("e_wave")]
    views_e = [E("a_hit"), E("q_hit"), E("q_back_hit"), E("p_spirit"), E("p_heal"), E("w_veil", FX, 3, False),
               E("e_burst", FX, 3, False), E("e_hit"), E("r_shock", BIG, -1, False), E("r_zone", BIG, -1, False),
               E("r_hit")]
    # r_slow: the main pack's rift slow; r_hop: Realm Hopper under her feet (the veil's haste light)
    views_b = [B_("q_curse", FX, 3), B_("p_mark", FX, 3), B_("w_haste", FX, -1), B_("e_slow", FX, -1, "slow"),
               *([] if p["native"] else [B_("r_slow", FX, -1, "slow")]), B_("r_slow1", FX, -1, "slow"),
               B_("r_hop", FX, -1, "w_haste")]
    if p["native"]:
        # the add-on draws them itself: the doors at both ends of her crossing, the border's slow (src/rift.rs)
        views_e.append(E("r_blink"))
        views_b.append(B_("r_edge", FX, -1, "slow"))
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": f"{ID}:veil",
                            "params": {k: int(p[k]) for k in NATIVE_PARAMS}}
    return {
        "id": ID, "category": "Magician", **extra, "tags": ["AP", "Magic", "Range", "CC"],
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


# 技能栏层数格的图标（stack_skill_index）：重新生成也带着（tools/kit/stack_nums.py，2026-11-22）
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (native=1)")
    a = ap_.parse_args()
    p = dict(P)
    if a.native:
        p["native"] = 1
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
