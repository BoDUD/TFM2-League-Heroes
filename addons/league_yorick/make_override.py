"""Build the add-on's copy of Yorick from the main pack (graves from kills, the Maiden's bonus on her target, as in League).

    python addons/league_yorick/make_override.py [--draft] [--check]

Rebuilds Yorick with tools/kit/build_yorick.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_yorick.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_yorick/override/league_yorick.data_champion and
.../text/champion.i18n: the build with native=1 -
  * passive = league_yorick:shepherd (params r_pct g_t);
  * Last Rites' blow raises `q_win` on him (the add-on digs a grave for each minion or monster that dies meanwhile) in
    place of the main pack's every-second-blow grave;
  * the ult puts `maiden` on her champion and his attacks a 3-tick `hit` on the champions they strike while she stands
    (the add-on deals the bonus on her target only), in place of the main pack's bonus on any champion;
  * the attack's and the ult's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Yorick changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yorick")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_yorick as kit  # noqa: E402
import setup_yorick as setup  # noqa: E402

MOD_ID = "league_yorick"
HERO = "league_yorick"
KEYS = ("r_pct", "g_t")
phys, t, n, cc = setup.phys, setup.t, setup.n, setup.cc
# lang -> the add-on's attack and ult texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】抡铲。" + n("牧魂人") + "：临终仪式打英雄或打死单位挖一座坟，满{g_n}座时下一铲唤醒{k_n}只" + n("雾行者") +
                  "咬目标" + t("{k_t}秒") + "（每只每口" + phys("k_dmg", "k_ratio") + "），同时" + n("暗灵缠身") + "把附近的敌方英雄" +
                  cc("定身") + t("{w_root}秒") + "。",
        "ult": "【附加包】在敌方英雄身后召唤" + n("迷雾室女") + "和{r_n}只雾行者，跟着它" + t("{r_t}秒") + "，" + t("每秒") + "抓" +
               phys("r_dmg", "r_ratio") + "；期间约里克普攻她的目标额外造成最大生命{r_pct}%真实伤害。",
    },
    "zh-hant": {
        "attack": "【附加包】揮鏟。" + n("亡魂牧人") + "：臨終葬儀打英雄或打死單位挖一座墳，滿{g_n}座時下一鏟喚醒{k_n}隻" + n("霧行者") +
                  "咬目標" + t("{k_t}秒") + "（每隻每口" + phys("k_dmg", "k_ratio") + "），同時" + n("黯影屍陣") + "把附近的敵方英雄" +
                  cc("定身") + t("{w_root}秒") + "。",
        "ult": "【附加包】在敵方英雄身後召喚" + n("迷霧少女") + "和{r_n}隻霧行者，跟著它" + t("{r_t}秒") + "，" + t("每秒") + "抓" +
               phys("r_dmg", "r_ratio") + "；期間約瑞科普攻她的目標額外造成最大生命{r_pct}%真實傷害。",
    },
    "en": {
        "attack": "[Add-on] Shovel blows. " + n("Shepherd of Souls") + ": Last Rites digs a grave on a champion or on a unit it "
                  "kills; with {g_n} graves the next one raises {k_n} " + n("Mist Walkers") + " that gnaw at the target for " +
                  t("{k_t}s") + " (" + phys("k_dmg", "k_ratio") + " a bite each), and " + n("Dark Procession") + " " +
                  cc("roots") + " the enemy champions near it for " + t("{w_root}s") + ".",
        "ult": "[Add-on] Raises the " + n("Maiden of the Mist") + " and {r_n} walkers behind an enemy champion; she follows it "
               "for " + t("{r_t}s") + ", clawing for " + phys("r_dmg", "r_ratio") + " " + t("every second") + ", and his "
               "attacks on her target deal {r_pct}% max health more as true damage meanwhile.",
    },
    "ko": {
        "attack": "[확장] 삽 공격. " + n("영혼의 길잡이") + ": 최후의 의식으로 챔피언을 치거나 유닛을 처치하면 무덤 생성, {g_n}개가 차면 "
                  "다음 일격에 " + n("안개 망령") + " {k_n}마리가 " + t("{k_t}초") + " 동안 대상을 물어뜯음(한 번에 " +
                  phys("k_dmg", "k_ratio") + "), " + n("망자의 진") + "이 주변 적 챔피언 " + t("{w_root}초") + " " + cc("속박") + ".",
        "ult": "[확장] 적 챔피언 뒤에 " + n("안개 처녀") + "와 망령 {r_n}마리 소환, " + t("{r_t}초") + " 동안 따라다니며 " +
               t("매초") + " " + phys("r_dmg", "r_ratio") + "; 그동안 요릭이 그 대상을 공격하면 최대 체력 {r_pct}% 고정 피해 추가.",
    },
    "ja": {
        "attack": "【拡張】シャベル攻撃。" + n("魂の導き手") + "：葬送でチャンピオンを打つかユニットを倒すと墓を掘る、{g_n}つ溜まると次の一撃で" +
                  n("ミストウォーカー") + "{k_n}体が" + t("{k_t}秒") + "噛みつく（1回" + phys("k_dmg", "k_ratio") + "）、" +
                  n("屍の列") + "が周囲の敵チャンピオンを" + t("{w_root}秒") + cc("スネア") + "。",
        "ult": "【拡張】敵チャンピオンの背後に" + n("霧の乙女") + "とウォーカー{r_n}体を召喚、" + t("{r_t}秒") + "追従し" + t("毎秒") +
               phys("r_dmg", "r_ratio") + "；その間ヨリックがその対象を攻撃すると最大体力{r_pct}%の確定ダメージ。",
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
    m = re.search(r"Self \{ (r_pct: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":shepherd":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_yorick differs from build_yorick.P: rebuild it first")
        for slot in ("attack", "ult"):
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = setup.values(p)
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
