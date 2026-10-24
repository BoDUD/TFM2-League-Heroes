"""Build the add-on's copy of Aurelion Sol from the main pack (stardust kept through death, the black hole's real execute).

    python addons/league_aurelionsol/make_override.py

Rebuilds Aurelion Sol with tools/kit/build_aurelionsol.py (its parameter table P), checks that the plain build is the
main pack's league/champion/league_aurelionsol.data_champion byte for byte (so the copy never drifts from the shipped
kit) and that the defaults in src/lib.rs's Params are P's numbers, and writes
addons/league_aurelionsol/override/league_aurelionsol.data_champion and .../text/champion.i18n: the build with native=1 -
  * Singularity's centre also runs league_aurelionsol:core on every champion it strikes (it dies under e_low% of its
    maximum health + e_low_d% per stardust, by its real health);
  * passive = league_aurelionsol:stardust (params: d_max, e_low, e_low_d), which puts his stardust stacks back after a
    death;
  * the attack's and Singularity's tooltips (keys of the add-on's own id) say both rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Aurelion Sol changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_aurelionsol")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_aurelionsol as kit  # noqa: E402
import setup_aurelionsol as setup  # noqa: E402

MOD_ID = "league_aurelionsol"
HERO = "league_aurelionsol"
mag, t, n, cc = setup.mag, setup.t, setup.n, setup.cc
# lang -> the add-on's attack and skill2 texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】甩出一颗星星。" + n("星海焕然") + "：技能命中英雄收集星尘（每层法强+{d_ap}%，最多{d_max}层，"
                  "死亡后保留），每{sky_n}层下一次大招变为天瀑。" + n("星穹流丽") + "：击杀英雄后起飞" + t("{w_t}秒") +
                  "，移速+{w_ms}%、法强+{w_ap}%。",
        "skill2": "【附加包】在目标处召唤黑洞（" + t("{e_t}秒") + "），每" + t("{e_p}秒") + "造成" + mag("e_dmg", "e_ratio") +
                  "魔法伤害，把敌人拉向中心并" + cc("减速") + "{e_slow}%；中心" + cc("处决") + "生命低于{e_low}%（每层星尘+{e_low_d}%）的英雄。",
    },
    "zh-hant": {
        "attack": "【附加包】甩出一顆星星。" + n("宇宙創世") + "：技能命中英雄收集星塵（每層魔攻+{d_ap}%，最多{d_max}層，"
                  "死亡後保留），每{sky_n}層下一次大絕變為天界殞落。" + n("星界翱翔") + "：擊殺英雄後起飛" + t("{w_t}秒") +
                  "，移速+{w_ms}%、魔攻+{w_ap}%。",
        "skill2": "【附加包】在目標處召喚奇點（" + t("{e_t}秒") + "），每" + t("{e_p}秒") + "造成" + mag("e_dmg", "e_ratio") +
                  "魔法傷害，把敵人拉向中心並" + cc("緩速") + "{e_slow}%；中心" + cc("處決") + "生命低於{e_low}%（每層星塵+{e_low_d}%）的英雄。",
    },
    "en": {
        "attack": "[Add-on] Flings a star. " + n("Cosmic Creator") + ": his spells hitting champions gather Stardust "
                  "(+{d_ap}% ability power a stack, {d_max} at most, kept through death); every {sky_n} make his next ult "
                  "The Skies Descend. " + n("Astral Flight") + ": after a takedown he flies for " + t("{w_t}s") +
                  ", +{w_ms}% move speed and +{w_ap}% ability power.",
        "skill2": "[Add-on] Summons a black hole at the target for " + t("{e_t}s") + ": every " + t("{e_p}s") + " " +
                  mag("e_dmg", "e_ratio") + " magic damage, pulling enemies toward its centre and " + cc("slowing") +
                  " them {e_slow}%; its centre " + cc("executes") + " champions under {e_low}% health (+{e_low_d}% per "
                  "Stardust).",
    },
    "ko": {
        "attack": "[확장] 별을 던진다. " + n("우주의 창조자") + ": 스킬이 챔피언을 맞히면 별무리 획득(중첩당 주문력 +{d_ap}%, "
                  "최대 {d_max}, 죽어도 유지), {sky_n}개마다 다음 궁극기가 천상 강림이 됨. " + n("별의 비행") +
                  ": 처치 관여 후 " + t("{w_t}초") + " 동안 비행, 이동 속도 +{w_ms}%, 주문력 +{w_ap}%.",
        "skill2": "[확장] 대상 위치에 " + t("{e_t}초") + " 동안 블랙홀 소환: " + t("{e_p}초") + "마다 " +
                  mag("e_dmg", "e_ratio") + " 마법 피해, 적을 중심으로 끌어당기고 {e_slow}% " + cc("둔화") +
                  "; 중심은 체력 {e_low}%(별무리당 +{e_low_d}%) 미만 챔피언을 " + cc("처형") + ".",
    },
    "ja": {
        "attack": "【拡張】星を投げる。" + n("宇宙の創造者") + "：スキルがチャンピオンに当たると星屑獲得（1スタックにつき魔力"
                  "+{d_ap}%、最大{d_max}、死んでも残る）、{sky_n}個ごとに次のアルティメットが崩れ落つ天穹に。" +
                  n("天空への飛翔") + "：キル関与後" + t("{w_t}秒") + "飛行、移動速度+{w_ms}%、魔力+{w_ap}%。",
        "skill2": "【拡張】対象の位置に" + t("{e_t}秒") + "ブラックホールを召喚：" + t("{e_p}秒") + "ごとに" +
                  mag("e_dmg", "e_ratio") + "の魔法ダメージ、敵を中心へ引き寄せ{e_slow}%" + cc("スロウ") +
                  "；中心は体力{e_low}%（星屑1つにつき+{e_low_d}%）未満のチャンピオンを" + cc("処刑") + "。",
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
        sys.exit("the main pack's league_aurelionsol differs from build_aurelionsol.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_aurelionsol.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":stardust":
        sys.exit("the copy has no league_aurelionsol:stardust passive: update this script")
    if '"league_aurelionsol:core"' not in json.dumps(champion):
        sys.exit("the copy's black hole does not run league_aurelionsol:core: update this script")
    for slot in ("attack", "skill2"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), e_low=p["e_low"], e_low_d=p["e_low_d"])
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
