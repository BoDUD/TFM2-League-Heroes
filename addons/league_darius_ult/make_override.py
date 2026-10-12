"""Build the add-on's copy of Darius from the main pack (R cast only for a kill or under Noxian Might).

    python addons/league_darius_ult/make_override.py

Darius has no kit script: his kit is the main pack's league/champion/league_darius.data_champion itself. This reads
it, checks that src/plan.rs's numbers are the kit's -
  * R_TIERS: the six FixedAttacks of R's damage ladder (no stacks, hemo_1..hemo_4, Noxian Might), in that order;
  * MIGHT / HEMO: the caster buffs the ladder's SwitchByBuffs read, top down (might, hemo_4 .. hemo_1);
  * MIGHT_ATTACK_MULT: the attack_mult every AddCasterBuff of the might buff gives;
  * R_RANGE: R's range; R_LAND: R's start_timing + the Delayed ticks above the ladder (when the blow lands);
  * R's casting target is still EnemyChampionRecentlyAttacked (the AI's cue that a fight is on) -
and writes addons/league_darius_ult/override/league_darius.data_champion and .../text/champion.i18n: the same kit
with one change, R's tooltip pointing to description.league_darius_ult.ult (a "test build" lead, so the tooltip in
game shows whether the override took; the AI hook league_darius_ult:ult decides when R goes). Every other champion
stays untouched. Run it again whenever the main pack's Darius changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_darius_ult")

MOD_ID = "league_darius_ult"
HERO = "league_darius"
TEXT_KEY = "description.league_darius_ult.ult"
CASTING_TARGET = "EnemyChampionRecentlyAttacked"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
O, W, Y = "<#ff9028ff>", "<#f5f5f5ff>", "<#ffb900ff>"
E = "<>"
# {b} + {r}% AD true damage, +{s}% per hit in the last {w} s, doubled ({x}x) under Might
TEXT = {
    "zh-hans": "【大招读血测试版】" + O + "诺克萨斯断头台" + E + "：德莱厄斯跃向一名敌方英雄猛力劈下，造成" + W + "{b}" + E + " + " + ADi +
               O + "{r}% 攻击力" + E + "的" + W + "真实伤害" + E + "。" + Y + "{w}秒" + E + "内每命中敌方英雄一次，伤害提高" + Y + "{s}%" + E +
               "；" + O + "诺克萨斯之力" + E + "时翻倍。击杀则刷新大招。只在一刀砍得死射程内的英雄、或" + O + "诺克萨斯之力" + E + "期间释放。",
    "zh-hant": "【大招讀血測試版】" + O + "諾克薩斯斷頭台" + E + "：達瑞斯躍向一位敵方英雄猛力劈下，造成" + W + "{b}" + E + " + " + ADi +
               O + "{r}% 攻擊力" + E + "的" + W + "真實傷害" + E + "。" + Y + "{w}秒" + E + "內每命中敵方英雄一次，傷害提高" + Y + "{s}%" + E +
               "；" + O + "諾克薩斯威能" + E + "時加倍。擊殺則刷新大招。只在一刀砍得死射程內的英雄、或" + O + "諾克薩斯威能" + E + "期間施放。",
    "en": "[Health-reading ult test build] " + O + "Noxian Guillotine" + E + ": Darius leaps to an enemy champion and strikes, dealing " +
          W + "{b}" + E + " + " + ADi + O + "{r}% AD" + E + " " + W + "true damage" + E + ", " + Y + "{s}%" + E +
          " more for each hit he landed on an enemy champion in the last " + Y + "{w}s" + E + ", doubled during " + O + "Noxian Might" + E +
          "; a kill refreshes it. Cast only when it kills a champion in range or during " + O + "Noxian Might" + E + ".",
    "ko": "[체력 판독 테스트판] " + O + "녹서스의 단두대" + E + ": 적 챔피언에게 뛰어올라 " + W + "{b}" + E + " + " + ADi + O + "공격력의 {r}%" + E +
          " " + W + "고정 피해" + E + ". 최근 " + Y + "{w}초" + E + " 동안 적 챔피언 적중 1회마다 " + Y + "{s}%" + E + " 증가, " + O + "녹서스의 힘" + E +
          " 상태에서 2배. 처치하면 초기화. 사거리 안의 챔피언을 처치할 수 있을 때나 " + O + "녹서스의 힘" + E + " 상태일 때만 사용합니다.",
    "ja": "【体力判定テスト版】" + O + "ノクサスギロチン" + E + "：敵チャンピオンに飛びかかり、" + W + "{b}" + E + " + " + ADi + O + "攻撃力の{r}%" + E +
          "の" + W + "確定ダメージ" + E + "。直近" + Y + "{w}秒" + E + "間の敵チャンピオンへの命中1回ごとに" + Y + "{s}%" + E + "増加、" + O +
          "紅血の激昂" + E + "中は2倍。倒すとリセット。射程内のチャンピオンを倒せる時か" + O + "紅血の激昂" + E + "中にだけ使う。",
}
# the skill details panel's limits (lint_mod.TOOLTIP_MAX)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def consts():
    """src/plan.rs's numbers."""
    with open(lp(os.path.join(ADDON, "src", "plan.rs")), encoding="utf-8") as f:
        src = f.read()

    def one(pattern, name):
        m = re.search(pattern, src)
        if not m:
            sys.exit("no %s in src/plan.rs: update this script" % name)
        return m.group(1)

    num = lambda name: int(one(r"pub const %s: usize = ([0-9_]+);" % name, name).replace("_", ""))
    tiers = one(r"pub const R_TIERS: \[\(usize, usize\); 6\] = \[([^\]]*)\];", "R_TIERS")
    return {
        "HERO": one(r'pub const HERO: &str = "([^"]+)";', "HERO"),
        "MIGHT": one(r'pub const MIGHT: &str = "([^"]+)";', "MIGHT"),
        "HEMO": re.findall(r'"([^"]+)"', one(r"pub const HEMO: \[&str; 4\] = \[([^\]]*)\];", "HEMO")),
        "R_TIERS": [(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\)", tiers)],
        "MIGHT_TIER": num("MIGHT_TIER"),
        "MIGHT_ATTACK_MULT": num("MIGHT_ATTACK_MULT"),
        "R_RANGE": num("R_RANGE"),
        "R_LAND": num("R_LAND"),
    }


def walk(node, delay=0):
    """Every dict in the tree with the Delayed ticks above it."""
    if isinstance(node, dict):
        yield node, delay
        inner = delay + node.get("tick", 0) if node.get("type") == "Delayed" else delay
        for v in node.values():
            yield from walk(v, inner)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v, delay)


