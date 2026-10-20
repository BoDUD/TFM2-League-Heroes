"""Build league_velkoz.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_velkoz.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: mid, layout A, with the add-on). TFM2 has three active slots: Plasma Fission (Q) is
`skill`, Tectonic Disruption (E) `skill2`, Life Form Disintegration Ray (R) the `ult`. Void Rift (W) rides on the
attack, the passive Organic Deconstruction on every spell hit.
  passive Organic Deconstruction (有机体解构): every spell hit on an enemy champion is a stack; the third deals p_dmg +
          p_ratio% AP TRUE damage to the champion hit (an `ApAttack` under a 1-tick magic_resistance_penetration 100
          caster buff, league_syndra's way) and the count starts over. Nothing reads a buff on another unit, so the
          count lives on him (league_brand's ladder: caster flags p_1 -> p_2, p_keep ticks, climbed once per source per
          cast through a 3-tick lock; R's every r_mark-th wave stacks); the pips (1, 2,
          the burst) show over the champion hit. Every stack also "researches" for p_keep ticks (`p_res`): R deals
          true damage while it holds. The add-on (addons/league_velkoz, --native) counts real stacks per champion.
  attack  a void bolt (homing, 100% AD) released on a_rel. W Void Rift (虚空裂隙): every third attack (a_1 -> a_2, a_keep
          ticks) also tears a rift from him toward the target (a `LineRangeProjectile`, w_len x w_w): w_dmg + w_ratio%
          AP magic damage on the line at once (w_ap1), w_dmg2 + w_ratio2% AP when it detonates w_det ticks later;
          each burst is a stack on the champions in it.
          Combos (the user: 「有连招要做连招」; League's Vel'Koz lands E or Q, then rifts the slowed / airborne champion):
          E -> W: an attack inside e_combo (opened by E knocking up a champion) tears the rift at once, whatever the
          count; Q -> W W: an attack inside q_combo (opened by Q or its split hitting a champion - the slow) tears both
          rifts (League's two charges), the second w_gap ticks later.
  skill   Q Plasma Fission (等离子裂变), `Targeting` on `EnemyWithoutTower` (q_range): a bolt (non-penetrating line,
          q_speed, q_len) - q_dmg + q_ratio% AP magic and a q_slow% slow for q_slow_t ticks to the first enemy; on a
          hit it splits where it struck (League's split on hit; data cannot turn a bolt, so the split is a burst
          q_sr round the spot: q_sdmg + q_sratio% AP and the slow on every enemy in it, its picture two bolts flying
          off at right angles). Combo E -> Q: a Q released inside e_combo flies at the airborne champion (any champion
          in crowd control within q_range + 10000) at q_fspeed and closes the window.
  skill2  E Tectonic Disruption (构造分解), `Targeting` on `EnemyWithoutTower` (e_range): the ground at the target's spot
          cracks (telegraph) and e_delay ticks later erupts (radius e_r): e_dmg + e_ratio% AP magic damage and a
          knock-up (`Airborne` e_air ticks); a champion knocked up opens e_combo.
  ult     R Life Form Disintegration Ray (生命形态瓦解射线), `Targeting` on `EnemyChampion` (r_range): castable only while
          a champion is researched (`p_res`: the slot's effect is empty otherwise, which the AI never casts -
          league_leblanc W - the combo "stacks -> R"). He channels r_t ticks (`ult` then `ult_loop`): every r_p ticks
          a beam wave (r_len x r_w, aimed at the champion where he stands then: League's beam follows) deals r_dmg +
          r_ratio% AP magic damage in r_t / r_p equal parts - true while `p_res` holds - and every r_mark-th wave
          stacks the passive. The beam's picture rides a homing projectile lifted to his eye (`r_beam`, r_bspeed a
          tick, league_lucian Q's way: a line's picture sits on his pivot and turns upside down to the left). The waves
          wait on the target (a `Targeting` cast's `Delayed`): his death ends the beam. Crowd control on him or his
          death ends the channel (league_malzahar R's breaks).
The add-on copy (--native, addons/league_velkoz): the passive stack is the native `league_velkoz:deconstruct` (stacks,
research and the true-damage burst per champion), Q's split the native `league_velkoz:fission` (two bolts at right
angles from the struck spot), R's damage lines `league_velkoz:ray` (true damage on the champions researched by him).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_velkoz.data_champion")
ID = "league_velkoz"
FX = "asset/league/effects/league_velkoz_fx"
BIG = "asset/league/effects/league_velkoz_big"

# League units x 100 = ours (attack range 525 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings provisional until the frames (tools/art/rig_velkoz.py): every action releases on a_rel /
# q_rel / e_rel / r_rel ticks.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Vel'Koz:
    # 590 +102 hp, 22 armour, 30 mr, 340 move, 525 range, attack speed 0.643
    "hp": 880, "hp_g": 92, "atk": 72, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 90, "a_rel": 10, "a_speed": 4500, "a_y": 0, "a_keep": 600,
    # passive (League: 33-170 by level + 50% AP true damage, stacks 7 s)
    "p_keep": 420, "p_dmg": 40, "p_ratio": 40,
    # W Void Rift (League: 1050 long, 30-150 + 15% AP, then 45-225 + 25% AP after 0.25 s, two charges)
    "w_len": 75000, "w_w": 9000, "w_ap1": 4, "w_det": 19, "w_life": 34, "w_dmg": 30, "w_ratio": 15, "w_dmg2": 45,
    "w_ratio2": 25, "w_gap": 18,
    # Q Plasma Fission (League: 1050 range, 80-240 + 90% AP, 70% slow fading over 1.25 s, speed 1300, the split 1100)
    "q_cd": 420, "q_range": 85000, "q_dur": 30, "q_rel": 10, "q_speed": 2200, "q_fspeed": 4000, "q_rad": 5000,
    "q_len": 105000, "q_y": 0, "q_dmg": 80, "q_ratio": 60, "q_slow": 50, "q_slow_t": 75, "q_sr": 26000,
    "q_sdmg": 40, "q_sratio": 30, "q_cw": 90,
    # the add-on's split bolts (League: 1100 each way): from q_soff beside the struck spot, q_slen long
    "q_slen": 55000, "q_soff": 12000,
    # E Tectonic Disruption (League: 810 range, radius 235, 70-230 + 30% AP, knock-up 0.75 s after a 0.55 s delay)
    "e_cd": 660, "e_range": 75000, "e_dur": 30, "e_rel": 10, "e_delay": 33, "e_r": 22000, "e_dmg": 70, "e_ratio": 30,
    "e_air": 45, "e_cw": 75,
    # R Life Form Disintegration Ray (League: 1550 long, 450-800 + 125% AP over 2.5 s, true on researched champions)
    "r_cd": 2100, "r_range": 95000, "r_len": 120000, "r_w": 10000, "r_t": 150, "r_p": 15, "r_anim": 16, "r_rel": 10,
    "r_dmg": 300, "r_ratio": 100, "r_brk": 5, "r_mark": 3,
    # the beam's picture: a homing projectile at 1 px a tick lifted to his eye (5000 - r_by over the pivot)
    "r_bspeed": 1000, "r_by": -17000,
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


def flat(node):
    """The tree with every Combine that sits straight in a Combine's, a Delayed's or a RandomTarget's `effects`
    spliced into that list (the same effects in the same order, fewer nodes for the game's per-tick copy)."""
    if isinstance(node, list):
        return [flat(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: flat(v) for k, v in node.items()}
    if out.get("type") in ("Combine", "Delayed", "RandomTarget"):
        eff = []
        for x in out["effects"]:
            if isinstance(x, dict) and x.get("type") == "Combine":
                eff.extend(x["effects"])
            else:
                eff.append(x)
        out["effects"] = eff
    return out


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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true_ap(dmg, ratio):
    """AP-scaled true damage: the `ApAttack` under a 1-tick full magic penetration on him (league_syndra)."""
    return combine(refresh("pen", 1, magic_resistance_penetration=100), ap(dmg, ratio), *rm("pen"))


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a target's or a projectile's list (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Fire"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def strip(name, width, length, delay, apply, target, effects):
    """A `LineRangeProjectile` from him along the cast: hits once at `apply - 1`, gone at `delay - 1`."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, seen=""):
    """A hidden lob onto the target's spot (league_karthus's): `end` runs there `travel` ticks later; `seen` = a
    picture played on the landing point the whole flight (the telegraph)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": "EnemyWithoutTower",
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive: Organic Deconstruction
    def mark(src):
        """On an enemy champion a spell of his hit: the third stack bursts in true damage, the pips; research; the
        count on him a tick later (once per source per lock_t ticks)."""
        if native:
            return {"type": "Native", "effect_ref": f"{ID}:deconstruct"}
        keep = p["p_keep"]
        climb = sw("p_2", combine(*rm("p_1", "p_2")),
                   sw("p_1", combine(refresh("p_1", keep), refresh("p_2", keep)), refresh("p_1", keep)))
        lock = f"lk_{src}"
        return combine(sw("p_2", combine(true_ap(p["p_dmg"], p["p_ratio"]), view("p_full"), tsfx("p_full")),
                          sw("p_1", combine(view("p_s2"), tsfx("p_2")), combine(view("p_s1"), tsfx("p_1")))),
                       refresh("p_res", keep),
                       on_me(delayed(1, sw(lock, NONE, combine(flag(lock, 3), climb)))))

    # ------------------------------------------------------------------ attack: the void bolt + W Void Rift
    def rift():
        """W: the rift from him toward the target - the picture, the first burst at once, the detonation."""
        L, W_ = p["w_len"], p["w_w"]
        return combine(
            sfx("w"),
            strip("w_rift", W_, L, p["w_life"], p["w_life"] + 5, "EnemyWithoutTower", []),
            strip("w_b1", W_, L, p["w_ap1"], p["w_ap1"], "EnemyWithoutTower",
                  [ap(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")]),
            strip("w_b1c", W_, L, p["w_ap1"], p["w_ap1"], "EnemyChampion", [mark("w1")]),
            strip("w_b2", W_, L, p["w_det"], p["w_det"], "EnemyWithoutTower",
                  [ap(p["w_dmg2"], p["w_ratio2"]), view("w_hit"), tsfx("w_boom")]),
            strip("w_b2c", W_, L, p["w_det"], p["w_det"], "EnemyChampion", [mark("w2")]))

    # how many rifts this attack tears: Q -> W W (q_combo), E -> W (e_combo), else every third attack
    count = combine(sw("q_combo", combine(*rm("q_combo", "e_combo", "a_1", "a_2"), flag("w_go", 1), flag("w_two", 1)),
                       sw("e_combo", combine(*rm("e_combo", "a_1", "a_2"), flag("w_go", 1)),
                          sw("a_2", combine(*rm("a_1", "a_2"), flag("w_go", 1)),
                             sw("a_1", refresh("a_2", p["a_keep"]), refresh("a_1", p["a_keep"]))))),
                    sw("w_go", combine(rift(), sw("w_two", delayed(p["w_gap"], alive(rift()))))), *rm("w_go", "w_two"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(
                          sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                           p["a_speed"], p["a_y"]),
                          count))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Plasma Fission
    slow = buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"])
    if native:
        split = [{"type": "Native", "effect_ref": f"{ID}:fission"}]
    else:
        split = [view("q_split"), sfx("q_split"),
                 zone("q_frag", p["q_sr"], [ap(p["q_sdmg"], p["q_sratio"]), slow, view("q_split_hit"),
                                            tsfx("q_split_hit")]),
                 zone("q_frag_c", p["q_sr"], [mark("q"), refresh("q_combo", p["q_cw"])], target="EnemyChampion")]

    def bolt(name, speed):
        hit = [ap(p["q_dmg"], p["q_ratio"]), slow, view("q_hit"), tsfx("q_hit"), refresh("q_struck", 2),
               pick(1, "EnemyChampion", mark("q"), refresh("q_combo", p["q_cw"]), fp=True)]
        return line(name, speed, p["q_len"], p["q_rad"], "EnemyWithoutTower", hit,
                    end=[sw("q_struck", combine(*rm("q_struck"), *split))], y=p["q_y"])

    quick = pick(p["q_range"] + 10000, "EnemyChampionInCC", flag("q_go", 1), *rm("e_combo"),
                 bolt("q_bolt_f", p["q_fspeed"]))
    shot = combine(*rm("q_go"), sw("e_combo", quick), sw("q_go", NONE, bolt("q_bolt", p["q_speed"])), *rm("q_go"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(shot))))

    # ------------------------------------------------------------------ skill2: E Tectonic Disruption
    erupt = lob("e_spot", p["e_delay"], [
        view("e_boom"), sfx("e_boom"),
        zone("e_blast", p["e_r"], [ap(p["e_dmg"], p["e_ratio"]), {"type": "Airborne", "duration": p["e_air"]},
                                   view("e_hit"), tsfx("e_air")]),
        zone("e_blast_c", p["e_r"], [mark("e"), refresh("e_combo", p["e_cw"])], target="EnemyChampion")],
        seen="e_mark")
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(erupt))))

    # ------------------------------------------------------------------ ult: R Life Form Disintegration Ray
    waves = p["r_t"] // p["r_p"]
    dmg, ratio = round(p["r_dmg"] / waves), round(p["r_ratio"] / waves)

    def wave(k):
        """The k-th wave at the target where he stands now: the damage line (every r_mark-th one also stacks the passive
        on the champions in it) and the beam's picture from his eye (r_beam: a lifted homing projectile, the line's own
        picture would sit on his pivot - league_lucian Q's beam)."""
        beam = homing("r_beam", "EnemyChampion", [], p["r_bspeed"], p["r_by"])
        if native:
            return combine({"type": "Native", "effect_ref": f"{ID}:ray"}, beam)
        champ = [sw("p_res", tsfx("r_true"), tsfx("r_hit"))] + ([mark("r")] if k % p["r_mark"] == 0 else [])
        return combine(
            strip("r_wave", p["r_w"], p["r_len"], 1, 1, "EnemyWithoutTower",
                  [sw("p_res", true_ap(dmg, ratio), ap(dmg, ratio)), view("r_hit")]),
            strip("r_wave_c", p["r_w"], p["r_len"], 1, 1, "EnemyChampion", champ),
            beam)
    # crowd control on him ends the channel at the next check (league_malzahar R's breaks, one AddCasted on him)
    breaks = casted(p["r_t"], p["r_brk"], pick(1, "AllyChampionInCC", *rm("r_ch"),
                                               {"type": "RemoveCasterAnimation", "name": "ult"},
                                               {"type": "RemoveCasterAnimation", "name": "ult_loop"}), kind="Heal")
    t0 = p["r_rel"] - 1
    ray = combine(refresh("r_ch", p["r_t"] + p["r_rel"]), sfx("r"), voice("vo_r", p), anim("ult", p["r_anim"]),
                  delayed(p["r_anim"], sw("r_ch", anim("ult_loop", p["r_t"] + p["r_rel"] - p["r_anim"]))),
                  on_me(breaks),
                  delayed(t0, alive(sw("r_ch", sfx("r_beam")))),
                  *[delayed(t0 + k * p["r_p"], alive(sw("r_ch", wave(k)))) for k in range(waves)],
                  delayed(t0 + p["r_t"], sw("r_ch", sfx("r_end")), *rm("r_ch")))
    ult = action("ult", p["r_rel"] + 2, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 sw("p_res", combine(decoy(p["r_dmg"], p["r_ratio"], ap), ray)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX, rep=True: {"type": "Animated", "name": n(name), "anim": anim_,
                                                     "tag": tag or name, "repeat": rep, "z": 2}
    views_p = [Pj("a_bolt"), Pj("q_bolt"), Pj("q_bolt_f", "q_bolt"), Pj("w_rift", anim_=BIG, rep=False),
               Pj("r_beam", anim_=BIG, rep=False)] + ([Pj("q_split_bolt")] if native else [])
    views_e = [E("a_hit"), E("q_hit"), E("q_split", BIG, 2, False), E("q_split_hit"), E("w_hit"),
               E("e_mark", BIG, -1, False), E("e_boom", BIG, 2, False), E("e_hit"), E("r_hit"),
               E("p_s1"), E("p_s2"), E("p_full")]
    views_b = [B_("q_slow", FX, -1)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": f"{ID}:research", "params": {
            k: p[k] for k in ("p_keep", "p_dmg", "p_ratio", "q_sdmg", "q_sratio", "q_slow", "q_slow_t", "q_cw", "q_speed",
                              "q_rad", "q_range", "q_slen", "q_soff", "e_range", "e_r", "atk_range", "r_range", "r_len",
                              "r_w", "r_dmg", "r_ratio", "r_t", "r_p", "r_mark")}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": flat(attack_a), "skill": flat(skill), "skill2": flat(skill2), "ult": flat(ult),
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
