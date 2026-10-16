"""Build the add-on's copy of Urgot from the main pack (Echoing Flames by direction, Fear Beyond Death's real execute).

    python addons/league_urgot/make_override.py

Rebuilds Urgot with tools/kit/build_urgot.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_urgot.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_urgot/override/league_urgot.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the shot, Purge, the charge, the charge in, the drill);
  * every attack and Purge shot calling league_urgot:leg (a leg blasts only when the add-on raises league_urgot_leg_go);
  * the end of the leash calling league_urgot:mercy (the reel and the execute only when it raises league_urgot_r_low);
  * passive = the add-on's league_urgot:legs with the numbers of P;
  * the attack's and the ult's tooltips point to description.league_urgot.attack / .ult with the add-on's wording (keys
    of the add-on's own id), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Urgot changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_urgot")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_urgot as kit  # noqa: E402
import setup_urgot as setup  # noqa: E402

MOD_ID = "league_urgot"
HERO = "league_urgot"
O, A, T, R, E = setup.O, setup.A, setup.T, setup.R, setup.E
phy = setup.phy
# lang -> the add-on's attack and ult texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】炮臂霰弹。" + O + "回响烈焰" + E + "：六条腿各朝一个方向，普攻和净除的子弹落在哪边，就由朝那边的腿喷扇形火焰，造成{p_ratio}%攻击力+目标{p_hp}%最大生命的" +
                  O + "物理伤害" + E + "，每条腿各自冷却。",
        "ult": "【附加包】发射钻头钉住第一个敌方英雄，造成" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "并减速；" + A + "{r_t}秒" + E +
               "时目标生命低于25%就拽回来处决；处决成功时周围敌人" + R + "恐惧{r_fear}秒" + E + "。",
    },
    "zh-hant": {
        "attack": "【擴充包】砲臂霰彈。" + O + "振盪火砲" + E + "：六條腿各朝一個方向，普攻和殺戮射擊的子彈落在哪邊，就由朝那邊的腿噴扇形火焰，造成{p_ratio}%攻擊力+目標{p_hp}%最大生命的" +
                  O + "物理傷害" + E + "，每條腿各自冷卻。",
        "ult": "【擴充包】發射鑽頭釘住第一個敵方英雄，造成" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "並緩速；" + A + "{r_t}秒" + E +
               "時目標生命低於25%就拽回來處決；處決成功時周圍敵人" + R + "恐懼{r_fear}秒" + E + "。",
    },
    "en": {
        "attack": "[Add-on] Shotgun blasts from his cannon arm. " + O + "Echoing Flames" + E + ": each of his six legs faces its own way; "
                  "the leg facing where an attack or Purge's shot lands blasts a cone for {p_ratio}% AD + {p_hp}% of the target's max "
                  "health as " + O + "physical damage" + E + ", each leg on its own cooldown.",
        "ult": "[Add-on] Fires a drill that impales the first enemy champion for " + phy("r_dmg", "r_ratio") + " " + O +
               "physical damage" + E + " and a slow; after " + A + "{r_t}s" + E + ", if it is below 25% health, he reels it in and "
               "executes it. An execution makes nearby enemies " + R + "flee for {r_fear}s" + E + ".",
    },
    "ko": {
        "attack": "[확장] 포신 팔로 산탄을 쏩니다. " + O + "화염의 메아리" + E + ": 여섯 다리가 각자 한 방향을 향해, 기본 공격과 심판의 원 탄환이 "
                  "닿는 쪽 다리가 부채꼴로 발사해 공격력의 {p_ratio}% + 대상 최대 체력의 {p_hp}% " + O + "물리 피해" + E + ", 다리마다 재사용 대기시간.",
        "ult": "[확장] 드릴을 쏘아 첫 적 챔피언을 꿰뚫어 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + "와 둔화, " + A + "{r_t}초" + E +
               " 후 체력 25% 미만이면 끌어당겨 처형. 처형 성공 시 주변 적 " + R + "{r_fear}초 공포" + E + ".",
    },
    "ja": {
        "attack": "【拡張】砲腕で散弾を撃つ。" + O + "エコーフレイム" + E + "：6本の脚がそれぞれ別の方向を向き、通常攻撃とパージの弾が当たった側の脚が扇状に撃ち、"
                  "攻撃力の{p_ratio}%+対象の最大体力の{p_hp}%の" + O + "物理ダメージ" + E + "。脚ごとにクールダウン。",
        "ult": "【拡張】ドリルを撃ち最初の敵チャンピオンを貫き" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "とスロウ、" + A + "{r_t}秒" + E +
               "後に体力25%未満なら引き寄せて処刑。処刑成功で周囲の敵が" + R + "{r_fear}秒恐怖" + E + "。",
    },
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_urgot differs from build_urgot.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":legs":
        sys.exit("the copy has no league_urgot:legs passive: update this script")
    text = json.dumps(champion)
    for ref in ("league_urgot:leg\"", "league_urgot:mercy"):
        if ref not in text:
            sys.exit(f"the copy does not call {ref}: update this script")
    for slot in ("attack", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
