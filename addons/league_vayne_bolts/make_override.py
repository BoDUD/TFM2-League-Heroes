"""Build the add-on's copy of Vayne from the main pack (Silver Bolts counted on each target).

    python addons/league_vayne_bolts/make_override.py

Reads the main pack's league/champion/league_vayne.data_champion and writes addons/league_vayne_bolts/override/
league_vayne.data_champion and .../text/champion.i18n, the same kit with four changes:
  * every Silver Bolts ladder (a SwitchByBuff league_vayne_sb2 -> the proc, else sb1 -> the second ring, else the first:
    the attack's bolt, the empowered Tumble bolt, Condemn) becomes the Native league_vayne_bolts:bolt on the unit hit -
    it counts the stacks on THAT unit and adds one 3-tick caster flag: sb_go (the third hit), sb_r2 or sb_r1 - then the
    data reads the flag in the same tick and, if none was there yet, a tick later: sb_go -> the ladder's own proc
    (the flat true damage, sb_proc, the burst picture and sound), sb_r2 / sb_r1 -> the ring pictures;
  * sb_proc lasts 3 ticks and the champion twin reads it 2 ticks after the hit (the % max health part), so it is found
    whether the proc came in the hit's tick or a tick later;
  * the attack's tooltip points to description.league_vayne_bolts.attack ("test build" lead, "on the same target");
  * Condemn: the heavy bolt's Knockback becomes the Native league_vayne_bolts:condemn (it looks for a wall behind the
    target, pushes it to the wall and sets the caster flag league_vayne_e_wall, or knocks it back as the data did) and
    the landing's damage and stun (the Delayed at the knockback's last tick) only come with that flag; the tooltip
    points to description.league_vayne_bolts.skill2 ("only on a wall"). The Knockback's speed and ticks must be the
    add-on's E_KB_SPEED / E_KB_T (src/lib.rs), and its start, bolt speed and range E_START / E_BOLT_SPEED / E_RANGE (the AI
    hook aims with them), or the script stops.
Every other champion stays untouched. Run it again whenever the main pack's Vayne changes.
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_vayne_bolts")
MOD_ID = "league_vayne_bolts"
HERO = "league_vayne"
N = HERO + "_"
# lang -> (lead, the main pack's words for "3 hits in a row", the add-on's "3 hits in a row on the same target")
TEXT = {
    "zh-hans": ("【圣银弩箭测试版】", "内连续第", "内对同一目标连续第"),
    "zh-hant": ("【聖銀弩箭測試版】", "內連續第", "內對同一目標連續第"),
    "en": ("[Silver Bolts test build] ", "hit in a row", "hit in a row on the same target"),
    "ko": ("[은화살 테스트판] ", "안에 연속", "안에 같은 대상에게 연속"),
    "ja": ("【シルバーボルトテスト版】", "以内の連続", "以内に同じ相手への連続"),
}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
# lang -> [(the main pack's words, the add-on's)] in Condemn's tooltip: the landing's damage and stun only on a wall
CONDEMN_TEXT = {
    "zh-hans": [("，落地时再受到", "；撞到墙（地图的墙、5v5 地图的四边）才再受到"),
                ("<#ffb900ff>1秒<>。", "<#ffb900ff>1秒<>，没撞墙只击退。")],
    "zh-hant": [("，落地時再受到", "；撞到牆（地圖的牆、5v5 地圖的四邊）才再受到"),
                ("<#ffb900ff>1秒<>。", "<#ffb900ff>1秒<>，沒撞牆只擊退。")],
    "en": [("; where it lands it takes", "; only if it hits a wall (the map's walls, the 5v5 map's edges) it takes"),
           ("for <#ffb900ff>1s<>.", "for <#ffb900ff>1s<>. No wall, no stun.")],
    "ko": [(". 떨어진 곳에서", ". 벽(지도의 벽, 5v5 지도의 가장자리)에 부딪혀야"),
           ("<#ef5350ff>기절<>.", "<#ef5350ff>기절<>. 벽이 없으면 밀쳐내기만 합니다.")],
    "ja": [("。着地で", "。壁（マップの壁、5v5マップの端）にぶつかった時だけ"),
           ("<#ef5350ff>スタン<>。", "<#ef5350ff>スタン<>。壁がなければノックバックのみ。")],
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": N + buff, "effect_buff": yes,
            "effect_none": no or {"type": "Combine", "effects": []}}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": N + name}


def rust_const(name):
    """A `pub const NAME: usize = 3_000;` of the add-on's src/lib.rs."""
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        m = re.search(r"pub const " + name + r": usize = ([0-9_]+);", f.read())
    if not m:
        sys.exit(f"src/lib.rs has no {name}: update this script")
    return int(m.group(1).replace("_", ""))


