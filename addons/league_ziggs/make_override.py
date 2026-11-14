"""Build the add-on's copy of Ziggs from the main pack (League's Satchel Charge and Bouncing Bomb, Short Fuse x1.75 on
towers).

    python addons/league_ziggs/make_override.py

Rebuilds Ziggs with tools/kit/build_ziggs.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_ziggs.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_ziggs/override/league_ziggs.data_champion and .../text/champion.i18n: the build with native=1 -
  * passive league_ziggs:hexplode (params: the W and Q numbers of P it needs) - it throws Satchel Charge at a point
    itself, so the watch's own at-his-feet W is not in the copy; the flying satchel's picture `w_throw`;
  * Q's first landing finding nobody hands the point to league_ziggs:q_hop (the bounces go on along the throw);
  * Short Fuse's bomb raises `league_ziggs_p_now` on him as it hits (the add-on scales that hit on a tower);
  * the attack's (Satchel Charge) and Q's tooltips point to description.league_ziggs_addon.* with the add-on's
    wording, so the tooltip in game shows whether the override took.
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
                  "（打塔×1.75），放技能冷却-" + A + "{p_cut}秒" + E + "。" + O + "定点爆破" + E + "：3级起扔出炸药包，造成" + mag("w_dmg", "w_ratio") +
                  "并把敌人从炸点向外" + R + "击退" + E + "，炸到自己就炸飞自己；炸掉血量低于{w_ex}%的敌方塔。",
        "skill": "扔向目标，落在瞄准点，附近有敌人就爆炸，否则" + A + "往前弹" + E + "，最多落地" + A + "3次" + E + "：周围敌人受到" +
                 mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "。",
    },
    "zh-hant": {
        "attack": "扔小炸彈。" + O + "即刻爆發" + E + "：每" + A + "{p_t}秒" + E + "下次普攻多造成" + mag("p_dmg", "p_ratio") + M + "魔法傷害" + E +
                  "（打塔×1.75），施放技能冷卻-" + A + "{p_cut}秒" + E + "。" + O + "技術性引爆" + E + "：3級起扔出炸藥包，造成" +
                  mag("w_dmg", "w_ratio") + "並把敵人從炸點向外" + R + "擊退" + E + "，炸到自己就炸飛自己；炸掉血量低於{w_ex}%的敵方塔。",
        "skill": "扔向目標，落在瞄準點，附近有敵人就爆炸，否則" + A + "往前彈" + E + "，最多落地" + A + "3次" + E + "：周圍敵人受到" +
                 mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "。",
    },
    "en": {
        "attack": "Tosses a small bomb. " + O + "Short Fuse" + E + ": every " + A + "{p_t}s" + E + " his next attack deals " +
                  mag("p_dmg", "p_ratio") + " " + M + "magic damage" + E + " more (x1.75 on towers); each spell takes " + A + "{p_cut}s" + E +
                  " off. " + O + "Satchel Charge" + E + ": from level 3 he throws a satchel: " + mag("w_dmg", "w_ratio") + ", " + R +
                  "knocking enemies away from the blast" + E + " (and him too, if he is in it); it blows up an enemy tower below {w_ex}% health.",
        "skill": "Throws a bomb at the target's spot; it blows up there next to an enemy, else " + A + "bounces on" + E +
                 " along the throw, landing up to " + A + "3 times" + E + ": " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " around it.",
    },
    "ko": {
        "attack": "작은 폭탄. " + O + "짧은 도화선" + E + ": " + A + "{p_t}초" + E + "마다 다음 공격이 " + mag("p_dmg", "p_ratio") + "의 " + M + "마법 피해" + E +
                  " 추가(포탑 x1.75), 스킬 사용 시 " + A + "{p_cut}초" + E + " 감소. " + O + "휴대용 폭약" + E + ": 3레벨부터 폭약을 던져 " +
                  mag("w_dmg", "w_ratio") + ", 폭발 중심에서 적을 " + R + "밀쳐내기" + E + "(자신도 맞으면 날아감), 체력 {w_ex}% 이하 적 포탑 파괴.",
        "skill": "목표 지점에 폭탄을 던져 근처에 적이 있으면 폭발, 없으면 " + A + "앞으로 튀어" + E + " 최대 " + A + "3번" + E + " 착지: 주변에 " +
                 mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + ".",
    },
    "ja": {
        "attack": "小型爆弾。" + O + "ショートヒューズ" + E + "：" + A + "{p_t}秒" + E + "毎に次の攻撃が" + mag("p_dmg", "p_ratio") + "の" + M + "魔法ダメージ" + E +
                  "追加（タワーx1.75）、スキルで" + A + "{p_cut}秒" + E + "短縮。" + O + "エンジニアボム" + E + "：Lv3から爆弾を投げ" +
                  mag("w_dmg", "w_ratio") + "、爆心から敵を" + R + "ノックバック" + E + "（自分も当たれば吹き飛ぶ）。体力{w_ex}%以下の敵タワーを即破壊。",
        "skill": "目標地点に爆弾を投げ、近くに敵がいれば爆発、いなければ" + A + "前方へ跳ね" + E + "最大" + A + "3回" + E + "着地、周囲に" +
                 mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "。",
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
    if (champion.get("passive", {}).get("passive_ref") != "league_ziggs:hexplode" or "league_ziggs_p_now" not in text
            or '"league_ziggs:q_hop"' not in text or '"league_ziggs_w_throw"' not in text or '"MoveBack"' in text):
        sys.exit("the copy does not call the add-on: update this script")
    for slot in TEXT["en"]:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

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
