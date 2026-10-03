"""Build the add-on's copy of Camille from the main pack (wall, map edge and tower Hookshot v4).

    python addons/league_camille_wall/make_override.py

Reads league/champion/league_camille.data_champion and writes
addons/league_camille_wall/override/league_camille.data_champion and .../text/champion.i18n:
the same kit with two changes -
  * E's pulse keeps the main pack's choice between escaping and engaging, but both branches now
    call the add-on's native effects (league_camille_wall:escape / :engage), which hook walls,
    the 5v5 map's four edges and towers;
    the main pack's search for a minion, monster or tower to hook (and its pulls) is dropped,
    and E arms with an enemy champion within ENGAGE_R (the add-on engages from that far);
  * passive_skill2 = the add-on's passive league_camille_wall:e, which casts E by itself (every 6
    ticks once E is ready) without waiting for the AI to arm it;
  * E's tooltip points to description.league_camille_wall.skill2 (the wall-hook text, with a
    "wall-hook test build" lead, so the tooltip in game shows whether the override took).
Run it again whenever the main pack's Camille changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_camille_wall")
MOD_ID = "league_camille_wall"
TEXT_KEY = "description.league_camille_wall.skill2"
ENGAGE_R = 85000
AD = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
AS = "<i#asset/base/ui/banpick/champion_stat_icon:attack_speed_0>"
TEXT = {
    "zh-hans": "【钩墙测试版】<#ff9028ff>钩索<>：钩住射程内的墙（含地图四边）或防御塔并被拉过去（附近没有不出手），随后冲向附近的敌方英雄，"
               f"对周围敌人造成<#ff9028ff>60<> + {AD}<#ff9028ff>70% 攻击力<>的<#ff9028ff>物理伤害<>，被撞的英雄"
               f"<#ef5350ff>眩晕<><#ffb900ff>0.75秒<>，并获得{AS}<#ceff99ff>攻速+50%<>，持续<#ffb900ff>5秒<>。"
               "被以多打少时改钩远离敌人的墙或塔，拉过去后再冲开。",
    "zh-hant": "【鉤牆測試版】<#ff9028ff>鋼鐵鉤射<>：鉤住射程內的牆（含地圖四邊）或防禦塔並被拉過去（附近沒有不出手），隨後衝向附近的敵方英雄，"
               f"對周圍敵人造成<#ff9028ff>60<> + {AD}<#ff9028ff>70% 攻擊力<>的<#ff9028ff>物理傷害<>，被撞的英雄"
               f"<#ef5350ff>暈眩<><#ffb900ff>0.75秒<>，並獲得{AS}<#ceff99ff>攻速+50%<>，持續<#ffb900ff>5秒<>。"
               "被以多打少時改鉤遠離敵人的牆或塔，拉過去後再衝開。",
    "en": "[Wall-hook test build] <#ff9028ff>Hookshot<>: Camille hooks a wall (the map's edges too) or tower in range and is pulled to it, "
          "then dashes at a nearby enemy champion, dealing <#ff9028ff>60<> + "
          f"{AD}<#ff9028ff>70% AD<> <#ff9028ff>physical damage<> around her, <#ef5350ff>stunning<> it for "
          f"<#ffb900ff>0.75s<> and gaining {AS}<#ceff99ff>50% Attack Speed<> for <#ffb900ff>5s<>. Outnumbered, she "
          "hooks a wall or tower away from enemies and dashes off instead.",
    "ko": "[벽 갈고리 테스트판] <#ff9028ff>갈고리 발사<>: 사거리 안의 벽(맵 가장자리 포함)이나 포탑에 갈고리를 걸어 끌려간 뒤 "
          "근처 적 챔피언에게 돌진해 주변 적에게 <#ff9028ff>60<> + "
          f"{AD}<#ff9028ff>공격력의 70%<> <#ff9028ff>물리 피해<>를 입히고 그 챔피언을 <#ffb900ff>0.75초<> 동안 "
          f"<#ef5350ff>기절<>시키며, <#ffb900ff>5초<> 동안 {AS}<#ceff99ff>공격 속도가 50%<> 증가합니다. "
          "수적 열세면 적에게서 먼 벽이나 포탑에 걸어 빠져나갑니다.",
    "ja": "【壁フック試験版】<#ff9028ff>フックショット<>：射程内の壁（マップの端も）かタワーにフックを掛けて引き寄せられ（近くになければ"
          f"使わない）、近くの敵チャンピオンへ突進し周囲の敵に<#ff9028ff>60<> + {AD}<#ff9028ff>攻撃力の70%<>の"
          f"<#ff9028ff>物理ダメージ<>、その敵を<#ffb900ff>0.75秒<><#ef5350ff>スタン<>、<#ffb900ff>5秒<>間"
          f"{AS}<#ceff99ff>攻撃速度+50%<>。数で不利なら敵から離れた壁かタワーに掛けて離脱。",
}


def native(name):
    return {"type": "Native", "effect_ref": "%s:%s" % (MOD_ID, name)}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def find_choice(node, out):
    """The pulse's last step: SwitchByBuff e_flee -> escape picks, else engage picks."""
    if isinstance(node, dict):
        if node.get("type") == "SwitchByBuff" and node.get("buff_name") == "league_camille_e_flee":
            out.append(node)
        for value in node.values():
            find_choice(value, out)
    elif isinstance(node, list):
        for value in node:
            find_choice(value, out)


def count(node):
    if isinstance(node, dict):
        return ("type" in node) + sum(count(v) for v in node.values())
    if isinstance(node, list):
        return sum(count(v) for v in node)
    return 0


def main():
    src = os.path.join(ROOT, "league", "champion", "league_camille.data_champion")
    with open(lp(src), encoding="utf-8") as f:
        champion = json.load(f)
    skill2 = champion["skill2"]
    skill2["description"] = "#asset/base/text/champion?" + TEXT_KEY
    # the AI arms E with an enemy champion this close: the add-on engages from ENGAGE_R (src/lib.rs)
    skill2["range"] = ENGAGE_R
    # and the add-on's passive (from E learned on) casts E by itself whenever it is ready
    champion["passive_skill2"] = {"passive_ref": MOD_ID + ":e", "params": {}}
    before = count(skill2)

    choices = []
    find_choice(skill2["effect"], choices)
    if len(choices) != 1:
        sys.exit("expected one e_flee choice in E's pulse, found %d: the main pack's E changed, update this script"
                 % len(choices))
    choice = choices[0]
    escape, engage = json.dumps(choice["effect_buff"]), json.dumps(choice["effect_none"])
    if "league_camille_e_epick" not in escape or "league_camille_e_seek" not in engage:
        sys.exit("the e_flee choice no longer holds the escape / engage hold searches: update this script")
    choice["effect_buff"] = native("escape")
    choice["effect_none"] = native("engage")

    left = json.dumps(skill2)
    for gone in ("MoveToTarget", "league_camille_e_hook", "league_camille_e_seek", "league_camille_e_epick"):
        if gone in left:
            sys.exit("%s is still in E after the swap: update this script" % gone)

    out = os.path.join(ADDON, "override", "league_camille.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(TEXT)
    if missing:
        sys.exit("no wall-hook text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"skill2": TEXT[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT),
          "- E effect nodes %d -> %d" % (before, count(skill2)))


if __name__ == "__main__":
    main()
