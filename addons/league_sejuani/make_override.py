"""Build the add-on's copy of Sejuani from the main pack (Frost, the shatter, the Frost Armour and Arctic Assault as in League).

    python addons/league_sejuani/make_override.py [--draft]

Rebuilds Sejuani with tools/kit/build_sejuani.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_sejuani.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_sejuani/override/league_sejuani.data_champion
and .../text/champion.i18n: the build with native=1 -
  * passive = league_sejuani:frost (params f_n e_stun e_dmg e_ap sh_cd sh_dmg sh_ap sh_pct q_t fa_out);
  * the attack and W put a `frost` stack and a 3-tick `hit` mark on the champion they hit (the add-on freezes at f_n
    stacks and shatters a champion stunned by anyone), instead of the main pack's count on her;
  * the Frost Armour without the tenacity stand-in (the add-on clears slows off her);
  * Arctic Assault raises `q_stop` on its first champion (the add-on holds her there);
  * the attack's and the skill's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game
    shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Sejuani changes.
--draft: only the copy, without the main-pack check and the texts (before the main pack has Sejuani).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_sejuani")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_sejuani as kit  # noqa: E402
import setup_sejuani as setup  # noqa: E402

MOD_ID = "league_sejuani"
HERO = "league_sejuani"
KEYS = ("f_n", "e_stun", "e_dmg", "e_ap", "sh_cd", "sh_dmg", "sh_ap", "sh_pct", "q_t", "fa_out")
mag, t, n, cc = setup.mag, setup.t, setup.n, setup.cc
# lang -> the add-on's attack and skill texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】链枷抽打。" + n("北地之怒") + "：脱战后冰霜护甲，护甲、魔抗+{fa_def}%、免疫减速。普攻和凛冬之怒给每个"
                  "敌方英雄叠霜冻，满{f_n}层" + cc("冻住") + t("{e_stun}秒") + "并造成" + mag("e_dmg", "e_ap") +
                  "；打中被晕住的敌人（谁晕的都算）再造成其最大生命{sh_pct}%。",
        "skill": "【附加包】钢鬃冲向目标，撞到第一个敌方英雄就停下，路上的敌人受到" + mag("q_dmg", "q_ap") + "魔法伤害并被" +
                 cc("击飞") + t("{q_up}秒") + "。",
    },
    "zh-hant": {
        "attack": "【附加包】鏈枷抽打。" + n("北境之怒") + "：脫戰後冰霜護甲，護甲、魔防+{fa_def}%、免疫緩速。普攻和凜冬狂怒給每個"
                  "敵方英雄疊霜凍，滿{f_n}層" + cc("冰凍") + t("{e_stun}秒") + "並造成" + mag("e_dmg", "e_ap") +
                  "；打中被暈眩的敵人（誰暈的都算）再造成其最大生命{sh_pct}%。",
        "skill": "【附加包】坐騎衝向目標，撞到第一個敵方英雄就停下，路上的敵人受到" + mag("q_dmg", "q_ap") + "魔法傷害並被" +
                 cc("擊飛") + t("{q_up}秒") + "。",
    },
    "en": {
        "attack": "[Add-on] Flail blows. " + n("Fury of the North") + ": out of combat her Frost Armour gives +{fa_def}% "
                  "armour and magic resist and slow immunity. Her attacks and Winter's Wrath add Frost to each enemy "
                  "champion; {f_n} " + cc("freeze") + " it for " + t("{e_stun}s") + " and deal " + mag("e_dmg", "e_ap") +
                  "; hitting a stunned enemy (anyone's stun) deals {sh_pct}% of its maximum health more.",
        "skill": "[Add-on] Bristle charges at the target and stops at the first enemy champion: the enemies in the way take " +
                 mag("q_dmg", "q_ap") + " magic damage and are " + cc("knocked up") + " for " + t("{q_up}s") + ".",
    },
    "ko": {
        "attack": "[확장] 철퇴 공격. " + n("혹한의 분노") + ": 비전투 시 서리 갑옷, 방어력·마법 저항력 +{fa_def}%, 둔화 면역. "
                  "기본 공격과 혹한의 서릿발이 적 챔피언마다 서리 중첩, {f_n}중첩 시 " + t("{e_stun}초") + " " + cc("빙결") +
                  ", " + mag("e_dmg", "e_ap") + "; 기절한 적(누가 기절시켰든)을 치면 최대 체력의 {sh_pct}% 추가.",
        "skill": "[확장] 브리슬이 대상에게 돌진, 첫 적 챔피언에서 멈춤: 경로의 적에게 " + mag("q_dmg", "q_ap") + " 마법 피해와 " +
                 t("{q_up}초") + " " + cc("에어본") + ".",
    },
    "ja": {
        "attack": "【拡張】フレイルで打つ。" + n("極北の激憤") + "：非戦闘時フロストアーマー、物理・魔法防御+{fa_def}%、スロウ無効。"
                  "通常攻撃と氷河の怒りで敵チャンピオンごとにフロスト、{f_n}つで" + t("{e_stun}秒") + cc("凍結") + "し" +
                  mag("e_dmg", "e_ap") + "；スタン中の敵（誰のスタンでも）を打つと最大体力{sh_pct}%追加。",
        "skill": "【拡張】ブリッスルが対象へ突進、最初の敵チャンピオンで止まる：進路の敵に" + mag("q_dmg", "q_ap") +
                 "の魔法ダメージと" + t("{q_up}秒") + cc("ノックアップ") + "。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (f_n: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def main():
    draft = "--draft" in sys.argv[1:]
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":frost":
        sys.exit("the copy does not call the add-on: update this script")
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_sejuani differs from build_sejuani.P: rebuild it first")
        for slot in ("attack", "skill"):
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = setup.values(p)
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out_text = os.path.join(ADDON, "text", "champion.i18n")
        os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
        with open(lp(out_text), "w", encoding="utf-8", newline="") as f:
            f.write(dumps_main({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text}))
        print("wrote", os.path.relpath(out_text, ROOT), {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                                                         for lang, d in NATIVE.items() for k, tx in d.items()})
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    print(out, "(draft)" if draft else json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
