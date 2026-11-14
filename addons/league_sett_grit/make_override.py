"""Build the add-on's copy of Sett from the main pack (Grit from the damage he takes).

    python addons/league_sett_grit/make_override.py [--check]

Reads the main pack's league/champion/league_sett.data_champion and writes
addons/league_sett_grit/override/league_sett.data_champion and .../text/champion.i18n: the same kit with -
  * W's Grit ladder (SwitchByBuff league_sett_grit_5 .. 1 around six shields and true-damage lines) down to its last
    step (no Grit: the 50 + 20% AD shield, the 30 + 30% AD true damage) plus an AddCasterBuff of src/lib.rs's SPEND;
    that step's two middle lines (league_sett_w_true_0 / _truew_0) also put HIT (3 ticks) on whom they strike;
  * the passive league_sett_grit:grit (Grit = the damage of the last 4 s, up to cap% of max health; the shield adds it,
    the middle adds true% of it as true damage);
  * W's tooltip pointing to description.league_sett_grit.skill2: the Grit sentences swapped;
  * E (0.1.2, League: "If Facebreaker affects at least one enemy on each side, all enemies are stunned"): the "two or
    more pulled in" count (league_sett_e_one / e_two) gone, the stun's switch reads src/lib.rs's BOTH instead, set by
    the native effect SIDES one tick before the grab (enemies he pulls more than 90 degrees apart as seen from him);
    E's tooltip pointing to description.league_sett_grit.skill with "both sides" for "two or more".
Every other champion stays untouched. Run it again whenever the main pack's Sett changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_sett_grit")
MOD_ID = "league_sett_grit"
HERO = "league_sett"
PARAMS = {"cap": 50, "true": 25}
SLOT = "skill2"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
Y, E = "<#ffb900ff>", "<>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
G = "<#e8d44dff>"
# E's text (0.1.2): lang -> [(the main pack's phrase, the add-on's)]: "two or more" -> "both sides", "one" -> "otherwise"
# (en: "of the target's max health" shortened to fit)
E_SWAPS = {
    "zh-hans": [("拉到两个及以上时", "两侧都拉到人时")],
    "zh-hant": [("拉到兩個以上時", "兩側都拉到人時")],
    "en": [("two or more are <#ef5350ff>stunned<> for <#ffb900ff>1s<>, one is <#ef5350ff>slowed<>",
            "with enemies on both sides all are <#ef5350ff>stunned<> for <#ffb900ff>1s<>, else <#ef5350ff>slowed<>"),
           ("<#ffb900ff>4%<> of the target's max health more", "<#ffb900ff>4%<> of max health more")],
    "ko": [("둘 이상 끌어오면", "양쪽에서 끌어오면")],
    "ja": [("2体以上なら全員", "両側からなら全員"), ("、1体なら", "、片側なら")],
}
# lang -> (the stacks phrase, the add-on's), (the per-level sentence's start: cut to the end, the add-on's sentence)
SWAPS = {
    "zh-hans": (("受伤积攒" + G + "豪意" + E + "（最多" + Y + "5" + E + "层，" + Y + "4秒" + E + "消散）",
                 "受到的伤害积攒为" + G + "豪意" + E + "（最多" + Y + "50%" + E + "最大生命，" + Y + "4秒" + E + "消散）"),
                ("每层豪意护盾", "护盾再加上全部豪意，正中的真伤再加" + Y + "25%" + E + "豪意。")),
    "zh-hant": (("受傷累積" + G + "拳皇恆毅" + E + "（最多" + Y + "5" + E + "層，" + Y + "4秒" + E + "消散）",
                 "受到的傷害累積為" + G + "拳皇恆毅" + E + "（最多" + Y + "50%" + E + "最大生命，" + Y + "4秒" + E + "消散）"),
                ("每層拳皇恆毅護盾", "護盾再加上全部拳皇恆毅，正中的真傷再加" + Y + "25%" + E + "拳皇恆毅。")),
    "en": (("gains a level of " + G + "Grit" + E + " while taking damage (up to " + Y + "5" + E + ", lost after " + Y + "4s" + E + ")",
            "stores the damage he takes as " + G + "Grit" + E + " (up to " + Y + "50%" + E + " max health, lost after " + Y + "4s" + E + ")"),
           ("Each level of Grit adds", "The shield also adds all his Grit, the middle's true damage " + Y + "25%" + E + " of it.")),
    "ko": (("피해를 받으면 " + G + "투지" + E + "가 쌓입니다(최대 " + Y + "5" + E + ", " + Y + "4초" + E + " 후 소멸)",
            "받은 피해가 " + G + "투지" + E + "로 쌓입니다(최대 체력의 " + Y + "50%" + E + ", " + Y + "4초" + E + " 후 소멸)"),
           ("투지 1당", "보호막에 투지 전부, 중앙 고정 피해에 투지의 " + Y + "25%" + E + " 추가.")),
    "ja": (("被ダメージで" + G + "闘魂" + E + "を蓄積（最大" + Y + "5" + E + "、" + Y + "4秒" + E + "で消滅）",
            "受けたダメージを" + G + "闘魂" + E + "として蓄積（最大体力の" + Y + "50%" + E + "まで、" + Y + "4秒" + E + "で消滅）"),
           ("闘魂1につき", "シールドに闘魂すべて、中央の確定に闘魂の" + Y + "25%" + E + "を追加。")),
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


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def facebreaker(champion, sides, both, radius):
    """E: the stun by the native's BOTH instead of the "two or more" count, the native one tick before the grab."""
    s = champion["skill"]
    if (s["casting_type"], s["effect"].get("type")) != ("None", "Combine"):
        sys.exit("E is no longer an untargeted Combine: update this script")
    top = s["effect"]["effects"]
    grabs = [x for x in top if x.get("type") == "Delayed"
             and any(y.get("buff_name") == "league_sett_r_combo" for y in x["effects"])]
    if len(grabs) != 1:
        sys.exit("E's grab (the Delayed with the r_combo switch) changed: update this script")
    grab = grabs[0]
    count = [y for y in grab["effects"] if y.get("type") == "RangeEffect" and "league_sett_e_one" in json.dumps(y)]
    combo = [y for y in grab["effects"] if y.get("buff_name") == "league_sett_r_combo"][0]
    by_count = combo["effect_none"]
    if (len(count) != 1 or count[0]["target"] != "EnemyWithoutTower" or count[0]["shape"]["Circle"]["radius"] != radius
            or by_count.get("type") != "SwitchByBuff" or by_count.get("buff_name") != "league_sett_e_two"):
        sys.exit("E's count of the pulled (e_one / e_two, the RangeEffect's radius = src/lib.rs's E_RADIUS) changed: update this script")
    pulls = [x for x in (by_count["effect_buff"], by_count["effect_none"]) for x in [x] if "Grab" in json.dumps(x)]
    if len(pulls) != 2 or any(f'"radius": {radius}' not in json.dumps(x) for x in pulls):
        sys.exit("E's stun / slow branches no longer pull within E_RADIUS: update this script")
    grab["effects"].remove(count[0])
    by_count["buff_name"] = both
    top.insert(top.index(grab), {"type": "Delayed", "tick": grab["tick"] - 1,
                                 "effects": [{"type": "Native", "effect_ref": sides}]})
    if "league_sett_e_one" in json.dumps(champion) or "league_sett_e_two" in json.dumps(champion):
        sys.exit("league_sett_e_one / e_two still read somewhere: update this script")
    s["description"] = "#asset/base/text/champion?description." + MOD_ID + ".skill"


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    spend, hit, sides, both = (re.search(r'pub const ' + k + r': &str = "([^"]+)";', src).group(1)
                               for k in ("SPEND", "HIT", "SIDES", "BOTH"))
    radius = int(re.search(r"pub const E_RADIUS: u64 = ([\d_]+);", src).group(1).replace("_", ""))
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Sett has a passive in the main pack now: update this script")
    mark = {"casting_type": "Targeting", "effect": {"type": "AddBuff", "buff_state": {"name": hit, "duration": {"Time": {"tick": 3}}}}}

    def last_step(o):
        n = 0
        while o.get("type") == "SwitchByBuff" and o.get("buff_name", "").startswith("league_sett_grit_"):
            o, n = o["effect_none"], n + 1
        if n != 5:
            sys.exit(f"W's Grit ladder has {n} steps, not 5: update this script")
        lines = []
        o = replace(o, lambda x: x.get("type") == "LineRangeProjectile" and x.get("name") in ("league_sett_w_true_0", "league_sett_w_truew_0"),
                    lambda x: dict(x, applied_effects=x["applied_effects"] + [mark]), lines)
        shields = [x for x in o["effects"] if x.get("type") == "RangeEffect" and "Shield" in json.dumps(x)]
        if len(lines) != 2 or len(shields) != 1:
            sys.exit("W's last Grit step changed (two middle lines, one shield): update this script")
        return {"type": "Combine", "effects": o["effects"] + [
            {"type": "AddCasterBuff", "buff_state": {"name": spend, "duration": {"Time": {"tick": 3}}}, "only_to_enemy": False}]}

    ladders = []
    champion[SLOT] = replace(champion[SLOT], lambda o: o.get("type") == "SwitchByBuff" and o.get("buff_name") == "league_sett_grit_5",
                             last_step, ladders)
    if len(ladders) != 1:
        sys.exit(f"W's Grit ladder ({len(ladders)} found) changed: update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":grit", "params": PARAMS}
    champion[SLOT]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    facebreaker(champion, sides, both, radius)
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts, e_texts = {}, {}
    for lang, tab in main_text.items():
        (old, new), (cut, tail) = SWAPS[lang]
        t = tab["description"][HERO][SLOT]
        if old not in t or cut not in t:
            sys.exit(f"{lang} {HERO}.{SLOT}: the main pack's text changed: update this script")
        texts[lang] = LEAD[lang] + t.replace(old, new)[:t.replace(old, new).index(cut)] + tail
        e = tab["description"][HERO]["skill"]
        for e_old, e_new in E_SWAPS[lang]:
            if e.count(e_old) != 1:
                sys.exit(f"{lang} {HERO}.skill: the main pack's text changed: update this script")
            e = e.replace(e_old, e_new)
        e_texts[lang] = LEAD[lang] + e
        for slot, t in ((SLOT, texts[lang]), ("skill", e_texts[lang])):
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
    text = {lang: {"description": {MOD_ID: {"skill": e_texts[lang], SLOT: texts[lang]}}} for lang in main_text}
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
