"""Build league_zed.data_champion (mid, Assassin) from the parameters P.

    python tools/kit/build_zed.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-09: mid, Assassin, League's whole kit with the pros' combos). TFM2 has three active slots:
Living Shadow is `skill` (the combo opener), Razor Shuriken `skill2`, Death Mark the `ult`; Shadow Slash runs on its own
inside the attack (league_rengar's Savagery way).
  passive Contempt for the Weak (影忍法·灭魂劫): League hits a champion below 50% health for a share of his max health.
          Nothing reads health, so it counts his own work (league_akali R2's way): a spell of his that hits a champion
          (shuriken, slash, the mark) readies `cw_ready` (cw_t ticks); his next attack on a champion adds cw_pct% of
          its max health (true damage, `FixedAttack target_hp_ratio`) and starts cw_cd. The add-on
          addons/league_zed_mark (native=1) reads health instead: below cw_hp% his attack adds 6/8/10% of the max.
  The shadow (影分身). Projectiles leave from the caster and nothing started from a zone at a point spawns (measured
          2026-10-09, work/zd/test_echo.py), so a shadow is league_ekko's anchor - a hidden lob that lands on the
          target's spot - whose `end_effects` hold everything it does, each a `Delayed` there (it keeps the point):
          its picture in one-checkpoint pieces (its own throw / spin where it copies his), the copies of his slash and
          shuriken (its shuriken flies from it back toward him - a `BackToCasterLinearProjectile` through what stands
          between - and its slash rings it): the W combo's exactly a tick after him (the slash with `ec_echo`, the
          shuriken on the first checkpoint), every later one at the next checkpoint (every echo_step ticks for the W
          shadow, r_echo_step for the R shadow; his slash and shuriken set `e_echo` / `q_echo` and `er_echo` / `qr_echo`
          for exactly one step, so one checkpoint copies each) - the user: 「你可以增加节点 实现成原样的」 (W's tree 781
          nodes: the engine copies it every tick; the R shadow's checkpoints sit in the ult, which it does not copy) -
          and the swap onto it to chase (one champion near it, none near him, soon after the combo).
  attack  The wrist-blade swing, the hit on tick a_st. Shadow Slash (影奔, automatic): with e_cd off and an enemy
          within e_r, the attack is the E spin instead - e_dmg + e_ratio% AD round him (a live shadow copies it), the
          champions slowed e_slow% for e_slow_t ticks.
  skill   W Living Shadow (影分身): on an enemy champion within w_range: the shadow lands on his spot and stays w_life
          ticks. The cast goes straight on (the pros' W-E-Q, 三影齐发): Shadow Slash if it is ready, then Razor
          Shuriken if it is ready - both copied by the shadow, as every later one while it stands. Within chase_t of the landing, one enemy champion near it and
          none near him: he swaps onto it (W2 chase).
  skill2  Q Razor Shuriken (影奥义！诸刃): a shuriken thrown on tick q_at toward where the target stood 8 ticks before
          (dodgeable, league_caitlyn's lock), through everything on the line: q_dmg + q_ratio% AD to the first unit,
          q_pen% of that to the rest. A live shadow throws one too.
  ult     R Death Mark (禁奥义！瞬狱影杀阵): on `EnemyChampionRecentlyAttacked` within r_range: untargetable, he dashes
          through the champion (`RushMoveToBack`), marks him and leaves a shadow where he stood (it copies his
          shurikens and slashes too). r_pop ticks later the
          mark bursts: r_dmg + r_ratio% AD plus r_per for each of his hits on the marked champion meanwhile (League adds
          a share of the damage dealt; nothing reads damage, so it counts the hits, up to three; the add-on
          adds r_pct% of the damage he dealt). He swaps back to the shadow (R2) when the burst kills, when he is
          outnumbered as it bursts (two enemy champions within r_safe_r), whenever he is in crowd control while the
          shadow stands, and (the add-on) under r_low% health. The pros' R-W-E-Q: under the
          mark with W ready, Razor Shuriken's slot is an empty branch, so the AI opens Living Shadow's combo.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_zed.data_champion")
ID = "league_zed"
FX = "asset/league/effects/league_zed_fx"
BIG = "asset/league/effects/league_zed_big"

# Timings (provisional until the strips exist): the swing's hit on tick 9, Shadow Slash's ring on 8 (skill_e), the
# shuriken leaves on 10 (skill2), the shadow thrown on 4 (skill), the R dash from 6 (ult).
P = {
    # stats (Assassin base: attack 120 +30, hp 900 +80, defence 25, mr 15, move 1100, range 23000); League's Zed:
    # 654 +99 hp, 63 AD +3.4, 32 armour, 345 move, 125 range
    "hp": 920, "hp_g": 86, "atk": 125, "atk_g": 26, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    # attack: the wrist blades
    "atk_range": 23000, "atk_dur": 25, "atk_cd": 55, "a_st": 9,
    # passive: Contempt for the Weak (League: 6-10% max health magic, 10 s per target)
    "cw_t": 240, "cw_pct": 6, "cw_cd": 600,
    # E Shadow Slash (League: 290 radius, 70-190 + 65% bonus AD, 20-40% slow 1.5 s, cd 5-4 s)
    "e_cd": 240, "e_dur": 24, "e_at": 8, "e_r": 24000, "e_dmg": 50, "e_ratio": 75, "e_slow": 25, "e_slow_t": 90,
    # Q Razor Shuriken (League: 900 range, 1700 speed, 80-280 + 110% bonus AD, 60% to the next, cd 6 s)
    "q_cd": 240, "q_dur": 26, "q_at": 10, "q_lock": 6, "q_range": 55000, "q_len": 70000, "q_speed": 10000, "q_rad": 5500,
    "q_y": 3000, "q_dmg": 60, "q_ratio": 100, "q_pen": 60,
    # W Living Shadow (League: 650 range, 5.25 s, cd 20-16 s)
    "w_cd": 720, "w_dur": 6, "w_at": 3, "w_fly": 4, "c_e": 8, "w_range": 55000, "w_life": 300, "swap_step": 45, "chase_t": 90,
    # every later Q / E he casts while a shadow stands is copied at its next checkpoint: the W shadow's every echo_step
    # ticks (in W's tree, which the engine copies each tick), the R shadow's every r_echo_step (in the ult's, which it
    # does not)
    "echo_step": 12, "r_echo_step": 6,
    "sh_near_r": 25000, "near_r": 30000,
    # R Death Mark (League: 625 range, 3 s mark, 25-55% of the damage dealt, cd 120-80 s; shadow 6 s)
    "r_cd": 3000, "r_dur": 24, "r_go": 6, "r_speed": 6000, "r_range": 60000, "r_pop": 180, "r_dmg": 80, "r_ratio": 100,
    "r_per": 35, "r_inv": 24, "r_life": 360, "r_safe_r": 40000,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_zed_mark: its native passive reads health (Contempt below cw_hp%, cw_lo/mid/hi% of
    # max health by his level, cw_cd per target) and the damage dealt under the mark (r_pct% of it at the burst); the
    # data stand-ins (cw_ready after a spell hit, the r_1..r_3 hit ladder) go; it also sends him back to the R shadow
    # under r_low% health (the r_back flag)
    "native": 0, "cw_hp": 50, "cw_lo": 6, "cw_mid": 8, "cw_hi": 10, "r_pct": 35, "r_low": 30,
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
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


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


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, radius, target, effects):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": 400000,
            "penetrate": True, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def lob(name, travel, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 1000000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, r, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(r), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def pzone(name, r, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(r), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ the passive and the mark's count
    # a spell hit on a champion: Contempt readies; under the mark (r_on) each hit climbs r_1..r_5
    climb = sw("r_on", sw("r_3", NONE, sw("r_2", combine(*rm("r_2"), flag("r_3", p["r_pop"] + 10)),
                                         sw("r_1", combine(*rm("r_1"), flag("r_2", p["r_pop"] + 10)),
                                            flag("r_1", p["r_pop"] + 10)))))
    spell_mark = NONE if p["native"] else on_me(sw("cw_cd", NONE, refresh("cw_ready", p["cw_t"])), climb)

    # ------------------------------------------------------------------ Shadow Slash
    def slash_hits():
        return [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]

    def slash(echo="e_echo"):
        """His ring (the cast's tick is e_at - 1 before); `echo` tells the W shadow (W's combo copies it exactly with
        its own flag, its checkpoints the later ones), er_echo the R shadow."""
        return combine(cview("e_spin"), sfx("e"),
                       around(p["e_r"], "EnemyWithoutTower", slash_hits()),
                       around(p["e_r"], "EnemyChampion", [buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                                                          *([] if p["native"] else [spell_mark])]),
                       refresh(echo, p["echo_step"] + 1), refresh("er_echo", p["r_echo_step"] + 1),
                       flag("e_cd", p["e_cd"]))

    # ------------------------------------------------------------------ Razor Shuriken
    def q_hit():
        """First unit full, the rest q_pen% (league_caitlyn's first-hit flag)."""
        pen = p["q_pen"]
        return [sw("q_first", combine(attack(p["q_dmg"] * pen // 100, p["q_ratio"] * pen // 100), view("q_hit")),
                   combine(attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), flag("q_first", p["q_dur"] + 10))),
                tsfx("q_hit")]

    def shuriken(lead, echo="q_echo"):
        """Lock the aim q_lock ticks before the throw on tick lead + q_at; `echo` as slash()'s."""
        star = line("q_star", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True, q_hit())
        twin = [] if p["native"] else             [line("q_twin", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyChampion", False, [spell_mark])]
        aimed = {"type": "RandomTarget", "range": p["q_range"] + 10000, "casting_target": "EnemyChampion",
                 "from_projectile": False,
                 "effects": [flag("q_aim", p["q_lock"] + 2), lob("q_aim", p["q_lock"], "EnemyChampion", [star, *twin])]}
        return combine(delayed(lead + p["q_at"] - p["q_lock"] - 1, *rm("q_first"), aimed),
                       delayed(lead + p["q_at"] - 1, sfx("q"), sw("q_aim", NONE, star),
                               refresh(echo, p["echo_step"] + 1), refresh("qr_echo", p["r_echo_step"] + 1)),
                       flag("q_cd", p["q_cd"]))

    # ------------------------------------------------------------------ the shadows (league_ekko's anchor)
    def copies():
        """What a shadow copies: his shuriken - flown from the shadow back toward him, through what stands between -
        and his slash round it."""
        pen = p["q_pen"]           # the shadow's shuriken: q_pen% to all (the first-hit flag per copy cost 6 nodes)
        star = back("sh_star", p["q_speed"], p["q_rad"], "EnemyWithoutTower",
                    [attack(p["q_dmg"] * pen // 100, p["q_ratio"] * pen // 100), view("q_hit"), tsfx("q_hit")])
        return star, combine(view("sh_spin"), zone("sh_slash", p["e_r"], "EnemyWithoutTower", slash_hits()))

    def checkpoint(qf, ef, stand, busy=()):
        """A checkpoint: the copies of his shuriken / slash whose flag runs (each flag is there for exactly one checkpoint
        step - a buff of n ticks is seen on n - 1 of them, so the flags are a step + 1 long - and exactly one checkpoint
        sees it: no copy twice, nothing to spend; 12 ticks missed 1 cast in 12) and the shadow's picture for the
        step - its own throw (sh_q) or spin (sh_e) when it copies one, else `stand`, its standing frame. The pictures
        are one step long (tools/art/import_zed.py), so they never overlap; `busy` marks a cast longer than the step."""
        star, slash_ = copies()
        return [sw(qf, star), sw(ef, slash_),
                sw(qf, combine(view("sh_q"), *busy), sw(ef, combine(view("sh_e"), *busy), stand))]

    def shadow(life, live, d_e, d_q):
        """The W shadow's end_effects (ticks from the landing): it forms (2 ticks), copies the combo's slash (d_e) -
        its spin, 8 ticks, else the rest of its forming - and from the combo's shuriken (d_q) a checkpoint every
        echo_step ticks copying every later Q / E of his, each with its picture; the chase swap (within chase_t), the
        end."""
        assert (d_e, d_q - d_e, p["echo_step"]) == (2, 8, 12), "the pieces' lengths in tools/art/import_zed.py"
        swap = sw("sn2", NONE, sw("sn1", sw("zn", NONE, combine(*rm(live), cview("w_swap"), {"type": "Teleport"},
                                                               sfx("w2")))))
        count = sw("sn_t", refresh("sn2", 7), combine(flag("sn_t", 1), refresh("sn1", 7)))
        out = [view("sh_in_a"), sfx("w_land"),
               pzone("sh_near", p["sh_near_r"], life, 6, "EnemyChampion", [on_me(count)]),
               delayed(d_e, sw(live, sw("ec_echo", combine(view("sh_e8"), copies()[1]), view("sh_in_b"))))]
        # a picture at every checkpoint, the copies' or a standing frame: the standing shadow once played 45-tick
        # pieces only where its steps met the checkpoints' (tick 180) - it vanished after forming and blinked back
        # (「会突然出现然后消失了再出现」) - and its copies showed no cast of its own (「看不到攻击和技能的效果」)
        step = p["echo_step"]
        ticks = range(d_q, life - step + 1, step)
        for j, t in enumerate(ticks):
            out.append(delayed(t, sw(live, combine(*checkpoint("q_echo", "e_echo",
                                                                view(f"sh_st{j % 4}"))))))
        out += [delayed(t, sw(live, swap)) for t in range(p["swap_step"], p["chase_t"] + 1, p["swap_step"])]
        out.append(delayed(ticks[-1] + step, sw(live, combine(*rm(live), view("sh_out")))))
        return out

    def combo(lead):
        """The pros' W-E-Q from tick lead, quick as League's (the first version took 46 ticks from the throw to the
        shuriken and 5 of 73 shurikens met a champion): the throw (W's strip), the shadow landing on the target's spot
        on tick lead + w_at - 1 + w_fly, the slash on c_e (its ring only; his body goes on into the shuriken's
        strip, which starts at w_dur), the shuriken on w_dur + q_at; the shadow copies each a tick after him."""
        land = lead + p["w_at"] - 1 + p["w_fly"]
        q_go = lead + p["w_dur"]
        d_e = lead + p["c_e"] - land
        d_q = q_go + p["q_at"] - land
        throw = delayed(lead + p["w_at"] - 1, sfx("w"), cview("w_dash"),
                        on_me(refresh("w_live", p["w_life"] + p["w_fly"])),
                        lob("w_lob", p["w_fly"], "EnemyChampion", shadow(p["w_life"], "w_live", d_e, d_q)))
        return combine(anim("skill", p["w_dur"]), throw, flag("w_cd", p["w_cd"]),
                       sw("e_cd", NONE, delayed(lead + p["c_e"] - 1, slash("ec_echo"))),
                       sw("q_cd", NONE, combine(delayed(q_go - 1, anim("skill2", p["q_dur"])), shuriken(q_go))))

    # ------------------------------------------------------------------ the attack (Shadow Slash folded in)
    # the add-on reads the probe on the champion it hit (health below cw_hp%: its native Contempt)
    probe = homing("cw_probe", 100000, 0, "EnemyChampion", [buff("cw_probe", 2)])
    contempt = probe if p["native"] else sw("cw_ready", sw("cw_cd", NONE,
                                 homing("cw_hit", 100000, 0, "EnemyChampion",
                                        [{"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0,
                                          "target_hp_ratio": p["cw_pct"], "attack_effect_type": "Target"},
                                         view("cw_hit"), tsfx("cw_hit"),
                                         on_me(*rm("cw_ready"), flag("cw_cd", p["cw_cd"]))])))
    swing = combine(sfx("a_swing"),
                    delayed(p["a_st"] - 1, homing("a_hit", 100000, 0, "EnemyWithoutTower",
                                                 [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                            *([] if p["native"] else [homing("a_twin", 100000, 0, "EnemyChampion", [on_me(climb)])]),
                            contempt))
    spin = combine(anim("skill_e", p["e_dur"]), voice("vo_e", p), delayed(p["e_at"] - 1, slash()))
    near = {"type": "RandomTarget", "range": p["near_r"], "casting_target": "EnemyChampion", "from_projectile": False,
            "effects": [refresh("zn", 40)]}
    e_ready = {"type": "RandomTarget", "range": p["e_r"], "casting_target": "EnemyWithoutTower", "from_projectile": False,
               "effects": [flag("e_go", 1)]}
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(near, sw("e_cd", swing, combine(e_ready, sw("e_go", spin, swing)))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: W Living Shadow (+ W-E-Q)
    # chase: zn (an enemy champion near him, renewed by his actions) holds the shadow's swap
    # the slots are 3-tick actions whose CasterAnimations hold him (league_aatrox Q), their cooltimes the real ones: a
    # slot ready while its flag still runs is cast empty, and the AI walks at a champion to cast a ready W (60-tick
    # slots with flag cooldowns: 58 attacks in a 10-minute game, -3.8)
    skill = action("skill", 3, p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                   combine(near, voice("vo_w", p), combo(0)))

    # ------------------------------------------------------------------ skill2: Q Razor Shuriken
    # under his mark with W ready the slot is an empty branch (the AI does not cast it), so the AI opens Living
    # Shadow's W-E-Q next: the pros' R-W-E-Q
    q_cast = combine(near, anim("skill2", p["q_dur"]), voice("vo_q", p), shuriken(0))
    skill2 = action("skill2", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                    sw("q_cd", NONE, sw("r_on", sw("w_cd", q_cast, NONE), q_cast)))

    # ------------------------------------------------------------------ ult: R Death Mark
    def r_pieces():
        """The R shadow (league_ekko's anchor, left where he stood): formed in the first r_echo_step ticks, then a
        checkpoint every r_echo_step copying his Q / E with its picture (a cast is two steps long: r_pic keeps the
        next standing frame off) and swapping him back when r_back is up, faded before r_live runs out.
        R2 (the user: 「做第一和第二个」): r_back comes from the pop when it killed (back to safety), from the
        outnumbered count at the pop, from the checkpoint's own look at him in crowd control (league_missfortune R's
        RandomTarget AllyChampionInCC of range 1 finds the caster: stunned, rooted, airborne, pulled, feared or charmed)
        and, with addons/league_zed_mark, from his health under r_low%."""
        step = p["r_echo_step"]
        assert step == 6, "the pieces' lengths in tools/art/import_zed.py"
        busy = [refresh("r_pic", step + 2)]
        ticks = range(step, p["r_life"] - 2 * step + 1, step)
        cc = {"type": "RandomTarget", "range": 1, "casting_target": "AllyChampionInCC", "from_projectile": False,
              "effects": [refresh("r_back", 3)]}
        back = sw("r_live", sw("r_back", combine(*rm("r_live", "r_back"), cview("w_swap"), {"type": "Teleport"},
                                                view("w_swap"), sfx("w2"))))
        out = [delayed(t, sw("r_live", combine(*checkpoint("qr_echo", "er_echo",
                                                           sw("r_pic", NONE, view(f"sh_sr{(j // 2) % 4}")), busy),
                                               cc, delayed(1, back))))
               for j, t in enumerate(ticks)]
        fade = combine(*rm("r_live"), view("sh_out"))
        # a cast on the last checkpoint finishes first
        return out + [delayed(ticks[-1] + step, sw("r_live", sw("r_pic", delayed(step, fade), fade)))]

    pop_dmg = [attack(p["r_dmg"], p["r_ratio"])]
    for k in range(1, 1 if p["native"] else 4):       # the add-on adds r_pct% of the damage dealt instead
        pop_dmg.append(sw(f"r_{k}", attack(p["r_per"] * k, 0)))
    # the kill check (league_darius R reset): r_kill set before the blow; a tick later a Delayed on the target clears
    # it - on a dead one nothing but pictures runs from a Delayed, so it stays - and 4 ticks after the blow a check on
    # him turns a kept r_kill into r_back (the R shadow's next checkpoint swaps him there)
    kill = [{"type": "Delayed", "tick": 1, "effects": [casted(3, 1, *rm("r_kill"))]},
            on_me(delayed(4, sw("r_kill", combine(*rm("r_kill"), refresh("r_back", p["r_echo_step"] + 3)))))]
    pop = combine(*rm("r_kill"), flag("r_kill", 40), view("r_pop"), tsfx("r_pop"), *pop_dmg, *kill)
    count = combine(*rm("rn1", "rn2"), around(p["r_safe_r"], "EnemyChampion",
                                             [on_me(sw("rn1", flag("rn2", 2), flag("rn1", 2)))]))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                         buff("r_safe", p["r_inv"], damaged_reduce=100, cc_immune=True),
                         {"type": "CasterInvisible", "tick": p["r_inv"]},
                         on_me(refresh("r_live", p["r_life"])),
                         line("r_anchor", 1, 1, 1, 5000, "EnemyWithoutTower", True, [],
                              [view("sh_in_r")] + r_pieces()),
                         delayed(p["r_go"] - 1, {"type": "RushMoveToBack", "speed": p["r_speed"], "applied_effects": [
                             buff("r_mark", p["r_pop"]), view("r_hit"), tsfx("r_hit"), attack(0, 100),
                             casted(p["r_pop"] + 1, p["r_pop"], sw("r_on", combine(pop, *rm("r_on", *([] if p["native"] else ["r_1", "r_2", "r_3"])))))]},
                                 refresh("r_on", p["r_pop"] + 2), spell_mark),
                         delayed(p["r_go"] + p["r_pop"] + 1, count),
                         delayed(p["r_go"] + p["r_pop"] + 2, sw("rn2", refresh("r_back", p["r_echo_step"] + 3)))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, tag=None, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_star"), P_("sh_star")]
    views_e = [E("a_hit"), E("cw_hit", FX, 3), E("e_hit"), E("e_spin", BIG, -1, False), E("q_hit"),
               E("w_dash", FX, 2, False), E("sh_out", FX, 1, False), E("sh_spin", BIG, -1, False),
               *[E(t, FX, 1, False) for t in ("sh_in_a", "sh_in_b", "sh_in_r", "sh_q", "sh_e", "sh_e8")],
               *[E(f"sh_{w}{k}", FX, 1, False) for w in ("st", "sr") for k in range(4)],
               E("w_swap", FX, 3, False), E("r_hit", BIG), E("r_pop", BIG, 3)]
    views_b = [B_("e_slow", "e_slow", FX, 3), B_("r_mark", "r_mark", FX, 4), *([] if p["native"] else [B_("cw_ready", "cw_ready", FX, 4)])]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": "league_zed_mark:edge",
                            "params": {k: p[k] for k in ("cw_hp", "cw_lo", "cw_mid", "cw_hi", "cw_cd", "r_pct", "r_low")}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (health and damage read natively)")
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
