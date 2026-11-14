"""Build the add-on's copy of Kog'Maw from the main pack (Icathian Surprise as in League: his body a void form that runs at
the nearest enemy champion for 4 s and bursts).

    python addons/league_kogmaw/make_override.py [--check]

Reads the main pack's league/champion/league_kogmaw.data_champion and writes
addons/league_kogmaw/override/league_kogmaw.data_champion and .../text/champion.i18n: the same kit with -
  * in each of the four slots' watch (tools/kit/build_kogmaw.py `wake`), the comet - `RandomTarget {p_seek,
    EnemyChampion}` holding the homing p_form and the hidden splash p_burst - replaced by the add-on's native effect
    league_kogmaw:void (src/lib.rs); the wake's light (p_wake) and its two sounds before it stay, and so does
    everything else of the watch, his attack, Q, W, E and R, byte for byte (the packers' lob wrap, tools/kit/
    attack_self.py, is made from this file at packing as from the main pack's);
  * the splash's numbers checked against src/lib.rs (P_DMG / P_RATIO / P_R / P_SPEED / P_SEEK: the add-on deals them);
  * one more view effect, league_kogmaw_p_void: the burst (league/effects/league_kogmaw_burst, tools/art/
    fx_kogmaw_burst.py); the comet's pictures (p_form, p_boom, p_hit) stay for the add-on's fallback;
  * the add-on's passive league_kogmaw:life (it notes his attack while he lives: his entity is gone once he dies);
  * the attack's tooltip pointing to description.league_kogmaw_addon.attack (the main pack's text, its Icathian Surprise
    sentence the add-on's, five languages).
Every other champion stays untouched. Run it again whenever the main pack's Kog'Maw changes (--check: compare only, CI).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kogmaw")
MOD_ID = "league_kogmaw"
HERO = "league_kogmaw"
TEXT_ID = "league_kogmaw_addon"
SLOTS = ("attack", "skill", "skill2", "ult")
NATIVE = {"type": "Native", "effect_ref": MOD_ID + ":void"}
PASSIVE = {"passive_ref": MOD_ID + ":life", "params": {}}
VIEW = {"type": "Animation", "name": HERO + "_p_void", "anim": "asset/league/effects/league_kogmaw_burst", "tag": "burst",
        "z": 2, "is_follow": False}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
A, E = "<#ffb900ff>", "<>"
# each language's Icathian Surprise in the main pack's attack text: (its lead, the words before the damage, the words
# after it) -> the add-on's words before and after (the damage itself, number and icon, kept as it is)
SURPRISE = {
    "zh-hans": ("<#ff9028ff>来自艾卡西亚的惊喜<>：", "死后虚空之力化身追向附近敌方英雄，爆炸造成", "真实伤害。",
                "死后化身虚空形态" + A + "4秒" + E + "，冲向最近的敌方英雄，碰到或时间到时爆炸，对周围敌人造成", "真实伤害。"),
    "zh-hant": ("<#ff9028ff>來自伊卡西亞的驚喜<>：", "死後虛空之力化身追向附近敵方英雄，爆炸造成", "真實傷害。",
                "死後化身虛空形態" + A + "4秒" + E + "，衝向最近的敵方英雄，碰到或時間到時爆炸，對周圍敵人造成", "真實傷害。"),
    "en": ("<#ff9028ff>Icathian Surprise<>: ", "when he dies his void form chases a nearby enemy champion and bursts for ",
           " true damage.",
           "on death he becomes a void form for " + A + "4s" + E + " that runs at the nearest enemy champion and bursts on "
           "contact or at the end, dealing ", " true damage around it."),
    "ko": ("<#ff9028ff>이케시아식 마무리<>: ", "죽으면 공허의 힘이 가까운 적 챔피언을 쫓아가 터져 ", "의 고정 피해.",
           "죽으면 " + A + "4초" + E + " 동안 공허 형태가 되어 가장 가까운 적 챔피언에게 달려가고, 닿거나 시간이 다 되면 터져 주변 "
           "적에게 ", "의 고정 피해."),
    "ja": ("<#ff9028ff>イカシアの自爆<>：", "死ぬとヴォイドの力が近くの敵チャンピオンを追い爆発し", "の確定ダメージ。",
           "死ぬと" + A + "4秒" + E + "ヴォイド形態となり最も近い敵チャンピオンへ走り、触れるか時間切れで爆発し周囲の敵に",
           "の確定ダメージ。"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {}
    for k in ("P_DMG", "P_RATIO", "P_R", "P_SPEED", "P_SEEK"):
        m = re.search(r"pub const %s: usize = ([\d_]+);" % k, src)
        if not m:
            sys.exit(f"{k} is not a `pub const {k}: usize` in src/lib.rs: update this script")
        out[k] = int(m.group(1).replace("_", ""))
    return out


def wakes(node, out):
    """Every Combine that is the watch's wake: the light, its two sounds, the comet's RandomTarget."""
    if isinstance(node, dict):
        effects = node.get("effects")
        if node.get("type") == "Combine" and isinstance(effects, list) and len(effects) == 4 and \
                [e.get("type") for e in effects] == ["ViewEffect", "Sfx", "Sfx", "RandomTarget"] and \
                effects[0].get("name") == HERO + "_p_wake":
            out.append(node)
        for v in node.values():
            wakes(v, out)
    elif isinstance(node, list):
        for v in node:
            wakes(v, out)
    return out


def check_comet(pick, k):
    """The comet as tools/kit/build_kogmaw.py writes it, with the numbers src/lib.rs deals."""
    want = (k["P_SEEK"], "EnemyChampion", True)
    have = (pick.get("range"), pick.get("casting_target"), pick.get("from_projectile"))
    if have != want:
        sys.exit(f"the main pack's comet looks {have}, src/lib.rs says {want}: update P_SEEK or this script")
    form, splash = pick["effects"]
    if (form.get("type"), form.get("name"), form.get("speed")) != ("TargetProjectile", HERO + "_p_form", k["P_SPEED"]):
        sys.exit(f"the main pack's homing form is not p_form at {k['P_SPEED']}: update P_SPEED or this script")
    if (splash.get("type"), splash.get("name"), splash.get("speed"), splash.get("range")) != \
            ("TargetSplashProjectile", HERO + "_p_burst", k["P_SPEED"], k["P_R"]):
        sys.exit(f"the main pack's splash is not p_burst at {k['P_SPEED']} within {k['P_R']}: update P_R or this script")
    hits = [e["effect"] for e in splash["applied_effects"]]
    fixed = [e for e in hits if e.get("type") == "FixedAttack"]
    if len(fixed) != 1 or (fixed[0]["damage"], fixed[0]["attack_ratio"], fixed[0]["hp_ratio"], fixed[0]["target_hp_ratio"]) != \
            (k["P_DMG"], k["P_RATIO"], 0, 0) or splash.get("applied_target") != "EnemyWithoutTower":
        sys.exit(f"the main pack's splash is not {k['P_DMG']} + {k['P_RATIO']}% AD true damage on EnemyWithoutTower: update "
                 "P_DMG / P_RATIO or this script")


def build():
    k = rust_consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Kog'Maw has a passive in the main pack now: update this script")
    champion = copy.deepcopy(champion)
    for slot in SLOTS:
        found = wakes(champion[slot]["effect"], [])
        if len(found) != 1:
            sys.exit(f"{slot}: {len(found)} wakes in the main pack's watch, not one: update this script")
        check_comet(found[0]["effects"][3], k)
        found[0]["effects"][3] = copy.deepcopy(NATIVE)
    if any(v["name"] == VIEW["name"] for v in champion["view_effects"]):
        sys.exit(f"the main pack has a view {VIEW['name']} now: update this script")
    champion["view_effects"].append(copy.deepcopy(VIEW))
    champion["attack"]["description"] = "#asset/base/text/champion?description." + TEXT_ID + ".attack"
    champion["passive"] = copy.deepcopy(PASSIVE)

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        lead, old_head, old_tail, new_head, new_tail = SURPRISE[lang]
        main = tab["description"][HERO]["attack"]
        at = main.find(lead + old_head)
        if main.count(lead) != 1 or at < 0:
            sys.exit(f"{lang}: the main pack's attack text has no single Icathian Surprise sentence {lead + old_head!r}: "
                     "update this script")
        rest = main[at + len(lead + old_head):]
        if not rest.endswith(old_tail):
            sys.exit(f"{lang}: the main pack's Icathian Surprise does not end with {old_tail!r}: update this script")
        damage = rest[:-len(old_tail)]
        if not damage.startswith("<#f5f5f5ff>%d<>" % k["P_DMG"]) or "%d%%" % k["P_RATIO"] not in damage:
            sys.exit(f"{lang}: the main pack's Icathian Surprise does not read {k['P_DMG']} + {k['P_RATIO']}%: {damage!r}")
        t = LEAD[lang] + main[:at] + lead + new_head + damage + new_tail
        if shown_length(t) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang} attack: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
        texts[lang] = {"attack": t}
    for lang, t in texts.items():
        print(f"{lang} attack:{shown_length(t['attack'])}/{TOOLTIP_MAX[lang]}")
    i18n = {lang: {"description": {TEXT_ID: texts[lang]}} for lang in main_text}
    return [(os.path.join(ADDON, "override", HERO + ".data_champion"), dumps(champion)),
            (os.path.join(ADDON, "text", "champion.i18n"), dumps(i18n))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="only compare the copy with the files (CI)")
    a = ap.parse_args()
    out = build()
    if a.check:
        bad = []
        for path, text in out:
            try:
                with open(lp(path), encoding="utf-8", newline="") as f:
                    have = f.read()
            except FileNotFoundError:
                have = None
            if have is None or have.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
                bad.append(os.path.relpath(path, ROOT))
        if bad:
            sys.exit(f"out of date (python addons/{MOD_ID}/make_override.py): " + ", ".join(bad))
        print(f"{MOD_ID}: the copy is up to date")
        return
    for path, text in out:
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(path)


if __name__ == "__main__":
    main()
