"""Build ragnarok_thor.data_champion (the ragnarok pack's second hero: Thor, top lane, Tank) from the parameters P.

    python tools/kit/build_thor.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Thor (索尔) of Record of Ragnarok, the Norse god of thunder who fought Lu Bu in the first round, with Mjolnir and its
awakening. The ragnarok pack's second hero; art, icons and audio are Codex's (assets/source/thor/), the kit is ours after
Codex's four icons and handoff (docs/ragnarok_thor/CLAUDE_HANDOFF.md in its branch): a heavy hammer, a slam that sends
lightning through the ground, a hammer that flies out and comes back, and Mjolnir's awakening. A tank of the top lane
(category Tank, game 0.7.3+), his blows scaling with his health; Lu Bu is the pack's fighter.
  passive Mjolnir Awakening (雷槌觉醒): every third cast of Thunder God's Hammer or Returning Hammer awakens Mjolnir for
          p_t ticks (the red cracks and their sound; a counter of caster flags, t1 / t2). Awake, his attacks add p_dmg +
          p_hp% of his max health as magic damage (lightning) and the slam stuns q_stun ticks instead of q_stun0.
  attack  a hammer blow on `Enemy` (towers too): 100% AD on atk_st, the thunder spark on the target.
  skill   Thunder God's Hammer (雷神之锤), `Targeting` on `EnemyWithoutTower` (q_range): the hammer comes down on q_hit;
          the ground lightning hits every enemy within q_r of a point q_off in front of him: q_dmg + q_ad% AD + q_hp% of
          his max health, stunned q_stun0 ticks (awake: q_stun; a q_stun0 of 0 slows q_slow% for q_slow_t instead).
  skill2  Returning Hammer (回旋雷槌), `Direction` on `EnemyWithoutTower` (e_range): on e_go he throws Mjolnir
          e_len straight ahead and it flies back to him (league_sivir's Q: a LinearProjectile whose end starts a
          BackToCasterLinearProjectile), through every enemy both ways: e_dmg + e_ad% AD + e_hp% max health, slowed
          e_slow% for e_slow_t. His hands stay empty while it flies (`skill2_wait`, a CasterAnimation held up to e_wait
          ticks); the catch (`skill2_catch`) and its shield (e_sh + e_sh_ad% AD for e_sh_t ticks) come only when it
          really reaches him - the return's end_effects, never a timer (Codex's handoff).
  ult     Awakened Thunder Hammer (觉醒雷槌), `Targeting` on `EnemyChampion` (r_range): Mjolnir awakens at once for
          r_awake ticks; he gathers himself r_go ticks - unstoppable, taking r_dr% less damage - and brings it down:
          every enemy within r_r of a point r_off ahead takes r_dmg + r_ad% AD + r_hp% of his max health and is thrown
          up r_up ticks. A Thor killed while gathering does not strike (the alive search).

Timings are the frames' (Codex's asset_manifest_v01.json presentation_events, 60 ticks a second): the attack's blow on
frame 4 (0.42 s), the throw on frame 3 (0.36 s), the ult's blow on frame 5 (1.24 s); the slam's frame 4 is drawn at
0.62 s and played at 0.43 s (q_hit 26, tools/art/import_thor.py RETIME).

ragnarok.dll (addons/ragnarok/src/thor.rs): the passive ragnarok_thor:voice - only his voice lines (the rules are all
data: --plain is the same kit with category Melee for the classic engine, which has no Tank).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_thor"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
PROJ = f"asset/{MOD_ID}/effects/{ID}_proj"

# Units: melee range 25000 for the base tanks, his hammer a little longer; radii count the unit's collision radius
# (~15000) on top. Ticks: 60 a second. Numbers: the classic-SDK simulations (C:/t/lb_sim, lane 0, 600 s, 288 games a
# batch of seeds, kill diff with its s.e. +-0.4), 2026-11-20 - the League tank controls (two batches each): Cho'Gath
# +0.99 / +1.05, Dr. Mundo +0.82 / +0.38, Malphite +0.23 / +1.44, Nasus +0.96 / +0.96, Olaf +0.31 / +1.17, Ornn +1.86 /
# +1.53, Shen +1.96 / +1.37, Sion +1.51 / +1.58 (mean +1.13). The draft -1.95 / -2.85: the slam and the throw quicker
# (q_hit 26 / q_dur 46, e_len 44000 at e_speed 5000) -0.86, the plain slam stunning (q_stun0) -0.62, a wider ult +-0,
# q_cd 360 + e_slow 40 +0.36; more health / armour / shield -0.49, a longer awakening +0.28, more AD or a quicker
# attack no better; the ult (r_dr 45, r_cd 2400, r_dmg 180) +0.65, with the stun and a little health +0.68, its throw
# 1.5 s over r_r 44000 +1.22; this P +1.41 / +0.77 (K/D/A 1.67 / 1.00 / 3.86, 97 attacks, 41 slams, 34 throws, 6.7 ults
# a game).
P = {
    # stats (Tank, top): the base tanks' (atk 80 +6, hp 1100 +120, def 40 +10, mr 30 +5), a god a little more
    "hp": 1220, "hp_g": 120, "atk": 84, "atk_g": 12, "apw": 0, "apw_g": 0, "def": 40, "def_g": 9, "mr": 30,
    "mr_g": 5, "ms": 990, "ms_g": 10,
    "atk_range": 27000, "atk_dur": 36, "atk_cd": 76, "atk_st": 24,
    # passive Mjolnir Awakening
    "p_t": 360, "p_dmg": 25, "p_hp": 3, "p_n": 3,
    # Thunder God's Hammer
    "q_cd": 360, "q_range": 30000, "q_dur": 46, "q_hit": 26, "q_off": 14000, "q_r": 26000, "q_dmg": 60, "q_ad": 70,
    "q_hp": 4, "q_slow": 40, "q_slow_t": 60, "q_stun": 66, "q_stun0": 42,
    # Returning Hammer
    "e_cd": 480, "e_range": 55000, "e_dur": 26, "e_go": 22, "e_speed": 5000, "e_len": 44000, "e_r": 12000,
    "e_dmg": 40, "e_ad": 60, "e_hp": 2, "e_slow": 40, "e_slow_t": 60, "e_wait": 40, "e_catch": 10, "e_sh": 60,
    "e_sh_ad": 50, "e_sh_t": 150,
    # Awakened Thunder Hammer
    "r_cd": 2400, "r_range": 55000, "r_dur": 108, "r_go": 75, "r_off": 24000, "r_r": 44000, "r_dmg": 180, "r_ad": 100,
    "r_hp": 8, "r_up": 90, "r_dr": 45, "r_awake": 480,
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


def magic(dmg, hp):
    """Magic damage from his health (the awakened lightning): ApAttack's attack_ratio is ability power, he has none."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def slow(name, pct, tick):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}},
                                              "move_speed_mult": -pct}}


