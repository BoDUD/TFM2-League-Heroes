"""Build league_seraphine.data_champion (support, Util) from the parameters P.

    python tools/kit/build_seraphine.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-07, all the recommended options: Q alone / E -> W combo / the echo and the notes both
in data / R a charming line that reaches farther past an ally, armed until two champions stand near; plus the pro
combos):
  passive Stage Presence (星光漫射):
          echo - every cast (Q, E -> W, R, the combos' casts too) climbs c1 on her; the next one with c1 held turns it
          into `echo` (Permanent, its picture glowing round her) and the one after that is played twice, the copy
          echo_delay ticks later (League's every-third-spell echo). Q leaves a ready echo alone for echo_hold ticks
          (saved for E -> W or R) and takes it after that.
          notes - every cast gives her one note and one more for each other allied champion within note_r (League:
          her allies near her get one when she casts): rungs n1..n4 on her (one at a time, note_t ticks, each with
          +note_range attack range). Her next attack spends all of them: the bolt flies as a charged note adding
          k x (note_dmg + note_ratio% AP) magic.
  attack  A sound bolt (homing, physical 100% AD), or the charged note above.
  skill   Q High Note (清籁穿云): a `Targeting` cast on `EnemyWithoutTower` (q_range): a note lobbed onto where the target
          stands (q_travel ticks, dodgeable), magic q_dmg + q_ratio% AP round it (q_r). League adds up to 75% against
          missing health; nothing reads health, so a twin of the lob on `EnemyChampionInCC` adds q_amp% to champions
          held by crowd control (her E's root and stun, R's charm - the pro combo E -> Q aims there).
  skill2  E Beat Drop (增幅节拍) -> W Surround Sound (聚和心声): a `Targeting` cast on `EnemyChampion` (e_range).
          E: a piercing wave (e_len, e_speed) on `EnemyWithoutTower`: magic e_dmg + e_ratio% AP and e_slow% slow
          e_slow_t. Already slowed -> rooted: nothing reads a slow on the target, so every champion hit carries her
          mark (an `AddCasted` poll e_mark ticks, armed 4 ticks after the hit) that roots e_root when the echoed wave
          (flag e_2nd while it flies) hits a champion (the caster flag e_rt, 3 ticks): the echo roots what the first
          wave slowed, as in League (her own E is the only slow she has; its cooldown outlasts the slow). Already crowd-controlled -> stunned: a twin wave on `EnemyChampionInCC` stuns e_stun.
          The slot's E -> W runs the echo and the notes; a combo's E (from R) as well.
          W, w_rel ticks into the action: every allied champion within w_r (her too) gets a w_sh + w_sh_ratio% AP
          shield and +w_ms% move speed (w_t ticks); w_heal_delay ticks later the ones still near are healed
          w_heal + w_heal_ratio% AP once for every allied champion near (League: a share of missing health per ally).
          The slot's cooldown is E's; the combos' E lays the caster flag e_cd, and a slot cast inside it is W alone.
  ult     R Encore (炫音返场): a 3-tick `Targeting` cast on `EnemyChampion` (r_slot). Armed like league_twitch R: with two
          enemy champions within r_reach it fires at once, else it arms r_armed for r_arm ticks - each of her attacks
          counts again and fires it, and after r_hold ticks one champion in her attack's reach is enough -
          and refunds the cooldown (ult_cooldown_mult 4900) when it lapses unused.
          Fire: a fast hidden probe line on `AllyChampion` (r_len) looks for an ally ahead (flag r_ext), then the
          wave (r_speed, r_w) goes r_len, or r_len2 with an ally ahead (League's wave extends through allies): magic
          r_dmg + r_ratio% AP and a r_charm-tick charm on every enemy champion.
  combos  (「要」高手连招): E -> Q: cq_wait ticks after E's wave leaves, with Q's flag q_cd off, the High Note lands on
          a crowd-controlled champion in Q's reach (the one just rooted or stunned; a note, no echo); R -> E: rc_wait
          ticks after the wave leaves,
          with e_cd off, Beat Drop (-> W) goes to a charmed champion and stuns; the echo is saved for E -> W / R (above).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_seraphine.data_champion")
ID = "league_seraphine"
FX = "asset/league/effects/league_seraphine_fx"
BIG = "asset/league/effects/league_seraphine_big"

# Draft numbers (to be set by the classic-SDK simulations: kd.py --lane 4 against priest, bard, enchanter, monk, taoist).
P = {
    # stats (Util, league_sona: attack 80 +6, AP 30 +15, hp 950 +95, def/mr 24); League's Seraphine: 525 range, 50 AD,
    # 570 +90 hp, 26 armour, 325 move speed
    "hp": 920, "hp_g": 92, "atk": 75, "atk_g": 6, "ap": 30, "ap_g": 15, "def": 22, "def_g": 7, "mr": 24, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    # attack: the bolt leaves her hand on a_st
    "atk_range": 55000, "atk_dur": 30, "atk_cd": 90, "a_st": 9, "bolt_speed": 6000, "bolt_y": 1500,
    # passive (League: notes 4% AP + level scaling each, max 4, 6 s, +25 range; echo every 3rd spell)
    "note_t": 360, "note_r": 60000, "note_dmg": 12, "note_ratio": 12, "note_range": 3000,
    "echo_delay": 12, "echo_hold": 300,
    # skill: Q High Note (League: 900 range, radius 350, 35-185 + 40% AP, up to +75% vs missing health, cd 8-6 s)
    "q_cd": 480, "q_range": 75000, "q_anim": 24, "q_rel": 10, "q_travel": 18, "q_r": 30000, "q_dmg": 70,
    "q_ratio": 50, "q_amp": 75,
    # skill2: E Beat Drop (League: 1300 line, 40-220 + 50% AP, slow 1-1.6 s, root slowed, stun CC'd, cd 11-9 s)
    "e_cd": 600, "e_range": 85000, "e_anim": 34, "e_rel": 9, "e_speed": 6000, "e_len": 100000, "e_w": 9000,
    "e_dmg": 60, "e_ratio": 45, "e_slow": 60, "e_slow_t": 60, "e_root": 60, "e_stun": 60, "e_mark": 90,
    # -> W Surround Sound (League: 800 range, shield 40-160 + 20% AP 2.5 s, +20% MS, heal 6-18% missing HP a nearby
    # ally after 2.5 s, cd 22 s)
    "w_rel": 22, "w_r": 50000, "w_sh": 60, "w_sh_ratio": 30, "w_t": 150, "w_ms": 20, "w_heal_delay": 150,
    "w_heal": 10, "w_heal_ratio": 8,
    # ult: R Encore (League: 1200 range extended by allies, 100-400 + 40% AP, charm 1-2.5 s, cd 160-120 s)
    "r_cd": 3300, "r_slot": 80000, "r_reach": 70000, "r_arm": 600, "r_hold": 180, "r_anim": 30, "r_rel": 12,
    "r_speed": 5000, "r_len": 90000, "r_len2": 150000, "r_w": 18000, "r_dmg": 150, "r_ratio": 60, "r_charm": 90,
    # combos
    "cq_wait": 10, "rc_wait": 20,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Ally"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(radius), "range_effect_name": "", "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    ns = ["n1", "n2", "n3", "n4"]

    # ------------------------------------------------------------------ passive: notes and the echo
    # one note rung at a time, read from the top: n4 renews itself, n<k> steps up, none starts n1
    def note_flag(k):
        return flag(ns[k], p["note_t"], range=p["note_range"])

    climb = note_flag(0)
    for k in range(len(ns) - 1):
        climb = sw(ns[k], combine(*rm(ns[k]), note_flag(k + 1)), climb)
    climb = sw(ns[-1], combine(*rm(ns[-1]), note_flag(len(ns) - 1)), climb)
    notes = combine(climb, around(p["note_r"], "AllyNotSelf", [climb]))

    def cast(play, hold=False, copy=()):
        """A spell: its notes, the echo ladder (c1 -> echo ready -> the copy echo_delay ticks later, after `copy`), then
        the play. With hold, a ready echo is kept for echo_hold ticks (Q saves it for E -> W and R)."""
        echoed = combine(*rm("echo"), cview("echo"), sfx("echo"), delayed(p["echo_delay"], *copy, play))
        count = sw("c1", combine(*rm("c1"), flag("echo", None), refresh("e_hold", p["echo_hold"])),
                   flag("c1", None))
        ready = sw("e_hold", NONE, echoed) if hold else echoed
        return combine(notes, sw("echo", ready, count), play)

    # ------------------------------------------------------------------ Q High Note
    q_amp = p["q_amp"] / 100

    def q_note():
        return combine(sfx("q_throw"),
                       lob("q_note", p["q_travel"], p["q_r"], "EnemyWithoutTower",
                           [magic(p["q_dmg"], p["q_ratio"]), view("q_hit")], end=[view("q_land"), sfx("q_hit")]),
                       lob("q_amp", p["q_travel"], p["q_r"], "EnemyChampionInCC",
                           [magic(round(p["q_dmg"] * q_amp), round(p["q_ratio"] * q_amp)), view("q_amp")]))

    q_slot = combine(refresh("q_cd", p["q_cd"]), sfx("q_cast"), voice("vo_q", p), anim("skill", p["q_anim"]),
                     delayed(p["q_rel"], cast(q_note(), hold=True)))
    # the combo's Q: no pose of its own (she is in E's), the note thrown at once, a note for her, no echo
    q_combo = combine(refresh("q_cd", p["q_cd"]), sfx("q_cast"), notes, q_note())

    # ------------------------------------------------------------------ skill2's E (also played by R -> E)
    mark = delayed(4, casted(p["e_mark"], 2, sw("e_rt", combine({"type": "Bind", "duration": p["e_root"]}, view("e_root"))), kind="Bleed"))
    champ = pick(1000, "EnemyChampion", on_me(sw("e_2nd", refresh("e_rt", 3))), fp=True)

    def wave():
        return combine(sfx("e_wave"),
                       line("e_wave", p["e_speed"], p["e_len"], p["e_w"], 0, "EnemyWithoutTower", True,
                            [magic(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                             view("e_hit"), champ, mark]),
                       line("e_stun", p["e_speed"], p["e_len"], p["e_w"], 0, "EnemyChampionInCC", True,
                            [{"type": "Stun", "duration": p["e_stun"]}, view("e_stun"), tsfx("e_stun")]))

    def w_song():
        hit = [shield(p["w_sh"], p["w_sh_ratio"], p["w_t"]), buff("w_on", p["w_t"], move_speed_mult=p["w_ms"])]
        mend = [view("w_heal"), around(p["w_r"], "AllyChampion", [heal(p["w_heal"], p["w_heal_ratio"])])]
        return combine(cview("w_cast"), sfx("w_cast"), voice("vo_w", p), around(p["w_r"], "AllyChampion", hit),
                       delayed(p["w_heal_delay"], sfx("w_heal"), around(p["w_r"], "AllyChampion", mend)))

    # E -> Q: once the wave has passed, a crowd-controlled champion in Q's reach takes the High Note
    e_q = delayed(p["e_rel"] + p["cq_wait"], sw("q_cd", NONE, pick(p["q_range"], "EnemyChampionInCC", q_combo)))
    e_then_w = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_anim"]), voice("vo_e", p),
                       delayed(p["e_rel"], cast(combine(wave(), delayed(p["w_rel"] - p["e_rel"], w_song())),
                                                copy=[refresh("e_2nd", p["e_len"] // p["e_speed"] + 8)])), e_q)

    # ------------------------------------------------------------------ R Encore
    def count():
        """2-tick flags u1 -> u2: two enemy champions within r_reach."""
        return combine(*rm("u1", "u2"),
                       around(p["r_reach"], "EnemyChampion", [sw("u1", refresh("u2", 2), refresh("u1", 2))]))

    def r_wave(rng):
        return line("r_wave", p["r_speed"], rng, p["r_w"], 0, "EnemyChampion", True,
                    [magic(p["r_dmg"], p["r_ratio"]), {"type": "Charm", "tick": p["r_charm"]}, view("r_hit"),
                     tsfx("r_charm")])

    def encore():
        return combine(*rm("r_ext"), sfx("r_wave"),
                       line("r_probe", 60000, p["r_len"], p["r_w"], 0, "AllyChampion", True,
                            [on_me(refresh("r_ext", 4))]),
                       delayed(2, sw("r_ext", r_wave(p["r_len2"]), r_wave(p["r_len"]))))

    # R -> E: once the wave has passed, a charmed champion takes Beat Drop (a stun: he is crowd-controlled)
    r_e = sw("e_cd", NONE, pick(p["e_range"], "EnemyChampionInCC", e_then_w))

    def fire(slot):
        rel = p["r_rel"] if slot else 0
        out = [*rm("r_armed"), sfx("r_cast"), voice("vo_r", p), cview("r_cast"),
               delayed(rel, cast(encore())), on_me(delayed(rel + p["rc_wait"], r_e))]
        if slot:
            out.append(anim("ult", p["r_anim"]))
        return combine(*out)

    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(count(), sw("u2", fire(True), arm)))

    # armed: two champions in reach fire it, or one in her attack's reach once r_hold ticks have passed
    near = pick(p["atk_range"] + 5000, "EnemyChampion", refresh("r_solo", 2))
    go = sw("r_armed", combine(*rm("r_solo"), count(), sw("u2", refresh("r_solo", 2), sw("r_wait", NONE, near)),
                               sw("r_solo", fire(False))))

    # ------------------------------------------------------------------ the slots
    skill = action("skill", p["q_anim"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q_slot))
    # the slot's own cooldown is E's; a combo's E lays e_cd too, and a slot cast inside it is W alone (no echo, no note)
    skill2 = action("skill2", p["e_anim"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    sw("e_cd", delayed(p["w_rel"] - p["e_rel"], w_song()), e_then_w))

    # ------------------------------------------------------------------ attack: the bolt, or the charged note
    def bolt(k):
        if k == 0:
            return homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy",
                          [attack(0, 100), view("a_hit")])
        return homing("a_note", p["bolt_speed"], p["bolt_y"], "Enemy",
                      [attack(0, 100), magic(k * p["note_dmg"], k * p["note_ratio"]), view("a_note_hit")])

    shoot = delayed(p["a_st"], sfx("a_shot"), bolt(0))
    for k in range(len(ns)):
        shoot = sw(ns[k], combine(*rm(*ns), delayed(p["a_st"], sfx("a_note"), bolt(k + 1))), shoot)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(go, shoot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow her (the red side's mirroring); the
    # flying notes and waves are drawn top-bottom symmetric, the buffs left-right symmetric; Q's ground burst is a
    # ViewEffect on the landing point (never turned)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bolt"), P_("a_note"), P_("q_note"), P_("e_wave", BIG), P_("r_wave", BIG)]
    views_e = [E("a_hit"), E("a_note_hit"), E("q_hit"), E("q_land", BIG, -1, follow=False), E("q_amp"),
               E("e_hit"), E("e_root"), E("e_stun"), E("w_cast", BIG, -1, **LATE), E("w_heal"), E("r_cast", BIG, 3, **LATE),
               E("r_hit"), E("echo", FX, 3, **LATE)]
    views_b = [B_("n1", FX, 3), B_("n2", FX, 3), B_("n3", FX, 3), B_("n4", FX, 3), B_("echo", FX, 3),
               B_("e_slow", FX, -1), B_("w_on", FX, -1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "CC", "Heal", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2",
                        f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--set", nargs="*", default=[])
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    a = ap_.parse_args()
    p = dict(P)
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
