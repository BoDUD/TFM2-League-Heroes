"""Build tft_sentinel.data_champion (a tft pack hero: the Blue Sentinel, jungle, Melee) from the parameters P.

    python tools/kit/build_sentinel.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Blue Sentinel (苍蓝雕纹魔像) is Teamfight Tactics set 18's 4-cost Rift Monster / Vanguard / Invoker tank
(DA_Sentinel18, range 1, 1300 health, 75 AD, 0.60 attack speed, 60 armour and magic resistance, 60/150 mana): Azure
Shockwave / 蔚蓝冲击波 - a shield (AP + health), then a slam sending a fissure toward the most enemies: knocked up,
magic damage, Mana Reave; Blue Buff: each cast gives its allies mana regeneration. The kit is our own design from that
(the user's pick, 2026-10-31: jungle, plan A 「蔚蓝冲击波」):
  passive Blue Buff (蓝霸符): each of its skills (Q, E, R) puts p_cdm `skill_cooldown_mult` on every other allied champion
          within p_r for p_t ticks (the engine's refund: each one's remaining skill cooldowns capped at once to
          100 / (100 + p_cdm) of its cooltime) and the blue glow (p_blue) for p_glow ticks. Data alone.
  attack  Rock Fist (岩拳猛击) on `Enemy` (towers too): 100% AD at atk_st.
  skill   Twin Slam (双拳重砸), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): both fists into the
          ground at q_st: every enemy within q_r takes q_dmg + q_ap% AP + q_hp% of its maximum health as magic damage
          and is q_slow% slower for q_slow_t ticks.
  skill2  Carved Skin (雕纹石肤), `Targeting` on `EnemyWithoutTower` (e_range): its runes flare: a shield of e_sh +
          e_ap% AP for e_sh_t ticks and every enemy within e_r taunted e_taunt ticks.
  ult     Azure Shockwave (蔚蓝冲击波, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): a shield of r_sh +
          r_ap% AP for r_sh_t ticks and no crowd control until the slam; at r_st both fists smash the ground and a
          fissure runs r_len toward the MOST ENEMY CHAMPIONS (`tft_sentinel:fissure`, tft.dll: a penetrating line r_w
          wide either side, r_speed a tick): every enemy it reaches takes r_dmg + r_ratio% AP + r_hp% of its maximum
          health as magic damage and is knocked up r_up ticks; a champion is Mana Reaved - its next skill to come ready
          (within r_mark ticks) is sealed r_reave ticks (TFT raises the next cast's mana; the engine can only shorten a
          cooldown, so the next cast waits instead). --plain: a `LineRangeProjectile` toward the AI's target, the same
          damage and knock-up, and BlockSkill r_reave at once.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/sentinel.rs; the passive is
tft_sentinel:golem, params NATIVE_KEYS): the data can neither pick a direction by who stands where nor wait for a
skill to come ready. A build of P checks sentinel.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_sentinel"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 26000 (the huge fists); radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips are rigged (tools/art/rig_sentinel.py). Stats start from the pack's jungle tanks
# (tft_krug hp 1200 +118 / atk 80 / def 38, league_rammus, league_sejuani): the 4-cost stone golem, slow and heavy,
# its skills magic.
# Numbers = the 10-min classic-SDK simulations (C:/t/bg_sim with C:/t/al_sim/kd.py: jungle lane 1 against the base
# ninja, demon, hunter, werewolf and vampire, three lineups, both sides; 2026-10-31), all --plain (the fissure a line
# at the AI's target, the reave a silence at once): the draft (atk 70, Q 60 + 80% AP + 3%, R 120 + 140% + 4%) +0.93 on
# seeds 1-8 against tft_krug --plain +2.06 - too little damage (4800 dealt to Krug's 6200); atk 76, Q 80 + 100% + 4%,
# R 160 + 160% +1.66; atk 78, Q 90 + 110% + 5% every 6 s, R 180 + 180%, taunt 1.25 s +3.31; between the two (atk 77,
# Q 85 + 105% + 4% every 6.5 s, R 170 + 170%, taunt 70 ticks; then 72 = 1.2 s for the text) +2.20 / +3.00 on seeds 1-8 / 9-16 (tft_krug +2.06 /
# +1.89) = P: the 4-cost a little above the 3-cost jungle tank.
P = {
    # stats (Melee, a jungle tank with magic skills)
    "hp": 1250, "hp_g": 120, "atk": 77, "atk_g": 11, "apw": 40, "apw_g": 14, "def": 40, "def_g": 8, "mr": 36, "mr_g": 6,
    "ms": 950, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 36, "atk_cd": 76, "atk_st": 18,
    # passive Blue Buff (TFT: allies' mana regeneration on each cast)
    "p_r": 50000, "p_cdm": 50, "p_t": 3, "p_glow": 60,
    # Twin Slam
    "q_cd": 390, "q_range": 30000, "q_dur": 34, "q_st": 16, "q_r": 34000, "q_dmg": 85, "q_ap": 105, "q_hp": 4,
    "q_slow": 30, "q_slow_t": 120,
    # Carved Skin
    "e_cd": 600, "e_range": 30000, "e_dur": 30, "e_st": 10, "e_sh": 120, "e_ap": 120, "e_sh_t": 240, "e_r": 30000,
    "e_taunt": 72,
    # Azure Shockwave (TFT: a shield, the fissure toward the most enemies, knock-up, magic damage, Mana Reave)
    "r_cd": 3000, "r_range": 60000, "r_dur": 48, "r_st": 24, "r_sh": 150, "r_ap": 120, "r_sh_t": 240,
    "r_len": 100000, "r_w": 16000, "r_speed": 5000, "r_dmg": 170, "r_ratio": 170, "r_hp": 4, "r_up": 50,
    "r_mark": 900, "r_reave": 120,
}
# what tft.dll reads from passive.params (addons/tft/src/sentinel.rs)
NATIVE_KEYS = ("r_len", "r_w", "r_speed", "r_dmg", "r_ratio", "r_hp", "r_up", "r_mark", "r_reave")
# names sentinel.rs uses that need no view: sounds (the death crumble, the fissure's hit, the reave)
NATIVE_ONLY = {"d", "r_reave"}


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


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


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


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on it alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def blue(p):
    """Blue Buff: the other allied champions round it get their skills' cooldowns cut (the refund) and the glow."""
    return combine(sfx("p"), around(p["p_r"], "AllyNotSelf", [buff("p_cd", p["p_t"], skill_cooldown_mult=p["p_cdm"]),
                                                            buff("p_blue", p["p_glow"])]))


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: Rock Fist
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Twin Slam
    slammed = [magic(p["q_dmg"], p["q_ap"], p["q_hp"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"])]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), blue(p),
                           delayed(p["q_st"] - 1, sfx("q_hit"), cview("q_hit"),
                                   around(p["q_r"], "EnemyWithoutTower", slammed))))

    # ------------------------------------------------------------------ skill2: Carved Skin
    taunted = [{"type": "Taunt", "duration": p["e_taunt"]}, buff("e_taunt", p["e_taunt"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), blue(p), cview("e_cast"),
                            delayed(p["e_st"] - 1, sfx("e_taunt"), on_me(shield(p["e_sh"], p["e_ap"], p["e_sh_t"])),
                                    flag("e_shield", p["e_sh_t"]), around(p["e_r"], "EnemyWithoutTower", taunted))))

    # ------------------------------------------------------------------ ult: Azure Shockwave
    if is_native:   # tft.dll: the fissure toward the most enemy champions, its hits and the Mana Reave
        fissure = native("fissure")
    else:           # --plain: a line toward the AI's target, the reave a silence at once
        hit = [magic(p["r_dmg"], p["r_ratio"], p["r_hp"]), {"type": "Airborne", "duration": p["r_up"]},
               {"type": "BlockSkill", "tick": p["r_reave"]}, view("r_hit")]
        line = {"type": "LineRangeProjectile", "name": n("r_line"), "width": p["r_w"], "length": p["r_len"],
                "delay": 2, "apply": 1, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in hit]}
        # the running fissure's picture: a view-only line along it on the ground (y_offset 5000: it leaves 5000 -
        # y_offset north of its pivot, champion-data.md), the hits all at once on the line's apply
        crack = {"type": "LinearProjectile", "name": n("r_crack"), "penetrate": True,
                 "applied_target": "EnemyWithoutTower", "applied_effects": [], "end_effects": [],
                 "speed": p["r_speed"], "range": p["r_len"], "shape": circle(1000), "y_offset": 5000}
        fissure = combine(crack, line)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r_vo"), sfx("r"), sfx("r_shield"), blue(p),
                         on_me(shield(p["r_sh"], p["r_ap"], p["r_sh_t"])), flag("r_shield", p["r_sh_t"]),
                         flag("r_rise", p["r_st"], cc_immune=True),
                         delayed(p["r_st"] - 1, cview("r_slam"), sfx("r_crack"), fissure)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the slams' rings lie on the ground where it struck (z -1, not following); the rune flare and the shells ride it;
    # the ult's shield is the Carved Skin's shell (tag e_shield)
    views_e = [E("a_hit"), E("q_hit", BIG, -1, False), E("e_cast", BIG, 3), E("r_slam", BIG, -1, False)]
    views_b = [B_("p_blue"), B_("q_slow"), B_("e_shield", BIG), B_("r_shield", BIG, 3, "e_shield"), B_("e_taunt", FX, 4)]
    views_p = [B_("r_crack", BIG, 1)]   # tft.dll's fissure (a projectile it spawns), or --plain's picture line
    if is_native:   # the buffs tft.dll gives
        views_b += [B_("r_hit"), B_("r_reave", FX, 4), B_("r_seal", FX, 4)]
    else:
        views_e += [E("r_hit", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AP", "Melee", "Tank", "CC", "Shield"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/sentinel.rs): the fissure and the Mana Reave
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:golem", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Azure Shockwave as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's
    add-on bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll (the user,
    2026-10-27: 「塞拉斯的大招什么一定要能偷到特效版本的」). The kit's --plain ult: the shield, the smash, the fissure's
    picture and its line toward his target, the knock-up, the magic damage and the silence. The views are the kit's own
    (tft_sentinel_*); make_override copies them and their sheets."""
    p = dict(P) if p is None else p
    return build(p, False)["ult"]["effect"]


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def names(o):
    """Every `name` in a tree: the buffs, flags, pictures and sounds the kit sets or plays."""
    if isinstance(o, dict):
        return ({o["name"]} if isinstance(o.get("name"), str) else set()).union(*(names(v) for v in o.values()))
    if isinstance(o, list):
        return set().union(*(names(v) for v in o))
    return set()


def check_dll(p, kit):
    """addons/tft/src/sentinel.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback) and every name it plays or puts on (`sn("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "sentinel.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"sentinel.rs Params::default() differs from P (sentinel.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sn\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"sentinel.rs plays or puts on names the kit does not have: {missing}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no tft.dll calls (for the balance sims)")
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
    if not a.set and not a.params:
        check_dll(p, build(p, True))
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