def circle(r):
    return {"Circle": {"radius": r}}


def ahead(radius, offset, effects):
    """Every enemy within `radius` of a point `offset` ahead of him (toward the action's target)."""
    return {"type": "RangeEffect", "shape": circle(radius), "target": "EnemyWithoutTower",
            "apply_type": {"Forward": {"offset": offset}}, "effects": list(effects)}


def on_self(*effects):
    """Effects on him alone (a WithSelf would hit the action's target too, champion-data section 4)."""
    return {"type": "RangeEffect", "shape": circle(1000), "target": "AllyOnlySelf", "apply_type": "AroundCaster",
            "effects": list(effects)}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """A Delayed's effects that use the action's target, kept to a living Thor (build_lubu.alive_only)."""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # Mjolnir awakens: the red cracks over the hammer and their sound, the count cleared
    awaken = lambda t: combine(flag("awake", t), cview("p_awake"), sfx("p_awake"), unflag("t1"), unflag("t2"))
    # every third skill cast (not while awake): t1, t2, then the awakening
    if p["p_n"] == 2:       # every second cast
        count = when("awake", combine(), when("t1", awaken(p["p_t"]), flag("t1", None)))
    else:
        count = when("awake", combine(), when("t2", awaken(p["p_t"]),
                                              when("t1", combine(unflag("t1"), flag("t2", None)), flag("t1", None))))

    # ------------------------------------------------------------------ attack: the hammer blow
    zap = when("awake", combine(magic(p["p_dmg"], p["p_hp"]), view("a_zap")), combine())
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), zap, sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Thunder God's Hammer
    struck = [attack(p["q_dmg"], p["q_ad"], p["q_hp"]),
              when("awake", {"type": "Stun", "duration": p["q_stun"]},
                   {"type": "Stun", "duration": p["q_stun0"]} if p["q_stun0"] else slow("q_slow", p["q_slow"],
                                                                                         p["q_slow_t"])),
              view("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(count, sfx("q"), delayed(p["q_hit"] - 1, sfx("q_slam"), ahead(p["q_r"], p["q_off"], struck),
                                                   tsfx("q_hit"))))

    # ------------------------------------------------------------------ skill2: Returning Hammer
    passed = lambda: [{"casting_type": "Targeting", "effect": e} for e in
                      (attack(p["e_dmg"], p["e_ad"], p["e_hp"]), slow("e_slow", p["e_slow"], p["e_slow_t"]),
                       view("e_hit"), tsfx("e_hit"))]
    catch = [{"type": "RemoveCasterAnimation", "name": "skill2_wait"}, anim("skill2_catch", p["e_catch"]), sfx("e_catch"),
             on_self({"type": "Shield", "amount": p["e_sh"], "attack_ratio": p["e_sh_ad"], "ap_ratio": 0,
                      "tick": p["e_sh_t"]})]
    back = {"type": "BackToCasterLinearProjectile", "name": n("e_back"), "penetrate": True,
            "applied_target": "EnemyWithoutTower", "applied_effects": passed(), "end_effects": catch,
            "speed": p["e_speed"], "range": 400000, "shape": circle(p["e_r"])}
    out = {"type": "LinearProjectile", "name": n("e_out"), "penetrate": True, "applied_target": "EnemyWithoutTower",
           "applied_effects": passed(), "end_effects": [sfx("e_turn"), back], "speed": p["e_speed"],
           "range": p["e_len"], "shape": circle(p["e_r"]), "y_offset": -2000}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Direction", "EnemyWithoutTower",
                    combine(count, delayed(p["e_go"] - 1, sfx("e"), anim("skill2_wait", p["e_wait"]), out)))

    # ------------------------------------------------------------------ ult: Awakened Thunder Hammer
    wake = combine(unflag("t1"), unflag("t2"),
                   when("awake", combine(unflag("awake"), flag("awake", p["r_awake"])), awaken(p["r_awake"])))
    guard = flag("r_guard", p["r_go"] + 2, cc_immune=True, damaged_reduce=p["r_dr"])
    blow = ahead(p["r_r"], p["r_off"], [attack(p["r_dmg"], p["r_ad"], p["r_hp"]), {"type": "Airborne", "duration": p["r_up"]},
                                        view("r_hit"), tsfx("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(guard, wake, sfx("r"), sfx("r_vo"), delayed(p["r_go"] - 1, alive_only(sfx("r_slam"), blow))))

    # ------------------------------------------------------------------ views
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    # the swing, the slam's lightning, the charge and the ult's bolt are drawn into his own frames
    # (tools/art/import_thor.py); the flying hammer is the boomerang's picture, turned with its flight (it spins)
    views_e = [E("a_hit", "thunder_hit"), E("a_zap", "thunder_hit", 3), E("q_hit", "thunder_hit"),
               E("e_hit", "thunder_hit"), E("r_hit", "ult_impact"), E("p_awake", "hammer_awakening", 3)]
    views_p = [{"type": "Animated", "name": n(x), "anim": PROJ, "tag": "hammer_flight", "repeat": True, "z": 2}
               for x in ("e_out", "e_back")]
    kit = {
        "id": ID, "category": "Tank" if is_native else "Melee", "tags": ["AD", "Tank", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll (addons/ragnarok/src/thor.rs): his voice lines
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:voice", "params": {}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


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
    ap_.add_argument("--plain", action="store_true", help="for the balance sims: no DLL passive, category Melee")
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
