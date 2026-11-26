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
  skill   Thor's Hammer (斗神之雷槌), `Targeting` on `EnemyWithoutTower` (q_range): the hammer comes down on q_hit;
          the ground lightning hits every enemy within q_r of a point q_off in front of him: q_dmg + q_ad% AD + q_hp% of
          his max health, stunned q_stun0 ticks (awake: q_stun; a q_stun0 of 0 slows q_slow% for q_slow_t instead).
  skill2  Járngreipr (铁手套): 2026-11-26 照原作改（用户：「我需要的是完美的还原度」）。原作第一回合：雷神的铁手套
          Járngreipr 是「天界最强的防御」（真正的用处是压住他的握力，免得捏碎没觉醒的雷槌），吕布的方天戟正面打碎了右手套，雷槌
          这时才觉醒。Codex 补画的格挡（assets/source/thor/fidelity，0.82 秒）：`Targeting` on `EnemyWithoutTower`
          (e_range)，第 4 帧 e_on 到第 7 帧 e_off 双臂的铁手套顶在身前——普攻全挡（base_attack_damaged_reduce 100）、
          受到的技能伤害降低 e_dr%；举起来的时候拿到 e_sh + e_sh_ad% AD 的护盾 e_sh_t ticks。算雷槌觉醒的一次。
  ult     Awakened Thunder Hammer (覚醒雷槌 / ゲイルロズトールハンマー), `Targeting` on `EnemyChampion` (r_range): 原作是把觉醒的
          雷槌扔出去、飞出场外像回旋镖一样回来、接住，把速度和离心力变成一击（第一次打断了吕布的双腿）。原来 E 的扔锤搬过来：
          雷槌立即觉醒 r_awake ticks；r_go 扔出（league_sivir 的 Q：LinearProjectile 的终点放 BackToCasterLinearProjectile），
          来回穿过的敌人受到 r_pdmg + r_pad% AD + r_php% 最大生命、减速 r_slow% r_slow_t ticks；锤子飞着的时候空着手
          （`ult_wait`，CasterAnimation 一直放到锤子回来），真飞回来才接住（`ult_catch`，回程的 end_effects，不按时间放），
          接住 r_catch ticks 后举锤过头（`ult_slam`，原来大招举过头顶起的后半段），再过 r_hit ticks 砸下：前方 r_off 处 r_r
          以内的敌人受到 r_dmg + r_ad% AD + r_hp% 最大生命并被击飞 r_up ticks。整个大招 r_dur ticks 不受控制、受到的伤害降低
          r_dr%。砸下前死了就不砸（alive_only）。

