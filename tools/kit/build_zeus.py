"""Build ragnarok_zeus.data_champion (the ragnarok pack's third hero: Zeus, top, Melee) from the parameters P.

    python tools/kit/build_zeus.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Zeus (宙斯) of Record of Ragnarok, the father of the gods who boxed Adam in the second round: a stooped old man whose
muscles swell when he gets serious and then press down into Adamas (阿陀磨须), his strongest body. Art, icons and audio
are Codex's (assets/source/zeus/: three form banks - elder, muscle, adamas - and the three changes between them), the kit
is ours after Codex's handoff (docs/ragnarok_zeus/CLAUDE_HANDOFF.md in its branch). One hero, one entity: the form is a
caster buff (`mu` muscle, `ad` Adamas, neither = the old man); ragnarok.dll's display hook (addons/ragnarok/src/zeus.rs)
shows the standing, running, hit and dying frames and the attack / skill / skill2 of the form his buffs say (mu_*,
ad_*), the data plays the changes (CasterAnimation `expand`, the ult's own `ult` = the compression, `revert`).
  passive Muscle Expansion (肌肉膨胀): every life starts old; after p_n punches (attacks, on anything: the old man
          warming up - caster flags c1 .. c3) his next attack is the expansion instead: the `expand` change (x_dur
          ticks, unstoppable, x_dr% less damage), then a burst round his feet (x_r: x_dmg + x_ad% AD, slowed x_slow%
          for x_slow_t) and the muscle buff `mu` for the rest of the life: m_atk% attack, m_def% armour and magic
          resistance.
  attack  a jab on `Enemy` (towers too): 100% AD on atk_st (frame 4, 0.245 s), the jab's wind drawn into his frames.
  skill   Barrage (连拳), `Targeting` on `EnemyWithoutTower` (q_range): two punches (frames 3 and 5, 0.18 s and
          0.315 s), each q_dmg + q_ad% AD; muscle: the second slows q_slow% for q_slow_t, Adamas: it stuns q_stun.
  skill2  The Fist That Transcends Time (超越时间之拳), `Targeting` on `EnemyWithoutTower` (e_range): the blow lands
          at once (e_dmg + e_ad% AD, stunned e_stun; Adamas e_stun_ad) - the punch itself shows only at 0.4 s, it
          was faster than time.
  ult     Adamas (阿陀磨须), `Targeting` on `EnemyChampion` (r_range): the compression (`ult`, r_go ticks; from the old
          man the expansion plays first), unstoppable and r_dr% less damage; then a blast round him (r_r: r_dmg +
          r_ad% AD, thrown up r_up) and Adamas for r_t ticks (in place of the muscle buff): r_atk% attack, r_def%
          armour and magic resistance, r_as% attack speed, r_vamp% life steal; at its end the `revert` change
          (v_dur ticks) and he is the old man again (the punches count from 0). Killed while changing: nothing.

Timings are the frames' (Codex's handoff, 60 ticks a second): the jab on frame 4 (0.245 s), the barrage on frames 3
and 5 (0.18 / 0.315 s), the time punch on frame 3 (0.4 s); the expansion 1.02 s, the compression 1.04 s, the
reverting 0.93 s.

ragnarok.dll (addons/ragnarok/src/zeus.rs): the passive ragnarok_zeus:voice (his voice lines) and the display hook.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_zeus"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"

# Units: melee range 25000, his fists a little longer; radii count the unit's collision radius (~15000) on top.
# Ticks: 60 a second. Numbers: the classic-SDK simulations (C:/t/lb_sim, lane 0, 600 s, 288 games a batch of seeds,
# kill diff with its s.e. +-0.4), 2026-11-21, against the base fighter and five more base top laners, the same games as
# Lu Bu's (+1.48 / +1.38; the League fighters' median about +1.44). The draft -0.36 / -0.31 (he dealt the most damage
# and died the most: the old man is frail and the changes stand still): more health and armour +1.02, a quicker
# expansion alone -0.30, a longer, tougher Adamas +0.36, the three together +1.43 / +0.67; with more attack +1.57 /
# +1.80, with a little more health and armour (this P) +1.18 / +1.30 (K/D/A about 2.0 / 1.4 / 3.8, 125 attacks, 42
# barrages, 32 time punches, 5 Adamas a game).
P = {
    # stats (Melee fighter, top): the old man quick, his forms make him strong
    "hp": 1150, "hp_g": 105, "atk": 90, "atk_g": 17, "apw": 0, "apw_g": 0, "def": 38, "def_g": 8, "mr": 30,
    "mr_g": 4, "ms": 1030, "ms_g": 11,
    "atk_range": 26000, "atk_dur": 39, "atk_cd": 62, "atk_st": 15,
    # passive Muscle Expansion: punches to warm up, the change, the burst, the muscle buff
    "p_n": 3, "x_dur": 61, "x_dr": 50, "x_r": 24000, "x_dmg": 90, "x_ad": 60, "x_slow": 30, "x_slow_t": 90,
    "m_atk": 25, "m_def": 35,
    # Barrage
    "q_cd": 360, "q_range": 28000, "q_dur": 38, "q_hit1": 11, "q_hit2": 19, "q_dmg": 30, "q_ad": 65,
    "q_slow": 40, "q_slow_t": 60, "q_stun": 36,
    # The Fist That Transcends Time
    "e_cd": 540, "e_range": 40000, "e_dur": 40, "e_dmg": 70, "e_ad": 110, "e_stun": 30, "e_stun_ad": 54,
    # Adamas
    "r_cd": 2700, "r_range": 30000, "r_go": 62, "r_dr": 40, "r_r": 30000, "r_dmg": 120, "r_ad": 100, "r_up": 42,
    "r_t": 600, "r_atk": 45, "r_def": 60, "r_as": 30, "r_vamp": 25, "v_dur": 56,
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def slow(name, pct, tick):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}},
                                              "move_speed_mult": -pct}}


def circle(r):
    return {"Circle": {"radius": r}}


def around(radius, effects):
    """Every enemy within `radius` of him."""
    return {"type": "RangeEffect", "shape": circle(radius), "target": "EnemyWithoutTower", "apply_type": "AroundCaster",
            "effects": list(effects)}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """A Delayed's effects, kept to a living Zeus (build_lubu.alive_only): one killed meanwhile does nothing."""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def by_form(adamas, muscle, elder):
    """The effect of his form: Adamas, muscle or the old man."""
    return when("ad", adamas, when("mu", muscle, elder))


