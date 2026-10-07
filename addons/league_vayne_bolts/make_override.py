"""Build the add-on's copy of Vayne from the main pack (Silver Bolts counted on each target).

    python addons/league_vayne_bolts/make_override.py

Reads the main pack's league/champion/league_vayne.data_champion and writes addons/league_vayne_bolts/override/
league_vayne.data_champion and .../text/champion.i18n, the same kit with three changes:
  * every Silver Bolts ladder (a SwitchByBuff league_vayne_sb2 -> the proc, else sb1 -> the second ring, else the first:
    the attack's bolt, the empowered Tumble bolt, Condemn) becomes the Native league_vayne_bolts:bolt on the unit hit -
    it counts the stacks on THAT unit and adds one 3-tick caster flag: sb_go (the third hit), sb_r2 or sb_r1 - then the
    data reads the flag in the same tick and, if none was there yet, a tick later: sb_go -> the ladder's own proc
    (the flat true damage, sb_proc, the burst picture and sound), sb_r2 / sb_r1 -> the ring pictures;
  * sb_proc lasts 3 ticks and the champion twin reads it 2 ticks after the hit (the % max health part), so it is found
    whether the proc came in the hit's tick or a tick later;
  * the attack's tooltip points to description.league_vayne_bolts.attack ("test build" lead, "on the same target").
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
        texts[lang] = lead + attack
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), f"- {len(ladders)} ladders ask",
          f"{MOD_ID}:bolt, {len(twins)} twin reads moved to tick 2")
    print("tooltip lengths", {lang: f"{shown_length(t)}/{TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
