"""Build the add-on's copy of Ziggs from the main pack (Satchel Charge hexplodes low towers, Short Fuse x1.75 on towers).

    python addons/league_ziggs/make_override.py

Rebuilds Ziggs with tools/kit/build_ziggs.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_ziggs.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_ziggs/override/league_ziggs.data_champion and .../text/champion.i18n: the build with native=1 -
  * passive league_ziggs:hexplode (params: w_ex, w_hex_r, w_cd, p_tower);
  * Short Fuse's bomb raises `league_ziggs_p_now` on him as it hits (the add-on scales that hit on a tower);
  * the attack's tooltip points to description.league_ziggs_addon.attack with the add-on's wording, so the tooltip in
    game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Ziggs changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_ziggs")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_ziggs as kit  # noqa: E402
import setup_ziggs as setup  # noqa: E402

TEXT_ID = "league_ziggs_addon"       # the texts' key (the hero's own id is league_ziggs)
HERO = "league_ziggs"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag = setup.mag
TEXT = {
    "zh-hans": {
        "attack": "扔小炸弹。" + O + "一触即发" + E + "：每" + A + "{p_t}秒" + E + "下次普攻多造成" + mag("p_dmg", "p_ratio") + M + "魔法伤害" + E +
                  "（打塔×1.75），放技能冷却-" + A + "{p_cut}秒" + E + "。" + O + "定点爆破" + E + "：3级起贴身时脚下引爆" + mag("w_dmg", "w_ratio") +
                  "并" + R + "击退" + E + "；敌方塔血量低于{w_ex}%时直接炸掉。",
    },
    "zh-hant": {
        "attack": "扔小炸彈。" + O + "即刻爆發" + E + "：每" + A + "{p_t}秒" + E + "下次普攻多造成" + mag("p_dmg", "p_ratio") + M + "魔法傷害" + E +
                  "（打塔×1.75），施放技能冷卻-" + A + "{p_cut}秒" + E + "。" + O + "技術性引爆" + E + "：3級起貼身時腳下引爆" +
                  mag("w_dmg", "w_ratio") + "並" + R + "擊退" + E + "；敵方塔血量低於{w_ex}%時直接炸掉。",
    },
    "en": {
        "attack": "Tosses a small bomb. " + O + "Short Fuse" + E + ": every " + A + "{p_t}s" + E + " his next attack deals " +
                  mag("p_dmg", "p_ratio") + " " + M + "magic damage" + E + " more (x1.75 on towers); each spell takes " + A + "{p_cut}s" + E +
                  " off. " + O + "Satchel Charge" + E + ": from level 3 it blows up at his feet when a champion closes in (" +
                  mag("w_dmg", "w_ratio") + ", " + R + "knock-back" + E + ") and blows up an enemy tower below {w_ex}% health.",
    },
    "ko": {
        "attack": "작은 폭탄. " + O + "짧은 도화선" + E + ": " + A + "{p_t}초" + E + "마다 다음 공격이 " + mag("p_dmg", "p_ratio") + "의 " + M + "마법 피해" + E +
                  " 추가(포탑 x1.75), 스킬 사용 시 " + A + "{p_cut}초" + E + " 감소. " + O + "휴대용 폭약" + E + ": 3레벨부터 근접 시 발밑 폭발(" +
                  mag("w_dmg", "w_ratio") + ", " + R + "밀쳐내기" + E + "), 체력 {w_ex}% 이하 적 포탑 즉시 파괴.",
    },
    "ja": {
        "attack": "小型爆弾。" + O + "ショートヒューズ" + E + "：" + A + "{p_t}秒" + E + "毎に次の攻撃が" + mag("p_dmg", "p_ratio") + "の" + M + "魔法ダメージ" + E +
                  "追加（タワーx1.75）、スキルで" + A + "{p_cut}秒" + E + "短縮。" + O + "エンジニアボム" + E + "：Lv3から接近時に足元で爆発" +
                  mag("w_dmg", "w_ratio") + "、" + R + "ノックバック" + E + "。体力{w_ex}%以下の敵タワーを即破壊。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_ziggs differs from build_ziggs.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if champion.get("passive", {}).get("passive_ref") != "league_ziggs:hexplode" or "league_ziggs_p_now" not in text:
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    values = dict(setup.values(p), w_ex=p["w_ex"])
    texts = {lang: {k: (LEAD[lang] + t[k]).format(**values) for k in t} for lang, t in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(LEAD[lang] + TEXT[lang][k]) for lang in TEXT for k in TEXT[lang]
            if setup.shown_length(LEAD[lang] + TEXT[lang][k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    for lang in TEXT:
        print(lang, " ".join(f"{k}:{setup.shown_length(LEAD[lang] + TEXT[lang][k])}/{setup.TOOLTIP_MAX[lang]}"
                             for k in TEXT[lang]))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
