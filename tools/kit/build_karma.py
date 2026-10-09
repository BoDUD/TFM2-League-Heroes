"""Build league_karma.data_champion (support, Util, enchanter) from the parameters P.

    python tools/kit/build_karma.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-09: support, Util, kit A - League's whole kit - plus 「高手连招」). TFM2 has three active
slots: Inner Flame is `skill`, Focused Resolve `skill2`, Mantra the `ult`; Inspire runs on its own.
  passive Gathering Fire (聚炎): her spell hits on enemy champions bring Mantra back sooner. A cooldown cap is all data
          has (`ult_cooldown_mult` caps what is left at cooltime x 100 / (100 + mult), champion-data section 5), so the
          hits since the last Mantra climb a ladder g1..g5 and each rung caps R at (1 - g_step% x rung) of its cooltime:
          the more she lands, the sooner it is back. A champion hit leaves a pending rung (g_pend, g_wait ticks) that her
          next attack or Q climbs (one ladder per tree: the game copies every tree each tick).
  attack  A homing spirit bolt (100% AD).
  skill   Q Inner Flame (心灵烈焰): a `Direction` cast on `EnemyWithoutTower` (the aim is locked at the cast: dodgeable).
          The flame (non-penetrating) stops on the first enemy on its line or at its range and bursts there: q_dmg +
          q_ap% AP to every enemy within q_r and a q_slow% slow for q_slow_t ticks. Mantra -> Soulflare (灵光闪耀): the
          burst deals rq_dmg + rq_ap% AP more and leaves a field that blows rq_wait ticks later: rq_dmg2 + rq_ap2% AP
          and rq_slow% slow to every enemy within rq_r. Q's cooldown is also the caster flag q_cd, which the slot
          shares (an empty branch while it runs, league_leblanc W), so the W -> RQ combo can throw it.
  skill2  W Focused Resolve (坚定专注): a `Targeting` cast on `EnemyWithoutTower` (w_range): w_dmg + w_ap% AP and a tether
          (league_leblanc E's links). If she stays within w_leash for w_hold ticks the unit is rooted (`Bind` w_root)
          and takes the damage again. Mantra -> Renewal (重焕新生), only when she is crowded (two enemy champions within
          w_crowd of her - nothing reads her health): a heal of rw_heal + rw_ap% AP at once and the root rw_root long.
  E       Inspire (鼓舞, automatic): every attack, Q, W and Mantra checks it while the caster flag e_cd is off: an
          allied champion in crowd control within e_range first, then one random ally there with an enemy champion
          within e_near of him (league_lulu R's probe), then herself with an enemy champion within e_self of her. The
          pick gets a shield of e_sh + e_ap% AP for e_t ticks and e_ms% move speed for e_ht ticks. Mantra -> Defiance
          (不屈之心): every allied champion within re_r of him (her too) gets re_sh + re_ap% AP more shield and the haste.
  ult     R Mantra (真言): a 3-tick `None` cast on `EnemyChampion` (r_range) arms `mantra` for r_arm ticks (her hands
          glow); her next spell is empowered - Defiance at once if an ally is in danger, else the next Q (Soulflare),
          or a W while she is crowded (Renewal). Left unused the cooldown is refunded (60 ticks, league_lulu R).
  combos (the pros' Karma, each in the slot it spends)
          W -> E (连线加速): a tether on a champion with E ready shields and hastes her at once (she keeps the tether).
          W -> RQ (定身接真言Q): the root lands on a champion while Mantra is armed and Q ready -> Soulflare thrown at
                  the rooted champion (a lob on his spot locks the aim: it lands).
          RE (真言E救人): Mantra armed while an ally is in crowd control or pressed -> Defiance for the whole group.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_karma.data_champion")
ID = "league_karma"
FX = "asset/league/effects/league_karma_fx"
BIG = "asset/league/effects/league_karma_big"

# Draft numbers (c1). Timings are placeholders until the strips' release frames (assets/source/karma/poses.json).
P = {
    # stats (the pack's ranged supports: Janna/Nami/Sona/Lulu hp 880-950 +80-95, atk 75-80, ap 30 +15, def 20-24,
    # mr 20-24, range 55000-60000, attack cooldown 90); League's Karma: 604 +109 hp, 525 range
    "hp": 900, "hp_g": 92, "atk": 76, "atk_g": 6, "ap": 32, "ap_g": 15, "def": 22, "def_g": 7, "mr": 24, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "atk_st": 11, "a_speed": 5000, "a_y": -1000,
    # passive Gathering Fire (League: 2.5 s per spell hit on a champion, 1.25 s per attack)
    "g_step": 12, "g_rungs": 5, "g_keep": 3600, "g_wait": 240,
    # skill: Q Inner Flame (League: 950 range at 1700/s, width 60, radius 280, 70-250 + 40% AP, slow 35% 1.5 s,
    # cd 9-5 s; Soulflare + 40-280 + 50% AP, the field 1.5 s later 40-280 + 60% AP? and 50% slow)
    "q_cd": 420, "q_range": 62000, "q_dur": 22, "q_st": 10, "q_speed": 5500, "q_reach": 70000, "q_rad": 5000,
    "q_y": -4000, "q_r": 14000, "q_dmg": 80, "q_ap": 55, "q_slow": 35, "q_slow_t": 90,
    "rq_dmg": 50, "rq_ap": 30, "rq_wait": 90, "rq_r": 20000, "rq_dmg2": 70, "rq_ap2": 50, "rq_slow": 50,
    "rq_slow_t": 60,
    # skill2: W Focused Resolve (League: 675 range, leash 1000, 40-160 + 45% AP twice, root 1-1.75 s after 2 s, cd 12 s;
    # Renewal: heal 20% missing hp, root +0.75 s)
    "w_cd": 660, "w_range": 50000, "w_dur": 22, "w_st": 9, "w_speed": 100000, "w_hold": 120, "w_leash": 80000,
    "w_champ_only": 1, "w_dmg": 45, "w_ap": 30, "w_root": 60, "w_crowd": 35000, "rw_heal": 110, "rw_ap": 40, "rw_root": 105,
    # E Inspire (League: 800 range, shield 80-200 + 50% AP 2.5 s, haste 40% decaying over 1.5 s, cd 10-9 s;
    # Defiance: allies within 650 of the target, +shield, haste)
    "e_cd": 540, "e_range": 50000, "e_near": 55000, "e_self": 40000, "e_sh": 90, "e_ap": 50, "e_t": 150, "e_ms": 35,
    "e_ht": 90, "e_anim": 16, "re_r": 30000, "re_sh": 60, "re_ap": 30,
    # ult: R Mantra (League: next spell empowered within 8 s, cd 40-34 s)
    "r_cd": 2100, "r_range": 70000, "r_arm": 360, "r_anim": 18,
    # her spoken lines: one every vo_gap ticks at most
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
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    d = tick if isinstance(tick, str) else {"Time": {"tick": tick}}
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": d, **fields}}


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


def magic(dmg, ap):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": 0, "can_crit": False}


def heal_me(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Bleed"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


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


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, end, target="EnemyWithoutTower", hit=(), travel=1):
    """A hidden lob onto the unit in hand: `end` runs on its landing spot, `hit` on the unit (a `Delayed` there is
    queued on him)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target,
            "applied_effects": [T(e) for e in hit], "end_effects": list(end)}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": flat(effect)}


