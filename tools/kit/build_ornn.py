"""Build league_ornn.data_champion (top, Melee, tank) from the parameters P.

    python tools/kit/build_ornn.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-21: top, plan A - Q / E / R, W in the attack -, the add-on league_ornn, 「有连招要做连招」).
TFM2 has three active slots for League's four buttons; League's forge (buying and upgrading items) cannot be built, so
the passive keeps Living Forge's stats and Brittle:
  passive Living Forge (活体熔炉): +p_def% armour and MR, +p_hp% health (a permanent buff his actions put back after a
          death). Brittle (脆弱): W, E's pillar quake and both of R's rams make enemy champions Brittle for br_t ticks (a
          picture on them) and flag him (`brittle`); his next attack on a champion breaks it: br_hp% of the target's
          max health as true damage (`FixedAttack`: magic has no max-health field), a short knock-back and knock-up.
          The main pack reads the flag on him (data reads only the caster's buffs); the add-on keeps Brittle on each
          champion.
  W       Bellows Breath (风箱烈息), in the attack (league_sylas's Kingslayer way): with w_cd off and an enemy champion
          within w_go, the attack becomes the breath - w_t ticks unstoppable (`cc_immune`) with a w_sh shield, w_n
          pulses of fire in a cone ahead (w_dmg + w_hp% of his max health magic; champions also w_thp% of their max
          health), the last pulse making champions Brittle.
  skill   Q Volcanic Rupture (火山裂隙), `Position` on `EnemyWithoutTower` (q_range): on q_rel he slams the ground and a
          fissure runs q_len toward the target's spot (q_dmg + q_ratio% AD, slowed q_slow% for q_slow_t ticks); at its end a
          magma pillar rises for q_life ticks (a picture stamped every q_stamp ticks while `q_pillar` holds on him).
  skill2  E Searing Charge (灼热冲撞), `Targeting` on `EnemyWithoutTower` (e_range): he charges onto the target,
          e_dmg + e_hp% of his max health to everyone within e_r of the contact. COMBO Q -> E (League's charge into his
          own pillar): with `q_pillar` up the charge breaks the pillar (its stamps stop) and the quake knocks up
          everyone within e_quake_r for e_up ticks with e_q_dmg + e_q_hp% more, champions made Brittle. The main pack
          cannot see where the pillar stands - the fissure runs through the target's spot, so any charge while the
          pillar stands counts as the charge into it; the add-on's pillar is real terrain, and map walls quake too.
  ult     R Call of the Forge God (熔铸之神的召唤), `Targeting` on `EnemyChampion` (r_range), two stages in one cast
          (COMBO R1 -> R2, League's recast): a hidden line runs r_len past him toward the champion and a fire ram
          charges back from its end to him (`BackToCasterLinearProjectile`): r_dmg + r_hp% of his max health magic, slowed
          r_slow% for r_slow_t ticks, champions made Brittle; he holds the summoning pose until it arrives (r_back
          ticks after the cast), then headbutts it: a second ram runs r_len toward the champion, r2_dmg + r2_hp% and a
          knock-up of r2_up ticks on everyone it passes, champions made Brittle.
The add-on copy (--native, addons/league_ornn) keeps the same tree; its passive league_ornn:forge makes the pillar real
terrain, keeps Brittle per champion and holds E for the pillar (the AI hook).
The timings match the strips (tools/art/rig_ornn.py MS: a frame's start in ticks = ms x 0.06).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_ornn.data_champion")
ID = "league_ornn"
FX = "asset/league/effects/league_ornn_fx"
BIG = "asset/league/effects/league_ornn_big"

# League units x 100 = ours for skill ranges (the pack's melee attack is 25000 against League's 175).
P = {
    "hp": 1100, "hp_g": 115, "atk": 80, "atk_g": 8, "mp": 0, "mp_g": 0, "def": 38, "def_g": 9, "mr": 30, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 72, "atk_st": 14,
    # passive Living Forge (League: +10% bonus armour / MR / health) and Brittle (League: 3 s, 10-18% max health magic
    # and a short knock-back on his next attack, CC +30%)
    "p_def": 10, "p_hp": 6, "br_t": 180, "br_hp": 8, "br_up": 15, "br_kb_speed": 1500, "br_kb_t": 8,
    "br_speed": 6000,
    # the add-on's forge (the user, 2026-10-21: 「有装备系统吧 你可以加强装备属性吧」, picked "himself + allies' masterwork",
    # "+20%, masterwork +35%"): his items' main stats +p_item%, from level p_master_lv (League's 13 of 18; TFM2 has 12)
    # +p_master%, and every allied champion's +p_ally%
    "p_item": 20, "p_master": 35, "p_ally": 10, "p_master_lv": 9,
    # W Bellows Breath (League: 0.75 s unstoppable, 12-20% max health magic over the breath, cd 17-13)
    "w_cd": 720, "w_go": 30000, "w_t": 45, "w_n": 5, "w_gap": 9, "w_first": 6, "w_len": 40000, "w_cone": 700,
    "w_dmg": 10, "w_hp": 1, "w_thp": 2, "w_sh": 120, "w_sh_t": 120,
    # Q Volcanic Rupture (League: 800 range, 20-120 +110% AD, slow 40% 2 s, pillar 4 s, cd 9-5)
    "q_cd": 480, "q_range": 75000, "q_dur": 30, "q_rel": 12, "q_speed": 6000, "q_w": 9000, "q_len": 80000,
    "q_dmg": 50, "q_ratio": 100, "q_slow": 40, "q_slow_t": 120, "q_life": 240, "q_stamp": 15,
    # E Searing Charge (League: 650 range, 80-260 + 40% bonus armour / MR, terrain: knock-up 1 s r 360, cd 16-12)
    "e_cd": 720, "e_range": 55000, "e_speed": 4000, "e_anim": 20, "e_r": 18000, "e_dmg": 60, "e_hp": 4,
    "e_quake_r": 30000, "e_up": 60, "e_q_dmg": 40, "e_q_hp": 3, "e_hit_t": 14,
    # R Call of the Forge God (League: 2500 range, 125-225 +20% AP, slow 40-80%, recast: knock-up 1 s, again the
    # damage; cd 140-100); the rams' half width r_w 12000 -> 18000 (the user, 2026-10-21: 「R的羊的效果范围和效果都要做大点」)
    "r_cd": 3000, "r_range": 90000, "r_rel": 12, "r_len": 110000, "r_out": 40000, "r_speed": 2500, "r_w": 18000,
    "r_dmg": 120, "r_hp": 3, "r_slow": 50, "r_slow_t": 90, "r_butt_t": 24, "r_butt_rel": 8, "r2_speed": 3000,
    "r2_dmg": 120, "r2_hp": 3, "r2_up": 60,
    "vo_gap": 600,
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
    return {"type": "Combine", "effects": list(effects)}


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


def attack(dmg, ratio, hp=0):
    """Physical: dmg + ratio% AD + hp% of HIS max health."""
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, hp):
    """Magic: dmg + hp% of his max health (he has no ability power; League's AP ratios become health, the tank stat)."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": hp, "can_crit": False}


def true_max(thp):
    """True damage: thp% of the TARGET's max health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(radius, cone, target, effects):
    """A cone ahead of him toward the action's target (league_darius E's Forward DirDot)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cone}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once. For effects that use no target, point or direction."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def alive_aimed(*effects):
    """The same guard for effects that use the action's target (a line toward it): the effects themselves as the
    flag's branch, a copy inside the search as the other branch so the AI still reads them (champion-data section 5)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)),
                   sw("lives", combine(*effects), pick(1, "AllyOnlySelf", *effects)), *rm("lives"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=(), y=5000):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, radius, target, effects, end=()):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": 400000,
            "penetrate": True, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def build(p):
    nat = bool(p["native"])
    # ------------------------------------------------------------------ passive Living Forge + Brittle
    # (the add-on's forge scales his items instead: league_ornn:forge)
    forge = NONE if nat else sw("forge", NONE, flag("forge", None, defence_mult=p["p_def"],
                                                    magic_resistance_mult=p["p_def"], hp_mult=p["p_hp"]))
    # Brittle on an enemy champion: its picture on him (by name) and the flag on Ornn his next attack reads
    brittle = [buff("brittle", p["br_t"]), tsfx("br"), on_me(refresh("brittle", p["br_t"]))]
    # the break: a champion-only twin of the attack's blow (it only lands when the attack's target is a champion)
    shatter = homing("br_pop", "EnemyChampion", [
        true_max(p["br_hp"]), {"type": "Knockback", "speed": p["br_kb_speed"], "tick": p["br_kb_t"]},
        {"type": "Airborne", "duration": p["br_up"]}, view("br_pop"), tsfx("br_pop"), on_me(*rm("brittle"))],
        p["br_speed"])

    # ------------------------------------------------------------------ W Bellows Breath (the attack's other form)
    def pulse(k):
        last = k == p["w_n"] - 1
        champs = [true_max(p["w_thp"]), *(brittle if last else [])]
        return delayed(p["w_first"] + k * p["w_gap"], alive_aimed(
            ahead(p["w_len"], p["w_cone"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_hp"]), view("w_hit"), tsfx("w_hit")]),
            ahead(p["w_len"], p["w_cone"], "EnemyChampion", champs)))
    # (the fire itself is drawn into his skill_w frames: tools/art/rig_ornn.py, the client never mirrors an effect picture)
    breath = combine(flag("w_cd", p["w_cd"]), anim("skill_w", p["w_t"]), sfx("w"), voice("vo_w", p),
                     on_me(refresh("w_still", p["w_t"], cc_immune=True),
                           {"type": "Shield", "amount": p["w_sh"], "attack_ratio": 0, "ap_ratio": 0,
                            "tick": p["w_sh_t"]},
                           refresh("w_shown", p["w_sh_t"]), delayed(p["w_sh_t"], *rm("w_shown"))),
                     *[pulse(k) for k in range(p["w_n"])])
    # the add-on breaks Brittle on the very champion that carries it (league_ornn:shatter on the attack's target)
    # (its picture and sound a tick later, on the flag br_now the add-on sets when it breaks)
    pop = (combine(native("shatter"), delayed(1, sw("br_now", combine(view("br_pop"), tsfx("br_pop"), *rm("br_now")))))
           if nat else sw("brittle", shatter))
    blow = combine(sfx("a"), attack(0, 100), view("a_hit"), tsfx("a_hit"), pop)
    # the breath when it is ready and an enemy champion is near (a 1-tick flag from the search, read at once)
    w_go = combine(*rm("w_near"), sw("w_cd", NONE, pick(p["w_go"], "EnemyChampion", flag("w_near", 1))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(forge, w_go, sw("w_near", combine(*rm("w_near"), breath), blow)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Volcanic Rupture (the pillar)
    stamps = [delayed(k, sw("q_pillar", view("q_pillar"))) for k in range(p["q_stamp"], p["q_life"], p["q_stamp"])]
    # the add-on's pillar is terrain where the fissure ends (league_ornn:pillar reads that point)
    rise = [view("q_rise"), sfx("q_pillar"), refresh("q_pillar", p["q_life"]), *stamps, *([native("pillar")] if nat else [])]
    fissure = line("q_fissure", p["q_speed"], p["q_len"], p["q_w"], "EnemyWithoutTower", True,
                   [attack(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                    view("q_hit"), tsfx("q_hit")], end=rise, y=0)
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(forge, sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive_aimed(cview("q_slam"), sfx("q_crack"), fissure))))

    # ------------------------------------------------------------------ skill2: E Searing Charge (Q -> E)
    quake = combine(*rm("q_pillar"), cview("e_quake"), sfx("q_break"), sfx("e_up"),
                    around(p["e_quake_r"], "EnemyWithoutTower",
                           [attack(p["e_q_dmg"], 0, p["e_q_hp"]), {"type": "Airborne", "duration": p["e_up"]},
                            view("e_hit")]),
                    around(p["e_quake_r"], "EnemyChampion", brittle))
    contact = [anim("skill2_hit", p["e_hit_t"]), sfx("e_hit"),
               around(p["e_r"], "EnemyWithoutTower", [attack(p["e_dmg"], 0, p["e_hp"]), view("e_hit"), tsfx("e_hit")]),
               # the add-on quakes on a real pillar near the contact or a wall ahead (league_ornn:charge sets e_quake_go)
               *([native("charge"), delayed(1, sw("e_quake_go", quake))] if nat else [sw("q_pillar", quake)])]
    charge = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000, "end_effects": contact}
    skill2 = action("skill2", p["e_anim"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(forge, *([native("from")] if nat else []), sfx("e"), voice("vo_e", p),
                            anim("skill2", p["e_anim"]), charge))

    # ------------------------------------------------------------------ ult: R Call of the Forge God (R1 -> R2)
    ram_hit = [magic(p["r_dmg"], p["r_hp"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
               view("r_hit"), tsfx("r_hit")]
    ram = back("r_ram", p["r_speed"], p["r_w"], "EnemyWithoutTower", ram_hit)
    ram_c = back("r_ram_c", p["r_speed"], p["r_w"], "EnemyChampion", brittle)   # its champion-only twin (Brittle)
    out = line("r_call", p["r_out"], p["r_len"], 1000, "EnemyChampion", True, [], end=[view("r_rise"), ram, ram_c])
    out_t = -(-p["r_len"] // p["r_out"])
    arrive = p["r_rel"] + out_t + -(-p["r_len"] // p["r_speed"])   # the ram reaches him (he stands still meanwhile)
    butt_hit = [magic(p["r2_dmg"], p["r2_hp"]), {"type": "Airborne", "duration": p["r2_up"]}, view("r_hit"),
                tsfx("r2_hit")]
    ram2 = line("r_ram2", p["r2_speed"], p["r_len"], p["r_w"], "EnemyWithoutTower", True, butt_hit, y=0)
    ram2_c = line("r_ram2_c", p["r2_speed"], p["r_len"], p["r_w"], "EnemyChampion", True, brittle, y=0)
    ult = action("ult", p["r_rel"] + 2, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(forge, sfx("r"), voice("vo_r", p), anim("ult", arrive),
                         delayed(p["r_rel"] - 1, alive_aimed(cview("r_call"), sfx("r_run"), out)),
                         delayed(arrive, anim("ult_butt", p["r_butt_t"]), sfx("r2"), voice("vo_r2", p)),
                         delayed(arrive + p["r_butt_rel"], alive_aimed(cview("r_butt"), sfx("r2_butt"), sfx("r2_run"), ram2, ram2_c))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    views_p = [Pj("q_fissure", BIG), Pj("r_ram", BIG), Pj("r_ram2", BIG)]
    views_e = [E("a_hit"), E("br_pop"), E("w_hit"), E("q_slam", BIG, -1),
               E("q_hit"), E("q_rise", BIG, 1, False), E("q_pillar", BIG, 1, False), E("e_quake", BIG, -1),
               E("e_hit"), E("r_call", BIG, -1), E("r_rise", BIG, 1, False), E("r_butt", BIG, 3), E("r_hit")]
    views_b = [B_("brittle"), B_("w_shown", FX, 3)]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:forge", "params": {
            k: p[k] for k in ("q_life", "br_hp", "br_up", "br_kb_speed", "br_kb_t", "e_quake_r", "e_anim", "p_item",
                              "p_master", "p_ally", "p_master_lv")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Shield"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
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