def ladder(node):
    """R's damage ladder from its top SwitchByBuff: [(buff or None, (damage, attack_ratio))], top down."""
    out = []
    while node.get("type") == "SwitchByBuff":
        hit = node["effect_buff"]
        if hit.get("type") != "FixedAttack":
            sys.exit("R's ladder step on %s is not a FixedAttack: update this script" % node["buff_name"])
        out.append((node["buff_name"], (hit["damage"], hit["attack_ratio"])))
        node = node["effect_none"]
    if node.get("type") != "FixedAttack":
        sys.exit("R's ladder does not end in a FixedAttack: update this script")
    out.append((None, (node["damage"], node["attack_ratio"])))
    return out


def check(kit, c):
    """Stop when src/plan.rs's numbers are not the kit's."""
    if c["HERO"] != HERO or kit["id"] != HERO:
        sys.exit("plan.rs HERO %s / kit id %s: expected %s" % (c["HERO"], kit["id"], HERO))
    ult = kit["ult"]
    tops = [(nd, dl) for nd, dl in walk(ult["effect"]) if nd.get("type") == "SwitchByBuff" and nd.get("buff_name") == c["MIGHT"]
            and nd.get("effect_buff", {}).get("type") == "FixedAttack"]
    if len(tops) != 1:
        sys.exit("expected one damage ladder in R, found %d: update this script" % len(tops))
    top, delay = tops[0]
    steps = ladder(top)
    want_names = [c["MIGHT"]] + c["HEMO"][::-1] + [None]
    if [s[0] for s in steps] != want_names:
        sys.exit("R's ladder reads %s, plan.rs %s: update plan.rs" % ([s[0] for s in steps], want_names))
    tiers = [s[1] for s in steps][::-1]  # bottom up: no stacks .. hemo_4, might
    if tiers != c["R_TIERS"] or c["MIGHT_TIER"] != len(tiers) - 1:
        sys.exit("R's tiers are %s, plan.rs R_TIERS %s (MIGHT_TIER %d): update plan.rs" % (tiers, c["R_TIERS"], c["MIGHT_TIER"]))
    land = ult["start_timing"] + delay
    if (ult["range"], land) != (c["R_RANGE"], c["R_LAND"]):
        sys.exit("R's range %d / blow at tick %d, plan.rs R_RANGE %d / R_LAND %d: update plan.rs"
                 % (ult["range"], land, c["R_RANGE"], c["R_LAND"]))
    mults = [nd["buff_state"].get("attack_mult", 0) for nd, _ in walk(kit) if nd.get("type") == "AddCasterBuff"
             and nd.get("buff_state", {}).get("name") == c["MIGHT"]]
    if not mults or set(mults) != {c["MIGHT_ATTACK_MULT"]}:
        sys.exit("the kit's %s attack_mult %s, plan.rs MIGHT_ATTACK_MULT %d: update plan.rs" % (c["MIGHT"], mults, c["MIGHT_ATTACK_MULT"]))
    windows = {nd["buff_state"]["duration"]["Time"]["tick"] for nd, _ in walk(kit) if nd.get("type") == "AddCasterBuff"
               and nd.get("buff_state", {}).get("name") in c["HEMO"]}
    if len(windows) != 1:
        sys.exit("the hemorrhage stacks last %s ticks: one window expected" % sorted(windows))
    if ult["casting_target"] != CASTING_TARGET:
        sys.exit("R's casting target is %s, not %s: update this script and the README" % (ult["casting_target"], CASTING_TARGET))
    return windows.pop()


def main():
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        kit = json.load(f)
    window = check(kit, c)
    (b, r), step = c["R_TIERS"][0], c["R_TIERS"][1][1] - c["R_TIERS"][0][1]
    if c["R_TIERS"][c["MIGHT_TIER"]] != (2 * b, 2 * r) or window % 60:
        sys.exit("the tooltip says Might doubles R and the window is whole seconds: update TEXT")
    kit["ult"]["description"] = "#asset/base/text/champion?" + TEXT_KEY

    values = {"b": b, "r": r, "s": step * 100 // r, "w": window // 60}
    texts = {lang: t.format(**values) for lang, t in TEXT.items()}
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(kit, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- tooltip lengths",
          {lang: "%d/%d" % (shown_length(t), TOOLTIP_MAX[lang]) for lang, t in texts.items()})


if __name__ == "__main__":
    main()
