"""Build league_sion.data_champion (top, Melee AD tank / fighter) from the parameters P.

    python tools/kit/build_sion.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-14: top / melee AD tank-fighter; Q as skill, E Roar of the Slayer with W Soul Furnace
after it as skill2, R a charge at a far champion, W's kill stacks in the main pack and Glory in Death's revive in the
native add-on addons/league_sion):
  passive Soul Furnace's stacks (灵魂熔炉, W's passive): a unit his attack kills gives him k_hp maximum health for good
          (League: +4 a minion, +15 a champion or large monster; a kill check after league_olaf's - the attack's own
          last hits only, every unit the same; buffs end with his death, so the stacks build again each life).
          Glory in Death (死亡荣耀): League's zombie revive needs his health read - the add-on (native=1) does it.
  attack  The axe, the hit on tick atk_st.
  skill   Q Decimating Smash (残虐猛击): a `Position` cast on `EnemyWithoutTower` (q_range, waves and camps too). He
          charges q_ch ticks in place (the axe raised, a line on the ground in front of him, q_len long, half-width
          q_w); crowd control on him (checked every q_brk ticks) breaks it. Then the slam: every enemy on the line takes
          q_dmg + q_ratio% AD and is knocked up q_up ticks (League: a full charge knocks up and stuns 1.25-1.75 s).
  skill2  E Roar of the Slayer (杀手怒吼) and W Soul Furnace (灵魂熔炉) share the slot, each on its own cooldown (caster
          flags e_cd and w_cd; the slot waits only s2_cd). A `Direction` cast on `EnemyWithoutTower` (e_range):
          - E ready: the roar flies e_len (`LinearProjectile`, through minions as League's knocked-back minion does):
            every enemy hit takes e_dmg + e_hp% of his maximum health as magic damage, is slowed e_slow% for e_slow_t
            and loses e_shred% armour for e_shred_t ticks;
          - else W ready and an enemy champion within w_trig: a shield of w_sh + w_ad% AD for w_t ticks; still holding
            any of it after w_det ticks, it blasts: every enemy within w_r takes w_dmg + w_hp% of his maximum health as
            magic damage (League: 40-140 + 14% max health after 3 s, the shield 6 s).
  ult     R Unstoppable Onslaught (蛮横冲撞): a `Targeting` cast on `EnemyChampion` (r_range): immune to crowd control he
          charges (`RushTime`, r_speed a tick for at most r_tick ticks) and stops on the first enemy champion: the
          longer he ran, the harder it hits - two caster flags laid at the start (r_d1 for r_b1 ticks, r_d2 for r_b2,
          league_xerath E's way) pick r_dmg1 / r_dmg2 / r_dmg3 + r_ratio% AD and a knock-up of r_up1 / r_up2 / r_up3
          ticks; every enemy within r_r of him is slowed r_slow% for r_slow_t (League: 150-450 -> 400-1200 by distance,
          0.75-1.75 s knock-up).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_sion.data_champion")
ID = "league_sion"
FX = "asset/league/effects/league_sion_fx"
BIG = "asset/league/effects/league_sion_big"

# Timings from the frames (tools/art/rig_sion.py MS): the axe chop 410 ms, the blade down on frame 4 (210 ms, tick 13);
# Q's charge 670 ms (skill_charge), the slam 400 ms with the axe on the ground on frame 3 (120 ms, tick 7); E 410 ms, the
# roar on frame 3 (130 ms, tick 8); W 390 ms; R's charge 8 x 104 ms (50 ticks), the crash 420 ms.
P = {
    # stats (the pack's AD tanks top: league_darius hp 1080 +105, atk 90 +18, def 34 +8, mr 26 +4; league_garen 1100
    # +110, 88 +17; league_malphite 1100 +120): League's Sion 655 +87 hp, 68 AD, 36 armour +4.2, 32 mr +2.05, 345 move,
    # 175 range - the tankiest of them, a slow axe
    "hp": 1250, "hp_g": 125, "atk": 88, "atk_g": 16, "mp": 0, "mp_g": 0, "def": 36, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 980, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 25, "atk_cd": 64, "atk_st": 13,
    # Soul Furnace stacks (League: +4 hp a minion, +15 a champion / large monster); the add-on's own: every kill,
    # k_u a unit, k_c a champion, kept through death
    "k_hp": 6, "k_u": 4, "k_c": 15,
    # Glory in Death, the add-on's zombie (League: ~9 s, attack speed up, 100% life steal, no abilities)
    "z_t": 540, "z_as": 60, "z_vamp": 100,
    # Q Decimating Smash (League: cd 11-6 s, up to 2 s charge, 30-110 + 45-75% AD -> 90-330 + 135-225% AD, cone 720)
    "q_cd": 420, "q_range": 34000, "q_ch": 40, "q_brk": 10, "q_rel": 24, "q_hit": 7, "q_len": 50000, "q_w": 10000,
    "q_dmg": 140, "q_ratio": 180, "q_up": 50,
    # skill2 slot: E Roar of the Slayer + W Soul Furnace
    "s2_cd": 60,
    # E (League: 800 line, 65-205 + 55% AP magic, slow 40-60% 2.5 s, armour -20% 4 s, cd 13-8 s)
    "e_cd": 480, "e_range": 50000, "e_dur": 25, "e_at": 8, "e_speed": 3000, "e_len": 52000, "e_rad": 6000,
    "e_dmg": 120, "e_hp": 4, "e_slow": 40, "e_slow_t": 120, "e_shred": 20, "e_shred_t": 240,
    # W (League: shield 60-120 + 8-16% max hp 6 s, blast after 3 s: 40-140 + 14% max hp magic r 400, cd 15-11 s)
    "w_cd": 720, "w_trig": 26000, "w_anim": 23, "w_sh": 160, "w_ad": 100, "w_t": 360, "w_det": 180, "w_r": 26000,
    "w_dmg": 80, "w_hp": 8,
    # R Unstoppable Onslaught (League: 150-450 + 40% bonus AD -> 400-1200 + 80%, knock-up 0.75-1.75 s, slow, cd 140-60 s)
    "r_cd": 3600, "r_range": 90000, "r_speed": 2400, "r_tick": 50, "r_b1": 16, "r_b2": 32, "r_hitanim": 25,
    "r_dmg1": 200, "r_dmg2": 300, "r_dmg3": 400, "r_ratio": 100, "r_up1": 45, "r_up2": 70, "r_up3": 95,
    "r_r": 24000, "r_slow": 40, "r_slow_t": 150,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_sion: its passive brings him back as Glory in Death's zombie
    "native": 0,
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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, proj=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": proj,
            "effects": [e for e in effects if e is not None]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, fly, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": fly, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, apply, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": apply, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def pzone(name, r, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(r), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def rush(speed, tick, target, effects):
    return {"type": "RushTime", "speed": speed, "tick": tick, "range": 12000, "casting_target": target,
            "penetrate": False, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def magic_hp(dmg, hp):
    """Magic damage of dmg + hp% of HIS maximum health (hp_ratio is the caster's)."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def ad_shield(amount, ad, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ad, "ap_ratio": 0, "tick": tick}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def band(name, width, length, delay, apply, target, effects):
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def kill_check(src, reward):
    """On a hit unit, around its damage: the flag before, the living target's clear after, the read on him later
    (league_jinx Get Excited! through league_olaf; a dead target's `Delayed` adds nothing, so the flag stays). Inside the
    attack's own `Delayed` the casted clear must wait a tick (straight away it ran on the dying minion too: no kill
    found in a 600 s game; a tick later 25, the read at 6), as league_jinx R's."""
    k = f"k_{src}"
    return (combine(*rm(k), flag(k, 40)),
            combine(delayed(1, casted(3, 1, *rm(k))), on_me(delayed(6, sw(k, combine(*rm(k), reward))))))


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ attack (+ Soul Furnace's kill stacks)
    k_set, k_read = kill_check("a", combine(flag("k_hp", None, hp=p["k_hp"]), cview("k_soul")))
    if native:  # the add-on counts every kill itself (league_sion:glory on_kill)
        k_set = k_read = None
    chop = combine(sfx("a_swing"), delayed(p["atk_st"] - 1, k_set, attack(0, 100), view("a_hit"), tsfx("a_hit"),
                                           k_read))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", chop,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Decimating Smash
    breaks = [delayed(t, pick(1, "AllyChampionInCC", *rm("q_ch"))) for t in range(p["q_brk"], p["q_ch"], p["q_brk"])]
    slam = combine(*rm("q_ch"), anim("skill", p["q_rel"]),
                   delayed(p["q_hit"], sfx("q_hit"),
                           band("q_slam", p["q_w"], p["q_len"], 31, 1, "EnemyWithoutTower",
                                [attack(p["q_dmg"], p["q_ratio"]), {"type": "Airborne", "duration": p["q_up"]},
                                 view("q_hit")])))
    skill = action("skill", p["q_ch"] + p["q_rel"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(anim("skill_charge", p["q_ch"]), sfx("q"), voice("vo_q", p), refresh("q_ch", p["q_ch"] + 2),
                           band("q_warn", p["q_w"], p["q_len"], p["q_ch"] + p["q_hit"] + 2, p["q_ch"] + p["q_hit"] + 2,
                                "EnemyChampion", []),
                           *breaks, delayed(p["q_ch"], sw("q_ch", slam))))

    # ------------------------------------------------------------------ skill2: E Roar of the Slayer / W Soul Furnace
    roar_hits = [magic_hp(p["e_dmg"], p["e_hp"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                 buff("e_shred", p["e_shred_t"], defence_mult=-p["e_shred"]), view("e_hit"), tsfx("e_hit")]
    roar = combine(flag("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                   delayed(p["e_at"], line("e_roar", p["e_speed"], p["e_len"], p["e_rad"], "EnemyWithoutTower", True,
                                           roar_hits)))
    blast = combine(*rm("w_sh"), cview("w_burst"), sfx("w_hit"),
                    around(p["w_r"], "EnemyWithoutTower", [magic_hp(p["w_dmg"], p["w_hp"]), view("w_hit")]))
    furnace = combine(flag("w_cd", p["w_cd"]), anim("skill2_w", p["w_anim"]), sfx("w"), voice("vo_w", p),
                      on_me(ad_shield(p["w_sh"], p["w_ad"], p["w_t"]), *rm("w_sh"),
                            {"type": "AddCasterBuff", "buff_state": {"name": n("w_sh"), "duration": "WithShield"},
                             "only_to_enemy": False}),
                      delayed(p["w_det"], sw("w_sh", blast)))
    near = combine(*rm("w_near"), pick(p["w_trig"], "EnemyChampion", flag("w_near", 1)))
    w_try = sw("w_cd", NONE, combine(near, sw("w_near", combine(*rm("w_near"), furnace))))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Direction", "EnemyWithoutTower",
                    sw("e_cd", w_try, roar), key="skill2")

    # ------------------------------------------------------------------ ult: R Unstoppable Onslaught
    def crash(dmg, up):
        return combine(attack(dmg, p["r_ratio"]), {"type": "Airborne", "duration": up})

    r_hits = [sw("r_d1", crash(p["r_dmg1"], p["r_up1"]), sw("r_d2", crash(p["r_dmg2"], p["r_up2"]),
                                                            crash(p["r_dmg3"], p["r_up3"]))),
              view("r_hit"), tsfx("r_hit"),
              on_me(*rm("r_go", "r_d1", "r_d2"), anim("ult_hit", p["r_hitanim"]), cview("r_crash")),
              around(p["r_r"], "EnemyWithoutTower", [buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"])])]
    ult = action("ult", p["r_tick"] + p["r_hitanim"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(refresh("r_go", p["r_tick"] + 2, cc_immune=True), flag("r_d1", p["r_b1"]),
                         flag("r_d2", p["r_b2"]), anim("ult", p["r_tick"]), sfx("r"), voice("vo_r", p),
                         rush(p["r_speed"], p["r_tick"], "EnemyChampion", r_hits),
                         delayed(p["r_tick"] + 1, *rm("r_go", "r_d1", "r_d2"))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # Q's line while he charges (looped) and its smash cracking along it once (its band lasts the picture's 500 ms;
    # it hits on its first tick all the same), both on the ground
    views_p = [P_("e_roar"), P_("q_warn", BIG, -1),
               {"type": "Animated", "name": n("q_slam"), "anim": BIG, "tag": "q_slam", "repeat": False, "z": -1}]
    views_e = [E("a_hit"), E("k_soul", FX, 3), E("q_hit"), E("e_hit"), E("w_burst", BIG, 2, False), E("w_hit"),
               E("r_hit"), E("r_crash", BIG, 2, False)]
    # the shield and the zombie's fire round him over him (their middles bare), the charge's glow under him
    views_b = [B_("w_sh", BIG, 3), B_("r_go", BIG, -1), B_("e_shred", FX, 3), B_("p_zombie", BIG, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_sion:glory",
                          "params": {k: p[k] for k in ("k_u", "k_c", "z_t", "z_as", "z_vamp")}}
    return kit


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
