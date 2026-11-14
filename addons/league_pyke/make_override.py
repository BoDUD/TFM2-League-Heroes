"""Build the add-on's copy of Pyke from the main pack (R cast only on a champion it kills, the exact execute).

    python addons/league_pyke/make_override.py

Rebuilds Pyke with tools/kit/build_pyke.py (its parameter table P), checks that it is the main pack's
league/champion/league_pyke.data_champion (so the copy never drifts from the shipped kit) and that src/lib.rs's
R_DMG / R_RATIO / R_RANGE are P's r_dmg / r_ratio / r_range, and writes addons/league_pyke/override/
league_pyke.data_champion and .../text/champion.i18n: the same kit with three changes -
  * in the X's champion zone (league_pyke_r_x_c) the threshold's true damage and the heal back a tick later become one
    `Native` league_pyke:execute (it reads the health: at or under the threshold executed, else half of it), and the
    data's kill check (k_r, the blink, the reset) goes: league_pyke:after does them K_READ ticks later (the native
    damage lands at the end of its tick, so the data's check saw the target alive and called the blink off);
  * R's casting_target is EnemyChampion (the add-on's AI hook league_pyke:ult decides whom: only a champion the X
    kills; the main pack's EnemyChampionRecentlyAttacked was its stand-in for "wounded");
  * R's tooltip points to description.league_pyke.ult (an "exact execute test build" lead, so the tooltip in game
    shows whether the override took);
  * the grey health as League's (2026-11-14): the copy is build_pyke.py's native=1 build - no hit sensor, no grey levels,
    no data heal (attack, W, R) - with passive = league_pyke:grey (src/lib.rs's Grey, params p_share p_crowd p_near
    p_cap), and the attack's tooltip (the passive) is description.league_pyke.attack.
Every other champion stays untouched. Run it again whenever the main pack's Pyke changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_pyke")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_pyke as kit  # noqa: E402
import hide_aim_twins  # noqa: E402

MOD_ID = "league_pyke"
HERO = "league_pyke"
TEXT_KEY = "description.league_pyke.ult"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
A, W, R, E = "<#ffb900ff>", "<#ffffffff>", "<#ff5050ff>", "<>"
TRU = A + "{r_dmg}" + E + " + " + ADi + A + "{r_ratio}%" + E
TEXT = {
    "zh-hans": "【精确斩杀测试版】只对斩得死的英雄出手。X形打击：生命不高于" + TRU + "的英雄" + R + "被处决" + E + "，其余受到一半的" + W +
               "真实伤害" + E + "。英雄死在X里，派克闪到那里并" + A + "刷新大招" + E + "。",
    "zh-hant": "【精確斬殺測試版】只對斬得死的英雄出手。X形打擊：生命不高於" + TRU + "的英雄" + R + "被處決" + E + "，其餘受到一半的" + W +
               "真實傷害" + E + "。英雄死在X裡，派克閃到那裡並" + A + "刷新大招" + E + "。",
    "en": "[Exact execute test build] Cast only on a champion it kills. Strikes an X: champions at or below " + TRU + " health are " +
          R + "executed" + E + ", the rest take half of it as " + W + "true damage" + E + ". A champion dying in the X blinks him to it and " +
          A + "refreshes the ult" + E + ".",
    "ko": "[정밀 처형 테스트판] 처형할 수 있는 챔피언에게만 사용. X자 타격: 체력이 " + TRU + " 이하인 챔피언은 " + R + "처형" + E +
          ", 나머지는 그 절반의 " + W + "고정 피해" + E + ". X 안에서 챔피언이 죽으면 그곳으로 이동하고 " + A + "궁극기 초기화" + E + ".",
    "ja": "【精密処刑テスト版】処刑できるチャンピオンにだけ使う。X字の斬撃：体力" + TRU + "以下のチャンピオンは" + R + "処刑" + E +
          "、残りはその半分の" + W + "確定ダメージ" + E + "。X内でチャンピオンが死ぬとそこへ移動し" + A + "アルティメット再使用" + E + "。",
}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
# the copy's attack text (the passive): League's grey health, src/lib.rs's Grey
O, G = "<#ff9028ff>", "<#66bb6aff>"
PASSIVE = {
    "zh-hans": "【附加包】鱼叉挥砍。被动" + O + "溺水之幸" + E + "：英雄打他的伤害存下{p_share}%成灰血（身边有2个以上敌方英雄时{p_crowd}%），"
               "最多最大生命{p_cap}%；敌人看不见他时（草丛、W潜行）迅速" + G + "回成生命" + E + "，阵亡清零。无法靠生命成长，攻击力成长更高。",
    "zh-hant": "【擴充包】魚叉揮砍。被動" + O + "血港淹禮" + E + "：英雄打他的傷害存下{p_share}%成灰血（身邊有2個以上敵方英雄時{p_crowd}%），"
               "最多最大生命{p_cap}%；敵人看不見他時（草叢、W潛行）迅速" + G + "回成生命" + E + "，陣亡清零。無法靠生命成長，攻擊力成長更高。",
    "en": "[Add-on] Harpoon slashes. Passive " + O + "Gift of the Drowned Ones" + E + ": {p_share}% of the damage champions deal "
          "him is stored as grey health ({p_crowd}% with two or more enemy champions near), up to {p_cap}% of his maximum "
          "health; while enemies cannot see him (brush, W's camouflage) it quickly " + G + "heals him" + E + "; lost at death. "
          "Little health growth, more AD growth.",
    "ko": "[확장] 작살 공격. 기본 지속 효과 " + O + "가라앉은 자들의 축복" + E + ": 챔피언에게 받은 피해의 {p_share}%를 회색 체력으로 "
          "저장(적 챔피언 2명 이상 근처면 {p_crowd}%), 최대 체력의 {p_cap}%까지; 적에게 보이지 않으면(수풀, W 위장) 빠르게 " + G +
          "체력 회복" + E + ", 사망 시 소멸. 체력 성장 낮음, 공격력 성장 높음.",
    "ja": "【拡張】銛で斬る。パッシブ " + O + "沈みし者の力" + E + "：チャンピオンからのダメージの{p_share}%をグレー体力に（敵2体以上が"
          "近いと{p_crowd}%）、最大体力の{p_cap}%まで；敵に見えないとき（茂み、Wの擬態）素早く" + G + "回復" + E + "、デスで消える。"
          "体力成長は低く攻撃力成長は高い。",
}


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def consts():
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        src = f.read()
    out = {}
    for name in ("R_DMG", "R_RATIO", "R_RANGE", "SURVIVE", "K_READ"):
        m = re.search(r"pub const %s: usize = ([0-9_]+);" % name, src)
        if not m:
            sys.exit("no %s in src/lib.rs: update this script" % name)
        out[name] = int(m.group(1).replace("_", ""))
    return out


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def main():
    p = dict(kit.P)
    c = consts()
    want = {"R_DMG": p["r_dmg"], "R_RATIO": p["r_ratio"], "R_RANGE": p["r_range"], "SURVIVE": 50, "K_READ": p["k_read"]}
    if c != want:
        sys.exit("src/lib.rs %s differs from build_pyke.P %s: update the constants" % (c, want))
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        shipped = json.load(f)
    if json.loads(json.dumps(hide_aim_twins.hide(kit.build(p)))) != shipped:
        sys.exit("the main pack's league_pyke differs from build_pyke.P: rebuild it first")
    # the copy: League's grey health is the passive's (no sensor, no levels, no data heal)
    champion = hide_aim_twins.hide(kit.build(dict(p, native=1)))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":grey" or HERO + "_sense" in json.dumps(champion):
        sys.exit("the native build must hand the grey health to league_pyke:grey (no league_pyke_sense): update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    ult = champion["ult"]
    zones = [nd for nd in walk(ult) if nd.get("type") == "RangeProjectile" and nd.get("name") == HERO + "_r_x_c"]
    if len(zones) != 1:
        sys.exit("expected one champion zone r_x_c in R, found %d: update this script" % len(zones))
    applied = zones[0]["applied_effects"]
    eff = [a["effect"] for a in applied]
    true_hits = [i for i, e in enumerate(eff) if e.get("type") == "FixedAttack"]
    heals = [i for i, e in enumerate(eff) if e.get("type") == "Delayed" and e.get("tick") == 1
             and any(n.get("type") == "Heal" and n.get("heal_type") == "Any" for n in walk(e))]
    if len(true_hits) != 1 or len(heals) != 1:
        sys.exit("R's champion hit changed shape (one FixedAttack, one Delayed 1 Heal Any): update this script")
    hit = eff[true_hits[0]]
    if (hit["damage"], hit["attack_ratio"]) != (p["r_dmg"], p["r_ratio"]):
        sys.exit("R's threshold is not r_dmg + r_ratio% AD any more: update src/lib.rs")
    # the data's kill check (league_jinx's: k_r set, kept while the target is dead, then Teleport and the reset): the
    # native damage lands at the end of the tick, so the check saw him alive and called the blink off - the add-on's
    # league_pyke:after blinks and resets instead
    kill = [i for i, e in enumerate(eff) if HERO + "_k_r" in json.dumps(e)]
    if len(kill) != 4:
        sys.exit("R's kill check changed shape (k_r set, kept, Teleport, reset - %d found): update this script" % len(kill))
    for name in (HERO + "_r_reset", HERO + "_vo_r"):
        if name not in json.dumps(ult):
            sys.exit("%s is not in R any more: update src/lib.rs (after)" % name)
    native = {"casting_type": "Targeting", "effect": {"type": "Native", "effect_ref": MOD_ID + ":execute"}}
    drop = set(kill) | {heals[0]}
    zones[0]["applied_effects"] = [native if i == true_hits[0] else a for i, a in enumerate(applied) if i not in drop]
    if ult["casting_target"] != "EnemyChampionRecentlyAttacked":
        sys.exit("R's casting target changed: update this script")
    ult["casting_target"] = "EnemyChampion"
    ult["description"] = "#asset/base/text/champion?" + TEXT_KEY

    values = {"r_dmg": p["r_dmg"], "r_ratio": p["r_ratio"]}
    texts = {lang: t.format(**values) for lang, t in TEXT.items()}
    attacks = {lang: t.format(**{k: p[k] for k in ("p_share", "p_crowd", "p_cap")}) for lang, t in PASSIVE.items()}
    long = {f"{lang}.{k}": shown_length(t) for k, tab in (("ult", texts), ("attack", attacks)) for lang, t in tab.items()
            if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no exact-execute text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"attack": attacks[lang], "ult": texts[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT),
          "- R on EnemyChampion, the X's champion hit =", native["effect"]["effect_ref"], "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{shown_length(t)}/{TOOLTIP_MAX[lang]}"
                              for k, tab in (("ult", texts), ("attack", attacks)) for lang, t in tab.items()})


if __name__ == "__main__":
    main()
