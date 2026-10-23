"""Build the add-on's copy of Aurora from the main pack (Across the Veil at her real low health).

    python addons/league_aurora/make_override.py

Rebuilds Aurora with tools/kit/build_aurora.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_aurora.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_aurora/override/league_aurora.data_champion and
.../text/champion.i18n: the build with native=1 -
  * Across the Veil's hop (in the attack and The Weirding) reads the flag `league_aurora_low` as well as an enemy
    champion within w_near (the main pack's stand-in reads the champion alone);
  * passive = league_aurora:veil (params: w_low), which raises the flag every tick she is under w_low% health;
  * the attack's tooltip (a key of the add-on's own id) says the low-health rule, so the tooltip in game shows whether
    the override took.
Every other champion stays untouched. Run it again whenever the main pack's Aurora changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_aurora")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_aurora as kit  # noqa: E402
import setup_aurora as setup  # noqa: E402

MOD_ID = "league_aurora"
HERO = "league_aurora"
mag, t, n, hl = setup.mag, setup.t, setup.n, setup.hl
# lang -> the add-on's attack text (the main pack's with the low-health rule)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】魔杖点出灵光。" + n("驱灵奇术") + "：命中英雄叠层，第三层抽出灵物，造成" + mag("p_dmg", "p_ratio") + " + 目标{p_hp}%最大生命值"
                  "的伤害，" + hl("回复") + mag("p_heal", "p_heal_r") + "生命并加速。" + n("灵纱洞开") + "：生命低于{w_low}%被贴身时后跳，隐身" +
                  t("{w_inv}秒") + "、加速{w_ms}%（" + t("{w_cd}秒") + "一次）。",
    },
    "zh-hant": {
        "attack": "【附加包】魔杖點出靈光。" + n("精靈附體") + "：命中英雄疊層，第三層抽出精靈，造成" + mag("p_dmg", "p_ratio") + " + 目標{p_hp}%最大生命值"
                  "的傷害，" + hl("回復") + mag("p_heal", "p_heal_r") + "生命並加速。" + n("跨越兩界") + "：生命低於{w_low}%被貼身時後跳，隱形" +
                  t("{w_inv}秒") + "、加速{w_ms}%（" + t("{w_cd}秒") + "一次）。",
    },
    "en": {
        "attack": "[Add-on] A spirit bolt. " + n("Spirit Abjuration") + ": her hits on champions add up; the third "
                  "exorcises a spirit for " + mag("p_dmg", "p_ratio") + " + {p_hp}% of the target's max health, and it " +
                  hl("heals") + " her " + mag("p_heal", "p_heal_r") + " and speeds her up. " + n("Across the Veil") + ": under "
                  "{w_low}% health with an enemy on her, she hops back, invisible " + t("{w_inv}s") + ", {w_ms}% faster "
                  "(every " + t("{w_cd}s") + ").",
    },
    "ko": {
        "attack": "[확장] 지팡이로 영혼 빛을 쏜다. " + n("영혼 방호술") + ": 챔피언 적중이 쌓여 세 번째에 영혼을 뽑아 " + mag("p_dmg", "p_ratio") +
                  " + 최대 체력의 {p_hp}% 피해, " + mag("p_heal", "p_heal_r") + " " + hl("회복") + "과 이동 속도 증가. " + n("장막 너머로") +
                  ": 체력 {w_low}% 미만에 적이 붙으면 뒤로 뛰어 " + t("{w_inv}초") + " 투명, 이동 속도 +{w_ms}% (" + t("{w_cd}초") + "마다).",
    },
    "ja": {
        "attack": "【拡張】杖から霊光を放つ。" + n("精霊の解放") + "：英雄への命中が重なり、3回目で精霊を引き出し" + mag("p_dmg", "p_ratio") +
                  "＋最大体力の{p_hp}%のダメージ、" + mag("p_heal", "p_heal_r") + hl("回復") + "し加速。" + n("ベールを越えて") +
                  "：体力{w_low}%未満で敵に詰められると後ろへ跳び" + t("{w_inv}秒") + "透明、移動速度+{w_ms}%（" + t("{w_cd}秒") + "ごと）。",
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
        sys.exit("the main pack's league_aurora differs from build_aurora.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_aurora.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":veil":
        sys.exit("the copy has no league_aurora:veil passive: update this script")
    if '"league_aurora_low"' not in json.dumps(champion):
        sys.exit("the copy's veil does not read league_aurora_low: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = dict(setup.values(p), w_low=p["w_low"])
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