Timings are the frames' (Codex's asset_manifest_v01.json presentation_events, 60 ticks a second): the attack's blow on
frame 4 (0.42 s), the throw on frame 3 (0.36 s: r_go 22); the slam's frame 4 is drawn at 0.62 s and played at 0.43 s
(q_hit 26, tools/art/import_thor.py RETIME); the guard's frames 4-7 at 0.29-0.59 s (e_on 17, e_off 35; Codex's
frames.json guard_window / guard_end); ult_slam's blow 0.18 s after it starts (r_hit 11), the catch 0.12 s (r_catch 7).

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
# 2026-11-26 照原作改（E 铁手套格挡、R 扔锤飞回接住砸下）以后重新调：初版 -0.39；E 的护盾和减伤、
# Q 和 R 的伤害、血量都加一档 +0.28，再把 Q 冷却缩到 5 秒（这份 P）+1.07，和改之前（+1.09）一样。
P = {
    # stats (Tank, top): the base tanks' (atk 80 +6, hp 1100 +120, def 40 +10, mr 30 +5), a god a little more
    "hp": 1300, "hp_g": 120, "atk": 84, "atk_g": 12, "apw": 0, "apw_g": 0, "def": 40, "def_g": 9, "mr": 30,
    "mr_g": 5, "ms": 990, "ms_g": 10,
    "atk_range": 27000, "atk_dur": 36, "atk_cd": 76, "atk_st": 24,
    # passive Mjolnir Awakening
    "p_t": 360, "p_dmg": 25, "p_hp": 3, "p_n": 3,
    # Thunder God's Hammer
    "q_cd": 300, "q_range": 30000, "q_dur": 46, "q_hit": 26, "q_off": 14000, "q_r": 26000, "q_dmg": 75, "q_ad": 85,
    "q_hp": 4, "q_slow": 40, "q_slow_t": 60, "q_stun": 66, "q_stun0": 42,
    # Járngreipr（铁手套格挡）
    "e_cd": 420, "e_range": 32000, "e_dur": 49, "e_on": 17, "e_off": 35, "e_dr": 70, "e_sh": 140, "e_sh_ad": 90,
    "e_sh_t": 150,
    # Awakened Thunder Hammer（扔出、飞回、接住、砸下）
    "r_cd": 2400, "r_range": 55000, "r_dur": 94, "r_go": 22, "r_speed": 5000, "r_len": 44000, "r_rr": 12000,
    "r_pdmg": 60, "r_pad": 80, "r_php": 2, "r_slow": 40, "r_slow_t": 60, "r_wait": 60, "r_catch": 7, "r_slam": 46,
    "r_hit": 11, "r_off": 24000, "r_r": 44000, "r_dmg": 220, "r_ad": 100, "r_hp": 8, "r_up": 90, "r_dr": 45,
    "r_awake": 480,
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

    # ------------------------------------------------------------------ skill: Thor's Hammer (闘神の雷槌): the shockwave throws
    # them up (the first round: it blew the sand away and knocked the watchers flying), q_stun0 / q_stun ticks in the air
    struck = [attack(p["q_dmg"], p["q_ad"], p["q_hp"]),
              when("awake", {"type": "Airborne", "duration": p["q_stun"]},
                   {"type": "Airborne", "duration": p["q_stun0"]} if p["q_stun0"] else slow("q_slow", p["q_slow"],
                                                                                         p["q_slow_t"])),
              view("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(count, sfx("q"), delayed(p["q_hit"] - 1, sfx("q_slam"), ahead(p["q_r"], p["q_off"], struck),
                                                   tsfx("q_hit"))))

    # ------------------------------------------------------------------ skill2: Járngreipr（铁手套格挡）
    # 第 4 帧到第 7 帧双臂的铁手套顶在身前：普攻全挡、技能伤害减 e_dr%；举起来就拿到护盾
    guard_e = flag("e_guard", p["e_off"] - p["e_on"], base_attack_damaged_reduce=100, damaged_reduce=p["e_dr"])
    shield_e = on_self({"type": "Shield", "amount": p["e_sh"], "attack_ratio": p["e_sh_ad"], "ap_ratio": 0,
                        "tick": p["e_sh_t"]})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(count, sfx("e"), delayed(p["e_on"] - 1, guard_e, shield_e, sfx("e_block"))))

    # ------------------------------------------------------------------ ult: Awakened Thunder Hammer（覚醒雷槌）
    wake = combine(unflag("t1"), unflag("t2"),
                   when("awake", combine(unflag("awake"), flag("awake", p["r_awake"])), awaken(p["r_awake"])))
    guard = flag("r_guard", p["r_dur"] + 2, cc_immune=True, damaged_reduce=p["r_dr"])
    passed = lambda: [{"casting_type": "Targeting", "effect": e} for e in
                      (attack(p["r_pdmg"], p["r_pad"], p["r_php"]), slow("r_slow", p["r_slow"], p["r_slow_t"]),
                       view("r_pass"), tsfx("r_pass"))]
    blow = ahead(p["r_r"], p["r_off"], [attack(p["r_dmg"], p["r_ad"], p["r_hp"]), {"type": "Airborne", "duration": p["r_up"]},
                                        view("r_hit"), tsfx("r_hit")])
    # 接住：空手的动作停掉，接锤 r_catch ticks，再举锤过头 r_hit ticks 后砸下
    catch = [{"type": "RemoveCasterAnimation", "name": "ult_wait"}, anim("ult_catch", p["r_catch"]), sfx("r_catch"),
             delayed(p["r_catch"], anim("ult_slam", p["r_slam"]),
                     delayed(p["r_hit"] - 1, alive_only(sfx("r_slam"), blow)))]
    back = {"type": "BackToCasterLinearProjectile", "name": n("r_back"), "penetrate": True,
            "applied_target": "EnemyWithoutTower", "applied_effects": passed(), "end_effects": catch,
            "speed": p["r_speed"], "range": 400000, "shape": circle(p["r_rr"])}
    out = {"type": "LinearProjectile", "name": n("r_out"), "penetrate": True, "applied_target": "EnemyWithoutTower",
           "applied_effects": passed(), "end_effects": [sfx("r_turn"), back], "speed": p["r_speed"],
           "range": p["r_len"], "shape": circle(p["r_rr"]), "y_offset": -2000}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(guard, wake, sfx("r"), sfx("r_vo"),
                         delayed(p["r_go"] - 1, sfx("r_throw"), anim("ult_wait", p["r_wait"]), out)))

    # ------------------------------------------------------------------ views
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    # the swing, the slam's lightning, the charge and the ult's bolt are drawn into his own frames
    # (tools/art/import_thor.py); the flying hammer is the boomerang's picture, turned with its flight (it spins)
    views_e = [E("a_hit", "thunder_hit"), E("a_zap", "thunder_hit", 3), E("q_hit", "thunder_hit"),
               E("r_pass", "thunder_hit"), E("r_hit", "ult_impact"), E("p_awake", "hammer_awakening", 3)]
    views_p = [{"type": "Animated", "name": n(x), "anim": PROJ, "tag": "hammer_flight", "repeat": True, "z": 2}
               for x in ("r_out", "r_back")]
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
