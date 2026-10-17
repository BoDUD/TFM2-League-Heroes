"""Build the add-on's copy of Anivia from the main pack (Rebirth's egg, a real Crystallize wall, Frostbite on Iced).

    python addons/league_anivia/make_override.py

Rebuilds Anivia with tools/kit/build_anivia.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_anivia.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_anivia/override/league_anivia.data_champion and .../text/champion.i18n: the build with native=1 -
  * passive league_anivia:rebirth (params: egg_t, egg_cd, the wall's w_t / w_w / w_h, ice_t);
  * the egg shown by the data (egg_go / egg_hatch flags), the wall without the main pack's slow ring (the add-on keeps
    every unit out), Frostbite's hit raising e_now (the add-on doubles it on an Iced target);
  * the attack's, Q's and E's tooltips point to description.league_anivia_addon.* with the add-on's wording, so the
    tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Anivia changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_anivia")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_anivia as kit  # noqa: E402
import setup_anivia as setup  # noqa: E402

TEXT_ID = "league_anivia_addon"         # the texts' key (the hero's own id is league_anivia)
HERO = "league_anivia"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
M, O, A, R, E = setup.M, setup.O, setup.A, setup.R, setup.E
mag = setup.mag
TEXT = {
    "zh-hans": {
        "attack": "冰弹。" + O + "寒霜涅槃" + E + "：受到致命伤害时变成冰蛋" + A + "{egg_t}秒" + E + "（生命回满，双抗降低），蛋被打碎才阵亡；"
                  "撑过去就带着蛋剩下的生命复活。冷却" + A + "{egg_cd}秒" + E + "，阵亡不重置。",
        "skill": "射出冰球，穿过的敌人受到" + mag("q_pass", "q_pass_r") + "并" + R + "减速{q_slow}%" + E + "；碰到英雄或到达落点时引爆：" +
                 mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "并" + R + "眩晕{q_stun}秒" + E + "。" + O + "寒冰屏障" + E + "：晕到英雄时在原地竖起冰墙" +
                 A + "{w_t}秒" + E + "，两边的英雄和小兵都过不去。",
        "skill2": "冰锥造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "；目标带冰冻（被寒冰闪耀或成形的冰川风暴打中后" + A + "{ice_t}秒" + E +
                  "）时伤害翻倍。",
    },
    "zh-hant": {
        "attack": "冰彈。" + O + "寒霜涅槃" + E + "：受到致命傷害時變成冰蛋" + A + "{egg_t}秒" + E + "（生命回滿，雙抗降低），蛋被打碎才陣亡；"
                  "撐過去就帶著蛋剩下的生命復活。冷卻" + A + "{egg_cd}秒" + E + "，陣亡不重置。",
        "skill": "射出冰球，穿過的敵人受到" + mag("q_pass", "q_pass_r") + "並" + R + "緩速{q_slow}%" + E + "；碰到英雄或到達落點時引爆：" +
                 mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "並" + R + "暈眩{q_stun}秒" + E + "。" + O + "寒冰屏障" + E + "：暈到英雄時在原地豎起冰牆" +
                 A + "{w_t}秒" + E + "，兩邊的英雄和小兵都過不去。",
        "skill2": "冰錐造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "；目標帶冰凍（被寒冰閃耀或成形的冰川風暴打中後" + A + "{ice_t}秒" + E +
                  "）時傷害加倍。",
    },
    "en": {
        "attack": "An ice bolt. " + O + "Rebirth" + E + ": lethal damage turns her into an egg for " + A + "{egg_t}s" + E +
                  " (full health, lower armour and magic resistance); only breaking the egg kills her, if it survives she "
                  "is reborn with its health. Cooldown " + A + "{egg_cd}s" + E + ", kept through death.",
        "skill": "An ice ball: " + mag("q_pass", "q_pass_r") + " " + M + "magic damage" + E + " and a " + R + "{q_slow}% slow" + E +
                 " to enemies it passes; it bursts on the first champion or at its spot for " + mag("q_dmg", "q_ratio") + " " + M +
                 "magic damage" + E + " and a " + R + "{q_stun}s stun" + E + ". " + O + "Crystallize" + E + ": a champion stunned, an ice wall "
                 "rises there for " + A + "{w_t}s" + E + " that no champion or minion can cross.",
        "skill2": "An ice shard for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ", doubled on an Iced target (struck by "
                  "Flash Frost or the formed Glacial Storm in the last " + A + "{ice_t}s" + E + ").",
    },
    "ko": {
        "attack": "얼음 화살. " + O + "환생" + E + ": 치명적인 피해를 받으면 " + A + "{egg_t}초" + E + "간 알로 변함(체력 회복, 방어력·마법 저항력 감소). "
                  "알이 깨져야 사망하고, 버티면 알의 체력으로 부활. 재사용 대기시간 " + A + "{egg_cd}초" + E + ", 사망해도 유지.",
        "skill": "얼음 구체: 지나간 적에게 " + mag("q_pass", "q_pass_r") + " 피해와 " + R + "{q_slow}% 둔화" + E + "; 첫 챔피언이나 목표 지점에서 폭발해 " +
                 mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + "와 " + R + "{q_stun}초 기절" + E + ". " + O + "결정화" + E +
                 ": 챔피언을 기절시키면 그 자리에 " + A + "{w_t}초" + E + "간 챔피언도 미니언도 넘을 수 없는 얼음벽.",
        "skill2": "얼음 조각으로 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + ". 냉기 표식(" + A + "{ice_t}초" + E + " 안에 냉기 폭발이나 "
                  "완성된 얼음 폭풍에 맞음) 대상에게 2배.",
    },
    "ja": {
        "attack": "氷の弾。" + O + "再誕" + E + "：致死ダメージで" + A + "{egg_t}秒" + E + "卵になる（体力全快、物理・魔法防御低下）。卵が壊されると死亡、"
                  "耐えれば卵の体力で復活。クールダウン" + A + "{egg_cd}秒" + E + "、死亡後も継続。",
        "skill": "氷の球：通過した敵に" + mag("q_pass", "q_pass_r") + "と" + R + "スロウ{q_slow}%" + E + "。最初のチャンピオンか着弾点で炸裂し" +
                 mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "と" + R + "スタン{q_stun}秒" + E + "。" + O + "アイスウォール" + E +
                 "：スタンさせるとそこに" + A + "{w_t}秒" + E + "チャンピオンもミニオンも越えられない氷の壁。",
        "skill2": "氷の欠片で" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "。凍結（" + A + "{ice_t}秒" + E + "以内にフラッシュ"
                  "フロストか完成したブリザードを受けた）の対象には2倍。",
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
        sys.exit("the main pack's league_anivia differs from build_anivia.P: rebuild it first")
    champion = kit.build(dict(p, native=1, w_slow=0))
    if (champion.get("passive", {}).get("passive_ref") != "league_anivia:rebirth" or "w_stuck" in json.dumps(champion)
            or "w_mark" not in json.dumps(champion)):
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("attack", "skill", "skill2"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = setup.values(p)
    values["ice_t"] = setup.secs(p["ice_t"])
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
