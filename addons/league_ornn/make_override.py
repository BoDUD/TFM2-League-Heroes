"""Build the add-on's copy of Ornn from the main pack (a real pillar, quakes on pillars and walls, Brittle per champion).

    python addons/league_ornn/make_override.py

Rebuilds Ornn with tools/kit/build_ornn.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_ornn.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_ornn/override/league_ornn.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (Bellows Breath in the attack, the fissure and the pillar's picture, the charge, the
    two rams);
  * passive = the add-on's league_ornn:forge (the pillar as terrain, his items' stats scaled, the masterwork) with the numbers of P the add-on uses (checked against
    src/lib.rs's constants);
  * the fissure's end calls league_ornn:pillar (the pillar's place), E records its start (league_ornn:from) and on contact
    asks league_ornn:charge for the quake (a pillar near or a wall ahead), the attack breaks Brittle through
    league_ornn:shatter on the champion that carries it;
  * the attack's, skill's and skill2's tooltips point to description.league_ornn.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Ornn changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_ornn")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_ornn as kit  # noqa: E402
import setup_ornn as setup  # noqa: E402

MOD_ID = "league_ornn"
HERO = "league_ornn"
SLOTS = ("attack", "skill", "skill2")
O, A, R, M, T, E = setup.O, setup.A, setup.R, setup.M, setup.T, setup.E
phys, hpp = setup.phys, setup.hpp
TEXT = {
    "zh-hans": {
        "attack": "【扩展包】" + O + "活体锻炉" + E + "：装备属性+{p_item}%，{p_master_lv}级起+{p_master}%、友方英雄+{p_ally}%。W/E/R使敌方英雄" + O + "易碎" + E + "，普攻打中易碎的英雄造成" + T + "{br_hp}%最大生命" + E + "真实伤害并" + R + "击飞" + E + "。" +
                  O + "风箱炎息" + E + "：每" + A + "{w_cd}秒" + E + "喷火，" + R + "不可阻挡" + E + "并获得护盾，造成" + hpp("w_sum", "w_hpsum", M) + "魔法伤害。",
        "skill": "【扩展包】砸地裂出一道裂隙，造成" + phys("q_dmg", "q_ratio") + "物理伤害并" + R + "减速{q_slow}%" + E + "，尽头升起挡路的熔岩柱，持续" + A + "{q_life}秒" + E + "。",
        "skill2": "【扩展包】冲向目标，造成" + hpp("e_dmg", "e_hp") + "物理伤害。撞上熔岩柱或墙时周围敌人" + R + "击飞" + A + "{e_up}秒" + E + E + "并受到" + hpp("e_q_dmg", "e_q_hp") + "物理伤害，英雄易碎。",
    },
    "zh-hant": {
        "attack": "【擴充包】" + O + "活火爐" + E + "：裝備屬性+{p_item}%，{p_master_lv}級起+{p_master}%、友方英雄+{p_ally}%。W/E/R使敵方英雄" + O + "焦化" + E + "，普攻打中焦化的英雄造成" + T + "{br_hp}%最大生命" + E + "真實傷害並" + R + "擊飛" + E + "。" +
                  O + "熾焰吹息" + E + "：每" + A + "{w_cd}秒" + E + "噴火，" + R + "不可阻擋" + E + "並獲得護盾，造成" + hpp("w_sum", "w_hpsum", M) + "魔法傷害。",
        "skill": "【擴充包】砸地裂出一道裂隙，造成" + phys("q_dmg", "q_ratio") + "物理傷害並" + R + "緩速{q_slow}%" + E + "，盡頭升起擋路的熔岩柱，持續" + A + "{q_life}秒" + E + "。",
        "skill2": "【擴充包】衝向目標，造成" + hpp("e_dmg", "e_hp") + "物理傷害。撞上熔岩柱或牆時周圍敵人" + R + "擊飛" + A + "{e_up}秒" + E + E + "並受到" + hpp("e_q_dmg", "e_q_hp") + "物理傷害，英雄焦化。",
    },
    "en": {
        "attack": "[Add-on] " + O + "Living Forge" + E + ": item stats +{p_item}% (from level {p_master_lv}: +{p_master}%, allies +{p_ally}%). W, E and R make enemy champions " + O + "Brittle" + E +
                  "; his attack on a Brittle champion deals " + T + "{br_hp}% of its max health" + E + " as true damage and " + R + "knocks it up" + E + ". " +
                  O + "Bellows Breath" + E + ": every " + A + "{w_cd}s" + E + " he breathes fire, " + R + "unstoppable" + E + " and shielded, dealing " +
                  hpp("w_sum", "w_hpsum", M) + " magic damage.",
        "skill": "[Add-on] Slams the ground: a fissure deals " + phys("q_dmg", "q_ratio") + " physical damage and " + R + "slows {q_slow}%" + E +
                 "; a magma pillar that blocks the way rises at its end for " + A + "{q_life}s" + E + ".",
        "skill2": "[Add-on] Charges the target, dealing " + hpp("e_dmg", "e_hp") + " physical damage. Slamming into a pillar or a wall: enemies "
                  "around are " + R + "knocked up" + E + " for " + A + "{e_up}s" + E + " and take " + hpp("e_q_dmg", "e_q_hp") + " physical damage, "
                  "champions made Brittle.",
    },
    "ko": {
        "attack": "[확장] " + O + "간이 대장간" + E + ": 아이템 능력치 +{p_item}%({p_master_lv}레벨부터 +{p_master}%, 아군 +{p_ally}%). W/E/R이 적 챔피언을 " + O + "불안정" + E + " 상태로 만들고, "
                  "불안정한 챔피언을 기본 공격하면 " + T + "최대 체력 {br_hp}%" + E + " 고정 피해와 " + R + "에어본" + E + ". " +
                  O + "불꽃 풀무질" + E + ": " + A + "{w_cd}초" + E + "마다 불을 뿜어 " + R + "저지 불가" + E + "·보호막, " + hpp("w_sum", "w_hpsum", M) + " 마법 피해.",
        "skill": "[확장] 땅을 내리쳐 균열이 " + phys("q_dmg", "q_ratio") + " 물리 피해와 " + R + "{q_slow}% 둔화" + E + ". 끝에 길을 막는 용암 기둥이 " + A + "{q_life}초" + E + " 솟음.",
        "skill2": "[확장] 대상에게 돌진해 " + hpp("e_dmg", "e_hp") + " 물리 피해. 기둥이나 벽에 부딪히면 주변 적을 " + R + "{e_up}초 에어본" + E + "시키며 " +
                  hpp("e_q_dmg", "e_q_hp") + " 물리 피해, 챔피언은 불안정.",
    },
    "ja": {
        "attack": "【拡張】" + O + "歩く鍛冶場" + E + "：装備の能力値+{p_item}%（{p_master_lv}レベルから+{p_master}%、味方+{p_ally}%）。W/E/Rで敵チャンピオンを" + O + "脆弱" + E + "にし、脆弱な相手への通常攻撃は" +
                  T + "最大体力の{br_hp}%" + E + "の確定ダメージと" + R + "ノックアップ" + E + "。" + O + "ふいごの息" + E + "：" + A + "{w_cd}秒" + E + "ごとに炎を吐き、" +
                  R + "阻害無効" + E + "とシールド、" + hpp("w_sum", "w_hpsum", M) + "の魔法ダメージ。",
        "skill": "【拡張】地面を叩き、亀裂が" + phys("q_dmg", "q_ratio") + "の物理ダメージと" + R + "{q_slow}%スロウ" + E + "。終点に道を塞ぐ溶岩の柱が" + A + "{q_life}秒" + E + "立つ。",
        "skill2": "【拡張】対象へ突進し" + hpp("e_dmg", "e_hp") + "の物理ダメージ。柱か壁に当たると周囲の敵を" + R + "{e_up}秒ノックアップ" + E + "して" +
                  hpp("e_q_dmg", "e_q_hp") + "の物理ダメージ、チャンピオンは脆弱。",
    },
}

CONSTS = {k: k.upper() for k in ("q_life", "br_hp", "br_up", "br_kb_speed", "br_kb_t", "e_quake_r", "e_anim", "p_item",
                                  "p_master", "p_ally", "p_master_lv")}
RANGES = {"E_RANGE": "e_range", "Q_RANGE": "q_range"}


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
        sys.exit("the main pack's league_ornn differs from build_ornn.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in list(CONSTS.items()) + [(v, k) for k, v in RANGES.items()]:
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P[{key!r}] = {p[key]}: update the add-on")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":forge":
        sys.exit("the copy has no league_ornn:forge passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values.update({k: p[k] for k in ("p_item", "p_master", "p_ally", "p_master_lv")})
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in TEXT.items() for k, t in d.items()
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
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
