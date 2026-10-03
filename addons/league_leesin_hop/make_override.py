"""Build the add-on's copy of Lee Sin from the main pack (Wild Rift style W dash v1).

    python addons/league_leesin_hop/make_override.py

Reads league/champion/league_leesin.data_champion and league/text/champion.i18n and writes
addons/league_leesin_hop/override/league_leesin.data_champion and .../text/champion.i18n:
the same kit with three changes -
  * R's approach when nobody stands behind the target (RushMoveToBack at tick 7) becomes the add-on's
    native league_leesin_hop:insec: W dashes to a spot behind the target (no ward, as in Wild Rift),
    so the kick at tick 17 sends him back toward Lee Sin's side;
  * passive_skill2 = league_leesin_hop:hop: once skill2 is learned, low on health with an enemy close
    W dashes away, and an enemy champion low on health running off gets chased with a W dash;
  * skill2's and R's tooltips point to description.league_leesin_hop.* (the texts with a
    "W dash test build" lead, so the tooltips in game show whether the override took).
Run it again whenever the main pack's Lee Sin changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_leesin_hop")
MOD_ID = "league_leesin_hop"
AD = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TEXT = {
    "skill2": {
        "zh-hans": "【W位移测试版】<#ff9028ff>天雷破<>：跃起捶地，周围敌人受到<#ff9028ff>60<> + "
                   f"{AD}<#ff9028ff>80% 攻击力<>的<#ff9028ff>物理伤害<>并被<#ef5350ff>减速<><#ffb900ff>40%<>，"
                   "持续<#ffb900ff>2秒<>。<#ff9028ff>铁布衫<>：<#6aff55ff>20% 吸血<>，持续<#ffb900ff>3秒<>。"
                   f"<#ff9028ff>连招<>：回音击后<#ffb900ff>2.5秒<>内先出一拳（{AD}<#ff9028ff>100%<>）。"
                   "<#ff9028ff>金钟罩<>：残血被追时 W 冲走，敌方残血逃跑时 W 追上。",
        "zh-hant": "【W位移測試版】<#ff9028ff>天雷破<>：躍起捶地，周圍敵人受到<#ff9028ff>60<> + "
                   f"{AD}<#ff9028ff>80% 攻擊力<>的<#ff9028ff>物理傷害<>並被<#ef5350ff>緩速<><#ffb900ff>40%<>，"
                   "持續<#ffb900ff>2秒<>。<#ff9028ff>鐵布衫<>：<#6aff55ff>20% 吸血<>，持續<#ffb900ff>3秒<>。"
                   f"<#ff9028ff>連招<>：回音擊後<#ffb900ff>2.5秒<>內先出一拳（{AD}<#ff9028ff>100%<>）。"
                   "<#ff9028ff>金鐘罩<>：殘血被追時 W 衝走，敵方殘血逃跑時 W 追上。",
        "en": "[W dash test build] <#ff9028ff>Tempest<>: Lee Sin smashes the ground, dealing <#ff9028ff>60<> + "
              f"{AD}<#ff9028ff>80% AD<> <#ff9028ff>physical damage<> and <#ef5350ff>slowing<> by <#ffb900ff>40%<> for "
              "<#ffb900ff>2s<>. <#ff9028ff>Iron Will<>: <#6aff55ff>20% life steal<> for <#ffb900ff>3s<>. "
              f"<#ff9028ff>Combo<>: within <#ffb900ff>2.5s<> of Resonating Strike he punches first ({AD}<#ff9028ff>100%<>). "
              "<#ff9028ff>Safeguard<>: low, he W-dashes away; a fleeing low enemy gets W-chased.",
        "ko": "[W 이동 테스트판] <#ff9028ff>폭풍<>: 땅을 내리쳐 주변 적에게 <#ff9028ff>60<> + "
              f"{AD}<#ff9028ff>공격력의 80%<> <#ff9028ff>물리 피해<>를 주고 <#ffb900ff>2초<> 동안 <#ffb900ff>40%<> "
              "<#ef5350ff>둔화<>. <#ff9028ff>철갑<>: <#ffb900ff>3초<> 동안 <#6aff55ff>생명력 흡수 20%<>. "
              f"<#ff9028ff>연계<>: 공명의 일격 후 <#ffb900ff>2.5초<> 안이면 먼저 주먹({AD}<#ff9028ff>100%<>). "
              "<#ff9028ff>방호<>: 빈사 시 W로 빠지고, 도망치는 빈사 적은 W로 쫓습니다.",
        "ja": "【W移動試験版】<#ff9028ff>テンペスト<>：地面を叩き周囲の敵に<#ff9028ff>60<> + "
              f"{AD}<#ff9028ff>攻撃力の80%<>の<#ff9028ff>物理ダメージ<>、<#ffb900ff>2秒<>間<#ffb900ff>40%<>"
              "<#ef5350ff>スロウ<>。<#ff9028ff>アイアンウィル<>：<#ffb900ff>3秒<>間<#6aff55ff>ライフスティール20%<>。"
              f"<#ff9028ff>連携<>：響掌撃の後<#ffb900ff>2.5秒<>以内なら先に一撃（{AD}<#ff9028ff>100%<>）。"
              "<#ff9028ff>守りの拳<>：瀕死ならWで離脱、逃げる瀕死の敵はWで追う。",
    },
    "ult": {
        "zh-hans": "【W位移测试版】<#ff9028ff>猛龙摆尾<>：把目标正面踢进身后的敌方英雄，身后没人则 W 冲到他身后<#ef5350ff>踢回<>己方："
                   f"<#ff9028ff>120<> + {AD}<#ff9028ff>130% 攻击力<>的<#ff9028ff>物理伤害<>，撞到的敌人受到<#ff9028ff>80<> + "
                   f"{AD}<#ff9028ff>80%<>伤害并<#ef5350ff>击飞<><#ffb900ff>0.75秒<>。<#ff9028ff>连招<>：飞踢追击或接天音波、回音击。",
        "zh-hant": "【W位移測試版】<#ff9028ff>猛龍擺尾<>：把目標正面踢進身後的敵方英雄，身後沒人則 W 衝到他身後<#ef5350ff>踢回<>己方："
                   f"<#ff9028ff>120<> + {AD}<#ff9028ff>130% 攻擊力<>的<#ff9028ff>物理傷害<>，撞到的敵人受到<#ff9028ff>80<> + "
                   f"{AD}<#ff9028ff>80%<>傷害並<#ef5350ff>擊飛<><#ffb900ff>0.75秒<>。<#ff9028ff>連招<>：飛踢追擊或接天音波、回音擊。",
        "en": "[W dash test build] <#ff9028ff>Dragon's Rage<>: kicks the target into an enemy champion behind it, or W-dashes "
              f"behind it and kicks it <#ef5350ff>back<> to his allies: <#ff9028ff>120<> + {AD}<#ff9028ff>130% AD<> "
              f"<#ff9028ff>physical damage<>; enemies it hits take <#ff9028ff>80<> + {AD}<#ff9028ff>80% AD<> and are "
              "<#ef5350ff>knocked up<> <#ffb900ff>0.75s<>. <#ff9028ff>Combo<>: a flying kick, or Sonic Wave and Resonating Strike.",
        "ko": "[W 이동 테스트판] <#ff9028ff>용의 분노<>: 대상을 뒤의 적 챔피언에게 차거나, 뒤에 아무도 없으면 W로 대상 뒤로 가 "
              f"아군 쪽으로 <#ef5350ff>되찹니다<>: <#ff9028ff>120<> + {AD}<#ff9028ff>공격력의 130%<> <#ff9028ff>물리 피해<>, "
              f"부딪힌 적은 <#ff9028ff>80<> + {AD}<#ff9028ff>80%<> 피해와 <#ffb900ff>0.75초<> <#ef5350ff>에어본<>. "
              "<#ff9028ff>연계<>: 날아차기 추격 또는 음파·공명의 일격.",
        "ja": "【W移動試験版】<#ff9028ff>龍の怒り<>：対象を後ろの敵チャンピオンへ蹴り込む。後ろに誰もいなければWで背後に回り"
              f"味方側へ<#ef5350ff>蹴り返す<>：<#ff9028ff>120<> + {AD}<#ff9028ff>攻撃力の130%<>の<#ff9028ff>物理ダメージ<>、"
              f"ぶつかった敵に<#ff9028ff>80<> + {AD}<#ff9028ff>80%<>と<#ffb900ff>0.75秒<>の<#ef5350ff>ノックアップ<>。"
              "<#ff9028ff>連携<>：飛び蹴りか音波・響掌撃。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def swap_rush(node, counts):
    """R's RushMoveToBack (the jump behind the target) -> the native W dash behind it."""
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, dict) and value.get("type") == "RushMoveToBack":
                node[key] = {"type": "Native", "effect_ref": MOD_ID + ":insec"}
                counts["insec"] += 1
            else:
                swap_rush(value, counts)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            if isinstance(value, dict) and value.get("type") == "RushMoveToBack":
                node[i] = {"type": "Native", "effect_ref": MOD_ID + ":insec"}
                counts["insec"] += 1
            else:
                swap_rush(value, counts)


