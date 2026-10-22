"""Build the add-on's copy of Qiyana from the main pack (the element by the terrain beside her, else by the situation,
Royal Privilege per enemy, Edge of Ixtal's rock execute).

    python addons/league_qiyana/make_override.py

Rebuilds Qiyana with tools/kit/build_qiyana.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_qiyana.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_qiyana/override/league_qiyana.data_champion and
.../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * Terrashape's enchant is the Native league_qiyana:element (the element by the terrain beside her - else by the situation - instead of the cycle), every
    hit's Royal Privilege the Native league_qiyana:royal (each enemy once per rp_rest ticks), Edge of Ixtal's rock bonus
    the Native league_qiyana:rock (twice the bonus under q_exec% health, none above);
  * passive = league_qiyana:empress (it keeps these numbers for the natives, passive.params);
  * the attack's, the skill's and the skill2's tooltips (description.league_qiyana.<slot>, keys of the add-on's own id)
    say what the add-on changes, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Qiyana changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_qiyana")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_qiyana as kit  # noqa: E402
import setup_qiyana as setup  # noqa: E402

MOD_ID = "league_qiyana"
HERO = "league_qiyana"
O, M, A, R, E = setup.O, setup.M, setup.A, setup.R, setup.E
phys, mag = setup.phys, setup.mag
# src/lib.rs Params field -> P key
PARAMS = ("rp_dmg", "rp_ratio", "rp_rest", "q_rock", "q_rock_r", "q_exec", "w_as")
# lang -> the add-on's attack, skill and skill2 texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】挥环攻击。" + O + "凌人贵气" + E + "：对每个敌人" + A + "{rp_rest}秒" + E + "内的首次命中额外造成" +
                  phys("rp_dmg", "rp_ratio") + "物理伤害。武器附有元素时攻速+{w_as}%，攻击额外造成" + mag("w_on", "w_on_r") + "魔法伤害。",
        "skill": "【附加包】挥环横扫前方，造成" + phys("q_dmg", "q_ratio") + "物理伤害。消耗元素：河流" + R + "定身" + E + A + "{q_root}秒" + E +
                 "后减速{q_slow}%；岩石对生命低于{q_exec}%的敌人额外造成" + phys("q_rock2", "q_rock_r2") + "；草丛伪装" + A + "{q_inv}秒" + E +
                 "并加速{q_ms}%。",
        "skill2": "【附加包】突进到敌人身上，造成" + phys("e_dmg", "e_ratio") + "物理伤害；" + O + "方圆塑令" + E + "按身边地形附上元素：草丛选草丛，"
                  "墙选岩石，河道选河流；身边都没有就按局势选（自己残血草丛，残血英雄岩石，其他英雄河流，野怪小兵岩石）；并刷新以绪塔尔之锋。",
    },
    "zh-hant": {
        "attack": "【附加包】揮環攻擊。" + O + "皇家特權" + E + "：對每個敵人" + A + "{rp_rest}秒" + E + "內的首次命中額外造成" +
                  phys("rp_dmg", "rp_ratio") + "物理傷害。武器附有元素時攻速+{w_as}%，攻擊額外造成" + mag("w_on", "w_on_r") + "魔法傷害。",
        "skill": "【附加包】揮環橫掃前方，造成" + phys("q_dmg", "q_ratio") + "物理傷害。消耗元素：河流" + R + "定身" + E + A + "{q_root}秒" + E +
                 "後緩速{q_slow}%；岩石對生命低於{q_exec}%的敵人額外造成" + phys("q_rock2", "q_rock_r2") + "；草叢偽裝" + A + "{q_inv}秒" + E +
                 "並加速{q_ms}%。",
        "skill2": "【附加包】突進到敵人身上，造成" + phys("e_dmg", "e_ratio") + "物理傷害；" + O + "元素之形" + E + "依身邊地形附上元素：草叢選草叢，"
                  "牆選岩石，河道選河流；身邊都沒有就依局勢選（自己殘血草叢，殘血英雄岩石，其他英雄河流，野怪小兵岩石）；並刷新伊克斯塔爾迴旋刀。",
    },
    "en": {
        "attack": "[Add-on] A swing of her ring blade. " + O + "Royal Privilege" + E + ": her first hit on each enemy within " + A +
                  "{rp_rest}s" + E + " deals " + phys("rp_dmg", "rp_ratio") + " physical damage more. While her ring holds an element "
                  "she has +{w_as}% attack speed and her attacks deal " + mag("w_on", "w_on_r") + " magic damage more.",
        "skill": "[Add-on] Sweeps the ring through the enemies before her for " + phys("q_dmg", "q_ratio") + " physical damage, "
                 "spending her element: river " + R + "roots" + E + " for " + A + "{q_root}s" + E + " then slows {q_slow}%; rock deals " +
                 phys("q_rock2", "q_rock_r2") + " more to enemies under {q_exec}% health; grass camouflages her for " + A +
                 "{q_inv}s" + E + " with +{q_ms}% move speed.",
        "skill2": "[Add-on] Dashes onto an enemy for " + phys("e_dmg", "e_ratio") + " physical damage. " + O + "Terrashape" + E +
                  " takes the element from the terrain beside her: brush gives grass, a wall rock, the river river; with none near, "
                  "the fight picks: grass when she is low, rock on a wounded champion, a monster or a minion, river on any other "
                  "champion; Edge of Ixtal refreshed.",
    },
    "ko": {
        "attack": "[확장] 고리 칼날로 공격. " + O + "왕가의 특권" + E + ": 적마다 " + A + "{rp_rest}초" + E + " 안의 첫 적중이 " +
                  phys("rp_dmg", "rp_ratio") + " 물리 피해 추가. 무기에 원소가 깃들면 공격 속도 +{w_as}%, 공격이 " + mag("w_on", "w_on_r") +
                  " 마법 피해 추가.",
        "skill": "[확장] 고리로 앞쪽을 베어 " + phys("q_dmg", "q_ratio") + " 물리 피해, 원소 소모: 강 " + A + "{q_root}초" + E + " " + R + "속박" + E +
                 " 후 {q_slow}% 둔화, 바위 체력 {q_exec}% 미만의 적에게 " + phys("q_rock2", "q_rock_r2") + " 추가, 풀숲 " + A + "{q_inv}초" + E +
                 " 위장과 이동 속도 +{q_ms}%.",
        "skill2": "[확장] 적에게 돌진해 " + phys("e_dmg", "e_ratio") + " 물리 피해. " + O + "대지창조" + E + "가 주변 지형으로 원소 선택: 풀숲은 "
                  "풀숲, 벽은 바위, 강은 강; 주변에 없으면 상황에 따라: 위험하면 풀숲, 약한 챔피언·몬스터·미니언에 바위, 다른 챔피언에 강; "
                  "이쉬탈의 칼날 초기화.",
    },
    "ja": {
        "attack": "【拡張】リングで攻撃。" + O + "女帝の威風" + E + "：敵ごとに" + A + "{rp_rest}秒" + E + "以内の最初の命中が" +
                  phys("rp_dmg", "rp_ratio") + "の物理ダメージを追加。武器にエレメントがある間、攻撃速度+{w_as}%、攻撃が" +
                  mag("w_on", "w_on_r") + "の魔法ダメージを追加。",
        "skill": "【拡張】リングで前方を薙ぎ" + phys("q_dmg", "q_ratio") + "の物理ダメージ、エレメントを消費：川は" + A + "{q_root}秒" + E + R +
                 "スネア" + E + "後{q_slow}%スロウ、岩は体力{q_exec}%未満の敵に" + phys("q_rock2", "q_rock_r2") + "追加、草むらは" + A +
                 "{q_inv}秒" + E + "迷彩と移動速度+{q_ms}%。",
        "skill2": "【拡張】敵へ突進し" + phys("e_dmg", "e_ratio") + "の物理ダメージ。" + O + "大地の力" + E + "が近くの地形でエレメントを選ぶ："
                  "草むらは草むら、壁は岩、川は川。近くに無ければ状況で：危ない時は草むら、弱った敵や中立・ミニオンには岩、他のチャンピオンには川。"
                  "イシュタルの切先も再使用可能に。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """Params::default() in src/lib.rs as {field: value}."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (rp_dmg: .*?) \}", src)
    return {k.strip(): int(v) for k, v in (kv.split(":") for kv in m.group(1).split(","))}


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_qiyana differs from build_qiyana.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_qiyana.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":empress":
        sys.exit("the copy has no league_qiyana:empress passive: update this script")
    text = json.dumps(champion)
    for ref in ("element", "royal", "rock"):
        if f'"{MOD_ID}:{ref}"' not in text:
            sys.exit(f"the copy lacks the Native {MOD_ID}:{ref}: update this script")
    if '"league_qiyana_nx_w"' in text or '"league_qiyana_rp_cd"' in text:
        sys.exit("the copy still carries the element cycle or the caster-wide rest: update this script")
    for slot in ("attack", "skill", "skill2"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), rp_rest=setup.secs(p["rp_rest"]), q_exec=p["q_exec"], q_rock2=2 * p["q_rock"],
                  q_rock_r2=2 * p["q_rock_r"])
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
