"""Build tft_alune.data_champion (the tft pack's third hero: Alune, mid, Magician) from the parameters P.

    python tools/kit/build_alune.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Alune is Aphelios's sister, the moon priestess of Teamfight Tactics set 18: the 5-cost unit DA_18_Alune (Lunar
Goddess / Eclipse Knight / Mage, range 4, 900 health, 35 mana). TFT gives her one ability (Moonfall: moonshards fall on
the nearest enemies, magic damage each and 20% magic resistance shred for 6 s; at full moon the moon itself falls, its
damage split between all enemies) and an attack-speed boost (20-30% for 5 s). The rest is our own design (the user's
pick, 2026-10-26: mid lane, plan A 「月相」):
  passive Moon Phase (月相): each Moonfall and Moonlight cast grows the moon a phase (flags ph1 / ph2 / ph3, a little
          moon over her head: `view_buffs` p_moon1..3); full at three. The ult falls harder by phase (+r_ph% damage a
          phase) and wanes the moon back to new.
  attack  the spiral ring flung like a disc (100% AD), homing on `Enemy` (towers too), released on a_rel; it flies back
          to her (tft.dll, below).
  skill   Moonfall (月之降临, TFT's ability), `Targeting` on `EnemyWithoutTower` (q_range): q_n moonshards fall on the
          q_n enemies nearest her within q_range (tft.dll), each q_fall ticks after the cast (the shard falling is the
          upright picture q_drop on its landing spot, the burst q_hit) with q_dmg + q_ratio% AP within q_r and the
          moonlit mark (magic_resistance_mult -q_shred for q_shred_t ticks).
  skill2  Moonlight (月华), `Targeting` on `EnemyChampion` (e_range, only in fights): she and every allied champion
          within e_r gain attack_speed_mult e_as for e_t ticks (TFT's attack-speed boost).
  ult     Moon Descends (月曜降临), `Targeting` on `EnemyChampion` (r_range): a warning ring for r_open ticks on the
          champion's spot, then the full moon slams down: r_dmg + r_ratio% AP (+r_ph% a phase) split between the enemies
          within r_r (tft.dll) and the ones within r_core stunned r_stun ticks; the moon wanes to new.

What the data cannot read is the tft pack's own code (the user: 「要做附加包的地方你就做附加包」, then 「拉露恩要和诺拉
爆爆放一个mod里面」: tft.dll, addons/tft/src/alune.rs; the kit's passive is tft_alune:moon, params NATIVE_KEYS):
  * Moonfall's shards fall on the q_n NEAREST enemies (TFT's rule): the data only casts (the pose, the sound, flag q_go
    for 2 ticks, the phase); tft.dll drops the shards (q_drop, q_fall ticks later q_hit, damage and the mark);
  * Moon Descends' damage is SPLIT between the enemies it hits (TFT's rule): the data's slam marks them (r_mark<phase>
    2 ticks, the stun) and deals nothing; tft.dll shares (r_dmg + r_ratio% AP) x the phase bonus x r_split% between
    them, each at most r_cap% of the whole (one alone takes the most);
  * the ring comes back (the boomerang it is in League's cinematic): each attack that hits marks a_mark; tft.dll flies
    the ring back to her (projectile a_back, `Linear`, through every enemy on the way), a_back_r% AD to each.
--plain builds the data alone for the classic-engine balance sims (they run no DLL code): one shard on the target and
the others on random enemies within q_range (data has no "nearest", each a hidden lob), every enemy within r_r taking
the slam's whole damage, no ring back. A build of P checks alune.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_alune"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips exist (tools/art/rig_alune.py). Numbers = the 10-min classic-SDK simulations (C:/t/al_sim,
# a copy of the balance sim: mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three
# lineups, both sides; 2026-10-26): the draft (Q 30 + 22% every 270, R 130 + 55%, E +30%) -2.60 on seeds 1-8
# (league_ziggs +1.38); Q 40 + 30%, R 160 + 70% +0.44; Q 45 + 34% every 240, R 170 + 75%, E +40% +1.98; Q 42 + 32% every
# 255, R 165 + 72%, E +36% +1.20 / +1.19 (seeds 9-16; league_ziggs +2.22) = P, all --plain. tft.dll's rules are not
# simulated (the classic engine runs no DLL code): its split is set so two enemies take about what the data deals each.
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9)
    "hp": 880, "hp_g": 98, "atk": 74, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 9, "a_speed": 4000,
    # the ring's way back (tft.dll)
    "a_back_r": 30,
    # passive Moon Phase
    "r_ph": 20,
    # Moonfall (TFT: 160 / 240 / 380 magic damage a shard at 1-3 stars, 20% shred for 6 s)
    "q_cd": 255, "q_range": 70000, "q_dur": 36, "q_rel": 15, "q_n": 3, "q_fall": 20, "q_r": 18000,
    "q_dmg": 42, "q_ratio": 32, "q_shred": 20, "q_shred_t": 360,
    # Moonlight (TFT: +20 / 25 / 30% attack speed for 5 s)
    "e_cd": 600, "e_range": 60000, "e_dur": 24, "e_rel": 9, "e_r": 50000, "e_as": 36, "e_t": 300,
    # Moon Descends
    "r_cd": 3000, "r_range": 75000, "r_dur": 40, "r_rel": 25, "r_open": 45, "r_r": 45000, "r_core": 22000,
    "r_dmg": 165, "r_ratio": 72, "r_stun": 50,
    # tft.dll's split: the slam's damage (what --plain deals each enemy) x r_split% shared between the n enemies hit,
    # each at most r_cap% of it - alone 180%, two 110%, three 73%, five 44%
    "r_split": 220, "r_cap": 180,
}
# what tft.dll reads from passive.params (addons/tft/src/alune.rs)
NATIVE_KEYS = ("q_n", "q_range", "q_fall", "q_r", "q_dmg", "q_ratio", "q_shred", "q_shred_t", "r_dmg", "r_ratio",
               "r_ph", "r_split", "r_cap", "a_back_r", "a_speed")


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


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pick(rng, target, effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point; `seen` = the
    picture played on the landing point the whole flight."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ passive Moon Phase: one phase a cast
    phase_up = when("ph2", combine(unflag("ph2"), flag("ph3", None)),
                    when("ph1", combine(unflag("ph1"), flag("ph2", None)),
                         when("ph3", combine(), flag("ph1", None))))

    # ------------------------------------------------------------------ attack: the ring flung like a disc
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")] + ([buff("a_mark", 2)] if is_native else [])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_ring", "Enemy", hit, p["a_speed"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Moonfall
    shard = lob("q_shard", p["q_fall"], [sfx("q_hit"), view("q_hit"),
                                         zone("q_zone", p["q_r"], [ap(p["q_dmg"], p["q_ratio"]),
                                                                   buff("q_shred", p["q_shred_t"],
                                                                        magic_resistance_mult=-p["q_shred"])])],
                seen="q_drop")
    if is_native:   # tft.dll drops q_n shards on the nearest enemies
        fall = flag("q_go", 2)
    else:           # one on the target, the rest on random enemies within reach
        fall = combine(shard, *[pick(p["q_range"], "EnemyWithoutTower", [shard]) for _ in range(p["q_n"] - 1)])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_rel"] - 1, fall, phase_up)))

    # ------------------------------------------------------------------ skill2: Moonlight
    glow = [buff("e_glow", p["e_t"], attack_speed_mult=p["e_as"]), tsfx("e")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    delayed(p["e_rel"] - 1, sfx("e_cast"), around(p["e_r"], "AllyChampion", glow), phase_up))

    # ------------------------------------------------------------------ ult: Moon Descends
    def slam(k):   # k phases: tft.dll's marks (it shares the damage out); --plain the damage itself (+r_ph% a phase)
        dmg = [buff(f"r_mark{k}", 2)] if is_native else [ap(p["r_dmg"] * (100 + k * p["r_ph"]) // 100,
                                                     p["r_ratio"] * (100 + k * p["r_ph"]) // 100)]
        return combine(zone(f"r_hit{k}", p["r_r"], dmg + [view("r_hit")]),
                       zone(f"r_core{k}", p["r_core"], [{"type": "Stun", "duration": p["r_stun"]}]))
    wane = combine(unflag("ph1"), unflag("ph2"), unflag("ph3"))
    moon = [view("r_moon"), sfx("r_blast"),
            when("ph3", slam(3), when("ph2", slam(2), when("ph1", slam(1), slam(0)))), wane]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), delayed(p["r_rel"] - 1, view("r_fall"),
                                           lob("r_fall", p["r_open"], moon, target="EnemyChampion", seen="r_warn"))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_ring (and tft.dll's a_back) is a disc seen edge-on, the same turned with its flight; q_shard and r_fall fly
    # hidden: the shard and the moon fall as upright pictures on the landing spot (ViewEffects, never turned): q_drop the
    # shard's fall (the lob's range picture), r_fall the moon's descent over the champion's spot from the launch (over
    # the units: z 3) while r_warn shadows the ground under it (z -2), r_moon the slam where it lands
    views_p = [B_("a_ring")] + ([B_("a_back", tag="a_ring")] if is_native else [])
    views_e = [E("a_hit"), E("q_drop", BIG, 3, False), E("q_hit", FX, 2, False),
               E("r_warn", BIG, -2, False), E("r_fall", BIG, 3, False), E("r_moon", BIG, 3, False), E("r_hit")]
    views_b = [B_("q_shred", FX, 3), B_("e_glow", FX, 3), B_("ph1", FX, 4, "p_moon1"), B_("ph2", FX, 4, "p_moon2"),
               B_("ph3", FX, 4, "p_moon3")]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"],
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
    if is_native:   # tft.dll (addons/tft/src/alune.rs): the TFT rules the data cannot read
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:moon", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


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
    """addons/tft/src/alune.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), and every name it reads off the data or plays (`al("...")`, `al(&format!("...{k}"))` for its 0..4
    phases) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "alune.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"alune.rs Params::default() differs from P (alune.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'al\("(\w+)"\)', src))
    read |= {f"{x}{k}" for x in re.findall(r'al\(&format!\("(\w+)\{k\}"\)\)', src) for k in range(4)}
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"alune.rs reads or plays names the kit does not have: {missing}")


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
