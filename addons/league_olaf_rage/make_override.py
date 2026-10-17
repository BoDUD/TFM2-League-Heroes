"""Build the add-on's copy of Olaf from the main pack (Berserker Rage by his real missing health).

    python addons/league_olaf_rage/make_override.py

Rebuilds Olaf with tools/kit/build_olaf.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_olaf.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_olaf_rage/override/league_olaf.data_champion and .../text/champion.i18n: the same kit with three
changes -
  * the main pack's hit counter in his attack (a 1-point shield broken = one Rage level more, levels dropping out of
    combat) is gone (build_olaf native=1);
  * passive = the add-on's league_olaf_rage:rage with the numbers from P as its params: every tick it reads his health
    and holds the Rage levels league_olaf_p_1..p_n by his missing health (n_lo% missing for the first level, every
    n_band% more one more level) - the same buffs and numbers as the main pack's, so the top level's picture shows;
  * the attack's tooltip points to description.league_olaf_rage.attack (a "health-read test build" lead, so the
    tooltip in game shows whether the override took).
Every other champion stays untouched. Run it again whenever the main pack's Olaf changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_olaf_rage")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_olaf as kit  # noqa: E402

MOD_ID = "league_olaf_rage"
TEXT_KEY = "description.league_olaf_rage.attack"
A, O, E = "<#ffb900ff>", "<#ff9028ff>", "<>"
TEXT = {
    "zh-hans": "【读血测试版】" + O + "狂战之怒" + E + "：已损失生命越多攻速越高（损失{n_lo}%起一层，每多{n_band}%再一层，每层+{p_as}%，共{p_n}层），"
               "最高两层吸血{p_vamp}%。" + O + "挺过去" + E + "（自动，" + A + "{w_cd}秒" + E + "）：交战时攻速+{w_as}%并获得护盾。" +
               O + "诸神黄昏" + E + "被动：护甲、魔抗+{r_def}。",
    "zh-hant": "【讀血測試版】" + O + "狂戰之怒" + E + "：已損失生命越多攻速越高（損失{n_lo}%起一層，每多{n_band}%再一層，每層+{p_as}%，共{p_n}層），"
               "最高兩層吸血{p_vamp}%。" + O + "咬牙苦撐" + E + "（自動，" + A + "{w_cd}秒" + E + "）：交戰時攻速+{w_as}%並獲得護盾。" +
               O + "諸神黃昏" + E + "被動：護甲、魔抗+{r_def}。",
    "en": "[Health-read test build] " + O + "Berserker Rage" + E + ": the more health he has lost, the faster he attacks (a level "
          "from {n_lo}% missing, one more every {n_band}%; +{p_as}% a level, {p_n} levels; the top two also {p_vamp}% life "
          "steal). " + O + "Tough It Out" + E + " (automatic, " + A + "{w_cd}s" + E + "): in a fight +{w_as}% attack speed and a "
          "shield. " + O + "Ragnarok" + E + " passive: +{r_def} armour and magic resistance.",
    "ko": "[체력 판독 테스트판] " + O + "광전사의 분노" + E + ": 잃은 체력이 많을수록 공격 속도 증가({n_lo}%부터 1단계, {n_band}%마다 1단계 더, "
          "단계당 +{p_as}%, {p_n}단계, 상위 두 단계 생명력 흡수 {p_vamp}%). " + O + "버티기" + E + "(자동, " + A + "{w_cd}초" + E +
          "): 교전 시 공격 속도 +{w_as}%와 보호막. " + O + "라그나로크" + E + " 기본 지속 효과: 방어력·마법 저항력 +{r_def}.",
    "ja": "【体力判定テスト版】" + O + "狂戦士の怒り" + E + "：失った体力が多いほど攻撃速度上昇（{n_lo}%で1段階、{n_band}%ごとに1段階、1段階+{p_as}%、"
          "{p_n}段階、上位2段階はライフスティール{p_vamp}%）。" + O + "根性比べ" + E + "（自動、" + A + "{w_cd}秒" + E +
          "）：交戦時に攻撃速度+{w_as}%とシールド。" + O + "ラグナロク" + E + "自動効果：物防・魔防+{r_def}。",
}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_olaf.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_olaf differs from build_olaf.P: rebuild it first")
    q = dict(p, native=1)
    champion = kit.build(q)
    attack = json.dumps(champion["attack"])
    if "league_olaf_sense" in attack:
        sys.exit("the hit counter is still in the attack: update this script")
    if champion.get("passive", {}).get("passive_ref") != "league_olaf_rage:rage":
        sys.exit("the native build has no league_olaf_rage:rage passive: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    values = {k: p[k] for k in ("n_lo", "n_band", "p_as", "p_n", "p_vamp", "w_as", "r_def")}
    values["w_cd"] = f"{p['w_cd'] / 60:g}"
    texts = {lang: t.format(**values) for lang, t in TEXT.items()}
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_olaf.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no health-read text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- hit counter dropped, passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]),
          "| tooltip lengths", {lang: shown_length(t) for lang, t in texts.items()})


if __name__ == "__main__":
    main()
