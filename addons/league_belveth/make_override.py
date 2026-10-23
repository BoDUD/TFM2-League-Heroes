"""Build the add-on's copy of Bel'Veth from the main pack (the storm at her real low health, lavender kept through death).

    python addons/league_belveth/make_override.py

Rebuilds Bel'Veth with tools/kit/build_belveth.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_belveth.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_belveth/override/league_belveth.data_champion
and .../text/champion.i18n: the build with native=1 -
  * Royal Maelstrom (in the true form) reads the flag `league_belveth_low` (the main pack's stand-in: two enemy
    champions on her);
  * passive = league_belveth:banquet (params: e_low, l_max), which raises the flag every tick she is under e_low%
    health and puts her lavender stacks back after a death;
  * the attack's and the ult's tooltips (keys of the add-on's own id) say both rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Bel'Veth changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_belveth")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_belveth as kit  # noqa: E402
import setup_belveth as setup  # noqa: E402

MOD_ID = "league_belveth"
HERO = "league_belveth"
phys, t, n, cc, hl = setup.phys, setup.t, setup.n, setup.cc, setup.hl
# lang -> the add-on's attack and ult texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】用翼刃劈砍，出手很快。" + n("溶烛化紫") + "：每放一个技能攻速+{p_as}%（" + t("{p_t}秒") + "）；"
                  "参与击杀敌方英雄后永久攻速+{l_as}%（最多" + t("{l_max}层") + "，死亡后保留）。",
        "ult": "【附加包】吞下珊瑚爆开：周围敌人受" + phys("r_dmg", "r_ratio") + "物理伤害并" + cc("减速") + "{r_slow}%；化为真身" +
               t("{r_t}秒") + "：生命+{r_hp}%、攻击距离增加、攻速+{r_as}%、移速+{r_ms}%。真身生命低于{e_low}%时化为" +
               n("搠面皇锋") + "：原地" + t("{e_t}秒") + "减伤{e_dr}%、" + hl("吸血{e_vamp}%") + "。",
    },
    "zh-hant": {
        "attack": "【附加包】用翼刃劈砍，出手很快。" + n("魂斷紫海") + "：每施放一個技能攻速+{p_as}%（" + t("{p_t}秒") + "）；"
                  "參與擊殺敵方英雄後永久攻速+{l_as}%（最多" + t("{l_max}層") + "，死亡後保留）。",
        "ult": "【附加包】吞下珊瑚爆開：周圍敵人受" + phys("r_dmg", "r_ratio") + "物理傷害並" + cc("緩速") + "{r_slow}%；化為真身" +
               t("{r_t}秒") + "：生命+{r_hp}%、攻擊距離增加、攻速+{r_as}%、移速+{r_ms}%。真身生命低於{e_low}%時化為" +
               n("女皇風暴") + "：原地" + t("{e_t}秒") + "減傷{e_dr}%、" + hl("吸血{e_vamp}%") + "。",
    },
    "en": {
        "attack": "[Add-on] Fast slashes of her wing-blades. " + n("Death in Lavender") + ": every spell gives {p_as}% attack "
                  "speed for " + t("{p_t}s") + "; each enemy champion takedown adds {l_as}% attack speed for good (up to " +
                  t("{l_max} stacks") + ", kept through death).",
        "ult": "[Add-on] Eats the void coral: it bursts round her for " + phys("r_dmg", "r_ratio") + " physical damage and a "
               "{r_slow}% " + cc("slow") + "; she takes her true form for " + t("{r_t}s") + ": +{r_hp}% health, more attack "
               "range, +{r_as}% attack speed, +{r_ms}% move speed. Under {e_low}% health in it she becomes " +
               n("Royal Maelstrom") + ": rooted for " + t("{e_t}s") + ", {e_dr}% less damage taken, " +
               hl("{e_vamp}% life steal") + ".",
    },
    "ko": {
        "attack": "[확장] 날개 칼날로 빠르게 벤다. " + n("연보랏빛 죽음") + ": 스킬을 쓸 때마다 " + t("{p_t}초") + " 동안 공격 속도 "
                  "+{p_as}%; 적 챔피언 처치 관여 시 공격 속도 영구 +{l_as}%(최대 " + t("{l_max}중첩") + ", 죽어도 유지).",
        "ult": "[확장] 공허 산호를 삼켜 터뜨림: 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해와 {r_slow}% " + cc("둔화") +
               "; " + t("{r_t}초") + " 동안 진정한 모습: 체력 +{r_hp}%, 사거리 증가, 공격 속도 +{r_as}%, 이동 속도 +{r_ms}%. "
               "체력 {e_low}% 미만이면 " + n("여제의 소용돌이") + ": " + t("{e_t}초") + " 동안 제자리에서 받는 "
               "피해 {e_dr}% 감소, " + hl("생명력 흡수 {e_vamp}%") + ".",
    },
    "ja": {
        "attack": "【拡張】翼の刃で素早く斬る。" + n("死のラベンダー") + "：スキルを使うたび" + t("{p_t}秒") + "攻撃速度+{p_as}%；"
                  "敵チャンピオンのキル/アシストで攻撃速度が永続+{l_as}%（最大" + t("{l_max}スタック") + "、死んでも残る）。",
        "ult": "【拡張】ヴォイドコーラルを喰らい炸裂：周囲の敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージと{r_slow}%" +
               cc("スロウ") + "。" + t("{r_t}秒") + "真の姿：体力+{r_hp}%、射程増加、攻撃速度+{r_as}%、移動速度+{r_ms}%。真の姿で"
               "体力{e_low}%未満なら" + n("ロイヤルストーム") + "：" + t("{e_t}秒") + "その場で被ダメージ-{e_dr}%、" +
               hl("ライフスティール{e_vamp}%") + "。",
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
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    return {k.strip(): int(v.strip().rstrip(",")) for k, v in re.findall(r"(\w+): (\d+),?", m.group(1))}


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_belveth differs from build_belveth.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_belveth.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":banquet":
        sys.exit("the copy has no league_belveth:banquet passive: update this script")
    if '"league_belveth_low"' not in json.dumps(champion):
        sys.exit("the copy's storm does not read league_belveth_low: update this script")
    for slot in ("attack", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), e_low=p["e_low"])
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