def condemn(champion):
    """Condemn's Knockback -> the add-on's wall check; the landing's damage and stun wait for its caster flag."""
    bolts = []

    def bolt(o):
        if o.get("type") == "TargetProjectile" and o.get("name") == N + "e_bolt":
            bolts.append(o)

    walk(champion["skill2"]["effect"], bolt)
    if len(bolts) != 1:
        sys.exit(f"found {len(bolts)} Condemn bolts: update this script")
    applied = [a["effect"] for a in bolts[0]["applied_effects"]]
    pushes = [e for e in applied if e.get("type") == "Knockback"]
    lands = [e for e in applied if e.get("type") == "Delayed" and any(x.get("type") == "Stun" for x in e["effects"])]
    if len(pushes) != 1 or len(lands) != 1:
        sys.exit(f"Condemn has {len(pushes)} knockbacks and {len(lands)} stunning landings: update this script")
    push, land = pushes[0], lands[0]
    # the AI hook's numbers (src/ai.rs: when the bolt lands, whom E reaches)
    aim = (champion["skill2"]["start_timing"], bolts[0]["speed"], champion["skill2"]["range"])
    if aim != (rust_const("E_START"), rust_const("E_BOLT_SPEED"), rust_const("E_RANGE")):
        sys.exit(f"Condemn's start / bolt speed / range {aim} are not src/lib.rs's E_START / E_BOLT_SPEED / E_RANGE: update them")
    speed, ticks = rust_const("E_KB_SPEED"), rust_const("E_KB_T")
    if (push["speed"], push["tick"], land["tick"]) != (speed, ticks, ticks):
        sys.exit(f"Condemn pushes {push['speed']} x {push['tick']} and lands at tick {land['tick']}, src/lib.rs says "
                 f"{speed} x {ticks}: update E_KB_SPEED / E_KB_T")
    push.clear()
    push.update({"type": "Native", "effect_ref": MOD_ID + ":condemn"})
    land["effects"] = [sw("e_wall", combine(rm("e_wall"), *land["effects"]))]
    champion["skill2"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".skill2"


def without_sb(branch):
    """The branch's effects minus its own sb1/sb2 bookkeeping (the stacks are on the target now)."""
    effs = branch["effects"] if branch.get("type") == "Combine" else [branch]
    out = []
    for e in effs:
        if e.get("type") == "RemoveCasterBuff" and e["name"] in (N + "sb1", N + "sb2"):
            continue
        if e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] in (N + "sb1", N + "sb2"):
            continue
        out.append(copy.deepcopy(e))
    return out


def main():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)

    ladders = []

    def ladder(o):
        if o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "sb2":
            ladders.append(o)

    for slot in ("attack", "skill", "skill2", "ult"):
        walk(champion[slot]["effect"], ladder)
    ladders = list({id(x): x for x in ladders}.values())
    if len(ladders) < 2:
        sys.exit(f"found only {len(ladders)} Silver Bolts ladders: update this script")
    for o in ladders:
        proc = without_sb(o["effect_buff"])
        for e in proc:
            if e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == N + "sb_proc":
                e["buff_state"]["duration"] = {"Time": {"tick": 3}}
        two = o["effect_none"]
        if two.get("buff_name") != N + "sb1":
            sys.exit("a ladder without the sb1 rung: update this script")
        ring2, ring1 = without_sb(two["effect_buff"]), without_sb(two["effect_none"])

        def chain(last):
            return sw("sb_go", combine(rm("sb_go"), *copy.deepcopy(proc)),
                      sw("sb_r2", combine(rm("sb_r2"), *copy.deepcopy(ring2)),
                         sw("sb_r1", combine(rm("sb_r1"), *copy.deepcopy(ring1)), last)))

        new = combine({"type": "Native", "effect_ref": MOD_ID + ":bolt"},
                      chain({"type": "Delayed", "tick": 1, "effects": [chain(None)]}))
        o.clear()
        o.update(new)

    twins = []

    def twin(o):
        if o.get("type") == "Delayed" and o.get("tick") == 1 and any(
                e.get("type") == "SwitchByBuff" and e.get("buff_name") == N + "sb_proc" for e in o.get("effects", [])):
            twins.append(o)

    for slot in ("attack", "skill", "skill2", "ult"):
        walk(champion[slot]["effect"], twin)
    for o in {id(x): x for x in twins}.values():
        o["tick"] = 2
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    condemn(champion)

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang in main_text:
        lead, old, new = TEXT[lang]
        attack = main_text[lang]["description"][HERO]["attack"]
        if old is not None:
            if attack.count(old) != 1:
                sys.exit(f"{lang}: the main pack's Silver Bolts text changed ({old!r} not found once): update TEXT")
            attack = attack.replace(old, new)
        skill2 = main_text[lang]["description"][HERO]["skill2"]
        for old2, new2 in CONDEMN_TEXT[lang]:
            if skill2.count(old2) != 1:
                sys.exit(f"{lang}: the main pack's Condemn text changed ({old2!r} not found once): update CONDEMN_TEXT")
            skill2 = skill2.replace(old2, new2)
        texts[lang] = {"attack": lead + attack, "skill2": skill2}
    long = {f"{lang} {k}": shown_length(t) for lang, d in texts.items() for k, t in d.items()
            if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), f"- {len(ladders)} ladders ask",
          f"{MOD_ID}:bolt, {len(twins)} twin reads moved to tick 2, Condemn asks {MOD_ID}:condemn")
    print("tooltip lengths", {f"{lang} {k}": f"{shown_length(t)}/{TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
