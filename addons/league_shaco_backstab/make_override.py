"""Build the add-on's copy of Shaco from the main pack (Backstab from behind; Hallucinate's clone a unit of its own).

    python addons/league_shaco_backstab/make_override.py [--check]

Reads the main pack's league/champion/league_shaco.data_champion and writes
addons/league_shaco_backstab/override/league_shaco.data_champion and .../text/champion.i18n: the same kit with -
  * the attack's and the shiv's backstab twins (TargetProjectile league_shaco_a_bs / league_shaco_e_bs on
    EnemyChampionInCC, 15 + 25% AD) aimed at every enemy champion and only marking him with src/lib.rs's ASK (3 ticks);
  * the passive league_shaco_backstab:backstab (it deals the backstab when Shaco is behind; params = the twins' numbers);
  * R (0.2.0) asking for its clone as a unit: as it is cast the flag R_UNIT goes and R_ASK (3 ticks) is laid on him - the
    passive answers with spawn_unit and, when the host gives a unit, puts R_UNIT back on him; the clone riding on the
    target (the `Delayed 12`: its picture, its sound, the `AddCasted` with its stabs, its watch and its blast) plays only
    when R_UNIT is not there 12 ticks after the cast, so a host without the unit plays the main pack's R as it is.
    The numbers the natives use for the unit and its blast (src/lib.rs: CLONE_*, BOOM*, FEAR_*, BOX_*) are checked
    against the main pack's R and attack here: change the main pack and this script stops until lib.rs follows;
  * W (0.3.0, src/jack.rs; tools/art/unit_shaco_jack.py draws its sheet): the box's landing runs the native
    league_shaco_backstab:jack (it spawns the box's body there and lays W_UNIT on him when the host gives a unit); at the
    spring the box's picture (w_box) and its shooting zone (w_shots) play only without W_UNIT - the add-on fires the
    volleys from the body; the fears and the sound stay the data's. The numbers the natives use (src/jack.rs: W_*, JACK_*)
    are checked against the main pack's W and the unit sheet here;
  * Two-Shiv Poison (0.3.1): the shiv's hit (TargetProjectile league_shaco_e_shiv in the attack slot) runs the native
    league_shaco_backstab:shiv first - 50 % more of the shiv's magic damage on a target below 30 % of its maximum health
    (League's; src/lib.rs E_HIT / E_HIT_AP checked against the main pack's shiv, E_LOW_PCT / E_LOW_MORE League's);
  * the attack's, W's and R's tooltips pointing to description.league_shaco_backstab.<slot>: "crowd-controlled" swapped
    for "from behind", the shiv's low-health bonus told, the box and the clone told as the units they are.
Every other champion stays untouched. Run it again whenever the main pack's Shaco changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_shaco_backstab")
MOD_ID = "league_shaco_backstab"
HERO = "league_shaco"
TWINS = ("league_shaco_a_bs", "league_shaco_e_bs")
SLOT = "attack"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
AD = "<#ff9028ff>"
# per slot and language: (the main pack's words, ours) pairs, applied in order; {hit} = CLONE_HIT, {takes} = CLONE_TAKES
SWAPS = {
    "skill2": {
        "zh-hans": [("向敌人脚下扔出惊吓魔盒，", "向敌人脚下扔出惊吓魔盒（可被打掉），")],
        "zh-hant": [("向敵人腳下扔出驚嚇魔盒，", "向敵人腳下扔出驚嚇魔盒（可被打掉），")],
        "en": [("Shaco throws a Jack-in-the-Box at an enemy's feet.", "Shaco throws a Jack-in-the-Box (it can be destroyed) at an enemy's feet.")],
        "ko": [("적의 발밑에 깜짝 상자를 던집니다.", "적의 발밑에 깜짝 상자(파괴 가능)를 던집니다.")],
        "ja": [("敵の足元にびっくり箱を投げる。", "敵の足元にびっくり箱（倒せる）を投げる。")],
    },
    "attack": {
        "zh-hans": [("攻击被控制的敌方英雄时", "从背后攻击敌方英雄时"),
                    ("的<#a974ffff>魔法伤害<>并", "的<#a974ffff>魔法伤害<>（目标生命低于" + Y + "{low}%" + E + "时多" + Y + "{more}%" + E + "）并")],
        "zh-hant": [("攻擊被控制的敵方英雄時", "從背後攻擊敵方英雄時"),
                    ("的<#a974ffff>魔法傷害<>並", "的<#a974ffff>魔法傷害<>（目標生命低於" + Y + "{low}%" + E + "時多" + Y + "{more}%" + E + "）並")],
        "en": [("attacks on crowd-controlled enemy champions", "attacks on enemy champions from behind"),
               ("<#a974ffff>magic damage<> and <#ef5350ff>slowing<>",
                "<#a974ffff>magic damage<> (" + Y + "{more}%" + E + " more below " + Y + "{low}%" + E + " health) and <#ef5350ff>slowing<>")],
        "ko": [("군중 제어된 적 챔피언을 공격하면", "적 챔피언을 뒤에서 공격하면"),
               ("<#a974ffff>마법 피해<>를 입히고", "<#a974ffff>마법 피해<>(체력 " + Y + "{low}%" + E + " 미만이면 " + Y + "{more}%" + E + " 증가)를 입히고")],
        "ja": [("行動妨害中の敵チャンピオンへの攻撃は", "敵チャンピオンの背後からの攻撃は"),
               ("の<#a974ffff>魔法ダメージ<>と<#ef5350ff>", "の<#a974ffff>魔法ダメージ<>（体力" + Y + "{low}%" + E + "未満なら" + Y + "{more}%" + E + "増加）と<#ef5350ff>")],
    },
    "ult": {
        "zh-hans": [
            ("在敌方英雄身后召出幻像", "在身旁召出幻像"),
            ("萨科每次攻击时幻像同步背刺，造成", "幻像自己追击、攻击敌人，每下造成" + AD + "{hit}" + E + " + "),
            ("的" + AD + "物理伤害" + E + "。结束或目标死亡时爆炸",
             "的" + AD + "物理伤害" + E + "，受到的伤害提高" + Y + "{takes}%" + E + "，可以被击杀。它阵亡或到时间时爆炸"),
        ],
        "zh-hant": [
            ("在敵方英雄身後召出幻象", "在身旁召出幻象"),
            ("薩科每次攻擊時幻象同步背刺，造成", "幻象自己追擊、攻擊敵人，每下造成" + AD + "{hit}" + E + " + "),
            ("的" + AD + "物理傷害" + E + "。結束或目標死亡時爆炸",
             "的" + AD + "物理傷害" + E + "，受到的傷害提高" + Y + "{takes}%" + E + "，可以被擊殺。它陣亡或到時間時爆炸"),
        ],
        "en": [
            ("a clone appears behind an enemy champion for", "a clone appears beside him for"),
            (E + ", backstabbing it whenever Shaco attacks for ",
             E + ": it chases and attacks enemies on its own for " + AD + "{hit}" + E + " + "),
            (AD + "physical damage" + E + ". When it ends or the target dies it explodes",
             AD + "physical damage" + E + " a hit, takes " + Y + "{takes}%" + E + " more damage and can be killed. When it dies or "
             "its time is up it explodes"),
        ],
        "ko": [
            ("적 챔피언의 뒤에 ", "자신의 곁에 "),
            ("샤코가 공격할 때마다 분신이 함께 찔러 ", "분신은 스스로 적을 쫓아 공격해 한 번에 " + AD + "{hit}" + E + " + "),
            (AD + "물리 피해" + E + "를 입힙니다. 끝나거나 대상이 죽으면 폭발해",
             AD + "물리 피해" + E + "를 입히고, 받는 피해가 " + Y + "{takes}%" + E + " 늘며 처치될 수 있습니다. 분신이 죽거나 끝나면 폭발해"),
        ],
        "ja": [
            ("敵チャンピオンの背後に分身を", "自分のそばに分身を"),
            ("シャコが攻撃するたびに分身も刺し、", "分身は自ら敵を追い攻撃し、1回ごとに" + AD + "{hit}" + E + " + "),
            (AD + "物理ダメージ" + E + "。終了時か対象の死亡時に爆発し",
             AD + "物理ダメージ" + E + "。被ダメージが" + Y + "{takes}%" + E + "増え、倒されることもある。倒されるか時間切れで爆発し"),
        ],
    },
}


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def walk(o):
    """every dict of a tree"""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(float(value.replace("_", "")))
    return out


def clone(champion, c):
    """R asking for its clone as a unit; the natives' numbers (c: src/lib.rs) checked against the main pack's."""
    ult, attack = champion["ult"], champion["attack"]
    eff = ult["effect"]["effects"]

    def buff(name):
        ticks = [x["buff_state"]["duration"]["Time"]["tick"] for x in eff
                 if x.get("type") == "AddCasterBuff" and x["buff_state"]["name"] == name]
        if len(ticks) != 1:
            sys.exit(f"R lays {name} {len(ticks)} times at its cast, not once: update this script")
        return ticks[0]

    riding = [x for x in eff if x.get("type") == "Delayed" and any(y.get("type") == "AddCasted" for y in x["effects"])]
    if len(riding) != 1 or riding[0]["tick"] != 12:
        sys.exit("R's `Delayed 12` with the clone riding on the target changed in the main pack: update this script")
    casted = [y for y in riding[0]["effects"] if y.get("type") == "AddCasted"]
    stabs = {(x["damage"], x["attack_ratio"]) for x in walk(casted) if x.get("type") == "Attack"}

    def zones(kind, stem):
        found = [x for x in walk(ult) if x.get("type") == kind and re.fullmatch(stem, x.get("name", ""))]
        if len(found) != 2:     # the blast when the target dies and the one at the clone's time
            sys.exit(f"R has {len(found)} {kind} named {stem}, not 2: update this script")
        return found

    def one(values, what):
        values = set(values)
        if len(values) != 1:
            sys.exit(f"R's {what} differ between its two ends ({sorted(values)}): update this script")
        return values.pop()

    def hit(zone, kind):
        return one(((e["effect"]["damage"], e["effect"]["attack_ratio"]) for e in zone["applied_effects"]
                    if e["effect"].get("type") == kind), zone["name"] + " hits")

    def fear(zone):
        return one((e["effect"]["tick"] for e in zone["applied_effects"] if e["effect"].get("type") == "Fear"), zone["name"])

    booms = zones("RangeProjectile", r"league_shaco_r_boom(_d)?")
    fear_c = zones("RangeProjectile", r"league_shaco_r_md?_fear_c")
    fear_o = zones("RangeProjectile", r"league_shaco_r_md?_fear_o")
    shots = zones("RangePeriodProjectile", r"league_shaco_r_md?_shots")
    # the plain stab: the attack's start plus the `Delayed` its hit sits in
    plain = [x for x in walk(attack) if x.get("type") == "Delayed" and any(
        y.get("type") == "Attack" and (y["damage"], y["attack_ratio"]) == (0, 100) for y in x["effects"])]
    if len(plain) != 1:
        sys.exit("the attack's plain stab changed in the main pack: update this script")
    boom, shot = one((hit(z, "ApAttack") for z in booms), "blasts"), one((hit(z, "ApAttack") for z in shots), "box shots")
    got = {
        "CLONE_LIFE": buff("league_shaco_r_on"),
        "CLONE_HIT": one((s[0] for s in stabs), "the clone's stabs"),
        "CLONE_HIT_AD": one((s[1] for s in stabs), "the clone's stabs"),
        "CLONE_RANGE": attack["range"],
        "CLONE_COOL": attack["cooltime"],
        "CLONE_ACT": attack["duration"],
        "CLONE_LANDS": attack["start_timing"] + plain[0]["tick"],
        "BOOM": boom[0],
        "BOOM_AP": boom[1],
        "BOOM_R": one((z["shape"]["Circle"]["radius"] for z in booms + fear_c + fear_o), "blast and fear radius"),
        "FEAR_CHAMP": one((fear(z) for z in fear_c), "champions' fear"),
        "FEAR_OTHER": one((fear(z) for z in fear_o), "the others' fear"),
        "BOX_SHOTS": one((z["tick"] // z["period"] for z in shots), "box shots"),
        "BOX_FIRST": one((z["first_delay"] for z in shots), "box shots' first"),
        "BOX_EVERY": one((z["period"] for z in shots), "box shots' period"),
        "BOX_HIT": shot[0],
        "BOX_HIT_AP": shot[1],
        "BOX_R": one((z["shape"]["Circle"]["radius"] for z in shots), "box shots' radius"),
    }
    if casted[0]["duration"] != got["CLONE_LIFE"]:
        sys.exit("the riding clone's AddCasted and league_shaco_r_on differ in the main pack: update this script")
    wrong = {k: (c.get(k), v) for k, v in got.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the clone's numbers differ from src/lib.rs (lib, kit): {wrong}")
    views = {v["name"] for v in champion["view_effects"]}
    kit = json.dumps(champion)
    for k in ("BOOM_VIEW", "BURN_VIEW", "MINI_VIEW", "FEAR_VIEW", "SHOT_VIEW", "APPEAR_VIEW"):
        if c[k] not in views:
            sys.exit(f"src/lib.rs's {k} = {c[k]} is no view effect of the main pack's Shaco")
    for k in ("BOOM_VIEW", "POP_SFX", "APPEAR_SFX"):
        if not re.search(r'"type": "(Target)?Sfx", "name": "' + re.escape(c[k]) + '"', kit):
            sys.exit(f"src/lib.rs's {k} = {c[k]} is no sound the main pack's Shaco plays")
    if c["CLONE_NAME"] != HERO:
        sys.exit("the clone's unit name is not the hero's id: the game would not draw it from his sheet")
    buffs = {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    buffs |= {x.get("name") for x in walk(champion) if x.get("type") == "RemoveCasterBuff"}
    buffs |= {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    if any(c[k] in buffs for k in ("R_ASK", "R_UNIT", "CLONE_BUFF")) or any(str(b).startswith(c["R_UID"]) for b in buffs):
        sys.exit("the main pack's Shaco already uses one of the add-on's buff names: update src/lib.rs")
    # the cast: the flag of an earlier clone off, the ask on; the riding clone only without the flag
    i = eff.index(riding[0])
    ask = [{"type": "RemoveCasterBuff", "name": c["R_UNIT"]},
           {"type": "AddCasterBuff", "buff_state": {"name": c["R_ASK"], "duration": {"Time": {"tick": 3}}}, "only_to_enemy": False}]
    unit = {"type": "SwitchByBuff", "buff_name": c["R_UNIT"], "effect_buff": {"type": "Combine", "effects": []},
            "effect_none": {"type": "Combine", "effects": riding[0]["effects"]}}
    ult["effect"]["effects"] = eff[:i] + ask + [dict(riding[0], effects=[unit])] + eff[i + 1:]


def jack(champion, cj):
    """W's box (0.3.0): the landing asks the add-on for the box's body; the spring's picture and shooting zone play only
    without W_UNIT. The natives' numbers (cj: src/jack.rs) checked against the main pack's W and the unit sheet."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
    import unit_shaco_jack as sheet  # noqa: E402
    throws = [x for x in walk(champion["skill2"]) if x.get("type") == "ParabolicProjectile" and x.get("name") == HERO + "_w_throw"]
    if len(throws) != 1:
        sys.exit("W throws its box more or less than once: update this script")
    end = throws[0]["end_effects"]
    spring = [x for x in end if x.get("type") == "Delayed"]
    if len(spring) != 1:
        sys.exit("the box's spring is no longer one Delayed after its landing: update this script")
    spring = spring[0]
    shots = [x for x in spring["effects"] if x.get("type") == "RangePeriodProjectile" and x.get("name") == HERO + "_w_shots"]
    if len(shots) != 1:
        sys.exit("the box's shooting zone changed: update this script")
    z = shots[0]
    hit = [e["effect"] for e in z["applied_effects"] if e["effect"].get("type") == "ApAttack"]
    act, lands = sheet.shot_lands()
    want = {"W_WAIT": spring["tick"], "W_TIME": z["tick"], "W_EVERY": z["period"], "W_FIRST": z["first_delay"],
            "W_R": z["shape"]["Circle"]["radius"], "W_HIT": hit[0]["damage"] if hit else None,
            "W_HIT_AP": hit[0]["attack_ratio"] if hit else None, "JACK_ACT": act, "JACK_LANDS": lands,
            "W_SHOTS": len(range(z["first_delay"], z["tick"], z["period"]))}
    wrong = {k: (cj.get(k), v) for k, v in want.items() if cj.get(k) != v}
    if wrong:
        sys.exit(f"the box's numbers differ from src/jack.rs (jack.rs, main pack or sheet): {wrong}")
    names = {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    names |= {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    if cj["W_UNIT"] in names or any(str(b).startswith(cj["W_UID"]) for b in names):
        sys.exit("the main pack's Shaco already uses one of the box's buff names: update src/jack.rs")
    only = lambda x: {"type": "SwitchByBuff", "buff_name": cj["W_UNIT"], "effect_buff": {"type": "Combine", "effects": []},  # noqa: E731
                      "effect_none": x}
    wrapped = 0
    for i, x in enumerate(spring["effects"]):
        if (x.get("type") == "ViewEffect" and x.get("name") == HERO + "_w_box") or x is z:
            spring["effects"][i] = only(x)
            wrapped += 1
    if wrapped != 2:
        sys.exit("the box's spring picture or shooting zone is not where this script looks: update it")
    end.insert(0, {"type": "Native", "effect_ref": MOD_ID + ":jack"})


def shiv(champion, c):
    """Two-Shiv Poison (0.3.1): League's shiv deals 50 % more below 30 % of the target's maximum health; the data reads no
    health, so the shiv's hit runs the native league_shaco_backstab:shiv first (it reads the health before the shiv's own
    damage lands). The shiv's numbers (src/lib.rs E_HIT / E_HIT_AP) checked against the main pack's."""
    shivs = [x for x in walk(champion[SLOT]) if x.get("type") == "TargetProjectile" and x.get("name") == HERO + "_e_shiv"]
    if len(shivs) != 1:
        sys.exit("the attack throws its shiv more or less than once: update this script")
    effects = shivs[0]["applied_effects"]
    hits = [e["effect"] for e in effects if e.get("effect", {}).get("type") == "ApAttack"]
    if len(hits) != 1 or (hits[0]["damage"], hits[0]["attack_ratio"]) != (c["E_HIT"], c["E_HIT_AP"]):
        sys.exit(f"the shiv's hit differs from src/lib.rs's E_HIT / E_HIT_AP ({c['E_HIT']}, {c['E_HIT_AP']}): {hits}")
    if (c["E_LOW_PCT"], c["E_LOW_MORE"]) != (30, 50):
        sys.exit("E_LOW_PCT / E_LOW_MORE are League's 30 % / 50 %: update this script if League changed")
    effects.insert(0, {"casting_type": "Targeting", "effect": {"type": "Native", "effect_ref": MOD_ID + ":shiv"}})


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    c = consts(src)
    ask = c["ASK"]
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Shaco has a passive in the main pack now: update this script")
    mark = {"casting_type": "Targeting", "effect": {"type": "AddBuff", "buff_state": {"name": ask, "duration": {"Time": {"tick": 3}}}}}
    twins = []
    champion[SLOT] = replace(champion[SLOT], lambda o: o.get("type") == "TargetProjectile" and o.get("name") in TWINS,
                             lambda o: dict(o, applied_target="EnemyChampion", applied_effects=[mark]), twins)
    hits = {(e["effect"]["damage"], e["effect"]["attack_ratio"]) for t in twins for e in t["applied_effects"]
            if e["effect"].get("type") == "Attack"}
    if sorted(t["name"] for t in twins) != sorted(TWINS) or any(t["applied_target"] != "EnemyChampionInCC" for t in twins)             or len(hits) != 1:
        sys.exit("Shaco's backstab twins changed in the main pack: update this script")
    (base, ad), = hits
    champion["passive"] = {"passive_ref": MOD_ID + ":backstab", "params": {"base": base, "ad": ad}}
    clone(champion, c)
    jack(champion, consts(open(lp(os.path.join(ADDON, "src", "jack.rs")), encoding="utf-8").read()))
    shiv(champion, c)
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    text = {lang: {"description": {MOD_ID: {}}} for lang in main_text}
    for slot, swaps in SWAPS.items():
        champion[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{slot}"
        for lang, tab in main_text.items():
            t = tab["description"][HERO][slot]
            for old, new in swaps[lang]:
                if t.count(old) != 1:
                    sys.exit(f"{lang} {HERO}.{slot}: the main pack's text changed ({old!r} found {t.count(old)} times): "
                             f"update this script")
                t = t.replace(old, new.format(hit=c["CLONE_HIT"], takes=c["CLONE_TAKES"], low=c["E_LOW_PCT"], more=c["E_LOW_MORE"]))
            t = LEAD[lang] + t
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            text[lang]["description"][MOD_ID][slot] = t
    return champion, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    champion, text = build()
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps(text, ensure_ascii=False, indent=2) + "\n"}
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.exists(lp(p)) or open(lp(p), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for p, t in files.items():
        os.makedirs(lp(os.path.dirname(p)), exist_ok=True)
        with open(lp(p), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in files))


if __name__ == "__main__":
    main()
