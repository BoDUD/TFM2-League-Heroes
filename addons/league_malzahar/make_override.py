"""Build the add-on's copy of Malzahar from the main pack (Void Shift as in League, Malefic Visions jumping on deaths).

    python -X utf8 addons/league_malzahar/make_override.py

Rebuilds Malzahar with tools/kit/build_malzahar.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_malzahar.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_malzahar/override/league_malzahar.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus the data passive (the Granite-Shield ladder) and the vision's data death
    watch (its one jump);
  * passive league_malzahar:void (params: p_cd / p_linger / p_dr for Void Shift, e_t / e_p / e_dmg / e_ap / e_jump for
    the visions it moves) and the native effect league_malzahar:vision on every unit the vision's bolt hits;
  * the attack's and the skill's tooltips point to description.league_malzahar_void.* with the add-on's wording (Void
    Shift and the jumps as League has them), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Malzahar changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_malzahar")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_malzahar as kit  # noqa: E402
import setup_malzahar as setup  # noqa: E402

TEXT_ID = "league_malzahar_void"          # the text's key (the hero's own id is league_malzahar)
HERO = "league_malzahar"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, C, M, E = setup.O, setup.A, setup.C, setup.M, setup.E
mag = setup.mag
ATTACK = {
    "zh-hans": "射出虚空弹。被动" + O + "虚空穿越" + E + "：受到的伤害减少{p_dr}%并" + C + "免疫控制" + E + "；被非小兵单位打中" + A + "{p_linger}秒" + E +
               "后消失，" + A + "{p_cd}秒" + E + "内未受到英雄伤害时重新获得。",
    "zh-hant": "射出虛空彈。被動" + O + "虛空象限" + E + "：受到的傷害減少{p_dr}%並" + C + "免疫控場" + E + "；被非小兵單位打中" + A + "{p_linger}秒" + E +
               "後消失，" + A + "{p_cd}秒" + E + "內未受到英雄傷害時重新獲得。",
    "en": "Fires a void bolt. Passive " + O + "Void Shift" + E + ": takes {p_dr}% less damage and is " + C + "immune to crowd control" + E +
          "; it fades " + A + "{p_linger}s" + E + " after a non-minion hit and returns after " + A + "{p_cd}s" + E + " without champion damage.",
    "ko": "공허의 화살을 쏩니다. 기본 지속 효과 " + O + "공허 태세" + E + ": 받는 피해 {p_dr}% 감소, " + C + "군중 제어 면역" + E + "; 미니언이 아닌 적에게 맞고 " + A +
          "{p_linger}초" + E + " 뒤 사라지며, " + A + "{p_cd}초" + E + " 동안 챔피언 피해를 받지 않으면 다시 생깁니다.",
    "ja": "ヴォイドの弾を放つ。自動効果" + O + "ヴォイドシフト" + E + "：受けるダメージ{p_dr}%減少、" + C + "行動妨害無効" + E + "；ミニオン以外の攻撃を受けて" + A +
          "{p_linger}秒" + E + "後に消え、" + A + "{p_cd}秒" + E + "チャンピオンのダメージを受けないと再び得る。",
}
SKILL = {
    "zh-hans": O + "煞星幻象" + E + "：" + A + "{e_t}秒" + E + "内造成" + mag("e") + M + "魔法伤害" + E + "，目标死亡时立刻跳到最近的敌人身上（优先英雄），可以一直跳。" + O +
               "虚空虫群" + E + "随之撕咬目标，每" + A + "{w_p}秒" + E + "造成" + mag("w") + M + "魔法伤害" + E + "。",
    "zh-hant": O + "煞星幻象" + E + "：" + A + "{e_t}秒" + E + "內造成" + mag("e") + M + "魔法傷害" + E + "，目標死亡時立刻跳到最近的敵人身上（優先英雄），可以一直跳。" + O +
               "召喚虛靈" + E + "隨之撕咬目標，每" + A + "{w_p}秒" + E + "造成" + mag("w") + M + "魔法傷害" + E + "。",
    "en": O + "Malefic Visions" + E + ": deals " + mag("e") + " " + M + "magic damage" + E + " over " + A + "{e_t}s" + E +
          "; whenever the target dies, the vision jumps at once to the nearest enemy, champions first. " + O + "Void Swarm" + E + ": voidlings bite the target, " +
          mag("w") + " " + M + "magic damage" + E + " every " + A + "{w_p}s" + E + ".",
    "ko": O + "재앙의 환상" + E + ": " + A + "{e_t}초" + E + "에 걸쳐 " + mag("e") + " " + M + "마법 피해" + E + ", 대상이 죽을 때마다 가장 가까운 적(챔피언 우선)에게 바로 옮겨갑니다. " +
          O + "공허의 무리" + E + ": 공허충이 대상을 물어 " + A + "{w_p}초" + E + "마다 " + mag("w") + " " + M + "마법 피해" + E + ".",
    "ja": O + "虚性侵蝕" + E + "：" + A + "{e_t}秒" + E + "かけて" + mag("e") + "の" + M + "魔法ダメージ" + E + "、対象が倒れるたびに最も近い敵（チャンピオン優先）へすぐ移る。" + O +
          "ヴォイドスワーム" + E + "：ヴォイドリングが対象に噛みつき" + A + "{w_p}秒" + E + "ごとに" + mag("w") + "の" + M + "魔法ダメージ" + E + "。",
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
        sys.exit("the main pack's league_malzahar differs from build_malzahar.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    s = json.dumps(champion)
    if (champion.get("passive", {}).get("passive_ref") != "league_malzahar:void" or "league_malzahar:vision" not in s
            or "league_malzahar_e_watch" in s or "league_malzahar_p_init" in s):
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"
    champion["skill"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.skill"

    values = setup.values(p)
    values.update({"p_dr": p["p_dr"], "p_linger": setup.secs(p["p_linger"])})
    texts = {lang: {"attack": (LEAD[lang] + ATTACK[lang]).format(**values),
                    "skill": (LEAD[lang] + SKILL[lang]).format(**values)} for lang in ATTACK}
    long = {f"{lang}.{k}": setup.shown_length(d[k]) for lang, d in texts.items() for k in d
            if setup.shown_length(d[k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
