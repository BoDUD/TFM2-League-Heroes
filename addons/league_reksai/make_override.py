"""Build the add-on's copy of Rek'Sai from the main pack (the burrowed body, tunnels, Void Rush by real health).

    python addons/league_reksai/make_override.py

Rebuilds Rek'Sai with tools/kit/build_reksai.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_reksai.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_reksai/override/league_reksai.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (every hit, picture and sound; the prey marks; W's w_go / w_land signals);
  * the watch no longer arms Void Rush (r_ok) by crowd control or an ally: only the add-on does, for a killable prey;
  * passive = the add-on's league_reksai:fury with the numbers of P;
  * the attack's, skill2's and ult's tooltips point to description.league_reksai.attack / .skill2 / .ult with the
    add-on's wording (keys of the add-on's own id), so the tooltip in game shows whether the override took.
The burrowed body needs no data: the add-on's passive sets league_reksai_burrow and its display hook reads it.
Every other champion stays untouched. Run it again whenever the main pack's Rek'Sai changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_reksai")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_reksai as kit  # noqa: E402
import setup_reksai as setup  # noqa: E402

MOD_ID = "league_reksai"
HERO = "league_reksai"
O, A, R, G, E = setup.O, setup.A, setup.R, setup.G, setup.E
phy = setup.phy
TRUE = setup.TRUE
SLOTS = ("attack", "skill2", "ult")
# lang -> the add-on's attack, skill2 and ult texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】爪咬。" + O + "艾克塞之怒" + E + "：命中攒怒气，满怒时下一口是" + O + "狂野之噬" + E + "（" + TRUE + G + "真实伤害" + E + "）。脱离战斗赶路时" +
                  O + "遁地" + E + "：整个身体钻进土里、移速提高，按怒气回复生命，敌人靠近就破土。",
        "skill2": "【附加包】钻地冲到目标脚下破土：" + phy("w_dmg", "w_ratio") + O + "物理伤害" + E + "并" + R + "击飞{w_up}秒" + E + "。起点和落点连成" + O +
                  "隧道" + E + "（最多8个入口，敌方英雄站上去会踩塌）；残血或突袭时钻隧道。",
        "ult": "【附加包】" + O + "猎物" + E + "能被打死、残血（40%以下）或被控（70%以下）时才放：钻进地底" + A + "{r_hide}秒" + E + "，再扑出造成" + phy("r_dmg", "r_ratio") +
               "+目标最大生命{r_hp}%" + O + "物理伤害" + E + "。",
    },
    "zh-hant": {
        "attack": "【擴充包】爪咬。" + O + "憤怒沙蟲" + E + "：命中累積怒氣，滿怒時下一口是" + O + "狂食" + E + "（" + TRUE + G + "真實傷害" + E + "）。脫離戰鬥趕路時" +
                  O + "深掘" + E + "：整個身體鑽進土裡、移速提高，按怒氣回復生命，敵人靠近就破土。",
        "skill2": "【擴充包】鑽地衝到目標腳下破土：" + phy("w_dmg", "w_ratio") + O + "物理傷害" + E + "並" + R + "擊飛{w_up}秒" + E + "。起點和落點連成" + O +
                  "隧道" + E + "（最多8個入口，敵方英雄站上去會踩塌）；殘血或突襲時鑽隧道。",
        "ult": "【擴充包】" + O + "獵物" + E + "能被打死、殘血（40%以下）或被控（70%以下）時才施放：鑽進地底" + A + "{r_hide}秒" + E + "，再撲出造成" + phy("r_dmg", "r_ratio") +
               "+目標最大生命{r_hp}%" + O + "物理傷害" + E + "。",
    },
    "en": {
        "attack": "[Add-on] Claws and bites. " + O + "Fury of the Xer'Sai" + E + ": hits build Fury; at full Fury her next bite is " + O +
                  "Furious Bite" + E + " (" + TRUE + " " + G + "true damage" + E + "). Out of combat on the move she " + O + "burrows" + E +
                  ": her whole body under the earth, faster, healing by her Fury, and comes up when enemies near.",
        "skill2": "[Add-on] Tunnels under the target and bursts up: " + phy("w_dmg", "w_ratio") + " " + O + "physical damage" + E + ", " + R +
                  "knocking up {w_up}s" + E + ". Start and landing become a " + O + "tunnel" + E + " (8 entrances at most; enemy champions "
                  "standing on one cave it in); she takes them to escape or to strike.",
        "ult": "[Add-on] Only when one of her " + O + "Prey" + E + " would die, is below 40% health, or is held below 70%: she goes under for " + A + "{r_hide}s" + E + " and lunges for " +
               phy("r_dmg", "r_ratio") + " + {r_hp}% of its max health " + O + "physical damage" + E + ".",
    },
    "ko": {
        "attack": "[확장] 할퀴고 문다. " + O + "제르사이의 분노" + E + ": 적중 시 분노, 가득하면 다음 공격이 " + O + "성난 이빨" + E + "(" + TRUE + "의 " + G +
                  "고정 피해" + E + "). 비전투 이동 중 " + O + "매복" + E + ": 몸 전체가 땅속으로, 더 빠르게, 분노로 회복, 적이 다가오면 솟아오름.",
        "skill2": "[확장] 대상 발밑으로 파고들어 솟아오름: " + phy("w_dmg", "w_ratio") + "의 " + O + "물리 피해" + E + "와 " + R + "{w_up}초 에어본" + E +
                  ". 출발점과 도착점이 " + O + "땅굴" + E + "이 됨(입구 최대 8개, 적 챔피언이 밟으면 무너짐); 도주나 기습에 사용.",
        "ult": "[확장] " + O + "먹잇감" + E + "을 처치할 수 있거나 체력 40% 이하, 또는 군중 제어 중 70% 이하일 때만: " + A + "{r_hide}초" + E + " 땅속 후 덮쳐 " + phy("r_dmg", "r_ratio") +
               " + 대상 최대 체력 {r_hp}%의 " + O + "물리 피해" + E + ".",
    },
    "ja": {
        "attack": "【拡張】爪と牙で攻撃。" + O + "ゼル＝サイの怒り" + E + "：命中で怒り、最大時の次の攻撃は" + O + "激情の牙" + E + "（" + TRUE + "の" + G +
                  "確定ダメージ" + E + "）。非戦闘の移動中は" + O + "潜伏" + E + "：全身が地中へ、速く、怒りで回復、敵が近づくと浮上。",
        "skill2": "【拡張】対象の足元へ潜って襲撃：" + phy("w_dmg", "w_ratio") + "の" + O + "物理ダメージ" + E + "と" + R + "{w_up}秒ノックアップ" + E +
                  "。出発点と着地点が" + O + "トンネル" + E + "に（入口最大8、敵チャンピオンが踏むと崩れる）。逃走や奇襲に使う。",
        "ult": "【拡張】" + O + "獲物" + E + "を倒せる、体力40%以下、またはCC中で70%以下の時だけ：" + A + "{r_hide}秒" + E + "地中へ、飛び出して" + phy("r_dmg", "r_ratio") +
               "+対象の最大体力{r_hp}%の" + O + "物理ダメージ" + E + "。",
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
        sys.exit("the main pack's league_reksai differs from build_reksai.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":fury":
        sys.exit("the copy has no league_reksai:fury passive: update this script")
    if json.dumps(champion["ult"]).count('"league_reksai_r_ok"') != 1:
        sys.exit("the copy's ult should read r_ok once and nothing else set it: update this script")
    text = json.dumps(champion)
    if text.count('"league_reksai_r_ok"') != 1:
        sys.exit("the copy still arms r_ok in the data: update this script")
    for slot in SLOTS:
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
