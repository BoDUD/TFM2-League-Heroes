"""Build league_xayah.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_xayah.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's pick B, 2026-10-08; the Rakan duo is added afterwards, on buffs only she gives):
  feathers  A feather is the stop point of a penetrating `LinearProjectile` (a dagger or an empowered attack). It lies
          there as a stamp (a `ViewEffect` every f_step ticks, so it vanishes the moment it flies) and comes back as a
          `BackToCasterLinearProjectile` from that point (league_ekko Q / league_pyke E: the only projectile that leaves
          from a point is a BackToCaster one in a projectile's end_effects or a Delayed there). Nothing can wait for an
          on-demand E, so the recall is a fixed moment: a caster flag `rc` (f_step + 1 ticks) that every lying feather
          polls for f_life ticks (League: 6 s); Q's and R's own feathers fly back on the recall tick itself.
          A returning feather: e_dmg + e_ratio% AD to every enemy it passes; the third champion hit of one recall and
          every one after it are rooted (e_root ticks) - League roots an enemy hit by 3 feathers, nothing counts hits
          per target, so the count is hers (rh1, rh2 caster flags, cleared at each recall).
  passive Clean Cuts: every spell adds 3 empowered attacks (p1..p5 caster flags, League's store of 5, p_t ticks). An
          empowered attack is a penetrating line at the target, a_pierce% to every unit after the first (a_hit1/2
          flags per line), flying a_reach so the feather lands behind the target.
  attack  a homing blade (physical 100% AD); with W on, a second blade w_blade ticks later for w_pct% (a champion hit
          by it gives her w_ms% move speed for w_ms_t ticks).
  skill   Q Double Daggers -> E Bladecaller: a `Direction` cast on `EnemyWithoutTower` (aimed at an enemy champion in
          reach, else the cast direction): two penetrating daggers q_gap ticks apart (q_dmg + q_ratio% AD, q_fall% after
          the first unit), each leaving a feather at its full range; q_recall ticks after the release the recall: E's
          pose, `rc` for the lying feathers, the daggers' feathers fly back.
  skill2  W Deadly Plumage: `None` on `EnemyWithoutTower` within her attack range: w_as% attack speed for w_t ticks, the
          second blade on every attack, 3 empowered attacks.
  ult     R Featherstorm: a `Direction` cast on `EnemyChampion`: she leaps (r_air ticks untargetable in effect:
          CasterInvisible + damaged_reduce 100 + cc_immune, league_masteryi Q's way - a self-Banish blinds her team), at
          r_hit the dagger rain (a `LineRangeProjectile` fan, league_ashe W: r_dmg + r_ratio% AD) and r_n feathers in a
          row along the cast line; r_recall ticks later the recall; 3 empowered attacks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_xayah.data_champion")
ID = "league_xayah"
FX = "asset/league/effects/league_xayah_fx"
BIG = "asset/league/effects/league_xayah_big"

# Numbers = candidate e1 of the 10-min classic-SDK simulations (xy_sim/sim/kd.py, bottom lane against gunner, archer and
# boomerang_hunter, three lineups, both sides, 2026-10-08): +1.81 on seeds 1-24, +1.83 on seeds 25-48 (the pack's
# league_varus +2.11 / +2.15, league_jhin +1.92 / +2.01 in the same batches). The draft was -0.68: the empowered attack
# as a bare line missed walking targets (a_mode 1: a homing blade gives the target its 100%, +0.85), then attack 100 /
# interval 50 / range 57500, Q 60 + 80%, feathers 50 + 60%, W every 8 s with 50% attack speed, hp 980 and defence 24.
# R (the user: 「霞的大招逻辑要注意 别乱放」): on EnemyChampionRecentlyAttacked within 60000 - a fight on - instead of any
# enemy champion within 85000: 3.3 casts a game, 1 of 40 with no champion under the rain (6 of 58 before), 1.5 champions
# a cast; +2.12 on seeds 1-24 (the old R +1.31, 85000 on the same target +1.77).
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Xayah: 525 range
    "hp": 980, "hp_g": 88, "atk": 100, "atk_g": 19, "def": 24, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 910, "ms_g": 9,
    # attack: the blade leaves her hand on atk_st
    "atk_range": 57500, "atk_dur": 24, "atk_cd": 50, "atk_st": 8, "a_speed": 7000, "a_y": -3000,
    # passive Clean Cuts (League: 3 a spell, store 5, 8 s; other targets on the path take ~50%)
    "p_t": 480, "a_reach": 72000, "a_rad": 5000, "a_pierce": 50, "a_mode": 1,
    # feathers (League: 6 s on the ground)
    "f_life": 360, "f_step": 20, "f_speed": 4500, "f_rad": 5500, "f_reach": 160000,
    # E Bladecaller (League: 55-155 + 60% bonus AD a feather, minions 50%, root 1.25 s at 3 feathers)
    "e_dmg": 50, "e_ratio": 60, "e_root": 75, "e_need": 3,
    # W Deadly Plumage (League: +35-55% attack speed 4 s, second blade 25%, +30% move speed 1.5 s; cd 20-14 s)
    "w_cd": 480, "w_t": 240, "w_as": 50, "w_blade": 6, "w_pct": 25, "w_ms": 30, "w_ms_t": 90,
    # skill: Q Double Daggers (League: 2 x 45-125 + 50% bonus AD, 1100 range, later targets 50%, cd 10-6 s)
    "q_cd": 420, "q_range": 75000, "q_dur": 18, "q_st": 8, "q_gap": 6, "q_aim": 90000, "q_reach": 95000,
    "q_speed": 6000, "q_rad": 5500, "q_y": -3000, "q_dmg": 60, "q_ratio": 80, "q_fall": 50, "q_recall": 70,
    "e_t": 20,
    # ult: R Featherstorm (League: 100-300 + 100% bonus AD, untargetable 1.25 s, a cone of daggers, cd 160-100 s)
    "r_cd": 3600, "r_target": "EnemyChampionRecentlyAttacked", "r_range": 60000, "r_dur": 70, "r_air": 66, "r_hit": 48, "r_dmg": 160, "r_ratio": 100,
    "r_len": 90000, "r_width": 40000, "r_n": 5, "r_near": 40000, "r_far": 95000, "r_recall": 40,
    # the Rakan duo (the user's option 1): every attack marks the allies within duo_r for duo_t ticks (Rakan's E reaches
    # duo_r while he has it), W marks those within duo_w_r for w_t (Rakan takes W's attack speed, move speed and second
    # feather); his E shield on her plays her line, once per vo_cd ticks
    "duo_r": 130000, "duo_t": 120, "duo_w_r": 70000, "vo_cd": 600,
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
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


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
    """Effects on her alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, rng, radius, target, effects, end=()):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": rng,
            "shape": circle(radius), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def fan(name, width, length, delay, apply_, target, effects):
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply_, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ feathers
    def fly_back():
        """A feather leaving its point for her: damage on the way, the root from the recall's third champion hit."""
        root = combine({"type": "Bind", "duration": p["e_root"]}, buff("e_bind", p["e_root"]), view("e_root"),
                       tsfx("e_root"))
        count = sw("rh2", root, sw("rh1", root if p["e_need"] == 2 else flag("rh2", 60), flag("rh1", 60)))
        dmg = back("feather", p["f_speed"], p["f_reach"], p["f_rad"], "EnemyWithoutTower",
                   [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")])
        champ = back("feather_c", p["f_speed"], p["f_reach"], p["f_rad"], "EnemyChampion", [count])
        return [dmg, champ]

    def lying(steps):
        """A feather that lies `steps` x f_step ticks (a stamp each step) and then flies back."""
        out = fly_back()
        for _ in range(steps):
            out = [view("f_lie"), delayed(p["f_step"], *out)]
        return out

    def waiting():
        """A feather from an empowered attack: lies up to f_life ticks, flies back when it sees the recall flag."""
        out = []
        for _ in range(p["f_life"] // p["f_step"]):
            out = [sw("rc", combine(*fly_back()), combine(view("f_lie"), delayed(p["f_step"], *out)))]
        return out

    recall = combine(*rm("rh1", "rh2"), refresh("rc", p["f_step"] + 1), anim("skill_e", p["e_t"]), cview("e_cast"),
                     sfx("e_cast"))

    # ------------------------------------------------------------------ passive: empowered attacks
    def arm():
        """A spell: +3 empowered attacks, at most 5 (p1..p5: the count, one flag at a time)."""
        def to(k):
            return combine(*rm("p1", "p2", "p3", "p4", "p5"), flag(f"p{min(k, 5)}", p["p_t"]), cview("p_on"))
        return sw("p5", to(5), sw("p4", to(7), sw("p3", to(6), sw("p2", to(5), sw("p1", to(4), to(3))))))

    def spend():
        out = NONE
        for k in range(1, 6):
            out = sw(f"p{k}", combine(*rm(f"p{k}"), *([flag(f"p{k - 1}", p["p_t"])] if k > 1 else [])), out)
        return out

    # ------------------------------------------------------------------ attack
    blade = homing("a_blade", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    w_hit = [attack(0, p["w_pct"]), view("a_hit")]
    w_ms = [refresh("w_ms", p["w_ms_t"], move_speed_mult=p["w_ms"])]
    second = combine(delayed(p["w_blade"], cview("w_flash"), sfx("w_blade"),
                             homing("w_blade", p["a_speed"], p["a_y"], "Enemy", w_hit),
                             homing("w_blade_c", p["a_speed"], p["a_y"], "EnemyChampion", w_ms)))
    # a_mode 0: the line alone, its first unit 100%; 1: a homing blade gives the target its 100% (a line can miss a
    # walking target) and the line skips its first unit (the target, mostly) and cuts the rest
    first = flag("a_h1", 30) if p["a_mode"] else combine(flag("a_h1", 30), attack(0, 100), view("a_hit"), tsfx("a_hit"))
    pierce_hit = sw("a_h1", combine(attack(0, p["a_pierce"]), view("a_hit")), first)
    pierce = line("a_pierce", p["a_speed"], p["a_reach"], p["a_rad"], p["a_y"], "EnemyWithoutTower", True,
                  [pierce_hit], end=[view("f_drop"), sfx("f_drop")] + waiting())
    plain = combine(sfx("a_shot"), blade)
    strong = combine(sfx("a_shot_p"), *rm("a_h1"), pierce, spend(), *([blade] if p["a_mode"] else []))
    mark = flag("p_any", 1)
    any_p = combine(*rm("p_any"), sw("p1", mark, sw("p2", mark, sw("p3", mark, sw("p4", mark, sw("p5", mark))))),
                    sw("p_any", strong, plain))
    # the duo: nothing here reads Rakan; his kit (tools/fix/rakan_xayah_duo.py) reads these marks
    duo = around(p["duo_r"], "AllyNotSelf", [buff("duo", p["duo_t"])])
    shielded = {"type": "SwitchByBuff", "buff_name": "league_rakan_e_on", "effect_none": NONE,
                "effect_buff": sw("vo_cd", NONE, combine(sfx("shield_rakan"), flag("vo_cd", p["vo_cd"])))}
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(any_p, sw("w_on", second), duo, shielded), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Double Daggers -> E Bladecaller
    flight = p["q_reach"] // p["q_speed"]
    wait = max(p["q_recall"] - flight, 0)

    def dagger(name):
        hit = sw("q_h1", combine(attack(p["q_dmg"] * p["q_fall"] // 100, p["q_ratio"] * p["q_fall"] // 100),
                                 view("q_hit")),
                 combine(flag("q_h1", 20), attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")))
        end = [view("f_drop")] + lying(wait // p["f_step"]) if wait >= p["f_step"] else [view("f_drop")] + fly_back()
        return line(name, p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True, [hit],
                    end=[delayed(wait % p["f_step"], *end)] if wait % p["f_step"] else end)

    def throw(first):
        d = dagger("q_dagger")
        return combine(*rm("q_h1"), cview("q_flash"), sfx("q_cast"), d) if first else \
            combine(*rm("q_h1"), sfx("q_throw"), d)

    def release():
        aim = p["q_reach"] - 10000
        both = lambda: [throw(True), delayed(p["q_gap"], throw(False))]
        return combine(*rm("q_go"), pick(aim, "EnemyChampion", flag("q_go", 1), *both()),
                       sw("q_go", NONE, combine(*both())))

    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(anim("skill", p["q_dur"]), arm(), release(), delayed(p["q_recall"], recall)))

    # ------------------------------------------------------------------ skill2: W Deadly Plumage
    skill2 = action("skill2", 12, p["w_cd"], 2, p["atk_range"], "None", "EnemyWithoutTower",
                    combine(anim("skill2", 24), refresh("w_on", p["w_t"], attack_speed_mult=p["w_as"]),
                            cview("w_cast"), sfx("w_cast"), arm(),
                            around(p["duo_w_r"], "AllyNotSelf", [buff("duo_w", p["w_t"])])))

    # ------------------------------------------------------------------ ult: R Featherstorm
    guard = flag("r_air", p["r_air"], damaged_reduce=100, cc_immune=True)
    rain = fan("r_rain", p["r_width"], p["r_len"], 18, 3, "EnemyWithoutTower",
               [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")])
    rows = []
    for i in range(p["r_n"]):
        reach = p["r_near"] + (p["r_far"] - p["r_near"]) * i // max(p["r_n"] - 1, 1)
        fl = reach // p["q_speed"]
        rest = max(p["r_recall"] - fl, 0)
        end = [view("f_drop")] + lying(rest // p["f_step"])
        rows.append(line(f"r_feather", p["q_speed"], reach, 1000, 0, "Enemy", True, [],
                         end=[delayed(rest % p["f_step"], *end)] if rest % p["f_step"] else end))
    ult = action("ult", p["r_dur"], p["r_cd"], 2, p["r_range"], "Direction", p["r_target"],
                 combine(anim("ult", p["r_dur"]), {"type": "CasterInvisible", "tick": p["r_air"]}, guard,
                         cview("r_cast"), sfx("r_cast"), arm(),
                         delayed(p["r_hit"], sfx("r_rain"), rain, *rows),
                         delayed(p["r_hit"] + p["r_recall"], recall)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1, repeat=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                    "repeat": repeat, "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_blade"), P_("w_blade"), P_("a_pierce"), P_("q_dagger"), P_("feather"), P_("r_rain", BIG, 2, False)]
    views_e = [E("a_hit", FX, 2), E("w_flash", FX, 2, **LATE), E("q_flash", FX, 2, **LATE), E("q_hit", FX, 2),
               E("f_drop", FX, 0, False), E("f_lie", FX, 0, False), E("e_cast", FX, 2, **LATE), E("e_hit", FX, 2),
               E("e_root", FX, 2), E("w_cast"), E("p_on", FX, 2, **LATE), E("r_cast"), E("r_hit", FX, 2)]
    views_b = [B_("e_bind", FX, 2), B_("w_on", FX, -1), B_("w_ms", FX, -1)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "CC"],
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
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