def build(p):
    # ------------------------------------------------------------------ passive: Gathering Fire
    def climb(src):
        """On her, from a spell's champion hit: a pending rung (one a cast) that her next attack or Q climbs."""
        return on_me(refresh("g_pend", p["g_wait"]))

    def gather():
        """Climb one rung while one is pending: each rung caps Mantra's cooldown lower."""
        rungs = p["g_rungs"]
        out = NONE
        for k in range(1, rungs + 1):          # rung k reached: cap at (1 - step k) of the cooltime
            left = max(100 - p["g_step"] * k, 10)
            step = combine(refresh(f"g{k}", p["g_keep"]), refresh("g_cap", 2, ult_cooldown_mult=round(10000 / left) - 100))
            out = step if k == 1 else sw(f"g{k - 1}", step, out)
        return sw("g_pend", combine(*rm("g_pend"), out))

    # ------------------------------------------------------------------ E Inspire (automatic) and Defiance
    def inspire(mantra):
        """On the picked ally (or her): the shield and the haste; Defiance spreads it round him."""
        own = [shield(p["e_sh"], p["e_ap"], p["e_t"]), buff("e_on", "WithShield"),
               buff("e_haste", p["e_ht"], move_speed_mult=p["e_ms"]), view("e_land")]
        if not mantra:
            return own
        wave = lob("re_lob", [view("re_wave"), zone("re_zone", p["re_r"], 1, 1, "AllyChampion", [
            shield(p["re_sh"], p["re_ap"], p["e_t"]), buff("e_on", "WithShield"),
            buff("e_haste", p["e_ht"], move_speed_mult=p["e_ms"]), view("e_land")])], target="AllyChampion")
        return own + [wave]

    def e_go(self_=False, pose=True):
        """Spend E on the unit in hand (Defiance while Mantra is armed); `pose` plays her E strip."""
        head = [flag("e_got", 3), refresh("e_cd", p["e_cd"])] + ([anim("skill_e", p["e_anim"])] if pose else [])
        plain = combine(*inspire(False), sfx("e_cast"), voice("vo_e", p))
        emp = combine(*rm("mantra"), *inspire(True), sfx("re_cast"), voice("vo_e", p))
        body = sw("mantra", emp, plain)
        return combine(*head, on_me(body) if self_ else body)

    probe = lob("e_probe", [zone("e_count", p["e_near"], 1, 1, "EnemyChampion", [flag("e_n1", 4)])],
                target="AllyChampion", hit=[delayed(2, sw("e_n1", sw("e_got", NONE, e_go())))])

    def e_check():
        """The automatic Inspire: an ally in crowd control, an ally pressed, then herself pressed."""
        return sw("e_cd", NONE, combine(
            *rm("e_got", "e_n1", "e_me"),
            pick(p["e_range"], "AllyChampionInCC", e_go()),
            sw("e_got", NONE, pick(p["e_range"], "AllyNotSelf", probe)),
            around(p["e_self"], "EnemyChampion", [flag("e_me", 6)]),
            delayed(4, sw("e_got", NONE, sw("e_me", e_go(self_=True))))))

    # ------------------------------------------------------------------ attack: the spirit bolt
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", combine(
        sfx("a_cast"), homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
        on_me(gather(), delayed(2, e_check()))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Inner Flame / Soulflare
    def burst(emp):
        out = [view("rq_boom" if emp else "q_boom"), sfx("rq_hit" if emp else "q_hit"),
               zone("q_burst", p["q_r"], 1, 1, "EnemyWithoutTower",
                    [magic(p["q_dmg"] + (p["rq_dmg"] if emp else 0), p["q_ap"] + (p["rq_ap"] if emp else 0)),
                     buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]), view("q_hit")]),
               zone("q_burst_c", p["q_r"], 1, 1, "EnemyChampion", [climb("q")])]
        if emp:
            w = p["rq_wait"] + 1
            out += [view("rq_field"), sfx("rq_field"),
                    delayed(p["rq_wait"] - 4, view("rq_blast")),
                    zone("rq_zone", p["rq_r"], w, w, "EnemyWithoutTower",
                         [magic(p["rq_dmg2"], p["rq_ap2"]), buff("rq_slow", p["rq_slow_t"], move_speed_mult=-p["rq_slow"]),
                          view("q_hit")]),
                    zone("rq_zone_c", p["rq_r"], w, w, "EnemyChampion", [climb("rq")])]
        return out

    def flame(emp):
        name = "rq_ball" if emp else "q_ball"
        return line(name, p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyWithoutTower", False, [], burst(emp))

    def q_spend(emp):
        head = [refresh("q_cd", p["q_cd"]), sfx("q_cast")]
        if emp:
            return combine(*rm("mantra"), *head, voice("vo_q", p))
        return combine(*head, voice("vo_q", p))

    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Direction", "EnemyWithoutTower",
                   sw("q_cd", NONE, combine(
                       sw("mantra", combine(q_spend(True), flame(True)), combine(q_spend(False), flame(False))),
                       on_me(gather(), delayed(2, e_check())))))

    # ------------------------------------------------------------------ skill2: W Focused Resolve / Renewal
    tie = homing("w_tie", 100000, 0, "EnemyWithoutTower", [
        pick(p["w_leash"], "AllyOnlySelf", flag("w_tie", 3), fp=True),
        delayed(1, sw("w_tie", sw("w_held", homing("w_link", 100000, 0, "EnemyWithoutTower", [
            lob("w_spot", [{"type": "BackToCasterLinearProjectile", "name": n("w_tether"), "speed": 3000,
                            "range": p["w_leash"] + 15000, "penetrate": True, "shape": circle(0),
                            "applied_target": "EnemyWithoutTower", "applied_effects": []}])])),
                     combine(*rm("w_held"))))])
    rq_combo = sw("w_champ", sw("mantra", sw("q_cd", NONE, combine(
        q_spend(True), lob("rq_aim", [flame(True)])))))

    def root(t):
        return [{"type": "Bind", "duration": t}, buff("w_root", t), magic(p["w_dmg"], p["w_ap"]), view("w_snap"),
                tsfx("w_root")]

    def resolve():
        """The tether on the unit; held for w_hold ticks it roots (Renewal, the caster flag w_renew: longer)."""
        champ = pick(1, "EnemyChampion", climb("w"), on_me(refresh("w_champ", p["w_hold"] + 8),
                     sw("e_cd", NONE, e_go(self_=True, pose=False))), fp=True)
        snap = sw("w_held", combine(*rm("w_held"), sw("w_renew", combine(*root(p["rw_root"])), combine(*root(p["w_root"]))),
                                    rq_combo))
        return homing("w_beam", p["w_speed"], 0, "EnemyWithoutTower", [
            magic(p["w_dmg"], p["w_ap"]), view("w_hit"), champ, buff("w_mark", p["w_hold"]),
            on_me(refresh("w_held", p["w_hold"] + 4)), casted(p["w_hold"], 6, tie), delayed(p["w_hold"], snap)])

    w_plain = combine(sfx("w_cast"), voice("vo_w", p))
    w_emp = combine(*rm("mantra"), refresh("w_renew", p["w_hold"] + 8), sfx("w_cast"), voice("vo_w", p),
                    heal_me(p["rw_heal"], p["rw_ap"]), cview("rw_heal"))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting",
                    "EnemyChampion" if p["w_champ_only"] else "EnemyWithoutTower", combine(
        *rm("c1", "c2"), around(p["w_crowd"], "EnemyChampion", [sw("c1", flag("c2", p["w_st"] + 2),
                                                                    flag("c1", p["w_st"] + 2))]),
        delayed(p["w_st"] - 1, *rm("w_champ", "w_renew"), sw("mantra", sw("c2", w_emp, w_plain), w_plain), resolve(),
                on_me(delayed(2, e_check())))))

    # ------------------------------------------------------------------ ult: R Mantra (arms the next spell)
    refund = sw("mantra", combine(*rm("mantra"), refresh("r_ref", 3, ult_cooldown_mult=4900)))
    ult = action("ult", p["r_anim"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion", combine(
        *rm(*[f"g{k}" for k in range(1, 7)]), refresh("mantra", p["r_arm"]), cview("r_cast"), sfx("r_cast"),
        voice("vo_r", p), on_me(delayed(2, e_check()), delayed(p["r_arm"], refund))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bolt"), P_("q_ball"), P_("rq_ball"), P_("w_beam"), P_("w_tether")]
    views_e = [E("a_hit"), E("q_boom", BIG, 2, False), E("rq_boom", BIG, 2, False), E("q_hit"),
               E("rq_field", BIG, -1, False), E("rq_blast", BIG, 2, False), E("w_hit"), E("w_snap"),
               E("e_land"), E("re_wave", BIG, -1, False), E("r_cast", FX, 2), E("rw_heal", FX, 2)]
    views_b = [P_("e_on", FX, 2), P_("e_haste", FX, -1), P_("w_mark", FX, 2), P_("w_root", FX, -1),
               P_("mantra", FX, 2), P_("q_slow", FX, -1), P_("rq_slow", FX, -1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Range", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
