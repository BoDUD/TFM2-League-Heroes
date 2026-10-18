"""Build the add-on's copy of Akshan from the main pack (per-target Dirty Fighting, missing-health Comeuppance, the
Scoundrels and the revive).

    python addons/league_akshan/make_override.py

Rebuilds Akshan with tools/kit/build_akshan.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_akshan.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_akshan/override/league_akshan.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the double shot, Avengerang, Heroic Swing, Comeuppance's channel and release);
  * every hit counts through league_akshan:hit (the third on the same target raises league_akshan_p_go);
  * R's bullets deal league_akshan:bullet (from the target's missing health);
  * passive = the add-on's league_akshan:rogue with the numbers of P (r_dmg, r_ratio, r_max, r_full, p_t);
  * the attack's, skill2's and ult's tooltips point to description.league_akshan.<slot> with the add-on's wording, a key
    of the add-on's own id, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Akshan changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_akshan")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_akshan as kit  # noqa: E402
import setup_akshan as setup  # noqa: E402

MOD_ID = "league_akshan"
HERO = "league_akshan"
SLOTS = ("attack", "skill2", "ult")
O, A, R, G, E = setup.O, setup.A, setup.R, setup.G, setup.E
phys, shield = setup.phys, setup.shield
TEXT = {
    "zh-hans": {
        "attack": "【扩展包】普攻开两枪。" + O + "无所不用" + E + "：对同一目标每打中3下，多造成" + phys("p_dmg", "p_ratio") + "物理伤害，英雄还给他" + shield() +
                  "护盾。" + O + "赴险夺人" + E + "：被围时伪装" + A + "{w_inv}秒" + E + "；杀了队友的敌人成为恶徒" + A + "60秒" + E + "，他参与击杀恶徒时，"
                  "被恶徒杀死的队友" + G + "1秒后复活" + E + "，他得100金。",
        "skill2": "【扩展包】甩出钩索朝敌方英雄荡过去，" + A + "{e_t}秒" + E + "内每" + A + "{e_every}秒" + E + "朝最近的敌人开一枪，造成" +
                  phys("e_dmg", "e_ratio") + "物理伤害，最后翻滚再开一枪。参与击杀英雄后冷却刷新。",
        "ult": "【扩展包】锁定受伤的敌方英雄蓄力" + A + "{r_ch}秒" + E + "，最多存{r_n}发，被" + R + "控制" + E + "会中断；打得死或目标要跑时提前开火。每发打中"
               "路上第一个敌人，造成" + phys("r_dmg", "r_ratio") + "物理伤害，目标每少1%生命伤害更高，少{r_full}%时{r_max}倍。",
    },
    "zh-hant": {
        "attack": "【擴充包】普攻開兩槍。" + O + "無賴之道" + E + "：對同一目標每打中3下，多造成" + phys("p_dmg", "p_ratio") + "物理傷害，英雄還給他" + shield() +
                  "護盾。" + O + "離經叛道" + E + "：被圍時偽裝" + A + "{w_inv}秒" + E + "；殺了隊友的敵人成為惡徒" + A + "60秒" + E + "，他參與擊殺惡徒時，"
                  "被惡徒殺死的隊友" + G + "1秒後復活" + E + "，他得100金。",
        "skill2": "【擴充包】甩出勾索朝敵方英雄盪過去，" + A + "{e_t}秒" + E + "內每" + A + "{e_every}秒" + E + "朝最近的敵人開一槍，造成" +
                  phys("e_dmg", "e_ratio") + "物理傷害，最後翻滾再開一槍。參與擊殺英雄後冷卻刷新。",
        "ult": "【擴充包】鎖定受傷的敵方英雄蓄力" + A + "{r_ch}秒" + E + "，最多存{r_n}發，被" + R + "控制" + E + "會中斷；打得死或目標要跑時提前開火。每發打中"
               "路上第一個敵人，造成" + phys("r_dmg", "r_ratio") + "物理傷害，目標每少1%生命傷害更高，少{r_full}%時{r_max}倍。",
    },
    "en": {
        "attack": "[Add-on] Two shots an attack. " + O + "Dirty Fighting" + E + ": every third hit on the same target deals " + phys("p_dmg", "p_ratio") +
                  " physical damage more, and a " + shield() + " shield on a champion. " + O + "Going Rogue" + E + ": camouflage for " + A + "{w_inv}s" + E +
                  " when surrounded; an ally's killer is a Scoundrel for " + A + "60s" + E + ": taking him down makes the allies he killed " +
                  G + "revive 1s later" + E + " (+100 gold).",
        "skill2": "[Add-on] Hooks and swings toward an enemy champion: for " + A + "{e_t}s" + E + " he shoots the nearest enemy every " + A + "{e_every}s" +
                  E + " for " + phys("e_dmg", "e_ratio") + " physical damage, then rolls off with a last shot. A champion takedown refreshes it.",
        "ult": "[Add-on] Locks onto a wounded enemy champion and charges for " + A + "{r_ch}s" + E + ", up to {r_n} bullets (" + R + "crowd control" + E +
               " stops it), firing early when they kill or he is escaping: each hits the first enemy in its path for " + phys("r_dmg", "r_ratio") +
               " physical damage, more the more health he has lost ({r_max}x at {r_full}% lost).",
    },
    "ko": {
        "attack": "[확장] 공격마다 두 발. " + O + "비열한 싸움" + E + ": 같은 대상 3회 적중마다 " + phys("p_dmg", "p_ratio") + " 물리 피해 추가, 챔피언이면 " +
                  shield() + " 보호막. " + O + "악당 처단" + E + ": 포위 시 " + A + "{w_inv}초" + E + " 위장; 아군을 죽인 적은 " + A + "60초" + E +
                  " 악당: 아크샨이 처치에 관여하면 그가 죽인 아군이 " + G + "1초 후 부활" + E + ", 아크샨 100골드.",
        "skill2": "[확장] 갈고리를 걸고 적 챔피언 쪽으로 날아감: " + A + "{e_t}초" + E + " 동안 " + A + "{e_every}초" + E + "마다 가장 가까운 적에게 " +
                  phys("e_dmg", "e_ratio") + " 물리 피해, 마지막에 한 발 더. 챔피언 처치 관여 시 초기화.",
        "ult": "[확장] 부상당한 적 챔피언을 조준해 " + A + "{r_ch}초" + E + " 충전, 최대 {r_n}발(" + R + "군중 제어" + E + " 시 중단), 처치 가능하거나 도망치면 "
               "바로 발사: 처음 맞는 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해, 잃은 체력에 비례해 증가({r_full}%에서 {r_max}배).",
    },
    "ja": {
        "attack": "【拡張】通常攻撃は2発。" + O + "ダーティーファイト" + E + "：同じ対象への3回目の命中で" + phys("p_dmg", "p_ratio") + "の物理ダメージ追加、"
                  "チャンピオンなら" + shield() + "のシールド。" + O + "義賊の流儀" + E + "：囲まれると" + A + "{w_inv}秒" + E + "迷彩；味方を倒した敵は" + A +
                  "60秒" + E + "悪党：倒すと味方が" + G + "1秒後に復活" + E + "、100ゴールド。",
        "skill2": "【拡張】フックで敵チャンピオンへスイング：" + A + "{e_t}秒" + E + "間、" + A + "{e_every}秒" + E + "毎に最も近い敵へ" + phys("e_dmg", "e_ratio") +
                  "の物理ダメージ、最後にもう1発。チャンピオンキル関与で解消。",
        "ult": "【拡張】負傷した敵チャンピオンを狙い" + A + "{r_ch}秒" + E + "チャージ、最大{r_n}発（" + R + "行動妨害" + E + "で中断）、倒せるか逃げる時は即発射："
               "最初に当たった敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージ、失った体力が多いほど増加（{r_full}%で{r_max}倍）。",
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
        sys.exit("the main pack's league_akshan differs from build_akshan.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":rogue":
        sys.exit("the copy has no league_akshan:rogue passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), r_full=p["r_full"], r_max=p["r_max"])
    texts = {lang: {slot: t[slot].format(**values) for slot in SLOTS} for lang, t in TEXT.items()}
    long = {f"{lang}.{slot}": setup.shown_length(TEXT[lang][slot]) for lang in TEXT for slot in SLOTS
            if setup.shown_length(TEXT[lang][slot]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{slot}": f"{setup.shown_length(TEXT[lang][slot])}/{setup.TOOLTIP_MAX[lang]}"
                              for lang in TEXT for slot in SLOTS})


if __name__ == "__main__":
    main()
