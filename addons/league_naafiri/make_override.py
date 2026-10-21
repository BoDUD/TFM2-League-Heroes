"""Build the add-on's copy of Naafiri from the main pack (the second dagger's execute, the pounce again on every
takedown, a smart ult, four hounds in the roar).

    python addons/league_naafiri/make_override.py

Rebuilds Naafiri with tools/kit/build_naafiri.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_naafiri.data_champion byte for byte (so the copy never drifts from the shipped kit), checks
that the AI hook's constants in src/lib.rs are P's numbers, and writes addons/league_naafiri/override/
league_naafiri.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * the second dagger's damage is the Native league_naafiri:q2 (up to q_exec% more by the target's missing health);
  * no takedown window: the pounce arms `r_armed` and passive = league_naafiri:pack (the recast on every takedown);
  * the skill's and the ult's tooltips (description.league_naafiri.skill / .ult, keys of the add-on's own id) say what
    the add-on changes, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Naafiri changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_naafiri")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_naafiri as kit  # noqa: E402
import setup_naafiri as setup  # noqa: E402

MOD_ID = "league_naafiri"
HERO = "league_naafiri"
O, G, A, R, E = setup.O, setup.G, setup.A, setup.R, setup.E
phys, grn = setup.phys, setup.grn
# src/lib.rs constant -> P key
CONSTS = {"R_RANGE": "r_range", "R_DMG": "r_dmg", "R_RATIO": "r_ratio", "Q_DMG": "q_dmg", "Q_RATIO": "q_ratio",
          "Q_B_DMG": "q_b_dmg", "Q_B_RATIO": "q_b_ratio", "Q2_DMG": "q2_dmg", "Q2_RATIO": "q2_ratio", "E_DMG": "e_dmg",
          "E_RATIO": "e_ratio", "E2_DMG": "e2_dmg", "E2_RATIO": "e2_ratio", "PK_DMG": "pk_dmg", "PK_RATIO": "pk_ratio",
          "ROAR_AD": "roar_ad"}
# lang -> the add-on's skill and ult texts
NATIVE = {
    "zh-hans": {
        "skill": "【附加包】掷出匕首，造成" + phys("q_dmg", "q_ratio") + "物理伤害并流血" + A + "{q_bleed}秒" + E + "；狗群扑向命中的英雄。" + A +
                 "{q_win}秒" + E + "内下次普攻掷出第二把匕首，造成" + phys("q2_dmg", "q2_ratio") + "，目标每损失1%生命多{q_exec_pct}%伤害，"
                 "命中英雄回复" + grn("q_heal", "q_heal_r") + "生命。",
        "ult": "【附加包】" + O + "暴吼" + E + "：" + A + "{r_imm}秒" + E + "不可选取，狗群翻倍、攻击力+{roar_ad}%、移速+{roar_ms}%；随后扑向敌方英雄，造成" +
               phys("r_dmg", "r_ratio") + "物理伤害、" + R + "减速" + E + "并降低{r_shred}%护甲。" + A + "{r_win}秒" + E + "内每次参与击杀都可再扑一次，"
               "获得" + grn("r_sh", "r_sh_r") + "护盾。",
    },
    "zh-hant": {
        "skill": "【附加包】擲出匕首，造成" + phys("q_dmg", "q_ratio") + "物理傷害並流血" + A + "{q_bleed}秒" + E + "；犬群撲向命中的英雄。" + A +
                 "{q_win}秒" + E + "內下次普攻擲出第二把匕首，造成" + phys("q2_dmg", "q2_ratio") + "，目標每損失1%生命多{q_exec_pct}%傷害，"
                 "命中英雄回復" + grn("q_heal", "q_heal_r") + "生命。",
        "ult": "【附加包】" + O + "獵犬嚎殺" + E + "：" + A + "{r_imm}秒" + E + "無法被選取，犬群加倍、攻擊力+{roar_ad}%、移速+{roar_ms}%；隨後撲向敵方英雄，造成" +
               phys("r_dmg", "r_ratio") + "物理傷害、" + R + "緩速" + E + "並降低{r_shred}%護甲。" + A + "{r_win}秒" + E + "內每次參與擊殺都可再撲一次，"
               "獲得" + grn("r_sh", "r_sh_r") + "護盾。",
    },
    "en": {
        "skill": "[Add-on] Hurls a dagger for " + phys("q_dmg", "q_ratio") + " physical damage and a bleed over " + A + "{q_bleed}s" + E +
                 "; her pack leaps on a champion hit. Within " + A + "{q_win}s" + E + " her next attack hurls the second dagger for " +
                 phys("q2_dmg", "q2_ratio") + ", {q_exec_pct}% more for every 1% of health the target has lost, healing her " +
                 grn("q_heal", "q_heal_r") + " on a champion.",
        "ult": "[Add-on] " + O + "The Call of the Pack" + E + ": untargetable for " + A + "{r_imm}s" + E + ", a pack twice as big, "
               "+{roar_ad}% attack and +{roar_ms}% move speed. Then she pounces on an enemy champion for " + phys("r_dmg", "r_ratio") +
               " physical damage, a " + R + "slow" + E + " and -{r_shred}% armour. Every takedown within " + A + "{r_win}s" + E +
               " lets her pounce again with a " + grn("r_sh", "r_sh_r") + " shield.",
    },
    "ko": {
        "skill": "[확장] 단검을 던져 " + phys("q_dmg", "q_ratio") + " 물리 피해와 " + A + "{q_bleed}초" + E + " 출혈; 맞힌 챔피언에게 무리가 덤벼듦. " +
                 A + "{q_win}초" + E + " 안에 다음 공격은 두 번째 단검으로 " + phys("q2_dmg", "q2_ratio") + ", 대상이 잃은 체력 1%당 피해 "
                 "{q_exec_pct}% 증가, 챔피언 적중 시 체력 " + grn("q_heal", "q_heal_r") + " 회복.",
        "ult": "[확장] " + O + "무리의 부름" + E + ": " + A + "{r_imm}초" + E + " 대상 지정 불가, 무리 두 배, 공격력 +{roar_ad}%, 이동 속도 +{roar_ms}%. "
               "이어서 적 챔피언에게 덮쳐 " + phys("r_dmg", "r_ratio") + " 물리 피해, " + R + "둔화" + E + ", 방어력 -{r_shred}%. " + A +
               "{r_win}초" + E + " 안에 처치 관여할 때마다 " + grn("r_sh", "r_sh_r") + " 보호막과 함께 다시 덮침.",
    },
    "ja": {
        "skill": "【拡張】短剣を投げ" + phys("q_dmg", "q_ratio") + "の物理ダメージと" + A + "{q_bleed}秒" + E + "の出血、当たったチャンピオンに群れが"
                 "食らいつく。" + A + "{q_win}秒" + E + "以内の次の攻撃で二本目を投げ" + phys("q2_dmg", "q2_ratio") + "、対象の失った体力1%ごとに"
                 "{q_exec_pct}%増、チャンピオンなら体力" + grn("q_heal", "q_heal_r") + "回復。",
        "ult": "【拡張】" + O + "群れの呼び声" + E + "：" + A + "{r_imm}秒" + E + "対象指定不可、群れが倍、攻撃力+{roar_ad}%、移動速度+{roar_ms}%。"
               "続けて敵チャンピオンに飛びかかり" + phys("r_dmg", "r_ratio") + "の物理ダメージ、" + R + "スロウ" + E + "、物防-{r_shred}%。" + A +
               "{r_win}秒" + E + "以内のキル関与ごとに" + grn("r_sh", "r_sh_r") + "のシールドでもう一度。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    got = {m.group(1): int(m.group(2).replace("_", "")) for m in
           re.finditer(r"pub const ([A-Z0-9_]+): usize = ([0-9_]+);", src)}
    return {name: got.get(name) for name in CONSTS}


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_naafiri differs from build_naafiri.P: rebuild it first")
    wrong = {name: (got, p[CONSTS[name]]) for name, got in consts().items() if got != p[CONSTS[name]]}
    if wrong:
        sys.exit("src/lib.rs constants differ from build_naafiri.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":pack":
        sys.exit("the copy has no league_naafiri:pack passive: update this script")
    text = json.dumps(champion)
    if '"league_naafiri_r_alive"' in text or '"league_naafiri:q2"' not in text:
        sys.exit("the copy still carries the takedown window or lacks the execute: update this script")
    for slot in ("skill", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), q_exec_pct=f"{p['q_exec'] / 100:g}")
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
