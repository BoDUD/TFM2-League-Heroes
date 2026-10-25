"""Build the add-on's copy of Trundle from the main pack (King's Tribute, a fixed domain, terrain pillars, League's Chomp
and Subjugate).

    python addons/league_trundle/make_override.py [--draft] [--check]

Rebuilds Trundle with tools/kit/build_trundle.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_trundle.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_trundle/override/league_trundle.data_champion and
.../text/champion.i18n: the build with native=1 (build_trundle.py's docstring) -
  * passive = league_trundle:troll (params build_trundle.NATIVE_KEYS);
  * no kill trigger (the add-on heals for every enemy dying near him); `w_on` a plain mark (the add-on's `w_in` holds the
    domain's stats while he stands in it); the pillar marks its champions `e_at` (no hold); Chomp marks `q_mark` (no sap,
    no `q_ad`); Subjugate marks `r_drain` (no true damage, heal or stat cut of its own);
  * the attack's and the ult's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Trundle changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_trundle")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_trundle as kit  # noqa: E402
import setup_trundle as setup  # noqa: E402

MOD_ID = "league_trundle"
HERO = "league_trundle"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")   # every slot's rules differ from the main pack's
phys, t, n, cc = setup.phys, setup.t, setup.n, setup.cc
# lang -> the add-on's texts for every slot (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】抡冰棒。" + n("国王的贡品") + "：身边敌方单位倒下时回复它最大生命{p_pct}%，冰面上双倍。" + n("冰封领域") +
                  "：利齿撕咬咬中英雄时在原地冻出冰面" + t("{w_t}秒") + "（每" + t("{w_cd}秒") + "一次），站在上面攻速+{w_as}%、"
                  "移速+{w_ms}%，受到的治疗+{w_amp}%。",
        "skill": "【附加包】咬一口造成" + phys("q_dmg", "q_ratio") + "物理伤害并" + cc("减速") + "{q_slow}%；" + t("{q_t}秒") +
                 "内偷走对方攻击力的{q_flat}%（对方少一半）。",
        "skill2": "【附加包】在敌方英雄身后立起寒冰之柱" + t("{e_t}秒") + "：冰柱是地形，谁都过不去；周围敌人" + cc("减速") +
                  "{e_slow}%。",
        "ult": "【附加包】吸取敌方英雄：立刻造成最大生命{r_pct0}%魔法伤害，" + t("{r_t}秒") + "内" + t("每秒") + "再{r_pct}%，"
               "吸多少回多少；偷走它{r_steal}%护甲和魔抗" + t("{r_hold}秒") + "。",
    },
    "zh-hant": {
        "attack": "【附加包】揮冰棒。" + n("帝王獻祭") + "：身邊敵方單位倒下時回復它最大生命{p_pct}%，冰面上雙倍。" + n("極凍領地") +
                  "：狂野撕咬咬中英雄時在原地凍出冰面" + t("{w_t}秒") + "（每" + t("{w_cd}秒") + "一次），站在上面攻速+{w_as}%、"
                  "移速+{w_ms}%，受到的治療+{w_amp}%。",
        "skill": "【附加包】咬一口造成" + phys("q_dmg", "q_ratio") + "物理傷害並" + cc("緩速") + "{q_slow}%；" + t("{q_t}秒") +
                 "內偷走對方攻擊力的{q_flat}%（對方少一半）。",
        "skill2": "【附加包】在敵方英雄身後立起狡詰冰柱" + t("{e_t}秒") + "：冰柱是地形，誰都過不去；周圍敵人" + cc("緩速") +
                  "{e_slow}%。",
        "ult": "【附加包】吸取敵方英雄：立刻造成最大生命{r_pct0}%魔法傷害，" + t("{r_t}秒") + "內" + t("每秒") + "再{r_pct}%，"
               "吸多少回多少；偷走它{r_steal}%護甲和魔抗" + t("{r_hold}秒") + "。",
    },
    "en": {
        "attack": "[Add-on] Ice club blows. " + n("King's Tribute") + ": an enemy unit dying near him heals him {p_pct}% of its "
                  "max health, doubled on his domain. " + n("Frozen Domain") + ": Chomp biting a champion freezes the ground "
                  "where he stands for " + t("{w_t}s") + " (once every " + t("{w_cd}s") + "): on it +{w_as}% attack speed, "
                  "+{w_ms}% move speed and {w_amp}% more healing.",
        "skill": "[Add-on] Bites for " + phys("q_dmg", "q_ratio") + " physical damage and " + cc("slows") + " {q_slow}%; for " +
                 t("{q_t}s") + " he steals {q_flat}% of the target's attack (it loses half that).",
        "skill2": "[Add-on] Raises a Pillar of Ice behind an enemy champion for " + t("{e_t}s") + ": terrain no one can walk "
                  "through; enemies around it are " + cc("slowed") + " {e_slow}%.",
        "ult": "[Add-on] Drains an enemy champion: {r_pct0}% max health as magic damage at once, {r_pct}% more " +
               t("every second") + " for " + t("{r_t}s") + ", healing him for all it drains; steals {r_steal}% of its "
               "armour and magic resistance for " + t("{r_hold}s") + ".",
    },
    "ko": {
        "attack": "[확장] 얼음 몽둥이 공격. " + n("헌납") + ": 주변 적 유닛이 죽으면 그 최대 체력의 {p_pct}% 회복, 얼음 위에서는 2배. " +
                  n("얼음 왕국") + ": 깨물기가 챔피언을 물면 그 자리 땅을 " + t("{w_t}초") + " 얼림(" + t("{w_cd}초") + "마다 한 번), "
                  "그 위에서 공격 속도 +{w_as}%, 이동 속도 +{w_ms}%, 받는 회복 +{w_amp}%.",
        "skill": "[확장] 깨물어 " + phys("q_dmg", "q_ratio") + " 물리 피해, {q_slow}% " + cc("둔화") + "; " + t("{q_t}초") +
                 " 동안 대상 공격력의 {q_flat}%를 빼앗음(대상은 그 절반 감소).",
        "skill2": "[확장] 적 챔피언 뒤에 얼음 기둥을 " + t("{e_t}초") + " 세움: 누구도 지나갈 수 없는 지형, 주변 적 {e_slow}% " +
                  cc("둔화") + ".",
        "ult": "[확장] 적 챔피언을 흡수: 즉시 최대 체력 {r_pct0}% 마법 피해, " + t("{r_t}초") + " 동안 " + t("매초") + " {r_pct}% "
               "추가, 흡수한 만큼 회복; 방어력과 마법 저항력 {r_steal}%를 " + t("{r_hold}초") + " 동안 빼앗음.",
    },
    "ja": {
        "attack": "【拡張】氷の棍棒で攻撃。" + n("王への貢物") + "：近くの敵ユニットが倒れるとその最大体力の{p_pct}%回復、氷の上では2倍。" +
                  n("凍てつく大地") + "：咬み付きがチャンピオンに当たるとその場の地面を" + t("{w_t}秒") + "凍らせる（" +
                  t("{w_cd}秒") + "に1回）、その上で攻撃速度+{w_as}%、移動速度+{w_ms}%、受ける回復+{w_amp}%。",
        "skill": "【拡張】咬み付いて" + phys("q_dmg", "q_ratio") + "の物理ダメージ、{q_slow}%" + cc("スロウ") + "；" + t("{q_t}秒") +
                 "間 相手の攻撃力の{q_flat}%を奪う（相手はその半分減少）。",
        "skill2": "【拡張】敵チャンピオンの背後に氷冷の柱を" + t("{e_t}秒") + "立てる：誰も通れない地形、周囲の敵に{e_slow}%" +
                  cc("スロウ") + "。",
        "ult": "【拡張】敵チャンピオンから搾取：即座に最大体力{r_pct0}%の魔法ダメージ、" + t("{r_t}秒") + "間" + t("毎秒") +
               "{r_pct}%、奪った分だけ回復；物理防御と魔法防御の{r_steal}%を" + t("{r_hold}秒") + "奪う。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (p_pct: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":troll":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_trundle differs from build_trundle.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = dict(setup.values(p), p_pct=p["p_pct"], w_amp=p["w_amp"], q_flat=p["q_flat"], r_steal=p["r_steal"])
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
        print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in NATIVE.items()
               for k, tx in d.items()})
    out[os.path.join(ADDON, "override", HERO + ".data_champion")] = dumps_main(champion)
    return out, champion


def main():
    draft = "--draft" in sys.argv[1:]
    out, champion = files(draft)
    if "--check" in sys.argv[1:]:
        stale = [os.path.relpath(path, ROOT) for path, text in out.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8", newline="").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in out.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, ROOT))
    print("(draft)" if draft else json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