def main():
    src = os.path.join(ROOT, "league", "champion", "league_leesin.data_champion")
    with open(lp(src), encoding="utf-8") as f:
        champion = json.load(f)
    counts = {"insec": 0}
    swap_rush(champion["ult"], counts)
    if counts["insec"] != 1:
        sys.exit("expected one RushMoveToBack in R, found %d: the main pack's R changed, update this script"
                 % counts["insec"])
    if "RushMoveToBack" in json.dumps(champion):
        sys.exit("a RushMoveToBack is left outside R: update this script")
    if champion.get("passive_skill2"):
        sys.exit("the main pack's Lee Sin has a passive_skill2 now: update this script")
    champion["passive_skill2"] = {"passive_ref": MOD_ID + ":hop", "params": {}}
    for slot in ("skill2", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description.%s.%s" % (MOD_ID, slot)

    out = os.path.join(ADDON, "override", "league_leesin.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8") as f:
        main_text = json.load(f)
    missing = [(slot, lang) for slot in TEXT for lang in main_text if lang not in TEXT[slot]]
    if missing:
        sys.exit("no W dash text for %s" % missing)
    text = {lang: {"description": {MOD_ID: {slot: TEXT[slot][lang] for slot in TEXT}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT))


if __name__ == "__main__":
    main()