def build(p, is_native=False):
    # ------------------------------------------------------------------ the forms
    muscle = flag("mu", None, attack_mult=p["m_atk"], defence_mult=p["m_def"], magic_resistance_mult=p["m_def"])
    guard = lambda t: flag("guard", t, cc_immune=True, damaged_reduce=p["x_dr"])
    burst = around(p["x_r"], [attack(p["x_dmg"], p["x_ad"]), slow("x_slow", p["x_slow"], p["x_slow_t"]),
                              view("x_hit")])
    # the expansion: the change, then the burst and the muscle buff (a Zeus killed meanwhile stays old)
    expand = combine(unflag("rdy"), anim("expand", p["x_dur"]), guard(p["x_dur"]), sfx("x"),
                     delayed(p["x_dur"] - 1, alive_only(muscle, cview("x_burst"), sfx("x_burst"), burst)))
    # warming up: p_n punches as the old man (flags c1, c2, c3 ...), then the next attack expands
    marks = [f"c{i}" for i in range(1, p["p_n"])]
    count = chain(marks)

    # ------------------------------------------------------------------ attack: the jab
    jab = combine(attack(0, 100), sfx("a"), view("a_hit"), tsfx("a_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      when("rdy", expand, by_form(jab, jab, combine(count, jab))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Barrage
    def punch(extra):
        return combine(attack(p["q_dmg"], p["q_ad"]), sfx("q"), view("q_hit"), tsfx("q_hit"), extra)
    second = by_form({"type": "Stun", "duration": p["q_stun"]}, slow("q_slow", p["q_slow"], p["q_slow_t"]), combine())
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(delayed(p["q_hit1"] - 1, punch(None)), delayed(p["q_hit2"] - 1, punch(second))))

    # ------------------------------------------------------------------ skill2: The Fist That Transcends Time
    stun_e = by_form({"type": "Stun", "duration": p["e_stun_ad"]}, {"type": "Stun", "duration": p["e_stun"]},
                     {"type": "Stun", "duration": p["e_stun"]})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(attack(p["e_dmg"], p["e_ad"]), stun_e, view("e_hit"), tsfx("e_hit"), sfx("e_charge"),
                            delayed(23, sfx("e"))))

    # ------------------------------------------------------------------ ult: Adamas
    adamas = flag("ad", p["r_t"], attack_mult=p["r_atk"], defence_mult=p["r_def"], magic_resistance_mult=p["r_def"],
                  attack_speed_mult=p["r_as"], vamp=p["r_vamp"])
    blast = around(p["r_r"], [attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]},
                              view("r_hit")])
    revert = combine(anim("revert", p["v_dur"]), unflag("ad"), sfx("v"))

    def pressed(go):
        """The compression from the muscle body (`go` ticks after the cast), then Adamas and, r_t later, the revert."""
        return combine(delayed(go, anim("ult", p["r_go"])) if go else None,
                       delayed(go + p["r_go"] - 1, alive_only(unflag("mu"), adamas, cview("x_burst"), sfx("r_burst"),
                                                              blast)),
                       delayed(go + p["r_go"] - 1 + p["r_t"], alive_only(revert)))
    from_old = combine(anim("expand", p["x_dur"]), sfx("x"), pressed(p["x_dur"]))
    ult = action("ult", p["r_go"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(*[unflag(m) for m in marks], unflag("rdy"), sfx("r"),
                         # Adamas cannot cast it again (r_cd > r_t): the muscle body presses down, the old man swells first
                         when("mu", combine(guard(p["r_go"] + 2), pressed(0)),
                              combine(guard(p["x_dur"] + p["r_go"] + 2), from_old))))

    # ------------------------------------------------------------------ views
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    # the jab's wind, the barrage's streaks, the time punch's charge and release and the changes' rising light are
    # drawn into his own frames (tools/art/import_zeus.py); these play on units
    views_e = [E("a_hit", "jab_hit"), E("q_hit", "barrage_hit"), E("e_hit", "barrage_hit", 3),
               E("x_hit", "jab_hit"), E("x_burst", "form_burst", 1), E("r_hit", "barrage_hit", 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll (addons/ragnarok/src/zeus.rs): his voice lines; the display hook needs no data
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:voice", "params": {}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def chain(marks):
    """c1 unset -> set c1; c1 set, c2 unset -> set c2; ... all set -> clear them and set rdy."""
    e = combine(*[unflag(m) for m in marks], flag("rdy", None))
    for m in reversed(marks):
        e = when(m, e, flag(m, None))
    return e


def nodes(o):
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
    ap_.add_argument("--plain", action="store_true", help="for the balance sims: no DLL passive")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, not a.plain)
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
