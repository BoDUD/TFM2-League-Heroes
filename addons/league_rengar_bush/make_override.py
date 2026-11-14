"""Build the add-on's copy of Rengar from the main pack (Unseen Predator from the map's bushes).

    python addons/league_rengar_bush/make_override.py

Rebuilds Rengar with tools/kit/build_rengar.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_rengar.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_rengar_bush/override/league_rengar.data_champion and .../text/champion.i18n: the build with native=1 -
  * the main pack's readiness all kept: the respawn, R and the "ready after quiet ticks" check (`league_rengar_fight`,
    back since 0.2.0, 2026-11-03: without it a fight began with a leap only when the AI had just walked through a bush,
    the players: 「他的跳跃机制非常不稳定，有时候会跳，有时候不跳」);
  * passive = the add-on's league_rengar_bush:bush with {leap_range}: every tick it readies the pounce while he stands
    in a bush and, in a fight, takes that readiness back when he leaves it;
  * the attack runs the add-on's native league_rengar_bush:aim on its target just before it reads `ready`: at a tower or
    the nexus the readiness is set aside (the pounce's landing never hit one) and comes back for the next unit;
  * the attack's tooltip (the passive) points to description.league_rengar_bush.attack with a "bush build" lead and the
    bush wording, so the tooltip in game shows whether the override took;
  * Battle Roar as League's (0.2.4): the copy's W has no heal of its own - it raises league_rengar_w_mend and the passive
    heals 50% of the damage taken in the last 1.5 s (src/lib.rs ROAR_WINDOW); the empowered roar's league_rengar_we_cc is
    a plain flag and the passive clears the crowd control on him; its tooltip is description.league_rengar_bush.skill.
Every other champion stays untouched. Run it again whenever the main pack's Rengar changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_rengar_bush")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_rengar as kit  # noqa: E402
import setup_rengar as setup  # noqa: E402

MOD_ID = "league_rengar_bush"
HERO = "league_rengar"
# lang -> (the lead, the main pack's readiness wording, the same with the bush first). 0.2.0 keeps the out-of-combat
# readiness, so the wording grew and the leads shrank ("test build" -> "bush build"): zh-hans 130/130, en 334/334 and
# ja 147/147 sit at TOOLTIP_MAX
NATIVE = {
    "zh-hans": ("【草丛版】", "复活、脱战" + setup.A + "{quiet}秒" + setup.E + "或R后",
                "草丛里、复活、脱战" + setup.A + "{quiet}秒" + setup.E + "或R后"),
    "zh-hant": ("【草叢版】", "復活、脫戰" + setup.A + "{quiet}秒" + setup.E + "或R後",
                "草叢裡、復活、脫戰" + setup.A + "{quiet}秒" + setup.E + "或R後"),
    "en": ("[Bush] ", "on respawn, after " + setup.A + "{quiet}s" + setup.E + " out of combat or after R",
           "in brush, on respawn, " + setup.A + "{quiet}s" + setup.E + " out of combat or after R"),
    "ko": ("[수풀] ", "부활, " + setup.A + "{quiet}초" + setup.E + " 비전투 또는 R 후",
           "수풀 안, 부활, " + setup.A + "{quiet}초" + setup.E + " 비전투 또는 R 후"),
    "ja": ("【茂み版】", "復活時、" + setup.A + "{quiet}秒" + setup.E + "非戦闘またはR後",
           "茂みの中、復活時、" + setup.A + "{quiet}秒" + setup.E + "非戦闘またはR後"),
}
# lang -> (the main pack's Bonetooth Necklace wording in the ult's tooltip, the add-on's: League's takedowns, once per
# champion, kept through death - src/lib.rs counts them from the kill log)
BONE = {
    "zh-hans": ("：击杀英雄得一枚战利品（最多5枚），", "：击杀或助攻每个敌方英雄各得一枚战利品（最多5枚，阵亡不丢），"),
    "zh-hant": ("：擊殺英雄得一枚戰利品（最多5枚），", "：擊殺或助攻每個敵方英雄各得一枚戰利品（最多5枚，陣亡不丟），"),
    "en": (": each champion he kills is a Trophy (up to 5), ",
           ": a takedown on each enemy champion is a Trophy (up to 5, kept through death), "),
    "ko": (": 챔피언 처치마다 전리품(최대 5개), ", ": 적 챔피언마다 처치 관여 시 전리품 1개(최대 5개, 사망해도 유지), "),
    "ja": ("：チャンピオンを倒すたびトロフィー（最大5個）、", "：敵チャンピオンごとにキル関与でトロフィー1個（最大5個、デスでも保持）、"),
}


# lang -> the copy's Battle Roar text (League's heal and cleanse: src/lib.rs's passive does both)
ROAR = {
    "zh-hans": "【草丛版】咆哮，对周围敌人造成" + setup.phy("w") + "伤害，回复最近" + setup.A + "1.5秒" + setup.E + "受到伤害的" +
               setup.G + "50%" + setup.E + "（野怪的全部）。" + setup.O + "强化" + setup.E + "：" + setup.R + "解除身上的控制" +
               setup.E + "。" + setup.O + "强化技能" + setup.E + "都加速{fe_ms}%，持续" + setup.A + "{fe_ms_t}秒" + setup.E + "。",
    "zh-hant": "【草叢版】咆哮，對周圍敵人造成" + setup.phy("w") + "傷害，回復最近" + setup.A + "1.5秒" + setup.E + "受到傷害的" +
               setup.G + "50%" + setup.E + "（野怪的全部）。" + setup.O + "強化" + setup.E + "：" + setup.R + "解除身上的控場" +
               setup.E + "。" + setup.O + "強化技能" + setup.E + "都加速{fe_ms}%，持續" + setup.A + "{fe_ms_t}秒" + setup.E + "。",
    "en": "[Bush] Roars, dealing " + setup.phy("w") + " to enemies around him and healing " + setup.G + "50%" + setup.E +
          " of the damage he took in the last " + setup.A + "1.5s" + setup.E + " (all of monsters'). " + setup.O + "Empowered" +
          setup.E + ": " + setup.R + "cleanses crowd control" + setup.E + ". " + setup.O + "Every empowered skill" + setup.E +
          " also gives +{fe_ms}% move speed for " + setup.A + "{fe_ms_t}s" + setup.E + ".",
    "ko": "[수풀] 포효해 주변 적에게 " + setup.phy("w") + "의 피해를 주고 최근 " + setup.A + "1.5초" + setup.E + " 동안 받은 피해의 " +
          setup.G + "50%" + setup.E + "(몬스터 피해는 전부) 회복. " + setup.O + "강화" + setup.E + ": " + setup.R + "군중 제어 해제" +
          setup.E + ". " + setup.O + "강화 스킬" + setup.E + "은 모두 " + setup.A + "{fe_ms_t}초" + setup.E + " 동안 이동 속도 +{fe_ms}%.",
    "ja": "【茂み版】咆哮し周囲の敵に" + setup.phy("w") + "、直近" + setup.A + "1.5秒" + setup.E + "の被ダメージの" + setup.G + "50%" +
          setup.E + "（モンスターからは全量）回復。" + setup.O + "強化" + setup.E + "：" + setup.R + "行動妨害を解除" + setup.E + "。" +
          setup.O + "強化スキル" + setup.E + "はすべて" + setup.A + "{fe_ms_t}秒" + setup.E + "移動速度+{fe_ms}%。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_rengar.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_rengar differs from build_rengar.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if "league_rengar_fight" not in text:
        sys.exit("the copy lost the quiet-ticks check (league_rengar_fight, which src/lib.rs reads): update this script")
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":bush":
        sys.exit("the copy has no league_rengar_bush:bush passive: update this script")
    effects = champion["attack"]["effect"]["effects"]
    aim = [i for i, e in enumerate(effects) if e.get("effect_ref") == MOD_ID + ":aim"]
    reads = [i for i, e in enumerate(effects) if e.get("type") == "SwitchByBuff" and e.get("buff_name") == HERO + "_ready"]
    if len(aim) != 1 or len(reads) != 1 or aim[0] > reads[0]:
        sys.exit("the copy's attack must run league_rengar_bush:aim once, before it reads league_rengar_ready")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    # the Bonetooth Necklace: no Trophy from the data's kill check in the copy (the passive gives them), its numbers in
    # the passive's params
    if '"league_rengar_bt1"' in text or sorted(champion["passive"]["params"]) != ["bt1", "bt2", "bt3", "bt4", "bt5", "leap_range"]:
        sys.exit("the copy must leave the Trophies (league_rengar_bt1..5) to the passive and hand it bt1..bt5")
    champion["ult"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".ult"
    # Battle Roar: no heal in the copy's W (the passive heals from the damage it saw), the empowered flag without cc_immune
    w = json.dumps(champion["skill"])
    if '"Heal"' in w or '"' + HERO + '_w_mend"' not in w or '"cc_immune"' in w:
        sys.exit("the copy's W must leave the heal to the passive (league_rengar_w_mend) and the cleanse too (no cc_immune)")
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        if "pub const ROAR_WINDOW: usize = 90;" not in f.read():
            sys.exit("src/lib.rs's ROAR_WINDOW is not 90 ticks: the texts say 1.5 s")
    champion["skill"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".skill"

    values = setup.values(p)
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        attack = setup.TEXT[lang]["attack"]
        if attack.count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update NATIVE")
        texts[lang] = (lead + attack.replace(old, new)).format(**values)
    ults = {}
    for lang, (old, new) in BONE.items():
        ult = setup.TEXT[lang]["ult"]
        if ult.count(old) != 1:
            sys.exit(f"{lang}: the main pack's Bonetooth text changed ({old!r} not found once): update BONE")
        ults[lang] = ult.replace(old, new).format(**values)
    roars = {lang: t.format(**values) for lang, t in ROAR.items()}
    tabs = (("attack", texts), ("skill", roars), ("ult", ults))
    long = {f"{lang}.{k}": setup.shown_length(t) for k, tab in tabs for lang, t in tab.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_rengar.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no bush-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang], "skill": roars[lang], "ult": ults[lang]}}}
                            for lang in main_text}, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for k, tab in tabs for lang, t in tab.items()})


if __name__ == "__main__":
    main()
